# DR-06 — Translation Nuance Core

| Field | Value |
|---|---|
| Design ID | `DR-06` |
| Status | `APPROVED` |
| Approval date | 2026-08-15 |
| Project owner | Joseph Abbud |
| Designer and independent reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2; DR-03; DR-04; DR-05 |
| Implementation authority | GPT-5.6 Sol, under the approved design |

## 1. Purpose

Biblical Scholar Lab needs a formal architecture for answering a question that ordinary Bible comparison tools often leave implicit:

> Why do these textual forms or translations differ, what evidence supports each explanation, what nuance changes in the target language, and what remains uncertain?

This design defines the **Translation Nuance Core** (`TNC`), the logical layer that connects:

- source textual forms, editions, and readings;
- translation works, editions, revisions, and instances;
- passage-scoped source-base and lineage assertions;
- source-to-target and target-to-target span alignments;
- observed differences among textual realizations;
- candidate causal explanations for those differences;
- translation operations and target-language constraints;
- terminology and parallel-passage decisions;
- interpretive effects without unsupported claims about translator intent;
- evidence, counterevidence, uncertainty, disagreement, and review status;
- runtime comparison tools, training examples, and benchmark cases.

The TNC is the signature scholarly capability of version one. It is intended to help the assistant distinguish, for example:

- a manuscript or edition difference from a translation choice;
- a syntactic ambiguity from lexical polysemy;
- a target-language necessity from a theological preference;
- inherited wording from an independent translation decision;
- an ancient version's translation technique from evidence for a different source text;
- a visible heading or footnote from canonical text;
- an effect of a rendering from an alleged translator motive.

The TNC does not replace DR-04's reference architecture, DR-05's provenance graph, DR-07's detailed linguistic representation, DR-08's ancient-version and apparatus policy, or DR-09's scholarship and citation model. It defines the translation-comparison entities and causal contracts that connect those systems.

## 2. Governing principle

> **A translation difference is an evidence-bearing, potentially multi-causal relationship among identified textual realizations—not a freestanding fact, a popularity vote, or an automatic judgment that one rendering is right and another is wrong.**

The system must preserve the complete analytical chain:

```text
source textual state
    → source-language construal
    → transfer operation
    → target-language realization
    → revision/editorial lineage
    → interpretive effect
```

Any step may be:

- directly documented;
- strongly supported;
- plausible;
- contested;
- speculative;
- unsupported;
- unknown.

A diagnosis may contain several contributing causes. The architecture must not force one label where the evidence supports a causal chain or unresolved alternatives.

## 3. What the Translation Nuance Core is—and is not

### 3.1 It is a custom semantic architecture at the system level

The TNC consists of:

1. translation identity and lineage;
2. passage- and span-level alignment;
3. contrast and difference representation;
4. causal diagnosis;
5. interpretive-effect description;
6. evidence and uncertainty;
7. runtime, training, and benchmark projections.

It is not merely a dataset placed beside the model. It is the project-specific semantic substrate through which the assistant, deterministic tools, retrieval system, training curriculum, benchmark, and evidence ledger represent and reason about translation relationships.

The intended baseline system is:

```text
foundation model
    + Translation Nuance semantic graph
    + deterministic alignment and source tools
    + translation-aware retrieval
    + structured training objectives
    + claim/evidence verification
```

### 3.2 It is not initially a single custom neural or compute kernel

The name `Core` does not mean that the baseline begins with a custom transformer block, attention mechanism, recurrent kernel, graph-neural module, tokenizer modification, or CUDA kernel.

The selected foundation model's neural topology remains unchanged in the baseline in order to:

- establish clear scientific attribution;
- preserve expensive pretrained multilingual, multimodal, long-context, and tool-use capabilities;
- avoid introducing several causal variables at once;
- retain compatibility with mature training, inference, quantization, and mobile runtimes;
- discover whether the first limiting factor is evidence, data quality, retrieval, supervision, capacity, or representation before selecting an architectural intervention.

The baseline first realizes Translation Nuance through:

- approved structured data;
- deterministic tools;
- retrieval;
- explicit training objectives;
- supervised examples;
- preference shaping;
- evidence-ledger verification.

This sequencing does **not** foreclose architectural innovation. DR-06 preregisters a Translation Nuance architecture-extension ladder in section 32. Temporary auxiliary heads, relation-aware adapters, sidecar graph memory, specialist models, routing, and—only at the final tier—foundation-block modification remain legitimate later experiments when a persistent benchmarked deficit justifies them.

### 3.3 A GPU kernel optimizes an approved operation; it does not supply semantic capability

A custom GPU or CUDA kernel can make a mathematical operation faster or more memory-efficient. It cannot by itself teach the model the distinction between a textual variant and a translation choice, identify revision ancestry, explain target-language constraints, or preserve uncertainty about an ancient version's possible source text.

A project-specific compute kernel may therefore be considered only after:

- an approved semantic operation already exists;
- profiling identifies that operation as a material bottleneck;
- the optimized implementation is numerically and semantically equivalent within an approved tolerance;
- the implementation does not compromise reproducibility, portability, quantization, or deployment requirements.

### 3.4 It is not a universal translation-quality score

The TNC must not reduce translations to a single ranking such as:

```text
accurate / inaccurate
literal / nonliteral
good / bad
```

Evaluation requires a stated purpose and criterion. A rendering may preserve ambiguity well, read naturally, support public reading, retain lexical form, or communicate discourse force to different degrees. Those are distinct properties.

## 4. Core conceptual separations

The following concepts must remain separate.

### 4.1 Textual variation is not translation variation

A target difference may reflect:

- a different source reading;
- a different source edition;
- a different textual form;
- the same source text interpreted differently;
- the same interpretation realized differently in the target language;
- revision inheritance;
- editorial paratext rather than translation.

The system must identify which layer is implicated before explaining the difference.

### 4.2 Alignment is not equivalence

An alignment means that identified spans participate in a translation or comparison relationship. It does not assert identical lexical meaning, grammatical function, discourse effect, or theological implication.

### 4.3 Effect is not intent

The system may responsibly say:

> This rendering resolves an ambiguity in favor of interpretation A.

It may not say:

> The translators intended to impose doctrine A.

unless documented translator statements or other suitable evidence support that claim.

### 4.4 Consistency is not mechanical sameness

The same source expression may require different target renderings in different contexts. Parallel passages may appropriately vary. A consistency tool identifies a question for review; it does not establish that identical wording is always preferable.

### 4.5 Translation frequency is not evidentiary weight

Many translations may:

- descend from one revision family;
- use the same critical edition;
- inherit traditional wording;
- reproduce one another;
- be multiple instances of the same edition.

Frequency must not be represented as independent manuscript or scholarly support.

### 4.6 A model-generated rendering is not a published translation

Every system-generated translation or paraphrase must retain explicit provenance and cannot silently enter a published-translation comparison.

## 5. Logical layers of the Translation Nuance Core

The TNC has six logical layers.

### 5.1 Translation identity and lineage layer

Identifies works, editions, revisions, instances, declared source bases, predecessor dependence, translation direction, and revision history.

### 5.2 Alignment layer

Represents many-to-many, discontinuous, null, and uncertain relationships among exact source and target segments.

### 5.3 Contrast layer

Defines versioned comparison frames and editorially identified difference units.

### 5.4 Diagnosis layer

Represents one or more candidate causal chains with evidence, method, counterevidence, status, and uncertainty.

