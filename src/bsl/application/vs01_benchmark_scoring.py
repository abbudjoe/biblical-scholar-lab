from __future__ import annotations

import json
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from uuid import UUID

from uuid6 import uuid7

from bsl.application.vs01_benchmark import (
    ScorerCaseAuthority,
    StructuredSubjectResponse,
    SubjectCasePackage,
    _CaseAuthority,  # pyright: ignore[reportPrivateUsage]
    audit_subject_package,
    build_execution_specification,
    canonical_sha256,
    compile_reference_fixture,
    compile_scorer_authority,
    compile_subject_package,
    failed_case_result,
    guard_real_case,
    load_benchmark_authority,
)
from bsl.application.vs01_reference_subject import DeterministicReferenceSubjectAdapter
from bsl.contracts.benchmark import (
    VS01BenchmarkCaseResult,
    VS01BenchmarkExecutionReceipt,
    VS01BenchmarkExecutionSpecification,
    VS01BenchmarkRunResult,
)
from bsl.infrastructure.benchmark_store import (
    build_execution_receipt,
    canonical_run_result_bytes,
    implementation_head,
    publish_benchmark_result,
    verify_existing,
    verify_upstream_authority,
)

CANONICAL_ARCHIVE_ROOT = Path("/Volumes/BSL-Archive/BiblicalScholarLab")
NewUuid = Callable[[], UUID]
Now = Callable[[], datetime]


@dataclass(frozen=True)
class BenchmarkOperationLedger:
    replay_count: int = 0
    subject_invocations: int = 0
    scoring_invocations: int = 0
    case_results_constructed: int = 0
    run_results_constructed: int = 0
    receipts_constructed: int = 0
    publication_attempts: int = 0

    def add(self, **changes: int) -> BenchmarkOperationLedger:
        return replace(self, **{name: getattr(self, name) + value for name, value in changes.items()})


@dataclass(frozen=True)
class _SyntheticCaseResult:
    case_id: str
    attempt_state: str
    criterion_scores: tuple[tuple[str, int, int, int], ...]
    deterministic_checks: tuple[tuple[str, str, bool], ...]
    hard_failures: tuple[tuple[str, str, str], ...]
    raw_points: int
    capped_points: int
    case_disposition: str
    leakage_state: str = "CLEAR"


CaseResult = VS01BenchmarkCaseResult | _SyntheticCaseResult


def _facts(response: StructuredSubjectResponse) -> tuple[str, dict[str, Any]]:
    text = "\n".join(value for _, value in response.response_payload)
    structured: dict[str, Any] = {}
    for _name, value in response.response_payload:
        try:
            candidate = json.loads(value)
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict):
            structured.update(cast(dict[str, Any], candidate))
    return text, structured


def _check(kind: str, encoded: str, response: StructuredSubjectResponse, evidence: tuple[str, ...]) -> bool:
    rule = cast(dict[str, Any], json.loads(encoded))
    text, facts = _facts(response)
    if kind == "EXACT_STRING":
        return rule["value"] in text and ("source" not in rule or rule["source"] in text)
    if kind == "FORBIDDEN_STRING":
        return rule["value"] not in text
    if kind == "REQUIRED_SOURCE_HANDLE":
        return rule["value"] in text and rule["value"] in evidence
    if kind == "TEXT_QUOTE_SELECTOR":
        return rule["exact"] in text and f"{rule['prefix']}{rule['exact']}" in text
    if kind == "EXACT_FIELD":
        wording = {
            "third": "third-person",
            "singular": "singular",
            "aorist": "aorist",
            "active": "active",
            "indicative": "indicative",
        }
        expected = wording.get(rule["value"], rule["value"])
        return facts.get(rule["field"]) == rule["value"] or bool(expected and expected in text)
    if kind == "CLAIM_SOURCE_MAP":
        return facts.get("claims", {}).get(rule["claim"]) == rule["required_source"] or rule["required_source"] in text
    if kind == "ONLY_CANONICAL_QUOTE":
        return rule["value"] in text and facts.get("noncanonical_quoted", False) is False
    if kind in {"REGION_ROLE_MAP", "SESSION_STATE", "REQUIRED_EVENT"}:
        return _state_check(kind, rule, text, facts)
    raise ValueError(f"unsupported deterministic check type: {kind}")


def _state_check(kind: str, rule: dict[str, Any], text: str, facts: dict[str, Any]) -> bool:
    if kind == "SESSION_STATE":
        expected = rule.get("value", rule.get("contains"))
        return (
            facts.get("session_state", {}).get(rule["field"]) == expected
            or isinstance(expected, str)
            and expected in text
        )
    if kind == "REQUIRED_EVENT":
        return rule["value"] in facts.get("events", ()) or "later correction" in text
    labels = {
        "USER_ANNOTATION": "user annotation",
        "CANONICAL_TEXT": "Canonical Scripture",
        "CROSS_REFERENCE": "cross-reference",
        "PAGE_HEADER": "page header",
        "SECTION_HEADING": "section heading",
        "STUDY_NOTE_OR_FOOTNOTE": "study note",
        "VERSE_NUMBER": "verse-number",
    }
    return facts.get("region_roles") == rule["expected"] or all(
        labels[value] in text for value in rule["expected"].values()
    )


