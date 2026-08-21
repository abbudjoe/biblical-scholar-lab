from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

STRICT = ConfigDict(strict=True, frozen=True, extra="forbid", allow_inf_nan=False)
MINIMUM_FREE_BYTES = 20 * 1024**3
APPROVED_PROFILE_SHA256 = "1b1571c1b18a1c0e73858b2e3d24d2e1be848e01651665e25f99c9e110c58ef7"
APPROVED_PREFLIGHT_SHA256 = "6c3baa9f428bbe55b0062a06af214a1892510375edcb82f47748e5fc5ff8da0c"
APPROVED_APFS_SHA256 = "5cbef8cee7f9f180afc941380eb2bbfc5d053026ce94444ea513da5360818870"
CANARY_SHA256 = "faeb22898dfceb94a94874b336f75be3d084f03f8fce2b24b8bf077134a9407b"
CANARY_RELATIVE_PATH = f"objects/sha256/fa/{CANARY_SHA256}"
SHA256_PATTERN = r"^[0-9a-f]{64}$"


class ArchiveReadiness(StrEnum):
    CANDIDATE_READY_FOR_OWNER_APPROVAL = "CANDIDATE_READY_FOR_OWNER_APPROVAL"
    VOLUME_NOT_FOUND = "VOLUME_NOT_FOUND"
    AMBIGUOUS_VOLUME = "AMBIGUOUS_VOLUME"
    NOT_APFS = "NOT_APFS"
    NOT_ENCRYPTED = "NOT_ENCRYPTED"
    NOT_EXTERNAL = "NOT_EXTERNAL"
    IDENTITY_INCOMPLETE = "IDENTITY_INCOMPLETE"
    INSUFFICIENT_SPACE = "INSUFFICIENT_SPACE"
    READ_ONLY = "READ_ONLY"
    UNSUPPORTED_HOST = "UNSUPPORTED_HOST"
    INSPECTION_FAILED = "INSPECTION_FAILED"


class StablePhysicalDeviceIdKind(StrEnum):
    MEDIA_UUID = "MEDIA_UUID"
    DISK_UUID = "DISK_UUID"


class ArchiveCandidate(BaseModel):
    model_config = STRICT

    filesystem: str | None
    encrypted: bool | None
    internal: bool | None
    mounted: bool
    read_only: bool | None
    volume_uuid: str | None
    live_parent_device: str | None
    stable_physical_device_id: str | None
    stable_physical_device_id_kind: StablePhysicalDeviceIdKind | None
    free_bytes: int | None = Field(ge=0)
    thunderbolt_evidenced: bool


def evaluate_archive_candidate(candidate: ArchiveCandidate) -> tuple[ArchiveReadiness, tuple[str, ...]]:
    incomplete = ArchiveReadiness.IDENTITY_INCOMPLETE
    missing_facts = any(value is None for value in (candidate.filesystem, candidate.encrypted, candidate.internal))
    stable_physical_id_missing = not (candidate.stable_physical_device_id and candidate.stable_physical_device_id_kind)
    checks = (
        (missing_facts, incomplete, "REQUIRED_VOLUME_FACT_NOT_PROVEN"),
        (
            candidate.filesystem is not None and candidate.filesystem.lower() != "apfs",
            ArchiveReadiness.NOT_APFS,
            "FILESYSTEM_NOT_APFS",
        ),
        (candidate.encrypted is False, ArchiveReadiness.NOT_ENCRYPTED, "ENCRYPTION_NOT_PROVEN"),
        (candidate.internal is True, ArchiveReadiness.NOT_EXTERNAL, "VOLUME_IS_INTERNAL"),
        (not candidate.mounted, incomplete, "VOLUME_NOT_MOUNTED"),
        (candidate.read_only is not False, ArchiveReadiness.READ_ONLY, "VOLUME_READ_ONLY_OR_UNKNOWN"),
        (not candidate.volume_uuid, incomplete, "STABLE_VOLUME_ID_NOT_PROVEN"),
        (not candidate.live_parent_device, incomplete, "LIVE_PARENT_DEVICE_NOT_PROVEN"),
        (stable_physical_id_missing, incomplete, "STABLE_PHYSICAL_DEVICE_ID_NOT_PROVEN"),
        (candidate.free_bytes is None, incomplete, "FREE_SPACE_NOT_PROVEN"),
        (
            candidate.free_bytes is not None and candidate.free_bytes < MINIMUM_FREE_BYTES,
            ArchiveReadiness.INSUFFICIENT_SPACE,
            "LESS_THAN_20_GIB_FREE",
        ),
        (not candidate.thunderbolt_evidenced, incomplete, "THUNDERBOLT_NOT_PROVEN"),
    )
    for failed, readiness, reason in checks:
        if failed:
            return readiness, (reason,)
    return ArchiveReadiness.CANDIDATE_READY_FOR_OWNER_APPROVAL, ()


def _uuid7(value: UUID) -> UUID:
    if value.version != 7:
        raise ValueError("receipt_id must be UUIDv7")
    return value


