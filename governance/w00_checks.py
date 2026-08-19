import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import PurePosixPath
from typing import Any, cast

import jsonschema

REPOSITORY = "abbudjoe/biblical-scholar-lab"
BRANCH = "codex/w00-repository-governance"
ACTIVATION = "ACT-W00-REPOSITORY-GOVERNANCE-v3"
BASE_SHA = "3d3ebb706fe6c8779445cbbfd9fea271b86d3646"
PR_URL = f"https://github.com/{REPOSITORY}/pull/1"
COMPARE_URL = f"https://github.com/{REPOSITORY}/compare/{BASE_SHA}...{BRANCH}"
OBJECTIVE = "W00A1A_CANONICAL_RECORDS_AND_EVIDENCE_INTEGRITY"
EVIDENCE_ROOT = "handoffs/W00/evidence"
ACTIVATION_PATH = "activations/ACT-W00-REPOSITORY-GOVERNANCE-v3.json"
ACTIVATION_HASH = "60def3ad374823a3c9065ad43deb6fb41b7ff079de52a212dc7c47c18d0d30c6"
WORKFLOW = ".github/workflows/governance-integrity.yml"
WORKFLOW_HASH = "406f36d7102ac87da134a9ed817683344e89a12d2a50662504d7b716dd68dbdd"
SCHEMA = "governance/schemas/turn-handoff.schema.json"
TEST = "governance/test_w00_checks.py"
FIXTURE = "governance/fixtures/w00a1a-record.json"
PRODUCTION = {WORKFLOW, "governance/ruff.toml", "governance/w00_checks.py"}
TEST_FILES = {TEST, FIXTURE}
PACKAGE_FILES = {"governance/GOV-01-package-manifest.json", "governance/GOV-01-artifacts.sha256"}
ACTIVE_FILES = PRODUCTION | TEST_FILES | PACKAGE_FILES | {SCHEMA}
DEPENDENCIES = ["actions/checkout", "pypi:jsonschema"]
FINDINGS = {
    "CANONICAL_JSON_TRUTH": ("P2", "CLOSED"),
    "RECEIPT_PATH_CONTENT_BINDING": ("P2", "CLOSED"),
    "COMMAND_CHRONOLOGY": ("P2", "CLOSED"),
    "AST_PROVENANCE": ("P2", "DEFERRED_REMOVED"),
    "DYNAMIC_DEPENDENCY_DISCOVERY": ("P2", "DEFERRED_REMOVED"),
}
TOOLS = "coverage==7.10.6 mypy==2.3.1 radon==6.0.1 ruff==0.16.3 zizmor==1.29.0".split()
UV_COVERAGE = "uv run --with jsonschema==4.25.1 --with coverage==7.10.6 -- "
_COMMANDS = (
    f"{UV_COVERAGE}python3 -m coverage run --branch -m unittest -q {TEST}",
    f"{UV_COVERAGE}python3 -m coverage report --format=total --fail-under=90 governance/w00_checks.py",
    f"uvx ruff@0.16.3 check --quiet --config governance/ruff.toml governance/w00_checks.py {TEST}",
    f"uvx ruff@0.16.3 format --quiet --check --config governance/ruff.toml governance/w00_checks.py {TEST}",
    "uvx mypy@2.3.1 --strict --no-error-summary --ignore-missing-imports governance/w00_checks.py",
    f"uvx zizmor@1.29.0 --offline -q {WORKFLOW}",
    "uvx radon@6.0.1 cc -j governance/w00_checks.py",
    "shasum -a 256 -s -c governance/GOV-01-artifacts.sha256",
    "git diff --check",
)
VALIDATION_ARGV = tuple(tuple(command.split()) for command in _COMMANDS)
_PRIOR = """03e20dfb4692bad3f76710824e7535a4e6a59446 516254fff643371f4315376a4a2ee0f5aaaaad64 W00-SOL-20260817T234806Z
e5a7fb3ff3c20d7eebdcf73af1ba9c0b18084cab 80e52f0c4f91b3b0dc9314e73e7c270e34475927 W00-SOL-REPAIR01-20260818T021301Z
33ebbfdc07b8429e6b1f7a19132e118a476f4fb6 0adb60bd8daa307655b20ec87d11f35fa2590ce9 W00-SOL-REPAIR02-20260818T141853Z
ef7616c0e1d2d3a7e56647762c8441c6d31f7d80 9e72144628880841599d983d6ab9079dfab1a838 W00-SOL-REPAIR03-20260818T230834Z"""
PRIOR_HANDOFFS = tuple(tuple(row.split()) for row in _PRIOR.splitlines())
TURN = re.compile(r"^handoffs/W00/(W00-SOL(?:-REPAIR\d+)?-[0-9]{8}T[0-9]{6}Z)\.(json|md)$")
PATH = re.compile(r"^[A-Za-z0-9._/-]+$")
UTC_TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
Reader = Callable[[str], bytes]


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def strict_json(source: str | bytes) -> Any:
    def unique(items: list[tuple[str, Any]]) -> dict[str, Any]:
        need(len(items) == len(dict(items)), "JSON key is duplicated")
        return dict(items)

    def finite(value: str) -> float:
        number = float(value)
        need(math.isfinite(number), "JSON number is non-finite")
        return number

    return json.loads(source, object_pairs_hook=unique, parse_constant=finite, parse_float=finite)


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def utc(value: str) -> datetime:
    need(UTC_TIME.fullmatch(value) is not None, "timestamp is not canonical UTC")
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)


