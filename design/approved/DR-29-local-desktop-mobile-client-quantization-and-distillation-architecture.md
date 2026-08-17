# DR-29 — Local Desktop, Mobile Client, Quantization, and Distillation Architecture

| Field | Value |
|---|---|
| Design ID | `DR-29` |
| Status | `APPROVED` |
| Approval date | 2026-08-17 |
| Project owner | Joseph Abbud |
| Product, architecture, benchmark, and experiment designer | ChatGPT |
| Independent implementation and evidence reviewer | ChatGPT |
| Depends on | DR-01 through DR-28, including DR-02 revision 2 and DR-02-S03 |
| Supersedes within scope | DR-02-S03 sections 3–4 and its mobile-first deployment priority; all compatible evidence, OCR, quantization, privacy, explicit-routing, and capability-tier principles remain in force |
| Implementation authority | GPT-5.6 Sol exclusively implements and repairs the approved mobile, edge, distillation, quantization, packaging, native-platform, runtime-adapter, local-data, evaluation, and release architecture |
| Execution authority | GPT-5.6 Luna may execute only frozen conversion, packaging, benchmark, device-test, deployment, or artifact-transfer campaigns delegated by Sol; Luna may not change models, distillation data, quantization, device targets, runtimes, thresholds, tool contracts, or release decisions |
| Governance authority | ChatGPT defines mobile and edge architecture, distillation and quantization experiments, device capability claims, benchmark and promotion gates; Joseph Abbud approves consequential experiments, model/device support claims, budgets, publication, and release |
| Approved change | Defines a desktop-first local inference architecture centered on Apple-silicon Macs with 16 GB or more unified memory; makes a mobile app primarily a secure client to a paired local Mac or the approved Lambda-hosted runtime; retains offline mobile reference and optional bounded on-device inference; and establishes local model/runtime bake-offs, secure LAN pairing, explicit cloud routing, distillation and quantization ladders, local evidence and retrieval, native OCR, device-specific performance evaluation, artifact update and rollback, and the first owner-device validation matrix |


## 1. Purpose

DR-02-S03 originally emphasized a 2B–4B mobile student. DR-29 supersedes that supplement within the scope of deployment priority and primary product-model direction, while retaining its compatible evidence, OCR, quantization, privacy, explicit-routing, and capability-tier principles. The 2B–4B student remains an optional later path rather than the first product dependency.

The approved priority order is now:

```text
1. Apple-silicon Mac mini / MacBook local inference with 16 GB+ unified memory
2. Mobile app as a secure client to the paired local Mac
3. Mobile app as a secure client to the approved Lambda-hosted BSL runtime
4. Mobile offline reference and bounded OS-managed-model assistance
5. Project-owned full on-phone inference as an optional later capability
```

The primary local product target is therefore:

```text
selected compact 8B–12B BSL model
+ validated 4-bit or mixed-precision derivative
+ local deterministic tools and retrieval
+ Runtime Scholar Harness
+ Mac mini / Apple-silicon MacBook
```

The preferred mobile user experience is:

```text
native mobile app
+ camera and native OCR
+ local deterministic reference pack
+ secure paired API to the user's Mac when available
+ explicit Lambda API route when the local Mac is unavailable or insufficient
```

DR-29 converts that direction into an implementation-ready architecture. It defines:

- Which capabilities belong on the Mac, on the phone, or on Lambda;
- How the winning compact 8B–12B model is quantized and served locally on Apple silicon;
- How a phone discovers, pairs with, authenticates to, and revokes a local Mac scholar node;
- How mobile and desktop clients select local-Mac, Lambda, or on-device routes without hidden fallback;
- Which MLX, llama.cpp, OS-managed, and mobile-runtime paths enter the bake-off;
- How exact text, local evidence, Translation Nuance, notes, embeddings, and indexes are stored and served;
- How phone-camera Bible study uses native OCR and delegates deeper analysis to the paired Mac or Lambda;
- How later 2B–4B students and experimental phone-local models are distilled and quantized;
- How Mac mini, Apple-silicon MacBook, iPhone, Pixel, and later devices receive capability-specific support claims;
- How downloads, signatures, pairing, updates, rollback, deletion, privacy, memory pressure, thermal behavior, battery use, and network failure are handled.

On-phone custom inference is a bonus capability. It is not a prerequisite for the first useful local or mobile product.

Approval of DR-29 completes the scheduled preimplementation design-review series. Production implementation may begin only through the consolidated Sol build package derived from DR-01 through DR-29 and the governing owner/ChatGPT/Sol/Luna authority model.

## 2. Governing principle

> **Biblical Scholar Lab will prioritize a full local scholar experience on consumer Apple-silicon desktops and laptops before attempting to place the complete learned system on a phone. The mobile application will primarily be a secure research client to either a paired local Mac scholar node or the approved Lambda runtime, while retaining deterministic offline reference tools and optional bounded on-device assistance. Exact evidence, route identity, privacy state, and capability limits will remain explicit.**

The approved architecture favors:

```text
strong local Mac inference
+ deterministic local evidence
+ mobile-first interaction and capture
+ explicit local-Mac or Lambda routing
+ optional on-phone inference
```

over:

```text
make full phone inference an MVP dependency
+ accept a smaller model solely to fit the phone
+ obscure whether the answer came from phone, Mac, or cloud
```

A mobile result may be powered by the phone, the paired Mac, or Lambda. The interface must disclose which route actually produced it.

## 3. Local desktop, mobile client, and cloud are role-specific architectures

DR-29 distinguishes these model and execution roles:

```text
LOCAL_DESKTOP_COMPACT_MODEL
LOCAL_DESKTOP_SMALL_FALLBACK
LOCAL_SCHOLAR_NODE
MOBILE_CLIENT_TO_LOCAL_NODE
MOBILE_CLIENT_TO_LAMBDA
OS_MANAGED_ON_DEVICE_MODEL
PROJECT_CUSTOM_MOBILE_STUDENT
EXPERIMENTAL_FULL_PHONE_MODEL
REMOTE_COMPACT_OR_LARGE_MODEL
DETERMINISTIC_LOCAL_ONLY
```

They are not interchangeable.

### 3.1 Local desktop compact model

The primary local learned route is the winning compact product checkpoint from DR-11, ordinarily in the 8B–12B range, converted to a validated Apple-silicon runtime and precision.

Its intended scope is:

- Brief and Study mode;
- A bounded subset of Scholarly mode;
- Original-language and Translation Nuance workflows supported by local evidence;
- Local private-library analysis where rights permit;
- Local page-study reasoning after OCR and evidence resolution;
- A local API for paired mobile clients.

The local compact model remains subordinate to the same deterministic tools, evidence packets, verification, rights, and audit contracts as the Lambda-hosted system.

### 3.2 Local Scholar Node

The `LocalScholarNode` is the complete Mac-side product boundary. It contains:

```text
project-owned ModelInferenceGateway
Runtime Scholar Harness
local deterministic tools
local evidence and retrieval services
approved local model runtime
session and audit state
secure paired-client API
```

The model server itself is not exposed directly to mobile clients or the public network.

### 3.3 Mobile client

The mobile application is primarily:

