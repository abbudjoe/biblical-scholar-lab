from __future__ import annotations

import hashlib
import os
import stat
from pathlib import Path

import rfc8785
from pydantic import ValidationError

from bsl.contracts.benchmark import VS01BenchmarkExecutionReceipt, VS01BenchmarkRunResult

SNAPSHOT_PATH = "snapshots/benchmark/vs01-batch-01/reference-conformance.json"
RECEIPT_PATH = "manifests/benchmark/vs01-batch-01/reference-conformance/benchmark-execution-receipt.json"


def canonical_run_result_bytes(result: VS01BenchmarkRunResult) -> bytes:
    return rfc8785.dumps(result.model_dump(mode="json"))


def publication_paths(result_sha256: str) -> tuple[str, str, str]:
    return f"objects/sha256/{result_sha256[:2]}/{result_sha256}", SNAPSHOT_PATH, RECEIPT_PATH


def benchmark_stage_path(root: Path, result_sha256: str) -> Path:
    return root / ".incoming" / f"vs01-batch-01-{result_sha256}.benchmark-stage"


def _fsync(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _directory(root: Path, *parts: str) -> Path:
    path = root.joinpath(*parts)
    path.mkdir(parents=True, exist_ok=True)
    if path.is_symlink() or not path.is_dir():
        raise ValueError(f"benchmark publication directory is unsafe: {path.name}")
    return path


def _read_exact(path: Path, expected: bytes) -> None:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        metadata = os.fstat(descriptor)
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            actual = stream.read()
        os.close(descriptor)
    except OSError:
        raise ValueError(f"benchmark publication is missing or unsafe: {path.name}") from None
    if not stat.S_ISREG(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) != 0o444 or actual != expected:
        raise ValueError(f"benchmark publication differs or is mutable: {path.name}")


def _write_immutable(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o444)
    try:
        os.write(descriptor, data)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.chmod(path, 0o444, follow_symlinks=False)
    _read_exact(path, data)
    _fsync(path.parent)


def _receipt_bytes(receipt: VS01BenchmarkExecutionReceipt) -> bytes:
    return rfc8785.dumps(receipt.model_dump(mode="json"))


def _validated_receipt(
    path: Path, root: Path, result: VS01BenchmarkRunResult, result_bytes: bytes
) -> VS01BenchmarkExecutionReceipt:
    try:
        receipt = VS01BenchmarkExecutionReceipt.model_validate_json(path.read_bytes())
    except (OSError, ValidationError):
        raise ValueError("existing benchmark receipt is invalid") from None
    result_sha = hashlib.sha256(result_bytes).hexdigest()
    expected = (
        receipt.disposition == "REFERENCE_CONFORMANT",
        receipt.published is True,
        receipt.verified_existing is False,
        receipt.dry_run is False,
        receipt.archive_root == str(root),
        receipt.run_result_identity == result.run_result_identity,
        receipt.run_result_file_sha256 == result_sha,
        receipt.archive_paths == publication_paths(result_sha),
        receipt.archive_writes == 3,
    )
    if not all(expected):
        raise ValueError("existing benchmark receipt authority differs")
    _read_exact(path, _receipt_bytes(receipt))
    return receipt


def verify_existing(
    root: Path, result: VS01BenchmarkRunResult, result_bytes: bytes
) -> VS01BenchmarkExecutionReceipt | None:
    result_sha = hashlib.sha256(result_bytes).hexdigest()
    object_path, snapshot_path, receipt_path = (root / value for value in publication_paths(result_sha))
    states = object_path.exists(), snapshot_path.exists(), receipt_path.exists()
    if not any(states):
        return None
    if states[2] and not all(states[:2]):
        raise ValueError("benchmark receipt exists without every prerequisite")
    if states[1] and not states[0]:
        raise ValueError("benchmark snapshot exists without its content object")
    _read_exact(object_path, result_bytes)
    if states[1]:
        _read_exact(snapshot_path, result_bytes)
    return _validated_receipt(receipt_path, root, result, result_bytes) if states[2] else None


def _clean_exact_stage(
    root: Path,
    result: VS01BenchmarkRunResult,
    result_bytes: bytes,
    receipt: VS01BenchmarkExecutionReceipt,
) -> None:
    result_sha = hashlib.sha256(result_bytes).hexdigest()
    stage = benchmark_stage_path(root, result_sha)
    if stage.is_symlink() or (stage.exists() and not stage.is_dir()):
        raise ValueError("result-bound benchmark stage is unsafe")
    if not stage.exists():
        return
    payloads = {"object": result_bytes, "snapshot": result_bytes, "receipt": _receipt_bytes(receipt)}
    contents = {path.name: path for path in stage.iterdir()}
    if set(contents) - set(payloads):
        raise ValueError("result-bound benchmark stage contains unexpected content")
    for name, path in contents.items():
        if name == "receipt":
            _validated_receipt(path, root, result, result_bytes)
        else:
            _read_exact(path, payloads[name])
    for name in payloads:
        (stage / name).unlink(missing_ok=True)
    stage.rmdir()
    _fsync(stage.parent)


def prepare_publication(
    root: Path,
    result: VS01BenchmarkRunResult,
    result_bytes: bytes,
    receipt: VS01BenchmarkExecutionReceipt,
) -> VS01BenchmarkExecutionReceipt | None:
    existing = verify_existing(root, result, result_bytes)
    _clean_exact_stage(root, result, result_bytes, receipt)
    return existing


def _link(source: Path, destination: Path, expected: bytes) -> None:
    try:
        os.link(source, destination, follow_symlinks=False)
        _fsync(destination.parent)
    except FileExistsError:
        _read_exact(destination, expected)


def publish_benchmark_result(
    root: Path, result: VS01BenchmarkRunResult, receipt: VS01BenchmarkExecutionReceipt
) -> None:
    result_bytes = canonical_run_result_bytes(result)
    result_sha = hashlib.sha256(result_bytes).hexdigest()
    if prepare_publication(root, result, result_bytes, receipt) is not None:
        raise ValueError("benchmark publication already exists")
    payloads = {"object": result_bytes, "snapshot": result_bytes, "receipt": _receipt_bytes(receipt)}
    stage = _directory(root, ".incoming", benchmark_stage_path(root, result_sha).name)
    for name, data in payloads.items():
        _write_immutable(stage / name, data)
    destinations = tuple(root / value for value in publication_paths(result_sha))
    for name, destination in zip(("object", "snapshot", "receipt"), destinations, strict=True):
        _directory(root, *destination.relative_to(root).parent.parts)
        _link(stage / name, destination, payloads[name])
    if verify_existing(root, result, result_bytes) is None:
        raise ValueError("benchmark publication verification failed")
    _clean_exact_stage(root, result, result_bytes, receipt)
