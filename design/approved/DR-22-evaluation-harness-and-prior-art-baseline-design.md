# DR-22 — Evaluation Harness and Prior-Art Baseline Design

| Field | Value |
|---|---|
| Design ID | `DR-22` |
| Status | `APPROVED` |
| Approval date | 2026-08-16 |
| Project owner | Joseph Abbud |
| Benchmark and experiment designer | ChatGPT |
| Independent implementation and evidence reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2 and supplements; DR-03; DR-04; DR-05; DR-06; DR-07; DR-08; DR-09; DR-10; DR-11; DR-12; DR-13; DR-14; DR-15; DR-16; DR-17; DR-18; DR-19; DR-20; DR-21 |
| Benchmark-content authority | ChatGPT designs and generates; Joseph Abbud reviews and approves; qualification-matched SMEs validate `REV-P2` specialist gold |
| Implementation authority | GPT-5.6 Sol implements only the approved evaluation core, engine adapters, subject adapters, scorers, reports, sandboxes, reproducibility controls, and prior-art reproduction machinery |
| Execution authority | GPT-5.6 Luna may execute only frozen evaluation campaigns delegated by Sol under an approved campaign envelope; Luna may not modify code, cases, prompts, scorers, thresholds, subjects, or interpretations |
| Approved change | Establishes the framework-neutral evaluation core, deterministic reference engine, Inspect AI execution adapter, benchmark-to-engine projection, evaluation-subject and baseline taxonomy, prior-art reproduction tiers, normalized versus native elicitation conditions, inference-backend equivalence policy, generation/scoring separation, retry and failure semantics, private-holdout security, sandboxing, immutable result bundles, cost and statistical accounting, and initial Rhema BibleAI, Bible AI Assistant, model-family, frontier, external-benchmark, and human-reference baselines |

## 1. Purpose

DR-20 defines what the benchmark measures.

DR-21 defines how benchmark cases, gold boundaries, rubrics, review authority, and scoring semantics are created and governed.

DR-22 defines how approved benchmark cases are projected into executable evaluations, how models and complete systems become subjects, how prior art is reproduced without misrepresentation, how generation and scoring remain separately versioned, how errors and retries are handled, and how raw outputs become reproducible evidence for a scientific comparison.

A benchmark can be valid while its execution harness still creates invalid conclusions if:

- Different models receive different evidence, prompts, or budgets without disclosure;
- A base checkpoint is judged as though it were an instruction-tuned assistant;
- A model is evaluated through one optimized backend and another through a reference backend whose semantics differ;
- Retries silently reroll difficult samples;
- Failed, refused, timed-out, or malformed outputs are dropped from the denominator;
- A prior-art system is described as reproduced even though its exact weights, prompt, retrieval corpus, or runtime were unavailable;
- A model judge receives the answer contract or system identity in a way that creates leakage or bias;
- Private benchmark content is sent to an unauthorized external provider;
- A framework's logs become the sole audit record despite missing project-specific evidence, rights, or runtime identities;
- Generation and scoring are coupled so tightly that scorer changes require paying to regenerate every answer;
- Model-only and full-system results are blended into one score;
- Author-native, common-denominator, family-native, and product-runtime conditions are compared as though they were the same experiment;
- Cost, latency, token usage, tool calls, failures, fallbacks, and quantization are omitted from the result;
- A public benchmark or system created by a model developer is treated as an independent final examination without contamination analysis.

DR-22 is intended to prevent those failures.

It does **not** create benchmark cases, select final model winners, authorize a final public leaderboard, set every numerical promotion threshold, or approve a billable campaign. Those remain under DR-20, DR-21, DR-24, DR-25, approved benchmark batches, and owner-approved experiment designs.

## 2. Governing principle

> **Biblical Scholar Lab will own the semantic evaluation contract while adopting mature execution infrastructure for ordinary evaluation mechanics. Every evaluation will bind an immutable benchmark revision, subject artifact, elicitation condition, evidence mode, runtime and tool configuration, inference backend, generation policy, scorer revision, attempt history, rights state, and cost record. The execution framework may schedule, persist, resume, sandbox, log, and display an approved evaluation; it may not redefine the benchmark, silently change the subject, discard failures, reroll semantic outcomes, or become the source of scholarly truth. Prior-art systems will be reported at the level actually reproduced, with author-native and normalized conditions kept separate.**

The intended architecture is:

```text
approved benchmark cases and scoring contracts
    → project-owned Evaluation Core
    → immutable Evaluation Campaign Specification
    → project-owned subject and engine adapters
    → deterministic reference engine or Inspect AI execution engine
    → raw generation and tool/runtime traces
    → separately versioned scoring and human-review passes
    → project-owned Evaluation Result Bundle
    → statistical and error-analysis reports
    → ChatGPT review
    → Joseph Abbud promotion, redesign, or publication decision
```

## 3. The benchmark, evaluation core, and execution engine remain separate

The authoritative architecture distinguishes:

```text
Benchmark Content
    What the examination asks and what counts as defensible behavior

Evaluation Core
    How a benchmark case, subject, mode, budget, and scoring contract
    become one immutable evaluation request and result

Execution Engine
    How tasks are scheduled, persisted, resumed, sandboxed, and logged

Subject Under Evaluation
    Model, retriever, tool set, runtime, prior-art system, or human workflow

Scoring System
    How frozen outputs are evaluated under a frozen scorer revision

Reporting System
    How sample results become cluster-aware, multidimensional evidence
```

No execution engine owns the benchmark's semantic definitions.

No benchmark file imports a provider-specific model client as part of its authoritative content.

No model-provider response format becomes the project's public evaluation schema.

## 4. Logical evaluation planes

DR-22 defines eight logical planes.

### 4.1 Benchmark plane

Contains the approved DR-20/DR-21 records:

- Track and task-family identities;
- Case-family blueprints;
- Case and variant revisions;
- Evidence and answer contracts;
- Rubrics and hard failures;
- Review partitions;
- Public/private/fresh split state;
- Relationship and contamination clusters;
- Rights and source manifests.

### 4.2 Subject plane

Defines exactly what is being evaluated:

- Model-only checkpoint;
- Model plus system prompt;
- Retriever;
- Reranker;
- Deterministic tools;
- Runtime Scholar Harness;
- Prior-art application;
- Quantized or mobile derivative;
- Human reference workflow.

### 4.3 Elicitation plane

Defines:

- Prompt and chat template;
- Reasoning mode;
- Structured-output policy;
- Tool availability;
- Evidence packet;
- Context mode;
- Answer-depth mode;
- Sampling and output budget;
- Number of attempts or epochs.

### 4.4 Execution plane

Owns:

- Scheduling;
- Concurrency;
- Resource limits;
- Sandboxes;
- Checkpointing;
- Failure capture;
- Resumption;
- Provider calls;
- Local serving;
- Run control.

### 4.5 Trace and artifact plane

Captures:

- Raw model outputs;
- Tool calls and results;
- Retrieval results;
- Context and evidence packets;
- Runtime audit receipts;
- Errors, retries, and fallbacks;
- Token and cost usage;
- Image and multimodal inputs where permitted;
- Exact artifact hashes.

### 4.6 Scoring plane

Applies:

- Deterministic scorers;
- Structured semantic scorers;
- Source-grounded criteria;
- Human review;
- Calibrated model-assisted judges;
- Hard-failure checks;
- Abstention and calibration scoring.

### 4.7 Statistical plane

Aggregates over approved independent units such as case families or relationship clusters and produces uncertainty, effect size, worst-group, and cost reports.

### 4.8 Governance plane

Preserves:

- Design authority;
- Owner approval;
- SME state;
- Private-access state;
- Campaign authorization;
- Incident handling;
- Promotion decisions;
- Public-release state.

The planes may share one implementation repository, but their logical authorities remain distinct.

## 5. Canonical evaluation objects

The implementation will define at least the following project-owned logical records.

### `EvaluationSubjectSpecification`

Identifies:

```text
subject_id
subject_type
model or application artifacts
parent and derivative lineage
system prompt or policy
runtime or application commit
retriever and tool configuration
quantization and precision
provider and inference backend
capability declarations
rights and access constraints
```

### `ElicitationCondition`

Identifies:

```text
condition_id
comparison class
prompt and template revision
reasoning mode
structured-output mode
evidence mode
context mode
answer-depth mode
tool and retrieval permissions
sampling, seed, and budgets
```

### `EvaluationCampaignSpecification`

Binds:

```text
benchmark snapshot
case and split selection
subjects and conditions
scorer plan
model and judge roles
execution engine
sandboxes
failure and retry policy
cost and runtime caps
privacy and rights route
statistical plan
release and visibility state
```

### `EvaluationSampleRequest`

The immutable projection of one case, subject, condition, and attempt.

### `EvaluationAttemptRecord`

Records:

```text
attempt identity
start and completion state
model and provider calls
raw output
tool/runtime trace
errors and retries
usage and cost
fallbacks
artifacts and hashes
```

### `ScoringRunSpecification`

Binds one frozen output set to one exact scorer, rubric, judge, and human-review configuration.

### `SampleScoreRecord`

Preserves criterion-level values, hard failures, explanations, source evidence, reviewer or judge identity, confidence, and edit history.

### `EvaluationResultBundle`

The canonical project artifact containing:

```text
campaign and subject identities
all sample requests and attempt records
raw outputs and trace references
all scoring runs and histories
cluster-aware metrics
failure and retry accounting
cost, latency, token, and hardware use
rights and privacy state
public-safe projection state
content hash
```

### `EvaluationComparisonReport`

Provides paired deltas, uncertainty, practical effect size, worst groups, hard failures, costs, and limits without replacing the result bundle.

Framework-native task, sample, log, or score objects remain adapters around these records.

## 6. Evaluation subjects

Every subject declares one of the following types.

```text
MODEL_BASE_CHECKPOINT
MODEL_POST_TRAINED_CHECKPOINT
MODEL_ADAPTER_DERIVATIVE
MODEL_MERGED_DERIVATIVE
MODEL_QUANTIZED_DERIVATIVE
RETRIEVAL_PIPELINE
DETERMINISTIC_TOOL_SUITE
RUNTIME_HARNESS
END_TO_END_PRODUCT_SYSTEM
PRIOR_ART_MODEL
PRIOR_ART_APPLICATION
FRONTIER_API_CEILING
HUMAN_REFERENCE_WORKFLOW
```

### Base checkpoints

Base checkpoints are not judged as though they are fully post-trained assistants.

They may receive:

- Perplexity or target-completion measures;
- Fixed-format language and structure probes;
- Tokenization and context tests;
- Matched post-training after an approved stage;
- Evidence-interpretation tasks under a minimal explicit prompt where scientifically meaningful.

Their lack of instruction following is not treated as proof of weak ancient-language representation.

### Post-trained checkpoints

Post-trained checkpoints receive model-only, common-denominator, family-native, and full-runtime conditions as applicable.

### Complete systems

A system result identifies all model, retrieval, tools, policies, context, runtime, and verification components. It is never labeled as a model-only result.

## 7. Elicitation and comparison conditions

DR-22 defines several comparison classes.

### `COMMON_DENOMINATOR_DIRECT`

Uses the most comparable supported interface across model families:

- Same user task;
- Same evidence packet;
- Same answer-depth contract;
- No provider-exclusive tool or memory feature;
- Comparable output budget;
- Explicitly controlled reasoning mode.

This supports a conservative cross-family comparison.

### `FAMILY_NATIVE_BEST_PRACTICE`

Uses the official model's:

- Chat template;
- Recommended reasoning control;
- Native structured output where appropriate;
- Supported multimodal processor;
- Recommended serving backend.

This measures what each family can do when used as intended.

### `AUTHOR_NATIVE_PRIOR_ART`

Uses a prior-art author's documented:

- Model artifact;
- System prompt;
- Retrieval system;
- Decoding policy;
- Quantization;
- Application behavior.

This is the closest attempt to reproduce the original system.

### `NORMALIZED_PRIOR_ART_MODEL`

Places prior-art weights behind a common prompt or approved Biblical Scholar Lab runtime where technically compatible.

This isolates the model artifact from the original application. It must not be described as the author-native system.

### `BSL_A0_PRODUCT_RUNTIME`

Uses the complete unchanged-model Biblical Scholar Lab Runtime Scholar Harness.

### `BSL_ADAPTED_PRODUCT_RUNTIME`

Uses the same runtime with one identified adapted checkpoint or component enabled.

### `HUMAN_REFERENCE`

Uses the same evidence and task conditions under a separately defined human workflow.

Results from different conditions are displayed separately. They may be compared, but never merged into one unexplained score.

## 8. Framework decision

