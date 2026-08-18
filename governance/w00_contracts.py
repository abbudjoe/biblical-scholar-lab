import ast
import hashlib
import json
import math
import re
from datetime import datetime
from typing import Any, cast

import jsonschema

REPOSITORY = "abbudjoe/biblical-scholar-lab"
BRANCH = "codex/w00-repository-governance"
ACTIVATION = "ACT-W00-REPOSITORY-GOVERNANCE-v3"
BASE = "3d3ebb706fe6c8779445cbbfd9fea271b86d3646"
ROOT = "/Users/joseph/biblical-scholar-lab"
PR_URL = f"https://github.com/{REPOSITORY}/pull/1"
PR_TITLE = "W00A1: local governance kernel and defense checks"
PROHIBITED_JSON = re.compile(r"\b(?:approv\w*|authoriz\w*|billable\w*|merg\w*|ready|safe|w00a2|w00b|w01)\b")
CONTRADICTORY_MARKDOWN = re.compile(
    r"\b(?:(?:pr|pull request).{0,40}(?:already|has|was).{0,20}merged|w01.{0,20}(?:started|underway)|"
    r"(?:safe|can|may|ready).{0,30}merg\w*|owner authorization.{0,20}(?:active|implemented))\b"
)
REQUIRED_FINDINGS = set(
    "R0-P1-TRUST-PROVENANCE R1-F2 R2-F4 R3-F3 R4-F1 R5-F1 R6-F7 R7-F5 R8-F6 "
    "R02-P2-STRICT-CONTENT R02-P2-HANDOFF-EVIDENCE R02-P2-CLAIMS R02-P2-CODEOWNERS "
    "R02-P2-QUALITY-SPEC R02-P1-ABSTRACTIONS R02-P2-DR30 P2-01 P2-02 P2-03 P2-04 P2-05 P2-06 "
    "R03-P2-WORKFLOW R03-P2-CHRONOLOGY R03-P2-PROTOCOL R03-P2-DISPOSITION "
    "R03R2-P2-SCHEMA R03R2-P2-ALIAS R03R2-P2-LEDGER R03R2-P2-STUB "
    "R03R2-P3-PROTOCOL-COVERAGE R03R2-P3-TOOL-INVENTORY".split()
)
P1_FINDINGS = {"R0-P1-TRUST-PROVENANCE", "R1-F2", "R2-F4", "R3-F3", "R02-P1-ABSTRACTIONS"}
P3_FINDINGS = {"R03R2-P3-PROTOCOL-COVERAGE", "R03R2-P3-TOOL-INVENTORY"}
SPLIT_FINDINGS = {"R0-P1-TRUST-PROVENANCE", "R2-F4", "R5-F1", "R6-F7", "R02-P2-CODEOWNERS"}
EXTERNAL_TOOLS = "coverage==7.10.6 detect-secrets==1.5.0 mypy==2.3.1 radon==6.0.1 ruff==0.16.3 zizmor==1.29.0".split()
CONTROLLED, LITERAL, SELECTOR, UNKNOWN = "<controlled>", "<literal>:", "<selector>:", "<unknown>"
GETTERS = {"getattr", "builtins.getattr", "inspect.getattr_static", "object.__getattribute__", "type.__getattribute__"}
FACTORIES = {"dict.get", "operator.attrgetter", "operator.methodcaller", "type", "builtins.type"}
BUILTINS = set("__import__ dict eval exec getattr globals locals object setattr type vars".split())
PROSE_FIELDS = "objective acceptance_criteria changes review_targets known_risks decisions_required".split()
PROSE_FIELDS += "complexity_receipt evaluations artifacts delegated_operations".split()
STAGE_PATHS = set(
    ".github/workflows/governance-integrity.yml governance/GOV-01-artifacts.sha256 "
    "governance/GOV-01-package-manifest.json governance/ruff.toml governance/schemas/turn-handoff.schema.json "
    "governance/test_w00_checks.py governance/w00_checks.py governance/w00_contracts.py governance/w00_yaml.rb".split()
)
PYTHON_FILES = ("governance/w00_contracts.py", "governance/w00_checks.py", "governance/test_w00_checks.py")
UV_PYTHON = ("uv", "run", "--with", "jsonschema==4.25.1", "--")
UV_COVERAGE = (*UV_PYTHON[:-1], "--with", "coverage==7.10.6", "--")
VALIDATION_ARGV = (
    (*UV_PYTHON, "python3", "-m", "unittest", "-v", PYTHON_FILES[-1]),
    (*UV_PYTHON, "python3", "-m", "py_compile", *PYTHON_FILES[:-1]),
    (*UV_COVERAGE, "python3", "-m", "coverage", "run", "--branch", "-m", "unittest", PYTHON_FILES[-1]),
    (*UV_COVERAGE, "python3", "-m", "coverage", "report", "--fail-under=90", *PYTHON_FILES[:-1]),
    ("uvx", "ruff@0.16.3", "check", "--config", "governance/ruff.toml", *PYTHON_FILES),
    ("uvx", "ruff@0.16.3", "format", "--check", "--config", "governance/ruff.toml", *PYTHON_FILES),
    ("uvx", "mypy@2.3.1", "--strict", "--ignore-missing-imports", *PYTHON_FILES[:-1]),
    ("uvx", "detect-secrets@1.5.0", "scan", "--all-files"),
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


def _command(item: dict[str, Any], identity: tuple[str, str, str]) -> None:
    keys = ("root_turn_id", "activation_id", "implementation_head_sha")
    need(tuple(item[key] for key in keys) == identity, "command identity differs")
    need(assess_argv(item["argv"]), "argv is not allowlisted")
    need(item["working_directory"] == ROOT, "working directory differs")
    times = [datetime.fromisoformat(item[key].replace("Z", "+00:00")) for key in ("started_at", "finished_at")]
    need(times[0] <= times[1], "command time order differs")
    need((item["exit_code"] == 0) == (item["result"] == "PASS"), "command result differs")
    need(_command_digest(item) == item["combined_evidence_artifact_sha256"], "command artifact binding differs")


def _commands(items: list[dict[str, Any]], identity: tuple[str, str, str]) -> None:
    for item in items:
        _command(item, identity)
    identities = [{item[key] for item in items} for key in ("command_evidence_id", "combined_evidence_artifact_sha256")]
    need(all(len(values) == len(items) for values in identities), "command evidence is reused")


def finding_state(finding: str) -> tuple[str, str]:
    severity = "P1" if finding in P1_FINDINGS else "P3" if finding in P3_FINDINGS else "P2"
    status = "SUPERSEDED_BY_APPROVED_SPLIT" if finding in SPLIT_FINDINGS else "CLOSED"
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
    need(record["changes"] and record["review_targets"] and record["commands"], "required evidence is empty")
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
    prose = json.dumps({key: record[key] for key in PROSE_FIELDS}, sort_keys=True, separators=(",", ":")).casefold()
    need(len(prose) <= 262_144, "record prose is unbounded")
    need(PROHIBITED_JSON.search(prose) is None, "JSON prose restates terminal facts")


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
    head = values["--head-sha"]
    valid_head = head == "HEAD" or re.fullmatch(r"[0-9a-f]{40}", head)
    identity = values["--base-sha"], values["--branch"], values.get("--pr-url", PR_URL)
    return bool(valid_head and identity == (BASE, BRANCH, PR_URL))


def _literal(node: ast.AST | None, aliases: dict[str, str]) -> str | None:
    if isinstance(node, ast.Constant):
        return node.value if isinstance(node.value, str) else None
    if isinstance(node, ast.Name):
        value = aliases.get(node.id, "")
        return value[len(LITERAL) :] if value.startswith(LITERAL) else None
    if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Add):
        return None
    left, right = _literal(node.left, aliases), _literal(node.right, aliases)
    return left + right if left is not None and right is not None else None


