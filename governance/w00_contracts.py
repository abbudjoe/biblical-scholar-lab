import ast
import hashlib
import json
import math
import re
from datetime import UTC, datetime
from typing import Any, cast

import jsonschema

REPOSITORY = "abbudjoe/biblical-scholar-lab"
BRANCH = "codex/w00-repository-governance"
ACTIVATION = "ACT-W00-REPOSITORY-GOVERNANCE-v3"
BASE = "3d3ebb706fe6c8779445cbbfd9fea271b86d3646"
ROOT = "/Users/joseph/biblical-scholar-lab"
PR_URL = f"https://github.com/{REPOSITORY}/pull/1"
PR_TITLE = "W00A1: local governance kernel and defense checks"
NON_NORMATIVE_TOKEN = re.compile(r"[A-Za-z0-9_./:@=-]+")
REQUIRED_FINDINGS = set(
    "R0-P1-TRUST-PROVENANCE R1-F2 R2-F4 R3-F3 R4-F1 R5-F1 R6-F7 R7-F5 R8-F6 "
    "R02-P2-STRICT-CONTENT R02-P2-HANDOFF-EVIDENCE R02-P2-CLAIMS R02-P2-CODEOWNERS "
    "R02-P2-QUALITY-SPEC R02-P1-ABSTRACTIONS R02-P2-DR30 P2-01 P2-02 P2-03 P2-04 P2-05 P2-06 "
    "R03-P2-WORKFLOW R03-P2-CHRONOLOGY R03-P2-PROTOCOL R03-P2-DISPOSITION "
    "R03R2-P2-SCHEMA R03R2-P2-ALIAS R03R2-P2-LEDGER R03R2-P2-STUB "
    "R03R2-P3-PROTOCOL-COVERAGE R03R2-P3-TOOL-INVENTORY R03R3-P2-DEPENDENCY-SCAN".split()
)
P1_FINDINGS = {"R0-P1-TRUST-PROVENANCE", "R1-F2", "R2-F4", "R3-F3", "R02-P1-ABSTRACTIONS"}
P3_FINDINGS = {"R03R2-P3-PROTOCOL-COVERAGE", "R03R2-P3-TOOL-INVENTORY"}
SPLIT_FINDINGS = {"R0-P1-TRUST-PROVENANCE", "R2-F4", "R5-F1", "R6-F7", "R02-P2-CODEOWNERS"}
EXTERNAL_TOOLS = "coverage==7.10.6 detect-secrets==1.5.0 mypy==2.3.1 pip-audit==2.10.1".split()
EXTERNAL_TOOLS += "radon==6.0.1 ruff==0.16.3 zizmor==1.29.0".split()
CONTROLLED, UNKNOWN, LITERAL, DERIVED, ITEM = "<controlled>", "<unknown>", "<literal>:", "<derived>:", "<item>:"
MAPPING, GETTER, SELECTOR, METHOD, CALLED = "<mapping>:", "<getter>:", "<selector>:", "<method>:", "<called>:"
PARSER, SUBPARSERS = "<argparse-parser>", "<argparse-subparsers>"
GETTERS = {"builtins.getattr", "inspect.getattr_static"}
GETTERS.update(f"builtins.{name}.__getattribute__" for name in ("object", "type"))
SAFE_CALLS = GETTERS | {"operator.attrgetter", "operator.methodcaller"}
DYNAMIC_IMPORTS = {"builtins.__import__", "importlib.import_module"}
DYNAMIC = DYNAMIC_IMPORTS | {"builtins.eval", "builtins.exec", "builtins.globals", "builtins.locals", "builtins.vars"}
BUILTINS = DYNAMIC | {f"builtins.{name}" for name in "dict getattr len object print setattr type".split()}
PROSE_FIELDS = "objective acceptance_criteria changes review_targets known_risks decisions_required".split()
PROSE_FIELDS += "complexity_receipt evaluations artifacts delegated_operations".split()
PYTHON_FILES = ("governance/w00_contracts.py", "governance/w00_checks.py", "governance/test_w00_checks.py")
STAGE_PATHS = set(PYTHON_FILES) | set(
    ".github/workflows/governance-integrity.yml governance/GOV-01-artifacts.sha256 "
    "governance/GOV-01-package-manifest.json governance/ruff.toml governance/schemas/turn-handoff.schema.json "
    "governance/w00_yaml.rb".split()
)
UV_PYTHON = ("uv", "run", "--with", "jsonschema==4.25.1", "--")
UV_COVERAGE = (*UV_PYTHON[:-1], "--with", "coverage==7.10.6", "--")
UV_AUDIT = (*UV_PYTHON[:-1], "--with", "pip-audit==2.10.1", "--")
VALIDATION_ARGV = (
    (*UV_PYTHON, "python3", "-m", "unittest", "-v", PYTHON_FILES[-1]),
    (*UV_PYTHON, "python3", "-m", "py_compile", *PYTHON_FILES[:-1]),
    (*UV_COVERAGE, "python3", "-m", "coverage", "run", "--branch", "-m", "unittest", PYTHON_FILES[-1]),
    (*UV_COVERAGE, "python3", "-m", "coverage", "report", "--fail-under=90", *PYTHON_FILES[:-1]),
    ("uvx", "ruff@0.16.3", "check", "--config", "governance/ruff.toml", *PYTHON_FILES),
    ("uvx", "ruff@0.16.3", "format", "--check", "--config", "governance/ruff.toml", *PYTHON_FILES),
    ("uvx", "mypy@2.3.1", "--strict", "--ignore-missing-imports", *PYTHON_FILES[:-1]),
    ("uvx", "detect-secrets@1.5.0", "scan", "--all-files"),
    (*UV_AUDIT, "python3", "-m", "pip_audit", "--local", "-S", "--progress-spinner=off"),
    ("uvx", "zizmor@1.29.0", ".github/workflows/governance-integrity.yml"),
    ("uvx", "radon@6.0.1", "cc", "-s", "-a", *PYTHON_FILES[:-1]),
    ("ruby", "-c", "governance/w00_yaml.rb"),
    ("shasum", "-a", "256", "-c", "governance/GOV-01-artifacts.sha256"),
    ("git", "diff", "--check"),
    ("git", "fsck", "--full"),
)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def strict_json(source: str | bytes) -> Any:
    def unique(items: list[tuple[str, Any]]) -> dict[str, Any]:
        need(len(items) == len(dict(items)), "JSON key is duplicated")
        return dict(items)

    def finite(value: str) -> float:
        number = float(value)
        need(math.isfinite(number), "JSON number is non-finite")
        return number

    try:
        return json.loads(source, object_pairs_hook=unique, parse_constant=finite, parse_float=finite)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError("JSON is malformed") from error


