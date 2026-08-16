# DR-15 — Long-Context and Context-Composer Design

| Field | Value |
|---|---|
| Design ID | `DR-15` |
| Status | `APPROVED` |
| Approval date | 2026-08-16 |
| Project owner | Joseph Abbud |
| Designer and independent reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2 and supplements; DR-03; DR-04; DR-05; DR-06; DR-07; DR-08; DR-09; DR-10; DR-11; DR-12; DR-13; DR-14 |
| Implementation authority | GPT-5.6 Sol, under the approved design |
| Execution authority | GPT-5.6 Luna only for frozen campaigns delegated by Sol under a later approved campaign envelope |
| Experiment-design authority | ChatGPT designs; Joseph Abbud approves; Sol implements only the approved design |
| Changes if approved | Establishes long context as an evidence-composition and routing problem rather than a raw token-capacity claim; defines the deterministic Context Composer, immutable context plans and packets, full-New-Testament and hybrid modes, budget, compression, and provenance-preserving compaction policy, multi-turn memory boundaries, positional-robustness tests, and evidence-gated routing among tools, RAG, book context, canon context, and larger models |

## 1. Purpose

Biblical Scholar Lab will often need to reason over material larger than one passage:

- an entire biblical book;
- the complete New Testament;
- Greek and one or more modern translations;
- a passage together with textual, linguistic, ancient-version, Translation Nuance, and scholarly evidence;
- several distant passages connected by quotation, allusion, terminology, or argument;
- a long commentary, monograph, article set, or conversation;
- a photographed page plus its canonical text and supporting research;
- multilingual evidence whose token cost varies materially by language and tokenizer.

The current candidate families advertise native context windows of approximately 256K or 262K tokens. Qwen3.5-9B reports a native 262,144-token window; Gemma 4 12B and 31B report 256K; Ministral 3 8B reports 256K. Rhema's BibleAI announcement also identifies a 128K design as roughly sufficient to place the New Testament and a question in one context. Those facts establish useful engineering possibilities. They do **not** establish that a model can reliably locate, connect, weigh, and cite evidence throughout the full window.[^qwen-context] [^gemma-context] [^ministral-context] [^rhema-context]

Long-context research has repeatedly found that nominal capacity and effective use are different. Models can be sensitive to the location of relevant evidence, degrade as distractors and reasoning complexity increase, and perform well on literal needle retrieval while failing on semantically indirect or multi-hop tasks. Long-context models may outperform RAG when sufficiently capable and resourced, while RAG remains substantially cheaper; hybrid routing can preserve much of the long-context performance while reducing token use.[^lost-middle] [^ruler] [^nolima] [^longbench2] [^rag-lc]

DR-15 therefore defines:

- the distinction between native context capacity, configured capacity, and effective scholarly context;
- a deterministic, evidence-aware `ContextComposer`;
- immutable context requests, plans, blocks, packets, projections, and usage receipts;
- passage, book, canon, research-synthesis, conversation, and multimodal context modes;
- exact token-budget accounting by model, processor, language, modality, reasoning mode, and tool loop;
- the role of the complete New Testament as an optional evidence block rather than a permanent system prompt;
- routing among deterministic tools, targeted retrieval, long retrieved units, full-book context, full-New-Testament context, hybrid context, and larger-model escalation;
- evidence-dependency and counterevidence preservation;
- context ordering, positional robustness, and anti-dilution measures;
- context compression, provenance-preserving compaction, summaries, caches, rehydration, invalidation, and loss disclosure;
- multi-turn session memory and user-correction handling;
- prompt-injection, privacy, rights, and restricted-source controls;
- multilingual and multimodal context composition;
- long-context training, retention, benchmark, and promotion requirements.

DR-15 does **not** select a final retriever, reranker, vector database, context length for training, exact chunk size, exact full-New-Testament translation, final token-budget percentages, context-compression model, concrete compaction algorithm or backend memory mechanism, cache product, or model-specific routing threshold. Those are later implementation and experiment decisions constrained by this logical contract.

## 2. Governing principle

> **A large context window is a bounded communication channel, not a guarantee of comprehension. Biblical Scholar Lab will compose the smallest complete, provenance-preserving context that can answer the question responsibly; escalate to broader book, canon, or research context only when the evidence dependency requires it; and preserve exact source identity, counterevidence, rights, uncertainty, and omissions throughout the process.**

The intended flow is:

```text
user request and selected study profile
    → question, claim, passage, and evidence-dependency analysis
    → deterministic tools and retrieval candidate generation
    → rights, trust, language, source-role, and version filtering
    → context-mode and model-route selection
    → token and modality budget allocation
    → evidence-preserving selection, ordering, and compression
    → immutable context plan and packet
    → model/tool execution
    → claim/evidence and citation verification
    → usage receipt, omissions, and escalation decision
```

The composer may omit irrelevant material. It may not silently omit evidence necessary to understand a material alternative or to qualify the answer.

## 3. Native window, configured window, and effective window remain distinct

Every model artifact receives a `ModelContextProfile` containing at least:

```text
model_artifact_id
native_context_limit
configured_context_limit
verified_context_limit
input_output_accounting_rule
reasoning_mode_budget_behavior
multimodal_token_accounting
position_encoding_configuration
attention_or_state_architecture
sliding_window_or_local_attention_policy
runtime_and_kernel_identity
precision_and_kv_cache_policy
benchmark_revision
```

The project distinguishes:

### `NATIVE_CONTEXT_LIMIT`

The context length officially supported by the selected checkpoint without project-added position scaling or architectural modification.

### `CONFIGURED_CONTEXT_LIMIT`

The length requested from the runtime. A server configuration does not establish reliable model behavior.

### `VERIFIED_CONTEXT_LIMIT`

The largest length at which the exact model/runtime/precision combination passes the approved Biblical Scholar Lab long-context gates.

### `EFFECTIVE_TASK_CONTEXT`

The largest length at which the model performs adequately for a named task family, evidence distribution, language, and modality.

A model may therefore be verified at 128K for literal passage retrieval but only 32K for difficult causal Translation Nuance synthesis. The product must report the task-specific limit rather than advertising only the maximum accepted token count.

## 4. Candidate-family context behavior is architecture-specific

The context composer remains family-neutral at the contract level but must not treat each family as internally equivalent.

### Qwen3.5 and related Qwen architecture

Qwen3.5-9B reports a native 262,144-token window and a hybrid architecture with Gated DeltaNet and full-attention layers. Its official documentation describes optional YaRN extension beyond the native window. Any extension beyond native context is a separate derivative experiment and cannot become the baseline merely because the runtime accepts it.[^qwen-context] [^qwen-ultra]

### Gemma 4

