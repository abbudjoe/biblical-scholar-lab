# DR-31 — Biblos Translation Nuance Laboratory Recharter and Annotation Package Authority

| Field | Value |
|---|---|
| Design ID | `DR-31` |
| Status | `APPROVED` |
| Approval date | 2026-08-28 |
| Program authority | `UP-01`; `UP-01-ERRATUM-01`; `UP-01-A01` |
| Project owner | Joseph Abbud |
| Designer and independent reviewer | ChatGPT |
| Repository base | `3f52895459aefb84e6e6a7da8870f12e5f653e76` |
| Repository tree | `cbe157cad80adf42127871a9859db11707a7b278` |
| Depends on | DR-01 through DR-30; VS-01; completed VS01-T03 through VS01-T09B; `BSL-STATUS-01`; merged Biblos P0-D11 consumer authority |
| Nature | Additive recharter; no historical design is deleted |
| Implementation authority | None; every physical change requires a later approved activation |
| Experiment authority | None; provider, model, cloud, and training work require separate authorization |

## 1. Purpose

Biblical Scholar Lab completed a rigorous John 1:5 technical proof spanning source authority, normalization, evidence, claims, deterministic runtime, benchmark execution, evidence acquisition, immutable publication, a public-safe Study projection, and a loopback reference workspace.

The cross-project program has now selected Biblos as the final production Bible reader and Biblical Scholar Notes as the editorial master. The Lab therefore no longer proceeds on the assumption that it must itself become the production reader, production backend, or model-serving product.

DR-31 recharters the Lab as the Translation Nuance source, evidence, annotation-validation, package-compilation, evaluation, and optional future model-research laboratory supporting Biblos.

This review defines:

- final cross-project role allocation;
- preservation of completed John 1:5 authority;
- the exact relationship among the three cross-project contracts;
- the Lab's producer, verifier, receipt, and reference-validator responsibilities;
- the Notes input boundary;
- the merged Biblos consumer authority the Lab must conform to without duplicating;
- deterministic package-compilation and detached-receipt posture;
- independent Biblos validation without a Lab runtime;
- API-first evaluation;
- a conjunctive training-reactivation gate;
- a future, unactivated John 13 cross-project slice;
- capability reuse and anti-duplication classifications;
- formal pause and dormancy effects.

DR-31 does not authorize implementation, source acquisition, package compilation, provider evaluation, archive or database mutation, model work, cloud work, VS01-T09-OP01, VS01-T10, or a successor slice.

## 2. Governing principle

> **Biblos is the sole production reader. Biblical Scholar Notes is the editorial master. Biblical Scholar Lab is the source, evidence, rights, annotation-validation, deterministic package-compilation, receipt, reference-validation, benchmark, API-evaluation, and optional future model-research laboratory. The Lab may produce independently verifiable artifacts for Biblos, but it may not become a required Biblos runtime service or duplicate Biblos product ownership. Retrieval and standard API baselines precede any weight adaptation.**

The intended forward flow is:

```text
Biblical Scholar Notes editorial master
    → bounded ReaderAnnotationProjection v1
    → Lab source, claim, morphology, review, and rights validation
    → deterministic compilation against the Biblos-owned consumer contract
    → TranslationAnnotationPackage v1 exact JSON bytes
    → detached TranslationAnnotationCompilationReceipt v1 and checksum evidence
    → independent Biblos validation and bundled import
    → offline Nuance reading in Biblos
```

No arrow authorizes the next arrow automatically.

## 3. Additive relationship to DR-01 through DR-30

DR-01 through DR-30 remain approved historical authority. DR-31 changes the forward program role and current critical path, not the truth conditions or historical meaning of prior records.

### 3.1 Preserved as active methodological authority

The following remain directly applicable where a future bounded task activates them:

- DR-06 Translation Nuance causal distinctions and evidence-first diagnosis;
- DR-07 immutable source text, stand-off linguistic analysis, and ambiguity preservation;
- DR-09 claim-level citation, source identity, and evidence-proximity controls;
- DR-10 component- and operation-specific rights;
- DR-12 external authoritative evidence, deterministic semantic compilation, and model-subordinate behavior;
- DR-16 typed tools, evidence sufficiency, verification, audit, and correction boundaries;
- DR-20 benchmark charter;
- DR-21 authority-separated annotation and scoring;
- DR-22 subject, evidence, cost, failure, and condition separation in evaluation;
- DR-24 hard-gate precedence, practical-value requirements, and stop decisions for both API evaluation and later training;
- DR-25 safety, cost, termination, cleanup, and provider-operation controls when separately bounded A1–A3 API evaluation is authorized;
- DR-26 evidence visibility, accessibility, and anti-overtrust principles;
- DR-28 Git/archive/contract authority and modular-monolith posture;
- DR-30 activation, simplicity, dependency, and anti-scaffolding controls.

### 3.2 Approved but currently dormant and conditional

The following retain historical authority but are classified:

```text
DORMANT_PENDING_TRAINING_REACTIVATION_GATE
NOT_ON_CURRENT_CRITICAL_PATH
NOT_IMPLEMENTATION_AUTHORITY
```

