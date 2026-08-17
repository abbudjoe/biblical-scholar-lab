# DR-09 — Scholarship and Citation Model

| Field | Value |
|---|---|
| Design ID | `DR-09` |
| Status | `APPROVED` |
| Approval date | 2026-08-15 |
| Project owner | Joseph Abbud |
| Designer and independent reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2; DR-03; DR-04; DR-05; DR-06; DR-07; DR-08 |
| Implementation authority | GPT-5.6 Sol, under the approved design |

## 1. Purpose

Biblical Scholar Lab needs modern scholarship to do more than populate a search box or decorate generated prose with plausible-looking citations.

The assistant must be able to determine:

- which scholarly object is being discussed;
- which version, edition, chapter, article, manifestation, or access copy was actually consulted;
- whether the source is current, corrected, retracted, superseded, translated, or only a preprint;
- who made a claim and what role each contributor played;
- what methodology, evidence, passage, language, tradition, or historical period the source addresses;
- whether a quoted sentence is exact, translated, OCR-derived, paraphrased, or encountered only through another source;
- whether a cited passage actually supports the associated claim;
- whether several sources are independent or inherit one argument, dataset, apparatus, translation, or bibliographic record;
- whether a statement about scholarly consensus is supported by a sufficiently broad and current landscape assessment;
- whether the system had access only to metadata, an abstract, a snippet, a partial preview, or the full text;
- what rights permit local retrieval, quotation, training, redistribution, or public benchmark use.

Modern biblical scholarship is unusually dependent on monographs, edited volumes, commentaries, chapters, reference works, dissertations, critical editions, journal articles, reviews, and scholarship in several languages. An article-only or DOI-only model would therefore be inadequate.

DR-09 defines the logical contract for:

- scholarly-work and publication-version identity;
- bibliographic metadata and persistent identifiers;
- contributors, affiliations, and roles;
- publication, review, correction, and retraction status;
- source acquisition and evidence proximity;
- exact quotations, translations, paraphrases, and secondary citations;
- scholarly claims, arguments, citations, and evidence spans;
- methodology, perspective, tradition, and coverage assertions;
- scholarly-landscape and consensus assessment;
- discovery, retrieval, reranking, source diversity, and evidence-packet construction;
- citation rendering, current-status verification, rights, provenance, and benchmark use.

DR-09 provides the scholarship layer required by:

- DR-02's claim taxonomy, source-fitness rules, consensus protocol, and evidence ledger;
- DR-03's sensitive-use and current-resource boundaries;
- DR-05's immutable provenance, argument, dependency, and graph-snapshot contracts;
- DR-06's translation-history evidence and translator-intent restraints;
- DR-08's apparatus, edition, versional, and evidential-distance contracts;
- DR-10's source-by-source rights and release architecture;
- DR-13's multilingual research behavior;
- DR-15 and DR-16's context composer, retrieval planner, tools, and answer rendering;
- DR-17 through DR-19's corpus, training, and preference policies;
- DR-20 through DR-22's benchmark, scoring, and evaluation harness;
- DR-28's integrated logical architecture and contract registry.

DR-09 does not select a final search engine, vector database, citation style, commercial database subscription, ranking model, publisher platform, or full-text parser. Those implementation and acquisition choices are made later within the contracts defined here.

## 2. Governing principle

> **A citation is a versioned relationship between a typed claim and identified evidence—not a decoration, authority token, popularity vote, or guarantee that a source supports the sentence beside it. Scholarly identity, publication status, access state, quotation provenance, methodological fit, and claim-level entailment must remain separately inspectable.**

The system must preserve this chain:

```text
scholarly work and version
    → exact manifestation or access artifact
    → source span or reported metadata
    → extracted or reported scholarly claim
    → project claim/evidence relationship
    → synthesized assessment
    → rendered citation and bibliography
```

No later layer may silently impersonate an earlier one.

## 3. Core commitments

### 3.1 Discovery is not evidence

A search result, embedding match, citation-graph edge, title, keyword, snippet, or generated summary may identify a source worth inspecting. It does not by itself support a substantive scholarly claim.

### 3.2 Bibliographic identity is assertion-based

DOIs, ISBNs, ISSNs, ORCID iDs, ROR IDs, repository handles, catalog identifiers, and local database keys are valuable external identifiers. They are not self-interpreting or universally complete. Every identity link and metadata value retains its source, timestamp, scope, and confidence.

### 3.3 Work, version, manifestation, and accessed bytes remain separate

A preprint, accepted manuscript, version of record, corrected version, translation, revised monograph edition, PDF, HTML rendering, print volume, repository copy, and exact downloaded file are related but not interchangeable.

### 3.4 Current publication status is time-sensitive

Correction, retraction, expression of concern, withdrawal, replacement, and version relationships may change after ingestion. Claims about current status require a timestamped status check rather than model memory alone.

### 3.5 Citation correctness has several dimensions

A citation can be bibliographically real yet still be wrong because:

- the wrong version was cited;
- the locator is incorrect;
- the quotation is inaccurate;
- the cited span does not entail the claim;
- the source is retracted or corrected in a way material to the claim;
- the source is only encountered secondarily;
- the citation is methodologically irrelevant;
- the answer silently translated or paraphrased it.

### 3.6 Peer review is one signal, not a truth certificate

Peer-review status and process should be represented when evidence exists. Peer review does not make every claim correct, and lack of known peer-review metadata does not prove that a work received none.

### 3.7 Scholarship is not one English-language journal corpus

The architecture must support monographs, chapters, commentaries, dictionaries, dissertations, reference works, editions, preprints, datasets, software, reviews, and scholarship in several languages and traditions.

### 3.8 Consensus is a separately evidenced claim

Retrieval counts, citation counts, translation counts, one handbook, one commentary series, or one denomination's literature cannot establish scholarly consensus.

### 3.9 Exact quotation is manifestation-specific

Page, column, paragraph, section, note, figure, table, and line locators belong to an identified manifestation or version. A page number from one edition cannot silently be transferred to another.

### 3.10 Machine output is not a source

A model-generated summary, translation, citation candidate, methodology label, or consensus estimate remains a candidate analysis with full provenance. It cannot become accepted scholarly evidence by repetition.

## 4. What DR-09 is not

The Modern Scholarship and Citation Model is not:

- a generic vector index over PDFs;
- a DOI lookup table;
- a universal source-quality score;
- a journal-impact or citation-count ranking system;
- an assumption that peer review guarantees correctness;
- an assumption that open access guarantees an open license;
- an assumption that publisher metadata is complete or error-free;
- an assumption that a preprint and version of record are textually identical;
- an instruction to ingest every accessible scholarly work into model weights;
- a license to quote copyrighted sources beyond applicable permissions;
- a mechanism for inferring an author's religion, ethnicity, ideology, or methodology from name or affiliation;
- a claim that one generated bibliography represents the whole field;
- a substitute for DR-02's scholarly judgment or DR-05's provenance and argument graph;
- a requirement that every answer contain many citations;
- a custom foundation-model architecture or compute kernel.

## 5. Logical architecture

The authoritative scholarship architecture has ten logical layers.

### 5.1 Work and publication identity layer

Represents conceptual works, citable components, publication versions, manifestations, access artifacts, and part-whole relationships.

### 5.2 Agent and contribution layer

Represents persons, organizations, contributor roles, affiliations, editors, translators, reviewers, and assertion provenance.

### 5.3 Bibliographic metadata and identifier layer

Represents titles, dates, publishers, containers, identifiers, language, volume, issue, edition, and conflicting metadata assertions.

### 5.4 Publication-process and status layer

Represents submission, acceptance, peer-review, publication, correction, retraction, expression-of-concern, withdrawal, and replacement events.

### 5.5 Content and access layer

Represents abstracts, full text, figures, tables, supplements, references, reviews, licenses, access copies, and exact acquired bytes.

### 5.6 Claim, argument, and evidence layer

Represents scholarly claims, methods, premises, evidence spans, counterevidence, conclusions, and project claim/evidence links.

### 5.7 Quotation and translation-provenance layer

Represents exact quotations, ellipses, bracketed changes, paraphrases, OCR, published translations, human translations, and model-generated translations.

### 5.8 Scholarly-landscape layer

Represents questions, search scope, representative sources, dependence, methodological distribution, dissent, time horizon, and consensus assessments.

### 5.9 Retrieval and operational-selection layer

Represents query plans, filters, ranking evidence, source diversity, selected evidence packets, and bounded operational choices.

### 5.10 Rendering and audit layer

Represents citation styles, locales, bibliographies, answer citations, evidence ledgers, status checks, and reproducible reports.

## 6. Core publication entities

### 6.1 `ScholarlyWork`

Represents an intellectual work or contribution that may appear in several versions or manifestations.

Examples include:

- a journal article;
- a monograph;
- a dissertation;
- a commentary volume;
- a dictionary entry;
- a critical essay;
- a dataset;
- a software release;
- a scholarly translation;
- a book review;
- a conference contribution.

Minimum fields include:

```text
scholarly_work_id
work_type
canonical_title_assertions
language_assertions
subject_and_passage_coverage_assertions
work_family_relationships
part_whole_relationships
creation_or_first_release_interval
rights_summary_projection
provenance
```

A work identity is not created solely by title similarity.

### 6.2 `CitableUnit`

Represents the exact intellectual unit that can be cited independently.

Examples include:

- a chapter in an edited volume;
- one dictionary entry;
- one article in a journal issue;
- one introduction or appendix;
- one volume in a commentary series;
- a review of another work;
- a correction or retraction notice.

A citation to a chapter must not silently resolve to the containing book when the chapter has its own authorship, title, pages, and argument.

### 6.3 `PublicationVersion`

Represents a content state of a work or citable unit.

Possible version classes include:

```text
DRAFT
PREPRINT
WORKING_PAPER
SUBMITTED_MANUSCRIPT
AUTHOR_ACCEPTED_MANUSCRIPT
ADVANCE_ONLINE_PUBLICATION
VERSION_OF_RECORD
CORRECTED_VERSION
UPDATED_VERSION
REVISED_EDITION
ABRIDGED_VERSION
EXPANDED_VERSION
TRANSLATED_VERSION
REPLACEMENT_VERSION
WITHDRAWN_VERSION
RETRACTED_VERSION
UNKNOWN
```

Version-class assignment is an assertion with source and evidence.

Crossref and DataCite provide useful relation types and versioning practices, but their deposited metadata remains source-attributed rather than automatically authoritative.

### 6.4 `PublicationManifestation`

Represents a format- or edition-specific realization such as:

```text
PRINT_EDITION
PUBLISHER_PDF
PUBLISHER_HTML
EPUB
REPOSITORY_PDF
AUTHOR_MANUSCRIPT_PDF
DATABASE_ENTRY
SCANNED_PRINT_COPY
OCR_DERIVATIVE
AUDIO_OR_VIDEO_RECORDING
```

Manifestations may differ in pagination, figures, footnotes, corrections, and layout.

### 6.5 `AccessArtifact`

Represents the exact acquired bytes or timestamped remote representation used by the project.

It records:

```text
access_artifact_id
source_uri_or_repository_locator
retrieved_at
content_hash
media_type
manifestation_relation
access_method
access_scope
license_or_terms_evidence
parser_or_ocr_activity
completeness
warnings
```

A URL without a captured state is not sufficient for a reproducible exact quotation.

### 6.6 `WorkRelationshipAssertion`

Represents relationships such as:

```text
IS_PREPRINT_OF
HAS_PREPRINT
IS_VERSION_OF
HAS_VERSION
IS_TRANSLATION_OF
HAS_TRANSLATION
IS_PART_OF
HAS_PART
IS_CORRECTION_OF
IS_RETRACTED_BY
IS_REPLACED_BY
IS_REVIEW_OF
HAS_REVIEW
IS_COMMENTARY_ON
IS_DATASET_FOR
USES_DATASET
USES_SOFTWARE
SUPPLEMENTS
IS_SUPPLEMENTED_BY
```

The relation retains direction, source, claimant, time, evidence, confidence, and review state.

## 7. Bibliographic metadata is a set of assertions

Fields such as these may disagree among publisher pages, Crossref, DataCite, library catalogs, repositories, author records, and imported files:

```text
title
subtitle
author order
editor
translator
publication date
online date
volume
issue
edition
publisher
container title
page range
language
abstract
license
identifier
```

The architecture therefore uses `BibliographicMetadataAssertion` rather than one silent last-write-wins record.

Each assertion records:

```text
field
value
normalized_projection
source
assertion_origin
retrieved_at
applicability_scope
confidence
review_state
supersedes_or_conflicts_with
```

An `OperationalBibliographicSelection` may select one value for citation rendering or retrieval. The alternative values and selection rationale remain inspectable.

Crossref states that its metadata comes primarily from member deposits, supplemented by internal enrichment and selected external sources. That is useful provenance and also a reason not to treat every field as directly observed from the publication.

## 8. Persistent identifiers and identity resolution

Supported external aliases should include, where applicable:

```text
DOI
ISBN
ISSN and ISSN-L
ORCID iD
ROR ID
DataCite DOI
repository handle
ARK
URN
PubMed or other domain identifiers
library catalog identifiers
publisher identifiers
local corpus identifiers
```

### 8.1 Identifier principles

- A DOI identifies a registered object, not an abstract timeless intellectual work.
- Different versions or language editions may have separate DOIs.
- An ISBN identifies an edition or format, not every edition of a book.
- An ISSN identifies a continuing resource, not an individual article.
- An ORCID iD identifies a person record, while the works and affiliations attached to it remain sourced assertions.
- A ROR ID identifies an organization record whose names, relationships, and status may evolve.
- An identifier's resolvability does not prove that all associated metadata are correct.
- Unauthenticated identifier strings are candidate links until verified where an authenticated workflow exists.

### 8.2 Identity-resolution rules

The system must not merge records solely because of:

- title similarity;
- author-name similarity;
- identical first page;
- one shared DOI-like string in OCR;
- one citation-graph match;
- a model's confidence.

Identity resolution should use several signals and preserve unresolved candidates.

## 9. Agents, affiliations, and contributions

### 9.1 `ScholarlyAgent`

Represents persons, organizations, editorial collectives, translation committees, and other responsible agents.

Names remain versioned and language-aware. A person is not identified solely by a name string.

### 9.2 `ContributionAssertion`

Represents roles such as:

```text
AUTHOR
EDITOR
TRANSLATOR
COMPILER
COMMENTATOR
REVIEWER
SERIES_EDITOR
DATA_CURATOR
SOFTWARE_DEVELOPER
METHODOLOGIST
RESEARCHER
PUBLISHER
```

CRediT may be supported as an external adapter for outputs that use it, but it does not replace humanities-specific roles such as editor, translator, commentator, or critical-text preparer.

### 9.3 ORCID provenance

An ORCID work or affiliation record remains an assertion whose source and assertion origin must be preserved. Self-asserted, publisher-asserted, repository-asserted, and institution-asserted records may carry different trust implications for different uses.

### 9.4 Affiliation assertions

Affiliations are time-scoped relationships. A current institution cannot be projected backward over every publication.

ROR is the preferred open organizational identifier where available, but department-level and historical structures may require project-local qualified entities.

### 9.5 No identity-to-method inference

The system must not infer a person's:

- denomination;
- religion;
- ethnicity;
- political ideology;
- methodology;
- trustworthiness;

from a name, country, institution, publisher, or other proxy.

Methodological or confessional labels require evidence from the work, author, publisher, or qualified scholarship and remain scoped assertions.

## 10. Source-type taxonomy

The system should distinguish at least:

```text
JOURNAL_ARTICLE
MONOGRAPH
EDITED_VOLUME
BOOK_CHAPTER
COMMENTARY
REFERENCE_WORK
DICTIONARY_OR_ENCYCLOPEDIA_ENTRY
CRITICAL_EDITION
GRAMMAR
LEXICON
HANDBOOK_OR_COMPANION
LITERATURE_REVIEW
SYSTEMATIC_REVIEW_OR_META_ANALYSIS
DISSERTATION_OR_THESIS
CONFERENCE_PAPER
PREPRINT_OR_WORKING_PAPER
BOOK_REVIEW
RESPONSE_OR_REPLY
EDITORIAL
CORRECTION_NOTICE
EXPRESSION_OF_CONCERN
RETRACTION_NOTICE
DATASET
SOFTWARE
PROTOCOL_OR_METHOD
INSTITUTIONAL_REPORT
CONFESSIONAL_OR_ECCLESIAL_DOCUMENT
SCHOLARLY_BLOG_OR_WEB_ESSAY
POPULAR_OR_PASTORAL_WORK
UNKNOWN
```

Source type affects source fitness but does not mechanically determine quality or truth.

Biblical scholarship often develops in monographs and chapters rather than journal articles alone. Retrieval and landscape assessment must therefore avoid journal-only bias.

## 11. Publication and post-publication status

### 11.1 `PublicationStatusAssertion`

Possible states include:

```text
ACTIVE_CURRENT
PREPRINT_NOT_FORMALLY_PUBLISHED
SUPERSEDED
CORRECTED
UPDATED
EXPRESSION_OF_CONCERN
RETRACTED
WITHDRAWN
REMOVED
REPLACED
STATUS_CONFLICT
UNKNOWN
```

Status is timestamped, source-attributed, and may be passage- or claim-relevant.

### 11.2 Status notices are separate citable works

A correction, expression of concern, retraction, replacement, or withdrawal notice has its own identity and relation to the affected work.

The original work is not deleted from the graph. It remains available for:

- research-history analysis;
- reception history;
- explaining the correction or retraction;
- auditing prior answers;
- identifying downstream dependence.

### 11.3 Current-status verification

Before materially relying on a modern source, the runtime should consult an approved current-status resolver when feasible.

Candidate status sources may include:

- publisher landing pages and notices;
- Crossmark and Crossref update metadata;
- Retraction Watch metadata integrated into Crossref;
- repository records;
- other approved domain systems.

Conflicts remain visible. Crossref or Crossmark metadata is not silently treated as complete simply because a DOI resolves.

### 11.4 Effect of status on use

- A corrected source should normally be cited in its corrected form.
- A retracted source cannot support a live substantive claim without an explicit reason and warning.
- An expression of concern requires visible caution but does not automatically establish that every claim is false.
- A superseded preprint should link to the version of record when available.
- A retracted work may still be appropriate evidence for reception, historiography, or the history of an error.

## 12. Peer review and editorial process

### 12.1 `PeerReviewProcessAssertion`

Peer-review claims should record, when known:

- whether review occurred;
- whether reviewers were internal or external;
- identity transparency;
- reviewer interaction;
- whether review reports were published;
- whether post-publication commenting occurred;
- source of the process description;
- journal-level versus item-level scope;
- exceptions for the content type;
- review date and status.

The NISO Peer Review Terminology standard should be supported as an adapter for journal-article workflows.

### 12.2 Article-level evidence overrides broad assumptions

A journal may use different processes for research articles, editorials, invited essays, reviews, special issues, or corrections. The assistant must not label an item peer reviewed solely because it appears in a peer-reviewed journal.

### 12.3 Books and humanities scholarship

Book and chapter review practices are often less uniformly encoded than journal peer review. Unknown review state remains `UNKNOWN`, not `NO_REVIEW`.

Editorial selection, dissertation examination, series review, publisher review, and external peer review may be represented separately.

### 12.4 Peer review does not settle claims

Peer review is a provenance and process signal. It does not replace analysis of the source's evidence and argument.

## 13. Content components and access states

The following components receive independent identities, access states, and rights:

