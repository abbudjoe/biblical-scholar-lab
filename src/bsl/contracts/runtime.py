from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, Literal, Self
from uuid import UUID

import rfc8785
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
CommitSha = Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
SPEC_SHA256 = "06e97f36db1071d9085688ceb33dbc66f02dd0349889ab4df4d0fa280801d9e5"
PACKET_IDENTITY = "aebcbb50fc8383f2f4f395bc71116563325c1fde237427dc8c1bc8140e8ebe31"
PACKET_SHA256 = "9f81621785924161cc4861e2af9f010bd18e822b60199d62a6327eff44ea0409"
PACKET_RECEIPT_IDENTITY = "01a02bbe-bda5-776b-a95e-16bb40d18597"
PACKET_RECEIPT_SHA256 = "02272e1ec458a33e449aa93f9508a57d4eaacf3d9dccc48888f3952bbe96dad4"
ACTIVE_REQUEST_IDENTITY = "5b0d413278c3dcf03421989dcec84228a828d13236a232977b448b14bd0b68ef"
RUNTIME_SPEC_PATH = Path(__file__).parents[3] / "design/approved/VS01-T05-runtime-spec.json"


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(rfc8785.dumps(value)).hexdigest()


def load_runtime_spec(path: Path = RUNTIME_SPEC_PATH) -> dict[str, Any]:
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != SPEC_SHA256:
        raise ValueError("frozen VS01-T05 runtime specification hash differs")
    try:
        spec = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("frozen VS01-T05 runtime specification is invalid JSON") from None
    counts = (len(spec.get("evidence_ledger", ())), len(spec.get("claim_ledger", ())))
    exact = (
        spec.get("spec_id") == "VS01-T05-RUNTIME-SPEC-v1",
        counts == (12, 16),
        len(spec.get("citation_records", ())) == 10,
        len(spec.get("verification_rules", ())) == 12,
    )
    if not all(exact):
        raise ValueError("frozen VS01-T05 runtime specification structure differs")
    return spec


def _request_payload(revision: int) -> dict[str, Any]:
    spec = load_runtime_spec()["canonical_request"]
    key = "initial_request" if revision == 1 else "active_request"
    return dict(spec[key])


def _execution_payload() -> dict[str, Any]:
    spec = load_runtime_spec()
    value = {
        "schema_version": "1.0",
        "contract": "John15StudyExecutionRecord",
        "request_identity": ACTIVE_REQUEST_IDENTITY,
        "packet_identity": PACKET_IDENTITY,
        "packet_canonical_sha256": PACKET_SHA256,
        "packet_receipt_identity": PACKET_RECEIPT_IDENTITY,
        "packet_receipt_file_sha256": PACKET_RECEIPT_SHA256,
        "runtime_spec_sha256": SPEC_SHA256,
        "resolved_task": spec["resolved_task"],
        "research_execution_plan": spec["research_execution_plan"],
        "runtime_state_sequence": spec["runtime_state_machine"]["principal_sequence"],
        "skipped_state_reasons": spec["runtime_state_machine"]["skip_reasons"],
        "evidence_ledger": spec["evidence_ledger"],
        "claim_ledger": spec["claim_ledger"],
        "citation_ledger": spec["citation_records"],
        "structured_answer_candidate": spec["structured_answer_candidate"],
        "verification_rules": spec["verification_rules"],
        "verification_report": spec["verification_report"],
        "brief_study_consistency_result": spec["answer_artifacts"]["consistency_rule"],
        "executor_kind": "DETERMINISTIC_REFERENCE",
    }
    return value | {"execution_record_identity": canonical_sha256(value)}


