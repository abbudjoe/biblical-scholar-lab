# DR-11 — Foundation-Model Family and Component Architecture

| Field | Value |
|---|---|
| Design ID | `DR-11` |
| Status | `APPROVED` |
| Approval date | 2026-08-15 |
| Project owner | Joseph Abbud |
| Designer and independent reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2 and supplements; DR-03; DR-04; DR-05; DR-06; DR-07; DR-08; DR-09; DR-10 |
| Implementation authority | GPT-5.6 Sol, under the approved design |
| Supersedes if approved | The dated model-release inventory in DR-02-S02 where the current official catalog has changed; all DR-02 capacity, bake-off, hard-gate, and budget principles remain binding unless explicitly changed here |

## 1. Purpose

Biblical Scholar Lab requires a foundation model that can act as the generative, planning, comparison, and explanation core of a larger scholarly system. It is not expected to contain the exact biblical corpus, textual apparatus, translation genealogy, modern scholarship, reference system, or rights decisions entirely in its parameters.

The selected model family must nevertheless be capable of:

- interpreting structured evidence from DR-04 through DR-10;
- selecting and using deterministic tools;
- preserving source, witness, edition, translation, and scholarship distinctions;
- comparing several causal explanations under the Translation Nuance Core;
- producing calibrated, cited prose at Brief, Study, and Scholarly depths;
- supporting ancient-script input and multilingual output;
- understanding printed Bible and commentary pages;
- operating over long evidence packets without silently losing critical distinctions;
- accepting domain adaptation without catastrophic loss of general, multilingual, multimodal, tool-use, and long-context capability;
- supporting an economically plausible inference and deployment path.

DR-11 defines:

- the current official candidate inventory and admission rules;
- the roles of Base, instruction, reasoning, and higher-capacity checkpoints;
- the component identity required for every model artifact;
- architecture-specific preservation and adaptation constraints;
- tokenizer, processor, special-token, chat-template, multimodal, long-context, reasoning, and MTP contracts;
- compact-model, large-model, and mobile-family relationships;
- family-neutral harness requirements;
- model-selection and promotion rules;
- conditions under which architectural specialization may be considered later.

DR-11 does **not** choose the winning model. The winner is determined by the approved project-specific bake-off and later evidence gates.

## 2. Governing principle

> **The project selects a model role by measured fitness for Biblical Scholar Lab—not by release recency, vendor benchmark rank, parameter count, or family loyalty. Every checkpoint is treated as a versioned bundle of neural weights, tokenizer, processor, modality pathways, templates, generation policy, runtime assumptions, licenses, and training lineage. Base and post-trained checkpoints are different experimental objects, and architecture-specific capabilities may not be silently altered or compared under incompatible conditions.**

The system must preserve this chain:

```text
official model family and release
    → exact checkpoint and immutable revision
    → exact tokenizer, processor, templates, and model components
    → approved runtime and precision configuration
    → measured baseline capability
    → approved adaptation activity
    → exact derivative checkpoint
    → capability-retention and release evaluation
```

No derivative may be described merely as “Qwen,” “Gemma,” or “Ministral” without the exact lineage needed to reproduce and interpret it.

## 3. Current official-release audit

This section is a dated inventory as of 2026-08-15. It must be reverified immediately before the model bake-off and before any billable campaign.

### 3.1 Compact clean-adaptation candidates

The initial compact Base-checkpoint candidates remain:

```text
Qwen/Qwen3.5-9B-Base
google/gemma-4-12B
mistralai/Ministral-3-8B-Base-2512
```

Current official records identify:

- Qwen3.5-9B-Base as a pretrained-only, native vision-language checkpoint intended for fine-tuning and research;
- Gemma 4 12B as an official pretrained, unified multimodal checkpoint;
- Ministral 3 8B Base as an official base-pretrained model with a separate vision encoder and matched post-trained family.

### 3.2 Compact product-first candidates

The corresponding initial product candidates are:

```text
Qwen/Qwen3.5-9B
google/gemma-4-12B-it
mistralai/Ministral-3-8B-Instruct-2512
mistralai/Ministral-3-8B-Reasoning-2512
```

The Ministral Instruct and Reasoning variants may be screened before both are admitted to every expensive test.

### 3.3 Higher-capacity candidates