Gemma 4 12B and 31B report 256K context and interleave local sliding-window attention with global attention. The placement and recurrence of evidence may therefore behave differently from Qwen even when both accept a similar token count. Gemma's vendor-reported long-context scores are useful screening evidence, not proof of our passage, canon, or scholarship tasks.[^gemma-context]

### Ministral 3

Ministral 3 8B reports a 256K context while its own deployment guidance notes that the maximum length is not necessary for most scenarios and materially affects memory and serving configuration.[^ministral-context]

### Consequence

Context ordering, evidence repetition, context compression, KV-cache behavior, latency, and effective length must be measured per exact model bundle and runtime. One family's successful composer configuration may not be copied to another without validation.

## 5. Canonical long-context entities

DR-15 defines the following logical entities.

### `ContextRequest`

The normalized request to compose context:

```text
request_id
user_request_revision
conversation_state_revision
answer_depth
requested_language
canon_and_edition_profile
selected_model_role
tool_and_retrieval_permissions
privacy_and rights context
latency and cost class
required output form
```

### `ContextRequirement`

A condition that the packet must satisfy, such as:

```text
include exact primary passage
include materially relevant textual variants
include strongest counterevidence
include source-language analysis
include at least two independent scholarly positions
preserve original-language quotation
exclude nonauthorized full text
reserve image tokens
reserve tool loop
```

### `ContextUnit`

A candidate evidence unit with stable identity and provenance. A unit may be:

```text
primary-text span
work or book section
linguistic annotation bundle
Translation Nuance evidence unit
apparatus or ancient-version record
scholarly source span
counterevidence span
page region or multimodal packet projection
tool result
session-state record
user correction
policy or task instruction
```

A `ContextUnit` is not necessarily a fixed-size chunk. It is a semantically and provenance-coherent unit with internal boundaries and dependencies.

### `ContextDependency`

A typed relationship indicating that one unit is needed to interpret another:

```text
REQUIRES_SOURCE_TEXT
REQUIRES_PRECEDING_ARGUMENT
REQUIRES_COUNTEREVIDENCE
REQUIRES_DEFINITION
REQUIRES_METHOD_DESCRIPTION
REQUIRES_TRANSLATION_LINEAGE
REQUIRES_CITATION_LOCATOR
REQUIRES_PAGE_OVERVIEW
REQUIRES_DETAIL_CROP
REQUIRES_LANGUAGE_PIVOT_DISCLOSURE
REQUIRES_RIGHTS_NOTICE
```

### `ContextBudgetLedger`

An exact accounting of available and consumed capacity.

### `ContextPlan`

The deterministic composition decision before model projection.

### `ContextBlock`

One ordered block in the final packet with source role, trust, authority, language, priority, compression state, and token count.

### `ContextProjection`

A model- and processor-specific rendering of the canonical plan.

### `ContextPacket`

The immutable, hash-addressed set of projected blocks actually supplied to a model or tool.

### `ContextUsageReceipt`

The post-execution record of what was provided, retrieved, cited, used, omitted, truncated, cached, or escalated.

## 6. The Context Composer is deterministic and reviewable

The project implements a system-level:

```text
ContextComposer
```

The composer is not an LLM prompt assembled ad hoc by application code. It is a deterministic or explicitly rule-governed component that:

```text
classifies the research task
resolves passage, edition, canon, language, and modality
identifies required evidence layers
constructs evidence dependencies
selects an approved context mode
allocates token and modality budgets
applies rights and trust policies
selects, groups, compresses, and orders units
preserves material alternatives and counterevidence
renders a model-specific projection
validates completeness and budget conformance
hashes the plan and packet
records omissions and fallbacks
```

A model may propose context units or recommend escalation. The model does not silently determine the authoritative packet.

## 7. Context modes

Every invocation declares one primary mode and any approved secondary mode.

### `FOCUSED_PASSAGE`

The default for ordinary passage questions.

Typical contents:

- Exact passage and immediate literary context
- Selected source-language text
- Relevant linguistic and Translation Nuance records
- Deterministic tool results
- Targeted scholarship and counterevidence

### `BOOK_SCOPE`

Used when argument, narrative, terminology, discourse, or structure requires a complete biblical book or major section.

### `CANON_SCOPE_NT`

Uses a complete, identified New Testament representation as an evidence block for cross-book or canon-wide questions.

### `CANON_SCOPE_CUSTOM`

Uses an explicitly identified canon or research corpus under DR-04. Version one does not imply full Hebrew Bible scholarly support merely because a larger canon can fit.

### `RESEARCH_SYNTHESIS`

Composes several primary and scholarly sources around a question. The unit of selection may be whole article sections, chapters, or long evidence bundles rather than isolated short chunks.

### `TRANSLATION_NUANCE`

Prioritizes the immutable TNC evidence packet, exact source and target spans, causal alternatives, lineage, and source fitness.

### `MULTIMODAL_PAGE`

Uses the DR-14 MPEP with page overview, detail regions, canonical lookup, and supporting evidence.

### `CONVERSATION_CONTINUITY`

Carries only approved structured session state and selected prior turns needed for continuity.

### `HYBRID_CANON_RAG`

Combines a full book or New Testament context with targeted retrieved evidence, tools, and scholarship.

A mode is a composition policy, not merely a token-length category.

## 8. Focused hybrid context is the default

The default production path should be:

```text
exact tools
+ focused primary context
+ targeted evidence retrieval
+ counterevidence
+ structured packet
```

The project does not load the full New Testament for every question merely because it fits. Full-canon prompts can increase latency, memory, cost, distractor density, positional risk, and the chance that weakly relevant passages overshadow stronger evidence.

The composer escalates when the task requires:

- evidence distributed across many books;
- whole-book or canon-level structure;
- implicit thematic or lexical patterns that retrieval may not identify reliably;
- verification that a proposed pattern is absent or widespread;
- an approved long-context benchmark case;
- a user-requested full-canon comparison whose cost and limitations are disclosed.

## 9. The complete New Testament is an optional evidence block

Rhema's 128K design suggests that a compact New Testament representation can fit alongside instructions and a question. Our candidate models advertise larger native windows. Biblical Scholar Lab will test that opportunity rather than assume it.[^rhema-context]

A full-New-Testament block must identify:

```text
translation or source edition
canon profile
reference scheme
textual form
formatting and verse-label policy
rights and display permissions
exact tokenizer and token count
content hash
included and excluded paratext
```

The complete New Testament is never inserted into the system-policy channel. It is an evidence block with no instruction authority.

The default full-canon packet should not contain hundreds of modern translations simultaneously. Candidate forms include:

```text
one modern translation
Greek New Testament only
Greek plus one modern translation
one user-selected translation plus selected comparison passages
compact parallel representation for bounded experiments
```

The exact forms are selected only after the token census and benchmark.

## 10. Full-canon context does not replace exact tools

Even when the entire New Testament is present, the model should use deterministic tools for:

- exact quotation;
- edition identity;
- original-language text;
- morphology;
- translation parallels;
- canonical reference resolution;
- textual or apparatus evidence;
- citation locators.

The full-canon block supports global awareness and synthesis. It is not treated as the canonical quotation database, critical apparatus, or source of edition metadata.

## 11. Exact token census precedes any full-context promise

Before a context mode is enabled, Sol must implement a reproducible census using the exact model tokenizer and multimodal processor revision.

Required measurements include at least:

```text
English New Testament, minimal text
English New Testament with book/chapter/verse labels
Greek New Testament
Greek plus English
Spanish and French New Testaments
selected ancient-version context
system and scope policy
representative user prompts
retrieved evidence packs
reserved output and tool budgets
page images and detail crops
```

The report must distinguish:

- Text tokens
- Special and formatting tokens
- Image or modality tokens
- Input reserve
- Maximum output reserve
- Deliberate/reasoning-mode reserve
- Tool-loop reserve
- Runtime overhead, where applicable

No word-count estimate becomes a product context guarantee.

## 12. Input, output, reasoning, and tool loops share one budget

The composer allocates capacity before filling the packet.

A `ContextBudgetLedger` contains:

```text
native limit
verified task limit
configured runtime limit
system-policy reserve
user-request reserve
model-output reserve
reasoning-mode reserve
tool-schema reserve
tool-call and tool-result reserve
multimodal reserve
safety margin
evidence capacity
consumed capacity
unused capacity
```

The packet may not fill the nominal context window and then discover that no room remains for a scholarly answer, citations, or a tool response.

The model-specific accounting rule is authoritative. For Qwen's documented long-context behavior, total input and output are considered together when enforcing the model limit.[^qwen-ultra]

## 13. Priority classes

Every context block receives one priority.

### `P0_NON_DROPPABLE`

- System and safety policy
- User's current request and explicit constraints
- Exact context identity and packet metadata
- Rights and privacy enforcement
- Required output and citation contract
- Essential tool schemas

### `P1_REQUIRED_EVIDENCE`

- Exact primary text needed for the claim
- Material textual or linguistic evidence
- Material counterevidence
- Required source and edition identity
- Evidence needed to distinguish interpretation from fact

### `P2_SUPPORTING_EVIDENCE`

- Additional scholarship
- Broader context
- Supporting parallels
- Method or terminology explanation

### `P3_OPTIONAL_CONTEXT`

- Convenience background
- Redundant examples
- Nonessential prior conversation
- Low-value retrieval candidates

A P3 block may never displace a P1 block merely because it has a higher semantic-similarity score.

## 14. Context units are not arbitrary fixed chunks

Short fixed-size chunks can sever:

- a premise from its conclusion;
- a quotation from its source or qualification;
- a commentary claim from its objection;
- a verse from its clause or paragraph;
- an apparatus reading from its legend;
- a footnote from its marker;
- a source span from its citation locator.

The composer operates on semantically coherent units produced by the approved corpus, scholarship, TNC, and page models. A backend may use smaller chunks for candidate retrieval, but the final evidence unit should expand to a meaningful boundary and include required dependencies.

LongRAG and related work provide evidence that larger, semantically coherent retrieval units can preserve context that short-chunk systems lose. This does not establish one universal unit size; it supports making unit boundaries task-aware and evidence-aware.[^longrag]

## 15. Evidence dependencies are explicit

Before selection, the composer constructs a bounded evidence-dependency graph.

Examples:

```text
translation claim
    → exact source span
    → exact target span
    → alignment
    → linguistic analysis
    → translation lineage

scholarly claim
    → exact source span
    → methodology
    → relevant counterargument
    → current-status check

page quotation
    → source image region
    → recognition hypothesis
    → edition identification
    → deterministic canonical lookup
```

Selection is therefore dependency-closed. A context plan cannot include a conclusion while dropping the evidence or qualification needed to interpret it.

## 16. Counterevidence receives protected capacity

The composer reserves capacity for material counterevidence and alternative analyses when DR-02 requires them.

It must not allocate the entire evidence budget to the top-ranked supporting position and then claim that no alternatives exist.

Counterevidence may be omitted only when:

- no material alternative exists under the approved evidence review;
- the user explicitly requests a bounded tradition-specific analysis and the answer labels that scope;
- rights prevent display, in which case the omission and its effect are disclosed;
- the packet escalates rather than pretending completeness.

## 17. Retrieval and long context are complementary

DR-15 does not declare RAG or long context universally superior.

Research comparing the two has found that capable long-context models may outperform RAG on average when supplied with the full material, while RAG can process far fewer tokens. Hybrid routing can preserve much of the performance at lower cost. The tested datasets and models do not establish our domain outcome; they justify a controlled hybrid design.[^rag-lc]

Biblical Scholar Lab should compare:

```text
focused tools only
focused RAG
long retrieved units
full book
full New Testament
full context plus RAG
full context plus tools and RAG
```

## 18. Routing is rule-governed before it is learned

The initial `ContextRouter` is deterministic and uses:

- Task type
- Passage scope
- Number and distance of required evidence units
- Dependency-graph coverage
- Retrieval confidence and diversity
- Whether the question is global or absence-sensitive
- Model role and verified capacity
- Language and modality
- Rights and privacy
- Cost and latency class
- User-selected mode

A model self-assessment may provide an additional signal. It may not be the sole authority because the same model can be overconfident about missing evidence.

Learned routing becomes a later ablation only after the deterministic router and escalation rules are benchmarked.

## 19. Evidence-coverage gates control escalation

After focused retrieval, the system computes a structured coverage assessment:

```text
required evidence layers present
source identity resolved
material alternatives covered
counterevidence covered
citation locators available
rights permit use
language path validated
page regions included
unresolved dependencies
```

Possible outcomes:

```text
ANSWER_WITH_FOCUSED_PACKET
EXPAND_RETRIEVAL
EXPAND_TO_BOOK_CONTEXT
EXPAND_TO_CANON_CONTEXT
ROUTE_TO_LARGER_MODEL
REQUEST_CLARIFICATION
REQUEST_HUMAN_REVIEW
ABSTAIN_MISSING_EVIDENCE
```

The model cannot convert an incomplete evidence packet into a confident answer merely because it can produce fluent prose.

## 20. Context ordering is an experimental variable with protected semantics

The composer records the exact order of every block. It does not assume that ordering is behaviorally neutral.

Long-context research reports position-sensitive performance, including a recurring tendency to retrieve information more effectively near the beginning or end than in the middle.[^lost-middle]

The baseline ordering policy is:

1. System governance and tool contract
2. Compact task-focus and identity card
3. Essential source and edition identities
4. Primary evidence organized by dependency and chronology
5. Linguistic, textual, TNC, and scholarly evidence
6. Material alternatives and counterevidence
7. Context limitations and omitted evidence
8. Exact user request in its native conversation role