def _carrier(symbol: str) -> bool:
    known = symbol in GETTERS | FACTORIES or symbol.startswith(SELECTOR)
    return known or symbol.endswith((".__dict__", ".__getattribute__")) or ".__dict__." in symbol


def _text(symbol: str | None) -> str:
    return symbol if symbol is not None else ""


def _indirect(node: ast.AST, aliases: dict[str, str]) -> str | None:
    if isinstance(node, ast.Subscript):
        base, key = _text(_resolve(node.value, aliases)), _literal(node.slice, aliases)
        if base.endswith(".__dict__") and key is not None:
            return f"{base.rpartition('.')[0]}.{key}"
    if not isinstance(node, ast.Call):
        return None
    function = _text(_resolve(node.func, aliases))
    if function.endswith(".add_subparsers"):
        return "*"
    if not node.args:
        return None
    if function in {"operator.attrgetter", "operator.methodcaller"}:
        return SELECTOR + _text(_literal(node.args[0], aliases))
    return _resolve(node.args[0], aliases) if function in {"type", "builtins.type"} else None


def _resolve(node: ast.AST | None, aliases: dict[str, str]) -> str | None:
    if isinstance(node, ast.Name):
        return aliases.get(node.id, node.id if node.id in BUILTINS else UNKNOWN)
    if isinstance(node, ast.Attribute):
        base = _resolve(node.value, aliases)
        return base if base in {None, CONTROLLED} else f"{base}.{node.attr}"
    literal = _literal(node, aliases)
    return LITERAL + literal if literal is not None else _indirect(node, aliases) if node is not None else None


