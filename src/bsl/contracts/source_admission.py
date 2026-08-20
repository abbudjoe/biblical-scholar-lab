from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Literal, Self
from uuid import UUID

import rfc8785
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

STRICT = ConfigDict(strict=True, frozen=True, extra="forbid", allow_inf_nan=False, validate_by_name=True)
APPROVED_SOURCE_IDS = tuple(f"SP01-SRC-00{index}" for index in range(1, 7))
HARD_PROHIBITIONS = (
    "no training",
    "no embeddings or vector indexes",
    "no Lambda or other cloud execution",
    "no automatic source updates",
    "no mixed-rights MACULA ingestion",
    "no apparatus",
    "no copyrighted modern translation or study Bible page",
    "no user-private source",
    "no model-generated source evidence",
)


class PlannedSource(BaseModel):
    model_config = STRICT

    source_id: str = Field(pattern=r"^SP01-SRC-00[1-6]$")
    name: str
    provider: str | None = None
    transport_class: str = Field(validation_alias="source_type")
    repository: str | None = None
    package: str | None = None
    source_page: str | None = None
    revision: str
    tag: str | None = None
    doi: str | None = None
    trademark: str | None = None
    admitted_components: tuple[str, ...] = Field(validation_alias="components")
    admitted_fields: tuple[str, ...] = ()
    excluded_components: tuple[str, ...] = ()
    excluded_fields: tuple[str, ...] = ()
    normalized_scope: tuple[str, ...]
    license: str
    rights_lineage: str = Field(validation_alias="lineage")
    disposition: str
    relative_quarantine_plan: str
    planned_manifest_identity: str = Field(pattern=r"^[0-9a-f]{64}$")
    pre_acquisition_stop_conditions: tuple[str, ...]


class SourcePlanSemanticPayload(BaseModel):
    model_config = STRICT

    artifact_id: Literal["SOURCE-PLAN-01"]
    status: Literal["APPROVED"]
    vertical_slice: Literal["VS-01"]
    design_baseline_commit: str = Field(pattern=r"^[0-9a-f]{40}$")
    manifest_identity: str = Field(pattern=r"^[0-9a-f]{64}$")
    training_authorized: Literal[False]
    embedding_authorized: Literal[False]
    cloud_execution_authorized: Literal[False]
    source_acquisition_authorized_now: Literal[False]
    sources: tuple[PlannedSource, ...] = Field(min_length=6, max_length=6)
    hard_prohibitions: tuple[str, ...]

    @model_validator(mode="after")
    def exact_source_plan(self) -> Self:
        if tuple(source.source_id for source in self.sources) != APPROVED_SOURCE_IDS:
            raise ValueError("sources must match the exact approved order")
        if self.hard_prohibitions != HARD_PROHIBITIONS:
            raise ValueError("hard prohibitions must match SOURCE-PLAN-01 exactly")
        wrong_identity = any(source.planned_manifest_identity != self.manifest_identity for source in self.sources)
        if wrong_identity:
            raise ValueError("planned source identity does not match manifest identity")
        wrong_path = any(
            source.relative_quarantine_plan != f"quarantine/SOURCE-PLAN-01/{source.source_id}"
            for source in self.sources
        )
        if wrong_path:
            raise ValueError("planned quarantine path is not exact")
        return self


def _uuid7(value: UUID) -> UUID:
    if value.version != 7:
        raise ValueError("receipt_id must be UUIDv7")
    return value


class SourceAcquisitionDryRun(BaseModel):
    model_config = STRICT

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["SourceAcquisitionDryRun"] = "SourceAcquisitionDryRun"
    receipt_id: UUID
    generated_at: datetime
    semantic_payload: SourcePlanSemanticPayload
    semantic_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    _receipt_id_is_uuid7 = field_validator("receipt_id")(_uuid7)

    @model_validator(mode="after")
    def semantic_hash_matches_payload(self) -> Self:
        canonical = rfc8785.dumps(self.semantic_payload.model_dump(mode="json"))
        if hashlib.sha256(canonical).hexdigest() != self.semantic_sha256:
            raise ValueError("semantic SHA-256 does not match semantic payload")
        return self