def _command_digest(item: dict[str, Any]) -> str:
    envelope = {key: item[key] for key in sorted(item) if key != "combined_evidence_artifact_sha256"}
    return hashlib.sha256(json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _command(item: dict[str, Any], identity: tuple[str, str, str]) -> datetime:
    keys = ("root_turn_id", "activation_id", "implementation_head_sha")
    need(tuple(item[key] for key in keys) == identity, "command identity differs")
    need(assess_argv(item["argv"]), "argv is not allowlisted")
    need(item["working_directory"] == ROOT, "working directory differs")
    times = [datetime.fromisoformat(item[key].replace("Z", "+00:00")) for key in ("started_at", "finished_at")]
    need(times[0] <= times[1], "command time order differs")
    need((item["exit_code"] == 0) == (item["result"] == "PASS"), "command result differs")
    need(_command_digest(item) == item["combined_evidence_artifact_sha256"], "command artifact binding differs")
    return times[1]


def _commands(items: list[dict[str, Any]], identity: tuple[str, str, str]) -> None:
    finished = [_command(item, identity) for item in items]
    turn = datetime.strptime(identity[0].rsplit("-", 1)[-1], "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)
    need(max(finished) <= turn, "command chronology differs")
    identities = [{item[key] for item in items} for key in ("command_evidence_id", "combined_evidence_artifact_sha256")]
    need(all(len(values) == len(items) for values in identities), "command evidence is reused")


def finding_state(finding: str) -> tuple[str, str]:
    severity = "P1" if finding in P1_FINDINGS else "P3" if finding in P3_FINDINGS else "P2"
    status = "SUPERSEDED_BY_APPROVED_SPLIT" if finding in SPLIT_FINDINGS else "CLOSED"
    if finding == "R03R2-P3-TOOL-INVENTORY":
        status = "BLOCKED_WITH_EXACT_REASON"
    return severity, status


def _finding_allowed(finding: str, item: dict[str, Any], blocked: bool) -> bool:
    expected, actual = finding_state(finding), (item["severity"], item["final_status"])
    return actual == expected or blocked and actual == (expected[0], "BLOCKED_WITH_EXACT_REASON")


def _review_state(record: dict[str, Any]) -> None:
    findings = {item["finding_id"]: item for item in record["review_targets"]}
    need(len(findings) == len(record["review_targets"]), "finding is duplicated")
    blocked = record["status"] != "READY_FOR_CHATGPT_REVIEW"
    complete = set(findings) == REQUIRED_FINDINGS
    complete = complete and all(_finding_allowed(finding, item, blocked) for finding, item in findings.items())
    need(complete, "finding ledger differs")


def _evidence(record: dict[str, Any]) -> None:
    artifacts = {item["artifact_id"] for item in record["artifacts"]}
    need(len(artifacts) == len(record["artifacts"]), "artifact is duplicated")
    need({item["evidence"] for item in record["evaluations"]} == artifacts, "artifact reference differs")
    if record["status"] == "READY_FOR_CHATGPT_REVIEW":
        need(all(item["status"] == "PASS" for item in record["evaluations"]), "evaluation is not passing")
        need(all(item["result"] == "CLEAN" for item in record["delegated_operations"]), "review is not clean")


def validate_handoff(record: dict[str, Any], schema: dict[str, Any]) -> None:
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    error = next(validator.iter_errors(record), None)
    need(error is None, f"handoff schema differs: {error.message if error else ''}")
    need(all((record["changes"], record["review_targets"], record["commands"])), "required evidence is empty")
    keys = ("schema_version", "project_id", "activation_id", "task_id", "repository", "branch", "base_sha", "pr_url")
    expected = ("1.0", "biblical-scholar-lab", ACTIVATION, "W00", REPOSITORY, BRANCH, BASE, PR_URL)
    need(tuple(record[key] for key in keys) == expected, "handoff identity differs")
    design = record["design_conformance"]
    need(design["status"] == "CONFORMING" and "W00-SPLIT-01" in design["approved_design_ids"], "design differs")
    billable = {"performed": False, "actual_cost_usd": 0, "campaign_ids": []}
    need(record["billable_actions"] == billable, "billable differs")
    need(record["compare_url"] == f"https://github.com/{REPOSITORY}/compare/{BASE}...{BRANCH}", "compare URL differs")
    _commands(record["commands"], (record["turn_id"], record["activation_id"], record["implementation_head_sha"]))
    _review_state(record)
    _evidence(record)
    expected_complexity = {"SPLIT_REQUIRED": "BLOCKED_REQUIRES_SPLIT"}.get(record["status"], "PASS")
    need(record["complexity_receipt"]["simplicity_conformance"] == expected_complexity, "simplicity differs")
    pending = [record[key] for key in PROSE_FIELDS]
    while pending:
        item = pending.pop()
        if isinstance(item, str):
            need(NON_NORMATIVE_TOKEN.fullmatch(item) is not None, "free-form JSON prose is prohibited")
        elif isinstance(item, (dict, list)):
            pending.extend(item.values() if isinstance(item, dict) else item)


def assess_argv(argv: list[str]) -> bool:
    if not argv or any(not token or "\0" in token for token in argv):
        return False
    if tuple(argv) in VALIDATION_ARGV:
        return True
    if tuple(argv[: len(UV_PYTHON)]) == UV_PYTHON:
        return _validator(argv[len(UV_PYTHON) :])
    if argv[0] in {"env", "command", "sudo", "xargs", "bash", "sh", "zsh"} or "=" in argv[0]:
        return False
    return {"gh": _gh, "git": _git}.get(argv[0], _validator)(argv)


def _gh(argv: list[str]) -> bool:
    if argv[:2] == ["gh", "auth"]:
        return argv == ["gh", "auth", "status", "--active", "--hostname", "github.com"]
    suffixes = (
        "pulls/1|issues/1/comments?per_page=100|actions/workflows?per_page=100|rulesets/20960975|"
        "codeowners/errors|contents/.github/CODEOWNERS?ref=main|environments/owner-merge-authorization"
    ).split("|")
    reads = {"user", f"repos/{REPOSITORY}", *(f"repos/{REPOSITORY}/{suffix}" for suffix in suffixes)}
    if argv[:2] == ["gh", "api"]:
        return len(argv) == 3 and argv[2].lstrip("/") in reads
    exact = (
        ["gh", "pr", "checks", "1", "--repo", REPOSITORY],
        ["gh", "pr", "comment", "1", "--repo", REPOSITORY, "--body-file", ".codex-tmp-pr-completion.md"],
        ["gh", "pr", "edit", "1", "--repo", REPOSITORY, "--title", PR_TITLE, "--body-file", ".codex-tmp-pr-body.md"],
    )
    return argv in exact


def _stage_paths(paths: list[str]) -> bool:
    handoff = r"handoffs/W00/W00-SOL-REPAIR03-[0-9]{8}T[0-9]{6}Z\.(?:md|json)"
    return bool(paths) and all(path in STAGE_PATHS or re.fullmatch(handoff, path) for path in paths)


def _git(argv: list[str]) -> bool:
    if argv == ["git", "push", "origin", BRANCH]:
        return True
    if argv[1:3] == ["commit", "-m"]:
        return len(argv) == 4 and argv[3] in {"W00A1 Repair03 local governance kernel", "W00A1 Repair03 handoff"}
    if argv[1:2] == ["add"]:
        return _stage_paths(argv[2:])
    fixed = (["git", "status", "--short"], ["git", "diff", "--check"], ["git", "fsck", "--full"])
    revision = argv[2] if len(argv) == 3 and argv[:2] == ["git", "rev-parse"] else ""
    return argv in fixed or revision == "HEAD" or re.fullmatch(r"[0-9a-f]{40}", revision.removesuffix("^")) is not None


def _validator(argv: list[str]) -> bool:
    if argv[:2] != ["python3", "governance/w00_checks.py"] or len(argv) < 3:
        return False
    common = ("--base-sha", "--head-sha", "--branch")
    specs = {"project-integrity": common, "turn-handoff-integrity": (*common, "--pr-url")}
    flags = specs.get(argv[2])
    if flags is None or len(argv[3:]) != len(flags) * 2 or tuple(argv[3::2]) != flags:
        return False
    values = dict(zip(flags, argv[4::2], strict=True))
    valid_head = values["--head-sha"] == "HEAD" or re.fullmatch(r"[0-9a-f]{40}", values["--head-sha"])
    identity = values["--base-sha"], values["--branch"], values.get("--pr-url", PR_URL)
    return bool(valid_head and identity == (BASE, BRANCH, PR_URL))


def _plain(symbol: str) -> str:
    return _plain(symbol.split(":", 1)[1]) if symbol.startswith((DERIVED, ITEM)) else symbol


class _Symbols(ast.NodeVisitor):
    def __init__(self, targets: set[str]) -> None:
        self.targets, self.prefixes = targets, {item.rpartition(".")[0] for item in targets}
        self.aliases: dict[str, set[str]] = {"__builtins__": {MAPPING + "builtins"}}
        self.calls: list[tuple[str, ast.Call]] = []
        self.scope = ""
        self.class_values: set[str] = set()
        self.classes: set[str] = set()

    def _literal(self, node: ast.AST | str | None) -> str | None:
        if isinstance(node, ast.Name):
            values = {item[len(LITERAL) :] for item in self._value(node) if item.startswith(LITERAL)}
            return next(iter(values)) if len(values) == 1 else None
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left, right = self._literal(node.left), self._literal(node.right)
            return left + right if left is not None and right is not None else None
        value = getattr(node, "value", None)
        return value if isinstance(value, str) else None

    def _member(self, bases: set[str], key: ast.AST | str | None) -> set[str]:
        literal = key if isinstance(key, str) and key != UNKNOWN else self._literal(key)
        output = set()
        for raw in bases:
            derived, base = raw.startswith(DERIVED), _plain(raw).removeprefix(MAPPING)
            if literal is not None:
                qualified = f"{base}.{literal}"
                values = self.aliases.get(qualified, {qualified})
                output.update({DERIVED + value if derived else value for value in values})
            elif base in self.prefixes | {"builtins", "importlib", SUBPARSERS}:
                output.add(CONTROLLED)
            else:
                output.add(UNKNOWN)
        return output or {UNKNOWN}

    def _attribute_value(self, raw: str, name: str) -> set[str]:
        derived, value = raw.startswith(DERIVED), _plain(raw)
        if value in {UNKNOWN, CONTROLLED}:
            return {value}
        if name == "__dict__":
            return {MAPPING + value}
        if name == "__getattribute__" or value.startswith(MAPPING) and name in {"get", "__getitem__"}:
            return {GETTER + value.removeprefix(MAPPING)}
        qualified = f"{value}.{name}"
        found = self.aliases.get(qualified, {qualified})
        return {DERIVED + item if derived else item for item in found}

    def _attribute(self, values: set[str], name: str) -> set[str]:
        return set().union(*(self._attribute_value(raw, name) for raw in values))

    def _container_items(self, values: set[str]) -> set[str]:
        items = {_plain(item[len(ITEM) :]) for item in values if item.startswith(ITEM)}
        return {DERIVED + item for item in items} or {UNKNOWN}

    def _get(self, function: str, node: ast.Call) -> set[str] | None:
        if function in GETTERS | {"builtins.dict.get"}:
            return self._member(self._value(node.args[0]), node.args[1]) if len(node.args) >= 2 else {UNKNOWN}
        if function.startswith(GETTER):
            return self._member({function[len(GETTER) :]}, node.args[0]) if node.args else {UNKNOWN}
        return None

    def _select(self, function: str, node: ast.Call) -> set[str] | None:
        if function in {"operator.attrgetter", "operator.methodcaller"}:
            marker = SELECTOR if function.endswith("attrgetter") else METHOD
            return {marker + (self._literal(node.args[0]) or UNKNOWN)} if node.args else {UNKNOWN}
        if not function.startswith((SELECTOR, METHOD)):
            return None
        if not node.args:
            return {UNKNOWN}
        marker = SELECTOR if function.startswith(SELECTOR) else METHOD
        key = function[len(marker) :]
        members = self._member(self._value(node.args[0]), key)
        return members if marker == SELECTOR else {CALLED + item for item in members}

    def _produce(self, function: str, node: ast.Call) -> set[str]:
        for handler in (self._get, self._select):
            if (value := handler(function, node)) is not None:
                return value
        if function == "builtins.type":
            return self._value(node.args[0]) if node.args else {UNKNOWN}
        special = {"argparse.ArgumentParser": PARSER, f"{PARSER}.add_subparsers": SUBPARSERS}
        return {CONTROLLED if function in DYNAMIC else special.get(function, UNKNOWN)}

    def _call_value(self, node: ast.Call) -> set[str]:
        if isinstance(node.func, ast.Attribute) and node.func.attr in {"get", "__getitem__"}:
            values = self._value(node.func.value)
            if any(item.startswith(ITEM) for item in values):
                return self._container_items(values)
        functions, output = self._value(node.func), set()
        for raw in functions:
            derived, function = raw.startswith(DERIVED), _plain(raw)
            result = self._produce(function, node)
            output.update({DERIVED + item if derived and item != CONTROLLED else item for item in result})
        return output or {UNKNOWN}

    def _collect(self, nodes: Any, tag: str) -> set[str]:
        return {tag + (_plain(x) if tag == DERIVED else x) for node in nodes for x in self._value(node)} or {UNKNOWN}

    def _compound(self, node: ast.AST) -> set[str]:
        if isinstance(node, (ast.List, ast.Tuple, ast.Set, ast.Dict)):
            nodes = node.values if isinstance(node, ast.Dict) else node.elts
            return self._collect(nodes, ITEM)
        if isinstance(node, ast.Subscript):
            symbols = self._value(node.value)
            mappings = {item for item in symbols if _plain(item).startswith(MAPPING)}
            return self._member(mappings, node.slice) if mappings else self._container_items(symbols)
        if isinstance(node, (ast.IfExp, ast.BoolOp)):
            choices = [node.body, node.orelse] if isinstance(node, ast.IfExp) else node.values
            return self._collect(choices, DERIVED)
        return self._collect(ast.iter_child_nodes(node), "")

    def _value(self, node: ast.AST | None) -> set[str]:
        if node is None:
            return {UNKNOWN}
        if isinstance(node, ast.Name):
            builtin = f"builtins.{node.id}"
            return self.aliases.get(node.id, {builtin} if builtin in BUILTINS else {UNKNOWN})
        if literal := self._literal(node):
            return {LITERAL + literal}
        if isinstance(node, ast.Attribute):
            return self._attribute(self._value(node.value), node.attr)
        if isinstance(node, ast.NamedExpr):
            values = {DERIVED + _plain(item) for item in self._value(node.value)}
            self._bind(node.target, values)
            return values
        if isinstance(node, ast.Call):
            return self._call_value(node)
        return self._compound(node)

    def _risky(self, values: set[str]) -> bool:
        governed = self.targets or self.class_values
        prefixes = {item.rpartition(".")[0] for item in governed}
        subjects = {_plain(item).removeprefix(CALLED).removeprefix(MAPPING).removeprefix(GETTER) for item in values}
        return CONTROLLED in values or bool(subjects & (governed | prefixes | DYNAMIC))

    def _bind(self, target: ast.expr, values: set[str]) -> None:
        need(isinstance(target, ast.Name) or not self._risky(values), "policy alias target is dynamic")
        if not isinstance(target, ast.Name):
            return
        public = target.id[:1].isupper() and not target.id.isupper()
        clean = {_plain(item) for item in values}
        need(not public or values == clean and clean <= self.class_values, "public class is unclassified")
        self.aliases[target.id] = values
        if self.scope:
            self.aliases[f"{self.scope}.{target.id}"] = values
        self.classes.update(clean & self.class_values if public else set())

    def _assign(self, value: ast.AST | None, targets: list[ast.expr]) -> None:
        for target in targets:
            if isinstance(target, (ast.List, ast.Tuple)) and isinstance(value, (ast.List, ast.Tuple)):
                need(len(target.elts) == len(value.elts), "assignment shape differs")
                for left, right in zip(target.elts, value.elts, strict=True):
                    self._bind(left, {DERIVED + _plain(item) for item in self._value(right)})
            else:
                self._bind(target, self._value(value))

    def _branches(self, branches: list[list[ast.stmt]]) -> None:
        prior, states = self.aliases.copy(), []
        for branch in branches:
            self.aliases = prior.copy()
            for item in branch:
                self.visit(item)
            states.append(self.aliases)
        keys = set(prior).union(*(set(state) for state in states))
        self.aliases = {
            key: set().union(*(state.get(key, prior.get(key, {UNKNOWN})) for state in states)) for key in keys
        }

    def visit_Import(self, node: ast.Import) -> None:
        for item in node.names:
            self.aliases[item.asname or item.name.split(".")[0]] = {item.name}

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        governed = self.prefixes | {"argparse", "builtins", "importlib"}
        for item in node.names:
            need(item.name != "*" or node.module not in governed, "governed wildcard import differs")
            if item.name == "*":
                continue
            local, canonical = item.asname or item.name, f"{node.module}.{item.name}"
            self.aliases[local] = {canonical}
            if node.module != "typing" and item.name[:1].isupper() and not local.isupper():
                self.class_values.add(canonical)
                self.classes.update(() if local.startswith("_") else (canonical,))

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for header in [*node.bases, *node.decorator_list]:
            self.visit(header)
        prior, outer = self.aliases.copy(), self.scope
        qualified = f"{outer}.{node.name}" if outer else node.name
        self.aliases[node.name], self.scope = {qualified}, qualified
        self.class_values.add(qualified)
        self.classes.update(() if node.name.startswith("_") else (qualified,))
        for item in node.body:
            self.visit(item)
        scoped = {key: value for key, value in self.aliases.items() if key.startswith(f"{qualified}.")}
        self.aliases, self.scope = prior | {node.name: {qualified}} | scoped, outer

    def visit_Assign(self, node: ast.Assign | ast.AnnAssign | ast.NamedExpr) -> None:
        self._assign(node.value, node.targets if isinstance(node, ast.Assign) else [node.target])
        if node.value:
            self.visit(node.value)

    visit_NamedExpr = visit_AnnAssign = visit_Assign

    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        defaults = [*node.args.defaults, *(item for item in node.args.kw_defaults if item), *node.decorator_list]
        need(not any(self._risky(self._value(item)) for item in defaults), "parameter default differs")
        self.visit(node.args)
        prior = self.aliases.copy()
        for item in ast.walk(node.args):
            if isinstance(item, ast.arg):
                self.aliases[item.arg] = {UNKNOWN}
        for item in node.body:
            self.visit(item)
        receivers = {key: value for key, value in self.aliases.items() if SUBPARSERS in value}
        self.aliases = prior | receivers
        self._bind(ast.Name(id=node.name), {UNKNOWN})

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_If(self, node: ast.If) -> None:
        self.visit(node.test)
        self._branches([node.body, node.orelse])

    def visit_For(self, node: ast.For | ast.AsyncFor | ast.While) -> None:
        self.visit(node.test if isinstance(node, ast.While) else node.iter)
        self._branches([node.body + node.orelse, node.orelse])

    visit_AsyncFor = visit_While = visit_For

    def visit_Try(self, node: ast.Try) -> None:
        self._branches([node.body + node.orelse, *(item.body for item in node.handlers), []])
        for item in node.finalbody:
            self.visit(item)

    def visit_Match(self, node: ast.Match) -> None:
        self.visit(node.subject)
        self._branches([*(item.body for item in node.cases), []])

    def visit_Call(self, node: ast.Call) -> None:
        functions, result = self._value(node.func), self._call_value(node)
        hits = {_plain(item) for item in functions if _plain(item) in self.targets}
        hits.update(_plain(item)[len(CALLED) :] for item in result if _plain(item).startswith(CALLED))
        self.calls.extend((item, node) for item in hits if item in self.targets)
        need(CONTROLLED not in functions | result, "controlled call is ambiguous")
        passed = any(self._risky(self._value(item)) for item in node.args)
        safe = {_plain(item) for item in functions} <= BUILTINS | SAFE_CALLS | self.targets
        need(not passed or safe, "controlled argument differs")
        self.generic_visit(node)


def policy_calls(source: str, targets: set[str]) -> list[tuple[str, ast.Call]]:
    visitor = _Symbols(targets)
    visitor.visit(ast.parse(source))
    return visitor.calls


def cli_surface(source: str) -> set[str]:
    calls = [call for _, call in policy_calls(source, {f"{SUBPARSERS}.add_parser"})]
    need(
        all(len(call.args) == 1 and not call.keywords and isinstance(call.args[0], ast.Constant) for call in calls),
        "CLI is ambiguous",
    )
    names = [cast(str, cast(ast.Constant, call.args[0]).value) for call in calls]
    need(len(names) == len(set(names)) and set(names) == {"project-integrity", "turn-handoff-integrity"}, "CLI differs")
    return cast(set[str], set(names))


def class_surface(source: str) -> set[str]:
    visitor = _Symbols(set())
    visitor.visit(ast.parse(source))
    return visitor.classes


def _decision(node: ast.AST) -> int:
    if isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.IfExp, ast.Assert)):
        return 1
    if isinstance(node, ast.BoolOp):
        return len(node.values) - 1
    if isinstance(node, ast.Try):
        return len(node.handlers) + int(bool(node.orelse))
    if isinstance(node, ast.comprehension):
        return 1 + len(node.ifs)
    if isinstance(node, ast.Match):
        return max(0, len(node.cases) - 1)
    return 0


