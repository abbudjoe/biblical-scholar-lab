from __future__ import annotations

import hashlib
import json
import os
import stat
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest
import rfc8785
from pydantic import ValidationError

import bsl.application.vs01_runtime_screening as runtime_screening
import bsl.infrastructure.benchmark_store as benchmark_store
import bsl.interfaces.cli as cli
from bsl.application.vs01_benchmark import load_benchmark_authority
from bsl.application.vs01_runtime_reference import (
    DeterministicRuntimeSubject,
    RuntimeToolBroker,
    complete_runtime_pair,
    corrected_runtime,
    execute_reference_runtime,
    subject_package_from_projection,
)
from bsl.application.vs01_runtime_scoring import evaluate_hard_failures, score_runtime_pair
from bsl.application.vs01_runtime_screening import compile_pair_specification
from bsl.contracts.runtime_screening import (
    CASE_IDENTITY,
    EVENT_SEQUENCE,
    HARD_FAILURES,
    SPEC_IDENTITY,
    TOOL_NAMES,
    RuntimeOperationCounters,
    VS01B08RuntimePairResult,
    VS01B08RuntimePairSpecification,
    VS01RuntimeAcquisitionRun,
    VS01RuntimeScreeningReceipt,
    canonical_sha256,
)
from bsl.infrastructure.runtime_screening_store import (
    build_screening_receipt,
    canonical_pair_result_bytes,
    publication_paths,
    publish_runtime_screening,
    verify_existing,
)

ROOT = Path(__file__).parents[1]
SYNTHETIC_ID = "SYN-VS01-B08-RUNTIME-C01"
FIXED_RESULT_IDENTITY = "e" * 64


def _static() -> tuple[dict[str, object], VS01RuntimeAcquisitionRun]:
    projection = json.loads((ROOT / "fixtures/VS01-T08/runtime-subject-projection.json").read_bytes())
    run = VS01RuntimeAcquisitionRun.model_validate_json(
        (ROOT / "fixtures/VS01-T08/reference-runtime-run.json").read_bytes()
    )
    return projection, run


def _synthetic_run() -> VS01RuntimeAcquisitionRun:
    projection, template = _static()
    package = subject_package_from_projection(projection, case_id=SYNTHETIC_ID)
    return execute_reference_runtime(template, package)


def _result(run: VS01RuntimeAcquisitionRun | None = None) -> VS01B08RuntimePairResult:
    value = run or _synthetic_run()
    return score_runtime_pair(
        compile_pair_specification(),
        value,
        _synthetic_run(),
        FIXED_RESULT_IDENTITY,
        (value.acquisition_run_identity, value.acquisition_run_identity),
    )


def _counters(**changes: int) -> RuntimeOperationCounters:
    values = _synthetic_run().operation_counters.model_dump(mode="python") | changes
    return RuntimeOperationCounters.model_validate(values)


def test_frozen_design_identities_fixed_case_and_same_prompt() -> None:
    pair = compile_pair_specification()
    case_bytes = (ROOT / "design/approved/VS01-B08-RUNTIME-C01.json").read_bytes()
    spec_bytes = (ROOT / "design/approved/VS01-T08-runtime-pair-spec.json").read_bytes()
    assert hashlib.sha256(case_bytes).hexdigest() == "a7fc02da5ed8fda15ee29cba79cff8b037b2abc66352107f87165a0bfbea9f0f"
    assert hashlib.sha256(spec_bytes).hexdigest() == "9e49e2f2b540a54c1d945991eb6500a52c0a7873136630d8bf49854efeb765ba"
    assert (pair.runtime_case_content_sha256, pair.specification_identity) == (CASE_IDENTITY, SPEC_IDENTITY)
    fixed = load_benchmark_authority()[7]
    source = ROOT / "design/approved/BENCH-VS01-BATCH-01-cases.json"
    assert (
        hashlib.sha256(source.read_bytes()).hexdigest()
        == "4241a0bf5baf50a12ce5fe6dcfef6ed5492cde410f3d92f5aad8a9f26ba3113f"
    )
    assert fixed.source["prompt"] == pair.prompt and fixed.compatibility_sha256 == pair.fixed_case_content_sha256


