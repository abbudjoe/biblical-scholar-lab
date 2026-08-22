from __future__ import annotations

import copy
import hashlib
import json
import shutil
import socket
import stat
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest
import rfc8785
from uuid6 import uuid7

import bsl.application.john15_evidence as evidence
import bsl.infrastructure.evidence_store as evidence_store
import bsl.interfaces.cli as cli
from bsl.contracts.evidence import (
    John15TranslationNuanceEvidencePacket,
    John15TranslationNuanceEvidenceReceipt,
    load_frozen_spec,
)
from bsl.contracts.normalization import NormalizationReceipt
from bsl.interfaces.cli import main

IMPLEMENTATION_COMMIT = "a" * 40
SOURCE_SNAPSHOTS = tuple(f"{index:064x}" for index in range(1, 7))
SOURCE_CONTENT = tuple(f"{index:064x}" for index in range(11, 17))


@pytest.fixture(autouse=True)
def deny_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def blocked(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("external network access attempted")

    monkeypatch.setattr(socket.socket, "connect", blocked)


def _item(
    order: int,
    parent: int | None,
    tag: str,
    text: str | None = None,
    attributes: tuple[tuple[str, str], ...] = (),
) -> SimpleNamespace:
    return SimpleNamespace(order=order, parent_order=parent, tag=tag, text=text, attributes=attributes)


def _fake_bundle(case: str | None = None) -> SimpleNamespace:
    target = SimpleNamespace(
        token_index=0,
        source_form="κατέλαβεν",
        lemma="καταλαμβάνω",
        person="third",
        number="singular",
        tense="aorist",
        voice="active",
        mood="indicative",
    )
    token = SimpleNamespace(word="κατέλαβεν", lemma="καταλαμβάνω", parsing_code="3AAI-S--", text_alignment="κατέλαβεν.")
    structure = (
        _item(0, None, "entry", attributes=(("n", "καταλαμβάνω|G2638"),)),
        _item(1, 0, "sense", attributes=(("n", "1."),)),
        _item(2, 1, "gloss", "to lay hold of"),
        _item(3, 1, "gloss", "seize"),
        _item(4, 1, "gloss", "appropriate"),
        _item(5, 0, "sense", attributes=(("n", "2."),)),
        _item(6, 5, "gloss", "to overtake"),
        _item(7, 5, "ref", attributes=(("osisRef", "John.1.5"),)),
        _item(8, 5, "ref", attributes=(("osisRef", "John.12.35"),)),
        _item(9, 0, "sense", "Of mental action", (("n", "3."),)),
        _item(10, 9, "gloss", "to apprehend"),
        _item(11, 9, "gloss", "comprehend"),
        _item(12, 9, "ref", attributes=(("osisRef", "Eph.3.18"),)),
    )
    bundle = SimpleNamespace(
        bundle_identity=evidence.BUNDLE_IDENTITY,
        normalization_specification_id="ACT-VS01-T03-JOHN-1-5-NORMALIZATION-v1",
        normalization_specification_sha256="ef3f8bd34d727a89bab5942c550006f0eda408d1f472ba2782fc2ccd519597e9",
        sources=tuple(
            SimpleNamespace(snapshot_identity=snapshot, content_identity=content)
            for snapshot, content in zip(SOURCE_SNAPSHOTS, SOURCE_CONTENT, strict=True)
        ),
        sblgnt=SimpleNamespace(
            exact_source_view=SimpleNamespace(text="καὶ τὸ φῶς ἐν τῇ σκοτίᾳ φαίνει, καὶ ἡ σκοτία αὐτὸ οὐ κατέλαβεν. ")
        ),
        morphgnt=SimpleNamespace(target_verb=target, tokens=(token,)),
        asv=SimpleNamespace(
            canonical_realization=SimpleNamespace(
                text="And the light shineth in the darkness; and the darkness apprehended it not."
            )
        ),
        web_classic=SimpleNamespace(
            canonical_realization=SimpleNamespace(
                text="The light shines in the darkness, and the darkness hasn’t overcome it."
            )
        ),
        abbott_smith=SimpleNamespace(selector='entry@n="καταλαμβάνω|G2638"', ordered_structure=structure),
        source_serif=SimpleNamespace(scholarly_evidence=False),
    )
    if case == "greek":
        bundle.sblgnt.exact_source_view.text = "changed"
    elif case == "morphology":
        target.tense = "present"
    elif case == "target-index":
        token.lemma = "changed"
    elif case == "asv":
        bundle.asv.canonical_realization.text = "changed"
    elif case == "web":
        bundle.web_classic.canonical_realization.text = "changed"
    elif case == "sense-2":
        structure[7].attributes = (("osisRef", "John.1.4"),)
    elif case == "sense-3":
        structure[12].attributes = (("osisRef", "John.1.5"),)
    elif case == "serif":
        bundle.source_serif.scholarly_evidence = True
    return bundle


def _normalization_receipt(
    *, bundle_sha: str = evidence.BUNDLE_SHA256, root: str | None = None
) -> NormalizationReceipt:
    return NormalizationReceipt(
        receipt_identity=UUID("01a02a37-79f8-7f29-abf7-a2dd9d7161ba"),
        generated_at=datetime(2026, 8, 22, tzinfo=UTC),
        implementation_commit=evidence.T03_IMPLEMENTATION_COMMIT,
        archive_root=root or str(evidence.CANONICAL_ARCHIVE_ROOT),
        disposition="PUBLISHED",
        dry_run=False,
        bundle_identity=evidence.BUNDLE_IDENTITY,
        bundle_canonical_sha256=bundle_sha,
        source_snapshot_identities=SOURCE_SNAPSHOTS,
        source_content_identities=SOURCE_CONTENT,
        publication_paths=(
            f"objects/sha256/{bundle_sha[:2]}/{bundle_sha}",
            evidence.T03_SNAPSHOT,
            evidence.T03_RECEIPT,
        ),
        archive_authority_fingerprint_before="d" * 64,
        archive_authority_fingerprint_after="e" * 64,
        published=True,
        verified_existing=False,
    )


def _authority(root: Path) -> evidence._T03Authority:  # pyright: ignore[reportPrivateUsage]
    return evidence._T03Authority(root, _fake_bundle(), _normalization_receipt(), "f" * 64)


def _packet(root: Path) -> John15TranslationNuanceEvidencePacket:
    authority = _authority(root)
    spec = load_frozen_spec()
    evidence.verify_source_evidence(authority.bundle, spec)
    return evidence._packet(authority, spec)  # pyright: ignore[reportPrivateUsage]


def _receipt(
    root: Path, packet: John15TranslationNuanceEvidencePacket, disposition: str = "PUBLISHED"
) -> John15TranslationNuanceEvidenceReceipt:
    packet_sha = hashlib.sha256(evidence_store.canonical_packet_bytes(packet)).hexdigest()
    state = {
        "PUBLISHED": (False, True, False),
        "DRY_RUN_VALIDATED": (True, False, False),
        "VERIFIED_EXISTING": (False, False, True),
    }[disposition]
    return John15TranslationNuanceEvidenceReceipt(
        receipt_identity=uuid7(),
        generated_at=datetime.now(UTC),
        implementation_commit=IMPLEMENTATION_COMMIT,
        archive_root=str(root),
        disposition=disposition,
        dry_run=state[0],
        input_bundle_identity=evidence.BUNDLE_IDENTITY,
        input_bundle_canonical_sha256=evidence.BUNDLE_SHA256,
        input_normalization_receipt_identity=packet.input_authority.normalization_receipt_identity,
        input_normalization_receipt_file_sha256=packet.input_authority.normalization_receipt_file_sha256,
        packet_identity=packet.packet_identity,
        packet_canonical_sha256=packet_sha,
        publication_paths=evidence_store.publication_paths(packet_sha),
        input_authority_fingerprint_before="a" * 64,
        input_authority_fingerprint_after="a" * 64,
        published=state[1],
        verified_existing=state[2],
    )


def _retain(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    path.chmod(0o444)


def test_exact_t03_raw_json_loader_uses_only_minimum_authority_trio(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from test_source_acquisition import archive_root

    root = archive_root.__wrapped__(tmp_path)
    for relative in ("snapshots/source", "manifests/source", "quarantine"):
        shutil.rmtree(root / relative)
    bundle_bytes = b'{"exact":"test-only-normalization-fixture"}'
    bundle_sha = hashlib.sha256(bundle_bytes).hexdigest()
    object_path = f"objects/sha256/{bundle_sha[:2]}/{bundle_sha}"
    monkeypatch.setattr(evidence, "BUNDLE_SHA256", bundle_sha)
    monkeypatch.setattr(evidence, "T03_OBJECT", object_path)
    receipt = _normalization_receipt(bundle_sha=bundle_sha)
    _retain(root / object_path, bundle_bytes)
    _retain(root / evidence.T03_SNAPSHOT, bundle_bytes)
    _retain(root / evidence.T03_RECEIPT, rfc8785.dumps(receipt.model_dump(mode="json")))
    seen: list[Path] = []
    original = evidence._retained_bytes  # pyright: ignore[reportPrivateUsage]

    def audited(path: Path):
        relative = path.relative_to(root)
        if relative.parts[:2] in {("snapshots", "source"), ("manifests", "source")} or "quarantine" in relative.parts:
            raise AssertionError("forbidden raw-source authority read")
        seen.append(relative)
        return original(path)

    monkeypatch.setattr(evidence, "_retained_bytes", audited)
    monkeypatch.setattr(
        evidence.John15NormalizationBundle,
        "model_validate_json",
        lambda raw: _fake_bundle() if raw == bundle_bytes else pytest.fail("loader did not validate raw bytes"),
    )
    authority = evidence.load_t03_authority(root, _expected_archive_root=root.resolve())
    assert authority.receipt.disposition == "PUBLISHED"
    assert {Path(object_path), Path(evidence.T03_SNAPSHOT), Path(evidence.T03_RECEIPT)} <= set(seen)
    assert not (root / "snapshots/source").exists()
    assert not (root / "manifests/source").exists()
    assert not (root / "quarantine").exists()
    assert tuple((root / "objects/sha256").rglob("*"))


def test_changed_claim_spec_bytes_fail_exact_hash(tmp_path: Path) -> None:
    changed = tmp_path / "claim-spec.json"
    changed.write_bytes(Path(evidence.load_frozen_spec.__defaults__[0]).read_bytes() + b"\n")
    with pytest.raises(ValueError, match="hash"):
        load_frozen_spec(changed)


def test_packet_has_exact_graph_counts_ids_links_and_status_asymmetry(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    assert (len(packet.evidence_items), len(packet.claims), len(packet.claim_evidence_links)) == (12, 16, 34)
    assert (len(packet.diagnoses), len(packet.accepted_alternatives), len(packet.prohibited_inferences)) == (3, 3, 17)
    evidence_ids = {item["evidence_id"] for item in packet.evidence_items}
    claim_ids = {item["claim_id"] for item in packet.claims}
    assert len(evidence_ids) == 12 and len(claim_ids) == 16
    assert all(
        link["claim_id"] in claim_ids and link["evidence_id"] in evidence_ids for link in packet.claim_evidence_links
    )
    assert {link["claim_id"] for link in packet.claim_evidence_links} == claim_ids
    alternatives = {item["alternative_id"]: item["epistemic_status"] for item in packet.accepted_alternatives}
    assert alternatives == {
        "ALT-T04-COGNITIVE": "PLAUSIBLE",
        "ALT-T04-CONFLICT": "STRONGLY_SUPPORTED",
        "ALT-T04-DOUBLE-RESONANCE": "PLAUSIBLE",
    }


@pytest.mark.parametrize("case", ("greek", "morphology", "target-index", "asv", "web", "sense-2", "sense-3", "serif"))
def test_source_verification_rejects_normalized_evidence_changes(case: str) -> None:
    with pytest.raises(ValueError):
        evidence.verify_source_evidence(_fake_bundle(case), load_frozen_spec())


@pytest.mark.parametrize(
    ("section", "mutate"),
    (
        ("evidence_items", lambda value: value + [copy.deepcopy(value[0])]),
        ("claims", lambda value: value[:-1]),
        ("claim_evidence_links", lambda value: [dict(value[0], evidence_id="missing")] + value[1:]),
        ("diagnoses", lambda value: [dict(value[0], packet_status="UNKNOWN")] + value[1:]),
        (
            "accepted_alternatives",
            lambda value: [dict(value[0], epistemic_status="DIRECTLY_ATTESTED")] + value[1:],
        ),
        ("prohibited_inferences", lambda value: value[:-1] + ["A theological conclusion follows."]),
        ("public_display_constraints", lambda value: value + ["Source Serif is scholarly evidence."]),
    ),
)
def test_contract_rejects_duplicate_referential_status_and_overclaim_mutations(
    tmp_path: Path, section: str, mutate
) -> None:
    data = _packet(tmp_path).model_dump(mode="json")
    data[section] = mutate(data[section])
    data["packet_identity"] = hashlib.sha256(
        rfc8785.dumps({key: value for key, value in data.items() if key != "packet_identity"})
    ).hexdigest()
    with pytest.raises(ValueError, match="frozen"):
        John15TranslationNuanceEvidencePacket.model_validate_json(rfc8785.dumps(data))


def test_packet_canonical_bytes_and_identity_are_stable(tmp_path: Path) -> None:
    first, second = _packet(tmp_path), _packet(tmp_path)
    assert evidence_store.canonical_packet_bytes(first) == evidence_store.canonical_packet_bytes(second)
    assert first.packet_identity == second.packet_identity
    assert not {"generated_at", "receipt_identity", "hostname", "username"} & set(type(first).model_fields)


@pytest.mark.parametrize("case", ("path", "state", "fingerprint"))
def test_receipt_rejects_path_disposition_and_dry_run_mutations(tmp_path: Path, case: str) -> None:
    packet = _packet(tmp_path)
    data = _receipt(tmp_path, packet, "DRY_RUN_VALIDATED").model_dump(mode="json")
    if case == "path":
        data["publication_paths"][0] = "objects/sha256/ff/" + "f" * 64
    elif case == "state":
        data["published"] = True
    else:
        data["input_authority_fingerprint_after"] = "b" * 64
    with pytest.raises(ValueError):
        John15TranslationNuanceEvidenceReceipt.model_validate_json(rfc8785.dumps(data))


def test_application_dry_run_writes_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "archive"
    root.mkdir()
    authority = _authority(root)
    monkeypatch.setattr(evidence, "load_t03_authority", lambda *_args, **_kwargs: authority)
    monkeypatch.setattr(evidence, "canonical_input_fingerprint", lambda _authority: "a" * 64)
    result = evidence.generate_john15_evidence(
        root, dry_run=True, _expected_archive_root=root, _implementation_commit=IMPLEMENTATION_COMMIT
    )
    assert result.receipt.disposition == "DRY_RUN_VALIDATED"
    assert result.published is result.verified_existing is False
    assert set(root.iterdir()) == set()


def test_application_fixture_publication_is_receipt_last_and_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "archive"
    (root / ".incoming").mkdir(parents=True)
    authority = _authority(root)
    monkeypatch.setattr(evidence, "load_t03_authority", lambda *_args, **_kwargs: authority)
    monkeypatch.setattr(evidence, "canonical_input_fingerprint", lambda _authority: "a" * 64)
    arguments = {
        "dry_run": False,
        "_expected_archive_root": root,
        "_implementation_commit": IMPLEMENTATION_COMMIT,
    }
    published = evidence.generate_john15_evidence(root, **arguments)
    existing = evidence.generate_john15_evidence(root, **arguments)
    assert published.published and published.receipt.disposition == "PUBLISHED"
    assert existing.verified_existing and existing.receipt.disposition == "VERIFIED_EXISTING"
    paths = tuple(root / path for path in published.receipt.publication_paths)
    assert all(path.exists() for path in paths)


@pytest.mark.parametrize(
    ("state", "retained", "disposition"),
    (
        ("none", 0, "PUBLISHED"),
        ("object", 1, "PUBLISHED"),
        ("object-snapshot", 2, "PUBLISHED"),
        ("complete", 3, "VERIFIED_EXISTING"),
    ),
)
def test_receipt_last_publication_recovers_exact_states(
    tmp_path: Path, state: str, retained: int, disposition: str
) -> None:
    root = tmp_path / state
    (root / ".incoming").mkdir(parents=True)
    packet = _packet(root)
    receipt = _receipt(root, packet)
    packet_bytes = evidence_store.canonical_packet_bytes(packet)
    packet_sha = hashlib.sha256(packet_bytes).hexdigest()
    paths = tuple(root / path for path in evidence_store.publication_paths(packet_sha))
    payloads = (packet_bytes, packet_bytes, rfc8785.dumps(receipt.model_dump(mode="json")))
    for path, data in zip(paths[:retained], payloads[:retained], strict=True):
        _retain(path, data)
    existing = evidence_store.prepare_publication(root, packet, packet_bytes)
    if existing is None:
        evidence_store.publish_evidence(root, packet, receipt)
    assert ("VERIFIED_EXISTING" if existing else "PUBLISHED") == disposition
    assert all(path.exists() and stat.S_IMODE(path.stat().st_mode) == 0o444 for path in paths)
    assert paths[0].read_bytes() == paths[1].read_bytes() == packet_bytes
    assert not evidence_store.evidence_stage_path(root, packet_sha).exists()


@pytest.mark.parametrize(
    "state",
    (
        "mismatched-object",
        "mismatched-snapshot",
        "receipt-no-object",
        "receipt-no-snapshot",
        "mismatched-receipt",
        "mismatched-stage",
    ),
)
def test_publication_rejects_mismatches_without_replacement(tmp_path: Path, state: str) -> None:
    root = tmp_path / state
    (root / ".incoming").mkdir(parents=True)
    packet = _packet(root)
    receipt = _receipt(root, packet)
    packet_bytes = evidence_store.canonical_packet_bytes(packet)
    packet_sha = hashlib.sha256(packet_bytes).hexdigest()
    paths = tuple(root / path for path in evidence_store.publication_paths(packet_sha))
    receipt_bytes = rfc8785.dumps(receipt.model_dump(mode="json"))
    retained: list[tuple[Path, bytes]]
    if state == "mismatched-object":
        retained = [(paths[0], b"changed")]
    elif state == "mismatched-snapshot":
        retained = [(paths[0], packet_bytes), (paths[1], b"changed")]
    elif state == "receipt-no-object":
        retained = [(paths[1], packet_bytes), (paths[2], receipt_bytes)]
    elif state == "receipt-no-snapshot":
        retained = [(paths[0], packet_bytes), (paths[2], receipt_bytes)]
    elif state == "mismatched-receipt":
        changed = receipt.model_copy(update={"archive_root": "changed"})
        retained = [
            (paths[0], packet_bytes),
            (paths[1], packet_bytes),
            (paths[2], rfc8785.dumps(changed.model_dump(mode="json"))),
        ]
    else:
        stage = evidence_store.evidence_stage_path(root, packet_sha)
        retained = [(stage / "object", b"changed")]
    for path, data in retained:
        _retain(path, data)
    with pytest.raises(ValueError):
        evidence_store.prepare_publication(root, packet, packet_bytes)
    assert all(path.read_bytes() == data for path, data in retained)


def test_publication_cleans_exact_stale_stage_and_preserves_unrelated_incoming(tmp_path: Path) -> None:
    root = tmp_path / "archive"
    (root / ".incoming").mkdir(parents=True)
    packet = _packet(root)
    receipt = _receipt(root, packet)
    packet_bytes = evidence_store.canonical_packet_bytes(packet)
    packet_sha = hashlib.sha256(packet_bytes).hexdigest()
    stage = evidence_store.evidence_stage_path(root, packet_sha)
    unrelated = root / ".incoming/unrelated-operation/evidence"
    _retain(unrelated, b"unrelated")
    for name, data in (
        ("object", packet_bytes),
        ("snapshot", packet_bytes),
        ("receipt", rfc8785.dumps(receipt.model_dump(mode="json"))),
    ):
        _retain(stage / name, data)
    evidence_store.publish_evidence(root, packet, receipt)
    assert unrelated.read_bytes() == b"unrelated" and not stage.exists()


def test_cli_success_error_json_and_no_root_bypass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    packet = _packet(tmp_path)
    result = evidence._EvidenceResult(packet, _receipt(tmp_path, packet, "DRY_RUN_VALIDATED"), False, False)
    monkeypatch.setattr(cli, "generate_john15_evidence", lambda _root, *, dry_run: result)
    command = ["evidence", "john-1-5-translation-nuance", "--archive-root", str(tmp_path), "--dry-run"]
    assert main(command) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["receipt"]["disposition"] == "DRY_RUN_VALIDATED"
    assert output["published"] is output["verified_existing"] is False
    assert main(command + ["--expected-root", str(tmp_path)]) == 2
    assert json.loads(capsys.readouterr().out)["error"]["code"] == "INVALID_CLI_INPUT"
    monkeypatch.setattr(
        cli, "generate_john15_evidence", lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("closed"))
    )
    assert main(command) == 2
    assert json.loads(capsys.readouterr().out)["error"]["code"] == "OPERATION_FAILED"


def test_no_network_model_database_retrieval_or_benchmark_surface() -> None:
    production = Path(evidence.__file__).read_text() + Path(evidence_store.__file__).read_text()
    forbidden = ("requests", "httpx", "openai", "anthropic", "sqlalchemy", "psycopg", "embedding", "benchmark")
    assert all(term not in production.lower() for term in forbidden)
