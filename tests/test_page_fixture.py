from __future__ import annotations

import binascii
import copy
import hashlib
import json
import os
import struct
import zlib
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest
from pydantic import ValidationError
from uuid6 import uuid7

import bsl.application.john15_page_fixture as application
import bsl.infrastructure.runtime_persistence as runtime_persistence
import bsl.interfaces.cli as cli
from bsl.contracts.page_fixture import (
    BASE_SHA256,
    DEGRADED_SHA256,
    FIXTURE_JSON_SHA256,
    RENDERER_SHA256,
    John15PageExtractionGroundTruth,
    John15PageRegionGroundTruth,
    John15SyntheticPageFixture,
    John15SyntheticPagePublicationReceipt,
    canonical_fixture_bytes,
    fixture_identity,
    load_page_spec,
    publication_paths,
)
from bsl.infrastructure.page_fixture_store import (
    page_stage_path,
    prepare_publication,
    publish_fixture,
    verify_existing,
)

ROOT = Path(__file__).parents[1]
ASSETS = ROOT / "fixtures/VS01-T06"


def _fixture() -> John15SyntheticPageFixture:
    return John15SyntheticPageFixture.model_validate_json(canonical_fixture_bytes())


def _asset_bytes() -> tuple[bytes, bytes, bytes]:
    return (
        (ASSETS / "john-1-5-base-page.png").read_bytes(),
        (ASSETS / "john-1-5-degraded-illegibility-v1.png").read_bytes(),
        (ASSETS / "john-1-5-synthetic-fixture.json").read_bytes(),
    )


def _receipt(root: Path, disposition: str = "PUBLISHED") -> John15SyntheticPagePublicationReceipt:
    states = {
        "DRY_RUN_VALIDATED": (True, False, False, 0),
        "PUBLISHED": (False, True, False, 5),
        "VERIFIED_EXISTING": (False, False, True, 0),
    }
    dry, published, existing, writes = states[disposition]
    fingerprint = "a" * 64
    return John15SyntheticPagePublicationReceipt(
        receipt_identity=uuid7(),
        generated_at=datetime.now(UTC),
        implementation_commit="b" * 40,
        archive_root=str(root),
        disposition=disposition,
        dry_run=dry,
        fixture_identity=fixture_identity(),
        fixture_json_sha256=FIXTURE_JSON_SHA256,
        base_png_sha256=BASE_SHA256,
        degraded_png_sha256=DEGRADED_SHA256,
        renderer_authority_sha256=RENDERER_SHA256,
        publication_paths=publication_paths(FIXTURE_JSON_SHA256),
        authority_fingerprint_before=fingerprint,
        authority_fingerprint_after=fingerprint,
        archive_writes=writes,
        database_writes=0,
        raw_non_font_source_reads=0,
        ocr_invocations=0,
        vlm_invocations=0,
        model_invocations=0,
        benchmark_executions=0,
        published=published,
        verified_existing=existing,
    )


def test_exact_scene_contract_and_realized_assets() -> None:
    fixture, spec = _fixture(), load_page_spec()
    assert fixture.scene.model_dump(mode="json")["fixture_id"] == "SP01-DER-002"
    assert len(fixture.scene.regions) == 7 and len(fixture.scene.extractions) == 14
    assert [item.region_id for item in fixture.scene.regions] == spec["scene"]["reading_orders"]["benchmark_flat_order"]
    assert fixture.raster_assets[0]["sha256"] == BASE_SHA256
    assert fixture.raster_assets[1]["sha256"] == DEGRADED_SHA256
    assert fixture.fixture_identity == fixture_identity()
    assert hashlib.sha256(canonical_fixture_bytes()).hexdigest() == FIXTURE_JSON_SHA256


