# DR-13 — Multilingual Architecture

| Field | Value |
|---|---|
| Design ID | `DR-13` |
| Status | `APPROVED` |
| Approval date | 2026-08-16 |
| Project owner | Joseph Abbud |
| Designer and independent reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2 and supplements; DR-03; DR-04; DR-05; DR-06; DR-07; DR-08; DR-09; DR-10; DR-11; DR-12 |
| Implementation authority | GPT-5.6 Sol, under the approved design |
| Execution authority | GPT-5.6 Luna only for frozen campaigns delegated by Sol under a later approved campaign envelope |
| Experiment-design authority | ChatGPT designs; Joseph Abbud approves; Sol implements only the approved design |
| Approved change | Establishes multilingualism as a cross-cutting product, corpus, retrieval, training, benchmark, multimodal, safety, and release contract rather than a later translation layer |

## 1. Purpose

Biblical Scholar Lab is English-first for version one, but it is not architected as an English system that may later receive translated prompts. It must support several distinct multilingual requirements from the beginning:

- ancient source texts in Greek, Hebrew, Aramaic, Latin, Syriac, Coptic, and other languages;
- modern Bible translations in many languages;
- scholarly works whose language differs from the user's language;
- users who ask and receive answers in different modern languages;
- quotations that must remain in their source language while being explained or translated;
- multilingual and mixed-script printed pages;
- language-specific canon names, Bible references, punctuation, directionality, and typography;
- language-specific scope, safety, and crisis-resource behavior;
- cross-lingual retrieval without silently treating English as the only authoritative scholarly language;
- future language expansion without rebuilding the corpus ontology, Translation Nuance Core, model harness, or benchmark.

DR-13 defines:

- the language, language-variety, script, orthography, locale, and transliteration identity model;
- the distinction between ancient source-language competence and modern interface-language competence;
- capability-specific support tiers and product claims;
- user-language resolution and code-switching behavior;
- multilingual retrieval, evidence selection, pivot translation, and answer generation;
- multilingual corpus, training, SFT, preference, multimodal, quantization, and mobile requirements;
- multilingual benchmark design, native expert review, and worst-group reporting;
- right-to-left, mixed-direction, Unicode-security, and source-fidelity requirements;
- explicit fallback and escalation behavior when a requested language is not sufficiently supported.

DR-13 does **not** select the final launch languages beyond the already approved English-first posture, choose the winning foundation model, fix corpus mixture percentages, authorize translation of copyrighted sources, select a machine-translation provider, or claim professional-quality support in any language before benchmark and human-review gates pass.

## 2. Governing principle

> **Language is part of the evidence, not merely a presentation preference. Every source, question, answer, quotation, translation, retrieval route, and model-generated rendering must retain its language, variety, script, orthography, provenance, and support status. Biblical Scholar Lab may reason across languages, but it may not hide an English pivot, translate away material ambiguity, or claim equivalent capability where native evidence and evaluation do not exist.**

The system preserves this chain:

```text
user language and locale intent
    → exact source-language and publication-language identities
    → language-aware reference and retrieval planning
    → same-language, source-language, and cross-language evidence
    → explicit translation or pivot provenance where required
    → language-constrained structured analysis
    → native-language verification and citation audit
    → answer in the requested language with source wording preserved
```

No broad vendor claim such as “supports 200 languages” becomes a Biblical Scholar Lab product claim without task-specific measurement.

## 3. Multilingualism has several independent dimensions

The system separates at least the following language roles:

```text
interface_language
interface_locale
question_language
requested_answer_language
actual_answer_language
source_text_language
source_text_variety
source_script
source_orthography
quotation_language
publication_language
title_language
abstract_language
retrieval_query_language
retrieved_evidence_language
display_translation_language
pivot_language
model_generated_translation_language
tool_input_language
tool_output_language
page_region_language
```

These may all differ in one valid workflow.

Example:

```text
interface locale: es-MX
question language: Spanish
answer language: Spanish
biblical source: Koine Greek
ancient version: Latin
scholarship: English and German
quotation display: original German plus a labeled model translation into Spanish
Bible page image: Italian
```

A single field named `language` is therefore invalid for consequential records.

## 4. Language identity is richer than a code

The canonical logical entity is a versioned `LanguageVarietyProfile`.

It may record:

```text
stable language-variety identity
preferred display name
self-name or endonym
BCP 47 aliases
ISO 639 aliases where applicable
script identities
historical period or stage
dialect or regional variety
orthographic tradition
vocalization or pointing tradition
register
genre and corpus domain
writing direction
normalization profile
transliteration schemes
known ambiguity with related varieties
source and review state
```

This is necessary because labels such as these are too broad by themselves:

```text
Greek
Hebrew
Aramaic
Syriac
Latin
Arabic
Chinese
Spanish
French
```

The project must distinguish, where material:

- Classical, Hellenistic, Koine, patristic, Byzantine, and Modern Greek;
- Biblical, Qumran, Mishnaic, Medieval, and Modern Hebrew;
- Biblical Aramaic, Jewish Palestinian Aramaic, Jewish Babylonian Aramaic, Syriac varieties, and other Aramaic traditions;
- Classical, ecclesiastical, medieval, and modern Latin;
- regional and orthographic modern-language varieties where wording, reference names, or safety resources differ.

Language identity is an evidence-bearing assertion under DR-05 rather than a guess derived only from script or filename.

## 5. BCP 47 and CLDR are interoperability adapters

