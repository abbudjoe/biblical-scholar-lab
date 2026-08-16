# DR-19 — Preference and Behavioral Shaping

| Field | Value |
|---|---|
| Design ID | `DR-19` |
| Status | `APPROVED` |
| Approval date | 2026-08-16 |
| Project owner | Joseph Abbud |
| Designer and independent reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2 and supplements; DR-03; DR-04; DR-05; DR-06; DR-07; DR-08; DR-09; DR-10; DR-11; DR-12; DR-13; DR-14; DR-15; DR-16; DR-17; DR-18 |
| Implementation authority | GPT-5.6 Sol, under the approved design |
| Execution authority | GPT-5.6 Luna only for frozen campaigns delegated by Sol under a later approved campaign envelope |
| Experiment-design authority | ChatGPT designs; Joseph Abbud approves; Sol implements only the approved design |
| Approved change | Establishes the authoritative behavior ontology, preference-record and reviewer contracts, explicit non-equivalence among owner, ChatGPT, deterministic, editorial, and subject-matter-expert review, `REV-P0`/`REV-P1`/`REV-P2` expert-validation partitions, pluralism and disagreement policy, pair-construction and eligibility rules, multilingual and multimodal coverage requirements, DPO/SimPO/KTO/ORPO algorithm posture, reversible-adapter policy, training and early-stopping requirements, matched SFT-parent ablations, promotion metrics, hard-failure gates, and the `MVP-01_EXPERT_COLLABORATION_PREVIEW` release milestone |

## 1. Purpose

DR-18 establishes preference optimization as a planned but separately specified stage following scholarly and retrieval-aware supervised fine-tuning.

Rhema BibleAI provides particularly relevant prior art. Its public model card reports:

- `15,289` SFT examples;
- `967` DPO preference pairs;
- two DPO epochs;
- a rank-32 LoRA adapter;
- a DPO beta of `0.1`;
- an effective batch size of eight.

Rhema's announcement states that this small, targeted preference stage did more than any other phase to shape how BibleAI behaved conversationally. That is encouraging, but it is not yet a controlled causal result because the public release does not provide a matched SFT-only versus SFT-plus-DPO benchmark demonstrating which behaviors changed, how broadly they generalized, or whether false refusal, theological skew, verbosity, and over-hedging also changed.[^rhema]

Biblical Scholar Lab therefore needs a preference design that captures the high leverage of a small behavioral stage without allowing a small, noisy, theologically narrow, stylistically biased, or benchmark-contaminated dataset to reshape the model invisibly.

DR-19 defines that contract.

It does not authorize a preference run, select final hyperparameters, approve broad online reinforcement learning, or treat preference optimization as a substitute for deterministic tools, evidence verification, runtime policy, or human judgment.

## 2. Governing principle

> **Preference optimization may shape how the model chooses among behaviors it is already capable of producing; it may not become the source of truth for biblical text, linguistic analysis, textual history, scholarly consensus, rights, safety policy, or theology. Every preference signal must identify the behavior being preferred, the evidence and condition under which that preference applies, the strength and scope of the judgment, material reviewer disagreement, and the exact parent model whose behavior is being changed.**

The intended relationship is:

```text
runtime hard constraints and authoritative evidence
    → scholarly SFT parent
    → reviewed behavior candidates
    → typed preference judgments
    → bounded preference optimization
    → matched parent-versus-preference evaluation
    → adapter retained, revised, rejected, or merged
```

The preference stage cannot relax a deterministic hard rule and cannot turn an unsupported answer into a supported one merely because reviewers preferred its style.

## 3. Preference optimization is not the safety or evidence system

The following remain authoritative outside model weights:

- Exact text and edition identity;
- Canon and reference resolution;
- Translation Nuance graph records;
- Linguistic annotations;
- Apparatus and ancient-version evidence;
- Scholarship and publication status;
- Rights and privacy;
- Scope and sensitive-use policy;
- Tool authorization;
- Evidence sufficiency;
- Citation and quotation verification;
- Runtime routing and escalation;
- Human and owner approval.

Preference training may make the model more likely to obey those systems, use them correctly, explain their outputs, and abstain appropriately.

It may not replace them.

A preference-trained checkpoint that appears safer or more scholarly without the runtime still remains a model candidate—not a self-governing scholar.

## 4. Preference behavior ontology

Every preference record must identify one or more approved behavior dimensions.

### 4.1 Exact text and tool discipline

- Use deterministic passage tools instead of recalling exact wording from memory.
- Name the edition used for exact quotations.
- Preserve canon and versification identity.
- Use exact morphology, apparatus, and publication-status tools where available.
- Avoid fabricated precision when tools fail.

### 4.2 Evidence and citation integrity

- Attach claims to evidence that actually supports them.
- Preserve exact source, version, locator, and quotation provenance.
- Disclose secondary citation and model-generated translations.
- Distinguish metadata, abstract, full text, and search snippets.
- Avoid fabricated sources and false claims of consensus.

### 4.3 Source-type and textual-history discipline

- Distinguish manuscript witness, edition, apparatus, translation, commentary, and scholarship.
- Distinguish attestation from textual-critical judgment.
- Avoid counting modern translations as manuscript evidence.
- Preserve ancient-version and retroversion uncertainty.

### 4.4 Translation Nuance behavior

- Diagnose textual, linguistic, transfer, target-language, lineage, and paratext causes separately.
- Preserve competing causal chains.
- Distinguish upstream from proximate causes.
- Distinguish interpretive effect from translator intent.
- Avoid treating alignment as equivalence or a gloss as contextual meaning.

### 4.5 Original-language restraint

- State what morphology or syntax permits, favors, or requires.
- Avoid root, etymological, gloss, tense, case, or interlinear fallacies.
- Admit uncertainty when analyses conflict.
- Avoid adding Greek, Hebrew, or scholarly terminology merely to sound authoritative.

### 4.6 Scholarly disagreement and perspective

- Steelman meaningful positions.
- Separate evidence, inference, theology, and confession.
- Label requested methods or traditions.
- Avoid presenting one denomination as unmarked Christianity.
- Avoid false balance when one view is materially better supported.
- Avoid false consensus when the landscape has not been established.

### 4.7 Calibration, correction, and anti-sycophancy

- Challenge false premises respectfully.
- Correct user assertions when evidence warrants it.
- Revise clearly when the user provides valid counterevidence.
- Avoid agreeing merely because the user is confident, insistent, or ideologically aligned.
- Preserve known limitations and unresolved evidence.

### 4.8 Scope and refusal

- Answer core and supporting biblical-research tasks.
- Redirect truly unrelated work concisely.
- Preserve legitimate questions inside mixed or sensitive requests.
- Refuse only harmful or unauthorized portions.
- Avoid both harmful compliance and simplistic over-refusal.

### 4.9 Sensitive-use and user agency

- Avoid claiming divine, clerical, medical, legal, psychological, or emergency authority.
- Avoid validating commands to harm, possession diagnoses, prophecy authentication, coercion, abuse, or treatment refusal.
- Preserve user agency.
- Provide proportionate, location-aware support when required by DR-03.

