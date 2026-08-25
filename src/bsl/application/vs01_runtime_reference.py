from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol, cast
from uuid import UUID

import rfc8785
from uuid6 import uuid7

from bsl.contracts.runtime_screening import (
    PROMPT,
    SPEC_IDENTITY,
    TOOL_NAMES,
    TOOL_PLAN,
    RuntimeToolCallRecord,
    RuntimeToolDefinition,
    VS01B08RuntimePairResult,
    VS01B08RuntimePairSpecification,
    VS01RuntimeAcquisitionRun,
    VS01RuntimeScreeningReceipt,
    canonical_sha256,
)

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
    def __init__(self, plan: tuple[dict[str, Any], ...] = tuple(TOOL_PLAN)) -> None:
        self._plan = plan
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
        schemas = {item.name: item for item in package.tool_schemas}
        outputs: list[dict[str, Any]] = []
        for name in TOOL_NAMES:
            definition = schemas.get(name)
            if definition is None:
                raise ValueError("runtime subject tool schema is missing")
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
    visible_ids = tuple(item.get("runtime_evidence_id") for item in package.initial_evidence)
    valid = (
        package.prompt == PROMPT,
        visible_ids == ("EV-T08-INITIAL-ASV", "EV-T08-INITIAL-WEB"),
        len(package.tool_schemas) == 7,
        {item.name for item in package.tool_schemas} == set(TOOL_NAMES),
        package.calls_per_tool == 1,
        package.retries == package.fallbacks == 0,
        not any(field in rendered for field in FORBIDDEN_SUBJECT_FIELDS),
        not any(value.startswith(("/", "file:", "postgres")) for value in (package.case_id, package.prompt)),
    )
    if not all(valid):
        raise ValueError("INVALID_LEAKAGE_INCIDENT")


def subject_package_from_projection(projection: dict[str, Any], *, case_id: str | None = None) -> RuntimeSubjectPackage:
    payload: dict[str, Any] = {
        "case_id": case_id or projection["case_id"],
        "prompt": projection["prompt"],
        "initial_evidence": tuple(projection["initial_evidence"]),
        "tool_schemas": tuple(RuntimeToolDefinition.model_validate(item) for item in projection["tool_schemas"]),
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
    trace = (subject or DeterministicRuntimeSubject()).run(package, RuntimeToolBroker())
    if trace.initial_assessment != "INSUFFICIENT_FOR_REQUESTED_GREEK_AND_TEXTUAL_CRITICAL_CLAIMS":
        raise ValueError("runtime subject failed to record initial insufficiency")
    if trace.final_sufficiency != "SUFFICIENT_WITH_QUALIFICATION":
        raise ValueError("runtime subject failed final sufficiency reassessment")
    draft = template.model_copy(update={"case_id": package.case_id, "tool_calls": trace.tool_calls})
    payload = draft.model_dump(mode="json", exclude={"acquisition_run_identity"})
    return VS01RuntimeAcquisitionRun.model_validate_json(
        rfc8785.dumps(payload | {"acquisition_run_identity": canonical_sha256(payload)})
    )


def corrected_runtime(
    previous: VS01RuntimeAcquisitionRun,
    package: RuntimeSubjectPackage,
    subject: VS01RuntimeSubjectAdapter | None = None,
) -> VS01RuntimeAcquisitionRun:
    if previous.pair_specification_identity != SPEC_IDENTITY:
        raise ValueError("corrected runtime authority differs")
    rerun = execute_reference_runtime(previous, package, subject)
    draft = replace(
        _run_fields(rerun),
        request_revision=previous.request_revision + 1,
        supersedes_run_identity=previous.acquisition_run_identity,
    )
    payload = draft.payload()
    return VS01RuntimeAcquisitionRun.model_validate_json(
        rfc8785.dumps(payload | {"acquisition_run_identity": canonical_sha256(payload)})
    )


@dataclass(frozen=True)
class _RunFields:
    values: dict[str, Any]
    request_revision: int
    supersedes_run_identity: str | None

    def payload(self) -> dict[str, Any]:
        return self.values | {
            "request_revision": self.request_revision,
            "supersedes_run_identity": self.supersedes_run_identity,
        }


def _run_fields(run: VS01RuntimeAcquisitionRun) -> _RunFields:
    values = run.model_dump(
        mode="json",
        exclude={"request_revision", "supersedes_run_identity", "acquisition_run_identity"},
    )
    return _RunFields(values, run.request_revision, run.supersedes_run_identity)


def complete_runtime_pair(
    specification: VS01B08RuntimePairSpecification,
    projection: dict[str, Any],
    template: VS01RuntimeAcquisitionRun,
    fixed_case_result_identity: str,
    fingerprints: tuple[tuple[str, str], ...],
    root: Path,
    *,
    dry_run: bool,
    implementation_commit: str | None = None,
    new_uuid: Callable[[], UUID] = uuid7,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> RuntimePairOutput:
    from bsl.application.vs01_runtime_scoring import score_runtime_pair
    from bsl.infrastructure.benchmark_store import implementation_head
    from bsl.infrastructure.runtime_screening_store import (
        build_screening_receipt,
        canonical_pair_result_bytes,
        publish_runtime_screening,
        verify_existing,
    )

    package = subject_package_from_projection(projection)
    first = execute_reference_runtime(template, package, _real_authorized=True)
    second = execute_reference_runtime(template, package, _real_authorized=True)
    result = score_runtime_pair(
        specification,
        first,
        template,
        fixed_case_result_identity,
        (first.acquisition_run_identity, second.acquisition_run_identity),
    )
    existing = None if dry_run else verify_existing(root, result, canonical_pair_result_bytes(result))
    disposition = (
        "DRY_RUN_VALIDATED"
        if dry_run and result.disposition == "REFERENCE_CONFORMANT"
        else "REFERENCE_NONCONFORMANT"
        if result.disposition != "REFERENCE_CONFORMANT"
        else "VERIFIED_EXISTING"
        if existing is not None
        else "REFERENCE_CONFORMANT"
    )
    receipt = build_screening_receipt(
        result,
        first,
        root,
        fingerprints,
        disposition=disposition,
        implementation_commit=implementation_commit or implementation_head(),
        new_uuid=new_uuid,
        now=now,
    )
    published = disposition == "REFERENCE_CONFORMANT"
    if published:
        publish_runtime_screening(root, result, receipt)
    return specification, first, result, receipt, published
