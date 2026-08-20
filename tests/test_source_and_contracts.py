from __future__ import annotations

import hashlib
import json
import socket
from pathlib import Path

import pytest
from pydantic import ValidationError

from bsl.application.source_admission import HARD_PROHIBITIONS, compile_source_plan, semantic_bytes
from bsl.contracts.source_admission import SourceAcquisitionDryRun

MANIFEST = Path("design/approved/SOURCE-PLAN-01-source-admission-manifest.json")


def test_exact_six_source_plan_is_deterministic(monkeypatch: pytest.MonkeyPatch) -> None:
    def blocked(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("external network access attempted")

    monkeypatch.setattr(socket.socket, "connect", blocked)
    first = compile_source_plan(MANIFEST)
    second = compile_source_plan(MANIFEST)
    assert (first.receipt_id, first.generated_at) != (second.receipt_id, second.generated_at)
    assert semantic_bytes(first) == semantic_bytes(second)
    assert first.semantic_sha256 == second.semantic_sha256 == hashlib.sha256(semantic_bytes(first)).hexdigest()
    payload = first.semantic_payload
    assert tuple(source.source_id for source in payload.sources) == tuple(f"SP01-SRC-00{i}" for i in range(1, 7))
    assert (payload.hard_prohibitions, payload.source_acquisition_authorized_now) == (HARD_PROHIBITIONS, False)
    assert payload.sources[3].revision == "ACQUISITION_TIMESTAMP_PLUS_SHA256_REQUIRED"
    assert (payload.sources[1].admitted_fields[-1], payload.sources[1].excluded_fields[-1]) == ("lemma", "word_senses")
    assert payload.sources[5].normalized_scope == ()
    assert all(source.planned_manifest_identity == payload.manifest_identity for source in payload.sources)
    assert all(
        source.relative_quarantine_plan == f"quarantine/SOURCE-PLAN-01/{source.source_id}" for source in payload.sources
    )


def test_changed_authority_and_web_snapshot_fail_closed(tmp_path: Path) -> None:
    manifest = json.loads(MANIFEST.read_text())
    manifest["training_authorized"] = True
    changed = tmp_path / "manifest.json"
    changed.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        compile_source_plan(changed)
    manifest = json.loads(MANIFEST.read_text())
    manifest["sources"][3]["revision"] = "latest"
    changed.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        compile_source_plan(changed)


def test_ambiguous_json_fails_closed(tmp_path: Path) -> None:
    changed = tmp_path / "manifest.json"
    for invalid in ('{"x": 1, "x": 2}', '{"x": NaN}'):
        changed.write_text(invalid)
        with pytest.raises(ValueError):
            compile_source_plan(changed)


def test_contract_is_strict_frozen_and_uuid7() -> None:
    receipt = compile_source_plan(MANIFEST)
    assert receipt.receipt_id.version == 7
    changed = receipt.model_dump(mode="json") | {"unexpected": True}
    with pytest.raises(ValidationError):
        SourceAcquisitionDryRun.model_validate(changed)
    with pytest.raises(ValidationError):
        receipt.semantic_sha256 = "0" * 64  # type: ignore[misc]
