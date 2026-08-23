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
    brief = John15StudyAnswerArtifact.model_validate_json(
        rfc8785.dumps(contracts._answer_payload("BRIEF"))  # pyright: ignore[reportPrivateUsage]
    )
    study = John15StudyAnswerArtifact.model_validate_json(
        rfc8785.dumps(contracts._answer_payload("STUDY"))  # pyright: ignore[reportPrivateUsage]
    )
    return request, execution, brief, study


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
        persistence.check_runtime_schema(connection)
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='bsl_runtime'"
            )
        }
        assert tables == persistence.TABLES
        triggers = connection.execute(
            "SELECT trigger_name,event_manipulation FROM information_schema.triggers WHERE trigger_schema='bsl_runtime'"
        ).fetchall()
        assert {row[0] for row in triggers} == persistence.TRIGGERS
        assert {row[1] for row in triggers} == {"UPDATE", "DELETE"}
        indexes = {
            row[0] for row in connection.execute("SELECT indexname FROM pg_indexes WHERE schemaname='bsl_runtime'")
        }
        assert indexes == {
            "study_run_pkey",
            "study_run_run_key_sha256_key",
            "study_run_session_id_request_revision_key",
            "runtime_artifact_pkey",
            "runtime_artifact_run_id_artifact_type_key",
            "runtime_event_pkey",
            "runtime_event_run_id_stream_sequence_key",
            "runtime_event_run_id_event_sha256_key",
        }
        assert not connection.execute(
            "SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
            "WHERE n.nspname='bsl_runtime' AND c.relkind IN ('v','m','S')"
        ).fetchall()
        assert not connection.execute(
            "SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
            "WHERE n.nspname='bsl_runtime' AND c.relrowsecurity"
        ).fetchall()


@pytest.mark.parametrize("table", ("study_run", "runtime_artifact", "runtime_event"))
@pytest.mark.parametrize("operation", ("UPDATE", "DELETE"))
def test_every_table_rejects_update_and_delete(table: str, operation: str) -> None:
    _persist()
    assert DATABASE_URL is not None
    statement = (
        f"{operation} FROM bsl_runtime.{table}"
        if operation == "DELETE"
        else (f"UPDATE bsl_runtime.{table} SET created_at=created_at")
    )
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
        rows = connection.execute(
            "SELECT stream_sequence,state,event_sha256,event_json FROM bsl_runtime.runtime_event "
            "ORDER BY stream_sequence"
        ).fetchall()
    persistence._validate_events(rows, outcome.run_id)  # pyright: ignore[reportPrivateUsage]
    assert [row[1] for row in rows] == list(persistence.STATES)


def test_injected_failure_rolls_back_every_row() -> None:
    with pytest.raises(RuntimeError, match="injected"):
        _persist(_fail_after_artifacts=True)
    assert _counts() == (0, 0, 0)


def test_identical_replay_verifies_all_rows_without_writing() -> None:
    first, second = _persist(), _persist()
    assert first.run_id == second.run_id and first.session_id == second.session_id
    assert second.verified_existing and second.audit_receipt.disposition == "PERSISTED"
    assert _counts() == (1, 5, 11)


def test_changed_existing_artifact_under_same_run_key_fails_closed() -> None:
    assert DATABASE_URL is not None
    request, execution, brief, study = _models()
    run_id, session_id, created_at = uuid7(), uuid7(), datetime.now(UTC)
    from bsl.application.john15_study_runtime import _audit

    audit = _audit(execution, brief, study, "PERSISTED", "a" * 40, time.monotonic_ns(), run_id, session_id)
    artifacts = persistence._artifact_rows(  # pyright: ignore[reportPrivateUsage]
        run_id, request, execution, brief, study, audit
    )
    changed = study.model_dump(mode="json") | {"markdown": "changed"}
    artifacts[3] = (contracts.canonical_sha256(changed), run_id, "ANSWER_STUDY", study.contract, Jsonb(changed))
    with psycopg.connect(DATABASE_URL) as connection, connection.transaction():
        persistence._insert_run(  # pyright: ignore[reportPrivateUsage]
            connection, run_id, session_id, request, created_at, None
        )
        with connection.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO bsl_runtime.runtime_artifact VALUES (%s,%s,%s,%s,%s,%s)",
                [(*row, created_at) for row in artifacts],
            )
    with pytest.raises(ValueError, match="changed artifact"):
        _persist()


def test_correction_preserves_revision_one_and_uses_supersession() -> None:
    assert DATABASE_URL is not None
    initial = John15StudyRequest.model_validate(contracts._request_payload(1))  # pyright: ignore[reportPrivateUsage]
    run_id, session_id, created_at = uuid7(), uuid7(), datetime.now(UTC)
    request_json = initial.model_dump(mode="json")
    artifact_sha = contracts.canonical_sha256(request_json)
    with psycopg.connect(DATABASE_URL) as connection, connection.transaction():
        persistence._insert_run(  # pyright: ignore[reportPrivateUsage]
            connection, run_id, session_id, initial, created_at, None
        )
        connection.execute(
            "INSERT INTO bsl_runtime.runtime_artifact VALUES (%s,%s,'REQUEST','John15StudyRequest',%s,%s)",
            (artifact_sha, run_id, Jsonb(request_json), created_at),
        )
    with psycopg.connect(DATABASE_URL) as connection:
        before = connection.execute("SELECT * FROM bsl_runtime.study_run WHERE run_id=%s", (run_id,)).fetchone()
        before_artifact = connection.execute(
            "SELECT * FROM bsl_runtime.runtime_artifact WHERE run_id=%s", (run_id,)
        ).fetchone()
    corrected = _persist(_session_id=session_id, _supersedes_run_id=run_id)
    with psycopg.connect(DATABASE_URL) as connection:
        after = connection.execute("SELECT * FROM bsl_runtime.study_run WHERE run_id=%s", (run_id,)).fetchone()
        after_artifact = connection.execute(
            "SELECT * FROM bsl_runtime.runtime_artifact WHERE run_id=%s", (run_id,)
        ).fetchone()
        revision_two = connection.execute(
            "SELECT session_id,request_revision,supersedes_run_id FROM bsl_runtime.study_run WHERE run_id=%s",
            (corrected.run_id,),
        ).fetchone()
    assert before == after and before_artifact == after_artifact
    assert revision_two == (session_id, 2, run_id)
    assert _counts() == (2, 6, 11)
