# DR-24 — Experiment Ladder and Promotion Gates

| Field | Value |
|---|---|
| Design ID | `DR-24` |
| Status | `APPROVED` |
| Approval date | 2026-08-16 |
| Project owner | Joseph Abbud |
| Product, benchmark, and experiment designer | ChatGPT |
| Independent implementation and evidence reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2 and supplements; DR-03; DR-04; DR-05; DR-06; DR-07; DR-08; DR-09; DR-10; DR-11; DR-12; DR-13; DR-14; DR-15; DR-16; DR-17; DR-18; DR-19; DR-20; DR-21; DR-22; DR-23 |
| Implementation authority | GPT-5.6 Sol exclusively implements and repairs the approved experimental machinery and frozen experiment designs |
| Execution authority | GPT-5.6 Luna may execute only frozen, reviewed Lambda Cloud campaigns delegated by Sol through the approved run controllers; Luna may not modify code, data, benchmark cases, models, objectives, thresholds, budgets, storage destinations, or scientific interpretation |
| Benchmark-content authority | ChatGPT designs and generates benchmark content; Joseph reviews and approves it; qualification-matched SMEs validate specialist `REV-P2` records |
| Approved cloud provider | Lambda.ai / Lambda Cloud only for project-controlled cloud training and evaluation |
| Authoritative artifact destination | Owner-controlled external MacBook Pro storage volume connected through Thunderbolt; Lambda storage is temporary scratch only |
| Budget status | This design allocates planning envelopes and gates only. It does not authorize any billable run. Every campaign still requires a separately approved immutable envelope and live price verification. |
| Approved change | Establishes the complete readiness, baseline, model-family, product-first, clean-Base, preference, capacity, MVP, final-evaluation, and optional extension experiment DAG; defines evidence levels, promotion semantics, hard-gate precedence, budget release, review boundaries, negative-result handling, and the exact conditions under which a model, checkpoint, system, or public preview may advance |

## 1. Purpose

DR-18 defines the available training stages and what each stage is intended to learn.

DR-20 and DR-21 define what the benchmark measures and how benchmark cases become authoritative.

DR-22 defines how evaluation campaigns are executed and how prior-art systems are reproduced.

DR-23 defines how approved training jobs are executed, checkpointed, archived, resumed, and audited.

DR-24 defines **which experiments occur, in what dependency order, what each experiment is allowed to claim, which evidence is required to advance, when the program branches, when it converges, when it stops, and how the approved $3,500 active compute cap is released stage by stage**.

A technically valid training run can still be a scientifically invalid experiment if:

- The benchmark has not demonstrated content, construct, scorer, or discrimination validity;
- The A0 runtime has not been measured before weight adaptation;
- A model family is selected from vendor claims or one aggregate score;
- Product-first and clean-Base lineages are mixed together;
- A stage advances because loss fell even though the named product capability did not improve;
- A small positive result is promoted without a matched baseline, protected-capability checks, or uncertainty estimates;
- An expensive main run begins before a bounded pilot establishes stability and value;
- A failed family retains later budget merely because funds were previously allocated;
- A public MVP waits unnecessarily for specialist `REV-P2` review even though deterministic `REV-P0` and source-verifiable `REV-P1` capability are already useful;
- A public preview overclaims specialist authority before appropriate SMEs participate;
- A larger model is trained merely because it outperforms a compact model on generic reasoning;
- A compact model is declared sufficient merely because it is cheap;
- An architecture extension is attempted before evidence shows a representational deficit;
- Sol redesigns a failed experiment during implementation;
- Luna changes a live campaign to keep it running;
- A cloud-only artifact is used to support a promotion decision before the authoritative external archive is verified;
- A weighted average hides a critical source, citation, safety, rights, multilingual, or multimodal hard failure;
- More credits are treated as a reason to keep training after the named hypothesis has failed.

DR-24 is intended to prevent those failures.

## 2. Governing principle

> **Biblical Scholar Lab will advance through a preregistered, branch-capable experiment graph in which every node repairs one named deficit, consumes one bounded evidence and budget envelope, preserves one immutable parent and comparison set, and ends in an explicit promotion, limitation, repair, redesign, stop, collaboration-preview, or release decision. A successful engineering run is not automatically a successful scientific experiment; a statistically detectable change is not automatically a practically valuable capability gain; and no aggregate score may override a hard evidentiary, rights, safety, retention, reproducibility, archival, or governance failure.**

The intended program is:

```text
approved designs and benchmark blueprints
    → implementation/readiness gates
    → valid public/private benchmark alpha
    → complete A0 runtime and prior-art baselines
    → no-training model-family and capacity screen
    ├── product-first fast path
    │       → source-verifiable scholarly behavior
    │       → bounded preference shaping if needed
    │       → MVP-01 expert-collaboration preview
    │
    └── clean-Base research path
            → adaptation strategy smoke
            → ancient/context CPT pilot
            → selected main CPT, if justified
            → Translation Nuance mid-training
            → scholarly and retrieval/tool SFT
            → preference ablation, if justified

product-first and clean-Base candidates
    + high-capacity comparators
    + prior art
    + human references
    → private and fresh final comparison
    → compact, tiered, large, specialist, or stop decision
    → optional SME-P2, mobile, capacity, or architecture-extension programs
```

The graph deliberately allows the product-first path to reach `MVP-01_EXPERT_COLLABORATION_PREVIEW` **before** main continued pretraining or specialist `REV-P2` gold is complete.

## 3. Experiment authority and record types

### 3.1 ChatGPT

ChatGPT owns:

- Experiment hypotheses;
- Subject and baseline selection;
- Benchmark and evidence conditions;
- Primary, secondary, protected, and hard-failure metrics;
- Minimum practically important differences;
- Confidence and repeated-run requirements;
- Data, objective, component, and ablation design;
- Budget recommendations and stop rules;
- Promotion logic;
- Scientific interpretation;
- Experiment amendments after unexpected evidence;
- Public-claim boundaries.

Every executable experiment receives an immutable, content-hashed:

```text
ExperimentDesignRecord
```

approved by Joseph before Sol implements or Luna executes it.

### 3.2 Joseph Abbud

Joseph retains sole authority to:

- Approve or reject each experiment design;
- Authorize each billable campaign envelope;
- Approve pull requests and merge to `main`;
- Approve checkpoint or system promotion;
- Approve budget reallocation;
- Approve MVP or public release;
- Approve provider, storage, or program-scope changes;
- Stop the program.

### 3.3 GPT-5.6 Sol

Sol may:

- Implement the approved experiment;
- Select design-neutral code organization and equivalent engineering mechanics;
- Validate that the implementation conforms to the approved design;
- Propose scientific changes with evidence;
- Delegate frozen mechanical execution to Luna;
- Produce the consolidated implementation and run handoff.

Sol may not independently change:

- Hypotheses;
- Subjects or parents;
- Data eligibility or mixture;
- Benchmark cases or split;
- Objective or trainable components;
- Model, tokenizer, reasoning mode, precision, or context policy;
- Thresholds;
- Retry or budget rules;
- Promotion interpretation.

