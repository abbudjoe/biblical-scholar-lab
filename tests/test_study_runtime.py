from __future__ import annotations

import copy
import hashlib
import json
import shutil
import socket
import time
from contextlib import nullcontext
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock
from uuid import UUID

import psycopg
import pytest
import rfc8785
from uuid6 import uuid7

import bsl.application.john15_study_runtime as runtime
import bsl.contracts.runtime as contracts
import bsl.infrastructure.runtime_persistence as persistence
import bsl.interfaces.cli as cli
from bsl.contracts.evidence import John15TranslationNuanceEvidenceReceipt
from bsl.contracts.runtime import (
    PACKET_RECEIPT_SHA256,
    John15RuntimeAuditReceipt,
    John15StudyAnswerArtifact,
    John15StudyExecutionRecord,
    John15StudyRequest,
    canonical_sha256,
    load_runtime_spec,
)


@pytest.fixture(autouse=True)
def deny_network(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket.socket, "connect", lambda *_args, **_kwargs: pytest.fail("network attempted"))


def _authority(tmp_path: Path) -> runtime._T04Authority:  # pyright: ignore[reportPrivateUsage]
    from test_evidence_packet import _packet

    packet = _packet(tmp_path)
    receipt = John15TranslationNuanceEvidenceReceipt(
        receipt_identity=UUID(runtime.PACKET_RECEIPT_IDENTITY),
        generated_at=datetime(2026, 8, 22, tzinfo=UTC),
        implementation_commit=runtime.T04_IMPLEMENTATION_COMMIT,
        archive_root=str(runtime.CANONICAL_ARCHIVE_ROOT),
        disposition="PUBLISHED",
        dry_run=False,
        input_bundle_identity=packet.input_authority.bundle_identity,
        input_bundle_canonical_sha256=packet.input_authority.bundle_canonical_sha256,
        input_normalization_receipt_identity=packet.input_authority.normalization_receipt_identity,
        input_normalization_receipt_file_sha256=packet.input_authority.normalization_receipt_file_sha256,
        packet_identity=packet.packet_identity,
        packet_canonical_sha256=runtime.PACKET_SHA256,
        publication_paths=(runtime.OBJECT_PATH, runtime.SNAPSHOT_PATH, runtime.RECEIPT_PATH),
        input_authority_fingerprint_before="a" * 64,
        input_authority_fingerprint_after="a" * 64,
        published=True,
        verified_existing=False,
    )
    return runtime._T04Authority(tmp_path, packet, receipt, PACKET_RECEIPT_SHA256)  # pyright: ignore[reportPrivateUsage]


def _artifacts(tmp_path: Path):
    request, execution = runtime._verified_execution(_authority(tmp_path))  # pyright: ignore[reportPrivateUsage]
    brief = runtime._answer(execution, "BRIEF")  # pyright: ignore[reportPrivateUsage]
    study = runtime._answer(execution, "STUDY")  # pyright: ignore[reportPrivateUsage]
    return request, execution, brief, study


def test_exact_request_correction_plan_states_and_ledgers(tmp_path: Path) -> None:
    request, execution, _brief, _study = _artifacts(tmp_path)
    spec = load_runtime_spec()
    initial = John15StudyRequest.model_validate(spec["canonical_request"]["initial_request"])
    assert (initial.request_revision, request.request_revision) == (1, 2)
    assert request.request_identity == contracts.ACTIVE_REQUEST_IDENTITY
    assert request.supersedes_request_identity == initial.request_identity
    assert request.correction_identity == spec["canonical_request"]["correction"]["correction_identity"]
    plan = execution.research_execution_plan
    assert (plan["tool_call_budget"], plan["model_invocation_budget"], plan["network_request_budget"]) == (1, 0, 0)
    assert plan["repair_attempt_budget"] == 0
    assert execution.runtime_state_sequence == tuple(spec["runtime_state_machine"]["principal_sequence"])
    assert execution.skipped_state_reasons == spec["runtime_state_machine"]["skip_reasons"]
    assert (len(execution.evidence_ledger), len(execution.claim_ledger), len(execution.citation_ledger)) == (12, 16, 10)
    assert len(execution.structured_answer_candidate["claim_ids"]) == 15
    assert len(execution.verification_rules) == 12


