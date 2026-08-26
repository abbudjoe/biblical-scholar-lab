from __future__ import annotations

import copy
import hashlib
import json
import os
import stat
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import UUID

import pytest
import rfc8785
from pydantic import ValidationError

import bsl.application.vs01_runtime_screening as runtime_screening
import bsl.infrastructure.benchmark_store as benchmark_store
import bsl.infrastructure.runtime_screening_store as screening_store
import bsl.interfaces.cli as cli
from bsl.application.vs01_benchmark import load_benchmark_authority
from bsl.application.vs01_runtime_reference import (
    complete_runtime_pair,
    corrected_runtime,
    execute_reference_runtime,
    subject_package_from_projection,
)
from bsl.application.vs01_runtime_scoring import score_runtime_pair
from bsl.application.vs01_runtime_screening import compile_pair_specification
from bsl.contracts.runtime_screening import (
    CASE_IDENTITY,
    CORRECTION_PROMPT,
    EVENT_SEQUENCE,
    FINGERPRINT_NAMES,
    FIXED_CASE_RESULT_IDENTITY,
    HARD_FAILURES,
    INITIAL_EVIDENCE,
    SPEC_IDENTITY,
    SYNTHETIC_CASE_ID,
    TOOL_NAMES,
    RuntimeControllerLedger,
    VS01B08RuntimePairResult,
    VS01B08RuntimePairSpecification,
    VS01RuntimeAcquisitionRun,
    VS01RuntimeScreeningReceipt,
    canonical_sha256,
)
from bsl.infrastructure.runtime_screening_store import (
    RetainedPublicationAuthority,
    build_screening_receipt,
    canonical_pair_result_bytes,
    publication_paths,
    publish_runtime_screening,
    verify_existing,
)

ROOT = Path(__file__).parents[1]
FINGERPRINTS: tuple[tuple[str, str], ...] = tuple(
    (name, str(index) * 64) for index, name in enumerate(FINGERPRINT_NAMES, 1)
)


def NOW() -> datetime:
    return datetime(2026, 8, 25, tzinfo=UTC)


def UUID1() -> UUID:
    return UUID("01900000-0000-7000-8000-000000000001")


def _static() -> tuple[dict[str, Any], VS01RuntimeAcquisitionRun]:
    projection = json.loads((ROOT / "fixtures/VS01-T08/runtime-subject-projection.json").read_bytes())
    run = VS01RuntimeAcquisitionRun.model_validate_json(
        (ROOT / "fixtures/VS01-T08/reference-runtime-run.json").read_bytes()
    )
    return projection, run


def _synthetic_run() -> VS01RuntimeAcquisitionRun:
    projection, template = _static()
    package = subject_package_from_projection(projection, case_id=SYNTHETIC_CASE_ID)
    return execute_reference_runtime(template, package)


def _result(run: VS01RuntimeAcquisitionRun | None = None) -> VS01B08RuntimePairResult:
    value = run or _synthetic_run()
    return score_runtime_pair(
        compile_pair_specification(),
        value,
        value,
        FIXED_CASE_RESULT_IDENTITY,
        (value.acquisition_run_identity, value.acquisition_run_identity),
    )


def _rehash(payload: dict[str, Any], identity: str) -> dict[str, Any]:
    payload[identity] = canonical_sha256({key: value for key, value in payload.items() if key != identity})
    return payload


def _no_go() -> VS01B08RuntimePairResult:
    payload = _result().model_dump(mode="json")
    payload["runtime_criteria"][0] |= {"score": 0, "points": 0}
    payload |= {
        "runtime_points": 24,
        "pair_points": 32,
        "hard_failures": [HARD_FAILURES[0]],
        "disposition": "RUNTIME_SCREENING_NO_GO",
    }
    return VS01B08RuntimePairResult.model_validate_json(rfc8785.dumps(_rehash(payload, "pair_result_identity")))


