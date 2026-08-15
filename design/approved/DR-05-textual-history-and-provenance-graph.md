# DR-05 — Textual-History and Provenance Graph

| Field | Value |
|---|---|
| Design ID | `DR-05` |
| Status | `APPROVED` |
| Approval date | 2026-08-15 |
| Project owner | Joseph Abbud |
| Designer and independent reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2; DR-03; DR-04 |
| Implementation authority | GPT-5.6 Sol, under the approved design |

## 1. Purpose

Biblical Scholar Lab needs a textual-history and provenance architecture capable of answering not only:

> What text does the system have?

but also:

> What physical or digital source does this representation come from? Who observed, transcribed, edited, translated, normalized, aligned, or asserted it? What method and evidence support the relationship? Which later artifacts depend on it? What is known directly, what is reconstructed, what is disputed, and what remains unexamined?

This design defines the logical graph for:

- physical text-bearing artifacts and their parts;
- digital surrogates and exact source files;
- written marks, recognized graphemes, transcriptions, normalized texts, editions, translations, and annotations;
- witnesses and witness coverage;
- copying, correction, revision, translation, compilation, quotation, and other textual-history relationships;
- human, institutional, software, and model agents;
- observations, assertions, arguments, methods, evidence, and counterevidence;
- computational derivation and reproducibility;
- immutable revisions, retractions, and graph snapshots;
- exact source-span and image-region provenance;
- impact analysis when a source, mapping, or claim changes;
- interoperability with established cultural-heritage, textual-editing, annotation, image, and provenance standards.

DR-05 supplies the graph substrate required by the Translation Nuance Core, linguistic representation, ancient-version policy, scholarship and citation model, corpus pipeline, retrieval system, benchmark, and training harness.

## 2. Governing principle

> **Textual history, material custody, digital derivation, and scholarly belief are different kinds of provenance. The system must represent each explicitly and must never turn a disputed relationship or editorial inference into an unlabeled fact.**

The graph must preserve a recoverable path from every derived text span, annotation, claim, benchmark case, and training record back to exact source evidence and the activities that produced it.

## 3. Four provenance domains must remain separate

The word *provenance* is overloaded. Biblical Scholar Lab will represent at least four distinct domains.

### 3.1 Material and custodial provenance

The history of a physical object or object part, including:

- production or writing;
- physical composition and parts;
- correction and modification;
- damage and restoration;
- ownership and custody;
- acquisition and transfer;
- current repository and shelfmark;
- fragment separation or virtual reconstruction.

A custody claim is not a claim about textual ancestry.

### 3.2 Textual transmission and intellectual lineage

Relationships among textual representations, including:

- copying;
- exemplar use;
- contamination from multiple sources;
- recension or revision;
- translation;
- daughter-version dependence;
- quotation;
- harmonization;
- editorial compilation;
- reconstructed or conjectural text;
- modern translation revision families.

These relationships are normally scholarly claims, not directly observed facts.

### 3.3 Digital and computational provenance

The derivation of digital resources, including:

- photography and scanning;
- file acquisition;
- OCR or handwritten-text recognition;
- transcription;
- transliteration;
- Unicode normalization;
- tokenization;
- parsing;
- collation;
- alignment;
- deduplication;
- dataset materialization;
- indexing;
- model generation;
- evaluation and report generation.

This domain must be sufficiently exact to reproduce or audit a result.

### 3.4 Epistemic and assertion provenance

The history of who asserted, adopted, inferred, reviewed, rejected, or retracted a claim; what evidence and method were used; and how strongly the claimant held it.

Examples include:

- authorship attribution;
- dating;
- place of origin;
- scribal-hand identification;
- identification of a reading;
- claim of translation dependence;
- proposed source text or *Vorlage*;
- classification of a quotation or allusion;
- textual-family or stemmatic hypothesis;
- project decision to use an assertion operationally.

No domain may be substituted silently for another. For example, a digital file's derivation from a printed edition does not prove the printed edition's claim about a manuscript, and a manuscript's custody history does not prove its textual genealogy.

## 4. Logical architecture layers

The normative graph contains five logical layers.

### 4.1 Identity layer

Stable identities for physical objects, conceptual works, textual forms, editions, source artifacts, agents, methods, activities, and other addressable entities.

### 4.2 Evidence and observation layer

Directly inspected or source-reported observations, each anchored to exact evidence and scope.

### 4.3 Assertion and argument layer

Claims, denials, uncertainty, competing interpretations, premises, inference methods, conclusions, and review state.

### 4.4 Derivation and activity layer

Qualified transformations connecting exact input revisions, activities, agents, configurations, and output revisions.

### 4.5 Operational projection layer

Versioned project selections and rebuildable indexes used for retrieval, training, display, or evaluation. Operational selections do not erase competing assertions and do not become timeless truth.

## 5. Stable identity and immutable revision

Every graph object that may change over time uses two identities:

```text
stable_entity_id
revision_id
```

The stable entity identifies the continuing thing or conceptual object. The revision identifies one immutable recorded state.

A revision contains:

```text
revision_id
stable_entity_id
schema_version
created_at
created_by_agent_id
content_hash
supersedes_revision_id?
invalidation_or_retraction_status
provenance_bundle_id
```

Rules:

1. Committed revisions are immutable.
2. Corrections create new revisions.
3. A revision may be superseded without being deleted.
4. Historical references remain bound to the revision used at the time.
5. Content hashes describe canonical serialized content or exact bytes, according to entity type.
6. Stable IDs must not encode mutable titles, repository locations, dates, canon membership, or scholarly conclusions.

Physical objects may change through events; descriptions of them are revised assertions rather than destructive updates to historical state.