def _answer_payload(mode: Literal["BRIEF", "STUDY"]) -> dict[str, Any]:
    artifact = load_runtime_spec()["answer_artifacts"][mode.lower()]
    citation_ids = {citation for block in artifact["blocks"] for citation in block["citation_ids"]}
    citations = [item for item in load_runtime_spec()["citation_records"] if item["citation_id"] in citation_ids]
    value = {
        "schema_version": "1.0",
        "contract": "John15StudyAnswerArtifact",
        "request_identity": ACTIVE_REQUEST_IDENTITY,
        "execution_record_identity": _execution_payload()["execution_record_identity"],
        "packet_identity": PACKET_IDENTITY,
        "packet_canonical_sha256": PACKET_SHA256,
        "packet_receipt_identity": PACKET_RECEIPT_IDENTITY,
        "packet_receipt_file_sha256": PACKET_RECEIPT_SHA256,
        **artifact,
        "citation_records": citations,
    }
    return value | {"answer_identity": canonical_sha256(value)}


def _request_schema(schema: dict[str, Any]) -> None:
    schema.clear()
    schema.update(
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "oneOf": [{"const": _request_payload(1)}, {"const": _request_payload(2)}],
            "title": "John15StudyRequest",
        }
    )


def _execution_schema(schema: dict[str, Any]) -> None:
    schema.clear()
    schema.update(
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "const": _execution_payload(),
            "title": "John15StudyExecutionRecord",
        }
    )


def _answer_schema(schema: dict[str, Any]) -> None:
    schema.clear()
    schema.update(
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "oneOf": [{"const": _answer_payload("BRIEF")}, {"const": _answer_payload("STUDY")}],
            "title": "John15StudyAnswerArtifact",
        }
    )


def _audit_schema(schema: dict[str, Any]) -> None:
    properties = schema["properties"]
    constants = {
        "packet_receipt_identity": PACKET_RECEIPT_IDENTITY,
        "execution_record_identity": _execution_payload()["execution_record_identity"],
        "brief_answer_identity": _answer_payload("BRIEF")["answer_identity"],
        "brief_answer_sha256": canonical_sha256(_answer_payload("BRIEF")),
        "study_answer_identity": _answer_payload("STUDY")["answer_identity"],
        "study_answer_sha256": canonical_sha256(_answer_payload("STUDY")),
        "verification_rule_ids": [item["rule_id"] for item in load_runtime_spec()["verification_rules"]],
    }
    for field, value in constants.items():
        properties[field] = {"const": value}
    count_shapes = (
        {"study_run": 0, "runtime_artifact": 0, "runtime_event": 0},
        {"study_run": 1, "runtime_artifact": 5, "runtime_event": 11},
    )
    for field in ("database_rows_written", "database_rows_verified"):
        properties[field] = {"oneOf": [{"const": value} for value in count_shapes]}
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"


class John15StudyRequest(BaseModel):
    model_config = ConfigDict(
        strict=True, frozen=True, extra="forbid", allow_inf_nan=False, json_schema_extra=_request_schema
    )

    request_revision: Literal[1, 2]
    exact_user_text: str
    passage: str
    primary_edition: str
    comparison_edition: str
    requested_answer_depth: str
    answer_language: str
    supersedes_request_identity: Sha256 | None = None
    correction_identity: Sha256 | None = None
    request_identity: Sha256

    @model_validator(mode="after")
    def exact_revision_and_identity(self) -> Self:
        actual = self.model_dump(mode="json", exclude_none=True)
        if actual != _request_payload(self.request_revision):
            raise ValueError("study request differs from the frozen request revision")
        del actual["request_identity"]
        if self.request_identity != canonical_sha256(actual):
            raise ValueError("request identity differs from canonical semantic fields")
        return self


