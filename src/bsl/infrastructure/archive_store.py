from __future__ import annotations

import hashlib
import os
import stat
from datetime import UTC, datetime
from pathlib import Path

from uuid6 import uuid7

from bsl.contracts.archive import ArchiveObjectPromotionReceipt

FIXTURE_MARKER = ".bsl-non-authoritative-fixture"
FIXTURE_MARKER_BYTES = b"BSL_NON_AUTHORITATIVE_FIXTURE_V1\n"


def _require_fixture_root(root: Path) -> Path:
    if root.is_symlink() or not root.is_dir():
        raise ValueError("fixture root must be a real directory, not a symlink")
    resolved = root.resolve(strict=True)
    marker = resolved / FIXTURE_MARKER
    if marker.is_symlink() or not marker.is_file() or marker.read_bytes() != FIXTURE_MARKER_BYTES:
        raise ValueError("archive root lacks the exact non-authoritative fixture marker")
    return resolved


def _directory(root: Path, *parts: str) -> Path:
    current = root
    for part in parts:
        if part in {"", ".", ".."} or "/" in part:
            raise ValueError("unsafe archive path component")
        current = current / part
        current.mkdir(exist_ok=True)
        mode = current.lstat().st_mode
        if not stat.S_ISDIR(mode) or stat.S_ISLNK(mode):
            raise ValueError("archive path contains a symlink or non-directory")
    return current


def _hash_file(path: Path) -> tuple[str, int]:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        with os.fdopen(fd, "rb", closefd=False) as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
            size = os.fstat(fd).st_size
    finally:
        os.close(fd)
    return digest, size


def _fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def promote_synthetic(root: Path, data: bytes, *, expected_sha256: str | None = None) -> ArchiveObjectPromotionReceipt:
    root = _require_fixture_root(root)
    incoming = _directory(root, ".incoming")
    stage = incoming / f"{uuid7()}.stage"
    fd = os.open(stage, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        with os.fdopen(fd, "wb", closefd=False) as stream:
            stream.write(data)
            stream.flush()
            os.fsync(fd)
        os.fchmod(fd, 0o444)
    finally:
        os.close(fd)
    try:
        actual_hash, byte_count = _hash_file(stage)
        if expected_sha256 is not None and actual_hash != expected_sha256:
            raise ValueError("staged object hash does not match expected SHA-256")
        object_dir = _directory(root, "objects", "sha256", actual_hash[:2])
        destination = object_dir / actual_hash
        try:
            os.link(stage, destination, follow_symlinks=False)
            disposition = "PUBLISHED"
            _fsync_directory(object_dir)
        except FileExistsError:
            existing_hash, existing_size = _hash_file(destination)
            if (existing_hash, existing_size) != (actual_hash, byte_count):
                raise ValueError("existing content-addressed object is corrupt") from None
            disposition = "DEDUPLICATED"
        verified_hash, verified_size = _hash_file(destination)
        if (verified_hash, verified_size) != (actual_hash, byte_count):
            raise ValueError("published object verification failed")
        return ArchiveObjectPromotionReceipt(
            receipt_id=uuid7(),
            generated_at=datetime.now(UTC),
            object_sha256=actual_hash,
            byte_count=byte_count,
            disposition=disposition,
            object_relative_path=f"objects/sha256/{actual_hash[:2]}/{actual_hash}",
        )
    finally:
        stage.unlink(missing_ok=True)
