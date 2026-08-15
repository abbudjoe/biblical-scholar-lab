# DR-07 — Linguistic Representation

| Field | Value |
|---|---|
| Design ID | `DR-07` |
| Status | `APPROVED` |
| Approval date | 2026-08-15 |
| Project owner | Joseph Abbud |
| Designer and independent reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2; DR-03; DR-04; DR-05; DR-06 |
| Implementation authority | GPT-5.6 Sol, under the approved design |

## 1. Purpose

Biblical Scholar Lab needs a linguistic representation that can support careful analysis of Greek, Hebrew, Aramaic, and later supported languages without reducing language to a verse table, a one-word-to-one-gloss interlinear, or one supposedly authoritative parse.

This design defines the logical contract for representing:

- exact written forms and derived normalized views;
- graphemes, graphic tokens, morphemes, clitics, syntactic words, multiword expressions, phrases, clauses, sentences, and discourse units;
- lemmas, lexemes, roots, stems, derivations, and lexical senses;
- morphology and language-specific grammatical categories;
- dependency, constituency, functional, and distributional syntax;
- predicate-argument structure and semantic roles;
- referents, mentions, coreference, speakers, and addressees;
- lexical semantics, semantic domains, frames, modality, negation, scope, and event relations;
- discourse relations, information structure, pragmatics, genre, and register;
- accentuation, vocalization, cantillation, punctuation, prosodic structure, and pronunciation traditions;
- alternate, uncertain, competing, imported, projected, rule-based, human, and model-generated analyses;
- annotation provenance, rights, confidence, adjudication, operational selection, and benchmark eligibility.

DR-07 provides the linguistic substrate required by:

- DR-06's source-language construal and target-language constraint axes;
- DR-08's ancient-version and apparatus analysis;
- DR-09's scholarly claims and citation model;
- DR-13's multilingual architecture;
- DR-14's page and OCR analysis;
- DR-16's deterministic linguistic tools and scholar runtime;
- DR-17's corpus and sampling architecture;
- DR-18 and DR-19's training and preference designs;
- DR-20 through DR-22's benchmark and evaluation system.

It does not select a physical database, a final API transport, one universal linguistic theory, one preferred grammar for every question, or one annotation source as timeless truth. Those choices are integrated later under DR-16, DR-23, and DR-28.

## 2. Governing principle

> **The exact textual form is evidence; every segmentation, lemma, morphological parse, syntactic relation, semantic role, referent, discourse function, and linguistic interpretation is a versioned, provenance-bearing analysis of that evidence. No analytical layer may silently replace the written text or be presented as theory-neutral fact.**

The system must preserve the distinction:

```text
written realization
    → segmentation
    → formal linguistic analysis
    → functional interpretation
    → contextual meaning
    → translation implication
```

Each stage may contain:

- one accepted analysis for a bounded operational purpose;
- several compatible analyses;
- several competing analyses;
- partial analysis;
- uncertainty;
- no analysis.

The absence of an annotation does not establish the absence of a linguistic property.

## 3. Core commitments

DR-07 locks the following commitments.

### 3.1 The source text remains immutable

Linguistic annotation is stand-off and targets exact DR-05 textual-representation revisions and selectors. It does not rewrite the source text into a linguistically convenient form.

### 3.2 There is no universal `word` primitive

Different analytical tasks require different units. An orthographically printed unit, a clitic group, a morphological word, a syntactic word, and a lexeme occurrence may not have the same boundaries.

### 3.3 Formal shape is separate from interpreted function

Examples include:

- Greek tense-form versus temporal reference and viewpoint aspect;
- verbal voice-form versus semantic agency or affectedness;
- morphological case versus semantic role;
- Hebrew conjugation form versus temporal, aspectual, modal, or discourse function;
- grammatical gender versus referent gender;
- lexical sense versus English gloss;
- cantillation pattern versus one mandatory syntactic parse.

### 3.4 Source-native and project-normalized analyses coexist

Every imported annotation retains its source-native representation. A project-normalized projection may be added for cross-corpus querying, but it cannot erase distinctions or manufacture equivalence.

### 3.5 Competing analyses coexist

There is no scholarly last-write-wins rule. A bounded operational selection may choose an analysis for one tool, experiment, or display, but the alternatives and selection rationale remain available.

### 3.6 Ambiguity is data

An ambiguous form, parse, referent, sense, or discourse relation must not be forced into one label merely because a training pipeline expects one target.

### 3.7 Linguistic evidence remains edition- and passage-specific

An annotation attached to one edition or textual form is not automatically valid for another. Projection requires an explicit DR-04/DR-05/DR-06 mapping with scope, method, confidence, and provenance.

### 3.8 Linguistic analysis supports—not replaces—scholarly judgment

A morphology tag, syntax tree, semantic-domain number, or lexicon entry cannot by itself establish a translation, theology, historical reconstruction, or authorial intention.

## 4. What DR-07 is not

The linguistic representation is not:

- a universal grammar claiming one ontology perfectly describes every language;
- a one-token/one-lemma/one-gloss interlinear;
- a hidden normalization process that discards accents, vowels, cantillation, punctuation, orthography, or variant forms;
- an instruction to treat Universal Dependencies, MACULA, MorphGNT, BHSA, OSHB, TEI, or another resource as the project's unquestioned internal truth;
- a license to infer contextual meaning from roots, etymology, semantic domains, or dictionary glosses alone;
- a claim that every passage has one accepted syntactic parse;
- a requirement to materialize every possible annotation at the finest granularity;
- a custom foundation-model block or GPU kernel.

## 5. Logical architecture

The authoritative linguistic architecture has eight logical layers.

### 5.1 Text-view layer

Preserves exact source forms and explicitly generated derivative views.

### 5.2 Segmentation and unit layer

Represents overlapping, nested, discontinuous, and alternative units.

### 5.3 Lexical and morphological layer

Represents lemmas, lexemes, roots, stems, inflection, derivation, and formal feature bundles.

### 5.4 Syntactic layer

Represents dependency, constituency, functional, distributional, clause, coordination, discontinuity, and ellipsis analyses.

### 5.5 Semantic and referential layer

Represents senses, semantic domains, frames, predicates, arguments, roles, referents, coreference, modality, negation, and scope.

### 5.6 Discourse and pragmatic layer

Represents discourse relations, information structure, speaker/addressee structure, speech acts, register, genre, and rhetorical function.

### 5.7 Prosodic and reading-tradition layer

Represents accentuation, vocalization, cantillation, punctuation, oral phrasing, and pronunciation traditions without confusing them with the source's earliest recoverable state.

### 5.8 Annotation and adjudication layer

Represents schemes, agents, methods, provenance, confidence, disagreements, review, promotion, operational selection, and rights.

