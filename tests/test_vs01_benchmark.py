# pyright: reportPrivateUsage=false
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import os
import subprocess
import sys
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
from pydantic import ValidationError
from uuid6 import uuid7

import bsl.application.vs01_benchmark as benchmark
import bsl.application.vs01_benchmark_scoring as scoring
import bsl.application.vs01_reference_subject as reference_subject
import bsl.infrastructure.benchmark_store as store
from bsl.application.vs01_benchmark import (
    ReferenceSubjectFixture,
    ScorerCaseAuthority,
    StructuredSubjectResponse,
    SubjectCasePackage,
)
from bsl.application.vs01_reference_subject import DeterministicReferenceSubjectAdapter
from bsl.contracts.benchmark import (
    CASE_IDS,
    PARTITIONS,
    VS01BenchmarkCaseResult,
    VS01BenchmarkExecutionReceipt,
    VS01BenchmarkExecutionSpecification,
    VS01BenchmarkRunResult,
)

ROOT = Path(__file__).parents[1]


def _synthetic(
    index: int,
    check: tuple[str, dict[str, Any]] | None = None,
    severity: str = "HF-2_MAJOR",
) -> tuple[SubjectCasePackage, ScorerCaseAuthority, ReferenceSubjectFixture]:
    case_id = f"SYN-T07-CASE-{index:02d}"
    digest = benchmark.canonical_sha256((case_id, "private synthetic authority"))
    package_data = {
        "case_id": case_id,
        "source_declared_compatibility_sha256": digest,
        "execution_rfc8785_jcs_sha256": digest,
        "prompt_fields": (("prompt", f"Synthetic non-benchmark prompt {index}"),),
        "evaluation_mode": "SYNTHETIC",
        "answer_mode": "BRIEF",
        "evidence_contract_id": "SYNTHETIC-EVIDENCE",
        "whitelisted_source_handles": ("SYN-SOURCE",),
        "authorized_raster_sha256": None,
        "deterministic_tool_interfaces": (),
        "response_fields": ("answer",),
        "case_local_budgets": (("attempts", 1), ("retries", 0), ("semantic_rerolls", 0)),
    }
    case = SubjectCasePackage(**cast(Any, package_data), package_identity=benchmark.canonical_sha256(package_data))
    response = (("answer", '{"value":"safe"}'),)
    checks = () if check is None else ((check[0], json.dumps(check[1], sort_keys=True, separators=(",", ":"))),)
    scorer_data = {
        "case_id": case_id,
        "source_declared_compatibility_sha256": digest,
        "execution_rfc8785_jcs_sha256": digest,
        "reference_payload": response,
        "reference_payload_sha256": benchmark.canonical_sha256(response),
        "deterministic_checks": checks,
        "criteria": ((f"SYN-R{index}", 1, severity),),
        "evidence_references": ("SYN-SOURCE",),
        "review_partition": "SYNTHETIC",
    }
    scorer = ScorerCaseAuthority(**cast(Any, scorer_data), scorer_plan_identity=benchmark.canonical_sha256(scorer_data))
    fixture = ReferenceSubjectFixture(case_id, digest, digest, "BRIEF", response, scorer.reference_payload_sha256)
    return case, scorer, fixture


def _response(case: SubjectCasePackage, value: str, state: str = "COMPLETED") -> StructuredSubjectResponse:
    payload = (("answer", value),)
    return StructuredSubjectResponse(
        case.case_id,
        case.source_declared_compatibility_sha256,
        case.execution_rfc8785_jcs_sha256,
        case.package_identity,
        payload,
        benchmark.canonical_sha256(payload),
        state,
    )


def _spec(dry_run: bool = False) -> VS01BenchmarkExecutionSpecification:
    return benchmark.build_execution_specification(benchmark.load_benchmark_authority(), dry_run=dry_run)


