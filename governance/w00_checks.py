"""W00 repository, trusted-run, record, and live-state checks."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, cast

import w00_contracts as contracts
from w00_contracts import ContractError, _require

ACTIVATION_PATH = "activations/ACT-W00-REPOSITORY-GOVERNANCE-v3.json"
ACTIVATION_ID = "ACT-W00-REPOSITORY-GOVERNANCE-v3"
ACTIVATION_SHA256 = "60def3ad374823a3c9065ad43deb6fb41b7ff079de52a212dc7c47c18d0d30c6"
EXPECTED_DESIGNS = {"DR-20", "DR-21", "DR-25", "DR-30", "GOV-01", "GOV-01-ERRATA-01", "GOV-01-ERRATA-02"}
CHECK_NAMES = {"project-integrity", "turn-handoff-integrity", "chatgpt-review-integrity", "owner-merge-record-integrity"}
EXPECTED_APP_ID = 15368
WORKFLOWS = {".github/workflows/governance-integrity.yml", ".github/workflows/trusted-governance-validator.yml", ".github/workflows/owner-merge-authorization.yml"}
WORKFLOW_HASHES = {".github/workflows/governance-integrity.yml": "e2b47241696ebc70a6e34cb08a5c3451e460e3de1454f5c4c7684d03b9a16e3a", ".github/workflows/trusted-governance-validator.yml": "9717ba01a5ea10cf780610fd323cd35c29629ed2d601179704d8eae3e3b8dabe", ".github/workflows/owner-merge-authorization.yml": "0827b08df05c12585855955933579c7896da4b47eff7c88acbfee9f9433a97d0"}
PUBLIC_CONTRACTS = {"TrustedGovernanceValidationReceipt", "OwnerMergeAuthorizationReceipt", "TurnHandoffDisposition:SPLIT_REQUIRED"}
TRUSTED_WORKFLOW = ".github/workflows/trusted-governance-validator.yml"
OWNER_WORKFLOW = ".github/workflows/owner-merge-authorization.yml"
TRUSTED_HASH_PATHS = (TRUSTED_WORKFLOW, "governance/w00_checks.py", "governance/w00_contracts.py")
PROTECTED_TRUST_PATHS = {*TRUSTED_HASH_PATHS, OWNER_WORKFLOW}
MAX_FILES, MAX_FILE_BYTES, MAX_TOTAL_BYTES, MAX_JSON_DEPTH = 128, 524_288, 4_194_304, 32
DEPENDENCY_MANIFESTS = {"pyproject.toml", "package.json", "Pipfile", "setup.py", "setup.cfg", "Cargo.toml", "go.mod"}


def _run(arguments: list[str], *, text: bool = True, check: bool = True) -> subprocess.CompletedProcess[Any]:
    return subprocess.run(arguments, check=check, text=text, capture_output=True)


def _git(*arguments: str) -> str: return cast(str, _run(["git", *arguments]).stdout).strip()


def _git_bytes(revision: str, file_name: str) -> bytes:
    return cast(bytes, _run(["git", "show", f"{revision}:{file_name}"], text=False).stdout)


def _git_text(revision: str, file_name: str) -> str: return _git_bytes(revision, file_name).decode("utf-8")


def _git_json(revision: str, file_name: str) -> dict[str, Any]:
    value = json.loads(_git_text(revision, file_name))
    _require(isinstance(value, dict), f"{file_name} must contain a JSON object")
    return cast(dict[str, Any], value)


def _json_file(file_name: str) -> Any: return json.loads(Path(file_name).read_text(encoding="utf-8"))


def changed_paths(base_sha: str, head_sha: str) -> list[str]:
    raw = cast(bytes, _run(["git", "diff", "--name-only", "-z", f"{base_sha}...{head_sha}"], text=False).stdout)
    try:
        paths = [item.decode("utf-8") for item in raw.split(b"\0") if item]
    except UnicodeDecodeError as error:
        raise ContractError("changed paths must be UTF-8") from error
    return paths


def resolve_activation(revision: str, branch: str) -> dict[str, Any]:
    candidates: list[tuple[dict[str, Any], str]] = []
    for file_name in _git("ls-tree", "-r", "--name-only", revision, "activations").splitlines():
        if file_name.endswith(".json"):
            record = _git_json(revision, file_name)
            if record.get("status") == "APPROVED" and record.get("root_turn", {}).get("task_branch") == branch:
                contracts.validate_activation(record); candidates.append((record, file_name))
    _require(len(candidates) == 1, f"expected one base-approved activation for {branch}; found {len(candidates)}")
    record, file_name = candidates[0]
    _require(not _run(["git", "merge-base", "--is-ancestor", record["approved_design_commit"], revision], check=False).returncode, "approved design commit is not an ancestor of the base")
    if record["activation_id"] == ACTIVATION_ID:
        _require(set(record["approved_design_ids"]) == EXPECTED_DESIGNS, "W00 approved design identity differs")
        _require(hashlib.sha256(_git_bytes(revision, file_name)).hexdigest() == ACTIVATION_SHA256, "W00 activation hash differs")
    return record


def validate_change_scope(paths: list[str], activation: dict[str, Any]) -> None:
    disallowed = [path for path in paths if not any(path == item or (item.endswith("/") and path.startswith(item)) for item in activation["activated_paths"])]
    _require(not disallowed, f"out-of-scope paths changed: {disallowed}")
    _require(not any(path.startswith(("design/", "activations/", "benchmark/", "sources/")) for path in paths), "immutable design, activation, source, or benchmark content changed")


def _production_path(file_name: str) -> bool:
    excluded = ("test_", "/tests/", "/fixtures/", "handoffs/", "/evidence/")
    return file_name.endswith((".py", ".sh", ".yml", ".yaml")) and not any(item in file_name for item in excluded)


def scan_anti_slop(file_name: str, source: str) -> None:
    markers = ("TO" + "DO", "FIX" + "ME", "Not" + "ImplementedError", "place" + "holder")
    for number, line in enumerate(source.splitlines(), 1):
        _require(not any(marker.lower() in line.lower() for marker in markers) and not re.fullmatch(r"\s*pass(?:\s*#.*)?", line), f"unfinished implementation marker in {file_name}:{number}")


def _logical(lines: list[str]) -> int: return sum(bool(line.strip()) and not line.lstrip().startswith("#") for line in lines)


def _complexity(node: ast.AST) -> int:
    controls = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.IfExp, ast.Match)
    total = sum(isinstance(child, controls) for child in ast.walk(node))
    total += sum(max(0, len(child.values) - 1) for child in ast.walk(node) if isinstance(child, ast.BoolOp))
    return 1 + total


def _nesting(node: ast.AST, depth: int = 0) -> int:
    controls = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith, ast.Match)
    values = [depth]
    for child in ast.iter_child_nodes(node):
        values.append(_nesting(child, depth + int(isinstance(child, controls))))
    return max(values)


def validate_python_complexity(file_name: str, source: str) -> None:
    lines, tree = source.splitlines(), ast.parse(source, filename=file_name)
    _require(_logical(lines) <= 500, f"production module exceeds 500 logical lines: {file_name}")
    for node in ast.walk(tree):
        _validate_python_node(file_name, lines, node)


def _validate_python_node(file_name: str, lines: list[str], node: ast.AST) -> None:
    logical = _logical(lines[node.lineno - 1:(getattr(node, "end_lineno", None) or node.lineno)]) if hasattr(node, "lineno") else 0
    _require(not isinstance(node, ast.ClassDef) or logical <= 250, f"production class exceeds 250 logical lines: {file_name}:{getattr(node, 'lineno', 0)}")
    _require(not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or all((logical <= 60, _complexity(node) <= 10, _nesting(node) <= 3)), f"DR-30 function threshold exceeded: {file_name}:{getattr(node, 'lineno', 0)}")


def _diff_line_counts(base_sha: str, head_sha: str) -> tuple[int, int]:
    additions = deletions = 0
    for line in _git("diff", "--unified=0", f"{base_sha}...{head_sha}").splitlines():
        if line.startswith(("+++", "---")) or len(line) < 2 or not line[1:].strip():
            continue
        additions += int(line.startswith("+")); deletions += int(line.startswith("-"))
    return additions, deletions


def _action_dependencies(revision: str, workflows: set[str]) -> set[str]:
    dependencies: set[str] = set()
    for path in workflows:
        try:
            source = _git_text(revision, path)
        except subprocess.CalledProcessError:
            continue
        dependencies.update(match.split("@", 1)[0] for match in re.findall(r"uses:\s*([^\s]+@[^\s]+)", source))
    return dependencies


@dataclass(frozen=True)
class BudgetMetrics:
    additions: int
    deletions: int
    production_files: tuple[str, ...]
    dependencies: tuple[str, ...]
    public_contracts: tuple[str, ...]
    workflows: tuple[str, ...]
    migrations: tuple[str, ...]


def budget_metrics(base_sha: str, head_sha: str, paths: list[str]) -> BudgetMetrics:
    additions, deletions = _diff_line_counts(base_sha, head_sha)
    production = tuple(sorted(path for path in paths if _production_path(path)))
    workflows = tuple(sorted(path for path in paths if path.startswith(".github/workflows/")))
    manifests = {path for path in paths if PurePosixPath(path).name in DEPENDENCY_MANIFESTS or PurePosixPath(path).name.startswith("requirements")}
    _require(not manifests, f"dependency manifest changes require a separately activated validator: {sorted(manifests)}")
    dependencies = _action_dependencies(head_sha, set(workflows)) - _action_dependencies(base_sha, set(workflows))
    migrations = tuple(sorted(path for path in paths if any(part.startswith("migration") for part in PurePosixPath(path).parts) or path.endswith(".sql")))
    contract_paths = {"governance/w00_contracts.py", "governance/schemas/turn-handoff.schema.json"}
    contracts = tuple(sorted(PUBLIC_CONTRACTS)) if contract_paths.intersection(paths) else ()
    return BudgetMetrics(additions, deletions, production, tuple(sorted(dependencies)), contracts, workflows, migrations)


def validate_budgets(metrics: BudgetMetrics, activation: dict[str, Any]) -> None:
    budgets = activation["budgets"]
    values = ((metrics.additions + metrics.deletions, budgets["substantive_changed_lines_hard_limit"], "substantive line"),
              (len(metrics.production_files), budgets["handwritten_production_files_hard_limit"], "production file"),
              (len(metrics.dependencies), budgets["new_direct_dependencies_hard_limit"], "direct dependency"),
              (len(metrics.public_contracts), budgets["new_public_contracts_hard_limit"], "public contract"),
              (len(metrics.migrations), budgets["migrations_hard_limit"], "migration"))
    for actual, limit, label in values:
        _require(actual <= limit, f"{label} hard limit exceeded")
    _require(activation["activation_id"] != ACTIVATION_ID or set(metrics.workflows) == WORKFLOWS, "W00 must change exactly the three approved workflows")


def _validate_workflows(head_sha: str) -> None:
    sources = {path: _git_text(head_sha, path) for path in WORKFLOWS}
    observed = {path: hashlib.sha256(source.encode()).hexdigest() for path, source in sources.items()}
    _require(observed == WORKFLOW_HASHES, "an audited governance workflow differs from its trusted canonical content")


def validate_project(base_sha: str, head_sha: str, branch: str) -> dict[str, Any]:
    activation = resolve_activation(base_sha, branch)
    _require(activation["root_turn"]["task_branch"] == branch, "branch differs from the activation")
    paths = changed_paths(base_sha, head_sha); validate_change_scope(paths, activation)
    _require(activation["activation_id"] == ACTIVATION_ID or not PROTECTED_TRUST_PATHS.intersection(paths), "trusted control-plane changes require a separately approved governance activation")
    metrics = budget_metrics(base_sha, head_sha, paths); validate_budgets(metrics, activation)
    for file_name in metrics.production_files:
        source = _git_text(head_sha, file_name); scan_anti_slop(file_name, source)
        if file_name.endswith(".py"):
            validate_python_complexity(file_name, source)
    _validate_workflows(head_sha)
    return {"changed_paths": paths, **metrics.__dict__}


def _safe_candidate_path(path: str) -> None:
    pure = PurePosixPath(path)
    invalid = pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts)
    invalid = invalid or "\\" in path or len(path) > 240 or any(ord(character) < 32 or ord(character) == 127 for character in path)
    _require(not invalid and not path.lower().endswith((".zip", ".tar", ".gz", ".tgz", ".7z", ".rar")), "candidate path is unsafe or unsupported")


def _json_depth(value: Any, depth: int = 0) -> int:
    _require(depth <= MAX_JSON_DEPTH, "candidate JSON exceeds the parse-depth bound")
    children = value.values() if isinstance(value, dict) else (value if isinstance(value, list) else ())
    return max([depth, *(_json_depth(item, depth + 1) for item in children)])


def inspect_candidate(base_sha: str, head_sha: str) -> dict[str, Any]:
    _require(not _run(["git", "merge-base", "--is-ancestor", base_sha, head_sha], check=False).returncode, "candidate head does not descend from its reported base")
    paths = changed_paths(base_sha, head_sha)
    _require(len(paths) <= MAX_FILES, "candidate changed-file count exceeds the inert-input bound")
    total = 0
    for path in paths:
        _safe_candidate_path(path); blob = _candidate_blob(head_sha, path)
        if blob is None:
            continue
        content = blob; total += len(content)
        _require(total <= MAX_TOTAL_BYTES, "candidate total input exceeds the inert-input bound")
        if path.endswith((".json", ".md", ".yml", ".yaml", ".py")):
            text = content.decode("utf-8")
            if path.endswith(".json"):
                _json_depth(json.loads(text))
    return {"changed_files": len(paths), "total_bytes": total, "execution": "NONE"}


def _candidate_blob(revision: str, path: str) -> bytes | None:
    listing = _git("ls-tree", revision, "--", path)
    if not listing:
        return None
    metadata, listed = listing.split("\t", 1); mode, kind, object_id = metadata.split()
    _require((listed, kind) == (path, "blob") and mode in {"100644", "100755"}, "candidate contains a symlink, special file, or ambiguous tree entry")
    _require(int(_git("cat-file", "-s", object_id)) <= MAX_FILE_BYTES, "candidate file exceeds the inert-input size bound")
    return cast(bytes, _run(["git", "cat-file", "blob", object_id], text=False).stdout)


def validator_content_hash(revision: str) -> str:
    digest = hashlib.sha256()
    for path in TRUSTED_HASH_PATHS:
        content = _git_bytes(revision, path)
        digest.update(path.encode() + b"\0" + str(len(content)).encode() + b"\0" + content)
    return digest.hexdigest()


def create_trusted_receipt(arguments: argparse.Namespace) -> dict[str, Any]:
    _require((arguments.repository, arguments.event, arguments.base_sha) == (contracts.REPOSITORY, "pull_request_target", arguments.trusted_revision), "trusted workflow runtime identity differs")
    inert = inspect_candidate(arguments.base_sha, arguments.head_sha)
    project = validate_project(arguments.base_sha, arguments.head_sha, arguments.branch)
    handoff = validate_turn_handoff(arguments.base_sha, arguments.head_sha, arguments.branch, f"https://github.com/{contracts.REPOSITORY}/pull/{arguments.pr_number}")
    record = {
        "schema_version": "1.0", "receipt_type": "TrustedGovernanceValidationReceipt",
        "repository": contracts.REPOSITORY, "pr_number": arguments.pr_number, "inspected_head_sha": arguments.head_sha,
        "base_sha": arguments.base_sha, "trusted_validator_revision": arguments.trusted_revision,
        "workflow_path": TRUSTED_WORKFLOW, "workflow_run_id": arguments.run_id,
        "workflow_run_attempt": arguments.run_attempt, "event": arguments.event,
        "validator_content_hash": validator_content_hash(arguments.trusted_revision),
        "validation_results": {"candidate_input_safety": "PASS", "project_integrity": "PASS", "turn_handoff_integrity": "PASS"},
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "conclusion": "success",
    }
    record["receipt_hash"] = contracts.receipt_hash(record); contracts.validate_trusted_receipt(record)
    Path(arguments.output).write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return {"receipt": record, "inert_input": inert, "handoff": handoff["turn_id"], "project_additions": project["additions"]}


def _comments(file_name: str) -> list[dict[str, Any]]:
    value = _json_file(file_name)
    if isinstance(value, list) and value and all(isinstance(item, list) for item in value):
        value = [entry for page in value for entry in page]
    _require(isinstance(value, list) and all(isinstance(item, dict) for item in value), "comments input must be an array of objects")
    return cast(list[dict[str, Any]], value)


def _pr_identity(pr_file: str) -> tuple[dict[str, Any], str, str, str]:
    pr = _json_file(pr_file)
    _require(isinstance(pr, dict) and pr.get("state") == "open" and pr.get("base", {}).get("ref") == "main", "target PR must be open against main")
    pr = cast(dict[str, Any], pr)
    return pr, pr["html_url"], pr["base"]["sha"], pr["head"]["sha"]


def validate_review_comments(pr_file: str, comments_file: str) -> dict[str, Any]:
    pr, url, base, head = _pr_identity(pr_file); activation = resolve_activation(base, pr["head"]["ref"])
    review = contracts.current_clean_review(_comments(comments_file), pr_url=url, activation_id=activation["activation_id"], base_sha=base, head_sha=head)
    return {"review_id": review["review_id"], "reviewed_head_sha": head}


def validate_authorization_comments(pr_file: str, comments_file: str) -> dict[str, Any]:
    pr, url, base, head = _pr_identity(pr_file); activation = resolve_activation(base, pr["head"]["ref"]); comments = _comments(comments_file)
    review = contracts.current_clean_review(comments, pr_url=url, activation_id=activation["activation_id"], base_sha=base, head_sha=head)
    authorization = contracts.current_authorization(comments, repository=contracts.REPOSITORY, pr_url=url, activation_id=activation["activation_id"], head_sha=head, review_id=review["review_id"])
    return {"authorization_id": authorization["authorization_id"], "authorized_head_sha": head}


def validate_owner_inputs(pr_number: int, head_sha: str, review_id: str, trusted_run_id: int, workflow_ref: str) -> None:
    _require(pr_number > 0 and trusted_run_id > 0 and bool(re.fullmatch(r"[0-9a-f]{40}", head_sha)), "owner authorization dispatch identity is invalid")
    _require(bool(re.fullmatch(r"[A-Za-z0-9._:-]+", review_id)) and workflow_ref == "refs/heads/main", "owner authorization review or workflow ref is invalid")


def _validate_quality_checks(record: dict[str, Any], head_sha: str) -> None:
    runs = record.get("check_runs") if isinstance(record, dict) else None
    _require(isinstance(runs, list), "quality-check evidence is unavailable")
    runs = cast(list[Any], runs)
    for name in CHECK_NAMES:
        matches = [item for item in runs if isinstance(item, dict) and all((item.get("name") == name, item.get("head_sha") == head_sha, isinstance(item.get("app"), dict), item.get("app", {}).get("id") == EXPECTED_APP_ID))]
        _require(bool(matches and max(matches, key=lambda item: item.get("completed_at") or "").get("conclusion") == "success"), f"ordinary quality check is not successful: {name}")


def _validate_conversations(record: dict[str, Any]) -> None:
    try:
        threads = record["data"]["repository"]["pullRequest"]["reviewThreads"]
        unresolved = any(not node["isResolved"] for node in threads["nodes"])
    except (KeyError, TypeError) as error:
        raise ContractError("conversation evidence is unavailable") from error
    _require(not unresolved and threads.get("pageInfo", {}).get("hasNextPage") is False, "review conversations are unresolved or incomplete")


def create_owner_receipt(arguments: argparse.Namespace) -> dict[str, Any]:
    validate_owner_inputs(arguments.pr_number, arguments.authorized_head_sha, arguments.chatgpt_review_id, arguments.trusted_run_id, arguments.workflow_ref)
    pr, url, base, head = _pr_identity(arguments.pr_json)
    actual_pr = (pr.get("number"), url, head, arguments.workflow_sha)
    expected_pr = (arguments.pr_number, f"https://github.com/{contracts.REPOSITORY}/pull/{arguments.pr_number}", arguments.authorized_head_sha, base)
    _require(actual_pr == expected_pr, "live PR or authorization-workflow revision differs")
    comments = _comments(arguments.comments_json); activation = resolve_activation(base, pr["head"]["ref"])
    review = contracts.current_clean_review(comments, pr_url=url, activation_id=activation["activation_id"], base_sha=base, head_sha=head)
    _require(review["review_id"] == arguments.chatgpt_review_id, "owner authorization references a different review")
    trusted = _json_file(arguments.trusted_receipt); contracts.validate_trusted_receipt(trusted)
    run = _json_file(arguments.trusted_run_json)
    run_identity = (run.get("id"), run.get("run_attempt"), run.get("event"), run.get("status"), run.get("conclusion"), run.get("head_sha"), run.get("path"))
    expected_run = (arguments.trusted_run_id, trusted["workflow_run_attempt"], "pull_request_target", "completed", "success", trusted["trusted_validator_revision"], TRUSTED_WORKFLOW)
    _require(run_identity == expected_run, "trusted validator workflow-run evidence differs")
    trusted_identity = (trusted["pr_number"], trusted["inspected_head_sha"], trusted["base_sha"], trusted["workflow_run_id"])
    _require(trusted_identity == (arguments.pr_number, head, base, arguments.trusted_run_id) and trusted["validator_content_hash"] == validator_content_hash(trusted["trusted_validator_revision"]), "trusted validator receipt is stale or mismatched")
    trusted_at = datetime.fromisoformat(trusted["timestamp"].replace("Z", "+00:00"))
    reviewed_at = datetime.fromisoformat(review["review_timestamp"].replace("Z", "+00:00"))
    _require(trusted_at <= reviewed_at <= datetime.now(timezone.utc), "trusted validation, review, and authorization ordering differs")
    _validate_quality_checks(_json_file(arguments.checks_json), head); _validate_conversations(_json_file(arguments.conversations_json))
    record = {
        "schema_version": "1.0", "receipt_type": "OwnerMergeAuthorizationReceipt",
        "repository": contracts.REPOSITORY, "pr_number": arguments.pr_number, "pr_url": url,
        "authorized_head_sha": head, "chatgpt_review_id": review["review_id"],
        "trusted_validator": {"workflow_path": TRUSTED_WORKFLOW, "run_id": arguments.trusted_run_id, "receipt_hash": trusted["receipt_hash"]},
        "authorization_workflow": {"workflow_path": OWNER_WORKFLOW, "run_id": arguments.run_id, "run_attempt": arguments.run_attempt, "trusted_revision": arguments.workflow_sha},
        "environment_name": contracts.ENVIRONMENT, "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "conclusion": "success",
    }
    record["receipt_hash"] = contracts.receipt_hash(record); contracts.validate_owner_receipt(record)
    Path(arguments.output).write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return record


def _handoff_pair(head_sha: str, task_id: str) -> tuple[str, str]:
    prefix = f"handoffs/{task_id}/"
    entries = _git("diff-tree", "--no-commit-id", "--name-status", "-r", head_sha, "--", prefix).splitlines()
    added = [line.split("\t", 1)[1] for line in entries if line.startswith("A\t")]
    stems = {str(PurePosixPath(path).with_suffix("")) for path in added}
    _require((len(added), len(stems), {PurePosixPath(path).suffix for path in added}) == (2, 1, {".md", ".json"}), "final commit must add exactly one Markdown/JSON handoff pair")
    return next(path for path in added if path.endswith(".json")), next(path for path in added if path.endswith(".md"))


def _validate_append_only_handoffs(base_sha: str, head_sha: str, task_id: str) -> None:
    prefix = f"handoffs/{task_id}/"
    commits = _git("rev-list", "--reverse", f"{base_sha}..{head_sha}", "--", prefix).splitlines()
    for commit in commits:
        entries = _git("diff-tree", "--no-commit-id", "--name-status", "-r", commit, "--", prefix).splitlines()
        _require(not any(not line.startswith("A\t") for line in entries), "handoff history edited, deleted, replaced, or reordered a prior record")
        paths = [line.split("\t", 1)[1] for line in entries if not line.endswith(".gitkeep")]
        stems = {str(PurePosixPath(path).with_suffix("")) for path in paths}
        _require(not paths or (len(paths), len(stems), {PurePosixPath(path).suffix for path in paths}) == (2, 1, {".md", ".json"}), "each handoff commit must append one complete pair")


def _validate_complexity_receipt(record: dict[str, Any], metrics: BudgetMetrics) -> None:
    receipt = record["complexity_receipt"]
    expected = {"modules_added": metrics.production_files, "dependencies_added": metrics.dependencies, "public_contracts_changed": metrics.public_contracts, "migrations_added": metrics.migrations}
    _require(not any(sorted(receipt[field]) != sorted(value) for field, value in expected.items()), "complexity receipt omits files, dependencies, contracts, or migrations")
    _require(receipt["production_files_added"] == len(metrics.production_files), "complexity production-file count differs")


def _validate_handoff_commands(record: dict[str, Any], activation: dict[str, Any]) -> None:
    for item in record["commands"]:
        _require(isinstance(item.get("command"), str) and isinstance(item.get("exit_status"), int), "handoff command evidence is malformed")
        phase_name = item.get("phase", contracts.CommandPhase.IMPLEMENTATION.value)
        _require(phase_name != contracts.CommandPhase.MERGE_ONLY.value, "implementation handoff cannot self-declare merge-only authority")
        _require(phase_name != contracts.CommandPhase.W00_GOVERNANCE.value or activation["activation_id"] == ACTIVATION_ID, "W00 governance exception cannot be reused")
        try:
            phase = contracts.CommandPhase(phase_name)
        except ValueError as error:
            raise ContractError("handoff command phase is invalid") from error
        decision = contracts.assess_command(item["command"], phase)
        _require(decision.allowed, f"handoff records a prohibited command: {decision.reason}")


def validate_turn_handoff(base_sha: str, head_sha: str, branch: str, pr_url: str) -> dict[str, Any]:
    activation = resolve_activation(base_sha, branch); task_id = activation["root_turn"]["task_id"]
    _validate_append_only_handoffs(base_sha, head_sha, task_id)
    json_path, markdown_path = _handoff_pair(head_sha, task_id); record = _git_json(head_sha, json_path)
    parent = _git("rev-parse", f"{head_sha}^")
    final_paths = _git("diff-tree", "--no-commit-id", "--name-only", "-r", head_sha).splitlines()
    contracts.validate_handoff(record); expected_pair = {json_path, markdown_path}
    _require(set(final_paths) == expected_pair and record["implementation_head_sha"] == parent and {PurePosixPath(path).stem for path in expected_pair} == {record["turn_id"]}, "final commit is not one correctly named handoff pair over the implementation head")
    expected = (activation["activation_id"], task_id, branch, base_sha, pr_url, contracts.REPOSITORY)
    _require(tuple(record[key] for key in ("activation_id", "task_id", "branch", "base_sha", "pr_url", "repository")) == expected, "handoff task, branch, base, PR, or repository differs")
    _validate_handoff_commands(record, activation)
    metrics = budget_metrics(base_sha, head_sha, changed_paths(base_sha, head_sha)); validate_budgets(metrics, activation); _validate_complexity_receipt(record, metrics)
    markdown = _git_text(head_sha, markdown_path)
    phrase = "Expected-App matching is defense in depth only and is not treated as proof of workflow provenance."
    _require(all(item in markdown for item in (record["implementation_head_sha"], record["status"], phrase)), "Markdown handoff identity or trust declaration differs")
    return {"turn_id": record["turn_id"], "json": json_path, "markdown": markdown_path, "implementation_head_sha": parent}


def validate_repository_settings(record: dict[str, Any]) -> None:
    actual = tuple(record.get(key) for key in ("default_branch", "visibility", "allow_squash_merge", "allow_merge_commit", "allow_rebase_merge", "allow_auto_merge", "delete_branch_on_merge"))
    _require(actual == ("main", "public", True, False, False, False, True), "live repository merge configuration differs")


def validate_ruleset(record: dict[str, Any]) -> None:
    _require(tuple(record.get(key) for key in ("id", "name", "target", "enforcement", "bypass_actors", "current_user_can_bypass")) == (20960975, "main-quality-and-authorization-gates", "branch", "active", [], "never"), "ruleset identity, enforcement, or bypass posture differs")
    refs = record.get("conditions", {}).get("ref_name", {})
    _require(refs == {"exclude": [], "include": ["~DEFAULT_BRANCH"]}, "ruleset target can exclude or miss main")
    items = record.get("rules", [])
    _require(isinstance(items, list) and all(isinstance(item, dict) for item in items), "ruleset rules are unavailable")
    rules = {item.get("type"): item for item in items}
    _require(len(rules) == len(items) and set(rules) == {"deletion", "non_fast_forward", "required_linear_history", "pull_request", "required_status_checks"}, "ruleset rule set differs")
    pull = rules["pull_request"].get("parameters", {})
    expected_pull = (0, True, False, False, True, ["squash"])
    actual_pull = tuple(pull.get(key) for key in ("required_approving_review_count", "dismiss_stale_reviews_on_push", "require_code_owner_review", "require_last_push_approval", "required_review_thread_resolution", "allowed_merge_methods"))
    status = rules["required_status_checks"].get("parameters", {})
    contexts = {(item.get("context"), item.get("integration_id")) for item in status.get("required_status_checks", [])}
    _require(actual_pull == expected_pull and (status.get("strict_required_status_checks_policy"), status.get("do_not_enforce_on_create")) == (True, False) and contexts == {(name, EXPECTED_APP_ID) for name in CHECK_NAMES}, "pull-request or defense-in-depth status parameters differ")


def validate_codeowners(text: str, errors: dict[str, Any]) -> None:
    required = {"*", "/.github/", "/AGENTS.md", "/EXPERIMENT_AUTHORITY.md", "/governance/", "/activations/", "/handoffs/", "/reviews/"}
    owned = {line.split()[0] for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#") and line.split()[-1] == "@abbudjoe"}
    _require(required.issubset(owned) and errors.get("errors") == [], "local or GitHub-recognized CODEOWNERS posture differs")


def validate_environment(record: dict[str, Any]) -> None:
    rules = record.get("protection_rules", [])
    reviewers = [item for item in rules if isinstance(item, dict) and item.get("type") == "required_reviewers"]
    reviewer = reviewers[0] if len(reviewers) == 1 else None
    logins = [item.get("reviewer", {}).get("login") for item in reviewer.get("reviewers", [])] if reviewer else []
    _require(record.get("name") == contracts.ENVIRONMENT and record.get("can_admins_bypass") is False and reviewer is not None and reviewer.get("prevent_self_review") is False and logins == ["abbudjoe"], "owner authorization environment protection differs")


def _recent(value: str) -> None:
    try:
        observed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as error:
        raise ContractError("live UI evidence timestamp is invalid") from error
    age = datetime.now(timezone.utc) - observed
    _require(observed.utcoffset() is not None and 0 <= age.total_seconds() <= 86_400, "live UI evidence is stale or future-dated")


def _gh_json(endpoint: str) -> dict[str, Any]:
    value = json.loads(_run(["gh", "api", endpoint]).stdout)
    _require(isinstance(value, dict), "live GitHub response must be an object")
    return cast(dict[str, Any], value)


def validate_live_governance(expected_head: str, review_limit_at: str, environment_ui_at: str, review_limit_enabled: bool, admin_bypass_disabled: bool) -> dict[str, Any]:
    _recent(review_limit_at); _recent(environment_ui_at)
    _require(review_limit_enabled and admin_bypass_disabled, "required UI-only governance settings are not confirmed")
    repository = _gh_json(f"repos/{contracts.REPOSITORY}"); validate_repository_settings(repository)
    ruleset = _gh_json(f"repos/{contracts.REPOSITORY}/rulesets/20960975"); validate_ruleset(ruleset)
    environment = _gh_json(f"repos/{contracts.REPOSITORY}/environments/{contracts.ENVIRONMENT}"); validate_environment(environment)
    workflows = _gh_json(f"repos/{contracts.REPOSITORY}/actions/workflows")
    live_paths = {item.get("path") for item in workflows.get("workflows", []) if item.get("state") == "active"}
    _require(live_paths == {".github/workflows/governance-integrity.yml"}, "W00 bootstrap workflow live state is missing or ambiguous")
    errors = _gh_json(f"repos/{contracts.REPOSITORY}/codeowners/errors"); validate_codeowners(Path(".github/CODEOWNERS").read_text(encoding="utf-8"), errors)
    pr = _gh_json(f"repos/{contracts.REPOSITORY}/pulls/1")
    _require((pr.get("state"), pr.get("draft"), pr.get("base", {}).get("ref"), pr.get("head", {}).get("sha")) == ("open", True, "main", expected_head), "draft PR live identity differs")
    return {"repository_settings": "PASS", "ruleset": "PASS", "code_review_limit": "PASS_UI_OBSERVED", "codeowners": "PASS", "environment": "PASS_API_AND_UI", "workflow_state": "W00_BOOTSTRAP_NOT_LIVE_TRUSTED", "pr_state": "PASS", "expected_app_role": "DEFENSE_IN_DEPTH_ONLY"}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest="check", required=True)
    for name in ("project-integrity", "turn-handoff-integrity"):
        command = sub.add_parser(name); command.add_argument("--base-sha", required=True); command.add_argument("--head-sha", required=True); command.add_argument("--branch", required=True)
        if name == "turn-handoff-integrity":
            command.add_argument("--pr-url", required=True)
    for name in ("chatgpt-review-integrity", "owner-merge-record-integrity"):
        command = sub.add_parser(name); command.add_argument("--pr-json", required=True); command.add_argument("--comments-json", required=True)
    trusted = sub.add_parser("trusted-governance")
    for name in ("repository", "base-sha", "head-sha", "trusted-revision", "branch", "event", "output"):
        trusted.add_argument(f"--{name}", required=True)
    for name in ("pr-number", "run-id", "run-attempt"):
        trusted.add_argument(f"--{name}", required=True, type=int)
    owner = sub.add_parser("owner-authorize")
    for name in ("authorized-head-sha", "chatgpt-review-id", "workflow-ref", "workflow-sha", "pr-json", "comments-json", "trusted-receipt", "trusted-run-json", "checks-json", "conversations-json", "output"):
        owner.add_argument(f"--{name}", required=True)
    for name in ("pr-number", "trusted-run-id", "run-id", "run-attempt"):
        owner.add_argument(f"--{name}", required=True, type=int)
    live = sub.add_parser("live-governance"); live.add_argument("--expected-head", required=True); live.add_argument("--review-limit-observed-at", required=True); live.add_argument("--environment-ui-observed-at", required=True); live.add_argument("--review-limit-enabled", action="store_true"); live.add_argument("--admin-bypass-disabled", action="store_true")
    policy = sub.add_parser("command-policy"); policy.add_argument("--phase", choices=[item.value for item in contracts.CommandPhase], required=True); policy.add_argument("command")
    return parser


def _dispatch(arguments: argparse.Namespace) -> Any:
    if arguments.check == "project-integrity":
        return validate_project(arguments.base_sha, arguments.head_sha, arguments.branch)
    if arguments.check == "turn-handoff-integrity":
        return validate_turn_handoff(arguments.base_sha, arguments.head_sha, arguments.branch, arguments.pr_url)
    if arguments.check == "chatgpt-review-integrity":
        return validate_review_comments(arguments.pr_json, arguments.comments_json)
    if arguments.check == "owner-merge-record-integrity":
        return validate_authorization_comments(arguments.pr_json, arguments.comments_json)
    if arguments.check == "trusted-governance":
        return create_trusted_receipt(arguments)
    if arguments.check == "owner-authorize":
        return create_owner_receipt(arguments)
    if arguments.check == "live-governance":
        return validate_live_governance(arguments.expected_head, arguments.review_limit_observed_at, arguments.environment_ui_observed_at, arguments.review_limit_enabled, arguments.admin_bypass_disabled)
    decision = contracts.assess_command(arguments.command, contracts.CommandPhase(arguments.phase))
    if not decision.allowed:
        raise ContractError(decision.reason)
    return {"command_allowed": True, "reason": decision.reason}


def main() -> int:
    try:
        result = _dispatch(_parser().parse_args())
    except (ContractError, json.JSONDecodeError, subprocess.CalledProcessError, KeyError, OSError, SyntaxError, UnicodeDecodeError) as error:
        print(json.dumps({"status": "failure", "error": str(error)}, sort_keys=True)); return 1
    print(json.dumps({"status": "success", "result": result}, sort_keys=True)); return 0


if __name__ == "__main__":
    sys.exit(main())
