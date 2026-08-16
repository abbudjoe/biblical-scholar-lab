# DR-18 — Training Curriculum and Objectives

| Field | Value |
|---|---|
| Design ID | `DR-18` |
| Status | `APPROVED` |
| Approval date | 2026-08-16 |
| Project owner | Joseph Abbud |
| Designer and independent reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2 and supplements; DR-03; DR-04; DR-05; DR-06; DR-07; DR-08; DR-09; DR-10; DR-11; DR-12; DR-13; DR-14; DR-15; DR-16; DR-17 |
| Implementation authority | GPT-5.6 Sol, under the approved design |
| Execution authority | GPT-5.6 Luna only for frozen campaigns delegated by Sol under a later approved campaign envelope |
| Experiment-design authority | ChatGPT designs; Joseph Abbud approves; Sol implements only the approved design |
| Approved change | Establishes the authoritative model-adaptation lineages, stage order, objective taxonomy, replay and capability-preservation requirements, checkpoint and evaluation policy, baseline and ablation matrix, stage-promotion gates, synthetic-data and teacher-use rules, and separation among continued pretraining, Translation Nuance mid-training, scholarly SFT, retrieval-aware SFT, preference optimization, distillation, and later architecture-extension experiments |

## 1. Purpose

The approved designs now specify:

- The product and scholarly contract;
- Canon, textual history, linguistic representation, ancient versions, and scholarship;
- The Translation Nuance Core and its A0–A6 integration ladder;
- Rights, multilingual, multimodal, long-context, runtime, and corpus architecture;
- The candidate foundation-model families and model-role bake-off;
- The vertical-slice-first data strategy and hierarchical sampling system.

Those designs do not yet determine how model weights should be changed, in what order, for which purpose, under which objective, with which replay and preservation data, or what evidence is required before a training stage may advance.

A poorly designed curriculum could:

- Teach verse completion without scholarly method;
- Improve domain perplexity while damaging instruction following;
- Improve English while degrading Greek, Hebrew, or other languages;
- Improve text behavior while damaging page understanding;
- Teach modern translation repetition as though it were independent evidence;
- Memorize exact passages or restricted scholarship;
- Overfit a small SFT or preference set;
- Conflate knowledge acquisition, tool use, evidence handling, and conversational style;
- Make it impossible to determine which stage produced a gain or regression;
- Spend most of the Lambda budget before demonstrating value beyond tools and retrieval.

DR-18 defines the stage-specific training contract needed to prevent those outcomes.

It does not authorize a billable run, choose final numerical hyperparameters, set final data-mixture percentages, select the winning model family, or guarantee that every proposed stage will occur. Each consequential run still requires an approved experiment design, immutable campaign envelope, ChatGPT review, and owner authorization.

## 2. Governing principle

> **Every training stage must have one explicit capability hypothesis, one immutable parent, one approved data and objective contract, one preservation plan, and one preregistered promotion rule. Biblical Scholar Lab will not modify weights merely because data are available or compute remains. Tools and retrieval will remain the preferred home for exact, current, rights-sensitive, and inspectable knowledge; model training will be used only for capabilities that demonstrably benefit from learned representation or behavior.**

The intended adaptation flow is:

```text
unmodified model and complete A0 runtime baseline
    → bounded strategy and stability screen
    → ancient/context continued pretraining, if justified
    → structured Translation Nuance mid-training, if justified
    → scholarly supervised fine-tuning
    → retrieval- and tool-aware supervised fine-tuning
    → multilingual, multimodal, long-context, and safety preservation confirmation
    → preference optimization ablation
    → optional distillation, quantization, merging, specialists, or A2–A5 extensions
    → private and fresh final evaluation
```

No arrow in this flow is automatic.

## 3. Training is an experiment—not a deployment ritual

Every stage is treated as a falsifiable intervention.

A stage must answer:

```text
What measured deficit exists?
Why should this objective repair it?
What data contain the needed learning signal?
Which model components may change?
Which capabilities are at risk?
Which baseline isolates the stage's contribution?
What result means GO, REPAIR, NO-GO, or STOP?
```

The system may succeed at A0—with tools, structured evidence, retrieval, and the Runtime Scholar Harness—without requiring substantial foundation-model adaptation.

If a training stage does not beat its matched no-stage baseline on the named capability, it is rejected or redesigned. It is not retained because it consumed time or money.

## 4. Knowledge, representation, behavior, and evidence remain distinct

DR-18 separates four intended effects.

### 4.1 Domain representation

Learned through continued pretraining and structured mid-training:

- Ancient-language distributions;
- Domain terminology;
- Textual and literary patterns;
- Translation correspondences;
- Recurring relation structures;
- Efficient internal representations useful across tasks.

### 4.2 Scholarly task behavior

Learned primarily through supervised and preference training:

- How to use the approved tools;
- How to consume evidence packets;
- How to distinguish claim types;
- How to cite, qualify, compare, and abstain;
- How to render Brief, Study, and Scholarly answers;
- How to preserve scope, safety, and user agency.

### 4.3 Exact and current evidence

Remains primarily in:

- Deterministic text and linguistic tools;
- The Translation Nuance graph;
- Apparatus and version tools;
- Scholarship retrieval;
- Citation and publication-status services;
- Immutable evidence packets.

### 4.4 Product authority

Remains in:

- The Runtime Scholar Harness;
- Rights and policy systems;
- Verification;
- Human review;
- Owner-approved designs.

A model checkpoint never becomes the authoritative source of exact biblical wording, manuscript support, publication status, rights, consensus, or current scholarship.

Research comparing unsupervised fine-tuning with retrieval has found retrieval more reliable for injecting factual knowledge, including new facts not present in the original model. That evidence reinforces the project's retrieval-first treatment of exact and current scholarship while preserving continued pretraining for domain representation and task capability.[^fine-tuning-or-retrieval]

## 5. Canonical training entities

The implementation must support at least the following immutable records.

### `TrainingProgram`

A reviewed set of lineages and stage hypotheses associated with one product or research objective.

### `TrainingLineage`

An append-only branch of model artifacts from one immutable parent.

### `TrainingStageSpecification`

Binds:

```text
stage identity and hypothesis
parent checkpoint
model bundle and component map
corpus and mixture snapshot
objective set
component-update policy
precision and runtime policy
sequence-length distribution
optimizer and scheduler specification
evaluation and checkpoint schedule
preservation plan
stop and promotion gates
budget and campaign identity
```

### `TrainingObjectiveSpecification`

Defines:

```text
objective type
input and target schema
loss-bearing fields
loss masks
objective weight or schedule
sample eligibility
component targets
metrics
known failure modes
```

### `ComponentUpdatePolicy`