A scientific change requires:

```text
BLOCKED_REQUIRES_EXPERIMENT_DESIGN_REVIEW
```

### 3.4 GPT-5.6 Luna

Luna may execute only through approved `campaignctl`, `evalctl`, or `trainctl` operations inside one frozen Sol-led root turn.

Luna may not author code, repair code, change configuration, replace a model, tune a parameter, alter a case, reinterpret a gate, raise a budget, substitute a cloud provider, or change an artifact destination.

### 3.5 Canonical records

The experiment program distinguishes:

```text
ExperimentProgram
ExperimentNode
ExperimentDesignRecord
ExperimentCampaignEnvelope
ExperimentExecutionRecord
ExperimentEvidenceBundle
ExperimentReviewRecord
PromotionRecommendation
OwnerPromotionDecision
BudgetReleaseRecord
LineageTerminationRecord
PublicClaimRecord
```

Implementation results never overwrite the approved design. A design amendment creates a new design revision and invalidates unexecuted envelopes based on the old revision.

## 4. The program is a directed acyclic graph—not one mandatory linear pipeline

The approved scientific graph contains several branches.

### 4.1 Shared foundation branch

Builds and validates:

- Benchmark content and scoring;
- Corpus vertical slice;
- Deterministic tools and evidence graph;
- Runtime Scholar Harness;
- Evaluation harness;
- Training harness;
- External archive and Lambda execution controls;
- A0 system baselines;
- Prior-art baselines;
- Model-family and capacity screening.

### 4.2 Product-first branch

Uses the strongest post-trained compact checkpoint under the A0 runtime and adds only the smallest training intervention needed to produce useful, source-verifiable `REV-P1` behavior.

This branch is the preferred route to the expert-collaboration MVP.

### 4.3 Clean-Base research branch

Tests whether ancient/context CPT, Translation Nuance mid-training, scholarly SFT, and retrieval/tool SFT add measurable capability beyond A0 and product-first adaptation.

This branch supplies the cleanest scientific attribution.

### 4.4 Capacity branch

Evaluates 27B–31B models as inference-only capacity comparators before any adaptation budget is authorized.

### 4.5 Optional extension branches

Remain separately gated:

- `REV-P2` specialist annotation and training;
- 31B adaptation;
- DR-12 A2–A5 architecture extensions;
- Mobile student distillation and quantization;
- Additional modern languages;
- Full Hebrew Bible expansion;
- Specialist manuscript-image programs.

No optional branch is implied by the success of an earlier node.

## 5. Evidence levels and permitted claims

Every experiment result receives one evidence level.

### `EL-0_IMPLEMENTATION_CONFORMANCE`

Supports claims that:

- The code follows the design;
- Schemas and state transitions work;
- Reference and production engines agree within approved tolerance;
- Checkpoint, resume, archive, and cleanup behavior works.

It does not support a scholarly capability claim.

### `EL-1_SCREENING`

Supports:

- Elimination of a clearly unstable, incompatible, materially weak, or prohibitively expensive option;
- Selection of candidates for a stronger experiment;
- Provisional cost and throughput estimates.

A positive EL-1 result does not support final model promotion or public superiority claims.

### `EL-2_STAGE_PROMOTION`

Requires:

- A valid benchmark subset;
- A preregistered primary effect;
- Matched baselines or ablations;
- Protected-capability checks;
- Complete failure accounting;
- Reproducible artifacts and archive receipts;
- Appropriate uncertainty or repeatability evidence.

Supports promotion to the next experimental stage.

### `EL-3_PRODUCT_PREVIEW`

Requires:

- Authoritative `REV-P0` and reviewed `REV-P1` public-safe evidence;
- Full runtime and auditability;
- Rights and privacy clearance;
- Public reproducibility subset;
- No disqualifying hard failure;
- Honest limitations and `SME_REVIEW_PENDING` labels.

Supports `MVP-01_EXPERT_COLLABORATION_PREVIEW`.

### `EL-4_FINAL_RESEARCH_CLAIM`

Requires:

- Private final evaluation;
- Fresh post-freeze challenge cases;
- Human or SME evidence appropriate to the claim;
- Final frozen systems;
- Cluster-aware statistics;
- Public-safe result and failure reporting;
- No unresolved release-blocking incident.

Supports final research conclusions and later public product or model claims.

A result may support different evidence levels for different capabilities.

## 6. Promotion decisions

Every node ends with exactly one approved disposition:

```text
PROMOTE
PROMOTE_WITH_LIMITATIONS
CONTINUE_SCREENING
REPAIR_IMPLEMENTATION_AND_REPEAT
REDESIGN_EXPERIMENT
DEFER_PENDING_BENCHMARK_VALIDITY
DEFER_PENDING_SME
DEFER_PENDING_RIGHTS_OR_ACCESS
NO_GO_STAGE
STOP_LINEAGE
ESCALATE_TO_CAPACITY_COMPARATOR
AUTHORIZE_OPTIONAL_EXTENSION_DESIGN
RELEASE_MVP_01
DO_NOT_RELEASE
STOP_PROGRAM
```

`PROMOTE_WITH_LIMITATIONS` must record:

- The exact limitations;
- Which claims remain prohibited;
- Which routes must abstain or escalate;
- Which benchmark groups remain unsupported;
- When the limitation expires or is reviewed.

A promotion decision is not encoded into the model or runtime automatically. ChatGPT issues the recommendation after reviewing the complete evidence; Joseph approves, rejects, or modifies the project decision.

## 7. Hard-gate precedence

Every scientific decision follows this order.

### Gate 0 — Identity and integrity

Required:

- Exact design and campaign hash;
- Clean reviewed code identity;
- Exact subject, model, tokenizer, data, benchmark, scorer, runtime, hardware, provider, and storage identity;
- Complete requested-sample and attempt accounting;
- No unapproved live mutation.

Failure invalidates the experiment.

### Gate 1 — Rights, privacy, security, and benchmark firewall

Required:

- Authorized data, provider, model, and output operations;
- Private and fresh holdouts protected;
- User-private and restricted evidence correctly routed;
- No credential, secret, prompt-injection, or provider-substitution incident.

Failure blocks promotion regardless of score.

### Gate 2 — Artifact, archive, and provider closeout

Required:

- Canonical artifacts transferred to the approved external Thunderbolt archive;
- Hash and load verification completed where required;
- `ArtifactArchiveReceipt` present;
- Lambda instances terminated;
- Temporary filesystems and scratch cleaned under policy;
- Actual cost reconciled.

A cloud-only result is nonpromotable.

### Gate 3 — Benchmark and scorer validity

Required:

- Cases valid for the claim;
- Scorers calibrated for the track and mode;
- Sufficient independent families;
- No unresolved gold or leakage incident;
- Evidence conditions support the conclusion.

Failure returns the program to benchmark design rather than model training.

### Gate 4 — Hard-failure caps

No weighted score may override:

- Fabricated source or passage;
- Unsupported central citation;
- Source-type confusion;
- Certain retroversion from underdetermined evidence;
- Hidden pivot affecting the conclusion;
- Private or restricted-data leakage;
- Harmful spiritual-authority behavior;
- Material multilingual or multimodal collapse;
- Lost user correction or counterevidence through compaction;
- Other track-specific `HF-1` or promotion-blocking `HF-2` failures.

### Gate 5 — Primary capability effect

The named capability must improve by the preregistered minimum practically important difference or satisfy the approved noninferiority objective.

A lower training loss, higher preference margin, or better generic benchmark does not satisfy this gate by itself.

### Gate 6 — Protected-capability retention

General reasoning, ancient and modern languages, multimodality, long context, tools, citations, calibration, safety, and runtime behavior must remain within approved bounds.

### Gate 7 — Reproducibility and robustness

Required evidence depends on the node, but may include:

- Independent seed or attempt confirmation;
- Same-environment resume equivalence;
- Backend equivalence;
- Position, language, modality, or perturbation robustness;
- Family-level confidence intervals;
- Human or SME confirmation.

### Gate 8 — Practical utility and cost

The gain must justify:

- Training and inference cost;
- Latency and memory;
- Deployment complexity;
- Maintenance and rights burden;
- Additional review requirements.

If two candidates are practically equivalent, the lower-cost, simpler, more reproducible, and more releasable option is preferred.

### Gate 9 — Governance approval

ChatGPT recommends the disposition. Joseph approves it.

## 8. Threshold and metric preregistration

Before a campaign becomes executable, its `ExperimentDesignRecord` freezes:

```text
primary capability metrics
minimum practically important difference
noninferiority margins
protected-capability margins
hard-failure caps
family and cluster units
confidence or repeated-run method
missing/error treatment
multiple-comparison policy
budget and runtime cap
stop and futility rules
promotion decision table
```

Thresholds may be amended after new evidence only by:

1. Freezing the current result without applying the revised rule;
2. Recording why the original threshold was invalid or insufficient;
3. Approving a new design revision;
4. Applying the new threshold prospectively to a new campaign or clearly labeled rescoring analysis.

A threshold cannot be changed merely because a favored model narrowly missed it.

## 9. Practical equivalence and Pareto selection

Candidate selection proceeds lexicographically:

1. Remove hard-gate failures;
2. Determine whether the primary effect is established;
3. Apply protected-capability gates;
4. Identify the Pareto frontier across capability, reliability, cost, latency, memory, rights, and release suitability;
5. Apply the DR-02 planning weights only among candidates that survive the preceding gates;
6. Treat differences below the approved practical threshold as ties;
7. Prefer the simpler and cheaper tied candidate unless another role-specific capability justifies the added complexity.

No model family wins from a single aggregate score.

Different role-specific winners are permitted:

```text
compact primary
large fallback
multimodal front end
clean research lineage
mobile student
specialist verifier
```

## 10. Benchmark readiness before model selection

Before any result controls family selection or model promotion:

- Every selection-controlling track meets DR-21’s minimum independent-family floor;
- Translation Nuance contains at least the approved major-claim floor;
- Known-correct, known-hard-failure, weaker, stronger, and human responses demonstrate discrimination;
- Scorers pass their authority gates;
- Relationship clusters and private splits are frozen;
- The private final set remains unused;
- The selected screening subset is explicitly separated from later final claims.

A smaller developmental set may support implementation conformance and obvious elimination. It may not support a definitive family winner.

## 11. Readiness gates before scientific experiments

The following logical gates must close before the first adaptation campaign.

### `RDY-00_DESIGN_AND_AUTHORITY`

Requires:

- DR-01 through DR-28 approved for the involved components;
- DR-29 approved before mobile work;
- Public repository and branch-protection governance active;
- Root `AGENTS.md` and experiment-authority contracts active;
- Sol/Luna identities and permissions verified.

### `RDY-01_CORPUS_AND_RIGHTS_VERTICAL_SLICE`

Requires:

- Rights registry and evidence;
- Immutable acquisition and normalized vertical-slice corpus;
- Graph, TNC, linguistic, scholarship, and page records;
- Stage eligibility and split firewall;
- Corpus health, leakage, overlap, and tokenization report.

### `RDY-02_BENCHMARK_ALPHA`

Requires:

- Approved family blueprints;
- Authoritative `REV-P0` and reviewed `REV-P1` cases sufficient for the planned screening claims;
- Scorers and hard-failure rules;
- Public/private separation;
- Benchmark-validity pilot.

### `RDY-03_RUNTIME_AND_EVALUATION_CONFORMANCE`

Requires:

- Reference runtime engine;
- LangGraph adapter conformance;
- Reference evaluation engine;
- Inspect adapter conformance;
- Exact tools and evidence packets;
- Runtime audit receipts;
- Sandbox and provider routing.

### `RDY-04_TRAINING_HARNESS_CONFORMANCE`

Requires DR-23:

```text
TH-00 through TH-06
```

including model-family smokes, failure injection, exact/qualified resume, `trainctl`, external archive, Lambda-only execution, provider cleanup, and Luna permissions.

### `RDY-05_OPERATIONAL_CLOSEOUT`

Requires one nonauthoritative end-to-end Lambda smoke proving:

- Live price capture;
- Launch and watchdog;
- Run-local scratch;
- Checkpoint generation;
- Owner-controlled transfer to the Thunderbolt archive;
- Hash/load verification;
- Archive receipt;
- Provider termination and cleanup;
- Cost reconciliation.

This gate supports execution readiness only, not model capability.

## 12. Experiment graph overview

| ID | Node | Branch | Primary question | Maximum claim level |
|---|---|---|---|---|
| `EXP-00` | A0 vertical-slice system validation | Shared | Does the full untrained runtime produce a valid, auditable research workflow? | `EL-1` then `EL-2` for component promotion |
| `EXP-01` | Prior-art reproduction | Shared | How do Rhema and Timms systems perform under author-native and normalized conditions? | `EL-1`/`EL-2` by reproduction tier |
| `EXP-02` | No-training family and capacity screen | Shared | Which compact and large families are viable under our tasks and runtime? | `EL-1`; selected compact finalists may reach `EL-2` |
| `EXP-03` | Runtime, context, and evidence ablations | Shared | Which system components add capability beyond model-only or ordinary RAG? | `EL-2` |
| `PF-01` | Product-first scholarly adaptation | Product-first | Can the strongest post-trained compact model reach useful `REV-P1` behavior with minimal PEFT/SFT/RAFT? | `EL-2` |
| `PF-02` | Product-first preference pilot | Product-first | Does reviewed preference data improve named behavior beyond SFT/chosen-only controls? | `EL-2` |
| `MVP-01` | Expert Collaboration Preview gate | Product-first or A0 | Is the public-safe P0/P1 system useful and honest enough to recruit SMEs? | `EL-3` |
| `CB-01` | Compact Base adaptation-strategy smoke | Clean Base | Which family and update/replay strategy is stable and promising? | `EL-1`/`EL-2` |
| `CB-02` | Ancient/context CPT pilot | Clean Base | Does CPT repair measured ancient/domain deficits without unacceptable forgetting? | `EL-2` |
| `CB-03` | Main ancient/context CPT | Clean Base | Does a scaled selected CPT run deliver practically useful gains? | `EL-2` |
| `CB-04` | Translation Nuance mid-training | Clean Base | Does structured TNC training improve causal diagnosis beyond token-matched controls? | `EL-2` |
| `CB-05` | Scholarly SFT | Clean Base | Can the clean lineage perform approved scholarly operations and answer contracts? | `EL-2` |
| `CB-06` | Retrieval/tool-aware SFT | Clean Base | Does training improve evidence/tool use beyond prompting and runtime alone? | `EL-2` |
| `PREF-01` | Selected-lineage preference ablation | Convergence | Which preference method, if any, improves behavior beyond SFT and chosen-only SFT? | `EL-2` |
| `SYS-01` | Final system comparison and routing | Convergence | Which compact, tiered, large, or specialist architecture should be retained? | `EL-4` after final/fresh review |
| `SME-01` | Specialist P2 validation program | Collaboration | Which provisional specialist cases become authoritative gold? | `EL-4` for the reviewed claims |
| `OPT-CAP-01` | Large-model adaptation | Optional | Is large-model adaptation worth its cost beyond inference-only capacity? | Separately gated |
| `OPT-ARCH-01` | DR-12 A2–A5 extension | Optional | Does a measured representational deficit justify specialized architecture? | Separately gated |
| `OPT-MOB-01` | Mobile student and quantization | Optional | Which bounded capabilities can be delivered locally? | Separately gated under DR-29 |

