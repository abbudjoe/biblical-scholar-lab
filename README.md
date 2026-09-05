# Biblical Scholar Lab — Design Baseline

## J13-LAB-02 private pilot finalization

J13-LAB-01 is merged at `ff362da6300a16b4c36aacc5039ff5fe90a39bae`. J13-LAB-02 alone is active under [its exact activation](activations/ACT-J13-LAB-02-FINALIZE-PRIVATE-PILOT-RELEASE-v1.json) for local private release derivation of the unchanged three approved notes. Actual Biblos admission, public release, other original tasks and all evaluations remain unauthorized.

This repository is the authoritative design and implementation record for Biblical Scholar Lab.

Governance implementation is closed. `VS01-T01` and its R02 APFS compatibility repair are merged historical foundation. `VS01-T02` is complete: the canonical archive is initialized, six authoritative source snapshots are admitted, and source acquisition is closed for VS-01. `VS01-T03`, `VS01-T04`, and `VS01-T06` are complete and canonically published. `VS01-T05` is complete and persisted. `VS01-T07` operational publication is complete. `VS01-T08` implementation, Hotfix01, and operational publication are complete. `VS01-T09A` is complete and merged at `95d587a2b09d8c07ac7574050a5d7afa0969a625` with workspace identity `9f9f9dd44384d90da5b3918e96ad3623e1235016f6283d224259cba9b670816d`; `VS01-T09B` is merged and complete at pause-entry implementation commit `3f52895459aefb84e6e6a7da8870f12e5f653e76`, tree `cbe157cad80adf42127871a9859db11707a7b278`. Those hashes identify the last completed implementation baseline before design persistence; the current Git `main` after persistence is established by repository history and the post-merge receipt. The program is formally `PAUSED_AFTER_VS01_T09B`. `VS01-T09-OP01` is optional editorial acceptance, deferred indefinitely, and not on the critical path. `VS01-T10` and later original tasks remain unstarted and unauthorized.

## Authority

- Joseph Abbud is the project owner and final approver.
- ChatGPT designs experiments and product contracts and reviews Sol's implementation and evidence.
- GPT-5.6 Sol is the exclusive implementation engineer.
- GPT-5.6 Luna may operate only as a frozen campaign runner delegated by Sol.

## Design-review lifecycle

1. ChatGPT proposes a numbered design review.
2. Joseph approves it or requests amendments.
3. The approved text is written to `design/approved/` and committed.
4. Every later implementation must cite the applicable design ID and approved commit.
5. Material changes require an explicit amendment or a new design review.

See [`DESIGN_GOVERNANCE.md`](DESIGN_GOVERNANCE.md) and [`design/DECISION_INDEX.md`](design/DECISION_INDEX.md).

Implementation navigation: [`design/APPROVED_BASELINE_SUMMARY.md`](design/APPROVED_BASELINE_SUMMARY.md), [`design/TERMINOLOGY_REGISTRY.md`](design/TERMINOLOGY_REGISTRY.md), and [`design/PACKAGE_STATUS.md`](design/PACKAGE_STATUS.md).

Current recharter authority: [`BSL-STATUS-01`](design/approved/BSL-STATUS-01-paused-after-vs01-t09b.md) and [`DR-31`](design/approved/DR-31-biblos-translation-nuance-laboratory-recharter-and-annotation-package-authority.md).

## Current implementation status

