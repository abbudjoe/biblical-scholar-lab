from __future__ import annotations

import hashlib
import re
import subprocess
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from uuid import UUID
from xml.etree import ElementTree

import rfc8785
from uuid6 import uuid7

from bsl.application.source_acquisition import (  # pyright: ignore[reportPrivateUsage]
    _load_snapshot,  # pyright: ignore[reportPrivateUsage]
    _read_regular,  # pyright: ignore[reportPrivateUsage]
    _require_initialized_root,  # pyright: ignore[reportPrivateUsage]
    _source,  # pyright: ignore[reportPrivateUsage]
    _verify_authority,  # pyright: ignore[reportPrivateUsage]
    _verify_objects,  # pyright: ignore[reportPrivateUsage]
)
from bsl.contracts.normalization import John15NormalizationBundle, NormalizationReceipt
from bsl.contracts.source_admission import APPROVED_SOURCE_IDS, SourceSnapshot
from bsl.infrastructure.archive_store import _hash_file  # pyright: ignore[reportPrivateUsage]
from bsl.infrastructure.normalization_store import (
    canonical_bundle_bytes,
    publication_paths,
    publish_normalization,
    verify_existing,
)
from bsl.infrastructure.source_transport import (  # pyright: ignore[reportPrivateUsage]
    _usfm_ids,  # pyright: ignore[reportPrivateUsage]
    _web_verse,  # pyright: ignore[reportPrivateUsage]
)
from bsl.infrastructure.source_validation import _asv_target  # pyright: ignore[reportPrivateUsage]

CANONICAL_ARCHIVE_ROOT = Path("/Volumes/BSL-Archive/BiblicalScholarLab")
SOURCE_MANIFEST = Path(__file__).parents[3] / "design/approved/SOURCE-PLAN-01-source-admission-manifest.json"
SPECIFICATION_ID = "ACT-VS01-T03-JOHN-1-5-NORMALIZATION-v1"
SPECIFICATION_SHA256 = "ef3f8bd34d727a89bab5942c550006f0eda408d1f472ba2782fc2ccd519597e9"
NewUuid = Callable[[], UUID]
Now = Callable[[], datetime]


@dataclass(frozen=True)
class _NormalizationResult:
    bundle: John15NormalizationBundle
    receipt: NormalizationReceipt
    published: bool
    verified_existing: bool


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _text_view(text: str) -> dict[str, Any]:
    data = text.encode("utf-8")
    return {"text": text, "utf8_sha256": _sha(data), "byte_count": len(data)}


def _object_binding(item: Any) -> dict[str, Any]:
    return {
        "relative_path": item.relative_path,
        "sha256": item.sha256,
        "byte_count": item.byte_count,
        "rights_evidence": item.rights_evidence,
    }


def _source_binding(snapshot: SourceSnapshot) -> dict[str, Any]:
    return {
        "source_id": snapshot.source_id,
        "snapshot_identity": snapshot.snapshot_identity,
        "content_identity": snapshot.content_identity,
        "source_spec_sha256": snapshot.source_spec_sha256,
        "package_sha256": snapshot.package_sha256,
        "objects": tuple(_object_binding(item) for item in snapshot.objects),
        "allowed_operations": snapshot.allowed_operations,
        "attribution": snapshot.attribution,
        "edition_identity": snapshot.edition_identity,
    }


def _selected(snapshot: SourceSnapshot, relative_path: str) -> Any:
    matches = tuple(item for item in snapshot.objects if item.relative_path == relative_path)
    if len(matches) != 1:
        raise ValueError(f"normalization component is not unique: {snapshot.source_id}:{relative_path}")
    return matches[0]


def _load_authoritative_sources(archive_root: Path, expected_root: Path) -> tuple[Path, tuple[SourceSnapshot, ...]]:
    root = _require_initialized_root(archive_root, expected_root)
    expected = tuple(f"{source_id}.json" for source_id in APPROVED_SOURCE_IDS)
    actual = tuple(path.name for path in sorted((root / "snapshots/source").iterdir()))
    if actual != expected:
        raise ValueError("authoritative source snapshot set is not exactly SP01-SRC-001 through SP01-SRC-006")
    snapshots: list[SourceSnapshot] = []
    for source_id in APPROVED_SOURCE_IDS:
        context = _source(SOURCE_MANIFEST, source_id)
        snapshot = _load_snapshot(root, source_id)
        if snapshot is None:
            raise ValueError(f"authoritative source snapshot is missing: {source_id}")
        _verify_authority(root, snapshot, context)
        _verify_objects(root, snapshot)
        snapshots.append(snapshot)
    return root, tuple(snapshots)


