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


def schema_bytes(
    model: type[ArchivePreflightReceipt] | type[ArchiveObjectPromotionReceipt] | type[SourceAcquisitionDryRun],
) -> bytes:
    rendered = json.dumps(model.model_json_schema(by_alias=False), indent=2, sort_keys=True)
    return f"{rendered}\n".encode()


def test_schema_generation_has_no_drift_and_registry_hashes_match() -> None:
    for path, model in SCHEMAS:
        assert path.read_bytes() == schema_bytes(model)
    registry = json.loads((ROOT / "contracts/registry.json").read_text())
    names = ["ArchivePreflightReceipt", "ArchiveObjectPromotionReceipt", "SourceAcquisitionDryRun"]
    assert [entry["contract"] for entry in registry["contracts"]] == names
    for entry in registry["contracts"]:
        path = ROOT / entry["schema_path"]
        assert entry["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()


def test_workflow_binds_exact_pr_head_and_committed_diff() -> None:
    workflow = (ROOT / ".github/workflows/vs01-t01-ci.yml").read_text()
    assert "ref: ${{ github.event.pull_request.head.sha }}" in workflow
    assert "HEAD_SHA: ${{ github.event.pull_request.head.sha }}" in workflow
    assert "BASE_SHA: ${{ github.event.pull_request.base.sha }}" in workflow
    assert 'test "$(git rev-parse HEAD)" = "$HEAD_SHA"' in workflow
    assert 'git diff --check "${BASE_SHA}...${HEAD_SHA}"' in workflow
    assert "      - run: git diff --check\n" not in workflow


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
        reasons = {
            ArchiveReadiness.VOLUME_NOT_FOUND: ("NO_EXACT_NAME_MATCH",),
            ArchiveReadiness.UNSUPPORTED_HOST: ("DARWIN_REQUIRED",),
        }[readiness]
        return ArchivePreflightReceipt(
            receipt_id=uuid7(),
            generated_at=datetime.now(UTC),
            requested_volume_name="BSL-Archive",
            readiness=readiness,
            reasons=reasons,
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
