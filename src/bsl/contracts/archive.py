from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

STRICT = ConfigDict(strict=True, frozen=True, extra="forbid", allow_inf_nan=False)


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


class ArchiveCandidate(BaseModel):
    model_config = STRICT

    filesystem: str | None
    encrypted: bool | None
    internal: bool | None
    mounted: bool
    read_only: bool | None
    volume_uuid: str | None
    parent_physical_device: str | None
    free_bytes: int | None = Field(ge=0)
    thunderbolt_evidenced: bool


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