The primary higher-capacity comparison becomes:

```text
Qwen/Qwen3.8-27B
google/gemma-4-31B
google/gemma-4-31B-it
```

Current official records identify Qwen3.8-27B as a newly released, post-trained, native vision-language 27B model. Its official collection does not currently list a matching Qwen3.8-27B Base checkpoint.

Qwen3.8-27B therefore replaces Qwen3.6-27B as the primary Qwen higher-capacity product comparator. Qwen3.6-27B remains an engineering fallback and historical control because it shares the Qwen3.5 architecture family and has a longer operational history.

### 3.4 Optional capacity-efficiency comparator

The following may enter inference-only screening if the approved budget permits:

```text
google/gemma-4-26B-A4B
google/gemma-4-26B-A4B-it
```

Gemma 4 26B A4B is a mixture-of-experts model with approximately 25.2B total parameters and 3.8B active parameters per token. It is not part of the mandatory initial bake-off and receives no adaptation budget without a separate design decision.

### 3.5 Exploratory larger clean-Base candidate

The following may be evaluated only under a separate complexity and budget review:

```text
Qwen/Qwen3.5-35B-A3B-Base
```

Its clean Base status is scientifically attractive, but total-parameter optimizer state, expert routing, checkpoint size, distributed training, and adaptation stability make it materially different from the dense compact track.

### 3.6 Mobile and student candidates

The mobile-family candidates remain deferred to DR-29, but the current architecture families provide plausible smaller siblings:

```text
Qwen3.5 2B / 4B Base and post-trained
Gemma 4 E2B / E4B Base and instruction-tuned
Ministral 3 3B Base, Instruct, and Reasoning
```

No compact winner automatically determines the mobile winner.

## 4. Candidate-admission contract

A checkpoint may enter the primary bake-off only if all of the following are established:

1. It is published by the official model organization or an explicitly authorized official distributor.
2. It is an intact foundation checkpoint, not an unofficial layer reduction, pruning, merge, ablation, “uncensored” derivative, or distillation unless that derivative is the explicit subject of a later experiment.
3. The exact repository revision and all weight-file hashes can be frozen.
4. The tokenizer, processor, model configuration, generation configuration, chat template, and special-token map are available and hashable.
5. Its Base, instruction, reasoning, or other training stage is documented sufficiently for the intended comparison.
6. Its license and acceptable-use conditions pass DR-10 review for the intended operation and artifact.
7. It can be loaded without unreviewed arbitrary remote code, or any required custom code is pinned, audited, and included in the model manifest.
8. At least one viable training and inference path exists for the intended stage.
9. The checkpoint can be evaluated under the common harness without suppressing a project hard failure.
10. The project can retain the exact source artifact needed for reproducibility.

Community quantizations may be used for exploratory inference only after their derivation and numerical behavior are verified. They do not replace official master weights in the primary scientific lineage.

## 5. Model artifact identity

Every model artifact is identified by a `ModelArtifactManifest` containing at least:

```text
model_artifact_id
family
official_repository
immutable_repository_revision
model_configuration_hash
weight_file_hashes
tokenizer_repository_and_revision
tokenizer_file_hashes
processor_repository_and_revision
processor_file_hashes
chat_template_hash
special_token_map_hash
generation_configuration_hash
training_stage
parent_model_artifact_ids[]
architecture_type
parameter_counts_by_component
context_configuration
modality_configuration
reasoning_configuration
MTP_or_draft_component_configuration
precision_and_quantization
runtime_implementation_and_revision
kernel_path_and_attention_backend
license_and_rights_manifest
derivation_activity
content_hash
```

The project must never rely on an unversioned alias such as `latest`.

## 6. Component registry

The architecture treats the following as independently identified components where the family exposes them:

```text
language-model backbone
input embedding table
output language-model head
vision encoder or visual patch pathway
audio encoder or audio patch pathway
multimodal projector or direct modality projection
position-encoding system
full-attention layers
linear-, local-, or sliding-attention layers
mixture-of-experts router and experts
normalization and feed-forward blocks
multi-token-prediction or speculative-draft component
tokenizer
multimodal processor
chat template
reasoning or thinking controller
tool-call serialization
```

A derivative checkpoint records which components changed, which remained frozen, and which were absent or disabled.

## 7. Family architecture profiles

