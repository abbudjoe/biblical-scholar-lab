from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Annotated, Any, Literal, Self
from uuid import UUID

import rfc8785
from pydantic import BaseModel, ConfigDict, Field, model_validator

Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
CommitSha = Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
HashBinding = tuple[str, Sha256]
ResponseField = tuple[str, str]
CriterionScore = tuple[str, int, int, int]
DeterministicCheck = tuple[str, str, bool]
HardFailure = tuple[str, str, str]
CountBinding = tuple[str, int]


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(rfc8785.dumps(value)).hexdigest()


def _strict_schema(schema: dict[str, Any]) -> None:
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"


class VS01BenchmarkExecutionSpecification(BaseModel):
    model_config = ConfigDict(
        strict=True, frozen=True, extra="forbid", allow_inf_nan=False, json_schema_extra=_strict_schema
    )

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["VS01BenchmarkExecutionSpecification"] = "VS01BenchmarkExecutionSpecification"
    batch_id: Literal["BENCH-VS01-BATCH-01"] = "BENCH-VS01-BATCH-01"
    batch_markdown_sha256: Sha256
    batch_cases_sha256: Sha256
    r01_design_sha256: Sha256
    r01_protocol_sha256: Sha256
    erratum_markdown_sha256: Sha256
    erratum_json_sha256: Sha256
    source_declared_compatibility_hashes: tuple[HashBinding, ...]
    execution_rfc8785_jcs_hashes: tuple[HashBinding, ...]
    case_order: tuple[str, ...]
    subject_projection_identities: tuple[HashBinding, ...]
    subject_id: Literal["VS01-T07-REFERENCE-SUBJECT-v1"] = "VS01-T07-REFERENCE-SUBJECT-v1"
    engine_revision: Literal["VS01-T07-REFERENCE-ENGINE-v1"] = "VS01-T07-REFERENCE-ENGINE-v1"
    scorer_revision: Literal["VS01-T07-REFERENCE-CONFORMANCE-SCORER-v1"]
    scorer_scope: Literal["REFERENCE_CONFORMANCE_ONLY"] = "REFERENCE_CONFORMANCE_ONLY"
    attempts_per_case: Literal[1] = 1
    automatic_retries: Literal[0] = 0
    semantic_rerolls: Literal[0] = 0
    upstream_authority: tuple[tuple[str, str], ...]
    isolation_policy: tuple[str, ...]
    leakage_policy: Literal["INVALID_LEAKAGE_INCIDENT"] = "INVALID_LEAKAGE_INCIDENT"
    p0_maximum_points: Literal[64] = 64
    p1_maximum_points: Literal[56] = 56
    maximum_points: Literal[120] = 120
    screening_case_minimums: tuple[tuple[str, int], ...]
    screening_partition_minimums: tuple[tuple[str, int], ...]
    b08_full_runtime_limitation: Literal["VS01-B08-RUNTIME-C01_REQUIRED_NOT_AUTHORED"]
    execution_mode: Literal["REFERENCE_CONFORMANCE", "REFERENCE_CONFORMANCE_DRY_RUN"]
    specification_identity: Sha256

    @model_validator(mode="after")
    def exact_identity_and_inventory(self) -> Self:
        payload = self.model_dump(mode="json", exclude={"specification_identity"})
        if self.specification_identity != canonical_sha256(payload):
            raise ValueError("benchmark execution specification identity differs")
        ordered = tuple(case_id for case_id, _digest in self.source_declared_compatibility_hashes)
        compared = tuple(case_id for case_id, _digest in self.execution_rfc8785_jcs_hashes)
        projected = tuple(case_id for case_id, _digest in self.subject_projection_identities)
        if len(self.case_order) != 12 or ordered != self.case_order or compared != ordered or projected != ordered:
            raise ValueError("benchmark execution specification case inventory differs")
        if len(set(self.case_order)) != 12 or len(self.screening_case_minimums) != 12:
            raise ValueError("benchmark execution specification contains duplicate or missing cases")
        return self


