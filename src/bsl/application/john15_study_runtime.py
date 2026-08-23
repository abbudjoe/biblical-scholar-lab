from __future__ import annotations

import hashlib
import os
import stat
import subprocess
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol
from uuid import UUID

import rfc8785
from pydantic import ValidationError
from uuid6 import uuid7

from bsl.application.john15_evidence import CANONICAL_ARCHIVE_ROOT, _require_root  # pyright: ignore[reportPrivateUsage]
from bsl.contracts.evidence import John15TranslationNuanceEvidencePacket, John15TranslationNuanceEvidenceReceipt
from bsl.contracts.runtime import (
    ACTIVE_REQUEST_IDENTITY,
    PACKET_IDENTITY,
    PACKET_RECEIPT_IDENTITY,
    PACKET_RECEIPT_SHA256,
    PACKET_SHA256,
    SPEC_SHA256,
    John15RuntimeAuditReceipt,
    John15StudyAnswerArtifact,
    John15StudyExecutionRecord,
    John15StudyRequest,
    canonical_sha256,
    load_runtime_spec,
)

OBJECT_PATH = f"objects/sha256/{PACKET_SHA256[:2]}/{PACKET_SHA256}"
SNAPSHOT_PATH = "snapshots/evidence/john-1-5-translation-nuance.json"
RECEIPT_PATH = "manifests/evidence/john-1-5-translation-nuance/evidence-packet-receipt.json"
T04_IMPLEMENTATION_COMMIT = "7db0ff4a1ade89c043a9330b89de90467dba612c"


class ScholarModelAdapter(Protocol):
    def propose_candidate(
        self, request: John15StudyRequest, plan: dict[str, Any], packet: John15TranslationNuanceEvidencePacket
    ) -> dict[str, Any]: ...


@dataclass(frozen=True)
class _T04Authority:
    root: Path
    packet: John15TranslationNuanceEvidencePacket
    receipt: John15TranslationNuanceEvidenceReceipt
    receipt_file_sha256: str


@dataclass(frozen=True)
class StudyRuntimeResult:
    request: John15StudyRequest
    execution_record: John15StudyExecutionRecord
    brief_answer: John15StudyAnswerArtifact
    study_answer: John15StudyAnswerArtifact
    audit_receipt: John15RuntimeAuditReceipt
    persisted: bool
    verified_existing: bool


def _authority_fingerprint(authority: _T04Authority) -> str:
    packet_bytes = rfc8785.dumps(authority.packet.model_dump(mode="json"))
    receipt_bytes = rfc8785.dumps(authority.receipt.model_dump(mode="json"))
    return canonical_sha256(
        {
            "root": str(authority.root.resolve(strict=True)),
            "packet_semantic_sha256": hashlib.sha256(packet_bytes).hexdigest(),
            "receipt_file_sha256": authority.receipt_file_sha256,
            "receipt_semantic_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
        }
    )


def _regular_0444(path: Path) -> tuple[bytes, str]:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
        try:
            metadata = os.fstat(fd)
            if not stat.S_ISREG(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) != 0o444:
                raise ValueError
            with os.fdopen(fd, "rb", closefd=False) as stream:
                data = stream.read()
        finally:
            os.close(fd)
    except (OSError, ValueError):
        raise ValueError(f"T04 authority is missing, symlinked, non-regular, or mutable: {path.name}") from None
    return data, hashlib.sha256(data).hexdigest()


def _path_has_no_symlink(root: Path, path: Path) -> bool:
    current = root
    for part in path.relative_to(root).parts:
        current = current / part
        if current.is_symlink():
            return False
    return True