- A native study and page-capture interface;
- A local deterministic reference client;
- A secure client to the paired Mac node on the local network;
- A secure client to the approved Lambda API when permitted;
- A route-selection and privacy-control surface.

The mobile application does not need a project-owned model to deliver the first high-quality mobile experience.

### 3.4 Optional on-device models

Apple Foundation Models, Gemini Nano, a 2B–4B project student, or an experimental larger phone model may later provide:

- Offline Brief responses;
- Local classification and structured extraction;
- Compact evidence-packet interpretation;
- Route selection;
- Limited offline Study workflows.

These capabilities are secondary and independently benchmarked.

### 3.5 Remote model

The compact or large Lambda-hosted system remains responsible for:

- Current scholarship;
- Difficult textual criticism;
- Large evidence packets;
- Broad multilingual synthesis;
- Complex multimodal analysis;
- Full-canon and long-context workflows;
- Tasks beyond the verified local-Mac capability.

Remote escalation remains explicit, rights-aware, privacy-aware, and user-visible.

## 4. Product execution modes

The product exposes these route and capability modes:

| Mode | Primary route | Evidence | Intended capability |
|---|---|---|---|
| `LOCAL_MAC_REFERENCE` | Deterministic local Mac tools | Full approved local evidence | Exact passage, reference, morphology, citations, and notes |
| `LOCAL_MAC_STUDY` | Quantized compact Mac model + local runtime | Local tools and retrieval | Primary local Brief and Study experience |
| `LOCAL_MAC_SCHOLARLY_BOUNDED` | Compact Mac model + full local runtime | Locally available evidence | Scholarly mode within measured model and evidence limits |
| `MOBILE_TO_LOCAL_MAC` | Native mobile client → paired Mac | Mac tools, model, and evidence | Preferred mobile route when the Mac is reachable |
| `MOBILE_TO_LAMBDA` | Native mobile client → approved Lambda API | Full remote runtime | Best available remote experience when allowed |
| `MOBILE_OFFLINE_REFERENCE` | Deterministic phone tools | Signed local mobile pack | Passage lookup, notes, references, and lexical search |
| `MOBILE_OFFLINE_BRIEF` | OS model or custom student | Compact phone packet | Optional bounded offline assistance |
| `EXPERIMENTAL_PHONE_LOCAL` | Quantized phone model | Device-specific | Research-only on-phone learned inference |

The first product milestone prioritizes `LOCAL_MAC_STUDY`, `MOBILE_TO_LOCAL_MAC`, and `MOBILE_TO_LAMBDA`.

No interface may describe one route as equivalent to another without a task-specific benchmark showing equivalence.

## 5. Device, node, and route capability profiles

Every local inference host receives an immutable:

```text
LocalNodeDeviceProfile
```

containing:

```text
manufacturer and model
hardware identifier
SoC and accelerator
unified or physical memory
OS version and build
runtime versions
available storage
power and thermal state
compute backends
supported operators and precision
network interfaces
security state
benchmark date
```

Every mobile client receives a:

```text
MobileClientProfile
```

covering:

```text
camera and OCR capabilities
local deterministic pack
OS-managed model availability
custom student availability
local-network permission
paired-node identities
cloud-route permissions
secure-storage state
accessibility capabilities
benchmark date
```

Each node and client then receives a capability-specific profile for:

```text
exact passage tools
local retrieval
Brief / Study / Scholarly support
original-language fidelity
Translation Nuance
citations and structured output
multimodal page study
maximum verified context
concurrency
local API service
mobile pairing
remote escalation
thermal and sustained-use class
```

A device name, memory amount, or successful model load is not by itself a capability claim.

## 6. Initial owner-device matrix

### 6.1 Mac mini M4, 16 GB — first mandatory target

The Mac mini is the first and highest-priority local-inference target.

Required routes:

```text
winning compact 8B–12B product model, quantized or mixed precision
4B-class local fallback
MLX-LM reference path where the architecture is supported
llama.cpp / Metal comparator where the architecture is supported
local deterministic evidence and retrieval
Local Scholar Node API
local desktop/web study interface
```

The Mac mini must prove that a consumer 16 GB Apple-silicon machine can deliver a useful local BSL Study experience before substantial phone-local model work begins.

### 6.2 Apple-silicon MacBook with 16 GB or more — second mandatory target

The second target is a consumer Apple-silicon MacBook with at least 16 GB unified memory.

It must test:

- The same model and runtime artifacts used on the Mac mini where possible;
- Battery operation and plugged-in operation;
- Thermal throttling and sustained use;
- Sleep, wake, network transition, and cancellation;
- Local Scholar Node operation for a paired phone;
- Storage and model-download behavior.

The owner’s existing Intel MacBook Pro remains primarily the Thunderbolt archive and campaign-controller host under DR-23/DR-28. It is not the baseline consumer-inference target.

### 6.3 iPhone 15 Pro and Pixel 10 Pro — mobile-client targets

The first mandatory phone requirement is not full project-owned inference. It is a high-quality native client that can:

```text
capture and preprocess a page
use native OCR
run local deterministic reference tools
pair securely with a Local Scholar Node
stream a local-Mac answer
invoke the approved Lambda API when permitted
show the active route and privacy state
cancel, retry, and fall back explicitly
```

Optional phone-local routes include Apple Foundation Models, Gemini Nano, 2B–4B students, and later experimental larger models. They do not block the initial mobile product.

## 7. Desktop-first application and Local Scholar Node architecture

The initial local product consists of:

```text
BSL desktop/web study interface
        ↓
project-owned local API
        ↓
Scholar Runtime Core
        ↓
ModelInferenceGateway
        ↓
MLX / llama.cpp / approved runtime adapter
        ↓
selected local model
```

The same local node also exposes deterministic tools, retrieval, evidence inspection, notes, audit receipts, and page-study workflows.

The first desktop UI may use the approved TypeScript/React/Vite product client from DR-28 against a loopback API. A later native macOS wrapper or SwiftUI client may be added if it materially improves model lifecycle, camera, accessibility, or consumer distribution.

The model runtime, PostgreSQL, artifact archive, and evidence services are not exposed directly to client applications.

The local node runs in these network states:

```text
LOOPBACK_ONLY
PAIRING_ENABLED
PAIRED_LAN_SERVICE
PAUSED
REVOKED
```

`LOOPBACK_ONLY` is the default.

## 8. Secure mobile-to-Mac API boundary

The project introduces a:

```text
LocalScholarNodeGateway
```

between mobile clients and the Mac runtime.

### Discovery

On Apple platforms, the Mac may advertise an approved Bonjour service and the iOS client may browse for it through Network framework. Bonjour is used only for discovery; it does not confer trust or authorization.[^bonjour-network] The iOS app must also provide the required local-network privacy explanation.[^local-network-privacy]

### Pairing

Pairing requires explicit action on both devices and uses a one-time QR code or short authentication code to establish per-device credentials.

The resulting relationship must include:

```text
paired device identity
Mac node identity
public-key pin or client certificate
allowed user/profile
capability scope
created and last-used times
revocation state
```

### Transport and authentication

The initial approved design requires:

- TLS 1.3 or the strongest platform-supported approved equivalent;
- Mutual authentication or an equivalently strong per-device proof;
- Certificate or public-key pinning;
- Short-lived request/session tokens after pairing;
- Replay protection;
- Per-device revocation;
- No plaintext local API;
- No unauthenticated health or inference endpoint exposing sensitive state.

### Network exposure

Version one supports same-LAN access only.

It does not require:

- Router port forwarding;
- A publicly reachable Mac endpoint;
- A vendor relay;
- Unreviewed VPN or tunneling software.

When the phone is away from the paired Mac’s local network, the approved remote route is Lambda rather than direct public exposure of the Mac.

### Authority boundary

The mobile client calls only the project-owned gateway. It never receives direct PostgreSQL, archive, model-server, shell, or unrestricted tool access.

Every request produces a route receipt identifying whether execution occurred:

```text
ON_PHONE
PAIRED_LOCAL_MAC
LAMBDA_CLOUD
```

No fallback among these routes is silent.

## 9. Apple-silicon Mac execution routes

### 9.1 MLX-LM reference candidate

`MLX-LM` is the provisional first Apple-silicon runtime candidate because it is designed for LLM generation and fine-tuning on Apple silicon and supports model quantization.[^mlx-lm]

The project will not call MLX directly from the product UI. MLX remains an adapter behind the project-owned ModelInferenceGateway.

Required tests include:

- Candidate-model architecture support;
- Conversion and weight equivalence;
- Structured output and tool syntax;
- Original-language fidelity;
- Context and cache behavior;
- Cancellation and streaming;
- Memory and sustained throughput;
- Multimodal support where applicable;
- Quantized-parent regression.

### 9.2 llama.cpp / Metal comparator

`llama.cpp` is the mandatory portable comparator where the selected model architecture can be converted faithfully to GGUF. It treats Apple silicon as a first-class target through Metal and can expose an OpenAI-compatible local server.[^llama-cpp]

The project uses its own gateway and policies above `llama-server`; the generic server is not exposed as the product boundary.

### 9.3 Optional Apple-native runtimes

Core AI, Core ML, or another Apple-native runtime may enter later when it supports the exact selected model and passes the same conformance suite. No native framework receives preference merely because it is provided by the platform vendor.

## 10. Mobile client and optional on-device routes

### 10.1 Native clients

The first mobile clients remain:

```text
iOS: Swift + SwiftUI
Android: Kotlin + Jetpack Compose
```

They own camera capture, OCR integration, route disclosure, pairing, streaming presentation, local reference tools, secure storage, accessibility, cancellation, and retry UX.

### 10.2 OS-managed models

Apple Foundation Models and Gemini Nano remain optional bounded routes for:

- Classification;
- Structured extraction;
- Brief summaries;
- Offline route selection;
- Small evidence-packet interpretation.

They are not required for the first mobile release and do not replace the Mac or Lambda scholar runtimes.

### 10.3 Project-owned mobile students

A 2B–4B student becomes eligible only after the desktop-local system and mobile API client are operational. It is intended to improve offline or privacy-constrained phone use, not to define the project’s first consumer experience.

### 10.4 Phone-local larger models

A quantized 8B–12B phone route remains research-only. It cannot delay the desktop-local or API-client product path.

## 11. Local model candidate set

### 11.1 Primary local compact candidates

The primary desktop bake-off uses the winning compact product candidates from DR-11:

```text
Qwen3.5-9B
Gemma 4 12B instruction-tuned
Ministral 3 8B Instruct or Reasoning
```

Each candidate receives:

- High-precision reference evaluation;
- 8-bit and 4-bit/mixed-precision conversion where supported;
- MLX and/or llama.cpp runtime evaluation where supported;
- Local tool, structured-output, Greek/Hebrew, Translation Nuance, page, and citation tests;
- 8K, 16K, and optional 32K context tests;
- Mac mini and Apple-silicon MacBook physical evaluation.

The goal is to select one compact local product model—not to force every family onto every runtime.

### 11.2 Small local fallback and optional mobile-student candidates

```text
Gemma 4 E2B / E4B
Qwen3.5-2B / 4B
Ministral 3 3B
```

These candidates serve as:

- Low-memory Mac fallback;
- Fast local route;
- Potential mobile student;
- Distillation target;
- Offline Brief-mode model.

They are no longer the presumed primary product model.

### 11.3 OS-managed model comparators

Apple Foundation Models and Gemini Nano remain separately versioned provider routes. They are compared on bounded tasks but cannot win the project-owned checkpoint bake-off.

## 12. Model and runtime selection may differ by role

The architecture may select different winners for:

```text
Mac mini / MacBook primary local model
Mac low-memory fallback
Mac serving runtime
mobile OS-managed route
mobile custom student
Lambda compact model
Lambda large fallback
embedding and reranking
multimodal page front end
```

A single family is preferred only when performance is practically tied and family coherence materially reduces conversion, deployment, and maintenance burden.

The valid first product outcome may be:

```text
9B–12B model on Mac
native phone client with no project model
larger model on Lambda
```

That is an intended architecture—not a failure to achieve on-phone inference.

## 13. The teacher is a verified system—not one model

Distillation will not simply ask a larger model to answer questions and train the student to imitate every output.

The canonical teacher is:

```text
approved foundation model or routed model set
+ deterministic passage and linguistic tools
+ Translation Nuance Semantic Kernel
+ retrieval and citations
+ Context Composer
+ Runtime Scholar Harness
+ structure-first verification
+ reviewed P0/P1 behavior
```

A teacher trace is eligible only when:

- The exact evidence packet is known;
- Tool calls are valid;
- Quotations and citations verify;
- Source distinctions are correct;
- The response contains no hard failure;
- Review status is recorded;
- Rights allow the intended student-training operation.

The student should learn the verified behavior of the system rather than the unverified intuition of one large checkpoint.


## 14. Distillation data partitions

Distillation records are partitioned by review authority:

```text
DIST-P0_DETERMINISTIC_AND_OPERATIONAL
DIST-P1_SOURCE_VERIFIABLE_SCHOLARLY_BEHAVIOR
DIST-P2_SME_VALIDATED_SPECIALIST_BEHAVIOR
DIST-PRIVATE_USER_EXCLUDED
DIST-RESTRICTED_RIGHTS_GATED
```

The initial mobile student may train on:

- Approved P0;
- Validated P1;
- Public/open corpus and tool traces;
- Approved preference behavior;
- Synthetic page and OCR workflows;
- General multilingual and multimodal replay.

It may not train on unreviewed P2, private user sessions, private benchmark gold, or rights-ineligible evidence.


## 15. Distillation objective ladder

Distillation follows an explicit ladder.

### `DIST-0_DIRECT_STUDENT_POSTTRAIN`

Train the student directly on the approved mobile SFT and preference curriculum without teacher-specific targets.

This is the mandatory causal baseline.

### `DIST-1_VERIFIED_SEQUENCE_DISTILLATION`

Train on complete verified student-facing responses generated by the teacher system.

Sequence-level distillation is architecture- and tokenizer-independent and has a long research precedent.[^sequence-kd]

### `DIST-2_TOOL_AND_STRUCTURE_DISTILLATION`

