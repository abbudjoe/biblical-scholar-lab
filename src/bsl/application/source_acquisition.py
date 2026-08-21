from __future__ import annotations

import hashlib
import os
import stat
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any, Literal, cast
from uuid import UUID

import rfc8785
from pydantic import BaseModel, ValidationError
from uuid6 import uuid7

from bsl.application.source_admission import compile_source_plan
from bsl.contracts.archive import ArchiveInitializationReceipt, ArchiveRootMarker
from bsl.contracts.source_admission import (
    APPROVED_MANIFEST_SHA256,
    AdmissionDecision,
    FetchReceipt,
    PlannedSource,
    SourceId,
    SourceSnapshot,
    _ArchiveEntry,  # pyright: ignore[reportPrivateUsage]
    _FetchedObject,  # pyright: ignore[reportPrivateUsage]
    _HttpExchange,  # pyright: ignore[reportPrivateUsage]
    _snapshot_content_sha256,  # pyright: ignore[reportPrivateUsage]
    _source_rights,  # pyright: ignore[reportPrivateUsage]
    _source_spec_sha256,  # pyright: ignore[reportPrivateUsage]
)
from bsl.infrastructure.archive_store import (
    _directory,  # pyright: ignore[reportPrivateUsage]
    _fsync_directory,  # pyright: ignore[reportPrivateUsage]
    _hash_file,  # pyright: ignore[reportPrivateUsage]
    _write_immutable,  # pyright: ignore[reportPrivateUsage]
)
from bsl.infrastructure.source_transport import (
    FetchBatch,
    HttpResponse,
    SourceTransportError,
    Transport,
    fetch_source,
    https_transport,
)

NewUuid = Callable[[], UUID]
Now = Callable[[], datetime]
_Disposition = Literal["ADMITTED", "REJECTED", "UNRESOLVED"]
_CANONICAL_ARCHIVE_ROOT = Path("/Volumes/BSL-Archive/BiblicalScholarLab")


@dataclass(frozen=True)
class _SourceContext:
    plan: PlannedSource
    spec_sha256: str


@dataclass(frozen=True)
class _AcquisitionResult:
    fetch_receipt: FetchReceipt | None
    decision: AdmissionDecision
    snapshot: SourceSnapshot | None
    verified_existing: bool = False


def _canonical(model: BaseModel) -> bytes:
    return rfc8785.dumps(model.model_dump(mode="json"))


def _model_sha256(model: BaseModel) -> str:
    return hashlib.sha256(_canonical(model)).hexdigest()


def _read_regular(path: Path, label: str) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise ValueError
            with os.fdopen(fd, "rb", closefd=False) as stream:
                return stream.read()
        finally:
            os.close(fd)
    except (OSError, ValueError):
        raise ValueError(f"{label} cannot be read as a regular file") from None


def _require_expected_archive_root(root: Path, expected_root: Path) -> None:
    if root != expected_root:
        raise ValueError("archive root does not resolve to the canonical archive root")


def _require_initialized_root(root: Path, expected_root: Path = _CANONICAL_ARCHIVE_ROOT) -> Path:
    if root.is_symlink() or not root.is_dir():
        raise ValueError("archive root must be an initialized real directory")
    root = root.resolve(strict=True)
    _require_expected_archive_root(root, expected_root)
    marker_path = root / ".bsl-archive-root.json"
    try:
        marker = ArchiveRootMarker.model_validate_json(_read_regular(marker_path, "archive marker"))
        marker_sha256, _ = _hash_file(marker_path, require_read_only=True)
        canary_sha256, _ = _hash_file(root / marker.canary_relative_path, require_read_only=True)
        receipt_path = root / marker.initialization_receipt_relative_path
        receipt = ArchiveInitializationReceipt.model_validate_json(
            _read_regular(receipt_path, "initialization receipt")
        )
        _hash_file(receipt_path, require_read_only=True)
    except (OSError, ValidationError, ValueError):
        raise ValueError("archive root lacks a valid initialized marker and retained evidence") from None
    if (
        canary_sha256 != marker.canary_sha256
        or receipt.archive_id != marker.archive_id
        or receipt.operation_id != marker.archive_id
        or receipt.disposition != "INITIALIZED"
        or receipt.marker_sha256 != marker_sha256
        or marker.canonical_archive_root != str(_CANONICAL_ARCHIVE_ROOT)
        or receipt.canonical_archive_root != marker.canonical_archive_root
    ):
        raise ValueError("archive marker evidence bindings are invalid")
    required = ("objects/sha256", "manifests/source", "snapshots/source", "quarantine", ".incoming")
    if any(not (root / path).is_dir() or (root / path).is_symlink() for path in required):
        raise ValueError("initialized archive layout is incomplete")
    return root


