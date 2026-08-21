from __future__ import annotations

import hashlib
import json
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
        "LICENSE": b"Creative Commons Attribution 4.0 International",
        "data/sblgnt/text/John.txt": "1:5 καὶ τὸ φῶς ἐν τῇ σκοτίᾳ φαίνει, καὶ ἡ σκοτία αὐτὸ οὐ κατέλαβεν.\n".encode(),
    },
    "SP01-SRC-002": {
        "README.md": b"MorphGNT licensed CC BY-SA 3.0",
        "64-Jn-morphgnt.txt": "430105 V- 3SAAI-S κατέλαβεν κατέλαβεν κατέλαβεν καταλαμβάνω\n".encode(),
    },
    "SP01-SRC-003": {
        "README.md": b"American Standard Version",
        "License.html": b"This edition is public domain.",
        "usx/43-JHN.usx": (
            b"<usx><chapter number='1'/><verse number='5'/>And the light shineth in the darkness; "
            b"and the darkness apprehended it not.<verse eid='JHN 1:5'/></usx>"
        ),
    },
    "SP01-SRC-005": {
        "abbott-smith.tei.xml": "<TEI xmlns='u'><entry><form><orth>καταλαμβάνω</orth></form></entry></TEI>".encode(),
        "README.md": b"The TEI lexicon is public domain; the PDF is restricted.",
    },
    "SP01-SRC-006": {
        "TTF/SourceSerif4-Regular.ttf": synthetic_sfnt(b"reg!"),
        "TTF/SourceSerif4-It.ttf": synthetic_sfnt(b"ita!"),
        "LICENSE.md": b"SIL OPEN FONT LICENSE Version 1.1",
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
    john_text: str = (
        "\\id JHN World English Bible\n\\c 1\n"
        "\\v 5 The light shines in the darkness, and the darkness hasn't overcome it.\n"
    ),
) -> bytes:
    stream = BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("eng-web/", b"")
        archive.writestr("eng-web/43JHNeng-web.usfm", john_text)
        archive.writestr("eng-web/README.txt", "World English Bible eng-web is public domain.")
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
    return acquire_source(source_id, MANIFEST, root, transport=transport or FakeTransport(source_id))


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
        old, new = (b"1:5", b"1:6") if source_id.endswith("1") else (b"3SAAI", b"3SPAI")
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
    packages = [web_zip(extra=(link, b"target")), _encrypted(web_zip())]
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
    with pytest.raises(ValueError, match="initialized"):
        _acquire(archive_root, "SP01-SRC-003")
    with pytest.raises(ValueError, match="initialized"):
        acquire_source("SP01-SRC-003", MANIFEST, tmp_path, transport=FakeTransport("SP01-SRC-003"))


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
    with pytest.raises(ValueError, match="unsafe"):
        source_transport._BoundedRedirectHandler().redirect_request(None, None, 302, "", {}, "https://outside.test")


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

    unresolved = acquire_source("SP01-SRC-005", MANIFEST, archive_root, transport=unavailable)
    assert unresolved.decision.disposition == "UNRESOLVED"


def test_web_bad_zip_identity_and_content_failures(archive_root: Path) -> None:
    cases = (
        b"not-a-zip",
        web_zip(extra=("eng-web/44JHN-copy.usfm", b"\\v 5 duplicate")),
        web_zip(
            john_text="\\id GEN World English Bible\n\\c 1\n"
            "\\v 5 The light shines in the darkness, and the darkness hasn't overcome it.\n"
        ),
        web_zip(john_text="\\id JHN World English Bible\n\\c 1\n\\v 5 Different text.\n"),
    )
    for package in cases:
        result = _acquire(archive_root, "SP01-SRC-004", FakeTransport("SP01-SRC-004", package=package))
        assert result.decision.disposition == "REJECTED"


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