Identifies every trainable, frozen, low-learning-rate, adapter-only, or evaluation-only component.

### `CapabilityPreservationPlan`

Identifies the parent-relative abilities that must be measured and the replay or regularization mechanisms intended to protect them.

### `CheckpointArtifact`

Binds model state, optimizer state where applicable, scheduler state, RNG state, data position, mixture identity, tokenizer, processor, runtime, and lineage.

### `StageEvaluationRecord`

Records the exact candidate, baselines, development benchmark, retention suite, costs, failures, and gate result.

### `StagePromotionDecision`

One of:

```text
PROMOTE
PROMOTE_WITH_LIMITATIONS
REPAIR_AND_REPEAT
NO_GO
STOP_PROGRAM
DESIGN_REVIEW_REQUIRED
```

Only ChatGPT may recommend the scientific disposition; only Joseph may approve promotion.

## 6. No-training baselines precede gradient updates

Before any model receives project training, DR-18 requires baseline evaluation of:

```text
vendor post-trained checkpoint alone
vendor post-trained checkpoint + deterministic tools
vendor post-trained checkpoint + RAG
vendor post-trained checkpoint + tools + RAG
vendor post-trained checkpoint + complete A0 Runtime Scholar Harness
full-New-Testament and hybrid context modes where relevant
larger capacity comparator using the same harness
prior-art systems such as Rhema BibleAI where reproducible
```

These baselines establish:

- Which deficits already disappear through structure, tools, and retrieval;
- Which failures appear model-capacity-related;
- Which tasks are limited by corpus or benchmark quality;
- Whether training is justified;
- The parent-relative retention target for every later checkpoint.

No training stage may claim a product gain by comparing only with the bare model when the product baseline includes the full harness.

## 7. Approved model lineages

### 7.1 `PRODUCT_FIRST`

Starts from an official post-trained checkpoint.

```text
vendor post-trained checkpoint
    → A0 tools/RAG/runtime baseline
    → scholarly and retrieval-aware PEFT or bounded adaptation
    → preference optimization, if justified
```

Purpose:

- Reach a useful product quickly;
- Preserve vendor instruction following, reasoning, tool use, multimodal alignment, and safety behavior;
- Determine how much domain training is actually needed.

Initial preference:

- Parameter-efficient or low-learning-rate adaptation;
- Strong general, multilingual, and multimodal replay;
- Full-parameter changes only after a matched experiment demonstrates need.

### 7.2 `CLEAN_BASE`

Starts from an official pretrained-only checkpoint.

```text
official Base checkpoint
    → ancient/context continued pretraining
    → Translation Nuance mid-training
    → scholarly SFT
    → retrieval/tool-aware SFT
    → preference optimization
```

Purpose:

- Measure what our corpus and curriculum add;
- Avoid conflating project training with vendor post-training;
- Produce the cleanest scientific attribution.

### 7.3 `LARGE_CAPACITY_COMPARATOR`

Begins inference-only.

Purpose:

- Measure whether compact-model failures are capacity-limited;
- Supply a difficult-query fallback candidate;
- Provide bounded, verified teacher candidates where approved.

Training a 27B–31B comparator requires a separate capacity-value gate.

### 7.4 `MOBILE_STUDENT`

Begins only after a successful parent system exists.

Purpose:

- Distill bounded tool use, Translation Nuance behavior, and answer rendering into a 2B–4B mobile model;
- Preserve local privacy and offline utility;
- Escalate difficult cases to a larger route.

### 7.5 Lineage separation

A lineage is never overwritten.

The project preserves:

```text
parent
stage checkpoint
selected checkpoint
rejected checkpoints
adapters
merged derivatives
quantized derivatives
mobile packages
```

A model merge, adapter merge, or component replacement creates a new derivative lineage.

## 8. Curriculum overview

The approved curriculum is a set of gated stages rather than one combined training run.

| Stage | Primary purpose | Default objective class |
|---|---|---|
| `S0_BASELINE` | Establish untrained system capability | No weight update |
| `S1_STRATEGY_SMOKE` | Test stability, update policy, replay, and family support | Small CPT/SFT/PEFT probes |
| `S2_ANCIENT_CONTEXT_CPT` | Improve ancient and biblical language/domain representation | Causal next-token prediction |
| `S3_TRANSLATION_NUANCE_MIDTRAIN` | Learn structured translation relations and diagnoses | Generative structured and contrastive objectives |
| `S4_SCHOLARLY_SFT` | Teach scholarly operations and answer contracts | Supervised conditional generation |
| `S5_RETRIEVAL_TOOL_SFT` | Teach robust use of evidence, tools, and distractors | Retrieval/tool-aware SFT |
| `S6_BEHAVIOR_PREFERENCE` | Shape refusal, citation, uncertainty, scope, and style | Preference optimization |
| `S7_DISTILL_MOBILE` | Create smaller local derivatives | Verified distillation and PEFT |
| `S8_ARCHITECTURE_EXTENSION` | Test A2–A5 only after persistent deficits | Separately approved objectives |

The exact stage numbering in production code may differ. The logical separation may not.

## 9. Stage S1 — strategy and stability smoke

Before the main curriculum, every surviving compact family receives a bounded screen.

The screen may compare:

```text
Base full-parameter CPT smoke
Base PEFT CPT smoke, if technically meaningful
post-trained PEFT SFT
post-trained low-learning-rate adaptation
component freeze strategies
replay strategies
multimodal replay
short model-delta or merge experiment
```

The purpose is not to select a final model from 20–50M tokens alone. It is to eliminate:

- Unsupported training stacks;
- Unstable component updates;
- Excessive forgetting;
- Severe multimodal drift;
- Impractical memory or throughput;
- Incompatible checkpoint or resume behavior.

The same frozen scholarly units, evaluation cases, and resource accounting must be used across candidates as far as architecture permits.

## 10. Stage S2 — ancient/context continued pretraining

### 10.1 Hypothesis

Continued pretraining on a provenance-preserving ancient and biblical corpus will improve:

- Ancient-language modeling;
- Domain vocabulary and constructions;
- Cross-text familiarity;
- Contextual understanding of ancient genres;
- The internal representations required for later Translation Nuance and scholarly tasks.

Domain-adaptive pretraining has produced gains across specialized domains, but its value here must still be measured against the complete A0 tools-and-RAG baseline.[^dont-stop-pretraining]

### 10.2 Default objective

The baseline objective is causal next-token prediction over DR-17-approved sequences.

The stage does not initially add:

- Preference loss;
- Reward optimization;
- Unreviewed auxiliary heads;
- Tool-call loss;
- Hidden chain-of-thought targets;
- Modern-scholarship memorization objectives.

