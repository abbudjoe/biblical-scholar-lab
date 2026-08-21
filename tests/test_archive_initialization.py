from __future__ import annotations

import hashlib
import json
import os
import plistlib
import stat
import subprocess
from collections.abc import Callable, Iterator
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest
from pydantic import ValidationError

import bsl.application.archive_initialization as archive_initialization
import bsl.interfaces.cli as cli
from bsl.application.archive_initialization import CANARY_BYTES, MARKER_PATH, TOP_LEVEL, _Services, initialize_archive
from bsl.contracts.archive import (
    APPROVED_APFS_SHA256,
    APPROVED_PREFLIGHT_SHA256,
    APPROVED_PROFILE_SHA256,
    CANARY_RELATIVE_PATH,
    MINIMUM_FREE_BYTES,
    ApprovedArchiveProfile,
    ArchiveCandidate,
    ArchiveInitializationReceipt,
    ArchivePreflightReceipt,
    ArchiveRootMarker,
    StablePhysicalDeviceIdKind,
    evaluate_archive_candidate,
)

ROOT = Path(__file__).parents[1]
PROFILE = ROOT / "profiles/archive/ARCHIVE-PROFILE-BSL-ARCHIVE-v1.json"
PROFILE_SIDECAR = ROOT / "profiles/archive/ARCHIVE-PROFILE-BSL-ARCHIVE-v1.sha256"
LOGICAL_ROOT = Path("/Volumes/BSL-Archive/BiblicalScholarLab")
ARCHIVE_ID = UUID("01890f29-7c00-7000-8000-000000000001")
VERIFY_ID = UUID("01890f29-7c00-7000-8000-000000000002")
CREATED = datetime.fromisoformat("2026-08-20T21:10:47-04:00")
VERIFIED = datetime.fromisoformat("2026-08-20T21:11:47-04:00")
QUOTA = 650_000_003_072
USED = 1_000_000_000
EFFECTIVE_FREE = QUOTA - USED
VOLUME_UUID = "synthetic-volume-uuid"
APPROVED_PARENT = "synthetic-old-parent"
CURRENT_PARENT = "synthetic-current-parent"
STABLE_PHYSICAL_ID = "synthetic-stable-physical-id"
VOLUME_DEVICE = "synthetic-current-volume-device"


def candidate(**updates: object) -> ArchiveCandidate:
    values: dict[str, object] = {
        "filesystem": "apfs",
        "encrypted": True,
        "internal": False,
        "mounted": True,
        "read_only": False,
        "volume_uuid": VOLUME_UUID,
        "live_parent_device": CURRENT_PARENT,
        "stable_physical_device_id": STABLE_PHYSICAL_ID,
        "stable_physical_device_id_kind": StablePhysicalDeviceIdKind.DISK_UUID,
        "free_bytes": EFFECTIVE_FREE,
        "thunderbolt_evidenced": True,
    }
    return ArchiveCandidate.model_validate(values | updates)


def preflight(value: ArchiveCandidate | None = None) -> ArchivePreflightReceipt:
    selected = value or candidate()
    readiness, reasons = evaluate_archive_candidate(selected)
    return ArchivePreflightReceipt(
        receipt_id=UUID("01890f29-7c00-7000-8000-000000000003"),
        generated_at=CREATED,
        requested_volume_name="BSL-Archive",
        readiness=readiness,
        reasons=reasons,
        candidate_count=1,
        candidate=selected,
    )


def apfs(**updates: object) -> bytes:
    volume: dict[str, object] = {
        "VolumeName": "BSL-Archive",
        "DeviceIdentifier": VOLUME_DEVICE,
        "APFSVolumeUUID": VOLUME_UUID,
        "Encryption": True,
        "Locked": False,
        "CapacityQuota": QUOTA,
        "CapacityInUse": USED,
    }
    volume.update(updates)
    physical_store = {
        "DeviceIdentifier": volume.pop("PhysicalStore", CURRENT_PARENT),
        "DiskUUID": volume.pop("PhysicalDiskUUID", STABLE_PHYSICAL_ID),
    }
    container = {
        "CapacityCeiling": 1_000_000_000_000,
        "CapacityFree": 800_000_000_000,
        "Volumes": [volume],
        "PhysicalStores": volume.pop("PhysicalStores", [physical_store]),
    }
    return plistlib.dumps({"Containers": [container]})


