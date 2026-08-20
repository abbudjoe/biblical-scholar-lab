from __future__ import annotations

import hashlib
import json
import os
import plistlib
import tempfile
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError
from uuid6 import uuid7

from bsl.contracts.archive import (
    MINIMUM_FREE_BYTES,
    ArchiveCandidate,
    ArchiveObjectPromotionReceipt,
    ArchivePreflightReceipt,
    ArchiveReadiness,
    StablePhysicalDeviceIdKind,
    evaluate_archive_candidate,
)
from bsl.infrastructure.archive_store import FIXTURE_MARKER, FIXTURE_MARKER_BYTES, promote_synthetic
from bsl.infrastructure.macos_volume import inspect_volume

RunCommand = Callable[[tuple[str, ...]], bytes]
LIST = {"AllDisksAndPartitions": [{"APFSVolumes": [{"VolumeName": "BSL-Archive", "DeviceIdentifier": "disk4s1"}]}]}
INFO = {"FilesystemType": "apfs", "APFSEncrypted": True, "Internal": False, "MountPoint": "/fixture/archive"}
INFO |= {"ReadOnlyVolume": False, "VolumeUUID": "fixture-volume-uuid", "FreeSpace": MINIMUM_FREE_BYTES}
APFS = {
    "Containers": [{"Volumes": [{"DeviceIdentifier": "disk4s1"}], "PhysicalStores": [{"DeviceIdentifier": "disk4"}]}]
}
PARENT_INFO = {"MediaUUID": "fixture-media-uuid", "DiskUUID": "fixture-disk-uuid"}
PROFILE = {"SPThunderboltDataType": [{"_items": [{"bsd_name": "disk4"}]}]}


def runner(
    *,
    listing: object = LIST,
    info: object = INFO,
    apfs: object = APFS,
    parent_info: object = PARENT_INFO,
    profile: object = PROFILE,
    calls: list[tuple[str, ...]] | None = None,
) -> RunCommand:
    outputs = {
        ("diskutil", "list", "-plist"): plistlib.dumps(listing),
        ("diskutil", "info", "-plist", "disk4s1"): plistlib.dumps(info),
        ("diskutil", "apfs", "list", "-plist"): plistlib.dumps(apfs),
        ("diskutil", "info", "-plist", "disk4"): plistlib.dumps(parent_info),
        ("system_profiler", "SPThunderboltDataType", "-json"): json.dumps(profile).encode(),
    }

    def run(argv: tuple[str, ...]) -> bytes:
        if calls is not None:
            calls.append(argv)
        if argv not in outputs:
            raise RuntimeError("unexpected command")
        return outputs[argv]

    return run


def ready_candidate(**changes: object) -> ArchiveCandidate:
    values = {
        "filesystem": "apfs",
        "encrypted": True,
        "internal": False,
        "mounted": True,
        "read_only": False,
        "volume_uuid": "fixture-volume-uuid",
        "live_parent_device": "disk4",
        "stable_physical_device_id": "fixture-media-uuid",
        "stable_physical_device_id_kind": StablePhysicalDeviceIdKind.MEDIA_UUID,
        "free_bytes": MINIMUM_FREE_BYTES,
        "thunderbolt_evidenced": True,
    }
    return ArchiveCandidate.model_validate(values | changes)


def receipt(candidate: ArchiveCandidate) -> ArchivePreflightReceipt:
    readiness, reasons = evaluate_archive_candidate(candidate)
    return ArchivePreflightReceipt(
        receipt_id=uuid7(),
        generated_at=datetime.now(UTC),
        requested_volume_name="BSL-Archive",
        readiness=readiness,
        reasons=reasons,
        candidate_count=1,
        candidate=candidate,
    )


def data(model: ArchivePreflightReceipt | ArchiveObjectPromotionReceipt) -> dict[str, Any]:
    return json.loads(model.model_dump_json())