### 10.3 Intended data

The stage may include, under exact rights and mixture approval:

- Primary biblical and ancient texts;
- Linguistic and textual representations suitable for causal modeling;
- Documentary language context;
- Selected historical and literary context;
- Ancient versions;
- General multilingual replay;
- Multimodal replay appropriate to the family.

Modern scholarship remains retrieval-first by default.

### 10.4 What CPT is not expected to prove

A lower domain loss does not prove that the model can:

- Perform textual criticism;
- Diagnose translation causes;
- Use citations correctly;
- Distinguish consensus from reception history;
- Follow the runtime contract;
- Refuse harmful or unrelated requests;
- Preserve page understanding.

Those require downstream benchmark evidence.

## 11. Stage S3 — Translation Nuance mid-training

### 11.1 Hypothesis

Structured exposure to exact source/translation relationships, alignments, lineages, and causal diagnoses will improve the model's ability to consume and produce DR-06 and DR-12 structures beyond raw parallel-text familiarity.

### 11.2 Objective classes

The A1 baseline may use generative or contrastive tasks such as:

- Source and target identity reconstruction;
- Many-to-many alignment prediction and repair;
- Translation-difference-unit detection;
- Source-textual-state classification;
- Multi-axis cause diagnosis;
- Ordered causal-chain generation;
- Upstream versus proximate cause classification;
- Translation-family and revision-lineage discrimination;
- Variant-versus-translation-choice diagnosis;
- Target-language constraint explanation;
- Intent-versus-effect separation;
- Evidence and counterevidence selection;
- Calibrated abstention;
- Word-study-fallacy correction;
- Cross-language pivot disclosure;
- Bounded translation-option generation with explicit tradeoffs.

### 11.3 Raw repetition is insufficient

Hundreds of parallel New Testament translations may not simply be concatenated and treated as the primary learning objective.

Targum, eBible, and other translation collections are used through:

- Work and edition identity;
- Family-aware sampling;
- Held-out lineage evaluation;
- Structured comparison frames;
- Target-language and historical metadata;
- Exact source-text compatibility;
- Passage-level exposure controls.

### 11.4 A1 precedes architectural extensions

S3 initially preserves foundation-model topology.

Auxiliary heads, relation adapters, graph memory, specialist routing, or A6 core modification remain governed by DR-12 and become eligible only after the A1 structured-objective baseline shows a persistent representational deficit.

## 12. Stage S4 — scholarly supervised fine-tuning

### 12.1 Hypothesis

A relatively compact, high-quality, evidence-grounded SFT corpus can teach the model to perform the project's scholarly operations and answer contract once the necessary representations and tools exist.

Work such as LIMA provides evidence that carefully curated instruction data can strongly shape behavior even at modest scale, but Biblical Scholar Lab still requires domain-specific evaluation and cannot infer that a small dataset automatically supplies missing knowledge.[^lima]

### 12.2 Required task families

SFT must cover:

- Passage and edition resolution;
- Original-language explanation;
- Translation Nuance;
- Textual variant versus translation-choice distinction;
- Ancient versions and apparatus restraint;
- Historical and intertextual analysis;
- Scholarly landscape synthesis;
- Citation and quotation provenance;
- Evidence-versus-inference separation;
- Brief, Study, and Scholarly rendering;
- Multilingual and cross-lingual workflows;
- Page-image and paratext analysis;
- Scope and supporting research tasks;
- Sensitive-use and authority boundaries;
- User corrections and uncertainty.

### 12.3 Structure-first targets

The preferred target is not prose alone.

Training examples should include, where appropriate:

```text
task and assurance identity
research-plan steps or validated tool actions
evidence handles
ScholarAnswerCandidate or TNC candidate
claim/evidence links
epistemic status
counterevidence
citations
final answer
```

The model is not trained to emit private chain-of-thought. It may learn explicit, auditable plans, tool actions, concise rationale, evidence mappings, and structured scholarly analysis.

### 12.4 General instruction replay

Clean-Base lineages require enough general instruction replay to avoid becoming a narrow completion model.

Product-first lineages require enough vendor-behavior retention data to prevent domain SFT from degrading broad instruction following.

Exact replay sources and ratios remain experiment-design decisions.

## 13. Stage S5 — retrieval- and tool-aware supervised fine-tuning

### 13.1 Hypothesis

A model trained to use retrieved evidence, ignore distractors, cite exact spans, request missing sources, and call deterministic tools will outperform ordinary SFT in the open-book Runtime Scholar Harness.

RAFT demonstrates a domain-RAG training pattern in which models learn to use relevant documents and resist distractors.[^raft] Biblical Scholar Lab adopts the general open-book and distractor-training idea while replacing any uninspectable reasoning target with project-owned structured plans, evidence handles, and concise rationale.

### 13.2 Training inputs

Examples may include:

- Relevant evidence;
- Plausible distractors;
- Contradictory or outdated sources;
- Incomplete evidence packets;
- Rights-redacted evidence;
- Wrong-edition or wrong-passage candidates;
- Duplicate and dependent sources;
- Tool failures;
- Compacted state requiring rehydration;
- Multilingual pivots;
- Page OCR/VLM disagreements.

### 13.3 Required learned behavior

The model should learn to:

- Select the correct tool;
- Use exact source identities;
- Ignore irrelevant evidence;
- Identify material missing evidence;
- Distinguish tool results from instructions;
- Cite the exact supporting span;
- Preserve counterevidence;
- Qualify or abstain when support is incomplete;
- Request clarification only when material;
- Avoid relying on model memory when an exact tool exists.

### 13.4 Generator and retriever remain separable

The first baseline does not jointly optimize the generator, retriever, and reranker in one opaque loop.

Retriever and reranker adaptation receive separate component identities, data, objectives, and ablations. Joint optimization may be tested later only if independent components prove insufficient.

## 14. Cross-cutting multilingual preservation

Multilingual support is not deferred until one late translation pass.

Every stage records performance and exposure by:

- Interface language;
- Ancient language variety;
- Script;
- Translation direction;
- Question and answer language;
- Evidence language;
- Pivot route.

The curriculum includes:

- General multilingual replay;
- Native-language SFT cases;
- Parallel multilingual cases;
- Cross-lingual research cases;
- Language-specific tool and citation behavior;
- Worst-language and worst-script evaluation.

Machine-translated training examples remain candidates until the level of review required by DR-13 is satisfied.

## 15. Cross-cutting multimodal preservation

Every text-focused stage risks damaging page and general visual behavior.

The preservation plan must identify:

- Visual or unified-modal components;
- Trainable and frozen components;
- Multimodal replay;
- Page-specific SFT examples;
- General visual-retention cases;
- Parent-relative OCR, layout, image-tool, and prompt-injection tests.