def _source(manifest: Path, source_id: str) -> _SourceContext:
    plan = compile_source_plan(manifest)
    match = next((source for source in plan.semantic_payload.sources if source.source_id == source_id), None)
    if match is None:
        raise ValueError("source ID is not in the exact approved SOURCE-PLAN-01 set")
    return _SourceContext(match, _source_spec_sha256(match))


def _fetch_receipt(
    context: _SourceContext, batch: FetchBatch, attempt_id: UUID, new_uuid: NewUuid, now: Now
) -> FetchReceipt:
    source = context.plan
    generated_at = now()
    exchanges = tuple(
        _HttpExchange(
            requested_url=response.requested_url,
            final_url=response.final_url,
            status=200,
            redirect_chain=response.redirect_chain,
            headers=response.headers,
            response_sha256=hashlib.sha256(response.body).hexdigest(),
            retrieved_at=generated_at,
            byte_count=len(response.body),
        )
        for response in batch.responses
    )
    objects = tuple(
        _FetchedObject(
            relative_path=item.relative_path,
            sha256=hashlib.sha256(item.data).hexdigest(),
            byte_count=len(item.data),
            rights_evidence=item.rights_evidence,
        )
        for item in batch.files
    )
    inventory = tuple(
        _ArchiveEntry(relative_path=item.relative_path, sha256=item.sha256, byte_count=item.byte_count)
        for item in batch.archive_inventory
    )
    aggregate = hashlib.sha256(rfc8785.dumps(tuple(item.model_dump(mode="json") for item in objects))).hexdigest()
    return FetchReceipt(
        receipt_id=new_uuid(),
        attempt_id=attempt_id,
        generated_at=generated_at,
        source_id=cast(SourceId, source.source_id),
        manifest_identity=APPROVED_MANIFEST_SHA256,
        source_spec=source,
        source_spec_sha256=context.spec_sha256,
        resolved_revision=batch.resolved_revision,
        package_sha256=batch.package_sha256,
        exchanges=exchanges,
        objects=objects,
        archive_inventory=inventory,
        objects_aggregate_sha256=aggregate,
        total_received_bytes=sum(len(response.body) for response in batch.responses),
    )


def _attempt_directory(root: Path, source_id: str, attempt_id: UUID) -> tuple[Path, str]:
    relative = f"quarantine/SOURCE-PLAN-01/{source_id}/{attempt_id}"
    parts = PurePosixPath(relative).parts
    parent = _directory(root, *parts[:-1])
    path = parent / parts[-1]
    path.mkdir(mode=0o700)
    _fsync_directory(parent)
    return path, relative


def _retain_quarantine(attempt: Path, batch: FetchBatch, receipt: FetchReceipt) -> None:
    for item, record in zip(batch.files, receipt.objects, strict=True):
        target = attempt / "objects" / record.relative_path
        _directory(attempt, *target.relative_to(attempt).parent.parts)
        _write_immutable(target, item.data, expected_sha256=record.sha256)
    _write_immutable(attempt / "fetch-receipt.json", _canonical(receipt), expected_sha256=_model_sha256(receipt))


def _journal_transport(attempt: Path, transport: Transport) -> Transport:
    responses = _directory(attempt, "responses")
    sequence = 0

    def fetch(url: str, limit: int) -> HttpResponse:
        nonlocal sequence
        response = transport(url, limit)
        digest = hashlib.sha256(response.body).hexdigest()
        prefix = f"{sequence:03d}-{digest}"
        metadata = {
            "requested_url": response.requested_url,
            "final_url": response.final_url,
            "status": response.status,
            "headers": response.headers,
            "redirect_chain": response.redirect_chain,
            "body_sha256": digest,
            "byte_count": len(response.body),
        }
        _write_immutable(responses / f"{prefix}.bin", response.body, expected_sha256=digest)
        _write_immutable(responses / f"{prefix}.json", rfc8785.dumps(metadata))
        sequence += 1
        return response

    return fetch