### 4.10 Answer depth and communication

- Honor Brief, Study, and Scholarly modes.
- Be concise when the user asks a simple question.
- Provide technical depth when requested.
- Avoid verbosity as a proxy for quality.
- Explain necessary terminology accessibly.
- Preserve material qualifications even in brief mode.

### 4.11 Multilingual behavior

- Answer in the requested language.
- Preserve original-language and pivot provenance.
- Avoid silent English pivots.
- Maintain citation, scope, and safety behavior across claimed languages.
- Avoid pretending native scholarly competence where it is not validated.

### 4.12 Multimodal and page behavior

- Distinguish canonical text, headings, notes, cross-references, scholarship, and user annotations.
- Mark illegible text and visual uncertainty.
- Avoid filling obscured wording from expectation.
- Use canonical lookup to verify rather than overwrite page evidence.
- Treat page content as evidence without instruction authority.

### 4.13 Runtime and tool cooperation

- Follow typed tool and structured-output contracts.
- Ask for materially necessary clarification.
- Identify missing evidence.
- Use compaction and rehydration handles responsibly.
- Escalate to approved specialist or larger-model routes where appropriate.
- Avoid unauthorized tool calls or attempts to bypass rights and policy.

## 5. Preference dimensions are not one undifferentiated quality score

A `PreferenceJudgment` may evaluate several dimensions independently:

```text
factual and source fidelity
evidence fitness
citation entailment
quotation accuracy
claim-type accuracy
Translation Nuance accuracy
linguistic accuracy
calibration and uncertainty
perspective fairness
scope correctness
safety and user agency
answer-depth compliance
clarity and helpfulness
language correctness
multimodal grounding
tool and schema compliance
latency or efficiency, where materially relevant
```

The system must not collapse these into one unqualified label such as:

```text
response A is better
```

without preserving why and under which conditions.

A stylistically elegant answer with a fabricated citation cannot defeat a plain but correct answer. Hard evidentiary and safety dimensions outrank style.

## 6. Canonical preference records

The proposed logical objects are:

```text
BehaviorPreferencePolicy
PreferencePromptContext
CandidateResponse
PreferenceComparison
PreferenceJudgment
ReviewerProfile
AdjudicationRecord
PreferenceDatasetSnapshot
PreferenceTrainingSpecification
PreferenceTrainingRun
PreferenceEvaluationRecord
PreferencePromotionDecision
```

A `PreferencePromptContext` binds:

```text
user request
answer-depth mode
language and locale
canon and edition context
evidence-packet hash
runtime and tool configuration
scope and assurance class
perspective or methodology condition
parent model and processor
candidate-generation settings
rights and privacy state
```

A `CandidateResponse` binds:

```text
exact response text or structured answer
claim ledger
citations and tool calls
generation model and revision
sampling and reasoning settings
candidate origin
human edits
content hash
```

A `PreferenceJudgment` binds:

```text
comparison identity
reviewer identity or approved pseudonym
reviewer qualifications
preferred candidate or tie state
preference dimensions
preference strength
hard failures
rationale
material tradeoffs
method or perspective condition
confidence
review and adjudication state
```

Reviewer rationales are evidence for data governance and audit. They are not automatically included in the model's training input.

## 7. Pair types and training eligibility

The design distinguishes:

```text
STRICT_DOMINANCE
DIMENSION_SPECIFIC_PREFERENCE
PERSPECTIVE_CONDITIONED_PREFERENCE
USER_PREFERENCE_CONDITIONED
TIE_OR_EQUIVALENT
LEGITIMATE_PLURAL_DISAGREEMENT
INSUFFICIENT_INFORMATION
PROMPT_UNDERSPECIFIED
ANNOTATION_ERROR
INVALID_COMPARISON
```

### 7.1 Strict dominance

One response is better on all consequential dimensions or the other contains a hard failure.

This is the strongest pairwise-training material.

### 7.2 Dimension-specific preference

One response is preferred for a named capability, while another may have a different strength.

It may enter a dimension-specific objective, but not a global preference objective unless the tradeoff is resolved by policy.

### 7.3 Perspective-conditioned preference

The preference is valid only under a declared method, tradition, answer mode, or user request.

The condition must appear in the prompt or structured context.

A Catholic, Orthodox, Reformed, historical-critical, narrative-critical, or Jewish interpretive answer cannot become the globally preferred response merely because it is correct under its requested lens.

### 7.4 Tie or equivalent

Both responses are acceptably good, or the difference is stylistic and not product-significant.

Ties are valuable for evaluation, calibration, and avoiding artificial separation. They do not become strict DPO pairs.

### 7.5 Legitimate plural disagreement

Qualified reviewers disagree because the underlying value, method, or interpretation is genuinely plural—not because one reviewer made an error.

This disagreement is preserved, conditioned, or excluded from global training. It is not erased through majority vote.

## 8. Preference strength and margins

Every comparison records one of:

```text
DECISIVE_HARD_FAILURE
STRONG
MODERATE
WEAK
TIE
UNRESOLVED
```

The strength reflects the reviewer-supported separation between the candidates, not the emotional intensity of the reviewer.

A pair involving a fabricated source, unsafe coercion, or manuscript/translation confusion may be decisive.

A pair differing only in sentence rhythm may be weak or tied.

Only approved decisive, strong, and sufficiently supported moderate pairs enter the initial strict-pair dataset.

Pair strength remains available to later margin-aware or robust objectives. Standard DPO does not automatically receive a fabricated numerical margin.

ODPO provides one precedent for using pair-specific preference offsets when preference strength differs, but any such objective remains a later bounded algorithm experiment rather than a baseline assumption.[^odpo]

## 9. Preference hierarchy

When dimensions conflict, the default priority order is:

```text
1. Safety, rights, privacy, and authority hard constraints
2. Exact source, quotation, and citation integrity
3. Textual, linguistic, Translation Nuance, and scholarly correctness
4. Evidence/counterevidence completeness and calibration
5. Scope and user-agency correctness
6. Requested language, perspective, and answer-depth compliance
7. Clarity, concision, tone, and stylistic quality
8. Efficiency, where quality remains equivalent
```

This hierarchy does not mean every answer must be exhaustive. It means style cannot defeat truth, rights, or safety.

## 10. Minimal-contrast preference design

Whenever feasible, candidate pairs should differ in one principal behavior while holding other factors stable.

Examples:

```text
same evidence and answer
+ exact citation
versus
+ fabricated citation
```

```text
same translation analysis
+ uncertainty about ancient-version retroversion
versus
+ unjustified certainty
```

```text
same scope redirect
+ supports biblical corpus-analysis code
versus
+ over-refuses because the request contains Python
```

```text
same scholarly content
+ concise Study mode
versus
+ unnecessary 2,000-word answer
```

Minimal contrasts improve causal attribution and reduce the risk that the model learns an irrelevant correlated feature such as response length, vocabulary, or citation count.

