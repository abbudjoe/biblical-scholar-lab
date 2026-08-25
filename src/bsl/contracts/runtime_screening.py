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
CASE_FILE_SHA256 = "a7fc02da5ed8fda15ee29cba79cff8b037b2abc66352107f87165a0bfbea9f0f"
CASE_IDENTITY = "a1fdd253614df0ca7789a44372dabb895dcfda042656104ab68c9c6b351c17dd"
SPEC_FILE_SHA256 = "9e49e2f2b540a54c1d945991eb6500a52c0a7873136630d8bf49854efeb765ba"
SPEC_IDENTITY = "98c5df4b4906261cd96fa194ecf2035474633bdc9988388886c8b081e1835f51"


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(rfc8785.dumps(value)).hexdigest()


def _authority(path: Path, file_sha: str, identity_name: str, identity: str) -> dict[str, Any]:
    if hashlib.sha256(data := path.read_bytes()).hexdigest() != file_sha:
        raise ValueError(f"frozen runtime authority hash differs: {path.name}")
    value = cast(dict[str, Any], json.loads(data))
    claimed = value.pop(identity_name)
    if (claimed, canonical_sha256(value)) != (identity, identity):
        raise ValueError(f"frozen runtime authority identity differs: {path.name}")
    return value | {identity_name: claimed}


CASE = _authority(CASE_PATH, CASE_FILE_SHA256, "case_content_sha256", CASE_IDENTITY)
SPEC = _authority(SPEC_PATH, SPEC_FILE_SHA256, "spec_identity", SPEC_IDENTITY)
PROMPT = cast(str, CASE["prompt"])
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
PUBLICATION_PATHS = (
    "objects/sha256/<prefix>/<pair-result-sha256>",
    "snapshots/benchmark/vs01-b08-runtime-pair/reference-screening.json",
    "manifests/benchmark/vs01-b08-runtime-pair/reference-screening/runtime-screening-receipt.json",
    ".incoming/vs01-b08-runtime-pair-<pair-result-sha256>.runtime-screening-stage",
)
REAL_COUNTER_NAMES = (
    ("real_subject_invocations", "real_broker_tool_calls", "real_scoring_invocations")
    + ("real_acquisition_runs", "real_pair_results", "real_receipts", "real_publications")
    + ("canonical_archive_writes", "database_writes", "t03_raw_source_reads")
    + ("model_ocr_vlm_network_cloud_invocations",)
)


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
            value = json.loads(text)
            if (
                not isinstance(value, dict)
                or rfc8785.dumps(cast(dict[str, Any], value)).decode() != text
                or canonical_sha256(cast(dict[str, Any], value)) != digest
            ):
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


def _tuple_const(values: tuple[Any, ...]) -> dict[str, Any]:
    return {"const": [list(cast(tuple[Any, ...], item)) if isinstance(item, tuple) else item for item in values]}


def _fixed_records(schema: dict[str, Any], field: str, name: str, values: tuple[str, ...]) -> None:
    item = schema["properties"][field]["items"]
    schema["properties"][field] = {
        "type": "array",
        "prefixItems": [
            {"allOf": [item, {"properties": {name: {"const": value}}, "required": [name]}]} for value in values
        ],
        "minItems": len(values),
        "maxItems": len(values),
    }


def _upstream_constants() -> tuple[tuple[str, str], ...]:
    return tuple(
        (f"{task}.{name}", "null" if value is None else str(value))
        for task in ("t04", "t05", "t06", "t07")
        for name, value in SPEC["upstream_authorities"][task].items()
        if isinstance(value, (str, int)) or value is None
    )


