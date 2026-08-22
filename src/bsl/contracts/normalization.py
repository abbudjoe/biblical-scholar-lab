from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import PurePosixPath
from typing import Annotated, Literal, Self
from uuid import UUID

import rfc8785
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, field_validator, model_validator

from bsl.contracts.source_admission import APPROVED_SOURCE_IDS, SourceId

STRICT = ConfigDict(strict=True, frozen=True, extra="forbid", allow_inf_nan=False)
Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


def _relative(value: str) -> str:
    path = PurePosixPath(value)
    if not value or value.startswith("/") or "\\" in value or path.as_posix() != value:
        raise ValueError("path must be a deterministic POSIX relative path")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("relative path contains an unsafe component")
    return value


RelativePath = Annotated[str, Field(min_length=1), AfterValidator(_relative)]


def _uuid7(value: UUID) -> UUID:
    if value.version != 7:
        raise ValueError("identifier must be UUIDv7")
    return value


def _aware(value: datetime) -> datetime:
    if value.utcoffset() is None:
        raise ValueError("timestamp must include an offset")
    return value


class _ObjectBinding(BaseModel):
    model_config = STRICT

    relative_path: RelativePath
    sha256: Sha256
    byte_count: int = Field(ge=0)
    rights_evidence: bool


class _SourceBinding(BaseModel):
    model_config = STRICT

    source_id: SourceId
    snapshot_identity: Sha256
    content_identity: Sha256
    source_spec_sha256: Sha256
    package_sha256: Sha256 | None
    objects: tuple[_ObjectBinding, ...] = Field(min_length=1)
    allowed_operations: tuple[str, ...] = Field(min_length=1)
    attribution: str = Field(min_length=1)
    edition_identity: str = Field(min_length=1)


class _TextView(BaseModel):
    model_config = STRICT

    text: str
    utf8_sha256: Sha256
    byte_count: int = Field(ge=0)

    @model_validator(mode="after")
    def exact_hash(self) -> Self:
        data = self.text.encode("utf-8")
        if (hashlib.sha256(data).hexdigest(), len(data)) != (self.utf8_sha256, self.byte_count):
            raise ValueError("text view hash or byte count differs from UTF-8 bytes")
        return self


class _SblgntEvidence(BaseModel):
    model_config = STRICT

    source_object_sha256: Sha256
    source_object_relative_path: RelativePath
    exact_source_view: _TextView
    unicode_nfc_display_view: _TextView


class _MorphToken(BaseModel):
    model_config = STRICT

    bcv: Literal["040105"]
    part_of_speech: str
    parsing_code: str
    text_alignment: str
    word: str
    normalized_word: str
    lemma: str
    sblgnt_start: int = Field(ge=0)
    sblgnt_end: int = Field(gt=0)

    @model_validator(mode="after")
    def ordered_span(self) -> Self:
        if self.sblgnt_end <= self.sblgnt_start:
            raise ValueError("alignment span must be nonempty")
        return self


class _GrammaticalForm(BaseModel):
    model_config = STRICT

    token_index: int = Field(ge=0)
    source_form: Literal["κατέλαβεν"]
    lemma: Literal["καταλαμβάνω"]
    parsing_code: Literal["3AAI-S--"]
    person: Literal["third"]
    number: Literal["singular"]
    tense: Literal["aorist"]
    voice: Literal["active"]
    mood: Literal["indicative"]


class _MorphologyEvidence(BaseModel):
    model_config = STRICT

    source_object_sha256: Sha256
    source_object_relative_path: RelativePath
    tokens: tuple[_MorphToken, ...] = Field(min_length=1)
    target_verb: _GrammaticalForm


class _TranslationEvidence(BaseModel):
    model_config = STRICT

    source_id: Literal["SP01-SRC-003", "SP01-SRC-004"]
    source_object_sha256: Sha256
    source_object_relative_path: RelativePath
    package_sha256: Sha256 | None
    canonical_realization: _TextView


class _LexicalElement(BaseModel):
    model_config = STRICT

    order: int = Field(ge=0)
    parent_order: int | None = Field(default=None, ge=0)
    tag: str = Field(min_length=1)
    attributes: tuple[tuple[str, str], ...]
    text: str | None
    tail: str | None