def test_authority_compiler_builds_all_read_only_plans_from_verified_boundaries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from test_study_runtime import _authority
    from test_vs01_benchmark import _run

    fixed_run = _run()
    monkeypatch.setattr(runtime_screening, "load_t04_authority", lambda _root: _authority(tmp_path))
    monkeypatch.setattr(
        runtime_screening,
        "verify_t06_existing",
        lambda *_args: SimpleNamespace(
            receipt_identity=UUID("01a034c2-d6e4-73f4-91b2-7410e7453783"),
            model_dump=lambda **_kwargs: {"t06": "verified"},
        ),
    )
    monkeypatch.setattr(
        runtime_screening,
        "_load_t07",
        lambda _root: (
            fixed_run,
            SimpleNamespace(receipt_id=UUID("01a03a85-e49b-7d1c-b737-b560fd9a17df")),
            "f" * 64,
        ),
    )
    authority = runtime_screening.compile_runtime_authority(
        tmp_path, _t05_verifier=lambda _t04: {"t05": "verified", "database_writes": 0}
    )
    assert authority.fixed_case_result_identity == fixed_run.case_results[7].case_result_identity
    assert len(authority.subject_projection["tool_schemas"]) == len(authority.pair_specification.tool_definitions) == 7
    assert authority.reference_run.answer_blocks == _static()[1].answer_blocks
    assert authority.scorer_plan["free_form_judge"] is False


def test_static_fixtures_are_public_safe_exact_and_reproducible() -> None:
    projection, run = _static()
    raw = json.dumps(projection, sort_keys=True)
    assert len(projection["initial_evidence"]) == 2
    assert {item["name"] for item in projection["tool_schemas"]} == set(TOOL_NAMES)
    assert not any(name in raw for name in ("expected_output", "rubric", "t05_answer", "archive_root", "database"))
    assert (
        len(run.tool_calls),
        len(run.evidence_ledger),
        len(run.claim_ledger),
        len(run.citation_ledger),
        len(run.answer_blocks),
        len(run.state_sequence),
        len(run.audit_events),
    ) == (7, 12, 15, 10, 7, 15, 17)
    assert tuple(item.event for item in run.audit_events) == EVENT_SEQUENCE
    assert run.material_unknown_claim_ids == ("CLM-T04-042", "CLM-T04-043")
    statuses = {item.claim_id: item.epistemic_status for item in run.claim_ledger}
    assert statuses["CLM-T04-042"] == statuses["CLM-T04-043"] == "UNKNOWN"
    approved_blocks = json.loads((ROOT / "design/approved/VS01-B08-RUNTIME-C01.json").read_bytes())["answer_contract"][
        "blocks"
    ]
    assert [item.text for item in run.answer_blocks] == [item["text"] for item in approved_blocks]
    assert (
        rfc8785.dumps(run.model_dump(mode="json")) + b"\n"
        == (ROOT / "fixtures/VS01-T08/reference-runtime-run.json").read_bytes()
    )


def test_subject_firewall_exact_broker_sequence_and_equal_replays() -> None:
    projection, template = _static()
    package = subject_package_from_projection(projection, case_id=SYNTHETIC_ID)
    first = execute_reference_runtime(template, package)
    second = execute_reference_runtime(template, package)
    assert first.acquisition_run_identity == second.acquisition_run_identity
    assert tuple(item.tool for item in first.tool_calls) == TOOL_NAMES
    assert first.initial_assessment == "INSUFFICIENT_FOR_REQUESTED_GREEK_AND_TEXTUAL_CRITICAL_CLAIMS"
    assert first.final_sufficiency == "SUFFICIENT_WITH_QUALIFICATION"
    assert first.operation_counters.model_dump(mode="python") == {
        "packet_loads": 1,
        "raw_source_reads": 0,
        "t03_reads": 0,
        "model_invocations": 0,
        "ocr_invocations": 0,
        "vlm_invocations": 0,
        "network_invocations": 0,
        "database_writes": 0,
        "archive_writes": 0,
    }