## 6. Core entities

### 6.1 `LanguageVarietyProfile`

Identifies the language variety relevant to an analysis.

Minimum fields include:

```text
language_variety_profile_id
language identity aliases
historical period or date range
dialect or regional variety
register or corpus variety
script and writing-system profile
orthographic conventions
annotation grammar or descriptive framework
known category cautions
source authorities
revision
```

Examples of distinct profiles may include:

- Classical Greek;
- Hellenistic literary Greek;
- documentary Koine;
- New Testament Greek;
- Masoretic Biblical Hebrew;
- epigraphic Hebrew;
- Biblical Aramaic;
- Jewish Palestinian Aramaic;
- Classical Syriac.

The exact language-code and locale system is completed in DR-13. DR-07 requires that ancient language, dialect, period, script, and register not be collapsed into one broad modern-language label.

### 6.2 `WritingSystemProfile`

Records:

- script;
- character repertoire;
- text direction;
- combining-mark behavior;
- vocalization or diacritic conventions;
- punctuation conventions;
- word-separation conventions;
- numeral conventions;
- Unicode version;
- normalization policy;
- known legacy encodings;
- transliteration adapters.

### 6.3 `TextViewRevision`

A versioned representation derived from an exact textual-representation revision.

Possible view types include:

```text
SOURCE_EXACT
EDITION_DISPLAY
UNICODE_NFC
UNICODE_NFD
SEARCH_NORMALIZED
CASE_NORMALIZED
DIACRITIC_INSENSITIVE
ACCENT_INSENSITIVE
VOWEL_INSENSITIVE
CONSONANTAL
PUNCTUATION_REDUCED
TRANSLITERATED
PHONOLOGICAL_RECONSTRUCTION
MODEL_INPUT_VIEW
```

Each derived view records:

```text
source revision
transformation activity
normalization standard and version
loss profile
reversibility
character or segment mapping
rights status
content hash
```

`NFKC` and `NFKD` must not be applied to an authoritative text view by default. Unicode warns that compatibility normalization can remove distinctions important to semantics and round-trip conversion.[^unicode-normalization]

### 6.4 `AnnotationSchemeRevision`

Identifies the exact annotation theory and label inventory.

It records:

```text
scheme name and version
language variety scope
layer scope
feature and relation definitions
annotation guidelines
source-native label namespace
project-normalized mappings
known limitations
responsible agents
rights
content hash
```

### 6.5 `LinguisticUnit`

A unit defined under an exact segmentation or analysis scheme.

It records:

```text
unit revision
unit type
target selector or component selectors
continuous or discontinuous status
parent or containment assertions
linear order assertions
language variety
analysis scheme
origin and review state
```

A unit may target source text directly or be an abstract analytical node with no overt surface realization.

### 6.6 `FeatureAssertion`

Assigns a linguistic feature or value to a unit.

It records:

```text
target unit
feature namespace and identity
source-native value
project-normalized value, if available
value status
method
evidence and counterevidence
confidence dimensions
responsible agent
annotation-set revision
review state
```

### 6.7 `RelationAssertion`

Relates two or more units.

Examples include:

```text
DEPENDENCY
CONSTITUENCY
HEADSHIP
COORDINATION
ELLIPSIS_RECOVERY
PREDICATE_ARGUMENT
SEMANTIC_ROLE
COREFERENCE
DISCOURSE_RELATION
SPEAKER_OF
ADDRESSEE_OF
TOPIC_OF
FOCUS_OF
LEXICAL_RELATION
DERIVATIONAL_RELATION
```

A material relation is an evidence-bearing DR-05 assertion, not an unlabeled edge.

### 6.8 `AnalysisBundleRevision`

Groups a coherent set of annotations that were created or imported together under one method and scheme.

It identifies:

- source revision;
- segmentation revision;
- included layers;
- annotation scheme revisions;
- generation or import activity;
- responsible agents;
- validation results;
- completeness scope;
- rights;
- content hash.

### 6.9 `AnalysisAdjudication`

Records review of competing annotations.

Possible dispositions include:

```text
ACCEPTED_FOR_DEFINED_PURPOSE
MULTIPLE_DEFENSIBLE
PREFERRED_BUT_CONTESTED
REJECTED
INSUFFICIENT_EVIDENCE
SUPERSEDED
NOT_REVIEWED
```

### 6.10 `LinguisticOperationalSelection`

Selects one or more analyses for a bounded purpose such as:

- runtime display;
- morphology lookup;
- training corpus materialization;
- benchmark gold;
- retrieval indexing;
- translation comparison.

It records scope, rationale, approver, evidence, alternatives, revision, and expiration or review condition. It does not erase competing analyses.

## 7. Exact text, Unicode, and offset policy

### 7.1 Source bytes and source Unicode remain recoverable

The project preserves the exact acquired source object under DR-05. A decoded Unicode representation must record the decoder, encoding, replacement behavior, and any unmappable bytes.

### 7.2 Canonical equivalence is handled explicitly

Ancient Greek and Hebrew frequently use combining marks. Canonically equivalent strings may have different code-point sequences. The project therefore creates explicit NFC and, where useful, NFD views rather than silently rewriting the authoritative source representation.[^unicode-normalization]

### 7.3 Extended grapheme clusters are the default user-facing offset unit

Human-visible character selection should normally use Unicode extended grapheme clusters because they remain stable across canonically equivalent forms and keep a base character with its combining marks.[^unicode-segmentation]

Every intra-text selector must declare its coordinate system, such as:

```text
BYTE_OFFSET
UNICODE_CODE_POINT
UNICODE_CODE_UNIT
EXTENDED_GRAPHEME_CLUSTER
SOURCE_GRAPHIC_TOKEN
LINGUISTIC_UNIT
```

A bare integer offset without its source revision, text view, and coordinate system is invalid.

### 7.4 Search-normalized forms are disposable indexes

Accent-insensitive, vowel-insensitive, punctuation-reduced, case-normalized, or compatibility-normalized forms are derived projections. They may support search, fuzzy matching, and OCR recovery. They cannot replace exact source forms in quotations, citations, training lineage, or benchmark gold.

### 7.5 Transformations must preserve maps

Where practical, every derived text view preserves a mapping back to source grapheme clusters or segments. A lossy view must declare which distinctions cannot be recovered.

## 8. There is no single universal word boundary

The unit model supports at least:

```text
CODE_POINT
GRAPHEME_CLUSTER
GRAPHIC_TOKEN
PUNCTUATION_TOKEN
ORTHOGRAPHIC_WORD
CLITIC_GROUP
MORPHEME
MORPHOLOGICAL_WORD
SYNTACTIC_WORD
LEXICAL_UNIT_OCCURRENCE
MULTIWORD_EXPRESSION
PHRASE
CLAUSE
SENTENCE
PARAGRAPH_OR_PERICOPE
DISCOURSE_UNIT
ABSTRACT_SYNTACTIC_NODE
```

