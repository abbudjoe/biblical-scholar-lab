from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol, cast
from uuid import UUID

import rfc8785
from uuid6 import uuid7

from bsl.contracts.runtime_screening import (
    _LEDGER_HASHES,  # pyright: ignore[reportPrivateUsage]
    _REFERENCE,  # pyright: ignore[reportPrivateUsage]
    ALTERNATIVE_IDS,
    CORRECTION_PROMPT,
    INITIAL_EVIDENCE,
    PROMPT,
    SPEC_IDENTITY,
    STATE_SEQUENCE,
    SYNTHETIC_CASE_ID,
    TOOL_NAMES,
    TOOL_PLAN,
    TOOL_SCHEMA_IDENTITY,
    UNKNOWN_CLAIM_IDS,
    RuntimeControllerLedger,
    RuntimeToolCallRecord,
    RuntimeToolDefinition,
    VS01B08RuntimePairResult,
    VS01B08RuntimePairSpecification,
    VS01RuntimeAcquisitionRun,
    VS01RuntimeScreeningReceipt,
    acquisition_variant_payload,
    answer_identity,
    canonical_sha256,
    expected_events,
    expected_tool_calls,
    plan_identity,
    request_identity,
)

PROJECTION_PATH = Path(__file__).parents[3] / "fixtures/VS01-T08/runtime-subject-projection.json"
_PROJECTION = cast(dict[str, Any], json.loads(PROJECTION_PATH.read_bytes()))
if canonical_sha256(_PROJECTION["tool_schemas"]) != TOOL_SCHEMA_IDENTITY:
    raise ValueError("runtime subject tool-schema authority differs")
FORBIDDEN_SUBJECT_FIELDS = (
    "expected_output",
    "expected_tool_order",
    "scorer",
    "rubric",
    "hard_failures",
    "thresholds",
    "t04_claim_graph",
    "t05_answer",
    "archive_root",
    "database",
)
RuntimePairOutput = tuple[
    VS01B08RuntimePairSpecification,
    VS01RuntimeAcquisitionRun,
    VS01B08RuntimePairResult,
    VS01RuntimeScreeningReceipt,
    bool,
]


@dataclass(frozen=True)
class RuntimeSubjectPackage:
    case_id: str
    prompt: str
    initial_evidence: tuple[dict[str, Any], dict[str, Any]]
    tool_schemas: tuple[RuntimeToolDefinition, ...]
    calls_per_tool: int
    retries: int
    fallbacks: int
    output_schema: tuple[tuple[str, int | bool], ...]
    package_identity: str

    def payload(self, *, include_identity: bool = True) -> dict[str, Any]:
        value = {
            "case_id": self.case_id,
            "prompt": self.prompt,
            "initial_evidence": self.initial_evidence,
            "tool_schemas": tuple(item.model_dump(mode="json") for item in self.tool_schemas),
            "calls_per_tool": self.calls_per_tool,
            "retries": self.retries,
            "fallbacks": self.fallbacks,
            "output_schema": self.output_schema,
        }
        return value | ({"package_identity": self.package_identity} if include_identity else {})


@dataclass(frozen=True)
class RuntimeSubjectTrace:
    initial_assessment: str
    tool_calls: tuple[RuntimeToolCallRecord, ...]
    final_sufficiency: str


class RuntimeToolBroker:
    def __init__(self, prompt: str = PROMPT) -> None:
        plan: list[dict[str, Any]] = []
        for index, item in enumerate(TOOL_PLAN):
            value = dict(item)
            value["input"] = dict(item["input"])
            if index == 0:
                value["input"]["prompt"] = prompt
            plan.append(value)
        self._plan = tuple(plan)
        self._calls: list[RuntimeToolCallRecord] = []

    @property
    def calls(self) -> tuple[RuntimeToolCallRecord, ...]:
        return tuple(self._calls)

    def call(self, tool_name: str, structured_input: dict[str, Any]) -> dict[str, Any]:
        index = len(self._calls)
        if index >= len(self._plan):
            raise ValueError("runtime tool budget exhausted")
        expected = self._plan[index]
        if tool_name != expected["tool"] or structured_input != expected["input"]:
            raise ValueError("runtime tool name, order, or structured input differs")
        if any(item.tool == tool_name for item in self._calls) or expected["maximum_calls"] != 1:
            raise ValueError("runtime tool duplicate or budget differs")
        input_json = rfc8785.dumps(structured_input).decode()
        output = cast(dict[str, Any], expected["expected_output"])
        output_json = rfc8785.dumps(output).decode()
        self._calls.append(
            RuntimeToolCallRecord(
                sequence=index + 1,
                tool_call_id=expected["tool_call_id"],
                tool=tool_name,
                input_json=input_json,
                output_json=output_json,
                input_sha256=canonical_sha256(structured_input),
                output_sha256=canonical_sha256(output),
            )
        )
        return json.loads(output_json)