### 7.1 Qwen3.5 / Qwen3.6 / Qwen3.8 profile

The current dense Qwen3.5-derived architecture uses:

- a separate vision encoder;
- a hybrid language backbone containing three Gated DeltaNet layers for each full-attention layer;
- multimodal positional encoding;
- a large padded vocabulary of 248,320 entries;
- multi-token-prediction training support;
- a native 262,144-token context in the relevant 9B and 27B checkpoints.

For Qwen3.5-9B, the language model has 32 layers. Current Qwen3.8-27B uses the same general architectural family at 64 language-model layers and is post-trained with configurable reasoning effort and native vision-language input.

The Qwen profile creates the following mandatory checks:

- the active Gated DeltaNet implementation and fallback path are recorded;
- multimodal positional encoding is not modified casually;
- the vision encoder and language backbone are evaluated independently and jointly;
- the text-only serving mode is distinguished from the full multimodal path;
- the large tokenizer vocabulary receives explicit ancient-language and memory analysis;
- MTP behavior is validated after any backbone adaptation;
- framework and custom-kernel versions are part of run identity.

### 7.2 Gemma 4 profile

Gemma 4 uses hybrid local sliding-window and global attention, with the final layer global and proportional RoPE in the global layers. The 12B and 31B models expose materially different multimodal architectures.

#### Gemma 4 12B Unified

The 12B model has approximately 11.95B parameters, 48 layers, a 256K context, and a 262K vocabulary. It removes separate vision and audio encoders and instead projects raw image patches and audio waveforms into the decoder embedding space through lightweight linear pathways.

Consequences:

- “freeze the vision tower” is not a valid preservation strategy for the unified model;
- text-only adaptation changes the same decoder that performs image and audio understanding;
- multimodal retention and replay are especially important;
- whole-model and modality-path learning-rate controls must be designed explicitly;
- audio remains an inherited capability canary even though it is not a version-one product requirement.

#### Gemma 4 31B Dense

The 31B model has approximately 30.7B parameters, 60 layers, a 256K context, a 262K vocabulary, and a separate vision encoder of roughly 550M parameters. It does not provide native audio input.

The Base and instruction-tuned 31B checkpoints make Gemma the cleanest current family for a matched large Base/product capacity comparison.

#### Gemma 4 MTP

Gemma 4 provides multi-token-prediction components intended to accelerate speculative decoding. These are treated as inference-acceleration components, not as evidence of better scholarly reasoning.

### 7.3 Ministral 3 profile

Ministral 3 8B contains approximately:

- an 8.4B language model;
- a 0.4B vision encoder;
- a 256K context window;
- separate Base, Instruct, and Reasoning checkpoints;
- an edge-oriented deployment path;
- a tokenizer accessed through the versioned `mistral-common` stack.

Mandatory checks include:

- exact tokenizer and `mistral-common` revision;
- Base-versus-Instruct-versus-Reasoning behavior;
- vision-encoder retention after language adaptation;
- FP8/BF16 distinction among released product variants;
- quantized deployment and tool-call behavior;
- modern-language breadth versus ancient-language performance.

## 8. Base and post-trained checkpoints are distinct lineages

The project maintains two principal scientific lineages.

### 8.1 Clean adaptation lineage

```text
official Base checkpoint
    → approved continued pretraining
    → translation-aware mid-training
    → scholarly SFT
    → retrieval-aware SFT
    → preference optimization
```

This lineage provides the cleanest attribution for what our corpus and curriculum contribute.

### 8.2 Product-first lineage

```text
official post-trained checkpoint
    → deterministic tools and RAG baseline
    → retrieval-aware scholarly SFT or PEFT
    → bounded low-learning-rate domain adaptation if justified
    → preference optimization
```

This lineage preserves the vendor's existing reasoning, tool use, instruction following, multimodal alignment, and safety post-training as much as possible.

### 8.3 No false equivalence

A Base-derived model and a vendor post-trained model cannot be compared as if they differ only in domain knowledge. Their behavior, instruction following, refusal policy, thinking style, and multimodal alignment may differ substantially.

### 8.4 Merge experiments are separate

Any attempt to merge a Base-domain delta into an official post-trained checkpoint is an explicit later experiment. It requires:

- same-family and architecture compatibility;
- a defined merge method;
- a falsifiable preservation hypothesis;
- complete ablations;
- multimodal, multilingual, tool, reasoning, and safety regression tests.

Cross-family model merging is not authorized.

## 9. Tokenizer policy

### 9.1 No tokenizer modification in the baseline

The initial bake-off and adaptation smoke tests preserve each candidate's official tokenizer.

No baseline experiment may:

- add ancient-language tokens;
- delete tokens;
- retrain the tokenizer;
- remap token IDs;
- replace the embedding or language-model head;
- change normalization silently.

Tokenizer modification would introduce additional variables, complicate product-checkpoint compatibility, and risk multimodal and post-training behavior.

### 9.2 Required tokenizer census

Every candidate is measured on:

- polytonic Classical and Koine Greek;
- Greek with critical symbols and punctuation;
- pointed and unpointed Biblical Hebrew;
- Hebrew cantillation;
- Biblical Aramaic;
- Syriac and Coptic canary samples;
- Latin;
- scholarly transliteration conventions;
- English, Spanish, and French;
- canonical references and tool-call formats;
- complete-New-Testament context packs.

Metrics include:

```text
tokens per Unicode code point
tokens per extended grapheme cluster
tokens per orthographic token
tokens per linguistic word
byte-fallback or unknown behavior
normalization sensitivity
round-trip fidelity
special-token collision
embedding/output-head memory share
```

Tokenizer efficiency is a cost and representational signal, not a sufficient model-selection criterion.

### 9.3 Tokenizer change gate

Tokenizer or embedding modification may be proposed only if the selected family exhibits a persistent, material ancient-language deficit that cannot be addressed through data, normalization views, training objectives, or model selection.

## 10. Processor and multimodal input contract

Every multimodal evaluation and training run records:

```text
processor revision
image resizing and aspect-ratio policy
patch or visual-token count
OCR preprocessing
page-cropping policy
image quality transformations
modality ordering
maximum modality tokens
text/image/audio interleaving
```

The project does not compare two models' image capability using undocumented or materially different preprocessing.

Page-image inputs remain source artifacts under DR-05 and DR-10. The processor output is a computational projection, not the authoritative page transcription.

## 11. Multimodal preservation policy

### 11.1 Preservation is required even when training is text-heavy

Domain adaptation focused on text can still damage:

- image-text alignment;
- OCR and layout understanding;
- visual reference resolution;
- tool use conditioned on images;
- audio capability in Gemma 4 12B;
- general multimodal reasoning.

Every adaptation stage therefore runs multimodal retention tests.

### 11.2 Separate-encoder families

For Qwen and Ministral, candidate strategies may include:

- freezing the vision encoder;
- freezing or reducing learning rate on the multimodal projector;
- low learning rate on the shared language backbone;
- bounded multimodal replay;
- adapter targeting that excludes visual components.

Freezing the vision encoder alone does not guarantee preserved image behavior because the language backbone and projector still participate in cross-modal reasoning.

### 11.3 Unified Gemma 4 12B

Because the 12B model projects modalities directly into the shared decoder, preservation requires family-specific experiments. Candidate strategies include:

- low-learning-rate whole-backbone adaptation;
- parameter-efficient modules restricted to approved language blocks;
- multimodal replay;
- modality-balanced retention loss;
- product-first post-training rather than unrestricted full CPT.

No assumption that the unified architecture is easier or harder to adapt is accepted without evidence.

### 11.4 Modular fallback

A valid product outcome may use:

```text
official multimodal front-end model
    → page segmentation and evidence extraction
    → specialized text-domain reasoning model
```

A single-model architecture is preferred only when it meets the benchmark and operational requirements.

## 12. Reasoning and thinking modes

The candidate families expose different reasoning controls:

- Qwen3.8 provides configurable reasoning effort and optional non-thinking behavior;
- Gemma 4 provides configurable thinking behavior;
- Ministral 3 publishes separate Instruct and Reasoning variants.

The bake-off must not compare one model in an expensive deliberate mode against another in a direct mode without disclosure.

The harness defines at least:

```text
DIRECT_MODE
DELIBERATE_MODE
```

For each mode, it freezes:

- prompt and system policy;
- thinking or reasoning setting;
- output-token budget;
- sampling configuration;
- tool budget;
- wall-clock and cost accounting.

