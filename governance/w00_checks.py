#!/usr/bin/env python3
"""W00 local and trusted-CI governance checks."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from w00_contracts import (
    CommandPhase,
    ContractError,
    assess_command,
    current_authorization,
    current_clean_review,
    validate_activation,
    validate_handoff,
)


ACTIVATION_PATH = "activations/ACT-W00-REPOSITORY-GOVERNANCE-v3.json"
ACTIVATION_ID = "ACT-W00-REPOSITORY-GOVERNANCE-v3"
ACTIVATION_SHA256 = "60def3ad374823a3c9065ad43deb6fb41b7ff079de52a212dc7c47c18d0d30c6"
EXPECTED_DESIGNS = {"DR-20", "DR-21", "DR-25", "DR-30", "GOV-01", "GOV-01-ERRATA-01", "GOV-01-ERRATA-02"}
CHECK_NAMES = {"project-integrity", "turn-handoff-integrity", "chatgpt-review-integrity", "owner-merge-record-integrity"}
REPOSITORY = "abbudjoe/biblical-scholar-lab"


def _git(*arguments: str) -> str:
    result = subprocess.run(["git", *arguments], check=True, text=True, capture_output=True)
    return result.stdout.strip()


def _json_file(file_name: str) -> Any:
    return json.loads(Path(file_name).read_text(encoding="utf-8"))


def _git_text(revision: str, file_name: str) -> str:
    return _git("show", f"{revision}:{file_name}")


def _git_bytes(revision: str, file_name: str) -> bytes:
    result = subprocess.run(["git", "show", f"{revision}:{file_name}"], check=True, capture_output=True)
    return result.stdout


def _git_json(revision: str, file_name: str) -> dict[str, Any]:
    value = json.loads(_git_text(revision, file_name))
    if not isinstance(value, dict):
        raise ContractError(f"{file_name} must contain a JSON object")
    return value


def changed_paths(base_sha: str, head_sha: str) -> list[str]:
    output = _git("diff", "--name-only", f"{base_sha}...{head_sha}")
    return [line for line in output.splitlines() if line]


def resolve_activation(revision: str, branch: str) -> dict[str, Any]:
    listing = _git("ls-tree", "-r", "--name-only", revision, "activations")
    candidates: list[tuple[dict[str, Any], str]] = []
    for file_name in listing.splitlines():
        if not file_name.endswith(".json"):
            continue
        record = _git_json(revision, file_name)
        if record.get("status") == "APPROVED" and record.get("root_turn", {}).get("task_branch") == branch:
            validate_activation(record)
            candidates.append((record, file_name))
    if len(candidates) != 1:
        raise ContractError(f"expected one base-approved activation for {branch}; found {len(candidates)}")
    record, file_name = candidates[0]
    _validate_activation_identity(record, revision, file_name)
    return record


def _validate_activation_identity(activation: dict[str, Any], revision: str, file_name: str) -> None:
    design_commit = activation["approved_design_commit"]
    if subprocess.run(["git", "merge-base", "--is-ancestor", design_commit, revision]).returncode:
        raise ContractError("approved design commit is not an ancestor of the protected base")
    if activation["activation_id"] == ACTIVATION_ID and set(activation["approved_design_ids"]) != EXPECTED_DESIGNS:
        raise ContractError("W00 approved design identity differs")
    if activation["activation_id"] == ACTIVATION_ID:
        digest = hashlib.sha256(_git_bytes(revision, file_name)).hexdigest()
        if digest != ACTIVATION_SHA256:
            raise ContractError("W00 activation hash differs")


def _path_allowed(file_name: str, activated_paths: list[str]) -> bool:
    for allowed in activated_paths:
        if allowed.endswith("/") and file_name.startswith(allowed):
            return True
        if file_name == allowed:
            return True
    return False


def validate_change_scope(paths: list[str], activation: dict[str, Any]) -> None:
    disallowed = [file_name for file_name in paths if not _path_allowed(file_name, activation["activated_paths"])]
    if disallowed:
        raise ContractError(f"out-of-scope paths changed: {disallowed}")
    if any(file_name.startswith(("design/", "activations/", "benchmark/", "sources/")) for file_name in paths):
        raise ContractError("immutable design, activation, source, or benchmark content changed")


def _production_path(file_name: str) -> bool:
    excluded = ("test_", "/tests/", "/fixtures/", "handoffs/", "/evidence/")
    return file_name.endswith((".py", ".sh", ".yml", ".yaml")) and not any(part in file_name for part in excluded)


def scan_anti_slop(file_name: str, source: str) -> None:
    token_patterns = ("TO" + "DO", "FIX" + "ME", "Not" + "ImplementedError", "place" + "holder")
    for line_number, line in enumerate(source.splitlines(), start=1):
        if any(token.lower() in line.lower() for token in token_patterns):
            raise ContractError(f"prohibited unfinished marker in {file_name}:{line_number}")
        if re.fullmatch(r"\s*pass(?:\s*#.*)?", line):
            raise ContractError(f"production pass statement in {file_name}:{line_number}")


def _logical_line_count(lines: list[str]) -> int:
    return sum(bool(line.strip()) and not line.lstrip().startswith("#") for line in lines)


def _complexity(node: ast.AST) -> int:
    return 1 + sum(_decision_points(child) for child in ast.walk(node))


def _decision_points(node: ast.AST) -> int:
    if isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.IfExp, ast.Match)):
        return 1
    if isinstance(node, ast.BoolOp):
        return max(0, len(node.values) - 1)
    if isinstance(node, ast.comprehension):
        return 1 + len(node.ifs)
    return 0


def _nesting(node: ast.AST, depth: int = 0) -> int:
    controls = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith, ast.Match)
    maximum = depth
    for child in ast.iter_child_nodes(node):
        child_depth = depth + 1 if isinstance(child, controls) else depth
        maximum = max(maximum, _nesting(child, child_depth))
    return maximum


def validate_python_complexity(file_name: str, source: str) -> None:
    lines = source.splitlines()
    if _logical_line_count(lines) > 500:
        raise ContractError(f"production module exceeds 500 logical lines: {file_name}")
    tree = ast.parse(source, filename=file_name)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        end = node.end_lineno or node.lineno
        logical = _logical_line_count(lines[node.lineno - 1:end])
        if logical > 60 or _complexity(node) > 10 or _nesting(node) > 3:
            raise ContractError(f"DR-30 function threshold exceeded: {file_name}:{node.lineno}")


def _diff_line_counts(base_sha: str, head_sha: str) -> tuple[int, int]:
    additions = deletions = 0
    for line in _git("diff", "--unified=0", f"{base_sha}...{head_sha}").splitlines():
        added, removed = _substantive_delta(line)
        additions += added
        deletions += removed
    return additions, deletions


def _substantive_delta(line: str) -> tuple[int, int]:
    if line.startswith(("+++", "---")) or len(line) < 2 or not line[1:].strip():
        return 0, 0
    if line.startswith("+"):
        return 1, 0
    if line.startswith("-"):
        return 0, 1
    return 0, 0


def validate_budgets(additions: int, deletions: int, production_files: int, activation: dict[str, Any]) -> None:
    budgets = activation["budgets"]
    if additions + deletions > budgets["substantive_changed_lines_hard_limit"]:
        raise ContractError("root-turn substantive line hard limit exceeded")
    if production_files > budgets["handwritten_production_files_hard_limit"]:
        raise ContractError("handwritten production-file hard limit exceeded")


def validate_project(base_sha: str, head_sha: str, branch: str) -> dict[str, Any]:
    activation = resolve_activation(base_sha, branch)
    _validate_project_identity(activation, branch)
    paths = changed_paths(base_sha, head_sha)
    validate_change_scope(paths, activation)
    additions, deletions = _diff_line_counts(base_sha, head_sha)
    production = [file_name for file_name in paths if _production_path(file_name)]
    validate_budgets(additions, deletions, len(production), activation)
    _validate_production_files(production, head_sha)
    _validate_workflow(head_sha)
    return {"changed_paths": paths, "additions": additions, "deletions": deletions, "production_files": production}


def _validate_project_identity(activation: dict[str, Any], branch: str) -> None:
    root = activation["root_turn"]
    if root["task_branch"] != branch:
        raise ContractError("branch or task differs from the activation")


def _validate_production_files(production: list[str], head_sha: str) -> None:
    for file_name in production:
        source = _git_text(head_sha, file_name)
        scan_anti_slop(file_name, source)
        if file_name.endswith(".py"):
            validate_python_complexity(file_name, source)


def _validate_workflow(head_sha: str) -> None:
    workflow = _git_text(head_sha, ".github/workflows/governance-integrity.yml")
    if not CHECK_NAMES.issubset(set(re.findall(r"(?:project|turn-handoff|chatgpt-review|owner-merge-record)-integrity", workflow))):
        raise ContractError("workflow does not expose all four exact check names")
    required_fragments = {"issue_comment", "check-runs", "persist-credentials: false"}
    if not all(fragment in workflow for fragment in required_fragments):
        raise ContractError("trusted workflow trigger, exact-head reporter, or credential isolation is missing")
    if "pull_request_target" in workflow or "workflow_run" in workflow:
        raise ContractError("dangerous privileged workflow trigger is prohibited")


def validate_handoff_commit(record: dict[str, Any], *, final_paths: list[str], parent_sha: str, expected_pair: set[str]) -> None:
    validate_handoff(record)
    if set(final_paths) != expected_pair:
        raise ContractError("final commit is not handoff-only")
    if record["implementation_head_sha"] != parent_sha:
        raise ContractError("implementation_head_sha does not equal the handoff commit parent")


def validate_turn_handoff(base_sha: str, head_sha: str, branch: str, pr_url: str) -> dict[str, Any]:
    activation = resolve_activation(base_sha, branch)
    task_id = activation["root_turn"]["task_id"]
    json_path, markdown_path = _handoff_pair(base_sha, head_sha, task_id)
    record = _git_json(head_sha, json_path)
    parent_sha = _git("rev-parse", f"{head_sha}^")
    final_paths = _git("diff-tree", "--no-commit-id", "--name-only", "-r", head_sha).splitlines()
    validate_handoff_commit(record, final_paths=final_paths, parent_sha=parent_sha, expected_pair={json_path, markdown_path})
    _validate_handoff_identity(record, activation, branch, base_sha, pr_url)
    _validate_handoff_commands(record, activation)
    markdown = _git_text(head_sha, markdown_path)
    if record["implementation_head_sha"] not in markdown or record["status"] not in markdown:
        raise ContractError("Markdown and JSON handoff identities differ")
    return {"turn_id": record["turn_id"], "json": json_path, "markdown": markdown_path, "implementation_head_sha": parent_sha}


def _handoff_pair(base_sha: str, head_sha: str, task_id: str) -> tuple[str, str]:
    prefix = f"handoffs/{task_id}/"
    handoff_paths = list(filter(lambda name: _is_task_handoff(name, prefix), changed_paths(base_sha, head_sha)))
    stems = set(map(lambda name: str(Path(name).with_suffix("")), handoff_paths))
    suffixes = set(map(lambda name: Path(name).suffix, handoff_paths))
    if len(handoff_paths) != 2:
        raise ContractError("exactly one new Markdown/JSON W00 handoff pair is required")
    if len(stems) != 1:
        raise ContractError("exactly one new Markdown/JSON W00 handoff pair is required")
    if suffixes != {".md", ".json"}:
        raise ContractError("exactly one new Markdown/JSON W00 handoff pair is required")
    json_path = next(filter(lambda name: name.endswith(".json"), handoff_paths))
    markdown_path = next(filter(lambda name: name.endswith(".md"), handoff_paths))
    return json_path, markdown_path


def _is_task_handoff(file_name: str, prefix: str) -> bool:
    return file_name.startswith(prefix) and not file_name.endswith(".gitkeep")


def _validate_handoff_identity(record: dict[str, Any], activation: dict[str, Any], branch: str, base_sha: str, pr_url: str) -> None:
    expected = (activation["activation_id"], activation["root_turn"]["task_id"], branch, base_sha, pr_url, REPOSITORY)
    actual = (record["activation_id"], record["task_id"], record["branch"], record["base_sha"], record["pr_url"], record["repository"])
    if actual != expected:
        raise ContractError("handoff task, branch, base, PR, or repository identity differs")


def _validate_handoff_commands(record: dict[str, Any], activation: dict[str, Any]) -> None:
    for command_record in record["commands"]:
        if not isinstance(command_record, dict) or not isinstance(command_record.get("command"), str):
            raise ContractError("handoff command evidence is malformed")
        phase_name = command_record.get("phase", CommandPhase.IMPLEMENTATION.value)
        if phase_name == CommandPhase.W00_GOVERNANCE.value and activation["activation_id"] != ACTIVATION_ID:
            raise ContractError("W00 governance exception cannot be reused")
        try:
            phase = CommandPhase(phase_name)
        except ValueError as error:
            raise ContractError("handoff command phase is invalid") from error
        decision = assess_command(command_record["command"], phase)
        if not decision.allowed:
            raise ContractError(f"handoff records a prohibited command: {decision.reason}")


def _comments(file_name: str) -> list[dict[str, Any]]:
    value = _json_file(file_name)
    if isinstance(value, list) and value and all(isinstance(item, list) for item in value):
        value = [entry for page in value for entry in page]
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ContractError("comments input must be an array of objects")
    return value


def _pr_identity(pr_file: str) -> tuple[dict[str, Any], str, str, str]:
    pr = _json_file(pr_file)
    if not isinstance(pr, dict) or pr.get("state") != "open" or pr.get("base", {}).get("ref") != "main":
        raise ContractError("target PR must be open against main")
    return pr, pr["html_url"], pr["base"]["sha"], pr["head"]["sha"]


def validate_review_comments(pr_file: str, comments_file: str) -> dict[str, Any]:
    pr, pr_url, base_sha, head_sha = _pr_identity(pr_file)
    activation = resolve_activation(base_sha, pr["head"]["ref"])
    record = current_clean_review(_comments(comments_file), pr_url=pr_url, activation_id=activation["activation_id"], base_sha=base_sha, head_sha=head_sha)
    return {"review_id": record["review_id"], "reviewed_head_sha": head_sha}


def validate_authorization_comments(pr_file: str, comments_file: str) -> dict[str, Any]:
    pr, pr_url, base_sha, head_sha = _pr_identity(pr_file)
    activation = resolve_activation(base_sha, pr["head"]["ref"])
    comments = _comments(comments_file)
    review = current_clean_review(comments, pr_url=pr_url, activation_id=activation["activation_id"], base_sha=base_sha, head_sha=head_sha)
    record = current_authorization(comments, repository=REPOSITORY, pr_url=pr_url, activation_id=activation["activation_id"], head_sha=head_sha, review_id=review["review_id"])
    return {"authorization_id": record["authorization_id"], "authorized_head_sha": head_sha}


def validate_repository_settings(record: dict[str, Any]) -> None:
    actual = (
        record.get("default_branch"), record.get("visibility", "").lower(),
        record.get("allow_squash_merge"), record.get("allow_merge_commit"),
        record.get("allow_rebase_merge"), record.get("allow_auto_merge"),
        record.get("delete_branch_on_merge"),
    )
    if actual != ("main", "public", True, False, False, False, True):
        raise ContractError("live repository merge configuration differs")


def validate_ruleset(record: dict[str, Any]) -> None:
    if record.get("name") != "main-quality-and-authorization-gates" or record.get("target") != "branch" or record.get("enforcement") != "active":
        raise ContractError("ruleset identity or enforcement differs")
    if record.get("bypass_actors") != []:
        raise ContractError("ruleset bypass list is not empty")
    includes = record.get("conditions", {}).get("ref_name", {}).get("include", [])
    if "~DEFAULT_BRANCH" not in includes and "refs/heads/main" not in includes:
        raise ContractError("ruleset does not target default branch/main")
    rules = {rule.get("type"): rule for rule in record.get("rules", [])}
    if not {"deletion", "non_fast_forward", "required_linear_history", "pull_request", "required_status_checks"}.issubset(rules):
        raise ContractError("ruleset is missing a required rule")
    _validate_pull_request_rule(rules["pull_request"])
    _validate_status_rule(rules["required_status_checks"])


def _validate_pull_request_rule(rule: dict[str, Any]) -> None:
    pull = rule.get("parameters", {})
    if pull.get("required_approving_review_count") != 0 or pull.get("require_code_owner_review") is not False or pull.get("required_review_thread_resolution") is not True:
        raise ContractError("pull-request rule parameters differ")


def _validate_status_rule(rule: dict[str, Any]) -> None:
    statuses = rule.get("parameters", {})
    contexts = statuses.get("required_status_checks", [])
    if statuses.get("strict_required_status_checks_policy") is not True or {item.get("context") for item in contexts} != CHECK_NAMES:
        raise ContractError("strict required status checks differ")
    if any(not isinstance(item.get("integration_id"), int) or item["integration_id"] <= 0 for item in contexts):
        raise ContractError("required checks are not pinned to a GitHub App integration")


def validate_review_limit(record: dict[str, Any]) -> None:
    expected = (record.get("repository"), record.get("setting"), record.get("enabled"), record.get("verification_method"))
    if expected != (REPOSITORY, "Limit to users explicitly granted read or higher access", True, "SUPPORTED_AUTHENTICATED_BROWSER"):
        raise ContractError("public code-review limit receipt differs")
    if not record.get("verified_at") or not record.get("evidence"):
        raise ContractError("public code-review limit evidence is incomplete")


def validate_codeowners(text: str) -> None:
    required = {"*", "/.github/", "/AGENTS.md", "/EXPERIMENT_AUTHORITY.md", "/governance/", "/activations/", "/handoffs/", "/reviews/"}
    owned = {line.split()[0] for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#") and line.split()[-1] == "@abbudjoe"}
    if not required.issubset(owned):
        raise ContractError(f"CODEOWNERS patterns missing: {sorted(required - owned)}")


def validate_live_governance(repository_file: str, ruleset_file: str, review_limit_file: str, codeowners_file: str) -> dict[str, Any]:
    validate_repository_settings(_json_file(repository_file))
    validate_ruleset(_json_file(ruleset_file))
    validate_review_limit(_json_file(review_limit_file))
    validate_codeowners(Path(codeowners_file).read_text(encoding="utf-8"))
    return {"repository": REPOSITORY, "ruleset": "main-quality-and-authorization-gates", "required_checks": sorted(CHECK_NAMES), "code_review_limit": True, "codeowners": True}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="check", required=True)
    project = sub.add_parser("project-integrity")
    handoff = sub.add_parser("turn-handoff-integrity")
    for command in (project, handoff):
        command.add_argument("--base-sha", required=True)
        command.add_argument("--head-sha", required=True)
        command.add_argument("--branch", required=True)
    handoff.add_argument("--pr-url", required=True)
    for name in ("chatgpt-review-integrity", "owner-merge-record-integrity"):
        command = sub.add_parser(name)
        command.add_argument("--pr-json", required=True)
        command.add_argument("--comments-json", required=True)
    live = sub.add_parser("live-governance")
    live.add_argument("--repository-json", required=True)
    live.add_argument("--ruleset-json", required=True)
    live.add_argument("--review-limit-json", required=True)
    live.add_argument("--codeowners", required=True)
    policy = sub.add_parser("command-policy")
    policy.add_argument("--phase", choices=[phase.value for phase in CommandPhase], required=True)
    policy.add_argument("command")
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
    if arguments.check == "live-governance":
        return validate_live_governance(arguments.repository_json, arguments.ruleset_json, arguments.review_limit_json, arguments.codeowners)
    decision = assess_command(arguments.command, CommandPhase(arguments.phase))
    if not decision.allowed:
        raise ContractError(decision.reason)
    return {"command_allowed": True, "reason": decision.reason}


def main() -> int:
    try:
        result = _dispatch(_parser().parse_args())
    except (ContractError, json.JSONDecodeError, subprocess.CalledProcessError, KeyError, OSError, SyntaxError) as error:
        print(json.dumps({"status": "failure", "error": str(error)}, sort_keys=True))
        return 1
    print(json.dumps({"status": "success", "result": result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