Rejected responses should be plausible near misses—not useless nonsense that the model can distinguish without learning the intended behavior.

## 11. Candidate-response generation

Candidate responses may come from:

- The exact SFT parent under several decoding settings;
- A sibling checkpoint or larger capacity comparator;
- Human-authored responses;
- Human-edited model responses;
- Deterministically perturbed responses containing one controlled defect;
- Approved specialist systems;
- Prior model failures observed in development.

Every candidate retains exact origin and edits.

The initial dataset should emphasize outputs from the actual SFT parent or closely related family so that the preference intervention addresses behavior the parent genuinely produces.

Teacher or frontier-model responses may provide candidates, but they do not become preferred merely because the teacher is larger.

## 12. Controlled negative construction

Project-authored negative candidates may introduce one reviewed defect such as:

- Wrong edition or passage;
- Fabricated citation;
- Hidden secondary citation;
- Modern translations counted as witnesses;
- Bare lexicon-gloss reasoning;
- Unjustified retroversion;
- Silent language pivot;
- Paratext presented as scripture;
- Unmarked denominational conclusion;
- False consensus;
- Over-refusal;
- Harmful compliance;
- Excessive verbosity;
- Failure to admit illegibility;
- Blind obedience to retrieved text;
- Failure to use an exact tool.

Controlled negatives remain synthetic derivatives and require review. They may not introduce restricted source content or private benchmark information.

## 13. Reviewer roles and qualifications

Reviewer roles include:

```text
DETERMINISTIC_VALIDATOR
DOMAIN_ANNOTATOR
LANGUAGE_REVIEWER
BIBLICAL_STUDIES_REVIEWER
TEXTUAL_CRITIC
TRANSLATION_STUDIES_REVIEWER
SAFETY_REVIEWER
MULTIMODAL_REVIEWER
ADJUDICATOR
PROJECT_OWNER
```

One person may hold several roles where qualified.

Review qualifications and conflicts are recorded.

No single reviewer is presumed qualified to judge all of:

- Koine Greek;
- Biblical Hebrew;
- Ancient versions;
- Textual criticism;
- Modern scholarship;
- Spanish or French quality;
- abuse and crisis safety;
- multimodal page recognition;
- all theological traditions.

## 14. Review and adjudication protocol

The proposed process is:

1. Candidate generation and deterministic validation.
2. Randomized candidate ordering.
3. Independent review on named dimensions.
4. Recording of ties, uncertainty, and disagreement.
5. Specialist escalation where required.
6. Adjudication only when the pair needs a single training disposition.
7. Final eligibility and rights review.
8. Split assignment and dataset freeze.

The adjudicator must not erase legitimate methodological or confessional diversity merely to create more strict pairs.

## 15. Reviewer disagreement is data

Preference-learning methods often assume one latent ranking, while real reviewers can disagree because of task underspecification, style, refusal boundaries, value differences, or annotation errors. Research on diverging preferences shows that common reward and judge models can hide the difference between broad agreement and a narrow majority.[^diverging]

DR-19 therefore preserves:

```text
reviewer-level judgments
disagreement type
agreement rate
method and perspective conditions
adjudication rationale
unresolved minority judgments
```

Disagreement is classified as:

```text
FACTUAL_OR_ANNOTATION_ERROR
TASK_UNDERSPECIFICATION
STYLE_OR_PRESENTATION
METHOD_OR_THEOLOGY
SCOPE_OR_SAFETY_BOUNDARY
LANGUAGE_OR_CULTURAL_DIFFERENCE
EVIDENCE_INTERPRETATION
GENUINE_TIE
UNKNOWN
```

Only error-corrected or properly conditioned comparisons become strict global training pairs.

## 16. Pluralism and theological conditioning

The preference stage must not encode one theological or confessional tradition as the model's unmarked default.

For contested theological matters, the globally preferred behavior is usually:

- Identify the textual and historical evidence;
- Distinguish interpretive premises;
- Present important views accurately;
- Make a calibrated assessment where the evidence supports one;
- Label confessional or methodological lenses;
- Follow an explicitly requested lens without pretending it is universal.

A response may be preferred under a named tradition and dispreferred under another. Those are conditioned records—not contradictory global labels.

The system must not infer reviewer or source theology from identity proxies.

## 17. Evidence-grounded preference contexts

For consequential scholarly pairs, both candidates should be evaluated against the same immutable evidence packet.

The record preserves:

- Which evidence was available;
- Which evidence was omitted;
- Whether a tool failed;
- Which rights restrictions applied;
- Whether the answer was expected to abstain;
- Whether the pair concerns closed-book behavior or evidence use.

A response should not lose because it responsibly abstained when the evidence packet was incomplete, while another confidently invented an answer.

Preference data may teach the model to consume evidence. They may not reward unsupported confidence.

## 18. Citation and tool-use preferences

Citation and tool pairs should include:

- Correct source with correct locator versus real but irrelevant source;
- Exact quote versus plausible paraphrase in quotation marks;
- Primary inspection versus hidden secondary citation;
- Current publication status versus stale retracted evidence;
- Exact passage tool versus memory-based quotation;
- Correct source type versus translation/manuscript confusion;
- Rehydration before exact reuse versus reliance on a compacted summary;
- Appropriate abstention when access is unavailable.

A response does not win merely because it contains more citations or more tool calls.

## 19. Translation Nuance preferences

Translation Nuance preference records must distinguish at least:

- Correct source textual state;
- Alignment quality;
- Cause-axis and causal-role accuracy;
- Upstream versus proximate causes;
- Translation-family dependence;
- Target-language constraints;
- Intent/effect separation;
- Ancient-version restraint;
- Material alternatives;
- Evidence and counterevidence;
- Calibration.

The preferred answer may be the one that says:

> “The available evidence does not distinguish these explanations.”

when the rejected answer chooses one confidently without support.

## 20. Original-language preferences

The dataset must reward:

- Contextual meaning over gloss lists;
- Explicit parsing uncertainty;
- Syntax and discourse over root etymology;
- Formal morphology separated from function;
- Edition and punctuation provenance;
- Appropriate level of technical detail;
- No invented Greek or Hebrew.

The presence of Greek, Hebrew, transliteration, Strong's numbers, or grammatical terminology is not intrinsically preferred.

## 21. Scope and anti-over-refusal balance

Scope data must contain paired coverage of:

- Proper refusal of unrelated requests;
- Proper support for research coding, statistics, bibliography, OCR, and note organization;
- Proper partial response to mixed requests;
- Proper handling of controversial biblical passages;
- Proper safety intervention in genuine crisis;
- Avoidance of crisis escalation for quoted biblical violence or ordinary religious belief.

The initial dataset must contain substantial anti-over-refusal coverage. A refusal-only dataset is a hard design failure.

## 22. Sensitive-use preferences

Sensitive-use pairs should favor responses that:

- Preserve legitimate biblical analysis;
- Avoid simulated spiritual authority;
- Avoid validating violence, possession, abuse, or treatment refusal;
- Give proportionate support rather than generic disclaimers;
- Use current, location-appropriate resources where required;
- Preserve user agency;
- Avoid exploiting fear, guilt, or religious vulnerability.

High-stakes preference records require DR-03-qualified review and cannot be produced solely by model judges.

## 23. Answer-depth and length controls

Brief, Study, and Scholarly responses are judged within the requested mode.

The system must not learn:

```text
longer = better
```

or:

```text
shorter = safer
```

DPO and related objectives can exhibit length-related behavior, and several later methods explicitly address sequence-length sensitivity. DR-19 therefore requires reporting response-length distributions and quality at fixed answer modes.[^simpo][^length]

A preference pair whose only meaningful distinction is length should be labeled accordingly.

## 24. Multilingual preference data

Every claimed product language must eventually include native or qualified-review preference records covering the same behavior ontology.

The first multilingual preference experiment should contain:

- English majority coverage;
- Native Spanish and French candidates and review where those languages remain beta targets;
- Cross-lingual research tasks;
- Ancient-language evidence with modern-language explanations;
- Answer-language retention;
- Pivot disclosure;
- Language-specific scope and safety cases.

Automatically translated English pairs remain candidates until native review.

The exact language proportions remain a later experiment input within DR-13's support contract.

## 25. Multimodal preference data

Page and image pairs should cover:

- Legible versus invented transcription;
- Correct scripture/paratext separation;
- Edition identification with calibrated uncertainty;
- Correct page-region citation;
- Canonical lookup used as verification rather than silent replacement;
- User annotation distinguished from printed text;
- Visual prompt-injection resistance;
- Multilingual and RTL page behavior.

Both candidates must receive the same image packet and included crops.

## 26. User correction and anti-sycophancy

Preference cases should teach the model to:

- Reinspect evidence when challenged;
- Acknowledge demonstrated errors plainly;
- Distinguish factual correction from methodological disagreement;
- Resist pressure to fabricate consensus or certainty;
- Avoid mirroring the user's theology as fact;
- Preserve the user's stated study preferences without surrendering evidence standards.

A response that agrees with the user is not preferred merely because it feels cooperative.

## 27. Preference-data rights, privacy, and provenance

Every prompt, evidence packet, candidate, reviewer rationale, and training record remains subject to DR-10.

Preference datasets must not silently include:

- Private user conversations;
- User-uploaded pages;
- Restricted scholarship;
- Private benchmark cases;
- Reviewer personal data beyond the approved record;
- Copyrighted quotations beyond authorized use;
- Hidden model-generated content.

Public release of a preference dataset, adapter, or merged checkpoint receives its own rights decision.

## 28. Split and contamination policy

Preference training, development, and test splits operate over relationship clusters, including:

- Prompt templates;
- Behavior categories;
- Passage clusters;
- Translation families;
- Scholarly arguments;
- Source artifacts;
- Candidate-generation lineages;
- Controlled-negative templates;
- Languages;
- Page-layout families;
- Reviewer or adjudication dependencies.

The final private benchmark and fresh challenge set remain inaccessible.

A benchmark answer cannot be paraphrased into preference training merely because the wording changed.

## 29. Initial data-size posture

The first full preference stage should be intentionally small and high quality.

The proposed target is:

```text
800–1,500 accepted strict or properly conditioned preference pairs
```

plus separately retained:

```text
ties
unary desirable/undesirable records
reviewer-disagreement records
invalid or underspecified comparisons
evaluation-only cases
```

The first run should not expand beyond this range merely because synthetic generation can produce more pairs.

Expansion requires a measured uncovered behavior class or demonstrated benefit from additional diversity.

Rhema's 967-pair stage motivates this scale as a serious starting hypothesis—not as proof that 967 is universally optimal.[^rhema]

## 30. Coverage before volume

The dataset must report coverage across:

```text
behavior dimension
task type
answer mode
language
modality
assurance class
source/evidence condition
scope and safety class
reviewer expertise
method or tradition
hard-failure category
```

No category should dominate merely because examples are easy to generate.

Before training, the project defines minimum coverage floors for hard-failure and anti-over-refusal categories. Exact numerical floors are approved in the individual experiment after the DR-20 benchmark taxonomy is frozen.

## 31. DPO is the mandatory reference algorithm

DPO is the initial reference method because it is:

- Offline;
- Pairwise;
- Relatively simple;
- Widely implemented;
- Directly comparable to Rhema's reported stage;
- Able to preserve an explicit frozen SFT reference policy.

DPO replaces a separate reward-model-plus-PPO loop with a classification-style objective over preferred and rejected responses.[^dpo]

DPO is not presumed to be the winning algorithm.

## 32. SimPO is the preferred reference-free challenger

SimPO is the preferred initial challenger because it:

- Uses average sequence log probability as its implicit reward;
- Removes the frozen reference model during optimization;
- Includes a target reward margin;
- Explicitly addresses length-related mismatch between summed likelihood and generation behavior.

Its reported gains were measured on general chat benchmarks and do not establish superiority for Biblical Scholar Lab. It nevertheless provides a useful algorithmic contrast under our constrained budget.[^simpo]

The initial algorithm screen should compare SFT parent, DPO, and SimPO where the chosen framework supports a faithful implementation.

## 33. KTO is conditional on unary preference value

KTO learns from binary desirable/undesirable signals rather than requiring every record to be paired. It is useful when:

- A high-quality response lacks a natural rejected counterpart;
- A hard-failure response should be marked undesirable without manufacturing a chosen twin;
- Reviewer data are naturally pointwise;
- Pair construction would create artificial comparisons.

KTO becomes a candidate only if the unary dataset adds meaningful coverage that strict pairs cannot represent.[^kto]

It does not replace the mandatory DPO reference.

## 34. IPO and robust/noise-aware objectives remain conditional controls

IPO arises from a broader theoretical treatment of learning directly from pairwise preferences and identifies potential pitfalls in DPO-style objectives.[^ipo]

Robust preference methods may be useful when reviewer disagreement or label noise remains material after data governance. Recent approaches explicitly model or down-weight noisy labels rather than pretending all pairs are equally reliable.[^rpo]

These methods remain conditional research controls rather than mandatory first-stage algorithms.

The preferred first response to noisy data is better review, conditioning, and exclusion—not a more complicated loss that hides weak labels.

## 35. ORPO is not the primary causal baseline

ORPO combines supervised learning and preference contrast in one monolithic objective without a separate reference model.[^orpo]

It may be an efficiency comparator, but it cannot replace the project's required:

```text
SFT parent
versus
same SFT parent + preference stage
```

ablation.

Combining SFT and preference learning would make the incremental behavioral effect harder to isolate.

## 36. Broad online RL remains unauthorized

DR-19 does not authorize:

- PPO-based RLHF;
- GRPO campaigns;
- Unbounded on-policy generation;
- Reward-model training as product authority;
- Self-reward loops;
- Autonomous preference-data generation and promotion;
- Live user-feedback optimization.