Private chain-of-thought is not a project artifact or evaluation requirement. The project stores final answers, tool calls, evidence traces, usage, and concise rationale where available—not hidden internal reasoning traces.

## 13. Long-context architecture

### 13.1 Native capacity is not proven use

A 256K or 262K advertised context does not establish reliable use of evidence across that window.

DR-15 will define the final context composer. DR-11 requires each candidate to be tested at multiple lengths, including:

```text
4K
16K
32K
64K
128K
full-New-Testament candidate pack
maximum approved family-specific stress test
```

### 13.2 Training context is independently selected

Initial continued-pretraining and SFT sequence lengths are selected by the later experiment design. They do not default to the model's maximum inference context.

Position encoding, RoPE scaling, sliding-window structure, linear-attention state, and multimodal positional systems remain unchanged in the baseline.

### 13.3 Evidence-position testing

Long-context evaluation places decisive evidence:

- near the beginning;
- in the middle;
- near the end;
- across distant documents;
- among plausible distractors.

The model must be compared against targeted retrieval and hybrid full-context-plus-retrieval configurations.

## 14. Multi-token-prediction and speculative decoding

MTP or draft components are treated as serving optimizations unless a later experiment explicitly studies them.

The correctness reference is standard autoregressive generation from the selected target model.

After any adaptation:

1. The target-model output path is validated without speculative acceleration.
2. MTP acceptance rate and speed are measured.
3. Output equivalence or approved tolerance is tested.
4. A stale draft component is retrained, disabled, or clearly documented.

MTP speedup cannot be counted as a model-capability improvement.

## 15. Precision and quantization

### 15.1 Master checkpoints

The authoritative scientific checkpoint remains in its approved high-precision form, normally BF16 or another explicitly validated training precision.

### 15.2 Quantization is a derivative experiment

FP8, INT8, 4-bit, mixed-precision, GGUF, MLX, Core ML, LiteRT, or other forms are separately identified derivatives.

They are evaluated for:

- Translation Nuance;
- Greek, Hebrew, Aramaic, and multilingual fidelity;
- tool-call syntax;
- citation formatting;
- calibration and refusal behavior;
- multimodal retention;
- long-context stability;
- extraction and memorization risk.

No candidate wins the foundation-model bake-off solely because an unofficial quantization is convenient.

## 16. Architecture-neutral harness with capability negotiation

The model harness must expose one logical interface while preserving family-specific capabilities.

A `ModelCapabilities` record includes:

```text
base_or_posttrained
text_input
image_input
audio_input
video_input
native_tool_calling
structured_output
reasoning_modes
maximum_native_context
verified_context_lengths
processor_type
vision_architecture
audio_architecture
attention_architecture
MTP_support
quantization_support
training_backend_support
inference_backend_support
```

The harness may not force all models into the lowest common denominator. It supports:

- common comparison paths;
- family-native paths;
- explicit capability gaps;
- comparable cost and latency accounting.

Every result declares which path was used.

## 17. Training-component policy

Before an adaptation campaign, the approved experiment specifies for each component:

```text
FROZEN
TRAINED_FULL_RATE
TRAINED_REDUCED_RATE
ADAPTER_TARGET
REPLAY_PROTECTED
REINITIALIZED
REMOVED
NOT_PRESENT
```

The policy covers at least:

- embeddings;
- output head;
- language backbone;
- vision encoder or visual pathway;
- audio pathway;
- multimodal projector;
- router and experts where applicable;
- normalization layers;
- MTP/draft components.

Sol may implement the approved grouping. Sol may not choose a scientifically consequential freeze or learning-rate policy independently.

## 18. Model-family bake-off requirements

DR-02-S02 remains authoritative for weighting, hard gates, budget, and stages. DR-11 adds these component-level requirements.

### 18.1 Stage 0 — Static architecture audit

For every candidate:

- freeze exact artifacts and licenses;
- enumerate components and parameter counts;
- verify Base/post-trained lineage;
- verify tokenizer and processor behavior;
- identify supported training and inference paths;
- calculate memory and checkpoint requirements;
- identify custom kernels, remote code, and fallback paths;
- document unsupported or immature capabilities.

### 18.2 Stage 1 — No-training model evaluation

Run:

- project benchmark modes;
- tokenizer census;
- tools and RAG;
- page-image tests;
- long-context tests;
- direct and deliberate modes;
- latency, throughput, memory, and cost;
- public-safe extraction and behavior checks.

### 18.3 Stage 2 — Matched compact adaptation smoke

Surviving compact Base models receive the same approved domain sample, with family-specific component-preservation policies that implement the same scientific intent.

The experiment reports:

- domain loss;
- Translation Nuance change;
- general, multilingual, multimodal, and long-context retention;
- component drift;
- optimizer and checkpoint cost;
- runtime stability;
- cost per validated gain.

### 18.4 Stage 3 — Matched post-training learnability

Surviving compact product candidates receive the same scholarly behavior and retrieval-aware sample, adapted through approved comparable methods.

### 18.5 Stage 4 — Capacity comparison

Qwen3.8-27B and Gemma 4 31B-it receive the same difficult-case inference evaluation. Gemma 4 31B Base provides a clean large-Base reference but receives no adaptation without the separate DR-02 gate.

## 19. Selection may produce several winners

The project may select different artifacts for different roles:

```text
clean CPT research winner
compact product winner
large difficult-query fallback
multimodal page front-end
mobile student family
teacher/distillation model
```

One family is preferred across roles when its performance is statistically and practically close enough, because family coherence simplifies:

- tokenizer and prompt behavior;
- data and adapter reuse;
- model merging;
- deployment;
- quantization;
- evaluation;
- maintenance.

Family coherence may not override a meaningful epistemic hard failure or a large project-specific capability gap.

## 20. Compact versus large-model routing

A tiered architecture is an approved possible outcome:

```text
compact model
    → ordinary study
    → passage analysis
    → tool orchestration
    → common Translation Nuance cases

large model
    → difficult multi-source synthesis
    → complex textual criticism
    → unresolved causal chains
    → second-pass verification
```

The routing policy itself is designed later under DR-16 and benchmark evidence. The compact model may not secretly escalate private or restricted evidence to an external service.

## 21. Architecture-extension boundary

DR-06's A0–A6 Translation Nuance architecture ladder remains binding.

DR-11 authorizes no custom foundation block, tokenizer surgery, graph neural network, semantic kernel, or architecture change in the baseline.

Architecture extension requires:

- a persistent project-benchmark deficit;
- evidence that the deficit is representational rather than primarily data, retrieval, supervision, capacity, or tooling;
- a falsifiable design;
- controlled ablation;
- compatibility, deployment, and reproducibility review;
- owner approval.

## 22. Capability-preservation suite

Every adapted checkpoint is evaluated against its exact parent for:

```text
general reasoning
instruction following
tool use
structured output
English fluency
Spanish and French behavior
ancient-script handling
Greek and Hebrew analysis
multimodal page understanding
general visual reasoning
audio canary where inherited
long-context retrieval
scope and safety
citation behavior
quantization readiness
```

A gain in domain perplexity or verse recall cannot compensate for a material hard-failure regression.

## 23. Model release and derivative naming

Every public or internal derivative name must disclose enough lineage to avoid confusion.

A model card identifies:

- exact parent checkpoint;
- training stages;
- corpus and rights lineage;
- components changed and frozen;
- benchmark version;
- retained and degraded capabilities;
- precision and quantization;
- permitted release and use status.

The project must not use a family name in a way that implies vendor endorsement.

## 24. Sol implementation boundary

We define and approve:

- candidate admission and roles;
- exact artifact manifest;
- component registry;
- Base/product lineages;
- tokenizer and processor policy;
- multimodal-preservation intent;
- reasoning and long-context modes;
- MTP and quantization semantics;
- capability-preservation tests;
- model-selection and promotion rules.

Sol may determine only reversible implementation mechanics that preserve those contracts, including:

- module and adapter organization;
- model-loading code;
- test fixtures;
- telemetry implementation;
- backend glue selected under DR-23;
- performance optimizations proven equivalent.

Sol must stop with `BLOCKED_REQUIRES_DESIGN_REVIEW` when an architecture or framework limitation would require changing:

- candidate identity;
- component-freeze policy;
- tokenizer;
- objective;
- modality behavior;
- reasoning mode;
- context semantics;
- model-selection metric;
- retention gate;
- rights or release status.