This classification applies only to training, learned-model serving or conversion, cloud-training, adapted-model hosting, `TNEVAL-A4`, and related controller portions:

- DR-11 foundation-model family and capacity selection for adaptation or hosting;
- DR-12 `TNC-A1` through `TNC-A6` learned architecture extensions;
- DR-17 training-corpus materialization and sampling;
- DR-18 CPT, Translation Nuance mid-training, SFT, retrieval/tool SFT, preference-adjacent adaptation, distillation, and related stages;
- DR-19 preference optimization;
- DR-23 training harness and learned-artifact execution;
- DR-24 product-first, clean-Base, capacity, mobile-student, learned-extension, and `TNEVAL-A4` adapted-model branches;
- DR-25 cloud training, adapted-model hosting, `TNEVAL-A4` campaigns, and training/campaign-controller implementation;
- DR-29 learned local-model serving, quantization, distillation, and mobile-model paths.

DR-31 does not reject or supersede those designs. It makes them conditional on the conjunctive training-reactivation gate in section 21.

This dormancy classification does not apply to `TNEVAL-A0` through `TNEVAL-A3`. A0–A3 remain unstarted and unauthorized and require separate bounded authority. A1–A3 are eligible for separately frozen provider/API evaluation and are not gated by training reactivation. Applicable DR-22, DR-24, and DR-25 evaluation and operational controls remain methodological authority for that later bounded work.

### 3.3 Removed from the current critical path

The following prior product assumptions are classified:

```text
RETIRED_FROM_CRITICAL_PATH
```

- the Lab as the final reader;
- the Lab as the production backend for reader sessions;
- the Lab as the production Grounded Ask owner;
- the Lab loopback workspace as the production consumer UI;
- a required Lab online API for Biblos;
- immediate custom-model training as the next milestone.

These assumptions remain useful historical context but no longer define the active program.

## 4. Final cross-project role allocation

### 4.1 Biblos owns

Biblos owns:

- the sole production Bible reader;
- the normative `TranslationAnnotationPackage v1` consumer schema;
- independent package validation and import;
- bundled first delivery and offline Nuance presentation;
- Historical Explore;
- the production backend;
- later Grounded Ask;
- production privacy, security, release, update, rollback, and saved-user-data behavior;
- final product UI and reader interaction;
- any later package update or distribution service.

The Lab may not redefine the Biblos consumer schema in a Lab-owned public contract.

### 4.2 Biblical Scholar Notes owns

Biblical Scholar Notes owns:

- the `StudyRecord` editorial master;
- the normative `ReaderAnnotationProjection v1` export schema;
- owner revisions;
- short and full annotation prose;
- editorial correction and supersession history;
- decisions to publish or withhold editorial prose.

The Lab may validate a bounded projection but may not silently rewrite the Notes master.

### 4.3 Biblical Scholar Lab owns

The Lab owns:

- source admission and exact provenance;
- source and manifestation verification;
- linguistic and morphology verification;
- annotation claim/evidence/citation validation;
- operation-specific rights validation;
- deterministic compilation conforming to the Biblos consumer contract;
- the normative `TranslationAnnotationCompilationReceipt v1`;
- package checksum and compilation evidence;
- accepted and rejected candidate accounting;
- a platform-neutral reference validator;
- API-first evaluation and cost/stability accounting;
- contamination controls;
- optional future model research after explicit reactivation.

The Lab does not own final reader presentation or production saved state.

## 5. Exactly three cross-project contracts

The approved shared boundary contains exactly:

```text
TranslationAnnotationPackage v1
    normative consumer schema owned by Biblos

ReaderAnnotationProjection v1
    normative editorial export schema owned by Biblical Scholar Notes

TranslationAnnotationCompilationReceipt v1
    normative producer receipt owned by Biblical Scholar Lab
```

A fourth shared public contract is prohibited until an activated consumer demonstrates that one of these three cannot carry the required boundary without becoming semantically incoherent.

The following are explicitly prohibited:

- a generic cross-project `StudyItem`;
- a shared cross-project database schema;
- a common runtime package;
- an annotation CMS contract;
- an online registry contract;
- a generic plugin interface;
- a cross-repository live-sync protocol.

Internal implementation records may exist later when activated, but they do not become shared contracts by accident.

## 6. Exact merged Biblos consumer authority

The Lab must treat the following merged Biblos authority as normative and external:

```text
repository
abbudjoe/biblos

main
c1c9649fcb656603ff9752abc280ba446b49c083

tree
9230c04e04f5a5b754f64dd8d00df7df968a45da

merged design PR
#6 — [P0-D11] Persist unified reader design authority
```

Exact authority files:

```text
docs/phase1/amendments/P0-D11-unified-reader-and-contextual-study-lanes.md
SHA-256
f3b70816bd392bfbe23c29e84c76bdf983b8effc8f800b2b0e76ed4c6831c1fa

docs/phase1/tasks/P1-T12-translation-annotation-package-consumer-and-importer.md
Git blob
7af7b18dc2e103e7bf72d843bf4ee8680180a1ce

docs/phase1/tasks/P1-T13-john-13-offline-translation-nuance-reader.md
Git blob
852b931f0d2d411cfb2b24e05d8f440589cea416
```

