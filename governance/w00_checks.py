from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, cast

import w00_contracts as contracts
from w00_contracts import ContractError, need

ACTIVATION_PATH, ACTIVATION_HASH, BASE_SHA, CODEOWNERS_SHA = ("activations/ACT-W00-REPOSITORY-GOVERNANCE-v3.json", "60def3ad374823a3c9065ad43deb6fb41b7ff079de52a212dc7c47c18d0d30c6", "3d3ebb706fe6c8779445cbbfd9fea271b86d3646", "b87a860ad3725a955fecdfb3a85c265f8048faaa")
PACKAGE = "governance/GOV-01-package-manifest.json"
CHECKSUMS = "governance/GOV-01-artifacts.sha256"
WORKFLOWS = {".github/workflows/governance-integrity.yml", ".github/workflows/trusted-governance-validator.yml"}
WORKFLOW_HASHES = {".github/workflows/governance-integrity.yml": "b7a6e8e879834ce821f7f1c4092f59ed4a68307dfcbf4051ff703420fa5ddf6a", ".github/workflows/trusted-governance-validator.yml": "4781eb2e8fb7febad2d15663404c4ab01f046dcd08d52fc29e60cbbeb3f6672a"}
PRODUCTION = {*WORKFLOWS, "governance/ruff.toml", "governance/w00_contracts.py", "governance/w00_checks.py"}
PUBLIC_CONTRACTS = ("TrustedGovernanceValidationReceipt", "W00ABootstrapState", "schema:governance/schemas/turn-handoff.schema.json")
TRUSTED_FILES = (".github/workflows/trusted-governance-validator.yml", "governance/w00_contracts.py", "governance/w00_checks.py")
LIMITS = {"tree_entries": 512, "tree_bytes": 16_777_216, "files": 128, "file_bytes": 524_288, "changed_bytes": 4_194_304, "commits": 64, "json_depth": 32}
REQUIRED_EVALUATIONS = {"unit-and-adversarial", "branch-coverage", "formatter", "linter", "strict-typing", "workflow-static-security", "dependency-and-secret-scan", "package-integrity", "project-integrity", "live-governance", "independent-review"}
REQUIRED_HANDOFF_COMMANDS = {" ".join(command) for command in contracts.VALIDATION_COMMANDS if command[:3] != ["uvx", "ruff", "format"]} | {" ".join(contracts.VALIDATION_COMMANDS[6]), "git diff --check", "git fsck --full"}
CLI_SPECS = {"project-integrity": ("base-sha", "head-sha", "branch"), "turn-handoff-integrity": ("base-sha", "head-sha", "branch", "pr-url"), "package-integrity": ("revision",), "candidate-metadata": ("base-sha", "head-sha", "tree-json", "compare-json")}
CLI_SPECS.update({"trusted-governance": ("repository", "pr-number", "base-sha", "head-sha", "trusted-revision", "branch", "event", "run-id", "run-attempt", "candidate-repository", "tree-json", "compare-json", "output"), "completion-integrity": ("base-sha", "head-sha", "branch", "pr-json", "comments-json"), "live-governance": ("expected-head", "review-limit-observed-at", "environment-ui-observed-at")})
PRIOR_HANDOFFS = (
    ("03e20dfb4692bad3f76710824e7535a4e6a59446", "516254fff643371f4315376a4a2ee0f5aaaaad64", {"handoffs/W00/W00-SOL-20260817T234806Z.md": "c1ce6a9f4849cc9280045e2825d38b794027fce8eb59e8d0facb94b238cafdd6", "handoffs/W00/W00-SOL-20260817T234806Z.json": "1a48f94e97651175c9689ea99fa9b824ad4751ce42414951da00467288a6ee07"}),
    ("e5a7fb3ff3c20d7eebdcf73af1ba9c0b18084cab", "80e52f0c4f91b3b0dc9314e73e7c270e34475927", {"handoffs/W00/W00-SOL-REPAIR01-20260818T021301Z.md": "b05bbd1f56d2d6df2175f2ea9ef2ab954ed022b48080b97aded2878dd68b105e", "handoffs/W00/W00-SOL-REPAIR01-20260818T021301Z.json": "42339bc0be5da1c6d74699e86fea88677e2202c521cde14e906d497f98c246e4"}),
)
PRIOR_COMPLETIONS = {"W00-SOL-20260817T234806Z": (5321637400, "03e20dfb4692bad3f76710824e7535a4e6a59446"), "W00-SOL-REPAIR01-20260818T021301Z": (5322636121, "e5a7fb3ff3c20d7eebdcf73af1ba9c0b18084cab")}


def run(arguments: list[str], *, text: bool = True, input_data: str | bytes | None = None, timeout: int | None = None, check: bool = True) -> subprocess.CompletedProcess[Any]:
    return subprocess.run(arguments, check=check, text=text, capture_output=True, input=input_data, timeout=timeout)


def command(repository: str | None, *arguments: str) -> list[str]:
    return ["git", *(("-C", repository) if repository else ()), *arguments]


def git(repository: str | None, *arguments: str) -> str:
    return cast(str, run(command(repository, *arguments)).stdout).strip()


def blob(repository: str | None, revision: str, path: str) -> bytes:
    return cast(bytes, run(command(repository, "show", f"{revision}:{path}"), text=False).stdout)


def object_at(repository: str | None, revision: str, path: str) -> dict[str, Any]:
    value = contracts.strict_json(blob(repository, revision, path))
    need(isinstance(value, dict), f"{path} is not a JSON object")
    return cast(dict[str, Any], value)


