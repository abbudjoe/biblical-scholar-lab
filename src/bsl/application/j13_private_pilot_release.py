"""Exact, offline derivation of the three-note private pilot; no scholarly rerun."""

import subprocess
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator
from rfc8785 import dumps as canonical

from bsl.application.j13_package_compilation import COMPILER_FILES, prose_failures, validate_anchors
from bsl.contracts.translation_annotation_compilation import TranslationAnnotationCompilationReceipt
from bsl.contracts.translation_annotation_compilation_release import (
    CANDIDATE_SHA,
    COMMENT_SHA,
    HANDOFF,
    NOTICES,
    OWNER_ID,
    OWNER_SHA,
    PACKAGE,
    RECEIPT,
    RECEIPT_SHA,
    RELEASE_FILES,
    ROSTER,
    TranslationAnnotationCompilationReceiptV2,
)
from bsl.infrastructure.j13_authority import (
    MANIFEST_SHA,
    ROOT,
    SourceAuthority,
    UnicodeHelper,
    decode,
    inventory,
    load_j13_source_authority,
    load_j13_upstream_authority,
    read_regular,
    sha,
)

PERMISSIONS = {
    "SP01-SRC-001": (
        ("README.md", "7ae1dc2622a8dafe55cf8b17d4935c3e39a70c46636277dd0fc46fe8b7464721"),
        ("LICENSE", "7e7170e3cebf88a9f60c7b8421418323c09304da1af4d5e90f4da1dc1c8a2661"),
    ),
    "SP01-SRC-002": (("README.md", "794f8b9123c9f1651f3e682137056d7758b4deeae4478559549381dfa04b4290"),),
    "SP01-SRC-004": (("copr.htm", "04ae9f9a0143624973342a2de498281ae66ac5adb7a46f753dde60e577d28fe8"),),
    "SP01-SRC-005": (("README.md", "b6cee23b631059347d8356c2fe1d4e82496f5cc1873e1e77266ce9966cd297b6"),),
}
GRANTS = {
    "SP01-SRC-001": "Retained CC BY 4.0 section 2(a)(1) permits reproduction and sharing, including excerpts.",
    "SP01-SRC-002": "README licenses parsing/lemmatization under CC BY-SA 3.0; delivered uses are grammatical facts.",
    "SP01-SRC-004": "Retained copr.htm declares WEB public domain and expressly permits quotation and distribution.",
    "SP01-SRC-005": "Retained README declares the lexicon TEI, including this marked-up version, public domain.",
}
RECIPROCAL = (
    "MorphGNT supplies factual verification only: noun/lemma identity, form-to-lemma correspondence, perfect "
    "participle, and absence of a separate pronoun. No token rows, parsing-code sequence, table arrangement or "
    "README expression is delivered or adapted. ShareAlike is not treated as Attribution-only: a redistributed "
    "or adapted parsing dataset would require reciprocal compliance and a new bounded assessment. The retained "
    "README links CC BY-SA 3.0; full reciprocal legalcode is not retained. This facts-only use does not claim "
    "a grant to relicense the owner-authored note or a verified license for a parsing-data adaptation."
)


@dataclass(frozen=True)
class Inputs:
    candidate: dict[str, Any]
    receipt: TranslationAnnotationCompilationReceipt
    owner: dict[str, Any]
    authority: dict[str, Any]


def producer_files(producer: str) -> tuple[tuple[str, str], ...]:
    if len(producer) != 40 or any(c not in "0123456789abcdef" for c in producer):
        raise ValueError("producer must be an exact commit SHA")
    resolved = (
        subprocess.run(["git", "rev-parse", producer + "^{commit}"], cwd=ROOT, capture_output=True, check=True)
        .stdout.decode()
        .strip()
    )
    if resolved != producer:
        raise ValueError("producer is not an exact commit")
    result: list[tuple[str, str]] = []
    for path in (*RELEASE_FILES, *COMPILER_FILES):
        committed = subprocess.run(
            ["git", "show", f"{producer}:{path}"], cwd=ROOT, capture_output=True, check=True
        ).stdout
        raw = read_regular(ROOT, path)
        if committed != raw:
            raise ValueError(f"producer source drift: {path}")
        result.append((path, sha(raw)))
    return tuple(result)


