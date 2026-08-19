import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import chdir
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "governance"))
import w00_checks as checks  # noqa: E402

SHA, BRANCH, PR = "a" * 40, "codex/w00-repair", "https://github.com/abbudjoe/biblical-scholar-lab/pull/7"
TURN, NOW = "W00-SOL-REPAIR05-20260819T120000Z", "2026-08-19T12:00:00Z"
BEFORE, AFTER, OFFSET = "2026-08-19T11:59:59Z", "2026-08-19T12:00:01Z", "2026-08-19T12:00:00+00:00"
AT, SCHEMA_BYTES = checks.utc(NOW), (ROOT / checks.SCHEMA).read_bytes()
SCHEMA = checks.strict_json(SCHEMA_BYTES)
OPEN = {"finding_id": "OPEN", "severity": "P2", "status": "UNRESOLVED", "evidence": "X", "rationale": "X"}


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def example(node):
    if "$ref" in node:
        return example(SCHEMA["$defs"][str(node["$ref"]).rsplit("/", 1)[-1]])
    if "const" in node:
        return copy.deepcopy(node["const"])
    if "enum" in node:
        return node["enum"][0]
    kind = node.get("type")
    if kind == "object":
        keys = node.get("required", node.get("propertyNames", {}).get("enum", []))
        return {key: example(node.get("properties", {}).get(key, node["additionalProperties"])) for key in keys}
    if kind == "array":
        return [example(node["items"]) for _ in range(int(node.get("minItems", 0)))]
    if kind == "integer":
        return node.get("minimum", 0)
    pattern = str(node.get("pattern", ""))
    choices = (("{40}", SHA), ("{64}", "0" * 64), ("github", PR), ("codex/", BRANCH), ("{4}-", NOW))
    return next((value for marker, value in choices if marker in pattern), "X")


def store(files, path, content):
    files[path] = content
    return {"path": path, "sha256": checks.digest(content)}


def signed_receipt(files, path, item):
    return store(files, path, encoded({key: value for key, value in item.items() if key != "receipt"}))


def entry(turn, files):
    row = {"turn_id": turn}
    for name, suffix in (("json", "json"), ("markdown", "md")):
        path = f"handoffs/W00/{turn}.{suffix}"
        reference = store(files, path, files.get(path, b"{}\n"))
        row[f"{name}_path"], row[f"{name}_sha256"] = reference.values()
    return row


def review_files(record, binary):
    items, review = record["artifacts"], record["independent_review"]
    contents = {"COMPLEXITY": encoded(record["complexity_receipt"]), "BINARY_DIFF": binary}
    contents |= {"REVIEW_INSTRUCTION": checks.render_review_instruction(record).encode()}
    for key, content in contents.items():
        items[key]["sha256"] = checks.digest(content)
    contents["REVIEW_REPORT_RECORD"] = (json.dumps(review, indent=2, sort_keys=True) + "\n").encode()
    items["REVIEW_REPORT_RECORD"]["sha256"] = checks.digest(contents["REVIEW_REPORT_RECORD"])
    return contents


def fixture(base=SHA, implementation="b" * 40, start=SHA, binary=b"diff", tree="d" * 40):
    record, files = example(SCHEMA), {}
    record.update(
        root_turn_id=TURN, base_sha=base, starting_live_sha=start, implementation_head_sha=implementation, branch=BRANCH
    )
    record["integrity"]["schema_sha256"] = checks.digest(SCHEMA_BYTES)
    commands = record["commands"] = []
    for index, argv in enumerate(checks.command_suite(base, implementation, BRANCH), 1):
        item = example(SCHEMA["$defs"]["command"])
        stem = f"{checks.EVIDENCE_ROOT}/{TURN}/{index:02d}"
        item.update(command_index=index, evidence_id=f"CMD_{index:02d}", root_turn_id=TURN, argv=list(argv))
        item["implementation_head_sha"] = implementation
        for field, content in (("stdout", b"90\n" if index == 2 else b""), ("stderr", b"")):
            item[field] = store(files, f"{stem}.{field}", content)
        item["receipt"] = signed_receipt(files, f"{stem}.receipt.json", item)
        commands.append(item)
    root = f"{checks.EVIDENCE_ROOT}/{TURN}"
    auth = record["github_auth"]
    auth["receipt"] = signed_receipt(files, f"{root}/github.auth.json", auth)
    items = record["artifacts"] = {
        key: {"path": f"{root}/{name}", "sha256": "0" * 64} for key, name in checks.ARTIFACTS
    }
    review = record["independent_review"]
    review.update(review_run_id="REPAIR05_REVIEW", reviewer_revision_or_exact_model_identity="GPT_5_6_SOL")
    review.update(base_sha=base, implementation_head_sha=implementation, implementation_tree_sha=tree)
    review["diff_sha256"] = checks.digest(binary)
    review["review_instruction"] = items["REVIEW_INSTRUCTION"]
    inspected = checks.ACTIVE | checks.IMMUTABLE
    inspected |= {item[field]["path"] for item in commands for field in ("receipt", "stdout", "stderr")}
    inspected |= {auth["receipt"]["path"], items["COMPLEXITY"]["path"], items["BINARY_DIFF"]["path"]}
    review["artifacts_inspected"] = sorted(inspected)
    files.update((items[key]["path"], content) for key, content in review_files(record, binary).items())
    return record, files


