from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import PurePosixPath
from typing import Annotated, Literal, Self
from uuid import UUID

import rfc8785
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

STRICT = ConfigDict(strict=True, frozen=True, extra="forbid", allow_inf_nan=False, validate_by_name=True)
APPROVED_SOURCE_IDS = tuple(f"SP01-SRC-00{index}" for index in range(1, 7))
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


class PlannedSource(BaseModel):
    model_config = STRICT

    source_id: str = Field(pattern=r"^SP01-SRC-00[1-6]$")
    name: str
    provider: str | None = None
    transport_class: str = Field(validation_alias="source_type")
    repository: str | None = None
    package: str | None = None
    source_page: str | None = None
    revision: str
    tag: str | None = None
    doi: str | None = None
    trademark: str | None = None
    admitted_components: tuple[str, ...] = Field(validation_alias="components")
    admitted_fields: tuple[str, ...] = ()
    excluded_components: tuple[str, ...] = ()
    excluded_fields: tuple[str, ...] = ()
    normalized_scope: tuple[str, ...]
    license: str
    rights_lineage: str = Field(validation_alias="lineage")
    disposition: str
    relative_quarantine_plan: str
    planned_manifest_identity: str = Field(pattern=r"^[0-9a-f]{64}$")
    pre_acquisition_stop_conditions: tuple[str, ...]


class SourcePlanSemanticPayload(BaseModel):
    model_config = STRICT

    artifact_id: Literal["SOURCE-PLAN-01"]
    status: Literal["APPROVED"]
    vertical_slice: Literal["VS-01"]
    design_baseline_commit: str = Field(pattern=r"^[0-9a-f]{40}$")
    manifest_identity: str = Field(pattern=r"^[0-9a-f]{64}$")
    training_authorized: Literal[False]
    embedding_authorized: Literal[False]
    cloud_execution_authorized: Literal[False]
    source_acquisition_authorized_now: Literal[False]
    sources: tuple[PlannedSource, ...] = Field(min_length=6, max_length=6)
    hard_prohibitions: tuple[str, ...]

    @model_validator(mode="after")
    def exact_source_plan(self) -> Self:
        if tuple(source.source_id for source in self.sources) != APPROVED_SOURCE_IDS:
            raise ValueError("sources must match the exact approved order")
        if self.hard_prohibitions != HARD_PROHIBITIONS:
            raise ValueError("hard prohibitions must match SOURCE-PLAN-01 exactly")
        wrong_identity = any(source.planned_manifest_identity != self.manifest_identity for source in self.sources)
        if wrong_identity:
            raise ValueError("planned source identity does not match manifest identity")
        wrong_path = any(
            source.relative_quarantine_plan != f"quarantine/SOURCE-PLAN-01/{source.source_id}"
            for source in self.sources
        )
        if wrong_path:
            raise ValueError("planned quarantine path is not exact")
        return self


def _uuid7(value: UUID) -> UUID:
    if value.version != 7:
        raise ValueError("identifier must be UUIDv7")
    return value


def _aware(value: datetime) -> datetime:
    if value.utcoffset() is None:
        raise ValueError("timestamp must include an offset")
    return value


def _relative(value: str) -> str:
    path = PurePosixPath(value)
    if not value or value.startswith("/") or "\\" in value or path.as_posix() != value:
        raise ValueError("path must be a deterministic POSIX relative path")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("relative path contains an unsafe component")
    return value


class SourceAcquisitionDryRun(BaseModel):
    model_config = STRICT

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["SourceAcquisitionDryRun"] = "SourceAcquisitionDryRun"
    receipt_id: UUID
    generated_at: datetime
    semantic_payload: SourcePlanSemanticPayload
    semantic_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    _receipt_id_is_uuid7 = field_validator("receipt_id")(_uuid7)

    @model_validator(mode="after")
    def semantic_hash_matches_payload(self) -> Self:
        canonical = rfc8785.dumps(self.semantic_payload.model_dump(mode="json"))
        if hashlib.sha256(canonical).hexdigest() != self.semantic_sha256:
            raise ValueError("semantic SHA-256 does not match semantic payload")
        return self


