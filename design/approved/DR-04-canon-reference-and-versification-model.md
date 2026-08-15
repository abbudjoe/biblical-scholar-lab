# DR-04 — Canon, Reference, and Versification Model

| Field | Value |
|---|---|
| Design ID | `DR-04` |
| Status | `APPROVED` |
| Approval date | 2026-08-15 |
| Project owner | Joseph Abbud |
| Designer and independent reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2; DR-03 |
| Implementation authority | GPT-5.6 Sol, under the approved design |

## 1. Purpose

Biblical Scholar Lab needs a reference system that can identify, compare, retrieve, cite, and display biblical passages without silently imposing one canon, one textual form, one language, one edition, or one chapter-and-verse system on every source.

This design defines the logical model for:

- canon profiles;
- literary works and materially distinct textual forms;
- editions and source artifacts;
- chapter, verse, subverse, superscription, and other reference coordinates;
- versification schemes;
- many-to-many mappings among schemes;
- multilingual book names and reference expressions;
- passage selections, ranges, and discontinuous mappings;
- exact, partial, disputed, and absent correspondences;
- edition-aware reference resolution;
- stable provenance across ingestion, tools, retrieval, notes, images, and citations.

The model is intended to support New Testament-centered version one while remaining extensible to the Hebrew Bible, Septuagint, deuterocanonical and Orthodox collections, Ethiopian and Syriac traditions, ancient versions, related Jewish and Christian literature, and nonbiblical ancient works.

## 2. Governing principle

> **A biblical reference is a coordinate within an identified reference scheme, not a universal identity for a piece of text. Canon membership, literary work, textual form, edition, reference scheme, displayed name, and textual content are separate concepts and must never be silently collapsed.**

The architecture must preserve both:

1. the source's own reference expression and local structure; and
2. any normalized or cross-tradition mapping produced by the system.

Normalization may add mappings. It may not erase the source-local identity.

## 3. Core separations

The following concepts are independent.

### 3.1 Canon profile is not textual content

A canon profile expresses how a particular tradition, jurisdiction, historical community, edition, liturgical context, or research corpus includes, classifies, groups, orders, or omits works.

It does not determine the wording of those works.

### 3.2 Work family is not textual form

A broad literary identity such as Esther, Daniel, Jeremiah, Psalms, Ezra, or the Gospel of Matthew may exist in one or more materially distinct textual forms.

Examples include:

- Hebrew Esther and longer Greek Esther;
- Hebrew/Aramaic Daniel, Old Greek Daniel, and Theodotionic Daniel;
- materially different orders and textual extent in forms of Jeremiah;
- Psalms collections with differing numbering or additional psalms;
- Ezra/Esdras configurations whose names and grouping vary by tradition.

### 3.3 Textual form is not edition

A textual form is a historically or structurally distinct form of a work. An edition is a specific editorial realization, transcription, translation, or publication of one or more textual forms.

Several editions may represent the same textual form differently.

### 3.4 Edition is not source artifact

An edition is the intellectual publication identity. A source artifact is the exact digital file, scan, database release, or physical-page representation ingested by the project.

Each artifact must have its own revision, rights, checksum, and provenance.

### 3.5 Reference scheme is not text segmentation

A chapter-and-verse system supplies addressable coordinates. It does not define the only legitimate segmentation of the text.

Paragraphs, clauses, poetic lines, sentences, discourse units, manuscript lines, and tokens may cross or subdivide verse boundaries.

### 3.6 Reference mapping is not textual equivalence

A mapping between two numbering systems does not prove that the mapped spans contain identical wording or even identical content.

Reference mapping answers:

> Where should a user look in the target scheme?

Textual alignment answers:

> Which source and target spans correspond, differ, overlap, or lack a counterpart?

Textual alignment is defined further in DR-05 and DR-06.

## 4. No universal canon

Biblical Scholar Lab will not define one internal canon as universally correct.

The repository may contain works and textual forms regardless of whether a selected tradition treats them as:

- canonical;
- deuterocanonical;
- anagignoskomena;
- ecclesiastical;
- appendicial;
- liturgical;
- disputed;
- noncanonical but historically relevant;
- excluded.

Those labels are not globally interchangeable. The model therefore records a profile-local classification string and structured inclusion behavior rather than converting every tradition into one universal hierarchy.

A canon profile is an evidence-bearing description, not a theological verdict.

## 5. Canon profiles

### 5.1 Canon-profile record

The normative logical record is:

```text
CanonProfile
  canon_profile_id
  revision_id
  display_name
  tradition_or_community
  jurisdiction_or_region
  historical_period
  profile_type
  authority_or_source
  source_citation
  default_language
  default_reference_scheme_id
  entries[]
  derived_from_profile_id?
  effective_date_range?
  notes
  content_hash
```

`profile_type` may include:

```text
ECCLESIAL
LITURGICAL
TRANSLATION_EDITION
HISTORICAL
ACADEMIC_CORPUS
USER_DEFINED
```

### 5.2 Canon-profile entries

Each entry records:

```text
CanonProfileEntry
  canon_profile_entry_id
  canon_profile_id
  canon_member_id
  membership_state
  local_classification
  order_path
  grouping_label?
  integration_expectation?
  accepted_textual_form_ids[]?
  local_names[]
  notes
  evidence_ids[]
```

`membership_state` is deliberately generic:

```text
INCLUDED
OPTIONAL
DISPUTED
APPENDIX
EXCLUDED
UNKNOWN
```

The `local_classification` field preserves tradition-specific language rather than translating every category into a project-created theological label.

### 5.3 Ordering

`order_path` must support nested groupings rather than one flat integer. A profile may group works under categories such as Torah, Prophets, Writings, Gospels, Pauline letters, Catholic letters, or other local arrangements.

Ordering is profile-specific and must not be inferred from a book code.

### 5.4 Historical and regional precision

The system must not use labels such as `Orthodox canon` or `Jewish canon` as though each described one timeless, globally uniform list.

Profiles should be as specific as evidence permits, including period, jurisdiction, edition, or community.

## 6. Work-family and textual-form model

### 6.1 Work family

A `WorkFamily` is a broad literary identity used to organize related textual forms.

```text
WorkFamily
  work_family_id
  preferred_display_label
  work_type
  component_ids[]
  external_aliases[]
  notes
```

The work-family record must not imply that all forms share identical content, order, authorship, or historical development.

### 6.2 Work component

A `WorkComponent` represents a separately identifiable literary component that may appear independently or be integrated into another work.

Examples may include:

- Susanna;
- Bel and the Dragon;
- Prayer of Azariah and the Song of the Three;
- Letter of Jeremiah;
- Psalm 151;
- prologues, epilogues, or other transmitted additions when they function as identifiable literary units.

```text
WorkComponent
  work_component_id
  parent_work_family_ids[]
  preferred_display_label
  component_type
  external_aliases[]
  notes
```

### 6.3 Textual form

A `TextualForm` represents a materially distinct form, order, extent, or language-tradition realization of a work or component.

```text
TextualForm
  textual_form_id
  work_family_id
  included_component_ids[]
  language_or_language_stage
  traditional_label
  content_extent_description
  ordering_description
  relationship_to_other_forms[]
  evidence_ids[]
  notes
```

A textual form is created only when the distinction is materially useful for textual history, reference mapping, translation analysis, or user interpretation. Minor edition-level variants do not automatically create a new textual form.

DR-05 defines the fuller textual-history relationship graph.

## 7. Edition and artifact identities

### 7.1 Edition

```text
Edition
  edition_id
  edition_revision_id
  title
  abbreviation
  language
  script
  edition_type
  publisher_or_editor
  publication_date
  represented_textual_form_ids[]
  canon_profile_id?
  default_reference_scheme_id
  alternate_reference_scheme_ids[]
  rights_record_id
  source_artifact_ids[]
  content_hash
```

`edition_type` may include:

```text
CRITICAL_EDITION
DIPLOMATIC_TRANSCRIPTION
MODERN_TRANSLATION
ANCIENT_TRANSLATION_EDITION
INTERLINEAR
STUDY_BIBLE
COMMENTARY_TEXT
MANUSCRIPT_TRANSCRIPTION
OTHER
```

### 7.2 Source artifact

```text
SourceArtifact
  source_artifact_id
  edition_revision_id
  artifact_type
  source_uri_or_local_locator
  retrieved_at
  raw_sha256
  media_type
  encoding
  rights_record_id
  ingestion_status
  provenance_record_id
```

The reference resolver must be able to return both edition identity and exact artifact provenance where available.

## 8. Reference schemes

### 8.1 Definition

A `ReferenceScheme` defines the legal address space and ordering for references in a specified textual or editorial context.

```text
ReferenceScheme
  reference_scheme_id
  revision_id
  display_name
  authority_or_source
  scheme_type
  applicable_work_or_form_ids[]
  book_alias_namespace_ids[]
  slot_inventory_id
  mapping_set_ids[]
  superscription_policy
  subverse_policy
  addition_integration_policy
  content_hash
```

