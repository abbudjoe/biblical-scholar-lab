# ruff: noqa: SIM905
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
from typing import Any, cast
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
    DeterministicRuntimeSubject,
    RuntimeSubjectTrace,
    RuntimeToolBroker,
    complete_runtime_pair,
    corrected_runtime,
    execute_reference_runtime,
    subject_package_from_projection,
)
from bsl.application.vs01_runtime_scoring import score_runtime_pair
from bsl.application.vs01_runtime_screening import compile_pair_specification
from bsl.contracts.runtime_screening import (
    CASE_IDENTITY,
    CORRECTION_ANSWER_SENTENCE,
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
    VS01RuntimeAcquisitionRun,
    VS01RuntimeScreeningReceipt,
    canonical_sha256,
)
from bsl.infrastructure.runtime_screening_store import (
    CanonicalRecoveryState,
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


def _ledger(disposition: str, recovery: str | None = None) -> RuntimeControllerLedger:
    recovery = recovery or ({"REFERENCE_CONFORMANT": "EMPTY", "VERIFIED_EXISTING": "COMPLETE"}.get(disposition))
    live, existing = disposition == "REFERENCE_CONFORMANT", disposition == "VERIFIED_EXISTING"
    store, attempts, success = 2 * int(live) + int(existing), int(live), int(live)
    writes = {"EMPTY": 3, "OBJECT_ONLY": 2, "OBJECT_AND_SNAPSHOT": 1}.get(recovery or "", 0)
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
    recovery: str | None = None,
) -> VS01RuntimeScreeningReceipt:
    recovery = recovery or ({"REFERENCE_CONFORMANT": "EMPTY", "VERIFIED_EXISTING": "COMPLETE"}.get(disposition))
    return build_screening_receipt(
        result,
        _synthetic_run(),
        root,
        FINGERPRINTS,
        pre_store_fingerprints=FINGERPRINTS,
        post_store_fingerprints=FINGERPRINTS,
        recovery_state=recovery,
        operation_ledger=_ledger(disposition, recovery),
        disposition=disposition,
        implementation_commit="a" * 40,
        new_uuid=new_uuid,
        now=NOW,
        retained=retained,
    )


def _publish(root: Path, result: VS01B08RuntimePairResult, receipt: VS01RuntimeScreeningReceipt) -> None:
    writes = screening_store._prepare_result_store(  # pyright: ignore[reportPrivateUsage]
        root, result, cast(CanonicalRecoveryState, receipt.canonical_recovery_state or "EMPTY")
    )
    assert (
        writes + publish_runtime_screening(root, result, receipt) == receipt.operation_ledger.canonical_archive_writes
    )


def _inspect(root: Path, result: VS01B08RuntimePairResult) -> Any:
    return verify_existing(
        root,
        result,
        canonical_pair_result_bytes(result),
        implementation_commit="a" * 40,
        fingerprints=FINGERPRINTS,
    )


def _live_campaign(
    root: Path,
    loader: Callable[[], tuple[tuple[str, str], ...]],
    new_uuid: Callable[[], UUID] = UUID1,
) -> tuple[Any, ...]:
    projection, template = _static()
    return complete_runtime_pair(
        compile_pair_specification(),
        projection,
        template,
        FIXED_CASE_RESULT_IDENTITY,
        FINGERPRINTS,
        root,
        dry_run=False,
        authority_loader=loader,
        implementation_commit="a" * 40,
        new_uuid=new_uuid,
        now=NOW,
        _case_id=SYNTHETIC_CASE_ID,
    )


def _published_authority(
    root: Path,
) -> tuple[VS01B08RuntimePairResult, VS01RuntimeScreeningReceipt, RetainedPublicationAuthority]:
    result = _result()
    live = _receipt(root, result, "REFERENCE_CONFORMANT")
    _publish(root, result, live)
    inspected = _inspect(root, result)
    assert inspected.retained
    return result, live, inspected.retained


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
    "case",
    (
        "initial:runtime_evidence_id initial:source_handle initial:source_role initial:state "
        "initial:exact_excerpt tool:input_schema_json tool:output_schema_json budget:calls_per_tool "
        "output:answer_blocks"
    ).split(),
)
def test_positive_subject_firewall_rejects_every_changed_authority(case: str) -> None:
    target, field = case.split(":")
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


