# DR-08 — Ancient Versions and Apparatus Policy

| Field | Value |
|---|---|
| Design ID | `DR-08` |
| Status | `APPROVED` |
| Approval date | 2026-08-15 |
| Project owner | Joseph Abbud |
| Designer and independent reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2; DR-03; DR-04; DR-05; DR-06; DR-07 |
| Implementation authority | GPT-5.6 Sol, under the approved design |

## 1. Purpose

Biblical Scholar Lab needs to use ancient translations and critical apparatuses without turning either into a shortcut around textual history.

Ancient versions are indispensable because they can preserve:

- early translation choices;
- evidence about source-text states;
- reception history;
- language-specific interpretation;
- revision and daughter-version relationships;
- traditions not fully preserved in the surviving source-language manuscripts.

They are also difficult evidence. A reading in Syriac, Latin, Coptic, Armenian, Georgian, Ethiopic, Arabic, Gothic, an Aramaic Targum, or a Greek Jewish translation can arise from several causes:

- a different source reading;
- a different source textual form;
- ordinary translation technique;
- target-language grammar;
- explicitation or paraphrase;
- harmonization;
- revision against another version or the source language;
- a daughter-version relationship;
- later corruption in the version's own transmission;
- editorial reconstruction in a modern edition.

Critical apparatuses are likewise indispensable and limited. They are edited scholarly reports governed by:

- a particular edition;
- an explicit or implicit apparatus policy;
- selected witnesses;
- local sigla and abbreviations;
- variation-unit boundaries;
- editorial judgments;
- coverage thresholds;
- source reports and transcriptions of varying proximity to the underlying witnesses.

An apparatus is therefore not the manuscript tradition itself. Its silence does not automatically establish absence; its lemma is not necessarily an autograph; and a witness citation may be a report several steps removed from direct inspection.

DR-08 defines the logical and epistemic contract for:

- ancient-version traditions, recensions, editions, witnesses, and passage realizations;
- direct and daughter-version source relationships;
- versional evidence and retroversion limits;
- critical-apparatus publications, entries, readings, sigla, scope, and evidence chains;
- direct observation versus transcription, collation, apparatus, and secondary report;
- Hebrew Bible, Septuagint, New Testament, and ancient-version apparatus patterns;
- patristic citation evidence;
- open, licensed, transient, metadata-only, and excluded access lanes;
- training-versus-retrieval eligibility;
- runtime tools, answer behavior, benchmark cases, and hard failures.

DR-08 does not select one apparatus as universally authoritative, grant rights to any restricted resource, or authorize model training on apparatus content. Rights and release decisions are finalized under DR-10, while physical storage and serialization are integrated under DR-28.

## 2. Governing principle

> **An ancient version is a translation tradition with its own textual history, not a transparent window into a lost source; a critical apparatus is an edition-specific scholarly report, not the underlying witness tradition. Every versional or apparatus claim must preserve source identity, evidential distance, editorial scope, uncertainty, rights, and the distinction between observation and inference.**

The system must preserve this chain:

```text
physical or textual witness
    → image or transcription
    → collation or versional alignment
    → apparatus or edition report
    → project-normalized evidence record
    → textual or translation diagnosis
    → scholarly assessment
```

No later layer may silently impersonate an earlier one.

## 3. Core commitments

### 3.1 Ancient translations have several roles

An ancient version can function as:

- a translation realization to analyze;
- a witness to the version's own textual history;
- indirect evidence about one or more possible source-text states;
- evidence for early interpretation and reception;
- evidence for historical language and translation technique;
- a source for later daughter versions.

These roles remain separate and passage-scoped.

### 3.2 Apparatus entries are editorial constructs

Variation-unit boundaries, lemmas, reading groups, witness lists, and notes belong to an identified apparatus revision and responsible editorial process.

They are not theory-neutral facts simply copied from manuscripts.

### 3.3 Evidential distance is explicit

A statement based on direct inspection of an image differs from one based on:

- a diplomatic transcription;
- a scholarly edition;
- a collation;
- a critical apparatus;
- another scholar's citation of an apparatus;
- model-generated reconstruction.

The assistant must report that distance when material.

### 3.4 Apparatus silence is not automatically negative evidence

A witness omitted from an apparatus entry may be:

- in agreement with the lemma under the apparatus's conventions;
- outside the selected witness set;
- not collated;
- lacunose;
- excluded by the edition's reporting threshold;
- represented under a group siglum;
- unreported for another reason.

Only the apparatus scope and legend can determine what silence means.

### 3.5 Retroversion is constrained inference

A translated wording may narrow possible source readings. It rarely proves one exact source-language sequence by itself.

The system must preserve several compatible source candidates where the target wording underdetermines the source.

### 3.6 Version labels are not monoliths

Terms such as:

- Septuagint;
- Old Latin;
- Vulgate;
- Syriac;
- Peshitta;
- Coptic;
- Targum;
- Armenian;
- Georgian;
- Ethiopic;
- Arabic;

cannot serve as sufficient passage-level witness identities without a more specific tradition, textual form, witness, edition, and source-chain record.

### 3.7 Component rights are independent

The running text, apparatus, images, transcriptions, introductions, annotations, and software of one publication may have different rights and access conditions.

Access to one component never implies permission to ingest, train on, redistribute, or quote another.

### 3.8 Restricted evidence should normally remain external to weights

When rights permit local consultation but not training or redistribution, the material belongs in a controlled retrieval or evidence-packet lane rather than the model weights.

### 3.9 Exact claims require exact tools

The assistant must not rely on model memory for a claim such as:

- which witnesses support a reading;
- what an apparatus reports;
- whether a manuscript is lacunose;
- whether an ancient version is cited;
- what a critical editor concludes.

It must retrieve the identified apparatus or source record, or state that it cannot verify the claim.

## 4. Logical entity model

DR-08 requires the following logical entities. DR-28 will select their physical representation.

### 4.1 `AncientVersionTradition`

A historically identifiable translation tradition or family.

Required properties include:

```text
tradition_id
canonical_name
source_language_or_languages
target_language_and_variety
script_history
approximate_origin_interval
translation_direction
historical_community_or_context
known_revision_layers
known_daughter_versions
work_and_canon_scope
major_scholarly_identifiers
provenance
rights_summary
```

This is a broad identity, not a passage-level reading.

### 4.2 `VersionTextualForm`

A materially distinct textual form, recension, revision layer, or translation stage within a tradition.

Examples may include:

- Old Greek and later Greek revisions;
- Old Syriac and Peshitta forms;
- Philoxenian and Harklean revisions;
- Old Latin textual forms and Vulgate revisions;
- Sahidic and Bohairic traditions;
- separate Targumic works;
- version forms revised against another version or source text.