Biblical Scholar Lab will implement a framework-neutral `EvaluationCore` and a small deterministic `ReferenceEvaluationEngine`.

The provisional production evaluation engine will be:

```text
Inspect AI
```

using its low-level task, dataset, solver, scorer, model-provider, sandbox, eval-set, log, and control interfaces.

Inspect is selected provisionally because it supports:

- Custom tasks, solvers, scorers, and tools;
- Multi-turn and tool-using evaluations;
- A broad provider and local-runtime matrix;
- Stable sample identities;
- Evaluation sets and retries;
- Sample and campaign resource limits;
- Sandboxing;
- Structured output;
- Deferred and repeatable scoring;
- Detailed event and usage logs;
- Interactive log inspection;
- Extension points for models, components, sandboxes, approvers, hooks, filesystems, and agents.[^inspect-core]

This is an implementation-substrate decision—not a transfer of benchmark authority.

## 9. Inspect AI remains an adapter

The project will use Inspect through a bounded adapter.

### Canonical direction

```text
BSL benchmark case
    → BSL evaluation request
    → Inspect Task/Sample/Solver projection
    → Inspect execution and raw log
    → BSL attempt and scoring import
    → BSL Evaluation Result Bundle
```

### Rules

1. Project-owned Pydantic or equivalent domain models are canonical.
2. Inspect `Task`, `Sample`, `Target`, `Score`, `EvalLog`, and `Store` are execution projections.
3. Inspect logs remain important raw evidence but are not the sole scholarly audit artifact.
4. Public and private benchmark content remains in project-owned stores.
5. A framework upgrade cannot silently alter case semantics, prompts, budgets, scoring, or metrics.
6. Every Inspect revision, plugin, provider, and extension enters the campaign identity.
7. Inspect's viewer may display public-safe or authorized private logs only under the relevant access rules.
8. Project scoring may occur after generation through an explicit frozen scoring run.
9. Post-evaluation score edits remain append-only and provenance-bearing.
10. A complete result must remain reconstructable if Inspect is later replaced.

Inspect's log format already records task, dataset, model, generation config, packages, sample outputs, events, usage, scores, and score-edit histories. Biblical Scholar Lab will retain those records while adding its domain-specific benchmark, source, rights, graph, context, runtime, and campaign identities.[^inspect-logs]

## 10. Deterministic reference engine

Sol will implement a small:

```text
ReferenceEvaluationEngine
```

for:

- Unit and contract tests;
- Deterministic fixtures;
- Single-process execution;
- Framework-conformance checks;
- Scorer validation;
- Replaying frozen outputs;
- Verifying that the Inspect projection does not alter case semantics.

The reference engine is not intended to replace Inspect for large campaigns.

Before Inspect controls an authoritative evaluation, the same bounded test set must demonstrate equivalent:

- Case identity;
- Prompt and evidence projection;
- Subject invocation;
- Raw output capture;
- Tool and runtime trace capture;
- Scorer inputs and values;
- Error and timeout classification;
- Cost and usage import;
- Result-bundle hashes apart from engine-specific operational fields.

## 11. Other framework adapters

### `lm-evaluation-harness`

The project may implement an adapter for:

- Standard general-capability and retention tasks;
- Perplexity and multiple-choice baselines;
- External task reproduction;
- Quantized and local-model screening.

It does not become the primary Biblical Scholar Benchmark runtime because its core strength is standardized model evaluation rather than the full tools, runtime, evidence, rights, multimodal-page, and human-review architecture required here. Its current multimodal support is still described as developing, while its broad Hugging Face, vLLM, SGLang, API, PEFT, and quantized-model support makes it valuable for external controls.[^lm-eval]

### HELM

HELM remains an external comparison and reporting influence, especially for multidimensional and transparent evaluation. It entered maintenance mode in June 2026, so it will not be selected as the primary new execution dependency.[^helm]

### OpenAI Evals and provider-native evaluation APIs

OpenAI Evals or provider-native evaluation services may be used for:

- Provider-specific model experiments;
- Frontier-ceiling checks;
- Private provider-local comparisons where rights permit;
- Cross-validation of selected public tasks.

They remain optional adapters. Provider-managed datasets, graders, dashboards, or traces cannot become the canonical private benchmark store or scoring authority.[^openai-evals]

### Inspect Evals publication

A later public-safe BSL evaluation package may be registered with Inspect Evals after:

- The public benchmark name is selected;
- The public subset is stable;
- Rights are cleared;
- The API is versioned;
- The collaboration preview has passed;
- Owner release approval is given.

Private, fresh, and restricted content remains outside any public registry.

## 12. Model-provider and inference-backend identity

Every subject invocation records:

```text
model repository and immutable revision
weight and configuration hashes
tokenizer and processor revisions
chat template and special tokens
reasoning mode
structured-output mode
inference engine and version
kernel and attention path
precision or quantization
hardware and topology
server arguments
provider endpoint class
caching and batching state
```

Inspect supports local Hugging Face, vLLM, Ollama, llama.cpp, SGLang, and several hosted providers, as well as OpenAI-compatible endpoints. That provider breadth is useful only when exact execution identity remains visible.[^inspect-providers]

## 13. Reference and optimized inference paths

An optimized serving engine may alter:

- Chat-template application;
- Stop conditions;
- Sampling;
- Log probabilities;
- Multimodal preprocessing;
- Structured-output enforcement;
- Tool schemas;
- Quantization;
- Numerical results.

Each family therefore receives:

```text
REFERENCE_INFERENCE_PATH
OPTIMIZED_INFERENCE_PATH
```

The reference path is the most direct officially supported implementation suitable for correctness validation.

The optimized path may use vLLM, SGLang, llama.cpp, MLX, or another approved engine.

Before an optimized path controls a primary result, a bounded equivalence suite must compare:

- Prompt and template bytes;
- Tokenized input;
- Special tokens;
- Image/audio preprocessing;
- Greedy or fixed-seed outputs where applicable;
- Log probabilities where available;
- Tool-call schemas;
- Structured-output behavior;
- Long-context behavior;
- Ancient-script fidelity;
- Cost and throughput.

Non-equivalent paths remain separate subjects. Speed is not permission to replace the reference path silently.

## 14. Structured output is an elicitation variable

Structured output can improve schema conformance while changing model behavior.

The project will compare, where relevant:

```text
UNCONSTRAINED_TEXT
PROMPTED_JSON
NATIVE_STRUCTURED_OUTPUT
GRAMMAR_OR_GUIDED_DECODING
```