Teach:

- Task classification;
- Tool selection;
- Structured arguments;
- Evidence handles;
- Citation placement;
- Abstention and escalation;
- Brief and Study rendering;
- Compaction and rehydration decisions.

The targets are typed records and observable tool traces—not private chain-of-thought.

### `DIST-3_DISTRIBUTION_DISTILLATION`

When teacher access and tokenizer compatibility permit, compare token-distribution objectives such as forward KL, reverse KL, or approved variants.

MiniLLM provides evidence that reverse-KL-style distillation can improve generative student behavior relative to ordinary forward-KL baselines, but it does not establish that reverse KL is the correct objective for this project.[^minillm]

### `DIST-4_ON_POLICY_DISTILLATION`

The student generates its own attempts; the verified teacher supplies distributional or correction targets on the student’s visited states.

This may reduce exposure mismatch but is more expensive and remains separately gated.

### `DIST-5_REPRESENTATION_OR_RELATION_DISTILLATION`

Where teacher and student architectures permit, distill:

- Hidden representations;
- TNC auxiliary heads;
- Alignment and lineage relations;
- Evidence-fitness scores;
- Calibrated abstention.

This is most defensible inside one compatible model family.

### `DIST-6_MULTI_TEACHER_ROUTED_DISTILLATION`

A routed teacher set may contribute distinct strengths:

- Large scholarly synthesis;
- Ancient-language analysis;
- Multimodal page understanding;
- Safety and scope;
- Multilingual answers.

The teacher identity and selection rule remain explicit for every example.

No later tier replaces the earlier baselines.


## 16. Distillation does not transfer authority

The student may learn to:

- Use an exact passage tool;
- Identify a translation-choice issue;
- Ask for missing evidence;
- Present a concise source-grounded explanation;
- Escalate to a larger route.

It may not become the authoritative repository of:

- Exact biblical text;
- Current scholarship;
- Manuscript support;
- Rights;
- User-private notes;
- Benchmark gold;
- Scholarly consensus.

Distillation of a fact does not remove the need for runtime verification when the product presents that fact as exact or current.


## 17. No hidden chain-of-thought distillation

The project does not require or retain private chain-of-thought from teachers.

Permitted supervision includes:

- Final structured answer candidates;
- Tool calls and results;
- Evidence selections;
- Claim/evidence links;
- Brief concise rationale;
- Error categories;
- Verification and repair outcomes;
- Explicit uncertainty;
- Accepted and rejected response pairs.

This is sufficient for observable scholarly behavior while preserving the project’s chain-of-thought boundary.


## 18. Quantization artifact hierarchy

Every model derivative belongs to one quantization class:

```text
Q0_HIGH_PRECISION_MASTER
Q1_8BIT_REFERENCE
Q2_MIXED_8_6BIT
Q3_4BIT_POST_TRAINING
Q4_4BIT_OR_MIXED_QAT
Q5_MOBILE_RUNTIME_SPECIALIZED
Q6_SUB4BIT_EXPERIMENTAL
```

### Q0 — High-precision master

The BF16 or approved parent artifact remains the scientific master.

### Q1 — 8-bit reference

Used to establish a low-risk compression baseline and identify runtime/conversion defects.

### Q2 — Mixed 8/6-bit

Provides an intermediate quality/size path where supported.

### Q3 — 4-bit PTQ

The first serious weight-footprint candidate.

### Q4 — QAT or compression-aware fine-tuning

Used when PTQ fails the capability or runtime targets. Apple’s Core AI Optimization explicitly supports PTQ, calibration-based compression, and compression-aware fine-tuning, with QAT generally needed for the most aggressive compression.[^apple-coreai-opt]

### Q5 — Mobile-runtime-specialized

Runtime-specific schemes such as Gemma mobile QAT, optimized KV caches, AOT-compiled Tensor artifacts, Core AI-specialized models, or LiteRT-LM-specific packages.

### Q6 — Sub-4-bit experimental

2-bit, 3-bit, or highly mixed schemes are research-only until they pass the full hard-failure and multilingual/ancient-script suite.


## 19. Quantization specifications are component-aware

A `QuantizationSpecification` records precision separately for:

```text
token embeddings
language-model blocks
attention and DeltaNet components
feed-forward blocks
normalization
output head
vision encoder
multimodal projector
audio encoder
draft or MTP model
KV cache
activations
auxiliary heads
```

The project will not quantize every parameter uniformly merely because a converter exposes one global switch.

The starting sensitivity hypothesis is:

- Norms, numerically sensitive accumulations, and selected control/output components remain at higher precision;
- The bulk of large matrix weights may move to 4-bit or another validated representation;
- Embeddings and the output head receive explicit ancient-language and tool-syntax sensitivity testing;
- Vision/audio components are quantized independently;
- KV-cache quantization receives separate long-context and citation tests.

The sensitivity map is measured and versioned.


## 20. Calibration corpus

Quantization calibration must include the declared deployment workload, not generic English text alone.

The mandatory calibration strata are:

```text
English Brief and Study answers
Spanish and French canaries
Polytonic Greek
pointed and unpointed Hebrew
Biblical Aramaic and scholarly transliteration
canonical references and tool JSON
citation and bibliography syntax
Translation Nuance evidence packets
scope and refusal cases
page OCR and image/text examples where applicable
long and compacted context examples
```

The calibration corpus is separate from the final private benchmark and is rights-approved for the compression operation.


## 21. Quantization-aware training order

The baseline order is:

```text
freeze high-precision student
→ PTQ screen
→ identify sensitive components and failures
→ mixed-precision PTQ
→ QAT/compression-aware fine-tuning if required
→ runtime-specific conversion
→ device benchmark
```

We will not begin with expensive QAT before a PTQ screen demonstrates the need.

Official Gemma 4 mobile QAT checkpoints are valid baselines and teacher/student artifacts, but a project-adapted checkpoint still needs its own compression and validation path.[^gemma4-mobile-qat]


## 22. Runtime-specific derivatives remain distinct

Possible artifacts include:

```text
LITERTLM_MODEL
CORE_AI_AIMODEL
CORE_ML_MODEL
TENSOR_G5_AOT_MODEL
GGUF_DIAGNOSTIC_MODEL
APPLE_FOUNDATION_MODEL_ROUTE_CONFIG
GEMINI_NANO_ROUTE_CONFIG
```

They may derive from one common master but are not interchangeable.

Every artifact records:

- Converter and revision;
- Operator mapping;
- Unsupported or custom operations;
- Precision and compression;
- Runtime and target device;
- Numerical comparison;
- Capability benchmark;
- Packaging and signature;
- Rollback parent.

A route does not inherit another route’s benchmark results.


## 23. Local evidence architecture

### 23.1 Mac Local Scholar Node

The Mac node uses the approved DR-28 architecture:

```text
PostgreSQL authoritative metadata and assertions
Thunderbolt BSL-Archive / BSL-Private where applicable
Parquet and DuckDB analytical projections
hybrid exact / lexical / vector retrieval
project-owned tools and evidence packets
```

The local compact model does not replace these systems.

### 23.2 Consumer local node packaging