def activation(repository: str | None, revision: str, branch: str) -> dict[str, Any]:
    names = git(repository, "ls-tree", "-r", "--name-only", revision, "--", "activations").splitlines()
    candidates = []
    for path in names:
        if not path.endswith(".json"):
            continue
        record = object_at(repository, revision, path)
        if record.get("status") == "APPROVED" and record.get("root_turn", {}).get("task_branch") == branch:
            contracts.validate_activation(record)
            candidates.append((record, path))
    need(len(candidates) == 1, "one base-approved activation is required")
    record, path = candidates[0]
    ancestor = run(command(repository, "merge-base", "--is-ancestor", record["approved_design_commit"], revision), check=False)
    need(ancestor.returncode == 0, "approved design commit is not in the trusted base")
    if record["activation_id"] == contracts.ACTIVATION:
        need(path == ACTIVATION_PATH and hashlib.sha256(blob(repository, revision, path)).hexdigest() == ACTIVATION_HASH, "W00 activation hash differs")
    return record


def changed_paths(base: str, head: str, repository: str | None = None) -> list[str]:
    raw = cast(bytes, run(command(repository, "diff", "--no-renames", "--name-only", "-z", f"{base}...{head}"), text=False).stdout)
    return [item.decode() for item in raw.split(b"\0") if item]


def safe_path(path: str) -> None:
    pure = PurePosixPath(path)
    unsafe = not path or pure.is_absolute() or str(pure) != path or any(part in {"", ".", ".."} for part in pure.parts) or "\\" in path or len(path) > 240 or any(ord(character) < 32 or ord(character) == 127 for character in path)
    need(not unsafe and not path.lower().endswith((".zip", ".tar", ".gz", ".tgz", ".7z", ".rar")), "candidate path is unsafe")


def _diff_lines(base: str, head: str, repository: str | None, paths: list[str] | None = None) -> tuple[int, int]:
    if paths == []:
        return 0, 0
    arguments = ["diff", "--no-renames", "--unified=0", f"{base}...{head}", *(("--", *paths) if paths else ())]
    source, additions, deletions, hunk = (git(repository, *arguments), 0, 0, False)
    for line in source.splitlines():
        if line.startswith("diff --git"):
            hunk = False
            continue
        if line.startswith("@@"):
            hunk = True
            continue
        if not hunk or len(line) <= 1 or not line[1:].strip():
            continue
        additions += int(line.startswith("+"))
        deletions += int(line.startswith("-"))
    return additions, deletions


def _dependencies(repository: str | None, revision: str, workflows: set[str]) -> set[str]:
    output: set[str] = set()
    for path in workflows:
        try:
            source = blob(repository, revision, path).decode()
        except subprocess.CalledProcessError:
            continue
        output.update(item.split("@", 1)[0] for item in re.findall(r"uses:\s*([^\s]+@[^\s]+)", source))
    return output


def _record_types(repository: str | None, revision: str, production: set[str], schemas: set[str]) -> set[str]:
    output = {f"schema:{path}" for path in schemas}
    for path in (item for item in production if item.endswith(".py")):
        tree = ast.parse(blob(repository, revision, path).decode(), filename=path)
        need(not {node.name for node in tree.body if isinstance(node, ast.ClassDef) and not node.name.startswith("_")} - ({"ContractError", "CommandPhase"} if path == "governance/w00_contracts.py" else set()), "public Python class is unclassified")
        output.update(value.value for node in ast.walk(tree) if isinstance(node, ast.Dict) for key, value in zip(node.keys, node.values, strict=True) if isinstance(key, ast.Constant) and key.value in {"receipt_type", "state_type"} and isinstance(value, ast.Constant) and isinstance(value.value, str))
    return output


def _statuses(base: str, head: str, paths: list[str], repository: str | None) -> dict[str, str]:
    rows = [line.split("\t", 1) for line in git(repository, "diff", "--no-renames", "--name-status", f"{base}...{head}").splitlines()]
    for status, path in rows:
        safe_path(path)
    output = {path: status for status, path in rows if status in {"A", "M", "D"}}
    need(len(output) == len(rows), "candidate change status differs")
    need(set(output) == set(paths), "candidate change set differs")
    return output


def budget(base: str, head: str, paths: list[str], repository: str | None = None) -> dict[str, Any]:
    names = {PurePosixPath(path).name for path in paths}
    manifests = {name for name in names if name in {"pyproject.toml", "setup.py", "setup.cfg", "package.json", "Cargo.toml", "go.mod", "Pipfile", "Gemfile", "pom.xml", "build.gradle", "composer.json"} or name.startswith("requirements") or name.endswith((".lock", "-lock.json"))}
    need(not manifests, "dependency manifest change is unclassified")
    schemas = {path for path in paths if path.startswith("governance/schemas/")}
    need(schemas <= {"governance/schemas/turn-handoff.schema.json"}, "public schema change is unclassified")
    additions, deletions = _diff_lines(base, head, repository)
    workflows = {path for path in paths if path.startswith(".github/workflows/")}
    migrations = {path for path in paths if path.endswith(".sql") or "migrations" in PurePosixPath(path).parts or {"alembic", "versions"} <= set(PurePosixPath(path).parts)}
    dependencies = _dependencies(repository, head, workflows) - _dependencies(repository, base, workflows)
    tests = {path for path in paths if path.startswith(("governance/test_", "governance/fixtures/"))}
    production = {path for path in paths if path in workflows or path.startswith("governance/") and path not in tests and not path.startswith("governance/schemas/") and PurePosixPath(path).suffix not in {".md", ".sha256"}} - {PACKAGE}
    statuses, production_lines, test_lines = _statuses(base, head, paths, repository), _diff_lines(base, head, repository, sorted(production)), _diff_lines(base, head, repository, sorted(tests))
    metrics = {"additions": additions, "deletions": deletions, "production_loc_added": production_lines[0], "production_loc_removed": production_lines[1], "test_loc_added": test_lines[0], "test_loc_removed": test_lines[1], "production_files": sorted(production), "production_added": sorted(path for path in production if statuses[path] == "A"), "production_removed": sorted(path for path in production if statuses[path] == "D")}
    metrics.update({"test_files": sorted(tests), "governance_files": sorted(path for path in paths if path.startswith("governance/")), "dependencies": sorted(dependencies), "public_contracts": sorted(_record_types(repository, head, production, schemas)), "workflows": sorted(workflows), "migrations": sorted(migrations), "cli_commands": sorted(contracts.cli_surface(ast.parse(blob(repository, head, "governance/w00_checks.py").decode())) if statuses.get("governance/w00_checks.py") == "A" else ())})
    return metrics