```text
bibliographic metadata
abstract
keywords
full text
footnotes and endnotes
bibliography
figures
images
tables
appendices
supplementary files
data
software
peer-review reports
correction or retraction notices
publisher metadata
repository metadata
```

A work may have open metadata but copyrighted abstract and restricted full text. Crossref explicitly notes that almost all of its metadata is reusable while abstracts may remain copyrighted.

### 13.1 Preliminary access lanes

DR-10 will finalize rights policy, but DR-09 requires the logical distinction:

```text
METADATA_ONLY
ABSTRACT_ONLY
OPEN_FULL_TEXT
LICENSED_LOCAL_FULL_TEXT
TRANSIENT_AUTHORIZED_ACCESS
REVIEWED_EVIDENCE_PACKET_ONLY
USER_SUPPLIED_TRANSIENT
NO_CONTENT_ACCESS
EXCLUDED
```

### 13.2 Open access is not one rights state

A source may be:

- openly licensed;
- free to read without an open license;
- self-archived under a different version and license;
- available only through subscription;
- temporarily accessible;
- legally uploaded to a repository but not redistributable by the project.

Unpaywall may help locate lawful open copies. The project still records the exact location, version, license, and acquisition evidence.

## 14. Evidence-proximity and content-completeness classes

Every scholarly claim or quotation should indicate what the system actually accessed.

### 14.1 Evidence proximity

```text
PUBLISHER_VERSION_OF_RECORD_FULL_TEXT
PUBLISHER_CORRECTED_FULL_TEXT
AUTHOR_ACCEPTED_MANUSCRIPT_FULL_TEXT
PREPRINT_FULL_TEXT
REPOSITORY_FULL_TEXT
SCANNED_PRINT_COPY
OCR_DERIVATIVE
PUBLISHER_ABSTRACT
INDEXED_ABSTRACT
STRUCTURED_METADATA
REFERENCE_LIST_ONLY
SEARCH_SNIPPET_ONLY
SECONDARY_QUOTATION
TERTIARY_SUMMARY
MODEL_GENERATED_CANDIDATE
UNKNOWN
```

### 14.2 Content completeness

```text
COMPLETE
COMPLETE_EXCEPT_SUPPLEMENTS
PARTIAL_PREVIEW
ABSTRACT_ONLY
METADATA_ONLY
EXCERPT_ONLY
MISSING_PAGES
OCR_INCOMPLETE
UNKNOWN
```

Evidence proximity and completeness are not identical to reliability. They record the system's actual evidential basis.

## 15. Structured full-text and locators

### 15.1 Source structure

Where available, the project should preserve:

- headings and hierarchy;
- paragraphs;
- footnotes and endnotes;
- block quotations;
- tables and figures;
- captions;
- equations;
- bibliographic references;
- page breaks;
- XML or HTML identifiers;
- language spans;
- accessibility descriptions.

JATS 1.4 may be supported for journal content; TEI, BITS, publisher XML, EPUB, PDF structure, and other formats may require adapters.

### 15.2 Locators are manifestation-specific

Supported locators may include:

```text
page and page range
volume and page
chapter
section and subsection
paragraph
footnote or endnote
figure or table
appendix
entry headword
column
line
XML or HTML element ID
PDF page plus region
character or token span
```

A locator records its coordinate system and manifestation revision.

### 15.3 Stable and display locators coexist

A stable structured selector may support reproducibility while a human-facing page or section citation supports usability. The system should preserve both where available.

## 16. Scholarly claims and arguments

### 16.1 `ScholarlyClaim`

Represents a claim made by a source, not merely a topic assigned to the source.

Minimum fields include:

```text
scholarly_claim_id
claim_text_or_normalized_proposition
claim_type_from_DR_02
claimant
source_version
source_span
discourse_status
methodology_assertions
epistemic_language_in_source
premise_and_conclusion_relations
counterclaims
extraction_origin
review_state
```

### 16.2 Claim extraction remains interpretive

A model-extracted claim is initially:

```text
MODEL_GENERATED_CANDIDATE
```

It cannot be treated as the author's settled position until verified against the source and discourse context.

### 16.3 Source-level labels do not replace claim-level analysis

A book may contain several methods, cite contrary views, change its conclusion, or represent other scholars. One source-wide label cannot be projected onto every sentence.

## 17. Citation relations and claim/evidence links remain separate

### 17.1 `BibliographicCitationRelation`

Represents that one citable unit cites another.

It records:

```text
citing_version
cited_identity_or_unresolved_reference
reference-list span
in-text citation spans
citation context
resolution confidence
citation-function candidate
provenance
```

A citation edge does not establish agreement, endorsement, or independent corroboration.

### 17.2 `ClaimEvidenceLink`

Represents how identified evidence bears on a project or source claim.

Possible roles include:

```text
DIRECTLY_SUPPORTS
PARTIALLY_SUPPORTS
INDIRECTLY_SUPPORTS
QUALIFIES
LIMITS
CONTRADICTS
PROVIDES_COUNTEREXAMPLE
DEFINES_METHOD
SUPPLIES_PRIMARY_EVIDENCE
SUPPLIES_BACKGROUND
REPORTS_RECEPTION
REPORTS_ANOTHER_SOURCE
MOTIVATES_FURTHER_SEARCH
NO_SUPPORT
RELATION_UNKNOWN
```

The link records exact evidence spans, method, scope, strength, counterevidence, reviewer, and current-status checks.

### 17.3 Entailment is claim-specific

The same source may directly support one sentence and fail to support the next. Citation verification must therefore operate at claim level rather than answer level alone.

## 18. Citation-correctness dimensions

Every citation associated with an answer claim should be evaluable along separate dimensions:

```text
SOURCE_IDENTITY_CORRECTNESS
VERSION_CORRECTNESS
CONTRIBUTOR_CORRECTNESS
BIBLIOGRAPHIC_METADATA_CORRECTNESS
LOCATOR_CORRECTNESS
QUOTATION_CORRECTNESS
CLAIM_ENTAILMENT
SCOPE_COMPATIBILITY
METHODOLOGICAL_FIT
CURRENT_STATUS_AWARENESS
SECONDARY_CITATION_DISCLOSURE
TRANSLATION_PROVENANCE
RIGHTS_COMPLIANCE
```

Possible states include:

```text
VERIFIED
PARTIALLY_VERIFIED
CONFLICTING_EVIDENCE
UNVERIFIED
INCORRECT
NOT_APPLICABLE
```

There is no single citation-confidence number that hides a failed entailment or fabricated locator.

## 19. Quotation, paraphrase, and translation provenance

### 19.1 `QuotationRecord`