def test_live_projection_output_schema_order_is_semantic() -> None:
    live = runtime_screening._subject_projection(  # pyright: ignore[reportPrivateUsage]
        compile_pair_specification()
    )
    reordered = copy.deepcopy(live)
    reordered["output_schema"] = dict(reversed(tuple(live["output_schema"].items())))
    assert tuple(live["output_schema"]) != tuple(reordered["output_schema"])

    live_package = subject_package_from_projection(live, case_id="VS01-B08-RUNTIME-C01")
    reordered_package = subject_package_from_projection(reordered, case_id="VS01-B08-RUNTIME-C01")
    assert live_package.output_schema == reordered_package.output_schema
    assert live_package.package_identity == reordered_package.package_identity

    changed = copy.deepcopy(live)
    changed["output_schema"]["answer_blocks"] = 8
    with pytest.raises(ValueError):
        subject_package_from_projection(changed, case_id="VS01-B08-RUNTIME-C01")


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
    assert CORRECTION_ANSWER_SENTENCE in corrected.answer_blocks[5].text
    assert corrected.acquisition_run_identity != before.acquisition_run_identity
    assert corrected.supersedes_request_identity == before.request_identity
    assert corrected.supersedes_run_identity == before.acquisition_run_identity
    assert len(corrected.tool_calls) == 7
    assert json.loads(corrected.tool_calls[0].input_json)["prompt"] == CORRECTION_PROMPT
    with pytest.raises(ValueError):
        corrected_runtime(corrected, correction_package)


@pytest.mark.parametrize("part", ("initial", "final", "missing", "reordered", "fabricated", "previous"))
def test_correction_rejects_false_or_nonbroker_trace(part: str) -> None:
    projection, template = _static()
    before = execute_reference_runtime(template, subject_package_from_projection(projection, case_id=SYNTHETIC_CASE_ID))
    package = subject_package_from_projection(projection, case_id=SYNTHETIC_CASE_ID, prompt=CORRECTION_PROMPT)

    class BrokenSubject:
        def run(self, value: Any, broker: RuntimeToolBroker) -> RuntimeSubjectTrace:
            if part == "previous":
                object.__setattr__(before, "prompt", "mutated")
            if part == "fabricated":
                return DeterministicRuntimeSubject().run(value, RuntimeToolBroker(CORRECTION_PROMPT))
            trace = DeterministicRuntimeSubject().run(value, broker)
            calls = trace.tool_calls
            if part == "missing":
                calls = calls[:-1]
            elif part == "reordered":
                calls = (calls[1], calls[0], *calls[2:])
            return RuntimeSubjectTrace(
                "changed" if part == "initial" else trace.initial_assessment,
                calls,
                "changed" if part == "final" else trace.final_sufficiency,
            )

    with pytest.raises(ValueError):
        corrected_runtime(before, package, BrokenSubject())


@pytest.mark.parametrize("part", ("answer_projection", "answer_identity", "supersession"))
def test_correction_rejects_rehashed_prior_answer_or_lineage(part: str) -> None:
    projection, template = _static()
    before = execute_reference_runtime(template, subject_package_from_projection(projection, case_id=SYNTHETIC_CASE_ID))
    package = subject_package_from_projection(projection, case_id=SYNTHETIC_CASE_ID, prompt=CORRECTION_PROMPT)
    payload = corrected_runtime(before, package).model_dump(mode="json")
    if part == "answer_projection":
        payload["answer_blocks"] = before.model_dump(mode="json")["answer_blocks"]
        payload["answer_projection_identity"] = before.answer_projection_identity
    elif part == "answer_identity":
        payload["answer_projection_identity"] = before.answer_projection_identity
    else:
        payload["supersedes_request_identity"] = "0" * 64
    with pytest.raises(ValidationError):
        VS01RuntimeAcquisitionRun.model_validate_json(rfc8785.dumps(_rehash(payload, "acquisition_run_identity")))


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


