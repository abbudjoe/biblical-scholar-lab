# DR-17 — Corpus Composition and Sampling

| Field | Value |
|---|---|
| Design ID | `DR-17` |
| Status | `APPROVED` |
| Approval date | 2026-08-16 |
| Project owner | Joseph Abbud |
| Designer and independent reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2 and supplements; DR-03; DR-04; DR-05; DR-06; DR-07; DR-08; DR-09; DR-10; DR-11; DR-12; DR-13; DR-14; DR-15; DR-16 |
| Implementation authority | GPT-5.6 Sol, under the approved design |
| Execution authority | GPT-5.6 Luna only for frozen campaigns delegated by Sol under a later approved campaign envelope |
| Experiment-design authority | ChatGPT designs; Joseph Abbud approves; Sol implements only the approved design |
| Changes if approved | Establishes the authoritative corpus roles, source-quality and relevance model, vertical-slice and expansion policy, lineage-aware deduplication and contamination controls, hierarchical sampling architecture, general-replay and multilingual balancing requirements, tokenizer- and model-family materializations, immutable corpus and mixture manifests, per-sample exposure receipts, and evidence-gated mixture optimization needed before continued pretraining or translation-focused mid-training |

## 1. Purpose

Biblical Scholar Lab has identified many promising sources:

- Greek New Testament editions and linguistic annotations;
- Biblical Hebrew and Septuagint resources;
- Targum's historically deep New Testament translation collection;
- eBible's broad multilingual verse-aligned corpus;
- Open Christian Data's large collection of historical Christian writing;
- documentary papyri and wider Koine corpora;
- Greek, Latin, cuneiform, Egyptian, Hittite, Syriac, Coptic, and other ancient texts;
- early Christian and Jewish reception;
- modern open scholarship;
- page images and source-traceable synthetic document data;
- general multilingual replay data needed to preserve the base model.

Availability does not determine training value.

A corpus can be:

- legally admissible but irrelevant;
- highly relevant but too repetitive;
- historically important but low quality;
- useful for retrieval but unsuitable for weights;
- valuable for evaluation but forbidden from training;
- useful as translation evidence but not independent textual evidence;
- rich in tokens while poor in independent information;
- balanced by file count while badly biased by language, tradition, work, era, or digitization history.

DR-17 defines how Biblical Scholar Lab will compose, classify, deduplicate, split, sample, materialize, audit, and freeze data before any model adaptation.

It does not authorize bulk acquisition, admit any source whose DR-10 rights decision is incomplete, set final numerical mixture weights, select the winning model family, or authorize a billable training run. Those require source-registry implementation, corpus measurement, benchmark protection, proxy experiments, and owner-approved campaign designs.

## 2. Governing principle

> **A training token is an editorially weighted exposure, not a vote about truth, historical prevalence, manuscript support, translation quality, or scholarly consensus. Biblical Scholar Lab will optimize for relevant, independent, provenance-preserving learning signal rather than raw corpus size, file count, or the number of parallel translations. Every exposure must remain traceable to an exact source, role, lineage, quality state, rights decision, sampling policy, and experiment.**

The intended corpus flow is:

```text
candidate source and rights evidence
    → immutable source acquisition
    → source-preserving normalization
    → entity, lineage, language, date, genre, and role assignment
    → quality and relevance assessment
    → overlap, quotation, translation-family, and dependency clustering
    → protected benchmark and holdout firewall
    → eligibility decision by operation and training stage
    → hierarchical sampling policy
    → tokenizer- and model-specific materialization
    → immutable mixture manifest
    → sample generation and exposure logging
    → training, retention, memorization, and leakage evaluation
    → revised owner-approved mixture or stop decision
```

No directory of text files may be treated as an approved training corpus merely because it can be tokenized.

## 3. Corpus, evidence library, and training materialization remain separate

DR-17 distinguishes:

```text
SourceUniverse
    every known or candidate source object

AdmittedEvidenceLibrary
    source revisions admitted for at least one approved operation

CorpusSnapshot
    immutable graph-backed selection of admitted source revisions

StageEligibleCorpus
    the subset eligible for one training or evaluation stage

MixtureSpecification
    the approved sampling policy over eligible groups

ModelMaterialization
    tokenizer- and processor-specific examples and token sequences

ExposureLedger
    what the model actually saw, how often, and under which policy
```

This separation is mandatory.

A source may be available to retrieval while excluded from continued pretraining. A passage may be present in the evidence library while excluded from training because it belongs to a private benchmark cluster. A source may enter one model lineage but not another because of rights. A materialization may change when the tokenizer changes without changing the underlying corpus snapshot.

## 4. Canonical corpus entities

The logical architecture must support at least the following records.

### `CorpusSourceCandidate`

Records a candidate provider, source, exact revision, known components, languages, modalities, provenance, and preliminary rights state.

### `CorpusObjectRevision`

Identifies an exact immutable text, annotation, image, metadata, or derived object revision under DR-05 and DR-10.

### `CorpusUnit`

An addressable scholarly unit suitable for selection or sampling, such as:

```text
work
book
chapter
passage
paragraph
sentence
clause
verse
translation span
apparatus entry
commentary entry
article section
page region
image-text pair
structured task example
```

A corpus unit is not necessarily the eventual model sequence.

### `CorpusRoleAssignment`

Assigns one or more approved roles to a source or unit for a bounded stage and scope.

### `CorpusEligibilityDecision`

States which operations are allowed, blocked, held, or conditional for the exact component and lineage.

### `CorpusQualityAssessment`

Records text fidelity, annotation quality, OCR state, completeness, provenance, review, and known defects.

### `CorpusRelevanceAssessment`

Records how directly the material serves the version-one product and the particular training objective.

### `CorpusRelationship`

Records edition, translation, revision, quotation, derivation, duplication, lineage, and shared-source relationships.

### `OverlapCluster`

Groups exact, near, semantic, genealogical, quotation, paraphrase, or translated forms for deduplication and split control.

### `SplitAssignment`

Assigns a unit and all required related clusters to training, development, public test, private holdout, fresh challenge, RAG-only, or exclusion.

### `SamplingGroup`

Defines a coherent group over which probability mass or exposure limits may be assigned.

### `MixtureSpecification`

Defines hierarchical weights, floors, caps, curricula, sequence-length distributions, replay, and stop conditions.

### `ModelMaterialization`

Binds a corpus snapshot and mixture specification to an exact model tokenizer, processor, template, packing policy, and code revision.

### `TrainingSampleReceipt`

Records the exact source units, transformations, tokenization, metadata, packing boundaries, and exposure identity of a generated example.

### `ExposureLedger`

Aggregates how much effective exposure each source, work, passage, family, language, role, and overlap cluster actually received.

## 5. Corpus roles are explicit and stage-specific

A source may have several roles, but each role is separately authorized.

