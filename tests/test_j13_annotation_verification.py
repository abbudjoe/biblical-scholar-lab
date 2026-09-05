import json
from copy import deepcopy

import pytest
import rfc8785
from jsonschema.exceptions import ValidationError as SchemaError
from test_j13_package_compilation import unicode_helper as unicode_helper
from test_source_acquisition import ARCHIVE_ID, CREATED, _immutable, archive_root
from test_source_acquisition import no_network as no_network

from bsl.application.j13_annotation_verification import verify_j13_annotation_batch
from bsl.contracts import source_admission as contracts
from bsl.infrastructure.j13_authority import (
    ROOT,
    inventory,
    load_j13_source_authority,
    load_j13_upstream_authority,
    sha,
)


def _changed(document, path, value):
    result = deepcopy(document)
    target = result
    parts = path.split("/")
    for part in parts[:-1]:
        target = target[int(part)] if isinstance(target, list) else target[part]
    target[int(parts[-1]) if isinstance(target, list) else parts[-1]] = value
    return result


def _snapshot(root, index, files):
    manifest = json.loads((ROOT / "design/approved/SOURCE-PLAN-01-source-admission-manifest.json").read_bytes())
    source_id = f"SP01-SRC-00{index}"
    spec = contracts.PlannedSource.model_validate_json(
        json.dumps(
            manifest["sources"][index - 1]
            | {
                "relative_quarantine_plan": f"quarantine/SOURCE-PLAN-01/{source_id}",
                "planned_manifest_identity": contracts.APPROVED_MANIFEST_SHA256,
                "pre_acquisition_stop_conditions": (
                    "SOURCE_ACQUISITION_NOT_AUTHORIZED_NOW",
                    *contracts.HARD_PROHIBITIONS,
                ),
            }
        )
    )
    objects = [
        {"relative_path": k, "sha256": sha(v), "byte_count": len(v), "rights_evidence": k == "README.md"}
        for k, v in files.items()
    ]
    package = sha(files["eng-web_usfm.zip"]) if index == 4 else None
    inventory_rows = [{k: v for k, v in objects[0].items() if k != "rights_evidence"}] if index == 4 else []
    shared = {
        "source_id": source_id,
        "manifest_identity": contracts.APPROVED_MANIFEST_SHA256,
        "source_spec": spec,
        "source_spec_sha256": contracts._source_spec_sha256(spec),
        "package_sha256": package,
        "objects": tuple(objects),
        "archive_inventory": tuple(inventory_rows),
        "objects_aggregate_sha256": sha(rfc8785.dumps(objects)),
    }
    fetch = contracts.FetchReceipt(
        **shared,
        receipt_id=ARCHIVE_ID,
        attempt_id=ARCHIVE_ID,
        generated_at=CREATED,
        resolved_revision=spec.revision,
        total_received_bytes=1,
        exchanges=(
            {
                "requested_url": "https://example.invalid/synthetic",
                "final_url": "https://example.invalid/synthetic",
                "status": 200,
                "redirect_chain": (),
                "headers": (),
                "response_sha256": "0" * 64,
                "retrieved_at": CREATED,
                "byte_count": 1,
            },
        ),
    )
    fetch_bytes = rfc8785.dumps(fetch.model_dump(mode="json"))
    decision = contracts.AdmissionDecision(
        decision_id=ARCHIVE_ID,
        attempt_id=ARCHIVE_ID,
        generated_at=CREATED,
        source_id=source_id,
        manifest_identity=contracts.APPROVED_MANIFEST_SHA256,
        disposition="ADMITTED",
        fetch_receipt_sha256=sha(fetch_bytes),
        admitted_object_sha256=tuple(dict.fromkeys(o["sha256"] for o in objects)),
        reasons=(),
        quarantine_relative_path=f"quarantine/SOURCE-PLAN-01/{source_id}/{ARCHIVE_ID}",
    )
    decision_bytes = rfc8785.dumps(decision.model_dump(mode="json"))
    operations, attribution = contracts._source_rights(spec)
    prefix = f"manifests/source/{source_id}/{ARCHIVE_ID}"
    model = contracts.SourceSnapshot.model_construct(
        **{**shared, "objects": fetch.objects, "archive_inventory": fetch.archive_inventory},
        acquired_at=CREATED,
        retrieval_urls=("https://example.invalid/synthetic",),
        http_metadata_sha256=sha(rfc8785.dumps([e.model_dump(mode="json") for e in fetch.exchanges])),
        allowed_operations=operations,
        attribution=attribution,
        language_identity="grc",
        script_identity="Greek",
        edition_identity="synthetic test edition",
        passage_identity="John 13",
        fetch_receipt_sha256=sha(fetch_bytes),
        admission_decision_sha256=sha(decision_bytes),
        admission_attempt_id=ARCHIVE_ID,
        fetch_receipt_relative_path=prefix + "-fetch-receipt.json",
        admission_decision_relative_path=prefix + "-admission-decision.json",
        snapshot_relative_path=f"snapshots/source/{source_id}.json",
        content_identity="0" * 64,
        snapshot_identity="0" * 64,
    )
    payload = model.model_dump(mode="json")
    payload["content_identity"] = contracts._snapshot_content_sha256(model)
    payload["snapshot_identity"] = sha(rfc8785.dumps({k: v for k, v in payload.items() if k != "snapshot_identity"}))
    contracts.SourceSnapshot.model_validate_json(rfc8785.dumps(payload))
    for path, raw in [
        (prefix + "-fetch-receipt.json", fetch_bytes),
        (prefix + "-admission-decision.json", decision_bytes),
        (model.snapshot_relative_path, rfc8785.dumps(payload)),
    ]:
        _immutable(root / path, raw)
    for raw in files.values():
        destination = root / f"objects/sha256/{sha(raw)[:2]}/{sha(raw)}"
        if not destination.exists():
            _immutable(destination, raw)