Inspect supports structured output across several providers and local engines, while warning that constrained generation can affect task performance. DR-22 therefore treats it as an experimental condition rather than an automatic fairness improvement.[^inspect-structured]

A model is not credited with semantic correctness merely because its JSON validates.

## 15. Generation and scoring are separately frozen

Authoritative evaluation uses two logical phases.

### Generation phase

Produces immutable:

- Subject outputs;
- Tool/runtime traces;
- Evidence and context identities;
- Errors, retries, and usage;
- Raw artifacts.

### Scoring phase

Applies one exact:

- Benchmark and rubric revision;
- Scorer implementation;
- Judge configuration;
- Human-review batch;
- Statistical reducer.

The same outputs may be rescored under a corrected scorer without being regenerated.

A scoring revision does not overwrite an earlier score. It creates a new `ScoringRunSpecification` and preserves the complete history.

Inspect supports deferring scoring and applying or editing scores later; Biblical Scholar Lab will use that capability behind its own append-only scoring and incident contracts.[^inspect-scoring]

## 16. Stable sample identities

Every executable sample ID is derived from:

```text
benchmark revision
case family
case revision
variant revision
evaluation mode
subject
elicitation condition
attempt or epoch
```

Stable IDs are mandatory for:

- Resume and retry;
- Detecting duplicate execution;
- Pairing subjects;
- Cluster-aware statistics;
- Merging distributed logs;
- Reproducing a failed sample;
- Preserving private/fresh access boundaries.

Inspect can reuse completed samples during retries when stable IDs are available. The project will supply explicit IDs and will not rely on auto-incrementing identities for authoritative campaigns.[^inspect-evalsets]

## 17. Determinism, stochasticity, and repeated trials

The project will never describe an LLM evaluation as deterministic merely because temperature is zero.

Every condition records:

- Temperature, top-p, top-k, and other sampling values;
- Seed and whether the backend honors it;
- Reasoning mode;
- Concurrent batching;
- Provider and server revision;
- Cache state;
- Number of epochs or repeated attempts.

### Deterministic-intent conditions

Use greedy or the most deterministic supported configuration and repeat a calibration subset to measure residual variation.

### Stochastic conditions

Use preregistered repeats and aggregate at the case-family level.

### Tool and retrieval nondeterminism

Record search index, reranker, provider, currentness horizon, network state, and result ordering.

One lucky sample cannot control promotion.

## 18. Budgets and fairness

Every evaluation request declares:

```text
input context budget
output token budget
reasoning budget
tool-call budget
retrieval budget
message limit
time limit
working-time limit
cost limit
image and modality budget
```

Inspect supports per-sample message, token, time, working-time, and cost limits. Biblical Scholar Lab will surface all of them in the result rather than treating them as hidden execution settings.[^inspect-limits]

Comparisons will distinguish:

### Budget-matched

Subjects receive comparable evidence, time, tokens, and tool opportunities.

### Cost-matched

Subjects operate under an equal approved monetary budget.

### Best-practice

Each subject receives an approved native configuration intended to show its strongest practical result.

### Product-default

The actual product route is evaluated at its intended latency and cost.

No one condition replaces the others.

## 19. Error and failure semantics

The result vocabulary includes:

```text
SUCCESS
MODEL_REFUSAL
MALFORMED_OUTPUT
TOOL_FAILURE
RETRIEVAL_FAILURE
RIGHTS_BLOCK
CAPABILITY_BLOCK
TIMEOUT
COST_LIMIT
CONTEXT_OVERFLOW
OUT_OF_MEMORY
PROVIDER_ERROR
SANDBOX_ERROR
FRAMEWORK_ERROR
CANCELLED
UNKNOWN_FAILURE
```

These are outcomes, not missing rows.

A campaign report must show:

- Every requested sample;
- Every completed attempt;
- Every failed attempt;
- Every retry;
- Every fallback;
- The final disposition;
- Whether the sample entered each metric denominator.

## 20. Retry policy

Retries can introduce distribution shift by giving certain failing samples additional opportunities. Inspect's documentation explicitly warns that sample retries can alter the evaluated distribution when errors correlate with input type.[^inspect-errors]

The default authoritative policy is:

### Provider connection retries

Bounded retries are permitted for clearly transient transport or rate-limit failures. The provider's own hidden retries must be measured or disabled where practical.

### Sample reruns

A sample may be rerun only when:

- The failure is classified as infrastructure-related;
- The subject, prompt, evidence, seed policy, and budgets remain unchanged;
- The original attempt remains in the record;
- The rerun is labeled as a new attempt;
- Retry counts and outcome differences are reported.

### No semantic reroll

The project may not retry because:

- The answer was wrong;
- The model refused;
- The output was inconvenient;
- A citation failed;
- The model used too much uncertainty;
- A judge disliked the prose.

### Ambiguous completion

If a connection drops after generation may have occurred, the attempt remains ambiguous rather than being silently replaced.

### Run-level resume

Completed sample results may be reused after an interrupted run when stable IDs and exact campaign identity match.

## 21. Scoring errors do not erase generation results

If a scorer fails:

- The raw subject output remains valid execution evidence;
- The score is marked `SCORER_ERROR` or unscored;
- Other scorers may continue where authorized;
- A corrected scorer produces a new scoring run;
- The failure is included in the benchmark incident record when material.

An unscored sample is not automatically incorrect or correct.

## 22. Scoring and judge isolation

Project scorers receive only the information authorized by the case contract.

A judge may be blinded to:

- Subject name;
- Model family;
- Quantization;
- Response order;
- Author or developer identity;
- Whether the answer is human or model-generated;
- Other candidates' scores.

Where a judge requires evidence, it receives the approved evidence packet—not hidden gold or private notes beyond the rubric contract.

Judge prompts and outputs become immutable artifacts.

The generating model cannot be its own sole authoritative judge.

Inspect supports multiple scorers and model-graded scorers; DR-21's calibration and human-governance requirements remain controlling.[^inspect-model-grading]

## 23. Human review and human reference baselines

Human evaluation is separated into:

```text
HUMAN_SCORER
HUMAN_ADJUDICATOR
HUMAN_REFERENCE_SUBJECT
HUMAN_WORKFLOW_USER_STUDY
```

A human reference subject receives:

- The same defined evidence mode;
- A recorded time and tool budget;
- The same answer contract;
- An interface appropriate to the task;
- Qualification metadata;
- A recorded completion time and confidence.

The project will not use one undifferentiated `human score`.

Inspect includes a human-agent facility for Linux-environment agent tasks, but Biblical Scholar Lab's scholarly human baselines will normally use the DR-21 annotation and study workbench because their task is evidence interpretation rather than terminal operation.[^inspect-human]

## 24. Prior-art reproduction tiers

Every prior-art result receives one of these statuses.

```text
PA-R0_AUTHOR_REPORTED_ONLY
PA-R1_ARTIFACT_INFERENCE_REPRODUCED
PA-R2_AUTHOR_NATIVE_SYSTEM_REPRODUCED
PA-R3_NORMALIZED_MODEL_COMPARISON
PA-R4_COMPONENT_ABLATION_REPRODUCED
PA-R5_INDEPENDENT_RETRAINING_REPLICATION
PA-BLOCKED_MISSING_ARTIFACTS
PA-BLOCKED_RIGHTS_OR_ACCESS
PA-PARTIAL_WITH_MATERIAL_DEVIATIONS
```

### `PA-R0`

Only the author's published result is available. It is cited, not rerun.

### `PA-R1`

The released model weights are run under their documented prompt and inference policy.

### `PA-R2`

The complete documented application, retrieval, prompt, and model stack is reproduced at a frozen commit.

### `PA-R3`

The released model artifact is evaluated under a common Biblical Scholar Lab condition.

### `PA-R4`

Intermediate checkpoints, adapters, or ablations are available and reproduced.

### `PA-R5`

The training pipeline is independently rerun from source data and code.

A result is never described as `reproduced` at a higher tier than the evidence supports.

## 25. Rhema BibleAI baseline

Rhema BibleAI is a mandatory prior-art baseline because its public release closely matches the high-level CPT → SFT → DPO trajectory considered for this project.

The official materials describe:

- A Gemma 4 E4B-derived multimodal model;
- Continued pretraining on Christian texts;
- 15,289 SFT examples and 1,601 evaluation examples;
- A sub-1,000-pair DPO stage;
- A published system prompt emphasizing Bible-domain scope, concise answers, and nonfabrication;
- BF16 and quantized releases;
- A 128K context claim;
- Known limitations including Reformed leaning, over-hedging, and weaker long multi-step reasoning than larger frontier models.[^rhema]

### Required conditions

```text
RHEMA_AUTHOR_NATIVE_BF16
RHEMA_AUTHOR_NATIVE_QUANTIZED
RHEMA_MODEL_NORMALIZED
RHEMA_MODEL_PLUS_BSL_A0 where technically compatible
```

### Reproduction caveats

- The public training datasets are not presently available from the official organization page.
- The exact CPT and SFT parent lineage must be verified from artifacts and logs.
- The author-native prompt remains separate from our scope policy.
- A normalized BSL runtime result is not labeled as Rhema's application.
- Rhema's own BibleBench remains an external benchmark adapter, not an independent private final set.

### Desired ablation

If intermediate SFT and DPO artifacts are sufficiently available, compare:

```text
SFT parent
versus
SFT + DPO
```

Otherwise the causal claim remains author-reported rather than independently reproduced.

## 26. Timms Bible AI Assistant baseline

The public `t-timms/bible-ai-assistant` repository is a second mandatory prior-art system because it provides an end-to-end Qwen3.5-4B system with:

- LoRA SFT;
- ORPO preference training;
- Hybrid dense/BM25 retrieval;
- Reciprocal-rank fusion and cross-encoder reranking;
- Quantized and full-precision artifacts;
- A public evaluation protocol and 54-question suite;
- Application, training, testing, and deployment code.[^timms]

### Required conditions

```text
TIMMS_AUTHOR_NATIVE_FULL_PRECISION where artifact exists
TIMMS_AUTHOR_NATIVE_QUANTIZED
TIMMS_MODEL_NORMALIZED
TIMMS_MODEL_PLUS_BSL_A0 where technically compatible
```

### Required reporting

- Exact repository commit;
- Exact model artifact and hash;
- Retrieval corpus and index revision;
- Environment and dependency lock;
- System prompt and generation settings;
- Whether all documented application services were active;
- Deviations from the published setup;
- Our independent benchmark results separately from the author's reported metrics.

The project's own 54-question benchmark remains an external baseline, not authoritative gold for Biblical Scholar Lab.

## 27. Other prior-art products

Closed products such as commercial Bible-study or scholarly platforms may inform product feature analysis but cannot receive quantitative reproduction status unless:

- The exact system can be evaluated under a stable authorized interface;
- The evidence and tool conditions are known;
- Terms permit the evaluation;
- The result is described as black-box product behavior rather than model capability.

Marketing demonstrations do not become benchmark results.

## 28. Foundation-model and capacity baselines

The initial mandatory compact product baselines remain those approved in DR-11:

```text
Qwen3.5-9B
Gemma 4 12B instruction-tuned
Ministral 3 8B Instruct and/or Reasoning after screening
```

The initial high-capacity comparators remain:

```text
Qwen3.8-27B
Gemma 4 31B instruction-tuned
```

Base checkpoints receive representation and post-training comparisons as appropriate.

The exact official repositories and revisions are audited immediately before the campaign because model catalogs may change.

## 29. Frontier ceiling

A current high-capability frontier model will be evaluated as a ceiling under the same fixed-evidence and full-runtime conditions where rights permit.

The exact provider and revision are selected in a dated experiment design immediately before execution.

Because ChatGPT authors the benchmark cases, an OpenAI frontier result on ChatGPT-authored cases cannot be represented as an uncontaminated independent final examination. A strong claim about that subject requires a separate human- or SME-authored fresh subset under DR-21.

The frontier model is a capability ceiling and design diagnostic—not the project's default deployment model.

## 30. External benchmark adapters

The following remain separate scorecards.

### Rhema BibleBench

Used for external biblical-literacy and prior-art comparison under its own version and scoring policy.

### BIBLE

Used only as a broad literacy or failure-discovery screen until item-level validation supports stronger use. Its dataset card notes substantial model-generated content and incomplete manual review.

### FMG-Bench

Used for theological triage, preference configuration, escalation, and pastoral-adjacent safety comparison under its own stated limitations.

### Biblical Hebrew intertextuality benchmark

Used as a specialist external control for known parallel detection.

### MTEB BibleNLP bitext retrieval