class ArchivePreflightReceipt(BaseModel):
    model_config = STRICT

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["ArchivePreflightReceipt"] = "ArchivePreflightReceipt"
    receipt_id: UUID
    generated_at: datetime
    requested_volume_name: str = Field(min_length=1)
    readiness: ArchiveReadiness
    reasons: tuple[str, ...]
    candidate_count: int = Field(ge=0)
    candidate: ArchiveCandidate | None

    _receipt_id_is_uuid7 = field_validator("receipt_id")(_uuid7)

    @model_validator(mode="after")
    def state_is_consistent(self) -> Self:
        if self.candidate is not None:
            expected = evaluate_archive_candidate(self.candidate)
            if self.candidate_count != 1 or (self.readiness, self.reasons) != expected:
                raise ValueError("candidate receipt does not match evaluated readiness")
            return self
        global_states = {
            ArchiveReadiness.VOLUME_NOT_FOUND: (0, ("NO_EXACT_NAME_MATCH",)),
            ArchiveReadiness.UNSUPPORTED_HOST: (0, ("DARWIN_REQUIRED",)),
            ArchiveReadiness.INSPECTION_FAILED: (0, ("INSPECTION_TOOL_FAILURE",)),
            ArchiveReadiness.IDENTITY_INCOMPLETE: (1, ("DEVICE_ID_NOT_PROVEN",)),
        }
        valid = (self.candidate_count, self.reasons) == global_states.get(self.readiness)
        if self.readiness == ArchiveReadiness.AMBIGUOUS_VOLUME:
            valid = self.candidate_count >= 2 and self.reasons == ("MULTIPLE_EXACT_NAME_MATCHES",)
        if not valid:
            raise ValueError("candidate-less receipt has contradictory state")
        return self


class ArchiveObjectPromotionReceipt(BaseModel):
    model_config = STRICT

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["ArchiveObjectPromotionReceipt"] = "ArchiveObjectPromotionReceipt"
    receipt_id: UUID
    generated_at: datetime
    algorithm: Literal["sha256"] = "sha256"
    object_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    byte_count: int = Field(ge=0)
    disposition: Literal["PUBLISHED", "DEDUPLICATED"]
    object_relative_path: str = Field(pattern=r"^objects/sha256/[0-9a-f]{2}/[0-9a-f]{64}$")
    verified: Literal[True] = True
    fixture_only: Literal[True] = True

    _receipt_id_is_uuid7 = field_validator("receipt_id")(_uuid7)

    @model_validator(mode="after")
    def path_matches_hash(self) -> Self:
        parts = PurePosixPath(self.object_relative_path).parts
        if parts[2] != self.object_sha256[:2] or parts[3] != self.object_sha256:
            raise ValueError("object path does not match object SHA-256")
        return self


class _ProfileEvidence(BaseModel):
    model_config = STRICT

    archive_preflight_receipt_sha256: str = Field(pattern=SHA256_PATTERN)
    post_merge_apfs_snapshot_sha256: str = Field(pattern=SHA256_PATTERN)


class _PublicArchiveRequirements(BaseModel):
    model_config = STRICT

    volume_name: Literal["BSL-Archive"]
    filesystem: Literal["apfs"]
    encrypted: Literal[True]
    external: Literal[True]
    mounted: Literal[True]
    writable: Literal[True]
    thunderbolt_evidenced: Literal[True]
    stable_volume_identity_required: Literal[True]
    stable_physical_identity_required: Literal[True]
    quota_bytes_observed: Literal[650_000_003_072]
    minimum_effective_free_bytes: Literal[21_474_836_480]
    canonical_archive_root: Literal["/Volumes/BSL-Archive/BiblicalScholarLab"]


class _ArchiveProfilePrivacy(BaseModel):
    model_config = STRICT

    stable_volume_identifier_committed: Literal[False]
    stable_physical_identifier_committed: Literal[False]
    mount_device_identifier_committed: Literal[False]
    private_evidence_must_remain_uncommitted: Literal[True]


PROFILE_INVALIDATION_CONDITIONS = (
    "archive volume replacement or recreation",
    "stable volume identity change",
    "stable physical-device identity change",
    "encryption state change",
    "quota change",
    "filesystem change",
    "approved volume-name or canonical-root change",
    "loss of positive Thunderbolt evidence",
    "private evidence hash mismatch",
)


class ApprovedArchiveProfile(BaseModel):
    model_config = STRICT

    schema_version: Literal["1.0"] = "1.0"
    profile_id: Literal["ARCHIVE-PROFILE-BSL-ARCHIVE-v1"]
    status: Literal["APPROVED_CANONICAL_ARCHIVE_TARGET"]
    approved_at: datetime
    approved_by: Literal["Joseph Abbud"]
    profile_evidence: _ProfileEvidence
    public_requirements: _PublicArchiveRequirements
    privacy: _ArchiveProfilePrivacy
    invalidation_conditions: tuple[str, ...]

    @model_validator(mode="after")
    def approved_invariants_hold(self) -> Self:
        if self.approved_at.isoformat() != "2026-08-20T21:10:47-04:00":
            raise ValueError("profile approval time differs from the approved profile")
        if self.profile_evidence.model_dump() != {
            "archive_preflight_receipt_sha256": APPROVED_PREFLIGHT_SHA256,
            "post_merge_apfs_snapshot_sha256": APPROVED_APFS_SHA256,
        }:
            raise ValueError("profile evidence hashes differ from approval")
        if self.invalidation_conditions != PROFILE_INVALIDATION_CONDITIONS:
            raise ValueError("profile invalidation conditions differ from approval")
        return self


