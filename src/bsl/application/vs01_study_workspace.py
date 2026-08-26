from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import rfc8785

from bsl.contracts.page_fixture import BASE_BYTES, BASE_SHA256, DEGRADED_BYTES, DEGRADED_SHA256
from bsl.contracts.runtime_screening import SPEC_IDENTITY
from bsl.contracts.study_workspace import VS01StudyWorkspaceProjection
from bsl.infrastructure import study_workspace_authority as authority_store

# ruff: noqa: E501, SIM905

QUESTION = (
    "You have only the supplied ASV and WEB Classic wording for John 1:5. Does the Greek mean both "
    "“understand” and “overcome,” and is a textual variant involved?"
)
REGION_ROLES = (
    *(
        "CANONICAL_TEXT VERSE_NUMBER SECTION_HEADING STUDY_NOTE_OR_FOOTNOTE CROSS_REFERENCE USER_ANNOTATION PAGE_HEADER"
    ).split(),  # noqa: SIM905
)
EVIDENCE_HORIZON = (
    *(
        "critical apparatus and witness evidence|translation-project source-base documentation|"
        "translator documentation|"
        "modern specialist scholarship|historical English semantic evidence for ASV “apprehended”"
    ).split("|"),  # noqa: SIM905
)
TRANSLATIONS = tuple(
    json.loads(
        '[{"edition":"American Standard Version","focal_span":"apprehended it not","text":"And the light shineth in the darkness; and the darkness apprehended it not.","translation_id":"ASV"},{"edition":"World English Bible Classic","focal_span":"hasn’t overcome it","text":"The light shines in the darkness, and the darkness hasn’t overcome it.","translation_id":"WEB_CLASSIC"}]'
    )  # noqa: E501
)
ZERO_OPERATIONS = (
    *(
        "archive_writes database_reads database_writes t03_reads raw_source_reads model_calls ocr_calls vlm_calls "
        "external_network_calls cloud_calls"
    ).split(),  # noqa: SIM905
)


def _page(authority: authority_store.StudyWorkspaceAuthority) -> dict[str, Any]:
    fixture = authority.page_fixture
    by_role = {region.benchmark_role: region for region in fixture.scene.regions}
    regions = [
        {
            "region_id": by_role[role].region_id,
            "role": role,
            "text": by_role[role].text,
            "reading_order": by_role[role].benchmark_reading_order_index,
            "pixel_bbox_xywh": by_role[role].pixel_bbox_xywh,
            "normalized_bbox_xyxy": by_role[role].normalized_bbox_xyxy,
            "authority_class": by_role[role].authority_class,
        }
        for role in REGION_ROLES
    ]
    variants = (
        {
            "variant_id": "BASE",
            "view_id": "base-page",
            "asset_id": "T06-BASE-PNG",
            "sha256": BASE_SHA256,
            "byte_count": BASE_BYTES,
            "dimensions_px": (1600, 2200),
            "region_roles": REGION_ROLES,
            "visual_state": "LEGIBLE",
            "canonical_text_may_replace_illegible_pixels": False,
        },
        {
            "variant_id": "DEGRADED_ILLEGIBILITY",
            "view_id": "degraded-illegibility-v1",
            "asset_id": "T06-DEGRADED-PNG",
            "sha256": DEGRADED_SHA256,
            "byte_count": DEGRADED_BYTES,
            "dimensions_px": (1600, 2200),
            "region_roles": REGION_ROLES,
            "visual_state": "PARTIALLY_ILLEGIBLE",
            "canonical_text_may_replace_illegible_pixels": False,
        },
    )
    return {
        "fixture_identity": fixture.fixture_identity,
        "publication_receipt_uuid": str(authority.page_receipt.receipt_identity),
        "label": fixture.rights_and_public_display["required_label"],
        "variants": variants,
        "regions": regions,
    }


def _audit(authority: authority_store.StudyWorkspaceAuthority) -> dict[str, Any]:
    run, result = authority.acquisition_run, authority.pair_result
    return {
        "t04": {"packet_identity": "aebcbb50fc8383f2f4f395bc71116563325c1fde237427dc8c1bc8140e8ebe31"},
        "t05": {
            "execution_identity": "f0697ce01cfa4579223a59042e49de7377d3ec5dee7cca29468bbab3cfba20cc",
            "study_answer_identity": "f18264255ab9117cdd7fa40d9da35c614d31a9bfcabce7a5e95e7b0a040424fd",
        },
        "t06": {
            "fixture_identity": authority.page_fixture.fixture_identity,
            "publication_receipt_uuid": authority_store.T06_RECEIPT_UUID,
            "fixture_json_sha256": "c8cfc4eafee6b0a16fc2e0442190782a35e2b03477a619854105d5272f08417f",
            "base_png_sha256": BASE_SHA256,
            "degraded_png_sha256": DEGRADED_SHA256,
        },
        "t08": {
            "implementation_commit": authority.t08_receipt.implementation_commit,
            "pair_specification_identity": SPEC_IDENTITY,
            "acquisition_run_identity": authority_store.RUN_IDENTITY,
            "answer_projection_identity": authority_store.ANSWER_IDENTITY,
            "fixed_case_result_identity": authority_store.FIXED_RESULT_IDENTITY,
            "pair_result_identity": authority_store.PAIR_IDENTITY,
            "pair_result_file_sha256": authority_store.PAIR_SHA256,
            "publication_receipt_uuid": authority_store.T08_RECEIPT_UUID,
            "receipt_canonical_sha256": authority_store.T08_RECEIPT_CANONICAL_SHA256,
            "receipt_file_sha256": authority_store.T08_RECEIPT_FILE_SHA256,
            "scores": {"fixed": result.fixed_points, "runtime": result.runtime_points, "pair": result.pair_points},
            "structure_counts": {
                "tool_calls": len(run.tool_calls),
                "evidence": len(run.evidence_ledger),
                "claims": len(run.claim_ledger),
                "citations": len(run.citation_ledger),
                "blocks": len(run.answer_blocks),
                "states": len(run.state_sequence),
                "events": len(run.audit_events),
            },
            "disposition": result.disposition,
        },
    }