- W00A1a and W00C are merged historical governance implementation; governance implementation is closed.
- W00A1b, W00A2, W00B, and the dummy W01 proof are retired or canceled as VS-01 prerequisites.
- `VS01-T01` and R02 are merged historical archive/source-admission foundation.
- `VS01-T02 — Canonical Archive Bootstrap and Raw Source Admission` is complete; the canonical archive is initialized with six authoritative source snapshots.
- Source acquisition is closed for VS-01.
- `VS01-T03` is complete and canonically published: bundle identity `9e147d9e218564d744360fd94b794758d1cc3e98e3826380008939eb0c494f32`, canonical SHA-256 `397f7c8908bf8e8533b23eb808ab7c0ede796c95d7b49451fa92f40261ee19d6`.
- `VS01-T04` is complete and canonically published: packet identity `aebcbb50fc8383f2f4f395bc71116563325c1fde237427dc8c1bc8140e8ebe31`, canonical SHA-256 `9f81621785924161cc4861e2af9f010bd18e822b60199d62a6327eff44ea0409`.
- `VS01-T05` is complete and persisted; its T04 authority and the upstream T03 authority remain immutable.
- `VS01-T06` is complete and canonically published.
- `VS01-T07` operational publication is complete.
- `VS01-T08` implementation, Hotfix01, and operational publication are complete: acquisition-run identity `3ac851b431e75b14b5d50fcb24a16e6243e19eca1f916d8ed81cb95969c9337e`, pair-result identity `f73ffd20f5096f2b465f3bd91bdb093f4d44a1c9fa5f717f6589ea5ae11d9426`, pair-result file SHA-256 `04c9b4680a0d612bda05508da65720eb583587ebb83ab6f766ac151f1c656222`, publication receipt UUID `01a03f23-35e7-7ef4-b482-d84dafa77010`, receipt canonical SHA-256 `8af561aba1c2d0df41ba58f8bd65f6a93de547b5353e8be7eac2c1ece505fac9`, and receipt file SHA-256 `1b2498a08e9221ab53dde1c9dea59e021cf1c361356f24b6420e872c96d638b6`.
- `VS01-T09A` is complete and merged.
- `VS01-T09-ERRATA-01` is complete and merged.
- `VS01-T09B` is complete and merged at `3f52895459aefb84e6e6a7da8870f12e5f653e76`, tree `cbe157cad80adf42127871a9859db11707a7b278`.
- `VS01-T09-OP01` is `OPTIONAL_EDITORIAL_ACCEPTANCE`, `DEFERRED_INDEFINITELY`, and `NOT_ON_CRITICAL_PATH`.
- `VS01-T10` and later original tasks are unstarted and unauthorized.
- Foundation-model family or capacity selection for adaptation or hosting, continued pretraining, Translation Nuance mid-training, SFT, retrieval/tool fine-tuning, preference optimization, model merging, quantization, distillation, learned-model serving, cloud training, adapted-model hosting, `TNEVAL-A4`, and training/campaign-controller implementation are `DORMANT_PENDING_TRAINING_REACTIVATION_GATE`, `NOT_ON_CURRENT_CRITICAL_PATH`, and `NOT_IMPLEMENTATION_AUTHORITY`.
- `TNEVAL-A0` is a future deterministic retrieval baseline requiring a separate bounded design or activation and no provider. `TNEVAL-A1` through `TNEVAL-A3` are `UNSTARTED`, `NOT_AUTHORIZED`, `NOT_ON_CURRENT_CRITICAL_PATH`, `ELIGIBLE_FOR_SEPARATE_BOUNDED_API_EVALUATION_AUTHORITY`, and `NOT_GATED_BY_TRAINING_REACTIVATION`.

## Current program role

Biblos is the sole production Bible reader. Biblical Scholar Notes is the editorial master. Biblical Scholar Lab is the source, evidence, annotation-validation, operation-specific rights-validation, deterministic package-compilation, receipt, reference-validation, benchmark, API-evaluation, and optional future model-research laboratory supporting Biblos.

Exactly three cross-project contracts are recognized:

- `TranslationAnnotationPackage v1` — normative consumer schema owned by Biblos.
- `ReaderAnnotationProjection v1` — normative editorial export schema owned by Biblical Scholar Notes.
- `TranslationAnnotationCompilationReceipt v1` — normative producer receipt owned by Biblical Scholar Lab.

The Lab is not a required Biblos runtime service. No implementation of these contracts, John 13 source work, package compilation, provider/API evaluation, model work, cloud work, or training is authorized by the recharter alone. A later A1–A3 evaluation may be authorized separately without satisfying the training-reactivation gate, but only after its package, evidence, benchmark, rights, privacy, retention, cost, provider, and operational controls are frozen.