def test_exact_answers_identities_citations_uncertainty_and_alternatives(tmp_path: Path) -> None:
    request, execution, brief, study = _artifacts(tmp_path)
    spec = load_runtime_spec()
    assert brief.markdown.encode() == spec["answer_artifacts"]["brief"]["markdown"].encode()
    assert study.markdown.encode() == spec["answer_artifacts"]["study"]["markdown"].encode()
    assert (len(brief.visible_claim_ids), len(study.visible_claim_ids)) == (10, 15)
    assert ({item["citation_id"] for item in brief.citation_records}, len(study.citation_records)) == (
        {f"CIT-T05-{number:03}" for number in range(1, 11)} - {"CIT-T05-005"},
        10,
    )
    assert (
        brief.material_uncertainty_claim_ids
        == study.material_uncertainty_claim_ids
        == (
            "CLM-T04-042",
            "CLM-T04-043",
        )
    )
    assert brief.alternative_ids == study.alternative_ids
    repeated = _artifacts(tmp_path)
    assert [item.model_dump_json() for item in (request, execution, brief, study)] == [
        item.model_dump_json() for item in repeated
    ]


@pytest.mark.parametrize("case", ("evidence", "claim", "citation", "candidate", "alternative"))
def test_packet_projection_verifier_rejects_semantic_mutations(tmp_path: Path, case: str) -> None:
    authority = _authority(tmp_path)
    spec = copy.deepcopy(load_runtime_spec())
    if case == "evidence":
        spec["evidence_ledger"][0]["selector"] = "changed"
        verifier = runtime._verify_ledgers  # pyright: ignore[reportPrivateUsage]
    elif case == "claim":
        spec["claim_ledger"][0]["epistemic_status"] = "UNKNOWN"
        verifier = runtime._verify_ledgers  # pyright: ignore[reportPrivateUsage]
    elif case == "citation":
        spec["citation_records"][0]["quoted_span"] = "changed"
        verifier = runtime._verify_citations  # pyright: ignore[reportPrivateUsage]
    elif case == "candidate":
        spec["structured_answer_candidate"]["claim_ids"].append("CLM-T04-001")
        verifier = runtime._verify_candidate  # pyright: ignore[reportPrivateUsage]
    else:
        packet = authority.packet.model_dump(mode="json")
        packet["accepted_alternatives"][0]["epistemic_status"] = "DIRECTLY_ATTESTED"
        with pytest.raises(ValueError):
            type(authority.packet).model_validate_json(rfc8785.dumps(packet))
        return
    with pytest.raises(ValueError):
        verifier(authority.packet, spec)


@pytest.mark.parametrize("target", ("request", "plan", "claim", "brief", "study", "receipt"))
def test_strict_contracts_reject_frozen_and_prohibited_inference_mutations(tmp_path: Path, target: str) -> None:
    request, execution, brief, study = _artifacts(tmp_path)
    if target == "request":
        value, model, field = request.model_dump(mode="json"), John15StudyRequest, "exact_user_text"
    elif target in {"plan", "claim"}:
        value, model = execution.model_dump(mode="json"), John15StudyExecutionRecord
        field = "research_execution_plan" if target == "plan" else "claim_ledger"
    else:
        artifact = brief if target == "brief" else study
        value, model, field = artifact.model_dump(mode="json"), John15StudyAnswerArtifact, "markdown"
        if target == "receipt":
            value["packet_receipt_file_sha256"] = "0" * 64
            field = "packet_receipt_file_sha256"
    if field == "research_execution_plan":
        value[field]["model_invocation_budget"] = 1
    elif field == "claim_ledger":
        value[field][12]["epistemic_status"] = "DIRECTLY_ATTESTED"
    else:
        value[field] = "A theological conclusion and translator intent are certain."
    with pytest.raises(ValueError):
        model.model_validate_json(rfc8785.dumps(value))


def test_two_audits_differ_only_in_operational_fields(tmp_path: Path) -> None:
    _request, execution, brief, study = _artifacts(tmp_path)
    first = runtime._audit(execution, brief, study, "DRY_RUN_VALIDATED", "a" * 40, time.monotonic_ns())  # pyright: ignore[reportPrivateUsage]
    second = runtime._audit(execution, brief, study, "DRY_RUN_VALIDATED", "a" * 40, time.monotonic_ns())  # pyright: ignore[reportPrivateUsage]
    excluded = {"receipt_identity", "generated_at", "latency_ms", "receipt_canonical_sha256"}
    left = first.model_dump(mode="json", exclude=excluded)
    right = second.model_dump(mode="json", exclude=excluded)
    assert left == right
    assert first.receipt_identity != second.receipt_identity
    assert John15RuntimeAuditReceipt.model_validate_json(first.model_dump_json()) == first


