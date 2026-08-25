from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError
from uuid6 import uuid7

import bsl.application.vs01_benchmark as benchmark
import bsl.application.vs01_benchmark_scoring as scoring
import bsl.application.vs01_reference_subject as reference_subject
import bsl.interfaces.cli as cli
from bsl.application.vs01_benchmark import (
    ReferenceSubjectFixture,
    ScorerCaseAuthority,
    StructuredSubjectResponse,
    SubjectCasePackage,
)
from bsl.application.vs01_reference_subject import DeterministicReferenceSubjectAdapter
from bsl.contracts.benchmark import (
    VS01BenchmarkCaseResult,
    VS01BenchmarkExecutionReceipt,
    VS01BenchmarkExecutionSpecification,
    VS01BenchmarkRunResult,
)
from bsl.infrastructure.benchmark_store import (
    benchmark_stage_path,
    canonical_run_result_bytes,
    publication_paths,
    publish_benchmark_result,
    verify_existing,
)

ROOT = Path(__file__).parents[1]
WEIGHTS = (5, 5, 5, 5, 4, 4, 4, 6, 6, 6, 5, 5)
PARTITIONS = ("REV-P0",) * 7 + ("REV-P1",) * 5


def _synthetic(index: int) -> tuple[SubjectCasePackage, ScorerCaseAuthority, ReferenceSubjectFixture]:
    case_id = f"SYN-T07-CASE-{index:02d}"
    digest = benchmark.canonical_sha256((case_id, "synthetic authority"))
    package_payload = {
        "case_id": case_id,
        "source_declared_compatibility_sha256": digest,
        "execution_rfc8785_jcs_sha256": digest,
        "prompt_fields": (("prompt", f"Synthetic non-benchmark prompt {index}"),),
        "evaluation_mode": "SYNTHETIC",
        "answer_mode": "BRIEF",
        "evidence_contract_id": "SYNTHETIC-EVIDENCE",
        "whitelisted_source_handles": (f"SYNTHETIC-SOURCE-{index}",),
        "authorized_raster_sha256": None,
        "deterministic_tool_interfaces": (),
        "response_fields": ("answer",),
        "case_local_budgets": (("attempts", 1), ("retries", 0), ("semantic_rerolls", 0)),
    }
    package = SubjectCasePackage(**package_payload, package_identity=benchmark.canonical_sha256(package_payload))
    response_payload = (("answer", f"Synthetic response {index}"),)
    response_sha = benchmark.canonical_sha256(response_payload)
    scorer_payload = {
        "case_id": case_id,
        "source_declared_compatibility_sha256": digest,
        "execution_rfc8785_jcs_sha256": digest,
        "reference_payload": response_payload,
        "reference_payload_sha256": response_sha,
        "deterministic_checks": (("SYNTHETIC_EXACT", str(index)),),
        "criteria": ((f"SYN-R{index}", WEIGHTS[index - 1], ""),),
        "evidence_references": (f"SYNTHETIC-SOURCE-{index}",),
    }
    scorer = ScorerCaseAuthority(**scorer_payload, scorer_plan_identity=benchmark.canonical_sha256(scorer_payload))
    fixture = ReferenceSubjectFixture(case_id, digest, digest, "BRIEF", response_payload, response_sha)
    return package, scorer, fixture