def reject_preflight(value: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        ArchivePreflightReceipt.model_validate_json(json.dumps(value))


def test_live_parent_and_separate_stable_media_identity_reach_ready() -> None:
    calls: list[tuple[str, ...]] = []
    result = inspect_volume("BSL-Archive", system="Darwin", run=runner(calls=calls))
    assert (result.readiness, result.reasons) == (ArchiveReadiness.CANDIDATE_READY_FOR_OWNER_APPROVAL, ())
    assert result.candidate and evaluate_archive_candidate(result.candidate) == (result.readiness, result.reasons)
    assert result.candidate.live_parent_device == "disk4"
    assert result.candidate.stable_physical_device_id == "fixture-media-uuid"
    assert result.candidate.stable_physical_device_id_kind == StablePhysicalDeviceIdKind.MEDIA_UUID
    assert result.candidate.live_parent_device != result.candidate.stable_physical_device_id
    assert ("diskutil", "info", "-plist", "disk4") in calls
    assert ("system_profiler", "SPThunderboltDataType", "-json") in calls
    assert "serial" not in result.model_dump_json().lower()


def test_live_parent_alone_cannot_prove_stable_physical_identity() -> None:
    parent_only = {"DeviceIdentifier": "disk4", "VolumeUUID": "not-a-parent-identity"}
    result = inspect_volume("BSL-Archive", system="Darwin", run=runner(parent_info=parent_only))
    assert (result.readiness, result.reasons) == (
        ArchiveReadiness.IDENTITY_INCOMPLETE,
        ("STABLE_PHYSICAL_DEVICE_ID_NOT_PROVEN",),
    )
    assert result.candidate and result.candidate.live_parent_device == "disk4"
    assert result.candidate.stable_physical_device_id is None


def test_parent_disk_uuid_is_valid_fallback() -> None:
    result = inspect_volume("BSL-Archive", system="Darwin", run=runner(parent_info={"DiskUUID": "fixture-disk-uuid"}))
    assert result.readiness == ArchiveReadiness.CANDIDATE_READY_FOR_OWNER_APPROVAL
    assert result.candidate and result.candidate.stable_physical_device_id_kind == StablePhysicalDeviceIdKind.DISK_UUID


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("filesystem", "hfs"),
        ("filesystem", None),
        ("encrypted", False),
        ("encrypted", None),
        ("internal", True),
        ("internal", None),
        ("mounted", False),
        ("read_only", True),
        ("volume_uuid", None),
        ("live_parent_device", None),
        ("stable_physical_device_id", None),
        ("stable_physical_device_id_kind", None),
        ("free_bytes", MINIMUM_FREE_BYTES - 1),
        ("thunderbolt_evidenced", False),
    ],
)
def test_serialized_ready_candidate_tampering_fails(field: str, value: object) -> None:
    changed = data(receipt(ready_candidate()))
    changed["candidate"][field] = value
    reject_preflight(changed)


@pytest.mark.parametrize(
    ("field", "value"),
    [("candidate", None), ("candidate_count", 2), ("reasons", ["unexpected"]), ("receipt_id", str(uuid4()))],
)
def test_serialized_ready_envelope_tampering_fails(field: str, value: object) -> None:
    changed = data(receipt(ready_candidate()))
    changed[field] = value
    reject_preflight(changed)


def test_candidate_failure_must_match_shared_evaluator() -> None:
    valid = receipt(ready_candidate(encrypted=False))
    assert (valid.readiness, valid.reasons) == (ArchiveReadiness.NOT_ENCRYPTED, ("ENCRYPTION_NOT_PROVEN",))
    for field, value in (("readiness", "NOT_EXTERNAL"), ("reasons", ["wrong"])):
        changed = data(valid)
        changed[field] = value
        reject_preflight(changed)


