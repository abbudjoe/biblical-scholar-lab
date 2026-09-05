"""Synthetic release evidence only; no owner archive, consumer importer or network."""

import importlib
import os
import subprocess
from copy import deepcopy
from dataclasses import replace

import pytest
from jsonschema.exceptions import ValidationError as SchemaError
from pydantic import ValidationError
from test_j13_annotation_verification import _snapshot
from test_j13_package_compilation import unicode_helper as unicode_helper
from test_source_acquisition import archive_root
from test_source_acquisition import no_network as no_network

import bsl.application.j13_private_pilot_release as release
import bsl.infrastructure.j13_authority as authority
from bsl.contracts.translation_annotation_compilation import TranslationAnnotationCompilationReceipt as V1
from bsl.contracts.translation_annotation_compilation_release import (
    CANDIDATE_SHA,
    COMMENT_SHA,
    NOTICES,
    OWNER_SHA,
    PACKAGE,
    RECEIPT,
    RECEIPT_SHA,
    RELEASE_FILES,
    ROSTER,
)
from bsl.contracts.translation_annotation_compilation_release import (
    TranslationAnnotationCompilationReceiptV2 as V2,
)

BASE = "ff362da6300a16b4c36aacc5039ff5fe90a39bae"
SYNTHETIC_PRODUCER = "a" * 40


@pytest.fixture
def controller(monkeypatch):
    monkeypatch.syspath_prepend(str(authority.ROOT))
    return importlib.import_module("tools.j13_lab_02_finalize_private_pilot")


def originals():
    root = authority.ROOT
    candidate = authority.decode(
        (root / "artifacts/J13-LAB-01/translation-annotation-package.j13-pilot-01.candidate.json").read_bytes()
    )
    receipt = V1.model_validate_json(
        (
            root / "artifacts/J13-LAB-01/translation-annotation-compilation-receipt.j13-pilot-01.candidate.json"
        ).read_bytes()
    )
    owner = authority.decode((root / "artifacts/J13-LAB-02/owner-decision.json").read_bytes())
    return release.Inputs(candidate, receipt, owner, authority.load_j13_upstream_authority())


@pytest.fixture
def synthetic(tmp_path, monkeypatch, controller):
    root = archive_root.__wrapped__(tmp_path)
    permissions = {}
    for index in (1, 2, 4, 5):
        source = f"SP01-SRC-00{index}"
        files = {
            name: f"SYNTHETIC permission evidence for {source}: {name}".encode()
            for name, _ in release.PERMISSIONS[source]
        }
        if index == 4:
            files = {"eng-web_usfm.zip": b"SYNTHETIC package, not actual source data"} | files
        files.setdefault("README.md", b"SYNTHETIC admitted permission marker")
        _snapshot(root, index, files)
        permissions[source] = tuple((n, authority.sha(files[n])) for n, _ in release.PERMISSIONS[source])
    sources = authority.load_j13_source_authority(root, synthetic=True)
    inputs = originals()
    inputs = replace(
        inputs,
        receipt=inputs.receipt.model_copy(
            update={"source_snapshots": tuple(s.snapshot for s in sources if s.snapshot)}
        ),
    )
    monkeypatch.setattr(release, "PERMISSIONS", permissions)
    monkeypatch.setattr(release, "load_inputs", lambda: inputs)
    monkeypatch.setattr(
        release, "load_j13_source_authority", lambda p: authority.load_j13_source_authority(p, synthetic=True)
    )
    monkeypatch.setattr(controller, "producer_files", lambda p: tuple((f, "b" * 64) for f in RELEASE_FILES))
    monkeypatch.setattr(release, "producer_files", lambda p: tuple((f, "b" * 64) for f in RELEASE_FILES))
    monkeypatch.setattr(controller, "check_frozen_release", lambda outputs: None)
    return root, inputs


