# DR-16 — Runtime Scholar Harness

| Field | Value |
|---|---|
| Design ID | `DR-16` |
| Status | `APPROVED` |
| Approval date | 2026-08-16 |
| Project owner | Joseph Abbud |
| Designer and independent reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2 and supplements; DR-03; DR-04; DR-05; DR-06; DR-07; DR-08; DR-09; DR-10; DR-11; DR-12; DR-13; DR-14; DR-15 |
| Implementation authority | GPT-5.6 Sol, under the approved design |
| Execution authority | GPT-5.6 Luna only for frozen campaigns delegated by Sol under a later approved campaign envelope |
| Experiment-design authority | ChatGPT designs; Joseph Abbud approves; Sol implements only the approved design |
| Changes if approved | Establishes the deterministic, policy-governed Runtime Scholar Harness that classifies requests, plans evidence acquisition, exposes typed tools, composes context, routes among model roles, verifies structured claims and citations, renders accessible answers, maintains compactable session state, and produces an auditable receipt without allowing the model to become the authority over evidence, rights, safety, or experiment design; also establishes a framework-neutral project-owned runtime core, a deterministic reference executor, LangGraph v1 as the provisional durable workflow substrate, and the OpenAI Agents SDK only as an optional bounded adapter rather than the authoritative runtime |

## 1. Purpose

The approved designs through DR-15 define the scholarly evidence model, Translation Nuance Core, linguistic representation, ancient-version and apparatus policy, scholarship and citation model, rights architecture, model-family candidates, multilingual and multimodal systems, and long-context composer.

Those components do not by themselves determine how a user request becomes a trustworthy answer.

Biblical Scholar Lab still needs a runtime architecture that can answer questions such as:

- “Why does my Bible say *servant* while another says *slave*?”
- “Does this difference reflect a Greek manuscript variant?”
- “What does this participle do in the argument?”
- “How does this New Testament quotation relate to the Septuagint and Hebrew text?”
- “What are the major interpretations, and what evidence supports each?”
- “Can you read this photographed study-Bible page and explain the note?”
- “Write a Python script to compare lemma frequencies in Romans and Galatians.”
- “Explain this passage accessibly, but show me the sources.”
- “Answer in Spanish while preserving the Greek and the wording of a German article.”

The runtime must decide, reproducibly:

- What task is actually being requested;
- Whether a clarification is materially necessary;
- Which canon, edition, language, passage, source, and user profile apply;
- Which safety or sensitive-use overlay is relevant;
- Which evidence layers are required;
- Which deterministic tools and retrieval routes may be used;
- Which model role and reasoning mode are justified;
- Which context mode and compaction state apply;
- Whether the evidence is sufficient;
- Which claims the model is permitted to make;
- Which claims were actually verified;
- How the result should be rendered for a nonexpert or specialist user;
- What must be recorded for audit, reproducibility, cost, and future correction.

DR-16 defines that runtime contract.

It does not select a web framework, database product, model winner, retriever, cloud provider, exact prompt wording, UI component library, or numerical thresholds. It does select the **logical runtime ownership boundary** and a provisional execution strategy: Biblical Scholar Lab owns the authoritative runtime core and domain contracts; a small deterministic reference executor serves as the conformance oracle; LangGraph v1 is the provisional durable workflow and persistence substrate; and the OpenAI Agents SDK may be used only through bounded adapters or comparative experiments rather than as the governing runtime. Exact package versions, checkpointer products, deployment topology, queues, and observability systems remain later implementation and evidence-gated decisions.

## 2. Governing principle

> **The model is a bounded reasoning and language component inside an evidence-governed scholarly runtime. The runtime—not the model—owns task identity, policy, rights, tool authority, source identity, evidence sufficiency, verification, session state, and audit. A fluent answer cannot bypass the contracts required to make it trustworthy.**

The intended execution flow is:

```text
user request and study profile
    → request normalization without semantic rewriting
    → domain, intent, discourse, and risk classification
    → reference, edition, language, and source resolution
    → task and assurance-class selection
    → deterministic research-plan construction
    → rights-aware tool and evidence acquisition
    → evidence-sufficiency evaluation
    → Context Composer and optional compaction/rehydration
    → model-route and reasoning-mode execution
    → typed answer candidate
    → deterministic and evidence-based verification
    → bounded repair, escalation, qualification, or abstention
    → user-facing answer rendering
    → immutable runtime audit receipt and session-state update
```

The system may use a model to propose a classification, plan, diagnosis, or explanation. Every such proposal remains subordinate to the approved schemas, deterministic constraints, evidence records, and verification rules.

## 3. The `ScholarRuntimeOrchestrator`

The architecture introduces a deterministic or explicitly rule-governed component:

```text
ScholarRuntimeOrchestrator
SRO
```

The SRO is responsible for:

- Creating the authoritative runtime state machine;
- Binding the request to exact design and policy revisions;
- Preserving the user’s wording and explicit choices;
- Applying DR-03 scope and sensitive-use policy;
- Resolving DR-04 reference and canon context;
- Selecting the task template and assurance class;
- Constructing or validating the research execution plan;
- Issuing narrow tool capabilities;
- Enforcing DR-10 rights before retrieval or model transmission;
- Invoking the DR-15 Context Composer;
- Selecting an approved model route and reasoning mode;
- Validating structured output;
- Invoking the TNSK, Page Evidence Kernel, citation verifiers, linguistic validators, and other approved components;
- Enforcing bounded repair and escalation;
- Rendering only verified or appropriately qualified claims;
- Updating session state and compaction artifacts;
- Producing an immutable audit receipt.

The SRO may determine that a request is incomplete, unsupported, out of scope, unsafe, blocked by rights, or beyond the verified capability of the available system.

It may not decide a contested scholarly issue by hard-coded preference unless an approved design or reviewed evidence record supplies that decision.

## 4. Logical runtime planes

The runtime is separated into eight logical planes.

### 4.1 Interaction and identity plane

Owns:

- User request and exact wording;
- Conversation and session identity;
- Study profile;
- Canon, edition, language, locale, and answer-depth preferences;
- User corrections;
- Workspace and privacy scope;
- Requested output form.

### 4.2 Scope, policy, and risk plane

Owns:

- Domain relevance;
- Supporting-task classification;
- Intent;
- Discourse status;
- Sensitive-use and crisis overlay;
- Allowed response behavior;
- Required resource resolution;
- Refusal or partial-compliance boundaries.

### 4.3 Research planning plane

Owns:

- Task type;
- Assurance class;
- Required evidence layers;
- Tool plan;
- Retrieval plan;
- Model route;
- Context mode;
- Verification plan;
- Budget and stop conditions.

### 4.4 Tool and evidence plane

Owns:

- Deterministic passage and reference tools;
- Linguistic tools;
- Translation Nuance tools;
- Ancient-version and apparatus tools;
- Scholarship and citation tools;
- Multimodal and page tools;
- Rights and entitlement checks;
- Current-resource and publication-status checks;
- Evidence records and source handles.

### 4.5 Context and model-execution plane

Owns:

- Context plans and packets;
- Compaction and rehydration;
- Model adapter and route;
- Reasoning mode;
- Tool loop;
- Structured model output;
- Resource usage.

### 4.6 Verification and adjudication plane

Owns:

- Schema validation;
- Source identity and passage verification;
- Claim/evidence entailment;
- Quotation and locator verification;
- Translation Nuance semantic validation;
- Linguistic and apparatus validation;
- Rights and privacy validation;
- Safety and scope validation;
- Multilingual and page-grounding validation;
- Promotion, qualification, removal, escalation, or abstention decisions.

### 4.7 Presentation plane

Owns:

- Brief, Study, and Scholarly rendering;
- Evidence and uncertainty visibility;
- Source and edition labels;
- Published versus generated translation labels;
- Accessible terminology;
- Citation display;
- Exportable research-note structure.

### 4.8 State, audit, and correction plane

Owns:

- Append-only runtime events;
- Session research state;
- Compaction artifacts;
- User corrections;
- Model, tool, packet, and verifier identity;
- Cost and latency;
- Failures and fallbacks;
- Reproducibility;
- Privacy-aware logs;
- Audit receipt.

An implementation may deploy these planes in one process or several services. Their logical authority and boundaries remain unchanged.

## 5. Canonical runtime entities