def safe_path(path: str) -> None:
    pure = PurePosixPath(path)
    valid = path and not pure.is_absolute() and str(pure) == path and ".." not in pure.parts
    need(bool(valid and "\\" not in path and PATH.fullmatch(path) and len(path) <= 240), "path is unsafe")


def _file(turn: str, path: str, expected: str, suffix: str | None, read: Reader, used: set[str]) -> bytes:
    safe_path(path)
    need(
        path.startswith(f"{EVIDENCE_ROOT}/{turn}/") and (suffix is None or path.endswith(suffix)),
        "evidence path differs",
    )
    need(path not in used, "evidence path is reused")
    used.add(path)
    content = read(path)
    need(digest(content) == expected, f"artifact digest differs: {path}")
    return content


def _commands(record: dict[str, Any], read: Reader, used: set[str], implementation_time: datetime) -> None:
    commands = record["commands"]
    need([item["command_index"] for item in commands] == list(range(1, len(commands) + 1)), "command indexes differ")
    need(len({item["command_evidence_id"] for item in commands}) == len(commands), "command evidence id is reused")
    previous = implementation_time
    identity = record["turn_id"], record["activation_id"], record["implementation_head_sha"]
    for command in commands:
        actual = command["root_turn_id"], command["activation_id"], command["implementation_head_sha"]
        need(actual == identity and command["cwd_repo_relative"] == ".", "command identity differs")
        started, finished = utc(command["started_at_utc"]), utc(command["finished_at_utc"])
        need(previous <= started <= finished <= utc(record["completed_at_utc"]), "command chronology differs")
        need(utc(record["started_at_utc"]) <= started, "command precedes root turn")
        previous = started
        receipt = _file(
            record["turn_id"], command["receipt_path"], command["receipt_sha256"], ".receipt.json", read, used
        )
        expected = {key: value for key, value in command.items() if key not in {"receipt_path", "receipt_sha256"}}
        need(strict_json(receipt) == expected, "receipt identity differs")
        _file(record["turn_id"], command["stdout_path"], command["stdout_sha256"], ".stdout", read, used)
        _file(record["turn_id"], command["stderr_path"], command["stderr_sha256"], ".stderr", read, used)


def _results(record: dict[str, Any], artifact_ids: set[str]) -> None:
    evaluations = {item["evidence_artifact_id"] for item in record["evaluations"]}
    findings = {item["finding_id"]: (item["severity"], item["final_status"]) for item in record["review_targets"]}
    need(evaluations == artifact_ids and findings == FINDINGS, "evaluation or finding ledger differs")
    need(
        all(item["evidence_artifact_id"] in artifact_ids for item in record["review_targets"]),
        "finding evidence differs",
    )
    if record["status"] == "READY_FOR_CHATGPT_REVIEW":
        need(all(item["status"] == "PASS" for item in record["evaluations"]), "evaluation failed")
        need(all(item["result"] == "CLEAN" for item in record["delegated_operations"]), "review is not clean")