class VS01RuntimeSubjectAdapter(Protocol):
    def run(self, package: RuntimeSubjectPackage, broker: RuntimeToolBroker) -> RuntimeSubjectTrace: ...


def _value_from_schema(schema: dict[str, Any]) -> Any:
    if "const" in schema:
        return schema["const"]
    if schema.get("type") == "object":
        properties = cast(dict[str, dict[str, Any]], schema["properties"])
        return {name: _value_from_schema(properties[name]) for name in cast(list[str], schema["required"])}
    if schema.get("type") == "array":
        return [_value_from_schema(item) for item in cast(list[dict[str, Any]], schema["prefixItems"])]
    raise ValueError("runtime subject input schema lacks a deterministic value")


class DeterministicRuntimeSubject:
    def run(self, package: RuntimeSubjectPackage, broker: RuntimeToolBroker) -> RuntimeSubjectTrace:
        audit_subject_package(package)
        outputs: list[dict[str, Any]] = []
        for name, definition in zip(TOOL_NAMES, package.tool_schemas, strict=True):
            schema = cast(dict[str, Any], json.loads(definition.input_schema_json))
            value = cast(dict[str, Any], _value_from_schema(schema))
            outputs.append(broker.call(name, value))
        initial = cast(str, outputs[0].get("status"))
        final = cast(str, outputs[-1].get("status"))
        return RuntimeSubjectTrace(initial, broker.calls, final)


def audit_subject_package(package: RuntimeSubjectPackage) -> None:
    payload = package.payload(include_identity=False)
    if package.package_identity != canonical_sha256(payload):
        raise ValueError("runtime subject package identity differs")
    rendered = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    expected_tools = _subject_tool_definitions(package.prompt)
    real = package.case_id == "VS01-B08-RUNTIME-C01"
    valid = (
        package.case_id in {"VS01-B08-RUNTIME-C01", SYNTHETIC_CASE_ID},
        package.prompt == PROMPT if real else package.prompt in {PROMPT, CORRECTION_PROMPT},
        package.initial_evidence == INITIAL_EVIDENCE,
        package.tool_schemas == expected_tools,
        package.calls_per_tool == 1,
        package.retries == package.fallbacks == 0,
        package.output_schema == tuple(_PROJECTION["output_schema"].items()),
        not any(field in rendered for field in FORBIDDEN_SUBJECT_FIELDS),
        not any(value.startswith(("/", "file:", "postgres")) for value in (package.case_id, package.prompt)),
    )
    if not all(valid):
        raise ValueError("INVALID_LEAKAGE_INCIDENT")


def _subject_tool_definitions(prompt: str) -> tuple[RuntimeToolDefinition, ...]:
    values = [dict(item) for item in cast(list[dict[str, Any]], _PROJECTION["tool_schemas"])]
    if prompt == CORRECTION_PROMPT:
        schema = json.loads(values[0]["input_schema_json"])
        schema["properties"]["prompt"]["const"] = prompt
        values[0]["input_schema_json"] = rfc8785.dumps(schema).decode()
    return tuple(RuntimeToolDefinition.model_validate(item) for item in values)


def subject_package_from_projection(
    projection: dict[str, Any], *, case_id: str | None = None, prompt: str | None = None
) -> RuntimeSubjectPackage:
    provided = tuple(RuntimeToolDefinition.model_validate(item) for item in projection["tool_schemas"])
    if provided != _subject_tool_definitions(PROMPT):
        raise ValueError("runtime subject projection tool authority differs")
    request_prompt = prompt or cast(str, projection["prompt"])
    payload: dict[str, Any] = {
        "case_id": case_id or projection["case_id"],
        "prompt": request_prompt,
        "initial_evidence": tuple(projection["initial_evidence"]),
        "tool_schemas": _subject_tool_definitions(request_prompt),
        "calls_per_tool": projection["budgets"]["calls_per_tool"],
        "retries": projection["budgets"]["retries"],
        "fallbacks": projection["budgets"]["fallbacks"],
        "output_schema": tuple(projection["output_schema"].items()),
    }
    payload["package_identity"] = canonical_sha256(
        {
            **payload,
            "tool_schemas": tuple(item.model_dump(mode="json") for item in payload["tool_schemas"]),
        }
    )
    package = RuntimeSubjectPackage(**payload)
    audit_subject_package(package)
    return package