SourceId = Literal[
    "SP01-SRC-001",
    "SP01-SRC-002",
    "SP01-SRC-003",
    "SP01-SRC-004",
    "SP01-SRC-005",
    "SP01-SRC-006",
]
Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
APPROVED_SOURCE_SPEC_SHA256 = {
    "SP01-SRC-001": "3f3dd2052ecd3ec5bb8453f886a08f78ead832bb12876f6c7f722b3b3bf053bc",
    "SP01-SRC-002": "ada40a6ea7fc6a612e5df6553db9dcf6ed814f8f970629442c5ccfce8cb200af",
    "SP01-SRC-003": "ba11adf17b62f02e6439aa8f9706ef33f4d234e919154f2f82e2604e71d9f822",
    "SP01-SRC-004": "3bbdd5ada5fcd247b018abd995a51df9c6545e0a543f80473bc171a72867cc98",
    "SP01-SRC-005": "b1538182c0cabbcbb2a85f42ac0e31ecc3200ceccccf5690cfb814ddd0a56141",
    "SP01-SRC-006": "dc251b4ad859fc42d78cbd619a91cb55b440b966393444683fef6f4d8856bb22",
}
_TEXT_OPERATIONS = (
    "ACQUIRE_AND_RETAIN",
    "PARSE_NORMALIZE",
    "EXACT_RUNTIME_LOOKUP",
    "PUBLIC_BENCHMARK_EXCERPT",
    "PUBLIC_DEMO",
)
_ATTRIBUTION = {
    "SP01-SRC-001": (
        "SBL Greek New Testament (SBLGNT), copyright © 2010 Society of Biblical Literature and Logos Bible "
        "Software, licensed CC BY 4.0. Source: https://github.com/Faithlife/SBLGNT"
    ),
    "SP01-SRC-002": (
        "Tauber, J. K., ed. (2017). MorphGNT: SBLGNT Edition, Version 6.12. DOI: 10.5281/zenodo.376200. "
        "Morphological parsing and lemmatization licensed CC BY-SA 3.0."
    ),
    "SP01-SRC-003": "American Standard Version (1901), openbibleinfo high-fidelity digital USX edition; public domain.",
    "SP01-SRC-004": (
        "World English Bible Classic, 2020 stable text; public domain. World English Bible is a trademark; "
        "modified derivatives must not be presented as the World English Bible."
    ),
    "SP01-SRC-005": "Abbott-Smith Greek Lexicon TEI release 1.1; public-domain TEI source.",
    "SP01-SRC-006": "Source Serif 4 release 4.005R; copyright and SIL Open Font License 1.1 notice retained.",
}
_SOURCE_OPERATIONS = {
    "SP01-SRC-003": (*_TEXT_OPERATIONS, "SYNTHETIC_PAGE"),
    "SP01-SRC-006": ("ACQUIRE_AND_RETAIN", "SYNTHETIC_PAGE", "PUBLIC_DEMO"),
}


def _source_spec_sha256(source: PlannedSource) -> str:
    digest = hashlib.sha256(rfc8785.dumps(source.model_dump(mode="json"))).hexdigest()
    if digest != APPROVED_SOURCE_SPEC_SHA256.get(source.source_id):
        raise ValueError("source specification differs from the approved manifest entry")
    return digest


def _source_rights(source: PlannedSource) -> tuple[tuple[str, ...], str]:
    return _SOURCE_OPERATIONS.get(source.source_id, _TEXT_OPERATIONS), _ATTRIBUTION[source.source_id]


class _HttpExchange(BaseModel):
    model_config = STRICT

    requested_url: str
    final_url: str
    status: Literal[200]
    redirect_chain: tuple[str, ...] = Field(max_length=5)
    headers: tuple[tuple[str, str], ...]
    response_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    retrieved_at: datetime
    byte_count: int = Field(ge=0)

    _retrieved_at_is_aware = field_validator("retrieved_at")(_aware)

    @model_validator(mode="after")
    def secure_urls(self) -> Self:
        urls = (self.requested_url, *self.redirect_chain, self.final_url)
        if any(not url.startswith("https://") for url in urls):
            raise ValueError("all retrieval URLs must use HTTPS")
        return self


class _FetchedObject(BaseModel):
    model_config = STRICT

    relative_path: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    byte_count: int = Field(ge=0)
    rights_evidence: bool

    _relative_path_is_safe = field_validator("relative_path")(_relative)


class _ArchiveEntry(BaseModel):
    model_config = STRICT

    relative_path: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    byte_count: int = Field(ge=0)

    _relative_path_is_safe = field_validator("relative_path")(_relative)