The initial role vocabulary includes:

```text
PRIMARY_BIBLICAL_TEXT
PRIMARY_ANCIENT_TEXT
LINGUISTIC_ANNOTATION
TEXTUAL_WITNESS_OR_APPARATUS
ANCIENT_VERSION
MODERN_TRANSLATION
DOCUMENTARY_LANGUAGE_CONTEXT
LITERARY_AND_HISTORICAL_CONTEXT
SECOND_TEMPLE_AND_JEWISH_CONTEXT
EARLY_CHRISTIAN_RECEPTION
LATER_RECEPTION_AND_HISTORICAL_THEOLOGY
MODERN_SCHOLARSHIP
GENERAL_MULTILINGUAL_REPLAY
MULTIMODAL_PAGE_DATA
STRUCTURED_TRANSLATION_NUANCE_TASK
SCHOLARLY_SFT_TASK
PREFERENCE_PAIR
RETRIEVAL_ONLY
TOOL_DATABASE_ONLY
PUBLIC_BENCHMARK
PRIVATE_HOLDOUT
FRESH_CHALLENGE
SYNTHETIC_CANDIDATE
QUARANTINE
EXCLUDED
```

Role assignment is stage-specific.

For example:

- A modern article may be `MODERN_SCHOLARSHIP` and `RETRIEVAL_ONLY` but not eligible for CPT.
- A public New Testament translation may be `MODERN_TRANSLATION`, eligible for structured mid-training, but capped in raw CPT.
- A critical apparatus may be available through a licensed tool while excluded from weights.
- A private benchmark case may use open primary texts but remain excluded from every training materialization because its diagnosis and annotation are protected.

## 6. Training stages consume different corpus projections

The project will not make one giant dataset and reuse it indiscriminately.

### Continued pretraining projection

May include, when authorized:

- Primary ancient and biblical texts;
- Documentary and literary ancient context;
- Selected ancient versions;
- Source-preserving linguistic renderings;
- Carefully bounded historical reception;
- General multilingual replay;
- Bounded metadata-aware examples.

It should not be dominated by modern translation repetition, modern commentary, or benchmark-style question answering.

### Translation-focused mid-training projection

May include:

- Source-to-translation pairs;
- Many-to-many alignments;
- Translation-family and edition metadata;
- Translation-difference units;
- Source-textual-state contrasts;
- Ancient-version relationships;
- Target-language constraints;
- Structured Translation Nuance tasks;
- Held-out-family and held-out-language controls.

### Scholarly SFT projection

May include:

- Human-authored or human-verified research tasks;
- Tool-use traces;
- Evidence packets;
- Claim/evidence links;
- Citation and abstention behavior;
- Multilingual, multimodal, safety, and anti-fallacy tasks.

### Preference projection

Contains reviewed chosen/rejected response pairs or verifiable reward cases under DR-19.

### Retrieval projection

May include current scholarship, restricted materials, exact sources, and large corpora not appropriate for weights, subject to DR-10.

### Benchmark projection

Remains isolated from every training and synthetic-data generation route unless a case is explicitly public development material.

## 7. Version-one vertical-slice corpus

The first corpus implementation should prove the full architecture with a bounded, high-value vertical slice rather than ingesting the entire ancient world.

The proposed vertical slice includes candidate source classes—not automatic admissions.

### Core Greek New Testament

- At least one authorized, exact Greek New Testament edition;
- Stable passage and edition identities;
- Morphology and lemma data;
- Richer syntax, senses, semantic roles, and participant referents where authorized;
- Explicit mappings among source editions where available.

MACULA Greek currently provides syntax trees, morphology, senses, semantic frames, participant referents, and mappings, with its linguistic datasets licensed under CC BY 4.0. It is therefore a high-priority candidate for the vertical slice, subject to component-level source-text review.[^macula]

### Translation-depth corpus

The public Targum subset is a priority candidate because it distinguishes translation works, editions, and per-site instances rather than presenting every collected copy as independent. The current public release describes 651 collected instances, 334 unique editions, and 302 public-domain or openly licensed instances across English, French, Italian, Polish, and Spanish.[^targum]

The vertical slice should use its public, reviewed subset and metadata—not its collection count as sampling weight.

### Multilingual breadth corpus

A rights-filtered eBible subset is a priority candidate for broad primary-text alignment. eBible provides canonical verse-aligned text and retains source-specific licenses, but its normalized files remove introductions, notes, and footnotes.[^ebible]

It is therefore useful for multilingual passage alignment and canary evaluation, but insufficient as:

- Phrase-level Translation Nuance gold;
- Paratext evidence;
- Scholarly explanation data;
- Independent textual evidence for each translation.

### Hebrew Bible and Septuagint context

The vertical slice should include a bounded set of Hebrew Bible and Septuagint passages directly relevant to selected New Testament benchmark and Translation Nuance cases, with source-native linguistic and textual representations where authorized.

It should not claim comprehensive Hebrew Bible or Septuagint coverage in version one.

### Documentary and wider Koine context

A bounded documentary-papyri set should provide genre and register evidence closer to ordinary Koine usage than literary corpora alone. Papyri.info combines version-controlled, peer-reviewed curation of papyrological texts, translations, commentary, metadata, bibliography, and images from several contributing databases.[^papyri]

Exact component licenses and quality remain item-specific.

### Greek and Roman literary context

A bounded, date- and genre-aware selection may include Homer, Plato, historians, philosophers, drama, and other Greek and Latin works relevant to language, rhetoric, intellectual context, or explicit comparison.

Perseus and related open corpora provide useful TEI editions, but file-level rights, edition identity, quality, and date remain individually reviewable. The Perseus canonical Greek repository states a CC BY-SA 4.0 default while warning that component copyright status and headers vary.[^perseus]

### Ancient Near Eastern context

A bounded selection of cuneiform, Egyptian, Hittite, Ugaritic, Persian, and other material may support directly named historical or comparative questions.

Oracc is a strong candidate for cuneiform material because it publishes richly annotated editions and places projects under CC BY-SA 3.0 by default unless a project states otherwise.[^oracc]

Ancient Near Eastern material should not be added merely to increase temporal breadth. It needs an explicit role and sampling cap.

### Early Christian and historical reception

A bounded subset of early Christian texts and historical commentary should support reception history, ancient citation, and methodological examples.

Open Christian Data currently reports approximately 195.7 million tokens across 805,146 records, but it is English-language, historical, uneven across traditions, and explicitly not an authoritative critical edition or representation of present-day global Christianity.[^ocd]

The vertical slice should therefore select by work, era, role, and source quality rather than importing the dataset as one monolithic domain.

### Modern scholarship

A small open scholarship library should support RAG, citation verification, and benchmark evidence. Modern scholarship remains retrieval-first under DR-09 and DR-10; it is not automatically admitted to CPT.

