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

ACTIVATION, START = "ACT-W00-REPOSITORY-GOVERNANCE-v3", "20c2755bd5be2b080f78a9529792c83f0cd9c400"
ACTIVATION_PATH, TEST = "activations/ACT-W00-REPOSITORY-GOVERNANCE-v3.json", "governance/test_w00_checks.py"
SCHEMA, REGISTRY = "governance/schemas/w00a1a-handoff.schema.json", "governance/handoff-registry.json"
WORKFLOW, CODE = ".github/workflows/governance-integrity.yml", "governance/w00_checks.py"
WORKFLOW_SHA = "372ebcfd646c9ac4e8e1105a79ed7d4b4dc5bf32e6b02720b594c744eee8f02e"
ACTIVE = {WORKFLOW, CODE, TEST, SCHEMA, REGISTRY}
IMMUTABLE = set("governance/schemas/turn-handoff.schema.json governance/GOV-01-artifacts.sha256 ".split())
IMMUTABLE.add("governance/GOV-01-package-manifest.json")
REMOVED = {f"governance/fixtures/w00a1a-{name}.json" for name in ("policy", "record", "negative")}
REMOVED.add("governance/ruff.toml")
EVIDENCE_ROOT, COVERAGE = "handoffs/W00/evidence", "--data-file=/tmp/bsl-w00a1a-repair05.coverage"
TURN = re.compile(r"^W00-SOL(?:-REPAIR\d+)?-[0-9]{8}T[0-9]{6}Z$")
SHA = re.compile(r"^[0-9a-f]{40}$")
SAFE = re.compile(r"^[A-Za-z0-9._/-]+$")
STAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
Obj = dict[str, Any]
Reader = Callable[[str], bytes]
ARTIFACTS: tuple[tuple[str, str], ...] = (("COMPLEXITY", "complexity.json"), ("BINARY_DIFF", "implementation.diff"))
ARTIFACTS += (("REVIEW_INSTRUCTION", "review.prompt.md"), ("REVIEW_REPORT_RECORD", "review.report.json"))
STOP = (
    "No merge was performed. No approval was submitted. The PR remains draft. No ready transition occurred. "
    "No W00A1b, W00A2, W00B, or W01 work was started. No source acquisition or benchmark execution occurred. "
    "No model, cloud, Lambda, Luna, training, evaluation, or billable work occurred. "
    "The next action belongs to ChatGPT exact-head review and Joseph's decision."
)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def strict_json(source: str | bytes) -> Any:
    def unique(items: list[tuple[str, Any]]) -> Obj:
        need(len(items) == len(dict(items)), "duplicate JSON key")
        return dict(items)

    def finite(value: str) -> float:
        need(math.isfinite(number := float(value)), "nonfinite JSON number")
        return number

    return json.loads(source, object_pairs_hook=unique, parse_constant=finite, parse_float=finite)


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def utc(value: str) -> datetime:
    need(STAMP.fullmatch(value) is not None, "timestamp is not canonical UTC")
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)


def safe_path(path: str) -> None:
    pure = PurePosixPath(path)
    valid = path and str(pure) == path and not pure.is_absolute() and ".." not in pure.parts
    need(bool(valid and "\\" not in path and SAFE.fullmatch(path) and len(path) <= 240), "unsafe path")


def run(arguments: list[str], *, text: bool = True) -> subprocess.CompletedProcess[Any]:
    return subprocess.run(arguments, check=True, text=text, capture_output=True, timeout=60)


def git(*arguments: str) -> str:
    return cast(str, run(["git", *arguments]).stdout).strip()


def blob(revision: str, path: str) -> bytes:
    return cast(bytes, run(["git", "show", f"{revision}:{path}"], text=False).stdout)


def object_at(revision: str, path: str) -> Obj:
    content = reader(revision)(path)
    need(len(content) <= 262_144, f"{path} is oversized")
    value = strict_json(content)
    need(isinstance(value, dict), f"{path} is not an object")
    return cast(Obj, value)


def reader(revision: str) -> Reader:
    def read(path: str) -> bytes:
        safe_path(path)
        entry = git("ls-tree", revision, "--", path)
        need(entry.startswith("100644 blob ") and entry.endswith(f"\t{path}"), "path is not a regular Git blob")
        return blob(revision, path)

    return read


