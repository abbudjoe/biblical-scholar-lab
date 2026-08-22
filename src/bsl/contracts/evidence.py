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
INPUT_AUTHORITY_SHA256 = "3ac15fc7b52ac669750db9ebf2b78860a2e535a92ac6c98143f03f6b62dc265b"
PACKET_IDENTITY = "aebcbb50fc8383f2f4f395bc71116563325c1fde237427dc8c1bc8140e8ebe31"
PACKET_SHA256 = "9f81621785924161cc4861e2af9f010bd18e822b60199d62a6327eff44ea0409"
T03_RECEIPT_IDENTITY = "01a02a37-79f8-7f29-abf7-a2dd9d7161ba"
T03_RECEIPT_SHA256 = "e4871e859481614da6d4f52e77fa41e35234884b9f5baacad68c4855e2ed6af2"
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
EXACT_INPUT_AUTHORITY = {
    "contract": "John15NormalizationBundle",
    "bundle_identity": "9e147d9e218564d744360fd94b794758d1cc3e98e3826380008939eb0c494f32",
    "bundle_canonical_sha256": "397f7c8908bf8e8533b23eb808ab7c0ede796c95d7b49451fa92f40261ee19d6",
    "normalization_specification_id": "ACT-VS01-T03-JOHN-1-5-NORMALIZATION-v1",
    "normalization_specification_sha256": "ef3f8bd34d727a89bab5942c550006f0eda408d1f472ba2782fc2ccd519597e9",
    "normalization_receipt_identity": T03_RECEIPT_IDENTITY,
    "normalization_receipt_file_sha256": T03_RECEIPT_SHA256,
    "source_snapshot_identities": [
        "74a7ea1a9eed418e20eaa67ad066adc22f6a0989d60dd634bd1a3cf0ae86fd31",
        "865877202c118c7df2d6159768393a13d2ee390dc298671df631dec4275cd586",
        "271525f7f326fc6f4490d341c09cb70c7caabda86f88c0cc356c5cd63b82bf8c",
        "8d465020ab17ff07670ad6324a8d9bab9f510db2c626a3d29b8d1983aea79eb8",
        "5ef75e98d5f0c9b8455dc875a66ee06cbd7bbf5da01a6daab240083effb11bb9",
        "f58b3699e4a06b2e7de393772a33d0aa73a3e841f1587759787b25855805e3ab",
    ],
    "source_content_identities": [
        "1ea5a49223f65d380efcbb6829a644c958d59da7f9dd06d21a1d8d3ceab2603d",
        "d8d39c61bc496d1e9da9b11db18834d9da3ca02b2c081778dfec2e2a2c94a5ac",
        "61652c227fb0b35e860aea271961b8cca9be92a140ca776a4432cc46e19ec3ba",
        "9ea1f23bf0d532c392893c2b0f4c46c3f07ec18e6b23cdc6ece6efd5c5b895a0",
        "0c5f74d4ed4177bf73f92dec336688d9c9d655dad03ceb38f5b76f0a8f8fbae3",
        "03c6fcd8350e12f50eacaca9afb9a7ec1a73b8323bd95c5a683685ea0e1dc2e5",
    ],
}


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


def _packet_schema(schema: dict[str, Any]) -> None:
    spec = load_frozen_spec()
    for field in FROZEN_FIELDS:
        schema["properties"][field] = {"const": spec[field]}
    schema["properties"]["input_authority"] = {"const": EXACT_INPUT_AUTHORITY}
    schema["properties"]["packet_identity"] = {"const": PACKET_IDENTITY}


def _receipt_schema(schema: dict[str, Any]) -> None:
    constants = {
        "input_normalization_receipt_identity": T03_RECEIPT_IDENTITY,
        "input_normalization_receipt_file_sha256": T03_RECEIPT_SHA256,
        "packet_identity": PACKET_IDENTITY,
        "packet_canonical_sha256": PACKET_SHA256,
    }
    for field, value in constants.items():
        schema["properties"][field] = {"const": value}


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
        digest = hashlib.sha256(rfc8785.dumps(self.model_dump(mode="json"))).hexdigest()
        if digest != INPUT_AUTHORITY_SHA256:
            raise ValueError("T03 input authority differs from the exact canonical authority")
        return self


class John15TranslationNuanceEvidencePacket(BaseModel):
    """Exact frozen John 1:5 claim/evidence graph bound to published T03 authority."""

    model_config = ConfigDict(
        strict=True, frozen=True, extra="forbid", allow_inf_nan=False, json_schema_extra=_packet_schema
    )

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
        if (
            self.packet_identity != PACKET_IDENTITY
            or self.packet_identity != hashlib.sha256(rfc8785.dumps(semantic)).hexdigest()
        ):
            raise ValueError("packet identity differs from canonical semantic fields")
        if hashlib.sha256(rfc8785.dumps(actual)).hexdigest() != PACKET_SHA256:
            raise ValueError("packet canonical SHA-256 differs from the exact packet")
        return self


class John15TranslationNuanceEvidenceReceipt(BaseModel):
    """Operational receipt for dry-run validation or receipt-last packet publication."""

    model_config = ConfigDict(
        strict=True, frozen=True, extra="forbid", allow_inf_nan=False, json_schema_extra=_receipt_schema
    )

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
        if self.input_authority_fingerprint_before != self.input_authority_fingerprint_after:
            raise ValueError("receipt input-authority fingerprints differ")
        authority = (
            str(self.input_normalization_receipt_identity),
            self.input_normalization_receipt_file_sha256,
            self.packet_identity,
            self.packet_canonical_sha256,
        )
        if authority != (T03_RECEIPT_IDENTITY, T03_RECEIPT_SHA256, PACKET_IDENTITY, PACKET_SHA256):
            raise ValueError("receipt does not bind the exact T03 authority and packet")
        expected = (
            f"objects/sha256/{self.packet_canonical_sha256[:2]}/{self.packet_canonical_sha256}",
            "snapshots/evidence/john-1-5-translation-nuance.json",
            "manifests/evidence/john-1-5-translation-nuance/evidence-packet-receipt.json",
        )
        if self.publication_paths != expected:
            raise ValueError("receipt publication paths do not derive from packet SHA-256")
        return self
