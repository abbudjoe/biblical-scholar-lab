from __future__ import annotations

import hashlib
import stat
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

import rfc8785
from pydantic import ValidationError

from bsl.contracts.runtime_screening import (
    REAL_COUNTER_NAMES,
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


def canonical_pair_result_bytes(result: VS01B08RuntimePairResult) -> bytes:
    return rfc8785.dumps(result.model_dump(mode="json"))


def publication_paths(result_sha256: str) -> tuple[str, str, str, str]:
    stage = f".incoming/vs01-b08-runtime-pair-{result_sha256}.runtime-screening-stage"
    return (
        f"objects/sha256/{result_sha256[:2]}/{result_sha256}",
        SNAPSHOT_PATH,
        RECEIPT_PATH,
        stage,
    )


def build_screening_receipt(
    result: VS01B08RuntimePairResult,
    run: VS01RuntimeAcquisitionRun,
    root: Path,
    fingerprints: tuple[tuple[str, str], ...],
    *,
    disposition: str,
    implementation_commit: str,
    new_uuid: Callable[[], UUID],
    now: Callable[[], datetime],
) -> VS01RuntimeScreeningReceipt:
    result_sha = hashlib.sha256(canonical_pair_result_bytes(result)).hexdigest()
    state = {
        "DRY_RUN_VALIDATED": (False, False),
        "REFERENCE_CONFORMANT": (True, False),
        "REFERENCE_NONCONFORMANT": (False, False),
        "VERIFIED_EXISTING": (False, True),
    }[disposition]
    payload: dict[str, Any] = {
        "receipt_id": new_uuid(),
        "generated_at": now(),
        "implementation_commit": implementation_commit,
        "pair_specification_identity": result.pair_specification_identity,
        "acquisition_run_identity": run.acquisition_run_identity,
        "pair_result_identity": result.pair_result_identity,
        "pair_result_file_sha256": result_sha,
        "archive_root": str(root),
        "archive_paths": publication_paths(result_sha),
        "disposition": disposition,
        "published": state[0],
        "verified_existing": state[1],
        "authority_fingerprints_before": fingerprints,
        "authority_fingerprints_after": fingerprints,
        "real_operation_counters": tuple((name, 0) for name in REAL_COUNTER_NAMES),
    }
    draft = VS01RuntimeScreeningReceipt.model_construct(**payload, receipt_canonical_sha256="0" * 64)
    body = draft.model_dump(mode="json", exclude={"receipt_canonical_sha256"})
    return VS01RuntimeScreeningReceipt.model_validate_json(
        rfc8785.dumps(body | {"receipt_canonical_sha256": canonical_sha256(body)})
    )


def _receipt_bytes(receipt: VS01RuntimeScreeningReceipt) -> bytes:
    return rfc8785.dumps(receipt.model_dump(mode="json"))


def _validated_receipt(
    path: Path,
    root: Path,
    result: VS01B08RuntimePairResult,
    result_bytes: bytes,
) -> VS01RuntimeScreeningReceipt:
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
        receipt.pair_result_file_sha256 == result_sha,
        receipt.archive_root == str(root),
        receipt.archive_paths == publication_paths(result_sha),
        receipt.disposition == "REFERENCE_CONFORMANT",
        receipt.published is True,
        receipt.verified_existing is False,
        all(value == 0 for _name, value in receipt.real_operation_counters),
    )
    if not all(expected):
        raise ValueError("existing runtime screening receipt authority differs")
    return receipt


def verify_existing(
    root: Path,
    result: VS01B08RuntimePairResult,
    result_bytes: bytes,
) -> VS01RuntimeScreeningReceipt | None:
    result_sha = hashlib.sha256(result_bytes).hexdigest()
    resolved = tuple(_existing_file(root, item) for item in publication_paths(result_sha)[:3])
    paths = tuple(item[0] for item in resolved)
    states = tuple(item[1] for item in resolved)
    if not any(states):
        return None
    if states[2] and not all(states[:2]) or states[1] and not states[0]:
        raise ValueError("runtime screening publication prerequisite is missing")
    _read_exact(paths[0], result_bytes)
    if states[1]:
        _read_exact(paths[1], result_bytes)
    return _validated_receipt(paths[2], root, result, result_bytes) if states[2] else None


def _clean_exact_stage(
    root: Path,
    result: VS01B08RuntimePairResult,
    result_bytes: bytes,
    receipt: VS01RuntimeScreeningReceipt,
) -> None:
    result_sha = hashlib.sha256(result_bytes).hexdigest()
    incoming = _safe_directory(root, ".incoming")
    stage = incoming / Path(publication_paths(result_sha)[3]).name
    try:
        metadata = stage.lstat()
    except FileNotFoundError:
        return
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise ValueError("result-bound runtime screening stage is unsafe")
    payloads = {"object": result_bytes, "snapshot": result_bytes, "receipt": _receipt_bytes(receipt)}
    contents = {item.name: item for item in stage.iterdir()}
    if set(contents) - set(payloads):
        raise ValueError("result-bound runtime screening stage contains unexpected content")
    for name, path in contents.items():
        if name == "receipt":
            _validated_receipt(path, root, result, result_bytes)
        else:
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
    if verify_existing(root, result, result_bytes) is not None:
        raise ValueError("runtime screening publication already exists")
    stage = _safe_directory(root, ".incoming", Path(publication_paths(result_sha)[3]).name)
    payloads = {"object": result_bytes, "snapshot": result_bytes, "receipt": _receipt_bytes(receipt)}
    contents = {item.name: item for item in stage.iterdir()}
    if set(contents) - set(payloads):
        raise ValueError("result-bound runtime screening stage contains unexpected content")
    for name, data in payloads.items():
        path = stage / name
        if name in contents:
            _read_exact(path, data)
        else:
            _write_immutable(path, data)
    destinations = tuple(root / item for item in publication_paths(result_sha)[:3])
    for name, destination in zip(payloads, destinations, strict=True):
        _safe_directory(root, *destination.relative_to(root).parent.parts)
        _link(stage / name, destination, payloads[name])
    if verify_existing(root, result, result_bytes) is None:
        raise ValueError("runtime screening publication verification failed")
    _clean_exact_stage(root, result, result_bytes, receipt)
