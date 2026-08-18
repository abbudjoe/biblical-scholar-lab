import hashlib
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "governance"))
import w00_checks as checks  # noqa: E402
import w00_contracts as contracts  # noqa: E402

IMPL, HEAD, EMPTY = "c" * 40, "d" * 40, hashlib.sha256(b"").hexdigest()
TURN = "W00-SOL-REPAIR03-20260818T150000Z"
SCHEMA = contracts.strict_json((ROOT / checks.SCHEMA).read_bytes())


def evidence(argv: tuple[str, ...], index: int) -> dict[str, object]:
    profile = {"kind": "LOCAL_EXISTING_GH", "actor_login": "abbudjoe", "token_overrides_present": False}
    item = dict(argv=list(argv), command_evidence_id=f"cmd-{index:02d}", stdout_sha256=EMPTY, stderr_sha256=EMPTY)
    item.update(root_turn_id=TURN, activation_id=contracts.ACTIVATION, implementation_head_sha=IMPL)
    item.update(working_directory=contracts.ROOT, execution_profile=profile, started_at="2026-08-18T12:00:00Z")
    item.update(finished_at="2026-08-18T12:00:01Z", exit_code=0, result="PASS")
    item["combined_evidence_artifact_sha256"] = contracts._command_digest(item)
    return item


def finding(identifier: str) -> dict[str, str]:
    fields = "finding_id source severity affected_path_or_behavior root_cause repair regression_test evidence final_status".split()
    item = dict.fromkeys(fields, "FIXTURE")
    severity, status = contracts.finding_state(identifier)
    item.update(finding_id=identifier, source="ASSEMBLY", severity=severity, final_status=status)
    return item


def record() -> dict[str, object]:
    output = contracts.strict_json((ROOT / "handoffs/W00/W00-SOL-REPAIR02-20260818T141853Z.json").read_bytes())
    output.update(turn_id=TURN, status="READY_FOR_CHATGPT_REVIEW", implementation_head_sha=IMPL)
    output["compare_url"] = f"https://github.com/{contracts.REPOSITORY}/compare/{checks.BASE_SHA}...{contracts.BRANCH}"
    output.update(objective="W00A1_LOCAL_KERNEL", acceptance_criteria=["ALL_ACTIVATED_GATES_PASS"])
    output["changes"] = [dict(change_id="C1", kind="MODIFY", paths=["governance/w00_checks.py"], summary="REPAIR")]
    output["commands"] = [evidence(("git", "status", "--short"), 0)]
    output["artifacts"] = [dict(artifact_id="v", kind="VALIDATION_REPORT", reference="inline:v", sha256=EMPTY)]
    output["evaluations"] = [dict(name="GATES", status="PASS", evidence="v")]
    delegation = dict(role="READ_ONLY_REVIEWER", agent="J", scope="H", write_performed=False, result="CLEAN")
    output["delegated_operations"] = [delegation]
    output["known_risks"] = output["decisions_required"] = []
    output["design_conformance"]["approved_design_ids"].append("W00-SPLIT-01")
    output["review_targets"] = [finding(item) for item in sorted(contracts.REQUIRED_FINDINGS)]
    receipt = output["complexity_receipt"]
    receipt.update(substantive_lines_total=1, workflow_files=[checks.WORKFLOW])
    receipt["external_validation_tools"] = contracts.EXTERNAL_TOOLS
    receipt.update(abstractions=[{"name": "AST", "reason": "BOUNDED"}], simpler_alternatives_considered=[])
    receipt.update(known_duplication_or_debt=[], waivers=[], simplicity_conformance="PASS")
    return output