def synthetic_archive(tmp_path):
    root = archive_root.__wrapped__(tmp_path)
    greek = {
        1: "εἰς τέλος",
        8: "Οὐ μὴ νίψῃς Ἐὰν μὴ νίψω σε, οὐκ ἔχεις μέρος μετʼ ἐμοῦ",
        10: "λελουμένος τοὺς πόδας νίψασθαι καθαρὸς ὅλος",
        14: "ὀφείλετε",
        15: "ὑπόδειγμα",
        17: "μακάριοί",
        19: "λέγω ὑμῖν πρὸ τοῦ γενέσθαι πιστεύσητε ὅταν γένηται ὅτι ἐγώ εἰμι.",
    }
    tokens = {
        1: [("εἰς", "εἰς", "--------"), ("τέλος", "τέλος", "----ASN-")],
        8: [("μέρος", "μέρος", "----ASN-")],
        10: [("λελουμένος", "λούω", "-XMPNSM-"), ("νίψασθαι", "νίπτω", "-AMN----")],
        15: [("ὑπόδειγμα", "ὑπόδειγμα", "----ASN-")],
        17: [("μακάριοι", "μακάριος", "----NPM-")],
        19: [("ἐγώ", "ἐγώ", "----NS--"), ("εἰμί", "εἰμί", "1PAI-S--")],
    }
    forms = "\n".join(f"0413{v:02d} N- {m} {f} {f} {f} {lemma}" for v, rows in tokens.items() for f, lemma, m in rows)
    lex = {
        "τέλος": "to or at the end (or here, to the uttermost)",
        "μέρος": "a part, share, portion",
        "λούω": "to bathe, wash the body",
        "νίπτω": "to wash, usually of a part of the body",
        "ὑπόδειγμα": "example for imitation",
        "μακάριος": "blessed, happy",
    }
    entries = "".join(f'<entry n="{lemma}|synthetic">{value}</entry>' for lemma, value in lex.items())
    authority = load_j13_upstream_authority()
    web = "\\c 13\n" + "\n".join(
        f"\\v {slot['verseNumber']} "
        + " ".join("\\w " + word + '|strong="synthetic"\\w*' for word in slot["text"].split(" "))
        for slot in authority["chapter"]["verseSlots"]
    )
    components = [
        {
            "data/sblgnt/text/John.txt": (
                "\n".join(f"John 13:{v}\t{t}" for v, t in greek.items()) + "\nJohn 8:24\tἐγώ εἰμι"
            ).encode()
        },
        {"64-Jn-morphgnt.txt": forms.encode()},
        {"usx/43-JHN.usx": b"unused comparison"},
        {"eng-web_usfm.zip": b"synthetic archive", "73-JHNeng-web.usfm": web.encode()},
        {"abbott-smith.tei.xml": ('<TEI xmlns="urn:synthetic">' + entries + "</TEI>").encode()},
    ]
    for index, files in enumerate(components, 1):
        _snapshot(root, index, files | {"README.md": b"synthetic rights evidence"})
    return root