### 8.1 Graphic and linguistic segmentation remain separate

A printed or source-delimited form may contain several morphemes or syntactic words. Several graphic tokens may form one lexical or multiword expression.

### 8.2 Units may overlap, nest, and be discontinuous

The architecture must support:

- prefixed and suffixed morphemes;
- clitic groups;
- discontinuous constituents;
- split lexical expressions;
- nested phrases;
- alternative sentence and clause boundaries;
- ellipsis nodes with no overt surface token.

Universal Dependencies likewise distinguishes raw tokens, syntactic words, multiword tokens, and empty nodes for ellipsis. It is supported as an interoperability projection, not adopted as the only internal model.[^ud-conllu]

### 8.3 Segmentation is an annotation

Whitespace, punctuation, maqaf, elision, crasis, clitic behavior, or edition markup may inform segmentation, but no one rule establishes universal linguistic units.

### 8.4 Competing segmentations remain possible

Two annotation projects may divide one source form differently. Both may be retained. Cross-project mapping records exact coverage and loss.

### 8.5 Model subword tokenization is a computational projection

A foundation model's tokenizer divides a text view into computational IDs for training and inference. Those IDs are not scholarly words, morphemes, lexemes, phrases, or semantic units.

A versioned `ModelTokenizationProjection` records:

```text
model and tokenizer revision
input text-view revision
model token IDs and byte or character spans
mapping to grapheme clusters and linguistic units
special-token policy
truncation or normalization behavior
content hash
```

Model-token boundaries may be useful for cost, attribution, quantization, error analysis, and training alignment. They may not be cited as linguistic evidence or used as stable linguistic identities. A new model tokenizer creates a new projection without changing DR-07 units.

## 9. Lemma, lexeme, root, stem, derivation, sense, and gloss

The following remain separate:

```text
surface form
normalized form
citation form
lemma assignment
lexeme identity
root analysis
stem analysis
derivational analysis
inflectional paradigm
contextual sense
semantic domain
gloss
translation equivalent
etymological assertion
```

### 9.1 Lemma is scheme-specific

A lemma is a canonical form under a named lexicon or annotation scheme. Different schemes may choose different citation forms or divide homographs differently.

### 9.2 Lexeme identity is an assertion

The project may define stable internal lexeme records, but occurrence-to-lexeme assignment and cross-lexicon equivalence remain versioned analyses.

### 9.3 Root and stem do not define contextual meaning

A root or derivational relationship may be relevant historical or morphological evidence. It cannot be used as a shortcut to the contextual sense of an occurrence.

### 9.4 A gloss is not a definition

A gloss is a language-specific display aid. It may be useful for search or explanation but cannot stand in for a contextual sense analysis.

### 9.5 Sense inventories are versioned and contestable

A `SenseAssignment` records:

```text
occurrence
sense inventory and revision
candidate senses
preferred sense, if any
method
evidence
confidence
review state
```

Semantic-domain assignments and sense assignments are related but not identical.

### 9.6 Strong-style numbers and external IDs are aliases

External lexical identifiers may be stored as namespaced aliases. They do not become universal lexeme or sense identities.

## 10. Morphological representation

### 10.1 Formal morphology is a feature graph, not an opaque code

Source-native codes are preserved, but the normalized layer exposes individual features and their definitions.

Core cross-language feature categories may include:

```text
part_of_speech
subtype
person
number
grammatical_gender
case
state
definiteness
degree
verb_form
conjugation_form
tense_form
aspect_form
mood_form
voice_form
polarity
pronominal_suffix
clitic_type
inflection_class
stem_or_binyan_form
```

Not every category applies to every language. `NOT_APPLICABLE`, `UNKNOWN`, `UNANNOTATED`, and `AMBIGUOUS` are distinct states.

### 10.2 Language-specific categories are first-class

A universal feature inventory may support comparison, but it may not erase language-specific distinctions. Every normalized feature can retain a source-native value and a mapping status:

```text
LOSSLESS
PARTIAL
APPROXIMATE
ONE_TO_MANY
UNMAPPED
DISPUTED
```

Universal Dependencies' separation of universal POS/features from language- or treebank-specific values is a useful adapter pattern, but DR-07 retains richer source-native schemes where required.[^ud-conllu]

### 10.3 Formal category and contextual interpretation are separate

The architecture stores separate assertions for:

```text
tense_form
viewpoint_aspect_interpretation
temporal_reference
modality
aktionsart_or_lexical_aspect
discourse_function
```

Similarly:

```text
voice_form
syntactic_voice_analysis
semantic_roles
agency_or_affectedness
```

and:

```text
morphological_case
syntactic_function
semantic_role
```

### 10.4 Inflection and derivation remain separate

A derived lexeme and an inflected occurrence are not represented by one undifferentiated morphology string.

### 10.5 Morphological ambiguity remains explicit

A token may have several candidate parses. Training and runtime tools must not convert an unresolved ambiguity into one certain tag without a recorded operational selection.

## 11. Greek language-profile requirements

The Greek profile must support at least the following distinctions.

### 11.1 Exact orthographic form

Preserve:

- letters and capitalization as represented by the edition;
- accents;
- breathing marks;
- diaeresis;
- iota subscript or adscript representation;
- apostrophe and elision marks;
- punctuation;
- editorial word separation;
- movable letters and orthographic variants;
- edition-specific normalization.

Accent- or breathing-insensitive views may be derived for search, but not substituted for exact text.

### 11.2 Period and dialect metadata

Classical, Hellenistic, documentary Koine, New Testament, patristic, and later Greek data must not be treated as one homogeneous variety merely because the script is Greek.

### 11.3 Segmentation phenomena

The model must be able to represent:

- proclitics and enclitics;
- crasis;
- elision;
- compound forms;
- multiword expressions;
- punctuation and clause-boundary disagreement;
- editorially joined or separated forms.

### 11.4 Formal morphology

The Greek profile must support, where applicable:

- part of speech and subtype;
- lemma and principal-part evidence;
- person, number, gender, case, degree;
- tense-form, aspect-form, mood-form, voice-form;
- finite, infinitive, participial, and other verbal forms;
- article, pronoun, particle, conjunction, and preposition subtypes;
- inflection class and irregularity;
- candidate parses.

MorphGNT illustrates a traditional word-level morphology representation, while MACULA Greek supplies richer syntax, word-sense, semantic-role, participant-reference, synonym, mapping, and adjunct annotations. Neither resource is treated as the final universal scheme.[^morphgnt][^macula-greek]

