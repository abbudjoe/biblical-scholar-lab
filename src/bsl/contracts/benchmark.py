from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, Literal, Self, cast
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
ROOT = Path(__file__).parents[3]
CASE_IDS = tuple(f"VS01-B{index:02d}-C01" for index in range(1, 13))
CASE_MINIMUMS = (5, 8, 5, 10, 8, 12, 10, 7, 8, 8, 8, 10)
_P0 = "REV-P0_DETERMINISTIC_AND_OPERATIONAL"
_P1 = "REV-P1_SOURCE_VERIFIABLE_SCHOLARLY_BEHAVIOR"
PARTITIONS = (_P0, _P0, _P0, _P1, _P1, _P1, _P0, _P1, _P0, _P0, _P0, _P1)


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(rfc8785.dumps(value)).hexdigest()


def _load(relative: str) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads((ROOT / relative).read_bytes()))


def _checks(case: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    return tuple(
        (
            item["type"],
            json.dumps(
                {key: value for key, value in item.items() if key != "type"},
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
        for item in case.get("deterministic_checks", ())
    )


def _authority() -> dict[str, Any]:
    source = _load("design/approved/BENCH-VS01-BATCH-01-cases.json")
    plans = _load("design/approved/VS01-T07-benchmark-execution-protocol-R01.json")["frozen_batch"]["cases"]
    projections = _load("fixtures/VS01-T07/subject-projection-manifest.json")["cases"]
    fixtures = _load("fixtures/VS01-T07/reference-subject-responses.json")["cases"]
    result: dict[str, Any] = {}
    for case, plan, projection, fixture, partition in zip(
        source["cases"], plans, projections, fixtures, PARTITIONS, strict=True
    ):
        severity = {item["criterion_id"]: item.get("hard_failure_severity", "") for item in plan["criteria"]}
        result[case["case_id"]] = {
            "compatibility": case["case_content_sha256"],
            "jcs": plan["execution_rfc8785_jcs_sha256"],
            "projection": projection["subject_projection_identity"],
            "criteria": tuple((item["criterion_id"], item["weight"]) for item in case["rubric"]),
            "checks": _checks(case),
            "evidence": tuple(case["source_dependencies"]),
            "failures": tuple((name, value) for name, value in severity.items() if value),
            "partition": partition,
            "response_sha": fixture["response_payload_sha256"],
        }
    return result


AUTHORITY = _authority()
COMPATIBILITY_HASHES = tuple((case_id, AUTHORITY[case_id]["compatibility"]) for case_id in CASE_IDS)
JCS_HASHES = tuple((case_id, AUTHORITY[case_id]["jcs"]) for case_id in CASE_IDS)
PROJECTION_IDENTITIES = tuple((case_id, AUTHORITY[case_id]["projection"]) for case_id in CASE_IDS)
UPSTREAM_AUTHORITY = (
    ("t04_packet_identity", "aebcbb50fc8383f2f4f395bc71116563325c1fde237427dc8c1bc8140e8ebe31"),
    ("t04_packet_sha256", "9f81621785924161cc4861e2af9f010bd18e822b60199d62a6327eff44ea0409"),
    ("t04_receipt_id", "01a02bbe-bda5-776b-a95e-16bb40d18597"),
    ("t04_receipt_sha256", "02272e1ec458a33e449aa93f9508a57d4eaacf3d9dccc48888f3952bbe96dad4"),
    ("t05_run_id", "01a030a1-c3ca-76f6-b4c8-f74392e2cd91"),
    ("t05_session_id", "01a030a1-c3cb-72d0-aac0-19da47db369e"),
    ("t06_fixture_identity", "929ddc1c1aeb1e976a70cfbceb238f0ef6a55e8ca1b354a0210463cec50b4d9b"),
    ("t06_base_sha256", "2c0cebc7245eb1032b2b1e4c0ee16e6f74dec47e6a53d8f49c4b9d0a847abbfb"),
    ("t06_degraded_sha256", "cb47073c8e40da01285d90d26ebb7144b34047a2cde8f58e4ba0d1f2cfb67fce"),
    ("t06_fixture_json_sha256", "c8cfc4eafee6b0a16fc2e0442190782a35e2b03477a619854105d5272f08417f"),
    ("t06_receipt_id", "01a034c2-d6e4-73f4-91b2-7410e7453783"),
)
ISOLATION_POLICY = (
    "fresh subprocess per case",
    "case-local state only",
    "one attempt",
    "zero retries",
    "errors remain in denominator",
)


def _array(values: tuple[Any, ...]) -> dict[str, Any]:
    constants: list[dict[str, Any]] = [
        {"const": list(cast(tuple[Any, ...], value)) if isinstance(value, tuple) else value} for value in values
    ]
    return {"type": "array", "prefixItems": constants, "minItems": len(values), "maxItems": len(values)}


def _fixed(*items: dict[str, Any]) -> dict[str, Any]:
    return {"type": "array", "prefixItems": list(items), "minItems": len(items), "maxItems": len(items)}


def _exact_tuple(items: list[dict[str, Any]]) -> dict[str, Any]:
    schema: dict[str, Any] = {"type": "array", "minItems": len(items), "maxItems": len(items)}
    if items:
        schema["prefixItems"] = items
    return schema


def _base_schema(schema: dict[str, Any]) -> None:
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"


def _spec_schema(schema: dict[str, Any]) -> None:
    _base_schema(schema)
    for name, value in (
        ("case_order", CASE_IDS),
        ("source_declared_compatibility_hashes", COMPATIBILITY_HASHES),
        ("execution_rfc8785_jcs_hashes", JCS_HASHES),
        ("subject_projection_identities", PROJECTION_IDENTITIES),
        ("screening_case_minimums", tuple(zip(CASE_IDS, CASE_MINIMUMS, strict=True))),
        ("screening_partition_minimums", (("REV-P0", 58), ("REV-P1", 45), ("TOTAL", 102))),
        ("upstream_authority", UPSTREAM_AUTHORITY),
        ("isolation_policy", ISOLATION_POLICY),
    ):
        schema["properties"][name] = _array(value)


def _case_schema(schema: dict[str, Any]) -> None:
    _base_schema(schema)
    schema["properties"]["case_id"] = {"enum": list(CASE_IDS)}
    rules: list[dict[str, Any]] = []
    for case_id, authority in AUTHORITY.items():
        scores = [
            _fixed({"const": name}, {"enum": [0, 1, 2]}, {"const": weight}, {"type": "integer"})
            for name, weight in authority["criteria"]
        ]
        checks = [_fixed({"const": kind}, {"const": value}, {"type": "boolean"}) for kind, value in authority["checks"]]
        properties: dict[str, dict[str, Any]] = {
            "source_declared_compatibility_sha256": {"const": authority["compatibility"]},
            "execution_rfc8785_jcs_sha256": {"const": authority["jcs"]},
            "subject_package_identity": {"const": authority["projection"]},
            "review_partition": {"const": authority["partition"]},
            "criterion_scores": _exact_tuple(scores),
            "deterministic_checks": _exact_tuple(checks),
            "evidence_references": _array(authority["evidence"]),
            "hard_failures": {
                "type": "array",
                "maxItems": len(authority["failures"]),
            },
        }
        if authority["failures"]:
            properties["hard_failures"]["items"] = {
                "oneOf": [
                    _fixed({"const": criterion}, {"const": severity}, {"type": "string"})
                    for criterion, severity in authority["failures"]
                ]
            }
        rules.append(
            {
                "if": {"properties": {"case_id": {"const": case_id}}, "required": ["case_id"]},
                "then": {"properties": properties},
            }
        )
    schema["allOf"] = rules


def _run_schema(schema: dict[str, Any]) -> None:
    _base_schema(schema)
    slots = (schema["properties"]["case_results"]["items"],) * 12
    schema["properties"]["case_results"] = {
        "type": "array",
        "prefixItems": [
            {
                "allOf": [
                    slot,
                    {"properties": {"case_id": {"const": case_id}}},
                ]
            }
            for case_id, slot in zip(CASE_IDS, slots, strict=True)
        ],
        "minItems": 12,
        "maxItems": 12,
    }


def _receipt_schema(schema: dict[str, Any]) -> None:
    _base_schema(schema)
    combinations = {
        "DRY_RUN_VALIDATED": (True, False, False, 0, 0),
        "REFERENCE_CONFORMANT": (False, True, False, 3, 1),
        "REFERENCE_NONCONFORMANT": (None, False, False, 0, 0),
        "VERIFIED_EXISTING": (False, False, True, 0, 1),
    }
    fields = ("dry_run", "published", "verified_existing", "archive_writes", "publication_attempts")
    conditions: list[dict[str, Any]] = []
    for disposition, values in combinations.items():
        retained = {"type": "string" if disposition == "VERIFIED_EXISTING" else "null"}
        properties: dict[str, dict[str, Any]] = {
            field: {"const": value} for field, value in zip(fields, values, strict=True) if value is not None
        }
        properties["retained_publication_receipt_id"] = retained
        properties["retained_publication_receipt_sha256"] = retained
        conditions.append(
            {
                "if": {"properties": {"disposition": {"const": disposition}}},
                "then": {"properties": properties},
            }
        )
    schema["allOf"] = conditions


class VS01BenchmarkExecutionSpecification(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid", json_schema_extra=_spec_schema)
    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["VS01BenchmarkExecutionSpecification"] = "VS01BenchmarkExecutionSpecification"
    batch_id: Literal["BENCH-VS01-BATCH-01"] = "BENCH-VS01-BATCH-01"
    batch_markdown_sha256: Literal["f1f0be8a3be9b4f56de0968ad3f166306a4fdfbdd57e7a45a5d972bbb50b66ff"]
    batch_cases_sha256: Literal["4241a0bf5baf50a12ce5fe6dcfef6ed5492cde410f3d92f5aad8a9f26ba3113f"]
    r01_design_sha256: Literal["d6e89b7db1bd686fb74bdc2530719a3c9e3d9a753983fac7a35bdd8be40abdf7"]
    r01_protocol_sha256: Literal["bf48cbd15b09673f965e4a6300dbec61aec924f56f026032d8c9ccaaa12014bb"]
    erratum_markdown_sha256: Literal["8f3de652db50fc7a93d1368ac6ad53177f0f45858cad927b386127795dc3817d"]
    erratum_json_sha256: Literal["9153c12bc7ea3254ff2c76e685dc56ccbd26e615a6d20e770d196fcc3f5ad2be"]
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
    def exact_authority(self) -> Self:
        exact = (
            self.source_declared_compatibility_hashes == COMPATIBILITY_HASHES,
            self.execution_rfc8785_jcs_hashes == JCS_HASHES,
            self.case_order == CASE_IDS,
            self.subject_projection_identities == PROJECTION_IDENTITIES,
            self.upstream_authority == UPSTREAM_AUTHORITY,
            self.isolation_policy == ISOLATION_POLICY,
            self.screening_case_minimums == tuple(zip(CASE_IDS, CASE_MINIMUMS, strict=True)),
            self.screening_partition_minimums == (("REV-P0", 58), ("REV-P1", 45), ("TOTAL", 102)),
        )
        if not all(exact):
            raise ValueError("benchmark execution specification authority differs")
        if self.specification_identity != canonical_sha256(
            self.model_dump(mode="json", exclude={"specification_identity"})
        ):
            raise ValueError("benchmark execution specification identity differs")
        return self


class VS01BenchmarkCaseResult(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid", json_schema_extra=_case_schema)
    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["VS01BenchmarkCaseResult"] = "VS01BenchmarkCaseResult"
    case_id: str
    source_declared_compatibility_sha256: Sha256
    execution_rfc8785_jcs_sha256: Sha256
    review_partition: str
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
    def exact_authority(self) -> Self:
        authority = AUTHORITY.get(self.case_id)
        if authority is None:
            raise ValueError("benchmark case-result case differs")
        exact = (
            self.source_declared_compatibility_sha256 == authority["compatibility"],
            self.execution_rfc8785_jcs_sha256 == authority["jcs"],
            self.subject_package_identity == authority["projection"],
            self.review_partition == authority["partition"],
            tuple((item[0], item[2]) for item in self.criterion_scores) == authority["criteria"],
            tuple(item[:2] for item in self.deterministic_checks) == authority["checks"],
            self.evidence_references == authority["evidence"],
            all(item[:2] in authority["failures"] for item in self.hard_failures),
        )
        if not all(exact):
            raise ValueError("benchmark case-result authority differs")
        if any(
            score not in (0, 1, 2) or points != score * weight for _, score, weight, points in self.criterion_scores
        ):
            raise ValueError("benchmark criterion arithmetic differs")
        raw = sum(item[3] for item in self.criterion_scores)
        severe = any(item[1] != "HF-4_MINOR" for item in self.hard_failures)
        states = tuple(self.attempt_state == name for name in ("ERROR", "REFUSAL", "TIMEOUT", "MALFORMED"))
        conformant = self.attempt_state == "COMPLETED" and self.leakage_state == "CLEAR"
        conformant &= all(item[1] == 2 for item in self.criterion_scores)
        conformant &= all(item[2] for item in self.deterministic_checks) and not self.hard_failures
        conformant &= self.response_identity == authority["response_sha"]
        incomplete = self.attempt_state != "COMPLETED"
        failed_criteria = {item[0] for item in self.hard_failures}
        valid = (
            self.raw_points == raw,
            self.capped_points == (0 if severe else raw),
            self.response_identity == canonical_sha256(self.response_payload),
            (self.error, self.refusal, self.timeout, self.malformed) == states,
            not incomplete
            or not self.hard_failures
            and raw == 0
            and not any(item[2] for item in self.deterministic_checks),
            all(score == 0 for name, score, _weight, _points in self.criterion_scores if name in failed_criteria),
            (self.leakage_state == "INVALID_LEAKAGE_INCIDENT")
            == (self.attempt_state == self.case_disposition == "INVALID_LEAKAGE_INCIDENT"),
            (self.case_disposition == "REFERENCE_CONFORMANT") == conformant,
        )
        if not all(valid):
            raise ValueError("benchmark case-result accounting differs")
        if self.case_result_identity != canonical_sha256(
            self.model_dump(mode="json", exclude={"case_result_identity"})
        ):
            raise ValueError("benchmark case-result identity differs")
        return self


TwelveCaseResults = Annotated[tuple[VS01BenchmarkCaseResult, ...], Field(min_length=12, max_length=12)]


class VS01BenchmarkRunResult(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid", json_schema_extra=_run_schema)
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
    archive_writes: Literal[0] = 0
    run_result_identity: Sha256

    @model_validator(mode="after")
    def exact_accounting(self) -> Self:
        if tuple(item.case_id for item in self.case_results) != CASE_IDS:
            raise ValueError("benchmark run-result case order differs")
        p0 = sum(item.capped_points for item in self.case_results if item.review_partition.startswith("REV-P0"))
        p1 = sum(item.capped_points for item in self.case_results if item.review_partition.startswith("REV-P1"))
        failures = tuple(
            (name.lower(), sum(item.attempt_state == name for item in self.case_results))
            for name in ("ERROR", "REFUSAL", "TIMEOUT", "MALFORMED", "INVALID_LEAKAGE_INCIDENT")
        )
        hard = tuple(
            (name, sum(value[1] == name for item in self.case_results for value in item.hard_failures))
            for name in ("HF-1_CRITICAL", "HF-2_MAJOR", "HF-3_MATERIAL", "HF-4_MINOR")
        )
        conformant = all(item.case_disposition == "REFERENCE_CONFORMANT" for item in self.case_results)
        disposition = "REFERENCE_CONFORMANT" if conformant else "REFERENCE_NONCONFORMANT_REPAIR_REQUIRED"
        exact = (
            self.completed_attempts == sum(item.attempt_state == "COMPLETED" for item in self.case_results),
            (self.p0_points, self.p1_points, self.total_points) == (p0, p1, p0 + p1),
            self.failure_counts == failures,
            self.hard_failure_counts == hard,
            self.special_outcomes
            == tuple(
                (name, self.case_results[index].case_disposition)
                for name, index in (("B09", 8), ("B10", 9), ("B11", 10))
            ),
            self.disposition == disposition,
        )
        if not all(exact):
            raise ValueError("benchmark run-result accounting differs")
        if self.run_result_identity != canonical_sha256(self.model_dump(mode="json", exclude={"run_result_identity"})):
            raise ValueError("benchmark run-result identity differs")
        return self


class VS01BenchmarkExecutionReceipt(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid", json_schema_extra=_receipt_schema)
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
    disposition: Literal["DRY_RUN_VALIDATED", "REFERENCE_CONFORMANT", "REFERENCE_NONCONFORMANT", "VERIFIED_EXISTING"]
    dry_run: bool
    published: bool
    verified_existing: bool
    initial_upstream_fingerprints: tuple[HashBinding, ...]
    pre_store_upstream_fingerprints: tuple[HashBinding, ...]
    replay_count: Literal[2]
    subject_invocations: Literal[24]
    scoring_invocations: Literal[24]
    case_results_constructed: Literal[24]
    run_results_constructed: Literal[2]
    receipts_constructed: Literal[1]
    publication_attempts: Literal[0, 1]
    retained_publication_receipt_id: UUID | None
    retained_publication_receipt_sha256: Sha256 | None
    requested_attempts: Literal[12] = 12
    completed_attempts: int = Field(ge=0, le=12)
    error_counts: tuple[CountBinding, ...]
    model_invocations: Literal[0] = 0
    ocr_invocations: Literal[0] = 0
    vlm_invocations: Literal[0] = 0
    network_invocations: Literal[0] = 0
    database_writes: Literal[0] = 0
    archive_writes: Literal[0, 3]

    @model_validator(mode="after")
    def exact_operation(self) -> Self:
        if self.receipt_id.version != 7 or self.generated_at.tzinfo is None or self.generated_at.utcoffset() is None:
            raise ValueError("benchmark receipt identity or timestamp differs")
        retained = (
            self.retained_publication_receipt_id is not None and self.retained_publication_receipt_sha256 is not None
        )
        combinations = {
            "DRY_RUN_VALIDATED": (True, False, False, 0, 0, False),
            "REFERENCE_CONFORMANT": (False, True, False, 3, 1, False),
            "REFERENCE_NONCONFORMANT": (self.dry_run, False, False, 0, 0, False),
            "VERIFIED_EXISTING": (False, False, True, 0, 1, True),
        }
        observed = (
            self.dry_run,
            self.published,
            self.verified_existing,
            self.archive_writes,
            self.publication_attempts,
            retained,
        )
        if observed != combinations[self.disposition]:
            raise ValueError("benchmark receipt operation differs")
        if self.initial_upstream_fingerprints != self.pre_store_upstream_fingerprints:
            raise ValueError("benchmark upstream authority changed")
        names = ("t04", "t05", "t06", "archive_root", "incoming_inventory")
        if tuple(item[0] for item in self.initial_upstream_fingerprints) != names:
            raise ValueError("benchmark upstream fingerprint inventory differs")
        expected_errors = ("error", "refusal", "timeout", "malformed", "invalid_leakage_incident")
        if tuple(item[0] for item in self.error_counts) != expected_errors:
            raise ValueError("benchmark receipt error accounting differs")
        if self.completed_attempts + sum(item[1] for item in self.error_counts) != self.requested_attempts:
            raise ValueError("benchmark receipt attempt accounting differs")
        return self
