# VS-01 — John 1:5 Translation Nuance Vertical Slice

| Field | Value |
|---|---|
| Artifact ID | `VS-01` |
| Status | `APPROVED` |
| Approval date | 2026-08-17 |
| Artifact type | Binding implementation vertical slice |
| Project owner | Joseph Abbud |
| Product, architecture, benchmark, and experiment designer | ChatGPT |
| Independent implementation and evidence reviewer | ChatGPT |
| Depends on | DR-01 through DR-30 |
| Activation authority | ChatGPT defines the activated contracts, evidence, tests, and non-goals; Joseph Abbud approves the slice and any material expansion |
| Implementation authority | GPT-5.6 Sol exclusively implements and repairs the activated VS-01 production code and must satisfy DR-30 simplicity conformance |
| Execution authority | GPT-5.6 Luna may execute only frozen operations delegated by Sol; VS-01 itself authorizes no cloud launch or training |
| Approved change | Freezes John 1:5 as the first end-to-end implementation workflow, activating only the source, linguistic, Translation Nuance, evidence, runtime, page, audit, and seed-benchmark contracts needed to prove one cited Study-mode translation-comparison and page-study experience |

## 1. User-visible capability

A user can select or enter John 1:5, compare two approved public/open English translation editions, inspect the Greek source and reviewed linguistic evidence, ask why the wording differs, and receive a cited Study-mode answer that:

- Identifies the exact editions and source text.
- States whether a textual variant is involved in the compared wording.
- Explains the relevant lexical/semantic issue without a root or gloss fallacy.
- Distinguishes surface wording from material nuance.
- Presents reviewed alternatives and uncertainty.
- Shows claim/evidence links.
- Separates Scripture, headings, notes, and handwriting on a controlled page image.
- Produces an immutable runtime audit receipt.

## 2. Why this passage

John 1:5 provides a compact but meaningful example of translation variation around the Greek verb commonly represented by forms such as “comprehended,” “apprehended,” or “overcome.” It allows the first slice to demonstrate:

- Exact passage and edition identity
- Koine Greek linguistic analysis
- Translation comparison without counting translations as witnesses
- Source-textual-state versus translation-choice distinction
- Multiple defensible renderings
- Citation and evidence handling
- Page-region authority
- Accessible Brief/Study rendering

It is not selected to establish one final specialist interpretation of the verse.

## 3. Activated contracts

Only the following logical contracts are activated for VS-01:

```text
stable identity and immutable revision
source artifact and rights decision
work, edition, reference scheme, passage selection, text segment
basic Greek surface/lemma/morphology/sense candidate records
translation work, edition, realization, difference unit
bounded alignment and cause diagnosis
claim, evidence link, epistemic status, citation
context request/packet
runtime request, answer candidate, claim ledger, audit receipt
page artifact, page region, recognition candidate, authority class
benchmark case family, evidence contract, answer contract, score result
```

A concept not in this list remains `NORMATIVE_FUTURE` unless a later approved activation manifest adds it.

## 4. Candidate source set

Exact admission remains subject to `SOURCE-PLAN-01` and rights verification. The intended source roles are:

- One approved Greek New Testament edition.
- One approved Greek linguistic annotation source with lemma, morphology, and where available syntax/sense information.
- Two approved public/open English translation editions exhibiting the target wording difference.
- One project-authored source-verifiable explanation packet.
- One source-traceable synthetic page containing canonical text, a section heading, a footnote/study note, a verse number, and a user annotation overlay.

No restricted apparatus, copyrighted study-Bible page, user-private image, or private benchmark gold is needed.

## 5. Required deterministic operations

```text
resolve_reference("John 1:5")
get_passage(reference, edition)
get_original_text(reference, edition)
get_linguistic_analysis(reference, unit)
get_translation_parallel(reference, editions)
compare_translation_realizations(...)
get_source_span(...)
resolve_citation(...)
classify_page_region(...)
```

A deterministic reference implementation may use direct in-process functions. A plugin system, remote service mesh, or generalized provider registry is not required.

## 6. Required answer behavior

A Study-mode answer must include:

1. Direct answer to why the translations differ.
2. Exact translation and Greek-edition identity.
3. A source-textual-state statement.
4. A bounded source-language explanation.
5. At least two defensible translation effects or possibilities when supported.
6. A calibrated assessment.
7. Material uncertainty.
8. Evidence links and exact locators.
9. No claim that translation frequency establishes manuscript support.
10. No presentation of a glossary list as contextual meaning.

The answer may qualify or abstain when the evidence packet is incomplete.

