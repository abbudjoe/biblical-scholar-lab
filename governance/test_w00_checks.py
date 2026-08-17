"""Positive and negative W00 conformance fixtures."""

from __future__ import annotations

import copy
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


GOVERNANCE_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = GOVERNANCE_DIR.parent
sys.path.insert(0, str(GOVERNANCE_DIR))

import w00_checks as checks  # noqa: E402

from w00_checks import (  # noqa: E402
    CHECK_NAMES,
    validate_budgets,
    validate_change_scope,
    validate_codeowners,
    validate_handoff_commit,
    validate_repository_settings,
    validate_review_limit,
    validate_ruleset,
    scan_anti_slop,
)
from w00_contracts import (  # noqa: E402
    AUTHORIZATION_MARKER,
    REVIEW_MARKER,
    CommandPhase,
    ContractError,
    assess_command,
    current_authorization,
    current_clean_review,
    validate_activation,
    validate_authorization_schema,
    validate_auth_preflight,
    validate_handoff,
    validate_review_schema,
)


BASE_SHA = "a" * 40
HEAD_SHA = "b" * 40
IMPLEMENTATION_SHA = "c" * 40
PR_URL = "https://github.com/abbudjoe/biblical-scholar-lab/pull/1"


def _comment(marker: str, record: dict) -> dict:
    return {"body": f"{marker}\n\n```json\n{json.dumps(record)}\n```"}


def _replace(record: dict, path: tuple[str, ...], value) -> dict:
    changed = copy.deepcopy(record)
    target = changed
    for field in path[:-1]:
        target = target[field]
    target[path[-1]] = value
    return changed


def _review(head_sha: str = HEAD_SHA, disposition: str = "CHATGPT_REVIEW_CLEAN") -> dict:
    return {
        "schema_version": "1.0",
        "review_id": "REVIEW-W00-1",
        "pr_url": PR_URL,
        "activation_id": "ACT-W00-REPOSITORY-GOVERNANCE-v3",
        "base_sha": BASE_SHA,
        "reviewed_head_sha": head_sha,
        "reviewer": "ChatGPT",
        "disposition": disposition,
        "summary": "Exact-head review fixture.",
        "findings": [],
        "evidence_reviewed": ["handoffs/W00/W00-fixture.json"],
        "required_next_action": "OWNER_AUTHORIZATION" if disposition == "CHATGPT_REVIEW_CLEAN" else "SOL_REPAIR",
        "review_timestamp": "2026-08-17T22:00:00Z",
    }


def _authorization(head_sha: str = HEAD_SHA, status: str = "AUTHORIZED") -> dict:
    return {
        "schema_version": "1.0",
        "authorization_id": "AUTH-W00-1",
        "repository": "abbudjoe/biblical-scholar-lab",
        "pr_url": PR_URL,
        "activation_id": "ACT-W00-REPOSITORY-GOVERNANCE-v3",
        "chatgpt_review_id": "REVIEW-W00-1",
        "authorized_head_sha": head_sha,
        "owner_login": "abbudjoe",
        "authorization_channel": "CHATGPT_CONVERSATION_EXPLICIT_APPROVAL",
        "owner_approval_reference": "conversation-fixture",
        "approved_at": "2026-08-17T22:05:00Z",
        "merge_method": "squash",
        "status": status,
    }


def _complexity_receipt() -> dict:
    return {
        "production_loc_added": 10,
        "production_loc_removed": 0,
        "test_loc_added": 10,
        "test_loc_removed": 0,
        "generated_loc": 0,
        "production_files_added": 1,
        "production_files_removed": 0,
        "modules_added": ["governance fixture"],
        "modules_removed": [],
        "tables_added": [],
        "migrations_added": [],
        "endpoints_added": [],
        "cli_commands_added": ["local governance verification CLI"],
        "dependencies_added": [],
        "dependencies_removed": [],
        "public_contracts_changed": [],
        "abstractions": [],
        "simpler_alternatives_considered": ["standard library direct validation"],
        "known_duplication_or_debt": [],
        "waivers": [],
        "simplicity_conformance": "PASS",
    }


