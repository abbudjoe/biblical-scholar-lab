from __future__ import annotations

from typing import Any

import rfc8785
from jsonschema import Draft202012Validator

from bsl.contracts.translation_annotation_compilation import (  # pyright: ignore[reportPrivateUsage]
    ROSTER,
    TranslationAnnotationCompilationReceipt,
    _Decision,  # pyright: ignore[reportPrivateUsage]
)
from bsl.infrastructure.j13_authority import MANIFEST_SHA, ROOT, SourceAuthority, UnicodeHelper, sha

PACKAGE_NAME = "translation-annotation-package.j13-pilot-01.candidate.json"
RECEIPT_NAME = "translation-annotation-compilation-receipt.j13-pilot-01.candidate.json"
COMPILER_FILES = (
    "src/bsl/contracts/translation_annotation_compilation.py",
    "src/bsl/application/j13_annotation_verification.py",
    "src/bsl/application/j13_package_compilation.py",
    "src/bsl/infrastructure/j13_authority.py",
    "tools/j13_lab_01_compile_candidate.py",
    "tools/j13_unicode_profile.swift",
)


def canonical_package_bytes(package: dict[str, Any]) -> bytes:
    return rfc8785.dumps(package)


def prose_fields(package: dict[str, Any]) -> list[tuple[str, str]]:
    fields = [("target.translation_version", package["target"]["translation_version"])]
    for index, annotation in enumerate(package["annotations"]):
        prefix = f"annotations.{index}"
        fields.append((prefix + ".short_note", annotation["short_note"]))
        for key in ("full_note_paragraphs", "interpretive_limits"):
            fields.extend((f"{prefix}.{key}.{i}", text) for i, text in enumerate(annotation[key]))
        for operation, decision in annotation["eligibility"].items():
            fields.extend(
                (f"{prefix}.eligibility.{operation}.limitations.{i}", text)
                for i, text in enumerate(decision["limitations"])
            )
    for index, claim in enumerate(package["claim_summaries"]):
        fields.append((f"claim_summaries.{index}.claim_summary", claim["claim_summary"]))
    for index, source in enumerate(package["source_citations"]):
        for key in ("citation_display", "exact_locator", "attribution"):
            fields.append((f"source_citations.{index}.{key}", source[key]))
        fields.extend(
            (f"source_citations.{index}.display_limitations.{i}", text)
            for i, text in enumerate(source["display_limitations"])
        )
    return fields


def prose_failures(package: dict[str, Any], helper: UnicodeHelper) -> list[tuple[str, str, str]]:
    fields = prose_fields(package)
    results = helper.check([{"text": text, "plainText": True, "endpoints": []} for _, text in fields])
    failures = [
        (path, text, result["plainTextError"])
        for (path, text), result in zip(fields, results, strict=True)
        if result["plainTextError"]
    ]
    counts = {path: result["scalarCount"] for (path, _), result in zip(fields, results, strict=True)}
    for index, annotation in enumerate(package["annotations"]):
        prefix = f"annotations.{index}"
        total = sum(count for path, count in counts.items() if path.startswith(prefix + ".full_note_paragraphs."))
        if total > 2400:
            failures.append(
                (prefix + ".full_note_paragraphs", "\n".join(annotation["full_note_paragraphs"]), "scalar limit 2400")
            )
    return failures


def validate_anchors(anchors: list[dict[str, Any]], authority: dict[str, Any], helper: UnicodeHelper) -> None:
    slots = {v["verseNumber"]: v for v in authority["chapter"]["verseSlots"]}
    target = authority["manifest"]["target"]
    previous = (-1, -1)
    ids: set[str] = set()
    for order, anchor in enumerate(anchors, 1):
        verse = anchor["verse"]
        if anchor["book_id"] != "john" or anchor["chapter"] != 13 or verse not in slots:
            raise ValueError("anchor outside exact John 13 authority")
        text = slots[verse]["text"]
        start, length = anchor["utf16_start"], anchor["utf16_length"]
        if length <= 0 or anchor["verse_text_sha256"] != sha(text.encode()):
            raise ValueError("anchor verse hash or length differs")
        result = helper.check([{"text": text, "plainText": False, "endpoints": [start, start + length]}])[0]
        if any(result["endpointErrors"]):
            raise ValueError("invalid UTF-16/grapheme anchor")
        phrase = text.encode("utf-16-le")[start * 2 : (start + length) * 2].decode("utf-16-le")
        if phrase != anchor["expected_phrase"]:
            raise ValueError("anchor expected phrase differs")
        if anchor["anchor_order"] != order or (verse, start) < previous or anchor["anchor_id"] in ids:
            raise ValueError("anchor order or uniqueness differs")
        if any(anchor[key] != target[key] for key in ("scripture_package_id", "scripture_package_content_sha256")):
            raise ValueError("anchor target binding differs")
        ids.add(anchor["anchor_id"])
        previous = (verse, start)


