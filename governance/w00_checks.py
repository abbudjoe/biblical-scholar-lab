import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any, cast

import jsonschema

BRANCH = "codex/w00-repository-governance"
ACTIVATION = "ACT-W00-REPOSITORY-GOVERNANCE-v3"
BASE_SHA = "3d3ebb706fe6c8779445cbbfd9fea271b86d3646"
PR_URL = "https://github.com/abbudjoe/biblical-scholar-lab/pull/1"
EVIDENCE_ROOT = "handoffs/W00/evidence"
ACTIVATION_PATH = "activations/ACT-W00-REPOSITORY-GOVERNANCE-v3.json"
WORKFLOW = ".github/workflows/governance-integrity.yml"
SCHEMA = "governance/schemas/turn-handoff.schema.json"
TEST = "governance/test_w00_checks.py"
FIXTURE = "governance/fixtures/w00a1a-record.json"
POLICY_PATH = "governance/fixtures/w00a1a-policy.json"
POLICY_HASH = "8229fa6af5030d395e5a6f8d53b841e70db68d78f6957949121a4022e5e92eea"
PRODUCTION = {WORKFLOW, "governance/ruff.toml", "governance/w00_checks.py", POLICY_PATH}
TEST_FILES = {TEST, FIXTURE, "governance/fixtures/w00a1a-negative.json"}
PACKAGE_FILES = {"governance/GOV-01-package-manifest.json", "governance/GOV-01-artifacts.sha256"}
ACTIVE_FILES = PRODUCTION | TEST_FILES | PACKAGE_FILES | {SCHEMA}
DR30_KEYS = "module_max_lines function_max_lines cyclomatic_complexity_max line_length_max nesting_limit_enforced target_excess_justification simplicity_conformance".split()
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


POLICY = cast(
    dict[str, Any], strict_json(Path(__file__).with_name("fixtures").joinpath("w00a1a-policy.json").read_bytes())
)
VALIDATION_ARGV = tuple(tuple(command.split()) for command in POLICY["validation_commands"])
PRIOR_HANDOFFS = tuple(tuple(row) for row in POLICY["prior_handoffs"])


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def utc(value: str) -> datetime:
    need(UTC_TIME.fullmatch(value) is not None, "timestamp is not canonical UTC")
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)


def safe_path(path: str) -> None:
    pure = PurePosixPath(path)
    valid = path and not pure.is_absolute() and str(pure) == path and ".." not in pure.parts
    need(bool(valid and "\\" not in path and PATH.fullmatch(path) and len(path) <= 240), "path is unsafe")


def _file(turn: str, path: str, expected: str, suffix: str, read: Reader, used: set[str]) -> bytes:
    safe_path(path)
    need(path.startswith(f"{EVIDENCE_ROOT}/{turn}/") and path.endswith(suffix), "evidence path differs")
    need(path not in used, "evidence path is reused")
    used.add(path)
    content = read(path)
    need(len(content) <= 262_144 and digest(content) == expected, f"artifact digest differs: {path}")
    return content


def _commands(
    record: dict[str, Any], read: Reader, used: set[str], implementation_time: datetime
) -> dict[tuple[str, ...], bytes]:
    commands = record["commands"]
    suite = [*VALIDATION_ARGV, project_command(record["implementation_head_sha"])]
    need([tuple(item["argv"]) for item in commands] == suite, "authoritative command set differs")
    need(all(item["exit_code"] == 0 for item in commands), "authoritative command failed")
    need([item["command_index"] for item in commands] == list(range(1, len(commands) + 1)), "command indexes differ")
    need(len({item["command_evidence_id"] for item in commands}) == len(commands), "command evidence id is reused")
    turn = record["turn_id"]
    previous = implementation_time
    identity = turn, record["activation_id"], record["implementation_head_sha"]
    completed = utc(record["completed_at_utc"])
    outputs: dict[tuple[str, ...], bytes] = {}
    for command in commands:
        observed = command["root_turn_id"], command["activation_id"], command["implementation_head_sha"]
        need(observed == identity and command["cwd_repo_relative"] == ".", "command identity differs")
        started, finished = utc(command["started_at_utc"]), utc(command["finished_at_utc"])
        need(previous <= started <= finished <= completed, "command chronology differs")
        previous = started
        receipt = _file(turn, command["receipt_path"], command["receipt_sha256"], ".receipt.json", read, used)
        envelope = {key: value for key, value in command.items() if key not in {"receipt_path", "receipt_sha256"}}
        need(strict_json(receipt) == envelope, "receipt identity differs")
        stdout = _file(turn, command["stdout_path"], command["stdout_sha256"], ".stdout", read, used)
        outputs[tuple(command["argv"])] = stdout
        _file(turn, command["stderr_path"], command["stderr_sha256"], ".stderr", read, used)
    return outputs