## 6. Intrinsic facts, imported metadata, scholarly claims, and operational decisions

The graph must distinguish four record classes.

### 6.1 Intrinsic system facts

Mechanically established facts such as:

- a file's exact hash;
- byte length;
- media type;
- schema version;
- ingestion timestamp;
- internal revision identity.

These may be stored as normative fields.

### 6.2 Imported source assertions

Metadata or claims made by a provider, catalog, edition, article, or dataset.

Examples:

- a repository-supplied date;
- a catalog attribution;
- a dataset's witness siglum;
- a translation preface's statement of source text.

They remain attributed to the source and are not automatically project-endorsed.

### 6.3 Scholarly or project assertions

Evidence-bearing propositions created or adopted by scholars, curators, project reviewers, algorithms, or models.

Conflicting assertions may coexist.

### 6.4 Operational selection decisions

A versioned project decision that one or more assertions may be used for a bounded purpose, such as:

- resolving a user query;
- constructing a training split;
- displaying a probable date;
- selecting a source-text relation for an experiment.

An operational selection records its scope, rationale, approver, evidence, applicable design ID, and expiration or review condition. It is not a claim that alternatives are false.

## 7. Core physical and documentary entities

### 7.1 `PhysicalTextBearingObject`

A physical carrier or composite object bearing or containing text, such as:

- codex;
- scroll;
- papyrus;
- parchment leaf;
- tablet;
- ostracon;
- inscription;
- printed volume;
- photographically printed page;
- microfilm or other physical surrogate.

### 7.2 `PhysicalObjectPart`

An addressable physical component or region, such as:

- codicological unit;
- fragment;
- leaf;
- folio side;
- page;
- column;
- line;
- margin;
- writing field;
- binding component;
- inscribed surface;
- damaged region.

Containment is versioned and time-aware where an object's composition changed.

### 7.3 `WrittenMarkRegion`

A bounded region containing physical visual or tactile marks intended or interpreted as writing.

Physical marks are not identical to recognized graphemes or transcribed characters.

### 7.4 `RepositoryHolding`

A time-bounded relation among a physical object, repository or custodian, shelfmark or identifier, and evidence.

Current location, ownership, and custody are separate where necessary.

### 7.5 `DigitalSurrogate`

A digital representation of a physical object or part, such as an image, PDF page, multispectral capture, three-dimensional scan, audio record, or video.

A surrogate must identify:

- represented physical object or part;
- capture activity;
- device and parameters where available;
- image or media dimensions;
- exact file revision;
- rights and provider;
- transformations such as crop, color correction, deskewing, or compression.

## 8. Work, textual form, edition, and representation

DR-04's `WorkFamily`, `WorkComponent`, `TextualForm`, `Edition`, `SourceArtifact`, `TextSegment`, and reference entities remain authoritative.

DR-05 adds the provenance-bearing representation layer.

### 8.1 `TextualRepresentation`

A stable identity for an identifiable representation of textual content, such as:

- diplomatic transcription;
- normalized transcription;
- transliteration;
- reconstructed text;
- critical text;
- reading text;
- translation;
- OCR output;
- linguistic annotation stream;
- model-generated proposal.

### 8.2 `TextualRepresentationRevision`

An immutable version of a textual representation, tied to exact source inputs and a generating or revising activity.

### 8.3 `RepresentationSegmentRevision`

An addressable segment of one immutable representation revision. It may bind to one or more DR-04 `TextSegment` identities and uses selectors to preserve exact source scope.

### 8.4 Representation type is mandatory

Every representation must state what it is. A normalized text may not masquerade as a diplomatic transcription; an OCR output may not masquerade as human-reviewed text; a reconstructed reading may not masquerade as directly witnessed wording.

## 9. Written marks, graphemes, readings, and transcriptions are distinct

The graph must support the following chain when evidence requires it:

```text
physical written marks
  → image or direct autopsy
  → glyph or grapheme observations
  → reading interpretation
  → diplomatic transcription
  → normalized transcription
  → linguistic analysis
```

The chain may begin at a later stage for born-digital or already curated sources, but omitted earlier stages must not be invented.

### 9.1 `TextRecognitionActivity`

An activity in which a human or system identifies physical features as writing and proposes graphemes, characters, words, or readings.

### 9.2 `GraphemeObservation`

A scoped observation connecting a physical or image region to one or more candidate grapheme interpretations.

### 9.3 `ReadingObservation`

A scoped observation of what a witness appears to read at a locus. It records:

- target artifact or representation revision;
- selector or passage scope;
- observed or proposed reading;
- observer;
- observation method;
- direct autopsy versus surrogate use;
- confidence or uncertainty;
- damage, correction, hand, abbreviation, illegibility, or other conditions;
- exact evidence region;
- time of observation.

Two scholars may record different reading observations of the same marks without either observation being overwritten.

### 9.4 `TranscriptionActivity`

An activity that converts interpreted written marks or an existing textual representation into an explicitly typed transcription revision.

### 9.5 `TransliterationActivity`

An activity that re-encodes graphemes or characters in another writing system according to a stated scheme without silently treating the output as translation.

## 10. Witness is a role, not a universal object class

The term *witness* is context-dependent. A manuscript, printed edition, ancient translation, quotation, or patristic citation may function as a witness for a particular textual question.

The system therefore uses:

```text
WitnessRoleAssignment
  witness_role_id
  bearer_entity_revision_id
  witnessed_work_or_textual_form_id
  passage_or_segment_scope
  witness_type
  assignment_assertion_id
  siglum_or_external_aliases
  coverage_status
```