def mounted(**updates: object) -> bytes:
    info: dict[str, object] = {
        "VolumeName": "BSL-Archive",
        "VolumeUUID": VOLUME_UUID,
        "MountPoint": str(LOGICAL_ROOT.parent),
        "Internal": False,
        "Writable": True,
        "FilesystemType": "apfs",
        "DeviceIdentifier": VOLUME_DEVICE,
    }
    return plistlib.dumps(info | updates)


def sequence(values: list[Any]) -> Callable[[], Any]:
    iterator: Iterator[Any] = iter(values)
    return lambda: next(iterator)


def setup(tmp_path: Path, **service_updates: object) -> tuple[Path, Path, Path, _Services]:
    receipt_path, snapshot_path = tmp_path / "approved-receipt.json", tmp_path / "approved-apfs.plist"
    receipt_path.write_text(f"{preflight(candidate(live_parent_device=APPROVED_PARENT)).model_dump_json(indent=2)}\n")
    snapshot_path.write_bytes(plistlib.dumps({"ApprovedSyntheticSnapshot": True}))
    sandbox = tmp_path / "sandbox"
    mount = sandbox / "Volumes/BSL-Archive"
    mount.mkdir(parents=True)

    def approved_digest(path: Path, _data: bytes) -> str:
        return APPROVED_PREFLIGHT_SHA256 if path == receipt_path else APPROVED_APFS_SHA256

    services = _Services(
        inspect=lambda _name: preflight(),
        current_apfs=apfs,
        mount_info=lambda _mount: mounted(),
        evidence_digest=approved_digest,
        new_uuid=sequence([ARCHIVE_ID, VERIFY_ID]),
        now=sequence([CREATED, VERIFIED]),
        sandbox_root=sandbox,
    )
    return receipt_path, snapshot_path, sandbox, replace(services, **service_updates)


def run(
    receipt: Path, snapshot: Path, services: _Services, root: Path = LOGICAL_ROOT, profile: Path = PROFILE
) -> ArchiveInitializationReceipt:
    return initialize_archive(profile, receipt, snapshot, root, _services=services)


def test_exact_public_profile_sidecar_and_privacy_contract() -> None:
    data = PROFILE.read_bytes()
    assert hashlib.sha256(data).hexdigest() == APPROVED_PROFILE_SHA256
    assert PROFILE_SIDECAR.read_text() == (
        f"{APPROVED_PROFILE_SHA256}  profiles/archive/ARCHIVE-PROFILE-BSL-ARCHIVE-v1.json\n"
    )
    profile = ApprovedArchiveProfile.model_validate_json(data)
    assert profile.public_requirements.minimum_effective_free_bytes == MINIMUM_FREE_BYTES
    assert profile.privacy.model_dump() == {
        "stable_volume_identifier_committed": False,
        "stable_physical_identifier_committed": False,
        "mount_device_identifier_committed": False,
        "private_evidence_must_remain_uncommitted": True,
    }
    assert "fixture-" not in PROFILE.read_text() and "disk-fixture" not in PROFILE.read_text()


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("profile_evidence", "archive_preflight_receipt_sha256"), "A" * 64),
        (("public_requirements", "canonical_archive_root"), "relative/root"),
        (("public_requirements", "volume_name"), "Other"),
        (("public_requirements", "encrypted"), False),
        (("public_requirements", "quota_bytes_observed"), MINIMUM_FREE_BYTES - 1),
        (("privacy", "stable_volume_identifier_committed"), True),
    ],
)
def test_profile_invariant_mismatches_fail(path: tuple[str, str], value: object) -> None:
    data = json.loads(PROFILE.read_text())
    data[path[0]][path[1]] = value
    with pytest.raises(ValidationError):
        ApprovedArchiveProfile.model_validate(data)


