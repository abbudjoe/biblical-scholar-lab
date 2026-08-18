from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "governance"))

import w00_checks as checks
import w00_contracts as contracts
from w00_contracts import ContractError

BASE, HEAD, IMPL = "a" * 40, "b" * 40, "c" * 40
TREE = "d" * 40
PR_URL = f"https://github.com/{contracts.REPOSITORY}/pull/1"
RECORDS = cast(dict[str, Any], json.loads((ROOT / "governance/fixtures/w00-records.json").read_text()))


def activation() -> dict[str, Any]:
    return cast(dict[str, Any], json.loads((ROOT / checks.ACTIVATION_PATH).read_text()))


def complexity(modules: list[str] | None = None) -> dict[str, Any]:
    value = cast(dict[str, Any], copy.deepcopy(RECORDS["handoff"]["complexity_receipt"]))
    return value | {"production_files_added": len(modules or []), "modules_added": modules or [], "cli_commands_added": sorted({*checks.CLI_SPECS, "command-policy"})}


def handoff(parent: str = IMPL) -> dict[str, Any]:
    value = cast(dict[str, Any], copy.deepcopy(RECORDS["handoff"])) | {"implementation_head_sha": parent, "acceptance_criteria": ["fixture"]}
    validators = (f"project-integrity --base-sha {checks.BASE_SHA} --head-sha HEAD --branch {contracts.BRANCH}", f"turn-handoff-integrity --base-sha {checks.BASE_SHA} --head-sha HEAD --branch {contracts.BRANCH} --pr-url {PR_URL}", "package-integrity --revision HEAD", "live-governance --expected-head HEAD --review-limit-observed-at Z --environment-ui-observed-at Z --review-limit-enabled --admin-bypass-disabled")
    commands = checks.REQUIRED_HANDOFF_COMMANDS | {"gh auth status --active --hostname github.com", *(f"python3 governance/w00_checks.py {item}" for item in validators)}
    value["commands"] = [{"phase": "implementation", "command": command, "exit_status": 0, "result": "pass"} for command in sorted(commands)]
    value["evaluations"] = [{"name": name, "status": "PASS", "evidence": "fixture"} for name in checks.REQUIRED_EVALUATIONS]
    return value


def marked(marker: str, record: dict[str, Any], identifier: int, when: datetime) -> dict[str, Any]:
    stamp = when.isoformat().replace("+00:00", "Z")
    return {"id": identifier, "created_at": stamp, "updated_at": stamp, "body": f"{marker}\n```json\n{json.dumps(record)}\n```"}


def metadata(path: str = "safe.txt", *, mode: str = "100644", size: int = 1) -> tuple[dict[str, Any], dict[str, Any]]:
    tree, compare = cast(dict[str, Any], copy.deepcopy(RECORDS["tree"])), cast(dict[str, Any], copy.deepcopy(RECORDS["compare"]))
    tree.update({"sha": TREE})
    tree["tree"][0].update({"path": path, "mode": mode, "size": size})
    compare["commits"][0]["commit"] = {"tree": {"sha": TREE}}
    compare["files"][0]["filename"] = path
    return tree, compare


class GitFixture(unittest.TestCase):
    def repository(self) -> tuple[tempfile.TemporaryDirectory[str], str, str]:
        temporary = tempfile.TemporaryDirectory()
        directory = temporary.name
        self.git(directory, "init", "-q")
        self.git(directory, "config", "user.email", "fixture@example.test")
        self.git(directory, "config", "user.name", "Fixture")
        Path(directory, "seed").write_text("seed\n")
        self.git(directory, "add", "seed")
        self.git(directory, "commit", "-q", "-m", "base")
        return temporary, directory, self.git(directory, "rev-parse", "HEAD")

    def git(self, directory: str, *arguments: str) -> str:
        return subprocess.run(["git", "-C", directory, *arguments], check=True, text=True, capture_output=True).stdout.strip()


