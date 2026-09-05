from __future__ import annotations

import hashlib
from typing import Literal, Self

import rfc8785
from pydantic import BaseModel, ConfigDict, model_validator

from bsl.contracts.source_admission import Sha256, SourceSnapshot

STRICT = ConfigDict(
    strict=True,
    frozen=True,
    extra="forbid",
    allow_inf_nan=False,
    json_schema_extra={"$schema": "https://json-schema.org/draft/2020-12/schema"},
)
ROSTER = (
    "tan:john.13.1:to-the-end",
    "tan:john.13.8:no-share-with-me",
    "tan:john.13.10:bathed-versus-washed",
    "tan:john.13.15:example-or-pattern",
    "tan:john.13.17:blessed-or-happy",
    "tan:john.13.19:i-am-or-i-am-he",
    "tan:john.13.30:night-symbolism",
)
Disposition = Literal[
    "VERIFIED_FOR_PACKAGE_CANDIDATE",
    "NEEDS_EDITORIAL_REVISION",
    "SOURCE_OR_RIGHTS_GAP",
    "REJECTED_NOT_TRANSLATION_NUANCE",
]
REJECTION = (
    "The translated phrase is direct. The proposed additional value is literary symbolism rather than a "
    "lexical, grammatical, textual, or translation-choice issue."
)


class _FileAuthority(BaseModel):
    model_config = STRICT
    repository: str
    commit: str
    tree: str
    source_path: str
    git_blob: str
    sha256: Sha256
    byte_count: int


class _Evidence(BaseModel):
    model_config = STRICT
    assertion_id: str
    source_id: str
    snapshot_identity: Sha256
    component: str
    component_sha256: Sha256
    locator: str
    value: str
    value_sha256: Sha256
    attribution: str
    allowed_operations: tuple[str, ...]

    @model_validator(mode="after")
    def exact_value(self) -> Self:
        if hashlib.sha256(self.value.encode()).hexdigest() != self.value_sha256:
            raise ValueError("source value identity mismatch")
        return self


class _ClaimSupport(BaseModel):
    model_config = STRICT
    claim_id: str
    statement: str
    assertion_ids: tuple[str, ...]
    assessment: str


class _Decision(BaseModel):
    model_config = STRICT
    annotation_id: str
    revision: int
    projection_sha256: Sha256
    disposition: Disposition
    reason: str
    unsupported_statement: str | None = None
    suggested_replacement: str | None = None
    missing_sources: tuple[str, ...] = ()
    checked_sources: tuple[str, ...] = ()
    notes_bytes_unchanged: Literal[True] = True
    substitution_or_acquisition: Literal[False] = False
    evidence: tuple[_Evidence, ...] = ()
    claims: tuple[_ClaimSupport, ...] = ()

    @model_validator(mode="after")
    def coherent_decision(self) -> Self:
        if self.annotation_id == ROSTER[-1] and (self.disposition, self.reason, self.evidence) != (
            "REJECTED_NOT_TRANSLATION_NUANCE",
            REJECTION,
            (),
        ):
            raise ValueError("fixed John 13:30 rejection differs")
        if self.disposition == "NEEDS_EDITORIAL_REVISION" and not (
            self.unsupported_statement and self.suggested_replacement
        ):
            raise ValueError("editorial revision lacks exact statement/replacement")
        if self.disposition == "SOURCE_OR_RIGHTS_GAP" and not (self.missing_sources and self.unsupported_statement):
            raise ValueError("source gap lacks required authority and statement")
        if self.disposition == "VERIFIED_FOR_PACKAGE_CANDIDATE":
            ids = {e.assertion_id for e in self.evidence}
            if not self.claims or any(not c.assertion_ids or not set(c.assertion_ids) <= ids for c in self.claims):
                raise ValueError("claim support is incomplete")
            if self.missing_sources or self.unsupported_statement:
                raise ValueError("verified record contains a gap")
        return self


class TranslationAnnotationCompilationReceipt(BaseModel):
    model_config = STRICT
    schema_version: Literal["translation-annotation-compilation-receipt-v1"]
    receipt_identity: Sha256
    activation_sha256: Literal["6b3ed11fbd47113bdc7e5ec8abe3b9491119e0d06377b30c7ccdd389dc4e22d4"]
    compiler_version: Literal["j13-lab-01-v1"]
    compiler_files: tuple[tuple[str, Sha256], ...]
    lab_base: Literal["dca0d48e38528037f8c5bb7f510705f3324714de"]
    lab_tree: Literal["261b0fcbddf7462ae9a98f924aeab84891edb653"]
    upstream_authority_sha256: Sha256
    upstream_files: tuple[_FileAuthority, ...]
    notes_tree_chain: tuple[tuple[str, str], ...]
    source_snapshots: tuple[SourceSnapshot, ...]
    decisions: tuple[_Decision, ...]
    unread_records: tuple[Literal["tan:john.13.2:during-supper", "tan:john.13.31:glorified-aorist"], ...]
    accepted_roster: tuple[str, ...]
    excluded_roster: tuple[tuple[str, Disposition, str], ...]
    package_series_id: Literal["tap:j13-pilot-01"]
    package_revision: Literal[1]
    package_path: Literal["artifacts/J13-LAB-01/translation-annotation-package.j13-pilot-01.candidate.json"]
    package_sha256: Sha256
    package_bytes: int
    package_schema_conformance: Literal["PASS"]
    non_activatable: Literal[True]
    remaining_gate: Literal["Owner package review before Biblos admission; independent exact-head review before merge."]
    double_build_package_hashes: tuple[Sha256, Sha256]
    double_build_models_and_decisions_equal: Literal[True]
    double_build_receipt_bytes_equal: Literal[True]
    archive_unchanged: Literal[True]
    prohibited_operation_counts: tuple[tuple[str, Literal[0]], ...]
    limitations: tuple[str, ...]

    @model_validator(mode="after")
    def receipt_bindings(self) -> Self:
        if tuple(d.annotation_id for d in self.decisions) != ROSTER:
            raise ValueError("receipt decision roster differs")
        accepted = tuple(d.annotation_id for d in self.decisions if d.disposition == "VERIFIED_FOR_PACKAGE_CANDIDATE")
        excluded = tuple(
            (d.annotation_id, d.disposition, d.reason) for d in self.decisions if d.annotation_id not in accepted
        )
        if (self.accepted_roster, self.excluded_roster) != (accepted, excluded):
            raise ValueError("receipt inclusion roster differs from decisions")
        if self.double_build_package_hashes != (self.package_sha256, self.package_sha256):
            raise ValueError("double-build package binding differs")
        payload = self.model_dump(mode="json", exclude={"receipt_identity"})
        if self.receipt_identity != hashlib.sha256(rfc8785.dumps(payload)).hexdigest():
            raise ValueError("receipt identity mismatch")
        return self