A `VersionTextualForm` records:

```text
form_id
parent_tradition
language_variety
work_scope
date_interval
revision_or_recension_type
probable_source_relationships
known_predecessors
known_daughters
responsible_agents_or_communities
supporting_assertions
competing_assertions
```

### 4.3 `VersionWitnessRoleAssignment`

Connects a physical or textual witness from DR-05 to a version tradition or form for an exact passage scope.

It records:

```text
witness_entity_revision
version_tradition_or_form
passage_scope
coverage_status
hand_or_layer
sigla_and_catalog_aliases
assignment_assertion
review_state
```

A manuscript may contain more than one version form or revision layer.

### 4.4 `VersionEdition`

A specific scholarly edition, transcription, or publication of a version.

It records:

```text
edition_revision
edited_version_form
base_witnesses
editorial_method
running_text_policy
apparatus_policy
normalization_policy
reference_scheme
introductions_and_commentary
rights_by_component
source_artifacts
```

### 4.5 `VersionPassageRealization`

The exact passage realization in a version witness or edition revision.

It binds:

- DR-04 passage selection;
- DR-05 textual-representation revision;
- DR-07 linguistic view;
- DR-06 translation-realization identity;
- exact provenance and rights.

### 4.6 `VersionSourceRelationshipAssertion`

A passage-scoped claim about source direction and dependence.

Relation values include:

```text
DIRECT_TRANSLATION_FROM_SOURCE_LANGUAGE
REVISED_AGAINST_SOURCE_LANGUAGE
TRANSLATED_FROM_INTERMEDIATE_VERSION
REVISED_FROM_PREDECESSOR_VERSION
DAUGHTER_VERSION_OF
MIXED_SOURCE_DEPENDENCE
COMPATIBLE_WITH_SOURCE_READING
POSSIBLE_SOURCE_RELATIONSHIP
SOURCE_RELATIONSHIP_CONTESTED
SOURCE_RELATIONSHIP_UNKNOWN
```

The assertion records method, evidence, counterevidence, chronological plausibility, translator-technique assumptions, and confidence dimensions.

### 4.7 `TranslationTechniqueProfile`

A scoped description of recurring translation behavior.

The scope must identify:

```text
version form
work or passage class
source edition or reconstructed source
linguistic features examined
method
data coverage
exceptions
responsible scholar or project
review state
```

A profile is evidence for evaluating a passage. It never proves a passage-level source reading by itself.

### 4.8 `ApparatusPublication`

The stable identity of a critical apparatus or edition containing one.

Examples include a hand edition, editio maior, apparatus volume, digital apparatus, versional apparatus, or specialized collation publication.

### 4.9 `ApparatusRevision`

An immutable revision of the apparatus.

It records:

```text
publication_id
revision_id
edition_and_volume
publication_date
covered_works
base_or_lemma_text
editorial_team
methodology
apparatus_type
legend_revision
witness_selection
inclusion_thresholds
known_errata
source_artifacts
rights_by_component
```

### 4.10 `ApparatusScopeProfile`

Defines what the apparatus attempts to report and what silence may mean.

Required dimensions include:

```text
positive_or_negative_reporting_policy
selected_witness_universe
versional_evidence_policy
patristic_evidence_policy
orthographic_variant_policy
punctuation_policy
correction_and_hand_policy
lacuna_policy
minority_reading_threshold
subsingular_reading_policy
conjecture_policy
normalization_policy
book_or_passage_exceptions
completeness_claim
```

The profile may differ by volume, book, passage, or evidence class.

### 4.11 `ApparatusLegendRevision`

The edition-specific definitions of:

- sigla;
- abbreviations;
- punctuation;
- qualifiers;
- correction notation;
- versional group symbols;
- uncertainty markers;
- omission conventions;
- cross-references.

No apparatus parser may assume that identical-looking symbols have universal meanings across publications.

### 4.12 `ApparatusEntry`

A versioned editorial record at an exact locus.

It includes:

```text
entry_id
apparatus_revision
locus
variation_unit
lemma_or_anchor
reading_groups
witness_citations
version_citations
patristic_citations
conjectures
editorial_notes
source_note
raw_representation
normalized_representation
parser_and_review_state
```

### 4.13 `ApparatusReading`

A reading as represented by the apparatus editor.

It records:

```text
reading_text_or_symbol
language
normalization
reading_type
reading_group
sequence_or_local_stemma_position
cited_witnesses
cited_hands_or_corrections
source
editorial_responsibility
certainty
```

An apparatus reading is not automatically a new direct transcription of every cited witness.

### 4.14 `ApparatusWitnessCitation`

A citation by one apparatus of a witness, version, patristic source, or group.

It must distinguish:

```text
INDIVIDUAL_WITNESS
WITNESS_HAND_OR_CORRECTOR
WITNESS_GROUP
VERSION_TRADITION
VERSION_FORM
PATRISTIC_AUTHOR_OR_WORK
LECTIONARY_GROUP
MANUSCRIPT_FAMILY_LABEL
OTHER_EDITORIAL_GROUP
```

The citation preserves the source siglum exactly and maps it, where possible, to DR-05 identities through a reviewed alias record.

### 4.15 `ApparatusEvidenceChain`

Connects an apparatus claim to the evidence the apparatus used or cited.

A chain may be:

```text
physical manuscript
→ image
→ transcription
→ collation
→ apparatus entry
→ project record
```

or:

```text
ancient version edition
→ versional collation
→ apparatus citation
→ project record
```

or:

```text
prior apparatus
→ later apparatus
→ project record
```

Unknown links remain unknown rather than being invented.

### 4.16 `ApparatusCoverageAssertion`

A claim about whether a witness, passage, variant class, or source type was examined or reportable under the apparatus policy.

Coverage states include:

```text
EXPLICITLY_COLLATED
IN_SCOPE_AND_REPORTED_BY_SILENCE_POLICY
SELECTED_BUT_COVERAGE_UNCERTAIN
OUTSIDE_SELECTED_WITNESS_SET
OUTSIDE_APPARATUS_POLICY
NOT_COLLATED
LACUNOSE_OR_DAMAGED
NOT_APPLICABLE
UNKNOWN
```

This entity is required before apparatus silence can be interpreted as agreement or absence.

## 5. Evidence-proximity ladder

Every textual claim receives an `EvidenceProximity` value.