def _synthetic_spec() -> VS01BenchmarkExecutionSpecification:
    records = tuple(_synthetic(index) for index in range(1, 13))
    payload = {
        "batch_markdown_sha256": "a" * 64,
        "batch_cases_sha256": "b" * 64,
        "r01_design_sha256": "c" * 64,
        "r01_protocol_sha256": "d" * 64,
        "erratum_markdown_sha256": "e" * 64,
        "erratum_json_sha256": "f" * 64,
        "source_declared_compatibility_hashes": tuple(
            (case.case_id, case.source_declared_compatibility_sha256) for case, _, _ in records
        ),
        "execution_rfc8785_jcs_hashes": tuple(
            (case.case_id, case.execution_rfc8785_jcs_sha256) for case, _, _ in records
        ),
        "case_order": tuple(case.case_id for case, _, _ in records),
        "subject_projection_identities": tuple((case.case_id, case.package_identity) for case, _, _ in records),
        "scorer_revision": scoring.SCORER_REVISION,
        "upstream_authority": (("synthetic", "authority"),),
        "isolation_policy": ("fresh subprocess per case", "one attempt", "zero retries"),
        "screening_case_minimums": tuple((case.case_id, 0) for case, _, _ in records),
        "screening_partition_minimums": (("REV-P0", 58), ("REV-P1", 45), ("TOTAL", 102)),
        "b08_full_runtime_limitation": "VS01-B08-RUNTIME-C01_REQUIRED_NOT_AUTHORED",
        "execution_mode": "REFERENCE_CONFORMANCE_DRY_RUN",
    }
    draft = VS01BenchmarkExecutionSpecification.model_construct(**payload, specification_identity="0" * 64)
    payload["specification_identity"] = benchmark.canonical_sha256(
        draft.model_dump(mode="json", exclude={"specification_identity"})
    )
    return VS01BenchmarkExecutionSpecification.model_validate(payload)


def _response(
    case: SubjectCasePackage, fixture: ReferenceSubjectFixture, state: str = "COMPLETED"
) -> StructuredSubjectResponse:
    return StructuredSubjectResponse(
        case.case_id,
        case.source_declared_compatibility_sha256,
        case.execution_rfc8785_jcs_sha256,
        case.package_identity,
        fixture.response_payload,
        fixture.response_payload_sha256,
        state,
    )


def _synthetic_results() -> tuple[VS01BenchmarkCaseResult, ...]:
    values = []
    for index in range(1, 13):
        case, scorer, fixture = _synthetic(index)
        values.append(
            scoring.score_reference_case(case, scorer, _response(case, fixture), implementation_evidence_mode=True)
        )
    return tuple(values)


def _synthetic_run() -> tuple[VS01BenchmarkExecutionSpecification, VS01BenchmarkRunResult]:
    specification = _synthetic_spec()
    return specification, scoring._run_result(specification, _synthetic_results(), PARTITIONS)


def _receipt(root: Path, result: VS01BenchmarkRunResult, *, dry_run: bool = False) -> VS01BenchmarkExecutionReceipt:
    return scoring._receipt(
        _synthetic_spec(),
        result,
        root,
        dry_run=dry_run,
        implementation_commit="1" * 40,
        new_uuid=uuid7,
        now=lambda: datetime.now(UTC),
    )


def test_exact_real_authority_dual_hash_arithmetic_and_static_compilation_only() -> None:
    authorities = benchmark.load_benchmark_authority()
    matrix = benchmark.compatibility_hash_matrix(authorities)
    assert len(authorities) == len(matrix) == 12
    assert [item[0] for item in matrix] == list(benchmark.REAL_CASE_IDS)
    assert [item[0] for item in matrix if item[1] != item[2]] == ["VS01-B10-C01"]
    assert matrix[9][1:] == (benchmark.B10_COMPATIBILITY_SHA256, benchmark.B10_JCS_SHA256)
    assert benchmark.static_compilation_identity(authorities) == benchmark.static_compilation_identity(authorities)
    assert benchmark._REAL_OPERATION_COUNTS == {
        "subject": 0,
        "scoring": 0,
        "case_result": 0,
        "run_result": 0,
        "receipt": 0,
    }
    with pytest.raises(ValueError, match="prohibited"):
        benchmark.guard_real_case("VS01-B01-C01", "subject", implementation_evidence_mode=True)


