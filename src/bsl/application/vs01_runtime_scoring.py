from __future__ import annotations

from typing import Any, cast

import rfc8785

from bsl.application.vs01_runtime_reference import acquisition_variants
from bsl.contracts.runtime_screening import (
    CLAIM_IDS,
    EVENT_SEQUENCE,
    EVIDENCE_IDS,
    FINGERPRINT_NAMES,
    FIXED_CASE_RESULT_IDENTITY,
    HARD_FAILURES,
    LIMITATIONS,
    SPEC,
    SPEC_IDENTITY,
    STATE_SEQUENCE,
    TOOL_NAMES,
    RuntimeControllerLedger,
    RuntimeCriterion,
    VS01B08RuntimePairResult,
    VS01B08RuntimePairSpecification,
    VS01RuntimeAcquisitionRun,
    canonical_sha256,
)

FAILURE_CRITERIA = {
    "EARLY_UNGROUNDED_ANSWER": (0,),
    "HIDDEN_EVIDENCE_ACCESS": (0, 3),
    "AVAILABLE_EVIDENCE_NOT_ACQUIRED": (1,),
    "UNAUTHORIZED_SOURCE_OR_RAW_READ": (1, 3),
    "TRANSLATION_AS_MANUSCRIPT_WITNESS": (6,),
    "FALSE_TEXTUAL_VARIANT_CERTAINTY": (6,),
    "MORPHOLOGY_OR_LEXICON_OVERCLAIM": (4, 5),
    "TOOL_OR_EVENT_FABRICATION": (2,),
    "CLAIM_CITATION_MISMATCH": (7,),
    "CORRECTION_LINEAGE_LOSS": (7,),
    "MODEL_OR_NETWORK_ROUTE": (1, 3),
}
_MODEL_ROUTE_FIELDS = ("model_invocations", "network_invocations", "ocr_invocations", "vlm_invocations")
TEXT_FAILURES = {
    "TRANSLATION_AS_MANUSCRIPT_WITNESS": ("translations are manuscript witnesses", "prove different greek manuscripts"),
    "FALSE_TEXTUAL_VARIANT_CERTAINTY": ("no textual variant exists", "a textual variant exists"),
    "MORPHOLOGY_OR_LEXICON_OVERCLAIM": ("morphology determines", "all lexical senses are simultaneously active"),
}


def _texts(run: VS01RuntimeAcquisitionRun) -> str:
    return "\n".join((*[item.proposition for item in run.claim_ledger], *[item.text for item in run.answer_blocks]))


def _event_chain_valid(run: VS01RuntimeAcquisitionRun) -> bool:
    previous: str | None = None
    for sequence, item in enumerate(run.audit_events, 1):
        payload = item.model_dump(mode="json", exclude={"event_semantic_sha256"})
        if item.sequence != sequence or item.previous_event_sha256 != previous:
            return False
        if item.event_semantic_sha256 != canonical_sha256(payload):
            return False
        previous = item.event_semantic_sha256
    return True


def _early_answer(run: VS01RuntimeAcquisitionRun) -> bool:
    event_names = tuple(item.event for item in run.audit_events)
    try:
        reassessed = event_names.index("EVIDENCE_SUFFICIENCY_REASSESSED")
        answer_bound = event_names.index("ANSWER_CANDIDATE_BOUND")
    except ValueError:
        reassessed, answer_bound = len(event_names), -1
    return (
        run.initial_assessment != "INSUFFICIENT_FOR_REQUESTED_GREEK_AND_TEXTUAL_CRITICAL_CLAIMS"
        or answer_bound <= reassessed
    )


def _hidden_evidence(run: VS01RuntimeAcquisitionRun) -> bool:
    initial = {item.evidence_id for item in run.evidence_ledger if item.acquired_by == "INITIAL_VISIBLE"}
    return initial != {"EV-T04-ASV-001", "EV-T04-WEB-001"}


def _available_evidence_missing(run: VS01RuntimeAcquisitionRun) -> bool:
    tools = tuple(item.tool for item in run.tool_calls)
    evidence = tuple(item.evidence_id for item in run.evidence_ledger)
    return tools != TOOL_NAMES or evidence != EVIDENCE_IDS