def exact_file(relative: str, digest: str, size: int | None = None) -> bytes:
    raw = read_regular(ROOT, relative)
    if sha(raw) != digest or (size is not None and len(raw) != size):
        raise ValueError(f"pinned input identity differs: {relative}")
    return raw


def load_inputs() -> Inputs:
    candidate = decode(
        exact_file(
            "artifacts/J13-LAB-01/translation-annotation-package.j13-pilot-01.candidate.json", CANDIDATE_SHA, 20925
        )
    )
    raw = exact_file(
        "artifacts/J13-LAB-01/translation-annotation-compilation-receipt.j13-pilot-01.candidate.json",
        RECEIPT_SHA,
        77503,
    )
    decode(raw)
    receipt = TranslationAnnotationCompilationReceipt.model_validate_json(raw)
    owner = decode(exact_file("artifacts/J13-LAB-02/owner-decision.json", OWNER_SHA))
    authority = load_j13_upstream_authority()
    exact_file(
        "activations/ACT-J13-LAB-02-FINALIZE-PRIVATE-PILOT-RELEASE-v1.json",
        "ef38fd4e87b85b3b5062ede0c7890058450a16d250af6d9e452f39ef04fcff68",
    )
    exact_file(".local/evidence/J13-LAB-02/merge-comment-5548832754.txt", COMMENT_SHA, 4464)
    for entry in authority["manifest"]["consumer_conformance_references"]:
        exact_file(
            ".local/evidence/J13-LAB-02/" + Path(entry["source_path"]).name, entry["sha256"], entry["byte_count"]
        )
    for path, digest in receipt.compiler_files:
        exact_file(path, digest)
    if tuple(a["annotation_issue_id"] for a in candidate["annotations"]) != ROSTER:
        raise ValueError("exact three-note roster differs")
    for note in owner["approved_annotations"]:
        match = next(f for f in authority["manifest"]["files"] if f["git_blob"] == note["notes_git_blob"])
        record = decode(exact_file(match["fixture_path"], note["notes_original_sha256"]))
        if record["annotation"]["annotation_issue_id"] != note["annotation_issue_id"]:
            raise ValueError("Notes identity differs")
    return Inputs(candidate, receipt, owner, authority)


def rights(archive: Path, inputs: Inputs) -> tuple[list[dict[str, Any]], bytes]:
    sources = load_j13_source_authority(archive)
    expected = {s.source_id: s for s in inputs.receipt.source_snapshots}
    findings: list[dict[str, Any]] = []
    retained: dict[str, SourceAuthority] = {}
    for source in sources:
        if source.source_id not in PERMISSIONS:
            continue
        if source.snapshot is None or source.snapshot != expected[source.source_id]:
            raise ValueError(f"reader rights: {source.source_id} snapshot/admission binding missing or changed")
        files = dict(source.files)
        for name, digest in PERMISSIONS[source.source_id]:
            if name not in files or sha(files[name]) != digest:
                raise ValueError(f"reader rights: {source.source_id} permission object {name} missing or changed")
        retained[source.source_id] = source
        findings.append(
            {
                "basis_id": "J13-LAB-02-RIGHTS-" + source.source_id,
                "source_id": source.source_id,
                "source_version": source.snapshot.edition_identity + "; snapshot " + source.snapshot.snapshot_identity,
                "snapshot_identity": source.snapshot.snapshot_identity,
                "components": [(n, sha(b)) for n, b in source.files],
                "permission_evidence": PERMISSIONS[source.source_id],
                "grant": GRANTS[source.source_id],
                "obligations": obligations(source.source_id),
                "fulfillment": [
                    NOTICES + ": " + source.source_id,
                    "Package source_citations attribution and notice routing",
                ],
                "reciprocal_assessment": RECIPROCAL
                if source.source_id == "SP01-SRC-002"
                else "No reciprocal condition.",
                "result": "supported",
            }
        )
    if set(retained) != set(PERMISSIONS):
        raise ValueError("reader rights: all four exact source authorities required; no subset release")
    return findings, notices(retained, inputs)