def identity(base: str, head: str, branch: str) -> None:
    need(all(SHA.fullmatch(value) for value in (base, head)), "invalid Git SHA")
    need(re.fullmatch(r"codex/[A-Za-z0-9._/-]+", branch) is not None, "invalid task branch")
    ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", base, head], capture_output=True)
    need(ancestor.returncode == 0, "base is not an ancestor of head")
    activation = object_at(base, ACTIVATION_PATH)
    root = cast(Obj, activation.get("root_turn", {}))
    observed = activation.get("activation_id"), activation.get("status"), root.get("task_id")
    need(observed == (ACTIVATION, "APPROVED", "W00"), "base activation differs")


def handoff_snapshot(revision: str) -> dict[str, str]:
    paths = git("ls-tree", "-r", "--name-only", revision, "--", "handoffs/W00").splitlines()
    read = reader(revision)
    return {path: digest(read(path)) for path in paths}


def handoff_entries(revision: str) -> list[dict[str, str]]:
    snapshot = handoff_snapshot(revision)
    direct = {path for path in snapshot if path.count("/") == 2}
    turns = sorted({path.removeprefix("handoffs/W00/").rsplit(".", 1)[0] for path in direct})
    expected = {f"handoffs/W00/{turn}.{suffix}" for turn in turns for suffix in ("json", "md")}
    need(direct == expected and all(TURN.fullmatch(turn) for turn in turns), "handoff pair or path differs")
    entries = []
    for turn in turns:
        json_path, markdown_path = (f"handoffs/W00/{turn}.{suffix}" for suffix in ("json", "md"))
        entry = {"turn_id": turn, "json_path": json_path, "json_sha256": snapshot[json_path]}
        entry |= {"markdown_path": markdown_path, "markdown_sha256": snapshot[markdown_path]}
        entries.append(entry)
    return entries


def registry_entries(revision: str, data: Obj) -> list[dict[str, str]]:
    entries = handoff_entries(revision)
    need(bool(entries) and data == {"schema_version": "bsl.handoff-registry.v1", "entries": entries}, "registry")
    return entries


def validate_registry(base: str, head: str) -> tuple[str, list[dict[str, str]]]:
    candidate = registry_entries(head, object_at(head, REGISTRY))
    present = subprocess.run(["git", "cat-file", "-e", f"{base}:{REGISTRY}"], capture_output=True).returncode == 0
    if not present:
        return "BOOTSTRAP", candidate
    registry_entries(base, object_at(base, REGISTRY))
    return "APPEND", candidate


def change_ledger(base: str, head: str) -> list[Obj]:
    kinds = {"A": "ADD", "M": "MODIFY", "D": "DELETE"}
    changes = []
    for row in git("diff", "--no-renames", "--name-status", f"{base}...{head}").splitlines():
        status, path = row.split("\t", 1)
        safe_path(path)
        need(status in kinds, "unsupported diff status")
        reason = "IMMUTABLE_HANDOFF_HISTORY" if path.startswith("handoffs/W00/") else "W00A1A_IMPLEMENTATION"
        changes.append({"kind": kinds[status], "reason": reason, "path": path})
    return changes


def diff_lines(base: str, head: str, paths: set[str]) -> tuple[int, int]:
    output = git("diff", "--no-renames", "--unified=0", f"{base}...{head}", "--", *sorted(paths))
    added = removed = 0
    hunk = False
    for line in output.splitlines():
        if line.startswith(("diff --git", "@@")):
            hunk = line.startswith("@@")
        elif hunk and len(line) > 1 and line[1:].strip():
            added += int(line.startswith("+"))
            removed += int(line.startswith("-"))
    return added, removed


def budget(base: str, head: str) -> Obj:
    production, tests = diff_lines(base, head, ACTIVE - {TEST}), diff_lines(base, head, {TEST})
    lines = {path: blob(head, path).decode().splitlines() for path in ACTIVE}
    readable = all(
        sum(bool(line.strip()) for line in value) > 1 for path, value in lines.items() if path.endswith(".json")
    )
    longest = max(len(line) for value in lines.values() for line in value)
    total = sum(production + tests)
    need(readable and longest <= 120 and total <= 800, "readability or W00A1a budget differs")
    names = ("production_loc_added", "production_loc_removed", "test_loc_added", "test_loc_removed")
    receipt: Obj = {"substantive_lines_total": total, **dict(zip(names, production + tests, strict=True))}
    receipt["production_files"] = len(ACTIVE - {TEST})
    return receipt | {"public_contracts": 1, "workflows": 1, "migrations": 0}


