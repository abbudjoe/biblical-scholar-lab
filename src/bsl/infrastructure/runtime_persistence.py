from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

import psycopg
import rfc8785
from psycopg import Connection
from psycopg.types.json import Jsonb
from uuid6 import uuid7

from bsl.contracts.runtime import (
    PACKET_IDENTITY,
    PACKET_RECEIPT_IDENTITY,
    PACKET_RECEIPT_SHA256,
    PACKET_SHA256,
    SPEC_SHA256,
    John15RuntimeAuditReceipt,
    John15StudyAnswerArtifact,
    John15StudyExecutionRecord,
    John15StudyRequest,
    canonical_sha256,
)

SCHEMA_REVISION = "0001_vs01_t05_runtime"
MIGRATION_PATH = Path(__file__).parents[3] / "migrations/0001_vs01_t05_runtime.sql"
STATES = (
    "RECEIVED",
    "NORMALIZED",
    "CLASSIFIED",
    "IDENTITIES_RESOLVED",
    "PLAN_FROZEN",
    "EVIDENCE_ASSESSED",
    "CANDIDATE_RECEIVED",
    "VERIFYING",
    "RENDERED",
    "AUDITED",
    "COMPLETE",
)
TABLES = {"study_run", "runtime_artifact", "runtime_event"}
TRIGGERS = {"study_run_reject_mutation", "runtime_artifact_reject_mutation", "runtime_event_reject_mutation"}


@dataclass(frozen=True)
class PersistenceOutcome:
    run_id: UUID
    session_id: UUID
    verified_existing: bool
    audit_receipt: John15RuntimeAuditReceipt


def run_key_sha256(request_identity: str) -> str:
    return canonical_sha256(
        {
            "request_identity": request_identity,
            "packet_identity": PACKET_IDENTITY,
            "packet_canonical_sha256": PACKET_SHA256,
            "runtime_spec_sha256": SPEC_SHA256,
            "executor_kind": "DETERMINISTIC_REFERENCE",
        }
    )


def check_runtime_schema(connection: Connection[Any]) -> None:
    version = connection.execute("SHOW server_version_num").fetchone()
    if version is None or version[0] != "180006":
        raise ValueError("PostgreSQL server_version_num must equal 180006")
    tables = {
        row[0]
        for row in connection.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'bsl_runtime'"
        )
    }
    functions = {
        row[0]
        for row in connection.execute(
            "SELECT p.proname FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='bsl_runtime'"
        )
    }
    triggers = {
        row[0]
        for row in connection.execute(
            "SELECT trigger_name FROM information_schema.triggers WHERE trigger_schema='bsl_runtime'"
        )
    }
    expected = (tables == TABLES, functions == {"reject_mutation"}, triggers == TRIGGERS)
    if not all(expected):
        raise ValueError("database schema differs from the exact VS01-T05 boundary")


def _artifact_rows(
    run_id: UUID,
    request: John15StudyRequest,
    execution: John15StudyExecutionRecord,
    brief: John15StudyAnswerArtifact,
    study: John15StudyAnswerArtifact,
    audit: John15RuntimeAuditReceipt,
) -> list[tuple[str, UUID, str, str, Jsonb]]:
    records = (
        ("REQUEST", "John15StudyRequest", request),
        ("EXECUTION_RECORD", execution.contract, execution),
        ("ANSWER_BRIEF", brief.contract, brief),
        ("ANSWER_STUDY", study.contract, study),
        ("AUDIT_RECEIPT", audit.contract, audit),
    )
    return [
        (
            canonical_sha256(model.model_dump(mode="json")),
            run_id,
            kind,
            contract,
            Jsonb(model.model_dump(mode="json")),
        )
        for kind, contract, model in records
    ]