## 13. `EXP-00 — A0 vertical-slice system validation`

### Hypothesis

A project-untrained foundation model behind the complete deterministic tools, Translation Nuance Semantic Kernel, Context Composer, Runtime Scholar Harness, verification system, and public-safe vertical-slice evidence can outperform the same model alone and ordinary unstructured RAG on source-verifiable tasks.

### Required subjects

At minimum:

```text
model alone
model + static system prompt
model + unstructured RAG
model + deterministic tools
model + structured evidence packet
complete A0 runtime
```

One provisional compact post-trained model may be used to validate the pipeline. That choice does not select the final model family.

### Required task coverage

- Passage and edition identity;
- Translation comparison;
- Clear textual-variant versus translation-choice cases;
- Citation entailment;
- Word-study fallacy correction;
- Scope and anti-over-refusal;
- One multilingual path;
- One page-image path;
- One long-context or compaction path;
- One evidence-insufficiency or abstention case.

### Promotion gate

A0 advances when:

- The benchmark and runtime distinguish known-correct and known-failure fixtures;
- The complete runtime improves at least one named capability over ordinary RAG without creating a new hard failure;
- Exact tools and evidence packets are actually used where required;
- The audit receipt reconstructs the result;
- Latency and cost are acceptable for continued baseline work.

If A0 does not improve evidence-grounded behavior, the project repairs the architecture, benchmark, tools, or retrieval **before** training model weights.

## 14. `EXP-01 — Prior-art reproduction`

### Subjects

Mandatory where artifacts permit:

```text
Rhema BibleAI
Timms Bible AI Assistant
```

Conditions follow DR-22:

```text
author-native
quantized and full-precision where available
normalized model-only
model plus BSL A0 runtime
```

### Purpose

- Establish a credible baseline against existing Bible-domain work;
- Identify reusable design ideas and public failure modes;
- Determine whether our runtime adds value to existing weights;
- Prevent novelty claims that prior art already invalidates.

### Promotion gate

The result must receive an explicit reproduction tier and list every missing artifact or deviation.

A weights-only run cannot support claims about the author’s full application.

Prior-art performance does not block the project merely because it is strong. It changes the minimum value our system must demonstrate.

## 15. `EXP-02 — No-training model-family and capacity screen`

### Compact product candidates

The current DR-11 mandatory set is reverified immediately before execution.

The initial product candidates are expected to include the approved Qwen, Gemma, and Ministral compact post-trained variants.

### Compact Base candidates

Base models receive role-appropriate probes such as:

- Tokenization and ancient-script efficiency;
- Perplexity or completion likelihood;
- Fixed evidence interpretation;
- Model-family training-stack compatibility.

They are not ranked as conversational products before post-training.

### Capacity comparators

The approved larger candidates are inference-only during the initial screen.

### Conditions

At minimum:

```text
COMMON_DENOMINATOR_DIRECT
FAMILY_NATIVE_BEST_PRACTICE
BSL_A0_PRODUCT_RUNTIME
full-book/full-NT and hybrid context where relevant
reference and optimized inference paths
```

### Selection logic

- Every candidate must pass hard gates;
- Translation Nuance and original-language analysis remain the largest planning category;
- Role-specific Pareto fronts are produced;
- Ordinarily no more than two compact families advance to expensive target-size adaptation smoke;
- A third may advance only if it preserves a materially distinct capability, release advantage, or cost frontier;
- A model may be retained as a multimodal or mobile candidate without winning the primary text-reasoning role.

### Large-model capacity gate

A large candidate becomes eligible for a separate adaptation design only if it demonstrates, on the reconciled capacity-sensitive subset:

- The DR-02 provisional eight-point absolute improvement; **or**
- At least a 50% reduction in the designated epistemic hard failures;

and the result survives blinded expert confirmation, practical-effect review, and evidence that the gain is not merely verbosity or citation-format imitation.

The exact score scale and confidence treatment are frozen before this becomes executable.

## 16. `EXP-03 — Runtime, context, and evidence ablations`

This node isolates the value of system architecture before model adaptation.

Mandatory ablations include, where applicable:

```text
focused passage context
book context
full New Testament
RAG only
full NT + RAG
full NT + tools + RAG
structured evidence packet
with/without TNSK
with/without Page Evidence Kernel
with/without claim verification
with/without compaction and rehydration
compact versus large model under identical evidence
```

The full-New-Testament mode advances only if it improves the named canon-wide or cross-book task enough to justify its latency, cost, distractor, and position risks.

Focused tools and evidence remain the default when full-canon context is not materially better.

## 17. `PF-01 — Product-first scholarly adaptation`

### Entry condition

- A compact post-trained product candidate survives `EXP-02`;
- A0 identifies named behavior deficits not adequately repaired by prompts, tools, retrieval, or verification alone;
- Reviewed `REV-P0` and `REV-P1` training data exist;
- The parent checkpoint and adapter policy are frozen.

### First intervention

The default is a reversible PEFT path using:

- Scholarly SFT;
- Retrieval- and tool-aware SFT;
- General instruction, multilingual, multimodal, long-context, and safety replay as required.

The scholarly and retrieval/tool checkpoints remain distinguishable even if one campaign executes them efficiently.

### Matched controls

At minimum:

```text
unchanged post-trained parent + A0 runtime
parent + selected SFT only
parent + retrieval/tool SFT
```

### Gate

The product-first derivative advances when it:

- Improves named source-verifiable `REV-P1` behavior;
- Preserves or improves exact tool use and citation integrity;
- Does not create a material false-refusal, safety, multilingual, multimodal, or long-context regression;
- Remains disableable and parent-comparable;
- Demonstrates value beyond the unchanged A0 runtime.