class GovernanceTests(unittest.TestCase):
    def reject(self, path: tuple[object, ...], value: object = None, status: str | None = None) -> None:
        item = target = record()
        item["status"] = status or item["status"]
        for key in path[:-1]:
            target = target[key]
        target.pop(path[-1]) if value is None else target.__setitem__(path[-1], value)
        self.assertRaises(ValueError, contracts.validate_handoff, item, SCHEMA)

    def blocked(self, source: str) -> bool:
        try:
            return bool(contracts.policy_calls(source, {"subprocess.run"}))
        except ValueError:
            return True

    def test_record_and_command_contracts(self) -> None:
        contracts.validate_handoff(record(), SCHEMA)
        for field in "changes review_targets commands evaluations artifacts delegated_operations".split():
            self.reject((field, 0, "unknown"), True)
        self.reject(("commands", 0, "stdout_sha256"), "bad")
        self.reject(("review_targets", 0, "severity"), "P3", "SPLIT_REQUIRED")
        self.reject(("known_risks",), ["The pull request landed successfully."])
        future = record()
        future["commands"][0].update(finished_at="2027-08-18T12:00:01Z")
        future["commands"][0]["combined_evidence_artifact_sha256"] = contracts._command_digest(future["commands"][0])
        self.assertRaises(ValueError, contracts.validate_handoff, future, SCHEMA)
        allowed = "gh auth status --active --hostname github.com|gh api user|gh pr checks 1 --repo abbudjoe/biblical-scholar-lab|git status --short|git add governance/w00_checks.py|git push origin codex/w00-repository-governance|git rev-parse HEAD|python3 governance/w00_checks.py project-integrity --base-sha 3d3ebb706fe6c8779445cbbfd9fea271b86d3646 --head-sha HEAD --branch codex/w00-repository-governance"
        denied = "|gh auth token|gh auth status --show-token|gh auth login|gh auth logout|gh auth refresh|gh auth switch|gh pr ready 1|gh pr merge 1 --admin|gh pr merge 1 --auto|gh api --method DELETE repos/x|gh api --method PUT repos/x|gh workflow run x|gh secret set X|gh api repos/x/collaborators/y -X PUT|gh api repos/x/environments/y/reviewers -X POST|git push origin main|git push --force origin codex/w00-repository-governance|git add other|git commit -m wrong|env X=1 git status --short|bash -c git status --short|git status --short ; gh auth token|git status --short > x|python3 governance/w00_checks.py project-integrity --base-sha bad --head-sha HEAD --branch bad"
        self.assertTrue(all(contracts.assess_argv(item.split()) for item in allowed.split("|")))
        self.assertTrue(all(not contracts.assess_argv(item.split()) for item in denied.split("|")))

    def test_alias_discovery(self) -> None:
        governed = (
            "import subprocess as sp\nsp.run([])|from subprocess import run as f\na=f\na([])|import subprocess as sp\n(x:=sp)\nx.run([])|"
            "import subprocess as sp\nf=sp.run\nif flag:f=print\nf([])|import subprocess as sp\nf=sp.run\ntry:f=print\nexcept:pass\nf([])|from subprocess import *\nrun([])|"
            "import subprocess as sp\ndef f(g=sp.run):g([])|import subprocess as sp\ndef f(g):g([])\nf(sp.run)|"
            "import subprocess as sp,operator\n[operator.attrgetter][0]('run')(sp)([])|import subprocess as sp,operator\n[operator.methodcaller][0]('run',[])(sp)|"
            "import subprocess as sp\ng=sp.__dict__.__getitem__\ng(input())([])|import subprocess as sp\nsp.__dict__.get(input())([])|import subprocess as sp\n[type][0](sp).run([])|"
            "import subprocess as sp\nobject.__getattribute__(sp,'run')([])|import subprocess as sp,inspect\ninspect.getattr_static(sp,'run')([])|import subprocess as sp\nclass Box: execute=sp.run\nBox.execute([])|"
            "[__import__][0]('subprocess').run([])|import builtins\ngetattr(builtins,input())('subprocess').run([])|"
            "import importlib\nimportlib.__dict__[input()]('subprocess').run([])|import builtins,operator\noperator.attrgetter(input())(builtins)('subprocess').run([])|import subprocess as sp\nif sp.run([]):pass|import subprocess as sp\ndef f(x=sp.run([])):pass|import subprocess as sp\nclass C(sp.run([])):pass|import subprocess as sp\nmatch sp.run([]):\n case _:pass|import subprocess as sp\nf=sp.run\nfor x in []:f=print\nf([])|import subprocess as sp\nf=sp.run\nwhile flag:f=print\nf([])"
        ).split("|")
        forms = "[sp][0]|(sp,)[0]|{'m':sp}['m']|sp if flag else other|sp or other|(x:=sp)".split("|")
        governed += tuple(f"import subprocess as sp\ngetattr(({form}),input())([])" for form in forms)
        self.assertTrue(all(self.blocked(item) for item in governed))
        cases = "[print][0]()|(print if x else len)()|(print or len)()|{'run':print}['run']()|class Helper:\n def run(self): ...\nHelper.run(None)|import subprocess as sp\n[sp.Popen][0]([])|import subprocess as sp\ngetattr(sp,'other')([])|import logging\n[getattr][0](logging,'info')('x')|import logging\ngetattr(logging,input())('x')"
        self.assertTrue(all(not contracts.policy_calls(item, {"subprocess.run"}) for item in cases.split("|")))
        source = (ROOT / "governance/w00_checks.py").read_text()
        cases = "(p:=sub.add_parser)\np('rogue')|p=sub.add_parser\nif flag:p=print\np('rogue')|[p]=[sub.add_parser]\np('rogue')|def f(g=sub.add_parser):g('rogue')|def f(g):g('rogue')\nf(sub.add_parser)|getattr(sub,input())('rogue')|class Box:p=sub.add_parser\nBox.p('rogue')"
        for call in cases.split("|"):
            self.assertRaises(ValueError, contracts.cli_surface, source + "\n" + call)
        source += "\nimport other\nother.add_parser('x')\nclass H:\n def add_parser(self):...\nH.add_parser(None)"
        contracts.cli_surface(source)
        self.assertEqual(contracts.class_surface("from package import C as Renamed"), {"package.C"})
        self.assertRaises(ValueError, contracts.class_surface, "from package import C as _C\nx=[_C][0]\nRogue=x")
        for body in ("pass", "..."):
            self.assertRaises(ValueError, contracts.validate_python, "stub.py", f"def f():\n {body}")

    def test_repository_and_history_contracts(self) -> None:
        checks.validate_yaml(b"base: &b {x: 1}\none: *b\ntwo: *b\n")
        cases = "x: 1\nx: 2|1: a\n01: b|true: a\nTRUE: b|null: a\n~: b|0xA: a\n10: b|base: &b {x: 1}\nitem: {<<: *b, x: 2}|a: &a {self: *a}|x: ["
        for source in cases.split("|"):
            self.assertRaises(ValueError, checks.validate_yaml, source.encode())
        checks.validate_project(checks.BASE_SHA, head := checks.git("rev-parse", "HEAD"), contracts.BRANCH)
        handoff_args = checks.BASE_SHA, head, contracts.BRANCH, contracts.PR_URL
        self.assertRaises(ValueError, checks.validate_handoff, *handoff_args)
        self.assertRaises(ValueError, checks._required_commands, record(), IMPL)
        with mock.patch.object(checks, "blob", return_value=b"def adapter():\n import requests\n"):
            self.assertEqual(checks._dependencies(HEAD, ["governance/adapter.py"], set()), {"pypi:requests"})
        baseline = {**record()["complexity_receipt"], "production_files": sorted(checks.PRODUCTION)}
        self.assertRaises(ValueError, checks.validate_budget, {**baseline, "substantive_lines_total": 1201})
        manifest = {**checks.object_at(head, checks.PACKAGE), "github_execution_identity": "MALLORY"}
        base_manifest = checks.object_at(checks.BASE_SHA, checks.PACKAGE)
        self.assertRaises(ValueError, checks._package_metadata, manifest, base_manifest, set())
        pair = tuple(f"handoffs/W00/W00-SOL-REPAIR03-20260818T150000Z.{suffix}" for suffix in ("json", "md"))
        with mock.patch.object(checks, "_pair", return_value=None):
            with mock.patch.object(checks, "git", side_effect=["b" * 40, "\n".join(pair), "2026-08-18T15:01:00+00:00"]):
                self.assertEqual(checks._final_commit(HEAD, [(HEAD, IMPL, pair)])[1], IMPL)
            with mock.patch.object(checks, "git", side_effect=["b" * 40, "\n".join(pair), "2026-08-18T14:00:00+00:00"]):
                self.assertRaises(ValueError, checks._final_commit, HEAD, [(HEAD, IMPL, pair)])
        item, source = record(), checks._render_markdown(record(), IMPL)
        with mock.patch.object(checks, "blob", return_value=source.encode()):
            checks._markdown(HEAD, "x.md", item, IMPL)
        with mock.patch.object(checks, "blob", return_value=(source + "The PR is merged.").encode()):
            self.assertRaises(ValueError, checks._markdown, HEAD, "x.md", item, IMPL)