Used as a multilingual primary-text retrieval control.

### General and multimodal retention

Selected tasks from lm-eval, HELM/VHELM, or other approved suites may measure parent-relative general, multilingual, vision, reasoning, tool, and safety retention.

External scores are not merged into the BSL benchmark composite.

## 31. Benchmark-content privacy and least privilege

Private and fresh cases must remain inaccessible to:

- Sol's ordinary development environment;
- Public CI;
- Public artifact generation;
- Training or synthetic-data agents;
- Unauthorized model providers;
- Prior-art applications not approved to receive them;
- Model judges before their scoring role is authorized.

Sol implements secure loaders and access controls without seeing benchmark content where the design permits.

A private campaign may expose only the minimum required projection to:

- The subject;
- The scorer;
- The human reviewer;
- The statistical reducer.

Each exposure is recorded.

## 32. Provider and rights routing

Before transmitting a case or evidence packet, the campaign verifies:

- Benchmark split and privacy state;
- Source and rights lanes;
- User-private content;
- Provider retention and training policy;
- Geographic or contractual restrictions;
- Whether model and judge providers may receive the content;
- Whether raw requests and responses may be logged.

A private benchmark case that cannot be sent to a frontier API remains local or is omitted from that comparison with explicit missing coverage.

Rights filtering occurs before transmission, not after.

## 33. Sandboxing and network isolation

Prior-art applications, agentic subjects, and untrusted tools run in approved sandboxes.

The initial default is a reproducible local container or Docker Compose sandbox with:

- Read-only benchmark input;
- Ephemeral writable storage;
- No host credentials;
- Restricted or disabled network;
- Resource limits;
- Pinned image digest;
- Explicit artifact export;
- Cleanup verification.

Stronger isolation may use Kubernetes or VM-backed sandboxes when the threat model or scale requires it.

Inspect supports pluggable sandbox environments and approval policies, and AISI publishes separate sandboxing tooling and protocols for agentic evaluations.[^inspect-sandbox]

A prior-art system may not download new data or phone home during an authoritative run unless that behavior is explicitly part of the approved condition and recorded.

## 34. Long-running evaluation control

Authoritative campaigns must remain observable and cancellable after the launching Sol or Luna session ends.

The execution adapter should use the framework's detached-run and control facilities, or an equivalent project-owned controller, to:

- Confirm launch through a machine-readable record;
- Poll active tasks and samples;
- Inspect errors and stalled work;
- Pause, resume, or cancel under the campaign policy;
- Confirm final completion and log locations;
- Verify cleanup and resource termination.

Inspect's control channel provides live task and sample inspection and pause/resume/cancel operations; those capabilities remain subordinate to DR-25's campaign and cost authority.[^inspect-control]

## 35. Logs and privacy

Inspect logs may contain:

- Private prompts;
- Evidence text;
- Images;
- Model requests and responses;
- Tool results;
- Scorer explanations;
- Human edits.

Therefore:

- Private logs remain in restricted storage.
- Raw model API logging is disabled unless needed and authorized.
- Images are embedded or retained only when the rights and privacy policy permits.
- Public result bundles use redacted, public-safe projections.
- Secret-bearing URLs or credentials never enter logs.
- Human-review notes receive the appropriate privacy state.
- Framework viewers are not exposed publicly over private log directories.

## 36. Runtime and system traces

For the full Runtime Scholar Harness, the evaluation result must import or reference:

- `RuntimeAuditReceipt`;
- Context packet and usage receipt;
- Tool capability grants;
- Retrieval and evidence identities;
- Translation Nuance and Page Evidence packets;
- Verification and repair results;
- Compaction and rehydration events;
- Model fallbacks;
- Cost and latency.

A final answer alone is insufficient for diagnosing the system.

## 37. Public-safe projections

Every result bundle may generate a projection containing only:

- Public case identity;
- Public prompt and evidence where authorized;
- Subject identity and configuration;
- Public output;
- Public scores;
- Aggregate metrics;
- Public-safe error analysis;
- Cost and performance;
- Known limitations.

Private case wording, gold, evidence, reviewer notes, and traces remain absent.

A public aggregate must not permit reconstruction of private benchmark answers through per-case leakage.

## 38. Evaluation campaign classes

The initial campaign classes are:

```text
DEV_SMOKE
PUBLIC_REPRODUCTION
MODEL_FAMILY_SCREEN
PRIOR_ART_REPRODUCTION
RUNTIME_COMPONENT_ABLATION
PRIVATE_MODEL_SELECTION
TRAINING_STAGE_PROMOTION
FINAL_FROZEN_EVALUATION
FRESH_CHALLENGE
HUMAN_REFERENCE
INCIDENT_REGRESSION
```

Each class has its own:

- Permitted splits;
- Subject types;
- Providers;
- Cost limits;
- Retry policy;
- Scorer authority;
- Publication state.

A development smoke run cannot be promoted into a final result by relabeling its output.

## 39. Sol and Luna operating boundary

### Sol

Sol may:

- Implement the project-owned evaluation core;
- Implement the reference and Inspect engine adapters;
- Build subject and provider adapters;
- Build sandboxes;
- Implement approved scorers and statistical reports;
- Implement prior-art reproduction environments;
- Create public-safe projections;
- Diagnose implementation failures;
- Propose design-neutral optimizations.

Sol may not:

- Author benchmark cases;
- Alter benchmark semantics;
- Change evidence or answer contracts;
- Select model winners;
- Change campaign hypotheses, subjects, budgets, retries, prompts, scorer authority, or promotion rules without an approved design;
- Hide reproduction deviations;
- Interpret ambiguous scientific results as a design decision.

### Luna

Luna may:

- Validate the frozen campaign envelope;
- Launch approved subjects and sandboxes;
- Monitor progress, errors, usage, and cost;
- Resume exact authorized work;
- Collect logs and artifacts;
- Stop on approved limits;
- Confirm cleanup and shutdown.

Luna may not:

- Modify code, cases, prompts, evidence, scores, judges, thresholds, model configs, or retry rules;
- Replace a failed subject;
- Increase budget;
- Interpret results;
- Decide promotion.

## 40. Campaign completion handoff

Sol's consolidated evaluation handoff must include:

```text
approved experiment and benchmark design IDs
campaign specification and hash
subjects and elicitation conditions
execution engine and exact revisions
case and split counts
completion, error, retry, refusal, and timeout counts
raw and scored artifact locations and hashes
scorer and judge revisions
cost, usage, latency, and hardware
prior-art reproduction tier and deviations
primary and worst-group results
hard failures and error taxonomy
statistical report
public/private visibility state
known limitations
implementation conformance statement
```

Sol may report measurements and implementation observations. It may not determine the scientific promotion decision.

## 41. Principal hard failures

DR-22 treats the following as hard failures:

- Executing unapproved or modified benchmark content;
- Letting Inspect, another framework, or a provider-managed eval redefine benchmark semantics;
- Mixing model-only and full-system results under one label;
- Evaluating a Base checkpoint as though it were a post-trained assistant without disclosure;
- Using different evidence or hidden budgets in a supposedly controlled comparison;
- Omitting model, tokenizer, template, processor, runtime, quantization, or kernel identity;
- Silently changing inference backends without equivalence validation;
- Treating schema-valid structured output as substantively correct;
- Retrying wrong or refused answers until one passes;
- Dropping errors, refusals, timeouts, or malformed outputs from the denominator;
- Overwriting earlier outputs or scores;
- Claiming a prior-art reproduction above the achieved tier;
- Using author-reported results as independently reproduced results;
- Sending private or restricted cases to an unauthorized provider;
- Exposing private gold or evidence to a judge or subject without authorization;
- Allowing a prior-art application network or host access outside its sandbox contract;
- Publishing private traces or reconstructable per-case private results;
- Treating an LLM judge as authoritative without DR-21 calibration;
- Allowing Sol to alter cases or experiment design;
- Allowing Luna to modify or interpret a campaign;
- Presenting a ChatGPT-authored benchmark as an uncontaminated independent final OpenAI-model examination;
- Hiding actual cost, retries, fallbacks, or failed samples;
- Promoting a system based only on aggregate accuracy while hard failures or worst-group regressions remain material.

## 42. Decisions DR-22 would lock

Approval would establish that:

1. The project owns a framework-neutral Evaluation Core.
2. A deterministic Reference Evaluation Engine is the conformance oracle.
3. Inspect AI is the provisional production evaluation engine.
4. Inspect tasks, samples, logs, stores, and scores remain adapters around project records.
5. The benchmark content remains outside framework authority.
6. Generation and scoring remain separately frozen and versioned.
7. Stable project-owned sample identities are mandatory.
8. Model and system subjects remain separate.
9. Common-denominator, family-native, author-native, normalized prior-art, and full-product conditions remain separate.
10. Base checkpoints receive appropriate representation and post-training evaluations rather than being judged as finished assistants.
11. Every model bundle, prompt, provider, backend, processor, reasoning mode, precision, quantization, kernel, and budget remains explicit.
12. Optimized inference paths require equivalence testing against a reference path.
13. Structured output is an elicitation condition, not proof of correctness.
14. Errors, refusals, timeouts, limits, and malformed outputs remain visible outcomes.
15. Retries are limited to classified infrastructure failures and never used as semantic rerolls.
16. Scorer failures preserve raw outputs and create new scoring runs rather than overwritten results.
17. Model judges remain secondary and case-contract-limited.
18. Human scoring, adjudication, reference performance, and workflow studies remain separate roles.
19. Prior-art results use explicit `PA-R0` through `PA-R5` reproduction tiers.
20. Rhema BibleAI and the Timms Bible AI Assistant are mandatory initial prior-art baselines.
21. Qwen, Gemma, Ministral, Qwen3.8-27B, and Gemma 4 31B remain the initial model-family and capacity baselines under DR-11.
22. The frontier ceiling remains dated and separately caveated for author-model contamination.
23. External benchmarks remain separate adapters and scorecards.
24. Private and fresh content remains least-privilege and provider-gated.
25. Prior-art and agentic applications run in restricted sandboxes.
26. Long-running campaigns remain observable, cancellable, resumable, and cleanup-verifiable.
27. Inspect logs remain important raw evidence but project result bundles remain canonical.
28. Runtime audit, context, tool, retrieval, compaction, fallback, and verification traces enter full-system results.
29. Public-safe projections cannot reveal private benchmark content.
30. Campaign classes control split, provider, retry, scorer, cost, and release permissions.
31. Sol implements the approved machinery and consolidated handoff.
32. Luna only executes frozen campaigns delegated by Sol.
33. ChatGPT retains evaluation and experiment design, result review, and next-step design authority.
34. Joseph Abbud retains sole authority over campaign approval, model and system promotion, public claims, and release.

## 43. Decisions intentionally deferred

DR-22 does not yet select:

- Exact Inspect AI version;
- Exact package and plugin layout;
- Exact initial model revisions at campaign time;
- Exact frontier ceiling provider;
- Exact inference engine for every candidate family;
- Exact Docker or Kubernetes implementation;
- Exact numeric sample budgets and cost limits;
- Exact public/private case counts beyond DR-21 envelopes;
- Exact judge model and prompt;
- Exact human reviewer interface and compensation;
- Exact public result website or dashboard;
- Exact baseline campaign schedule;
- Exact statistical promotion thresholds;
- Exact Lambda hardware assignment.

Those belong to Sol's implementation under this contract, DR-23, DR-24, DR-25, DR-28, and approved campaign designs.

## 44. Proposed approval statement

