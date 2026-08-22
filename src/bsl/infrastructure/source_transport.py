from __future__ import annotations

import hashlib
import io
import json
import re
import stat
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import PurePosixPath, PureWindowsPath
from typing import cast
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from bsl.contracts.source_admission import PlannedSource
from bsl.infrastructure.source_validation import (
    _rights_error,  # pyright: ignore[reportPrivateUsage]
    validate_github_content,
)

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
_TEXT_LIKE_SUFFIXES = {
    ".asc",
    ".htm",
    ".html",
    ".json",
    ".markdown",
    ".md",
    ".sfm",
    ".txt",
    ".usfm",
    ".xml",
    ".yaml",
    ".yml",
}


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
        if len(self.history) >= MAX_REDIRECTS:
            raise ValueError("HTTP redirect chain exceeds the limit")
        if not newurl.startswith("https://"):
            raise ValueError("HTTP redirect target is not HTTPS")
        if urlsplit(newurl).hostname != "ebible.org":
            raise ValueError("WEB package redirected outside the approved host")
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


def _validate_response_redirects(response: HttpResponse, url: str, allow_redirects: bool) -> None:
    if len(response.redirect_chain) > (MAX_REDIRECTS if allow_redirects else 0):
        raise ValueError("source response has an unexpected redirect")
    if not response.final_url.startswith("https://"):
        raise ValueError("source response final URL is not HTTPS")
    if not allow_redirects and response.final_url != url:
        raise ValueError("immutable GitHub request redirected unexpectedly")
    if allow_redirects and any(urlsplit(value).hostname != "ebible.org" for value in response.redirect_chain):
        raise ValueError("WEB redirect chain contains an unapproved host")
    if allow_redirects and urlsplit(response.final_url).hostname != "ebible.org":
        raise ValueError("WEB package final URL is outside the approved host")


def _checked_response(
    response: HttpResponse, url: str, max_bytes: int, *, allow_redirects: bool = False
) -> HttpResponse:
    if not url.startswith("https://"):
        raise ValueError("source request URL is not HTTPS")
    if response.requested_url != url:
        raise ValueError("transport response does not match the requested HTTPS URL")
    if response.status != 200:
        raise ValueError("source response status is not 200")
    if len(response.body) > max_bytes:
        raise ValueError("source response exceeds its byte limit")
    _validate_response_redirects(response, url, allow_redirects)
    return response


def _repository_parts(repository: str | None) -> tuple[str, str]:
    if repository is None:
        raise ValueError("GitHub source lacks a repository")
    parsed = urlsplit(repository)
    parts = tuple(part for part in parsed.path.split("/") if part)
    if parsed.scheme != "https":
        raise ValueError("GitHub repository identity is not HTTPS")
    if parsed.hostname != "github.com":
        raise ValueError("GitHub repository identity uses an unapproved host")
    if parsed != parsed._replace(path=f"/{'/'.join(parts)}"):
        raise ValueError("GitHub repository path is not canonical")
    if len(parts) != 2:
        raise ValueError("GitHub repository identity must contain owner and repository")
    if any(part in {".", ".."} for part in parts):
        raise ValueError("GitHub repository identity contains an unsafe path component")
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


def fetch_github(source: PlannedSource, transport: Transport) -> FetchBatch:
    paths = _GITHUB_PATHS.get(source.source_id)
    if paths is None:
        raise ValueError("source is not an approved GitHub component set")
    if "manualgreeklexic00abborich.pdf" in {path for path, _rights in paths}:
        raise ValueError("prohibited Abbott-Smith PDF is present in the acquisition component set")
    owner, repository = _repository_parts(source.repository)
    resolved, metadata = _metadata_revision(source, owner, repository, transport)
    responses: list[HttpResponse] = [metadata]
    fetched: list[FetchedBytes] = []
    for path, rights in paths:
        url = _raw_url(owner, repository, source.revision, path)
        response = _checked_response(transport(url, MAX_COMPONENT_BYTES), url, MAX_COMPONENT_BYTES)
        responses.append(response)
        fetched.append(FetchedBytes(path, response.body, rights))
    validate_github_content(source.source_id, {item.relative_path: item.data for item in fetched})
    return FetchBatch(resolved, None, tuple(responses), tuple(fetched))


def _validate_zip_path(name: str) -> PurePosixPath:
    posix, windows = PurePosixPath(name), PureWindowsPath(name)
    if not name:
        raise ValueError("ZIP contains an empty path")
    if name.startswith(("/", "\\")) or windows.drive:
        raise ValueError("ZIP contains an absolute path")
    if "\\" in name:
        raise ValueError("ZIP contains a non-POSIX path")
    if posix.as_posix() != name:
        raise ValueError("ZIP contains a nondeterministic path")
    if any(part in {"", ".", ".."} for part in posix.parts):
        raise ValueError("ZIP contains path traversal")
    return posix


def _validate_zip_type(info: zipfile.ZipInfo, path: PurePosixPath) -> None:
    mode = info.external_attr >> 16
    file_type = stat.S_IFMT(mode)
    if stat.S_ISLNK(mode):
        raise ValueError("ZIP contains a symlink")
    if file_type and info.is_dir() and not stat.S_ISDIR(mode):
        raise ValueError("ZIP directory entry has a non-directory Unix file type")
    if file_type and not info.is_dir() and not stat.S_ISREG(mode):
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
    if not all_infos:
        archive.close()
        raise ValueError("WEB package contains no ZIP members")
    if len(all_infos) > MAX_ZIP_FILES:
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


