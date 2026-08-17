"""Pure W00 governance contracts and command-policy decisions."""

from __future__ import annotations

import json
import re
import shlex
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Iterable
from urllib.parse import urlparse


SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REVIEW_MARKER = "<!-- BSL_CHATGPT_REVIEW_V1 -->"
AUTHORIZATION_MARKER = "<!-- BSL_OWNER_MERGE_AUTHORIZATION_V1 -->"
ALLOWED_HANDOFF_STATUSES = {
    "READY_FOR_CHATGPT_REVIEW",
    "BLOCKED_MISSING_EVIDENCE",
    "BLOCKED_DEPENDENCY",
    "BLOCKED_REQUIRES_DESIGN_REVIEW",
    "BLOCKED_REQUIRES_SOL_REPAIR",
    "NO_CHANGE",
    "FAILED",
}
TOKEN_OVERRIDE_NAMES = {"GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN"}


class ContractError(ValueError):
    """A machine-readable governance record violated its contract."""


def _fields(record: dict[str, Any], required: set[str], optional: set[str] = set()) -> None:
    missing = required - record.keys()
    extra = record.keys() - required - optional
    if missing or extra:
        raise ContractError(f"record fields differ: missing={sorted(missing)} extra={sorted(extra)}")


def _typed(record: dict[str, Any], field: str, expected: type) -> Any:
    value = record.get(field)
    if not isinstance(value, expected):
        raise ContractError(f"{field} must be {expected.__name__}")
    return value


def _nonempty_strings(record: dict[str, Any], fields: Iterable[str]) -> None:
    invalid = [field for field in fields if not isinstance(record.get(field), str) or not record[field]]
    if invalid:
        raise ContractError(f"fields must be nonempty strings: {invalid}")


def _sha(value: Any, field: str) -> str:
    if not isinstance(value, str) or not SHA_RE.fullmatch(value):
        raise ContractError(f"{field} must be a lowercase 40-character SHA")
    return value


def _timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ContractError(f"{field} must be an RFC3339 timestamp")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ContractError(f"{field} must be an RFC3339 timestamp") from error


def _uri(value: Any, field: str) -> str:
    parsed = urlparse(value) if isinstance(value, str) else None
    if not parsed or parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ContractError(f"{field} must be an HTTP(S) URI")
    return value


ACTIVATION_FIELDS = {
    "schema_version", "activation_id", "status", "approved_design_commit",
    "approved_design_ids", "root_turn", "objective", "vertical_slice_id",
    "activated_user_visible_capability", "activated_invariants", "activated_paths",
    "activated_contracts", "activated_interfaces", "activated_data_stores",
    "activated_adapters", "required_tests", "required_evidence", "explicit_non_goals",
    "prohibited_scaffolding", "budgets", "completion_criteria", "owner_approval",
}


def validate_activation(record: dict[str, Any]) -> None:
    _fields(record, ACTIVATION_FIELDS)
    if record.get("schema_version") != "1.0" or record.get("status") != "APPROVED":
        raise ContractError("activation must be schema 1.0 and APPROVED")
    _sha(record.get("approved_design_commit"), "approved_design_commit")
    _nonempty_strings(record, ("activation_id", "objective", "activated_user_visible_capability"))
    if not re.fullmatch(r"ACT-[A-Z0-9-]+-v[0-9]+", record["activation_id"]):
        raise ContractError("activation_id is invalid")
    _validate_activation_root(_typed(record, "root_turn", dict))
    _validate_activation_arrays(record)
    _validate_activation_owner(_typed(record, "owner_approval", dict))


def _validate_activation_root(root: dict[str, Any]) -> None:
    _fields(root, {"task_id", "title", "model", "reasoning_effort", "base_branch", "task_branch"}, {"luna_delegation_allowed"})
    if root.get("model") != "gpt-5.6" or root.get("base_branch") != "main":
        raise ContractError("activation requires GPT-5.6 Sol on main")
    _nonempty_strings(root, ("task_id", "title", "task_branch"))
    if root.get("reasoning_effort") not in {"high", "max", "ultra"}:
        raise ContractError("activation reasoning effort is invalid")
    if root.get("task_id") == "W00" and (root.get("reasoning_effort") != "max" or root.get("luna_delegation_allowed")):
        raise ContractError("W00 requires max effort and prohibits Luna delegation")
    if not re.fullmatch(r"codex/[a-z0-9][a-z0-9-]*", str(root.get("task_branch", ""))):
        raise ContractError("task_branch is invalid")


