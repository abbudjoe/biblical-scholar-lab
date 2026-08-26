from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, Literal, Self, cast
from uuid import UUID

import rfc8785
from pydantic import BaseModel, ConfigDict, Field, model_validator

Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
CommitSha = Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
ROOT = Path(__file__).parents[3]
CASE_PATH = ROOT / "design/approved/VS01-B08-RUNTIME-C01.json"
SPEC_PATH = ROOT / "design/approved/VS01-T08-runtime-pair-spec.json"
FIXTURE_PATH = ROOT / "fixtures/VS01-T08/reference-runtime-run.json"
CASE_FILE_SHA256 = "a7fc02da5ed8fda15ee29cba79cff8b037b2abc66352107f87165a0bfbea9f0f"
CASE_IDENTITY = "a1fdd253614df0ca7789a44372dabb895dcfda042656104ab68c9c6b351c17dd"
SPEC_FILE_SHA256 = "9e49e2f2b540a54c1d945991eb6500a52c0a7873136630d8bf49854efeb765ba"
SPEC_IDENTITY = "98c5df4b4906261cd96fa194ecf2035474633bdc9988388886c8b081e1835f51"
FIXED_CASE_RESULT_IDENTITY = "eb3ae952a7cb62911e259350ca847299b95f1661daf98be879c86f646ae1c880"
TOOL_SCHEMA_IDENTITY = "303b36c0a040dc0d3c27487b048569e321e51d742d1dfc51691e68a8fafb6695"
SYNTHETIC_CASE_ID = "SYN-VS01-B08-RUNTIME-C01"


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(rfc8785.dumps(value)).hexdigest()


def _authority(path: Path, file_sha: str, identity_name: str, identity: str) -> dict[str, Any]:
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != file_sha:
        raise ValueError(f"frozen runtime authority hash differs: {path.name}")
    value = cast(dict[str, Any], json.loads(data))
    claimed = value.pop(identity_name)
    if (claimed, canonical_sha256(value)) != (identity, identity):
        raise ValueError(f"frozen runtime authority identity differs: {path.name}")
    return value | {identity_name: claimed}


CASE = _authority(CASE_PATH, CASE_FILE_SHA256, "case_content_sha256", CASE_IDENTITY)
SPEC = _authority(SPEC_PATH, SPEC_FILE_SHA256, "spec_identity", SPEC_IDENTITY)
PROMPT = cast(str, CASE["prompt"])
CORRECTION_PROMPT = f"{PROMPT}\n[SYNTHETIC_CORRECTION] Emphasize the retained textual-state uncertainty."
CORRECTION_ANSWER_SENTENCE = (
    "Correction emphasis: apparatus and witness evidence remain absent, so the broader textual-critical state "
    "remains unknown."
)
TOOL_PLAN = cast(list[dict[str, Any]], CASE["tool_plan"])
TOOL_NAMES = tuple(cast(str, item["tool"]) for item in TOOL_PLAN)
EVIDENCE_IDS = tuple(cast(list[str], CASE["answer_contract"]["required_evidence_ids"]))
CLAIM_IDS = tuple(cast(list[str], CASE["answer_contract"]["required_claim_ids"]))
CITATION_IDS = tuple(cast(list[str], CASE["answer_contract"]["required_citation_ids"]))
ALTERNATIVE_IDS = tuple(cast(list[str], CASE["answer_contract"]["required_alternative_ids"]))
UNKNOWN_CLAIM_IDS = tuple(cast(list[str], CASE["answer_contract"]["material_uncertainty_claim_ids"]))
BLOCK_IDS = tuple(cast(str, item["block_id"]) for item in CASE["answer_contract"]["blocks"])
STATE_SEQUENCE = tuple(cast(list[str], CASE["runtime_state_sequence"]))
EVENT_SEQUENCE = tuple(cast(list[str], CASE["audit_event_sequence"]))
HARD_FAILURES = tuple(cast(list[str], SPEC["hard_failures"]))
LIMITATIONS = tuple(cast(list[str], SPEC["promotion_and_no_go"]["remaining_limitations"]))
INITIAL_EVIDENCE = tuple(cast(list[dict[str, Any]], CASE["initial_evidence_contract"]["visible_evidence"]))
PUBLICATION_PATHS = (
    "objects/sha256/<prefix>/<pair-result-sha256>",
    "snapshots/benchmark/vs01-b08-runtime-pair/reference-screening.json",
    "manifests/benchmark/vs01-b08-runtime-pair/reference-screening/runtime-screening-receipt.json",
    ".incoming/vs01-b08-runtime-pair-<pair-result-sha256>.runtime-screening-stage",
)
FINGERPRINT_NAMES = ("t04", "t05", "t06", "t07", "archive_root", "incoming_inventory")
FRESH_PUBLICATION_VERIFICATIONS = 2
VERIFIED_EXISTING_VERIFICATIONS = 1
_REFERENCE = cast(dict[str, Any], json.loads(FIXTURE_PATH.read_bytes()))
_LEDGER_FIELDS = ("evidence_ledger", "claim_ledger", "citation_ledger", "answer_blocks")
_LEDGER_HASHES = (
    "fb72d7cbd234f3be742b789de59093c204400b14b0ed888ba6a42d30b3a40645",
    "bcd68e48c4e3a895bfcea299f2a2165db093affceb30a34bfc08c1d7fbfd25d5",
    "1e0bdf98569221f5c1cb4ec58349264ef217db622ebb9295dfe392c15b291292",
    "8c4ccc54107dfa54c250cb1fe88cd9914d4d4b18b9332484d596584e6cdc5dbe",
)
for _field, _digest in zip(_LEDGER_FIELDS, _LEDGER_HASHES, strict=True):
    if canonical_sha256(_REFERENCE[_field]) != _digest:
        raise ValueError(f"reference runtime {_field} authority differs")


