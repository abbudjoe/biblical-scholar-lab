from __future__ import annotations

import hashlib
import json
import socket
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from bsl.application.source_admission import compile_source_plan, semantic_bytes
from bsl.contracts.source_admission import APPROVED_SOURCE_IDS, HARD_PROHIBITIONS, SourceAcquisitionDryRun

MANIFEST = Path("design/approved/SOURCE-PLAN-01-source-admission-manifest.json")


def _data() -> dict:
    return json.loads(compile_source_plan(MANIFEST).model_dump_json())


def _reject(data: dict) -> None:
    with pytest.raises(ValidationError):
        SourceAcquisitionDryRun.model_validate_json(json.dumps(data))


def test_exact_six_source_plan_is_deterministic(monkeypatch: pytest.MonkeyPatch) -> None:
    def blocked(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("external network access attempted")

    monkeypatch.setattr(socket.socket, "connect", blocked)
    first, second = compile_source_plan(MANIFEST), compile_source_plan(MANIFEST)
    assert (first.receipt_id, first.generated_at) != (second.receipt_id, second.generated_at)
    assert semantic_bytes(first) == semantic_bytes(second)
    assert first.semantic_sha256 == second.semantic_sha256 == hashlib.sha256(semantic_bytes(first)).hexdigest()
    assert SourceAcquisitionDryRun.model_validate_json(first.model_dump_json()) == first
    payload = first.semantic_payload
    assert tuple(source.source_id for source in payload.sources) == APPROVED_SOURCE_IDS
    assert payload.hard_prohibitions == HARD_PROHIBITIONS
    assert payload.sources[3].revision == "ACQUISITION_TIMESTAMP_PLUS_SHA256_REQUIRED"
    assert (payload.sources[1].admitted_fields[-1], payload.sources[1].excluded_fields[-1]) == ("lemma", "word_senses")
    assert payload.sources[5].normalized_scope == ()


@pytest.mark.parametrize("case", ["duplicate", "missing", "extra", "reordered"])
def test_source_set_tampering_fails(case: str) -> None:
    data = _data()
    sources = data["semantic_payload"]["sources"]
    if case == "duplicate":
        sources[1] = dict(sources[0])
    elif case == "missing":
        sources.pop()
    elif case == "extra":
        sources.append(dict(sources[-1]))
    else:
        sources[0], sources[1] = sources[1], sources[0]
    _reject(data)


@pytest.mark.parametrize("case", ["modified", "reordered", "missing", "extra"])
def test_prohibition_tampering_fails(case: str) -> None:
    data = _data()
    prohibitions = data["semantic_payload"]["hard_prohibitions"]
    if case == "modified":
        prohibitions[0] = "changed"
    elif case == "reordered":
        prohibitions[0], prohibitions[1] = prohibitions[1], prohibitions[0]
    elif case == "missing":
        prohibitions.pop()
    else:
        prohibitions.append("additional prohibition")
    _reject(data)


@pytest.mark.parametrize("field", ["planned_manifest_identity", "relative_quarantine_plan"])
def test_planned_identity_and_quarantine_tampering_fails(field: str) -> None:
    data = _data()
    data["semantic_payload"]["sources"][0][field] = "0" * 64 if field.endswith("identity") else "quarantine/wrong"
    _reject(data)


def test_envelope_hash_uuid_and_extra_field_tampering_fails() -> None:
    for field, value in (
        ("semantic_sha256", "0" * 64),
        ("receipt_id", str(uuid4())),
        ("unexpected", True),
    ):
        data = _data()
        data[field] = value
        _reject(data)
    receipt = compile_source_plan(MANIFEST)
    with pytest.raises(ValidationError):
        receipt.semantic_sha256 = "0" * 64  # type: ignore[misc]


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
