"""Finalize only the activated private local release; no network or database path."""

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from bsl.application.j13_private_pilot_release import build_outputs, producer_files, validate_context
from bsl.contracts.translation_annotation_compilation_release import PACKAGE
from bsl.infrastructure.j13_authority import ROOT, UnicodeHelper, decode, inventory, read_regular, sha
from tools.j13_lab_01_compile_candidate import (
    _output_parent,
    _remove_owned,
    _remove_owned_directory,
    _verify_outputs,
    _write_outputs,
)

PRIVATE_ROOT = ROOT / ".local/releases/J13-LAB-02"


def private_path(path: Path, archive: Path) -> Path:
    absolute = path.absolute()
    if (
        absolute.resolve() != absolute
        or not absolute.is_relative_to(PRIVATE_ROOT)
        or absolute == PRIVATE_ROOT
        or absolute.is_relative_to(archive)
    ):
        raise ValueError("output must be beneath the private release root, outside archive, without symlinks")
    subprocess.run(["git", "check-ignore", "-q", str(PRIVATE_ROOT) + "/"], cwd=ROOT, check=True)
    return absolute


def check_frozen_release(outputs: dict[str, bytes]) -> None:
    manifest = ROOT / "artifacts/J13-LAB-02/release-manifest.json"
    if manifest.exists():
        existing = decode(read_regular(ROOT, str(manifest.relative_to(ROOT))))
        expected = {f["name"]: (f["sha256"], f["byte_count"]) for f in existing["files"]}
        actual = {name: (sha(raw), len(raw)) for name, raw in outputs.items()}
        if existing["package_revision"] != 2 or expected != actual:
            raise ValueError("revision 2 already bound to different finalized bytes")


def validate_private_set(path: Path, outputs: dict[str, bytes]) -> None:
    if {p.name for p in path.iterdir()} != set(outputs):
        raise ValueError("private output inventory differs")
    if path.stat().st_mode & 0o077:
        raise ValueError("private output directory permissions differ")
    for name, raw in outputs.items():
        if read_regular(path, name) != raw or (path / name).stat().st_mode & 0o777 != 0o600:
            raise ValueError("private output bytes or permissions differ")


def publish_exclusive(output: Path, outputs: dict[str, bytes], archive: Path, before: str) -> None:
    parent = _output_parent(output)
    descriptor, identity = None, None
    published: list[tuple[str, int, int]] = []
    try:
        os.mkdir(output.name, mode=0o700, dir_fd=parent)
        identity = os.stat(output.name, dir_fd=parent, follow_symlinks=False)
        descriptor = os.open(output.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
        opened = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino) != (identity.st_dev, identity.st_ino):
            raise ValueError("new output directory ownership changed")
        _write_outputs(descriptor, outputs, published)
        _verify_outputs(descriptor, outputs, published)
        validate_private_set(output, outputs)
        current = os.stat(output.name, dir_fd=parent, follow_symlinks=False)
        if (
            (current.st_dev, current.st_ino) != (identity.st_dev, identity.st_ino)
            or output.resolve() != output
            or inventory(archive) != before
        ):
            raise ValueError("archive or output directory changed during publication")
    except BaseException:
        if descriptor is not None:
            _remove_owned(descriptor, published)
        if identity is not None:
            _remove_owned_directory(parent, output.name, identity)
        raise
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(parent)


def execute(archive: Path, producer: str, output: Path, expected: Path | None, helper: UnicodeHelper) -> dict[str, Any]:
    fingerprints = producer_files(producer)
    before = inventory(archive)
    outputs = build_outputs(archive, producer, fingerprints, before, helper)
    # Independently reload all approval/source authorities and compare all seven bytes before publishing.
    validate_context(outputs, archive, producer, fingerprints, before, helper)
    if inventory(archive) != before:
        raise ValueError("archive changed during independent derivations")
    if expected is not None:
        validate_private_set(expected, outputs)
    check_frozen_release(outputs)
    if output.exists():
        raise ValueError("preserve existing output directory; choose a fresh attempt")
    publish_exclusive(output, outputs, archive, before)
    return {
        "producer_commit": producer,
        "producer_files": fingerprints,
        "files": [{"name": n, "sha256": sha(b), "byte_count": len(b)} for n, b in outputs.items()],
        "independent_seven_file_equality": True,
        "external_build_comparison": expected is not None,
        "archive_before": before,
        "archive_after": inventory(archive),
        "native_helper": {"runtime": helper.runtime, "os": helper.os_identity, "source_sha256": helper.source_sha256},
        "package_sha256": sha(outputs[PACKAGE]),
        "biblos_admission_performed": False,
        "prohibited_operation_counts": dict.fromkeys(
            (
                "network",
                "database",
                "models",
                "providers",
                "cloud",
                "source_acquisition",
                "archive_mutation",
                "original_batch",
                "excluded_or_deferred_re_evaluation",
                "Notes_mutation",
                "Biblos_mutation",
                "training",
            ),
            0,
        ),
    }


def main(argv: list[str] | None = None) -> dict[str, Any]:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-root", type=Path, required=True)
    parser.add_argument("--producer-commit", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--check-against", type=Path)
    args = parser.parse_args(argv)
    if any(k in os.environ for k in ("BSL_DATABASE_URL", "BSL_TEST_DATABASE_URL")):
        raise ValueError("database configuration prohibited")
    archive = args.archive_root.absolute()
    if archive != Path("/Volumes/BSL-Archive/BiblicalScholarLab") or archive.resolve() != archive:
        raise ValueError("canonical read-only archive required")
    output = private_path(args.output_dir, archive)
    expected = private_path(args.check_against, archive) if args.check_against is not None else None
    previous_umask = os.umask(0o077)
    helper = None
    try:
        helper = UnicodeHelper()
        evidence = execute(archive, args.producer_commit, output, expected, helper)
        print(json.dumps(evidence, sort_keys=True))
        return evidence
    finally:
        if helper is not None:
            helper.close()
        os.umask(previous_umask)


if __name__ == "__main__":
    main()