class StrictRecord(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")


class RuntimeToolDefinition(StrictRecord):
    name: str
    input_schema_json: str
    output_schema_json: str
    maximum_calls: Literal[1] = 1


class RuntimeToolCallRecord(StrictRecord):
    sequence: int = Field(ge=1)
    tool_call_id: str
    tool: str
    input_json: str
    output_json: str
    input_sha256: Sha256
    output_sha256: Sha256

    @model_validator(mode="after")
    def canonical_payloads(self) -> Self:
        for text, digest in ((self.input_json, self.input_sha256), (self.output_json, self.output_sha256)):
            value: Any = json.loads(text)
            if not isinstance(value, dict):
                raise ValueError("runtime tool-call payload is not a JSON object")
            mapping = cast(dict[str, Any], value)
            if rfc8785.dumps(mapping).decode() != text or canonical_sha256(mapping) != digest:
                raise ValueError("runtime tool-call payload is not canonical or hash-bound")
        return self


class RuntimeEvidenceRecord(StrictRecord):
    evidence_id: str
    source_handle: str
    source_role: str
    selector: str
    exact_excerpt: str | None
    acquired_by: str


class RuntimeClaimRecord(StrictRecord):
    claim_id: str
    proposition: str
    epistemic_status: str
    evidence_ids: tuple[str, ...]
    required_qualifications: tuple[str, ...]


class RuntimeCitationRecord(StrictRecord):
    citation_id: str
    evidence_id: str
    selector: str
    quoted_span: str | None


class RuntimeAnswerBlock(StrictRecord):
    block_id: str
    heading: str
    text: str
    claim_ids: tuple[str, ...]
    citation_ids: tuple[str, ...]
    alternative_ids: tuple[str, ...] = ()


class RuntimeCriterion(StrictRecord):
    criterion_id: str
    weight: int = Field(ge=1)
    score: int = Field(ge=0, le=2)
    points: int = Field(ge=0)

    @model_validator(mode="after")
    def arithmetic(self) -> Self:
        if self.points != self.score * self.weight:
            raise ValueError("runtime criterion arithmetic differs")
        return self


class RuntimeAuditEvent(StrictRecord):
    sequence: int = Field(ge=1)
    event: str
    artifact_ref: str
    previous_event_sha256: Sha256 | None
    event_semantic_sha256: Sha256

    @model_validator(mode="after")
    def semantic_hash(self) -> Self:
        payload = self.model_dump(mode="json", exclude={"event_semantic_sha256"})
        if self.event_semantic_sha256 != canonical_sha256(payload):
            raise ValueError("runtime audit event semantic hash differs")
        return self


class RuntimeOperationCounters(StrictRecord):
    packet_loads: int = Field(ge=0)
    raw_source_reads: int = Field(ge=0)
    t03_reads: int = Field(ge=0)
    model_invocations: int = Field(ge=0)
    ocr_invocations: int = Field(ge=0)
    vlm_invocations: int = Field(ge=0)
    network_invocations: int = Field(ge=0)
    database_writes: int = Field(ge=0)
    archive_writes: int = Field(ge=0)


class RuntimeControllerLedger(StrictRecord):
    subject_invocations: int = Field(ge=0)
    broker_tool_calls: int = Field(ge=0)
    scoring_invocations: int = Field(ge=0)
    acquisition_runs_constructed: int = Field(ge=0)
    pair_results_constructed: int = Field(ge=0)
    receipts_constructed: int = Field(ge=0)
    store_verification_attempts: int = Field(ge=0)
    publication_attempts: int = Field(ge=0)
    successful_publications: int = Field(ge=0)
    canonical_archive_writes: int = Field(ge=0)
    database_writes: int = Field(ge=0)
    t03_reads: int = Field(ge=0)
    raw_source_reads: int = Field(ge=0)
    model_invocations: int = Field(ge=0)
    ocr_invocations: int = Field(ge=0)
    vlm_invocations: int = Field(ge=0)
    network_invocations: int = Field(ge=0)
    cloud_invocations: int = Field(ge=0)


def expected_tool_calls(prompt: str) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = []
    for index, item in enumerate(TOOL_PLAN):
        inputs = dict(item["input"])
        if index == 0:
            inputs["prompt"] = prompt
        input_json, output_json = rfc8785.dumps(inputs).decode(), rfc8785.dumps(item["expected_output"]).decode()
        records.append(
            {
                "sequence": item["sequence"],
                "tool_call_id": item["tool_call_id"],
                "tool": item["tool"],
                "input_json": input_json,
                "output_json": output_json,
                "input_sha256": canonical_sha256(inputs),
                "output_sha256": canonical_sha256(item["expected_output"]),
            }
        )
    return tuple(records)


def request_identity(case_id: str, prompt: str, revision: int, supersedes: str | None) -> str:
    return canonical_sha256({"case_id": case_id, "prompt": prompt, "revision": revision, "supersedes": supersedes})


def plan_identity(request: str, calls: tuple[dict[str, Any], ...]) -> str:
    return canonical_sha256({"request_identity": request, "tool_calls": calls})


def answer_identity(request: str, ledger_hashes: tuple[str, ...] = _LEDGER_HASHES) -> str:
    return canonical_sha256({"request_identity": request, **dict(zip(_LEDGER_FIELDS, ledger_hashes, strict=True))})


def expected_events(request: str, plan: str, answer: str) -> tuple[dict[str, Any], ...]:
    refs = (
        request,
        _LEDGER_HASHES[0],
        request,
        plan,
        *(item["tool_call_id"] for item in TOOL_PLAN[1:6]),
        _LEDGER_HASHES[0],
        TOOL_PLAN[6]["tool_call_id"],
        _LEDGER_HASHES[1],
        answer,
        answer,
        answer,
        plan,
        plan,
    )
    previous: str | None = None
    records: list[dict[str, Any]] = []
    for sequence, (event, artifact) in enumerate(zip(EVENT_SEQUENCE, refs, strict=True), 1):
        payload = {"sequence": sequence, "event": event, "artifact_ref": artifact, "previous_event_sha256": previous}
        payload["event_semantic_sha256"] = canonical_sha256(payload)
        records.append(payload)
        previous = payload["event_semantic_sha256"]
    return tuple(records)


def acquisition_variant_payload(
    case_id: str,
    prompt: str,
    revision: int,
    supersedes_request: str | None,
    supersedes_run: str | None,
) -> dict[str, Any]:
    from bsl.application.vs01_runtime_reference import answer_blocks_for, ledger_hashes_for

    request = request_identity(case_id, prompt, revision, supersedes_request)
    calls = expected_tool_calls(prompt)
    blocks, hashes = answer_blocks_for(prompt), ledger_hashes_for(prompt)
    plan, answer = plan_identity(request, calls), answer_identity(request, hashes)
    payload = dict(_REFERENCE) | {
        "case_id": case_id,
        "prompt": prompt,
        "request_revision": revision,
        "request_identity": request,
        "supersedes_request_identity": supersedes_request,
        "supersedes_run_identity": supersedes_run,
        "plan_identity": plan,
        "tool_calls": calls,
        "answer_blocks": blocks,
        "audit_events": expected_events(request, plan, answer),
        "answer_projection_identity": answer,
    }
    payload.pop("acquisition_run_identity", None)
    payload["acquisition_run_identity"] = canonical_sha256(payload)
    return payload


def _upstream_constants() -> tuple[tuple[str, str], ...]:
    return tuple(
        (f"{task}.{name}", "null" if value is None else str(value))
        for task in ("t04", "t05", "t06", "t07")
        for name, value in SPEC["upstream_authorities"][task].items()
        if isinstance(value, (str, int)) or value is None
    )


def _spec_schema(schema: dict[str, Any]) -> None:
    from bsl.application.vs01_runtime_screening import specification_schema

    specification_schema(schema)


def _run_schema(schema: dict[str, Any]) -> None:
    from bsl.application.vs01_runtime_reference import acquisition_run_schema

    acquisition_run_schema(schema)


def _result_schema(schema: dict[str, Any]) -> None:
    from bsl.application.vs01_runtime_scoring import pair_result_schema

    pair_result_schema(schema)


def _receipt_schema(schema: dict[str, Any]) -> None:
    from bsl.application.vs01_runtime_scoring import screening_receipt_schema

    screening_receipt_schema(schema)


class VS01B08RuntimePairSpecification(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid", json_schema_extra=_spec_schema)
    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["VS01B08RuntimePairSpecification"] = "VS01B08RuntimePairSpecification"
    spec_id: Literal["VS01-T08-FULL-RUNTIME-PAIR-v1"] = "VS01-T08-FULL-RUNTIME-PAIR-v1"
    pair_id: str
    prompt: str
    fixed_case_id: str
    fixed_case_content_sha256: Sha256
    fixed_reference_score: tuple[Literal[8], Literal[8]]
    runtime_case_id: str
    runtime_case_content_sha256: Sha256
    upstream_authority: tuple[tuple[str, str], ...]
    initial_evidence_ids: tuple[str, str]
    tool_definitions: tuple[RuntimeToolDefinition, ...]
    required_evidence_ids: tuple[str, ...]
    required_claim_ids: tuple[str, ...]
    required_citation_ids: tuple[str, ...]
    required_alternative_ids: tuple[str, ...]
    material_unknown_claim_ids: tuple[str, ...]
    required_block_ids: tuple[str, ...]
    required_state_sequence: tuple[str, ...]
    required_event_sequence: tuple[str, ...]
    fixed_criteria: tuple[tuple[str, int], ...]
    runtime_criteria: tuple[tuple[str, int], ...]
    required_counts: tuple[tuple[str, int], ...]
    future_thresholds: tuple[tuple[str, int], ...]
    hard_failures: tuple[str, ...]
    allowed_dispositions: tuple[str, ...]
    publication_paths: tuple[str, str, str, str]
    specification_identity: Sha256

    @model_validator(mode="after")
    def exact_authority(self) -> Self:
        exact = (
            (self.pair_id, self.prompt, self.runtime_case_id, self.runtime_case_content_sha256)
            == ("BENCH-VS01-B08-PAIR-01", PROMPT, "VS01-B08-RUNTIME-C01", CASE_IDENTITY),
            (self.fixed_case_id, self.fixed_case_content_sha256, self.fixed_reference_score)
            == ("VS01-B08-C01", "28ebe4b02d19b316e027b2c68dce02114e7a40c1f050bba357a4b8cb43d5529a", (8, 8)),
            self.upstream_authority == _upstream_constants(),
            self.initial_evidence_ids == ("EV-T08-INITIAL-ASV", "EV-T08-INITIAL-WEB"),
            tuple(item.name for item in self.tool_definitions) == TOOL_NAMES,
            canonical_sha256([item.model_dump(mode="json") for item in self.tool_definitions]) == TOOL_SCHEMA_IDENTITY,
            self.required_evidence_ids == EVIDENCE_IDS,
            self.required_claim_ids == CLAIM_IDS,
            self.required_citation_ids == CITATION_IDS,
            self.required_alternative_ids == ALTERNATIVE_IDS,
            self.material_unknown_claim_ids == UNKNOWN_CLAIM_IDS,
            self.required_block_ids == BLOCK_IDS,
            self.required_state_sequence == STATE_SEQUENCE,
            self.required_event_sequence == EVENT_SEQUENCE,
            self.fixed_criteria == (("B08-R1", 2), ("B08-R2", 1), ("B08-R3", 1)),
            self.runtime_criteria
            == tuple((item["criterion_id"], item["weight"]) for item in SPEC["scoring"]["runtime_case"]["criteria"]),
            self.required_counts
            == (("evidence", 12), ("claims", 15), ("citations", 10), ("blocks", 7), ("states", 15), ("events", 17)),
            self.future_thresholds == (("fixed", 7), ("runtime", 24), ("pair", 32)),
            self.hard_failures == HARD_FAILURES,
            self.allowed_dispositions
            == ("REFERENCE_CONFORMANT", "RUNTIME_SCREENING_PASS_WITH_EXPLICIT_LIMITATIONS", "RUNTIME_SCREENING_NO_GO"),
            self.publication_paths == PUBLICATION_PATHS,
            self.specification_identity == SPEC_IDENTITY,
        )
        if not all(exact):
            raise ValueError("runtime pair specification authority differs")
        return self


class VS01RuntimeAcquisitionRun(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid", json_schema_extra=_run_schema)
    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["VS01RuntimeAcquisitionRun"] = "VS01RuntimeAcquisitionRun"
    pair_specification_identity: Sha256
    case_id: str
    prompt: str
    request_revision: int = Field(ge=1, le=2)
    request_identity: Sha256
    supersedes_request_identity: Sha256 | None
    supersedes_run_identity: Sha256 | None
    plan_identity: Sha256
    initial_assessment: str
    tool_calls: tuple[RuntimeToolCallRecord, ...]
    evidence_ledger: tuple[RuntimeEvidenceRecord, ...]
    claim_ledger: tuple[RuntimeClaimRecord, ...]
    citation_ledger: tuple[RuntimeCitationRecord, ...]
    answer_blocks: tuple[RuntimeAnswerBlock, ...]
    accepted_alternative_ids: tuple[str, ...]
    material_unknown_claim_ids: tuple[str, ...]
    final_sufficiency: str
    state_sequence: tuple[str, ...]
    audit_events: tuple[RuntimeAuditEvent, ...]
    operation_counters: RuntimeOperationCounters
    answer_projection_identity: Sha256
    acquisition_run_identity: Sha256

    @model_validator(mode="after")
    def exact_state(self) -> Self:
        from bsl.application.vs01_runtime_reference import validate_acquisition_run

        validate_acquisition_run(self)
        return self


class VS01B08RuntimePairResult(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid", json_schema_extra=_result_schema)
    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["VS01B08RuntimePairResult"] = "VS01B08RuntimePairResult"
    pair_specification_identity: Sha256
    acquisition_run_identity: Sha256
    fixed_case_result_identity: Sha256
    fixed_points: int = Field(ge=0, le=8)
    runtime_criteria: tuple[RuntimeCriterion, ...]
    runtime_points: int = Field(ge=0, le=28)
    pair_points: int = Field(ge=0, le=36)
    tool_calls_observed: int = Field(ge=0)
    events_observed: int = Field(ge=0)
    hard_failures: tuple[str, ...]
    leakage_incidents: int = Field(ge=0)
    replay_run_identities: tuple[Sha256, Sha256]
    disposition: Literal[
        "REFERENCE_CONFORMANT", "RUNTIME_SCREENING_PASS_WITH_EXPLICIT_LIMITATIONS", "RUNTIME_SCREENING_NO_GO"
    ]
    limitations: tuple[str, ...]
    pair_result_identity: Sha256

    @model_validator(mode="after")
    def exact_state(self) -> Self:
        from bsl.application.vs01_runtime_scoring import validate_pair_result

        validate_pair_result(self)
        return self


class VS01RuntimeScreeningReceipt(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid", json_schema_extra=_receipt_schema)
    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["VS01RuntimeScreeningReceipt"] = "VS01RuntimeScreeningReceipt"
    receipt_id: UUID
    generated_at: datetime
    receipt_canonical_sha256: Sha256
    implementation_commit: CommitSha
    pair_specification_identity: Sha256
    acquisition_run_identity: Sha256
    pair_result: VS01B08RuntimePairResult
    pair_result_identity: Sha256
    pair_result_file_sha256: Sha256
    archive_root: str
    archive_paths: tuple[str, str, str, str]
    disposition: Literal["DRY_RUN_VALIDATED", "REFERENCE_CONFORMANT", "REFERENCE_NONCONFORMANT", "VERIFIED_EXISTING"]
    published: bool
    verified_existing: bool
    authority_fingerprints_initial: tuple[tuple[str, Sha256], ...]
    authority_fingerprints_pre_store: tuple[tuple[str, Sha256], ...]
    authority_fingerprints_post_store: tuple[tuple[str, Sha256], ...]
    canonical_recovery_state: Literal["EMPTY", "OBJECT_ONLY", "OBJECT_AND_SNAPSHOT", "COMPLETE"] | None
    operation_ledger: RuntimeControllerLedger
    retained_publication_receipt: VS01RuntimeScreeningReceipt | None
    retained_publication_receipt_id: UUID | None
    retained_publication_receipt_file_sha256: Sha256 | None

    @model_validator(mode="after")
    def exact_state(self) -> Self:
        from bsl.infrastructure.runtime_screening_store import validate_screening_receipt

        validate_screening_receipt(self)
        return self
