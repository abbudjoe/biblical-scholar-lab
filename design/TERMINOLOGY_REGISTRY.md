# Biblical Scholar Lab — Canonical Terminology Registry

Use these globally unique names in code, schemas, database records, events, metrics, logs, handoffs, and public contracts. Short local forms may appear only in explanatory prose where no ambiguity exists.

## Collision-safe ladders

| Canonical namespace | Meaning |
|---|---|
| `TNC-A0` … `TNC-A6` | Translation Nuance architecture and integration ladder |
| `ACCESS-A0` … `ACCESS-A6` | Ancient-version/apparatus access lanes |
| `ASSURE-A0` … `ASSURE-A3` | Runtime assurance classes |
| `RETRO-R0` … `RETRO-R5` | Retroversion-restraint ladder |
| `RELEVANCE-R0` … `RELEVANCE-R4` | Corpus relevance tiers |
| `TRAIN-S0` … `TRAIN-S8` | Training curriculum stages |
| `SENS-S0` … `SENS-S8` | Privacy and sensitivity classes |
| `QUALITY-Q0` … `QUALITY-Q6` | Corpus quality classes |
| `QUANT-Q0` … `QUANT-Q6` | Quantization ladder |
| `CTX-P0` … `CTX-P3` | Context priority classes |
| `REV-P0` … `REV-P2` | Benchmark/review authority partitions |
| `ALG-P0` … `ALG-P4` | Preference-training algorithm stages |
| `CC-0` … `CC-5` | Cloud campaign classes |
| `EL-0` … `EL-4` | Experiment evidence levels |
| `K0` … `K5` | Context compaction classes; use the `COMPACT-` prefix in code when collision is possible |
| `TNEVAL-A0` … `TNEVAL-A4` | DR-31 Translation Nuance evaluation ladder; A0 is deterministic retrieval, A1–A3 are separately authorizable API evaluations, and A4 is training-gated |

## Program and status records

| Name | Purpose |
|---|---|
| `BSL-STATUS-01` | Formal Lab program-status authority |
| `PAUSED_AFTER_VS01_T09B` | Current Lab program disposition entered from an exact pause-entry implementation baseline; current Git `main` after persistence is established by repository history and the post-merge receipt |
| `OPTIONAL_EDITORIAL_ACCEPTANCE` | Deferred acceptance work that may be run only if the reference workspace gains a real editorial/accessibility consumer |
| `DORMANT_PENDING_TRAINING_REACTIVATION_GATE` | Approved historical training, learned-model serving/conversion, cloud-training, adapted-model-hosting, or A4 design that has no current implementation or execution authority |
| `ELIGIBLE_FOR_SEPARATE_BOUNDED_API_EVALUATION_AUTHORITY` | A1–A3 may later receive an exact provider/API evaluation design and activation without satisfying the training-reactivation gate |
| `NOT_GATED_BY_TRAINING_REACTIVATION` | The named A1–A3 evaluation posture is a prerequisite to a training decision rather than a product of the training gate |
| `NOT_ON_CURRENT_CRITICAL_PATH` | Explicit forward-program exclusion without historical supersession |
| `NOT_IMPLEMENTATION_AUTHORITY` | Design or status statement that authorizes no physical implementation |

## API-first evaluation posture

| Name | Current posture |
|---|---|
| `TNEVAL-A0` | `DETERMINISTIC_RETRIEVAL_BASELINE`; `FUTURE_BOUNDED_DESIGN_OR_ACTIVATION_REQUIRED`; `NO_PROVIDER_REQUIRED` |
| `TNEVAL-A1` | `UNSTARTED`; `NOT_AUTHORIZED`; `NOT_ON_CURRENT_CRITICAL_PATH`; `ELIGIBLE_FOR_SEPARATE_BOUNDED_API_EVALUATION_AUTHORITY`; `NOT_GATED_BY_TRAINING_REACTIVATION` |
| `TNEVAL-A2` | `UNSTARTED`; `NOT_AUTHORIZED`; `NOT_ON_CURRENT_CRITICAL_PATH`; `ELIGIBLE_FOR_SEPARATE_BOUNDED_API_EVALUATION_AUTHORITY`; `NOT_GATED_BY_TRAINING_REACTIVATION` |
| `TNEVAL-A3` | `UNSTARTED`; `NOT_AUTHORIZED`; `NOT_ON_CURRENT_CRITICAL_PATH`; `ELIGIBLE_FOR_SEPARATE_BOUNDED_API_EVALUATION_AUTHORITY`; `NOT_GATED_BY_TRAINING_REACTIVATION` |
| `TNEVAL-A4` | `DORMANT_PENDING_TRAINING_REACTIVATION_GATE`; eligible only after every gate in DR-31 section 21 |