def _failure(scorer: ScorerCaseAuthority, index: int) -> tuple[str, str, str]:
    criterion, _weight, severity = scorer.criteria[min(index, len(scorer.criteria) - 1)]
    return criterion, severity or "HF-3_MATERIAL", "deterministic check failed"


def _synthetic_result(
    case: SubjectCasePackage, scorer: ScorerCaseAuthority, response: StructuredSubjectResponse
) -> _SyntheticCaseResult:
    try:
        audit_subject_package(case)
    except ValueError:
        return _SyntheticCaseResult(
            case.case_id,
            "INVALID_LEAKAGE_INCIDENT",
            (),
            (),
            (),
            0,
            0,
            "INVALID_LEAKAGE_INCIDENT",
            "INVALID_LEAKAGE_INCIDENT",
        )
    if response.attempt_state != "COMPLETED":
        scores = tuple((name, 0, weight, 0) for name, weight, _ in scorer.criteria)
        return _SyntheticCaseResult(
            case.case_id, response.attempt_state, scores, (), (), 0, 0, "REFERENCE_NONCONFORMANT_REPAIR_REQUIRED"
        )
    checks = tuple(
        (kind, value, _check(kind, value, response, scorer.evidence_references))
        for kind, value in scorer.deterministic_checks
    )
    failed = [index for index, item in enumerate(checks) if not item[2]]
    failures = tuple(_failure(scorer, index) for index in failed)
    failed_criteria = {min(index, len(scorer.criteria) - 1) for index in failed}
    scores = tuple(
        (name, 0 if index in failed_criteria else 2, weight, 0 if index in failed_criteria else 2 * weight)
        for index, (name, weight, _) in enumerate(scorer.criteria)
    )
    raw = sum(item[3] for item in scores)
    capped = 0 if any(item[1] != "HF-4_MINOR" for item in failures) else raw
    disposition = "REFERENCE_CONFORMANT" if not failures else "REFERENCE_NONCONFORMANT_REPAIR_REQUIRED"
    return _SyntheticCaseResult(case.case_id, "COMPLETED", scores, checks, failures, raw, capped, disposition)


def _public_result(
    case: SubjectCasePackage, scorer: ScorerCaseAuthority, response: StructuredSubjectResponse
) -> VS01BenchmarkCaseResult:
    audit_subject_package(case)
    exact = (
        response.case_id == case.case_id == scorer.case_id,
        response.source_declared_compatibility_sha256 == scorer.source_declared_compatibility_sha256,
        response.execution_rfc8785_jcs_sha256 == scorer.execution_rfc8785_jcs_sha256,
        response.subject_package_identity == case.package_identity,
        response.response_payload == scorer.reference_payload,
        response.response_payload_sha256
        == scorer.reference_payload_sha256
        == canonical_sha256(response.response_payload),
    )
    completed = response.attempt_state == "COMPLETED"
    checks = tuple(
        (kind, value, completed and _check(kind, value, response, scorer.evidence_references))
        for kind, value in scorer.deterministic_checks
    )
    conformant = all(exact) and all(item[2] for item in checks) and response.attempt_state == "COMPLETED"
    disposition = (
        "REFERENCE_CONFORMANT"
        if conformant
        else "UNSUPPORTED_SUBJECT_FOR_REFERENCE_SCORER"
        if response.attempt_state == "COMPLETED"
        else "REFERENCE_NONCONFORMANT_REPAIR_REQUIRED"
    )
    scores = tuple(
        (name, 2 if conformant else 0, weight, 2 * weight if conformant else 0) for name, weight, _ in scorer.criteria
    )
    payload: dict[str, Any] = {
        "case_id": case.case_id,
        "source_declared_compatibility_sha256": case.source_declared_compatibility_sha256,
        "execution_rfc8785_jcs_sha256": case.execution_rfc8785_jcs_sha256,
        "review_partition": scorer.review_partition,
        "subject_package_identity": case.package_identity,
        "response_identity": response.response_payload_sha256,
        "response_payload": response.response_payload,
        "attempt_state": response.attempt_state,
        "criterion_scores": scores,
        "deterministic_checks": checks,
        "hard_failures": (),
        "raw_points": sum(item[3] for item in scores),
        "capped_points": sum(item[3] for item in scores),
        "case_disposition": disposition,
        "leakage_state": "CLEAR",
        "error": response.attempt_state == "ERROR",
        "refusal": response.attempt_state == "REFUSAL",
        "timeout": response.attempt_state == "TIMEOUT",
        "malformed": response.attempt_state == "MALFORMED",
        "evidence_references": scorer.evidence_references,
    }
    draft = VS01BenchmarkCaseResult.model_construct(**payload, case_result_identity="0" * 64)
    payload["case_result_identity"] = canonical_sha256(draft.model_dump(mode="json", exclude={"case_result_identity"}))
    return VS01BenchmarkCaseResult.model_validate(payload)


