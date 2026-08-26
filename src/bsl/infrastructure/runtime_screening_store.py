from __future__ import annotations

import hashlib
import os
import stat
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, cast
from uuid import UUID

import rfc8785
from pydantic import ValidationError

from bsl.contracts.runtime_screening import (
    FINGERPRINT_NAMES,
    FRESH_PUBLICATION_VERIFICATIONS,
    SPEC_IDENTITY,
    VERIFIED_EXISTING_VERIFICATIONS,
    RuntimeControllerLedger,
    VS01B08RuntimePairResult,
    VS01RuntimeAcquisitionRun,
    VS01RuntimeScreeningReceipt,
    canonical_sha256,
)
from bsl.infrastructure.benchmark_store import (
    _existing_file,  # pyright: ignore[reportPrivateUsage]
    _fsync,  # pyright: ignore[reportPrivateUsage]
    _read_exact,  # pyright: ignore[reportPrivateUsage]
    _read_regular,  # pyright: ignore[reportPrivateUsage]
    _safe_directory,  # pyright: ignore[reportPrivateUsage]
    _write_immutable,  # pyright: ignore[reportPrivateUsage]
)

SNAPSHOT_PATH = "snapshots/benchmark/vs01-b08-runtime-pair/reference-screening.json"
RECEIPT_PATH = "manifests/benchmark/vs01-b08-runtime-pair/reference-screening/runtime-screening-receipt.json"
_FORBIDDEN_LEDGER_FIELDS = (
    "database_writes",
    "t03_reads",
    "raw_source_reads",
    "model_invocations",
    "ocr_invocations",
    "vlm_invocations",
    "network_invocations",
    "cloud_invocations",
)


@dataclass(frozen=True)
class RetainedPublicationAuthority:
    retained_receipt: VS01RuntimeScreeningReceipt
    retained_receipt_id: UUID
    retained_receipt_file_sha256: str


CanonicalRecoveryState = Literal["EMPTY", "OBJECT_ONLY", "OBJECT_AND_SNAPSHOT", "COMPLETE"]


@dataclass(frozen=True)
class PublicationInspection:
    recovery_state: CanonicalRecoveryState
    retained: RetainedPublicationAuthority | None


@dataclass(frozen=True)
class _StoreContext:
    result: VS01B08RuntimePairResult
    run: VS01RuntimeAcquisitionRun
    root: Path
    fingerprints: tuple[tuple[str, str], ...]
    ledger: RuntimeControllerLedger
    loader: Callable[[], tuple[tuple[str, str], ...]]
    implementation_commit: str
    new_uuid: Callable[[], UUID]
    now: Callable[[], datetime]


def canonical_pair_result_bytes(result: VS01B08RuntimePairResult) -> bytes:
    return rfc8785.dumps(result.model_dump(mode="json"))


def publication_paths(result_sha256: str) -> tuple[str, str, str, str]:
    stage = f".incoming/vs01-b08-runtime-pair-{result_sha256}.runtime-screening-stage"
    return (f"objects/sha256/{result_sha256[:2]}/{result_sha256}", SNAPSHOT_PATH, RECEIPT_PATH, stage)


def _ledger_state(
    disposition: str, recovery_state: CanonicalRecoveryState | None
) -> tuple[int, int, int, int, bool, bool]:
    states: dict[tuple[str, CanonicalRecoveryState | None], tuple[int, int, int, int, bool, bool]] = {
        ("DRY_RUN_VALIDATED", None): (0, 0, 0, 0, False, False),
        ("REFERENCE_NONCONFORMANT", None): (0, 0, 0, 0, False, False),
        ("REFERENCE_CONFORMANT", "EMPTY"): (FRESH_PUBLICATION_VERIFICATIONS, 1, 1, 3, True, False),
        ("REFERENCE_CONFORMANT", "OBJECT_ONLY"): (FRESH_PUBLICATION_VERIFICATIONS, 1, 1, 2, True, False),
        ("REFERENCE_CONFORMANT", "OBJECT_AND_SNAPSHOT"): (FRESH_PUBLICATION_VERIFICATIONS, 1, 1, 1, True, False),
        ("VERIFIED_EXISTING", "COMPLETE"): (VERIFIED_EXISTING_VERIFICATIONS, 0, 0, 0, False, True),
    }
    try:
        return states[(disposition, recovery_state)]
    except KeyError:
        raise ValueError("runtime screening recovery state contradicts disposition") from None


