from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, Literal, Self, cast
from uuid import UUID

import rfc8785
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

STRICT = ConfigDict(strict=True, frozen=True, extra="forbid", allow_inf_nan=False)
Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
ROOT = Path(__file__).parents[3]
SPEC_PATH = ROOT / "design/approved/VS01-T06-page-fixture-spec.json"
RENDERER_PATH = ROOT / "design/approved/VS01-T06-renderer-authority.json"
SPEC_SHA256 = "dd76d124b0ab9c42cb3551e1afd5a9e0326ac402977ae3f4625d9092fd80b285"
DESIGN_SHA256 = "188915da1f62812bf88eb9c5168dc07246b0a411990857663b12d1b7446eca8c"
SCENE_IDENTITY = "ed19a7d564a00da054a26347f750b799e4a2b489412bd47c6159d1ca2097bcea"
ERRATUM_SHA256 = "fe5accbe92a40078122099a236a7569e8dd80de8de1f2d764ecec15d896cfd38"
ACTIVATION_SHA256 = "73ba0a542958fadbc8d260d0de8cf5160aac0e9d35555d82027c4962d0bed986"
RENDERER_SHA256 = "3ac7df8910bf4ea6a630a8f5e222483541121458620a80edf5bab20d067623de"
BASE_SHA256 = "2c0cebc7245eb1032b2b1e4c0ee16e6f74dec47e6a53d8f49c4b9d0a847abbfb"
DEGRADED_SHA256 = "cb47073c8e40da01285d90d26ebb7144b34047a2cde8f58e4ba0d1f2cfb67fce"
BASE_BYTES = 83499
DEGRADED_BYTES = 94398
FIXTURE_IDENTITY = "929ddc1c1aeb1e976a70cfbceb238f0ef6a55e8ca1b354a0210463cec50b4d9b"
FIXTURE_JSON_SHA256 = "c8cfc4eafee6b0a16fc2e0442190782a35e2b03477a619854105d5272f08417f"
FIXTURE_JSON_BYTES = 23185


def _authority(path: Path, expected_sha: str) -> dict[str, Any]:
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected_sha:
        raise ValueError(f"frozen authority differs: {path.name}")
    value: Any = json.loads(data)
    if not isinstance(value, dict):
        raise ValueError(f"frozen authority is not an object: {path.name}")
    return cast(dict[str, Any], value)


def load_page_spec() -> dict[str, Any]:
    spec = _authority(SPEC_PATH, SPEC_SHA256)
    checks = (
        spec.get("spec_id") == "VS01-T06-PAGE-FIXTURE-SPEC-v1",
        spec.get("scene_spec_identity") == SCENE_IDENTITY,
        len(spec.get("scene", {}).get("regions", ())) == 7,
        len(spec.get("scene", {}).get("extractions", ())) == 14,
        len(spec.get("public_contracts", ())) == 4,
    )
    if not all(checks):
        raise ValueError("frozen page specification identity or counts differ")
    return spec


def load_renderer_authority() -> dict[str, Any]:
    value = _authority(RENDERER_PATH, RENDERER_SHA256)
    if value.get("platform") != "linux/amd64" or value.get("characterization", {}).get("fresh_container_count") != 2:
        raise ValueError("renderer authority characterization differs")
    return value


def _exact_schema(title: str, values: list[dict[str, Any]]) -> Any:
    def apply(schema: dict[str, Any]) -> None:
        schema.clear()
        schema.update(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "title": title,
                "oneOf": [{"const": value} for value in values],
            }
        )

    return apply


def _dump_without_none(model: BaseModel) -> dict[str, Any]:
    return model.model_dump(mode="json", exclude_none=True)


def _region_schema(schema: dict[str, Any]) -> None:
    _exact_schema("John15PageRegionGroundTruth", load_page_spec()["scene"]["regions"])(schema)


