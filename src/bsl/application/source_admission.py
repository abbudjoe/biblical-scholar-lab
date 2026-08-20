from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import rfc8785
from uuid6 import uuid7

from bsl.contracts.source_admission import (
    PlannedSource,
    SourceAcquisitionDryRun,
    SourcePlanSemanticPayload,
)

APPROVED_MANIFEST_SHA256 = "9410d89f00829dd7bfe0d71d4f27a64b59046d8f38c353426e161d7c36415816"
HARD_PROHIBITIONS = (
    "no training",
    "no embeddings or vector indexes",
    "no Lambda or other cloud execution",
    "no automatic source updates",
    "no mixed-rights MACULA ingestion",
    "no apparatus",
    "no copyrighted modern translation or study Bible page",
    "no user-private source",
    "no model-generated source evidence",
)


def _object_without_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"unsupported JSON number: {value}")


def _read_manifest(path: Path) -> tuple[dict[str, object], str]:
    raw = path.read_bytes()
    parsed = json.loads(
        raw,
        object_pairs_hook=_object_without_duplicates,
        parse_constant=_reject_constant,
    )
    if not isinstance(parsed, dict):
        raise ValueError("source plan must be a JSON object")
    return cast(dict[str, object], parsed), hashlib.sha256(raw).hexdigest()


def _validated_sources(manifest: dict[str, object], identity: str) -> tuple[PlannedSource, ...]:
    sources = cast(list[dict[str, object]], manifest["sources"])
    stops = ("SOURCE_ACQUISITION_NOT_AUTHORIZED_NOW", *HARD_PROHIBITIONS)
    planned: list[PlannedSource] = []
    for source in sources:
        computed = {
            "relative_quarantine_plan": f"quarantine/SOURCE-PLAN-01/{source['source_id']}",
            "planned_manifest_identity": identity,
            "pre_acquisition_stop_conditions": stops,
        }
        planned.append(PlannedSource.model_validate_json(json.dumps(source | computed)))
    return tuple(planned)


def compile_source_plan(path: Path) -> SourceAcquisitionDryRun:
    manifest, identity = _read_manifest(path)
    if identity != APPROVED_MANIFEST_SHA256:
        raise ValueError("manifest bytes do not match the approved SOURCE-PLAN-01 identity")
    payload = SourcePlanSemanticPayload(
        artifact_id="SOURCE-PLAN-01",
        status="APPROVED",
        vertical_slice="VS-01",
        design_baseline_commit=cast(str, manifest["design_baseline_commit"]),
        manifest_identity=identity,
        training_authorized=False,
        embedding_authorized=False,
        cloud_execution_authorized=False,
        source_acquisition_authorized_now=False,
        sources=_validated_sources(manifest, identity),
        hard_prohibitions=HARD_PROHIBITIONS,
    )
    semantic_sha256 = hashlib.sha256(rfc8785.dumps(payload.model_dump(mode="json"))).hexdigest()
    return SourceAcquisitionDryRun(
        receipt_id=uuid7(),
        generated_at=datetime.now(UTC),
        semantic_payload=payload,
        semantic_sha256=semantic_sha256,
    )


def semantic_bytes(receipt: SourceAcquisitionDryRun) -> bytes:
    return rfc8785.dumps(receipt.semantic_payload.model_dump(mode="json"))