def _uuid7_value(value: UUID) -> UUID:
    if value.version != 7:
        raise ValueError("value must be UUIDv7")
    return value


def _aware_time(value: datetime) -> datetime:
    if value.utcoffset() is None:
        raise ValueError("time must include an offset")
    return value


class ArchiveRootMarker(BaseModel):
    model_config = STRICT

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["ArchiveRootMarker"] = "ArchiveRootMarker"
    archive_id: UUID
    created_at: datetime
    layout_revision: Literal[1] = 1
    profile_id: Literal["ARCHIVE-PROFILE-BSL-ARCHIVE-v1"]
    profile_file_sha256: str = Field(pattern=SHA256_PATTERN)
    archive_preflight_receipt_sha256: str = Field(pattern=SHA256_PATTERN)
    post_merge_apfs_snapshot_sha256: str = Field(pattern=SHA256_PATTERN)
    canonical_archive_root: Literal["/Volumes/BSL-Archive/BiblicalScholarLab"]
    volume_name: Literal["BSL-Archive"]
    stable_volume_identifier: str = Field(min_length=1, max_length=256)
    stable_physical_identifier: str = Field(min_length=1, max_length=256)
    stable_physical_identifier_kind: StablePhysicalDeviceIdKind
    canary_sha256: Literal["faeb22898dfceb94a94874b336f75be3d084f03f8fce2b24b8bf077134a9407b"]
    canary_relative_path: Literal["objects/sha256/fa/faeb22898dfceb94a94874b336f75be3d084f03f8fce2b24b8bf077134a9407b"]
    initialization_receipt_relative_path: str = Field(pattern=r"^registry/archive-initialization/[0-9a-f-]{36}\.json$")

    _archive_id_is_uuid7 = field_validator("archive_id")(_uuid7_value)
    _created_at_has_offset = field_validator("created_at")(_aware_time)

    @model_validator(mode="after")
    def marker_bindings_are_consistent(self) -> Self:
        expected_receipt = f"registry/archive-initialization/{self.archive_id}.json"
        if self.profile_file_sha256 != APPROVED_PROFILE_SHA256:
            raise ValueError("marker profile hash differs from approval")
        if (self.archive_preflight_receipt_sha256, self.post_merge_apfs_snapshot_sha256) != (
            APPROVED_PREFLIGHT_SHA256,
            APPROVED_APFS_SHA256,
        ):
            raise ValueError("marker evidence hashes differ from approval")
        if self.initialization_receipt_relative_path != expected_receipt:
            raise ValueError("initialization receipt path does not match archive ID")
        if self.stable_volume_identifier == self.stable_physical_identifier:
            raise ValueError("volume and physical identities must be distinct")
        return self


class ArchiveInitializationReceipt(BaseModel):
    model_config = STRICT

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["ArchiveInitializationReceipt"] = "ArchiveInitializationReceipt"
    operation_id: UUID
    archive_id: UUID
    generated_at: datetime
    disposition: Literal["INITIALIZED", "VERIFIED_EXISTING"]
    profile_id: Literal["ARCHIVE-PROFILE-BSL-ARCHIVE-v1"]
    profile_file_sha256: str = Field(pattern=SHA256_PATTERN)
    canonical_archive_root: Literal["/Volumes/BSL-Archive/BiblicalScholarLab"]
    marker_relative_path: Literal[".bsl-archive-root.json"]
    marker_sha256: str = Field(pattern=SHA256_PATTERN)
    canary_relative_path: Literal["objects/sha256/fa/faeb22898dfceb94a94874b336f75be3d084f03f8fce2b24b8bf077134a9407b"]
    canary_sha256: Literal["faeb22898dfceb94a94874b336f75be3d084f03f8fce2b24b8bf077134a9407b"]
    initialization_receipt_relative_path: str = Field(pattern=r"^registry/archive-initialization/[0-9a-f-]{36}\.json$")
    verified: Literal[True] = True

    _ids_are_uuid7 = field_validator("operation_id", "archive_id")(_uuid7_value)
    _generated_at_has_offset = field_validator("generated_at")(_aware_time)

    @model_validator(mode="after")
    def receipt_bindings_are_consistent(self) -> Self:
        expected_receipt = f"registry/archive-initialization/{self.archive_id}.json"
        if self.profile_file_sha256 != APPROVED_PROFILE_SHA256:
            raise ValueError("receipt profile hash differs from approval")
        if self.initialization_receipt_relative_path != expected_receipt:
            raise ValueError("initialization receipt path does not match archive ID")
        initialized = self.disposition == "INITIALIZED"
        if initialized != (self.operation_id == self.archive_id):
            raise ValueError("only the persisted initialization receipt reuses the archive ID")
        return self