## Current approved baseline

- `DR-01` — Version-One Product Contract
- `DR-02` revision 2 — Scholarly Epistemology and Methodology, including the approved architecture-contract schedule, model-capacity and family-bake-off policy, Gemma budget posture, and the original mobile/quantization direction later superseded within scope by DR-29
- `DR-03` — Scope, Refusal, and Sensitive-Use Policy
- `DR-04` — Canon, Reference, and Versification Model
- `DR-05` — Textual-History and Provenance Graph
- `DR-06` — Translation Nuance Core, including the approved A0–A6 architecture-extension ladder and profiling-gated compute-kernel policy
- `DR-07` — Linguistic Representation, including stand-off multilingual analysis, explicit source-text views and coordinate contracts, source-native annotation preservation, language-specific Greek/Hebrew/Aramaic profiles, and word-study-fallacy guardrails
- `DR-08` — Ancient Versions and Apparatus Policy, including passage-scoped version roles, evidential-distance tracking, R0–R5 retroversion restraint, apparatus scope and silence contracts, edition-local sigla, daughter-version dependencies, and component-specific access lanes
- `DR-09` — Scholarship and Citation Model, including work/version/manifestation separation, assertion-based bibliographic identity, claim-level citation entailment, quotation and translation provenance, publication-status awareness, source-dependence tracking, and dated scholarly-landscape assessment
- `DR-10` — Rights, Lineage, and Release Architecture, including component- and operation-specific authorization, purpose and jurisdiction scoping, fail-closed unknowns, rights-partitioned storage and lineage, user-private and holdout isolation, artifact-specific release review, memorization/extraction gates, and owner-only consequential release approval
- `DR-11` — Foundation-Model Family and Component Architecture, including the mandatory Qwen/Gemma/Ministral compact bake-off, Qwen3.8/Gemma 31B capacity comparison, exact model-bundle identity, Base/product lineage separation, family-specific multimodal preservation, reasoning/context/MTP controls, and role-specific model selection
- `DR-12` — Translation Nuance Model Integration Architecture, including the deterministic Translation Nuance Semantic Kernel, immutable evidence packets, structure-first verified generation, the A0–A6 integration ladder, relation-aware adapters and graph-memory gates, specialist routing, exact rollback paths, and family-specific component integration
- `DR-13` — Multilingual Architecture, including separate source/question/answer/quotation/retrieval language roles, language-variety and script identity, capability-specific support tiers, explicit pivot provenance, multilingual retrieval and training, native review, worst-group reporting, RTL and Unicode-security requirements, and auditable unsupported-language fallback
- `DR-14` — Multimodal and Page-Understanding Architecture, including immutable media provenance, coordinate and transform contracts, hierarchical layout and reading order, dual specialist/VLM recognition, the Page Evidence Kernel, immutable multimodal evidence packets, canonical-text reconciliation without evidence replacement, prompt-injection isolation, private-upload controls, and real-degradation retention testing
- `DR-15` — Long-Context and Context-Composer Design, including native/configured/verified/effective context separation, deterministic evidence-aware composition, focused and full-canon modes, exact budgeting, protected counterevidence, immutable plans and packets, provenance-preserving compression and compaction, mandatory rehydration, structured multi-turn state, and position-, cost-, rights-, multilingual-, and multimodal-aware evaluation
- `DR-16` — Runtime Scholar Harness, including the deterministic Scholar Runtime Orchestrator, typed task and assurance contracts, narrow tool capabilities, evidence-sufficiency states, immutable context and answer packets, layered claim verification, bounded repair and escalation, one verified claim ledger across answer depths, the project-owned framework-neutral runtime core, a deterministic reference executor, LangGraph v1 as the provisional durable workflow substrate, and OpenAI Agents SDK only as an optional bounded adapter
- `DR-17` — Corpus Composition and Sampling, including the vertical-slice-first corpus strategy, stage-specific roles and eligibility, translation-family and overlap controls, cluster-level benchmark firewalls, hierarchical sampling, mandatory multilingual replay, content- and compute-matched model materializations, immutable mixture specifications, proxy-tested mixture optimization, actual exposure ledgers, and corpus privacy, poisoning, rights, and historical-harm safeguards
- `DR-18` — Training Curriculum and Objectives, including no-training A0 baselines, distinct product-first and clean-Base lineages, ancient/context CPT, structured Translation Nuance mid-training, scholarly and retrieval-aware SFT, explicit replay and component-update policies, parent-relative capability preservation, matched preference ablations, immutable checkpoint and exposure identity, stage-gated compute, and owner-only promotion authority
- `DR-19` — Preference and Behavioral Shaping, including typed and conditional preference judgments, task-specific `REV-P0`/`REV-P1`/`REV-P2` review partitions, explicit separation of owner/methodology/deterministic/SME review, DPO and SimPO matched controls, reversible adapter-first training, multilingual and multimodal behavior coverage, anti-over-refusal and safety balance, and the post-`REV-P1` `MVP-01_EXPERT_COLLABORATION_PREVIEW` milestone
- `DR-20` — Benchmark Charter, including the multidimensional benchmark suite, Translation Nuance signature track, distinct model/system/evidence modes, relationship-cluster splits, public/private/fresh contamination firewall, `REV-P0`/`REV-P1`/`REV-P2` authority, ChatGPT-authored and owner-approved benchmark content, SME-gated specialist gold, Sol-only implementation machinery, calibrated scoring hierarchy, hard-failure caps, validity gates, and the public-safe expert-collaboration benchmark preview
- `DR-21` — Benchmark Annotation, Scoring, and Governance, including authority-separated case design and approval, `REV-P0`/`REV-P1`/`REV-P2` validation paths, case-family blueprints and bounded review batches, evidence and answer contracts, atomic dependency-aware rubrics, hard-failure caps, qualified human adjudication, calibrated judge governance, relationship-cluster statistics, public/private/fresh construction controls, and Sol-only benchmark machinery implementation
- `DR-22` — Evaluation Harness and Prior-Art Baseline Design, including the project-owned Evaluation Core and deterministic reference engine, Inspect AI as the provisional production execution adapter, immutable subject and elicitation identities, independent generation and scoring, stable sample IDs, complete failure accounting, no semantic rerolls, common-denominator/family-native/author-native/normalized conditions, inference-backend equivalence, explicit prior-art reproduction tiers, Rhema BibleAI and Timms assistant baselines, private-holdout provider controls, sandboxed execution, canonical result bundles, and Sol/Luna authority boundaries
- `DR-23` — Model and Training Harness Contract, including the project-owned Training Core, deterministic reference engine, replaceable FSDP2/DCP and ms-swift adapters, exact exposure/packing/loss/component/checkpoint semantics, evidence-tiered resume and reproducibility, Lambda Cloud as the sole project-controlled training and evaluation cloud, the owner-controlled external Thunderbolt drive as the authoritative retained checkpoint/artifact archive, verified transfer and provider-cleanup receipts, and Sol/Luna training-operation boundaries
- `DR-24` — Experiment Ladder and Promotion Gates, including the gated experiment DAG, evidence levels, lexicographic hard-gate precedence, readiness and A0 requirements, product-first and clean-Base branches, `MVP-01` collaboration-preview path, model-family and capacity screening, staged budget release, fit-for-claim replication, Thunderbolt archive and Lambda closeout gates, negative-result handling, and preapproved Sol-to-Luna campaign delegation
- `DR-25` — Cloud Campaign and Sol-to-Luna Operating Design, including immutable owner-authorized campaign envelopes, standing-smoke and one-use approval classes, Sol-led/Luna-operated delegation, a durable controller and local Lambda Control Broker, nearest-available eligible-region selection from live Lambda capacity, strict provider and credential isolation, bounded retries and watchdogs, owner-pull Thunderbolt archival, provider-side termination and cleanup receipts, and the `CE-00`–`CE-06` conformance gates required before substantive cloud work
- `DR-26` — User Experience and Answer Contract, including the evidence-centered research workspace, Brief/Study/Scholarly rendering from one verified claim ledger, visible active passage/edition/canon/language/method/context state, inspectable citations and Translation Nuance, multimodal page-study evidence separation, versioned user corrections and exports, compaction visibility and rehydration, multilingual/RTL behavior, WCAG 2.2 AA accessibility, anti-overtrust and anti-dependency controls, and the public-safe expert-collaboration preview surface
- `DR-27` — Privacy, Security, Telemetry, and Release, including sensitivity and purpose separation, private-by-default user data, granular consent and user controls, trust zones and least privilege, provider-route and secrets isolation, content-minimized telemetry, upload/RAG/output and LLM-specific defenses, supply-chain provenance and signing, incident response and kill switches, staged public release, rollback and revocation, and owner-only consequential processing and release authority
- `DR-28` — Integrated Logical Architecture and Contract Registry, including the modular-monolith-first system, PostgreSQL authoritative records, the Thunderbolt research archive and deletable private vault, project-owned configuration and inference gateways, source acquisition and freshness, PostgreSQL work control, embedding/reranker bake-off and index contracts, retention and erasure, and the IA-00–IA-11 implementation gates
- `DR-29` — Local Desktop, Mobile Client, Quantization, and Distillation Architecture, including Mac mini M4 local inference as the first edge priority, Apple-silicon MacBook support, a secure paired-Mac/Lambda mobile-client architecture, the Local Scholar Node boundary, MLX-LM and llama.cpp runtime comparison, 8B–12B local model quantization, optional 2B–4B distillation and on-phone inference, native mobile OCR, explicit route disclosure, and LE-00–LE-13 implementation gates
- `DR-30` — Implementation Readiness, Simplicity, and Anti-Slop Contract, including immutable activation manifests, vertical-slice-first implementation, globally unique code identifiers, hard code/complexity/dependency budgets, anti-scaffolding and anti-placeholder rules, public-repository review governance, the initial Mac mini/MacBook execution topology, and IR-00–IR-06 readiness gates
- `DR-31` — Biblos Translation Nuance Laboratory Recharter and Annotation Package Authority, including the final Biblos/Notes/Lab role allocation, exact three-contract boundary, merged Biblos consumer authority, deterministic package and detached-receipt posture, API-first evaluation, conjunctive training reactivation, formal pause, and anti-duplication requirements