def test_changed_transient_parent_first_layout_and_verification_are_exact_and_unchanged(tmp_path: Path) -> None:
    receipt_path, snapshot_path, sandbox, services = setup(tmp_path)
    first = run(receipt_path, snapshot_path, services)
    root = sandbox / "Volumes/BSL-Archive/BiblicalScholarLab"
    assert first.disposition == "INITIALIZED"
    assert {path.name for path in root.iterdir()} == set(TOP_LEVEL)
    assert (root / CANARY_RELATIVE_PATH).read_bytes() == CANARY_BYTES
    marker = ArchiveRootMarker.model_validate_json((root / MARKER_PATH).read_bytes())
    persisted = ArchiveInitializationReceipt.model_validate_json(
        (root / marker.initialization_receipt_relative_path).read_bytes()
    )
    assert persisted == first and persisted.operation_id == persisted.archive_id == marker.archive_id
    retained = [root / MARKER_PATH, root / CANARY_RELATIVE_PATH, root / marker.initialization_receipt_relative_path]
    assert all(stat.S_IMODE(path.stat().st_mode) == 0o444 for path in retained)
    before = {
        str(path.relative_to(root)): (path.read_bytes(), path.stat().st_mode, path.stat().st_mtime_ns)
        for path in retained
    }
    second = run(receipt_path, snapshot_path, services)
    after = {
        str(path.relative_to(root)): (path.read_bytes(), path.stat().st_mode, path.stat().st_mtime_ns)
        for path in retained
    }
    assert second.disposition == "VERIFIED_EXISTING" and second.operation_id == VERIFY_ID
    assert before == after


@pytest.mark.parametrize("nonempty", [False, True])
def test_every_existing_unmarked_root_fails(tmp_path: Path, nonempty: bool) -> None:
    receipt_path, snapshot_path, sandbox, services = setup(tmp_path)
    root = sandbox / "Volumes/BSL-Archive/BiblicalScholarLab"
    root.mkdir()
    if nonempty:
        (root / "content").write_text("not authoritative")
    with pytest.raises(ValueError, match="unmarked"):
        run(receipt_path, snapshot_path, services)


@pytest.mark.parametrize(
    "requested",
    [
        Path("relative"),
        Path("/tmp/BiblicalScholarLab"),
        Path("/Network/BSL-Archive/BiblicalScholarLab"),
        Path("/Volumes/Other/BiblicalScholarLab"),
        Path("/Volumes/BSL-Archive/../Escape"),
    ],
)
def test_wrong_internal_network_temporary_and_escape_roots_fail(tmp_path: Path, requested: Path) -> None:
    receipt_path, snapshot_path, _sandbox, services = setup(tmp_path)
    with pytest.raises(ValueError, match="exact approved"):
        run(receipt_path, snapshot_path, services, requested)


def test_symlink_mount_root_fails(tmp_path: Path) -> None:
    receipt_path, snapshot_path, sandbox, services = setup(tmp_path)
    mount = sandbox / "Volumes/BSL-Archive"
    mount.rmdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    mount.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        run(receipt_path, snapshot_path, services)


@pytest.mark.parametrize(
    "writability",
    [
        {"Writable": True, "WritableVolume": True, "WritableMedia": True},
        {"Writable": True, "ReadOnlyVolume": False},
        {"Writable": True, "ReadOnlyMedia": False},
    ],
)
def test_supported_positive_mount_writability_evidence_passes(tmp_path: Path, writability: dict[str, object]) -> None:
    receipt_path, snapshot_path, _sandbox, services = setup(tmp_path)
    receipt = run(
        receipt_path,
        snapshot_path,
        replace(services, mount_info=lambda _mount: mounted(**writability)),
    )
    assert receipt.disposition == "INITIALIZED"


@pytest.mark.parametrize(
    "changes",
    [
        {"FilesystemType": "other"},
        {"VolumeUUID": "other-volume"},
        {"DeviceIdentifier": "other-device"},
        {"MountPoint": "/synthetic/other"},
        {"VolumeName": "Other"},
        {"Internal": True},
        {"Writable": False},
        {"WritableVolume": False},
        {"WritableMedia": False},
        {"ReadOnlyVolume": True},
        {"ReadOnlyMedia": True},
        {"ReadOnlyVolume": False, "ReadOnlyMedia": True},
        {"Internal": 0},
        {"Writable": 1},
        {"WritableVolume": 1},
        {"WritableMedia": 1},
        {"ReadOnlyVolume": 0},
        {"ReadOnlyMedia": 0},
    ],
)
def test_mounted_root_identity_or_security_mismatch_fails_before_staging(
    tmp_path: Path, changes: dict[str, object]
) -> None:
    receipt_path, snapshot_path, sandbox, services = setup(tmp_path)
    with pytest.raises(ValueError, match="mounted archive evidence"):
        run(receipt_path, snapshot_path, replace(services, mount_info=lambda _mount: mounted(**changes)))
    assert not (sandbox / "Volumes/BSL-Archive/BiblicalScholarLab").exists()