def score_reference_case(
    case: SubjectCasePackage,
    scorer: ScorerCaseAuthority,
    response: StructuredSubjectResponse,
    *,
    implementation_evidence_mode: bool,
) -> CaseResult:
    guard_real_case(case.case_id, "scoring", implementation_evidence_mode=implementation_evidence_mode)
    return (
        _synthetic_result(case, scorer, response)
        if case.case_id.startswith("SYN-")
        else _public_result(case, scorer, response)
    )


def _failed_result(case: SubjectCasePackage, scorer: ScorerCaseAuthority) -> CaseResult:
    if not case.case_id.startswith("SYN-"):
        return failed_case_result(case, scorer, "ERROR")
    response = StructuredSubjectResponse(
        case.case_id,
        case.source_declared_compatibility_sha256,
        case.execution_rfc8785_jcs_sha256,
        case.package_identity,
        (),
        canonical_sha256(()),
        "ERROR",
    )
    return _synthetic_result(case, scorer, response)


def screening_disposition(
    *,
    p0_points: int,
    p1_points: int,
    total_points: int,
    every_case_minimum_met: bool,
    no_zero_criteria: bool,
    hf1_count: int,
    hf2_count: int,
    hf3_count: int,
    b09_passed: bool,
    b10_passed: bool,
    b11_correction_losses: int,
) -> str:
    hard_no_go = hf1_count > 0 or hf2_count > 0 or not b09_passed or not b10_passed or b11_correction_losses > 0
    if hard_no_go or not every_case_minimum_met or not no_zero_criteria:
        return "SCREENING_NO_GO"
    if hf3_count > 0:
        return "SCREENING_REVIEW_REQUIRED"
    if p0_points >= 58 and p1_points >= 45 and total_points >= 102:
        return "SCREENING_PASS_WITH_EXPLICIT_LIMITATIONS"
    return "SCREENING_NO_GO"


def meets_case_minimum(points: int, minimum: int) -> bool:
    return points >= minimum


def _run_result(
    specification: VS01BenchmarkExecutionSpecification,
    results: tuple[VS01BenchmarkCaseResult, ...],
    partitions: tuple[str, ...],
) -> VS01BenchmarkRunResult:
    p0 = sum(item.capped_points for item, part in zip(results, partitions, strict=True) if part.startswith("REV-P0"))
    p1 = sum(item.capped_points for item, part in zip(results, partitions, strict=True) if part.startswith("REV-P1"))
    failures = tuple(
        (name.lower(), sum(item.attempt_state == name for item in results))
        for name in ("ERROR", "REFUSAL", "TIMEOUT", "MALFORMED", "INVALID_LEAKAGE_INCIDENT")
    )
    hard = tuple(
        (name, sum(value[1] == name for item in results for value in item.hard_failures))
        for name in ("HF-1_CRITICAL", "HF-2_MAJOR", "HF-3_MATERIAL", "HF-4_MINOR")
    )
    conformant = all(item.case_disposition == "REFERENCE_CONFORMANT" for item in results)
    payload: dict[str, Any] = {
        "execution_specification_identity": specification.specification_identity,
        "case_results": results,
        "completed_attempts": sum(item.attempt_state == "COMPLETED" for item in results),
        "p0_points": p0,
        "p1_points": p1,
        "total_points": p0 + p1,
        "failure_counts": failures,
        "hard_failure_counts": hard,
        "special_outcomes": tuple(
            (name, results[index].case_disposition) for name, index in (("B09", 8), ("B10", 9), ("B11", 10))
        ),
        "contamination_limitation": "CHATGPT_AUTHORED_PUBLIC_SEED",
        "public_seed_limitation": "EL-1_SCREENING_ONLY",
        "b08_runtime_pair_limitation": "VS01-B08-RUNTIME-C01_REQUIRED_NOT_AUTHORED",
        "disposition": "REFERENCE_CONFORMANT" if conformant else "REFERENCE_NONCONFORMANT_REPAIR_REQUIRED",
    }
    draft = VS01BenchmarkRunResult.model_construct(**payload, run_result_identity="0" * 64)
    payload["run_result_identity"] = canonical_sha256(draft.model_dump(mode="json", exclude={"run_result_identity"}))
    return VS01BenchmarkRunResult.model_validate(payload)