def _decision(
    source: PlannedSource,
    attempt_id: UUID,
    quarantine_relative: str,
    disposition: _Disposition,
    receipt: FetchReceipt | None,
    reasons: tuple[str, ...],
    new_uuid: NewUuid,
    now: Now,
) -> AdmissionDecision:
    hashes = (
        ()
        if receipt is None or disposition != "ADMITTED"
        else tuple(dict.fromkeys(item.sha256 for item in receipt.objects))
    )
    return AdmissionDecision(
        decision_id=new_uuid(),
        attempt_id=attempt_id,
        generated_at=now(),
        source_id=cast(SourceId, source.source_id),
        manifest_identity=APPROVED_MANIFEST_SHA256,
        disposition=disposition,
        fetch_receipt_sha256=_model_sha256(receipt) if receipt is not None else None,
        admitted_object_sha256=hashes,
        reasons=reasons,
        quarantine_relative_path=quarantine_relative,
    )


def _load_snapshot(root: Path, source_id: str) -> SourceSnapshot | None:
    path = root / "snapshots" / "source" / f"{source_id}.json"
    if not path.exists():
        return None
    try:
        _hash_file(path, require_read_only=True)
        return SourceSnapshot.model_validate_json(_read_regular(path, "source snapshot"))
    except (OSError, ValidationError, ValueError):
        raise ValueError("existing source snapshot is invalid") from None


def _verify_authority(root: Path, snapshot: SourceSnapshot, context: _SourceContext) -> None:
    try:
        receipt_path = root / snapshot.fetch_receipt_relative_path
        receipt_hash, _ = _hash_file(receipt_path, require_read_only=True)
        receipt = FetchReceipt.model_validate_json(_read_regular(receipt_path, "fetch receipt"))
        decision_path = root / snapshot.admission_decision_relative_path
        decision_hash, _ = _hash_file(decision_path, require_read_only=True)
        decision = AdmissionDecision.model_validate_json(_read_regular(decision_path, "admission decision"))
    except (OSError, ValidationError, ValueError):
        raise ValueError("existing snapshot authority is missing or invalid") from None
    expected = (snapshot.source_id, snapshot.admission_attempt_id, context.spec_sha256)
    if (receipt.source_id, receipt.attempt_id, receipt.source_spec_sha256) != expected:
        raise ValueError("fetch receipt does not bind the existing snapshot")
    if (decision.source_id, decision.attempt_id) != expected[:2] or decision.disposition != "ADMITTED":
        raise ValueError("admission decision does not bind the existing snapshot")
    admitted = tuple(dict.fromkeys(item.sha256 for item in snapshot.objects))
    exchanges = tuple(exchange.model_dump(mode="json") for exchange in receipt.exchanges)
    bindings = (
        receipt_hash == snapshot.fetch_receipt_sha256,
        decision_hash == snapshot.admission_decision_sha256,
        decision.fetch_receipt_sha256 == receipt_hash,
        decision.admitted_object_sha256 == admitted,
        receipt.objects == snapshot.objects,
        receipt.archive_inventory == snapshot.archive_inventory,
        receipt.source_spec == context.plan == snapshot.source_spec,
        receipt.generated_at == snapshot.acquired_at,
        receipt.package_sha256 == snapshot.package_sha256,
        tuple(exchange.final_url for exchange in receipt.exchanges) == snapshot.retrieval_urls,
        hashlib.sha256(rfc8785.dumps(exchanges)).hexdigest() == snapshot.http_metadata_sha256,
        receipt.objects_aggregate_sha256 == snapshot.objects_aggregate_sha256,
    )
    if not all(bindings):
        raise ValueError("existing snapshot authority hashes are inconsistent")


def _verify_objects(root: Path, snapshot: SourceSnapshot) -> None:
    for item in snapshot.objects:
        path = root / "objects" / "sha256" / item.sha256[:2] / item.sha256
        digest, size = _hash_file(path, require_read_only=True)
        if (digest, size) != (item.sha256, item.byte_count):
            raise ValueError("existing snapshot object is missing or corrupt")