def _spec_schema(schema: dict[str, Any]) -> None:
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    constants = {
        "pair_id": "BENCH-VS01-B08-PAIR-01",
        "prompt": PROMPT,
        "fixed_case_id": "VS01-B08-C01",
        "fixed_case_content_sha256": "28ebe4b02d19b316e027b2c68dce02114e7a40c1f050bba357a4b8cb43d5529a",
        "runtime_case_id": "VS01-B08-RUNTIME-C01",
        "runtime_case_content_sha256": CASE_IDENTITY,
        "specification_identity": SPEC_IDENTITY,
    }
    for name, value in constants.items():
        schema["properties"][name] = {"const": value}
    for name, values in (
        ("upstream_authority", _upstream_constants()),
        ("initial_evidence_ids", ("EV-T08-INITIAL-ASV", "EV-T08-INITIAL-WEB")),
        ("required_evidence_ids", EVIDENCE_IDS),
        ("required_claim_ids", CLAIM_IDS),
        ("required_citation_ids", CITATION_IDS),
        ("required_alternative_ids", ALTERNATIVE_IDS),
        ("material_unknown_claim_ids", UNKNOWN_CLAIM_IDS),
        ("required_block_ids", BLOCK_IDS),
        ("required_state_sequence", STATE_SEQUENCE),
        ("required_event_sequence", EVENT_SEQUENCE),
        ("hard_failures", HARD_FAILURES),
        (
            "allowed_dispositions",
            (
                "REFERENCE_CONFORMANT",
                "RUNTIME_SCREENING_PASS_WITH_EXPLICIT_LIMITATIONS",
                "RUNTIME_SCREENING_NO_GO",
            ),
        ),
        ("publication_paths", PUBLICATION_PATHS),
    ):
        schema["properties"][name] = _tuple_const(values)
    _fixed_records(schema, "tool_definitions", "name", TOOL_NAMES)
    for field, values in (
        ("fixed_criteria", (("B08-R1", 2), ("B08-R2", 1), ("B08-R3", 1))),
        (
            "runtime_criteria",
            tuple((item["criterion_id"], item["weight"]) for item in SPEC["scoring"]["runtime_case"]["criteria"]),
        ),
        (
            "required_counts",
            (("evidence", 12), ("claims", 15), ("citations", 10), ("blocks", 7), ("states", 15), ("events", 17)),
        ),
        ("future_thresholds", (("fixed", 7), ("runtime", 24), ("pair", 32))),
    ):
        schema["properties"][field] = _tuple_const(values)


def _run_schema(schema: dict[str, Any]) -> None:
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["properties"]["pair_specification_identity"] = {"const": SPEC_IDENTITY}
    schema["properties"]["prompt"] = {"const": PROMPT}
    schema["properties"]["state_sequence"] = _tuple_const(STATE_SEQUENCE)
    schema["properties"]["accepted_alternative_ids"] = _tuple_const(ALTERNATIVE_IDS)
    schema["properties"]["material_unknown_claim_ids"] = _tuple_const(UNKNOWN_CLAIM_IDS)
    _fixed_records(schema, "tool_calls", "tool", TOOL_NAMES)
    _fixed_records(schema, "evidence_ledger", "evidence_id", EVIDENCE_IDS)
    _fixed_records(schema, "claim_ledger", "claim_id", CLAIM_IDS)
    _fixed_records(schema, "citation_ledger", "citation_id", CITATION_IDS)
    _fixed_records(schema, "answer_blocks", "block_id", BLOCK_IDS)
    _fixed_records(schema, "audit_events", "event", EVENT_SEQUENCE)


def _result_schema(schema: dict[str, Any]) -> None:
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["properties"]["pair_specification_identity"] = {"const": SPEC_IDENTITY}
    criteria = tuple(item["criterion_id"] for item in SPEC["scoring"]["runtime_case"]["criteria"])
    _fixed_records(schema, "runtime_criteria", "criterion_id", criteria)