def _case(index: int) -> VS01BenchmarkCaseResult:
    authority = benchmark.load_benchmark_authority()[index]
    package, scorer, fixture = (
        benchmark.compile_subject_package(authority),
        benchmark.compile_scorer_authority(authority),
        benchmark.compile_reference_fixture(authority),
    )
    scores = tuple((name, 2, weight, 2 * weight) for name, weight, _ in scorer.criteria)
    payload: dict[str, Any] = {
        "case_id": authority.case_id,
        "source_declared_compatibility_sha256": authority.compatibility_sha256,
        "execution_rfc8785_jcs_sha256": authority.execution_rfc8785_jcs_sha256,
        "review_partition": scorer.review_partition,
        "subject_package_identity": package.package_identity,
        "response_identity": fixture.response_payload_sha256,
        "response_payload": fixture.response_payload,
        "attempt_state": "COMPLETED",
        "criterion_scores": scores,
        "deterministic_checks": tuple((kind, value, True) for kind, value in scorer.deterministic_checks),
        "hard_failures": (),
        "raw_points": sum(item[3] for item in scores),
        "capped_points": sum(item[3] for item in scores),
        "case_disposition": "REFERENCE_CONFORMANT",
        "leakage_state": "CLEAR",
        "error": False,
        "refusal": False,
        "timeout": False,
        "malformed": False,
        "evidence_references": scorer.evidence_references,
    }
    draft = VS01BenchmarkCaseResult.model_construct(**payload, case_result_identity="0" * 64)
    payload["case_result_identity"] = benchmark.canonical_sha256(
        draft.model_dump(mode="json", exclude={"case_result_identity"})
    )
    return VS01BenchmarkCaseResult.model_validate(payload)


def _run(dry_run: bool = False) -> VS01BenchmarkRunResult:
    return scoring._run_result(_spec(dry_run), tuple(_case(index) for index in range(12)), PARTITIONS)


def _fingerprints() -> tuple[tuple[str, str], ...]:
    return tuple(
        (name, benchmark.canonical_sha256(name)) for name in ("t04", "t05", "t06", "archive_root", "incoming_inventory")
    )


def _receipt(root: Path, result: VS01BenchmarkRunResult) -> VS01BenchmarkExecutionReceipt:
    ledger = scoring.BenchmarkOperationLedger(2, 24, 24, 24, 2, 1, 1)
    return store.build_execution_receipt(
        _spec(),
        result,
        root,
        ledger.__dict__,
        _fingerprints(),
        _fingerprints(),
        disposition="REFERENCE_CONFORMANT",
        implementation_commit="1" * 40,
        new_uuid=uuid7,
        now=lambda: datetime.now(UTC),
    )


def test_real_authority_static_compilation_dual_hash_and_fixtures() -> None:
    authorities = benchmark.load_benchmark_authority()
    matrix = benchmark.compatibility_hash_matrix(authorities)
    assert len(authorities) == 12 and [item[0] for item in matrix] == list(CASE_IDS)
    assert [item[0] for item in matrix if item[1] != item[2]] == ["VS01-B10-C01"]
    assert matrix[9][1:] == (benchmark.B10_COMPATIBILITY_SHA256, benchmark.B10_JCS_SHA256)
    assert benchmark.static_compilation_identity(authorities) == benchmark.static_compilation_identity(authorities)
    generated = benchmark.generated_fixture_bytes(authorities)
    assert generated == benchmark.generated_fixture_bytes(authorities)
    assert generated == tuple(
        (ROOT / path).read_bytes()
        for path in (
            "fixtures/VS01-T07/reference-subject-responses.json",
            "fixtures/VS01-T07/subject-projection-manifest.json",
        )
    )
    with pytest.raises(ValueError, match="prohibited"):
        benchmark.guard_real_case(CASE_IDS[0], "subject", implementation_evidence_mode=True)


def test_check_inventory_closed_and_special_projection_firewall() -> None:
    authorities = benchmark.load_benchmark_authority()
    observed = {
        kind for item in authorities for kind, _ in benchmark.compile_scorer_authority(item).deterministic_checks
    }
    assert observed == set(benchmark.CHECK_FIELDS)
    changed = dict(authorities[0].source) | {"deterministic_checks": [{"type": "UNKNOWN"}]}
    with pytest.raises(ValueError, match="unsupported deterministic"):
        benchmark.compile_scorer_authority(replace(authorities[0], source=changed))
    packages = {item.case_id: benchmark.compile_subject_package(item) for item in authorities}
    assert packages[CASE_IDS[7]].deterministic_tool_interfaces == ()
    assert packages[CASE_IDS[8]].authorized_raster_sha256 == benchmark.BASE_RASTER_SHA256
    assert packages[CASE_IDS[9]].authorized_raster_sha256 == benchmark.DEGRADED_RASTER_SHA256
    assert "Correction: use the ASV" in packages[CASE_IDS[10]].prompt_fields[2][1]
    assert packages[CASE_IDS[11]].response_fields == ("brief", "study")
    assert set(SubjectCasePackage.__dataclass_fields__).isdisjoint(benchmark.FORBIDDEN_SUBJECT_FIELDS)