### 5.5 Interpretive-effect layer

Describes what a rendering makes explicit, leaves implicit, narrows, broadens, foregrounds, or resolves—without confusing effect with motive or truth.

### 5.6 Operational projection layer

Materializes approved alignments, diagnoses, training labels, benchmark gold records, runtime evidence packets, and reports for a bounded purpose and graph snapshot.

## 6. Translation identity model

DR-05 establishes the general work, representation, assertion, and revision semantics. DR-06 refines the translation-specific identities.

### 6.1 `TranslationWork`

A `TranslationWork` is the continuing intellectual translation project or family across one or more editions.

```text
TranslationWork
  translation_work_id
  revision_id
  display_name
  abbreviations[]
  target_language_id
  target_language_variety?
  target_script_ids[]
  work_scope
  originating_agents[]
  originating_organization?
  declared_tradition_or_context?
  initial_date_assertions[]
  declared_translation_policy_assertions[]
  external_aliases[]
  rights_partition
  provenance
  content_hash
```

A work is not assumed to be textually unchanged across its editions.

### 6.2 `TranslationEdition`

A `TranslationEdition` is a materially identifiable published or released state of a translation work.

```text
TranslationEdition
  translation_edition_id
  revision_id
  translation_work_id
  edition_label
  publication_or_release_date_assertions[]
  publisher_or_releasing_agent?
  language_revision_notes?
  scope_and_coverage
  source_artifact_ids[]
  predecessor_edition_assertions[]
  rights_record_id
  provenance
  content_hash
```

Different editions may change:

- wording;
- source text;
- translation philosophy;
- language modernization;
- footnotes and headings;
- canon or versification;
- textual-critical decisions.

### 6.3 `TranslationInstance`

A `TranslationInstance` is one hosted, packaged, printed, scanned, or otherwise distributed occurrence of an edition.

```text
TranslationInstance
  translation_instance_id
  revision_id
  translation_edition_id
  provider_or_repository
  source_artifact_ids[]
  declared_metadata
  observed_metadata
  rights_claims[]
  completeness
  integrity_status
  provenance
```

Several website copies of one edition are not several independent translations.

This work/edition/instance separation is compatible with the structure published by Targum, which distinguishes underlying translation works, distinct editions, and per-source instances rather than treating every collected file as unique.[^targum]

### 6.4 `TranslationPassageRealization`

Represents the exact target-language realization of an identified passage in one edition revision.

```text
TranslationPassageRealization
  realization_id
  translation_edition_revision_id
  passage_selection_id
  textual_representation_revision_id
  segment_ids[]
  text_layer
  paratext_region_ids[]
  language_id
  script_id
  provenance
  content_hash
```

It does not flatten headings, notes, or cross-references into canonical text.

## 7. Translation event and revision lineage

A translation edition may be created through:

- direct translation from one or more original-language sources;
- revision of a predecessor translation;
- consultation of several modern translations;
- revision against a new critical edition;
- adaptation into a related language;
- translation through an intermediate language;
- committee editing over time;
- partial retranslation of selected passages.

The architecture therefore defines a versioned `TranslationActivity` and evidence-bearing lineage assertions.

```text
TranslationActivity
  activity_id
  activity_type
  passage_or_work_scope
  input_representation_revisions[]
  output_translation_edition_revision
  responsible_agents[]
  declared_methods[]
  start_and_end_assertions[]
  source_documentation[]
  provenance
```

`activity_type` may include:

```text
NEW_TRANSLATION
REVISION
LANGUAGE_MODERNIZATION
SOURCE_TEXT_REVISION
RELATED_LANGUAGE_ADAPTATION
BACK_TRANSLATION
EDITORIAL_HARMONIZATION
PARTIAL_RETRANSLATION
UNKNOWN
```

## 8. Passage-scoped source-base assignments

A translation work's preface may declare a general base text, but a specific passage may reflect a different reading, a predecessor translation, or an uncertain source.

The normative record is:

```text
TranslationSourceAssignment
  assignment_id
  target_realization_id
  source_representation_revision_ids[]
  source_passage_or_segment_ids[]
  intermediate_translation_ids[]
  assignment_role
  direction
  evidence_ids[]
  method
  epistemic_status
  confidence_dimensions
  counterevidence_ids[]
  assertion_origin
  review_state
```

`assignment_role` may include:

```text
DECLARED_PRIMARY_SOURCE
DECLARED_CONSULTED_SOURCE
INFERRED_COMPATIBLE_SOURCE
INFERRED_PREDECESSOR_SOURCE
INTERMEDIATE_OR_DAUGHTER_SOURCE
POSSIBLE_SOURCE
SOURCE_UNKNOWN
```

The system must distinguish:

- what translators or publishers declared;
- what wording is compatible with;
- what scholars infer was actually used.

Compatibility does not prove direct use.

## 9. Alignment set

Alignment is stored in versioned sets because different annotators or methods may produce different alignments.

```text
AlignmentSet
  alignment_set_id
  revision_id
  source_representation_revision_id
  target_representation_revision_id
  passage_scope
  directionality
  segmentation_profile
  tokenization_profiles[]
  creation_method
  responsible_agents[]
  review_state
  graph_snapshot_id
  provenance
  content_hash
```

Possible `creation_method` values include:

```text
HUMAN_AUTHORED
HUMAN_CORRECTED
IMPORTED
RULE_BASED
STATISTICAL
NEURAL
MODEL_GENERATED_CANDIDATE
HYBRID
```

An imported or automated alignment remains an evidence-bearing candidate unless its review state permits stronger use.

## 10. Alignment link

### 10.1 Normative logical record

```text
AlignmentLink
  alignment_link_id
  alignment_set_revision_id
  source_selectors[]
  target_selectors[]
  cardinality
  relation_types[]
  transfer_operations[]
  boundary_confidence
  relation_confidence
  source_text_confidence
  target_text_confidence
  evidence_ids[]
  annotator_or_generator
  review_state
  notes
```

Selectors bind to exact representation revisions under DR-05. Token indices alone are insufficient because tokenization may change.

### 10.2 Cardinality

```text
ONE_TO_ONE
ONE_TO_MANY
MANY_TO_ONE
MANY_TO_MANY
SOURCE_NULL
TARGET_NULL
DISCONTINUOUS
COMPOSITE
```

### 10.3 Alignment relation types

```text
LEXICAL_CORRESPONDENCE
GRAMMATICAL_REALIZATION
SEMANTIC_REALIZATION
REFERENTIAL_CORRESPONDENCE
DISCOURSE_CORRESPONDENCE
IDIOMATIC_REALIZATION
FORMAL_CORRESPONDENCE
PARATEXT_CORRESPONDENCE
UNCERTAIN_CORRESPONDENCE
```

Several relation types may apply to one link.

### 10.4 Alignment is directional

A source-to-target link and its target-to-source interpretation need not carry the same information. The architecture must not assume that an alignment can be inverted without loss.

### 10.5 Nested and overlapping alignment

The system may represent:

- clause-level alignment;
- phrase-level alignment;
- word-level alignment;
- morpheme-level alignment;
- discontinuous spans;
- nested links.

Fine-grained alignment is materialized where it supports analysis, training, or review; it is not required for every corpus before useful passage-level comparison can begin.

### 10.6 Standards interoperability

USFM/USX, unfoldingWord alignment milestones, and other source formats may be imported through adapters. unfoldingWord's published alignment layer, for example, associates target-language words with original-language lemma, morphology, occurrence, and content through USFM milestone markup.[^uw-alignment]

