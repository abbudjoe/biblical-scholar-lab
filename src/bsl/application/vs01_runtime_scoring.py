from __future__ import annotations

from typing import Any

import rfc8785

from bsl.contracts.runtime_screening import (
    CLAIM_IDS,
    EVENT_SEQUENCE,
    EVIDENCE_IDS,
    HARD_FAILURES,
    STATE_SEQUENCE,
    TOOL_NAMES,
    RuntimeCriterion,
    VS01B08RuntimePairResult,
    VS01B08RuntimePairSpecification,
    VS01RuntimeAcquisitionRun,
    canonical_sha256,
)

LIMITATIONS = (
    "single passage and ChatGPT-authored public screening pair",
    "deterministic oracle runtime rather than model-mediated tool selection",
    "no critical apparatus or witness evidence",
    "no REV-P2 specialist gold",
    "not training eligible or private-final eligible",
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
            tuple(item.model_dump(mode="json") for item in run.claim_ledger)
            == tuple(item.model_dump(mode="json") for item in reference.claim_ledger),
            tuple(item.model_dump(mode="json") for item in run.citation_ledger)
            == tuple(item.model_dump(mode="json") for item in reference.citation_ledger),
            tuple(item.model_dump(mode="json") for item in run.answer_blocks)
            == tuple(item.model_dump(mode="json") for item in reference.answer_blocks),
            tuple(item.claim_id for item in run.claim_ledger) == CLAIM_IDS,
        )
    )


def _lineage_lost(run: VS01RuntimeAcquisitionRun) -> bool:
    valid = (run.request_revision == 1 and run.supersedes_run_identity is None) or (
        run.request_revision > 1 and run.supersedes_run_identity is not None
    )
    return not valid


def _model_route(run: VS01RuntimeAcquisitionRun) -> bool:
    counters = run.operation_counters
    return bool(
        counters.model_invocations
        or counters.network_invocations
        or counters.ocr_invocations
        or counters.vlm_invocations
    )


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