def _promote(root: Path, data: bytes, expected_sha256: str, stage_id: UUID) -> None:
    incoming = _directory(root, ".incoming")
    stage = incoming / f"{stage_id}.source-stage"
    _write_immutable(stage, data, expected_sha256=expected_sha256)
    destination_dir = _directory(root, "objects", "sha256", expected_sha256[:2])
    destination = destination_dir / expected_sha256
    try:
        try:
            os.link(stage, destination, follow_symlinks=False)
            _fsync_directory(destination_dir)
        except FileExistsError:
            digest, size = _hash_file(destination, require_read_only=True)
            if (digest, size) != (expected_sha256, len(data)):
                raise ValueError("existing content-addressed object is corrupt") from None
        digest, size = _hash_file(destination, require_read_only=True)
        if (digest, size) != (expected_sha256, len(data)):
            raise ValueError("promoted source object verification failed")
    finally:
        stage.unlink(missing_ok=True)


def _build_snapshot(context: _SourceContext, receipt: FetchReceipt, decision: AdmissionDecision) -> SourceSnapshot:
    source = context.plan
    language = "grc" if source.source_id in {"SP01-SRC-001", "SP01-SRC-002", "SP01-SRC-005"} else None
    language = "en" if source.source_id in {"SP01-SRC-003", "SP01-SRC-004"} else language
    operations, attribution = _source_rights(source)
    exchanges = tuple(exchange.model_dump(mode="json") for exchange in receipt.exchanges)
    prefix = f"manifests/source/{source.source_id}/{receipt.attempt_id}"
    data: dict[str, Any] = {
        "disposition": "ADMITTED",
        "source_id": receipt.source_id,
        "source_spec": source,
        "source_spec_sha256": context.spec_sha256,
        "acquired_at": receipt.generated_at,
        "package_sha256": receipt.package_sha256,
        "retrieval_urls": tuple(exchange.final_url for exchange in receipt.exchanges),
        "http_metadata_sha256": hashlib.sha256(rfc8785.dumps(exchanges)).hexdigest(),
        "objects": receipt.objects,
        "archive_inventory": receipt.archive_inventory,
        "objects_aggregate_sha256": receipt.objects_aggregate_sha256,
        "allowed_operations": operations,
        "attribution": attribution,
        "storage_zone": "AUTHORITATIVE_ARCHIVE",
        "language_identity": language,
        "script_identity": "Greek" if language == "grc" else "Latin" if language else None,
        "edition_identity": f"{source.name}; {source.tag or source.revision}",
        "passage_identity": "; ".join(source.normalized_scope) or None,
        "normalization_state": "NOT_STARTED",
        "extraction_code_identity": "bsl.source-acquisition.v1",
        "upstream_update_policy": "FROZEN_NO_AUTOMATIC_REFRESH",
        "review_state": "PENDING_CHATGPT_EXACT_HEAD_REVIEW",
        "manifest_identity": receipt.manifest_identity,
        "fetch_receipt_sha256": _model_sha256(receipt),
        "admission_decision_sha256": _model_sha256(decision),
        "admission_attempt_id": receipt.attempt_id,
        "fetch_receipt_relative_path": f"{prefix}-fetch-receipt.json",
        "admission_decision_relative_path": f"{prefix}-admission-decision.json",
        "snapshot_relative_path": f"snapshots/source/{source.source_id}.json",
    }
    draft = SourceSnapshot.model_construct(  # pyright: ignore[reportArgumentType]
        content_identity="", snapshot_identity="", **data
    )
    data["content_identity"] = _snapshot_content_sha256(draft)
    draft = SourceSnapshot.model_construct(snapshot_identity="", **data)  # pyright: ignore[reportArgumentType]
    identity = hashlib.sha256(rfc8785.dumps(draft.model_dump(mode="json", exclude={"snapshot_identity"}))).hexdigest()
    return SourceSnapshot.model_validate({"snapshot_identity": identity} | data)


