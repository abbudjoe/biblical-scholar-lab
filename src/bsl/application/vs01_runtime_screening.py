from __future__ import annotations

import hashlib
import stat
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from uuid import UUID

import rfc8785
from pydantic import ValidationError
from uuid6 import uuid7

from bsl.application.john15_page_fixture import _fixture_assets, verify_t05_owner  # pyright: ignore[reportPrivateUsage]
from bsl.application.john15_study_runtime import (
    _answer,  # pyright: ignore[reportPrivateUsage]
    _authority_fingerprint,  # pyright: ignore[reportPrivateUsage]
    _verified_execution,  # pyright: ignore[reportPrivateUsage]
    load_t04_authority,
)
from bsl.application.vs01_benchmark import compile_subject_package, load_benchmark_authority
from bsl.application.vs01_runtime_reference import RuntimePairOutput, complete_runtime_pair
from bsl.contracts.benchmark import VS01BenchmarkExecutionReceipt, VS01BenchmarkRunResult
from bsl.contracts.runtime_screening import (
    ALTERNATIVE_IDS,
    BLOCK_IDS,
    CASE,
    CASE_IDENTITY,
    CITATION_IDS,
    CLAIM_IDS,
    EVENT_SEQUENCE,
    EVIDENCE_IDS,
    HARD_FAILURES,
    PROMPT,
    PUBLICATION_PATHS,
    SPEC,
    SPEC_IDENTITY,
    STATE_SEQUENCE,
    TOOL_NAMES,
    TOOL_PLAN,
    UNKNOWN_CLAIM_IDS,
    RuntimeAnswerBlock,
    RuntimeAuditEvent,
    RuntimeCitationRecord,
    RuntimeClaimRecord,
    RuntimeEvidenceRecord,
    RuntimeOperationCounters,
    RuntimeToolCallRecord,
    RuntimeToolDefinition,
    VS01B08RuntimePairSpecification,
    VS01RuntimeAcquisitionRun,
    canonical_sha256,
)
from bsl.infrastructure.page_fixture_store import verify_existing as verify_t06_existing

ROOT = Path(__file__).parents[3]
CANONICAL_ARCHIVE_ROOT = Path("/Volumes/BSL-Archive/BiblicalScholarLab")
T08_DESIGN = "design/approved/VS01-T08-full-runtime-evidence-acquisition-design.md"
T08_SPEC = "design/approved/VS01-T08-runtime-pair-spec.json"
T08_ACTIVATION = "activations/ACT-VS01-T08-FULL-RUNTIME-PAIR-v1.json"
T08_ACTIVATION_SIDECAR = "activations/ACT-VS01-T08-FULL-RUNTIME-PAIR-v1.sha256"
T08_FILES = {
    T08_DESIGN: "64cc1c740bc7454a97541301b32594c5f2577ec39287bb693592cf131c312d50",
    "design/approved/VS01-B08-RUNTIME-C01.json": "a7fc02da5ed8fda15ee29cba79cff8b037b2abc66352107f87165a0bfbea9f0f",
    T08_SPEC: "9e49e2f2b540a54c1d945991eb6500a52c0a7873136630d8bf49854efeb765ba",
    "design/approved/VS01-T08-design-manifest.json": "ac36bf7773d49c9938739b671131aecff46ed75065e3a85c9ed7e5ca41676544",
    "design/approved/VS01-T08-design-files.sha256": "e75a06e02793629ba1a415695e3e4ca8f8596059562f89fdab7af033989eb822",
    T08_ACTIVATION: "a42f0c8159ae84a56702db1cc9010f2e72f6e75f2284197c22104855050a6ce8",
    T08_ACTIVATION_SIDECAR: "ae204cd79c309300a20c03c085e953e0b1dec79ee6edba6b67997dbd8886ebe3",
}
T07_SNAPSHOT = "snapshots/benchmark/vs01-batch-01/reference-conformance.json"
T07_RECEIPT = "manifests/benchmark/vs01-batch-01/reference-conformance/benchmark-execution-receipt.json"
T07_RESULT_IDENTITY = "2f5838b85627c257d94436ff2aed94d2bf3528ed478b6ae2a3e2f81f7db9ae7f"
T07_RESULT_SHA256 = "32649b32eafeea121f6c0eea9aa43819863ed07a528577f2a40c2ff3847ee853"