Family-specific rules from DR-11 and DR-14 apply.

A stage is not promoted when its text gains materially damage required page behavior unless a modular visual/text architecture has been explicitly selected and evaluated.

## 16. Cross-cutting long-context preservation

Training does not automatically use the maximum model window.

The initial curriculum should use a measured distribution of short and medium sequences, with long-context examples added only under DR-15's evidence and benchmark contract.

Every stage tests:

- Focused passage behavior;
- Book-level context;
- Full-New-Testament and hybrid context where relevant;
- Evidence-position sensitivity;
- Tool and citation retention;
- Compaction and rehydration;
- Short-context regression.

A gain at maximum length cannot justify damage to ordinary passage analysis.

## 17. Replay architecture

Replay is a first-class curriculum component rather than an emergency fix after forgetting occurs.

The approved replay categories include:

```text
GENERAL_MULTILINGUAL_REPLAY
GENERAL_INSTRUCTION_REPLAY
PRIOR_DOMAIN_REPLAY
TRANSLATION_NUANCE_REPLAY
TOOL_AND_RETRIEVAL_REPLAY
MULTIMODAL_REPLAY
SCOPE_AND_SAFETY_REPLAY
LONG_CONTEXT_REPLAY
```

Continual multi-domain training can cause general-domain deterioration, and replay is a well-established mitigation candidate.[^multi-domain-forgetting] Recent work also continues to find value in general-sample replay for preserving broad capability during sequential LLM adaptation.[^general-replay]

Exact ratios, datasets, and schedules are not fixed by DR-18. Their presence, identity, and ablation are mandatory.

## 18. Replay data must be rights- and contamination-safe

Replay is not exempt from DR-10 or DR-17.

Every replay source must have:

- Approved operation rights;
- Exact provenance;
- Split and holdout compatibility;
- Language and modality identity;
- Exposure accounting;
- No private final benchmark leakage.

The project may not replay unknown fragments of the foundation model's original training data merely because they would be useful for retention.

## 19. Sequence representation and metadata visibility

Every stage defines whether the model sees:

- Plain source text;
- Canonical reference labels;
- Work and edition identity;
- Language and script labels;
- Translation-family metadata;
- Textual-form identity;
- Evidence handles;
- Review state;
- Rights-safe provenance labels;
- Structured schemas.

Metadata is exposed only when it serves a named capability.

The model must not learn hidden shortcuts such as:

- A publisher label proving confessional intent;
- A corpus name proving a source is correct;
- A benchmark-specific marker revealing the target;
- A translation family label substituting for linguistic analysis.

Metadata ablations are required where leakage or shortcut learning is plausible.

## 20. Objective taxonomy

The project supports the following logical objective classes.

### `CAUSAL_LANGUAGE_MODELING`

Next-token prediction over approved source sequences.

### `CONDITIONAL_GENERATION`

Generate a structured or natural-language target from an approved input.

### `STRUCTURED_RECONSTRUCTION`

Recover omitted identities, alignments, relations, or fields from evidence.

### `CONTRASTIVE_SELECTION`

Choose relevant evidence, compatible readings, or preferred analyses among reviewed alternatives.

### `MULTI_LABEL_CLASSIFICATION`

Identify several compatible Translation Nuance cause axes or evidence roles.

### `PAIRWISE_OR_SET_ALIGNMENT`

Learn many-to-many, discontinuous, and null span relations.

### `TOOL_ACTION_SUPERVISION`

Produce typed, bounded tool calls and process results.

### `CITATION_AND_ENTAILMENT`

Select exact evidence and link claims to supporting or contradicting spans.

### `CALIBRATION_AND_ABSTENTION`

Learn when evidence is sufficient, partial, conflicted, inaccessible, or absent.

### `PREFERENCE_OPTIMIZATION`

Increase preferred behavior relative to reviewed rejects.

### `DISTILLATION`

Transfer verified capabilities to another approved model while preserving source and teacher provenance.

### `AUXILIARY_HEAD_OBJECTIVE`

Separately gated objective under DR-12 A2.

An objective class does not authorize a specific algorithm or loss implementation by itself.

## 21. Objective composition is explicit

No training stage may silently combine several losses because a framework enables them.

Every multi-objective stage records:

```text
objective names
sample eligibility
loss masks
loss weights or schedules
component targets
normalization method
interaction assumptions
metrics
ablation plan
```

The project must be able to answer:

- Which objective produced a gradient for this sample?
- Which components received that gradient?
- How much exposure came from each objective?
- Did one high-volume objective suppress a rare but essential one?

Loss weighting is an experiment-design decision. Sol may implement the approved policy but may not select the scientific tradeoff.

## 22. Full-parameter and parameter-efficient adaptation

### 22.1 Clean Base CPT

Full-parameter continued pretraining is the default scientific reference for compact Base models when memory and stability permit.

A PEFT CPT variant may be screened for efficiency, but it does not automatically replace the full-parameter reference.

### 22.2 Product-first adaptation

PEFT is the default first adaptation strategy for post-trained product checkpoints because it:

- Reduces compute and optimizer memory;
- Preserves an exact parent fallback;
- Enables clean enable/disable ablations;
- Reduces the risk of broad post-training loss.

LoRA provides a standard low-rank adaptation mechanism with far fewer trainable parameters than full fine-tuning and no inherent additional inference latency once appropriately merged, although its suitability must still be measured per candidate architecture.[^lora]

### 22.3 Full-parameter promotion

Full-parameter product adaptation requires evidence that:

- PEFT cannot repair the named deficit;
- The gain survives retention tests;
- The additional compute is justified;
- The full checkpoint is preferable to a modular adapter;
- Rollback and release implications are understood.

## 23. Component-update policy is family-specific

Every run explicitly identifies the update state of:

- Embeddings and output head;
- Foundation blocks;
- Attention and DeltaNet components;
- Vision encoder or unified modality path;
- Projectors;
- MTP/draft components;
- Norms;
- Adapters;
- Auxiliary heads;
- Graph-memory components;
- Specialist components.

There is no universal “freeze vision tower” rule because the model families differ materially.

A component omitted from the policy is not implicitly trainable.

## 24. Tokenizer and embeddings remain unchanged in the baseline

DR-11's no-tokenizer-surgery baseline applies throughout the initial curriculum.

The project may measure tokenizer inefficiency and train the existing embeddings through normal model updates, but it may not:

- Add tokens;
- Reassign IDs;
- Replace the tokenizer;
- Resize embeddings;
- Alter normalization;
- Modify special tokens;

without a separate approved experiment.

## 25. Precision and numerical policy