def project_annotation(record: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    annotation = record["annotation"]
    keys = schema["$defs"]["annotation"]["properties"]
    result = {key: value for key, value in annotation.items() if key in keys}
    result["anchors"] = [
        {k: v for k, v in a.items() if k in schema["$defs"]["anchor"]["properties"]} for a in annotation["anchors"]
    ]
    result["supersedes_revision"] = annotation["supersedes_annotation_revision"]
    result.update({key: record["editorial"][key] for key in ("editorial_state", "scholarly_review_label")})
    result.update(source_verification_state="verified", eligibility=record["requested_operation_eligibility"])
    return result


def _candidate(authority: dict[str, Any], decisions: tuple[_Decision, ...]) -> dict[str, Any]:
    package: dict[str, Any] = {
        "schema_version": "translation-annotation-package-v1",
        "package_series_id": "tap:j13-pilot-01",
        "package_revision": 1,
        "annotations": [],
        "claim_summaries": [],
        "source_citations": [],
    }
    package["target"] = {
        k: v
        for k, v in authority["manifest"]["target"].items()
        if k in authority["schema"]["$defs"]["target"]["properties"]
    }
    for record, decision in zip(authority["records"], decisions, strict=True):
        if decision.disposition != "VERIFIED_FOR_PACKAGE_CANDIDATE":
            continue
        annotation = project_annotation(record, authority["schema"])
        references: dict[str, list[str]] = {}
        for index, evidence in enumerate(decision.evidence):
            reference = evidence.assertion_id + f":{index + 1}"
            references.setdefault(evidence.assertion_id, []).append(reference)
            package["source_citations"].append(
                {
                    "source_reference_id": reference,
                    "source_version_id": evidence.source_id + ":" + evidence.snapshot_identity,
                    "citation_display": evidence.source_id,
                    "exact_locator": evidence.locator,
                    "attribution": evidence.attribution.split(" Source: https://")[0],
                    "display_limitations": ["Citation metadata only; no source quotation or reader admission."],
                }
            )
        annotation["claim_reference_ids"] = [claim.claim_id for claim in decision.claims]
        annotation["source_reference_ids"] = [ref for refs in references.values() for ref in refs]
        package["annotations"].append(annotation)
        for claim in decision.claims:
            package["claim_summaries"].append(
                {
                    "claim_reference_id": claim.claim_id,
                    "claim_summary": claim.statement,
                    "source_reference_ids": list(
                        dict.fromkeys(ref for a in claim.assertion_ids for ref in references[a])
                    ),
                }
            )
    return package


def _unique(items: list[dict[str, Any]], key: str) -> set[str]:
    values = [item[key] for item in items]
    if len(values) != len(set(values)):
        raise ValueError("duplicate package identity")
    return set(values)


def validate_package(
    package: dict[str, Any], authority: dict[str, Any], helper: UnicodeHelper, decisions: tuple[_Decision, ...]
) -> None:
    validator: Any = Draft202012Validator(authority["schema"])
    validator.validate(package)
    if tuple(d.annotation_id for d in decisions) != ROSTER:
        raise ValueError("decision roster differs")
    if package != _candidate(authority, decisions):
        raise ValueError("package differs from exact verified decisions, prose, target or proof graph")
    if prose_failures(package, helper):
        raise ValueError("candidate prose violates consumer profile")
    _unique(package["annotations"], "annotation_issue_id")
    claims = _unique(package["claim_summaries"], "claim_reference_id")
    sources = _unique(package["source_citations"], "source_reference_id")
    for annotation in package["annotations"]:
        validate_anchors(annotation["anchors"], authority, helper)
    if {r for a in package["annotations"] for r in a["claim_reference_ids"]} != claims or {
        r for c in package["claim_summaries"] for r in c["source_reference_ids"]
    } != sources:
        raise ValueError("dangling or orphan claim/source reference")
    rendered = canonical_package_bytes(package)
    if any(
        marker in rendered for marker in (b"/Volumes/", b"/Users/", b".local/", b"postgresql://", b"ghp_", b"sk-proj-")
    ):
        raise ValueError("private path or credential in package")


def compile_j13_package_candidate(
    authority: dict[str, Any], decisions: tuple[_Decision, ...], helper: UnicodeHelper
) -> bytes:
    package = _candidate(authority, decisions)
    validate_package(package, authority, helper, decisions)
    return canonical_package_bytes(package)


def canonical_receipt_bytes(receipt: TranslationAnnotationCompilationReceipt) -> bytes:
    return rfc8785.dumps(receipt.model_dump(mode="json"))


def build_outputs(
    authority: dict[str, Any],
    sources: tuple[SourceAuthority, ...],
    decisions: tuple[_Decision, ...],
    helper: UnicodeHelper,
    proof: dict[str, Any],
) -> dict[str, bytes]:
    package = compile_j13_package_candidate(authority, decisions, helper)
    manifest = authority["manifest"]
    accepted = tuple(d.annotation_id for d in decisions if d.disposition == "VERIFIED_FOR_PACKAGE_CANDIDATE")
    files = manifest["files"] + manifest["consumer_conformance_references"]
    constants = TranslationAnnotationCompilationReceipt.model_json_schema()["properties"]
    data = {k: v["const"] for k, v in constants.items() if "const" in v} | {
        "compiler_files": [(p, sha((ROOT / p).read_bytes())) for p in COMPILER_FILES],
        "lab_base": manifest["lab"]["commit"],
        "lab_tree": manifest["lab"]["tree"],
        "upstream_authority_sha256": MANIFEST_SHA,
        "upstream_files": [{k: v for k, v in f.items() if k != "fixture_path"} for f in files],
        "notes_tree_chain": [(r["path"], r["tree"]) for r in manifest["notes_tree_chain"]],
        "source_snapshots": [s.snapshot.model_dump(mode="json") for s in sources if s.snapshot is not None],
        "decisions": [d.model_dump(mode="json") for d in decisions],
        "accepted_roster": accepted,
        "excluded_roster": [
            (d.annotation_id, d.disposition, d.reason) for d in decisions if d.annotation_id not in accepted
        ],
        "unread_records": ["tan:john.13.2:during-supper", "tan:john.13.31:glorified-aorist"],
        "package_sha256": sha(package),
        "package_bytes": len(package),
        **proof,
        "prohibited_operation_counts": [
            (k, 0)
            for k in (
                "source_admissions",
                "archive_writes",
                "database_connections",
                "network",
                "models",
                "providers",
                "cloud",
                "training",
                "upstream_mutations",
                "deferred_record_reads",
                "T09",
                "T10",
            )
        ],
        "limitations": [
            "Candidate only; owner-fixed prose is unchanged. No substitute source or acquisition.",
            "Foundation operations and conformance cases are tested; no claim covers every future runtime.",
        ],
    }
    data["receipt_identity"] = sha(rfc8785.dumps(data))
    receipt = TranslationAnnotationCompilationReceipt.model_validate_json(rfc8785.dumps(data))
    encoded = canonical_receipt_bytes(receipt)
    summary = [
        "# John 13 verification — non-activatable candidate",
        "",
        f"Package SHA-256: `{sha(package)}`",
        f"Receipt identity: `{receipt.receipt_identity}`",
        "",
        "Owner package review remains required.",
        "",
    ]
    for decision in decisions:
        summary.extend([f"- {decision.annotation_id}: **{decision.disposition}**. {decision.reason}"])
        if decision.unsupported_statement:
            summary.append(f"  Exact statement: {decision.unsupported_statement}")
        if decision.suggested_replacement:
            summary.append(f"  Suggested owner revision, not applied: {decision.suggested_replacement}")
        if decision.missing_sources:
            summary.append("  Missing: " + "; ".join(decision.missing_sources))
    outputs = {
        PACKAGE_NAME: package,
        RECEIPT_NAME: encoded,
        "J13-LAB-01-verification-summary.md": ("\n".join(summary) + "\n").encode(),
    }
    for name, content in ((PACKAGE_NAME, package), (RECEIPT_NAME, encoded)):
        outputs[name.removesuffix(".json") + ".sha256"] = f"{sha(content)}  {name}\n".encode()
    return outputs