If A0 already meets the MVP capability threshold, training is optional rather than ceremonial.

## 18. `PF-02 — Product-first preference pilot`

### Entry condition

A measured behavioral deficit remains after A0, SFT, retrieval/tool training, and runtime policy.

### Pilot

Use approximately:

```text
150–300 accepted pair-equivalents
```

from authoritative `REV-P0` and validated `REV-P1` partitions.

Required controls:

```text
SFT parent
SFT parent + runtime policy only
chosen-only SFT on the same accepted preferred responses
DPO
SimPO
adapter off/on
```

### Full P1 program

The selected method may expand toward:

```text
800–1,500 high-quality accepted pair-equivalents
```

only if the pilot shows that pairwise information adds value beyond chosen-only SFT and does not cause style, length, refusal, doctrinal, language, or evidence regressions.

Specialist `REV-P2` preference labels remain excluded until appropriate SME review.

## 19. `MVP-01 — Expert Collaboration Preview`

`MVP-01` is a capability and release gate—not a training-stage gate.

It may be reached through:

- A0 alone;
- A0 plus product-first SFT/RAFT;
- A0 plus product-first preference shaping;
- A later clean-Base derivative;

provided the system satisfies the same requirements.

### Required capability state

- Deterministic `REV-P0` functionality is complete and validated;
- A credible, public-safe `REV-P1` partition demonstrates source-verifiable scholarly behavior;
- Exact tools, evidence packets, citations, rights, and audit receipts are inspectable;
- The system can explain clear translation differences, avoid common lexical and textual-history errors, and admit insufficient evidence;
- Public multilingual and multimodal demonstrations remain within validated bounds;
- `REV-P2` cases are visibly labeled `SME_REVIEW_PENDING`.

### Required public artifacts

- Public branch-protected repository;
- Design and architecture records;
- Public-safe benchmark development and reproduction subset;
- Reproducible baseline and P1 evaluation report;
- Working bounded demo;
- Model, data, benchmark, evaluation, rights, and limitation cards;
- Expert collaboration brief and specialty queues;
- Public-safe error analysis;
- No private holdout or restricted evidence.

### Release gate

`MVP-01` does not require:

- Main CPT;
- Specialist P2 gold;
- Final model family selection;
- Public model weights;
- Full production readiness;
- Every planned language.

It does require ChatGPT review and Joseph’s release approval.

## 20. `CB-01 — Compact Base adaptation-strategy smoke`

### Purpose

Select one clean-Base family and one update/replay policy suitable for a meaningful CPT pilot.

### Candidates

Ordinarily the best one or two compact Base families from `EXP-02`.

### Planning scale

A planning range of:

```text
20–50 million effective tokens per approved condition
```

may be used, with exact content-, compute-, and cost-matched conditions frozen in the experiment design.

### Candidate conditions

May include:

```text
full-parameter Base CPT smoke
PEFT CPT smoke where technically meaningful
with/without general replay
approved multimodal preservation strategy
component freeze strategies
reference versus production backend
```

A smaller family sibling may be used for implementation mechanics only when architectural equivalence is demonstrated. It cannot select a target-size strategy without target-size confirmation.

### Gate

The selected strategy must demonstrate:

- Stable loss and gradients;
- Valid exposure and checkpoint behavior;
- Domain-loss movement;
- Acceptable protected-capability retention;
- No multimodal collapse;
- Practical throughput and memory;
- Successful archive and resume;
- Cost consistent with the next pilot.

A positive smoke result is not yet proof that CPT adds product value.

## 21. `CB-02 — Ancient/context CPT pilot`

### Purpose

Test whether the selected clean-Base CPT strategy repairs a named ancient-language or domain-representation deficit under realistic target-size conditions.

### Planning scale

The initial planning envelope is approximately:

```text
50–150 million effective tokens
```

The exact amount follows the strategy smoke and live measured throughput.

### Required controls

The design should include, at the cheapest scale capable of answering the question:

- Selected replay condition;
- A token- or compute-matched non-domain or alternative-mixture control where needed;
- Intermediate checkpoints;
- Parent-relative evaluation;
- Exposure and memorization audit;
- Short-, medium-, and long-context retention;
- Multilingual and multimodal retention.

### Gate

The pilot promotes only when:

- The named ancient/domain capability improves by the preregistered threshold;
- The improvement survives the matched control;
- A0 product behavior and protected capabilities remain within bounds;
- The measured curve and throughput justify a main run;
- No hard failure or archive defect occurs;
- The projected main-run cost remains within the approved active budget.

A plateau or small nonpractical gain ends or redesigns the CPT lineage.

## 22. `CB-03 — Main ancient/context CPT`

### Entry condition

Only a promoted `CB-02` pilot can authorize a main CPT design.

### Scale

The token budget, sequence curriculum, replay ratio, checkpoint cadence, and stop rules are designed from measured pilot evidence. DR-24 does not precommit to using the entire corpus or a nominal token count.

### Required behavior

- Early stopping on futility or regression;
- Intermediate model-only exports;
- Frequent protected-capability monitoring without tuning on the private final set;
- Complete exposure ledgers;
- External archive and Lambda cleanup;
- Parent and pilot comparisons.

### Gate

The selected checkpoint must deliver a practically meaningful domain gain that justifies its cost and serves as a better parent for Translation Nuance than the unadapted Base or product-first alternatives.

A checkpoint is not selected merely because it is the final step of the longest run.

## 23. `CB-04 — Translation Nuance mid-training`

### Hypothesis

Structured Translation Nuance objectives improve source-textual-state recognition, alignment, causal diagnosis, lineage, target-language constraint reasoning, and calibrated abstention beyond ordinary domain continuation.

### Required controls

At minimum, using the same approved parent:

```text
parent without TNC mid-training
parent + structured TNC mid-training
parent + token/compute-matched generic or unstructured domain continuation
```

Where affordable, a bounded `Base + TNC without prior CPT` control may test whether CPT is actually necessary for the TNC gain.

### Gate

The TNC derivative advances when it:

- Improves the signature Translation Nuance track by the approved practical threshold;
- Improves causal-chain and source-state accuracy—not merely fluent explanation;
- Preserves citation, source-type, original-language, multilingual, and multimodal behavior;
- Does not increase certain retroversion, intent inference, lexical fallacy, or translation-as-witness hard failures;
- Demonstrates value beyond token-matched unstructured continuation.

If structured training fails but A0 tools perform well, the authoritative TNC remains external and the model uses it through the runtime.

## 24. `CB-05 — Scholarly SFT`

This stage teaches the clean lineage to consume approved evidence, produce typed claims, present defensible alternatives, and render Brief, Study, and Scholarly answers.

Required comparison:

```text
clean lineage parent + A0 runtime
clean lineage + scholarly SFT + A0 runtime
product-first lineage under the same runtime
```

The stage advances only if the clean lineage becomes a credible conversational and scholarly subject without losing the clean attribution needed for the research comparison.