@pytest.fixture
def outputs(synthetic, unicode_helper):
    root, _ = synthetic
    return release.build_outputs(
        root, SYNTHETIC_PRODUCER, tuple((f, "b" * 64) for f in RELEASE_FILES), authority.inventory(root), unicode_helper
    )


def rehash(data):
    data["receipt_identity"] = authority.sha(
        release.canonical({k: v for k, v in data.items() if k != "receipt_identity"})
    )
    return release.canonical(data)


def test_frozen_bytes_and_v1_authority():
    inputs = originals()
    assert authority.sha(release.canonical(inputs.candidate)) == CANDIDATE_SHA
    assert authority.sha(release.canonical(inputs.receipt.model_dump(mode="json"))) == RECEIPT_SHA
    assert authority.sha(release.canonical(inputs.owner)) == OWNER_SHA
    paths = [f["fixture_path"] for f in inputs.authority["manifest"]["files"]]
    paths += [p for p, _ in inputs.receipt.compiler_files]
    paths += ["contracts/json-schema/translation-annotation/translation-annotation-compilation-receipt-v1.schema.json"]
    for path in paths:
        assert (
            subprocess.run(["git", "show", f"{BASE}:{path}"], capture_output=True, check=True).stdout
            == (authority.ROOT / path).read_bytes()
        )
    bad = inputs.receipt.model_dump(mode="json") | {"non_activatable": False}
    with pytest.raises(ValidationError):
        V1.model_validate_json(rehash(bad))


def test_synthetic_complete_derivation(synthetic, outputs, unicode_helper):
    root, inputs = synthetic
    first = authority.inventory(root)
    findings, notice = release.rights(root, inputs)
    package = authority.decode(outputs[PACKAGE])
    receipt = V2.model_validate_json(outputs[RECEIPT])
    assert len(outputs) == 7 and b"SYNTHETIC" in notice
    assert tuple(a["annotation_issue_id"] for a in package["annotations"]) == ROSTER
    assert package["package_revision"] == 2 and "supersedes_package_file_sha256" not in package
    delta = release.validate_release(package, inputs, findings, unicode_helper)
    assert release.protected(inputs.candidate, package, delta) == CANDIDATE_SHA
    assert {m.material_type for m in receipt.payload_inventory} == {
        "original prose",
        "quotation",
        "lexical paraphrase",
        "morphology-derived statement",
        "citation/notice",
    }
    prose = [m for m in receipt.payload_inventory if m.material_type == "original prose" and m.pointer != NOTICES]
    assert len(prose) == 29 and len({m.pointer for m in prose}) == 29
    assert all(m.basis_ids and m.result == "supported" for m in receipt.payload_inventory)
    assert len([m for m in receipt.payload_inventory if "/expected_phrase" in m.pointer]) == 4
    for old, new in zip(inputs.candidate["annotations"], package["annotations"], strict=True):
        assert new["scholarly_review_label"] == "model_assisted_editorial_review"
        assert new["annotation_revision"] == 2 and new["supersedes_revision"] == 1
        assert old["eligibility"]["training"] == new["eligibility"]["training"]
        for operation in ("retrieval", "evaluation", "public_sharing"):
            assert {k: v for k, v in old["eligibility"][operation].items() if k != "limitations"} == {
                k: v for k, v in new["eligibility"][operation].items() if k != "limitations"
            }
    release.validate_context(
        outputs, root, SYNTHETIC_PRODUCER, tuple((f, "b" * 64) for f in RELEASE_FILES), first, unicode_helper
    )
    assert authority.inventory(root) == first
    assert b"http://creativecommons.org/licenses/by-sa/3.0/" in notice
    assert b"https://creativecommons.org/licenses/by/4.0/" in notice
    assert not release.prose_failures(package, unicode_helper)