def test_acquisition_run_draft_rejects_rehashed_semantic_mutation() -> None:
    jsonschema = pytest.importorskip("jsonschema", reason="Draft 2020-12 validator is external")
    payload = _synthetic_run().model_dump(mode="json")
    payload["claim_ledger"][0]["proposition"] = "changed"
    schema = json.loads((ROOT / "contracts/json-schema/runtime-screening/acquisition-run.schema.json").read_text())
    assert not jsonschema.Draft202012Validator(schema).is_valid(_rehash(payload, "acquisition_run_identity"))


PAIR_MUTATIONS: dict[str, tuple[tuple[str | int, ...], Any]] = {
    "fixed_id": (("fixed_case_result_identity",), "0" * 64),
    "fixed_points": (("fixed_points",), 7),
    "criterion_id": (("runtime_criteria", 0, "criterion_id"), "changed"),
    "weight": (("runtime_criteria", 0, "weight"), 3),
    "score": (("runtime_criteria", 0, "score"), 1),
    "points": (("runtime_criteria", 0, "points"), 0),
    "criterion_arithmetic": (("runtime_criteria", 0, "score"), 1),
    "runtime_arithmetic": (("runtime_points",), 27),
    "pair_arithmetic": (("pair_points",), 35),
    "hard_failure": (("hard_failures",), [HARD_FAILURES[0]]),
    "duplicate_hard_failure": (("hard_failures",), [HARD_FAILURES[0]] * 2),
    "unauthorized_hard_failure": (("hard_failures",), ["UNAUTHORIZED"]),
    "leakage": (("leakage_incidents",), 1),
    "replay": (("replay_run_identities", 1), "0" * 64),
    "acquisition_replay": (("acquisition_run_identity",), "0" * 64),
    "tools": (("tool_calls_observed",), 6),
    "events": (("events_observed",), 16),
    "limitations": (("limitations", 0), "changed"),
    "disposition": (("disposition",), "RUNTIME_SCREENING_NO_GO"),
    "state_combination": (("disposition",), "RUNTIME_SCREENING_PASS_WITH_EXPLICIT_LIMITATIONS"),
}


def _set_path(payload: dict[str, Any], path: tuple[str | int, ...], value: Any) -> None:
    target: Any = payload
    for step in path[:-1]:
        target = target[step]
    target[path[-1]] = value


def _pair_adversary(part: str) -> dict[str, Any]:
    payload = _result().model_dump(mode="json")
    _set_path(payload, *PAIR_MUTATIONS[part])
    if part == "score":
        criterion = payload["runtime_criteria"][0]
        criterion["points"] = criterion["weight"]
    return _rehash(payload, "pair_result_identity")


@pytest.mark.parametrize("part", PAIR_MUTATIONS)
def test_pair_result_draft202012_matches_material_state_machine(part: str) -> None:
    jsonschema = pytest.importorskip("jsonschema", reason="Draft 2020-12 validator is external")
    payload = _pair_adversary(part)
    with pytest.raises(ValidationError):
        VS01B08RuntimePairResult.model_validate_json(rfc8785.dumps(payload))
    schema = json.loads((ROOT / "contracts/json-schema/runtime-screening/pair-result.schema.json").read_text())
    validator = jsonschema.Draft202012Validator(schema)
    assert validator.is_valid(_result().model_dump(mode="json")) and not validator.is_valid(payload)


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

    live = _live_campaign(tmp_path, loader)
    assert len(loads) == 2 and live[3].operation_ledger == _ledger("REFERENCE_CONFORMANT")
    assert live[3].canonical_recovery_state == "EMPTY"
    assert live[3].published and live[4]
    ids = iter((UUID("01900000-0000-7000-8000-000000000002"),))
    existing = _live_campaign(tmp_path, loader, lambda: next(ids))
    receipt = existing[3]
    assert receipt.operation_ledger == _ledger("VERIFIED_EXISTING") and receipt.verified_existing
    assert receipt.canonical_recovery_state == "COMPLETE"
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
        _live_campaign(tmp_path, lambda: next(values))
    assert calls == (0 if phase == "pre" else 1)
    result_sha = hashlib.sha256(canonical_pair_result_bytes(_result())).hexdigest()
    exists = tuple((tmp_path / path).exists() for path in publication_paths(result_sha)[:3])
    assert exists == ((False, False, False) if phase == "pre" else (True, True, False))
    assert list(tmp_path.joinpath(".incoming").iterdir()) == []