def test_generated_fixtures_are_reproducible_committed_and_public_safe() -> None:
    first = benchmark.generated_fixture_bytes()
    second = benchmark.generated_fixture_bytes()
    assert first == second
    paths = (
        ROOT / "fixtures/VS01-T07/reference-subject-responses.json",
        ROOT / "fixtures/VS01-T07/subject-projection-manifest.json",
    )
    assert tuple(path.read_bytes() for path in paths) == first
    reference = json.loads(first[0])
    assert len(reference["cases"]) == 12
    assert set(reference["cases"][0]) == {
        "case_id",
        "source_declared_compatibility_sha256",
        "execution_rfc8785_jcs_sha256",
        "answer_mode",
        "response_payload",
        "response_payload_sha256",
    }
    for forbidden in (b'"rubric":', b'"deterministic_checks":', b'"hard_failures":', b'"scorer_path":'):
        assert forbidden not in first[0] and forbidden not in first[1]


def test_subject_projection_firewall_and_special_case_boundaries() -> None:
    authorities = benchmark.load_benchmark_authority()
    packages = {item.case_id: benchmark.compile_subject_package(item) for item in authorities}
    assert set(packages["VS01-B08-C01"].whitelisted_source_handles) == {
        "SP01-SRC-003#John.1.5",
        "SP01-SRC-004#John.1.5",
    }
    assert packages["VS01-B08-C01"].deterministic_tool_interfaces == ()
    assert packages["VS01-B09-C01"].authorized_raster_sha256 == benchmark.BASE_RASTER_SHA256
    assert packages["VS01-B10-C01"].authorized_raster_sha256 == benchmark.DEGRADED_RASTER_SHA256
    assert len(packages["VS01-B11-C01"].prompt_fields) == 5
    assert "Correction: use the ASV" in packages["VS01-B11-C01"].prompt_fields[2][1]
    assert packages["VS01-B12-C01"].response_fields == ("brief", "study")
    package_fields = set(SubjectCasePackage.__dataclass_fields__)
    assert not package_fields.intersection(benchmark.FORBIDDEN_SUBJECT_FIELDS)
    assert set(ScorerCaseAuthority.__dataclass_fields__).isdisjoint({"prompt_fields", "deterministic_tool_interfaces"})


def test_reference_subject_uses_a_fresh_subprocess_per_synthetic_case(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = 0
    original = scoring.DeterministicReferenceSubjectAdapter.generate

    def counted(self: DeterministicReferenceSubjectAdapter, case: SubjectCasePackage) -> StructuredSubjectResponse:
        nonlocal calls
        calls += 1
        return original(self, case)

    monkeypatch.setattr(DeterministicReferenceSubjectAdapter, "generate", counted)
    for index in (1, 2):
        case, _scorer, fixture = _synthetic(index)
        response = DeterministicReferenceSubjectAdapter(fixture, implementation_evidence_mode=True).generate(case)
        assert response.response_payload == fixture.response_payload
    assert calls == 2


def test_reference_subject_rejects_identity_and_subprocess_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    case, _scorer, fixture = _synthetic(1)
    changed_fixture = ReferenceSubjectFixture(
        fixture.case_id,
        fixture.source_declared_compatibility_sha256,
        fixture.execution_rfc8785_jcs_sha256,
        fixture.answer_mode,
        (("answer", "changed synthetic response"),),
        fixture.response_payload_sha256,
    )
    with pytest.raises(ValueError, match="identity differs"):
        reference_subject._execute(case, changed_fixture)
    assert reference_subject._record(SubjectCasePackage, case.payload()) == case
    with pytest.raises(ValueError, match="record differs"):
        reference_subject._record(SubjectCasePackage, {})
    adapter = DeterministicReferenceSubjectAdapter(fixture, implementation_evidence_mode=True)
    monkeypatch.setattr(
        reference_subject.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 1, b"", b"synthetic failure"),
    )
    with pytest.raises(ValueError, match="subprocess failed"):
        adapter.generate(case)
    monkeypatch.setattr(
        reference_subject.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, b"not-json", b""),
    )
    with pytest.raises(ValueError, match="malformed output"):
        adapter.generate(case)


