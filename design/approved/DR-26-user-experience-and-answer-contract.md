# DR-26 — User Experience and Answer Contract

| Field | Value |
|---|---|
| Design ID | `DR-26` |
| Status | `APPROVED` |
| Approval date | 2026-08-16 |
| Project owner | Joseph Abbud |
| Product, architecture, benchmark, and experiment designer | ChatGPT |
| Independent implementation and evidence reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2 and supplements; DR-03; DR-04; DR-05; DR-06; DR-07; DR-08; DR-09; DR-10; DR-11; DR-12; DR-13; DR-14; DR-15; DR-16; DR-17; DR-18; DR-19; DR-20; DR-21; DR-22; DR-23; DR-24; DR-25 |
| Implementation authority | GPT-5.6 Sol exclusively implements and repairs the approved user-interface, accessibility, answer-rendering, evidence-inspection, correction, export, privacy, and collaboration-preview machinery |
| Execution authority | GPT-5.6 Luna may execute only frozen usability, accessibility, evaluation, packaging, or publication campaigns delegated by Sol; Luna may not create or modify code, content, benchmark cases, interface contracts, product claims, release state, or experiment design |
| Product authority | ChatGPT designs the user promise, information architecture, answer contract, evidence presentation, accessibility requirements, and user-study design; Joseph reviews and approves consequential product, release, and public-claim decisions |
| Approved cloud and archive constraints | Project-controlled cloud execution remains Lambda-only under DR-25; retained generated artifacts remain authoritative on the owner-controlled Thunderbolt archive under DR-23 and DR-25 |
| Approved change | Establishes the version-one user experience, workspace surfaces, answer modes, progressive-disclosure rules, evidence and citation inspection, Translation Nuance and original-language presentation, multimodal page study, visible context and compaction state, correction and note-export flows, multilingual and RTL behavior, accessibility conformance target, trust and privacy disclosures, error states, anti-overtrust and anti-dependency controls, expert-collaboration preview, usability metrics, and Sol implementation boundaries |

## 1. Purpose

DR-01 defines Biblical Scholar Lab as a source-aware, multimodal, multilingual-capable New Testament philology and contextual research assistant serving serious Bible learners and researchers regardless of credentials.

DR-02 through DR-16 define the evidence, provenance, linguistic, Translation Nuance, scholarship, context, multimodal, and runtime systems required to make the assistant trustworthy.

DR-19 defines the behavior the model should prefer.

DR-20 through DR-22 define how the benchmark and evaluation system measure those capabilities.

DR-26 defines **what the user experiences; which choices and evidence remain visible; how the same verified claim ledger becomes Brief, Study, or Scholarly output; how ordinary Bible learners gain access to technical depth without being overwhelmed; how citations, uncertainty, translation differences, original languages, page images, corrections, compaction, privacy, and model routing remain inspectable; and how the interface avoids turning a fluent model into a simulated spiritual or scholarly authority**.

A technically correct runtime can still produce a poor or unsafe product if:

- The user cannot tell which translation or edition was used;
- A concise answer hides a material qualification;
- Citations look authoritative but cannot be inspected;
- Greek or Hebrew detail is presented as a prestige signal rather than evidence;
- A study note or generated paraphrase is visually indistinguishable from Scripture;
- The application silently changes canon, language, model route, or context mode;
- A page viewer replaces uncertain OCR with expected canonical wording;
- A user correction disappears after compaction;
- The interface presents one global confidence percentage that hides uncertainty in a crucial claim;
- A general learner must understand apparatus notation before receiving a useful answer;
- An expert cannot inspect the source span, edition, methodology, or counterevidence;
- A private Bible-page image is uploaded or retained without clear consent and route disclosure;
- The system uses urgency, streaks, spiritualized language, or emotional dependence to drive engagement;
- A public collaboration preview implies that `SME_REVIEW_PENDING` content is validated scholarship;
- The interface is technically functional but inaccessible to keyboard, screen-reader, low-vision, motor-impaired, multilingual, or RTL users.

DR-26 is intended to prevent those failures.

## 2. Governing principle

> **Biblical Scholar Lab will make rigorous evidence easier to use without hiding its uncertainty, provenance, or limits. The interface will expose the minimum information necessary for a responsible answer, allow progressive access to deeper evidence, keep the user's active passage, edition, canon, language, method, and privacy state visible and correctable, and render every answer from one verified claim ledger. Simplicity may reduce displayed detail; it may not alter the underlying conclusion, erase material alternatives, or simulate authority.**

The product should feel:

```text
clear
quiet
scholarly
approachable
inspectable
user-controlled
```

It should not feel:

```text
oracular
clerical
argumentative by default
academically performative
gamified
engagement-maximizing
opaque
```

## 3. Product form: research workspace, not chat alone

The conversational interface is one entry point. Version one is a research workspace with several coordinated surfaces.

### 3.1 `ASK_AND_STUDY`

The primary conversational surface for:

- Passage questions;
- Translation comparisons;
- Original-language questions;
- Historical and literary context;
- Scholarly synthesis;
- Supporting research tasks;
- Follow-up questions within a structured study session.

### 3.2 `PASSAGE_WORKSPACE`

A passage-centered workspace containing:

- Active passage and reference scheme;
- Selected translation or edition;
- Source-language text where available;
- Parallel translations;
- Notes, cross-references, and evidence;
- Current research question;
- Answer and sources;
- Saved research notes.

### 3.3 `TRANSLATION_COMPARE`

A dedicated Translation Nuance surface for:

- Source and target spans;
- Parallel translation wording;
- Many-to-many alignments;
- Textual-state differences;
- Causal diagnoses;
- Translation lineage;
- Materiality and uncertainty;
- User-selected translation sets.

### 3.4 `PAGE_STUDY`

A page-image workspace for:

- Bible, study Bible, interlinear, commentary, lexicon, grammar, or article pages;
- Region overlays;
- OCR, VLM, and deterministic-text comparison;
- Edition and passage identification;
- Scripture-versus-paratext distinctions;
- User corrections;
- Page-grounded study notes.

### 3.5 `SOURCE_AND_EVIDENCE_INSPECTOR`

A reusable inspector for:

- Exact source spans;
- Publication and edition identity;
- Translation provenance;
- Claim/evidence links;
- Counterevidence;
- Source type and methodological role;
- Publication status and rights limitations.

### 3.6 `RESEARCH_NOTES_AND_EXPORT`

A structured workspace for:

- Saved study questions;
- Passage and edition identity;
- Claims and evidence;
- Translation options;
- User annotations;
- Open questions;
- Citation export;
- Reproducible research packets.

### 3.7 `EXPERT_COLLABORATION_PREVIEW`

A public-safe or reviewer-only surface for:

- `REV-P2` candidate cases;
- `SME_REVIEW_PENDING` labels;
- Evidence packets;
- Specialty queues;
- Review qualifications;
- Original and adjudicated judgments;
- Contribution and attribution policy.

This is not a public vote on scholarly truth.

## 4. Canonical user-experience records

The logical architecture includes at least:

```text
UserStudyProfile
StudyWorkspace
StudySession
StudyRequest
ActiveStudyContext
AnswerPresentationContract
ClaimPresentationRecord
EvidenceDisclosureRecord
CitationInteractionRecord
TranslationComparisonView
OriginalLanguageView
PageStudyView
ContextDisclosureRecord
CompactionDisclosureRecord
UserCorrectionRecord
ResearchNoteArtifact
PublicShareArtifact
AccessibilityConformanceRecord
UsabilityStudyRecord
UXAuditReceipt
```

These are project-owned contracts. A front-end framework, component library, chat SDK, analytics provider, or design system cannot become the authoritative representation of user state or scholarly meaning.

## 5. User identity and onboarding

The product must not require formal biblical training.

Initial onboarding may ask, but must not require:

- Preferred interface and answer language;
- Preferred Bible translation;
- Canon or reference profile;
- Default answer depth;
- Whether original-language detail should be shown by default;
- Accessibility preferences;
- Whether research sessions may be retained;
- Whether private uploads may be retained for a bounded period.

The product must not ask the user to select a denomination in order to function.

A user may later choose a tradition or methodology as an explicit lens. That selection remains visible and reversible.

The default onboarding message should communicate:

- The assistant is a source-grounded research aid;
- No Greek, Hebrew, or seminary background is required;
- Exact passages and citations come from tools and sources;
- Disputed conclusions are labeled;
- The model is not a divine, clerical, medical, legal, or psychological authority;
- Private uploads are not used for shared training by default.

## 6. Active study context is always inspectable

The interface must expose the active context that can materially change an answer:

```text
passage or work
translation or edition
canon/reference profile
question language
answer language
answer-depth mode
methodology or tradition lens
context mode
provider/model route when material
rights or access limitation
current evidence horizon
```

This information may be compactly displayed in a context bar or study header.

The application may omit a control from the primary view when it is irrelevant, but the active value remains inspectable.

The system may not silently change:

- Translation;
- Edition;
- Canon profile;
- Answer language;
- Methodology;
- Context mode;
- Private/public state;
- Model route when the route changes rights, privacy, cost, or capability.

A material change requires an explicit user action, a clear system disclosure, or a clarification request.

## 7. Request entry

Version-one request entry supports:

```text
free-text question
passage or range
translation comparison
source or citation
image or screenshot upload
selected text span
follow-up on current study
supporting research task
```

The application should infer ordinary context when safe, but ask for clarification only when ambiguity changes:

- The passage;
- The textual form;
- The translation or edition;
- The question's method;
- The evidence required;
- The answer's likely conclusion;
- The privacy or provider route.

Clarification should be concise and should preserve any portion of the request that can already be answered safely.

## 8. Answer-depth modes

The three approved answer depths remain:

### `BRIEF`

Provides:

- Direct answer;
- Most important distinction;
- Essential qualification;
- One or more key sources where relevant.

Brief mode may omit technical derivation. It may not omit a material variant, serious counterinterpretation, source limitation, or safety qualification necessary to avoid misleading the user.

### `STUDY`

The default mode.

Provides:

- Accessible explanation;
- Relevant context;
- Translation or linguistic issue;
- Principal interpretations;
- Reasoned assessment;
- Citations;
- Expandable technical evidence.

### `SCHOLARLY`

Provides, where relevant:

- Exact source-language text and edition;
- Morphology, syntax, semantics, and discourse;
- Textual variants and apparatus evidence;
- Ancient versions;
- Translation lineage and causal diagnosis;
- Methodological alternatives;
- Modern scholarship;
- Claim-level citations;
- Explicit evidence/inference boundaries;
- Full uncertainty and limitations.

### 8.1 Same truth, different disclosure

All three modes render from the same verified claim ledger.

The modes may differ in:

- Depth;
- Technical vocabulary;
- Number of displayed sources;
- Amount of visible linguistic analysis;
- Default expansion state.

They may not differ in:

- Core conclusion;
- Source identity;
- Material uncertainty;
- Whether a textual variant exists;
- Whether an answer is disputed;
- Whether a citation supports the claim;
- Safety or rights requirements.