A physical codex is not globally and permanently “a witness” to one work. It may contain several works, mixed textual affiliations, lacunae, corrections, and later hands.

A single witness may attest different textual relationships at different passages. No whole-document textual-family label may be projected automatically onto every segment.

## 11. Witness coverage and absence states

The graph must distinguish:

```text
ATTESTED
ABSENT_IN_EXAMINED_SCOPE
LACUNOSE_OR_DAMAGED
OUTSIDE_WITNESS_COVERAGE
NOT_COLLATED
NOT_EXAMINED
NOT_APPLICABLE
UNKNOWN
```

A missing database entry is not evidence of absence.

An absence assertion must identify:

- the searched or examined source;
- exact passage or segment scope;
- method;
- expected completeness;
- observer or responsible agent;
- time and source revision.

Negative evidence may not be inferred from silence unless the graph records why the evidence should have been present.

## 12. Variation units, readings, and attestations

### 12.1 `VariationUnit`

A versioned editorial or analytical grouping of a locus and its compared readings.

A variation unit is not assumed to be an objective natural boundary. It records the responsible agent, method, base or parallel-segmentation strategy, and source.

### 12.2 `ReadingForm`

A representation of one reading within a variation unit. It may preserve:

- diplomatic form;
- normalized form;
- omissions or additions;
- uncertain characters;
- editorial supplements;
- subvariation grouping;
- relation to a base or lemma, if one is used.

### 12.3 `ReadingAttestationAssertion`

An assertion that a witness role supports, partially supports, does not support, or cannot be assessed for a reading form at a locus.

The assertion records who made the judgment and whether it came from direct examination, a transcription, an apparatus, or another secondary source.

### 12.4 Conjecture is not witness attestation

A conjectural emendation, reconstructed reading, or editorial preference may appear in a variation unit but must never be represented as physically attested unless evidence identifies a witness.

## 13. Textual-history activities and relationship claims

The system distinguishes an event or activity from a claim that the activity occurred.

Relevant activity types include:

```text
COMPOSITION
REDACTION
COPYING
INSCRIPTION_OR_WRITING
CORRECTION
ERASURE
SUPPLEMENTATION
RECENSION_OR_REVISION
TRANSLATION
DAUGHTER_VERSION_TRANSLATION
COMPILATION
QUOTATION_OR_EXCERPTION
EDITORIAL_RECONSTRUCTION
CONJECTURAL_EMENDATION
CRITICAL_EDITION_CREATION
TRANSCRIPTION
TRANSLITERATION
NORMALIZATION
COLLATION
ALIGNMENT
ANNOTATION
DIGITIZATION
OCR_OR_HTR
INGESTION
DATA_TRANSFORMATION
MODEL_GENERATION
HUMAN_REVIEW
```

Directly documented modern activities may be normative provenance events. Ancient copying, redaction, exemplar use, or translation-source events are normally represented through evidence-bearing assertions or hypotheses.

## 14. Textual genealogy is a hypothesis graph, not a fixed tree

The model must permit:

- multiple exemplars;
- contamination;
- correction from another source;
- mixed textual affiliation;
- passage-local relationships;
- uncertainty and competing stemmata;
- relationships that cannot be oriented confidently;
- revisions influenced by both a predecessor translation and an original-language source.

A `TextualGenealogyHypothesis` contains:

```text
genealogy_hypothesis_id
scope
relationship_assertions[]
method
premises[]
evidence[]
counterevidence[]
responsible_agent
status
confidence_dimensions
source_publication
review_state
```

No algorithmic clustering or stemma becomes project truth without an approved assertion and evidence path.

## 15. Relation assertions rather than unlabeled truth edges

Consequential historical and scholarly relationships are represented as assertions.

Examples include:

```text
ATTRIBUTED_TO
TRADITIONALLY_ATTRIBUTED_TO
DATED_TO
ORIGINATED_AT
COPIED_FROM
INFLUENCED_BY_TEXTUAL_SOURCE
REVISED_FROM
TRANSLATED_FROM
DAUGHTER_VERSION_OF
USES_BASE_TEXT
QUOTES
ALLUDES_TO
PARAPHRASES
HARMONIZES_WITH
ATTESTS_TEXTUAL_FORM
BELONGS_TO_TEXTUAL_FAMILY
WRITTEN_BY_HAND
CORRECTED_BY_HAND
IDENTIFIED_AS
```

A relation assertion records its subject, predicate, object or value, scope, claimant, method, evidence, counterevidence, epistemic status, and workflow state.

Direct graph edges may be materialized for performance only as rebuildable projections of assertion records.

### 15.1 Temporal and spatial qualification

Historical dates, places, and sequences are frequently uncertain and must not be reduced to unqualified scalar fields.

A temporal or spatial assertion may include:

```text
earliest_possible
latest_possible
preferred_interval?
calendar_or_era
precision
approximation_type
relative_order_assertions[]
place_or_gazetteer_refs[]
historical_place_name
geometry_or_region?
method
basis
confidence_dimensions
```

Rules:

1. Modern system timestamps are intrinsic technical facts; ancient or historical dates are normally assertions.
2. `not before`, `not after`, approximate, disputed, relative, and unknown dates remain distinguishable.
3. A repository's present location is not the object's place of origin.
4. Modern political geography must not be projected silently onto ancient places.
5. Relative sequence may be recorded even when absolute dating is unavailable.
6. Calendar conversions preserve the original expression and conversion method.

## 16. Claim and assertion contract

The normative logical assertion record is:

```text
Assertion
  assertion_id
  revision_id
  proposition_id
  subject_ref
  predicate_id
  object_ref_or_literal
  polarity
  claim_type
  scope_selector
  claimant_agent_id
  asserted_at
  source_assertion_ref?
  method_id?
  evidence_refs[]
  counterevidence_refs[]
  epistemic_status
  confidence_dimensions
  origin_class
  workflow_state
  review_records[]
  valid_time_or_applicability?
  content_hash
```

`polarity` supports at least:

```text
AFFIRMS
DENIES
UNDETERMINED
```

`origin_class` supports at least:

```text
DIRECT_OBSERVATION
SOURCE_REPORTED
SCHOLARLY_INFERENCE
PROJECT_CURATED
ALGORITHMIC_CANDIDATE
MODEL_GENERATED_CANDIDATE
USER_ASSERTED
IMPORTED_UNKNOWN
```

Workflow state and epistemic status are separate. A human-reviewed assertion may remain contested; an unreviewed source assertion may still accurately report what its source says.

## 17. Arguments and inference provenance

Where a conclusion depends on premises and method, the graph uses:

```text
ArgumentationActivity
  argumentation_id
  responsible_agent
  premise_assertion_ids[]
  evidence_refs[]
  inference_method_id
  conclusion_assertion_ids[]
  assumptions[]
  counterarguments[]
  performed_at
  source_publication?
  review_state
```

This supports impact analysis when a premise changes and makes methodology inspectable.

### 17.1 Evidence dependency and independence

The graph must preserve whether apparently separate evidence items depend on one another.

Examples include:

- several translations revising one predecessor;
- several articles repeating one apparatus entry;
- a catalog copying another catalog's attribution;
- an OCR dataset derived from a published transcription;
- a model answer derived from retrieved summaries rather than primary sources;
- several witness readings reported through one secondary edition.

An `EvidenceDependencyAssertion` may classify a relationship as:

```text
DIRECT_DERIVATION
COMMON_UPSTREAM_SOURCE
QUOTATION_OR_RESTATEMENT
REVISION_DEPENDENCE
SHARED_DATASET
SHARED_WITNESS_REPORT
POSSIBLY_DEPENDENT
INDEPENDENT_WITHIN_DEFINED_SCOPE
UNKNOWN
```

The system must not count inherited or repeated claims as independent corroboration merely because they appear in multiple records. Claims of independence require a stated scope and evidence.

The project should support interoperability with argumentation models such as CRMinf, but the internal contract remains the approved Biblical Scholar Lab ontology.

## 18. Agents, roles, and responsibility

### 18.1 Agent types

```text
PERSON
ORGANIZATION
SOFTWARE_AGENT
MODEL_AGENT
COLLECTIVE_OR_TEAM
UNKNOWN_AGENT
```

### 18.2 Roles are activity-specific

An agent may act as:

- author;
- scribe;
- corrector;
- translator;
- editor;
- cataloger;
- photographer;
- transcriber;
- annotator;
- reviewer;
- software operator;
- model generator;
- source provider;
- rights holder;
- project approver.

Authorship, physical inscription, transcription, editorial responsibility, and software generation are never collapsed into one generic `creator` field.

### 18.3 Delegation and software responsibility

A computational activity records:

- software or model agent;
- human or organizational operator;
- applicable plan or configuration;
- delegated role;
- code and environment identity.

A model output remains attributed to the exact model revision and generation activity even after a human reviews it.

## 19. Methods, plans, configurations, and environments

Every material transformation or inference identifies its method.

A `MethodRevision` may represent:

- editorial method;
- collation rules;
- OCR model;
- transliteration scheme;
- normalization policy;
- inference logic;
- alignment algorithm;
- statistical method;
- prompt template;
- training or evaluation procedure.

A computational activity records, where applicable:

```text
code_commit
container_or_environment_digest
dependency_lock_hash
configuration_hash
random_seed
hardware_identity
model_revision
tokenizer_revision
input_manifest_hash
output_manifest_hash
start_and_end_time
```

Nondeterministic activities must state that they are nondeterministic and preserve enough identity to rerun or bound the variation.

## 20. Qualified derivation contract

A generic `derived_from` edge is insufficient for consequential outputs.

The normative derivation record is:

```text
Derivation
  derivation_id
  output_entity_revision_id
  input_entity_revision_ids[]
  activity_id
  derivation_type
  used_scopes_or_selectors[]
  generated_scope?
  agent_associations[]
  method_revision_id
  configuration_revision_id?
  generated_at
  content_hashes
  determinism_class
  validation_result
```

`derivation_type` includes:

```text
COPY
REVISION
QUOTATION
PRIMARY_SOURCE_USE
DIGITIZATION
TRANSCRIPTION
TRANSLITERATION
NORMALIZATION
OCR_OR_HTR
COLLATION
ALIGNMENT
ANNOTATION
AGGREGATION
FILTERING
TOKENIZATION
INDEXING
MODEL_GENERATION
HUMAN_EDIT
OTHER_QUALIFIED
```

The system may expose a simplified provenance path to users while retaining the qualified record internally.

## 21. Source artifacts and exact byte provenance

Every acquired digital source has an immutable `SourceArtifactRevision` containing:

```text
source_artifact_id
revision_id
provider
source_uri_or_locator
retrieved_at
provider_revision_or_release
media_type
byte_length
sha256_or_stronger_hash
rights_record_id
acquisition_activity_id
original_filename
storage_partition
availability_status
```

Rules:

1. Raw bytes are never silently overwritten.
2. Upstream changes create new revisions.
3. A URL is not a version identity.
4. A source artifact may be unavailable for redistribution while its metadata and hash remain referenceable.
5. Remote-only evidence must preserve sufficient state and locator information to identify the exact representation inspected.
6. Derived text cannot be promoted if its source artifact cannot be identified.