@pytest.mark.parametrize("mutation", ("brief_hash", "row_counts", "database_ids"))
def test_audit_contract_rejects_changed_deterministic_and_persistence_bindings(tmp_path: Path, mutation: str) -> None:
    _request, execution, brief, study = _artifacts(tmp_path)
    audit = runtime._audit(  # pyright: ignore[reportPrivateUsage]
        execution, brief, study, "DRY_RUN_VALIDATED", "a" * 40, time.monotonic_ns()
    )
    value = audit.model_dump(mode="json")
    if mutation == "brief_hash":
        value["brief_answer_sha256"] = "0" * 64
    elif mutation == "row_counts":
        value["database_rows_verified"]["study_run"] = 1
    else:
        value["database_schema_revision"] = "0001_vs01_t05_runtime"
    value["receipt_canonical_sha256"] = canonical_sha256(
        {key: item for key, item in value.items() if key != "receipt_canonical_sha256"}
    )
    with pytest.raises(ValueError):
        John15RuntimeAuditReceipt.model_validate_json(rfc8785.dumps(value))


def _retain(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    path.chmod(0o444)


def test_raw_t04_loader_uses_minimum_authority_and_no_forbidden_reads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from test_source_acquisition import archive_root

    root = archive_root.__wrapped__(tmp_path)
    for relative in ("snapshots/source", "manifests/source", "quarantine"):
        shutil.rmtree(root / relative)
    authority = _authority(root)
    packet_bytes = rfc8785.dumps(authority.packet.model_dump(mode="json"))
    receipt_bytes = rfc8785.dumps(authority.receipt.model_dump(mode="json"))
    monkeypatch.setattr(runtime, "PACKET_RECEIPT_SHA256", hashlib.sha256(receipt_bytes).hexdigest())
    for relative, data in zip(
        (runtime.OBJECT_PATH, runtime.SNAPSHOT_PATH, runtime.RECEIPT_PATH),
        (packet_bytes, packet_bytes, receipt_bytes),
        strict=True,
    ):
        _retain(root / relative, data)
    seen: list[Path] = []
    original = runtime._regular_0444  # pyright: ignore[reportPrivateUsage]

    def audited(path: Path):
        seen.append(path.relative_to(root))
        return original(path)

    monkeypatch.setattr(runtime, "_regular_0444", audited)
    loaded = runtime.load_t04_authority(root, _expected_archive_root=root)
    assert loaded.packet.packet_identity == runtime.PACKET_IDENTITY
    assert seen == [Path(runtime.OBJECT_PATH), Path(runtime.SNAPSHOT_PATH), Path(runtime.RECEIPT_PATH)]
    assert all(not (root / path).exists() for path in ("snapshots/source", "manifests/source", "quarantine"))


def test_dry_run_rejects_adapter_and_performs_no_archive_or_database_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    authority = _authority(tmp_path)
    loads = 0

    def load(*_args, **_kwargs):
        nonlocal loads
        loads += 1
        return authority

    monkeypatch.setattr(runtime, "load_t04_authority", load)
    with pytest.raises(ValueError, match="rejects model adapters"):
        runtime.execute_john15_study(tmp_path, dry_run=True, model_adapter=object())  # type: ignore[arg-type]
    before = tuple(tmp_path.rglob("*"))
    result = runtime.execute_john15_study(tmp_path, dry_run=True, _implementation_commit="a" * 40)
    assert result.audit_receipt.disposition == "DRY_RUN_VALIDATED"
    assert (result.persisted, result.verified_existing) == (False, False)
    assert result.audit_receipt.database_connections == result.audit_receipt.archive_writes == 0
    assert result.audit_receipt.network_requests == result.audit_receipt.model_invocations == 0
    assert tuple(tmp_path.rglob("*")) == before
    assert loads == 1


def test_runtime_spec_hash_and_run_key_are_exact(tmp_path: Path) -> None:
    changed = tmp_path / "runtime-spec.json"
    changed.write_bytes(contracts.RUNTIME_SPEC_PATH.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="hash"):
        load_runtime_spec(changed)
    expected = "780efc349dc22648791cd4c08475f78f4fdb884b81623e6397a65294f1a2449a"
    from bsl.infrastructure.runtime_persistence import run_key_sha256

    assert run_key_sha256(contracts.ACTIVE_REQUEST_IDENTITY) == expected
    assert canonical_sha256(_artifacts(tmp_path)[0].model_dump(mode="json", exclude={"request_identity"})) == (
        contracts.ACTIVE_REQUEST_IDENTITY
    )


def test_persistence_artifact_and_event_envelopes_verify_without_database(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request, execution, brief, study = _artifacts(tmp_path)
    run_id, session_id, created = uuid7(), uuid7(), datetime.now(UTC)
    audit = runtime._audit(  # pyright: ignore[reportPrivateUsage]
        execution, brief, study, "PERSISTED", "a" * 40, time.monotonic_ns(), run_id, session_id
    )
    artifacts = persistence._artifact_rows(  # pyright: ignore[reportPrivateUsage]
        run_id, request, execution, brief, study, audit
    )
    events = persistence._event_rows(run_id, artifacts, created)  # pyright: ignore[reportPrivateUsage]
    artifact_rows = [(*row[:4], row[4].obj, created) for row in artifacts]
    event_rows = [(*row[:5], row[5].obj, *row[6:]) for row in events]
    _verified, hashes = persistence._validate_artifacts(  # pyright: ignore[reportPrivateUsage]
        artifact_rows, run_id, session_id, created, request, execution, brief, study, "a" * 40
    )
    persistence._validate_events(event_rows, run_id, hashes)  # pyright: ignore[reportPrivateUsage]
    with pytest.raises(ValueError, match="count"):
        persistence._validate_events(event_rows[1:], run_id, hashes)  # pyright: ignore[reportPrivateUsage]
    connection = Mock()
    connection.transaction.return_value = nullcontext()
    monkeypatch.setattr(persistence, "check_runtime_schema", Mock())
    monkeypatch.setattr(runtime, "_audit", Mock(return_value=audit))
    monkeypatch.setattr(persistence, "_root_row", Mock(side_effect=(None, (run_id,))))
    monkeypatch.setattr(persistence, "_insert_bundle", Mock())
    monkeypatch.setattr(
        persistence, "_existing", Mock(return_value=persistence.PersistenceOutcome(run_id, session_id, True, audit))
    )
    outcome = persistence._persist_connected(  # pyright: ignore[reportPrivateUsage]
        connection, request, execution, brief, study, "a" * 40, time.monotonic_ns(), False
    )
    parameters = connection.execute.call_args.args[1]
    root = (*parameters[:3], None, *parameters[3:7], UUID(parameters[7]), *parameters[8:])
    persistence._validate_run(root, request)  # pyright: ignore[reportPrivateUsage]
    assert not outcome.verified_existing


def test_schema_checker_uses_normalized_catalog_fingerprint(monkeypatch: pytest.MonkeyPatch) -> None:
    assert persistence._normalize_check("((value::text=ANY(ARRAY['x'::text])))") == "valueIN('x')"
    catalog_connection = Mock()
    catalog_connection.execute.return_value = [("record",)]
    assert len(persistence._catalog(catalog_connection)) == 7  # pyright: ignore[reportPrivateUsage]
    connection = Mock()
    connection.execute.return_value.fetchone.return_value = ("180006",)
    empty = {name: set() for name in ("relations", "columns", "keys", "checks", "indexes", "triggers", "functions")}
    monkeypatch.setattr(persistence, "_catalog", lambda _connection: empty)
    monkeypatch.setattr(persistence, "EXPECTED_CATALOG_SHA256", canonical_sha256({name: [] for name in empty}))
    persistence.check_runtime_schema(connection)


def test_live_application_reloads_authority_before_any_database_access(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = _authority(tmp_path)
    changed = replace(first, receipt=first.receipt.model_copy(update={"implementation_commit": "b" * 40}))
    persist, connect = Mock(), Mock()
    authorities = iter((first, changed))
    monkeypatch.setattr(runtime, "load_t04_authority", lambda *_args, **_kwargs: next(authorities))
    monkeypatch.setattr(persistence, "persist_runtime", persist)
    monkeypatch.setattr(persistence.psycopg, "connect", connect)
    with pytest.raises(ValueError, match="T04 authority changed before persistence"):
        runtime.execute_john15_study(tmp_path, dry_run=False, database_url="unused", _implementation_commit="a" * 40)
    persist.assert_not_called()
    connect.assert_not_called()


@pytest.mark.parametrize("stage", ("connect", "transaction"))
def test_database_provider_errors_are_stably_redacted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stage: str
) -> None:
    request, execution, brief, study = _artifacts(tmp_path)
    secret = "postgresql://owner:fake-secret@private-host/db SELECT secret"
    failure = Mock(side_effect=psycopg.OperationalError(secret))
    if stage == "connect":
        monkeypatch.setattr(persistence.psycopg, "connect", failure)
    else:
        monkeypatch.setattr(persistence.psycopg, "connect", lambda _url: nullcontext(object()))
        monkeypatch.setattr(persistence, "_persist_connected", failure)
    with pytest.raises(ValueError, match="^database operation failed$"):
        persistence.persist_runtime("hidden-dsn", request, execution, brief, study, "a" * 40, 0)


def test_cli_redacts_database_provider_failure(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    secret = "postgresql://owner:fake-secret@private-host/db SELECT secret provider detail"
    monkeypatch.setattr(cli, "execute_john15_study", Mock(side_effect=ValueError("database operation failed")))
    result = cli.main(("study", "john-1-5-translation-nuance", "--archive-root", "/unused", "--render", "both"))
    output = capsys.readouterr().out
    assert result == 2
    assert json.loads(output) == {"error": {"code": "OPERATION_FAILED", "message": "database operation failed"}}
    assert all(value not in output for value in (secret, "fake-secret", "SELECT", "provider detail"))
