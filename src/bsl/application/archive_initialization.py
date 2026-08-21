from __future__ import annotations

import hashlib
import json
import os
import plistlib
import shutil
import stat
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import cast
from uuid import UUID

from pydantic import ValidationError
from uuid6 import uuid7

from bsl.contracts.archive import (
    APPROVED_PROFILE_SHA256,
    CANARY_RELATIVE_PATH,
    CANARY_SHA256,
    MINIMUM_FREE_BYTES,
    ApprovedArchiveProfile,
    ArchiveCandidate,
    ArchiveInitializationReceipt,
    ArchivePreflightReceipt,
    ArchiveReadiness,
    ArchiveRootMarker,
    StablePhysicalDeviceIdKind,
)
from bsl.infrastructure.archive_store import (
    _atomic_rename_absent,  # pyright: ignore[reportPrivateUsage]
    _directory,  # pyright: ignore[reportPrivateUsage]
    _fsync_directory,  # pyright: ignore[reportPrivateUsage]
    _hash_file,  # pyright: ignore[reportPrivateUsage]
    _write_immutable,  # pyright: ignore[reportPrivateUsage]
)
from bsl.infrastructure.macos_volume import inspect_volume

CANARY_BYTES = b"BSL_ARCHIVE_INITIALIZATION_CANARY_V1\n"
MARKER_PATH = ".bsl-archive-root.json"
TOP_LEVEL = frozenset(
    {MARKER_PATH, "registry", "objects", "manifests", "snapshots", "quarantine", "incidents", ".incoming"}
)
LAYOUT_DIRECTORIES = (
    ("registry", "archive-initialization"),
    ("objects", "sha256", "fa"),
    ("manifests", "archive"),
    ("manifests", "source"),
    ("snapshots", "source"),
    ("quarantine",),
    ("incidents",),
    (".incoming",),
)