_USFM_INLINE_SPAN = re.compile(r"\\([fx])(\*|\s)")
_USFM_CHAPTER = re.compile(r"^\\c\s+(\S+)\s*$")
_USFM_VERSE = re.compile(r"^\\v\s+(\S+)(?:\s+(.*))?$")
_USFM_ID = re.compile(r"^\\id\s+(\S+)(?:\s+.*)?$")
_USFM_WORD_SPAN = re.compile(r"\\w\s+([^|\\\r\n]+)(?:\|[^\\\r\n]*)?\\w\*")
_USFM_PARAGRAPH = re.compile(r"\\p(?:\s|$)")


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


def _web_verse(text: str) -> tuple[int, str]:
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
    normalized = ""
    if targets == 1:
        verse = _without_usfm_notes("\n".join(fragments))
        verse = _USFM_WORD_SPAN.sub(lambda match: match.group(1), verse)
        normalized = " ".join(_USFM_PARAGRAPH.sub(" ", verse).split())
    return targets, normalized


def _usfm_ids(text: str) -> tuple[str, ...]:
    return tuple(match.group(1) for line in text.splitlines() if (match := _USFM_ID.fullmatch(line.strip())))


def _web_text_entries(
    archive: zipfile.ZipFile, infos: tuple[zipfile.ZipInfo, ...]
) -> tuple[tuple[zipfile.ZipInfo, bytes, str], ...]:
    entries: list[tuple[zipfile.ZipInfo, bytes, str]] = []
    for info in infos:
        if (
            PurePosixPath(info.filename).suffix.lower() not in _TEXT_LIKE_SUFFIXES
            or info.file_size > MAX_COMPONENT_BYTES
        ):
            continue
        data = archive.read(info)
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        entries.append((info, data, text))
    return tuple(entries)


def _validate_web_evidence(john_data: bytes, evidence: tuple[FetchedBytes, ...]) -> None:
    try:
        text = john_data.decode("utf-8").replace("’", "'")
    except UnicodeDecodeError:
        raise ValueError("WEB_JOHN_COMPONENT_NOT_UTF8") from None
    evidence_text = b"\n".join(item.data for item in evidence).decode("utf-8", errors="replace").lower()
    expected = "The light shines in the darkness, and the darkness hasn't overcome it."
    identities = _usfm_ids(text)
    if not identities:
        raise ValueError("WEB_JOHN_IDENTITY_NOT_FOUND")
    if identities != ("JHN",):
        raise ValueError("WEB_JOHN_IDENTITY_AMBIGUOUS_OR_CHANGED")
    targets, verse = _web_verse(text)
    if targets == 0:
        raise ValueError("WEB_JOHN_1_5_NOT_FOUND")
    if targets > 1:
        raise ValueError("WEB_JOHN_1_5_AMBIGUOUS")
    if verse != expected:
        raise ValueError("WEB_JOHN_1_5_CONTENT_MISMATCH")
    if not any(value in evidence_text for value in ("world english bible", "eng-web")):
        raise ValueError("WEB_TRANSLATION_IDENTITY_NOT_FOUND")
    rights_error = _rights_error(
        evidence_text,
        ("public domain",),
        (
            r"\bnot\s+(?:in\s+the\s+)?public\s+domain\b",
            r"\ball\s+rights\s+reserved\b",
            r"\b(?:world\s+english\s+bible|this\s+(?:work|text|translation))\b[^\r\n.]{0,96}\b(?:is|remains)\s+copyrighted\b",
        ),
        missing="WEB_RIGHTS_EVIDENCE_NOT_FOUND",
        contradicted="WEB_RIGHTS_EVIDENCE_CONTRADICTED",
    )
    if rights_error is not None:
        raise ValueError(rights_error)


def _web_components(package: bytes) -> tuple[tuple[FetchedBytes, ...], tuple[ArchiveEntry, ...]]:
    archive, infos = _zip_inventory(package)
    try:
        text_entries = _web_text_entries(archive, infos)
        john = [
            entry
            for entry in text_entries
            if PurePosixPath(entry[0].filename).suffix.lower() in {".sfm", ".usfm"} and _usfm_ids(entry[2]) == ("JHN",)
        ]
        if not john:
            raise ValueError("WEB_JOHN_COMPONENT_NOT_FOUND")
        if len(john) > 1:
            raise ValueError("WEB_JOHN_COMPONENT_AMBIGUOUS")
        identity = tuple(
            entry
            for entry in text_entries
            if any(value in entry[2].lower() for value in ("world english bible", "eng-web"))
        )
        if not identity:
            raise ValueError("WEB_TRANSLATION_IDENTITY_NOT_FOUND")
        rights = tuple(entry for entry in identity if "public domain" in entry[2].lower())
        if not rights:
            raise ValueError("WEB_RIGHTS_EVIDENCE_NOT_FOUND")
        john_info, john_data, _john_text = john[0]
        evidence = tuple(FetchedBytes(info.filename, data, True) for info, data, _text in rights)
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
    files = (package_object, FetchedBytes(john_info.filename, john_data, False), *evidence)
    return files, inventory


def fetch_web(source: PlannedSource, transport: Transport) -> FetchBatch:
    if source.package != WEB_PACKAGE_URL:
        raise ValueError("WEB package URL differs from SOURCE-PLAN-01")
    if source.revision != "ACQUISITION_TIMESTAMP_PLUS_SHA256_REQUIRED":
        raise ValueError("WEB revision policy differs from SOURCE-PLAN-01")
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
