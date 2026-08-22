from __future__ import annotations

import hashlib
import os
import re
import stat
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from uuid import UUID

import rfc8785
from pydantic import ValidationError
from uuid6 import uuid7

from bsl.contracts.archive import ArchiveInitializationReceipt, ArchiveRootMarker
from bsl.contracts.evidence import (
    DESIGN_SHA256,
    EXACT_INPUT_AUTHORITY,
    FROZEN_FIELDS,
    SPEC_SHA256,
    John15TranslationNuanceEvidencePacket,
    John15TranslationNuanceEvidenceReceipt,
    load_frozen_spec,
)
from bsl.contracts.normalization import John15NormalizationBundle, NormalizationReceipt
from bsl.infrastructure.evidence_store import (
    canonical_packet_bytes,
    evidence_stage_path,
    prepare_publication,
    publication_paths,
    publish_evidence,
)

CANONICAL_ARCHIVE_ROOT = Path("/Volumes/BSL-Archive/BiblicalScholarLab")
BUNDLE_IDENTITY = "9e147d9e218564d744360fd94b794758d1cc3e98e3826380008939eb0c494f32"
BUNDLE_SHA256 = "397f7c8908bf8e8533b23eb808ab7c0ede796c95d7b49451fa92f40261ee19d6"
T03_IMPLEMENTATION_COMMIT = "5a558f9ff1049295985da88096d36542283b4e50"
T03_OBJECT = f"objects/sha256/{BUNDLE_SHA256[:2]}/{BUNDLE_SHA256}"
T03_SNAPSHOT = "snapshots/normalization/john-1-5.json"
T03_RECEIPT = "manifests/normalization/john-1-5/normalization-receipt.json"
GREEK_CLAUSE = "καὶ ἡ σκοτία αὐτὸ οὐ κατέλαβεν."
NewUuid = Callable[[], UUID]
Now = Callable[[], datetime]


@dataclass(frozen=True)
class _T03Authority:
    root: Path
    bundle: John15NormalizationBundle
    receipt: NormalizationReceipt
    receipt_file_sha256: str


@dataclass(frozen=True)
class _EvidenceResult:
    packet: John15TranslationNuanceEvidencePacket
    receipt: John15TranslationNuanceEvidenceReceipt
    published: bool
    verified_existing: bool


def _retained_bytes(path: Path) -> tuple[bytes, str, int]:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
        try:
            metadata = os.fstat(fd)
            if not stat.S_ISREG(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) != 0o444:
                raise ValueError
            with os.fdopen(fd, "rb", closefd=False) as stream:
                data = stream.read()
        finally:
            os.close(fd)
    except (OSError, ValueError):
        raise ValueError(f"retained authority is missing, mutable, symlinked, or non-regular: {path.name}") from None
    return data, hashlib.sha256(data).hexdigest(), metadata.st_size


def _require_root(root: Path, expected_root: Path) -> Path:
    if root.is_symlink() or not root.is_dir():
        raise ValueError("archive root must be an existing real directory")
    root = root.resolve(strict=True)
    if root != expected_root.resolve(strict=True):
        raise ValueError("archive root does not resolve to the canonical archive root")
    marker_bytes, marker_sha, _ = _retained_bytes(root / ".bsl-archive-root.json")
    try:
        marker = ArchiveRootMarker.model_validate_json(marker_bytes)
        canary_sha = _retained_bytes(root / marker.canary_relative_path)[1]
        receipt_bytes = _retained_bytes(root / marker.initialization_receipt_relative_path)[0]
        receipt = ArchiveInitializationReceipt.model_validate_json(receipt_bytes)
    except (ValidationError, ValueError):
        raise ValueError("archive governance authority is missing or invalid") from None
    bindings = (
        marker.canonical_archive_root == str(CANONICAL_ARCHIVE_ROOT),
        canary_sha == marker.canary_sha256,
        receipt.archive_id == marker.archive_id,
        receipt.operation_id == marker.archive_id,
        receipt.disposition == "INITIALIZED",
        receipt.marker_sha256 == marker_sha,
        receipt.canonical_archive_root == marker.canonical_archive_root,
    )
    if not all(bindings):
        raise ValueError("archive governance authority bindings differ")
    return root


