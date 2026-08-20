from __future__ import annotations

import json
import platform
import plistlib
import subprocess
from collections.abc import Callable
from datetime import UTC, datetime
from typing import cast

from uuid6 import uuid7

from bsl.contracts.archive import ArchiveCandidate, ArchivePreflightReceipt, ArchiveReadiness

MINIMUM_FREE_BYTES = 20 * 1024**3
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


def _parent_device(apfs: dict[str, object], volume_device: str) -> str | None:
    for item in _values(apfs):
        volumes = item.get("Volumes")
        stores = item.get("PhysicalStores")
        if not isinstance(volumes, list) or not isinstance(stores, list):
            continue
        if volume_device not in _device_ids(cast(list[object], volumes)):
            continue
        valid = _device_ids(cast(list[object], stores))
        return valid[0] if len(valid) == 1 else None
    return None


def _thunderbolt_evidenced(profile: bytes, parent_device: str) -> bool:
    parsed = json.loads(profile)
    normalized = parent_device.removeprefix("/dev/")
    return any(item.get("bsd_name") == normalized or item.get("BSD Name") == normalized for item in _values(parsed))


def _candidate(info: dict[str, object], parent: str | None, thunderbolt: bool) -> ArchiveCandidate:
    filesystem = info.get("FilesystemType") or info.get("FileSystemPersonality")
    encrypted = info.get("APFSEncrypted", info.get("Encrypted"))
    internal = info.get("Internal")
    mount_point = info.get("MountPoint")
    read_only = info.get("ReadOnlyVolume", info.get("ReadOnlyMedia"))
    if read_only is None and isinstance(info.get("Writable"), bool):
        read_only = not info["Writable"]
    free_bytes = info.get("FreeSpace", info.get("VolumeFreeSpace"))
    volume_uuid = info.get("VolumeUUID")
    return ArchiveCandidate(
        filesystem=_optional(filesystem, str),
        encrypted=_optional(encrypted, bool),
        internal=_optional(internal, bool),
        mounted=bool(_optional(mount_point, str)),
        read_only=_optional(read_only, bool),
        volume_uuid=_optional(volume_uuid, str),
        parent_physical_device=parent,
        free_bytes=_optional(free_bytes, int),
        thunderbolt_evidenced=thunderbolt,
    )


def _space_readiness(free_bytes: int | None) -> tuple[ArchiveReadiness, tuple[str, ...]] | None:
    if free_bytes is None:
        return ArchiveReadiness.IDENTITY_INCOMPLETE, ("FREE_SPACE_NOT_PROVEN",)
    low_space = ArchiveReadiness.INSUFFICIENT_SPACE, ("LESS_THAN_20_GIB_FREE",)
    return low_space if free_bytes < MINIMUM_FREE_BYTES else None


def _readiness(candidate: ArchiveCandidate) -> tuple[ArchiveReadiness, tuple[str, ...]]:
    if None in (candidate.filesystem, candidate.internal, candidate.encrypted):
        return ArchiveReadiness.IDENTITY_INCOMPLETE, ("REQUIRED_VOLUME_FACT_NOT_PROVEN",)
    if cast(str, candidate.filesystem).lower() != "apfs":
        return ArchiveReadiness.NOT_APFS, ("FILESYSTEM_NOT_APFS",)
    if not candidate.encrypted:
        return ArchiveReadiness.NOT_ENCRYPTED, ("ENCRYPTION_NOT_PROVEN",)
    if candidate.internal:
        return ArchiveReadiness.NOT_EXTERNAL, ("VOLUME_IS_INTERNAL",)
    if not candidate.mounted:
        return ArchiveReadiness.IDENTITY_INCOMPLETE, ("VOLUME_NOT_MOUNTED",)
    if candidate.read_only is not False:
        return ArchiveReadiness.READ_ONLY, ("VOLUME_READ_ONLY_OR_UNKNOWN",)
    if not all((candidate.volume_uuid, candidate.parent_physical_device)):
        return ArchiveReadiness.IDENTITY_INCOMPLETE, ("STABLE_IDENTITY_NOT_PROVEN",)
    if space_readiness := _space_readiness(candidate.free_bytes):
        return space_readiness
    if not candidate.thunderbolt_evidenced:
        return ArchiveReadiness.IDENTITY_INCOMPLETE, ("THUNDERBOLT_NOT_PROVEN",)
    return ArchiveReadiness.CANDIDATE_READY_FOR_OWNER_APPROVAL, ()


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
        parent = _parent_device(apfs, device)
        thunderbolt = False
        if parent:
            try:
                profile = run(("system_profiler", "SPThunderboltDataType", "-json"))
                thunderbolt = _thunderbolt_evidenced(profile, parent)
            except (RuntimeError, ValueError, json.JSONDecodeError):
                thunderbolt = False
        candidate = _candidate(info, parent, thunderbolt)
        readiness, reasons = _readiness(candidate)
        return _receipt(volume_name, readiness, reasons, 1, candidate)
    except (OSError, RuntimeError, subprocess.SubprocessError, plistlib.InvalidFileException, ValueError):
        return _receipt(volume_name, ArchiveReadiness.INSPECTION_FAILED, ("INSPECTION_TOOL_FAILURE",), 0)
