from __future__ import annotations

import hashlib
import os
import stat
import subprocess
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

import rfc8785
from pydantic import ValidationError

from bsl.application.vs01_benchmark import canonical_sha256
from bsl.contracts.benchmark import (
    VS01BenchmarkExecutionReceipt,
    VS01BenchmarkExecutionSpecification,
    VS01BenchmarkRunResult,
)

SNAPSHOT_PATH = "snapshots/benchmark/vs01-batch-01/reference-conformance.json"
RECEIPT_PATH = "manifests/benchmark/vs01-batch-01/reference-conformance/benchmark-execution-receipt.json"


def implementation_head() -> str:
    completed = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True, timeout=10)
    head = completed.stdout.strip()
    if len(head) != 40 or any(character not in "0123456789abcdef" for character in head):
        raise ValueError("implementation commit is invalid")
    return head


def _inventory(path: Path, *, contents: bool) -> str:
    metadata = path.lstat()
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise ValueError("benchmark archive authority is unsafe")
    value: Any = (metadata.st_dev, metadata.st_ino, metadata.st_mode & 0o7777)
    if contents:
        value = tuple(sorted((item.name, item.lstat().st_mode & 0o170000) for item in path.iterdir()))
    return canonical_sha256(value)


def verify_upstream_authority(root: Path) -> tuple[tuple[str, str], ...]:
    from bsl.application.john15_page_fixture import (
        _fixture_assets,  # pyright: ignore[reportPrivateUsage]
        verify_t05_owner,
    )
    from bsl.application.john15_study_runtime import (
        _authority_fingerprint,  # pyright: ignore[reportPrivateUsage]
        load_t04_authority,
    )
    from bsl.infrastructure.page_fixture_store import verify_existing as verify_page_fixture

    t04 = load_t04_authority(root)
    t05 = verify_t05_owner(t04)
    fixture, base, degraded, fixture_bytes = _fixture_assets()
    t06 = verify_page_fixture(root, fixture, base, degraded, fixture_bytes)
    if t06 is None or str(t06.receipt_identity) != "01a034c2-d6e4-73f4-91b2-7410e7453783":
        raise ValueError("canonical T06 authority differs")
    return (
        ("t04", _authority_fingerprint(t04)),
        ("t05", canonical_sha256(t05)),
        ("t06", canonical_sha256(t06.model_dump(mode="json"))),
        ("archive_root", _inventory(root, contents=False)),
        ("incoming_inventory", _inventory(root / ".incoming", contents=True)),
    )


def canonical_run_result_bytes(result: VS01BenchmarkRunResult) -> bytes:
    return rfc8785.dumps(result.model_dump(mode="json"))


def build_execution_receipt(
    specification: VS01BenchmarkExecutionSpecification,
    result: VS01BenchmarkRunResult,
    root: Path,
    operation_counts: dict[str, int],
    initial: tuple[tuple[str, str], ...],
    pre_store: tuple[tuple[str, str], ...],
    *,
    disposition: str,
    implementation_commit: str,
    new_uuid: Callable[[], UUID],
    now: Callable[[], datetime],
    retained: VS01BenchmarkExecutionReceipt | None = None,
) -> VS01BenchmarkExecutionReceipt:
    result_sha = hashlib.sha256(canonical_run_result_bytes(result)).hexdigest()
    retained_sha = hashlib.sha256(_receipt_bytes(retained)).hexdigest() if retained else None
    values = {
        "DRY_RUN_VALIDATED": (True, False, False, 0),
        "REFERENCE_CONFORMANT": (False, True, False, 3),
        "REFERENCE_NONCONFORMANT": (False, False, False, 0),
        "VERIFIED_EXISTING": (False, False, True, 0),
    }[disposition]
    return VS01BenchmarkExecutionReceipt.model_validate(
        {
            "receipt_id": new_uuid(),
            "generated_at": now(),
            "execution_specification_identity": specification.specification_identity,
            "run_result_identity": result.run_result_identity,
            "run_result_file_sha256": result_sha,
            "implementation_commit": implementation_commit,
            "archive_root": str(root),
            "archive_paths": publication_paths(result_sha),
            "disposition": disposition,
            "dry_run": values[0],
            "published": values[1],
            "verified_existing": values[2],
            "initial_upstream_fingerprints": initial,
            "pre_store_upstream_fingerprints": pre_store,
            **operation_counts,
            "retained_publication_receipt_id": retained.receipt_id if retained else None,
            "retained_publication_receipt_sha256": retained_sha,
            "completed_attempts": result.completed_attempts,
            "error_counts": result.failure_counts,
            "archive_writes": values[3],
        }
    )