class ContractTests(unittest.TestCase):
    def test_activation_auth_and_handoff_shapes(self) -> None:
        record = activation()
        contracts.validate_activation(record)
        contracts.validate_auth("abbudjoe", [])
        contracts.validate_handoff(handoff(), w00a=True)
        mutations = [(record, ("root_turn", "model"), "other"), (record, ("root_turn", "luna_delegation_allowed"), True), (handoff(), ("branch",), "main"), (handoff(), ("objective",), 1), (handoff(), ("acceptance_criteria",), []), (handoff(), ("known_risks",), ["SAFE_TO_MERGE"])]
        mutations += [(handoff(), ("design_conformance", "approved_design_ids"), ["GOV-01"]), (handoff(), ("design_conformance", "secret"), "x"), (handoff(), ("delegated_operations",), [{"role": "luna_runner", "write_performed": False}]), (handoff(), ("billable_actions", "secret"), "x"), (handoff(), ("billable_actions", "performed"), True), (handoff(), ("github_auth_preflight", "token"), "secret")]
        for original, path, value in mutations:
            changed = copy.deepcopy(original)
            target = changed
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            self.assertRaises(ContractError, lambda changed=changed: contracts.validate_activation(changed) if "root_turn" in changed else contracts.validate_handoff(changed, w00a=True))
        for login, names in (("other", []), ("abbudjoe", ["GH_TOKEN"])):
            self.assertRaises(ContractError, contracts.validate_auth, login, names)

    def test_command_fixture_and_phase_isolation(self) -> None:
        fixture = json.loads((ROOT / "governance/fixtures/w00-command-policy.json").read_text())
        payload = {key: RECORDS["live"][1][key] for key in ("name", "target", "enforcement", "bypass_actors", "conditions", "rules")}
        for item in fixture:
            for command in item["commands"]:
                authority = item["phase"] == "w00a-governance" and item["allowed"]
                actual = contracts.assess_command(command, contracts.CommandPhase(item["phase"]), governance_available=authority, governance_payload=payload if authority else None)[0]
                self.assertEqual(actual, item["allowed"], command)
        put = f"gh api --method PUT repos/{contracts.REPOSITORY}/rulesets/{contracts.RULESET} --input .codex-tmp-ruleset-w00a.json"
        self.assertTrue(contracts.assess_command(put, contracts.CommandPhase.W00A_GOVERNANCE, governance_available=True, governance_payload=payload)[0])
        self.assertFalse(contracts.assess_command(put, contracts.CommandPhase.W00A_GOVERNANCE, governance_available=True, governance_payload=payload | {"enforcement": "evaluate"})[0])
        self.assertFalse(contracts.assess_command(put, contracts.CommandPhase.W00A_GOVERNANCE)[0])
        self.assertFalse(contracts.assess_command(put, contracts.CommandPhase.IMPLEMENTATION)[0])

    def test_completion_review_order_and_w00b_records_fail_closed(self) -> None:
        now = datetime.now(timezone.utc)
        expected = (contracts.ACTIVATION, "W00", "turn", IMPL, HEAD, f"https://github.com/{contracts.REPOSITORY}/blob/{HEAD}/h.md", f"https://github.com/{contracts.REPOSITORY}/blob/{HEAD}/h.json", "READY_FOR_CHATGPT_REVIEW", "CHATGPT_REVIEW")
        completion = dict(zip(("activation_id", "task_id", "turn_id", "implementation_head_sha", "live_pr_head_sha", "handoff_markdown", "handoff_json", "status", "next_required_action"), expected, strict=True))
        comments = [marked(contracts.COMPLETION, completion, 1, now)]
        _, completed = contracts.current_completion(comments, expected)
        identity, handoff_url = (PR_URL, contracts.ACTIVATION, BASE, HEAD), expected[6]
        self.assertEqual(contracts.validate_record_order(comments, completed, identity, handoff_url), "HANDOFF")
        review = {"schema_version": "1.0", "review_id": "r1", "pr_url": PR_URL, "activation_id": contracts.ACTIVATION, "base_sha": BASE, "reviewed_head_sha": HEAD, "reviewer": "ChatGPT", "disposition": "CHATGPT_REVIEW_CLEAN", "summary": "clean", "findings": [], "required_next_action": "OWNER_AUTHORIZATION", "review_timestamp": now.isoformat(), "evidence_reviewed": [handoff_url]}
        comments.append(marked(contracts.REVIEW, review, 2, now + timedelta(seconds=1)))
        self.assertEqual(contracts.validate_record_order(comments, completed, identity, handoff_url), "REVIEW")
        comments.append(marked(contracts.INACTIVE_MARKERS[0], {"status": "AUTHORIZED"}, 3, now + timedelta(seconds=2)))
        self.assertRaises(ContractError, contracts.validate_record_order, comments, completed, identity, handoff_url)
        self.assertRaises(ContractError, contracts.current_completion, [*comments[:1], comments[0]], expected)