External language and locale interchange uses canonical BCP 47 tags where suitable. BCP 47 supports language, script, region, variant, extension, and private-use subtags and is the default exchange syntax for modern language and locale identifiers.[^bcp47]

Unicode CLDR and LDML provide versioned locale data and canonicalization for language, script, region, variant, formatting, collation, display names, text boundaries, and transforms.[^cldr]

The project will:

- preserve the exact externally supplied language tag;
- store a canonicalized external representation;
- retain the registry and CLDR revision used;
- map external tags to opaque internal language-variety IDs;
- use project profiles when a historical language or scholarly variety is not adequately represented by one standard tag;
- never encode permanent semantic identity solely inside a mutable external code;
- distinguish language identity from locale preferences.

A BCP 47 tag is an interoperability label, not proof that the corresponding language capability exists in the model.

## 6. Script, orthography, transliteration, and language remain separate

The same language may use several scripts or orthographies, and the same script may represent several languages.

The architecture therefore separates:

```text
LanguageVarietyProfile
ScriptProfile
OrthographyProfile
TransliterationScheme
TextViewProfile
LocaleProfile
```

Examples include:

- Biblical Aramaic written in square Hebrew script;
- Greek represented in Greek script or scholarly transliteration;
- Hebrew with consonants only, vocalization, cantillation, or a search-normalized view;
- Serbian or other modern languages represented in more than one script;
- Chinese writing-system and locale distinctions;
- Latin-script transliteration of Syriac or Coptic.

A transliteration is a derived text view with a named scheme, transformation activity, information-loss profile, and source mapping. It is not the original text and does not replace the source script.

## 7. Language support is capability-specific

Biblical Scholar Lab will not publish one global statement such as:

```text
Spanish supported
```

Instead, each `LanguageCapabilityProfile` reports support by capability:

```text
interface navigation
question understanding
answer generation
Bible reference parsing
exact passage retrieval
quotation display
original-language analysis
translation comparison
Translation Nuance diagnosis
ancient-version handling
scholarship discovery
scholarship synthesis
citation rendering
scope and safety
multimodal OCR and layout
tool calling
structured output
long-context use
mobile or quantized operation
```

A language may be strong for Bible-text lookup but weak for modern scholarly retrieval. Another may be strong for general conversation but unvalidated for page OCR or crisis-resource handling.

No aggregate label may hide a required capability failure.

## 8. Product support tiers

Each capability receives one of these states:

```text
FULL
BETA
CANARY
TRANSFER_ONLY
SOURCE_OR_EVIDENCE_ONLY
DISPLAY_ONLY
UNSUPPORTED
BLOCKED_BY_RIGHTS_OR_RESOURCES
```

### `FULL`

Requires:

- native-language benchmark coverage;
- native or professionally reviewed SFT and preference examples where post-training is used;
- language-aware tools and retrieval;
- citation and quotation verification;
- scope and sensitive-use tests;
- human review by qualified native or near-native reviewers;
- multimodal evaluation if the product claims page support;
- published limitations and worst-case results.

### `BETA`

Requires a bounded native benchmark, reviewed examples, language-aware retrieval, and disclosed limitations. It is useful but not represented as parity with `FULL`.

### `CANARY`

Used to detect regression in a language or script not yet offered as a product-quality interface.

### `TRANSFER_ONLY`

The base model may respond, but the project has not validated domain-specific quality. The interface must not imply a quality guarantee.

### `SOURCE_OR_EVIDENCE_ONLY`

The language can be ingested, displayed, retrieved, or analyzed within a bounded scholarly role but is not offered as a normal user-interface language.

### `DISPLAY_ONLY`

Exact content can be shown, but the assistant may not claim meaningful analysis in that language.

### `BLOCKED_BY_RIGHTS_OR_RESOURCES`

The architecture could support the capability, but required sources, reviewers, tools, or permissions are unavailable.

## 9. Version-one language posture

DR-13 preserves the DR-01 product contract:

### Modern interface languages

```text
English: initial FULL target
Spanish: initial BETA candidate
French: initial BETA candidate
```

Spanish and French do not become `BETA` merely because Targum contains translations in those languages. They must pass the DR-13 and benchmark gates.

Polish and Italian are valuable Targum corpus languages but receive no version-one interface-quality claim until native evaluation and retrieval coverage exist.

At least one non-Latin-script modern language should enter the canary program before public release. The exact language will be selected later based on:

- qualified reviewer availability;
- scripture and scholarship coverage;
- script and directionality diversity;
- user demand;
- foundation-model behavior;
- rights and resource availability.

### Ancient and historical source languages

The provisional target roles are:

```text
Koine Greek: CORE_ANALYTIC_TARGET
Classical and wider ancient Greek: CONTEXTUAL_ANALYTIC_TARGET
Biblical Hebrew: BOUNDED_ANALYTIC_TARGET for NT-context workflows
Biblical Aramaic: BOUNDED_ANALYTIC_TARGET
Latin: ANCIENT_VERSION_AND_SCHOLARSHIP_TARGET
Syriac: ANCIENT_VERSION_EVIDENCE_TARGET
Coptic: ANCIENT_VERSION_EVIDENCE_TARGET
other ancient languages: SOURCE_OR_EVIDENCE_ONLY until separately validated
```

These are design targets rather than completed capability claims.

Modern Greek competence cannot substitute for Koine Greek evaluation. Modern Hebrew competence cannot substitute for Biblical Hebrew evaluation.