A later broadly distributed consumer node may use signed, versioned local evidence packs and a smaller packaged store rather than requiring the complete owner research database. That projection remains derived from the same authoritative contracts.

### 23.3 Mobile client evidence

The mobile app stores only the bounded evidence needed for offline reference and capture workflows:

```text
SQLite exact metadata and local notes
signed public/open passage and reference pack
optional lexical index
optional compact embedding index
pairing and route state
```

When paired, the Mac remains the primary evidence and learned-inference provider. The phone does not need to duplicate the entire local research library.

## 24. Local and mobile retrieval

The Mac node uses DR-28’s full hybrid retrieval path:

```text
exact identifiers and canonical references
→ rights, tenant, language, date, method, and source filters
→ lexical, lemma, morphology, and citation retrieval
→ dense or multi-vector candidate retrieval
→ reranking and dependence audit
→ exact evidence-span acquisition
```

The provisional embedding and reranker bake-off remains governed by DR-28.

The mobile client may use:

- Local exact and lexical search for offline reference;
- The paired Mac retrieval API;
- The approved Lambda retrieval API;
- An optional small mobile embedding index when it demonstrates value.

The first mobile product does not require a full on-device semantic index.

## 25. Native OCR before learned page analysis on the phone

The preferred mobile page workflow is:

```text
phone camera / document capture
→ native document detection and OCR
→ local page-region and passage candidates
→ exact local or Mac passage resolution
→ Mac or Lambda page-evidence analysis
→ verified response streamed to the phone
```

This uses the phone for the tasks it performs especially well—capture, image preprocessing, OCR, and interaction—without requiring the complete multimodal scholar model to reside on the phone.

The user may choose whether the full image, selected crops, OCR text, or only a resolved passage packet is transmitted to the paired Mac or Lambda, subject to rights and privacy policy.

Any on-device VLM remains an optional comparator. Visible pixels, OCR, VLM observations, canonical text, and user corrections remain separate evidence layers under DR-14.

## 26. Edge and mobile page evidence packets

A mobile page workflow produces a versioned packet containing:

```text
source image identity
local/private state
orientation and crop
page regions
OCR hypotheses and alternatives
language and script
edition and passage candidates
user corrections
route decision
transmitted image/crops/text
receiving Mac or Lambda endpoint
returned evidence and answer receipt
```

The paired Mac or Lambda converts that packet into the authoritative DR-14 `MultimodalPageEvidencePacket` where deeper analysis is needed.

The product cannot claim that a remote model inspected a region that the mobile client did not transmit.

## 27. Context policy by route

### Local Mac

Initial verified profiles are:

```text
MAC_CTX_8K
MAC_CTX_16K
MAC_CTX_32K_EXPERIMENTAL
```

The first product target is a focused 8K–16K Study packet. Full-New-Testament local context remains a measured experiment, not a requirement.

### Mobile client to Mac or Lambda

The phone transmits the structured request, active study state, necessary image evidence, and user-authorized private material. Context composition occurs on the selected scholar node.

### On-device phone

Initial profiles remain:

```text
PHONE_CTX_4K
PHONE_CTX_8K
PHONE_CTX_16K_EXPERIMENTAL
```

On-device context is optimized for Brief and bounded Study work. A phone does not need a full-canon prompt when it can use exact local tools or an API route.

## 28. Session, personalization, and cross-device continuity

The authoritative session remains structured under DR-15 and DR-16.

A paired phone may synchronize approved bounded state with the Mac node, including:

```text
active passage and edition
canon and language profile
answer depth
open research questions
user corrections
selected notes
route and privacy preferences
```

The system must not synchronize private source content merely because two devices are paired.

Cross-device state changes are:

- Versioned;
- Conflict-detectable;
- User-correctable;
- Rights- and privacy-filtered;
- Revocable with the device pairing.

A mobile-generated summary cannot overwrite the Mac’s authoritative evidence or session state without validation.

## 29. Route selection and escalation

The default route order is:

```text
1. paired Local Scholar Node, when reachable and sufficient
2. approved Lambda route, when allowed and necessary
3. on-device bounded route, when offline or explicitly selected
4. deterministic-only response or explicit abstention
```

The user may select:

```text
PREFER_LOCAL_MAC
ASK_BEFORE_CLOUD
ALLOW_LAMBDA_FOR_PUBLIC_EVIDENCE
ALLOW_LAMBDA_FOR_THIS_SESSION
ON_DEVICE_ONLY
DETERMINISTIC_ONLY
```

A route decision considers:

- Model and evidence capability;
- Current local-node availability;
- Question complexity;
- Language and modality;
- Rights and privacy;
- User preference;
- Network state;
- Latency and cost;
- Current scholarship requirements.

The interface always discloses the route.

A paired Mac failure may fall back to Lambda only under the user’s active route policy. It may not silently transfer private material to the cloud.

## 30. Offline guarantees

The first mobile offline guarantee is deterministic rather than model-dependent.

The app should retain, where rights permit:

- Passage and reference lookup;
- Saved notes;
- Selected public/open translations;
- Basic lexical and morphology records;
- Previously downloaded public-safe evidence;
- OCR capture and local staging;
- Pending requests that can be sent later.

An OS-managed or project-owned phone model may add offline Brief capability, but offline learned inference is not required for the initial mobile UX.

The Mac local node should remain fully usable without Internet access for locally installed models and evidence, except for current scholarship or other explicitly remote resources.

## 31. Local model, client, and evidence distribution

Desktop models, mobile optional models, and evidence packs are separately signed post-install artifacts rather than mandatory application-bundle payloads where platform rules permit.

The owner research node may activate artifacts directly from the authoritative Thunderbolt archive after verification. A broadly distributed consumer node downloads an approved public/research release artifact through the project update service.

Every downloadable bundle includes:

```text
artifact and model identity
compatible app/runtime/OS/device matrix
size and free-space requirement
license and rights
signature and hashes
capability profile
context limits
migration and rollback
minimum power/network conditions
retention and deletion behavior
```

The artifacts remain separate:

```text
desktop compact model
small desktop fallback
optional mobile student
local evidence pack
mobile reference pack
embedding/reranker artifact
vector index
OCR or multimodal component
runtime adapter
prompt/policy bundle
```

A user may delete optional models or evidence packs without deleting private notes. Removing a paired Mac node from a phone removes its credentials and cached private session state without erasing the Mac’s own authorized data.

## 32. Local-edge and mobile artifact records

DR-29 adds these canonical contracts to DR-28’s Contract Registry:

```text
LocalNodeDeviceProfile
LocalNodeCapabilityProfile
MobileClientProfile
MobileCapabilityProfile
LocalScholarNodeArtifact
LocalScholarNodeGatewayConfiguration
PairedDeviceIdentity
PairingReceipt
PairingRevocationReceipt
EdgeRouteSpecification
LocalModelArtifact
MobileModelArtifact
QuantizationSpecification
QuantizedModelArtifact
DistillationSpecification
DistillationDatasetSnapshot
DistillationRun
StudentModelArtifact
LocalEvidencePack
MobileEvidencePack
LocalVectorIndexSnapshot
MobileVectorIndexSnapshot
NativeOCRRouteSpecification
EdgeInferenceReceipt
RouteSelectionReceipt
DeviceBenchmarkCampaign
DeviceBenchmarkRun
ThermalEnergyProfile
LocalEdgeReleaseBundle
MobileClientReleaseBundle
UpdateManifest
RemoteEscalationReceipt
```