def test_static_execution_specification_compiles_real_authority_without_execution() -> None:
    authorities = benchmark.load_benchmark_authority()
    specification = scoring.build_execution_specification(authorities, dry_run=True)
    assert specification.case_order == benchmark.REAL_CASE_IDS
    assert specification.execution_mode == "REFERENCE_CONFORMANCE_DRY_RUN"
    assert benchmark._REAL_OPERATION_COUNTS == {
        "subject": 0,
        "scoring": 0,
        "case_result": 0,
        "run_result": 0,
        "receipt": 0,
    }


def test_synthetic_replay_and_campaign_publication_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    synthetic = tuple(_synthetic(index) for index in range(1, 13))
    authorities = tuple(
        SimpleNamespace(case_id=case.case_id, source={"review_partition": PARTITIONS[index]})
        for index, (case, _scorer, _fixture) in enumerate(synthetic)
    )
    by_id = {case.case_id: values for case, *values in synthetic}
    monkeypatch.setattr(scoring, "compile_subject_package", lambda item: _synthetic(int(item.case_id[-2:]))[0])
    monkeypatch.setattr(scoring, "compile_scorer_authority", lambda item: by_id[item.case_id][0])
    monkeypatch.setattr(scoring, "compile_reference_fixture", lambda item: by_id[item.case_id][1])
    specification = _synthetic_spec()
    replay = scoring.execute_reference_replay(
        authorities,  # type: ignore[arg-type]
        specification,
        implementation_evidence_mode=True,
    )
    assert replay.disposition == "REFERENCE_CONFORMANT"

    def fail_synthetic_subject(
        self: DeterministicReferenceSubjectAdapter, case: SubjectCasePackage
    ) -> StructuredSubjectResponse:
        raise ValueError("synthetic subject failure")

    monkeypatch.setattr(DeterministicReferenceSubjectAdapter, "generate", fail_synthetic_subject)
    failed_replay = scoring.execute_reference_replay(
        authorities,  # type: ignore[arg-type]
        specification,
        implementation_evidence_mode=True,
    )
    assert dict(failed_replay.failure_counts)["error"] == 12

    monkeypatch.setattr(scoring, "build_execution_specification", lambda items, dry_run: specification)
    monkeypatch.setattr(scoring, "execute_reference_replay", lambda *args, **kwargs: replay)
    common = {
        "archive_root": tmp_path,
        "_authorities": authorities,
        "_implementation_commit": "1" * 40,
        "_new_uuid": uuid7,
        "_now": lambda: datetime.now(UTC),
    }
    assert scoring.run_reference_campaign(dry_run=True, **common)[3] is False  # type: ignore[arg-type]
    live = scoring.run_reference_campaign(dry_run=False, **common)  # type: ignore[arg-type]
    assert live[3] is True and live[2].published
    existing = scoring.run_reference_campaign(dry_run=False, **common)  # type: ignore[arg-type]
    assert existing[3] is False and existing[2] == live[2]


def test_campaign_rejects_replay_mismatch_and_git_head_mutation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    specification, conformant = _synthetic_run()
    case, scorer, fixture = _synthetic(1)
    failed_case = scoring.score_reference_case(
        case,
        scorer,
        _response(case, fixture, "ERROR"),
        implementation_evidence_mode=True,
    )
    failed = scoring._run_result(specification, (failed_case,) + _synthetic_results()[1:], PARTITIONS)
    authorities = (SimpleNamespace(case_id="SYN-T07-CASE-01"),)
    monkeypatch.setattr(scoring, "build_execution_specification", lambda items, dry_run: specification)
    runs = iter((conformant, failed))
    monkeypatch.setattr(scoring, "execute_reference_replay", lambda *args, **kwargs: next(runs))
    with pytest.raises(ValueError, match="replay identity differs"):
        scoring.run_reference_campaign(
            dry_run=True,
            archive_root=tmp_path,
            _authorities=authorities,  # type: ignore[arg-type]
            _implementation_commit="1" * 40,
        )
    assert (
        scoring._git_head()
        == subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    )
    monkeypatch.setattr(
        scoring.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, "not-a-commit\n", ""),
    )
    with pytest.raises(ValueError, match="commit is invalid"):
        scoring._git_head()


