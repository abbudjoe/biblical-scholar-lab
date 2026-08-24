from __future__ import annotations

import binascii
import hashlib
import json
import os
import re
import stat
import struct
import subprocess
import zlib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import psycopg
import rfc8785
from pydantic import ValidationError
from uuid6 import uuid7

from bsl.application.john15_evidence import CANONICAL_ARCHIVE_ROOT, _require_root  # pyright: ignore[reportPrivateUsage]
from bsl.application.john15_study_runtime import (
    _answer,  # pyright: ignore[reportPrivateUsage]
    _authority_fingerprint,  # pyright: ignore[reportPrivateUsage]
    _verified_execution,  # pyright: ignore[reportPrivateUsage]
    load_t04_authority,
)
from bsl.contracts.page_fixture import (
    ACTIVATION_SHA256,
    BASE_BYTES,
    BASE_SHA256,
    DEGRADED_BYTES,
    DEGRADED_SHA256,
    DESIGN_SHA256,
    ERRATUM_SHA256,
    FIXTURE_JSON_BYTES,
    FIXTURE_JSON_SHA256,
    RENDERER_SHA256,
    SPEC_SHA256,
    John15SyntheticPageFixture,
    John15SyntheticPagePublicationReceipt,
    canonical_fixture_bytes,
    fixture_identity,
    load_page_spec,
    load_renderer_authority,
    publication_paths,
)
from bsl.infrastructure.page_fixture_store import page_stage_path, prepare_publication, publish_fixture

ROOT = Path(__file__).parents[3]
FIXTURE_ROOT = ROOT / "fixtures/VS01-T06"
T03_BUNDLE = "snapshots/normalization/john-1-5.json"
T03_RECEIPT = "manifests/normalization/john-1-5/normalization-receipt.json"
AUTHORITY_FILES = {
    "design/approved/VS01-T06-synthetic-page-region-grounding.md": DESIGN_SHA256,
    "design/approved/VS01-T06-page-fixture-spec.json": SPEC_SHA256,
    "design/approved/VS01-T06-ERRATA-01-renderer-font-authority.md": ERRATUM_SHA256,
    "activations/ACT-VS01-T06-SYNTHETIC-PAGE-FIXTURE-v1.json": ACTIVATION_SHA256,
    "design/approved/VS01-T06-renderer-authority.json": RENDERER_SHA256,
}
T05_EXPECTED = {
    "run_id": "01a030a1-c3ca-76f6-b4c8-f74392e2cd91",
    "session_id": "01a030a1-c3cb-72d0-aac0-19da47db369e",
    "request": "5b0d413278c3dcf03421989dcec84228a828d13236a232977b448b14bd0b68ef",
    "execution": "f0697ce01cfa4579223a59042e49de7377d3ec5dee7cca29468bbab3cfba20cc",
    "brief": "b97e895bfc640d0020f7146cd88112fd0f6f9ec8669bfab316c8d49688aef2a0",
    "study": "f18264255ab9117cdd7fa40d9da35c614d31a9bfcabce7a5e95e7b0a040424fd",
}
NewUuid = Callable[[], UUID]
Now = Callable[[], datetime]
T05Verifier = Callable[[Any], dict[str, Any]]


@dataclass(frozen=True)
class PageFixtureResult:
    fixture: John15SyntheticPageFixture
    receipt: John15SyntheticPagePublicationReceipt
    published: bool
    verified_existing: bool


def _bytes(path: Path, *, immutable: bool = False) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        metadata = os.fstat(descriptor)
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            data = stream.read()
        os.close(descriptor)
    except OSError:
        raise ValueError(f"required fixture authority is missing or unsafe: {path.name}") from None
    if not stat.S_ISREG(metadata.st_mode) or (immutable and stat.S_IMODE(metadata.st_mode) != 0o444):
        raise ValueError(f"required fixture authority is not an immutable regular file: {path.name}")
    return data


def _validate_repo_authority() -> None:
    for relative, expected in AUTHORITY_FILES.items():
        if hashlib.sha256(_bytes(ROOT / relative)).hexdigest() != expected:
            raise ValueError(f"committed authority hash differs: {Path(relative).name}")
    load_page_spec()
    load_renderer_authority()