> **Biblical Scholar Lab will use a framework-neutral, project-owned Evaluation Core that converts approved benchmark cases, subject artifacts, elicitation conditions, evidence modes, budgets, scorer plans, and campaign policies into immutable evaluation requests, attempt records, scoring runs, result bundles, and comparison reports. A small deterministic Reference Evaluation Engine will serve as the semantic conformance oracle, while Inspect AI will be the provisional production engine for task scheduling, model and system invocation, tool and multi-turn execution, sandboxing, persistence, retries, limits, logging, deferred scoring, and inspection. Inspect tasks, samples, stores, logs, and scores will remain replaceable operational projections of project-owned benchmark and result records and may not redefine benchmark content, scholarly authority, rights, or promotion criteria. Model-only, Base, post-trained, retriever, tool, Runtime Scholar Harness, end-to-end product, prior-art, quantized, mobile, frontier, and human-reference subjects will remain distinct; common-denominator, family-native, author-native, normalized prior-art, full-A0-runtime, and adapted-product conditions will remain separately reported. Generation and scoring will be independently frozen and versioned; stable project-owned sample identities will support exact resume and paired comparison; every model, tokenizer, processor, template, reasoning mode, structured-output policy, inference backend, kernel, precision, quantization, prompt, context, tool, retrieval, runtime, seed, retry, fallback, cost, and hardware state will remain explicit. Wrong answers, refusals, malformed outputs, timeouts, rights blocks, capability blocks, provider errors, and scorer failures will remain visible outcomes rather than disappearing from denominators, and retries will be limited to classified infrastructure failures with original attempts retained. Optimized inference backends will require parent-relative equivalence tests, LLM judges will remain secondary and calibrated under DR-21, and human scoring, adjudication, reference performance, and workflow studies will retain separate roles. Prior art will be reported through explicit reproduction tiers from author-reported results to full independent retraining; Rhema BibleAI and the public Timms Bible AI Assistant will be mandatory first baselines under both author-native and normalized conditions where artifacts permit, while Qwen, Gemma, Ministral, high-capacity comparators, frontier ceilings, and external Bible, multilingual, multimodal, safety, and general-retention benchmarks remain separate scorecards. Private, fresh, user-private, restricted, and rights-sensitive content will be protected before provider transmission, prior-art and agentic subjects will execute in restricted sandboxes, long-running campaigns will remain observable and cancellable, and public projections will not reveal private gold or evidence. Sol will implement the approved evaluation and reproduction machinery and produce one consolidated evidence handoff; Luna may only launch and monitor frozen campaigns delegated by Sol; ChatGPT will design evaluations, review code and results, and determine recommended scientific next steps; and Joseph Abbud will retain sole authority over campaign approval, model or system promotion, public claims, and release.**

---

## References

[^inspect-core]: UK AI Security Institute, “Inspect AI,” official repository and documentation. Inspect provides extensible tasks, solvers, scorers, tools, model providers, multi-turn and tool-use evaluation, logs, and more than 200 registered evaluations: <https://github.com/UKGovernmentBEIS/inspect_ai> and <https://inspect.aisi.org.uk/>.

[^inspect-logs]: Inspect, “Log Files” and `inspect_ai.log` API. Eval logs preserve task and model configuration, packages, sample outputs, events, usage, scores, and append-only score and metadata edit histories: <https://inspect.aisi.org.uk/eval-logs.html> and <https://inspect.aisi.org.uk/reference/inspect_ai.log.html>.

[^lm-eval]: EleutherAI, `lm-evaluation-harness`. The framework provides standard academic tasks and adapters for Hugging Face, vLLM, SGLang, APIs, PEFT, and quantized models, while describing multimodal support as developing: <https://github.com/EleutherAI/lm-evaluation-harness>.

[^helm]: Stanford CRFM, `helm`. HELM is a holistic, reproducible evaluation framework and set of leaderboards; its repository states that the framework entered maintenance mode on June 1, 2026: <https://github.com/stanford-crfm/helm>.

[^openai-evals]: OpenAI, `evals`. OpenAI Evals supports custom and private evaluations of LLMs and LLM systems and provider-specific execution, but remains an optional adapter rather than the project-owned benchmark store: <https://github.com/openai/evals>.

[^inspect-providers]: Inspect, “Model Providers.” Inspect supports OpenAI, Anthropic, Google, Mistral, other hosted APIs, Hugging Face, vLLM, Ollama, llama.cpp, SGLang, and OpenAI-compatible endpoints: <https://inspect.aisi.org.uk/providers.html>.

[^inspect-structured]: Inspect, “Structured Output.” Inspect supports schema-constrained output across several providers and notes that structured output can change task performance and therefore should itself be evaluated: <https://inspect.aisi.org.uk/structured.html>.

[^inspect-scoring]: Inspect, “Scoring Workflow” and “Log Files.” Inspect supports unscored generation, later scoring, score editing, history, and aggregate recomputation: <https://inspect.aisi.org.uk/scoring-workflow.html> and <https://inspect.aisi.org.uk/eval-logs.html>.

[^inspect-evalsets]: Inspect, “Eval Sets.” Stable explicit sample IDs allow completed samples to be matched and preserved during retry and resume: <https://inspect.aisi.org.uk/eval-sets.html>.

[^inspect-limits]: Inspect, “Options” and “Tasks.” Per-sample controls include message, token, time, working-time, and cost limits: <https://inspect.aisi.org.uk/options.html> and <https://inspect.aisi.org.uk/tasks.html>.

[^inspect-errors]: Inspect, “Handling Errors.” Inspect distinguishes runtime errors and crash recovery and warns that sample retries may create distribution shift when errors correlate with input type: <https://inspect.aisi.org.uk/errors-and-limits.html>.

[^inspect-model-grading]: Inspect, “Model Grading” and “Multiple Scorers.” Inspect supports custom grader prompts, several grader models, repeated grading, and several scorers per sample: <https://inspect.aisi.org.uk/model-graded.html> and <https://inspect.aisi.org.uk/multiple-scorers.html>.

[^inspect-human]: Inspect, “Human Agent.” Inspect can run human baselines under the same task, sandbox, and scorer configuration for terminal-based agent tasks: <https://inspect.aisi.org.uk/human-agent.html>.

[^rhema]: Rhema, “Meet BibleAI,” and official `rhemabible/BibleAI` model card. The released model uses a Gemma 4 E4B foundation and a CPT → SFT → DPO pipeline, with 15,289 SFT examples and fewer than 1,000 preference pairs; Rhema describes it as a proof of concept and discloses limitations: <https://rhemabible.co/blog/introducing-bibleai> and <https://huggingface.co/rhemabible/BibleAI>.

[^timms]: Tremayne Timms, `bible-ai-assistant`. The public repository describes a Qwen3.5-4B LoRA SFT and ORPO system with hybrid retrieval, quantized deployment, a public 54-question evaluation suite, and a pinned dependency lock: <https://github.com/t-timms/bible-ai-assistant>.

[^inspect-sandbox]: UK AI Security Institute, `aisi-sandboxing` and Inspect sandbox documentation. AISI provides Docker Compose, Kubernetes, and VM-oriented sandboxing tools and a protocol spanning tool, host, and network isolation: <https://github.com/UKGovernmentBEIS/aisi-sandboxing> and <https://inspect.aisi.org.uk/sandboxing.html>.

[^inspect-control]: Inspect, “Control Channel.” Inspect supports detached evaluation processes, machine-readable launch and completion records, live task and sample inspection, and pause, resume, and cancellation: <https://inspect.aisi.org.uk/control-channel.html>.