## 22. Segment selectors and source anchoring

Annotations and assertions frequently target part of a resource rather than the entire resource.

The project therefore supports selector types including:

```text
TEXT_POSITION
TEXT_QUOTE_WITH_CONTEXT
TOKEN_RANGE
LINE_RANGE
PAGE_REGION
CANVAS_REGION
TIME_RANGE
BYTE_RANGE
XML_OR_JSON_PATH
DR04_REFERENCE_SELECTION
COMPOSITE_SELECTOR
```

A target includes both:

- a source revision or immutable state; and
- one or more selectors for the intended segment.

Multiple selectors may describe the same target to increase recoverability. Position selectors alone are insufficient for mutable text; quote/context selectors or revision hashes should accompany them where practical.

## 23. Image and IIIF integration

For IIIF-compatible sources, the system preserves external identities for:

- collection;
- manifest;
- canvas;
- range;
- annotation page;
- annotation;
- image service;
- spatial or temporal selector.

A IIIF Canvas or region remains an external presentation coordinate, not the project's physical-object identity.

The graph may associate:

```text
physical object part
  ↔ IIIF canvas
  ↔ image resource
  ↔ selected page region
  ↔ reading observation
  ↔ transcription segment
```

OCR, manual transcriptions, translations, and commentary must remain distinguishable annotation motivations or project relation types.

## 24. TEI and apparatus interoperability

The system must ingest and export relevant TEI structures without flattening them.

Important distinctions include:

- manuscript identity and parts;
- physical description and history;
- source transcriptions;
- apparatus entries;
- lemmas and readings;
- witness lists and witness detail;
- responsible agents;
- certainty;
- hands;
- conjectures;
- embedded versus stand-off apparatus;
- source text versus editorial interpretation.

TEI encodings are source representations. The project records the exact TEI revision and maps its structures into the internal model. It does not treat one editor's apparatus grouping, base text, or witness classification as method-free truth.

## 25. External ontology alignment policy

Biblical Scholar Lab will support explicit versioned mappings to established standards while retaining its own normative logical model.

### 25.1 W3C PROV-O

Used as the primary interoperability model for:

- entities;
- activities;
- agents;
- generation;
- usage;
- attribution;
- association;
- delegation;
- revision;
- quotation;
- primary-source derivation;
- qualified derivation.

### 25.2 CIDOC CRM and extensions

Used for cultural-heritage interoperability, especially:

- physical and conceptual objects;
- events and activities;
- information and linguistic objects;
- manuscript and custody history;
- digital provenance through CRMdig;
- written marks, recognition, transliteration, and ancient-text study through CRMtex;
- scholarly argument and provenance claims through CRMinf.

### 25.3 Web Annotation

Used as an interoperability model for bodies, targets, selectors, resource states, creators, and generated annotations.

### 25.4 IIIF Presentation API

Used for image and compound-object presentation coordinates, not as a complete scholarly ontology.

### 25.5 TEI

Used for textual encoding, manuscript descriptions, transcriptions, apparatuses, responsibility, certainty, and source interchange.

### 25.6 Adapter rule

No external standard silently becomes the internal source of truth. Every mapping is:

- namespaced;
- versioned;
- testable;
- documented as exact, close, partial, or project-specific;
- reversible where practical.

## 26. Granularity policy

The graph must preserve exact provenance without requiring a permanent node for every character in every corpus.

### 26.1 Required minimum granularity

Every admitted source must support provenance at:

- source-artifact revision;
- document or work representation revision;
- addressable segment sufficient for exact citation and training traceability.

### 26.2 Optional fine granularity

Token, grapheme, glyph, or image-region nodes are materialized when required for:

- manuscript or page-image analysis;
- critical apparatus;
- linguistic annotation;
- Translation Nuance alignment;
- benchmark gold evidence;
- error analysis.

### 26.3 Inheritance

Shared provenance may be attached through a `ProvenanceBundle` inherited by child segments, with explicit overrides. Any query must be able to expand inherited provenance into a complete effective record.

### 26.4 No provenance-free denormalization

Performance projections may duplicate data, but every projected field must retain a pointer to the authoritative revision and assertion from which it was derived.

## 27. Graph snapshots and reproducibility

A benchmark, corpus materialization, model run, or published report must bind to an immutable `KnowledgeGraphSnapshot`.

```text
KnowledgeGraphSnapshot
  snapshot_id
  schema_revision
  included_entity_revisions_manifest
  included_assertion_revisions_manifest
  operational_selection_manifest
  rights_partition_manifest
  generated_at
  generating_activity_id
  content_or_merkle_hash
  parent_snapshot_id?
  release_status
```

A snapshot is the unit of reproducibility. “Latest graph” is never a valid identity for a training or evaluation run.

Snapshots may be incremental internally, but their effective contents must be independently verifiable.

## 28. Conflict and disagreement policy

The graph uses no scholarly last-write-wins policy.

When assertions conflict:

- both remain present;
- each retains source, method, claimant, and evidence;
- the conflict is discoverable;
- an operational selection may identify the preferred assertion for a bounded use;
- the selection records rationale and approver;
- later evidence creates a new selection or assertion revision rather than rewriting history.

A source provider's correction may invalidate a prior source revision for current use, but historical runs remain bound to the prior revision.

## 29. Identity resolution and duplicate control

Potential duplicate entities are represented first as candidates.

An `IdentityResolutionAssertion` records:

```text
SAME_ENTITY
PROBABLY_SAME
POSSIBLY_SAME
DISTINCT
UNKNOWN
```

