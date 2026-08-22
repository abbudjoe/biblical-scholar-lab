from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable, Iterator
from xml.etree import ElementTree

_RIGHTS_CONFLICT_PATTERNS = (
    r"\b(?:license(?:\s+grant)?|permission|grant)\s+(?:(?:has\s+been|was|is)\s+)?(?:replaced|withdrawn|revoked)\b",
)
_SOURCE_SERIF_FONT_PATHS = ("TTF/SourceSerif4-Regular.ttf", "TTF/SourceSerif4-It.ttf")


def _text(files: dict[str, bytes], path: str) -> str:
    try:
        return files[path].decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError(f"approved text component is not UTF-8: {path}") from None


def _rights_error(
    text: str,
    required: tuple[str, ...],
    conflict_patterns: tuple[str, ...] = (),
    *,
    missing: str,
    contradicted: str,
) -> str | None:
    lowered = text.lower()
    if not all(value in lowered for value in required):
        return missing
    if any(re.search(pattern, lowered) for pattern in (*_RIGHTS_CONFLICT_PATTERNS, *conflict_patterns)):
        return contradicted
    return None


def _xml_root(files: dict[str, bytes], path: str) -> ElementTree.Element:
    try:
        return ElementTree.fromstring(_text(files, path))
    except ElementTree.ParseError:
        raise ValueError(f"approved XML component is malformed: {path}") from None


def _sblgnt_checks(files: dict[str, bytes]) -> tuple[str | None, str | None]:
    expected = "καὶ τὸ φῶς ἐν τῇ σκοτίᾳ φαίνει, καὶ ἡ σκοτία αὐτὸ οὐ κατέλαβεν."
    prefix = "John 1:5\t"
    lines = [
        line.rstrip() for line in _text(files, "data/sblgnt/text/John.txt").splitlines() if line.startswith(prefix)
    ]
    if not lines:
        content_error = "SBLGNT_JOHN_1_5_NOT_FOUND"
    elif len(lines) > 1:
        content_error = "SBLGNT_JOHN_1_5_AMBIGUOUS"
    elif lines[0] != f"{prefix}{expected}":
        content_error = "SBLGNT_JOHN_1_5_CONTENT_MISMATCH"
    else:
        content_error = None
    rights_error = _rights_error(
        _text(files, "LICENSE"),
        ("attribution 4.0 international",),
        (r"\bnot\s+(?:licensed|distributed)\s+under\b[^\r\n.]{0,96}\battribution\s+4\.0\s+international\b",),
        missing="SBLGNT_RIGHTS_EVIDENCE_NOT_FOUND",
        contradicted="SBLGNT_RIGHTS_EVIDENCE_CONTRADICTED",
    )
    return content_error, rights_error


def _morphgnt_checks(files: dict[str, bytes]) -> tuple[str | None, str | None]:
    rows = tuple(line.split() for line in _text(files, "64-Jn-morphgnt.txt").splitlines())
    target = ("V-", "3AAI-S--", "κατέλαβεν.", "κατέλαβεν", "κατέλαβε(ν)", "καταλαμβάνω")
    verse_rows = tuple(row for row in rows if row and row[0] == "040105")
    matches = sum(tuple(row[1:]) == target for row in verse_rows)
    if matches == 0:
        content_error = "MORPHGNT_TARGET_ROW_NOT_FOUND"
    elif matches > 1:
        content_error = "MORPHGNT_TARGET_ROW_AMBIGUOUS"
    else:
        content_error = None
    rights_error = _rights_error(
        _text(files, "README.md"),
        ("cc-by-sa license", "/licenses/by-sa/3.0/"),
        (r"\bnot\s+(?:licensed|distributed)\s+under\b[^\r\n.]{0,96}\bcc-by-sa\s+license\b",),
        missing="MORPHGNT_RIGHTS_EVIDENCE_NOT_FOUND",
        contradicted="MORPHGNT_RIGHTS_EVIDENCE_CONTRADICTED",
    )
    return content_error, rights_error


def _xml_events(element: ElementTree.Element) -> Iterator[ElementTree.Element | str]:
    yield element
    if element.tag.rsplit("}", 1)[-1] != "note" and element.text:
        yield element.text
    if element.tag.rsplit("}", 1)[-1] != "note":
        for child in element:
            yield from _xml_events(child)
            if child.tail:
                yield child.tail


def _asv_target(files: dict[str, bytes]) -> tuple[int, str]:
    chapter: str | None = None
    active = False
    targets = 0
    fragments: list[str] = []
    for event in _xml_events(_xml_root(files, "usx/43-JHN.usx")):
        if isinstance(event, str):
            if active:
                fragments.append(event)
            continue
        element = event
        name = element.tag.rsplit("}", 1)[-1]
        if name == "chapter":
            active = False
            chapter = element.get("number")
        elif name == "verse":
            if active:
                active = False
            if chapter == "1" and element.get("number") == "5":
                targets += 1
                active = True
    return targets, re.sub(r"[ \t\r\n]+", " ", "".join(fragments)).strip()