def test_child_source_wire_argv_environment_and_two_processes(monkeypatch: pytest.MonkeyPatch) -> None:
    assert {"hashlib", "json", "sys"} == reference_subject.CHILD_IMPORTS
    names = {node.id for node in ast.walk(ast.parse(reference_subject.CHILD_SOURCE)) if isinstance(node, ast.Name)}
    assert names.isdisjoint({"bsl", "pathlib", "os", "subprocess", "socket", "importlib", "site"})
    seen: list[tuple[list[str], dict[str, str], dict[str, Any]]] = []
    original = reference_subject.subprocess.run

    def inspect_run(argv: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        seen.append((argv, kwargs["env"], json.loads(kwargs["input"])))
        return cast(subprocess.CompletedProcess[bytes], original(argv, **kwargs))

    monkeypatch.setattr(reference_subject.subprocess, "run", inspect_run)
    for index in (1, 2):
        case, _scorer, fixture = _synthetic(index)
        assert (
            DeterministicReferenceSubjectAdapter(fixture, implementation_evidence_mode=True).generate(case).case_id
            == case.case_id
        )
    for argv, environment, request in seen:
        assert argv[1:5] == ["-I", "-S", "-X", "utf8"]
        assert environment == {"PYTHONUTF8": "1", "LC_ALL": "C.UTF-8"}
        assert set(request) == {
            "case_id",
            "source_declared_compatibility_sha256",
            "execution_rfc8785_jcs_sha256",
            "subject_package_identity",
            "response_field_names",
            "oracle_response_payload",
            "oracle_response_payload_sha256",
        }
        assert not any("path" in key or "module" in key for key in request)


def test_child_rejects_malformed_and_mismatched_wire(tmp_path: Path) -> None:
    script = tmp_path / "child.py"
    script.write_text(reference_subject.CHILD_SOURCE)
    completed = subprocess.run(
        [sys.executable, "-I", "-S", "-X", "utf8", str(script)], input=b"{}", capture_output=True, check=False
    )
    assert completed.returncode == 2
    case, _scorer, fixture = _synthetic(1)
    with pytest.raises(ValueError, match="identity differs"):
        reference_subject._request(case, replace(fixture, response_payload_sha256="0" * 64))


ADVERSARIES = (
    ("wrong canonical quotation", "EXACT_STRING", {"value": "canonical quotation"}, "wrong quotation"),
    ("morphology-as-meaning", "EXACT_FIELD", {"field": "morphology", "value": "aorist"}, '{"morphology":"present"}'),
    ("edition-label swap", "EXACT_STRING", {"value": "ASV"}, "WEB edition"),
    (
        "translations-as-manuscript-witnesses",
        "FORBIDDEN_STRING",
        {"value": "translations prove manuscripts"},
        "translations prove manuscripts",
    ),
    ("illegitimate totality transfer", "FORBIDDEN_STRING", {"value": "every gloss applies"}, "every gloss applies"),
    ("false literally both claim", "FORBIDDEN_STRING", {"value": "literally both"}, "literally both"),
    (
        "citation/source-role swap",
        "CLAIM_SOURCE_MAP",
        {"claim": "quotation", "required_source": "SYN-SOURCE"},
        '{"claims":{"quotation":"WRONG"}}',
    ),
    (
        "confident Greek claim from translations only",
        "FORBIDDEN_STRING",
        {"value": "Greek certainly means"},
        "Greek certainly means",
    ),
    ("study note as Scripture", "FORBIDDEN_STRING", {"value": "note is Scripture"}, "note is Scripture"),
    (
        "obscured phrase claimed visually read",
        "FORBIDDEN_STRING",
        {"value": "visually read obscured"},
        "visually read obscured",
    ),
    (
        "stale WEB preference",
        "SESSION_STATE",
        {"field": "primary_translation", "value": "ASV"},
        '{"session_state":{"primary_translation":"WEB"}}',
    ),
    (
        "Brief mode hides uncertainty",
        "EXACT_FIELD",
        {"field": "uncertainty", "value": "explicit"},
        '{"uncertainty":"hidden"}',
    ),
)

CHECK_CONTROLS = (
    ("EXACT_STRING", {"value": "required"}, "required", "missing"),
    ("FORBIDDEN_STRING", {"value": "forbidden"}, "safe", "forbidden"),
    ("REQUIRED_SOURCE_HANDLE", {"value": "SYN-SOURCE"}, "SYN-SOURCE", "missing"),
    ("TEXT_QUOTE_SELECTOR", {"prefix": "alpha ", "exact": "omega"}, "alpha omega", "omega"),
    ("EXACT_FIELD", {"field": "lemma", "value": "target"}, '{"lemma":"target"}', '{"lemma":"wrong"}'),
    (
        "CLAIM_SOURCE_MAP",
        {"claim": "claim", "required_source": "SYN-SOURCE"},
        '{"claims":{"claim":"SYN-SOURCE"}}',
        '{"claims":{"claim":"WRONG"}}',
    ),
    (
        "REGION_ROLE_MAP",
        {"expected": {"r_note": "STUDY_NOTE_OR_FOOTNOTE"}},
        '{"region_roles":{"r_note":"STUDY_NOTE_OR_FOOTNOTE"}}',
        '{"region_roles":{"r_note":"CANONICAL_TEXT"}}',
    ),
    (
        "ONLY_CANONICAL_QUOTE",
        {"value": "verse"},
        '{"noncanonical_quoted":false,"quote":"verse"}',
        '{"noncanonical_quoted":true,"quote":"verse"}',
    ),
    (
        "SESSION_STATE",
        {"field": "primary_translation", "value": "ASV"},
        '{"session_state":{"primary_translation":"ASV"}}',
        '{"session_state":{"primary_translation":"WEB"}}',
    ),
    ("REQUIRED_EVENT", {"value": "correction"}, '{"events":["correction"]}', '{"events":[]}'),
)


@pytest.mark.parametrize(("category", "kind", "rule", "mutation"), ADVERSARIES)
def test_twelve_mutated_data_controls(category: str, kind: str, rule: dict[str, Any], mutation: str) -> None:
    del category
    case, scorer, _fixture = _synthetic(1, (kind, rule))
    good = json.dumps(
        {
            rule.get("field", "value"): rule.get("value", "safe"),
            "claims": {rule.get("claim", "none"): rule.get("required_source", "none")},
            "session_state": {rule.get("field", "none"): rule.get("value", "none")},
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    if kind == "FORBIDDEN_STRING":
        good = '{"value":"safe"}'
    if kind == "EXACT_STRING":
        good += str(rule["value"])
    failed = scoring.score_reference_case(case, scorer, _response(case, mutation), implementation_evidence_mode=True)
    passed = scoring.score_reference_case(case, scorer, _response(case, good), implementation_evidence_mode=True)
    assert failed.hard_failures == (("SYN-R1", "HF-2_MAJOR", "deterministic check failed"),)
    assert failed.case_disposition == "REFERENCE_NONCONFORMANT_REPAIR_REQUIRED"
    assert passed.case_disposition == "REFERENCE_CONFORMANT"


@pytest.mark.parametrize(("kind", "rule", "passing", "failing"), CHECK_CONTROLS)
def test_every_frozen_check_type_reads_synthetic_data(
    kind: str, rule: dict[str, Any], passing: str, failing: str
) -> None:
    case, scorer, _ = _synthetic(1, (kind, rule))
    outcomes = tuple(
        scoring.score_reference_case(case, scorer, _response(case, value), implementation_evidence_mode=True)
        for value in (passing, failing)
    )
    assert tuple(item.case_disposition for item in outcomes) == (
        "REFERENCE_CONFORMANT",
        "REFERENCE_NONCONFORMANT_REPAIR_REQUIRED",
    )


def test_no_answer_key_parameters_hard_failure_precedence_and_leakage() -> None:
    assert {"synthetic_adversary", "synthetic_severity", "failed_criterion"}.isdisjoint(
        inspect.signature(scoring.score_reference_case).parameters
    )
    for severity, cap in (("HF-1_CRITICAL", 0), ("HF-2_MAJOR", 0), ("HF-3_MATERIAL", 0), ("HF-4_MINOR", 0)):
        case, scorer, _ = _synthetic(1, ("EXACT_STRING", {"value": "required"}), severity)
        result = scoring.score_reference_case(
            case, scorer, _response(case, "missing"), implementation_evidence_mode=True
        )
        assert result.capped_points == cap and result.hard_failures[0][1] == severity
    case, scorer, fixture = _synthetic(1)
    changed: dict[str, Any] = case.payload() | {"whitelisted_source_handles": ("/tmp/private",)}
    changed["package_identity"] = benchmark.canonical_sha256(
        {key: value for key, value in changed.items() if key != "package_identity"}
    )
    result = scoring.score_reference_case(
        SubjectCasePackage(**cast(Any, changed)),
        scorer,
        _response(case, fixture.response_payload[0][1]),
        implementation_evidence_mode=True,
    )
    assert result.attempt_state == result.leakage_state == result.case_disposition == "INVALID_LEAKAGE_INCIDENT"


@pytest.mark.parametrize(
    ("field", "below", "at"), (("p0_points", 57, 58), ("p1_points", 44, 45), ("total_points", 101, 102))
)
def test_every_screening_threshold_boundary(field: str, below: int, at: int) -> None:
    values = {"p0_points": 58, "p1_points": 45, "total_points": 102}
    policy = {
        "every_case_minimum_met": True,
        "no_zero_criteria": True,
        "hf1_count": 0,
        "hf2_count": 0,
        "hf3_count": 0,
        "b09_passed": True,
        "b10_passed": True,
        "b11_correction_losses": 0,
    }
    assert scoring.screening_disposition(**cast(Any, values | {field: below}), **cast(Any, policy)) == "SCREENING_NO_GO"
    assert (
        scoring.screening_disposition(**cast(Any, values | {field: at}), **cast(Any, policy))
        == "SCREENING_PASS_WITH_EXPLICIT_LIMITATIONS"
    )


def test_screening_hard_failure_and_material_review_precedence() -> None:
    policy = {
        "p0_points": 64,
        "p1_points": 56,
        "total_points": 120,
        "every_case_minimum_met": True,
        "no_zero_criteria": True,
        "hf2_count": 0,
        "b09_passed": True,
        "b10_passed": True,
        "b11_correction_losses": 0,
    }
    assert scoring.screening_disposition(**cast(Any, policy), hf1_count=1, hf3_count=0) == "SCREENING_NO_GO"
    assert scoring.screening_disposition(**cast(Any, policy), hf1_count=0, hf3_count=1) == "SCREENING_REVIEW_REQUIRED"


@pytest.mark.parametrize("minimum", (5, 8, 5, 10, 8, 12, 10, 7, 8, 8, 8, 10))
def test_every_case_threshold_immediately_below_and_at_gate(minimum: int) -> None:
    assert not scoring.meets_case_minimum(minimum - 1, minimum)
    assert scoring.meets_case_minimum(minimum, minimum)


def test_operation_ledger_observes_two_synthetic_replays(monkeypatch: pytest.MonkeyPatch) -> None:
    records = tuple(
        SimpleNamespace(case_id=f"SYN-T07-CASE-{index:02d}", source={"review_partition": "SYN"})
        for index in range(1, 13)
    )
    values = {item.case_id: _synthetic(index) for index, item in enumerate(records, 1)}

    def subject(item: Any) -> Any:
        return values[item.case_id][0]

    def scorer(item: Any) -> Any:
        return values[item.case_id][1]

    def fixture(item: Any) -> Any:
        return values[item.case_id][2]

    def run_result(_spec: Any, results: tuple[Any, ...], _parts: Any) -> Any:
        identity = benchmark.canonical_sha256(tuple((item.case_id, item.criterion_scores) for item in results))
        return SimpleNamespace(run_result_identity=identity)

    monkeypatch.setattr(scoring, "compile_subject_package", subject)
    monkeypatch.setattr(scoring, "compile_scorer_authority", scorer)
    monkeypatch.setattr(scoring, "compile_reference_fixture", fixture)
    monkeypatch.setattr(scoring, "_run_result", run_result)
    ledger = scoring.BenchmarkOperationLedger()
    identities: list[str] = []
    for _ in range(2):
        result, ledger = scoring.execute_reference_replay(
            cast(Any, records), cast(Any, object()), ledger, implementation_evidence_mode=True
        )
        identities.append(result.run_result_identity)
    assert identities[0] == identities[1]
    assert ledger == scoring.BenchmarkOperationLedger(2, 24, 24, 24, 2, 0, 0)


def test_subject_error_remains_in_synthetic_denominator(monkeypatch: pytest.MonkeyPatch) -> None:
    records = (SimpleNamespace(case_id="SYN-T07-CASE-01", source={"review_partition": "SYN"}),)
    case, scorer, fixture = _synthetic(1)

    def package(_item: Any) -> SubjectCasePackage:
        return case

    def authority(_item: Any) -> ScorerCaseAuthority:
        return scorer

    def oracle(_item: Any) -> ReferenceSubjectFixture:
        return fixture

    def fail(_adapter: Any, _case: Any) -> StructuredSubjectResponse:
        raise OSError

    monkeypatch.setattr(scoring, "compile_subject_package", package)
    monkeypatch.setattr(scoring, "compile_scorer_authority", authority)
    monkeypatch.setattr(scoring, "compile_reference_fixture", oracle)
    monkeypatch.setattr(DeterministicReferenceSubjectAdapter, "generate", fail)

    def observed(_spec: Any, results: tuple[Any, ...], _parts: Any) -> Any:
        assert results[0].attempt_state == "ERROR"
        return SimpleNamespace(run_result_identity="error-retained")

    monkeypatch.setattr(scoring, "_run_result", observed)
    _result, ledger = scoring.execute_reference_replay(
        cast(Any, records), cast(Any, object()), scoring.BenchmarkOperationLedger(), implementation_evidence_mode=True
    )
    assert (ledger.subject_invocations, ledger.scoring_invocations, ledger.case_results_constructed) == (1, 0, 1)


@pytest.mark.parametrize(
    "field",
    (
        "source_declared_compatibility_sha256",
        "subject_package_identity",
        "response_payload",
        "criterion_scores",
        "deterministic_checks",
        "evidence_references",
        "review_partition",
    ),
)
def test_case_contract_rejects_recomputed_authority_mutation(field: str) -> None:
    payload = _case(0).model_dump(mode="python")
    mutations = {
        "source_declared_compatibility_sha256": "0" * 64,
        "subject_package_identity": "0" * 64,
        "response_payload": (("answer", "mutated response"),),
        "criterion_scores": (("WRONG", 2, 2, 4),) + payload["criterion_scores"][1:],
        "deterministic_checks": (("WRONG", "{}", True),) + payload["deterministic_checks"][1:],
        "evidence_references": ("WRONG",),
        "review_partition": "REV-P1_SOURCE_VERIFIABLE_SCHOLARLY_BEHAVIOR",
    }
    payload[field] = mutations[field]
    payload["case_result_identity"] = benchmark.canonical_sha256(
        {key: value for key, value in payload.items() if key != "case_result_identity"}
    )
    with pytest.raises(ValidationError, match="differs"):
        VS01BenchmarkCaseResult.model_validate(payload)


def test_spec_run_and_receipt_cross_validation(tmp_path: Path) -> None:
    specification = _spec()
    payload = specification.model_dump(mode="python") | {"case_order": tuple(reversed(CASE_IDS))}
    payload["specification_identity"] = benchmark.canonical_sha256(
        {key: value for key, value in payload.items() if key != "specification_identity"}
    )
    with pytest.raises(ValidationError, match="authority differs"):
        VS01BenchmarkExecutionSpecification.model_validate(payload)
    run = _run()
    draft = run.model_copy(update={"case_results": run.case_results[::-1]})
    changed = draft.model_dump(mode="python")
    changed["run_result_identity"] = benchmark.canonical_sha256(
        draft.model_dump(mode="json", exclude={"run_result_identity"})
    )
    with pytest.raises(ValidationError, match="case order differs"):
        VS01BenchmarkRunResult.model_validate(changed)
    receipt = _receipt(tmp_path, run)
    for mutation in (
        {"published": False},
        {"archive_writes": 0},
        {"pre_store_upstream_fingerprints": (("changed", "b" * 64),)},
    ):
        with pytest.raises(ValidationError):
            VS01BenchmarkExecutionReceipt.model_validate(receipt.model_dump(mode="python") | mutation)


def test_campaign_dry_live_verified_existing_and_stale_authority(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    authorities = benchmark.load_benchmark_authority()
    runs = {False: _run(False), True: _run(True)}

    def replay(
        _items: Any,
        specification: VS01BenchmarkExecutionSpecification,
        ledger: scoring.BenchmarkOperationLedger,
        **_kwargs: Any,
    ) -> tuple[VS01BenchmarkRunResult, scoring.BenchmarkOperationLedger]:
        return runs[specification.execution_mode.endswith("DRY_RUN")], ledger.add(
            replay_count=1,
            subject_invocations=12,
            scoring_invocations=12,
            case_results_constructed=12,
            run_results_constructed=1,
        )

    monkeypatch.setattr(scoring, "execute_reference_replay", replay)

    def fingerprints(_root: Path) -> tuple[tuple[str, str], ...]:
        return _fingerprints()

    def campaign(dry_run: bool) -> tuple[Any, Any, VS01BenchmarkExecutionReceipt, bool]:
        return scoring.run_reference_campaign(
            dry_run=dry_run,
            archive_root=tmp_path,
            _authorities=authorities,
            _implementation_commit="1" * 40,
            _authority_loader=fingerprints,
        )

    dry, live, existing = campaign(True), campaign(False), campaign(False)
    assert dry[2].disposition == "DRY_RUN_VALIDATED" and dry[3] is False
    assert live[2].published and live[3] is True
    assert existing[2].disposition == "VERIFIED_EXISTING" and existing[2].published is existing[3] is False
    assert existing[2].retained_publication_receipt_id == live[2].receipt_id
    changed = iter((_fingerprints(), (("changed", "b" * 64),)))

    def changed_fingerprints(_root: Path) -> tuple[tuple[str, str], ...]:
        return next(changed)

    with pytest.raises(ValueError, match="changed before store"):
        scoring.run_reference_campaign(
            dry_run=True,
            archive_root=tmp_path,
            _authorities=authorities,
            _implementation_commit="1" * 40,
            _authority_loader=changed_fingerprints,
        )


def test_store_retained_validation_unsafe_paths_and_complete_writes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    result = _run()
    original = store.os.write
    calls = 0

    def short(descriptor: int, data: memoryview) -> int:
        nonlocal calls
        calls += 1
        return original(descriptor, data[: max(1, len(data) // 2)])

    scratch = tmp_path / "scratch"
    monkeypatch.setattr(store.os, "write", short)
    store._write_immutable(scratch, b"complete-write")
    assert scratch.read_bytes() == b"complete-write" and calls > 1

    def zero(_descriptor: int, _data: memoryview) -> int:
        return 0

    monkeypatch.setattr(store.os, "write", zero)
    with pytest.raises(OSError, match="zero-byte"):
        store._write_immutable(tmp_path / "zero", b"x")
    monkeypatch.setattr(store.os, "write", original)
    root = tmp_path / "archive"
    root.mkdir()
    root_receipt = _receipt(root, result)
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / ".incoming").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="unsafe"):
        store.publish_benchmark_result(root, result, root_receipt)
    (root / ".incoming").unlink()
    root.joinpath(".incoming").write_text("not-directory")
    with pytest.raises(ValueError, match="unsafe"):
        store.publish_benchmark_result(root, result, root_receipt)


def test_store_partial_stage_recovery_unexpected_and_malformed_receipt(tmp_path: Path) -> None:
    result = _run()
    receipt = _receipt(tmp_path, result)
    result_bytes = store.canonical_run_result_bytes(result)
    result_sha = hashlib.sha256(result_bytes).hexdigest()
    stage = store.benchmark_stage_path(tmp_path, result_sha)
    stage.mkdir(parents=True)
    store._write_immutable(stage / "object", result_bytes)
    unrelated = tmp_path / ".incoming/unrelated-stage"
    unrelated.mkdir()
    store.publish_benchmark_result(tmp_path, result, receipt)
    assert unrelated.is_dir() and not stage.exists()
    receipt_path = tmp_path / store.publication_paths(result_sha)[2]
    os.chmod(receipt_path, 0o644)
    receipt_path.write_bytes(b"{}")
    os.chmod(receipt_path, 0o444)
    with pytest.raises(ValueError, match="invalid"):
        store.verify_existing(tmp_path, result, result_bytes, {"implementation_commit": "1" * 40})


@pytest.mark.parametrize("unsafe", ("symlink", "broken", "file"))
def test_store_rejects_unsafe_existing_ancestors(tmp_path: Path, unsafe: str) -> None:
    root = tmp_path / "archive"
    root.mkdir()
    target = tmp_path / "target"
    target.mkdir()
    if unsafe == "symlink":
        (root / "objects").symlink_to(target, target_is_directory=True)
    elif unsafe == "broken":
        (root / "objects").symlink_to(tmp_path / "missing", target_is_directory=True)
    else:
        (root / "objects").write_text("not a directory")
    result = _run()
    with pytest.raises(ValueError, match="unsafe"):
        store.verify_existing(root, result, store.canonical_run_result_bytes(result))


def test_store_rejects_unexpected_exact_stage_and_mismatched_object(tmp_path: Path) -> None:
    result = _run()
    result_bytes = store.canonical_run_result_bytes(result)
    result_sha = hashlib.sha256(result_bytes).hexdigest()
    stage = store.benchmark_stage_path(tmp_path, result_sha)
    stage.mkdir(parents=True)
    (stage / "unexpected").write_text("preserve and reject")
    with pytest.raises(ValueError, match="unexpected"):
        store.publish_benchmark_result(tmp_path, result, _receipt(tmp_path, result))
    assert (stage / "unexpected").read_text() == "preserve and reject"
    for item in stage.iterdir():
        item.unlink()
    stage.rmdir()
    object_path = tmp_path / store.publication_paths(result_sha)[0]
    object_path.parent.mkdir(parents=True)
    store._write_immutable(object_path, b"wrong")
    with pytest.raises(ValueError, match="differs"):
        store.verify_existing(tmp_path, result, result_bytes)


def test_inventory_child_and_fixture_hashes_stable() -> None:
    inventory = tuple(
        kind
        for authority in benchmark.load_benchmark_authority()
        for kind, _rule in benchmark.compile_scorer_authority(authority).deterministic_checks
    )
    assert {kind: inventory.count(kind) for kind in benchmark.CHECK_FIELDS} == {
        "CLAIM_SOURCE_MAP": 5,
        "EXACT_FIELD": 6,
        "EXACT_STRING": 3,
        "FORBIDDEN_STRING": 1,
        "ONLY_CANONICAL_QUOTE": 1,
        "REGION_ROLE_MAP": 1,
        "REQUIRED_EVENT": 1,
        "REQUIRED_SOURCE_HANDLE": 1,
        "SESSION_STATE": 2,
        "TEXT_QUOTE_SELECTOR": 1,
    }
    assert hashlib.sha256(reference_subject.CHILD_SOURCE.encode()).hexdigest() == reference_subject.CHILD_SHA256


def test_authority_parser_and_firewall_fail_closed(tmp_path: Path) -> None:
    for raw, message in (
        (b'{"a":1,"a":2}', "duplicate JSON keys"),
        (b'{"a":NaN}', "non-finite number"),
        (b"not-json", "strict UTF-8 JSON"),
        (b"[]", "not a JSON object"),
    ):
        with pytest.raises(ValueError, match=message):
            benchmark._strict_json(raw)
    missing = tmp_path / "missing.json"
    with pytest.raises(ValueError, match="is missing"):
        benchmark._read_exact(missing, "0" * 64)
    missing.write_text("changed")
    with pytest.raises(ValueError, match="hash differs"):
        benchmark._read_exact(missing, "0" * 64)
    authorities = benchmark.load_benchmark_authority()
    with pytest.raises(ValueError, match="order differs"):
        benchmark.build_execution_specification(tuple(reversed(authorities)), dry_run=False)
    b08 = benchmark.compile_subject_package(authorities[7])
    with pytest.raises(ValueError, match="INVALID_LEAKAGE"):
        benchmark.audit_subject_package(replace(b08, deterministic_tool_interfaces=(("lookup", "{}"),)))
    b09 = benchmark.compile_subject_package(authorities[8])
    with pytest.raises(ValueError, match="INVALID_LEAKAGE"):
        benchmark.audit_subject_package(replace(b09, authorized_raster_sha256=None))


def test_reference_parent_rejects_bad_child_results(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValueError, match="malformed output"):
        reference_subject._parse_response(b"{}")
    case, _scorer, fixture = _synthetic(1)
    adapter = DeterministicReferenceSubjectAdapter(fixture, implementation_evidence_mode=True)
    completed = subprocess.CompletedProcess([], 1, b"", b"child error")
    monkeypatch.setattr(reference_subject.subprocess, "run", lambda *_args, **_kwargs: completed)
    with pytest.raises(ValueError, match="subprocess failed"):
        adapter.generate(case)
    wrong = StructuredSubjectResponse(
        case.case_id,
        case.source_declared_compatibility_sha256,
        case.execution_rfc8785_jcs_sha256,
        case.package_identity,
        fixture.response_payload,
        fixture.response_payload_sha256,
    )
    monkeypatch.setattr(
        reference_subject.subprocess, "run", lambda *_args, **_kwargs: subprocess.CompletedProcess([], 0)
    )
    monkeypatch.setattr(reference_subject, "_parse_response", lambda _value: replace(wrong, case_id="SYN-WRONG"))
    with pytest.raises(ValueError, match="response differs"):
        adapter.generate(case)


def test_store_path_and_partial_publication_fail_closed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(store.subprocess, "run", lambda *_args, **_kwargs: SimpleNamespace(stdout="bad\n"))
    with pytest.raises(ValueError, match="implementation commit"):
        store.implementation_head()
    unsafe = tmp_path / "unsafe"
    unsafe.write_text("not-directory")
    with pytest.raises(ValueError, match="archive authority is unsafe"):
        store._inventory(unsafe, contents=False)
    root = tmp_path / "archive"
    root.mkdir()
    with pytest.raises(ValueError, match="escapes its root"):
        store._safe_directory(root, "..")
    with pytest.raises(ValueError, match="missing or unsafe"):
        store._safe_directory(root, "missing", create=False)
    result = _run()
    result_bytes = store.canonical_run_result_bytes(result)
    paths = store.publication_paths(hashlib.sha256(result_bytes).hexdigest())
    receipt_path = root / paths[2]
    receipt_path.parent.mkdir(parents=True)
    store._write_immutable(receipt_path, b"{}")
    with pytest.raises(ValueError, match="prerequisite is missing"):
        store.verify_existing(root, result, result_bytes)
