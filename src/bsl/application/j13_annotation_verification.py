from __future__ import annotations

import re
from typing import Any
from xml.etree import ElementTree

from bsl.application.j13_package_compilation import project_annotation, prose_failures, validate_anchors
from bsl.contracts.translation_annotation_compilation import (  # pyright: ignore[reportPrivateUsage]
    REJECTION,
    ROSTER,
    _ClaimSupport,  # pyright: ignore[reportPrivateUsage]
    _Decision,  # pyright: ignore[reportPrivateUsage]
    _Evidence,  # pyright: ignore[reportPrivateUsage]
)
from bsl.infrastructure.j13_authority import ROOT, SourceAuthority, UnicodeHelper, decode, read_regular, sha

# Frozen bounded assertions for these exact editorial inputs, not admission decisions.
TOKENS = {
    1: (("εἰς", "εἰς", "--------"), ("τέλος", "τέλος", "----ASN-")),
    8: (("μέρος", "μέρος", "----ASN-"),),
    10: (("λελουμένος", "λούω", "-XMPNSM-"), ("νίψασθαι", "νίπτω", "-AMN----")),
    15: (("ὑπόδειγμα", "ὑπόδειγμα", "----ASN-"),),
    17: (("μακάριοι", "μακάριος", "----NPM-"),),
    19: (("ἐγώ", "ἐγώ", "----NS--"), ("εἰμί", "εἰμί", "1PAI-S--")),
}
GREEK = {
    1: ("εἰς τέλος",),
    8: ("Οὐ μὴ νίψῃς", "Ἐὰν μὴ νίψω σε", "οὐκ ἔχεις μέρος μετʼ ἐμοῦ"),
    10: ("λελουμένος", "τοὺς πόδας νίψασθαι", "καθαρὸς ὅλος"),
    15: ("ὑπόδειγμα",),
    17: ("μακάριοί",),
    19: ("λέγω ὑμῖν πρὸ τοῦ γενέσθαι", "πιστεύσητε ὅταν γένηται", "ὅτι ἐγώ εἰμι."),
}
LEXICON = {1: ("τέλος",), 8: ("μέρος",), 10: ("λούω", "νίπτω"), 15: ("ὑπόδειγμα",), 17: ("μακάριος",), 19: ()}
LEXICAL_VALUES = {
    "τέλος": "to or at the end",
    "μέρος": "a part, share, portion",
    "λούω": "to bathe, wash the body",
    "νίπτω": "to wash, usually of a part of the body",
    "ὑπόδειγμα": "example",
    "μακάριος": "blessed, happy",
}

# Assessments cover the exact frozen prose and limits, not arbitrary future notes.
ASSESSMENTS = {
    1: (
        "The exact phrase and lexical endpoint sense support continuation; completion is a contextual "
        "reading, not an additional independently encoded meaning."
    ),
    15: (
        "The lexical range explains the rendering; verse 14 supplies obligation to wash feet and verse 15 "
        "commands imitation. The limits withhold ordinance conclusions."
    ),
    17: (
        "The adjective and practical condition require the exact admitted comparison; emotion and favor "
        "claims require independent lexical evidence."
    ),
    8: (
        "Peter refuses washing; the negative condition makes washing necessary for having a share with Jesus. "
        "The lexicon supports part/share/portion; participation is a contextual paraphrase. The limits "
        "decline sacramental conclusions absent from this wording."
    ),
    10: (
        "The perfect passive participle identifies an already bathed person; feet are the object of the "
        "separate washing. The two entries support whole-body versus local washing. The English contrast "
        "preserves this distinction. The limits exclude variant adjudication and sacramental claims."
    ),
    19: (
        "The clause ends with first-person I am and no following pronoun. WEB supplies he. Another exact "
        "Johannine occurrence establishes repeated wording. Prediction before occurrence and belief afterward "
        "support the foreknowledge limit; divine-name and Exodus claims are explicitly withheld."
    ),
}


def _value(source: SourceAuthority, assertion: str, component: str, locator: str, value: str) -> _Evidence:
    snapshot = source.snapshot
    if snapshot is None:
        raise ValueError("missing source snapshot")
    item = next(o for o in snapshot.objects if o.relative_path == component)
    return _Evidence(
        assertion_id=assertion,
        source_id=source.source_id,
        snapshot_identity=snapshot.snapshot_identity,
        component=component,
        component_sha256=item.sha256,
        locator=locator,
        value=value,
        value_sha256=sha(value.encode()),
        attribution=snapshot.attribution,
        allowed_operations=snapshot.allowed_operations,
    )


