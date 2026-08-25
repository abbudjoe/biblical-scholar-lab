from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol, cast

import rfc8785

from bsl.contracts.benchmark import (
    CASE_IDS,
    CASE_MINIMUMS,
    COMPATIBILITY_HASHES,
    ISOLATION_POLICY,
    JCS_HASHES,
    PROJECTION_IDENTITIES,
    UPSTREAM_AUTHORITY,
    VS01BenchmarkCaseResult,
    VS01BenchmarkExecutionSpecification,
)

ROOT = Path(__file__).parents[3]
BATCH_MARKDOWN = ROOT / "design/approved/BENCH-VS01-BATCH-01.md"
BATCH_CASES = ROOT / "design/approved/BENCH-VS01-BATCH-01-cases.json"
PROTOCOL = ROOT / "design/approved/VS01-T07-benchmark-execution-protocol-R01.json"
ERRATUM = ROOT / "design/approved/BENCH-VS01-BATCH-01-ERRATA-01.json"
BATCH_MARKDOWN_SHA256 = "f1f0be8a3be9b4f56de0968ad3f166306a4fdfbdd57e7a45a5d972bbb50b66ff"
BATCH_CASES_SHA256 = "4241a0bf5baf50a12ce5fe6dcfef6ed5492cde410f3d92f5aad8a9f26ba3113f"
PROTOCOL_SHA256 = "bf48cbd15b09673f965e4a6300dbec61aec924f56f026032d8c9ccaaa12014bb"
ERRATUM_SHA256 = "9153c12bc7ea3254ff2c76e685dc56ccbd26e615a6d20e770d196fcc3f5ad2be"
DESIGN_SHA256 = "d6e89b7db1bd686fb74bdc2530719a3c9e3d9a753983fac7a35bdd8be40abdf7"
ERRATUM_MARKDOWN_SHA256 = "8f3de652db50fc7a93d1368ac6ad53177f0f45858cad927b386127795dc3817d"
BASE_RASTER_SHA256 = "2c0cebc7245eb1032b2b1e4c0ee16e6f74dec47e6a53d8f49c4b9d0a847abbfb"
DEGRADED_RASTER_SHA256 = "cb47073c8e40da01285d90d26ebb7144b34047a2cde8f58e4ba0d1f2cfb67fce"
B10_COMPATIBILITY_SHA256 = "dccf12a80604494847853850d86706da17dce45e4663cedbf6c07a68f2d3fa06"
B10_JCS_SHA256 = "f158ea959695243e18c6fc46661387d17f7fe2268bd479f24db02ef868ac7eab"
REAL_CASE_IDS = tuple(f"VS01-B{index:02d}-C01" for index in range(1, 13))
FORBIDDEN_SUBJECT_FIELDS = (
    "answer_contract",
    "reference_response",
    "reference_responses",
    "rubric",
    "deterministic_checks",
    "hard_failures",
    "scorer_identity",
    "scorer_path",
    "hidden_t06_truth",
    "degradation_masks",
    "other_case_outputs",
    "promotion_thresholds",
    "archive_handle",
    "database_handle",
    "environment_coordinates",
)
CHECK_FIELDS = {
    "CLAIM_SOURCE_MAP": (frozenset({"claim", "required_source"}),),
    "EXACT_FIELD": (frozenset({"field", "value"}),),
    "EXACT_STRING": (frozenset({"value"}), frozenset({"source", "value"})),
    "FORBIDDEN_STRING": (frozenset({"value"}),),
    "ONLY_CANONICAL_QUOTE": (frozenset({"value"}),),
    "REGION_ROLE_MAP": (frozenset({"expected"}),),
    "REQUIRED_EVENT": (frozenset({"value"}),),
    "REQUIRED_SOURCE_HANDLE": (frozenset({"value"}),),
    "SESSION_STATE": (frozenset({"field", "value"}), frozenset({"field", "contains"})),
    "TEXT_QUOTE_SELECTOR": (frozenset({"exact", "prefix"}),),
}


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(rfc8785.dumps(value)).hexdigest()