@pytest.mark.parametrize(
    ("mutation", "message"),
    (
        ({"specification_identity": "0" * 64}, "specification identity differs"),
        ({"case_order": ("SYN-T07-CASE-01",) * 12}, "case inventory differs"),
        ({"screening_case_minimums": (("SYN-T07-CASE-01", 0),)}, "duplicate or missing cases"),
    ),
)
def test_execution_specification_rejects_identity_and_inventory(mutation: dict[str, object], message: str) -> None:
    payload = _synthetic_spec().model_dump(mode="python") | mutation
    if "specification_identity" not in mutation:
        payload["specification_identity"] = benchmark.canonical_sha256(
            {key: value for key, value in payload.items() if key != "specification_identity"}
        )
    with pytest.raises(ValidationError, match=message):
        VS01BenchmarkExecutionSpecification.model_validate(payload)


@pytest.mark.parametrize(
    ("mutation", "message"),
    (
        ({"case_result_identity": "0" * 64}, "case-result identity differs"),
        ({"criterion_scores": (("SYN-R1", 2, 5, 9),)}, "criterion arithmetic differs"),
        ({"raw_points": 9}, "case-point arithmetic differs"),
        ({"error": True}, "attempt-state accounting differs"),
        ({"leakage_state": "INVALID_LEAKAGE_INCIDENT"}, "leakage disposition differs"),
    ),
)
def test_case_result_rejects_broken_accounting(mutation: dict[str, object], message: str) -> None:
    payload = _synthetic_results()[0].model_dump(mode="python") | mutation
    if "case_result_identity" not in mutation:
        payload["case_result_identity"] = benchmark.canonical_sha256(
            {key: value for key, value in payload.items() if key != "case_result_identity"}
        )
    with pytest.raises(ValidationError, match=message):
        VS01BenchmarkCaseResult.model_validate(payload)


@pytest.mark.parametrize(
    ("mutation", "message"),
    (
        ({"run_result_identity": "0" * 64}, "run-result identity differs"),
        (
            {
                "case_results": tuple(
                    item.model_dump(mode="python") for item in _synthetic_results()[:11] + (_synthetic_results()[0],)
                )
            },
            "twelve unique cases",
        ),
        ({"p0_points": 63}, "partition arithmetic differs"),
        ({"p0_points": 63, "total_points": 119}, "case arithmetic differs"),
        ({"completed_attempts": 11}, "completed-attempt accounting differs"),
    ),
)
def test_run_result_rejects_broken_accounting(mutation: dict[str, object], message: str) -> None:
    payload = _synthetic_run()[1].model_dump(mode="python") | mutation
    if "run_result_identity" not in mutation:
        payload["run_result_identity"] = benchmark.canonical_sha256(
            {key: value for key, value in payload.items() if key != "run_result_identity"}
        )
    with pytest.raises(ValidationError, match=message):
        VS01BenchmarkRunResult.model_validate(payload)


@pytest.mark.parametrize(
    ("mutation", "message"),
    (
        ({"receipt_id": uuid4()}, "not UUIDv7"),
        ({"generated_at": datetime.now()}, "not offset-aware"),
        ({"dry_run": True, "published": True}, "claims publication"),
        ({"published": True, "verified_existing": True}, "both published and verified-existing"),
    ),
)
def test_execution_receipt_rejects_invalid_operations(
    mutation: dict[str, object], message: str, tmp_path: Path
) -> None:
    receipt = _receipt(tmp_path, _synthetic_run()[1])
    with pytest.raises(ValidationError, match=message):
        VS01BenchmarkExecutionReceipt.model_validate(receipt.model_dump(mode="python") | mutation)