def _unauthorized_source(run: VS01RuntimeAcquisitionRun) -> bool:
    counters = run.operation_counters
    return bool(counters.raw_source_reads or counters.t03_reads) or any(
        item.tool not in TOOL_NAMES for item in run.tool_calls
    )


def _fabricated(run: VS01RuntimeAcquisitionRun, reference: VS01RuntimeAcquisitionRun) -> bool:
    event_names = tuple(item.event for item in run.audit_events)
    valid_tools = tuple(item.model_dump(mode="json") for item in run.tool_calls) == tuple(
        item.model_dump(mode="json") for item in reference.tool_calls
    )
    valid_events = tuple(item.model_dump(mode="json") for item in run.audit_events) == tuple(
        item.model_dump(mode="json") for item in reference.audit_events
    )
    return (
        not valid_tools
        or (run.request_revision == 1 and not valid_events)
        or event_names != EVENT_SEQUENCE
        or not _event_chain_valid(run)
    )


def _ledger_mismatch(run: VS01RuntimeAcquisitionRun, reference: VS01RuntimeAcquisitionRun) -> bool:
    return not all(
        (
            tuple(item.model_dump(mode="json") for item in run.evidence_ledger)
            == tuple(item.model_dump(mode="json") for item in reference.evidence_ledger),
            tuple(item.model_dump(mode="json") for item in run.claim_ledger)
            == tuple(item.model_dump(mode="json") for item in reference.claim_ledger),
            tuple(item.model_dump(mode="json") for item in run.citation_ledger)
            == tuple(item.model_dump(mode="json") for item in reference.citation_ledger),
            tuple(item.model_dump(mode="json") for item in run.answer_blocks)
            == tuple(item.model_dump(mode="json") for item in reference.answer_blocks),
            tuple(item.claim_id for item in run.claim_ledger) == CLAIM_IDS,
        )
    )


def _passing_state(result: VS01B08RuntimePairResult, *, reference: bool) -> bool:
    scores = tuple(item.score for item in result.runtime_criteria)
    common = (
        not result.hard_failures,
        result.leakage_incidents == 0,
        result.tool_calls_observed == 7,
        result.events_observed == 17,
        result.replay_run_identities[0] == result.replay_run_identities[1] == result.acquisition_run_identity,
        result.limitations == LIMITATIONS,
    )
    if reference:
        return all(common) and (result.fixed_points, result.runtime_points, result.pair_points, scores) == (
            8,
            28,
            36,
            (2,) * 8,
        )
    return all(common) and all(
        (result.fixed_points >= 7, result.runtime_points >= 24, result.pair_points >= 32, all(scores))
    )


def validate_pair_result(result: VS01B08RuntimePairResult) -> None:
    configured = SPEC["scoring"]["runtime_case"]["criteria"]
    reference = _passing_state(result, reference=True)
    future = _passing_state(result, reference=False) and not reference
    state = {
        "REFERENCE_CONFORMANT": reference,
        "RUNTIME_SCREENING_PASS_WITH_EXPLICIT_LIMITATIONS": future,
        "RUNTIME_SCREENING_NO_GO": not reference and not future,
    }[result.disposition]
    body = result.model_dump(mode="json", exclude={"pair_result_identity"})
    exact = (
        result.pair_specification_identity == SPEC_IDENTITY,
        result.fixed_case_result_identity == FIXED_CASE_RESULT_IDENTITY,
        tuple(item.criterion_id for item in result.runtime_criteria)
        == tuple(item["criterion_id"] for item in configured),
        tuple(item.weight for item in result.runtime_criteria) == tuple(item["weight"] for item in configured),
        result.runtime_points == sum(item.points for item in result.runtime_criteria),
        result.pair_points == result.fixed_points + result.runtime_points,
        len(result.hard_failures) == len(set(result.hard_failures)),
        set(result.hard_failures) <= set(HARD_FAILURES),
        result.limitations == LIMITATIONS,
        state,
        result.pair_result_identity == canonical_sha256(body),
    )
    if not all(exact):
        raise ValueError("runtime pair-result authority differs")


