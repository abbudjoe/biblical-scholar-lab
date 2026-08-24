from __future__ import annotations

import copy
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import BaseModel
from uuid6 import uuid7

import bsl.application.john15_study_runtime as study_runtime
import bsl.contracts.runtime as runtime_contracts
import bsl.interfaces.cli as cli
from bsl.contracts.archive import (
    ApprovedArchiveProfile,
    ArchiveInitializationReceipt,
    ArchiveObjectPromotionReceipt,
    ArchivePreflightReceipt,
    ArchiveReadiness,
    ArchiveRootMarker,
)
from bsl.contracts.evidence import (
    John15TranslationNuanceEvidencePacket,
    John15TranslationNuanceEvidenceReceipt,
)
from bsl.contracts.normalization import John15NormalizationBundle, NormalizationReceipt
from bsl.contracts.page_fixture import (
    John15PageExtractionGroundTruth,
    John15PageRegionGroundTruth,
    John15SyntheticPageFixture,
    John15SyntheticPagePublicationReceipt,
)
from bsl.contracts.runtime import (
    John15RuntimeAuditReceipt,
    John15StudyAnswerArtifact,
    John15StudyExecutionRecord,
    John15StudyRequest,
)
from bsl.contracts.source_admission import AdmissionDecision, FetchReceipt, SourceAcquisitionDryRun, SourceSnapshot
from bsl.interfaces.cli import main

ROOT = Path(__file__).parents[1]
SCHEMAS = (
    (ROOT / "contracts/json-schema/archive/archive-preflight-receipt.schema.json", ArchivePreflightReceipt),
    (
        ROOT / "contracts/json-schema/archive/archive-object-promotion-receipt.schema.json",
        ArchiveObjectPromotionReceipt,
    ),
    (ROOT / "contracts/json-schema/acquisition/source-acquisition-dry-run.schema.json", SourceAcquisitionDryRun),
    (ROOT / "contracts/json-schema/archive/approved-archive-profile.schema.json", ApprovedArchiveProfile),
    (ROOT / "contracts/json-schema/archive/archive-root-marker.schema.json", ArchiveRootMarker),
    (
        ROOT / "contracts/json-schema/archive/archive-initialization-receipt.schema.json",
        ArchiveInitializationReceipt,
    ),
    (ROOT / "contracts/json-schema/acquisition/fetch-receipt.schema.json", FetchReceipt),
    (ROOT / "contracts/json-schema/acquisition/source-snapshot.schema.json", SourceSnapshot),
    (ROOT / "contracts/json-schema/acquisition/admission-decision.schema.json", AdmissionDecision),
    (
        ROOT / "contracts/json-schema/normalization/john-15-normalization-bundle.schema.json",
        John15NormalizationBundle,
    ),
    (ROOT / "contracts/json-schema/normalization/normalization-receipt.schema.json", NormalizationReceipt),
    (
        ROOT / "contracts/json-schema/evidence/john-15-translation-nuance-evidence-packet.schema.json",
        John15TranslationNuanceEvidencePacket,
    ),
    (
        ROOT / "contracts/json-schema/evidence/john-15-translation-nuance-evidence-receipt.schema.json",
        John15TranslationNuanceEvidenceReceipt,
    ),
    (ROOT / "contracts/json-schema/runtime/john-15-study-request.schema.json", John15StudyRequest),
    (
        ROOT / "contracts/json-schema/runtime/john-15-study-execution-record.schema.json",
        John15StudyExecutionRecord,
    ),
    (
        ROOT / "contracts/json-schema/runtime/john-15-study-answer-artifact.schema.json",
        John15StudyAnswerArtifact,
    ),
    (
        ROOT / "contracts/json-schema/runtime/john-15-runtime-audit-receipt.schema.json",
        John15RuntimeAuditReceipt,
    ),
    (
        ROOT / "contracts/json-schema/page/john-15-synthetic-page-fixture.schema.json",
        John15SyntheticPageFixture,
    ),
    (
        ROOT / "contracts/json-schema/page/john-15-page-region-ground-truth.schema.json",
        John15PageRegionGroundTruth,
    ),
    (
        ROOT / "contracts/json-schema/page/john-15-page-extraction-ground-truth.schema.json",
        John15PageExtractionGroundTruth,
    ),
    (
        ROOT / "contracts/json-schema/page/john-15-synthetic-page-publication-receipt.schema.json",
        John15SyntheticPagePublicationReceipt,
    ),
)


def schema_bytes(model: type[BaseModel]) -> bytes:
    rendered = json.dumps(model.model_json_schema(by_alias=False), indent=2, sort_keys=True)
    return f"{rendered}\n".encode()