def test_source_backed_independent_decisions(tmp_path, unicode_helper):
    root = synthetic_archive(tmp_path)
    before = inventory(root)
    decisions = verify_j13_annotation_batch(
        load_j13_upstream_authority(), load_j13_source_authority(root, synthetic=True), unicode_helper
    )
    assert [d.disposition for d in decisions] == [
        "NEEDS_EDITORIAL_REVISION",
        "VERIFIED_FOR_PACKAGE_CANDIDATE",
        "VERIFIED_FOR_PACKAGE_CANDIDATE",
        "NEEDS_EDITORIAL_REVISION",
        "SOURCE_OR_RIGHTS_GAP",
        "VERIFIED_FOR_PACKAGE_CANDIDATE",
        "REJECTED_NOT_TRANSLATION_NUANCE",
    ]
    assert "KJV" in decisions[4].missing_sources[0]
    assert decisions[-1].evidence == () and inventory(root) == before


@pytest.mark.parametrize(
    "mutation", ["token", "lemma", "morphology", "lexical", "locator", "source", "english", "empty_verse"]
)
def test_one_record_failure_preserves_independent_records(tmp_path, unicode_helper, mutation):
    root = synthetic_archive(tmp_path)
    sources = list(load_j13_source_authority(root, synthetic=True))
    from dataclasses import replace

    index, old, new = {
        "token": (1, "μέρος μέρος μέρος", "other other other"),
        "lemma": (1, "μέρος μέρος μέρος μέρος", "μέρος μέρος μέρος other"),
        "morphology": (1, "N- ----ASN- μέρος", "N- ----DSN- μέρος"),
        "lexical": (4, "a part, share, portion", "unrelated sense"),
        "locator": (4, "μέρος|synthetic", "other|synthetic"),
        "source": (4, "", ""),
        "english": (3, 'part|strong="synthetic"', 'wrong|strong="synthetic"'),
        "empty_verse": (1, "041308", "041399"),
    }[mutation]
    source = sources[index]
    if mutation == "source":
        sources[index] = replace(source, snapshot=None, files=(), gap="missing")
    else:
        sources[index] = replace(
            source, files=tuple((p, b.replace(old.encode(), new.encode())) for p, b in source.files)
        )
    result = verify_j13_annotation_batch(load_j13_upstream_authority(), tuple(sources), unicode_helper)
    assert result[1].disposition != "VERIFIED_FOR_PACKAGE_CANDIDATE"
    assert result[5].disposition == "VERIFIED_FOR_PACKAGE_CANDIDATE"


@pytest.mark.parametrize("contents", [None, b"wrong"])
def test_hash_drift_and_database_guards(tmp_path, monkeypatch, contents):
    root = synthetic_archive(tmp_path)
    source = load_j13_source_authority(root, synthetic=True)[0]
    obj = source.snapshot.objects[0]
    path = root / f"objects/sha256/{obj.sha256[:2]}/{obj.sha256}"
    path.chmod(0o644)
    if contents is not None:
        path.write_bytes(contents)
        path.chmod(0o444)
    with pytest.raises(ValueError, match="mutable|component drift"):
        load_j13_source_authority(root, synthetic=True)
    monkeypatch.setenv("BSL_DATABASE_URL", "must-not-connect")
    with pytest.raises(ValueError, match="database"):
        load_j13_source_authority(root, synthetic=True)


