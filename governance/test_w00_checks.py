import copy
import json
import sys
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "governance"))
import w00_checks as checks  # noqa: E402

TURN = "W00-SOL-REPAIR04-20260818T235900Z"
HEAD = "c" * 40
IMPLEMENTED = datetime(2026, 8, 18, 23, 51, tzinfo=UTC)
LIMIT = datetime(2026, 8, 19, 0, 0, tzinfo=UTC)
SCHEMA = checks.strict_json((ROOT / checks.SCHEMA).read_bytes())
RECORD = ROOT / "governance/fixtures/w00a1a-record.json"
NEGATIVES = checks.strict_json((ROOT / "governance/fixtures/w00a1a-negative.json").read_bytes())


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def put(files: dict[str, bytes], path: str, content: bytes) -> str:
    files[path] = content
    return checks.digest(content)


def fixture() -> tuple[dict[str, object], dict[str, bytes]]:
    record, files = checks.strict_json(RECORD.read_bytes()), {}
    for index, item in enumerate(record["commands"]):
        item["stdout_sha256"] = put(files, item["stdout_path"], b"92\n" if index == 1 else b"output")
        put(files, item["stderr_path"], b"")
        receipt = {key: value for key, value in item.items() if not key.startswith("receipt_")}
        item["receipt_sha256"] = put(files, item["receipt_path"], canonical(receipt))
    auth = record["github_auth_preflight"]
    receipt = {key: value for key, value in auth.items() if not key.startswith("receipt_")}
    auth["receipt_sha256"] = put(files, auth["receipt_path"], canonical(receipt))
    dr30 = dict(zip(checks.DR30_KEYS, (400, 50, 9, 120, 3, checks.POLICY["target_excess"], "PASS"), strict=True))
    reports = checks._reports(record, 92, dr30)
    for item in record["artifacts"]:
        item["sha256"] = put(files, item["path"], canonical(reports[item["artifact_id"]]))
    return record, files


def validate(record: dict[str, object], files: dict[str, bytes]) -> None:
    checks.validate_record(record, SCHEMA, files.__getitem__, set(files), IMPLEMENTED, LIMIT)


def sync(record: dict[str, object], files: dict[str, bytes], index: int) -> None:
    item = record["commands"][index]
    receipt = {key: value for key, value in item.items() if not key.startswith("receipt_")}
    item["receipt_sha256"] = put(files, item["receipt_path"], canonical(receipt))


def apply_case(record: dict[str, object], case: dict[str, object]) -> None:
    target = record
    for key in case["path"][:-1]:
        target = target[key]
    key, operation = case["path"][-1], case["op"]
    if operation == "set":
        target[key] = copy.deepcopy(case["value"])
    elif operation == "pop":
        target.pop(key)
    elif operation == "append_copy":
        target[key].append(copy.deepcopy(target[key][case["value"]]))
    else:
        target[key].reverse()