@pytest.mark.parametrize(
    ("path", "value"),
    (
        (("scene", "regions", 0, "functional_class"), "VERSE_TEXT"),
        (("scene", "regions", 0, "authority_class"), "TRANSLATION_TEXT"),
        (("scene", "regions", 0, "canonicality"), "CANONICAL_SCRIPTURE"),
        (("scene", "regions", 0, "pixel_bbox_xywh", 0), 121),
        (("scene", "regions", 0, "normalized_bbox_xyxy", 0), "0.075001"),
        (("scene", "region_groups", 0, "children", 0), "r_heading"),
        (("scene", "reading_orders", "benchmark_flat_order", 0), "r_heading"),
        (("scene", "relationships", 0, "relation"), "ANNOTATES"),
        (("scene", "styles", "style_heading", "font_size_px"), 69),
        (("scene", "styles", "style_canonical", "draw_lines", 0, "text"), "changed"),
        (("scene", "views", 1, "operations", 0, "region_id"), "r_note"),
        (("scene", "views", 1, "geometry_identity"), "CHANGED"),
        (("upstream_authority", "t03", "bundle_identity"), "0" * 64),
        (("upstream_authority", "t04", "packet_identity"), "0" * 64),
        (("upstream_authority", "t05", "canonical_run_id"), "01900000-0000-7000-8000-000000000000"),
        (("renderer_authority_sha256",), "0" * 64),
        (("renderer_authority", "fonts", 0, "sha256"), "0" * 64),
        (("rights_and_public_display", "page_status"), "HISTORICAL_PUBLISHER_PAGE"),
        (("operation_counts", "model_invocations"), 1),
    ),
)
def test_fixture_rejects_frozen_mutations(path: tuple[object, ...], value: object) -> None:
    data = json.loads(canonical_fixture_bytes())
    target: object = data
    for key in path[:-1]:
        target = target[key]  # type: ignore[index]
    target[path[-1]] = value  # type: ignore[index]
    with pytest.raises(ValidationError):
        John15SyntheticPageFixture.model_validate_json(json.dumps(data))


def test_region_and_extraction_keep_canonical_lookup_separate() -> None:
    spec = load_page_spec()
    header = copy.deepcopy(spec["scene"]["regions"][0])
    header["canonicality"] = "CANONICAL_SCRIPTURE"
    with pytest.raises(ValidationError):
        John15PageRegionGroundTruth.model_validate_json(json.dumps(header))
    degraded = copy.deepcopy(spec["scene"]["extractions"][10])
    degraded["visual_transcription"] = degraded["canonical_lookup"]["text"]
    with pytest.raises(ValidationError):
        John15PageExtractionGroundTruth.model_validate_json(json.dumps(degraded))
    degraded = copy.deepcopy(spec["scene"]["extractions"][10])
    degraded["ocr_or_vlm_used"] = True
    with pytest.raises(ValidationError):
        John15PageExtractionGroundTruth.model_validate_json(json.dumps(degraded))


def _png_chunks(data: bytes) -> list[tuple[bytes, bytes]]:
    offset, chunks = 8, []
    while offset < len(data):
        size = struct.unpack(">I", data[offset : offset + 4])[0]
        chunks.append((data[offset + 4 : offset + 8], data[offset + 8 : offset + 8 + size]))
        offset += size + 12
    return chunks


def _png(chunks: list[tuple[bytes, bytes]]) -> bytes:
    body = bytearray(b"\x89PNG\r\n\x1a\n")
    for kind, payload in chunks:
        body += struct.pack(">I", len(payload)) + kind + payload
        body += struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)
    return bytes(body)


@pytest.mark.parametrize("case", ("dimension", "chunk", "crc", "filter", "metadata"))
def test_png_verifier_rejects_structural_mutations(case: str) -> None:
    base = _asset_bytes()[0]
    chunks = _png_chunks(base)
    if case == "dimension":
        values = list(struct.unpack(">IIBBBBB", chunks[0][1]))
        values[0] = 1599
        chunks[0] = (b"IHDR", struct.pack(">IIBBBBB", *values))
        changed = _png(chunks)
    elif case == "chunk":
        chunks[1] = (b"tEXt", chunks[1][1])
        changed = _png(chunks)
    elif case == "crc":
        changed = base[:-1] + bytes((base[-1] ^ 1,))
    elif case == "filter":
        raw = bytearray(zlib.decompress(chunks[3][1]))
        raw[0] = 1
        chunks[3] = (b"IDAT", zlib.compress(bytes(raw), level=9))
        changed = _png(chunks)
    else:
        chunks.insert(3, (b"tEXt", b"forbidden"))
        changed = _png(chunks)
    with pytest.raises(ValueError):
        application.inspect_canonical_png(changed)


def test_png_verifier_accepts_both_committed_assets() -> None:
    for data in _asset_bytes()[:2]:
        result = application.inspect_canonical_png(data)
        assert result == {
            "chunks": ["IHDR", "sRGB", "pHYs", "IDAT", "IEND"],
            "crc_valid": True,
            "dimensions": [1600, 2200],
            "rgb8": True,
            "filter": 0,
        }


