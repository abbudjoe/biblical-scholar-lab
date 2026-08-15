# DR-02-S03 — Mobile, Edge, Quantization, and Distillation Direction

**Status:** APPROVED
**Parent design:** DR-02 — Scholarly Epistemology and Methodology
**Approved by:** Joseph Abbud
**Approval date:** 2026-08-15
**Supersedes:** none

## 1. Purpose

This supplemental decision records the approved mobile and edge direction identified during DR-02 capacity review. It establishes architectural intent without prematurely selecting a runtime, quantization method, or mobile model.

DR-29 will define the complete implementation contract.

## 2. Governing principle

> **Mobile support will preserve the scholar system's evidence discipline by moving exact texts, reference resolution, morphology, and retrieval into deterministic local services rather than requiring a phone-sized model to memorize the scholarly corpus.**

The on-device model is primarily responsible for question understanding, tool orchestration, evidence interpretation, concise explanation, and privacy-preserving interaction.

## 3. Device and model posture

A fine-tuned 9B-class model may be quantized and tested on high-memory mobile devices, but it is not a version-one cross-platform product assumption.

The approved direction is:

| Deployment tier | Provisional role |
|---|---|
| 2B–4B mobile student | Primary on-device target for common Bible study, tool use, and short evidence packets |
| Quantized 9B model | Experimental high-memory device and desktop-edge target |
| 9B–12B server/desktop model | Main compact research-engine candidate |
| 27B–31B cloud model | Difficult-query, advanced-synthesis, or second-pass candidate |
| Deterministic tools and local/remote RAG | Exact text, morphology, reference, provenance, and scholarship access across all tiers |

A constrained 9B experiment may be attempted on a newer high-memory Android phone. No product-quality promise is made for the user's iPhone 15 Pro or Pixel 10 Pro until device-specific benchmarks pass.

Operating-system foundation models, including Apple Intelligence, are separate model providers; their presence does not automatically host, accelerate, or grant memory to the project's custom checkpoint.

## 4. Mobile student strategy

The preferred cross-platform mobile path is a 2B–4B student trained through a subset of:

- scholarly SFT;
- Translation Nuance tasks;
- verified tool-use traces;
- short evidence-packet reasoning;
- preference-behavior distillation;
- carefully reviewed teacher outputs from the winning compact and larger systems;
- mobile-specific printed-page and OCR workflows.

Teacher-generated material remains synthetic and must preserve provenance, validation, and human-review rules from DR-02.

## 5. Native OCR and visual architecture

On mobile, native platform OCR and layout services may replace or precede a large multimodal vision tower when that produces better memory, speed, and fidelity.

The preferred flow is:

```text
camera or page image
    → native OCR and layout segmentation
    → passage and edition resolution
    → deterministic local text verification
    → local or remote retrieval
    → compact model analysis
    → optional cloud escalation
```

The full multimodal model remains available for difficult layouts, ambiguous page structure, or richer image reasoning.

## 6. Quantization policy

Quantization is a separately evaluated model transformation, not a packaging afterthought.

The project should compare, as appropriate:

- BF16 or FP16 master checkpoints;
- 8-bit;
- 4-bit;
- mixed 4/8-bit;
- 3-bit experimental variants;
- quantized KV cache;
- separately quantized vision and language components.

Mixed precision should be considered for sensitive components such as embeddings, output heads, normalization, rare-script pathways, tool-call formatting, and vision alignment.

Every quantized candidate must be re-evaluated on:

- Greek and Hebrew text fidelity;
- morphology and Translation Nuance diagnosis;
- multilingual output;
- tool-call structure;
- citation formatting and source identity;
- uncertainty and refusal behavior;
- multimodal/page performance where included;
- latency, memory, thermal behavior, battery use, and cold start.

A quantized model may not inherit the benchmark status of its unquantized parent automatically.

## 7. Context policy for phones

Phone deployments should use short, targeted evidence packets and retrieval rather than full-New-Testament context.

The exact context budgets are deferred to DR-29 and device testing. The architectural default is:

```text
short local context
+ exact passage tools
+ compact local index
+ selective cloud escalation
```

## 8. Privacy and offline behavior

DR-29 must define:

- what page images and queries remain on-device;
- user consent for remote escalation;
- local encrypted storage;
- handling of copyrighted Bible pages and private annotations;
- offline capability claims;
- deletion and telemetry policy;
- separation of user material from training data.

No user-uploaded image or research note enters training by default.

## 9. Capability tiers

Mobile capability should be reported explicitly rather than through a single “runs locally” claim.

Possible tiers include:

```text
OFFLINE_CORE
  passage lookup, reference resolution, local OCR, compact analysis

CONNECTED_STUDY
  local interaction plus remote scholarship retrieval

CLOUD_SCHOLARLY
  larger model, long context, and advanced multi-source synthesis
```

## 10. Locked decisions

1. A quantized 9B model is an experiment, not the primary mobile product assumption.
2. A 2B–4B student is the preferred cross-platform on-device target.
3. Deterministic local tools and retrieval carry exact knowledge and provenance.
4. Native mobile OCR may replace the full vision tower for ordinary printed-page workflows.
5. Quantization requires full project-specific reevaluation.
6. Full-New-Testament context is not a phone requirement.
7. Cloud escalation is acceptable when explicit, privacy-aware, and user-controllable.
8. DR-29 will define the complete mobile, edge, quantization, and distillation architecture.

## 11. Deferred decisions

This supplement does not select:

- Apple Core ML, Foundation Models, LiteRT, or another runtime;
- a mobile model family;
- exact quantization algorithms;
- exact memory or context budgets;
- device support claims;
- distillation loss or curriculum;
- offline storage implementation;
- application architecture.

## 12. Approval statement

> **Biblical Scholar Lab will pursue mobile support through a compact, evidence-aware architecture rather than assuming that the full 9B research model must run on every phone. A 2B–4B student with deterministic local tools, compact retrieval, native OCR, and optional privacy-aware cloud escalation is the preferred product direction. Quantized 9B deployment remains an experimental high-memory-device target, and every quantized or distilled model must independently pass the project's language, Translation Nuance, citation, tool-use, multimodal, safety, latency, memory, and thermal evaluations.**
