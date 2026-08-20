from __future__ import annotations

import hashlib
import json
import os
import plistlib
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from bsl.contracts.archive import ArchiveReadiness
from bsl.infrastructure.archive_store import FIXTURE_MARKER, FIXTURE_MARKER_BYTES, promote_synthetic
from bsl.infrastructure.macos_volume import MINIMUM_FREE_BYTES, inspect_volume

LIST = {"AllDisksAndPartitions": [{"APFSVolumes": [{"VolumeName": "BSL-Archive", "DeviceIdentifier": "disk4s1"}]}]}
INFO = {"FilesystemType": "apfs", "APFSEncrypted": True, "Internal": False, "MountPoint": "/Volumes/BSL-Archive"}
INFO |= {"ReadOnlyVolume": False, "VolumeUUID": "private-volume-uuid", "FreeSpace": MINIMUM_FREE_BYTES}
APFS = {
    "Containers": [{"Volumes": [{"DeviceIdentifier": "disk4s1"}], "PhysicalStores": [{"DeviceIdentifier": "disk4"}]}]
}
PROFILE = {"SPThunderboltDataType": [{"_items": [{"bsd_name": "disk4"}]}]}


def runner(*, listing: object = LIST, info: object = INFO, apfs: object = APFS, profile: object = PROFILE):
    outputs = {
        ("diskutil", "list", "-plist"): plistlib.dumps(listing),
        ("diskutil", "info", "-plist", "disk4s1"): plistlib.dumps(info),
        ("diskutil", "apfs", "list", "-plist"): plistlib.dumps(apfs),
        ("system_profiler", "SPThunderboltDataType", "-json"): json.dumps(profile).encode(),
    }

    def run(argv: tuple[str, ...]) -> bytes:
        if argv not in outputs:
            raise RuntimeError("unexpected command")
        return outputs[argv]

    return run


def test_archive_readiness_matrix() -> None:
    ready = inspect_volume("BSL-Archive", system="Darwin", run=runner())
    assert ready.readiness == ArchiveReadiness.CANDIDATE_READY_FOR_OWNER_APPROVAL
    assert ready.candidate and ready.candidate.thunderbolt_evidenced
    cases = [
        ({"FilesystemType": "hfs"}, ArchiveReadiness.NOT_APFS),
        ({"APFSEncrypted": False}, ArchiveReadiness.NOT_ENCRYPTED),
        ({"Internal": True}, ArchiveReadiness.NOT_EXTERNAL),
        ({"ReadOnlyVolume": True}, ArchiveReadiness.READ_ONLY),
        ({"FreeSpace": MINIMUM_FREE_BYTES - 1}, ArchiveReadiness.INSUFFICIENT_SPACE),
        ({"VolumeUUID": ""}, ArchiveReadiness.IDENTITY_INCOMPLETE),
        ({"MountPoint": ""}, ArchiveReadiness.IDENTITY_INCOMPLETE),
    ]
    for change, expected in cases:
        result = inspect_volume("BSL-Archive", system="Darwin", run=runner(info=INFO | change))
        assert result.readiness == expected


def test_archive_name_protocol_host_and_tool_fail_closed() -> None:
    assert (
        inspect_volume("BSL-Archive", system="Darwin", run=runner(listing={})).readiness
        == ArchiveReadiness.VOLUME_NOT_FOUND
    )
    duplicate = {"Volumes": [LIST, {"VolumeName": "BSL-Archive", "DeviceIdentifier": "disk5s1"}]}
    ambiguous = inspect_volume("BSL-Archive", system="Darwin", run=runner(listing=duplicate))
    assert ambiguous.readiness == ArchiveReadiness.AMBIGUOUS_VOLUME
    no_protocol = inspect_volume("BSL-Archive", system="Darwin", run=runner(profile={}))
    assert (no_protocol.readiness, no_protocol.reasons) == (
        ArchiveReadiness.IDENTITY_INCOMPLETE,
        ("THUNDERBOLT_NOT_PROVEN",),
    )

    def failed(_argv: tuple[str, ...]) -> bytes:
        raise RuntimeError("failed")

    assert inspect_volume("BSL-Archive", system="Darwin", run=failed).readiness == ArchiveReadiness.INSPECTION_FAILED
    assert inspect_volume("BSL-Archive", system="Linux").readiness == ArchiveReadiness.UNSUPPORTED_HOST


def fixture_root(parent: Path) -> Path:
    root = parent / "fixture"
    root.mkdir(parents=True)
    (root / FIXTURE_MARKER).write_bytes(FIXTURE_MARKER_BYTES)
    return root


@given(st.binary(max_size=2048))
@settings(max_examples=12)
def test_synthetic_publish_and_deduplicate(data: bytes) -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = fixture_root(Path(temporary))
        first, second = promote_synthetic(root, data), promote_synthetic(root, data)
        assert (first.disposition, second.disposition) == ("PUBLISHED", "DEDUPLICATED")
        assert (root / first.object_relative_path).read_bytes() == data
        assert first.object_sha256 == hashlib.sha256(data).hexdigest()


def test_promotion_rejects_unsafe_or_corrupt_state(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="marker"):
        promote_synthetic(tmp_path, b"bytes")
    root = fixture_root(tmp_path)
    with pytest.raises(ValueError, match="hash"):
        promote_synthetic(root, b"truncated", expected_sha256=hashlib.sha256(b"complete").hexdigest())
    receipt = promote_synthetic(root, b"original")
    destination = root / receipt.object_relative_path
    os.chmod(destination, 0o600)
    destination.write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="corrupt"):
        promote_synthetic(root, b"original")
    unsafe, outside = fixture_root(tmp_path / "other"), tmp_path / "outside"
    outside.mkdir()
    (unsafe / ".incoming").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        promote_synthetic(unsafe, b"bytes")


def test_concurrent_identical_publication_is_one_object(tmp_path: Path) -> None:
    root = fixture_root(tmp_path)
    with ThreadPoolExecutor(max_workers=2) as pool:
        receipts = list(pool.map(lambda _: promote_synthetic(root, b"same"), range(2)))
    assert {receipt.disposition for receipt in receipts} == {"PUBLISHED", "DEDUPLICATED"}
    assert len([path for path in (root / "objects").rglob("*") if path.is_file()]) == 1