## 25. Hard failures

The following are DR-11 hard failures:

- Misidentifying a post-trained checkpoint as a clean Base checkpoint.
- Using an unofficial derivative as the official foundation artifact.
- Loading a mutable model alias without frozen hashes.
- Changing tokenizer IDs, normalization, processor behavior, or chat template without recording it.
- Comparing models under materially different reasoning, tool, context, or image-processing conditions without disclosure.
- Treating vendor benchmarks as project selection evidence.
- Claiming native context length proves reliable full-context reasoning.
- Freezing a vision encoder while ignoring cross-modal degradation in the language backbone.
- Applying the same freeze policy to Gemma 4 12B Unified as to separate-encoder models.
- Enabling stale MTP or speculative-draft components without validation.
- Calling quantized behavior equivalent without domain and multimodal tests.
- Allowing a high aggregate score to conceal citation, source-type, language, or multimodal hard failures.
- Letting release recency bypass framework-stability and reproducibility gates.
- Allowing Sol or Luna to substitute a different checkpoint or revision during execution.

## 26. Binding decisions

Approval of DR-11 would lock the following:

1. No foundation-model family is selected before the project-specific bake-off.
2. The mandatory compact clean-adaptation candidates are Qwen3.5-9B-Base, Gemma 4 12B, and Ministral 3 8B Base, subject to live revalidation.
3. Their matched product checkpoints form the compact product-first comparison.
4. Qwen3.8-27B becomes the primary high-capacity Qwen product comparator; Qwen3.6-27B becomes fallback and historical control.
5. Gemma 4 31B Base and instruction-tuned checkpoints provide the matched large-capacity Gemma comparison.
6. Gemma 4 26B A4B and Qwen3.5-35B-A3B-Base remain optional, separately gated experiments.
7. Model identity includes weights, tokenizer, processor, templates, components, runtime, precision, license, and immutable revisions.
8. Base and post-trained checkpoints remain distinct lineages.
9. No tokenizer modification occurs in the baseline.
10. Qwen, Gemma, and Ministral receive family-specific component-preservation strategies under a common scientific intent.
11. Gemma 4 12B's unified modality architecture requires a distinct preservation experiment.
12. Reasoning modes, processor behavior, context length, and generation configuration are explicit comparison variables.
13. MTP is an acceleration component rather than a scholarly-capability claim.
14. Quantized and converted models are derivative artifacts requiring separate evaluation.
15. The harness is family-neutral at the contract level and capability-aware at runtime.
16. The project may select different winners for clean research, compact product, large fallback, multimodal front-end, and mobile roles.
17. Family coherence is a preference, not a hard override of capability or epistemic reliability.
18. A tiered compact-plus-large architecture is an approved success outcome.
19. DR-06's architecture-extension ladder remains the only path to custom semantic model architecture.
20. Every adapted checkpoint must pass a parent-relative capability-preservation suite.

## 27. Decisions intentionally deferred

DR-11 does not yet select:

- the winning compact or large model;
- exact immutable revisions used in the eventual bake-off;
- the final training or inference framework;
- exact component learning rates;
- LoRA target modules;
- exact replay ratios;
- exact training sequence length;
- final reasoning settings;
- final tokenizer admission thresholds;
- final long-context promotion thresholds;
- final image resolution and token budget;
- exact model-routing policy;
- exact quantization method;
- exact mobile model;
- exact MTP retraining or disablement policy;
- final public model names;
- final model release status;
- whether any optional MoE or larger clean-Base experiment is authorized.

Those decisions belong to DR-12 through DR-16, DR-18, DR-20 through DR-25, DR-28, DR-29, and owner-approved experiment designs.

## 28. Approved statement