Every local or mobile release is reproducible from its parent model, data, conversion, runtime, pack, prompt, policy, route, and device identities.

## 33. Model, node, client, and pack rollout and rollback

Local models, Local Scholar Node builds, mobile clients, and evidence packs use staged channels:

```text
DEVELOPMENT
OWNER_DEVICE_ALPHA
PRIVATE_REVIEW
EXPERT_PREVIEW
PUBLIC_PREVIEW
STABLE_LOCAL_DESKTOP
STABLE_MOBILE_CLIENT
STABLE_OPTIONAL_MOBILE_MODEL
REVOKED
```

An `UpdateManifest` binds:

- Current and target versions;
- Download and installed size;
- Device and route compatibility;
- Database or pack migration steps;
- Required benchmark evidence;
- Rollback artifact;
- Pairing compatibility;
- Revocation and kill-switch state;
- Signature and hashes.

An update does not replace the known-good local artifact until download, signature, integrity, migration, model-load, API, and bounded scholarly smoke tests pass.

The node and client retain a compatible rollback path when storage permits.

OS-managed model routes are reevaluated when an OS update changes the observable model or capabilities.

## 34. Local-edge and mobile security and privacy

The architecture inherits DR-10, DR-27, and DR-28 and adds these rules:

- Local model, runtime, and evidence packs are signed and hash verified;
- Model servers bind to loopback and are reachable only through the project gateway;
- LAN serving is disabled until explicit pairing is enabled;
- Pairing establishes per-device credentials and supports immediate revocation;
- Bonjour or other discovery metadata contain no study content, user identity, model prompt, or private source data;
- Mobile-to-Mac transport is encrypted and authenticated;
- Private notes, uploads, and session state remain in approved encrypted storage;
- User-private data never enter shared model or vector packs;
- Cross-user and cross-pairing cache reuse is prohibited;
- The client never embeds Lambda, archive, model-provider, or database credentials;
- Local tools remain narrow and read-only by default;
- OCR text, QR codes, document instructions, and retrieved content have no instruction authority;
- No public router port, automatic UPnP mapping, or internet-facing Mac server is authorized;
- Remote escalation obeys the exact provider-route and consent state;
- Crash and performance telemetry contain no raw study content by default;
- Revoking a device invalidates active sessions, cached credentials, and future access without relying on the client’s cooperation.

Jailbroken, rooted, or otherwise materially compromised devices may receive a reduced capability profile when the platform can detect the condition.

## 35. Local and mobile support and release claims

A node/client/runtime/model combination receives one of:

```text
VALIDATED_LOCAL_STUDY
VALIDATED_LOCAL_SCHOLARLY_BOUNDED
VALIDATED_MOBILE_TO_LOCAL
VALIDATED_MOBILE_TO_LAMBDA
VALIDATED_OFFLINE_REFERENCE
VALIDATED_OPTIONAL_ON_DEVICE
EXPERIMENTAL
UNSUPPORTED
BLOCKED_BY_OS_OR_RUNTIME
BLOCKED_BY_RIGHTS
REVOKED
```

Support is capability-specific:

```text
Brief
Study
Scholarly
multilingual
original-language
page study
Translation Nuance
citations
local API
mobile pairing
offline
cloud escalation
```

A Mac may be validated for Study mode but not difficult Scholarly synthesis. A phone may be validated as a client without any project-owned model installed. Neither condition is described misleadingly as generic full support.

## 36. Performance and resource measurement

### 36.1 Mac mini / MacBook local inference

Every local-node benchmark records:

```text
cold and warm model load
first-token latency
prefill throughput
decode throughput
peak unified memory
memory-pressure and swap behavior
model and index storage
30-minute sustained throughput
thermal state
power use on MacBook
context length and cache size
OCR, retrieval, tool, and verification latency
local API concurrency
cancellation and recovery
```

Initial planning targets for the primary 16 GB local compact route are:

```text
warm p50 time to first token <= 3 seconds
warm p95 time to first token <= 6 seconds
p50 decode >= 8 tokens/second
30-minute sustained run without process termination or critical memory pressure
sustained decode >= 65% of the initial stable rate
verified 8K Study context
16K Study context as the preferred target
```

These are product targets, not claims that every 8B–12B candidate will satisfy them.

### 36.2 Mobile client experience

The mobile-to-Mac path records:

```text
service discovery time
pairing success and revocation
local-network connection latency
request upload time
stream-start overhead beyond model TTFT
interruption and reconnect
route fallback behavior
image/OCR transfer cost
battery use attributable to capture and networking
```

The initial target is that the local API adds no more than 300 ms p50 overhead before model generation on a healthy local network.

### 36.3 On-phone inference

Phone-local performance remains separately reported and does not block the initial Mac-local/mobile-client release.

## 37. Local edge and mobile-client capability benchmark

DR-20 gains local-edge and client-server conditions:

```text
high-precision parent on reference hardware
quantized local Mac model
MLX reference path
llama.cpp / Metal comparator
Local Scholar Node direct client
mobile client → Local Scholar Node
mobile client → Lambda
mobile deterministic-only route
optional OS-managed phone model
optional custom mobile student
```

Required benchmark areas include:

- Exact reference and passage tools;
- Greek/Hebrew and transliteration fidelity;
- Translation Nuance within declared local scope;
- Tool calls and structured output;
- Citation and source identity;
- Page OCR and scripture/paratext separation;
- Multilingual answer retention;
- Context and compaction;
- Local-network pairing and route disclosure;
- Local-versus-cloud answer parity;
- Quantization and serving-engine deltas;
- Mac memory, sustained latency, and power behavior;
- Mobile capture, streaming, offline reference, and network failure.

No one aggregate may conceal a route-specific hard failure.

## 38. Parent-relative gates

### Quantized local Mac derivative

A quantized desktop derivative ordinarily requires:

- No new `HF-1` critical hard failure;
- No material increase in `HF-2` major failures;
- No more than a two-point absolute drop on the declared P0/P1 local subset, or an approved case-family-equivalent margin;
- No material worst-language, ancient-script, citation, tool, or page-study regression;
- Verified improvement in memory, load time, throughput, or storage;
- Successful 30-minute physical-device stability;
- Working Local Scholar Node API and cancellation.

### Distilled small model

A 2B–4B student ordinarily requires:

- A meaningful improvement over the undeveloped student baseline;
- Correct escalation outside its support tier;
- No new critical hard failures;
- Demonstrated value as a low-memory Mac fallback or optional phone route.

A student is no longer required for the first desktop-local or mobile-client MVP.

## 39. Device- and route-specific gates

The promotion order is:

```text
reference runtime checks
→ Mac mini M4 physical tests
→ Apple-silicon MacBook 16 GB+ physical tests
→ Local Scholar Node API and pairing tests
→ iPhone and Pixel client tests
→ Lambda fallback tests
→ optional on-device-model tests
→ update, rollback, deletion, privacy, and accessibility tests
→ ChatGPT review
→ owner approval
```