def _receipt_schema(schema: dict[str, Any]) -> None:
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["properties"]["pair_specification_identity"] = {"const": SPEC_IDENTITY}
    schema["properties"]["archive_paths"] = {
        "type": "array",
        "prefixItems": [
            {"type": "string", "pattern": r"^objects/sha256/[0-9a-f]{2}/[0-9a-f]{64}$"},
            {"const": PUBLICATION_PATHS[1]},
            {"const": PUBLICATION_PATHS[2]},
            {"type": "string", "pattern": r"^\.incoming/vs01-b08-runtime-pair-[0-9a-f]{64}\.runtime-screening-stage$"},
        ],
        "minItems": 4,
        "maxItems": 4,
    }


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
            self.pair_id == "BENCH-VS01-B08-PAIR-01",
            self.prompt == PROMPT,
            (self.fixed_case_id, self.fixed_case_content_sha256)
            == ("VS01-B08-C01", SPEC["upstream_authorities"]["t07"]["fixed_case_content_sha256"]),
            (self.runtime_case_id, self.runtime_case_content_sha256) == ("VS01-B08-RUNTIME-C01", CASE_IDENTITY),
            self.upstream_authority == _upstream_constants(),
            self.initial_evidence_ids == ("EV-T08-INITIAL-ASV", "EV-T08-INITIAL-WEB"),
            tuple(item.name for item in self.tool_definitions) == TOOL_NAMES,
            all(item.maximum_calls == 1 for item in self.tool_definitions),
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
    request_revision: int = Field(ge=1)
    supersedes_run_identity: Sha256 | None
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
    acquisition_run_identity: Sha256

    @model_validator(mode="after")
    def identity_and_boundary(self) -> Self:
        boundary = (
            tuple(item.tool for item in self.tool_calls)
            + tuple(item.evidence_id for item in self.evidence_ledger)
            + tuple(item.claim_id for item in self.claim_ledger)
            + tuple(item.citation_id for item in self.citation_ledger)
            + tuple(item.block_id for item in self.answer_blocks)
            + self.state_sequence
            + tuple(item.event for item in self.audit_events)
            + self.accepted_alternative_ids
            + self.material_unknown_claim_ids
        )
        expected_boundary = (
            TOOL_NAMES
            + EVIDENCE_IDS
            + CLAIM_IDS
            + CITATION_IDS
            + BLOCK_IDS
            + STATE_SEQUENCE
            + EVENT_SEQUENCE
            + ALTERNATIVE_IDS
            + UNKNOWN_CLAIM_IDS
        )
        if self.pair_specification_identity != SPEC_IDENTITY or self.prompt != PROMPT or boundary != expected_boundary:
            raise ValueError("runtime acquisition authority differs")
        if self.request_revision == 1 and self.supersedes_run_identity is not None:
            raise ValueError("initial runtime request cannot supersede a run")
        expected = canonical_sha256(self.model_dump(mode="json", exclude={"acquisition_run_identity"}))
        if self.acquisition_run_identity != expected:
            raise ValueError("runtime acquisition identity differs")
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
        "REFERENCE_CONFORMANT",
        "RUNTIME_SCREENING_PASS_WITH_EXPLICIT_LIMITATIONS",
        "RUNTIME_SCREENING_NO_GO",
    ]
    limitations: tuple[str, ...]
    pair_result_identity: Sha256

    @model_validator(mode="after")
    def identity_and_arithmetic(self) -> Self:
        runtime = sum(item.points for item in self.runtime_criteria)
        if (self.runtime_points, self.pair_points) != (runtime, self.fixed_points + runtime):
            raise ValueError("runtime pair-result arithmetic differs")
        expected = canonical_sha256(self.model_dump(mode="json", exclude={"pair_result_identity"}))
        if self.pair_specification_identity != SPEC_IDENTITY or self.pair_result_identity != expected:
            raise ValueError("runtime pair-result identity differs")
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
    pair_result_identity: Sha256
    pair_result_file_sha256: Sha256
    archive_root: str
    archive_paths: tuple[str, str, str, str]
    disposition: Literal["DRY_RUN_VALIDATED", "REFERENCE_CONFORMANT", "REFERENCE_NONCONFORMANT", "VERIFIED_EXISTING"]
    published: bool
    verified_existing: bool
    authority_fingerprints_before: tuple[tuple[str, Sha256], ...]
    authority_fingerprints_after: tuple[tuple[str, Sha256], ...]
    real_operation_counters: tuple[tuple[str, int], ...]

    @model_validator(mode="after")
    def operational_identity(self) -> Self:
        if self.receipt_id.version != 7 or self.generated_at.tzinfo is None or self.generated_at.utcoffset() is None:
            raise ValueError("runtime screening receipt UUID or timestamp differs")
        payload = self.model_dump(mode="json", exclude={"receipt_canonical_sha256"})
        if self.pair_specification_identity != SPEC_IDENTITY or self.receipt_canonical_sha256 != canonical_sha256(
            payload
        ):
            raise ValueError("runtime screening receipt identity differs")
        result_sha = self.pair_result_file_sha256
        paths = (
            f"objects/sha256/{result_sha[:2]}/{result_sha}",
            PUBLICATION_PATHS[1],
            PUBLICATION_PATHS[2],
            f".incoming/vs01-b08-runtime-pair-{result_sha}.runtime-screening-stage",
        )
        state = {
            "DRY_RUN_VALIDATED": (False, False),
            "REFERENCE_CONFORMANT": (True, False),
            "REFERENCE_NONCONFORMANT": (False, False),
            "VERIFIED_EXISTING": (False, True),
        }[self.disposition]
        valid = (
            self.archive_paths == paths,
            (self.published, self.verified_existing) == state,
            self.authority_fingerprints_before == self.authority_fingerprints_after,
            tuple(name for name, _value in self.real_operation_counters) == REAL_COUNTER_NAMES,
            all(value == 0 for _name, value in self.real_operation_counters),
        )
        if not all(valid):
            raise ValueError("runtime screening receipt operation differs")
        return self
