# DR-20 — Benchmark Charter

| Field | Value |
|---|---|
| Design ID | `DR-20` |
| Status | `APPROVED` |
| Approval date | 2026-08-16 |
| Project owner | Joseph Abbud |
| Designer and independent reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2 and supplements; DR-03; DR-04; DR-05; DR-06; DR-07; DR-08; DR-09; DR-10; DR-11; DR-12; DR-13; DR-14; DR-15; DR-16; DR-17; DR-18; DR-19 |
| Implementation authority | GPT-5.6 Sol, under the approved design |
| Execution authority | GPT-5.6 Luna only for frozen benchmark campaigns delegated by Sol under a later approved campaign envelope |
| Experiment-design authority | ChatGPT designs; Joseph Abbud approves; Sol implements only the approved design |
| Approved change | Establishes the authoritative benchmark-suite purpose, tracks, modes, case and evidence identities, public/private/fresh partitions, contamination firewall, expert-review tiers, benchmark-content authorship and approval authority, Sol implementation boundaries, baseline classes, multidimensional reporting, hard-failure policy, robustness families, lifecycle governance, and `MVP-01_EXPERT_COLLABORATION_PREVIEW` benchmark release contract; detailed annotation and scoring mechanics remain for DR-21 and execution framework details for DR-22 |

## 1. Purpose

Biblical Scholar Lab requires a benchmark before substantial model adaptation because the benchmark defines what improvement means.

Without a frozen evaluation contract, the project could:

- Optimize for Bible trivia rather than scholarly research behavior;
- Mistake verse memorization for textual understanding;
- Mistake fluent Greek or Hebrew terminology for correct analysis;
- Mistake a real citation for an entailed citation;
- Count translation agreement as manuscript evidence;
- Reward one theological tradition as an unmarked universal answer;
- Hide poor multilingual, multimodal, long-context, or safety behavior behind one average;
- Tune the model and retrieval system against the same cases used for the final claim;
- Change the benchmark after observing which tasks the chosen model performs well;
- Produce a high score that says little about whether a serious Bible learner or scholar would find the system useful.

DR-20 defines the benchmark’s constitutional purpose and scope.

It does **not** yet define every item, gold annotation, rubric weight, scorer implementation, judge prompt, numerical promotion threshold, model revision, or evaluation runtime. Those belong to DR-21, DR-22, DR-24, and approved benchmark-construction and experiment designs.

## 2. Governing principle

> **Biblical Scholar Lab will benchmark the specific scholarly operations, evidentiary distinctions, runtime behaviors, and failure modes required by the product contract—not generic biblical familiarity alone. Every result will remain conditional on the exact case, evidence mode, system configuration, language, modality, model, runtime, scorer, benchmark revision, and review state. A benchmark score is evidence about behavior under those conditions; it is not scholarly authority, theological truth, deployment certification, or proof that the system will behave identically outside the evaluated distribution.**

The benchmark is the examination.

The evaluation harness is the machinery that runs and scores the examination.

The model, retrieval system, deterministic tools, Runtime Scholar Harness, and full product system are different examinees or configurations.

## 3. One benchmark suite—not one question bank

The authoritative benchmark is a versioned suite:

```text
BiblicalScholarBenchmarkSuite
    → benchmark tracks
    → task families
    → case families
    → individual cases and variants
    → evidence modes
    → scoring contracts
    → review and split state
```

The suite may contain:

- Deterministically scored reference and quotation cases;
- Structured linguistic and Translation Nuance cases;
- Open-ended, rubric-scored research cases;
- Tool-use and retrieval trajectories;
- Multilingual and cross-lingual cases;
- Long-context and multi-turn cases;
- Multimodal page cases;
- Scope, safety, and sensitive-use cases;
- General-capability and capability-retention controls.

A single flat multiple-choice dataset cannot represent this product.

## 4. Internal name and public naming

The stable internal identity is:

```text
BSL_BENCHMARK_SUITE
```

The public benchmark name remains deferred.

`BibleBench` is already used by Rhema for an emerging benchmark that combines biblical-literacy tiers, LLM judges, and planned human scholarly review.[^biblebench] Biblical Scholar Lab will not create a confusingly similar public name or imply ownership of that initiative.

The public name must later pass:

- Prior-art and trademark search;
- Repository and package-name availability;
- Cross-language usability review;
- Expert-collaborator review;
- Owner approval.

## 5. Benchmark goals

The suite is intended to answer:

1. Can the system identify the exact text, edition, canon, and reference involved?
2. Can it analyze morphology, syntax, semantics, discourse, and referents without common word-study errors?
3. Can it diagnose **why** translations differ?
4. Can it distinguish textual witnesses, editions, ancient versions, modern translations, and commentary?
5. Can it use scholarship and citations at claim level?
6. Can it retrieve and synthesize appropriate evidence rather than merely repeat memorized knowledge?
7. Can it represent legitimate disagreement and make calibrated assessments?
8. Can it reason across languages without hiding pivots?
9. Can it understand printed pages without conflating scripture, notes, and annotations?
10. Can it use long context and compaction without losing decisive evidence or user corrections?
11. Can it answer legitimate Bible-study and supporting research tasks without harmful compliance or exaggerated refusal?
12. Does domain adaptation improve the complete system beyond an unchanged foundation model with the same tools and retrieval?
13. Are gains worth their compute, latency, memory, and operational cost?
14. Where does compact-model capacity cease to be sufficient?
15. Which cases require human scholarly judgment regardless of model size?

## 6. Benchmark non-goals

The suite is not designed to:

- Determine which religion or denomination is true;
- Rank Bible translations globally without a declared use criterion;
- Establish doctrinal orthodoxy as a single universal metric;
- Replace peer review or specialist scholarly judgment;
- Certify a model as a pastor, therapist, legal adviser, translator, or textual critic;
- Reward memorization of public questions;
- Measure only closed-book biblical trivia;
- Collapse model capability, retrieval quality, runtime quality, and tool quality into an uninterpretable number;
- Produce one permanent leaderboard that remains valid after public contamination or model advances;
- Treat benchmark performance as sufficient evidence for public deployment.

Product usefulness also requires user studies, expert workflow evaluation, incident review, and real-world monitoring beyond this benchmark.

## 7. Prior-art posture

Biblical Scholar Lab will reuse and compare with prior evaluations where appropriate, but no existing benchmark defines our success criteria.

### 7.1 Rhema BibleBench

BibleBench is an emerging public initiative centered on biblical literacy and tiered difficulty, with separate LLM-judge and planned human-scholar scores.[^biblebench]

It is relevant for:

- External biblical-literacy comparison;
- Human-versus-model judge analysis;
- Community contribution and tiering practices;
- Direct prior-art comparison with Rhema BibleAI.

It does not presently substitute for our evidence-graph, Translation Nuance, apparatus, multilingual, multimodal, runtime, and contamination contracts.

### 7.2 BIBLE

The BIBLE dataset contains 31,415 English multiple-choice records covering all 66 Protestant-canon books and several thematic categories. Its own dataset card warns that a significant portion was generated with NotebookLM and not manually reviewed for theological or factual accuracy.[^bible-dataset]