USFM and USX also preserve structured scripture content, word-level attributes, linking metadata, and milestone-based overlap that should be ingested without flattening the text to a verse table.[^usfm][^usx]

Those encodings are not the internal source of truth. The internal link must preserve exact source and target revision identities, arbitrary many-to-many spans, provenance, confidence, and review state.

## 11. Comparison frame

A translation comparison must identify exactly what is being compared and for what purpose.

```text
ComparisonFrame
  comparison_frame_id
  revision_id
  passage_selection_id
  source_representation_revision_ids[]
  target_realization_ids[]
  comparison_purpose
  active_canon_profile_id
  reference_scheme_ids[]
  requested_language
  included_text_layers[]
  excluded_text_layers[]
  graph_snapshot_id
  creator
  provenance
```

`comparison_purpose` may include:

```text
EXPLAIN_TRANSLATION_DIFFERENCE
TEXTUAL_VARIANT_ANALYSIS
SOURCE_LANGUAGE_ANALYSIS
TRANSLATION_LINEAGE_ANALYSIS
TERMINOLOGY_ANALYSIS
PARALLEL_PASSAGE_ANALYSIS
ANCIENT_VERSION_ANALYSIS
TARGET_LANGUAGE_ANALYSIS
GENERAL_COMPARISON
```

A comparison frame is immutable once used in a benchmark, training example, evaluation, or published note.

## 12. Translation difference unit

A `TranslationDifferenceUnit` is a versioned editorial construct identifying a comparison-worthy contrast.

```text
TranslationDifferenceUnit
  difference_unit_id
  revision_id
  comparison_frame_id
  source_selectors[]
  target_selectors_by_realization{}
  difference_scope
  observed_features[]
  materiality
  creation_method
  responsible_agents[]
  review_state
  evidence_ids[]
  provenance
```

`difference_scope` may include:

```text
TEXTUAL_STATE
LEXICAL
MORPHOLOGICAL
SYNTACTIC
SEMANTIC
REFERENTIAL
DISCOURSE
PRAGMATIC
STRUCTURAL
STYLISTIC
REGISTER
PARATEXT
REFERENCE_OR_VERSIFICATION
MIXED
```

`materiality` may include:

```text
NO_MATERIAL_DIFFERENCE
MINOR_FORM_DIFFERENCE
POTENTIAL_NUANCE_DIFFERENCE
MATERIAL_INTERPRETIVE_DIFFERENCE
TEXTUAL_HISTORY_DIFFERENCE
UNKNOWN
```

Materiality is task-relative and evidence-bearing. Different wording does not necessarily produce a material difference, and similar wording does not guarantee equivalent meaning.

## 13. Translation-cause ontology

The ontology is multi-axis rather than one flat list. A complete diagnosis can contain one or more values from each relevant axis.

### 13.1 Axis A — source textual state

```text
SAME_IDENTIFIED_SOURCE_TEXT
DIFFERENT_SOURCE_READING
DIFFERENT_TEXTUAL_FORM
DIFFERENT_SOURCE_EDITION
DIFFERENT_CANON_OR_REFERENCE_SCOPE
SOURCE_PUNCTUATION_OR_SEGMENTATION
UNCERTAIN_SOURCE_BASE
SOURCE_BASE_NOT_ESTABLISHED
```

A claim that source readings differ must connect to DR-05 attestation evidence or a suitable apparatus source. Translation wording alone does not establish it.

### 13.2 Axis B — source-language construal

```text
ORTHOGRAPHIC_OR_DIACRITIC_DIFFERENCE
MORPHOLOGICAL_AMBIGUITY
SYNTACTIC_AMBIGUITY
LEXICAL_POLYSEMY
IDIOM_OR_METAPHOR
SEMANTIC_ROLE_DIFFERENCE
REFERENT_OR_COREFERENCE_DIFFERENCE
DISCOURSE_OR_INFORMATION_STRUCTURE
PRAGMATIC_FORCE
PUNCTUATION_OR_CLAUSE_BOUNDARY
INTERTEXTUAL_CONSTRUAL
SOURCE_LANGUAGE_UNCERTAINTY
```

Detailed linguistic feature contracts are completed in DR-07. MACULA Greek and Hebrew illustrate the kind of morphology, syntax, word-sense, semantic-role, participant-reference, and mapping evidence that may be attached through that later contract.[^macula-greek][^macula-hebrew]

### 13.3 Axis C — transfer operation

```text
FORM_PRESERVING_CORRESPONDENCE
BORROWING_OR_TRANSLITERATION
CALQUE
TRANSPOSITION
REORDERING
EXPLICITATION
IMPLICITATION
ADDITION
OMISSION
COMPRESSION
EXPANSION
GENERALIZATION
SPECIFICATION
MODULATION
PARAPHRASE
HARMONIZATION
TERMINOLOGY_STANDARDIZATION
AMBIGUITY_PRESERVATION
AMBIGUITY_RESOLUTION
FIGURATIVE_TO_EXPLICIT_RENDERING
UNIT_OR_CULTURAL_ADAPTATION
UNKNOWN_TRANSFER_OPERATION
```

A transfer-operation label describes what happened between representations. It does not by itself judge whether the operation was justified.

### 13.4 Axis D — target-language realization constraint

```text
TARGET_GRAMMAR
TARGET_LEXICALIZATION
TARGET_IDIOM
TARGET_WORD_ORDER
TARGET_TENSE_ASPECT_OR_MOOD_SYSTEM
TARGET_GENDER_NUMBER_OR_AGREEMENT
TARGET_REFERENCE_TRACKING
TARGET_POLITENESS_OR_SOCIAL_REGISTER
TARGET_DISCOURSE_STRUCTURE
TARGET_INFORMATION_DENSITY
TARGET_POETIC_OR_RHYTHMIC_FORM
TARGET_ORAL_OR_AURAL_CLARITY
TARGET_READABILITY_OR_ACCESSIBILITY
TARGET_CULTURAL_CONVENTION
TARGET_SCRIPT_OR_ORTHOGRAPHY
TARGET_CONSTRAINT_UNKNOWN
```

A target-language constraint should be supported by evidence about that language. English intuition cannot stand in for native-language analysis.

### 13.5 Axis E — translation and revision lineage

```text
PREDECESSOR_WORDING_INHERITANCE
REVISION_FAMILY_DEPENDENCE
DECLARED_TRANSLATION_POLICY
SOURCE_EDITION_POLICY
COMMITTEE_OR_EDITORIAL_DECISION
TERMINOLOGY_POLICY
LITURGICAL_OR_TRADITIONAL_FORMULA
INTERPRETIVE_DECISION
CONFESSIONAL_TRADITION_INFLUENCE
LANGUAGE_MODERNIZATION
PUBLISHER_OR_STYLE_POLICY
PARALLEL_PASSAGE_CONSISTENCY
LEGACY_WORDING_CONTINUITY
LINEAGE_CAUSE_UNKNOWN
```

A confessional or interpretive diagnosis must not be inferred merely from the translation's publisher, tradition label, or outcome. It requires suitable evidence.

### 13.6 Axis F — paratext and presentation

```text
SECTION_HEADING
TRANSLATOR_NOTE
STUDY_NOTE
CROSS_REFERENCE
CAPITALIZATION
PUNCTUATION
PARAGRAPHING
VERSE_NUMBER_OR_REFERENCE_MAPPING
TYPOGRAPHIC_EMPHASIS
RED_LETTER_OR_SPEAKER_MARKING
PAGE_LAYOUT
USER_ANNOTATION
NOT_TRANSLATION_TEXT
```

