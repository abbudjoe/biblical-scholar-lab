from __future__ import annotations

import hashlib
import subprocess
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from uuid6 import uuid7

from bsl.application.vs01_benchmark import (
    ERRATUM_SHA256,
    PROTOCOL_SHA256,
    ScorerCaseAuthority,
    StructuredSubjectResponse,
    SubjectCasePackage,
    _CaseAuthority,  # pyright: ignore[reportPrivateUsage]
    audit_subject_package,
    canonical_sha256,
    compile_reference_fixture,
    compile_scorer_authority,
    compile_subject_package,
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
    canonical_run_result_bytes,
    publication_paths,
    publish_benchmark_result,
    verify_existing,
)

DESIGN_SHA256 = "d6e89b7db1bd686fb74bdc2530719a3c9e3d9a753983fac7a35bdd8be40abdf7"
ERRATUM_MARKDOWN_SHA256 = "8f3de652db50fc7a93d1368ac6ad53177f0f45858cad927b386127795dc3817d"
SCORER_REVISION = "VS01-T07-REFERENCE-CONFORMANCE-SCORER-v1"
CANONICAL_ARCHIVE_ROOT = Path("/Volumes/BSL-Archive/BiblicalScholarLab")
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
ADVERSARY_SEVERITIES = {
    "wrong canonical quotation": "HF-1_CRITICAL",
    "morphology-as-meaning": "HF-2_MAJOR",
    "edition-label swap": "HF-2_MAJOR",
    "translations-as-manuscript-witnesses": "HF-2_MAJOR",
    "illegitimate totality transfer": "HF-2_MAJOR",
    "false ‘literally both’ claim": "HF-2_MAJOR",
    "citation/source-role swap": "HF-2_MAJOR",
    "confident Greek claim from translations only": "HF-2_MAJOR",
    "study note as Scripture": "HF-2_MAJOR",
    "obscured phrase claimed visually read": "HF-1_CRITICAL",
    "stale WEB preference": "HF-2_MAJOR",
    "Brief mode hides uncertainty": "HF-2_MAJOR",
}
NewUuid = Callable[[], UUID]
Now = Callable[[], datetime]


def build_execution_specification(
    authorities: tuple[_CaseAuthority, ...], *, dry_run: bool
) -> VS01BenchmarkExecutionSpecification:
    projections = tuple((item.case_id, compile_subject_package(item).package_identity) for item in authorities)
    minimums = tuple((item.case_id, item.protocol["screening_case_pass_points"]) for item in authorities)
    payload: dict[str, Any] = {
        "batch_markdown_sha256": "f1f0be8a3be9b4f56de0968ad3f166306a4fdfbdd57e7a45a5d972bbb50b66ff",
        "batch_cases_sha256": "4241a0bf5baf50a12ce5fe6dcfef6ed5492cde410f3d92f5aad8a9f26ba3113f",
        "r01_design_sha256": DESIGN_SHA256,
        "r01_protocol_sha256": PROTOCOL_SHA256,
        "erratum_markdown_sha256": ERRATUM_MARKDOWN_SHA256,
        "erratum_json_sha256": ERRATUM_SHA256,
        "source_declared_compatibility_hashes": tuple(
            (item.case_id, item.compatibility_sha256) for item in authorities
        ),
        "execution_rfc8785_jcs_hashes": tuple(
            (item.case_id, item.execution_rfc8785_jcs_sha256) for item in authorities
        ),
        "case_order": tuple(item.case_id for item in authorities),
        "subject_projection_identities": projections,
        "scorer_revision": SCORER_REVISION,
        "upstream_authority": UPSTREAM_AUTHORITY,
        "isolation_policy": (
            "fresh subprocess per case",
            "case-local state only",
            "one attempt",
            "zero retries",
            "errors remain in denominator",
        ),
        "screening_case_minimums": minimums,
        "screening_partition_minimums": (("REV-P0", 58), ("REV-P1", 45), ("TOTAL", 102)),
        "b08_full_runtime_limitation": "VS01-B08-RUNTIME-C01_REQUIRED_NOT_AUTHORED",
        "execution_mode": "REFERENCE_CONFORMANCE_DRY_RUN" if dry_run else "REFERENCE_CONFORMANCE",
    }
    draft = VS01BenchmarkExecutionSpecification.model_construct(**payload, specification_identity="0" * 64)
    payload["specification_identity"] = canonical_sha256(
        draft.model_dump(mode="json", exclude={"specification_identity"})
    )
    return VS01BenchmarkExecutionSpecification.model_validate(payload)