A1–A3 require a separately frozen provider/API evaluation authority using applicable DR-22 and DR-24 methodology and applicable DR-25 safety, cost, termination, and cleanup controls. This registry creates no experiment or provider authority.

## Cross-project contracts

Exactly these three shared contracts are recognized.

| Name | Normative owner | Purpose |
|---|---|---|
| `TranslationAnnotationPackage v1` | Biblos | Normative reader-consumer package schema and offline import boundary |
| `ReaderAnnotationProjection v1` | Biblical Scholar Notes | Normative bounded editorial export consumed by the Lab |
| `TranslationAnnotationCompilationReceipt v1` | Biblical Scholar Lab | Normative producer receipt binding compilation inputs, validation, rights, accepted/rejected records, and exact package bytes |

A checksum sidecar, transport ZIP, internal validation result, or project-local type is not a fourth shared contract.

## Notes record classes

| Name | Purpose |
|---|---|
| `StudyRecord` | Notes-owned complete editorial master and research record |
| `ReaderAnnotationProjection` | Bounded Notes-owned package-candidate export |
| `PublicPost` | Public-facing prose that is not automatic philological, benchmark, or training gold |
| `PersonalReflection` | Private reflection excluded by default from package, benchmark, retrieval, evaluation, and training input |
| `SourceRecord` | Notes source/provenance reference used by Lab validation when authorized |

## Independent annotation axes

| Name | Purpose |
|---|---|
| `editorial_state` | Notes-owned editorial readiness |
| `source_verification_state` | Lab verification of exact source, locator, quotation, morphology, and claim support |
| `scholarly_review_label` | Review partition and qualification state; owner approval is not specialist review |
| `lifecycle_state` | Active, superseded, retired, or withdrawn revision state |
| `reader_delivery` | Eligibility for reader-package delivery |
| `retrieval` | Eligibility for retrieval use |
| `evaluation` | Eligibility for evaluation use |
| `training` | Eligibility for training use; defaults to disallowed |
| `public_sharing` | Eligibility for public redistribution or display |

## Capability-reuse classifications

| Name | Meaning |
|---|---|
| `REUSE_DIRECTLY` | Existing authority or implementation can serve the new role without semantic change |
| `REUSE_AFTER_ADAPTER` | Existing capability is useful after a bounded, activated projection or adapter |
| `REFERENCE_ONLY` | Existing work remains a precedent, fixture, or historical authority but is not a forward runtime dependency |
| `DORMANT_TRAINING_PATH` | Existing training, learned-model serving/conversion, cloud-training, adapted-model-hosting, or A4 design is retained but inactive pending the DR-31 section 21 gate |
| `RETIRED_FROM_CRITICAL_PATH` | Existing product assumption or implementation is preserved but no longer blocks the active program |

## Governance records

| Name | Purpose |
|---|---|
| `ImplementationActivationManifest` | Exact boundary of one Sol implementation root turn |
| `TurnHandoff` | Append-only implementation/evidence record for one root turn |
| `ChatGPTReviewRecord` | Exact-PR-head independent review disposition |
| `OwnerMergeAuthorizationRecord` | Owner authorization of one exact reviewed PR head |
| `MergeReceipt` | Post-merge evidence and resulting `main` identity |
| `ComplexityReceipt` | DR-30 code, dependency, abstraction, and size conformance |

## Core evidence/runtime records

| Name | Purpose |
|---|---|
| `TranslationNuanceEvidencePacket` | Immutable evidence packet for Translation Nuance analysis |
| `MultimodalPageEvidencePacket` | Immutable page/image evidence packet |
| `ContextPacket` | Exact model-facing context projection |
| `ContextCompactionArtifact` | Provenance-preserving context compaction record |
| `ScholarAnswerCandidate` | Structure-first model output awaiting verification |
| `RuntimeAuditReceipt` | Observable request, tool, model, verification, cost, and state record |
| `EvaluationResultBundle` | Project-owned canonical evaluation result |
| `TrainingResultBundle` | Project-owned canonical training result |
| `ArtifactArchiveReceipt` | Verified promotion of retained artifacts to the owner archive |

New collisions require a registry amendment before implementation.