class _LexicalEvidence(BaseModel):
    model_config = STRICT

    source_object_sha256: Sha256
    source_object_relative_path: RelativePath
    selector: Literal['entry@n="καταλαμβάνω|G2638"']
    source_entry_utf8: str
    source_entry_sha256: Sha256
    source_entry_byte_count: int = Field(gt=0)
    ordered_structure: tuple[_LexicalElement, ...] = Field(min_length=1)
    locators: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def exact_entry_hash(self) -> Self:
        data = self.source_entry_utf8.encode("utf-8")
        if (hashlib.sha256(data).hexdigest(), len(data)) != (
            self.source_entry_sha256,
            self.source_entry_byte_count,
        ):
            raise ValueError("lexical entry hash or byte count differs from exact UTF-8 span")
        return self


class _PageDependency(BaseModel):
    model_config = STRICT

    regular_font: _ObjectBinding
    italic_font: _ObjectBinding
    license_object: _ObjectBinding
    scholarly_evidence: Literal[False]


def _source_map(sources: tuple[_SourceBinding, ...]) -> dict[SourceId, _SourceBinding]:
    if tuple(source.source_id for source in sources) != APPROVED_SOURCE_IDS:
        raise ValueError("bundle sources must match the exact six-source order")
    if len({source.snapshot_identity for source in sources}) != 6:
        raise ValueError("bundle source snapshot identities must be unique")
    if len({source.content_identity for source in sources}) != 6:
        raise ValueError("bundle source content identities must be unique")
    for source in sources:
        paths = tuple(item.relative_path for item in source.objects)
        hashes = tuple(item.sha256 for item in source.objects)
        if len(set(paths)) != len(paths) or len(set(hashes)) != len(hashes):
            raise ValueError(f"bundle source objects must be unique: {source.source_id}")
    return {source.source_id: source for source in sources}


def _require_object(source: _SourceBinding, path: str, sha256: str) -> None:
    if not any(item.relative_path == path and item.sha256 == sha256 for item in source.objects):
        raise ValueError(f"evidence object does not bind to {source.source_id}")


def _validate_evidence(bundle: John15NormalizationBundle, sources: dict[SourceId, _SourceBinding]) -> None:
    _require_object(
        sources["SP01-SRC-001"], bundle.sblgnt.source_object_relative_path, bundle.sblgnt.source_object_sha256
    )
    _require_object(
        sources["SP01-SRC-002"], bundle.morphgnt.source_object_relative_path, bundle.morphgnt.source_object_sha256
    )
    _require_object(sources["SP01-SRC-003"], bundle.asv.source_object_relative_path, bundle.asv.source_object_sha256)
    _require_object(
        sources["SP01-SRC-004"], bundle.web_classic.source_object_relative_path, bundle.web_classic.source_object_sha256
    )
    _require_object(
        sources["SP01-SRC-005"],
        bundle.abbott_smith.source_object_relative_path,
        bundle.abbott_smith.source_object_sha256,
    )
    if bundle.asv.source_id != "SP01-SRC-003" or bundle.web_classic.source_id != "SP01-SRC-004":
        raise ValueError("translation evidence source identifiers are incorrect")
    web_package = sources["SP01-SRC-004"].package_sha256
    if web_package is None or bundle.web_classic.package_sha256 != web_package:
        raise ValueError("WEB evidence does not bind its admitted package")
    serif = bundle.source_serif
    expected = (
        (serif.regular_font, "TTF/SourceSerif4-Regular.ttf", False),
        (serif.italic_font, "TTF/SourceSerif4-It.ttf", False),
        (serif.license_object, "LICENSE.md", True),
    )
    for item, path, rights_evidence in expected:
        if item.relative_path != path or item.rights_evidence is not rights_evidence:
            raise ValueError("Source Serif dependency path or rights-evidence role is incorrect")
        _require_object(sources["SP01-SRC-006"], item.relative_path, item.sha256)


def _validate_morphology(bundle: John15NormalizationBundle) -> None:
    text = bundle.sblgnt.exact_source_view.text
    cursor = 0
    for token in bundle.morphgnt.tokens:
        gap = text[cursor : token.sblgnt_start]
        if token.sblgnt_start < cursor or gap.strip():
            raise ValueError("MorphGNT spans are not ordered exact whitespace-delimited coverage")
        if text[token.sblgnt_start : token.sblgnt_end] != token.text_alignment:
            raise ValueError("MorphGNT span does not resolve to the exact SBLGNT substring")
        cursor = token.sblgnt_end
    if text[cursor:].strip():
        raise ValueError("MorphGNT spans do not cover the complete SBLGNT source view")
    target = bundle.morphgnt.target_verb
    if target.token_index >= len(bundle.morphgnt.tokens):
        raise ValueError("MorphGNT target token index is out of range")
    token = bundle.morphgnt.tokens[target.token_index]
    if (token.word, token.lemma, token.parsing_code) != (target.source_form, target.lemma, target.parsing_code):
        raise ValueError("MorphGNT target does not bind its token record")


