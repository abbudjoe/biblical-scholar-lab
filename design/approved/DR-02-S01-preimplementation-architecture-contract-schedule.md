# DR-02-S01 — Preimplementation Architecture Contract Schedule

**Status:** APPROVED
**Parent design:** DR-02 — Scholarly Epistemology and Methodology
**Approved by:** Joseph Abbud
**Approval date:** 2026-08-15
**Supersedes:** none

## 1. Purpose

This supplemental decision records when and how Biblical Scholar Lab's consequential logical architecture will be defined before GPT-5.6 Sol writes production implementation.

It operationalizes the DR-02 rule that Sol owns implementation correctness and conformance, while the project owner and ChatGPT retain product, experiment, benchmark, data, harness, and architecture authority.

## 2. Governing rule

> **No consequential architectural contract is delegated to Sol merely because it is expressed in code. The applicable design review must define and receive owner approval before Sol implements it.**

Sol may recommend alternatives and explain engineering consequences. It may not select or implement a materially different architecture until ChatGPT has designed the amendment and the project owner has approved it.

## 3. Component design schedule

The following design reviews will define the named contracts before their corresponding implementation begins.

| Design review | Contracts to be defined |
|---|---|
| DR-04 — Canon and Reference Model | Canon-independent passage identities, localized references, versification mappings, aliases, uncertainty, and reference-resolution behavior |
| DR-05 — Textual-History and Provenance Graph | Entity identities, relationship types, provenance, lineage, immutability, authority rules, and source-to-derivative traceability |
| DR-06 — Translation Nuance Core | Many-to-many span alignment, translation-cause representation, translation genealogy, competing diagnoses, confidence, and retroversion uncertainty |
| DR-07 — Linguistic Representation | Surface, lemma, morphology, syntax, semantics, discourse, annotation provenance, and language-specific invariants |
| DR-08 — Ancient Versions and Apparatus | Witness and translation roles, apparatus records, access lanes, retroversion limits, and training-versus-retrieval boundaries |
| DR-09 — Scholarship and Citation Model | Claim ledger, evidence records, bibliographic identity, quotation provenance, citation entailment, and source-role compatibility |
| DR-10 — Rights and Release Architecture | Open and restricted storage partitions, access controls, derivative lineage, and artifact-specific redistribution rules |
| DR-13 — Multilingual Architecture | Source, interface, quotation, and scholarship language identities; translated-evidence provenance; and per-language retrieval contracts |
| DR-14 — Multimodal Page Architecture | Page, region, OCR span, layout, edition resolution, user-upload provenance, and visual uncertainty contracts |
| DR-15 — Context Composer | Evidence-packet structure, source ordering, context modes, token budgets, truncation rules, and citation-survival requirements |
| DR-16 — Runtime Scholar Harness | Tool interfaces, router, retrieval planner, evidence bundles, claim verification, answer contract, and audit trace |
| DR-17 — Corpus and Sampling | Dataset manifests, materialization rules, work/witness/translation grouping, overlap clusters, mixture identity, and sampling invariants |
| DR-20 through DR-22 — Benchmark and Evaluation | Case format, scoring records, model/run identity, logs, reports, human review, and portable harness contracts |
| DR-23 — Model and Training Harness | Experiment, model, dataset, stage, checkpoint, backend-adapter, metric, and artifact contracts |
| DR-25 — Campaign Execution | Immutable campaign envelope, run identity, approval, Sol-to-Luna delegation, retry, cost, shutdown, and evidence contracts |
| DR-28 — Integrated Logical Architecture and Contract Registry | Cross-component source-of-truth rules, storage topology, foreign keys, serialization, migrations, service boundaries, failure semantics, audit events, and compatibility policy |
| DR-29 — Mobile, Edge, Quantization, and Distillation | Mobile capability tiers, model/runtime packaging, quantization, local retrieval, OCR, device limits, and cloud escalation contracts |

## 4. DR-28 integration gate

DR-28 is the final preimplementation integration review for the architecture as a whole. It will consolidate all approved component designs and resolve contradictions among them.

DR-28 must define at least:

- canonical source-of-truth stores;
- derived and rebuildable indexes;
- identifier namespaces and cross-component keys;
- public, private, restricted, and holdout storage topology;
- normative serialization formats;
- versioning, migration, and backward-compatibility policy;
- service and tool interfaces;
- validation boundaries and fail-closed behavior;
- audit-event and evidence-record formats;
- performance, reproducibility, and equivalence requirements;
- normative versus optional fields;
- changes that require a new design review.

Sol may not begin the integrated production implementation before DR-28 is approved. Bounded prototypes may be authorized earlier only when their design review explicitly permits them and identifies them as disposable evidence-gathering artifacts rather than the trusted production architecture.

## 5. What the project will specify tightly

The approved design baseline will be highly opinionated about:

- logical identities and invariants;
- source and evidence authority;
- storage and rights boundaries;
- provenance and lineage;
- retrieval stages and mandatory filtering;
- ranking objectives that can affect scholarly conclusions;
- evidence bundles and citation behavior;
- validation and hard-failure semantics;
- experiment and artifact identity;
- auditability and reproducibility;
- security, privacy, and release constraints.

## 6. Sol's remaining discretion

Sol may choose reversible, local, design-neutral mechanics such as:

- module, class, and function decomposition;
- code organization and internal naming;
- test implementation and fixtures;
- equivalent local algorithms;
- dependency choices among approved or demonstrably equivalent options;
- performance optimizations that preserve all approved semantics, evidence, metrics, security, reproducibility, and material cost boundaries.

A choice is not design-neutral merely because users cannot see it directly. Retrieval ordering, storage partitioning, serialization loss, validation behavior, benchmark scoring, and artifact lineage are design matters.

## 7. Escalation

Sol must stop with:

```text
BLOCKED_REQUIRES_DESIGN_REVIEW
```

when implementation reveals that an approved contract is missing, contradictory, infeasible, or likely to produce materially different behavior.

## 8. Locked decisions

1. Consequential logical architecture will be defined before Sol implements it.
2. Component designs will be approved in their named reviews.
3. DR-28 will integrate the complete architecture before trusted production implementation.
4. Sol owns engineering correctness and conformance, not architecture selection.
5. Disposable prototypes require explicit authorization and may not silently become production foundations.
6. Material architecture changes require ChatGPT design and owner approval.

## 9. Deferred decisions

This supplement does not select specific databases, vector stores, graph engines, runtime frameworks, or training backends. Those choices will be made in the relevant component reviews or through approved bounded comparisons.

## 10. Approval statement

> **Biblical Scholar Lab will define and approve its consequential logical architecture, schemas, storage topology, indexing semantics, retrieval contracts, validation behavior, reporting contracts, and cross-component interfaces before GPT-5.6 Sol implements them. Individual component reviews will establish their domain contracts, and DR-28 will consolidate them into the authoritative integrated architecture. Sol may make only reversible, design-neutral engineering choices within those contracts and must escalate any material gap or conflict for design review.**