### `ScholarRequestEnvelope`

The exact request entering the runtime:

```text
request_id
session_id
user-message revision and exact wording
attachments and source-artifact handles
explicit passage, edition, canon, language, and method selections
requested answer language and depth
requested output format
privacy and workspace scope
user-provided constraints
received timestamp
content hash
```

The system may create normalized views for parsing. It may not overwrite the original request.

### `StudyProfile`

A versioned, user-controlled profile containing only approved preferences such as:

```text
preferred interface and answer language
preferred Bible translation or edition
canon and versification profile
answer-depth default
citation style preference
methodological or confessional lens, when explicitly selected
accessibility preferences
privacy and retention preferences
cost or latency preference
```

A profile is a convenience input, not theological authority. Material ambiguity still requires disclosure or clarification.

### `RuntimeClassificationRecord`

Records independent classifications for:

```text
domain relevance
intent
discourse status
risk level
task types
assurance class
language and script
modality
clarification necessity
```

Each classification retains source, model or rule identity, confidence, alternatives, and review state.

### `ResearchExecutionPlan`

The approved plan for one request:

```text
plan_id
request and session revisions
applicable design and policy revisions
task types and assurance class
resolved passage, edition, canon, language, and source identities
required evidence layers
tool operations and dependencies
retrieval routes
rights and privacy requirements
context mode
model route and reasoning mode
verification suite
budgets, retry limits, and stop conditions
clarification, fallback, escalation, and abstention rules
content hash
```

### `ToolCapabilityGrant`

A narrow, temporary authorization binding:

```text
tool identity and revision
permitted operation
request and plan identity
authorized source and rights scope
argument constraints
result-display constraints
call count and budget
expiration
issuer
content hash or signature
```

The model never receives general cloud, filesystem, network, or database authority merely because one tool is available.

### `ToolCallRecord`

Records:

```text
tool capability and call identity
validated arguments
input source and revision handles
start and end times
result status
structured result and evidence handles
warnings and alternatives
rights and display status
retry or fallback state
resource usage
content hash
```

### `EvidenceLedger`

An append-only request-scoped index of evidence considered, including:

```text
evidence identity
source type and role
exact source revision and selector
language and translation provenance
review and evidential-proximity state
rights and access state
claim types it may support
material counterevidence relation
selected, rejected, omitted, or unavailable state
reason for inclusion or exclusion
```

### `ClaimLedger`

Implements the DR-02 and DR-09 claim model:

```text
claim_id
claim text and type
epistemic status
method
supporting evidence
counterevidence
source-role compatibility
consensus or landscape status
translation provenance
verification outcomes
known limitations
rendering state
```

### `ScholarAnswerCandidate`

The model-produced structured candidate before final rendering:

```text
request and plan identity
model and packet identity
answer-language identity
claims and claim/evidence links
quotations and locators
translation and linguistic analyses
material alternatives and counterevidence
uncertainty and missing evidence
citations
proposed user-facing answer
abstention or escalation request
concise rationale
```

### `ScholarAnswerArtifact`

The verified and rendered answer:

```text
answer identity and revision
verified claim ledger revision
rendering mode and language
user-facing text
citations and source links
visible uncertainty and omissions
model-generated translation labels
verification summary
rights and display state
content hash
```

### `RuntimeAuditReceipt`

The authoritative execution receipt described later in this review.


## 6. Authoritative runtime state machine

Every request advances through an append-only state machine. The SRO validates each transition and records the responsible component, exact input and output revision, timestamp, and reason.

The principal states are:

```text
RECEIVED
NORMALIZED
CLASSIFIED
POLICY_AND_SAFETY_EVALUATED
IDENTITIES_RESOLVED
PLAN_FROZEN
EVIDENCE_ACQUIRING
EVIDENCE_ASSESSED
CONTEXT_COMPOSED
MODEL_EXECUTING
CANDIDATE_RECEIVED
VERIFYING
REPAIRING
RENDERED
AUDITED
COMPLETE
```

Branch and terminal states include:

```text
NEEDS_MATERIAL_CLARIFICATION
PARTIAL_SCOPE_REDIRECT
SAFETY_RESPONSE
BLOCKED_BY_RIGHTS
BLOCKED_BY_ACCESS
BLOCKED_BY_EVIDENCE
BLOCKED_BY_CAPABILITY
ESCALATED_TO_APPROVED_ROUTE
HUMAN_REVIEW_PENDING
ABSTAINED
FAILED
CANCELLED_BY_USER
```

The state machine enforces at least these invariants:

- A request cannot reach `MODEL_EXECUTING` before its plan, rights route, and context packet are frozen.
- A consequential answer cannot reach `RENDERED` before structured verification.
- A repaired candidate returns to `VERIFYING`; it does not inherit the previous candidate's pass state.
- A deterministic-only answer may bypass model execution but not identity, rights, rendering, and audit requirements.
- A safety response may intentionally use a shortened path, but its resource, location, and authority claims still require the applicable verification.
- A blocked state cannot be converted into `COMPLETE` through model prose.
- Every fallback or escalation creates a visible transition rather than silently replacing the failed route.
- User cancellation stops new work and records which private or billable operations were already performed.

An implementation may use events, workflows, transactions, or another mechanism. It may not allow unrecorded state changes or skip a required authority boundary.


## 7. Task taxonomy

A request may contain more than one task type.

The initial extensible taxonomy includes:

```text
PASSAGE_EXPLANATION
TRANSLATION_COMPARISON
TRANSLATION_NUANCE_DIAGNOSIS
ORIGINAL_LANGUAGE_ANALYSIS
TEXTUAL_CRITICISM
ANCIENT_VERSION_ANALYSIS
HEBREW_BIBLE_OR_LXX_RELATIONSHIP
INTERTEXTUALITY_ANALYSIS
ANCIENT_CONTEXT_RESEARCH
SCHOLARSHIP_DISCOVERY
SCHOLARSHIP_SYNTHESIS
CITATION_OR_BIBLIOGRAPHY
PAGE_OR_DOCUMENT_STUDY
DEVOTIONAL_REFLECTION
TEACHING_OR_SERMON_TRANSFORMATION
RESEARCH_CODE_OR_DATA_SUPPORT
NOTE_OR_TABLE_ORGANIZATION
SCOPE_REDIRECT
SENSITIVE_USE_SUPPORT
```

A user’s credentials do not determine whether a task is permitted. Task complexity affects planning and explanation, not access to the evidence.

## 8. Runtime assurance classes

Answer depth and assurance are independent.

A user may request a brief answer to a high-assurance question or a scholarly explanation of a low-risk passage.

The proposed classes are:

### `A0_CONVERSATIONAL`

For greetings, navigation, scope explanation, or responses containing no consequential external scholarly claim.

Requirements are minimal, but scope and safety still apply.

### `A1_STANDARD_STUDY`

For ordinary passage explanation and common translation questions.

Requires:

- Exact passage and edition resolution when quoting;
- Suitable evidence retrieval;
- Basic claim and citation verification;
- Visible uncertainty where material.

### `A2_SCHOLARLY_RESEARCH`

For original-language analysis, textual criticism, Translation Nuance, intertextuality, current scholarship, or multi-source synthesis.

Requires:

- Full evidence and claim ledgers;
- Material counterevidence;
- Method and source-role validation;
- Claim-level citation entailment;
- Structured verification;
- Stronger escalation and abstention rules.

### `A3_SENSITIVE_OR_DECISION_BEARING`

For crisis, abuse, medical, legal, coercive, or other high-stakes applications.

Requires:

- DR-03 safety overlay;
- Verified current resources where applicable;
- Minimal necessary personal-data handling;
- No unverified professional or spiritual authority;
- Proportionate and concise response behavior.

The runtime may elevate assurance. It may not lower an assurance class merely to reduce cost.

## 9. Scope, safety, and research planning are separate decisions

A request can be:

- Core biblical scholarship and ordinary risk;
- Supporting research and ordinary risk;
- Core biblical content with high-stakes application;
- Out of scope but harmless;
- Mixed, with one permitted and one prohibited component.

The SRO therefore performs scope and risk analysis before detailed research planning, but does not confuse them.

Examples:

- A Python script for Greek lemma counts is supporting in-scope and ordinarily safe.
- A historical question about biblical warfare is core in-scope and ordinarily safe.
- A request to use Scripture to justify imminent harm is core-domain language with a crisis-risk overlay.
- An unrelated résumé request is out of scope but not dangerous.

The assistant should answer the legitimate component and refuse or redirect only the prohibited component where possible.

## 10. Clarification is required only for material ambiguity

The runtime asks a clarifying question when ambiguity changes:

- The work or passage;
- The textual form;
- The edition or translation under comparison;
- The canon or versification;
- The requested perspective or method;
- The answer language;
- The evidence required;
- The safety outcome;
- The operation’s rights or privacy state.

It does not ask needless questions merely because several harmless defaults exist.

When a safe, reversible default is used, the answer identifies it where material.

## 11. Research planning is template-governed before it is learned

The baseline uses deterministic or rule-governed task templates.

A model may propose a `ResearchPlanCandidate`, but the SRO must validate it against mandatory evidence requirements.

### Translation comparison template

At minimum considers:

```text
exact translation editions and passage realizations
source textual state
source-language text and linguistic analyses
textual-variant evidence where relevant
TNC alignments, lineage, and causal alternatives
target-language constraints
material counterevidence
```

### Original-language template

At minimum considers:

```text
exact edition and text view
segmentation
lemma and morphology alternatives
syntax alternatives
sense, reference, discourse, and context
translation implications
word-study-fallacy validation
```

### Textual-criticism template

At minimum considers:

```text
variation unit and edition scope
witness and apparatus identity
coverage and silence policy
ancient versions and patristic evidence where relevant
conjecture versus attestation
method and counterevidence
```

### Scholarship-synthesis template

At minimum considers:

```text
question and field scope
current evidence horizon
source identity and publication status
methodological and language coverage
claim-level evidence
source dependence
material minority or dissenting positions
consensus restraint
```

### Page-study template

At minimum considers:

```text
source artifact and privacy
PEK and MPEP
region role and authority
specialist recognition and VLM observations
edition and passage resolution
deterministic text verification
page-specific notes and paratext
scholarly evidence where requested
```

Templates prevent a model from skipping decisive evidence merely because it can generate a plausible answer more cheaply.

## 12. Evidence-sufficiency states

Before final generation, the SRO records one of:

```text
SUFFICIENT_FOR_REQUESTED_CLAIM
SUFFICIENT_WITH_QUALIFICATION
PARTIAL_EVIDENCE
MATERIAL_CONFLICT
MISSING_PRIMARY_EVIDENCE
MISSING_COUNTEREVIDENCE
BLOCKED_BY_RIGHTS
BLOCKED_BY_ACCESS
BLOCKED_BY_LANGUAGE_CAPABILITY
BLOCKED_BY_MODEL_CAPABILITY
BLOCKED_BY_TOOL_FAILURE
UNKNOWN_SUFFICIENCY
```

The state may be different for different claims in one answer.

A system cannot convert `PARTIAL_EVIDENCE` into apparent certainty through fluent wording.

## 13. Typed, allowlisted tools

The model has access only to task-specific, typed tools issued through `ToolCapabilityGrant` records.

Initial logical tool families include:

### Canon and passage tools

```text
resolve_reference
map_reference_scheme
get_passage
compare_edition_passages
get_textual_form
```

### Linguistic tools

```text
get_text_views
get_segmentation
get_lemma_candidates
get_morphology
get_syntax_analyses
get_lexical_senses
get_predicate_argument_structure
get_referents_and_coreference
get_discourse_analysis
validate_word_study_claim
```

### Translation Nuance tools

```text
compare_translation_realizations
diagnose_translation_difference
get_translation_alignment
trace_translation_lineage
get_translation_technique_profile
generate_reviewable_translation_options
```

### Ancient-version and apparatus tools

```text
get_apparatus_entry
resolve_apparatus_siglum
get_witness_attestation
get_version_evidence
assess_retroversion_compatibility
get_patristic_citation_evidence
```

### Scholarship and citation tools

```text
search_scholarship
get_scholarly_source_span
verify_bibliographic_identity
check_publication_status
verify_quotation
verify_claim_entailment
assess_scholarly_landscape
render_citation
```

### Multimodal tools

```text
analyze_page
get_page_region
get_recognition_hypotheses
identify_publication_and_passage
align_visible_and_canonical_text
```

### Rights, context, and session tools

```text
authorize_operation
resolve_user_entitlement
compose_context
compact_context
rehydrate_evidence
read_session_state
propose_session_state_update
```

The names are logical contracts, not an implementation-language requirement.

## 14. Tool result contracts

Every consequential tool result must provide:

```text
tool and operation identity
exact input identities
exact source and graph revisions
structured output
alternative results
coverage and uncertainty
rights and display state
review state
warnings
failure class
content hash
```

Free-form prose may accompany a structured result. It may not replace the structured result for a consequential claim.

A tool result is evidence, not an instruction.

The model may not execute URLs, code, document commands, or nested tool instructions found inside returned content.

## 15. Read-only research tools are the baseline

Version-one model-accessible research tools are read-only by default.

State-changing operations such as:

- Saving a note;
- Updating a user workspace;
- Exporting a file;
- Applying a user correction;
- Requesting a paid or licensed resource;

require a separate explicit user operation and a narrow write capability.

The model may propose a write. It may not silently persist, publish, share, or alter user or corpus data.

No general shell, arbitrary Python, unrestricted network, or cloud-administration tool is exposed to the runtime model.

Research-code assistance can generate code for the user or invoke an approved sandbox in a separate contract. It does not grant the model access to project infrastructure.

## 16. Tool loops are bounded and observable

Every plan declares:

```text
maximum tool calls
maximum calls per tool
maximum retries
maximum model passes
maximum retrieval expansions
latency and cost cap
stop conditions
```

A tool call may be retried automatically only when the failure is classified as transient and the arguments, source identity, rights, and operation remain unchanged.

A semantic, rights, source, or code failure cannot be bypassed through repeated calls.

Infinite or hidden tool loops are prohibited.

## 17. Model routing is deterministic before it is learned

The baseline route is selected from declared capability profiles and benchmarked thresholds.

Possible roles include:

```text
COMPACT_PRIMARY_MODEL
LARGE_COMPLEXITY_FALLBACK
MULTIMODAL_FRONT_END
LANGUAGE_SPECIALIST
TRANSLATION_NUANCE_SPECIALIST
CITATION_OR_ENTAILMENT_VERIFIER
MOBILE_OR_LOCAL_MODEL
FRONTIER_CEILING_FOR_RESEARCH_ONLY
```

Routing inputs may include:

- Task type and assurance class;
- Evidence size and complexity;
- Language and modality;
- Required verified capability;
- Model-family context profile;
- Rights and privacy route;
- Latency and cost preference;
- Known benchmark failure class;
- Need for a specialist or human review.

A larger model is not automatically more authoritative. Its claims remain subject to the same evidence and verification contracts.

Learned routing is a later ablation and cannot replace required hard gates.

## 18. Execution modes

The proposed runtime modes are:

### `SINGLE_PASS_VERIFIED`

One model generation followed by deterministic and claim-level verification.

Appropriate for many A1 tasks.

### `PLAN_EXECUTE_VERIFY`

A model may propose tool calls or structured analyses within the approved plan, followed by final synthesis and verification.

This is the principal A2 mode.

### `DUAL_MODEL_CROSSCHECK`

A second model or specialist independently evaluates a named failure-sensitive component.

It is not a general “two models agree, therefore true” rule. Shared training data and correlated errors remain possible.

### `LARGE_MODEL_ESCALATION`

The compact model or SRO escalates a bounded task and evidence packet to the approved large model when a verified compact-model limitation applies.

### `HUMAN_REVIEW_REQUIRED`

Used when the system lacks sufficient capability, rights, evidence, or calibration for a consequential claim or release decision.

### `DETERMINISTIC_ONLY`

Used where exact tools can answer without model inference, such as passage lookup, reference mapping, or citation formatting.

The runtime selects the least costly mode that meets the required assurance.

## 19. Every model invocation consumes an immutable context packet

The SRO invokes the DR-15 Context Composer for every consequential model call.

The model never receives an untracked concatenation of:

- User text;
- Retrieved documents;
- Tool output;
- Full-canon text;
- Conversation summaries;
- Page OCR;
- System instructions.