Supporting official-source verification for DR-02 revision 2 is recorded under `design/evidence/`.

## Approved initial implementation scope

- `VS-01` — John 1:5 Translation Nuance Vertical Slice, activating the smallest end-to-end source, linguistic, translation-comparison, evidence, runtime, page-study, correction, audit, and seed-benchmark workflow while explicitly excluding cloud execution, training, vector search, mobile clients, full-canon context, and speculative service scaffolding

## Approved governance packages

- `GOV-01` — Public Repository Governance and Review Package, revision 3, authorizing the existing stored `gh` CLI identity `@abbudjoe`, exact-head ChatGPT review, explicit exact-head owner approval in this conversation, and a separate merge-only Sol turn

## Approved source plans

- `SOURCE-PLAN-01` — John 1:5 Vertical-Slice Source Admission Plan, freezing the exact SBLGNT, MorphGNT, ASV, WEB Classic, Abbott-Smith, and Source Serif components, revisions, rights lineages, exclusions, derived-artifact boundaries, and hard-stop conditions for VS-01

## Approved benchmark batches

- `BENCH-VS01-BATCH-01` — first ChatGPT-authored, owner-approved, public-safe John 1:5 benchmark seed, freezing twelve `REV-P0`/bounded `REV-P1` cases, evidence and answer contracts, atomic rubrics, hard failures, contamination relationships, and the fixed-evidence-versus-proactive-full-runtime distinction