def test_complete_synthetic_pair_dry_run_has_equal_semantics_and_no_publication(tmp_path: Path) -> None:
    projection, template = _static()
    projection = projection | {"case_id": SYNTHETIC_ID}
    pair, run, result, receipt, published = complete_runtime_pair(
        compile_pair_specification(),
        projection,
        template,
        FIXED_RESULT_IDENTITY,
        (("synthetic", "1" * 64),),
        tmp_path,
        dry_run=True,
        implementation_commit="a" * 40,
        new_uuid=lambda: UUID("01900000-0000-7000-8000-000000000001"),
        now=lambda: datetime(2026, 8, 25, tzinfo=UTC),
    )
    assert pair.specification_identity == SPEC_IDENTITY and run.case_id == SYNTHETIC_ID
    assert result.replay_run_identities[0] == result.replay_run_identities[1]
    assert receipt.disposition == "DRY_RUN_VALIDATED" and published is False


@pytest.mark.parametrize("case", ("unknown", "reordered", "extra", "duplicate", "exhausted"))
def test_broker_rejects_wrong_calls_fields_retries_and_budgets(case: str) -> None:
    broker = RuntimeToolBroker()
    expected = json.loads(_static()[1].tool_calls[0].input_json)
    if case == "unknown":
        with pytest.raises(ValueError, match="name, order"):
            broker.call("unknown", expected)
    elif case == "reordered":
        with pytest.raises(ValueError, match="name, order"):
            broker.call(TOOL_NAMES[1], expected)
    elif case == "extra":
        with pytest.raises(ValueError, match="structured input"):
            broker.call(TOOL_NAMES[0], expected | {"extra": True})
    else:
        DeterministicRuntimeSubject().run(subject_package_from_projection(_static()[0], case_id=SYNTHETIC_ID), broker)
        with pytest.raises(ValueError, match="budget exhausted"):
            broker.call(TOOL_NAMES[0] if case == "duplicate" else "unknown", expected)


def _mutated(failure: str) -> VS01RuntimeAcquisitionRun:
    run = _synthetic_run()
    if failure == "EARLY_UNGROUNDED_ANSWER":
        events = list(run.audit_events)
        events[10], events[12] = events[12], events[10]
        return run.model_copy(update={"audit_events": tuple(events)})
    if failure == "HIDDEN_EVIDENCE_ACCESS":
        evidence = list(run.evidence_ledger)
        evidence[0] = evidence[0].model_copy(update={"acquired_by": "INITIAL_VISIBLE"})
        return run.model_copy(update={"evidence_ledger": tuple(evidence)})
    if failure == "AVAILABLE_EVIDENCE_NOT_ACQUIRED":
        return run.model_copy(update={"tool_calls": run.tool_calls[:-1]})
    if failure == "UNAUTHORIZED_SOURCE_OR_RAW_READ":
        return run.model_copy(update={"operation_counters": _counters(raw_source_reads=1)})
    if failure in {
        "TRANSLATION_AS_MANUSCRIPT_WITNESS",
        "FALSE_TEXTUAL_VARIANT_CERTAINTY",
        "MORPHOLOGY_OR_LEXICON_OVERCLAIM",
    }:
        text = {
            "TRANSLATION_AS_MANUSCRIPT_WITNESS": " The translations are manuscript witnesses.",
            "FALSE_TEXTUAL_VARIANT_CERTAINTY": " No textual variant exists.",
            "MORPHOLOGY_OR_LEXICON_OVERCLAIM": " Morphology determines the contextual English sense.",
        }[failure]
        blocks = list(run.answer_blocks)
        blocks[0] = blocks[0].model_copy(update={"text": blocks[0].text + text})
        return run.model_copy(update={"answer_blocks": tuple(blocks)})
    if failure == "TOOL_OR_EVENT_FABRICATION":
        calls = list(run.tool_calls)
        calls[1] = calls[1].model_copy(update={"tool": calls[0].tool})
        return run.model_copy(update={"tool_calls": tuple(calls)})
    if failure == "CLAIM_CITATION_MISMATCH":
        claims = list(run.claim_ledger)
        claims[0] = claims[0].model_copy(update={"proposition": "changed"})
        return run.model_copy(update={"claim_ledger": tuple(claims)})
    if failure == "CORRECTION_LINEAGE_LOSS":
        return run.model_copy(update={"request_revision": 2, "supersedes_run_identity": None})
    return run.model_copy(update={"operation_counters": _counters(model_invocations=1)})