It may be used as:

- A broad, low-cost biblical-literacy screen;
- An error-discovery source after independent verification;
- A prior-art external result.

It may not become authoritative gold or the primary scholar-assistant benchmark without item-level rights and accuracy review.

### 7.3 FMG-Bench

FMG-Bench currently provides 120 English Christian theological and pastoral-adjacent base scenarios with perturbations and reports that a structured system layer improves model behavior. Its release also states that human calibration remains necessary before strong claims about judge validity or pastoral adequacy.[^fmg]

It is relevant to:

- Scope and sensitive-use behavior;
- Theological-triage prior art;
- System-layer versus raw-model comparisons;
- Perturbation and robustness design.

Its confessional and pastoral purpose differs from Biblical Scholar Lab’s evidence-first, multi-perspectival research contract.

### 7.4 Narrow biblical-language benchmarks

A 2025 Biblical Hebrew intertextual-parallel benchmark evaluates embedding models on known Samuel/Kings and Chronicles parallels.[^bh-parallel]

BibleNLP bitext-mining tasks in MTEB provide verse-aligned multilingual retrieval evaluation over hundreds of languages.[^mteb-bible]

These are valuable external controls for narrow capabilities. They do not establish complete scholar-assistant performance.

### 7.5 General benchmark-design lessons

The suite adopts several broader lessons:

- Instance-specific and atomic rubrics are more informative than one generic “helpful” score.[^biggen][^prbench]
- LLM judges vary substantially by task and must be calibrated against relevant human review before use as primary scorers.[^judgebench]
- Public benchmark content, paraphrases, and translations can contaminate model development even when exact string overlap is absent.[^rephrased]
- Public validation plus protected test material and fresh challenge sets can preserve some comparative value, although secrecy alone does not guarantee a durable benchmark.[^mmlucf][^saturation]
- Cluster-level worst-case reporting can reveal brittleness hidden by average accuracy.[^romqa]

## 8. Benchmark tracks

The suite contains the following first-class tracks.

### 8.1 `PRIMARY_TEXT_REFERENCE_AND_CANON`

Evaluates:

- Passage and work resolution;
- Canon and versification differences;
- Edition identity;
- Exact quotation;
- Missing, merged, split, or relocated verse slots;
- Localized reference parsing;
- Source versus paratext identity;
- Invalid and materially ambiguous references.

### 8.2 `LINGUISTIC_REPRESENTATION_AND_ANALYSIS`

Evaluates:

- Exact text views and Unicode handling;
- Segmentation and many-to-one word structures;
- Greek, Hebrew, and bounded Aramaic morphology;
- Alternative syntax;
- Lexical sense and semantic-role analysis;
- Referents and discourse;
- Accentuation, vocalization, cantillation, and ketiv/qere;
- Formal-versus-functional distinctions;
- Correction of named word-study fallacies.

### 8.3 `TRANSLATION_NUANCE`

This is the suite’s signature track.

It evaluates:

- Source-textual-state identification;
- Source/target span alignment;
- Translation-difference-unit identification;
- Multi-axis causal diagnosis;
- Upstream versus proximate cause;
- Textual variant versus translation choice;
- Target-language constraint;
- Ambiguity preservation or resolution;
- Translation and revision lineage;
- Ancient-version restraint;
- Interpretive effect versus translator intent;
- Evidence and counterevidence;
- Calibrated abstention where the cause remains underdetermined.

### 8.4 `ANCIENT_VERSIONS_AND_APPARATUS`

Evaluates:

- Version-tradition identity;
- Translation versus indirect-witness roles;
- Daughter-version dependence;
- Evidential distance;
- Apparatus scope, policy, and silence;
- Sigla and corrector identity;
- Conjecture versus attestation;
- Retroversion compatibility sets;
- Edition main text versus witness reading;
- Rights-constrained apparatus use.

### 8.5 `SCHOLARSHIP_CITATION_AND_LANDSCAPE`

Evaluates:

- Work/version/manifestation identity;
- Bibliographic correctness;
- Exact quotation and locator;
- Claim-level citation entailment;
- Primary versus secondary inspection;
- Metadata/abstract/full-text boundaries;
- Correction and retraction status;
- Source fitness;
- Methodology and perspective labeling;
- Source dependence;
- Dated, scoped scholarly-landscape assessment.

### 8.6 `ANCIENT_CONTEXT_AND_INTERTEXTUALITY`

Evaluates:

- Septuagint and Hebrew Bible relationships;
- Direct quotation, probable allusion, possible echo, thematic parallel, and coincidence;
- Second Temple Jewish context;
- Documentary Koine;
- Greek and Roman literary/historical context;
- Ancient Near Eastern contextual claims;
- Chronology, genre, geography, and evidential relevance;
- Anachronism and overgeneralization resistance.

### 8.7 `TOOLS_RETRIEVAL_AND_RUNTIME`

Evaluates the complete system’s ability to:

- Choose exact deterministic tools;
- Retrieve appropriate evidence;
- Ignore plausible distractors;
- Apply rights before access and display;
- Construct evidence packets;
- Assess sufficiency;
- Produce structured claims;
- Verify and repair unsupported output;
- Escalate or abstain;
- Preserve audit identity.

### 8.8 `LONG_CONTEXT_SESSION_AND_COMPACTION`

Evaluates:

- Passage, book, full-New-Testament, RAG, and hybrid modes;
- Position sensitivity;
- Cross-book and distributed evidence;
- Distractor density;
- Structured session continuity;
- `K0`–`K5` compaction behavior;
- User-correction retention;
- Counterevidence retention;
- Evidence-handle rehydration;
- Session drift and stale-state invalidation.

### 8.9 `MULTILINGUAL_AND_CROSS_LINGUAL`

Evaluates:

- Answer-language correctness;
- Ancient-source-language fidelity;
- Cross-language retrieval;
- Pivot disclosure;
- Original and translated quotation provenance;
- Native-language and translated-case gaps;
- Localized references and citation rendering;
- Code-switching and mixed scripts;
- Worst-language performance.

### 8.10 `MULTIMODAL_PAGE_STUDY`

Evaluates:

- Layout and reading order;
- OCR/ATR and VLM observations;
- Page and region identity;
- Scripture, headings, footnotes, cross-references, apparatus, commentary, and user annotations;
- Edition and passage resolution;
- Canonical lookup without overwriting visible evidence;
- Blur, skew, glare, crop, moiré, handwriting, and mixed scripts;
- Visual prompt injection;
- Page-grounded citations and research answers.

### 8.11 `SCOPE_SAFETY_AND_USER_AGENCY`

Evaluates:

- Core and supporting in-scope responses;
- Unrelated redirect precision;
- Anti-over-refusal;
- Harmful-application refusal;
- Crisis and escalation boundaries;
- Spiritual-authority restraint;
- Abuse and coercion;
- Medical and mental-health boundaries;
- Prophecy, possession, scrupulosity, and divine-command claims;
- Hate and dehumanization;
- User agency and correction.