def _case_result(payload: dict[str, Any]) -> VS01BenchmarkCaseResult:
    draft = VS01BenchmarkCaseResult.model_construct(**payload, case_result_identity="0" * 64)
    payload["case_result_identity"] = canonical_sha256(draft.model_dump(mode="json", exclude={"case_result_identity"}))
    return VS01BenchmarkCaseResult.model_validate(payload)


def _failed_case_result(
    case: SubjectCasePackage,
    scorer: ScorerCaseAuthority,
    state: str,
    disposition: str,
    *,
    leakage: bool = False,
) -> VS01BenchmarkCaseResult:
    scores = tuple((criterion_id, 0, weight, 0) for criterion_id, weight, _severity in scorer.criteria)
    return _case_result(
        {
            "case_id": case.case_id,
            "source_declared_compatibility_sha256": case.source_declared_compatibility_sha256,
            "execution_rfc8785_jcs_sha256": case.execution_rfc8785_jcs_sha256,
            "subject_package_identity": case.package_identity,
            "response_identity": "0" * 64,
            "response_payload": (),
            "attempt_state": state,
            "criterion_scores": scores,
            "deterministic_checks": tuple((kind, value, False) for kind, value in scorer.deterministic_checks),
            "hard_failures": (),
            "raw_points": 0,
            "capped_points": 0,
            "case_disposition": disposition,
            "leakage_state": "INVALID_LEAKAGE_INCIDENT" if leakage else "CLEAR",
            "error": state == "ERROR",
            "refusal": state == "REFUSAL",
            "timeout": state == "TIMEOUT",
            "malformed": state == "MALFORMED",
            "evidence_references": scorer.evidence_references,
        }
    )


def score_reference_case(
    case: SubjectCasePackage,
    scorer: ScorerCaseAuthority,
    response: StructuredSubjectResponse,
    *,
    implementation_evidence_mode: bool,
    synthetic_adversary: str | None = None,
    synthetic_severity: str | None = None,
) -> VS01BenchmarkCaseResult:
    guard_real_case(case.case_id, "scoring", implementation_evidence_mode=implementation_evidence_mode)
    try:
        audit_subject_package(case)
    except ValueError:
        return _failed_case_result(case, scorer, "INVALID_LEAKAGE_INCIDENT", "INVALID_LEAKAGE_INCIDENT", leakage=True)
    if response.attempt_state != "COMPLETED":
        return _failed_case_result(case, scorer, response.attempt_state, "REFERENCE_NONCONFORMANT_REPAIR_REQUIRED")
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
    if not all(exact) and synthetic_adversary is None:
        return _failed_case_result(case, scorer, "COMPLETED", "UNSUPPORTED_SUBJECT_FOR_REFERENCE_SCORER")
    if synthetic_adversary is not None and (
        not case.case_id.startswith("SYN-") or synthetic_adversary not in ADVERSARY_SEVERITIES
    ):
        raise ValueError("synthetic adversary is not authorized")
    scores = [(criterion_id, 2, weight, 2 * weight) for criterion_id, weight, _severity in scorer.criteria]
    failures: tuple[tuple[str, str, str], ...] = ()
    if synthetic_adversary is not None:
        criterion_id, _score, weight, _points = scores[0]
        scores[0] = criterion_id, 0, weight, 0
        severity = synthetic_severity or ADVERSARY_SEVERITIES[synthetic_adversary]
        failures = ((f"SYN-{criterion_id}", severity, synthetic_adversary),)
    raw = sum(item[3] for item in scores)
    capped = raw if not failures or failures[0][1] == "HF-4_MINOR" else 0
    disposition = "REFERENCE_CONFORMANT" if not failures else "REFERENCE_NONCONFORMANT_REPAIR_REQUIRED"
    return _completed_case_result(case, scorer, response, scores, failures, raw, capped, disposition)


