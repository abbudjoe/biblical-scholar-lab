# DR-23 — Model and Training Harness Contract

| Field | Value |
|---|---|
| Design ID | `DR-23` |
| Status | `APPROVED` |
| Approval date | 2026-08-16 |
| Project owner | Joseph Abbud |
| Product, architecture, and experiment designer | ChatGPT |
| Independent implementation and evidence reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2 and supplements; DR-03; DR-04; DR-05; DR-06; DR-07; DR-08; DR-09; DR-10; DR-11; DR-12; DR-13; DR-14; DR-15; DR-16; DR-17; DR-18; DR-19; DR-20; DR-21; DR-22 |
| Implementation authority | GPT-5.6 Sol exclusively implements and repairs the approved model, data, training, checkpoint, telemetry, conversion, and conformance machinery |
| Execution authority | GPT-5.6 Luna may execute only frozen, reviewed training and evaluation jobs delegated by Sol through the approved run controller on Lambda Cloud; Luna may not modify code, data, configuration, objectives, models, thresholds, provider, artifact destination, or scientific interpretation |
| Approved cloud provider | Lambda.ai / Lambda Cloud is the sole approved external cloud execution provider for project training and evaluation; local owner-controlled development and evaluation remain permitted, and any other external cloud provider requires a new approved design |
| Canonical durable artifact storage | All non-Git checkpoints and generated training or evaluation artifacts must have their authoritative retained copy on the owner-controlled external storage volume attached to the MacBook Pro through Thunderbolt; Lambda-local storage is temporary execution scratch only |
| Approved change | Establishes the project-owned Training Core, canonical training objects and engine interface, deterministic reference engine, provisional native Transformers/FSDP2 and ms-swift production adapters, DeepSpeed and Megatron escalation paths, exact data and exposure contracts, packing and loss-mask semantics, component-update and precision policies, distributed execution identity, token-based scheduling, distributed checkpoint and model-export contracts, exact-resume and reproducibility tiers, training-time evaluation boundaries, observability and cost records, failure injection, backend conformance, security and rights controls, Lambda-only cloud execution, the owner-controlled Thunderbolt artifact archive, verified transfer and cleanup receipts, and the Sol-led/Luna-operated training workflow |

## 1. Purpose

DR-18 defines **which training stages may exist, why each stage exists, and what evidence is required to promote it**.

DR-23 defines **how an approved stage becomes an executable, resumable, inspectable, backend-portable training job without allowing a framework, trainer default, model implementation, or launch operator to change the experiment**.

A sound curriculum can still produce an invalid experiment if:

- The data order cannot be reconstructed;
- A streaming shuffle changes after resume;
- Packing crosses document boundaries without disclosure;
- Prompt, evidence, and response tokens receive the wrong loss mask;
- A supposedly frozen vision or language component receives gradients;
- One backend silently enables a different attention or DeltaNet kernel;
- A tokenizer, chat template, processor, or special-token map changes between runs;
- Effective batch size is reported in examples even though sequence lengths differ materially;
- Evaluation or checkpoint intervals are tied to steps in a way that makes models incomparable;
- A checkpoint omits optimizer, scheduler, RNG, sampler, packer, or exposure state;
- Resume begins from the same weights but not the same data position;
- An optimized backend changes outputs or loss relative to the reference path;
- A training framework silently truncates examples, inserts templates, masks losses, or selects modules;
- A failed run is “repaired” through an unrecorded live hyperparameter change;
- A monitoring service becomes the only record of metrics or uploads restricted material;
- The final checkpoint is selected from a private final benchmark;
- A run is described as reproducible merely because its config file was saved;
- Luna changes the experiment to keep a cloud job running;
- A job launches on an external cloud provider other than Lambda Cloud without a new approved design;
- A checkpoint or evaluation artifact exists only on ephemeral cloud storage when the instance terminates;
- A run silently falls back to the Mac internal disk or another location because the approved external Thunderbolt volume is unavailable;
- A cloud copy is deleted before its authoritative external-drive copy is cryptographically verified.

DR-23 is intended to prevent those failures.

It does **not** select final model-family winners, exact learning rates, data-mixture weights, sequence-length curricula, optimizer hyperparameters, Lambda instance types or regions, checkpoint intervals, transfer cadence, or the scientific outcome of any training stage. Those remain experiment-specific decisions under DR-24, DR-25, DR-28, approved campaign designs, ChatGPT review, and owner approval. The cloud-provider identity and canonical durable-storage destination are already fixed: Lambda Cloud is the sole approved external cloud execution provider, and the owner-controlled external volume attached to the MacBook Pro through Thunderbolt is the authoritative retained artifact archive.

## 2. Governing principle

> **Biblical Scholar Lab will own the semantic identity of every training job while adopting mature training libraries for ordinary tensor execution, distributed sharding, optimization, checkpoint I/O, and model-family support. A framework may execute an approved objective; it may not define the data, loss, trainable components, model identity, exposure order, checkpoint semantics, evaluation gate, retry policy, cloud provider, artifact destination, or scientific conclusion. Lambda Cloud will be the sole approved external cloud execution provider for project training and evaluation. All non-Git checkpoints and generated run artifacts will have their authoritative retained copy on the owner-controlled external volume attached to the MacBook Pro through Thunderbolt; Lambda-local disks are temporary scratch only. Every update must be reproducible as an immutable relation among an exact parent model, exact data and exposure plan, exact objective, exact component policy, exact numerical and distributed environment, exact archive and provider receipts, and exact resulting artifacts.**

The intended architecture is:

```text
approved TrainingStageSpecification
    → project-owned Training Core
    → immutable TrainingJobSpecification
    → project-owned data, objective, model, and checkpoint contracts
    → deterministic Reference Training Engine or approved production adapter
    → frozen Lambda Cloud execution plan or approved local reference plan
    → Sol-delegated Luna run through trainctl/campaignctl
    → canonical training events and exposure ledger
    → temporary atomic Lambda-local checkpoint and artifact staging
    → encrypted owner-initiated transfer to the external Thunderbolt archive
    → cryptographic and required load verification
    → authoritative archive receipt and Lambda cleanup receipt
    → resumable checkpoints and model-only evaluation artifacts
    → separately versioned checkpoint evaluation
    → project-owned TrainingResultBundle
    → ChatGPT code/evidence/scientific review
    → Joseph Abbud promotion, redesign, merge, budget, or stop decision
```

## 3. Project-owned Training Core

The project will implement a framework-neutral:

```text
TrainingCore
```

The Training Core owns:

- Validation of the approved design and stage identity;
- Compilation of data, model, objective, component, numerical, distributed, checkpoint, and evaluation contracts;
- Preflight checks;
- Generation of an immutable executable job specification;
- Backend selection only from owner-approved eligible adapters;
- Conversion of the canonical job into a backend projection;
- Verification that the backend projection preserves the canonical semantics;
- Canonical event, metric, exposure, checkpoint, and result records;
- Stop, resume, fork, export, and conversion semantics;
- Detection of any backend or runtime deviation;
- Production of a complete training result bundle;
- Validation that every cloud job uses the approved Lambda Cloud identity and campaign envelope;
- Validation of the external archive volume identity, capacity, rights state, transfer path, archive receipts, and required load checks;
- Refusal to promote or normally close a run whose required retained artifacts are not authoritatively archived.

The Training Core does **not** independently choose:

- Which experiment should be run;
- Which model should win;
- Which data should be admitted;
- Which loss objective should be preferred;
- Which hyperparameter values should be tried;
- Whether a regression is acceptable;
- Whether a checkpoint should be promoted.

Those remain explicit experiment-design decisions.

## 4. Canonical training objects

The implementation must preserve at least the following logical objects.

### 4.1 `TrainingProgram`

The complete approved multi-stage lineage described in DR-18.

It records:

```text
program identity
approved design IDs and hashes
lineages
stage graph
budget ceiling
protected benchmark and rights boundaries
owner approval state
```

### 4.2 `TrainingLineage`

A named immutable parent/child chain such as:

```text
PRODUCT_FIRST
CLEAN_BASE
LARGE_CAPACITY_COMPARATOR
MOBILE_STUDENT
ARCHITECTURE_EXTENSION
```