def _validate_t03_receipt(
    root: Path, bundle: John15NormalizationBundle, receipt: NormalizationReceipt, receipt_sha: str
) -> None:
    expected_paths = (T03_OBJECT, T03_SNAPSHOT, T03_RECEIPT)
    expected = (
        receipt.disposition == "PUBLISHED",
        receipt.dry_run is False,
        receipt.published is True,
        receipt.verified_existing is False,
        receipt.implementation_commit == T03_IMPLEMENTATION_COMMIT,
        receipt.archive_root == str(CANONICAL_ARCHIVE_ROOT),
        receipt.publication_paths == expected_paths,
        receipt.bundle_identity == BUNDLE_IDENTITY == bundle.bundle_identity,
        receipt.bundle_canonical_sha256 == BUNDLE_SHA256,
        receipt.source_snapshot_identities == tuple(source.snapshot_identity for source in bundle.sources),
        receipt.source_content_identities == tuple(source.content_identity for source in bundle.sources),
        len(set(receipt.source_snapshot_identities)) == 6,
        len(set(receipt.source_content_identities)) == 6,
        str(receipt.receipt_identity) == EXACT_INPUT_AUTHORITY["normalization_receipt_identity"],
        receipt_sha == EXACT_INPUT_AUTHORITY["normalization_receipt_file_sha256"],
        list(receipt.source_snapshot_identities) == EXACT_INPUT_AUTHORITY["source_snapshot_identities"],
        list(receipt.source_content_identities) == EXACT_INPUT_AUTHORITY["source_content_identities"],
        root.is_dir(),
    )
    if not all(expected):
        raise ValueError("published T03 receipt does not bind the exact required authority")


def load_t03_authority(archive_root: Path, *, _expected_archive_root: Path = CANONICAL_ARCHIVE_ROOT) -> _T03Authority:
    root = _require_root(archive_root, _expected_archive_root)
    object_bytes, object_sha, _ = _retained_bytes(root / T03_OBJECT)
    snapshot_bytes, snapshot_sha, _ = _retained_bytes(root / T03_SNAPSHOT)
    receipt_bytes, receipt_sha, _ = _retained_bytes(root / T03_RECEIPT)
    if object_bytes != snapshot_bytes or object_sha != BUNDLE_SHA256 or snapshot_sha != BUNDLE_SHA256:
        raise ValueError("T03 object and snapshot are not the exact required canonical bytes")
    try:
        bundle = John15NormalizationBundle.model_validate_json(snapshot_bytes)
        receipt = NormalizationReceipt.model_validate_json(receipt_bytes)
    except ValidationError:
        raise ValueError("T03 bundle or receipt raw JSON is invalid") from None
    expected_bundle = (
        bundle.bundle_identity == BUNDLE_IDENTITY,
        bundle.normalization_specification_id == "ACT-VS01-T03-JOHN-1-5-NORMALIZATION-v1",
        bundle.normalization_specification_sha256 == "ef3f8bd34d727a89bab5942c550006f0eda408d1f472ba2782fc2ccd519597e9",
    )
    if not all(expected_bundle):
        raise ValueError("T03 normalization identity or specification differs")
    _validate_t03_receipt(root, bundle, receipt, receipt_sha)
    return _T03Authority(root, bundle, receipt, receipt_sha)


def _sense(bundle: John15NormalizationBundle, number: str) -> tuple[Any, ...]:
    structure = bundle.abbott_smith.ordered_structure
    matches = tuple(item for item in structure if item.tag == "sense" and dict(item.attributes).get("n") == number)
    if len(matches) != 1:
        raise ValueError(f"Abbott-Smith sense {number} is not unique")
    parent = matches[0].order
    return tuple(item for item in structure if item.order == parent or item.parent_order == parent)


def _sense_values(items: tuple[Any, ...], tag: str, attribute: str | None = None) -> set[str]:
    if attribute is None:
        return {cast(str, item.text) for item in items if item.tag == tag and item.text is not None}
    return {value for item in items if item.tag == tag for key, value in item.attributes if key == attribute}


