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

IMPL, HEAD = "c" * 40, "d" * 40
TURN = "W00-SOL-REPAIR03-20260818T150000Z"
SCHEMA = contracts.strict_json((ROOT / checks.SCHEMA).read_bytes())
EMPTY = hashlib.sha256(b"").hexdigest()


def evidence(argv: tuple[str, ...], index: int = 0) -> dict[str, object]:
    envelope = {
        "argv": list(argv),
        "command_evidence_id": f"cmd-{index:02d}",
        "stderr_sha256": EMPTY,
        "stdout_sha256": hashlib.sha256(f"stdout-cmd-{index:02d}".encode()).hexdigest(),
    }
    keys = "root_turn_id activation_id implementation_head_sha working_directory execution_profile started_at finished_at exit_code result combined_evidence_artifact_sha256".split()
    profile = {"kind": "LOCAL_EXISTING_GH", "actor_login": "abbudjoe", "token_overrides_present": False}
    values = (TURN, contracts.ACTIVATION, IMPL, contracts.ROOT, profile)
    values += ("2026-08-18T12:00:00Z", "2026-08-18T12:00:01Z", 0, "PASS", "")
    item = {**envelope, **dict(zip(keys, values, strict=True))}
    item["combined_evidence_artifact_sha256"] = contracts._command_digest(item)
    return item


def finding(identifier: str) -> dict[str, str]:
    item = dict.fromkeys(
        "finding_id source severity affected_path_or_behavior root_cause repair regression_test evidence final_status".split(),
        "fixture",
    )
    severity, status = contracts.finding_state(identifier)
    item.update(finding_id=identifier, source="Assembly", severity=severity, final_status=status)
    return item


def record() -> dict[str, object]:
    project = (
        *contracts.UV_PYTHON,
        *f"python3 governance/w00_checks.py project-integrity --base-sha {checks.BASE_SHA} --head-sha {IMPL} --branch {contracts.BRANCH}".split(),
    )
    auth = ("gh", "auth", "status", "--active", "--hostname", "github.com")
    output = contracts.strict_json((ROOT / "handoffs/W00/W00-SOL-REPAIR02-20260818T141853Z.json").read_bytes())
    delegation = dict(role="READ_ONLY_REVIEWER", agent="r", scope="head", write_performed=False, result="CLEAN")
    output["turn_id"], output["status"], output["implementation_head_sha"] = TURN, "READY_FOR_CHATGPT_REVIEW", IMPL
    output.update(
        compare_url=f"https://github.com/{contracts.REPOSITORY}/compare/{checks.BASE_SHA}...{contracts.BRANCH}",
        changes=[{"change_id": "C1", "kind": "MODIFY", "paths": ["governance/w00_checks.py"], "summary": "repair"}],
        commands=[evidence(argv, index) for index, argv in enumerate((*contracts.VALIDATION_ARGV, project, auth))],
        objective="Close local-kernel findings.",
        acceptance_criteria=["All activated gates pass."],
        artifacts=[dict(artifact_id="v", kind="VALIDATION_REPORT", reference="inline:v", sha256=EMPTY)],
        evaluations=[{"name": "gates", "status": "PASS", "evidence": "v"}],
        delegated_operations=[delegation],
    )
    output["known_risks"] = output["decisions_required"] = []
    output["design_conformance"]["approved_design_ids"].append("W00-SPLIT-01")
    output["review_targets"] = [finding(item) for item in sorted(contracts.REQUIRED_FINDINGS)]
    receipt = output["complexity_receipt"]
    receipt["substantive_lines_total"] = 1
    receipt["dependencies_added"] = sorted(checks.DEPENDENCIES)
    receipt["public_contracts_changed"] = [f"schema:{checks.SCHEMA}"]
    receipt["cli_commands_added"] = ["project-integrity", "turn-handoff-integrity"]
    receipt["workflow_files"] = [checks.WORKFLOW]
    receipt["external_validation_tools"] = contracts.EXTERNAL_TOOLS
    receipt["simplicity_conformance"] = "PASS"
    return output