`scheme_type` may include:

```text
BIBLE_CHAPTER_VERSE
LITURGICAL
MANUSCRIPT_FOLIO_LINE
CLASSICAL_BOOK_SECTION_LINE
PAGE_SECTION
TOKEN_SPAN
CUSTOM
```

The Bible-specific chapter-and-verse layer must sit on a generic locator architecture so the same system can cite Homer, Plato, Josephus, Philo, papyri, patristic texts, manuscripts, and modern scholarship without forcing them into Bible-style numbering.

### 8.2 Immutable revisions

Reference schemes are immutable once approved and used in a stored resolution. Corrections create a new revision.

Every resolved reference records the exact scheme revision and mapping revision used.

## 9. Reference slots are coordinates, not containers

### 9.1 Slot record

```text
ReferenceSlot
  reference_slot_id
  reference_scheme_revision_id
  work_or_form_scope_id
  chapter_label?
  verse_label?
  subverse_label?
  slot_kind
  sort_key
  display_label
  parent_slot_id?
  status
  notes
```

`slot_kind` may include:

```text
BOOK
CHAPTER
VERSE
SUBVERSE
SUPERSCRIPTION
SUBSCRIPTION
PROLOGUE
EPILOGUE
ADDITION
OTHER
```

Labels must be strings rather than positive integers only. This allows source-defined labels such as:

- verse parts;
- Psalm titles;
- nonstandard additions;
- source-local lettered or compound designations;
- schemes whose divisions are not purely numeric.

### 9.2 Verses as milestones

Verse references are modeled as addressable milestones or slots, not as the primary text-storage container.

This permits:

- paragraphs that cross verse boundaries;
- poetic lines within or across verses;
- partial-verse alignments;
- a verse number with no text in a particular edition;
- one verse slot bound to several noncontiguous text spans;
- several verse slots bound to one continuous span.

## 10. Text segments and slot bindings

### 10.1 Text segment

A `TextSegment` is a provenance-bearing span in a specific edition revision and normalized-text release.

```text
TextSegment
  text_segment_id
  edition_revision_id
  normalized_release_id
  structural_role
  start_locator
  end_locator
  text_hash
  parent_segment_id?
  source_artifact_locator
```

Segments may represent:

- paragraphs;
- clauses;
- sentences;
- poetic lines;
- manuscript lines;
- tokens;
- page regions;
- other source-preserved units.

### 10.2 Slot binding

A `SlotBinding` relates a reference slot to zero, one, or more edition-specific text segments.

```text
SlotBinding
  slot_binding_id
  reference_slot_id
  edition_revision_id
  text_segment_spans[]
  binding_status
  binding_basis
  evidence_ids[]
  review_status
  notes
```

`binding_status` may include:

```text
BOUND
PARTIALLY_BOUND
NO_TEXT_IN_EDITION
INTEGRATED_ELSEWHERE
UNRESOLVED
NOT_APPLICABLE
```

This distinction is essential for verses omitted from the running text, additions embedded elsewhere, Psalm superscriptions, and editions that preserve traditional numbering while lacking a corresponding textual reading.

## 11. Reference mappings

### 11.1 Mapping object

A `ReferenceMapping` maps one source selection to one or more target selections.

```text
ReferenceMapping
  reference_mapping_id
  source_scheme_revision_id
  source_slot_selection
  target_scheme_revision_id
  target_slot_selections[]
  cardinality
  coverage
  relation_type
  directionality
  confidence_status
  mapping_basis
  evidence_ids[]
  created_by
  review_status
  notes
  content_hash
```

### 11.2 Cardinality

```text
ONE_TO_ONE
ONE_TO_MANY
MANY_TO_ONE
MANY_TO_MANY
NO_TARGET
```

### 11.3 Coverage

```text
EXACT_REFERENCE_COVERAGE
PARTIAL_REFERENCE_COVERAGE
APPROXIMATE_REFERENCE_COVERAGE
NO_REFERENCE_COVERAGE
```

`EXACT_REFERENCE_COVERAGE` means the target coordinates are the accepted mapping of the source coordinate under the mapping authority. It does not assert identical wording.

### 11.4 Relation type

```text
SAME_CONTENT_DIFFERENT_NUMBERING
SPLIT
MERGED
REORDERED
TEXTUAL_ADDITION
TEXTUAL_OMISSION
INTEGRATED_COMPONENT
SEPARATED_COMPONENT
APPROXIMATE_PARALLEL
DISPUTED_MAPPING
UNMAPPED
```

