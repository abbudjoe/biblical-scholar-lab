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
        result[case["case_id"]] = {
            "compatibility": case["case_content_sha256"],
            "jcs": plan["execution_rfc8785_jcs_sha256"],
            "projection": projection["subject_projection_identity"],
            "criteria": tuple((item["criterion_id"], item["weight"]) for item in case["rubric"]),
            "checks": _checks(case),
            "evidence": tuple(case["source_dependencies"]),
            "partition": partition,
            "response_payload": tuple(tuple(item) for item in fixture["response_payload"]),
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


LIVE_SPECIFICATION_IDENTITY = "ebba965fd37846d2a0af2ff27e35cdd79574f37042751d581c69f74e4ca35561"
DRY_SPECIFICATION_IDENTITY = "9426a48b6c53d0f3ee5e34ae65e3d1894c83192540a65054195e1d2ebc710528"
SPECIFICATION_IDENTITIES = (LIVE_SPECIFICATION_IDENTITY, DRY_SPECIFICATION_IDENTITY)


def _array(values: tuple[Any, ...]) -> dict[str, Any]:
    constants: list[dict[str, Any]] = [
        {"const": list(cast(tuple[Any, ...], value)) if isinstance(value, tuple) else value} for value in values
    ]
    return _exact_tuple(constants)


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
    schema["oneOf"] = [
        {"properties": {"execution_mode": {"const": mode}, "specification_identity": {"const": identity}}}
        for mode, identity in (
            ("REFERENCE_CONFORMANCE", LIVE_SPECIFICATION_IDENTITY),
            ("REFERENCE_CONFORMANCE_DRY_RUN", DRY_SPECIFICATION_IDENTITY),
        )
    ]


def _state_fields(authority: dict[str, Any], score: int, checks: bool, disposition: str) -> dict[str, Any]:
    points = sum(2 * weight for _name, weight in authority["criteria"]) if score == 2 else 0
    return {
        "criterion_scores": _array(
            tuple((name, score, weight, score * weight) for name, weight in authority["criteria"])
        ),
        "deterministic_checks": _array(tuple((kind, rule, checks) for kind, rule in authority["checks"])),
        "hard_failures": {"type": "array", "maxItems": 0},
        "raw_points": {"const": points},
        "capped_points": {"const": points},
        "case_disposition": {"const": disposition},
    }


def _case_state_rules(authority: dict[str, Any]) -> list[dict[str, Any]]:
    reference = {
        "response_payload": {"const": [list(item) for item in authority["response_payload"]]},
        "response_identity": {"const": authority["response_sha"]},
    }
    completed = {"attempt_state": {"const": "COMPLETED"}}
    unsupported = _state_fields(authority, 0, False, "UNSUPPORTED_SUBJECT_FOR_REFERENCE_SCORER")
    unsupported["deterministic_checks"] = _exact_tuple(
        [_fixed({"const": kind}, {"const": rule}, {"type": "boolean"}) for kind, rule in authority["checks"]]
    )
    clear_flags = {name: {"const": False} for name in ("error", "refusal", "timeout", "malformed")}
    rules = [
        {
            "if": {"properties": completed | reference, "required": list(completed | reference)},
            "then": {
                "properties": _state_fields(authority, 2, True, "REFERENCE_CONFORMANT")
                | clear_flags
                | {"leakage_state": {"const": "CLEAR"}}
            },
        },
        {
            "if": {
                "properties": completed,
                "required": list(completed),
                "not": {"properties": reference, "required": list(reference)},
            },
            "then": {"properties": unsupported | clear_flags | {"leakage_state": {"const": "CLEAR"}}},
        },
    ]
    for state, flag in ((name, name.lower()) for name in ("ERROR", "REFUSAL", "TIMEOUT", "MALFORMED")):
        rules.append(
            {
                "if": {"properties": {"attempt_state": {"const": state}}, "required": ["attempt_state"]},
                "then": {
                    "properties": _state_fields(authority, 0, False, "REFERENCE_NONCONFORMANT_REPAIR_REQUIRED")
                    | clear_flags
                    | {flag: {"const": True}, "leakage_state": {"const": "CLEAR"}}
                },
            }
        )
    rules.append(
        {
            "if": {
                "properties": {"attempt_state": {"const": "INVALID_LEAKAGE_INCIDENT"}},
                "required": ["attempt_state"],
            },
            "then": {
                "properties": _state_fields(authority, 0, False, "INVALID_LEAKAGE_INCIDENT")
                | clear_flags
                | {"leakage_state": {"const": "INVALID_LEAKAGE_INCIDENT"}}
            },
        }
    )
    return rules


def _case_schema(schema: dict[str, Any]) -> None:
    _base_schema(schema)
    schema["properties"]["case_id"] = {"enum": list(CASE_IDS)}
    rules: list[dict[str, Any]] = []
    for case_id, authority in AUTHORITY.items():
        properties: dict[str, dict[str, Any]] = {
            "source_declared_compatibility_sha256": {"const": authority["compatibility"]},
            "execution_rfc8785_jcs_sha256": {"const": authority["jcs"]},
            "subject_package_identity": {"const": authority["projection"]},
            "review_partition": {"const": authority["partition"]},
            "evidence_references": _array(authority["evidence"]),
        }
        rules.append(
            {
                "if": {"properties": {"case_id": {"const": case_id}}, "required": ["case_id"]},
                "then": {"properties": properties, "allOf": _case_state_rules(authority)},
            }
        )
    schema["allOf"] = rules


def _run_schema(schema: dict[str, Any]) -> None:
    _base_schema(schema)
    schema["properties"]["execution_specification_identity"] = {"enum": list(SPECIFICATION_IDENTITIES)}
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
    for name, value in (
        ("replay_count", 2),
        ("subject_invocations", 24),
        ("case_results_constructed", 24),
        ("run_results_constructed", 2),
        ("receipts_constructed", 1),
    ):
        schema["properties"][name] = {"const": value}
    schema["properties"]["scoring_invocations"] = {"type": "integer", "minimum": 0, "maximum": 24}
    combinations = {
        "DRY_RUN_VALIDATED": (True, False, False, 0, 0, DRY_SPECIFICATION_IDENTITY),
        "REFERENCE_CONFORMANT": (False, True, False, 3, 1, LIVE_SPECIFICATION_IDENTITY),
        "VERIFIED_EXISTING": (False, False, True, 0, 1, LIVE_SPECIFICATION_IDENTITY),
    }
    for dry_run, identity in ((False, LIVE_SPECIFICATION_IDENTITY), (True, DRY_SPECIFICATION_IDENTITY)):
        combinations[f"REFERENCE_NONCONFORMANT_{dry_run}"] = (dry_run, False, False, 0, 0, identity)
    names = (
        "dry_run",
        "published",
        "verified_existing",
        "archive_writes",
        "publication_attempts",
        "execution_specification_identity",
    )
    choices: list[dict[str, Any]] = []
    for key, values in combinations.items():
        disposition = key.removesuffix("_True").removesuffix("_False")
        retained = {"type": "string" if disposition == "VERIFIED_EXISTING" else "null"}
        properties = {name: {"const": value} for name, value in zip(names, values, strict=True)}
        properties |= {"disposition": {"const": disposition}, "retained_publication_receipt_id": retained}
        properties["retained_publication_receipt_sha256"] = retained
        choices.append({"properties": properties, "required": list(properties)})
    schema["oneOf"] = choices


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
        expected = (
            DRY_SPECIFICATION_IDENTITY if self.execution_mode.endswith("DRY_RUN") else LIVE_SPECIFICATION_IDENTITY
        )
        if self.specification_identity != expected or expected != canonical_sha256(
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
        )
        if not all(exact):
            raise ValueError("benchmark case-result authority differs")
        if any(score not in (0, 2) or points != score * weight for _, score, weight, points in self.criterion_scores):
            raise ValueError("benchmark criterion arithmetic differs")
        valid = _case_state_valid(self, authority)
        if not all(valid):
            raise ValueError("benchmark case-result accounting differs")
        if self.case_result_identity != canonical_sha256(
            self.model_dump(mode="json", exclude={"case_result_identity"})
        ):
            raise ValueError("benchmark case-result identity differs")
        return self


def _case_state_valid(result: VS01BenchmarkCaseResult, authority: dict[str, Any]) -> tuple[bool, ...]:
    states = tuple(result.attempt_state == name for name in ("ERROR", "REFUSAL", "TIMEOUT", "MALFORMED"))
    zeros = all(score == points == 0 for _name, score, _weight, points in result.criterion_scores)
    base = (
        result.response_identity == canonical_sha256(result.response_payload),
        (result.error, result.refusal, result.timeout, result.malformed) == states,
        not result.hard_failures,
    )
    if result.attempt_state == "INVALID_LEAKAGE_INCIDENT":
        return base + (
            result.leakage_state == result.case_disposition == "INVALID_LEAKAGE_INCIDENT",
            zeros and not any(item[2] for item in result.deterministic_checks),
            result.raw_points == result.capped_points == 0,
        )
    if result.attempt_state != "COMPLETED":
        return base + (
            result.leakage_state == "CLEAR" and result.case_disposition == "REFERENCE_NONCONFORMANT_REPAIR_REQUIRED",
            zeros and not any(item[2] for item in result.deterministic_checks),
            result.raw_points == result.capped_points == 0,
        )
    exact = (
        result.response_payload == authority["response_payload"]
        and result.response_identity == authority["response_sha"]
    )
    if exact:
        maximum = sum(2 * weight for _name, weight in authority["criteria"])
        return base + (
            result.leakage_state == "CLEAR" and result.case_disposition == "REFERENCE_CONFORMANT",
            all(score == 2 and points == 2 * weight for _name, score, weight, points in result.criterion_scores),
            all(item[2] for item in result.deterministic_checks),
            result.raw_points == result.capped_points == maximum,
        )
    return base + (
        result.leakage_state == "CLEAR" and result.case_disposition == "UNSUPPORTED_SUBJECT_FOR_REFERENCE_SCORER",
        zeros,
        result.raw_points == result.capped_points == 0,
    )


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
        if self.execution_specification_identity not in SPECIFICATION_IDENTITIES:
            raise ValueError("benchmark run-result execution specification differs")
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
    scoring_invocations: int = Field(ge=0, le=24)
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
        identity = DRY_SPECIFICATION_IDENTITY if self.dry_run else LIVE_SPECIFICATION_IDENTITY
        combinations = {
            "DRY_RUN_VALIDATED": (True, False, False, 0, 0, False, DRY_SPECIFICATION_IDENTITY),
            "REFERENCE_CONFORMANT": (False, True, False, 3, 1, False, LIVE_SPECIFICATION_IDENTITY),
            "REFERENCE_NONCONFORMANT": (self.dry_run, False, False, 0, 0, False, identity),
            "VERIFIED_EXISTING": (False, False, True, 0, 1, True, LIVE_SPECIFICATION_IDENTITY),
        }
        observed = (
            self.dry_run,
            self.published,
            self.verified_existing,
            self.archive_writes,
            self.publication_attempts,
            retained,
            self.execution_specification_identity,
        )
        if observed != combinations[self.disposition]:
            raise ValueError("benchmark receipt operation differs")
        if self.initial_upstream_fingerprints != self.pre_store_upstream_fingerprints:
            raise ValueError("benchmark upstream authority changed")
        ledger = (
            self.subject_invocations == self.replay_count * 12,
            self.scoring_invocations <= self.subject_invocations,
            self.case_results_constructed == self.subject_invocations,
            self.run_results_constructed == self.replay_count,
            self.receipts_constructed == 1,
        )
        if not all(ledger):
            raise ValueError("benchmark receipt operation ledger differs")
        names = ("t04", "t05", "t06", "archive_root", "incoming_inventory")
        if tuple(item[0] for item in self.initial_upstream_fingerprints) != names:
            raise ValueError("benchmark upstream fingerprint inventory differs")
        expected_errors = ("error", "refusal", "timeout", "malformed", "invalid_leakage_incident")
        if tuple(item[0] for item in self.error_counts) != expected_errors:
            raise ValueError("benchmark receipt error accounting differs")
        if self.completed_attempts + sum(item[1] for item in self.error_counts) != self.requested_attempts:
            raise ValueError("benchmark receipt attempt accounting differs")
        return self