class John15StudyExecutionRecord(BaseModel):
    model_config = ConfigDict(
        strict=True, frozen=True, extra="forbid", allow_inf_nan=False, json_schema_extra=_execution_schema
    )

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["John15StudyExecutionRecord"] = "John15StudyExecutionRecord"
    request_identity: Sha256
    packet_identity: Sha256
    packet_canonical_sha256: Sha256
    packet_receipt_identity: UUID
    packet_receipt_file_sha256: Sha256
    runtime_spec_sha256: Sha256
    resolved_task: dict[str, Any]
    research_execution_plan: dict[str, Any]
    runtime_state_sequence: tuple[str, ...]
    skipped_state_reasons: dict[str, str]
    evidence_ledger: tuple[dict[str, Any], ...]
    claim_ledger: tuple[dict[str, Any], ...]
    citation_ledger: tuple[dict[str, Any], ...]
    structured_answer_candidate: dict[str, Any]
    verification_rules: tuple[dict[str, Any], ...]
    verification_report: dict[str, Any]
    brief_study_consistency_result: str
    executor_kind: Literal["DETERMINISTIC_REFERENCE"]
    execution_record_identity: Sha256

    @model_validator(mode="after")
    def exact_execution(self) -> Self:
        actual = self.model_dump(mode="json")
        if actual != _execution_payload():
            raise ValueError("execution record differs from the frozen verified record")
        identity = actual.pop("execution_record_identity")
        if identity != canonical_sha256(actual):
            raise ValueError("execution record identity differs")
        return self


class John15StudyAnswerArtifact(BaseModel):
    model_config = ConfigDict(
        strict=True, frozen=True, extra="forbid", allow_inf_nan=False, json_schema_extra=_answer_schema
    )

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["John15StudyAnswerArtifact"] = "John15StudyAnswerArtifact"
    request_identity: Sha256
    execution_record_identity: Sha256
    packet_identity: Sha256
    packet_canonical_sha256: Sha256
    packet_receipt_identity: UUID
    packet_receipt_file_sha256: Sha256
    rendering_mode: Literal["BRIEF", "STUDY"]
    language: Literal["en"]
    primary_edition: str
    comparison_edition: str
    blocks: tuple[dict[str, Any], ...]
    markdown: str
    visible_claim_ids: tuple[str, ...]
    material_uncertainty_claim_ids: tuple[str, ...]
    alternative_ids: tuple[str, ...]
    citation_records: tuple[dict[str, Any], ...]
    answer_identity: Sha256

    @model_validator(mode="after")
    def exact_answer(self) -> Self:
        actual = self.model_dump(mode="json")
        if actual != _answer_payload(self.rendering_mode):
            raise ValueError("answer artifact differs from the frozen rendering")
        identity = actual.pop("answer_identity")
        if identity != canonical_sha256(actual):
            raise ValueError("answer artifact identity differs")
        return self