## 10. User language and answer language resolution

The runtime receives a versioned `LanguageInteractionContext` containing, where available:

```text
explicit user answer-language request
interface locale
conversation language history
current message language and confidence
selected study language
source artifact languages
accessibility preferences
transliteration preferences
language capability profile
```

Resolution precedence is:

1. Explicit user instruction.
2. Explicit session or account preference.
3. Current conversation's established answer language.
4. Current message language when sufficiently clear.
5. Interface locale as a fallback.
6. Product default only when no other reliable signal exists.

The system must not change answer language because retrieved evidence or model decoding drifts toward English.

If the requested language is unsupported for the task, the assistant should disclose the limitation and offer the strongest safe alternative, such as:

- answer in a supported language;
- provide exact source text and a clearly labeled provisional translation;
- restrict the response to deterministic passage information;
- escalate to a larger or language-specialist model;
- request human review.

## 11. Automatic language identification remains probabilistic

Language identification records:

```text
candidate languages or varieties
script evidence
confidence
passage scope
code-switch boundaries
model/tool identity
known limitations
user corrections
```

It may not silently overwrite user-supplied or source-catalog language identity.

Short strings, proper names, transliterations, shared vocabulary, biblical references, and mixed-language quotations are often underdetermined. The system should preserve ambiguity rather than forcing one language label.

## 12. Code-switching and mixed-language discourse are first-class

A message, page, or scholarly source may contain:

- an English question with a Greek phrase;
- Spanish prose quoting an English article;
- a Hebrew page with English study notes;
- a French commentary using Latin technical terms;
- a multilingual parallel Bible;
- transliterated Syriac inside German scholarship;
- code-switching between a user's primary language and biblical-language terminology.

The system therefore supports span-level language and script annotations.

It should not:

- translate original-language terms merely to force monolingual output;
- treat technical code-switching as malformed language;
- let one dominant language relabel every embedded span;
- produce an answer in several languages accidentally.

Intentional multilingual answers must be structured and labeled.

## 13. No hidden English pivot

English may be used as a deliberate pivot when it is the best available route, but the pivot must be explicit in the audit trace and disclosed where it affects scholarly meaning.

A `PivotTranslationRecord` identifies:

```text
source language and source span
pivot language
pivot text
pivot origin
translation model or publication
prompt and decoding identity where applicable
review state
known uncertainty
final answer language
whether reasoning used source, pivot, or both
```

The system must distinguish:

```text
DIRECT_SOURCE_LANGUAGE_ANALYSIS
PUBLISHED_TRANSLATION_ASSISTED_ANALYSIS
HUMAN_TRANSLATION_ASSISTED_ANALYSIS
MODEL_PIVOT_ASSISTED_ANALYSIS
MULTI_PIVOT_ANALYSIS
SOURCE_NOT_DIRECTLY_ANALYZED
```

It may not state that it analyzed a German, Syriac, or Coptic source directly when it only consumed an English summary.

Cross-lingual RAG research shows that systems can drift into the wrong answer language and can struggle to reason when query and evidence languages differ. These are benchmarked failure modes, not presumed solved capabilities.[^xrag]

## 14. Quotation and translation provenance remain visible

Every quoted or translated span must identify whether it is:

```text
ORIGINAL_SOURCE_WORDING
PUBLISHED_TRANSLATION
ANCIENT_TRANSLATION
PROJECT_HUMAN_TRANSLATION
USER_SUPPLIED_TRANSLATION
MODEL_GENERATED_TRANSLATION
PIVOT_TRANSLATION
PARAPHRASE
```

Rules include:

- Quotation marks apply only to exact verified wording.
- A model-generated translation may be useful, but it is labeled as generated.
- A translated quotation does not replace the original-language source.
- The assistant cannot attribute its own wording to a scholar.
- Material ambiguity should not be silently removed during translation.
- When an exact published translation is unavailable because of rights, the system may provide a rights-compliant paraphrase or generated rendering with clear provenance.

## 15. Reference parsing and canon display are localized

DR-04's language-neutral internal passage identity remains authoritative.

DR-13 adds localized adapters for:

- book names and abbreviations;
- punctuation and range conventions;
- number systems;
- localized canon and edition names;
- historical title variants;
- right-to-left reference display;
- OCR-corrupted localized references.

The same canonical passage may be resolved from:

```text
Romans 3:22
Romanos 3:22
Romains 3,22
Römer 3,22
羅馬書 3:22
رومية ٣:٢٢
```

A localized string is a presentation and parsing form, not the permanent passage identity.

## 16. Multilingual retrieval uses several routes

The retrieval planner may combine:

```text
SAME_LANGUAGE_RETRIEVAL
SOURCE_LANGUAGE_PRIMARY_TEXT_RETRIEVAL
CROSS_LINGUAL_SEMANTIC_RETRIEVAL
TRANSLATED_QUERY_RETRIEVAL
MULTILINGUAL_LEXICAL_RETRIEVAL
CANONICAL_PASSAGE_LINK_RETRIEVAL
CITATION_NETWORK_EXPANSION
TRANSLATION_FAMILY_RETRIEVAL
LANGUAGE_SPECIALIST_RETRIEVAL
```

Every route records:

```text
original query
query language
translated or expanded queries
retriever and index revision
candidate evidence languages
reranker
language preference policy
rights filters
selected evidence
rejected evidence
pivot translations
```