## 25. `CB-06 — Retrieval- and tool-aware SFT`

### Hypothesis

Training on relevant evidence, hard distractors, contradiction, missing evidence, tool failures, rehydration, rights-redacted inputs, and multilingual pivots improves runtime cooperation beyond prompting and SFT alone.

### Required comparison

```text
scholarly SFT parent + runtime
scholarly SFT parent + retrieval/tool SFT + runtime
```

### Gate

The stage must improve:

- Exact tool selection;
- Evidence fitness;
- Citation entailment;
- Distractor rejection;
- Missing-evidence clarification or abstention;
- Compaction rehydration;

without creating unconditional obedience to retrieved text or reducing the runtime’s authority.

## 26. `PREF-01 — Selected-lineage preference ablation`

Preference training is performed only on a frozen, selected SFT parent or on explicitly compared product-first and clean parents.

The algorithm ladder follows DR-19:

```text
ALG-P0 data/rubric validation
ALG-P1 small adapter smoke
ALG-P2 held-out behavior screen
ALG-P3 selected compact run
ALG-P4 optional cross-family confirmation
```

The exact chosen-only SFT, DPO, and SimPO comparisons remain mandatory.

Promotion requires improvement in the named behavior classes, no hard-failure or worst-group regression, and evidence that the adapter adds value beyond runtime policy and SFT.

Preference remains a reversible adapter unless a separately reviewed merged derivative is justified.

## 27. `SYS-01 — Final system comparison and routing decision`

### Subjects

The final frozen comparison should include, as available:

```text
best A0 untrained runtime
best product-first derivative
best clean-Base CPT/TNC/SFT derivative
preference adapter off/on
high-capacity comparator
prior-art systems
human reference groups
quantized derivative, if relevant
```

### Evaluation

Uses:

- Private model-selection cases for final internal selection;
- `PRIVATE_FINAL` only at the final approved stage;
- Fresh post-freeze challenge cases;
- Human and SME cases appropriate to the claims;
- Complete cost, latency, memory, rights, archive, and deployment analysis.

### Possible approved outcomes

```text
COMPACT_PRIMARY
TIERED_COMPACT_PLUS_LARGE
LARGE_PRIMARY
SPECIALIST_ROUTED_SYSTEM
A0_RUNTIME_WITHOUT_MAJOR_TRAINING
RESEARCH_SUCCESS_PRODUCT_NO_GO
HARNESS_OR_BENCHMARK_REDESIGN_REQUIRED
FRONTIER_ONLY_TEMPORARY_PRODUCT
STOP_PROGRAM
```

A tiered system is an accepted success outcome.

## 28. `SME-01 — Specialist P2 collaboration program`

This branch begins when `MVP-01` attracts appropriate collaborators or when existing experts become available.

It includes:

- Qualification-matched review of `SME_REVIEW_PENDING` cases;
- Multiple accepted analyses where disagreement is legitimate;
- Specialist benchmark expansion;
- P2 preference and SFT candidate review;
- Human reference performance;
- Fresh specialist cases;
- Joint publication and attribution policy where appropriate.

The program does not retroactively relabel owner approval or ChatGPT methodology review as SME validation.

## 29. Optional large-model adaptation gate

The initial 27B–31B allocation is inference-only.

A large-model adaptation design may be created only when:

- The capacity gate in `EXP-02` is satisfied;
- Compact-model failure is shown to be capacity-related rather than primarily evidence, retrieval, benchmark, or runtime-related;
- The expected gain is important enough to justify training and serving cost;
- A rights-compatible data and checkpoint path exists;
- A new budget allocation is approved.

The initial 31B adaptation reserve remains:

```text
$0
```

Any adaptation requires a new approved budget decision. The untouched $500 reserve is not automatically available.

## 30. Optional architecture-extension gate

DR-12 A2–A5 experiments require:

- A persistent named Translation Nuance or relational deficit;
- A0 and A1 failure to repair it;
- Evidence that the deficit is representational rather than caused mainly by missing data, weak retrieval, insufficient model capacity, or invalid evaluation;
- A falsifiable mechanism;
- A matched disableable ablation;
- Cost, latency, quantization, mobile, multilingual, and multimodal analysis;
- A separate experiment design and owner approval.

Core foundation-model modification remains A6 and requires a new design review.

## 31. Optional mobile and edge gate

Mobile work begins only after a successful parent system and DR-29 approval.

The initial goal is not to compress the full cloud scholar into a phone. It is to identify a bounded local capability set, likely using:

```text
2B–4B student
native OCR
local deterministic passage and linguistic tools
local compact retrieval
remote escalation for complex scholarly work
```

Every quantized or distilled derivative receives ancient-language, citation, tool, multilingual, multimodal, privacy, thermal, memory, and battery evaluation.

## 32. Main ablation matrix

The program should preserve, at minimum, evidence for:

```text
model alone
ordinary RAG
complete A0 runtime
product-first SFT/RAFT
clean Base CPT
clean Base CPT + TNC
clean Base CPT + TNC + scholarly SFT
clean Base CPT + TNC + scholarly SFT + retrieval/tool SFT
SFT versus SFT + preference
with versus without general replay
with versus without multimodal replay
with versus without multilingual native cases
focused context versus full NT versus hybrid
compact versus large model
high-precision versus quantized derivative
TNSK on/off
Page Evidence Kernel on/off
compaction/rehydration on/off
```

Not every comparison requires a main-scale training run. Proxy and selected checkpoints may answer some ablations.

## 33. Repeated-run and replication policy

### Screening failures

A catastrophic incompatibility, OOM, nonfinite loss, broken checkpoint, or hard failure may eliminate a candidate after one reproducible or independently confirmed occurrence when the cause is clear.

### Positive stage promotion

A positive result ordinarily requires one of:

- An independent repeat under the same frozen design;
- A second seed or attempt;
- Confirmation at a larger scale;
- Confirmation on a fresh or independently authored subset;
- Human or SME confirmation;
- A deterministic effect with negligible stochastic ambiguity.

The exact confirmation method is preregistered according to cost and construct.

### Expensive main runs

DR-24 does not require duplicating an entire expensive main CPT merely to satisfy a generic “two seeds” rule.

A major claim may instead combine:

- Proxy-stage replication;
- Stable intermediate-checkpoint trends;
- Final held-out and fresh evaluation;
- Resume and backend conformance;
- Parent-relative comparisons;
- Human or SME confirmation;
- Complete uncertainty and limitation reporting.

The report must disclose that only one main-scale training trajectory was executed when that is the case.

## 34. Checkpoint selection and early stopping

Checkpoint selection uses only approved development and model-selection evidence—not `PRIVATE_FINAL` or unused fresh cases.

The selection rule must be frozen before candidate checkpoints are compared and may include:

- Multi-objective Pareto selection;
- Primary metric with protected-capability constraints;
- Earliest checkpoint within a practical-equivalence band;
- Cost-normalized gain;
- Explicit abstention from selection if no checkpoint passes.

A run stops early when:

- Nonfinite or divergent behavior occurs;
- A hard failure is detected;
- Protected capabilities exceed approved regression limits;
- The primary effect is futile under the approved rule;
- Cost or runtime reaches the cap;
- Archive or provider safety requires termination;
- The experiment no longer answers the approved hypothesis.

No run continues merely because later checkpoints were planned.

## 35. Budget release and stage caps

The active project budget remains:

```text
Active hard cap: $3,500
Untouched reserve: $500
Known credits: approximately $4,000
```

The DR-02 allocation remains the planning authority:

| Program area | Planning cap |
|---|---:|
| Baselines, benchmark, tools, and RAG | $200 |
| Model-family screening | $200 |
| Compact adaptation smoke tests | $350 |
| 31B capacity evaluation | $150 |
| 31B adaptation reserve | $0 initially |
| Winning compact-model validation | $300 |
| Main domain adaptation | $850 |
| Translation mid-training | $400 |
| Scholarly SFT and preference work | $400 |
| Final evaluation and contingency | $650 |
| **Active total** | **$3,500** |
| **Untouched reserve** | **$500** |

These are caps—not targets.

The initial mapping from allocation to experiment nodes is:

| Program area | Principal nodes |
|---|---|
| Baselines, benchmark, tools, and RAG | `EXP-00`, `EXP-01`, selected `EXP-03` work |
| Model-family screening | `EXP-02` compact no-training screen |
| Compact adaptation smoke tests | `CB-01` and bounded product-first adaptation probes |
| 31B capacity evaluation | Inference-only large-model portion of `EXP-02` |
| Winning compact-model validation | `CB-02` CPT pilot and target-size confirmation |
| Main domain adaptation | `CB-03` selected main CPT lineage |
| Translation mid-training | `CB-04` structured TNC mid-training and controls |
| Scholarly SFT and preference work | `PF-01`, `PF-02`, `CB-05`, `CB-06`, and `PREF-01`, with only bounded alternative-lineage screens before one primary lineage receives full allocation |
| Final evaluation and contingency | `SYS-01`, fresh evaluation, approved reruns, and unforeseen validated operational failures |

The budget does **not** fund full-scale product-first and clean-Base training for every surviving family. Alternative families and lineages receive only the minimum screen needed to answer the comparison. Full-stage allocation is released to one selected primary lineage at a time unless a new owner-approved design reallocates funds. This prevents an apparently parallel experiment graph from becoming an uncontrolled multiplication of full training runs.

A failed experiment loses its later allocation. Unused funds return to the unallocated active pool and cannot be reassigned without owner approval. `MVP-01` has no automatic separate training allocation; it may use the public-safe artifacts produced by A0 or the product-first branch and only receives additional compute through an approved campaign.

Every campaign must use current Lambda pricing and provider availability. As of 2026-08-16, Lambda’s public instance table lists, among other options, 8× H100 SXM at $3.99 per GPU-hour, 4× H100 SXM at $4.09 per GPU-hour, 2× B200 at $6.89 per GPU-hour, 1× B200 at $6.99 per hour, and 1× GH200 at $2.29 per hour; these values are planning observations only and must be reverified before launch.[^lambda-pricing]

Lambda documents that on-demand instances are billed while they remain running until provider-side termination and that persistent filesystems continue billing while they exist.[^lambda-billing]

Budget calculations must therefore include:

- Environment setup;
- Download and initialization;
- Training or evaluation;
- Checkpointing;
- Transfer to the Thunderbolt archive;
- Hash and load verification;
- Provider termination;
- Filesystem cleanup;
- One approved failure allowance where appropriate.

## 36. Conditional campaign progression without review spam

One owner-approved experiment campaign may contain several frozen jobs and deterministic conditional transitions.

For example:

```text
compatibility smoke passes
    → run bounded throughput job

throughput and memory pass approved limits
    → run approved adaptation smoke

hard-failure or retention threshold triggers
    → stop campaign
```

Sol may delegate those mechanical transitions to Luna inside the same root turn when:

- Every job is specified in the same approved campaign envelope;
- The transition uses machine-checkable approved criteria;
- No code, data, model, objective, hyperparameter, threshold, hardware class, provider, or budget changes;
- The aggregate campaign remains within the approved cap;
- The full activity is reported in one consolidated Sol handoff.

A transition requiring scientific interpretation stops for ChatGPT review and owner decision.

This allows meaningful work to proceed without requiring a manual kickoff after every command or subagent invocation.

## 37. Review boundaries

A review is required after a Sol root turn that:

- Changes code or executable configuration;
- Produces a new benchmark or scorer implementation;
- Completes a scientific experiment;
- Produces a checkpoint proposed for promotion;
- Exposes a material unexpected result;
- Changes an artifact, rights, or storage state relevant to a decision;
- Reaches a public-release gate.

A separate review is not required for every Luna status poll, checkpoint transfer, or preapproved deterministic sub-job inside the same frozen root turn.

New implementation commits invalidate earlier code review. New scientific evidence invalidates only the conclusions that depended on the earlier evidence, not unrelated approved designs.

## 38. Experiment handoff requirements

Sol’s consolidated handoff for each experiment must include:

```text
approved design ID and hash
campaign ID and hash
implementation commit and PR
subjects and parent checkpoints
benchmark and split identities
corpus, mixture, and exposure identities
objective and trainable-component manifest
runtime, provider, hardware, kernel, and precision
requested and actual budget
run attempts, retries, failures, and stops
checkpoint and artifact identities
Thunderbolt archive receipts
Lambda termination and cleanup receipts
primary and protected metrics
hard failures and error taxonomy
cluster-aware statistics
prior-art reproduction tiers where applicable
public/private visibility
implementation-conformance declaration
unapproved design changes executed: none
```

Sol may summarize measurements and implementation observations. It may not assign the scientific promotion decision.

## 39. Negative and null results

A result remains valuable when it establishes that:

- A0 tools and RAG are sufficient;
- CPT does not add practical value;
- TNC mid-training does not improve causal diagnosis;
- Preference training teaches verbosity or refusal rather than evidence discipline;
- Full-NT context is inferior to focused retrieval;
- A larger model’s gain is not worth the cost;
- One model family is operationally unsuitable;
- A proposed architecture extension is unnecessary;
- A benchmark case is invalid or nondiscriminating.

Negative results must be preserved and reported. The program may stop a lineage while retaining its corpus, benchmark, tools, runtime, and methodological contributions.

## 40. Program-level stop conditions

The owner may stop the program at any point.

The scientific program should recommend `STOP_PROGRAM` when, after reasonable repair and evidence review:

- The benchmark cannot validly measure the intended constructs;
- Rights prevent the necessary evidence or release path;
- No tested open model plus approved runtime reaches a useful P1 capability level;
- Only an unaffordable or unreleasable model can meet the target;
- Hard safety, citation, privacy, or source-type failures remain uncontainable;
- Expert collaboration is unavailable for the claims the project wishes to make;
- The expected benefit no longer justifies the remaining cost and complexity.

Stopping the model-training program does not imply that the benchmark, semantic graph, Translation Nuance Core, tools, or public research artifacts lack value.

