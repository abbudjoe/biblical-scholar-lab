from __future__ import annotations

import hashlib
import os
from pathlib import Path

import rfc8785
from pydantic import ValidationError

from bsl.contracts.evidence import (
    John15TranslationNuanceEvidencePacket,
    John15TranslationNuanceEvidenceReceipt,
)
from bsl.infrastructure.archive_store import (
    _directory,  # pyright: ignore[reportPrivateUsage]
    _fsync_directory,  # pyright: ignore[reportPrivateUsage]
    _hash_file,  # pyright: ignore[reportPrivateUsage]
    _write_immutable,  # pyright: ignore[reportPrivateUsage]
)

SNAPSHOT_PATH = "snapshots/evidence/john-1-5-translation-nuance.json"
RECEIPT_PATH = "manifests/evidence/john-1-5-translation-nuance/evidence-packet-receipt.json"


def canonical_packet_bytes(packet: John15TranslationNuanceEvidencePacket) -> bytes:
    return rfc8785.dumps(packet.model_dump(mode="json"))


def publication_paths(packet_sha256: str) -> tuple[str, str, str]:
    return (f"objects/sha256/{packet_sha256[:2]}/{packet_sha256}", SNAPSHOT_PATH, RECEIPT_PATH)


def evidence_stage_path(root: Path, packet_sha256: str) -> Path:
    return root / ".incoming" / f"john-1-5-translation-nuance-{packet_sha256}.evidence-stage"


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
        raise ValueError(f"existing evidence publication differs or is corrupt: {path.name}")


def _validated_receipt(
    path: Path,
    root: Path,
    packet: John15TranslationNuanceEvidencePacket,
    packet_sha256: str,
) -> John15TranslationNuanceEvidenceReceipt:
    try:
        receipt = John15TranslationNuanceEvidenceReceipt.model_validate_json(_regular_bytes(path))
        _hash_file(path, require_read_only=True)
    except (OSError, ValidationError, ValueError):
        raise ValueError("existing evidence receipt is invalid") from None
    authority = packet.input_authority
    expected = (
        receipt.disposition == "PUBLISHED",
        receipt.archive_root == str(root),
        receipt.packet_identity == packet.packet_identity,
        receipt.packet_canonical_sha256 == packet_sha256,
        receipt.input_bundle_identity == authority.bundle_identity,
        receipt.input_bundle_canonical_sha256 == authority.bundle_canonical_sha256,
        receipt.input_normalization_receipt_identity == authority.normalization_receipt_identity,
        receipt.input_normalization_receipt_file_sha256 == authority.normalization_receipt_file_sha256,
    )
    if not all(expected):
        raise ValueError("existing evidence receipt does not bind the exact packet publication")
    return receipt


def verify_existing(
    root: Path, packet: John15TranslationNuanceEvidencePacket, packet_bytes: bytes
) -> John15TranslationNuanceEvidenceReceipt | None:
    packet_sha = hashlib.sha256(packet_bytes).hexdigest()
    object_path, snapshot_path, receipt_path = tuple(root / value for value in publication_paths(packet_sha))
    states = (object_path.exists(), snapshot_path.exists(), receipt_path.exists())
    if not any(states):
        return None
    if states[2] and not states[1]:
        raise ValueError("evidence receipt exists without its snapshot")
    if states[2] and not states[0]:
        raise ValueError("evidence receipt exists without its content object")
    if states[1] and not states[0]:
        raise ValueError("evidence snapshot exists without its content object")
    _exact_file(object_path, packet_bytes)
    if states[1]:
        _exact_file(snapshot_path, packet_bytes)
    return _validated_receipt(receipt_path, root, packet, packet_sha) if states[2] else None


def _stage_receipt(path: Path, root: Path, packet: John15TranslationNuanceEvidencePacket, packet_sha: str) -> None:
    _validated_receipt(path, root, packet, packet_sha)


def _validate_stage(root: Path, packet: John15TranslationNuanceEvidencePacket, packet_bytes: bytes) -> Path | None:
    packet_sha = hashlib.sha256(packet_bytes).hexdigest()
    stage = evidence_stage_path(root, packet_sha)
    if stage.is_symlink() or (stage.exists() and not stage.is_dir()):
        raise ValueError("packet-bound evidence stage is not a real directory")
    if not stage.exists():
        return None
    contents = {path.name: path for path in stage.iterdir()}
    if set(contents) - {"object", "snapshot", "receipt"}:
        raise ValueError("packet-bound evidence stage contains unexpected content")
    for name in ("object", "snapshot"):
        if name in contents:
            _exact_file(contents[name], packet_bytes)
    if "receipt" in contents:
        _stage_receipt(contents["receipt"], root, packet, packet_sha)
    return stage


def _clean_stage(root: Path, packet: John15TranslationNuanceEvidencePacket, packet_bytes: bytes) -> None:
    stage = _validate_stage(root, packet, packet_bytes)
    if stage is None:
        return
    for name in ("object", "snapshot", "receipt"):
        (stage / name).unlink(missing_ok=True)
    stage.rmdir()
    _fsync_directory(stage.parent)


def prepare_publication(
    root: Path, packet: John15TranslationNuanceEvidencePacket, packet_bytes: bytes
) -> John15TranslationNuanceEvidenceReceipt | None:
    existing = verify_existing(root, packet, packet_bytes)
    _clean_stage(root, packet, packet_bytes)
    return existing


def _link_no_overwrite(source: Path, destination: Path) -> None:
    try:
        os.link(source, destination, follow_symlinks=False)
        _fsync_directory(destination.parent)
    except FileExistsError:
        _exact_file(destination, _regular_bytes(source))


def publish_evidence(
    root: Path,
    packet: John15TranslationNuanceEvidencePacket,
    receipt: John15TranslationNuanceEvidenceReceipt,
) -> None:
    packet_bytes = canonical_packet_bytes(packet)
    packet_sha = hashlib.sha256(packet_bytes).hexdigest()
    if prepare_publication(root, packet, packet_bytes) is not None:
        raise ValueError("evidence publication already exists")
    payloads = {
        "object": packet_bytes,
        "snapshot": packet_bytes,
        "receipt": rfc8785.dumps(receipt.model_dump(mode="json")),
    }
    stage = _directory(root, ".incoming", evidence_stage_path(root, packet_sha).name)
    for name, data in payloads.items():
        _write_immutable(stage / name, data, expected_sha256=hashlib.sha256(data).hexdigest())
    destinations = (
        _directory(root, "objects", "sha256", packet_sha[:2]) / packet_sha,
        _directory(root, "snapshots", "evidence") / "john-1-5-translation-nuance.json",
        _directory(root, "manifests", "evidence", "john-1-5-translation-nuance") / "evidence-packet-receipt.json",
    )
    for name, destination in zip(("object", "snapshot", "receipt"), destinations, strict=True):
        _link_no_overwrite(stage / name, destination)
    if verify_existing(root, packet, packet_bytes) is None:
        raise ValueError("evidence publication verification failed")
    _clean_stage(root, packet, packet_bytes)
