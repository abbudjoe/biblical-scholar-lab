from __future__ import annotations

import json
import platform
import plistlib
import subprocess
from collections.abc import Callable
from datetime import UTC, datetime
from typing import cast

from uuid6 import uuid7

from bsl.contracts.archive import (
    ArchiveCandidate,
    ArchivePreflightReceipt,
    ArchiveReadiness,
    StablePhysicalDeviceIdKind,
    evaluate_archive_candidate,
)

RunCommand = Callable[[tuple[str, ...]], bytes]


def _run(argv: tuple[str, ...]) -> bytes:
    completed = subprocess.run(argv, check=False, capture_output=True, timeout=15)
    if completed.returncode != 0:
        raise RuntimeError(f"inspection command failed: {argv[0]} {argv[1]}")
    return completed.stdout


def _values(value: object) -> list[dict[str, object]]:
    found: list[dict[str, object]] = []
    if isinstance(value, dict):
        item = cast(dict[str, object], value)
        found.append(item)
        for child in item.values():
            found.extend(_values(child))
    elif isinstance(value, list):
        for child in cast(list[object], value):
            found.extend(_values(child))
    return found


def _optional[T](value: object, kind: type[T]) -> T | None:
    return value if isinstance(value, kind) else None


def _device_ids(value: object) -> list[str]:
    identities = (item.get("DeviceIdentifier") for item in _values(value))
    return [identity for identity in identities if isinstance(identity, str) and identity]


def _receipt(
    name: str,
    readiness: ArchiveReadiness,
    reasons: tuple[str, ...],
    count: int,
    candidate: ArchiveCandidate | None = None,
) -> ArchivePreflightReceipt:
    return ArchivePreflightReceipt(
        receipt_id=uuid7(),
        generated_at=datetime.now(UTC),
        requested_volume_name=name,
        readiness=readiness,
        reasons=reasons,
        candidate_count=count,
        candidate=candidate,
    )


def _matching_volumes(data: dict[str, object], name: str) -> list[dict[str, object]]:
    matches = {
        str(item.get("DeviceIdentifier") or id(item)): item for item in _values(data) if item.get("VolumeName") == name
    }
    return list(matches.values())


def _compatible_uuid(selected: str | None, observed: str | None) -> bool:
    return not selected or not observed or selected == observed


def _apfs_match(
    apfs: dict[str, object], volume_device: str, volume_uuid: str | None
) -> tuple[dict[str, object] | None, dict[str, object] | None, str | None]:
    matches: list[tuple[dict[str, object], dict[str, object], str]] = []
    for container in _values(apfs):
        volumes = container.get("Volumes")
        stores = container.get("PhysicalStores")
        if not isinstance(volumes, list) or not isinstance(stores, list):
            continue
        parents = _device_ids(cast(list[object], stores))
        if len(parents) != 1:
            continue
        for value in cast(list[object], volumes):
            if not isinstance(value, dict):
                continue
            volume = cast(dict[str, object], value)
            if volume.get("DeviceIdentifier") != volume_device:
                continue
            apfs_uuid = _optional(volume.get("APFSVolumeUUID"), str)
            if not _compatible_uuid(volume_uuid, apfs_uuid):
                continue
            matches.append((container, volume, parents[0]))
    return matches[0] if len(matches) == 1 else (None, None, None)


def _encryption_evidence(info: dict[str, object], volume: dict[str, object] | None) -> bool | None:
    if volume is None:
        return None
    fields = ("APFSEncrypted", "Encrypted", "Encryption", "EncryptionThisVolumeProper")
    observed: list[bool] = []
    for key in fields:
        value = info.get(key)
        if isinstance(value, bool):
            observed.append(value)
    volume_encryption = volume.get("Encryption")
    if isinstance(volume_encryption, bool):
        observed.append(volume_encryption)
    return observed[0] if observed and all(value == observed[0] for value in observed) else None


def _exact_integer(value: object) -> int | None:
    return value if type(value) is int else None


def _container_capacity(container: dict[str, object]) -> tuple[int, int] | None:
    ceiling = _exact_integer(container.get("CapacityCeiling"))
    free = _exact_integer(container.get("CapacityFree"))
    if ceiling is None or free is None:
        return None
    if ceiling <= 0 or free < 0 or free > ceiling:
        return None
    return ceiling, free