## 9. Perspective, method, and devotional intent are separate controls

Answer depth is not a theological perspective.

The user may separately request:

```text
evidence-first default
historical-critical
literary or narrative
translation-studies
canonical-theological
Catholic
Orthodox
Reformed
Wesleyan
Jewish interpretive context
another explicitly identified lens
```

The selected lens remains visible in the answer and source inspector.

A devotional reflection, prayer, sermon draft, or teaching outline is an explicitly labeled output intent under DR-03. It is not the default interpretation mode and does not gain divine or clerical authority.

## 10. Canonical answer structure

The logical answer contract is:

```text
Direct answer
Text and source identity
Issue
Evidence
Options or competing interpretations
Assessment
Uncertainty and limitations
Sources
```

The interface may collapse or rename sections according to answer depth, but the underlying structure remains available.

For Translation Nuance cases, the answer should ordinarily disclose:

```text
Is a textual variant involved?
What source-language issue is involved?
What target-language or translation-policy issue is involved?
What effect does each rendering have?
What evidence supports the diagnosis?
What remains uncertain?
```

For textual-critical or ancient-version questions, it should disclose whether the system inspected:

- A manuscript image;
- A transcription;
- An apparatus;
- An ancient-version edition;
- A secondary report.

## 11. Progressive disclosure

The product should make technical evidence available without forcing all users to confront it at once.

Progressive disclosure may hide:

- Full morphology tables;
- Alternative parses;
- Apparatus notation;
- Translation-lineage details;
- Full bibliographic metadata;
- Audit and model-route details;
- Full runtime receipts.

Progressive disclosure may not hide:

- Material uncertainty;
- A textual variant that affects the answer;
- A serious alternative interpretation;
- A source-access limitation;
- A rights or privacy restriction affecting the result;
- A hidden pivot translation;
- A corrected or retracted source;
- A safety boundary.

Expandable controls must have meaningful accessible names, keyboard support, and persistent state within the current workspace.

## 12. Claim-level epistemic presentation

The UI will not show one global confidence score for the entire answer.

Individual consequential claims may display approved DR-02 statuses such as:

```text
DIRECTLY_ATTESTED
STRONGLY_SUPPORTED
PLAUSIBLE
CONTESTED
SPECULATIVE
UNSUPPORTED
UNKNOWN
```

The status must be conveyed through text and accessible semantics—not color alone.

A user may inspect:

- What the status applies to;
- Which evidence supports it;
- Which evidence limits or contradicts it;
- Which method was used;
- Whether the claim is source observation, analysis, inference, interpretation, or application.

Numerical probabilities are not shown unless task-specific calibration has been established and the display itself passes a later design review.

## 13. Evidence and citation inspection

Every consequential citation should be interactive when the source and rights permit.

The evidence inspector should expose:

```text
claim being supported
source title and contributor
source type
publication or edition version
exact locator or source span
quoted wording
quotation language
published or model-generated translation status
inspection level
methodological role
current publication status
rights/display limitations
counterevidence or related sources
```

The user should be able to distinguish:

```text
directly inspected full text
abstract only
metadata only
secondary quotation
apparatus report
primary source
historical commentary
modern scholarship
```

A citation card must not imply that the system accessed a full source when it accessed only metadata, an abstract, or a secondary quotation.

Citations must remain usable with keyboard and screen readers. Hover-only evidence is prohibited.

## 14. Translation Nuance workspace

The Translation Compare surface should support:

- User-selected translations and editions;
- Source-language text;
- Many-to-many and discontinuous alignment;
- Surface-difference highlighting;
- Material-difference classification;
- Textual-state status;
- Causal chain;
- Translation-family lineage;
- Target-language constraints;
- Intent-versus-effect distinction;
- Alternative diagnoses;
- Evidence and uncertainty.

The default visual comparison should not imply that every different word is a meaningful disagreement.

The interface should distinguish at least:

```text
surface wording difference
minor form difference
potential nuance difference
material interpretive difference
textual-history difference
no material difference
unknown
```

Color may reinforce these states but cannot be the only signal. A table or list alternative must be available for assistive technology and narrow screens.

The product may not provide a global “best translation” ranking without a user-defined criterion such as:

- Source-form transparency;
- Accessibility;
- Public reading;
- Ambiguity preservation;
- Literary style;
- Translation-history study.

## 15. Original-language presentation

Original-language detail should be approachable and evidence-centered.

The interface may show:

```text
surface form
transliteration, optional
lemma
morphology
syntactic role
contextual sense candidates
semantic role
referent
translation alignments
source and annotation provenance
```

It should not begin by dumping an interlinear or every lexicon gloss.

A user selecting a word should receive:

1. The form in context;
2. The source edition;
3. Its morphological analysis and alternatives;
4. The contextual issue;
5. Relevant translation choices;
6. A warning when a common word-study fallacy would be misleading.

Transliteration is optional and never replaces the original script.

Greek accentuation, Hebrew pointing and cantillation, Aramaic identity, RTL direction, and combining marks must render correctly and remain copyable.

## 16. Textual criticism, ancient versions, and apparatus presentation

The interface must visibly distinguish:

```text
manuscript witness
corrector or hand
critical edition
apparatus report
ancient version
modern translation
conjecture
patristic citation
secondary report
```

Apparatus notation should be expandable into a plain-language explanation without deleting the exact notation.

The UI should say whether a witness reading was:

- Directly inspected;
- Read from a transcription;
- Reported by an apparatus;
- Reported by a secondary source.

Apparatus silence cannot be displayed as “the witness omits this” unless the coverage contract supports that conclusion.

