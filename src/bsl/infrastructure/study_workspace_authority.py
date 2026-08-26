from __future__ import annotations

import hashlib
import os
import stat
from dataclasses import dataclass
from pathlib import Path

import rfc8785
from pydantic import ValidationError

from bsl.contracts.page_fixture import (
    BASE_BYTES,
    BASE_SHA256,
    DEGRADED_BYTES,
    DEGRADED_SHA256,
    FIXTURE_IDENTITY,
    FIXTURE_JSON_SHA256,
    John15SyntheticPageFixture,
    John15SyntheticPagePublicationReceipt,
    canonical_fixture_bytes,
)
from bsl.contracts.runtime_screening import (
    SPEC_IDENTITY,
    VS01B08RuntimePairResult,
    VS01RuntimeAcquisitionRun,
    VS01RuntimeScreeningReceipt,
)
from bsl.infrastructure.runtime_screening_store import canonical_pair_result_bytes

# ruff: noqa: SIM905

ROOT = Path(__file__).parents[3]
RUN_FIXTURE = ROOT / "fixtures/VS01-T08/reference-runtime-run.json"
RUN_FIXTURE_SHA256 = "eaf59d7d2e654b8f3ae73f36633dca9ffc095788ffbb7c0937bcac583eb1b161"
PAIR_SHA256 = "04c9b4680a0d612bda05508da65720eb583587ebb83ab6f766ac151f1c656222"
PAIR_IDENTITY = "f73ffd20f5096f2b465f3bd91bdb093f4d44a1c9fa5f717f6589ea5ae11d9426"
RUN_IDENTITY = "3ac851b431e75b14b5d50fcb24a16e6243e19eca1f916d8ed81cb95969c9337e"
ANSWER_IDENTITY = "ce9500860ea1be8c4bf4916a554ce541040a34784633389beddb12f80cc321c3"
FIXED_RESULT_IDENTITY = "eb3ae952a7cb62911e259350ca847299b95f1661daf98be879c86f646ae1c880"
T08_RECEIPT_UUID = "01a03f23-35e7-7ef4-b482-d84dafa77010"
T08_RECEIPT_CANONICAL_SHA256 = "8af561aba1c2d0df41ba58f8bd65f6a93de547b5353e8be7eac2c1ece505fac9"
T08_RECEIPT_FILE_SHA256 = "1b2498a08e9221ab53dde1c9dea59e021cf1c361356f24b6420e872c96d638b6"
T06_RECEIPT_UUID = "01a034c2-d6e4-73f4-91b2-7410e7453783"
T06_RECEIPT_FILE_SHA256 = "ec0b4018d30d7160213b20945461325be7821c4b7e666675de5529e4a76ed860"
RUN_COUNT_FIELDS = (
    *("tool_calls evidence_ledger claim_ledger citation_ledger answer_blocks state_sequence audit_events").split(),  # noqa: SIM905
)
PAGE_ROLES = (
    *(
        "PAGE_HEADER SECTION_HEADING VERSE_NUMBER CANONICAL_TEXT STUDY_NOTE_OR_FOOTNOTE CROSS_REFERENCE USER_ANNOTATION"
    ).split(),  # noqa: SIM905
)

T08_PATHS = (
    f"objects/sha256/{PAIR_SHA256[:2]}/{PAIR_SHA256}",
    "snapshots/benchmark/vs01-b08-runtime-pair/reference-screening.json",
    "manifests/benchmark/vs01-b08-runtime-pair/reference-screening/runtime-screening-receipt.json",
)
T06_PATHS = (
    f"objects/sha256/{BASE_SHA256[:2]}/{BASE_SHA256}",
    f"objects/sha256/{DEGRADED_SHA256[:2]}/{DEGRADED_SHA256}",
    f"objects/sha256/{FIXTURE_JSON_SHA256[:2]}/{FIXTURE_JSON_SHA256}",
    "snapshots/page/john-1-5-synthetic-fixture.json",
    "manifests/page/john-1-5-synthetic-fixture/page-fixture-receipt.json",
)


@dataclass(frozen=True)
class StudyWorkspaceAuthority:
    pair_result: VS01B08RuntimePairResult
    t08_receipt: VS01RuntimeScreeningReceipt
    acquisition_run: VS01RuntimeAcquisitionRun
    page_fixture: John15SyntheticPageFixture
    page_receipt: John15SyntheticPagePublicationReceipt


def _open_directory(path: Path) -> int:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open("/", flags)
    try:
        for component in path.parts[1:]:
            child = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except OSError:
        os.close(descriptor)
        raise


def _immutable(root: Path, relative: str) -> bytes:
    components = Path(relative).parts
    if not components or any(component in ("", ".", "..") for component in components):
        raise ValueError("canonical authority relative path is unsafe")
    directory = -1
    try:
        directory = _open_directory(root)
        directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
        for component in components[:-1]:
            child = os.open(component, directory_flags, dir_fd=directory)
            os.close(directory)
            directory = child
        descriptor = os.open(components[-1], os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory)
        metadata = os.fstat(descriptor)
        with os.fdopen(descriptor, "rb") as stream:
            data = stream.read()
    except OSError:
        raise ValueError(f"canonical authority is unreadable: {Path(relative).name}") from None
    finally:
        if directory >= 0:
            os.close(directory)
    if not stat.S_ISREG(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) != 0o444:
        raise ValueError(f"canonical authority is not an immutable regular file: {Path(relative).name}")
    return data


