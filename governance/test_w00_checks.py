import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "governance"))

import w00_checks as checks  # noqa: E402
import w00_contracts as contracts  # noqa: E402

IMPL = "c" * 40
HEAD = "d" * 40
TURN = "W00-SOL-REPAIR03-20260818T150000Z"
SCHEMA = contracts.strict_json((ROOT / checks.SCHEMA).read_bytes())
EMPTY = hashlib.sha256(b"").hexdigest()


def evidence(argv: tuple[str, ...], index: int = 0) -> dict[str, object]:
    identifier = f"cmd-{index:02d}"
    envelope = {
        "argv": list(argv),
        "command_evidence_id": identifier,
        "stderr_sha256": EMPTY,
        "stdout_sha256": hashlib.sha256(f"stdout-{identifier}".encode()).hexdigest(),
    }
    keys = "root_turn_id activation_id implementation_head_sha working_directory execution_profile started_at finished_at exit_code result combined_evidence_artifact_sha256".split()
    profile = {"kind": "LOCAL_EXISTING_GH", "actor_login": "abbudjoe", "token_overrides_present": False}
    values = (TURN, contracts.ACTIVATION, IMPL, contracts.ROOT, profile)
    values += ("2026-08-18T12:00:00Z", "2026-08-18T12:00:01Z", 0, "PASS", "")
    item = {**envelope, **dict(zip(keys, values, strict=True))}
    item["combined_evidence_artifact_sha256"] = contracts._command_digest(item)
    return item


def record() -> dict[str, object]:
    project = (
        *contracts.UV_PYTHON,
        *f"python3 governance/w00_checks.py project-integrity --base-sha {checks.BASE_SHA} --head-sha {IMPL} --branch {contracts.BRANCH}".split(),
    )
    auth = ("gh", "auth", "status", "--active", "--hostname", "github.com")
    commands = [evidence(argv, index) for index, argv in enumerate((*contracts.VALIDATION_ARGV, project, auth))]
    prior = ROOT / "handoffs/W00/W00-SOL-REPAIR02-20260818T141853Z.json"
    output = contracts.strict_json(prior.read_bytes())
    output.update(
        turn_id=TURN,
        status="READY_FOR_CHATGPT_REVIEW",
        implementation_head_sha=IMPL,
        compare_url=f"https://github.com/{contracts.REPOSITORY}/compare/{checks.BASE_SHA}...{contracts.BRANCH}",
        changes=[{"change_id": "C1", "kind": "MODIFY", "paths": ["governance/w00_checks.py"], "summary": "repair"}],
        commands=commands,
        objective="Close local-kernel findings.",
        acceptance_criteria=["All activated gates pass."],
        artifacts=[],
        evaluations=[],
        delegated_operations=[],
        known_risks=["Shared GitHub identity remains."],
        decisions_required=["ChatGPT exact-head review."],
    )
    output["github_auth_preflight"].pop("receipt_path", None)
    output["design_conformance"]["approved_design_ids"].append("W00-SPLIT-01")
    fields = (
        "finding_id source severity affected_path_or_behavior root_cause repair regression_test evidence final_status"
    )
    review = dict.fromkeys(fields.split(), "fixture")
    review.update(source="Assembly", severity="P2", final_status="CLOSED")
    output["review_targets"] = [{**review, "finding_id": item} for item in sorted(contracts.REQUIRED_FINDINGS)]
    output["complexity_receipt"].update(
        substantive_lines_total=1,
        workflow_files=[checks.WORKFLOW],
        external_validation_tools=contracts.EXTERNAL_TOOLS,
        abstractions=[{"name": "local-kernel", "reason": "Shared parsing boundary."}],
        simpler_alternatives_considered=["Direct functions."],
        known_duplication_or_debt=["None."],
        waivers=[],
        simplicity_conformance="PASS",
    )
    return output