### General replay

The vertical slice must include a measured, rights-authorized general multilingual replay corpus appropriate to the selected base model and retention objectives.

General replay is not filler. It protects instruction potential, broad language competence, multimodal language alignment, and general reasoning from narrow-domain forgetting.

### Multimodal page data

The vertical slice should include source-traceable synthetic pages and a small authorized real-page set spanning scripture, headings, footnotes, study notes, Greek, Hebrew, and ordinary phone-photo degradation under DR-14.

## 8. Full-corpus expansion is evidence-gated

After the vertical slice and baseline evaluation are working, corpus expansion may add:

- Broader Hebrew Bible and Septuagint coverage;
- Additional documentary papyri and inscriptions;
- Larger Greek and Latin corpora;
- Cuneiform, Egyptian, Hittite, Ugaritic, Persian, Sanskrit, Chinese, and other ancient corpora where relevant;
- Additional ancient versions;
- Broader early Christian, Jewish, rabbinic, and reception material;
- Additional modern languages and native scholarship;
- Larger open scholarship collections;
- More real and synthetic page data.

Each expansion must identify the deficit it is expected to repair.

The project will not add a corpus merely because it is large, old, prestigious, or open.

## 9. Relevance is multidimensional

Every source or group receives a `CorpusRelevanceAssessment` that may include:

```text
target-task proximity
language and variety proximity
temporal proximity
geographic proximity
genre proximity
textual-history relevance
translation-history relevance
reception-history relevance
methodological relevance
multilingual value
multimodal value
negative-control value
benchmark value
```

A broad relevance tier may summarize these dimensions for sampling:

```text
R0_DIRECT_TARGET
R1_IMMEDIATE_CONTEXT
R2_BROAD_CONTEXT
R3_COMPARATIVE_OR_CONTROL
R4_ARCHIVAL_OR_FUTURE
```

The tier is not a quality score.

Homer may be high quality but broad context for many New Testament tasks. A documentary papyrus may be fragmentary yet immediate linguistic context. A modern commentary may be central to reception or scholarship but inappropriate for ancient-language CPT.

## 10. Quality is multidimensional and source-specific

A `CorpusQualityAssessment` should separate at least:

```text
textual fidelity
edition identity confidence
source completeness
structural integrity
OCR or HTR quality
normalization loss
annotation quality
alignment quality
metadata quality
language identification
passage and reference accuracy
provenance completeness
rights clarity
human review state
known defect density
```

There is no single universal quality score.

A source can be high quality for lexical retrieval and low quality for exact quotation. A machine-repaired OCR corpus can be useful for language-model exposure while remaining unsuitable as direct benchmark evidence.

## 11. Quality tiers

The baseline quality classes are:

```text
Q0_SCHOLARLY_BORN_DIGITAL_REVIEWED
Q1_HUMAN_TRANSCRIBED_OR_CORRECTED
Q2_HIGH_CONFIDENCE_MACHINE_WITH_REVIEWED_SAMPLE
Q3_RAW_OR_PARTIAL_OCR
Q4_MACHINE_REPAIRED_OR_MODEL_NORMALIZED
Q5_SYNTHETIC
Q6_UNKNOWN_OR_CONFLICTED
```

These classes do not automatically decide eligibility.

For example:

- Q3 may be useful in OCR-robustness training but excluded from primary-text CPT.
- Q4 may be admitted to a separate ablation with a low cap.
- Q5 may be valuable for controlled page geometry or negative examples but cannot become historical primary evidence.
- Q0 may still be excluded because of rights or benchmark leakage.

## 12. OCR and machine repair are preserved as separate layers

The project must retain:

```text
raw image or source
raw OCR/HTR
machine-corrected candidate
human-corrected transcription
normalized text
training projection
```

Machine correction may not erase the raw recognition or create false certainty.

The corpus reports exposure separately for:

- Scholarly born-digital text;
- Human-corrected transcription;
- Raw OCR;
- Machine-repaired OCR;
- Synthetic text.

A model may not be evaluated on its ability to reconstruct a held-out text after receiving a machine-repaired near-copy during training.

## 13. Synthetic data remains a candidate layer

Synthetic data may include:

- Structured Translation Nuance tasks generated from reviewed records;
- Counterfactual source-confusion cases;
- Tool-use traces;
- Page layouts and controlled degradations;
- Multilingual paraphrases;
- Negative examples;
- Candidate SFT or preference responses;
- Explanations generated by a stronger model.

Every synthetic item records:

```text
generating model and revision
prompt and evidence packet
source records
sampling and decoding
rights lineage
review state
content hash
watermark or synthetic provenance where applicable
```

Synthetic content remains:

```text
MODEL_GENERATED_CANDIDATE
```

until the applicable deterministic or human review promotes it for a defined purpose.

Human editing does not erase synthetic provenance.

## 14. The corpus needs an overlap ontology—not one deduplication flag

The overlap model distinguishes at least:

```text
IDENTICAL_OBJECT
IDENTICAL_CONTENT_DIFFERENT_INSTANCE
FORMATTING_OR_NORMALIZATION_VARIANT
EDITION_OR_REVISION_RELATION
DERIVED_TRANSCRIPTION
TRANSLATION_PARALLEL
BACK_TRANSLATION_OR_PIVOT
QUOTATION
PARAPHRASE
ALLUSION
FORMULAIC_OR_LITURGICAL_REPETITION
COMMENTARY_QUOTING_PRIMARY_TEXT
SCHOLARSHIP_QUOTING_ANOTHER_SOURCE
SYNTHETIC_DERIVATIVE
SEMANTIC_NEAR_DUPLICATE
SHARED_UPSTREAM_DATASET
UNKNOWN_RELATION
```

These relationships have different consequences.

An exact duplicate hosted by two websites should ordinarily receive one training exposure mass. Two editions of a translation may need separate lineage-aware exposure. Parallel translations are intentionally related and should not be deleted as semantic duplicates. A patristic quotation may be historically significant and should be retained, while also being clustered for leakage and independence analysis.

## 15. Deduplication means exposure control—not evidence destruction

The project should preserve source records even when it suppresses duplicate training mass.

The deduplication system may:

- Select one canonical training representative;
- Assign shared exposure mass across a duplicate cluster;
- Preserve several editions with capped family-level weight;
- Retain quotation relationships while preventing evaluation leakage;
- Exclude an exact benchmark derivative;
- Create a contrastive task from meaningful differences.

It may not erase:

- Provenance;
- Edition identity;
- Translation lineage;
- Historical quotation;
- Material textual variation;
- Rights differences;
- Review and correction history.

Research on language-model data has shown that near duplication can increase memorization and train-test overlap, while deduplication can improve training efficiency and evaluation reliability.[^dedup]

Biblical Scholar Lab has an unusually duplication-heavy domain, so the project requires stricter lineage-aware controls than generic web-corpus deduplication.