def _asv_checks(files: dict[str, bytes]) -> tuple[str | None, str | None]:
    expected = "And the light shineth in the darkness; and the darkness apprehended it not."
    targets, normalized = _asv_target(files)
    if targets == 0:
        content_error = "ASV_JOHN_1_5_NOT_FOUND"
    elif targets > 1:
        content_error = "ASV_JOHN_1_5_AMBIGUOUS"
    elif normalized != expected:
        content_error = "ASV_JOHN_1_5_CONTENT_MISMATCH"
    else:
        content_error = None
    rights_error = _rights_error(
        _text(files, "License.html"),
        ("public domain",),
        (
            r"\bnot\s+(?:in\s+the\s+)?public\s+domain\b",
            r"\ball\s+rights\s+reserved\b",
            r"\b(?:this\s+(?:edition|work)|american\s+standard\s+version)\b[^\r\n.]{0,96}\b(?:is|remains)\s+copyrighted\b",
        ),
        missing="ASV_RIGHTS_EVIDENCE_NOT_FOUND",
        contradicted="ASV_RIGHTS_EVIDENCE_CONTRADICTED",
    )
    return content_error, rights_error


def _abbott_smith_checks(files: dict[str, bytes]) -> tuple[str | None, str | None]:
    target = unicodedata.normalize("NFC", "καταλαμβάνω|G2638")
    entries = tuple(
        entry
        for entry in _xml_root(files, "abbott-smith.tei.xml").iter()
        if entry.tag.rsplit("}", 1)[-1] == "entry" and unicodedata.normalize("NFC", entry.get("n", "")) == target
    )
    if not entries:
        content_error = "ABBOTT_SMITH_ENTRY_NOT_FOUND"
    elif len(entries) > 1:
        content_error = "ABBOTT_SMITH_ENTRY_AMBIGUOUS"
    else:
        content_error = None
    rights_error = _rights_error(
        _text(files, "README.md"),
        ("public domain",),
        (
            r"\b(?:tei|lexicon)\b[^\r\n.]{0,96}\bnot\s+(?:in\s+the\s+)?public\s+domain\b",
            r"\ball\s+rights\s+reserved\b",
        ),
        missing="ABBOTT_SMITH_RIGHTS_EVIDENCE_NOT_FOUND",
        contradicted="ABBOTT_SMITH_RIGHTS_EVIDENCE_CONTRADICTED",
    )
    return content_error, rights_error


def _sfnt_error(data: bytes) -> str | None:
    if len(data) < 12:
        return "SOURCE_SERIF_FONT_TRUNCATED"
    if data[:4] != b"\x00\x01\x00\x00":
        return "SOURCE_SERIF_FONT_SIGNATURE_INVALID"
    count = int.from_bytes(data[4:6], "big")
    directory_end = 12 + count * 16
    if count < 4:
        return "SOURCE_SERIF_FONT_TABLE_COUNT_INVALID"
    if len(data) < directory_end:
        return "SOURCE_SERIF_FONT_DIRECTORY_TRUNCATED"
    records = tuple(data[offset : offset + 16] for offset in range(12, directory_end, 16))
    tags = {record[:4] for record in records}
    if not {b"cmap", b"head", b"maxp", b"name"} <= tags:
        return "SOURCE_SERIF_FONT_REQUIRED_TABLE_MISSING"
    bounds = ((int.from_bytes(record[8:12], "big"), int.from_bytes(record[12:16], "big")) for record in records)
    if not all(offset >= directory_end and length > 0 and offset + length <= len(data) for offset, length in bounds):
        return "SOURCE_SERIF_FONT_TABLE_BOUNDS_INVALID"
    return None


def _source_serif_checks(files: dict[str, bytes]) -> tuple[str | None, str | None]:
    content_error = next(
        (
            f"{reason}: {path}"
            for path in _SOURCE_SERIF_FONT_PATHS
            for reason in (_sfnt_error(files[path]),)
            if reason is not None
        ),
        None,
    )
    rights_error = _rights_error(
        _text(files, "LICENSE.md"),
        ("sil open font license", "version 1.1"),
        (r"\bnot\s+(?:licensed|distributed)\s+under\b[^\r\n.]{0,96}\bsil\s+open\s+font\s+license\b",),
        missing="SOURCE_SERIF_RIGHTS_EVIDENCE_NOT_FOUND",
        contradicted="SOURCE_SERIF_RIGHTS_EVIDENCE_CONTRADICTED",
    )
    return content_error, rights_error


_GITHUB_CHECKS: dict[str, Callable[[dict[str, bytes]], tuple[str | None, str | None]]] = {
    "SP01-SRC-001": _sblgnt_checks,
    "SP01-SRC-002": _morphgnt_checks,
    "SP01-SRC-003": _asv_checks,
    "SP01-SRC-005": _abbott_smith_checks,
    "SP01-SRC-006": _source_serif_checks,
}


def validate_github_content(source_id: str, files: dict[str, bytes]) -> None:
    content_error, rights_error = _GITHUB_CHECKS[source_id](files)
    if content_error is not None:
        raise ValueError(content_error)
    if rights_error is not None:
        raise ValueError(rights_error)