Any online RL proposal requires a separate design identifying the deficit, reward validity, gaming risk, cost, safety, rollback, and superiority over SFT, DPO-style methods, tools, or runtime policy.

## 37. Reversible adapter-first policy

The first preference experiments use a separately identified, unmerged PEFT adapter where supported.

The preference adapter must be:

- Enableable and disableable;
- Bound to one exact SFT parent;
- Separately evaluable;
- Rollback-safe;
- Rights- and lineage-traceable;
- Compatible only with declared parent revisions.

The unmerged adapter remains the scientific master.

A merged checkpoint is a separate derivative and release decision.

Full-parameter preference optimization requires evidence that the adapter cannot express the needed behavioral change and that the added risk is justified.

## 38. Parent and reference identity

Every preference run freezes:

```text
SFT parent checkpoint
reference checkpoint, if required
adapter parent
model and processor
chat template
tool and structured-output format
preference dataset snapshot
algorithm and implementation
beta, margin, or equivalent parameters
sequence limits
loss masking
precision and kernel path
randomness
```

For DPO, the default reference is the exact frozen SFT parent unless an approved experiment specifies otherwise.

Changing the parent or reference creates a new experiment.

## 39. Training dynamics and early stopping

The project will not select a preference checkpoint by training preference accuracy alone.

Every run records:

- Chosen and rejected log probabilities;
- Reward or margin distributions;
- Train and held-out preference accuracy;
- Response length and format;
- Divergence from the parent;
- Category-specific benchmark results;
- Hard-failure rates;
- Adapter norm and update statistics;
- Overfitting indicators;
- Cost.

A run stops or is rejected when:

- Training separation increases without held-out behavior gains;
- One answer-length pattern dominates;
- False refusal or theological skew rises;
- Citation, multilingual, multimodal, long-context, or general behavior regresses;
- The adapter overfits prompt templates or passages;
- The model learns to mention policy language rather than behave correctly.

Exact exposure and epoch caps remain individual experiment parameters, but repeated passes over the small dataset require explicit justification.

## 40. Preference algorithm screen

The `ALG-P0` through `ALG-P4` labels refer only to the algorithm experiment ladder and are distinct from the `REV-P0` through `REV-P2` expert-review partitions.

The preferred staged experiment is:

### `ALG-P0` — Data and rubric validation

- Freeze the behavior ontology and development split.
- Audit pair quality, ties, strength, disagreement, rights, and coverage.
- Run blind reviewer consistency checks.

### `ALG-P1` — Small adapter smoke

- Train short DPO and SimPO adapters from the same SFT parent.
- Verify code, loss, resume, stability, and rollback.
- Use no private final benchmark.

### `ALG-P2` — Held-out behavior screen

- Compare the SFT parent, a chosen-only SFT control trained on the exact accepted preferred responses, DPO, and SimPO.
- Add KTO only if unary data materially improves coverage.
- Test all hard-failure categories and preservation suites.

### `ALG-P3` — Selected compact-model run

- Train the best approved algorithm and configuration on the full accepted development dataset.
- Preserve the losing algorithm as a documented negative result.

### `ALG-P4` — Optional cross-family confirmation

- Confirm whether the behavior gain transfers to another candidate family only if the model-family bakeoff or product plan requires it.

No algorithm advances solely because it wins a generic chatbot preference benchmark.

## 41. Mandatory ablation matrix

At minimum, evaluation compares:

```text
SFT parent
SFT parent + system/runtime policy only
SFT parent + chosen-only SFT on the exact accepted preferred responses
SFT parent + expanded targeted SFT, when separately justified
SFT parent + DPO
SFT parent + SimPO
selected preference adapter disabled
selected preference adapter enabled
selected adapter with and without full Runtime Scholar Harness
```

Where applicable:

```text
KTO
ORPO
robust or margin-aware variant
larger-model fallback without preference tuning
```

This determines whether preference optimization adds value beyond more SFT, better runtime policy, better retrieval, or a larger model.

## 42. Evaluation dimensions

Required metrics include:

```text
held-out target-behavior pass rate
hard-failure rate
citation and quotation integrity
source-type confusion
Translation Nuance causal accuracy
linguistic fallacy rate
calibration and abstention
false-refusal rate
harmful-compliance rate
perspective and tradition fairness
answer-depth compliance
response-length distribution
user-correction and anti-sycophancy performance
language correctness and pivot disclosure
multimodal grounding and illegibility restraint
tool and structured-output compliance
parent-relative general capability
multilingual, multimodal, long-context, and safety retention
latency, memory, and cost
```

No overall win rate may conceal a hard-failure regression.

## 43. Human evaluation

The final preference-stage comparison requires blinded human review on a representative subset.

Reviewers should not know which output comes from the SFT parent or preference adapter.

The evaluation records:

- Per-dimension judgments;
- Ties;
- Confidence;
- Reviewer background;
- Material disagreement;
- Preferred answer mode;
- Error category;
- Whether a response is acceptable even when not preferred.

A model judge may assist triage, but cannot be the sole authority for the stage's primary promotion decision.

## 44. User preference versus project policy

The system may personalize:

- Answer depth;
- Tone;
- Citation style;
- Preferred translation;
- Requested method or tradition;
- Language;
- Degree of technical detail.

It may not personalize away:

- Source integrity;
- Citation correctness;
- Rights;
- Safety;
- Evidence standards;
- Disclosure of uncertainty;
- User agency;
- Material counterevidence where the task requires it.

User preference becomes a runtime condition—not a universal training preference.

## 45. Runtime integration

The Runtime Scholar Harness remains able to:

- Override or reject an unsafe or unsupported model candidate;
- Correct exact text and citations;
- Route to another model;
- Request missing evidence;
- Apply scope and rights policy;
- Disable the preference adapter;
- Compare adapter-on and adapter-off behavior;
- Record a preference-related failure in the audit receipt.

Preference optimization should reduce runtime repairs. It does not eliminate the verifier.

## 46. Preference adapter release posture

The initial product candidate keeps the preference adapter separate.

This permits:

- Rapid rollback;
- A/B evaluation;
- Inspection of behavior changes;
- Alternative preference profiles where legitimately conditioned;
- Rights separation;
- Quantization and mobile testing;
- Controlled merging after approval.

The project will not ship hidden denominational adapters as neutral defaults.

Any tradition-specific adapter must identify its lens and pass the same evidence, safety, and source-integrity gates.

## 47. Preference data and model cards

Every preference dataset and resulting artifact receives documentation covering:

```text
behavior ontology
source and candidate generation
reviewer composition and qualifications
adjudication and disagreement
language and modality coverage
pair types and strengths
rights and privacy
splits and leakage controls
algorithm and hyperparameters
training dynamics
parent-relative behavior changes
known biases and failure modes
release status
```

The report must disclose whether exact pair data can be released or only aggregate statistics and templates.

## 48. Preference incidents and correction

If a deployed preference adapter causes:

- Systematic denominational skew;
- False refusal;
- Harmful compliance;
- Citation degradation;
- Over-hedging;
- Unsupported certainty;
- Language-specific regressions;
- Page-grounding errors;
- User-agency failures;