def _handoff() -> dict:
    return {
        "schema_version": "1.0",
        "project_id": "biblical-scholar-lab",
        "activation_id": "ACT-W00-REPOSITORY-GOVERNANCE-v3",
        "task_id": "W00",
        "turn_id": "W00-fixture",
        "codex_run_id": "fixture",
        "status": "READY_FOR_CHATGPT_REVIEW",
        "repository": "abbudjoe/biblical-scholar-lab",
        "branch": "codex/w00-repository-governance",
        "base_sha": BASE_SHA,
        "implementation_head_sha": IMPLEMENTATION_SHA,
        "pr_url": PR_URL,
        "compare_url": "https://github.com/abbudjoe/biblical-scholar-lab/compare/main...codex/w00-repository-governance",
        "github_actor_login": "abbudjoe",
        "github_auth_mode": "GH_CLI_EXISTING_AUTH",
        "github_auth_preflight": {
            "hostname": "github.com",
            "active_login": "abbudjoe",
            "auth_healthy": True,
            "token_override_present": False,
            "token_exposed": False,
            "receipt_path": None,
        },
        "objective": "W00 fixture",
        "acceptance_criteria": ["fixture passes"],
        "design_conformance": {
            "status": "CONFORMING",
            "approved_design_ids": ["GOV-01"],
            "unapproved_design_changes_executed": False,
        },
        "changes": [],
        "review_targets": [],
        "commands": [],
        "evaluations": [],
        "artifacts": [],
        "delegated_operations": [],
        "complexity_receipt": _complexity_receipt(),
        "known_risks": [],
        "decisions_required": [],
        "billable_actions": {"performed": False, "actual_cost_usd": 0},
        "next_required_action": "CHATGPT_REVIEW",
        "merge_performed": False,
        "next_task_started": False,
    }


def _ruleset() -> dict:
    return {
        "name": "main-quality-and-authorization-gates",
        "target": "branch",
        "enforcement": "active",
        "bypass_actors": [],
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "rules": [
            {"type": "deletion"},
            {"type": "non_fast_forward"},
            {"type": "required_linear_history"},
            {
                "type": "pull_request",
                "parameters": {
                    "required_approving_review_count": 0,
                    "require_code_owner_review": False,
                    "required_review_thread_resolution": True,
                },
            },
            {
                "type": "required_status_checks",
                "parameters": {
                    "strict_required_status_checks_policy": True,
                    "required_status_checks": [
                        {"context": name, "integration_id": 15368} for name in sorted(CHECK_NAMES)
                    ],
                },
            },
        ],
    }


class ActivationAndScopeFixtures(unittest.TestCase):
    def setUp(self) -> None:
        path = REPOSITORY_ROOT / "activations/ACT-W00-REPOSITORY-GOVERNANCE-v3.json"
        self.activation = json.loads(path.read_text(encoding="utf-8"))

    def test_valid_activation_and_scope(self) -> None:
        validate_activation(self.activation)
        validate_change_scope(["governance/w00_checks.py", ".github/workflows/governance-integrity.yml"], self.activation)

    def test_invalid_activation_and_out_of_scope_change_block(self) -> None:
        invalid = copy.deepcopy(self.activation)
        invalid["status"] = "SUPERSEDED"
        with self.assertRaises(ContractError):
            validate_activation(invalid)
        with self.assertRaises(ContractError):
            validate_change_scope(["design/approved/DR-20-benchmark-charter.md"], self.activation)

    def test_model_role_and_token_override_block(self) -> None:
        invalid = copy.deepcopy(self.activation)
        invalid["root_turn"]["model"] = "gpt-5.6-luna"
        with self.assertRaises(ContractError):
            validate_activation(invalid)
        validate_auth_preflight("abbudjoe", set())
        with self.assertRaises(ContractError):
            validate_auth_preflight("abbudjoe", {"GH_TOKEN"})

    def test_activation_schema_boundaries_block(self) -> None:
        cases = [
            (("activation_id",), "bad"), (("objective",), ""),
            (("root_turn", "reasoning_effort"), "low"), (("root_turn", "reasoning_effort"), "high"),
            (("root_turn", "task_branch"), "main"), (("approved_design_ids",), []),
            (("approved_design_ids",), [1]), (("approved_design_ids",), ["DR-20", "DR-20"]),
            (("activated_paths",), ["activations/changed.json"]),
            (("owner_approval", "owner"), "other"), (("owner_approval", "approved_at"), "bad-time"),
        ]
        for path, value in cases:
            with self.subTest(path=path, value=value), self.assertRaises(ContractError):
                validate_activation(_replace(self.activation, path, value))
        with self.assertRaises(ContractError):
            validate_auth_preflight("other", set())