An exact quotation records:

```text
quoted_text
source_version
manifestation
source_span
language
normalization applied
ellipses
bracketed changes
emphasis changes
OCR origin
verification status
rights lane
```

### 19.2 Direct quotation rules

- Quotation marks require wording verified against an accessible source.
- Material omissions or insertions must be visible.
- Silent modernization, spelling change, or punctuation change is prohibited unless the transformation is disclosed.
- A quotation from a scan or OCR should identify its basis and review state.
- A quote cannot be reconstructed from model memory when the exact source is available through a tool.

### 19.3 Paraphrases

Paraphrases do not use quotation marks. They still require source and entailment verification when used as evidence.

### 19.4 Translated quotations

The record distinguishes:

```text
PUBLISHED_TRANSLATION
AUTHOR_PROVIDED_TRANSLATION
PROJECT_HUMAN_TRANSLATION
MODEL_GENERATED_TRANSLATION
TRANSLATION_SOURCE_UNKNOWN
```

If the assistant translates a source quotation, the answer should say so. Its English wording cannot be attributed to the original scholar as though the scholar wrote those exact words.

### 19.5 Parallel presentation

When useful and legally permitted, the interface may show:

```text
source-language quotation
project or published translation
citation and locator
translation provenance
```

## 20. Secondary citation and indirect access

If Source B quotes or reports Source A and the project has not inspected Source A, the assistant must use an explicit indirect-citation relation.

It may say:

> Source A is quoted in Source B as saying…

It may not imply that Source A was directly verified.

When the original is accessible, the resolver should prefer direct inspection. When it is not, the answer must preserve the evidential distance and avoid detailed claims that exceed Source B's report.

Bibliographies copied from another work are not automatically verified citations.

## 21. Dependence, citation networks, and source independence

Several scholarly sources may depend on:

- one critical apparatus;
- one edition;
- one dataset;
- one translation;
- one earlier monograph;
- one unpublished dissertation;
- one publisher abstract;
- one bibliographic record;
- one review article;
- one model-generated summary.

DR-05 dependence relations apply to modern scholarship.

The system should distinguish:

```text
DIRECT_ARGUMENT_DEPENDENCE
SHARED_PRIMARY_EVIDENCE
SHARED_DATASET
SHARED_APPARATUS
SHARED_TRANSLATION
RESTATEMENT_OR_QUOTATION
REVIEW_SYNTHESIS_DEPENDENCE
POSSIBLY_DEPENDENT
INDEPENDENT_WITHIN_DEFINED_SCOPE
UNKNOWN
```

Citation count and number of retrieved documents cannot be used as independent-vote counts.

## 22. Methodology, perspective, and tradition assertions

### 22.1 Methodology profiles

Possible methods include, among others:

```text
TEXTUAL_CRITICISM
PHILOLOGY
TRANSLATION_STUDIES
HISTORICAL_CRITICISM
SOURCE_OR_REDACTION_CRITICISM
FORM_CRITICISM
LITERARY_OR_NARRATIVE_CRITICISM
RHETORICAL_CRITICISM
SOCIAL_SCIENTIFIC_ANALYSIS
ARCHAEOLOGY
RECEPTION_HISTORY
INTERTEXTUALITY
CANONICAL_INTERPRETATION
THEOLOGICAL_INTERPRETATION
CONFESSIONAL_EXEGESIS
FEMINIST_INTERPRETATION
POSTCOLONIAL_INTERPRETATION
DISABILITY_INTERPRETATION
OTHER_EXPLICIT_METHOD
MIXED
UNKNOWN
```

The taxonomy is extensible and not exhaustive.

### 22.2 Method claims require evidence

A methodology assertion records:

- whether the source names the method;
- whether the method is inferred from explicit procedures;
- the passage or section to which it applies;
- reviewer and confidence;
- competing labels.

### 22.3 Perspective and tradition remain scoped

A source may explicitly work within a Jewish, Catholic, Orthodox, Reformed, Wesleyan, Lutheran, Pentecostal, secular historical, or other framework. The system may represent that framework when relevant and evidenced.

It must not infer a person's private faith or reduce every argument to presumed identity.

### 22.4 Methodology is not a quality ranking

Different methods may answer different questions. A theological interpretation cannot substitute for manuscript evidence, while a textual apparatus cannot by itself answer a canonical-theological question.

## 23. Passage, language, period, and subject coverage

`ScholarlyCoverageAssertion` records, when known:

```text
biblical works and passages
ancient works and locators
languages and textual traditions
historical periods
geographic regions
methods
topics
source types
traditions or perspectives
coverage completeness
origin and review state
```

Coverage may be derived from:

- structured metadata;
- tables of contents;
- indexes;
- cited passages;
- human annotation;
- model candidates.

Model-derived coverage remains a candidate until accepted for a defined purpose.

## 24. Source fitness is multidimensional

No universal authority score is authorized.

For a given claim, source fitness may include:

```text
claim_type_fit
primary_evidence_proximity
methodological_fit
passage_or_topic_relevance
publication_version_status
currentness
peer_review_transparency
argument_and_evidence_visibility
exact_locator_availability
independence
language_and_tradition_coverage
rights_and_access_suitability
expertise_relevance
```

A historical commentary can be highly fit for reception history and poorly fit for current linguistic consensus. A recent article can be relevant yet speculative. A critical edition can be authoritative for its own editorial text and still not settle a disputed historical reconstruction.

## 25. Current scholarship and freshness

### 25.1 Currentness is question-dependent

A source's age is not automatically a weakness. Older works may be primary to reception history, foundational, or still persuasive.

However, claims such as these require a current evidence horizon:

- “Most scholars now hold…”
- “The current critical consensus is…”
- “Recent research has overturned…”
- “This article has not been corrected or retracted.”

### 25.2 Freshness record

A current-scholarship operation records:

```text
query_or_question
search_sources
search_date
metadata_snapshot
status_check_date
inclusion_and_exclusion criteria
language coverage
publication-date horizon
known access limitations
```

### 25.3 Cached scholarship

Cached metadata and full text may be used, but current-status-sensitive questions require refresh according to an approved policy.

## 26. Scholarly-landscape and consensus assessment

### 26.1 `LandscapeAssessment`

Represents a bounded claim about the state of scholarship.

Minimum fields include:

```text
landscape_assessment_id
question and claim scope
discipline and subfield
time horizon
language and geographic scope
methodological scope
search strategy
sources searched
inclusion and exclusion criteria
representative source set
dissenting and minority source set
dependence analysis
access limitations
consensus label from DR-02
rationale
reviewer or panel
expiration or review date
graph and corpus snapshot
```