def obligations(source_id: str) -> list[str]:
    if source_id == "SP01-SRC-001":
        return [
            "Retain copyright, attribution, source URI, license and warranty disclaimer.",
            "Identify excerpts and changes; no endorsement or additional restriction of licensed material.",
        ]
    if source_id == "SP01-SRC-002":
        return [
            "Retain attribution, edition, DOI and CC BY-SA 3.0 URI; distinguish factual use from adaptation.",
            "Do not restrict recipients' source-license rights or represent owner prose as relicensed.",
        ]
    if source_id == "SP01-SRC-004":
        return ["Do not present modified translation text as the World English Bible; distinguish commentary."]
    return ["Preserve accurate public-domain TEI attribution; no restricted PDF is delivered."]


def notices(sources: dict[str, SourceAuthority], inputs: Inputs) -> bytes:
    lines = [
        "John 13 private offline pilot — source notices",
        "",
        "Carry this complete notice file with the package in Biblos, without requiring the private receipt.",
        "Joseph-controlled private pilot is the project's operational scope. These controls do not revoke",
        "source licenses or impose additional legal restrictions on recipients of licensed source material.",
        "Owner-authored commentary remains distinct; no whole-note relicensing or source endorsement is claimed.",
        "",
    ]
    for source_id, source in sources.items():
        assert source.snapshot is not None
        citation = next(c for c in inputs.candidate["source_citations"] if c["citation_display"] == source_id)
        lines += [source_id, citation["attribution"], "Snapshot: " + source.snapshot.snapshot_identity]
        lines += ["Source: " + u for u in source.snapshot.retrieval_urls]
        lines += obligations(source_id)
        if source_id == "SP01-SRC-001":
            lines += [
                "https://creativecommons.org/licenses/by/4.0/",
                "Greek excerpts from the pinned SBLGNT text; excerpted without changing quoted words.",
                "Lemma forms are separately verified against the public-domain lexicon and morphology facts.",
                dict(source.files)["LICENSE"].decode("utf-8"),
            ]
        elif source_id == "SP01-SRC-002":
            lines += [
                "http://creativecommons.org/licenses/by-sa/3.0/",
                "https://doi.org/10.5281/zenodo.376200",
                RECIPROCAL,
            ]
        else:
            lines += [GRANTS[source_id]]
        lines += [""]
    return ("\n".join(lines) + "\n").encode("utf-8")