def _validate_inventory(
    source_id: str,
    objects: tuple[_FetchedObject, ...],
    archive_inventory: tuple[_ArchiveEntry, ...],
    objects_aggregate_sha256: str,
) -> None:
    paths = tuple(item.relative_path for item in objects)
    inventory_paths = tuple(item.relative_path for item in archive_inventory)
    invalid = (
        len(paths) != len(set(paths)) or not any(item.rights_evidence for item in objects),
        len(inventory_paths) != len(set(inventory_paths)),
        (source_id == "SP01-SRC-004") != bool(archive_inventory),
    )
    aggregate = hashlib.sha256(rfc8785.dumps(tuple(item.model_dump(mode="json") for item in objects))).hexdigest()
    if any(invalid) or objects_aggregate_sha256 != aggregate:
        raise ValueError("source object or archive inventory is inconsistent")


class FetchReceipt(BaseModel):
    model_config = STRICT

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["FetchReceipt"] = "FetchReceipt"
    receipt_id: UUID
    attempt_id: UUID
    generated_at: datetime
    source_id: SourceId
    manifest_identity: Literal["9410d89f00829dd7bfe0d71d4f27a64b59046d8f38c353426e161d7c36415816"]
    source_spec: PlannedSource
    source_spec_sha256: Sha256
    resolved_revision: str
    package_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    exchanges: tuple[_HttpExchange, ...] = Field(min_length=1)
    objects: tuple[_FetchedObject, ...] = Field(min_length=1)
    archive_inventory: tuple[_ArchiveEntry, ...]
    objects_aggregate_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    total_received_bytes: int = Field(ge=0)

    _ids_are_uuid7 = field_validator("receipt_id", "attempt_id")(_uuid7)
    _generated_at_is_aware = field_validator("generated_at")(_aware)

    def _revision_is_consistent(self) -> None:
        spec = self.source_spec
        expected = (spec.source_id, _source_spec_sha256(spec))
        actual = (self.source_id, self.source_spec_sha256)
        if actual != expected:
            raise ValueError("fetch identity differs from its frozen source specification")
        if self.source_id == "SP01-SRC-004":
            packages = tuple(item.sha256 for item in self.objects if item.relative_path == "eng-web_usfm.zip")
            if spec.revision != "ACQUISITION_TIMESTAMP_PLUS_SHA256_REQUIRED" or packages != (self.package_sha256,):
                raise ValueError("WEB fetch must bind its acquisition package")
        elif self.package_sha256 is not None or self.resolved_revision != spec.revision:
            raise ValueError("GitHub fetch must resolve the exact approved revision")

    @model_validator(mode="after")
    def fetch_bindings_are_consistent(self) -> Self:
        self._revision_is_consistent()
        _validate_inventory(self.source_id, self.objects, self.archive_inventory, self.objects_aggregate_sha256)
        if self.total_received_bytes != sum(exchange.byte_count for exchange in self.exchanges):
            raise ValueError("received byte count does not match exchanges")
        return self


class AdmissionDecision(BaseModel):
    model_config = STRICT

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["AdmissionDecision"] = "AdmissionDecision"
    decision_id: UUID
    attempt_id: UUID
    generated_at: datetime
    source_id: SourceId
    manifest_identity: Literal["9410d89f00829dd7bfe0d71d4f27a64b59046d8f38c353426e161d7c36415816"]
    disposition: Literal["ADMITTED", "REJECTED", "UNRESOLVED"]
    fetch_receipt_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    admitted_object_sha256: tuple[Sha256, ...]
    reasons: tuple[str, ...]
    quarantine_relative_path: str

    _ids_are_uuid7 = field_validator("decision_id", "attempt_id")(_uuid7)
    _generated_at_is_aware = field_validator("generated_at")(_aware)
    _quarantine_path_is_safe = field_validator("quarantine_relative_path")(_relative)

    @model_validator(mode="after")
    def decision_state_is_consistent(self) -> Self:
        expected = f"quarantine/SOURCE-PLAN-01/{self.source_id}/{self.attempt_id}"
        if self.quarantine_relative_path != expected:
            raise ValueError("decision quarantine path does not match attempt")
        admitted = self.disposition == "ADMITTED"
        if admitted != (self.fetch_receipt_sha256 is not None and bool(self.admitted_object_sha256)):
            raise ValueError("admission evidence contradicts disposition")
        if admitted == bool(self.reasons):
            raise ValueError("admitted decisions have no reasons; other decisions require reasons")
        if len(self.admitted_object_sha256) != len(set(self.admitted_object_sha256)):
            raise ValueError("admitted object hashes must be unique")
        return self