### 11.5 Directionality

Mappings may be asymmetric. A source-to-target mapping does not automatically authorize a target-to-source inverse.

Round-trip equivalence may be asserted only for mapping classes that pass explicit validation.

### 11.6 Mapping basis

The mapping must state whether it comes from:

```text
PUBLISHED_STANDARD
EDITION_METADATA
SCHOLARLY_ALIGNMENT
EXPERT_REVIEW
PROJECT_MANUAL_MAPPING
ALGORITHMIC_CANDIDATE
UNKNOWN
```

Algorithmic candidates may support review and discovery. They may not silently become authoritative mappings.

## 12. Passage selections

A user or tool may select:

- one slot;
- a continuous range;
- a partial slot;
- several discontinuous ranges;
- several works;
- a source-local span without a chapter-and-verse label.

The canonical runtime representation is an ordered selection list:

```text
PassageSelection
  selection_id
  reference_scheme_revision_id
  ordered_items[]
  original_expression?
  resolution_context_id
  provenance
```

Each ordered item may be:

```text
SLOT
SLOT_RANGE
SEGMENT_SPAN
TOKEN_SPAN
```

A cross-scheme mapping that becomes discontinuous must remain a list. It must not be falsely rendered as one continuous target range.

## 13. Reference expressions

### 13.1 Preserve original input

The system stores the user's or source's original reference expression exactly as received.

```text
ReferenceExpression
  expression_id
  raw_expression
  source_language
  source_script
  locale
  source_artifact_id?
  surrounding_text?
  parser_version
```

### 13.2 Parsed representation

```text
ParsedReference
  expression_id
  parsed_candidates[]
  recognized_aliases[]
  numeral_system
  punctuation_convention
  parse_warnings[]
  parse_confidence
```

### 13.3 Resolved representation

```text
ResolvedReference
  resolved_reference_id
  expression_id
  selected_candidate
  canon_profile_revision_id?
  edition_revision_id?
  reference_scheme_revision_id
  passage_selection
  alternate_candidates[]
  alternate_numberings[]
  resolution_basis
  ambiguity_status
  warnings[]
  resolver_version
  resolved_at
```

The original expression and all material ambiguity must survive resolution.

## 14. Multilingual names and aliases

### 14.1 Localized-name record

```text
LocalizedReferenceName
  localized_name_id
  target_entity_id
  language
  script
  locale_or_region?
  canon_profile_revision_id?
  name_type
  value
  normalized_search_forms[]
  authority_or_source
  ambiguity_group_id?
```

`name_type` may include:

```text
FULL_TITLE
SHORT_TITLE
ABBREVIATION
TRADITIONAL_TITLE
TRANSLITERATION
ALTERNATE_TITLE
HISTORICAL_TITLE
```

### 14.2 Parsing requirements

The parser must support:

- localized book names;
- local abbreviations;
- Arabic, Roman, and other supported numeral conventions;
- localized punctuation and range conventions;
- translated and transliterated names;
- profile-specific naming such as Kingdoms, Samuel/Kings, Ezra/Esdras, and Apocalypse/Revelation;
- OCR-tolerant candidate generation without hiding uncertainty.

No English abbreviation may function as the universal internal identifier.

### 14.3 Rendering requirements

Reference rendering must be language-, locale-, style-, profile-, and scheme-aware.

A rendered string is a presentation layer. The underlying resolved-reference object remains language-neutral.

## 15. Resolution context and precedence

Every resolver call receives or constructs a `ReferenceContext`:

```text
ReferenceContext
  active_edition_revision_id?
  active_canon_profile_revision_id?
  active_reference_scheme_revision_id?
  interface_language
  locale
  user_profile_id?
  source_artifact_id?
  conversation_context_ids[]
  preferred_output_style?
```

Resolution precedence is:

1. an edition, profile, or scheme explicitly named in the expression;
2. the identified page, document, or active source artifact;
3. the currently selected edition in the product interface;
4. the user's saved reference profile;
5. the explicit session profile;
6. a locale-aware technical default, only when the result is not materially ambiguous.

The resolver should not ask a clarification question when all plausible profiles identify the same relevant content and the distinction is immaterial to the answer.

It must ask or display alternatives when the difference changes:

- the work;
- the textual form;
- the passage content;
- the chapter/verse mapping;
- the source evidence;
- the user's likely interpretation.

## 16. No invisible theological default

A product interface may offer a default translation or reference profile for usability, but it must:

- identify the selected edition and numbering system;
- allow the user to change it;
- disclose alternate numbering when material;
- never label the default simply as `the Bible` or `the original`;
- never treat the default profile's included works as the project's universal canon.

For an ordinary New Testament reference shared across supported profiles, the interface may remain unobtrusive while still preserving exact metadata in the evidence trace.

For a materially divergent reference, the user-facing answer should make the distinction visible, for example:

```text
Psalm 51 in common Hebrew-based English numbering
Psalm 50 in Septuagint/Vulgate numbering
```

The exact wording and style are defined later in DR-26.

## 17. Ambiguous, invalid, and impossible references

The resolver must distinguish:

```text
VALID_UNAMBIGUOUS
VALID_WITH_ALTERNATE_NUMBERING
AMBIGUOUS_BOOK_OR_FORM
AMBIGUOUS_SCHEME
PARTIALLY_VALID
INVALID_IN_SELECTED_SCHEME
VALID_IN_ANOTHER_SCHEME
UNRESOLVED
```

It must not silently coerce an invalid reference to the nearest verse.

When a likely correction is safe and obvious, it may offer the candidate while preserving the original input:

> This edition has no Psalm 23:10; did you mean Psalm 23:6 or another numbering system?

When an edition preserves a traditional verse number but lacks running text for it, the response should identify the slot and its status rather than report that the reference is universally nonexistent.

## 18. Ranges and ordering

### 18.1 Scheme-local range meaning

A range is expanded according to the source scheme's order, not a global canonical order.

### 18.2 Cross-work references

A continuous range may not silently cross work boundaries. Multi-work requests are represented as ordered lists.

### 18.3 Mapping reordered material

If source material is reordered in the target textual form or scheme, mapping a continuous source range may produce several target selections. The target must remain discontinuous unless the target scheme itself defines a valid continuous range with the intended coverage.

### 18.4 Partial verses

Partial-verse labels such as `a`, `b`, or `c` are scheme-specific. The project may use segment or token spans where the source edition does not define subverse labels.

## 19. Superscriptions, subscriptions, headings, and paratext

The architecture must distinguish:

- canonical or transmitted superscriptions;
- editorial section headings;
- chapter headings;
- running headers;
- verse numbers;
- footnotes;
- cross-references;
- study notes;
- subscriptions;
- introductions;
- user annotations.

A Psalm title may be part of the transmitted text and numbered differently across schemes. A modern section heading is normally editorial paratext. They may not share one generic `heading` identity.

DR-14 defines the visual/page region model; DR-05 defines source and textual-role provenance.

## 20. Additions, omissions, and integrated components

The model must represent at least these patterns without data loss:

- a component transmitted as a separate work in one profile and integrated into another;
- additions embedded inside a work in one edition and presented separately in another;
- a verse number retained as a reference slot but absent from the running text;
- content present without a counterpart in another textual form;
- material reordered between forms;
- several source verses represented as one target verse or the reverse;
- a profile including only part of a larger transmitted collection.

The system must not force an addition into a conventional chapter-and-verse coordinate if the source or edition does not support one. A source-local locator remains valid.

## 21. Edition-aware passage retrieval

A passage request is incomplete for exact quotation until an edition or deterministic edition-selection rule is established.

The passage tool must return at minimum:

```text
edition_revision_id
textual_form_id
canon_profile_revision_id?
reference_scheme_revision_id
resolved_reference
text_segments
source_artifact_provenance
rights_status
alternate_numberings[]
warnings[]
```

The assistant may discuss a general passage without first asking the user to choose an edition, but any exact quotation must identify the edition actually quoted.

## 22. Screenshot and page-image resolution

When the user provides a Bible or commentary page, the visual system should produce candidate:

- edition identity;
- language and script;
- canon profile;
- reference scheme;
- visible reference expressions;
- page-region roles;
- passage selections.

The reference resolver must treat image-derived references as probabilistic observations and verify them against deterministic edition data where available.

A low-confidence edition identification must not be converted into a confident citation.

## 23. Generic ancient-text locator architecture

Biblical Scholar Lab must not create a Bible-only reference subsystem that later has to be replaced for ancient context.

The generic locator layer must support references such as:

- Homeric book and line;
- Platonic dialogue and Stephanus page/section;
- Josephus work/book/section;
- Philo work/section;
- papyrus collection and line;
- manuscript folio/column/line;
- patristic work/book/chapter/section;
- modern page, section, figure, or table;
- token or character span.

Bible chapter-and-verse schemes are one family of locator schemes within this larger model.

## 24. Interoperability