### 11.5 Tense and aspect discipline

The presence of an aorist, present, perfect, future, or other formal category does not by itself establish temporal reference, discourse prominence, or one English tense. Formal morphology and contextual interpretation must be represented separately.

### 11.6 Voice discipline

A morphological middle or passive form does not by itself determine semantic agency, reflexivity, affectedness, or target-language voice.

### 11.7 Case discipline

A genitive, dative, accusative, or nominative form does not by itself establish one semantic relation. Case, syntactic relation, semantic role, lexical governance, and discourse context remain distinct.

## 12. Hebrew language-profile requirements

### 12.1 Parallel written views

The Hebrew profile must support:

- exact edition form;
- consonantal form;
- vocalized form;
- cantillation-preserving form;
- punctuation and maqaf;
- qere and ketiv relationships;
- transliteration;
- derived search views.

The qere and ketiv must not be collapsed into one word. They are related textual and reading-tradition representations with explicit provenance.

### 12.2 Cantillation remains evidence, not a mandatory parse

Cantillation marks may encode musical, phonetic, and syntactic divisions and can be valuable evidence for clause and poetic structure. The project must preserve them and their hierarchy where available, while allowing syntactic analyses to agree or disagree explicitly.[^oshb-cantillation]

### 12.3 Morphological segmentation

The system must represent independently:

- conjunctions;
- prepositions;
- articles;
- interrogative or relative particles;
- lexical bases;
- pronominal suffixes;
- inflectional affixes;
- orthographic word or maqaf group;
- syntactic-word analysis.

### 12.4 Lexical morphology

The profile must distinguish:

- lemma;
- root;
- stem or binyan form;
- derived lexeme;
- inflected form;
- weak-root behavior;
- noun or adjective state;
- definiteness;
- person, number, and gender;
- pronominal suffixes;
- candidate parses.

### 12.5 Verbal-form discipline

Formal labels such as qatal, yiqtol, wayyiqtol, weqatal, imperative, infinitive, participle, cohortative, and jussive must remain separate from contextual claims about:

- tense;
- aspect;
- modality;
- sequence;
- discourse function;
- foregrounding or backgrounding.

The architecture must permit competing theories and passage-specific analyses.

### 12.6 Functional and distributional syntax

The system must support discontinuous functional units and continuous distributional units where an imported analysis makes that distinction. BHSA, for example, distinguishes functional and distributional sentence, clause, and phrase objects and supplies rich morphological and syntactic features. These concepts may be mapped without becoming the project's only syntax theory.[^bhsa]

### 12.7 Hebrew and Aramaic within one source

Language identity is occurrence- or segment-scoped. A biblical work containing both Hebrew and Aramaic cannot be assigned one undifferentiated language profile.

## 13. Aramaic and Syriac language-profile requirements

### 13.1 Dialect and period are mandatory

`Aramaic` alone is not a sufficient linguistic identity for serious analysis. The profile must identify the relevant dialect, period, corpus, and script where evidence permits.

Version-one priority is Biblical Aramaic where directly relevant to the Hebrew Bible and New Testament context. Later Syriac and other Aramaic varieties are added under their own profiles and review.

### 13.2 Script and vocalization are independent dimensions

The same or related language material may appear in different scripts, orthographies, and vocalization traditions. Script identity must not substitute for language-variety identity.

### 13.3 Morphological categories

The architecture must support language-profile-specific categories such as:

- absolute, construct, and emphatic states where applicable;
- stem or conjugation classes;
- person, number, and gender;
- suffixes and clitics;
- definiteness strategies;
- verbal forms and moods;
- dialect-specific orthography and morphology.

### 13.4 No automatic projection across dialects

A lemma, sense, parse, or translation inference from one Aramaic or Syriac variety cannot be transferred to another without an explicit mapping and uncertainty record.

## 14. Syntactic representation

### 14.1 Multiple syntax models are supported

The canonical logical contract supports:

```text
DEPENDENCY_GRAPH
ENHANCED_DEPENDENCY_GRAPH
CONSTITUENCY_TREE_OR_GRAPH
FUNCTIONAL_HIERARCHY
DISTRIBUTIONAL_HIERARCHY
CLAUSE_RELATION_GRAPH
CONSTRUCTION_ANALYSIS
VALENCY_ANALYSIS
```

No mandatory conversion may discard source distinctions.

### 14.2 Source-native syntax is preserved

Imported treebanks retain:

- original nodes;
- original labels;
- head rules;
- ellipsis policy;
- coordination policy;
- punctuation policy;
- sentence boundaries;
- version and guidelines.

A normalized projection may map comparable relations across schemes, with loss and uncertainty recorded.

### 14.3 Discontinuity is first-class

A phrase, clause, or construction may be discontinuous. The project must not force it into a false continuous span.

### 14.4 Ellipsis is analytical

An abstract node used to represent an elided predicate or argument does not become source text. It must be marked as non-overt and tied to the analysis that introduced it. UD enhanced syntax likewise uses empty nodes for some ellipsis analyses.[^ud-enhanced]

### 14.5 Coordination is explicit

The graph must distinguish conjuncts, coordinators, shared dependents, and alternative analyses. Coordination must not be flattened in a way that changes semantic-role or translation analysis.

### 14.6 Clause boundaries are disputable

Punctuation, cantillation, conjunctions, verbal forms, and discourse structure may provide evidence. A clause boundary remains an annotation under a named scheme.

### 14.7 Syntax does not equal semantics

A subject is not automatically an agent; an object is not automatically a patient; a genitive dependent is not automatically one semantic relation.

## 15. Lexical semantics

### 15.1 Occurrence sense is contextual

A contextual sense assignment must identify:

- occurrence;
- lexeme candidate;
- sense inventory and revision;
- candidate or selected sense;
- evidence;
- method;
- confidence;
- review state.

### 15.2 Semantic domains are not definitions

A semantic-domain label groups related concepts for a defined purpose. It does not establish the contextual meaning of every occurrence in the group.

### 15.3 Lexical relations are evidence-bearing

Relations may include:

```text
SYNONYM_OR_NEAR_SYNONYM
ANTONYM
HYPERNYM
HYPONYM
PART_WHOLE
DERIVATIONAL_RELATION
ETYMOLOGICAL_RELATION
COLLOCATION
CONSTRUCTIONAL_ASSOCIATION
```

Their scope, language variety, method, and source must be recorded.

### 15.4 Idiom and multiword meaning are first-class

An idiom or construction may have a meaning not compositionally recoverable from isolated glosses. The architecture must permit a sense or semantic analysis to target a multiword, discontinuous, or constructional unit.

### 15.5 Metaphor and figurative construal are analyses

