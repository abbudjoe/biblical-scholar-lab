from __future__ import annotations

import hashlib
import os
from contextlib import suppress
from pathlib import Path
from uuid import UUID

import rfc8785
from pydantic import ValidationError

from bsl.contracts.normalization import John15NormalizationBundle, NormalizationReceipt
from bsl.infrastructure.archive_store import (
    _directory,  # pyright: ignore[reportPrivateUsage]
    _fsync_directory,  # pyright: ignore[reportPrivateUsage]
    _hash_file,  # pyright: ignore[reportPrivateUsage]
    _write_immutable,  # pyright: ignore[reportPrivateUsage]
)

SNAPSHOT_PATH = "snapshots/normalization/john-1-5.json"
RECEIPT_PATH = "manifests/normalization/john-1-5/normalization-receipt.json"


def canonical_bundle_bytes(bundle: John15NormalizationBundle) -> bytes:
    return rfc8785.dumps(bundle.model_dump(mode="json"))


def publication_paths(bundle_sha256: str) -> tuple[str, str, str]:
    return (f"objects/sha256/{bundle_sha256[:2]}/{bundle_sha256}", SNAPSHOT_PATH, RECEIPT_PATH)


def _regular_bytes(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        with os.fdopen(fd, "rb", closefd=False) as stream:
            return stream.read()
    finally:
        os.close(fd)


def _exact_file(path: Path, expected: bytes) -> None:
    digest, size = _hash_file(path, require_read_only=True)
    if (digest, size, _regular_bytes(path)) != (hashlib.sha256(expected).hexdigest(), len(expected), expected):
        raise ValueError(f"existing normalization publication differs or is corrupt: {path.name}")


def verify_existing(root: Path, bundle: John15NormalizationBundle, bundle_bytes: bytes) -> NormalizationReceipt | None:
    bundle_sha256 = hashlib.sha256(bundle_bytes).hexdigest()
    relative_paths = publication_paths(bundle_sha256)
    object_path, snapshot_path, receipt_path = tuple(root / value for value in relative_paths)
    states = (object_path.exists(), snapshot_path.exists(), receipt_path.exists())
    if not any(states):
        return None
    if states[1:] != (True, True):
        if states == (True, False, False):
            _exact_file(object_path, bundle_bytes)
            return None
        raise ValueError("existing normalization publication is partial")
    if not states[0]:
        raise ValueError("existing normalization publication lacks its content object")
    _exact_file(object_path, bundle_bytes)
    _exact_file(snapshot_path, bundle_bytes)
    try:
        receipt = NormalizationReceipt.model_validate_json(_regular_bytes(receipt_path))
        _hash_file(receipt_path, require_read_only=True)
    except (OSError, ValidationError, ValueError):
        raise ValueError("existing normalization receipt is invalid") from None
    expected = (
        receipt.disposition == "PUBLISHED",
        receipt.bundle_identity == bundle.bundle_identity,
        receipt.bundle_canonical_sha256 == bundle_sha256,
        receipt.publication_paths == relative_paths,
        receipt.source_snapshot_identities == tuple(source.snapshot_identity for source in bundle.sources),
        receipt.source_content_identities == tuple(source.content_identity for source in bundle.sources),
    )
    if not all(expected):
        raise ValueError("existing normalization receipt does not bind the exact bundle publication")
    return receipt


def _created_directory(root: Path, created: list[Path], *parts: str) -> Path:
    path = root
    for index, part in enumerate(parts):
        candidate = path / part
        existed = candidate.exists()
        path = _directory(root, *parts[: index + 1])
        if not existed:
            created.append(path)
    return path


def publish_normalization(
    root: Path,
    bundle: John15NormalizationBundle,
    receipt: NormalizationReceipt,
    stage_id: UUID,
) -> None:
    bundle_bytes = canonical_bundle_bytes(bundle)
    bundle_sha256 = hashlib.sha256(bundle_bytes).hexdigest()
    if verify_existing(root, bundle, bundle_bytes) is not None:
        raise ValueError("normalization publication already exists")
    receipt_bytes = rfc8785.dumps(receipt.model_dump(mode="json"))
    incoming = root / ".incoming"
    stage = _directory(root, ".incoming", f"{stage_id}.normalization-stage")
    staged = (stage / "object", stage / "snapshot", stage / "receipt")
    payloads = (bundle_bytes, bundle_bytes, receipt_bytes)
    linked: list[Path] = []
    created_dirs: list[Path] = [stage]
    try:
        for path, data in zip(staged, payloads, strict=True):
            _write_immutable(path, data, expected_sha256=hashlib.sha256(data).hexdigest())
        destinations = (
            _created_directory(root, created_dirs, "objects", "sha256", bundle_sha256[:2]) / bundle_sha256,
            _created_directory(root, created_dirs, "snapshots", "normalization") / "john-1-5.json",
            _created_directory(root, created_dirs, "manifests", "normalization", "john-1-5")
            / "normalization-receipt.json",
        )
        for source, destination in zip(staged, destinations, strict=True):
            try:
                os.link(source, destination, follow_symlinks=False)
                linked.append(destination)
                _fsync_directory(destination.parent)
            except FileExistsError:
                _exact_file(destination, _regular_bytes(source))
        if verify_existing(root, bundle, bundle_bytes) is None:
            raise ValueError("normalization publication verification failed")
    except BaseException:
        for path in reversed(linked):
            path.unlink(missing_ok=True)
            _fsync_directory(path.parent)
        for path in reversed(created_dirs[1:]):
            with suppress(OSError):
                path.rmdir()
        raise
    finally:
        for path in staged:
            path.unlink(missing_ok=True)
        with suppress(OSError):
            stage.rmdir()
        _fsync_directory(incoming)
