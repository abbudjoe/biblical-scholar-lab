# Biblical Scholar Lab — Approved Baseline Summary

This document is a navigation aid. The approved design reviews, source plans, benchmark batches, governance package, and implementation activations remain normative.

## Authority

- Joseph Abbud approves designs, activations, campaigns, budgets, merges, progression, claims, and releases.
- ChatGPT owns product, architecture, experiment, source, and benchmark design and reviews Sol's exact-head implementation evidence.
- GPT-5.6 Sol exclusively writes and repairs production implementation.
- GPT-5.6 Luna performs only frozen operations delegated by Sol.

## Product target

Biblical Scholar Lab is a source-aware, multilingual-capable, multimodal biblical research assistant centered initially on New Testament philology, textual history, translation nuance, ancient context, and inspectable scholarship. It serves serious Bible learners without requiring academic credentials and exposes deeper evidence progressively.

## Trust architecture

The model is subordinate to deterministic tools, reviewed evidence, rights controls, the Translation Nuance Semantic Kernel, the Context Composer, the Runtime Scholar Harness, claim-level verification, and human governance. Exact text, editions, citations, rights, and current scholarship remain external to model memory.

## First bounded implementation

`VS-01` proves one complete John 1:5 workflow using the sources frozen by `SOURCE-PLAN-01` and the cases frozen by `BENCH-VS01-BATCH-01`. It covers exact passage and edition identity, Greek morphology, two English translations, translation-choice diagnosis, citations, a synthetic page fixture, user correction, Study-mode rendering, and an audit receipt.

Explicitly absent from VS-01: model training, Lambda execution, vector search, LangGraph, Inspect AI, full-canon context, mobile clients, accounts, and speculative service scaffolding.

## Implementation order

1. `W00` — repository governance, exact-head review, owner authorization, and integrity checks.
2. `W01` — activation validation, simplicity enforcement, and minimal project tooling.
3. `W02` — minimal authoritative storage and archive/private-vault preflight.
4. `W03` — exact `SOURCE-PLAN-01` acquisition and verification.
5. `W04` — minimal VS-01 scholarly domain records.
6. `W05` — exact tools, evidence packet, deterministic runtime, verification, and audit.
7. `W06` — approved benchmark loaders and deterministic reference evaluation.
8. `W07` — minimal accessible Study workspace.
9. `W08` — framework and retrieval adapters only after the reference slice proves a need.
10. `W09` — Lambda and training control plane only after A0 and benchmark validity.

## Simplicity rule

Only contracts named by the active `ImplementationActivationManifest` may become code. Unactivated future architecture receives no stub, table, package, endpoint, interface, flag, TODO, or service shell. DR-30 code, dependency, abstraction, and PR budgets are merge-blocking.

## Current implementation gate

`GOV-01`, GOV-01-ERRATA-01/02, and `ACT-W00-REPOSITORY-GOVERNANCE-v3` are approved. Production implementation may begin only after the final clean-room package review and owner bootstrap of the public repository.