A lineage is never rewritten to make a later model appear to have a cleaner parent than it actually had.

### 4.3 `TrainingStageSpecification`

The scientific contract approved under DR-18 and an individual experiment design:

```text
capability hypothesis
immutable parent checkpoint
admitted corpus and mixture
objective suite
component update policy
replay and preservation plan
evaluation schedule
stop and promotion contract
budget envelope
```

### 4.4 `TrainingJobSpecification`

The fully executable frozen job:

```text
stage identity
model artifact bundle
processor and tokenizer
materialized dataset and exposure program
objective and loss contract
trainable component manifest
precision and kernel policy
distributed execution plan
optimizer and scheduler
batch and token accounting
checkpoint policy
training-time evaluation policy
failure and stop policy
container and dependency identity
artifact destinations and authoritative external-archive binding
Lambda Cloud provider, region, instance, image, API, and scratch-storage identity
artifact transfer, durability, retention, and cleanup policy
security and telemetry policy
content hash
```

Changing any consequential field creates a new job ID.

### 4.5 `ModelTrainingBundle`

Extends DR-11’s model identity with training-specific state:

```text
parent weight hashes
architecture and config
processor/tokenizer/template/special tokens
trainable component names
frozen component names
tied-parameter relationships
MTP or auxiliary components
modality pathways
parameter count by component and dtype
model implementation revision
custom-code and trust-remote-code state
license and lineage
```

### 4.6 `DataMaterializationManifest`

Identifies the exact model-specific input records generated from DR-17:

```text
corpus and graph snapshots
mixture revision
tokenizer and processor
example IDs
source and rights handles
content hashes
text and modality views
loss-label fields
truncation/splitting decisions
packing eligibility
overlap and holdout exclusions
```

### 4.7 `SamplingProgram` and `SampleCursor`

Together define and record the exact exposure order without requiring one enormous static file of every sample position.

They bind:

```text
hierarchical sampler and weights
random algorithm and seed
shard ordering
within-shard ordering
replacement policy
curriculum phase
epoch or token phase
rank assignment
worker assignment
shuffle state
current cursor
```

### 4.8 `PackedSequencePlan`

Records exactly which examples and spans entered each packed sequence, their order, their token ranges, document boundaries, attention boundaries, loss masks, and discarded padding.

### 4.9 `TrainingObjectiveSpecification`

Defines every loss term, target, mask, weight, reduction, normalization, label source, and schedule.

### 4.10 `ComponentUpdatePolicy`

Defines every trainable, frozen, adapter, auxiliary, modality, embedding, output, normalization, routing, and learning-rate group.

### 4.11 `PrecisionKernelPolicy`

Defines dtypes, accumulators, optimizer states, TF32, autocast, gradient scaling, attention implementation, DeltaNet or other specialized kernels, compilation, activation checkpointing, and fallback rules.

### 4.12 `DistributedExecutionPlan`

Defines topology, world size, data/tensor/pipeline/context/expert parallelism, FSDP or ZeRO policy, gradient accumulation, communication settings, and checkpoint topology.

### 4.13 `CheckpointPolicy`

Defines resumable, evaluation, milestone, export, retention, atomicity, and preemption behavior.

### 4.14 `TrainingRun`

The actual attempted execution, including every event, deviation, failure, retry, checkpoint, and cost.

### 4.15 `TrainingResultBundle`

The canonical result containing:

```text
job and run identity
complete requested and actual exposure
loss and metric histories
checkpoint inventory
failure and stop reasons
resume history
resource and cost accounting
kernel and backend path
training-time evaluations
selected and rejected checkpoint recommendations
public-safe projection
content hash
```

A framework’s directory or dashboard is never the complete result bundle by itself.

### 4.16 `ExternalArtifactStoreProfile`

Defines the authoritative retained store for every non-Git training and evaluation artifact. The initial approved store is the owner-controlled external storage volume attached to the MacBook Pro through Thunderbolt. The mount path is operational metadata rather than identity.

The profile records:

```text
stable macOS volume UUID or equivalent device identity
approved physical device identity
current mount point
Thunderbolt attachment state where exposed by the operating system
filesystem, case-sensitivity, and health state
encryption and access-control state
owner and authorized process identity
project root
writable-state test
capacity, free-space floor, and reserve
allowed rights and artifact lineages
retention and backup status
last verification time
```

No authoritative artifact path may resolve to the Mac internal disk, the Git repository, a temporary directory, a persistent cloud filesystem, or another removable or network volume.

### 4.17 `ArtifactArchiveReceipt`

Binds every retained checkpoint or artifact to:

```text
artifact and run identity
Lambda source instance and scratch path
external archive profile and final path
byte count and chunk inventory
cryptographic hashes
transfer protocol and encryption state
start and completion times
structural and load validation
archive promotion result
cloud deletion eligibility and deletion result
content hash
```

A cloud-local artifact is not durable, promotable, or safe to rely on merely because its write completed.

### 4.18 `LambdaExecutionProfile`

Every cloud training or evaluation job binds:

```text
Lambda workspace and account identity
Lambda API or CLI revision
region and instance type
GPU and host topology
base image and container digest
local and attached scratch storage
network and credential identity
observed price and billing unit
maximum cost and runtime
launch, stop, and termination policy
artifact-transfer route
maximum unsynchronized artifact window
provider cleanup result
```

Local owner-controlled reference tests and bounded local evaluations remain permitted. A hosted model API may be an evaluation subject under DR-22, but it is not an alternate self-hosted training or evaluation infrastructure provider.

## 5. We will not build a full tensor-training framework from scratch

The project will own experiment semantics and artifact identity, but it will adopt mature libraries for:

- Model implementations;
- Automatic differentiation;
- Optimizers;
- Mixed precision;
- Distributed sharding and communication;
- Checkpoint I/O;
- PEFT adapters;
- SFT and offline preference objectives;
- Supported model-family processors and templates.

The project will not reimplement CUDA collectives, AdamW, FSDP, ZeRO, tensor parallelism, tokenizers, or ordinary transformer training loops merely to avoid dependencies.

The architecture is therefore:

```text
strict project-owned orchestration and evidence layer
    over
mature, pinned, replaceable training backends
```

## 6. Required training-engine interface

Every backend adapter implements a project-owned logical interface resembling:

```text
TrainingEngine
  capabilities()
  validate(job_spec)
  compile(job_spec)
  preflight(execution_plan)
  run(execution_plan)
  interrupt(run_id, reason)
  resume(checkpoint_id, execution_plan)
  inspect(run_id)
  export(checkpoint_id, export_spec)
  verify_export(source, derivative)
  close(run_id)
```

The interface must expose, not hide:

- Which trainer and objective implementation are active;
- Which model modules are trainable;
- Which data collator and packing path are active;
- Which distributed strategy is active;
- Which checkpoint implementation is active;
- Which optimized kernels are active or unavailable;
- Which framework defaults were overridden;
- Which unsupported features caused a fallback.

A backend that cannot expose these facts is ineligible for an authoritative run.

## 7. Deterministic Reference Training Engine

The project will implement a small:

```text
ReferenceTrainingEngine
```

Its purpose is conformance—not production performance.

It will support:

- A tiny deterministic causal language model or tiny public test checkpoint;
- Single-process CPU and, where available, single-GPU execution;
- Small fixed datasets;
- CPT and SFT loss contracts;
- Simple adapter and preference fixtures where feasible;
- Exact sample schedules and packing;
- Checkpoint interruption and resume;
- Known-gradient and known-loss fixtures;
- Model-only export;
- Canonical event, exposure, and result generation.

The reference engine provides the semantic oracle against which production adapters are tested.

It does not need to be fast or support a 9B model.

## 8. Provisional production backend strategy

No one backend is presumed best for every family and stage.

### 8.1 `NativeTransformersFSDP2Engine` — preferred low-level compact reference

The first production candidate will use:

```text
PyTorch
+ Transformers model implementations
+ Accelerate or project-owned launch integration
+ PyTorch FSDP2 for compact full-parameter distributed training
+ torch.distributed.checkpoint for resumable state
+ PEFT for adapters
+ TRL objective implementations where they pass conformance
```

