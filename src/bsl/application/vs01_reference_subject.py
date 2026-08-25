from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, cast

from bsl.application.vs01_benchmark import (
    ReferenceSubjectFixture,
    StructuredSubjectResponse,
    SubjectCasePackage,
    canonical_sha256,
    guard_real_case,
)

CHILD_SOURCE = r"""import hashlib
import json
import sys

def digest(value):
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

try:
    request = json.loads(sys.stdin.buffer.read())
    names = [item[0] for item in request["oracle_response_payload"]]
    valid = set(request) == {
        "case_id", "source_declared_compatibility_sha256", "execution_rfc8785_jcs_sha256",
        "subject_package_identity", "response_field_names", "oracle_response_payload",
        "oracle_response_payload_sha256"
    }
    valid = valid and names == request["response_field_names"]
    valid = valid and digest(request["oracle_response_payload"]) == request["oracle_response_payload_sha256"]
    if not valid:
        raise ValueError
    reply = {
        "case_id": request["case_id"],
        "source_declared_compatibility_sha256": request["source_declared_compatibility_sha256"],
        "execution_rfc8785_jcs_sha256": request["execution_rfc8785_jcs_sha256"],
        "subject_package_identity": request["subject_package_identity"],
        "response_payload": request["oracle_response_payload"],
        "response_payload_sha256": request["oracle_response_payload_sha256"],
        "attempt_state": "COMPLETED"
    }
    sys.stdout.buffer.write(json.dumps(reply, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
except (KeyError, TypeError, ValueError, json.JSONDecodeError):
    raise SystemExit(2)
"""
CHILD_SHA256 = hashlib.sha256(CHILD_SOURCE.encode()).hexdigest()
CHILD_IMPORTS = frozenset(
    node.names[0].name for node in ast.walk(ast.parse(CHILD_SOURCE)) if isinstance(node, ast.Import)
)


def _request(case: SubjectCasePackage, fixture: ReferenceSubjectFixture) -> dict[str, Any]:
    exact = (
        case.case_id == fixture.case_id,
        case.source_declared_compatibility_sha256 == fixture.source_declared_compatibility_sha256,
        case.execution_rfc8785_jcs_sha256 == fixture.execution_rfc8785_jcs_sha256,
        case.package_identity == canonical_sha256(case.payload(include_identity=False)),
        fixture.response_payload_sha256 == canonical_sha256(fixture.response_payload),
        tuple(name for name, _ in fixture.response_payload) == case.response_fields,
    )
    if not all(exact):
        raise ValueError("reference subject case, projection, or fixture identity differs")
    return {
        "case_id": case.case_id,
        "source_declared_compatibility_sha256": case.source_declared_compatibility_sha256,
        "execution_rfc8785_jcs_sha256": case.execution_rfc8785_jcs_sha256,
        "subject_package_identity": case.package_identity,
        "response_field_names": case.response_fields,
        "oracle_response_payload": fixture.response_payload,
        "oracle_response_payload_sha256": fixture.response_payload_sha256,
    }


def _parse_response(value: bytes) -> StructuredSubjectResponse:
    try:
        payload = cast(dict[str, Any], json.loads(value))
        payload["response_payload"] = tuple(tuple(item) for item in payload["response_payload"])
        response = StructuredSubjectResponse(**payload)
    except (KeyError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("reference subject subprocess returned malformed output") from None
    if response.response_payload_sha256 != canonical_sha256(response.response_payload):
        raise ValueError("reference subject subprocess returned invalid identity")
    return response


class DeterministicReferenceSubjectAdapter:
    def __init__(self, fixture: ReferenceSubjectFixture, *, implementation_evidence_mode: bool = False) -> None:
        self._fixture = fixture
        self._implementation_evidence_mode = implementation_evidence_mode

    def generate(self, case: SubjectCasePackage) -> StructuredSubjectResponse:
        guard_real_case(case.case_id, "subject", implementation_evidence_mode=self._implementation_evidence_mode)
        request = json.dumps(_request(case, self._fixture), ensure_ascii=False, separators=(",", ":")).encode()
        with tempfile.TemporaryDirectory(prefix="bsl-vs01-t07-subject-") as directory:
            script = Path(directory) / "subject.py"
            script.write_text(CHILD_SOURCE, encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "-I", "-S", "-X", "utf8", str(script)],
                input=request,
                capture_output=True,
                check=False,
                timeout=30,
                cwd=directory,
                env={"PYTHONUTF8": "1", "LC_ALL": "C.UTF-8"},
            )
        if completed.returncode or completed.stderr:
            raise ValueError("reference subject subprocess failed")
        response = _parse_response(completed.stdout)
        expected = StructuredSubjectResponse(
            case.case_id,
            case.source_declared_compatibility_sha256,
            case.execution_rfc8785_jcs_sha256,
            case.package_identity,
            self._fixture.response_payload,
            self._fixture.response_payload_sha256,
        )
        if response != expected:
            raise ValueError("reference subject subprocess response differs")
        return response