### 8.12 `RESEARCH_WORKFLOW_AND_ACCESSIBILITY`

Evaluates whether the same verified evidence can support:

- Brief, Study, and Scholarly answers;
- Accessible explanations for non-specialists;
- Structured research notes;
- Source inspection and citation navigation;
- User-selected canon, translation, language, and methodological lens;
- A coherent multi-turn study workflow.

### 8.13 `GENERAL_AND_PARENT_RELATIVE_RETENTION`

This is a companion suite rather than a biblical-scholar score.

It evaluates whether training or quantization damages:

- General instruction following;
- Reasoning;
- Tool use;
- Multilingual behavior;
- General visual understanding;
- Long-context use;
- Safety and refusal calibration;
- Structured output;
- Mobile and quantized behavior.

## 9. Evaluation modes

Every case declares one or more approved modes.

```text
CLOSED_BOOK_MODEL
FIXED_PRIMARY_EVIDENCE
FIXED_COMPLETE_EVIDENCE_PACKET
DETERMINISTIC_TOOLS_ONLY
LIVE_RETRIEVAL
TOOLS_PLUS_RETRIEVAL
FULL_RUNTIME_HARNESS
FULL_CANON_CONTEXT
HYBRID_CANON_RAG
IMAGE_ONLY
IMAGE_PLUS_TOOLS
MULTI_TURN_SESSION
COMPACTED_SESSION
QUANTIZED_OR_MOBILE
HUMAN_REFERENCE
```

A score in one mode cannot be reported as though it measured another.

For example:

- `CLOSED_BOOK_MODEL` measures what the checkpoint can produce without retrieval.
- `FIXED_COMPLETE_EVIDENCE_PACKET` measures evidence interpretation under controlled input.
- `LIVE_RETRIEVAL` measures retriever plus model behavior.
- `FULL_RUNTIME_HARNESS` measures the product system.
- `IMAGE_ONLY` measures visual extraction without deterministic correction.
- `IMAGE_PLUS_TOOLS` measures the actual page-study architecture.

## 10. System identity and result identity

Every benchmark result binds:

```text
benchmark-suite revision
case and variant revision
split
scoring revision
model artifact bundle
runtime and provider
reasoning mode
system prompt and policy revision
tool and retrieval revisions
graph, corpus, and rights snapshots
context-composer and compaction policy
language and modality
precision or quantization
random seed and sampling
actual tool calls and evidence packet
latency, token usage, memory, and cost
```

A model name alone is not a result identity.

## 11. Canonical benchmark objects

The logical architecture includes:

```text
BenchmarkSuite
BenchmarkTrack
TaskFamily
CaseFamily
BenchmarkCase
CaseVariant
EvaluationMode
EvidenceContract
AnswerContract
RubricContract
ScorerContract
HumanReviewContract
SplitAssignment
ContaminationCluster
EvaluationRun
CaseResult
AggregateReport
BenchmarkRelease
BenchmarkIncident
```

DR-21 will specify the canonical schemas and atomic scoring representation.

## 12. Case-family architecture

A base scholarly problem may produce several related cases:

```text
same question in closed-book mode
same question with a fixed evidence packet
same question with distractors
same question in another language
same question with a false premise
same question after session compaction
same question from a page image
same question with one source unavailable
same question under a named tradition or method
```

Those variants form one `CaseFamily` and normally remain in the same split.

This architecture supports robustness without counting near-duplicate prompts as independent evidence.

## 13. Case formats

The suite may use:

```text
EXACT_ANSWER
SET_VALUED_ANSWER
MULTI_LABEL_CLASSIFICATION
SPAN_ALIGNMENT
STRUCTURED_GRAPH_OR_CHAIN
RANKED_OPTIONS
FREE_TEXT_ATOMIC_RUBRIC
TOOL_TRAJECTORY
RETRIEVAL_AND_EVIDENCE_SELECTION
PAIRWISE_COMPARISON
MULTI_TURN_TRAJECTORY
MULTIMODAL_REGION_AND_ANSWER
ABSTENTION_OR_ESCALATION
COUNTERFACTUAL_OR_METAMORPHIC
```

Multiple choice is permitted only when it fits the capability. It is not the default for nuanced scholarly tasks.

## 14. Evidence contracts

Every consequential case declares:

- What evidence is available;
- What evidence is required;
- What evidence is intentionally absent;
- Which sources are authoritative for deterministic fields;
- Which sources are counterevidence;
- Whether live retrieval is permitted;
- Which rights constrain display;
- What the model should do if evidence is insufficient;
- Whether the case tests memory, evidence use, retrieval, or the full system.

A candidate is not penalized for refusing to overclaim when the case deliberately withholds decisive evidence.

## 15. Answer contracts

A case may define:

```text
required conclusions
accepted alternative conclusions
required qualifications
required citations
required tool actions
required uncertainty
prohibited claims
prohibited source confusions
hard failures
acceptable abstention conditions
answer-depth mode
```

For disputed cases, the benchmark can accept several analyses while penalizing unsupported overclaims.

The gold is therefore often a structured boundary of defensible behavior—not one exact prose paragraph.

Gold answers and rubrics may require concise rationale, evidence mapping, intermediate structured outputs, and tool traces. They do not require the evaluated model or human reviewer to expose private chain-of-thought.

## 16. Review partitions

DR-19’s review partitions govern benchmark authority.

### `REV-P0_DETERMINISTIC_AND_OPERATIONAL`

Suitable for exact, mechanically or policy-verifiable cases.

### `REV-P1_SOURCE_VERIFIABLE_SCHOLARLY_BEHAVIOR`

Suitable for source-verifiable epistemic discipline that does not require a subtle specialist adjudication.

### `REV-P2_SPECIALIST_SCHOLARLY_JUDGMENT`

Requires task-matched human subject-matter review before the case may become authoritative specialist gold or final promotion evidence.

A case can move from `REV-P1` to `REV-P2` when review reveals hidden specialist ambiguity.

Owner approval and ChatGPT methodology review remain necessary governance steps but never substitute for `SME_REVIEWED`.

## 17. Case-construction sources

Cases may originate from:

```text
expert-authored research questions
real user workflows with consent and privacy controls
source-derived deterministic transformations
published scholarly disputes
documented model failures
runtime incidents
translation-family comparisons
controlled linguistic minimal pairs
adversarial false premises
synthetic page renderings
licensed real page captures
multilingual native-authored cases
prior-art benchmark adapters
model-generated candidates
```

Model-generated cases remain candidates and require the appropriate source, methodology, rights, and human review.

The system must record who authored or generated each case and which evidence was used.

### Benchmark-design and benchmark-content authority

Benchmark design is experiment design. Accordingly:

- **ChatGPT is the benchmark designer and primary benchmark-content author.** ChatGPT defines the constructs, case-selection strategy, individual prompts, evidence requirements, answer boundaries, accepted alternatives, required uncertainty, prohibited claims, semantic rubrics, distractor intent, case-family relationships, contamination clusters, split recommendations, and fresh challenge cases.
- **Joseph Abbud is the project owner and final benchmark approver.** Owner approval determines whether a proposed case batch, revision, split, benchmark version, public claim, or release may advance.
- **Qualification-matched human subject-matter experts validate specialist content.** `REV-P2` prompts, diagnoses, gold records, and rubrics remain `SME_REVIEW_PENDING` until reviewed by appropriately qualified humans. ChatGPT methodology review and owner approval are necessary but are never relabeled as SME validation.
- **GPT-5.6 Sol implements benchmark machinery but does not author benchmark meaning.** Sol may implement schemas, editors, validators, deterministic renderers, loaders, scorers, access controls, reports, and approved variant generators. Sol may not independently select passages, formulate semantic questions, choose evidence, author or rewrite gold answers, determine accepted scholarly analyses, create semantic distractors, assign case families or contamination clusters, set private/fresh partitions, or alter rubric meaning.
- **Luna executes only frozen benchmark campaigns.** Luna has no case-authoring, scoring-design, adjudication, or benchmark-interpretation authority.

The default benchmark-content workflow is:

```text
ChatGPT case blueprint
    → bounded case batch, normally 10–25 cases
    → source and methodology verification
    → Joseph editorial/product review and approval
    → deterministic validation
    → SME review where required
    → immutable content hash and split assignment
    → Sol implementation in the approved schema and harness
```

Sol may mechanically instantiate or render variants only when the complete source set, transformation policy, randomization bounds, seed policy, gold derivation, split relationship, and scoring semantics were approved in advance. Examples include seeded page degradations, option-order shuffles, localized reference renderings, or schema-preserving perturbations. Mechanical generation does not authorize Sol to choose what capability is tested or what constitutes a correct scholarly response.

If Sol finds ambiguity, contradiction, missing evidence, impossible scoring semantics, or a materially better proposed case design, it must stop with:

```text
BLOCKED_REQUIRES_BENCHMARK_DESIGN_REVIEW
```

It may report the defect and recommend alternatives, but it may not repair benchmark content on its own. Every case record will preserve the design author, owner approval, source-verification state, ChatGPT methodology-review state, SME-review state, deterministic-validation state, rights evidence, and exact content hash.

## 18. Difficulty and complexity are multidimensional

The suite will not use one vague “easy/hard” label.

Each case may be profiled along:

```text
source specialization
evidence breadth
number of evidence hops
logical nesting
linguistic specialization
textual-critical ambiguity
translation-causal ambiguity
scholarly disagreement
retrieval difficulty
context length
position sensitivity
language distance
modality and degradation
session-state dependence
currentness
safety sensitivity
answer openness
```

A basic factual question can be obscure but not reason-intensive. A familiar passage can require expert Translation Nuance analysis.

## 19. Benchmark partitions

The approved logical partitions are:

```text
DEV_PUBLIC
PUBLIC_REPRODUCTION
PRIVATE_DEVELOPMENT_AUDIT
PRIVATE_MODEL_SELECTION
PRIVATE_FINAL
FRESH_POST_FREEZE_CHALLENGE
SME_COLLABORATION_CANDIDATE
INCIDENT_REGRESSION
RETIRED_OR_SUPERSEDED
```

### `DEV_PUBLIC`

Visible examples used for implementation, documentation, scorer development, and contributor guidance.

### `PUBLIC_REPRODUCTION`

A stable public subset used for reproducible system comparisons and the collaboration preview.

### `PRIVATE_MODEL_SELECTION`

Protected cases used for model-family, training-stage, and checkpoint decisions before final evaluation.

### `PRIVATE_FINAL`

Protected cases used only under the final approved evaluation protocol. They may not select ordinary checkpoints or tune prompts.

### `FRESH_POST_FREEZE_CHALLENGE`

New cases created after the model, prompt, retrieval, and training decisions are frozen. This provides the strongest project-level protection against our own overfitting.

### `SME_COLLABORATION_CANDIDATE`

Provisional `REV-P2` cases published or shared specifically to recruit and organize qualified review.

## 20. Split assignment follows relationship clusters

Cases are assigned to splits through the relationship graph, not row-by-row randomness.

Clusters may include:

- The same passage;
- Translation families;
- Edition lineages;
- Witness groups;
- Quotation and paraphrase families;
- Shared scholarly arguments;
- Synthetic templates;
- Page layouts and source images;
- Language translations;
- Multi-turn variants;
- Shared evidence packets;
- Model-generated derivation families.

Material relatives must remain together or be excluded.

## 21. Contamination accounting

The project distinguishes:

```text
UNKNOWN_BASE_MODEL_EXPOSURE
PUBLIC_BENCHMARK_EXPOSURE
PROJECT_PROMPT_DEVELOPMENT_EXPOSURE
PROJECT_RETRIEVAL_EXPOSURE
PROJECT_TRAINING_EXPOSURE
SYNTHETIC_DERIVATIVE_EXPOSURE
PRIVATE_SELECTION
PRIVATE_FINAL
FRESH_POST_FREEZE
```

We cannot prove that vendor models never saw biblical texts or public scholarship.

We can guarantee that private and fresh project cases do not enter:

- Corpus materialization;
- SFT or preference generation;
- Training retrieval;
- Prompt optimization;
- Mixture optimization;
- Public CI;
- Luna training campaigns;
- Model-generated case synthesis.

Paraphrase, translation, and semantic relationship checks supplement exact string matching because simple rewording can conceal benchmark overlap.[^rephrased]

## 22. Private benchmark security

Private cases and rubrics remain in DR-10’s protected zones.

Access requires:

- Named role;
- Purpose;
- Expiration;
- Least privilege;
- Immutable audit;
- No access by training or synthesis agents;
- No export to unauthorized providers;
- No inclusion in public logs or handoffs.

The public repository contains hashes, schemas, aggregate coverage, and public-safe examples—not the private content.

## 23. Fresh challenge construction

The fresh challenge set is created after:

- Model family and checkpoint are frozen;
- Main training and preference stages are complete;
- System prompt and runtime policy are frozen;
- Retrieval configuration is frozen;
- Primary scorer configuration is frozen.

Fresh cases should emphasize:

- Newly authored expert or source-verifiable questions;
- New page layouts and captures;
- New translation-family combinations;
- New adversarial perturbations;
- New scholarly publications where currentness is part of the task;
- Failure classes observed during development but not copied directly from training cases.

A fresh challenge set is a one-time examination. Once used for public development, it becomes public exposure and a later fresh set is required.

## 24. Baseline classes

The suite will compare at least:

```text
foundation model alone
foundation model + fixed system policy
foundation model + exact tools
foundation model + RAG
foundation model + tools + RAG
complete A0 Runtime Scholar Harness
full-New-Testament context variants
trained checkpoint without runtime
trained checkpoint with full runtime
compact versus large-capacity route
preference adapter off versus on
quantized/mobile derivative versus parent
reproducible Bible-specific prior-art systems
frontier-model ceiling
qualified human reference subset
```

Exact model revisions belong to DR-22 and individual evaluation runs.

## 25. Model scores and system scores remain separate

The project will report:

```text
MODEL_ONLY_SCORECARD
EVIDENCE_INTERPRETATION_SCORECARD
RETRIEVAL_SCORECARD
RUNTIME_SYSTEM_SCORECARD
END_TO_END_PRODUCT_SCORECARD
```

A weak model can be improved by tools. A strong model can be damaged by poor retrieval. The benchmark must reveal which component produced the result.

## 26. Scoring hierarchy

The scoring priority is:

1. Deterministic verification where possible.
2. Exact structured comparison against accepted sets or graphs.
3. Atomic, case-specific rubrics.
4. Qualification-matched human review.
5. Calibrated model-assisted scoring only after meta-evaluation.

LLM-as-judge may assist scale and triage but cannot be presumed reliable across biblical languages, textual criticism, theology, safety, or multimodal evidence. Large cross-task studies show that judge reliability varies by property, dataset, and required expertise.[^judgebench]

DR-21 will define the scorer and meta-evaluation contracts.

## 27. Atomic criteria and partial credit

Open-ended cases should be scored through atomic criteria such as:

```text
identified correct source edition
recognized that no textual variant is involved
parsed the relevant form correctly
represented both defensible syntactic analyses
cited the supporting source span
avoided an unsupported consensus claim
preserved the counterevidence
stated the remaining uncertainty
```

Each criterion has:

- A type;
- Weight or severity;
- Evidence requirement;
- Accepted realizations;
- Disallowed shortcuts;
- Review authority;
- Scorer type.

High-weight critical criteria cannot be offset by many low-value stylistic points. Expert rubric benchmarks in other professional domains show why fine-grained criteria reveal failures hidden by overall answer quality.[^prbench]

## 28. No single authoritative aggregate

The primary report is a dashboard, not one score.

It must show:

- Per-track performance;
- Per-mode performance;
- Per-language and script;
- Per-modality;
- Per-review partition;
- Per-assurance class;
- Hard-failure counts;
- Worst-group and cluster performance;
- Abstention and calibration;
- Cost, latency, and memory;
- Human disagreement;
- Missing coverage.

A composite index may be generated for internal regression tracking only if:

- Its weights are transparent;
- All component results remain visible;
- Hard-failure caps apply;
- It is not treated as scholarly authority;
- It cannot authorize promotion by itself.

The first public collaboration preview should not launch a competitive single-score leaderboard.


### 28.1 Statistical and repeated-run reporting

The benchmark must distinguish item count from independent evidence count.

Statistical analysis should use the case family, passage cluster, translation lineage, source family, page-template family, or other appropriate dependency cluster as the resampling and comparison unit rather than treating every perturbation as independent.

Reports should include, where applicable:

```text
number of cases and independent clusters
number of completed and failed runs
paired performance deltas
confidence intervals
bootstrap or permutation procedure
stochastic run count
between-run variance
reviewer variance
practical effect size
multiple-comparison policy
missing-data and timeout treatment
```

Nondeterministic model, retrieval, routing, or tool configurations require repeated runs when one execution would not support a stable conclusion. A statistically detectable change that does not repair the named capability or exceeds the approved cost is not automatically a meaningful gain.

## 29. Hard failures and severity caps

Hard failures from DR-02 through DR-19 remain visible regardless of aggregate score.

Examples include:

- Fabricated text, manuscript, source, quotation, or page;
- Citation that does not support the claim;
- Modern translations counted as manuscript witnesses;
- Study notes presented as scripture;
- Certain retroversion from underdetermined evidence;
- Hidden pivot translation;
- Unmarked doctrinal default;
- Harmful spiritual-authority claim;
- Private or restricted evidence leakage;
- Loss of a user correction through compaction;
- Claiming visual inspection of an omitted or illegible region.

A severe failure may cap a case, track, system, or release disposition even when other criteria pass.

## 30. Calibration and abstention

The suite measures whether the system:

- Knows when the evidence is insufficient;
- Distinguishes unknown, contested, and unsupported;
- Abstains only from the unsupported portion;
- Avoids excessive hedging when evidence is strong;
- Escalates appropriately;
- Preserves confidence differences across claim components.

Metrics may include:

```text
selective accuracy
coverage-risk curve
abstention precision and recall
unsupported-certainty rate
over-hedging rate
confidence calibration by task class
```

User-facing numerical confidence is not required.

## 31. Robustness and metamorphic case families

Each major track should include controlled variants testing whether the answer changes appropriately when:

- The edition changes;
- A textual variant is added or removed;
- One piece of counterevidence is withheld;
- The user applies pressure;
- The prompt is paraphrased;
- The order of evidence changes;
- A source is retracted or rights-blocked;
- The answer language changes;
- The page is photographed rather than digitally rendered;
- The session is compacted;
- A false premise is introduced;
- The named theological or methodological lens changes.

The expected invariant or change must be explicit.

Cluster-level worst-case reporting is required so that one easy variant cannot hide a brittle failure on another.[^romqa]

## 32. Long-context evaluation

Long-context cases vary:

- Input length;
- Evidence location;
- Distractor count;
- Multi-hop depth;
- Full-book versus full-New-Testament context;
- RAG versus full-context versus hybrid route;
- Compaction and rehydration;
- Question position;
- Output and tool budget.

The suite reports task-effective context rather than merely whether the runtime accepted the prompt.

## 33. Multilingual evaluation

Every claimed interface language receives:

- Native-authored cases;
- Parallel cases;
- Cross-lingual evidence cases;
- Pivot-disclosure cases;
- Citation and quotation cases;
- Scope and safety cases;
- Answer-language drift measurement.

Ancient-language competence is reported separately from modern answer fluency.

Macro averages must not conceal the worst language, script, or language pair.

## 34. Multimodal evaluation

Page cases preserve exact source images, region selectors, recognition alternatives, and page evidence packets.

The suite separates:

- OCR/layout performance;
- VLM-only performance;
- Canonical lookup;
- Page evidence reconciliation;
- Page-grounded scholarly answer quality;
- Prompt-injection resistance;
- Privacy and rights behavior.

Synthetic pages and real physical captures remain separate reporting strata.

## 35. Scope and sensitive-use evaluation

The suite must measure both:

```text
harmful compliance
false refusal
```

Cases include:

- Legitimate controversial biblical analysis;
- Supporting research coding;
- Quoted violent or self-harm language;
- Present crisis disclosure;
- Spiritual abuse;
- Claimed divine commands;
- Scrupulosity;
- Medical treatment refusal;
- Hate and extremist proof-texting;
- Ordinary devotional reflection;
- Unrelated general-assistant work.

The benchmark may adapt external safety cases, but must preserve this domain-specific distinction.

## 36. Efficiency and cost

Every system run records:

- Input and output tokens;
- Reasoning-token or effort setting where available;
- Tool calls;
- Retrieved bytes or passages;
- Context length;
- Model route;
- Latency;
- Throughput;
- Peak memory;
- GPU or API cost;
- Cache and compaction use;
- Retry and failure cost.

The project reports:

```text
quality per dollar
quality per second
cost per verified answer
cost per successful hard case
compact-to-large escalation rate
```

Cost never overrides hard evidence, rights, or safety requirements.