PyTorch FSDP2 uses per-parameter sharding and is the preferred first sharding primitive for 8B–12B compact full-parameter experiments. PyTorch Distributed Checkpoint supports parallel save/load and load-time resharding, making it suitable for resumable distributed state when validated for the selected model and topology.[^fsdp2] [^dcp]

Hugging Face Accelerate may supply launch and FSDP integration, but its configuration remains a backend projection of our `DistributedExecutionPlan`, not the authoritative experiment record.[^accelerate]

### 8.2 `MSSwiftEngine` — preferred broad model/multimodal compatibility candidate

The second production candidate will wrap a pinned ms-swift release or exact commit.

ms-swift currently advertises:

- CPT, SFT, DPO, SimPO, KTO, ORPO, and other objectives;
- Full-parameter, LoRA, and QLoRA training;
- FSDP/FSDP2, DeepSpeed, and Megatron paths;
- Text and multimodal training;
- Model-family support including Qwen3.5 and Gemma 4 classes;
- Independent control of multimodal components;
- Quantization and deployment utilities.[^msswift]

Those capabilities make it a serious implementation candidate, especially for model-specific templates and multimodal preservation. They do not authorize its defaults as project semantics.

The ms-swift adapter must expose and validate:

- Exact encoded examples;
- Template and processor bytes;
- Packing behavior;
- Loss masks;
- Trainable modules;
- Objective implementation;
- Distributed configuration;
- Checkpoint completeness;
- Kernel and precision paths.

### 8.3 `DeepSpeedEngine` — fallback and memory-pressure adapter

DeepSpeed ZeRO-3 shards parameters, gradients, and optimizer state and may be used when FSDP2 or a family-specific implementation cannot satisfy memory or compatibility requirements.[^deepspeed]

It remains a separate backend condition. A ZeRO checkpoint, consolidated model, and resumed training state have different semantics and must pass the same conformance and export checks.

CPU or NVMe offload is not a free optimization. It changes performance, failure modes, storage traffic, and cost and therefore requires an explicit execution plan.

### 8.4 `MegatronSwiftEngine` or `MegatronCoreEngine` — scale-gated

Megatron-style tensor, pipeline, context, and expert parallelism becomes eligible when:

- A 27B–31B or MoE adaptation is separately approved;
- Compact FSDP2/ZeRO paths are insufficient;
- Long-sequence or multimodal training requires additional parallelism;
- A measured throughput or memory result justifies the increased complexity.

Megatron Core supplies composable TP, PP, DP, EP, CP, mixed precision, and optimized building blocks; ms-swift also exposes Megatron-SWIFT support for CPT, SFT, DPO, and multimodal training.[^megatron] [^megatron-swift]

This path is not part of the first mandatory compact-model training run.

### 8.5 TorchTitan — reference and future adapter, not initial production dependency

TorchTitan is a useful PyTorch-native reference for FSDP2, TP, PP, CP, activation checkpointing, distributed checkpointing, float8, checkpointable data loading, structured logs, and profiling. Its current repository also describes it as under extensive development and supports a narrower set of models out of the box.[^torchtitan]

The project may borrow design patterns or add a later adapter. TorchTitan will not become the initial constitutional harness or require nightly PyTorch unless a separate spike demonstrates decisive value.

### 8.6 Lambda Cloud — sole approved external execution provider

All billable external GPU training and evaluation infrastructure will run on Lambda.ai / Lambda Cloud. Local owner-controlled development, deterministic fixtures, and bounded local evaluation remain permitted. No automatic or operator-selected failover to AWS, Google Cloud, Azure, CoreWeave, RunPod, Vast.ai, or another infrastructure provider is authorized.

Every cloud adapter must expose:

```text
provider and API identity
region and instance type
GPU and host topology
image and boot identity
working-storage identity
network and access policy
observed price and cost cap
launch, lifecycle, and termination events
artifact archive state
provider-side cleanup result
```

If Lambda lacks the approved capacity, region, price, network path, or technical support, the run stops with:

```text
BLOCKED_REQUIRES_CLOUD_EXECUTION_DESIGN_REVIEW
```

Sol may propose a Lambda configuration change or another provider. It may not implement or use an alternative until ChatGPT designs the amendment and Joseph approves it. Lambda filesystems may be used only as temporary separately approved working storage and never as the authoritative retained archive.

## 9. Backend selection requires a conformance spike

Before any production backend is promoted, Sol must implement a bounded comparison using the same approved job specification.

The initial spike should test at least:

```text
ReferenceTrainingEngine
NativeTransformersFSDP2Engine
MSSwiftEngine
```

DeepSpeed is added when needed for memory or compatibility; Megatron is added only after a scale gate.

The spike must compare:

- Exact encoded samples;
- Exact loss-bearing tokens;
- Initial loss on fixed batches;
- Gradient presence and freeze behavior;
- Short loss trajectory;
- Optimizer and scheduler state;
- Checkpoint completeness;
- Interrupted versus uninterrupted continuation;
- Exposure ledger identity;
- Model-only export and inference equivalence;
- Structured and multimodal data where relevant;
- Throughput, memory, startup, checkpoint time, and engineering complexity;
- Active kernels and fallbacks.

A backend may be selected separately by model family and training stage.

Framework uniformity is desirable, but it may not override correctness, model support, or scientific auditability.

## 10. Immutable data and exposure contract

Training reads only an approved `ModelMaterialization` from DR-17.

The training harness may not:

- Discover new files by walking a directory;
- Download a replacement dataset during a run;
- Re-tokenize from an unpinned tokenizer;
- Add web data;
- Skip malformed examples silently;
- Change source eligibility;
- Read benchmark holdouts;
- Allow provider-native data mixing.

Every accepted example has an immutable ID and source lineage.

Every rejected example receives a recorded reason.

## 11. Exact sampling and resume semantics

The project requires exact exposure accounting.

A generic streaming iterator with a finite shuffle buffer is insufficient for an authoritative exact-resume claim unless the complete buffer state is checkpointed. Hugging Face Datasets documents that streaming resume can recover the dataset position but loses shuffled examples held in the shuffle buffer when resuming, after which the buffer is refilled.[^hf-stream]

Accordingly, the project will use one of these approved strategies:

1. **Precomputed schedule:** exact example or shard schedule materialized before launch;
2. **Counter-based deterministic schedule:** sample identity reconstructed from immutable counters, seeds, and rank assignment;
3. **Fully checkpointed streaming state:** including every shuffle buffer and worker cursor;
4. **Declared approximate resume:** permitted only for a nonauthoritative smoke run and labeled accordingly.

Authoritative runs require strategies 1–3.

The `SampleCursor` must survive:

- Process interruption;
- Worker restart;
- Checkpoint resume;
- Node replacement;
- Approved world-size change, if the backend claims resharded resume.

The exposure ledger records what was actually consumed, not merely what was planned.

## 12. Packing is a scientific contract

Packing can alter the context seen by the model and therefore is not a backend-only optimization.

Every packed sequence records:

```text
member example IDs
source and passage scopes
token offsets
special tokens
document boundaries
attention boundary policy
position IDs
loss mask
modality positions
truncation or padding
```

Approved attention-boundary modes include:

```text
BLOCK_DIAGONAL_BETWEEN_UNRELATED_DOCUMENTS
ALLOW_CROSS_DOCUMENT_WITHIN_APPROVED_UNIT
CONTIGUOUS_SAME_WORK_OR_PASSAGE
MODEL_NATIVE_MULTIMODAL_PACKING
```

Cross-document attention between unrelated sources is not silently permitted merely because a trainer’s packer concatenates examples.

### No silent truncation

Every overlength record must be:

- Rejected with a reason;
- Split under an approved semantic-boundary policy;
- Routed to a longer-context stage;
- Or included under an explicitly approved truncation contract.

The project records which text, annotation, image region, or answer content was omitted.

## 13. Token and exposure accounting

Every run distinguishes:

```text
raw source tokens
encoded input tokens
loss-bearing tokens
prompt/context tokens
answer tokens
tool and schema tokens
special tokens
padding tokens
modality tokens
replay tokens
unique source tokens
repeated exposure tokens
```

The primary training-progress clock is normally:

```text
loss-bearing tokens processed
```