class HandoffFixtures(unittest.TestCase):
    def test_valid_handoff_only_commit(self) -> None:
        pair = {"handoffs/W00/W00-fixture.md", "handoffs/W00/W00-fixture.json"}
        validate_handoff_commit(_handoff(), final_paths=sorted(pair), parent_sha=IMPLEMENTATION_SHA, expected_pair=pair)

    def test_parent_mismatch_and_code_in_final_commit_block(self) -> None:
        pair = {"handoffs/W00/W00-fixture.md", "handoffs/W00/W00-fixture.json"}
        with self.assertRaises(ContractError):
            validate_handoff_commit(_handoff(), final_paths=sorted(pair), parent_sha=HEAD_SHA, expected_pair=pair)
        with self.assertRaises(ContractError):
            validate_handoff_commit(_handoff(), final_paths=[*sorted(pair), "governance/w00_checks.py"], parent_sha=IMPLEMENTATION_SHA, expected_pair=pair)

    def test_prohibited_claim_and_luna_write_block(self) -> None:
        claim = _handoff()
        claim["status"] = "MERGE_READY"
        with self.assertRaises(ContractError):
            validate_handoff(claim)
        delegated = _handoff()
        delegated["delegated_operations"] = [{"role": "luna_runner", "write_performed": True}]
        with self.assertRaises(ContractError):
            validate_handoff(delegated)

    def test_handoff_schema_boundaries_block(self) -> None:
        cases = [
            (("schema_version",), "2.0"), (("github_actor_login",), "other"),
            (("next_task_started",), True), (("base_sha",), "bad"),
            (("pr_url",), "not-a-uri"), (("branch",), "main"),
            (("github_auth_preflight", "auth_healthy"), False),
            (("design_conformance", "status"), "DEVIATION_PROPOSED"),
            (("complexity_receipt", "simplicity_conformance"), "WAIVER_REQUIRED"),
            (("complexity_receipt", "production_loc_added"), -1),
            (("acceptance_criteria",), "not-an-array"),
            (("billable_actions", "performed"), True),
        ]
        for path, value in cases:
            with self.subTest(path=path), self.assertRaises(ContractError):
                validate_handoff(_replace(_handoff(), path, value))
        luna = _handoff()
        luna["delegated_operations"] = [{"role": "luna_runner", "write_performed": False}]
        with self.assertRaises(ContractError):
            validate_handoff(luna)

    def test_design_review_blocker_handoff_accepts_only_matching_design_state(self) -> None:
        blocked = _handoff()
        blocked["status"] = "BLOCKED_REQUIRES_DESIGN_REVIEW"
        blocked["design_conformance"]["status"] = "BLOCKED_REQUIRES_DESIGN_REVIEW"
        validate_handoff(blocked)
        blocked["design_conformance"]["status"] = "CONFORMING"
        with self.assertRaises(ContractError):
            validate_handoff(blocked)