@pytest.mark.parametrize(
    "pointer,value",
    [
        ("/annotations/0/short_note", "changed prose"),
        ("/annotations/1/full_note_paragraphs/1", "changed paragraph"),
        ("/annotations/2/interpretive_limits/0", "changed limit"),
        ("/claim_summaries/1/claim_summary", "changed claim"),
        ("/claim_summaries/0/source_reference_ids/0", "unknown"),
        ("/annotations/0/source_reference_ids/0", "unknown"),
        ("/annotations/0/claim_reference_ids/0", "unknown"),
        ("/annotations/0/annotation_issue_id", ROSTER[1]),
        ("/annotations/0/scholarly_review_label", "specialist_reviewed"),
        ("/annotations/0/eligibility/training/decision", "allowed"),
        ("/annotations/0/eligibility/public_sharing/decision", "allowed"),
        ("/annotations/0/eligibility/evaluation/authority_id", "fabricated"),
        ("/annotations/0/eligibility/reader_delivery/basis_record_ids/0", "free-form-approval"),
        ("/source_citations/0/source_version_id", "unknown"),
        ("/source_citations/0/exact_locator", "John 13:9"),
        ("/source_citations/0/citation_display", "replacement"),
        ("/target/translation_id", "replacement"),
        ("/annotations/0/anchors/0/utf16_start", -1),
        ("/annotations/0/anchors/0/expected_phrase", "different"),
        ("/annotations/0/anchors/0/anchor_id", "unknown"),
        ("/annotations/0/annotation_revision", 3),
        ("/annotations/0/supersedes_revision", 2),
        ("/source_citations/0/attribution", "https://example.invalid"),
    ],
)
def test_protected_mutations_reject_even_rehashed(synthetic, outputs, unicode_helper, pointer, value):
    root, inputs = synthetic
    package = authority.decode(outputs[PACKAGE])
    parent, key = pointer.rsplit("/", 1)
    target = release.at(package, parent)
    target[int(key) if isinstance(target, list) else key] = value
    findings, _ = release.rights(root, inputs)
    with pytest.raises((ValueError, SchemaError)):
        release.validate_release(package, inputs, findings, unicode_helper)
    changed = outputs | {PACKAGE: release.canonical(package)}
    receipt = authority.decode(outputs[RECEIPT])
    receipt["package_file"] = release.file_record(PACKAGE, changed[PACKAGE])
    changed[RECEIPT] = rehash(receipt)
    with pytest.raises(ValueError, match="contextual"):
        release.validate_context(
            changed,
            root,
            SYNTHETIC_PRODUCER,
            tuple((f, "b" * 64) for f in RELEASE_FILES),
            authority.inventory(root),
            unicode_helper,
        )


@pytest.mark.parametrize("source", ("SP01-SRC-001", "SP01-SRC-002", "SP01-SRC-004", "SP01-SRC-005"))
@pytest.mark.parametrize(
    "gap", ("missing", "metadata-only", "PUBLIC_DEMO-only", "permission-hash", "reciprocal-unresolved")
)
def test_rights_gaps_reject_whole_roster(synthetic, monkeypatch, source, gap):
    root, inputs = synthetic
    sources = list(authority.load_j13_source_authority(root, synthetic=True))
    i = next(i for i, s in enumerate(sources) if s.source_id == source)
    if gap == "missing":
        sources[i] = replace(sources[i], snapshot=None, gap="missing")
    elif gap == "reciprocal-unresolved":
        files = tuple((n, b"SYNTHETIC unresolved reciprocal condition") for n, _ in sources[i].files)
        sources[i] = replace(sources[i], files=files)
    elif gap in ("metadata-only", "PUBLIC_DEMO-only"):
        sources[i] = replace(sources[i], files=())
    else:
        sources[i] = replace(sources[i], files=tuple((n, b + b"changed") for n, b in sources[i].files))
    monkeypatch.setattr(release, "load_j13_source_authority", lambda p: tuple(sources))
    with pytest.raises(ValueError, match="reader rights"):
        release.rights(root, inputs)