```text
DIRECT_PHYSICAL_OR_IMAGE_OBSERVATION
DIRECT_DIPLOMATIC_TRANSCRIPTION
DIRECT_NORMALIZED_TRANSCRIPTION
PRIMARY_COLLATION_FROM_IDENTIFIED_TRANSCRIPTION
CRITICAL_EDITION_OR_APPARATUS_REPORT
SPECIALIZED_CATALOG_OR_DATABASE_REPORT
SECONDARY_SCHOLARLY_REPORT
TERTIARY_SUMMARY
MODEL_OR_ALGORITHMIC_CANDIDATE
UNKNOWN
```

### 5.1 Proximity is not identical to reliability

A high-quality critical apparatus may be more useful than an untrained observer's direct inspection. The ladder records evidential distance, not an automatic quality ranking.

Reliability is separately assessed through:

- source quality;
- responsible agent;
- method;
- review;
- image quality;
- transcription quality;
- apparatus scope;
- correction history;
- independent confirmation.

### 5.2 The assistant must not upgrade evidence silently

Examples of prohibited upgrading include:

- “the manuscript reads” when only an apparatus was checked;
- “the Syriac proves” when only a modern version edition was consulted;
- “all manuscripts omit” when one selective apparatus was silent;
- “the original Hebrew was” when only a retroversion candidate exists.

Preferred wording includes:

- “This apparatus reports witness X with reading Y.”
- “The accessible transcription gives Y at this locus.”
- “The Syriac wording is compatible with source readings X and Z.”
- “I have not directly inspected the manuscript image.”

## 6. Ancient-version analytical roles

A version passage may receive one or more independent role assignments.

### 6.1 `TRANSLATION_REALIZATION`

Used to analyze how an identified source or candidate source was rendered.

### 6.2 `VERSION_INTERNAL_WITNESS`

Used to reconstruct the textual history of the version itself.

### 6.3 `INDIRECT_SOURCE_TEXT_WITNESS`

Used as evidence concerning one or more possible source-language readings.

This role always requires a source-relationship and retroversion assessment.

### 6.4 `RECEPTION_HISTORY_EVIDENCE`

Used to show how a passage was understood, transmitted, read, or used in a historical community.

### 6.5 `LINGUISTIC_EVIDENCE`

Used for the target language, dialect, register, or translation technique.

### 6.6 `DAUGHTER_VERSION_SOURCE`

Used when another version is translated or revised through this version.

One role never implies the others.

## 7. Ancient-version family requirements

DR-08 does not attempt to settle every version's history. It requires a language- and tradition-specific profile before the version supports high-confidence analysis.

### 7.1 Greek Jewish translations and the Septuagintal tradition

The system must distinguish, where relevant:

- Old Greek translation layers;
- later Greek revisions;
- kaige-type revision phenomena;
- Aquila, Symmachus, Theodotion, and other identifiable revision traditions;
- Hexaplaric and post-Hexaplaric influence;
- separate textual forms within books;
- daughter versions translated from Greek;
- edition-specific reconstructed texts;
- manuscript evidence and recensional hypotheses.

“The Septuagint says” is insufficient where the passage or edition is materially disputed.

### 7.2 Aramaic Targumic traditions

The system must identify the specific Targum, language variety, work, witness or edition, and historical layer.

It must not treat “the Targum” as one translation or as direct evidence for one Hebrew source text.

Paraphrase, expansion, interpretive tradition, liturgical use, and later transmission are first-class considerations.

### 7.3 Syriac traditions

The system must distinguish, where relevant:

- Old Syriac forms;
- the Peshitta;
- Philoxenian and Harklean revisions;
- Syro-Hexaplaric material;
- Christian Palestinian Aramaic;
- Diatessaronic evidence;
- direct translation, revision, and daughter-version relationships;
- Syriac dialect, script, vocalization, and manuscript layer.

The label `syr` in an apparatus cannot be expanded into a precise passage-level Syriac witness claim without the apparatus legend and underlying source report.

### 7.4 Latin traditions

The system must distinguish:

- Old Latin textual traditions and individual witnesses;
- the Vulgate and its internal transmission;
- Jerome's different translation and revision activities by work;
- later Vulgate recensions and editions;
- liturgical and patristic Latin quotations;
- translations revised from predecessors or source languages.

“Old Latin” is not one uniform version.

### 7.5 Coptic traditions

The system must identify:

- dialect;
- textual form;
- witness;
- edition;
- translation direction and possible source form;
- automatic versus human annotation;
- reference and alignment uncertainty.

Sahidic, Bohairic, and other dialectal evidence cannot be conflated.

### 7.6 Armenian, Georgian, Gothic, Ethiopic, Arabic, and other versions

Each requires a version-specific profile covering:

- language variety and script;
- translation date range;
- direct or intermediate source relationships;
- revision history;
- witness coverage;
- edition quality;
- translator technique;
- rights and access;
- expert-review availability.

Arabic in particular may derive from Greek, Syriac, Coptic, or mixed sources and cannot be treated as one uniform source relationship.

### 7.7 No hierarchy by language prestige

The system must not rank versional evidence by cultural familiarity. Weight depends on:

- date;
- source relationship;
- passage coverage;
- translation technique;
- textual history;
- witness quality;
- edition quality;
- evidential fit for the question.

## 8. Retroversion policy

Retroversion is the inference from target-language wording to one or more possible source-language forms.

DR-08 defines the following levels.

```text
R0_NO_RETROVERSION
R1_SEMANTIC_COMPATIBILITY_ONLY
R2_STRUCTURAL_OR_GRAMMATICAL_COMPATIBILITY
R3_SOURCE_READING_COMPATIBILITY_SET
R4_CONSTRAINED_RETROVERSION_CANDIDATE
R5_EXPERT_REVIEWED_RETROVERSION_HYPOTHESIS
```

### 8.1 `R0_NO_RETROVERSION`

The evidence is insufficient or the task does not require a source reconstruction.

### 8.2 `R1_SEMANTIC_COMPATIBILITY_ONLY`

The version conveys a semantic result compatible with one or more source readings, but target wording does not constrain form sufficiently.

### 8.3 `R2_STRUCTURAL_OR_GRAMMATICAL_COMPATIBILITY`

The target grammar constrains some structural features while leaving lexical or morphological alternatives open.

### 8.4 `R3_SOURCE_READING_COMPATIBILITY_SET`

A bounded set of known source readings is compatible or incompatible with the version under an identified translation-technique model.

### 8.5 `R4_CONSTRAINED_RETROVERSION_CANDIDATE`

A candidate source form is generated with explicit alternatives, assumptions, and uncertainty. It remains a project candidate, not a directly attested reading.