The task-focus card is a deterministic restatement of the approved request and required evidence, not a model-generated reinterpretation. Its hash binds it to the original request.

Ordering experiments must include:

- Relevant evidence at beginning, middle, and end
- Chronological versus relevance ordering
- Supporting and counterevidence interleaving versus grouping
- Source-first versus question-first composition
- Full-canon block before versus after targeted evidence
- One-pass versus staged tool-assisted synthesis

The project will not permanently duplicate large evidence spans merely to exploit positional bias. Limited duplication of a small task card, source identity, or decisive evidence handle is permitted only when benchmarked and disclosed.

## 21. Long-context dilution is a measured failure

The system measures whether adding more context causes:

- lower answer accuracy;
- weaker citation entailment;
- omitted counterevidence;
- source-type confusion;
- false thematic connections;
- irrelevant detail;
- reduced calibration;
- answer-language drift;
- slower or more expensive tool use.

NoLiMa, RULER, BABILong, and LongBench v2 all reinforce that literal retrieval, multi-hop reasoning, implicit associations, and realistic long-document understanding are distinct capabilities.[^nolima] [^ruler] [^babilong] [^longbench2]

A context mode that accepts 256K tokens but performs worse than the focused mode on the target task is not promoted.

## 22. Exact quotations and citation-critical spans are compression-protected

The following may not be replaced by a model summary when exact wording is material:

- Biblical source text
- Translation wording under comparison
- Apparatus notation
- Ancient-version wording
- Direct scholarly quotations
- Citation locators
- Definitions whose wording is under analysis
- User-provided wording being evaluated

A compressed context may include a summary **in addition to** an exact span, not instead of it, when the exact span is required for the answer.

## 23. Context-compression ladder

Compression is explicit and provenance-bearing.

### `C0_EXACT`

Exact source span or structured record.

### `C1_STRUCTURE_PRESERVING_SELECTION`

Selects exact relevant sections without rewriting them.

### `C2_DETERMINISTIC_NORMALIZATION`

Applies approved normalization while retaining a reversible map and loss profile.

### `C3_REVIEWED_ABSTRACT`

A human-authored or human-reviewed abstract with exact source links.

### `C4_MODEL_SUMMARY_CANDIDATE`

A model-generated summary with source handles, model identity, prompt, omissions, and review state.

### `C5_STRUCTURED_OR_LEARNED_MEMORY_PROJECTION`

A graph, embedding, tensor, KV, or other compressed representation used only under a separately approved experiment.

Each block records:

```text
compression class
source units
compressor identity
information-loss declaration
retained and omitted claims
rights and display status
review state
```

A model summary is not primary evidence and cannot be quoted as though it were the source.

## 24. Compression may not erase disagreement

When a source set contains disagreement, the compressed representation must preserve:

- The important positions
- Evidence for each
- Counterevidence
- Methodological differences
- Uncertainty
- Dependence among sources

A consensus-looking summary produced by averaging conflicting views is a hard failure.

## 25. Immutable `ContextPlan` contract

A plan contains at least:

```text
context_plan_id
request and session revision
model artifact and processor revision
context mode and route
verified task-context limit
budget ledger
required evidence layers
candidate units and scores
selected and rejected units
rejection reasons
context dependencies
priority classes
ordering policy
compression decisions
compaction policy, triggers, and artifact identities
rights and trust labels
language and modality labels
known omissions
fallback and escalation rules
content hash
```

The plan exists before the model invocation and can be independently reviewed.

## 26. Immutable `ContextPacket` contract

The packet records exactly what the model received:

```text
packet_id
context_plan_id
model-facing block sequence
role and instruction-authority labels
exact rendered bytes or canonical serialization
per-block source handles
per-block token or modality counts
total budget
processor output identity
included and omitted images or crops
special tokens and templates
content hash
```

The packet is the unit of reproducibility for a model response.

A packet generated for one tokenizer, processor, or model cannot be represented as the same packet for another family.

## 27. `ContextUsageReceipt` and post-answer audit

After execution, the system records:

```text
packet identity
model and runtime identity
actual input and output usage
tool calls and results
cache use
citations and evidence handles used
claims not supported by packet evidence
unused required evidence, where measurable
fallbacks and escalations
compaction and rehydration events
truncation or runtime warnings
latency, memory, and cost
answer and audit hashes
```

The receipt does not require private chain-of-thought. It records observable model, tool, evidence, citation, and resource behavior.

## 28. Conversation history is not dumped indefinitely

Multi-turn interaction uses a versioned `SessionResearchState` rather than replaying the entire conversation forever.

The session state may contain:

```text
active passage and editions
canon and language profile
user-selected answer depth
approved user preferences
research question
resolved terminology
accepted and rejected hypotheses
user corrections
sources already inspected
open questions
current evidence packet identities
current compaction artifact identities and staleness state
```

Raw prior turns are included only when needed for exact discourse continuity or when the user asks to inspect them.

Model-generated conversation summaries remain candidates. They may preserve convenience state, but they cannot overwrite the user's wording, source evidence, or approved decisions.


## 29. Context compaction is a first-class lifecycle operation

Compression and compaction are related but distinct.

- **Compression** reduces the representation size of a particular evidence unit.
- **Compaction** is a versioned state transition that decides which information leaves the active context window, what derivative representation replaces it, and how the authoritative evidence can be recovered when it becomes relevant again.

Compaction is required for long-running Bible-study sessions, staged agent workflows, full-book or full-canon analysis, and repeated tool loops. It may improve cost and continuity. It may not silently become a lossy substitute for the research record.

The approved lifecycle is:

```text
active context and session state
    → identify durable state, removable detail, and protected evidence
    → create an immutable compaction artifact
    → retain source handles and unresolved issues
    → remove selected material from active context
    → rehydrate authoritative evidence before consequential reuse
```

### `ContextCompactionArtifact`

Every compaction produces a versioned artifact containing at least:

```text
compaction_artifact_id
source context-packet and session-state identities
compaction policy and revision
trigger and budget state
units retained verbatim
units replaced by structured state
units replaced by immutable evidence handles
units summarized
units omitted
reason for each decision
protected-state audit
model, deterministic process, or human reviewer used
information-loss declaration
rehydration instructions
rights, privacy, and access scope
review state
invalidation dependencies
content hash
```

A compaction artifact is a derivative of the original context. It is not a new primary source, approved scholarly conclusion, or independent line of evidence.

### Approved compaction classes

#### `K0_LOSSLESS_DEDUPLICATION`

Removes exact duplicates and repeated metadata while preserving stable references to the authoritative unit.

Examples include duplicate passage results, repeated edition metadata, or the same citation already present in the packet.