def _current_apfs_plist() -> bytes:
    try:
        result = subprocess.run(("diskutil", "apfs", "list", "-plist"), check=False, capture_output=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        raise ValueError("current APFS inspection failed") from None
    if result.returncode != 0:
        raise ValueError("current APFS inspection failed")
    return result.stdout


def _evidence_digest(_path: Path, data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _nothing(_path: Path) -> None:
    return None


@dataclass(frozen=True)
class _Services:
    inspect: Callable[[str], ArchivePreflightReceipt] = inspect_volume
    current_apfs: Callable[[], bytes] = _current_apfs_plist
    evidence_digest: Callable[[Path, bytes], str] = _evidence_digest
    new_uuid: Callable[[], UUID] = uuid7
    now: Callable[[], datetime] = lambda: datetime.now(UTC)
    is_mount: Callable[[Path], bool] = os.path.ismount
    sandbox_root: Path | None = None
    before_publish: Callable[[Path], None] = _nothing


def _read_regular(path: Path, label: str) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise ValueError
            with os.fdopen(fd, "rb", closefd=False) as stream:
                return stream.read()
        finally:
            os.close(fd)
    except (OSError, ValueError):
        raise ValueError(f"{label} cannot be read as a regular file") from None


def _load_profile(path: Path) -> tuple[ApprovedArchiveProfile, str]:
    data = _read_regular(path, "public profile")
    digest = hashlib.sha256(data).hexdigest()
    if digest != APPROVED_PROFILE_SHA256:
        raise ValueError("public profile hash differs from the approved profile")
    try:
        return ApprovedArchiveProfile.model_validate_json(data), digest
    except ValidationError:
        raise ValueError("public profile is not semantically valid") from None


def _load_private_receipt(data: bytes) -> ArchivePreflightReceipt:
    try:
        return ArchivePreflightReceipt.model_validate_json(data)
    except ValidationError:
        raise ValueError("approved private receipt is not semantically valid") from None


def _ready_candidate(receipt: ArchivePreflightReceipt, volume_name: str, label: str) -> ArchiveCandidate:
    if (
        receipt.requested_volume_name != volume_name
        or receipt.readiness is not ArchiveReadiness.CANDIDATE_READY_FOR_OWNER_APPROVAL
        or receipt.candidate_count != 1
        or receipt.candidate is None
    ):
        raise ValueError(f"{label} does not contain one ready archive candidate")
    return receipt.candidate


def _require_candidate_agreement(approved: ArchiveCandidate, live: ArchiveCandidate) -> None:
    approved_facts = (
        approved.filesystem and approved.filesystem.lower(),
        approved.encrypted,
        approved.internal,
        approved.mounted,
        approved.read_only,
        approved.volume_uuid,
        approved.live_parent_device,
        approved.stable_physical_device_id,
        approved.stable_physical_device_id_kind,
        approved.thunderbolt_evidenced,
    )
    live_facts = (
        live.filesystem and live.filesystem.lower(),
        live.encrypted,
        live.internal,
        live.mounted,
        live.read_only,
        live.volume_uuid,
        live.live_parent_device,
        live.stable_physical_device_id,
        live.stable_physical_device_id_kind,
        live.thunderbolt_evidenced,
    )
    if approved_facts != live_facts or approved_facts[:5] != ("apfs", True, False, True, False):
        raise ValueError("approved and live archive identity or readiness facts differ")
    if approved.free_bytes is None or live.free_bytes is None:
        raise ValueError("approved and live effective free space must be proven")
    if min(approved.free_bytes, live.free_bytes) < MINIMUM_FREE_BYTES:
        raise ValueError("approved or live effective free space is below the minimum")


def _dicts(value: object) -> list[dict[str, object]]:
    found: list[dict[str, object]] = []
    if isinstance(value, dict):
        item = cast(dict[str, object], value)
        found.append(item)
        for child in item.values():
            found.extend(_dicts(child))
    elif isinstance(value, list):
        for child in cast(list[object], value):
            found.extend(_dicts(child))
    return found


def _integer(value: object) -> int | None:
    return value if type(value) is int else None


def _matching_apfs_entries(parsed: object, live: ArchiveCandidate) -> list[tuple[dict[str, object], dict[str, object]]]:
    matches: list[tuple[dict[str, object], dict[str, object]]] = []
    for container in _dicts(parsed):
        volumes_value, stores_value = container.get("Volumes"), container.get("PhysicalStores")
        if not isinstance(volumes_value, list) or not isinstance(stores_value, list):
            continue
        volumes, stores = cast(list[object], volumes_value), cast(list[object], stores_value)
        if len(stores) != 1 or not isinstance(stores[0], dict):
            continue
        store = cast(dict[str, object], stores[0])
        if store.get("DeviceIdentifier") != live.live_parent_device:
            continue
        for volume in volumes:
            if isinstance(volume, dict):
                typed_volume = cast(dict[str, object], volume)
                if typed_volume.get("APFSVolumeUUID") == live.volume_uuid:
                    matches.append((container, typed_volume))
    return matches


def _effective_apfs_free(container: dict[str, object], volume: dict[str, object], expected_quota: int) -> int:
    ceiling = _integer(container.get("CapacityCeiling"))
    free = _integer(container.get("CapacityFree"))
    quota = _integer(volume.get("CapacityQuota"))
    used = _integer(volume.get("CapacityInUse"))
    if any(value is None for value in (ceiling, free, quota, used)):
        raise ValueError("current APFS capacity evidence is incomplete")
    assert ceiling is not None and free is not None and quota is not None and used is not None
    if quota != expected_quota:
        raise ValueError("current APFS quota differs from approval")
    if not all((ceiling > 0, 0 <= free <= ceiling)):
        raise ValueError("current APFS container capacity evidence is impossible")
    if not all((0 <= used <= quota, quota <= ceiling)):
        raise ValueError("current APFS volume capacity evidence is impossible")
    return min(free, quota - used)


def _require_apfs_facts(
    container: dict[str, object],
    volume: dict[str, object],
    profile: ApprovedArchiveProfile,
    live: ArchiveCandidate,
) -> None:
    if volume.get("VolumeName", volume.get("Name")) != profile.public_requirements.volume_name:
        raise ValueError("current APFS volume name differs from the approved profile")
    if volume.get("Encryption") is not True:
        raise ValueError("current APFS encryption state differs from approval")
    if volume.get("Locked") is not False:
        raise ValueError("current APFS lock state differs from approval")
    effective_free = _effective_apfs_free(container, volume, profile.public_requirements.quota_bytes_observed)
    if effective_free < profile.public_requirements.minimum_effective_free_bytes:
        raise ValueError("current APFS effective free space is below the minimum")
    if live.free_bytes != effective_free:
        raise ValueError("fresh preflight and current APFS capacity evidence differ")


def _require_current_apfs(data: bytes, profile: ApprovedArchiveProfile, live: ArchiveCandidate) -> None:
    try:
        parsed = plistlib.loads(data)
    except (plistlib.InvalidFileException, ValueError):
        raise ValueError("current APFS evidence is not a valid plist") from None
    matches = _matching_apfs_entries(parsed, live)
    if len(matches) != 1:
        raise ValueError("current APFS evidence does not uniquely match the archive volume and physical store")
    _require_apfs_facts(*matches[0], profile, live)


def _actual_root(requested: Path, profile: ApprovedArchiveProfile, sandbox: Path | None) -> tuple[Path, Path]:
    logical = PurePosixPath(str(requested))
    approved = profile.public_requirements.canonical_archive_root
    if not logical.is_absolute() or str(logical) != approved:
        raise ValueError("requested root must be the exact approved canonical archive root")
    if sandbox is None:
        return requested, Path("/")
    if not sandbox.is_absolute():
        raise ValueError("injected filesystem root must be absolute")
    return sandbox / Path(*logical.parts[1:]), sandbox


def _require_mount(root: Path, boundary: Path, volume_name: str, is_mount: Callable[[Path], bool]) -> None:
    mount = root.parent
    try:
        relative = mount.relative_to(boundary)
    except ValueError:
        raise ValueError("archive root escapes its filesystem boundary") from None
    current = boundary
    for part in relative.parts:
        current = current / part
        try:
            mode = current.lstat().st_mode
        except OSError:
            raise ValueError("approved archive mount is absent") from None
        if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
            raise ValueError("archive mount path contains a symlink or non-directory")
    if mount.name != volume_name or not is_mount(mount):
        raise ValueError("archive root is not on the exact approved mounted volume")
    if root.is_symlink():
        raise ValueError("archive root must not be a symlink")


def _canonical(model: ArchiveRootMarker | ArchiveInitializationReceipt) -> bytes:
    rendered = json.dumps(model.model_dump(mode="json"), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return f"{rendered}\n".encode()


def _fsync_tree(root: Path) -> None:
    directories = [path for path in root.rglob("*") if path.is_dir()]
    for path in sorted(directories, key=lambda item: len(item.parts), reverse=True):
        _fsync_directory(path)
    _fsync_directory(root)


def _build_archive(
    root: Path,
    profile: ApprovedArchiveProfile,
    profile_hash: str,
    candidate: ArchiveCandidate,
    services: _Services,
) -> ArchiveInitializationReceipt:
    archive_id, created_at = services.new_uuid(), services.now()
    receipt_path = f"registry/archive-initialization/{archive_id}.json"
    marker = ArchiveRootMarker(
        archive_id=archive_id,
        created_at=created_at,
        profile_id=profile.profile_id,
        profile_file_sha256=profile_hash,
        archive_preflight_receipt_sha256=profile.profile_evidence.archive_preflight_receipt_sha256,
        post_merge_apfs_snapshot_sha256=profile.profile_evidence.post_merge_apfs_snapshot_sha256,
        canonical_archive_root=profile.public_requirements.canonical_archive_root,
        volume_name=profile.public_requirements.volume_name,
        stable_volume_identifier=cast(str, candidate.volume_uuid),
        stable_physical_identifier=cast(str, candidate.stable_physical_device_id),
        stable_physical_identifier_kind=cast(StablePhysicalDeviceIdKind, candidate.stable_physical_device_id_kind),
        canary_sha256=CANARY_SHA256,
        canary_relative_path="objects/sha256/fa/faeb22898dfceb94a94874b336f75be3d084f03f8fce2b24b8bf077134a9407b",
        initialization_receipt_relative_path=receipt_path,
    )
    stage = root.parent / f".{root.name}.incoming.{uuid7()}"
    stage.mkdir(mode=0o700)
    _fsync_directory(root.parent)
    try:
        for parts in LAYOUT_DIRECTORIES:
            directory = _directory(stage, *parts)
            os.chmod(directory, 0o755)
        os.chmod(stage, 0o755)
        _write_immutable(stage / CANARY_RELATIVE_PATH, CANARY_BYTES, expected_sha256=CANARY_SHA256)
        marker_hash, _ = _write_immutable(stage / MARKER_PATH, _canonical(marker))
        receipt = ArchiveInitializationReceipt(
            operation_id=archive_id,
            archive_id=archive_id,
            generated_at=created_at,
            disposition="INITIALIZED",
            profile_id=profile.profile_id,
            profile_file_sha256=profile_hash,
            canonical_archive_root=profile.public_requirements.canonical_archive_root,
            marker_relative_path=MARKER_PATH,
            marker_sha256=marker_hash,
            canary_relative_path="objects/sha256/fa/faeb22898dfceb94a94874b336f75be3d084f03f8fce2b24b8bf077134a9407b",
            canary_sha256=CANARY_SHA256,
            initialization_receipt_relative_path=receipt_path,
        )
        _write_immutable(stage / receipt_path, _canonical(receipt))
        _fsync_tree(stage)
        services.before_publish(stage)
        _atomic_rename_absent(stage, root)
        return receipt
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def _parse_marker(data: bytes) -> ArchiveRootMarker:
    try:
        marker = ArchiveRootMarker.model_validate_json(data)
    except ValidationError:
        raise ValueError("archive root marker is invalid") from None
    if data != _canonical(marker):
        raise ValueError("archive root marker is not canonical JSON")
    return marker


def _parse_initialization_receipt(data: bytes) -> ArchiveInitializationReceipt:
    try:
        receipt = ArchiveInitializationReceipt.model_validate_json(data)
    except ValidationError:
        raise ValueError("persisted initialization receipt is invalid") from None
    if data != _canonical(receipt):
        raise ValueError("persisted initialization receipt is not canonical JSON")
    return receipt


def _require_existing_layout(root: Path) -> None:
    if not root.is_dir() or root.is_symlink():
        raise ValueError("existing archive root is not an exact initialized directory")
    if {item.name for item in root.iterdir()} != set(TOP_LEVEL):
        raise ValueError("existing archive root has an unexpected top-level layout")
    for parts in LAYOUT_DIRECTORIES:
        path = root.joinpath(*parts)
        if not path.is_dir() or path.is_symlink():
            raise ValueError("existing archive layout is incomplete or unsafe")


def _require_marker_identity(
    marker: ArchiveRootMarker,
    profile: ApprovedArchiveProfile,
    profile_hash: str,
    candidate: ArchiveCandidate,
) -> None:
    fields = {
        "profile_id",
        "profile_file_sha256",
        "archive_preflight_receipt_sha256",
        "post_merge_apfs_snapshot_sha256",
        "canonical_archive_root",
        "volume_name",
        "stable_volume_identifier",
        "stable_physical_identifier",
        "stable_physical_identifier_kind",
    }
    expected = {
        "profile_id": profile.profile_id,
        "profile_file_sha256": profile_hash,
        "archive_preflight_receipt_sha256": profile.profile_evidence.archive_preflight_receipt_sha256,
        "post_merge_apfs_snapshot_sha256": profile.profile_evidence.post_merge_apfs_snapshot_sha256,
        "canonical_archive_root": profile.public_requirements.canonical_archive_root,
        "volume_name": profile.public_requirements.volume_name,
        "stable_volume_identifier": candidate.volume_uuid,
        "stable_physical_identifier": candidate.stable_physical_device_id,
        "stable_physical_identifier_kind": candidate.stable_physical_device_id_kind,
    }
    if marker.model_dump(include=fields) != expected:
        raise ValueError("archive root marker differs from the approved live identity")


def _require_canary(root: Path, marker: ArchiveRootMarker) -> None:
    canary = root / marker.canary_relative_path
    digest, size = _hash_file(canary, require_read_only=True)
    if (digest, size, _read_regular(canary, "archive canary")) != (CANARY_SHA256, len(CANARY_BYTES), CANARY_BYTES):
        raise ValueError("archive canary is corrupt")


def _persisted_receipt(root: Path, marker: ArchiveRootMarker, marker_hash: str) -> ArchiveInitializationReceipt:
    receipt_file = root / marker.initialization_receipt_relative_path
    persisted = _parse_initialization_receipt(_read_regular(receipt_file, "initialization receipt"))
    _hash_file(receipt_file, require_read_only=True)
    bindings = (
        persisted.disposition == "INITIALIZED",
        persisted.archive_id == marker.archive_id,
        persisted.generated_at == marker.created_at,
        persisted.marker_sha256 == marker_hash,
        persisted.initialization_receipt_relative_path == marker.initialization_receipt_relative_path,
    )
    if not all(bindings):
        raise ValueError("persisted initialization receipt does not match the archive marker")
    return persisted


def _verify_existing(
    root: Path,
    profile: ApprovedArchiveProfile,
    profile_hash: str,
    candidate: ArchiveCandidate,
    services: _Services,
) -> ArchiveInitializationReceipt:
    _require_existing_layout(root)
    marker_data = _read_regular(root / MARKER_PATH, "archive root marker")
    marker_hash, _ = _hash_file(root / MARKER_PATH, require_read_only=True)
    marker = _parse_marker(marker_data)
    _require_marker_identity(marker, profile, profile_hash, candidate)
    _require_canary(root, marker)
    persisted = _persisted_receipt(root, marker, marker_hash)
    return ArchiveInitializationReceipt(
        operation_id=services.new_uuid(),
        archive_id=persisted.archive_id,
        generated_at=services.now(),
        disposition="VERIFIED_EXISTING",
        profile_id=persisted.profile_id,
        profile_file_sha256=persisted.profile_file_sha256,
        canonical_archive_root=persisted.canonical_archive_root,
        marker_relative_path=persisted.marker_relative_path,
        marker_sha256=persisted.marker_sha256,
        canary_relative_path=persisted.canary_relative_path,
        canary_sha256=persisted.canary_sha256,
        initialization_receipt_relative_path=persisted.initialization_receipt_relative_path,
    )


def initialize_archive(
    profile_path: Path,
    private_receipt_path: Path,
    private_apfs_snapshot_path: Path,
    requested_root: Path,
    *,
    _services: _Services | None = None,
) -> ArchiveInitializationReceipt:
    services = _services or _Services()
    profile, profile_hash = _load_profile(profile_path)
    receipt_data = _read_regular(private_receipt_path, "approved private receipt")
    snapshot_data = _read_regular(private_apfs_snapshot_path, "approved private APFS snapshot")
    if (
        services.evidence_digest(private_receipt_path, receipt_data)
        != profile.profile_evidence.archive_preflight_receipt_sha256
    ):
        raise ValueError("approved private receipt hash differs from the public profile")
    if (
        services.evidence_digest(private_apfs_snapshot_path, snapshot_data)
        != profile.profile_evidence.post_merge_apfs_snapshot_sha256
    ):
        raise ValueError("approved private APFS snapshot hash differs from the public profile")
    approved = _ready_candidate(
        _load_private_receipt(receipt_data), profile.public_requirements.volume_name, "approved receipt"
    )
    live_receipt = services.inspect(profile.public_requirements.volume_name)
    live = _ready_candidate(live_receipt, profile.public_requirements.volume_name, "fresh preflight")
    _require_candidate_agreement(approved, live)
    _require_current_apfs(services.current_apfs(), profile, live)
    root, boundary = _actual_root(requested_root, profile, services.sandbox_root)
    _require_mount(root, boundary, profile.public_requirements.volume_name, services.is_mount)
    if root.exists() or root.is_symlink():
        if not (root / MARKER_PATH).is_file() or (root / MARKER_PATH).is_symlink():
            raise ValueError("every existing unmarked archive root is rejected")
        return _verify_existing(root, profile, profile_hash, live, services)
    return _build_archive(root, profile, profile_hash, live, services)