@pytest.mark.parametrize(
    "case", ("missing-source", "unsupported", "substring", "delta-old", "delta-new", "closed", "duplicate", "surrogate")
)
def test_integrity_failures(synthetic, outputs, monkeypatch, unicode_helper, case):
    root, inputs = synthetic
    findings, notice = release.rights(root, inputs)
    package, delta = release.derive(inputs, findings)
    with pytest.raises((ValueError, SchemaError)):
        if case == "missing-source":
            monkeypatch.setattr(release, "load_j13_source_authority", lambda p: ())
            release.rights(root, inputs)
        elif case == "unsupported":
            findings[0]["result"] = "unresolved"
            release.derive(inputs, findings)
        elif case == "substring":
            package["annotations"][0]["short_note"] = "missing quotation"
            release.payload_inventory(package, notice)
        elif case.startswith("delta-"):
            delta[0]["old_canonical_json" if case == "delta-old" else "new_canonical_json"] = "999"
            release.protected(inputs.candidate, package, delta)
        elif case == "closed":
            package["free_form_approved"] = True
            release.validate_release(package, inputs, findings, unicode_helper)
        else:
            changed = outputs | {PACKAGE: b'{"a":1,"\\u0061":2}' if case == "duplicate" else b'"\\ud800"'}
            release.validate_context(changed, root, SYNTHETIC_PRODUCER, (), authority.inventory(root), unicode_helper)


@pytest.mark.parametrize(
    "revision,declared,expected,valid",
    [
        (2, None, None, True),
        (1, None, None, True),
        (3, None, None, True),
        (2, "a" * 64, "a" * 64, True),
        (2, "a" * 64, None, False),
        (2, "a" * 64, "b" * 64, False),
        (2, None, "a" * 64, False),
        (1, "a" * 64, "a" * 64, False),
        (0, None, None, False),
        (-1, None, None, False),
        (True, None, None, False),
        (1.5, None, None, False),
        (2, "bad", "bad", False),
        (2, "A" * 64, "A" * 64, False),
    ],
)
def test_pinned_consumer_first_install_truth_table(revision, declared, expected, valid):
    package = {"package_revision": revision}
    if declared is not None:
        package["supersedes_package_file_sha256"] = declared
    if valid:
        release.validate_first_install(package, expected)
    else:
        with pytest.raises(ValueError):
            release.validate_first_install(package, expected)


@pytest.mark.parametrize(
    "field,value",
    [
        ("owner_decision_sha256", "0" * 64),
        ("approval_comment_sha256", "0" * 64),
        ("input_candidate", {"name": "wrong", "sha256": "0" * 64, "byte_count": 1}),
        ("input_receipt", {"name": "wrong", "sha256": "0" * 64, "byte_count": 1}),
        ("notes", []),
        ("package_revision", 1),
        ("biblos_admission_performed", True),
        ("package_file", {"name": "wrong", "sha256": "0" * 64, "byte_count": 1}),
        ("permitted_delta_sha256", "0" * 64),
        ("unexpected", True),
    ],
)
def test_receipt_closed_bindings(outputs, field, value):
    data = authority.decode(outputs[RECEIPT]) | {field: value}
    with pytest.raises(ValidationError):
        V2.model_validate_json(rehash(data))


def test_receipt_immutable_and_contextual_rehash(outputs, synthetic, unicode_helper):
    receipt = V2.model_validate_json(outputs[RECEIPT])
    with pytest.raises(ValidationError):
        receipt.notes[0].annotation_revision = 4
    with pytest.raises(TypeError):
        receipt.payload_inventory[0].basis_ids[0] = "fake"
    bad = authority.decode(outputs[RECEIPT])
    bad["receipt_identity"] = "0" * 64
    with pytest.raises(ValidationError):
        V2.model_validate_json(release.canonical(bad))
    bad["source_rights"][0]["grant"] = "owner says allowed"
    forged = rehash(bad)
    V2.model_validate_json(forged)  # Shape alone deliberately cannot establish rights.
    root, _ = synthetic
    with pytest.raises(ValueError, match="contextual"):
        release.validate_context(
            outputs | {RECEIPT: forged},
            root,
            SYNTHETIC_PRODUCER,
            tuple((f, "b" * 64) for f in RELEASE_FILES),
            authority.inventory(root),
            unicode_helper,
        )