class RepositoryTests(GitFixture):
    def metrics(self, **changes: object) -> dict[str, Any]:
        values = {"additions": 1, "deletions": 0, "production_loc_added": 1, "production_loc_removed": 0, "test_loc_added": 1, "test_loc_removed": 0, "production_files": sorted(checks.PRODUCTION), "production_added": sorted(checks.PRODUCTION), "production_removed": []}
        values.update({"test_files": ["governance/test_w00_checks.py"], "governance_files": [], "dependencies": ["actions/checkout", "actions/upload-artifact"], "public_contracts": list(checks.PUBLIC_CONTRACTS), "workflows": sorted(checks.WORKFLOWS), "migrations": [], "cli_commands": sorted({*checks.CLI_SPECS, "command-policy"})})
        values.update(changes)
        return values

    def test_stateful_diff_count_and_all_budgets(self) -> None:
        temporary, directory, base = self.repository()
        try:
            Path(directory, "safe").write_text("---old\n")
            self.git(directory, "add", "safe")
            self.git(directory, "commit", "-q", "-m", "header base")
            base = self.git(directory, "rev-parse", "HEAD")
            Path(directory, "safe").write_text("+++payload\n")
            self.git(directory, "add", "safe")
            self.git(directory, "commit", "-q", "-m", "header content")
            self.assertEqual(checks._diff_lines(base, self.git(directory, "rev-parse", "HEAD"), directory), (1, 1))
        finally:
            temporary.cleanup()
        checks.validate_budget(self.metrics(), activation())
        failures = (self.metrics(additions=1501), self.metrics(production_files=[str(i) for i in range(13)]), self.metrics(dependencies=["a", "b", "c"]), self.metrics(public_contracts=["a", "b", "c", "d"]), self.metrics(migrations=["x.sql"]), self.metrics(workflows=["other.yml"]))
        for item in failures:
            self.assertRaises(ContractError, checks.validate_budget, item, activation())

    def test_dependency_schema_migration_and_complexity_discovery(self) -> None:
        with mock.patch.object(checks, "_diff_lines", return_value=(1, 0)), mock.patch.object(checks, "_statuses", side_effect=lambda _b, _h, paths, _r: dict.fromkeys(paths, "A")), mock.patch.object(checks, "_record_types", return_value=set()):
            for path in ("governance/package.json", "governance/Pipfile", "governance/schemas/other.json"):
                self.assertRaises(ContractError, checks.budget, BASE, HEAD, [path])
            self.assertEqual(checks.budget(BASE, HEAD, ["governance/alembic/versions/x.py"])["migrations"], ["governance/alembic/versions/x.py"])
            self.assertEqual(checks.budget(BASE, HEAD, ["governance/run.sh", "governance/runtime-policy.json"])["production_files"], ["governance/run.sh", "governance/runtime-policy.json"])
        source = (ROOT / "governance/w00_checks.py").read_text()
        self.assertEqual(contracts.cli_surface(__import__("ast").parse(source)), {*checks.CLI_SPECS, "command-policy"})
        for invalid in (source.replace('policy = sub.add_parser("command-policy")', 'policy = sub.add_parser("command-policy")\n    sub.add_parser("rogue")'), source.replace("CLI_SPECS.update(", 'CLI_SPECS["rogue"] = ()\nCLI_SPECS.update(')):
            self.assertRaises(ContractError, contracts.cli_surface, __import__("ast").parse(invalid))
        with mock.patch.object(checks, "blob", return_value=b"class PublicContract: pass\n"), self.assertRaises(ContractError):
            checks._record_types(None, HEAD, {"governance/new.py"}, set())
        contracts.validate_python("ok.py", "def ok():\n    return True\n")
        self.assertRaises(ContractError, contracts.validate_python, "large.py", "\n".join(f"x{i}={i}" for i in range(501)))

    def test_base_package_is_fully_bound_and_corruption_fails(self) -> None:
        self.assertGreater(checks.validate_package(None, "3d3ebb706fe6c8779445cbbfd9fea271b86d3646")["checksum_files"], 30)
        with mock.patch.object(checks, "blob", return_value=b"{}"), self.assertRaises(ContractError):
            checks.validate_package(None, HEAD)
        empty = {"artifact_id": "GOV-01", "status": "APPROVED", "file_count": 0, "files": []}
        content = json.dumps(empty, separators=(",", ":")).encode()
        sidecar = f"{__import__('hashlib').sha256(content).hexdigest()}  {checks.PACKAGE}\n".encode()
        original = checks.blob
        forged = lambda repository, revision, path: (sidecar if path == checks.CHECKSUMS else content) if revision == HEAD else original(repository, revision, path)
        with mock.patch.object(checks, "blob", side_effect=forged), self.assertRaises(ContractError):
            checks.validate_package(None, HEAD)