def execute_reference_replay(
    authorities: tuple[_CaseAuthority, ...],
    specification: VS01BenchmarkExecutionSpecification,
    ledger: BenchmarkOperationLedger,
    *,
    implementation_evidence_mode: bool,
) -> tuple[VS01BenchmarkRunResult, BenchmarkOperationLedger]:
    results: list[CaseResult] = []
    current = ledger.add(replay_count=1)
    for authority in authorities:
        case, scorer, fixture = (
            compile_subject_package(authority),
            compile_scorer_authority(authority),
            compile_reference_fixture(authority),
        )
        current = current.add(subject_invocations=1)
        try:
            response = DeterministicReferenceSubjectAdapter(
                fixture, implementation_evidence_mode=implementation_evidence_mode
            ).generate(case)
            current = current.add(scoring_invocations=1)
            result = score_reference_case(
                case, scorer, response, implementation_evidence_mode=implementation_evidence_mode
            )
        except (OSError, ValueError, subprocess.SubprocessError):
            result = _failed_result(case, scorer)
        results.append(result)
        current = current.add(case_results_constructed=1)
    result = _run_result(
        specification,
        cast(tuple[VS01BenchmarkCaseResult, ...], tuple(results)),
        tuple(item.source["review_partition"] for item in authorities),
    )
    return result, current.add(run_results_constructed=1)


def _live_campaign(
    specification: VS01BenchmarkExecutionSpecification,
    result: VS01BenchmarkRunResult,
    archive_root: Path,
    ledger: BenchmarkOperationLedger,
    initial: tuple[tuple[str, str], ...],
    pre_store: tuple[tuple[str, str], ...],
    commit: str,
    new_uuid: NewUuid,
    now: Now,
) -> tuple[VS01BenchmarkExecutionReceipt, bool]:
    current = ledger.add(publication_attempts=1, receipts_constructed=1)
    expectation = {
        "implementation_commit": commit,
        "initial_upstream_fingerprints": initial,
        "pre_store_upstream_fingerprints": pre_store,
        **current.__dict__,
    }
    existing = verify_existing(archive_root, result, canonical_run_result_bytes(result), expectation)
    disposition = "VERIFIED_EXISTING" if existing is not None else "REFERENCE_CONFORMANT"
    receipt = build_execution_receipt(
        specification,
        result,
        archive_root,
        current.__dict__,
        initial,
        pre_store,
        disposition=disposition,
        implementation_commit=commit,
        new_uuid=new_uuid,
        now=now,
        retained=existing,
    )
    if existing is not None:
        return receipt, False
    publish_benchmark_result(archive_root, result, receipt)
    return receipt, True


def run_reference_campaign(
    *,
    dry_run: bool,
    archive_root: Path = CANONICAL_ARCHIVE_ROOT,
    implementation_evidence_mode: bool = False,
    _authorities: tuple[_CaseAuthority, ...] | None = None,
    _implementation_commit: str | None = None,
    _new_uuid: NewUuid = uuid7,
    _now: Now = lambda: datetime.now(UTC),
    _authority_loader: Callable[[Path], tuple[tuple[str, str], ...]] = verify_upstream_authority,
) -> tuple[VS01BenchmarkExecutionSpecification, VS01BenchmarkRunResult, VS01BenchmarkExecutionReceipt, bool]:
    authorities = _authorities or load_benchmark_authority()
    initial = _authority_loader(archive_root)
    specification = build_execution_specification(authorities, dry_run=dry_run)
    first, ledger = execute_reference_replay(
        authorities,
        specification,
        BenchmarkOperationLedger(),
        implementation_evidence_mode=implementation_evidence_mode,
    )
    second, ledger = execute_reference_replay(
        authorities, specification, ledger, implementation_evidence_mode=implementation_evidence_mode
    )
    if first.run_result_identity != second.run_result_identity:
        raise ValueError("deterministic benchmark replay identity differs")
    pre_store = _authority_loader(archive_root)
    if initial != pre_store:
        raise ValueError("benchmark upstream authority changed before store access")
    commit = _implementation_commit or implementation_head()
    if dry_run or first.disposition != "REFERENCE_CONFORMANT":
        disposition = "DRY_RUN_VALIDATED" if first.disposition == "REFERENCE_CONFORMANT" else "REFERENCE_NONCONFORMANT"
        receipt = build_execution_receipt(
            specification,
            first,
            archive_root,
            ledger.add(receipts_constructed=1).__dict__,
            initial,
            pre_store,
            disposition=disposition,
            implementation_commit=commit,
            new_uuid=_new_uuid,
            now=_now,
        )
        return specification, first, receipt, False
    receipt, published = _live_campaign(
        specification, first, archive_root, ledger, initial, pre_store, commit, _new_uuid, _now
    )
    return specification, first, receipt, published
