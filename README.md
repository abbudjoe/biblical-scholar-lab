# Biblical Scholar Lab — Design Baseline

This repository is the authoritative design and implementation record for Biblical Scholar Lab.

Governance implementation is closed. `VS01-T01` and its R02 APFS compatibility repair are merged historical foundation. `VS01-T02` and `ARCHIVE-PROFILE-BSL-ARCHIVE-v1` are approved, and `T02A-IMP` is the active code-only implementation task.

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

## Current implementation status

- W00A1a and W00C are merged historical governance implementation; governance implementation is closed.
- W00A1b, W00A2, W00B, and the dummy W01 proof are retired or canceled as VS-01 prerequisites.
- `VS01-T01` and R02 are merged historical archive/source-admission foundation.
- `ARCHIVE-PROFILE-BSL-ARCHIVE-v1` and `VS01-T02 — Canonical Archive Bootstrap and Raw Source Admission` are approved.
- `T02A-IMP — Archive Bootstrap Kernel` is active for code, contracts, schemas, and synthetic tests only.
- No real archive initialization or source acquisition is authorized.

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
- `ACT-VS01-T02A-ARCHIVE-BOOTSTRAP-KERNEL-v1` — active code-only T02A-IMP authorization; no real archive initialization or source acquisition

## Preimplementation design status

The approved design baseline remains intact. W00C, VS01-T01, and R02 are merged historical foundation. `ARCHIVE-PROFILE-BSL-ARCHIVE-v1` and `VS01-T02` are approved; `T02A-IMP` is active. Real archive initialization, source acquisition, and benchmark execution still require later approved activations and verification gates.

Clean-room review: [`audits/PREIMPLEMENTATION-CLEAN-ROOM-REVIEW-2026-08-17.md`](audits/PREIMPLEMENTATION-CLEAN-ROOM-REVIEW-2026-08-17.md).