def _read_source_object(root: Path, snapshot: SourceSnapshot, relative_path: str) -> bytes:
    item = _selected(snapshot, relative_path)
    path = root / "objects/sha256" / item.sha256[:2] / item.sha256
    digest, size = _hash_file(path, require_read_only=True)
    data = _read_regular(path, "selected source object")
    if (digest, size, len(data)) != (item.sha256, item.byte_count, item.byte_count):
        raise ValueError("selected source object hash or byte count is inconsistent")
    return data


def _sblgnt(root: Path, snapshot: SourceSnapshot) -> tuple[dict[str, Any], str]:
    relative = "data/sblgnt/text/John.txt"
    item = _selected(snapshot, relative)
    data = _read_source_object(root, snapshot, relative)
    candidates = tuple(line for line in data.splitlines(keepends=True) if line.startswith(b"John 1:5\t"))
    if len(candidates) != 1:
        raise ValueError("SBLGNT John 1:5 must occur exactly once")
    source_bytes = candidates[0].split(b"\t", 1)[1].rstrip(b"\r\n")
    try:
        source = source_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("SBLGNT John 1:5 is not UTF-8") from None
    display = unicodedata.normalize("NFC", source)
    evidence: dict[str, Any] = {
        "source_object_sha256": item.sha256,
        "source_object_relative_path": relative,
        "exact_source_view": _text_view(source),
        "unicode_nfc_display_view": _text_view(display),
    }
    return evidence, source


def _morphgnt(root: Path, snapshot: SourceSnapshot, source: str) -> dict[str, Any]:
    relative = "64-Jn-morphgnt.txt"
    item = _selected(snapshot, relative)
    data = _read_source_object(root, snapshot, relative)
    try:
        rows = tuple(line.split() for line in data.decode("utf-8").splitlines() if line.startswith("040105 "))
    except UnicodeDecodeError:
        raise ValueError("MorphGNT John data is not UTF-8") from None
    if not rows or any(len(row) != 7 for row in rows):
        raise ValueError("MorphGNT John 1:5 rows must preserve exactly seven source-native columns")
    spans = tuple(match.span() for match in re.finditer(r"\S+", source))
    if len(rows) != len(spans):
        raise ValueError("MorphGNT token count does not cover SBLGNT John 1:5")
    tokens: list[dict[str, Any]] = []
    for row, (start, end) in zip(rows, spans, strict=True):
        if unicodedata.normalize("NFC", row[3]) != unicodedata.normalize("NFC", source[start:end]):
            raise ValueError("MorphGNT text-alignment token differs from ordered SBLGNT coverage")
        tokens.append(
            dict(
                zip(
                    ("bcv", "part_of_speech", "parsing_code", "text_alignment", "word", "normalized_word", "lemma"),
                    row,
                    strict=True,
                )
            )
            | {"sblgnt_start": start, "sblgnt_end": end}
        )
    targets = tuple(index for index, row in enumerate(rows) if unicodedata.normalize("NFC", row[6]) == "καταλαμβάνω")
    if len(targets) != 1:
        raise ValueError("MorphGNT target lemma must occur exactly once")
    target_index = targets[0]
    target = rows[target_index]
    if (target[2], unicodedata.normalize("NFC", target[4])) != ("3AAI-S--", "κατέλαβεν"):
        raise ValueError("MorphGNT target source form or parsing code differs from the approved record")
    grammar = {
        "token_index": target_index,
        "source_form": "κατέλαβεν",
        "lemma": "καταλαμβάνω",
        "parsing_code": "3AAI-S--",
        "person": "third",
        "number": "singular",
        "tense": "aorist",
        "voice": "active",
        "mood": "indicative",
    }
    return {
        "source_object_sha256": item.sha256,
        "source_object_relative_path": relative,
        "tokens": tuple(tokens),
        "target_verb": grammar,
    }