def _effective_free(container: dict[str, object] | None, volume: dict[str, object] | None) -> int | None:
    if container is None or volume is None:
        return None
    capacity = _container_capacity(container)
    if capacity is None:
        return None
    ceiling, free = capacity
    if "CapacityQuota" not in volume:
        return free
    quota = _exact_integer(volume.get("CapacityQuota"))
    if quota == 0:
        return free
    used = _exact_integer(volume.get("CapacityInUse"))
    if quota is None or used is None or not 0 <= used <= quota <= ceiling:
        return None
    return min(free, quota - used)


def _thunderbolt_evidenced(profile: bytes, parent_device: str) -> bool:
    parsed = json.loads(profile)
    normalized = parent_device.removeprefix("/dev/")
    return any(item.get("bsd_name") == normalized or item.get("BSD Name") == normalized for item in _values(parsed))


def _candidate(
    info: dict[str, object],
    container: dict[str, object] | None,
    apfs_volume: dict[str, object] | None,
    parent: str | None,
    parent_info: dict[str, object],
    thunderbolt: bool,
) -> ArchiveCandidate:
    filesystem = info.get("FilesystemType") or info.get("FileSystemPersonality")
    internal = info.get("Internal")
    mount_point = info.get("MountPoint")
    read_only = info.get("ReadOnlyVolume", info.get("ReadOnlyMedia"))
    if read_only is None and isinstance(info.get("Writable"), bool):
        read_only = not info["Writable"]
    volume_uuid = info.get("VolumeUUID")
    stable_id = _optional(parent_info.get("MediaUUID"), str)
    stable_kind = StablePhysicalDeviceIdKind.MEDIA_UUID if stable_id else None
    if not stable_id:
        stable_id = _optional(parent_info.get("DiskUUID"), str)
        stable_kind = StablePhysicalDeviceIdKind.DISK_UUID if stable_id else None
    return ArchiveCandidate(
        filesystem=_optional(filesystem, str),
        encrypted=_encryption_evidence(info, apfs_volume),
        internal=_optional(internal, bool),
        mounted=bool(_optional(mount_point, str)),
        read_only=_optional(read_only, bool),
        volume_uuid=_optional(volume_uuid, str),
        live_parent_device=parent,
        stable_physical_device_id=stable_id,
        stable_physical_device_id_kind=stable_kind,
        free_bytes=_effective_free(container, apfs_volume),
        thunderbolt_evidenced=thunderbolt,
    )


def inspect_volume(volume_name: str, *, system: str | None = None, run: RunCommand = _run) -> ArchivePreflightReceipt:
    if (system or platform.system()) != "Darwin":
        return _receipt(volume_name, ArchiveReadiness.UNSUPPORTED_HOST, ("DARWIN_REQUIRED",), 0)
    try:
        listing = cast(dict[str, object], plistlib.loads(run(("diskutil", "list", "-plist"))))
        matches = _matching_volumes(listing, volume_name)
        if not matches:
            return _receipt(volume_name, ArchiveReadiness.VOLUME_NOT_FOUND, ("NO_EXACT_NAME_MATCH",), 0)
        if len(matches) != 1:
            return _receipt(
                volume_name, ArchiveReadiness.AMBIGUOUS_VOLUME, ("MULTIPLE_EXACT_NAME_MATCHES",), len(matches)
            )
        device = matches[0].get("DeviceIdentifier")
        if not isinstance(device, str) or not device:
            return _receipt(volume_name, ArchiveReadiness.IDENTITY_INCOMPLETE, ("DEVICE_ID_NOT_PROVEN",), 1)
        info = cast(dict[str, object], plistlib.loads(run(("diskutil", "info", "-plist", device))))
        apfs = cast(dict[str, object], plistlib.loads(run(("diskutil", "apfs", "list", "-plist"))))
        container, apfs_volume, parent = _apfs_match(apfs, device, _optional(info.get("VolumeUUID"), str))
        parent_info: dict[str, object] = {}
        thunderbolt = False
        if parent:
            parent_info = cast(
                dict[str, object],
                plistlib.loads(run(("diskutil", "info", "-plist", parent))),
            )
            try:
                profile = run(("system_profiler", "SPThunderboltDataType", "-json"))
                thunderbolt = _thunderbolt_evidenced(profile, parent)
            except (RuntimeError, ValueError, json.JSONDecodeError):
                thunderbolt = False
        candidate = _candidate(info, container, apfs_volume, parent, parent_info, thunderbolt)
        readiness, reasons = evaluate_archive_candidate(candidate)
        return _receipt(volume_name, readiness, reasons, 1, candidate)
    except (OSError, RuntimeError, subprocess.SubprocessError, plistlib.InvalidFileException, ValueError):
        return _receipt(volume_name, ArchiveReadiness.INSPECTION_FAILED, ("INSPECTION_TOOL_FAILURE",), 0)
