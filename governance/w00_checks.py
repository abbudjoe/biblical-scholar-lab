import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import PurePosixPath as _PurePosixPath
from typing import Any, cast

import jsonschema
import w00_contracts as contracts

BASE_SHA = contracts.BASE
ACTIVATION_PATH = "activations/ACT-W00-REPOSITORY-GOVERNANCE-v3.json"
ACTIVATION_HASH = "60def3ad374823a3c9065ad43deb6fb41b7ff079de52a212dc7c47c18d0d30c6"
PACKAGE = "governance/GOV-01-package-manifest.json"
CHECKSUMS = "governance/GOV-01-artifacts.sha256"
WORKFLOW = ".github/workflows/governance-integrity.yml"
WORKFLOW_HASH = "406f36d7102ac87da134a9ed817683344e89a12d2a50662504d7b716dd68dbdd"
SCHEMA = "governance/schemas/turn-handoff.schema.json"
DEPENDENCIES = {"actions/checkout", "pypi:jsonschema"}
PRODUCTION_NAMES = "ruff.toml w00_checks.py w00_contracts.py w00_yaml.rb".split()
PRODUCTION = {WORKFLOW, *(f"governance/{name}" for name in PRODUCTION_NAMES)}
RUNTIME_PACKAGE = PRODUCTION | {"governance/test_w00_checks.py", SCHEMA}
_PRIOR = """03e20dfb4692bad3f76710824e7535a4e6a59446 516254fff643371f4315376a4a2ee0f5aaaaad64 W00-SOL-20260817T234806Z
e5a7fb3ff3c20d7eebdcf73af1ba9c0b18084cab 80e52f0c4f91b3b0dc9314e73e7c270e34475927 W00-SOL-REPAIR01-20260818T021301Z
33ebbfdc07b8429e6b1f7a19132e118a476f4fb6 0adb60bd8daa307655b20ec87d11f35fa2590ce9 W00-SOL-REPAIR02-20260818T141853Z"""
PRIOR_HANDOFFS = tuple(tuple(row.split()) for row in _PRIOR.strip().splitlines())


def run(arguments: list[str], *, text: bool = True) -> subprocess.CompletedProcess[Any]:
    return subprocess.run(arguments, check=True, text=text, capture_output=True, timeout=30)


def git(*arguments: str) -> str:
    return cast(str, run(["git", *arguments]).stdout).strip()


def blob(revision: str, path: str) -> bytes:
    return cast(bytes, run(["git", "show", f"{revision}:{path}"], text=False).stdout)


def object_at(revision: str, path: str) -> dict[str, Any]:
    content = blob(revision, path)
    contracts.need(len(content) <= 262_144, f"{path} is oversized")
    value = contracts.strict_json(content)
    contracts.need(isinstance(value, dict), f"{path} is not an object")
    return cast(dict[str, Any], value)


def activation(base: str, branch: str) -> None:
    contracts.need((base, branch) == (BASE_SHA, contracts.BRANCH), "base or branch differs")
    digest = hashlib.sha256(blob(base, ACTIVATION_PATH)).hexdigest()
    contracts.need(digest == ACTIVATION_HASH, "activation hash differs")


def safe_path(path: str) -> None:
    pure = _PurePosixPath(path)
    unsafe = not path or pure.is_absolute() or str(pure) != path or ".." in pure.parts or "\\" in path
    unsafe = unsafe or len(path) > 240 or any(ord(character) < 32 or ord(character) == 127 for character in path)
    contracts.need(not unsafe, "path is unsafe")


def changed_paths(base: str, head: str) -> list[str]:
    command = ["git", "diff", "--no-renames", "--name-only", "-z", f"{base}...{head}"]
    content = cast(bytes, run(command, text=False).stdout)
    paths = [item.decode() for item in content.split(b"\0") if item]
    for path in paths:
        safe_path(path)
    return paths


def _diff_lines(base: str, head: str, paths: list[str] | None = None) -> tuple[int, int]:
    if paths == []:
        return 0, 0
    arguments = ["diff", "--no-renames", "--unified=0", f"{base}...{head}", *(("--", *paths) if paths else ())]
    additions = deletions = 0
    in_hunk = False
    for line in git(*arguments).splitlines():
        if line.startswith(("diff --git", "@@")):
            in_hunk = line.startswith("@@")
            continue
        if in_hunk and len(line) > 1 and line[1:].strip():
            additions += int(line.startswith("+"))
            deletions += int(line.startswith("-"))
    return additions, deletions