class W00A1aTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record, self.files = fixture()

    def rejects(self, mutate: object, *, sync_index: int | None = None) -> None:
        changed, files = copy.deepcopy((self.record, self.files))
        mutate(changed)
        if sync_index is not None:
            sync(changed, files, sync_index)
        with self.assertRaises((ValueError, KeyError, checks.jsonschema.ValidationError)):
            validate(changed, files)

    def test_typed_truth_and_recursive_schema(self) -> None:
        validate(self.record, self.files)
        markdown = checks.render_markdown(self.record, HEAD)
        self.assertIn('"approval_submitted":false', markdown)
        self.assertIn(checks.POLICY["stop_statement"], markdown)
        self.assertEqual(self.record["commands"][0]["argv"].count("--with"), 2)
        self.assertEqual(SCHEMA["properties"]["status"]["const"], checks.POLICY["terminal_dispositions"][0])
        for case in NEGATIVES:
            self.rejects(lambda record, item=case: apply_case(record, item), sync_index=case.get("sync"))
        for source in ('{"x":1,"x":2}', '{"x":1e999}', "{"):
            with self.assertRaises(ValueError):
                checks.strict_json(source)
        self.assertEqual(checks.strict_json('{"x":1.5}')["x"], 1.5)

    def test_git_primitives_and_bootstrap_project(self) -> None:
        head = checks.PRIOR_HANDOFFS[-1][0]
        checks.activation(checks.BASE_SHA, checks.BRANCH)
        paths = checks.paths_at(checks.BASE_SHA, head)
        self.assertEqual(checks._diff_lines(checks.BASE_SHA, head, []), (0, 0))
        checks.object_at(checks.BASE_SHA, checks.ACTIVATION_PATH)
        checks.artifact_reader(checks.BASE_SHA)(checks.ACTIVATION_PATH)
        checks.budget(checks.BASE_SHA, head, paths)
        checks._prior(head)
        with (
            mock.patch.object(checks, "budget", return_value=self.record["complexity_receipt"]),
            mock.patch.object(checks, "blob", side_effect=lambda _revision, path: (ROOT / path).read_bytes()),
        ):
            checks.validate_project(checks.BASE_SHA, checks.BASE_SHA, checks.BRANCH)
        report = {"governance/w00_checks.py": [{"lineno": 1, "endline": 40, "complexity": 9}]}
        with mock.patch.object(checks, "blob", return_value=b"x\n" * 400):
            metrics = checks._dr30({checks.VALIDATION_ARGV[6]: canonical(report)}, HEAD, 700)
        bad = {**metrics, "cyclomatic_complexity_max": 11}
        with self.assertRaises(ValueError):
            checks._check_dr30(bad, 700)

    def test_receipts_paths_and_evidence_set(self) -> None:
        first = self.record["commands"][0]
        receipt_path = first["receipt_path"]
        receipt = checks.strict_json(self.files[receipt_path])
        receipt["command_evidence_id"] = "OTHER"
        first["receipt_sha256"] = put(self.files, receipt_path, canonical(receipt))
        with self.assertRaises(ValueError):
            validate(self.record, self.files)
        sync(self.record, self.files, 0)
        review = self.record["artifacts"][1]
        original = self.files[review["path"]]
        review["sha256"] = put(self.files, review["path"], b"{}")
        with self.assertRaises(ValueError):
            validate(self.record, self.files)
        review["sha256"] = put(self.files, review["path"], original)
        self.files[f"{checks.EVIDENCE_ROOT}/{TURN}/dangling.receipt.json"] = b""
        with self.assertRaises(ValueError):
            validate(self.record, self.files)

    def test_symlink_and_chronology(self) -> None:
        path = f"{checks.EVIDENCE_ROOT}/{TURN}/link.stdout"
        entry = f"120000 blob {'a' * 40}\t{path}"
        with mock.patch.object(checks, "git", return_value=entry), self.assertRaises(ValueError):
            checks.artifact_reader(HEAD)(path)
        sequential, files = fixture()
        for index, command in enumerate(sequential["commands"][1:], 1):
            command.update(started_at_utc="2026-08-18T23:56:00Z", finished_at_utc="2026-08-18T23:57:00Z")
            sync(sequential, files, index)
        validate(sequential, files)

    def test_append_only_scope_and_budget(self) -> None:
        pair = [f"handoffs/W00/{TURN}.{suffix}" for suffix in ("json", "md")]
        evidence = f"{checks.EVIDENCE_ROOT}/{TURN}/01.stdout"
        additions = "\n".join(f"A\t{path}" for path in [*pair, evidence])
        with mock.patch.object(checks, "git", return_value=additions):
            self.assertEqual(checks._record_files("d" * 40, HEAD)[2], {evidence})
        with mock.patch.object(checks, "git", return_value="A\ta.py\nM\tb.py\nD\tc.py"):
            self.assertEqual(
                [item["kind"] for item in checks.change_ledger(checks.BASE_SHA, HEAD)], ["ADD", "MODIFY", "DELETE"]
            )
        for source in (additions.replace("A\t", "M\t", 1), additions + f"\nA\thandoffs/W00/{TURN}x.json"):
            with mock.patch.object(checks, "git", return_value=source), self.assertRaises(ValueError):
                checks._record_files("d" * 40, HEAD)
        for evidence in ([b"original", b"changed"], FileNotFoundError()):
            with (
                mock.patch.object(checks, "PRIOR_HANDOFFS", (("c" * 40, "b" * 40, TURN),)),
                mock.patch.object(checks.subprocess, "run", return_value=mock.Mock(returncode=0)),
                mock.patch.object(checks, "git", return_value="b" * 40),
                mock.patch.object(checks, "blob", side_effect=evidence),
                self.assertRaises((ValueError, FileNotFoundError)),
            ):
                checks._prior("d" * 40)
        self.record["complexity_receipt"]["substantive_lines_total"] = 801
        with self.assertRaises(ValueError):
            checks.validate_budget(self.record["complexity_receipt"])
        for deferred in ("import ast", "policy_calls", "class_surface", "_dependencies", "w00_yaml"):
            self.assertNotIn(deferred, (ROOT / "governance/w00_checks.py").read_text())
        with mock.patch.object(checks, "blob", return_value=b"x" * 262_145), self.assertRaises(ValueError):
            checks.object_at(HEAD, checks.SCHEMA)
        self.assertLessEqual(max(map(len, (ROOT / "governance/w00_checks.py").read_text().splitlines())), 120)

    def test_composed_handoff(self) -> None:
        final, pair = "d" * 40, (f"handoffs/W00/{TURN}.json", f"handoffs/W00/{TURN}.md")
        record_files = (TURN, pair, set(self.files))

        def fake_git(*args: str) -> str:
            if args[0] == "rev-list":
                return f"{final} {HEAD}"
            if args[0] == "rev-parse":
                return "b" * 40
            if args[0] == "diff-tree":
                return "\n".join(sorted(set(pair) | set(self.files)))
            return "2026-08-18T23:51:00+00:00" if args[-1] == HEAD else "2026-08-19T00:00:00+00:00"

        commands = self.record["commands"]
        commands[-1]["argv"] = list(checks.project_command(HEAD))
        sync(self.record, self.files, len(commands) - 1)
        dr30 = checks.strict_json(self.files[self.record["artifacts"][0]["path"]])["dr30"]
        names = "activation _prior change_ledger budget _dr30".split()

        def objects(_revision: str, path: str) -> object:
            return SCHEMA if path == checks.SCHEMA else self.record

        with (
            mock.patch.multiple(checks, **{name: mock.DEFAULT for name in names}),
            mock.patch.object(checks, "PRIOR_HANDOFFS", ()),
            mock.patch.object(
                checks, "_record_files", side_effect=lambda commit, _parent: record_files if commit == final else None
            ),
            mock.patch.object(checks, "git", side_effect=fake_git),
            mock.patch.object(checks, "object_at", side_effect=objects),
            mock.patch.object(checks, "artifact_reader", return_value=self.files.__getitem__),
            mock.patch.object(checks, "blob", return_value=checks.render_markdown(self.record, HEAD).encode()),
        ):
            checks.change_ledger.return_value = self.record["changes"]
            checks.budget.return_value = self.record["complexity_receipt"]
            checks._dr30.return_value = dr30
            checks.validate_handoff(checks.BASE_SHA, final, checks.BRANCH, checks.PR_URL)
            for contradiction in ("The PR was merged.", "Owner approval was submitted."):
                checks.blob.return_value = (checks.render_markdown(self.record, HEAD) + contradiction).encode()
                with self.assertRaises(ValueError):
                    checks.validate_handoff(checks.BASE_SHA, final, checks.BRANCH, checks.PR_URL)