def inspect_canonical_png(data: bytes) -> dict[str, Any]:
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("fixture PNG signature differs")
    offset = 8
    names: list[str] = []
    payloads: list[bytes] = []
    while offset < len(data):
        size = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : offset + 8 + size]
        crc = struct.unpack(">I", data[offset + 8 + size : offset + 12 + size])[0]
        if binascii.crc32(kind + payload) & 0xFFFFFFFF != crc:
            raise ValueError("fixture PNG CRC differs")
        names.append(kind.decode("ascii"))
        payloads.append(payload)
        offset += size + 12
    if names != ["IHDR", "sRGB", "pHYs", "IDAT", "IEND"]:
        raise ValueError("fixture PNG chunk sequence differs")
    try:
        header = struct.unpack(">IIBBBBB", payloads[0])
        scanlines = zlib.decompress(payloads[3])
    except (IndexError, struct.error, zlib.error):
        raise ValueError("fixture PNG payload is invalid") from None
    valid = (
        offset == len(data),
        header == (1600, 2200, 8, 2, 0, 0, 0),
        payloads[1] == b"\x00",
        payloads[2] == struct.pack(">IIB", 7874, 7874, 1),
        payloads[4] == b"",
        len(scanlines) == 2200 * 4801,
        all(scanlines[row * 4801] == 0 for row in range(2200)),
    )
    if not all(valid):
        raise ValueError("fixture PNG structure or scanlines differ")
    return {"chunks": names, "crc_valid": True, "dimensions": [1600, 2200], "rgb8": True, "filter": 0}


def _fixture_assets() -> tuple[John15SyntheticPageFixture, bytes, bytes, bytes]:
    base = _bytes(FIXTURE_ROOT / "john-1-5-base-page.png")
    degraded = _bytes(FIXTURE_ROOT / "john-1-5-degraded-illegibility-v1.png")
    fixture_bytes = _bytes(FIXTURE_ROOT / "john-1-5-synthetic-fixture.json")
    exact = (
        (hashlib.sha256(base).hexdigest(), len(base)) == (BASE_SHA256, BASE_BYTES),
        (hashlib.sha256(degraded).hexdigest(), len(degraded)) == (DEGRADED_SHA256, DEGRADED_BYTES),
        (hashlib.sha256(fixture_bytes).hexdigest(), len(fixture_bytes)) == (FIXTURE_JSON_SHA256, FIXTURE_JSON_BYTES),
        fixture_bytes == canonical_fixture_bytes(),
    )
    if not all(exact):
        raise ValueError("committed page fixture bytes differ from realized authority")
    inspect_canonical_png(base)
    inspect_canonical_png(degraded)
    try:
        fixture = John15SyntheticPageFixture.model_validate_json(fixture_bytes)
    except ValidationError:
        raise ValueError("committed page fixture JSON is invalid") from None
    return fixture, base, degraded, fixture_bytes


def _validate_font_binding(root: Path, actual: dict[str, Any], expected: dict[str, Any]) -> None:
    fields = (actual["relative_path"], actual["sha256"], actual["byte_count"], actual["rights_evidence"])
    expected_fields = (
        expected["relative_path"],
        expected["sha256"],
        expected["byte_count"],
        expected["rights_evidence"],
    )
    if fields != expected_fields:
        raise ValueError("T03 Source Serif binding differs")
    object_path = root / "objects/sha256" / expected["sha256"][:2] / expected["sha256"]
    data = _bytes(object_path, immutable=True)
    if (hashlib.sha256(data).hexdigest(), len(data)) != (expected["sha256"], expected["byte_count"]):
        raise ValueError("Source Serif archive object differs")