def load_t04_authority(archive_root: Path, *, _expected_archive_root: Path = CANONICAL_ARCHIVE_ROOT) -> _T04Authority:
    root = _require_root(archive_root, _expected_archive_root)
    paths = tuple(root / relative for relative in (OBJECT_PATH, SNAPSHOT_PATH, RECEIPT_PATH))
    if not all(_path_has_no_symlink(root, path) for path in paths):
        raise ValueError("T04 authority path contains a symlink")
    object_bytes, object_sha = _regular_0444(paths[0])
    snapshot_bytes, snapshot_sha = _regular_0444(paths[1])
    receipt_bytes, receipt_sha = _regular_0444(paths[2])
    if object_bytes != snapshot_bytes or object_sha != snapshot_sha or object_sha != PACKET_SHA256:
        raise ValueError("T04 object and snapshot are not the exact published packet bytes")
    try:
        packet = John15TranslationNuanceEvidencePacket.model_validate_json(snapshot_bytes)
        receipt = John15TranslationNuanceEvidenceReceipt.model_validate_json(receipt_bytes)
    except ValidationError:
        raise ValueError("T04 packet or receipt raw JSON is invalid") from None
    expected = (
        packet.packet_identity == PACKET_IDENTITY,
        str(receipt.receipt_identity) == PACKET_RECEIPT_IDENTITY,
        receipt_sha == PACKET_RECEIPT_SHA256,
        receipt.disposition == "PUBLISHED",
        receipt.implementation_commit == T04_IMPLEMENTATION_COMMIT,
        receipt.archive_root == str(CANONICAL_ARCHIVE_ROOT),
        receipt.packet_identity == PACKET_IDENTITY,
        receipt.packet_canonical_sha256 == PACKET_SHA256,
        tuple(receipt.publication_paths) == (OBJECT_PATH, SNAPSHOT_PATH, RECEIPT_PATH),
    )
    if not all(expected):
        raise ValueError("T04 receipt does not bind the exact published authority")
    return _T04Authority(root, packet, receipt, receipt_sha)


def _verify_ledgers(packet: John15TranslationNuanceEvidencePacket, spec: dict[str, Any]) -> None:
    evidence = {item["evidence_id"]: item for item in packet.evidence_items}
    claims = {item["claim_id"]: item for item in packet.claims}
    if len(evidence) != 12 or len(claims) != 16:
        raise ValueError("T04 packet ledger IDs are missing or duplicated")
    for record in spec["evidence_ledger"]:
        source = evidence.get(record["evidence_id"])
        fields = ("evidence_id", "kind", "source_role", "selector")
        if source is None or any(source[field] != record[field] for field in fields):
            raise ValueError("runtime evidence ledger differs from T04 packet")
    for record in spec["claim_ledger"]:
        source = claims.get(record["claim_id"])
        expected = (
            None
            if source is None
            else (source["proposition"], source["epistemic_status"], source["required_qualifications"])
        )
        actual = (record["exact_proposition"], record["epistemic_status"], record["required_qualifications"])
        if expected != actual:
            raise ValueError("runtime claim ledger differs from T04 packet")


def _verify_citations(packet: John15TranslationNuanceEvidencePacket, spec: dict[str, Any]) -> None:
    evidence = {item["evidence_id"]: item for item in packet.evidence_items}
    citations = spec["citation_records"]
    if [item["citation_id"] for item in citations] != [f"CIT-T05-{number:03}" for number in range(1, 11)]:
        raise ValueError("citation IDs differ from the ten-record erratum authority")
    for citation in citations:
        source = evidence.get(citation["evidence_id"])
        if source is None or citation["selector"] != source["selector"]:
            raise ValueError("citation selector does not match T04 evidence")
        if citation["quoted_span"] != source.get("exact_excerpt"):
            raise ValueError("citation quotation does not match T04 evidence")


def _verify_candidate(packet: John15TranslationNuanceEvidencePacket, spec: dict[str, Any]) -> None:
    candidate = spec["structured_answer_candidate"]
    claims = {item["claim_id"] for item in packet.claims}
    alternatives = {item["alternative_id"] for item in packet.accepted_alternatives}
    citations = {item["citation_id"]: item["evidence_id"] for item in spec["citation_records"]}
    links = {(item["claim_id"], item["evidence_id"]) for item in packet.claim_evidence_links}
    if set(candidate["claim_ids"]) != claims - {"CLM-T04-001"} or set(candidate["alternative_ids"]) != alternatives:
        raise ValueError("candidate claims or alternatives differ from T04 authority")
    if set(candidate["citation_ids"]) != set(citations):
        raise ValueError("candidate does not reference all ten citations")
    qualifying = {"EV-T04-METHOD-001", "EV-T04-METHOD-002", "EV-T04-BOUNDARY-001"}
    for block in (*candidate["brief_blocks"], *candidate["study_blocks"]):
        block_evidence = {citations[item] for item in block["citation_ids"]}
        for claim_id in block["claim_ids"]:
            if not any((claim_id, item) in links or item in qualifying for item in block_evidence):
                raise ValueError("answer block claim lacks compatible cited evidence")