No one route is assumed universally best.

The exact Bible passage and source-language tools should use language-neutral canonical identities rather than semantic retrieval where an exact lookup exists.

## 17. Retrieval should prefer inspectable evidence—not automatically same-language evidence

When equally suitable evidence exists, the system should prefer evidence that the user can inspect directly in the requested language.

However, same-language evidence cannot outrank materially stronger or more relevant evidence merely because of language.

The retrieval objective must balance:

```text
semantic relevance
claim-type fitness
source quality and proximity
language inspectability
methodological coverage
source independence
rights and display permissions
currentness
citation granularity
```

The interface can present:

- source-language evidence;
- an authorized published translation;
- a clearly labeled display translation;
- a concise explanation in the user's language.

Research on multilingual RAG shows that multilingual evidence can improve robustness and perspective coverage, but it can also introduce language and citation-distribution biases.[^bordirlines]

## 18. English-language retrieval cannot define global scholarly consensus

A landscape assessment must record its language coverage under DR-09.

If the evidence search covered only English, the assistant may say:

> “Within the English-language scholarship retrieved…”

It may not say:

> “Scholars worldwide agree…”

The multilingual architecture must preserve:

- scholarship language;
- publication region;
- translated-title provenance;
- abstract versus full-text access;
- whether native-language sources were searched;
- whether evidence was read directly or through a pivot.

Adding languages is not merely a translation feature; it may change which scholarly traditions and historical sources are visible.

## 19. Context composition is language-aware

The context composer budgets tokens using the exact selected model and tokenizer projection from DR-11.

It cannot assume that the same New Testament, source packet, or citation block consumes equal context across languages and scripts.

The composer records:

```text
answer language
included source languages
translation layers
context token count per component
omitted evidence
compression or summarization
pivot translations
output reserve
long-context mode
```

The normal multilingual packet should contain:

```text
user's selected translation or study language
relevant original-language text
selected comparison translations
retrieved scholarship in the strongest available languages
necessary display translations
```

It should not load complete New Testaments in many languages merely because the context window permits it.

Full-canon context is an experiment under DR-11 and DR-12, not the default multilingual strategy.

## 20. Multilingual corpus architecture

Every corpus record retains:

```text
language variety
script
orthography
text layer
translation direction
source or target role
published or generated status
edition and translation lineage
rights
quality tier
native or projected annotation
review state
```

Language metadata may not be inferred only from directory names or vendor labels.

The corpus must distinguish:

- independent original works;
- parallel translations of one work;
- duplicate instances of one edition;
- revision families;
- machine-translated copies;
- ancient daughter versions;
- bilingual and multilingual editions;
- code-switched or mixed-language scholarship.

Parallel volume is not independent conceptual volume.

## 21. Targum and eBible have complementary roles

Targum provides unusually deep historical and edition-level New Testament translation coverage in English, French, Italian, Polish, and Spanish. Its public subset contains 302 public-domain or openly licensed translation instances, while metadata distinguishes works, editions, and instances.[^targum]

Its role is:

- translation-history depth;
- revision lineage;
- chronology;
- confessional and edition comparison;
- held-out-family evaluation;
- structured New Testament translation tasks.

It is not a broad global-language solution.

BibleNLP's eBible collection provides verse-aligned primary-text breadth across many languages. The project repository states that each translation retains its original license and that the normalized corpus contains verse text only, with introductions, notes, and footnotes removed.[^ebible]

Its role is:

- broad scripture-text alignment;
- canonical passage retrieval;
- multilingual primary-text canaries;
- cross-lingual passage matching;
- low-resource and transfer experiments.

It is not sufficient for:

- phrase-level scholarly alignment;
- translation philosophy;
- footnote analysis;
- edition-independent rights assumptions;
- native-language scholarship.

## 22. Language balance is hierarchical—not proportional to file count

Training and retrieval sampling should select hierarchically, for example:

```text
capability or task
→ language or variety
→ corpus category
→ work or passage
→ edition or translation family
→ span
```

This prevents:

- English dominating because it has more scholarship;
- the New Testament dominating every ancient language because it has many translations;
- one translation family dominating because it appears on many sites;
- low-resource languages being oversampled through duplicate verse files;
- parallel data being counted as independent historical evidence.

Exact mixture weights remain an experiment-design decision under DR-17 and DR-18.

## 23. Continued pretraining must preserve multilingual capability

Every CPT stage reports held-out loss and downstream behavior by:

```text
language
variety
script
corpus class
text layer
modern interface role
ancient source role
```

General multilingual replay is required unless an approved experiment demonstrates that another strategy better preserves capability.

The evaluation must distinguish:

- improved domain modeling;
- catastrophic forgetting;
- cross-lingual interference;
- English over-specialization;
- ancient-language improvement that damages modern-language interaction;
- script and tokenizer regressions.

Cross-lingual continual-pretraining research supports replay as one mechanism for mitigating forgetting, but the project must measure the effect in its selected family and corpus.[^crosslingual-cpt]

## 24. Multilingual scholarly SFT uses three data classes

### Parallel behavior cases

The same scholarly operation is represented across several languages to measure and teach consistency.

### Native-language cases

Cases are authored in the target language and include language-specific:

- Bible translation traditions;
- terminology;
- reference conventions;
- scholarship;
- ambiguity;
- confessional and historical context;
- style and register.

Translated English cases cannot substitute for these.

### Cross-lingual research cases

Examples include:

```text
ask in Spanish
analyze Greek
retrieve English and French scholarship
quote German accurately
answer in Spanish
```

or:

```text
photograph an Italian Bible page
resolve the passage
compare the Greek source
produce English study notes
```

Research suggests that a relatively small but diverse multilingual instruction set can materially improve cross-lingual instruction following, but this does not eliminate the need for native evaluation.[^pinch]

## 25. Preference optimization is multilingual by behavior ontology

The preference corpus should represent the same approved behaviors across supported languages:

- citation integrity;
- exact passage-tool use;
- uncertainty;
- source-type distinctions;
- translation versus manuscript evidence;
- scope refusal and anti-over-refusal;
- sensitive-use behavior;
- concise versus scholarly depth;
- image uncertainty;
- no hidden pivot;
- correct answer-language retention.

The project may use unequal counts by language, but every claimed `FULL` or `BETA` language must cover the behavior ontology.

A preference pair translated automatically from English remains a candidate until native review.

## 26. Synthetic and translated training data remain candidates

Synthetic data may help fill multilingual gaps, but it must retain:

```text
source example
source language
translation model or human translator
prompt and decoding identity
pivot languages
review status
known errors
rights lineage
```

The system must not:

- treat machine-translated scholarship as the author's wording;
- turn a model translation into gold alignment automatically;
- create false native-language diversity by translating one English template repeatedly;
- obscure the fact that several examples share one English semantic source;
- use a teacher model's fluency as proof of scholarly correctness.

Native-language and cross-lingual cases should remain distinguishable in every report.

## 27. Model-generated Bible translations are bounded outputs

Biblical Scholar Lab may generate translation options for analysis, but they are labeled:

```text
MODEL_GENERATED_TRANSLATION_OPTION
```

They must identify:

- source edition and passage;
- source-language analysis;
- target language and variety;
- intended translation objective;
- ambiguities preserved or resolved;
- tradeoffs;
- model and run identity;
- human review state.

A generated option is not:

- a published translation;
- an approved church translation;
- a replacement for a translation committee;
- evidence of how a historical translation reads.

Professional translation workflow remains outside version-one claims.

## 28. Multimodal language architecture

Every page region may have its own:

```text
language
script
direction
edition or source identity
region type
OCR output
confidence
text-view mapping
```

The system must support pages containing:

- two or more translation columns;
- Greek or Hebrew with English notes;
- right-to-left scripture with left-to-right numbers and references;
- Latin-script transliteration beside source script;
- multilingual footnotes;
- user annotations in another language;
- mixed-language commentaries.

OCR and layout performance is benchmarked by language and script. An English page result cannot establish Hebrew, Arabic, Greek, Coptic, or mixed-direction capability.

Native device OCR may be combined with the multimodal foundation model, but every OCR path retains provenance and confidence.

## 29. Right-to-left and bidirectional text are correctness requirements

Hebrew, Aramaic in Hebrew script, Arabic, and mixed-direction citations require Unicode-conformant bidirectional handling.

The project will:

- store text in logical order;
- follow the Unicode Bidirectional Algorithm for display;
- prefer markup and layout controls over unnecessary embedded direction-control characters;
- isolate mixed-direction spans in the interface;
- test copied text, references, punctuation, footnotes, and code blocks;
- retain exact source controls where they are part of the acquired artifact;
- sanitize or visibly disclose suspicious controls in generated identifiers and interface fields.

Unicode UAX #9 specifies logical storage and display ordering for bidirectional text and warns that formatting controls can affect surrounding presentation.[^bidi]

## 30. Unicode confusables and mixed-script spoofing are security issues

Greek, Cyrillic, Latin, Hebrew, and other scripts can contain visually confusable characters. This creates risks for:

- source identifiers;
- DOI or URL display;
- manuscript sigla;
- usernames;
- tool calls;
- citation fields;
- model-generated file paths;
- benchmark labels.

The system should implement versioned Unicode confusable and mixed-script checks for security-sensitive identifiers while preserving exact scholarly text.

Confusable detection must not rewrite source quotations. It produces warnings or normalized security projections. Unicode UTS #39 distinguishes single-script, mixed-script, and whole-script confusables and supplies mechanisms for security checks.[^uts39]

## 31. Language-aware scope and sensitive-use behavior

DR-03 applies in every supported language.

A language is not `FULL` or `BETA` for user-facing operation unless it has:

- scope and refusal evaluation;
- crisis and imminent-danger evaluation;
- non-reinforcement tests for dangerous religious claims;
- localized response templates or verified generation behavior;
- current, region-appropriate resource resolution where applicable;
- anti-over-refusal tests for quoted scripture and ordinary religious speech.

Crisis resources may not be machine-translated from an English list without verification. Service names, hours, channels, eligibility, and jurisdiction remain current-resource records under DR-03.

## 32. Tool and service contracts are language-explicit

The runtime will require logical records such as:

```text
LanguageVarietyProfile
LanguageCapabilityProfile
LanguageInteractionContext
LanguageDetectionCandidate
MultilingualQueryPlan
RetrievalLanguageRoute
PivotTranslationRecord
DisplayTranslationRecord
LanguageAwareEvidencePacket
MultilingualAnswerContract
LanguageEvaluationReport
```

Every tool declares:

```text
accepted input languages
output languages
script support
transliteration behavior
locale assumptions
fallback behavior
confidence
rights behavior
version
```

A tool may not return English silently when a structured answer claims another language.