## 37. Benchmark validity gates

Before a benchmark revision governs model promotion, it must demonstrate:

1. **Content validity:** tracks map to approved product capabilities and failures.
2. **Construct validity:** cases measure the intended capability rather than formatting, memory, or shortcuts.
3. **Scorer validity:** automatic and model-assisted scoring agrees sufficiently with the relevant human or deterministic authority.
4. **Discrimination:** the suite separates known stronger and weaker systems without immediate saturation.
5. **Reliability:** reruns and reviewer judgments remain acceptably stable.
6. **Coverage:** important languages, modes, difficulty axes, and hard failures are represented.
7. **Contamination control:** project-induced leakage is blocked and public exposure is disclosed.
8. **Fairness of comparison:** model, system, tool, context, reasoning, and cost conditions are explicit.
9. **Rights and privacy:** every case and evidence packet is authorized for its operation.
10. **Interpretability:** aggregate results can be traced to cases, criteria, and evidence.

A benchmark that fails these gates remains developmental and cannot authorize a main training conclusion.

## 38. Human reference performance

Human evaluation should include several relevant reference groups where feasible:

```text
serious Bible learner
seminary or graduate student
pastor or teacher
qualified domain specialist
```

The purpose is not to rank humans against machines as one homogeneous group.

Human results help establish:

- Case clarity;
- Difficulty;
- Expert disagreement;
- Time requirements;
- Whether the rubric rewards real scholarship;
- Whether the system saves research effort.

`REV-P2` human reference work must use qualification-matched reviewers.

## 39. Judge and scorer meta-evaluation

Every model-assisted scorer receives a separate meta-benchmark containing:

- Citation errors;
- Source-type confusion;
- Subtle Translation Nuance errors;
- Legitimate plural answers;
- False-refusal cases;
- Overconfident but fluent answers;
- Multilingual and translated answers;
- Page-grounding errors;
- Length and formatting biases.

The judge is compared with the relevant deterministic and human labels.

A judge that performs well on generic helpfulness but fails source entailment cannot score that track.

## 40. Benchmark lifecycle and versioning

Every release uses semantic benchmark versioning.

```text
MAJOR: construct, track, split, or scoring change that breaks comparability
MINOR: new cases or nonbreaking track expansion
PATCH: corrected metadata, wording, or scorer bug with documented impact
```

Every release records:

- Cases added, removed, corrected, or retired;
- Split changes;
- Rubric and scorer changes;
- Baseline reruns;
- Known contamination;
- Human-calibration status;
- Comparability with prior versions.

A corrected gold label does not silently rewrite historical results.

## 41. Benchmark incidents and corrections

An incident may involve:

- Incorrect gold;
- Ambiguous prompt;
- Rights issue;
- Leakage;
- Broken scorer;
- Judge bias;
- Unsupported SME claim;
- Duplicate or dependent cases;
- Private-case exposure;
- Security or privacy problem.

The project must:

1. Freeze affected use.
2. Preserve the original case and evidence.
3. Assess downstream runs and claims.
4. Correct, retire, or reclassify the case.
5. Version the benchmark.
6. Rerun affected baselines where material.
7. Publish an incident note where the result was public.

## 42. Contribution and expert-collaboration governance

A contributor submits:

- The proposed question or task;
- Intended track and mode;
- Source and rights evidence;
- Expected answer boundary;
- Material alternatives;
- Required qualifications;
- Potential conflicts;
- Whether the case may be public.

The project records authorship, review, adjudication, and attribution.

Community submission does not guarantee inclusion. A community or expert submission remains a candidate. ChatGPT evaluates and, where appropriate, rewrites it into the approved benchmark contract; Joseph approves inclusion; and qualification-matched experts validate specialist content. The original submission and all material transformations remain attributable.

Expert contributors should be able to review bounded case sets in their actual specialty rather than being asked to endorse the whole benchmark. No contributor, Sol implementation turn, automated generator, or model judge may bypass the approved benchmark-design workflow.

## 43. Relationship to training

The benchmark does not become training data merely because it is public.

The project may create separate training examples targeting the same **capability ontology**, but not copy private questions, gold rationales, evidence packets, or case-family variants.

Training data and benchmark data must remain linked only through abstract capability labels and separately reviewed source materials.

A model may be trained on public external benchmarks only in a separately disclosed experiment. It cannot then be evaluated on those same items as an uncontaminated result.

## 44. External benchmark adapters

DR-22 may implement adapters for:

- BibleBench;
- BIBLE;
- FMG-Bench;
- Biblical Hebrew intertextuality;
- BibleNLP/MTEB bitext retrieval;
- General long-context, safety, multimodal, instruction-following, and retention evaluations.

External results remain separate scorecards. They do not alter the internal benchmark ontology or gold.

## 45. `MVP-01_EXPERT_COLLABORATION_PREVIEW` benchmark release

The collaboration preview may publish:

- A `DEV_PUBLIC` subset;
- A stable `PUBLIC_REPRODUCTION` subset centered on `REV-P0` and reviewed `REV-P1`;
- Benchmark and evaluation cards;
- Baseline system comparisons;
- Public-safe model outputs and error analyses;
- Candidate `REV-P2` cases labeled `SME_REVIEW_PENDING`;
- Contribution instructions and specialty queues.

It must not publish:

- Private selection or final cases;
- Fresh challenge material before use;
- Restricted evidence;
- Unreviewed specialist gold;
- A single leaderboard score implying scholar-level authority.

The preview’s success criterion is that qualified readers can inspect the benchmark’s seriousness, reproduce the public results, identify its limitations, and see exactly where their expertise would improve it.

## 46. Benchmark release artifacts

Every release receives:

```text
benchmark card
suite and track manifests
case and variant manifests
review-state summary
rights and privacy manifest
split and contamination report
scorer and judge card
human-calibration report
baseline results
hard-failure report
known limitations
changelog
reproduction instructions
content hashes
```

Public and private release artifacts remain separate.

## 47. Sol implementation authority

Sol may implement:

- Benchmark schemas and validators;
- Case-authoring, source-review, and adjudication tooling;
- Exact storage of ChatGPT-authored and owner-approved benchmark records;
- Deterministic generators and variants whose complete source set, transformation policy, seed rules, gold derivation, family relationship, and scoring semantics were approved in advance;
- Split and contamination controls;
- Public/private storage boundaries;
- Deterministic scorers;
- Rubric execution;
- Evaluation adapters;
- Reporting and visualization;
- External benchmark adapters;
- Design-neutral performance optimizations.

Sol may not independently author, select, rewrite, label, semantically score, partition, or materially modify:

- Benchmark questions, prompts, or user scenarios;
- Source passages, evidence packets, or decisive evidence selection;
- Required conclusions, accepted alternatives, required uncertainty, or prohibited claims;
- Gold answers, gold structures, semantic rubrics, criterion meaning, or difficulty intent;
- Translation Nuance diagnoses, linguistic judgments, textual-critical conclusions, or scholarly-landscape labels;
- Semantic distractors or adversarial false premises;
- Case-family membership, contamination clusters, private/fresh assignments, or fresh challenge cases;
- The benchmark tracks;
- Evaluation modes;
- Review partitions;
- Split and contamination policy;
- Case authority;
- Hard failures;
- Scoring hierarchy;
- Public/private release policy;
- Baseline classes;
- Benchmark claims;
- Promotion use.