### 8.6 `R5_EXPERT_REVIEWED_RETROVERSION_HYPOTHESIS`

Qualified review accepts a retroversion as useful for a defined scholarly purpose. It remains a hypothesis and never becomes direct source attestation.

### 8.7 Retroversion confidence is multidimensional

Required dimensions include:

```text
version_text_certainty
version_witness_coverage
translation_direction_certainty
translator_technique_model_quality
target_language_constraint_strength
source_candidate_distinctiveness
chronological_plausibility
revision_or_contamination_risk
expert_review_status
```

No single score may hide a weak dimension.

### 8.8 Retroversion hard rule

A retroverted form may not enter the source-language witness list as if it were directly attested.

It is stored as an inference linked to the version evidence.

## 9. Translation-technique prerequisite

Before an ancient version can provide strong source-text evidence, the project should know enough about the relevant translation technique to assess whether the target difference is likely to be source-driven.

Required questions include:

- Does the version normally preserve or rearrange word order?
- How does it handle articles, pronouns, verbal forms, particles, and conjunctions?
- Does it explicitate implicit subjects or objects?
- How does it handle idiom, metaphor, and ambiguity?
- Does it harmonize parallel passages?
- Is the passage in a heavily revised section?
- Does the version depend on an intermediate translation?
- Are there book-level or translator-level differences?

When the project lacks this profile, the assistant must lower confidence and avoid exact source reconstruction.

## 10. Daughter versions and pivot chains

A version may depend on another version rather than directly on the presumed source language.

The system records chains such as:

```text
Hebrew source tradition
→ Greek translation or revision
→ Syriac daughter version
→ later translation or revision
```

or:

```text
Greek New Testament
→ Syriac version
→ Arabic translation
```

A daughter version cannot count as independent confirmation of both the intermediate version and the source text without an explicit dependence analysis.

The runtime must disclose a materially relevant pivot chain.

## 11. Apparatus types and editorial scope

The system distinguishes:

```text
POSITIVE_APPARATUS
NEGATIVE_APPARATUS
SELECTIVE_APPARATUS
FULL_OR_MAJOR_APPARATUS
VERSIONAL_APPARATUS
ORTHOGRAPHIC_APPARATUS
PUNCTUATION_APPARATUS
GENETIC_OR_REVISION_APPARATUS
COMMENTARY_APPARATUS
DIGITAL_COLLATION_INTERFACE
MIXED_APPARATUS
```

These labels describe intended reporting behavior, not guaranteed completeness.

### 11.1 Positive apparatus

A positive apparatus may list both supporting and differing witnesses under its own conventions.

The project must still inspect the legend and coverage.

### 11.2 Negative apparatus

A negative apparatus may emphasize witnesses differing from the lemma and leave agreement implicit.

Silence can be interpreted only for witnesses and variant classes known to be in scope.

### 11.3 Selective apparatus

A hand edition may cite only readings judged significant or a selected witness set.

It cannot support claims about all known witnesses.

### 11.4 Major or comprehensive apparatus

A major apparatus may be much fuller while still embodying:

- witness selection;
- normalization;
- editorial grouping;
- passage-specific omissions;
- source limitations.

“Comprehensive” remains relative to its stated project scope.

## 12. Sigla and legends are local namespaces

A siglum is interpreted under:

```text
apparatus publication
apparatus revision
legend revision
work or volume
passage exceptions
```

The same symbol may mean different things elsewhere.

The system stores:

```text
source_siglum
source_display_form
local_meaning
mapped_entity_or_group
mapping_evidence
scope
review_state
```

It never strips qualifiers such as:

- first hand;
- corrector;
- uncertain reading;
- partial support;
- alternate hand;
- marginal reading;
- group qualification.

## 13. Individual witnesses, hands, and corrections

A manuscript witness citation may refer to:

- the first hand;
- one or more correctors;
- a marginal or interlinear reading;
- a lectionary adaptation;
- a supplied leaf;
- a later replacement;
- an uncertain or damaged reading.

DR-05 hand and layer identities must remain attached.

The system may not flatten:

```text
original hand
+ later correction
```

into one undifferentiated witness vote.

## 14. Lemma, critical text, and witness reading remain separate

An apparatus lemma may be:

- the critical text selected by the editor;
- a base-edition reading;
- an anchor text;
- a reading supplied for presentation.

It is not necessarily:

- the autograph;
- the earliest recoverable text;
- a reading in any one manuscript;
- the project's operational selection.

The assistant must say:

> “The edition prints X”

rather than:

> “The original says X”

unless a separate, qualified textual-critical assessment has been made.

## 15. Conjectures and editorial emendations

Conjectural readings are represented separately from attested readings.

A conjecture records:

```text
proposed_text
proponent
publication
method
rationale
passage scope
relationship to attested readings
reception history
review state
```

No conjecture may receive witness support unless a witness actually attests it.

A later manuscript discovery matching a conjecture creates a new attestation relationship; it does not retroactively make the earlier conjecture directly evidenced at the time it was proposed.

## 16. Genealogical and coherence methods

Method outputs such as local stemmata, textual-flow diagrams, and coherence measures are versioned scholarly analyses.

The system must preserve:

- method and software revision;
- apparatus and collation dataset;
- variation-unit definition;
- parameter choices;
- local versus global scope;
- editor judgment;
- competing analyses.

The INTF describes the initial New Testament text as not extant and reconstructed through textual-critical work; its CBGM analyzes genealogical relationships among variants passage by passage and derives relationships among textual witnesses from those local relationships. DR-08 therefore prohibits treating a CBGM output as a timeless whole-manuscript family label or direct observation.[^intf-cbgm]

## 17. Hebrew Bible apparatus profile

A Hebrew Bible apparatus may combine or distinguish:

- a diplomatic base manuscript;
- Masoretic notes;
- ketiv/qere;
- Dead Sea Scrolls and Judean Desert evidence;
- Samaritan Pentateuch evidence;
- Septuagintal evidence;
- Targumic evidence;
- Syriac evidence;
- Vulgate or Old Latin evidence;
- conjectural emendation;
- editorial commentary.

### 17.1 Diplomatic base versus eclectic reconstruction

The system must record whether the edition prints:

- one base manuscript diplomatically;
- a corrected or normalized base;
- an eclectic reconstruction;
- another edition policy.

The official description of Biblia Hebraica Quinta, for example, says it presents Codex Leningradensis diplomatically while providing a newly designed apparatus and commentary that draw on expanded textual evidence. That base-text policy must not be confused with a claim that every printed form is the editor's reconstructed earliest text.[^bhq]

### 17.2 Masorah is not generic apparatus noise