## 16. Exact, near, semantic, and relational overlap are measured separately

The initial detection stack should support candidate generation through:

```text
cryptographic identity
normalized exact identity
long exact-substring overlap
MinHash or locality-sensitive near-duplicate detection
edit distance
n-gram similarity
embedding similarity
translation alignment
source lineage
quotation and citation graph
manual or expert relation
```

No single similarity threshold becomes the universal deduplication rule.

High semantic similarity is expected among legitimate translations and paraphrases. It may indicate a translation-family relationship rather than a duplicate to delete.

Every automated cluster remains reviewable and records its method, thresholds, and uncertainty.

## 17. Translation multiplicity is not conceptual multiplicity

New Testament translations are a major source of raw tokens and a major risk of distorted training exposure.

The system therefore distinguishes:

```text
translation work
edition
revision
instance
language
family or lineage
source edition
passage realization
```

Sampling does not assign equal mass to every file or instance.

The default hierarchy for translation data is:

```text
language
→ translation family or work
→ edition or revision
→ passage cluster
→ span
```

A translation found on five websites does not receive five times the mass. A translation family with many revisions does not automatically outweigh a family with one edition. Agreement among related translations does not become independent evidence.

Targum's work/edition/instance metadata makes this distinction unusually tractable and should be preserved through every materialization.[^targum]

## 18. Repeated biblical passages receive controlled exposure

The same New Testament passage may appear in:

- Greek editions;
- Ancient versions;
- Hundreds of modern translations;
- Commentaries;
- Sermons;
- Creeds;
- Patristic quotations;
- Interlinears;
- Benchmark tasks;
- Synthetic explanations.

The `PassageExposureLedger` must report aggregate exposure across all these forms.

The project may deliberately repeat a passage for a structured alignment or Translation Nuance objective. It may not allow accidental repetition to dominate next-token training.

Exact quotation in the product is provided by deterministic tools. The model does not need hundreds of near-equivalent exposures merely to reproduce a verse from memory.

## 19. Historical repetition and formulaic language are not blindly removed

Formulae, liturgy, legal language, genealogies, repeated narratives, parallel passages, and scribal or translation patterns may be meaningful evidence.

The deduplication decision therefore records whether repetition is:

```text
ACCIDENTAL_COLLECTION_DUPLICATION
DERIVATIVE_COPY
MEANINGFUL_FORMULA
LITERARY_REPETITION
PARALLEL_TRADITION
TRANSLATION_PARALLEL
QUOTATION_OR_RECEPTION
UNKNOWN
```

Meaningful repetition may be retained but capped and explicitly sampled.

## 20. Splits operate over relationship clusters

Random row, verse, sentence, or chunk splitting is prohibited for consequential evaluation.

Split assignment must occur over the largest relevant leakage unit, which may include:

- Complete work;
- Passage cluster;
- Translation family;
- Edition and revision lineage;
- Manuscript or textual-form group;
- Quotation and paraphrase cluster;
- Synthetic derivation family;
- Page-layout template family;
- Scholarship argument or citation lineage;
- Language-pair relation;
- Source dataset lineage.

If one member enters a protected split, all members with material leakage risk enter the same split or are excluded.

## 21. Benchmark and training infrastructure are separated physically and logically

Private holdout and fresh-challenge material must not be accessible to:

- Corpus builders producing training materializations;
- Synthetic example generation;
- Proxy mixture optimization;
- Model selection prompts;
- Retrieval indexes used during training;
- Training-data quality models;
- Luna training runs;
- Public CI;
- Public repository content.

The training pipeline receives only a denylist or nonreversible cluster fingerprints sufficient to exclude overlap, not the protected case content.

Private benchmark access remains a separate capability with audit.

## 22. Project-induced contamination must be prevented even when base-model contamination is unknowable

Public Bible texts, Homer, Plato, common commentaries, and many scholarly discussions may already exist in foundation-model pretraining. We cannot guarantee a clean closed-book test of whether the base model has ever seen them.

We can guarantee that Biblical Scholar Lab does not add its protected:

- Gold diagnoses;
- Expert explanations;
- Evidence packets;
- Benchmark prompts;
- Scoring rubrics;
- Fresh page images;
- Private translations or notes;
- Held-out translation-family examples;

to its own training routes.

Evaluation reports must distinguish:

```text
UNKNOWN_BASE_MODEL_EXPOSURE
PROJECT_TRAINING_EXPOSURE
PROJECT_RETRIEVAL_EXPOSURE
PROJECT_PROMPT_DEVELOPMENT_EXPOSURE
PUBLIC_BENCHMARK_EXPOSURE
PRIVATE_HOLDOUT
FRESH_POST_FREEZE_CHALLENGE
```

String matching alone is insufficient because paraphrase and translation can carry contamination across forms and languages.[^rephrased-contamination] [^crosslingual-contamination]

## 23. Fresh challenge material is mandatory

A final model cannot be evaluated only on public cases available before training.

The final program should include:

- Private held-out cases frozen before training;
- Fresh expert-authored cases created after model and prompts are frozen;
- Fresh synthetic page layouts generated after model freeze from authorized source text;
- Held-out translation families;
- Held-out language or direction pairs where feasible;
- New evidence packets and distractor configurations.

Fresh cases remain subject to the same quality and rights review as the rest of the benchmark.

## 24. Corpus exposure is measured in several units

The project will report at least:

```text
raw bytes
Unicode characters or grapheme clusters
source words where meaningful
model tokens
number of scholarly units
number of works
number of passages
number of languages and varieties
number of translation works and families
number of overlap clusters
effective unique-content mass
effective independent-evidence mass
actual sampled exposures
```

Raw token count is not enough.

`effective independent-evidence mass` is a project analytical measure, not a claim that independence can be reduced perfectly to one number. It should discount known shared lineage and duplication while preserving the underlying relationships.

## 25. Model token count is materialization-specific

A corpus snapshot has no universal token count.

Qwen, Gemma, and Ministral tokenizers may assign materially different costs to:

- Polytonic Greek;
- Hebrew with and without cantillation;
- Syriac and Coptic;
- Scholarly transliteration;
- Long metadata tags;
- Spanish and French translations;
- Tool schemas;
- Page and multimodal inputs.

Every `ModelMaterialization` therefore records tokenizer-specific counts and fragmentation metrics.

The bake-off requires two comparison views:

### Content-matched

Each model receives the same scholarly units and examples. This compares what each architecture learns from the same content.

### Compute-matched

Each model receives an equal or approximately equal approved token, FLOP, or cost budget. This compares efficiency.

A model should not win merely because its tokenizer counted the same source content differently.

## 26. Sampling is hierarchical

The baseline sampler chooses through an explicit hierarchy such as:

