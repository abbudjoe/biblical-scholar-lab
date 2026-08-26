from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import MappingProxyType
from typing import Annotated, Any, Literal, Self, cast

import rfc8785
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, PlainSerializer, model_validator

from bsl.contracts import runtime_screening

Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
ROOT = Path(__file__).parents[3]
FIXTURE_PATH = ROOT / "fixtures/VS01-T09/john-1-5-study-workspace-projection.json"
EXPECTED_WORKSPACE_IDENTITY = "9f9f9dd44384d90da5b3918e96ad3623e1235016f6283d224259cba9b670816d"


def _freeze_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        mapping = cast(Mapping[str, Any], value)
        return MappingProxyType({key: _freeze_json(item) for key, item in mapping.items()})
    if isinstance(value, (list, tuple)):
        sequence = cast(list[Any] | tuple[Any, ...], value)
        return tuple(_freeze_json(item) for item in sequence)
    return value


def _thaw_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        mapping = cast(Mapping[str, Any], value)
        return {key: _thaw_json(item) for key, item in mapping.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in cast(tuple[Any, ...], value)]
    return value


ImmutableJsonObject = Annotated[
    Mapping[str, Any], AfterValidator(_freeze_json), PlainSerializer(_thaw_json, return_type=dict)
]


def _projection_schema(schema: dict[str, Any]) -> None:
    data = FIXTURE_PATH.read_bytes()
    projection = json.loads(data)
    if data != rfc8785.dumps(projection) + b"\n" or projection.get("workspace_identity") != EXPECTED_WORKSPACE_IDENTITY:
        raise ValueError("committed workspace projection fixture differs")
    schema.clear()
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["title"] = "VS01StudyWorkspaceProjection"
    schema["additionalProperties"] = False
    schema["const"] = projection


class VS01StudyWorkspaceProjection(BaseModel):
    model_config = ConfigDict(
        strict=True, frozen=True, extra="forbid", allow_inf_nan=False, json_schema_extra=_projection_schema
    )

    schema_version: Literal["1.0"]
    contract: Literal["VS01StudyWorkspaceProjection"]
    workspace_id: Literal["VS01-JOHN-1-5-STUDY-WORKSPACE"]
    workspace_identity: Sha256
    route: Literal["DETERMINISTIC_LOCAL_ONLY"]
    answer_mode: Literal["STUDY"]
    active_context: ImmutableJsonObject
    question: Literal[
        "You have only the supplied ASV and WEB Classic wording for John 1:5. Does the Greek mean both "
        "“understand” and “overcome,” and is a textual variant involved?"
    ]
    translations: tuple[ImmutableJsonObject, ImmutableJsonObject]
    greek: ImmutableJsonObject
    study_blocks: tuple[runtime_screening.RuntimeAnswerBlock, ...]
    evidence_records: tuple[runtime_screening.RuntimeEvidenceRecord, ...]
    claim_records: tuple[runtime_screening.RuntimeClaimRecord, ...]
    citation_records: tuple[runtime_screening.RuntimeCitationRecord, ...]
    evidence_inspector: tuple[ImmutableJsonObject, ...]
    accepted_alternative_ids: tuple[str, str, str]
    material_unknown_claim_ids: tuple[str, str]
    evidence_horizon: tuple[str, str, str, str, str]
    page_study: ImmutableJsonObject
    audit_bindings: ImmutableJsonObject
    operation_disclosure: ImmutableJsonObject

    @model_validator(mode="after")
    def exact_identity_and_links(self) -> Self:
        payload = self.model_dump(mode="json", exclude={"workspace_identity"})
        identity = hashlib.sha256(rfc8785.dumps(payload)).hexdigest()
        page_variants, page_regions = self.page_study.get("variants"), self.page_study.get("regions")
        if not isinstance(page_variants, Sequence) or not isinstance(page_regions, Sequence):
            raise ValueError("workspace page projection shape differs")
        page_variants, page_regions = cast(Sequence[Any], page_variants), cast(Sequence[Any], page_regions)
        evidence = {item.evidence_id for item in self.evidence_records}
        claims = {item.claim_id for item in self.claim_records}
        citations = {item.citation_id for item in self.citation_records}
        inspectors = {cast(str, item.get("citation_id")): item for item in self.evidence_inspector}
        links = all(set(item.evidence_ids) <= evidence for item in self.claim_records) and all(
            item.evidence_id in evidence for item in self.citation_records
        )
        links = links and all(
            set(block.claim_ids) <= claims and set(block.citation_ids) <= citations for block in self.study_blocks
        )
        links = links and inspectors.keys() == citations
        counts = (
            len(self.translations),
            len(self.study_blocks),
            len(self.evidence_records),
            len(self.claim_records),
            len(self.citation_records),
            len(self.evidence_inspector),
            len(self.accepted_alternative_ids),
            len(self.material_unknown_claim_ids),
            len(page_variants),
            len(page_regions),
        )
        if self.workspace_identity != identity or identity != EXPECTED_WORKSPACE_IDENTITY:
            raise ValueError("workspace projection differs from the frozen identity")
        if counts != (2, 7, 12, 15, 10, 10, 3, 2, 2, 7) or not links:
            raise ValueError("workspace projection counts or links differ")
        return self