def test_candidate_receipt_and_adversarial_rejection(tmp_path, unicode_helper):
    from bsl.application.j13_package_compilation import PACKAGE_NAME, RECEIPT_NAME, build_outputs, validate_package
    from bsl.contracts.translation_annotation_compilation import TranslationAnnotationCompilationReceipt
    from bsl.infrastructure.j13_authority import decode

    authority = load_j13_upstream_authority()
    sources = load_j13_source_authority(synthetic_archive(tmp_path), synthetic=True)
    decisions = verify_j13_annotation_batch(authority, sources, unicode_helper)
    from bsl.application.j13_package_compilation import compile_j13_package_candidate

    package = decode(compile_j13_package_candidate(authority, decisions, unicode_helper))
    digest = sha(rfc8785.dumps(package))
    proof = {
        "double_build_package_hashes": [digest, digest],
        "double_build_models_and_decisions_equal": True,
        "double_build_receipt_bytes_equal": True,
        "archive_unchanged": True,
    }
    outputs = build_outputs(authority, sources, decisions, unicode_helper, proof)
    assert outputs == build_outputs(authority, sources, decisions, unicode_helper, proof)
    receipt = TranslationAnnotationCompilationReceipt.model_validate_json(outputs[RECEIPT_NAME])
    assert receipt.package_sha256 == sha(outputs[PACKAGE_NAME]) and receipt.package_bytes == len(outputs[PACKAGE_NAME])
    assert outputs[PACKAGE_NAME] == rfc8785.dumps(decode(outputs[PACKAGE_NAME]))
    for name in (PACKAGE_NAME, RECEIPT_NAME):
        assert outputs[name.removesuffix(".json") + ".sha256"] == f"{sha(outputs[name])}  {name}\n".encode()
    from bsl.application.j13_package_compilation import prose_failures, prose_fields

    for path, _ in prose_fields(package):
        altered = _changed(package, path.replace(".", "/"), "# Forbidden markup")
        assert any(p == path for p, _, _ in prose_failures(altered, unicode_helper))
    altered = _changed(package, "annotations/0/full_note_paragraphs", ["😀" * 2401])
    assert any("full_note_paragraphs" in p for p, _, _ in prose_failures(altered, unicode_helper))
    cases = [
        ("target/scripture_package_content_sha256", "0" * 64),
        ("annotations/0/editorial_state", "approved"),
        ("annotations/0/lifecycle_state", "withdrawn"),
        ("annotations/0/supersedes_revision", 8),
        ("annotations/0/eligibility/training/decision", "allowed"),
        ("annotations/0/eligibility/reader_delivery/decision", "allowed"),
        ("annotations/0/annotation_issue_id", "tan:john.13.30:night-symbolism"),
        ("annotations/0/annotation_issue_id", "tan:john.13.2:during-supper"),
        ("annotations/0/short_note", "/Users/private"),
        ("annotations/0/short_note", "ghp_fake"),
        ("annotations/0/short_note", "Unsupported claim"),
        ("annotations/0/short_note", "😀" * 321),
        ("annotations/0/full_note_paragraphs", []),
        ("annotations/0/full_note_paragraphs", ["Plain text"] * 9),
        ("annotations/0/interpretive_limits", ["Plain text"] * 9),
        ("annotations/0/claim_reference_ids", []),
        ("annotations/0/source_reference_ids", ["dangling"]),
        ("claim_summaries", []),
        ("source_citations", []),
        ("annotations/0/anchors/0/utf16_start", 1),
        ("annotations/0/anchors/0/utf16_length", 0),
        ("annotations/0/anchors/0/expected_phrase", "wrong"),
        ("annotations/0/anchors/0/verse_text_sha256", "0" * 64),
        ("annotations/0/anchors/0/anchor_order", 2),
        ("annotations/0/anchors/0/chapter", 14),
    ]
    for path, value in cases:
        altered = _changed(package, path, value)
        with pytest.raises((ValueError, SchemaError)):
            validate_package(altered, authority, unicode_helper, decisions)
        if "/anchors/" in path:
            from bsl.application.j13_package_compilation import validate_anchors

            with pytest.raises(ValueError):
                validate_anchors(altered["annotations"][0]["anchors"], authority, unicode_helper)
    for key in ("annotations", "claim_summaries", "source_citations"):
        altered = deepcopy(package)
        altered[key].append(altered[key][0])
        with pytest.raises(ValueError):
            validate_package(altered, authority, unicode_helper, decisions)
    for path, value in (
        ("decisions/0/suggested_replacement", None),
        ("decisions/4/missing_sources", []),
        ("decisions/1/missing_sources", ["missing"]),
        ("decisions/1/claims", []),
        ("decisions/6/reason", "wrong"),
        ("decisions/1/evidence/0/value", "wrong"),
        ("accepted_roster", []),
        ("decisions", []),
        ("package_sha256", "0" * 64),
        ("receipt_identity", "0" * 64),
    ):
        altered = _changed(decode(outputs[RECEIPT_NAME]), path, value)
        with pytest.raises(ValueError):
            TranslationAnnotationCompilationReceipt.model_validate_json(json.dumps(altered))