def test_archive_adapter_global_states_are_exact_and_fail_closed() -> None:
    def failed(_argv: tuple[str, ...]) -> bytes:
        raise RuntimeError("failed")

    duplicate = {"Volumes": [LIST, {"VolumeName": "BSL-Archive", "DeviceIdentifier": "disk5s1"}]}
    no_device = {"VolumeName": "BSL-Archive"}
    cases = (
        (
            inspect_volume("BSL-Archive", system="Darwin", run=runner(listing={})),
            ArchiveReadiness.VOLUME_NOT_FOUND,
            0,
            ("NO_EXACT_NAME_MATCH",),
        ),
        (
            inspect_volume("BSL-Archive", system="Darwin", run=runner(listing=duplicate)),
            ArchiveReadiness.AMBIGUOUS_VOLUME,
            2,
            ("MULTIPLE_EXACT_NAME_MATCHES",),
        ),
        (inspect_volume("BSL-Archive", system="Linux"), ArchiveReadiness.UNSUPPORTED_HOST, 0, ("DARWIN_REQUIRED",)),
        (
            inspect_volume("BSL-Archive", system="Darwin", run=failed),
            ArchiveReadiness.INSPECTION_FAILED,
            0,
            ("INSPECTION_TOOL_FAILURE",),
        ),
        (
            inspect_volume("BSL-Archive", system="Darwin", run=runner(listing=no_device)),
            ArchiveReadiness.IDENTITY_INCOMPLETE,
            1,
            ("DEVICE_ID_NOT_PROVEN",),
        ),
    )
    for valid, readiness, count, reasons in cases:
        assert (valid.readiness, valid.candidate_count, valid.reasons, valid.candidate) == (
            readiness,
            count,
            reasons,
            None,
        )
        for field, value in (("candidate_count", 1 if count != 1 else 0), ("reasons", ["wrong"])):
            changed = data(valid)
            changed[field] = value
            reject_preflight(changed)
    no_protocol = inspect_volume("BSL-Archive", system="Darwin", run=runner(profile={}))
    assert (no_protocol.readiness, no_protocol.reasons) == (
        ArchiveReadiness.IDENTITY_INCOMPLETE,
        ("THUNDERBOLT_NOT_PROVEN",),
    )


def fixture_root(parent: Path) -> Path:
    root = parent / "fixture"
    root.mkdir(parents=True)
    (root / FIXTURE_MARKER).write_bytes(FIXTURE_MARKER_BYTES)
    return root


@given(st.binary(max_size=2048))
@settings(max_examples=12)
def test_synthetic_publish_and_deduplicate(data_bytes: bytes) -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = fixture_root(Path(temporary))
        first, second = promote_synthetic(root, data_bytes), promote_synthetic(root, data_bytes)
        assert (first.disposition, second.disposition) == ("PUBLISHED", "DEDUPLICATED")
        assert (root / first.object_relative_path).read_bytes() == data_bytes
        assert first.object_sha256 == hashlib.sha256(data_bytes).hexdigest()


@pytest.mark.parametrize("case", ["uuid", "prefix", "digest"])
def test_promotion_receipt_serialized_tampering_fails(tmp_path: Path, case: str) -> None:
    published = promote_synthetic(fixture_root(tmp_path), b"contract-object")
    changed = data(published)
    if case == "uuid":
        changed["receipt_id"] = str(uuid4())
    elif case == "prefix":
        prefix = "00" if published.object_sha256[:2] != "00" else "ff"
        changed["object_relative_path"] = f"objects/sha256/{prefix}/{published.object_sha256}"
    else:
        digest = "0" * 64 if published.object_sha256 != "0" * 64 else "f" * 64
        changed["object_relative_path"] = f"objects/sha256/{published.object_sha256[:2]}/{digest}"
    with pytest.raises(ValidationError):
        ArchiveObjectPromotionReceipt.model_validate_json(json.dumps(changed))


def test_promotion_rejects_unsafe_or_corrupt_state(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="marker"):
        promote_synthetic(tmp_path, b"bytes")
    root = fixture_root(tmp_path)
    with pytest.raises(ValueError, match="hash"):
        promote_synthetic(root, b"truncated", expected_sha256=hashlib.sha256(b"complete").hexdigest())
    published = promote_synthetic(root, b"original")
    destination = root / published.object_relative_path
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
    assert {item.disposition for item in receipts} == {"PUBLISHED", "DEDUPLICATED"}
    assert len([path for path in (root / "objects").rglob("*") if path.is_file()]) == 1