def publication_paths(result_sha256: str) -> tuple[str, str, str]:
    return f"objects/sha256/{result_sha256[:2]}/{result_sha256}", SNAPSHOT_PATH, RECEIPT_PATH


def benchmark_stage_path(root: Path, result_sha256: str) -> Path:
    return root / ".incoming" / f"vs01-batch-01-{result_sha256}.benchmark-stage"


def _metadata(path: Path) -> os.stat_result:
    try:
        return path.lstat()
    except OSError:
        raise ValueError(f"benchmark publication path is missing or unsafe: {path.name}") from None


def _safe_directory(root: Path, *parts: str, create: bool = True) -> Path:
    if root.is_symlink() or not stat.S_ISDIR(_metadata(root).st_mode):
        raise ValueError("benchmark publication root is unsafe")
    current = root
    for part in parts:
        if part in {"", ".", ".."} or Path(part).is_absolute() or "/" in part:
            raise ValueError("benchmark publication path escapes its root")
        current /= part
        try:
            metadata = current.lstat()
        except FileNotFoundError:
            if not create:
                raise ValueError(f"benchmark publication path is missing or unsafe: {current.name}") from None
            current.mkdir(mode=0o755)
            metadata = _metadata(current)
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise ValueError(f"benchmark publication directory is unsafe: {current.name}")
    return current