def _event_rows(
    run_id: UUID, artifacts: list[tuple[str, UUID, str, str, Jsonb]], created_at: datetime
) -> list[tuple[Any, ...]]:
    hashes = {item[2]: item[0] for item in artifacts}
    artifact_types = (
        "REQUEST",
        "REQUEST",
        "EXECUTION_RECORD",
        "EXECUTION_RECORD",
        "EXECUTION_RECORD",
        "EXECUTION_RECORD",
        "EXECUTION_RECORD",
        "EXECUTION_RECORD",
        "ANSWER_STUDY",
        "AUDIT_RECEIPT",
        "AUDIT_RECEIPT",
    )
    previous: str | None = None
    rows: list[tuple[Any, ...]] = []
    for sequence, (state, artifact_type) in enumerate(zip(STATES, artifact_types, strict=True), 1):
        event_id, artifact_sha = uuid7(), hashes[artifact_type]
        envelope = {
            "event_id": str(event_id),
            "run_id": str(run_id),
            "stream_sequence": sequence,
            "state": state,
            "artifact_sha256": artifact_sha,
            "previous_event_sha256": previous,
            "created_at": created_at.isoformat().replace("+00:00", "Z"),
        }
        event_sha = canonical_sha256(envelope)
        rows.append(
            (
                event_id,
                run_id,
                sequence,
                state,
                artifact_sha,
                Jsonb(envelope | {"event_sha256": event_sha}),
                previous,
                event_sha,
                created_at,
            )
        )
        previous = event_sha
    return rows