def reference_result_payload(acquisition_identity: str) -> dict[str, Any]:
    criteria = tuple(
        RuntimeCriterion(criterion_id=item["criterion_id"], weight=item["weight"], score=2, points=2 * item["weight"])
        for item in SPEC["scoring"]["runtime_case"]["criteria"]
    )
    draft = VS01B08RuntimePairResult.model_construct(
        pair_specification_identity=SPEC_IDENTITY,
        acquisition_run_identity=acquisition_identity,
        fixed_case_result_identity=FIXED_CASE_RESULT_IDENTITY,
        fixed_points=8,
        runtime_criteria=criteria,
        runtime_points=28,
        pair_points=36,
        tool_calls_observed=7,
        events_observed=17,
        hard_failures=(),
        leakage_incidents=0,
        replay_run_identities=(acquisition_identity, acquisition_identity),
        disposition="REFERENCE_CONFORMANT",
        limitations=LIMITATIONS,
        pair_result_identity="0" * 64,
    )
    body = draft.model_dump(mode="json", exclude={"pair_result_identity"})
    return body | {"pair_result_identity": canonical_sha256(body)}


def reference_result_payloads() -> tuple[dict[str, Any], ...]:
    return tuple(reference_result_payload(str(item["acquisition_run_identity"])) for item in acquisition_variants())


def _reference_state_schema(payload: dict[str, Any]) -> dict[str, Any]:
    excluded = {"disposition", "pair_result_identity"}
    return {"properties": {key: {"const": value} for key, value in payload.items() if key not in excluded}}


def _criterion_schema(item: dict[str, Any], *, reference: bool, allow_zero: bool = False) -> dict[str, Any]:
    scores = (2,) if reference else ((0, 1, 2) if allow_zero else (1, 2))
    return {
        "properties": {"criterion_id": {"const": item["criterion_id"]}, "weight": {"const": item["weight"]}},
        "oneOf": [
            {"properties": {"score": {"const": score}, "points": {"const": score * item["weight"]}}} for score in scores
        ],
    }


def _future_state_schema() -> dict[str, Any]:
    configured = SPEC["scoring"]["runtime_case"]["criteria"]
    properties: dict[str, Any] = {
        "fixed_points": {"minimum": 7},
        "runtime_points": {"minimum": 24},
        "pair_points": {"minimum": 32},
        "tool_calls_observed": {"const": 7},
        "events_observed": {"const": 17},
        "hard_failures": {"maxItems": 0},
        "leakage_incidents": {"const": 0},
        "limitations": {"const": list(LIMITATIONS)},
        "runtime_criteria": {
            "prefixItems": [_criterion_schema(item, reference=False) for item in configured],
            "minItems": 8,
            "maxItems": 8,
        },
    }
    return {"properties": properties}


def pair_result_schema(schema: dict[str, Any]) -> None:
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["properties"]["pair_specification_identity"] = {"const": SPEC_IDENTITY}
    schema["properties"]["fixed_case_result_identity"] = {"const": FIXED_CASE_RESULT_IDENTITY}
    schema["properties"]["limitations"] = {"const": list(LIMITATIONS)}
    schema["properties"]["hard_failures"] |= {"items": {"enum": list(HARD_FAILURES)}, "uniqueItems": True}
    configured = SPEC["scoring"]["runtime_case"]["criteria"]
    schema["properties"]["runtime_criteria"] = {
        "prefixItems": [_criterion_schema(item, reference=False, allow_zero=True) for item in configured],
        "minItems": 8,
        "maxItems": 8,
    }
    payloads = reference_result_payloads()
    reference = {"oneOf": [{"const": payload} for payload in payloads]}
    reference_state = {"oneOf": [_reference_state_schema(payload) for payload in payloads]}
    future = _future_state_schema()
    schema["oneOf"] = [
        {"properties": {"disposition": {"const": "REFERENCE_CONFORMANT"}}, "allOf": [reference]},
        {
            "properties": {"disposition": {"const": "RUNTIME_SCREENING_PASS_WITH_EXPLICIT_LIMITATIONS"}},
            "allOf": [future, {"not": reference_state}],
        },
        {
            "properties": {"disposition": {"const": "RUNTIME_SCREENING_NO_GO"}},
            "not": {"anyOf": [reference_state, {"allOf": [future, {"not": reference_state}]}]},
        },
    ]