The system should support adapters for established external identifiers and formats, subject to source-specific verification.

Initial interoperability targets should include:

- USFM/USX/USJ book identifiers and reference expressions;
- Paratext versification mappings where available and permitted;
- OSIS book and passage identifiers;
- Scripture Burrito metadata and ingredient identities;
- CTS or other established classical-text URNs where useful;
- source-dataset native IDs.

External identifiers are namespaced aliases, not the internal source of truth.

USFM's standard book identifier list itself distinguishes, among other cases, Hebrew and Greek Esther and Hebrew and Greek Daniel, and records tradition-dependent names and groupings. That demonstrates why the project must not equate one three-character code list with one universal canon.[^usfm-books]

USFM also defines a standard reference-string pattern for links within scripture projects; Biblical Scholar Lab should ingest and render compatible expressions while retaining richer internal mapping semantics.[^usfm-links]

USX is an XML representation closely associated with USFM and used for encoded scripture translations; an adapter should preserve its structural and linking information rather than flattening it into verse-only text.[^usx]

## 25. Identifier policy

### 25.1 Internal identifiers

Internal identifiers must be:

- globally unique within the project namespace;
- stable across display-name and localization changes;
- opaque enough not to encode disputed scholarly conclusions;
- typed by entity class;
- revision-aware where the object is mutable by correction;
- independent of chapter-and-verse labels;
- never recycled.

Examples of identifier classes are:

```text
work_family_id
work_component_id
textual_form_id
edition_id
edition_revision_id
canon_profile_id
canon_profile_revision_id
reference_scheme_id
reference_scheme_revision_id
reference_slot_id
text_segment_id
reference_mapping_id
```

DR-28 defines the final URI or serialization syntax.

### 25.2 External aliases

Every external alias records:

```text
namespace
namespace_version?
value
entity_id
source
status
```

One external code may map to different entities under different namespace versions or contexts. Ambiguity must be represented rather than overwritten.

## 26. Versioning and migration

### 26.1 Immutability

The following are immutable once referenced by a committed artifact, user note, evaluation case, or model-training manifest:

- edition revisions;
- canon-profile revisions;
- reference-scheme revisions;
- slot inventories;
- mapping-set revisions;
- normalized segmentation releases.

Corrections create new revisions.

### 26.2 Stored references

A stored note, citation, benchmark case, or training record must retain:

- original expression;
- resolved entity IDs;
- exact scheme/profile/edition revisions;
- resolver version;
- mapping revision;
- warnings and ambiguity state.

The system may offer re-resolution under a newer revision, but it may not silently rewrite the historical resolution.

### 26.3 Compatibility

Migration tooling must report:

- unchanged resolutions;
- changed target coordinates;
- newly ambiguous references;
- newly invalid references;
- mapping-confidence changes;
- edition or profile substitutions.

## 27. Normative logical operations

DR-16 defines exact runtime APIs. DR-04 locks the semantics of these operations:

```text
parse_reference(expression, context)
resolve_reference(parsed_reference, context)
map_reference(resolved_reference, target_scheme)
render_reference(resolved_reference, locale, style)
get_passage(resolved_reference, edition)
list_alternate_numberings(resolved_reference)
validate_reference(resolved_reference)
explain_reference_mapping(source, target)
```

### 27.1 Parsing

Parsing identifies possible syntactic interpretations without selecting a theological or canon profile.

### 27.2 Resolution

Resolution selects an entity and scheme using explicit context and returns ambiguity.

### 27.3 Mapping

Mapping returns structured target selections, relation types, coverage, confidence, and evidence. It does not return a bare string only.

### 27.4 Rendering

Rendering never changes the underlying resolution.

### 27.5 Passage retrieval

Passage retrieval is edition-specific and provenance-bearing.

## 28. Validation invariants

The implementation must enforce at least these invariants.

1. Every edition revision declares one default reference scheme.
2. Every reference slot is unique within a scheme revision.
3. Every slot binding identifies one edition revision and one slot.
4. Every resolved reference records an exact scheme revision.
5. Every exact quotation records an edition revision.
6. Every mapping records source and target scheme revisions.
7. A mapping may not claim textual equivalence merely from coordinate correspondence.
8. A canon profile may not be inferred from book order or book code alone.
9. A localized name may not become an internal identifier.
10. A source-local reference may not be discarded after normalization.
11. An absent verse slot and an invalid reference are different states.
12. Editorial paratext may not be bound as canonical text without explicit source-role evidence.
13. A discontinuous mapping may not be collapsed into a continuous range.
14. A many-to-one mapping may not be treated as invertibly one-to-one.
15. An algorithmic mapping candidate may not be promoted without the required review status.
16. No reference resolver may silently select among materially different textual forms.
17. Cross-language rendering must preserve the same resolved IDs.
18. Stored historical references may not be silently remapped after a scheme update.