def _validate_activation_arrays(record: dict[str, Any]) -> None:
    for field in ("approved_design_ids", "activated_paths", "required_tests", "required_evidence", "explicit_non_goals"):
        if not isinstance(record.get(field), list) or not record[field]:
            raise ContractError(f"{field} must be a nonempty array")
        if not all(isinstance(item, str) for item in record[field]):
            raise ContractError(f"{field} items must be strings")
    if len(record["approved_design_ids"]) != len(set(record["approved_design_ids"])):
        raise ContractError("approved_design_ids must be unique")
    if any(str(path).startswith("activations/") for path in record["activated_paths"]):
        raise ContractError("an activation manifest cannot be implementation-writable")


def _validate_activation_owner(owner: dict[str, Any]) -> None:
    if owner.get("owner") != "Joseph Abbud" or owner.get("status") != "APPROVED":
        raise ContractError("activation lacks Joseph Abbud approval")
    _timestamp(owner.get("approved_at"), "owner_approval.approved_at")


def validate_auth_preflight(active_login: str, environment_names: Iterable[str]) -> None:
    if active_login != "abbudjoe":
        raise ContractError("active GitHub login must be abbudjoe")
    present = TOKEN_OVERRIDE_NAMES.intersection(environment_names)
    if present:
        raise ContractError(f"token override variables are present: {sorted(present)}")


HANDOFF_FIELDS = {
    "schema_version", "project_id", "activation_id", "task_id", "turn_id",
    "codex_run_id", "status", "repository", "branch", "base_sha",
    "implementation_head_sha", "pr_url", "github_actor_login", "github_auth_mode",
    "github_auth_preflight", "objective", "acceptance_criteria", "design_conformance",
    "changes", "review_targets", "commands", "evaluations", "artifacts",
    "delegated_operations", "complexity_receipt", "known_risks", "decisions_required",
    "billable_actions", "next_required_action", "merge_performed", "next_task_started",
}


def _validate_handoff_identity(record: dict[str, Any]) -> None:
    if (record.get("schema_version"), record.get("project_id")) != ("1.0", "biblical-scholar-lab"):
        raise ContractError("handoff schema or project identity is invalid")
    if record.get("status") not in ALLOWED_HANDOFF_STATUSES:
        raise ContractError("handoff status is not allowed")
    if (record.get("github_actor_login"), record.get("github_auth_mode")) != ("abbudjoe", "GH_CLI_EXISTING_AUTH"):
        raise ContractError("handoff GitHub identity is invalid")
    stop_state = (record.get("next_required_action"), record.get("merge_performed"), record.get("next_task_started"))
    if stop_state != ("CHATGPT_REVIEW", False, False):
        raise ContractError("handoff violates the root-turn stop boundary")
    _sha(record.get("base_sha"), "base_sha")
    _sha(record.get("implementation_head_sha"), "implementation_head_sha")
    _uri(record.get("pr_url"), "pr_url")
    if record.get("compare_url") is not None:
        _uri(record.get("compare_url"), "compare_url")
    _nonempty_strings(record, ("activation_id", "task_id", "turn_id", "codex_run_id", "repository", "branch", "objective"))
    if not record["branch"].startswith("codex/"):
        raise ContractError("handoff branch is invalid")


