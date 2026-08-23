from __future__ import annotations

import os
import time
from datetime import UTC, datetime

import psycopg
import pytest
import rfc8785
from psycopg.conninfo import conninfo_to_dict
from psycopg.types.json import Jsonb
from uuid6 import uuid7

import bsl.contracts.runtime as contracts
import bsl.infrastructure.runtime_persistence as persistence
from bsl.contracts.runtime import John15StudyAnswerArtifact, John15StudyExecutionRecord, John15StudyRequest

DATABASE_URL = os.environ.get("BSL_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(DATABASE_URL is None, reason="BSL_TEST_DATABASE_URL is absent")


def _models():
    request = John15StudyRequest.model_validate(contracts._request_payload(2))  # pyright: ignore[reportPrivateUsage]
    execution = John15StudyExecutionRecord.model_validate_json(
        rfc8785.dumps(contracts._execution_payload())  # pyright: ignore[reportPrivateUsage]
    )
    answers = [
        John15StudyAnswerArtifact.model_validate_json(rfc8785.dumps(contracts._answer_payload(depth)))
        for depth in ("BRIEF", "STUDY")  # pyright: ignore[reportPrivateUsage]
    ]
    return request, execution, *answers


@pytest.fixture(autouse=True)
def migrated_database() -> None:
    assert DATABASE_URL is not None
    coordinate = conninfo_to_dict(DATABASE_URL)
    assert (coordinate.get("user"), coordinate.get("dbname")) == ("bsl_test", "bsl_test")
    with psycopg.connect(DATABASE_URL, autocommit=True) as connection:
        connection.execute("DROP SCHEMA IF EXISTS bsl_runtime CASCADE")
        connection.execute(persistence.MIGRATION_PATH.read_text())


def _counts() -> tuple[int, int, int]:
    assert DATABASE_URL is not None
    with psycopg.connect(DATABASE_URL) as connection:
        return tuple(
            connection.execute(f"SELECT count(*) FROM bsl_runtime.{table}").fetchone()[0]  # noqa: S608
            for table in ("study_run", "runtime_artifact", "runtime_event")
        )


def _persist(**kwargs):
    assert DATABASE_URL is not None
    return persistence.persist_runtime(DATABASE_URL, *_models(), "a" * 40, time.monotonic_ns(), **kwargs)


def test_migration_has_exact_catalog_boundary() -> None:
    assert DATABASE_URL is not None
    with psycopg.connect(DATABASE_URL) as connection:
        assert connection.execute("SHOW server_version_num").fetchone()[0] == "180006"
        catalog = persistence._catalog(connection)  # pyright: ignore[reportPrivateUsage]
        catalog["checks"] = {(*row[:2], persistence._normalize_check(row[2]), *row[3:]) for row in catalog["checks"]}  # pyright: ignore[reportPrivateUsage]
        normalized = {name: sorted((list(row) for row in rows), key=repr) for name, rows in catalog.items()}
        print(contracts.canonical_sha256(normalized))
        persistence.check_runtime_schema(connection)


@pytest.mark.parametrize("table", ("study_run", "runtime_artifact", "runtime_event"))
@pytest.mark.parametrize("operation", ("UPDATE", "DELETE"))
def test_every_table_rejects_update_and_delete(table: str, operation: str) -> None:
    _persist()
    assert DATABASE_URL is not None
    target = f"bsl_runtime.{table}"
    statement = f"DELETE FROM {target}" if operation == "DELETE" else f"UPDATE {target} SET created_at=created_at"
    with (
        psycopg.connect(DATABASE_URL, autocommit=True) as connection,
        pytest.raises(psycopg.errors.RaiseException, match="append-only"),
    ):
        connection.execute(statement)


def test_atomic_counts_and_contiguous_previous_hash_chain() -> None:
    outcome = _persist()
    assert not outcome.verified_existing and outcome.audit_receipt.disposition == "PERSISTED"
    assert _counts() == (1, 5, 11)
    assert DATABASE_URL is not None
    with psycopg.connect(DATABASE_URL) as connection:
        artifacts = dict(
            connection.execute("SELECT artifact_type,artifact_sha256 FROM bsl_runtime.runtime_artifact").fetchall()
        )
        rows = connection.execute(
            "SELECT event_id,run_id,stream_sequence,state,artifact_sha256,event_json,previous_event_sha256,"
            "event_sha256,created_at FROM bsl_runtime.runtime_event ORDER BY stream_sequence"
        ).fetchall()
    persistence._validate_events(rows, outcome.run_id, artifacts)  # pyright: ignore[reportPrivateUsage]
    assert [row[3] for row in rows] == list(persistence.STATES)


def test_injected_failure_rolls_back_every_row() -> None:
    with pytest.raises(ValueError, match="^database operation failed$"):
        _persist(_fail_after_artifacts=True)
    assert _counts() == (0, 0, 0)


def test_identical_replay_verifies_all_rows_without_writing() -> None:
    first, second = _persist(), _persist()
    assert first.run_id == second.run_id and first.session_id == second.session_id
    assert second.verified_existing and second.audit_receipt.disposition == "PERSISTED"
    assert _counts() == (1, 5, 11)


@pytest.mark.parametrize(
    "statements",
    (
        (
            "DROP TRIGGER study_run_reject_mutation ON bsl_runtime.study_run",
            "CREATE TRIGGER study_run_reject_mutation BEFORE UPDATE ON bsl_runtime.study_run "
            "FOR EACH ROW EXECUTE FUNCTION bsl_runtime.reject_mutation()",
        ),
        ("ALTER TABLE bsl_runtime.study_run DROP CONSTRAINT study_run_run_key_sha256_key",),
        ("ALTER TABLE bsl_runtime.study_run DROP CONSTRAINT study_run_request_revision_check",),
        ("CREATE VIEW bsl_runtime.extra_relation AS SELECT 1 AS value",),
        (
            "CREATE TRIGGER extra_trigger BEFORE UPDATE ON bsl_runtime.study_run "
            "FOR EACH ROW EXECUTE FUNCTION bsl_runtime.reject_mutation()",
        ),
        ("ALTER TABLE bsl_runtime.study_run DISABLE TRIGGER study_run_reject_mutation",),
        (
            "DROP TRIGGER study_run_reject_mutation ON bsl_runtime.study_run",
            "CREATE TRIGGER study_run_reject_mutation BEFORE UPDATE OR DELETE ON bsl_runtime.study_run "
            "FOR EACH ROW WHEN (false) EXECUTE FUNCTION bsl_runtime.reject_mutation()",
        ),
        ("ALTER TABLE bsl_runtime.runtime_artifact ALTER CONSTRAINT runtime_artifact_run_id_fkey NOT ENFORCED",),
    ),
)
def test_schema_gate_rejects_catalog_adversaries_before_insert(statements: tuple[str, ...]) -> None:
    with psycopg.connect(DATABASE_URL, autocommit=True) as connection:
        for statement in statements:
            connection.execute(statement)
    with pytest.raises(ValueError, match="schema differs"):
        _persist()
    assert _counts() == (0, 0, 0)


def _seed_existing_adversary(mutation: str) -> None:
    request, execution, brief, study = _models()
    run_id, session_id, created_at = uuid7(), uuid7(), datetime.now(UTC)
    from bsl.application.john15_study_runtime import _audit

    audit = _audit(execution, brief, study, "PERSISTED", "a" * 40, time.monotonic_ns(), run_id, session_id)
    audit_json = audit.model_dump(mode="json")
    if mutation in {"audit_run", "audit_session"}:
        audit_json[mutation.removeprefix("audit_")] = str(uuid7())
    elif mutation == "authority":
        audit_json["packet_receipt_file_sha256"] = "0" * 64
    elif mutation == "implementation":
        audit_json["implementation_commit"] = "b" * 40
    artifacts = persistence._artifact_rows(run_id, request, execution, brief, study, audit)  # pyright: ignore[reportPrivateUsage]
    if mutation in {"audit_run", "audit_session", "authority", "implementation"}:
        audit_json["receipt_canonical_sha256"] = contracts.canonical_sha256(
            {key: value for key, value in audit_json.items() if key != "receipt_canonical_sha256"}
        )
        artifacts[-1] = (contracts.canonical_sha256(audit_json), *artifacts[-1][1:4], Jsonb(audit_json))
    if mutation == "contract":
        artifacts[0] = (*artifacts[0][:3], "WrongContract", artifacts[0][4])
    elif mutation == "changed_artifact":
        changed = study.model_dump(mode="json") | {"markdown": "changed"}
        artifacts[3] = (contracts.canonical_sha256(changed), run_id, "ANSWER_STUDY", study.contract, Jsonb(changed))
    events = persistence._event_rows(run_id, artifacts, created_at)  # pyright: ignore[reportPrivateUsage]
    if mutation == "event_artifact":
        events[0] = (*events[0][:4], artifacts[1][0], *events[0][5:])
    with psycopg.connect(DATABASE_URL) as connection, connection.transaction():
        persistence._insert_run(connection, run_id, session_id, request, created_at)  # pyright: ignore[reportPrivateUsage]
        with connection.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO bsl_runtime.runtime_artifact VALUES (%s,%s,%s,%s,%s,%s)",
                [(*row, created_at) for row in artifacts],
            )
        if mutation == "event_run":
            alternate = uuid7()
            connection.execute(
                "INSERT INTO bsl_runtime.study_run SELECT %s,%s,99,NULL,request_identity,%s,packet_identity,"
                "packet_sha256,packet_receipt_identity,packet_receipt_file_sha256,runtime_spec_sha256,"
                "executor_kind,created_at FROM bsl_runtime.study_run WHERE run_id=%s",
                (alternate, uuid7(), "f" * 64, run_id),
            )
            events[0] = (events[0][0], alternate, *events[0][2:])
        with connection.cursor() as cursor:
            cursor.executemany("INSERT INTO bsl_runtime.runtime_event VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", events)