def validate_screening_receipt(receipt: VS01RuntimeScreeningReceipt) -> None:
    verifications, attempts, successes, writes, published, existing = _ledger_state(
        receipt.disposition, receipt.canonical_recovery_state
    )
    ledger = receipt.operation_ledger
    phases = (
        receipt.authority_fingerprints_initial,
        receipt.authority_fingerprints_pre_store,
        receipt.authority_fingerprints_post_store,
    )
    retained = receipt.retained_publication_receipt
    retained_bytes = _receipt_bytes(retained) if retained else None
    exact = (
        receipt.receipt_id.version == 7,
        receipt.generated_at.tzinfo is not None,
        receipt.pair_specification_identity == SPEC_IDENTITY,
        receipt.pair_result_identity == receipt.pair_result.pair_result_identity,
        receipt.acquisition_run_identity == receipt.pair_result.acquisition_run_identity,
        receipt.pair_result_file_sha256 == hashlib.sha256(canonical_pair_result_bytes(receipt.pair_result)).hexdigest(),
        (receipt.pair_result.disposition == "REFERENCE_CONFORMANT")
        == (receipt.disposition != "REFERENCE_NONCONFORMANT"),
        Path(receipt.archive_root).is_absolute(),
        receipt.archive_paths == publication_paths(receipt.pair_result_file_sha256),
        all(tuple(name for name, _value in phase) == FINGERPRINT_NAMES for phase in phases),
        phases[0] == phases[1] == phases[2],
        (ledger.subject_invocations, ledger.broker_tool_calls, ledger.scoring_invocations) == (2, 14, 1),
        (ledger.acquisition_runs_constructed, ledger.pair_results_constructed, ledger.receipts_constructed)
        == (2, 1, 1),
        (ledger.store_verification_attempts, ledger.publication_attempts) == (verifications, attempts),
        (ledger.successful_publications, ledger.canonical_archive_writes) == (successes, writes),
        all(getattr(ledger, field) == 0 for field in _FORBIDDEN_LEDGER_FIELDS),
        (receipt.published, receipt.verified_existing) == (published, existing),
        retained is not None if existing else retained is None,
        receipt.retained_publication_receipt_id == retained.receipt_id
        if retained
        else receipt.retained_publication_receipt_id is None,
        receipt.retained_publication_receipt_file_sha256 == hashlib.sha256(retained_bytes).hexdigest()
        if retained_bytes
        else receipt.retained_publication_receipt_file_sha256 is None,
        retained.implementation_commit == receipt.implementation_commit if retained else True,
        retained.pair_result_identity == receipt.pair_result_identity if retained else True,
        retained.acquisition_run_identity == receipt.acquisition_run_identity if retained else True,
        retained.authority_fingerprints_initial == phases[0] if retained else True,
    )
    body = receipt.model_dump(mode="json", exclude={"receipt_canonical_sha256"})
    if not all(exact) or receipt.receipt_canonical_sha256 != canonical_sha256(body):
        raise ValueError("runtime screening receipt authority differs")