@dataclass(frozen=True)
class CompiledRuntimeAuthority:
    pair_specification: VS01B08RuntimePairSpecification
    subject_projection: dict[str, Any]
    reference_run: VS01RuntimeAcquisitionRun
    scorer_plan: dict[str, Any]
    authority_fingerprints: tuple[tuple[str, str], ...]
    fixed_case_result_identity: str


def _read_regular_0444(path: Path) -> bytes:
    metadata = path.lstat()
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) != 0o444:
        raise ValueError(f"published runtime authority is unsafe: {path.name}")
    current = path
    while current != current.parent:
        if current.is_symlink():
            raise ValueError(f"published runtime authority has a symlink ancestor: {path.name}")
        current = current.parent
    return path.read_bytes()


def _validate_repo_authority() -> None:
    for relative, expected in T08_FILES.items():
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != expected:
            raise ValueError(f"committed T08 authority hash differs: {Path(relative).name}")
    case = dict(CASE)
    spec = dict(SPEC)
    case_identity = case.pop("case_content_sha256")
    spec_identity = spec.pop("spec_identity")
    if (case_identity, canonical_sha256(case), spec_identity, canonical_sha256(spec)) != (
        CASE_IDENTITY,
        CASE_IDENTITY,
        SPEC_IDENTITY,
        SPEC_IDENTITY,
    ):
        raise ValueError("committed T08 semantic identity differs")


def _load_t07(root: Path) -> tuple[VS01BenchmarkRunResult, VS01BenchmarkExecutionReceipt, str]:
    result_bytes = _read_regular_0444(root / T07_SNAPSHOT)
    receipt_bytes = _read_regular_0444(root / T07_RECEIPT)
    if hashlib.sha256(result_bytes).hexdigest() != T07_RESULT_SHA256:
        raise ValueError("published T07 result file hash differs")
    try:
        result = VS01BenchmarkRunResult.model_validate_json(result_bytes)
        receipt = VS01BenchmarkExecutionReceipt.model_validate_json(receipt_bytes)
    except ValidationError:
        raise ValueError("published T07 result or receipt is invalid") from None
    object_path = root / receipt.archive_paths[0]
    object_bytes = _read_regular_0444(object_path)
    expected = (
        object_bytes == result_bytes,
        result.run_result_identity == receipt.run_result_identity == T07_RESULT_IDENTITY,
        receipt.run_result_file_sha256 == T07_RESULT_SHA256,
        str(receipt.receipt_id) == "01a03a85-e49b-7d1c-b737-b560fd9a17df",
        receipt.disposition == result.disposition == "REFERENCE_CONFORMANT",
        receipt.published is True,
    )
    if not all(expected):
        raise ValueError("published T07 authority bindings differ")
    return result, receipt, hashlib.sha256(receipt_bytes).hexdigest()


def _json_schema(value: Any, *, constants: bool) -> dict[str, Any]:
    if isinstance(value, dict):
        mapping = cast(dict[str, Any], value)
        properties = {key: _json_schema(item, constants=constants) for key, item in mapping.items()}
        return {"type": "object", "properties": properties, "required": list(mapping), "additionalProperties": False}
    if isinstance(value, list):
        items = cast(list[Any], value)
        return {
            "type": "array",
            "prefixItems": [_json_schema(item, constants=constants) for item in items],
            "minItems": len(items),
            "maxItems": len(items),
        }
    if constants:
        return {"const": value}
    return {"type": "boolean" if isinstance(value, bool) else "integer" if isinstance(value, int) else "string"}


def _tool_definitions() -> tuple[RuntimeToolDefinition, ...]:
    return tuple(
        RuntimeToolDefinition(
            name=item["tool"],
            input_schema_json=rfc8785.dumps(_json_schema(item["input"], constants=True)).decode(),
            output_schema_json=rfc8785.dumps(_json_schema(item["expected_output"], constants=False)).decode(),
        )
        for item in TOOL_PLAN
    )


def _upstream_bindings() -> tuple[tuple[str, str], ...]:
    values: list[tuple[str, str]] = []
    for task in ("t04", "t05", "t06", "t07"):
        for name, value in SPEC["upstream_authorities"][task].items():
            if isinstance(value, (str, int)) or value is None:
                values.append((f"{task}.{name}", "null" if value is None else str(value)))
    return tuple(values)