Ancient-version evidence should expose the approved retroversion restraint level and should not present a reconstructed source wording as direct attestation.

## 17. Multimodal page-study experience

The Page Study surface should display:

- Original image or authorized derivative;
- Page orientation and crop state;
- Region overlays;
- Region role and authority class;
- OCR/ATR candidate;
- VLM observation;
- Deterministic canonical-text match where available;
- Edition and passage candidates;
- Uncertainty and illegibility;
- User correction controls.

The interface must preserve the difference between:

```text
what the pixels visibly support
what OCR recognized
what the VLM inferred
what the identified edition contains
what the user corrected
```

A user may toggle overlays, but an accessible region list and text alternative must also be provided.

No generative enhancement is presented as observed text.

When a region is illegible, the UI should say so rather than silently filling expected words from the canonical passage.

## 18. Long-context and evidence-mode disclosure

The user should be able to inspect the active evidence mode:

```text
focused passage
book scope
full New Testament
custom canon scope
targeted RAG
hybrid canon + RAG
multimodal page
compacted session
```

The primary answer need not expose token counts by default, but the advanced audit view should disclose:

- Context mode;
- Key evidence blocks included;
- Material evidence omitted;
- Full-canon translation or edition;
- Whether a pivot was used;
- Whether a larger model or specialist route was invoked;
- Source limitations caused by rights, context, or provider constraints.

Full-New-Testament context should never be presented as automatically more authoritative than targeted evidence.

## 19. Compaction transparency

When session state has been compacted, the interface must expose a visible but unobtrusive state such as:

```text
Session summarized for continuity
```

The user should be able to inspect:

- Which durable preferences and corrections were retained;
- Which sources are represented by evidence handles;
- Which information was summarized;
- Which information was omitted;
- Whether the source can be rehydrated;
- Whether the compaction is stale.

The user must be able to correct a compacted session assumption.

The application may not hide the fact that a previous exact source is no longer active when a new claim depends on it. The runtime must rehydrate the evidence before exact quotation or consequential reuse.

## 20. Research notes and export

A `ResearchNoteArtifact` should support:

```text
research question
active passage and editions
answer mode and methodology
textual and linguistic issue
Translation Nuance diagnoses
ancient context
scholarly positions
assessment
uncertainty
user notes
open questions
citations
source and evidence handles
model/runtime and evidence horizon
```

Version-one exports should prioritize:

- Markdown;
- Structured JSON;
- Copyable citation lists;
- CSL-compatible bibliographic data where available;
- A public-safe share view.

Exact additional formats remain deferred.

An exported answer should preserve:

- Edition and translation identity;
- Citation locators;
- Model-generated translation labels;
- Evidence horizon;
- Material uncertainty;
- Date of generation;
- Whether the source was available directly or through a secondary report.

A public share artifact must exclude private, restricted, or non-displayable evidence and explain any resulting omission.

## 21. User corrections and answer revision

The user may correct:

- Passage;
- Edition or translation;
- Canon profile;
- Language;
- OCR or page region;
- Source identity;
- A user preference;
- A factual or interpretive claim.

A correction creates a versioned `UserCorrectionRecord`.

It does not silently overwrite:

- The original model output;
- The original OCR hypothesis;
- The original source record;
- Benchmark gold;
- Shared training data.

The runtime should:

1. Reinspect the affected source or context;
2. Distinguish a demonstrated factual correction from a methodological disagreement;
3. Acknowledge a demonstrated error plainly;
4. Revise affected claims and citations;
5. Identify what changed;
6. Preserve the correction across valid compaction;
7. Ask permission before using the correction beyond the private session.

## 22. Session continuity and memory

The user should be able to view and edit durable session state such as:

- Active passage;
- Translation and canon profile;
- Language and depth;
- Selected lens;
- Sources already inspected;
- Accepted user preferences;
- User corrections;
- Open questions.

The product must not imply indefinite or perfect memory.

The user should have controls to:

```text
start a clean study
clear current session state
export the session
remove retained private uploads
inspect compaction state
```

No spiritual, personal, or sensitive inference may be retained merely because it appeared in conversation.

## 23. Multilingual and RTL user experience

The interface must keep separate:

```text
interface language
question language
answer language
source language
quotation language
translation language
pivot language
```

The UI must:

- Preserve original-language quotations;
- Label model-generated translations;
- Allow the answer language to differ from the source;
- Support code-switching;
- Render RTL text in logical order;
- Isolate mixed-direction citations and reference strings;
- Preserve Greek and Hebrew diacritics;
- Apply correct language metadata to page and span content;
- Avoid forcing English technical labels where localized terms are available.

A hidden English pivot is a product hard failure.

Language-support badges must reflect the capability-specific DR-13 status rather than one blanket “multilingual” label.

## 24. Accessibility target

The public web experience will target:

```text
WCAG 2.2 Level AA
```

as the minimum approved conformance target, with selected higher-level practices adopted where practical for important controls.

WCAG 2.2 is the current W3C Recommendation and adds requirements concerning focus visibility, dragging alternatives, target size, consistent help, redundant entry, and accessible authentication, among other criteria.[^wcag22]

Implementation principles include:

- Native semantic HTML before ARIA;
- WAI-ARIA patterns only when native elements are insufficient;
- Full keyboard operation;
- No keyboard traps;
- Visible and unobscured focus;
- Accessible names and descriptions;
- Screen-reader announcements for status changes;
- Sufficient color and non-text contrast;
- No color-only meaning;
- Text resize and spacing support;
- Reflow without loss at narrow widths and high zoom, except for genuinely two-dimensional content;
- Non-drag alternatives;
- Adequate touch targets;
- Reduced-motion support;
- No flashing or distracting animation;
- Language-of-page and language-of-parts metadata;
- Error identification, suggestions, and prevention;
- Accessible authentication without unnecessary cognitive tests.