def _verify_lexicon(bundle: John15NormalizationBundle, spec: dict[str, Any]) -> None:
    if bundle.abbott_smith.selector != 'entry@n="καταλαμβάνω|G2638"':
        raise ValueError("normalized Abbott-Smith selector differs")
    senses = (_sense(bundle, "1."), _sense(bundle, "2."), _sense(bundle, "3."))
    if not {"to lay hold of", "seize", "appropriate"} <= _sense_values(senses[0], "gloss"):
        raise ValueError("Abbott-Smith sense 1 differs")
    if "to overtake" not in _sense_values(senses[1], "gloss") or not {
        "John.1.5",
        "John.12.35",
    } <= _sense_values(senses[1], "ref", "osisRef"):
        raise ValueError("Abbott-Smith sense 2 or its John locators differ")
    if not {"to apprehend", "comprehend"} <= _sense_values(senses[2], "gloss"):
        raise ValueError("Abbott-Smith mental-action glosses differ")
    if "John.1.5" in _sense_values(senses[2], "ref", "osisRef") or bundle.source_serif.scholarly_evidence:
        raise ValueError("Abbott-Smith sense 3 or Source Serif boundary differs")
    if any(item.get("source_id") == "SP01-SRC-006" for item in spec["evidence_items"]):
        raise ValueError("Source Serif cannot receive a scholarly-evidence role")


def verify_source_evidence(bundle: John15NormalizationBundle, spec: dict[str, Any]) -> None:
    target = bundle.morphgnt.target_verb
    token = bundle.morphgnt.tokens[target.token_index]
    greek = bundle.sblgnt.exact_source_view.text.rstrip()
    morphology = (
        target.source_form,
        target.lemma,
        target.person,
        target.number,
        target.tense,
        target.voice,
        target.mood,
    )
    if not greek.endswith(GREEK_CLAUSE) or greek.count("κατέλαβεν") != 1:
        raise ValueError("normalized Greek evidence differs from the exact controlled clause")
    if morphology != ("κατέλαβεν", "καταλαμβάνω", "third", "singular", "aorist", "active", "indicative"):
        raise ValueError("normalized target morphology differs")
    if (token.word, token.lemma, token.parsing_code, token.text_alignment) != (
        "κατέλαβεν",
        "καταλαμβάνω",
        "3AAI-S--",
        "κατέλαβεν.",
    ):
        raise ValueError("normalized target index does not resolve to the exact MorphGNT token")
    if bundle.asv.canonical_realization.text != (
        "And the light shineth in the darkness; and the darkness apprehended it not."
    ) or bundle.web_classic.canonical_realization.text != (
        "The light shines in the darkness, and the darkness hasn’t overcome it."
    ):
        raise ValueError("normalized translation realization differs")
    _verify_lexicon(bundle, spec)


def _packet(authority: _T03Authority, spec: dict[str, Any]) -> John15TranslationNuanceEvidencePacket:
    bundle, receipt = authority.bundle, authority.receipt
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "contract": "John15TranslationNuanceEvidencePacket",
        "packet_id": "SP01-DER-001",
        "frozen_design_id": "VS01-T04",
        "frozen_design_sha256": DESIGN_SHA256,
        "frozen_claim_evidence_spec_id": "VS01-T04-CLAIM-EVIDENCE-SPEC-v1",
        "frozen_claim_evidence_spec_sha256": SPEC_SHA256,
        "input_authority": {
            "contract": "John15NormalizationBundle",
            "bundle_identity": bundle.bundle_identity,
            "bundle_canonical_sha256": BUNDLE_SHA256,
            "normalization_specification_id": bundle.normalization_specification_id,
            "normalization_specification_sha256": bundle.normalization_specification_sha256,
            "normalization_receipt_identity": str(receipt.receipt_identity),
            "normalization_receipt_file_sha256": authority.receipt_file_sha256,
            "source_snapshot_identities": receipt.source_snapshot_identities,
            "source_content_identities": receipt.source_content_identities,
        },
    }
    payload.update({field: spec[field] for field in FROZEN_FIELDS})
    identity = hashlib.sha256(rfc8785.dumps(payload)).hexdigest()
    return John15TranslationNuanceEvidencePacket.model_validate_json(
        rfc8785.dumps(payload | {"packet_identity": identity})
    )