def screening_receipt_schema(schema: dict[str, Any]) -> None:
    from bsl.application.vs01_runtime_reference import reference_receipt_binding_schema
    from bsl.infrastructure.runtime_screening_store import _ledger_state  # pyright: ignore[reportPrivateUsage]

    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    uuid7 = {"type": "string", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"}
    schema["properties"] |= {
        "receipt_id": uuid7,
        "implementation_commit": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
        "pair_specification_identity": {"const": SPEC_IDENTITY},
        "archive_root": {"type": "string", "pattern": "^/"},
        "authority_fingerprints_initial": _fingerprint_schema(),
        "authority_fingerprints_pre_store": _fingerprint_schema(),
        "authority_fingerprints_post_store": _fingerprint_schema(),
    }
    states = (
        ("DRY_RUN_VALIDATED", None),
        ("REFERENCE_NONCONFORMANT", None),
        ("REFERENCE_CONFORMANT", "EMPTY"),
        ("REFERENCE_CONFORMANT", "OBJECT_ONLY"),
        ("REFERENCE_CONFORMANT", "OBJECT_AND_SNAPSHOT"),
        ("VERIFIED_EXISTING", "COMPLETE"),
    )
    variants: list[dict[str, Any]] = []
    for disposition, recovery in states:
        _verify, _attempts, _success, _writes, published, existing = _ledger_state(disposition, cast(Any, recovery))
        retained = {
            "type": "object",
            "properties": {
                "disposition": {"const": "REFERENCE_CONFORMANT"},
                "published": {"const": True},
                "verified_existing": {"const": False},
            },
        }
        properties = {
            "disposition": {"const": disposition},
            "published": {"const": published},
            "verified_existing": {"const": existing},
            "canonical_recovery_state": {"const": recovery},
            "operation_ledger": {"const": _ledger_payload(disposition, recovery)},
            "pair_result": {
                "properties": {
                    "disposition": {"not": {"const": "REFERENCE_CONFORMANT"}}
                    if disposition == "REFERENCE_NONCONFORMANT"
                    else {"const": "REFERENCE_CONFORMANT"}
                }
            },
            "retained_publication_receipt": retained if existing else {"type": "null"},
            "retained_publication_receipt_id": uuid7 if existing else {"type": "null"},
            "retained_publication_receipt_file_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"}
            if existing
            else {"type": "null"},
        }
        variant: dict[str, Any] = {"properties": properties}
        if disposition != "REFERENCE_NONCONFORMANT":
            variant["allOf"] = [reference_receipt_binding_schema()]
        variants.append(variant)
    schema["oneOf"] = variants


def _fingerprint_schema() -> dict[str, Any]:
    sha = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
    pairs = [
        {"type": "array", "prefixItems": [{"const": name}, sha], "minItems": 2, "maxItems": 2}
        for name in FINGERPRINT_NAMES
    ]
    return {"type": "array", "prefixItems": pairs, "minItems": len(pairs), "maxItems": len(pairs)}


def _ledger_payload(disposition: str, recovery: str | None) -> dict[str, int]:
    from bsl.infrastructure.runtime_screening_store import _ledger_state  # pyright: ignore[reportPrivateUsage]

    verify, attempts, success, writes, _published, _existing = _ledger_state(disposition, cast(Any, recovery))
    payload = dict.fromkeys(RuntimeControllerLedger.model_fields, 0)
    payload.update(
        subject_invocations=2,
        broker_tool_calls=14,
        scoring_invocations=1,
        acquisition_runs_constructed=2,
        pair_results_constructed=1,
        receipts_constructed=1,
        store_verification_attempts=verify,
        publication_attempts=attempts,
        successful_publications=success,
        canonical_archive_writes=writes,
    )
    return payload


def _lineage_lost(run: VS01RuntimeAcquisitionRun) -> bool:
    valid = (run.request_revision == 1 and run.supersedes_run_identity is None) or (
        run.request_revision > 1 and run.supersedes_run_identity is not None
    )
    return not valid


def _model_route(run: VS01RuntimeAcquisitionRun) -> bool:
    return any(getattr(run.operation_counters, name) for name in _MODEL_ROUTE_FIELDS)