class ExactHeadRecordFixtures(unittest.TestCase):
    def test_current_review_and_authorization_accept(self) -> None:
        comments = [_comment(REVIEW_MARKER, _review()), _comment(AUTHORIZATION_MARKER, _authorization())]
        review = current_clean_review(comments, pr_url=PR_URL, activation_id="ACT-W00-REPOSITORY-GOVERNANCE-v3", base_sha=BASE_SHA, head_sha=HEAD_SHA)
        authorization = current_authorization(comments, repository="abbudjoe/biblical-scholar-lab", pr_url=PR_URL, activation_id="ACT-W00-REPOSITORY-GOVERNANCE-v3", head_sha=HEAD_SHA, review_id=review["review_id"])
        self.assertEqual(authorization["authorized_head_sha"], HEAD_SHA)

    def test_stale_review_and_authorization_block(self) -> None:
        comments = [_comment(REVIEW_MARKER, _review("c" * 40)), _comment(AUTHORIZATION_MARKER, _authorization("c" * 40))]
        with self.assertRaises(ContractError):
            current_clean_review(comments, pr_url=PR_URL, activation_id="ACT-W00-REPOSITORY-GOVERNANCE-v3", base_sha=BASE_SHA, head_sha=HEAD_SHA)
        with self.assertRaises(ContractError):
            current_authorization(comments, repository="abbudjoe/biblical-scholar-lab", pr_url=PR_URL, activation_id="ACT-W00-REPOSITORY-GOVERNANCE-v3", head_sha=HEAD_SHA, review_id="REVIEW-W00-1")

    def test_reused_or_superseded_authorization_blocks(self) -> None:
        reused = [_comment(AUTHORIZATION_MARKER, _authorization()), _comment(AUTHORIZATION_MARKER, _authorization())]
        with self.assertRaises(ContractError):
            current_authorization(reused, repository="abbudjoe/biblical-scholar-lab", pr_url=PR_URL, activation_id="ACT-W00-REPOSITORY-GOVERNANCE-v3", head_sha=HEAD_SHA, review_id="REVIEW-W00-1")
        superseded = _authorization(status="SUPERSEDED")
        superseded["authorization_id"] = "AUTH-W00-2"
        with self.assertRaises(ContractError):
            current_authorization([_comment(AUTHORIZATION_MARKER, superseded)], repository="abbudjoe/biblical-scholar-lab", pr_url=PR_URL, activation_id="ACT-W00-REPOSITORY-GOVERNANCE-v3", head_sha=HEAD_SHA, review_id="REVIEW-W00-1")

    def test_malformed_records_and_missing_evidence_block(self) -> None:
        invalid_review = _review()
        invalid_review["summary"] = ""
        comments = [{"body": REVIEW_MARKER + "\n```json\n{bad}\n```"}, _comment(REVIEW_MARKER, invalid_review), "not-a-comment"]
        with self.assertRaises(ContractError):
            current_clean_review(comments, pr_url=PR_URL, activation_id="ACT-W00-REPOSITORY-GOVERNANCE-v3", base_sha=BASE_SHA, head_sha=HEAD_SHA)
        no_evidence = _review()
        no_evidence["evidence_reviewed"] = []
        with self.assertRaises(ContractError):
            current_clean_review([_comment(REVIEW_MARKER, no_evidence)], pr_url=PR_URL, activation_id="ACT-W00-REPOSITORY-GOVERNANCE-v3", base_sha=BASE_SHA, head_sha=HEAD_SHA)
        invalid_auth = _authorization()
        invalid_auth["repository"] = "invalid"
        with self.assertRaises(ContractError):
            current_authorization([_comment(AUTHORIZATION_MARKER, invalid_auth)], repository="abbudjoe/biblical-scholar-lab", pr_url=PR_URL, activation_id="ACT-W00-REPOSITORY-GOVERNANCE-v3", head_sha=HEAD_SHA, review_id="REVIEW-W00-1")

    def test_review_and_authorization_schema_boundaries_block(self) -> None:
        review_cases = [
            (("reviewer",), "other"), (("pr_url",), "bad"), (("base_sha",), "bad"),
            (("review_timestamp",), 1), (("review_timestamp",), "bad"),
            (("disposition",), "UNKNOWN"), (("findings",), "bad"),
            (("required_next_action",), "UNKNOWN"),
        ]
        auth_cases = [
            (("owner_login",), "other"), (("merge_method",), "merge"),
            (("status",), "UNKNOWN"), (("repository",), "bad"),
            (("authorized_head_sha",), "bad"), (("approved_at",), "bad"),
            (("authorization_id",), ""),
        ]
        for path, value in review_cases:
            with self.subTest(record="review", path=path), self.assertRaises(ContractError):
                validate_review_schema(_replace(_review(), path, value))
        for path, value in auth_cases:
            with self.subTest(record="authorization", path=path), self.assertRaises(ContractError):
                validate_authorization_schema(_replace(_authorization(), path, value))


class PolicyAndAntiSlopFixtures(unittest.TestCase):
    def test_command_policy_matrix(self) -> None:
        fixtures = json.loads((GOVERNANCE_DIR / "fixtures/w00-command-policy.json").read_text(encoding="utf-8"))
        for fixture in fixtures:
            with self.subTest(fixture=fixture["name"]):
                decision = assess_command(fixture["command"], CommandPhase(fixture["phase"]))
                self.assertEqual(decision.allowed, fixture["allowed"], decision.reason)

    def test_unfinished_markers_and_oversize_block(self) -> None:
        scan_anti_slop("governance/example.py", "def complete():\n    return True\n")
        with self.assertRaises(ContractError):
            scan_anti_slop("governance/example.py", "# " + "TO" + "DO" + ": later")
        activation = json.loads((REPOSITORY_ROOT / "activations/ACT-W00-REPOSITORY-GOVERNANCE-v3.json").read_text(encoding="utf-8"))
        with self.assertRaises(ContractError):
            validate_budgets(1501, 0, 1, activation)