@pytest.fixture
def controller(monkeypatch):
    import importlib

    monkeypatch.syspath_prepend(str(ROOT))
    return importlib.import_module("tools.j13_lab_01_compile_candidate")


def _invoke(controller, root, output, helper, expected=None):
    args = ["--archive-root", str(root), "--output-dir", str(output)]
    if expected is not None:
        args += ["--check-against", str(expected)]
    return controller.main(args, _synthetic=True, _helper=helper)


def test_controller_five_output_equality_and_drift(controller, tmp_path, unicode_helper):
    root = synthetic_archive(tmp_path)
    before = inventory(root)
    first, second = tmp_path / "first", tmp_path / "second"
    evidence = _invoke(controller, root, first, unicode_helper)
    repeated = _invoke(controller, root, second, unicode_helper, first)
    assert evidence == repeated and evidence["archive_inventory"] == before == inventory(root)
    assert len(evidence["artifacts"]) == 5
    assert evidence["helper_source_sha256"] == sha((ROOT / "tools/j13_unicode_profile.swift").read_bytes())
    assert evidence["swift_version"] and evidence["os_identity"]
    for name, digest in evidence["artifacts"].items():
        assert (first / name).read_bytes() == (second / name).read_bytes()
        assert sha((first / name).read_bytes()) == digest
    next(first.iterdir()).write_bytes(b"drift")
    failed = tmp_path / "failed"
    with pytest.raises(ValueError, match="artifact drift"):
        _invoke(controller, root, failed, unicode_helper, first)
    assert not failed.exists()


@pytest.mark.parametrize("phase", ["candidate", "receipt", "before_publication"])
def test_controller_refuses_archive_change(controller, tmp_path, unicode_helper, monkeypatch, phase):
    root = synthetic_archive(tmp_path)
    function = (
        "build_outputs"
        if phase == "receipt"
        else "_compile"
        if phase == "before_publication"
        else "compile_j13_package_candidate"
    )
    original = getattr(controller, function)
    calls = 0

    def change_after_build(*args, **kwargs):
        nonlocal calls
        result = original(*args, **kwargs)
        calls += 1
        if calls == 1:
            (root / "unexpected-inventory-entry").write_bytes(b"synthetic external change")
        return result

    monkeypatch.setattr(controller, function, change_after_build)
    output = tmp_path / "out"
    with pytest.raises(ValueError, match="archive inventory changed"):
        _invoke(controller, root, output, unicode_helper)
    assert not output.exists() and (root / "unexpected-inventory-entry").exists()


@pytest.mark.parametrize("phase", ["candidate", "receipt"])
def test_controller_independently_detects_mismatch(controller, tmp_path, unicode_helper, monkeypatch, phase):
    root = synthetic_archive(tmp_path)
    function = "compile_j13_package_candidate" if phase == "candidate" else "build_outputs"
    original = getattr(controller, function)
    calls = 0

    def corrupt_second_result(*args, **kwargs):
        nonlocal calls
        result = original(*args, **kwargs)
        calls += 1
        if calls == 2:
            return result + b" " if isinstance(result, bytes) else result | {next(iter(result)): b"changed"}
        return result

    monkeypatch.setattr(controller, function, corrupt_second_result)
    output = tmp_path / "out"
    with pytest.raises(ValueError, match="independent .* differ"):
        _invoke(controller, root, output, unicode_helper)
    assert calls == 2 and not output.exists()