@pytest.mark.parametrize("state", ("ERROR", "REFUSAL", "TIMEOUT", "MALFORMED"))
def test_reference_scoring_replay_arithmetic_and_error_denominator(state: str) -> None:
    specification = _synthetic_spec()
    first = _synthetic_results()
    second = _synthetic_results()
    run1 = scoring._run_result(specification, first, PARTITIONS)
    run2 = scoring._run_result(specification, second, PARTITIONS)
    assert run1.run_result_identity == run2.run_result_identity
    assert (run1.p0_points, run1.p1_points, run1.total_points) == (64, 56, 120)
    case, scorer, fixture = _synthetic(1)
    failed = scoring.score_reference_case(
        case, scorer, _response(case, fixture, state), implementation_evidence_mode=True
    )
    changed = (failed,) + first[1:]
    failed_run = scoring._run_result(specification, changed, PARTITIONS)
    assert failed_run.requested_attempts == 12 and failed_run.completed_attempts == 11
    assert dict(failed_run.failure_counts)[state.lower()] == 1 and failed_run.total_points == 110


@pytest.mark.parametrize("category", tuple(scoring.ADVERSARY_SEVERITIES))
def test_twelve_synthetic_adversary_categories(category: str) -> None:
    case, scorer, fixture = _synthetic(1)
    result = scoring.score_reference_case(
        case,
        scorer,
        _response(case, fixture),
        implementation_evidence_mode=True,
        synthetic_adversary=category,
    )
    assert result.case_disposition == "REFERENCE_NONCONFORMANT_REPAIR_REQUIRED"
    assert result.hard_failures[0][2] == category and result.capped_points == 0


@pytest.mark.parametrize(
    ("severity", "expected_cap"),
    (("HF-1_CRITICAL", 0), ("HF-2_MAJOR", 0), ("HF-3_MATERIAL", 0), ("HF-4_MINOR", 2)),
)
def test_hard_failure_precedence(severity: str, expected_cap: int) -> None:
    case, scorer, fixture = _synthetic(1)
    scorer = ScorerCaseAuthority(
        scorer.case_id,
        scorer.source_declared_compatibility_sha256,
        scorer.execution_rfc8785_jcs_sha256,
        scorer.reference_payload,
        scorer.reference_payload_sha256,
        scorer.deterministic_checks,
        (scorer.criteria[0], ("SYN-EXTRA", 1, "")),
        scorer.evidence_references,
        scorer.scorer_plan_identity,
    )
    result = scoring.score_reference_case(
        case,
        scorer,
        _response(case, fixture),
        implementation_evidence_mode=True,
        synthetic_adversary="wrong canonical quotation",
        synthetic_severity=severity,
    )
    assert result.raw_points == 2 and result.capped_points == expected_cap


@pytest.mark.parametrize(
    ("field", "below", "at"), (("p0_points", 57, 58), ("p1_points", 44, 45), ("total_points", 101, 102))
)
def test_every_screening_threshold_boundary(field: str, below: int, at: int) -> None:
    values = {"p0_points": 58, "p1_points": 45, "total_points": 102}
    common = {
        "every_case_minimum_met": True,
        "no_zero_criteria": True,
        "hf1_count": 0,
        "hf2_count": 0,
        "hf3_count": 0,
        "b09_passed": True,
        "b10_passed": True,
        "b11_correction_losses": 0,
    }
    assert scoring.screening_disposition(**(values | {field: below}), **common) == "SCREENING_NO_GO"
    assert (
        scoring.screening_disposition(**(values | {field: at}), **common) == "SCREENING_PASS_WITH_EXPLICIT_LIMITATIONS"
    )