def command_suite(base: str, head: str, branch: str) -> list[tuple[str, ...]]:
    commands = [
        f"uv run --with=jsonschema==4.25.1 --with=coverage==7.10.6 python3 -B -m coverage run "
        f"{COVERAGE} --branch -m unittest {TEST}",
        f"uv run --with=coverage==7.10.6 python3 -B -m coverage report "
        f"{COVERAGE} --format=total --fail-under=90 {CODE}",
        f"uvx ruff@0.16.3 check --quiet --preview --line-length 120 --select E4,E7,E9,F,B,C90,PLR1702 "
        f"--config lint.mccabe.max-complexity=10 --config lint.pylint.max-nested-blocks=3 {CODE} {TEST}",
        f"uvx ruff@0.16.3 format --quiet --check --preview --line-length 120 "
        f"--config format.skip-magic-trailing-comma=true {CODE} {TEST}",
        f"uvx mypy@2.3.1 --strict --no-error-summary --ignore-missing-imports {CODE}",
        f"uvx zizmor@1.29.0 --offline -q {WORKFLOW}",
        f"uvx radon@6.0.1 cc -j {CODE}",
        "shasum -a 256 -s -c governance/GOV-01-artifacts.sha256",
        f"git diff --check {base}...{head}",
        f"uv run --with=jsonschema==4.25.1 python3 {CODE} project-integrity "
        f"--base-sha {base} --head-sha {head} --branch {branch}",
        "git fsck --full",
        "git status --porcelain",
    ]
    return [tuple(command.split()) for command in commands]


def load_evidence(turn: str, item: Obj, suffix: str, read: Reader, used: set[str]) -> bytes:
    path, expected = item["path"], item["sha256"]
    safe_path(path)
    valid = path.startswith(f"{EVIDENCE_ROOT}/{turn}/") and path.endswith(suffix) and path not in used
    need(valid, "invalid or reused evidence path")
    used.add(path)
    content = read(path)
    need(len(content) <= 262_144 and digest(content) == expected, "evidence hash differs")
    return content


def validate_commands(record: Obj, read: Reader, used: set[str], at: datetime) -> bytes:
    commands = record["commands"]
    suite = command_suite(record["base_sha"], record["implementation_head_sha"], record["branch"])
    need([tuple(item["argv"]) for item in commands] == suite, "authoritative command suite differs")
    need([item["command_index"] for item in commands] == list(range(1, len(commands) + 1)), "command order differs")
    need(len({item["evidence_id"] for item in commands}) == len(commands), "command evidence ID is reused")
    turn = record["root_turn_id"]
    identity_values = turn, record["activation_id"], record["implementation_head_sha"]
    previous, completed = at, utc(record["completed_at_utc"])
    radon = b""
    for item in commands:
        identity_fields = item["root_turn_id"], item["activation_id"], item["implementation_head_sha"]
        need(identity_fields == identity_values, "command identity differs")
        started, finished = utc(item["started_at_utc"]), utc(item["finished_at_utc"])
        need(previous <= started <= finished <= completed, "command chronology differs")
        previous = started
        receipt = load_evidence(turn, item["receipt"], ".receipt.json", read, used)
        envelope = {key: value for key, value in item.items() if key != "receipt"}
        need(strict_json(receipt) == envelope, "command receipt differs")
        stdout = load_evidence(turn, item["stdout"], ".stdout", read, used)
        stderr = load_evidence(turn, item["stderr"], ".stderr", read, used)
        if tuple(item["argv"]) == ("git", "status", "--porcelain"):
            need(not stdout and not stderr, "worktree was not clean")
        if tuple(item["argv"][:3]) == ("uvx", "radon@6.0.1", "cc"):
            radon = stdout
    return radon


def source_metrics(head: str, output: bytes) -> Obj:
    report = strict_json(output)
    roots = report.get(CODE) if isinstance(report, dict) else None
    need(isinstance(roots, list) and bool(roots), "Radon report differs")
    blocks = cast(list[Obj], roots)
    blocks += sum((item.get("closures", []) + item.get("methods", []) for item in blocks), [])
    return {
        "module_nonblank_lines": sum(bool(line.strip()) for line in blob(head, CODE).decode().splitlines()),
        "maximum_function_lines": max(item["endline"] - item["lineno"] + 1 for item in blocks),
        "maximum_cyclomatic_complexity": max(item["complexity"] for item in blocks),
        "maximum_observed_line_length": max(
            len(line) for path in ACTIVE for line in blob(head, path).decode().splitlines()
        ),
    }


def complexity(base: str, head: str, radon: bytes) -> Obj:
    measured = budget(base, head)
    measured |= source_metrics(head, radon)
    limits = {"module_nonblank_lines": 500, "maximum_function_lines": 60}
    limits |= {"maximum_cyclomatic_complexity": 10, "maximum_observed_line_length": 120}
    need(all(measured[name] <= limit for name, limit in limits.items()), "DR-30 source limit differs")
    target = "NONE" if measured["substantive_lines_total"] <= 650 else "ABOVE_TARGET_SMALLEST_READABLE_KERNEL"
    return {
        "measured": measured,
        "configured": {"max_cyclomatic_complexity": 10, "max_line_length": 120, "nesting_limit": 3},
        "target_excess_justification": target,
    }


