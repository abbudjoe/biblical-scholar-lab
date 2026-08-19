import copy
import json
import sys
import tempfile
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


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def put(root: Path, path: str, content: bytes) -> str:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    return checks.digest(content)


def fixture() -> tuple[dict[str, object], Path, set[str], tempfile.TemporaryDirectory[str]]:
    temporary = tempfile.TemporaryDirectory()
    root, record = Path(temporary.name), checks.strict_json(RECORD.read_bytes())
    for item in record["commands"]:
        put(root, item["stdout_path"], b"output")
        put(root, item["stderr_path"], b"")
        receipt = {key: value for key, value in item.items() if not key.startswith("receipt_")}
        item["receipt_sha256"] = put(root, item["receipt_path"], canonical(receipt))
    auth = record["github_auth_preflight"]
    receipt = {key: value for key, value in auth.items() if not key.startswith("receipt_")}
    auth["receipt_sha256"] = put(root, auth["receipt_path"], canonical(receipt))
    for item in record["artifacts"]:
        item["sha256"] = put(root, item["path"], b"{}")
    paths = {str(path.relative_to(root)) for path in root.rglob("*") if path.is_file()}
    return record, root, paths, temporary


def validate(record: dict[str, object], root: Path, paths: set[str]) -> None:
    checks.validate_record(record, SCHEMA, lambda path: (root / path).read_bytes(), paths, IMPLEMENTED, LIMIT)


def sync(record: dict[str, object], root: Path, index: int) -> None:
    item = record["commands"][index]
    receipt = {key: value for key, value in item.items() if not key.startswith("receipt_")}
    item["receipt_sha256"] = put(root, item["receipt_path"], canonical(receipt))


