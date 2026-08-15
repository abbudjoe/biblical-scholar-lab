# DR-02-S02 — Model Capacity, Family Bake-Off, and Budget Policy

**Status:** APPROVED
**Parent design:** DR-02 — Scholarly Epistemology and Methodology
**Approved by:** Joseph Abbud
**Approval date:** 2026-08-15
**Supersedes:** earlier conversational assumptions that Qwen is selected or that a compact model is presumed sufficient

## 1. Purpose

This supplemental decision records the approved model-capacity assumptions, candidate-family policy, bake-off structure, and Lambda budget posture arising during DR-02 review.

Exact repositories and immutable revisions remain subject to a current official-release audit in DR-11 because model availability can change before implementation.

## 2. Model-capacity premise

A compact model is not expected to contain the complete scholarly system in its weights.

Biblical Scholar Lab distributes responsibility across:

| Capability | Primary system component |
|---|---|
| Exact biblical wording | Deterministic passage service |
| Morphology and structured linguistic data | Linguistic databases and tools |
| Witness, edition, and translation identity | Textual-history graph |
| Translation genealogy and causal structure | Translation Nuance Core |
| Modern scholarship | Retrieval library |
| Exact source spans and citations | Citation resolver |
| Consensus evidence | Scholarship metadata and retrieval |
| Claim/evidence mapping | Evidence ledger |
| Canon and versification mapping | Reference service |
| Page segmentation and text recognition | Multimodal model plus deterministic resolution |
| Comparison, explanation, synthesis, and interaction | Language model plus post-training |

The compact model must understand questions, select tools, interpret structured evidence, compare explanations, preserve claim types, compose calibrated assessments, and abstain or escalate when evidence or capacity is insufficient.

## 3. No presumed compact-model sufficiency

A 9B- to 12B-class model is a plausible primary engine, not a presumed sufficient model.

The benchmark must determine whether compact models can reliably perform:

- Translation Nuance diagnosis;
- original-language analysis;
- source-type discrimination;
- multi-source synthesis;
- citation-grounded assessment;
- long-context use;
- multilingual interaction;
- printed-page analysis;
- calibrated uncertainty.

A tiered architecture in which difficult cases escalate to a larger model is an acceptable success outcome rather than a failure of the compact-model research track.

## 4. Current official-release audit snapshot

The following facts were reverified from official model records on 2026-08-15 and must be audited again before DR-11 closes:

- [`Qwen/Qwen3.5-9B-Base`](https://huggingface.co/Qwen/Qwen3.5-9B-Base) is an official pretrained-only checkpoint intended for fine-tuning and research.
- [`Qwen/Qwen3.6-27B`](https://huggingface.co/Qwen/Qwen3.6-27B) is an official post-trained checkpoint, not a Base checkpoint.
- Google provides official [`Gemma 4 12B`](https://huggingface.co/google/gemma-4-12B) and [`Gemma 4 31B`](https://huggingface.co/google/gemma-4-31B) pretrained and instruction-tuned variants.
- Mistral provides official [`Ministral 3 8B Base`](https://huggingface.co/mistralai/Ministral-3-8B-Base-2512), [`Instruct`](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512), and [`Reasoning`](https://huggingface.co/mistralai/Ministral-3-8B-Reasoning-2512) variants.
- No Qwen3.8 open checkpoint is frozen into this design. Any later official release must pass the same admission audit and bake-off rule.

These facts are a dated audit snapshot, not a permanent model-selection decision.

## 5. Provisional candidate matrix

### 5.1 Compact clean-adaptation candidates

The initial Base-checkpoint bake-off should include:

```text
Qwen/Qwen3.5-9B-Base
google/gemma-4-12B
mistralai/Ministral-3-8B-Base-2512
```

### 5.2 Compact product candidates

The matched product-first evaluation should include the corresponding post-trained checkpoints:

```text
Qwen/Qwen3.5-9B
google/gemma-4-12B-it
mistralai/Ministral-3-8B-Instruct-2512
mistralai/Ministral-3-8B-Reasoning-2512
```

The Ministral Instruct and Reasoning variants may be screened before deciding which enters every expensive comparison.

### 5.3 Larger capacity candidates

The initial higher-capacity comparison should include:

```text
google/gemma-4-31B
google/gemma-4-31B-it
Qwen/Qwen3.6-27B
```

Gemma 4 31B supplies a clean large-Base and matched instruction lineage. Qwen3.6-27B is a post-trained product comparator and engineering fallback, not a clean CPT control.

A current strong frontier model and qualified human experts should provide ceiling and human-reference results on a representative benchmark subset.

Community-pruned, layer-reduced, unofficially renamed, or otherwise noncanonical derivatives may not substitute for an official intact foundation checkpoint in the primary bake-off.

## 6. Bake-off principle

No family is selected on generic benchmark reputation, release recency, parameter count, or vendor claims alone.

The project-specific bake-off will use the following approved planning weights, subject to formal reconciliation with the benchmark's scale and uncertainty model before execution:

| Category | Approved planning weight |
|---|---:|
| Translation Nuance and original-language analysis | 30% |
| Evidence use, citation fidelity, tool selection, and source distinctions | 15% |
| Ancient- and modern-language capability | 15% |
| Printed-page and document understanding | 10% |
| Full-book and full-New-Testament long-context performance | 10% |
| Adaptation stability and general/multimodal retention | 10% |
| Training, inference, quantization, and deployment cost | 10% |

The exact metric definitions, normalization, confidence treatment, and promotion threshold will be approved in DR-20 through DR-24 before execution.

## 7. Hard gates

A candidate cannot win merely through a high aggregate score if it exhibits material:

- source-type confusion;
- citation fabrication or non-entailment;
- Greek or Hebrew regression after adaptation;
- multimodal collapse;
- training-stack instability;
- rights or release incompatibility;
- non-reproducible checkpoint or tokenizer behavior;
- cost or latency outside approved limits.

## 8. Bake-off stages

### Stage 1 — No-training screening

Measure, using identical benchmark contracts where applicable:

- tokenizer efficiency by script and language;
- closed-book performance;
- fixed-evidence performance;
- deterministic-tool use;
- RAG performance;
- full-New-Testament context behavior;
- page-image understanding;
- latency, memory, and cost.

### Stage 2 — Compact adaptation smoke

Each surviving compact Base model receives the same approved small continued-pretraining sample and evaluation schedule. A planning range of 20–50 million effective tokens may be considered, but the final size is set in the experiment design.

Measure:

- held-out domain-loss improvement;
- general, multilingual, and multimodal retention;
- Translation Nuance change;
- throughput, memory, checkpointing, and resume reliability;
- cost per validated gain.

### Stage 3 — Small scholarly post-training

Each surviving compact product lineage receives the same approved scholarly SFT, retrieval-aware, and preference subset sufficient to compare behavioral learnability per dollar.

### Stage 4 — Capacity comparison

The larger candidates receive the same inference, tool, retrieval, long-context, and difficult-case evaluation before any large-model adaptation is authorized.

## 9. Gemma 12B and 31B treatment

Gemma 4 12B is approved as a full compact-model candidate and receives the complete compact bake-off if it passes Stage 1.

Gemma 4 31B is approved initially as an inference-only capacity comparator. It does not receive full-parameter or parameter-efficient adaptation in the initial bake-off.

A 31B adaptation experiment requires a new approved design gate based on evidence that its capacity solves important compact-model failures and that the gain justifies training and serving cost.

The approved provisional planning trigger is either:

- at least an eight-point absolute improvement on a preregistered capacity-sensitive subset; or
- at least a 50% reduction in designated epistemic hard failures;

with both forms requiring blinded expert confirmation and evidence that the gain is not merely verbosity, citation-format imitation, or benchmark leakage. The benchmark and experiment reviews must reconcile this planning trigger with the final score scale, confidence intervals, and hard-failure definitions before it becomes an executable promotion rule.

## 10. Budget policy

The approved planning posture is:

```text
Expected total project spend: approximately $2,800–$3,200
Active hard cap: $3,500
Untouched reserve: $500
Known Lambda credits: approximately $4,000
```

The Gemma 12B full compact bake-off plus Gemma 31B inference-only capacity comparison is allocated an incremental planning range of:

```text
$300–$700
```

This range is not a spending authorization. Each billable campaign still requires a separately approved immutable envelope and current provider price verification.

A provisional active allocation is:

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

The official [Lambda pricing page](https://lambda.ai/pricing) must be checked immediately before every campaign. Prices recorded during planning are not execution authorization.

## 11. Interpretation outcomes

The bake-off may produce any of these acceptable architectures:

1. **Compact primary:** a 9B–12B model performs near the larger systems and becomes the main engine.
2. **Tiered system:** the compact model handles ordinary study and tool orchestration, while a larger model handles difficult multi-source cases or second-pass verification.
3. **Large primary:** a 27B–31B model provides a material capability advantage worth the additional cost.
4. **Harness-limited:** neither compact nor large model performs adequately, indicating a need for better evidence, training tasks, retrieval, benchmark design, or architectural support.
5. **Frontier-only ceiling:** only a frontier model succeeds, which must be reported honestly while the open-model research track continues.

## 12. Locked decisions

1. No model family is selected before the project-specific bake-off.
2. Qwen3.5, Gemma 4, and Ministral 3 are the initial compact candidate families.
3. A 9B–12B model is not presumed sufficient.
4. The assistant is designed as a model-plus-tools system.
5. Gemma 4 12B receives a full compact bake-off.
6. Gemma 4 31B begins as an inference-only capacity comparator.
7. Qwen3.6-27B is treated as post-trained, not Base.
8. Any later official model release requires a fresh admission audit rather than automatic substitution.
9. Tiered compact/large inference is an acceptable final architecture.
10. The active project cap remains $3,500 with a $500 reserve.
11. The initial Gemma addition is planned at $300–$700.
12. Training a 31B model requires a separate approved capacity-value gate.

## 13. Deferred decisions

This supplement does not yet freeze:

- exact model revisions;
- tokenizer revisions;
- final candidate subset after Stage 1;
- exact benchmark formulas;
- precise adaptation token counts;
- training backend or hardware;
- final executable 31B promotion threshold;
- final main model or tiering policy;
- any billable campaign.

## 14. Approval statement

> **Biblical Scholar Lab will not presume that Qwen or any 9B-class model is best or sufficient. It will run a project-specific, evidence-gated comparison of Qwen3.5, Gemma 4, and Ministral 3 compact Base and product lineages, with Gemma 4 31B and Qwen3.6-27B serving as larger capacity comparators and a frontier model and human experts providing ceilings on selected cases. Gemma 4 12B will receive the full compact bake-off; Gemma 4 31B will initially remain inference-only. The initial Gemma addition is planned at $300–$700 within a $3,500 active project cap and $500 reserve. Final selection, 31B training, and model tiering will follow the approved benchmark and measured capability rather than reputation or recency.**