def _committed_run() -> VS01RuntimeAcquisitionRun:
    data = RUN_FIXTURE.read_bytes()
    if hashlib.sha256(data).hexdigest() != RUN_FIXTURE_SHA256 or not data.endswith(b"\n"):
        raise ValueError("committed T08 acquisition-run fixture differs")
    try:
        run = VS01RuntimeAcquisitionRun.model_validate_json(data)
    except ValidationError:
        raise ValueError("committed T08 acquisition-run fixture is invalid") from None
    canonical = rfc8785.dumps(run.model_dump(mode="json")) + b"\n"
    counts = tuple(len(getattr(run, name)) for name in RUN_COUNT_FIELDS)
    exact = (
        data == canonical,
        run.acquisition_run_identity == RUN_IDENTITY,
        run.answer_projection_identity == ANSWER_IDENTITY,
        run.pair_specification_identity == SPEC_IDENTITY,
        counts == (7, 12, 15, 10, 7, 15, 17),
    )
    if not all(exact):
        raise ValueError("committed T08 acquisition-run binding differs")
    return run


def _t08(root: Path) -> tuple[VS01B08RuntimePairResult, VS01RuntimeScreeningReceipt]:
    object_bytes, snapshot_bytes, receipt_bytes = (_immutable(root, path) for path in T08_PATHS)
    if object_bytes != snapshot_bytes or hashlib.sha256(object_bytes).hexdigest() != PAIR_SHA256:
        raise ValueError("canonical T08 object and snapshot differ")
    try:
        result = VS01B08RuntimePairResult.model_validate_json(object_bytes)
        receipt = VS01RuntimeScreeningReceipt.model_validate_json(receipt_bytes)
    except ValidationError:
        raise ValueError("canonical T08 publication is invalid") from None
    exact = (
        object_bytes == canonical_pair_result_bytes(result),
        receipt_bytes == rfc8785.dumps(receipt.model_dump(mode="json")),
        hashlib.sha256(receipt_bytes).hexdigest() == T08_RECEIPT_FILE_SHA256,
        str(receipt.receipt_id) == T08_RECEIPT_UUID,
        receipt.receipt_canonical_sha256 == T08_RECEIPT_CANONICAL_SHA256,
        receipt.disposition == "REFERENCE_CONFORMANT",
        receipt.published is True and receipt.verified_existing is False,
        result.pair_result_identity == PAIR_IDENTITY,
        result.acquisition_run_identity == RUN_IDENTITY,
        result.fixed_case_result_identity == FIXED_RESULT_IDENTITY,
        (result.fixed_points, result.runtime_points, result.pair_points) == (8, 28, 36),
        not result.hard_failures and result.leakage_incidents == 0,
    )
    if not all(exact):
        raise ValueError("canonical T08 publication authority differs")
    return result, receipt


def _t06(root: Path) -> tuple[John15SyntheticPageFixture, John15SyntheticPagePublicationReceipt]:
    base, degraded, fixture_object, fixture_snapshot, receipt_bytes = (_immutable(root, path) for path in T06_PATHS)
    fixture_bytes = canonical_fixture_bytes()
    exact_files = (
        (hashlib.sha256(base).hexdigest(), len(base)) == (BASE_SHA256, BASE_BYTES),
        (hashlib.sha256(degraded).hexdigest(), len(degraded)) == (DEGRADED_SHA256, DEGRADED_BYTES),
        fixture_object == fixture_snapshot == fixture_bytes,
        hashlib.sha256(fixture_bytes).hexdigest() == FIXTURE_JSON_SHA256,
        hashlib.sha256(receipt_bytes).hexdigest() == T06_RECEIPT_FILE_SHA256,
    )
    if not all(exact_files):
        raise ValueError("canonical T06 publication files differ")
    try:
        fixture = John15SyntheticPageFixture.model_validate_json(fixture_bytes)
        receipt = John15SyntheticPagePublicationReceipt.model_validate_json(receipt_bytes)
    except ValidationError:
        raise ValueError("canonical T06 publication is invalid") from None
    exact = (
        receipt_bytes == rfc8785.dumps(receipt.model_dump(mode="json")),
        fixture.fixture_identity == FIXTURE_IDENTITY,
        str(receipt.receipt_identity) == T06_RECEIPT_UUID,
        receipt.disposition == "PUBLISHED",
        receipt.published is True and receipt.verified_existing is False,
        tuple(region.benchmark_role for region in fixture.scene.regions) == PAGE_ROLES,
    )
    if not all(exact):
        raise ValueError("canonical T06 publication authority differs")
    return fixture, receipt


def load_study_workspace_authority(archive_root: Path) -> StudyWorkspaceAuthority:
    if not archive_root.is_absolute():
        raise ValueError("archive root must be absolute")
    root = archive_root
    result, t08_receipt = _t08(root)
    run = _committed_run()
    fixture, page_receipt = _t06(root)
    if (
        run.acquisition_run_identity != result.acquisition_run_identity
        or result.acquisition_run_identity != t08_receipt.acquisition_run_identity
    ):
        raise ValueError("T08 acquisition-run identity binding differs")
    return StudyWorkspaceAuthority(result, t08_receipt, run, fixture, page_receipt)
