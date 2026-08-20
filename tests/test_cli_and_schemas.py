from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from uuid6 import uuid7

import bsl.interfaces.cli as cli
from bsl.contracts.archive import (
    ArchiveObjectPromotionReceipt,
    ArchivePreflightReceipt,
    ArchiveReadiness,
)
from bsl.contracts.source_admission import SourceAcquisitionDryRun
from bsl.interfaces.cli import main

ROOT = Path(__file__).parents[1]
SCHEMAS = (
    (ROOT / "contracts/json-schema/archive/archive-preflight-receipt.schema.json", ArchivePreflightReceipt),
    (
        ROOT / "contracts/json-schema/archive/archive-object-promotion-receipt.schema.json",
        ArchiveObjectPromotionReceipt,
    ),
    (ROOT / "contracts/json-schema/acquisition/source-acquisition-dry-run.schema.json", SourceAcquisitionDryRun),
)


def pretty_json(value: object, level: int = 0, *, expand: bool = False) -> str:
    indent = "  " * level
    child_indent = "  " * (level + 1)
    if isinstance(value, dict):
        if not value:
            return "{}"
        inline = json.dumps(value, sort_keys=True, separators=(", ", ": "))
        if not expand and len(indent + inline) <= 120:
            return inline
        entries = []
        for key, item in sorted(value.items()):
            prefix = f"{child_indent}{json.dumps(key)}: "
            rendered = pretty_json(item, level + 1)
            if "\n" not in rendered and len(prefix + rendered) > 120:
                rendered = pretty_json(item, level + 1, expand=True)
            entries.append(prefix + rendered)
        return "{\n" + ",\n".join(entries) + f"\n{indent}}}"
    if isinstance(value, list):
        inline = json.dumps(value, separators=(", ", ": "))
        if not expand and all(not isinstance(item, (dict, list)) for item in value) and len(indent + inline) <= 120:
            return inline
        entries = [f"{child_indent}{pretty_json(item, level + 1)}" for item in value]
        return "[\n" + ",\n".join(entries) + f"\n{indent}]"
    return json.dumps(value)


def schema_bytes(
    model: type[ArchivePreflightReceipt] | type[ArchiveObjectPromotionReceipt] | type[SourceAcquisitionDryRun],
) -> bytes:
    return (pretty_json(model.model_json_schema(by_alias=False)) + "\n").encode()


def test_schema_generation_has_no_drift_and_registry_hashes_match() -> None:
    for path, model in SCHEMAS:
        assert path.read_bytes() == schema_bytes(model)
    registry = json.loads((ROOT / "contracts/registry.json").read_text())
    names = ["ArchivePreflightReceipt", "ArchiveObjectPromotionReceipt", "SourceAcquisitionDryRun"]
    assert [entry["contract"] for entry in registry["contracts"]] == names
    for entry in registry["contracts"]:
        path = ROOT / entry["schema_path"]
        assert entry["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()


def test_cli_plan_and_invalid_input_are_machine_readable(capsys) -> None:
    manifest = ROOT / "design/approved/SOURCE-PLAN-01-source-admission-manifest.json"
    assert main(["source", "plan", "--manifest", str(manifest)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["contract"] == "SourceAcquisitionDryRun"
    assert len(output["semantic_payload"]["sources"]) == 6
    assert main(["archive", "inspect"]) == 2
    error = json.loads(capsys.readouterr().out)
    assert error["error"]["code"] == "INVALID_CLI_INPUT"


def test_cli_archive_persists_private_receipt_and_maps_exit_codes(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    def receipt(readiness: ArchiveReadiness) -> ArchivePreflightReceipt:
        return ArchivePreflightReceipt(
            receipt_id=uuid7(),
            generated_at=datetime.now(UTC),
            requested_volume_name="BSL-Archive",
            readiness=readiness,
            reasons=(),
            candidate_count=0,
            candidate=None,
        )

    monkeypatch.setattr(cli, "inspect_volume", lambda _name: receipt(ArchiveReadiness.VOLUME_NOT_FOUND))
    assert main(["archive", "inspect", "--volume-name", "BSL-Archive"]) == 0
    private = tmp_path / ".local/evidence/VS01-T01/archive-preflight.json"
    assert json.loads(private.read_text())["contract"] == "ArchivePreflightReceipt"
    assert json.loads(capsys.readouterr().out)["readiness"] == "VOLUME_NOT_FOUND"
    monkeypatch.setattr(cli, "inspect_volume", lambda _name: receipt(ArchiveReadiness.UNSUPPORTED_HOST))
    assert main(["archive", "inspect", "--volume-name", "BSL-Archive"]) == 1
    capsys.readouterr()
    assert main(["source", "plan", "--manifest", "missing.json"]) == 2
    assert json.loads(capsys.readouterr().out)["error"]["code"] == "OPERATION_FAILED"