def _evidence_inspector(authority: authority_store.StudyWorkspaceAuthority) -> tuple[dict[str, Any], ...]:
    run = authority.acquisition_run
    evidence = {item.evidence_id: item for item in run.evidence_ledger}
    return tuple(
        {
            "citation_id": citation.citation_id,
            "evidence_id": citation.evidence_id,
            "source_role": evidence[citation.evidence_id].source_role,
            "source_handle": evidence[citation.evidence_id].source_handle,
            "selector": citation.selector,
            "quoted_span": citation.quoted_span,
            "claims": tuple(
                {
                    "claim_id": claim.claim_id,
                    "epistemic_status": claim.epistemic_status,
                    "required_qualifications": claim.required_qualifications,
                }
                for claim in run.claim_ledger
                if citation.evidence_id in claim.evidence_ids
            ),
            "inspection_level": "PUBLIC_SAFE_PROJECTED_AUTHORITY",
        }
        for citation in run.citation_ledger
    )


def _workspace_payload(authority: authority_store.StudyWorkspaceAuthority) -> dict[str, Any]:
    run = authority.acquisition_run
    return {
        "schema_version": "1.0",
        "contract": "VS01StudyWorkspaceProjection",
        "workspace_id": "VS01-JOHN-1-5-STUDY-WORKSPACE",
        "route": "DETERMINISTIC_LOCAL_ONLY",
        "answer_mode": "STUDY",
        "active_context": {
            "reference": "John.1.5",
            "display_reference": "John 1:5",
            "greek_edition": "SBLGNT",
            "translation_editions": ("American Standard Version", "World English Bible Classic"),
            "method": "EVIDENCE_FIRST",
            "evidence_state": "SUFFICIENT_WITH_QUALIFICATION",
            "model_route": "NONE",
            "runtime_characterization": "DETERMINISTIC_MODEL_FREE",
            "scope": "ONE_PASSAGE_ONLY",
            "specialist_review": "NOT_REV_P2_SPECIALIST_GOLD",
            "capability_claim": "NO_BROAD_PRODUCT_CAPABILITY_CLAIM",
        },
        "question": QUESTION,
        "translations": TRANSLATIONS,
        "greek": {
            "clause": "καὶ ἡ σκοτία αὐτὸ οὐ κατέλαβεν.",
            "target": "κατέλαβεν",
            "lemma": "καταλαμβάνω",
            "morphology": {
                "person": "third",
                "number": "singular",
                "tense_form": "aorist",
                "voice_form": "active",
                "mood_form": "indicative",
            },
            "morphology_evidential_role": "FORMAL_EVIDENCE_NOT_DECISIVE_CONTEXTUAL_MEANING",
        },
        "study_blocks": [item.model_dump(mode="json") for item in run.answer_blocks],
        "evidence_records": [item.model_dump(mode="json") for item in run.evidence_ledger],
        "claim_records": [item.model_dump(mode="json") for item in run.claim_ledger],
        "citation_records": [item.model_dump(mode="json") for item in run.citation_ledger],
        "evidence_inspector": _evidence_inspector(authority),
        "accepted_alternative_ids": run.accepted_alternative_ids,
        "material_unknown_claim_ids": run.material_unknown_claim_ids,
        "evidence_horizon": EVIDENCE_HORIZON,
        "page_study": _page(authority),
        "audit_bindings": _audit(authority),
        "operation_disclosure": dict.fromkeys(ZERO_OPERATIONS, 0),
    }


def compile_vs01_study_workspace(archive_root: Path) -> VS01StudyWorkspaceProjection:
    payload = _workspace_payload(authority_store.load_study_workspace_authority(archive_root))
    identity = hashlib.sha256(rfc8785.dumps(payload)).hexdigest()
    return VS01StudyWorkspaceProjection.model_validate_json(rfc8785.dumps(payload | {"workspace_identity": identity}))


def canonical_workspace_projection_bytes(projection: VS01StudyWorkspaceProjection) -> bytes:
    data = rfc8785.dumps(projection.model_dump(mode="json"))
    VS01StudyWorkspaceProjection.model_validate_json(data)
    return data