@pytest.mark.parametrize("kind", ["contained", "parent_symlink", "artifact_symlink", "existing_artifact"])
def test_controller_output_containment_and_symlinks(controller, tmp_path, unicode_helper, kind):
    from bsl.application.j13_package_compilation import PACKAGE_NAME

    root = synthetic_archive(tmp_path)
    before = inventory(root)
    output = tmp_path / "out"
    sentinel = tmp_path / "sentinel"
    sentinel.write_bytes(b"preserve")
    if kind == "contained":
        output = root / "out"
    elif kind == "parent_symlink":
        output.symlink_to(root, target_is_directory=True)
        output = output / "out"
    else:
        output.mkdir()
        if kind == "artifact_symlink":
            (output / PACKAGE_NAME).symlink_to(sentinel)
        else:
            (output / PACKAGE_NAME).write_bytes(b"existing")
    with pytest.raises((ValueError, FileExistsError), match="outside|exists"):
        _invoke(controller, root, output, unicode_helper)
    assert sentinel.read_bytes() == b"preserve" and inventory(root) == before


@pytest.mark.parametrize("existing_directory", [False, True])
def test_controller_failure_cleans_only_owned_outputs(
    controller, tmp_path, unicode_helper, monkeypatch, existing_directory
):
    root = synthetic_archive(tmp_path)
    before = inventory(root)
    output = tmp_path / "out"
    if existing_directory:
        output.mkdir()
        (output / "unrelated").write_bytes(b"preserve")
    original = controller.os.open
    calls = 0

    def fail_second_open(path, flags, *args, **kwargs):
        nonlocal calls
        if flags & controller.os.O_EXCL:
            calls += 1
            if calls == 2:
                raise OSError("synthetic publication failure")
        return original(path, flags, *args, **kwargs)

    monkeypatch.setattr(controller.os, "open", fail_second_open)
    with pytest.raises(OSError, match="publication failure"):
        _invoke(controller, root, output, unicode_helper)
    assert calls == 2 and inventory(root) == before
    assert not list(tmp_path.glob(".j13-output-*"))
    if existing_directory:
        assert [p.name for p in output.iterdir()] == ["unrelated"]
        assert (output / "unrelated").read_bytes() == b"preserve"
    else:
        assert not output.exists()


def test_controller_owned_helper_cleanup_on_failure(controller, tmp_path, monkeypatch, unicode_helper):
    closed = []
    monkeypatch.setattr(controller, "UnicodeHelper", lambda: unicode_helper)
    monkeypatch.setattr(unicode_helper, "close", lambda: closed.append(True))
    with pytest.raises(ValueError, match="canonical archive"):
        controller.main(["--archive-root", str(tmp_path), "--output-dir", str(tmp_path.parent / "unused")])
    assert closed == [True]
    import runpy
    import sys

    monkeypatch.setattr(sys, "argv", ["j13_lab_01_compile_candidate.py"])
    with pytest.raises(SystemExit) as error:
        runpy.run_path(str(ROOT / "tools/j13_lab_01_compile_candidate.py"), run_name="__main__")
    assert error.value.code == 2


def test_required_source_permission_is_a_record_gap(tmp_path, unicode_helper):
    from dataclasses import replace

    sources = list(load_j13_source_authority(synthetic_archive(tmp_path), synthetic=True))
    snapshot = sources[4].snapshot
    sources[4] = replace(
        sources[4],
        snapshot=snapshot.model_copy(
            update={
                "allowed_operations": tuple(op for op in snapshot.allowed_operations if op != "EXACT_RUNTIME_LOOKUP")
            }
        ),
    )
    decisions = verify_j13_annotation_batch(load_j13_upstream_authority(), tuple(sources), unicode_helper)
    assert decisions[1].disposition == "SOURCE_OR_RIGHTS_GAP"
    assert decisions[1].missing_sources == (sources[4].source_id,)
    assert decisions[5].disposition == "VERIFIED_FOR_PACKAGE_CANDIDATE"