def _statuses(base: str, head: str) -> dict[str, str]:
    content = git("diff", "--no-renames", "--name-status", f"{base}...{head}")
    rows = [line.split("\t", 1) for line in content.splitlines()]
    contracts.need(all(status in {"A", "M", "D"} for status, _ in rows), "change status differs")
    return {path: status for status, path in rows}


def _is_migration(path: str) -> bool:
    return path.endswith(".sql") or bool({"migrations", "alembic"} & set(_PurePosixPath(path).parts))


def _is_production(path: str, excluded: set[str]) -> bool:
    governed = path.startswith("governance/") and path not in excluded
    return path.startswith(".github/workflows/") or governed and not path.endswith((".md", ".sha256"))


def _classify(paths: list[str]) -> tuple[set[str], set[str], set[str], set[str]]:
    migrations = {path for path in paths if _is_migration(path)}
    schemas = {path for path in paths if path.startswith("governance/schemas/")}
    tests = {path for path in paths if path.startswith(("governance/test_", "governance/fixtures/"))}
    excluded = tests | schemas | {PACKAGE, CHECKSUMS}
    production = {path for path in paths if _is_production(path, excluded)}
    return production, tests, schemas, migrations


def _public(head: str, production: set[str], schemas: set[str], statuses: dict[str, str]) -> set[str]:
    output = {f"schema:{path}" for path in schemas}
    for path in production:
        if path.endswith(".py") and statuses[path] != "D":
            output.update(contracts.class_surface(blob(head, path).decode()))
    return output


def budget(base: str, head: str, paths: list[str]) -> dict[str, Any]:
    production, tests, schemas, migrations = _classify(paths)
    contracts.need(schemas <= {SCHEMA}, "schema change is unclassified")
    statuses, workflows = _statuses(base, head), {path for path in paths if path.startswith(".github/workflows/")}
    added, removed = _diff_lines(base, head)
    production_lines, test_lines = _diff_lines(base, head, sorted(production)), _diff_lines(base, head, sorted(tests))
    public = _public(head, production, schemas, statuses)
    modules = {status: sorted(path for path in production if statuses[path] == status) for status in ("A", "D")}
    return {
        "substantive_lines_total": added + removed,
        "production_loc_added": production_lines[0],
        "production_loc_removed": production_lines[1],
        "test_loc_added": test_lines[0],
        "test_loc_removed": test_lines[1],
        "generated_loc": 0,
        "production_files": sorted(production),
        "production_files_added": len(modules["A"]),
        "production_files_removed": len(modules["D"]),
        "modules_added": modules["A"],
        "modules_removed": modules["D"],
        "tables_added": [],
        "endpoints_added": [],
        "dependencies_added": sorted(DEPENDENCIES if workflows else set()),
        "dependencies_removed": [],
        "external_validation_tools": contracts.EXTERNAL_TOOLS,
        "public_contracts_changed": sorted(public),
        "workflow_files": sorted(workflows),
        "migrations_added": sorted(migrations),
        "cli_commands_added": sorted(contracts.cli_surface(blob(head, "governance/w00_checks.py").decode())),
    }


def validate_budget(metrics: dict[str, Any]) -> None:
    keys = "production_files dependencies_added public_contracts_changed migrations_added".split()
    actual = (metrics["substantive_lines_total"], *(len(metrics[key]) for key in keys))
    limits = (1200, 12, 2, 3, 0)
    contracts.need(all(value <= limit for value, limit in zip(actual, limits, strict=True)), "W00A1 budget exceeded")
    expected = (PRODUCTION, {WORKFLOW}, {"project-integrity", "turn-handoff-integrity"})
    surface = (set(metrics["production_files"]), set(metrics["workflow_files"]), set(metrics["cli_commands_added"]))
    contracts.need(surface == expected, "W00A1 surface differs")


def _checksums(source: str) -> dict[str, str]:
    output = {}
    for line in source.splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\n]+)", line)
        contracts.need(match is not None, "checksum sidecar is malformed")
        digest, path = cast(re.Match[str], match).groups()
        safe_path(path)
        contracts.need(path not in output, "checksum path is duplicated")
        output[path] = digest
    return output