unless an experiment explicitly selects another clock.

Learning-rate schedules, validation intervals, checkpoint intervals, and stage budgets should be expressed in tokens where feasible rather than optimizer steps alone.

This allows comparisons across:

- Variable sequence lengths;
- Different packing efficiency;
- Different gradient accumulation;
- Different model-family tokenizers;
- Content-matched and compute-matched conditions.

## 14. Objective contracts

A framework may not infer the loss from the dataset format.

Every objective explicitly defines:

- Input fields;
- Target fields;
- Loss-bearing spans;
- Ignored spans;
- Reduction;
- Per-token, per-example, per-domain, or per-objective weights;
- Label smoothing;
- Auxiliary losses;
- Modality losses;
- Normalization across variable sequence lengths;
- Invalid-example behavior.

### 14.1 Causal continued pretraining

The baseline CPT objective is causal next-token prediction.

It must declare:

- Document boundaries;
- Whether boundary tokens receive loss;
- Whether unrelated documents attend to one another;
- How source metadata is represented;
- How image or multimodal tokens are handled;
- Whether any MTP or auxiliary loss is active;
- How replay and domain tokens are weighted.

### 14.2 Scholarly SFT

SFT must declare whether loss applies to:

- Assistant answer tokens;
- Structured claim and evidence fields;
- Tool calls;
- Tool results;
- System instructions;
- Retrieved evidence;
- User text;
- Reasoning summaries;
- Citations and locators.

The default is that evidence, system policy, tool results, and user text provide context but do not receive answer-generation loss unless an approved task explicitly trains reconstruction or transformation.

### 14.3 Retrieval- and tool-aware SFT

Tool and retrieval trajectories must distinguish:

- Model-proposed tool calls;
- Deterministic tool results;
- Gold tool actions;
- Distractor evidence;
- Missing-evidence outcomes;
- Rehydration events;
- Final answer spans.

The model is not trained to reproduce arbitrary retrieved text as though it were its own answer.

### 14.4 Preference objectives

DPO, SimPO, KTO, ORPO, or another approved objective must implement DR-19’s exact pair, tie, unary, condition, reference-model, length-normalization, and adapter contracts.

Trainer defaults cannot silently redefine the preference objective.

### 14.5 Translation Nuance and auxiliary objectives

A1 structured generative tasks may run on the unchanged model architecture.

Any A2 auxiliary head or later component must cite the approved DR-12 extension design and declare its loss, layer tap, gradient path, runtime disposition, and rollback behavior.

## 15. Component update and freeze contract

Every run produces a machine-readable `TrainableParameterManifest` containing:

```text
parameter name
component identity
shape
dtype
parameter count
requires_grad state
optimizer group
learning rate and weight decay
adapter or full-parameter role
parent hash where applicable
```

Preflight checks verify:

- The intended parameters are trainable;
- The intended parameters are frozen;
- Tied weights remain correctly tied;
- LoRA targets match exact module identities;
- The vision encoder, projector, unified decoder, MTP head, embeddings, norms, and output head have the approved state;
- No unexpected parameter was added or omitted.

During training, the harness may sample or fully audit:

- Gradient presence;
- Parameter deltas;
- Frozen-parameter immutability;
- Adapter isolation;
- Modality component drift.

A trainer’s `target_modules=all-linear` convenience setting cannot substitute for an approved exact component manifest.

## 16. Precision and numerical policy

### 16.1 Scientific reference precision

The provisional high-precision training reference for supported H100/B200-class hardware is:

```text
BF16 model computation
with explicitly declared accumulation and optimizer-state precision
```

Exact optimizer-state dtype remains stage-specific and must be recorded.

FP32 is used for small reference fixtures where feasible.

### 16.2 Separately gated precision paths

These are separate experimental conditions:

```text
FP16
TF32 changes
FP8
MXFP8
FP4 or other sub-8-bit training
8-bit or paged optimizers
QLoRA or quantized-base training
BF16 optimizer-state experiments
```

They may improve efficiency but cannot silently replace the scientific reference.

### 16.3 Kernel identity

Every run records:

- Attention implementation;
- Qwen DeltaNet kernel or fallback;
- FlashAttention version;
- SDPA backend;
- Liger or Triton kernels;
- `torch.compile` and compiler settings;
- Activation-checkpointing implementation;
- Fused optimizer;
- MTP path;
- Any custom extension.

A silent fallback from an optimized path is a reportable event and may be a stop condition when it changes cost, memory, or numerics materially.

Custom kernels remain governed by DR-06 and DR-12: they may optimize an approved operation only after profiling and equivalence validation.

## 17. Distributed execution policy

The project distinguishes:

```text
DATA_PARALLEL
FSDP2
DEEPSPEED_ZERO_2
DEEPSPEED_ZERO_3
TENSOR_PARALLEL
PIPELINE_PARALLEL
CONTEXT_PARALLEL
EXPERT_PARALLEL
HYBRID_PARALLEL
```

Every execution plan records:

- Node and GPU topology;
- Rank mapping;
- Device mesh;
- Sharding and wrapping plan;
- Activation checkpointing;
- Gradient accumulation;
- Microbatch and global batch;
- Effective loss-bearing tokens per optimizer update;
- Collective and overlap settings;
- Communication library and environment;
- Failure and elastic-resume policy.

Changing world size, parallelism, batch, or accumulation is not an invisible operational change.

It creates either:

- A validated compatible resume under the same job;
- A resharded-resume event;
- Or a new job/fork identity.

## 18. Optimizer and scheduler contract

The exact optimizer and scheduler belong to each experiment design, not to an unreviewed framework default.

The harness must record:

```text
optimizer type and implementation
all optimizer hyperparameters
parameter groups
weight-decay exclusions
scheduler type
warmup and decay clocks
minimum learning rate
gradient clipping
gradient accumulation
loss scaling
zeroing behavior
update skipping
```

AdamW may serve as a reference optimizer in initial compact experiments, but DR-23 does not declare it universally superior.

An optimizer or scheduler change creates a new job identity.

Dynamic responses such as reducing the learning rate after divergence, changing batch size after OOM, or increasing warmup during a live run are prohibited. Sol may implement a reviewed repair; Luna may not improvise it.

## 19. Checkpoint architecture

### 19.1 Resumable distributed checkpoint

The canonical resumable checkpoint should use a distributed state format capable of preserving the sharded model and optimizer state. PyTorch Distributed Checkpoint is the preferred first substrate for FSDP2 and compatible PyTorch-native runs because it supports parallel save/load and load-time resharding.[^dcp]

A resumable checkpoint must include:

```text
model state
optimizer state
scheduler state
gradient scaler or numerical state
RNG state for every relevant generator and rank
sampler and data cursor
shuffle buffers where applicable
packer state
exposure ledger cursor
gradient-accumulation position
objective and curriculum phase
trainable component state
runtime and kernel identity
checkpoint policy and manifest
```

### 19.2 Model-only evaluation checkpoint

A separate model-only artifact is exported for evaluation and inference.

The preferred tensor format is `safetensors`, which is designed as a non-pickle, fast tensor-storage format.[^safetensors]

The model-only artifact includes:

- Model or adapter weights;
- Config;
- Tokenizer and processor;
- Chat template and special-token map;
- Generation defaults only as metadata;
- Lineage and rights manifest;
- Export/conversion report.

It is not sufficient for training resume.

### 19.3 Adapter-only artifact

LoRA or another PEFT adapter remains a separate scientific master by default.

A merged model is a new derivative and must pass parent-plus-adapter equivalence testing.

### 19.4 Atomicity

A checkpoint is not considered valid until:

- Every rank or writer completes;
- The manifest is written;
- Checksums pass;
- The complete marker is present;
- A load validation succeeds or is scheduled according to policy.

Interrupted or partial checkpoints remain marked incomplete and cannot be selected automatically.

### 19.5 Preemption handling

The harness should support a bounded preemption signal path that finishes the current safe boundary and writes a checkpoint when the available grace period allows it.

Current Transformers documentation includes just-in-time checkpointing on `SIGTERM`, but the project must still verify completeness and allow enough grace time rather than trusting a directory’s existence.[^trainer-jit]

### 19.6 Authoritative external artifact archive