@pytest.mark.parametrize(
    "artifact", (PACKAGE, RECEIPT, NOTICES, "SOURCE-NOTICES.j13-pilot-01.sha256", "J13-LAB-02-admission-handoff.md")
)
def test_missing_or_altered_companion_rejects(synthetic, outputs, unicode_helper, artifact):
    root, _ = synthetic
    bad = outputs | {artifact: outputs[artifact] + b" "}
    with pytest.raises((ValueError, ValidationError)):
        release.validate_context(
            bad,
            root,
            SYNTHETIC_PRODUCER,
            tuple((f, "b" * 64) for f in RELEASE_FILES),
            authority.inventory(root),
            unicode_helper,
        )


def test_private_two_builds_no_overwrite(synthetic, tmp_path, unicode_helper, controller):
    root, _ = synthetic
    first, second = tmp_path / "synthetic-build-1", tmp_path / "synthetic-build-2"
    e1 = controller.execute(root, SYNTHETIC_PRODUCER, first, None, unicode_helper)
    e2 = controller.execute(root, SYNTHETIC_PRODUCER, second, first, unicode_helper)
    assert e1["independent_seven_file_equality"] and e2["external_build_comparison"]
    assert {p.name: p.read_bytes() for p in first.iterdir()} == {p.name: p.read_bytes() for p in second.iterdir()}
    assert e1["archive_before"] == e2["archive_after"]
    assert all(v == 0 for v in e1["prohibited_operation_counts"].values())
    with pytest.raises(ValueError, match="preserve existing"):
        controller.execute(root, SYNTHETIC_PRODUCER, first, None, unicode_helper)


@pytest.mark.parametrize("case", ("extra", "permissions", "file-permissions", "bytes", "symlink"))
def test_private_output_integrity(synthetic, outputs, tmp_path, case, controller):
    path = tmp_path / "synthetic-output"
    path.mkdir(mode=0o700)
    for name, raw in outputs.items():
        (path / name).write_bytes(raw)
        (path / name).chmod(0o600)
    if case == "extra":
        (path / "other").write_bytes(b"preserve")
    elif case == "permissions":
        path.chmod(0o755)
    elif case == "file-permissions":
        (path / PACKAGE).chmod(0o644)
    elif case == "bytes":
        (path / PACKAGE).write_bytes(b"changed")
    else:
        (path / PACKAGE).unlink()
        (path / PACKAGE).symlink_to(path / RECEIPT)
    with pytest.raises(ValueError):
        controller.validate_private_set(path, outputs)


@pytest.mark.parametrize("case", ("outside", "archive", "root", "symlink", "valid"))
def test_real_output_containment(tmp_path, monkeypatch, case, controller):
    private = tmp_path / "private"
    private.mkdir()
    monkeypatch.setattr(controller, "PRIVATE_ROOT", private)
    monkeypatch.setattr(controller.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess([], 0, b""))
    archive = tmp_path / "archive"
    paths = {"outside": tmp_path / "elsewhere", "archive": archive / "out", "root": private, "valid": private / "new"}
    (private / "link").symlink_to(tmp_path)
    paths["symlink"] = private / "link" / "out"
    if case == "valid":
        assert controller.private_path(paths[case], archive) == paths[case]
    else:
        with pytest.raises(ValueError):
            controller.private_path(paths[case], archive)