def validate_budget(metrics: dict[str, Any], record: dict[str, Any]) -> None:
    limits = record["budgets"]
    actual = (metrics["additions"] + metrics["deletions"], len(metrics["production_files"]), len(metrics["dependencies"]), len(metrics["public_contracts"]), len(metrics["migrations"]))
    maximum = (limits["substantive_changed_lines_hard_limit"], limits["handwritten_production_files_hard_limit"], limits["new_direct_dependencies_hard_limit"], limits["new_public_contracts_hard_limit"], limits["migrations_hard_limit"])
    need(all(value <= limit for value, limit in zip(actual, maximum, strict=True)), "an activation budget is exceeded")
    need(record["activation_id"] != contracts.ACTIVATION or (set(metrics["workflows"]), set(metrics["production_files"]), set(metrics["public_contracts"]), set(metrics["cli_commands"])) == (WORKFLOWS, PRODUCTION, set(PUBLIC_CONTRACTS), {*CLI_SPECS, "command-policy"}), "W00A activated surface differs")


def validate_package(repository: str | None, revision: str, baseline: str = BASE_SHA) -> dict[str, Any]:
    manifest, entries = (object_at(repository, revision, PACKAGE), _checksums(blob(repository, revision, CHECKSUMS).decode()))
    files = manifest.get("files")
    need((manifest.get("artifact_id"), manifest.get("status")) == ("GOV-01", "APPROVED") and isinstance(files, list) and manifest.get("file_count") == len(files), "package manifest identity differs")
    files = cast(list[Any], files)
    seen: set[str] = set()
    for item in files:
        need(isinstance(item, dict) and isinstance(item.get("path"), str), "package entry is malformed")
        path, content = item["path"], blob(repository, revision, item["path"])
        safe_path(path)
        need(path not in seen, "package manifest path is duplicated")
        seen.add(path)
        digest = hashlib.sha256(content).hexdigest()
        need((item.get("sha256"), item.get("bytes"), entries.get(path)) == (digest, len(content), digest), f"package manifest mismatch: {path}")
    for path, digest in entries.items():
        need(hashlib.sha256(blob(repository, revision, path)).hexdigest() == digest, f"package checksum mismatch: {path}")
    need(PACKAGE in entries, "package manifest lacks a sidecar binding")
    trusted_manifest = object_at(repository, baseline, PACKAGE).get("files")
    need(isinstance(trusted_manifest, list), "baseline package manifest is malformed")
    required_files = {item.get("path") for item in cast(list[Any], trusted_manifest) if isinstance(item, dict)}
    required_checksums = set(_checksums(blob(repository, baseline, CHECKSUMS).decode()))
    need(required_files <= seen and required_checksums <= entries.keys(), "governed package membership was removed")
    return {"manifest_files": len(files), "checksum_files": len(entries), "manifest_paths": sorted(seen), "checksum_paths": sorted(entries)}


def _checksums(source: str) -> dict[str, str]:
    output: dict[str, str] = {}
    for line in source.splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\n]+)", line)
        need(match is not None, "checksum sidecar is malformed")
        digest, path = cast(re.Match[str], match).groups()
        safe_path(path)
        need(path not in output, "checksum path is duplicated")
        output[path] = digest
    return output


def validate_project(base: str, head: str, branch: str, repository: str | None = None) -> dict[str, Any]:
    record, paths = (activation(repository, base, branch), changed_paths(base, head, repository))
    allowed = record["activated_paths"]
    need(not [path for path in paths if not any(path == item or item.endswith("/") and path.startswith(item) for item in allowed)], "change is outside activation scope")
    need(not any(path.startswith(("design/", "activations/", "benchmark/", "sources/")) for path in paths), "immutable content changed")
    metrics = budget(base, head, paths, repository)
    validate_budget(metrics, record)
    validate_package(repository, base, base)
    validate_package(repository, head, base)
    for path in metrics["production_files"]:
        source = blob(repository, head, path).decode()
        need(not re.search(r"\b(?:TO" + "DO|FIX" + "ME|Not" + "ImplementedError|place" + "holder)\b", source, re.IGNORECASE), f"unfinished marker: {path}")
        if path.endswith(".py"):
            contracts.validate_python(path, source)
    if record["activation_id"] == contracts.ACTIVATION:
        observed = {path: hashlib.sha256(blob(repository, head, path)).hexdigest() for path in WORKFLOWS}
        need(observed == WORKFLOW_HASHES, "workflow content differs from the audited version")
        need(not git(repository, "ls-tree", "-r", "--name-only", head, "--", ".github/workflows/owner-merge-authorization.yml"), "W00B owner workflow remains executable")
    return {"changed_paths": paths, **metrics}


def _tree_item(item: Any) -> int:
    need(isinstance(item, dict) and isinstance(item.get("path"), str), "candidate tree entry is malformed")
    safe_path(item["path"])
    if item.get("type") == "tree":
        need(item.get("mode") == "040000", "candidate directory mode differs")
        return 0
    size = item.get("size")
    need(item.get("type") == "blob" and item.get("mode") in {"100644", "100755"}, "candidate contains a symlink, submodule, or special file")
    need(isinstance(size, int) and 0 <= size <= LIMITS["file_bytes"], "candidate file is oversized")
    return cast(int, size)