The scientific master checkpoint uses BF16 or another explicitly approved high-precision format appropriate to the model and hardware.

FP8, lower-precision optimization, quantized training, or alternate kernels are separate performance experiments.

Every run records:

- Precision by component and state;
- Loss-scaling behavior;
- Active attention and architecture kernels;
- Fallback paths;
- Numerical anomalies;
- Parent-relative output and benchmark changes.

A silent kernel or precision fallback is a run defect.

## 26. Optimization parameters are approved experiment inputs

The following are scientific variables rather than Sol implementation discretion:

```text
optimizer family
learning rate and layer-wise groups
warmup
scheduler
weight decay
gradient clipping
effective batch and accumulation
sequence-length distribution
objective weights
component freeze policy
replay ratio
checkpoint cadence
stop rule
```

DR-18 does not fix their final numbers.

They will be defined through bounded, owner-approved strategy screens and run designs. Sol may recommend values and implement the search, but may not select or change the approved range independently.

## 27. Stable training before scale

Every lineage progresses through:

```text
unit and data-path tests
single-batch overfit or loss sanity
very small local or cloud smoke
interrupt/resume validation
short capped training probe
full pilot
main run
```

A stage does not scale while:

- Loss is unstable;
- Resume behavior is unverified;
- Exposure logs are incomplete;
- Multimodal or multilingual regressions are unexplained;
- Evaluation artifacts cannot be reproduced;
- Cost forecast is based only on theoretical throughput.

## 28. Checkpoints have distinct purposes

The system distinguishes:

```text
RESUMABLE_TRAINING_CHECKPOINT
MODEL_ONLY_EVALUATION_CHECKPOINT
MILESTONE_CHECKPOINT
SELECTED_STAGE_CHECKPOINT
REJECTED_CHECKPOINT
PUBLIC_RELEASE_CANDIDATE
```

A resumable checkpoint may contain optimizer and RNG state that cannot be released.

A model-only checkpoint may be sufficient for evaluation but not exact resume.

Checkpoint pruning must preserve the artifacts needed to reproduce the selected result and investigate failures.

## 29. Checkpoint selection cannot use the private final benchmark

The curriculum uses:

- Training metrics for stability;
- Development benchmarks for iteration;
- Frozen nonfinal held-out sets for stage promotion;
- Private final and fresh challenge sets only at the approved final evaluation stage.

The best checkpoint is selected according to preregistered metrics and constraints.

The project must not repeatedly evaluate every checkpoint on the private holdout and choose the highest score.

## 30. Checkpoint selection is multi-objective

A single scalar cannot safely choose the model.

The decision should consider a Pareto-style set including:

- Target scholarly capability;
- Translation Nuance;
- Citation and evidence integrity;
- General capability retention;
- Multilingual retention;
- Multimodal retention;
- Long-context retention;
- Scope and safety;
- Memorization and extraction;
- Latency, memory, and cost.

Hard failures disqualify a checkpoint regardless of its average score.

## 31. Training loss is diagnostic—not a promotion metric

The project reports loss and perplexity by:

- Corpus role;
- Language and variety;
- Work and passage cluster;
- Quality tier;
- General replay;
- Sequence length;
- Objective;
- Model component where relevant.

A lower aggregate loss cannot hide:

- Memorization;
- Translation-family dominance;
- General forgetting;
- Citation regression;
- Page degradation;
- Language collapse;
- Safety or scope failure.

## 32. Parent-relative capability preservation

Every selected checkpoint is compared with its exact parent on:

- General language and reasoning;
- Instruction following;
- Tool use;
- Structured output;
- Greek, Hebrew, Aramaic, Latin, Syriac, Coptic, and modern-language canaries;
- Multimodal and page tasks;
- Context and compaction;
- Citation and evidence behavior;
- Scope and sensitive-use behavior;
- Quantization or deployment compatibility where relevant.

The comparison is stage-specific and versioned.

## 33. Forgetting mitigation is an ablation—not a hidden recipe

Candidate mitigation strategies may include:

- General and prior-stage replay;
- Component freezing;
- Lower or layer-wise learning rates;
- PEFT;
- Regularization or trust-region-like constraints;
- Model-delta or weight-space merging;
- Separate modular adapters;
- A tiered product architecture.

No mitigation is assumed optimal in advance.

The simplest method that preserves required capability and achieves the target gain is preferred.

## 34. Retrieval-aware training must not create blind context obedience

The model should not learn:

```text
retrieved document present
→ document must be correct
```

Training must include:

- Correct model knowledge with misleading retrieval;
- Relevant evidence mixed with distractors;
- Contradictory sources;
- Retracted or outdated scholarship;
- Unsupported claims attached to real citations;
- Empty retrieval;
- Rights-redacted evidence;
- Evidence that supports only part of the answer.

Research on RAG adaptation shows that noisy or misleading retrieval can itself create errors, motivating explicit training and evaluation of evidence filtering rather than unconditional retrieval dependence.[^rule-rag]

## 35. Synthetic data remains candidate data

Synthetic data may be used for:

- Task coverage;
- Negative examples;
- Controlled minimal pairs;
- Page rendering;
- Translation Nuance contrast sets;
- Tool-use traces;
- Preference candidates;
- Distillation.

Every synthetic record retains:

```text
source evidence
teacher model and revision
prompt and tools
sampling configuration
output hash
automatic validation
human review state
accepted and rejected fields
lineage and rights
```

A synthetic answer does not become gold because a larger model generated it.

## 36. Teacher models are proposal generators—not authorities

A large model may propose:

- Candidate questions;
- Structured analyses;
- Translation differences;
- Distractors;
- Preference alternatives;
- Explanations;
- Tool plans.

Promotion requires deterministic verification, exact source evidence, qualified review, or an approved combination.

The teacher's unsupported confidence cannot be distilled into the student as fact.

## 37. Negative, contrastive, and abstention data are first-class

The curriculum must include cases where the correct behavior is to:

- Reject a false textual-variant premise;
- Identify no material translation difference;
- Say that several source readings remain compatible;
- Refuse to invent a quotation;
- Distinguish historical commentary from current scholarship;
- Identify a hidden pivot;
- Decline to infer translator intent;
- Ask for an edition or image clarification;
- Abstain when the source is unavailable;
- Redirect an unrelated request;
- Avoid over-refusing a supporting research task.

The model must not learn that every prompt requires a confident, elaborate answer.

## 38. Preference optimization is planned but separately designed

DR-18 reserves a later behavior-shaping stage after scholarly and retrieval-aware SFT.

The first preference experiment should compare:

```text
SFT-only parent
versus
SFT + reviewed preference optimization
```

