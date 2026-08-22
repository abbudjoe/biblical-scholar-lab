from __future__ import annotations

import copy
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
from bsl.contracts.normalization import John15NormalizationBundle, NormalizationReceipt
from bsl.infrastructure.normalization_store import (
    canonical_bundle_bytes,
    normalization_stage_path,
    prepare_publication,
    publication_paths,
)
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


def _retain(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    path.chmod(0o444)


def _publication_material(root: Path):
    result = _normalize(root, dry_run=True)
    bundle_bytes = canonical_bundle_bytes(result.bundle)
    receipt_data = result.receipt.model_dump(mode="json") | {
        "disposition": "PUBLISHED",
        "dry_run": False,
        "published": True,
    }
    receipt = NormalizationReceipt.model_validate_json(rfc8785.dumps(receipt_data))
    paths = tuple(root / path for path in publication_paths(hashlib.sha256(bundle_bytes).hexdigest()))
    return result.bundle, bundle_bytes, receipt, paths


def _bundle_payload(bundle: John15NormalizationBundle, case: str) -> dict:
    data = copy.deepcopy(bundle.model_dump(mode="json"))
    sources, morph = data["sources"], data["morphgnt"]
    mutations = {
        "snapshot-identity": lambda: sources[1].update(snapshot_identity=sources[0]["snapshot_identity"]),
        "content-identity": lambda: sources[1].update(content_identity=sources[0]["content_identity"]),
        "object-path": lambda: sources[0]["objects"][1].update(relative_path=sources[0]["objects"][0]["relative_path"]),
        "object-hash": lambda: sources[0]["objects"][1].update(sha256=sources[0]["objects"][0]["sha256"]),
        "sblgnt-binding": lambda: data["sblgnt"].update(source_object_sha256="f" * 64),
        "morphgnt-binding": lambda: morph.update(source_object_relative_path="wrong.txt"),
        "asv-source": lambda: data["asv"].update(source_id="SP01-SRC-004"),
        "web-source": lambda: data["web_classic"].update(source_id="SP01-SRC-003"),
        "web-package": lambda: data["web_classic"].update(package_sha256="f" * 64),
        "abbott-binding": lambda: data["abbott_smith"].update(source_object_sha256="f" * 64),
        "serif-regular": lambda: data["source_serif"]["regular_font"].update(relative_path="wrong.ttf"),
        "serif-italic": lambda: data["source_serif"]["italic_font"].update(sha256="f" * 64),
        "serif-license": lambda: data["source_serif"]["license_object"].update(rights_evidence=False),
        "span-order": lambda: morph["tokens"][1].update(sblgnt_start=0),
        "span-substring": lambda: morph["tokens"][0].update(text_alignment="wrong"),
        "target-index": lambda: morph["target_verb"].update(token_index=0),
        "target-lemma": lambda: morph["tokens"][-1].update(lemma="wrong"),
        "target-form": lambda: morph["tokens"][-1].update(word="wrong"),
        "target-parsing": lambda: morph["tokens"][-1].update(parsing_code="wrong"),
    }
    mutations[case]()
    data["bundle_identity"] = hashlib.sha256(
        rfc8785.dumps({key: value for key, value in data.items() if key != "bundle_identity"})
    ).hexdigest()
    return data


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
    "case",
    (
        "snapshot-identity",
        "content-identity",
        "object-path",
        "object-hash",
        "sblgnt-binding",
        "morphgnt-binding",
        "asv-source",
        "web-source",
        "web-package",
        "abbott-binding",
        "serif-regular",
        "serif-italic",
        "serif-license",
        "span-order",
        "span-substring",
        "target-index",
        "target-lemma",
        "target-form",
        "target-parsing",
    ),
)
def test_bundle_model_rejects_reidentified_cross_binding_mutations(admitted_archive: Path, case: str) -> None:
    bundle = _normalize(admitted_archive, dry_run=True).bundle
    with pytest.raises(ValueError):
        John15NormalizationBundle.model_validate_json(rfc8785.dumps(_bundle_payload(bundle, case)))


@pytest.mark.parametrize("case", ("publication-path", "snapshot-identity", "content-identity"))
def test_receipt_model_rejects_publication_and_identity_mutations(admitted_archive: Path, case: str) -> None:
    data = copy.deepcopy(_normalize(admitted_archive, dry_run=True).receipt.model_dump(mode="json"))
    if case == "publication-path":
        data["publication_paths"][0] = "objects/sha256/ff/" + "f" * 64
    else:
        field = {"snapshot-identity": "source_snapshot_identities", "content-identity": "source_content_identities"}[
            case
        ]
        data[field][1] = data[field][0]
    with pytest.raises(ValueError):
        NormalizationReceipt.model_validate_json(rfc8785.dumps(data))


def test_authority_fingerprint_hashes_actual_source_objects(admitted_archive: Path) -> None:
    snapshots = normalization._load_authoritative_sources(admitted_archive, admitted_archive.resolve())[1]
    first = normalization.authority_fingerprint(admitted_archive, snapshots)
    assert all(item["read_only_verified"] for item in first["objects"])
    selected = snapshots[0].objects[0]
    path = admitted_archive / f"objects/sha256/{selected.sha256[:2]}/{selected.sha256}"
    changed = bytes([path.read_bytes()[0] ^ 1]) + path.read_bytes()[1:]
    path.chmod(0o644)
    path.write_bytes(changed)
    path.chmod(0o444)
    with pytest.raises(ValueError, match="differs from snapshot authority"):
        normalization.authority_fingerprint(admitted_archive, snapshots)


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


