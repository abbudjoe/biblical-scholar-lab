from __future__ import annotations

import hashlib
import inspect
import json
import shutil
import socket
import stat
import zipfile
from datetime import datetime
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock
from uuid import UUID

import pytest
import rfc8785
from pydantic import ValidationError

import bsl.application.source_acquisition as acquisition
import bsl.infrastructure.source_transport as source_transport
import bsl.infrastructure.source_validation as source_validation
import bsl.interfaces.cli as cli
from bsl.application.source_acquisition import acquire_source
from bsl.contracts.archive import (
    APPROVED_APFS_SHA256,
    APPROVED_PREFLIGHT_SHA256,
    APPROVED_PROFILE_SHA256,
    CANARY_RELATIVE_PATH,
    CANARY_SHA256,
    ArchiveInitializationReceipt,
    ArchiveRootMarker,
    StablePhysicalDeviceIdKind,
)
from bsl.contracts.source_admission import AdmissionDecision, FetchReceipt, SourceSnapshot
from bsl.infrastructure.source_transport import HttpResponse, SourceTransportError

ROOT = Path(__file__).parents[1]
MANIFEST = ROOT / "design/approved/SOURCE-PLAN-01-source-admission-manifest.json"
CREATED = datetime.fromisoformat("2026-08-21T12:00:00-04:00")
ARCHIVE_ID = UUID("01890f29-7c00-7000-8000-000000000011")
REVISIONS = {source["source_id"]: source["revision"] for source in json.loads(MANIFEST.read_text())["sources"]}


def synthetic_sfnt(marker: bytes) -> bytes:
    tags = (b"cmap", b"head", b"maxp", b"name")
    directory_end = 12 + len(tags) * 16
    records = b"".join(
        tag + b"\0" * 4 + (directory_end + index * 4).to_bytes(4, "big") + b"\0\0\0\4" for index, tag in enumerate(tags)
    )
    return b"\0\1\0\0" + len(tags).to_bytes(2, "big") + b"\0" * 6 + records + marker * len(tags)


COMPONENTS: dict[str, dict[str, bytes]] = {
    "SP01-SRC-001": {
        "README.md": b"SBL Greek New Testament",
        "LICENSE": b"Attribution 4.0 International\nThis Public License does not apply",
        "data/sblgnt/text/John.txt": (
            "John 1:5\tκαὶ τὸ φῶς ἐν τῇ σκοτίᾳ φαίνει, καὶ ἡ σκοτία αὐτὸ οὐ κατέλαβεν. \n"
        ).encode(),
    },
    "SP01-SRC-002": {
        "README.md": b"CC-BY-SA License\nhttps://creativecommons.org/licenses/by-sa/3.0/",
        "64-Jn-morphgnt.txt": (
            "040105 C- -------- καὶ καὶ καί καί\n"
            "040105 RA ----NSN- τὸ τὸ τό ὁ\n"
            "040105 N- ----NSN- φῶς φῶς φῶς φῶς\n"
            "040105 P- -------- ἐν ἐν ἐν ἐν\n"
            "040105 RA ----DSF- τῇ τῇ τῇ ὁ\n"
            "040105 N- ----DSF- σκοτίᾳ σκοτίᾳ σκοτίᾳ σκοτία\n"
            "040105 V- 3PAI-S-- φαίνει, φαίνει φαίνει φαίνω\n"
            "040105 C- -------- καὶ καὶ καί καί\n"
            "040105 RA ----NSF- ἡ ἡ ἡ ὁ\n"
            "040105 N- ----NSF- σκοτία σκοτία σκοτία σκοτία\n"
            "040105 RP ----ASN- αὐτὸ αὐτὸ αὐτό αὐτός\n"
            "040105 D- -------- οὐ οὐ οὐ οὐ\n"
            "040105 V- 3AAI-S-- κατέλαβεν. κατέλαβεν κατέλαβε(ν) καταλαμβάνω\n"
        ).encode(),
    },
    "SP01-SRC-003": {
        "README.md": b"American Standard Version",
        "License.html": b"This edition is public domain.",
        "usx/43-JHN.usx": (
            b"<usx><chapter number='1'/><verse number='5'/>And the light shineth in the darkness; "
            b"and the darkness<note>excluded note text</note> apprehended it not."
            b"<verse eid='JHN 1:5'/></usx>"
        ),
    },
    "SP01-SRC-005": {
        "abbott-smith.tei.xml": (
            '<TEI><entry n="καταλαμβάνω|G2638"><form><orth>κατα-λαμβάνω</orth></form>'
            '<sense n="1"><gloss>lay hold of</gloss><ref osisRef="John.1.5">Jn 1:5</ref></sense>'
            '<sense n="2"><gloss>understand</gloss><xr>see also</xr></sense></entry></TEI>'
        ).encode(),
        "README.md": b"The TEI lexicon is public domain; the PDF is restricted.",
    },
    "SP01-SRC-006": {
        "TTF/SourceSerif4-Regular.ttf": synthetic_sfnt(b"reg!"),
        "TTF/SourceSerif4-It.ttf": synthetic_sfnt(b"ita!"),
        "LICENSE.md": b"Copyright 2014 Adobe. All Rights Reserved.\nSIL Open Font License\nVersion 1.1",
    },
}