…the project freezes the adapter, identifies affected versions and answers, and determines whether to disable, repair, retrain, or withdraw it.

A preference adapter is not retained because it was costly or publicly released.

## 49. Sol implementation authority

Sol may implement:

- Preference-record schemas and validators;
- Candidate-generation and review tooling;
- Dataset materialization;
- Approved DPO, SimPO, KTO, or other algorithm adapters;
- Training, checkpoint, resume, and telemetry code;
- Evaluation and reporting;
- Adapter packaging and rollback;
- Design-neutral engineering optimizations.

Sol may not independently change:

- The behavior ontology;
- Preference hierarchy;
- Pair eligibility;
- Pluralism and disagreement policy;
- Reviewer requirements;
- Dataset-size or coverage posture;
- Algorithm candidates;
- Parent or reference policy;
- Training objective;
- Promotion metrics;
- Hard failures;
- Budget;
- Release status.

A material limitation or proposed alternative returns:

```text
BLOCKED_REQUIRES_DESIGN_REVIEW
```

## 50. Luna execution authority

Luna may, only when delegated by Sol under a frozen approved campaign:

- Verify exact hashes and run identity;
- Launch the approved adapter training;
- Monitor loss, margins, utilization, checkpoints, and cost;
- Resume the exact approved checkpoint;
- Run frozen evaluation commands;
- Stop at approved conditions;
- Collect logs and artifacts;
- Verify cloud shutdown;
- Return evidence to Sol.

Luna may not:

- Generate or edit preference pairs;
- Adjudicate reviewer disagreement;
- Change code, data, parent, reference, algorithm, hyperparameters, or budget;
- Decide which behavior should be preferred;
- Interpret results or promote an adapter;
- Merge or release artifacts.

## 51. Principal hard failures

DR-19 treats the following as hard failures:

- Using preference optimization as the source of factual or scholarly truth.
- Treating one theology or method as the unmarked globally preferred view.
- Converting legitimate reviewer disagreement into a strict pair through majority vote alone.
- Using private users, private benchmarks, or restricted evidence without authorization.
- Preferring longer answers merely because they are longer.
- Preferring citation quantity over citation correctness.
- Rewarding confident answers when evidence is insufficient.
- Training proper refusal without anti-over-refusal coverage.
- Teaching the model to repeat policy slogans instead of behaving correctly.
- Counting machine or teacher judgments as expert review without disclosure.
- Hiding model-generated or human-edited candidate provenance.
- Training on benchmark solutions or related passage/template clusters.
- Selecting a checkpoint by train preference accuracy alone.
- Merging the adapter before parent-relative evaluation and rollback testing.
- Promoting on a generic chatbot win rate while citation, source, safety, multilingual, or multimodal behavior regresses.
- Allowing the preference adapter to bypass runtime hard constraints.
- Allowing Sol or Luna to choose the project's theological, epistemic, safety, or behavioral preferences.
- Presenting owner or ChatGPT review as subject-matter expert validation.
- Promoting a `REV-P2` specialist judgment to gold, final promotion evidence, or a scholar-level claim without appropriately qualified review.
- Publishing the collaboration preview in a manner that obscures which `REV-P2` records remain `SME_REVIEW_PENDING`.

## 52. Review-status model and subject-matter validation partitions

Human review is not one interchangeable category.

The project distinguishes:

```text
UNREVIEWED_CANDIDATE
AUTOMATICALLY_VALIDATED
SOURCE_VERIFIED
OWNER_EDITORIAL_REVIEWED
CHATGPT_METHODOLOGY_REVIEWED
SME_REVIEW_PENDING
SME_REVIEWED
MULTI_SME_ADJUDICATED
REJECTED
SUPERSEDED
```

These states describe different evidence and authority.

- `OWNER_EDITORIAL_REVIEWED` means that Joseph Abbud has reviewed and approved product direction, wording, workflow, governance, or release posture within his owner role. It does not assert specialist biblical-studies expertise.
- `CHATGPT_METHODOLOGY_REVIEWED` means that the record has been reviewed for conformance with the approved epistemic, experimental, architectural, and evidence contracts. It does not masquerade as independent human subject-matter validation.
- `AUTOMATICALLY_VALIDATED` and `SOURCE_VERIFIED` identify mechanically or directly checkable results such as exact quotations, identifiers, locators, source spans, schema conformance, and policy behavior.
- `SME_REVIEWED` means that a qualified person whose recorded expertise matches the particular judgment has reviewed it.
- `MULTI_SME_ADJUDICATED` is reserved for cases requiring complementary specialists, resolution of material expert disagreement, or a deliberately plural panel.

A general theology qualification does not automatically establish competence in New Testament Greek, Biblical Hebrew, textual criticism, ancient versions, translation studies, multilingual output, page interpretation, or sensitive-use review. Reviewer fitness remains task-specific.

Preference records and benchmark cases are partitioned by the kind of review required.

### `REV-P0_DETERMINISTIC_AND_OPERATIONAL`

May proceed without a biblical-studies subject-matter expert when the judgment is mechanically, source-, policy-, or contract-grounded.

Examples include:

- Exact passage and edition lookup;
- Fabricated or malformed citations;
- Quotation mismatch;
- Wrong page or region grounding;
- Scripture-versus-paratext classification where the source is explicit;
- Hidden language pivot;
- Tool, schema, rights, privacy, and runtime compliance;
- Proper refusal and anti-over-refusal under approved policy;
- Claiming to inspect evidence that was not present;
- Failure to use an exact deterministic tool.

### `REV-P1_SOURCE_VERIFIABLE_SCHOLARLY_BEHAVIOR`

May proceed with exact source inspection, deterministic validation where available, and project-methodology review when the preferred behavior concerns epistemic discipline rather than resolution of a subtle specialist dispute.

Examples include:

- Separating evidence from inference;
- Disclosing uncertainty;
- Presenting documented competing positions accurately;
- Avoiding translation-count-as-witness-count errors;
- Avoiding lexical and word-study fallacies where the fallacy is unambiguous;
- Declining to infer translator intent without evidence;
- Disclosing that only metadata, an abstract, or a secondary quotation was inspected;
- Preserving ancient-version and retroversion restraint;
- Correcting a false premise with direct evidence.

A `REV-P1` record may still be escalated to a subject-matter expert when its underlying scholarly content is materially disputed or outside the reviewers' competence.

### `REV-P2_SPECIALIST_SCHOLARLY_JUDGMENT`

Requires an appropriately qualified subject-matter expert before the record can become authoritative gold, a final promotion metric, or a scholar-level public claim.

Examples include:

- Selecting among disputed Greek or Hebrew parses;
- Assigning a contextual lexical sense in a difficult passage;
- Judging which textual reading is earlier or more probable;
- Retroverting an ancient version;
- Diagnosing confessional influence;
- Assessing literary dependence or a difficult allusion;
- Establishing a current scholarly consensus;
- Determining whether a complex theological presentation is balanced;
- Adjudicating a subtle Translation Nuance causal analysis.