Automatic matching by title, name, shelfmark, checksum, or text similarity may propose candidates but may not merge stable identities when the consequence is material.

Merging requires:

- evidence;
- review;
- redirect or equivalence records;
- preservation of all former identifiers;
- reversible audit history.

## 30. Model-generated and synthetic content

Any language-model or algorithmic output is initially a candidate artifact or assertion.

It records:

- exact model and tokenizer revision;
- system and user prompt or prompt-template revision;
- tools and retrieved evidence;
- decoding configuration;
- seed where applicable;
- generation timestamp;
- output hash;
- parent activity and campaign identity;
- human review state.

Model-generated content may not become:

- primary-source text;
- accepted transcription;
- gold benchmark data;
- scholarly consensus;
- training gold;
- authoritative mapping;

without an explicit review and promotion activity.

Human editing does not erase model provenance.

## 31. Retraction, invalidation, and deletion

### 31.1 Retraction

A claimant or project reviewer may retract an assertion while preserving its historical identity and reason.

### 31.2 Invalidation

A revision may become invalid for current operational use because of corruption, source withdrawal, rights change, or discovered error.

### 31.3 Deletion

Physical deletion of content is reserved for privacy, legal, rights, or security obligations. Where content must be removed, the system retains only the minimum lawful tombstone and dependency information.

### 31.4 Impact propagation

Retraction or invalidation triggers dependency analysis but does not silently rewrite dependent artifacts. Affected datasets, benchmarks, indexes, model runs, and reports receive a flagged impact record and explicit re-evaluation decision.

## 32. Public, restricted, and private graph partitions

Logical identity and provenance contracts apply across partitions, but access does not.

The graph must support at least:

```text
PUBLIC_OPEN
PUBLIC_METADATA_RESTRICTED_CONTENT
NONCOMMERCIAL_RESEARCH
LOCAL_RESEARCH_ONLY
PRIVATE_USER
PRIVATE_BENCHMARK
SECURITY_OR_LEGAL_HOLD
```

A public projection may expose an entity ID, bibliographic metadata, rights status, and content hash without exposing restricted text.

No index, export, evidence bundle, or model input may cross a partition boundary without an authorized materialization activity.

DR-10 and DR-27 define detailed rights and privacy policy.

## 33. Required query capabilities

The logical design must support queries equivalent to:

1. Trace a displayed quotation to the exact edition revision, source artifact, segment, and acquisition activity.
2. Trace a normalized token to the raw source and every transformation applied.
3. Show all competing authorship, dating, or textual-lineage assertions with evidence and methods.
4. Identify which witnesses were actually examined for a reading and which were merely uncollated.
5. Distinguish a direct reading observation from a report copied from an apparatus.
6. Find every dataset, benchmark case, index, model run, or report dependent on an invalidated source revision.
7. Show which agent, software, model, configuration, and review produced an annotation.
8. Identify whether two apparently independent sources derive from the same upstream edition or translation family.
9. Reconstruct the exact graph snapshot used by a run.
10. Export an interoperable provenance bundle without exposing restricted content.

## 34. Validation invariants

The following invariants are normative.

1. Every derived revision identifies at least one generating activity or a documented external-import activity.
2. Every recorded project derivation that generates a revision identifies exact input revisions and output revisions; hypothesized ancient activities remain assertion-based when their inputs are unknown.
3. No committed revision is modified in place.
4. Every source artifact has an exact checksum or documented reason one cannot be retained.
5. A URL alone is never treated as immutable source identity.
6. Every exact quotation resolves to a source revision and selector.
7. Every representation declares its type and review state.
8. OCR and model output are not human transcription by default.
9. A witness role has explicit passage or segment coverage.
10. Missing data are not interpreted as absence.
11. A negative attestation identifies examination scope and method.
12. A conjecture is not represented as witnessed text.
13. A historical or genealogical relation with material scholarly consequences is an assertion, not an unqualified edge.
14. A model-generated assertion is never operationally accepted without a review activity.
15. Workflow approval does not change epistemic status automatically.
16. Conflicting assertions may coexist.
17. Operational selections cannot delete or rewrite competing assertions.
18. Provenance derivation records are acyclic with respect to exact revision generation.
19. Assertion or citation cycles do not count as independent evidence.
20. Every training and evaluation run binds to a graph snapshot.
21. Derived indexes are rebuildable and identify their authoritative inputs.
22. Restricted content cannot enter an unauthorized public or open-lineage materialization.
23. Identity merges preserve prior IDs and audit history.
24. Retraction or invalidation preserves historical run reproducibility.
25. Human correction of model output preserves the model-generation lineage.

## 35. Benchmark and evaluation obligations

DR-05 creates a dedicated provenance and textual-history evaluation track.

### 35.1 Case families

- manuscript versus digital surrogate identity;
- physical mark versus recognized grapheme versus transcription;
- direct observation versus secondary report;
- witness coverage and unexamined states;
- conjecture versus attested reading;
- conflicting reading observations;
- authorship and date disagreement;
- passage-local mixed textual affiliation;
- contaminated genealogy;
- translation or revision lineage;
- model-generated candidate promotion;
- source correction and dependency impact;
- restricted-source public projection;
- IIIF page-region to transcription trace;
- TEI apparatus ingestion;
- graph-snapshot reproducibility;
- exact quotation provenance;
- non-independent evidence detection.

### 35.2 Metrics

```text
provenance_path_completeness
source_revision_accuracy
selector_recovery_accuracy
assertion_vs_fact_classification
witness_coverage_accuracy
false_absence_rate
conjecture_attestation_confusion_rate
agent_role_accuracy
secondary_source_disclosure_rate
dependency_impact_recall
restricted_content_leakage_rate
snapshot_reproducibility
model_generated_provenance_retention
conflict_preservation_accuracy
identity_merge_precision
```