The packet binds exact roles, evidence handles, authority labels, rights, model processor, token counts, included and omitted regions, compaction state, and content hash.

A new tool result or rehydration creates a new packet revision.

## 20. Compaction invocation belongs to the runtime

The SRO decides when compaction is eligible based on:

- Context budget;
- Session length;
- Task phase transition;
- Completed evidence units;
- Expected future relevance;
- Rights and retention requirements;
- Model route;
- Benchmark-validated compaction policy.

The default order is:

```text
K0 lossless deduplication
→ K1 structured state extraction
→ K2 evidence-handle compaction
→ K3 reviewed abstract, when available
→ K4 model summary candidate only when disclosed and allowed
→ K5 learned projection only under a separately approved experiment
```

Before compaction, the SRO freezes the authoritative session state and protected-evidence audit.

Before an exact or consequential reuse, it invokes rehydration.

A compaction failure does not authorize silent loss. The runtime retains the uncompacted state, reduces scope, selects another route, or asks the user to continue in a new bounded session.

## 21. Structure-first model output

A model must first produce a `ScholarAnswerCandidate` conforming to the approved schema.

The structure includes:

- Typed claims;
- Epistemic status;
- Evidence and counterevidence handles;
- Source type and methodology;
- Translation provenance;
- Quotations and locators;
- Material alternatives;
- Missing evidence;
- Uncertainty;
- Proposed citations;
- User-facing answer draft.

Schema validity is necessary but not sufficient.

The runtime does not accept a free-form answer and attempt to invent its evidence afterward.

## 22. Verification is layered

The baseline verifier suite includes:

### Structural verification

- Schema and type validity;
- Required fields;
- Identifier and revision validity;
- No unknown tool or evidence handles.

### Source and reference verification

- Correct passage, edition, textual form, canon, and versification;
- Exact source-selector validity;
- No invalid cross-edition locator transfer.

### Text and quotation verification

- Exact wording;
- Ellipses and bracketed changes;
- Published versus generated translation;
- OCR or page-source disclosure.

### Linguistic verification

- Morphological and syntactic compatibility;
- Alternative analyses;
- Source-native annotation provenance;
- Word-study-fallacy checks.

### Translation Nuance verification

- Alignment and source-target identity;
- Cause-axis and causal-role compatibility;
- Lineage and source dependence;
- Textual variant versus translation choice;
- Intent/effect separation;
- Ancient-version restraint.

### Scholarship and citation verification

- Bibliographic identity;
- Publication version and status;
- Claim/citation entailment;
- Locator;
- Secondary-citation disclosure;
- Consensus evidence.

### Rights and privacy verification

- Authorized retrieval and model route;
- Display and quotation rights;
- No private or restricted leakage;
- Artifact-specific output restrictions.

### Scope and safety verification

- Proper refusal or partial compliance;
- No professional, clerical, divine, or crisis-authority overclaim;
- Current verified resources where required;
- No harmful or coercive application.

### Multilingual and multimodal verification

- Answer language;
- Source and pivot provenance;
- RTL and script integrity;
- Page-region grounding;
- Scripture versus paratext;
- No visual prompt-injection compliance.

Model-assisted verification may help classify or triage a claim, but the generating model cannot serve as the sole verifier for its own consequential output. Hard source, quotation, rights, reference, tool, and schema checks remain deterministic or source-grounded. Expert-rubric claims may use an independent model as supplementary evidence, but benchmark and product promotion cannot rest only on self-judgment or one correlated model family.

## 23. Verification outcomes are claim-specific

Each claim receives one of:

```text
VERIFIED
VERIFIED_WITH_QUALIFICATION
PARTIALLY_VERIFIED
CONFLICTED_EVIDENCE
UNSUPPORTED
NOT_CHECKABLE_WITH_AVAILABLE_EVIDENCE
BLOCKED_BY_RIGHTS
BLOCKED_BY_CAPABILITY
REJECTED_HARD_FAILURE
```

One answer may contain several states.

The renderer may include a partially verified claim only if its qualification is explicit and the remaining uncertainty is material to the user.

An unsupported or rejected claim is removed, replaced with a supported formulation, or causes abstention.

## 24. Repair is bounded

When verification fails, the SRO may perform only approved remediation actions:

```text
retrieve missing evidence
rehydrate compacted evidence
correct an exact quotation from the deterministic source
remove an unsupported claim
qualify an overclaim
request clarification
invoke an approved specialist
escalate to the approved larger model
abstain from the unsupported portion
```

The runtime may not enter an indefinite model-self-critique loop.

Each repair creates a new answer-candidate and packet or evidence revision and is recorded in the audit receipt.

A hard rights, source-identity, safety, or policy failure cannot be “reasoned around.”

## 25. Rendering is downstream from verification

The answer renderer receives only verified or appropriately qualified structured claims.

It supports the DR-01 modes:

```text
BRIEF
STUDY
SCHOLARLY
```

### Brief

Provides the direct answer, the principal distinction, and minimal evidence.

### Study

Provides accessible context, translation or interpretive alternatives, important evidence, and citations.

### Scholarly

Provides edition-level identity, original-language analysis, textual and ancient-version evidence, method, material positions, assessment, uncertainty, and fuller citations.

The same verified claim ledger underlies all three modes.

A simpler answer may hide technical detail. It may not change the underlying conclusion or remove a material qualification.

## 26. Default answer architecture

Where appropriate, the renderer uses this logical structure:

```text
Text
Issue
Evidence
Translation or interpretive options
Assessment
Uncertainty and limitations
Sources
```

The interface may collapse or rename sections for readability.

The answer should distinguish:

- What the text directly attests;
- What the language permits or favors;
- What a translation makes explicit;
- What a scholar or tradition argues;
- What the system assesses;
- What remains unknown.

Technical terms should be explained for general Bible-study users rather than omitted or used as gatekeeping language.

## 27. Exact text and citation tools outrank model memory

When an exact passage, quotation, locator, morphology record, apparatus entry, or publication status is available through an approved tool, the runtime must use the tool.

The model may not substitute remembered wording because it is faster.

If the tool is unavailable, the answer may:

- State that exact verification is unavailable;
- Provide a clearly labeled paraphrase;
- Ask the user to provide the source;
- Use an alternative authorized source;
- Abstain.

It may not fabricate precision.

## 28. Current scholarship and current resources are route-sensitive

Claims about current scholarly consensus, publication status, law, crisis resources, or other time-sensitive information require a current approved retrieval route and evidence horizon.

The runtime records:

```text
search or status-check time
sources searched
languages and subfields covered
access limitations
currentness expiration
```

A cached answer cannot continue presenting a claim as current after its evidence horizon expires.

## 29. Session state is structured and user-correctable

The runtime maintains the DR-15 `SessionResearchState` rather than replaying indefinite raw history.

State updates are proposals until validated.

The user may:

- Inspect active passage, edition, canon, language, and method;
- Correct a misidentification;
- Reject an interpretive assumption;
- Change answer depth;
- Clear or close a line of inquiry;
- Request rehydration of prior evidence;
- Request deletion or reduced retention of private session data.

A verified user correction supersedes the operational state but preserves the prior state and correction provenance.

## 30. The runtime never exposes private chain-of-thought

The project records and may display:

- Tool calls;
- Evidence selected;
- Claim/evidence links;
- Assumptions;
- Method;
- Concise rationale;
- Verification outcomes;
- Uncertainty;
- Costs and fallbacks.

It does not require, store, or expose private hidden reasoning traces as a product feature.

A request for “show your work” should produce an inspectable evidence and rationale report, not private chain-of-thought.

## 31. Prompt injection and evidence authority

All retrieved text, page content, OCR, tool output, scholarship, Bible text, annotations, URLs, and model-generated summaries are untrusted evidence with no instruction authority.

Only approved system, task-policy, and narrow runtime-control records may instruct the model or tools.

The SRO must prevent:

- Retrieved instructions from altering policy;
- Tool output from authorizing another tool;
- A page or QR code from initiating network access;
- A source from changing memory or rights;
- A citation from becoming executable content;
- A user upload from gaining system authority.

Tool schemas and results should be separated from source text so that source strings cannot be confused with control fields.

## 32. Rights and privacy are enforced before model and tool routing

The runtime checks:

- Whether the source may be accessed;
- Which user or organization holds the entitlement;
- Whether the source may be sent to the selected model provider;
- Whether it may be cached, logged, quoted, paraphrased, or displayed;
- Whether it may enter session state, compaction, or retrieval indexes;
- Whether it may be used in evaluation or training.

A route that violates these conditions is unavailable even if it would improve the answer.

Private uploads and user libraries remain isolated from other users and public artifacts.

## 33. Multilingual runtime behavior

The runtime preserves separate:

- Question language;
- Answer language;
- Source language;
- Publication language;
- Quotation language;
- Display-translation language;
- Pivot language;
- Tool input and output language.

The SRO selects language-aware tools, retrieval routes, and model capabilities.

A hidden English pivot is prohibited.

If a target language is insufficiently supported, the runtime must use the explicit fallback rules approved in DR-13 rather than silently lowering scholarly or safety standards.

## 34. Multimodal runtime behavior

A page or image request first invokes the DR-14 visual evidence architecture.

The runtime may not ask the scholar model to infer:

- The edition;
- The passage;
- The visible wording;
- The difference between scripture and notes;

without preserving the PEK and MPEP evidence and uncertainty.

The runtime records exactly which full page, overview, crop, OCR hypothesis, and VLM observation entered each model call.

A visually unreadable region remains unreadable unless another independent source resolves it—and that distinction remains visible.

## 35. Caching is subordinate to identity, rights, and currentness

The runtime may cache:

- Deterministic tool results;
- Evidence packets;
- Context plans;
- Model prefixes;
- Verified answer fragments;
- Public passage lookups;

only under exact keys containing the relevant:

```text
source and graph revisions
rights and user scope
model and processor
runtime and verifier revisions
language and profile
policy and currentness horizon
content hash
```

Private or restricted caches cannot be reused across unauthorized users.

A source correction, rights change, retraction, user correction, policy change, model change, or compaction invalidation expires the affected cache.

Cached model prose remains derivative and cannot replace revalidation of current evidence.

## 36. Runtime budgets are explicit

Every request has a `RuntimeBudget` containing, where applicable:

```text
input and output tokens
reasoning tokens or effort
model calls
tool calls
retrieval expansions
images and crops
latency
memory
actual or projected dollar cost
external-provider use
privacy and data-route constraints
```

Budget pressure may reduce optional context, choose a cheaper verified route, or request user approval for a more expensive mode.

It may not remove required evidence, lower assurance, or hide a capability failure.

Actual usage appears in the audit receipt.

## 37. Failure taxonomy and fallback

The runtime distinguishes:

```text
REQUEST_AMBIGUITY
SCOPE_OR_POLICY_BLOCK
SAFETY_ESCALATION
REFERENCE_OR_IDENTITY_FAILURE
RIGHTS_OR_ENTITLEMENT_FAILURE
SOURCE_UNAVAILABLE
RETRIEVAL_FAILURE
TOOL_TRANSIENT_FAILURE
TOOL_SEMANTIC_FAILURE
MODEL_CAPABILITY_FAILURE
MODEL_RUNTIME_FAILURE
CONTEXT_BUDGET_FAILURE
COMPACTION_OR_REHYDRATION_FAILURE
VERIFICATION_FAILURE
CITATION_OR_QUOTATION_FAILURE
LANGUAGE_OR_SCRIPT_FAILURE
MULTIMODAL_GROUNDING_FAILURE
CURRENTNESS_EXPIRED
HUMAN_REVIEW_REQUIRED
UNKNOWN_FAILURE
```

Each failure class has an approved response:

- Retry unchanged;
- Use an equivalent authorized source;
- Rehydrate evidence;
- Reduce scope;
- Ask a material clarification;
- Select an approved fallback model;
- Qualify;
- Abstain;
- Return for human review.

A fallback is recorded and visible. It cannot pretend that the unavailable capability was used.

## 38. Human review is an explicit state

The runtime may require human review for:

- Benchmark gold or adjudication;
- Difficult textual-critical claims;
- New source or rights decisions;
- Unsupported languages;
- High-impact pastoral or sensitive cases where automated support is inadequate;
- Model-generated Translation Nuance records proposed for promotion;
- Release decisions;
- Persistent disagreement among evidence and verifiers.

The answer must not claim “reviewed by a scholar” unless an identified qualified reviewer actually reviewed the relevant artifact or claim.

Human review creates a versioned assertion. It does not erase model provenance or prior disagreement.

## 39. Runtime observability and audit

Every consequential request produces a `RuntimeAuditReceipt` containing at least:

```text
request, session, and study-profile revisions
applicable design and policy revisions
classification and assurance records
resolved source, passage, edition, canon, language, and modality
research execution plan
rights and entitlement decisions
tool capabilities and calls
evidence ledger revision
context plan, packet, compaction, and rehydration identities
model, processor, reasoning mode, runtime, and precision
answer candidates and repair iterations
claim-verification outcomes
citations and source handles
fallbacks, escalations, and abstentions
latency, memory, tokens, and cost
answer artifact and content hashes
privacy-aware logging state
```

The receipt supports:

- Reproduction;
- User correction;
- Incident analysis;
- Benchmark scoring;
- Cost analysis;
- Model comparison;
- Rights impact analysis;
- Post-release monitoring.

It must not expose private user content publicly or require private chain-of-thought.

## 40. User-visible transparency

The product should allow a user, at an appropriate level of detail, to inspect:

- The passage, edition, canon, and translation selected;
- Sources cited;
- Whether a quotation is original, published translation, or model translation;
- Material alternative interpretations;
- Important limitations;
- Whether the answer used page OCR, a VLM, deterministic tools, RAG, full-canon context, compact or large models, or human review;
- Whether any evidence was unavailable because of rights or access;
- The currentness horizon for a “current scholarship” claim.

This should be useful transparency rather than an overwhelming dump of internal telemetry.

## 41. Product efficiency is a design requirement

The harness is not intended to turn every question into an expensive research project.

Efficiency comes from:

- Assurance classes;
- Deterministic answers where possible;
- Focused tools and context;
- Reuse of valid public evidence packets;
- Structured session state;
- Safe compaction;
- Compact-primary and large-fallback routing;
- Bounded verification;
- Explicit user-controlled depth and cost.

The runtime must measure both:

- Failure from insufficient evidence or verification;
- Waste from unnecessary model calls, retrieval, or escalation.

A system that is maximally cautious but unusably slow or costly has not satisfied DR-01.

## 42. Runtime benchmark track

The benchmark must evaluate the full system—not only model weights.

Required case families include:

- Simple deterministic passage lookup;
- Ordinary passage explanation;
- Translation comparison requiring and not requiring a textual variant;
- Original-language ambiguity;
- Ancient-version and apparatus analysis;
- Scholarship synthesis with corrections and retractions;
- Full-book and full-New-Testament questions;
- Multilingual and cross-lingual evidence;
- Printed and photographed pages;
- Missing and rights-blocked evidence;
- False premises;
- User corrections across turns;
- Compacted sessions requiring later rehydration;
- Scope and safety edge cases;
- Adversarial prompt injection in retrieved text and images;
- Compact-model escalation to a larger model;
- Tool, model, verifier, and cache failure.

## 43. Mandatory runtime ablations

At minimum compare:

```text
model alone
model + one static system prompt
model + unstructured RAG
model + deterministic tools
model + Context Composer
model + structure-first output
model + claim/citation verification
complete Runtime Scholar Harness
compact primary versus large fallback
single-pass versus plan-execute-verify
without versus with compaction and rehydration
without versus with Translation Nuance Semantic Kernel
without versus with Page Evidence Kernel
without versus with current-status verification
```

Each ablation uses the same underlying sources and benchmark cases where possible.

A runtime component is promoted only if it repairs a named failure or materially improves usefulness relative to its cost and complexity.

## 44. Runtime metrics

Required metrics include:

```text
task correctness
primary-text fidelity
source, edition, canon, and language identity accuracy
claim/evidence entailment
quotation and locator accuracy
citation completeness and accuracy
Translation Nuance causal accuracy
linguistic and apparatus hard-failure rates
material counterevidence recall
calibration and abstention
false-refusal and harmful-compliance rates
tool-selection precision and recall
unnecessary-tool-call rate
tool-loop failure rate
clarification necessity and burden
model-routing accuracy
compact-to-large escalation precision and recall
verification catch and false-rejection rates
repair success and iteration count
session-drift and user-correction retention
compaction and rehydration fidelity
multilingual and multimodal worst-group performance
prompt-injection success rate
rights and privacy compliance
latency, memory, throughput, token use, and dollar cost
expert-rated scholarly faithfulness
user-rated usefulness and evidence inspectability
```