A simulator cannot establish actual unified-memory pressure, Metal behavior, thermal throttling, battery life, local-network permissions, camera/OCR quality, or OS-managed-model behavior.

## 40. Optional full-model phone experiments

Full learned inference on a phone is a bonus branch, not an MVP prerequisite.

A quantized 8B–12B phone experiment becomes eligible only after:

- The Mac-local compact model is operational;
- The mobile-to-Mac and mobile-to-Lambda clients are stable;
- The exact model has a supported phone runtime;
- The experiment has a bounded device, thermal, memory, and quality hypothesis.

The first likely target remains the higher-memory Pixel route. The iPhone 15 Pro route is optional and not required.

Any phone-local experiment must report:

- Installed size;
- Load success and time;
- Peak memory;
- Sustained decode;
- Thermal and battery behavior;
- OS memory-pressure behavior;
- Ancient-language, citation, and tool fidelity;
- Comparison with the local-Mac and Lambda routes.

A model that merely loads does not qualify as a usable product route.

## 41. OS-managed mobile model evaluation

Apple Foundation Models and Gemini Nano remain optional client-side comparators for:

- Classification;
- Structured output;
- Local route selection;
- Brief explanation;
- Small evidence-packet interpretation;
- Scope and safety;
- OCR-adjacent tasks.

They are evaluated after the mobile API client exists, because they are enhancements to the client rather than the foundation of the initial mobile product.

Their provider-managed policies, quotas, and model revisions remain separate and auditable. The Runtime Scholar Harness remains the project authority.

## 42. Quantization, local serving, and optional distillation order

The evidence-gated order is:

```text
LE-00 local Mac and runtime capability probe
LE-01 quantized compact-model screen on Mac mini
LE-02 local evidence, tools, retrieval, and Runtime Scholar integration
LE-03 Local Scholar Node API and desktop UX
LE-04 mobile client pairing and local-Mac streaming
LE-05 Lambda API route and explicit fallback
LE-06 Mac mini / MacBook physical benchmark and selected local release candidate
LE-07 mobile offline reference and OS-managed-model baselines
LE-08 optional 2B–4B distillation and phone-runtime bake-off
LE-09 optional full-model phone experiment
```

Distillation is performed only if it repairs a measured low-memory, latency, offline, or phone-capability deficit.

## 43. Implementation gates

Sol will implement DR-29 through:

```text
LE-00 — Local-edge contracts, Mac and phone capability probes,
        route identities, and benchmark fixtures

LE-01 — Local Scholar Node shell, loopback API,
        desktop/web client integration, and lifecycle controls

LE-02 — MLX-LM reference adapter and llama.cpp / Metal comparator,
        conversion, quantization, streaming, cancellation, and receipts

LE-03 — Compact 8B–12B local model bake-off on the Mac mini,
        with 4B fallback and parent-relative conformance

LE-04 — Local evidence, retrieval, page, Translation Nuance,
        session, compaction, and audit integration

LE-05 — Secure LAN service discovery, explicit pairing,
        TLS/mutual authentication, device revocation, and route receipts

LE-06 — Native iOS and Android clients, camera/OCR,
        deterministic offline reference, streaming, and accessibility

LE-07 — Approved Lambda API route, privacy disclosure,
        network failure, cancellation, and explicit fallback

LE-08 — Mac mini M4 and Apple-silicon MacBook 16 GB+
        physical performance, memory, thermal, power, and stability suite

LE-09 — Apple Foundation Models and Gemini Nano bounded client adapters

LE-10 — Optional 2B–4B distillation, PTQ/QAT,
        mobile runtime, embedding, and offline Study experiments

LE-11 — Optional Pixel-first full-model phone experiment

LE-12 — Security, update, rollback, deletion, telemetry,
        pairing revocation, incident, and privacy conformance

LE-13 — Expert-preview local-desktop and mobile-client release candidate
```

Every gate receives one accountable Sol root turn, PR, consolidated handoff, ChatGPT review, and owner merge or redesign decision.

## 44. Sol and Luna authority

### Sol may

- Implement native mobile apps and shared contracts;
- Implement model/runtime adapters;
- Implement distillation and quantization pipelines;
- Implement model and evidence pack downloads, signatures, rollback, and deletion;
- Implement device benchmarking and reports;
- Diagnose runtime and conversion defects;
- Recommend design changes with evidence.

### Sol may not

- Select the student, teacher, quantization, runtime, device support tier, or performance threshold independently;
- Add private or unreviewed data to distillation;
- Change the declared mobile capability;
- Hide unsupported routes or fallback;
- Treat an OS-managed model as a reproducible project checkpoint;
- Promote a device based on simulator results.

### Luna may

- Execute frozen conversion, package, benchmark, device-test, and artifact-validation campaigns delegated by Sol;
- Collect performance, thermal, battery, memory, and correctness evidence;
- Operate Lambda teacher-generation or student-training campaigns approved under DR-25.

### Luna may not

- Change code, prompts, data, teacher, student, quantization, runtime, device, context, threshold, or route;
- Interpret or promote results.


## 45. Principal hard failures

DR-29 treats the following as hard failures:

- Claiming the custom project model runs through Apple Intelligence merely because the device supports Apple Intelligence;
- Treating an OS-managed model as immutable across OS updates;
- Claiming a quantized or distilled derivative inherited the parent benchmark without rerunning it;
- Hiding a remote escalation behind an offline or on-device label;
- Sending private content remotely without the approved disclosure and route;
- Treating native OCR output as exact scripture without deterministic lookup;
- Silently replacing visible page evidence with expected canonical wording;
- Using full-New-Testament context on a phone without an approved experiment;
- Allowing a mobile vector index to become source authority;
- Training on user-private mobile sessions by default;
- Distilling unverified teacher hallucinations;
- Distilling or displaying private chain-of-thought;
- Using unreviewed P2 specialist judgments as mobile gold;
- Uniformly quantizing sensitive components without evidence;
- Hiding ancient-language, tool, citation, or safety regressions under an average score;
- Shipping an unsigned or unverified model/evidence pack;
- Updating a model without rollback;
- Using simulator performance as proof of physical-device support;
- Running a local tool with unrestricted filesystem, shell, or network authority;
- Claiming background Gemini Nano support where the platform blocks background inference;
- Promoting the 9B phone experiment as the default product path without owner approval.


## 46. Decisions approved by DR-29

Approval establishes that:

1. The first local learned-inference priority is the Mac mini M4 with 16 GB unified memory.
2. Apple-silicon MacBooks with 16 GB or more are the second consumer local target.
3. The primary local model is the winning compact 8B–12B product candidate, quantized or mixed precision if it passes parent-relative gates.
4. A 2B–4B model is a fallback and optional mobile student—not the presumed primary product model.
5. The first mobile product is primarily a native API client to a paired local Mac or the approved Lambda runtime.
6. On-phone project-owned inference is a bonus branch and does not block MVP-01 or the first consumer UX.
7. `LocalScholarNode` and its project-owned gateway form the local trust and inference boundary.
8. Model servers, databases, and archives are never exposed directly to mobile clients.
9. Same-LAN discovery may use Bonjour/approved platform discovery, but pairing and TLS establish trust.
10. Local Mac pairing is explicit, mutually authenticated, revocable, and same-LAN-only in version one.
11. No router port forwarding or publicly exposed Mac endpoint is required.
12. Mobile route identity—phone, paired Mac, or Lambda—is always visible.
13. MLX-LM is the provisional first Apple-silicon runtime candidate; llama.cpp/Metal is the mandatory portable comparator where supported.
14. The exact runtime winner is evidence-gated per selected model family.
15. Mac local evidence and retrieval use the approved DR-28 architecture.
16. The phone stores only a bounded signed evidence pack for offline reference by default.
17. Native phone OCR precedes full learned page analysis and may send only user-authorized evidence to Mac or Lambda.
18. The local Mac initial context target is focused 8K–16K Study mode; full-canon local context remains experimental.
19. Quantization of the winning compact desktop model precedes mobile distillation.
20. Distillation is authorized only to repair a measured low-memory, offline, latency, or phone-capability deficit.
21. Full phone-local 8B–12B inference remains an optional research branch.
22. Physical Mac and client-server performance, memory, network, privacy, cancellation, and route tests are mandatory.
23. Capability claims remain device-, route-, model-, and task-specific.
24. Sol implements; Luna runs frozen campaigns; ChatGPT designs and reviews; Joseph approves support claims and release.

## 47. Decisions intentionally deferred

DR-29 does not yet freeze:

- Which compact 8B–12B family wins the local Mac bake-off;
- Whether MLX-LM or llama.cpp is the final local runtime for that family;
- Exact quantization algorithm and component bit map;
- Exact local API implementation library, port, or Bonjour service name;
- Exact certificate format and pairing user interface, provided the approved security semantics are preserved;
- Exact consumer Mac packaging and installer;
- Exact broadly distributed local evidence-pack contents;
- Exact public account or subscription model;
- Whether a 2B–4B mobile student is needed after the API-client UX is measured;
- The winning iOS or Android on-device runtime;
- Exact remote public-product endpoint design beyond the approved Lambda route;
- Exact battery and energy thresholds for optional phone-local inference;
- Remote access to a home Mac outside the local network;
- On-device weight personalization;
- Tablet, watch, browser-only, or embedded-device support claims.

Those decisions require LE-00–LE-13 evidence, later release design, and owner approval.

## 48. Approval statement

> **Biblical Scholar Lab will prioritize high-quality local inference on consumer Apple-silicon desktops and laptops before treating full learned inference on a phone as a product requirement. The Mac mini M4 with 16 GB unified memory will be the first mandatory local target, followed by Apple-silicon MacBooks with 16 GB or more. The winning compact 8B–12B BSL product model will be converted and quantized for a project-owned Local Scholar Node that combines deterministic tools, local evidence and retrieval, the Runtime Scholar Harness, model inference, verification, audit, and a secure client API. MLX-LM will be the provisional Apple-silicon reference runtime and llama.cpp/Metal the mandatory portable comparator where the selected architecture is supported; both remain adapters behind the project-owned ModelInferenceGateway and must pass exact parent-relative, structured-output, original-language, Translation Nuance, citation, page, context, memory, sustained-performance, and cancellation tests. The primary mobile experience will be a native iOS or Android research client that performs capture, native OCR, deterministic offline reference, route selection, streaming, notes, and accessibility and then invokes either a mutually authenticated paired Local Scholar Node on the same local network or the approved Lambda Runtime Scholar Harness. Bonjour or platform discovery may locate a Mac service, but explicit pairing, TLS, per-device credentials, revocation, and route receipts will establish trust; no public Mac endpoint, router port forwarding, direct model-server exposure, or silent cloud fallback is authorized. The interface will always disclose whether a result was produced on the phone, on the paired Mac, or on Lambda and will apply rights and privacy policy before transmitting any source, image, note, or session state. Optional Apple Foundation Models, Gemini Nano, 2B–4B project students, compact mobile evidence indexes, and full phone-local 8B–12B experiments remain separately benchmarked bonus capabilities and will not delay the first local-desktop or mobile-client release. Quantization of the selected desktop compact model will precede mobile distillation; distillation will be undertaken only to repair a measured low-memory, latency, offline, or phone-capability deficit and will use verified BSL evidence and outputs rather than private chain-of-thought. Every local model, runtime, quantization, API route, pairing relationship, evidence pack, device, update, rollback, and support claim will remain a signed and versioned artifact tested on physical owner devices for correctness, memory, latency, sustained performance, power, thermal behavior, network failure, privacy, security, deletion, accessibility, and route transparency. Sol will implement the approved architecture through LE-00–LE-13; Luna may execute only frozen conversion, packaging, benchmark, and device-test campaigns; ChatGPT will design and review every local, mobile, quantization, distillation, runtime, and routing experiment; and Joseph Abbud will retain sole authority over model and runtime selection, support tiers, budgets, public claims, and release.**

## References

[^gemma4-mobile-qat]: Google, `gemma-4-E2B-it-qat-mobile-ct` model card and Gemma 4 QAT releases. Google documents unquantized QAT, GGUF, mobile-optimized, and compressed-tensor variants, including targeted lower-bit decoding and optimized KV caches for E2B/E4B: <https://huggingface.co/google/gemma-4-E2B-it-qat-mobile-ct>.

[^sequence-kd]: Yoon Kim and Alexander Rush, “Sequence-Level Knowledge Distillation,” EMNLP 2016: <https://aclanthology.org/D16-1139/>.

[^minillm]: Yuxian Gu et al., “MiniLLM: Knowledge Distillation of Large Language Models,” 2023. The paper proposes reverse-KL distillation for generative language models and evaluates students across several scales: <https://arxiv.org/abs/2306.08543>.

[^apple-coreai-opt]: Apple Core AI Optimization Documentation. Apple describes PTQ, calibration-based compression, compression-aware fine-tuning, mixed-bit compression, and the need for more expensive training approaches at aggressive precision: <https://apple.github.io/coreai-optimization/>.

[^mlx-lm]: Apple Machine Learning Research, `mlx-lm`. MLX-LM is a package for generating text and fine-tuning LLMs on Apple silicon, with Hugging Face integration and quantization support: <https://github.com/ml-explore/mlx-lm>.

[^llama-cpp]: ggml-org, `llama.cpp`. The project treats Apple silicon as a first-class target through ARM, Accelerate, and Metal; supports several quantization formats; and provides an OpenAI-compatible `llama-server`: <https://github.com/ggml-org/llama.cpp>.

[^bonjour-network]: Apple Developer, “Bonjour” and TN3151, “Choosing the right networking API.” Apple documents Bonjour service advertisement, browsing, and connection and recommends Network framework for these operations: <https://developer.apple.com/bonjour/> and <https://developer.apple.com/documentation/technotes/tn3151-choosing-the-right-networking-api>.

[^local-network-privacy]: Apple Developer, `NSLocalNetworkUsageDescription`. Apple requires apps that access local-network hosts or Bonjour services to explain that access to the user: <https://developer.apple.com/documentation/BundleResources/Information-Property-List/NSLocalNetworkUsageDescription>.