def validate_metadata(tree: dict[str, Any], compare: dict[str, Any], base: str, head: str) -> dict[str, Any]:
    entries, commits, files, base_commit, merge_base = (tree.get("tree"), compare.get("commits"), compare.get("files"), compare.get("base_commit"), compare.get("merge_base_commit"))
    need(tree.get("truncated") is False and isinstance(entries, list), "candidate tree metadata differs")
    entries = cast(list[Any], entries)
    need(len(entries) <= LIMITS["tree_entries"] and sum(_tree_item(item) for item in entries) <= LIMITS["tree_bytes"], "candidate tree bound exceeded")
    candidate_commits, base_record, merge_record = cast(list[dict[str, Any]], commits), cast(dict[str, Any], base_commit), cast(dict[str, Any], merge_base)
    try:
        count, last = len(candidate_commits), candidate_commits[-1]
        identity = (last["sha"], last["commit"]["tree"]["sha"], base_record["sha"], merge_record["sha"], compare.get("total_commits"))
    except (AttributeError, IndexError, KeyError, TypeError) as error:
        raise ContractError("candidate commit metadata is malformed") from error
    need(0 < count <= LIMITS["commits"] and identity == (head, tree.get("sha"), base, base, count), "candidate ancestry or commit bound differs")
    names = _compare_paths(files)
    return {"paths": names, "tree_entries": len(entries), "changed_files": len(names)}


def _compare_paths(files: Any) -> list[str]:
    need(isinstance(files, list) and len(files) <= LIMITS["files"], "candidate file-count bound exceeded")
    names: list[str] = []
    for item in files:
        need(isinstance(item, dict) and isinstance(item.get("filename"), str) and item.get("status") in {"added", "modified", "removed"}, "candidate compare entry differs")
        safe_path(item["filename"])
        names.append(item["filename"])
    need(len(names) == len(set(names)), "candidate paths are duplicated")
    return names


def _json_depth(value: Any, depth: int = 0) -> int:
    need(depth <= LIMITS["json_depth"], "candidate JSON nesting is excessive")
    children = value.values() if isinstance(value, dict) else value if isinstance(value, list) else ()
    return max([depth, *(_json_depth(item, depth + 1) for item in children)])


def _content(path: str, content: bytes) -> None:
    if not path.endswith((".json", ".md", ".py", ".yml", ".yaml")):
        return
    text = content.decode()
    need(not re.search(r"[\x00-\x08\x0b-\x1f\x7f]", text), "candidate contains log-control bytes")
    if path.endswith(".json"):
        _json_depth(contracts.strict_json(text))
    if path.endswith(".py"):
        ast.parse(text, filename=path)
    if path.endswith((".yml", ".yaml")):
        script = "require 'yaml'; s=STDIN.read; d=Psych.parse_stream(s); raise unless d.children.length==1; w=nil; w=->(n){if n.is_a?(Psych::Nodes::Mapping); k=n.children.each_slice(2).map(&:first); raise unless k.all?{|x| x.is_a?(Psych::Nodes::Scalar)} && k.map(&:value).uniq.length==k.length; end; Array(n.children).each{|c| w.call(c)}}; w.call(d); YAML.safe_load(s, permitted_classes: [], permitted_symbols: [], aliases: false)"
        result = run(["ruby", "-e", script], text=False, input_data=content, timeout=5, check=False)
        need(result.returncode == 0, "candidate YAML is malformed")


def inspect_candidate(repository: str, base: str, head: str, tree: dict[str, Any], compare: dict[str, Any]) -> dict[str, Any]:
    metadata = validate_metadata(tree, compare, base, head)
    ancestry = run(command(repository, "merge-base", "--is-ancestor", base, head), check=False)
    need(ancestry.returncode == 0, "candidate head is not based on the reported base")
    paths, total = changed_paths(base, head, repository), 0
    need(set(paths) == set(metadata["paths"]), "prefetch metadata and candidate diff differ")
    for path in paths:
        listing = git(repository, "ls-tree", head, "--", path)
        if not listing:
            continue
        meta, listed = listing.split("\t", 1)
        mode, kind, object_id = meta.split()
        need((listed, kind, mode) == (path, "blob", mode) and mode in {"100644", "100755"}, "candidate blob identity differs")
        size = int(git(repository, "cat-file", "-s", object_id))
        need(size <= LIMITS["file_bytes"], "candidate blob is oversized")
        content = cast(bytes, run(command(repository, "cat-file", "blob", object_id), text=False).stdout)
        total += len(content)
        need(total <= LIMITS["changed_bytes"], "candidate changed-byte bound exceeded")
        _content(path, content)
    return {"changed_files": len(paths), "changed_bytes": total, "execution": "NONE"}


def _history(repository: str | None, base: str, head: str) -> list[tuple[str, str]]:
    output = []
    for line in git(repository, "rev-list", "--reverse", "--parents", f"{base}..{head}").splitlines():
        fields = line.split()
        need(len(fields) == 2, "candidate history contains a merge")
        output.append((fields[0], fields[1]))
    return output


def _pair(repository: str | None, commit: str, parent: str, prefix: str = "handoffs/W00/") -> tuple[str, str] | None:
    lines = git(repository, "diff-tree", "--no-commit-id", "--name-status", "--no-renames", "-r", parent, commit, "--", prefix).splitlines()
    if not lines:
        return None
    need(all(line.startswith("A\t") for line in lines), "handoff was edited, deleted, renamed, or replaced")
    paths = [line.split("\t", 1)[1] for line in lines]
    stems, suffixes = ({str(PurePosixPath(path).with_suffix("")) for path in paths}, {PurePosixPath(path).suffix for path in paths})
    need((len(paths), len(stems), suffixes) == (2, 1, {".md", ".json"}), "handoff commit is not one complete pair")
    return next(path for path in paths if path.endswith(".json")), next(path for path in paths if path.endswith(".md"))