def _insert_run(
    connection: Connection[Any],
    run_id: UUID,
    session_id: UUID,
    request: John15StudyRequest,
    created_at: datetime,
    supersedes_run_id: UUID | None,
) -> None:
    connection.execute(
        """INSERT INTO bsl_runtime.study_run
           (run_id, session_id, request_revision, supersedes_run_id, request_identity, run_key_sha256,
            packet_identity, packet_sha256, packet_receipt_identity, packet_receipt_file_sha256,
            runtime_spec_sha256, executor_kind, created_at)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (
            run_id,
            session_id,
            request.request_revision,
            supersedes_run_id,
            request.request_identity,
            run_key_sha256(request.request_identity),
            PACKET_IDENTITY,
            PACKET_SHA256,
            PACKET_RECEIPT_IDENTITY,
            PACKET_RECEIPT_SHA256,
            SPEC_SHA256,
            "DETERMINISTIC_REFERENCE",
            created_at,
        ),
    )


def _insert_bundle(
    connection: Connection[Any],
    run_id: UUID,
    artifacts: list[tuple[str, UUID, str, str, Jsonb]],
    events: list[tuple[Any, ...]],
    fail_after_artifacts: bool,
) -> None:
    with connection.cursor() as cursor:
        cursor.executemany(
            "INSERT INTO bsl_runtime.runtime_artifact VALUES (%s,%s,%s,%s,%s,%s)",
            [(*row, events[0][-1]) for row in artifacts],
        )
    if fail_after_artifacts:
        raise RuntimeError("injected persistence failure")
    with connection.cursor() as cursor:
        cursor.executemany("INSERT INTO bsl_runtime.runtime_event VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", events)


def _validate_artifacts(
    rows: list[tuple[Any, ...]],
    request: John15StudyRequest,
    execution: John15StudyExecutionRecord,
    brief: John15StudyAnswerArtifact,
    study: John15StudyAnswerArtifact,
) -> John15RuntimeAuditReceipt:
    expected = {
        "REQUEST": request.model_dump(mode="json"),
        "EXECUTION_RECORD": execution.model_dump(mode="json"),
        "ANSWER_BRIEF": brief.model_dump(mode="json"),
        "ANSWER_STUDY": study.model_dump(mode="json"),
    }
    if len(rows) != 5 or {row[0] for row in rows} != {*expected, "AUDIT_RECEIPT"}:
        raise ValueError("existing runtime artifact set differs")
    audit: John15RuntimeAuditReceipt | None = None
    for artifact_type, digest, value in rows:
        if digest != canonical_sha256(value):
            raise ValueError("existing runtime artifact hash differs")
        if artifact_type == "AUDIT_RECEIPT":
            audit = John15RuntimeAuditReceipt.model_validate_json(rfc8785.dumps(value))
        elif value != expected[artifact_type]:
            raise ValueError("changed artifact exists under the same run key")
    if audit is None or audit.disposition != "PERSISTED":
        raise ValueError("existing persisted audit receipt differs")
    return audit


def _validate_events(rows: list[tuple[Any, ...]], run_id: UUID) -> None:
    if len(rows) != 11:
        raise ValueError("existing runtime event count differs")
    previous: str | None = None
    for expected_sequence, (sequence, state, event_sha, value) in enumerate(rows, 1):
        if (sequence, state) != (expected_sequence, STATES[expected_sequence - 1]):
            raise ValueError("runtime event sequence differs")
        envelope = dict(value)
        stored_sha = envelope.pop("event_sha256", None)
        if envelope.get("run_id") != str(run_id) or envelope.get("previous_event_sha256") != previous:
            raise ValueError("runtime event previous-hash binding differs")
        if stored_sha != event_sha or event_sha != canonical_sha256(envelope):
            raise ValueError("runtime event hash differs")
        previous = event_sha


def _existing(
    connection: Connection[Any],
    row: tuple[Any, ...],
    request: John15StudyRequest,
    execution: John15StudyExecutionRecord,
    brief: John15StudyAnswerArtifact,
    study: John15StudyAnswerArtifact,
) -> PersistenceOutcome:
    run_id, session_id, revision, request_identity = row
    if (revision, request_identity) != (request.request_revision, request.request_identity):
        raise ValueError("existing run key binds a changed request")
    artifacts = connection.execute(
        "SELECT artifact_type, artifact_sha256, artifact_json FROM bsl_runtime.runtime_artifact WHERE run_id=%s",
        (run_id,),
    ).fetchall()
    audit = _validate_artifacts(artifacts, request, execution, brief, study)
    events = connection.execute(
        "SELECT stream_sequence,state,event_sha256,event_json FROM bsl_runtime.runtime_event "
        "WHERE run_id=%s ORDER BY stream_sequence",
        (run_id,),
    ).fetchall()
    _validate_events(events, run_id)
    return PersistenceOutcome(run_id, session_id, True, audit)


def persist_runtime(
    database_url: str,
    request: John15StudyRequest,
    execution: John15StudyExecutionRecord,
    brief: John15StudyAnswerArtifact,
    study: John15StudyAnswerArtifact,
    implementation_commit: str,
    started_ns: int,
    *,
    _fail_after_artifacts: bool = False,
    _session_id: UUID | None = None,
    _supersedes_run_id: UUID | None = None,
) -> PersistenceOutcome:
    with psycopg.connect(database_url) as connection:
        check_runtime_schema(connection)
        connection.commit()
        row = connection.execute(
            "SELECT run_id,session_id,request_revision,request_identity FROM bsl_runtime.study_run "
            "WHERE run_key_sha256=%s",
            (run_key_sha256(request.request_identity),),
        ).fetchone()
        if row is not None:
            return _existing(connection, row, request, execution, brief, study)
        run_id, session_id, created_at = uuid7(), _session_id or uuid7(), datetime.now(UTC)
        from bsl.application.john15_study_runtime import _audit  # pyright: ignore[reportPrivateUsage]

        audit = _audit(execution, brief, study, "PERSISTED", implementation_commit, started_ns, run_id, session_id)
        artifacts = _artifact_rows(run_id, request, execution, brief, study, audit)
        events = _event_rows(run_id, artifacts, created_at)
        with connection.transaction():
            _insert_run(connection, run_id, session_id, request, created_at, _supersedes_run_id)
            _insert_bundle(connection, run_id, artifacts, events, _fail_after_artifacts)
            verified = _existing(
                connection,
                (run_id, session_id, request.request_revision, request.request_identity),
                request,
                execution,
                brief,
                study,
            )
            if verified.audit_receipt != audit:
                raise ValueError("new persisted audit receipt differs after insertion")
    return PersistenceOutcome(run_id, session_id, False, audit)