# Exact field overlays; full fields also receive original-exposition records below.
# (annotation index, field relative to annotation or absolute claim path, material, source, substrings)
MATERIALS = (
    (0, "short_note", "quotation", "001", ("μέρος",)),
    (0, "short_note", "quotation", "004", ("no part",)),
    (0, "short_note", "lexical paraphrase", "005", ("a part, share, or portion",)),
    (0, "full_note_paragraphs/0", "quotation", "001", ("οὐκ ἔχεις μέρος μετʼ ἐμοῦ",)),
    (0, "full_note_paragraphs/0", "quotation", "004", ("you have no part with me",)),
    (0, "full_note_paragraphs/1", "quotation", "001", ("μέρος",)),
    (0, "full_note_paragraphs/1", "morphology-derived statement", "002", ("The noun μέρος",)),
    (0, "full_note_paragraphs/1", "quotation", "004", ("no part",)),
    (0, "full_note_paragraphs/1", "lexical paraphrase", "005", ("a part, share, or portion",)),
    (0, "/claim_summaries/0/claim_summary", "quotation", "004", ("you have no part with me",)),
    (0, "/claim_summaries/1/claim_summary", "quotation", "001", ("μέρος",)),
    (0, "/claim_summaries/1/claim_summary", "lexical paraphrase", "005", ("a part, share, or portion",)),
    (0, "/claim_summaries/1/claim_summary", "morphology-derived statement", "002", ("μέρος",)),
    (1, "short_note", "lexical paraphrase", "005", ("λούω refers to bathing", "νίπτω refers here to washing the feet")),
    (1, "full_note_paragraphs/0", "quotation", "004", ("bathed", "washed")),
    (1, "full_note_paragraphs/0", "quotation", "001", ("λελουμένος",)),
    (1, "full_note_paragraphs/0", "lexical paraphrase", "005", ("λούω", "νίπτω")),
    (1, "full_note_paragraphs/0", "morphology-derived statement", "002", ("λελουμένος, from λούω",)),
    (1, "full_note_paragraphs/1", "lexical paraphrase", "005", ("a whole bath from a local washing",)),
    (1, "full_note_paragraphs/1", "morphology-derived statement", "002", ("The perfect participle",)),
    (1, "interpretive_limits/2", "morphology-derived statement", "002", ("The perfect form",)),
    (1, "/claim_summaries/3/claim_summary", "quotation", "004", ("bathed", "washed")),
    (1, "/claim_summaries/4/claim_summary", "quotation", "001", ("λελουμένος",)),
    (1, "/claim_summaries/4/claim_summary", "lexical paraphrase", "005", ("λούω", "νίπτω")),
    (1, "/claim_summaries/4/claim_summary", "morphology-derived statement", "002", ("λελουμένος from λούω",)),
    (1, "/claim_summaries/5/claim_summary", "lexical paraphrase", "005", ("the Greek lexical contrast",)),
    (2, "short_note", "quotation", "001", ("ἐγώ εἰμι",)),
    (2, "short_note", "quotation", "004", ("I am he",)),
    (2, "short_note", "morphology-derived statement", "002", ("without a separate word for “he.”",)),
    (2, "full_note_paragraphs/0", "quotation", "001", ("ὅτι ἐγώ εἰμι",)),
    (2, "full_note_paragraphs/0", "morphology-derived statement", "002", ("There is no separate Greek word",)),
    (2, "/claim_summaries/6/claim_summary", "quotation", "004", ("I am he",)),
    (2, "/claim_summaries/7/claim_summary", "quotation", "001", ("ἐγώ εἰμι",)),
    (2, "/claim_summaries/7/claim_summary", "morphology-derived statement", "002", ("without a separate word",)),
)


def at(document: Any, pointer: str) -> Any:
    for part in pointer.split("/")[1:]:
        document = cast(list[Any], document)[int(part)] if isinstance(document, list) else document[part]
    return document


def material(annotation: str, pointer: str, text: str, kind: str, basis: str, reason: str) -> dict[str, Any]:
    return {
        "annotation_id": annotation,
        "pointer": pointer,
        "text": text,
        "material_type": kind,
        "basis_ids": [basis],
        "reason": reason,
        "result": "supported",
    }