```text
training stage
→ task or corpus role
→ relevance tier
→ language or variety
→ historical/genre group
→ work or corpus family
→ edition, witness, or translation family
→ passage or overlap cluster
→ scholarly unit
→ span and sequence projection
```

Each level may define:

- Weight;
- Floor;
- Cap;
- Temperature;
- Replacement policy;
- Curriculum schedule;
- Eligibility filter;
- Maximum exposures;
- Required diversity.

Sampling directly from a flat list of files or tokens is prohibited.

## 27. Sampling probability is not epistemic weight

A source sampled frequently is not thereby more true, ancient, authoritative, or consensual.

Training reports must avoid language such as:

> “The model saw the majority view more often, so it learned the consensus.”

Sampling is a capability intervention. Scholarly claims remain governed by DR-02 and runtime evidence.

## 28. Group caps protect against dominance

The sampling architecture must support caps over:

- Individual source artifact;
- Work;
- Passage cluster;
- Translation work and family;
- Commentary or sermon collection;
- Author;
- Publisher or provider;
- Language;
- Genre;
- Tradition label;
- Synthetic generator;
- OCR or quality tier;
- Overlap cluster.

Exact numeric caps remain experiment-specific, but every mixture must report them.

No source may gain unlimited exposure because it was divided into more files or records.

## 29. Floors protect rare but necessary capabilities

The sampler may set minimum exposure floors for:

- Koine Greek;
- Biblical Hebrew and Aramaic canaries;
- Target modern languages;
- Translation-family diversity;
- Documentary Koine;
- Ancient versions;
- Citation and source metadata;
- Multimodal page tasks;
- Safety and refusal behavior in later stages;
- General multilingual replay.

Floors must be justified by a named capability or retention risk.

They are not used to manufacture false historical balance.

## 30. Language balancing is capability-aware

The project will not sample languages simply in proportion to available tokens or equally across all languages.

Language weighting should consider:

- Version-one capability target;
- Base-model strength;
- Tokenizer cost;
- Source quality;
- User interface goal;
- Ancient-language role;
- Translation-family diversity;
- Reviewer availability;
- Retention risk;
- Benchmark deficit.

Ancient source-language data and modern answer-language data remain separate roles under DR-13.

## 31. Genre and register remain explicit

Ancient corpora must preserve genre and register such as:

```text
literary prose
poetry
drama
philosophy
historiography
documentary papyri
letters
legal and administrative text
inscriptions
ritual and liturgy
commentary
sermon
lexicon or grammar
```

A model trained mostly on literary Greek should not be described as broadly representative of Koine usage.

A corpus rich in sermons should not become the unmarked source of scholarly behavior.

## 32. Date and geography are sampling dimensions—not truth claims

Date bands and geographic regions may support curriculum or diversity analysis, but they retain DR-05 uncertainty.

The sampler must not silently convert disputed date or origin assertions into fixed categorical truth. It uses an approved operational projection tied to an exact graph snapshot and records the uncertainty.

## 33. General replay is mandatory and measured

Narrow domain adaptation risks forgetting broad language, reasoning, instruction, and multimodal capabilities.

Every CPT or large domain-adaptation mixture must include an approved general replay component unless a specific ablation intentionally removes it.

General replay must be:

- Rights-authorized;
- Multilingual where relevant;
- Compatible with the chosen base-model family;
- Free of protected benchmark contamination;
- Measured separately from domain data;
- Evaluated for its effect on domain learning and retention.

The project should compare several replay ratios rather than selecting one from intuition.

## 34. Modern translations receive structured training before raw repetition

The preferred use of large translation collections is:

```text
alignment
source comparison
family and edition discrimination
translation-cause diagnosis
target-language constraint analysis
chronology and revision lineage
held-out-family generalization
```

not unrestricted next-token repetition.

A bounded amount of translation prose may enter CPT for language exposure. Its family-level mass and passage-level exposure remain capped.

## 35. Modern historical Christian material is role-aware

Open Christian Data and similar collections may serve:

- Historical reception;
- Church history;
- RAG;
- Citation and methodology tasks;
- SFT candidates;
- Negative examples of outdated or biased claims;
- Tradition-conditioned comparisons.

They may not define:

- Current scholarly consensus;
- Global Christianity;
- The original meaning of a passage;
- An unmarked denominational default.

Sampling should preserve era, tradition, author, work, and source identity and cap large commentary or sermon collections.

## 36. Modern scholarship remains retrieval-first

Modern scholarship should normally remain outside CPT because:

- Rights are often restrictive;
- Claims change and require currentness;
- Disputed arguments should remain source-attributable;
- Exact citations and page locators matter;
- The runtime should retrieve current evidence rather than rely on frozen model memory.

A later owner-approved experiment may admit a carefully licensed scholarship subset for bounded continued pretraining or SFT. It must preserve source identity and compare against RAG-only use.

## 37. Negative and contrastive examples are first-class

The data program should include reviewed contrasts such as:

- Textual variant versus translation choice;
- Independent witness versus dependent translation family;
- Gloss versus contextual sense;
- Published quotation versus model translation;
- Translation effect versus translator intent;
- Direct source inspection versus secondary report;
- Apparatus silence versus actual omission;
- Strongly supported versus plausible diagnosis;
- In-scope research code versus unrelated programming;
- Page scripture versus study note;
- Legitimate religious language versus safety crisis.

These should usually enter structured mid-training, SFT, or preference stages rather than raw CPT.

## 38. Packing preserves document and evidence boundaries

Sequence packing may improve hardware utilization, but every packed sequence records:

- Component sample identities;
- Exact source boundaries;
- Separator and metadata policy;
- Attention or loss masks;
- Whether continuation across boundaries is allowed;
- Token-level source provenance;
- Rights and split compatibility.

Unrelated documents may not be concatenated in a way that teaches a false continuation or destroys source identity without a deliberate, tested packing policy.

Protected benchmark and restricted-rights boundaries cannot be crossed inside one sequence.

## 39. Metadata exposure is deliberate

The model may benefit from explicit tags for:

- Work;
- Passage;
- Language;
- Text layer;
- Edition;
- Translation role;
- Date range;
- Genre;
- Source type;
- Review state.

However, metadata can also leak benchmark labels, encourage shortcut learning, or make prose unnatural.

Every stage specifies:

- Which metadata fields are visible to the model;
- Which are used only by the sampler;
- Whether tags are always present, dropped, or varied;
- How tags differ from ordinary source text;
- Whether the model is expected to generate them.

## 40. Mixtures are immutable, named experimental objects

Every training mixture is represented by a `MixtureSpecification` containing:

```text
mixture identity and revision
approved design and experiment
corpus and graph snapshot
rights lineage
eligible source groups
hierarchical sampling policy
weights, floors, caps, and temperatures
curriculum schedule
sequence-length distribution
general replay policy
quality and synthetic limits
tokenizer and processor target
packing and metadata policy
randomness and seed policy
stop conditions
expected exposure report
content hash
```

