from __future__ import annotations

import hashlib
import json
import os
import platform
import plistlib
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from jsonschema import Draft202012Validator

from bsl.contracts.archive import ArchiveRootMarker
from bsl.contracts.source_admission import AdmissionDecision, FetchReceipt, SourceSnapshot

ROOT = Path(__file__).resolve().parents[3]
MANIFEST_SHA = "e3ff1619cf1621fcf046eae9ad9198455cf54a306f6573353e43e153e3e1277a"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate decoded JSON member")
        result[key] = value
    return result


def decode(data: bytes) -> Any:
    value = json.loads(data.decode("utf-8"), object_pairs_hook=_pairs)
    json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")
    return value


class UnicodeHelper:
    """Own one bounded compiler process and executable for this compilation/session."""

    def __init__(self) -> None:
        self.directory = TemporaryDirectory(prefix="j13-unicode-")
        self.executable = Path(self.directory.name) / "profile"
        source = ROOT / "tools/j13_unicode_profile.swift"
        try:
            self.runtime = subprocess.run(
                ["swiftc", "--version"], capture_output=True, check=True, timeout=30
            ).stdout.decode()
            self.os_identity = platform.platform()
            self.source_sha256 = sha(source.read_bytes())
            subprocess.run(
                ["swiftc", str(source), "-o", str(self.executable)], capture_output=True, check=True, timeout=120
            )
        except BaseException:
            self.close()
            raise

    def close(self) -> None:
        self.directory.cleanup()

    def check(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        request = json.dumps({"items": items}, ensure_ascii=False, allow_nan=False).encode()
        raw = subprocess.run([str(self.executable)], input=request, capture_output=True, check=True, timeout=30).stdout
        try:
            results: list[dict[str, Any]] = decode(raw)
        except (ValueError, UnicodeError) as error:
            raise RuntimeError("malformed Unicode helper JSON") from error
        if type(results) is not list or len(results) != len(items):
            raise RuntimeError("incomplete Unicode helper response")
        for item, result in zip(items, results, strict=True):
            if type(result) is not dict or set(result) != {"plainTextError", "scalarCount", "endpointErrors"}:
                raise RuntimeError("malformed Unicode helper response")
            errors: list[str | None] = result["endpointErrors"]
            invalid = (
                type(result["scalarCount"]) is not int or result["scalarCount"] != len(item["text"]),
                result["plainTextError"] not in (None, "proseViolation", "markupViolation"),
                type(errors) is not list or len(errors) != len(item["endpoints"]),
                type(errors) is list
                and any(e not in (None, "invalidUTF16Range", "invalidStringBoundary", "graphemeSplit") for e in errors),
            )
            if any(invalid):
                raise RuntimeError("invalid Unicode helper response values")
        return results


def read_regular(root: Path, relative: str, immutable: bool = False) -> bytes:
    path = root / relative
    if path.resolve() != path.absolute() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("unsafe authority path")
    with path.open("rb") as stream:
        mode = os.fstat(stream.fileno()).st_mode
        if not stat.S_ISREG(mode) or (immutable and stat.S_IMODE(mode) != 0o444):
            raise ValueError("authority file is nonregular or mutable")
        return stream.read()


def inventory(root: Path) -> str:
    entries: list[tuple[Any, ...]] = []
    for folder, directories, files in os.walk(root, followlinks=False):
        for name in sorted(directories + files):
            path = Path(folder) / name
            info = path.lstat()
            entries.append((str(path.relative_to(root)), info.st_mode, info.st_size, info.st_mtime_ns, info.st_ino))
    return sha(json.dumps(sorted(entries)).encode())


def load_j13_upstream_authority() -> dict[str, Any]:
    raw = read_regular(ROOT, "fixtures/J13-LAB-01/upstream-authority.json")
    if sha(raw) != MANIFEST_SHA:
        raise ValueError("upstream authority manifest drift")
    manifest = decode(raw)
    files: dict[str, Any] = {}
    for entry in manifest["files"]:
        raw = read_regular(ROOT, entry["fixture_path"])
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        if (blob, sha(raw), len(raw)) != (entry["git_blob"], entry["sha256"], entry["byte_count"]):
            raise ValueError("upstream original-byte drift")
        files[Path(entry["fixture_path"]).name] = decode(raw) if entry["source_path"].endswith(".json") else raw
    notes_schema = files["reader-annotation-projection-v1.schema.json"]
    package_schema = files["translation-annotation-package-v1.schema.json"]
    for schema in (notes_schema, package_schema):
        Draft202012Validator.check_schema(schema)
    records = tuple(v for k, v in files.items() if k.startswith("tan-"))
    for record in records:
        validator: Any = Draft202012Validator(notes_schema)
        validator.validate(record)
    book = files["engwebp-2020-2242945d71ca925b.43-john.json"]
    chapter = next(c for c in book["chapters"] if c["chapterNumber"] == 13)
    transport = files["engwebp-2020-2242945d71ca925b.manifest.json"]
    mapping = {
        "scripture_package_id": "packageID",
        "scripture_package_content_sha256": "contentSHA256",
        "translation_id": "translationID",
        "translation_version": "translationVersion",
        "canon_id": "canonID",
        "versification_id": "versificationID",
    }
    if any(manifest["target"][key] != transport[value] for key, value in mapping.items()):
        raise ValueError("target Scripture identity drift")
    return {"manifest": manifest, "records": records, "schema": package_schema, "chapter": chapter}


@dataclass(frozen=True)
class SourceAuthority:
    source_id: str
    snapshot: SourceSnapshot | None
    files: tuple[tuple[str, bytes], ...]
    gap: str | None = None


def _source(root: Path, source_id: str) -> SourceAuthority:
    raw = read_regular(root, f"snapshots/source/{source_id}.json", True)
    decode(raw)
    snapshot = SourceSnapshot.model_validate_json(raw)
    fetch_bytes = read_regular(root, snapshot.fetch_receipt_relative_path, True)
    decision_bytes = read_regular(root, snapshot.admission_decision_relative_path, True)
    decode(fetch_bytes)
    decode(decision_bytes)
    fetch = FetchReceipt.model_validate_json(fetch_bytes)
    decision = AdmissionDecision.model_validate_json(decision_bytes)
    if (sha(fetch_bytes), sha(decision_bytes)) != (snapshot.fetch_receipt_sha256, snapshot.admission_decision_sha256):
        raise ValueError("admission receipt hash drift")
    if not (
        source_id == snapshot.source_id == fetch.source_id == decision.source_id
        and snapshot.admission_attempt_id == fetch.attempt_id == decision.attempt_id
        and decision.disposition == "ADMITTED"
        and decision.fetch_receipt_sha256 == sha(fetch_bytes)
        and snapshot.source_spec == fetch.source_spec
        and snapshot.objects == fetch.objects
        and snapshot.archive_inventory == fetch.archive_inventory
        and snapshot.acquired_at == fetch.generated_at
        and snapshot.package_sha256 == fetch.package_sha256
        and decision.admitted_object_sha256 == tuple(dict.fromkeys(o.sha256 for o in snapshot.objects))
        and snapshot.retrieval_urls == tuple(e.final_url for e in fetch.exchanges)
    ):
        raise ValueError("source admission binding drift")
    files: list[tuple[str, bytes]] = []
    for item in snapshot.objects:
        raw = read_regular(root, f"objects/sha256/{item.sha256[:2]}/{item.sha256}", True)
        if (sha(raw), len(raw)) != (item.sha256, item.byte_count):
            raise ValueError("admitted component drift")
        files.append((item.relative_path, raw))
    return SourceAuthority(source_id, snapshot, tuple(files))


def load_j13_source_authority(root: Path, *, synthetic: bool = False) -> tuple[SourceAuthority, ...]:
    if any(name in os.environ for name in ("BSL_DATABASE_URL", "BSL_TEST_DATABASE_URL")):
        raise ValueError("database configuration is prohibited")
    if root.resolve() != root.absolute():
        raise ValueError("archive root is a symlink")
    if not synthetic and root != Path("/Volumes/BSL-Archive/BiblicalScholarLab"):
        raise ValueError("not the owner canonical archive")
    try:
        marker_bytes = read_regular(root, ".bsl-archive-root.json", True)
    except FileNotFoundError:
        return tuple(SourceAuthority(f"SP01-SRC-00{i}", None, (), "owner archive unavailable") for i in range(1, 6))
    decode(marker_bytes)
    marker = ArchiveRootMarker.model_validate_json(marker_bytes)
    if not synthetic:
        volume = plistlib.loads(
            subprocess.run(
                ["diskutil", "info", "-plist", str(root.parent)], capture_output=True, check=True, timeout=30
            ).stdout
        )
        if (volume["VolumeUUID"], str(marker.archive_id)) != (
            marker.stable_volume_identifier,
            "01a02576-0e1b-78f0-b059-46cd5407f8d6",
        ):
            raise ValueError("owner archive physical identity differs")
    sources: list[SourceAuthority] = []
    for index in range(1, 6):
        source_id = f"SP01-SRC-00{index}"
        try:
            sources.append(
                _source(root, source_id)
                if index != 3
                else SourceAuthority(source_id, None, (), "unused comparison; no component read")
            )
        except FileNotFoundError:
            sources.append(SourceAuthority(source_id, None, (), "required admitted authority file unavailable"))
    return tuple(sources)