def build_screening_receipt(
    result: VS01B08RuntimePairResult,
    run: VS01RuntimeAcquisitionRun,
    root: Path,
    fingerprints: tuple[tuple[str, str], ...],
    *,
    pre_store_fingerprints: tuple[tuple[str, str], ...],
    post_store_fingerprints: tuple[tuple[str, str], ...],
    recovery_state: CanonicalRecoveryState | None,
    operation_ledger: RuntimeControllerLedger,
    disposition: str,
    implementation_commit: str,
    new_uuid: Callable[[], UUID],
    now: Callable[[], datetime],
    retained: RetainedPublicationAuthority | None = None,
) -> VS01RuntimeScreeningReceipt:
    result_sha = hashlib.sha256(canonical_pair_result_bytes(result)).hexdigest()
    payload: dict[str, Any] = {
        "receipt_id": new_uuid(),
        "generated_at": now(),
        "implementation_commit": implementation_commit,
        "pair_specification_identity": result.pair_specification_identity,
        "acquisition_run_identity": run.acquisition_run_identity,
        "pair_result": result,
        "pair_result_identity": result.pair_result_identity,
        "pair_result_file_sha256": result_sha,
        "archive_root": str(root),
        "archive_paths": publication_paths(result_sha),
        "disposition": disposition,
        "published": disposition == "REFERENCE_CONFORMANT",
        "verified_existing": disposition == "VERIFIED_EXISTING",
        "authority_fingerprints_initial": fingerprints,
        "authority_fingerprints_pre_store": pre_store_fingerprints,
        "authority_fingerprints_post_store": post_store_fingerprints,
        "canonical_recovery_state": recovery_state,
        "operation_ledger": operation_ledger,
        "retained_publication_receipt": retained.retained_receipt if retained else None,
        "retained_publication_receipt_id": retained.retained_receipt_id if retained else None,
        "retained_publication_receipt_file_sha256": retained.retained_receipt_file_sha256 if retained else None,
    }
    body = VS01RuntimeScreeningReceipt.model_construct(**payload).model_dump(
        mode="json", exclude={"receipt_canonical_sha256"}
    )
    return VS01RuntimeScreeningReceipt.model_validate_json(
        rfc8785.dumps(body | {"receipt_canonical_sha256": canonical_sha256(body)})
    )


def _increment(ledger: RuntimeControllerLedger, **increments: int) -> RuntimeControllerLedger:
    payload = ledger.model_dump(mode="python")
    for name, value in increments.items():
        payload[name] += value
    return RuntimeControllerLedger.model_validate(payload)


def complete_store_decision(
    result: VS01B08RuntimePairResult,
    run: VS01RuntimeAcquisitionRun,
    root: Path,
    fingerprints: tuple[tuple[str, str], ...],
    ledger: RuntimeControllerLedger,
    *,
    dry_run: bool,
    authority_loader: Callable[[], tuple[tuple[str, str], ...]] | None,
    implementation_commit: str,
    new_uuid: Callable[[], UUID],
    now: Callable[[], datetime],
) -> tuple[VS01RuntimeScreeningReceipt, bool]:
    if dry_run or result.disposition != "REFERENCE_CONFORMANT":
        disposition = (
            "DRY_RUN_VALIDATED"
            if dry_run and result.disposition == "REFERENCE_CONFORMANT"
            else "REFERENCE_NONCONFORMANT"
        )
        receipt = build_screening_receipt(
            result,
            run,
            root,
            fingerprints,
            pre_store_fingerprints=fingerprints,
            post_store_fingerprints=fingerprints,
            recovery_state=None,
            operation_ledger=_increment(ledger, receipts_constructed=1),
            disposition=disposition,
            implementation_commit=implementation_commit,
            new_uuid=new_uuid,
            now=now,
        )
        return receipt, False
    if authority_loader is None:
        raise ValueError("non-dry runtime store path requires an authority reload")
    context = _StoreContext(
        result, run, root, fingerprints, ledger, authority_loader, implementation_commit, new_uuid, now
    )
    return _complete_non_dry(context)


def _complete_non_dry(context: _StoreContext) -> tuple[VS01RuntimeScreeningReceipt, bool]:
    result, run, root = context.result, context.run, context.root
    fingerprints, authority_loader = context.fingerprints, context.loader
    if (pre_store := authority_loader()) != fingerprints:
        raise ValueError("upstream runtime authority changed before store decision")
    checked = _increment(context.ledger, store_verification_attempts=1)
    inspection = verify_existing(
        root,
        result,
        canonical_pair_result_bytes(result),
        implementation_commit=context.implementation_commit,
        fingerprints=fingerprints,
    )
    if inspection.recovery_state == "COMPLETE":
        retained, post_store = _retained_post_store(root, result, inspection, authority_loader, fingerprints)
        receipt = build_screening_receipt(
            result,
            run,
            root,
            fingerprints,
            pre_store_fingerprints=pre_store,
            post_store_fingerprints=post_store,
            recovery_state="COMPLETE",
            operation_ledger=_increment(checked, receipts_constructed=1),
            disposition="VERIFIED_EXISTING",
            implementation_commit=context.implementation_commit,
            new_uuid=context.new_uuid,
            now=context.now,
            retained=retained,
        )
        return receipt, False
    result_writes = _prepare_result_store(root, result, inspection.recovery_state)
    if (post_store := authority_loader()) != fingerprints:
        raise ValueError("upstream runtime authority changed after store mutation")
    expected_writes = result_writes + 1
    increments = {
        "receipts_constructed": 1,
        "store_verification_attempts": 1,
        "publication_attempts": 1,
        "successful_publications": 1,
        "canonical_archive_writes": expected_writes,
    }
    receipt = build_screening_receipt(
        result,
        run,
        root,
        fingerprints,
        pre_store_fingerprints=pre_store,
        post_store_fingerprints=post_store,
        recovery_state=inspection.recovery_state,
        operation_ledger=_increment(checked, **increments),
        disposition="REFERENCE_CONFORMANT",
        implementation_commit=context.implementation_commit,
        new_uuid=context.new_uuid,
        now=context.now,
    )
    if result_writes + publish_runtime_screening(root, result, receipt) != expected_writes:
        raise ValueError("runtime screening canonical-write ledger differs")
    return receipt, True