The WAI-ARIA Authoring Practices Guide may inform keyboard, landmark, accessible-name, table, tab, disclosure, dialog, tree, and grid patterns, but the project must validate actual behavior with assistive technologies rather than assuming that ARIA attributes alone create accessibility.[^aria-apg]

### 24.1 Primary controls

For high-frequency or consequential controls, the project should aim for the stronger 44-by-44 CSS-pixel target-size practice where layout permits, while always satisfying the WCAG 2.2 AA minimum.[^target-size]

### 24.2 Two-dimensional scholarly interfaces

Translation alignments, apparatus tables, and page overlays may require two-dimensional presentation.

They must also provide:

- A linearized accessible alternative;
- Keyboard navigation;
- Meaningful row, column, and region labels;
- No hover-only details;
- A narrow-screen stacked mode where possible;
- Zoom and pan controls that do not trap focus.

### 24.3 Ancient scripts and assistive technology

The accessibility program must test:

- Polytonic Greek;
- Pointed and unpointed Hebrew;
- Cantillation;
- Biblical Aramaic;
- Latin;
- Mixed RTL/LTR citations;
- Transliteration;
- Screen-reader pronunciation and fallback behavior;
- Copy/paste fidelity.

Where assistive technology cannot reliably vocalize a source script, the interface may offer transliteration and descriptive alternatives without replacing the original.

## 25. Cognitive accessibility and technical vocabulary

The interface should reduce unnecessary cognitive load through:

- Consistent structure;
- Plain-language labels;
- Technical-term definitions;
- Progressive disclosure;
- Short direct summaries;
- Visible current context;
- Predictable source and citation behavior;
- Undoable changes;
- No hidden mode shifts;
- No unexplained abbreviations;
- Examples where a technical distinction is difficult.

Technical precision must not be removed merely to lower reading level.

The product should explain terms such as:

```text
textual variant
critical edition
manuscript witness
Vorlage
lemma
syntax
semantic range
Septuagint
apparatus
retroversion
```

at the point of need.

## 26. Responsive and mobile experience

The version-one web interface should support desktop, tablet, and mobile layouts.

Desktop may use coordinated panes.

Narrow screens should use a stacked flow such as:

```text
active context
question and answer
key evidence
expandable source inspector
translation or language detail
notes and export
```

The mobile experience should support:

- Asking and following up;
- Passage selection;
- Translation comparison in a linearized view;
- Camera or image upload;
- Source inspection;
- Note saving and export;
- Clear local-versus-cloud route disclosure.

Mobile does not require the full model to run on device in version one.

A future local 2B–4B student, native OCR, local tools, and cloud escalation remain governed by DR-02-S03 and DR-29.

## 27. Provider, model, privacy, and cost transparency

The ordinary user does not need every infrastructure detail in the primary answer.

The audit or privacy view should disclose when material:

- Whether processing occurred locally or through Lambda/project infrastructure;
- Whether an external model provider was used;
- Which broad model role was used, such as compact, large fallback, multimodal front end, or specialist;
- Whether private or restricted evidence left the local environment;
- Upload-retention state;
- Whether a model or route was blocked by rights;
- Whether the answer used live retrieval, fixed evidence, or full-canon context;
- Whether the answer incurred a paid route, where user-facing cost disclosure is applicable.

Private uploads default to:

```text
private processing
no shared training
no public benchmark use
no public release
minimum necessary retention
```

A user must explicitly authorize broader use.

## 28. Progress and long-running work

The interface may show workflow phases such as:

```text
resolving passage
checking editions
retrieving sources
comparing translations
verifying citations
archiving notes
```

These are observable workflow states—not simulated private thought.

The product must not:

- Display fabricated internal reasoning;
- Claim that a model is “thinking like a scholar”;
- Show a fake deterministic percentage;
- Provide an unsupported completion-time estimate;
- Keep the user waiting without a visible cancellation path for long-running work.

The user should be able to cancel a request. The runtime should report whether partial evidence or notes were retained.

## 29. Error, block, and abstention states

User-facing errors should be specific and actionable.

Approved categories include:

```text
NEEDS_MATERIAL_CLARIFICATION
INVALID_OR_AMBIGUOUS_REFERENCE
SOURCE_OR_EDITION_UNAVAILABLE
EVIDENCE_INSUFFICIENT
MATERIAL_EVIDENCE_CONFLICT
RIGHTS_OR_ACCESS_BLOCK
UNSUPPORTED_LANGUAGE_CAPABILITY
UNSUPPORTED_MODALITY_CAPABILITY
IMAGE_REGION_ILLEGIBLE
TOOL_OR_RETRIEVAL_FAILURE
STALE_COMPACTION_OR_SESSION_STATE
MODEL_OR_ROUTE_UNAVAILABLE
SAFETY_RESPONSE
REQUEST_OUT_OF_SCOPE
```

The product should preserve the part of the task that can be answered responsibly.

It must not expose raw stack traces, secrets, internal paths, or provider credentials.

An error may offer:

- A narrower question;
- Another edition;
- A supported language;
- A deterministic tool-only answer;
- Rehydration;
- Human review;
- A source upload;
- A later retry when the provider is unavailable.

It may not silently lower evidence standards.

## 30. Scope, refusal, and sensitive-use presentation

The interface implements DR-03 proportionately.