## 33. Multilingual answer contract

A multilingual answer records:

```text
requested answer language
actual answer language
language conformance result
source languages used
pivot languages used
quoted languages
translated spans and provenance
technical terms preserved or localized
citations and source-language access
unsupported-language warnings
```

The assistant should normally:

- answer in the user's requested language;
- preserve source-language quotations where material;
- explain technical terms accessibly in the answer language;
- offer transliteration as an aid rather than replacing source script;
- label its own translations;
- avoid gratuitous English terminology when established target-language terminology exists;
- retain internationally recognizable bibliographic identities.

It may use a source-language term directly where translation would obscure the issue, but it should explain that term in the user's language.

## 34. Benchmark case families

The multilingual benchmark must include:

### Parallel cases

The same underlying scholarly operation across languages, used to measure consistency and cross-language gaps.

### Native cases

Questions authored natively and grounded in language-specific translations, scholarship, terminology, or ambiguity.

### Cross-lingual evidence cases

The answer language differs from one or more evidence languages.

### Source-language explanation cases

Ancient text is analyzed and explained in several modern languages.

### Code-switch cases

The question, quotation, and requested answer intentionally cross languages.

### Script and orthography cases

Pointed and unpointed Hebrew, polytonic Greek, transliteration, right-to-left references, and mixed-script text.

### Multimodal cases

Pages, notes, footnotes, parallel columns, and OCR in the relevant scripts.

### Scope and safety cases

Language-specific refusal, anti-over-refusal, and crisis behavior.

### Translation-provenance traps

The model must identify published, ancient, human, model-generated, and pivot translations correctly.

### Language-drift cases

Retrieved evidence is dominated by another language and the model must retain the requested answer language.

## 35. Multilingual metrics

Reports must include at least:

```text
question-understanding accuracy
answer-language correctness
source-language fidelity
translation-provenance accuracy
reference-resolution accuracy
retrieval recall by evidence language
reranker language-bias analysis
citation entailment by language
quotation accuracy by language
Translation Nuance accuracy by language pair
cross-lingual synthesis quality
native-versus-translated-case gap
false-refusal rate by language
harmful-compliance rate by language
multimodal OCR/layout accuracy by script
code-switch handling
language-drift rate
calibration by language
latency and cost by language/tokenizer
```

The report must show:

- per-language results;
- per-capability results;
- worst-language and worst-group results;
- confidence intervals where appropriate;
- human-review disagreement;
- missing coverage.

No macro average may justify a support claim when a required language or safety capability fails.

## 36. Native human review is mandatory for product claims

A model judge may assist with triage but may not be the sole authority for a language-support claim.

Qualified reviewers should assess:

- naturalness and grammar;
- scholarly terminology;
- citation clarity;
- translation provenance;
- ambiguity preservation;
- perspective representation;
- refusal proportionality;
- safety and cultural appropriateness;
- OCR and page interpretation where relevant.

The review record identifies:

```text
reviewer language competence
native or near-native status
subject-matter expertise
methodological or confessional perspective where relevant
cases reviewed
agreement and disagreement
conflicts of interest
```

A native speaker without biblical or scholarly expertise and a biblical scholar without target-language competence provide different, complementary evidence.

## 37. Foundation-model bake-off requirements

DR-11's model-family bake-off must include:

- tokenizer efficiency by language, script, and text layer;
- exact Unicode and normalization behavior;
- closed-book and evidence-grounded multilingual tasks;
- answer-language retention under cross-lingual evidence;
- original-language analysis explained in modern languages;
- multilingual tool calling and structured output;
- multilingual page OCR and layout;
- cross-language citation fidelity;
- adaptation and quantization retention;
- cost and latency by language.

Vendor language-count claims are discovery inputs, not selection criteria.

A family can win the compact product role and lose the ancient-language or mobile role.

## 38. Quantization, distillation, and mobile deployment are language-sensitive

Every derivative model under DR-02-S03 and DR-29 must be evaluated for:

- rare Greek and Hebrew tokens;
- diacritics and cantillation;
- tool syntax;
- answer-language drift;
- multilingual citation formatting;
- cross-language retrieval use;
- right-to-left output;
- page OCR handoff;
- scope and safety behavior.

A quantized model may remain fluent in English while losing ancient-script fidelity or non-English calibration.

The preferred mobile architecture may use native OCR, local passage tools, and a smaller student model, but it remains subject to the same provenance and support-tier rules.

## 39. Fallback and escalation are explicit

When a language capability is insufficient, the system may:

```text
use deterministic tools only
retrieve exact passage text
provide a labeled provisional translation
switch to a larger approved model
invoke a language-specialist model
request a different answer language
request human review
abstain from the unsupported portion
```

It may not:

- pretend fluency;
- silently answer in English;
- fabricate scholarship in the target language;
- claim direct source analysis after using only a pivot;
- lower evidence standards for a low-resource language;
- make a high-stakes claim through an unvalidated language path.

The audit trace records every fallback.

## 40. Observability and reproducibility

Every multilingual invocation binds:

```text
language-profile revisions
locale and script profiles
model and tokenizer revisions
language-detection result
query translations
retrieval routes
reranker configuration
evidence languages
pivot translations
context composition
answer-language constraints
verifier results
support-tier policy
human or model review
```

This allows the project to reproduce why an answer in Spanish used an English article, a Greek passage, and a model-generated translation of a German quotation.

## 41. Hard failures