def test_temp_publication_is_receipt_last_immutable_and_idempotent(tmp_path: Path) -> None:
    (tmp_path / ".incoming").mkdir()
    unrelated = tmp_path / ".incoming/unrelated-stage"
    unrelated.mkdir()
    fixture, (base, degraded, fixture_bytes) = _fixture(), _asset_bytes()
    receipt = _receipt(tmp_path)
    publish_fixture(tmp_path, fixture, base, degraded, fixture_bytes, receipt)
    assert unrelated.is_dir() and not page_stage_path(tmp_path, FIXTURE_JSON_SHA256).exists()
    for relative in publication_paths(FIXTURE_JSON_SHA256):
        assert stat_mode(tmp_path / relative) == 0o444
    assert verify_existing(tmp_path, fixture, base, degraded, fixture_bytes) == receipt
    with pytest.raises(ValueError, match="already exists"):
        publish_fixture(tmp_path, fixture, base, degraded, fixture_bytes, _receipt(tmp_path))


def stat_mode(path: Path) -> int:
    return os.stat(path, follow_symlinks=False).st_mode & 0o777


def test_partial_publication_recovers_and_mismatch_refuses(tmp_path: Path) -> None:
    (tmp_path / ".incoming").mkdir()
    fixture, (base, degraded, fixture_bytes) = _fixture(), _asset_bytes()
    publish_fixture(tmp_path, fixture, base, degraded, fixture_bytes, _receipt(tmp_path))
    receipt_path = tmp_path / publication_paths(FIXTURE_JSON_SHA256)[-1]
    os.chmod(receipt_path, 0o644)
    receipt_path.unlink()
    publish_fixture(tmp_path, fixture, base, degraded, fixture_bytes, _receipt(tmp_path))
    base_path = tmp_path / publication_paths(FIXTURE_JSON_SHA256)[0]
    os.chmod(base_path, 0o644)
    with pytest.raises(ValueError, match="differs or is mutable"):
        verify_existing(tmp_path, fixture, base, degraded, fixture_bytes)


def test_exact_stage_recovers_without_touching_unrelated(tmp_path: Path) -> None:
    incoming = tmp_path / ".incoming"
    incoming.mkdir()
    unrelated = incoming / "foreign"
    unrelated.write_text("opaque")
    fixture, (base, degraded, fixture_bytes) = _fixture(), _asset_bytes()
    stage = page_stage_path(tmp_path, FIXTURE_JSON_SHA256)
    stage.mkdir()
    (stage / "base").write_bytes(base)
    os.chmod(stage / "base", 0o444)
    publish_fixture(tmp_path, fixture, base, degraded, fixture_bytes, _receipt(tmp_path))
    assert unrelated.read_text() == "opaque" and not stage.exists()


def test_complete_publication_cleans_valid_stale_own_stage(tmp_path: Path) -> None:
    (tmp_path / ".incoming").mkdir()
    fixture, (base, degraded, fixture_bytes) = _fixture(), _asset_bytes()
    receipt = _receipt(tmp_path)
    publish_fixture(tmp_path, fixture, base, degraded, fixture_bytes, receipt)
    stage = page_stage_path(tmp_path, FIXTURE_JSON_SHA256)
    stage.mkdir()
    stale = stage / "receipt"
    stale.write_bytes((tmp_path / publication_paths(FIXTURE_JSON_SHA256)[-1]).read_bytes())
    os.chmod(stale, 0o444)
    assert prepare_publication(tmp_path, fixture, base, degraded, fixture_bytes, _receipt(tmp_path)) == receipt
    assert not stage.exists()


def test_application_dry_run_has_zero_operations(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / ".incoming").mkdir()
    dummy_t04 = object()
    monkeypatch.setattr(application, "_require_root", lambda *_args: tmp_path)
    monkeypatch.setattr(application, "_font_authority", lambda _root: {"bundle_identity": "x"})
    monkeypatch.setattr(application, "load_t04_authority", lambda *_args, **_kwargs: dummy_t04)
    monkeypatch.setattr(application, "_archive_fingerprint", lambda *_args: "c" * 64)
    result = application.generate_john15_page_fixture(
        tmp_path,
        dry_run=True,
        _expected_archive_root=tmp_path,
        _implementation_commit="d" * 40,
        _t05_verifier=lambda authority: {"verified": authority is dummy_t04},
    )
    receipt = result.receipt
    assert receipt.disposition == "DRY_RUN_VALIDATED"
    assert receipt.archive_writes == receipt.database_writes == receipt.model_invocations == 0
    assert receipt.ocr_invocations == receipt.vlm_invocations == receipt.benchmark_executions == 0
    assert result.published is result.verified_existing is False and list(tmp_path.rglob("*")) == [
        tmp_path / ".incoming"
    ]