This axis prevents visible page differences from being misrepresented as differences in canonical wording.

### 13.7 Axis G — unresolved or mixed cause

```text
MULTI_CAUSAL
COMPETING_DIAGNOSES
INSUFFICIENT_EVIDENCE
CAUSE_UNKNOWN
NOT_A_MATERIAL_TRANSLATION_DIFFERENCE
```

## 14. Causal-chain model

A diagnosis is not simply an unordered tag list. It may represent an ordered chain.

```text
NuanceCausalChain
  causal_chain_id
  difference_unit_id
  source_state_steps[]
  source_construal_steps[]
  transfer_steps[]
  target_realization_steps[]
  lineage_editorial_steps[]
  resulting_effects[]
  upstream_cause_ids[]
  proximate_cause_ids[]
  contributing_cause_ids[]
  unresolved_branch_ids[]
```

Example abstract chain:

```text
same Greek wording
→ syntactic ambiguity
→ translators select different construals
→ one target rendering resolves the ambiguity
→ another preserves it less explicitly
```

This must not be collapsed into a false textual-variant diagnosis.

Another abstract chain:

```text
different source reading
→ different grammatical subject
→ different target clause
→ later revisions inherit each branch
```

The source reading is upstream; revision inheritance may be a later contributing cause.

## 15. Nuance diagnosis assertion

Every diagnosis is an assertion under DR-05.

```text
NuanceDiagnosis
  diagnosis_id
  revision_id
  difference_unit_id
  causal_chain_ids[]
  diagnosis_summary
  method
  evidence_ids[]
  counterevidence_ids[]
  source_fitness_assessment
  epistemic_status
  confidence_dimensions
  alternative_diagnosis_ids[]
  excluded_diagnosis_ids[]
  responsible_agent
  assertion_origin
  review_state
  applicability_scope
  graph_snapshot_id
  provenance
  content_hash
```

### 15.1 Assertion origins

```text
TRANSLATOR_OR_PUBLISHER_DOCUMENTED
SCHOLARLY_SOURCE
EXPERT_PROJECT_ANNOTATION
IMPORTED_ANNOTATION
RULE_BASED_CANDIDATE
STATISTICAL_CANDIDATE
MODEL_GENERATED_CANDIDATE
SYSTEM_SYNTHESIS
```

### 15.2 Review states

```text
UNREVIEWED
REVIEW_IN_PROGRESS
HUMAN_REVIEWED
EXPERT_REVIEWED
APPROVED_FOR_RUNTIME
APPROVED_FOR_TRAINING
APPROVED_FOR_BENCHMARK
CONTESTED
REJECTED
RETRACTED
```

One approval does not imply every other approval. Data suitable for runtime exploration may not be suitable as benchmark gold.

## 16. Evidence requirements by diagnosis type

The system must validate that the evidence is suitable for the claim.

| Diagnosis | Minimum evidence expectation |
|---|---|
| Different source reading | Identified source editions, apparatus, witness evidence, or explicit translator documentation |
| Morphological ambiguity | Exact source form plus qualified morphological analysis |
| Syntactic ambiguity | Exact source span plus defensible competing parses or scholarly analysis |
| Lexical polysemy | Contextual lexical evidence, not a decontextualized gloss list |
| Target-language constraint | Native-language or qualified linguistic evidence about the target construction |
| Revision inheritance | Edition lineage, documented revision history, or robust passage-level dependence evidence |
| Translation philosophy | Translation preface, policy statement, or reviewed pattern analysis |
| Confessional influence | Direct documentation or substantial reviewed evidence; affiliation alone is insufficient |
| Different Vorlage | Version wording plus translation-technique analysis and suitable textual evidence; wording alone is insufficient |
| Translator intent | Direct documentation or appropriately cautious historical inference |

When the evidence is insufficient, the correct output is an unresolved or competing diagnosis—not a confident narrative.

## 17. Interpretive effect is represented separately from cause

The TNC may describe how a rendering affects the reader's available interpretation.

```text
InterpretiveEffect
  effect_id
  difference_unit_id
  affected_target_realization_id
  effect_types[]
  affected_claim_or_construal?
  evidence_ids[]
  method
  epistemic_status
  responsible_agent
  review_state
```

`effect_types` may include:

```text
PRESERVES_SOURCE_AMBIGUITY
RESOLVES_SOURCE_AMBIGUITY
MAKES_IMPLICIT_CONTENT_EXPLICIT
LEAVES_CONTENT_IMPLICIT
NARROWS_SEMANTIC_RANGE
BROADENS_SEMANTIC_RANGE
FOREGROUNDS_AGENT
BACKGROUNDS_AGENT
CHANGES_REFERENT_CLARITY
CHANGES_TEMPORAL_OR_ASPECTUAL_CONSTRUAL
CHANGES_MODAL_FORCE
CHANGES_DISCOURSE_PROMINENCE
CHANGES_REGISTER
CHANGES_METAPHOR_VISIBILITY
CHANGES_INTERTEXTUAL_VISIBILITY
INTRODUCES_INTERPRETIVE_COMMITMENT
REDUCES_INTERPRETIVE_COMMITMENT
NO_MATERIAL_INTERPRETIVE_EFFECT
EFFECT_UNCERTAIN
```

An effect record does not establish:

- that the translation is wrong;
- that the effect was intended;
- that readers necessarily perceive it;
- that one theological conclusion follows.

## 18. Translation option and tradeoff model

The assistant may generate or retrieve multiple defensible translation options.

```text
TranslationOption
  option_id
  source_representation_revision_id
  source_selectors[]
  target_language_id
  proposed_text
  origin
  construal_assertions[]
  transfer_operations[]
  preserved_features[]
  explicitated_features[]
  reduced_or_lost_features[]
  target_language_constraints[]
  intended_use_profile?
  evidence_ids[]
  review_state
  provenance
```

`origin` must distinguish:

```text
PUBLISHED_TRANSLATION
HUMAN_PROJECT_TRANSLATION
SCHOLARLY_PROPOSAL
MODEL_GENERATED_TRANSLATION
BACK_TRANSLATION
GLOSS
PARAPHRASE
```

A model-generated option must never be displayed as a published translation.

The product should describe tradeoffs rather than rank options without a stated criterion.

## 19. Translation policy and terminology decisions

A translation may document policies or terminology decisions.

### 19.1 Translation policy assertions

```text
TranslationPolicyAssertion
  policy_assertion_id
  translation_work_or_edition_revision_id
  policy_type
  scope
  policy_text_or_normalized_claim
  evidence_ids[]
  status
  provenance
```

### 19.2 Terminology decisions

```text
TerminologyDecision
  terminology_decision_id
  translation_work_or_edition_revision_id
  source_concept_or_term_ids[]
  passage_scope
  accepted_target_renderings[]
  conditional_renderings[]
  avoided_renderings[]
  rationale
  evidence_ids[]
  responsible_agents[]
  status
  provenance
```

A terminology decision is evidence about a translation project, not universal evidence that one target term is always correct.

Paratext's Biblical Terms tooling demonstrates the practical importance of tracking key source terms, target renderings, verse occurrences, comparison texts, and consistency questions.[^paratext-terms] DR-06 extends this concept with passage scope, evidence, lineage, alternative renderings, and explicit protection against mechanical one-to-one glossing.

