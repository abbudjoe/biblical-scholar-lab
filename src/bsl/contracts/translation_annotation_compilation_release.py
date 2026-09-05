"""Detached private release version of the existing compilation receipt family."""

from typing import Annotated, Literal, Self

import rfc8785
from pydantic import BaseModel, Field, model_validator

from bsl.contracts.source_admission import Sha256
from bsl.contracts.translation_annotation_compilation import STRICT
from bsl.infrastructure.j13_authority import sha

OWNER_SHA = "77fc75c831da6fbf8bed11d7e1c227466a7d3b205627b3318d62326f2a63bbf8"
CANDIDATE_SHA = "77648d3c8f562df6110eecbb7c978cfbd13e0b7b7ec7583ba98b1f72ade8cbfa"
RECEIPT_SHA = "5f4f85288fc312fafdf164ac93f1c553e55a6b6c892f209de78d7cc4e6d46bdc"
COMMENT_SHA = "0125e0c139afc84170c93a676f3d0c5c5dde1969b603063d3e82463dc1faf136"
OWNER_ID = "J13-LAB-02-OWNER-DECISION-01"
ROSTER = (
    "tan:john.13.8:no-share-with-me",
    "tan:john.13.10:bathed-versus-washed",
    "tan:john.13.19:i-am-or-i-am-he",
)
PACKAGE = "translation-annotation-package.j13-pilot-01.release.json"
RECEIPT = "translation-annotation-compilation-receipt.j13-pilot-01.release.json"
NOTICES = "SOURCE-NOTICES.j13-pilot-01.txt"
HANDOFF = "J13-LAB-02-admission-handoff.md"
RELEASE_FILES = (
    "src/bsl/contracts/translation_annotation_compilation_release.py",
    "src/bsl/application/j13_private_pilot_release.py",
    "tools/j13_lab_02_finalize_private_pilot.py",
)
DigestRecord = tuple[str, Sha256]
GitSha = Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]


class _File(BaseModel):
    model_config = STRICT
    name: str
    sha256: Sha256
    byte_count: Annotated[int, Field(gt=0)]


class _Note(BaseModel):
    model_config = STRICT
    annotation_issue_id: str
    annotation_revision: Literal[2]
    reader_annotation_projection_revision: Literal[2]
    notes_git_blob: GitSha
    notes_original_sha256: Sha256


class _Right(BaseModel):
    model_config = STRICT
    basis_id: str
    source_id: str
    source_version: str
    snapshot_identity: Sha256
    components: tuple[DigestRecord, ...]
    permission_evidence: tuple[DigestRecord, ...]
    grant: str
    obligations: tuple[str, ...]
    fulfillment: tuple[str, ...]
    reciprocal_assessment: str
    result: Literal["supported"]


class _Material(BaseModel):
    model_config = STRICT
    annotation_id: str
    pointer: str
    text: str
    material_type: Literal[
        "quotation", "original prose", "lexical paraphrase", "morphology-derived statement", "citation/notice"
    ]
    basis_ids: tuple[str, ...]
    reason: str
    result: Literal["supported"]


class _Delta(BaseModel):
    model_config = STRICT
    pointer: str
    old_canonical_json: str
    new_canonical_json: str
    reason: str
    basis_ids: tuple[str, ...]


class TranslationAnnotationCompilationReceiptV2(BaseModel):
    model_config = STRICT
    schema_version: Literal["translation-annotation-compilation-receipt-v2"]
    variant: Literal["private-offline-pilot-release"]
    receipt_identity: Sha256
    activation_sha256: Literal["ef38fd4e87b85b3b5062ede0c7890058450a16d250af6d9e452f39ef04fcff68"]
    input_candidate: _File
    input_receipt: _File
    input_receipt_identity: Literal["1565dfdecb33c000714a25721603043e0d8e8a6de95558364d9677bf5a2369da"]
    owner_decision_sha256: Sha256
    approval_comment_id: Literal[5548832754]
    approval_pull_request: Literal[23]
    approval_repository: Literal["abbudjoe/biblical-scholar-lab"]
    approval_comment_sha256: Sha256
    notes: tuple[_Note, ...]
    upstream_manifest_sha256: Sha256
    consumer_commit: Literal["8d9a8a2e051089fbd05a3d03e32da445a6d13f48"]
    consumer_schema: Literal["translation-annotation-package-v1"]
    consumer_schema_sha256: Literal["f4ed1437b95c037d619b93c9e414948eb8f8fb4f5602b365c9cf250956aefd49"]
    consumer_references: tuple[DigestRecord, ...]
    producer_commit: GitSha
    producer_files: tuple[DigestRecord, ...]
    source_rights: tuple[_Right, ...]
    payload_inventory: tuple[_Material, ...]
    package_series_id: Literal["tap:j13-pilot-01"]
    package_revision: Literal[2]
    first_install: Literal[True]
    expected_installed_predecessor: None
    declared_predecessor_present: Literal[False]
    protected_content_equal: Literal[True]
    protected_content_sha256: Sha256
    permitted_delta: tuple[_Delta, ...]
    permitted_delta_sha256: Sha256
    non_reader_eligibility_sha256: Sha256
    delivery_scope: Literal["Joseph-controlled private offline Biblos pilot only"]
    review_label: Literal["model_assisted_editorial_review"]
    package_file: _File
    notice_file: _File
    archive_inventory_sha256: Sha256
    deterministic_output_proof: Literal[
        "Contextual reconstruction binds every byte; independent seven-file equality is recorded in execution evidence."
    ]
    biblos_admission_performed: Literal[False]
    remaining_gate: Literal[
        "Exact-head governance review of private bytes, then independent Biblos admission with notices."
    ]

    @model_validator(mode="after")
    def coherent(self) -> Self:
        if (self.input_candidate.sha256, self.input_candidate.byte_count) != (CANDIDATE_SHA, 20925):
            raise ValueError("candidate binding differs")
        if (self.input_receipt.sha256, self.input_receipt.byte_count) != (RECEIPT_SHA, 77503):
            raise ValueError("candidate receipt binding differs")
        if (self.owner_decision_sha256, self.approval_comment_sha256) != (OWNER_SHA, COMMENT_SHA):
            raise ValueError("owner authority differs")
        if tuple(n.annotation_issue_id for n in self.notes) != ROSTER:
            raise ValueError("three-note roster differs")
        if (self.package_file.name, self.notice_file.name) != (PACKAGE, NOTICES):
            raise ValueError("release output names differ")
        delta = [d.model_dump(mode="json") for d in self.permitted_delta]
        if sha(rfc8785.dumps(delta)) != self.permitted_delta_sha256:
            raise ValueError("delta digest differs")
        payload = self.model_dump(mode="json", exclude={"receipt_identity"})
        if sha(rfc8785.dumps(payload)) != self.receipt_identity:
            raise ValueError("release receipt identity differs")
        return self