A DPO-style method is the initial algorithmic candidate because it provides a relatively simple, stable, offline preference objective without requiring a separately trained reward model or online PPO loop.[^dpo]

Rhema reports that fewer than 1,000 targeted preference pairs materially shaped BibleAI's conversational behavior. That is useful prior-art motivation, not causal proof for our model or data.[^rhema]

The current planning target remains approximately 800–1,500 high-quality pairs spanning:

- Exact quotation and tool use;
- Citation integrity;
- Linguistic uncertainty;
- Witness/edition/translation distinctions;
- Competing interpretations;
- Concision and requested depth;
- Scope and anti-over-refusal;
- Multilingual behavior;
- Page and OCR uncertainty;
- False-premise correction;
- Sensitive-use behavior.

DR-19 will define the binding preference-data and algorithm contract.

## 39. Online reinforcement learning is not the default

Broad online RL, PPO, self-rewarding loops, or autonomous reward optimization are not authorized by DR-18.

They require a separate design demonstrating:

- A named failure not solved by SFT, DPO, tools, retrieval, or verification;
- A defensible reward signal;
- Resistance to reward hacking;
- Stable and affordable rollout infrastructure;
- Preservation of citation, safety, multilingual, and multimodal behavior;
- Independent evaluation.

## 40. Model merging is an optional controlled experiment

Possible merge experiments include:

- Domain Base-CPT delta with a matched post-trained model;
- General instruction retention merge;
- Adapter composition;
- Multimodal preservation merge.

A merge creates a new model artifact and lineage.

It must be compared with:

- The unmerged parent;
- The domain-adapted parent;
- Direct SFT or PEFT alternatives;
- The same runtime and benchmark.

Cross-family merges are not authorized.

## 41. Specialist and retriever curricula remain separate

The following components may later receive their own training lineages:

- Retriever;
- Reranker;
- Citation-entailment verifier;
- Alignment model;
- Translation-cause classifier;
- Page-region model;
- Language specialist;
- Graph encoder;
- Mobile student.

Their data, objectives, checkpoints, and promotion gates remain separate from the main generator.

A specialist output remains candidate evidence under DR-12 and DR-16.

## 42. Architecture-extension curriculum

A2–A5 experiments become eligible only after the A0/A1 baseline demonstrates a persistent Translation Nuance deficit.

The sequence remains:

```text
A2 auxiliary heads
→ A3 relation-aware adapter
→ A4 graph-memory sidecar
→ A5 specialist or routed system
```

Each extension receives:

- One named representational hypothesis;
- One matched no-extension baseline;
- One exact component-update policy;
- One disable and rollback path;
- Parent-relative capability tests;
- Runtime and deployment cost analysis.

A6 core architecture modification remains separately gated.

## 43. Distillation and mobile curriculum

A mobile student is trained only from:

- Approved open or compatible source data;
- Verified teacher outputs;
- Tool-use traces whose sources are available to the student route;
- Short evidence-packet tasks;
- Translation Nuance structures suitable for the student;
- Mobile-specific OCR and page workflows;
- Scope, safety, citation, and escalation examples.

The student is not expected to reproduce the full 9B–31B system.

Its contract may emphasize:

- Local passage study;
- Deterministic lookup;
- Basic translation comparison;
- Short-context source-grounded explanation;
- Local page OCR orchestration;
- Explicit escalation.

## 44. Quantization follows training—not vice versa

The high-precision selected checkpoint remains the reference.

Quantized derivatives are evaluated separately for:

- Ancient scripts;
- Morphology and Translation Nuance;
- Tool syntax;
- Citations;
- Calibration;
- Refusal behavior;
- Page understanding;
- Multilingual output;
- Long context;
- Memory, speed, battery, and thermal behavior.

A quantized result cannot be used to judge the training curriculum unless the high-precision parent is reported beside it.

## 45. Training records expose actual learning conditions

Every run must preserve:

- Parent checkpoint and exact components;
- Corpus, split, mixture, and exposure identities;
- Objective schedule;
- Trainable components;
- Optimizer and scheduler;
- Precision and kernels;
- Effective batch and sequence lengths;
- Gradient and stability telemetry;
- Checkpoint schedule;
- Evaluation results;
- Cost and hardware;
- Interruptions, retries, resumes, and skipped samples;
- Actual final step and reason for stopping.

A dashboard is not the authoritative record. The immutable run artifacts are.

## 46. Stage evaluation schedule

Every stage includes at least:

```text
parent baseline
preflight smoke evaluation
periodic development evaluation
final stage evaluation
parent-relative retention evaluation
memorization and extraction tests
cost and efficiency report
```

The exact cadence is selected in the approved stage experiment based on run length and cost.

Evaluation should be frequent enough to detect divergence or forgetting without repeatedly tuning against the final benchmark.

## 47. Stage promotion is capability-based

A stage advances only when:

- The named capability improves by the preregistered threshold;
- The gain survives a matched baseline and relevant ablations;
- No hard failure triggers;
- General, language, multimodal, long-context, safety, and citation retention remain within approved bounds;
- Memorization and extraction remain acceptable;
- The run is reproducible and fully identified;
- The measured cost supports the next stage;
- Expert review supports the interpretation;
- ChatGPT recommends promotion;
- Joseph approves it.

A plateau, small gain, or regression may end the lineage even when more data and credits remain.

## 48. Main research ablations

At minimum, the final training program should isolate:

```text
A0 full runtime without project training
product-first scholarly SFT/RAFT
clean Base ancient CPT
clean Base CPT + Translation Nuance mid-training
clean Base CPT + TNC + scholarly SFT
clean Base CPT + TNC + scholarly SFT + retrieval/tool SFT
SFT-only versus SFT + preference optimization
compact versus large model under the same harness
with versus without general replay
with versus without multimodal replay
with versus without multilingual native cases
with versus without full-New-Testament context
high-precision versus quantized derivative
```

Not every comparison requires a full main-scale run. Proxy and compact-model experiments may eliminate weak strategies before 9B–12B confirmation.

## 49. Budget is allocated by evidence gates

The active budget remains a sequence of capped decisions rather than one program-wide permission to spend.

The curriculum should reserve budget for:

- Baseline and benchmark inference;
- Model-family and strategy screens;
- One meaningful CPT pilot;
- One selected main lineage;
- Translation mid-training;
- Scholarly and retrieval-aware SFT;
- Preference ablation;
- Final evaluation and contingency.

A model family, stage, or architecture that fails its gate loses its later allocation.

## 50. Sol and Luna authority

Sol implements:

- Training data materialization;
- Objective and loss code;
- Component update policies;
- Training, checkpoint, resume, and evaluation infrastructure;
- Approved model and framework adapters;
- Tests and evidence reports.

