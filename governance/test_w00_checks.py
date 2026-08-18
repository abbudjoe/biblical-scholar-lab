import copy
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
TURN = "W00-SOL-REPAIR03-fixture"
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
    item["combined_evidence_artifact_sha256"] = hashlib.sha256(
        json.dumps(
            {key: item[key] for key in sorted(item) if key != "combined_evidence_artifact_sha256"},
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    return item


def record() -> dict[str, object]:
    project = tuple(
        f"python3 governance/w00_checks.py project-integrity --base-sha {checks.BASE_SHA} "
        f"--head-sha {IMPL} --branch {contracts.BRANCH}".split()
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
        artifacts=[{"artifact_id": "A1", "kind": "review", "reference": "fixture", "sha256": EMPTY}],
    )
    output["github_auth_preflight"].pop("receipt_path", None)
    output["design_conformance"]["approved_design_ids"].append("W00-SPLIT-01")
    review = dict.fromkeys(
        "finding_id source severity affected_path_or_behavior root_cause repair regression_test evidence final_status".split(),
        "fixture",
    )
    review.update(finding_id="P2-01", source="Assembly", severity="P2", final_status="CLOSED")
    output["review_targets"] = [review]
    output["complexity_receipt"].update(
        substantive_lines_total=1, workflow_files=[checks.WORKFLOW], simplicity_conformance="PASS"
    )
    return output


class GovernanceTests(unittest.TestCase):
    def test_record_command_static_and_canonical_contracts(self) -> None:
        contracts.validate_handoff(record(), SCHEMA)
        for field in "changes review_targets commands artifacts".split():
            changed = copy.deepcopy(record())
            changed[field][0]["unknown"] = True
            self.assertRaises(contracts.ContractError, contracts.validate_handoff, changed, SCHEMA)
        changed = copy.deepcopy(record())
        changed["commands"][0]["execution_profile"]["unknown"] = True
        self.assertRaises(contracts.ContractError, contracts.validate_handoff, changed, SCHEMA)
        for target in ("github_auth_preflight", "complexity_receipt"):
            changed = copy.deepcopy(record())
            item = changed[target] if target == "github_auth_preflight" else changed[target]["abstractions"][0]
            item["receipt_path" if target == "github_auth_preflight" else "unknown"] = True
            self.assertRaises(contracts.ContractError, contracts.validate_handoff, changed, SCHEMA)

        fields = "activation_id implementation_head_sha argv finished_at stdout_sha256 exit_code unknown".split()
        values = ("other", "e" * 40, "git status --short", "2026-08-18T11:59:59Z", "bad", 2, True)
        for field, value in zip(fields, values, strict=True):
            changed = copy.deepcopy(record())
            changed["commands"][0][field] = value
            self.assertRaises(contracts.ContractError, contracts.validate_handoff, changed, SCHEMA)
        for field in ("command_evidence_id", "started_at", "combined_evidence_artifact_sha256"):
            changed = copy.deepcopy(record())
            del changed["commands"][0][field]
            self.assertRaises(contracts.ContractError, contracts.validate_handoff, changed, SCHEMA)

        changed = copy.deepcopy(record())
        changed["commands"][1] = copy.deepcopy(changed["commands"][0])
        self.assertRaises(contracts.ContractError, contracts.validate_handoff, changed, SCHEMA)
        changed = copy.deepcopy(record())
        changed["implementation_head_sha"] = "e" * 40
        for item in changed["commands"]:
            item["implementation_head_sha"] = "e" * 40
        self.assertRaises(contracts.ContractError, contracts.validate_handoff, changed, SCHEMA)

        claims = "The PR was merged.|W01 is now underway.|Safe to merge.|Owner authorization is active.|Merge-only path active."
        for prose in claims.split("|"):
            changed = copy.deepcopy(record())
            changed["known_risks"] = [prose]
            self.assertRaises(contracts.ContractError, contracts.validate_handoff, changed, SCHEMA)

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
            "gh api --method DELETE repos/x"
        ).split("|")
        self.assertTrue(all(contracts.command_allowed(command) for command in allowed))
        self.assertTrue(all(not contracts.command_allowed(command) for command in denied))
        self.assertFalse(contracts.assess_argv(["git", "status", "--short", "--porcelain"]))

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
        public = "from package import PublicClass as RenamedClass\nreexport=RenamedClass\n"
        self.assertEqual(contracts.class_surface(public), {"package.PublicClass"})
        self.assertEqual(contracts.class_surface("class _Rogue: pass\nRogue=_Rogue\n"), {"_Rogue"})
        self.assertRaises(contracts.ContractError, contracts.class_surface, "Rogue=type('Rogue',(),{})\n")

        for path in contracts.PYTHON_FILES[:2]:
            contracts.validate_python(path, (ROOT / path).read_text())
        complex_source = "def f(xs):\n    return [x for x in xs if x if x if x if x if x if x if x if x if x]\n"
        self.assertRaises(contracts.ContractError, contracts.validate_python, "complex.py", complex_source)
        self.assertRaises(contracts.ContractError, contracts.validate_python, "long.py", "x = '" + "x" * 121 + "'\n")

    def metrics(self, **changes: object) -> dict[str, object]:
        values = {
            "additions": 1,
            "deletions": 0,
            "production_files": sorted(checks.PRODUCTION),
            "dependencies": ["actions/checkout", "pypi:jsonschema"],
            "public_contracts": ["ContractError", f"schema:{checks.SCHEMA}"],
            "migrations": [],
            "workflows": [checks.WORKFLOW],
            "cli_commands": ["project-integrity", "turn-handoff-integrity"],
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
        self.assertRaises(contracts.ContractError, checks.validate_yaml, duplicate_names, workflow=True)

        head = checks.git("rev-parse", "HEAD")
        actual = checks.validate_project(checks.BASE_SHA, head, contracts.BRANCH)
        self.assertEqual(actual["workflows"], [checks.WORKFLOW])
        checks._prior(head)
        argv = record()["commands"][-2]["argv"][1:]
        argv[5] = head
        with mock.patch.object(sys, "argv", argv):
            self.assertEqual(checks.main(), 0)
        checks.validate_budget(self.metrics())
        failures = (
            {"additions": 1201},
            {"production_files": [str(x) for x in range(13)]},
            {"dependencies": ["a", "b", "c"]},
            {"public_contracts": ["a", "b", "c", "d"]},
            {"migrations": ["x.sql"]},
            {"workflows": ["other"]},
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
        item = record()
        keys = ("billable_actions", "merge_performed", "next_task_started", "status")
        facts = {key: item[key] for key in keys}
        source = f"<!-- BSL_TERMINAL_FACTS_V1 -->\n```json\n{json.dumps(facts)}\n```"
        with mock.patch.object(checks, "blob", return_value=source.encode()):
            self.assertRaises(contracts.ContractError, checks._markdown, HEAD, "x.md", item, IMPL)