No aggregate score may hide a hard source, citation, safety, rights, language, or page-grounding failure.

## 45. Promotion gates

The runtime is promoted only if it:

- Materially outperforms the same model without the harness on named tasks;
- Reduces citation, source-type, and Translation Nuance hard failures;
- Preserves accessible answers for nonexpert users;
- Does not create unacceptable false refusal or over-escalation;
- Demonstrates bounded cost and latency;
- Preserves multilingual and multimodal capabilities;
- Enforces rights before transmission and display;
- Survives adversarial evidence and prompt injection;
- Preserves user corrections and compaction state;
- Provides reproducible audit receipts;
- Passes qualified expert review;
- Receives owner approval.

A sophisticated harness is not promoted merely because it has more components.

## 46. Runtime hard failures

DR-16 treats the following as hard failures:

- Allowing the model to invent or silently alter task, source, edition, canon, language, or rights identity.
- Quoting a passage, source, or scholar from model memory when exact verification is required and available.
- Rendering a claim whose evidence handle is absent, invalid, or does not support it.
- Treating larger-model output as verified merely because the model is larger.
- Letting retrieved text, OCR, a page, a URL, a QR code, or a tool result gain instruction authority.
- Exposing unrestricted shell, network, filesystem, cloud, or database authority to the runtime model.
- Allowing a model-generated TNC, linguistic, apparatus, page, or scholarship record to become authoritative without promotion.
- Hiding a model, language, translation, context, compaction, tool, or evidence fallback.
- Silently lowering the assurance class to reduce cost.
- Allowing optional context to displace required evidence or counterevidence.
- Continuing an indefinite or hidden tool or self-repair loop.
- Treating a tool semantic failure as transient and retrying around it.
- Claiming current consensus or resource status without a valid evidence horizon.
- Presenting a study note, model translation, compacted summary, or page OCR as the underlying source.
- Using compacted state for an exact claim without required rehydration.
- Ignoring or overwriting a verified user correction.
- Sending private or restricted material to an unauthorized provider or user.
- Reusing private or restricted caches across entitlement boundaries.
- Claiming human or scholar review when none occurred.
- Storing or publishing private chain-of-thought as a product requirement.
- Recording incomplete audit evidence while claiming reproducibility.
- Permitting Luna to modify code, task design, runtime configuration, evidence, or experiment parameters.

## 47. Runtime engine and framework boundary

Biblical Scholar Lab will not build durable workflow scheduling, checkpoint persistence, interruption, resumption, streaming, and ordinary graph execution entirely from scratch. It will also not allow an off-the-shelf agent framework to become the authority over scholarly state, evidence, rights, safety, tools, compaction, or verification.

The approved architecture is:

```text
Biblical Scholar Runtime Core
    project-owned domain models, policies, state transitions,
    planning, evidence, rights, verification, compaction, rendering, and audit
        ↓
RuntimeEngine contract
        ↓
ReferenceRuntimeEngine
    deterministic in-process conformance oracle

LangGraphRuntimeEngine
    provisional durable production substrate

Optional bounded adapters
    OpenAI Agents SDK or provider-native runtimes for specific calls,
    specialists, research ceilings, voice, or comparative experiments
```

### 47.1 The project-owned Scholar Runtime Core is authoritative

The Scholar Runtime Core contains the canonical implementations of:

- `ScholarRuntimeOrchestrator` semantics;
- Runtime state and transition rules;
- Request, profile, classification, plan, grant, evidence, claim, answer, and audit contracts;
- Scope, sensitive-use, rights, privacy, and assurance policy;
- Research-plan templates and evidence-sufficiency rules;
- Tool capability and authorization rules;
- Context composition, compaction, rehydration, and invalidation semantics;
- Model-route and escalation policy;
- Structure-first answer generation contracts;
- Verification, repair, qualification, abstention, and human-review rules;
- User correction and session-state semantics;
- Framework-independent audit events and artifact identities.

No framework-specific message, checkpoint, thread, run item, trace, or session object becomes a canonical public or persisted domain type merely because the framework exposes it conveniently.

### 47.2 The `RuntimeEngine` contract

The runtime core interacts with execution substrates only through a project-owned logical interface equivalent to:

```text
RuntimeEngine
  start(request, approved_graph_revision)
  resume(runtime_id, approved_event)
  inspect(runtime_id)
  interrupt(runtime_id, reason)
  cancel(runtime_id, reason)
  replay(authoritative_audit_events)
  export_operational_state(runtime_id)
```

The final method names and language bindings may differ, but the contract must preserve:

- Exact runtime and graph identity;
- Deterministic transition validation;
- Idempotent node or activity identity where required;
- Bounded retry and resume semantics;
- Explicit interruption and human-review states;
- Framework-neutral input and output domain objects;
- Authoritative audit-event emission;
- Cancellation and cleanup;
- Reproducible replay where the underlying external dependencies permit it.

### 47.3 The deterministic reference executor

Sol must first implement a small:

```text
ReferenceRuntimeEngine
```

that executes the approved graph in-process without relying on a third-party agent loop.

Its purpose is not production scale. It is the conformance oracle for:

- State transitions;
- Branching and blocked states;
- Tool grants and denials;
- Context packet and answer candidate flow;
- Verification and repair;
- Audit-event order;
- Interrupt, resume, cancellation, and replay semantics;
- Framework equivalence tests.

The reference executor must remain simple enough to inspect and deterministic enough to distinguish a project-contract failure from a workflow-framework behavior.

### 47.4 LangGraph v1 is the provisional durable execution substrate

The provisional production adapter is:

```text
LangGraphRuntimeEngine
```

implemented with the low-level LangGraph v1 `StateGraph` and persistence APIs rather than high-level autonomous-agent abstractions.

LangGraph is a low-level orchestration runtime that does not require LangChain's higher-level agent architecture. Its documentation explicitly distinguishes workflows with predetermined code paths from agents that dynamically choose their own processes and tools; it also provides durable execution, checkpointed state, interruption, resumption, streaming, human-in-the-loop operation, and fault tolerance.[^langgraph-overview] [^langgraph-workflows] [^langgraph-persistence]

Those capabilities fit DR-16 because Biblical Scholar Lab is primarily a reviewed state machine containing bounded model calls, not a free-roaming autonomous agent.

LangGraph may provide:

- Node and edge scheduling;
- Parallel execution of independent approved evidence activities;
- Operational checkpointing;
- Durable interruption and resume;
- Streaming of progress events;
- Fault recovery for transient execution failures;
- Operational state inspection and debugging.

LangGraph may not determine:

- Which state transitions are scholarly valid;
- What evidence is sufficient;
- Which tool capability is authorized;
- Which source may be transmitted;
- What may be compacted;
- Which claim may be rendered;
- Whether a scholarly conclusion is supported;
- Which repair, escalation, or abstention is epistemically appropriate.

The project-owned runtime core supplies those decisions to the adapter.

### 47.5 LangGraph checkpoints are operational projections

A LangGraph checkpoint is not the authoritative scholarly record.

The authoritative record remains:

```text
project-owned RuntimeAuditEvent stream
+ immutable request, plan, packet, evidence, claim, answer, and artifact identities
```

The LangGraph checkpoint is a replaceable operational projection used to resume execution.

The implementation must define and test:

- Mapping from canonical runtime state to LangGraph state;
- Mapping from LangGraph execution outcomes to canonical audit events;
- Checkpoint schema and version identity;
- Safe migration or invalidation rules;
- Reconciliation after crash or partial write;
- Prevention of framework-only state from becoming an unreviewed scholarly fact;
- Export sufficient for replay through the reference executor where feasible.

### 47.6 High-level agent abstractions are not the baseline

The initial implementation must not use a generic ReAct loop, high-level `create_agent`, Deep Agents, or another autonomous planning abstraction as the governing runtime.

A model may propose a plan, tool call, or route only inside the validated DR-16 contracts. Predetermined workflow paths remain code-owned and reviewable. LangGraph itself distinguishes predetermined workflows from autonomous agents; this design deliberately selects the former as the baseline.[^langgraph-workflows]