For mixed requests:

- Answer the legitimate biblical or supporting research component;
- Refuse or redirect only the unrelated or harmful component.

For safety-critical requests:

- Prioritize immediate safety;
- Avoid long theological debate that delays help;
- Preserve a brief non-condemning answer to the biblical question where appropriate;
- Use verified regional resources;
- Never claim divine, clerical, medical, legal, or emergency authority.

The product should not display permanent warning banners on ordinary difficult biblical topics. Controversy is not itself a safety event.

## 31. Anti-overtrust and anti-dependency design

The interface must not use:

- A clergy avatar or title that implies ordination;
- A divine voice or first-person speech as God;
- “Prophetic” personalization;
- Claims that the model knows God's will for the user;
- Streaks, spiritual scores, guilt, fear, or reward loops;
- Notifications implying that study with the assistant is spiritually necessary;
- Artificial intimacy or exclusivity;
- Prompts to replace a community, pastor, teacher, clinician, lawyer, or scholar;
- Engagement optimization that conflicts with answer quality or user agency.

The product may be warm, respectful, and supportive. It may not manufacture dependence.

The interface should avoid visual or textual design that makes a generated answer appear more authoritative than the evidence warrants.

## 32. Public expert-collaboration preview

`MVP-01_EXPERT_COLLABORATION_PREVIEW` should make it easy for a potential collaborator to understand:

- What the project has built;
- Which capabilities are deterministic or source-verifiable;
- Which cases remain `SME_REVIEW_PENDING`;
- Which specialties are needed;
- What evidence and rubric apply to each candidate case;
- How disagreement is preserved;
- How contributions are attributed;
- Whether work is volunteer, advisory, compensated, or publication-oriented.

The preview must separate:

```text
public demonstrated capability
provisional candidate analysis
human specialist validation
final gold or model-promotion evidence
```

A public comment count or poll does not adjudicate specialist truth.

## 33. Feedback and incident reporting

Users should be able to report:

```text
wrong passage or edition
wrong quotation
unsupported citation
translation-analysis problem
original-language problem
missing perspective
page/OCR problem
privacy concern
harmful or inappropriate behavior
accessibility problem
other
```

A feedback submission records the exact answer, runtime identity, sources, and user-visible state when consent and privacy permit.

Feedback does not automatically:

- Change benchmark gold;
- Retrain the model;
- Alter a source record;
- Publish the user's content.

Confirmed incidents follow the versioned correction process in DR-05, DR-09, DR-20, and DR-21.

## 34. Sharing and export boundaries

A user may share a public-safe answer or note artifact only after the system checks:

- Source display rights;
- Private uploads;
- Restricted scholarship;
- User annotations;
- Hidden benchmark material;
- Model-generated translations;
- Citations and locators;
- Currentness and correction status.

The shared artifact should display:

- Date;
- Passage and edition;
- Answer mode;
- Sources;
- Material limitations;
- Whether the analysis was provisional or SME-reviewed;
- A stable public-safe artifact identity.

Public sharing never changes a private session into training consent.

## 35. Visual design principles

DR-26 does not select final branding, colors, or typography, but locks these principles:

- Quiet, neutral visual hierarchy;
- High text readability;
- Fonts capable of robust Greek, Hebrew, Aramaic, Latin, and combining-mark rendering;
- No decorative “ancient manuscript” styling that reduces readability;
- No denominational symbol as the default product identity;
- No color-only epistemic or alignment meaning;
- Clear distinction among Scripture, translations, notes, scholarship, and user content;
- Minimal unnecessary animation;
- Consistent evidence and citation affordances;
- Responsive rather than desktop-only scholarly tools.

## 36. Performance and cost experience

Exact latency service levels remain deferred, but the product must measure and expose:

- Time to first useful status;
- Time to complete answer;
- Time to inspect first source;
- Tool and retrieval latency;
- Compact versus large-model routing;
- Context and page-processing cost;
- Cancellation success;
- Failure and fallback rate.

The runtime should prefer the least expensive route that satisfies the approved capability and assurance requirements.

It may not lower assurance, skip counterevidence, or suppress a required larger-model escalation merely to improve latency or cost.

## 37. Usability, comprehension, and trust evaluation

The product will be evaluated with distinct user groups, where feasible:

```text
self-directed Bible readers
small-group leaders and teachers
pastors
seminary or graduate students
independent researchers
qualified specialists
users of assistive technologies
multilingual users
```

Key measures include:

- Task completion;
- Time to locate and inspect evidence;
- Understanding of translation differences;
- Ability to distinguish evidence from interpretation;
- Citation navigation success;
- Correction success;
- Appropriate trust and skepticism;
- False-authority perception;
- Answer-depth fit;
- Accessibility conformance and assistive-technology behavior;
- Multilingual and RTL usability;
- Page-study success;
- Research-note usefulness;
- User-reported time saved;
- Rate of harmful or misleading overtrust.

A user preference for a fluent answer does not override source or benchmark correctness.

NIST's AI Risk Management Framework and Generative AI Profile provide a useful external reminder that trustworthy AI requires lifecycle governance, testing, evaluation, documentation, and management rather than relying on a model's apparent fluency.[^nist-rmf]

## 38. Benchmark implications

DR-26 strengthens the `RESEARCH_WORKFLOW_AND_ACCESSIBILITY` track and adds or clarifies case families for:

