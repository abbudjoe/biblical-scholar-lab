"""Adversarial W00 and GOV-01-S01 conformance tests."""

from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

GOVERNANCE = Path(__file__).resolve().parent
ROOT = GOVERNANCE.parent
sys.path.insert(0, str(GOVERNANCE))

import w00_checks as checks
from w00_checks import BudgetMetrics
from w00_contracts import (
    AUTHORIZATION_MARKER,
    REVIEW_MARKER,
    CommandPhase,
    ContractError,
    assess_command,
    current_authorization,
    current_clean_review,
    receipt_hash,
    validate_activation,
    validate_append_only_comments,
    validate_auth_preflight,
    validate_handoff,
    validate_owner_receipt,
    validate_owner_receipt_binding,
    validate_review_schema,
    validate_trusted_receipt,
    validate_trusted_receipt_binding,
)

BASE, HEAD, IMPL = "a" * 40, "b" * 40, "c" * 40
PR_URL = "https://github.com/abbudjoe/biblical-scholar-lab/pull/1"
NOW = datetime.now(timezone.utc).replace(microsecond=0)


def _time(minutes: int) -> str:
    return (NOW + timedelta(minutes=minutes)).isoformat().replace("+00:00", "Z")


def _replace(record: dict, path: tuple[str, ...], value) -> dict:
    changed = copy.deepcopy(record)
    target = changed
    for field in path[:-1]:
        target = target[field]
    target[path[-1]] = value
    return changed


def _comment(marker: str, record: dict, comment_id: int, minute: int) -> dict:
    stamp = _time(minute)
    return {"id": comment_id, "created_at": stamp, "updated_at": stamp, "body": f"{marker}\n```json\n{json.dumps(record)}\n```"}


def _review(head: str = HEAD) -> dict:
    return {
        "schema_version": "1.0", "review_id": "REVIEW-W00-1", "pr_url": PR_URL,
        "activation_id": "ACT-W00-REPOSITORY-GOVERNANCE-v3", "base_sha": BASE,
        "reviewed_head_sha": head, "reviewer": "ChatGPT", "disposition": "CHATGPT_REVIEW_CLEAN",
        "summary": "Exact-head review.", "findings": [],
        "evidence_reviewed": [f"https://github.com/abbudjoe/biblical-scholar-lab/blob/{head}/handoffs/W00/W00-fixture.json"],
        "required_next_action": "OWNER_AUTHORIZATION", "review_timestamp": _time(-8),
    }


def _authorization(head: str = HEAD, identifier: str = "AUTH-W00-1") -> dict:
    return {
        "schema_version": "1.0", "authorization_id": identifier, "repository": "abbudjoe/biblical-scholar-lab",
        "pr_url": PR_URL, "activation_id": "ACT-W00-REPOSITORY-GOVERNANCE-v3",
        "chatgpt_review_id": "REVIEW-W00-1", "authorized_head_sha": head, "owner_login": "abbudjoe",
        "authorization_channel": "CHATGPT_CONVERSATION_EXPLICIT_APPROVAL",
        "owner_approval_reference": "conversation", "approved_at": _time(-5), "merge_method": "squash",
        "status": "AUTHORIZED",
    }


def _complexity(modules: list[str] | None = None) -> dict:
    return {
        "production_loc_added": 10, "production_loc_removed": 0, "test_loc_added": 10,
        "test_loc_removed": 0, "generated_loc": 0, "production_files_added": len(modules or ["governance/x.py"]),
        "production_files_removed": 0, "modules_added": modules or ["governance/x.py"], "modules_removed": [],
        "tables_added": [], "migrations_added": [], "endpoints_added": [], "cli_commands_added": [],
        "dependencies_added": [], "dependencies_removed": [], "public_contracts_changed": [],
        "abstractions": [], "simpler_alternatives_considered": ["direct validation"],
        "known_duplication_or_debt": [], "waivers": [], "simplicity_conformance": "PASS",
    }


def _handoff() -> dict:
    return {
        "schema_version": "1.0", "project_id": "biblical-scholar-lab",
        "activation_id": "ACT-W00-REPOSITORY-GOVERNANCE-v3", "task_id": "W00", "turn_id": "W00-fixture",
        "codex_run_id": "fixture", "status": "READY_FOR_CHATGPT_REVIEW", "repository": "abbudjoe/biblical-scholar-lab",
        "branch": "codex/w00-repository-governance", "base_sha": BASE, "implementation_head_sha": IMPL,
        "pr_url": PR_URL, "github_actor_login": "abbudjoe", "github_auth_mode": "GH_CLI_EXISTING_AUTH",
        "github_auth_preflight": {"hostname": "github.com", "active_login": "abbudjoe", "auth_healthy": True, "token_override_present": False, "token_exposed": False},
        "objective": "fixture", "acceptance_criteria": ["passes"],
        "design_conformance": {"status": "CONFORMING", "approved_design_ids": ["GOV-01-S01"], "unapproved_design_changes_executed": False},
        "changes": [], "review_targets": [], "commands": [], "evaluations": [], "artifacts": [],
        "delegated_operations": [], "complexity_receipt": _complexity(), "known_risks": [], "decisions_required": [],
        "billable_actions": {"performed": False, "actual_cost_usd": 0}, "next_required_action": "CHATGPT_REVIEW",
        "merge_performed": False, "next_task_started": False,
    }