class GovernanceTests(unittest.TestCase):
    def reject(self, path: tuple[object, ...], value: object = None, status: str | None = None) -> None:
        item, target = record(), None
        item["status"] = status or item["status"]
        target = item
        for key in path[:-1]:
            target = target[key]
        target.pop(path[-1]) if value is None else target.__setitem__(path[-1], value)
        self.assertRaises(ValueError, contracts.validate_handoff, item, SCHEMA)

    def test_record_command_static_and_canonical_contracts(self) -> None:
        contracts.validate_handoff(record(), SCHEMA)
        for field in "changes review_targets commands evaluations artifacts delegated_operations".split():
            self.reject((field, 0, "unknown"), True)
        self.reject(("commands", 0, "execution_profile", "unknown"), True)
        self.reject(("billable_actions", "campaign_ids"))
        self.reject(("complexity_receipt", "abstractions", 0, "unknown"), True)

        fields = "activation_id implementation_head_sha argv finished_at stdout_sha256 exit_code unknown".split()
        values = ("other", "e" * 40, "git status --short", "2026-08-18T11:59:59Z", "bad", 2, True)
        for field, value in zip(fields, values, strict=True):
            self.reject(("commands", 0, field), value)
        self.reject(("commands", 1), record()["commands"][0])
        self.reject(("review_targets", -1), status="SPLIT_REQUIRED")
        self.reject(("review_targets", 0, "severity"), "P3", status="SPLIT_REQUIRED")
        self.reject(("review_targets", 0, "final_status"), "SUPERSEDED_BY_APPROVED_SPLIT")
        self.reject(("status",), "NO_CHANGE")
        self.reject(("status",), "BLOCKED_MISSING_EVIDENCE")
        self.reject(("evaluations", 0, "status"), "FAIL")
        self.reject(("delegated_operations", 0, "result"), "REPAIR_REQUIRED")
        self.reject(("evaluations", 0, "evidence"), "absent")

        for path, prose in (
            (("evaluations", 0, "name"), "W01 started today."),
            (("artifacts", 0, "reference"), "This head can be merged without another review."),
            (("delegated_operations", 0, "scope"), "Safe to merge without review."),
        ):
            self.reject(path, prose)

        allowed = (
            "gh auth status --active --hostname github.com|gh api repos/abbudjoe/biblical-scholar-lab/rulesets/20960975|"
            "git status --short|git add governance/w00_checks.py|"
            "git push origin codex/w00-repository-governance"
        ).split("|")
        denied = (
            "gh auth token|gh auth status --show-token|gh auth login|gh auth logout|gh auth refresh|gh auth switch|"
            "gh pr ready 1|gh pr merge 1 --admin|gh pr merge 1 --auto|git push origin main|"
            "git push --force origin codex/w00-repository-governance|gh workflow run x|gh secret set X|"
            "env X=1 git status --short|git status --short ; gh auth token|bash -c git status --short|"
            "gh api --method DELETE repos/x|git status --short --porcelain|git status --short > x"
        ).split("|")
        self.assertTrue(all(contracts.assess_argv(command.split()) for command in allowed))
        self.assertTrue(all(not contracts.assess_argv(command.split()) for command in denied))

        sources = (
            "import subprocess as sp\nsp.run([])\n|from subprocess import run as execute\nexecute([])\n|"
            "from subprocess import run as execute\nalias=execute\nalias([])\n"
        ).split("|")
        for source in sources:
            self.assertEqual(contracts.policy_calls(source, {"subprocess.run"})[0][0], "subprocess.run")
        dynamic = "import subprocess as sp\nname='run'\nalias=getattr(sp,name)\nalias([])\n"
        self.assertRaises(ValueError, contracts.policy_calls, dynamic, {"subprocess.run"})

        source = (ROOT / "governance/w00_checks.py").read_text()
        hidden = ("(sub.add_parser if x else print)()|(sub.add_parser or print)()|(x := sub.add_parser)()").split("|")
        for call in hidden:
            self.assertRaises(ValueError, contracts.cli_surface, source + "\n" + call)
        public = "from package import PublicClass as RenamedClass\nreexport=RenamedClass\n"
        self.assertEqual(contracts.class_surface(public), {"package.PublicClass"})
        hidden_classes = (
            "from package import PublicClass as _Imported\nhidden=[_Imported][0]\nRogue=hidden\n|"
            'import package\nhidden=getattr(package,"PublicClass")\nRogue=hidden\n'
        ).split("|")
        for hidden_class in hidden_classes:
            self.assertRaises(ValueError, contracts.class_surface, hidden_class)
        unrelated = "import logging as log\nalias=log.info\nalias('ok')\n"
        self.assertEqual(contracts.policy_calls(unrelated, {"*.add_parser"}), [])

        for body in ("pass", "..."):
            self.assertRaises(ValueError, contracts.validate_python, "stub.py", f"def f():\n    {body}\n")

    def metrics(self, **changes: object) -> dict[str, object]:
        return {**record()["complexity_receipt"], "production_files": sorted(checks.PRODUCTION), **changes}

    def test_yaml_budget_and_history_contracts(self) -> None:
        checks.validate_yaml(b"base: &b {x: 1}\none: *b\ntwo: *b\n")
        invalid = [
            item.encode()
            for item in "x: 1\nx: 2|1: a\n01: b|true: a\nTRUE: b|null: a\n~: b|"
            "0xA: a\n10: b|base: &b {x: 1}\nitem: {<<: *b, x: 2}|a: &a {self: *a}|x: [".split("|")
        ]
        invalid.append(("base: &b {x: 1}\n" + "\n".join(f"x{i}: *b" for i in range(33))).encode())
        for source in invalid:
            self.assertRaises(ValueError, checks.validate_yaml, source)
        duplicate_names = b"jobs:\n  a: {name: Project Integrity}\n  b: {name: ' project   integrity '}\n"
        self.assertRaises(ValueError, checks.validate_workflow, duplicate_names)

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
            self.assertRaises(ValueError, checks.validate_budget, self.metrics(**change))
        production, _, _, migrations = checks._classify(
            ["governance/run.sh", "governance/runtime.json", "governance/alembic/x.py"]
        )
        self.assertEqual(production, {"governance/run.sh", "governance/runtime.json", "governance/alembic/x.py"})
        self.assertEqual(migrations, {"governance/alembic/x.py"})

        for line in ("M\thandoffs/W00/x.json", "D\thandoffs/W00/x.json", "R100\ta\tb"):
            with mock.patch.object(checks, "git", return_value=line):
                self.assertRaises(ValueError, checks._pair, HEAD, IMPL)
        pair = tuple(f"handoffs/W00/W00-SOL-REPAIR03-20260818T150000Z.{suffix}" for suffix in ("json", "md"))
        with mock.patch.object(checks, "_pair", return_value=None):
            with mock.patch.object(checks, "git", side_effect=["b" * 40, "\n".join(pair)]):
                self.assertEqual(checks._final_commit(HEAD, [(HEAD, IMPL, pair)])[1], IMPL)
            with mock.patch.object(checks, "git", side_effect=["b" * 40, "\n".join((*pair, "governance/x.py"))]):
                self.assertRaises(ValueError, checks._final_commit, HEAD, [(HEAD, IMPL, pair)])
        stale = tuple(path.replace("150000Z", "140000Z") for path in pair)
        self.assertRaises(ValueError, checks._final_commit, HEAD, [(IMPL, HEAD, pair), (HEAD, IMPL, stale)])
        item = record()
        keys = ("billable_actions", "merge_performed", "next_task_started", "status")
        facts = {key: item[key] for key in keys}
        source = f"<!-- BSL_TERMINAL_FACTS_V1 -->\n```json\n{json.dumps(facts)}\n```"
        with mock.patch.object(checks, "blob", return_value=source.encode()):
            self.assertRaises(ValueError, checks._markdown, HEAD, "x.md", item, IMPL)