- Answer-depth consistency;
- Material caveat retention in Brief mode;
- Active-context visibility;
- Translation and edition correction;
- Evidence-inspector accuracy;
- Citation navigation;
- Translation Nuance alignment alternatives;
- Accessible original-language display;
- Apparatus plain-language expansion;
- Page overlay and linear alternative;
- Compaction disclosure and correction retention;
- Language and RTL behavior;
- Keyboard and screen-reader workflows;
- Responsive narrow-screen use;
- Privacy and provider-route disclosure;
- Progress-state truthfulness;
- Actionable error messages;
- Anti-overtrust and anti-dependency behavior;
- Public collaboration-preview truthfulness;
- Research-note export fidelity.

The benchmark should test both task correctness and whether the interface helps the user understand the evidence rather than merely exposing more controls.

## 39. Product hard failures

DR-26 treats these as hard failures:

- Hiding the active translation or edition when it materially affects the answer;
- Displaying a study note, heading, user annotation, or model paraphrase as Scripture;
- Rendering a direct quotation without source identity or with the wrong manifestation;
- Showing one global confidence badge that conceals a contested central claim;
- Omitting a material qualification from Brief mode;
- Changing canon, language, methodology, privacy route, or context mode silently;
- Presenting a generated translation as published wording;
- Treating alignment as semantic equivalence;
- Visually implying that translation frequency is manuscript evidence;
- Replacing uncertain page evidence with expected canonical text without disclosure;
- Claiming to have inspected an omitted or illegible image region;
- Losing a user correction through compaction or session transition;
- Hiding an English or other pivot translation;
- Making citations inaccessible by keyboard or screen reader;
- Relying on color alone for source, epistemic, or alignment distinctions;
- Making a core workflow impossible at 400% zoom or on a narrow viewport without an accessible alternative;
- Exposing private uploads or restricted evidence in a share artifact;
- Sending private evidence through an undisclosed provider route;
- Simulating divine, clerical, prophetic, medical, legal, psychological, or emergency authority;
- Using streaks, guilt, fear, exclusivity, or spiritualized engagement pressure;
- Presenting `SME_REVIEW_PENDING` content as validated scholarship;
- Displaying fake chain-of-thought, fake progress, or unsupported completion-time estimates;
- Allowing Sol to change the answer contract or benchmark behavior as a design-neutral implementation choice;
- Allowing Luna to modify UI content, product policy, release state, or benchmark cases.

## 40. Required implementation and conformance sequence

Before product promotion, Sol must implement and close:

```text
UX-00 — Canonical UX records, answer contract, and static prototypes
UX-01 — Accessible application shell and active-context model
UX-02 — Claim-ledger rendering and evidence inspector
UX-03 — Translation Nuance and original-language surfaces
UX-04 — Page-study surface and accessible region alternative
UX-05 — Session, correction, compaction, notes, and export
UX-06 — Multilingual, RTL, responsive, and assistive-technology conformance
UX-07 — Privacy, provider-route, sharing, error, and progress states
UX-08 — MVP-01 collaboration-preview surface
UX-09 — Usability and accessibility pilot with recorded defects
```

Every implementation turn must cite DR-26 and the relevant upstream designs.

A static mock that looks correct but is not connected to exact evidence and runtime state cannot close the corresponding gate.

## 41. Sol implementation discretion

Sol may determine, within later DR-28 contracts:

- Framework-local component organization;
- State-management implementation;
- Design-system implementation mechanics;
- Equivalent accessible HTML and interaction techniques;
- Test fixtures and automation;
- Performance optimizations that preserve every approved behavior;
- Internal names that do not change public contracts.

Sol may not independently change:

- Product surfaces;
- Answer modes;
- Progressive-disclosure rules;
- Evidence and citation semantics;
- Source and authority distinctions;
- User-correction behavior;
- Privacy defaults;
- Accessibility target;
- Multilingual and RTL rules;
- Anti-overtrust controls;
- Public collaboration claims;
- Hard failures;
- Benchmark meaning.

A material conflict returns:

```text
BLOCKED_REQUIRES_DESIGN_REVIEW
```

## 42. Decisions DR-26 would lock

Approval would establish that:

1. Biblical Scholar Lab is a research workspace, not only a chat interface.
2. `ASK_AND_STUDY`, `PASSAGE_WORKSPACE`, `TRANSLATION_COMPARE`, `PAGE_STUDY`, `SOURCE_AND_EVIDENCE_INSPECTOR`, `RESEARCH_NOTES_AND_EXPORT`, and the collaboration preview are first-class product surfaces.
3. Active passage, edition, canon, language, depth, lens, context mode, and material provider/privacy state remain inspectable and correctable.
4. Brief, Study, and Scholarly modes render from one verified claim ledger.
5. Study is the default mode.
6. Concision may not remove material uncertainty, counterevidence, or source limitations.
7. Perspective, method, and devotional intent remain separate from answer depth.
8. The answer contract preserves direct answer, source identity, issue, evidence, alternatives, assessment, uncertainty, and sources.
9. Progressive disclosure cannot hide material evidence boundaries.
10. Confidence remains claim-specific and categorical unless calibrated probabilities are separately approved.
11. Citations are claim-linked, inspectable, manifestation-specific, and accessible.
12. Translation Nuance receives a dedicated comparison workspace.
13. Original-language display is contextual and fallacy-aware rather than gloss-driven.
14. Witnesses, apparatuses, ancient versions, modern translations, conjectures, and reports remain visually distinct.
15. Page pixels, OCR, VLM inference, canonical text, and user correction remain separate.
16. Context and compaction state are user-inspectable.
17. Exact reuse after compaction requires rehydration.
18. User corrections create versioned records and are not used for shared training by default.
19. Research notes and public share artifacts preserve source, uncertainty, provenance, and rights.
20. Multilingual, code-switched, RTL, and ancient-script behavior are product-level requirements.
21. The public web application targets WCAG 2.2 AA, with stronger practices for important controls where practical.
22. Accessibility is tested with real assistive technologies and cannot be inferred from ARIA markup alone.
23. Mobile and narrow-screen workflows receive linearized alternatives to two-dimensional scholarly views.
24. Private uploads default to no shared training, benchmark, or release use.
25. Progress indicators expose workflow state rather than simulated thought.
26. Error states are specific, actionable, and preserve answerable portions.
27. DR-03 safety is applied proportionately without making ordinary controversial study feel unsafe or blocked.
28. The product prohibits dark patterns, spiritual dependence, and simulated divine or clerical authority.
29. `MVP-01` clearly separates demonstrated P0/P1 capability from provisional P2 collaboration candidates.
30. Public feedback does not automatically change gold, source records, or training data.
31. Visual design remains quiet, readable, script-capable, neutral, and evidence-centered.
32. Usability, comprehension, accessibility, trust calibration, latency, and cost are evaluated alongside correctness.
33. Sol implements the approved UX; Luna only runs frozen campaigns; ChatGPT and Joseph retain design and approval authority.