Masora parva, Masora magna, ketiv/qere, accentuation, and scribal phenomena require their own DR-07 and DR-05 representations.

They must not be flattened into ordinary manuscript-variant rows.

### 17.3 Versional evidence remains indirect

A Hebrew Bible apparatus citing Greek, Syriac, Latin, or Targumic evidence does not automatically supply an exact Hebrew retroversion.

The project must retain the apparatus's own wording and qualification and, where needed, conduct a separate versional analysis.

### 17.4 Text and apparatus rights may differ

The Society of Biblical Literature currently makes BHS text available without its critical apparatus. This illustrates why the project must classify the running text and apparatus as separate rights-bearing components rather than infer apparatus access from text access.[^bhs-sbl]

## 18. Greek New Testament apparatus profile

A Greek New Testament apparatus may draw on:

- Greek manuscripts;
- correctors and hands;
- lectionaries;
- ancient versions;
- patristic citations;
- conjectures;
- editorial analyses.

The ECM states that it documents Greek textual history using selected Greek manuscripts, older translations, and citations in ancient Christian literature. The digital ECM can link apparatus citations to manuscript transcriptions and, where available, images. This is the model DR-08 wants conceptually: an apparatus as a gateway into traceable evidence rather than a terminal truth table.[^ecm][^ecm-digital]

### 18.1 Concise versus major apparatus

A concise apparatus and the ECM cannot be interpreted as if they had the same witness universe or reporting threshold.

The assistant must identify which apparatus supports the claim.

### 18.2 Version group labels require expansion

Group citations such as Latin, Syriac, Coptic, or other versional shorthand remain apparatus reports until mapped to their underlying version sources.

### 18.3 Patristic evidence requires source criticism

A patristic citation can be:

- a direct quotation;
- an adapted quotation;
- an allusion;
- a lectionary form;
- a translation;
- a memory-based citation;
- a later textual interpolation;
- an editor's reconstructed biblical text within the patristic work.

It may serve as textual evidence only under an identified analysis.

## 19. Septuagint and Greek Old Testament apparatus profile

The project must distinguish:

- an edition's reconstructed Greek text;
- individual Greek manuscripts;
- Old Greek layers;
- recensional or revision hypotheses;
- Hexaplaric evidence;
- daughter-version evidence;
- retroverted Hebrew candidates;
- manuscript and version-specific orthography;
- edition-specific variation-unit boundaries.

A Greek reading is direct evidence for the Greek tradition. Its relevance to a Hebrew source state requires a separate translation and retroversion analysis.

The Göttingen critical-edition tradition and related projects demonstrate that Greek Old Testament textual work is itself a major critical-editing enterprise rather than one static “LXX text.” The current Göttingen Psalter project explicitly plans a hybrid printed and publicly accessible digital critical edition, reinforcing the need to bind claims to exact edition and revision.[^goettingen]

## 20. Patristic and other embedded biblical citations

Embedded citations receive at least three separate identities:

```text
host work passage
cited or echoed biblical passage
editorial reconstruction of the citation
```

The project records:

- host-work manuscript and edition;
- language;
- citation boundaries;
- formula of introduction;
- exactness or adaptation;
- surrounding argument;
- possible source version;
- editor responsibility;
- uncertainty.

A quotation repeated by several later authors may depend on one prior source and cannot automatically count as independent textual evidence.

## 21. Apparatus ingestion and parsing

### 21.1 Apparatus parsers are edition-specific

There is no universal regex or notation grammar for all apparatuses.

Each adapter requires:

- exact edition and legend revision;
- tested grammar;
- passage exceptions;
- witness-siglum mapping;
- raw-text preservation;
- round-trip or source-link validation;
- parse confidence;
- human-review state.

### 21.2 OCR is candidate generation

OCR or vision parsing of an apparatus page produces candidates. It cannot by itself create accepted witness assignments.

Small typography, superscripts, diacritics, punctuation, abbreviations, and column layouts make apparatus OCR particularly error-prone.

### 21.3 Raw representation is preserved

Every normalized entry retains a locator to the exact source page, region, XML node, or database record.

### 21.4 Parser updates create new revisions

A corrected parser or legend mapping creates new normalized apparatus records and a new graph snapshot. It does not silently rewrite historical experiment evidence.

## 22. User-provided apparatus and page images

A user may upload a photograph, screenshot, or scan of an apparatus, Bible, manuscript, or commentary that the project does not otherwise possess.

The system may, subject to privacy and rights policy:

- inspect it for the user's current task;
- parse visible entries;
- explain notation;
- link claims to the uploaded region;
- compare the report with accessible sources.

It must not automatically:

- add the image to the training corpus;
- persist it in a public index;
- redistribute it;
- infer that the user owns all relevant rights;
- claim a direct manuscript observation when the image is an apparatus page;
- treat an OCR result as reviewed truth.

The response should identify the uploaded source as user-provided evidence and state uncertainty where legibility is limited.

## 23. Access and operation lanes

DR-08 defines operation lanes. DR-10 will bind them to the full rights architecture.

```text
A0_OPEN_TRAINING_AND_RETRIEVAL
A1_OPEN_RETRIEVAL_ONLY
A2_LICENSED_LOCAL_RETRIEVAL
A3_LICENSED_TRANSIENT_QUERY
A4_REVIEWED_EVIDENCE_PACKET_ONLY
A5_METADATA_AND_BIBLIOGRAPHY_ONLY
A6_EXCLUDED
```

### 23.1 `A0_OPEN_TRAINING_AND_RETRIEVAL`

The exact component is explicitly permitted for the relevant training, local processing, retrieval, and intended derivative use.

This classification is component- and revision-specific.

### 23.2 `A1_OPEN_RETRIEVAL_ONLY`

Retrieval and quotation are permitted, but training or derivative-weight use is not established or intentionally excluded.

### 23.3 `A2_LICENSED_LOCAL_RETRIEVAL`

A user, institution, or project license permits local indexed use under access control.

The resource remains outside open-lineage weights and public indexes.

### 23.4 `A3_LICENSED_TRANSIENT_QUERY`

The system may query or display the resource in an authorized session but may not persist a local corpus or vector index beyond what the license permits.

### 23.5 `A4_REVIEWED_EVIDENCE_PACKET_ONLY`

A qualified person may construct a bounded case-specific evidence packet when permitted. The full source is not ingested.

### 23.6 `A5_METADATA_AND_BIBLIOGRAPHY_ONLY`

Only identity, catalog, citation, and access metadata may be stored or used.

### 23.7 `A6_EXCLUDED`

The component may not be acquired or used under the current evidence.