## 41. Principal hard failures

DR-24 treats the following as program hard failures:

- Executing a billable experiment without an approved `ExperimentDesignRecord` and campaign envelope;
- Sol or Luna altering scientific design during execution;
- Using the private final or fresh challenge sets for tuning, checkpoint selection, data generation, or prompt development;
- Promoting from training loss, preference accuracy, or generic benchmark gains without the named product capability;
- Changing a threshold after observing results without preserving the original decision;
- Averaging away a critical rights, safety, citation, source-type, language, modality, compaction, or artifact hard failure;
- Treating public translations, repeated files, or citations as independent evidence counts;
- Training a 31B model before the capacity-value and budget gates;
- Launching a DR-12 architecture extension before A0/A1 and representational-deficit gates;
- Claiming a model family winner from a developmental or invalid benchmark;
- Treating one stochastic run as definitive where repeatability is material;
- Hiding failed attempts, timeouts, refusals, OOMs, or archive failures;
- Promoting or resuming a cloud-only checkpoint without an authoritative external-archive receipt;
- Allowing Lambda billing or filesystems to continue after campaign close;
- Reassigning a failed stage’s unused budget without owner approval;
- Delaying `MVP-01` solely because specialist P2 validation is incomplete when P0/P1 publication gates are satisfied;
- Publishing specialist claims from `SME_REVIEW_PENDING` cases as validated gold;
- Continuing a stage merely to consume available credits;
- Claiming a public product or scholarly authority beyond the approved evidence level.

## 42. Decisions DR-24 locks

Approval would establish that:

1. The experiment program is a gated DAG rather than one mandatory linear training pipeline.
2. Product-first, clean-Base, capacity, MVP, SME, mobile, and architecture-extension branches remain separate.
3. The product-first branch may reach `MVP-01` before main CPT or P2 review.
4. Every experiment has a ChatGPT-authored, owner-approved immutable design record.
5. Sol implements and delegates frozen execution; Luna cannot change or interpret the experiment.
6. Evidence levels `EL-0` through `EL-4` constrain permitted claims.
7. Promotion uses lexicographic hard-gate precedence before aggregate weighting.
8. Thresholds and practical differences are preregistered.
9. Practical ties favor lower cost and simpler deployment.
10. Benchmark and scorer validity precede model selection.
11. Readiness gates close before adaptation.
12. A0 and prior-art baselines precede weight training.
13. Model-family screening is no-training first and role-specific.
14. Compact candidates are narrowed before target-size adaptation smoke.
15. Large models are inference-only until a separate capacity-value gate passes.
16. Product-first training is optional when A0 already meets the capability threshold.
17. Clean-Base CPT requires strategy smoke, pilot, and main-run gates.
18. Translation Nuance mid-training must beat token-matched controls.
19. Scholarly SFT, retrieval/tool SFT, and preference remain separately attributable.
20. `MVP-01` is capability- and release-gated, not tied to completion of the entire research curriculum.
21. Final selection may produce compact, tiered, large, specialist, A0-only, or no-go outcomes.
22. P2 collaboration remains a separate expert-validation program.
23. Architecture, large-model adaptation, and mobile work remain separately gated.
24. Positive claims receive fit-for-cost confirmation rather than one universal seed rule.
25. Checkpoint selection and early stopping are preregistered and private-final-safe.
26. The approved $3,500 active cap and $500 reserve remain intact.
27. Unused stage funds do not create automatic permission for another stage.
28. One Sol root turn may contain preapproved Luna sub-jobs without creating separate review boundaries.
29. Every completed experiment receives one consolidated evidence handoff.
30. Negative and null results remain first-class outcomes.
31. Every promotion and public claim requires ChatGPT review and owner approval.

## 43. Decisions intentionally deferred

DR-24 does not yet freeze:

- Exact experiment dates;
- Exact model repositories and revisions at execution time;
- Exact benchmark case IDs and final thresholds;
- Exact Lambda instance type, region, availability, or price;
- Exact training token counts beyond the approved planning envelopes;
- Exact sequence-length, optimizer, learning-rate, or replay values;
- Exact number of seeds or repeats for each experiment;
- Exact artifact-transfer cadence and retention count;
- Exact public model, adapter, or demo release;
- Exact SME partners;
- Exact final model or tiered routing architecture;
- Any billable campaign;
- Any 31B adaptation;
- Any A2–A6 architecture experiment;
- Any mobile or edge training.

Those are specified in later designs, benchmark batches, DR-25 campaign envelopes, DR-28 integrated contracts, DR-29 mobile design, and experiment-specific approvals.

## 44. Approval statement

> **Biblical Scholar Lab will use a preregistered, branch-capable experiment graph in which readiness, A0 system validation, prior-art reproduction, no-training model-family screening, runtime and context ablation, product-first adaptation, clean-Base continued pretraining, Translation Nuance mid-training, scholarly and retrieval/tool SFT, preference shaping, expert-collaboration preview, specialist review, capacity comparison, final system selection, and optional mobile or architecture extensions remain distinct, evidence-gated nodes. Every executable node will have a ChatGPT-authored and Joseph-approved immutable experiment design defining the named deficit, parent, subjects, data, benchmark, evidence mode, objective, trainable components, ablations, minimum practical effect, protected-capability margins, hard-failure caps, uncertainty method, budget, stop rules, and promotion table. The program will apply identity, rights, archive, benchmark-validity, hard-failure, primary-effect, protected-capability, reproducibility, utility, and governance gates in that order before any weighted comparison. The complete untrained A0 runtime and prior art will be measured before gradient updates; compact and large models will be screened without training before expensive adaptation; the clean-Base path will require strategy smoke, CPT pilot, selected main CPT, structured Translation Nuance controls, scholarly SFT, and retrieval/tool SFT; and preference optimization will require chosen-only SFT, DPO, and SimPO controls. Completion of authoritative `REV-P0` and credible public-safe `REV-P1` capability may trigger `MVP-01_EXPERT_COLLABORATION_PREVIEW` before main CPT, specialist `REV-P2` validation, final model selection, or weights release. Large-model adaptation, specialized Translation Nuance architecture, mobile distillation, and later languages will remain separate optional programs. Every campaign will run only on Lambda Cloud, retain canonical artifacts on the owner-controlled Thunderbolt archive, stop at immutable cost and safety limits, expose every failure and retry, and produce one consolidated Sol handoff for ChatGPT review; Luna may execute only frozen mechanical jobs; Joseph will retain sole authority over budget, merge, progression, checkpoint promotion, public claims, and release. Negative or null results will remain valid scientific outcomes, and no stage will continue merely because compute or credits remain.**

---

## References

[^lambda-pricing]: Lambda, “AI cloud pricing.” Current public on-demand instance rates and configurations are listed at <https://lambda.ai/pricing>. Prices and availability must be reverified immediately before every campaign.

[^lambda-billing]: Lambda Docs, “Billing overview.” Lambda documents that on-demand instances are billed from launch/health until provider-side termination and that filesystems continue billing while they exist: <https://docs.lambda.ai/public-cloud/billing/>.