@pytest.mark.parametrize(
    ("state", "retained_count", "disposition"),
    (
        ("none", 0, "PUBLISHED"),
        ("object", 1, "PUBLISHED"),
        ("object-snapshot", 2, "PUBLISHED"),
        ("complete", 3, "VERIFIED_EXISTING"),
        ("complete-stale-stage", 3, "VERIFIED_EXISTING"),
    ),
)
def test_publication_recovers_every_safe_commit_marker_state(
    admitted_archive: Path, state: str, retained_count: int, disposition: str
) -> None:
    bundle, bundle_bytes, receipt, paths = _publication_material(admitted_archive)
    payloads = (bundle_bytes, bundle_bytes, rfc8785.dumps(receipt.model_dump(mode="json")))
    for path, data in zip(paths[:retained_count], payloads[:retained_count], strict=True):
        _retain(path, data)
    stage = normalization_stage_path(admitted_archive, hashlib.sha256(bundle_bytes).hexdigest())
    if state == "complete-stale-stage":
        for name, data in zip(("object", "snapshot", "receipt"), payloads, strict=True):
            _retain(stage / name, data)
    result = _normalize(admitted_archive, dry_run=False)
    assert result.receipt.disposition == disposition
    assert all(path.exists() and stat.S_IMODE(path.stat().st_mode) == 0o444 for path in paths)
    assert paths[0].read_bytes() == paths[1].read_bytes() == bundle_bytes
    assert not stage.exists()


@pytest.mark.parametrize(
    "state",
    (
        "mismatched-object",
        "mismatched-snapshot",
        "mismatched-receipt",
        "receipt-no-snapshot",
        "receipt-no-object",
        "mismatched-stage",
    ),
)
def test_publication_rejects_unsafe_states_without_deleting_evidence(admitted_archive: Path, state: str) -> None:
    bundle, bundle_bytes, receipt, paths = _publication_material(admitted_archive)
    receipt_data = receipt.model_dump(mode="json")
    if state == "mismatched-receipt":
        receipt_data["bundle_identity"] = "f" * 64
    payloads = (bundle_bytes, bundle_bytes, rfc8785.dumps(receipt_data))
    retained: list[tuple[Path, bytes]] = []
    if state in {"mismatched-object", "mismatched-snapshot"}:
        count = 1 if state == "mismatched-object" else 2
        retained = list(zip(paths[:count], payloads[:count], strict=True))
        retained[-1] = (retained[-1][0], b"mismatched authority")
    elif state in {"mismatched-receipt", "receipt-no-snapshot"}:
        retained = [(paths[0], payloads[0]), (paths[2], payloads[2])]
        if state == "mismatched-receipt":
            retained.insert(1, (paths[1], payloads[1]))
    elif state == "receipt-no-object":
        retained = [(paths[1], payloads[1]), (paths[2], payloads[2])]
    else:
        stage = normalization_stage_path(admitted_archive, hashlib.sha256(bundle_bytes).hexdigest())
        retained = [(stage / "object", b"mismatched stage")]
    for path, data in retained:
        _retain(path, data)
    with pytest.raises(ValueError):
        _normalize(admitted_archive, dry_run=False)
    assert all(path.read_bytes() == data for path, data in retained)


def test_publication_preserves_unrelated_incoming_content(admitted_archive: Path) -> None:
    unrelated = admitted_archive / ".incoming/unrelated-operation/evidence"
    _retain(unrelated, b"unrelated")
    assert _normalize(admitted_archive, dry_run=False).published
    assert unrelated.read_bytes() == b"unrelated"


def test_interrupted_publication_retries_from_content_object(
    admitted_archive: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bundle, bundle_bytes, _receipt, paths = _publication_material(admitted_archive)
    real_link = normalization_store.os.link

    def fail_snapshot(source: Path, destination: Path, *, follow_symlinks: bool = True) -> None:
        if source.name == "snapshot":
            raise OSError("injected publication failure")
        real_link(source, destination, follow_symlinks=follow_symlinks)

    monkeypatch.setattr(normalization_store.os, "link", fail_snapshot)
    with pytest.raises(OSError, match="injected publication failure"):
        _normalize(admitted_archive, dry_run=False)
    stage = normalization_stage_path(admitted_archive, hashlib.sha256(bundle_bytes).hexdigest())
    assert paths[0].read_bytes() == bundle_bytes and stage.exists()
    monkeypatch.setattr(normalization_store.os, "link", real_link)
    assert _normalize(admitted_archive, dry_run=False).published
    assert all(path.exists() for path in paths) and not stage.exists()


def test_changed_bundle_never_replaces_complete_publication(admitted_archive: Path) -> None:
    published = _normalize(admitted_archive, dry_run=False)
    retained = tuple(admitted_archive / path for path in published.receipt.publication_paths)
    identities = tuple(path.read_bytes() for path in retained)
    data = published.bundle.model_dump(mode="json")
    data["normalization_methods"].append("changed method")
    data["bundle_identity"] = hashlib.sha256(
        rfc8785.dumps({key: value for key, value in data.items() if key != "bundle_identity"})
    ).hexdigest()
    changed = John15NormalizationBundle.model_validate_json(rfc8785.dumps(data))
    with pytest.raises(ValueError):
        prepare_publication(admitted_archive, changed, canonical_bundle_bytes(changed))
    assert tuple(path.read_bytes() for path in retained) == identities


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