class John15NormalizationBundle(BaseModel):
    """Deterministic John 1:5 evidence graph with atomic source and alignment cross-validation."""

    model_config = STRICT

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["John15NormalizationBundle"] = "John15NormalizationBundle"
    normalization_specification_id: Literal["ACT-VS01-T03-JOHN-1-5-NORMALIZATION-v1"]
    normalization_specification_sha256: Literal["ef3f8bd34d727a89bab5942c550006f0eda408d1f472ba2782fc2ccd519597e9"]
    passage_identity: Literal["John 1:5"]
    sources: tuple[_SourceBinding, ...] = Field(min_length=6, max_length=6)
    sblgnt: _SblgntEvidence
    morphgnt: _MorphologyEvidence
    asv: _TranslationEvidence
    web_classic: _TranslationEvidence
    abbott_smith: _LexicalEvidence
    source_serif: _PageDependency
    normalization_methods: tuple[str, ...] = Field(min_length=1)
    deterministic_limitations: tuple[str, ...] = Field(min_length=1)
    bundle_identity: Sha256

    @model_validator(mode="after")
    def semantic_identity(self) -> Self:
        sources = _source_map(self.sources)
        _validate_evidence(self, sources)
        _validate_morphology(self)
        payload = self.model_dump(mode="json", exclude={"bundle_identity"})
        if self.bundle_identity != hashlib.sha256(rfc8785.dumps(payload)).hexdigest():
            raise ValueError("bundle identity differs from canonical semantic fields")
        return self


class NormalizationReceipt(BaseModel):
    """Operational receipt with disposition, identity, and derived publication-path cross-validation."""

    model_config = STRICT

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["NormalizationReceipt"] = "NormalizationReceipt"
    receipt_identity: UUID
    generated_at: datetime
    implementation_commit: str = Field(pattern=r"^[0-9a-f]{40}$")
    archive_root: str
    disposition: Literal["DRY_RUN_VALIDATED", "PUBLISHED", "VERIFIED_EXISTING"]
    dry_run: bool
    bundle_identity: Sha256
    bundle_canonical_sha256: Sha256
    source_snapshot_identities: tuple[Sha256, ...] = Field(min_length=6, max_length=6)
    source_content_identities: tuple[Sha256, ...] = Field(min_length=6, max_length=6)
    publication_paths: tuple[RelativePath, RelativePath, RelativePath]
    archive_authority_fingerprint_before: Sha256
    archive_authority_fingerprint_after: Sha256
    published: bool
    verified_existing: bool

    _receipt_is_uuid7 = field_validator("receipt_identity")(_uuid7)
    _generated_at_is_aware = field_validator("generated_at")(_aware)

    @model_validator(mode="after")
    def state_is_consistent(self) -> Self:
        expected = {
            "DRY_RUN_VALIDATED": (True, False, False),
            "PUBLISHED": (False, True, False),
            "VERIFIED_EXISTING": (False, False, True),
        }[self.disposition]
        if (self.dry_run, self.published, self.verified_existing) != expected:
            raise ValueError("receipt state contradicts its disposition")
        if self.dry_run and self.archive_authority_fingerprint_before != self.archive_authority_fingerprint_after:
            raise ValueError("dry run changed the archive authority fingerprint")
        expected_paths = (
            f"objects/sha256/{self.bundle_canonical_sha256[:2]}/{self.bundle_canonical_sha256}",
            "snapshots/normalization/john-1-5.json",
            "manifests/normalization/john-1-5/normalization-receipt.json",
        )
        if self.publication_paths != expected_paths:
            raise ValueError("receipt publication paths do not derive from the bundle SHA-256")
        if len(set(self.source_snapshot_identities)) != 6:
            raise ValueError("receipt source snapshot identities must be unique")
        if len(set(self.source_content_identities)) != 6:
            raise ValueError("receipt source content identities must be unique")
        return self