def _reports(record: dict[str, Any], coverage: int, dr30: dict[str, Any]) -> dict[str, Any]:
    validation = {
        **POLICY["validation_report"],
        "branch_coverage_percent": coverage,
        "command_count": len(record["commands"]),
        "commands_passed": len(record["commands"]),
        "dr30": dr30,
        "implementation_head_sha": record["implementation_head_sha"],
    }
    review = {**POLICY["review_report"], "implementation_head_sha": record["implementation_head_sha"]}
    return {"VALIDATION": validation, "REVIEW": review}


def _results(record: dict[str, Any], reports: dict[str, Any], outputs: dict[tuple[str, ...], bytes]) -> None:
    need(record["review_targets"] == POLICY["findings"], "finding ledger differs")
    if record["status"] == "READY_FOR_CHATGPT_REVIEW":
        review = record["evaluations"], record["delegated_operations"]
        need(review == (POLICY["evaluations"], [POLICY["delegation"]]), "review differs")
        coverage = int(outputs[VALIDATION_ARGV[1]].strip())
        validation = reports.get("VALIDATION")
        need(isinstance(validation, dict), "validation report differs")
        claimed = cast(dict[str, Any], validation).get("dr30", {})
        _check_dr30(claimed, record["complexity_receipt"]["substantive_lines_total"])
        need(reports == _reports(record, coverage, claimed), "validation or review report differs")


def validate_record(
    record: dict[str, Any],
    schema: dict[str, Any],
    read: Reader,
    declared_paths: set[str],
    implementation_time: datetime,
    completion_limit: datetime,
) -> tuple[dict[tuple[str, ...], bytes], dict[str, Any]]:
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(record)
    canonical = cast(dict[str, Any], POLICY["canonical_fields"])
    need(all(record[key] == value for key, value in canonical.items()), "canonical handoff truth differs")
    need(record["status"] in POLICY["statuses"], "handoff disposition differs")
    started, completed = utc(record["started_at_utc"]), utc(record["completed_at_utc"])
    need(started <= implementation_time <= completed <= completion_limit, "root-turn chronology differs")
    turn = record["turn_id"]
    used: set[str] = set()
    outputs = _commands(record, read, used, implementation_time)
    auth = record["github_auth_preflight"]
    auth_bytes = _file(turn, auth["receipt_path"], auth["receipt_sha256"], ".auth.json", read, used)
    canonical_auth = {key: value for key, value in auth.items() if key not in {"receipt_path", "receipt_sha256"}}
    need(strict_json(auth_bytes) == canonical_auth, "authentication receipt differs")
    root = f"{EVIDENCE_ROOT}/{turn}"
    descriptors = [(item["artifact_id"], item["kind"], item["path"]) for item in record["artifacts"]]
    expected_artifacts = [(artifact_id, kind, f"{root}/{name}") for artifact_id, kind, name in POLICY["artifacts"]]
    need(descriptors == expected_artifacts, "artifact ledger differs")
    reports = {
        artifact["artifact_id"]: strict_json(_file(turn, artifact["path"], artifact["sha256"], ".json", read, used))
        for artifact in record["artifacts"]
    }
    _results(record, reports, outputs)
    observed = used, record["billable_actions"], record["known_risks"], record["decisions_required"]
    need(observed == (declared_paths, POLICY["billable"], POLICY["risks"], []), "canonical evidence differs")
    return outputs, reports