All non-Git checkpoints and generated training or evaluation artifacts have one authoritative retained home:

```text
OWNER_EXTERNAL_THUNDERBOLT_ARCHIVE
```

The archive is the owner-controlled external MacBook Pro storage volume connected through Thunderbolt. The system binds it by stable volume and device identity, not only by a familiar mount name. It contains resumable and model-only checkpoints, adapters and derivatives, optimizer and scheduler state, exposure ledgers, training and evaluation result bundles, canonical logs and profiles, corpus materializations and indexes used by campaigns, conversion reports, rights and lineage manifests, and archive and deletion receipts.

Small public-safe summaries, manifests, hashes, or release projections may later be committed to Git. The external archive remains their canonical generated-artifact origin.

### 19.7 External-drive preflight and no-fallback policy

Before any cloud campaign launches, preflight must verify:

1. The approved volume UUID and device identity;
2. Thunderbolt-connected availability where the OS exposes transport identity;
3. Read/write access under the approved owner or service identity;
4. Filesystem health;
5. Sufficient free space for retained artifacts, transfer staging, verification overhead, and safety reserve;
6. Required encryption and access controls for the involved rights lineages;
7. Atomic create, write, hash, rename, and delete fixture operations;
8. No symlink or path traversal from the project root onto the internal disk.

The transfer `.incoming` area resides on the external volume. The Mac internal disk may hold only unavoidable bounded operating-system metadata; it may not be used as a checkpoint or artifact cache. If the external archive is unavailable, mismatched, unwritable, full, unhealthy, or under the wrong rights/encryption state, launch fails closed.

### 19.8 Lambda scratch, transfer, and archival protocol

Lambda instance storage is temporary run-local scratch. Artifacts transition through states such as:

```text
CLOUD_WRITING
CLOUD_COMPLETE_UNVERIFIED
LOCAL_TRANSFER_IN_PROGRESS
LOCAL_BYTES_COMPLETE
LOCAL_HASH_VERIFIED
LOCAL_LOAD_VALIDATED
ARCHIVED_AUTHORITATIVE
CLOUD_DELETE_ELIGIBLE
CLOUD_DELETED_VERIFIED
ARCHIVE_FAILED
```

The protocol is:

1. Lambda writes an atomic artifact and complete manifest;
2. The artifact is hashed and marked structurally complete on scratch;
3. An owner-controlled process pulls it directly into the external archive `.incoming` area over an authenticated encrypted channel;
4. Byte count, manifest, and hashes are verified locally;
5. Checkpoints receive the required structural or load validation;
6. The artifact is atomically promoted into its final content-addressed path;
7. An immutable `ArtifactArchiveReceipt` is recorded;
8. Only then may the cloud copy become deletion-eligible.

The preferred security posture is owner-initiated pull rather than exposing the external volume as a public network filesystem.

The campaign reserves cost and wall-clock headroom for final checkpointing, transfer, validation, and termination. If archival cannot complete before the immutable safety or cost deadline, the controller terminates Lambda at the cap, marks the run:

```text
ARTIFACT_ARCHIVE_INCOMPLETE
RUN_NOT_PROMOTABLE
```

and preserves the available failure and inventory record. Missing archival receipts prohibit stage completion, checkpoint promotion, or public result claims.

### 19.9 Retention and deletion

The external archive uses owner-approved retention classes:

```text
RETAIN_PERMANENT
RETAIN_UNTIL_STAGE_DECISION
RETAIN_UNTIL_SUCCESSOR_VERIFIED
RETAIN_FOR_REPRODUCTION_WINDOW
DELETE_AFTER_ARCHIVE_VERIFICATION
DELETE_ONLY_WITH_OWNER_APPROVAL
```

No automated cleanup may delete the last validated resumable checkpoint, selected model artifact, result bundle, rights/lineage manifest, or source required to reproduce a published claim. External deletion and cloud scratch deletion each create immutable receipts. A later owner-approved secondary local backup may be added, but its absence does not authorize use of the internal disk or another cloud as the canonical store.

## 20. Resume, continuation, and fork are different

DR-23 defines:

```text
EXACT_RESUME
    same job semantics and validated same-environment continuation

RESHARDED_RESUME
    same approved job with validated topology or sharding change

COMPATIBLE_BACKEND_RESUME
    same job semantics through a separately validated backend conversion

WEIGHTS_ONLY_CONTINUATION
    new job using weights but not full optimizer/data state

FORK_FROM_CHECKPOINT
    new experiment lineage from an intermediate checkpoint

RESTART_FROM_PARENT
    new run from the original parent
```

Only the first three may be described as resume.

A weights-only continuation resets optimizer, schedule, exposure, or other state and therefore is a new job.

## 21. Reproducibility tiers

PyTorch explicitly warns that complete reproducibility is not guaranteed across releases, commits, platforms, or CPU/GPU execution even with identical seeds.[^pytorch-repro]

The project will therefore use explicit tiers rather than claiming universal determinism.

### `REP-T0_COMPLETE_IDENTITY`

Every model, data, config, code, environment, hardware, kernel, and artifact identity is recorded.

### `REP-T1_REFERENCE_BITWISE`

Tiny reference fixtures reproduce bitwise under the same pinned environment where supported.

### `REP-T2_SAME_ENVIRONMENT_RESUME_EQUIVALENT`

Interrupted and uninterrupted runs match within a preregistered numerical and loss tolerance under the same environment.

### `REP-T3_SAME_ENVIRONMENT_REPEAT_STATISTICAL`

Independent seeds or repeated runs show expected metric and checkpoint variation within declared bounds.

### `REP-T4_CROSS_TOPOLOGY_OR_BACKEND_SEMANTIC_EQUIVALENCE`

A resharded or backend-converted run preserves the approved loss and behavior contract within declared tolerance.

No result receives a stronger reproducibility label than its evidence supports.

## 22. Randomness contract

The harness records and controls, where applicable:

- Python RNG;
- NumPy RNG;
- PyTorch CPU RNG;
- Every CUDA device RNG;
- Data-sampler RNG;
- Packing RNG;
- Augmentation RNG;
- Dropout;
- Multimodal perturbation;
- Candidate-response generation;
- Distributed rank seeding.

The determinism mode, cuDNN benchmarking, deterministic algorithms, compiler autotuning, and relevant environment variables are explicit.

Deterministic operation modes may reduce performance and are not automatically used for every production run, but they are mandatory for selected reference and debugging fixtures.[^pytorch-deterministic]

## 23. Training-time evaluation boundaries

Training-time evaluation may use:

- Validation loss on a rights-approved held-out corpus;
- Public development benchmark cases;
- Private development audit cases under explicit access control;
- Parent-relative preservation suites;
- Data, kernel, and checkpoint conformance tests.

It may not use:

- `PRIVATE_FINAL` for checkpoint selection;
- Unused fresh challenge cases;
- Specialist cases unavailable to the authorized training environment;
- A public leaderboard as an adaptive training signal.

A checkpoint evaluation binds the exact exported checkpoint and scorer revision.

Asynchronous evaluation is permitted only when it cannot mutate the active training job and when its checkpoint identity is exact.

The harness will not use a single `load_best_model_at_end` scalar as the final scientific selection rule. Checkpoint selection is a separate multi-objective DR-18/DR-24 decision.

## 24. Canonical observability

The project will produce canonical owner-controlled records independent of any commercial telemetry service. Their authoritative retained copy is stored on the external Thunderbolt archive. Lambda-local and dashboard copies are operational mirrors only.

At minimum, it records:

### Training state

```text
loss by objective and domain
learning rate
gradient norm
clipping and skipped updates
optimizer state indicators
NaN/Inf and overflow events
```

### Data and exposure

```text
examples and tokens consumed
language and corpus role
work, edition, and translation family
passage and overlap cluster
replay class
sequence length and packing efficiency
actual versus planned exposure
```

### Performance

```text
tokens/sec and loss-bearing tokens/sec
step and data-loader time
GPU utilization
memory allocated/reserved and peak memory
TFLOPs/MFU where valid
communication and checkpoint time
kernel path and compile time
```

### Operations and cost