## 29. User-facing behavior

The assistant should normally be helpful rather than pedantic.

It should not burden a user with canon metadata when no material difference exists. It should surface the metadata when it affects the answer.

Examples of appropriate behavior include:

- resolving an ordinary reference in the active edition without interruption;
- showing `Psalm 51 (50 in LXX/Vulgate numbering)` when relevant;
- distinguishing Greek Esther from Hebrew Esther;
- explaining that a requested verse is traditionally numbered but absent from the selected edition's running text;
- identifying that a page's numbering appears to follow a different scheme;
- asking a concise question when `1 Kingdoms` or `Esdras` is materially ambiguous in context;
- preserving the user's preferred tradition and language without treating it as universal.

## 30. Benchmark requirements

DR-20 and DR-21 must include a dedicated Canon and Reference track.

### 30.1 Case families

The benchmark should include:

- ordinary unambiguous New Testament references;
- localized book names and abbreviations;
- aliases shared by several works;
- Psalm-numbering differences;
- Psalm superscriptions;
- Esther and Daniel additions;
- Ezra/Esdras naming and grouping;
- Baruch and Letter of Jeremiah integration;
- Samuel/Kings/Kingdoms naming;
- merged and split verses;
- omitted traditional verse slots;
- reordered material;
- cross-chapter ranges;
- discontinuous selections;
- partial verses and token spans;
- invalid references;
- OCR-corrupted references from page images;
- cross-language input and output;
- edition-specific exact quotation;
- source-local references in ancient texts;
- migration between scheme revisions.

### 30.2 Metrics

```text
parse accuracy
resolution accuracy
material ambiguity detection
scheme-selection accuracy
mapping coverage accuracy
false-exactness rate
edition-identification accuracy
alternate-numbering recall
localized rendering accuracy
source-provenance completeness
invalid-reference correction precision
cross-language identity preservation
```

### 30.3 Evaluation modes

Cases should be run in:

- explicit-edition mode;
- active-session-profile mode;
- no-profile mode;
- image-derived-reference mode;
- cross-scheme mapping mode;
- multilingual rendering mode.

## 31. Hard failures

The following are disqualifying when they occur materially:

- silently resolving to the wrong work or textual form;
- conflating Hebrew and Greek Esther or Daniel;
- silently dropping additions or integrated components;
- treating chapter-and-verse numbering as universal textual identity;
- presenting a partial or disputed mapping as exact;
- converting a missing verse in one edition into a claim that the passage never exists in any tradition;
- citing an exact quotation without edition identity;
- mapping a modern study note or heading as canonical text;
- overwriting the source's original reference expression;
- silently changing a stored reference after a scheme revision;
- rendering the correct internal reference as the wrong localized book;
- collapsing a discontinuous target mapping into a misleading range;
- treating a canon profile as a universal theological judgment;
- hiding a materially relevant numbering difference from the user;
- allowing rights-restricted edition content to leak through a reference lookup.

## 32. Security, privacy, and rights boundaries

Reference metadata may be public even when the referenced text is restricted. Passage retrieval must enforce edition-level rights independently of reference resolution.

A valid reference does not authorize display, training, export, or redistribution of the underlying text.

User-created canon profiles, reading lists, and notes may reveal religious affiliation or personal study interests. Their privacy and retention are governed by DR-27.

## 33. Explicit non-goals

DR-04 does not:

- decide which canon is theologically correct;
- create one synthetic harmonized Bible;
- claim exact content equivalence from reference mapping;
- choose the product's default Bible translation;
- define full textual-history relationships among witnesses;
- define span-level translation alignment;
- choose physical database or index products;
- implement a production parser;
- guarantee complete version-one coverage of every historic canon or versification;
- replace source-specific scholarly judgment with automatic mapping.

## 34. Sol implementation boundary

Project design authority defines:

- the entity model;
- the distinction among canon, work, textual form, edition, scheme, slot, segment, and mapping;
- identifier semantics;
- profile and mapping taxonomies;
- resolution precedence;
- ambiguity behavior;
- versioning and migration requirements;
- validation invariants;
- benchmark obligations;
- hard failures;
- interoperability semantics.