def _font_authority(
    root: Path,
    *,
    _bundle_sha256: str = "397f7c8908bf8e8533b23eb808ab7c0ede796c95d7b49451fa92f40261ee19d6",
    _receipt_sha256: str = "e4871e859481614da6d4f52e77fa41e35234884b9f5baacad68c4855e2ed6af2",
) -> dict[str, Any]:
    bundle_bytes, receipt_bytes = _bytes(root / T03_BUNDLE, immutable=True), _bytes(root / T03_RECEIPT, immutable=True)
    if (
        hashlib.sha256(bundle_bytes).hexdigest() != _bundle_sha256
        or hashlib.sha256(receipt_bytes).hexdigest() != _receipt_sha256
    ):
        raise ValueError("T03 font bundle or receipt file hash differs")
    bundle, receipt, renderer = json.loads(bundle_bytes), json.loads(receipt_bytes), load_renderer_authority()
    if (
        bundle.get("bundle_identity") != renderer["t03_authority"]["bundle_identity"]
        or receipt.get("receipt_identity") != renderer["t03_authority"]["receipt_id"]
    ):
        raise ValueError("T03 font bundle or receipt identity differs")
    if not any(item.get("source_id") == "SP01-SRC-006" for item in bundle.get("sources", ())):
        raise ValueError("Source Serif source membership differs")
    for expected in renderer["fonts"]:
        _validate_font_binding(root, bundle["source_serif"][expected["role"]], expected)
    return renderer["t03_authority"]


def _owner_database_url() -> str:
    password = _bytes(Path.home() / ".config/bsl/vs01-t05-postgres.password").decode().strip()
    if not password or "\n" in password:
        raise ValueError("owner PostgreSQL credential file is invalid")
    return f"postgresql://bsl_owner:{quote(password, safe='')}@127.0.0.1:55432/bsl_runtime"