@pytest.mark.parametrize("data", [b"not a plist", plistlib.dumps([]), plistlib.dumps({})])
def test_missing_malformed_or_non_dictionary_mount_plist_fails(tmp_path: Path, data: bytes) -> None:
    receipt_path, snapshot_path, _sandbox, services = setup(tmp_path)
    with pytest.raises(ValueError, match="mounted archive"):
        run(receipt_path, snapshot_path, replace(services, mount_info=lambda _: data))


def test_production_mount_info_uses_exact_fixed_command_and_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    def run(argv: tuple[str, ...], *, check: bool, capture_output: bool, timeout: int):
        assert (argv, check, capture_output, timeout) == (
            ("diskutil", "info", "-plist", "/Volumes/BSL-Archive"),
            False,
            True,
            15,
        )
        return subprocess.CompletedProcess(argv, 0, b"synthetic plist", b"")

    monkeypatch.setattr(archive_initialization.subprocess, "run", run)
    assert archive_initialization._mount_info(LOGICAL_ROOT.parent) == b"synthetic plist"


@pytest.mark.parametrize(
    "changes",
    [
        {"volume_uuid": "other-volume"},
        {"stable_physical_device_id": "other-physical"},
        {"stable_physical_device_id_kind": StablePhysicalDeviceIdKind.MEDIA_UUID},
        {"thunderbolt_evidenced": False},
        {"internal": True},
        {"encrypted": False},
        {"free_bytes": MINIMUM_FREE_BYTES - 1},
    ],
)
def test_every_live_identity_security_or_readiness_mismatch_fails(tmp_path: Path, changes: dict[str, object]) -> None:
    receipt_path, snapshot_path, _sandbox, services = setup(tmp_path)
    live = preflight(candidate(**changes))
    with pytest.raises(ValueError):
        run(receipt_path, snapshot_path, replace(services, inspect=lambda _: live))


@pytest.mark.parametrize(
    "changes",
    [
        {"APFSVolumeUUID": "other-volume"},
        {"PhysicalStore": "other-parent"},
        {"PhysicalDiskUUID": "other-physical"},
        {"PhysicalDiskUUID": ""},
        {"PhysicalDiskUUID": 7},
        {"PhysicalStores": [{"DeviceIdentifier": CURRENT_PARENT}]},
        {"PhysicalStores": [{"DeviceIdentifier": CURRENT_PARENT, "DiskUUID": STABLE_PHYSICAL_ID}] * 2},
        {"DeviceIdentifier": ""},
        {"VolumeName": "Other"},
        {"Encryption": False},
        {"Locked": True},
        {"CapacityQuota": QUOTA - 1},
        {"CapacityInUse": QUOTA + 1},
        {"CapacityInUse": -1},
    ],
)
def test_every_current_apfs_volume_security_quota_or_capacity_mismatch_fails(
    tmp_path: Path, changes: dict[str, object]
) -> None:
    receipt_path, snapshot_path, _sandbox, services = setup(tmp_path)
    with pytest.raises(ValueError):
        run(receipt_path, snapshot_path, replace(services, current_apfs=lambda: apfs(**changes)))


@pytest.mark.parametrize("which", ["receipt", "snapshot"])
def test_private_evidence_hash_mismatch_fails_before_initialization(tmp_path: Path, which: str) -> None:
    receipt_path, snapshot_path, sandbox, services = setup(tmp_path)

    def digest(path: Path, _data: bytes) -> str:
        expected = APPROVED_PREFLIGHT_SHA256 if path == receipt_path else APPROVED_APFS_SHA256
        return "0" * 64 if path == (receipt_path if which == "receipt" else snapshot_path) else expected

    with pytest.raises(ValueError, match="hash differs"):
        run(receipt_path, snapshot_path, replace(services, evidence_digest=digest))
    assert not (sandbox / "Volumes/BSL-Archive/BiblicalScholarLab").exists()