def validate_project_history(base: str, head: str, mode: str, entries: list[dict[str, str]]) -> set[str]:
    anchor = START if mode == "BOOTSTRAP" else base
    prior = handoff_entries(anchor)
    if entries == prior:
        need(handoff_snapshot(head) == handoff_snapshot(anchor), "handoff history changed")
        return set()
    need(entries[:-1] == prior and len(entries) == len(prior) + 1, "unexpected handoff append")
    turn, parent = entries[-1]["turn_id"], git("rev-parse", f"{head}^")
    need(turn.startswith("W00-SOL-REPAIR05-"), "unexpected handoff turn")
    need(registry_entries(parent, object_at(parent, REGISTRY)) == prior, "implementation registry differs")
    need(handoff_snapshot(parent) == handoff_snapshot(anchor), "handoff history changed")
    return record_scope(parent, head, entries[-1], turn)


def validate_project(base: str, head: str, branch: str) -> Obj:
    identity(base, head, branch)
    paths = {item["path"] for item in change_ledger(base, head)}
    in_scope = all(path in ACTIVE or path.startswith("handoffs/W00/") for path in paths)
    need(in_scope and all(blob(base, path) == blob(head, path) for path in IMMUTABLE), "scope differs")
    removed = (subprocess.run(["git", "cat-file", "-e", f"{head}:{path}"], capture_output=True) for path in REMOVED)
    need(all(item.returncode != 0 for item in removed), "minified fixture remains")
    jsonschema.Draft202012Validator.check_schema(object_at(head, SCHEMA))
    mode, entries = validate_registry(base, head)
    validate_project_history(base, head, mode, entries)
    need(digest(blob(head, WORKFLOW)) == WORKFLOW_SHA, "workflow differs")
    return {"scope": "BOOTSTRAP_COMPATIBILITY_ONLY", **budget(base, head)}


def validate_review(record: Obj, artifacts: dict[str, bytes]) -> None:
    review = cast(Obj, record["independent_review"])
    rendered = json.dumps(review, indent=2, sort_keys=True) + "\n"
    need(artifacts["REVIEW_REPORT_RECORD"].decode() == rendered, "structured review differs")
    base, head = record["base_sha"], record["implementation_head_sha"]
    binary = cast(bytes, run(["git", "diff", "--binary", f"{base}...{head}"], text=False).stdout)
    expected = base, head, git("rev-parse", f"{head}^{{tree}}"), digest(binary)
    keys = "base_sha", "implementation_head_sha", "implementation_tree_sha", "diff_sha256"
    need(tuple(review[key] for key in keys) == expected, "review Git identity differs")
    items = record["artifacts"]
    need(review["review_instruction"] == items["REVIEW_INSTRUCTION"], "review instruction differs")
    need(artifacts["REVIEW_INSTRUCTION"].decode() == render_review_instruction(record), "review prompt differs")
    required = ACTIVE | IMMUTABLE
    required |= {item[field]["path"] for item in record["commands"] for field in ("receipt", "stdout", "stderr")}
    required |= {record["github_auth"]["receipt"]["path"], items["COMPLEXITY"]["path"], items["BINARY_DIFF"]["path"]}
    need(required == set(review["artifacts_inspected"]), "review artifact set differs")
    blocking = (item for item in review["findings"] if item["severity"] in {"P0", "P1", "P2"})
    need(all(item["status"] == "CLOSED" for item in blocking), "review has unresolved finding")
    finished = max(utc(item["finished_at_utc"]) for item in record["commands"])
    started, completed = utc(review["started_at_utc"]), utc(review["completed_at_utc"])
    need(finished <= started <= completed <= utc(record["completed_at_utc"]), "review chronology differs")


def render_review_instruction(record: Obj) -> str:
    review = record["independent_review"]
    instruction = {"contract": "BIBLICAL_SCHOLAR_LAB_W00A1A_REPAIR05", "acceptance": "ZERO_UNRESOLVED_P0_P1_P2"}
    instruction |= {"implementation": record["implementation_head_sha"], "tree": review["implementation_tree_sha"]}
    instruction |= {"base": record["base_sha"], "binary_diff_sha256": review["diff_sha256"]}
    instruction["review_inputs"] = review["artifacts_inspected"]
    return json.dumps(instruction, indent=2, sort_keys=True) + "\n"