DR-31 recognizes these records. It does not copy their normative schema into the Lab, modify them, or create a competing consumer definition.

A future Lab compiler must bind the exact supported Biblos package-schema revision and content identity supplied by merged P1-T12 authority. Until that consumer schema is merged and separately activated for Lab use, the Lab has no package implementation authority.

## 7. Binding package encoding and identity

The Biblos consumer authority fixes:

```text
interchange
UTF-8 JSON

producer conformance
RFC 8785 canonical JSON bytes

immutable package-version identity
SHA-256 of the exact emitted package JSON file bytes

file-hash location
detached Lab receipt and checksum evidence

self-referential package file hash
prohibited

ZIP or directory
transport only; not semantic authority
```

The Lab compiler must emit exact JSON bytes accepted by the normative Biblos schema. The package file SHA-256 is computed over those exact bytes.

No package field may contain its own final file SHA-256.

A detached checksum file may list:

```text
<package-file-sha256>  <package-filename>
<receipt-file-sha256>  <receipt-filename>
```

but that sidecar is evidence rather than a fourth shared contract.

## 8. Exact anchor semantics

Every annotation anchor is measured against the exact decoded verse string in the exact bound Biblos Scripture package.

Before hashing, indexing, extracting, or comparing, the producer and consumer perform no:

- Unicode normalization;
- case folding;
- punctuation substitution;
- whitespace collapse;
- typography substitution;
- fuzzy matching;
- canonical-text replacement.

Version-one anchors require:

```text
exact Scripture package identity
exact Scripture package-content identity
exact translation identity and revision
exact canon identity
exact versification identity
one exact verse identifier
SHA-256 of the complete exact decoded verse string bytes under the Biblos contract
UTF-16 code-unit start
UTF-16 code-unit length
exact expected phrase
```

A single anchor may not cross a verse boundary.

A multi-verse issue uses multiple ordered anchors. Their order is meaningful and must be preserved.

`prefix_guard` and `suffix_guard` are excluded from version one.

An anchor is invalid when:

- the Scripture package or package-content identity differs;
- the verse hash differs;
- the UTF-16 range is outside the exact string;
- the extracted phrase differs from `expected_phrase`;
- the translation, canon, or versification differs;
- an unapproved normalization would be needed to make it match.

The Lab must reject the candidate rather than repair the reader text or guess the intended span.

## 9. Reader payload and detached receipt

### 9.1 Reader package

`TranslationAnnotationPackage v1` carries only public-safe reader-required material:

- exact package and Scripture bindings;
- exact target verse and ordered anchors;
- stable annotation identity and revision;
- issue category;
- short note;
- full note;
- interpretive limits;
- bounded claim summaries;
- public-safe citations;
- display eligibility;
- active correction, supersession, and retirement relationships;
- the independent review, verification, lifecycle, and eligibility fields required by the Biblos contract.

The package does not carry:

- absolute Lab archive paths;
- private Notes paths;
- private evidence locations;
- credentials;
- full restricted source bodies;
- scorer-only plans;
- benchmark gold;
- provider prompts;
- Lab database coordinates;
- rejected candidate prose;
- compilation diagnostics not required by the reader.

### 9.2 Lab receipt

`TranslationAnnotationCompilationReceipt v1` may additionally bind:

- compiler name, version, and Git commit;
- exact Biblos consumer authority identity;
- exact package-schema revision and hash;
- exact Notes export identity and record revisions;
- source-authority snapshots;
- rights-decision snapshots;
- accepted annotation identities;
- rejected candidate identities and reason codes;
- validation results;
- exact package byte count and SHA-256;
- exact receipt identity and receipt-file SHA-256;
- compilation timestamp;
- zero-operation or execution disclosures;
- public-safe and private evidence projections.

The iOS runtime does not require the full Lab receipt to render a previously accepted package.

## 10. Independent axes and derived reader eligibility

The following remain independent:

```text
editorial_state
source_verification_state
scholarly_review_label
lifecycle_state
reader_delivery eligibility
retrieval eligibility
evaluation eligibility
training eligibility
public_sharing eligibility
```

No one field substitutes for another.

### 10.1 Editorial state

Owned by Notes. It records whether the prose is drafted, reviewed, revised, or owner-approved for the declared editorial use.

### 10.2 Source verification state

Owned by the Lab for the bounded candidate. It records whether cited source identities, locators, quotations, morphology, and claim support were verified.

### 10.3 Scholarly review label

It must distinguish deterministic/source-verifiable review from qualification-matched specialist review.

Owner approval must not be represented as specialist scholarly review.

### 10.4 Lifecycle state

It records whether the annotation revision is active, superseded, retired, or withdrawn.

### 10.5 Operation-specific eligibility

Each of these is independently decided:

```text
reader_delivery
retrieval
evaluation
training
public_sharing
```

Each decision is one of:

```text
ALLOWED
DISALLOWED
REQUIRES_REVIEW
```

Each binds its authority, evidence, scope, limitations, and decision date.

`training` defaults to `DISALLOWED`.

### 10.6 Derived reader eligibility

Reader delivery is derived only when every required condition is satisfied under the Biblos contract. At minimum:

- the exact Notes projection revision is editorially approved for reader use;
- source verification satisfies the required partition;
- lifecycle state is active;
- `reader_delivery = ALLOWED`;
- every anchor validates against the exact bound Scripture package;
- no required public-safe field is missing;
- correction and supersession relationships are valid;
- the package-level schema and identity validate.

There is no opaque `PACKAGE_ELIGIBLE` authority that hides these independent axes.

## 11. Notes input boundary

The Lab recognizes these Notes record classes:

### `StudyRecord`

The complete editorial master. It may contain research notes, reasoning, source links, unresolved questions, drafting history, and long-form prose.

Rules:

- it remains owned by Notes;
- it is referenced by exact identity and revision;
- it does not enter the reader package directly;
- the Lab does not silently rewrite it.

### `ReaderAnnotationProjection`

The only package-candidate input.

It is the bounded, normative Notes export containing the fields required for validation and compilation. Notes owns its schema.

A future projection should include only fields authorized by that schema, such as:

- projection and export identity;
- annotation identity and revision;
- source `StudyRecord` identity and revision;
- issue category;
- passage and exact Scripture binding;
- proposed anchor;
- short and full reader prose;
- bounded claim statements;
- source-record references;
- interpretive limitations;
- editorial state;
- correction and supersession state;
- operation-specific rights assertions.

This list is descriptive, not a Lab definition of the Notes schema.

### `PublicPost`

Public-facing article, post, teaching, or announcement prose.

It is not automatic philological gold, package input, benchmark gold, evaluation gold, or training data.

### `PersonalReflection`

Private devotional, autobiographical, pastoral, or exploratory writing.

It is excluded by default from:

- package compilation;
- benchmark construction;
- evaluation gold;
- retrieval corpora;
- training corpora;
- public sharing.

Any later exception requires a separate consent, privacy, rights, and design process.

### `SourceRecord`

A Notes reference to a work, edition, source, locator, rights record, or provenance authority.

It may support Lab verification even when the source text may not be redistributed.

A reader package receives only the public-safe source projection allowed by the operation-specific rights decision.

### Validation findings

When a candidate fails validation, the Lab returns structured findings to Notes. The finding may identify:

- stale anchor;
- unsupported claim;
- incorrect source identity;
- unverified quotation;
- morphology mismatch;
- missing qualification;
- rights block;
- review-state insufficiency;
- invalid correction chain.

Notes creates the corrected editorial revision. The Lab does not mutate the editorial master.

## 12. Lab producer responsibilities

Under a later activation, the Lab may:

1. consume an exact, owner-approved `ReaderAnnotationProjection v1` export;
2. validate the export schema and identity;
3. resolve referenced source and editorial revisions;
4. verify exact Scripture, translation, canon, versification, and package bindings;
5. validate UTF-16 anchors and exact expected phrases;
6. verify source and morphology claims;
7. validate claim/evidence/citation relationships and required qualifications;
8. validate independent review states;
9. evaluate operation-specific rights and eligibility;
10. reject unsupported, stale, contradictory, or ineligible candidates;
11. compile accepted records deterministically against the Biblos schema;
12. emit the exact package bytes;
13. emit the detached Lab receipt and checksum evidence;
14. maintain a platform-neutral reference validator;
15. produce candidate spans or findings for human review.

Candidate span generation does not make a span package-eligible. Human editorial review and exact anchor validation remain required.

## 13. Lab prohibitions

The Lab must not:

- alter Scripture text;
- silently edit Notes prose;
- decide Biblos UI or reader behavior;
- publish an unreviewed annotation;
- infer training rights from reader, retrieval, evaluation, or public-sharing rights;
- treat owner approval as specialist scholarly review;
- include PersonalReflection or PublicPost prose automatically;
- import Biblos production internals;
- require a running Lab service in production;
- expose Lab PostgreSQL to Biblos;
- become the production package registry;
- become the reader's saved-state store;
- compile against an unmerged or unidentified Biblos schema;
- retain rejected candidates in the reader package;
- use a model to create final package prose or package identities in the first slice.

## 14. Deterministic compilation posture

The first compiler should be a small, deterministic Lab use case using existing project conventions where appropriate:

- strict Pydantic records;
- RFC 8785 canonical JSON;
- SHA-256;
- immutable typed states;
- explicit source and rights bindings;
- deterministic receipts;
- exact schema validation;
- fail-closed errors;
- append-only supersession;
- no hidden network or model call.

DR-31 authorizes none of that implementation.

The compiler must not own the package schema. It consumes the exact normative Biblos schema as a versioned input.

The compilation receipt is the Lab-owned proof of what happened; it is not required to redefine the reader payload.

## 15. Independent Biblos validation

Biblos must be able to validate and import without contacting the Lab.

At minimum, Biblos independently:

1. verifies the supported package schema identity;
2. parses the exact UTF-8 JSON bytes;
3. validates the package against its normative schema;
4. recomputes the package file SHA-256;
5. verifies any detached checksum and accepted receipt projection used during import;
6. verifies the exact bundled Scripture package and content identities;
7. re-hashes every target verse;
8. applies every UTF-16 code-unit range;
9. requires the extracted phrase to equal the exact expected phrase;
10. rejects invalid or cross-verse anchors;
11. validates independent state axes and `reader_delivery`;
12. validates active correction, supersession, and retirement relationships;
13. rejects unknown required semantics or unsupported schema versions;
14. rejects the package atomically on package-level integrity failure;
15. retains the last independently accepted package when a candidate update fails.

The first John 13 package is bundled with Biblos.

Version one has no:

- remote package registry;
- update service;
- signing infrastructure;
- runtime synchronization;
- vector store;
- shared cross-project database.

## 16. John 1:5 preservation

John 1:5 remains:

```text
COMPLETED_REFERENCE_IMPLEMENTATION
CONFORMANCE_FIXTURE
COMPILER_DESIGN_PRECEDENT
BENCHMARK_SEED
```

It demonstrates:

```text
source admission
→ normalization
→ bounded evidence
→ claim/evidence/citation authority
→ deterministic runtime
→ benchmark
→ full-runtime acquisition
→ immutable publication
→ Study projection
→ reference web workspace
```

No completed John 1:5 artifact is reclassified as failed, obsolete, or product proof beyond its demonstrated scope.

The John 1:5 runtime and web client may inform a future compiler or validator. They must not become a required Biblos runtime dependency.

## 17. Existing-capability reuse map

| Capability | Classification | Rechartered role |
|---|---|---|
| Source admission and source receipts | `REUSE_DIRECTLY` | Verify exact sources used by annotation candidates |
| Canonical archive and publication receipts | `REUSE_DIRECTLY` | Retain Lab source, evidence, package, and receipt authority when separately activated |
| John 1:5 normalization implementation | `REUSE_AFTER_ADAPTER` | Precedent for passage-independent exact text and morphology validation |
| Normalization contracts and receipt patterns | `REUSE_AFTER_ADAPTER` | Bind exact edition, text, token, and morphology coordinates |
| T04 evidence packet | `REUSE_AFTER_ADAPTER` | Precedent for bounded annotation-validation evidence |
| Claim/evidence/citation graph | `REUSE_AFTER_ADAPTER` | Validate annotation statements and qualifications |
| Rights controls | `REUSE_DIRECTLY` | Decide reader, retrieval, evaluation, training, and public-sharing eligibility separately |
| Deterministic Study runtime | `REFERENCE_ONLY` | Reference answer decomposition, correction, and audit behavior |
| PostgreSQL runtime catalog | `REFERENCE_ONLY` | Preserve T05 historical authority; no first-package dependency |
| T07 benchmark harness | `REUSE_AFTER_ADAPTER` | Evaluate packages, retrieval, API subjects, and optional adapted models |
| T08 full-runtime evidence acquisition | `REUSE_AFTER_ADAPTER` | Lab evaluation of evidence acquisition and sufficiency; not package compilation |
| T08 operation ledgers and receipts | `REUSE_AFTER_ADAPTER` | Evaluation and compilation receipt precedent |
| T06 page fixture and page-region contracts | `REFERENCE_ONLY` | Historical multimodal and accessibility fixture |
| T09 workspace projection | `REUSE_AFTER_ADAPTER` | Optional editorial/reference inspection and conformance fixture |
| T09 loopback API and React client | `RETIRED_FROM_CRITICAL_PATH` | Optional internal editorial workspace only |
| DR-22/DR-24 provider/API evaluation methodology and applicable DR-25 safety controls | `REUSE_AFTER_ADAPTER` | Future separately bounded `TNEVAL-A1` through `TNEVAL-A3` evaluation authority |
| Training-corpus designs | `DORMANT_TRAINING_PATH` | Available only after every section 21 gate passes |
| CPT, SFT, and preference designs | `DORMANT_TRAINING_PATH` | Optional future capability-gap experiments after every section 21 gate passes |
| Quantization and distillation | `DORMANT_TRAINING_PATH` | Optional only after a justified parent model and every section 21 gate passes |
| Cloud training, adapted-model hosting, A4, and training-controller designs | `DORMANT_TRAINING_PATH` | Optional only after every section 21 gate passes and a bounded campaign is approved |
| Prior Lab-centered reader/backend architecture | `RETIRED_FROM_CRITICAL_PATH` | Historical reference; Biblos owns production |

These classifications authorize no code or operation.

## 18. API-first evaluation ladder

The canonical repository identifiers are:

```text
TNEVAL-A0
TNEVAL-A1
TNEVAL-A2
TNEVAL-A3
TNEVAL-A4
```

Within DR-31 discussion they correspond to A0 through A4.

Current posture:

```text
TNEVAL-A0
DETERMINISTIC_RETRIEVAL_BASELINE
FUTURE_BOUNDED_DESIGN_OR_ACTIVATION_REQUIRED
NO_PROVIDER_REQUIRED
NOT_IMPLEMENTATION_AUTHORITY

TNEVAL-A1 through TNEVAL-A3
UNSTARTED
NOT_AUTHORIZED
NOT_ON_CURRENT_CRITICAL_PATH
ELIGIBLE_FOR_SEPARATE_BOUNDED_API_EVALUATION_AUTHORITY
NOT_GATED_BY_TRAINING_REACTIVATION

TNEVAL-A4
DORMANT_PENDING_TRAINING_REACTIVATION_GATE
NOT_ON_CURRENT_CRITICAL_PATH
NOT_IMPLEMENTATION_AUTHORITY
```