A later learned planner or router requires the specific promotion gates already defined by DR-16 and the later experiment ladder.

### 47.7 OpenAI Agents SDK is an optional adapter—not the constitution

The OpenAI Agents SDK provides agents, tools, guardrails, sessions, handoffs, tracing, human involvement, and structured outputs. Its documentation states that `Agent` plus `Runner` allows the SDK to manage turns, tools, guardrails, handoffs, and sessions, whereas applications that need to own the loop should use lower-level control.[^openai-agents] [^openai-agents-overview]

Biblical Scholar Lab needs to own the loop.

The SDK may later be used for:

- An OpenAI frontier-ceiling model adapter;
- A bounded specialist model invocation;
- OpenAI-specific structured-output or tool experiments;
- A controlled SDK-versus-project-loop comparison;
- A future voice interface;
- Optional public-safe tracing under an approved privacy route.

It may not replace:

- The SRO;
- Project session and compaction state;
- Evidence packets;
- Tool grants;
- Rights filtering;
- Verification;
- Audit receipts;
- Deterministic repair and escalation.

This restriction is also practical. SDK sessions automatically maintain conversation history, while DR-15 requires explicit structured state, compaction, rehydration, and invalidation.[^openai-sessions] SDK handoffs can transfer or summarize prior history, whereas Biblical Scholar Lab requires rights-filtered immutable evidence packets.[^openai-handoffs] Tool guardrails do not apply uniformly to every SDK tool and handoff category, so the project cannot treat them as a universal authorization boundary.[^openai-guardrails]

### 47.8 Framework-neutral tools and model providers

The project owns one canonical `ToolContract` and one capability-aware model-provider contract.

LangGraph nodes, OpenAI function tools, MCP servers, provider tool schemas, or other wrappers are adapters around these contracts.

Every provider adapter declares and verifies support for relevant capabilities, including:

```text
structured output
function or tool calling
images and other modalities
reasoning controls
long context
streaming
usage and cost reporting
cancellation
retry behavior
privacy and data-routing constraints
```

Provider-specific behavior cannot silently change runtime semantics.

### 47.9 Tracing and observability

Framework-native tracing may assist debugging, but it is never the only audit record.

Any tracing integration must:

- Be disabled by default for private, restricted, or holdout evidence unless an approved private route exists;
- Redact or hash sensitive content where appropriate;
- Preserve exact project artifact identities;
- Record the tracing provider and revision;
- Avoid exporting private chain-of-thought as a requirement;
- Remain replaceable without losing the authoritative audit history.

The OpenAI Agents SDK traces runs, generations, tools, guardrails, and handoffs by default, while allowing tracing to be disabled or redirected; any use must therefore be explicitly configured under DR-10 rather than accepted by framework default.[^openai-tracing]

### 47.10 Conformance spike before promotion

Before LangGraph becomes the production runtime substrate, Sol must implement a bounded vertical slice through both:

```text
ReferenceRuntimeEngine
LangGraphRuntimeEngine
```

The slice should support one representative task such as comparing two authorized translations of one passage and determining whether the difference is textual, linguistic, translational, or unresolved.

It must demonstrate:

- Identical canonical state transitions;
- Typed tool capabilities;
- Rights denial before transmission;
- Immutable evidence and context packets;
- Structure-first model output;
- Unsupported-claim removal or qualification;
- Forced interruption and exact resume;
- Cancellation and cleanup;
- Audit receipt generation;
- Model-provider substitution;
- Operational checkpoint corruption or incompatibility handling;
- Semantically equivalent outcomes through both engines within an approved tolerance.

LangGraph is promoted only if this spike shows that it reduces implementation burden without weakening the project contracts.

If it fails, the project may select another workflow substrate through a new design amendment. The reference executor remains the conformance oracle rather than becoming an accidental full production framework.

### 47.11 Versioning and upgrade policy

Every workflow-framework deployment records:

```text
framework and exact version
adapter revision
checkpointer implementation and version
serialized state schema
runtime-core revision
approved graph revision
migration revision
```

Framework upgrades require:

- Changelog and compatibility review;
- Reference-versus-adapter conformance tests;
- Resume from representative old checkpoints where supported;
- Failure and rollback testing;
- Security and dependency review;
- Owner-approved promotion for material changes.

A framework upgrade may not silently alter tool loops, retries, message history, compaction, state merging, or human-review behavior.

### 47.12 Deferred framework details

DR-16 does not yet select:

- The final implementation language;
- Exact LangGraph package version;
- In-memory, SQLite, Postgres, or other checkpointer;
- Queue, worker, or deployment topology;
- LangSmith or another observability platform;
- Exact model-provider client libraries;
- Whether OpenAI Agents SDK integration is implemented at all;
- The final production workflow substrate after the conformance spike.

It does select the authority boundary, the project-owned contracts, the required reference executor, and LangGraph v1 as the provisional substrate to test.

## 48. Sol implementation discretion

The logical architecture and consequential contracts are owned by the approved designs.

Sol may determine design-neutral implementation details such as:

- Module, class, and function organization;
- Concurrency and scheduling mechanics;
- Internal immutable collection types;
- Equivalent schema-validation libraries;
- Error-handling implementation within the approved failure semantics;
- Test structure and fixtures;
- Performance optimizations proven behaviorally equivalent;
- Approved backend adapters;
- Deployment topology that preserves the logical planes and authority boundaries.

Sol may not independently change:

- The SRO’s authority;
- Runtime state semantics;
- Task taxonomy or assurance meaning;
- Required evidence templates;
- Tool capabilities or authority boundaries;
- Rights-before-routing behavior;
- Context and compaction contracts;
- Model-routing authority;
- Structure-first output;
- Verification layers or claim outcomes;
- Bounded repair and escalation;
- Answer modes or epistemic distinctions;
- Safety and scope policy;
- Audit and user-correction semantics;
- Benchmark, metrics, promotion gates, or experiment design.

A material limitation or proposed improvement returns:

```text
BLOCKED_REQUIRES_DESIGN_REVIEW
```

or a clearly labeled design proposal without implementation.

Luna may execute only frozen runtime, inference, benchmark, or evaluation campaigns delegated by Sol. Luna may not write code, alter configuration, select evidence, change a route, repair a tool, modify thresholds, or redesign the experiment.

## 49. Binding decisions

Approval of DR-16 would lock:

1. The model remains a bounded reasoning component rather than the authority over evidence, policy, rights, tools, or audit.
2. The project implements a deterministic or rule-governed `ScholarRuntimeOrchestrator`.
3. Every request advances through an append-only, transition-validated runtime state machine; blocked, repair, fallback, escalation, and completion states cannot be changed through model prose.
4. The runtime is divided into interaction, policy, planning, evidence, model, verification, presentation, and audit planes.
5. Requests, profiles, classifications, plans, tool grants, tool calls, evidence ledgers, claim ledgers, answer candidates, answer artifacts, and audit receipts remain separate versioned entities.
6. Domain scope, intent, discourse status, risk, task type, and assurance class remain separate classifications.
7. Clarification is required only for material ambiguity.
8. Research planning is template-governed before learned planning is eligible.
9. Evidence sufficiency is explicit and claim-specific.
10. All consequential tools are typed, allowlisted, rights-aware, and narrowly capability-scoped.
11. Read-only research tools are the baseline; state changes require explicit user-authorized capabilities.
12. The runtime model receives no unrestricted shell, network, filesystem, database, or cloud authority.
13. Tool loops, retries, model passes, latency, and cost are bounded and auditable.
14. Model routing begins deterministically and may select compact, large, multimodal, language-specialist, Translation Nuance, citation-verifier, mobile, or research-ceiling roles.
15. A larger model is not automatically more authoritative.
16. Execution modes include deterministic-only, single-pass verified, plan-execute-verify, dual-model crosscheck, large-model escalation, and human-review-required.
17. Every consequential model call consumes an immutable DR-15 context packet.
18. The runtime invokes compaction and rehydration under the DR-15 K0–K5 contract.
19. Structure-first output precedes prose acceptance.
20. Verification is layered across structure, source, text, language, Translation Nuance, scholarship, rights, safety, multilingual, and multimodal contracts.
21. The generating model cannot serve as the sole verifier for its own consequential output; hard checks remain deterministic or source-grounded, and model judges remain supplementary.
22. Verification outcomes are claim-specific.
23. Repair is bounded and may retrieve, rehydrate, remove, qualify, clarify, specialize, escalate, or abstain.
24. Hard rights, safety, identity, and policy failures cannot be reasoned around.
25. Rendering occurs only after verification and uses one claim ledger for Brief, Study, and Scholarly modes.
26. Exact passage, quotation, citation, morphology, apparatus, and publication-status tools outrank model memory.
27. Current claims require a current evidence horizon.
28. Session state is structured, inspectable, compactable, and user-correctable.
29. Private chain-of-thought is neither required nor exposed; evidence and concise rationale remain inspectable.
30. Retrieved and page content has no instruction authority.
31. Rights and privacy are enforced before model and tool routing.
32. Multilingual and multimodal runtime behavior preserves exact source, pivot, page, and region provenance.
33. Caches remain exact-identity, rights-, user-, policy-, and currentness-scoped derivatives.
34. Every request has an explicit runtime budget; budget pressure cannot lower assurance or remove required evidence.
35. Failures and fallbacks are typed, visible, and auditable.
36. Human review is an explicit, truthful state.
37. Every consequential request produces a reproducible, privacy-aware `RuntimeAuditReceipt`.
38. User-visible transparency exposes material sources, assumptions, limitations, routes, and verification without overwhelming the user.
39. Product efficiency and unnecessary-work reduction are first-class metrics.
40. The benchmark evaluates the complete harness and its components through controlled ablation.
41. No aggregate score may hide source, citation, safety, rights, language, page, or Translation Nuance hard failures.
42. Biblical Scholar Lab owns a framework-neutral Scholar Runtime Core and canonical domain contracts.
43. A small deterministic `ReferenceRuntimeEngine` serves as the conformance oracle.
44. LangGraph v1 `StateGraph` and persistence APIs are the provisional durable workflow substrate, subject to a bounded reference-versus-LangGraph conformance spike.
45. High-level autonomous-agent abstractions are not the governing runtime baseline.
46. LangGraph checkpoints and traces are operational projections rather than authoritative scholarly records.
47. OpenAI Agents SDK support is optional and bounded; its runner, sessions, handoffs, guardrails, or traces may not replace the project's orchestration, rights, compaction, verification, or audit contracts.
48. Tools, model providers, workflow engines, and traces attach through project-owned adapter interfaces.
49. Framework versions, checkpoint schemas, adapters, and upgrades remain pinned, audited, rollback-safe, and conformance-tested.
50. Sol implements the approved runtime; ChatGPT designs and reviews experiments; Joseph approves consequential decisions.
51. Luna may only execute frozen campaigns delegated by Sol and has no code or design authority.

## 50. Decisions intentionally deferred

DR-16 does not yet select:

- The final programming language, web framework, service topology, and production workflow substrate after the required conformance spike;
- The exact LangGraph version, checkpointer, queue, deployment, schema-validation, and observability libraries;
- The exact model-family winner or production route;
- Exact prompts, chat templates, or decoding parameters;
- Final numerical thresholds for assurance, evidence sufficiency, escalation, verification, retry, or cost;
- The final retriever, reranker, search provider, or licensed-resource connectors;
- Exact current-resource and publication-status providers;
- The final tool implementation, RPC protocol, model-provider library, or whether an OpenAI Agents SDK adapter is implemented;
- Exact cache product, retention, or eviction policy;
- The final user workspace, note, or export implementation;
- Final UI layout, progressive disclosure, or source-inspection controls;
- Exact human-review operations and staffing;
- Whether learned planning, routing, verification, or compaction is ever promoted;
- Exact second-model or specialist crosscheck policy;
- Exact mobile and offline runtime implementation;
- Exact public telemetry and privacy-retention settings;
- Final benchmark case count or numerical product thresholds.

Those decisions belong to later design reviews, DR-28’s integrated logical architecture, and owner-approved experiments.

## 51. Approval statement

> **Biblical Scholar Lab will use a deterministic, policy-governed Runtime Scholar Harness in which the foundation model remains a bounded reasoning and language component rather than the authority over task identity, safety, rights, tools, source identity, evidence sufficiency, verification, session state, or audit. A Scholar Runtime Orchestrator will transform an immutable user request and study profile into independent domain, intent, risk, task, language, modality, and assurance classifications; resolve exact passage, edition, canon, source, and user context; construct a template-governed research execution plan; issue narrow typed tool capabilities; acquire rights-authorized evidence; invoke the Context Composer and approved compaction or rehydration policy; route among deterministic tools, compact, large, multimodal, language-specialist, Translation Nuance, verifier, or human-review roles; and require structure-first answer candidates before prose acceptance. Every consequential claim will pass layered source, quotation, linguistic, Translation Nuance, apparatus, scholarship, citation, rights, safety, multilingual, and multimodal verification and will be removed, qualified, repaired, escalated, or withheld when support is inadequate. Exact source and citation tools will outrank model memory; current claims will require a valid evidence horizon; untrusted documents and tool results will have no instruction authority; private and restricted evidence will be filtered before transmission; and all tool loops, model passes, repairs, costs, fallbacks, session changes, compaction events, and human-review states will remain bounded and auditable. Brief, Study, and Scholarly responses will render from the same verified claim ledger, preserving material evidence, alternatives, uncertainty, translation provenance, and user accessibility without exposing private chain-of-thought. The authoritative runtime core, domain schemas, state transitions, tool grants, evidence rules, compaction semantics, verification, and audit records will be project-owned and framework-neutral. A deterministic reference executor will serve as the conformance oracle, while low-level LangGraph v1 StateGraph and persistence APIs will be tested as the provisional durable workflow substrate through a bounded equivalence, interruption, resume, and rollback spike. LangGraph checkpoints and framework traces will remain replaceable operational projections. The OpenAI Agents SDK may be used only as an optional bounded provider or specialist adapter and may not replace the project-owned orchestration, sessions, rights, tool, compaction, verification, or audit contracts. Every consequential request will produce a reproducible, privacy-aware Runtime Audit Receipt, while product promotion will require controlled component ablation, framework-conformance evidence, expert review, acceptable latency and cost, and owner approval.**

[^langgraph-overview]: LangChain, “LangGraph overview,” describing LangGraph as a low-level orchestration runtime with durable execution, streaming, human-in-the-loop support, and no requirement to use higher-level LangChain agents: <https://docs.langchain.com/oss/python/langgraph/overview>.
[^langgraph-workflows]: LangChain, “Workflows and agents,” distinguishing predetermined workflow code paths from dynamic agent-selected processes and tools: <https://docs.langchain.com/oss/python/langgraph/workflows-agents>.
[^langgraph-persistence]: LangChain, “Persistence,” describing per-step checkpoints, threads, human-in-the-loop pause/resume, time travel, pending writes, and fault tolerance: <https://docs.langchain.com/oss/python/langgraph/persistence>.
[^openai-agents]: OpenAI, “Agents,” explaining that `Agent` plus `Runner` can manage turns, tools, guardrails, handoffs, and sessions, while lower-level control is appropriate when the application needs to own the loop: <https://openai.github.io/openai-agents-python/agents/>.
[^openai-agents-overview]: OpenAI, “OpenAI Agents SDK,” comparing the Agents SDK with direct lower-level control and listing sessions, human involvement, tracing, and MCP integration: <https://openai.github.io/openai-agents-python/>.
[^openai-sessions]: OpenAI, “Sessions,” describing SDK-managed conversation-history persistence across runs: <https://openai.github.io/openai-agents-python/sessions/>.
[^openai-handoffs]: OpenAI, “Handoffs,” describing transfer and filtering of conversation history between agents: <https://openai.github.io/openai-agents-python/handoffs/>.
[^openai-guardrails]: OpenAI, “Guardrails,” documenting that tool guardrails apply to custom function tools but not uniformly to handoffs, hosted tools, built-in execution tools, or `Agent.as_tool()`: <https://openai.github.io/openai-agents-python/guardrails/>.
[^openai-tracing]: OpenAI, “Tracing,” describing default tracing of runs, generations, tools, guardrails, and handoffs and the ability to disable or redirect traces: <https://openai.github.io/openai-agents-js/guides/tracing/>.