def render_markdown(record: dict[str, Any], parent: str) -> str:
    facts = {key: record[key] for key in POLICY["terminal_fields"]}
    lines = [
        f"Identity: activation `{record['activation_id']}` / `W00A1A-REPAIR04`; branch `{record['branch']}`; PR "
        f"`{record['pr_url']}`; base `{record['base_sha']}`; start `{POLICY['start_head']}`; implementation `{parent}`; "
        "final/live "
        f"SHA is the containing commit/live PR head; root `{record['turn_id']}`; window `{record['started_at_utc']}`–"
        f"`{record['completed_at_utc']}`.",
        f"Scope: {POLICY['scope_statement']} Exact path ledger `{compact(record['changes'])}`.",
        f"Evidence: commands `{compact(record['commands'])}`; artifacts `{compact(record['artifacts'])}`; review "
        f"`{compact(record['evaluations'] + record['delegated_operations'])}`.",
        f"Complexity/dependencies `{compact(record['complexity_receipt'])}`; facts `{compact(facts)}`; limitations "
        f"`{compact(record['known_risks'])}`.",
        POLICY["stop_statement"],
    ]
    return "# W00A1a — Canonical Records and Evidence Integrity\n\n" + "\n".join(lines) + "\n"


def project_command(head: str) -> tuple[str, ...]:
    command = "uv run --with jsonschema==4.25.1 -- python3 governance/w00_checks.py project-integrity"
    return tuple(f"{command} --base-sha {BASE_SHA} --head-sha {head} --branch {BRANCH}".split())


def run(arguments: list[str], *, text: bool = True) -> subprocess.CompletedProcess[Any]:
    return subprocess.run(arguments, check=True, text=text, capture_output=True, timeout=30)


def git(*arguments: str) -> str:
    return cast(str, run(["git", *arguments]).stdout).strip()


def blob(revision: str, path: str) -> bytes:
    return cast(bytes, run(["git", "show", f"{revision}:{path}"], text=False).stdout)


def object_at(revision: str, path: str) -> dict[str, Any]:
    content = blob(revision, path)
    need(len(content) <= 262_144, f"{path} is oversized")
    value = strict_json(content)
    need(isinstance(value, dict), f"{path} is not an object")
    return cast(dict[str, Any], value)


def artifact_reader(revision: str) -> Reader:
    def read(path: str) -> bytes:
        safe_path(path)
        entry = git("ls-tree", revision, "--", path)
        need(entry.startswith("100644 blob ") and entry.endswith(f"\t{path}"), "evidence is not a regular file")
        return blob(revision, path)

    return read


def activation(base: str, branch: str) -> None:
    valid = (base, branch) == (BASE_SHA, BRANCH) and digest(blob(base, ACTIVATION_PATH)) == POLICY["activation_hash"]
    need(valid, "activation differs")


def change_ledger(base: str, head: str) -> list[dict[str, Any]]:
    groups: dict[str, list[str]] = {kind: [] for kind in ("ADD", "MODIFY", "DELETE")}
    status_kind = {"A": "ADD", "M": "MODIFY", "D": "DELETE"}
    for row in git("diff", "--no-renames", "--name-status", f"{base}...{head}").splitlines():
        status, path = row.split("\t", 1)
        safe_path(path)
        need(status in status_kind, "change status differs")
        groups[status_kind[status]].append(path)
    return [
        {"change_id": f"FILES_{kind}", "kind": kind, "paths": sorted(paths)} for kind, paths in groups.items() if paths
    ]


def paths_at(base: str, head: str) -> list[str]:
    return [path for item in change_ledger(base, head) for path in item["paths"]]


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
    ledger = change_ledger(base, head)
    statuses = {path: item["kind"] for item in ledger for path in item["paths"]}
    production, tests = sorted(PRODUCTION & set(paths)), sorted(TEST_FILES & set(paths))
    total, production_lines, test_lines = (
        _diff_lines(base, head),
        _diff_lines(base, head, production),
        _diff_lines(base, head, tests),
    )
    added, removed = (sorted(path for path in production if statuses[path] == status) for status in ("ADD", "DELETE"))
    receipt = dict(POLICY["complexity_static"])
    receipt.update({
        "substantive_lines_total": sum(total),
        "production_loc_added": production_lines[0],
        "production_loc_removed": production_lines[1],
        "test_loc_added": test_lines[0],
        "test_loc_removed": test_lines[1],
        "production_files_added": len(added),
        "production_files_removed": len(removed),
        "modules_added": added,
    })
    need(not removed, "removed production surface differs")
    return receipt