Sol must preserve the approved content byte-for-byte except for explicitly authorized serialization, escaping, or deterministic rendering. A material limitation, ambiguity, or proposed semantic change returns:

```text
BLOCKED_REQUIRES_BENCHMARK_DESIGN_REVIEW
```

## 48. Luna execution authority

Luna may, only within a frozen campaign delegated by Sol:

- Verify benchmark, model, runtime, scorer, and split hashes;
- Launch approved evaluation runs;
- Monitor execution, latency, utilization, and cost;
- Resume exact approved runs;
- Collect logs and artifacts;
- Stop at approved limits;
- Verify cloud shutdown;
- Return objective execution evidence to Sol.

Luna may not:

- Author or edit cases;
- See private content outside its exact execution grant;
- Change prompts, scorers, models, tools, evidence, splits, or thresholds;
- Interpret results;
- Adjudicate cases;
- Decide benchmark validity or promotion;
- Release results.

## 49. Principal hard failures

DR-20 treats the following as hard failures:

- Designing the benchmark after observing the trained model’s strengths.
- Using private or fresh cases for training, prompt tuning, retrieval tuning, or case synthesis.
- Random row or verse splitting across related cases.
- Treating Bible trivia as the complete scholar benchmark.
- Treating one exact answer as gold where several analyses are defensible.
- Treating LLM judgment as expert validation without track-specific calibration.
- Hiding hard failures inside one aggregate score.
- Scoring model-only and full-system conditions as though they were identical.
- Changing evidence availability without changing the evaluation mode or case revision.
- Publishing restricted evidence or private benchmark content.
- Treating modern translation frequency as scholarly or textual consensus.
- Using public benchmark performance to claim uncontaminated closed-book knowledge without qualification.
- Claiming multilingual, multimodal, long-context, or safety capability from English text-only averages.
- Allowing an easy case-family variant to hide a failure on a material adversarial variant.
- Correcting gold or scorer behavior without benchmark versioning and impact analysis.
- Allowing Sol or Luna to define benchmark success or reinterpret failed gates.

## 50. Binding decisions

Approval of DR-20 would lock:

1. The benchmark is a versioned suite, not one flat dataset.
2. Benchmark and evaluation harness remain separate artifacts.
3. The internal identity is `BSL_BENCHMARK_SUITE`; the public name remains deferred because BibleBench is already in use.
4. Translation Nuance is the signature track.
5. Primary text, linguistics, ancient versions, scholarship, context, runtime, long context, multilingual, multimodal, safety, workflow, and retention are separate tracks.
6. Model-only, fixed-evidence, tools, RAG, full-runtime, full-canon, multimodal, multi-turn, and mobile modes remain separate.
7. Every result binds exact benchmark, model, runtime, evidence, scorer, language, modality, precision, and cost identities.
8. Case families preserve related variants and normally remain in one split.
9. Cases may use exact, set-valued, structured, rubric, trajectory, multimodal, and abstention formats.
10. Consequential cases declare evidence and answer contracts.
11. `REV-P0`, `REV-P1`, and `REV-P2` review authority applies to benchmark gold.
12. Case difficulty is multidimensional.
13. Public development, public reproduction, private selection, private final, fresh challenge, SME candidate, incident, and retired partitions remain separate.
14. Split assignment follows relationship clusters rather than rows.
15. Project-induced leakage is prohibited and semantic contamination is audited.
16. Private benchmark access is least-privilege and unavailable to training and synthesis agents.
17. A fresh post-freeze challenge set is mandatory for final claims.
18. Model, retrieval, runtime, product, prior-art, frontier, and human reference configurations remain distinguishable.
19. Model and system scorecards remain separate.
20. Deterministic scoring is preferred; atomic rubrics and qualified human review govern open-ended cases.
21. LLM judges require track-specific meta-evaluation and cannot replace SME review.
22. No single aggregate may hide track, language, modality, review-state, or hard-failure results.
23. Severe failures may cap promotion regardless of average score.
24. Calibration, abstention, robustness, position sensitivity, multilingual, multimodal, safety, and efficiency are first-class metrics.
25. Benchmark validity requires content, construct, scorer, discrimination, reliability, coverage, contamination, comparison, rights, and interpretability gates.
26. Human reference performance is qualification-stratified.
27. Benchmark releases are versioned and corrected through incident procedures.
28. Community and expert contributions remain reviewed, attributable, and bounded by specialty.
29. Benchmark cases remain outside training except under a separately disclosed contaminated experiment.
30. External benchmarks are adapters and separate scorecards.
31. The collaboration preview publishes only public-safe `REV-P0`/`REV-P1` benchmark material and provisional `REV-P2` collaboration candidates.
32. The initial preview does not launch a single-score scholar leaderboard.
33. ChatGPT has exclusive benchmark-design and primary benchmark-content authority, subject to Joseph Abbud's review and approval and qualification-matched SME validation where required.
34. Joseph Abbud retains final authority over case batches, benchmark revisions, split use, promotion use, public claims, and release.
35. Sol may implement schemas, tools, deterministic generators, scorers, harnesses, and reports, but may not independently author or materially alter benchmark prompts, evidence, gold, rubrics, semantic distractors, case families, contamination clusters, private/fresh assignments, or fresh challenge cases.
36. Sol-generated variants are permitted only under a fully approved deterministic generation contract and remain members of the approved case family.
37. Every case records design authorship, owner approval, source and methodology review, deterministic validation, SME status, rights evidence, and content hash.
38. Benchmark-content defects or proposed semantic changes stop with `BLOCKED_REQUIRES_BENCHMARK_DESIGN_REVIEW`.
39. Luna only executes frozen evaluation campaigns and has no benchmark-content or scoring-design authority.

## 51. Decisions intentionally deferred

DR-20 does not yet select:

- The public benchmark name;
- Exact v0.1 case count;
- Exact cases and gold annotations;
- Exact track weights;
- Exact difficulty thresholds;
- Exact rubric schema and criterion weights;
- Exact deterministic scorer implementations;
- Exact LLM judge models and prompts;
- Exact human-review panel and compensation;
- Exact inter-rater thresholds;
- Exact private/fresh proportions;
- Exact numerical promotion thresholds;
- Exact baseline model revisions;
- Exact external benchmark versions;
- Exact leaderboard policy after the collaboration preview;
- Exact storage and execution framework.

Those belong to DR-21, DR-22, DR-24, DR-28, the benchmark-construction plan, and individual approved evaluation experiments.

## 52. Approved statement