class CandidateTests(GitFixture):
    def test_metadata_bounds_modes_paths_ancestry_and_counts(self) -> None:
        tree, compare = metadata()
        self.assertEqual(checks.validate_metadata(tree, compare, BASE, HEAD)["changed_files"], 1)
        changes = (("tree", "truncated", True), ("tree", "sha", IMPL), ("tree", "tree", [{"path": "../x", "type": "blob", "mode": "100644", "size": 1}]), ("tree", "tree", [{"path": "x", "type": "blob", "mode": "120000", "size": 1}]), ("compare", "total_commits", 2), ("compare", "merge_base_commit", {"sha": IMPL}), ("compare", "commits", [0]), ("compare", "files", [{"filename": "x", "status": "renamed"}]))
        for target, key, value in changes:
            changed_tree, changed_compare = copy.deepcopy(tree), copy.deepcopy(compare)
            (changed_tree if target == "tree" else changed_compare)[key] = value
            self.assertRaises(ContractError, checks.validate_metadata, changed_tree, changed_compare, BASE, HEAD)

    def test_malformed_content_depth_archives_and_controls_fail(self) -> None:
        nested: object = 0
        for _ in range(checks.LIMITS["json_depth"] + 2):
            nested = [nested]
        self.assertRaises(ContractError, checks._json_depth, nested)
        for path in ("", "a//b", "../x", "x.zip", "bad\\path", "bad\x1bpath"):
            self.assertRaises(ContractError, checks.safe_path, path)
        for path, content in (("bad.json", b"{"), ("nan.json", b'{"x":NaN}'), ("overflow.json", b'{"x":1e999}'), ("duplicate.json", b'{"x":1,"x":2}'), ("bad.yml", b"x: ["), ("duplicate.yml", b"x: 1\nx: 2\n"), ("tag-duplicate.yml", b"x: 1\n!!str x: 2\n"), ("multi.yml", b"x: 1\n---\ny: 2\n"), ("bad.py", b"def:"), ("log.md", b"x\rcontrol"), ("text.py", b"\xff")):
            self.assertRaises((ContractError, SyntaxError, UnicodeDecodeError), checks._content, path, content)

    def test_candidate_scripts_workflows_hooks_makefiles_and_dependencies_are_inert(self) -> None:
        temporary, directory, base = self.repository()
        try:
            sentinel = Path(directory, "executed")
            files = {"run.sh": f"#!/bin/sh\ntouch {sentinel}\n", "Makefile": f"all:\n\ttouch {sentinel}\n", "package.json": '{"scripts":{"postinstall":"touch executed"}}', "hooks/pre-commit": f"#!/bin/sh\ntouch {sentinel}\n", ".github/workflows/evil.yml": "name: evil\non: push\njobs: {}\n"}
            for name, content in files.items():
                target = Path(directory, name)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content)
            self.git(directory, "add", ".")
            self.git(directory, "commit", "-q", "-m", "candidate")
            head = self.git(directory, "rev-parse", "HEAD")
            paths = sorted(files)
            entries = []
            for path in paths:
                mode = self.git(directory, "ls-tree", head, "--", path).split()[0]
                entries.append({"path": path, "type": "blob", "mode": mode, "size": len(Path(directory, path).read_bytes())})
            tree_sha = self.git(directory, "rev-parse", f"{head}^{{tree}}")
            tree = {"sha": tree_sha, "truncated": False, "tree": entries}
            compare = {"base_commit": {"sha": base}, "merge_base_commit": {"sha": base}, "total_commits": 1, "commits": [{"sha": head, "commit": {"tree": {"sha": tree_sha}}}], "files": [{"filename": path, "status": "added"} for path in paths]}
            self.assertEqual(checks.inspect_candidate(directory, base, head, tree, compare)["execution"], "NONE")
            self.assertFalse(sentinel.exists())
        finally:
            temporary.cleanup()