#### `K1_STRUCTURED_STATE_EXTRACTION`

Extracts durable research state such as:

```text
active passage and editions
canon and language profile
answer depth and user preferences
research question
authorized user corrections
hypotheses under consideration
hypotheses rejected and why
sources already inspected
open questions
material disagreements
current packet and evidence identities
```

This is the default compaction mechanism for long-running conversations.

#### `K2_EVIDENCE_HANDLE_COMPACTION`

Removes full source text from active context while retaining an immutable handle to the exact source span, its role, review state, rights, and rehydration requirement.

For example:

```text
source_handle: scholarly-work-123:pp-44-47
role: COUNTEREVIDENCE
status: INSPECTED
rehydrate_before_quotation: true
```

This is preferred over lossy summarization when exact evidence can be retrieved again.

#### `K3_REVIEWED_ABSTRACT_COMPACTION`

Replaces a long source or completed discussion with a human-authored or human-reviewed structured abstract that preserves:

- Claim types;
- Supporting evidence;
- Counterevidence;
- Method;
- Uncertainty;
- Source identity;
- Exact handles for material quotations and locators;
- Review scope and date.

#### `K4_MODEL_SUMMARY_CANDIDATE`

A model-generated summary may reduce context, but it remains an unreviewed candidate. It cannot silently alter durable session state, erase disagreement, or become evidence.

#### `K5_LEARNED_MEMORY_PROJECTION`

A vector, soft prompt, recurrent state, KV-derived representation, or other learned projection may be used only under a separately approved experiment. It must preserve a traceable path to its originating context and may not be the sole basis for an exact quotation, textual claim, citation, or scholarly conclusion.

### Protected information may not be compacted away

Unless the relevant task and evidence issue are explicitly closed, compaction must preserve or retain authoritative handles for:

- Current system and safety policy;
- The user's active question and requested perspective;
- Verified user corrections;
- Exact source, edition, canon, versification, language, and translation identity;
- Exact wording currently under textual, linguistic, translation, or citation analysis;
- Material textual variants;
- Material alternative interpretations and causal diagnoses;
- Counterevidence;
- Unresolved disagreement;
- Rights, privacy, access, and display restrictions;
- Translation and quotation provenance;
- Known uncertainty and missing evidence;
- Active crisis or safety state;
- The fact that a previous claim was corrected, withdrawn, or superseded.

A compaction that converts:

```text
Interpretations A and B remain contested.
```

into:

```text
Interpretation A was accepted.
```

is a hard failure even if the compacted form is fluent and shorter.

### Rehydration is mandatory for consequential reuse

A compacted representation may support routing, continuity, and evidence discovery. Before the assistant performs any of the following, it must rehydrate and revalidate the relevant authoritative evidence when that evidence is no longer present in active context:

- Quote a source;
- Give a precise linguistic or textual-critical analysis;
- Attribute a position to a scholar;
- Reuse a page-image observation;
- Assert that evidence supports, limits, or contradicts a claim;
- Resolve a materially disputed translation diagnosis;
- Render an exact citation or locator.

The governing rule is:

> **Compacted state may support continuity. Exact scholarly claims must be revalidated against authoritative evidence.**

If rehydration fails because access expired, rights changed, a source was corrected, or the artifact is unavailable, the assistant must disclose the limitation, seek an authorized alternative, or abstain. It may not rely confidently on stale compacted memory.

### Compaction invalidation and staleness

A compaction artifact becomes stale or requires reevaluation when:

- A source, edition, transcription, or annotation is corrected;
- A citation is retracted, corrected, or updated;
- A rights or privacy decision changes;
- The user corrects the assistant;
- The selected canon, versification, language, translation, or edition changes;
- An underlying graph assertion is superseded;
- The compaction policy changes materially;
- The research question changes enough that omitted evidence may become relevant;
- The model, tokenizer, runtime, or context contract changes in a way that affects interpretation.

The system must not continue using a stale summary merely because it remains available in session state or a provider cache.

### Compaction benchmarking

The long-context benchmark must compare at least:

```text
uncompacted conversation or evidence packet
structured-state compaction
immutable evidence-handle compaction
reviewed abstract compaction
model-generated summary compaction
learned-memory projection, when authorized
```

Required measurements include:

- Answer-quality delta;
- Primary-evidence retention;
- Counterevidence retention;
- User-correction retention;
- Source, edition, canon, and language identity retention;
- Citation and quotation fidelity;
- Uncertainty retention;
- Rehydration success;
- Contradiction and session-drift rate;
- False-consensus rate;
- Token and cost reduction;
- Latency improvement;
- Rights, privacy, and safety-state compliance.

The benchmark must include cases where an apparently minor detail from an earlier turn becomes decisive later, such as a corrected translation, another Psalm numbering scheme, a rejected interpretive assumption, or a previously identified access restriction.

### Backend and cache compaction remain subordinate implementations

KV-cache eviction, sliding-window attention, prefix caching, provider-native conversation compaction, recurrent-state compression, and architecture-specific mechanisms belong to the later model and training harness review.

All such mechanisms remain subject to this semantic contract:

> **No backend-level cache or state compaction may change the scholarly meaning of active context without exposing the loss to the Context Composer and triggering rehydration, fallback, or abstention.**

An opaque provider-native compaction feature cannot be assumed to preserve citations, counterevidence, user corrections, safety state, or rights constraints merely because the conversation continues successfully.


## 30. User corrections are first-class context records

A user correction records:

```text
original claim or recognition
user-supplied correction
supporting evidence
verification state
scope
source artifact or passage
session and graph linkage
```

Verified corrections may alter the operational context plan. Unverified corrections are retained as claims rather than silently accepted or discarded.

## 31. Context trust and instruction authority are separate

Every block is labeled with both:

```text
evidence trust / review state
instruction authority
```

Only approved system and task-policy blocks have instruction authority.

The following are untrusted evidence even when scholarly or canonical in content:

- Retrieved web or document text
- OCR and VLM page text
- Tool outputs containing source content
- User uploads
- Bible and commentary text
- URLs and QR-code contents
- Model-generated summaries

A source saying “ignore previous instructions” remains a quoted source string, not a command.

## 32. Rights and privacy constrain composition before retrieval display

The context composer applies DR-10 at two separate points:

1. May the evidence enter this model or service route?
2. May the resulting answer quote, paraphrase, expose, cache, log, or release it?

A locally licensed source may be eligible for local RAG but not for an external API model. A private user upload may be eligible for transient processing but not session reuse or training.

Rights filters cannot be applied only after the packet has already been sent to an unauthorized provider.

## 33. Multilingual context is tokenized and routed per language

The same passage can occupy very different token budgets in different scripts and languages.

The composer therefore records per block:

```text
source language and variety
question and answer language
quotation language
pivot language
exact token count
translation provenance
right-to-left or mixed-direction state
language-support tier
```