def build_execution_specification(
    authorities: tuple[_CaseAuthority, ...], *, dry_run: bool
) -> VS01BenchmarkExecutionSpecification:
    if tuple(item.case_id for item in authorities) != CASE_IDS:
        raise ValueError("benchmark execution authority order differs")
    payload: dict[str, Any] = {
        "batch_markdown_sha256": BATCH_MARKDOWN_SHA256,
        "batch_cases_sha256": BATCH_CASES_SHA256,
        "r01_design_sha256": DESIGN_SHA256,
        "r01_protocol_sha256": PROTOCOL_SHA256,
        "erratum_markdown_sha256": ERRATUM_MARKDOWN_SHA256,
        "erratum_json_sha256": ERRATUM_SHA256,
        "source_declared_compatibility_hashes": COMPATIBILITY_HASHES,
        "execution_rfc8785_jcs_hashes": JCS_HASHES,
        "case_order": CASE_IDS,
        "subject_projection_identities": PROJECTION_IDENTITIES,
        "scorer_revision": "VS01-T07-REFERENCE-CONFORMANCE-SCORER-v1",
        "upstream_authority": UPSTREAM_AUTHORITY,
        "isolation_policy": ISOLATION_POLICY,
        "screening_case_minimums": tuple(zip(CASE_IDS, CASE_MINIMUMS, strict=True)),
        "screening_partition_minimums": (("REV-P0", 58), ("REV-P1", 45), ("TOTAL", 102)),
        "b08_full_runtime_limitation": "VS01-B08-RUNTIME-C01_REQUIRED_NOT_AUTHORED",
        "execution_mode": "REFERENCE_CONFORMANCE_DRY_RUN" if dry_run else "REFERENCE_CONFORMANCE",
    }
    draft = VS01BenchmarkExecutionSpecification.model_construct(**payload, specification_identity="0" * 64)
    payload["specification_identity"] = canonical_sha256(
        draft.model_dump(mode="json", exclude={"specification_identity"})
    )
    return VS01BenchmarkExecutionSpecification.model_validate(payload)


def _strict_json(data: bytes) -> dict[str, Any]:
    def unique(items: list[tuple[str, Any]]) -> dict[str, Any]:
        if len(items) != len(dict(items)):
            raise ValueError("benchmark authority contains duplicate JSON keys")
        return dict(items)

    def finite(value: str) -> float:
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("benchmark authority contains a non-finite number")
        return number

    try:
        result = json.loads(data, object_pairs_hook=unique, parse_constant=finite, parse_float=finite)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("benchmark authority is not strict UTF-8 JSON") from None
    if not isinstance(result, dict):
        raise ValueError("benchmark authority is not a JSON object")
    return cast(dict[str, Any], result)


def _read_exact(path: Path, expected: str) -> bytes:
    try:
        data = path.read_bytes()
    except OSError:
        raise ValueError(f"benchmark authority is missing: {path.name}") from None
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f"benchmark authority hash differs: {path.name}")
    return data


@dataclass(frozen=True)
class _CaseAuthority:
    source: dict[str, Any]
    protocol: dict[str, Any]
    evidence_contract: dict[str, Any]
    compatibility_sha256: str
    execution_rfc8785_jcs_sha256: str

    @property
    def case_id(self) -> str:
        return cast(str, self.source["case_id"])


@dataclass(frozen=True)
class SubjectCasePackage:
    case_id: str
    source_declared_compatibility_sha256: str
    execution_rfc8785_jcs_sha256: str
    prompt_fields: tuple[tuple[str, str], ...]
    evaluation_mode: str
    answer_mode: str
    evidence_contract_id: str
    whitelisted_source_handles: tuple[str, ...]
    authorized_raster_sha256: str | None
    deterministic_tool_interfaces: tuple[tuple[tuple[str, str], ...], ...]
    response_fields: tuple[str, ...]
    case_local_budgets: tuple[tuple[str, int], ...]
    package_identity: str

    def payload(self, *, include_identity: bool = True) -> dict[str, Any]:
        value = asdict(self)
        if not include_identity:
            value.pop("package_identity")
        return value


@dataclass(frozen=True)
class ScorerCaseAuthority:
    case_id: str
    source_declared_compatibility_sha256: str
    execution_rfc8785_jcs_sha256: str
    reference_payload: tuple[tuple[str, str], ...]
    reference_payload_sha256: str
    deterministic_checks: tuple[tuple[str, str], ...]
    criteria: tuple[tuple[str, int, str], ...]
    evidence_references: tuple[str, ...]
    review_partition: str
    scorer_plan_identity: str


@dataclass(frozen=True)
class StructuredSubjectResponse:
    case_id: str
    source_declared_compatibility_sha256: str
    execution_rfc8785_jcs_sha256: str
    subject_package_identity: str
    response_payload: tuple[tuple[str, str], ...]
    response_payload_sha256: str
    attempt_state: str = "COMPLETED"

    def payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReferenceSubjectFixture:
    case_id: str
    source_declared_compatibility_sha256: str
    execution_rfc8785_jcs_sha256: str
    answer_mode: str
    response_payload: tuple[tuple[str, str], ...]
    response_payload_sha256: str

    def payload(self) -> dict[str, Any]:
        return asdict(self)


