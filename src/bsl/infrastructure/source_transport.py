from __future__ import annotations

import hashlib
import io
import json
import re
import stat
import zipfile
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import PurePosixPath, PureWindowsPath
from typing import cast
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from xml.etree import ElementTree

from bsl.contracts.source_admission import PlannedSource

MAX_COMPONENT_BYTES = 32 * 1024 * 1024
MAX_PACKAGE_BYTES = 128 * 1024 * 1024
MAX_ZIP_FILES = 1_000
MAX_EXPANDED_BYTES = 512 * 1024 * 1024
MAX_REDIRECTS = 5
WEB_PACKAGE_URL = "https://ebible.org/Scriptures/eng-web_usfm.zip"

_GITHUB_PATHS: dict[str, tuple[tuple[str, bool], ...]] = {
    "SP01-SRC-001": (("README.md", True), ("LICENSE", True), ("data/sblgnt/text/John.txt", False)),
    "SP01-SRC-002": (("README.md", True), ("64-Jn-morphgnt.txt", False)),
    "SP01-SRC-003": (("README.md", True), ("License.html", True), ("usx/43-JHN.usx", False)),
    "SP01-SRC-005": (("abbott-smith.tei.xml", False), ("README.md", True)),
    "SP01-SRC-006": (
        ("TTF/SourceSerif4-Regular.ttf", False),
        ("TTF/SourceSerif4-It.ttf", False),
        ("LICENSE.md", True),
    ),
}
_NESTED_ARCHIVES = {".zip", ".tar", ".tgz", ".gz", ".bz2", ".xz", ".7z", ".rar", ".jar", ".war", ".apk"}
_EXECUTABLE_EXTENSIONS = {".app", ".bat", ".bin", ".class", ".cmd", ".com", ".dll", ".dylib", ".exe", ".msi"} | {
    ".ps1",
    ".py",
    ".pyc",
    ".rb",
    ".sh",
}
_EXECUTABLE_MAGIC = (b"MZ", b"\x7fELF", b"#!", b"\0asm") + tuple(
    bytes.fromhex(value) for value in ("cafebabe", "feedface", "cefaedfe", "feedfacf", "cffaedfe")
)
_RIGHTS_CONFLICTS = ("license replaced", "license withdrawn", "permission revoked")


@dataclass(frozen=True)
class HttpResponse:
    requested_url: str
    final_url: str
    status: int
    headers: tuple[tuple[str, str], ...]
    body: bytes
    redirect_chain: tuple[str, ...] = ()


@dataclass(frozen=True)
class FetchedBytes:
    relative_path: str
    data: bytes
    rights_evidence: bool


@dataclass(frozen=True)
class ArchiveEntry:
    relative_path: str
    sha256: str
    byte_count: int


@dataclass(frozen=True)
class FetchBatch:
    resolved_revision: str
    package_sha256: str | None
    responses: tuple[HttpResponse, ...]
    files: tuple[FetchedBytes, ...]
    archive_inventory: tuple[ArchiveEntry, ...] = ()


Transport = Callable[[str, int], HttpResponse]


class SourceTransportError(ValueError):
    pass