class HandoffAndReceiptTests(unittest.TestCase):
    def test_prior_handoffs_are_exact_and_history_or_mutation_fails(self) -> None:
        live = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, text=True, capture_output=True).stdout.strip()
        checks._prior(None, live)
        with mock.patch.object(checks, "git", return_value="c p1 p2"), self.assertRaises(ContractError):
            checks._history(None, BASE, HEAD)
        for line in ("M\thandoffs/W00/x.json", "D\thandoffs/W00/x.json", "R100\thandoffs/W00/a.json\thandoffs/W00/b.json"):
            with mock.patch.object(checks, "git", return_value=line), self.assertRaises(ContractError):
                checks._pair(None, HEAD, IMPL)

    def test_exact_handoff_parent_head_pair_and_complexity_binding(self) -> None:
        record = handoff()
        payload = {key: RECORDS["live"][1][key] for key in ("name", "target", "enforcement", "bypass_actors", "conditions", "rules")}
        record["commands"].append({"phase": "w00a-governance", "command": f"gh api --method PUT repos/{contracts.REPOSITORY}/rulesets/{contracts.RULESET} --input .codex-tmp-ruleset-w00a.json", "exit_status": 0, "result": "applied once", "input": payload})
        record["complexity_receipt"] = complexity(sorted(checks.PRODUCTION))
        record["complexity_receipt"]["dependencies_added"] = ["actions/checkout", "actions/upload-artifact"]
        record["complexity_receipt"]["public_contracts_changed"] = list(checks.PUBLIC_CONTRACTS)
        pair = ("handoffs/W00/W00A-fixture.json", "handoffs/W00/W00A-fixture.md")
        phrases = " ".join((contracts.TITLE, IMPL, record["status"], "Required GitHub Actions checks are defense-in-depth evidence and are not treated as proof of trusted workflow provenance.", "The trusted base-controlled validator becomes operational from main only after W00A is manually merged.", "Owner authorization, receipt consumption, and the merge-only path are not active after W00A and require W00B."))
        metrics = RepositoryTests().metrics()

        def git_side(_repo: str | None, *args: str) -> str:
            if args[:2] == ("diff-tree", "--no-commit-id"):
                return "\n".join(pair)
            if args[:2] == ("rev-parse", f"{IMPL}^"):
                return BASE
            return ""

        with mock.patch.multiple(checks, activation=mock.DEFAULT, _prior=mock.DEFAULT, _history=mock.DEFAULT, _pair=mock.DEFAULT, object_at=mock.DEFAULT, changed_paths=mock.DEFAULT, budget=mock.DEFAULT, git=mock.DEFAULT, blob=mock.DEFAULT) as patched:
            patched["activation"].return_value = activation()
            patched["_history"].return_value = [(HEAD, IMPL)]
            patched["_pair"].side_effect = [pair, None]
            patched["object_at"].return_value = record
            patched["changed_paths"].return_value = sorted(checks.PRODUCTION)
            patched["budget"].return_value = metrics
            patched["git"].side_effect = git_side
            patched["blob"].return_value = phrases.encode()
            self.assertEqual(checks.validate_handoff(BASE, HEAD, contracts.BRANCH, PR_URL)["implementation_head_sha"], IMPL)
            failed_exit = copy.deepcopy(record)
            failed_exit["commands"][0]["exit_status"] = 99
            for invalid in (record | {"commands": []}, record | {"commands": [item for item in record["commands"] if "project-integrity" not in item["command"]]}, record | {"commands": [record["commands"][0] | {"result": ""}, *record["commands"][1:]]}, record | {"evaluations": []}, record | {"evaluations": [record["evaluations"][0] | {"evidence": ""}, *record["evaluations"][1:]]}, failed_exit):
                self.assertRaises(ContractError, checks._handoff_commands, invalid, contracts.BRANCH, PR_URL, True)
            patched["blob"].return_value = (phrases + " SAFE_TO_MERGE").encode()
            self.assertRaises(ContractError, checks._handoff_markdown, None, HEAD, pair[1], IMPL, record["status"], True)
            replay = [(HEAD, IMPL, pair, record), ("d" * 40, HEAD, pair, record)]
            self.assertRaises(ContractError, checks._w00a_mutation, replay)
            forged = copy.deepcopy(record)
            forged["complexity_receipt"]["production_loc_added"] = 999999
            self.assertRaises(ContractError, checks._handoff_receipt, forged, metrics)
            patched["_history"].return_value = [(IMPL, BASE)]
            patched["_pair"].side_effect = [pair]
            self.assertRaises(ContractError, checks.validate_handoff, BASE, HEAD, contracts.BRANCH, PR_URL)

    def test_trusted_receipt_binds_head_base_run_workflow_hash_and_handoff(self) -> None:
        tree, compare = metadata()
        with tempfile.TemporaryDirectory() as directory:
            tree_file, compare_file, output = (Path(directory, "tree.json"), Path(directory, "compare.json"), Path(directory, "receipt.json"))
            tree_file.write_text(json.dumps(tree))
            compare_file.write_text(json.dumps(compare))
            args = argparse.Namespace(repository=contracts.REPOSITORY, event="pull_request_target", base_sha=BASE, trusted_revision=BASE, head_sha=HEAD, pr_number=2, tree_json=str(tree_file), compare_json=str(compare_file), candidate_repository="candidate", branch=contracts.BRANCH, run_id=7, run_attempt=1, output=str(output))
            with mock.patch.multiple(checks, inspect_candidate=mock.DEFAULT, validate_project=mock.DEFAULT, validate_handoff=mock.DEFAULT, content_hash=mock.DEFAULT, blob=mock.DEFAULT) as patched:
                cast(mock.Mock, patched["inspect_candidate"]).return_value = {"execution": "NONE"}
                cast(mock.Mock, patched["validate_project"]).return_value = {"additions": 1}
                cast(mock.Mock, patched["validate_handoff"]).return_value = {"json": "handoffs/W00/x.json"}
                cast(mock.Mock, patched["content_hash"]).return_value = "d" * 64
                cast(mock.Mock, patched["blob"]).return_value = b"handoff"
                receipt = checks.create_receipt(args)["receipt"]
            self.assertEqual(((receipt["inspected_head_sha"], receipt["base_sha"], receipt["workflow_run_id"]), receipt["receipt_hash"], json.loads(output.read_text())), ((HEAD, BASE, 7), checks._receipt_hash(receipt), receipt))