def _completed_case_result(
    case: SubjectCasePackage,
    scorer: ScorerCaseAuthority,
    response: StructuredSubjectResponse,
    scores: list[tuple[str, int, int, int]],
    failures: tuple[tuple[str, str, str], ...],
    raw: int,
    capped: int,
    disposition: str,
) -> VS01BenchmarkCaseResult:
    return _case_result(
        {
            "case_id": case.case_id,
            "source_declared_compatibility_sha256": case.source_declared_compatibility_sha256,
            "execution_rfc8785_jcs_sha256": case.execution_rfc8785_jcs_sha256,
            "subject_package_identity": case.package_identity,
            "response_identity": response.response_payload_sha256,
            "response_payload": response.response_payload,
            "attempt_state": "COMPLETED",
            "criterion_scores": tuple(scores),
            "deterministic_checks": tuple((kind, value, not failures) for kind, value in scorer.deterministic_checks),
            "hard_failures": failures,
            "raw_points": raw,
            "capped_points": capped,
            "case_disposition": disposition,
            "leakage_state": "CLEAR",
            "error": False,
            "refusal": False,
            "timeout": False,
            "malformed": False,
            "evidence_references": scorer.evidence_references,
        }
    )


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
    *,
    archive_writes: int = 0,
) -> VS01BenchmarkRunResult:
    p0 = sum(
        item.capped_points
        for item, partition in zip(results, partitions, strict=True)
        if partition.startswith("REV-P0")
    )
    p1 = sum(
        item.capped_points
        for item, partition in zip(results, partitions, strict=True)
        if partition.startswith("REV-P1")
    )
    failure_names = ("ERROR", "REFUSAL", "TIMEOUT", "MALFORMED", "INVALID_LEAKAGE_INCIDENT")
    failure_counts = tuple(
        (name.lower(), sum(item.attempt_state == name for item in results)) for name in failure_names
    )
    severities = ("HF-1_CRITICAL", "HF-2_MAJOR", "HF-3_MATERIAL", "HF-4_MINOR")
    hard_counts = tuple(
        (name, sum(failure[1] == name for item in results for failure in item.hard_failures)) for name in severities
    )
    conformant = p0 == 64 and p1 == 56 and all(item.case_disposition == "REFERENCE_CONFORMANT" for item in results)
    payload: dict[str, Any] = {
        "execution_specification_identity": specification.specification_identity,
        "case_results": results,
        "completed_attempts": sum(item.attempt_state == "COMPLETED" for item in results),
        "p0_points": p0,
        "p1_points": p1,
        "total_points": p0 + p1,
        "failure_counts": failure_counts,
        "hard_failure_counts": hard_counts,
        "special_outcomes": (
            ("B09", results[8].case_disposition),
            ("B10", results[9].case_disposition),
            ("B11", results[10].case_disposition),
        ),
        "contamination_limitation": "CHATGPT_AUTHORED_PUBLIC_SEED",
        "public_seed_limitation": "EL-1_SCREENING_ONLY",
        "b08_runtime_pair_limitation": "VS01-B08-RUNTIME-C01_REQUIRED_NOT_AUTHORED",
        "disposition": "REFERENCE_CONFORMANT" if conformant else "REFERENCE_NONCONFORMANT_REPAIR_REQUIRED",
        "archive_writes": archive_writes,
    }
    draft = VS01BenchmarkRunResult.model_construct(**payload, run_result_identity="0" * 64)
    payload["run_result_identity"] = canonical_sha256(draft.model_dump(mode="json", exclude={"run_result_identity"}))
    return VS01BenchmarkRunResult.model_validate(payload)


def execute_reference_replay(
    authorities: tuple[_CaseAuthority, ...],
    specification: VS01BenchmarkExecutionSpecification,
    *,
    implementation_evidence_mode: bool,
) -> VS01BenchmarkRunResult:
    results: list[VS01BenchmarkCaseResult] = []
    for authority in authorities:
        case = compile_subject_package(authority)
        scorer = compile_scorer_authority(authority)
        fixture = compile_reference_fixture(authority)
        try:
            response = DeterministicReferenceSubjectAdapter(
                fixture, implementation_evidence_mode=implementation_evidence_mode
            ).generate(case)
            result = score_reference_case(
                case, scorer, response, implementation_evidence_mode=implementation_evidence_mode
            )
        except ValueError:
            result = _failed_case_result(case, scorer, "ERROR", "REFERENCE_NONCONFORMANT_REPAIR_REQUIRED")
        results.append(result)
    partitions = tuple(item.source["review_partition"] for item in authorities)
    return _run_result(specification, tuple(results), partitions)


def _git_head() -> str:
    completed = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True, timeout=10)
    head = completed.stdout.strip()
    if len(head) != 40 or any(character not in "0123456789abcdef" for character in head):
        raise ValueError("implementation commit is invalid")
    return head