### 35.3 Hard gates

No aggregate score may hide:

- restricted-data leakage;
- fabricated provenance;
- loss of source revision identity;
- model output presented as primary evidence;
- conjecture presented as attestation;
- an unexamined witness presented as negative evidence;
- silent destruction of a competing scholarly assertion.

## 36. Hard failures

The system fails this design if it materially:

- conflates a physical artifact with its image, transcription, edition, or textual form;
- conflates custody provenance with textual genealogy;
- treats an inferred exemplar relation as observed fact;
- overwrites raw sources or committed revisions;
- loses the chain from a derived span to exact source evidence;
- presents OCR or model-generated text as human-verified transcription;
- treats database silence as witness absence;
- reports a conjecture as manuscript evidence;
- assigns a whole witness to one textual family despite passage-local contrary evidence;
- merges conflicting assertions through last-write-wins behavior;
- erases the responsible agent or method for a consequential claim;
- treats a secondary apparatus report as direct manuscript inspection;
- accepts model-generated assertions without review;
- rewrites historical benchmark or run identity after a graph update;
- permits restricted content to leak through a public graph projection or index;
- destroys dependency evidence needed to assess a retraction or source correction;
- creates a false claim of evidence independence by ignoring upstream derivation.

## 37. Security, privacy, and rights boundaries

Provenance itself may expose sensitive information, including:

- private user research interests;
- uploaded page images;
- unpublished scholar annotations;
- repository access locations;
- restricted corpus identity;
- reviewer identities;
- security-sensitive storage paths or credentials.

The graph must support redacted projections and role-based access. Public identifiers may not encode secrets, file-system paths, personal data, or access tokens.

User uploads and private annotations are excluded from training by default and governed by DR-27.

## 38. Explicit non-goals

DR-05 does not:

- declare one correct stemma or textual history;
- define the Translation Nuance cause taxonomy in full;
- define all linguistic annotation layers;
- choose a critical edition or textual-critical method;
- select physical database products;
- require RDF as the operational storage model;
- require character-level graph nodes for every corpus;
- guarantee that all historical events can be reconstructed;
- equate a complete provenance record with truth;
- replace expert examination of manuscripts or apparatuses;
- decide rights or release eligibility beyond required partition hooks;
- define the final public API or user interface.

## 39. Sol implementation boundary

Project design authority defines:

- the four provenance domains;
- logical graph layers;
- entity and revision semantics;
- observation, assertion, argument, and derivation contracts;
- witness-as-role semantics;
- coverage and absence states;
- relationship-assertion policy;
- model-generated content policy;
- snapshot and impact-analysis requirements;
- selector and source-anchoring semantics;
- interoperability obligations;
- validation invariants;
- benchmark obligations;
- hard failures.

Sol may implement the approved design and choose only reversible, local, design-neutral coding mechanics that preserve all approved logical contracts.

Sol may not replace evidence-bearing assertions with unqualified graph edges, collapse provenance domains, use destructive updates, or remove revision and snapshot identity. Any material implementation conflict must stop with:

```text
BLOCKED_REQUIRES_DESIGN_REVIEW
```

DR-28 will select the authoritative physical storage topology, graph/relational boundaries, canonical serialization, service ownership, and migration system before production implementation.

## 40. Decisions DR-05 would lock

Approval would freeze these principles:

1. Material custody, textual transmission, digital derivation, and epistemic provenance are separate domains.
2. The graph has identity, evidence/observation, assertion/argument, derivation/activity, and operational-projection layers.
3. Stable entity identity is separate from immutable revision identity.
4. Raw sources and committed revisions are append-only in logical history.
5. Intrinsic facts, imported metadata, scholarly assertions, and operational selections are distinct.
6. Physical artifacts, object parts, written marks, digital surrogates, textual representations, and representation segments are distinct.
7. Physical marks, grapheme recognition, readings, transcription, normalization, and linguistic analysis are separate stages.
8. Witness is a scoped evidentiary role rather than one universal object class.
9. Witness coverage, absence, lacuna, unexamined, and uncollated states are explicit.
10. Variation units and reading groupings are versioned editorial constructs with responsibility and method.
11. Conjectural or reconstructed readings are never represented as physical attestations.
12. Textual genealogy is a competing hypothesis graph and may contain contamination and multiple parentage.
13. Consequential historical and textual relations are evidence-bearing assertions rather than unlabeled truth edges.
14. Assertions preserve claimant, method, evidence, counterevidence, epistemic status, origin, scope, and review state.
15. Arguments preserve premises, inference method, conclusions, and responsible agent.
16. Authorship, inscription, transcription, editing, translation, software generation, and review use distinct agent roles.
17. Material computational derivations record exact revisions, activity, agent, method, configuration, and hashes.
18. URLs are locators, not immutable source identities.
19. Segment selectors bind claims and annotations to exact source states.
20. IIIF, Web Annotation, TEI, W3C PROV-O, and CIDOC CRM-family standards are versioned interoperability adapters rather than internal truth.
21. Provenance granularity is sufficient for exact citation and training traceability, with finer nodes created only where needed.
22. Every benchmark, corpus materialization, model run, and report binds to an immutable knowledge-graph snapshot.
23. Scholarly conflicts coexist; there is no last-write-wins truth policy.
24. Identity-resolution candidates do not cause destructive automatic merges.
25. Model-generated content remains labeled through all human revisions and requires explicit promotion.
26. Retraction or invalidation triggers impact analysis without destroying historical reproducibility.
27. Public, restricted, private, and benchmark partitions remain enforceable across graph projections and indexes.
28. Historical dates, places, and sequences are qualified assertions with intervals, original expressions, methods, and uncertainty rather than unqualified scalar facts.
29. Evidence derivation and common upstream sources are represented so repeated or inherited claims are not counted automatically as independent corroboration.
30. Provenance receives dedicated benchmark metrics and hard-failure gates.