class John15RuntimeAuditReceipt(BaseModel):
    model_config = ConfigDict(
        strict=True, frozen=True, extra="forbid", allow_inf_nan=False, json_schema_extra=_audit_schema
    )

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["John15RuntimeAuditReceipt"] = "John15RuntimeAuditReceipt"
    receipt_identity: UUID
    generated_at: datetime
    implementation_commit: CommitSha
    runtime_spec_sha256: Literal["06e97f36db1071d9085688ceb33dbc66f02dd0349889ab4df4d0fa280801d9e5"]
    request_identity: Literal["5b0d413278c3dcf03421989dcec84228a828d13236a232977b448b14bd0b68ef"]
    correction_identity: Literal["bfd475b96f4e0296396b6e3771767194b9210e841643bc66ab3657e995d0d97d"]
    supersedes_request_identity: Literal["782f577a42001df95b1f2094b7c44a075102bd3c54ee157e809828853352ec80"]
    packet_identity: Literal["aebcbb50fc8383f2f4f395bc71116563325c1fde237427dc8c1bc8140e8ebe31"]
    packet_canonical_sha256: Literal["9f81621785924161cc4861e2af9f010bd18e822b60199d62a6327eff44ea0409"]
    packet_receipt_identity: UUID
    packet_receipt_file_sha256: Literal["02272e1ec458a33e449aa93f9508a57d4eaacf3d9dccc48888f3952bbe96dad4"]
    plan_id: Literal["PLAN-VS01-T05-JOHN-1-5-ASV-WEB-v1"]
    execution_record_identity: Sha256
    brief_answer_identity: Sha256
    brief_answer_sha256: Sha256
    study_answer_identity: Sha256
    study_answer_sha256: Sha256
    verification_outcome: Literal["VERIFIED_WITH_QUALIFICATION"]
    verification_rule_ids: tuple[str, ...]
    disposition: Literal["DRY_RUN_VALIDATED", "PERSISTED", "VERIFIED_EXISTING"]
    persisted: bool
    verified_existing: bool
    database_schema_revision: Literal["0001_vs01_t05_runtime"] | None
    run_id: UUID | None
    session_id: UUID | None
    executor_kind: Literal["DETERMINISTIC_REFERENCE"]
    model_route: Literal["NONE"]
    model_invocations: Literal[0]
    network_requests: Literal[0]
    packet_loads: Literal[1]
    repair_attempts: Literal[0]
    archive_writes: Literal[0]
    database_connections: Literal[0, 1]
    database_rows_written: dict[str, int]
    database_rows_verified: dict[str, int]
    terminal_state: Literal["COMPLETE"]
    latency_ms: int = Field(ge=0)
    actual_cost_usd: float = Field(ge=0.0, le=0.0)
    private_chain_of_thought: Literal["NOT_COLLECTED_OR_STORED"]
    receipt_canonical_sha256: Sha256

    @field_validator("receipt_identity")
    @classmethod
    def uuid7_receipt(cls, value: UUID) -> UUID:
        if value.version != 7:
            raise ValueError("audit receipt identity must be UUIDv7")
        return value

    @field_validator("generated_at")
    @classmethod
    def aware_timestamp(cls, value: datetime) -> datetime:
        if value.utcoffset() is None:
            raise ValueError("audit generated_at must include an offset")
        return value

    @model_validator(mode="after")
    def exact_audit(self) -> Self:
        spec = load_runtime_spec()
        expected_rules = tuple(item["rule_id"] for item in spec["verification_rules"])
        bindings = (
            str(self.packet_receipt_identity) == PACKET_RECEIPT_IDENTITY,
            self.execution_record_identity == _execution_payload()["execution_record_identity"],
            self.brief_answer_identity == _answer_payload("BRIEF")["answer_identity"],
            self.brief_answer_sha256 == canonical_sha256(_answer_payload("BRIEF")),
            self.study_answer_identity == _answer_payload("STUDY")["answer_identity"],
            self.study_answer_sha256 == canonical_sha256(_answer_payload("STUDY")),
            self.verification_rule_ids == expected_rules,
        )
        if not all(bindings):
            raise ValueError("audit receipt deterministic bindings differ")
        state = (self.persisted, self.verified_existing, self.database_connections)
        expected_state = {
            "DRY_RUN_VALIDATED": (False, False, 0),
            "PERSISTED": (True, False, 1),
            "VERIFIED_EXISTING": (False, True, 1),
        }[self.disposition]
        if state != expected_state:
            raise ValueError("audit persistence state contradicts disposition")
        zero = {"study_run": 0, "runtime_artifact": 0, "runtime_event": 0}
        counts = {"study_run": 1, "runtime_artifact": 5, "runtime_event": 11}
        expected_rows = {
            "DRY_RUN_VALIDATED": (zero, zero),
            "PERSISTED": (counts, zero),
            "VERIFIED_EXISTING": (zero, counts),
        }[self.disposition]
        if (self.database_rows_written, self.database_rows_verified) != expected_rows:
            raise ValueError("audit database row counts contradict disposition")
        database_ids = (self.database_schema_revision, self.run_id, self.session_id)
        if (self.disposition == "DRY_RUN_VALIDATED") != (database_ids == (None, None, None)):
            raise ValueError("audit database identities contradict disposition")
        actual = self.model_dump(mode="json", exclude={"receipt_canonical_sha256"})
        if self.receipt_canonical_sha256 != canonical_sha256(actual):
            raise ValueError("audit receipt canonical SHA-256 differs")
        return self