```text
hardware and topology
wall time
GPU time
Lambda workspace, region, instance type, instance ID, image, API revision, and lifecycle state
provider-billed cost and credit impact
Lambda scratch inventory and artifact-transfer state
external archive volume identity, free-space state, and archive-receipt IDs
retries, pauses, resumes, and failures
```

PyTorch provides profiler and CUDA-memory snapshot tooling that may assist in diagnosing operator time and allocator behavior; third-party allocations such as NCCL may require separate accounting.[^pytorch-profiler] [^pytorch-memory]

TensorBoard, Weights & Biases, Trackio, or another dashboard may mirror approved public-safe metrics. They are not the canonical record, and remote telemetry is disabled for restricted or private data unless specifically authorized.

Source text, private prompts, private benchmark gold, and restricted evidence must not leak into logs or telemetry.

## 25. Failure detection and stop behavior

The harness must detect and classify at least:

```text
NONFINITE_LOSS
NONFINITE_GRADIENT
LOSS_DIVERGENCE
UNEXPECTED_LOSS_DISCONTINUITY
GRADIENT_EXPLOSION_OR_COLLAPSE
FROZEN_PARAMETER_CHANGED
EXPECTED_PARAMETER_NOT_UPDATED
DATA_EXPOSURE_MISMATCH
DATA_EXHAUSTION
HOLDOUT_OR_RIGHTS_VIOLATION
PACKING_OR_MASK_DEFECT
KERNEL_FALLBACK
OUT_OF_MEMORY
DISTRIBUTED_HANG_OR_RANK_LOSS
CHECKPOINT_FAILURE_OR_CORRUPTION
EXTERNAL_ARCHIVE_UNAVAILABLE
EXTERNAL_ARCHIVE_IDENTITY_MISMATCH
EXTERNAL_ARCHIVE_INSUFFICIENT_SPACE
EXTERNAL_ARCHIVE_RIGHTS_OR_ENCRYPTION
ARTIFACT_TRANSFER_FAILURE
ARTIFACT_HASH_OR_LOAD_MISMATCH
LAMBDA_PROVIDER_OR_INSTANCE_MISMATCH
LAMBDA_CAPACITY_OR_REGION_BLOCK
LAMBDA_CLEANUP_FAILURE
UNAPPROVED_CLOUD_PROVIDER
RESUME_MISMATCH
EVALUATION_REGRESSION
COST_OR_RUNTIME_CAP
USER_OR_OWNER_STOP
```

The approved policy determines whether an event:

- Warns;
- Pauses;
- Saves a checkpoint;
- Stops the job;
- Blocks resume;
- Requires a Sol repair;
- Requires a new experiment design.

A framework’s automatic retry cannot change batch size, precision, optimizer, sequence length, data, model, or objective.

## 26. Failure injection and resume validation

Before a backend runs an expensive campaign, Sol must test:

- Graceful interruption;
- Abrupt worker loss where feasible;
- Partial checkpoint write;
- Corrupt checkpoint file;
- Lost or delayed data worker;
- Rank mismatch;
- Out-of-memory preflight or controlled failure;
- Nonfinite loss;
- Watchdog stop;
- Exact resume;
- Resharded resume where claimed;
- Model-only export and reload;
- Frozen-parameter enforcement;
- Exposure-ledger continuation;
- External-volume disconnect and reconnect;
- Wrong or spoofed volume identity;
- Low-space and rights/encryption preflight failure;
- Interrupted and resumed archive transfer;
- Local hash mismatch and checkpoint load-test failure;
- Lambda termination before archival completion;
- Lambda lifecycle or scratch-cleanup failure;
- Attempted launch on an unapproved cloud provider.

The production path is not approved merely because a happy-path smoke run completes.

## 27. Engine conformance and promotion gate

A production training engine is promoted only if it demonstrates:

1. Canonical job-spec validation;
2. Exact data and loss semantics;
3. Trainable/frozen parameter correctness;
4. Reference-batch loss and gradient compatibility;
5. Complete checkpoint and resume behavior;
6. Correct exposure ledger;
7. Correct model-only and adapter export;
8. Family-specific multimodal handling;
9. Kernel and precision transparency;
10. Failure injection and cleanup;
11. Acceptable throughput, memory, checkpoint time, and cost;
12. Pinned reproducible environment;
13. Public/private rights compliance;
14. Sol reviewable implementation and evidence;
15. Verified external-archive transfer, receipt, and restore behavior;
16. Lambda provider, lifecycle, billing, and cleanup conformance;
17. ChatGPT review and owner approval.

A faster backend that hides or changes semantics does not win.

## 28. Training security, privacy, and rights

Training jobs must:

- Read only approved source and artifact zones;
- Remain unable to access private final or fresh benchmark content;
- Avoid unapproved outbound network access;
- Use scoped credentials;
- Mount secrets outside Git and model artifacts;
- Avoid serializing secrets or source text into logs;
- Preserve rights and lineage in every checkpoint and export;
- Prevent public telemetry from receiving restricted data;
- Use Lambda Cloud as the only approved external cloud execution provider;
- Treat Lambda instance and attached disks as temporary scratch;
- Transfer retained artifacts only through an authenticated encrypted channel to the approved external archive;
- Verify destination volume identity, rights/encryption state, capacity, hashes, and required load tests;
- Prevent Lambda filesystems, another cloud, or the Mac internal disk from becoming the authoritative archive;
- Verify Lambda scratch cleanup and provider-side termination after archival;
- Record software bills of materials and container digests;
- Scan model and dataset loaders for unsafe remote code or archives.

`trust_remote_code` and model custom code are explicit model-bundle decisions, never automatic convenience flags.

A model checkpoint does not become releasable merely because training succeeded.

## 29. No authoritative notebook-only training

Notebooks may support exploration and visualization.

An authoritative run requires:

- Versioned source code;
- Versioned config;
- Noninteractive command entrypoint;
- Immutable job spec;
- Automated preflight;
- Canonical logs and artifacts;
- Resume and stop commands;
- Reproducible environment.

Copying cells from an uncommitted notebook is not an acceptable production training path.

## 30. `trainctl` becomes Luna’s only training interface

Sol will implement a narrow control interface conceptually including:

```text
trainctl validate <job-id>
trainctl preflight <job-id>
trainctl launch <job-id>
trainctl status <run-id>
trainctl pause <run-id>
trainctl resume <run-id>
trainctl checkpoint <run-id>
trainctl sync-artifacts <run-id>
trainctl verify-artifacts <run-id>
trainctl stop <run-id>
trainctl collect <run-id>
trainctl archive-status <run-id>
trainctl drain <run-id>
trainctl verify-termination <run-id>
trainctl close <run-id>
```

The controller verifies the owner-approved DR-25 campaign envelope, confirms the Lambda Cloud provider and instance profile, and validates the authoritative external archive before performing billable work.

Luna may:

- Invoke approved commands;
- Monitor objective state;
- Retry only classified infrastructure failures under the frozen policy;
- Resume the exact approved checkpoint;
- Stop at encoded conditions;
- Coordinate the approved owner-initiated transfer to the external archive;
- Verify archive receipts, required load tests, Lambda scratch cleanup, and provider-side termination.

Luna may not:

- Edit code;
- Edit data;
- Change a config;
- Select a different checkpoint, model, tokenizer, backend, precision, or hardware;
- Adjust learning rate, batch, sequence length, or budget;
- Substitute another cloud provider, artifact destination, archive volume, or transfer route;
- Remove a failing validation;
- Interpret whether a model improved;
- Continue a run after a semantic or implementation defect.

A defect requiring modification returns:

```text
BLOCKED_REQUIRES_SOL_REPAIR
```

A problem requiring scientific redesign returns:

```text
BLOCKED_REQUIRES_EXPERIMENT_DESIGN_REVIEW
```

## 31. Sol’s implementation authority and limits

Sol exclusively writes and repairs the training implementation.

Sol may choose design-neutral code mechanics such as:

- Module and class decomposition;
- Local algorithm implementations that satisfy the exact contract;
- Test fixtures;
- Error-handling mechanics;
- Performance optimizations proven equivalent;
- Approved dependency wiring.

Sol may not independently change:

- Model family or parent checkpoint;
- Tokenizer or processor;
- Admitted data;
- Sampler weights or exposure policy;
- Packing semantics;
- Loss objective;
- Trainable components;
- Precision or kernel policy;
- Optimizer or schedule;
- Evaluation or promotion gates;
- Retry or stop policy;
- Budget;
- Rights route;
- Scientific interpretation.

Sol may propose a change with evidence. It may not execute the changed experiment until ChatGPT designs the amendment and Joseph approves it.

## 32. Mandatory training-harness implementation sequence

The first implementation should proceed through these gates.

### `TH-00 — Canonical schemas and reference engine`

Implement the project-owned objects, tiny deterministic model/data fixtures, exact loss, exposure, checkpoint, and result contracts.

### `TH-01 — Native Transformers single-GPU adapter`

Prove exact encoding, loss masks, component manifest, checkpointing, and export on a small model.

### `TH-02 — FSDP2/DCP distributed adapter`

Prove multi-GPU sharding, complete state, interruption, exact or tolerance-defined resume, and model-only conversion.

### `TH-03 — ms-swift adapter`

Project the same canonical jobs through ms-swift and compare data, loss, components, resume, exports, and multimodal behavior.

### `TH-04 — Model-family compatibility`

Run bounded Qwen, Gemma, and Ministral compatibility smokes using approved tiny or 4B-class workloads where appropriate.

### `TH-05 — External-archive and transfer contract`

Prove stable volume identity, Thunderbolt/archive preflight, direct external staging, atomic promotion, hash and load verification, interrupted transfer, retention state, receipt generation, and no-fallback behavior using nonbillable fixtures.

### `TH-06 — Lambda Cloud adapter, failure injection, and run-controller integration`

Prove Lambda-only launch enforcement, current price and instance identity capture, watchdog and cost caps, checkpoint staging, archive-drain behavior, Luna permission boundaries, provider-side termination, scratch cleanup, and every required provider/archive failure mode.

Only then may the first DR-24 adaptation strategy experiment launch.

## 33. Principal hard failures

DR-23 treats the following as hard failures:

- A framework defining an unapproved model template, data transform, loss mask, objective, or trainable-module set;
- Silent truncation or example dropping;
- Cross-document packing without an approved attention policy;
- Loss applied to the wrong fields;
- A frozen parameter changing;
- A required trainable component receiving no update;
- Resuming from weights only while claiming exact resume;
- Losing sampler, shuffle, packer, RNG, or exposure state;
- Dropping failed samples or training attempts from the record;
- Hidden kernel or precision fallback;
- Changing the live job after OOM or divergence;
- Selecting checkpoints using the private final benchmark;
- Publishing only a dashboard while canonical metrics or logs are missing;
- Logging restricted source text, user data, secrets, or private gold;
- Treating one stochastic run as perfectly reproducible;
- Describing a cross-backend conversion as equivalent without a conformance test;
- Allowing an incomplete checkpoint to resume automatically;
- An export that differs materially from its source checkpoint;
- A training engine that cannot identify exact data exposure;
- Luna changing any code, data, model, objective, config, threshold, or budget;
- Sol redesigning the experiment without an approved amendment;
- Continuing a job merely to consume available credits;
- Launching project training or evaluation on an external cloud provider other than Lambda Cloud without a newly approved design;
- Treating Lambda scratch, a Lambda filesystem, another cloud store, the Mac internal disk, a dashboard, or another cache as the authoritative retained artifact archive;
- Launching while the approved external volume is absent, mismatched, unwritable, under the required rights/encryption state, or below its free-space floor;
- Promoting, resuming, or relying on a cloud-only checkpoint without a valid external-archive receipt;
- Deleting cloud-staged artifacts before local hash and required load validation;
- Closing a Lambda campaign without provider-side termination, scratch inventory, archive state, and billing closeout evidence;
- Hiding an archive, transfer, provider, or cleanup failure.

## 34. Decisions DR-23 would lock

Approval would establish that:

1. Biblical Scholar Lab owns the Training Core and canonical training semantics.
2. Mature libraries provide tensor execution and distributed mechanics rather than experiment authority.
3. A deterministic Reference Training Engine serves as the conformance oracle.
4. Native Transformers/PyTorch FSDP2 with Distributed Checkpoint is the preferred first low-level compact full-parameter path.
5. ms-swift is the preferred broad compatibility and multimodal training adapter candidate.
6. DeepSpeed ZeRO remains a separately evaluated fallback.
7. Megatron-SWIFT/Core remains scale-gated for larger, MoE, or advanced-parallelism training.
8. TorchTitan is an architectural reference and possible later adapter, not the initial production dependency.
9. Backend choice may differ by family and stage but must pass one canonical conformance suite.
10. Data, sampling, packing, loss, component, precision, kernel, distributed, optimizer, checkpoint, and evaluation semantics are immutable job inputs.
11. Streaming shuffle state must be reproducible; generic buffer shuffle cannot support exact resume without complete state.
12. Packing and attention boundaries are scientific contracts.
13. No example is silently truncated or dropped.
14. Token-based exposure and schedules are preferred to step-only accounting.
15. Every trainable and frozen parameter is explicitly manifested and verified.
16. BF16 is the provisional high-precision reference on capable hardware; lower precision is separately gated.
17. Active kernels and fallbacks are explicit run identity.
18. PyTorch Distributed Checkpoint is the preferred first distributed-resume substrate; safetensors is the preferred model-only export format.
19. Resume, resharded resume, weights-only continuation, and checkpoint fork remain distinct.
20. Reproducibility is reported through explicit tiers rather than universal bitwise claims.
21. Training-time evaluation cannot use the private final benchmark for checkpoint selection.
22. Canonical external-archive telemetry and exposure records remain authoritative; external dashboards and Lambda-local copies are optional operational mirrors.
23. Failure injection is required before expensive campaigns.
24. Training engines are promoted by correctness, resume, exposure, export, transparency, efficiency, and rights—not speed alone.
25. Authoritative training is noninteractive and versioned; notebooks are exploratory only.
26. Luna operates only through the frozen `trainctl` interface delegated by Sol.
27. Sol implements and repairs but does not redesign experiments.
28. ChatGPT designs training experiments and reviews code and evidence.
29. The owner-controlled external storage volume attached to the MacBook Pro through Thunderbolt is the authoritative retained store for every non-Git checkpoint and generated training or evaluation artifact.
30. The external volume is bound by stable device and volume identity; no silent fallback to the internal disk or another store is permitted.
31. Lambda local disks are temporary scratch, and every required artifact must receive a verified external-archive receipt before stage completion or promotion.
32. Lambda Cloud is the exclusive cloud infrastructure provider for project training and evaluation; capacity or provider failure blocks or requires a newly approved design rather than provider failover.
33. Lambda termination, scratch cleanup, archival transfer, and billing closeout are provider-verified lifecycle steps.
34. Joseph Abbud retains sole authority over budget, launch, checkpoint promotion, merge, storage-policy changes, provider changes, and release.

## 35. Decisions intentionally deferred

DR-23 does not yet select:

- Exact PyTorch, Transformers, Accelerate, ms-swift, TRL, PEFT, DeepSpeed, Megatron, or CUDA revisions;
- Exact production engine for each model family and stage;
- Exact optimizer, betas, epsilon, weight decay, or scheduler;
- Exact learning rates, warmup, token budgets, batch sizes, sequence lengths, or checkpoint intervals;
- Exact FSDP wrapping policy or DeepSpeed ZeRO configuration;
- Exact Lambda H100, B200, or other instance type, region, availability, price, and topology;
- Exact FP8 or compile configuration;
- Exact data-shard and physical serialization format;
- Exact remote telemetry provider;
- Exact profile-sampling frequency;
- Exact tolerance for every backend or resume equivalence test;
- Exact external-volume UUID, mount point, filesystem, encryption implementation, project-root path, transfer tool, cadence, maximum unsynchronized window, checkpoint retention count, and secondary owner-controlled backup policy;
- Exact DR-24 training experiments;
- Exact DR-25 campaign and budget envelopes;
- Exact Lambda workspace, networking, image, API/CLI integration, scratch size, cleanup procedure, and artifact-relay implementation consolidated in DR-25 and DR-28.