The following are hard failures when material:

- Claiming `FULL` or `BETA` support without native benchmark and human review.
- Treating modern Greek as proof of Koine Greek competence or Modern Hebrew as proof of Biblical Hebrew competence.
- Hiding an English or other pivot language.
- Attributing a model translation to the original author.
- Answering in the wrong language without disclosure.
- Treating a language tag as proof of actual model capability.
- Inferring language solely from script where alternatives are material.
- Letting one dominant language overwrite span-level code-switching.
- Using only English scholarship to claim global consensus.
- Counting parallel translations as independent evidence.
- Treating eBible verse alignment as phrase-level scholarly ground truth.
- Treating Targum's five-language depth as global multilingual coverage.
- Overweighting a language by file or translation-instance count.
- Using unreviewed machine translations as gold scholarly data.
- Losing source-language wording or ambiguity during context compression.
- Applying same-language preference so strongly that better evidence is suppressed.
- Allowing reranker language bias to remain unmeasured.
- Presenting a generated Bible translation as published or authoritative.
- Displaying mixed-direction text incorrectly in a way that changes references or quotations.
- Rewriting exact source text during confusable-character security checks.
- Using unverified translated crisis-resource information.
- Allowing aggregate performance to conceal a safety, citation, or language hard failure.
- Allowing Sol or Luna to add a language-support claim without approved evidence and owner approval.

## 42. Sol implementation boundary

### Sol may determine

Within the approved contracts, Sol may determine:

- module and package decomposition;
- equivalent local caching and batching;
- test implementation;
- implementation of standards adapters;
- performance optimizations proven semantically equivalent;
- source-specific adapters that preserve all required fields;
- family-specific hooks necessary to enforce the approved language contract.

### Sol may not determine

Sol may not independently alter:

- the separation of language roles;
- support-tier meanings;
- launch-language claims;
- no-hidden-pivot policy;
- native-review requirements;
- retrieval language objectives;
- source and translation provenance rules;
- corpus balancing principles;
- multilingual training or benchmark identity;
- right-to-left and Unicode-security invariants;
- safety-resource localization requirements;
- hard-failure definitions;
- experiment design or promotion decisions.

If an approved requirement is technically infeasible or materially changes cost, Sol returns:

```text
BLOCKED_REQUIRES_DESIGN_REVIEW
```

Luna may execute only frozen multilingual evaluation or training campaigns delegated by Sol. Luna may not change language mixtures, translation providers, answer-language constraints, support tiers, code, or experiment design.

## 43. Binding decisions

Approval of DR-13 would lock the following:

1. Biblical Scholar Lab is English-first but multilingual by design rather than through a later translation wrapper.
2. Source, question, answer, quotation, publication, retrieval, display, pivot, tool, and page-region languages remain distinct.
3. Language identity includes variety, period, dialect, script, orthography, register, and provenance where material.
4. BCP 47 and CLDR are versioned interoperability adapters, not permanent internal truth.
5. Language, script, orthography, locale, and transliteration remain separate entities.
6. Support is reported by capability rather than one global language label.
7. `FULL`, `BETA`, `CANARY`, `TRANSFER_ONLY`, `SOURCE_OR_EVIDENCE_ONLY`, `DISPLAY_ONLY`, `UNSUPPORTED`, and rights/resource-blocked states retain their approved meanings.
8. English remains the initial `FULL` target; Spanish and French remain initial `BETA` candidates subject to evidence.
9. Ancient source-language targets remain separate from modern interface-language tiers.
10. Explicit user answer-language choice has priority, and language drift is a measured failure.
11. Automatic language identification remains probabilistic and span-aware.
12. Code-switching and mixed-script sources are first-class.
13. English and other pivot translations must be recorded and disclosed where material.
14. Original, published, ancient, human, user, model, pivot, and paraphrase text remain distinct.
15. Retrieval combines same-language, source-language, cross-lingual, canonical, and translated-query routes under a recorded plan.
16. Same-language evidence is preferred for inspectability only when evidence quality is otherwise comparable.
17. English-only retrieval cannot establish global scholarly consensus.
18. Context composition and token budgets are language- and tokenizer-specific.
19. Targum supplies five-language translation-history depth; eBible supplies broad verse-aligned primary-text coverage; neither substitutes for the other or for native scholarship.
20. Corpus and training sampling remain hierarchical and lineage-aware rather than proportional to file count.
21. CPT must measure multilingual forgetting and interference and include approved preservation strategies.
22. Multilingual SFT contains parallel, native, and cross-lingual cases.
23. Preference training covers the same behavior ontology in every claimed language.
24. Synthetic and machine-translated data remain provenance-bearing candidates until reviewed.
25. Model-generated Bible translations remain bounded, labeled analytical outputs.
26. Multimodal OCR, layout, right-to-left, mixed-script, and code-switch behavior are evaluated per script and language.
27. Unicode bidi and confusable security are enforced without modifying authoritative source text.
28. Scope and sensitive-use behavior must be validated in every user-facing supported language.
29. Benchmark reports include per-language, per-capability, worst-group, language-drift, pivot, and native-versus-translated results.
30. Native or near-native human review is mandatory for product support claims.
31. Foundation-model, quantization, distillation, and mobile decisions include multilingual and ancient-script retention.
32. Unsupported-language fallback is explicit, auditable, and never silently presented as full capability.
33. Sol implements the approved multilingual architecture; ChatGPT designs and reviews experiments; Joseph Abbud approves support claims and consequential changes.
34. Luna may run only frozen multilingual campaigns delegated by Sol and may not alter language or experiment design.

