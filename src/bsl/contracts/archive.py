from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

STRICT = ConfigDict(strict=True, frozen=True, extra="forbid", allow_inf_nan=False)
MINIMUM_FREE_BYTES = 20 * 1024**3


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