def _nesting(node: ast.AST) -> int:
    controls = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith, ast.Match)
    maximum, pending = 0, [(node, 0)]
    while pending:
        current, depth = pending.pop()
        child_depth = depth + int(isinstance(current, controls))
        maximum = max(maximum, child_depth)
        pending.extend((child, child_depth) for child in ast.iter_child_nodes(current))
    return maximum


def _stub(node: ast.AST) -> bool:
    ellipsis = isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and node.value.value is Ellipsis
    return isinstance(node, ast.Pass) or ellipsis


def _logical(values: list[str]) -> int:
    return sum(bool(line.strip()) and not line.lstrip().startswith("#") for line in values)


def validate_python(path: str, source: str) -> None:
    lines, tree = source.splitlines(), ast.parse(source, filename=path)
    need(_logical(lines) <= 500 and all(len(line) <= 120 for line in lines), f"module violates DR-30: {path}")
    for node in ast.walk(tree):
        need(not _stub(node), f"production stub: {path}")
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        size = _logical(lines[node.lineno - 1 : node.end_lineno])
        if isinstance(node, ast.ClassDef):
            need(size <= 250, f"class violates DR-30: {path}:{node.lineno}")
        else:
            complexity = 1 + sum(_decision(item) for item in ast.walk(node))
            need(
                size <= 60 and complexity <= 10 and _nesting(node) <= 3,
                f"function violates DR-30: {path}:{node.lineno}",
            )