## 41. Decisions intentionally deferred

DR-05 does not yet select:

- exact internal URI syntax;
- graph, relational, document, search, vector, or object-store products;
- canonical JSON-LD, RDF, JSON, SQL, or tabular serialization;
- graph query language;
- exact CIDOC CRM or PROV-O mapping profile;
- complete entity and relation vocabulary for Translation Nuance;
- final apparatus schema;
- exact confidence-calibration representation;
- human-review workflow and permissions;
- snapshot implementation or Merkle structure;
- granularity thresholds by corpus;
- public provenance display format;
- retention periods and deletion implementation;
- final service and API boundaries.

These are completed in DR-06 through DR-10, DR-14, DR-16, DR-17, DR-20/21, DR-23, DR-27, and DR-28.

## 42. Approved statement

> **Biblical Scholar Lab will use an immutable, evidence-bearing textual-history and provenance graph that distinguishes physical and custodial history, textual transmission, digital derivation, and scholarly belief. Physical artifacts, written marks, digital surrogates, textual representations, editions, observations, assertions, arguments, activities, and agents will retain separate identities and exact revision histories. Witness status and textual genealogy will be scoped, evidence-bearing, and capable of representing lacunae, contamination, competing readings, uncertainty, and disagreement rather than being flattened into a single stemma or source-of-truth edge. Every derived span, benchmark case, dataset, model run, and report will remain traceable to exact source revisions, selectors, methods, configurations, agents, and graph snapshots. Established provenance, cultural-heritage, annotation, image, and textual-editing standards will be supported through versioned adapters, while the project's internal contracts remain designed for scholarly auditability, rights separation, reproducibility, and responsible model training.**

## 43. Change control

This design may be amended only through a new owner-approved revision or supplement. Any proposed change to the provenance-domain separations, stable entity/revision semantics, witness-role and coverage model, observation/attestation states, variation-unit and genealogy treatment, assertion and argument contracts, derivation identity, source anchoring, graph-snapshot guarantees, conflict and retraction policy, model-generated-content policy, public/restricted/private partitions, validation invariants, hard failures, or benchmark obligations must stop with:

```text
BLOCKED_REQUIRES_DESIGN_REVIEW
```

Sol may report implementation constraints and propose alternatives, but it may not silently collapse provenance layers, replace evidence-bearing assertions with unqualified truth edges, weaken immutable revision or snapshot guarantees, or promote model-generated candidates without the approved review process.

## 44. External reference anchors

These sources inform the interoperability and conceptual architecture. They do not replace the project's approved internal model or source-specific scholarly review.

[^prov-o]: World Wide Web Consortium, *PROV-O: The PROV Ontology*. PROV-O models entities, activities, agents, generation, usage, attribution, association, delegation, derivation, revision, quotation, and qualified relations: https://www.w3.org/TR/prov-o/

[^web-annotation]: World Wide Web Consortium, *Web Annotation Data Model*. The model represents annotation bodies and targets, selectors for segments of resources, resource states, creators, generators, and provenance: https://www.w3.org/TR/annotation-model/

[^iiif-presentation]: International Image Interoperability Framework, *Presentation API 3.0*. The API models manifests, canvases, ranges, annotation pages, annotations, and selected regions for compound digital objects: https://iiif.io/api/presentation/3.0/

[^tei-manuscript]: Text Encoding Initiative, *TEI P5 Guidelines — Manuscript Description*. The module distinguishes manuscript identifiers, intellectual contents, physical description, history, administrative information, surrogates, manuscript parts, and fragments: https://www.tei-c.org/release/doc/tei-p5-doc/en/html/MS.html

[^tei-apparatus]: Text Encoding Initiative, *TEI P5 Guidelines — Critical Apparatus*. The module represents apparatus entries, readings, witnesses, witness details, responsibility, certainty, variant types, and competing editorial strategies: https://www.tei-c.org/release/doc/tei-p5-doc/en/html/TC.html

[^cidoc-crm]: CIDOC CRM Special Interest Group, *Definition of the CIDOC Conceptual Reference Model*, official ISO-corresponding release 7.1.3. CIDOC CRM supports integration and interchange of cultural-heritage information, including physical objects, events, actors, conceptual objects, and information objects: https://cidoc-crm.org/Version/version-7.1.3

[^crmtex]: CIDOC CRM Special Interest Group, *CRMtex 2.0*. CRMtex models ancient textual entities and scholarly processes including written text, writing fields, text recognition, transliteration, graphemes, glyphs, readings, and text segments: https://cidoc-crm.org/extensions/crmtex/

[^crmdig]: CIDOC CRM Special Interest Group, *CRMdig 5.0*. CRMdig models digital objects, digitization, formal derivation, software execution, devices, measurements, transfers, and annotation creation: https://cidoc-crm.org/extensions/crmdig/html/CRMdig_v5.0.html

[^crminf]: CIDOC CRM Special Interest Group, *CRMinf 1.2.1*. CRMinf models argumentation, beliefs, proposition sets, inference methods, evidence, adopted interpretation, and provenance assessment: https://cidoc-crm.org/extensions/crminf/html/CRMinf_v1.2.1.html