Changing a weight, eligibility filter, cap, sequence-length policy, or replay ratio creates a new mixture revision and run identity.

## 41. Data-mixture optimization is evidence-gated

Human intuition should define meaningful groups and safe bounds, but it should not be assumed to identify the best mixture.

Methods such as DoReMi and RegMix demonstrate that domain weights can materially affect language-model performance and can be optimized through proxy experiments rather than selected only by intuition.[^doremi] [^regmix]

Biblical Scholar Lab should use a bounded, transparent proxy strategy:

1. Define human-reviewed groups and allowable ranges.
2. Select a small set of interpretable candidate mixtures.
3. Train inexpensive proxy or short adaptation runs.
4. Evaluate domain capability, worst-group performance, retention, memorization, and cost.
5. Fit or apply an approved mixture-selection method where justified.
6. Confirm the selected mixture at the target model size before the main run.

An optimizer may select weights within approved bounds. It may not:

- Add an unapproved source;
- Access private holdouts;
- Optimize directly on the final private benchmark;
- Eliminate a protected rare capability;
- Override rights or quality caps;
- Convert the benchmark into the training objective.

## 42. Proxy mixture studies must remain interpretable

The proxy study should compare at least:

```text
human relevance-weighted baseline
balanced-role baseline
general-retention-heavy baseline
translation-focused baseline
optimized candidate within approved bounds
```

The exact numbers belong to DR-24's experiment design after the corpus census.

Reports must show per-group exposures and outcome tradeoffs rather than presenting only one aggregate score.

## 43. Training exposure is logged, not merely planned

Planned sampling probabilities do not guarantee actual exposure.

Every run produces an `ExposureLedger` reporting actual:

- Tokens and examples by role;
- Language and variety;
- Work and passage;
- Translation family and edition;
- Relevance and quality tier;
- Overlap cluster;
- Synthetic origin;
- General replay group;
- Sequence length;
- Rights lineage;
- Number of repeat exposures.

Unexpected exposure drift is a run defect.

## 44. Reproducibility includes randomness and ordering

The training corpus must record:

- Random seeds;
- Shard order;
- Sampler revision;
- Worker and distributed-shuffle behavior;
- Resume state;
- Deterministic or nondeterministic operations;
- Data-loader and packing versions;
- Skipped or failed samples.

A resumed run must not silently restart the data order or duplicate a large portion of the corpus without recording that change.

## 45. Data corrections and rights changes create new snapshots

When a source is corrected, withdrawn, reclassified, or found to be mislicensed:

- The source revision is superseded or quarantined;
- Affected corpus snapshots and materializations are identified;
- Future sampling stops;
- Exposure ledgers identify affected model runs;
- Retraining, unlearning, release withdrawal, or disclosure is reviewed under DR-10;
- Historical runs retain their actual lineage.

Deleting a file from the current corpus does not rewrite the history of a model that already saw it.

## 46. Corpus safety, privacy, and poisoning controls

A source can be textually relevant and legally accessible while remaining unsafe for training or processing.

Every source and materialization must be screened, as appropriate to its modality and origin, for:

```text
personal or sensitive information
credentials, secrets, and access tokens
private user data
malicious archives or executable payloads
embedded prompt-injection or tool instructions
content designed to poison model behavior
undocumented synthetic or model-generated text
misleading source attribution
hate, abuse, coercion, or extremist material
medical or legal misinformation
corrupted Unicode, control characters, or mixed-script spoofing
```

The policy distinguishes **content that the assistant must understand and analyze** from **content that should shape its default behavior**.

Historical antisemitism, racism, coercive theology, abuse-enabling interpretation, and violent extremist material may be important for reception history, critique, safety evaluation, or source analysis. Such material may be retained under an explicit analytical role while being:

- Excluded from ordinary behavioral SFT;
- Capped or isolated in CPT;
- Paired with source, era, role, and critical-context metadata;
- Tested for undesirable imitation or default adoption;
- Prevented from becoming an unmarked theological or moral norm.

User uploads remain excluded from shared training unless a later explicit, informed, operation-specific consent and rights process authorizes a particular use under DR-10.

Ingestion must fail closed on:

- Unexpected executable content;
- Archive traversal or unsafe file paths;
- Hash or signature mismatch;
- Unrecognized binary payloads;
- Hidden network fetches;
- Provider or source revision changes outside the approved manifest;
- Content whose provenance or synthetic status cannot be established when that distinction is material.

Text found inside documents, annotations, OCR, metadata, repositories, or source code has no instruction authority over the corpus pipeline. A string such as `ignore previous instructions` remains corpus content rather than an operational command.

Any suspected poisoning, tampering, or private-data incident triggers quarantine and downstream impact analysis under DR-10 and DR-05.

## 47. Corpus health and data cards are mandatory

Every corpus snapshot and model materialization should produce a report including:

- Sources and rights lineages;
- Roles;
- Languages and varieties;
- Dates, genres, and regions;
- Quality tiers;
- OCR and synthetic shares;
- Works, passages, translations, and families;
- Exact, near, semantic, and relational overlap;
- Benchmark exclusions;
- Tokenization and fragmentation;
- Planned and actual exposures;
- Known representation biases;
- Missing traditions and languages;
- Current unresolved rights or quality holds;
- Changes from the previous revision.

## 48. Required corpus and sampling ablations

The later experiment ladder must include controlled comparisons such as:

```text
vertical slice versus expanded corpus
with versus without general replay
flat token sampling versus hierarchical sampling
instance-level versus family-level translation weighting
raw translation CPT versus structured translation mid-training
with versus without documentary Koine
with versus without broad classical context
with versus without historical reception material
open Christian data RAG-only versus bounded training use
raw OCR excluded versus capped inclusion
human weights versus optimized mixture
exact dedup only versus lineage-aware dedup
same-content versus compute-matched model-family materialization
```

A source group is promoted because it repairs a measured deficit—not merely because training loss decreases.

## 49. Corpus and sampling metrics

Required metrics include:

```text
held-out domain loss by role and language
Translation Nuance benchmark delta
linguistic and textual-critical delta
citation and source-type hard-failure delta
multilingual and multimodal retention
general-capability retention
memorization and extraction rate
exact and semantic leakage rate
passage and translation-family exposure concentration
worst-group performance
source-dependence awareness
calibration and abstention
training throughput and cost
tokenizer fragmentation
sample rejection and data-loader failure rate
rights and split compliance
expert-rated scholarly faithfulness
```

No one perplexity or benchmark average determines the corpus decision.

## 50. Promotion gates

A corpus or mixture advances only if it:

- Is fully bound to an approved rights and provenance snapshot;
- Excludes protected benchmark and holdout clusters;
- Passes exact, near, semantic, translation, and quotation leakage audits;
- Produces stable, reproducible materializations;
- Demonstrates a named capability improvement or required retention function;
- Does not create unacceptable source, citation, safety, rights, language, or multimodal regressions;
- Does not allow one work, passage, translation family, provider, language, or synthetic generator to dominate unintentionally;
- Has a complete exposure report;
- Passes expert and ChatGPT review;
- Receives owner approval for the next run.

## 51. Corpus hard failures

DR-17 treats the following as hard failures:

- Sampling files or records as though each were independent evidence.
- Counting duplicate translation instances as distinct translation works.
- Letting hundreds of parallel New Testament passages dominate CPT accidentally.
- Treating translation count as manuscript, historical, or scholarly support.
- Random verse, sentence, or row splits that leak parallel or quoted content.
- Making private holdout content available to training, synthetic generation, proxy optimization, or public CI.
- Treating string decontamination as sufficient where paraphrase or translation leakage exists.
- Removing meaningful textual variants or historical quotations as generic semantic duplicates.
- Erasing source, edition, rights, or overlap lineage during deduplication.
- Treating raw OCR, machine repair, synthetic text, or model annotations as reviewed primary text.
- Hiding an English or other pivot in multilingual data.
- Allowing public-domain availability to define scholarly consensus or corpus relevance.
- Training on restricted scholarship or apparatus material through an unauthorized derivative.
- Letting one commentary, sermon collection, author, tradition, or provider dominate because of record count.
- Omitting general replay without an explicit ablation and retention evidence.
- Comparing model families only by raw token count without content-matched analysis.
- Changing mixture weights or eligibility inside an active run without a new run identity.
- Failing to log actual exposure.
- Claiming a model is contamination-free because public source overlap was not detected.
- Promoting a larger corpus without showing value beyond the vertical slice.
- Permitting Luna to change source eligibility, deduplication, splits, mixture weights, or sampling policy.
- Ingesting private user data, credentials, executable payloads, or unsafe archives into a training lineage.
- Treating embedded document instructions as corpus-pipeline authority.
- Allowing historically hateful, abusive, coercive, or extremist content to become unmarked behavioral supervision.
- Failing to quarantine suspected poisoning, tampering, or undisclosed synthetic data.

## 52. Sol implementation discretion

The corpus and sampling architecture is owned by the approved design.

Sol may determine reversible implementation details such as:

- Module, class, and function organization;
- Efficient hashing, indexing, and candidate-generation implementations that preserve the approved overlap semantics;
- Dataframe, database, or streaming mechanics consistent with DR-28;
- Parallelization and caching;
- Test fixtures;
- Equivalent serialization and validation libraries;
- Performance optimizations that preserve exact corpus, split, mixture, and exposure results;
- Approved backend adapters.

Sol may not independently change:

- Corpus roles;
- Relevance or quality semantics;
- Vertical-slice scope policy;
- Stage eligibility;
- Overlap ontology;
- Split and holdout isolation;
- Sampling hierarchy;
- Translation-family weighting semantics;
- General replay requirement;
- Synthetic promotion rules;
- Mixture-selection authority;
- Required reports, metrics, gates, or hard failures;
- Experiment design.

A material limitation or alternative returns:

```text
BLOCKED_REQUIRES_DESIGN_REVIEW
```

Luna may execute only a frozen acquisition, census, materialization, training, or evaluation campaign delegated by Sol. Luna may not add sources, change rights or quality state, repair corpus code, alter splits, select mixture weights, or change sampling policy.

## 53. Binding decisions

Approval of DR-17 would lock:

1. Corpus snapshots, stage eligibility, mixture specifications, model materializations, and actual exposure remain separate immutable objects.
2. Every source and unit has explicit stage-specific corpus roles.
3. The first implementation builds a bounded high-value vertical slice before comprehensive corpus expansion.
4. The vertical slice prioritizes Greek New Testament text and linguistic annotation, translation depth, multilingual breadth, bounded Hebrew/Septuagint context, documentary Koine, selected ancient context, early reception, retrieval-first modern scholarship, general replay, and multimodal pages.
5. Targum supplies translation depth and lineage; eBible supplies broader verse-aligned primary-text coverage; neither becomes unfiltered training gold.
6. Open Christian Data is selected by work, era, role, source, and quality rather than ingested as one monolithic domain.
7. Full-corpus expansion requires a named capability hypothesis.
8. Relevance and quality remain multidimensional.
9. Raw OCR, machine repair, and synthetic content remain separately labeled and capped.
10. The project implements an overlap ontology rather than one deduplication flag.
11. Deduplication controls exposure while preserving evidence, editions, quotations, and provenance.
12. Translation work, edition, revision, and instance remain separate sampling units.
13. Passage exposure is aggregated across translations, commentaries, quotations, and synthetic derivatives.
14. Meaningful formulaic repetition is preserved but explicitly controlled.
15. Splits operate over work, passage, translation-family, quotation, derivation, and other leakage clusters—not random rows.
16. Private holdout and fresh challenge material remain outside every training, synthetic, proxy, and public route.
17. Base-model contamination remains unknown; project-induced contamination is auditable and prohibited.
18. Fresh post-freeze challenge cases are mandatory.
19. Corpus size is reported in raw and effective units, including actual exposures.
20. Model token counts and materializations are tokenizer-specific.
21. Model-family bakeoffs include content-matched and compute-matched views.
22. Sampling is hierarchical rather than flat over files or tokens.
23. Sampling probability never becomes epistemic weight.
24. Work, passage, family, language, provider, quality, and synthetic caps are supported.
25. Capability-protecting floors are supported and justified explicitly.
26. Language, genre, date, and geography remain explicit sampling dimensions.
27. General multilingual replay is mandatory unless removed in an explicit ablation.
28. Large translation collections are used structurally before they are used as raw repetition.
29. Modern historical Christian material remains role-aware, and modern scholarship remains retrieval-first by default.
30. Negative and contrastive cases are first-class structured training material.
31. Packing preserves sample identity, source boundaries, rights, and split compatibility.
32. Metadata exposure is stage-specific and deliberate.
33. Every mixture is an immutable named experimental object.
34. Mixture weights are selected through bounded human-reviewed proxy experiments rather than intuition alone.
35. Mixture optimization cannot access private final benchmarks or override source, rights, quality, or rare-capability constraints.
36. Planned and actual exposure are both reported.
37. Randomness, sharding, packing, resume, and skipped samples remain reproducible.
38. Corrections and rights changes create new snapshots and downstream impact analysis.
39. Corpus ingestion and materialization include explicit privacy, secret, malicious-payload, prompt-injection, poisoning, Unicode-security, and synthetic-provenance controls.
40. Historically harmful material may be retained for analysis but cannot silently become unmarked behavioral supervision.
41. User uploads remain excluded from shared training by default.
42. Every snapshot and materialization receives a corpus health report.
43. Corpus value is established through controlled ablation, not training loss alone.
44. No aggregate metric may hide leakage, memorization, rights, source, language, safety, privacy, or retention failures.
45. Sol implements the approved corpus system; ChatGPT designs and reviews the mixtures and experiments; Joseph approves consequential decisions.
46. Luna may only execute frozen campaigns delegated by Sol and has no corpus-design or code authority.