The model may record literal source-domain, figurative interpretation, and competing analyses without treating one metaphor theory as universal truth.

## 16. Predicate-argument structure and semantic roles

A predicate analysis may target:

- a lexical verb;
- a nominal predicate;
- an adjective;
- a copular construction;
- a multiword expression;
- an inferred predicate under an explicit analysis.

A frame or predicate occurrence records:

```text
predicate unit
frame or valency inventory
arguments and adjuncts
semantic role labels
implicit arguments
role confidence
syntax mapping
sense mapping
review state
```

The project may support several role schemes. Source-native roles remain available, while a normalized role projection records loss or approximation.

MACULA Greek and Hebrew demonstrate the practical value of combining syntax, senses, semantic roles, and participant referents in one queryable corpus.[^macula-greek][^macula-hebrew]

## 17. Referents, mentions, and coreference

### 17.1 Mention and referent remain separate

A `Mention` is a textual or analytical expression. A `Referent` is the entity, group, event, place, object, proposition, or discourse participant it is analyzed as denoting.

### 17.2 Coreference is an assertion

A pronoun or implicit argument may have:

- one strongly supported antecedent;
- several possible antecedents;
- a split antecedent;
- an exophoric referent;
- an unknown referent.

The architecture must preserve alternatives.

### 17.3 Speaker and addressee are scoped

Direct speech, quoted speech, reported speech, letters, dialogues, and nested quotations require passage-scoped speaker and addressee assignments.

### 17.4 Entity identity remains provenance-bearing

A participant identifier must not silently equate two historical persons, places, groups, or divine referents. Identity and alias relations remain DR-05 assertions.

## 18. Semantics beyond lexical sense

The system may represent, under explicit schemes:

- event and state identity;
- temporal relations;
- modality;
- negation;
- quantification;
- scope;
- information source or evidentiality;
- aspectual interpretation;
- causation;
- comparison;
- conditionals;
- presupposition;
- entailment and contradiction candidates.

These layers are not required to be complete for every corpus. Absence must be distinguishable from negative analysis.

A scope or modality interpretation may be contested. It should not be baked irreversibly into a normalized sentence string.

## 19. Discourse and pragmatics

The architecture supports:

```text
discourse segment
discourse relation
topic
focus
contrast
information status
foreground/background analysis
cohesion link
participant continuity
speech act
rhetorical move
direct or indirect discourse
quotation boundary
register
genre
social setting
pragmatic force
```

### 19.1 Discourse structure is not paragraphing

Edition paragraphing and headings may be useful evidence but remain editorial presentation. A discourse analysis may agree or disagree.

### 19.2 Information structure is theory-bound

Topic, focus, emphasis, marked order, and prominence must identify the method or annotation scheme used.

### 19.3 Particles and conjunctions require contextual analysis

A lexicon or gloss list cannot by itself determine discourse function in an occurrence.

### 19.4 Genre and register are scoped

A genre label may apply to a work, section, speech, or embedded form. It must not be projected to every sentence without scope.

## 20. Accentuation, vocalization, cantillation, punctuation, and prosody

### 20.1 Written marks remain part of exact edition evidence

Accentuation, breathings, vowels, cantillation, punctuation, word division, and capitalization are preserved as represented by the identified edition or witness.

### 20.2 Reading traditions are separate from earliest textual claims

A vocalization, accentuation, or cantillation tradition may be ancient and linguistically important without being identical to an author's original written notation or pronunciation.

### 20.3 Prosodic analyses are versioned

Possible layers include:

- accentual unit;
- cantillation hierarchy;
- phonological phrase;
- pause or boundary;
- stress;
- syllabification;
- reconstructed pronunciation;
- liturgical reading tradition.

### 20.4 Punctuation is edition-specific

Punctuation can affect syntactic or interpretive analysis but cannot be treated as universal source evidence without identifying its origin.

### 20.5 Transliteration is a derived view

Every transliteration identifies:

- source view;
- scheme and revision;
- reversibility;
- loss;
- treatment of ambiguous characters and diacritics.

A transliteration is not the original text.

### 20.6 Textual uncertainty propagates into linguistic analysis

A linguistic annotation must identify whether its target consists of:

```text
DIRECTLY_READ_TEXT
EDITORIALLY_SUPPLIED_TEXT
RECONSTRUCTED_TEXT
NORMALIZED_TEXT
UNCERTAIN_READING
LACUNOSE_OR_DAMAGED_TEXT
ALTERNATIVE_READING
```

An analysis of editorially supplied or reconstructed wording cannot be presented with greater textual certainty than the target permits. If two reading candidates differ morphologically or syntactically, their analyses attach to the separate reading revisions rather than being merged into one synthetic form.

## 21. Annotation provenance and quality

Every annotation records its origin type.

```text
HUMAN_EXPERT
HUMAN_ANNOTATOR
HUMAN_ADJUDICATED
IMPORTED_SCHOLARLY_DATASET
RULE_BASED
ALGORITHMIC_PROJECTION
MODEL_GENERATED_CANDIDATE
HYBRID
UNKNOWN
```

### 21.1 Human editing does not erase machine origin

A model-generated or projected annotation remains traceable through later human correction.

### 21.2 Review states are explicit

```text
UNREVIEWED
AUTOMATICALLY_VALIDATED
HUMAN_REVIEWED
ADJUDICATED
ACCEPTED_FOR_DEFINED_PURPOSE
REJECTED
SUPERSEDED
HOLD
```

### 21.3 Completeness is scoped

An annotation bundle records whether it is complete for:

- a passage;
- a feature;
- a language profile;
- a corpus;
- an annotation layer.

Silence outside that scope is not negative evidence.

### 21.4 Agreement and disagreement are preserved

Where multiple annotators or datasets are available, the project may record:

- raw annotations;
- agreement metrics;
- disagreement types;
- adjudication;
- unresolved alternatives.

### 21.5 Confidence is multidimensional

Confidence may differ for:

- segmentation;
- morphology;
- lemma;
- syntax;
- sense;
- referent;
- discourse function;
- projection across editions.

One averaged confidence score is prohibited.

### 21.6 Rights remain layer-specific

The source text, morphology, syntax, senses, glosses, lexicon links, and semantic annotations may have different rights. DR-10 must enforce those differences through every derived artifact.

## 22. External scheme interoperability

The project uses adapters rather than adopting one external representation wholesale.

### 22.1 Universal Dependencies and CoNLL-U

Supported for:

- universal and language-specific POS/features;
- basic and enhanced dependencies;
- multiword tokens;
- empty nodes;
- sentence-level interchange.

Limitations and source-specific labels remain explicit.[^ud-conllu]

### 22.2 TEI

Supported for:

- source text structure;
- tokens and linguistic units;
- nested, discontinuous, and stand-off annotation;
- feature structures;
- manuscript and edition interoperability.

TEI explicitly permits linguistic annotation at word, token-group, nested, discontinuous, and other levels, which is compatible with DR-07's stand-off multilayer model.[^tei-corpora]

### 22.3 MACULA Greek and Hebrew

Supported through source-preserving adapters for:

- morphology;
- syntax trees;
- senses;
- semantic roles or frames;
- participant referents;
- mappings;
- TSV and XML/tree representations.

### 22.4 MorphGNT

Supported as a source-native Greek morphology and lemma layer, not as a universal word-study authority.

### 22.5 OSHB and BHSA

Supported through adapters that preserve:

- source text and morphology;
- lemmas;
- qere/ketiv where available;
- vocalization and cantillation;
- phrase, clause, and syntax representations;
- Aramaic occurrence identity;
- source-specific feature systems.

OSHB explicitly combines the Westminster Leningrad Codex with lemmas, morphology, and cantillation, while BHSA supplies a versioned Hebrew Bible database with rich linguistic annotations and related family modules.[^oshb][^bhsa]

### 22.6 Adapter mapping states

Every external-to-project mapping is labeled:

```text
LOSSLESS
LOSSLESS_WITH_ALIAS_CHANGE
PARTIAL
APPROXIMATE
ONE_TO_MANY
MANY_TO_ONE
UNMAPPED
DISPUTED
```

Round-trip export is promised only where a tested adapter declares it.

## 23. Deterministic linguistic-tool contract

DR-16 will define service transport and orchestration. DR-07 defines required logical operations.

Possible operations include:

```text
get_text_views
get_segmentation
get_units
get_lemma_candidates
get_morphology
get_syntax_analyses
get_lexical_senses
get_predicate_argument_structure
get_referents_and_coreference
get_discourse_analysis
get_prosodic_annotations
compare_linguistic_analyses
trace_annotation_provenance
project_analysis_between_editions
explain_linguistic_form
validate_word_study_claim
```

Every operation must return:

- exact source and view revision;
- selected annotation scheme or schemes;
- analysis values;
- alternatives;
- completeness scope;
- provenance;
- review state;
- confidence dimensions;
- warnings;
- rights status.

The model must not silently select an unreviewed parse when the tool reports a material ambiguity.

## 24. Required answer behavior

When a linguistic point materially affects an answer, the assistant should distinguish:

1. **Written form** — what exact edition or witness contains.
2. **Formal analysis** — morphology, segmentation, and syntax.
3. **Contextual interpretation** — sense, role, discourse, or pragmatics.
4. **Alternatives** — competing analyses and why they matter.
5. **Translation consequence** — which renderings each analysis supports or disfavors.
6. **Evidence and uncertainty** — source, scheme, review state, and remaining limits.

It should prefer wording such as:

- “This form is parsed as…”
- “The morphology permits…”
- “Under parse A…”
- “The syntax favors but does not require…”
- “The cantillation supports this division, although another syntactic analysis remains possible…”
- “This gloss is only a shorthand; in context…”

It should avoid:

- “The root literally means…”
- “The Greek tense proves…”
- “The Hebrew has no ambiguity…” without suitable evidence;
- “The word always means…”
- “The original punctuation says…” without edition provenance;
- “The semantic-domain number defines the meaning.”

## 25. Word-study fallacy guardrails

The runtime, training data, and benchmark must detect or penalize at least:

```text
ROOT_FALLACY
ETYMOLOGICAL_FALLACY
ILLEGITIMATE_TOTALITY_TRANSFER
GLOSS_AS_DEFINITION
ONE_SOURCE_WORD_ONE_TARGET_WORD
ONE_TARGET_WORD_ONE_SOURCE_WORD
SAME_LEMMA_SAME_SENSE
DIFFERENT_TRANSLATION_DIFFERENT_SOURCE_TEXT
MORPHOLOGY_DETERMINES_SEMANTIC_ROLE
TENSE_FORM_DETERMINES_TIME_REFERENCE
CASE_FORM_DETERMINES_ONE_RELATION
PUNCTUATION_IS_ORIGINAL
SEMANTIC_DOMAIN_IS_CONTEXTUAL_SENSE
LEXICON_ENTRY_SETTLES_PASSAGE
INTERLINEAR_ALIGNMENT_IS_EQUIVALENCE
MODERN_LANGUAGE_INTUITION_CONTROLS_ANCIENT_USAGE
```

A `validate_word_study_claim` result should identify the claim, the suspected fallacy, the evidence required, and a corrected formulation.

## 26. Training-data contract

### 26.1 Raw text and annotation are distinct channels

A model must not be unable to distinguish source text from lemma, gloss, morphology, parse, or commentary.

### 26.2 Annotation serialization is explicit

Every training example identifies:

- exact source text revision;
- language variety;
- annotation scheme;
- annotation origin;
- review state;
- rights lineage;
- graph snapshot;
- whether the target is unique, preferred, or one of several defensible analyses.

### 26.3 Ambiguous data are not forced into false single labels

Training strategies may include:

- multiple acceptable targets;
- probability or confidence targets where calibrated;
- contrastive analyses;
- abstention targets;
- explanation of evidence for alternatives;
- adjudication tasks.

### 26.4 Projection and model-generated labels remain labeled

Projected or synthetic annotations cannot silently enter gold training data.

### 26.5 Cross-edition leakage is controlled

A held-out passage, work, annotation source, or analysis may leak through aligned editions, translations, quotation, or projected annotation. DR-17 and DR-20 must cluster these relationships before splitting.

### 26.6 Linguistic objectives may be generative or auxiliary

The baseline may use generative tasks such as:

- produce or compare analyses;
- identify ambiguity;
- explain translation consequences;
- detect fallacies;
- select evidence;
- abstain.

DR-06's architecture-extension ladder governs any later auxiliary linguistic heads or specialist models.

## 27. Benchmark contract

DR-07 creates a dedicated **Linguistic Representation and Analysis** benchmark track.

### 27.1 Case families

The benchmark must include:

- exact-form and normalization distinctions;
- combining-mark and grapheme-cluster handling;
- alternate tokenizations;
- clitics and morpheme segmentation;
- lemma disagreements;
- morphological ambiguity;
- Greek tense-form versus temporal/aspectual interpretation;
- Greek voice-form versus semantic role;
- case versus semantic role;
- Hebrew prefix and suffix segmentation;
- qere/ketiv;
- Hebrew verbal form versus discourse interpretation;
- cantillation and competing clause divisions;
- dependency versus constituency analysis;
- discontinuous units;
- coordination and ellipsis;
- sense versus gloss;
- semantic-domain misuse;
- predicate and role analysis;
- pronoun or implicit-argument referent ambiguity;
- direct-speech speaker/addressee structure;
- discourse particles and information structure;
- punctuation and paragraphing provenance;
- cross-edition annotation projection;
- conflicting datasets;
- missing versus negative annotation;
- word-study fallacy correction;
- multilingual explanation of an ancient-language issue.