def compile_pair_specification() -> VS01B08RuntimePairSpecification:
    fixed = SPEC["scoring"]["fixed_case"]["criteria"]
    runtime = SPEC["scoring"]["runtime_case"]["criteria"]
    thresholds = SPEC["scoring"]["future_screening_gate"]
    return VS01B08RuntimePairSpecification(
        pair_id=CASE["pair_id"],
        prompt=PROMPT,
        fixed_case_id="VS01-B08-C01",
        fixed_case_content_sha256=CASE["paired_fixed_case"]["case_content_sha256"],
        fixed_reference_score=(8, 8),
        runtime_case_id=CASE["case_id"],
        runtime_case_content_sha256=CASE_IDENTITY,
        upstream_authority=_upstream_bindings(),
        initial_evidence_ids=("EV-T08-INITIAL-ASV", "EV-T08-INITIAL-WEB"),
        tool_definitions=_tool_definitions(),
        required_evidence_ids=EVIDENCE_IDS,
        required_claim_ids=CLAIM_IDS,
        required_citation_ids=CITATION_IDS,
        required_alternative_ids=ALTERNATIVE_IDS,
        material_unknown_claim_ids=UNKNOWN_CLAIM_IDS,
        required_block_ids=BLOCK_IDS,
        required_state_sequence=STATE_SEQUENCE,
        required_event_sequence=EVENT_SEQUENCE,
        fixed_criteria=tuple((item["criterion_id"], item["weight"]) for item in fixed),
        runtime_criteria=tuple((item["criterion_id"], item["weight"]) for item in runtime),
        required_counts=(
            ("evidence", 12),
            ("claims", 15),
            ("citations", 10),
            ("blocks", 7),
            ("states", 15),
            ("events", 17),
        ),
        future_thresholds=(
            ("fixed", thresholds["fixed_minimum"]),
            ("runtime", thresholds["runtime_minimum"]),
            ("pair", thresholds["pair_minimum"]),
        ),
        hard_failures=HARD_FAILURES,
        allowed_dispositions=(
            "REFERENCE_CONFORMANT",
            "RUNTIME_SCREENING_PASS_WITH_EXPLICIT_LIMITATIONS",
            "RUNTIME_SCREENING_NO_GO",
        ),
        publication_paths=PUBLICATION_PATHS,
        specification_identity=SPEC_IDENTITY,
    )


def _subject_projection(pair: VS01B08RuntimePairSpecification) -> dict[str, Any]:
    visible = CASE["initial_evidence_contract"]["visible_evidence"]
    tools = sorted(pair.tool_definitions, key=lambda item: item.name)
    return {
        "schema_version": "1.0",
        "projection_id": "VS01-T08-RUNTIME-SUBJECT-PROJECTION-v1",
        "case_id": pair.runtime_case_id,
        "prompt": pair.prompt,
        "initial_evidence": visible,
        "tool_schemas": [item.model_dump(mode="json") for item in tools],
        "budgets": {"calls_per_tool": 1, "retries": 0, "fallbacks": 0},
        "output_schema": {"structured_acquisition_run": True, "answer_blocks": 7},
    }


def _tool_calls() -> tuple[RuntimeToolCallRecord, ...]:
    records: list[RuntimeToolCallRecord] = []
    for item in TOOL_PLAN:
        input_json = rfc8785.dumps(item["input"]).decode()
        output_json = rfc8785.dumps(item["expected_output"]).decode()
        records.append(
            RuntimeToolCallRecord(
                sequence=item["sequence"],
                tool_call_id=item["tool_call_id"],
                tool=item["tool"],
                input_json=input_json,
                output_json=output_json,
                input_sha256=canonical_sha256(item["input"]),
                output_sha256=canonical_sha256(item["expected_output"]),
            )
        )
    return tuple(records)


def _evidence(packet: Any) -> tuple[RuntimeEvidenceRecord, ...]:
    acquisition = dict.fromkeys(("EV-T04-ASV-001", "EV-T04-WEB-001"), "INITIAL_VISIBLE")
    acquisition |= {"EV-T04-GRK-001": TOOL_NAMES[2], "EV-T04-MORPH-001": TOOL_NAMES[3]}
    acquisition |= dict.fromkeys(
        ("EV-T04-LEX-000", "EV-T04-LEX-001", "EV-T04-LEX-002", "EV-T04-LEX-003"), TOOL_NAMES[4]
    )
    acquisition |= dict.fromkeys(
        ("EV-T04-NORM-001", "EV-T04-METHOD-001", "EV-T04-METHOD-002", "EV-T04-BOUNDARY-001"),
        TOOL_NAMES[5],
    )
    by_id = {item["evidence_id"]: item for item in packet.evidence_items}
    return tuple(
        RuntimeEvidenceRecord(
            evidence_id=item,
            source_handle=by_id[item].get("source_id") or by_id[item]["selector"],
            source_role=by_id[item]["source_role"],
            selector=by_id[item]["selector"],
            exact_excerpt=by_id[item].get("exact_excerpt"),
            acquired_by=acquisition[item],
        )
        for item in EVIDENCE_IDS
    )