def validate_package(revision: str) -> None:
    manifest, entries = object_at(revision, PACKAGE), _checksums(blob(revision, CHECKSUMS).decode())
    files = manifest.get("files")
    identity = manifest.get("artifact_id"), manifest.get("status"), manifest.get("file_count")
    contracts.need(
        isinstance(files, list) and identity == ("GOV-01", "APPROVED", len(files)), "package identity differs"
    )
    seen = set()
    for item in cast(list[Any], files):
        contracts.need(isinstance(item, dict) and set(item) == {"path", "sha256", "bytes"}, "package entry differs")
        content, path = blob(revision, item["path"]), item["path"]
        digest = hashlib.sha256(content).hexdigest()
        expected = digest, len(content), digest
        contracts.need(
            path not in seen and (item["sha256"], item["bytes"], entries.get(path)) == expected,
            f"package mismatch: {path}",
        )
        seen.add(path)
    for path, digest in entries.items():
        contracts.need(hashlib.sha256(blob(revision, path)).hexdigest() == digest, f"checksum mismatch: {path}")
    contracts.need(seen | {PACKAGE} <= set(entries), "checksum membership differs")
    contracts.need(entries[PACKAGE] == hashlib.sha256(blob(revision, PACKAGE)).hexdigest(), "manifest checksum differs")
    baseline = {item["path"] for item in object_at(BASE_SHA, PACKAGE)["files"]}
    required = baseline | (RUNTIME_PACKAGE if revision != BASE_SHA else set())
    contracts.need(required <= seen, "package membership differs")


def validate_yaml(source: bytes) -> None:
    contracts.need(len(source) <= 262_144 and not re.search(rb"[\x00-\x08\x0b-\x1f\x7f]", source), "YAML bytes differ")
    result = subprocess.run(["ruby", "governance/w00_yaml.rb"], input=source, capture_output=True, timeout=5)
    contracts.need(result.returncode == 0, "YAML semantics are invalid")


def validate_workflow(source: bytes) -> None:
    validate_yaml(source)
    contracts.need(hashlib.sha256(source).hexdigest() == WORKFLOW_HASH, "workflow policy differs")


def _validate_sources(head: str, metrics: dict[str, Any]) -> None:
    for path in metrics["production_files"]:
        if path in metrics["modules_removed"]:
            continue
        source = blob(head, path)
        markers = (part.replace("|", "").encode() for part in "TO|DO FIX|ME NotImplemented|Error place|holder".split())
        unfinished = re.search(rb"\b(?:" + b"|".join(markers) + rb")\b", source, re.IGNORECASE)
        contracts.need(not unfinished, f"unfinished marker: {path}")
        if path.endswith(".py"):
            contracts.validate_python(path, source.decode())


def validate_project(base: str, head: str, branch: str) -> dict[str, Any]:
    activation(base, branch)
    paths = changed_paths(base, head)
    allowed = RUNTIME_PACKAGE | {PACKAGE, CHECKSUMS}
    contracts.need(
        all(path in allowed or path.startswith("handoffs/W00/") for path in paths), "change is outside W00A1"
    )
    metrics = budget(base, head, paths)
    validate_budget(metrics)
    validate_package(head)
    jsonschema.Draft202012Validator.check_schema(contracts.strict_json(blob(head, SCHEMA)))
    _validate_sources(head, metrics)
    validate_workflow(blob(head, WORKFLOW))
    return {"changed_paths": paths, **metrics}


def _history(base: str, head: str) -> list[tuple[str, str]]:
    rows = [line.split() for line in git("rev-list", "--reverse", "--parents", f"{base}..{head}").splitlines()]
    contracts.need(all(len(row) == 2 for row in rows), "candidate history contains a merge")
    return [(row[0], row[1]) for row in rows]


def _final_commit(head: str, pairs: list[tuple[str, str, tuple[str, str]]]) -> tuple[str, str, tuple[str, str]]:
    times = [_PurePosixPath(item[2][0]).stem.rsplit("-", 1)[-1] for item in pairs]
    contracts.need(times == sorted(set(times)), "handoff chronology differs")
    contracts.need(bool(pairs) and pairs[-1][0] == head, "live head is not the final handoff commit")
    commit, parent, pair = pairs[-1]
    prior = parent in {item[0] for item in PRIOR_HANDOFFS} or _pair(parent, git("rev-parse", f"{parent}^")) is not None
    contracts.need(not prior, "implementation head is a handoff commit")
    changed = set(git("diff-tree", "--no-commit-id", "--name-only", "-r", parent, commit).splitlines())
    contracts.need(changed == set(pair), "final commit contains implementation changes")
    return commit, parent, pair