class LiveGovernanceFixtures(unittest.TestCase):
    def test_exact_repository_ruleset_review_limit_and_codeowners_accept(self) -> None:
        repository = {
            "default_branch": "main", "visibility": "public", "allow_squash_merge": True,
            "allow_merge_commit": False, "allow_rebase_merge": False,
            "allow_auto_merge": False, "delete_branch_on_merge": True,
        }
        review_limit = {
            "repository": "abbudjoe/biblical-scholar-lab",
            "setting": "Limit to users explicitly granted read or higher access",
            "enabled": True,
            "verification_method": "SUPPORTED_AUTHENTICATED_BROWSER",
            "verified_at": "2026-08-17T22:00:00Z",
            "evidence": "authenticated settings UI",
        }
        validate_repository_settings(repository)
        validate_ruleset(_ruleset())
        validate_review_limit(review_limit)
        validate_codeowners((REPOSITORY_ROOT / ".github/CODEOWNERS").read_text(encoding="utf-8"))

    def test_force_push_deletion_unresolved_and_untrusted_checks_block(self) -> None:
        for mutation in ("non_fast_forward", "deletion"):
            invalid = _ruleset()
            invalid["rules"] = [rule for rule in invalid["rules"] if rule["type"] != mutation]
            with self.assertRaises(ContractError):
                validate_ruleset(invalid)
        unresolved = _ruleset()
        next(rule for rule in unresolved["rules"] if rule["type"] == "pull_request")["parameters"]["required_review_thread_resolution"] = False
        with self.assertRaises(ContractError):
            validate_ruleset(unresolved)
        untrusted = _ruleset()
        next(rule for rule in untrusted["rules"] if rule["type"] == "required_status_checks")["parameters"]["required_status_checks"][0]["integration_id"] = None
        with self.assertRaises(ContractError):
            validate_ruleset(untrusted)