def verify_upstream_authority(root: Path) -> tuple[tuple[str, str], ...]:
    from bsl.application.john15_page_fixture import (
        _fixture_assets,  # pyright: ignore[reportPrivateUsage]
        verify_t05_owner,
    )
    from bsl.application.john15_study_runtime import (
        _authority_fingerprint,  # pyright: ignore[reportPrivateUsage]
        load_t04_authority,
    )
    from bsl.infrastructure.page_fixture_store import verify_existing as verify_page_fixture

    t04 = load_t04_authority(root)
    t05 = verify_t05_owner(t04)
    fixture, base, degraded, fixture_bytes = _fixture_assets()
    t06 = verify_page_fixture(root, fixture, base, degraded, fixture_bytes)
    if t06 is None or str(t06.receipt_identity) != "01a034c2-d6e4-73f4-91b2-7410e7453783":
        raise ValueError("canonical T06 authority differs")
    return (
        ("t04", _authority_fingerprint(t04)),
        ("t05", canonical_sha256(t05)),
        ("t06", canonical_sha256(t06.model_dump(mode="json"))),
    )


def _receipt(
    specification: VS01BenchmarkExecutionSpecification,
    result: VS01BenchmarkRunResult,
    root: Path,
    *,
    dry_run: bool,
    implementation_commit: str,
    new_uuid: NewUuid,
    now: Now,
    upstream_fingerprints: tuple[tuple[str, str], ...] | None = None,
) -> VS01BenchmarkExecutionReceipt:
    result_sha = hashlib.sha256(canonical_run_result_bytes(result)).hexdigest()
    conformant = result.disposition == "REFERENCE_CONFORMANT"
    disposition = (
        "DRY_RUN_VALIDATED"
        if dry_run and conformant
        else "REFERENCE_CONFORMANT"
        if conformant
        else "REFERENCE_NONCONFORMANT"
    )
    return VS01BenchmarkExecutionReceipt(
        receipt_id=new_uuid(),
        generated_at=now(),
        execution_specification_identity=specification.specification_identity,
        run_result_identity=result.run_result_identity,
        run_result_file_sha256=result_sha,
        implementation_commit=implementation_commit,
        archive_root=str(root),
        archive_paths=publication_paths(result_sha),
        disposition=disposition,
        dry_run=dry_run,
        published=not dry_run and conformant,
        verified_existing=False,
        upstream_fingerprints=upstream_fingerprints or (("combined", canonical_sha256(UPSTREAM_AUTHORITY)),),
        completed_attempts=result.completed_attempts,
        error_counts=result.failure_counts,
        archive_writes=3 if not dry_run and conformant else 0,
    )


def run_reference_campaign(
    *,
    dry_run: bool,
    archive_root: Path = CANONICAL_ARCHIVE_ROOT,
    implementation_evidence_mode: bool = False,
    _authorities: tuple[_CaseAuthority, ...] | None = None,
    _implementation_commit: str | None = None,
    _new_uuid: NewUuid = uuid7,
    _now: Now = lambda: datetime.now(UTC),
) -> tuple[VS01BenchmarkExecutionSpecification, VS01BenchmarkRunResult, VS01BenchmarkExecutionReceipt, bool]:
    authorities = _authorities or load_benchmark_authority()
    upstream_fingerprints = None if _authorities is not None else verify_upstream_authority(archive_root)
    specification = build_execution_specification(authorities, dry_run=dry_run)
    first = execute_reference_replay(
        authorities, specification, implementation_evidence_mode=implementation_evidence_mode
    )
    second = execute_reference_replay(
        authorities, specification, implementation_evidence_mode=implementation_evidence_mode
    )
    if first.run_result_identity != second.run_result_identity:
        raise ValueError("deterministic benchmark replay identity differs")
    receipt = _receipt(
        specification,
        first,
        archive_root,
        dry_run=dry_run,
        implementation_commit=_implementation_commit or _git_head(),
        new_uuid=_new_uuid,
        now=_now,
        upstream_fingerprints=upstream_fingerprints,
    )
    if dry_run or first.disposition != "REFERENCE_CONFORMANT":
        return specification, first, receipt, False
    result_bytes = canonical_run_result_bytes(first)
    existing = verify_existing(archive_root, first, result_bytes)
    if existing is not None:
        return specification, first, existing, False
    publish_benchmark_result(archive_root, first, receipt)
    return specification, first, receipt, True