def _extraction_schema(schema: dict[str, Any]) -> None:
    _exact_schema("John15PageExtractionGroundTruth", load_page_spec()["scene"]["extractions"])(schema)


class John15PageRegionGroundTruth(BaseModel):
    """One of the seven exact authored regions in the frozen scene."""

    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
        allow_inf_nan=False,
        json_schema_extra=_region_schema,
    )

    region_id: str
    pixel_bbox_xywh: tuple[int, int, int, int]
    text: str
    benchmark_role: str
    functional_class: str
    authority_class: str
    canonicality: str | None = None
    style_id: str
    parent_group_id: str
    z_index: int
    source_binding: str
    t04_evidence_id: str | None = None
    t04_claim_bindings: tuple[str, ...] | None = None
    annotation_target_region_id: str | None = None
    normalized_bbox_xyxy: tuple[str, str, str, str]
    benchmark_reading_order_index: int
    base_legibility: str

    @model_validator(mode="after")
    def exact_region(self) -> Self:
        if _dump_without_none(self) not in load_page_spec()["scene"]["regions"]:
            raise ValueError("region differs from the exact frozen scene")
        return self


class John15PageExtractionGroundTruth(BaseModel):
    """One exact authored visual extraction with lookup kept separate."""

    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
        allow_inf_nan=False,
        json_schema_extra=_extraction_schema,
    )

    extraction_id: str
    view_id: str
    region_id: str
    ground_truth_method: str
    visual_legibility: str
    visual_transcription: str
    canonical_lookup: dict[str, Any] | None
    ocr_or_vlm_used: bool
    scorer_only_underlying_text: str

    @model_validator(mode="after")
    def exact_extraction(self) -> Self:
        if self.model_dump(mode="json") not in load_page_spec()["scene"]["extractions"]:
            raise ValueError("extraction differs from the exact frozen scene")
        if self.ocr_or_vlm_used:
            raise ValueError("OCR or VLM cannot create page ground truth")
        return self


class _Scene(BaseModel):
    model_config = STRICT

    fixture_id: Literal["SP01-DER-002"]
    canvas: dict[str, Any]
    coordinate_spaces: tuple[dict[str, Any], ...]
    page_label: str
    styles: dict[str, Any]
    display_only_graphics: tuple[dict[str, Any], ...]
    regions: tuple[John15PageRegionGroundTruth, ...] = Field(min_length=7, max_length=7)
    region_groups: tuple[dict[str, Any], ...]
    reading_orders: dict[str, Any]
    relationships: tuple[dict[str, Any], ...]
    views: tuple[dict[str, Any], ...]
    extractions: tuple[John15PageExtractionGroundTruth, ...] = Field(min_length=14, max_length=14)

    @model_validator(mode="after")
    def exact_scene(self) -> Self:
        actual = self.model_dump(mode="json")
        actual["regions"] = [_dump_without_none(region) for region in self.regions]
        if actual != load_page_spec()["scene"]:
            raise ValueError("scene differs from the exact frozen authority")
        return self


