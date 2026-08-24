from __future__ import annotations

import hashlib
import os
import stat
from pathlib import Path

import rfc8785
from pydantic import ValidationError

from bsl.contracts.page_fixture import (
    John15SyntheticPageFixture,
    John15SyntheticPagePublicationReceipt,
    publication_paths,
)


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
        raise ValueError(f"publication directory is unsafe: {path.name}")
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
        raise ValueError(f"fixture publication is missing or unsafe: {path.name}") from None
    if not stat.S_ISREG(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) != 0o444 or actual != expected:
        raise ValueError(f"fixture publication differs or is mutable: {path.name}")


def _write_immutable(path: Path, data: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o444)
    try:
        os.write(descriptor, data)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.chmod(path, 0o444, follow_symlinks=False)
    _read_exact(path, data)
    _fsync(path.parent)


def _payloads(
    base: bytes,
    degraded: bytes,
    fixture_bytes: bytes,
    receipt: John15SyntheticPagePublicationReceipt | None = None,
) -> dict[str, bytes]:
    values = {"base": base, "degraded": degraded, "fixture": fixture_bytes, "snapshot": fixture_bytes}
    if receipt is not None:
        values["receipt"] = rfc8785.dumps(receipt.model_dump(mode="json"))
    return values


def _destinations(root: Path, fixture_sha: str) -> dict[str, Path]:
    paths = publication_paths(fixture_sha)
    return dict(
        zip(("base", "degraded", "fixture", "snapshot", "receipt"), (root / item for item in paths), strict=True)
    )


def page_stage_path(root: Path, fixture_sha: str) -> Path:
    return root / ".incoming" / f"john-1-5-synthetic-fixture-{fixture_sha}.page-stage"


def _receipt_valid(
    path: Path,
    fixture: John15SyntheticPageFixture,
    fixture_sha: str,
    publication_root: Path | None = None,
) -> John15SyntheticPagePublicationReceipt:
    try:
        receipt = John15SyntheticPagePublicationReceipt.model_validate_json(path.read_bytes())
    except (OSError, ValidationError):
        raise ValueError("existing page fixture receipt is invalid") from None
    expected = (
        receipt.disposition == "PUBLISHED",
        receipt.published is True,
        receipt.verified_existing is False,
        receipt.fixture_identity == fixture.fixture_identity,
        receipt.fixture_json_sha256 == fixture_sha,
        receipt.archive_root == str(publication_root or path.parents[3]),
    )
    if not all(expected):
        raise ValueError("existing page fixture receipt authority differs")
    _read_exact(path, rfc8785.dumps(receipt.model_dump(mode="json")))
    return receipt


def verify_existing(
    root: Path,
    fixture: John15SyntheticPageFixture,
    base: bytes,
    degraded: bytes,
    fixture_bytes: bytes,
) -> John15SyntheticPagePublicationReceipt | None:
    fixture_sha = hashlib.sha256(fixture_bytes).hexdigest()
    destinations = _destinations(root, fixture_sha)
    expected = _payloads(base, degraded, fixture_bytes)
    for name, data in expected.items():
        path = destinations[name]
        if path.exists() or path.is_symlink():
            _read_exact(path, data)
    receipt_path = destinations["receipt"]
    if receipt_path.exists() or receipt_path.is_symlink():
        if not all(destinations[name].exists() for name in expected):
            raise ValueError("page fixture receipt exists without all prerequisites")
        return _receipt_valid(receipt_path, fixture, fixture_sha)
    return None


def _clean_exact_stage(
    root: Path,
    fixture_sha: str,
    payloads: dict[str, bytes],
    fixture: John15SyntheticPageFixture,
) -> None:
    stage = page_stage_path(root, fixture_sha)
    if stage.is_symlink() or (stage.exists() and not stage.is_dir()):
        raise ValueError("fixture-bound page stage is unsafe")
    if not stage.exists():
        return
    contents = {item.name: item for item in stage.iterdir()}
    if set(contents) - set(payloads):
        raise ValueError("fixture-bound page stage contains unexpected content")
    for name, path in contents.items():
        if name == "receipt":
            _receipt_valid(path, fixture, fixture_sha, root)
        else:
            _read_exact(path, payloads[name])
    for name in payloads:
        (stage / name).unlink(missing_ok=True)
    stage.rmdir()
    _fsync(stage.parent)


def prepare_publication(
    root: Path,
    fixture: John15SyntheticPageFixture,
    base: bytes,
    degraded: bytes,
    fixture_bytes: bytes,
    receipt: John15SyntheticPagePublicationReceipt,
) -> John15SyntheticPagePublicationReceipt | None:
    existing = verify_existing(root, fixture, base, degraded, fixture_bytes)
    _clean_exact_stage(
        root,
        hashlib.sha256(fixture_bytes).hexdigest(),
        _payloads(base, degraded, fixture_bytes, receipt),
        fixture,
    )
    return existing


def _link(source: Path, destination: Path, expected: bytes) -> None:
    try:
        os.link(source, destination, follow_symlinks=False)
        _fsync(destination.parent)
    except FileExistsError:
        _read_exact(destination, expected)


def publish_fixture(
    root: Path,
    fixture: John15SyntheticPageFixture,
    base: bytes,
    degraded: bytes,
    fixture_bytes: bytes,
    receipt: John15SyntheticPagePublicationReceipt,
) -> None:
    fixture_sha = hashlib.sha256(fixture_bytes).hexdigest()
    payloads = _payloads(base, degraded, fixture_bytes, receipt)
    if prepare_publication(root, fixture, base, degraded, fixture_bytes, receipt) is not None:
        raise ValueError("page fixture publication already exists")
    stage = _directory(root, ".incoming", page_stage_path(root, fixture_sha).name)
    for name, data in payloads.items():
        _write_immutable(stage / name, data)
    destinations = _destinations(root, fixture_sha)
    for name in ("base", "degraded", "fixture", "snapshot", "receipt"):
        _directory(root, *destinations[name].relative_to(root).parent.parts)
        _link(stage / name, destinations[name], payloads[name])
    if verify_existing(root, fixture, base, degraded, fixture_bytes) is None:
        raise ValueError("page fixture publication verification failed")
    _clean_exact_stage(root, fixture_sha, payloads, fixture)