def _patch_application_authority(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> object:
    dummy_t04 = object()
    monkeypatch.setattr(application, "_require_root", lambda *_args: tmp_path)
    monkeypatch.setattr(application, "_font_authority", lambda _root: {"bundle_identity": "x"})
    monkeypatch.setattr(application, "load_t04_authority", lambda *_args, **_kwargs: dummy_t04)
    monkeypatch.setattr(application, "_archive_fingerprint", lambda *_args: "c" * 64)
    return dummy_t04


def test_application_temp_live_publication_and_verification(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / ".incoming").mkdir()
    dummy_t04 = _patch_application_authority(tmp_path, monkeypatch)
    arguments = {
        "dry_run": False,
        "_expected_archive_root": tmp_path,
        "_implementation_commit": "d" * 40,
        "_t05_verifier": lambda authority: {"verified": authority is dummy_t04},
    }
    first = application.generate_john15_page_fixture(tmp_path, **arguments)
    second = application.generate_john15_page_fixture(tmp_path, **arguments)
    assert first.published and not first.verified_existing and first.receipt.disposition == "PUBLISHED"
    assert second.verified_existing and not second.published and second.receipt.disposition == "VERIFIED_EXISTING"


def test_narrow_font_authority_from_synthetic_records(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    objects = (
        ("regular_font", "TTF/SourceSerif4-Regular.ttf", b"regular", False),
        ("italic_font", "TTF/SourceSerif4-It.ttf", b"italic", False),
        ("license_object", "LICENSE.md", b"license", True),
    )
    font_records = []
    for role, relative, data, rights in objects:
        digest = hashlib.sha256(data).hexdigest()
        path = tmp_path / "objects/sha256" / digest[:2] / digest
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        os.chmod(path, 0o444)
        font_records.append(
            {
                "role": role,
                "relative_path": relative,
                "sha256": digest,
                "byte_count": len(data),
                "rights_evidence": rights,
            }
        )
    bundle = {
        "bundle_identity": "bundle",
        "sources": [{"source_id": "SP01-SRC-006"}],
        "source_serif": {
            item["role"]: {key: value for key, value in item.items() if key != "role"} for item in font_records
        },
    }
    receipt = {"receipt_identity": "receipt"}
    bundle_bytes = json.dumps(bundle).encode()
    receipt_bytes = json.dumps(receipt).encode()
    bundle_path = tmp_path / application.T03_BUNDLE
    receipt_path = tmp_path / application.T03_RECEIPT
    bundle_path.parent.mkdir(parents=True)
    receipt_path.parent.mkdir(parents=True)
    bundle_path.write_bytes(bundle_bytes)
    receipt_path.write_bytes(receipt_bytes)
    os.chmod(bundle_path, 0o444)
    os.chmod(receipt_path, 0o444)
    renderer = {"t03_authority": {"bundle_identity": "bundle", "receipt_id": "receipt"}, "fonts": font_records}
    monkeypatch.setattr(application, "load_renderer_authority", lambda: renderer)
    result = application._font_authority(
        tmp_path,
        _bundle_sha256=hashlib.sha256(bundle_bytes).hexdigest(),
        _receipt_sha256=hashlib.sha256(receipt_bytes).hexdigest(),
    )
    assert result == renderer["t03_authority"]


def test_low_level_authority_readers_fail_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValueError, match="missing or unsafe"):
        application._bytes(tmp_path / "missing")
    mutable = tmp_path / "mutable"
    mutable.write_bytes(b"x")
    with pytest.raises(ValueError, match="immutable regular"):
        application._bytes(mutable, immutable=True)
    monkeypatch.setattr(application, "AUTHORITY_FILES", {str(mutable): "0" * 64})
    with pytest.raises(ValueError, match="committed authority hash differs"):
        application._validate_repo_authority()


def test_fixture_asset_and_png_parse_errors_are_redacted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValueError, match="signature"):
        application.inspect_canonical_png(b"not-png")
    malformed = _png([(b"IHDR", b"bad"), (b"sRGB", b"\0"), (b"pHYs", b"bad"), (b"IDAT", b"bad"), (b"IEND", b"")])
    with pytest.raises(ValueError, match="payload"):
        application.inspect_canonical_png(malformed)
    monkeypatch.setattr(application, "FIXTURE_ROOT", tmp_path)
    for name in ("john-1-5-base-page.png", "john-1-5-degraded-illegibility-v1.png", "john-1-5-synthetic-fixture.json"):
        (tmp_path / name).write_bytes(b"changed")
    with pytest.raises(ValueError, match="committed page fixture bytes differ"):
        application._fixture_assets()