A full-English-New-Testament result cannot be used to claim that Greek, Spanish, French, Syriac, or mixed parallel contexts fit or perform equally.

When a pivot translation is used to reduce or bridge context, it remains explicit and cannot replace original wording when the wording itself is material.

## 34. Multimodal context uses region-aware budgets

Images do not enter the packet as one opaque “image present” flag.

DR-14's overview-detail packet supplies:

- Full-page overview
- Region overview
- High-resolution crops
- Recognition hypotheses
- Region authority and language
- Omitted regions

The composer accounts for modality-token cost and may select only relevant detail crops while preserving the full-page overview needed to interpret their role.

It may not omit the page region containing a footnote and then claim to have considered that footnote.

## 35. Tool schemas and results are budgeted evidence

Tool descriptions and outputs consume context and can distract the model.

The composer therefore:

- Exposes only tools needed for the task;
- Uses compact, versioned schemas;
- Reserves result capacity;
- Truncates tool output only under source-aware rules;
- Preserves exact evidence handles;
- Prevents repeated tool calls from evicting required evidence;
- Records all tool-driven packet expansions.

A tool set is not expanded merely because the model can call more tools.

## 36. Context caching is hash-addressed and nonauthoritative

Immutable packets and stable prefixes may be cached for efficiency.

Every cache entry records:

```text
context or prefix hash
model and processor identity
runtime
rights and privacy scope
creation and expiration
source snapshot
invalidation dependencies
```

A cache hit does not bypass rights, freshness, or source-status checks. A corrected edition, retracted scholarship source, changed user permission, or modified context policy invalidates affected entries.

Private or restricted cache content cannot be shared across unauthorized users or environments.

## 37. Context extension beyond the native window is separately gated

Qwen documentation describes YaRN-based extension from 262K to approximately 1.01M tokens. Such extension is not the baseline.[^qwen-ultra]

Any native-window extension requires:

- A separately identified derived model/runtime configuration;
- Position-encoding and multimodal-compatibility review;
- Short- and long-context retention tests;
- RULER, NoLiMa, BABILong, and domain-specific tests;
- Latency, memory, and cost analysis;
- Citation and source-type retention;
- Exact fallback and rollback;
- Owner approval.

A runtime accepting a million-token prompt is insufficient evidence.

## 38. Long-context training does not default to maximum length

Continued pretraining or SFT at the maximum window can be expensive and may dilute learning or impair short-context behavior.

The initial policy is:

- Preserve the official position and attention architecture.
- Use a measured sequence-length curriculum.
- Retain substantial short- and medium-context data.
- Train on genuine long dependencies rather than padding or concatenation alone.
- Include evidence-position, multi-hop, and distractor variation.
- Evaluate checkpoints by context length and task.
- Stop if long-context gains materially damage ordinary passage work, multilingual behavior, multimodality, tool use, or calibration.

Research such as RULER, BABILong, and later long-context training work demonstrates that long-sequence acceptance and long-dependency learning are not equivalent.[^ruler] [^babilong] [^untie]

Exact training lengths, data volumes, and objectives remain later experiment decisions.

## 39. Context Composer behavior must survive adaptation

Every CPT, SFT, preference, adapter, merge, quantization, or distillation stage reruns:

- Packet-schema adherence
- Tool-use and evidence-coverage behavior
- Position sweeps
- Short, medium, and long contexts
- Full-book and full-New-Testament modes
- Citation and counterevidence retention
- Multilingual context
- Multimodal page context
- Context-injection resistance
- Cost and latency

A model that improves domain knowledge but stops using long evidence reliably is not promoted.

## 40. Long-context benchmark track

The benchmark includes controlled cases for:

### Position

- Decisive evidence at beginning, middle, and end
- Counterevidence separated from supporting evidence
- Several distant evidence points

### Retrieval difficulty

- Literal match
- Paraphrase
- Low lexical overlap
- Implicit relation
- Citation-network relation
- Translation-lineage relation

### Reasoning

- Single fact
- Multi-hop
- Aggregation
- Chronology
- Comparison
- Absence-sensitive claims
- Global theme or discourse structure
- Competing interpretations

### Biblical scope

- Passage
- Chapter
- Book
- Cross-book
- Full New Testament
- Septuagint/New Testament relation
- Translation family across many passages

### Evidence quality

- Relevant distractors
- Real but methodologically unfit sources
- Duplicate or dependent sources
- Contradictory scholarship
- Missing evidence
- Rights-redacted evidence

### Multi-turn

- User correction
- Changed edition
- Long conversation drift
- Summary corruption
- Resolved and reopened questions

### Multilingual and multimodal

- Different token budgets and pivots
- Mixed-language sources
- Page overview/detail evidence
- Footnotes and paratext
- Image plus long scholarship packet

## 41. Required ablations

At minimum, the benchmark compares:

```text
model alone
focused passage context
tools only
short-chunk RAG
long-unit RAG
book context
full New Testament context
full New Testament + targeted RAG
full New Testament + tools + RAG
structured evidence packet
structured packet + staged tool loop
compact model versus high-capacity fallback
```

For each model family, the comparison uses equivalent evidence and task semantics rather than mechanically identical token counts when tokenizers differ.

## 42. Primary metrics

Required metrics include:

```text
answer correctness
claim/evidence entailment
primary-text fidelity
source-type accuracy
citation and locator accuracy
material evidence recall
counterevidence recall
missing-evidence detection
position sensitivity
length sensitivity
distractor susceptibility
implicit-retrieval accuracy
multi-hop and aggregation accuracy
full-canon pattern accuracy
false-pattern rate
context-dilution delta
mode-routing accuracy
unnecessary-escalation rate
under-escalation rate
context-budget conformance
compression-loss rate
answer-language retention
prompt-injection success rate
latency
prefill and decode throughput
peak memory
actual token and dollar cost
```

Reports show curves by context length and position. One average score cannot hide middle-position collapse or severe cost growth.

## 43. Promotion gates

A broader context mode is promoted only if it:

- Improves a named task class over focused tools/RAG;
- Preserves citation and source-type hard metrics;
- Does not materially increase false thematic or intertextual links;
- Demonstrates acceptable position robustness;
- Has a clear cost and latency envelope;
- Preserves multilingual and multimodal behavior;
- Includes a reliable fallback;
- Passes expert review;
- Receives owner approval.

The full-New-Testament mode may be valuable even if it is not the default. It can be approved for specific task families and disabled elsewhere.

## 44. Long-context hard failures

DR-15 treats the following as hard failures:

- Advertising the native window as effective scholarly capacity without measurement.
- Filling the window without reserving output, reasoning, or tool capacity.
- Inserting the full New Testament as system instructions rather than evidence.
- Quoting exact text from a full-canon block without edition verification.
- Silently omitting required counterevidence because of budget pressure.
- Truncating a quotation, apparatus entry, or source qualification while preserving a misleading conclusion.
- Presenting a model summary as the underlying evidence.
- Losing source, rights, language, or review identity during compression.
- Allowing P3 background to evict P1 evidence.
- Treating RAG and long context as universally interchangeable.
- Using model confidence alone to decide that retrieval is complete.
- Claiming consideration of a page region, source, or passage omitted from the packet.
- Silently replaying an indefinite conversation history.
- Allowing document content to acquire instruction authority.
- Sending restricted or private context to an unauthorized model route.
- Hiding an English pivot or model-generated translation.
- Enabling context extension beyond native length without a separate evaluation.
- Promoting long-context training that damages ordinary passage, citation, multilingual, or multimodal performance.
- Reporting one long-context average that conceals position or task collapse.
- Compacting away a verified user correction, material alternative, counterevidence, uncertainty, rights restriction, or active safety state.
- Using a compacted summary as the sole basis for an exact quotation, citation, textual claim, or scholarly attribution without rehydration.
- Continuing to rely on a stale compaction artifact after a source, rights, graph, user, or task change invalidates it.
- Allowing opaque provider-native compaction to alter scholarly meaning without a usage receipt, disclosed loss, and rehydration path.
- Treating a learned memory projection as authoritative evidence.

## 45. Sol implementation discretion

Sol may determine design-neutral implementation details such as:

- Module and function organization
- Internal immutable collection types
- Efficient token-count caching
- Equivalent serialization mechanics
- Test implementation
- Performance optimizations that preserve the approved plan and packet semantics

Sol may not independently change:

- Context modes or routing authority
- Priority classes
- Evidence-dependency semantics
- Rights and trust behavior
- Counterevidence protection
- Compression classes
- Compaction classes, protected-state rules, rehydration, and invalidation semantics
- Packet, compaction-artifact, or receipt meaning
- Full-New-Testament default policy
- Long-context benchmark or promotion gates
- Training-context policy
- Experiment design

A technical limitation that requires a material contract change returns:

```text
BLOCKED_REQUIRES_DESIGN_REVIEW
```

Luna may execute only frozen token-census, context-evaluation, cache, or training campaigns delegated by Sol. Luna may not change context code, ordering, budgets, evidence, models, thresholds, or experiment design.

## 46. Binding decisions

Approval of DR-15 locks:

1. Native, configured, verified, and effective task context remain separate.
2. Long context is treated as an evidence-composition problem rather than a maximum-token feature.
3. The project implements a deterministic, reviewable `ContextComposer`.
4. Context requests, requirements, units, dependencies, budgets, plans, blocks, projections, packets, usage receipts, and compaction artifacts remain distinct versioned entities.
5. Focused tools plus targeted evidence is the default production route.
6. Full-book and full-New-Testament context remain explicit, task-specific modes.
7. The complete New Testament is an evidence block with no instruction authority.
8. Full-canon context never replaces deterministic quotation, edition, linguistic, or apparatus tools.
9. Exact token and modality census is required per model, processor, language, formatting scheme, and mode.
10. Input, output, reasoning, multimodal, and tool-loop capacity are allocated before evidence selection.
11. Priority classes prevent convenience context from evicting required evidence.
12. Final evidence units preserve semantic boundaries and dependencies rather than being arbitrary fixed chunks.
13. Selection is dependency-closed and protects material counterevidence.
14. RAG, long retrieved units, book context, canon context, and hybrid modes remain distinct comparators.
15. Initial routing is deterministic and evidence-coverage-aware; learned routing is separately gated.
16. Evidence-coverage outcomes determine expansion, escalation, clarification, or abstention.
17. Context ordering is explicit and benchmarked for positional sensitivity.
18. Exact quotation and citation-critical spans receive compression protection.
19. Compression classes and losses remain explicit and provenance-bearing.
20. Context compaction is a first-class, versioned lifecycle operation distinct from compression.
21. Every compaction produces an immutable `ContextCompactionArtifact` with declared inputs, policy, losses, retained and omitted state, rights, review state, invalidation dependencies, and rehydration instructions.
22. The approved compaction classes are `K0` lossless deduplication, `K1` structured state extraction, `K2` evidence-handle compaction, `K3` reviewed abstract compaction, `K4` model-summary candidate, and separately gated `K5` learned-memory projection.
23. User corrections, exact identities, material text, alternatives, counterevidence, uncertainty, rights, provenance, and active safety state may not be silently compacted away.
24. Exact quotations and consequential scholarly claims require rehydration and revalidation against authoritative evidence when that evidence is absent from active context.
25. Compaction artifacts are invalidated or reevaluated after material source, rights, graph, user, task, policy, model, or runtime changes.
26. Model-generated summaries and learned memory projections remain derivatives rather than evidence.
27. Backend-native cache or state compaction remains subordinate to the semantic-retention, audit, rehydration, and fallback contract.
28. Compaction receives explicit benchmark ablations for evidence retention, counterevidence, corrections, citations, uncertainty, drift, cost, rights, and safety state.
29. Context plans and model-facing packets are immutable and hash-addressed.
30. Post-execution usage receipts record observable evidence, tool, citation, resource, compaction, rehydration, and fallback behavior without requiring private chain-of-thought.
31. Multi-turn state is structured; indefinite raw-history replay is prohibited.
32. User corrections remain versioned evidence claims.
33. Evidence trust and instruction authority remain separate.
34. Rights and privacy constrain model-route composition before transmission.
35. Multilingual and multimodal context receive exact per-block budgets and provenance.
36. Tool schemas and results are bounded, task-specific context.
37. Caches are hash-addressed, rights-scoped, invalidatable, and nonauthoritative.
38. Native-window extension is a separately reviewed derivative experiment.
39. Long-context training uses a measured curriculum and cannot sacrifice short-context capability silently.
40. Every model adaptation and derivative reruns context-composer, compaction, and long-context retention tests.
41. The benchmark includes position, length, distractor, implicit-retrieval, multi-hop, full-canon, compaction, multi-turn, multilingual, and multimodal cases.
42. Full-canon context must beat or complement focused RAG for a named task before product promotion.
43. Sol implements the approved architecture; ChatGPT designs and reviews experiments; Joseph approves consequential changes.
44. Luna may only execute frozen campaigns delegated by Sol.

## 47. Decisions intentionally deferred

DR-15 does not yet select:

- the exact full-New-Testament translation or source edition used in each product mode;
- final context-length claims for any candidate family;
- exact token budget percentages;
- exact chunk or evidence-unit expansion algorithm;
- the final retriever or reranker;
- final context ordering after the benchmark;
- whether task-card duplication is useful for each family;
- exact thresholds for book, canon, or larger-model escalation;
- final context-compression models or loss limits;
- exact compaction trigger thresholds, retention periods, reviewed-abstract workflow, and automated promotion rules;
- exact KV-cache eviction, provider-native compaction, recurrent-state, prefix-cache, and other backend memory mechanisms;
- whether any `K5` learned-memory projection or learned router is promoted;
- exact cache product or retention duration;
- exact long-context training curriculum and token volume;
- final native-window extension policy for any model;
- final KV-cache, sparse-attention, or context-compression optimization;
- exact mobile context limit;
- exact benchmark case count and promotion thresholds;
- final user-interface controls for context mode and cost.

Those decisions belong to DR-16 through DR-29, DR-28's integrated contract registry, and owner-approved experiments.

## 48. Approved statement

> **Biblical Scholar Lab will treat long context as a bounded, evidence-bearing composition, routing, and state-lifecycle problem rather than equating a model's accepted token count with effective scholarly understanding. Native, configured, verified, and task-effective context limits will remain separate and will be measured per exact model, runtime, precision, language, modality, reasoning mode, and task. A deterministic Context Composer will transform a versioned request and evidence-dependency graph into an immutable context plan, budget ledger, ordered context packet, model-specific projection, and post-execution usage receipt. Focused deterministic tools and targeted evidence will remain the default route; book, full-New-Testament, research-synthesis, multimodal, and hybrid canon-plus-RAG modes will be invoked only when the evidence dependency requires them and their measured benefit justifies their cost. The complete New Testament will remain an identified evidence block with no instruction authority and will never replace exact edition, quotation, linguistic, translation, or apparatus tools. Context selection will protect required primary evidence, material alternatives, counterevidence, citation-critical wording, rights, privacy, language, and provenance; compression, summaries, caches, and learned memory will remain explicit derivatives with declared losses. Context compaction will be a versioned transition distinct from compression: it may deduplicate content, extract structured research state, replace source text with immutable evidence handles, or create reviewed derivative abstracts, but it may not silently discard user corrections, source identity, exact text under analysis, material alternatives, counterevidence, uncertainty, rights restrictions, or unresolved decisions. Every compaction artifact will declare its inputs, policy, information loss, retained and omitted units, rehydration path, process identity, review state, invalidation dependencies, and hash. Exact quotations and consequential scholarly claims will be revalidated against rehydrated authoritative evidence; model summaries, learned projections, and backend-native cache compaction will never become unmarked evidence. Multi-turn state will be structured rather than replayed indefinitely, untrusted document content will never gain instruction authority, and restricted evidence will be filtered before transmission to a model route. Long-context capability, compaction, training, context extension, routing, and compression will be promoted only through position-, length-, distractor-, multi-hop-, full-canon-, compaction-, multilingual-, multimodal-, citation-, and cost-aware ablations that preserve ordinary passage capability and pass expert and owner review.**

---

## References

[^qwen-context]: Qwen, `Qwen/Qwen3.5-9B-Base` model card. The official card reports a 262,144-token native context and the hybrid Gated DeltaNet/full-attention architecture: https://huggingface.co/Qwen/Qwen3.5-9B-Base

[^qwen-ultra]: Qwen, `Qwen/Qwen3.5-9B` README, “Processing Ultra-Long Texts.” The documentation describes 262,144 native tokens, input/output sharing the model limit, and optional YaRN configuration to extend to approximately 1.01M tokens: https://huggingface.co/Qwen/Qwen3.5-9B/blob/main/README.md

[^gemma-context]: Google DeepMind, “Gemma 4 model card.” The official model card reports 256K context for the 12B and 31B models, hybrid local/global attention, and vendor long-context benchmark results: https://ai.google.dev/gemma/docs/core/model_card_4

[^ministral-context]: Mistral AI, `mistralai/Ministral-3-8B-Base-2512` model card. The official card reports a 256K context and notes that a lower configured maximum is appropriate for many memory-constrained deployments: https://huggingface.co/mistralai/Ministral-3-8B-Base-2512

[^rhema-context]: Rhema, “Meet BibleAI: our first open-source model, free for the Church,” April 15, 2026. Rhema describes a 128K context as roughly sufficient for the New Testament plus a question. This is treated as prior-art motivation rather than a tokenizer-independent fact: https://rhemabible.co/blog/introducing-bibleai

[^lost-middle]: Nelson F. Liu et al., “Lost in the Middle: How Language Models Use Long Contexts,” 2023. The paper reports substantial position sensitivity, with relevant evidence often used more effectively near the beginning or end than in the middle: https://arxiv.org/abs/2307.03172

[^ruler]: Cheng-Ping Hsieh et al., “RULER: What's the Real Context Size of Your Long-Context Language Models?,” 2024. RULER extends simple needle tests with multiple needles, multi-hop tracing, and aggregation and reports large performance drops as length and complexity increase: https://arxiv.org/abs/2404.06654

[^nolima]: Ali Modarressi et al., “NoLiMa: Long-Context Evaluation Beyond Literal Matching,” 2025. NoLiMa removes easy lexical overlap and reports substantial degradation as context length increases, illustrating the difference between literal lookup and latent-association retrieval: https://arxiv.org/abs/2502.05167

[^longbench2]: Yushi Bai et al., “LongBench v2: Towards Deeper Understanding and Reasoning on Realistic Long-context Multitasks,” 2024. LongBench v2 evaluates realistic single- and multi-document, dialogue, code, and structured-data tasks requiring deeper reasoning: https://arxiv.org/abs/2412.15204

[^babilong]: Yuri Kuratov et al., “BABILong: Testing the Limits of LLMs with Long Context Reasoning-in-a-Haystack,” 2024. BABILong scatters facts through long natural text and evaluates reasoning, induction, deduction, counting, and set/list behavior: https://arxiv.org/abs/2406.10149

[^rag-lc]: Zhuowan Li et al., “Retrieval Augmented Generation or Long-Context LLMs? A Comprehensive Study and Hybrid Approach,” 2024. The study reports stronger average performance from sufficiently capable long-context models, substantially lower token cost from RAG, and a hybrid routing method with comparable performance at reduced cost: https://arxiv.org/abs/2407.16833

[^longrag]: Ziyan Jiang, Xueguang Ma, and Wenhu Chen, “LongRAG: Enhancing Retrieval-Augmented Generation with Long-context LLMs,” 2024. The work explores larger retrieval units and long-context readers to preserve document context lost by short chunks: https://arxiv.org/abs/2406.15319

[^untie]: Junfeng Tian et al., “Untie the Knots: An Efficient Data Augmentation Strategy for Long-Context Pre-Training in Language Models,” ACL 2025. The work demonstrates that explicitly training models to locate and connect relevant material can improve long-context performance and that long-context capability is a training problem, not only a window-size configuration: https://aclanthology.org/2025.acl-long.62/