@pytest.mark.parametrize(
    "mutation",
    "changed_artifact contract event_artifact event_run audit_run audit_session authority implementation".split(),  # noqa: E501, SIM905
)
def test_existing_run_rejects_relational_and_json_adversaries(mutation: str) -> None:
    _seed_existing_adversary(mutation)
    with pytest.raises(ValueError):
        _persist()


def test_active_revision_two_preserves_request_lineage_without_fabricating_revision_one_run() -> None:
    request, _execution, _brief, _study = _models()
    spec = contracts.load_runtime_spec()
    initial = John15StudyRequest.model_validate(spec["canonical_request"]["initial_request"])
    outcome = _persist()
    with psycopg.connect(DATABASE_URL) as connection:
        row = connection.execute(
            "SELECT request_revision,supersedes_run_id,request_identity FROM bsl_runtime.study_run WHERE run_id=%s",
            (outcome.run_id,),
        ).fetchone()
        revisions = connection.execute("SELECT request_revision FROM bsl_runtime.study_run").fetchall()
    assert request.supersedes_request_identity == initial.request_identity
    assert request.correction_identity == spec["canonical_request"]["correction"]["correction_identity"]
    assert row == (2, None, request.request_identity)
    assert revisions == [(2,)] and _counts() == (1, 5, 11)
