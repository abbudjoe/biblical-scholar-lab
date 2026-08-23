from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from uuid import UUID

import psycopg
import rfc8785
from psycopg import Connection
from psycopg.types.json import Jsonb
from uuid6 import uuid7

from bsl.contracts.runtime import (
    ACTIVE_REQUEST_IDENTITY,
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
ARTIFACT_TYPES = (
    "REQUEST",
    "REQUEST",
    *(("EXECUTION_RECORD",) * 6),
    "ANSWER_STUDY",
    "AUDIT_RECEIPT",
    "AUDIT_RECEIPT",
)
EXPECTED_CATALOG_SHA256 = "e7f1da1bff0edec3c5564f02a2da882abeb5142cc12054f460f5f4439a55bcf8"


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


def _freeze(row: tuple[Any, ...]) -> tuple[Any, ...]:
    return tuple(tuple(cast(list[Any], value)) if isinstance(value, list) else value for value in row)


def _normalize_check(value: str) -> str:
    normalized = "".join(value.split()).replace("::text", "").replace("::bpchar", "").replace("::uuid", "")
    while normalized.startswith("(") and normalized.endswith(")"):
        normalized = normalized[1:-1]
    return normalized.replace("=ANY(ARRAY[", "IN(").replace("])", ")")


def _catalog(connection: Connection[Any]) -> dict[str, set[tuple[Any, ...]]]:
    queries = {
        "relations": """/* relations */ SELECT c.relname,c.relkind,c.relrowsecurity FROM pg_class c
            JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='bsl_runtime'
            AND c.relkind IN ('r','p','v','m','S','f')""",
        "columns": """/* columns */ SELECT c.relname,string_agg(
            a.attname||':'||format_type(a.atttypid,a.atttypmod)||':'||a.attnotnull::int,',' ORDER BY a.attnum)
            FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_attribute a
            ON a.attrelid=c.oid AND a.attnum>0 AND NOT a.attisdropped
            WHERE n.nspname='bsl_runtime' AND c.relkind IN ('r','p') GROUP BY c.relname""",
        "keys": """/* keys */ SELECT r.relname,con.conname,con.contype,
            ARRAY(SELECT a.attname FROM unnest(con.conkey) WITH ORDINALITY k(attnum,ord)
                  JOIN pg_attribute a ON a.attrelid=con.conrelid AND a.attnum=k.attnum ORDER BY k.ord),
            rr.relname,
            ARRAY(SELECT a.attname FROM unnest(con.confkey) WITH ORDINALITY k(attnum,ord)
                  JOIN pg_attribute a ON a.attrelid=con.confrelid AND a.attnum=k.attnum ORDER BY k.ord),
            CASE WHEN con.contype='f' THEN con.confupdtype::text END, CASE WHEN con.contype='f'
            THEN con.confdeltype::text END, CASE WHEN con.contype='f' THEN con.confmatchtype::text END,
            con.condeferrable,con.condeferred,con.convalidated,con.connoinherit
            FROM pg_constraint con JOIN pg_class r ON r.oid=con.conrelid
            JOIN pg_namespace n ON n.oid=r.relnamespace LEFT JOIN pg_class rr ON rr.oid=con.confrelid
            WHERE n.nspname='bsl_runtime' AND con.contype IN ('p','u','f')""",
        "checks": """/* checks */ SELECT r.relname,con.conname,pg_get_expr(con.conbin,con.conrelid,true),
            con.convalidated,con.connoinherit FROM pg_constraint con
            JOIN pg_class r ON r.oid=con.conrelid JOIN pg_namespace n ON n.oid=r.relnamespace
            WHERE n.nspname='bsl_runtime' AND con.contype='c'""",
        "indexes": """/* indexes */ SELECT r.relname,i.relname,am.amname,x.indisunique,x.indisprimary,
            x.indnkeyatts,x.indnatts,pg_get_indexdef(x.indexrelid,0,true),
            ARRAY(SELECT a.attname FROM unnest(x.indkey) WITH ORDINALITY k(attnum,ord)
                  JOIN pg_attribute a ON a.attrelid=x.indrelid AND a.attnum=k.attnum ORDER BY k.ord),
            pg_get_expr(x.indpred,x.indrelid,true),pg_get_expr(x.indexprs,x.indrelid,true) FROM pg_index x
            JOIN pg_class r ON r.oid=x.indrelid JOIN pg_namespace n ON n.oid=r.relnamespace JOIN pg_class i
            ON i.oid=x.indexrelid JOIN pg_am am ON am.oid=i.relam WHERE n.nspname='bsl_runtime'""",
        "triggers": """/* triggers */ SELECT r.relname,t.tgname,t.tgtype::int,pn.nspname,p.proname
            FROM pg_trigger t JOIN pg_class r ON r.oid=t.tgrelid JOIN pg_namespace n ON n.oid=r.relnamespace
            JOIN pg_proc p ON p.oid=t.tgfoid JOIN pg_namespace pn ON pn.oid=p.pronamespace
            WHERE n.nspname='bsl_runtime' AND NOT t.tgisinternal""",
        "functions": """/* functions */ SELECT p.proname,l.lanname,pg_get_function_result(p.oid),p.pronargs,
            p.prosecdef,p.prokind,regexp_replace(btrim(p.prosrc),'\\s+',' ','g') FROM pg_proc p
            JOIN pg_namespace n ON n.oid=p.pronamespace JOIN pg_language l ON l.oid=p.prolang
            WHERE n.nspname='bsl_runtime'""",
    }
    catalog: dict[str, set[tuple[Any, ...]]] = {}
    for name, sql in queries.items():
        result = cast(
            Iterable[tuple[Any, ...]],
            connection.execute(sql),  # pyright: ignore[reportCallIssue,reportArgumentType]
        )
        catalog[name] = {_freeze(row) for row in result}
    return catalog


def check_runtime_schema(connection: Connection[Any]) -> None:
    version = connection.execute("SHOW server_version_num").fetchone()
    if version is None or version[0] != "180006":
        raise ValueError("PostgreSQL server_version_num must equal 180006")
    actual = _catalog(connection)
    actual["checks"] = {(*row[:2], _normalize_check(row[2]), *row[3:]) for row in actual["checks"]}
    normalized = {name: sorted((list(row) for row in rows), key=repr) for name, rows in actual.items()}
    digest = canonical_sha256(normalized)
    if digest != EXPECTED_CATALOG_SHA256:
        raise ValueError(f"database schema differs from the exact VS01-T05 boundary ({digest})")


def _artifact_rows(
    run_id: UUID,
    request: John15StudyRequest,
    execution: John15StudyExecutionRecord,
    brief: John15StudyAnswerArtifact,
    study: John15StudyAnswerArtifact,
    audit: John15RuntimeAuditReceipt,
) -> list[tuple[str, UUID, str, str, Jsonb]]:
    records = (
        ("REQUEST", request),
        ("EXECUTION_RECORD", execution),
        ("ANSWER_BRIEF", brief),
        ("ANSWER_STUDY", study),
        ("AUDIT_RECEIPT", audit),
    )
    return [
        (
            canonical_sha256(model.model_dump(mode="json")),
            run_id,
            kind,
            type(model).__name__,
            Jsonb(model.model_dump(mode="json")),
        )
        for kind, model in records
    ]


def _event_rows(
    run_id: UUID, artifacts: list[tuple[str, UUID, str, str, Jsonb]], created_at: datetime
) -> list[tuple[Any, ...]]:
    hashes = {item[2]: item[0] for item in artifacts}
    previous: str | None = None
    rows: list[tuple[Any, ...]] = []
    for sequence, (state, artifact_type) in enumerate(zip(STATES, ARTIFACT_TYPES, strict=True), 1):
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
        row = (
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
        rows.append(row)
        previous = event_sha
    return rows


def _insert_run(
    connection: Connection[Any], run_id: UUID, session_id: UUID, request: John15StudyRequest, created_at: datetime
) -> None:
    connection.execute(
        """INSERT INTO bsl_runtime.study_run
           (run_id, session_id, request_revision, supersedes_run_id, request_identity, run_key_sha256,
            packet_identity, packet_sha256, packet_receipt_identity, packet_receipt_file_sha256,
            runtime_spec_sha256, executor_kind, created_at)
           VALUES (%s,%s,%s,NULL,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (
            run_id,
            session_id,
            request.request_revision,
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
        raise psycopg.OperationalError("injected persistence failure")
    with connection.cursor() as cursor:
        cursor.executemany("INSERT INTO bsl_runtime.runtime_event VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", events)


def _validate_run(row: tuple[Any, ...], request: John15StudyRequest) -> tuple[UUID, UUID, datetime]:
    run_id, session_id, *stored, created_at = row
    expected = [
        2,
        None,
        ACTIVE_REQUEST_IDENTITY,
        run_key_sha256(request.request_identity),
        PACKET_IDENTITY,
        PACKET_SHA256,
        UUID(PACKET_RECEIPT_IDENTITY),
        PACKET_RECEIPT_SHA256,
        SPEC_SHA256,
        "DETERMINISTIC_REFERENCE",
    ]
    valid_time = created_at.tzinfo is not None and created_at.utcoffset() is not None
    if (
        request.request_revision != 2
        or request.request_identity != ACTIVE_REQUEST_IDENTITY
        or stored != expected
        or run_id.version != 7
        or session_id.version != 7
        or not valid_time
    ):
        raise ValueError("existing run key binds changed root authority")
    return run_id, session_id, created_at


def _validate_audit(
    audit: John15RuntimeAuditReceipt, run_id: UUID, session_id: UUID, implementation_commit: str
) -> None:
    counts = {"study_run": 1, "runtime_artifact": 5, "runtime_event": 11}
    expected = {
        "disposition": "PERSISTED",
        "run_id": str(run_id),
        "session_id": str(session_id),
        "database_schema_revision": "0001_vs01_t05_runtime",
        "database_rows_written": counts,
        "database_rows_verified": dict.fromkeys(counts, 0),
        "implementation_commit": implementation_commit,
    }
    if audit.model_dump(mode="json", include=set(expected)) != expected:
        raise ValueError("existing persisted audit receipt differs")


def _validate_artifacts(
    rows: list[tuple[Any, ...]],
    run_id: UUID,
    session_id: UUID,
    created_at: datetime,
    request: John15StudyRequest,
    execution: John15StudyExecutionRecord,
    brief: John15StudyAnswerArtifact,
    study: John15StudyAnswerArtifact,
    implementation_commit: str,
) -> tuple[John15RuntimeAuditReceipt, dict[str, str]]:
    by_type = {row[2]: row for row in rows}
    if len(rows) != 5 or set(by_type) != set(ARTIFACT_TYPES) | {"ANSWER_BRIEF"}:
        raise ValueError("existing runtime artifact set differs")
    audit = John15RuntimeAuditReceipt.model_validate_json(rfc8785.dumps(by_type["AUDIT_RECEIPT"][4]))
    _validate_audit(audit, run_id, session_id, implementation_commit)
    expected_rows = _artifact_rows(run_id, request, execution, brief, study, audit)
    expected = {row[2]: (*row[:4], row[4].obj, created_at) for row in expected_rows}
    if by_type != expected:
        raise ValueError("existing runtime artifact relational or semantic binding differs")
    return audit, {artifact_type: row[0] for artifact_type, row in by_type.items()}


def _validate_events(rows: list[tuple[Any, ...]], run_id: UUID, hashes: dict[str, str]) -> None:
    if len(rows) != 11:
        raise ValueError("existing runtime event count differs")
    previous: str | None = None
    for sequence, row in enumerate(rows, 1):
        event_id, stored_run, stored_sequence, state, artifact_sha, value, stored_previous, event_sha, created_at = row
        envelope = dict(value)
        stored_sha = envelope.pop("event_sha256", None)
        expected_envelope = {
            "event_id": str(event_id),
            "run_id": str(stored_run),
            "stream_sequence": stored_sequence,
            "state": state,
            "artifact_sha256": artifact_sha,
            "previous_event_sha256": stored_previous,
            "created_at": created_at.isoformat().replace("+00:00", "Z"),
        }
        valid = (
            event_id.version == 7
            and stored_run == run_id
            and stored_sequence == sequence
            and state == STATES[sequence - 1]
            and artifact_sha == hashes[ARTIFACT_TYPES[sequence - 1]]
            and stored_previous == previous
            and envelope == expected_envelope
            and stored_sha == event_sha
            and event_sha == canonical_sha256(envelope)
        )
        if not valid:
            raise ValueError("existing runtime event relational or hash binding differs")
        previous = event_sha


def _existing(
    connection: Connection[Any],
    row: tuple[Any, ...],
    request: John15StudyRequest,
    execution: John15StudyExecutionRecord,
    brief: John15StudyAnswerArtifact,
    study: John15StudyAnswerArtifact,
    implementation_commit: str,
) -> PersistenceOutcome:
    run_id, session_id, created_at = _validate_run(row, request)
    artifacts = connection.execute(
        "SELECT artifact_sha256,run_id,artifact_type,contract_name,artifact_json,created_at "
        "FROM bsl_runtime.runtime_artifact WHERE run_id=%s",
        (run_id,),
    ).fetchall()
    audit, hashes = _validate_artifacts(
        artifacts, run_id, session_id, created_at, request, execution, brief, study, implementation_commit
    )
    events = connection.execute(
        "SELECT event_id,run_id,stream_sequence,state,artifact_sha256,event_json,previous_event_sha256,"
        "event_sha256,created_at FROM bsl_runtime.runtime_event WHERE run_id=%s ORDER BY stream_sequence",
        (run_id,),
    ).fetchall()
    _validate_events(events, run_id, hashes)
    return PersistenceOutcome(run_id, session_id, True, audit)


def _root_row(connection: Connection[Any], run_key: str) -> tuple[Any, ...] | None:
    return connection.execute(
        "SELECT run_id,session_id,request_revision,supersedes_run_id,request_identity,run_key_sha256,"
        "packet_identity,packet_sha256,packet_receipt_identity,packet_receipt_file_sha256,"
        "runtime_spec_sha256,executor_kind,created_at FROM bsl_runtime.study_run WHERE run_key_sha256=%s",
        (run_key,),
    ).fetchone()


def _persist_connected(
    connection: Connection[Any],
    request: John15StudyRequest,
    execution: John15StudyExecutionRecord,
    brief: John15StudyAnswerArtifact,
    study: John15StudyAnswerArtifact,
    implementation_commit: str,
    started_ns: int,
    fail_after_artifacts: bool,
) -> PersistenceOutcome:
    check_runtime_schema(connection)
    connection.commit()
    key = run_key_sha256(request.request_identity)
    row = _root_row(connection, key)
    if row is not None:
        return _existing(connection, row, request, execution, brief, study, implementation_commit)
    run_id, session_id, created_at = uuid7(), uuid7(), datetime.now(UTC)
    from bsl.application.john15_study_runtime import _audit  # pyright: ignore[reportPrivateUsage]

    audit = _audit(execution, brief, study, "PERSISTED", implementation_commit, started_ns, run_id, session_id)
    artifacts = _artifact_rows(run_id, request, execution, brief, study, audit)
    events = _event_rows(run_id, artifacts, created_at)
    with connection.transaction():
        _insert_run(connection, run_id, session_id, request, created_at)
        _insert_bundle(connection, artifacts, events, fail_after_artifacts)
        inserted = _root_row(connection, key)
        if inserted is None:
            raise ValueError("new persisted run is missing after insertion")
        verified = _existing(connection, inserted, request, execution, brief, study, implementation_commit)
        if verified.audit_receipt != audit:
            raise ValueError("new persisted audit receipt differs after insertion")
    return PersistenceOutcome(run_id, session_id, False, audit)


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
) -> PersistenceOutcome:
    try:
        with psycopg.connect(database_url) as connection:
            return _persist_connected(
                connection, request, execution, brief, study, implementation_commit, started_ns, _fail_after_artifacts
            )
    except psycopg.Error:
        raise ValueError("database operation failed") from None