def _claims(packet: Any) -> tuple[RuntimeClaimRecord, ...]:
    by_id = {item["claim_id"]: item for item in packet.claims}
    links: dict[str, list[str]] = {item: [] for item in CLAIM_IDS}
    for link in packet.claim_evidence_links:
        if link["claim_id"] in links:
            links[link["claim_id"]].append(link["evidence_id"])
    return tuple(
        RuntimeClaimRecord(
            claim_id=item,
            proposition=by_id[item]["proposition"],
            epistemic_status=by_id[item]["epistemic_status"],
            evidence_ids=tuple(links[item]),
            required_qualifications=tuple(by_id[item]["required_qualifications"]),
        )
        for item in CLAIM_IDS
    )


def _citations_and_blocks(
    execution: Any, study: Any
) -> tuple[tuple[RuntimeCitationRecord, ...], tuple[RuntimeAnswerBlock, ...]]:
    citations = tuple(
        RuntimeCitationRecord(
            citation_id=item["citation_id"],
            evidence_id=item["evidence_id"],
            selector=item["selector"],
            quoted_span=item["quoted_span"],
        )
        for item in execution.citation_ledger
    )
    blocks = tuple(
        RuntimeAnswerBlock(
            block_id=item["block_id"],
            heading=item["heading"],
            text=item["text"],
            claim_ids=tuple(item["claim_ids"]),
            citation_ids=tuple(item["citation_ids"]),
            alternative_ids=tuple(item.get("alternative_ids", ())),
        )
        for item in study.blocks
    )
    return citations, blocks


def _events() -> tuple[RuntimeAuditEvent, ...]:
    previous: str | None = None
    records: list[RuntimeAuditEvent] = []
    refs = (
        "request",
        "initial-evidence",
        "assessment",
        "plan",
        *(item["tool_call_id"] for item in TOOL_PLAN[1:]),
        "sufficiency",
        "claim-ledger",
        "answer",
        "verification",
        "rendering",
        "audit",
        "run",
    )
    for sequence, (event, artifact) in enumerate(zip(EVENT_SEQUENCE, refs, strict=True), 1):
        payload = {"sequence": sequence, "event": event, "artifact_ref": artifact, "previous_event_sha256": previous}
        record = RuntimeAuditEvent(
            sequence=sequence,
            event=event,
            artifact_ref=artifact,
            previous_event_sha256=previous,
            event_semantic_sha256=canonical_sha256(payload),
        )
        records.append(record)
        previous = record.event_semantic_sha256
    return tuple(records)


def compile_reference_run(pair: VS01B08RuntimePairSpecification, t04: Any) -> VS01RuntimeAcquisitionRun:
    _request, execution = _verified_execution(t04)
    study = _answer(execution, "STUDY")
    if (execution.execution_record_identity, study.answer_identity) != (
        SPEC["upstream_authorities"]["t05"]["execution_record_identity"],
        SPEC["upstream_authorities"]["t05"]["study_answer_identity"],
    ):
        raise ValueError("T05 Study answer authority differs")
    citations, blocks = _citations_and_blocks(execution, study)
    payload: dict[str, Any] = {
        "pair_specification_identity": pair.specification_identity,
        "case_id": pair.runtime_case_id,
        "prompt": pair.prompt,
        "request_revision": 1,
        "supersedes_run_identity": None,
        "initial_assessment": "INSUFFICIENT_FOR_REQUESTED_GREEK_AND_TEXTUAL_CRITICAL_CLAIMS",
        "tool_calls": _tool_calls(),
        "evidence_ledger": _evidence(t04.packet),
        "claim_ledger": _claims(t04.packet),
        "citation_ledger": citations,
        "answer_blocks": blocks,
        "accepted_alternative_ids": ALTERNATIVE_IDS,
        "material_unknown_claim_ids": UNKNOWN_CLAIM_IDS,
        "final_sufficiency": "SUFFICIENT_WITH_QUALIFICATION",
        "state_sequence": STATE_SEQUENCE,
        "audit_events": _events(),
        "operation_counters": RuntimeOperationCounters(
            packet_loads=1,
            raw_source_reads=0,
            t03_reads=0,
            model_invocations=0,
            ocr_invocations=0,
            vlm_invocations=0,
            network_invocations=0,
            database_writes=0,
            archive_writes=0,
        ),
    }
    payload["acquisition_run_identity"] = canonical_sha256(
        VS01RuntimeAcquisitionRun.model_construct(**payload, acquisition_run_identity="0" * 64).model_dump(
            mode="json", exclude={"acquisition_run_identity"}
        )
    )
    return VS01RuntimeAcquisitionRun.model_validate(payload)