def _retained_post_store(
    root: Path,
    result: VS01B08RuntimePairResult,
    inspection: PublicationInspection,
    loader: Callable[[], tuple[tuple[str, str], ...]],
    fingerprints: tuple[tuple[str, str], ...],
) -> tuple[RetainedPublicationAuthority, tuple[tuple[str, str], ...]]:
    retained = inspection.retained
    if retained is None:
        raise ValueError("complete runtime screening publication lacks retained authority")
    result_bytes = canonical_pair_result_bytes(result)
    _clean_exact_stage(
        root,
        hashlib.sha256(result_bytes).hexdigest(),
        {"object": result_bytes, "snapshot": result_bytes, "receipt": _receipt_bytes(retained.retained_receipt)},
    )
    post_store = loader()
    if post_store != fingerprints:
        raise ValueError("upstream runtime authority changed after store decision")
    return retained, post_store


def _receipt_bytes(receipt: VS01RuntimeScreeningReceipt) -> bytes:
    return rfc8785.dumps(receipt.model_dump(mode="json"))


def _validated_receipt(
    path: Path,
    root: Path,
    result: VS01B08RuntimePairResult,
    result_bytes: bytes,
    *,
    implementation_commit: str,
    fingerprints: tuple[tuple[str, str], ...],
) -> RetainedPublicationAuthority:
    try:
        data, metadata = _read_regular(path)
        receipt = VS01RuntimeScreeningReceipt.model_validate_json(data)
    except (ValueError, ValidationError):
        raise ValueError("existing runtime screening receipt is invalid") from None
    result_sha = hashlib.sha256(result_bytes).hexdigest()
    expected = (
        stat.S_IMODE(metadata.st_mode) == 0o444,
        data == _receipt_bytes(receipt),
        receipt.pair_result_identity == result.pair_result_identity,
        receipt.acquisition_run_identity == result.acquisition_run_identity,
        receipt.pair_result_file_sha256 == result_sha,
        receipt.implementation_commit == implementation_commit,
        receipt.archive_root == str(root),
        receipt.archive_paths == publication_paths(result_sha),
        receipt.authority_fingerprints_initial == fingerprints,
        receipt.authority_fingerprints_pre_store == fingerprints,
        receipt.authority_fingerprints_post_store == fingerprints,
        receipt.disposition == "REFERENCE_CONFORMANT",
        receipt.published is True,
        receipt.verified_existing is False,
    )
    if not all(expected):
        raise ValueError("existing runtime screening receipt authority differs")
    return RetainedPublicationAuthority(receipt, receipt.receipt_id, hashlib.sha256(data).hexdigest())