class GovernanceTests(unittest.TestCase):
    def reject(self, path: tuple[object, ...], value: object = None) -> None:
        item, target = record(), None
        target = item
        for key in path[:-1]:
            target = target[key]
        target.pop(path[-1]) if value is None else target.__setitem__(path[-1], value)
        self.assertRaises(contracts.ContractError, contracts.validate_handoff, item, SCHEMA)

    def test_record_command_static_and_canonical_contracts(self) -> None:
        contracts.validate_handoff(record(), SCHEMA)
        for field in "changes review_targets commands".split():
            self.reject((field, 0, "unknown"), True)
        for field in "evaluations artifacts delegated_operations".split():
            self.reject((field,), [{}])
        self.reject(("commands", 0, "execution_profile", "unknown"), True)
        self.reject(("github_auth_preflight", "receipt_path"), True)
        self.reject(("complexity_receipt", "abstractions", 0, "unknown"), True)

        fields = "activation_id implementation_head_sha argv finished_at stdout_sha256 exit_code unknown".split()
        values = ("other", "e" * 40, "git status --short", "2026-08-18T11:59:59Z", "bad", 2, True)
        for field, value in zip(fields, values, strict=True):
            self.reject(("commands", 0, field), value)
        for field in ("command_evidence_id", "started_at", "combined_evidence_artifact_sha256"):
            self.reject(("commands", 0, field))

        changed = record()
        changed["commands"][1] = changed["commands"][0]
        self.assertRaises(contracts.ContractError, contracts.validate_handoff, changed, SCHEMA)
        changed = record()
        changed["implementation_head_sha"] = "e" * 40
        for item in changed["commands"]:
            item["implementation_head_sha"] = "e" * 40
        self.assertRaises(contracts.ContractError, contracts.validate_handoff, changed, SCHEMA)
        self.reject(("review_targets", -1))
        self.reject(("review_targets", 0, "final_status"), "BLOCKED_WITH_EXACT_REASON")

        claims = "The pull request has already been merged.|W01 started today.|This head can be merged without another review."
        for prose in claims.split("|"):
            self.reject(("known_risks",), [prose])

        allowed = (
            "gh auth status --active --hostname github.com|gh api repos/abbudjoe/biblical-scholar-lab/rulesets/20960975|"
            "git status --short|git add governance/w00_checks.py|git commit -m 'W00A1 Repair03 local governance kernel'|"
            "git push origin codex/w00-repository-governance"
        ).split("|")
        denied = (
            "gh auth token|gh auth status --show-token|gh auth login|gh auth logout|gh auth refresh|gh auth switch|"
            "gh pr ready 1|gh pr merge 1 --admin|gh pr merge 1 --auto|git push origin main|"
            "git push --force origin codex/w00-repository-governance|gh workflow run x|gh secret set X|"
            "env X=1 git status --short|git status --short ; gh auth token|bash -c 'git status --short'|"
            "gh api --method DELETE repos/x|git status --short --porcelain"
        ).split("|")
        self.assertTrue(all(contracts.command_allowed(command) for command in allowed))
        self.assertTrue(all(not contracts.command_allowed(command) for command in denied))

        sources = (
            "import subprocess as sp\nsp.run([])\n",
            "from subprocess import run as execute\nexecute([])\n",
            "from subprocess import run as execute\nalias=execute\nalias([])\n",
        )
        for source in sources:
            self.assertEqual(contracts.policy_calls(source, {"subprocess.run"})[0][0], "subprocess.run")
        dynamic = "import subprocess as sp\nname='run'\nalias=getattr(sp,name)\nalias([])\n"
        self.assertRaises(contracts.ContractError, contracts.policy_calls, dynamic, {"subprocess.run"})

        source = (ROOT / "governance/w00_checks.py").read_text()
        hidden = source.replace(
            'project = sub.add_parser("project-integrity")',
            'project = sub.add_parser("project-integrity")\n    alias = sub.add_parser\n    alias("rogue")',
        )
        self.assertRaises(contracts.ContractError, contracts.cli_surface, hidden)
        self.assertRaises(contracts.ContractError, contracts.cli_surface, source + '\nvars(sub)["add_parser"]("rogue")')
        public = "from package import PublicClass as RenamedClass\nreexport=RenamedClass\n"
        self.assertEqual(contracts.class_surface(public), {"package.PublicClass"})
        self.assertRaises(contracts.ContractError, contracts.class_surface, "Rogue=type('Rogue',(),{})\n")
        hidden_class = 'from package import PublicClass as _Imported\nglobals()["Rogue"]=_Imported\n'
        self.assertRaises(contracts.ContractError, contracts.class_surface, hidden_class)

        for path in contracts.PYTHON_FILES[:2]:
            contracts.validate_python(path, (ROOT / path).read_text())
        complex_source = "def f(xs):\n    return [x for x in xs if x if x if x if x if x if x if x if x if x]\n"
        self.assertRaises(contracts.ContractError, contracts.validate_python, "complex.py", complex_source)
        self.assertRaises(contracts.ContractError, contracts.validate_python, "long.py", "x = '" + "x" * 121 + "'\n")

    def metrics(self, **changes: object) -> dict[str, object]:
        values = {
            "substantive_lines_total": 1,
            "production_files": sorted(checks.PRODUCTION),
            "dependencies_added": ["actions/checkout", "pypi:jsonschema"],
            "public_contracts_changed": ["ContractError", f"schema:{checks.SCHEMA}"],
            "migrations_added": [],
            "workflow_files": [checks.WORKFLOW],
            "cli_commands_added": ["project-integrity", "turn-handoff-integrity"],
        }
        values.update(changes)
        return values

    def test_yaml_budget_and_history_contracts(self) -> None:
        checks.validate_yaml(b"base: &b {x: 1}\none: *b\ntwo: *b\n")
        invalid = [
            item.encode()
            for item in "x: 1\nx: 2|1: a\n01: b|true: a\nTRUE: b|null: a\n~: b|"
            "0xA: a\n10: b|base: &b {x: 1}\nitem: {<<: *b, x: 2}|a: &a {self: *a}|x: [".split("|")
        ]
        invalid.append(("base: &b {x: 1}\n" + "\n".join(f"x{i}: *b" for i in range(33))).encode())
        for source in invalid:
            self.assertRaises(contracts.ContractError, checks.validate_yaml, source)
        duplicate_names = b"jobs:\n  a: {name: Project Integrity}\n  b: {name: ' project   integrity '}\n"
        self.assertRaises(contracts.ContractError, checks.validate_workflow, duplicate_names)

        head = checks.git("rev-parse", "HEAD")
        checks._prior(head)
        checks._required_commands(record(), IMPL)
        argv = ["w00_checks.py", *record()["commands"][-2]["argv"][len(contracts.UV_PYTHON) + 2 :]]
        argv[5] = head
        with mock.patch.object(sys, "argv", argv):
            self.assertEqual(checks.main(), 0)
        failures = (
            {"substantive_lines_total": 1201},
            {"production_files": [str(x) for x in range(13)]},
            {"dependencies_added": ["a", "b", "c"]},
            {"public_contracts_changed": ["a", "b", "c", "d"]},
            {"migrations_added": ["x.sql"]},
            {"workflow_files": ["other"]},
        )
        for change in failures:
            self.assertRaises(contracts.ContractError, checks.validate_budget, self.metrics(**change))
        production, _, _, migrations = checks._classify(
            ["governance/run.sh", "governance/runtime.json", "governance/alembic/x.py"]
        )
        self.assertEqual(production, {"governance/run.sh", "governance/runtime.json", "governance/alembic/x.py"})
        self.assertEqual(migrations, {"governance/alembic/x.py"})

        with mock.patch.object(checks, "git", return_value="c p1 p2"):
            self.assertRaises(contracts.ContractError, checks._history, checks.BASE_SHA, HEAD)
        for line in ("M\thandoffs/W00/x.json", "D\thandoffs/W00/x.json", "R100\ta\tb"):
            with mock.patch.object(checks, "git", return_value=line):
                self.assertRaises(contracts.ContractError, checks._pair, HEAD, IMPL)
        pair = tuple(f"handoffs/W00/W00-SOL-REPAIR03-20260818T150000Z.{suffix}" for suffix in ("json", "md"))
        with mock.patch.object(checks, "_pair", return_value=None):
            with mock.patch.object(checks, "git", side_effect=["b" * 40, "\n".join(pair)]):
                self.assertEqual(checks._final_commit(HEAD, [(HEAD, IMPL, pair)])[1], IMPL)
            with mock.patch.object(checks, "git", side_effect=["b" * 40, "\n".join((*pair, "governance/x.py"))]):
                self.assertRaises(contracts.ContractError, checks._final_commit, HEAD, [(HEAD, IMPL, pair)])
        stale = tuple(path.replace("150000Z", "140000Z") for path in pair)
        self.assertRaises(
            contracts.ContractError, checks._final_commit, HEAD, [(IMPL, HEAD, pair), (HEAD, IMPL, stale)]
        )
        item = record()
        keys = ("billable_actions", "merge_performed", "next_task_started", "status")
        facts = {key: item[key] for key in keys}
        source = f"<!-- BSL_TERMINAL_FACTS_V1 -->\n```json\n{json.dumps(facts)}\n```"
        with mock.patch.object(checks, "blob", return_value=source.encode()):
            self.assertRaises(contracts.ContractError, checks._markdown, HEAD, "x.md", item, IMPL)