## 44. Decisions intentionally deferred

DR-13 does not yet select:

- the final Spanish or French launch tier;
- the first non-Latin-script modern canary language;
- exact native-review panels;
- final language support thresholds;
- exact corpus mixture percentages;
- exact replay ratios;
- exact multilingual SFT and preference counts;
- the final machine-translation provider or model;
- whether any pivot translation may be cached;
- exact multilingual embedding and reranking models;
- exact language-detection implementation;
- exact script-security thresholds;
- final terminology glossaries;
- final localized citation styles;
- final locale-specific crisis-resource coverage;
- exact mobile language tiers;
- exact multilingual routing thresholds;
- final public language-support claims.

Those decisions belong to DR-14 through DR-25, DR-28, DR-29, and owner-approved experiment designs after the benchmark and reviewer resources are known.

## 45. Approved statement

> **Biblical Scholar Lab will be English-first but multilingual by architecture rather than through an untracked translation wrapper. Language variety, historical stage, script, orthography, locale, transliteration, source language, question language, answer language, quotation language, publication language, retrieval language, page-region language, display translation, and pivot translation will remain separate, versioned, provenance-bearing identities. BCP 47 and Unicode CLDR will provide versioned interoperability while opaque internal identities preserve historically and scholarly meaningful distinctions. Capability will be reported per language and task through evidence-gated support tiers; English will remain the initial full-support target, Spanish and French initial beta candidates, and ancient source-language competence will be evaluated independently from modern interface fluency. Retrieval will combine same-language, source-language, canonical, cross-lingual, and translated-query routes without allowing language preference or English bias to suppress materially stronger evidence. Every pivot, translation, multilingual context packet, training example, answer, quotation, citation, safety response, and multimodal page analysis will retain exact language and provenance. Targum and eBible will provide complementary depth and breadth without being treated as universal multilingual scholarship or phrase-level gold. Multilingual CPT, SFT, preference training, quantization, mobile deployment, and model selection will be evaluated for forgetting, interference, answer-language drift, ancient-script fidelity, citation support, scope, safety, and worst-group performance. Native-language cases and qualified human review will be mandatory for product-quality support claims, while unsupported language paths will fall back or abstain explicitly rather than pretending fluency or hiding an English pivot.**

---

## References

[^bcp47]: IETF, RFC 5646 / BCP 47, “Tags for Identifying Languages.” The standard defines language tags with language, script, region, variant, extension, and private-use subtags for interchange: https://www.rfc-editor.org/info/rfc5646/

[^cldr]: Unicode Consortium, Unicode Technical Standard #35, “Unicode Locale Data Markup Language.” LDML and CLDR define versioned language and locale identifiers, canonicalization, display names, formatting, collation, text boundaries, transforms, and validity data: https://unicode.org/reports/tr35/

[^bidi]: Unicode Consortium, Unicode Standard Annex #9, “Unicode Bidirectional Algorithm.” UAX #9 defines logical storage and display ordering for right-to-left and mixed-direction text and discusses explicit formatting controls: https://www.unicode.org/reports/tr9/

[^uts39]: Unicode Consortium, Unicode Technical Standard #39, “Unicode Security Mechanisms.” UTS #39 defines script-resolution and confusable-detection mechanisms relevant to mixed-script identifiers and spoofing: https://www.unicode.org/reports/tr39/

[^targum]: Maciej Rapacz and Aleksander Smywiński-Pohl, “Targum — A Multilingual New Testament Translation Corpus,” LREC 2026, and the public dataset card. The public release describes 651 collected translation instances, 334 unique editions, five European languages, and a 302-instance public subset while retaining original translation licenses: https://huggingface.co/datasets/mrapacz/targum-corpus

[^ebible]: BibleNLP, `BibleNLP/ebible`. The project describes a verse-aligned multilingual corpus derived from eBible.org, states that each source retains its original license, and notes that the normalized corpus contains verse text without introductions, comments, or footnotes: https://github.com/BibleNLP/ebible

[^pinch]: Uri Shaham et al., “Multilingual Instruction Tuning With Just a Pinch of Multilinguality,” Findings of ACL 2024. The study reports meaningful cross-lingual instruction-following gains from a small but diverse multilingual instruction subset, including unseen-language transfer: https://aclanthology.org/2024.findings-acl.136/

[^xrag]: Wei Liu et al., “XRAG: Cross-lingual Retrieval-Augmented Generation,” Findings of EMNLP 2025. The work reports answer-language correctness problems and difficulty reasoning over evidence whose language differs from the user query: https://aclanthology.org/2025.findings-emnlp.849/

[^bordirlines]: Bryan Li et al., “Multilingual Retrieval Augmented Generation for Culturally-Sensitive Tasks: A Benchmark for Cross-lingual Robustness,” Findings of ACL 2025. The benchmark finds that multilingual evidence can improve robustness while also exposing language-distribution and citation-use variation: https://aclanthology.org/2025.findings-acl.219/

[^crosslingual-cpt]: Wenzhen Zheng et al., “Breaking Language Barriers: Cross-Lingual Continual Pre-Training at Scale,” 2024. The study analyzes cross-lingual continued pretraining and reports data replay as an effective mitigation for forgetting in its experiments: https://arxiv.org/abs/2407.02118