def failed_case_result(
    case: SubjectCasePackage, scorer: ScorerCaseAuthority, attempt_state: str
) -> VS01BenchmarkCaseResult:
    scores = tuple((name, 0, weight, 0) for name, weight, _ in scorer.criteria)
    payload: dict[str, Any] = {
        "case_id": case.case_id,
        "source_declared_compatibility_sha256": case.source_declared_compatibility_sha256,
        "execution_rfc8785_jcs_sha256": case.execution_rfc8785_jcs_sha256,
        "review_partition": scorer.review_partition,
        "subject_package_identity": case.package_identity,
        "response_identity": canonical_sha256(()),
        "response_payload": (),
        "attempt_state": attempt_state,
        "criterion_scores": scores,
        "deterministic_checks": tuple((kind, rule, False) for kind, rule in scorer.deterministic_checks),
        "hard_failures": (),
        "raw_points": 0,
        "capped_points": 0,
        "case_disposition": "REFERENCE_NONCONFORMANT_REPAIR_REQUIRED",
        "leakage_state": "CLEAR",
        "error": attempt_state == "ERROR",
        "refusal": attempt_state == "REFUSAL",
        "timeout": attempt_state == "TIMEOUT",
        "malformed": attempt_state == "MALFORMED",
        "evidence_references": scorer.evidence_references,
    }
    draft = VS01BenchmarkCaseResult.model_construct(**payload, case_result_identity="0" * 64)
    payload["case_result_identity"] = canonical_sha256(draft.model_dump(mode="json", exclude={"case_result_identity"}))
    return VS01BenchmarkCaseResult.model_validate(payload)


class VS01BenchmarkSubjectAdapter(Protocol):
    def generate(self, case: SubjectCasePackage) -> StructuredSubjectResponse: ...


def _case_hashes(case: dict[str, Any]) -> tuple[str, str]:
    payload = {key: value for key, value in case.items() if key != "case_content_sha256"}
    legacy = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(legacy).hexdigest(), canonical_sha256(payload)


def _validate_inventory(cases: list[dict[str, Any]], evidence_count: int) -> None:
    order = tuple(case.get("case_id") for case in cases)
    criteria = [criterion for case in cases for criterion in case.get("rubric", ())]
    weights = sum(item.get("weight", -10_000) for item in criteria)
    p0 = [case for case in cases if str(case.get("review_partition", "")).startswith("REV-P0")]
    p1 = [case for case in cases if str(case.get("review_partition", "")).startswith("REV-P1")]
    p0_max = 2 * sum(item["weight"] for case in p0 for item in case["rubric"])
    p1_max = 2 * sum(item["weight"] for case in p1 for item in case["rubric"])
    observed = evidence_count, len(cases), len(criteria), weights, 2 * weights, len(p0), p0_max, len(p1), p1_max
    if order != REAL_CASE_IDS or observed != (7, 12, 37, 60, 120, 7, 64, 5, 56):
        raise ValueError("frozen benchmark order or arithmetic differs")


def load_benchmark_authority() -> tuple[_CaseAuthority, ...]:
    _read_exact(BATCH_MARKDOWN, BATCH_MARKDOWN_SHA256)
    source = _strict_json(_read_exact(BATCH_CASES, BATCH_CASES_SHA256))
    protocol = _strict_json(_read_exact(PROTOCOL, PROTOCOL_SHA256))
    erratum = _strict_json(_read_exact(ERRATUM, ERRATUM_SHA256))
    raw_cases = cast(list[dict[str, Any]], source.get("cases", []))
    protocol_cases = cast(list[dict[str, Any]], protocol.get("frozen_batch", {}).get("cases", []))
    evidence_contracts = {
        item["evidence_contract_id"]: item for item in cast(list[dict[str, Any]], source.get("evidence_contracts", []))
    }
    _validate_inventory(raw_cases, len(source.get("evidence_contracts", ())))
    if tuple(item.get("case_id") for item in protocol_cases) != REAL_CASE_IDS:
        raise ValueError("R01 protocol case order differs")
    erratum_map = {item["case_id"]: item for item in erratum.get("case_hashes", ())}
    authorities: list[_CaseAuthority] = []
    mismatches: list[str] = []
    for case, plan in zip(raw_cases, protocol_cases, strict=True):
        legacy, jcs = _case_hashes(case)
        case_id = cast(str, case["case_id"])
        mapping = erratum_map.get(case_id, {})
        exact = (
            legacy == case.get("case_content_sha256") == plan.get("source_declared_case_content_sha256"),
            legacy == mapping.get("source_declared_case_content_sha256"),
            jcs == plan.get("execution_rfc8785_jcs_sha256") == mapping.get("execution_rfc8785_jcs_sha256"),
        )
        if not all(exact):
            raise ValueError(f"benchmark dual-hash authority differs: {case_id}")
        if legacy != jcs:
            mismatches.append(case_id)
        evidence = evidence_contracts.get(cast(str, case.get("evidence_contract_id")))
        if evidence is None:
            raise ValueError(f"benchmark evidence contract is missing: {case_id}")
        authorities.append(_CaseAuthority(case, plan, evidence, legacy, jcs))
    b10 = authorities[9]
    if mismatches != ["VS01-B10-C01"] or (b10.compatibility_sha256, b10.execution_rfc8785_jcs_sha256) != (
        B10_COMPATIBILITY_SHA256,
        B10_JCS_SHA256,
    ):
        raise ValueError("B10 dual-hash compatibility authority differs")
    return tuple(authorities)


