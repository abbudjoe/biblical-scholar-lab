from __future__ import annotations

import hashlib
import os
from pathlib import Path

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


def normalization_stage_path(root: Path, bundle_sha256: str) -> Path:
    return root / ".incoming" / f"john-1-5-{bundle_sha256}.normalization-stage"


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


def _validated_receipt(
    path: Path,
    root: Path,
    bundle: John15NormalizationBundle,
    bundle_sha256: str,
) -> NormalizationReceipt:
    try:
        receipt = NormalizationReceipt.model_validate_json(_regular_bytes(path))
        _hash_file(path, require_read_only=True)
    except (OSError, ValidationError, ValueError):
        raise ValueError("existing normalization receipt is invalid") from None
    expected = (
        receipt.disposition == "PUBLISHED",
        receipt.archive_root == str(root),
        receipt.bundle_identity == bundle.bundle_identity,
        receipt.bundle_canonical_sha256 == bundle_sha256,
        receipt.source_snapshot_identities == tuple(source.snapshot_identity for source in bundle.sources),
        receipt.source_content_identities == tuple(source.content_identity for source in bundle.sources),
    )
    if not all(expected):
        raise ValueError("existing normalization receipt does not bind the exact bundle publication")
    return receipt


def verify_existing(root: Path, bundle: John15NormalizationBundle, bundle_bytes: bytes) -> NormalizationReceipt | None:
    bundle_sha256 = hashlib.sha256(bundle_bytes).hexdigest()
    relative_paths = publication_paths(bundle_sha256)
    object_path, snapshot_path, receipt_path = tuple(root / value for value in relative_paths)
    states = (object_path.exists(), snapshot_path.exists(), receipt_path.exists())
    if not any(states):
        return None
    if states[2] and not states[1]:
        raise ValueError("normalization receipt exists without its snapshot")
    if states[2] and not states[0]:
        raise ValueError("normalization receipt exists without its content object")
    if states[1] and not states[0]:
        raise ValueError("normalization snapshot exists without its content object")
    _exact_file(object_path, bundle_bytes)
    if states[1]:
        _exact_file(snapshot_path, bundle_bytes)
    return _validated_receipt(receipt_path, root, bundle, bundle_sha256) if states[2] else None


def _stage_payloads(bundle: John15NormalizationBundle, receipt: NormalizationReceipt) -> dict[str, bytes]:
    bundle_bytes = canonical_bundle_bytes(bundle)
    return {
        "object": bundle_bytes,
        "snapshot": bundle_bytes,
        "receipt": rfc8785.dumps(receipt.model_dump(mode="json")),
    }


def _validate_stage(root: Path, bundle: John15NormalizationBundle, bundle_bytes: bytes) -> Path | None:
    bundle_sha256 = hashlib.sha256(bundle_bytes).hexdigest()
    stage = normalization_stage_path(root, bundle_sha256)
    if stage.is_symlink() or (stage.exists() and not stage.is_dir()):
        raise ValueError("bundle-bound normalization stage is not a real directory")
    if not stage.exists():
        return None
    contents = {path.name: path for path in stage.iterdir()}
    if set(contents) - {"object", "snapshot", "receipt"}:
        raise ValueError("bundle-bound normalization stage contains unexpected evidence")
    for name in ("object", "snapshot"):
        if name in contents:
            _exact_file(contents[name], bundle_bytes)
    if "receipt" in contents:
        _validated_receipt(contents["receipt"], root, bundle, bundle_sha256)
    return stage


def clean_normalization_stage(root: Path, bundle: John15NormalizationBundle, bundle_bytes: bytes) -> None:
    stage = _validate_stage(root, bundle, bundle_bytes)
    if stage is None:
        return
    for name in ("object", "snapshot", "receipt"):
        (stage / name).unlink(missing_ok=True)
    stage.rmdir()
    _fsync_directory(stage.parent)


def prepare_publication(
    root: Path, bundle: John15NormalizationBundle, bundle_bytes: bytes
) -> NormalizationReceipt | None:
    existing = verify_existing(root, bundle, bundle_bytes)
    clean_normalization_stage(root, bundle, bundle_bytes)
    return existing


def _link_no_overwrite(source: Path, destination: Path) -> None:
    try:
        os.link(source, destination, follow_symlinks=False)
        _fsync_directory(destination.parent)
    except FileExistsError:
        _exact_file(destination, _regular_bytes(source))


def publish_normalization(
    root: Path,
    bundle: John15NormalizationBundle,
    receipt: NormalizationReceipt,
) -> None:
    bundle_bytes = canonical_bundle_bytes(bundle)
    bundle_sha256 = hashlib.sha256(bundle_bytes).hexdigest()
    if prepare_publication(root, bundle, bundle_bytes) is not None:
        raise ValueError("normalization publication already exists")
    payloads = _stage_payloads(bundle, receipt)
    stage = _directory(root, ".incoming", normalization_stage_path(root, bundle_sha256).name)
    for name, data in payloads.items():
        _write_immutable(stage / name, data, expected_sha256=hashlib.sha256(data).hexdigest())
    destinations = (
        _directory(root, "objects", "sha256", bundle_sha256[:2]) / bundle_sha256,
        _directory(root, "snapshots", "normalization") / "john-1-5.json",
        _directory(root, "manifests", "normalization", "john-1-5") / "normalization-receipt.json",
    )
    for name, destination in zip(("object", "snapshot", "receipt"), destinations, strict=True):
        _link_no_overwrite(stage / name, destination)
    if verify_existing(root, bundle, bundle_bytes) is None:
        raise ValueError("normalization publication verification failed")
    clean_normalization_stage(root, bundle, bundle_bytes)