def _validate_handoff_receipts(record: dict[str, Any]) -> None:
    auth = _typed(record, "github_auth_preflight", dict)
    required_auth = {"hostname", "active_login", "auth_healthy", "token_override_present", "token_exposed"}
    _fields(auth, required_auth, {"receipt_path"})
    expected = (auth.get("hostname"), auth.get("active_login"), auth.get("auth_healthy"), auth.get("token_override_present"), auth.get("token_exposed"))
    if expected != ("github.com", "abbudjoe", True, False, False):
        raise ContractError("GitHub auth preflight is not compliant")
    design = _typed(record, "design_conformance", dict)
    _fields(design, {"status", "approved_design_ids", "unapproved_design_changes_executed"})
    if design.get("status") != "CONFORMING" or design.get("unapproved_design_changes_executed") is not False:
        raise ContractError("handoff design conformance is not clean")
    complexity = _typed(record, "complexity_receipt", dict)
    required_complexity = {
        "production_loc_added", "production_loc_removed", "test_loc_added", "test_loc_removed",
        "generated_loc", "production_files_added", "production_files_removed", "modules_added",
        "modules_removed", "tables_added", "migrations_added", "endpoints_added",
        "cli_commands_added", "dependencies_added", "dependencies_removed",
        "public_contracts_changed", "abstractions", "simpler_alternatives_considered",
        "known_duplication_or_debt", "waivers", "simplicity_conformance",
    }
    _fields(complexity, required_complexity)
    if complexity.get("simplicity_conformance") != "PASS":
        raise ContractError("handoff does not record DR-30 PASS")
    integer_fields = {"production_loc_added", "production_loc_removed", "test_loc_added", "test_loc_removed", "generated_loc", "production_files_added", "production_files_removed"}
    if any(not isinstance(complexity.get(field), int) or complexity[field] < 0 for field in integer_fields):
        raise ContractError("complexity receipt counts must be nonnegative integers")


def validate_handoff(record: dict[str, Any]) -> None:
    _fields(record, HANDOFF_FIELDS, {"compare_url"})
    _validate_handoff_identity(record)
    _validate_handoff_receipts(record)
    for field in ("acceptance_criteria", "changes", "review_targets", "commands", "evaluations", "artifacts", "delegated_operations", "known_risks", "decisions_required"):
        if not isinstance(record.get(field), list):
            raise ContractError(f"{field} must be an array")
    billable = _typed(record, "billable_actions", dict)
    _fields(billable, {"performed", "actual_cost_usd"}, {"campaign_ids"})
    if billable.get("performed") is not False or billable.get("actual_cost_usd") != 0:
        raise ContractError("W00 handoff must report no billable action")
    for operation in record["delegated_operations"]:
        if not isinstance(operation, dict) or operation.get("write_performed") is not False:
            raise ContractError("delegated operations must explicitly report no writes")
        if operation.get("role") == "luna_runner":
            raise ContractError("W00 prohibits Luna delegation")


REVIEW_FIELDS = {
    "schema_version", "review_id", "pr_url", "activation_id", "base_sha",
    "reviewed_head_sha", "reviewer", "disposition", "summary", "findings",
    "evidence_reviewed", "required_next_action", "review_timestamp",
}


def validate_review_schema(record: dict[str, Any]) -> None:
    _fields(record, REVIEW_FIELDS, {"supersedes_review_id"})
    if record.get("schema_version") != "1.0" or record.get("reviewer") != "ChatGPT":
        raise ContractError("review schema or reviewer is invalid")
    _uri(record.get("pr_url"), "pr_url")
    _sha(record.get("base_sha"), "base_sha")
    _sha(record.get("reviewed_head_sha"), "reviewed_head_sha")
    _timestamp(record.get("review_timestamp"), "review_timestamp")
    _nonempty_strings(record, ("review_id", "activation_id", "summary"))
    if record.get("disposition") not in {"CHATGPT_REVIEW_CLEAN", "REPAIR_REQUIRED", "BLOCKED_MISSING_EVIDENCE", "NO_GO_EXPERIMENT", "SPLIT_REQUIRED"}:
        raise ContractError("review disposition is invalid")
    if not isinstance(record.get("findings"), list) or not isinstance(record.get("evidence_reviewed"), list):
        raise ContractError("review findings and evidence must be arrays")
    if record.get("required_next_action") not in {"OWNER_AUTHORIZATION", "SOL_REPAIR", "DESIGN_REVIEW", "STOP"}:
        raise ContractError("review next action is invalid")


AUTH_FIELDS = {
    "schema_version", "authorization_id", "repository", "pr_url", "activation_id",
    "chatgpt_review_id", "authorized_head_sha", "owner_login", "authorization_channel",
    "owner_approval_reference", "approved_at", "merge_method", "status",
}


