from __future__ import annotations

import argparse
import ast
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

ACTIVATION_PATH = "activations/ACT-W00-REPOSITORY-GOVERNANCE-v3.json"
ACTIVATION_HASH = "60def3ad374823a3c9065ad43deb6fb41b7ff079de52a212dc7c47c18d0d30c6"
PACKAGE = "governance/GOV-01-package-manifest.json"
CHECKSUMS = "governance/GOV-01-artifacts.sha256"
WORKFLOWS = {".github/workflows/governance-integrity.yml", ".github/workflows/trusted-governance-validator.yml"}
WORKFLOW_HASHES = {".github/workflows/governance-integrity.yml": "5c141666a16e74bac382a1ff2067afa7d1716452a4f1c3ba790215de590f8377", ".github/workflows/trusted-governance-validator.yml": "4781eb2e8fb7febad2d15663404c4ab01f046dcd08d52fc29e60cbbeb3f6672a"}
PRODUCTION = {*WORKFLOWS, "governance/ruff.toml", "governance/w00_contracts.py", "governance/w00_checks.py"}
PUBLIC_CONTRACTS = ("RootTurnHandoff:SPLIT_REQUIRED", "TrustedGovernanceValidationReceipt", "W00ABootstrapState")
TRUSTED_FILES = (".github/workflows/trusted-governance-validator.yml", "governance/w00_contracts.py", "governance/w00_checks.py")
LIMITS = {"tree_entries": 512, "tree_bytes": 16_777_216, "files": 128, "file_bytes": 524_288, "changed_bytes": 4_194_304, "commits": 64, "json_depth": 32}
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
    value = json.loads(blob(repository, revision, path))
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
    try:
        return [item.decode() for item in raw.split(b"\0") if item]
    except UnicodeDecodeError as error:
        raise ContractError("changed paths are not UTF-8") from error


def safe_path(path: str) -> None:
    pure = PurePosixPath(path)
    unsafe = not path or pure.is_absolute() or str(pure) != path or any(part in {"", ".", ".."} for part in pure.parts) or "\\" in path or len(path) > 240
    unsafe = unsafe or any(ord(character) < 32 or ord(character) == 127 for character in path)
    need(not unsafe and not path.lower().endswith((".zip", ".tar", ".gz", ".tgz", ".7z", ".rar")), "candidate path is unsafe")


def _diff_lines(base: str, head: str, repository: str | None) -> tuple[int, int]:
    source, additions, deletions, hunk = (git(repository, "diff", "--no-renames", "--unified=0", f"{base}...{head}"), 0, 0, False)
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


def budget(base: str, head: str, paths: list[str], repository: str | None = None) -> dict[str, Any]:
    names = {PurePosixPath(path).name for path in paths}
    manifests = {name for name in names if name in {"pyproject.toml", "setup.py", "setup.cfg", "package.json", "Cargo.toml", "go.mod"} or name.startswith("requirements") or name.endswith((".lock", "-lock.json"))}
    need(not manifests, "dependency manifest change is unclassified")
    schemas = {path for path in paths if path.startswith("governance/schemas/")}
    need(schemas <= {"governance/schemas/turn-handoff.schema.json"}, "public schema change is unclassified")
    additions, deletions = _diff_lines(base, head, repository)
    workflows = {path for path in paths if path.startswith(".github/workflows/")}
    migrations = {path for path in paths if path.endswith(".sql") or "migrations" in PurePosixPath(path).parts}
    contracts_changed = PUBLIC_CONTRACTS if {"governance/w00_contracts.py", "governance/schemas/turn-handoff.schema.json"}.intersection(paths) else ()
    dependencies = _dependencies(repository, head, workflows) - _dependencies(repository, base, workflows)
    production = {path for path in paths if path in workflows or path == "governance/ruff.toml" or path.startswith("governance/") and path.endswith(".py") and not PurePosixPath(path).name.startswith("test_")}
    return {"additions": additions, "deletions": deletions, "production_files": sorted(production), "test_files": sorted(path for path in paths if path.startswith("governance/test_")), "governance_files": sorted(path for path in paths if path.startswith("governance/")), "dependencies": sorted(dependencies), "public_contracts": list(contracts_changed), "workflows": sorted(workflows), "migrations": sorted(migrations)}