def _matches(name: str | None, values: set[str]) -> bool:
    return name is not None and any(name == item or item.startswith("*") and name.endswith(item[1:]) for item in values)


def _positional_access(function: str, node: ast.Call, aliases: dict[str, str]) -> tuple[str | None, str | None] | None:
    if function not in GETTERS | {"dict.get"} or len(node.args) < 2:
        return None
    base = _resolve(node.args[0], aliases)
    base = base.removesuffix(".__dict__") if function == "dict.get" and base else base
    return base, _resolve(node.args[1], aliases)


def _access(node: ast.AST, aliases: dict[str, str]) -> tuple[str | None, str | None] | None:
    if isinstance(node, ast.Subscript):
        base = _text(_resolve(node.value, aliases))
        return (base.rpartition(".")[0], _resolve(node.slice, aliases)) if base.endswith(".__dict__") else None
    if not isinstance(node, ast.Call):
        return None
    function = _text(_resolve(node.func, aliases))
    if access := _positional_access(function, node, aliases):
        return access
    if not node.args:
        return None
    if function.endswith(".__dict__.get"):
        return function.removesuffix(".__dict__.get"), _resolve(node.args[0], aliases)
    if function.endswith(".__getattribute__"):
        return function.removesuffix(".__getattribute__"), _resolve(node.args[0], aliases)
    if function.startswith(SELECTOR):
        key = LITERAL + function[len(SELECTOR) :] if len(function) > len(SELECTOR) else UNKNOWN
        return _resolve(node.args[0], aliases), key
    return None


def _governed(access: tuple[str | None, str | None], values: set[str]) -> bool:
    base, key = access
    prefixes = {value.rpartition(".")[0] for value in values}
    if base not in prefixes:
        return False
    if key is None or key == UNKNOWN or key.startswith(f"{UNKNOWN}."):
        return True
    literal = key[len(LITERAL) :] if key.startswith(LITERAL) else None
    return literal is not None and _matches(f"{base}.{literal}", values)


def _controlled(node: ast.AST, aliases: dict[str, str], values: set[str]) -> bool:
    for item in ast.walk(node):
        resolved = _resolve(item, aliases)
        if resolved == CONTROLLED or _matches(resolved, values):
            return True
        if (access := _access(item, aliases)) and _governed(access, values):
            return True
    return False


def _symbols(node: ast.AST, aliases: dict[str, str]) -> set[str]:
    nested = {id(item.value) for item in ast.walk(node) if isinstance(item, ast.Attribute)}
    return {symbol for item in ast.walk(node) if id(item) not in nested and (symbol := _resolve(item, aliases))}


def _choice(symbols: set[str], values: set[str]) -> str:
    carriers = {symbol for symbol in symbols if _carrier(symbol)}
    choices = carriers or symbols & {value.rpartition(".")[0] for value in values}
    return next(iter(choices)) if len(choices) == 1 else CONTROLLED if choices else UNKNOWN


def _taint(node: ast.AST, aliases: dict[str, str], values: set[str]) -> str:
    if isinstance(node, ast.Call) and _matches(_resolve(node.func, aliases), values):
        return UNKNOWN
    return CONTROLLED if _controlled(node, aliases, values) else _choice(_symbols(node, aliases), values)


def _risky(resolved: str | None, values: set[str]) -> bool:
    prefixes = {value.rpartition(".")[0] for value in values}
    return _matches(resolved, values) or resolved in prefixes or bool(resolved and _carrier(resolved))


def _ambiguous_call(
    node: ast.Call, resolved: str | None, state: str, values: set[str], aliases: dict[str, str], strict: bool
) -> bool:
    computed = not isinstance(node.func, (ast.Name, ast.Attribute))
    hidden = not isinstance(node.func, ast.Call) and (_matches(resolved, values) or _carrier(state))
    if strict:
        if resolved == CONTROLLED:
            return True
        if resolved is None and state == CONTROLLED:
            return True
        if computed and hidden:
            return True
    access = _access(node, aliases)
    return bool(access and _governed(access, values))