def _prior(repository: str | None, head: str) -> None:
    for commit, parent, files in PRIOR_HANDOFFS:
        ancestry = run(command(repository, "merge-base", "--is-ancestor", commit, head), check=False)
        need(ancestry.returncode == 0 and git(repository, "rev-parse", f"{commit}^") == parent, "prior handoff ancestry differs")
        for path, digest in files.items():
            current = blob(repository, head, path)
            need(current == blob(repository, commit, path) and hashlib.sha256(current).hexdigest() == digest, f"prior handoff changed: {path}")


def validate_handoff(base: str, head: str, branch: str, pr_url: str, repository: str | None = None) -> dict[str, Any]:
    active = activation(repository, base, branch)
    task, is_w00a = (active["root_turn"]["task_id"], active["activation_id"] == contracts.ACTIVATION)
    prefix = f"handoffs/{task}/"
    if is_w00a:
        _prior(repository, head)
    turns = _append_only_turns(repository, base, head, prefix, is_w00a)
    _, parent, pair, record = turns[-1]
    mutation_owner = _w00a_mutation(turns) if is_w00a else None
    need(_pair(repository, parent, git(repository, "rev-parse", f"{parent}^"), prefix) is None, "implementation head is itself a handoff commit")
    expected = (active["activation_id"], task, branch, base, pr_url, contracts.REPOSITORY)
    need(tuple(record[key] for key in ("activation_id", "task_id", "branch", "base_sha", "pr_url", "repository")) == expected, "handoff binding differs")
    metrics = budget(base, head, changed_paths(base, head, repository), repository)
    validate_budget(metrics, active)
    _handoff_receipt(record, metrics)
    _handoff_commands(record, branch, pr_url, mutation_owner is record)
    _handoff_markdown(repository, head, pair[1], parent, record["status"], is_w00a)
    return {"turn_id": record["turn_id"], "json": pair[0], "markdown": pair[1], "implementation_head_sha": parent, "status": record["status"]}


def _append_only_turns(repository: str | None, base: str, head: str, prefix: str, w00a: bool) -> list[tuple[str, str, tuple[str, str], dict[str, Any]]]:
    turns, identifiers = [], set()
    for commit, parent in _history(repository, base, head):
        pair = _pair(repository, commit, parent, prefix)
        if pair is None:
            continue
        record = object_at(repository, commit, pair[0])
        contracts.validate_handoff(record, w00a=w00a and commit == head)
        need(record["turn_id"] not in identifiers and {PurePosixPath(path).stem for path in pair} == {record["turn_id"]}, "handoff turn ID is reused or misnamed")
        need(record["implementation_head_sha"] == parent, "handoff implementation parent differs")
        need(set(git(repository, "diff-tree", "--no-commit-id", "--name-only", "-r", parent, commit).splitlines()) == set(pair), "handoff commit contains other changes")
        identifiers.add(record["turn_id"])
        turns.append((commit, parent, pair, record))
    need(bool(turns) and turns[-1][0] == head, "live head is not the final handoff commit")
    return turns


def _w00a_mutation(turns: list[tuple[str, str, tuple[str, str], dict[str, Any]]]) -> dict[str, Any]:
    matches = [(record, item) for _, _, _, record in turns for item in record["commands"] if item.get("phase") == contracts.CommandPhase.W00A_GOVERNANCE.value]
    need(len(matches) == 1, "W00A governance exception must be consumed exactly once")
    record, item = matches[0]
    exact = {"phase", "command", "exit_status", "result", "input"}
    need(item.keys() == exact and item["exit_status"] == 0 and contracts.assess_command(item["command"], contracts.CommandPhase.W00A_GOVERNANCE, governance_available=True, governance_payload=item["input"])[0], "W00A governance receipt differs")
    return record


def _handoff_receipt(record: dict[str, Any], metrics: dict[str, Any]) -> None:
    receipt = record["complexity_receipt"]
    counts = {"production_loc_added": metrics["production_loc_added"], "production_loc_removed": metrics["production_loc_removed"], "test_loc_added": metrics["test_loc_added"], "test_loc_removed": metrics["test_loc_removed"], "production_files_added": len(metrics["production_added"]), "production_files_removed": len(metrics["production_removed"]), "generated_loc": 0}
    need(all(receipt[key] == value for key, value in counts.items()), "handoff complexity counts differ")
    for key, value in (("modules_added", metrics["production_added"]), ("modules_removed", metrics["production_removed"]), ("dependencies_added", metrics["dependencies"]), ("dependencies_removed", []), ("public_contracts_changed", metrics["public_contracts"]), ("migrations_added", metrics["migrations"]), ("cli_commands_added", metrics["cli_commands"]), ("tables_added", []), ("endpoints_added", [])):
        need(sorted(receipt[key]) == sorted(value), f"handoff complexity field differs: {key}")


def _command_evidence(item: dict[str, Any], branch: str, number: int, allow_mutation: bool) -> None:
    need(item.get("phase") in {phase.value for phase in contracts.CommandPhase}, "handoff command phase differs")
    phase = contracts.CommandPhase(item["phase"])
    fields = {"phase", "command", "exit_status", "result"} | ({"input"} if phase is contracts.CommandPhase.W00A_GOVERNANCE else set())
    payload = item.get("input") if phase is contracts.CommandPhase.W00A_GOVERNANCE else None
    need(item.keys() == fields and isinstance(item.get("command"), str) and item.get("exit_status") == 0 and isinstance(item.get("result"), str) and bool(item["result"].strip()) and contracts.assess_command(item["command"], phase, branch=branch, pr_number=number, governance_available=allow_mutation, governance_payload=payload)[0], "handoff command evidence differs")