The following are not deferred: Lambda Cloud is the sole approved external cloud provider, and the owner-controlled Thunderbolt-connected external volume attached to the MacBook Pro is the authoritative retained artifact archive.

Those choices require the approved model audit, implementation spike, data census, hardware measurements, and individual experiment designs.

## 36. Approval statement

> **Biblical Scholar Lab will use a framework-neutral, project-owned Training Core that converts approved model, corpus, mixture, objective, component-update, precision, distributed, optimizer, checkpoint, evaluation, failure, rights, and budget contracts into immutable Training Job Specifications, canonical execution plans, exposure ledgers, checkpoints, exports, and Training Result Bundles. The project will not implement tensor execution, automatic differentiation, distributed collectives, standard optimizers, tokenizers, or ordinary trainer mechanics from scratch, but every adopted backend will remain a replaceable adapter whose data transformations, templates, packing, loss masks, trainable components, numerical paths, checkpoints, retries, and exports must conform to project-owned semantics. A small deterministic Reference Training Engine will serve as the conformance oracle. Native Transformers/PyTorch with FSDP2 and Distributed Checkpoint will be the preferred first low-level compact full-parameter path; a pinned ms-swift adapter will be the preferred broad model-family, multimodal, and objective-compatibility candidate; DeepSpeed ZeRO will remain a separately validated fallback; and Megatron-SWIFT/Core will remain scale-gated for larger, MoE, long-sequence, or advanced-parallelism work. Every run will bind exact model and processor artifacts, source and rights snapshots, model-specific materialization, deterministic sampling and packing state, attention and loss boundaries, trainable and frozen parameter manifests, precision and kernel identity, topology, optimizer, scheduler, RNG, token clocks, evaluation schedule, checkpoint policy, stop conditions, environment, Lambda provider and instance identity, external-archive profile, hardware, and cost. Authoritative runs will preserve exact or explicitly qualified exposure and resume semantics; generic streaming shuffle may not support an exact-resume claim without complete state; interrupted, resharded, weights-only, and forked continuations will remain distinct. Distributed resumable state will use a validated complete checkpoint substrate, with PyTorch Distributed Checkpoint as the preferred first implementation and safetensors as the preferred model-only export; every checkpoint and conversion will be atomic, hashed, load-tested, lineage-preserving, and separately identified. Lambda Cloud will be the sole approved external cloud execution provider for training and evaluation. Lambda instance and attached disks will remain temporary scratch, while the owner-controlled external storage volume attached to the MacBook Pro through Thunderbolt will be the authoritative retained store for every checkpoint, export, event log, exposure ledger, evaluation result, profile, manifest, and run artifact. Every retained artifact will receive an authenticated transfer, cryptographic and required load-validation receipt before promotion or normal run closure; cloud copies will be deleted only after external-archive acknowledgement and verified provider cleanup. If archival cannot finish before the immutable safety or cost deadline, Lambda will terminate at the cap and the run will remain nonpromotable rather than creating unbounded billing. Reproducibility will be reported through explicit identity, reference, resume, repeated-run, and cross-backend tiers rather than unsupported universal determinism. Training-time evaluation will remain separate from private final selection, canonical local metrics and exposure records will remain authoritative over optional dashboards, failure injection will precede expensive campaigns, and no live run may be silently repaired by changing its data, model, objective, precision, batch, sequence length, optimizer, schedule, provider, hardware, storage destination, transfer route, or budget. GPT-5.6 Sol will exclusively implement and repair the approved training machinery and produce a consolidated review handoff; GPT-5.6 Luna may only validate, launch, monitor, checkpoint, stop, resume, coordinate approved artifact transfer, verify archival and provider shutdown, collect, and close frozen Lambda jobs through the approved control interface delegated by Sol; ChatGPT will design experiments, review code and evidence, and recommend scientific next steps; and Joseph Abbud will retain sole authority over budget, launch, merge, checkpoint promotion, model progression, storage-policy changes, provider changes, and release.**

---

## References

[^msswift]: ModelScope, `ms-swift`, official repository. The framework documents support for CPT, SFT, preference objectives, full and PEFT training, multimodal models, FSDP/FSDP2, DeepSpeed, Megatron, quantization, inference, and deployment: <https://github.com/modelscope/ms-swift>.

[^megatron-swift]: ModelScope, “Megatron-SWIFT Quick Start.” The documentation lists full-parameter and LoRA support across pretraining, SFT, DPO, KTO, multimodal, MoE, and FP8 conditions: <https://github.com/modelscope/ms-swift/blob/main/docs/source_en/Megatron-SWIFT/Quick-start.md>.

[^accelerate]: Hugging Face Accelerate, “Fully Sharded Data Parallel.” Accelerate exposes PyTorch FSDP configuration and launch integration: <https://huggingface.co/docs/accelerate/usage_guides/fsdp>.

[^fsdp2]: PyTorch, `torch.distributed.fsdp.fully_shard`. FSDP2 uses per-parameter sharding with DTensor-based parameters and explicit pre/post-forward and backward sharding behavior: <https://docs.pytorch.org/docs/main/distributed.fsdp.fully_shard.html>.

[^dcp]: PyTorch, `torch.distributed.checkpoint`. Distributed Checkpoint supports parallel save/load and load-time resharding across distributed topologies: <https://docs.pytorch.org/docs/main/distributed.checkpoint.html>.

[^deepspeed]: DeepSpeed, “Zero Redundancy Optimizer.” ZeRO stages shard optimizer states, gradients, and parameters; ZeRO-3 shards all three and may use CPU/NVMe offload through ZeRO-Infinity: <https://www.deepspeed.ai/tutorials/zero/>.

[^megatron]: NVIDIA, `Megatron-LM` and Megatron Core. The project provides composable TP, PP, DP, EP, CP, mixed precision, optimized transformer blocks, and Hugging Face checkpoint bridge support: <https://github.com/NVIDIA/Megatron-LM>.

[^torchtitan]: PyTorch, `torchtitan`. TorchTitan is a PyTorch-native generative-model training platform exposing FSDP2, TP, PP, CP, activation checkpointing, distributed checkpointing, float8, checkpointable data loading, observability, and custom extension points; its repository describes it as under extensive development and currently narrower in out-of-box model coverage: <https://github.com/pytorch/torchtitan>.

[^hf-stream]: Hugging Face Datasets, “Stream.” The documentation describes streaming, sharding, shuffle buffers, stateful loading, and the limitation that shuffled buffer contents are lost and refilled on resume: <https://huggingface.co/docs/datasets/stream>.

[^safetensors]: Hugging Face, Safetensors documentation. Safetensors is designed as a non-pickle, fast, zero-copy tensor storage format: <https://huggingface.co/docs/safetensors/index>.

[^trainer-jit]: Hugging Face Transformers, “Trainer features — Checkpointing.” Current Trainer documentation describes periodic, resumable, and just-in-time `SIGTERM` checkpointing and warns that incomplete checkpoint state must be handled and sufficient shutdown grace provided: <https://huggingface.co/docs/transformers/main/trainer_recipes>.

[^pytorch-repro]: PyTorch, “Reproducibility.” PyTorch states that complete reproducibility is not guaranteed across releases, commits, platforms, or CPU/GPU execution and documents methods for controlling randomness and nondeterministic algorithms within a pinned environment: <https://docs.pytorch.org/docs/stable/notes/randomness>.

[^pytorch-deterministic]: PyTorch, `torch.use_deterministic_algorithms`. The API can select deterministic alternatives or raise when only a nondeterministic implementation is available, while noting that the setting alone is insufficient for complete application reproducibility: <https://docs.pytorch.org/docs/main/generated/torch.use_deterministic_algorithms.html>.

[^pytorch-profiler]: PyTorch, `torch.profiler`. The profiler records CPU and device operators, shapes, stacks, memory, and execution traces for performance analysis: <https://docs.pytorch.org/docs/main/profiler.html>.

[^pytorch-memory]: PyTorch, “Understanding CUDA Memory Usage.” PyTorch supports allocator-history and memory snapshots while noting that allocations made outside the PyTorch allocator, including some NCCL memory, require separate accounting: <https://docs.pytorch.org/docs/main/torch_cuda_memory>.