### 26.2 Consensus labels

DR-02's labels remain binding:

```text
BROAD_CONSENSUS
MAJORITY_VIEW
SIGNIFICANT_MINORITY
ACTIVE_DISPUTE_NO_CLEAR_MAJORITY
NICHE_OR_SPECULATIVE
HISTORICALLY_INFLUENTIAL
LARGELY_ABANDONED
CONSENSUS_NOT_ESTABLISHED
```

### 26.3 Prohibited shortcuts

A consensus label cannot be generated solely from:

- citation counts;
- search-result counts;
- model priors;
- number of translations;
- one handbook;
- one denominational corpus;
- one language's publications;
- one review article;
- public-domain availability.

### 26.4 Landscape assessments expire

A landscape assessment is a dated research product. It may be reused within its scope until its review date, but it is not timeless truth.

## 27. Discovery and retrieval architecture contract

DR-09 defines the logical retrieval stages without selecting the final backend.

### 27.1 Query classification

The system first identifies:

- claim type;
- passage or work;
- method;
- date horizon;
- languages;
- user-requested tradition or perspective;
- source types;
- currentness requirement;
- access and privacy constraints.

### 27.2 Candidate discovery

Candidate discovery may use:

- exact bibliographic lookup;
- canonical passage and subject indexes;
- lexical search;
- semantic search;
- citation and relation graphs;
- author and identifier search;
- bibliography expansion;
- handbook and review discovery;
- multilingual query expansion.

Discovery results are candidates, not evidence.

### 27.3 Mandatory filters

Filters may include:

```text
publication status
version class
source type
methodology
passage or subject coverage
language
publication date
rights and access lane
peer-review state
tradition or perspective
private/public corpus boundary
```

Missing metadata is not treated as a negative match unless the query explicitly requires verified metadata.

### 27.4 Reranking objectives

Reranking should consider:

- claim-type fitness;
- exact passage relevance;
- methodological fit;
- source status;
- exact evidence-span availability;
- source independence;
- source diversity;
- currentness;
- user language;
- cost and latency.

No ranking model may turn popularity alone into authority.

### 27.5 Evidence packet construction

A selected evidence packet should include:

```text
source and version identity
manifestation and access artifact
status and last status check
relevant source spans
bibliographic metadata
source type and methodology
quotation and translation provenance
claim/evidence role
rights lane
known limitations
alternative and counterevidence candidates
```

The packet is immutable for a recorded evaluation or answer trace.

### 27.6 Source diversity

The retrieval planner should detect when its evidence set is concentrated in one:

- method;
- tradition;
- language;
- publisher;
- commentary family;
- dataset;
- apparatus;
- revision lineage.

Diversity does not require equal weighting of unequal evidence. It requires visibility into coverage and dependence.

## 28. Metadata and content sources

DR-09 supports versioned adapters for systems such as:

- Crossref;
- DataCite;
- ORCID;
- ROR;
- DOAJ;
- Unpaywall;
- publisher and repository metadata;
- JATS and related full-text structures;
- library and domain catalogs;
- project-local curated bibliographies.

These are interoperability and discovery sources, not the project's universal truth.

### 28.1 Crossref

Crossref is valuable for DOI metadata, relationships, references, ORCID/ROR connections, licenses, updates, Crossmark, and Retraction Watch enrichment. The source and update dates of each field remain preserved.

### 28.2 DataCite

DataCite is valuable for datasets, software, translations, versions, supplements, and related identifiers. Its relation and version metadata remain source assertions.

### 28.3 ORCID

ORCID supports researcher identity and sourced work or affiliation assertions. An ORCID record's source and assertion origin remain essential trust markers.

### 28.4 ROR

ROR provides open organization identifiers and metadata. Historical affiliations and department-level structures may still require qualified project assertions.

### 28.5 DOAJ and peer-review transparency

DOAJ can support open-journal discovery and journal-policy metadata. Journal-level policy does not automatically prove article-level review or license.

### 28.6 Unpaywall

Unpaywall can support discovery of lawful open copies and version locations. The project still verifies exact version, license, and content state.

### 28.7 JATS

JATS 1.4 can preserve structured journal content and metadata. It is an adapter, not a requirement that all scholarship be converted losslessly into one article-centric format.

## 29. Multilingual scholarship

Each source and evidence record separately identifies:

```text
source language
bibliographic-title language
abstract language
quotation language
published translation language
question language
answer language
model-generated display-translation language
```

### 29.1 Original-language metadata remains available

Translated titles and abstracts support discovery, but they do not replace original metadata.

### 29.2 Hidden pivoting is prohibited

If the assistant searches or reasons through an English translation of German, French, Spanish, Italian, Dutch, Hebrew, Greek, or another scholarly source, the pivot and its provenance should be visible where material.

### 29.3 Cross-language citation

The answer may summarize a source in the user's language. Direct quotations retain their original language or identify the published or generated translation.

### 29.4 Language support and landscape claims

A landscape assessment with only English-language evidence cannot silently claim global scholarly consensus.

## 30. User-provided and private scholarship

A user may upload or connect:

- articles;
- books;
- scans;
- notes;
- private bibliographies;
- licensed database exports;
- unpublished drafts.

These sources may support the user's private analysis when authorized. They do not automatically enter:

- the public corpus;
- model training;
- the public benchmark;
- another user's retrieval index;
- a distributable checkpoint.

User-provided metadata and assertions remain evidence to verify rather than automatic truth.

## 31. Deterministic scholarship and citation tools

DR-09 requires logical operations including:

```text
resolve_scholarly_source
get_bibliographic_metadata
get_publication_version_graph
get_current_publication_status
get_peer_review_assertions
get_contributors_and_affiliations
get_source_access_artifacts
get_source_structure
get_source_span
verify_quotation
trace_secondary_citation
search_scholarship
retrieve_scholarly_evidence
compare_scholarly_positions
get_methodology_and_perspective_assertions
build_landscape_assessment
verify_claim_citation_entailment
render_citation
render_bibliography
trace_citation_provenance
```

Every result should report:

- exact source and version;
- metadata sources;
- status and last check;
- access state;
- evidence proximity;
- source span;
- rights lane;
- alternatives and conflicts;
- provenance and review state;
- warnings.

The language model may not fabricate a source when resolution fails.

## 32. Citation rendering

### 32.1 Structured metadata is authoritative

Human-facing citation strings are generated from structured bibliographic records and locators. A hand-edited formatted citation is not the canonical source record.

### 32.2 Citation Style Language

CSL should be supported as the primary open citation-formatting adapter unless a later review identifies a material gap.

Every rendered citation records:

```text
CSL style identity and revision
locale
bibliographic record revision
locator
rendering engine and version
output hash
```

The eventual default style—potentially SBL, Chicago, or another style—is intentionally deferred.

### 32.3 Style cannot hide evidential distinctions

A citation style may omit version or access details for presentation. The evidence ledger and inspectable source view must still preserve them.

## 33. Runtime answer contract

### 33.1 Source claims use resolved evidence

The assistant should cite only sources returned by the approved scholarship tools or explicitly supplied and verified in the current evidence packet.

### 33.2 Claim-level citation placement

Citations should be placed close enough to the associated claim that support can be audited.

### 33.3 No citation dumping

A long list of loosely relevant sources does not substitute for precise claim support.

### 33.4 Current-status warning

When a source is corrected, retracted, under concern, superseded, or only a preprint, that status should be visible when material.

### 33.5 Evidence limitations

The assistant should say when it has only:

- metadata;
- an abstract;
- a preview;
- a secondary report;
- an inaccessible source;
- a model-generated candidate translation.

### 33.6 Answer modes

Brief, Study, and Scholarly modes may render different citation density, but none may fabricate or weaken source provenance.

## 34. Training policy

### 34.1 Modern scholarship is primarily a retrieval and behavior resource

The default role of modern scholarship is:

- retrieval-grounded evidence;
- source-aware SFT;
- citation and tool-use training;
- methodology and disagreement examples;
- benchmark evidence;
- reception and landscape analysis.

Indiscriminate continued pretraining on modern scholarship is not authorized by DR-09.

### 34.2 Training eligibility is component-specific

Only content authorized under DR-10 may enter weights. Metadata, abstracts, full text, figures, tables, references, and reviews may have different rights.

### 34.3 Candidate training tasks

Training may include:

- source identity resolution;
- work/version/manifestation discrimination;
- preprint versus version-of-record classification;
- correction and retraction awareness;
- claim extraction and verification;
- claim/evidence role classification;
- citation-entailment judgments;
- quotation verification;
- secondary-citation disclosure;
- methodology and source-fitness explanation;
- consensus restraint;
- multilingual source synthesis;
- refusal to invent missing sources;
- correction after contradictory evidence;
- citation-style rendering from structured metadata.

### 34.4 Model-generated scholarship remains candidate data

Synthetic claims, summaries, citations, translations, landscape labels, and preference pairs require source verification and review before promotion.

### 34.5 Citation verifier models are not sole judges

A model-based entailment scorer may triage cases. Primary benchmark truth and high-risk promotion decisions require deterministic verification, source inspection, or qualified human review.

## 35. Benchmark track

DR-09 creates a dedicated **Modern Scholarship and Citation** benchmark track.

Required case families include:

- exact source resolution from partial or conflicting metadata;
- article versus chapter versus containing book;
- preprint versus accepted manuscript versus version of record;
- corrected, retracted, replaced, withdrawn, or concerned sources;
- bibliographically real but claim-irrelevant citations;
- incorrect locators;
- accurate and inaccurate quotations;
- quoted source versus secondary quotation;
- abstract-only overreach;
- search-snippet overreach;
- peer-review-state uncertainty;
- journal-level policy versus article-level exception;
- methodology and source-fitness matching;
- historical commentary versus current scholarship;
- repeated dependent sources versus independent evidence;
- consensus and minority-position assessment;
- monograph- and chapter-centered scholarship;
- multilingual quotations and model-generated translations;
- rights-constrained source use;
- public versus private evidence;
- user-provided source correction;
- current-status refresh;
- citation-style rendering without metadata loss.

Primary metrics include:

```text
source_identity_accuracy
version_identity_accuracy
bibliographic_metadata_accuracy
publication_status_accuracy
peer_review_assertion_accuracy
locator_accuracy
quotation_accuracy
claim_citation_entailment
secondary_citation_disclosure
translation_provenance_accuracy
methodological_fit
source_independence_accuracy
consensus_label_accuracy
abstract_overreach_rate
fabricated_citation_rate
retracted_source_misuse_rate
rights_lane_compliance
multilingual_citation_faithfulness
expert_rated_scholarly_landscape_faithfulness
```

No aggregate score may hide citation fabrication, unsupported quotation, retracted-source misuse, or restricted-content leakage.

## 36. Validation invariants

The implementation must enforce at least these invariants.

1. Every exact quotation identifies an exact publication version and manifestation or access artifact.
2. Every page locator identifies the manifestation whose pagination it uses.
3. Every answer citation resolves to a structured source record or an explicitly unresolved user-supplied source.
4. Every claim/evidence link identifies the exact claim and evidence scope.
5. A bibliographic citation edge cannot be interpreted automatically as agreement or support.
6. A search result or snippet cannot support a substantive claim without further evidence.
7. Metadata-only access cannot be reported as full-text inspection.
8. Abstract-only access cannot support claims absent from the abstract.
9. Secondary citation cannot be presented as direct inspection.
10. A preprint cannot be presented as the version of record without an explicit relationship and status.
11. Correction, retraction, concern, withdrawal, and replacement notices remain separate citable works.
12. A retracted work cannot support a live substantive claim without explicit justification and warning.
13. Peer-review state cannot be inferred solely from venue identity.
14. Unknown peer-review state cannot be converted into `not peer reviewed`.
15. ORCID, ROR, DOI, ISBN, ISSN, and other identifiers remain external aliases with provenance.
16. Methodology or tradition cannot be inferred from author name or affiliation alone.
17. Citation counts and retrieval counts cannot establish consensus.
18. Dependent works cannot be counted as independent evidence without a scoped independence assertion.
19. A model-generated translation cannot be presented as a source-authored quotation.
20. A formatted citation string cannot replace the structured bibliographic record.
21. Restricted or private full text cannot leak into public evidence packets or model weights.
22. Historical answers remain bound to the publication-status and metadata snapshot actually used.
23. Conflicting bibliographic or status assertions remain inspectable.
24. Every landscape assessment records its scope, search horizon, limitations, and review date.
25. Every benchmark and experiment binds to exact scholarship-corpus and metadata snapshots.

## 37. Hard failures

The following are hard failures when they occur materially:

- fabricating a source, author, title, DOI, ISBN, journal, publisher, or page;
- attaching a real source to a claim it does not support;
- quoting words absent from the cited source;
- hiding that a quotation was translated or encountered secondarily;
- citing a preprint as though it were the final version;
- relying on a materially retracted source without disclosure;
- ignoring a correction that changes the cited claim;
- presenting search snippets or metadata as full-text evidence;
- inferring peer review from venue alone;
- representing historical commentary as current consensus;
- claiming consensus from source counts or citation counts;
- treating several dependent sources as independent confirmation;
- inferring denomination or methodology from identity proxies;
- citing the containing book instead of the specific chapter when the distinction matters;
- transferring page locators across editions;
- presenting a model-generated translation as a published quotation;
- leaking restricted scholarship into weights, public reports, or another user's workspace;
- failing to disclose that current publication status could not be checked;
- allowing citation formatting to erase the version or source identity required for audit.

