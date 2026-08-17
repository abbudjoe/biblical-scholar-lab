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
