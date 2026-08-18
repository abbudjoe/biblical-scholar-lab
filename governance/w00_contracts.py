"""Pure W00 governance contracts and exact command-policy decisions."""

from __future__ import annotations

import hashlib
import json
import re
import shlex
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, cast
from urllib.parse import urlparse

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
REVIEW_MARKER = "<!-- BSL_CHATGPT_REVIEW_V1 -->"
AUTHORIZATION_MARKER = "<!-- BSL_OWNER_MERGE_AUTHORIZATION_V1 -->"
REPOSITORY = "abbudjoe/biblical-scholar-lab"
TASK_BRANCH = "codex/w00-repository-governance"
RULESET_ID = "20960975"
ENVIRONMENT = "owner-merge-authorization"
TOKEN_OVERRIDE_NAMES = {"GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN"}
ALLOWED_HANDOFF_STATUSES = {
    "READY_FOR_CHATGPT_REVIEW", "BLOCKED_MISSING_EVIDENCE", "BLOCKED_DEPENDENCY",
    "BLOCKED_REQUIRES_DESIGN_REVIEW", "BLOCKED_REQUIRES_SOL_REPAIR", "SPLIT_REQUIRED",
    "NO_CHANGE", "FAILED",
}


class ContractError(ValueError):
    """A governance record violated its explicit contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _fields(record: dict[str, Any], required: set[str], optional: set[str] | None = None) -> None:
    optional = optional or set()
    missing, extra = required - record.keys(), record.keys() - required - optional
    _require(not missing and not extra, f"record fields differ: missing={sorted(missing)} extra={sorted(extra)}")


def _typed(record: dict[str, Any], field: str, expected: type) -> Any:
    value = record.get(field)
    _require(isinstance(value, expected), f"{field} must be {expected.__name__}")
    return value


def _strings(record: dict[str, Any], fields: Iterable[str]) -> None:
    _require(not any(not isinstance(record.get(field), str) or not record[field] for field in fields), "required string field is empty or mistyped")


def _array(record: dict[str, Any], field: str, item_type: type, *, nonempty: bool = False) -> list[Any]:
    value = record.get(field)
    _require(isinstance(value, list) and not (nonempty and not value) and all(isinstance(item, item_type) for item in value), f"{field} must be an array of {item_type.__name__}")
    return cast(list[Any], value)


def _sha(value: Any, field: str) -> str:
    _require(isinstance(value, str) and bool(SHA_RE.fullmatch(value)), f"{field} must be a lowercase 40-character SHA")
    return cast(str, value)


def _hash(value: Any, field: str) -> str:
    _require(isinstance(value, str) and bool(HASH_RE.fullmatch(value)), f"{field} must be a lowercase SHA-256 digest")
    return cast(str, value)


def _timestamp(value: Any, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else None
    except ValueError as error:
        raise ContractError(f"{field} must be an RFC3339 timestamp") from error
    _require(parsed is not None and parsed.utcoffset() is not None, f"{field} must be an RFC3339 timestamp with timezone")
    return cast(datetime, parsed)


def _uri(value: Any, field: str) -> str:
    parsed = urlparse(value) if isinstance(value, str) else None
    _require(bool(parsed and parsed.scheme in {"http", "https"} and parsed.netloc), f"{field} must be an HTTP(S) URI")
    return cast(str, value)


ACTIVATION_FIELDS = {
    "schema_version", "activation_id", "status", "approved_design_commit", "approved_design_ids",
    "root_turn", "objective", "vertical_slice_id", "activated_user_visible_capability",
    "activated_invariants", "activated_paths", "activated_contracts", "activated_interfaces",
    "activated_data_stores", "activated_adapters", "required_tests", "required_evidence",
    "explicit_non_goals", "prohibited_scaffolding", "budgets", "completion_criteria", "owner_approval",
}


def validate_activation(record: dict[str, Any]) -> None:
    _fields(record, ACTIVATION_FIELDS)
    _require((record.get("schema_version"), record.get("status")) == ("1.0", "APPROVED"), "activation must be schema 1.0 and APPROVED")
    _sha(record.get("approved_design_commit"), "approved_design_commit")
    _strings(record, ("activation_id", "objective", "activated_user_visible_capability"))
    _require(bool(re.fullmatch(r"ACT-[A-Z0-9-]+-v[0-9]+", record["activation_id"])), "activation_id is invalid")
    _validate_activation_root(_typed(record, "root_turn", dict))
    _validate_activation_arrays(record)
    _validate_activation_owner(_typed(record, "owner_approval", dict))


def _validate_activation_root(root: dict[str, Any]) -> None:
    _fields(root, {"task_id", "title", "model", "reasoning_effort", "base_branch", "task_branch"}, {"luna_delegation_allowed"})
    _require((root.get("model"), root.get("reasoning_effort"), root.get("base_branch")) == ("gpt-5.6", "max", "main"), "activation requires GPT-5.6 Sol at max effort on main")
    _require(root.get("task_id") != "W00" or root.get("luna_delegation_allowed") is False, "W00 prohibits Luna delegation")
    _require(bool(re.fullmatch(r"codex/[a-z0-9][a-z0-9-]*", str(root.get("task_branch", "")))), "task_branch is invalid")


def _validate_activation_arrays(record: dict[str, Any]) -> None:
    for field in ("approved_design_ids", "activated_paths", "required_tests", "required_evidence", "explicit_non_goals"):
        _array(record, field, str, nonempty=True)
    _require(len(record["approved_design_ids"]) == len(set(record["approved_design_ids"])), "approved_design_ids must be unique")
    _require(not any(path.startswith("activations/") for path in record["activated_paths"]), "an activation manifest cannot be implementation-writable")


def _validate_activation_owner(owner: dict[str, Any]) -> None:
    _require((owner.get("owner"), owner.get("status")) == ("Joseph Abbud", "APPROVED"), "activation lacks Joseph Abbud approval")
    _timestamp(owner.get("approved_at"), "owner_approval.approved_at")


def validate_auth_preflight(active_login: str, environment_names: Iterable[str]) -> None:
    _require(active_login == "abbudjoe", "active GitHub login must be abbudjoe")
    present = TOKEN_OVERRIDE_NAMES.intersection(environment_names)
    _require(not present, f"token override variables are present: {sorted(present)}")


HANDOFF_FIELDS = {
    "schema_version", "project_id", "activation_id", "task_id", "turn_id", "codex_run_id",
    "status", "repository", "branch", "base_sha", "implementation_head_sha", "pr_url",
    "github_actor_login", "github_auth_mode", "github_auth_preflight", "objective",
    "acceptance_criteria", "design_conformance", "changes", "review_targets", "commands",
    "evaluations", "artifacts", "delegated_operations", "complexity_receipt", "known_risks",
    "decisions_required", "billable_actions", "next_required_action", "merge_performed",
    "next_task_started",
}
COMPLEXITY_FIELDS = {
    "production_loc_added", "production_loc_removed", "test_loc_added", "test_loc_removed",
    "generated_loc", "production_files_added", "production_files_removed", "modules_added",
    "modules_removed", "tables_added", "migrations_added", "endpoints_added", "cli_commands_added",
    "dependencies_added", "dependencies_removed", "public_contracts_changed", "abstractions",
    "simpler_alternatives_considered", "known_duplication_or_debt", "waivers", "simplicity_conformance",
}


def validate_handoff(record: dict[str, Any]) -> None:
    _fields(record, HANDOFF_FIELDS, {"compare_url"})
    _require((record.get("schema_version"), record.get("project_id")) == ("1.0", "biblical-scholar-lab"), "handoff schema or project identity is invalid")
    _require(record.get("status") in ALLOWED_HANDOFF_STATUSES, "handoff status is not allowed")
    _require((record.get("github_actor_login"), record.get("github_auth_mode")) == ("abbudjoe", "GH_CLI_EXISTING_AUTH"), "handoff GitHub identity is invalid")
    _require((record.get("next_required_action"), record.get("merge_performed"), record.get("next_task_started")) == ("CHATGPT_REVIEW", False, False), "handoff violates the root-turn stop boundary")
    _strings(record, ("activation_id", "task_id", "turn_id", "codex_run_id", "repository", "branch", "objective"))
    _sha(record.get("base_sha"), "base_sha"); _sha(record.get("implementation_head_sha"), "implementation_head_sha")
    _uri(record.get("pr_url"), "pr_url")
    if record.get("compare_url") is not None:
        _uri(record["compare_url"], "compare_url")
    _require(record["branch"].startswith("codex/"), "handoff branch is invalid")
    _validate_handoff_state(record)


def _validate_handoff_state(record: dict[str, Any]) -> None:
    auth = _typed(record, "github_auth_preflight", dict)
    _fields(auth, {"hostname", "active_login", "auth_healthy", "token_override_present", "token_exposed"}, {"receipt_path"})
    _require(tuple(auth.get(key) for key in ("hostname", "active_login", "auth_healthy", "token_override_present", "token_exposed")) == ("github.com", "abbudjoe", True, False, False), "GitHub auth preflight is not compliant")
    design = _typed(record, "design_conformance", dict)
    _fields(design, {"status", "approved_design_ids", "unapproved_design_changes_executed"})
    expected = "BLOCKED_REQUIRES_DESIGN_REVIEW" if record["status"] == "BLOCKED_REQUIRES_DESIGN_REVIEW" else "CONFORMING"
    _require(design.get("status") == expected and design.get("unapproved_design_changes_executed") is False, "handoff design state does not match the disposition")
    _array(design, "approved_design_ids", str, nonempty=True)
    _validate_complexity(_typed(record, "complexity_receipt", dict), record["status"])
    for field, item_type in (("acceptance_criteria", str), ("known_risks", str), ("decisions_required", str), ("changes", dict), ("review_targets", dict), ("commands", dict), ("evaluations", dict), ("artifacts", dict), ("delegated_operations", dict)):
        _array(record, field, item_type)
    _require(not any(item.get("write_performed") is not False or item.get("role") == "luna_runner" for item in record["delegated_operations"]), "delegated operations violate the W00 read-only boundary")
    billable = _typed(record, "billable_actions", dict)
    _fields(billable, {"performed", "actual_cost_usd"}, {"campaign_ids"})
    _require((billable.get("performed"), billable.get("actual_cost_usd")) == (False, 0), "W00 handoff must report no billable action")


def _validate_complexity(complexity: dict[str, Any], status: str) -> None:
    _fields(complexity, COMPLEXITY_FIELDS)
    expected_simple = "BLOCKED_REQUIRES_SPLIT" if status == "SPLIT_REQUIRED" else "PASS"
    _require(complexity.get("simplicity_conformance") == expected_simple, "handoff simplicity state differs")
    count_fields = ("production_loc_added", "production_loc_removed", "test_loc_added", "test_loc_removed", "generated_loc", "production_files_added", "production_files_removed")
    _require(not any(not isinstance(complexity.get(name), int) or complexity[name] < 0 for name in count_fields), "complexity counts must be nonnegative integers")
    for field in ("modules_added", "modules_removed", "tables_added", "migrations_added", "endpoints_added", "cli_commands_added", "dependencies_added", "dependencies_removed", "public_contracts_changed", "simpler_alternatives_considered", "known_duplication_or_debt", "waivers"):
        _array(complexity, field, str)
    _array(complexity, "abstractions", dict)


REVIEW_FIELDS = {
    "schema_version", "review_id", "pr_url", "activation_id", "base_sha", "reviewed_head_sha",
    "reviewer", "disposition", "summary", "findings", "evidence_reviewed", "required_next_action",
    "review_timestamp",
}
AUTH_FIELDS = {
    "schema_version", "authorization_id", "repository", "pr_url", "activation_id",
    "chatgpt_review_id", "authorized_head_sha", "owner_login", "authorization_channel",
    "owner_approval_reference", "approved_at", "merge_method", "status",
}


def validate_review_schema(record: dict[str, Any]) -> None:
    _fields(record, REVIEW_FIELDS, {"supersedes_review_id"})
    _require((record.get("schema_version"), record.get("reviewer")) == ("1.0", "ChatGPT"), "review schema or reviewer is invalid")
    _uri(record.get("pr_url"), "pr_url"); _sha(record.get("base_sha"), "base_sha"); _sha(record.get("reviewed_head_sha"), "reviewed_head_sha")
    _timestamp(record.get("review_timestamp"), "review_timestamp")
    _strings(record, ("review_id", "activation_id", "summary"))
    _array(record, "findings", dict); _array(record, "evidence_reviewed", str, nonempty=True)
    _require(record.get("disposition") in {"CHATGPT_REVIEW_CLEAN", "REPAIR_REQUIRED", "BLOCKED_MISSING_EVIDENCE", "NO_GO_EXPERIMENT", "SPLIT_REQUIRED"}, "review disposition is invalid")
    _require(record.get("required_next_action") in {"OWNER_AUTHORIZATION", "SOL_REPAIR", "DESIGN_REVIEW", "STOP"}, "review next action is invalid")


def validate_authorization_schema(record: dict[str, Any]) -> None:
    _fields(record, AUTH_FIELDS)
    expected = ("1.0", "abbudjoe", "CHATGPT_CONVERSATION_EXPLICIT_APPROVAL", "squash")
    _require(tuple(record.get(key) for key in ("schema_version", "owner_login", "authorization_channel", "merge_method")) == expected, "authorization identity or method is invalid")
    _require(record.get("status") in {"AUTHORIZED", "REJECTED", "EXPIRED", "SUPERSEDED", "USED"}, "authorization status is invalid")
    _require(bool(re.fullmatch(r"[^/]+/[^/]+", str(record.get("repository", "")))), "authorization repository is invalid")
    _uri(record.get("pr_url"), "pr_url"); _sha(record.get("authorized_head_sha"), "authorized_head_sha")
    _timestamp(record.get("approved_at"), "approved_at")
    _strings(record, ("authorization_id", "activation_id", "chatgpt_review_id", "owner_approval_reference"))


@dataclass(frozen=True)
class _CommentRecord:
    record: dict[str, Any]
    index: int
    comment_id: int
    created_at: datetime


def _comment_records(comments: Iterable[dict[str, Any]], marker: str, validator: Callable[[dict[str, Any]], None]) -> list[_CommentRecord]:
    values = list(comments)
    dated: list[tuple[datetime, int]] = []
    records: list[_CommentRecord] = []
    pattern = re.compile(re.escape(marker) + r".*?```json\s*(.*?)\s*```", re.DOTALL)
    for index, comment in enumerate(values):
        if not isinstance(comment, dict):
            raise ContractError("comments must be objects")
        body = comment.get("body", "")
        if marker not in body:
            continue
        parsed, created = _parse_comment(comment, pattern, validator)
        timestamp_field = "review_timestamp" if marker == REVIEW_MARKER else "approved_at"
        _require(_timestamp(parsed[timestamp_field], timestamp_field) <= created, "governance record timestamp follows its comment")
        dated.append((created, comment["id"])); records.append(_CommentRecord(parsed, index, comment["id"], created))
    _require(dated == sorted(dated) and len({item.comment_id for item in records}) == len(records), "governance comments were reordered or reused")
    return records


def _parse_comment(comment: dict[str, Any], pattern: re.Pattern[str], validator: Callable[[dict[str, Any]], None]) -> tuple[dict[str, Any], datetime]:
    _require(isinstance(comment.get("id"), int) and comment["id"] > 0, "marked comment identity is missing")
    created = _timestamp(comment.get("created_at"), "comment.created_at")
    _require(created == _timestamp(comment.get("updated_at"), "comment.updated_at"), "marked governance comments are append-only and cannot be edited")
    matches = pattern.findall(comment["body"])
    _require(len(matches) == 1, "marked comment must contain exactly one JSON record")
    try:
        parsed = json.loads(matches[0])
    except json.JSONDecodeError as error:
        raise ContractError("marked comment JSON is malformed") from error
    _require(isinstance(parsed, dict), "marked comment JSON must be an object")
    validator(parsed)
    return parsed, created


def validate_append_only_comments(previous: Iterable[dict[str, Any]], current: Iterable[dict[str, Any]]) -> None:
    old_values, new_values = list(previous), list(current)
    for marker, validator in ((REVIEW_MARKER, validate_review_schema), (AUTHORIZATION_MARKER, validate_authorization_schema)):
        _comment_records(old_values, marker, validator)
        _comment_records(new_values, marker, validator)
    markers = (REVIEW_MARKER, AUTHORIZATION_MARKER)
    old_identity = [(item.get("id"), item) for item in old_values if any(marker in item.get("body", "") for marker in markers)]
    new_identity = [(item.get("id"), item) for item in new_values if any(marker in item.get("body", "") for marker in markers)]
    _require(new_identity[:len(old_identity)] == old_identity, "governance comments were deleted, edited, replaced, or reordered")


def current_clean_review(comments: Iterable[dict[str, Any]], *, pr_url: str, activation_id: str, base_sha: str, head_sha: str) -> dict[str, Any]:
    entries = _comment_records(comments, REVIEW_MARKER, validate_review_schema)
    _require(len({item.record["review_id"] for item in entries}) == len(entries), "review identifier was reused")
    expected = (pr_url, activation_id, base_sha, head_sha)
    matches = [item for item in entries if tuple(item.record[key] for key in ("pr_url", "activation_id", "base_sha", "reviewed_head_sha")) == expected]
    _require(bool(matches and matches[-1].record["disposition"] == "CHATGPT_REVIEW_CLEAN"), "no current clean ChatGPT review exists for the exact head")
    review = matches[-1].record
    _require(review["required_next_action"] == "OWNER_AUTHORIZATION", "clean review must transition to owner authorization")
    evidence_pattern = re.compile(rf"^https://github\.com/{re.escape(REPOSITORY)}/blob/{head_sha}/handoffs/[A-Za-z0-9-]+/[A-Za-z0-9._-]+\.json$")
    _require(any(evidence_pattern.fullmatch(item) for item in review["evidence_reviewed"]), "clean review does not bind a completed JSON handoff")
    return review


def current_authorization(comments: Iterable[dict[str, Any]], *, repository: str, pr_url: str, activation_id: str, head_sha: str, review_id: str) -> dict[str, Any]:
    values = list(comments)
    reviews = _comment_records(values, REVIEW_MARKER, validate_review_schema)
    authorizations = _comment_records(values, AUTHORIZATION_MARKER, validate_authorization_schema)
    unique = (len({item.record["review_id"] for item in reviews}) == len(reviews), len({item.record["authorization_id"] for item in authorizations}) == len(authorizations))
    _require(all(unique), "review or authorization identifier was reused")
    review = next((item for item in reviews if item.record["review_id"] == review_id), None)
    _require(review is not None and review.record["disposition"] == "CHATGPT_REVIEW_CLEAN", "referenced clean review is absent")
    review = cast(_CommentRecord, review)
    expected = (repository, pr_url, activation_id, head_sha, review_id)
    matches = [item for item in authorizations if tuple(item.record[key] for key in ("repository", "pr_url", "activation_id", "authorized_head_sha", "chatgpt_review_id")) == expected]
    authorized = [item for item in matches if item.record["status"] == "AUTHORIZED"]
    _require(all((len(authorized) == 1, matches, matches[-1] == authorized[0] if matches and authorized else False)), "one current, unsuperseded authorization is required")
    item = authorized[0]
    approved = _timestamp(item.record["approved_at"], "approved_at")
    reviewed = _timestamp(review.record["review_timestamp"], "review_timestamp")
    _require(all((item.index > review.index, item.created_at > review.created_at, reviewed <= approved <= item.created_at)), "authorization must be approved and posted after the clean review")
    return item.record


TRUSTED_RECEIPT_FIELDS = {
    "schema_version", "receipt_type", "repository", "pr_number", "inspected_head_sha", "base_sha",
    "trusted_validator_revision", "workflow_path", "workflow_run_id", "workflow_run_attempt", "event",
    "validator_content_hash", "validation_results", "timestamp", "conclusion", "receipt_hash",
}
OWNER_RECEIPT_FIELDS = {
    "schema_version", "receipt_type", "repository", "pr_number", "pr_url", "authorized_head_sha",
    "chatgpt_review_id", "trusted_validator", "authorization_workflow", "environment_name", "timestamp",
    "conclusion", "receipt_hash",
}


def receipt_hash(record: dict[str, Any]) -> str:
    unsigned = {key: value for key, value in record.items() if key != "receipt_hash"}
    return hashlib.sha256(json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate_trusted_receipt(record: dict[str, Any]) -> None:
    _fields(record, TRUSTED_RECEIPT_FIELDS)
    expected = ("1.0", "TrustedGovernanceValidationReceipt", REPOSITORY, ".github/workflows/trusted-governance-validator.yml", "pull_request_target", "success")
    actual = tuple(record.get(key) for key in ("schema_version", "receipt_type", "repository", "workflow_path", "event", "conclusion"))
    _require(actual == expected and record.get("receipt_hash") == receipt_hash(record), "trusted validation receipt identity or hash differs")
    for field in ("inspected_head_sha", "base_sha", "trusted_validator_revision"):
        _sha(record.get(field), field)
    _hash(record.get("validator_content_hash"), "validator_content_hash")
    _require(not any(not isinstance(record.get(field), int) or record[field] <= 0 for field in ("pr_number", "workflow_run_id", "workflow_run_attempt")), "trusted receipt numeric identity is invalid")
    results = _typed(record, "validation_results", dict)
    _require(bool(results) and not any(value != "PASS" for value in results.values()), "trusted validation results are incomplete")
    _timestamp(record.get("timestamp"), "timestamp")


def validate_trusted_receipt_binding(record: dict[str, Any], *, pr_number: int, head_sha: str, base_sha: str, workflow_run_id: int) -> None:
    validate_trusted_receipt(record)
    actual = (record["pr_number"], record["inspected_head_sha"], record["base_sha"], record["workflow_run_id"])
    _require(actual == (pr_number, head_sha, base_sha, workflow_run_id), "trusted validation receipt is bound to a different PR, head, base, or run")


def validate_owner_receipt(record: dict[str, Any]) -> None:
    _fields(record, OWNER_RECEIPT_FIELDS)
    expected = ("1.0", "OwnerMergeAuthorizationReceipt", REPOSITORY, ENVIRONMENT, "success")
    actual = tuple(record.get(key) for key in ("schema_version", "receipt_type", "repository", "environment_name", "conclusion"))
    _require(actual == expected and record.get("receipt_hash") == receipt_hash(record), "owner authorization receipt identity or hash differs")
    _uri(record.get("pr_url"), "pr_url"); _sha(record.get("authorized_head_sha"), "authorized_head_sha")
    _strings(record, ("chatgpt_review_id",)); _timestamp(record.get("timestamp"), "timestamp")
    _require(isinstance(record.get("pr_number"), int) and record["pr_number"] > 0, "authorization receipt PR number is invalid")
    trusted, workflow = _typed(record, "trusted_validator", dict), _typed(record, "authorization_workflow", dict)
    _fields(trusted, {"workflow_path", "run_id", "receipt_hash"})
    _fields(workflow, {"workflow_path", "run_id", "run_attempt", "trusted_revision"})
    _require((trusted.get("workflow_path"), workflow.get("workflow_path")) == (".github/workflows/trusted-governance-validator.yml", ".github/workflows/owner-merge-authorization.yml"), "authorization receipt workflow identity differs")
    _require(not any(not isinstance(value, int) or value <= 0 for value in (trusted.get("run_id"), workflow.get("run_id"), workflow.get("run_attempt"))), "authorization workflow run identity is invalid")
    _hash(trusted.get("receipt_hash"), "trusted_validator.receipt_hash"); _sha(workflow.get("trusted_revision"), "trusted_revision")


def validate_owner_receipt_binding(record: dict[str, Any], *, pr_number: int, head_sha: str, review_id: str, trusted_run_id: int, authorization_run_id: int, authorization_revision: str) -> None:
    validate_owner_receipt(record)
    actual = (record["pr_number"], record["authorized_head_sha"], record["chatgpt_review_id"], record["trusted_validator"]["run_id"], record["authorization_workflow"]["run_id"], record["authorization_workflow"]["trusted_revision"])
    expected = (pr_number, head_sha, review_id, trusted_run_id, authorization_run_id, authorization_revision)
    _require(actual == expected, "owner authorization receipt is bound to a different PR, head, review, or run")


class CommandPhase(Enum):
    IMPLEMENTATION = "implementation"
    W00_GOVERNANCE = "w00-governance"
    MERGE_ONLY = "merge-only"


@dataclass(frozen=True)
class CommandDecision:
    allowed: bool
    reason: str


def _decision(allowed: bool, good: str, bad: str) -> CommandDecision:
    return CommandDecision(allowed, good if allowed else bad)


def _gh_decision(tokens: list[str], phase: CommandPhase) -> CommandDecision:
    if len(tokens) < 2:
        return CommandDecision(False, "GitHub command is incomplete")
    pair = tuple(tokens[1:3])
    if tokens[1] == "auth":
        exact = tokens == ["gh", "auth", "status", "--active", "--hostname", "github.com"]
        return _decision(exact, "redacted authentication preflight", "authentication display or mutation is prohibited")
    if pair == ("pr", "merge"):
        exact = len(tokens) == 8 and all((tokens[3].isdigit(), tokens[4:6] == ["--squash", "--match-head-commit"], bool(SHA_RE.fullmatch(tokens[6])), tokens[7] == "--delete-branch"))
        return _decision(all((phase is CommandPhase.MERGE_ONLY, exact)), "exact merge-only sequence", "merge is unavailable or malformed")
    if pair == ("pr", "ready"):
        exact = len(tokens) == 4 and tokens[3].isdigit()
        return _decision(all((phase is CommandPhase.MERGE_ONLY, exact)), "merge-only ready transition", "ready transition is unavailable")
    if pair == ("repo", "edit"):
        expected = {"--enable-squash-merge=true", "--enable-merge-commit=false", "--enable-rebase-merge=false", "--enable-auto-merge=false", "--delete-branch-on-merge=true"}
        exact = len(tokens) == 9 and all((tokens[3] == REPOSITORY, set(tokens[4:]) == expected))
        return _decision(all((phase is CommandPhase.W00_GOVERNANCE, exact)), "exact W00 merge-settings operation", "repository mutation is prohibited")
    if tokens[1] == "api":
        return _api_decision(tokens, phase)
    return _ordinary_gh(tokens)

def _ordinary_gh(tokens: list[str]) -> CommandDecision:
    pair = tuple(tokens[:3])
    reads = {("gh", "repo", "view"), ("gh", "pr", "view"), ("gh", "pr", "status"), ("gh", "pr", "checks"), ("gh", "pr", "diff"), ("gh", "run", "list"), ("gh", "run", "view"), ("gh", "run", "watch")}
    if {"--hostname", "-H", "--header"}.intersection(tokens):
        return CommandDecision(False, "GitHub host or header override is prohibited")
    if pair in reads:
        return CommandDecision(True, "allowlisted read-only GitHub operation")
    if pair == ("gh", "pr", "comment"):
        valid = len(tokens) == 6 and tokens[3].isdigit() and tokens[4] == "--body-file" and not tokens[5].startswith("-")
        return _decision(valid, "bounded PR comment", "PR comment structure differs")
    if pair == ("gh", "pr", "create"):
        exact = tokens == ["gh", "pr", "create", "--draft", "--base", "main", "--head", TASK_BRANCH]
        return _decision(exact, "bounded draft PR creation", "PR creation structure differs")
    return CommandDecision(False, "GitHub operation is not allowlisted")


def _api_decision(tokens: list[str], phase: CommandPhase) -> CommandDecision:
    environment = ["gh", "api", "--method", "PUT", f"repos/{REPOSITORY}/environments/{ENVIRONMENT}", "--input", ".codex-tmp-owner-env.json"]
    ruleset = ["gh", "api", "--method", "PUT", f"repos/{REPOSITORY}/rulesets/{RULESET_ID}", "--input", ".codex-tmp-ruleset.json"]
    if tokens in (environment, ruleset):
        return _decision(phase is CommandPhase.W00_GOVERNANCE, "exact W00 governance operation", "governance mutation is unavailable")
    method_flags = [index for index, token in enumerate(tokens) if token in {"-X", "--method"}]
    method = "GET"
    if method_flags:
        index = method_flags[0]
        method = tokens[index + 1].upper() if index + 1 < len(tokens) else ""
    body_flags = {"-f", "-F", "--field", "--raw-field", "--input", "-H", "--header", "--hostname"}
    smuggled = any((token.startswith(("-X", "-f", "-F", "-H")) and token not in {"-X", "-f", "-F", "-H"}) or token.startswith(("--method=", "--field=", "--raw-field=", "--input=", "--header=", "--hostname=")) for token in tokens)
    endpoint = next((token.lstrip("/") for token in tokens[2:] if token.startswith(("repos/", "/repos/", "users/"))), "")
    endpoint = endpoint.split("?", 1)[0]
    pattern = rf"(?:repos/{re.escape(REPOSITORY)}/(?:pulls/1|issues/1/comments|actions/(?:workflows|runs/[0-9]+)|commits/[0-9a-f]{{40}}/check-runs|rulesets(?:/{RULESET_ID})?|codeowners/errors|environments/{ENVIRONMENT})|users/abbudjoe)"
    allowed = len(method_flags) <= 1 and method in {"GET", "HEAD"} and not smuggled and not body_flags.intersection(tokens) and bool(re.fullmatch(pattern, endpoint))
    return _decision(allowed, "bounded read-only GitHub API", "mutating or unbounded GitHub API is prohibited")


def _git_decision(tokens: list[str]) -> CommandDecision:
    if len(tokens) < 2 or tokens[1].startswith("-"):
        return CommandDecision(False, "Git command is incomplete or configured dynamically")
    if tokens[1] == "push":
        allowed = tokens in (["git", "push", "origin", TASK_BRANCH], ["git", "push", "-u", "origin", TASK_BRANCH])
        return _decision(allowed, "exact task-branch push", "direct, refspec, multi-ref, or force push is prohibited")
    if tokens[1] == "commit":
        allowed = len(tokens) == 4 and tokens[2] == "-m" and bool(tokens[3])
        return _decision(allowed, "new commit", "commit rewriting or argument smuggling is prohibited")
    if tokens[1] == "add":
        allowed = len(tokens) > 2 and all(re.fullmatch(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*", item) and not {".", ".."}.intersection(item.split("/")) for item in tokens[2:])
        return _decision(allowed, "explicit-path staging", "broad or option-based staging is prohibited")
    reads = {"status", "diff", "log", "show", "rev-parse", "branch", "fetch", "ls-remote", "ls-tree", "diff-tree", "merge-base"}
    return _decision(tokens[1] in reads, "allowlisted Git read", "Git operation is not allowlisted")


def assess_command(command: str, phase: CommandPhase) -> CommandDecision:
    tokens = _parse_command(command)
    if isinstance(tokens, CommandDecision):
        return tokens
    if tokens[0] == "gh":
        return _gh_decision(tokens, phase)
    if tokens[0] == "git":
        return _git_decision(tokens)
    return _local_decision(tokens)


def _parse_command(command: str) -> list[str] | CommandDecision:
    if re.search(r"[\n\r;&|`<>]|\$\(|\\\n", command):
        return CommandDecision(False, "shell composition or expansion is prohibited")
    try:
        tokens = shlex.split(command)
    except ValueError:
        return CommandDecision(False, "command cannot be parsed")
    if not tokens or tokens[0] == "env" or "=" in tokens[0]:
        return CommandDecision(False, "empty or environment-prefixed command is prohibited")
    return tokens


def _local_decision(tokens: list[str]) -> CommandDecision:
    uvx_tool = tokens[3] if len(tokens) > 3 and tokens[1:3] == ["--from", "coverage"] else (tokens[1] if len(tokens) > 1 else "")
    local = tokens[:3] in (["python3", "-m", "unittest"], ["python3", "-m", "py_compile"]) or (tokens[0] == "python3" and len(tokens) > 1 and tokens[1] == "governance/w00_checks.py") or (tokens[0] == "uvx" and uvx_tool in {"coverage", "ruff", "mypy", "detect-secrets"})
    return _decision(local, "allowlisted deterministic local tool", "wrapper, alias, or local command is not allowlisted")