def verify_existing(
    root: Path,
    result: VS01B08RuntimePairResult,
    result_bytes: bytes,
    *,
    implementation_commit: str,
    fingerprints: tuple[tuple[str, str], ...],
) -> PublicationInspection:
    result_sha = hashlib.sha256(result_bytes).hexdigest()
    resolved = tuple(_existing_file(root, item) for item in publication_paths(result_sha)[:3])
    paths = tuple(item[0] for item in resolved)
    states = cast(tuple[bool, bool, bool], tuple(item[1] for item in resolved))
    recovery = {
        (False, False, False): "EMPTY",
        (True, False, False): "OBJECT_ONLY",
        (True, True, False): "OBJECT_AND_SNAPSHOT",
        (True, True, True): "COMPLETE",
    }.get(states)
    if recovery is None:
        raise ValueError("runtime screening publication prerequisite is missing")
    if states[0]:
        _read_exact(paths[0], result_bytes)
    if states[1]:
        _read_exact(paths[1], result_bytes)
    retained = None
    if states[2]:
        retained = _validated_receipt(
            paths[2],
            root,
            result,
            result_bytes,
            implementation_commit=implementation_commit,
            fingerprints=fingerprints,
        )
    return PublicationInspection(cast(CanonicalRecoveryState, recovery), retained)


def _clean_exact_stage(root: Path, result_sha: str, payloads: dict[str, bytes]) -> None:
    incoming = _safe_directory(root, ".incoming")
    stage = incoming / Path(publication_paths(result_sha)[3]).name
    try:
        metadata = stage.lstat()
    except FileNotFoundError:
        return
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise ValueError("result-bound runtime screening stage is unsafe")
    contents = {item.name: item for item in stage.iterdir()}
    if set(contents) - set(payloads):
        raise ValueError("result-bound runtime screening stage contains unexpected content")
    for name, path in contents.items():
        _read_exact(path, payloads[name])
    for path in contents.values():
        path.unlink()
    stage.rmdir()
    _fsync(incoming)


def _link_exact(source: Path, destination: Path, expected: bytes) -> bool:
    try:
        os.link(source, destination, follow_symlinks=False)
    except FileExistsError:
        _read_exact(destination, expected)
        return False
    _fsync(destination.parent)
    return True


def _prepare_result_store(root: Path, result: VS01B08RuntimePairResult, recovery: CanonicalRecoveryState) -> int:
    result_bytes = canonical_pair_result_bytes(result)
    result_sha = hashlib.sha256(result_bytes).hexdigest()
    payloads = {"object": result_bytes, "snapshot": result_bytes}
    _clean_exact_stage(root, result_sha, payloads)
    stage = _safe_directory(root, ".incoming", Path(publication_paths(result_sha)[3]).name)
    for name, data in payloads.items():
        _write_immutable(stage / name, data)
    destinations = tuple(root / item for item in publication_paths(result_sha)[:3])
    first_missing = {"EMPTY": 0, "OBJECT_ONLY": 1, "OBJECT_AND_SNAPSHOT": 2}[recovery]
    writes = 0
    for index, name in enumerate(payloads):
        if index < first_missing:
            continue
        destination = destinations[index]
        _safe_directory(root, *destination.relative_to(root).parent.parts)
        writes += int(_link_exact(stage / name, destination, payloads[name]))
    _clean_exact_stage(root, result_sha, payloads)
    if writes != 2 - first_missing:
        raise ValueError("runtime screening result-link recovery differs")
    return writes


def publish_runtime_screening(
    root: Path, result: VS01B08RuntimePairResult, receipt: VS01RuntimeScreeningReceipt
) -> int:
    result_bytes = canonical_pair_result_bytes(result)
    result_sha = hashlib.sha256(result_bytes).hexdigest()
    payloads = {"receipt": _receipt_bytes(receipt)}
    _clean_exact_stage(root, result_sha, payloads)
    stage = _safe_directory(root, ".incoming", Path(publication_paths(result_sha)[3]).name)
    _write_immutable(stage / "receipt", payloads["receipt"])
    destination = root / publication_paths(result_sha)[2]
    _safe_directory(root, *destination.relative_to(root).parent.parts)
    if not _link_exact(stage / "receipt", destination, payloads["receipt"]):
        raise ValueError("runtime screening receipt link was not newly created")
    verified = verify_existing(
        root,
        result,
        result_bytes,
        implementation_commit=receipt.implementation_commit,
        fingerprints=receipt.authority_fingerprints_initial,
    )
    if verified.recovery_state != "COMPLETE" or verified.retained is None:
        raise ValueError("runtime screening publication verification failed")
    _clean_exact_stage(root, result_sha, payloads)
    return 1