def _ledger(disposition: str) -> RuntimeControllerLedger:
    store, attempts, success, writes = {
        "DRY_RUN_VALIDATED": (0, 0, 0, 0),
        "REFERENCE_NONCONFORMANT": (0, 0, 0, 0),
        "REFERENCE_CONFORMANT": (2, 1, 1, 3),
        "VERIFIED_EXISTING": (1, 0, 0, 0),
    }[disposition]
    values = dict.fromkeys(RuntimeControllerLedger.model_fields, 0)
    values |= {
        "subject_invocations": 2,
        "broker_tool_calls": 14,
        "scoring_invocations": 1,
        "acquisition_runs_constructed": 2,
        "pair_results_constructed": 1,
        "receipts_constructed": 1,
        "store_verification_attempts": store,
        "publication_attempts": attempts,
        "successful_publications": success,
        "canonical_archive_writes": writes,
    }
    return RuntimeControllerLedger.model_validate(values)


def _receipt(
    root: Path,
    result: VS01B08RuntimePairResult,
    disposition: str,
    retained: RetainedPublicationAuthority | None = None,
    new_uuid: Callable[[], UUID] = UUID1,
) -> VS01RuntimeScreeningReceipt:
    return build_screening_receipt(
        result,
        _synthetic_run(),
        root,
        FINGERPRINTS,
        pre_store_fingerprints=FINGERPRINTS,
        post_store_fingerprints=FINGERPRINTS,
        operation_ledger=_ledger(disposition),
        disposition=disposition,
        implementation_commit="a" * 40,
        new_uuid=new_uuid,
        now=NOW,
        retained=retained,
    )


def test_frozen_authority_and_exact_public_shapes() -> None:
    pair = compile_pair_specification()
    case = (ROOT / "design/approved/VS01-B08-RUNTIME-C01.json").read_bytes()
    spec = (ROOT / "design/approved/VS01-T08-runtime-pair-spec.json").read_bytes()
    assert hashlib.sha256(case).hexdigest() == "a7fc02da5ed8fda15ee29cba79cff8b037b2abc66352107f87165a0bfbea9f0f"
    assert hashlib.sha256(spec).hexdigest() == "9e49e2f2b540a54c1d945991eb6500a52c0a7873136630d8bf49854efeb765ba"
    assert (pair.runtime_case_content_sha256, pair.specification_identity) == (CASE_IDENTITY, SPEC_IDENTITY)
    assert load_benchmark_authority()[7].source["prompt"] == pair.prompt
    projection, run = _static()
    assert tuple(item["name"] for item in projection["tool_schemas"]) == TOOL_NAMES
    assert tuple(projection["initial_evidence"]) == INITIAL_EVIDENCE
    assert (len(run.tool_calls), len(run.evidence_ledger), len(run.claim_ledger)) == (7, 12, 15)
    assert (len(run.citation_ledger), len(run.answer_blocks), len(run.audit_events)) == (10, 7, 17)
    assert tuple(item.event for item in run.audit_events) == EVENT_SEQUENCE
    assert (
        rfc8785.dumps(run.model_dump(mode="json")) + b"\n"
        == (ROOT / "fixtures/VS01-T08/reference-runtime-run.json").read_bytes()
    )


def test_authority_compilation_and_reload_are_read_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from test_study_runtime import _authority  # pyright: ignore[reportPrivateUsage]
    from test_vs01_benchmark import _run  # pyright: ignore[reportPrivateUsage]

    tmp_path.joinpath(".incoming").mkdir()
    fixed = _run()

    def load_t04(_root: Path):
        return _authority(tmp_path)

    def dump_t06(**_kwargs: Any) -> dict[str, str]:
        return {"t06": "verified"}

    def load_t06(*_args: Any) -> SimpleNamespace:
        return SimpleNamespace(receipt_identity=UUID("01a034c2-d6e4-73f4-91b2-7410e7453783"), model_dump=dump_t06)

    def load_t07(_root: Path) -> tuple[Any, SimpleNamespace, str]:
        return (
            fixed,
            SimpleNamespace(receipt_id=UUID("01a03a85-e49b-7d1c-b737-b560fd9a17df")),
            "f" * 64,
        )

    monkeypatch.setattr(runtime_screening, "load_t04_authority", load_t04)
    monkeypatch.setattr(runtime_screening, "verify_t06_existing", load_t06)
    monkeypatch.setattr(runtime_screening, "_load_t07", load_t07)

    def verifier(_t04: Any) -> dict[str, Any]:
        return {"t05": "verified", "database_writes": 0}

    authority = runtime_screening.compile_runtime_authority(tmp_path, _t05_verifier=verifier)
    reloaded = runtime_screening.reload_runtime_authority_fingerprints(tmp_path, _t05_verifier=verifier)
    assert authority.authority_fingerprints == reloaded
    assert tuple(name for name, _value in reloaded) == FINGERPRINT_NAMES
    assert authority.fixed_case_result_identity == fixed.case_results[7].case_result_identity