class IntegratedControlPlaneFixtures(unittest.TestCase):
    def setUp(self) -> None:
        activation_path = REPOSITORY_ROOT / "activations/ACT-W00-REPOSITORY-GOVERNANCE-v3.json"
        self.activation = json.loads(activation_path.read_text(encoding="utf-8"))

    def test_protected_base_activation_and_git_readers(self) -> None:
        base = "3d3ebb706fe6c8779445cbbfd9fea271b86d3646"
        resolved = checks.resolve_activation(base, "codex/w00-repository-governance")
        self.assertEqual(resolved["activation_id"], "ACT-W00-REPOSITORY-GOVERNANCE-v3")
        self.assertEqual(checks.changed_paths(base, base), [])
        self.assertEqual(checks._diff_line_counts(base, base), (0, 0))
        deltas = {"+value": (1, 0), "-value": (0, 1), "+": (0, 0), " context": (0, 0), "+++ file": (0, 0)}
        for line, expected in deltas.items():
            self.assertEqual(checks._substantive_delta(line), expected)
        self.assertIn("schema_version", checks._git_json(base, checks.ACTIVATION_PATH))
        self.assertTrue(checks._git_bytes(base, checks.ACTIVATION_PATH))

    def test_project_orchestration_and_static_metrics(self) -> None:
        paths = ["governance/w00_contracts.py", "governance/w00_checks.py", ".github/workflows/governance-integrity.yml"]
        content = {name: (REPOSITORY_ROOT / name).read_text(encoding="utf-8") for name in paths}
        with mock.patch.object(checks, "resolve_activation", return_value=self.activation), mock.patch.object(checks, "changed_paths", return_value=paths), mock.patch.object(checks, "_diff_line_counts", return_value=(500, 0)), mock.patch.object(checks, "_git_text", side_effect=lambda _, name: content[name]):
            result = checks.validate_project(BASE_SHA, HEAD_SHA, "codex/w00-repository-governance")
        self.assertEqual(result["additions"], 500)
        for name in paths[:2]:
            checks.validate_python_complexity(name, content[name])

    def test_handoff_orchestration_and_command_policy(self) -> None:
        record = _handoff()
        record["commands"] = [{"phase": "implementation", "command": "git status"}]
        pair = ["handoffs/W00/W00-fixture.md", "handoffs/W00/W00-fixture.json"]
        git_results = {("rev-parse", HEAD_SHA + "^"): IMPLEMENTATION_SHA, ("diff-tree", "--no-commit-id", "--name-only", "-r", HEAD_SHA): "\n".join(pair)}
        with mock.patch.object(checks, "resolve_activation", return_value=self.activation), mock.patch.object(checks, "changed_paths", return_value=pair), mock.patch.object(checks, "_git_json", return_value=record), mock.patch.object(checks, "_git", side_effect=lambda *args: git_results[args]), mock.patch.object(checks, "_git_text", return_value=f"{IMPLEMENTATION_SHA} READY_FOR_CHATGPT_REVIEW"):
            result = checks.validate_turn_handoff(BASE_SHA, HEAD_SHA, "codex/w00-repository-governance", PR_URL)
        self.assertEqual(result["implementation_head_sha"], IMPLEMENTATION_SHA)

    def test_comment_and_live_file_adapters(self) -> None:
        pr = {"state": "open", "html_url": PR_URL, "base": {"ref": "main", "sha": BASE_SHA}, "head": {"ref": "codex/w00-repository-governance", "sha": HEAD_SHA}}
        comments = [_comment(REVIEW_MARKER, _review()), _comment(AUTHORIZATION_MARKER, _authorization())]
        repository = {"default_branch": "main", "visibility": "public", "allow_squash_merge": True, "allow_merge_commit": False, "allow_rebase_merge": False, "allow_auto_merge": False, "delete_branch_on_merge": True}
        review_limit = {"repository": "abbudjoe/biblical-scholar-lab", "setting": "Limit to users explicitly granted read or higher access", "enabled": True, "verification_method": "SUPPORTED_AUTHENTICATED_BROWSER", "verified_at": "2026-08-17T22:00:00Z", "evidence": "settings UI"}
        with tempfile.TemporaryDirectory() as directory:
            files = {"pr": pr, "comments": comments, "repository": repository, "ruleset": _ruleset(), "limit": review_limit}
            paths = {name: Path(directory, name + ".json") for name in files}
            for name, value in files.items():
                paths[name].write_text(json.dumps(value), encoding="utf-8")
            with mock.patch.object(checks, "resolve_activation", return_value=self.activation):
                self.assertEqual(checks.validate_review_comments(str(paths["pr"]), str(paths["comments"]))["reviewed_head_sha"], HEAD_SHA)
                self.assertEqual(checks.validate_authorization_comments(str(paths["pr"]), str(paths["comments"]))["authorized_head_sha"], HEAD_SHA)
            result = checks.validate_live_governance(str(paths["repository"]), str(paths["ruleset"]), str(paths["limit"]), str(REPOSITORY_ROOT / ".github/CODEOWNERS"))
        self.assertTrue(result["code_review_limit"])

    def test_cli_dispatch_success_and_failure(self) -> None:
        parser = checks._parser()
        arguments = parser.parse_args(["command-policy", "--phase", "implementation", "git status"])
        self.assertTrue(checks._dispatch(arguments)["command_allowed"])
        with mock.patch.object(sys, "argv", ["w00_checks.py", "command-policy", "--phase", "implementation", "gh auth token"]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(checks.main(), 1)
        with mock.patch.object(sys, "argv", ["w00_checks.py", "command-policy", "--phase", "implementation", "git status"]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(checks.main(), 0)

    def test_static_and_orchestration_failure_boundaries(self) -> None:
        with mock.patch.object(checks, "_git_text", return_value="[]"), self.assertRaises(ContractError):
            checks._git_json(BASE_SHA, "record.json")
        with mock.patch.object(checks, "_git", return_value=""), self.assertRaises(ContractError):
            checks.resolve_activation(BASE_SHA, "codex/missing")
        completed = mock.Mock(returncode=1)
        with mock.patch.object(checks.subprocess, "run", return_value=completed), self.assertRaises(ContractError):
            checks._validate_activation_identity(self.activation, BASE_SHA, checks.ACTIVATION_PATH)
        checks.scan_anti_slop("example.py", "return True")
        with self.assertRaises(ContractError):
            checks.scan_anti_slop("example.py", "    pass")
        with self.assertRaises(ContractError):
            checks.validate_python_complexity("large.py", "\n".join(f"value_{index} = {index}" for index in range(501)))
        with self.assertRaises(ContractError):
            checks.validate_python_complexity("complex.py", "def f(x):\n" + "\n".join(f"    if x == {index}: x += 1" for index in range(11)))
        with self.assertRaises(ContractError):
            checks.validate_budgets(0, 0, 13, self.activation)
        with mock.patch.object(checks, "_git_text", return_value="project-integrity"), self.assertRaises(ContractError):
            checks._validate_workflow(HEAD_SHA)
        for pair in ([], ["handoffs/W00/a.md", "handoffs/W00/a.json", "handoffs/W00/b.json"], ["handoffs/W00/a.md", "handoffs/W00/b.json"], ["handoffs/W00/a.md", "handoffs/W00/a.txt"]):
            with mock.patch.object(checks, "changed_paths", return_value=pair), self.assertRaises(ContractError):
                checks._handoff_pair(BASE_SHA, HEAD_SHA, "W00")
        with self.assertRaises(ContractError):
            checks._validate_handoff_identity(_replace(_handoff(), ("repository",), "other/repo"), self.activation, "codex/w00-repository-governance", BASE_SHA, PR_URL)
        command_cases = [[{}], [{"command": "git status", "phase": "bad"}], [{"command": "gh auth token"}]]
        for commands in command_cases:
            record = _handoff(); record["commands"] = commands
            with self.assertRaises(ContractError):
                checks._validate_handoff_commands(record, self.activation)

    def test_live_adapter_failure_boundaries(self) -> None:
        invalid_repository = {"default_branch": "other", "visibility": "public"}
        with self.assertRaises(ContractError):
            checks.validate_repository_settings(invalid_repository)
        ruleset_mutations = [("name", "other"), ("bypass_actors", [{"actor_id": 1}]), ("conditions", {}), ("rules", [])]
        for field, value in ruleset_mutations:
            with self.assertRaises(ContractError):
                checks.validate_ruleset(_replace(_ruleset(), (field,), value))
        invalid_status = _ruleset(); next(rule for rule in invalid_status["rules"] if rule["type"] == "required_status_checks")["parameters"]["strict_required_status_checks_policy"] = False
        with self.assertRaises(ContractError):
            checks.validate_ruleset(invalid_status)
        for receipt in ({}, {"repository": "abbudjoe/biblical-scholar-lab", "setting": "Limit to users explicitly granted read or higher access", "enabled": True, "verification_method": "SUPPORTED_AUTHENTICATED_BROWSER", "verified_at": "", "evidence": ""}):
            with self.assertRaises(ContractError):
                checks.validate_review_limit(receipt)
        with self.assertRaises(ContractError):
            checks.validate_codeowners("* @abbudjoe")
        with tempfile.TemporaryDirectory() as directory:
            invalid_comments = Path(directory, "comments.json"); invalid_comments.write_text("{}", encoding="utf-8")
            with self.assertRaises(ContractError):
                checks._comments(str(invalid_comments))
            closed_pr = Path(directory, "pr.json"); closed_pr.write_text(json.dumps({"state": "closed"}), encoding="utf-8")
            with self.assertRaises(ContractError):
                checks._pr_identity(str(closed_pr))

    def test_all_cli_dispatch_routes(self) -> None:
        routes = [
            ("project-integrity", "validate_project", {"base_sha": BASE_SHA, "head_sha": HEAD_SHA, "branch": "codex/x"}),
            ("turn-handoff-integrity", "validate_turn_handoff", {"base_sha": BASE_SHA, "head_sha": HEAD_SHA, "branch": "codex/x", "pr_url": PR_URL}),
            ("chatgpt-review-integrity", "validate_review_comments", {"pr_json": "pr", "comments_json": "comments"}),
            ("owner-merge-record-integrity", "validate_authorization_comments", {"pr_json": "pr", "comments_json": "comments"}),
            ("live-governance", "validate_live_governance", {"repository_json": "repo", "ruleset_json": "rules", "review_limit_json": "limit", "codeowners": "owners"}),
        ]
        for check_name, target, values in routes:
            arguments = checks.argparse.Namespace(check=check_name, **values)
            with mock.patch.object(checks, target, return_value={"route": check_name}):
                self.assertEqual(checks._dispatch(arguments)["route"], check_name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