def _verified_execution(authority: _T04Authority) -> tuple[John15StudyRequest, John15StudyExecutionRecord]:
    spec = load_runtime_spec()
    _verify_ledgers(authority.packet, spec)
    _verify_citations(authority.packet, spec)
    _verify_candidate(authority.packet, spec)
    request = John15StudyRequest.model_validate(spec["canonical_request"]["active_request"])
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "contract": "John15StudyExecutionRecord",
        "request_identity": request.request_identity,
        "packet_identity": authority.packet.packet_identity,
        "packet_canonical_sha256": PACKET_SHA256,
        "packet_receipt_identity": str(authority.receipt.receipt_identity),
        "packet_receipt_file_sha256": authority.receipt_file_sha256,
        "runtime_spec_sha256": SPEC_SHA256,
        "resolved_task": spec["resolved_task"],
        "research_execution_plan": spec["research_execution_plan"],
        "runtime_state_sequence": spec["runtime_state_machine"]["principal_sequence"],
        "skipped_state_reasons": spec["runtime_state_machine"]["skip_reasons"],
        "evidence_ledger": spec["evidence_ledger"],
        "claim_ledger": spec["claim_ledger"],
        "citation_ledger": spec["citation_records"],
        "structured_answer_candidate": spec["structured_answer_candidate"],
        "verification_rules": spec["verification_rules"],
        "verification_report": spec["verification_report"],
        "brief_study_consistency_result": spec["answer_artifacts"]["consistency_rule"],
        "executor_kind": "DETERMINISTIC_REFERENCE",
    }
    payload["execution_record_identity"] = canonical_sha256(payload)
    return request, John15StudyExecutionRecord.model_validate_json(rfc8785.dumps(payload))


def _answer(execution: John15StudyExecutionRecord, mode: str) -> John15StudyAnswerArtifact:
    spec = load_runtime_spec()
    artifact = spec["answer_artifacts"][mode.lower()]
    citation_ids = {citation for block in artifact["blocks"] for citation in block["citation_ids"]}
    payload = {
        "schema_version": "1.0",
        "contract": "John15StudyAnswerArtifact",
        "request_identity": ACTIVE_REQUEST_IDENTITY,
        "execution_record_identity": execution.execution_record_identity,
        "packet_identity": PACKET_IDENTITY,
        "packet_canonical_sha256": PACKET_SHA256,
        "packet_receipt_identity": PACKET_RECEIPT_IDENTITY,
        "packet_receipt_file_sha256": PACKET_RECEIPT_SHA256,
        **artifact,
        "citation_records": [item for item in spec["citation_records"] if item["citation_id"] in citation_ids],
    }
    payload["answer_identity"] = canonical_sha256(payload)
    return John15StudyAnswerArtifact.model_validate_json(rfc8785.dumps(payload))


def _git_head() -> str:
    result = subprocess.run(("git", "rev-parse", "HEAD"), check=False, capture_output=True, text=True)
    value = result.stdout.strip()
    if result.returncode or len(value) != 40 or any(character not in "0123456789abcdef" for character in value):
        raise ValueError("implementation Git commit cannot be resolved")
    return value