class SourceSnapshot(BaseModel):
    model_config = STRICT

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["SourceSnapshot"] = "SourceSnapshot"
    content_identity: Sha256
    snapshot_identity: str = Field(pattern=r"^[0-9a-f]{64}$")
    disposition: Literal["ADMITTED"] = "ADMITTED"
    source_id: SourceId
    source_spec: PlannedSource
    source_spec_sha256: Sha256
    acquired_at: datetime
    package_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    retrieval_urls: tuple[str, ...] = Field(min_length=1)
    http_metadata_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    objects: tuple[_FetchedObject, ...] = Field(min_length=1)
    archive_inventory: tuple[_ArchiveEntry, ...]
    objects_aggregate_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    allowed_operations: tuple[str, ...] = Field(min_length=1)
    attribution: str
    storage_zone: Literal["AUTHORITATIVE_ARCHIVE"] = "AUTHORITATIVE_ARCHIVE"
    language_identity: str | None
    script_identity: str | None
    edition_identity: str
    passage_identity: str | None
    normalization_state: Literal["NOT_STARTED"] = "NOT_STARTED"
    extraction_code_identity: Literal["bsl.source-acquisition.v1"] = "bsl.source-acquisition.v1"
    upstream_update_policy: Literal["FROZEN_NO_AUTOMATIC_REFRESH"] = "FROZEN_NO_AUTOMATIC_REFRESH"
    review_state: Literal["PENDING_CHATGPT_EXACT_HEAD_REVIEW"] = "PENDING_CHATGPT_EXACT_HEAD_REVIEW"
    manifest_identity: Literal["9410d89f00829dd7bfe0d71d4f27a64b59046d8f38c353426e161d7c36415816"]
    fetch_receipt_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    admission_decision_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    admission_attempt_id: UUID
    fetch_receipt_relative_path: str
    admission_decision_relative_path: str
    snapshot_relative_path: str

    _acquired_at_is_aware = field_validator("acquired_at")(_aware)
    _attempt_is_uuid7 = field_validator("admission_attempt_id")(_uuid7)
    _record_paths_are_safe = field_validator(
        "fetch_receipt_relative_path", "admission_decision_relative_path", "snapshot_relative_path"
    )(_relative)

    @model_validator(mode="after")
    def snapshot_bindings_are_consistent(self) -> Self:
        if self.snapshot_relative_path != f"snapshots/source/{self.source_id}.json":
            raise ValueError("snapshot path does not match source")
        prefix = f"manifests/source/{self.source_id}/{self.admission_attempt_id}"
        if (self.fetch_receipt_relative_path, self.admission_decision_relative_path) != (
            f"{prefix}-fetch-receipt.json",
            f"{prefix}-admission-decision.json",
        ):
            raise ValueError("snapshot authority paths do not match admission attempt")
        if (self.source_id, self.source_spec_sha256) != (
            self.source_spec.source_id,
            _source_spec_sha256(self.source_spec),
        ):
            raise ValueError("snapshot metadata differs from its frozen source specification")
        if any(not url.startswith("https://") for url in self.retrieval_urls):
            raise ValueError("snapshot retrieval URLs must use HTTPS")
        if (self.allowed_operations, self.attribution) != _source_rights(self.source_spec):
            raise ValueError("snapshot rights metadata differs from the approved source plan")
        _validate_inventory(self.source_id, self.objects, self.archive_inventory, self.objects_aggregate_sha256)
        if self.content_identity != _snapshot_content_sha256(self):
            raise ValueError("snapshot content identity does not match admitted content")
        payload = self.model_dump(mode="json", exclude={"snapshot_identity"})
        if self.snapshot_identity != hashlib.sha256(rfc8785.dumps(payload)).hexdigest():
            raise ValueError("snapshot identity does not match its semantic content")
        return self


def _snapshot_content_sha256(snapshot: SourceSnapshot) -> str:
    payload = {
        "source_spec_sha256": snapshot.source_spec_sha256,
        "package_sha256": snapshot.package_sha256,
        "objects": [item.model_dump(mode="json") for item in snapshot.objects],
        "archive_inventory": [item.model_dump(mode="json") for item in snapshot.archive_inventory],
        "language_identity": snapshot.language_identity,
        "script_identity": snapshot.script_identity,
        "edition_identity": snapshot.edition_identity,
        "passage_identity": snapshot.passage_identity,
        "allowed_operations": snapshot.allowed_operations,
        "attribution": snapshot.attribution,
    }
    return hashlib.sha256(rfc8785.dumps(payload)).hexdigest()
