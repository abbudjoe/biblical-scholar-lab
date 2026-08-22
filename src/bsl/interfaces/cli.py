from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn

from bsl.application.archive_initialization import initialize_archive
from bsl.application.john15_normalization import normalize_john15
from bsl.application.source_acquisition import acquire_source
from bsl.application.source_admission import compile_source_plan
from bsl.contracts.archive import ArchiveReadiness
from bsl.infrastructure.macos_volume import inspect_volume

PRIVATE_RECEIPT = Path(".local/evidence/VS01-T01/archive-preflight.json")


class CliInputError(ValueError):
    pass


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise CliInputError(message)


def _parser() -> JsonArgumentParser:
    parser = JsonArgumentParser(prog="bsl", description="Biblical Scholar Lab local foundation")
    commands = parser.add_subparsers(dest="command", required=True)
    archive = commands.add_parser("archive")
    archive_commands = archive.add_subparsers(dest="archive_command", required=True)
    inspect = archive_commands.add_parser("inspect")
    inspect.add_argument("--volume-name", required=True)
    initialize = archive_commands.add_parser("initialize")
    initialize.add_argument("--profile", required=True, type=Path)
    initialize.add_argument("--private-receipt", required=True, type=Path)
    initialize.add_argument("--private-apfs-snapshot", required=True, type=Path)
    initialize.add_argument("--root", required=True, type=Path)
    source = commands.add_parser("source")
    source_commands = source.add_subparsers(dest="source_command", required=True)
    plan = source_commands.add_parser("plan")
    plan.add_argument("--manifest", required=True, type=Path)
    acquire = source_commands.add_parser("acquire")
    acquire.add_argument("--source-id", required=True)
    acquire.add_argument("--manifest", required=True, type=Path)
    acquire.add_argument("--archive-root", required=True, type=Path)
    normalize = commands.add_parser("normalize")
    normalize_commands = normalize.add_subparsers(dest="normalize_command", required=True)
    john = normalize_commands.add_parser("john-1-5")
    john.add_argument("--archive-root", required=True, type=Path)
    john.add_argument("--dry-run", action="store_true")
    return parser


def _emit_error(code: str, message: str) -> int:
    print(json.dumps({"error": {"code": code, "message": message}}, sort_keys=True))
    return 2


def _archive(volume_name: str) -> int:
    receipt = inspect_volume(volume_name)
    rendered = receipt.model_dump_json(indent=2)
    PRIVATE_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    PRIVATE_RECEIPT.write_text(f"{rendered}\n", encoding="utf-8")
    print(rendered)
    return int(receipt.readiness in {ArchiveReadiness.UNSUPPORTED_HOST, ArchiveReadiness.INSPECTION_FAILED})


def _source_acquire(source_id: str, manifest: Path, archive_root: Path) -> int:
    result = acquire_source(source_id, manifest, archive_root)
    output = {
        "fetch_receipt": result.fetch_receipt.model_dump(mode="json") if result.fetch_receipt else None,
        "admission_decision": result.decision.model_dump(mode="json"),
        "source_snapshot": result.snapshot.model_dump(mode="json") if result.snapshot else None,
        "verified_existing": result.verified_existing,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return int(result.decision.disposition != "ADMITTED")


def _source(args: argparse.Namespace) -> int:
    if args.source_command == "plan":
        print(compile_source_plan(args.manifest).model_dump_json(indent=2))
        return 0
    if args.source_command == "acquire":
        return _source_acquire(args.source_id, args.manifest, args.archive_root)
    return _emit_error("INVALID_CLI_INPUT", "unsupported source command")


def _normalize(args: argparse.Namespace) -> int:
    if args.normalize_command != "john-1-5":
        return _emit_error("INVALID_CLI_INPUT", "unsupported normalization command")
    result = normalize_john15(args.archive_root, dry_run=args.dry_run)
    output = {
        "bundle": result.bundle.model_dump(mode="json"),
        "receipt": result.receipt.model_dump(mode="json"),
        "published": result.published,
        "verified_existing": result.verified_existing,
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        if args.command == "archive" and args.archive_command == "inspect":
            return _archive(args.volume_name)
        if args.command == "archive" and args.archive_command == "initialize":
            receipt = initialize_archive(args.profile, args.private_receipt, args.private_apfs_snapshot, args.root)
            print(receipt.model_dump_json(indent=2))
            return 0
        if args.command == "source":
            return _source(args)
        if args.command == "normalize":
            return _normalize(args)
        return _emit_error("INVALID_CLI_INPUT", "unsupported command")
    except CliInputError as exc:
        return _emit_error("INVALID_CLI_INPUT", str(exc))
    except (OSError, ValueError) as exc:
        return _emit_error("OPERATION_FAILED", str(exc))


if __name__ == "__main__":
    sys.exit(main())
