from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, Literal, Self
from uuid import UUID

import rfc8785
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, field_validator, model_validator

STRICT = ConfigDict(strict=True, frozen=True, extra="forbid", allow_inf_nan=False)
Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
SPEC_SHA256 = "48254fb7a8f68bfe6baf09f8fe33781c2dd5bf848a7fd2eb782fbc8da9588936"
DESIGN_SHA256 = "d979e04221bebba70671fa73311a07347058e652592cefaa424d4bb4675b3188"
SPEC_PATH = Path(__file__).parents[3] / "design/approved/VS01-T04-claim-evidence-spec.json"
FROZEN_FIELDS = (
    "comparison_frame",
    "difference_unit",
    "evidence_items",
    "claims",
    "claim_evidence_links",
    "diagnoses",
    "accepted_alternatives",
    "evidence_sufficiency",
    "review_vector",
    "rights_projection",
    "public_display_constraints",
    "known_limitations",
    "prohibited_inferences",
)


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


def load_frozen_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != SPEC_SHA256:
        raise ValueError("frozen claim/evidence specification hash differs from approved authority")
    try:
        spec = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("frozen claim/evidence specification is invalid JSON") from None
    expected = (
        spec.get("schema_version") == "1.0",
        spec.get("spec_id") == "VS01-T04-CLAIM-EVIDENCE-SPEC-v1",
        spec.get("design_id") == "VS01-T04",
        spec.get("status") == "FROZEN_DESIGN_IMPLEMENTATION_NOT_AUTHORIZED",
        len(spec.get("evidence_items", ())) == 12,
        len(spec.get("claims", ())) == 16,
        len(spec.get("claim_evidence_links", ())) == 34,
        len(spec.get("diagnoses", ())) == 3,
        len(spec.get("accepted_alternatives", ())) == 3,
        len(spec.get("prohibited_inferences", ())) == 17,
        len(spec.get("public_contracts", ())) == 2,
    )
    if not all(expected):
        raise ValueError("frozen claim/evidence specification metadata or counts differ")
    return spec


class _InputAuthority(BaseModel):
    model_config = STRICT

    contract: Literal["John15NormalizationBundle"]
    bundle_identity: Literal["9e147d9e218564d744360fd94b794758d1cc3e98e3826380008939eb0c494f32"]
    bundle_canonical_sha256: Literal["397f7c8908bf8e8533b23eb808ab7c0ede796c95d7b49451fa92f40261ee19d6"]
    normalization_specification_id: Literal["ACT-VS01-T03-JOHN-1-5-NORMALIZATION-v1"]
    normalization_specification_sha256: Literal["ef3f8bd34d727a89bab5942c550006f0eda408d1f472ba2782fc2ccd519597e9"]
    normalization_receipt_identity: UUID
    normalization_receipt_file_sha256: Sha256
    source_snapshot_identities: tuple[Sha256, ...] = Field(min_length=6, max_length=6)
    source_content_identities: tuple[Sha256, ...] = Field(min_length=6, max_length=6)

    @model_validator(mode="after")
    def unique_source_authority(self) -> Self:
        if len(set(self.source_snapshot_identities)) != 6 or len(set(self.source_content_identities)) != 6:
            raise ValueError("T03 source authority identities must be unique")
        return self


