from __future__ import annotations

import hashlib
import json
import socket
import stat
from pathlib import Path

import pytest
import rfc8785
from test_source_acquisition import _acquire

import bsl.application.john15_normalization as normalization
import bsl.infrastructure.normalization_store as normalization_store
import bsl.interfaces.cli as cli
from bsl.infrastructure.normalization_store import canonical_bundle_bytes, publication_paths
from bsl.interfaces.cli import main

IMPLEMENTATION_COMMIT = "a" * 40
SOURCE_IDS = tuple(f"SP01-SRC-00{index}" for index in range(1, 7))


@pytest.fixture(autouse=True)
def no_normalization_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def blocked(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("external network access attempted")

    monkeypatch.setattr(socket.socket, "connect", blocked)


@pytest.fixture
def admitted_archive(tmp_path: Path) -> Path:
    from test_source_acquisition import archive_root

    initialized_archive_root = archive_root.__wrapped__(tmp_path)
    for source_id in SOURCE_IDS:
        result = _acquire(initialized_archive_root, source_id)
        assert result.snapshot is not None and result.decision.disposition == "ADMITTED"
    return initialized_archive_root


def _normalize(root: Path, *, dry_run: bool):
    return normalization.normalize_john15(
        root,
        dry_run=dry_run,
        _expected_archive_root=root.resolve(),
        _implementation_commit=IMPLEMENTATION_COMMIT,
    )


def test_dry_run_builds_stable_source_bound_bundle_without_writes(admitted_archive: Path) -> None:
    before = normalization.authority_fingerprint(
        admitted_archive,
        normalization._load_authoritative_sources(admitted_archive, admitted_archive.resolve())[1],
    )
    first = _normalize(admitted_archive, dry_run=True)
    second = _normalize(admitted_archive, dry_run=True)
    bundle = first.bundle

    assert canonical_bundle_bytes(bundle) == canonical_bundle_bytes(second.bundle)
    assert bundle.bundle_identity == second.bundle.bundle_identity
    assert tuple(source.source_id for source in bundle.sources) == SOURCE_IDS
    assert bundle.sblgnt.exact_source_view is not bundle.sblgnt.unicode_nfc_display_view
    assert (
        bundle.sblgnt.exact_source_view.utf8_sha256
        == hashlib.sha256(bundle.sblgnt.exact_source_view.text.encode()).hexdigest()
    )
    assert len(bundle.morphgnt.tokens) == 13
    assert [token.bcv for token in bundle.morphgnt.tokens] == ["040105"] * 13
    for token in bundle.morphgnt.tokens:
        assert bundle.sblgnt.exact_source_view.text[token.sblgnt_start : token.sblgnt_end] == token.text_alignment
    assert bundle.morphgnt.target_verb.model_dump() == {
        "token_index": 12,
        "source_form": "κατέλαβεν",
        "lemma": "καταλαμβάνω",
        "parsing_code": "3AAI-S--",
        "person": "third",
        "number": "singular",
        "tense": "aorist",
        "voice": "active",
        "mood": "indicative",
    }
    assert bundle.asv.canonical_realization.text == (
        "And the light shineth in the darkness; and the darkness apprehended it not."
    )
    assert bundle.web_classic.canonical_realization.text == (
        "The light shines in the darkness, and the darkness hasn’t overcome it."
    )
    assert {item.tag for item in bundle.abbott_smith.ordered_structure} >= {"entry", "form", "sense", "gloss", "ref"}
    assert (
        bundle.abbott_smith.source_entry_sha256
        == hashlib.sha256(bundle.abbott_smith.source_entry_utf8.encode()).hexdigest()
    )
    assert any("osisRef=John.1.5" in locator for locator in bundle.abbott_smith.locators)
    assert bundle.source_serif.scholarly_evidence is False
    assert first.receipt.disposition == second.receipt.disposition == "DRY_RUN_VALIDATED"
    assert first.receipt.bundle_canonical_sha256 == second.receipt.bundle_canonical_sha256
    assert first.published is second.published is False
    assert first.verified_existing is second.verified_existing is False
    assert not (admitted_archive / "snapshots/normalization").exists()
    assert not (admitted_archive / "manifests/normalization").exists()
    after = normalization.authority_fingerprint(
        admitted_archive,
        normalization._load_authoritative_sources(admitted_archive, admitted_archive.resolve())[1],
    )
    assert before == after


@pytest.mark.parametrize(
    "case", ("missing", "extra", "mutable", "corrupt", "wrong-source", "wrong-rights", "wrong-hash", "wrong-byte-count")
)
def test_exact_source_authority_failures_are_closed(admitted_archive: Path, case: str) -> None:
    snapshot_path = admitted_archive / "snapshots/source/SP01-SRC-001.json"
    snapshot = json.loads(snapshot_path.read_text())
    if case == "missing":
        snapshot_path.unlink()
    elif case == "extra":
        extra = snapshot_path.parent / "SP01-SRC-007.json"
        extra.write_text("{}")
        extra.chmod(0o444)
    elif case == "mutable":
        snapshot_path.chmod(0o644)
    elif case == "corrupt":
        snapshot_path.chmod(0o644)
        snapshot_path.write_text("not-json")
        snapshot_path.chmod(0o444)
    elif case in {"wrong-source", "wrong-rights", "wrong-byte-count"}:
        if case == "wrong-source":
            snapshot["source_id"] = "SP01-SRC-002"
        elif case == "wrong-rights":
            snapshot["attribution"] = "changed rights"
        else:
            snapshot["objects"][0]["byte_count"] += 1
        snapshot_path.chmod(0o644)
        snapshot_path.write_bytes(rfc8785.dumps(snapshot))
        snapshot_path.chmod(0o444)
    else:
        object_hash = snapshot["objects"][0]["sha256"]
        object_path = admitted_archive / f"objects/sha256/{object_hash[:2]}/{object_hash}"
        object_path.chmod(0o644)
        object_path.write_bytes(b"corrupt")
        object_path.chmod(0o444)

    with pytest.raises(ValueError):
        _normalize(admitted_archive, dry_run=True)


@pytest.mark.parametrize("case", ("alignment", "target-duplicate", "parsing"))
def test_morphgnt_alignment_target_and_grammar_mismatches_fail(
    admitted_archive: Path, monkeypatch: pytest.MonkeyPatch, case: str
) -> None:
    original = normalization._read_source_object

    def changed(root: Path, snapshot, relative_path: str) -> bytes:
        data = original(root, snapshot, relative_path)
        if relative_path != "64-Jn-morphgnt.txt":
            return data
        text = data.decode()
        if case == "alignment":
            text = text.replace("040105 C- -------- καὶ καὶ", "040105 C- -------- δὲ καὶ", 1)
        elif case == "target-duplicate":
            text = text.replace("040105 C- -------- καὶ καὶ καί καί", "040105 C- -------- καὶ καὶ καί καταλαμβάνω", 1)
        else:
            text = text.replace("3AAI-S-- κατέλαβεν.", "3PAI-S-- κατέλαβεν.", 1)
        return text.encode()

    monkeypatch.setattr(normalization, "_read_source_object", changed)
    with pytest.raises(ValueError):
        _normalize(admitted_archive, dry_run=True)


@pytest.mark.parametrize(
    ("text", "count"),
    (
        ("\\id JHN\n\\c 1\n\\v 4 absent", 0),
        ("\\id JHN\n\\c 1\n\\v 5 one", 1),
        ("\\id JHN\n\\c 1\n\\v 5 one\n\\v 5 two", 2),
    ),
)
def test_web_zero_one_and_multiple_target_states(text: str, count: int) -> None:
    assert normalization._web_verse(text)[0] == count  # pyright: ignore[reportPrivateUsage]


def test_temporary_publication_is_atomic_read_only_and_idempotent(admitted_archive: Path) -> None:
    published = _normalize(admitted_archive, dry_run=False)
    bundle_bytes = canonical_bundle_bytes(published.bundle)
    paths = publication_paths(hashlib.sha256(bundle_bytes).hexdigest())
    retained = tuple(admitted_archive / path for path in paths)

    assert published.published and published.receipt.disposition == "PUBLISHED"
    assert all(path.exists() and stat.S_IMODE(path.stat().st_mode) == 0o444 for path in retained)
    identities = tuple((path.stat().st_mtime_ns, hashlib.sha256(path.read_bytes()).hexdigest()) for path in retained)
    verified = _normalize(admitted_archive, dry_run=False)
    assert verified.verified_existing and verified.receipt.disposition == "VERIFIED_EXISTING"
    assert identities == tuple(
        (path.stat().st_mtime_ns, hashlib.sha256(path.read_bytes()).hexdigest()) for path in retained
    )
    assert not any((admitted_archive / ".incoming").iterdir())

    retained[1].chmod(0o644)
    retained[1].write_bytes(b"changed existing bundle")
    retained[1].chmod(0o444)
    with pytest.raises(ValueError, match="differs or is corrupt"):
        _normalize(admitted_archive, dry_run=False)
    assert retained[1].read_bytes() == b"changed existing bundle"


def test_publication_failure_rolls_back_and_empties_its_stage(
    admitted_archive: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    real_link = normalization_store.os.link

    def fail_snapshot(source: Path, destination: Path, *, follow_symlinks: bool = True) -> None:
        if source.name == "snapshot":
            raise OSError("injected publication failure")
        real_link(source, destination, follow_symlinks=follow_symlinks)

    monkeypatch.setattr(normalization_store.os, "link", fail_snapshot)
    with pytest.raises(OSError, match="injected publication failure"):
        _normalize(admitted_archive, dry_run=False)
    assert not (admitted_archive / "snapshots/normalization").exists()
    assert not (admitted_archive / "manifests/normalization").exists()
    assert not any((admitted_archive / ".incoming").iterdir())


def test_cli_emits_success_and_error_json_without_a_root_bypass(
    admitted_archive: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    result = _normalize(admitted_archive, dry_run=True)
    monkeypatch.setattr(cli, "normalize_john15", lambda _root, *, dry_run: result)
    assert main(["normalize", "john-1-5", "--archive-root", str(admitted_archive), "--dry-run"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["receipt"]["disposition"] == "DRY_RUN_VALIDATED"
    assert output["published"] is output["verified_existing"] is False
    assert (
        main(
            [
                "normalize",
                "john-1-5",
                "--archive-root",
                str(admitted_archive),
                "--expected-root",
                str(admitted_archive),
            ]
        )
        == 2
    )
    assert json.loads(capsys.readouterr().out)["error"]["code"] == "INVALID_CLI_INPUT"

    def failed(_root: Path, *, dry_run: bool):
        raise ValueError("closed failure")

    monkeypatch.setattr(cli, "normalize_john15", failed)
    assert main(["normalize", "john-1-5", "--archive-root", str(admitted_archive), "--dry-run"]) == 2
    assert json.loads(capsys.readouterr().out)["error"]["code"] == "OPERATION_FAILED"