def _public_alias(target: ast.expr) -> bool:
    return isinstance(target, ast.Name) and target.id[:1].isupper() and not target.id.isupper()


class _Symbols(ast.NodeVisitor):
    def __init__(self, targets: set[str]) -> None:
        self.targets = targets
        self.aliases: dict[str, str] = {}
        self.calls: list[tuple[str, ast.Call]] = []
        self.class_values, self.classes = cast(tuple[set[str], set[str]], (set(), set()))

    def visit_Import(self, node: ast.Import) -> None:
        for item in node.names:
            self.aliases[item.asname or item.name.split(".")[0]] = item.name

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for item in node.names:
            local, canonical = item.asname or item.name, f"{node.module}.{item.name}"
            self.aliases[local] = canonical
            if node.module != "typing" and item.name[:1].isupper():
                self.class_values.add(canonical)
                self.classes.update(() if local.startswith("_") else (canonical,))

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.aliases[node.name] = node.name
        self.class_values.add(node.name)
        self.classes.update(() if node.name.startswith("_") else (node.name,))
        self.generic_visit(node)

    def _assign(self, value: ast.AST | None, targets: list[ast.expr]) -> None:
        resolved = _resolve(value, self.aliases)
        if resolved is None and value is not None:
            resolved = _taint(value, self.aliases, self.targets or self.class_values)
        for target in targets:
            self._bind(target, resolved)

    def _bind(self, target: ast.expr, resolved: str | None) -> None:
        controlled = resolved in self.class_values or _risky(resolved, self.targets or self.class_values)
        public = _public_alias(target)
        need(not controlled or isinstance(target, ast.Name), "policy alias target is dynamic")
        need(not public or resolved in self.class_values, "public class is unclassified")
        if not resolved or not isinstance(target, ast.Name):
            return
        self.aliases[target.id] = resolved
        self.classes.update((resolved,) if resolved in self.class_values and not target.id.startswith("_") else ())

    def visit_Assign(self, node: ast.Assign) -> None:
        self._assign(node.value, node.targets)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._assign(node.value, [node.target])
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        prior = self.aliases.copy()
        self.aliases.update({item.arg: UNKNOWN for item in ast.walk(node.args) if isinstance(item, ast.arg)})
        self.generic_visit(node)
        receivers = {name: value for name, value in self.aliases.items() if value == "*"}
        self.aliases = prior | receivers | {node.name: UNKNOWN}

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node: ast.Call) -> None:
        resolved = _resolve(node.func, self.aliases)
        values = self.targets or self.class_values
        state = _taint(node.func, self.aliases, values)
        ambiguous = _ambiguous_call(node, resolved, state, values, self.aliases, bool(self.targets))
        need(not ambiguous, "computed call target is unclassified")
        dynamic = {"__import__", "eval", "exec", "globals", "importlib.import_module", "locals", "setattr", "vars"}
        need((resolved or "").removeprefix("builtins.") not in dynamic, "dynamic policy code differs")
        if _matches(resolved, self.targets):
            self.calls.append((cast(str, resolved), node))
        self.generic_visit(node)


def policy_calls(source: str, targets: set[str]) -> list[tuple[str, ast.Call]]:
    visitor = _Symbols(targets)
    visitor.visit(ast.parse(source))
    return visitor.calls


def cli_surface(source: str) -> set[str]:
    calls = [call for _, call in policy_calls(source, {"*.add_parser"})]
    need(all(len(call.args) == 1 and not call.keywords for call in calls), "CLI is ambiguous")
    need(all(isinstance(call.args[0], ast.Constant) for call in calls), "CLI is ambiguous")
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


def _cyclomatic(node: ast.AST) -> int:
    return 1 + sum(_decision(item) for item in ast.walk(node))


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


def validate_python(path: str, source: str) -> None:
    lines, tree = source.splitlines(), ast.parse(source, filename=path)

    def logical(values: list[str]) -> int:
        return sum(bool(line.strip()) and not line.lstrip().startswith("#") for line in values)

    need(logical(lines) <= 500 and all(len(line) <= 120 for line in lines), f"module violates DR-30: {path}")
    for node in ast.walk(tree):
        need(not _stub(node), f"production stub: {path}")
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        size = logical(lines[node.lineno - 1 : node.end_lineno])
        if isinstance(node, ast.ClassDef):
            need(size <= 250, f"class violates DR-30: {path}:{node.lineno}")
        else:
            need(
                size <= 60 and _cyclomatic(node) <= 10 and _nesting(node) <= 3,
                f"function violates DR-30: {path}:{node.lineno}",
            )