def canonical_input_fingerprint(authority: _T03Authority) -> str:
    records: list[dict[str, Any]] = []
    for relative in (".bsl-archive-root.json", T03_OBJECT, T03_SNAPSHOT, T03_RECEIPT):
        _data, digest, size = _retained_bytes(authority.root / relative)
        records.append({"path": relative, "sha256": digest, "byte_count": size, "mode": "0444"})
    return hashlib.sha256(rfc8785.dumps({"files": records})).hexdigest()


def _git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=Path(__file__).parents[3], check=True, capture_output=True, text=True
    )
    value = result.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError("implementation commit cannot be resolved")
    return value


def _receipt(
    authority: _T03Authority,
    packet: John15TranslationNuanceEvidencePacket,
    packet_sha: str,
    implementation_commit: str,
    disposition: str,
    before: str,
    after: str,
    new_uuid: NewUuid,
    now: Now,
) -> John15TranslationNuanceEvidenceReceipt:
    state = {
        "DRY_RUN_VALIDATED": (True, False, False),
        "PUBLISHED": (False, True, False),
        "VERIFIED_EXISTING": (False, False, True),
    }[disposition]
    return John15TranslationNuanceEvidenceReceipt(
        receipt_identity=new_uuid(),
        generated_at=now(),
        implementation_commit=implementation_commit,
        archive_root=str(authority.root),
        disposition=cast(Any, disposition),
        dry_run=state[0],
        input_bundle_identity=BUNDLE_IDENTITY,
        input_bundle_canonical_sha256=BUNDLE_SHA256,
        input_normalization_receipt_identity=authority.receipt.receipt_identity,
        input_normalization_receipt_file_sha256=authority.receipt_file_sha256,
        packet_identity=packet.packet_identity,
        packet_canonical_sha256=packet_sha,
        publication_paths=publication_paths(packet_sha),
        input_authority_fingerprint_before=before,
        input_authority_fingerprint_after=after,
        published=state[1],
        verified_existing=state[2],
    )


def generate_john15_evidence(
    archive_root: Path,
    *,
    dry_run: bool,
    _expected_archive_root: Path = CANONICAL_ARCHIVE_ROOT,
    _implementation_commit: str | None = None,
    _new_uuid: NewUuid = uuid7,
    _now: Now = lambda: datetime.now(UTC),
) -> _EvidenceResult:
    authority = load_t03_authority(archive_root, _expected_archive_root=_expected_archive_root)
    spec = load_frozen_spec()
    verify_source_evidence(authority.bundle, spec)
    packet = _packet(authority, spec)
    packet_bytes = canonical_packet_bytes(packet)
    packet_sha = hashlib.sha256(packet_bytes).hexdigest()
    implementation_commit = _implementation_commit or _git_head()
    before = canonical_input_fingerprint(authority)
    if dry_run:
        after = canonical_input_fingerprint(
            load_t03_authority(archive_root, _expected_archive_root=_expected_archive_root)
        )
        receipt = _receipt(
            authority, packet, packet_sha, implementation_commit, "DRY_RUN_VALIDATED", before, after, _new_uuid, _now
        )
        return _EvidenceResult(packet, receipt, False, False)
    after = canonical_input_fingerprint(load_t03_authority(archive_root, _expected_archive_root=_expected_archive_root))
    if after != before:
        raise ValueError("T03 input authority changed before publication")
    existing = prepare_publication(authority.root, packet, packet_bytes, before)
    disposition = "VERIFIED_EXISTING" if existing is not None else "PUBLISHED"
    receipt = _receipt(
        authority, packet, packet_sha, implementation_commit, disposition, before, after, _new_uuid, _now
    )
    if existing is not None:
        return _EvidenceResult(packet, receipt, False, True)
    publish_evidence(authority.root, packet, receipt, before)
    actual_after = canonical_input_fingerprint(
        load_t03_authority(archive_root, _expected_archive_root=_expected_archive_root)
    )
    if actual_after != before or evidence_stage_path(authority.root, packet_sha).exists():
        raise ValueError("publication changed T03 input authority or left its packet-bound stage")
    return _EvidenceResult(packet, receipt, True, False)
