"""Pure W00A records and exact command-policy decisions."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import shlex
from collections.abc import Iterable
from datetime import datetime
from enum import Enum
from typing import Any, cast
from urllib.parse import urlparse

REPOSITORY = "abbudjoe/biblical-scholar-lab"
BRANCH = "codex/w00-repository-governance"
ACTIVATION = "ACT-W00-REPOSITORY-GOVERNANCE-v3"
RULESET = "20960975"
ENVIRONMENT = "owner-merge-authorization"
TITLE = "W00A — Governance Validation Foundation"
SHA = re.compile(r"[0-9a-f]{40}")
DIGEST = re.compile(r"[0-9a-f]{64}")
COMPLETION = "<!-- BSL_ROOT_TURN_COMPLETION_V1 -->"
REVIEW = "<!-- BSL_CHATGPT_REVIEW_V1 -->"
INACTIVE_MARKERS = ("<!-- BSL_OWNER_MERGE_AUTHORIZATION_V1 -->", "<!-- BSL_MERGE_RECEIPT_V1 -->")
PROHIBITED_CLAIMS = ("MERGE_READY", "SAFE_TO_MERGE", "OWNER_AUTHORIZATION_ACTIVE", "MERGE_ONLY_PATH_ACTIVE", "TRUSTED_VALIDATOR_LIVE_PROVEN_FOR_PR1")
STATUSES = {"READY_FOR_CHATGPT_REVIEW", "BLOCKED_MISSING_EVIDENCE", "BLOCKED_DEPENDENCY", "BLOCKED_REQUIRES_DESIGN_REVIEW", "BLOCKED_REQUIRES_SOL_REPAIR", "SPLIT_REQUIRED", "NO_CHANGE", "FAILED"}
TOKEN_OVERRIDES = {"GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN"}
W00A_RULESET_PAYLOAD_SHA256 = "a52b3d6c6a94a14a89fba182eb29ebc34af0fc6a6f34465031c7887d769caf65"
HANDOFF_IDENTITY_FIELDS = {"schema_version", "project_id", "activation_id", "task_id", "turn_id", "codex_run_id", "status", "repository", "branch", "base_sha", "implementation_head_sha", "pr_url", "github_actor_login", "github_auth_mode", "github_auth_preflight"}
HANDOFF_FIELDS = HANDOFF_IDENTITY_FIELDS | {"objective", "acceptance_criteria", "design_conformance", "changes", "review_targets", "commands", "evaluations", "artifacts", "delegated_operations", "complexity_receipt", "known_risks", "decisions_required", "billable_actions", "next_required_action", "merge_performed", "next_task_started"}
COMPLEXITY_FIELDS = {"production_loc_added", "production_loc_removed", "test_loc_added", "test_loc_removed", "generated_loc", "production_files_added", "production_files_removed", "modules_added", "modules_removed", "tables_added", "migrations_added", "endpoints_added", "cli_commands_added", "dependencies_added", "dependencies_removed", "public_contracts_changed", "abstractions", "simpler_alternatives_considered", "known_duplication_or_debt", "waivers", "simplicity_conformance"}
ACTIVATION_FIELDS = {"schema_version", "activation_id", "status", "approved_design_commit", "approved_design_ids", "root_turn", "objective", "vertical_slice_id", "activated_user_visible_capability", "activated_invariants", "activated_paths", "activated_contracts", "activated_interfaces", "activated_data_stores", "activated_adapters", "required_tests", "required_evidence", "explicit_non_goals", "prohibited_scaffolding", "budgets", "completion_criteria", "owner_approval"}
REVIEW_FIELDS = {"schema_version", "review_id", "pr_url", "activation_id", "base_sha", "reviewed_head_sha", "reviewer", "disposition", "summary", "findings", "evidence_reviewed", "required_next_action", "review_timestamp"}
VALIDATION_FILES = ["governance/w00_contracts.py", "governance/w00_checks.py", "governance/test_w00_checks.py"]
VALIDATION_COMMANDS = (
    ["python3", "-m", "unittest", "-v", VALIDATION_FILES[-1]],
    ["python3", "-m", "py_compile", *VALIDATION_FILES[:-1]],
    ["uvx", "--from", "coverage", "coverage", "run", "--branch", "-m", "unittest", VALIDATION_FILES[-1]],
    ["uvx", "--from", "coverage", "coverage", "report", "--show-missing", "--fail-under=90"],
    ["uvx", "ruff", "check", "--config", "governance/ruff.toml", *VALIDATION_FILES],
    ["uvx", "ruff", "format", "--config", "governance/ruff.toml", *VALIDATION_FILES],
    ["uvx", "ruff", "format", "--check", "--config", "governance/ruff.toml", *VALIDATION_FILES],
    ["uvx", "mypy", "--strict", *VALIDATION_FILES[:-1]],
    ["uvx", "detect-secrets", "scan", "--all-files"],
    ["uvx", "zizmor", ".github/workflows/governance-integrity.yml", ".github/workflows/trusted-governance-validator.yml"],
    ["shasum", "-a", "256", "-c", "governance/GOV-01-artifacts.sha256"],
)


class ContractError(ValueError):
    """An explicit governance contract failed."""


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _logical(lines: list[str]) -> int:
    return sum(bool(line.strip()) and not line.lstrip().startswith("#") for line in lines)


def _complexity(node: ast.AST) -> int:
    controls = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.IfExp, ast.Match)
    return 1 + sum(isinstance(item, controls) for item in ast.walk(node)) + sum(max(0, len(item.values) - 1) for item in ast.walk(node) if isinstance(item, ast.BoolOp))


def _nesting(node: ast.AST, depth: int = 0) -> int:
    controls = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith, ast.Match)
    return max([depth, *(_nesting(child, depth + int(isinstance(child, controls))) for child in ast.iter_child_nodes(node))])


def validate_python(path: str, source: str) -> None:
    lines, tree = source.splitlines(), ast.parse(source, filename=path)
    need(_logical(lines) <= 500, f"production module exceeds DR-30: {path}")
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        segment = lines[node.lineno - 1 : (node.end_lineno or node.lineno)]
        need(not isinstance(node, ast.ClassDef) or _logical(segment) <= 250, f"class exceeds DR-30: {path}:{node.lineno}")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            need(_logical(segment) <= 60 and _complexity(node) <= 10 and _nesting(node) <= 3, f"function exceeds DR-30: {path}:{node.lineno}")


def exact(record: dict[str, Any], required: set[str], optional: set[str] | None = None) -> None:
    optional = optional or set()
    need(record.keys() <= required | optional and required <= record.keys(), "record fields differ")


def cli_surface(tree: ast.Module) -> set[str]:
    definitions = [node.value for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "CLI_SPECS" for target in node.targets)] + [node.value.args[0] for node in tree.body if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and isinstance(node.value.func.value, ast.Name) and (node.value.func.value.id, node.value.func.attr, len(node.value.args)) == ("CLI_SPECS", "update", 1)]
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)]
    parsers = [call for call in calls if getattr(call.func, "attr", None) == "add_parser"]
    shapes = {(type(call.args[0]), getattr(call.args[0], "id", getattr(call.args[0], "value", None))) for call in parsers if len(call.args) == 1 and not call.keywords}
    writes = [node for node in ast.walk(tree) if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Delete)) and any(isinstance(name, ast.Name) and name.id == "CLI_SPECS" for target in (node.targets if isinstance(node, (ast.Assign, ast.Delete)) else [node.target]) for name in ast.walk(target))]
    methods = [attribute.attr for call in calls if isinstance(attribute := call.func, ast.Attribute) and isinstance(attribute.value, ast.Name) and attribute.value.id == "CLI_SPECS"]
    keys = [key.value for definition in definitions if isinstance(definition, ast.Dict) for key in definition.keys if isinstance(key, ast.Constant) and isinstance(key.value, str)]
    need(len(definitions) == 2 and all(isinstance(item, ast.Dict) for item in definitions) and len(keys) == len(set(keys)) == sum(len(cast(ast.Dict, item).keys) for item in definitions) and len(writes) == 1 and sorted(methods) == ["items", "update"] and len(parsers) == 2 and shapes == {(ast.Name, "check"), (ast.Constant, "command-policy")}, "CLI parser surface is unclassified")
    return set(keys) | {"command-policy"}


def strict_json(source: str | bytes) -> Any:
    def unique(items: list[tuple[str, Any]]) -> dict[str, Any]:
        output = dict(items)
        need(len(output) == len(items), "JSON object key is duplicated")
        return output

    def finite(value: str) -> float:
        number = float(value)
        need(abs(number) < float("inf"), f"JSON number is non-finite: {value}")
        return number

    try:
        return json.loads(source, object_pairs_hook=unique, parse_constant=finite, parse_float=finite)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ContractError("JSON is malformed") from error


def timestamp(value: Any) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else None
    except ValueError as error:
        raise ContractError("timestamp is invalid") from error
    need(parsed is not None and parsed.utcoffset() is not None, "timestamp requires a timezone")
    return cast(datetime, parsed)


def validate_auth(login: str, environment: Iterable[str]) -> None:
    need(login == "abbudjoe", "active GitHub login differs")
    need(not TOKEN_OVERRIDES.intersection(environment), "token override is present")


def validate_activation(record: dict[str, Any]) -> None:
    exact(record, ACTIVATION_FIELDS)
    root, owner = record.get("root_turn"), record.get("owner_approval")
    need(isinstance(root, dict) and isinstance(owner, dict), "activation ownership is malformed")
    root, owner = cast(dict[str, Any], root), cast(dict[str, Any], owner)
    identity = (record.get("schema_version"), record.get("status"), root.get("model"), root.get("reasoning_effort"), root.get("base_branch"))
    need(identity == ("1.0", "APPROVED", "gpt-5.6", "max", "main"), "activation identity differs")
    need(re.fullmatch(r"ACT-[A-Z0-9-]+-v[0-9]+", str(record.get("activation_id"))) is not None, "activation ID differs")
    need(re.fullmatch(r"codex/[a-z0-9][a-z0-9-]*", str(root.get("task_branch"))) is not None, "activation branch differs")
    need(isinstance(root.get("luna_delegation_allowed"), bool), "activation delegation boundary differs")
    need(record.get("activation_id") != ACTIVATION or (root.get("task_branch"), root.get("luna_delegation_allowed")) == (BRANCH, False), "W00 activation boundary differs")
    need(isinstance(record.get("approved_design_commit"), str) and SHA.fullmatch(record["approved_design_commit"]) is not None, "approved design commit differs")
    need(isinstance(record.get("approved_design_ids"), list) and bool(record["approved_design_ids"]) and all(isinstance(item, str) for item in record["approved_design_ids"]), "approved design IDs differ")
    need((owner.get("owner"), owner.get("status")) == ("Joseph Abbud", "APPROVED"), "activation approval differs")
    timestamp(owner.get("approved_at"))
    paths = record.get("activated_paths")
    need(isinstance(paths, list) and not any(str(path).startswith("activations/") for path in paths), "activation paths are invalid")


def _array(record: dict[str, Any], field: str, kind: type) -> None:
    value = record.get(field)
    need(isinstance(value, list) and all(isinstance(item, kind) for item in value), f"{field} has an invalid type")


def validate_handoff(record: dict[str, Any], *, w00a: bool = False) -> None:
    exact(record, HANDOFF_FIELDS, {"compare_url"})
    need(not any(item.lower() in json.dumps(record).lower() for item in PROHIBITED_CLAIMS), "handoff makes a prohibited capability claim")
    _handoff_identity(record)
    _handoff_design(record, w00a)
    _validate_handoff_details(record)


def _handoff_identity(record: dict[str, Any]) -> None:
    identity = (record.get("schema_version"), record.get("project_id"), record.get("activation_id"), record.get("task_id"), record.get("repository"), record.get("branch"))
    need(identity[:2] == ("1.0", "biblical-scholar-lab") and identity[4] == REPOSITORY, "handoff identity differs")
    need(all(isinstance(item, str) and item for item in (identity[2], identity[3], record.get("turn_id"), record.get("codex_run_id"))) and re.fullmatch(r"codex/[a-z0-9][a-z0-9-]*", str(identity[5])) is not None, "handoff task identity differs")
    need(record.get("status") in STATUSES and record.get("next_required_action") == "CHATGPT_REVIEW", "handoff transition differs")
    need(record.get("merge_performed") is False and record.get("next_task_started") is False, "handoff crossed the stop boundary")
    for field in ("base_sha", "implementation_head_sha"):
        need(isinstance(record.get(field), str) and SHA.fullmatch(record[field]) is not None, f"{field} differs")
    need(_url(record.get("pr_url")) and (record.get("compare_url") is None or _url(record.get("compare_url"))), "handoff URL is invalid")
    auth = record.get("github_auth_preflight")
    need(isinstance(auth, dict), "handoff auth evidence differs")
    exact(cast(dict[str, Any], auth), {"hostname", "active_login", "auth_healthy", "token_override_present", "token_exposed"}, {"receipt_path"})
    observed = tuple(auth.get(key) for key in ("hostname", "active_login")) if isinstance(auth, dict) else ()
    need(observed == ("github.com", "abbudjoe") and cast(dict[str, Any], auth).get("auth_healthy") is True and cast(dict[str, Any], auth).get("token_override_present") is False and cast(dict[str, Any], auth).get("token_exposed") is False, "handoff auth evidence differs")
    need(cast(dict[str, Any], auth).get("receipt_path") is None or isinstance(cast(dict[str, Any], auth).get("receipt_path"), str), "handoff auth receipt differs")
    need((record.get("github_actor_login"), record.get("github_auth_mode")) == ("abbudjoe", "GH_CLI_EXISTING_AUTH"), "handoff actor differs")


def _handoff_design(record: dict[str, Any], w00a: bool) -> None:
    design = record.get("design_conformance")
    need(isinstance(design, dict) and design.get("unapproved_design_changes_executed") is False, "handoff design evidence differs")
    design = cast(dict[str, Any], design)
    exact(design, {"status", "approved_design_ids", "unapproved_design_changes_executed"})
    expected = "BLOCKED_REQUIRES_DESIGN_REVIEW" if record["status"] == "BLOCKED_REQUIRES_DESIGN_REVIEW" else "CONFORMING"
    need(design["status"] == expected and isinstance(design["approved_design_ids"], list) and all(isinstance(item, str) for item in design["approved_design_ids"]) and (not w00a or "GOV-01-S02" in design["approved_design_ids"]), "handoff design evidence differs")


def _validate_handoff_details(record: dict[str, Any]) -> None:
    arrays = (("acceptance_criteria", str), ("changes", dict), ("review_targets", dict), ("commands", dict), ("evaluations", dict), ("artifacts", dict), ("delegated_operations", dict), ("known_risks", str), ("decisions_required", str))
    for field, kind in arrays:
        _array(record, field, kind)
    need(isinstance(record.get("objective"), str) and bool(record["objective"].strip()) and bool(record["acceptance_criteria"]) and not any(item.get("write_performed") is not False or item.get("role") == "luna_runner" for item in record["delegated_operations"]), "handoff detail or delegation boundary differs")
    _validate_complexity(record.get("complexity_receipt"), record["status"])
    billable = record.get("billable_actions")
    need(isinstance(billable, dict) and {"performed", "actual_cost_usd"} <= billable.keys() <= {"performed", "actual_cost_usd", "campaign_ids"} and billable.get("performed") is False and isinstance(cost := billable.get("actual_cost_usd"), (int, float)) and not isinstance(cost, bool) and cost == 0 and ("campaign_ids" not in billable or isinstance(billable["campaign_ids"], list) and all(isinstance(item, str) for item in billable["campaign_ids"])), "billable work was reported")


def _validate_complexity(value: Any, status: str) -> None:
    need(isinstance(value, dict), "complexity receipt is absent")
    receipt = cast(dict[str, Any], value)
    exact(receipt, COMPLEXITY_FIELDS)
    counts = ("production_loc_added", "production_loc_removed", "test_loc_added", "test_loc_removed", "generated_loc", "production_files_added", "production_files_removed")
    need(all(isinstance(receipt.get(key), int) and not isinstance(receipt[key], bool) and receipt[key] >= 0 for key in counts), "complexity counts differ")
    arrays = COMPLEXITY_FIELDS - set(counts) - {"simplicity_conformance"}
    need(all(isinstance(receipt.get(key), list) and all(isinstance(item, str) for item in receipt[key]) for key in arrays), "complexity arrays differ")
    expected = "BLOCKED_REQUIRES_SPLIT" if status == "SPLIT_REQUIRED" else "PASS"
    need(receipt.get("simplicity_conformance") == expected, "complexity disposition differs")


def _url(value: Any) -> bool:
    parsed = urlparse(value) if isinstance(value, str) else None
    return bool(parsed and parsed.scheme == "https" and parsed.netloc)


def marked(comments: Iterable[dict[str, Any]], marker: str) -> list[tuple[dict[str, Any], int, datetime]]:
    pattern, output = (re.compile(re.escape(marker) + r".*?```json\s*(.*?)\s*```", re.DOTALL), [])
    for comment in comments:
        need(isinstance(comment, dict), "comment is not an object")
        if marker not in str(comment.get("body", "")):
            continue
        created, updated = (timestamp(comment.get("created_at")), timestamp(comment.get("updated_at")))
        matches = pattern.findall(str(comment["body"]))
        need(created == updated and len(matches) == 1 and isinstance(comment.get("id"), int), "marked comment is edited or malformed")
        record = strict_json(matches[0])
        need(isinstance(record, dict), "marked comment record is not an object")
        output.append((record, comment["id"], created))
    need([item[2] for item in output] == sorted(item[2] for item in output), "marked comments were reordered")
    return output


def current_completion(comments: Iterable[dict[str, Any]], expected: tuple[Any, ...]) -> tuple[int, datetime]:
    entries = marked(comments, COMPLETION)
    fields = ("activation_id", "task_id", "turn_id", "implementation_head_sha", "live_pr_head_sha", "handoff_markdown", "handoff_json", "status", "next_required_action")
    need(len({item[0].get("turn_id") for item in entries}) == len(entries), "completion ID was reused")
    matches = [item for item in entries if tuple(item[0].get(key) for key in fields) == expected]
    need(len(matches) == 1, "one exact completion record is required")
    return matches[0][1], matches[0][2]


def _review_schema(record: dict[str, Any]) -> None:
    exact(record, REVIEW_FIELDS, {"supersedes_review_id"})
    need(isinstance(record.get("review_id"), str) and isinstance(record.get("summary"), str) and isinstance(record.get("findings"), list) and isinstance(record.get("evidence_reviewed"), list) and all(isinstance(item, str) for item in record["evidence_reviewed"]) and (record.get("supersedes_review_id") is None or isinstance(record.get("supersedes_review_id"), str)), "review schema differs")


def validate_record_order(comments: Iterable[dict[str, Any]], completion_at: datetime, identity: tuple[str, str, str, str], handoff_url: str) -> str:
    values = list(comments)
    need(not any(marker in str(item.get("body", "")) for marker in INACTIVE_MARKERS for item in values), "W00B authorization or merge record is inactive")
    all_reviews = marked(values, REVIEW)
    for record, _, _ in all_reviews:
        _review_schema(record)
    ids = [item[0].get("review_id") for item in all_reviews]
    need(len(ids) == len(set(ids)), "review ID is reused")
    reviews = [item for item in all_reviews if item[0].get("reviewed_head_sha") == identity[3]]
    if not reviews:
        return "HANDOFF"
    need(reviews[-1][2] > completion_at, "review precedes completion")
    review, _, created = reviews[-1]
    actual = tuple(review.get(key) for key in ("pr_url", "activation_id", "base_sha", "reviewed_head_sha"))
    valid = (review.get("schema_version"), review.get("reviewer"), review.get("disposition"), review.get("required_next_action")) == ("1.0", "ChatGPT", "CHATGPT_REVIEW_CLEAN", "OWNER_AUTHORIZATION")
    need(actual == identity and valid and handoff_url in review.get("evidence_reviewed", []), "current review binding differs")
    need(timestamp(review.get("review_timestamp")) <= created, "review timestamp follows its comment")
    return "REVIEW"


class CommandPhase(Enum):
    IMPLEMENTATION = "implementation"
    W00A_GOVERNANCE = "w00a-governance"


def assess_command(command: str, phase: CommandPhase, *, branch: str = BRANCH, pr_number: int = 1, governance_available: bool = False, governance_payload: Any = None) -> tuple[bool, str]:
    if re.search(r"[\n\r;&|`<>$\\*?\[\]{}()~#!]", command):
        return False, "shell composition or expansion is prohibited"
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False, "command cannot be parsed"
    if not tokens or tokens[0] in {"env", "command", "sudo", "xargs", "bash", "sh", "zsh"} or "=" in tokens[0]:
        return (False, "prefix, alias, nested shell, or environment smuggling is prohibited")
    if phase is CommandPhase.W00A_GOVERNANCE:
        exact_put = ["gh", "api", "--method", "PUT", f"repos/{REPOSITORY}/rulesets/{RULESET}", "--input", ".codex-tmp-ruleset-w00a.json"]
        digest = hashlib.sha256(json.dumps(governance_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        allowed = governance_available and tokens == exact_put and digest == W00A_RULESET_PAYLOAD_SHA256
        return (allowed, "exact unconsumed W00A ruleset adjustment" if allowed else "governance mutation is unavailable or differs")
    return _implementation(tokens, branch, pr_number)


def _implementation(tokens: list[str], branch: str, pr_number: int) -> tuple[bool, str]:
    github = _github_operation(tokens, pr_number)
    if github is not None:
        return github
    if tokens and tokens[0] == "git":
        return _git(tokens, branch)
    return _local(tokens)


def _github_operation(tokens: list[str], pr_number: int) -> tuple[bool, str] | None:
    if tokens[:2] == ["gh", "auth"]:
        allowed = tokens == ["gh", "auth", "status", "--active", "--hostname", "github.com"]
        return (allowed, "redacted auth preflight" if allowed else "authentication display or mutation is prohibited")
    if tokens[:2] == ["gh", "api"]:
        endpoint = tokens[2].lstrip("/").split("?", 1)[0] if len(tokens) == 3 else ""
        patterns = (r"user", rf"repos/{REPOSITORY}", rf"repos/{REPOSITORY}/pulls/1", rf"repos/{REPOSITORY}/issues/1/comments", rf"repos/{REPOSITORY}/actions/(?:workflows|runs/[0-9]+)", rf"repos/{REPOSITORY}/rulesets/{RULESET}", rf"repos/{REPOSITORY}/(?:codeowners/errors|contents/\.github/CODEOWNERS|commits/[0-9a-f]{{40}}/check-runs)", rf"repos/{REPOSITORY}/environments/{ENVIRONMENT}")
        allowed = any(re.fullmatch(pattern, endpoint) for pattern in patterns)
        return (allowed, "bounded API read" if allowed else "mutating or unbounded API is prohibited")
    return _pr_operation(tokens, pr_number)


def _pr_operation(tokens: list[str], pr_number: int) -> tuple[bool, str] | None:
    number = str(pr_number)
    exact_gh = (["gh", "pr", "view", number, "--repo", REPOSITORY], ["gh", "pr", "checks", number, "--repo", REPOSITORY], ["gh", "pr", "comment", number, "--repo", REPOSITORY, "--body-file", ".codex-tmp-pr-completion.md"])
    edit = len(tokens) == 10 and tokens[:4] == ["gh", "pr", "edit", number] and tokens[4:8] == ["--repo", REPOSITORY, "--title", TITLE] and tokens[8:] == ["--body-file", ".codex-tmp-pr-body.md"]
    if tokens in exact_gh or edit:
        return True, "exact PR operation"
    return None


def _git(tokens: list[str], branch: str) -> tuple[bool, str]:
    if tokens == ["git", "push", "origin", branch] and re.fullmatch(r"codex/[a-z0-9][a-z0-9-]*", branch):
        return True, "exact task-branch push"
    if len(tokens) == 4 and tokens[1:3] == ["commit", "-m"] and tokens[3]:
        return True, "new commit"
    if len(tokens) > 2 and tokens[1] == "add":
        safe = all(_staging_path(item) for item in tokens[2:])
        return bool(safe), "explicit staging" if safe else "broad or unsafe staging is prohibited"
    return _git_read(tokens)


def _staging_path(path: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*", path)) and ".." not in path.split("/") and (path == "AGENTS.md" or path.startswith((".github/workflows/", "governance/", "handoffs/W00/")))


def _git_read(tokens: list[str]) -> tuple[bool, str]:
    fixed = (["git", "status", "--short"], ["git", "diff", "--check"], ["git", "fsck", "--full"])
    revision = len(tokens) == 3 and tokens[:2] == ["git", "rev-parse"] and bool(re.fullmatch(r"HEAD\^?|main|origin/main|[0-9a-f]{40}", tokens[2]))
    return ((tokens in fixed or revision), "exact Git read" if tokens in fixed or revision else "Git operation is prohibited")


def _local(tokens: list[str]) -> tuple[bool, str]:
    if tokens in VALIDATION_COMMANDS:
        return True, "exact validation command"
    allowed = _validator_command(tokens)
    return (allowed, "governance validator" if allowed else "local command is not allowlisted")


def _validator_command(tokens: list[str]) -> bool:
    if len(tokens) < 3 or tokens[:2] != ["python3", "governance/w00_checks.py"]:
        return False
    specs = {
        "package-integrity": (["--revision"], []),
        "project-integrity": (["--base-sha", "--head-sha", "--branch"], []),
        "turn-handoff-integrity": (["--base-sha", "--head-sha", "--branch", "--pr-url"], []),
        "candidate-metadata": (["--base-sha", "--head-sha", "--tree-json", "--compare-json"], []),
        "trusted-governance": (["--repository", "--pr-number", "--base-sha", "--head-sha", "--trusted-revision", "--branch", "--event", "--run-id", "--run-attempt", "--candidate-repository", "--tree-json", "--compare-json", "--output"], []),
        "completion-integrity": (["--base-sha", "--head-sha", "--branch", "--pr-json", "--comments-json"], []),
        "live-governance": (["--expected-head", "--review-limit-observed-at", "--environment-ui-observed-at"], ["--review-limit-enabled", "--admin-bypass-disabled"]),
    }
    value_flags, boolean_flags = specs.get(tokens[2], ([], []))
    count, arguments = len(value_flags) * 2, tokens[3:]
    valid_pairs = arguments[:count:2] == value_flags and all(not value.startswith("-") for value in arguments[1:count:2])
    values = dict(zip(value_flags, arguments[1:count:2], strict=True)) if valid_pairs else {}
    return bool(value_flags) and valid_pairs and all(_cli_value(flag, value) for flag, value in values.items()) and arguments[count:] == boolean_flags


def _cli_value(flag: str, value: str) -> bool:
    if flag in {"--base-sha", "--head-sha", "--trusted-revision", "--revision", "--expected-head"}:
        return value == "HEAD" or SHA.fullmatch(value) is not None
    if flag == "--repository":
        return value == REPOSITORY
    if flag == "--branch":
        return re.fullmatch(r"codex/[a-z0-9][a-z0-9-]*", value) is not None
    if flag == "--pr-url":
        return re.fullmatch(rf"https://github\.com/{REPOSITORY}/pull/[1-9][0-9]*", value) is not None
    if flag in {"--pr-number", "--run-id", "--run-attempt"}:
        return value.isdigit() and int(value) > 0
    if flag == "--event":
        return value == "pull_request_target"
    if flag.endswith("observed-at"):
        return re.fullmatch(r"[0-9T:+.Z-]+", value) is not None
    return re.fullmatch(r"\.codex-tmp-[A-Za-z0-9.-]+", value) is not None