def git_capture(repo, *arguments, input=None, env=None):
    command = ["git", "-C", repo, *arguments]
    return subprocess.run(command, input=input, text=True, check=True, capture_output=True, env=env).stdout.strip()


def commit(repo, files):
    for name, content in files.items():
        path = Path(repo, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    git_capture(repo, "add", ".")
    environment = dict(os.environ, GIT_AUTHOR_DATE=NOW, GIT_COMMITTER_DATE=NOW)
    git_capture(repo, "-c", "user.name=T", "-c", "user.email=t@e", "commit", "-qm", "fixture", env=environment)
    return git_capture(repo, "rev-parse", "HEAD")


class Repair05Tests(unittest.TestCase):
    def test_schema_registry_and_primitives(self):
        for path in checks.IMMUTABLE:
            self.assertEqual((ROOT / path).read_bytes(), checks.blob("origin/main", path))
        record = example(SCHEMA)
        checks.jsonschema.Draft202012Validator(SCHEMA).validate(record)
        mutations = (lambda item: item.update(extra=True), lambda item: item["commands"][0].update(extra=True))
        mutations += (lambda item: item.pop("base_sha"), lambda item: item.update(base_sha=1))
        mutations += (lambda item: item.update(starting_live_sha="b" * 40),)
        for mutation in mutations:
            changed = copy.deepcopy(record)
            mutation(changed)
            self.assertRaises(checks.jsonschema.ValidationError, checks.jsonschema.validate, changed, SCHEMA)
        for source in ('{"x":1,"x":2}', '{"x":1e999}', '{"x":NaN}'):
            self.assertRaises(ValueError, checks.strict_json, source)
        files = {}
        rows = [entry(turn, files) for turn in ("W00-SOL-REPAIR04-20260819T025659Z", TURN)]
        data = {"schema_version": "bsl.handoff-registry.v1", "entries": rows}
        with (
            mock.patch.object(checks, "reader", return_value=files.__getitem__),
            mock.patch.object(checks, "git", return_value="\n".join(files)),
        ):
            for changed in (rows[::-1], rows[:1], [{**rows[0], "json_sha256": "0" * 64}, rows[1]], rows * 2):
                self.assertRaises(ValueError, checks.registry_entries, SHA, {**data, "entries": changed})
        for path in ("../x", "/x", "a//b", "a\\b"):
            self.assertRaises(ValueError, checks.safe_path, path)
        self.assertRaises(ValueError, checks.identity, "bad", SHA, BRANCH)
        self.assertRaises(ValueError, checks.identity, SHA, SHA, "main")
        diff_argv = checks.command_suite(SHA, "b" * 40, BRANCH)[8]
        self.assertEqual(diff_argv, ("git", "diff", "--check", f"{SHA}...{'b' * 40}"))
        suite = checks.command_suite(SHA, SHA, BRANCH)
        self.assertTrue(all({"-B", checks.COVERAGE} <= set(argv) for argv in suite[:2]))
        self.assertRegex((ROOT / checks.WORKFLOW).read_text(), r"turn-handoff-integrity:[\s\S]+env: \{PR_URL:")

    def test_evidence_chronology_review_and_budget(self):
        record, files = fixture()
        cases = (
            (0, "started_at_utc", BEFORE),
            (0, "finished_at_utc", BEFORE),
            (0, "finished_at_utc", AFTER),
            (0, "started_at_utc", OFFSET),
            (0, "implementation_head_sha", "c" * 40),
            (8, "argv", ["git", "diff", "--check"]),
            (1, "receipt", record["commands"][0]["receipt"]),
            (1, "stdout", record["commands"][0]["stdout"]),
            (0, "stdout", {**record["commands"][0]["stdout"], "sha256": "0" * 64}),
        )
        for index, field, value in cases:
            changed = copy.deepcopy(record)
            changed["commands"][index][field] = value
            self.assertRaises((ValueError, KeyError), checks.validate_commands, changed, files.__getitem__, set(), AT)
        record["completed_at_utc"] = AFTER
        first = record["commands"][0]
        first["finished_at_utc"] = record["completed_at_utc"]
        first["receipt"] = signed_receipt(files, first["receipt"]["path"], first)
        checks.validate_commands(record, files.__getitem__, set(), AT)
        first["started_at_utc"] = AFTER
        first["receipt"] = signed_receipt(files, first["receipt"]["path"], first)
        self.assertRaises(ValueError, checks.validate_commands, record, files.__getitem__, set(), AT)
        record, files = fixture()
        status = record["commands"][-1]
        status["stdout"] = store(files, status["stdout"]["path"], b"?? rogue\n")
        status["receipt"] = signed_receipt(files, status["receipt"]["path"], status)
        self.assertRaises(ValueError, checks.validate_commands, record, files.__getitem__, set(), AT)
        mutations = (
            lambda item: item["commands"][0].update(finished_at_utc="2026-08-19T12:30:00Z"),
            lambda item: item["independent_review"].update(implementation_tree_sha="e" * 40),
            lambda item: item["independent_review"].update(diff_sha256="f" * 64),
            lambda item: item["independent_review"].update(artifacts_inspected=[]),
            lambda item: item["independent_review"]["findings"].append(OPEN),
            None,
            "MINIFIED",
        )
        for mutation in mutations:
            record, _files = fixture()
            if callable(mutation):
                mutation(record)
            artifacts = review_files(record, b"diff")
            if mutation is None:
                artifacts["REVIEW_INSTRUCTION"] = b"generic\n"
            elif mutation == "MINIFIED":
                artifacts["REVIEW_REPORT_RECORD"] = encoded(record["independent_review"])
            with mock.patch.multiple(
                checks, run=mock.Mock(return_value=mock.Mock(stdout=b"diff")), git=mock.Mock(return_value="d" * 40)
            ):
                self.assertRaises(ValueError, checks.validate_review, record, artifacts)
        cases = (((401, 0), (400, 0), b"x\ny\n"), ((300, 0), (300, 0), b"{}\n"))
        cases += (((300, 0), (300, 0), b"x" * 121 + b"\ny\n"),)
        for production, tests, content in cases:
            with mock.patch.multiple(
                checks, diff_lines=mock.Mock(side_effect=[production, tests]), blob=mock.Mock(return_value=content)
            ):
                self.assertRaises(ValueError, checks.budget, SHA, "b" * 40)
        path = f"{checks.EVIDENCE_ROOT}/{TURN}/link.json"
        with mock.patch.object(checks, "git", return_value=f"120000 blob {'a' * 40}\t{path}"):
            self.assertRaises(ValueError, checks.reader("b" * 40), path)
        radon = subprocess.check_output(["uvx", "radon@6.0.1", "cc", "-j", checks.CODE], cwd=ROOT)
        with mock.patch.multiple(
            checks,
            blob=mock.Mock(side_effect=lambda _revision, path: (ROOT / path).read_bytes()),
            budget=mock.Mock(
                side_effect=lambda _base, head: {"substantive_lines_total": 800 if head[0] == "c" else 795}
            ),
        ):
            receipt = checks.complexity(SHA, SHA, "c" * 40, radon)
        self.assertNotIn("nesting", receipt["measured"])
        self.assertEqual(receipt["measured"]["substantive_lines_total"], 800)
        self.assertEqual(receipt["configured"]["nesting_limit"], 3)
        self.assertEqual(receipt["target_excess_justification"], "ABOVE_TARGET_SMALLEST_READABLE_KERNEL")
        prior = {"handoffs/W00/evidence/prior/review.txt": "old"}
        for mode in ("BOOTSTRAP", "APPEND"):
            for candidate in ({next(iter(prior)): "new"}, prior | {"handoffs/W00/evidence/rogue.txt": "x"}):
                with mock.patch.multiple(
                    checks,
                    handoff_entries=mock.Mock(return_value=[]),
                    handoff_snapshot=mock.Mock(side_effect=[candidate, prior]),
                ):
                    self.assertRaises(ValueError, checks.validate_project_history, SHA, SHA, mode, [])

    def test_bootstrap_handoff_and_squash_append(self):
        prior_files = {}
        prior = entry("W00-SOL-REPAIR04-20260819T025659Z", prior_files)
        registry = {"schema_version": "bsl.handoff-registry.v1", "entries": [prior]}
        activation = {"activation_id": checks.ACTIVATION, "status": "APPROVED", "root_turn": {"task_id": "W00"}}
        with tempfile.TemporaryDirectory() as repo:
            git_capture(repo, "init", "-q")
            immutable = {path: (ROOT / path).read_bytes() for path in checks.IMMUTABLE}
            base = commit(repo, {checks.ACTIVATION_PATH: encoded(activation)} | immutable)
            start = commit(repo, prior_files)
            local_schema = copy.deepcopy(SCHEMA)
            local_schema["properties"]["starting_live_sha"] = {"const": start}
            schema_bytes = json.dumps(local_schema, indent=2).encode()
            active = {checks.CODE: b"def active():\n    return True\n", checks.TEST: b"VALUE = True\n"}
            active[checks.WORKFLOW] = (ROOT / checks.WORKFLOW).read_bytes()
            active |= {checks.SCHEMA: schema_bytes, checks.REGISTRY: json.dumps(registry, indent=2).encode()}
            implementation = commit(repo, active)
            with (
                chdir(repo),
                mock.patch.object(checks, "START", start),
                mock.patch.object(checks, "complexity") as measured,
            ):
                checks.validate_project(base, implementation, BRANCH)
                for change in ({"outside.txt": b"rogue\n"}, {checks.WORKFLOW: b"on : {push: {}}\n"}):
                    bad = commit(repo, change)
                    self.assertRaises(ValueError, checks.validate_project, base, bad, BRANCH)
                    git_capture(repo, "switch", "-q", "--detach", implementation)
                binary = subprocess.check_output(["git", "-C", repo, "diff", "--binary", f"{base}...{implementation}"])
                tree = git_capture(repo, "rev-parse", f"{implementation}^{{tree}}")
                record, evidence = fixture(base, implementation, start, binary, tree)
                record["integrity"]["schema_sha256"] = checks.digest(schema_bytes)
                record["integrity"].update(registry_mode="BOOTSTRAP", registry_entry_count=2)
                record["changes"] = checks.change_ledger(base, implementation)
                measured.return_value = record["complexity_receipt"]
                pair = {f"handoffs/W00/{TURN}.json": encoded(record)}
                pair[f"handoffs/W00/{TURN}.md"] = checks.render_markdown(record).encode()
                registry["entries"].append(entry(TURN, pair))
                final_registry = json.dumps(registry, indent=2).encode()
                bad_pair = pair | {f"handoffs/W00/{TURN}.md": pair[f"handoffs/W00/{TURN}.md"] + b"Merged.\n"}
                bad_registry = copy.deepcopy(registry)
                bad_registry["entries"][-1]["markdown_sha256"] = checks.digest(bad_pair[f"handoffs/W00/{TURN}.md"])
                variants = (evidence | bad_pair | {checks.REGISTRY: json.dumps(bad_registry, indent=2).encode()},)
                variants += (evidence | pair | {checks.REGISTRY: final_registry, checks.CODE: b"changed\n"},)
                for files in variants:
                    bad = commit(repo, files)
                    self.assertRaises(ValueError, checks.validate_handoff, base, bad, BRANCH, PR)
                    git_capture(repo, "switch", "-q", "--detach", implementation)
                final = commit(repo, evidence | pair | {checks.REGISTRY: final_registry})
                result = checks.validate_handoff(base, final, BRANCH, PR)
                self.assertEqual(result["implementation_head_sha"], implementation)
                invalid = ((start, final, BRANCH, PR), (base, final, "codex/other", PR))
                invalid += ((base, final, BRANCH, "https://github.com/other/repo/pull/7"), (final, base, BRANCH, PR))
                for arguments in invalid:
                    self.assertRaises((ValueError, subprocess.CalledProcessError), checks.validate_handoff, *arguments)
                self.assertEqual(checks.validate_project(base, final, BRANCH)["scope"], "BOOTSTRAP_COMPATIBILITY_ONLY")
                tree = git_capture(repo, "rev-parse", f"{final}^{{tree}}")
                squash = git_capture(repo, "commit-tree", tree, "-p", base, input="squash\n")
                subprocess.run(["git", "switch", "-q", "--detach", squash], check=True)
                later_files = {}
                registry["entries"].append(entry("W00-SOL-REPAIR05-20260820T120000Z", later_files))
                candidate = commit(repo, later_files | {checks.REGISTRY: json.dumps(registry, indent=2).encode()})
                mode, entries = checks.validate_registry(squash, candidate)
                self.assertEqual(checks.validate_project_history(squash, candidate, mode, entries), set())
                ancestry = subprocess.run(["git", "merge-base", "--is-ancestor", final, candidate])
                self.assertNotEqual(ancestry.returncode, 0)