## 7. Page-study fixture

The synthetic page fixture must contain labeled ground truth for:

```text
CANONICAL_TEXT
VERSE_NUMBER
SECTION_HEADING
STUDY_NOTE_OR_FOOTNOTE
CROSS_REFERENCE
USER_ANNOTATION
PAGE_HEADER
```

The fixture generator may create approved seeded layout and image variants. It may not change the verse, translation edition, region roles, answer contract, or gold labels.

The page workflow must preserve separately:

```text
source pixels
OCR hypothesis
VLM observation, when activated
canonical edition lookup
user correction
```

## 8. Seed benchmark families

The first benchmark batch should contain at least these family blueprints, authored by ChatGPT and reviewed by Joseph:

```text
VS01-B01  exact passage and edition resolution
VS01-B02  Greek source-span identity
VS01-B03  translation wording comparison
VS01-B04  no-textual-variant versus translation-choice classification
VS01-B05  lexical-gloss fallacy trap
VS01-B06  ambiguity/alternative explanation
VS01-B07  claim-to-source citation entailment
VS01-B08  insufficient-evidence qualification
VS01-B09  page scripture-versus-note classification
VS01-B10  page illegibility and no-invention behavior
VS01-B11  user correction survives session compaction
VS01-B12  Brief versus Study answer-depth consistency
```

Most initial cases should be `REV-P0` or `REV-P1`. A specialist adjudication question may be included only as `REV-P2_SME_REVIEW_PENDING`.

## 9. Minimal implementation topology

VS-01 requires:

```text
one Python distribution
one PostgreSQL development database
one bounded archive directory conforming to the future archive contract
one CLI
one deterministic runtime path
one reference model adapter or fixture response path
one benchmark reference evaluator
one small accessible web page only after the backend slice passes
```

It does not require:

- Lambda
- Training
- Preference optimization
- LangGraph
- Inspect AI
- Vector search
- A model-family bakeoff
- Full-New-Testament context
- Mobile apps
- User accounts
- A public persistent service
- General source-connector framework breadth
- Separate microservices

Those are added later under explicit activation.

## 10. Acceptance criteria

### Source and identity

- Every displayed or quoted text binds an exact edition/source revision.
- Original and translation text remain distinct.
- All source bytes and derived records have reproducible hashes.
- Rights dispositions permit the exact implemented operations.

### Scholarly behavior

- The system distinguishes textual-state evidence from translation choice.
- It exposes source-language evidence without named word-study fallacies.
- It preserves material alternatives and uncertainty.
- It cannot count duplicate translation instances as independent evidence.

### Runtime

- The structured answer candidate validates before rendering.
- Unsupported central claims are removed, qualified, or blocked.
- The audit receipt identifies tools, sources, packet, model route, and result.
- A user correction changes a new revision rather than overwriting history.

### Page study

- Scripture, note, heading, verse number, and annotation are correctly distinguished on the clean fixture.
- Degraded variants report uncertainty rather than hallucinating unreadable content.
- Canonical lookup never silently rewrites OCR evidence.

### Simplicity

- No unactivated service/package/table/interface exists.
- No direct dependency lacks a handoff justification.
- The complete backend slice fits within the DR-30 complexity and PR budgets, or has an approved waiver.

## 11. Completion evidence

The Sol handoff must link:

- Exact activation manifest
- Source and rights manifest
- Database migration and schema diff
- Contract fixtures
- Test and coverage report
- End-to-end CLI demonstration
- Runtime audit receipt
- Benchmark seed results
- Page fixture and region results
- Complexity receipt
- Known limitations and deferred contracts

## 12. Non-goals

VS-01 does not establish:

- Comprehensive Johannine scholarship
- Final contextual-sense adjudication
- New Testament textual-criticism competence
- Full ancient-version analysis
- Scholar-level Greek competence
- General benchmark validity
- Model-training value
- Production security or scalability
- Public preview readiness

## 13. Approval statement

> **Biblical Scholar Lab will begin implementation with a tightly bounded John 1:5 translation-comparison and page-study vertical slice. The slice will prove exact source and edition identity, basic Koine Greek evidence, translation-difference representation, source-state-versus-translation-choice distinction, claim/evidence citation, calibrated Study-mode explanation, page-region authority, user correction, runtime verification, audit, and the first `REV-P0`/`REV-P1` benchmark families. Only explicitly named VS-01 contracts will be activated. No cloud execution, training, vector search, mobile client, full-canon context, persistent public service, or speculative service/package scaffolding will be required.**