def validate_authorization_schema(record: dict[str, Any]) -> None:
    _fields(record, AUTH_FIELDS)
    if record.get("schema_version") != "1.0" or record.get("owner_login") != "abbudjoe":
        raise ContractError("authorization schema or owner is invalid")
    if record.get("authorization_channel") != "CHATGPT_CONVERSATION_EXPLICIT_APPROVAL" or record.get("merge_method") != "squash":
        raise ContractError("authorization channel or merge method is invalid")
    if record.get("status") not in {"AUTHORIZED", "REJECTED", "EXPIRED", "SUPERSEDED", "USED"}:
        raise ContractError("authorization status is invalid")
    if not re.fullmatch(r"[^/]+/[^/]+", str(record.get("repository", ""))):
        raise ContractError("authorization repository is invalid")
    _uri(record.get("pr_url"), "pr_url")
    _sha(record.get("authorized_head_sha"), "authorized_head_sha")
    _timestamp(record.get("approved_at"), "approved_at")
    _nonempty_strings(record, ("authorization_id", "activation_id", "chatgpt_review_id", "owner_approval_reference"))


def marked_records(comments: Iterable[dict[str, Any]], marker: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    pattern = re.compile(re.escape(marker) + r".*?```json\s*(.*?)\s*```", re.DOTALL)
    for comment in comments:
        body = comment.get("body", "") if isinstance(comment, dict) else ""
        for match in pattern.finditer(body):
            try:
                parsed = json.loads(match.group(1))
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                records.append(parsed)
    return records


def current_clean_review(comments: Iterable[dict[str, Any]], *, pr_url: str, activation_id: str, base_sha: str, head_sha: str) -> dict[str, Any]:
    matching: list[dict[str, Any]] = []
    for record in marked_records(comments, REVIEW_MARKER):
        try:
            validate_review_schema(record)
        except ContractError:
            continue
        identity = (record["pr_url"], record["activation_id"], record["base_sha"], record["reviewed_head_sha"])
        if identity == (pr_url, activation_id, base_sha, head_sha):
            matching.append(record)
    if not matching or matching[-1]["disposition"] != "CHATGPT_REVIEW_CLEAN":
        raise ContractError("no current clean ChatGPT review exists for the exact head")
    if not any("handoff" in str(item).lower() for item in matching[-1]["evidence_reviewed"]):
        raise ContractError("clean review does not reference the completed handoff evidence")
    return matching[-1]


def current_authorization(comments: Iterable[dict[str, Any]], *, repository: str, pr_url: str, activation_id: str, head_sha: str, review_id: str) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for record in marked_records(comments, AUTHORIZATION_MARKER):
        try:
            validate_authorization_schema(record)
        except ContractError:
            continue
        identity = (record["repository"], record["pr_url"], record["activation_id"], record["authorized_head_sha"], record["chatgpt_review_id"])
        if identity == (repository, pr_url, activation_id, head_sha, review_id):
            records.append(record)
    identifiers = [record["authorization_id"] for record in records]
    if len(identifiers) != len(set(identifiers)):
        raise ContractError("authorization record was reused")
    authorized = [record for record in records if record["status"] == "AUTHORIZED"]
    if len(authorized) != 1 or records[-1] is not authorized[0]:
        raise ContractError("one current, unsuperseded authorization is required")
    return authorized[0]


class CommandPhase(Enum):
    IMPLEMENTATION = "implementation"
    W00_GOVERNANCE = "w00-governance"
    MERGE_ONLY = "merge-only"


@dataclass(frozen=True)
class CommandDecision:
    allowed: bool
    reason: str


def _gh_decision(tokens: list[str], phase: CommandPhase) -> CommandDecision:
    if len(tokens) < 2:
        return CommandDecision(False, "incomplete gh command")
    pair = tuple(tokens[:3])
    if tokens[1] == "auth":
        allowed = pair == ("gh", "auth", "status") and "--show-token" not in tokens
        return CommandDecision(allowed, "nonsecret auth status" if allowed else "authentication display or mutation is prohibited")
    if pair == ("gh", "pr", "merge"):
        return _merge_decision(tokens, phase)
    if pair == ("gh", "pr", "ready"):
        return CommandDecision(phase is CommandPhase.MERGE_ONLY, "ready transition is merge-only")
    if tokens[1:3] == ["repo", "edit"]:
        return _repo_edit_decision(tokens, phase)
    if tokens[1] == "api":
        return _api_decision(tokens, phase)
    allowed_pairs = {("gh", "repo", "view"), ("gh", "pr", "create"), ("gh", "pr", "edit"), ("gh", "pr", "comment"), ("gh", "pr", "view"), ("gh", "pr", "status"), ("gh", "pr", "checks"), ("gh", "pr", "diff"), ("gh", "run", "list"), ("gh", "run", "view"), ("gh", "run", "watch")}
    return CommandDecision(pair in allowed_pairs, "allowed root-turn operation" if pair in allowed_pairs else "gh operation is not allowlisted")


def _merge_decision(tokens: list[str], phase: CommandPhase) -> CommandDecision:
    exact_flags = {"--squash", "--match-head-commit", "--delete-branch"}
    prohibited = {"--admin", "--auto"}.intersection(tokens)
    allowed = phase is CommandPhase.MERGE_ONLY and exact_flags.issubset(tokens) and not prohibited
    return CommandDecision(allowed, "exact merge-only sequence" if allowed else "merge is unavailable in this phase")


def _repo_edit_decision(tokens: list[str], phase: CommandPhase) -> CommandDecision:
    expected_flags = {"--enable-squash-merge=true", "--enable-merge-commit=false", "--enable-rebase-merge=false", "--enable-auto-merge=false", "--delete-branch-on-merge=true"}
    correct_repository = len(tokens) > 3 and tokens[3] == "abbudjoe/biblical-scholar-lab"
    supplied = set(tokens[4:]) if correct_repository else set()
    allowed = phase is CommandPhase.W00_GOVERNANCE and supplied == expected_flags
    return CommandDecision(allowed, "W00 merge-setting exception" if allowed else "repository mutation is prohibited")


def _api_method(tokens: list[str]) -> str:
    for index, token in enumerate(tokens):
        if token in {"-X", "--method"} and index + 1 < len(tokens):
            return tokens[index + 1].upper()
    return "GET"


def _api_decision(tokens: list[str], phase: CommandPhase) -> CommandDecision:
    method = _api_method(tokens)
    endpoint = next((token.lstrip("/") for token in tokens[2:] if token.startswith(("repos/", "/repos/"))), "")
    body_flags = {"-f", "-F", "--field", "--raw-field", "--input"}
    mutation = method not in {"GET", "HEAD"} or bool(body_flags.intersection(tokens))
    ruleset = re.fullmatch(r"repos/abbudjoe/biblical-scholar-lab/rulesets(?:/[0-9]+)?", endpoint)
    exception = phase is CommandPhase.W00_GOVERNANCE and bool(ruleset) and method in {"POST", "PUT", "PATCH"}
    allowed = not mutation or exception
    return CommandDecision(allowed, "read API or exact W00 ruleset endpoint" if allowed else "unrestricted mutating API is prohibited")


def _git_decision(tokens: list[str]) -> CommandDecision:
    if len(tokens) < 2:
        return CommandDecision(False, "incomplete git command")
    if tokens[1] == "push":
        prohibited = any(token in {"--force", "-f", "--force-with-lease", "main", "HEAD:main", "refs/heads/main"} for token in tokens[2:])
        branch_named = any(token.startswith("codex/") for token in tokens[2:])
        return CommandDecision(branch_named and not prohibited, "task-branch push" if branch_named and not prohibited else "direct or force push is prohibited")
    allowed = tokens[1] in {"status", "diff", "log", "show", "rev-parse", "branch", "fetch", "add", "commit", "switch", "ls-remote"}
    return CommandDecision(allowed, "allowed local Git operation" if allowed else "Git operation is not allowlisted")


def assess_command(command: str, phase: CommandPhase) -> CommandDecision:
    try:
        tokens = shlex.split(command)
    except ValueError:
        return CommandDecision(False, "command cannot be parsed")
    if not tokens:
        return CommandDecision(False, "empty command")
    if tokens[0] == "gh":
        return _gh_decision(tokens, phase)
    if tokens[0] == "git":
        return _git_decision(tokens)
    return CommandDecision(True, "local non-GitHub command")