def _handoff_commands(record: dict[str, Any], branch: str, pr_url: str, allow_mutation: bool) -> None:
    number = int(pr_url.rsplit("/", 1)[1])
    need(bool(record["commands"]), "handoff command evidence is absent")
    for item in record["commands"]:
        _command_evidence(item, branch, number, allow_mutation)
    evaluations = record["evaluations"]
    need(all(item.keys() == {"name", "status", "evidence"} and isinstance(item.get("evidence"), str) and bool(item["evidence"].strip()) and item.get("status") in {"PASS", "PASS_WITH_REVIEW"} for item in evaluations), "handoff evaluation evidence differs")
    names = [item["name"] for item in evaluations]
    need(len(names) == len(set(names)) and REQUIRED_EVALUATIONS <= set(names), "required W00A evaluation evidence is absent")
    need(REQUIRED_HANDOFF_COMMANDS <= {item["command"] for item in record["commands"]} and all(any(item["command"].startswith(f"python3 governance/w00_checks.py {check} ") for item in record["commands"]) for check in ("project-integrity", "turn-handoff-integrity", "package-integrity", "live-governance")) and any(item["command"] == "gh auth status --active --hostname github.com" for item in record["commands"]), "required W00A command evidence is absent")


def _handoff_markdown(repository: str | None, head: str, path: str, parent: str, status: str, w00a: bool) -> None:
    markdown = blob(repository, head, path).decode()
    phrases = ("Required GitHub Actions checks are defense-in-depth evidence and are not treated as proof of trusted workflow provenance.", "The trusted base-controlled validator becomes operational from main only after W00A is manually merged.", "Owner authorization, receipt consumption, and the merge-only path are not active after W00A and require W00B.")
    required = (*phrases, contracts.TITLE) if w00a else ()
    need(all(item in markdown for item in (*required, parent, status)), "handoff declaration differs")
    prohibited = (*contracts.PROHIBITED_CLAIMS, "owner authorization is active", "merge-only path is active", "safe to merge")
    need(not any(item.lower() in markdown.lower() for item in prohibited), "handoff makes a prohibited capability claim")


def _load(path: str) -> Any:
    return contracts.strict_json(Path(path).read_bytes())


def _comments(path: str) -> list[dict[str, Any]]:
    value = _load(path)
    value = [entry for page in value for entry in page] if isinstance(value, list) and value and all(isinstance(item, list) for item in value) else value
    need(isinstance(value, list) and all(isinstance(item, dict) for item in value), "comments are malformed")
    return cast(list[dict[str, Any]], value)


def validate_completion(base: str, head: str, branch: str, pr_file: str, comments_file: str, repository: str | None = None) -> dict[str, Any]:
    pr, comments, url = (_load(pr_file), _comments(comments_file), f"https://github.com/{contracts.REPOSITORY}/pull/1")
    need(isinstance(pr, dict), "PR evidence is malformed")
    actual = (pr.get("number"), pr.get("state"), pr.get("draft"), pr.get("html_url"), pr.get("base", {}).get("ref"), pr.get("base", {}).get("sha"), pr.get("base", {}).get("repo", {}).get("full_name"), pr.get("head", {}).get("ref"), pr.get("head", {}).get("sha"), pr.get("head", {}).get("repo", {}).get("full_name"))
    need(actual == (1, "open", True, url, "main", base, contracts.REPOSITORY, branch, head, contracts.REPOSITORY), "live PR identity differs")
    handoff = validate_handoff(base, head, branch, url, repository)
    prefix = f"https://github.com/{contracts.REPOSITORY}/blob/{head}/"
    expected = (contracts.ACTIVATION, "W00", handoff["turn_id"], handoff["implementation_head_sha"], head, prefix + handoff["markdown"], prefix + handoff["json"], handoff["status"], "CHATGPT_REVIEW")
    comment_id, completed_at = contracts.current_completion(comments, expected)
    indexed = {item[0].get("turn_id"): (item[1], item[0].get("live_pr_head_sha")) for item in contracts.marked(comments, contracts.COMPLETION)}
    need(all(indexed.get(turn) == identity for turn, identity in PRIOR_COMPLETIONS.items()), "prior completion comment differs")
    state = contracts.validate_record_order(comments, completed_at, (url, contracts.ACTIVATION, base, head), prefix + handoff["json"])
    return {"completion_comment_id": comment_id, "live_pr_head_sha": head, "state": state}


def content_hash(repository: str | None, revision: str) -> str:
    digest = hashlib.sha256()
    for path in TRUSTED_FILES:
        content = blob(repository, revision, path)
        digest.update(path.encode() + b"\0" + str(len(content)).encode() + b"\0" + content)
    return digest.hexdigest()