@pytest.mark.parametrize(
    "current",
    [
        b"not a plist",
        apfs(CapacityQuota="invalid"),
        apfs(CapacityInUse=QUOTA - MINIMUM_FREE_BYTES + 1),
        apfs(CapacityInUse=USED + 1),
    ],
)
def test_malformed_insufficient_or_inconsistent_current_capacity_fails(tmp_path: Path, current: bytes) -> None:
    receipt_path, snapshot_path, _sandbox, services = setup(tmp_path)
    with pytest.raises(ValueError):
        run(receipt_path, snapshot_path, replace(services, current_apfs=lambda: current))


def test_semantically_invalid_private_receipt_and_changed_public_profile_fail(tmp_path: Path) -> None:
    receipt_path, snapshot_path, _sandbox, services = setup(tmp_path)
    receipt_path.write_text("{}\n")
    with pytest.raises(ValueError, match="semantically valid"):
        run(receipt_path, snapshot_path, services)
    changed_profile = tmp_path / "changed-profile.json"
    changed_profile.write_bytes(PROFILE.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="profile hash"):
        run(receipt_path, snapshot_path, services, profile=changed_profile)


@pytest.mark.parametrize("case", ["top", "marker", "receipt", "canary-bytes", "canary-mode"])
def test_existing_corruption_fails_closed(tmp_path: Path, case: str) -> None:
    receipt_path, snapshot_path, sandbox, services = setup(tmp_path)
    run(receipt_path, snapshot_path, services)
    root = sandbox / "Volumes/BSL-Archive/BiblicalScholarLab"
    marker = ArchiveRootMarker.model_validate_json((root / MARKER_PATH).read_bytes())
    target = root / MARKER_PATH
    if case == "top":
        (root / "unexpected").mkdir()
    elif case == "receipt":
        target = root / marker.initialization_receipt_relative_path
    elif case.startswith("canary"):
        target = root / CANARY_RELATIVE_PATH
    if case not in {"top", "canary-mode"}:
        os.chmod(target, 0o644)
        target.write_bytes(b"corrupt\n")
        os.chmod(target, 0o444)
    elif case == "canary-mode":
        os.chmod(target, 0o644)
    with pytest.raises(ValueError):
        run(receipt_path, snapshot_path, services)


def test_staged_failure_cleans_only_its_attempt_and_leaves_no_root(tmp_path: Path) -> None:
    receipt_path, snapshot_path, sandbox, services = setup(tmp_path)
    mount = sandbox / "Volumes/BSL-Archive"
    unrelated = mount / ".BiblicalScholarLab.incoming.unrelated"
    unrelated.mkdir()

    def fail(_stage: Path) -> None:
        raise RuntimeError("synthetic staged failure")

    with pytest.raises(RuntimeError, match="synthetic staged failure"):
        run(receipt_path, snapshot_path, replace(services, before_publish=fail))
    assert unrelated.is_dir()
    assert not (mount / "BiblicalScholarLab").exists()
    assert list(mount.iterdir()) == [unrelated]


def test_atomic_publication_refuses_a_root_that_appears_during_staging(tmp_path: Path) -> None:
    receipt_path, snapshot_path, sandbox, services = setup(tmp_path)
    root = sandbox / "Volumes/BSL-Archive/BiblicalScholarLab"
    with pytest.raises(FileExistsError):
        run(receipt_path, snapshot_path, replace(services, before_publish=lambda _stage: root.mkdir()))
    assert root.is_dir() and not any(root.iterdir())


def test_cli_initialize_emits_schema_valid_receipt_without_fixture_options(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    receipt_path, snapshot_path, _sandbox, services = setup(tmp_path)
    receipt = run(receipt_path, snapshot_path, services)
    calls: list[tuple[Path, Path, Path, Path]] = []
    monkeypatch.setattr(cli, "initialize_archive", lambda *args: calls.append(args) or receipt)
    argv = ["archive", "initialize", "--profile", "profile.json", "--private-receipt", "receipt.json"]
    argv += ["--private-apfs-snapshot", "snapshot.plist", "--root", str(LOGICAL_ROOT)]
    assert cli.main(argv) == 0
    assert ArchiveInitializationReceipt.model_validate_json(capsys.readouterr().out) == receipt
    assert calls == [(Path("profile.json"), Path("receipt.json"), Path("snapshot.plist"), LOGICAL_ROOT)]