def _fixture_payload() -> dict[str, Any]:
    spec, renderer = load_page_spec(), load_renderer_authority()
    return {
        "schema_version": "1.0",
        "contract": "John15SyntheticPageFixture",
        "fixture_id": "SP01-DER-002",
        "scene_spec_identity": SCENE_IDENTITY,
        "frozen_authority": {
            "design_sha256": DESIGN_SHA256,
            "spec_sha256": SPEC_SHA256,
            "erratum_sha256": ERRATUM_SHA256,
            "activation_sha256": ACTIVATION_SHA256,
        },
        "upstream_authority": {
            "t03": renderer["t03_authority"],
            "t04": spec["upstream_authority"]["t04"],
            "t05": spec["upstream_authority"]["t05"],
        },
        "renderer_authority_sha256": RENDERER_SHA256,
        "renderer_authority": renderer,
        "raster_contract": spec["raster_contract"],
        "scene": spec["scene"],
        "ground_truth_boundary": spec["ground_truth_boundary"],
        "rights_and_public_display": spec["rights_and_public_display"],
        "raster_assets": [
            {
                "view_id": "base-page",
                "path": "fixtures/VS01-T06/john-1-5-base-page.png",
                "sha256": BASE_SHA256,
                "byte_count": BASE_BYTES,
            },
            {
                "view_id": "degraded-illegibility-v1",
                "path": "fixtures/VS01-T06/john-1-5-degraded-illegibility-v1.png",
                "sha256": DEGRADED_SHA256,
                "byte_count": DEGRADED_BYTES,
            },
        ],
        "attribution": spec["rights_and_public_display"]["required_attribution_bundle"],
        "operation_counts": {
            "archive_writes": 0,
            "database_writes": 0,
            "raw_non_font_source_reads": 0,
            "ocr_invocations": 0,
            "vlm_invocations": 0,
            "model_invocations": 0,
            "benchmark_executions": 0,
        },
    }


def fixture_identity() -> str:
    identity = hashlib.sha256(rfc8785.dumps(_fixture_payload())).hexdigest()
    if identity != FIXTURE_IDENTITY:
        raise ValueError("realized fixture identity differs")
    return identity


def _fixture_schema(schema: dict[str, Any]) -> None:
    payload = _fixture_payload() | {"fixture_identity": fixture_identity()}
    for field, value in payload.items():
        schema["properties"][field] = {"const": value}
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"


class John15SyntheticPageFixture(BaseModel):
    """Exact realized scene, raster identities, authorities, and rights."""

    model_config = ConfigDict(
        strict=True, frozen=True, extra="forbid", allow_inf_nan=False, json_schema_extra=_fixture_schema
    )

    schema_version: Literal["1.0"]
    contract: Literal["John15SyntheticPageFixture"]
    fixture_id: Literal["SP01-DER-002"]
    scene_spec_identity: Sha256
    frozen_authority: dict[str, Sha256]
    upstream_authority: dict[str, Any]
    renderer_authority_sha256: Sha256
    renderer_authority: dict[str, Any]
    raster_contract: dict[str, Any]
    scene: _Scene
    ground_truth_boundary: dict[str, Any]
    rights_and_public_display: dict[str, Any]
    raster_assets: tuple[dict[str, Any], dict[str, Any]]
    attribution: tuple[str, str, str]
    operation_counts: dict[str, int]
    fixture_identity: Sha256

    @model_validator(mode="after")
    def exact_fixture(self) -> Self:
        actual = self.model_dump(mode="json")
        identity = actual.pop("fixture_identity")
        actual["scene"] = load_page_spec()["scene"]
        if actual != _fixture_payload() or identity != hashlib.sha256(rfc8785.dumps(actual)).hexdigest():
            raise ValueError("fixture differs from the exact realized authority")
        return self


def build_fixture() -> John15SyntheticPageFixture:
    payload = _fixture_payload()
    return John15SyntheticPageFixture.model_validate_json(
        rfc8785.dumps(payload | {"fixture_identity": fixture_identity()})
    )


def canonical_fixture_bytes() -> bytes:
    build_fixture()
    return rfc8785.dumps(_fixture_payload() | {"fixture_identity": fixture_identity()})


def _relative_paths(values: tuple[str, ...]) -> tuple[str, ...]:
    for value in values:
        path = PurePosixPath(value)
        if value.startswith("/") or "\\" in value or path.as_posix() != value or ".." in path.parts:
            raise ValueError("publication path must be a safe POSIX relative path")
    return values