class _BoundedRedirectHandler(HTTPRedirectHandler):
    def __init__(self) -> None:
        self.history: list[str] = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        if (
            len(self.history) >= MAX_REDIRECTS
            or not newurl.startswith("https://")
            or urlsplit(newurl).hostname != "ebible.org"
        ):
            raise ValueError("HTTP redirect chain is unsafe or exceeds the limit")
        self.history.append(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def https_transport(url: str, max_bytes: int) -> HttpResponse:
    if not url.startswith("https://"):
        raise ValueError("source transport requires HTTPS")
    redirects = _BoundedRedirectHandler()
    opener = build_opener(redirects)
    request = Request(url, headers={"User-Agent": "Biblical-Scholar-Lab/0.1", "Accept": "*/*"})
    try:
        with opener.open(request, timeout=30) as response:
            body = response.read(max_bytes + 1)
            result = HttpResponse(
                requested_url=url,
                final_url=response.url,
                status=response.status,
                headers=tuple(sorted((key.lower(), value) for key, value in response.headers.items())),
                body=body,
                redirect_chain=tuple(redirects.history),
            )
    except HTTPError as exc:
        return HttpResponse(
            requested_url=url,
            final_url=exc.url,
            status=exc.code,
            headers=tuple(sorted((key.lower(), value) for key, value in exc.headers.items())),
            body=exc.read(max_bytes + 1),
            redirect_chain=tuple(redirects.history),
        )
    except (URLError, TimeoutError, OSError) as exc:
        raise SourceTransportError("source HTTP request failed") from exc
    return result


def _checked_response(
    response: HttpResponse, url: str, max_bytes: int, *, allow_redirects: bool = False
) -> HttpResponse:
    if response.requested_url != url or not url.startswith("https://"):
        raise ValueError("transport response does not match the requested HTTPS URL")
    if response.status != 200:
        raise ValueError("source response status is not 200")
    if len(response.body) > max_bytes:
        raise ValueError("source response exceeds its byte limit")
    if len(response.redirect_chain) > (MAX_REDIRECTS if allow_redirects else 0):
        raise ValueError("source response has an unexpected redirect")
    if not response.final_url.startswith("https://"):
        raise ValueError("source response final URL is not HTTPS")
    if not allow_redirects and response.final_url != url:
        raise ValueError("immutable GitHub request redirected unexpectedly")
    if allow_redirects and any(
        urlsplit(value).hostname != "ebible.org" for value in (*response.redirect_chain, response.final_url)
    ):
        raise ValueError("WEB package redirected outside the approved host")
    return response


def _repository_parts(repository: str | None) -> tuple[str, str]:
    if repository is None:
        raise ValueError("GitHub source lacks a repository")
    parsed = urlsplit(repository)
    parts = tuple(part for part in parsed.path.split("/") if part)
    if (
        parsed != parsed._replace(path=f"/{'/'.join(parts)}")
        or parsed.scheme != "https"
        or parsed.hostname != "github.com"
    ):
        raise ValueError("GitHub repository identity is not exact HTTPS")
    if len(parts) != 2 or any(part in {".", ".."} for part in parts):
        raise ValueError("GitHub repository identity is invalid")
    return parts


def _raw_url(owner: str, repository: str, revision: str, path: str) -> str:
    encoded = "/".join(quote(part, safe="") for part in path.split("/"))
    return (
        f"https://raw.githubusercontent.com/{quote(owner, safe='')}/{quote(repository, safe='')}/{revision}/{encoded}"
    )


def _metadata_revision(
    source: PlannedSource, owner: str, repository: str, transport: Transport
) -> tuple[str, HttpResponse]:
    reference = source.tag or source.revision
    url = (
        f"https://api.github.com/repos/{quote(owner, safe='')}/{quote(repository, safe='')}"
        f"/commits/{quote(reference, safe='')}"
    )
    response = _checked_response(transport(url, MAX_COMPONENT_BYTES), url, MAX_COMPONENT_BYTES)
    try:
        raw_payload = json.loads(response.body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("GitHub revision metadata is invalid JSON") from None
    if not isinstance(raw_payload, dict):
        raise ValueError("GitHub revision metadata is not an object")
    payload = cast(dict[str, object], raw_payload)
    if payload.get("sha") != source.revision:
        raise ValueError("GitHub tag or revision does not resolve to the approved commit")
    return source.revision, response


def _text(files: dict[str, bytes], path: str) -> str:
    try:
        return files[path].decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError(f"approved text component is not UTF-8: {path}") from None


def _rights_claim(
    text: str,
    required: tuple[str, ...],
    forbidden: tuple[str, ...],
    conflict_patterns: tuple[str, ...] = (),
) -> bool:
    lowered = text.lower()
    return (
        all(value in lowered for value in required)
        and not any(value in lowered for value in (*forbidden, *_RIGHTS_CONFLICTS))
        and not any(re.search(pattern, lowered) for pattern in conflict_patterns)
    )


def _xml_root(files: dict[str, bytes], path: str) -> ElementTree.Element:
    try:
        return ElementTree.fromstring(_text(files, path))
    except ElementTree.ParseError:
        raise ValueError(f"approved XML component is malformed: {path}") from None


def _sblgnt_checks(files: dict[str, bytes]) -> tuple[bool, bool]:
    expected = "καὶ τὸ φῶς ἐν τῇ σκοτίᾳ φαίνει, καὶ ἡ σκοτία αὐτὸ οὐ κατέλαβεν."
    prefix = "John 1:5\t"
    lines = tuple(
        line.rstrip() for line in _text(files, "data/sblgnt/text/John.txt").splitlines() if line.startswith(prefix)
    )
    content = lines == (f"{prefix}{expected}",)
    rights = _rights_claim(
        _text(files, "LICENSE"),
        ("attribution 4.0 international",),
        (
            "not attribution 4.0 international",
            "not licensed under attribution 4.0 international",
            "attribution 4.0 international does not apply",
        ),
        (r"\bnot\s+(?:licensed|distributed)\s+under\b[^\r\n.]{0,96}\battribution\s+4\.0\s+international\b",),
    )
    return content, rights


def _morphgnt_checks(files: dict[str, bytes]) -> tuple[bool, bool]:
    rows = tuple(line.split() for line in _text(files, "64-Jn-morphgnt.txt").splitlines())
    target = ("V-", "3AAI-S--", "κατέλαβεν.", "κατέλαβεν", "κατέλαβε(ν)", "καταλαμβάνω")
    verse_rows = tuple(row for row in rows if row and row[0] == "040105")
    content = sum(tuple(row[1:]) == target for row in verse_rows) == 1
    rights = _rights_claim(
        _text(files, "README.md"),
        ("cc-by-sa license", "/licenses/by-sa/3.0/"),
        (
            "not the cc-by-sa license",
            "not licensed under cc-by-sa",
            "cc-by-sa license does not apply",
            "license unknown",
        ),
        (r"\bnot\s+(?:licensed|distributed)\s+under\b[^\r\n.]{0,96}\bcc-by-sa\s+license\b",),
    )
    return content, rights


def _xml_events(element: ElementTree.Element) -> Iterator[ElementTree.Element | str]:
    yield element
    if element.tag.rsplit("}", 1)[-1] != "note" and element.text:
        yield element.text
    if element.tag.rsplit("}", 1)[-1] != "note":
        for child in element:
            yield from _xml_events(child)
            if child.tail:
                yield child.tail


def _asv_checks(files: dict[str, bytes]) -> tuple[bool, bool]:
    expected = "And the light shineth in the darkness; and the darkness apprehended it not."
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
    normalized = re.sub(r"[ \t\r\n]+", " ", "".join(fragments)).strip()
    content = targets == 1 and normalized == expected
    rights = _rights_claim(
        _text(files, "License.html"), ("public domain",), ("not public domain", "copyrighted", "all rights reserved")
    )
    return content, rights


def _abbott_smith_checks(files: dict[str, bytes]) -> tuple[bool, bool]:
    entries = 0
    for entry in _xml_root(files, "abbott-smith.tei.xml").iter():
        if entry.tag.rsplit("}", 1)[-1] == "entry" and any(
            node.tag.rsplit("}", 1)[-1] == "orth" and "".join(node.itertext()).strip() == "καταλαμβάνω"
            for node in entry.iter()
        ):
            entries += 1
    rights = _rights_claim(
        _text(files, "README.md"),
        ("public domain",),
        ("tei is not public domain", "lexicon is not public domain", "all rights reserved"),
    )
    return entries == 1, rights


def _valid_sfnt(data: bytes) -> bool:
    if len(data) < 12 or data[:4] != b"\x00\x01\x00\x00":
        return False
    count = int.from_bytes(data[4:6], "big")
    directory_end = 12 + count * 16
    if count < 4 or len(data) < directory_end:
        return False
    records = tuple(data[offset : offset + 16] for offset in range(12, directory_end, 16))
    tags = {record[:4] for record in records}
    bounds = ((int.from_bytes(record[8:12], "big"), int.from_bytes(record[12:16], "big")) for record in records)
    return {b"cmap", b"head", b"maxp", b"name"} <= tags and all(
        offset >= directory_end and length > 0 and offset + length <= len(data) for offset, length in bounds
    )


def _source_serif_checks(files: dict[str, bytes]) -> tuple[bool, bool]:
    content = all(_valid_sfnt(files[path]) for path, rights in _GITHUB_PATHS["SP01-SRC-006"] if not rights)
    rights = _rights_claim(
        _text(files, "LICENSE.md"),
        ("sil open font license", "version 1.1"),
        (
            "not licensed under the sil open font license",
            "sil open font license does not apply",
            "sil open font license grant is withdrawn",
        ),
        (
            r"\bnot\s+(?:licensed|distributed)\s+under\b[^\r\n.]{0,96}\bsil\s+open\s+font\s+license\b",
            r"\b(?:license(?:\s+grant)?|grant)\s+(?:has\s+been|was|is)\s+(?:replaced|withdrawn)\b",
        ),
    )
    return content, rights


_GITHUB_CHECKS: dict[str, Callable[[dict[str, bytes]], tuple[bool, bool]]] = {
    "SP01-SRC-001": _sblgnt_checks,
    "SP01-SRC-002": _morphgnt_checks,
    "SP01-SRC-003": _asv_checks,
    "SP01-SRC-005": _abbott_smith_checks,
    "SP01-SRC-006": _source_serif_checks,
}


def _validate_github_content(source_id: str, files: dict[str, bytes]) -> None:
    valid, rights = _GITHUB_CHECKS[source_id](files)
    if not valid:
        raise ValueError("source-specific content sanity check failed")
    if not rights:
        raise ValueError("required rights evidence is missing or changed")


def fetch_github(source: PlannedSource, transport: Transport) -> FetchBatch:
    paths = _GITHUB_PATHS.get(source.source_id)
    if paths is None or "manualgreeklexic00abborich.pdf" in {path for path, _rights in paths}:
        raise ValueError("source is not an approved GitHub component set")
    owner, repository = _repository_parts(source.repository)
    resolved, metadata = _metadata_revision(source, owner, repository, transport)
    responses: list[HttpResponse] = [metadata]
    fetched: list[FetchedBytes] = []
    for path, rights in paths:
        url = _raw_url(owner, repository, source.revision, path)
        response = _checked_response(transport(url, MAX_COMPONENT_BYTES), url, MAX_COMPONENT_BYTES)
        responses.append(response)
        fetched.append(FetchedBytes(path, response.body, rights))
    _validate_github_content(source.source_id, {item.relative_path: item.data for item in fetched})
    return FetchBatch(resolved, None, tuple(responses), tuple(fetched))


def _validate_zip_path(name: str) -> PurePosixPath:
    posix, windows = PurePosixPath(name), PureWindowsPath(name)
    if not name or name.startswith(("/", "\\")) or "\\" in name or windows.drive:
        raise ValueError("ZIP contains an absolute or non-POSIX path")
    if posix.as_posix() != name or any(part in {"", ".", ".."} for part in posix.parts):
        raise ValueError("ZIP contains path traversal or a nondeterministic path")
    return posix


def _validate_zip_type(info: zipfile.ZipInfo, path: PurePosixPath) -> None:
    mode = info.external_attr >> 16
    file_type = stat.S_IFMT(mode)
    if stat.S_ISLNK(mode):
        raise ValueError("ZIP contains a symlink")
    if file_type and ((info.is_dir() and not stat.S_ISDIR(mode)) or (not info.is_dir() and not stat.S_ISREG(mode))):
        raise ValueError("ZIP contains a special file type")
    if info.flag_bits & 0x1:
        raise ValueError("ZIP contains an encrypted entry")
    if not info.is_dir() and path.suffix.lower() in _NESTED_ARCHIVES:
        raise ValueError("ZIP contains a nested archive")
    if not info.is_dir() and path.suffix.lower() in _EXECUTABLE_EXTENSIONS:
        raise ValueError("ZIP contains executable content")


def _safe_zip_info(info: zipfile.ZipInfo) -> None:
    name = info.filename[:-1] if info.is_dir() and info.filename.endswith("/") else info.filename
    _validate_zip_type(info, _validate_zip_path(name))


def _zip_inventory(package: bytes) -> tuple[zipfile.ZipFile, tuple[zipfile.ZipInfo, ...]]:
    try:
        archive = zipfile.ZipFile(io.BytesIO(package))
        all_infos = tuple(archive.infolist())
    except zipfile.BadZipFile:
        raise ValueError("WEB package is not a valid ZIP") from None
    if not all_infos or len(all_infos) > MAX_ZIP_FILES:
        archive.close()
        raise ValueError("WEB package file-count limit failed")
    for info in all_infos:
        _safe_zip_info(info)
    infos = tuple(info for info in all_infos if not info.is_dir())
    if not infos:
        archive.close()
        raise ValueError("WEB package contains no files")
    if sum(info.file_size for info in infos) > MAX_EXPANDED_BYTES:
        archive.close()
        raise ValueError("WEB package expanded-byte limit failed")
    try:
        for info in infos:
            with archive.open(info) as stream:
                prefix = stream.read(4)
            if prefix.startswith(_EXECUTABLE_MAGIC):
                archive.close()
                raise ValueError("ZIP contains executable content")
    except (RuntimeError, NotImplementedError, zipfile.BadZipFile, OSError, EOFError):
        archive.close()
        raise ValueError("WEB ZIP entry cannot be read") from None
    return archive, infos


def _john_entries(infos: tuple[zipfile.ZipInfo, ...]) -> tuple[zipfile.ZipInfo, ...]:
    return tuple(
        info
        for info in infos
        if info.filename.lower().endswith((".usfm", ".sfm"))
        and any(token in PurePosixPath(info.filename).name.lower() for token in ("jhn", "john"))
    )


def _rights_entries(infos: tuple[zipfile.ZipInfo, ...]) -> tuple[zipfile.ZipInfo, ...]:
    tokens = ("copyright", "license", "metadata", "readme")
    return tuple(info for info in infos if any(token in PurePosixPath(info.filename).name.lower() for token in tokens))


_USFM_INLINE_SPAN = re.compile(r"\\([fx])(\*|\s)")
_USFM_CHAPTER = re.compile(r"^\\c\s+(\S+)\s*$")
_USFM_VERSE = re.compile(r"^\\v\s+(\S+)(?:\s+(.*))?$")


def _without_usfm_notes(text: str) -> str:
    result: list[str] = []
    active: str | None = None
    retained_from = 0
    for marker in _USFM_INLINE_SPAN.finditer(text):
        name, suffix = marker.groups()
        if active is None and suffix != "*":
            result.append(text[retained_from : marker.start()])
            active = name
        elif active is None:
            raise ValueError("WEB verse has an unmatched inline note terminator")
        elif active == name and suffix == "*":
            active = None
            retained_from = marker.end()
    if active is not None:
        raise ValueError("WEB verse has an unbounded inline note")
    result.append(text[retained_from:])
    return "".join(result)


def _web_verse(text: str) -> str | None:
    chapter: str | None = None
    active = False
    targets = 0
    fragments: list[str] = []
    for line in text.splitlines():
        if match := _USFM_CHAPTER.fullmatch(line.strip()):
            active = False
            chapter = match.group(1)
            continue
        if match := _USFM_VERSE.fullmatch(line.strip()):
            active = False
            if chapter == "1" and match.group(1) == "5":
                active = True
                targets += 1
                fragments.append(match.group(2) or "")
            continue
        if active:
            fragments.append(line)
    if targets != 1:
        return None
    return " ".join(_without_usfm_notes("\n".join(fragments)).split())


def _validate_web_evidence(john_data: bytes, evidence: tuple[FetchedBytes, ...]) -> None:
    text = john_data.decode("utf-8").replace("’", "'")
    evidence_text = b"\n".join(item.data for item in evidence).decode("utf-8", errors="replace").lower()
    expected = "The light shines in the darkness, and the darkness hasn't overcome it."
    identities = tuple(line.strip() for line in text.splitlines() if line.startswith("\\id "))
    if identities != ("\\id JHN World English Bible",) or _web_verse(text) != expected:
        raise ValueError("WEB John 1:5 content sanity check failed")
    translation_names = ("world english bible", "eng-web")
    rights = _rights_claim(
        evidence_text, ("public domain",), ("not public domain", "copyrighted", "all rights reserved")
    )
    if not rights or not any(value in evidence_text for value in translation_names):
        raise ValueError("WEB translation identity or public-domain evidence failed")


def _web_components(package: bytes) -> tuple[tuple[FetchedBytes, ...], tuple[ArchiveEntry, ...]]:
    archive, infos = _zip_inventory(package)
    try:
        john = _john_entries(infos)
        rights = _rights_entries(infos)
        if len(john) != 1 or not rights:
            raise ValueError("WEB package lacks one John component or rights evidence")
        john_data = archive.read(john[0])
        evidence = tuple(FetchedBytes(info.filename, archive.read(info), True) for info in rights)
        inventory = tuple(
            ArchiveEntry(info.filename, hashlib.sha256(data).hexdigest(), len(data))
            for info in infos
            for data in (archive.read(info),)
        )
    except (RuntimeError, NotImplementedError, zipfile.BadZipFile, OSError, EOFError):
        raise ValueError("WEB ZIP entry cannot be read") from None
    finally:
        archive.close()
    _validate_web_evidence(john_data, evidence)
    package_object = FetchedBytes("eng-web_usfm.zip", package, False)
    files = (package_object, FetchedBytes(john[0].filename, john_data, False), *evidence)
    return files, inventory


def fetch_web(source: PlannedSource, transport: Transport) -> FetchBatch:
    if source.package != WEB_PACKAGE_URL or source.revision != "ACQUISITION_TIMESTAMP_PLUS_SHA256_REQUIRED":
        raise ValueError("WEB package identity differs from SOURCE-PLAN-01")
    response = _checked_response(
        transport(WEB_PACKAGE_URL, MAX_PACKAGE_BYTES), WEB_PACKAGE_URL, MAX_PACKAGE_BYTES, allow_redirects=True
    )
    files, inventory = _web_components(response.body)
    return FetchBatch(
        source.revision,
        hashlib.sha256(response.body).hexdigest(),
        (response,),
        files,
        inventory,
    )


def fetch_source(source: PlannedSource, transport: Transport = https_transport) -> FetchBatch:
    if source.source_id == "SP01-SRC-004":
        return fetch_web(source, transport)
    return fetch_github(source, transport)