def _fsync(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _read_exact(path: Path, expected: bytes) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        metadata = os.fstat(descriptor)
        with os.fdopen(descriptor, "rb") as stream:
            actual = stream.read()
    except OSError:
        raise ValueError(f"benchmark publication is missing or unsafe: {path.name}") from None
    if not stat.S_ISREG(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) != 0o444 or actual != expected:
        raise ValueError(f"benchmark publication differs or is mutable: {path.name}")


def _existing_file(root: Path, relative: str) -> tuple[Path, bool]:
    parts = Path(relative).parts
    if root.is_symlink() or not stat.S_ISDIR(_metadata(root).st_mode):
        raise ValueError("benchmark publication root is unsafe")
    current = root
    for part in parts[:-1]:
        current /= part
        try:
            metadata = current.lstat()
        except FileNotFoundError:
            return root / relative, False
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise ValueError(f"benchmark publication directory is unsafe: {current.name}")
    path = current / parts[-1]
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return path, False
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ValueError(f"benchmark publication is unsafe: {path.name}")
    return path, True


def _write_immutable(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o444)
    try:
        remaining = memoryview(data)
        while remaining:
            written = os.write(descriptor, remaining)
            if written == 0:
                raise OSError("zero-byte immutable write")
            remaining = remaining[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.chmod(path, 0o444, follow_symlinks=False)
    _read_exact(path, data)
    _fsync(path.parent)


def _receipt_bytes(receipt: VS01BenchmarkExecutionReceipt) -> bytes:
    return rfc8785.dumps(receipt.model_dump(mode="json"))


def _validated_receipt(
    path: Path, root: Path, result: VS01BenchmarkRunResult, result_bytes: bytes, expected: dict[str, Any] | None
) -> VS01BenchmarkExecutionReceipt:
    try:
        data = path.read_bytes()
        receipt = VS01BenchmarkExecutionReceipt.model_validate_json(data)
    except (OSError, ValidationError):
        raise ValueError("existing benchmark receipt is invalid") from None
    if data != _receipt_bytes(receipt):
        raise ValueError("existing benchmark receipt is not canonical")
    result_sha = hashlib.sha256(result_bytes).hexdigest()
    authority = {
        "execution_specification_identity": result.execution_specification_identity,
        "run_result_identity": result.run_result_identity,
        "run_result_file_sha256": result_sha,
        "archive_root": str(root),
        "archive_paths": publication_paths(result_sha),
        "completed_attempts": result.completed_attempts,
        "error_counts": result.failure_counts,
        "disposition": "REFERENCE_CONFORMANT",
        "dry_run": False,
        "published": True,
        "verified_existing": False,
        "archive_writes": 3,
        "publication_attempts": 1,
        "model_invocations": 0,
        "ocr_invocations": 0,
        "vlm_invocations": 0,
        "network_invocations": 0,
        "database_writes": 0,
    }
    observed = receipt.model_dump(mode="python")
    if any(observed.get(key) != value for key, value in (authority | (expected or {})).items()):
        raise ValueError("existing benchmark receipt authority differs")
    _read_exact(path, data)
    return receipt


def verify_existing(
    root: Path, result: VS01BenchmarkRunResult, result_bytes: bytes, expected: dict[str, Any] | None = None
) -> VS01BenchmarkExecutionReceipt | None:
    result_sha = hashlib.sha256(result_bytes).hexdigest()
    resolved = tuple(_existing_file(root, value) for value in publication_paths(result_sha))
    paths, states = tuple(item[0] for item in resolved), tuple(item[1] for item in resolved)
    if not any(states):
        return None
    if states[2] and not all(states[:2]) or states[1] and not states[0]:
        raise ValueError("benchmark publication prerequisite is missing")
    _read_exact(paths[0], result_bytes)
    if states[1]:
        _read_exact(paths[1], result_bytes)
    return _validated_receipt(paths[2], root, result, result_bytes, expected) if states[2] else None


def _clean_exact_stage(
    root: Path, result: VS01BenchmarkRunResult, result_bytes: bytes, receipt: VS01BenchmarkExecutionReceipt
) -> None:
    result_sha = hashlib.sha256(result_bytes).hexdigest()
    incoming = _safe_directory(root, ".incoming")
    stage = incoming / benchmark_stage_path(root, result_sha).name
    try:
        metadata = stage.lstat()
    except FileNotFoundError:
        return
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise ValueError("result-bound benchmark stage is unsafe")
    payloads = {"object": result_bytes, "snapshot": result_bytes, "receipt": _receipt_bytes(receipt)}
    contents = {path.name: path for path in stage.iterdir()}
    if set(contents) - set(payloads):
        raise ValueError("result-bound benchmark stage contains unexpected content")
    for name, path in contents.items():
        _validated_receipt(path, root, result, result_bytes, None) if name == "receipt" else _read_exact(
            path, payloads[name]
        )
    for path in contents.values():
        path.unlink()
    stage.rmdir()
    _fsync(incoming)


def _link(source: Path, destination: Path, expected: bytes) -> None:
    try:
        destination.lstat()
    except FileNotFoundError:
        os.link(source, destination, follow_symlinks=False)
        _fsync(destination.parent)
    else:
        _read_exact(destination, expected)


def publish_benchmark_result(
    root: Path, result: VS01BenchmarkRunResult, receipt: VS01BenchmarkExecutionReceipt
) -> None:
    result_bytes = canonical_run_result_bytes(result)
    result_sha = hashlib.sha256(result_bytes).hexdigest()
    if verify_existing(root, result, result_bytes) is not None:
        raise ValueError("benchmark publication already exists")
    _clean_exact_stage(root, result, result_bytes, receipt)
    stage = _safe_directory(root, ".incoming", benchmark_stage_path(root, result_sha).name)
    payloads = {"object": result_bytes, "snapshot": result_bytes, "receipt": _receipt_bytes(receipt)}
    for name, data in payloads.items():
        _write_immutable(stage / name, data)
    destinations = tuple(root / value for value in publication_paths(result_sha))
    for name, destination in zip(payloads, destinations, strict=True):
        _safe_directory(root, *destination.relative_to(root).parent.parts)
        _link(stage / name, destination, payloads[name])
    if verify_existing(root, result, result_bytes) is None:
        raise ValueError("benchmark publication verification failed")
    _clean_exact_stage(root, result, result_bytes, receipt)