def test_owner_database_coordinate_never_requires_exposure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(application, "_bytes", lambda _path: b"p@ss word\n")
    assert application._owner_database_url().endswith("bsl_owner:p%40ss%20word@127.0.0.1:55432/bsl_runtime")
    monkeypatch.setattr(application, "_bytes", lambda _path: b"")
    with pytest.raises(ValueError, match="credential file is invalid"):
        application._owner_database_url()


def test_authority_fingerprint_and_git_head_are_deterministic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / ".incoming").mkdir()
    marker = tmp_path / ".bsl-archive-root.json"
    marker.write_bytes(b"marker")
    os.chmod(marker, 0o444)
    monkeypatch.setattr(application, "_authority_fingerprint", lambda _authority: "t04")
    first = application._archive_fingerprint(tmp_path, {"t03": True}, object(), {"t05": True})
    second = application._archive_fingerprint(tmp_path, {"t03": True}, object(), {"t05": True})
    assert first == second and len(first) == 64
    head = application._git_head()
    assert len(head) == 40 and set(head) <= set("0123456789abcdef")


def test_dry_run_refuses_own_stage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / ".incoming").mkdir()
    dummy_t04 = _patch_application_authority(tmp_path, monkeypatch)
    page_stage_path(tmp_path, FIXTURE_JSON_SHA256).mkdir()
    with pytest.raises(ValueError, match="dry run refuses"):
        application.generate_john15_page_fixture(
            tmp_path,
            dry_run=True,
            _expected_archive_root=tmp_path,
            _implementation_commit="d" * 40,
            _t05_verifier=lambda authority: {"verified": authority is dummy_t04},
        )


class _Rows:
    def __init__(self, value: object) -> None:
        self.value = value

    def fetchone(self) -> object:
        return self.value


class _ReadOnlyConnection:
    read_only = False

    def __enter__(self) -> _ReadOnlyConnection:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def execute(self, sql: str, _parameters: object = None) -> _Rows:
        if "FROM bsl_runtime.study_run WHERE" in sql:
            return _Rows(("root-row",))
        if "count(*)" in sql:
            return _Rows((5 if "runtime_artifact" in sql else 11 if "runtime_event" in sql else 1,))
        if "artifact_type='AUDIT_RECEIPT'" in sql:
            return _Rows(({"implementation_commit": "e" * 40},))
        return _Rows(("f" * 64,))


def test_owner_t05_verification_is_read_only_and_exact(monkeypatch: pytest.MonkeyPatch) -> None:
    request = SimpleNamespace(request_identity=application.T05_EXPECTED["request"])
    execution = SimpleNamespace(execution_record_identity=application.T05_EXPECTED["execution"])
    answers = {
        "BRIEF": SimpleNamespace(answer_identity=application.T05_EXPECTED["brief"]),
        "STUDY": SimpleNamespace(answer_identity=application.T05_EXPECTED["study"]),
    }
    monkeypatch.setattr(application, "_verified_execution", lambda _authority: (request, execution))
    monkeypatch.setattr(application, "_answer", lambda _execution, mode: answers[mode])
    monkeypatch.setattr(application, "_owner_database_url", lambda: "redacted")
    monkeypatch.setattr(application.psycopg, "connect", lambda _url: _ReadOnlyConnection())
    monkeypatch.setattr(runtime_persistence, "check_runtime_schema", lambda _connection: None)
    outcome = SimpleNamespace(
        run_id=UUID(application.T05_EXPECTED["run_id"]), session_id=UUID(application.T05_EXPECTED["session_id"])
    )
    monkeypatch.setattr(runtime_persistence, "_existing", lambda *_args: outcome)
    result = application.verify_t05_owner(object())
    assert result["row_counts"] == {"study_run": 1, "runtime_artifact": 5, "runtime_event": 11}
    assert result["database_writes"] == 0 and result["final_event_sha256"] == "f" * 64


def test_page_cli_is_public_safe_and_machine_readable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    result = application.PageFixtureResult(_fixture(), _receipt(tmp_path, "DRY_RUN_VALIDATED"), False, False)
    monkeypatch.setattr(cli, "generate_john15_page_fixture", lambda *_args, **_kwargs: result)
    code = cli.main(["page", "john-1-5-synthetic-fixture", "--archive-root", str(tmp_path), "--dry-run"])
    raw = capsys.readouterr().out
    output = json.loads(raw)
    assert code == 0 and "scorer_only_underlying_text" not in raw
    assert output["receipt"]["disposition"] == "DRY_RUN_VALIDATED"
    assert output["published"] is output["verified_existing"] is False