> **Biblical Scholar Lab will use a versioned, multidimensional benchmark suite that evaluates the scholarly operations, evidentiary distinctions, runtime behaviors, and hard failures required by the approved product rather than treating biblical trivia, fluency, or one aggregate score as sufficient evidence of capability. The internal `BSL_BENCHMARK_SUITE` will remain distinct from its evaluation harness and will contain separate tracks for primary text and canon, linguistic analysis, Translation Nuance, ancient versions and apparatuses, scholarship and citations, ancient context and intertextuality, tools and retrieval, long context and compaction, multilingual and cross-lingual behavior, multimodal page study, scope and safety, research workflow, and parent-relative retention. Every case will bind an exact task family, review state, evidence and answer contract, evaluation mode, source and rights snapshot, language, modality, contamination cluster, scoring contract, and system identity. Model-only, fixed-evidence, deterministic-tool, live-retrieval, full-runtime, full-canon, multimodal, multi-turn, compacted-session, and mobile conditions will remain separate scorecards. Related passages, translations, lineages, paraphrases, languages, page templates, evidence packets, and perturbations will remain in case families and relationship-cluster splits rather than being randomized as independent rows. Public development and reproduction material, private model-selection and final material, fresh post-freeze challenges, provisional SME collaboration cases, incident regressions, and retired cases will remain physically and logically separated, with private and fresh content inaccessible to training, synthetic generation, prompt optimization, retrieval tuning, and ordinary agents. Deterministic verification will govern exact claims; structured answers, accepted alternatives, atomic case-specific rubrics, qualification-matched human review, and calibrated model-assisted scoring will govern open-ended tasks; LLM judges will require track-specific meta-evaluation and will never substitute for subject-matter expert review. Reports will expose per-track, per-mode, per-language, per-modality, per-review-partition, worst-group, calibration, abstention, hard-failure, latency, memory, and cost results, while severe evidence, citation, source-type, rights, safety, multilingual, multimodal, or compaction failures may cap promotion regardless of averages. Benchmark validity will require content, construct, scorer, discrimination, reliability, coverage, contamination, comparison, rights, and interpretability evidence; corrections and exposure will create versioned incidents rather than silent gold changes. Prior benchmarks such as BibleBench, BIBLE, FMG-Bench, biblical-language tasks, and general retention evaluations will remain external adapters and separate scorecards. `MVP-01_EXPERT_COLLABORATION_PREVIEW` may release reproducible public `REV-P0` and reviewed `REV-P1` cases and clearly provisional `REV-P2` collaboration candidates, but no private holdout, restricted evidence, unreviewed specialist gold, or single-score scholar-authority leaderboard. ChatGPT will retain exclusive benchmark-design and primary benchmark-content authority, including prompts, evidence contracts, gold boundaries, semantic rubrics, distractor intent, case families, contamination clusters, split recommendations, and fresh challenge cases; Joseph Abbud will review and approve every consequential case batch, benchmark version, promotion use, public claim, and release; and qualification-matched human experts will validate `REV-P2` specialist content. Sol will implement only the approved schemas, tools, deterministic generators, scorers, harnesses, access controls, and reports and will stop with `BLOCKED_REQUIRES_BENCHMARK_DESIGN_REVIEW` rather than independently altering benchmark meaning. Luna may execute only frozen evaluation campaigns delegated by Sol and will have no benchmark-content, scoring-design, adjudication, or interpretation authority.**

---

## References

[^biblebench]: Rhema, “BibleBench — A benchmark for biblical literacy, built by The Church,” 2026. The public project describes tiered questions, four independent LLM judges, planned human judges across Christian traditions, and separate machine and human scores: <https://biblebench.vercel.app/>.

[^bible-dataset]: MushroomGecko, “BIBLE: Biblically Informed Bot Learning Evaluation,” Hugging Face dataset card, accessed August 2026. The card reports 31,415 multiple-choice rows and warns that a substantial portion was generated through NotebookLM and not manually reviewed for theological or factual accuracy: <https://huggingface.co/datasets/MushroomGecko/BIBLE>.

[^fmg]: Alex Chao, “When AI Is Your Pastor: A Benchmark for LLM Theological Triage and Pastoral Guidance,” Fide AI technical report and FMG-Bench v1 dataset, 2026. The release describes 120 base scenarios, perturbation variants, structured system-condition comparisons, and a requirement for human calibration before strong claims: <https://fideai.org/research/fmg-bench/> and <https://huggingface.co/datasets/FideAI/fmg-bench>.

[^bh-parallel]: David M. Smiley, “Intertextual Parallel Detection in Biblical Hebrew: A Transformer-Based Benchmark,” 2025. The benchmark evaluates embedding methods on known parallels between Samuel/Kings and Chronicles: <https://arxiv.org/abs/2506.24117>.

[^mteb-bible]: MTEB, “BibleNLPBitextMining,” based on the eBible corpus. The current benchmark adapter contains verse-aligned partial Bible translations across hundreds of languages for bitext-mining evaluation: <https://huggingface.co/datasets/mteb/biblenlp-corpus-mmteb>.

[^biggen]: Seungone Kim et al., “The BiGGen Bench: A Principled Benchmark for Fine-grained Evaluation of Language Models with Language Models,” NAACL 2025. The benchmark uses instance-specific criteria across 77 tasks and nine capabilities: <https://aclanthology.org/2025.naacl-long.303/>.

[^prbench]: Afra Feyza Akyürek et al., “PRBench: Large-Scale Expert Rubrics for Evaluating High-Stakes Professional Reasoning,” 2025. PRBench uses expert-authored open-ended tasks and fine-grained expert criteria, illustrating why overall prose quality can hide critical professional failures: <https://arxiv.org/abs/2511.11562>.

[^judgebench]: Anna Bavaresco et al., “LLMs instead of Human Judges? A Large Scale Empirical Study across 20 NLP Evaluation Tasks,” ACL 2025. The study reports substantial variability by evaluated property, dataset, expertise level, and text source and recommends validation against human judgments: <https://aclanthology.org/2025.acl-short.20/>.

[^rephrased]: Shuo Yang et al., “Rethinking Benchmark and Contamination for Language Models with Rephrased Samples,” 2023. The study shows that paraphrases and translations can bypass simple string-overlap decontamination and advocates fresh one-time examinations: <https://arxiv.org/abs/2311.04850>.

[^mmlucf]: Qihao Zhao et al., “MMLU-CF: A Contamination-free Multi-task Language Understanding Benchmark,” ACL 2025. MMLU-CF provides a public validation set and closed test set and reports changed performance and rankings relative to the original MMLU: <https://aclanthology.org/2025.acl-long.656/>.

[^saturation]: Mubashara Akhtar et al., “When AI Benchmarks Plateau: A Systematic Study of Benchmark Saturation,” 2026. The study analyzes saturation across 60 LLM benchmarks and reports that expert-curated benchmarks resist saturation better than crowdsourced benchmarks, while hidden test data alone is not sufficient protection: <https://arxiv.org/abs/2602.16763>.

[^romqa]: Victor Zhong et al., “RoMQA: A Benchmark for Robust, Multi-evidence, Multi-answer Question Answering,” EMNLP Findings 2023. RoMQA evaluates robustness within clusters of related questions and reports worst-case cluster performance: <https://aclanthology.org/2023.findings-emnlp.470/>.