def _ruleset() -> dict:
    return {
        "id": 20960975, "name": "main-quality-and-authorization-gates", "target": "branch",
        "enforcement": "active", "bypass_actors": [], "current_user_can_bypass": "never",
        "conditions": {"ref_name": {"exclude": [], "include": ["~DEFAULT_BRANCH"]}},
        "rules": [{"type": name} for name in ("deletion", "non_fast_forward", "required_linear_history")] + [
            {"type": "pull_request", "parameters": {"required_approving_review_count": 0, "dismiss_stale_reviews_on_push": True, "require_code_owner_review": False, "require_last_push_approval": False, "required_review_thread_resolution": True, "allowed_merge_methods": ["squash"]}},
            {"type": "required_status_checks", "parameters": {"strict_required_status_checks_policy": True, "do_not_enforce_on_create": False, "required_status_checks": [{"context": name, "integration_id": 15368} for name in sorted(checks.CHECK_NAMES)]}},
        ],
    }


def _trusted_receipt(head: str = HEAD) -> dict:
    record = {
        "schema_version": "1.0", "receipt_type": "TrustedGovernanceValidationReceipt",
        "repository": "abbudjoe/biblical-scholar-lab", "pr_number": 1, "inspected_head_sha": head,
        "base_sha": BASE, "trusted_validator_revision": BASE,
        "workflow_path": ".github/workflows/trusted-governance-validator.yml", "workflow_run_id": 10,
        "workflow_run_attempt": 1, "event": "pull_request_target", "validator_content_hash": "d" * 64,
        "validation_results": {"candidate_input_safety": "PASS", "project_integrity": "PASS"},
        "timestamp": _time(-9), "conclusion": "success",
    }
    record["receipt_hash"] = receipt_hash(record)
    return record


def _owner_receipt() -> dict:
    record = {
        "schema_version": "1.0", "receipt_type": "OwnerMergeAuthorizationReceipt",
        "repository": "abbudjoe/biblical-scholar-lab", "pr_number": 1, "pr_url": PR_URL,
        "authorized_head_sha": HEAD, "chatgpt_review_id": "REVIEW-W00-1",
        "trusted_validator": {"workflow_path": ".github/workflows/trusted-governance-validator.yml", "run_id": 10, "receipt_hash": "e" * 64},
        "authorization_workflow": {"workflow_path": ".github/workflows/owner-merge-authorization.yml", "run_id": 20, "run_attempt": 1, "trusted_revision": BASE},
        "environment_name": "owner-merge-authorization", "timestamp": _time(-1), "conclusion": "success",
    }
    record["receipt_hash"] = receipt_hash(record)
    return record


class ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.activation = json.loads((ROOT / checks.ACTIVATION_PATH).read_text())

    def test_activation_scope_auth_and_handoff_boundaries(self) -> None:
        validate_activation(self.activation); validate_auth_preflight("abbudjoe", set()); validate_handoff(_handoff())
        bad = [
            _replace(self.activation, ("status",), "SUPERSEDED"),
            _replace(self.activation, ("root_turn", "reasoning_effort"), "high"),
            _replace(self.activation, ("approved_design_ids",), [1]),
        ]
        for record in bad:
            with self.assertRaises(ContractError): validate_activation(record)
        with self.assertRaises(ContractError): validate_auth_preflight("other", {"GH_TOKEN"})
        for path, value in (("acceptance_criteria", [1]), ("changes", ["bad"]), ("delegated_operations", [{"role": "luna_runner", "write_performed": False}]), ("status", "MERGE_READY")):
            with self.assertRaises(ContractError): validate_handoff(_replace(_handoff(), (path,), value))
        checks.validate_change_scope(["governance/w00_checks.py"], self.activation)
        with self.assertRaises(ContractError): checks.validate_change_scope(["sources/new.json"], self.activation)

    def test_review_authorization_order_identity_and_append_only(self) -> None:
        review = _comment(REVIEW_MARKER, _review(), 1, -7); authorization = _comment(AUTHORIZATION_MARKER, _authorization(), 2, -4)
        comments = [review, authorization]
        self.assertEqual(current_clean_review(comments, pr_url=PR_URL, activation_id=self.activation["activation_id"], base_sha=BASE, head_sha=HEAD)["review_id"], "REVIEW-W00-1")
        self.assertEqual(current_authorization(comments, repository="abbudjoe/biblical-scholar-lab", pr_url=PR_URL, activation_id=self.activation["activation_id"], head_sha=HEAD, review_id="REVIEW-W00-1")["authorization_id"], "AUTH-W00-1")
        edited = copy.deepcopy(review); edited["updated_at"] = _time(-6)
        reused = comments + [_comment(AUTHORIZATION_MARKER, _authorization("c" * 40), 3, -3)]
        replacement = [_comment(REVIEW_MARKER, _replace(_review(), ("review_id",), "REVIEW-NEW"), 3, -3)]
        for current in ([authorization, review], [edited, authorization], reused):
            with self.assertRaises(ContractError): current_authorization(current, repository="abbudjoe/biblical-scholar-lab", pr_url=PR_URL, activation_id=self.activation["activation_id"], head_sha=HEAD, review_id="REVIEW-W00-1")
        for current in ([], replacement, [authorization, review]):
            with self.assertRaises(ContractError): validate_append_only_comments([review], current)
        validate_append_only_comments([review], comments)

    def test_review_schema_evidence_and_new_commit_invalidation(self) -> None:
        validate_review_schema(_review())
        for record in (_replace(_review(), ("findings",), ["bad"]), _replace(_review(), ("evidence_reviewed",), ["handoff missing"]), _replace(_review(), ("required_next_action",), "STOP")):
            comment = _comment(REVIEW_MARKER, record, 1, -7)
            with self.assertRaises(ContractError): current_clean_review([comment], pr_url=PR_URL, activation_id="ACT-W00-REPOSITORY-GOVERNANCE-v3", base_sha=BASE, head_sha=HEAD)
        with self.assertRaises(ContractError): current_clean_review([_comment(REVIEW_MARKER, _review(), 1, -7)], pr_url=PR_URL, activation_id="ACT-W00-REPOSITORY-GOVERNANCE-v3", base_sha=BASE, head_sha="c" * 40)

    def test_receipt_hashes_and_exact_binding(self) -> None:
        trusted_record, owner = _trusted_receipt(), _owner_receipt()
        validate_trusted_receipt(trusted_record); validate_owner_receipt(owner)
        validate_owner_receipt_binding(owner, pr_number=1, head_sha=HEAD, review_id="REVIEW-W00-1", trusted_run_id=10, authorization_run_id=20, authorization_revision=BASE)
        for path, value in (("event", "pull_request"), ("workflow_path", ".github/workflows/evil.yml")):
            changed = _replace(trusted_record, (path,), value); changed["receipt_hash"] = receipt_hash(changed)
            with self.assertRaises(ContractError): validate_trusted_receipt(changed)
        for kwargs in ({"pr_number": 2}, {"head_sha": "c" * 40}, {"base_sha": "c" * 40}, {"workflow_run_id": 11}):
            expected = {"pr_number": 1, "head_sha": HEAD, "base_sha": BASE, "workflow_run_id": 10}; expected.update(kwargs)
            with self.assertRaises(ContractError): validate_trusted_receipt_binding(trusted_record, **expected)
        for kwargs in ({"pr_number": 2}, {"head_sha": "c" * 40}, {"review_id": "other"}, {"trusted_run_id": 11}, {"authorization_run_id": 21}):
            expected = {"pr_number": 1, "head_sha": HEAD, "review_id": "REVIEW-W00-1", "trusted_run_id": 10, "authorization_run_id": 20, "authorization_revision": BASE}; expected.update(kwargs)
            with self.assertRaises(ContractError): validate_owner_receipt_binding(owner, **expected)

    def test_schema_and_comment_error_branches(self) -> None:
        activation = self.activation
        activation_cases = (("activation_id", "bad"), ("approved_design_commit", "bad"), ("owner_approval", {}), ("activated_paths", ["activations/x.json"]), ("approved_design_ids", ["DR-20", "DR-20"]))
        for field, value in activation_cases:
            with self.assertRaises(ContractError): validate_activation(_replace(activation, (field,), value))
        handoff_cases = (("base_sha", "bad"), ("pr_url", "bad"), ("branch", "main"), ("github_actor_login", "other"), ("next_task_started", True), ("billable_actions", {"performed": True, "actual_cost_usd": 1}))
        for field, value in handoff_cases:
            with self.assertRaises(ContractError): validate_handoff(_replace(_handoff(), (field,), value))
        for body in (REVIEW_MARKER, REVIEW_MARKER + "\n```json\n{bad}\n```", REVIEW_MARKER + "\n```json\n[]\n```"):
            comment = {"id": 1, "created_at": _time(-7), "updated_at": _time(-7), "body": body}
            with self.assertRaises(ContractError): current_clean_review([comment], pr_url=PR_URL, activation_id=activation["activation_id"], base_sha=BASE, head_sha=HEAD)
        for path, value in (("workflow_run_id", 0), ("validation_results", {}), ("validator_content_hash", "bad"), ("timestamp", "bad")):
            record = _replace(_trusted_receipt(), (path,), value); record["receipt_hash"] = receipt_hash(record)
            with self.assertRaises(ContractError): validate_trusted_receipt(record)
        for path, value in (("pr_number", 0), ("environment_name", "other"), ("trusted_validator", {}), ("authorization_workflow", {})):
            record = _replace(_owner_receipt(), (path,), value); record["receipt_hash"] = receipt_hash(record)
            with self.assertRaises(ContractError): validate_owner_receipt(record)


class CommandAndBudgetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.activation = json.loads((ROOT / checks.ACTIVATION_PATH).read_text())

    def test_exact_command_policy_matrix(self) -> None:
        fixtures = json.loads((GOVERNANCE / "fixtures/w00-command-policy.json").read_text())
        for group in fixtures:
            for command in group["commands"]:
                with self.subTest(category=group["category"], command=command):
                    self.assertEqual(assess_command(command, CommandPhase(group["phase"])).allowed, group["allowed"])

    def test_all_activation_budgets_fail_closed(self) -> None:
        valid = BudgetMetrics(100, 0, tuple(f"governance/f{i}.py" for i in range(5)), ("actions/checkout", "actions/upload-artifact"), tuple(sorted(checks.PUBLIC_CONTRACTS)), tuple(sorted(checks.WORKFLOWS)), ())
        checks.validate_budgets(valid, self.activation)
        mutations = [
            valid.__class__(1501, 0, valid.production_files, valid.dependencies, valid.public_contracts, valid.workflows, ()),
            valid.__class__(1, 0, tuple(f"f{i}.py" for i in range(13)), valid.dependencies, valid.public_contracts, valid.workflows, ()),
            valid.__class__(1, 0, valid.production_files, ("a", "b", "c"), valid.public_contracts, valid.workflows, ()),
            valid.__class__(1, 0, valid.production_files, (), ("a", "b", "c", "d"), valid.workflows, ()),
            valid.__class__(1, 0, valid.production_files, (), (), valid.workflows, ("migrations/1.sql",)),
            valid.__class__(1, 0, valid.production_files, (), (), (".github/workflows/other.yml",), ()),
        ]
        for metrics in mutations:
            with self.assertRaises(ContractError): checks.validate_budgets(metrics, self.activation)

    def test_dependency_manifests_are_counted_or_blocked(self) -> None:
        with mock.patch.object(checks, "_diff_line_counts", return_value=(1, 0)), self.assertRaises(ContractError):
            checks.budget_metrics(BASE, HEAD, ["governance/package.json"])

    def test_complexity_and_incomplete_receipt_fail(self) -> None:
        checks.validate_python_complexity("ok.py", "def ok():\n    return True\n")
        with self.assertRaises(ContractError): checks.validate_python_complexity("large.py", "\n".join(f"x{i}={i}" for i in range(501)))
        with self.assertRaises(ContractError): checks.validate_python_complexity("class.py", "class C:\n" + "\n".join(f"    x{i}={i}" for i in range(251)))
        metrics = BudgetMetrics(1, 0, ("governance/x.py",), (), tuple(sorted(checks.PUBLIC_CONTRACTS)), tuple(sorted(checks.WORKFLOWS)), ())
        record = _handoff(); record["complexity_receipt"] = _complexity([])
        with self.assertRaises(ContractError): checks._validate_complexity_receipt(record, metrics)

    def test_handoff_pair_append_only_stem_and_root_phase(self) -> None:
        record = _handoff(); record["commands"] = [{"phase": "merge-only", "command": f"gh pr merge 1 --squash --match-head-commit {HEAD} --delete-branch", "exit_status": 0}]
        with self.assertRaises(ContractError): checks._validate_handoff_commands(record, self.activation)
        outputs = {("rev-list", "--reverse", f"{BASE}..{HEAD}", "--", "handoffs/W00/"): "1", ("diff-tree", "--no-commit-id", "--name-status", "-r", "1", "--", "handoffs/W00/"): "M\thandoffs/W00/old.json"}
        with mock.patch.object(checks, "_git", side_effect=lambda *args: outputs[args]), self.assertRaises(ContractError): checks._validate_append_only_handoffs(BASE, HEAD, "W00")