def _asv(root: Path, snapshot: SourceSnapshot) -> dict[str, Any]:
    relative = "usx/43-JHN.usx"
    item = _selected(snapshot, relative)
    targets, text = _asv_target({relative: _read_source_object(root, snapshot, relative)})
    if targets != 1:
        raise ValueError("ASV canonical John 1:5 must occur exactly once")
    return {
        "source_id": snapshot.source_id,
        "source_object_sha256": item.sha256,
        "source_object_relative_path": relative,
        "package_sha256": None,
        "canonical_realization": _text_view(text),
    }


def _web(root: Path, snapshot: SourceSnapshot) -> dict[str, Any]:
    candidates: list[tuple[Any, str]] = []
    for item in snapshot.objects:
        if not item.relative_path.lower().endswith((".sfm", ".usfm")):
            continue
        data = _read_source_object(root, snapshot, item.relative_path)
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError("WEB admitted USFM object is not UTF-8") from None
        if _usfm_ids(text) == ("JHN",):
            candidates.append((item, text))
    if len(candidates) != 1:
        raise ValueError("WEB admitted John component must be uniquely identified by canonical \\id JHN")
    item, source = candidates[0]
    targets, text = _web_verse(source)
    if targets != 1:
        raise ValueError("WEB canonical John 1:5 must occur exactly once")
    return {
        "source_id": snapshot.source_id,
        "source_object_sha256": item.sha256,
        "source_object_relative_path": item.relative_path,
        "package_sha256": snapshot.package_sha256,
        "canonical_realization": _text_view(text),
    }


def _xml_name(value: str) -> str:
    if value.startswith("{http://www.w3.org/XML/1998/namespace}"):
        return f"xml:{value.rsplit('}', 1)[1]}"
    return value.rsplit("}", 1)[-1]


def _lexical_structure(entry: ElementTree.Element) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = []

    def visit(element: ElementTree.Element, parent: int | None) -> None:
        order = len(records)
        records.append(
            {
                "order": order,
                "parent_order": parent,
                "tag": _xml_name(element.tag),
                "attributes": tuple(sorted((_xml_name(key), value) for key, value in element.attrib.items())),
                "text": element.text,
                "tail": element.tail,
            }
        )
        for child in element:
            visit(child, order)

    visit(entry, None)
    return tuple(records)


def _abbott_smith(root: Path, snapshot: SourceSnapshot) -> dict[str, Any]:
    relative = "abbott-smith.tei.xml"
    item = _selected(snapshot, relative)
    data = _read_source_object(root, snapshot, relative)
    target = "καταλαμβάνω|G2638".encode()
    pattern = re.compile(rb"<entry\b[^>]*\bn=(['\"])" + re.escape(target) + rb"\1[^>]*>")
    starts = tuple(match.start() for match in pattern.finditer(data))
    if len(starts) != 1:
        raise ValueError('Abbott-Smith entry@n="καταλαμβάνω|G2638" must occur exactly once')
    end = data.find(b"</entry>", starts[0])
    if end < 0:
        raise ValueError("Abbott-Smith target entry is unbounded")
    span = data[starts[0] : end + len(b"</entry>")]
    try:
        source_entry = span.decode("utf-8")
        entry = ElementTree.fromstring(span)
    except (UnicodeDecodeError, ElementTree.ParseError):
        raise ValueError("Abbott-Smith target entry is not exact well-formed UTF-8 XML") from None
    structure = _lexical_structure(entry)
    locators = ['entry@n="καταλαμβάνω|G2638"'] + [
        f"{record['tag']}@{key}={value}"
        for record in structure
        for key, value in cast(tuple[tuple[str, str], ...], record["attributes"])
        if key in {"n", "osisRef"}
    ]
    return {
        "source_object_sha256": item.sha256,
        "source_object_relative_path": relative,
        "selector": 'entry@n="καταλαμβάνω|G2638"',
        "source_entry_utf8": source_entry,
        "source_entry_sha256": _sha(span),
        "source_entry_byte_count": len(span),
        "ordered_structure": structure,
        "locators": tuple(locators),
    }