@pytest.mark.parametrize(
    ("target", "field"),
    (
        ("initial", "runtime_evidence_id"),
        ("initial", "source_handle"),
        ("initial", "source_role"),
        ("initial", "state"),
        ("initial", "exact_excerpt"),
        ("tool", "input_schema_json"),
        ("tool", "output_schema_json"),
        ("budget", "calls_per_tool"),
        ("output", "answer_blocks"),
    ),
)
def test_positive_subject_firewall_rejects_every_changed_authority(target: str, field: str) -> None:
    projection, _run = _static()
    changed = copy.deepcopy(projection)
    if target == "initial":
        changed["initial_evidence"][0][field] = "changed"
    elif target == "tool":
        changed["tool_schemas"][0][field] = "{}"
    elif target == "budget":
        changed["budgets"][field] = 2
    else:
        changed["output_schema"][field] = 8
    with pytest.raises((ValueError, ValidationError)):
        subject_package_from_projection(changed, case_id=SYNTHETIC_CASE_ID)


def test_subject_order_broker_and_genuine_correction_lineage() -> None:
    projection, template = _static()
    reordered = copy.deepcopy(projection)
    reordered["tool_schemas"].reverse()
    with pytest.raises(ValueError):
        subject_package_from_projection(reordered, case_id=SYNTHETIC_CASE_ID)
    initial_package = subject_package_from_projection(projection, case_id=SYNTHETIC_CASE_ID)
    before = execute_reference_runtime(template, initial_package)
    frozen = before.model_dump_json()
    correction_package = subject_package_from_projection(
        projection, case_id=SYNTHETIC_CASE_ID, prompt=CORRECTION_PROMPT
    )
    corrected = corrected_runtime(before, correction_package)
    assert before.model_dump_json() == frozen
    assert corrected.prompt != before.prompt and corrected.request_identity != before.request_identity
    assert corrected.plan_identity != before.plan_identity
    assert corrected.answer_projection_identity != before.answer_projection_identity
    assert corrected.acquisition_run_identity != before.acquisition_run_identity
    assert corrected.supersedes_request_identity == before.request_identity
    assert corrected.supersedes_run_identity == before.acquisition_run_identity
    assert len(corrected.tool_calls) == 7
    assert json.loads(corrected.tool_calls[0].input_json)["prompt"] == CORRECTION_PROMPT
    with pytest.raises(ValueError):
        corrected_runtime(corrected, correction_package)


@pytest.mark.parametrize(
    "field", ("evidence_id", "source_handle", "source_role", "selector", "exact_excerpt", "acquired_by")
)
def test_run_rejects_rehashed_evidence_provenance(field: str) -> None:
    payload = _synthetic_run().model_dump(mode="json")
    payload["evidence_ledger"][0][field] = "changed"
    with pytest.raises(ValidationError):
        VS01RuntimeAcquisitionRun.model_validate_json(rfc8785.dumps(_rehash(payload, "acquisition_run_identity")))