class TrustedPathTests(unittest.TestCase):
    def _git(self, directory: str, *arguments: str) -> str:
        return subprocess.run(["git", *arguments], cwd=directory, check=True, text=True, capture_output=True).stdout.strip()

    def _repository(self) -> tuple[tempfile.TemporaryDirectory, str, str]:
        temporary = tempfile.TemporaryDirectory(); directory = temporary.name
        self._git(directory, "init", "-b", "main"); self._git(directory, "config", "user.email", "fixture@example.com"); self._git(directory, "config", "user.name", "Fixture")
        for path in checks.TRUSTED_HASH_PATHS:
            target = Path(directory, path); target.parent.mkdir(parents=True, exist_ok=True); target.write_text("trusted\n")
        Path(directory, "safe.json").write_text('{"safe":true}\n')
        self._git(directory, "add", "."); self._git(directory, "commit", "-m", "base")
        return temporary, directory, self._git(directory, "rev-parse", "HEAD")

    def test_candidate_is_inert_and_cannot_replace_base_validator(self) -> None:
        temporary, directory, base = self._repository()
        try:
            sentinel = Path(directory, "executed")
            files = {"run.sh": f"#!/bin/sh\ntouch {sentinel}\n", "Makefile": f"all:\n\ttouch {sentinel}\n", "package.json": '{"scripts":{"postinstall":"touch executed"}}', ".github/workflows/trusted-governance-validator.yml": "name: trusted-governance-integrity\n"}
            for path, content in files.items():
                target = Path(directory, path); target.parent.mkdir(parents=True, exist_ok=True); target.write_text(content)
            self._git(directory, "add", "."); self._git(directory, "commit", "-m", "candidate"); head = self._git(directory, "rev-parse", "HEAD")
            with contextlib.chdir(directory):
                base_hash = checks.validator_content_hash(base); result = checks.inspect_candidate(base, head)
                self.assertEqual(result["execution"], "NONE"); self.assertFalse(sentinel.exists()); self.assertNotEqual(base_hash, checks.validator_content_hash(head))
        finally:
            temporary.cleanup()

    def test_symlink_archives_size_and_parse_depth_block(self) -> None:
        for path in ("../escape", "bad.zip", "bad\\path"):
            with self.assertRaises(ContractError): checks._safe_candidate_path(path)
        nested: object = 0
        for _ in range(checks.MAX_JSON_DEPTH + 2): nested = [nested]
        with self.assertRaises(ContractError): checks._json_depth(nested)
        with mock.patch.object(checks, "_run", return_value=mock.Mock(returncode=0)), mock.patch.object(checks, "changed_paths", return_value=["x"] * (checks.MAX_FILES + 1)), self.assertRaises(ContractError): checks.inspect_candidate(BASE, HEAD)
        oversized = b"x" * (checks.MAX_TOTAL_BYTES // 2 + 1)
        with mock.patch.object(checks, "_run", return_value=mock.Mock(returncode=0)), mock.patch.object(checks, "changed_paths", return_value=["a", "b"]), mock.patch.object(checks, "_candidate_blob", return_value=oversized), self.assertRaises(ContractError): checks.inspect_candidate(BASE, HEAD)
        tree = {("ls-tree", HEAD, "--", "x"): "100644 blob oid\tx", ("cat-file", "-s", "oid"): str(checks.MAX_FILE_BYTES + 1)}
        with mock.patch.object(checks, "_git", side_effect=lambda *args: tree[args]), self.assertRaises(ContractError): checks._candidate_blob(HEAD, "x")
        temporary, directory, base = self._repository()
        try:
            os.symlink("safe.json", Path(directory, "link")); self._git(directory, "add", "link"); self._git(directory, "commit", "-m", "symlink"); head = self._git(directory, "rev-parse", "HEAD")
            with contextlib.chdir(directory), self.assertRaises(ContractError): checks.inspect_candidate(base, head)
        finally:
            temporary.cleanup()

    def test_trusted_workflow_static_security_and_owner_no_merge(self) -> None:
        sources = {path: Path(ROOT, path).read_text() for path in checks.WORKFLOWS}
        with mock.patch.object(checks, "_git_text", side_effect=lambda _revision, path: sources[path]): checks._validate_workflows(HEAD)
        trusted = sources[checks.TRUSTED_WORKFLOW]
        self.assertEqual([item.split("@", 1)[0] for item in re.findall(r"uses:\s*([^\s]+@[^\s]+)", trusted)], ["actions/checkout", "actions/upload-artifact"]); self.assertIn("ref: ${{ github.event.pull_request.base.sha }}", trusted)
        malicious = dict(sources); malicious[checks.TRUSTED_WORKFLOW] += "\nrun: npm install\n"
        with mock.patch.object(checks, "_git_text", side_effect=lambda _revision, path: malicious[path]), self.assertRaises(ContractError): checks._validate_workflows(HEAD)
        self.assertNotRegex(sources[checks.OWNER_WORKFLOW], r"\bgh pr merge\b|\bgit push\b")

    def test_trusted_receipt_creation_binds_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = str(Path(directory, "receipt.json"))
            args = checks.argparse.Namespace(repository="abbudjoe/biblical-scholar-lab", pr_number=1, base_sha=BASE, head_sha=HEAD, trusted_revision=BASE, branch="codex/x", event="pull_request_target", run_id=10, run_attempt=1, output=output)
            with mock.patch.object(checks, "inspect_candidate", return_value={"execution": "NONE"}), mock.patch.object(checks, "validate_project", return_value={"additions": 1}), mock.patch.object(checks, "validate_turn_handoff", return_value={"turn_id": "W00-fixture"}), mock.patch.object(checks, "validator_content_hash", return_value="d" * 64):
                record = checks.create_trusted_receipt(args)["receipt"]
            self.assertEqual(record["inspected_head_sha"], HEAD); validate_trusted_receipt(json.loads(Path(output).read_text()))


class OwnerAndLiveTests(unittest.TestCase):
    def _owner_files(self, directory: str) -> dict[str, str]:
        pr = {"number": 1, "state": "open", "html_url": PR_URL, "base": {"ref": "main", "sha": BASE}, "head": {"ref": "codex/w00-repository-governance", "sha": HEAD}}
        comments = [_comment(REVIEW_MARKER, _review(), 1, -7)]
        checks_json = {"check_runs": [{"name": name, "head_sha": HEAD, "app": {"id": 15368}, "completed_at": _time(-6), "conclusion": "success"} for name in checks.CHECK_NAMES]}
        conversations = {"data": {"repository": {"pullRequest": {"reviewThreads": {"nodes": [{"isResolved": True}], "pageInfo": {"hasNextPage": False}}}}}}
        run = {"id": 10, "run_attempt": 1, "event": "pull_request_target", "status": "completed", "conclusion": "success", "head_sha": BASE, "path": checks.TRUSTED_WORKFLOW}
        values = {"pr": pr, "comments": comments, "checks": checks_json, "conversations": conversations, "run": run, "trusted": _trusted_receipt()}
        paths = {}
        for name, value in values.items():
            path = Path(directory, name + ".json"); path.write_text(json.dumps(value)); paths[name] = str(path)
        paths["output"] = str(Path(directory, "owner.json")); return paths

    def test_owner_workflow_requeries_and_emits_bound_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = self._owner_files(directory)
            args = checks.argparse.Namespace(pr_number=1, authorized_head_sha=HEAD, chatgpt_review_id="REVIEW-W00-1", trusted_run_id=10, workflow_ref="refs/heads/main", workflow_sha=BASE, run_id=20, run_attempt=1, pr_json=paths["pr"], comments_json=paths["comments"], trusted_receipt=paths["trusted"], trusted_run_json=paths["run"], checks_json=paths["checks"], conversations_json=paths["conversations"], output=paths["output"])
            with mock.patch.object(checks, "resolve_activation", return_value={"activation_id": "ACT-W00-REPOSITORY-GOVERNANCE-v3"}), mock.patch.object(checks, "validator_content_hash", return_value="d" * 64): record = checks.create_owner_receipt(args)
            validate_owner_receipt_binding(record, pr_number=1, head_sha=HEAD, review_id="REVIEW-W00-1", trusted_run_id=10, authorization_run_id=20, authorization_revision=BASE)
            args.authorized_head_sha = "c" * 40
            with mock.patch.object(checks, "resolve_activation", return_value={"activation_id": "ACT-W00-REPOSITORY-GOVERNANCE-v3"}), self.assertRaises(ContractError): checks.create_owner_receipt(args)

    def test_quality_conversation_and_dispatch_fail_closed(self) -> None:
        checks.validate_owner_inputs(1, HEAD, "REVIEW-W00-1", 10, "refs/heads/main")
        for values in ((0, HEAD, "R", 10, "refs/heads/main"), (1, "bad", "R", 10, "refs/heads/main"), (1, HEAD, "bad value", 10, "refs/heads/main"), (1, HEAD, "R", 10, "refs/heads/other")):
            with self.assertRaises(ContractError): checks.validate_owner_inputs(*values)
        with self.assertRaises(ContractError): checks._validate_quality_checks({"check_runs": []}, HEAD)
        with self.assertRaises(ContractError): checks._validate_conversations({"data": {"repository": {"pullRequest": {"reviewThreads": {"nodes": [{"isResolved": False}], "pageInfo": {"hasNextPage": False}}}}}})

    def test_exact_live_components_and_bootstrap_state(self) -> None:
        repository = {"default_branch": "main", "visibility": "public", "allow_squash_merge": True, "allow_merge_commit": False, "allow_rebase_merge": False, "allow_auto_merge": False, "delete_branch_on_merge": True}
        environment = {"name": "owner-merge-authorization", "can_admins_bypass": False, "protection_rules": [{"type": "required_reviewers", "prevent_self_review": False, "reviewers": [{"reviewer": {"login": "abbudjoe"}}]}]}
        workflows = {"workflows": [{"path": ".github/workflows/governance-integrity.yml", "state": "active"}]}
        pr = {"state": "open", "draft": True, "base": {"ref": "main"}, "head": {"sha": HEAD}}
        live = {f"repos/{checks.contracts.REPOSITORY}": repository, f"repos/{checks.contracts.REPOSITORY}/rulesets/20960975": _ruleset(), f"repos/{checks.contracts.REPOSITORY}/environments/{checks.contracts.ENVIRONMENT}": environment, f"repos/{checks.contracts.REPOSITORY}/actions/workflows": workflows, f"repos/{checks.contracts.REPOSITORY}/codeowners/errors": {"errors": []}, f"repos/{checks.contracts.REPOSITORY}/pulls/1": pr}
        with mock.patch.object(checks, "_gh_json", side_effect=lambda endpoint: live[endpoint]): result = checks.validate_live_governance(HEAD, _time(0), _time(0), True, True)
        self.assertEqual(result["expected_app_role"], "DEFENSE_IN_DEPTH_ONLY"); self.assertEqual(result["workflow_state"], "W00_BOOTSTRAP_NOT_LIVE_TRUSTED")
        checks.validate_ruleset(_ruleset()); checks.validate_environment(environment); checks.validate_repository_settings(repository)
        for mutation in (_replace(_ruleset(), ("conditions", "ref_name", "exclude"), ["refs/heads/main"]), _replace(_ruleset(), ("rules",), [])):
            with self.assertRaises(ContractError): checks.validate_ruleset(mutation)


class AdapterTests(unittest.TestCase):
    def test_cli_dispatch_and_failure_receipt(self) -> None:
        parser = checks._parser(); arguments = parser.parse_args(["command-policy", "--phase", "implementation", "git status"])
        self.assertTrue(checks._dispatch(arguments)["command_allowed"])
        with mock.patch.object(sys, "argv", ["w00_checks.py", "command-policy", "--phase", "implementation", "gh auth token"]), contextlib.redirect_stdout(io.StringIO()): self.assertEqual(checks.main(), 1)
        with mock.patch.object(sys, "argv", ["w00_checks.py", "command-policy", "--phase", "implementation", "git status"]), contextlib.redirect_stdout(io.StringIO()): self.assertEqual(checks.main(), 0)

    def test_json_comment_and_pr_adapters(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            comments = Path(directory, "comments.json"); comments.write_text(json.dumps([[_comment(REVIEW_MARKER, _review(), 1, -7)]]))
            self.assertEqual(len(checks._comments(str(comments))), 1)
            pr = Path(directory, "pr.json"); pr.write_text(json.dumps({"state": "closed"}))
            with self.assertRaises(ContractError): checks._pr_identity(str(pr))
            comments.write_text("{}")
            with self.assertRaises(ContractError): checks._comments(str(comments))

    def test_protected_base_git_and_project_adapters(self) -> None:
        base = "3d3ebb706fe6c8779445cbbfd9fea271b86d3646"
        activation = checks.resolve_activation(base, "codex/w00-repository-governance")
        self.assertEqual(checks.changed_paths(base, base), []); self.assertEqual(checks._diff_line_counts(base, base), (0, 0))
        self.assertIsInstance(checks._git_json(base, checks.ACTIVATION_PATH), dict); self.assertTrue(checks._git_bytes(base, checks.ACTIVATION_PATH))
        paths = ["governance/w00_contracts.py", "governance/w00_checks.py", *sorted(checks.WORKFLOWS)]
        metrics = BudgetMetrics(100, 0, tuple(paths), ("actions/checkout", "actions/upload-artifact"), tuple(sorted(checks.PUBLIC_CONTRACTS)), tuple(sorted(checks.WORKFLOWS)), ())
        sources = {path: Path(ROOT, path).read_text() for path in paths}
        with mock.patch.object(checks, "resolve_activation", return_value=activation), mock.patch.object(checks, "changed_paths", return_value=paths), mock.patch.object(checks, "budget_metrics", return_value=metrics), mock.patch.object(checks, "_git_text", side_effect=lambda _revision, path: sources[path]), mock.patch.object(checks, "_validate_workflows"):
            self.assertEqual(checks.validate_project(BASE, HEAD, "codex/w00-repository-governance")["additions"], 100)

    def test_handoff_orchestration_and_dispatch_routes(self) -> None:
        activation = json.loads((ROOT / checks.ACTIVATION_PATH).read_text()); paths = tuple(sorted(["governance/w00_contracts.py", "governance/w00_checks.py", *checks.WORKFLOWS]))
        metrics = BudgetMetrics(100, 0, paths, ("actions/checkout", "actions/upload-artifact"), tuple(sorted(checks.PUBLIC_CONTRACTS)), tuple(sorted(checks.WORKFLOWS)), ())
        record = _handoff(); receipt = record["complexity_receipt"]; receipt["modules_added"] = list(paths); receipt["production_files_added"] = len(paths); receipt["dependencies_added"] = list(metrics.dependencies); receipt["public_contracts_changed"] = list(metrics.public_contracts)
        pair = {"handoffs/W00/W00-fixture.md", "handoffs/W00/W00-fixture.json"}; final = "\n".join(sorted(pair))
        git_values = {("rev-parse", f"{HEAD}^"): IMPL, ("diff-tree", "--no-commit-id", "--name-only", "-r", HEAD): final}
        markdown = f"{IMPL} READY_FOR_CHATGPT_REVIEW Expected-App matching is defense in depth only and is not treated as proof of workflow provenance."
        with mock.patch.object(checks, "resolve_activation", return_value=activation), mock.patch.object(checks, "_validate_append_only_handoffs"), mock.patch.object(checks, "_handoff_pair", return_value=tuple(sorted(pair))), mock.patch.object(checks, "_git_json", return_value=record), mock.patch.object(checks, "_git", side_effect=lambda *args: git_values[args]), mock.patch.object(checks, "budget_metrics", return_value=metrics), mock.patch.object(checks, "changed_paths", return_value=list(paths)), mock.patch.object(checks, "_git_text", return_value=markdown):
            self.assertEqual(checks.validate_turn_handoff(BASE, HEAD, "codex/w00-repository-governance", PR_URL)["implementation_head_sha"], IMPL)
            record["turn_id"] = "wrong"
            with self.assertRaises(ContractError): checks.validate_turn_handoff(BASE, HEAD, "codex/w00-repository-governance", PR_URL)
        routes = (("project-integrity", "validate_project"), ("turn-handoff-integrity", "validate_turn_handoff"), ("chatgpt-review-integrity", "validate_review_comments"), ("owner-merge-record-integrity", "validate_authorization_comments"), ("trusted-governance", "create_trusted_receipt"), ("owner-authorize", "create_owner_receipt"), ("live-governance", "validate_live_governance"))
        for name, target in routes:
            arguments = checks.argparse.Namespace(check=name, base_sha=BASE, head_sha=HEAD, branch="codex/x", pr_url=PR_URL, pr_json="p", comments_json="c", expected_head=HEAD, review_limit_observed_at=_time(0), environment_ui_observed_at=_time(0), review_limit_enabled=True, admin_bypass_disabled=True)
            with mock.patch.object(checks, target, return_value={"route": name}): self.assertEqual(checks._dispatch(arguments)["route"], name)

    def test_validator_failure_boundaries(self) -> None:
        with self.assertRaises(ContractError): checks.scan_anti_slop("x.py", "# " + "TO" + "DO")
        for record in ({}, {"default_branch": "other"}):
            with self.assertRaises(ContractError): checks.validate_repository_settings(record)
        for record in ({}, {"name": checks.contracts.ENVIRONMENT, "protection_rules": []}, {"name": checks.contracts.ENVIRONMENT, "can_admins_bypass": True, "protection_rules": [{"type": "required_reviewers", "prevent_self_review": False, "reviewers": [{"reviewer": {"login": "abbudjoe"}}]}]}):
            with self.assertRaises(ContractError): checks.validate_environment(record)
        with self.assertRaises(ContractError): checks.validate_codeowners("* @abbudjoe", {"errors": []})
        with self.assertRaises(ContractError): checks.validate_codeowners((ROOT / ".github/CODEOWNERS").read_text(), {"errors": [{"line": 1}]})
        with self.assertRaises(ContractError): checks._recent(_time(-1500))
        with self.assertRaises(ContractError): checks._recent("bad")
        with mock.patch.object(checks, "_run", return_value=mock.Mock(stdout="[]")), self.assertRaises(ContractError): checks._gh_json("repos/x")
        with mock.patch.object(checks, "_git_text", return_value="[]"), self.assertRaises(ContractError): checks._git_json(BASE, "x.json")


if __name__ == "__main__":
    unittest.main(verbosity=2)