def execute_reference_runtime(
    template: VS01RuntimeAcquisitionRun,
    package: RuntimeSubjectPackage,
    subject: VS01RuntimeSubjectAdapter | None = None,
    *,
    _real_authorized: bool = False,
) -> VS01RuntimeAcquisitionRun:
    if package.case_id == "VS01-B08-RUNTIME-C01" and not _real_authorized:
        raise ValueError("real T08 execution requires separate operational authorization")
    trace = (subject or DeterministicRuntimeSubject()).run(package, RuntimeToolBroker(package.prompt))
    if trace.initial_assessment != "INSUFFICIENT_FOR_REQUESTED_GREEK_AND_TEXTUAL_CRITICAL_CLAIMS":
        raise ValueError("runtime subject failed to record initial insufficiency")
    if trace.final_sufficiency != "SUFFICIENT_WITH_QUALIFICATION":
        raise ValueError("runtime subject failed final sufficiency reassessment")
    return _construct_run(template, package, trace)


def corrected_runtime(
    previous: VS01RuntimeAcquisitionRun,
    package: RuntimeSubjectPackage,
    subject: VS01RuntimeSubjectAdapter | None = None,
) -> VS01RuntimeAcquisitionRun:
    if (
        previous.pair_specification_identity != SPEC_IDENTITY
        or previous.case_id != SYNTHETIC_CASE_ID
        or previous.request_revision != 1
        or package.case_id != SYNTHETIC_CASE_ID
        or package.prompt != CORRECTION_PROMPT
    ):
        raise ValueError("corrected runtime authority differs")
    trace = (subject or DeterministicRuntimeSubject()).run(package, RuntimeToolBroker(package.prompt))
    rerun = _construct_run(
        previous,
        package,
        trace,
        revision=2,
        supersedes_request=previous.request_identity,
        supersedes_run=previous.acquisition_run_identity,
    )
    return rerun


def _construct_run(
    template: VS01RuntimeAcquisitionRun,
    package: RuntimeSubjectPackage,
    trace: RuntimeSubjectTrace,
    *,
    revision: int = 1,
    supersedes_request: str | None = None,
    supersedes_run: str | None = None,
) -> VS01RuntimeAcquisitionRun:
    request = request_identity(package.case_id, package.prompt, revision, supersedes_request)
    calls = tuple(item.model_dump(mode="json") for item in trace.tool_calls)
    plan, answer = plan_identity(request, calls), answer_identity(request)
    body: dict[str, Any] = template.model_dump(
        mode="json",
        exclude={
            "case_id",
            "prompt",
            "request_revision",
            "request_identity",
            "supersedes_request_identity",
            "supersedes_run_identity",
            "plan_identity",
            "tool_calls",
            "audit_events",
            "answer_projection_identity",
            "acquisition_run_identity",
        },
    ) | {
        "case_id": package.case_id,
        "prompt": package.prompt,
        "request_revision": revision,
        "request_identity": request,
        "supersedes_request_identity": supersedes_request,
        "supersedes_run_identity": supersedes_run,
        "plan_identity": plan,
        "tool_calls": calls,
        "audit_events": expected_events(request, plan, answer),
        "answer_projection_identity": answer,
    }
    return VS01RuntimeAcquisitionRun.model_validate_json(
        rfc8785.dumps(body | {"acquisition_run_identity": canonical_sha256(body)})
    )


def _synthetic_initial_payload() -> dict[str, Any]:
    return acquisition_variant_payload(SYNTHETIC_CASE_ID, PROMPT, 1, None, None)