## 38. Sol implementation boundary

Sol may determine reversible, design-neutral mechanics such as:

- module, class, and function organization;
- local caching strategy within the approved freshness and provenance contract;
- adapter implementation details;
- parser organization;
- equivalent query-planning optimizations;
- test fixture construction;
- internal names that do not change public contracts.

Sol may not independently change:

- the work/version/manifestation/access-artifact separation;
- bibliographic assertion semantics;
- publication-status model;
- citation-correctness dimensions;
- quotation and translation-provenance rules;
- claim/evidence relation semantics;
- secondary-citation disclosure;
- peer-review restraints;
- consensus protocol;
- source-independence requirements;
- multilingual provenance;
- rights boundaries;
- benchmark hard failures.

Implementation must stop with:

```text
BLOCKED_REQUIRES_DESIGN_REVIEW
```

if a source or format exposes a materially missing contract or if a proposed simplification would alter scholarly evidence semantics.

## 39. Explicit non-goals

DR-09 does not:

- select a final scholarly search engine;
- select a final vector or lexical index;
- purchase or authorize a database subscription;
- select a default citation style;
- define final Crossref, DataCite, ORCID, ROR, DOAJ, Unpaywall, library, or publisher adapters;
- guarantee complete bibliographic coverage;
- authorize scraping contrary to terms or access controls;
- define one universal source-quality score;
- infer private author characteristics;
- define final ranking weights;
- determine exact scholarship-corpus inclusion;
- establish a final human-review panel;
- authorize modern-scholarship CPT;
- authorize restricted full-text training;
- select physical storage products or API transport;
- define the final user-interface bibliography view;
- replace expert review of difficult scholarship or consensus claims.

## 40. Decisions DR-09 locks

Approval would freeze these principles:

1. A citation is a typed claim/evidence relationship rather than a decorative source marker.
2. Work, citable unit, publication version, manifestation, and access artifact remain separate.
3. Bibliographic metadata and identifier links remain sourced assertions.
4. DOI, ISBN, ISSN, ORCID, ROR, and other identifiers are external aliases rather than universal truth keys.
5. Article, chapter, monograph, commentary, reference-work, dissertation, edition, review, dataset, and software identities remain distinct.
6. Preprints, accepted manuscripts, versions of record, corrections, retractions, translations, and revised editions remain versioned and related.
7. Current publication status is time-sensitive and source-attributed.
8. Peer-review process and status remain explicit provenance signals rather than correctness guarantees.
9. Journal-level review policy cannot silently determine item-level review state.
10. Metadata, abstract, full text, figures, supplements, reviews, and references receive separate access and rights treatment.
11. Discovery candidates cannot serve as substantive evidence without source inspection.
12. Exact quotations and locators bind to exact manifestations and source spans.
13. Paraphrase, published translation, human translation, and model translation remain distinct.
14. Secondary citation must be disclosed.
15. Bibliographic citation edges and claim/evidence support links remain separate.
16. Citation verification is claim-level and multidimensional.
17. Source dependence is tracked so repetition is not mistaken for independent corroboration.
18. Methodology, perspective, tradition, and coverage labels remain evidence-bearing, scoped assertions.
19. Source fitness is multidimensional and claim-specific.
20. Claims about current scholarship require a dated evidence horizon.
21. Consensus is represented through versioned landscape assessments rather than source counts.
22. Multilingual scholarship preserves original-language and pivot-translation provenance.
23. User-provided and private scholarship remains isolated from public corpora and training by default.
24. Runtime tools must resolve sources, versions, status, spans, quotations, claims, and citations deterministically where possible.
25. Citation strings are rendered from structured metadata through a versioned style adapter such as CSL.
26. Modern scholarship is primarily a retrieval, behavior-training, and evaluation resource unless later rights and curriculum reviews authorize more.
27. Fabricated citations, unsupported citations, quote errors, abstract overreach, hidden secondary citation, retracted-source misuse, false consensus, and restricted-content leakage are hard failures.
28. Every answer, benchmark, and experiment remains bound to exact scholarship, metadata, status, rights, and graph snapshots.

## 41. Decisions intentionally deferred

DR-09 does not yet select:

- final metadata providers and priority rules;
- exact bibliographic-resolution algorithms;
- exact current-status refresh cadence;
- exact source-ranking weights;
- default citation style and locale;
- final scholarly corpus;
- paid database subscriptions;
- full-text acquisition targets;
- source-by-source rights dispositions;
- exact methodology and tradition vocabularies beyond the initial extensible set;
- exact consensus-review workflow and panel;
- exact retrieval backend;
- exact claim-extraction and entailment models;
- final benchmark case count;
- final public/private scholarship partitions;
- exact multilingual launch coverage;
- physical schema, database, and serialization products;
- whether any modern scholarship enters continued pretraining;
- final user-facing evidence and bibliography interface.

Those decisions belong to DR-10, DR-13, DR-15 through DR-23, DR-25, DR-28, and later owner-approved experiment designs.

## 42. Approved statement

> **Biblical Scholar Lab will use a versioned, source-aware Modern Scholarship and Citation Model in which scholarly works, citable units, publication versions, manifestations, access artifacts, contributors, affiliations, identifiers, metadata assertions, publication events, peer-review assertions, post-publication notices, source spans, scholarly claims, quotations, translations, bibliographic citations, claim/evidence links, methodology assertions, and landscape assessments remain separate but interoperable entities. Discovery results, metadata, abstracts, snippets, full text, secondary reports, and model outputs will retain distinct evidential roles. Every consequential answer citation will be evaluated for source identity, version, locator, quotation, entailment, scope, methodology, current status, secondary-citation disclosure, translation provenance, and rights. Preprints, versions of record, corrections, retractions, translations, revised editions, and access copies will not be silently conflated; citation counts and retrieval counts will not establish consensus; peer review will remain a process signal rather than a truth certificate; and multilingual scholarship will preserve original-language and pivot provenance. Runtime tools, training records, benchmarks, and reports will bind to immutable scholarship, graph, metadata, status, access, rights, and review snapshots, while fabricated sources, unsupported citations, quotation errors, abstract overreach, hidden secondary citation, false consensus, retracted-source misuse, and restricted-content leakage remain hard failures.**

---

## References