class VS01BenchmarkCaseResult(BaseModel):
    model_config = ConfigDict(
        strict=True, frozen=True, extra="forbid", allow_inf_nan=False, json_schema_extra=_strict_schema
    )

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["VS01BenchmarkCaseResult"] = "VS01BenchmarkCaseResult"
    case_id: str
    source_declared_compatibility_sha256: Sha256
    execution_rfc8785_jcs_sha256: Sha256
    subject_package_identity: Sha256
    response_identity: Sha256
    response_payload: tuple[ResponseField, ...]
    attempt_number: Literal[1] = 1
    attempt_state: Literal["COMPLETED", "ERROR", "REFUSAL", "TIMEOUT", "MALFORMED", "INVALID_LEAKAGE_INCIDENT"]
    criterion_scores: tuple[CriterionScore, ...]
    deterministic_checks: tuple[DeterministicCheck, ...]
    hard_failures: tuple[HardFailure, ...]
    raw_points: int = Field(ge=0)
    capped_points: int = Field(ge=0)
    case_disposition: Literal[
        "REFERENCE_CONFORMANT",
        "REFERENCE_NONCONFORMANT_REPAIR_REQUIRED",
        "UNSUPPORTED_SUBJECT_FOR_REFERENCE_SCORER",
        "INVALID_LEAKAGE_INCIDENT",
    ]
    leakage_state: Literal["CLEAR", "INVALID_LEAKAGE_INCIDENT"]
    error: bool
    refusal: bool
    timeout: bool
    malformed: bool
    evidence_references: tuple[str, ...]
    case_result_identity: Sha256

    @model_validator(mode="after")
    def exact_identity_and_points(self) -> Self:
        payload = self.model_dump(mode="json", exclude={"case_result_identity"})
        if self.case_result_identity != canonical_sha256(payload):
            raise ValueError("benchmark case-result identity differs")
        if any(
            score not in (0, 1, 2) or weight < 1 or points != score * weight
            for _, score, weight, points in self.criterion_scores
        ):
            raise ValueError("benchmark criterion arithmetic differs")
        if self.raw_points != sum(item[3] for item in self.criterion_scores) or self.capped_points > self.raw_points:
            raise ValueError("benchmark case-point arithmetic differs")
        states = (self.error, self.refusal, self.timeout, self.malformed)
        expected = tuple(self.attempt_state == name for name in ("ERROR", "REFUSAL", "TIMEOUT", "MALFORMED"))
        if states != expected:
            raise ValueError("benchmark attempt-state accounting differs")
        if (self.leakage_state == "INVALID_LEAKAGE_INCIDENT") != (self.case_disposition == "INVALID_LEAKAGE_INCIDENT"):
            raise ValueError("benchmark leakage disposition differs")
        return self


TwelveCaseResults = tuple[
    VS01BenchmarkCaseResult,
    VS01BenchmarkCaseResult,
    VS01BenchmarkCaseResult,
    VS01BenchmarkCaseResult,
    VS01BenchmarkCaseResult,
    VS01BenchmarkCaseResult,
    VS01BenchmarkCaseResult,
    VS01BenchmarkCaseResult,
    VS01BenchmarkCaseResult,
    VS01BenchmarkCaseResult,
    VS01BenchmarkCaseResult,
    VS01BenchmarkCaseResult,
]