def _verse(text: str, verse: int, kind: str) -> str:
    lines = text.splitlines()
    if kind == "greek":
        return next(line.split("\t", 1)[1] for line in lines if line.startswith(f"John 13:{verse}\t"))
    if kind == "morphology":
        return "\n".join(line for line in lines if line.startswith(f"0413{verse:02d} "))
    chapter, active = None, False
    fragments: list[str] = []
    for line in lines:
        if line.startswith("\\c "):
            chapter, active = line.split()[1], False
        elif line.startswith("\\v "):
            active = chapter == "13" and line.split()[1] == str(verse)
            if active:
                fragments.append(line)
        elif active:
            fragments.append(line)
    return "\n".join(fragments)


def _evidence(record: dict[str, Any], sources: tuple[SourceAuthority, ...], verse: int) -> tuple[_Evidence, ...]:
    result: list[_Evidence] = []
    assertions = {a["source_class"]: a for a in record["source_assertions"]}
    specs = (
        (0, "greek_text", "data/sblgnt/text/John.txt", "greek"),
        (1, "morphology", "64-Jn-morphgnt.txt", "morphology"),
        (3, "english_comparison", "73-JHNeng-web.usfm", "english"),
    )
    for index, kind, component, mode in specs:
        source = sources[index]
        text = dict(source.files)[component].decode()
        selected = (14, verse) if verse == 15 and mode in ("greek", "english") else (verse,)
        for number in selected:
            value = _verse(text, number, mode)
            if not value:
                raise LookupError(f"missing {source.source_id} John 13:{number} locator")
            result.append(
                _value(source, assertions[kind]["source_assertion_id"], component, f"John 13:{number}", value)
            )
        if verse == 19 and mode == "greek":
            repeated = [
                line for line in text.splitlines() if "ἐγώ εἰμι" in line and not line.startswith("John 13:19\t")
            ]
            if not repeated:
                raise LookupError("no exact repeated ἐγώ εἰμι location in admitted John")
            line = repeated[0]
            result.append(_value(source, assertions[kind]["source_assertion_id"], component, *line.split("\t", 1)))
    if LEXICON[verse]:
        component = "abbott-smith.tei.xml"
        tree = ElementTree.fromstring(dict(sources[4].files)[component])
        for lemma in LEXICON[verse]:
            entry = next(e for e in tree.iter() if e.tag.endswith("}entry") and e.get("n", "").split("|")[0] == lemma)
            result.append(
                _value(
                    sources[4],
                    assertions["lexicon"]["source_assertion_id"],
                    component,
                    "entry[@n='" + entry.attrib["n"] + "']",
                    "".join(entry.itertext()),
                )
            )
    return tuple(result)


def _web_display(value: str) -> str:
    # Decode only the observed WEB USFM word and presentation markers. Evidence
    # retains the original fragment; this derived view never changes Notes or hashes.
    text = re.sub(r"\\(?P<tag>\+?w) (?P<word>[^\\|]+)\|[^\\]*\\(?P=tag)\*", r"\g<word>", value)
    text = re.sub(r"^\\v [0-9]+ ", "", text)
    text = re.sub(r"\\wj\*(?=\s|$)", "", text)
    text = re.sub(r"\\(?:wj|p)(?=\s|$) ?", "", text)
    if "\\" in text:
        raise ValueError("unsupported or malformed admitted WEB USFM marker")
    return text


def _unsupported(verse: int, evidence: tuple[_Evidence, ...], record: dict[str, Any]) -> tuple[str, str, str] | None:
    greek = next(e.value for e in evidence if e.source_id == "SP01-SRC-001" and e.locator == f"John 13:{verse}")
    morphology = next(e.value for e in evidence if e.source_id == "SP01-SRC-002")
    tokens = tuple((p[5], p[6], p[2]) for line in morphology.splitlines() if len(p := line.split()) == 7)
    claims = record["claim_assertions"]
    if not all(term in greek for term in GREEK[verse]) or not all(token in tokens for token in TOKENS[verse]):
        return claims[1]["claim_text"], "Greek form or parsing differs.", "Use the admitted form and parsing."
    entries = tuple(e for e in evidence if e.source_id == "SP01-SRC-005")
    for lemma, entry in zip(LEXICON[verse], entries, strict=True):
        if LEXICAL_VALUES[lemma] not in entry.value:
            return claims[1]["claim_text"], "Lexicon does not attest this range.", "Use the attested lexical sense."
    if verse == 1 and "or here, to the uttermost" in entries[0].value:
        return (
            "The temporal force is clear",
            "John 13:1 entry allows another reading.",
            "A temporal reading is available",
        )
    if verse == 15 and "demonstration" not in entries[0].value:
        return (
            claims[1]["claim_text"],
            "No demonstration sense attested.",
            "ὑπόδειγμα denotes an example for imitation.",
        )
    english = next(e.value for e in evidence if e.source_id == "SP01-SRC-004" and e.locator == f"John 13:{verse}")
    english = _web_display(english)
    if not all(a["expected_phrase"] in english for a in record["annotation"]["anchors"] if a["verse"] == verse):
        return claims[0]["claim_text"], "Admitted WEB wording differs.", "Identify the supporting edition."
    return None