### 19.3 Translation-technique profiles

The system may represent recurring tendencies in a translation, translator, committee, ancient version, book, or passage class.

```text
TranslationTechniqueProfile
  technique_profile_id
  subject_translation_work_or_edition_revision_id
  passage_or_corpus_scope
  observed_tendencies[]
  quantitative_features[]
  comparison_baseline
  method
  evidence_ids[]
  counterexamples[]
  responsible_agents[]
  epistemic_status
  review_state
  provenance
```

A technique profile is a scoped generalization, not a deterministic rule. It may inform a passage-level diagnosis but cannot establish that diagnosis by itself. The system must preserve exceptions and avoid reasoning:

```text
this translation often explicitates
→ therefore this passage must be an explicitation
```

This distinction is especially important when ancient-version wording is used to infer a possible source text.

## 20. Parallel-passage relationships

Parallel passage analysis must distinguish:

- identical source wording;
- similar source wording;
- explicit quotation;
- probable allusion;
- common traditional formula;
- independent description of the same event;
- target-language harmonization;
- appropriate contextual variation.

```text
ParallelPassageTranslationAssessment
  assessment_id
  source_passage_relation_id
  target_realization_ids[]
  source_similarity_features[]
  target_similarity_features[]
  consistency_status
  variation_rationale_assertions[]
  harmonization_assertions[]
  evidence_ids[]
  review_state
```

`consistency_status` may include:

```text
APPROPRIATELY_CONSISTENT
APPROPRIATELY_VARIED
POSSIBLE_UNJUSTIFIED_DIVERGENCE
POSSIBLE_HARMONIZATION
INSUFFICIENT_EVIDENCE
NOT_COMPARABLE
```

Paratext explicitly treats parallel-passage review as a question of suitable consistency or variation rather than requiring exact sameness; its tools compare original-language passages and target translations for review.[^paratext-parallels]

## 21. Translation lineage and independence

The TNC records relationships such as:

```text
REVISES
DERIVES_FROM
CONSULTS
ADAPTS
MODERNIZES
TRANSLATES_THROUGH
SHARES_COMMITTEE_OR_EDITORIAL_LINEAGE
SHARES_SOURCE_EDITION
INHERITS_PASSAGE_WORDING
DUPLICATE_INSTANCE_OF
POSSIBLY_DEPENDENT
INDEPENDENT_WITHIN_SCOPE
DEPENDENCE_UNKNOWN
```

Relationships may be:

- work-wide;
- edition-wide;
- book-specific;
- passage-specific;
- phrase-specific.

Textual similarity may generate a lineage candidate. It cannot establish dependence without reviewed evidence.

### 21.1 Independent-count projections

Any report that counts translations must state its unit:

```text
instances
editions
works
revision families
independent translation projects
unknown independence
```

No runtime answer or benchmark scorer may treat instance count as independent evidence.

### 21.2 Data splitting

Training and benchmark partitions must hold out at least some complete translation families or revision lineages. Random verse splitting is insufficient.

## 22. Ancient translations and daughter versions

Ancient versions enter the same translation architecture, with additional controls completed in DR-08.

The TNC must support:

- direct translation from Hebrew, Aramaic, or Greek;
- uncertain or changing source bases;
- daughter versions translated through another version;
- revision toward another source tradition;
- passage-specific translation technique;
- retroversion candidates;
- textual-witness use that remains separate from translation analysis.

An ancient version difference may be caused by:

- a different source text;
- target-language constraints;
- translator technique;
- paraphrase;
- harmonization;
- revision;
- later corruption;
- a daughter-version relationship.

The TNC must not infer an exact source reading from the version alone.

## 23. Cross-language and multilingual comparison

The architecture must separately record:

```text
source language
target translation language
question language
answer language
quoted-source language
display-translation language
translation provenance
```

### 23.1 No hidden English pivot

Where direct source-to-target analysis is available, the system must not silently reason through English and present the result as native-language analysis.

A pivot translation may be used when necessary, but the output must record:

- pivot language;
- pivot translation identity;
- whether the pivot is published, human, or model-generated;
- additional uncertainty introduced.

### 23.2 Target-language expertise

A diagnosis that relies on a target-language constraint requires suitable evidence or review in that language. Model fluency alone is not expert validation.

### 23.3 Cross-language quotation

A quotation translated by the assistant must be labeled as a project or model translation and must not be attributed verbatim to the original author.

## 24. Paratext and page-image integration

The TNC operates only on text layers correctly classified under DR-14.

A page comparison must distinguish:

```text
CANONICAL_TRANSLATION_TEXT
TRANSLATOR_NOTE
STUDY_NOTE
SECTION_HEADING
CROSS_REFERENCE
VERSE_NUMBER
TYPOGRAPHIC_MARKING
USER_ANNOTATION
ILLEGIBLE
```

A study note's wording must not enter a translation-difference unit as if it were canonical text.

Capitalization, punctuation, paragraphing, red letters, and headings may carry interpretive effects but must retain their editorial layer.

## 25. Data-promotion lifecycle

All translation-nuance records follow an append-only promotion process.

```text
IMPORTED_UNVERIFIED
ALGORITHMIC_CANDIDATE
MODEL_GENERATED_CANDIDATE
HUMAN_REVIEWED
EXPERT_REVIEWED
APPROVED_FOR_RUNTIME
APPROVED_FOR_TRAINING
APPROVED_FOR_BENCHMARK
CONTESTED
REJECTED
RETRACTED
```

Promotion records:

- exact prior revision;
- reviewing agent;
- evidence inspected;
- changes made;
- purpose-specific approval;
- graph snapshot;
- timestamp;
- content hash.

Human editing does not erase machine generation or imported provenance. Paratext's custom interlinear workflow, which proposes statistical glosses that improve through translator interaction, is a useful operational precedent for separating machine candidates from reviewed human decisions.[^paratext-interlinear]

## 26. Runtime logical operations

DR-16 will define service boundaries and transport syntax. DR-06 defines the required logical operations.

### `compare_translation_realizations`

Input:

```text
passage selection
source edition revisions
translation edition revisions
comparison purpose
active canon/reference context
requested answer language
```

Output:

```text
comparison frame
difference units
alignments
candidate diagnoses
interpretive effects
lineage context
evidence and counterevidence
uncertainty and unresolved questions
```

### `diagnose_translation_difference`

Returns one or more causal chains. It must be able to return:

```text
INSUFFICIENT_EVIDENCE
COMPETING_DIAGNOSES
NOT_A_MATERIAL_TRANSLATION_DIFFERENCE
```

### `get_translation_alignment`

Returns versioned, provenance-bearing alignment links rather than one opaque word map.

### `trace_translation_lineage`

Returns work, edition, revision, and passage-level dependencies with evidence and independence warnings.

### `explain_rendering`

Explains the source basis, linguistic construal, target realization, likely cause, effect, alternatives, and uncertainty at the requested depth.

### `generate_translation_options`

Generates explicitly labeled candidate translations with declared tradeoffs. It never adds them to the published-translation corpus automatically.

## 27. Required runtime answer contract

A substantive translation comparison should be able to expose:

1. **Texts and editions** — what exact forms are being compared.
2. **Textual state** — whether a source-reading difference is involved.
3. **Linguistic issue** — morphology, syntax, lexicon, discourse, or other source construal.
4. **Translation operations** — what each target realization does.
5. **Target constraints** — what the receiving language requires or encourages.
6. **Lineage and policy** — whether wording is inherited or documented by project policy.
7. **Interpretive effect** — what becomes explicit, implicit, narrowed, broadened, or resolved.
8. **Assessment** — the strongest diagnosis and alternatives.
9. **Uncertainty** — what cannot be established.
10. **Evidence** — exact source spans and supporting scholarship.

The interface may render a shorter answer, but the evidence ledger must preserve these distinctions.

## 28. Training-facing contracts

Training examples derived from the TNC must bind to:

```text
approved design revision
graph snapshot
source and target representation revisions
alignment-set revision
difference-unit revision
diagnosis revision
rights partition
split and leakage-cluster identity
review state
example generator and hash
```

### 28.1 Approved task families

The curriculum may include:

- source-to-target span alignment;
- alignment repair;
- source-reading difference versus translation-choice classification;
- multi-label translation-cause diagnosis;
- ordered causal-chain construction;
- source-edition compatibility;
- revision-family and lineage discrimination;
- terminology rendering analysis;
- parallel-passage consistency analysis;
- target-language constraint explanation;
- generation of defensible options with tradeoffs;
- evidence selection and counterevidence identification;
- uncertainty and abstention;
- correction of lexical and etymological fallacies;
- translator-intent versus interpretive-effect discrimination;
- ancient-version retroversion restraint.

### 28.2 Required negative controls

Examples must include traps such as:

- many translations agree, therefore many manuscripts support the reading;
- different English wording, therefore the Greek differs;
- one Greek word has several dictionary glosses, therefore all apply here;
- a confessional publisher produced a rendering, therefore doctrine caused it;
- an ancient version differs, therefore its source text definitely differed;
- a model-generated gloss is a published translation;
- a section heading is part of the biblical text;
- identical wording means independent translation decisions;
- a target-language grammatical necessity is translator bias.

### 28.3 Gold-data restrictions

Model-generated diagnoses may provide candidates for review but cannot become benchmark gold or high-confidence training gold without the approved promotion path.

Synthetic examples must remain labeled and must not dominate evaluation-sensitive categories.

### 28.4 Sampling controls

Sampling must not weight a passage in proportion to the number of available translations or hosted instances. The training curriculum must define hierarchical selection by:

```text
task family
cause family
language
work and passage
translation lineage
edition
example
```

Broad verse-aligned resources such as eBible are valuable for multilingual coverage and initial passage correspondence, but their verse-per-line structure and removal of introductions, notes, footnotes, and other paratext mean they cannot serve as phrase-level Translation Nuance gold without additional segmentation, provenance, lineage, and expert review.[^ebible]

## 29. Benchmark contract

Translation Nuance is the benchmark's primary distinguishing track.

### 29.1 Required case families

1. Same source text, different lexical rendering.
2. Same source text, syntactic ambiguity.
3. Different source reading.
4. Different textual form or source edition.
5. Mixed textual and translational cause.
6. Target-language grammatical constraint.
7. Ambiguity preservation versus resolution.
8. Revision-family inheritance.
9. Documented translation policy.
10. Alleged confessional influence with insufficient evidence.
11. Ancient version: technique versus possible Vorlage.
12. Parallel-passage consistency and appropriate variation.
13. Terminology consistency without one-to-one gloss fallacy.
14. Paratext or page-layout difference.
15. No material difference despite surface variation.
16. Material difference despite similar wording.
17. Multilingual comparison without hidden English pivot.
18. Model-generated translation provenance.
19. Insufficient evidence and correct abstention.
20. Expert disagreement with several defensible diagnoses.

### 29.2 Evaluation modes

```text
CLOSED_BOOK
FIXED_PRIMARY_TEXT_PACKET
FIXED_FULL_EVIDENCE_PACKET
LIVE_TOOLS_AND_RETRIEVAL
IMAGE_ONLY
IMAGE_PLUS_TOOLS_AND_RETRIEVAL
```

A closed-book score cannot substitute for evidence-grounded system evaluation.

### 29.3 Primary metrics

```text
source_textual_state_accuracy
alignment_boundary_and_relation_accuracy
cause_multi_label_precision_recall_f1
causal_chain_order_accuracy
proximate_vs_upstream_cause_accuracy
lineage_and_independence_accuracy
intent_effect_separation_accuracy
evidence_sufficiency_and_fitness
citation_entailment
calibration_and_abstention
interpretive_effect_accuracy
target_language_constraint_accuracy
source_type_confusion_rate
lexical_fallacy_rate
expert_rated_explanation_faithfulness
```

No composite average may hide a source-type or citation hard failure.

### 29.4 Multiple defensible answers

Gold records may contain:

```text
accepted diagnoses
accepted causal chains
minority but defensible diagnoses
required uncertainty
unsupported diagnoses
prohibited overclaims
expert disagreement
```

The benchmark must not force a false single answer to a genuinely contested passage.

## 30. Validation invariants

The implementation must enforce at least the following invariants.

1. Every compared text span identifies an exact representation revision.
2. Every published translation realization identifies a translation edition revision.
3. Every translation instance resolves to an edition and work or remains explicitly unresolved.
4. Every alignment set identifies exact source and target revisions.
5. Every alignment link uses revision-stable selectors, not token indices alone.
6. Alignment does not imply semantic equivalence.
7. A difference unit cannot silently combine canonical text and paratext.
8. A source-reading diagnosis requires suitable textual evidence.
9. Translation wording alone cannot establish a different Vorlage.
10. A translation-policy diagnosis identifies evidence or remains tentative.
11. A confessional-cause diagnosis cannot be inferred from affiliation alone.
12. Interpretive effect and translator intent remain distinct.
13. Multiple hosted instances cannot count as independent translations.
14. Lineage candidates inferred from similarity remain candidates.
15. Model-generated translations and diagnoses remain labeled.
16. Benchmark gold requires purpose-specific approval.
17. Training examples bind to graph and ontology revisions.
18. Translation-family leakage is represented in split metadata.
19. A target-language constraint identifies the relevant language and evidence.
20. A pivot translation is disclosed.
21. An ancient-version retroversion remains uncertain unless independently supported.
22. No user-facing count of translations is presented as manuscript evidence.
23. No single quality score is produced without an explicit criterion and use profile.
24. Retractions or corrected alignments trigger impact analysis under DR-05.
25. Restricted text cannot leak through public comparison, training, benchmark, or report projections.

## 31. Hard failures

The following are hard failures when they occur materially:

- treating modern translations as manuscript witnesses;
- diagnosing a textual variant where the source text is the same;
- denying a textual variant that is directly relevant and available in evidence;
- claiming a different Vorlage solely from ancient-version wording;
- inventing translator intent;
- inferring confessional motivation from affiliation alone;
- presenting a dictionary gloss list as contextual meaning;
- forcing one-to-one word alignment where the relationship is many-to-many or null;
- treating alignment as equivalence;
- presenting a model-generated rendering as a published translation;
- counting duplicated instances as independent evidence;
- conflating headings, notes, punctuation, or layout with canonical translation text;
- hiding a pivot translation;
- presenting an algorithmic lineage or diagnosis candidate as accepted fact;
- suppressing meaningful alternative diagnoses;
- presenting uncertainty as exact probability without calibration;
- leaking restricted translation text;
- allowing benchmark or training labels to lose their source and review provenance;
- ranking translations globally without a stated purpose and evidence;
- changing an approved diagnosis destructively rather than versioning it.