def test_store_ordering_places_post_reload_between_result_and_receipt_links(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tmp_path.joinpath(".incoming").mkdir()
    events: list[str] = []
    real_verify = screening_store.verify_existing
    real_link = screening_store._link_exact  # pyright: ignore[reportPrivateUsage]
    real_clean = screening_store._clean_exact_stage  # pyright: ignore[reportPrivateUsage]
    links = 0
    reloads = 0

    def loader():
        nonlocal reloads
        reloads += 1
        events.append(f"reload:{reloads}")
        return FINGERPRINTS

    def checked(*args: Any, **kwargs: Any):
        value = real_verify(*args, **kwargs)
        events.append(f"verify:{value.recovery_state}")
        return value

    def linked(source: Path, destination: Path, expected: bytes) -> bool:
        nonlocal links
        value = real_link(source, destination, expected)
        links += 1
        events.append(f"link:{links}")
        return value

    def cleaned(*args: Any, **kwargs: Any) -> None:
        real_clean(*args, **kwargs)
        events.append("cleanup")

    monkeypatch.setattr(screening_store, "verify_existing", checked)
    monkeypatch.setattr(screening_store, "_link_exact", linked)
    monkeypatch.setattr(screening_store, "_clean_exact_stage", cleaned)
    _live_campaign(tmp_path, loader)
    assert [event for event in events if event != "cleanup"] == (
        "reload:1 verify:EMPTY link:1 link:2 reload:2 link:3 verify:COMPLETE".split()
    )
    assert events.index("link:2") < events.index("cleanup", events.index("link:2")) < events.index("reload:2")
    assert events.index("verify:COMPLETE") < len(events) - 1 and events[-1] == "cleanup"
    events.clear()
    reloads = 0
    _live_campaign(tmp_path, loader, lambda: UUID("01900000-0000-7000-8000-000000000002"))
    assert [event for event in events if event != "cleanup"] == ("reload:1 verify:COMPLETE reload:2".split())


RECOVERY_CASES = {
    "before_object": ("EMPTY", 3, "REFERENCE_CONFORMANT"),
    "after_object": ("OBJECT_ONLY", 2, "REFERENCE_CONFORMANT"),
    "after_snapshot": ("OBJECT_AND_SNAPSHOT", 1, "REFERENCE_CONFORMANT"),
    "after_receipt": ("COMPLETE", 0, "VERIFIED_EXISTING"),
}


@pytest.mark.parametrize("failure", RECOVERY_CASES)
def test_interrupted_prefix_recovery_records_only_current_turn_links(
    failure: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recovery, writes, disposition = RECOVERY_CASES[failure]
    tmp_path.joinpath(".incoming").mkdir()
    unrelated = tmp_path / ".incoming/unrelated"
    unrelated.write_text("preserved")
    real_write = os.write

    def partial(fd: int, data: bytes | memoryview) -> int:
        return real_write(fd, bytes(data[: max(1, len(data) // 3)]))

    monkeypatch.setattr(benchmark_store.os, "write", partial)
    real_link = screening_store._link_exact  # pyright: ignore[reportPrivateUsage]
    calls = 0

    def interrupted(source: Path, destination: Path, expected: bytes) -> bool:
        nonlocal calls
        calls += 1
        if failure == "before_object" and calls == 1:
            raise OSError("synthetic interruption")
        value = real_link(source, destination, expected)
        if calls == {"after_object": 1, "after_snapshot": 2, "after_receipt": 3}.get(failure):
            raise OSError("synthetic interruption")
        return value

    monkeypatch.setattr(screening_store, "_link_exact", interrupted)
    ids = iter((UUID1(), UUID("01900000-0000-7000-8000-000000000002")))
    with pytest.raises(OSError, match="synthetic interruption"):
        _live_campaign(tmp_path, lambda: FINGERPRINTS, lambda: next(ids))
    result = _result()
    inspected = _inspect(tmp_path, result)
    assert inspected.recovery_state == recovery
    result_sha = hashlib.sha256(canonical_pair_result_bytes(result)).hexdigest()
    paths = tuple(tmp_path / value for value in publication_paths(result_sha)[:3])
    retained_bytes = {path: path.read_bytes() for path in paths if path.exists()}
    monkeypatch.setattr(screening_store, "_link_exact", real_link)
    receipt = _live_campaign(tmp_path, lambda: FINGERPRINTS, lambda: next(ids))[3]
    assert receipt.disposition == disposition
    assert receipt.canonical_recovery_state == recovery
    assert receipt.operation_ledger.canonical_archive_writes == writes
    assert all(path.read_bytes() == data for path, data in retained_bytes.items())
    assert all(stat.S_IMODE(path.stat().st_mode) == 0o444 for path in paths)
    assert unrelated.read_text() == "preserved"


def test_receipt_cross_phase_hash_equality_remains_cryptographic(tmp_path: Path) -> None:
    payload = _receipt(tmp_path, _result(), "DRY_RUN_VALIDATED").model_dump(mode="json")
    payload["authority_fingerprints_post_store"][0][1] = "0" * 64
    with pytest.raises(ValidationError):
        VS01RuntimeScreeningReceipt.model_validate_json(rfc8785.dumps(_rehash(payload, "receipt_canonical_sha256")))


RECEIPT_MUTATIONS: dict[str, tuple[tuple[str | int, ...], Any]] = {
    "top_acquisition": (("acquisition_run_identity",), "0" * 64),
    "top_pair": (("pair_result_identity",), "0" * 64),
    "result_sha": (("pair_result_file_sha256",), "0" * 64),
    "disposition": (("disposition",), "DRY_RUN_VALIDATED"),
    "published": (("published",), False),
    "verified": (("verified_existing",), True),
    "recovery": (("canonical_recovery_state",), "COMPLETE"),
    "recovery_writes": (("operation_ledger", "canonical_archive_writes"), 2),
    "archive_shape": (("archive_paths", 0), "relative"),
    "fingerprint_name": (("authority_fingerprints_pre_store", 0, 0), "changed"),
    "retained_uuid": (("retained_publication_receipt_id",), "not-a-uuid"),
    "retained_sha": (("retained_publication_receipt_file_sha256",), "short"),
    "receipt_uuid": (("receipt_id",), "01900000-0000-6000-8000-000000000001"),
    "implementation_commit": (("implementation_commit",), "a" * 39),
}
RECEIPT_SCHEMA_ADVERSARIES = (
    *RECEIPT_MUTATIONS,
    *"nested_acquisition nested_pair archive_order fingerprint_order phase_shape retained_presence".split(),
    *"retained_disposition retained_published retained_verified".split(),
    *(f"ledger:{field}" for field in RuntimeControllerLedger.model_fields),
)


def _receipt_adversary(part: str, root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    result, live, retained = _published_authority(root)
    verified = _receipt(
        root,
        result,
        "VERIFIED_EXISTING",
        retained,
        new_uuid=lambda: UUID("01900000-0000-7000-8000-000000000002"),
    )
    retained_part = part.startswith("retained_") and part != "retained_presence"
    base = verified if retained_part else live
    if part in {"recovery", "recovery_writes"}:
        state = "OBJECT_ONLY" if part == "recovery" else "OBJECT_AND_SNAPSHOT"
        base = _receipt(root, result, "REFERENCE_CONFORMANT", recovery=state)
    payload = base.model_dump(mode="json")
    original = copy.deepcopy(payload)
    if part in RECEIPT_MUTATIONS:
        _set_path(payload, *RECEIPT_MUTATIONS[part])
    elif part.startswith("ledger:"):
        field = part.split(":", 1)[1]
        payload["operation_ledger"][field] += 1
    elif part in {"nested_acquisition", "nested_pair"}:
        field, value = ("acquisition_run_identity", "0" * 64) if part.endswith("acquisition") else ("fixed_points", 7)
        payload["pair_result"][field] = value
        _rehash(payload["pair_result"], "pair_result_identity")
    elif part in {"archive_order", "fingerprint_order"}:
        values = payload["archive_paths"] if part == "archive_order" else payload["authority_fingerprints_pre_store"]
        values[0], values[1] = values[1], values[0]
    elif part == "phase_shape":
        payload["authority_fingerprints_post_store"].pop()
    elif part == "retained_presence":
        payload["retained_publication_receipt"] = copy.deepcopy(payload)
    else:
        retained = payload["retained_publication_receipt"]
        key, value = {
            "retained_disposition": ("disposition", "DRY_RUN_VALIDATED"),
            "retained_published": ("published", False),
            "retained_verified": ("verified_existing", True),
        }[part]
        retained[key] = value
        _rehash(retained, "receipt_canonical_sha256")
    return original, _rehash(payload, "receipt_canonical_sha256")


@pytest.mark.parametrize("part", RECEIPT_SCHEMA_ADVERSARIES)
def test_screening_receipt_draft202012_matches_material_state_machine(part: str, tmp_path: Path) -> None:
    jsonschema = pytest.importorskip("jsonschema", reason="Draft 2020-12 validator is external")
    tmp_path.joinpath(".incoming").mkdir()
    original, payload = _receipt_adversary(part, tmp_path)
    with pytest.raises((ValidationError, ValueError)):
        VS01RuntimeScreeningReceipt.model_validate_json(rfc8785.dumps(payload))
    schema = json.loads((ROOT / "contracts/json-schema/runtime-screening/screening-receipt.schema.json").read_text())
    validator = jsonschema.Draft202012Validator(schema)
    assert validator.is_valid(original) and not validator.is_valid(payload)


@pytest.mark.parametrize("part", ("commit", "fingerprints", "noncanonical", "mutable"))
def test_retained_receipt_full_store_binding(part: str, tmp_path: Path) -> None:
    tmp_path.joinpath(".incoming").mkdir()
    result, receipt, _retained = _published_authority(tmp_path)
    path = tmp_path / receipt.archive_paths[2]
    if part == "mutable":
        path.chmod(0o644)
    else:
        payload = receipt.model_dump(mode="json")
        if part == "commit":
            payload["implementation_commit"] = "b" * 40
        elif part == "fingerprints":
            payload["authority_fingerprints_initial"][0][1] = "0" * 64
        payload = _rehash(payload, "receipt_canonical_sha256")
        path.chmod(0o644)
        path.write_bytes(rfc8785.dumps(payload) + (b"\n" if part == "noncanonical" else b""))
        path.chmod(0o444)
    with pytest.raises(ValueError):
        _inspect(tmp_path, result)


def test_cli_redacts_failures(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    def failure(**_kwargs: Any):
        raise ValueError("secret path")

    monkeypatch.setattr(cli, "run_runtime_pair", failure)
    assert cli.main(["benchmark", "vs01-b08-runtime-pair", "--subject", "deterministic-runtime"]) == 2
    output = capsys.readouterr().out
    assert "secret path" not in output and json.loads(output)["error"]["code"] == "OPERATION_FAILED"
