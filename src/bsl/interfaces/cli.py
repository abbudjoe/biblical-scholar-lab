from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, NoReturn

from bsl.contracts.archive import ArchiveReadiness

PRIVATE_RECEIPT = Path(".local/evidence/VS01-T01/archive-preflight.json")


class CliInputError(ValueError):
    pass


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise CliInputError(message)


def initialize_archive(*args: Any, **kwargs: Any) -> Any:
    from bsl.application.archive_initialization import initialize_archive as operation

    return operation(*args, **kwargs)


def generate_john15_evidence(*args: Any, **kwargs: Any) -> Any:
    from bsl.application.john15_evidence import generate_john15_evidence as operation

    return operation(*args, **kwargs)


def normalize_john15(*args: Any, **kwargs: Any) -> Any:
    from bsl.application.john15_normalization import normalize_john15 as operation

    return operation(*args, **kwargs)


def generate_john15_page_fixture(*args: Any, **kwargs: Any) -> Any:
    from bsl.application.john15_page_fixture import generate_john15_page_fixture as operation

    return operation(*args, **kwargs)


def execute_john15_study(*args: Any, **kwargs: Any) -> Any:
    from bsl.application.john15_study_runtime import execute_john15_study as operation

    return operation(*args, **kwargs)


def acquire_source(*args: Any, **kwargs: Any) -> Any:
    from bsl.application.source_acquisition import acquire_source as operation

    return operation(*args, **kwargs)


def compile_source_plan(*args: Any, **kwargs: Any) -> Any:
    from bsl.application.source_admission import compile_source_plan as operation

    return operation(*args, **kwargs)


def run_reference_campaign(*args: Any, **kwargs: Any) -> Any:
    from bsl.application.vs01_benchmark_scoring import run_reference_campaign as operation

    return operation(*args, **kwargs)


def run_runtime_pair(*args: Any, **kwargs: Any) -> Any:
    from bsl.application.vs01_runtime_screening import run_runtime_pair as operation

    return operation(*args, **kwargs)


def inspect_volume(*args: Any, **kwargs: Any) -> Any:
    from bsl.infrastructure.macos_volume import inspect_volume as operation

    return operation(*args, **kwargs)


def run_vs01_web(*args: Any, **kwargs: Any) -> Any:
    from bsl.interfaces.vs01_web import run_vs01_web as operation

    return operation(*args, **kwargs)


def _loopback_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("port must be an integer from 1024 through 65535") from None
    if not 1024 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be an integer from 1024 through 65535")
    return port


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
    evidence = commands.add_parser("evidence")
    evidence_commands = evidence.add_subparsers(dest="evidence_command", required=True)
    nuance = evidence_commands.add_parser("john-1-5-translation-nuance")
    nuance.add_argument("--archive-root", required=True, type=Path)
    nuance.add_argument("--dry-run", action="store_true")
    study = commands.add_parser("study")
    study_commands = study.add_subparsers(dest="study_command", required=True)
    john_study = study_commands.add_parser("john-1-5-translation-nuance")
    john_study.add_argument("--archive-root", required=True, type=Path)
    john_study.add_argument("--render", required=True, choices=("brief", "study", "both"))
    john_study.add_argument("--dry-run", action="store_true")
    page = commands.add_parser("page")
    page_commands = page.add_subparsers(dest="page_command", required=True)
    fixture = page_commands.add_parser("john-1-5-synthetic-fixture")
    fixture.add_argument("--archive-root", required=True, type=Path)
    fixture.add_argument("--dry-run", action="store_true")
    benchmark = commands.add_parser("benchmark")
    benchmark_commands = benchmark.add_subparsers(dest="benchmark_command", required=True)
    batch = benchmark_commands.add_parser("vs01-batch-01")
    batch.add_argument("--subject", required=True, choices=("deterministic-reference",))
    batch.add_argument("--dry-run", action="store_true")
    runtime_pair = benchmark_commands.add_parser("vs01-b08-runtime-pair")
    runtime_pair.add_argument("--subject", required=True, choices=("deterministic-runtime",))
    runtime_pair.add_argument("--dry-run", action="store_true")
    web = commands.add_parser("web")
    web_commands = web.add_subparsers(dest="web_command", required=True)
    vs01 = web_commands.add_parser("vs01")
    vs01.add_argument("--port", required=True, type=_loopback_port)
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