class WorkflowAndLiveTests(unittest.TestCase):
    def live_records(self) -> list[dict[str, Any]]:
        records = cast(list[dict[str, Any]], copy.deepcopy(RECORDS["live"]))
        records[2].update({"id": 20070063288})
        records[2]["protection_rules"][0].update({"id": 62973311})
        records[2]["protection_rules"][0]["reviewers"][0].update({"type": "User"})
        records[2]["protection_rules"][0]["reviewers"][0]["reviewer"].update({"id": 43298060})
        source = __import__("base64").b64encode((ROOT / ".github/CODEOWNERS").read_bytes()).decode()
        codeowners = {"path": ".github/CODEOWNERS", "encoding": "base64", "content": source, "sha": checks.CODEOWNERS_SHA}
        records[4]["total_count"] = len(records[4]["workflows"])
        records[5].update({"number": 1, "html_url": PR_URL})
        records[5]["base"].update({"sha": checks.BASE_SHA, "repo": {"full_name": contracts.REPOSITORY}})
        records[5]["head"].update({"ref": contracts.BRANCH, "repo": {"full_name": contracts.REPOSITORY}})
        runs = [{"id": index, "name": name, "head_sha": HEAD, "status": "completed", "conclusion": "success", "app": {"id": 15368}} for index, name in enumerate(("project-integrity", "turn-handoff-integrity"))]
        return [*records[:3], codeowners, records[3], records[4], records[5], {"total_count": len(runs), "check_runs": runs}]

    def test_live_queries_are_separate_and_capabilities_truthful(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        graph = {"data": {"repository": {"pullRequest": {"reviewThreads": {"nodes": [], "pageInfo": {"hasNextPage": False}}}}}}
        with mock.patch.object(checks, "_api", side_effect=self.live_records()) as api, mock.patch.object(checks, "run", return_value=subprocess.CompletedProcess([], 0, json.dumps(graph), "")):
            result = checks.validate_live(HEAD, now, now, True, True)
        self.assertEqual(api.call_count, 8)
        self.assertEqual((result["owner_authorization"], result["required_checks_role"]), ("INACTIVE_REQUIRES_W00B", "DEFENSE_IN_DEPTH_ONLY"))
        self.assertRaises(ContractError, checks.validate_live, HEAD, "2000-01-01T00:00:00Z", now, True, True)
        for suffix in ("* @mallory", "* @abbudjoe @mallory"):
            record = self.live_records()[3] | {"content": __import__("base64").b64encode(((ROOT / ".github/CODEOWNERS").read_text() + suffix + "\n").encode()).decode()}
            self.assertRaises(ContractError, checks._codeowners, record, {"errors": []})

    def test_trusted_workflow_uses_only_base_code_and_bounded_inert_input(self) -> None:
        source = (ROOT / ".github/workflows/trusted-governance-validator.yml").read_text()
        self.assertTrue(all(item in source for item in ("pull_request_target", "ref: ${{ github.event.pull_request.base.sha }}", "$RUNNER_TEMP/candidate", "GIT_NO_LAZY_FETCH")))
        self.assertLess(source.index("candidate-metadata"), source.index("Fetch exact candidate"))
        self.assertEqual(source.count("actions/checkout@"), 1)
        self.assertNotIn("owner-merge-authorization", source)
        self.assertNotRegex(source, r"\b(?:source|make|npm|pip)\b")
        ordinary = (ROOT / ".github/workflows/governance-integrity.yml").read_text()
        self.assertTrue(all(item not in ordinary for item in ("chatgpt-review-integrity", "owner-merge-record-integrity")) and "exact, nonempty, zero-exit" in (ROOT / "governance/REQUIRED_CHECKS_SPEC.md").read_text())


class AdapterAndCliTests(unittest.TestCase):
    def test_base_activation_and_project_adapter(self) -> None:
        base = "3d3ebb706fe6c8779445cbbfd9fea271b86d3646"
        self.assertEqual(checks.activation(None, base, contracts.BRANCH)["activation_id"], contracts.ACTIVATION)
        record = activation()
        record["activated_paths"] = ["governance/", ".github/workflows/"]
        paths = sorted(checks.PRODUCTION)
        metrics = RepositoryTests().metrics(production_files=paths)

        def source(_repo: str | None, _head: str, path: str) -> bytes:
            return b"def ok():\n    return True\n" if path.endswith(".py") else b"trusted\n"

        hashes = {path: __import__("hashlib").sha256(b"trusted\n").hexdigest() for path in checks.WORKFLOWS}
        with mock.patch.multiple(checks, activation=mock.DEFAULT, changed_paths=mock.DEFAULT, budget=mock.DEFAULT, validate_budget=mock.DEFAULT, validate_package=mock.DEFAULT, blob=mock.DEFAULT, git=mock.DEFAULT) as patched, mock.patch.dict(checks.WORKFLOW_HASHES, hashes):
            cast(mock.Mock, patched["activation"]).return_value = record
            cast(mock.Mock, patched["changed_paths"]).return_value = paths
            cast(mock.Mock, patched["budget"]).return_value = metrics
            cast(mock.Mock, patched["blob"]).side_effect = source
            cast(mock.Mock, patched["git"]).return_value = ""
            self.assertEqual(checks.validate_project(BASE, HEAD, contracts.BRANCH)["changed_paths"], paths)
            cast(mock.Mock, patched["changed_paths"]).return_value = ["outside"]
            self.assertRaises(ContractError, checks.validate_project, BASE, HEAD, contracts.BRANCH)

    def test_completion_adapter_binds_pr_comments_and_prior_records(self) -> None:
        now = datetime.now(timezone.utc)
        current = {"activation_id": contracts.ACTIVATION, "task_id": "W00", "turn_id": "current", "implementation_head_sha": IMPL, "live_pr_head_sha": HEAD, "handoff_markdown": f"https://github.com/{contracts.REPOSITORY}/blob/{HEAD}/handoffs/W00/current.md", "handoff_json": f"https://github.com/{contracts.REPOSITORY}/blob/{HEAD}/handoffs/W00/current.json", "status": "READY_FOR_CHATGPT_REVIEW", "next_required_action": "CHATGPT_REVIEW"}
        comments = []
        for index, (turn, (identifier, live)) in enumerate(checks.PRIOR_COMPLETIONS.items()):
            comments.append(marked(contracts.COMPLETION, {"turn_id": turn, "live_pr_head_sha": live}, identifier, now + timedelta(seconds=index)))
        comments.append(marked(contracts.COMPLETION, current, 9, now + timedelta(seconds=3)))
        pr = {"number": 1, "state": "open", "draft": True, "html_url": PR_URL, "base": {"ref": "main", "sha": BASE, "repo": {"full_name": contracts.REPOSITORY}}, "head": {"ref": contracts.BRANCH, "sha": HEAD, "repo": {"full_name": contracts.REPOSITORY}}}
        with tempfile.TemporaryDirectory() as directory:
            pr_file, comments_file = Path(directory, "pr.json"), Path(directory, "comments.json")
            pr_file.write_text(json.dumps(pr))
            comments_file.write_text(json.dumps([comments]))
            result = {"turn_id": "current", "implementation_head_sha": IMPL, "markdown": "handoffs/W00/current.md", "json": "handoffs/W00/current.json", "status": "READY_FOR_CHATGPT_REVIEW"}
            with mock.patch.object(checks, "validate_handoff", return_value=result):
                self.assertEqual(checks.validate_completion(BASE, HEAD, contracts.BRANCH, str(pr_file), str(comments_file))["state"], "HANDOFF")

    def test_parser_dispatch_and_main_routes(self) -> None:
        common = {"base_sha": BASE, "head_sha": HEAD, "branch": contracts.BRANCH, "pr_url": PR_URL, "revision": HEAD, "tree_json": "tree", "compare_json": "compare", "pr_json": "pr", "comments_json": "comments", "expected_head": HEAD, "review_limit_observed_at": "now", "environment_ui_observed_at": "now", "review_limit_enabled": True, "admin_bypass_disabled": True}
        routes = (("project-integrity", "validate_project"), ("turn-handoff-integrity", "validate_handoff"), ("package-integrity", "validate_package"), ("trusted-governance", "create_receipt"), ("completion-integrity", "validate_completion"), ("live-governance", "validate_live"))
        for check, target in routes:
            with mock.patch.object(checks, target, return_value={}):
                self.assertEqual(checks.dispatch(argparse.Namespace(check=check, **common)), {})
        with mock.patch.object(sys, "argv", ["w00_checks.py", "command-policy", "--phase", "implementation", "git status --short"]):
            self.assertEqual(checks.main(), 0)
        with mock.patch.object(sys, "argv", ["w00_checks.py", "command-policy", "--phase", "implementation", "gh auth token"]):
            self.assertEqual(checks.main(), 1)