def _t05_counts(connection: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for name in ("study_run", "runtime_artifact", "runtime_event"):
        row = connection.execute(f"SELECT count(*) FROM bsl_runtime.{name}").fetchone()
        if row is None:
            raise ValueError("canonical T05 row count is missing")
        counts[name] = int(row[0])
    return counts


def _t05_rows(connection: Any) -> tuple[Any, dict[str, int], Any, str]:
    root = connection.execute(
        """SELECT run_id,session_id,request_revision,supersedes_run_id,request_identity,
        run_key_sha256,packet_identity,packet_sha256,packet_receipt_identity,
        packet_receipt_file_sha256,runtime_spec_sha256,executor_kind,created_at
        FROM bsl_runtime.study_run WHERE run_id=%s""",
        (T05_EXPECTED["run_id"],),
    ).fetchone()
    audit = connection.execute(
        """SELECT artifact_json FROM bsl_runtime.runtime_artifact
        WHERE run_id=%s AND artifact_type='AUDIT_RECEIPT'""",
        (T05_EXPECTED["run_id"],),
    ).fetchone()
    final = connection.execute(
        """SELECT event_sha256 FROM bsl_runtime.runtime_event WHERE run_id=%s
        ORDER BY stream_sequence DESC LIMIT 1""",
        (T05_EXPECTED["run_id"],),
    ).fetchone()
    if root is None or audit is None:
        raise ValueError("canonical T05 run is missing")
    if final is None:
        raise ValueError("canonical T05 event chain is missing")
    return root, _t05_counts(connection), audit, cast(str, final[0])


def verify_t05_owner(authority: Any) -> dict[str, Any]:
    from bsl.infrastructure.runtime_persistence import (  # pyright: ignore[reportPrivateUsage]
        _existing,  # pyright: ignore[reportPrivateUsage]
        check_runtime_schema,
    )

    request, execution = _verified_execution(authority)
    brief, study = _answer(execution, "BRIEF"), _answer(execution, "STUDY")
    try:
        with psycopg.connect(_owner_database_url()) as connection:
            connection.read_only = True
            check_runtime_schema(connection)
            row, counts, audit_row, final_hash = _t05_rows(connection)
            outcome = _existing(
                connection, row, request, execution, brief, study, audit_row[0]["implementation_commit"]
            )
    except psycopg.Error:
        raise ValueError("owner PostgreSQL read-only verification failed") from None
    observed = {
        "run_id": str(outcome.run_id),
        "session_id": str(outcome.session_id),
        "request": request.request_identity,
        "execution": execution.execution_record_identity,
        "brief": brief.answer_identity,
        "study": study.answer_identity,
    }
    if observed != T05_EXPECTED or counts != {"study_run": 1, "runtime_artifact": 5, "runtime_event": 11}:
        raise ValueError("canonical T05 authority differs")
    return observed | {
        "catalog_sha256": "b712aeed326f78fdfbb7d69d3fdf2816f6f6446b8bbefad0449aa525cd4552e4",
        "row_counts": counts,
        "final_event_sha256": final_hash,
        "database_writes": 0,
    }


def _archive_fingerprint(root: Path, t03: dict[str, Any], t04: Any, t05: dict[str, Any]) -> str:
    incoming = root / ".incoming"
    inventory = sorted(item.name for item in incoming.iterdir())
    value = {
        "root_marker_sha256": hashlib.sha256(_bytes(root / ".bsl-archive-root.json", immutable=True)).hexdigest(),
        "t03": t03,
        "t04": _authority_fingerprint(t04),
        "t05": t05,
        "incoming_inventory_sha256": hashlib.sha256(rfc8785.dumps(inventory)).hexdigest(),
        "fixture_assets": {"base": BASE_SHA256, "degraded": DEGRADED_SHA256, "json": FIXTURE_JSON_SHA256},
    }
    return hashlib.sha256(rfc8785.dumps(value)).hexdigest()


def _git_head() -> str:
    result = subprocess.run(("git", "rev-parse", "HEAD"), cwd=ROOT, check=True, capture_output=True, text=True)
    value = result.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError("implementation commit cannot be resolved")
    return value


def _receipt(
    root: Path, disposition: str, before: str, after: str, commit: str, new_uuid: NewUuid, now: Now
) -> John15SyntheticPagePublicationReceipt:
    state = {
        "DRY_RUN_VALIDATED": (True, False, False, 0),
        "PUBLISHED": (False, True, False, 5),
        "VERIFIED_EXISTING": (False, False, True, 0),
    }[disposition]
    return John15SyntheticPagePublicationReceipt(
        receipt_identity=new_uuid(),
        generated_at=now(),
        implementation_commit=commit,
        archive_root=str(root),
        disposition=cast(Any, disposition),
        dry_run=state[0],
        fixture_identity=fixture_identity(),
        fixture_json_sha256=FIXTURE_JSON_SHA256,
        base_png_sha256=BASE_SHA256,
        degraded_png_sha256=DEGRADED_SHA256,
        renderer_authority_sha256=RENDERER_SHA256,
        publication_paths=publication_paths(FIXTURE_JSON_SHA256),
        authority_fingerprint_before=before,
        authority_fingerprint_after=after,
        archive_writes=state[3],
        database_writes=0,
        raw_non_font_source_reads=0,
        ocr_invocations=0,
        vlm_invocations=0,
        model_invocations=0,
        benchmark_executions=0,
        published=state[1],
        verified_existing=state[2],
    )


def generate_john15_page_fixture(
    archive_root: Path,
    *,
    dry_run: bool,
    _expected_archive_root: Path = CANONICAL_ARCHIVE_ROOT,
    _implementation_commit: str | None = None,
    _new_uuid: NewUuid = uuid7,
    _now: Now = lambda: datetime.now(UTC),
    _t05_verifier: T05Verifier = verify_t05_owner,
) -> PageFixtureResult:
    _validate_repo_authority()
    fixture, base, degraded, fixture_bytes = _fixture_assets()
    root = _require_root(archive_root, _expected_archive_root)
    t03, t04 = _font_authority(root), load_t04_authority(root, _expected_archive_root=_expected_archive_root)
    t05 = _t05_verifier(t04)
    before = _archive_fingerprint(root, t03, t04, t05)
    commit = _implementation_commit or _git_head()
    if dry_run:
        if page_stage_path(root, FIXTURE_JSON_SHA256).exists():
            raise ValueError("dry run refuses an existing fixture-bound page stage")
        after = _archive_fingerprint(root, t03, t04, t05)
        return PageFixtureResult(
            fixture, _receipt(root, "DRY_RUN_VALIDATED", before, after, commit, _new_uuid, _now), False, False
        )
    provisional = _receipt(root, "PUBLISHED", before, before, commit, _new_uuid, _now)
    existing = prepare_publication(root, fixture, base, degraded, fixture_bytes, provisional)
    disposition = "VERIFIED_EXISTING" if existing else "PUBLISHED"
    receipt = _receipt(root, disposition, before, before, commit, _new_uuid, _now)
    if existing is None:
        publish_fixture(root, fixture, base, degraded, fixture_bytes, receipt)
    after = _archive_fingerprint(root, t03, t04, t05)
    if after != before or page_stage_path(root, FIXTURE_JSON_SHA256).exists():
        raise ValueError("page publication changed upstream authority or left its exact stage")
    return PageFixtureResult(fixture, receipt, existing is None, existing is not None)