### 23.8 Public visibility is not permission

A web interface that allows reading or searching does not establish permission for:

- automated extraction;
- bulk local storage;
- model training;
- vector indexing;
- redistribution;
- derivative checkpoint release.

The NTVMR, for example, states that user contributions are CC BY while manuscript images come from different owners and may not be used outside the NTVMR without permission from the holding institution. The project must preserve those distinct rights rather than assign one site-wide license to every component.[^ntvmr-license]

### 23.9 Edition components can have different lanes

Current Peshitta work provides a useful example: the ETCBC reports that the running text of the Leiden Peshitta is publicly available without the critical apparatus, while the Brill portal contains the complete apparatus and introductions. DR-08 requires independent classifications for those components.[^peshitta]

Coptic SCRIPTORIUM likewise records source-specific corpus licenses and annotation quality; one Sahidic Old Testament corpus is CC BY-SA 4.0 and warns that versification or aligned translations may be imperfect. Open licensing does not remove the need to preserve quality and alignment warnings.[^coptic]

The Vetus Latina Database is a subscription publication of archival citation cards. Its existence and scholarly value do not imply bulk-training permission; absent explicit rights, it begins in a licensed or metadata-only lane.[^vetus-latina]

## 24. Training policy

### 24.1 Default rule

Ancient-version or apparatus content enters model training only when the exact component and derivative use are explicitly approved under DR-10.

### 24.2 Restricted apparatus remains external

Licensed, subscription, user-provided, or local-research-only apparatus content should normally support:

- retrieval;
- transient tool calls;
- private evaluation;
- evidence packets;
- expert adjudication.

It should not be baked into distributable weights.

### 24.3 Training can teach apparatus competence without copying restricted content

The project may train on:

- open apparatuses;
- public-domain critical editions;
- project-authored synthetic notation examples;
- abstract apparatus structures;
- open witness lists and transcriptions;
- expert-authored tasks that do not reproduce restricted expression beyond permission;
- tool-use traces and epistemic restraint.

### 24.4 No pseudo-gold from apparatus parsing

Automatically parsed entries remain candidates until validation appropriate to the training tier.

### 24.5 Versional training preserves role labels

A training example must distinguish:

```text
translation realization
version-internal variant
indirect source-text evidence
reception evidence
retroversion hypothesis
```

The model must not learn that any target-language difference directly equals a source-language variant.

### 24.6 Rights-aware model lineage

Every checkpoint records which access lanes contributed to its weights.

A model trained on a restricted component cannot later be relabeled as open because the original text is absent from the public repository.

## 25. Retrieval and tool policy

### 25.1 Retrieval authorization is request-scoped

The runtime verifies:

- user or project entitlement;
- component lane;
- geographic or institutional constraints where applicable;
- permissible excerpt and display;
- persistence and logging rules;
- export restrictions.

### 25.2 Restricted evidence does not leak through logs

Logs and handoffs may preserve:

- resource ID;
- query;
- record locator;
- result hash;
- aggregate outcome;

without storing restricted full text when not permitted.

### 25.3 Tool outputs preserve the edition's voice

A tool result distinguishes:

- raw apparatus wording;
- normalized parser interpretation;
- project mapping;
- model explanation.

### 25.4 Unavailable evidence produces abstention

When the relevant apparatus is not accessible, the assistant should say:

> “I cannot verify the witness support from the required apparatus or transcription presently available to me.”

It may offer a provisional answer using accessible evidence, clearly labeled.

## 26. Required runtime operations

The logical runtime must support operations such as:

```text
get_version_passage
compare_version_passages
get_version_witnesses
trace_version_source_relationship
get_translation_technique_profile
assess_source_reading_compatibility
get_retroversion_hypotheses
get_apparatus_scope
get_apparatus_entry
resolve_apparatus_siglum
get_witness_attestation
trace_apparatus_evidence_chain
inspect_witness_image_or_transcription
compare_apparatus_reports
explain_apparatus_notation
```

Each result must return:

- exact source and revision;
- passage scope;
- evidence proximity;
- source and target language;
- version or apparatus role;
- raw and normalized forms where permitted;
- rights lane;
- coverage and silence semantics;
- alternatives and counterevidence;
- review state;
- multidimensional confidence;
- warnings.

## 27. Answer contract

For an ancient-version or apparatus question, a strong answer should identify:

### Source identity

Which version tradition, textual form, witness, edition, apparatus, and revision are being used?

### What is directly reported or observed

What does the accessible evidence actually say?

### Evidential distance

Was the manuscript image inspected, a transcription checked, or an apparatus consulted?

### Translation or textual issue

Does the difference concern source state, translation technique, target language, revision, or several causes?

### Retroversion limits

Which source readings are compatible, incompatible, or unresolved?

### Apparatus scope

What can silence, omission, or group notation mean in this edition?

### Assessment

What conclusion is best supported, under which method and assumptions?

### Uncertainty

What evidence remains inaccessible, disputed, or underdetermined?

The interface may render this compactly in Brief or Study mode, but the evidence ledger retains all layers.

## 28. Benchmark design consequences

DR-08 creates a dedicated **Ancient Versions and Apparatus** benchmark track.

Required case families include:

- direct witness image versus apparatus report;
- selective-apparatus silence;
- positive versus negative apparatus;
- witness outside the selected set;
- lacunose witness;
- first hand versus corrector;
- group siglum versus individual witness;
- apparatus legend differences;
- conjecture versus attestation;
- critical-text lemma versus manuscript reading;
- apparatus disagreement;
- Old Greek versus later revision;
- direct version versus daughter version;
- translation technique versus possible source reading;
- constrained retroversion with several compatible readings;
- unsupported exact retroversion;
- ancient-version reception evidence;
- patristic citation adaptation;
- user-uploaded apparatus screenshot;
- OCR ambiguity;
- restricted-source access denial;
- open running text with restricted apparatus;
- version or apparatus unavailable;
- multilingual explanation of versional evidence.

### 28.1 Evaluation modes

```text
CLOSED_BOOK
FIXED_OPEN_EVIDENCE_PACKET
FIXED_RESTRICTED_PRIVATE_PACKET
LIVE_AUTHORIZED_TOOLS
IMAGE_ONLY
IMAGE_PLUS_TOOLS
```

### 28.2 Primary metrics

```text
source_identity_accuracy
apparatus_scope_accuracy
witness_attestation_accuracy
evidence_proximity_accuracy
siglum_resolution_accuracy
hand_and_correction_accuracy
silence_interpretation_accuracy
version_role_accuracy
source_relationship_accuracy
retroversion_set_accuracy
retroversion_overclaim_rate
translator_technique_fitness
conjecture_attestation_confusion_rate
citation_entailment
rights_lane_compliance
abstention_quality
expert_rated_textual_critical_faithfulness
```