def _receipt_schema(schema: dict[str, Any]) -> None:
    constants = {
        "fixture_identity": FIXTURE_IDENTITY,
        "fixture_json_sha256": FIXTURE_JSON_SHA256,
        "base_png_sha256": BASE_SHA256,
        "degraded_png_sha256": DEGRADED_SHA256,
        "renderer_authority_sha256": RENDERER_SHA256,
        "publication_paths": list(publication_paths(FIXTURE_JSON_SHA256)),
    }
    for field, value in constants.items():
        schema["properties"][field] = {"const": value}
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"


class John15SyntheticPagePublicationReceipt(BaseModel):
    """UUIDv7 receipt for dry-run validation or receipt-last publication."""

    model_config = ConfigDict(
        strict=True, frozen=True, extra="forbid", allow_inf_nan=False, json_schema_extra=_receipt_schema
    )

    schema_version: Literal["1.0"] = "1.0"
    contract: Literal["John15SyntheticPagePublicationReceipt"] = "John15SyntheticPagePublicationReceipt"
    receipt_identity: UUID
    generated_at: datetime
    implementation_commit: str = Field(pattern=r"^[0-9a-f]{40}$")
    archive_root: str
    disposition: Literal["DRY_RUN_VALIDATED", "PUBLISHED", "VERIFIED_EXISTING"]
    dry_run: bool
    fixture_identity: Sha256
    fixture_json_sha256: Sha256
    base_png_sha256: Sha256
    degraded_png_sha256: Sha256
    renderer_authority_sha256: Sha256
    publication_paths: tuple[str, str, str, str, str]
    authority_fingerprint_before: Sha256
    authority_fingerprint_after: Sha256
    archive_writes: int = Field(ge=0)
    database_writes: Literal[0]
    raw_non_font_source_reads: Literal[0]
    ocr_invocations: Literal[0]
    vlm_invocations: Literal[0]
    model_invocations: Literal[0]
    benchmark_executions: Literal[0]
    published: bool
    verified_existing: bool

    @field_validator("receipt_identity")
    @classmethod
    def uuid7_only(cls, value: UUID) -> UUID:
        if value.version != 7:
            raise ValueError("receipt identity must be UUIDv7")
        return value

    @field_validator("generated_at")
    @classmethod
    def aware_only(cls, value: datetime) -> datetime:
        if value.utcoffset() is None:
            raise ValueError("generated_at must include an offset")
        return value

    @model_validator(mode="after")
    def state_and_authority(self) -> Self:
        state = {
            "DRY_RUN_VALIDATED": (True, False, False, 0),
            "PUBLISHED": (False, True, False, 5),
            "VERIFIED_EXISTING": (False, False, True, 0),
        }[self.disposition]
        expected_paths = publication_paths(self.fixture_json_sha256)
        authority = (
            self.fixture_identity,
            self.fixture_json_sha256,
            self.base_png_sha256,
            self.degraded_png_sha256,
            self.renderer_authority_sha256,
        )
        expected = (fixture_identity(), FIXTURE_JSON_SHA256, BASE_SHA256, DEGRADED_SHA256, RENDERER_SHA256)
        if (self.dry_run, self.published, self.verified_existing, self.archive_writes) != state:
            raise ValueError("receipt state contradicts disposition")
        if authority != expected or self.publication_paths != expected_paths:
            raise ValueError("receipt does not bind the exact fixture publication")
        if self.authority_fingerprint_before != self.authority_fingerprint_after:
            raise ValueError("read-only authority fingerprint changed")
        return self


def publication_paths(fixture_sha: str) -> tuple[str, str, str, str, str]:
    return _relative_paths(
        (
            f"objects/sha256/{BASE_SHA256[:2]}/{BASE_SHA256}",
            f"objects/sha256/{DEGRADED_SHA256[:2]}/{DEGRADED_SHA256}",
            f"objects/sha256/{fixture_sha[:2]}/{fixture_sha}",
            "snapshots/page/john-1-5-synthetic-fixture.json",
            "manifests/page/john-1-5-synthetic-fixture/page-fixture-receipt.json",
        )
    )  # type: ignore[return-value]