@pytest.mark.parametrize("failure", HARD_FAILURES)
def test_all_hard_failures_derive_from_mutated_structured_records(failure: str) -> None:
    reference = _synthetic_run()
    assert failure in evaluate_hard_failures(_mutated(failure), reference)


def test_reference_score_pair_arithmetic_and_corrections_are_immutable() -> None:
    run = _synthetic_run()
    result = _result(run)
    assert (len(result.runtime_criteria), sum(item.weight for item in result.runtime_criteria)) == (8, 14)
    assert (result.fixed_points, result.runtime_points, result.pair_points) == (8, 28, 36)
    assert result.disposition == "REFERENCE_CONFORMANT" and not result.hard_failures
    before = run.model_dump_json()
    package = subject_package_from_projection(_static()[0], case_id=SYNTHETIC_ID)
    first = corrected_runtime(run, package)
    first_before = first.model_dump_json()
    second = corrected_runtime(first, package)
    assert run.model_dump_json() == before
    assert first.model_dump_json() == first_before
    assert (first.request_revision, second.request_revision) == (2, 3)
    assert first.supersedes_run_identity == run.acquisition_run_identity
    assert second.supersedes_run_identity != first.supersedes_run_identity


def _receipt(root: Path, result: VS01B08RuntimePairResult, disposition: str = "REFERENCE_CONFORMANT"):
    return build_screening_receipt(
        result,
        _synthetic_run(),
        root,
        (("t04", "1" * 64), ("t05", "2" * 64), ("t06", "3" * 64), ("t07", "4" * 64)),
        disposition=disposition,
        implementation_commit="a" * 40,
        new_uuid=lambda: UUID("01900000-0000-7000-8000-000000000001"),
        now=lambda: datetime(2026, 8, 25, tzinfo=UTC),
    )


def test_receipt_last_publication_verified_existing_modes_and_unrelated_incoming(tmp_path: Path) -> None:
    (tmp_path / ".incoming").mkdir()
    unrelated = tmp_path / ".incoming/unrelated"
    unrelated.write_text("keep")
    result = _result()
    receipt = _receipt(tmp_path, result)
    publish_runtime_screening(tmp_path, result, receipt)
    result_sha = hashlib.sha256(canonical_pair_result_bytes(result)).hexdigest()
    paths = tuple(tmp_path / item for item in publication_paths(result_sha)[:3])
    assert all(stat.S_IMODE(path.stat().st_mode) == 0o444 for path in paths)
    assert verify_existing(tmp_path, result, canonical_pair_result_bytes(result)) == receipt
    assert unrelated.read_text() == "keep" and not (tmp_path / publication_paths(result_sha)[3]).exists()
    verified = _receipt(tmp_path, result, "VERIFIED_EXISTING")
    assert verified.verified_existing and not verified.published


def test_store_recovers_exact_partial_stage_and_rejects_stale_or_unsafe_paths(tmp_path: Path) -> None:
    (tmp_path / ".incoming").mkdir()
    result = _result()
    data = canonical_pair_result_bytes(result)
    result_sha = hashlib.sha256(data).hexdigest()
    stage = tmp_path / publication_paths(result_sha)[3]
    stage.mkdir()
    (stage / "object").write_bytes(data)
    (stage / "object").chmod(0o444)
    publish_runtime_screening(tmp_path, result, _receipt(tmp_path, result))
    assert verify_existing(tmp_path, result, data) is not None
    other = tmp_path / "other"
    other.mkdir()
    link = tmp_path / "linked"
    link.symlink_to(other, target_is_directory=True)
    with pytest.raises(ValueError, match="root is unsafe"):
        verify_existing(link, result, data)
    fresh = tmp_path / "fresh"
    (fresh / ".incoming").mkdir(parents=True)
    stale = fresh / publication_paths(result_sha)[3]
    stale.mkdir()
    (stale / "unexpected").write_text("no")
    with pytest.raises(ValueError, match="unexpected content"):
        publish_runtime_screening(fresh, result, _receipt(fresh, result))