def _revision(common: dict[str, Any], problem: tuple[str, str, str], **support: Any) -> _Decision:
    statement, reason, replacement = problem
    return _Decision(
        **common,
        disposition="NEEDS_EDITORIAL_REVISION",
        reason=reason,
        unsupported_statement=statement,
        suggested_replacement=replacement,
        **support,
    )


def _evaluate(
    record: dict[str, Any], authority: dict[str, Any], sources: tuple[SourceAuthority, ...], helper: UnicodeHelper
) -> _Decision:
    annotation = record["annotation"]
    verse = annotation["anchors"][0]["verse"]
    issue = annotation["annotation_issue_id"].split(":")[-1]
    filename = f"tan-john-13-{verse:02d}-{issue}.r{record['projection_revision']}.json"
    row = next(f for f in authority["manifest"]["files"] if f["source_path"].endswith("/" + filename))
    common = {
        "annotation_id": annotation["annotation_issue_id"],
        "revision": record["projection_revision"],
        "projection_sha256": row["sha256"],
    }
    if record != decode(read_regular(ROOT, row["fixture_path"])):
        raise ValueError("decoded Notes authority drift")
    if verse == 30:
        return _Decision(**common, disposition="REJECTED_NOT_TRANSLATION_NUANCE", reason=REJECTION)
    try:
        validate_anchors(annotation["anchors"], authority, helper)
    except ValueError as error:
        return _Decision(
            **common,
            disposition="NEEDS_EDITORIAL_REVISION",
            reason=str(error),
            unsupported_statement=str(annotation["anchors"]),
            suggested_replacement="Rebind the anchor to the exact target verse without changing reader prose.",
        )
    candidate = project_annotation(record, authority["schema"])
    prose = {
        "target": record["target_scripture_authority"],
        "annotations": [candidate],
        "source_citations": [],
        "claim_summaries": [{"claim_summary": c["claim_text"]} for c in record["claim_assertions"]],
    }
    failures = prose_failures(prose, helper)
    if failures:
        _, statement, reason = failures[0]
        return _revision(
            common, (statement, reason, "Replace the recognized markup with an owner-reviewed plain-text statement.")
        )
    checked = tuple(s.source_id for s in sources if s.snapshot is not None)
    required = (0, 1, 3, 4) if LEXICON[verse] else (0, 1, 3)
    missing = tuple(
        sources[i].source_id
        for i in required
        if (snapshot := sources[i].snapshot) is None or "EXACT_RUNTIME_LOOKUP" not in snapshot.allowed_operations
    )
    if verse == 17:
        missing += ("EDITORIAL-SRC-KJV-001: exact KJV edition, locator, attribution and jurisdictional rights",)
    try:
        if missing:
            raise LookupError("; ".join(missing))
        evidence = _evidence(record, sources, verse)
    except (LookupError, StopIteration) as error:
        return _Decision(
            **common,
            disposition="SOURCE_OR_RIGHTS_GAP",
            reason="Required source, rights, component or exact locator unavailable.",
            missing_sources=missing or (str(error) or "exact asserted locator",),
            checked_sources=checked,
            unsupported_statement=record["claim_assertions"][0 if missing else 1]["claim_text"],
        )
    problem = _unsupported(verse, evidence, record)
    if problem:
        return _revision(common, problem, evidence=evidence, checked_sources=checked)
    claims = tuple(
        _ClaimSupport(
            claim_id=c["claim_assertion_id"],
            statement=c["claim_text"],
            assertion_ids=tuple(c["source_assertion_ids"]),
            assessment="Exact bound/admitted English comparison." if index == 0 else ASSESSMENTS[verse],
        )
        for index, c in enumerate(record["claim_assertions"])
    )
    return _Decision(
        **common,
        disposition="VERIFIED_FOR_PACKAGE_CANDIDATE",
        reason="Exact source, anchor, prose and candidate-state checks passed.",
        evidence=evidence,
        claims=claims,
        checked_sources=checked,
    )


def verify_j13_annotation_batch(
    authority: dict[str, Any], sources: tuple[SourceAuthority, ...], helper: UnicodeHelper
) -> tuple[_Decision, ...]:
    records = authority["records"]
    if tuple(r["annotation"]["annotation_issue_id"] for r in records) != ROSTER:
        raise ValueError("selected record roster differs")
    return tuple(_evaluate(record, authority, sources, helper) for record in records)