### `TNEVAL-A0` — approved annotation retrieval only

Input:

- exact user/passage condition;
- independently accepted package;
- deterministic retrieval of approved annotation records.

Purpose:

- establish whether the product need is already satisfied without a model.

A0 is a legitimate final product outcome for every use case it satisfies. It requires a future bounded design or activation but no provider.

### `TNEVAL-A1` — standard cloud model plus approved annotations

Input:

- same frozen cases;
- retrieved approved reader annotations;
- no full Lab evidence packet unless separately declared.

Purpose:

- measure whether ordinary generation adds useful synthesis beyond approved retrieval.

### `TNEVAL-A2` — standard cloud model plus full evidence packet

Input:

- same frozen cases;
- the complete approved evidence condition;
- exact claim, citation, and limitation authority.

Purpose:

- measure the value of fuller grounding and evidence visibility.

### `TNEVAL-A3` — higher-capability grounded reference model

Input:

- the same frozen evidence condition as the approved comparison;
- a higher-capability reference subject.

Purpose:

- establish a practical grounded ceiling without adapting weights.

Before A1–A3 may be authorized, the exact package, evidence, benchmark, rights, privacy, retention, cost, provider, and operational controls must be frozen. They must use applicable DR-22 and DR-24 evaluation controls and applicable DR-25 safety, cost, termination, and cleanup controls. A1–A3 are prerequisites to the training-reactivation decision, not products of that gate.

### `TNEVAL-A4` — optional adapted model

Eligible only after every gate in section 21, the conjunctive training-reactivation gate, passes.

Purpose:

- test one exact, repeated capability-gap hypothesis that A0 through A3 did not adequately solve.

No provider is selected by DR-31. No experiment is authorized.

## 19. Evaluation measures

Every future A0 through A4 comparison must bind exact subject, package, evidence, prompt, tool, provider, model, version, configuration, attempt, scorer, and cost identities.

### Quality

- claim correctness;
- Translation Nuance accuracy;
- morphology accuracy;
- textual-state restraint;
- accepted-alternative coverage;
- required qualification preservation;
- appropriate abstention;
- prohibited-overclaim rate;
- structured-output conformance.

### Support

- supported consequential-claim rate;
- citation coverage;
- citation entailment;
- source-role accuracy;
- incorrect source linkage;
- unsupported claim count;
- evidence-horizon disclosure;
- rights-safe quotation behavior.

### Latency

- retrieval latency;
- request latency;
- time to first usable answer;
- total p50 and p95;
- timeout and retry rates.

### Cost

- cost per request;
- cost per accepted answer;
- cost per supported consequential claim;
- token usage;
- cache effect;
- projected monthly cost under declared use assumptions;
- human-review cost.

### Stability

- schema validity across repeats;
- claim-set consistency;
- citation consistency;
- qualification consistency;
- semantic variance;
- provider-version drift;
- failure-mode stability.

### Product fit

- offline capability;
- privacy and routing;
- evidence-transfer requirements;
- maintenance burden;
- package and context size;
- reader complexity.

Every failed, refused, malformed, timed-out, or provider-error attempt remains in the denominator. No semantic reroll or cherry-picking is permitted.

## 20. Contamination and holdout controls

The existing benchmark firewall applies where relevant.

Future package and API evaluations must:

- cluster by passage, issue, source family, annotation lineage, and source `StudyRecord`;
- keep near-duplicate editorial revisions in one contamination cluster;
- separate public, private, and fresh sets;
- maintain exposure records;
- prevent benchmark gold and scorer-only data from reaching subjects;
- exclude package/evaluation holdouts from training and synthetic-data generation;
- preserve rejected and failed outputs;
- report worst-group and hard-failure results;
- avoid generalizing from John 1:5 alone.

## 21. Conjunctive training-reactivation gate

All gates are required. Failure of one leaves the training path dormant.

### Gate 1 — frozen cross-project contracts

Required:

- merged normative Biblos `TranslationAnnotationPackage v1`;
- merged normative Notes `ReaderAnnotationProjection v1`;
- merged Lab `TranslationAnnotationCompilationReceipt v1`;
- exact serialization, identity, anchor, state, review, rights, and supersession semantics.

### Gate 2 — independently working non-model product

Biblos must independently import, validate, reject, display, update, and roll back packages without a Lab runtime.

### Gate 3 — sufficiently broad source-verified corpus

Required:

- multiple passages;
- multiple issue categories;
- multiple source and translation situations;
- versioned provenance;
- source-quality and independence review;
- enough breadth to test generalization.

John 1:5 and one John 13 package alone are insufficient to authorize training.

### Gate 4 — operation-specific training rights

Every proposed training object must have explicit `training = ALLOWED` authority for the exact operation and resulting artifact.

Reader, retrieval, evaluation, or public-sharing eligibility does not imply training eligibility.

### Gate 5 — completed A0 through A3 baseline