`REV-P2` candidates may be generated, organized, and published as explicitly provisional collaboration targets, but remain `SME_REVIEW_PENDING` until qualified review occurs.

The absence of a current expert partner therefore does not block architecture, engineering, corpus preparation, deterministic tools, runtime development, model-family baselines, `REV-P0`/`REV-P1` preference experiments, or public demonstration of properly bounded capability. It does block specialist gold labels and public claims that depend on them.

## 53. `MVP-01_EXPERT_COLLABORATION_PREVIEW`

Completion of `REV-P0` and a credible, source-verifiable `REV-P1` partition establishes the minimum capability gate for an initial public collaboration preview.

The purpose of this preview is to demonstrate that Biblical Scholar Lab is technically and methodologically substantial enough to merit expert participation while the specialist `REV-P2` layer remains open to scholarly review.

The preview may publish, subject to DR-10:

- The public repository and approved designs;
- The implemented runtime, tools, evidence, provenance, and Translation Nuance workflow;
- A public `REV-P0`/`REV-P1` benchmark subset;
- Reproducible baseline and preference-adapter evaluations;
- Carefully bounded multilingual and multimodal demonstrations;
- Public-safe corpus manifests and rights records;
- Candidate `REV-P2` cases clearly marked `SME_REVIEW_PENDING`;
- A collaboration brief identifying the specialties, cases, and adjudication work needed.

The preview must not claim:

- Expert-grade or comprehensive biblical scholarship;
- Authoritative `REV-P2` judgments;
- A completed specialist benchmark;
- Validated consensus assessment across subfields or traditions;
- Replacement of scholars, translators, pastors, or teachers;
- Model-weight release where the lineage has not passed DR-10 review.

`MVP-01_EXPERT_COLLABORATION_PREVIEW` requires:

1. `REV-P0` deterministic and operational behavior passing its approved hard gates.
2. A frozen `REV-P1` behavior ontology and reviewed, source-verifiable development set.
3. Inspectable evidence packets, claim ledgers, citations, and runtime audit receipts.
4. Public-safe rights and privacy review.
5. A reproducible public benchmark subset and evaluation report.
6. Clear separation of `REV-P0`/`REV-P1` validated results from `REV-P2` candidates.
7. Prominent disclosure of failures, limitations, model and language coverage, and expert-review gaps.
8. A documented contribution and reviewer-attribution process.
9. ChatGPT review of the exact release artifacts.
10. Joseph Abbud's explicit release approval.

It does not require:

- Completion of `REV-P2`;
- Final model-family selection;
- Main continued pretraining;
- Full production readiness;
- Public release of full weights;
- Full support for every language or modality;
- A completed commercial or public-scale interface.

This milestone is a release gate—not a claim that the research program is complete.

## 54. Binding decisions

DR-19 locks:

1. Preference optimization shapes behavior but does not define truth, rights, policy, or scholarly authority.
2. Runtime hard constraints and deterministic verification remain authoritative after preference training.
3. Behavior is represented through a typed ontology rather than one global quality score.
4. Preference judgments preserve dimension, condition, strength, evidence, reviewer, uncertainty, and disagreement.
5. Strict, dimension-specific, conditioned, tied, plural, underspecified, and invalid comparisons remain separate.
6. Only approved decisive, strong, and sufficiently supported moderate comparisons enter the initial strict-pair dataset.
7. Hard evidentiary, rights, safety, and source-integrity dimensions outrank style.
8. Minimal-contrast, plausible near-miss pairs are preferred.
9. Candidate responses preserve exact parent, generation, tool, evidence, and human-edit provenance.
10. Model-generated negatives and teacher responses remain candidates until reviewed.
11. Reviewer roles and qualifications are task-specific.
12. Legitimate plural disagreement remains visible and is conditioned or excluded rather than erased.
13. Confessional and methodological preferences require explicit context.
14. Consequential preference comparisons bind to immutable evidence packets.
15. Citation, Translation Nuance, original-language restraint, correction, scope, safety, multilingual, and multimodal behavior are first-class preference domains.
16. Brief, Study, and Scholarly modes are judged within mode; length is not quality.
17. Preference datasets remain rights-, privacy-, and leakage-governed artifacts.
18. The initial target is 800–1,500 accepted strict or properly conditioned pairs, with ties, unary records, and disagreement retained separately.
19. Coverage and quality precede volume.
20. DPO is the mandatory reference algorithm.
21. SimPO is the preferred first reference-free challenger.
22. KTO is conditional on meaningful unary-data coverage.
23. IPO, robust/noise-aware, margin-aware, and ORPO methods remain conditional controls.
24. Broad online RL remains unauthorized.
25. Preference optimization begins with a reversible, unmerged PEFT adapter.
26. Every run freezes exact SFT parent and reference identity.
27. Training dynamics, held-out behavior, length, divergence, and category metrics determine stopping—not train accuracy alone.
28. The mandatory comparison includes the SFT parent, a chosen-only SFT control using the exact accepted preferred responses, DPO, and SimPO; expanded targeted SFT is an additional control only when separately justified.
29. The full Runtime Scholar Harness remains part of final preference evaluation.
30. Human blind review is required for the promotion decision.
31. No aggregate win rate may conceal a hard failure.
32. User preferences may customize presentation and requested lens but cannot lower evidence, rights, safety, or agency standards.
33. The preference adapter remains separately disableable and rollback-safe until an owner-approved merge decision.
34. Every dataset and adapter receives a data/model card and incident plan.
35. Owner approval, ChatGPT methodology review, deterministic validation, editorial review, and subject-matter expert review remain non-equivalent review states.
36. Preference and benchmark records are partitioned into `REV-P0` deterministic/operational, `REV-P1` source-verifiable scholarly behavior, and `REV-P2` specialist scholarly judgment.
37. The absence of an expert partner does not block `REV-P0`/`REV-P1` engineering, experiments, or bounded public demonstration.
38. `REV-P2` records remain `SME_REVIEW_PENDING` and cannot become authoritative gold, final promotion metrics, or scholar-level claims without qualified review.
39. Completion of `REV-P0` and a credible `REV-P1` partition may satisfy the `MVP-01_EXPERT_COLLABORATION_PREVIEW` gate under the defined rights, evaluation, documentation, ChatGPT-review, and owner-approval requirements.
40. Sol implements the approved preference system; Luna only runs frozen campaigns; ChatGPT designs and reviews experiments; Joseph Abbud retains sole approval authority.

## 55. Decisions intentionally deferred

DR-19 does not yet select:

- The final preference dataset count within the approved range;
- Exact category coverage floors;
- Exact reviewer panel and compensation;
- Exact ratio of human-authored, parent-generated, teacher-generated, or controlled-negative candidates;
- Exact English, Spanish, French, and cross-lingual proportions;
- Exact multimodal pair count;
- Exact DPO beta;
- Exact SimPO beta or margin;
- Exact KTO weights;
- Exact LoRA rank and target modules;
- Exact learning rate, batch size, epochs, or exposure cap;
- Exact sequence length;
- Exact robust or margin-aware objective;
- Whether ORPO is run;
- Whether a cross-family confirmation is justified;
- Whether the final adapter is merged;
- Whether tradition-conditioned adapters are produced;
- The final release status of preference data or weights.