def test_schema_generation_has_no_drift_and_registry_hashes_match() -> None:
    for path, model in SCHEMAS:
        assert path.read_bytes() == schema_bytes(model)
    registry = json.loads((ROOT / "contracts/registry.json").read_text())
    names = [model.__name__ for _path, model in SCHEMAS]
    assert [entry["contract"] for entry in registry["contracts"]] == names
    for entry in registry["contracts"]:
        path = ROOT / entry["schema_path"]
        assert entry["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize("case", ("claim", "cognitive", "receipt", "source", "packet"))
def test_evidence_packet_schema_rejects_frozen_mutations(tmp_path: Path, case: str) -> None:
    jsonschema = pytest.importorskip("jsonschema", reason="Draft 2020-12 validator is an external validation tool")
    from test_evidence_packet import _packet

    path = ROOT / "contracts/json-schema/evidence/john-15-translation-nuance-evidence-packet.schema.json"
    validator = jsonschema.Draft202012Validator(json.loads(path.read_text()), format_checker=jsonschema.FormatChecker())
    data = copy.deepcopy(_packet(tmp_path).model_dump(mode="json"))
    if case == "claim":
        data["claims"][0]["proposition"] = "changed"
    elif case == "cognitive":
        data["accepted_alternatives"][0]["epistemic_status"] = "DIRECTLY_ATTESTED"
    elif case == "receipt":
        data["input_authority"]["normalization_receipt_identity"] = "01900000-0000-7000-8000-000000000000"
    elif case == "source":
        data["input_authority"]["source_snapshot_identities"].reverse()
    else:
        data["packet_identity"] = "0" * 64
    assert not validator.is_valid(data)


@pytest.mark.parametrize("case", ("request", "execution", "brief", "study"))
def test_runtime_schemas_reject_frozen_mutations(case: str) -> None:
    jsonschema = pytest.importorskip("jsonschema", reason="Draft 2020-12 validator is an external validation tool")
    values = {
        "request": runtime_contracts._request_payload(2),  # pyright: ignore[reportPrivateUsage]
        "execution": runtime_contracts._execution_payload(),  # pyright: ignore[reportPrivateUsage]
        "brief": runtime_contracts._answer_payload("BRIEF"),  # pyright: ignore[reportPrivateUsage]
        "study": runtime_contracts._answer_payload("STUDY"),  # pyright: ignore[reportPrivateUsage]
    }
    names = {
        "request": "john-15-study-request.schema.json",
        "execution": "john-15-study-execution-record.schema.json",
        "brief": "john-15-study-answer-artifact.schema.json",
        "study": "john-15-study-answer-artifact.schema.json",
    }
    value = copy.deepcopy(values[case])
    if case == "request":
        value["exact_user_text"] = "changed"
    elif case == "execution":
        value["claim_ledger"][12]["epistemic_status"] = "DIRECTLY_ATTESTED"
    else:
        value["markdown"] = "changed"
    schema = json.loads((ROOT / "contracts/json-schema/runtime" / names[case]).read_text())
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    assert not validator.is_valid(value)


def test_audit_schema_has_typed_operations_and_no_open_count_objects() -> None:
    schema = John15RuntimeAuditReceipt.model_json_schema()
    assert schema["additionalProperties"] is False
    assert schema["properties"]["receipt_identity"]["format"] == "uuid"
    assert schema["properties"]["generated_at"]["format"] == "date-time"
    assert schema["properties"]["latency_ms"]["type"] == "integer"
    for field in ("database_rows_written", "database_rows_verified"):
        assert all("const" in choice for choice in schema["properties"][field]["oneOf"])


def test_workflow_binds_exact_pr_head_and_committed_diff() -> None:
    workflow = (ROOT / ".github/workflows/vs01-t01-ci.yml").read_text()
    assert "ref: ${{ github.event.pull_request.head.sha }}" in workflow
    assert "HEAD_SHA: ${{ github.event.pull_request.head.sha }}" in workflow
    assert "BASE_SHA: ${{ github.event.pull_request.base.sha }}" in workflow
    assert 'test "$(git rev-parse HEAD)" = "$HEAD_SHA"' in workflow
    assert 'git diff --check "${BASE_SHA}...${HEAD_SHA}"' in workflow
    assert "      - run: git diff --check\n" not in workflow


def test_t05_workflow_binds_exact_database_and_pr_head() -> None:
    workflow = (ROOT / ".github/workflows/vs01-t05-ci.yml").read_text()
    assert "postgres:18.6-bookworm@sha256:7d2695c3aa88e792e8b3b233e7e4adb296a20412c6c0ca361e3edaaacfada108" in workflow
    assert "postgresql://bsl_test:bsl_test@localhost:5432/bsl_test" in workflow
    assert "pg_isready -U bsl_test -d bsl_test" in workflow
    assert "SHOW server_version_num" in workflow
    assert "ref: ${{ github.event.pull_request.head.sha }}" in workflow
    assert "persist-credentials: false" in workflow


@pytest.mark.parametrize("render", ("brief", "study", "both"))
def test_study_cli_is_machine_readable_and_dry_run_never_exposes_database_url(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], render: str
) -> None:
    from test_study_runtime import _authority

    monkeypatch.setattr(study_runtime, "load_t04_authority", lambda *_args, **_kwargs: _authority(tmp_path))
    monkeypatch.setenv("BSL_DATABASE_URL", "postgresql://must-not-appear")
    code = main(
        [
            "study",
            "john-1-5-translation-nuance",
            "--archive-root",
            str(tmp_path),
            "--render",
            render,
            "--dry-run",
        ]
    )
    raw = capsys.readouterr().out
    output = json.loads(raw)
    assert code == 0 and "must-not-appear" not in raw
    assert output["audit_receipt"]["disposition"] == "DRY_RUN_VALIDATED"
    assert output["persisted"] is output["verified_existing"] is False
    assert (output["brief_answer"] is not None) == (render in {"brief", "both"})
    assert (output["study_answer"] is not None) == (render in {"study", "both"})


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