def _audit(
    execution: John15StudyExecutionRecord,
    brief: John15StudyAnswerArtifact,
    study: John15StudyAnswerArtifact,
    disposition: str,
    implementation_commit: str,
    started_ns: int,
    run_id: UUID | None = None,
    session_id: UUID | None = None,
) -> John15RuntimeAuditReceipt:
    persisted, existing = disposition == "PERSISTED", disposition == "VERIFIED_EXISTING"
    counts = {"study_run": 1, "runtime_artifact": 5, "runtime_event": 11}
    zero = dict.fromkeys(counts, 0)
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "contract": "John15RuntimeAuditReceipt",
        "receipt_identity": str(uuid7()),
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "implementation_commit": implementation_commit,
        "runtime_spec_sha256": SPEC_SHA256,
        "request_identity": ACTIVE_REQUEST_IDENTITY,
        "correction_identity": "bfd475b96f4e0296396b6e3771767194b9210e841643bc66ab3657e995d0d97d",
        "supersedes_request_identity": "782f577a42001df95b1f2094b7c44a075102bd3c54ee157e809828853352ec80",
        "packet_identity": PACKET_IDENTITY,
        "packet_canonical_sha256": PACKET_SHA256,
        "packet_receipt_identity": PACKET_RECEIPT_IDENTITY,
        "packet_receipt_file_sha256": PACKET_RECEIPT_SHA256,
        "plan_id": "PLAN-VS01-T05-JOHN-1-5-ASV-WEB-v1",
        "execution_record_identity": execution.execution_record_identity,
        "brief_answer_identity": brief.answer_identity,
        "brief_answer_sha256": canonical_sha256(brief.model_dump(mode="json")),
        "study_answer_identity": study.answer_identity,
        "study_answer_sha256": canonical_sha256(study.model_dump(mode="json")),
        "verification_outcome": "VERIFIED_WITH_QUALIFICATION",
        "verification_rule_ids": tuple(item["rule_id"] for item in load_runtime_spec()["verification_rules"]),
        "disposition": disposition,
        "persisted": persisted,
        "verified_existing": existing,
        "database_schema_revision": "0001_vs01_t05_runtime" if run_id else None,
        "run_id": str(run_id) if run_id else None,
        "session_id": str(session_id) if session_id else None,
        "executor_kind": "DETERMINISTIC_REFERENCE",
        "model_route": "NONE",
        "model_invocations": 0,
        "network_requests": 0,
        "packet_loads": 1,
        "repair_attempts": 0,
        "archive_writes": 0,
        "database_connections": int(run_id is not None),
        "database_rows_written": counts if persisted else zero,
        "database_rows_verified": counts if existing else zero,
        "terminal_state": "COMPLETE",
        "latency_ms": max(0, (time.monotonic_ns() - started_ns) // 1_000_000),
        "actual_cost_usd": 0.0,
        "private_chain_of_thought": "NOT_COLLECTED_OR_STORED",
    }
    payload["receipt_canonical_sha256"] = canonical_sha256(payload)
    return John15RuntimeAuditReceipt.model_validate_json(rfc8785.dumps(payload))


def execute_john15_study(
    archive_root: Path,
    *,
    dry_run: bool,
    model_adapter: ScholarModelAdapter | None = None,
    database_url: str | None = None,
    _expected_archive_root: Path = CANONICAL_ARCHIVE_ROOT,
    _implementation_commit: str | None = None,
) -> StudyRuntimeResult:
    if model_adapter is not None:
        raise ValueError("the deterministic T05 executor rejects model adapters")
    started_ns = time.monotonic_ns()
    authority = load_t04_authority(archive_root, _expected_archive_root=_expected_archive_root)
    request, execution = _verified_execution(authority)
    brief, study = _answer(execution, "BRIEF"), _answer(execution, "STUDY")
    commit = _implementation_commit or _git_head()
    if dry_run:
        receipt = _audit(execution, brief, study, "DRY_RUN_VALIDATED", commit, started_ns)
        return StudyRuntimeResult(request, execution, brief, study, receipt, False, False)
    if not database_url:
        raise ValueError("BSL_DATABASE_URL is required for live persistence")
    reloaded = load_t04_authority(archive_root, _expected_archive_root=_expected_archive_root)
    if _authority_fingerprint(authority) != _authority_fingerprint(reloaded):
        raise ValueError("T04 authority changed before persistence")
    from bsl.infrastructure.runtime_persistence import persist_runtime

    outcome = persist_runtime(database_url, request, execution, brief, study, commit, started_ns)
    disposition = "VERIFIED_EXISTING" if outcome.verified_existing else "PERSISTED"
    receipt = (
        outcome.audit_receipt
        if not outcome.verified_existing
        else _audit(execution, brief, study, disposition, commit, started_ns, outcome.run_id, outcome.session_id)
    )
    return StudyRuntimeResult(
        request, execution, brief, study, receipt, not outcome.verified_existing, outcome.verified_existing
    )