## 43. Decisions intentionally deferred

DR-26 does not yet freeze:

- Public product name or brand;
- Exact visual style, color palette, iconography, or typography;
- Exact web or native application framework;
- Exact component library;
- Exact authentication and account design;
- Exact hosting architecture;
- Exact responsive breakpoints;
- Exact analytics provider or whether one is used;
- Exact retention periods for user sessions and uploads;
- Exact citation style default;
- Exact export formats beyond the initial priorities;
- Exact collaboration-review interface and compensation model;
- Exact latency service levels;
- Exact local-versus-cloud routing UI;
- Exact mobile native-app scope;
- Exact pronunciation or audio feature;
- Exact accessibility certification provider;
- Exact notification system;
- Exact public sharing domain;
- Exact paid-product or subscription model;
- Any engagement-optimization feature;
- Any final release date.

Those are resolved in DR-28, DR-29, release-specific designs, public-preview evidence, and implementation review.

## 44. Approval statement

> **Biblical Scholar Lab will present its source-grounded scholarly system through an accessible, progressive, evidence-centered research workspace rather than a chat interface that hides its active assumptions. Users of any credential level will be able to ask ordinary Bible-study questions, compare translations, inspect original languages, analyze photographed pages, review sources, correct the system, and export research notes while retaining access to the exact passage, edition, canon, language, methodology, context mode, evidence, counterevidence, uncertainty, and rights state that materially affect the answer. Brief, Study, and Scholarly modes will render from one verified claim ledger; simplicity may reduce visible technical depth but may not change conclusions or suppress material qualifications. Citation and evidence controls will reveal exact source identity, version, locator, inspection level, quotation and translation provenance, publication status, source role, and claim entailment. Translation Nuance, original-language, textual-critical, ancient-version, and page-study surfaces will preserve alignment alternatives, source-versus-translation distinctions, OCR/VLM/canonical-text differences, and unresolved evidence rather than simulating certainty. Context and compaction state will remain inspectable, user corrections will be versioned and revalidated, and exact scholarly reuse will require source rehydration. The public web application will target WCAG 2.2 Level AA, use semantic and keyboard-operable patterns, provide accessible alternatives for two-dimensional alignment and page interfaces, support ancient scripts, multilingual and RTL content, and test with actual assistive technologies. Private uploads will remain private and excluded from shared training by default; model routes, evidence modes, and material access limits will be disclosed; and public share artifacts will be rights-filtered. Progress indicators will describe observable workflow rather than private thought, error states will be actionable, and the product will prohibit simulated divine or clerical authority, fake certainty, spiritualized engagement pressure, dependency-building dark patterns, and unvalidated specialist claims. `MVP-01_EXPERT_COLLABORATION_PREVIEW` will clearly separate demonstrated `REV-P0` and reviewed `REV-P1` capability from `SME_REVIEW_PENDING` collaboration candidates. Sol will implement the approved user experience and accessibility contracts, Luna may only execute frozen operational campaigns, ChatGPT will review implementation and product evidence, and Joseph Abbud will retain sole authority over merge, public claims, and release.**

---

## References

[^wcag22]: W3C, “Web Content Accessibility Guidelines (WCAG) 2.2,” W3C Recommendation. WCAG 2.2 addresses perceivability, operability, understandability, and robustness across devices and adds criteria including focus not obscured, dragging alternatives, target size, consistent help, redundant entry, and accessible authentication: <https://www.w3.org/TR/WCAG22/>.

[^aria-apg]: W3C Web Accessibility Initiative, “ARIA Authoring Practices Guide.” The guide provides patterns and practices for accessible semantics, keyboard interaction, landmarks, names and descriptions, tables, grids, and common widgets: <https://www.w3.org/WAI/ARIA/apg/>.

[^target-size]: W3C WAI, “Understanding Success Criterion 2.5.8: Target Size (Minimum)” and “2.5.5: Target Size (Enhanced).” WCAG 2.2 AA defines a 24-by-24 CSS-pixel minimum or spacing alternative, while the enhanced AAA target is 44 by 44 CSS pixels: <https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum> and <https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced>.

[^nist-rmf]: NIST, “Artificial Intelligence Risk Management Framework (AI RMF 1.0)” and “Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile.” These voluntary frameworks emphasize lifecycle risk governance, mapping, measurement, management, testing, evaluation, verification, validation, documentation, and transparency for AI systems: <https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10> and <https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence>.