## Approved repository governance

- `GOV-01` revision 3 with `GOV-01-S03` — lean manual exact-head control: task-specific CI, ChatGPT exact-head review, Joseph exact-head approval, and a separate merge-only turn using `--match-head-commit`
- `GOV-01-ERRATA-01/02` — preserved historical conformance corrections; their bootstrap sequence is non-authoritative after S03

## Approved implementation activations

- `ACT-W00-REPOSITORY-GOVERNANCE-v1` — superseded; historical only
- `ACT-W00-REPOSITORY-GOVERNANCE-v2` — superseded by v3; historical only
- `ACT-W00-REPOSITORY-GOVERNANCE-v3` — completed historical W00A1a bootstrap authorization
- `ACT-W00C-GOVERNANCE-CLOSURE-v1` — superseded by v2; historical execution evidence
- `ACT-W00C-GOVERNANCE-CLOSURE-v2` — completed historical W00C authorization
- `ACT-VS01-T01-ARCHIVE-SOURCE-FOUNDATION-v1` — completed historical T01 foundation authorization
- `ACT-VS01-T01-APFS-PLIST-COMPAT-v1` — completed historical R02 compatibility authorization
- `ACT-VS01-T02A-ARCHIVE-BOOTSTRAP-KERNEL-v1` — completed historical T02A authorization
- `ACT-VS01-T02B-SOURCE-ADMISSION-KERNEL-v1` — completed historical T02B authorization
- `ACT-VS01-T03-JOHN-1-5-NORMALIZATION-v1` — completed historical T03 authorization; normalization is canonically published
- `ACT-VS01-T04-JOHN-1-5-TRANSLATION-NUANCE-EVIDENCE-v1` — completed historical T04 authorization; the evidence packet is canonically published
- `ACT-VS01-T05-DETERMINISTIC-STUDY-RUNTIME-v1` — completed; the canonical T05 runtime is persisted
- `ACT-VS01-T06-SYNTHETIC-PAGE-FIXTURE-v1` — completed historical T06 authorization; the fixture is canonically published
- `ACT-VS01-T07-R01-BENCHMARK-HARNESS-v1` — completed historical T07 harness authorization; operational publication is complete
- `ACT-VS01-T08-FULL-RUNTIME-PAIR-v1` — completed historical T08 implementation authorization; Hotfix01 and operational publication are complete
- `ACT-VS01-T09A-STUDY-WORKSPACE-PROJECTION-v1` — completed T09A canonical Study workspace projection authorization
- `ACT-VS01-T09B-LOOPBACK-STUDY-WEB-v1` — completed historical T09B authorization; implementation is merged at `3f52895459aefb84e6e6a7da8870f12e5f653e76`; T09-OP01 remains optional and deferred