@pytest.mark.parametrize("case", ("valid", "bad-sha", "wrong-commit", "source-drift"))
def test_producer_binding(monkeypatch, case, controller):
    def run(cmd, **kwargs):
        if cmd[1] == "rev-parse":
            raw = ("b" * 40 if case == "wrong-commit" else SYNTHETIC_PRODUCER).encode()
        else:
            raw = (authority.ROOT / cmd[2].split(":", 1)[1]).read_bytes()
            if case == "source-drift":
                raw += b"drift"
        return subprocess.CompletedProcess(cmd, 0, raw)

    monkeypatch.setattr(controller.subprocess, "run", run)
    if case == "valid":
        assert len(controller.producer_files(SYNTHETIC_PRODUCER)) == 9
    else:
        with pytest.raises(ValueError):
            controller.producer_files("main" if case == "bad-sha" else SYNTHETIC_PRODUCER)


@pytest.mark.parametrize("case", ("none", "match", "conflict"))
def test_finalized_revision_conflict(tmp_path, monkeypatch, case, controller):
    monkeypatch.setattr(controller, "ROOT", tmp_path)
    path = tmp_path / "artifacts/J13-LAB-02/release-manifest.json"
    path.parent.mkdir(parents=True)
    outputs = {"synthetic": b"SYNTHETIC"}
    if case != "none":
        path.write_bytes(
            release.canonical(
                {
                    "package_revision": 2,
                    "files": [
                        release.file_record("synthetic", b"different" if case == "conflict" else outputs["synthetic"])
                    ],
                }
            )
        )
    if case == "conflict":
        with pytest.raises(ValueError, match="already bound"):
            controller.check_frozen_release(outputs)
    else:
        controller.check_frozen_release(outputs)


@pytest.mark.parametrize("case", ("missing", "wrong-candidate", "decision", "revision", "rehash-flag", "size", "valid"))
def test_exact_owner_loader(tmp_path, monkeypatch, case):
    inputs = originals()
    raw = release.canonical(inputs.owner)
    if case in ("decision", "revision", "rehash-flag"):
        owner = deepcopy(inputs.owner)
        if case == "decision":
            owner["editorial_content"] = "approved_changed"
        elif case == "revision":
            owner["approved_annotations"][0]["annotation_revision"] = 3
        else:
            owner["free_form_allowed"] = True
        raw = release.canonical(owner)
    elif case == "wrong-candidate":
        raw = release.canonical(inputs.owner | {"candidate_package_sha256": "0" * 64})
    path = tmp_path / "owner.json"
    if case != "missing":
        path.write_bytes(raw)
    monkeypatch.setattr(release, "ROOT", tmp_path)
    if case == "valid":
        assert release.exact_file("owner.json", OWNER_SHA) == raw
    else:
        with pytest.raises((ValueError, FileNotFoundError)):
            release.exact_file("owner.json", OWNER_SHA, 1 if case == "size" else None)


def test_load_real_pinned_inputs_without_private_ci_dependencies(monkeypatch):
    exact = release.exact_file
    calls = []

    def read(path, digest, size=None):
        calls.append((path, digest))
        if path.startswith(".local/"):
            return b"SYNTHETIC private corroboration stand-in; not a release"
        return exact(path, digest, size)

    monkeypatch.setattr(release, "exact_file", read)
    loaded = release.load_inputs()
    assert loaded.receipt.non_activatable and len(loaded.owner["approved_annotations"]) == 3
    assert any(digest == COMMENT_SHA for _, digest in calls)
    assert len([p for p, _ in calls if "TranslationAnnotationPackage" in p]) == 2