Required:

- frozen cases and holdouts;
- retrieval-only result;
- standard-model annotations result;
- standard-model full-evidence result;
- higher-capability grounded reference result;
- complete cost, latency, quality, support, stability, and failure accounting.

### Gate 6 — realistic product assumptions

Required:

- expected Biblos use cases;
- query volume;
- online/offline expectations;
- latency targets;
- privacy and provider constraints;
- supported devices and contexts;
- expected annotation and evidence scale.

### Gate 7 — cost comparison

Compare:

- deterministic retrieval;
- cloud API routes;
- adapted-model training;
- adapted-model hosting;
- maintenance and evaluation;
- human review;
- local conversion or serving if proposed.

### Gate 8 — repeated measurable capability gap

The proposal must identify a repeated, consequential deficit that A0 through A3 do not adequately solve and that weight adaptation could plausibly repair.

“Data exist,” “credits remain,” or “a model can be trained” is not a capability-gap hypothesis.

### Gate 9 — contamination-safe holdouts

Required:

- private holdout;
- fresh post-freeze set;
- cluster-level separation;
- exposure ledger;
- leakage tests;
- protected scorer authority.

### Gate 10 — exact experiment specification

The proposal must freeze:

- parent model and license;
- exact data projection;
- objective;
- trainable components;
- tokenizer and processor;
- prompt and runtime conditions;
- baselines and ablations;
- primary and protected metrics;
- stop and promotion rules.

### Gate 11 — bounded budget and stop condition

Required:

- compute;
- storage;
- provider/API spend;
- human review;
- maximum attempts;
- automatic stop-loss;
- artifact-retention and provider-cleanup plan.

### Gate 12 — capability retention and rollback

Required:

- parent-relative preservation suite;
- unsupported-claim and safety limits;
- exact lineage;
- immutable artifacts;
- rollback plan;
- release limitations.

### Gate 13 — separate owner authorization

Joseph must separately authorize one exact experiment, including model, data projection, objective, provider or hardware, budget, and stop condition.

No general DR approval or old cloud allowance substitutes for that authorization.

## 22. Technique-specific evaluation and training requirements

### `TNEVAL-A1` through `TNEVAL-A3` provider/API evaluation

A1–A3 are not gated by section 21. Each requires a separate bounded evaluation design and activation that freezes:

- exact package and evidence conditions;
- benchmark cases, holdouts, scorers, and failure accounting;
- provider, model, version, route, prompts, tools, and attempt limits;
- operation-specific rights and provider-routing authority;
- privacy, retention, deletion, and output-handling policy;
- latency, cost, budget, timeout, retry, and stop conditions;
- raw-output and result-bundle retention;
- provider termination and cleanup evidence where applicable.

They must use applicable DR-22 and DR-24 evaluation controls and applicable DR-25 operational safety, cost, termination, and cleanup controls. They do not require DR-23 training-harness authority, do not change weights, and do not authorize A4.

### Continued pretraining

Additionally requires:

- corpus-level training rights;
- composition and sampling evidence;
- a demonstrated representation gap not adequately solved by retrieval;
- general and multilingual capability preservation.

### Supervised fine-tuning

Additionally requires:

- training eligibility for each prompt/answer object;
- reviewed answer authority;
- separation of editorial prose, reader notes, benchmark gold, and synthetic candidates.

### Preference optimization

Additionally requires:

- typed judgments;
- reviewer role and consent;
- evidence that preferences describe behavior rather than factual truth;
- absolute quality and support gates;
- matched parent comparison.

### Quantization

Additionally requires:

- justified parent model;
- exact conversion lineage;
- product deployment requirement;
- semantic and capability-regression evidence.

Quantization is not authorized merely because a model fits a device.

### Distillation

Additionally requires:

- teacher-output authority;
- exact teacher identity and configuration;
- output provenance and contamination controls;
- evidence that a student is economically or operationally necessary.

### Cloud training or `TNEVAL-A4` adapted-model evaluation

Additionally requires every gate in section 21 and the applicable DR-23, DR-24, and DR-25 envelope, budget, artifact, termination, and cleanup controls.

Ordinary A1–A3 provider/API evaluation is excluded from this subsection and follows the separately bounded requirements above.

## 23. Formal pause effect

Upon persistence of DR-31 and `BSL-STATUS-01`, current Lab status is:

```text
PAUSED_AFTER_VS01_T09B
```

VS01-T09B:

```text
MERGED_AND_COMPLETE
```

VS01-T09-OP01:

```text
OPTIONAL_EDITORIAL_ACCEPTANCE
DEFERRED_INDEFINITELY
NOT_ON_CRITICAL_PATH
```

VS01-T10 and later original tasks:

```text
UNSTARTED
NOT_AUTHORIZED
```

Training, learned-model serving or conversion, cloud-training, adapted-model hosting, `TNEVAL-A4`, and related controller paths:

```text
DORMANT_PENDING_TRAINING_REACTIVATION_GATE
NOT_ON_CURRENT_CRITICAL_PATH
NOT_IMPLEMENTATION_AUTHORITY
```

`TNEVAL-A0`:

```text
DETERMINISTIC_RETRIEVAL_BASELINE
FUTURE_BOUNDED_DESIGN_OR_ACTIVATION_REQUIRED
NO_PROVIDER_REQUIRED
NOT_IMPLEMENTATION_AUTHORITY
```

`TNEVAL-A1` through `TNEVAL-A3`:

```text
UNSTARTED
NOT_AUTHORIZED
NOT_ON_CURRENT_CRITICAL_PATH
ELIGIBLE_FOR_SEPARATE_BOUNDED_API_EVALUATION_AUTHORITY
NOT_GATED_BY_TRAINING_REACTIVATION
```

This is a forward-program disposition only. It creates no evaluation, provider, implementation, or operational authority.

## 24. Future John 13 cross-project slice

The future path is proposed, not activated:

```text
Biblos P1-T12 merges the exact normative consumer schema
    ↓
Notes freezes 6–10 ReaderAnnotationProjection records
    ↓
Lab verifies the required John 13 source scope
    ↓
Lab compiles the exact TranslationAnnotationPackage v1
    ↓
Lab emits TranslationAnnotationCompilationReceipt v1 and checksum
    ↓
Biblos independently validates the real package
    ↓
Biblos P1-T13 implements the reader experience
```

The future batch must eventually demonstrate:

- multiple issue categories;
- at least one textual-state restraint;
- at least one rejected candidate;
- at least one corrected or superseding revision;
- exact ordered anchors, including multiple anchors when needed;
- independent review-state axes;
- operation-specific rights;
- zero model requirement for package prose or compilation.

DR-31 does not:

- choose the exact annotations;
- approve a John 13 source plan;
- acquire sources;
- create the Notes projection schema;
- create the Biblos package schema;
- create the Lab receipt schema;
- implement a compiler;
- compile a package;
- activate P1-T12 or P1-T13 work;
- authorize provider evaluation.

## 25. Anti-duplication and anti-slop

The following must not be built for the first package slice:

- another reader UI;
- a second production backend;
- a generic annotation CMS;
- a shared cross-project database;
- an online package registry;
- a live repository synchronization service;
- an annotation-specific vector database;
- a model gateway;
- a training orchestrator;
- a Lambda controller;
- a local model server;
- a second web client;
- a generic plugin framework;
- speculative multi-passage abstractions;
- Lab PostgreSQL changes;
- a generic package abstraction with no second real package format;
- a new service boundary without a demonstrated security or lifecycle need.

The first future compiler should reuse existing Python, Pydantic, canonical-JSON, hashing, evidence, rights, immutable-state, and receipt infrastructure where the activated contract actually requires it.

DR-31 authorizes:

```text
new dependencies        0
new persistent stores   0
new schemas             0
new endpoints           0
new migrations          0
new implementation      0
```

## 26. Production independence

Biblos must remain able to:

- read Scripture without a Lab process;
- validate a package offline;
- bundle an accepted package;
- continue with the last accepted package if a candidate fails;
- roll back package revisions;
- preserve saved reader state;
- function when the Lab repository, archive, web client, API, and PostgreSQL are unavailable.

No production dependency is created on:

- Lab PostgreSQL;
- the T09 loopback API;
- the T09 React client;
- the Lab archive mount;
- Lab credentials;
- Lab model routes;
- Lab cloud infrastructure.

## 27. Change control

A later change requires a new design or amendment when it would:

- alter one of the three cross-project contracts;
- change contract ownership;
- change package identity or anchor semantics;
- add a fourth shared contract;
- add a production Lab service dependency;
- add a remote registry or update service;
- change operation-specific rights semantics;
- activate a source plan;
- activate package implementation;
- activate API or model evaluation;
- reactivate training or cloud work;
- change the John 13 batch scope materially;
- add a persistent store, dependency family, endpoint, or migration.

## 28. Explicit non-goals

DR-31 is not:

- a package schema;
- a Notes export schema;
- a compilation-receipt schema;
- a compiler;
- a validator implementation;
- a source plan;
- an annotation batch;
- an API-provider selection;
- an experiment design;
- a training authorization;
- a cloud campaign;
- a Biblos UI design;
- an online service design;
- an approval of T09-OP01 or T10.

## 29. Freeze statement

> **DR-31 preserves the completed John 1:5 system and DR-01 through DR-30 while changing the Lab's forward program role. Biblos is the final production reader and owns the normative TranslationAnnotationPackage v1 consumer schema. Biblical Scholar Notes is the editorial master and owns ReaderAnnotationProjection v1. Biblical Scholar Lab owns source, linguistic, claim, review, rights, deterministic compilation, TranslationAnnotationCompilationReceipt v1, reference validation, API-first evaluation, contamination controls, and optional future model research. The Lab is not a required Biblos runtime service. The first John 13 package is a future offline bundled artifact, not a remote service. A0 retrieval is a legitimate final outcome. A0–A3 remain unstarted and unauthorized; A1–A3 may later receive separate bounded provider/API evaluation authority and are not gated by training reactivation. They must precede any training decision. Training, learned-model serving or conversion, cloud-training, adapted-model hosting, and A4 remain dormant until every gate in section 21 is satisfied and Joseph separately authorizes one exact experiment.**
