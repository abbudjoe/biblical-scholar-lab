from __future__ import annotations

import hashlib
import stat
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
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
    _link,  # pyright: ignore[reportPrivateUsage]
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


def canonical_pair_result_bytes(result: VS01B08RuntimePairResult) -> bytes:
    return rfc8785.dumps(result.model_dump(mode="json"))


def publication_paths(result_sha256: str) -> tuple[str, str, str, str]:
    stage = f".incoming/vs01-b08-runtime-pair-{result_sha256}.runtime-screening-stage"
    return (f"objects/sha256/{result_sha256[:2]}/{result_sha256}", SNAPSHOT_PATH, RECEIPT_PATH, stage)


def _ledger_state(disposition: str) -> tuple[int, int, int, int, bool, bool]:
    return {
        "DRY_RUN_VALIDATED": (0, 0, 0, 0, False, False),
        "REFERENCE_NONCONFORMANT": (0, 0, 0, 0, False, False),
        "REFERENCE_CONFORMANT": (FRESH_PUBLICATION_VERIFICATIONS, 1, 1, 3, True, False),
        "VERIFIED_EXISTING": (VERIFIED_EXISTING_VERIFICATIONS, 0, 0, 0, False, True),
    }[disposition]


def validate_screening_receipt(receipt: VS01RuntimeScreeningReceipt) -> None:
    verifications, attempts, successes, writes, published, existing = _ledger_state(receipt.disposition)
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


def screening_receipt_schema(schema: dict[str, Any]) -> None:
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["properties"]["pair_specification_identity"] = {"const": SPEC_IDENTITY}
    variants: list[dict[str, Any]] = []
    for disposition in ("DRY_RUN_VALIDATED", "REFERENCE_CONFORMANT", "REFERENCE_NONCONFORMANT", "VERIFIED_EXISTING"):
        verify, attempts, successes, writes, published, existing = _ledger_state(disposition)
        ledger = {
            "subject_invocations": 2,
            "broker_tool_calls": 14,
            "scoring_invocations": 1,
            "acquisition_runs_constructed": 2,
            "pair_results_constructed": 1,
            "receipts_constructed": 1,
            "store_verification_attempts": verify,
            "publication_attempts": attempts,
            "successful_publications": successes,
            "canonical_archive_writes": writes,
            **dict.fromkeys(_FORBIDDEN_LEDGER_FIELDS, 0),
        }
        retained = {"type": "string", "format": "uuid"} if existing else {"type": "null"}
        retained_sha = {"type": "string", "pattern": "^[0-9a-f]{64}$"} if existing else {"type": "null"}
        variants.append(
            {
                "properties": {
                    "disposition": {"const": disposition},
                    "published": {"const": published},
                    "verified_existing": {"const": existing},
                    "operation_ledger": {"const": ledger},
                    "pair_result": {
                        "properties": {
                            "disposition": {"not": {"const": "REFERENCE_CONFORMANT"}}
                            if disposition == "REFERENCE_NONCONFORMANT"
                            else {"const": "REFERENCE_CONFORMANT"}
                        }
                    },
                    "retained_publication_receipt": {"type": "object"} if existing else {"type": "null"},
                    "retained_publication_receipt_id": retained,
                    "retained_publication_receipt_file_sha256": retained_sha,
                }
            }
        )
    schema["oneOf"] = variants


def build_screening_receipt(
    result: VS01B08RuntimePairResult,
    run: VS01RuntimeAcquisitionRun,
    root: Path,
    fingerprints: tuple[tuple[str, str], ...],
    *,
    pre_store_fingerprints: tuple[tuple[str, str], ...],
    post_store_fingerprints: tuple[tuple[str, str], ...],
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
            operation_ledger=_increment(ledger, receipts_constructed=1),
            disposition=disposition,
            implementation_commit=implementation_commit,
            new_uuid=new_uuid,
            now=now,
        )
        return receipt, False
    return _complete_non_dry(
        result,
        run,
        root,
        fingerprints,
        ledger,
        authority_loader=authority_loader,
        implementation_commit=implementation_commit,
        new_uuid=new_uuid,
        now=now,
    )


