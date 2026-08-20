from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

STRICT = ConfigDict(strict=True, frozen=True, extra="forbid", allow_inf_nan=False)


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


class SourceAcquisitionDryRun(BaseModel):
    model_config = STRICT

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["SourceAcquisitionDryRun"] = "SourceAcquisitionDryRun"
    receipt_id: UUID
    generated_at: datetime
    semantic_payload: SourcePlanSemanticPayload
    semantic_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