def _prompt_fields(case: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    if "prompt" in case:
        return (("prompt", cast(str, case["prompt"])),)
    if "turns" in case:
        return tuple((f"turn_{item['turn']}_{item['role']}", item["content"]) for item in case["turns"])
    prompts = cast(dict[str, str], case["prompts"])
    return tuple((name, prompts[name]) for name in ("brief", "study"))


def _tools(case_id: str) -> tuple[tuple[tuple[str, str], ...], ...]:
    if case_id in {"VS01-B01-C01", "VS01-B09-C01", "VS01-B10-C01"}:
        return ((("name", "exact_passage_lookup"), ("edition", "ASV"), ("passage", "John.1.5")),)
    if case_id == "VS01-B11-C01":
        return ((("name", "exact_passage_rehydration"), ("editions", "ASV,WEB_CLASSIC"), ("passage", "John.1.5")),)
    return ()


def compile_subject_package(authority: _CaseAuthority) -> SubjectCasePackage:
    case, case_id = authority.source, authority.case_id
    raster = (
        BASE_RASTER_SHA256
        if case_id == "VS01-B09-C01"
        else DEGRADED_RASTER_SHA256
        if case_id == "VS01-B10-C01"
        else None
    )
    payload: dict[str, Any] = {
        "case_id": case_id,
        "source_declared_compatibility_sha256": authority.compatibility_sha256,
        "execution_rfc8785_jcs_sha256": authority.execution_rfc8785_jcs_sha256,
        "prompt_fields": _prompt_fields(case),
        "evaluation_mode": case["evaluation_mode"],
        "answer_mode": case["answer_mode"],
        "evidence_contract_id": case["evidence_contract_id"],
        "whitelisted_source_handles": tuple(case["source_dependencies"]),
        "authorized_raster_sha256": raster,
        "deterministic_tool_interfaces": _tools(case_id),
        "response_fields": ("brief", "study") if "reference_responses" in case else ("answer",),
        "case_local_budgets": (("attempts", 1), ("retries", 0), ("semantic_rerolls", 0)),
    }
    package = SubjectCasePackage(**payload, package_identity=canonical_sha256(payload))
    audit_subject_package(package)
    return package


def audit_subject_package(package: SubjectCasePackage) -> None:
    rendered = json.dumps(package.payload(), ensure_ascii=False, sort_keys=True)
    leaked = [field for field in FORBIDDEN_SUBJECT_FIELDS if f'"{field}"' in rendered]
    if leaked or any(value.startswith(("/", "file:", "postgres")) for value in package.whitelisted_source_handles):
        raise ValueError("INVALID_LEAKAGE_INCIDENT")
    if package.case_id == "VS01-B08-C01" and (
        package.deterministic_tool_interfaces or len(package.whitelisted_source_handles) != 2
    ):
        raise ValueError("INVALID_LEAKAGE_INCIDENT")
    if package.case_id in {"VS01-B09-C01", "VS01-B10-C01"} and package.authorized_raster_sha256 is None:
        raise ValueError("INVALID_LEAKAGE_INCIDENT")


def _reference_payload(case: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    if "reference_response" in case:
        return (("answer", cast(str, case["reference_response"])),)
    responses = cast(dict[str, str], case["reference_responses"])
    return tuple((name, responses[name]) for name in ("brief", "study"))


def compile_reference_fixture(authority: _CaseAuthority) -> ReferenceSubjectFixture:
    payload = _reference_payload(authority.source)
    return ReferenceSubjectFixture(
        authority.case_id,
        authority.compatibility_sha256,
        authority.execution_rfc8785_jcs_sha256,
        cast(str, authority.source["answer_mode"]),
        payload,
        canonical_sha256(payload),
    )


def compile_scorer_authority(authority: _CaseAuthority) -> ScorerCaseAuthority:
    source, plan = authority.source, authority.protocol
    plan_criteria = {item["criterion_id"]: item for item in plan["criteria"]}
    criteria = tuple(
        (item["criterion_id"], item["weight"], plan_criteria[item["criterion_id"]].get("hard_failure_severity", ""))
        for item in source["rubric"]
    )
    if any(plan_criteria[item[0]]["weight"] != item[1] for item in criteria):
        raise ValueError(f"scorer-plan rubric differs: {authority.case_id}")
    check_records = source.get("deterministic_checks", ())
    for item in check_records:
        if frozenset(set(item) - {"type"}) not in CHECK_FIELDS.get(item.get("type"), ()):
            raise ValueError(f"unsupported deterministic check authority: {authority.case_id}")
    checks = tuple(
        (
            item["type"],
            json.dumps(
                {key: value for key, value in item.items() if key != "type"},
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
        for item in check_records
    )
    response = _reference_payload(source)
    payload: dict[str, Any] = {
        "case_id": authority.case_id,
        "source_declared_compatibility_sha256": authority.compatibility_sha256,
        "execution_rfc8785_jcs_sha256": authority.execution_rfc8785_jcs_sha256,
        "reference_payload": response,
        "reference_payload_sha256": canonical_sha256(response),
        "deterministic_checks": checks,
        "criteria": criteria,
        "evidence_references": tuple(source["source_dependencies"]),
        "review_partition": source["review_partition"],
    }
    return ScorerCaseAuthority(
        case_id=authority.case_id,
        source_declared_compatibility_sha256=authority.compatibility_sha256,
        execution_rfc8785_jcs_sha256=authority.execution_rfc8785_jcs_sha256,
        reference_payload=response,
        reference_payload_sha256=canonical_sha256(response),
        deterministic_checks=checks,
        criteria=criteria,
        evidence_references=tuple(source["source_dependencies"]),
        review_partition=source["review_partition"],
        scorer_plan_identity=canonical_sha256(payload),
    )


def compatibility_hash_matrix(authorities: tuple[_CaseAuthority, ...]) -> tuple[tuple[str, str, str], ...]:
    return tuple((item.case_id, item.compatibility_sha256, item.execution_rfc8785_jcs_sha256) for item in authorities)


def _fixture_document(authorities: tuple[_CaseAuthority, ...]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "fixture_id": "VS01-T07-REFERENCE-SUBJECT-RESPONSES-v1",
        "compatibility_hash_matrix_sha256": canonical_sha256(compatibility_hash_matrix(authorities)),
        "cases": [compile_reference_fixture(item).payload() for item in authorities],
    }


def _projection_document(authorities: tuple[_CaseAuthority, ...]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for authority in authorities:
        package = compile_subject_package(authority)
        withheld = tuple(authority.evidence_contract.get("withheld", ()))
        visible = authority.protocol.get("subject_visible", {})
        record = package.payload() | {
            "subject_projection_identity": package.package_identity,
            "explicit_withheld_layers": withheld
            + tuple(visible.get("explicitly_withheld", ()))
            + tuple(visible.get("withheld_from_subject", ())),
            "forbidden_subject_fields": FORBIDDEN_SUBJECT_FIELDS,
        }
        records.append(record)
    return {
        "schema_version": "1.0",
        "manifest_id": "VS01-T07-SUBJECT-PROJECTION-MANIFEST-v1",
        "compatibility_hash_matrix_sha256": canonical_sha256(compatibility_hash_matrix(authorities)),
        "cases": records,
    }


def generated_fixture_bytes(authorities: tuple[_CaseAuthority, ...] | None = None) -> tuple[bytes, bytes]:
    frozen = authorities or load_benchmark_authority()
    return rfc8785.dumps(_fixture_document(frozen)) + b"\n", rfc8785.dumps(_projection_document(frozen)) + b"\n"


def static_compilation_identity(authorities: tuple[_CaseAuthority, ...] | None = None) -> str:
    frozen = authorities or load_benchmark_authority()
    payload = tuple(
        (
            item.case_id,
            compile_subject_package(item).package_identity,
            compile_scorer_authority(item).scorer_plan_identity,
            compile_reference_fixture(item).response_payload_sha256,
        )
        for item in frozen
    )
    return canonical_sha256(payload)


def guard_real_case(case_id: str, phase: str, *, implementation_evidence_mode: bool) -> None:
    if case_id in REAL_CASE_IDS and implementation_evidence_mode:
        raise ValueError(f"real benchmark {phase} prohibited in implementation-evidence mode")