def _complete_non_dry(
    result: VS01B08RuntimePairResult,
    run: VS01RuntimeAcquisitionRun,
    root: Path,
    fingerprints: tuple[tuple[str, str], ...],
    ledger: RuntimeControllerLedger,
    *,
    authority_loader: Callable[[], tuple[tuple[str, str], ...]] | None,
    implementation_commit: str,
    new_uuid: Callable[[], UUID],
    now: Callable[[], datetime],
) -> tuple[VS01RuntimeScreeningReceipt, bool]:
    if authority_loader is None:
        raise ValueError("non-dry runtime store path requires an authority reload")
    pre_store = authority_loader()
    if pre_store != fingerprints:
        raise ValueError("upstream runtime authority changed before store decision")
    checked = _increment(ledger, store_verification_attempts=1)
    retained = verify_existing(
        root,
        result,
        canonical_pair_result_bytes(result),
        implementation_commit=implementation_commit,
        fingerprints=fingerprints,
    )
    post_store = authority_loader()
    if post_store != fingerprints:
        raise ValueError("upstream runtime authority changed after store decision")
    increments = {"receipts_constructed": 1}
    disposition, published = "VERIFIED_EXISTING", False
    if retained is None:
        increments |= {
            "store_verification_attempts": 1,
            "publication_attempts": 1,
            "successful_publications": 1,
            "canonical_archive_writes": 3,
        }
        disposition, published = "REFERENCE_CONFORMANT", True
    receipt = build_screening_receipt(
        result,
        run,
        root,
        fingerprints,
        pre_store_fingerprints=pre_store,
        post_store_fingerprints=post_store,
        operation_ledger=_increment(checked, **increments),
        disposition=disposition,
        implementation_commit=implementation_commit,
        new_uuid=new_uuid,
        now=now,
        retained=retained,
    )
    if published:
        publish_runtime_screening(root, result, receipt)
    return receipt, published


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
) -> RetainedPublicationAuthority | None:
    result_sha = hashlib.sha256(result_bytes).hexdigest()
    resolved = tuple(_existing_file(root, item) for item in publication_paths(result_sha)[:3])
    paths, states = tuple(item[0] for item in resolved), tuple(item[1] for item in resolved)
    if not any(states):
        return None
    if states[2] and not all(states[:2]) or states[1] and not states[0]:
        raise ValueError("runtime screening publication prerequisite is missing")
    _read_exact(paths[0], result_bytes)
    if states[1]:
        _read_exact(paths[1], result_bytes)
    if not states[2]:
        return None
    return _validated_receipt(
        paths[2],
        root,
        result,
        result_bytes,
        implementation_commit=implementation_commit,
        fingerprints=fingerprints,
    )


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


def publish_runtime_screening(
    root: Path,
    result: VS01B08RuntimePairResult,
    receipt: VS01RuntimeScreeningReceipt,
) -> None:
    result_bytes = canonical_pair_result_bytes(result)
    result_sha = hashlib.sha256(result_bytes).hexdigest()
    stage = _safe_directory(root, ".incoming", Path(publication_paths(result_sha)[3]).name)
    payloads = {"object": result_bytes, "snapshot": result_bytes, "receipt": _receipt_bytes(receipt)}
    contents = {item.name: item for item in stage.iterdir()}
    if set(contents) - set(payloads):
        raise ValueError("result-bound runtime screening stage contains unexpected content")
    for name, data in payloads.items():
        path = stage / name
        _read_exact(path, data) if name in contents else _write_immutable(path, data)
    destinations = tuple(root / item for item in publication_paths(result_sha)[:3])
    for name, destination in zip(payloads, destinations, strict=True):
        _safe_directory(root, *destination.relative_to(root).parent.parts)
        _link(stage / name, destination, payloads[name])
    if (
        verify_existing(
            root,
            result,
            result_bytes,
            implementation_commit=receipt.implementation_commit,
            fingerprints=receipt.authority_fingerprints_initial,
        )
        is None
    ):
        raise ValueError("runtime screening publication verification failed")
    _clean_exact_stage(root, result_sha, payloads)