def _source_serif(snapshot: SourceSnapshot) -> dict[str, Any]:
    paths = ("TTF/SourceSerif4-Regular.ttf", "TTF/SourceSerif4-It.ttf", "LICENSE.md")
    regular, italic, license_object = (_selected(snapshot, path) for path in paths)
    return {
        "regular_font": _object_binding(regular),
        "italic_font": _object_binding(italic),
        "license_object": _object_binding(license_object),
        "scholarly_evidence": False,
    }


def _build_bundle(root: Path, snapshots: tuple[SourceSnapshot, ...]) -> John15NormalizationBundle:
    by_id = {snapshot.source_id: snapshot for snapshot in snapshots}
    sblgnt, source = _sblgnt(root, by_id["SP01-SRC-001"])
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "contract": "John15NormalizationBundle",
        "normalization_specification_id": SPECIFICATION_ID,
        "normalization_specification_sha256": SPECIFICATION_SHA256,
        "passage_identity": "John 1:5",
        "sources": tuple(_source_binding(snapshot) for snapshot in snapshots),
        "sblgnt": sblgnt,
        "morphgnt": _morphgnt(root, by_id["SP01-SRC-002"], source),
        "asv": _asv(root, by_id["SP01-SRC-003"]),
        "web_classic": _web(root, by_id["SP01-SRC-004"]),
        "abbott_smith": _abbott_smith(root, by_id["SP01-SRC-005"]),
        "source_serif": _source_serif(by_id["SP01-SRC-006"]),
        "normalization_methods": (
            "exact UTF-8 source-span selection",
            "Unicode NFC display view without source replacement",
            "Unicode-whitespace tokenization and exact ordered token alignment",
            "USX canonical verse extraction excluding note subtrees",
            "USFM canonical verse extraction with bounded note and cross-reference exclusion and word-span unwrapping",
            "TEI exact-entry span selection with ordered source-element preservation",
            "content-addressed dependency binding without font parsing",
        ),
        "deterministic_limitations": (
            "MorphGNT supplies annotation and alignment evidence, not an independent Greek edition.",
            "The grammatical record does not establish contextual sense, aspectual interpretation, discourse effect, "
            "translator intent, or theology.",
            "Translation realizations do not adjudicate which rendering is best or establish a textual variant.",
            "Abbott-Smith preserves lexical range without selecting a contextual sense, combining all glosses as one "
            "meaning, or claiming consensus.",
            "Source Serif is a page-rendering dependency and is not scholarly evidence.",
        ),
    }
    identity = _sha(rfc8785.dumps(payload))
    return John15NormalizationBundle.model_validate(payload | {"bundle_identity": identity})


def authority_fingerprint(
    root: Path,
    snapshots: tuple[SourceSnapshot, ...],
    *,
    normalization_present: tuple[bool, bool] | None = None,
) -> dict[str, Any]:
    source_records: list[dict[str, Any]] = []
    objects: dict[str, dict[str, Any]] = {}
    for snapshot in snapshots:
        paths = (
            snapshot.snapshot_relative_path,
            snapshot.fetch_receipt_relative_path,
            snapshot.admission_decision_relative_path,
        )
        hashes = tuple(_hash_file(root / path, require_read_only=True)[0] for path in paths)
        source_records.append(
            {
                "source_id": snapshot.source_id,
                "snapshot_file_sha256": hashes[0],
                "fetch_receipt_sha256": hashes[1],
                "admission_decision_sha256": hashes[2],
            }
        )
        for item in snapshot.objects:
            relative = f"objects/sha256/{item.sha256[:2]}/{item.sha256}"
            objects[relative] = {"relative_path": relative, "sha256": item.sha256, "byte_count": item.byte_count}
    actual_present = ((root / "snapshots/normalization").exists(), (root / "manifests/normalization").exists())
    payload: dict[str, Any] = {
        "root_marker_sha256": _hash_file(root / ".bsl-archive-root.json", require_read_only=True)[0],
        "sources": tuple(source_records),
        "objects": tuple(objects[key] for key in sorted(objects)),
        "authoritative_source_snapshot_ids": tuple(snapshot.source_id for snapshot in snapshots),
        "incoming_empty": not any((root / ".incoming").iterdir()),
        "snapshots_normalization_present": (normalization_present or actual_present)[0],
        "manifests_normalization_present": (normalization_present or actual_present)[1],
    }
    return payload | {"semantic_fingerprint": _sha(rfc8785.dumps(payload))}