## 32. Baseline neural-topology preservation and preregistered architecture-extension ladder

### 32.1 Baseline restriction

The first controlled baseline does not authorize unreviewed changes to:

- attention or Gated DeltaNet recurrence;
- positional encoding or multimodal alignment machinery;
- foundation transformer blocks;
- tokenizer vocabulary or segmentation;
- embedding or output tables;
- expert routing;
- a graph-neural component embedded in the foundation model;
- a CUDA kernel claimed to encode translation semantics.

This restriction exists to preserve attribution and pretrained capability while the project measures what an unchanged foundation model can do with high-quality Translation Nuance structure and supervision.

### 32.2 Architecture-extension ladder

Architectural specialization remains an approved research direction. Advancement occurs in this order unless a later owner-approved design review supplies evidence for a different order.

#### `A0 — Structured-system baseline`

No foundation-topology change:

```text
TNC graph
+ deterministic tools
+ retrieval
+ structured context
+ evidence ledger
```

This establishes the strongest unmodified-model baseline.

#### `A1 — Translation-aware training objectives`

Keep the foundation architecture unchanged while adding approved objectives such as:

- multi-label cause diagnosis;
- source-target alignment;
- causal-chain ordering;
- translation-family prediction;
- source-edition compatibility;
- textual-variant versus translation-choice classification;
- evidence selection;
- confidence and abstention.

These objectives may initially be expressed as generative tasks.

#### `A2 — Temporary or retained auxiliary heads`

Candidate heads may include:

- span-pair alignment;
- translation-cause classification;
- evidence-type classification;
- lineage-relation prediction;
- confidence calibration;
- claim/evidence entailment.

A head may shape the shared representation during training and then be removed, or remain available for analysis if its inference value is demonstrated.

#### `A3 — Relation-aware adapters`

Candidate modular additions may include:

- translation-relation adapters;
- passage-pair cross-attention adapters;
- relation embeddings;
- specialized low-rank adapters;
- an approved router between ordinary and Translation Nuance processing.

These modifications must remain bounded, reversible, and separately ablatable.

#### `A4 — Sidecar graph encoder or structured memory`

A dedicated module may encode or query the relevant Translation Nuance subgraph and supply it through:

- cross-attention;
- prefix or structured-memory representations;
- retrieved relation packets;
- a tool-mediated graph-query loop.

This tier is especially relevant if ordinary text serialization demonstrably loses relational structure.

#### `A5 — Specialist model or tiered system`

A separate specialist may perform alignment, causal classification, lineage inference, evidence ranking, or another bounded function. The language model then consumes its structured output for explanation and synthesis.

This tier also permits routing difficult Translation Nuance cases to a larger-capacity model where the benchmark demonstrates a capacity limit.

#### `A6 — Core foundation-model modification`

Only after the preceding tiers are evaluated may the project consider:

- new relation-aware foundation blocks;
- graph-neural components embedded in the decoder;
- specialized experts;
- translation-specific recurrent state;
- tokenizer or embedding changes;
- modified attention, DeltaNet, or equivalent core computations.

This is the highest-risk tier and requires a separate architecture design review.

### 32.3 Evidence required for escalation

An extension beyond `A0` or `A1` requires a falsifiable design and controlled experiment. Core-model modification in particular requires all of the following:

1. the Translation Nuance benchmark is demonstrably discriminative;
2. the strongest approved model-plus-tools baseline has a persistent, material deficit;
3. the deficit remains after appropriate improvements to data quality, evidence, retrieval, context representation, structured supervision, preference shaping, and model capacity are tested;
4. evidence indicates that the remaining failure is representational or computational rather than primarily factual, retrieval-related, or caused by weak labels;
5. the proposed extension states why it should address that specific deficit;
6. the experiment compares the same foundation checkpoint, data, training budget, harness, and benchmark with and without the extension;
7. expected gains justify compatibility, compute, deployment, quantization, reproducibility, and maintenance costs;
8. the project owner approves the applicable later design review and experiment.

### 32.4 Custom compute kernels

A custom compute kernel is permitted only as an implementation optimization for an already approved operation after profiling identifies a material bottleneck. It must:

- preserve numerical and semantic behavior within an approved tolerance;
- be compared with a reference implementation;
- expose the active kernel path in run telemetry;
- fail visibly rather than silently switching to a materially different implementation;
- preserve supported deployment and reproducibility requirements or document the exact limitation.

A compute kernel is never treated as the source of Translation Nuance semantics.

## 33. Rights and release behavior

Translation-nuance annotations may themselves contain protected source text or reproduce restricted wording.

Every alignment, difference unit, evidence packet, training example, benchmark case, and report must record:

- source rights partition;
- permitted quotation extent;
- training eligibility;
- redistribution eligibility;
- derived-annotation rights status;
- model-weight release implications where known.

A public graph may expose metadata, hashes, abstract cause labels, and permitted snippets without exposing restricted full text.

Rights behavior is completed in DR-10.

## 34. Sol implementation boundary

Project design authority defines:

- translation identity and lineage semantics;
- passage-scoped source assignments;
- alignment-set and alignment-link contracts;
- comparison and difference-unit semantics;
- cause ontology and causal-chain model;
- diagnosis, effect, option, terminology, and parallel-passage contracts;
- evidence and review requirements;
- runtime logical operations;
- training and benchmark projections;
- validation invariants;
- hard failures;
- baseline neural-topology preservation and the approved architecture-extension escalation policy.

Sol may implement these contracts and choose only reversible, local, design-neutral coding mechanics that preserve them.

Sol may not:

- flatten the cause ontology into one opaque label;
- replace evidence-bearing diagnoses with unqualified model output;
- reduce alignment to one-to-one token indices;
- infer translator motive or textual history without the required evidence;
- change the ontology, approval states, or hard-failure rules;
- skip or weaken the approved architecture-extension gates;
- authorize a modified model architecture without the applicable owner-approved design review;
- choose physical storage or serialization contrary to DR-28.

Any material conflict must stop with:

```text
BLOCKED_REQUIRES_DESIGN_REVIEW
```

## 35. Explicit non-goals

DR-06 does not:

- declare one translation universally best;
- assign a universal accuracy score;
- define the complete linguistic annotation model;
- select a critical edition;
- select final apparatus sources;
- reconstruct an original text from translations;
- infer translator intent without evidence;
- require word-level alignment for every corpus before useful operation;
- require every ancient version to be fully aligned;
- replace professional translation review;
- provide a production Bible-translation collaboration platform;
- choose physical databases, vector stores, graph stores, or serialization formats;
- define final UI visualization;
- authorize baseline core-model surgery, unprofiled custom compute kernels, or an architecture extension without its later owner-approved design and ablation;
- authorize main-model training.

## 36. Decisions DR-06 locks

Approval freezes these principles:

1. Translation Nuance is a custom semantic system at the system level, not merely a dataset or one model kernel.
2. Translation works, editions, instances, passage realizations, activities, and revisions are separate.
3. Source-base assignments are passage-scoped assertions and distinguish declared, compatible, inferred, intermediate, and unknown sources.
4. Alignments are versioned, directional, many-to-many, discontinuous, nullable, selector-based, and provenance-bearing.
5. Alignment never implies semantic equivalence.
6. Difference units are versioned editorial constructs within an exact comparison frame.
7. Translation causes are represented through a multi-axis ontology covering source state, source construal, transfer operation, target-language constraints, lineage/editorial causes, and paratext.
8. Diagnoses may be multi-causal, ordered, competing, or unresolved.
9. Upstream, proximate, and contributing causes are separate.
10. Source-reading claims require textual evidence; translation wording alone is insufficient.
11. Effects of renderings are separate from alleged translator intent.
12. Translation-policy and confessional diagnoses require suitable evidence.
13. Translation lineage may be passage-specific and similarity alone cannot prove dependence.
14. Translation counts identify their unit and never become manuscript evidence.
15. Terminology consistency is contextual rather than mechanical one-to-one glossing.
16. Translation-technique profiles are scoped tendencies with explicit exceptions and cannot establish a passage diagnosis by themselves.
17. Parallel passages may be appropriately consistent or appropriately varied.
18. Ancient versions are both translations and potential textual witnesses, but those roles remain analytically separate.
19. Retroversion remains explicitly uncertain.
20. Cross-language analysis discloses pivots and preserves quotation provenance.
21. Model-generated translations, alignments, and diagnoses remain labeled and require explicit promotion.
22. Runtime operations return structured evidence, uncertainty, and lineage—not only prose.
23. Training examples bind to graph, ontology, rights, split, and review revisions.
24. Translation-family leakage is controlled in benchmark and training splits.
25. Translation Nuance is the benchmark's primary distinguishing track.
26. Multiple defensible diagnoses and expert disagreement remain representable.
27. The baseline preserves the selected foundation model's neural topology in order to establish attribution and retain pretrained capability.
28. Architectural innovation remains a preregistered research path through structured objectives, auxiliary heads, relation-aware adapters, sidecar graph memory, specialist models or routing, and—only at the final tier—core foundation-model modification.
29. Advancement along that ladder requires a persistent benchmarked deficit, evidence that the deficit is representational rather than primarily caused by data, retrieval, supervision, or capacity, and an owner-approved controlled ablation.
30. Custom GPU kernels may optimize approved operations only after profiling identifies a material bottleneck and equivalence is demonstrated; they do not supply semantic capability.
31. Rights restrictions propagate through alignments, examples, benchmarks, and reports.
32. Translation Nuance receives dedicated hard-failure gates that cannot be hidden by aggregate scores.

## 37. Decisions intentionally deferred

DR-06 does not yet select:

- exact internal ID or URI syntax;
- canonical JSON, JSON-LD, relational, graph, or tabular serialization;
- physical storage and index products;
- alignment algorithms or model families;
- tokenization or segmentation algorithms;
- exact alignment-review workflow;
- exact confidence-calibration representation;
- final taxonomy extension process;
- detailed Greek, Hebrew, Aramaic, Syriac, Latin, Coptic, or target-language feature schemas;
- ancient-version-specific retroversion rules;
- final scholarship retrieval and citation ranking;
- UI visualizations;
- benchmark case count and scoring thresholds;
- training objective weights;
- auxiliary-head architecture and retention policy;
- relation-aware adapter architecture;
- sidecar graph encoder or structured-memory architecture;
- specialist-model and routing architecture;
- any core foundation-model modification;
- model family or model size;
- release eligibility of any source-specific derivative.

These are completed in DR-07 through DR-12, DR-13, DR-16 through DR-23, DR-28, and the approved experiment designs.

## 38. Approved statement

> **Biblical Scholar Lab will use an evidence-bearing Translation Nuance Core that represents translation works, editions, revisions, instances, source assignments, passage realizations, many-to-many alignments, comparison frames, difference units, causal diagnoses, translation operations, target-language constraints, lineage, terminology decisions, interpretive effects, and uncertainty as separate, versioned entities. Translation differences will be diagnosed through an ordered multi-axis causal model that distinguishes source textual state, source-language construal, transfer operation, target-language realization, revision lineage, and paratext. The system will not treat alignment as equivalence, translation frequency as independent evidence, ancient-version wording as certain retroversion, interpretive effect as translator intent, or model output as accepted scholarship. All runtime explanations, training examples, benchmark cases, and reports will remain bound to exact source revisions, evidence, rights, review state, graph snapshot, and leakage controls. The baseline will preserve the selected foundation model's neural topology in order to establish scientific attribution, retain pretrained multilingual and multimodal capabilities, and avoid premature infrastructure lock-in. This does not foreclose Translation Nuance architectural innovation: the project preregisters an escalation ladder covering structured objectives, temporary auxiliary heads, relation-aware adapters, sidecar graph memory, specialist models or routing, and—in the final tier—foundation-block modification. Advancement requires a persistent benchmarked Translation Nuance deficit, evidence that the deficit is representational rather than primarily caused by data, retrieval, capacity, or supervision, and an owner-approved controlled ablation whose gains justify compatibility, compute, deployment, and reproducibility costs. Custom GPU kernels may optimize approved operations only after profiling identifies a material bottleneck; they are not treated as a source of semantic capability.**

## 39. External reference anchors

These resources inform interoperability, corpus identity, alignment, and translation-workflow requirements. They do not replace the project's approved internal contracts or source-specific scholarly review.

[^targum]: Maciej Rapacz and Aleksander Smywiński-Pohl, *Targum — A Multilingual New Testament Translation Corpus*. The public dataset distinguishes translation works, editions, and per-site instances; includes verse text, metadata, embeddings, and similarity artifacts; and records source-level licensing: https://huggingface.co/datasets/mrapacz/targum-corpus

[^macula-greek]: Clear Bible, *MACULA Greek*. The repository supplies Greek New Testament syntax trees, morphology, word senses, semantic roles, participant referents, and mappings in several representations: https://github.com/Clear-Bible/macula-greek

[^macula-hebrew]: Clear Bible, *MACULA Hebrew*. The repository supplies Hebrew Bible text, morphology, syntax, word senses, semantic roles, participant referents, and multiple data representations: https://github.com/Clear-Bible/macula-hebrew

[^ebible]: BibleNLP, *eBible*. The corpus provides verse-aligned multilingual Bible data while preserving per-translation license terms; its verse-level format also demonstrates why verse alignment alone is insufficient for phrase-level Translation Nuance: https://github.com/BibleNLP/ebible

[^uw-alignment]: unfoldingWord, *Developer Guide — Alignment Layer*. The guide documents source-to-target alignment embedded in USFM milestones, including source lemma, morphology, occurrence, and content attributes: https://docs.page/unfoldingWord/uW-Tools-Collab/2-unfoldingword-developer-guide

[^usfm]: United Bible Societies, *Unified Standard Format Markers*. USFM represents structured scripture content, word-level attributes, linking attributes, milestones, footnotes, cross-references, and other layers: https://docs.usfm.bible

[^usx]: United Bible Societies, *Unified Scripture XML*. USX preserves document structure and overlapping milestones rather than reducing scripture to a flat verse table: https://ubsicap.github.io/usx/

[^paratext-terms]: Paratext, *Translate Consistently with Key Biblical Terms*. The tool supports source-term lists, target renderings, occurrence checks, comparison texts, and contextual consistency review: https://paratext.org/features/biblical-terms/

[^paratext-parallels]: Paratext, *Translate Parallel Passages Consistently*. The tool compares source and translation passages and supports review of appropriate consistency or variation: https://paratext.org/features/parallel-passage-checking/

[^paratext-interlinear]: Paratext, *Create Custom Interlinear Texts*. The interlinearizer supports statistically proposed glosses and human refinement between languages, illustrating the need to preserve algorithmic candidates and review state: https://paratext.org/features/create-custom-interlinears-texts/