def _scorer_plan(pair: VS01B08RuntimePairSpecification) -> dict[str, Any]:
    return {
        "scorer_id": "VS01-T08-STRUCTURED-CONFORMANCE-SCORER-v1",
        "pair_specification_identity": pair.specification_identity,
        "fixed_criteria": pair.fixed_criteria,
        "runtime_criteria": pair.runtime_criteria,
        "required_counts": pair.required_counts,
        "hard_failures": pair.hard_failures,
        "future_thresholds": pair.future_thresholds,
        "free_form_judge": False,
    }


def compile_runtime_authority(
    archive_root: Path = CANONICAL_ARCHIVE_ROOT,
    *,
    _t05_verifier: Callable[[Any], dict[str, Any]] = verify_t05_owner,
) -> CompiledRuntimeAuthority:
    _validate_repo_authority()
    pair = compile_pair_specification()
    fixed = load_benchmark_authority()[7]
    fixed_package = compile_subject_package(fixed)
    if fixed.source["prompt"] != PROMPT or fixed_package.whitelisted_source_handles != (
        "SP01-SRC-003#John.1.5",
        "SP01-SRC-004#John.1.5",
    ):
        raise ValueError("fixed B08 prompt or translations-only firewall differs")
    t04 = load_t04_authority(archive_root)
    t05 = _t05_verifier(t04)
    fixture, base, degraded, fixture_bytes = _fixture_assets()
    t06 = verify_t06_existing(archive_root, fixture, base, degraded, fixture_bytes)
    if t06 is None or str(t06.receipt_identity) != "01a034c2-d6e4-73f4-91b2-7410e7453783":
        raise ValueError("published T06 authority differs")
    t07, receipt, receipt_sha = _load_t07(archive_root)
    b08 = t07.case_results[7]
    if (b08.case_id, b08.capped_points, b08.raw_points, b08.case_disposition) != (
        "VS01-B08-C01",
        8,
        8,
        "REFERENCE_CONFORMANT",
    ):
        raise ValueError("published T07 fixed B08 result differs")
    run = compile_reference_run(pair, t04)
    projection = _subject_projection(pair)
    fingerprints = (
        ("t04", _authority_fingerprint(t04)),
        ("t05", canonical_sha256(t05)),
        ("t06", canonical_sha256(t06.model_dump(mode="json"))),
        ("t07", canonical_sha256((t07.run_result_identity, str(receipt.receipt_id), receipt_sha))),
    )
    return CompiledRuntimeAuthority(
        pair,
        projection,
        run,
        _scorer_plan(pair),
        fingerprints,
        b08.case_result_identity,
    )


def generated_fixture_bytes(authority: CompiledRuntimeAuthority) -> tuple[bytes, bytes]:
    projection = rfc8785.dumps(authority.subject_projection) + b"\n"
    run = rfc8785.dumps(authority.reference_run.model_dump(mode="json")) + b"\n"
    return projection, run


def run_runtime_pair(
    *,
    dry_run: bool,
    archive_root: Path = CANONICAL_ARCHIVE_ROOT,
    _implementation_commit: str | None = None,
    _new_uuid: Callable[[], UUID] | None = None,
    _now: Callable[[], datetime] | None = None,
) -> RuntimePairOutput:
    authority = compile_runtime_authority(archive_root)
    return complete_runtime_pair(
        authority.pair_specification,
        authority.subject_projection,
        authority.reference_run,
        authority.fixed_case_result_identity,
        authority.authority_fingerprints,
        archive_root,
        dry_run=dry_run,
        implementation_commit=_implementation_commit,
        new_uuid=_new_uuid or uuid7,
        now=_now or (lambda: datetime.now(UTC)),
    )