Sol may recommend experimental changes but may not independently alter:

- Stage order;
- Training hypotheses;
- Data eligibility or mixture;
- Objectives or loss weights;
- Trainable components;
- Replay policy;
- Hyperparameter range;
- Evaluation sets;
- Promotion thresholds;
- Budget.

Luna may execute only frozen, approved campaigns delegated by Sol.

Luna may not:

- Write or repair code;
- Change data, objectives, components, or hyperparameters;
- Extend runtime or cost;
- Select a checkpoint;
- Interpret results;
- Promote a stage.

A code or design defect stops execution with:

```text
BLOCKED_REQUIRES_SOL_REPAIR
```

or:

```text
BLOCKED_REQUIRES_DESIGN_REVIEW
```

## 51. Training hard failures

DR-18 treats the following as hard failures:

- Beginning adaptation before the complete A0 baseline exists.
- Combining CPT, SFT, retrieval training, and preferences so that their effects cannot be isolated.
- Training on private holdout, fresh challenge, or rights-ineligible material.
- Treating modern scholarship memorization as a replacement for retrieval.
- Allowing translation repetition to dominate the objective without lineage controls.
- Omitting general replay without an explicit ablation.
- Damaging required multilingual or multimodal capability without disclosure.
- Selecting a checkpoint using the private final benchmark.
- Promoting a stage on training loss alone.
- Treating model-generated data as gold without promotion.
- Training hidden chain-of-thought as a required product artifact.
- Teaching unconditional obedience to retrieved text.
- Hiding a pivot translation or source mismatch.
- Silently changing tokenizer, special tokens, model components, kernels, precision, objectives, or mixture.
- Modifying a live run rather than creating a new run identity.
- Failing to preserve the exact parent and rollback artifact.
- Reporting only the selected checkpoint and concealing failed or regressed checkpoints.
- Allowing a scalar average to hide citation, source, language, page, safety, rights, or memorization hard failures.
- Training a larger model merely because it exists without passing the capacity-value gate.
- Continuing a run merely to use remaining credits.
- Allowing Sol to redesign the curriculum or Luna to modify or interpret the campaign.

## 52. Sol implementation discretion

The training curriculum and objective semantics are project-owned.

Sol may determine reversible implementation mechanics such as:

- Module, class, and function organization;
- Efficient batching, sharding, checkpoint serialization, and telemetry;
- Framework adapters that preserve the approved objective exactly;
- Test fixtures;
- Performance optimizations that preserve numerical and semantic equivalence;
- Equivalent local data-loader or distributed-execution mechanics;
- Approved failure-recovery implementations.

Sol may not independently decide:

- The stage hypothesis;
- Stage order;
- Parent checkpoint;
- Data or replay mixture;
- Objective class, target, loss, or weight;
- Component update policy;
- Hyperparameter candidates;
- Sequence curriculum;
- Checkpoint-selection rule;
- Evaluation or promotion threshold;
- Preference or distillation design;
- Model merge;
- Architecture extension;
- Budget.

Any material limitation or alternative returns:

```text
BLOCKED_REQUIRES_DESIGN_REVIEW
```

## 53. Binding decisions

Approval of DR-18 would lock:

1. Every training stage has one explicit capability hypothesis, immutable parent, objective contract, preservation plan, and promotion rule.
2. The complete no-training tools/RAG/runtime baseline precedes model adaptation.
3. Tools and retrieval remain the preferred home for exact, current, rights-sensitive, and inspectable knowledge.
4. Domain representation, scholarly behavior, evidence, and product authority remain separate.
5. Training programs, lineages, stages, objectives, update policies, checkpoints, evaluations, and promotion decisions remain distinct immutable objects.
6. Product-first and clean-Base lineages remain separate.
7. Large models begin as capacity comparators and require a separate training gate.
8. Mobile students begin only after a successful parent system exists.
9. The curriculum separates strategy smoke, ancient CPT, Translation Nuance mid-training, scholarly SFT, retrieval/tool SFT, preference optimization, distillation, and architecture extensions.
10. No stage is automatic.
11. Ancient CPT uses causal language modeling as its baseline objective.
12. CPT is evaluated through downstream scholarly and retention metrics rather than loss alone.
13. Translation Nuance mid-training uses structured, family-aware objectives rather than raw parallel-text repetition.
14. A1 structured objectives precede A2–A6 architectural extensions.
15. Scholarly SFT uses structure-first, evidence-grounded targets without requiring private chain-of-thought.
16. Retrieval/tool SFT includes distractors, contradictions, missing evidence, rights constraints, tool failures, and rehydration.
17. Retriever, reranker, generator, verifiers, and specialists retain separate lineages and ablations.
18. Multilingual, multimodal, and long-context preservation are cross-cutting requirements at every stage.
19. General multilingual, instruction, prior-domain, tool, safety, multimodal, and long-context replay categories are explicit.
20. Replay data remain rights- and contamination-safe.
21. Sequence metadata is exposed only for a named capability and receives shortcut-learning ablations where needed.
22. Objective classes and multi-objective loss composition remain explicit and immutable.
23. Full-parameter Base CPT is the default scientific reference where feasible; PEFT is the default first product-first adaptation strategy.
24. Every trainable and frozen component is explicit and family-specific.
25. Tokenizer and embedding surgery remain outside the baseline.
26. High-precision checkpoints remain the scientific reference; precision and kernel changes are separate experiments.
27. Optimization variables and search ranges remain approved experiment inputs rather than Sol discretion.
28. Every lineage progresses through tests, smoke, resume validation, pilot, and main run rather than scaling immediately.
29. Resumable, model-only, milestone, selected, rejected, and release checkpoints remain distinct.
30. Private final benchmarks cannot select checkpoints.
31. Checkpoint selection is multi-objective and hard-failure aware.
32. Parent-relative capability preservation is mandatory.
33. Forgetting mitigations are controlled ablations.
34. Retrieval-aware training must resist misleading evidence rather than learn blind obedience.
35. Synthetic and teacher-generated data remain provenance-bearing candidates until promoted.
36. Negative, contrastive, correction, and abstention cases are first-class training data.
37. Preference optimization is planned but remains separately specified in DR-19 and compared with its SFT-only parent.
38. DPO is the initial offline preference candidate; online RL is not the default.
39. Model merging, specialists, distillation, quantization, and architecture extensions create separate derivative lineages.
40. Every run records exact learning conditions and actual exposure.
41. Every stage includes baseline, periodic, final, retention, memorization, extraction, cost, and failure evaluation.
42. Stage promotion is capability-, retention-, reproducibility-, expert-, and owner-gated.
43. Budget is released stage by stage and is not an instruction to spend remaining credits.
44. Sol implements the approved curriculum; ChatGPT designs and reviews experiments; Joseph approves consequential decisions.
45. Luna executes only frozen campaigns and has no code, design, interpretation, or promotion authority.