@pytest.mark.parametrize("case", ("roster", "notes"))
def test_loader_context_mismatch(monkeypatch, case):
    exact = release.exact_file

    def read(path, digest, size=None):
        if path.startswith(".local/"):
            return b"SYNTHETIC private evidence"
        raw = exact(path, digest, size)
        if case == "roster" and path.endswith("candidate.json") and "package." in path:
            p = authority.decode(raw)
            p["annotations"].reverse()
            return release.canonical(p)
        if case == "notes" and path.endswith("tan-john-13-08-no-share-with-me.r2.json"):
            p = authority.decode(raw)
            p["annotation"]["annotation_issue_id"] = "wrong"
            return release.canonical(p)
        return raw

    monkeypatch.setattr(release, "exact_file", read)
    with pytest.raises(ValueError):
        release.load_inputs()


@pytest.mark.parametrize("case", ("success", "comparison", "db", "archive", "helper-failure", "execute-failure"))
def test_cli_lifecycle(tmp_path, monkeypatch, unicode_helper, case, controller):
    args = [
        "--archive-root",
        "/Volumes/BSL-Archive/BiblicalScholarLab",
        "--producer-commit",
        SYNTHETIC_PRODUCER,
        "--output-dir",
        str(tmp_path / "synthetic"),
    ]
    if case == "comparison":
        args += ["--check-against", str(tmp_path / "prior")]
    if case == "archive":
        args[1] = str(tmp_path)
    if case == "db":
        monkeypatch.setenv("BSL_DATABASE_URL", "SYNTHETIC-NO-CONNECTION")
    monkeypatch.setattr(controller, "private_path", lambda path, archive: path)
    closed = []

    class Helper:
        def close(self):
            closed.append(True)

    def helper():
        if case == "helper-failure":
            raise RuntimeError("synthetic helper failure")
        return Helper()

    def execute(*args):
        if case == "execute-failure":
            raise RuntimeError("synthetic execution failure")
        return {"SYNTHETIC": True}

    monkeypatch.setattr(controller, "UnicodeHelper", helper)
    monkeypatch.setattr(controller, "execute", execute)
    old = os.umask(0o077)
    os.umask(old)
    if case in ("success", "comparison"):
        assert controller.main(args) == {"SYNTHETIC": True}
    else:
        with pytest.raises((ValueError, RuntimeError)):
            controller.main(args)
    current = os.umask(old)
    assert current == old
    assert bool(closed) == (case in ("success", "comparison", "execute-failure"))


def test_owned_cleanup_and_archive_drift(synthetic, tmp_path, monkeypatch, unicode_helper, controller):

    root, _ = synthetic
    output = tmp_path / "synthetic-failed"

    def fail(fd, outputs, published):
        raise ValueError("synthetic publication failure")

    with monkeypatch.context() as m:
        m.setattr(controller, "_verify_outputs", fail)
        with pytest.raises(ValueError, match="publication failure"):
            controller.execute(root, SYNTHETIC_PRODUCER, output, None, unicode_helper)
        assert not output.exists()
    sequence = iter((authority.inventory(root), "changed"))
    monkeypatch.setattr(controller, "inventory", lambda p: next(sequence))
    with pytest.raises(ValueError, match="archive changed"):
        controller.execute(root, SYNTHETIC_PRODUCER, output, None, unicode_helper)
    assert not output.exists()


def test_no_original_batch_or_forbidden_operations(synthetic, tmp_path, monkeypatch, unicode_helper, controller):
    import bsl.application.j13_annotation_verification as scholarly

    def prohibited(*args, **kwargs):
        pytest.fail("prohibited original seven-record verification")

    monkeypatch.setattr(scholarly, "verify_j13_annotation_batch", prohibited)
    monkeypatch.setattr(
        __import__("tools.j13_lab_01_compile_candidate", fromlist=["x"]), "verify_j13_annotation_batch", prohibited
    )
    controller.execute(synthetic[0], SYNTHETIC_PRODUCER, tmp_path / "synthetic-no-batch", None, unicode_helper)