@pytest.mark.parametrize(
    "part", ("evidence_order", "tool_input", "tool_output", "event_chain", "claim", "citation", "block")
)
def test_run_rejects_rehashed_internal_record_mutations(part: str) -> None:
    payload = _synthetic_run().model_dump(mode="json")
    if part == "evidence_order":
        payload["evidence_ledger"][0], payload["evidence_ledger"][1] = (
            payload["evidence_ledger"][1],
            payload["evidence_ledger"][0],
        )
    elif part.startswith("tool_"):
        key = "input_json" if part == "tool_input" else "output_json"
        sha = "input_sha256" if part == "tool_input" else "output_sha256"
        value = json.loads(payload["tool_calls"][0][key]) | {"changed": True}
        payload["tool_calls"][0] |= {key: rfc8785.dumps(value).decode(), sha: canonical_sha256(value)}
    elif part == "event_chain":
        payload["audit_events"][1]["previous_event_sha256"] = "0" * 64
        payload["audit_events"][1]["event_semantic_sha256"] = canonical_sha256(
            {k: v for k, v in payload["audit_events"][1].items() if k != "event_semantic_sha256"}
        )
    else:
        ledger = {"claim": "claim_ledger", "citation": "citation_ledger", "block": "answer_blocks"}[part]
        key = {"claim": "proposition", "citation": "selector", "block": "text"}[part]
        payload[ledger][0][key] = "changed"
    with pytest.raises(ValidationError):
        VS01RuntimeAcquisitionRun.model_validate_json(rfc8785.dumps(_rehash(payload, "acquisition_run_identity")))


@pytest.mark.parametrize(
    "part",
    (
        "fixed_id",
        "fixed_points",
        "criterion_id",
        "weight",
        "score",
        "points",
        "hard_failure",
        "leakage",
        "replay",
        "tools",
        "events",
        "limitations",
        "disposition",
    ),
)
def test_pair_result_rejects_rehashed_contradictions(part: str) -> None:
    payload = _result().model_dump(mode="json")
    if part == "fixed_id":
        payload["fixed_case_result_identity"] = "0" * 64
    elif part == "fixed_points":
        payload["fixed_points"] = 7
        payload["pair_points"] = 35
    elif part in {"criterion_id", "weight", "score", "points"}:
        payload["runtime_criteria"][0][part] = 1 if part != "criterion_id" else "changed"
    elif part == "hard_failure":
        payload["hard_failures"] = [HARD_FAILURES[0]]
    elif part == "leakage":
        payload["leakage_incidents"] = 1
    elif part == "replay":
        payload["replay_run_identities"][1] = "0" * 64
    elif part == "tools":
        payload["tool_calls_observed"] = 6
    elif part == "events":
        payload["events_observed"] = 16
    elif part == "limitations":
        payload["limitations"][0] = "changed"
    else:
        payload["disposition"] = "RUNTIME_SCREENING_NO_GO"
    with pytest.raises(ValidationError):
        VS01B08RuntimePairResult.model_validate_json(rfc8785.dumps(_rehash(payload, "pair_result_identity")))


def test_controller_ledgers_reload_and_retained_receipt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    projection, template = _static()
    tmp_path.joinpath(".incoming").mkdir()
    arguments = (compile_pair_specification(), projection, template, FIXED_CASE_RESULT_IDENTITY, FINGERPRINTS, tmp_path)
    dry = complete_runtime_pair(*arguments, dry_run=True, implementation_commit="a" * 40, _case_id=SYNTHETIC_CASE_ID)
    assert dry[3].operation_ledger == _ledger("DRY_RUN_VALIDATED")
    loads: list[int] = []

    def loader():
        loads.append(1)
        return FINGERPRINTS

    live = complete_runtime_pair(
        *arguments,
        dry_run=False,
        authority_loader=loader,
        implementation_commit="a" * 40,
        new_uuid=UUID1,
        now=NOW,
        _case_id=SYNTHETIC_CASE_ID,
    )
    assert len(loads) == 2 and live[3].operation_ledger == _ledger("REFERENCE_CONFORMANT")
    assert live[3].published and live[4]
    ids = iter((UUID("01900000-0000-7000-8000-000000000002"),))
    existing = complete_runtime_pair(
        *arguments,
        dry_run=False,
        authority_loader=loader,
        implementation_commit="a" * 40,
        new_uuid=lambda: next(ids),
        now=NOW,
        _case_id=SYNTHETIC_CASE_ID,
    )
    receipt = existing[3]
    assert receipt.operation_ledger == _ledger("VERIFIED_EXISTING") and receipt.verified_existing
    assert receipt.retained_publication_receipt == live[3]
    assert receipt.retained_publication_receipt_id == live[3].receipt_id
    assert (
        receipt.retained_publication_receipt_file_sha256
        == hashlib.sha256(rfc8785.dumps(live[3].model_dump(mode="json"))).hexdigest()
    )
    assert _receipt(tmp_path, _no_go(), "REFERENCE_NONCONFORMANT").operation_ledger == _ledger(
        "REFERENCE_NONCONFORMANT"
    )