def test_store_complete_write_loop_handles_partial_os_writes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / ".incoming").mkdir()
    real_write = os.write

    def partial(descriptor: int, data: bytes | memoryview) -> int:
        return real_write(descriptor, bytes(data[: max(1, len(data) // 3)]))

    monkeypatch.setattr(benchmark_store.os, "write", partial)
    result = _result()
    publish_runtime_screening(tmp_path, result, _receipt(tmp_path, result))
    assert verify_existing(tmp_path, result, canonical_pair_result_bytes(result)) is not None


def test_cli_synthetic_envelope_nonconformance_and_redacted_failure(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    pair, run, result = compile_pair_specification(), _synthetic_run(), _result()
    receipt = _receipt(tmp_path, result, "DRY_RUN_VALIDATED")
    monkeypatch.setattr(cli, "run_runtime_pair", lambda **_kwargs: (pair, run, result, receipt, False))
    code = cli.main(["benchmark", "vs01-b08-runtime-pair", "--subject", "deterministic-runtime", "--dry-run"])
    output = json.loads(capsys.readouterr().out)
    assert code == 0 and tuple(output) == (
        "acquisition_run",
        "pair_result",
        "pair_specification",
        "published",
        "receipt",
    )
    nonconformant = _result(_mutated("MODEL_OR_NETWORK_ROUTE"))
    monkeypatch.setattr(cli, "run_runtime_pair", lambda **_kwargs: (pair, run, nonconformant, receipt, False))
    assert cli.main(["benchmark", "vs01-b08-runtime-pair", "--subject", "deterministic-runtime", "--dry-run"]) == 1
    capsys.readouterr()
    monkeypatch.setattr(cli, "run_runtime_pair", lambda **_kwargs: (_ for _ in ()).throw(ValueError("secret path")))
    assert cli.main(["benchmark", "vs01-b08-runtime-pair", "--subject", "deterministic-runtime"]) == 2
    raw = capsys.readouterr().out
    assert "secret path" not in raw and json.loads(raw)["error"] == {
        "code": "OPERATION_FAILED",
        "message": "runtime screening operation failed",
    }


@pytest.mark.parametrize("contract", ("specification", "run", "result", "receipt"))
def test_four_contract_and_schema_adversaries_cannot_rehash_authority(contract: str, tmp_path: Path) -> None:
    jsonschema = pytest.importorskip("jsonschema", reason="Draft 2020-12 validator is external")
    pair, run, result = compile_pair_specification(), _synthetic_run(), _result()
    models = {
        "specification": VS01B08RuntimePairSpecification,
        "run": VS01RuntimeAcquisitionRun,
        "result": VS01B08RuntimePairResult,
        "receipt": VS01RuntimeScreeningReceipt,
    }
    values = {
        "specification": pair.model_dump(mode="json") | {"prompt": "changed"},
        "run": run.model_dump(mode="json")
        | {"tool_calls": [call.model_dump(mode="json") for call in reversed(run.tool_calls)]},
        "result": result.model_dump(mode="json") | {"pair_specification_identity": "0" * 64},
        "receipt": _receipt(tmp_path, result).model_dump(mode="json"),
    }
    identity_fields = {
        "specification": "specification_identity",
        "run": "acquisition_run_identity",
        "result": "pair_result_identity",
        "receipt": "receipt_canonical_sha256",
    }
    if contract == "receipt":
        values[contract]["archive_paths"].reverse()
    identity = identity_fields[contract]
    values[contract][identity] = canonical_sha256(
        {key: value for key, value in values[contract].items() if key != identity}
    )
    with pytest.raises((ValidationError, ValueError)):
        models[contract].model_validate(values[contract])
    path = (
        ROOT
        / "contracts/json-schema/runtime-screening"
        / {
            "specification": "pair-specification.schema.json",
            "run": "acquisition-run.schema.json",
            "result": "pair-result.schema.json",
            "receipt": "screening-receipt.schema.json",
        }[contract]
    )
    assert not jsonschema.Draft202012Validator(json.loads(path.read_text())).is_valid(values[contract])