def render_markdown(record: Obj) -> str:
    canonical = json.dumps(record, indent=2, sort_keys=True)
    return f"# W00A1a Repair05 — Durable Handoff Contract\n\n```json\n{canonical}\n```\n\n{STOP}\n"


def validate_record(record: Obj, schema: Obj, read: Reader, paths: set[str], at: datetime, limit: datetime) -> None:
    jsonschema.Draft202012Validator(schema).validate(record)
    schema_hash = digest(blob(record["implementation_head_sha"], SCHEMA))
    need(record["integrity"]["schema_sha256"] == schema_hash, "schema hash differs")
    started, completed = utc(record["started_at_utc"]), utc(record["completed_at_utc"])
    need(started <= at <= completed <= limit, "root-turn chronology differs")
    used: set[str] = set()
    radon = validate_commands(record, read, used, at)
    names = {key: item["path"].rsplit("/", 1)[-1] for key, item in record["artifacts"].items()}
    need(names == dict(ARTIFACTS), "artifact set differs")
    artifacts = {
        artifact_id: load_evidence(record["root_turn_id"], item, PurePosixPath(item["path"]).suffix, read, used)
        for artifact_id, item in record["artifacts"].items()
    }
    auth_data = record["github_auth"]
    auth = {key: value for key, value in auth_data.items() if key != "receipt"}
    auth_content = load_evidence(record["root_turn_id"], auth_data["receipt"], ".auth.json", read, used)
    need(strict_json(auth_content) == auth and used == paths, "authentication receipt differs")
    measured = complexity(record["base_sha"], record["implementation_head_sha"], radon)
    observed = record["complexity_receipt"], strict_json(artifacts["COMPLEXITY"])
    need(observed == (measured, measured), "complexity differs")
    need(digest(artifacts["BINARY_DIFF"]) == record["independent_review"]["diff_sha256"], "diff artifact differs")
    validate_review(record, artifacts)


def record_scope(parent: str, head: str, entry: dict[str, str], turn: str) -> set[str]:
    pair = {entry["json_path"], entry["markdown_path"]}
    rows = git("diff", "--name-status", "--no-renames", parent, head).splitlines()
    evidence = {row.split("\t", 1)[1] for row in rows} - pair - {REGISTRY}
    statuses = f"M\t{REGISTRY}" in rows and all(row.startswith("A\t") or row == f"M\t{REGISTRY}" for row in rows)
    prefix = f"{EVIDENCE_ROOT}/{turn}/"
    need(statuses and all(path.startswith(prefix) for path in evidence), "final commit is not record-only")
    return evidence


def validate_handoff(base: str, head: str, branch: str, pr_url: str) -> Obj:
    identity(base, head, branch)
    parent = git("rev-parse", f"{head}^")
    mode, final_entries = validate_registry(base, head)
    evidence = validate_project_history(base, head, mode, final_entries)
    entry, turn = final_entries[-1], final_entries[-1]["turn_id"]
    record = object_at(head, entry["json_path"])
    keys = "root_turn_id", "base_sha", "implementation_head_sha", "branch", "pr_url"
    need(tuple(record[key] for key in keys) == (turn, base, parent, branch, pr_url), "handoff identity differs")
    registry_values = record["integrity"]["registry_mode"], record["integrity"]["registry_entry_count"]
    registry_ok = registry_values == (mode, len(final_entries))
    need(registry_ok and record["changes"] == change_ledger(base, parent), "receipt differs")
    implemented = datetime.fromisoformat(git("show", "-s", "--format=%cI", parent))
    final_time = datetime.fromisoformat(git("show", "-s", "--format=%cI", head))
    validate_record(record, object_at(head, SCHEMA), reader(head), evidence, implemented, final_time)
    need(blob(head, entry["markdown_path"]).decode() == render_markdown(record), "Markdown differs")
    return {"turn_id": turn, "implementation_head_sha": parent, "status": record["status"]}


def main() -> None:
    check = sys.argv[1] if len(sys.argv) > 1 else ""
    functions = {"project-integrity": validate_project, "turn-handoff-integrity": validate_handoff}
    function = cast(Callable[..., Obj], functions.get(check))
    need(function is not None, "unknown check")
    flags = ["--base-sha", "--head-sha", "--branch"] + (["--pr-url"] if check == "turn-handoff-integrity" else [])
    arguments = sys.argv[2:]
    need(arguments[::2] == flags and len(arguments) == 2 * len(flags), "CLI differs")
    print(json.dumps({"status": "success", "result": function(*arguments[1::2])}, sort_keys=True))


if __name__ == "__main__":
    main()