@pytest.mark.parametrize("case", ("producer", "inventory", "archive-drift"))
def test_context_rejects_forged_provenance(synthetic, outputs, monkeypatch, unicode_helper, case):
    root, _ = synthetic
    before = authority.inventory(root)
    fingerprints = tuple((f, "b" * 64) for f in RELEASE_FILES)
    if case == "producer":
        fingerprints = (("invented-file", "f" * 64),)
    elif case == "inventory":
        before = "0" * 64
    else:
        values = iter((before, "changed"))
        monkeypatch.setattr(release, "inventory", lambda p: next(values))
    with pytest.raises(ValueError, match="producer|inventory|archive changed"):
        release.validate_context(outputs, root, SYNTHETIC_PRODUCER, fingerprints, before, unicode_helper)


def test_notice_sections_have_exact_source_bases(outputs):
    receipt = V2.model_validate_json(outputs[RECEIPT])
    for source in release.PERMISSIONS:
        matching = [
            m
            for m in receipt.payload_inventory
            if m.pointer == NOTICES and m.basis_ids == ("J13-LAB-02-RIGHTS-" + source,)
        ]
        assert len(matching) == 3
        assert all(m.text.startswith(source + "\n") for m in matching)
        assert len({m.text for m in matching}) == 1
    joined = "".join(m.text for m in receipt.payload_inventory if m.pointer == NOTICES and m.annotation_id == ROSTER[0])
    assert joined.encode() == outputs[NOTICES]


def test_missing_companion_rejects(synthetic, outputs, unicode_helper):
    root, _ = synthetic
    bad = {k: v for k, v in outputs.items() if k != NOTICES}
    with pytest.raises(ValueError, match="contextual"):
        release.validate_context(
            bad,
            root,
            SYNTHETIC_PRODUCER,
            tuple((f, "b" * 64) for f in RELEASE_FILES),
            authority.inventory(root),
            unicode_helper,
        )


def test_concurrent_existing_directory_preserved(synthetic, outputs, tmp_path, monkeypatch, controller):
    root, _ = synthetic
    output = tmp_path / "synthetic-concurrent"
    original_mkdir = os.mkdir

    def concurrent(path, *args, **kwargs):
        if path == output.name:
            original_mkdir(path, *args, **kwargs)
            (output / "unrelated").write_bytes(b"preserve")
        return original_mkdir(path, *args, **kwargs)

    monkeypatch.setattr(controller.os, "mkdir", concurrent)
    with pytest.raises(FileExistsError):
        controller.publish_exclusive(output, outputs, root, authority.inventory(root))
    assert {p.name for p in output.iterdir()} == {"unrelated"}
    assert (output / "unrelated").read_bytes() == b"preserve"


@pytest.mark.parametrize("case", ("archive", "mode", "replacement"))
def test_publication_failure_cleans_only_owned(synthetic, outputs, tmp_path, monkeypatch, controller, case):
    root, _ = synthetic
    output = tmp_path / "synthetic-publication-failed"
    before = authority.inventory(root)
    original_verify = controller._verify_outputs

    def verify(fd, values, published):
        original_verify(fd, values, published)
        if case == "archive":
            monkeypatch.setattr(controller, "inventory", lambda p: "changed")
        elif case == "mode":
            output.chmod(0o755)
        else:
            (output / "unrelated").write_bytes(b"preserve concurrent addition")

    monkeypatch.setattr(controller, "_verify_outputs", verify)
    with pytest.raises(ValueError):
        controller.publish_exclusive(output, outputs, root, before)
    if case == "replacement":
        assert {p.name for p in output.iterdir()} == {"unrelated"}
    else:
        assert not output.exists()


def test_cli_module_entry_and_no_public_synthetic_flag(monkeypatch, controller):
    import runpy
    import sys

    monkeypatch.setattr(sys, "argv", ["synthetic-controller", "--synthetic"])
    with pytest.raises(SystemExit) as error:
        runpy.run_path(str(authority.ROOT / "tools/j13_lab_02_finalize_private_pilot.py"), run_name="__main__")
    assert error.value.code == 2