class John15TranslationNuanceEvidencePacket(BaseModel):
    """Exact frozen John 1:5 claim/evidence graph bound to published T03 authority."""

    model_config = STRICT

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["John15TranslationNuanceEvidencePacket"] = "John15TranslationNuanceEvidencePacket"
    packet_id: Literal["SP01-DER-001"]
    frozen_design_id: Literal["VS01-T04"]
    frozen_design_sha256: Literal["d979e04221bebba70671fa73311a07347058e652592cefaa424d4bb4675b3188"]
    frozen_claim_evidence_spec_id: Literal["VS01-T04-CLAIM-EVIDENCE-SPEC-v1"]
    frozen_claim_evidence_spec_sha256: Literal["48254fb7a8f68bfe6baf09f8fe33781c2dd5bf848a7fd2eb782fbc8da9588936"]
    input_authority: _InputAuthority
    comparison_frame: dict[str, Any]
    difference_unit: dict[str, Any]
    evidence_items: tuple[dict[str, Any], ...]
    claims: tuple[dict[str, Any], ...]
    claim_evidence_links: tuple[dict[str, Any], ...]
    diagnoses: tuple[dict[str, Any], ...]
    accepted_alternatives: tuple[dict[str, Any], ...]
    evidence_sufficiency: dict[str, Any]
    review_vector: dict[str, Any]
    rights_projection: dict[str, Any]
    public_display_constraints: tuple[str, ...]
    known_limitations: tuple[str, ...]
    prohibited_inferences: tuple[str, ...]
    packet_identity: Sha256

    @model_validator(mode="after")
    def frozen_graph_and_identity(self) -> Self:
        expected = load_frozen_spec()
        actual = self.model_dump(mode="json")
        if any(actual[field] != expected[field] for field in FROZEN_FIELDS):
            raise ValueError("packet claim/evidence graph differs from the exact frozen specification")
        semantic = self.model_dump(mode="json", exclude={"packet_identity"})
        if self.packet_identity != hashlib.sha256(rfc8785.dumps(semantic)).hexdigest():
            raise ValueError("packet identity differs from canonical semantic fields")
        return self


class John15TranslationNuanceEvidenceReceipt(BaseModel):
    """Operational receipt for dry-run validation or receipt-last packet publication."""

    model_config = STRICT

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["John15TranslationNuanceEvidenceReceipt"] = "John15TranslationNuanceEvidenceReceipt"
    receipt_identity: UUID
    generated_at: datetime
    implementation_commit: str = Field(pattern=r"^[0-9a-f]{40}$")
    archive_root: str
    disposition: Literal["DRY_RUN_VALIDATED", "PUBLISHED", "VERIFIED_EXISTING"]
    dry_run: bool
    input_bundle_identity: Literal["9e147d9e218564d744360fd94b794758d1cc3e98e3826380008939eb0c494f32"]
    input_bundle_canonical_sha256: Literal["397f7c8908bf8e8533b23eb808ab7c0ede796c95d7b49451fa92f40261ee19d6"]
    input_normalization_receipt_identity: UUID
    input_normalization_receipt_file_sha256: Sha256
    packet_identity: Sha256
    packet_canonical_sha256: Sha256
    publication_paths: tuple[RelativePath, RelativePath, RelativePath]
    input_authority_fingerprint_before: Sha256
    input_authority_fingerprint_after: Sha256
    published: bool
    verified_existing: bool

    _receipt_is_uuid7 = field_validator("receipt_identity")(_uuid7)
    _generated_at_is_aware = field_validator("generated_at")(_aware)

    @model_validator(mode="after")
    def state_and_paths(self) -> Self:
        state = {
            "DRY_RUN_VALIDATED": (True, False, False),
            "PUBLISHED": (False, True, False),
            "VERIFIED_EXISTING": (False, False, True),
        }[self.disposition]
        if (self.dry_run, self.published, self.verified_existing) != state:
            raise ValueError("receipt state contradicts its disposition")
        if self.dry_run and self.input_authority_fingerprint_before != self.input_authority_fingerprint_after:
            raise ValueError("dry run changed T03 input authority")
        expected = (
            f"objects/sha256/{self.packet_canonical_sha256[:2]}/{self.packet_canonical_sha256}",
            "snapshots/evidence/john-1-5-translation-nuance.json",
            "manifests/evidence/john-1-5-translation-nuance/evidence-packet-receipt.json",
        )
        if self.publication_paths != expected:
            raise ValueError("receipt publication paths do not derive from packet SHA-256")
        return self