def validate_budget(metrics: dict[str, Any], record: dict[str, Any]) -> None:
    limits = record["budgets"]
    actual = (metrics["additions"] + metrics["deletions"], len(metrics["production_files"]), len(metrics["dependencies"]), len(metrics["public_contracts"]), len(metrics["migrations"]))
    maximum = (limits["substantive_changed_lines_hard_limit"], limits["handwritten_production_files_hard_limit"], limits["new_direct_dependencies_hard_limit"], limits["new_public_contracts_hard_limit"], limits["migrations_hard_limit"])
    need(all(value <= limit for value, limit in zip(actual, maximum, strict=True)), "an activation budget is exceeded")
    need(record["activation_id"] != contracts.ACTIVATION or set(metrics["workflows"]) == WORKFLOWS, "W00A workflow set differs")


def validate_package(repository: str | None, revision: str) -> dict[str, int]:
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
    return {"manifest_files": len(files), "checksum_files": len(entries)}


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
    validate_package(repository, base)
    validate_package(repository, head)
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
    try:
        text = content.decode()
    except UnicodeDecodeError as error:
        raise ContractError("candidate governed text is not UTF-8") from error
    need(not re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", text), "candidate contains log-control bytes")
    if path.endswith(".json"):
        try:
            _json_depth(json.loads(text))
        except json.JSONDecodeError as error:
            raise ContractError("candidate JSON is malformed") from error
    if path.endswith(".py"):
        try:
            ast.parse(text, filename=path)
        except SyntaxError as error:
            raise ContractError("candidate Python is malformed") from error
    if path.endswith((".yml", ".yaml")):
        script = "require 'yaml'; YAML.safe_load(STDIN.read, permitted_classes: [], permitted_symbols: [], aliases: false)"
        try:
            result = run(["ruby", "-e", script], text=False, input_data=content, timeout=5, check=False)
        except subprocess.TimeoutExpired as error:
            raise ContractError("candidate YAML parse timed out") from error
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
    need(_pair(repository, parent, git(repository, "rev-parse", f"{parent}^"), prefix) is None, "implementation head is itself a handoff commit")
    expected = (active["activation_id"], task, branch, base, pr_url, contracts.REPOSITORY)
    need(tuple(record[key] for key in ("activation_id", "task_id", "branch", "base_sha", "pr_url", "repository")) == expected, "handoff binding differs")
    metrics = budget(base, head, changed_paths(base, head, repository), repository)
    validate_budget(metrics, active)
    _handoff_receipt(record, metrics)
    _handoff_commands(record, branch, pr_url)
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


def _handoff_receipt(record: dict[str, Any], metrics: dict[str, Any]) -> None:
    receipt = record["complexity_receipt"]
    need(receipt["production_files_added"] == len(metrics["production_files"]), "handoff production-file receipt differs")
    for key, value in (("modules_added", metrics["production_files"]), ("dependencies_added", metrics["dependencies"]), ("public_contracts_changed", metrics["public_contracts"]), ("migrations_added", metrics["migrations"])):
        need(sorted(receipt[key]) == sorted(value), f"handoff complexity field differs: {key}")


def _handoff_commands(record: dict[str, Any], branch: str, pr_url: str) -> None:
    number = int(pr_url.rsplit("/", 1)[1])
    for item in record["commands"]:
        try:
            phase = contracts.CommandPhase(item.get("phase", "implementation"))
        except ValueError as error:
            raise ContractError("handoff command phase differs") from error
        need(isinstance(item.get("command"), str) and isinstance(item.get("exit_status"), int) and contracts.assess_command(item["command"], phase, branch=branch, pr_number=number)[0], "handoff records a prohibited command")


def _handoff_markdown(repository: str | None, head: str, path: str, parent: str, status: str, w00a: bool) -> None:
    markdown = blob(repository, head, path).decode()
    phrases = ("Required GitHub Actions checks are defense-in-depth evidence and are not treated as proof of trusted workflow provenance.", "The trusted base-controlled validator becomes operational from main only after W00A is manually merged.", "Owner authorization, receipt consumption, and the merge-only path are not active after W00A and require W00B.")
    required = (*phrases, contracts.TITLE) if w00a else ()
    need(all(item in markdown for item in (*required, parent, status)), "handoff declaration differs")


def _load(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _comments(path: str) -> list[dict[str, Any]]:
    value = _load(path)
    if isinstance(value, list) and value and all(isinstance(item, list) for item in value):
        value = [entry for page in value for entry in page]
    need(isinstance(value, list) and all(isinstance(item, dict) for item in value), "comments are malformed")
    return cast(list[dict[str, Any]], value)


def validate_completion(base: str, head: str, branch: str, pr_file: str, comments_file: str, repository: str | None = None) -> dict[str, Any]:
    pr, comments, url = (_load(pr_file), _comments(comments_file), f"https://github.com/{contracts.REPOSITORY}/pull/1")
    need(isinstance(pr, dict), "PR evidence is malformed")
    actual = (pr.get("number"), pr.get("state"), pr.get("draft"), pr.get("html_url"), pr.get("base", {}).get("ref"), pr.get("base", {}).get("sha"), pr.get("head", {}).get("ref"), pr.get("head", {}).get("sha"))
    need(actual == (1, "open", True, url, "main", base, branch, head), "live PR identity differs")
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
    value = {key: item for key, item in record.items() if key != "receipt_hash"}
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def create_receipt(arguments: argparse.Namespace) -> dict[str, Any]:
    identity = (arguments.repository, arguments.event, arguments.base_sha, arguments.pr_number)
    need(identity[:3] == (contracts.REPOSITORY, "pull_request_target", arguments.trusted_revision) and identity[3] > 0, "trusted workflow identity differs")
    tree, compare = _load(arguments.tree_json), _load(arguments.compare_json)
    need(isinstance(tree, dict) and isinstance(compare, dict), "candidate metadata is malformed")
    inert = inspect_candidate(arguments.candidate_repository, arguments.base_sha, arguments.head_sha, tree, compare)
    project = validate_project(arguments.base_sha, arguments.head_sha, arguments.branch, arguments.candidate_repository)
    url = f"https://github.com/{contracts.REPOSITORY}/pull/{arguments.pr_number}"
    handoff = validate_handoff(arguments.base_sha, arguments.head_sha, arguments.branch, url, arguments.candidate_repository)
    record = {
        "schema_version": "1.0",
        "receipt_type": "TrustedGovernanceValidationReceipt",
        "repository": contracts.REPOSITORY,
        "pr_number": arguments.pr_number,
        "inspected_head_sha": arguments.head_sha,
        "base_sha": arguments.base_sha,
        "trusted_validator_revision": arguments.trusted_revision,
        "workflow_path": ".github/workflows/trusted-governance-validator.yml",
        "workflow_run_id": arguments.run_id,
        "workflow_run_attempt": arguments.run_attempt,
        "event": arguments.event,
        "validator_content_hash": content_hash(None, arguments.trusted_revision),
        "handoff_path": handoff["json"],
        "handoff_sha256": hashlib.sha256(blob(arguments.candidate_repository, arguments.head_sha, handoff["json"])).hexdigest(),
        "validation_results": {"candidate_input_safety": "PASS", "project_integrity": "PASS", "turn_handoff_integrity": "PASS", "package_integrity": "PASS"},
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "conclusion": "success",
    }
    record["receipt_hash"] = _receipt_hash(record)
    need(all(contracts.DIGEST.fullmatch(record[key]) for key in ("validator_content_hash", "handoff_sha256", "receipt_hash")), "trusted receipt digest differs")
    Path(arguments.output).write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return {"receipt": record, "inert_input": inert, "project_additions": project["additions"]}


def _api(endpoint: str) -> dict[str, Any]:
    value = json.loads(run(["gh", "api", endpoint]).stdout)
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
    logins = [item.get("reviewer", {}).get("login") for item in reviewer.get("reviewers", [])]
    need((record.get("name"), record.get("can_admins_bypass"), reviewer.get("prevent_self_review"), logins) == (contracts.ENVIRONMENT, False, False, ["abbudjoe"]), "future environment differs")


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
    source, errors = (Path(".github/CODEOWNERS").read_text(), _api(f"{prefix}/codeowners/errors"))
    required = {"*", "/.github/", "/AGENTS.md", "/EXPERIMENT_AUTHORITY.md", "/governance/", "/activations/", "/handoffs/", "/reviews/"}
    owned = {line.split()[0] for line in source.splitlines() if line.strip() and not line.startswith("#") and line.split()[-1] == "@abbudjoe"}
    need(required <= owned and errors.get("errors") == [], "CODEOWNERS differs")
    workflows, pr = _api(f"{prefix}/actions/workflows"), _api(f"{prefix}/pulls/1")
    live_paths = {item.get("path") for item in workflows.get("workflows", []) if item.get("state") == "active"}
    need(live_paths == {".github/workflows/governance-integrity.yml"}, "pre-merge workflow state differs")
    need((pr.get("state"), pr.get("draft"), pr.get("base", {}).get("ref"), pr.get("head", {}).get("sha")) == ("open", True, "main", head), "draft PR state differs")
    query = "query($owner:String!,$repo:String!,$number:Int!){repository(owner:$owner,name:$repo){pullRequest(number:$number){reviewThreads(first:100){nodes{isResolved}pageInfo{hasNextPage}}}}}"
    conversations = json.loads(run(["gh", "api", "graphql", "-f", f"query={query}", "-f", "owner=abbudjoe", "-f", "repo=biblical-scholar-lab", "-F", "number=1"]).stdout)
    try:
        threads = conversations["data"]["repository"]["pullRequest"]["reviewThreads"]
    except (KeyError, TypeError) as error:
        raise ContractError("conversation state is unavailable") from error
    need(not any(not item.get("isResolved") for item in threads["nodes"]) and threads["pageInfo"].get("hasNextPage") is False, "conversation state is unresolved or incomplete")
    return {"repository_settings": "PASS", "ruleset": "PASS_W00A_TWO_CHECKS", "codeowners": "PASS_API", "environment": "OBSERVED_FUTURE_DEPENDENCY_UNCHANGED", "workflow_state": "TRUSTED_VALIDATOR_NOT_LIVE_UNTIL_W00A_MERGE", "owner_authorization": "INACTIVE_REQUIRES_W00B", "required_checks_role": "DEFENSE_IN_DEPTH_ONLY"}


def _identity(parser: argparse.ArgumentParser, *, url: bool = False) -> None:
    for name in ("base-sha", "head-sha", "branch"):
        parser.add_argument(f"--{name}", required=True)
    if url:
        parser.add_argument("--pr-url", required=True)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="check", required=True)
    _identity(sub.add_parser("project-integrity"))
    _identity(sub.add_parser("turn-handoff-integrity"), url=True)
    package = sub.add_parser("package-integrity")
    package.add_argument("--revision", required=True)
    metadata = sub.add_parser("candidate-metadata")
    for name in ("base-sha", "head-sha", "tree-json", "compare-json"):
        metadata.add_argument(f"--{name}", required=True)
    trusted = sub.add_parser("trusted-governance")
    for name in ("repository", "base-sha", "head-sha", "trusted-revision", "branch", "event", "candidate-repository", "tree-json", "compare-json", "output"):
        trusted.add_argument(f"--{name}", required=True)
    for name in ("pr-number", "run-id", "run-attempt"):
        trusted.add_argument(f"--{name}", required=True, type=int)
    completion = sub.add_parser("completion-integrity")
    _identity(completion)
    completion.add_argument("--pr-json", required=True)
    completion.add_argument("--comments-json", required=True)
    live = sub.add_parser("live-governance")
    for name in ("expected-head", "review-limit-observed-at", "environment-ui-observed-at"):
        live.add_argument(f"--{name}", required=True)
    live.add_argument("--review-limit-enabled", action="store_true")
    live.add_argument("--admin-bypass-disabled", action="store_true")
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