def _pair(commit: str, parent: str) -> tuple[str, str] | None:
    lines = git(
        "diff-tree", "--no-commit-id", "--name-status", "--no-renames", "-r", parent, commit, "--", "handoffs/W00/"
    ).splitlines()
    if not lines:
        return None
    contracts.need(all(line.startswith("A\t") for line in lines), "handoff was edited, deleted, renamed, or replaced")
    paths = [line.split("\t", 1)[1] for line in lines]
    stems = {str(_PurePosixPath(path).with_suffix("")) for path in paths}
    suffixes = {_PurePosixPath(path).suffix for path in paths}
    contracts.need((len(paths), len(stems), suffixes) == (2, 1, {".md", ".json"}), "handoff pair differs")
    return next(path for path in paths if path.endswith(".json")), next(path for path in paths if path.endswith(".md"))


def _prior(head: str) -> None:
    for commit, parent, turn in PRIOR_HANDOFFS:
        ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", commit, head], capture_output=True)
        ancestry = ancestor.returncode == 0 and git("rev-parse", f"{commit}^") == parent
        contracts.need(ancestry, "prior handoff ancestry differs")
        for suffix in (".md", ".json"):
            path = f"handoffs/W00/{turn}{suffix}"
            contracts.need(blob(head, path) == blob(commit, path), f"prior handoff changed: {path}")


def _receipt(record: dict[str, Any], metrics: dict[str, Any]) -> None:
    receipt = record["complexity_receipt"]
    prose = set(
        "abstractions simpler_alternatives_considered known_duplication_or_debt waivers simplicity_conformance".split()
    )
    measured = set(receipt) - prose
    matches = measured <= set(metrics) and all(receipt[key] == metrics[key] for key in measured)
    contracts.need(matches, "complexity receipt differs")


def _render_markdown(record: dict[str, Any], parent: str) -> str:
    facts = {key: record[key] for key in ("billable_actions", "merge_performed", "next_task_started", "status")}
    declaration = "W00A1 implements only the local governance kernel and the project-integrity / "
    declaration += "turn-handoff-integrity defense checks. W00A2 trusted candidate validation, W00B owner "
    declaration += "authorization, and W01 merge-only proof are absent and remain unauthorized."
    prefix = f"{declaration} Parent: {parent}. Status: {record['status']}. <!-- BSL_TERMINAL_FACTS_V1 -->"
    return f"{prefix}\n```json\n{json.dumps(facts, sort_keys=True, separators=(',', ':'))}\n```\n"


def _markdown(revision: str, path: str, record: dict[str, Any], parent: str) -> None:
    contracts.need(blob(revision, path).decode() == _render_markdown(record, parent), "Markdown differs")


def _required_commands(record: dict[str, Any], parent: str) -> None:
    observed = {tuple(item["argv"]) for item in record["commands"] if item["result"] == "PASS"}
    command = f"python3 governance/w00_checks.py project-integrity --base-sha {BASE_SHA}"
    command += f" --head-sha {parent} --branch {contracts.BRANCH}"
    project = (*contracts.UV_PYTHON, *command.split())
    auth = ("gh", "auth", "status", "--active", "--hostname", "github.com")
    contracts.need(set(contracts.VALIDATION_ARGV) | {project, auth} <= observed, "required command evidence is absent")


def validate_handoff(base: str, head: str, branch: str, pr_url: str) -> dict[str, Any]:
    activation(base, branch)
    contracts.need(pr_url == contracts.PR_URL, "PR URL differs")
    _prior(head)
    pairs = [(commit, parent, pair) for commit, parent in _history(base, head) if (pair := _pair(commit, parent))]
    contracts.need([item[0] for item in pairs[:-1]] == [item[0] for item in PRIOR_HANDOFFS], "handoff order differs")
    commit, parent, pair = _final_commit(head, pairs)
    record = object_at(head, pair[0])
    contracts.validate_handoff(record, object_at(head, SCHEMA))
    stem = _PurePosixPath(pair[0]).stem
    bound = record["turn_id"] == stem and record["implementation_head_sha"] == parent
    contracts.need(bound, "handoff parent or name differs")
    metrics = budget(base, head, changed_paths(base, head))
    validate_budget(metrics)
    _required_commands(record, parent)
    _receipt(record, metrics)
    _markdown(head, pair[1], record, parent)
    return dict(turn_id=stem, implementation_head_sha=parent, json=pair[0], markdown=pair[1], status=record["status"])


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


def dispatch(arguments: argparse.Namespace) -> Any:
    if arguments.check == "project-integrity":
        return validate_project(arguments.base_sha, arguments.head_sha, arguments.branch)
    return validate_handoff(arguments.base_sha, arguments.head_sha, arguments.branch, arguments.pr_url)


def main() -> int:
    try:
        result = dispatch(parser().parse_args())
    except Exception:
        print('{"status":"failure"}')
        return 1
    print(json.dumps({"status": "success", "result": result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
