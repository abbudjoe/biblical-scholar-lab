from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from dataclasses import fields
from typing import Any, cast

from bsl.application.vs01_benchmark import (
    ReferenceSubjectFixture,
    StructuredSubjectResponse,
    SubjectCasePackage,
    canonical_sha256,
    guard_real_case,
)


def _tuples(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_tuples(item) for item in cast(list[Any], value))
    if isinstance(value, dict):
        return {key: _tuples(item) for key, item in cast(dict[str, Any], value).items()}
    return value


def _record(model: type[Any], value: object) -> Any:
    if not isinstance(value, dict) or set(cast(dict[str, Any], value)) != {item.name for item in fields(model)}:
        raise ValueError("reference subject input record differs")
    return model(**cast(dict[str, Any], _tuples(value)))


def _execute(case: SubjectCasePackage, fixture: ReferenceSubjectFixture) -> StructuredSubjectResponse:
    exact = (
        case.case_id == fixture.case_id,
        case.source_declared_compatibility_sha256 == fixture.source_declared_compatibility_sha256,
        case.execution_rfc8785_jcs_sha256 == fixture.execution_rfc8785_jcs_sha256,
        case.package_identity == canonical_sha256(case.payload(include_identity=False)),
        fixture.response_payload_sha256 == canonical_sha256(fixture.response_payload),
        tuple(name for name, _value in fixture.response_payload) == case.response_fields,
    )
    if not all(exact):
        raise ValueError("reference subject case, projection, or fixture identity differs")
    return StructuredSubjectResponse(
        case.case_id,
        case.source_declared_compatibility_sha256,
        case.execution_rfc8785_jcs_sha256,
        case.package_identity,
        fixture.response_payload,
        fixture.response_payload_sha256,
    )


class DeterministicReferenceSubjectAdapter:
    def __init__(self, fixture: ReferenceSubjectFixture, *, implementation_evidence_mode: bool = False) -> None:
        self._fixture = fixture
        self._implementation_evidence_mode = implementation_evidence_mode

    def generate(self, case: SubjectCasePackage) -> StructuredSubjectResponse:
        guard_real_case(case.case_id, "subject", implementation_evidence_mode=self._implementation_evidence_mode)
        request = json.dumps({"case": case.payload(), "fixture": self._fixture.payload()}, ensure_ascii=False).encode()
        with tempfile.TemporaryDirectory(prefix="bsl-vs01-t07-subject-") as directory:
            completed = subprocess.run(
                [sys.executable, "-I", "-m", "bsl.application.vs01_reference_subject"],
                input=request,
                capture_output=True,
                check=False,
                timeout=30,
                cwd=directory,
                env={"PYTHONUTF8": "1"},
            )
        if completed.returncode or completed.stderr:
            raise ValueError("reference subject subprocess failed")
        try:
            return cast(StructuredSubjectResponse, _record(StructuredSubjectResponse, json.loads(completed.stdout)))
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
            raise ValueError("reference subject subprocess returned malformed output") from None


def main() -> int:
    try:
        request = cast(object, json.loads(sys.stdin.buffer.read()))
        if not isinstance(request, dict) or set(cast(dict[str, object], request)) != {"case", "fixture"}:
            raise ValueError("reference subject request differs")
        values = cast(dict[str, object], request)
        case = cast(SubjectCasePackage, _record(SubjectCasePackage, values["case"]))
        fixture = cast(ReferenceSubjectFixture, _record(ReferenceSubjectFixture, values["fixture"]))
        sys.stdout.buffer.write(json.dumps(_execute(case, fixture).payload(), ensure_ascii=False).encode())
        return 0
    except (KeyError, TypeError, ValueError):
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