### 28.3 Hard failures cannot be averaged away

An overall score cannot hide:

- fabricated witness support;
- illegal restricted-source use;
- exact retroversion from insufficient evidence;
- apparatus silence misrepresented as universal agreement;
- a conjecture represented as attested.

## 29. Human review requirements

High-stakes versional and apparatus benchmark cases require qualified review appropriate to the evidence.

Review coverage should eventually include:

- Greek New Testament textual criticism;
- Hebrew Bible textual criticism;
- Septuagint and Greek revisions;
- Syriac versions;
- Latin versions;
- Coptic versions;
- Targumic and Aramaic traditions;
- other version traditions represented in product claims;
- critical-editing and apparatus notation;
- rights and source access.

One expert is not assumed to cover every tradition.

## 30. Validation invariants

Sol's implementation must enforce at least these invariants.

1. Every apparatus record identifies an exact publication, revision, and legend.
2. Every witness siglum is interpreted in a local apparatus namespace.
3. Every apparatus entry retains its raw source locator.
4. Every normalized reading retains editor responsibility and source.
5. Apparatus silence cannot become agreement without a compatible scope assertion.
6. A witness outside the apparatus scope cannot be inferred to support the lemma.
7. A lacunose witness cannot be counted for or against a reading.
8. A corrector and first hand remain distinct.
9. A group siglum cannot silently become a list of individual witnesses.
10. A version tradition citation cannot silently become exact source-language text.
11. A retroversion candidate cannot become direct attestation.
12. Translation technique and source reading remain separate causal factors.
13. A daughter version cannot be counted as independent of its intermediate source without analysis.
14. A critical lemma cannot be labeled an autograph merely because it is printed.
15. A conjecture cannot acquire witness support without an attestation record.
16. Model-generated apparatus parsing remains labeled.
17. Rights are tracked independently for running text, apparatus, images, introductions, annotations, and software.
18. Restricted text cannot enter open model weights or public indexes.
19. User-provided images cannot enter training without explicit consent and rights review.
20. Every experiment binds to exact version, apparatus, parser, graph, and rights revisions.
21. A corrected parser creates a new revision rather than rewriting historical evidence.
22. Exact witness claims require a retrievable evidence chain or explicit inability to verify.
23. Patristic quotation and reconstructed biblical text remain distinct.
24. The assistant cannot claim consensus from one apparatus.
25. An edition's apparatus scope and reporting policy remain visible to the runtime.

## 31. Hard failures

The following are hard failures when material:

- claiming direct manuscript inspection when only an apparatus was used;
- fabricating a witness, siglum, reading, hand, or correction;
- treating apparatus silence as universal agreement without scope evidence;
- counting a lacunose or uncollated witness as evidence;
- expanding a version group citation into unsupported individual witnesses;
- treating an ancient translation as an exact source transcript;
- presenting a retroversion as directly attested;
- inferring a different source reading without considering translation technique;
- treating a daughter version as independent evidence;
- conflating Old Greek, later Greek revisions, and one generic Septuagint text;
- conflating Old Latin and the Vulgate;
- conflating Syriac or Coptic traditions and dialects;
- treating the apparatus lemma as the autograph;
- representing a conjecture as manuscript evidence;
- losing first-hand and corrector distinctions;
- citing a restricted apparatus beyond permitted use;
- training on a restricted apparatus without explicit permission;
- allowing restricted evidence to leak into public logs, benchmarks, or checkpoints;
- using OCR-parsed apparatus text as accepted evidence without required review;
- presenting a secondary report as if the primary witness were checked;
- hiding an unavailable evidence source while making a confident conclusion.

## 32. Sol implementation boundary

### 32.1 Sol must implement the approved logical contract

Sol may not independently decide:

- to collapse ancient version, witness, and source-text roles;
- to make one apparatus notation universal;
- to infer agreement from apparatus silence without scope;
- to discard raw apparatus forms;
- to treat retroversion as attestation;
- to ingest restricted apparatus content into training;
- to flatten rights across edition components;
- to omit evidence-proximity tracking;
- to select one version tradition as a universal source proxy;
- to convert model-generated parses into gold.

### 32.2 Sol's design-neutral discretion

Sol may choose reversible local mechanics such as:

- module, class, and function decomposition;
- internal data structures preserving every approved entity and invariant;
- parser implementation under edition-specific contracts;
- cache and index mechanics consistent with DR-10 and DR-28;
- test fixtures;
- performance optimizations proven semantically and rights-equivalent;
- approved or demonstrably equivalent dependencies.

### 32.3 Escalation

Sol must stop with:

```text
BLOCKED_REQUIRES_DESIGN_REVIEW
```

when:

- an apparatus cannot be represented without material information loss;
- a version tradition exposes a missing source-role contract;
- a license conflicts with an intended operation;
- a parser cannot preserve the source legend or raw representation;
- a training objective would require restricted content;
- a proposed simplification changes evidence semantics.

## 33. Explicit non-goals

DR-08 does not:

- select one universally authoritative critical edition;
- select a preferred initial text for every passage;
- declare one textual-critical method correct for all questions;
- create a complete catalog of every ancient version;
- assume complete digital access to every witness;
- license restricted apparatuses;
- authorize bulk scraping of public interfaces;
- define the final rights implementation of DR-10;
- require full phrase alignment for every ancient version before useful operation;
- require exact retroversion where the evidence underdetermines it;
- replace specialists in Syriac, Latin, Coptic, Septuagint, Targumic, Armenian, Georgian, Ethiopic, Arabic, or Gothic traditions;
- authorize model training;
- select physical databases or serialization;
- define final user-interface notation;
- authorize custom neural or compute kernels.

## 34. Decisions DR-08 locks

Approval would freeze these principles:

1. Ancient versions are translation traditions with their own textual histories, not transparent source transcripts.
2. Translation, version-internal witness, indirect source witness, reception, linguistic, and daughter-version roles remain separate and passage-scoped.
3. Version tradition, textual form, witness, edition, realization, and source-relationship assertion remain separate.
4. Version labels such as Septuagint, Syriac, Latin, Coptic, or Targum require more specific identities for consequential claims.
5. Apparatus publications, revisions, scope profiles, legends, entries, readings, citations, and evidence chains remain separate.
6. Apparatus entries are editorial constructs rather than direct manuscript data.
7. Evidence proximity is explicit and cannot be silently upgraded.
8. Apparatus silence has meaning only under a verified scope and reporting policy.
9. Sigla are interpreted in edition-local namespaces.
10. First hands, correctors, marginal readings, lacunae, and uncertainty remain distinct.
11. Critical lemmas, base texts, witness readings, and reconstructed texts remain separate.
12. Conjectures remain separate from attested readings.
13. Genealogical method outputs are versioned analyses, not timeless manuscript-family facts.
14. Hebrew Bible, New Testament, Septuagint, patristic, and versional apparatuses receive domain-specific profiles.
15. Retroversion uses the R0–R5 ladder and never becomes direct attestation.
16. Translation-technique evidence is required before strong source-text inference.
17. Daughter versions and pivot chains remain explicit and dependent evidence is not double-counted.
18. Apparatus parsers are edition-specific, source-preserving, versioned, and reviewable.
19. OCR and model-parsed apparatus content remains candidate evidence.
20. Running text, apparatus, images, introductions, annotations, and software receive independent rights and operation lanes.
21. Public visibility does not imply training, indexing, or redistribution permission.
22. Restricted apparatus content normally remains in authorized retrieval, transient query, or evidence-packet lanes rather than open weights.
23. Runtime tools return source identity, scope, proximity, rights, alternatives, and uncertainty.
24. The benchmark treats versional overclaim, apparatus-silence errors, conjecture confusion, and rights violations as hard failures.
25. Every experiment binds to exact version, apparatus, parser, graph, and rights revisions.

## 35. Decisions intentionally deferred

DR-08 does not yet select:

- default Greek New Testament apparatus;
- default Hebrew Bible apparatus;
- default Septuagint edition by work;
- final list of ancient versions admitted to version one;
- exact witness and version abbreviations in the interface;
- exact source licenses or subscriptions to purchase;
- complete source-by-source rights dispositions;
- final apparatus parser formats;
- exact private benchmark evidence packets;
- one preferred retroversion algorithm;
- one preferred textual-critical method;
- one CBGM implementation;
- physical database and index products;
- final API transport;
- exact human-review panel;
- quantitative coverage targets;
- main-model training examples or token mixture.

Those decisions belong to DR-09, DR-10, DR-16 through DR-23, DR-25, DR-28, and later owner-approved experiment designs.

## 36. Approved statement

> **Biblical Scholar Lab will treat every ancient version as a translation tradition with its own witnesses, editions, revision layers, translation technique, source relationships, reception history, and rights—not as a transparent transcript of a lost Hebrew or Greek source. Versional roles as translation realization, version-internal witness, indirect source-text evidence, reception evidence, linguistic evidence, and daughter-version source will remain separate and passage-scoped. Critical apparatuses will be represented as edition-specific, scope-governed scholarly reports with immutable revisions, local legends and sigla, editorial variation units, readings, witness citations, conjectures, coverage assertions, and traceable evidence chains. Direct observation, transcription, collation, apparatus report, secondary citation, and model inference will remain distinct. Apparatus silence will not imply agreement without verified scope; retroversion will use an explicit R0–R5 uncertainty ladder and will never become direct attestation; translation-technique and daughter-version dependencies will constrain source-text claims. Running text, apparatus, images, introductions, annotations, and software will receive independent access and rights lanes, with restricted evidence normally remaining in authorized retrieval or bounded evidence packets rather than distributable model weights. Runtime tools, training records, benchmarks, and reports will bind every claim to exact version, apparatus, parser, graph, rights, and review revisions, while fabricated witness support, unsupported exact retroversion, conjecture-attestation confusion, apparatus-silence overclaim, and restricted-source leakage remain hard failures.**

---

## References

[^intf-cbgm]: Institute for New Testament Textual Research, “CBGM.” The INTF explains that the initial text is not extant, that textual-critical reconstruction uses internal and external criteria, and that the CBGM analyzes genealogical relationships among variants passage by passage before drawing inferences concerning witnesses: https://www.uni-muenster.de/INTF/en/forschung/cbgm/index.html

[^bhq]: Deutsche Bibelgesellschaft, “Biblia Hebraica Quinta.” The publisher describes BHQ as a diplomatic presentation of Codex Leningradensis with a newly designed and expanded critical apparatus and commentary: https://shop.die-bibel.de/bhq

[^bhs-sbl]: Society of Biblical Literature, “Biblica Hebraica Stuttgartensia.” The SBL resource makes the BHS text available without the critical apparatus, illustrating the need for component-level access classification: https://www.sbl-site.org/resources/digital-texts/biblica-hebraica-stuttgartensia/

[^ecm]: Institute for New Testament Textual Research, “Editio Critica Maior.” The ECM documents Greek textual history from selected Greek manuscripts, older translations, and citations in ancient Christian literature: https://www.uni-muenster.de/INTF/en/forschung/ecm/index.html

[^ecm-digital]: INTF, “An Interactive Textual Commentary on Acts.” The digital ECM apparatus links cited manuscripts to transcriptions and, where available, images, demonstrating an apparatus-as-gateway model: https://ntvmr.uni-muenster.de/de/intfblog/-/blogs/an-interactive-textual-commentary-on-acts

[^goettingen]: Göttingen Academy of Sciences and Humanities, “Editio Critica Maior of the Greek Psalter.” The project describes a future hybrid critical edition in print and publicly accessible digital form: https://adw-goe.de/cs/research/research-projects-within-the-academies-programme/editio-critica-maior/

[^ntvmr-license]: New Testament Virtual Manuscript Room, “License Agreement.” NTVMR contributions are made available under CC BY, while images are provided under licenses from their respective owners and require permission for use outside the NTVMR: https://ntvmr.uni-muenster.de/license-agreement

[^peshitta]: Eep Talstra Centre for Bible and Computer, “Digitizing and Annotating the Syriac Versions of the Old Testament.” ETCBC reports that the Brill Peshitta Online contains the complete critical apparatus and introductions while the running text without the apparatus is publicly available on GitHub: https://etcbc.nl/computational-linguistics/digitizating-and-annotating-the-syriac-versions-of-the-old-testament/

[^coptic]: Coptic SCRIPTORIUM, “Sahidic Coptic OT corpora licensing information” and corpus metadata. The corpus is source-specifically licensed CC BY-SA 4.0, while its metadata warns about possible versification and alignment issues: https://copticscriptorium.org/download/corpora/sahidic_bible_ot.html

[^vetus-latina]: Brepols, “Vetus Latina Database.” The subscription database contains citations to the Old Latin Bible from patristic writings and returns images of archival card records: https://www.brepols.net/series/vld-o