def _persist_authority(
    root: Path, attempt: Path, receipt: FetchReceipt, decision: AdmissionDecision, snapshot: SourceSnapshot
) -> None:
    source_dir = _directory(root, "manifests", "source", receipt.source_id)
    prefix = str(receipt.attempt_id)
    records = (
        ("fetch", receipt, source_dir / f"{prefix}-fetch-receipt.json"),
        ("decision", decision, source_dir / f"{prefix}-admission-decision.json"),
        ("quarantine-decision", decision, attempt / "admission-decision.json"),
        ("snapshot", snapshot, root / snapshot.snapshot_relative_path),
    )
    staged: list[tuple[Path, Path]] = []
    linked: list[Path] = []
    try:
        for label, model, destination in records:
            stage = root / ".incoming" / f"{prefix}.{label}.stage"
            _write_immutable(stage, _canonical(model), expected_sha256=_model_sha256(model))
            staged.append((stage, destination))
        for stage, destination in staged[:-1]:
            os.link(stage, destination, follow_symlinks=False)
            linked.append(destination)
        for parent in dict.fromkeys(path.parent for path in linked):
            _fsync_directory(parent)
        stage, destination = staged[-1]
        os.link(stage, destination, follow_symlinks=False)
        linked.append(destination)
        _fsync_directory(destination.parent)
    except BaseException:
        for destination in reversed(linked):
            destination.unlink(missing_ok=True)
        for parent in dict.fromkeys(path.parent for path in linked):
            _fsync_directory(parent)
        raise
    finally:
        for stage, _destination in staged:
            stage.unlink(missing_ok=True)


def _record_failure(
    attempt: Path,
    source: PlannedSource,
    attempt_id: UUID,
    relative: str,
    disposition: _Disposition,
    reason: str,
    receipt: FetchReceipt | None,
    new_uuid: NewUuid,
    now: Now,
) -> _AcquisitionResult:
    decision = _decision(source, attempt_id, relative, disposition, receipt, (reason,), new_uuid, now)
    path = attempt / "admission-decision.json"
    if path.exists():
        raise ValueError("acquisition attempt already has a final decision")
    _write_immutable(path, _canonical(decision), expected_sha256=_model_sha256(decision))
    return _AcquisitionResult(receipt, decision, None)


def acquire_source(
    source_id: str,
    manifest: Path,
    archive_root: Path,
    *,
    transport: Transport = https_transport,
    new_uuid: NewUuid = uuid7,
    now: Now = lambda: datetime.now(UTC),
    _expected_archive_root: Path = _CANONICAL_ARCHIVE_ROOT,
) -> _AcquisitionResult:
    context = _source(manifest, source_id)
    source = context.plan
    root = _require_initialized_root(archive_root, _expected_archive_root)
    attempt_id = new_uuid()
    attempt, relative = _attempt_directory(root, source.source_id, attempt_id)
    receipt: FetchReceipt | None = None
    try:
        batch = fetch_source(source, _journal_transport(attempt, transport))
        receipt = _fetch_receipt(context, batch, attempt_id, new_uuid, now)
        _retain_quarantine(attempt, batch, receipt)
        decision = _decision(source, attempt_id, relative, "ADMITTED", receipt, (), new_uuid, now)
        snapshot = _build_snapshot(context, receipt, decision)
        existing = _load_snapshot(root, source.source_id)
        if existing is not None:
            _verify_authority(root, existing, context)
        if existing is not None and existing.content_identity != snapshot.content_identity:
            return _record_failure(
                attempt, source, attempt_id, relative, "REJECTED", "SNAPSHOT_IDENTITY_CHANGED", receipt, new_uuid, now
            )
        if existing is not None:
            _verify_objects(root, existing)
            _write_immutable(
                attempt / "admission-decision.json", _canonical(decision), expected_sha256=_model_sha256(decision)
            )
            return _AcquisitionResult(receipt, decision, existing, verified_existing=True)
        for item, record in zip(batch.files, receipt.objects, strict=True):
            _promote(root, item.data, record.sha256, new_uuid())
        _persist_authority(root, attempt, receipt, decision, snapshot)
        return _AcquisitionResult(receipt, decision, snapshot)
    except SourceTransportError as exc:
        return _record_failure(attempt, source, attempt_id, relative, "UNRESOLVED", str(exc), receipt, new_uuid, now)
    except (OSError, ValidationError, ValueError) as exc:
        return _record_failure(attempt, source, attempt_id, relative, "REJECTED", str(exc), receipt, new_uuid, now)