def _receipt_hash(record: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps({key: item for key, item in record.items() if key != "receipt_hash"}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def create_receipt(arguments: argparse.Namespace) -> dict[str, Any]:
    identity = (arguments.repository, arguments.event, arguments.base_sha, arguments.pr_number)
    need(identity[:3] == (contracts.REPOSITORY, "pull_request_target", arguments.trusted_revision) and identity[3] > 0, "trusted workflow identity differs")
    tree, compare = _load(arguments.tree_json), _load(arguments.compare_json)
    need(isinstance(tree, dict) and isinstance(compare, dict), "candidate metadata is malformed")
    inert = inspect_candidate(arguments.candidate_repository, arguments.base_sha, arguments.head_sha, tree, compare)
    project = validate_project(arguments.base_sha, arguments.head_sha, arguments.branch, arguments.candidate_repository)
    url = f"https://github.com/{contracts.REPOSITORY}/pull/{arguments.pr_number}"
    handoff = validate_handoff(arguments.base_sha, arguments.head_sha, arguments.branch, url, arguments.candidate_repository)
    record = {"schema_version": "1.0", "receipt_type": "TrustedGovernanceValidationReceipt", "repository": contracts.REPOSITORY, "pr_number": arguments.pr_number, "inspected_head_sha": arguments.head_sha, "base_sha": arguments.base_sha, "trusted_validator_revision": arguments.trusted_revision, "workflow_path": ".github/workflows/trusted-governance-validator.yml", "workflow_run_id": arguments.run_id, "workflow_run_attempt": arguments.run_attempt, "event": arguments.event}
    record.update({"validator_content_hash": content_hash(None, arguments.trusted_revision), "handoff_path": handoff["json"], "handoff_sha256": hashlib.sha256(blob(arguments.candidate_repository, arguments.head_sha, handoff["json"])).hexdigest(), "validation_results": {"candidate_input_safety": "PASS", "project_integrity": "PASS", "turn_handoff_integrity": "PASS", "package_integrity": "PASS"}, "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "conclusion": "success"})
    record["receipt_hash"] = _receipt_hash(record)
    need(all(contracts.DIGEST.fullmatch(record[key]) for key in ("validator_content_hash", "handoff_sha256", "receipt_hash")), "trusted receipt digest differs")
    Path(arguments.output).write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return {"receipt": record, "inert_input": inert, "project_additions": project["additions"]}


def _api(endpoint: str) -> dict[str, Any]:
    value = contracts.strict_json(run(["gh", "api", endpoint]).stdout)
    need(isinstance(value, dict), "GitHub response is not an object")
    return cast(dict[str, Any], value)


def _ruleset(record: dict[str, Any]) -> None:
    identity = tuple(record.get(key) for key in ("id", "name", "target", "enforcement", "bypass_actors", "current_user_can_bypass"))
    need(identity == (20960975, "main-quality-and-authorization-gates", "branch", "active", [], "never"), "ruleset identity differs")
    need(record.get("conditions", {}).get("ref_name") == {"exclude": [], "include": ["~DEFAULT_BRANCH"]}, "ruleset target differs")
    items = record.get("rules")
    need(isinstance(items, list) and all(isinstance(item, dict) for item in items), "ruleset rules are malformed")
    items = cast(list[dict[str, Any]], items)
    rules = {item.get("type"): item for item in items}
    need(len(rules) == len(items) and set(rules) == {"deletion", "non_fast_forward", "required_linear_history", "pull_request", "required_status_checks"}, "ruleset protections differ")
    pull, status = (rules["pull_request"].get("parameters", {}), rules["required_status_checks"].get("parameters", {}))
    pull_values = tuple(pull.get(key) for key in ("required_approving_review_count", "dismiss_stale_reviews_on_push", "require_code_owner_review", "require_last_push_approval", "required_review_thread_resolution", "allowed_merge_methods"))
    contexts = {(item.get("context"), item.get("integration_id")) for item in status.get("required_status_checks", [])}
    need(pull_values == (0, True, False, False, True, ["squash"]) and (status.get("strict_required_status_checks_policy"), status.get("do_not_enforce_on_create")) == (True, False), "PR or status rule differs")
    need(contexts == {(name, 15368) for name in ("project-integrity", "turn-handoff-integrity")}, "required checks differ")


def _environment(record: dict[str, Any]) -> None:
    reviewers = [item for item in record.get("protection_rules", []) if isinstance(item, dict) and item.get("type") == "required_reviewers"]
    reviewer = reviewers[0] if len(reviewers) == 1 else {}
    identities = [(item.get("type"), item.get("reviewer", {}).get("login"), item.get("reviewer", {}).get("id")) for item in reviewer.get("reviewers", [])]
    need((record.get("id"), record.get("name"), record.get("can_admins_bypass"), reviewer.get("id"), reviewer.get("prevent_self_review"), identities) == (20070063288, contracts.ENVIRONMENT, False, 62973311, False, [("User", "abbudjoe", 43298060)]), "future environment differs")


def _check_runs(record: dict[str, Any], head: str) -> None:
    runs = record.get("check_runs")
    need(isinstance(runs, list) and record.get("total_count") == len(runs) and len(runs) <= 100, "check-run state is incomplete")
    for name in ("project-integrity", "turn-handoff-integrity"):
        matches = [item for item in cast(list[Any], runs) if isinstance(item, dict) and item.get("name") == name and isinstance(item.get("app"), dict) and item["app"].get("id") == 15368]
        need(bool(matches), f"required defense check is absent: {name}")
        latest = max(matches, key=lambda item: item.get("id", -1))
        need((latest.get("head_sha"), latest.get("status"), latest.get("conclusion")) == (head, "completed", "success"), f"required defense check differs: {name}")


def _codeowners(record: dict[str, Any], errors: dict[str, Any]) -> None:
    need((record.get("path"), record.get("encoding"), record.get("sha")) == (".github/CODEOWNERS", "base64", CODEOWNERS_SHA) and isinstance(record.get("content"), str), "default-branch CODEOWNERS response differs")
    required = {"*", "/.github/", "/AGENTS.md", "/EXPERIMENT_AUTHORITY.md", "/governance/", "/activations/", "/handoffs/", "/reviews/", "/contracts/", "/migrations/", "/benchmark/"}
    lines = [line.split() for line in base64.b64decode("".join(cast(str, record["content"]).split()), validate=True).decode().splitlines() if line.strip() and not line.lstrip().startswith("#")]
    need(len(lines) == len(required) and {parts[0] for parts in lines if parts[1:] == ["@abbudjoe"]} == required and errors.get("errors") == [], "CODEOWNERS differs")


def validate_live(head: str, review_at: str, environment_at: str, review_limit: bool, admin_disabled: bool) -> dict[str, str]:
    for observed_at in (review_at, environment_at):
        need(0 <= (datetime.now(timezone.utc) - contracts.timestamp(observed_at)).total_seconds() <= 86_400, "UI observation is stale or future-dated")
    need(review_limit and admin_disabled, "UI-only governance settings are unconfirmed")
    prefix = f"repos/{contracts.REPOSITORY}"
    repo, rules, environment = (_api(prefix), _api(f"{prefix}/rulesets/{contracts.RULESET}"), _api(f"{prefix}/environments/{contracts.ENVIRONMENT}"))
    settings = tuple(repo.get(key) for key in ("default_branch", "visibility", "allow_squash_merge", "allow_merge_commit", "allow_rebase_merge", "allow_auto_merge", "delete_branch_on_merge"))
    need(settings == ("main", "public", True, False, False, False, True), "repository merge settings differ")
    _ruleset(rules)
    _environment(environment)
    codeowners, errors = (_api(f"{prefix}/contents/.github/CODEOWNERS?ref=main"), _api(f"{prefix}/codeowners/errors"))
    _codeowners(codeowners, errors)
    workflows, pr, checks = (_api(f"{prefix}/actions/workflows?per_page=100"), _api(f"{prefix}/pulls/1"), _api(f"{prefix}/commits/{head}/check-runs?per_page=100"))
    need(isinstance(workflows.get("workflows"), list) and all(isinstance(item, dict) for item in workflows["workflows"]) and workflows.get("total_count") == len(workflows["workflows"]) and len(workflows["workflows"]) <= 100, "workflow state is incomplete")
    live_paths = {item.get("path") for item in workflows.get("workflows", []) if item.get("state") == "active"}
    need(live_paths == {".github/workflows/governance-integrity.yml"}, "pre-merge workflow state differs")
    pr_identity = (pr.get("number"), pr.get("state"), pr.get("draft"), pr.get("html_url"), pr.get("base", {}).get("ref"), pr.get("base", {}).get("sha"), pr.get("base", {}).get("repo", {}).get("full_name"), pr.get("head", {}).get("ref"), pr.get("head", {}).get("sha"), pr.get("head", {}).get("repo", {}).get("full_name"))
    need(pr_identity == (1, "open", True, f"https://github.com/{contracts.REPOSITORY}/pull/1", "main", BASE_SHA, contracts.REPOSITORY, contracts.BRANCH, head, contracts.REPOSITORY), "draft PR identity differs")
    _check_runs(checks, head)
    query = "query($owner:String!,$repo:String!,$number:Int!){repository(owner:$owner,name:$repo){pullRequest(number:$number){reviewThreads(first:100){nodes{isResolved}pageInfo{hasNextPage}}}}}"
    conversations = contracts.strict_json(run(["gh", "api", "graphql", "-f", f"query={query}", "-f", "owner=abbudjoe", "-f", "repo=biblical-scholar-lab", "-F", "number=1"]).stdout)
    try:
        threads = conversations["data"]["repository"]["pullRequest"]["reviewThreads"]
    except (KeyError, TypeError) as error:
        raise ContractError("conversation state is unavailable") from error
    need(not any(not item.get("isResolved") for item in threads["nodes"]) and threads["pageInfo"].get("hasNextPage") is False, "conversation state is unresolved or incomplete")
    return {"state_type": "W00ABootstrapState", "repository_settings": "PASS", "ruleset": "PASS_W00A_TWO_CHECKS", "codeowners": "PASS_DEFAULT_BRANCH_API", "environment": "OBSERVED_FUTURE_DEPENDENCY_UNCHANGED", "workflow_state": "TRUSTED_VALIDATOR_NOT_LIVE_UNTIL_W00A_MERGE", "owner_authorization": "INACTIVE_REQUIRES_W00B", "required_checks_role": "DEFENSE_IN_DEPTH_ONLY"}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="check", required=True)
    commands = {check: sub.add_parser(check) for check in CLI_SPECS}
    for check, names in CLI_SPECS.items():
        for name in names:
            commands[check].add_argument(f"--{name}", required=True, type=int if name in {"pr-number", "run-id", "run-attempt"} else str)
    for name in ("review-limit-enabled", "admin-bypass-disabled"):
        commands["live-governance"].add_argument(f"--{name}", action="store_true")
    policy = sub.add_parser("command-policy")
    policy.add_argument("--phase", choices=[item.value for item in contracts.CommandPhase], required=True)
    policy.add_argument("command")
    return root


def dispatch(arguments: argparse.Namespace) -> Any:
    if arguments.check == "project-integrity":
        return validate_project(arguments.base_sha, arguments.head_sha, arguments.branch)
    if arguments.check == "turn-handoff-integrity":
        return validate_handoff(arguments.base_sha, arguments.head_sha, arguments.branch, arguments.pr_url)
    if arguments.check == "package-integrity":
        return validate_package(None, arguments.revision)
    if arguments.check == "candidate-metadata":
        tree, compare = _load(arguments.tree_json), _load(arguments.compare_json)
        need(isinstance(tree, dict) and isinstance(compare, dict), "candidate metadata is malformed")
        return validate_metadata(tree, compare, arguments.base_sha, arguments.head_sha)
    if arguments.check == "trusted-governance":
        return create_receipt(arguments)
    if arguments.check == "completion-integrity":
        return validate_completion(arguments.base_sha, arguments.head_sha, arguments.branch, arguments.pr_json, arguments.comments_json)
    if arguments.check == "live-governance":
        return validate_live(arguments.expected_head, arguments.review_limit_observed_at, arguments.environment_ui_observed_at, arguments.review_limit_enabled, arguments.admin_bypass_disabled)
    allowed, reason = contracts.assess_command(arguments.command, contracts.CommandPhase(arguments.phase))
    need(allowed, reason)
    return {"command_allowed": True, "reason": reason}


def main() -> int:
    try:
        result = dispatch(parser().parse_args())
    except (ContractError, json.JSONDecodeError, subprocess.CalledProcessError, subprocess.TimeoutExpired, KeyError, OSError, SyntaxError, UnicodeDecodeError, ValueError) as error:
        print(json.dumps({"status": "failure", "error": str(error)}, sort_keys=True))
        return 1
    print(json.dumps({"status": "success", "result": result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
