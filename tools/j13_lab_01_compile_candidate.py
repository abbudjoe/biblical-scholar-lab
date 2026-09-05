"""Reproduce the bounded John 13 candidate from pinned fixtures and a read-only archive."""

import argparse
import json
import os
from contextlib import suppress
from pathlib import Path
from typing import Any

from bsl.application.j13_annotation_verification import verify_j13_annotation_batch
from bsl.application.j13_package_compilation import build_outputs, compile_j13_package_candidate
from bsl.infrastructure.j13_authority import (
    UnicodeHelper,
    inventory,
    load_j13_source_authority,
    load_j13_upstream_authority,
    sha,
)


def _compile(archive: Path, helper: UnicodeHelper, synthetic: bool) -> dict[str, bytes]:
    before = inventory(archive)
    runs = []
    for _ in range(2):
        authority = load_j13_upstream_authority()
        sources = load_j13_source_authority(archive, synthetic=synthetic)
        decisions = verify_j13_annotation_batch(authority, sources, helper)
        package = compile_j13_package_candidate(authority, decisions, helper)
        runs.append((authority, sources, decisions, package))
    if runs[0] != runs[1]:
        raise ValueError("independent candidate builds differ")
    if inventory(archive) != before:
        raise ValueError("archive inventory changed during candidate builds")
    proof = {
        "double_build_package_hashes": [sha(run[3]) for run in runs],
        "double_build_models_and_decisions_equal": runs[0] == runs[1],
        "archive_unchanged": True,
        "double_build_receipt_bytes_equal": True,
    }
    # Receipts are provisional until independent full-output equality is established.
    first, second = [build_outputs(a, s, d, helper, proof) for a, s, d, _ in runs]
    if first != second:
        raise ValueError("independent receipt/output builds differ")
    if inventory(archive) != before:
        raise ValueError("archive inventory changed during receipt builds")
    return first


def _output_parent(output: Path) -> int:
    descriptor = os.open(output.anchor, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for component in output.parts[1:-1]:
            with suppress(FileExistsError):
                os.mkdir(component, mode=0o700, dir_fd=descriptor)
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _remove_owned(descriptor: int, published: list[tuple[str, int, int]]) -> None:
    for name, device, inode in published:
        try:
            info = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
        except FileNotFoundError:
            continue
        if (info.st_dev, info.st_ino) == (device, inode):
            os.unlink(name, dir_fd=descriptor)


def _remove_owned_directory(parent: int, name: str, identity: os.stat_result) -> None:
    try:
        current = os.stat(name, dir_fd=parent, follow_symlinks=False)
        if (current.st_dev, current.st_ino) == (identity.st_dev, identity.st_ino):
            os.rmdir(name, dir_fd=parent)
    except OSError:
        pass  # Preserve unrelated concurrent additions or replacement; never recurse.


def _write_outputs(descriptor: int, outputs: dict[str, bytes], published: list[tuple[str, int, int]]) -> None:
    for name, data in outputs.items():
        fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=descriptor)
        info = os.fstat(fd)
        published.append((name, info.st_dev, info.st_ino))
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)


def _verify_outputs(descriptor: int, outputs: dict[str, bytes], published: list[tuple[str, int, int]]) -> None:
    for name, device, inode in published:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=descriptor)
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            if (info.st_dev, info.st_ino) != (device, inode) or stream.read() != outputs[name]:
                raise ValueError("published artifact identity or bytes changed")


def _publish(output: Path, outputs: dict[str, bytes], expected: Path | None, archive: Path, before: str) -> None:
    for name, data in outputs.items():
        if expected is not None and data != (expected / name).read_bytes():
            raise ValueError(f"candidate artifact drift: {name}")
    parent = _output_parent(output)
    descriptor, created = None, False
    published: list[tuple[str, int, int]] = []
    try:
        try:
            os.mkdir(output.name, mode=0o700, dir_fd=parent)
            created = True
        except FileExistsError:
            pass
        descriptor = os.open(output.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
        identity = os.fstat(descriptor)
        _write_outputs(descriptor, outputs, published)
        _verify_outputs(descriptor, outputs, published)
        if inventory(archive) != before:
            raise ValueError("archive inventory changed during publication")
        current = output.stat(follow_symlinks=False)
        if (current.st_dev, current.st_ino) != (identity.st_dev, identity.st_ino) or output.resolve() != output:
            raise ValueError("output directory identity changed during publication")
    except BaseException:
        if descriptor is not None:
            _remove_owned(descriptor, published)
            if created:
                _remove_owned_directory(parent, output.name, identity)
        raise
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(parent)


def main(
    argv: list[str] | None = None, *, _synthetic: bool = False, _helper: UnicodeHelper | None = None
) -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--check-against", type=Path)
    args = parser.parse_args(argv)
    archive, output = args.archive_root.absolute(), args.output_dir.absolute()
    if output.resolve().is_relative_to(archive.resolve()) or output.resolve() != output:
        raise ValueError("output must be outside the archive and free of symlinks")
    before = inventory(archive)
    helper = _helper if _helper is not None else UnicodeHelper()
    try:
        outputs = _compile(archive, helper, _synthetic)
        if inventory(archive) != before:
            raise ValueError("archive inventory changed before publication")
        _publish(output, outputs, args.check_against, archive, before)
        evidence = {
            "artifacts": {name: sha(data) for name, data in outputs.items()},
            "archive_inventory": before,
            "archive_unchanged": True,
            "swift_version": helper.runtime,
            "os_identity": helper.os_identity,
            "helper_source_sha256": helper.source_sha256,
        }
        print(json.dumps(evidence))
        return evidence
    finally:
        if _helper is None:
            helper.close()


if __name__ == "__main__":
    main()
