# Biblical Scholar Lab — Design Baseline

This repository is the authoritative pre-implementation design record for Biblical Scholar Lab.

Production code is intentionally absent. Approved product, scholarly, architecture, benchmark, experiment, governance, and execution decisions are recorded here before GPT-5.6 Sol implements them.

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

## Current approved baseline

- `DR-01` — Version-One Product Contract
- `DR-02` revision 2 — Scholarly Epistemology and Methodology, including the approved architecture-contract schedule, model-capacity and family-bake-off policy, Gemma budget posture, and mobile/quantization direction
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

Supporting official-source verification for DR-02 revision 2 is recorded under `design/evidence/`.