def _dr30(outputs: dict[tuple[str, ...], bytes], head: str, total: int) -> dict[str, Any]:
    report = strict_json(outputs[VALIDATION_ARGV[6]])
    need(isinstance(report, dict), "Radon report differs")
    need(set(report) == {"governance/w00_checks.py"}, "Radon report differs")
    roots = report["governance/w00_checks.py"]
    need(isinstance(roots, list), "Radon block differs")
    blocks = roots + sum((item.get("closures", []) + item.get("methods", []) for item in roots), [])
    need(bool(blocks) and all(isinstance(item, dict) for item in blocks), "Radon block differs")
    source = blob(head, "governance/w00_checks.py").decode()
    lines = source.splitlines()
    values = (
        sum(bool(line.strip()) for line in lines),
        max(item["endline"] - item["lineno"] + 1 for item in blocks),
        max(item["complexity"] for item in blocks),
        max(map(len, lines)),
        3,
        "NONE" if total <= 650 else POLICY["target_excess"],
        "PASS",
    )
    return dict(zip(DR30_KEYS, values, strict=True))


def _check_dr30(metrics: dict[str, Any], total: int) -> None:
    target = "NONE" if total <= 650 else POLICY["target_excess"]
    observed = tuple(metrics.get(key) for key in DR30_KEYS[:5])
    valid = set(metrics) == set(DR30_KEYS) and all(
        isinstance(value, int) and value <= limit for value, limit in zip(observed, (500, 60, 10, 120, 3), strict=True)
    )
    need(valid and metrics.get("target_excess_justification") == target, "DR-30 evidence differs")
    need(metrics.get("simplicity_conformance") == "PASS", "simplicity evidence differs")


def validate_budget(metrics: dict[str, Any]) -> None:
    surface = set(metrics["modules_added"]) == PRODUCTION and metrics["substantive_lines_total"] <= 800
    limits = len(metrics["dependencies_added"]) <= 2 and len(metrics["public_contracts_changed"]) <= 1
    need(surface and limits and not metrics["migrations_added"], "W00A1a budget or surface differs")


def validate_project(base: str, head: str, branch: str) -> dict[str, Any]:
    activation(base, branch)
    paths = paths_at(base, head)
    need(all(path in ACTIVE_FILES or path.startswith("handoffs/W00/") for path in paths), "change is outside W00A1a")
    metrics = budget(base, head, paths)
    validate_budget(metrics)
    jsonschema.Draft202012Validator.check_schema(strict_json(blob(head, SCHEMA)))
    hashes = {**POLICY["trusted_hashes"], POLICY_PATH: POLICY_HASH}
    need(all(digest(blob(head, path)) == expected for path, expected in hashes.items()), "trusted files differ")
    return {"scope": "BOOTSTRAP_COMPATIBILITY_ONLY", "changed_paths": paths, **metrics}


def _record_files(commit: str, parent: str) -> tuple[str, tuple[str, str], set[str]] | None:
    lines = git("diff", "--name-status", "--no-renames", parent, commit, "--", "handoffs/W00/").splitlines()
    if not lines:
        return None
    need(all(line.startswith("A\t") for line in lines), "append-only record was changed")
    paths = [line.split("\t", 1)[1] for line in lines]
    pair = {match.group(2): (path, match.group(1)) for path in paths if (match := TURN.fullmatch(path))}
    need(set(pair) == {"json", "md"} and pair["json"][1] == pair["md"][1], "handoff pair differs")
    turn = pair["json"][1]
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
    outputs, reports = validate_record(
        record, object_at(head, SCHEMA), artifact_reader(head), evidence, implementation_time, completion_limit
    )
    need(record["changes"] == change_ledger(base, parent), "change ledger differs")
    paths = paths_at(base, head)
    metrics = budget(base, head, paths)
    validate_budget(metrics)
    need(record["complexity_receipt"] == metrics, "complexity receipt differs")
    actual_dr30 = _dr30(outputs, parent, metrics["substantive_lines_total"])
    need(reports["VALIDATION"]["dr30"] == actual_dr30, "DR-30 report differs")
    need(blob(head, pair[1]).decode() == render_markdown(record, parent), "Markdown differs")
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