def _archive_command(args: argparse.Namespace) -> int:
    if args.archive_command == "inspect":
        return _archive(args.volume_name)
    if args.archive_command == "initialize":
        receipt = initialize_archive(args.profile, args.private_receipt, args.private_apfs_snapshot, args.root)
        print(receipt.model_dump_json(indent=2))
        return 0
    return _emit_error("INVALID_CLI_INPUT", "unsupported archive command")


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


def _evidence(args: argparse.Namespace) -> int:
    if args.evidence_command != "john-1-5-translation-nuance":
        return _emit_error("INVALID_CLI_INPUT", "unsupported evidence command")
    result = generate_john15_evidence(args.archive_root, dry_run=args.dry_run)
    output = {
        "packet": result.packet.model_dump(mode="json"),
        "receipt": result.receipt.model_dump(mode="json"),
        "published": result.published,
        "verified_existing": result.verified_existing,
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return 0


def _study(args: argparse.Namespace) -> int:
    if args.study_command != "john-1-5-translation-nuance":
        return _emit_error("INVALID_CLI_INPUT", "unsupported study command")
    database_url = None if args.dry_run else os.environ.get("BSL_DATABASE_URL")
    result = execute_john15_study(args.archive_root, dry_run=args.dry_run, database_url=database_url)
    output = {
        "request": result.request.model_dump(mode="json"),
        "execution_record": result.execution_record.model_dump(mode="json"),
        "brief_answer": result.brief_answer.model_dump(mode="json") if args.render in {"brief", "both"} else None,
        "study_answer": result.study_answer.model_dump(mode="json") if args.render in {"study", "both"} else None,
        "audit_receipt": result.audit_receipt.model_dump(mode="json"),
        "persisted": result.persisted,
        "verified_existing": result.verified_existing,
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return 0


def _page(args: argparse.Namespace) -> int:
    if args.page_command != "john-1-5-synthetic-fixture":
        return _emit_error("INVALID_CLI_INPUT", "unsupported page command")
    result = generate_john15_page_fixture(args.archive_root, dry_run=args.dry_run)
    output = {
        "fixture_identity": result.fixture.fixture_identity,
        "raster_assets": result.fixture.raster_assets,
        "receipt": result.receipt.model_dump(mode="json"),
        "published": result.published,
        "verified_existing": result.verified_existing,
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return 0


def _benchmark(args: argparse.Namespace) -> int:
    if args.benchmark_command == "vs01-batch-01" and args.subject == "deterministic-reference":
        specification, result, receipt, published = run_reference_campaign(dry_run=args.dry_run)
        output = {
            "execution_specification": specification.model_dump(mode="json"),
            "run_result": result.model_dump(mode="json"),
            "receipt": receipt.model_dump(mode="json"),
            "published": published,
        }
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
        return int(result.disposition != "REFERENCE_CONFORMANT")
    if args.benchmark_command == "vs01-b08-runtime-pair" and args.subject == "deterministic-runtime":
        try:
            specification, run, result, receipt, published = run_runtime_pair(dry_run=args.dry_run)
        except (OSError, ValueError):
            return _emit_error("OPERATION_FAILED", "runtime screening operation failed")
        output = {
            "pair_specification": specification.model_dump(mode="json"),
            "acquisition_run": run.model_dump(mode="json"),
            "pair_result": result.model_dump(mode="json"),
            "receipt": receipt.model_dump(mode="json"),
            "published": published,
        }
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
        success = result.disposition == "REFERENCE_CONFORMANT" or receipt.disposition == "VERIFIED_EXISTING"
        return int(not success)
    return _emit_error("INVALID_CLI_INPUT", "unsupported benchmark or subject")


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        if args.command == "archive":
            return _archive_command(args)
        if args.command == "source":
            return _source(args)
        if args.command == "normalize":
            return _normalize(args)
        if args.command == "evidence":
            return _evidence(args)
        if args.command == "study":
            return _study(args)
        if args.command == "page":
            return _page(args)
        if args.command == "benchmark":
            return _benchmark(args)
        if args.command == "web" and args.web_command == "vs01":
            run_vs01_web(args.port)
            return 0
        return _emit_error("INVALID_CLI_INPUT", "unsupported command")
    except CliInputError as exc:
        return _emit_error("INVALID_CLI_INPUT", str(exc))
    except (OSError, ValueError) as exc:
        return _emit_error("OPERATION_FAILED", str(exc))


if __name__ == "__main__":
    sys.exit(main())