Sol may implement the approved design and choose only reversible, local, design-neutral coding mechanics that preserve all approved semantics and externally visible contracts.

Sol may recommend an alternative representation, but it may not collapse or remove an approved entity or distinction. Any material change must stop with:

```text
BLOCKED_REQUIRES_DESIGN_REVIEW
```

Physical storage, indexing, final serialization syntax, service boundaries, and API transport are locked later in DR-16, DR-23, and DR-28 before production implementation.

## 35. Binding decisions

The following decisions are approved and binding:

1. Canon profile, work family, textual form, edition, artifact, reference scheme, slot, segment, and mapping are distinct entities.
2. No universal canon or versification is treated as project truth.
3. Canon profiles are versioned, evidence-bearing, historically and regionally specific where possible.
4. Textual forms represent materially distinct content or order, not minor edition variants.
5. Chapter and verse labels are coordinates, not text identity or storage containers.
6. Reference slots are bound separately to edition-specific text segments.
7. Missing text, invalid reference, integrated content, and absent counterpart are different states.
8. Reference mappings are many-to-many, directional, confidence-bearing, and evidence-bearing.
9. Reference mapping never implies identical wording or full textual equivalence.
10. Original reference expressions and source-local coordinates are preserved.
11. Internal IDs are stable, typed, language-neutral, and independent of display names and numbering.
12. External standards are interoperability aliases rather than the internal source of truth.
13. Reference parsing and rendering are multilingual and profile-aware.
14. Resolution uses explicit edition, page, user, and session context before any technical default.
15. Material ambiguity is exposed; immaterial ambiguity does not force needless clarification.
16. Exact quotation always identifies an edition.
17. Discontinuous and reordered mappings remain structurally visible.
18. Historical resolutions are immutable; new mapping revisions do not silently rewrite them.
19. Bible references use the same generic locator architecture as other ancient and scholarly texts.
20. Canon/reference behavior receives a dedicated benchmark track and hard-failure gates.

## 36. Decisions intentionally deferred

DR-04 does not yet select:

- the exact internal URI syntax;
- physical relational, graph, document, or object stores;
- search and index products;
- exact parsing library;
- final public API syntax;
- product-default translation or canon profile;
- complete initial inventory of profiles and schemes;
- final external-standard adapter list;
- numerical OCR-resolution thresholds;
- human-review workflow for mapping promotion;
- UI placement of alternate numbering and profile controls.

These are completed in DR-05, DR-14, DR-16, DR-20/21, DR-23, DR-26, and DR-28.

## 37. Approved statement

> **Biblical Scholar Lab will use a tradition-neutral, multilingual, edition-aware canon and reference architecture that treats canon profiles, literary works, textual forms, editions, reference schemes, address slots, textual segments, and cross-scheme mappings as separate entities. Chapter and verse labels will function as versioned coordinates rather than universal text identities. The system will preserve source-local references, expose materially relevant canon and numbering differences, support many-to-many and uncertain mappings, distinguish absent text from invalid references, identify exact quotation editions, and avoid silently imposing one canon or versification on every user or source. Established standards will be supported through versioned interoperability aliases, while the project's internal identities and provenance remain stable and language-neutral.**

## 38. Change control

This design may be amended only through a new owner-approved revision or supplement. Any proposed change to the entity separations, identifier semantics, canon-profile model, reference-scheme model, slot/segment distinction, mapping cardinality or confidence semantics, resolution precedence, ambiguity behavior, versioning guarantees, validation invariants, hard failures, or benchmark obligations must stop with:

```text
BLOCKED_REQUIRES_DESIGN_REVIEW
```

Sol may report implementation constraints and propose alternatives, but it may not silently collapse or weaken the approved reference architecture.

## 39. External reference anchors

These sources inform the interoperability and structural requirements. They do not replace the project's richer internal model or later source-by-source verification.

[^usfm-books]: United Bible Societies, *Unified Standard Format Markers — Book Identifiers*. The standard list records separate identifiers for Hebrew and Greek Esther and Daniel and notes tradition-dependent names and groupings: https://ubsicap.github.io/usfm/identification/books.html

[^usfm-links]: United Bible Societies, *Unified Standard Format Markers — Linking Attributes*. The standard defines a scripture-reference pattern for project links and uses standard book identifiers: https://ubsicap.github.io/usfm/usfm3.0.2/linking/index.html

[^usx]: United Bible Societies, *Unified Scripture XML Documentation*. USX is an XML format for encoded scripture translations whose structure and attributes are closely associated with USFM: https://ubsicap.github.io/usx/usx3.0/index.html