## 54. Decisions intentionally deferred

DR-17 does not yet select:

- The complete source inventory or final admission decision for any unreviewed source;
- Exact vertical-slice work and passage lists;
- Exact training, development, public-test, private-holdout, and fresh-challenge proportions;
- Exact deduplication thresholds or embedding models;
- Exact caps, floors, temperatures, or mixture percentages;
- The general replay dataset;
- Exact tokenizer-specific sequence formats;
- Exact packing and loss-mask implementation;
- Exact curriculum or token budget;
- Whether DoReMi, RegMix, another optimizer, or only manual proxy comparison is used;
- Exact proxy-model sizes and number of mixture trials;
- Exact long-context sequence-length curriculum;
- Exact synthetic-data volume or reviewer workflow;
- Exact corpus storage and query products;
- Final public corpus or model release status.

Those decisions require the implemented source registry, corpus census, benchmark firewall, model bakeoff, later training-curriculum review, DR-24 experiment design, DR-28 integrated architecture, and owner approval.

## 55. Approved statement

> **Biblical Scholar Lab will use an immutable, role-aware, rights-bound corpus and sampling architecture in which candidate sources, admitted evidence, corpus snapshots, stage-eligible corpora, mixture specifications, model-specific materializations, training samples, and actual exposure ledgers remain separate but linked objects. Training data will be selected for relevant, independent, provenance-preserving learning signal rather than raw token count, file count, public-domain availability, or the number of parallel translations. The first implementation will build a bounded vertical slice centered on Greek New Testament text and linguistic annotation, structured translation depth, multilingual primary-text breadth, directly relevant Hebrew Bible and Septuagint material, documentary Koine, selected ancient context, early reception, retrieval-first modern scholarship, general multilingual replay, and multimodal page evidence before comprehensive expansion. Every source will retain explicit role, relevance, quality, language, date, genre, lineage, rights, review, safety, and source identity. Corpus ingestion will fail closed on private data, credentials, unsafe payloads, untrusted instructions, suspected poisoning, and material provenance failures; historically harmful content may remain available for explicitly labeled analysis without becoming unmarked behavioral supervision. Exact, near, semantic, translation, quotation, revision, synthetic, and shared-upstream overlap will remain distinct; deduplication will control exposure without erasing meaningful textual variation, translation genealogy, historical quotation, or provenance. Splits will operate over relationship clusters rather than rows, and private holdout and fresh challenge material will remain inaccessible to training, synthetic generation, mixture optimization, and public workflows. Sampling will be hierarchical across stage, role, relevance, language, genre, work, edition or translation family, passage cluster, and unit, with explicit floors, caps, replay, quality limits, and actual exposure reporting. Modern translations will be used primarily through structured alignment and Translation Nuance objectives; modern scholarship will remain retrieval-first by default; OCR, machine repair, and synthetic data will remain labeled and separately gated. Mixture weights will become immutable experimental objects selected through bounded human-reviewed proxy studies and confirmed at target scale, while content-matched and compute-matched materializations will support fair model-family comparison. Every corpus and mixture will produce a reproducible health, leakage, rights, tokenization, concentration, and exposure report, and no corpus expansion or mixture will advance without measured capability value, retention, expert review, ChatGPT review, and owner approval.**

[^targum]: Maciej Rapacz and Aleksander Smywiński-Pohl, “Targum — A Multilingual New Testament Translation Corpus,” dataset card and LREC 2026 release, describing 651 collected translation instances, 334 unique editions, a 302-item public subset, five languages, and separate work, edition, and instance metadata: <https://huggingface.co/datasets/mrapacz/targum-corpus>.
[^ebible]: BibleNLP, `ebible`, describing canonical verse-per-line alignment, removal of introductions, comments, and footnotes, and source-specific license retention: <https://github.com/BibleNLP/ebible>.
[^ocd]: Open Christian Data, dataset card, describing approximately 195.7 million tokens and 805,146 records across historical English Christian texts, together with explicit limitations concerning language, tradition, authority, and source verification: <https://huggingface.co/datasets/OpenChristianDataOrg/open-christian-data>.
[^macula]: Clear Bible, `macula-greek`, describing syntax, morphology, senses, semantic frames, participant referents, and mappings; the linguistic datasets are released under CC BY 4.0: <https://github.com/Clear-Bible/macula-greek> and <https://github.com/Clear-Bible/macula-greek/blob/main/LICENSE.md>.
[^papyri]: Papyri.info, describing the Papyrological Navigator and version-controlled, peer-reviewed Papyrological Editor integrating texts, translations, commentary, metadata, bibliography, and images: <https://papyri.info/>.
[^perseus]: Perseus Digital Library, `canonical-greekLit`, describing a CC BY-SA 4.0 default while warning that file metadata and component rights vary and remain under review: <https://github.com/PerseusDL/canonical-greekLit>.
[^oracc]: Oracc, “About Oracc,” describing free online editions of cuneiform texts and a default CC BY-SA 3.0 license unless project-specific terms state otherwise: <https://oracc.museum.upenn.edu/doc/about/aboutoracc/>.
[^dedup]: Katherine Lee et al., “Deduplicating Training Data Makes Language Models Better,” showing that near duplicates and repeated substrings increase memorization and evaluation overlap and that deduplication can improve efficiency and reliability: <https://arxiv.org/abs/2107.06499>.
[^doremi]: Sang Michael Xie et al., “DoReMi: Optimizing Data Mixtures Speeds Up Language Model Pretraining,” demonstrating proxy-model optimization of domain weights and material effects from data-mixture selection: <https://arxiv.org/abs/2305.10429>.
[^regmix]: Qian Liu et al., “RegMix: Data Mixture as Regression for Language Model Pre-training,” demonstrating small-model mixture experiments and regression-based prediction of larger-model mixture performance: <https://arxiv.org/abs/2407.01492>.
[^rephrased-contamination]: Shuo Yang et al., “Rethinking Benchmark and Contamination for Language Models with Rephrased Samples,” showing that string matching can miss paraphrased and translated contamination and advocating fresh one-time evaluations: <https://arxiv.org/abs/2311.04850>.
[^crosslingual-contamination]: Feng Yao et al., “Data Contamination Can Cross Language Barriers,” analyzing translated benchmark contamination that can evade ordinary overlap checks: <https://arxiv.org/abs/2406.13236>.