def validate_acquisition_run(run: VS01RuntimeAcquisitionRun) -> None:
    synthetic = _synthetic_initial_payload()
    if run.request_revision == 1:
        lineage_valid = (run.supersedes_request_identity, run.supersedes_run_identity) == (None, None)
        namespace_valid = run.prompt == PROMPT and run.case_id in {"VS01-B08-RUNTIME-C01", SYNTHETIC_CASE_ID}
    else:
        lineage_valid = (run.supersedes_request_identity, run.supersedes_run_identity) == (
            synthetic["request_identity"],
            synthetic["acquisition_run_identity"],
        )
        namespace_valid = run.case_id == SYNTHETIC_CASE_ID and run.prompt == CORRECTION_PROMPT
    calls = expected_tool_calls(run.prompt)
    request = request_identity(run.case_id, run.prompt, run.request_revision, run.supersedes_request_identity)
    plan, answer = plan_identity(request, calls), answer_identity(request)
    records = (run.evidence_ledger, run.claim_ledger, run.citation_ledger, run.answer_blocks)
    exact = (
        run.pair_specification_identity == SPEC_IDENTITY,
        namespace_valid,
        lineage_valid,
        run.request_identity == request,
        run.plan_identity == plan,
        tuple(item.model_dump(mode="json") for item in run.tool_calls) == calls,
        tuple(canonical_sha256([item.model_dump(mode="json") for item in value]) for value in records)
        == _LEDGER_HASHES,
        run.initial_assessment == "INSUFFICIENT_FOR_REQUESTED_GREEK_AND_TEXTUAL_CRITICAL_CLAIMS",
        run.accepted_alternative_ids == ALTERNATIVE_IDS,
        run.material_unknown_claim_ids == UNKNOWN_CLAIM_IDS,
        run.final_sufficiency == "SUFFICIENT_WITH_QUALIFICATION",
        run.state_sequence == STATE_SEQUENCE,
        tuple(item.model_dump(mode="json") for item in run.audit_events) == expected_events(request, plan, answer),
        run.operation_counters.model_dump(mode="python") == _REFERENCE["operation_counters"],
        run.answer_projection_identity == answer,
    )
    identity = canonical_sha256(run.model_dump(mode="json", exclude={"acquisition_run_identity"}))
    if not all(exact) or run.acquisition_run_identity != identity:
        raise ValueError("runtime acquisition authority differs")


def acquisition_run_schema(schema: dict[str, Any]) -> None:
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    real = acquisition_variant_payload("VS01-B08-RUNTIME-C01", PROMPT, 1, None, None)
    synthetic = _synthetic_initial_payload()
    correction = acquisition_variant_payload(
        SYNTHETIC_CASE_ID,
        CORRECTION_PROMPT,
        2,
        cast(str, synthetic["request_identity"]),
        cast(str, synthetic["acquisition_run_identity"]),
    )
    schema["oneOf"] = [{"const": value} for value in (real, synthetic, correction)]


def _ledger(current: RuntimeControllerLedger | None = None, **increments: int) -> RuntimeControllerLedger:
    payload = current.model_dump(mode="python") if current else dict.fromkeys(RuntimeControllerLedger.model_fields, 0)
    for name, value in increments.items():
        payload[name] += value
    return RuntimeControllerLedger.model_validate(payload)


def complete_runtime_pair(
    specification: VS01B08RuntimePairSpecification,
    projection: dict[str, Any],
    template: VS01RuntimeAcquisitionRun,
    fixed_case_result_identity: str,
    fingerprints: tuple[tuple[str, str], ...],
    root: Path,
    *,
    dry_run: bool,
    authority_loader: Callable[[], tuple[tuple[str, str], ...]] | None = None,
    implementation_commit: str | None = None,
    new_uuid: Callable[[], UUID] = uuid7,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
    _case_id: str = "VS01-B08-RUNTIME-C01",
) -> RuntimePairOutput:
    from bsl.application.vs01_runtime_scoring import score_runtime_pair
    from bsl.infrastructure.benchmark_store import implementation_head
    from bsl.infrastructure.runtime_screening_store import complete_store_decision

    commit = implementation_commit or implementation_head()
    package = subject_package_from_projection(projection, case_id=_case_id)
    ledger = _ledger(subject_invocations=1)
    first = execute_reference_runtime(template, package, _real_authorized=True)
    ledger = _ledger(ledger, broker_tool_calls=len(first.tool_calls), acquisition_runs_constructed=1)
    ledger = _ledger(ledger, subject_invocations=1)
    second = execute_reference_runtime(template, package, _real_authorized=True)
    ledger = _ledger(ledger, broker_tool_calls=len(second.tool_calls), acquisition_runs_constructed=1)
    ledger = _ledger(ledger, scoring_invocations=1)
    result = score_runtime_pair(
        specification,
        first,
        first,
        fixed_case_result_identity,
        (first.acquisition_run_identity, second.acquisition_run_identity),
    )
    ledger = _ledger(ledger, pair_results_constructed=1)
    receipt, published = complete_store_decision(
        result,
        first,
        root,
        fingerprints,
        ledger,
        dry_run=dry_run,
        authority_loader=authority_loader,
        implementation_commit=commit,
        new_uuid=new_uuid,
        now=now,
    )
    return specification, first, result, receipt, published