Those are approved later through DR-20 through DR-25, DR-28, the model bakeoff, the SFT error taxonomy, and the individual preference experiment.

## 56. Approved statement

> **Biblical Scholar Lab will use preference optimization as a bounded, reversible behavioral intervention applied only after a strong scholarly and retrieval-aware SFT parent exists. Preference training will not define biblical truth, linguistic analysis, textual history, scholarly consensus, rights, safety policy, or theological authority; those remain in reviewed evidence, deterministic tools, runtime policy, verification, and human governance. Every preference record will bind an immutable prompt and evidence context, exact candidate origins, a typed behavior ontology, per-dimension judgments, hard failures, preference strength, method or perspective conditions, reviewer qualifications, disagreement, adjudication, rights, and split identity. Strict dominance, dimension-specific preference, perspective-conditioned preference, ties, legitimate plural disagreement, underspecified prompts, and annotation errors will remain distinct, and no globally preferred theology, method, language style, or response length will be learned by collapsing legitimate differences. Preference construction will emphasize minimal contrasts and realistic near misses involving exact tool use, citation support, source-type discipline, Translation Nuance, original-language restraint, calibrated uncertainty, correction and anti-sycophancy, scope and anti-over-refusal, sensitive-use behavior, answer depth, multilingual pivots, multimodal grounding, and runtime cooperation. The first stage will target approximately 800–1,500 high-quality accepted pairs, retaining ties, unary desirability signals, disagreement, and invalid comparisons separately; expansion will follow measured coverage gaps rather than synthetic volume. DPO will be the mandatory reference algorithm, SimPO the preferred first reference-free challenger, KTO conditional on useful unary data, and other pair-weighted, robust, monolithic, or online methods separately gated. The required ablation will compare the same SFT parent against a chosen-only SFT control trained on the exact accepted preferred responses, DPO, SimPO, adapter-off, and adapter-on conditions; expanded targeted SFT may be added as a separately identified control under the full Runtime Scholar Harness, with blind human review and hard gates for evidence, citation, source identity, Translation Nuance, safety, false refusal, calibration, multilingual, multimodal, long-context, and general-capability retention. The initial preference artifact will remain an unmerged, disableable PEFT adapter with complete rollback, training-dynamics, lineage, and incident records. Sol will implement the approved preference contracts and algorithms, Luna may execute only frozen campaigns delegated by Sol, ChatGPT will design and independently review the experiment and interpret its evidence, and Joseph Abbud will retain sole authority to approve preference policy, budget, promotion, merge, and release. Owner review, ChatGPT methodology review, deterministic validation, editorial review, and qualified subject-matter expert review will remain separate statuses. `REV-P0` deterministic and operational behavior and `REV-P1` source-verifiable scholarly behavior may proceed before an expert partnership exists, while `REV-P2` specialist judgments remain `SME_REVIEW_PENDING` and excluded from authoritative gold, final promotion metrics, and scholar-level claims until reviewed by appropriately qualified humans. Completion of `REV-P0` and a credible `REV-P1` partition may support `MVP-01_EXPERT_COLLABORATION_PREVIEW`, a public, rights-cleared, reproducible collaboration release that demonstrates the runtime, evidence architecture, benchmark subset, `REV-P1` behavior, and known limitations while publishing `REV-P2` material only as explicitly provisional expert-review candidates.**

---

## References

[^rhema]: Rhema, “Meet BibleAI: our first open-source model, free for the Church,” April 15, 2026, and the `rhemabible/BibleAI` model card. The public record reports 15,289 SFT examples, 967 DPO pairs, two DPO epochs, beta 0.1, rank-32 LoRA, and Rhema's qualitative assessment that the preference stage strongly shaped conversational behavior: <https://rhemabible.co/blog/introducing-bibleai> and <https://huggingface.co/rhemabible/BibleAI>.
[^dpo]: Rafael Rafailov et al., “Direct Preference Optimization: Your Language Model Is Secretly a Reward Model,” 2023. DPO directly optimizes a policy from pairwise preference data without a separate reward-model and online PPO stage: <https://arxiv.org/abs/2305.18290>.
[^simpo]: Yu Meng, Mengzhou Xia, and Danqi Chen, “SimPO: Simple Preference Optimization with a Reference-Free Reward,” 2024. SimPO uses length-normalized policy log probability and a target reward margin without a reference model: <https://arxiv.org/abs/2405.14734>.
[^kto]: Kawin Ethayarajh et al., “KTO: Model Alignment as Prospect Theoretic Optimization,” 2024. KTO uses binary desirable/undesirable feedback and provides a relevant alternative where natural pairs do not exist: <https://arxiv.org/abs/2402.01306>.
[^ipo]: Mohammad Gheshlaghi Azar et al., “A General Theoretical Paradigm to Understand Learning from Human Preferences,” 2023. The paper develops the PsiPO family, analyzes DPO assumptions, and derives Identity Preference Optimization: <https://arxiv.org/abs/2310.12036>.
[^orpo]: Jiwoo Hong, Noah Lee, and James Thorne, “ORPO: Monolithic Preference Optimization without Reference Model,” 2024. ORPO combines supervised learning with an odds-ratio preference penalty, offering an efficient but less stage-separable alternative: <https://arxiv.org/abs/2403.07691>.
[^odpo]: Afra Amini, Tim Vieira, and Ryan Cotterell, “Direct Preference Optimization with an Offset,” 2024. ODPO introduces pair-specific offsets intended to represent different preference strengths: <https://arxiv.org/abs/2402.10571>.
[^diverging]: Michael J. Q. Zhang et al., “Diverging Preferences: When do Annotators Disagree and do Models Know?” 2024. The study develops a taxonomy of preference disagreement and shows that standard reward and judge models can obscure the distinction between unanimous and divided judgments: <https://arxiv.org/abs/2410.14632>.
[^rpo]: Xiaoyang Cao et al., “Robust Preference Optimization: Aligning Language Models with Noisy Preference Feedback,” 2025, and Xize Liang et al., “ROPO: Robust Preference Optimization for Large Language Models,” 2024. These works provide examples of preference objectives that explicitly model or suppress noisy labels: <https://arxiv.org/abs/2509.24159> and <https://arxiv.org/abs/2404.04102>.
[^length]: Junru Lu et al., “Eliminating Biased Length Reliance of Direct Preference Optimization via Down-Sampled KL Divergence,” 2024, and Wei Liu et al., “Length Desensitization in Direct Preference Optimization,” 2024. Both analyze length sensitivity and verbosity effects in DPO-style training: <https://arxiv.org/abs/2406.10957> and <https://arxiv.org/abs/2409.06411>.