def test_upstream_changed_bytes_retain_expected_blob(tmp_path, monkeypatch):
    import shutil

    import bsl.infrastructure.j13_authority as module

    shutil.copytree(ROOT / "fixtures/J13-LAB-01", tmp_path / "fixtures/J13-LAB-01")
    manifest = json.loads((tmp_path / "fixtures/J13-LAB-01/upstream-authority.json").read_bytes())
    entry = manifest["files"][0]
    path = tmp_path / entry["fixture_path"]
    path.write_bytes(path.read_bytes() + b"\n")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="original-byte drift"):
        load_j13_upstream_authority()
    assert (
        json.loads((tmp_path / "fixtures/J13-LAB-01/upstream-authority.json").read_bytes())["files"][0]["git_blob"]
        == entry["git_blob"]
    )


def test_missing_and_symlink_authority(tmp_path):
    missing = load_j13_source_authority(tmp_path / "absent", synthetic=True)
    assert all(source.gap == "owner archive unavailable" for source in missing)
    root = synthetic_archive(tmp_path)
    alias = tmp_path / "alias"
    alias.symlink_to(root, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        load_j13_source_authority(alias, synthetic=True)
    from bsl.infrastructure.j13_authority import read_regular

    with pytest.raises(ValueError, match="unsafe authority"):
        read_regular(tmp_path, "alias/.bsl-archive-root.json")
    (root / "snapshots/source/SP01-SRC-001.json").unlink()
    assert load_j13_source_authority(root, synthetic=True)[0].gap == "required admitted authority file unavailable"


def test_controller_archive_change_during_publication(controller, tmp_path, unicode_helper, monkeypatch):
    root = synthetic_archive(tmp_path)
    output = tmp_path / "out"
    original = controller.os.open

    def change_on_file(path, flags, *args, **kwargs):
        if flags & controller.os.O_EXCL:
            (root / "external-change").write_bytes(b"change")
        return original(path, flags, *args, **kwargs)

    monkeypatch.setattr(controller.os, "open", change_on_file)
    with pytest.raises(ValueError, match="during publication"):
        _invoke(controller, root, output, unicode_helper)
    assert not output.exists() and (root / "external-change").exists()


def test_controller_parent_swap_before_publication(controller, tmp_path, unicode_helper, monkeypatch):
    root = synthetic_archive(tmp_path)
    before = inventory(root)
    parent = tmp_path / "destination"
    parent.mkdir()
    original = controller._compile

    def replace_parent(*args, **kwargs):
        result = original(*args, **kwargs)
        parent.rmdir()
        parent.symlink_to(root, target_is_directory=True)
        return result

    monkeypatch.setattr(controller, "_compile", replace_parent)
    with pytest.raises(OSError):
        _invoke(controller, root, parent / "out", unicode_helper)
    assert inventory(root) == before and not (root / "out").exists()


@pytest.mark.parametrize("replacement", ["file", "directory", "removed", "unrelated"])
def test_controller_preserves_concurrent_replacements(controller, tmp_path, unicode_helper, monkeypatch, replacement):
    root = synthetic_archive(tmp_path)
    output, moved = tmp_path / "out", tmp_path / "moved"
    original = controller.os.open
    first_name = None

    def replace_then_fail(path, flags, *args, **kwargs):
        nonlocal first_name
        if flags & controller.os.O_EXCL:
            if first_name is None:
                first_name = path
            else:
                if replacement in ("file", "removed"):
                    # Keep the owned inode alive so the filesystem cannot reuse it.
                    (output / first_name).rename(tmp_path / "moved-file")
                    if replacement == "file":
                        (output / first_name).write_bytes(b"external replacement")
                elif replacement == "directory":
                    output.rename(moved)
                    output.mkdir()
                else:
                    (output / "unrelated").write_bytes(b"external addition")
                raise OSError("synthetic concurrent failure")
        return original(path, flags, *args, **kwargs)

    monkeypatch.setattr(controller.os, "open", replace_then_fail)
    with pytest.raises(OSError, match="concurrent failure"):
        _invoke(controller, root, output, unicode_helper)
    if replacement == "file":
        assert (output / first_name).read_bytes() == b"external replacement"
    elif replacement == "directory":
        assert output.is_dir() and list(output.iterdir()) == [] and list(moved.iterdir()) == []
    elif replacement == "unrelated":
        assert (output / "unrelated").read_bytes() == b"external addition"
    else:
        assert not output.exists()


def test_controller_output_directory_replacement_refuses_success(controller, tmp_path, unicode_helper, monkeypatch):
    root = synthetic_archive(tmp_path)
    output, moved = tmp_path / "out", tmp_path / "moved"
    original = controller._write_outputs

    def replace_after_write(*args):
        original(*args)
        output.rename(moved)
        output.mkdir()

    monkeypatch.setattr(controller, "_write_outputs", replace_after_write)
    with pytest.raises(ValueError, match="directory identity changed"):
        _invoke(controller, root, output, unicode_helper)
    assert output.is_dir() and list(output.iterdir()) == [] and list(moved.iterdir()) == []


@pytest.mark.parametrize("replacement", [False, True])
def test_controller_verifies_published_bytes(controller, tmp_path, unicode_helper, monkeypatch, replacement):
    root = synthetic_archive(tmp_path)
    output = tmp_path / "out"
    original = controller._write_outputs
    changed = None

    def alter_after_write(*args):
        nonlocal changed
        original(*args)
        changed = next(output.iterdir())
        if replacement:
            changed.rename(tmp_path / "moved-artifact")
        changed.write_bytes(b"external changed bytes")

    monkeypatch.setattr(controller, "_write_outputs", alter_after_write)
    with pytest.raises(ValueError, match="published artifact identity or bytes"):
        _invoke(controller, root, output, unicode_helper)
    if replacement:
        assert changed.read_bytes() == b"external changed bytes" and len(list(output.iterdir())) == 1
    else:
        assert not output.exists()


@pytest.mark.parametrize("matches", [False, True])
def test_owner_volume_preflight_queries_mount_point(tmp_path, monkeypatch, matches):
    import plistlib
    import subprocess
    from pathlib import Path

    import bsl.infrastructure.j13_authority as module

    synthetic = synthetic_archive(tmp_path)
    marker = json.loads(
        (synthetic / ".bsl-archive-root.json")
        .read_text()
        .replace(str(ARCHIVE_ID), "01a02576-0e1b-78f0-b059-46cd5407f8d6")
    )
    original = module.read_regular
    calls = []

    def read_synthetic(root, relative, immutable=False):
        if relative == ".bsl-archive-root.json":
            return json.dumps(marker).encode()
        return original(synthetic, relative, immutable)

    def volume(args, **kwargs):
        calls.append(args)
        assert args == ["diskutil", "info", "-plist", "/Volumes/BSL-Archive"]
        identity = marker["stable_volume_identifier"] if matches else "wrong-volume"
        return subprocess.CompletedProcess(args, 0, plistlib.dumps({"VolumeUUID": identity}))

    monkeypatch.setattr(module, "read_regular", read_synthetic)
    monkeypatch.setattr(module.subprocess, "run", volume)
    if matches:
        assert load_j13_source_authority(Path("/Volumes/BSL-Archive/BiblicalScholarLab"))[0].snapshot is not None
    else:
        with pytest.raises(ValueError, match="physical identity differs"):
            load_j13_source_authority(Path("/Volumes/BSL-Archive/BiblicalScholarLab"))
    assert len(calls) == 1


def test_web_display_extracts_words_without_attribute_or_marker_evidence():
    from bsl.application.j13_annotation_verification import _web_display

    raw = r'\v 19 \wj \+w I|strong="G1473"\+w* \+w am|strong="G1510"\+w* \+w he|strong="G3754"\+w*. \wj*'
    assert _web_display(raw) == "I am he. "
    assert _web_display(r"\v 8 \wj Jesus\wj* answered") == "Jesus answered"
    assert _web_display(r"\v 8 \wj Jesus\wj*  answered") == "Jesus  answered"
    assert _web_display(r'\v 8 \p \w other|gloss="you have no part with me"\w*') == "other"
    assert _web_display("\\v 8 a\u0301  b") == "a\u0301  b"
    for malformed in (r'\v 8 \w word|x="value"\+w*', r"\v 8 \f + footnote\f*", r"\v 8 \unknown text"):
        with pytest.raises(ValueError, match="USFM marker"):
            _web_display(malformed)