class W00A1aTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record, self.root, self.paths, temporary = fixture()
        self.addCleanup(temporary.cleanup)

    def rejects(self, mutate: object, *, sync_index: int | None = None) -> None:
        changed = copy.deepcopy(self.record)
        mutate(changed)
        if sync_index is not None:
            sync(changed, self.root, sync_index)
        with self.assertRaises((ValueError, FileNotFoundError, checks.jsonschema.ValidationError)):
            validate(changed, self.root, self.paths)

    def test_typed_truth_and_recursive_schema(self) -> None:
        validate(self.record, self.root, self.paths)
        markdown = checks.render_markdown(self.record, HEAD)
        self.assertIn('"approval_submitted":false', markdown)
        self.assertIn('"merge_performed":false', markdown)
        for claim in ("The pull request is merged.", "Owner approval was submitted."):
            with self.assertRaises(ValueError):
                checks.validate_markdown(self.record, HEAD, markdown + claim)
        for mutate in (
            lambda x: x.__setitem__("unknown", True),
            lambda x: x["commands"][0].__setitem__("unknown", True),
            lambda x: x["commands"][0].pop("receipt_sha256"),
            lambda x: x["github_auth_preflight"].__setitem__("unknown", True),
            lambda x: x["complexity_receipt"].__setitem__("unknown", True),
            lambda x: x["artifacts"][0].__setitem__("unknown", True),
            lambda x: x.__setitem__("merge_performed", "false"),
            lambda x: x.pop("approval_submitted"),
            lambda x: x.__setitem__("status", "SAFE_TO_MERGE"),
            lambda x: x["changes"][0].__setitem__("summary", "merged"),
            lambda x: x.__setitem__("known_risks", ["MERGED"]),
        ):
            self.rejects(mutate)
        for source in ('{"x":1,"x":2}', '{"x":1e999}', "{"):
            with self.assertRaises(ValueError):
                checks.strict_json(source)
        self.assertEqual(checks.strict_json('{"x":1.5}')["x"], 1.5)
        checks.validate_markdown(self.record, HEAD, markdown)

    def test_git_primitives_and_bootstrap_project(self) -> None:
        head = checks.PRIOR_HANDOFFS[-1][0]
        checks.activation(checks.BASE_SHA, checks.BRANCH)
        paths = checks.changed_paths(checks.BASE_SHA, head)
        self.assertGreater(sum(checks._diff_lines(checks.BASE_SHA, head)), 0)
        self.assertEqual(checks._diff_lines(checks.BASE_SHA, head, []), (0, 0))
        checks.object_at(checks.BASE_SHA, checks.ACTIVATION_PATH)
        checks.artifact_reader(checks.BASE_SHA)(checks.ACTIVATION_PATH)
        checks.budget(checks.BASE_SHA, head, paths)
        checks._prior(head)
        with (
            mock.patch.object(checks, "changed_paths", return_value=[checks.WORKFLOW]),
            mock.patch.object(checks, "budget", return_value=self.record["complexity_receipt"]),
        ):
            checks.validate_project(checks.BASE_SHA, head, checks.BRANCH)

    def test_receipts_paths_and_evidence_set(self) -> None:
        first = self.record["commands"][0]
        root = f"{checks.EVIDENCE_ROOT}/{TURN}"
        for mutate in (
            lambda x: x["commands"][0].__setitem__("receipt_sha256", "0" * 64),
            lambda x: x["commands"][1].__setitem__("command_evidence_id", "CMD_01"),
            lambda x: x["commands"][1].__setitem__("command_index", 1),
            lambda x: x["commands"][1].__setitem__("command_index", 3),
            lambda x: x["commands"][1].__setitem__("receipt_path", first["receipt_path"]),
            lambda x: x["commands"][1].__setitem__("stdout_path", first["stdout_path"]),
            lambda x: x["commands"][1].__setitem__("stderr_path", first["stderr_path"]),
            lambda x: x["commands"][0].__setitem__("receipt_path", f"{root}/missing.receipt.json"),
            lambda x: x["commands"][0].__setitem__("stdout_path", "../escape.stdout"),
            lambda x: x["commands"][0].__setitem__("stdout_path", "/tmp/escape.stdout"),
            lambda x: x["commands"][0].__setitem__("stdout_path", f"{root}//ambiguous.stdout"),
            lambda x: x["commands"][0].__setitem__("implementation_head_sha", "d" * 40),
            lambda x: x["commands"][0].__setitem__("root_turn_id", TURN + "X"),
        ):
            self.rejects(mutate)
        receipt_path = first["receipt_path"]
        receipt = checks.strict_json((self.root / receipt_path).read_bytes())
        receipt["command_evidence_id"] = "OTHER"
        first["receipt_sha256"] = put(self.root, receipt_path, canonical(receipt))
        with self.assertRaises(ValueError):
            validate(self.record, self.root, self.paths)
        sync(self.record, self.root, 0)
        self.paths.add(f"{root}/dangling.receipt.json")
        with self.assertRaises(ValueError):
            validate(self.record, self.root, self.paths)

    def test_symlink_and_chronology(self) -> None:
        path = f"{checks.EVIDENCE_ROOT}/{TURN}/link.stdout"
        entry = f"120000 blob {'a' * 40}\t{path}"
        with mock.patch.object(checks, "git", return_value=entry), self.assertRaises(ValueError):
            checks.artifact_reader(HEAD)(path)
        for field, value in (
            ("finished_at_utc", "2026-08-18T23:51:00Z"),
            ("started_at_utc", "2026-08-18T23:49:00Z"),
            ("finished_at_utc", "2026-08-19T00:01:00Z"),
            ("started_at_utc", "2026-08-18T23:53:00+00:00"),
        ):
            self.rejects(lambda x, f=field, v=value: x["commands"][0].__setitem__(f, v), sync_index=0)
        sequential, root, paths, temporary = fixture()
        self.addCleanup(temporary.cleanup)
        sequential["commands"][1].update(started_at_utc="2026-08-18T23:56:00Z", finished_at_utc="2026-08-18T23:57:00Z")
        sync(sequential, root, 1)
        validate(sequential, root, paths)
        self.rejects(lambda x: x["commands"].reverse())
        self.rejects(lambda x: x["commands"][1].__setitem__("started_at_utc", "2026-08-18T23:51:00Z"), sync_index=1)

    def test_append_only_scope_and_budget(self) -> None:
        pair = [f"handoffs/W00/{TURN}.{suffix}" for suffix in ("json", "md")]
        evidence = f"{checks.EVIDENCE_ROOT}/{TURN}/01.stdout"
        additions = "\n".join(f"A\t{path}" for path in [*pair, evidence])
        with mock.patch.object(checks, "git", return_value=additions):
            self.assertEqual(checks._record_files("d" * 40, HEAD)[2], {evidence})
        with mock.patch.object(checks, "git", return_value=""):
            self.assertIsNone(checks._record_files("d" * 40, HEAD))
        for source in (additions.replace("A\t", "M\t", 1), additions + f"\nA\thandoffs/W00/{TURN}x.json"):
            with mock.patch.object(checks, "git", return_value=source), self.assertRaises(ValueError):
                checks._record_files("d" * 40, HEAD)
        prior = (("c" * 40, "b" * 40, TURN),)
        for evidence in ([b"original", b"changed"], FileNotFoundError()):
            with (
                mock.patch.object(checks, "PRIOR_HANDOFFS", prior),
                mock.patch.object(checks.subprocess, "run", return_value=mock.Mock(returncode=0)),
                mock.patch.object(checks, "git", return_value="b" * 40),
                mock.patch.object(checks, "blob", side_effect=evidence),
                self.assertRaises((ValueError, FileNotFoundError)),
            ):
                checks._prior("d" * 40)
        checks.validate_budget(self.record["complexity_receipt"])
        self.record["complexity_receipt"]["substantive_lines_total"] = 801
        with self.assertRaises(ValueError):
            checks.validate_budget(self.record["complexity_receipt"])
        source = (ROOT / "governance/w00_checks.py").read_text()
        for deferred in ("import ast", "policy_calls", "class_surface", "_dependencies", "w00_yaml"):
            self.assertNotIn(deferred, source)

    def test_composed_handoff(self) -> None:
        final, pair = "d" * 40, (f"handoffs/W00/{TURN}.json", f"handoffs/W00/{TURN}.md")
        record_files = (TURN, pair, self.paths)

        def fake_git(*args: str) -> str:
            if args[0] == "rev-list":
                return f"{final} {HEAD}"
            if args[0] == "rev-parse":
                return "b" * 40
            if args[0] == "diff-tree":
                return "\n".join(sorted(set(pair) | self.paths))
            return "2026-08-18T23:51:00+00:00" if args[-1] == HEAD else "2026-08-19T00:00:00+00:00"

        def objects(revision: str, path: str) -> object:
            return SCHEMA if path == checks.SCHEMA else self.record

        commands = self.record["commands"]
        commands[1]["argv"] = list(checks.project_command(HEAD))
        sync(self.record, self.root, 1)
        with (
            mock.patch.multiple(
                checks, activation=mock.DEFAULT, _prior=mock.DEFAULT, changed_paths=mock.DEFAULT, budget=mock.DEFAULT
            ),
            mock.patch.object(checks, "PRIOR_HANDOFFS", ()),
            mock.patch.object(checks, "_record_files", side_effect=[record_files, None]),
            mock.patch.object(checks, "git", side_effect=fake_git),
            mock.patch.object(checks, "object_at", side_effect=objects),
            mock.patch.object(checks, "artifact_reader", return_value=lambda path: (self.root / path).read_bytes()),
            mock.patch.object(checks, "blob", return_value=checks.render_markdown(self.record, HEAD).encode()),
            mock.patch.object(checks, "VALIDATION_ARGV", (tuple(commands[0]["argv"]),)),
        ):
            checks.changed_paths.return_value = []
            checks.budget.return_value = self.record["complexity_receipt"]
            checks.validate_handoff(checks.BASE_SHA, final, checks.BRANCH, checks.PR_URL)