def citation_inventory(package: dict[str, Any], i: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    annotation = package["annotations"][i]
    for j, citation in enumerate(package["source_citations"]):
        if citation["source_reference_id"] in annotation["source_reference_ids"]:
            for key in ("attribution", "citation_display", "exact_locator", "display_limitations"):
                items.append(
                    material(
                        ROSTER[i],
                        f"/source_citations/{j}/{key}",
                        canonical(citation[key]).decode(),
                        "citation/notice",
                        "J13-LAB-02-RIGHTS-" + citation["citation_display"],
                        "Factual citation identity and required source notice; source terms preserved.",
                    )
                )
    return items


def metadata_inventory(package: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for i, annotation in enumerate(package["annotations"]):
        items.append(
            material(
                ROSTER[i],
                f"/annotations/{i}/eligibility",
                canonical(annotation["eligibility"]).decode(),
                "citation/notice",
                OWNER_ID,
                "Task-authorized operation metadata; source licenses remain intact. "
                "Training and non-reader decisions preserve their existing authority; no license grant inferred.",
            )
        )
        items.append(
            material(
                ROSTER[i],
                "/target",
                canonical(package["target"]).decode(),
                "citation/notice",
                "J13-LAB-02-RIGHTS-SP01-SRC-004",
                "Factual frozen Scripture edition/target identifiers.",
            )
        )
    return items


def notice_inventory(notice: bytes) -> list[dict[str, Any]]:
    text = notice.decode()
    offsets = [text.index("\n" + source + "\n") + 1 for source in PERMISSIONS] + [len(text)]
    items: list[dict[str, Any]] = []
    for annotation in ROSTER:
        items.append(
            material(
                annotation,
                NOTICES,
                text[: offsets[0]],
                "original prose",
                OWNER_ID,
                "Task-authorized administrative notice introduction; no source grant inferred.",
            )
        )
        for i, source in enumerate(PERMISSIONS):
            items.append(
                material(
                    annotation,
                    NOTICES,
                    text[offsets[i] : offsets[i + 1]],
                    "citation/notice",
                    "J13-LAB-02-RIGHTS-" + source,
                    "Exact source-specific attribution and obligations. The verbatim SBLGNT LICENSE "
                    "legalcode is CC0 under its retained final paragraph; no MorphGNT README prose copied.",
                )
            )
    return items


def payload_inventory(package: dict[str, Any], notice: bytes) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for i, annotation in enumerate(package["annotations"]):
        paths = [f"/annotations/{i}/short_note"]
        for key in ("full_note_paragraphs", "interpretive_limits"):
            paths += [f"/annotations/{i}/{key}/{j}" for j in range(len(annotation[key]))]
        paths += [
            f"/claim_summaries/{j}/claim_summary"
            for j, c in enumerate(package["claim_summaries"])
            if c["claim_reference_id"] in annotation["claim_reference_ids"]
        ]
        for path in paths:
            items.append(
                material(
                    ROSTER[i],
                    path,
                    at(package, path),
                    "original prose",
                    OWNER_ID,
                    "Exact approved editorial exposition; embedded source material is separately inventoried. "
                    "English explanatory glosses and withheld variant topic are owner exposition.",
                )
            )
        for j, anchor in enumerate(annotation["anchors"]):
            items.append(
                material(
                    ROSTER[i],
                    f"/annotations/{i}/anchors/{j}/expected_phrase",
                    anchor["expected_phrase"],
                    "quotation",
                    "J13-LAB-02-RIGHTS-SP01-SRC-004",
                    "Exact bound WEB anchor excerpt.",
                )
            )
        items.extend(citation_inventory(package, i))
    for i, field, kind, source, strings in MATERIALS:
        path = field if field.startswith("/") else f"/annotations/{i}/{field}"
        for text in strings:
            if text not in at(package, path):
                raise ValueError("payload rights field/substring differs")
            reason = RECIPROCAL if source == "002" else GRANTS["SP01-SRC-" + source]
            items.append(material(ROSTER[i], path, text, kind, "J13-LAB-02-RIGHTS-SP01-SRC-" + source, reason))
    items.extend(notice_inventory(notice))
    items.extend(metadata_inventory(package))
    return items


def derive(inputs: Inputs, findings: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    package = deepcopy(inputs.candidate)
    delta: list[dict[str, Any]] = []
    required = ["J13-LAB-02-RIGHTS-" + s for s in PERMISSIONS]
    if [f["basis_id"] for f in findings] != required or any(f["result"] != "supported" for f in findings):
        raise ValueError("reader rights are incomplete")
    changes: list[tuple[str, Any, str]] = [("/package_revision", 2, "Frozen first-install release representation")]
    for i in range(3):
        prefix = f"/annotations/{i}"
        changes += [
            (prefix + "/editorial_state", "owner_approved", "Exact prior editorial decision"),
            (
                prefix + "/eligibility/reader_delivery",
                {
                    "decision": "allowed",
                    "authority_id": OWNER_ID,
                    "basis_record_ids": [OWNER_ID, *required],
                    "limitations": [
                        inputs.owner["delivery_scope"],
                        "Biblos must carry the complete companion source notices.",
                        "Project operation scope does not restrict recipients' existing source-license rights.",
                    ],
                },
                "Exact approval plus supported actual-payload rights and companion notices",
            ),
        ]
        for operation in ("retrieval", "evaluation", "public_sharing"):
            changes.append(
                (
                    prefix + f"/eligibility/{operation}/limitations",
                    [f"{operation.replace('_', ' ').capitalize()} remains unauthorized; separate authority required."],
                    "Remove obsolete pending-owner wording without changing decision or authority",
                )
            )
    for i in range(len(package["source_citations"])):
        changes.append(
            (
                f"/source_citations/{i}/display_limitations",
                [
                    "Carry the companion source notices with this private offline pilot package.",
                    "Project scope preserves recipients' existing source-license rights.",
                ],
                "Replace resolved candidate-only statement with required notice routing",
            )
        )
    for pointer, value, reason in changes:
        parent, key = pointer.rsplit("/", 1)
        target = at(package, parent)
        old = target[key]
        target[key] = value
        delta.append(
            {
                "pointer": pointer,
                "old_canonical_json": canonical(old).decode(),
                "new_canonical_json": canonical(value).decode(),
                "reason": reason,
                "basis_ids": [OWNER_ID, *required],
            }
        )
    return package, delta


def protected(candidate: dict[str, Any], release: dict[str, Any], delta: list[dict[str, Any]]) -> str:
    restored = deepcopy(release)
    for change in delta:
        parent, key = change["pointer"].rsplit("/", 1)
        target = at(restored, parent)
        if canonical(target[key]).decode() != change["new_canonical_json"]:
            raise ValueError("permitted delta new value differs")
        if canonical(at(candidate, change["pointer"])).decode() != change["old_canonical_json"]:
            raise ValueError("permitted delta old value differs")
        target[key] = decode(change["old_canonical_json"].encode())
    if canonical(restored) != canonical(candidate):
        raise ValueError("protected editorial content or unlisted JSON-pointer delta")
    return sha(canonical(candidate))


def validate_first_install(package: dict[str, Any], expected: str | None = None) -> None:
    revision, declared = package["package_revision"], package.get("supersedes_package_file_sha256")
    if type(revision) is not int or revision <= 0:
        raise ValueError("invalid package revision")
    for digest in (declared, expected):
        if digest is not None and (len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest)):
            raise ValueError("invalid predecessor digest")
    if declared is not None:
        if revision <= 1 or expected is None or declared != expected:
            raise ValueError("missing or mismatched predecessor")
    elif expected is not None:
        raise ValueError("unexpected predecessor")


def validate_release(
    package: dict[str, Any], inputs: Inputs, findings: list[dict[str, Any]], helper: UnicodeHelper
) -> list[dict[str, Any]]:
    expected, delta = derive(inputs, findings)
    validator: Any = Draft202012Validator(inputs.authority["schema"])
    validator.validate(package)
    validate_first_install(package)
    if prose_failures(package, helper):
        raise ValueError("release violates plain-text-v1 notice routing")
    for annotation in package["annotations"]:
        validate_anchors(annotation["anchors"], inputs.authority, helper)
    protected(inputs.candidate, package, delta)
    if canonical(package) != canonical(expected):
        raise ValueError("release differs from contextual reconstruction")
    return delta


def file_record(name: str, raw: bytes) -> dict[str, Any]:
    return {"name": name, "sha256": sha(raw), "byte_count": len(raw)}


def build_outputs(
    archive: Path, producer: str, fingerprints: tuple[tuple[str, str], ...], before: str, helper: UnicodeHelper
) -> dict[str, bytes]:
    inputs = load_inputs()
    findings, notice = rights(archive, inputs)
    package, _ = derive(inputs, findings)
    delta = validate_release(package, inputs, findings, helper)
    raw = canonical(package)
    constants = TranslationAnnotationCompilationReceiptV2.model_json_schema()["properties"]
    data = {k: v["const"] for k, v in constants.items() if "const" in v}
    data.update(
        {
            "input_candidate": file_record(
                "translation-annotation-package.j13-pilot-01.candidate.json", canonical(inputs.candidate)
            ),
            "input_receipt": {
                "name": "translation-annotation-compilation-receipt.j13-pilot-01.candidate.json",
                "sha256": RECEIPT_SHA,
                "byte_count": 77503,
            },
            "owner_decision_sha256": OWNER_SHA,
            "approval_comment_sha256": COMMENT_SHA,
            "notes": inputs.owner["approved_annotations"],
            "upstream_manifest_sha256": MANIFEST_SHA,
            "consumer_references": [
                (e["source_path"], e["sha256"]) for e in inputs.authority["manifest"]["consumer_conformance_references"]
            ],
            "producer_commit": producer,
            "producer_files": fingerprints,
            "source_rights": findings,
            "payload_inventory": payload_inventory(package, notice),
            "expected_installed_predecessor": None,
            "protected_content_sha256": protected(inputs.candidate, package, delta),
            "permitted_delta": delta,
            "permitted_delta_sha256": sha(canonical(delta)),
            "non_reader_eligibility_sha256": sha(
                canonical(
                    [
                        {k: v for k, v in a["eligibility"].items() if k != "reader_delivery"}
                        for a in package["annotations"]
                    ]
                )
            ),
            "package_file": file_record(PACKAGE, raw),
            "notice_file": file_record(NOTICES, notice),
            "archive_inventory_sha256": before,
        }
    )
    data["receipt_identity"] = sha(canonical(data))
    receipt = TranslationAnnotationCompilationReceiptV2.model_validate_json(canonical(data))
    outputs = {PACKAGE: raw, RECEIPT: canonical(receipt.model_dump(mode="json")), NOTICES: notice}
    handoff = [
        "# Private Biblos admission handoff",
        "",
        "No Biblos admission has been performed.",
        "First installation: tap:j13-pilot-01 revision 2; expected predecessor nil; declared predecessor absent.",
        "Annotations remain revision 2 with supersedes_revision 1; no prior annotation installation required.",
        "Review exact private bytes and PR head before attempting independent admission.",
        "Reader delivery requires package, package sidecar, complete SOURCE-NOTICES and its sidecar.",
        "Receipt and its sidecar are separate private governance artifacts, not reader runtime dependencies.",
        "Producer: " + producer,
        "",
        *ROSTER,
        "",
    ]
    for name, content in tuple(outputs.items()):
        sidecar = name.rsplit(".", 1)[0] + ".sha256"
        outputs[sidecar] = f"{sha(content)}  {name}\n".encode()
        handoff += [
            f"{name}: {sha(content)}; {len(content)} bytes",
            f"{sidecar}: {sha(outputs[sidecar])}; {len(outputs[sidecar])} bytes",
        ]
    outputs[HANDOFF] = ("\n".join(handoff) + "\n").encode()
    return outputs


def validate_context(
    outputs: dict[str, bytes],
    archive: Path,
    producer: str,
    fingerprints: tuple[tuple[str, str], ...],
    before: str,
    helper: UnicodeHelper,
) -> None:
    if producer_files(producer) != fingerprints or inventory(archive) != before:
        raise ValueError("contextual producer fingerprints or archive inventory differs")
    for name in (PACKAGE, RECEIPT):
        if canonical(decode(outputs[name])) != outputs[name]:
            raise ValueError("noncanonical or duplicate-key release JSON")
    TranslationAnnotationCompilationReceiptV2.model_validate_json(outputs[RECEIPT])
    reconstructed = build_outputs(archive, producer, fingerprints, before, helper)
    if inventory(archive) != before:
        raise ValueError("archive changed during contextual reconstruction")
    if reconstructed != outputs:
        raise ValueError("contextual release/receipt/notices/sidecars/handoff mismatch")