### 27.2 Evaluation modes

Cases may run in:

```text
CLOSED_BOOK
FIXED_LINGUISTIC_EVIDENCE
LIVE_LINGUISTIC_TOOLS
IMAGE_PLUS_TOOLS
CROSS_LANGUAGE_EXPLANATION
```

### 27.3 Metrics

Primary metrics include:

```text
exact_form_fidelity
segmentation_span_accuracy
lemma_accuracy_and_ambiguity_recall
morphological_feature_accuracy
formal_vs_functional_separation
syntax_relation_accuracy
alternative_parse_recall
lexical_sense_accuracy
semantic_role_accuracy
referent_and_coreference_accuracy
discourse_relation_accuracy
annotation_provenance_completeness
source_scheme_identification
cross_scheme_mapping_accuracy
uncertainty_and_abstention
word_study_fallacy_rate
translation_consequence_faithfulness
expert_rated_explanation_quality
```

Per-layer scores and hard failures remain visible. One aggregate score cannot hide a systematic lexical or syntactic error.

## 28. Validation invariants

The implementation must enforce at least these invariants.

1. Every annotation targets an exact source or text-view revision.
2. Every intra-text offset declares its coordinate system.
3. A derived text view records its transformation, loss, and source mapping.
4. The exact source form is never overwritten by a normalized form.
5. Compatibility normalization is never applied silently to authoritative text.
6. Every linguistic unit identifies its segmentation or analysis scheme.
7. A source graphic token is not automatically a morphological or syntactic word.
8. An abstract syntactic node is never quoted as surface text.
9. A lemma assignment identifies its scheme.
10. Root, lemma, sense, gloss, and translation equivalent cannot be stored as one field.
11. A formal morphological feature cannot silently stand for a contextual semantic interpretation.
12. A syntax relation identifies its source scheme and revision.
13. A semantic role cannot be inferred solely from a dependency label without an explicit analysis.
14. A referent link preserves uncertainty and alternatives.
15. Punctuation, accentuation, vocalization, and cantillation remain edition- or tradition-specific.
16. Cross-edition projection requires an explicit mapping and confidence record.
17. Imported source-native labels are retained even when normalized mappings exist.
18. `UNKNOWN`, `UNANNOTATED`, `NOT_APPLICABLE`, and negative analysis remain distinct.
19. Model-generated annotations remain candidates until explicit promotion.
20. Conflicting analyses cannot be silently overwritten.
21. An operational selection identifies purpose, approver, and alternatives.
22. Every training or benchmark record binds to exact annotation and graph revisions.
23. Annotation-layer rights remain separable from source-text rights.
24. A tool result reports completeness scope and cannot imply universal coverage from a partial dataset.
25. User-facing exact quotations use exact edition text rather than normalized linguistic views.
26. Model-token IDs cannot function as scholarly word, morpheme, lexeme, alignment, or citation identities.

## 29. Hard failures

The following are hard failures when material to the task:

- losing or corrupting Greek or Hebrew diacritics;
- anchoring an annotation to the wrong edition or textual form;
- treating one tokenization or parse as theory-neutral fact;
- collapsing qere and ketiv;
- quoting an abstract or normalized form as exact source text;
- treating a lemma, root, gloss, semantic domain, or etymology as contextual meaning by itself;
- inferring tense, aspect, temporal reference, modality, semantic role, or discourse function from one morphology code alone;
- forcing one-to-one token or alignment boundaries;
- treating missing annotation as negative evidence;
- silently transferring an analysis across textual forms or language varieties;
- hiding an analysis's source scheme or machine origin;
- presenting an unreviewed model parse as scholarly fact;
- allowing benchmark gold to depend on hidden or inaccessible annotation provenance;
- treating modern Greek, modern Hebrew, or one Aramaic dialect as an unquestioned substitute for the relevant ancient variety;
- using English glosses as the internal semantic representation;
- treating model subword tokens or their boundaries as linguistic words, morphemes, lexical units, or semantic evidence;
- losing alternate defensible analyses during data conversion;
- allowing a normalized cross-scheme mapping to erase a source-specific distinction;
- exposing restricted annotations or glosses through an open artifact.

## 30. Performance and materialization policy

DR-07 defines the logical representation, not a requirement to materialize every relation for every corpus.

The implementation may use:

- lazy annotation loading;
- layer-specific indexes;
- passage-scoped graph projections;
- precomputed operational selections;
- compact tabular projections;
- cached tool responses;
- vector or lexical indexes.

All such structures are derived and rebuildable from authoritative text, annotation, scheme, and selection revisions. They may not become untracked sources of truth.

## 31. Relationship to model architecture

DR-07 does not authorize a custom foundation-model topology.

The baseline supplies linguistic structure through:

- deterministic tools;
- structured evidence packets;
- source-aware retrieval;
- explicit training tasks;
- supervised and preference data;
- optional later auxiliary heads under DR-06's escalation ladder.

If persistent benchmark evidence shows that the model cannot represent competing parses, span relations, referents, or discourse structure despite suitable evidence and supervision, the architecture-extension process in DR-06 applies.

## 32. Sol implementation authority

### 32.1 Sol must implement the approved logical contract

Sol may not independently decide:

- to store one universal token or word layer;
- to overwrite exact text with normalized text;
- to collapse source-native schemes;
- to select one universal morphology or syntax theory;
- to remove competing analyses;
- to equate formal features with semantic interpretation;
- to omit annotation provenance or rights;
- to flatten Greek, Hebrew, Aramaic, or Syriac language profiles;
- to define benchmark gold from unreviewed model output.

### 32.2 Sol's design-neutral discretion

Sol may choose reversible local mechanics such as:

- module, class, and function decomposition;
- internal data structures that preserve all approved entities and invariants;
- index and cache implementation consistent with DR-28;
- validation code organization;
- source-adapter implementation;
- test fixtures;
- performance optimizations proven semantically equivalent;
- dependencies among approved or demonstrably equivalent options.

### 32.3 Escalation

Sol must stop with:

```text
BLOCKED_REQUIRES_DESIGN_REVIEW
```

if an imported scheme cannot be represented without material loss, if language-specific categories expose a missing contract, or if implementation requires changing the approved semantics.

## 33. Decisions DR-07 locks

Approval locks these decisions:

1. Linguistic annotation is stand-off over immutable textual revisions.
2. There is no universal `word` primitive.
3. Exact text, normalized views, transliterations, and phonological reconstructions remain separate.
4. Unicode normalization and offset systems are explicit and versioned.
5. Grapheme clusters are the default user-facing character-selection unit.
6. Segmentation is an annotation and may have alternatives.
7. Lemma, lexeme, root, stem, derivation, sense, domain, gloss, and translation equivalent remain separate.
8. Formal morphology and functional or semantic interpretation remain separate.
9. Source-native annotation schemes are retained alongside normalized projections.
10. Greek, Hebrew, Aramaic, and later language varieties receive explicit profiles and invariants.
11. Greek tense-form, voice-form, and case do not determine contextual interpretation by themselves.
12. Hebrew conjugation form does not determine tense, aspect, modality, or discourse function by itself.
13. Qere/ketiv, vocalization, cantillation, punctuation, and reading traditions remain explicit.
14. Dependency, constituency, functional, distributional, and other syntax schemes can coexist.
15. Discontinuity, coordination, ellipsis, and alternative clause boundaries are first-class.
16. Lexical sense, semantic roles, referents, coreference, discourse, and pragmatics are versioned analyses.
17. Competing annotations coexist; operational selections are bounded and auditable.
18. Missing annotation is not negative evidence.
19. Model-generated and projected annotations remain labeled candidates.
20. Runtime, training, benchmark, and publication artifacts bind to exact annotation revisions and rights.
21. Word-study fallacies are explicit training and benchmark targets.
22. External standards and datasets are adapters rather than internal truth.
23. Fine-grained annotation is materialized where useful rather than required uniformly.
24. No foundation-model or custom-kernel change is authorized by this design alone.
25. Model tokenizer projections are versioned computational artifacts and remain separate from the scholarly linguistic architecture.

## 34. Decisions intentionally deferred

DR-07 does not yet select:

- one default Greek syntax treebank;
- one default Hebrew syntax database;
- one default lexicon or sense inventory;
- one preferred theory of Greek aspect;
- one preferred theory of Biblical Hebrew verbal semantics;
- one universal semantic-role inventory;
- one discourse-analysis theory;
- exact internal URI or serialization syntax;
- physical database and index products;
- final API transport;
- exact runtime display format;
- benchmark case count;
- human-adjudication panel;
- annotation completeness targets for the full corpus;
- whether auxiliary linguistic heads will be trained;
- exact multilingual language codes and locale policy;
- which restricted annotation resources enter local-only experiments.

Those decisions belong to DR-08 through DR-10, DR-13, DR-16 through DR-23, DR-28, and the later approved experiment designs.

## 35. Approved statement

> **Biblical Scholar Lab will use a versioned, stand-off, multilingual linguistic representation anchored to immutable textual and text-view revisions. Exact written forms, normalized views, graphemes, tokens, morphemes, clitics, syntactic words, lexical units, phrases, clauses, abstract nodes, lemmas, lexemes, roots, morphology, syntax, senses, semantic roles, referents, discourse, prosody, and translation implications will remain distinct but interoperable layers. No universal word boundary, lemma, parse, tense interpretation, semantic role, discourse analysis, or external annotation scheme will be silently treated as theory-neutral fact. Greek, Hebrew, Aramaic, and later supported varieties will retain language-specific categories, orthography, vocalization, accentuation, cantillation, qere/ketiv, and formal-versus-functional distinctions. Competing analyses, uncertainty, source-native labels, provenance, rights, review state, and operational selections will remain inspectable. Deterministic tools, training examples, benchmark cases, and model explanations will bind to exact text, annotation, scheme, and graph revisions, while common word-study fallacies, hidden normalization, cross-edition projection, and model-generated pseudo-gold will be treated as explicit hard-failure risks.**

---

## References

[^unicode-normalization]: Unicode Consortium, *Unicode Standard Annex #15: Unicode Normalization Forms*. The specification defines NFC, NFD, NFKC, and NFKD and cautions that compatibility normalization can remove distinctions important to semantics and round-trip conversion: https://www.unicode.org/reports/tr15/

[^unicode-segmentation]: Unicode Consortium, *Unicode Standard Annex #29: Unicode Text Segmentation*. Extended grapheme clusters preserve base characters with combining marks and remain stable across canonically equivalent forms: https://unicode.org/reports/tr29/

[^ud-conllu]: Universal Dependencies, *CoNLL-U Format*. The format distinguishes raw tokens, syntactic words, multiword tokens, language-specific features, basic dependencies, enhanced dependencies, and empty nodes: https://universaldependencies.org/format.html

[^ud-enhanced]: Universal Dependencies, *Enhanced Dependencies*. The guidelines include explicit empty nodes for certain ellipsis analyses and enhanced relation structures: https://universaldependencies.org/u/overview/enhanced-syntax.html

[^tei-corpora]: TEI Consortium, *TEI P5 Guidelines — Language Corpora*. TEI supports linguistic annotation of tokens and groups that may be continuous, discontinuous, nested, or represented through feature structures and stand-off mechanisms: https://tei-c.org/release/doc/tei-p5-doc/en/html/CC.html

[^macula-greek]: Clear Bible, *MACULA Greek*. The repository supplies Greek New Testament text, syntax trees, morphology, word senses, semantic frames or roles, participant referents, synonyms, mappings, and several source representations: https://github.com/Clear-Bible/macula-greek

[^macula-hebrew]: Clear Bible, *MACULA Hebrew*. The repository supplies Hebrew Bible text, morphology, syntax, word senses, semantic roles, participant referents, and several source representations: https://github.com/Clear-Bible/macula-hebrew

[^morphgnt]: MorphGNT, *MorphGNT SBLGNT*. The dataset provides passage identity, part of speech, parsing codes, surface text, normalized word, and lemma under its own scheme: https://github.com/morphgnt/sblgnt

[^oshb]: Open Scriptures, *Open Scriptures Hebrew Bible*. OSHB combines the Westminster Leningrad Codex with lemmas, morphology, and cantillation-oriented resources: https://hb.openscriptures.org/HomeFiles/Oshb.html

[^oshb-cantillation]: Open Scriptures, *Hebrew Cantillation Marks*. The project describes cantillation as carrying musical, phonetic, and syntactic structure and as useful evidence for grammatical and poetic divisions: https://hb.openscriptures.org/HomeFiles/Accents.html

[^bhsa]: Eep Talstra Centre for Bible and Computer, *BHSA*. The versioned Text-Fabric dataset contains the Hebrew Bible with rich linguistic annotations and related modules for phonology, syntax trees, valence, parallels, extra-biblical texts, and Syriac corpora: https://github.com/ETCBC/bhsa