> **Biblical Scholar Lab will select foundation models through a project-specific, evidence-gated comparison rather than release recency, vendor benchmark rank, parameter count, or family preference. Every model will be represented as an immutable artifact bundle containing exact weights, tokenizer, processor, templates, modality pathways, context and reasoning configuration, MTP or draft components, runtime and kernel identity, precision, license, and derivation lineage. Qwen3.5-9B-Base, Gemma 4 12B, and Ministral 3 8B Base will form the mandatory compact clean-adaptation candidates with matched post-trained product candidates; Qwen3.8-27B and Gemma 4 31B-it will form the primary high-capacity product comparison, while Gemma 4 31B Base provides the clean large-Base reference and Qwen3.6-27B remains an engineering fallback. Base and post-trained lineages, model subword tokenization, modality processors, reasoning modes, context lengths, speculative decoding, and quantized derivatives will remain explicit experimental variables. The baseline will preserve official tokenizer and neural topology, use architecture-specific component-freeze and replay policies, evaluate multimodal and multilingual retention after every adaptation, and treat native context capacity or vendor benchmarks as hypotheses rather than proof. The model harness will expose a family-neutral logical contract while preserving family-native capabilities, and the project may select different compact, large, multimodal, mobile, or research winners when evidence warrants. Custom Translation Nuance architecture remains governed by DR-06's staged extension ladder, and every consequential model, component, adaptation, selection, and release decision remains subject to ChatGPT design and review and owner approval.**

---

## References

[^qwen35-base]: Qwen, `Qwen/Qwen3.5-9B-Base`. The official repository identifies a pretrained-only native vision-language checkpoint intended for fine-tuning and research and documents its 9B language model, hybrid Gated DeltaNet/full-attention stack, 248,320-entry padded vocabulary, MTP training, and 262,144-token native context: https://huggingface.co/Qwen/Qwen3.5-9B-Base

[^qwen35-transformers]: Hugging Face Transformers, “Qwen3.5.” The documentation describes Qwen3.5 as a natively multimodal family trained on interleaved text, image, and video tokens with three Gated DeltaNet layers per full-attention layer and shared architecture support for dense Qwen3.5 and Qwen3.6 variants: https://huggingface.co/docs/transformers/model_doc/qwen3_5

[^qwen38]: Qwen, `Qwen/Qwen3.8-27B`. The official repository identifies a post-trained 27B vision-language model with the Qwen3.5-derived hybrid architecture, configurable reasoning effort, 248,320-entry padded vocabulary, MTP, and 262,144-token native context: https://huggingface.co/Qwen/Qwen3.8-27B

[^qwen38-collection]: Qwen, “Qwen3.8 Collection.” The official collection currently lists Qwen3.8-27B and its FP8 derivative but no 27B Base checkpoint: https://huggingface.co/collections/Qwen/qwen38

[^qwen36]: Qwen, `Qwen/Qwen3.6-27B`. The official repository identifies the checkpoint as post-trained and architecture-compatible with the Qwen3.5 family: https://huggingface.co/Qwen/Qwen3.6-27B

[^qwen35-collection]: Qwen, “Qwen3.5 Collection.” The official collection lists 9B and 4B Base checkpoints, 27B post-trained weights, and the 35B-A3B Base and post-trained family: https://huggingface.co/collections/Qwen/qwen35

[^gemma4-card]: Google DeepMind, “Gemma 4 Model Card.” The official card describes pretrained and instruction-tuned variants, hybrid sliding/global attention, 256K context for the 12B and 31B models, a 262K vocabulary, the encoder-free 12B Unified model, the separate-vision-encoder 31B model, the 26B A4B MoE model, and support for more than 140 pretraining languages: https://ai.google.dev/gemma/docs/core/model_card_4

[^gemma4-collection]: Google, “Gemma 4 Collection.” The official collection lists Base and instruction-tuned 12B, 26B A4B, and 31B checkpoints along with mobile-oriented E2B and E4B variants: https://huggingface.co/collections/google/gemma-4

[^gemma4-mtp]: Google AI for Developers, “Speed up Gemma 4 with Multi-Token Prediction.” Google describes Gemma 4 MTP as a draft component for speculative decoding that shares embeddings and builds on target-model activations: https://ai.google.dev/gemma/docs/mtp/overview

[^ministral-base]: Mistral AI, `mistralai/Ministral-3-8B-Base-2512`. The official card identifies an 8.4B language model, 0.4B vision encoder, 256K context, Apache 2.0 license, edge orientation, and a Base checkpoint intended for custom post-training: https://huggingface.co/mistralai/Ministral-3-8B-Base-2512

[^ministral-collection]: Mistral AI, “Ministral 3 Collection.” The official collection provides Base, Instruct, and Reasoning checkpoints at 3B, 8B, and 14B sizes with vision support: https://huggingface.co/collections/mistralai/ministral-3