## Preimplementation design status

The approved design baseline and all completed artifacts remain intact. W00C, VS01-T01, and R02 are merged historical foundation. `VS01-T02` is complete, the canonical archive is initialized, six authoritative source snapshots are admitted, and source acquisition is closed for VS-01. `VS01-T03`, `VS01-T04`, and `VS01-T06` are complete and canonically published. `VS01-T05` is complete and persisted. `VS01-T07` operational publication is complete. `VS01-T08` implementation, Hotfix01, and operational publication are complete. `VS01-T09A`, `VS01-T09-ERRATA-01`, and `VS01-T09B` are complete and merged. The Lab is `PAUSED_AFTER_VS01_T09B`. `VS01-T09-OP01` is optional editorial acceptance, deferred indefinitely, and not on the critical path. `VS01-T10` and later original tasks remain unstarted and unauthorized. Training, learned-model serving or conversion, cloud-training, adapted-model hosting, and `TNEVAL-A4` paths remain dormant pending the conjunctive DR-31 training-reactivation gate in section 21. `TNEVAL-A0` through `TNEVAL-A3` remain unstarted and unauthorized; A1–A3 are eligible only for a separately bounded API-evaluation authority and are not gated by training reactivation.

Clean-room review: [`audits/PREIMPLEMENTATION-CLEAN-ROOM-REVIEW-2026-08-17.md`](audits/PREIMPLEMENTATION-CLEAN-ROOM-REVIEW-2026-08-17.md).