@pytest.mark.parametrize("phase", ("pre", "post"))
def test_changed_authority_load_stops_before_mutation(
    phase: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    projection, template = _static()
    tmp_path.joinpath(".incoming").mkdir()
    calls = 0
    original = screening_store.verify_existing

    def counted(*args: Any, **kwargs: Any):
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(screening_store, "verify_existing", counted)
    changed = (("t04", "0" * 64), *FINGERPRINTS[1:])
    values = iter((changed,) if phase == "pre" else (FINGERPRINTS, changed))
    with pytest.raises(ValueError, match="authority changed"):
        complete_runtime_pair(
            compile_pair_specification(),
            projection,
            template,
            FIXED_CASE_RESULT_IDENTITY,
            FINGERPRINTS,
            tmp_path,
            dry_run=False,
            authority_loader=lambda: next(values),
            implementation_commit="a" * 40,
            _case_id=SYNTHETIC_CASE_ID,
        )
    assert calls == (0 if phase == "pre" else 1)
    assert list(tmp_path.joinpath(".incoming").iterdir()) == []


@pytest.mark.parametrize("part", ("count", "flags", "disposition", "pair", "retained_id", "retained_sha"))
def test_receipt_rejects_rehashed_contradictions(part: str, tmp_path: Path) -> None:
    result = _result()
    if part.startswith("retained"):
        tmp_path.joinpath(".incoming").mkdir()
        published = _receipt(tmp_path, result, "REFERENCE_CONFORMANT")
        publish_runtime_screening(tmp_path, result, published)
        retained = verify_existing(
            tmp_path,
            result,
            canonical_pair_result_bytes(result),
            implementation_commit="a" * 40,
            fingerprints=FINGERPRINTS,
        )
        assert retained
        payload = _receipt(
            tmp_path,
            result,
            "VERIFIED_EXISTING",
            retained,
            new_uuid=lambda: UUID("01900000-0000-7000-8000-000000000002"),
        ).model_dump(mode="json")
    else:
        payload = _receipt(tmp_path, result, "DRY_RUN_VALIDATED").model_dump(mode="json")
    if part == "count":
        payload["operation_ledger"]["subject_invocations"] = 3
    elif part == "flags":
        payload["published"] = True
    elif part == "disposition":
        payload["disposition"] = "REFERENCE_CONFORMANT"
    elif part == "pair":
        payload["pair_result"]["fixed_points"] = 7
    elif part == "retained_id":
        payload["retained_publication_receipt_id"] = "01900000-0000-7000-8000-000000000099"
    else:
        payload["retained_publication_receipt_file_sha256"] = "0" * 64
    with pytest.raises(ValidationError):
        VS01RuntimeScreeningReceipt.model_validate_json(rfc8785.dumps(_rehash(payload, "receipt_canonical_sha256")))


@pytest.mark.parametrize("part", ("acquisition", "commit", "fingerprints", "pair_result", "noncanonical", "mutable"))
def test_retained_receipt_full_store_binding(part: str, tmp_path: Path) -> None:
    tmp_path.joinpath(".incoming").mkdir()
    result = _result()
    receipt = _receipt(tmp_path, result, "REFERENCE_CONFORMANT")
    publish_runtime_screening(tmp_path, result, receipt)
    result_sha = hashlib.sha256(canonical_pair_result_bytes(result)).hexdigest()
    path = tmp_path / publication_paths(result_sha)[2]
    if part == "mutable":
        path.chmod(0o644)
    else:
        payload = receipt.model_dump(mode="json")
        if part == "acquisition":
            payload["acquisition_run_identity"] = "0" * 64
        elif part == "commit":
            payload["implementation_commit"] = "b" * 40
        elif part == "fingerprints":
            payload["authority_fingerprints_initial"][0][1] = "0" * 64
        elif part == "pair_result":
            payload["pair_result_identity"] = "0" * 64
        payload = _rehash(payload, "receipt_canonical_sha256")
        path.chmod(0o644)
        path.write_bytes(rfc8785.dumps(payload) + (b"\n" if part == "noncanonical" else b""))
        path.chmod(0o444)
    with pytest.raises(ValueError):
        verify_existing(
            tmp_path,
            result,
            canonical_pair_result_bytes(result),
            implementation_commit="a" * 40,
            fingerprints=FINGERPRINTS,
        )


def test_receipt_last_store_recovery_modes_and_partial_writes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tmp_path.joinpath(".incoming").mkdir()
    unrelated = tmp_path / ".incoming/unrelated"
    unrelated.write_text("keep")
    real_write = os.write

    def partial(fd: int, data: bytes | memoryview) -> int:
        return real_write(fd, bytes(data[: max(1, len(data) // 3)]))

    monkeypatch.setattr(benchmark_store.os, "write", partial)
    result = _result()
    receipt = _receipt(tmp_path, result, "REFERENCE_CONFORMANT")
    publish_runtime_screening(tmp_path, result, receipt)
    retained = verify_existing(
        tmp_path,
        result,
        canonical_pair_result_bytes(result),
        implementation_commit="a" * 40,
        fingerprints=FINGERPRINTS,
    )
    assert retained and retained.retained_receipt == receipt and unrelated.read_text() == "keep"
    result_sha = hashlib.sha256(canonical_pair_result_bytes(result)).hexdigest()
    assert all(stat.S_IMODE((tmp_path / path).stat().st_mode) == 0o444 for path in publication_paths(result_sha)[:3])


def test_cli_redacts_failures(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    def failure(**_kwargs: Any):
        raise ValueError("secret path")

    monkeypatch.setattr(cli, "run_runtime_pair", failure)
    assert cli.main(["benchmark", "vs01-b08-runtime-pair", "--subject", "deterministic-runtime"]) == 2
    output = capsys.readouterr().out
    assert "secret path" not in output and json.loads(output)["error"]["code"] == "OPERATION_FAILED"


@pytest.mark.parametrize("contract", ("specification", "run", "result", "receipt"))
def test_pydantic_and_draft202012_reject_rehashed_outer_adversaries(contract: str, tmp_path: Path) -> None:
    jsonschema = pytest.importorskip("jsonschema", reason="Draft 2020-12 validator is external")
    pair, run, result = compile_pair_specification(), _synthetic_run(), _result()
    model, value, identity, schema_name = {
        "specification": (
            VS01B08RuntimePairSpecification,
            pair.model_dump(mode="json"),
            "specification_identity",
            "pair-specification",
        ),
        "run": (VS01RuntimeAcquisitionRun, run.model_dump(mode="json"), "acquisition_run_identity", "acquisition-run"),
        "result": (VS01B08RuntimePairResult, result.model_dump(mode="json"), "pair_result_identity", "pair-result"),
        "receipt": (
            VS01RuntimeScreeningReceipt,
            _receipt(tmp_path, result, "DRY_RUN_VALIDATED").model_dump(mode="json"),
            "receipt_canonical_sha256",
            "screening-receipt",
        ),
    }[contract]
    if contract == "specification":
        value["prompt"] = "changed"
    elif contract == "run":
        value["claim_ledger"][0]["proposition"] = "changed"
    elif contract == "result":
        value["fixed_points"] = 7
        value["pair_points"] = 35
    else:
        value["operation_ledger"]["subject_invocations"] = 3
    value = _rehash(value, identity)
    with pytest.raises((ValidationError, ValueError)):
        model.model_validate_json(rfc8785.dumps(value))
    schema = json.loads((ROOT / f"contracts/json-schema/runtime-screening/{schema_name}.schema.json").read_text())
    assert not jsonschema.Draft202012Validator(schema).is_valid(value)