def validate_record(
    record: dict[str, Any],
    schema: dict[str, Any],
    read: Reader,
    declared_paths: set[str],
    implementation_time: datetime,
    completion_limit: datetime,
) -> None:
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    validator.validate(record)
    keys = "repository branch base_sha pr_url compare_url objective activation_id task_id".split()
    identity = REPOSITORY, BRANCH, BASE_SHA, PR_URL, COMPARE_URL, OBJECTIVE, ACTIVATION, "W00"
    need(tuple(record[key] for key in keys) == identity, "handoff identity differs")
    statuses = "READY_FOR_CHATGPT_REVIEW BLOCKED_REQUIRES_DESIGN_REVIEW BLOCKED_START_STATE_MISMATCH FAILED".split()
    need(record["status"] in statuses, "handoff status differs")
    design = {
        "status": "CONFORMING",
        "approved_design_ids": ["W00A1A-REPAIR04"],
        "unapproved_design_changes_executed": False,
    }
    need(record["design_conformance"] == design, "design identity differs")
    started, completed = utc(record["started_at_utc"]), utc(record["completed_at_utc"])
    need(started <= implementation_time <= completed <= completion_limit, "root-turn chronology differs")
    used: set[str] = set()
    _commands(record, read, used, implementation_time)
    auth = record["github_auth_preflight"]
    auth_bytes = _file(record["turn_id"], auth["receipt_path"], auth["receipt_sha256"], ".auth.json", read, used)
    canonical_auth = {key: value for key, value in auth.items() if key not in {"receipt_path", "receipt_sha256"}}
    need(strict_json(auth_bytes) == canonical_auth, "authentication receipt differs")
    artifact_ids = {item["artifact_id"] for item in record["artifacts"]}
    need(len(artifact_ids) == len(record["artifacts"]), "artifact id is reused")
    for artifact in record["artifacts"]:
        _file(record["turn_id"], artifact["path"], artifact["sha256"], None, read, used)
    _results(record, artifact_ids)
    need(used == declared_paths, "evidence set has a dangling or missing artifact")
    need(
        record["billable_actions"] == {"performed": False, "actual_cost_usd": 0, "campaign_ids": []}, "billable differs"
    )
    risks = ["PROJECT_INTEGRITY_BOOTSTRAP_COMPATIBILITY_ONLY", "LATER_GOVERNANCE_PHASES_DEFERRED"]
    need(record["known_risks"] == risks and not record["decisions_required"], "canonical risk state differs")


def render_markdown(record: dict[str, Any], parent: str) -> str:
    keys = "approval_submitted billable_actions merge_performed next_task_started status".split()
    facts = {key: record[key] for key in keys}
    return (
        "# W00A1a — Canonical Records and Evidence Integrity\n\n"
        "The paired JSON is authoritative; "
        f"implementation `{parent}`; root `{record['turn_id']}`; "
        f"window `{record['started_at_utc']}`–`{record['completed_at_utc']}`.\n"
        f"Typed terminal facts: `{json.dumps(facts, sort_keys=True, separators=(',', ':'))}`.\n\n"
        "W00A1b, W00A2, W00B, and W01 remain absent and unauthorized.\n"
    )


def project_command(head: str) -> tuple[str, ...]:
    command = "uv run --with jsonschema==4.25.1 -- python3 governance/w00_checks.py project-integrity"
    return tuple(f"{command} --base-sha {BASE_SHA} --head-sha {head} --branch {BRANCH}".split())


def validate_markdown(record: dict[str, Any], parent: str, source: str) -> None:
    need(source == render_markdown(record, parent), "Markdown differs")


def run(arguments: list[str], *, text: bool = True) -> subprocess.CompletedProcess[Any]:
    return subprocess.run(arguments, check=True, text=text, capture_output=True, timeout=30)


def git(*arguments: str) -> str:
    return cast(str, run(["git", *arguments]).stdout).strip()


def blob(revision: str, path: str) -> bytes:
    return cast(bytes, run(["git", "show", f"{revision}:{path}"], text=False).stdout)


def object_at(revision: str, path: str) -> dict[str, Any]:
    content = blob(revision, path)
    value = strict_json(content)
    need(len(content) <= 262_144 and isinstance(value, dict), f"{path} is not a bounded object")
    return cast(dict[str, Any], value)


def artifact_reader(revision: str) -> Reader:
    def read(path: str) -> bytes:
        safe_path(path)
        entry = git("ls-tree", revision, "--", path)
        need(entry.startswith("100644 blob ") and entry.endswith(f"\t{path}"), "evidence is not a regular file")
        return blob(revision, path)

    return read