## 54. Decisions intentionally deferred

DR-18 does not yet select:

- The winning model family;
- Exact source inventory or mixture percentages;
- Exact general, instruction, multimodal, or prior-stage replay data and ratios;
- Final sequence-length distribution;
- Exact optimizer, scheduler, learning rate, weight decay, gradient clipping, or batch size;
- Exact component-specific learning-rate groups;
- Exact CPT token budget;
- Exact number and format of Translation Nuance tasks;
- Final SFT dataset size;
- Exact multilingual SFT proportions;
- Final tool and retrieval curriculum size;
- Exact preference algorithm, pair count, beta, or epoch count beyond the DR-19 design;
- Whether model merging is executed;
- Whether any 27B–31B model is adapted;
- Whether A2–A5 is promoted;
- Final distillation teacher, student, or mobile runtime;
- Exact checkpoint and evaluation cadence;
- Numerical promotion thresholds;
- Final training backend, distributed strategy, or cloud hardware.

Those decisions belong to DR-19, DR-20 through DR-25, DR-28, DR-29, and individual owner-approved experiments informed by the corpus census, benchmark, model bake-off, and strategy screens.

## 55. Approved statement

> **Biblical Scholar Lab will use a staged, falsifiable, capability-preserving training curriculum in which every gradient-bearing intervention has an immutable parent, one explicit capability hypothesis, approved data and objective contracts, a family-specific component-update policy, a replay and retention plan, preregistered baselines, bounded compute, and an owner-approved promotion rule. The complete tools, retrieval, Translation Nuance, context, verification, and Runtime Scholar Harness baseline will be evaluated before weight adaptation, and exact, current, rights-sensitive, and inspectable knowledge will remain primarily in deterministic tools and retrieval rather than being forced into model memory. Product-first post-trained lineages, clean Base continued-pretraining lineages, high-capacity comparators, mobile students, adapters, merges, quantized models, specialists, and architecture extensions will remain separate, rollback-safe artifacts. Ancient/context continued pretraining will begin with causal language modeling and mandatory general multilingual and multimodal preservation; Translation Nuance mid-training will use structured, lineage-aware alignment, causal-diagnosis, evidence, and abstention objectives rather than unweighted translation repetition; scholarly and retrieval-aware SFT will teach typed tool use, evidence selection, citation, counterevidence, answer modes, multilingual and page workflows, and calibrated uncertainty without requiring hidden chain-of-thought. Preference optimization will be compared with its SFT-only parent under a separately approved design, with DPO as the initial offline candidate and broad online RL separately gated. Every stage will preserve exact data exposure, objective, component, precision, kernel, checkpoint, evaluation, cost, and failure identity; use private final benchmarks only at the final approved stage; evaluate parent-relative general, linguistic, multilingual, multimodal, long-context, citation, safety, memorization, and extraction behavior; and stop when its named capability fails to improve or its regressions exceed approved bounds. Sol will implement the approved stages and may optimize only design-neutral mechanics, Luna may execute only frozen campaigns delegated by Sol, ChatGPT will design and review each experiment and interpret its evidence, and Joseph Abbud will retain sole authority to approve progression, budget, merge, model promotion, and release.**

---

## References

[^dont-stop-pretraining]: Suchin Gururangan et al., “Don't Stop Pretraining: Adapt Language Models to Domains and Tasks,” ACL 2020. The study found consistent gains from domain- and task-adaptive pretraining across several domains and tasks: https://aclanthology.org/2020.acl-main.740/

[^fine-tuning-or-retrieval]: Oded Ovadia et al., “Fine-Tuning or Retrieval? Comparing Knowledge Injection in LLMs,” EMNLP 2024. The study reports stronger factual knowledge injection from RAG than unsupervised fine-tuning across its evaluated settings and notes the difficulty of learning new facts through unsupervised adaptation: https://aclanthology.org/2024.emnlp-main.15/

[^lima]: Chunting Zhou et al., “LIMA: Less Is More for Alignment,” 2023. LIMA reports strong behavioral adaptation from 1,000 carefully curated supervised examples, motivating high-quality compact SFT as a baseline rather than proving sufficiency for Biblical Scholar Lab: https://arxiv.org/abs/2305.11206

[^raft]: Tianjun Zhang et al., “RAFT: Adapting Language Model to Domain Specific RAG,” 2024. RAFT trains models in open-book settings with relevant and distractor documents, providing a useful precedent for retrieval-aware domain adaptation: https://arxiv.org/abs/2403.10131

[^lora]: Edward J. Hu et al., “LoRA: Low-Rank Adaptation of Large Language Models,” 2021. LoRA freezes pretrained weights and learns low-rank updates, greatly reducing trainable parameters and optimizer memory in the evaluated models: https://arxiv.org/abs/2106.09685

[^multi-domain-forgetting]: Kristjan Arumae, Qing Sun, and Parminder Bhatia, “An Empirical Investigation Towards Efficient Multi-Domain Language Model Pre-training,” EMNLP 2020. The paper studies catastrophic forgetting during staged multi-domain pretraining and evaluates mitigation methods including replay: https://aclanthology.org/2020.emnlp-main.394/

[^general-replay]: Yunan Zhang et al., “GeRe: Towards Efficient Anti-Forgetting in Continual Learning of LLM via General Samples Replay,” 2025. The work studies general-sample replay and representation constraints for retaining broad capabilities during continual LLM adaptation: https://arxiv.org/abs/2508.04676

[^rule-rag]: Peng Xia et al., “RULE: Reliable Multimodal RAG for Factuality in Medical Vision Language Models,” EMNLP 2024. The work motivates explicit control of retrieved-context quantity and preference training against errors caused by over-reliance on misleading retrieval: https://aclanthology.org/2024.emnlp-main.62/

[^dpo]: Rafael Rafailov et al., “Direct Preference Optimization: Your Language Model Is Secretly a Reward Model,” 2023. DPO provides a comparatively simple offline preference objective without the separate reward-model and online PPO pipeline used in conventional RLHF: https://arxiv.org/abs/2305.18290

[^rhema]: Rhema, “Meet BibleAI: our first open-source model, free for the Church,” April 15, 2026. Rhema reports a three-stage CPT, SFT, and DPO process and says a targeted set of fewer than 1,000 preference pairs strongly shaped conversational behavior; Biblical Scholar Lab treats this as relevant prior art requiring independent ablation: https://rhemabible.co/blog/introducing-bibleai