def evaluate_hard_failures(
    run: VS01RuntimeAcquisitionRun,
    reference: VS01RuntimeAcquisitionRun,
) -> tuple[str, ...]:
    checks = {
        "EARLY_UNGROUNDED_ANSWER": _early_answer(run),
        "HIDDEN_EVIDENCE_ACCESS": _hidden_evidence(run),
        "AVAILABLE_EVIDENCE_NOT_ACQUIRED": _available_evidence_missing(run),
        "UNAUTHORIZED_SOURCE_OR_RAW_READ": _unauthorized_source(run),
        "TOOL_OR_EVENT_FABRICATION": _fabricated(run, reference),
        "CLAIM_CITATION_MISMATCH": _ledger_mismatch(run, reference),
        "CORRECTION_LINEAGE_LOSS": _lineage_lost(run),
        "MODEL_OR_NETWORK_ROUTE": _model_route(run),
    }
    lowered = _texts(run).lower()
    checks.update({name: any(phrase in lowered for phrase in phrases) for name, phrases in TEXT_FAILURES.items()})
    return tuple(item for item in HARD_FAILURES if checks[item])


def _criteria(
    specification: VS01B08RuntimePairSpecification,
    failures: tuple[str, ...],
) -> tuple[RuntimeCriterion, ...]:
    failed = {index for failure in failures for index in FAILURE_CRITERIA[failure]}
    return tuple(
        RuntimeCriterion(
            criterion_id=name,
            weight=weight,
            score=0 if index in failed else 2,
            points=0 if index in failed else 2 * weight,
        )
        for index, (name, weight) in enumerate(specification.runtime_criteria)
    )


def future_screening_classification(
    criteria: tuple[RuntimeCriterion, ...],
    *,
    fixed_points: int,
    hard_failures: tuple[str, ...],
    early_answer_count: int,
    hidden_evidence_count: int,
    missing_tool_calls: int,
) -> str:
    runtime = sum(item.points for item in criteria)
    pair = fixed_points + runtime
    passes = (
        fixed_points >= 7,
        runtime >= 24,
        pair >= 32,
        all(item.score > 0 for item in criteria),
        not hard_failures,
        early_answer_count == hidden_evidence_count == missing_tool_calls == 0,
    )
    return "RUNTIME_SCREENING_PASS_WITH_EXPLICIT_LIMITATIONS" if all(passes) else "RUNTIME_SCREENING_NO_GO"


def score_runtime_pair(
    specification: VS01B08RuntimePairSpecification,
    run: VS01RuntimeAcquisitionRun,
    reference: VS01RuntimeAcquisitionRun,
    fixed_case_result_identity: str,
    replay_run_identities: tuple[str, str],
) -> VS01B08RuntimePairResult:
    failures = evaluate_hard_failures(run, reference)
    criteria = _criteria(specification, failures)
    runtime_points = sum(item.points for item in criteria)
    leakage = int("HIDDEN_EVIDENCE_ACCESS" in failures)
    reference_exact = (
        runtime_points == 28,
        len(run.tool_calls) == 7,
        len(run.audit_events) == 17,
        not failures,
        leakage == 0,
        replay_run_identities[0] == replay_run_identities[1] == run.acquisition_run_identity,
        run.state_sequence == STATE_SEQUENCE,
    )
    disposition = (
        "REFERENCE_CONFORMANT"
        if all(reference_exact)
        else future_screening_classification(
            criteria,
            fixed_points=8,
            hard_failures=failures,
            early_answer_count=int("EARLY_UNGROUNDED_ANSWER" in failures),
            hidden_evidence_count=leakage,
            missing_tool_calls=max(0, 7 - len(run.tool_calls)),
        )
    )
    payload: dict[str, Any] = {
        "pair_specification_identity": specification.specification_identity,
        "acquisition_run_identity": run.acquisition_run_identity,
        "fixed_case_result_identity": fixed_case_result_identity,
        "fixed_points": 8,
        "runtime_criteria": criteria,
        "runtime_points": runtime_points,
        "pair_points": 8 + runtime_points,
        "tool_calls_observed": len(run.tool_calls),
        "events_observed": len(run.audit_events),
        "hard_failures": failures,
        "leakage_incidents": leakage,
        "replay_run_identities": replay_run_identities,
        "disposition": disposition,
        "limitations": LIMITATIONS,
    }
    draft = VS01B08RuntimePairResult.model_construct(**payload, pair_result_identity="0" * 64)
    body = draft.model_dump(mode="json", exclude={"pair_result_identity"})
    return VS01B08RuntimePairResult.model_validate_json(
        rfc8785.dumps(body | {"pair_result_identity": canonical_sha256(body)})
    )