def activation(base: str, branch: str) -> None:
    valid = (base, branch) == (BASE_SHA, BRANCH) and digest(blob(base, ACTIVATION_PATH)) == ACTIVATION_HASH
    need(valid, "activation differs")


def changed_paths(base: str, head: str) -> list[str]:
    content = cast(
        bytes, run(["git", "diff", "--no-renames", "--name-only", "-z", f"{base}...{head}"], text=False).stdout
    )
    paths = [item.decode() for item in content.split(b"\0") if item]
    for path in paths:
        safe_path(path)
    return paths


def _diff_lines(base: str, head: str, paths: list[str] | None = None) -> tuple[int, int]:
    if paths == []:
        return 0, 0
    args = ["diff", "--no-renames", "--unified=0", f"{base}...{head}", *(("--", *paths) if paths else ())]
    added = removed = 0
    in_hunk = False
    for line in git(*args).splitlines():
        if line.startswith(("diff --git", "@@")):
            in_hunk = line.startswith("@@")
        elif in_hunk and len(line) > 1 and line[1:].strip():
            added += int(line.startswith("+"))
            removed += int(line.startswith("-"))
    return added, removed


def budget(base: str, head: str, paths: list[str]) -> dict[str, Any]:
    rows = (
        line.split("\t", 1) for line in git("diff", "--no-renames", "--name-status", f"{base}...{head}").splitlines()
    )
    statuses = {path: status for status, path in rows}
    production, tests = sorted(PRODUCTION & set(paths)), sorted(TEST_FILES & set(paths))
    total, production_lines, test_lines = (
        _diff_lines(base, head),
        _diff_lines(base, head, production),
        _diff_lines(base, head, tests),
    )
    added, removed = (sorted(path for path in production if statuses[path] == status) for status in ("A", "D"))
    empty = (
        "modules_removed tables_added migrations_added endpoints_added dependencies_removed "
        "known_duplication_or_debt waivers"
    )
    receipt: dict[str, Any] = {key: [] for key in empty.split()}
    receipt.update(
        {
            "substantive_lines_total": sum(total),
            "production_loc_added": production_lines[0],
            "production_loc_removed": production_lines[1],
            "test_loc_added": test_lines[0],
            "test_loc_removed": test_lines[1],
            "generated_loc": 0,
            "production_files_added": len(added),
            "production_files_removed": len(removed),
            "modules_added": added,
            "cli_commands_added": ["project-integrity", "turn-handoff-integrity"],
            "dependencies_added": DEPENDENCIES,
            "public_contracts_changed": [f"schema:{SCHEMA}"],
            "abstractions": [{"name": "STRICT_RECORD_VALIDATOR", "reason": "CANONICAL_W00A1A_BOUNDARY"}],
            "simpler_alternatives_considered": ["DEFERRED_STATIC_ANALYSIS_REMOVED"],
            "workflow_files": [WORKFLOW],
            "external_validation_tools": TOOLS,
            "simplicity_conformance": "PASS",
        }
    )
    need(not removed, "removed production surface differs")
    return receipt


def validate_budget(metrics: dict[str, Any]) -> None:
    surface = set(metrics["modules_added"]) == PRODUCTION and metrics["substantive_lines_total"] <= 800
    limits = len(metrics["dependencies_added"]) <= 2 and len(metrics["public_contracts_changed"]) <= 1
    need(surface and limits and not metrics["migrations_added"], "W00A1a budget or surface differs")


def validate_project(base: str, head: str, branch: str) -> dict[str, Any]:
    activation(base, branch)
    paths = changed_paths(base, head)
    need(all(path in ACTIVE_FILES or path.startswith("handoffs/W00/") for path in paths), "change is outside W00A1a")
    metrics = budget(base, head, paths)
    validate_budget(metrics)
    jsonschema.Draft202012Validator.check_schema(strict_json(blob(head, SCHEMA)))
    need(digest(blob(head, WORKFLOW)) == WORKFLOW_HASH, "workflow differs")
    return {"scope": "BOOTSTRAP_COMPATIBILITY_ONLY", "changed_paths": paths, **metrics}