def test_screening_hard_failure_and_material_review_precedence() -> None:
    values = {
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
    assert scoring.screening_disposition(**values, hf1_count=1, hf3_count=0) == "SCREENING_NO_GO"
    assert scoring.screening_disposition(**values, hf1_count=0, hf3_count=1) == "SCREENING_REVIEW_REQUIRED"


@pytest.mark.parametrize("minimum", (5, 8, 5, 10, 8, 12, 10, 7, 8, 8, 8, 10))
def test_every_case_threshold_immediately_below_and_at_gate(minimum: int) -> None:
    assert not scoring.meets_case_minimum(minimum - 1, minimum)
    assert scoring.meets_case_minimum(minimum, minimum)


def test_leakage_invalidates_before_scoring() -> None:
    case, scorer, fixture = _synthetic(1)
    data = case.payload()
    data["whitelisted_source_handles"] = ("/tmp/hidden-scorer-store",)
    data["package_identity"] = benchmark.canonical_sha256(
        {key: value for key, value in data.items() if key != "package_identity"}
    )
    leaked = SubjectCasePackage(**data)
    result = scoring.score_reference_case(leaked, scorer, _response(leaked, fixture), implementation_evidence_mode=True)
    assert result.attempt_state == result.leakage_state == result.case_disposition == "INVALID_LEAKAGE_INCIDENT"


def test_result_canonicalization_and_receipt_operational_fields() -> None:
    specification, result = _synthetic_run()
    data = result.model_dump(mode="json")
    data["total_points"] = 119
    with pytest.raises(ValidationError):
        VS01BenchmarkRunResult.model_validate(data)
    first = scoring._receipt(
        specification,
        result,
        Path("/synthetic"),
        dry_run=True,
        implementation_commit="1" * 40,
        new_uuid=uuid7,
        now=lambda: datetime(2026, 1, 1, tzinfo=UTC),
    )
    second = scoring._receipt(
        specification,
        result,
        Path("/synthetic"),
        dry_run=True,
        implementation_commit="1" * 40,
        new_uuid=uuid7,
        now=lambda: datetime(2026, 1, 1, tzinfo=UTC) + timedelta(seconds=1),
    )
    assert first.receipt_id != second.receipt_id and first.generated_at != second.generated_at
    assert first.run_result_identity == second.run_result_identity == result.run_result_identity


def test_synthetic_result_store_receipt_last_recovery_and_unrelated_preservation(tmp_path: Path) -> None:
    (tmp_path / ".incoming").mkdir()
    unrelated = tmp_path / ".incoming/foreign-stage"
    unrelated.write_text("opaque")
    _specification, result = _synthetic_run()
    receipt = _receipt(tmp_path, result)
    publish_benchmark_result(tmp_path, result, receipt)
    result_sha = hashlib.sha256(canonical_run_result_bytes(result)).hexdigest()
    assert unrelated.read_text() == "opaque" and not benchmark_stage_path(tmp_path, result_sha).exists()
    for relative in publication_paths(result_sha):
        assert os.stat(tmp_path / relative, follow_symlinks=False).st_mode & 0o777 == 0o444
    assert verify_existing(tmp_path, result, canonical_run_result_bytes(result)) == receipt
    receipt_path = tmp_path / publication_paths(result_sha)[-1]
    os.chmod(receipt_path, 0o644)
    receipt_path.unlink()
    replacement = _receipt(tmp_path, result)
    publish_benchmark_result(tmp_path, result, replacement)
    object_path = tmp_path / publication_paths(result_sha)[0]
    os.chmod(object_path, 0o644)
    with pytest.raises(ValueError, match="differs or is mutable"):
        verify_existing(tmp_path, result, canonical_run_result_bytes(result))


def test_benchmark_cli_private_synthetic_seam_and_subject_rejection(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    specification, result = _synthetic_run()
    receipt = _receipt(Path("/synthetic"), result, dry_run=True)
    monkeypatch.setattr(cli, "run_reference_campaign", lambda **_kwargs: (specification, result, receipt, False))
    assert cli.main(["benchmark", "vs01-batch-01", "--subject", "deterministic-reference", "--dry-run"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["receipt"]["disposition"] == "DRY_RUN_VALIDATED" and output["published"] is False
    assert cli.main(["benchmark", "vs01-batch-01", "--subject", "unsupported"]) == 2
    assert json.loads(capsys.readouterr().out)["error"]["code"] == "INVALID_CLI_INPUT"