def _git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=Path(__file__).parents[3], check=True, capture_output=True, text=True
    )
    value = result.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError("implementation commit cannot be resolved")
    return value


def _receipt(
    *,
    bundle: John15NormalizationBundle,
    bundle_sha256: str,
    root: Path,
    implementation_commit: str,
    disposition: str,
    before: str,
    after: str,
    new_uuid: NewUuid,
    now: Now,
) -> NormalizationReceipt:
    state = {
        "DRY_RUN_VALIDATED": (True, False, False),
        "PUBLISHED": (False, True, False),
        "VERIFIED_EXISTING": (False, False, True),
    }[disposition]
    return NormalizationReceipt(
        receipt_identity=new_uuid(),
        generated_at=now(),
        implementation_commit=implementation_commit,
        archive_root=str(root),
        disposition=cast(Any, disposition),
        dry_run=state[0],
        bundle_identity=bundle.bundle_identity,
        bundle_canonical_sha256=bundle_sha256,
        source_snapshot_identities=tuple(source.snapshot_identity for source in bundle.sources),
        source_content_identities=tuple(source.content_identity for source in bundle.sources),
        publication_paths=publication_paths(bundle_sha256),
        archive_authority_fingerprint_before=before,
        archive_authority_fingerprint_after=after,
        published=state[1],
        verified_existing=state[2],
    )


def normalize_john15(
    archive_root: Path,
    *,
    dry_run: bool,
    _expected_archive_root: Path = CANONICAL_ARCHIVE_ROOT,
    _implementation_commit: str | None = None,
    _new_uuid: NewUuid = uuid7,
    _now: Now = lambda: datetime.now(UTC),
) -> _NormalizationResult:
    root, snapshots = _load_authoritative_sources(archive_root, _expected_archive_root)
    before_record = authority_fingerprint(root, snapshots)
    if not before_record["incoming_empty"]:
        raise ValueError("archive .incoming must be empty before normalization")
    before = cast(str, before_record["semantic_fingerprint"])
    bundle = _build_bundle(root, snapshots)
    bundle_bytes = canonical_bundle_bytes(bundle)
    bundle_sha256 = _sha(bundle_bytes)
    implementation_commit = _implementation_commit or _git_head()
    if dry_run:
        after = cast(str, authority_fingerprint(root, snapshots)["semantic_fingerprint"])
        receipt = _receipt(
            bundle=bundle,
            bundle_sha256=bundle_sha256,
            root=root,
            implementation_commit=implementation_commit,
            disposition="DRY_RUN_VALIDATED",
            before=before,
            after=after,
            new_uuid=_new_uuid,
            now=_now,
        )
        return _NormalizationResult(bundle, receipt, False, False)
    existing = verify_existing(root, bundle, bundle_bytes)
    if existing is not None:
        after = cast(str, authority_fingerprint(root, snapshots)["semantic_fingerprint"])
        receipt = _receipt(
            bundle=bundle,
            bundle_sha256=bundle_sha256,
            root=root,
            implementation_commit=implementation_commit,
            disposition="VERIFIED_EXISTING",
            before=before,
            after=after,
            new_uuid=_new_uuid,
            now=_now,
        )
        return _NormalizationResult(bundle, receipt, False, True)
    expected_after = cast(
        str, authority_fingerprint(root, snapshots, normalization_present=(True, True))["semantic_fingerprint"]
    )
    receipt = _receipt(
        bundle=bundle,
        bundle_sha256=bundle_sha256,
        root=root,
        implementation_commit=implementation_commit,
        disposition="PUBLISHED",
        before=before,
        after=expected_after,
        new_uuid=_new_uuid,
        now=_now,
    )
    publish_normalization(root, bundle, receipt, _new_uuid())
    actual_after = cast(str, authority_fingerprint(root, snapshots)["semantic_fingerprint"])
    if actual_after != expected_after or any((root / ".incoming").iterdir()):
        raise ValueError("published normalization does not match the expected archive authority state")
    return _NormalizationResult(bundle, receipt, True, False)