def _record_files(commit: str, parent: str) -> tuple[str, tuple[str, str], set[str]] | None:
    lines = git(
        "diff-tree", "--no-commit-id", "--name-status", "--no-renames", "-r", parent, commit, "--", "handoffs/W00/"
    ).splitlines()
    if not lines:
        return None
    need(all(line.startswith("A\t") for line in lines), "append-only record was changed")
    paths = [line.split("\t", 1)[1] for line in lines]
    pair = {match.group(2): (path, match.group(1)) for path in paths if (match := TURN.fullmatch(path))}
    turns = {value[1] for value in pair.values()}
    need(set(pair) == {"json", "md"} and len(turns) == 1, "handoff pair differs")
    turn = next(iter(turns))
    files = pair["json"][0], pair["md"][0]
    evidence = set(paths) - set(files)
    need(all(path.startswith(f"{EVIDENCE_ROOT}/{turn}/") for path in evidence), "record evidence path differs")
    return turn, files, evidence


def _prior(head: str) -> None:
    for commit, parent, turn in PRIOR_HANDOFFS:
        ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", commit, head], capture_output=True)
        need(ancestor.returncode == 0 and git("rev-parse", f"{commit}^") == parent, "prior ancestry differs")
        for suffix in ("json", "md"):
            path = f"handoffs/W00/{turn}.{suffix}"
            need(blob(head, path) == blob(commit, path), f"prior handoff changed: {path}")


def _validated_commands(record: dict[str, Any], parent: str) -> bool:
    commands = {tuple(item["argv"]) for item in record["commands"] if item["exit_code"] == 0}
    return commands == set(VALIDATION_ARGV) | {project_command(parent)}


def validate_handoff(base: str, head: str, branch: str, pr_url: str) -> dict[str, Any]:
    activation(base, branch)
    need(pr_url == PR_URL, "PR URL differs")
    _prior(head)
    rows = [line.split() for line in git("rev-list", "--reverse", "--parents", f"{base}..{head}").splitlines()]
    need(all(len(row) == 2 for row in rows), "candidate history contains a merge")
    records = [(commit, parent, item) for commit, parent in rows if (item := _record_files(commit, parent))]
    need([commit for commit, _, _ in records[:-1]] == [item[0] for item in PRIOR_HANDOFFS], "handoff order differs")
    commit, parent, (turn, pair, evidence) = records[-1]
    need(commit == head and turn.startswith("W00-SOL-REPAIR04-"), "final handoff differs")
    need(_record_files(parent, git("rev-parse", f"{parent}^")) is None, "implementation head is a record commit")
    changed = set(git("diff-tree", "--no-commit-id", "--name-only", "-r", parent, commit).splitlines())
    need(changed == set(pair) | evidence, "final commit contains implementation changes")
    record = object_at(head, pair[0])
    need(record["turn_id"] == turn and record["implementation_head_sha"] == parent, "handoff parent differs")
    implementation_time = datetime.fromisoformat(git("show", "-s", "--format=%cI", parent))
    completion_limit = datetime.fromisoformat(git("show", "-s", "--format=%cI", commit))
    validate_record(
        record, object_at(head, SCHEMA), artifact_reader(head), evidence, implementation_time, completion_limit
    )
    metrics = budget(base, head, changed_paths(base, head))
    validate_budget(metrics)
    need(record["complexity_receipt"] == metrics, "complexity receipt differs")
    validate_markdown(record, parent, blob(head, pair[1]).decode())
    need(_validated_commands(record, parent), "authoritative command set differs")
    return {"turn_id": turn, "implementation_head_sha": parent, "status": record["status"]}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="check", required=True)
    project = sub.add_parser("project-integrity")
    for flag in ("--base-sha", "--head-sha", "--branch"):
        project.add_argument(flag, required=True)
    handoff = sub.add_parser("turn-handoff-integrity")
    for flag in ("--base-sha", "--head-sha", "--branch", "--pr-url"):
        handoff.add_argument(flag, required=True)
    return root


def main() -> int:
    arguments = parser().parse_args()
    try:
        result = (
            validate_project(arguments.base_sha, arguments.head_sha, arguments.branch)
            if arguments.check == "project-integrity"
            else validate_handoff(arguments.base_sha, arguments.head_sha, arguments.branch, arguments.pr_url)
        )
    except Exception:
        print('{"status":"failure"}')
        return 1
    print(json.dumps({"status": "success", "result": result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