@pytest.fixture(autouse=True)
def no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def blocked(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("external network access attempted")

    monkeypatch.setattr(socket.socket, "connect", blocked)


def _immutable(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    path.chmod(0o444)


@pytest.fixture
def archive_root(tmp_path: Path) -> Path:
    root = tmp_path / "synthetic-initialized-archive"
    for relative in ("objects/sha256", "manifests/source", "snapshots/source", "quarantine", ".incoming"):
        (root / relative).mkdir(parents=True, exist_ok=True)
    _immutable(root / CANARY_RELATIVE_PATH, b"BSL_ARCHIVE_INITIALIZATION_CANARY_V1\n")
    marker = ArchiveRootMarker(
        archive_id=ARCHIVE_ID,
        created_at=CREATED,
        profile_id="ARCHIVE-PROFILE-BSL-ARCHIVE-v1",
        profile_file_sha256=APPROVED_PROFILE_SHA256,
        archive_preflight_receipt_sha256=APPROVED_PREFLIGHT_SHA256,
        post_merge_apfs_snapshot_sha256=APPROVED_APFS_SHA256,
        canonical_archive_root="/Volumes/BSL-Archive/BiblicalScholarLab",
        volume_name="BSL-Archive",
        stable_volume_identifier="synthetic-volume",
        stable_physical_identifier="synthetic-physical",
        stable_physical_identifier_kind=StablePhysicalDeviceIdKind.DISK_UUID,
        canary_sha256=CANARY_SHA256,
        canary_relative_path=CANARY_RELATIVE_PATH,
        initialization_receipt_relative_path=f"registry/archive-initialization/{ARCHIVE_ID}.json",
    )
    marker_bytes = rfc8785.dumps(marker.model_dump(mode="json"))
    _immutable(root / ".bsl-archive-root.json", marker_bytes)
    receipt = ArchiveInitializationReceipt(
        operation_id=ARCHIVE_ID,
        archive_id=ARCHIVE_ID,
        generated_at=CREATED,
        disposition="INITIALIZED",
        profile_id="ARCHIVE-PROFILE-BSL-ARCHIVE-v1",
        profile_file_sha256=APPROVED_PROFILE_SHA256,
        canonical_archive_root="/Volumes/BSL-Archive/BiblicalScholarLab",
        marker_relative_path=".bsl-archive-root.json",
        marker_sha256=hashlib.sha256(marker_bytes).hexdigest(),
        canary_relative_path=CANARY_RELATIVE_PATH,
        canary_sha256=CANARY_SHA256,
        initialization_receipt_relative_path=f"registry/archive-initialization/{ARCHIVE_ID}.json",
    )
    _immutable(root / receipt.initialization_receipt_relative_path, rfc8785.dumps(receipt.model_dump(mode="json")))
    return root


def web_zip(
    *,
    extra: tuple[str | zipfile.ZipInfo, bytes] | None = None,
    john_name: str = "eng-web/43JHNeng-web.usfm",
    john_text: str = (
        "\\id JHN World English Bible\n\\c 1\n"
        '\\p\n\\v 5 \\w The|strong="G1722"\\w* \\w light|strong="G5457"\\w* '
        '\\w shines|strong="G5316"\\w* \\w in|strong="G1722"\\w* \\w the|strong="G1722"\\w* '
        '\\w darkness|strong="G4653"\\w*, \\w and|strong="G2532"\\w* \\w the|strong="G1722"\\w* '
        '\\w darkness|strong="G4653"\\w* hasn’\\w t|strong="G3588"\\w* overcome'
        '\\f + \\fr 1:5 \\ft synthetic note \\f* \\w it|strong="G2532"\\w*. \\x + hidden \\x*\n'
    ),
    rights_name: str = "eng-web/README.txt",
    rights_text: str = "World English Bible eng-web is public domain.",
) -> bytes:
    stream = BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("eng-web/", b"")
        archive.writestr(john_name, john_text)
        archive.writestr(rights_name, rights_text)
        if extra is not None:
            archive.writestr(*extra)
    return stream.getvalue()


class FakeTransport:
    def __init__(self, source_id: str, *, package: bytes | None = None) -> None:
        self.source_id = source_id
        self.package = package or web_zip()
        self.urls: list[str] = []
        self.body_updates: dict[str, bytes] = {}
        self.final_url_updates: dict[str, str] = {}
        self.revision = REVISIONS[source_id]

    def __call__(self, url: str, _limit: int) -> HttpResponse:
        self.urls.append(url)
        if self.source_id == "SP01-SRC-004":
            body = self.package
        elif "api.github.com" in url:
            body = json.dumps({"sha": self.revision}).encode()
        else:
            body = next(data for path, data in COMPONENTS[self.source_id].items() if url.endswith(f"/{path}"))
        body = next((data for suffix, data in self.body_updates.items() if url.endswith(suffix)), body)
        final = next((value for suffix, value in self.final_url_updates.items() if url.endswith(suffix)), url)
        return HttpResponse(url, final, 200, (("content-type", "application/octet-stream"),), body)


def _acquire(root: Path, source_id: str, transport: FakeTransport | None = None):
    return acquire_source(
        source_id,
        MANIFEST,
        root,
        transport=transport or FakeTransport(source_id),
        _expected_archive_root=root.resolve(),
    )


@pytest.mark.parametrize("source_id", tuple(f"SP01-SRC-00{index}" for index in range(1, 7)))
def test_every_approved_source_admits_synthetic_bytes(archive_root: Path, source_id: str) -> None:
    transport = FakeTransport(source_id)
    result = _acquire(archive_root, source_id, transport)
    assert result.decision.disposition == "ADMITTED"
    assert result.fetch_receipt is not None and result.snapshot is not None
    for relative in (result.snapshot.fetch_receipt_relative_path, result.snapshot.admission_decision_relative_path):
        assert stat.S_IMODE((archive_root / relative).stat().st_mode) == 0o444
    for item in result.snapshot.objects:
        retained = archive_root / "objects/sha256" / item.sha256[:2] / item.sha256
        assert retained.read_bytes() and stat.S_IMODE(retained.stat().st_mode) == 0o444
    if source_id != "SP01-SRC-004":
        assert all(REVISIONS[source_id] in url for url in transport.urls if "raw.githubusercontent.com" in url)
        assert source_id != "SP01-SRC-005" or all("manualgreeklexic00abborich.pdf" not in url for url in transport.urls)


def test_morphgnt_exact_seven_column_target_is_accepted() -> None:
    content_error, rights_error = source_validation._morphgnt_checks(COMPONENTS["SP01-SRC-002"])

    assert content_error is None
    assert rights_error is None


@pytest.mark.parametrize(
    "target_row",
    (
        "040105 V- 3AAI-S-- κατέλαβεν. κατέλαβε(ν) καταλαμβάνω",
        "040105 V- 3AAI-S-- κατέλαβεν κατέλαβεν κατέλαβε(ν) καταλαμβάνω",
        "040105 V- 3AAI-S-- κατέλαβεν. κατέλαβεν! κατέλαβε(ν) καταλαμβάνω",
        "040105 V- 3AAI-S-- κατέλαβεν. κατέλαβεν κατέλαβε καταλαμβάνω",
        "040105 V- 3AAI-S-- κατέλαβεν. κατέλαβεν κατέλαβε(ν) καταλαμβάνω!",
        "040105 V- 3PAI-S-- κατέλαβεν. κατέλαβεν κατέλαβε(ν) καταλαμβάνω",
    ),
)
def test_morphgnt_target_column_mismatches_are_rejected(target_row: str) -> None:
    files = COMPONENTS["SP01-SRC-002"] | {
        "64-Jn-morphgnt.txt": f"040105 C- -------- καὶ καί καί\n{target_row}\n".encode()
    }
    content_error, rights_error = source_validation._morphgnt_checks(files)

    assert content_error == "MORPHGNT_TARGET_ROW_NOT_FOUND"
    assert rights_error is None


@pytest.mark.parametrize(
    ("source_id", "path", "body", "reason"),
    (
        (
            "SP01-SRC-001",
            "data/sblgnt/text/John.txt",
            b"John 1:4\tmissing target\n",
            "SBLGNT_JOHN_1_5_NOT_FOUND",
        ),
        (
            "SP01-SRC-001",
            "data/sblgnt/text/John.txt",
            COMPONENTS["SP01-SRC-001"]["data/sblgnt/text/John.txt"] * 2,
            "SBLGNT_JOHN_1_5_AMBIGUOUS",
        ),
        (
            "SP01-SRC-001",
            "data/sblgnt/text/John.txt",
            b"John 1:5\tchanged target\n",
            "SBLGNT_JOHN_1_5_CONTENT_MISMATCH",
        ),
        (
            "SP01-SRC-002",
            "64-Jn-morphgnt.txt",
            COMPONENTS["SP01-SRC-002"]["64-Jn-morphgnt.txt"] * 2,
            "MORPHGNT_TARGET_ROW_AMBIGUOUS",
        ),
        (
            "SP01-SRC-003",
            "usx/43-JHN.usx",
            b"<usx><chapter number='1'/><verse number='4'/>missing target</usx>",
            "ASV_JOHN_1_5_NOT_FOUND",
        ),
        (
            "SP01-SRC-003",
            "usx/43-JHN.usx",
            b"<usx><chapter number='1'/><verse number='5'/>first<verse number='5'/>second</usx>",
            "ASV_JOHN_1_5_AMBIGUOUS",
        ),
        (
            "SP01-SRC-003",
            "usx/43-JHN.usx",
            b"<usx><chapter number='1'/><verse number='5'/>changed target</usx>",
            "ASV_JOHN_1_5_CONTENT_MISMATCH",
        ),
    ),
)
def test_source_content_failure_reasons_are_distinct(source_id: str, path: str, body: bytes, reason: str) -> None:
    content_error, rights_error = source_validation._GITHUB_CHECKS[source_id](COMPONENTS[source_id] | {path: body})
    assert content_error == reason
    assert rights_error is None


def test_abbott_smith_uses_canonical_entry_identifier() -> None:
    content_error, rights_error = source_validation._abbott_smith_checks(COMPONENTS["SP01-SRC-005"])
    assert content_error is None
    assert rights_error is None

    display_variant = COMPONENTS["SP01-SRC-005"] | {
        "abbott-smith.tei.xml": (
            "<TEI xmlns='u'><entry n='καταλαμβάνω|G2638'><form><orth>display variant</orth></form></entry></TEI>"
        ).encode()
    }
    assert source_validation._abbott_smith_checks(display_variant)[0] is None

    missing = COMPONENTS["SP01-SRC-005"] | {"abbott-smith.tei.xml": b"<TEI xmlns='u'><entry n='other|G0'/></TEI>"}
    duplicate = COMPONENTS["SP01-SRC-005"] | {
        "abbott-smith.tei.xml": (
            "<TEI xmlns='u'><entry n='καταλαμβάνω|G2638'/><entry n='καταλαμβάνω|G2638'/></TEI>"
        ).encode()
    }
    assert source_validation._abbott_smith_checks(missing)[0] == "ABBOTT_SMITH_ENTRY_NOT_FOUND"
    assert source_validation._abbott_smith_checks(duplicate)[0] == "ABBOTT_SMITH_ENTRY_AMBIGUOUS"


def test_source_serif_font_failures_are_distinct() -> None:
    valid = bytearray(synthetic_sfnt(b"font"))
    bad_signature = bytearray(valid)
    bad_signature[:4] = b"OTTO"
    low_count = b"\0\1\0\0\0\3" + b"\0" * 6
    truncated_directory = b"\0\1\0\0\0\4" + b"\0" * 6
    missing_table = bytearray(valid)
    missing_table[12:16] = b"TEST"
    invalid_bounds = bytearray(valid)
    invalid_bounds[20:24] = b"\0\0\0\0"

    assert source_validation._sfnt_error(b"short") == "SOURCE_SERIF_FONT_TRUNCATED"
    assert source_validation._sfnt_error(bytes(bad_signature)) == "SOURCE_SERIF_FONT_SIGNATURE_INVALID"
    assert source_validation._sfnt_error(low_count) == "SOURCE_SERIF_FONT_TABLE_COUNT_INVALID"
    assert source_validation._sfnt_error(truncated_directory) == "SOURCE_SERIF_FONT_DIRECTORY_TRUNCATED"
    assert source_validation._sfnt_error(bytes(missing_table)) == "SOURCE_SERIF_FONT_REQUIRED_TABLE_MISSING"
    assert source_validation._sfnt_error(bytes(invalid_bounds)) == "SOURCE_SERIF_FONT_TABLE_BOUNDS_INVALID"


@pytest.mark.parametrize("case", ("unknown", "duplicate", "reordered", "changed-revision"))
def test_unknown_or_altered_manifest_fails_before_quarantine(tmp_path: Path, archive_root: Path, case: str) -> None:
    if case == "unknown":
        with pytest.raises(ValueError, match="source ID"):
            acquire_source("SP01-SRC-999", MANIFEST, archive_root, transport=FakeTransport("SP01-SRC-001"))
        return
    data = json.loads(MANIFEST.read_text())
    if case == "duplicate":
        data["sources"][1] = data["sources"][0]
    elif case == "reordered":
        data["sources"][0], data["sources"][1] = data["sources"][1], data["sources"][0]
    else:
        data["sources"][0]["revision"] = "0" * 40
    changed = tmp_path / "changed-manifest.json"
    changed.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="manifest bytes"):
        acquire_source("SP01-SRC-001", changed, archive_root, transport=FakeTransport("SP01-SRC-001"))
    assert not any((archive_root / "quarantine").iterdir())


@pytest.mark.parametrize("source_id", ("SP01-SRC-001", "SP01-SRC-002", "SP01-SRC-003", "SP01-SRC-005", "SP01-SRC-006"))
def test_wrong_revision_or_rights_evidence_is_rejected(archive_root: Path, source_id: str) -> None:
    transport = FakeTransport(source_id)
    transport.revision = "0" * 40
    result = _acquire(archive_root, source_id, transport)
    assert result.decision.disposition == "REJECTED" and result.snapshot is None
    path = next(path for path, rights in source_transport._GITHUB_PATHS[source_id] if not rights)
    body = b"invalid"
    if source_id in {"SP01-SRC-001", "SP01-SRC-002"}:
        old, new = (b"1:5", b"1:6") if source_id.endswith("1") else (b"3AAI-S--", b"3PAI-S--")
        body = COMPONENTS[source_id][path].replace(old, new)
    changed = FakeTransport(source_id)
    changed.body_updates[path] = body
    assert _acquire(archive_root, source_id, changed).decision.disposition == "REJECTED"


def test_missing_rights_oversize_and_unexpected_final_path_are_rejected(
    archive_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    missing = FakeTransport("SP01-SRC-003")
    missing.body_updates["License.html"] = b"public domain; all rights reserved"
    missing_result = _acquire(archive_root, "SP01-SRC-003", missing)
    attempt = archive_root / missing_result.decision.quarantine_relative_path
    assert list((attempt / "responses").glob("*.bin"))

    oversize = FakeTransport("SP01-SRC-001")
    monkeypatch.setattr(source_transport, "MAX_COMPONENT_BYTES", 8)
    assert _acquire(archive_root, "SP01-SRC-001", oversize).decision.disposition == "REJECTED"

    unexpected = FakeTransport("SP01-SRC-005")
    unexpected.final_url_updates["abbott-smith.tei.xml"] = "https://raw.githubusercontent.com/other/path"
    assert _acquire(archive_root, "SP01-SRC-005", unexpected).decision.disposition == "REJECTED"


@pytest.mark.parametrize(
    ("source_id", "path", "rights", "reason"),
    (
        (
            "SP01-SRC-001",
            "LICENSE",
            b"Attribution 3.0 International",
            "SBLGNT_RIGHTS_EVIDENCE_NOT_FOUND",
        ),
        (
            "SP01-SRC-001",
            "LICENSE",
            b"Attribution 4.0 International\nlicense withdrawn",
            "SBLGNT_RIGHTS_EVIDENCE_CONTRADICTED",
        ),
        (
            "SP01-SRC-001",
            "LICENSE",
            b"This work is not licensed under the Creative Commons Attribution 4.0 International License.",
            "SBLGNT_RIGHTS_EVIDENCE_CONTRADICTED",
        ),
        (
            "SP01-SRC-002",
            "README.md",
            b"CC-BY-SA License\nhttps://creativecommons.org/licenses/by-sa/4.0/",
            "MORPHGNT_RIGHTS_EVIDENCE_NOT_FOUND",
        ),
        (
            "SP01-SRC-002",
            "README.md",
            b"Not licensed under the CC-BY-SA License. https://creativecommons.org/licenses/by-sa/3.0/",
            "MORPHGNT_RIGHTS_EVIDENCE_CONTRADICTED",
        ),
        (
            "SP01-SRC-002",
            "README.md",
            b"CC-BY-SA License\nhttps://creativecommons.org/licenses/by-sa/3.0/\nlicense replaced",
            "MORPHGNT_RIGHTS_EVIDENCE_CONTRADICTED",
        ),
        (
            "SP01-SRC-003",
            "License.html",
            b"No rights statement.",
            "ASV_RIGHTS_EVIDENCE_NOT_FOUND",
        ),
        (
            "SP01-SRC-003",
            "License.html",
            b"The American Standard Version is not in the public domain.",
            "ASV_RIGHTS_EVIDENCE_CONTRADICTED",
        ),
        (
            "SP01-SRC-005",
            "README.md",
            b"No rights statement.",
            "ABBOTT_SMITH_RIGHTS_EVIDENCE_NOT_FOUND",
        ),
        (
            "SP01-SRC-005",
            "README.md",
            b"The TEI lexicon is not in the public domain.",
            "ABBOTT_SMITH_RIGHTS_EVIDENCE_CONTRADICTED",
        ),
        (
            "SP01-SRC-006",
            "LICENSE.md",
            b"Copyright 2014 Adobe. All Rights Reserved.\nApache License 2.0",
            "SOURCE_SERIF_RIGHTS_EVIDENCE_NOT_FOUND",
        ),
        (
            "SP01-SRC-006",
            "LICENSE.md",
            b"All Rights Reserved.\nSIL Open Font License\nVersion 1.1\nSIL Open Font License grant is withdrawn",
            "SOURCE_SERIF_RIGHTS_EVIDENCE_CONTRADICTED",
        ),
        (
            "SP01-SRC-006",
            "LICENSE.md",
            b"This software is not distributed under the SIL Open Font License Version 1.1.",
            "SOURCE_SERIF_RIGHTS_EVIDENCE_CONTRADICTED",
        ),
        (
            "SP01-SRC-006",
            "LICENSE.md",
            b"SIL Open Font License\nVersion 1.1\nThe SIL Open Font License grant has been withdrawn.",
            "SOURCE_SERIF_RIGHTS_EVIDENCE_CONTRADICTED",
        ),
        (
            "SP01-SRC-006",
            "LICENSE.md",
            b"SIL Open Font License\nVersion 1.1\nThis license has been replaced by Apache 2.0.",
            "SOURCE_SERIF_RIGHTS_EVIDENCE_CONTRADICTED",
        ),
    ),
)
def test_source_specific_rights_failures_are_rejected(
    archive_root: Path, source_id: str, path: str, rights: bytes, reason: str
) -> None:
    transport = FakeTransport(source_id)
    transport.body_updates[path] = rights
    result = _acquire(archive_root, source_id, transport)
    assert result.decision.disposition == "REJECTED"
    assert result.decision.reasons == (reason,)


def test_identical_rerun_verifies_and_changed_rerun_does_not_replace(archive_root: Path) -> None:
    first = _acquire(archive_root, "SP01-SRC-001")
    snapshot_path = archive_root / "snapshots/source/SP01-SRC-001.json"
    original = snapshot_path.read_bytes()
    second = _acquire(archive_root, "SP01-SRC-001")
    assert second.verified_existing and second.snapshot == first.snapshot and snapshot_path.read_bytes() == original

    changed = FakeTransport("SP01-SRC-001")
    changed.body_updates["README.md"] = b"SBL Greek New Testament changed"
    rejected = _acquire(archive_root, "SP01-SRC-001", changed)
    assert rejected.decision.reasons == ("SNAPSHOT_IDENTITY_CHANGED",)
    assert rejected.snapshot is None and snapshot_path.read_bytes() == original

    authority = archive_root / first.snapshot.fetch_receipt_relative_path
    authority.chmod(0o644)
    assert _acquire(archive_root, "SP01-SRC-001").decision.disposition == "REJECTED"


def test_late_snapshot_fsync_failure_rolls_back_snapshot(archive_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    original = acquisition._fsync_directory
    failed = False

    def fail_snapshot(path: Path) -> None:
        nonlocal failed
        if path == archive_root / "snapshots/source" and not failed:
            failed = True
            raise OSError("synthetic late fsync failure")
        original(path)

    monkeypatch.setattr(acquisition, "_fsync_directory", fail_snapshot)
    result = _acquire(archive_root, "SP01-SRC-002")
    assert result.decision.disposition == "REJECTED"
    assert not (archive_root / "snapshots/source/SP01-SRC-002.json").exists()
    assert len(list((archive_root / result.decision.quarantine_relative_path).glob("*decision.json"))) == 1
    assert not list((archive_root / "manifests/source/SP01-SRC-002").glob("*.json"))


def _encrypted(package: bytes) -> bytes:
    changed = bytearray(package)
    for signature, offset in ((b"PK\x03\x04", 6), (b"PK\x01\x02", 8)):
        start = 0
        while (index := changed.find(signature, start)) >= 0:
            flags = int.from_bytes(changed[index + offset : index + offset + 2], "little") | 1
            changed[index + offset : index + offset + 2] = flags.to_bytes(2, "little")
            start = index + 4
    return bytes(changed)


def _web_rejection_reason(archive_root: Path, package: bytes) -> str:
    result = _acquire(archive_root, "SP01-SRC-004", FakeTransport("SP01-SRC-004", package=package))
    assert result.decision.disposition == "REJECTED"
    assert len(result.decision.reasons) == 1
    return result.decision.reasons[0]


def test_web_content_identity_accepts_exact_source_shaped_names(archive_root: Path) -> None:
    package = web_zip(
        john_name="73-JHNeng-web.usfm",
        john_text=(
            "\\id JHN World English Bible\n\\c 1\n"
            '\\v 5 \\w The|strong="G1722"\\w* \\w light|strong="G5457"\\w* \\w shines|strong="G5316"\\w* '
            '\\w in|strong="G1722"\\w* \\w the|strong="G1722"\\w* \\w darkness|strong="G4653"\\w*, '
            '\\w and|strong="G2532"\\w* \\w the|strong="G1722"\\w* \\w darkness|strong="G4653"\\w* '
            'hasn’t \\w overcome|strong="G3588"\\w* \\w it|strong="G2532"\\w*. \\p\n'
        ),
        rights_name="copr.htm",
        rights_text="World English Bible is public domain and is not copyrighted.",
    )
    result = _acquire(archive_root, "SP01-SRC-004", FakeTransport("SP01-SRC-004", package=package))
    assert result.decision.disposition == "ADMITTED"


def test_web_filename_only_john_match_does_not_establish_identity(archive_root: Path) -> None:
    package = web_zip(
        john_name="73-JHNeng-web.usfm",
        john_text=(
            "\\id GEN World English Bible\n\\c 1\n"
            "\\v 5 The light shines in the darkness, and the darkness hasn't overcome it.\n"
        ),
    )
    assert _web_rejection_reason(archive_root, package) == "WEB_JOHN_COMPONENT_NOT_FOUND"


def test_web_candidate_and_rights_failures_are_distinct(archive_root: Path) -> None:
    john_text = (
        "\\id JHN World English Bible\n\\c 1\n"
        "\\v 5 The light shines in the darkness, and the darkness hasn't overcome it.\n"
    )
    cases = (
        (
            web_zip(john_text=john_text, extra=("second.sfm", john_text.encode())),
            "WEB_JOHN_COMPONENT_AMBIGUOUS",
        ),
        (
            web_zip(john_text=john_text, rights_text="World English Bible rights statement."),
            "WEB_RIGHTS_EVIDENCE_NOT_FOUND",
        ),
        (
            web_zip(
                john_text=john_text.replace(" World English Bible", ""),
                rights_text="This translation is public domain.",
            ),
            "WEB_TRANSLATION_IDENTITY_NOT_FOUND",
        ),
        (
            web_zip(john_text=john_text, rights_text="World English Bible is public domain. All rights reserved."),
            "WEB_RIGHTS_EVIDENCE_CONTRADICTED",
        ),
    )
    for package, reason in cases:
        assert _web_rejection_reason(archive_root, package) == reason


def test_web_john_content_failures_are_distinct(archive_root: Path) -> None:
    missing = web_zip(john_text="\\id JHN World English Bible\n\\c 1\n\\v 4 Different verse.\n")
    ambiguous = web_zip(
        john_text=(
            "\\id JHN World English Bible\n\\c 1\n"
            "\\v 5 The light shines in the darkness, and the darkness hasn't overcome it.\n"
            "\\v 5 The light shines in the darkness, and the darkness hasn't overcome it.\n"
        )
    )
    mismatch = web_zip(john_text="\\id JHN World English Bible\n\\c 1\n\\v 5 Different text.\n")
    assert _web_rejection_reason(archive_root, missing) == "WEB_JOHN_1_5_NOT_FOUND"
    assert _web_rejection_reason(archive_root, ambiguous) == "WEB_JOHN_1_5_AMBIGUOUS"
    assert _web_rejection_reason(archive_root, mismatch) == "WEB_JOHN_1_5_CONTENT_MISMATCH"


def test_web_component_discovery_does_not_reconflate_john_and_rights() -> None:
    source = inspect.getsource(source_transport._web_components)
    assert "len(john) != 1 or not rights" not in source
    assert "WEB package lacks one John component or rights evidence" not in source


def _unix_entry(name: str, mode: int, data: bytes = b"ordinary text") -> tuple[zipfile.ZipInfo, bytes]:
    entry = zipfile.ZipInfo(name)
    entry.create_system = 3
    entry.external_attr = (stat.S_IFREG | mode) << 16
    return entry, data


@pytest.mark.parametrize("name", ("ordinary.usfm", "ordinary.txt", "ordinary.md", "rights"))
@pytest.mark.parametrize("mode", (0o644, 0o755))
def test_web_regular_files_accept_unix_permission_modes(archive_root: Path, name: str, mode: int) -> None:
    package = web_zip(extra=_unix_entry(name, mode))
    result = _acquire(archive_root, "SP01-SRC-004", FakeTransport("SP01-SRC-004", package=package))
    assert result.decision.disposition == "ADMITTED"


@pytest.mark.parametrize("suffix", sorted(source_transport._EXECUTABLE_EXTENSIONS))
def test_web_executable_extensions_remain_rejected(archive_root: Path, suffix: str) -> None:
    package = web_zip(extra=_unix_entry(f"ordinary{suffix}", 0o644))
    result = _acquire(archive_root, "SP01-SRC-004", FakeTransport("SP01-SRC-004", package=package))
    assert result.decision.disposition == "REJECTED"


@pytest.mark.parametrize("magic", source_transport._EXECUTABLE_MAGIC)
def test_web_executable_magic_remains_rejected(archive_root: Path, magic: bytes) -> None:
    package = web_zip(extra=_unix_entry("ordinary.txt", 0o644, magic + b" ordinary text"))
    result = _acquire(archive_root, "SP01-SRC-004", FakeTransport("SP01-SRC-004", package=package))
    assert result.decision.disposition == "REJECTED"


@pytest.mark.parametrize(
    ("case", "entry"),
    (
        ("traversal", ("../evil.txt", b"x")),
        ("absolute", ("/evil.txt", b"x")),
        ("nested-jar", ("nested.jar", b"PK")),
        ("script-executable", ("run.py", b"text")),
        ("macho-executable", ("data.txt", b"\xfe\xed\xfa\xcf")),
    ),
)
def test_web_unsafe_inventory_is_rejected(archive_root: Path, case: str, entry: tuple[str, bytes]) -> None:
    result = _acquire(archive_root, "SP01-SRC-004", FakeTransport("SP01-SRC-004", package=web_zip(extra=entry)))
    assert result.decision.disposition == "REJECTED", case


def test_web_symlink_encryption_and_inventory_limits_are_rejected(
    archive_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    link = zipfile.ZipInfo("link")
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    fifo = zipfile.ZipInfo("fifo")
    fifo.create_system = 3
    fifo.external_attr = (stat.S_IFIFO | 0o644) << 16
    packages = [web_zip(extra=(link, b"target")), web_zip(extra=(fifo, b"")), _encrypted(web_zip())]
    for package in packages:
        result = _acquire(archive_root, "SP01-SRC-004", FakeTransport("SP01-SRC-004", package=package))
        assert result.decision.disposition == "REJECTED"

    monkeypatch.setattr(source_transport, "MAX_ZIP_FILES", 1)
    assert _acquire(archive_root, "SP01-SRC-004").decision.disposition == "REJECTED"
    monkeypatch.setattr(source_transport, "MAX_ZIP_FILES", 1_000)
    monkeypatch.setattr(source_transport, "MAX_EXPANDED_BYTES", 10)
    assert _acquire(archive_root, "SP01-SRC-004").decision.disposition == "REJECTED"


def test_uninitialized_or_unverified_archive_fails_closed(archive_root: Path, tmp_path: Path) -> None:
    receipt_path = archive_root / f"registry/archive-initialization/{ARCHIVE_ID}.json"
    initialization = ArchiveInitializationReceipt.model_validate_json(receipt_path.read_bytes())
    changed = initialization.model_copy(update={"disposition": "VERIFIED_EXISTING"})
    receipt_path.chmod(0o644)
    _immutable(receipt_path, rfc8785.dumps(changed.model_dump(mode="json")))
    with pytest.raises(ValueError, match="initialization receipt"):
        _acquire(archive_root, "SP01-SRC-003")
    with pytest.raises(ValueError, match="root marker"):
        acquire_source(
            "SP01-SRC-003",
            MANIFEST,
            tmp_path,
            transport=FakeTransport("SP01-SRC-003"),
            _expected_archive_root=tmp_path.resolve(),
        )


def test_canonical_archive_root_binding_requires_explicit_private_test_seam(archive_root: Path, tmp_path: Path) -> None:
    canonical = Path("/Volumes/BSL-Archive/BiblicalScholarLab")
    acquisition._require_expected_archive_root(canonical, canonical)

    with pytest.raises(ValueError, match="canonical archive root"):
        acquire_source("SP01-SRC-001", MANIFEST, archive_root, transport=FakeTransport("SP01-SRC-001"))

    copied = tmp_path / "copied-initialized-archive"
    shutil.copytree(archive_root, copied)
    with pytest.raises(ValueError, match="canonical archive root"):
        acquire_source("SP01-SRC-001", MANIFEST, copied, transport=FakeTransport("SP01-SRC-001"))

    assert _acquire(archive_root, "SP01-SRC-001").decision.disposition == "ADMITTED"


def test_attempt_ids_are_exclusive(archive_root: Path) -> None:
    attempt_id = UUID("01890f29-7c00-7000-8000-000000000099")
    acquisition._attempt_directory(archive_root, "SP01-SRC-001", attempt_id)
    with pytest.raises(FileExistsError):
        acquisition._attempt_directory(archive_root, "SP01-SRC-001", attempt_id)


def test_cli_acquire_outputs_machine_readable_success_and_errors(
    archive_root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    result = _acquire(archive_root, "SP01-SRC-006")
    monkeypatch.setattr(cli, "acquire_source", lambda *_args: result)
    argv = [
        "source",
        "acquire",
        "--source-id",
        "SP01-SRC-006",
        "--manifest",
        str(MANIFEST),
        "--archive-root",
        str(archive_root),
    ]
    assert cli.main(argv) == 0
    json.loads(capsys.readouterr().out)
    assert cli.main(["source", "acquire", "--all"]) == 2
    assert json.loads(capsys.readouterr().out)["error"]["code"] == "INVALID_CLI_INPUT"


@pytest.mark.parametrize(
    "response",
    (
        HttpResponse("https://example.test", "https://example.test", 404, (), b""),
        HttpResponse("https://example.test", "https://example.test", 200, (), b"", ("https://redirect",)),
        HttpResponse("https://example.test", "http://example.test", 200, (), b""),
    ),
)
def test_response_metadata_failures_are_explicit(response: HttpResponse) -> None:
    with pytest.raises(ValueError):
        source_transport._checked_response(response, "https://example.test", 10)
    outside = HttpResponse(
        source_transport.WEB_PACKAGE_URL,
        "https://outside.test/package.zip",
        200,
        (),
        b"",
        ("https://outside.test/package.zip",),
    )
    with pytest.raises(ValueError, match="approved host"):
        source_transport._checked_response(outside, source_transport.WEB_PACKAGE_URL, 10, allow_redirects=True)
    with pytest.raises(ValueError, match="approved host"):
        source_transport._BoundedRedirectHandler().redirect_request(None, None, 302, "", {}, "https://outside.test")


def test_redirect_diagnostics_are_distinct() -> None:
    handler = source_transport._BoundedRedirectHandler()
    handler.history = [source_transport.WEB_PACKAGE_URL] * source_transport.MAX_REDIRECTS
    with pytest.raises(ValueError, match="exceeds the limit"):
        handler.redirect_request(None, None, 302, "", {}, source_transport.WEB_PACKAGE_URL)
    with pytest.raises(ValueError, match="not HTTPS"):
        source_transport._BoundedRedirectHandler().redirect_request(None, None, 302, "", {}, "http://ebible.org")


@pytest.mark.parametrize(
    ("repository", "reason"),
    (
        (None, "lacks a repository"),
        ("http://github.com/owner/repository", "not HTTPS"),
        ("https://example.test/owner/repository", "unapproved host"),
        ("https://github.com/owner/repository/", "not canonical"),
        ("https://github.com/owner", "must contain owner and repository"),
        ("https://github.com/./repository", "unsafe path component"),
    ),
)
def test_repository_identity_diagnostics_are_distinct(repository: str | None, reason: str) -> None:
    with pytest.raises(ValueError, match=reason):
        source_transport._repository_parts(repository)


def test_request_binding_and_metadata_shape_diagnostics_are_distinct() -> None:
    response = HttpResponse("https://requested.test", "https://requested.test", 200, (), b"")
    with pytest.raises(ValueError, match="request URL is not HTTPS"):
        source_transport._checked_response(response, "http://requested.test", 10)
    with pytest.raises(ValueError, match="does not match"):
        source_transport._checked_response(response, "https://different.test", 10)

    source = acquisition._source(MANIFEST, "SP01-SRC-001").plan

    def metadata(body: bytes):
        def fetch(url: str, _limit: int) -> HttpResponse:
            return HttpResponse(url, url, 200, (), body)

        return fetch

    with pytest.raises(ValueError, match="invalid JSON"):
        source_transport._metadata_revision(source, "owner", "repository", metadata(b"{"))
    with pytest.raises(ValueError, match="not an object"):
        source_transport._metadata_revision(source, "owner", "repository", metadata(b"[]"))
    with pytest.raises(ValueError, match="not UTF-8"):
        source_validation._text({"component": b"\xff"}, "component")


@pytest.mark.parametrize(
    ("name", "reason"),
    (
        ("", "empty path"),
        ("/absolute", "absolute path"),
        ("C:\\absolute", "absolute path"),
        ("directory\\file", "non-POSIX path"),
        ("directory//file", "nondeterministic path"),
        ("directory/../file", "path traversal"),
    ),
)
def test_zip_path_diagnostics_are_distinct(name: str, reason: str) -> None:
    with pytest.raises(ValueError, match=reason):
        source_transport._validate_zip_path(name)


def test_empty_zip_and_text_decoding_diagnostics_are_distinct() -> None:
    stream = BytesIO()
    with zipfile.ZipFile(stream, "w"):
        pass
    with pytest.raises(ValueError, match="no ZIP members"):
        source_transport._web_components(stream.getvalue())

    stream = BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("directory/", b"")
    with pytest.raises(ValueError, match="no files"):
        source_transport._web_components(stream.getvalue())

    files, _inventory = source_transport._web_components(web_zip(extra=("undecodable.txt", b"\xff")))
    assert files
    with pytest.raises(ValueError, match="WEB_JOHN_COMPONENT_NOT_UTF8"):
        source_transport._validate_web_evidence(b"\xff", ())
    with pytest.raises(ValueError, match="unmatched inline note terminator"):
        source_transport._without_usfm_notes("\\f*")


def test_web_source_identity_diagnostics_are_distinct() -> None:
    source = acquisition._source(MANIFEST, "SP01-SRC-004").plan
    with pytest.raises(ValueError, match="package URL"):
        source_transport.fetch_web(
            source.model_copy(update={"package": "https://ebible.org/other.zip"}), FakeTransport("SP01-SRC-004")
        )
    with pytest.raises(ValueError, match="revision policy"):
        source_transport.fetch_web(source.model_copy(update={"revision": "changed"}), FakeTransport("SP01-SRC-004"))


def test_https_transport_success_and_failure_are_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    response = MagicMock(status=200, url="https://example.test/file", headers={"X-Test": "value"})
    response.__enter__.return_value = response
    response.read.return_value = b"body"
    opener = MagicMock()
    opener.open.return_value = response
    monkeypatch.setattr(source_transport, "build_opener", lambda _handler: opener)
    assert source_transport.https_transport("https://example.test/file", 4).body == b"body"
    opener.open.side_effect = OSError("synthetic failure")
    with pytest.raises(SourceTransportError):
        source_transport.https_transport("https://example.test/file", 4)
    opener.open.side_effect = source_transport.HTTPError("https://example.test/file", 404, "", {}, BytesIO(b"error"))
    assert source_transport.https_transport("https://example.test/file", 4).status == 404
    with pytest.raises(ValueError, match="HTTPS"):
        source_transport.https_transport("http://example.test/file", 4)


def test_unresolved_transport_retains_decision(archive_root: Path) -> None:
    def unavailable(_url: str, _limit: int) -> HttpResponse:
        raise SourceTransportError("synthetic unavailable")

    unresolved = acquire_source(
        "SP01-SRC-005",
        MANIFEST,
        archive_root,
        transport=unavailable,
        _expected_archive_root=archive_root.resolve(),
    )
    assert unresolved.decision.disposition == "UNRESOLVED"


def test_web_bad_zip_identity_and_content_failures(archive_root: Path) -> None:
    cases = (
        b"not-a-zip",
        web_zip(
            john_text="\\id GEN World English Bible\n\\c 1\n"
            "\\v 5 The light shines in the darkness, and the darkness hasn't overcome it.\n"
        ),
        web_zip(john_text="\\id JHN World English Bible\n\\c 1\n\\v 5 Different text.\n"),
    )
    for package in cases:
        result = _acquire(archive_root, "SP01-SRC-004", FakeTransport("SP01-SRC-004", package=package))
        assert result.decision.disposition == "REJECTED"


def test_web_cross_reference_is_excluded_and_unbounded_note_is_rejected(archive_root: Path) -> None:
    cross_reference = web_zip(
        john_text=(
            "\\id JHN World English Bible\n\\c 1\n"
            "\\v 5 The light shines in the darkness, \\x + \\xo 1:5 \\xt synthetic reference \\x* "
            "and the darkness hasn’t overcome it.\n"
        )
    )
    admitted = _acquire(
        archive_root,
        "SP01-SRC-004",
        FakeTransport("SP01-SRC-004", package=cross_reference),
    )
    assert admitted.decision.disposition == "ADMITTED"

    unbounded = web_zip(
        john_text=(
            "\\id JHN World English Bible\n\\c 1\n"
            "\\v 5 The light shines in the darkness, \\f + \\ft unbounded note "
            "and the darkness hasn't overcome it.\n"
        )
    )
    rejected = _acquire(
        archive_root,
        "SP01-SRC-004",
        FakeTransport("SP01-SRC-004", package=unbounded),
    )
    assert rejected.decision.disposition == "REJECTED"


def test_cross_field_contract_rejections(archive_root: Path) -> None:
    result = _acquire(archive_root, "SP01-SRC-004")
    assert result.fetch_receipt and result.snapshot
    fetch = result.fetch_receipt.model_dump(mode="json")
    for update in ({"source_spec": fetch["source_spec"] | {"name": "changed"}}, {"package_sha256": "0" * 64}):
        with pytest.raises(ValidationError):
            FetchReceipt.model_validate(fetch | update)

    decision = result.decision.model_dump(mode="json")
    with pytest.raises(ValidationError):
        AdmissionDecision.model_validate(decision | {"reasons": ["contradiction"]})

    snapshot = result.snapshot.model_dump(mode="json")
    with pytest.raises(ValidationError):
        SourceSnapshot.model_validate(snapshot | {"attribution": "changed"})