class VS01BenchmarkRunResult(BaseModel):
    model_config = ConfigDict(
        strict=True, frozen=True, extra="forbid", allow_inf_nan=False, json_schema_extra=_strict_schema
    )

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["VS01BenchmarkRunResult"] = "VS01BenchmarkRunResult"
    execution_specification_identity: Sha256
    case_results: TwelveCaseResults
    requested_attempts: Literal[12] = 12
    completed_attempts: int = Field(ge=0, le=12)
    p0_points: int = Field(ge=0, le=64)
    p1_points: int = Field(ge=0, le=56)
    total_points: int = Field(ge=0, le=120)
    failure_counts: tuple[CountBinding, ...]
    hard_failure_counts: tuple[CountBinding, ...]
    special_outcomes: tuple[tuple[str, str], ...]
    contamination_limitation: Literal["CHATGPT_AUTHORED_PUBLIC_SEED"]
    public_seed_limitation: Literal["EL-1_SCREENING_ONLY"]
    b08_runtime_pair_limitation: Literal["VS01-B08-RUNTIME-C01_REQUIRED_NOT_AUTHORED"]
    disposition: Literal["REFERENCE_CONFORMANT", "REFERENCE_NONCONFORMANT_REPAIR_REQUIRED", "SCREENING_NO_GO"]
    model_invocations: Literal[0] = 0
    ocr_invocations: Literal[0] = 0
    vlm_invocations: Literal[0] = 0
    network_invocations: Literal[0] = 0
    database_writes: Literal[0] = 0
    archive_writes: int = Field(ge=0, le=3)
    run_result_identity: Sha256

    @model_validator(mode="after")
    def exact_identity_and_accounting(self) -> Self:
        payload = self.model_dump(mode="json", exclude={"run_result_identity"})
        if self.run_result_identity != canonical_sha256(payload):
            raise ValueError("benchmark run-result identity differs")
        if len({item.case_id for item in self.case_results}) != 12:
            raise ValueError("benchmark run result does not contain twelve unique cases")
        if self.total_points != self.p0_points + self.p1_points:
            raise ValueError("benchmark run partition arithmetic differs")
        if self.total_points != sum(item.capped_points for item in self.case_results):
            raise ValueError("benchmark run case arithmetic differs")
        completed = sum(item.attempt_state == "COMPLETED" for item in self.case_results)
        if self.completed_attempts != completed:
            raise ValueError("benchmark completed-attempt accounting differs")
        return self


class VS01BenchmarkExecutionReceipt(BaseModel):
    model_config = ConfigDict(
        strict=True, frozen=True, extra="forbid", allow_inf_nan=False, json_schema_extra=_strict_schema
    )

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["VS01BenchmarkExecutionReceipt"] = "VS01BenchmarkExecutionReceipt"
    receipt_id: UUID
    generated_at: datetime
    execution_specification_identity: Sha256
    run_result_identity: Sha256
    run_result_file_sha256: Sha256
    implementation_commit: CommitSha
    archive_root: str
    archive_paths: tuple[str, str, str]
    disposition: Literal["DRY_RUN_VALIDATED", "REFERENCE_CONFORMANT", "REFERENCE_NONCONFORMANT"]
    dry_run: bool
    published: bool
    verified_existing: bool
    upstream_fingerprints: tuple[HashBinding, ...]
    requested_attempts: Literal[12] = 12
    completed_attempts: int = Field(ge=0, le=12)
    error_counts: tuple[CountBinding, ...]
    model_invocations: Literal[0] = 0
    ocr_invocations: Literal[0] = 0
    vlm_invocations: Literal[0] = 0
    network_invocations: Literal[0] = 0
    database_writes: Literal[0] = 0
    archive_writes: int = Field(ge=0, le=3)

    @model_validator(mode="after")
    def valid_operational_identity(self) -> Self:
        if self.receipt_id.version != 7:
            raise ValueError("benchmark receipt ID is not UUIDv7")
        if self.generated_at.tzinfo is None or self.generated_at.utcoffset() is None:
            raise ValueError("benchmark receipt timestamp is not offset-aware")
        if self.dry_run and (self.published or self.verified_existing or self.archive_writes):
            raise ValueError("benchmark dry-run receipt claims publication")
        if self.published and self.verified_existing:
            raise ValueError("benchmark receipt cannot be both published and verified-existing")
        return self
