# BENCH-VS01-BATCH-01 — John 1:5 Benchmark Seed

| Field | Value |
|---|---|
| Batch ID | `BENCH-VS01-BATCH-01` |
| Status | `APPROVED_CONTENT_FROZEN_PENDING_EXECUTION_PREREQUISITES` |
| Approval date | 2026-08-17 |
| Design and case author | ChatGPT |
| Owner reviewer and approver | Joseph Abbud |
| Sol benchmark-content authority | None; implementation machinery only |
| Review scope | Twelve public-safe `REV-P0` / `REV-P1` case families for `VS-01` |
| Depends on | Design baseline `2f9f0a1d2e56279787ebac81fffc9ded4cdfd92d`, `VS-01`, and `SOURCE-PLAN-01` |
| Owner disposition | Approved with the fixed-evidence/full-runtime clarification on 2026-08-17 |
| Execution status | Blocked until source verification, fixture generation, repository governance, and implementation activation |
| Machine-readable case file | `BENCH-VS01-BATCH-01-cases.json` |
| Machine-readable SHA-256 | `4241a0bf5baf50a12ce5fe6dcfef6ed5492cde410f3d92f5aad8a9f26ba3113f` |

## 1. High-level purpose

This batch turns the approved VS-01 benchmark-family blueprints into the first actual examination content. It measures whether a bounded John 1:5 system can preserve exact text and edition identity, use Greek morphology responsibly, diagnose a translation choice without inventing a manuscript variant, cite the evidence that supports each claim, distinguish Scripture from page paratext, preserve user corrections through compaction, and keep Brief and Study answers substantively consistent.

The cases are deliberately public-safe and source-verifiable. They are not specialist `REV-P2` gold, private final holdouts, training data, or a comprehensive benchmark of John, Greek semantics, or textual criticism.

## 2. Authority and review boundary

- ChatGPT authored the prompts, evidence contracts, answer boundaries, reference responses, rubrics, case-family assignments, and public-safe split recommendations.
- Joseph reviews and approves, limits, revises, splits, or rejects the batch.
- Sol may later implement schemas, loaders, deterministic page generation, scorers, reports, and execution adapters. Sol may not alter the semantic content.
- The cases remain `SOURCE_VERIFICATION_PENDING` until SOURCE-PLAN-01 is implemented and the acquired bytes, lexical entry, evidence packet, and page fixture are verified.
- Because ChatGPT authored these cases, they cannot by themselves support an uncontaminated independent-final-exam claim for an OpenAI frontier model.
- All twelve cases share the `passage:John.1.5` contamination cluster and remain in the public-safe seed partition together; they may not later be split across training and evaluation or public and private claims as though they were independent passage evidence.

## 3. Batch composition

| Family | Partition | Mode | Construct |
|---|---|---|---|
| `VS01-B01` | `REV-P0_DETERMINISTIC_AND_OPERATIONAL` | `DETERMINISTIC_TOOLS_ONLY` | Exact reference and edition resolution without silently substituting another translation. |
| `VS01-B02` | `REV-P0_DETERMINISTIC_AND_OPERATIONAL` | `FIXED_PRIMARY_EVIDENCE` | Exact source-span, lemma, and morphological-form identification without inferring contextual sense from morphology alone. |
| `VS01-B03` | `REV-P0_DETERMINISTIC_AND_OPERATIONAL` | `FIXED_PRIMARY_EVIDENCE` | Exact edition-labeled surface comparison before interpretation. |
| `VS01-B04` | `REV-P1_SOURCE_VERIFIABLE_SCHOLARLY_BEHAVIOR` | `FIXED_COMPLETE_EVIDENCE_PACKET` | Distinguish a translation choice from evidence of different manuscript readings. |
| `VS01-B05` | `REV-P1_SOURCE_VERIFIABLE_SCHOLARLY_BEHAVIOR` | `FIXED_COMPLETE_EVIDENCE_PACKET` | Prevent a lexicon’s possible senses from being treated as simultaneously active contextual meaning. |
| `VS01-B06` | `REV-P1_SOURCE_VERIFIABLE_SCHOLARLY_BEHAVIOR` | `FIXED_COMPLETE_EVIDENCE_PACKET` | Present cognitive and conflict-oriented effects as defensible alternatives while preserving the limit of the P1 evidence. |
| `VS01-B07` | `REV-P0_DETERMINISTIC_AND_OPERATIONAL` | `FIXED_COMPLETE_EVIDENCE_PACKET` | Claim-level citation entailment and source-role compatibility. |
| `VS01-B08` | `REV-P1_SOURCE_VERIFIABLE_SCHOLARLY_BEHAVIOR` | `FIXED_PRIMARY_EVIDENCE` | Evidence-sufficiency recognition and appropriate abstention from source-language claims. |
| `VS01-B09` | `REV-P0_DETERMINISTIC_AND_OPERATIONAL` | `IMAGE_PLUS_TOOLS` | Page-region role and authority classification with exact canonical quotation. |
| `VS01-B10` | `REV-P0_DETERMINISTIC_AND_OPERATIONAL` | `IMAGE_PLUS_TOOLS` | Separate visual transcription confidence from deterministic canonical lookup. |
| `VS01-B11` | `REV-P0_DETERMINISTIC_AND_OPERATIONAL` | `COMPACTED_SESSION` | Latest user correction survives structured state extraction and evidence-handle compaction. |
| `VS01-B12` | `REV-P1_SOURCE_VERIFIABLE_SCHOLARLY_BEHAVIOR` | `FIXED_COMPLETE_EVIDENCE_PACKET` | Progressive disclosure changes depth without changing the verified conclusion or suppressing material uncertainty. |

## 4. Shared scholarly boundary

The batch may test and reward only the bounded conclusions already approved by SOURCE-PLAN-01:

- `κατέλαβεν` is the target SBLGNT form; MorphGNT supplies the approved lemma and morphological form.
- ASV uses “apprehended it not”; WEB Classic uses “hasn’t overcome it.”
- The controlled wording difference does not require a different Greek source reading.
- Cognitive/apprehension and conflict/defeat effects may be discussed as bounded alternatives.
- A possible ambiguity or double resonance may be described only as a possibility.
- The evidence does not establish one final specialist-preferred rendering, translator intent, current consensus, or identical complete base editions.


### Fixed-evidence versus full-runtime behavior

This batch freezes a distinction that is central to both benchmark validity and the intended product experience:

```text
evidence absent from the prompt
    ≠
evidence unavailable to the system
```

A fixed-evidence case measures what the subject may responsibly conclude from the evidence deliberately supplied. When tools are prohibited or the required evidence is genuinely inaccessible, qualification or abstention is correct.

A full-runtime case measures whether the Runtime Scholar Harness recognizes a missing evidentiary layer, invokes the approved deterministic or retrieval tools, acquires the evidence, and continues the analysis. When an approved source or tool is available, merely stopping at “insufficient evidence” is a tool-selection or runtime-planning failure and is not rewarded as epistemic caution.

Accordingly, `VS01-B08-C01` is an intentionally incomplete fixed-evidence test, not the desired default UX. A paired `FULL_RUNTIME_HARNESS` case, provisionally identified as `VS01-B08-RUNTIME-C01`, must be separately authored by ChatGPT and approved by Joseph before VS-01 runtime promotion.

## 5. Evidence contracts

### `EC-VS01-01-EXACT-TEXTS`

**Completeness:** `COMPLETE_FOR_DEFINED_CLAIM`

**Required:** `SP01-SRC-001#John.1.5`; `SP01-SRC-003#John.1.5`; `SP01-SRC-004#John.1.5`

**Can support:** exact passage identity; exact edition wording; surface translation comparison.

**Cannot support:** contextual Greek sense; morphological analysis; textual-critical reconstruction; translator intent; scholarly consensus.

### `EC-VS01-02-GREEK-MORPH`

**Completeness:** `COMPLETE_FOR_DEFINED_CLAIM`

**Required:** `SP01-SRC-001#John.1.5`; `SP01-SRC-002#John.1.5:κατέλαβεν`

**Can support:** exact Greek token identity; lemma; morphological form.

**Cannot support:** one exclusive contextual sense; translator intent; current scholarly consensus.

### `EC-VS01-03-COMPLETE-TNC`

**Completeness:** `SUFFICIENT_WITH_QUALIFICATION`

**Required:** `SP01-SRC-001#John.1.5`; `SP01-SRC-002#John.1.5:κατέλαβεν`; `SP01-SRC-003#John.1.5`; `SP01-SRC-004#John.1.5`; `SP01-SRC-005#καταλαμβάνω`; `SP01-DER-001#John.1.5`

**Can support:** the controlled wording difference does not require a different Greek source reading; bounded cognitive/apprehension and conflict/defeat effects; source-verifiable uncertainty and alternative analysis.

**Cannot support:** the projects used identical complete Greek base editions; one final specialist-preferred rendering; translator intent; current scholarly consensus.

### `EC-VS01-04-TRANSLATIONS-ONLY`

**Completeness:** `INTENTIONALLY_INCOMPLETE`

**Required:** `SP01-SRC-003#John.1.5`; `SP01-SRC-004#John.1.5`

**Can support:** the two English editions have different wording.

**Cannot support:** Greek lexical range; morphology; textual variant status; source edition identity; one preferred interpretation.

**Expected behavior:** In this deliberately constrained fixed-evidence condition, qualify or abstain from claims that require withheld source-language evidence. This is not the product default when approved tools can acquire the missing evidence.

### `EC-VS01-05-PAGE-BASE`

**Completeness:** `COMPLETE_FOR_DEFINED_CLAIM`

**Required:** `SP01-DER-002#base-page`; `SP01-SRC-003#John.1.5`

**Can support:** page-region role; authority class; exact ASV canonical wording.

**Cannot support:** the synthetic page is a historical or publisher-produced page.

### `EC-VS01-06-PAGE-DEGRADED`

**Completeness:** `INTENTIONALLY_INCOMPLETE`

**Required:** `SP01-DER-002#degraded-illegibility-v1`; `SP01-SRC-003#John.1.5`

**Can support:** which words are visibly legible; what the canonical ASV source contains when explicitly looked up.

**Cannot support:** claim that obscured words were visually read.

**Expected behavior:** Mark the obscured visual phrase illegible and distinguish canonical lookup from visual observation.

### `EC-VS01-07-SESSION-COMPACTION`

**Completeness:** `COMPLETE_FOR_DEFINED_CLAIM`

**Required:** `SP01-SRC-003#John.1.5`; `SP01-SRC-004#John.1.5`; `session-event:initial-web-primary`; `session-event:user-correction-asv-primary`; `compaction-artifact:K1-K2-v1`

**Can support:** latest active edition preference; correction precedence; correct primary and secondary quotation roles.

**Cannot support:** discarding the user correction because an older preference appeared earlier.

## 6. Case-by-case review

### `VS01-B01-C01` — Resolve and quote John 1:5 from the approved ASV edition

**Family:** `VS01-B01`  
**Track:** `PRIMARY_TEXT_REFERENCE_AND_CANON`  
**Review partition:** `REV-P0_DETERMINISTIC_AND_OPERATIONAL`  
**Evaluation mode:** `DETERMINISTIC_TOOLS_ONLY`  
**Split recommendation:** `PUBLIC_REPRODUCTION_CANDIDATE`  
**SME state:** `NOT_REQUIRED_FOR_REV_P0`  
**Case SHA-256:** `4e9a8801921684c311267571e97a8382ef29691a5f60f782009199537d5b77fb`

**Construct:** Exact reference and edition resolution without silently substituting another translation.

**Prompt**

> In the approved American Standard Version edition, quote John 1:5 exactly and identify the edition. Do not substitute the World English Bible.

**Required behavior**

- The selected edition is the American Standard Version (1901), openbibleinfo digital USX edition.
- The exact approved wording is: “And the light shineth in the darkness; and the darkness apprehended it not.”

**Prohibited behavior**

- Presenting WEB wording as ASV.
- Omitting the edition identity.
- Adding footnotes or headings as canonical text.

**Reference response**

> The approved American Standard Version (1901), in the openbibleinfo digital USX edition, reads: “And the light shineth in the darkness; and the darkness apprehended it not.” [SP01-SRC-003#John.1.5]

**Atomic rubric**

- `B01-R1` — Exact ASV wording (weight 2; 0–2). Hard-failure trigger: Wrong or fabricated canonical wording.
- `B01-R2` — Edition identity and citation (weight 1; 0–2). Hard-failure trigger: Exact quotation without edition/source identity.

### `VS01-B02-C01` — Identify the Greek target span and morphology

**Family:** `VS01-B02`  
**Track:** `LINGUISTIC_REPRESENTATION_AND_ANALYSIS`  
**Review partition:** `REV-P0_DETERMINISTIC_AND_OPERATIONAL`  
**Evaluation mode:** `FIXED_PRIMARY_EVIDENCE`  
**Split recommendation:** `PUBLIC_REPRODUCTION_CANDIDATE`  
**SME state:** `NOT_REQUIRED_FOR_REV_P0`  
**Case SHA-256:** `ecfebb47228220bac9a1d5b710a78c216f216f15aa1c1e519652ca2e5d9a8ece`

**Construct:** Exact source-span, lemma, and morphological-form identification without inferring contextual sense from morphology alone.

**Prompt**

> In the supplied SBLGNT John 1:5 text, identify the Greek verb corresponding to the disputed final rendering. Give its lemma and morphological form, then state one thing morphology alone does not establish.

**Required behavior**

- The target surface form is κατέλαβεν.
- The lemma is καταλαμβάνω.
- The form is a verb, third-person singular, aorist active indicative.
- Morphology alone does not determine the contextual English sense or settle the translation question.

**Prohibited behavior**

- The aorist proves a once-for-all action.
- Morphology proves “understand” or “overcome.”

**Reference response**

> The target verb is κατέλαβεν, from the lemma καταλαμβάνω. MorphGNT parses it as a third-person singular aorist active indicative verb. That formal analysis does not by itself determine whether the best contextual English rendering is cognitive (“apprehend/understand”), conflict-oriented (“overcome/master”), or another defensible option. [SP01-SRC-001#John.1.5] [SP01-SRC-002#John.1.5:κατέλαβεν]

**Atomic rubric**

- `B02-R1` — Exact Greek span and lemma (weight 2; 0–2). Hard-failure trigger: Wrong Greek source span or lemma.
- `B02-R2` — Morphological form (weight 2; 0–2). Hard-failure trigger: Materially incorrect parse.
- `B02-R3` — Formal-versus-contextual restraint (weight 1; 0–2). Hard-failure trigger: Morphology presented as decisive contextual meaning.

### `VS01-B03-C01` — Compare exact ASV and WEB wording without interpretation

**Family:** `VS01-B03`  
**Track:** `PRIMARY_TEXT_REFERENCE_AND_CANON`  
**Review partition:** `REV-P0_DETERMINISTIC_AND_OPERATIONAL`  
**Evaluation mode:** `FIXED_PRIMARY_EVIDENCE`  
**Split recommendation:** `DEV_PUBLIC_CANDIDATE`  
**SME state:** `NOT_REQUIRED_FOR_REV_P0`  
**Case SHA-256:** `049f633f017823f6c50f19c75476f59a68474c6451c599a20db71560097305f0`

**Construct:** Exact edition-labeled surface comparison before interpretation.

**Prompt**

> Quote John 1:5 from the approved ASV and WEB Classic editions, then identify only the final-clause wording difference. Do not yet explain why they differ.

**Required behavior**

- ASV wording exactly matches the approved ASV source.
- WEB Classic wording exactly matches the acquisition-frozen approved WEB source.
- The salient final-clause contrast is “apprehended it not” versus “hasn’t overcome it.”

**Prohibited behavior**

- Interpretive diagnosis.
- Textual-variant claim.
- Translator-intent claim.

**Reference response**

> ASV (1901): “And the light shineth in the darkness; and the darkness apprehended it not.” [SP01-SRC-003#John.1.5]
>
> WEB Classic: “The light shines in the darkness, and the darkness hasn’t overcome it.” [SP01-SRC-004#John.1.5]
>
> The final-clause contrast is “apprehended it not” versus “hasn’t overcome it.”

**Atomic rubric**

- `B03-R1` — Exact edition-labeled quotations (weight 2; 0–2). Hard-failure trigger: Quotation or edition substitution.
- `B03-R2` — Surface difference isolated without overanalysis (weight 1; 0–2).

### `VS01-B04-C01` — Reject the false manuscript-variant inference

**Family:** `VS01-B04`  
**Track:** `TRANSLATION_NUANCE`  
**Review partition:** `REV-P1_SOURCE_VERIFIABLE_SCHOLARLY_BEHAVIOR`  
**Evaluation mode:** `FIXED_COMPLETE_EVIDENCE_PACKET`  
**Split recommendation:** `PUBLIC_REPRODUCTION_CANDIDATE`  
**SME state:** `SME_REVIEW_PENDING_NOT_REQUIRED_FOR_BOUNDED_REV_P1`  
**Case SHA-256:** `9664fcde1a4cac895d70cd905d129a784605dfcd65e96e5d0c345cb8ace21c46`

**Construct:** Distinguish a translation choice from evidence of different manuscript readings.

**Prompt**

> The ASV says “apprehended it not,” while WEB Classic says “hasn’t overcome it.” Does that prove the translations were based on different Greek manuscripts? Explain using only the supplied evidence.

**Required behavior**

- No: the English wording difference does not prove different Greek manuscripts.
- In the controlled evidence packet, no different Greek source reading is required to explain the contrast.
- The difference can be analyzed as a translation choice within the bounded lexical/semantic possibilities of καταλαμβάνω.
- The case does not establish that the two projects used identical complete Greek base editions.
- Required uncertainty: Do not infer complete source-edition identity beyond the supplied passage-level evidence.

**Prohibited behavior**

- Translation agreement or disagreement counts as manuscript evidence.
- The projects definitely used the same full Greek edition.
- A textual variant is established.

**Reference response**

> No. Different English renderings do not by themselves prove that the translations reflect different Greek manuscripts. In this controlled case, the same supplied SBLGNT wording contains κατέλαβεν, and no different Greek reading is required to explain the ASV’s “apprehended it not” and WEB Classic’s “hasn’t overcome it.” The contrast can therefore be analyzed as a translation choice that foregrounds different effects within the bounded lexical/semantic range. This passage-level evidence does not establish that the two translation projects used identical complete Greek base editions. [SP01-SRC-001#John.1.5] [SP01-SRC-003#John.1.5] [SP01-SRC-004#John.1.5] [SP01-DER-001#John.1.5]

**Atomic rubric**

- `B04-R1` — Rejects translation-as-witness inference (weight 2; 0–2). Hard-failure trigger: States or implies that the two English renderings prove different manuscripts.
- `B04-R2` — Correct bounded cause diagnosis (weight 2; 0–2).
- `B04-R3` — Preserves source-edition uncertainty (weight 1; 0–2). Hard-failure trigger: Claims identical full Greek base editions without evidence.
- `B04-R4` — Claim-level evidence support (weight 1; 0–2). Hard-failure trigger: Central claim lacks or misuses source evidence.

### `VS01-B05-C01` — Correct illegitimate totality transfer

**Family:** `VS01-B05`  
**Track:** `LINGUISTIC_REPRESENTATION_AND_ANALYSIS`  
**Review partition:** `REV-P1_SOURCE_VERIFIABLE_SCHOLARLY_BEHAVIOR`  
**Evaluation mode:** `FIXED_COMPLETE_EVIDENCE_PACKET`  
**Split recommendation:** `DEV_PUBLIC_CANDIDATE`  
**SME state:** `SME_REVIEW_PENDING_NOT_REQUIRED_FOR_BOUNDED_REV_P1`  
**Case SHA-256:** `3ade8c68fed0063598560fcb7f33c8ecb6fc31affb50f5a95189f8a965175772`

**Construct:** Prevent a lexicon’s possible senses from being treated as simultaneously active contextual meaning.

**Prompt**

> A study note claims: “Because καταλαμβάνω can mean understand, seize, attain, overtake, and overcome, all those meanings are present in John 1:5.” Evaluate that claim using the supplied evidence.

**Required behavior**

- The claim commits a gloss-as-definition or illegitimate-totality-transfer error.
- A lexicon records possible uses across contexts; it does not make every gloss active in one occurrence.
- The bounded evidence permits cognitive/apprehension and conflict/defeat effects to be considered, but the lexicon alone does not settle the contextual meaning.

**Prohibited behavior**

- All listed senses are simultaneously present.
- The root or morphology settles the meaning.
- The Greek literally means both.

**Reference response**

> That claim is too strong. A lexicon records possible uses of a word across different contexts; it does not make every gloss part of the meaning of one occurrence. Treating the whole entry as the meaning of John 1:5 would be illegitimate totality transfer. In this bounded case, cognitive/apprehension and conflict/defeat effects are both defensible possibilities to examine, but the lexicon alone does not decide which rendering is best or whether more than one resonance is active. [SP01-SRC-001#John.1.5] [SP01-SRC-005#καταλαμβάνω] [SP01-DER-001#John.1.5]

**Atomic rubric**

- `B05-R1` — Identifies the lexical fallacy (weight 2; 0–2). Hard-failure trigger: Endorses every gloss as simultaneously active.
- `B05-R2` — Explains contextual sense selection (weight 2; 0–2).
- `B05-R3` — Preserves bounded alternatives and uncertainty (weight 1; 0–2). Hard-failure trigger: Claims the lexicon alone settles the verse.

### `VS01-B06-C01` — Explain alternatives without false certainty

**Family:** `VS01-B06`  
**Track:** `TRANSLATION_NUANCE`  
**Review partition:** `REV-P1_SOURCE_VERIFIABLE_SCHOLARLY_BEHAVIOR`  
**Evaluation mode:** `FIXED_COMPLETE_EVIDENCE_PACKET`  
**Split recommendation:** `PUBLIC_REPRODUCTION_CANDIDATE`  
**SME state:** `SME_REVIEW_PENDING_NOT_REQUIRED_FOR_BOUNDED_REV_P1`  
**Case SHA-256:** `5a84bbdd91c3de39831c24ba39c17b643c02ec528aa20309f2718d6f594309ed`

**Construct:** Present cognitive and conflict-oriented effects as defensible alternatives while preserving the limit of the P1 evidence.

**Prompt**

> Why might one translation use “apprehended” and another use “overcome” in John 1:5? Give a calibrated explanation and state what the supplied evidence does not settle.

**Required behavior**

- ASV foregrounds a cognitive/apprehension effect.
- WEB Classic foregrounds a conflict/defeat effect.
- Both are connected to a broader grasping/seizing semantic family in the bounded evidence.
- A possible ambiguity or double resonance may be discussed as a possibility, not a settled fact.
- The evidence does not settle one final specialist-preferred rendering or translator intent.
- Required uncertainty: No definitive single rendering is established by this evidence packet.
- Required uncertainty: No translator-intent claim without translation documentation.

**Prohibited behavior**

- The Greek literally means both.
- One rendering is definitively correct.
- Current scholarly consensus is established.

**Reference response**

> The ASV’s “apprehended” foregrounds a cognitive or epistemic effect: the darkness does not grasp or understand the light. WEB Classic’s “overcome” foregrounds a conflict or defeat effect: the darkness does not master or extinguish the light. The supplied Greek and lexical evidence place both within a broader family of grasping or seizing ideas, so the translations make different effects salient. A double resonance is possible, but this P1 evidence packet does not prove that both senses are simultaneously intended, settle one final specialist-preferred rendering, or establish the translators’ intentions. [SP01-SRC-001#John.1.5] [SP01-SRC-003#John.1.5] [SP01-SRC-004#John.1.5] [SP01-SRC-005#καταλαμβάνω] [SP01-DER-001#John.1.5]

**Atomic rubric**

- `B06-R1` — Explains both principal effects (weight 2; 0–2).
- `B06-R2` — Connects effects to bounded evidence (weight 2; 0–2).
- `B06-R3` — Calibrates ambiguity and uncertainty (weight 2; 0–2). Hard-failure trigger: States that the Greek literally and definitively means both.
- `B06-R4` — Avoids translator-intent and consensus overclaim (weight 1; 0–2). Hard-failure trigger: Infers translator intent or consensus without evidence.

### `VS01-B07-C01` — Attach each claim to evidence that actually supports it

**Family:** `VS01-B07`  
**Track:** `SCHOLARSHIP_CITATION_AND_LANDSCAPE`  
**Review partition:** `REV-P0_DETERMINISTIC_AND_OPERATIONAL`  
**Evaluation mode:** `FIXED_COMPLETE_EVIDENCE_PACKET`  
**Split recommendation:** `PUBLIC_REPRODUCTION_CANDIDATE`  
**SME state:** `NOT_REQUIRED_FOR_REV_P0`  
**Case SHA-256:** `e1b54baa00e51174be723ba419886e454d225dc0b440ddaf17c6156fd0847f12`

**Construct:** Claim-level citation entailment and source-role compatibility.

**Prompt**

> Give a short cited explanation of the John 1:5 wording difference. Cite the Greek wording, morphology, each English rendering, and lexical-range claim to the source that actually supports it.

**Required behavior**

- Greek wording claim cites SBLGNT.
- Morphology claim cites MorphGNT.
- ASV wording claim cites ASV.
- WEB wording claim cites WEB.
- Lexical-range claim cites Abbott-Smith.

**Prohibited behavior**

- Citing the lexicon as manuscript evidence.
- Citing a translation as the source of Greek morphology.
- Fabricated bibliography or locator.

**Reference response**

> The SBLGNT text of John 1:5 ends with καὶ ἡ σκοτία αὐτὸ οὐ κατέλαβεν. [SP01-SRC-001#John.1.5] MorphGNT identifies κατέλαβεν as a third-person singular aorist active indicative form of καταλαμβάνω. [SP01-SRC-002#John.1.5:κατέλαβεν] The ASV renders the final clause “the darkness apprehended it not,” [SP01-SRC-003#John.1.5] while WEB Classic says “the darkness hasn’t overcome it.” [SP01-SRC-004#John.1.5] Abbott-Smith supplies lexical evidence for a range involving grasping or seizing ideas, which can support different contextual effects but does not by itself settle the verse. [SP01-SRC-005#καταλαμβάνω]

**Atomic rubric**

- `B07-R1` — Source identity and locator correctness (weight 2; 0–2). Hard-failure trigger: Fabricated source or locator.
- `B07-R2` — Claim-level entailment (weight 2; 0–2). Hard-failure trigger: A central claim is attached to evidence that does not support it.
- `B07-R3` — Source-role compatibility (weight 2; 0–2). Hard-failure trigger: Translation or lexicon treated as manuscript attestation.

### `VS01-B08-C01` — Qualify when only translations are available

**Family:** `VS01-B08`  
**Track:** `TOOLS_RETRIEVAL_AND_RUNTIME`  
**Review partition:** `REV-P1_SOURCE_VERIFIABLE_SCHOLARLY_BEHAVIOR`  
**Evaluation mode:** `FIXED_PRIMARY_EVIDENCE`  
**Split recommendation:** `DEV_PUBLIC_CANDIDATE`  
**SME state:** `SME_REVIEW_PENDING_NOT_REQUIRED_FOR_BOUNDED_REV_P1`  
**Case SHA-256:** `abb689a183a9f2f95f0985ecb40a45593832acc246d9ce26637adc0029a6b1e9`

**Construct:** Evidence-sufficiency recognition and appropriate abstention from source-language claims.

**Purpose boundary:** This case tests restraint under deliberately incomplete fixed evidence. It is not the default product interaction.

**Required paired runtime follow-up:** A separately authored `FULL_RUNTIME_HARNESS` variant must require proactive acquisition of the approved Greek, morphology, and bounded lexical evidence. In that paired condition, failure to attempt available evidence acquisition is a runtime-planning or tool-selection failure.


**Prompt**

> You have only the supplied ASV and WEB Classic wording for John 1:5. Does the Greek mean both “understand” and “overcome,” and is a textual variant involved?

**Required behavior**

- The evidence establishes only that the two English editions differ in wording.
- The available evidence is insufficient to establish the Greek lexical range, morphology, textual-variant status, or whether both senses are contextually active.
- The system should request or retrieve the Greek source, linguistic evidence, and if needed textual-critical evidence before answering those questions.
- Required uncertainty: No Greek or textual-critical conclusion from translations alone.

**Prohibited behavior**

- Inventing Greek evidence.
- Declaring a textual variant from English wording.
- Claiming both meanings are present.

**Reference response**

> From the two translations alone, we can establish only that the ASV and WEB Classic use different English wording. We cannot responsibly determine the Greek lexical range, morphology, whether both effects are contextually active, or whether a textual variant is involved without the Greek source and relevant linguistic—and, if necessary, textual-critical—evidence. [SP01-SRC-003#John.1.5] [SP01-SRC-004#John.1.5]

**Atomic rubric**

- `B08-R1` — Recognizes evidence insufficiency (weight 2; 0–2). Hard-failure trigger: Gives a confident Greek or variant conclusion from translations alone.
- `B08-R2` — States what the available evidence does establish (weight 1; 0–2).
- `B08-R3` — Requests the right missing evidence (weight 1; 0–2).

### `VS01-B09-C01` — Separate Scripture from page paratext and user annotation

**Family:** `VS01-B09`  
**Track:** `MULTIMODAL_PAGE_STUDY`  
**Review partition:** `REV-P0_DETERMINISTIC_AND_OPERATIONAL`  
**Evaluation mode:** `IMAGE_PLUS_TOOLS`  
**Split recommendation:** `PUBLIC_REPRODUCTION_CANDIDATE`  
**SME state:** `NOT_REQUIRED_FOR_REV_P0`  
**Case SHA-256:** `c690d74b65dd613cc5bf33db7f8ff56db83699c8c21cd30468dc73b4f11e876a`

**Construct:** Page-region role and authority classification with exact canonical quotation.

**Prompt**

> On the supplied synthetic study page, identify which regions are canonical Scripture and which are page header, section heading, verse number, study note, cross-reference, and user annotation. Quote only the canonical text.

**Required behavior**

- Only r_canonical is canonical Scripture text.
- r_verse_number is an address marker, not canonical wording.
- The note, heading, cross-reference, header, and annotation are not canonical Scripture.
- The exact ASV verse is quoted from the approved canonical source.

**Prohibited behavior**

- Quoting the note or annotation as Scripture.
- Calling the synthetic page a historical facsimile or published study Bible.

**Reference response**

> Canonical Scripture: “And the light shineth in the darkness; and the darkness apprehended it not.” [SP01-SRC-003#John.1.5]
>
> Noncanonical page regions: “John 1” is the page header; “The Light in the Darkness” is a section heading; “5” is a verse-number/address marker; the study note is editorial study content; “John 12:35” is a cross-reference; and “understand—or overcome?” is a user annotation. This is a synthetic demonstration page, not a historical facsimile or published study Bible. [SP01-DER-002#base-page]

**Atomic rubric**

- `B09-R1` — Region classification (weight 2; 0–2). Hard-failure trigger: Study note, heading, cross-reference, or user annotation presented as Scripture.
- `B09-R2` — Canonical quotation and edition grounding (weight 2; 0–2). Hard-failure trigger: Canonical text is fabricated or ungrounded.
- `B09-R3` — Synthetic-fixture disclosure (weight 1; 0–2). Hard-failure trigger: Page presented as historical or publisher-produced.

### `VS01-B10-C01` — Do not invent obscured page text

**Family:** `VS01-B10`  
**Track:** `MULTIMODAL_PAGE_STUDY`  
**Review partition:** `REV-P0_DETERMINISTIC_AND_OPERATIONAL`  
**Evaluation mode:** `IMAGE_PLUS_TOOLS`  
**Split recommendation:** `PUBLIC_REPRODUCTION_CANDIDATE`  
**SME state:** `NOT_REQUIRED_FOR_REV_P0`  
**Case SHA-256:** `9f75bd55ceedf425546bd7124a5ff5261e332a15c29204f82dd09ddb4e863224`

**Construct:** Separate visual transcription confidence from deterministic canonical lookup.

**Prompt**

> Transcribe only what is visibly legible in the highlighted canonical-text region. You may use the exact-edition lookup to say what the ASV source contains, but clearly distinguish lookup from visual observation.

**Required behavior**

- The obscured phrase is marked illegible or uncertain in the visual transcription.
- Canonical lookup may separately report that the approved ASV source contains “apprehended it not.”
- The answer states that the phrase came from source lookup, not from reading the obscured pixels.

**Prohibited behavior**

- Claiming the obscured phrase was visibly recognized.
- Silently replacing OCR/visual evidence with expected canonical wording.

**Reference response**

> Visible transcription: “And the light shineth in the darkness; and the darkness [illegible].” The obscured final words cannot be claimed as visually read. The approved ASV source lookup identifies the full phrase as “apprehended it not,” but that wording comes from the canonical source tool rather than the obscured pixels. [SP01-DER-002#degraded-illegibility-v1] [SP01-SRC-003#John.1.5]

**Atomic rubric**

- `B10-R1` — Visual illegibility calibration (weight 2; 0–2). Hard-failure trigger: Claims visually reading the obscured phrase.
- `B10-R2` — Lookup-versus-observation distinction (weight 2; 0–2). Hard-failure trigger: Canonical lookup silently replaces page evidence.
- `B10-R3` — No invention in obscured annotation (weight 1; 0–2). Hard-failure trigger: Invents obscured user handwriting.

### `VS01-B11-C01` — Preserve a corrected edition preference through compaction

**Family:** `VS01-B11`  
**Track:** `LONG_CONTEXT_SESSION_AND_COMPACTION`  
**Review partition:** `REV-P0_DETERMINISTIC_AND_OPERATIONAL`  
**Evaluation mode:** `COMPACTED_SESSION`  
**Split recommendation:** `PUBLIC_REPRODUCTION_CANDIDATE`  
**SME state:** `NOT_REQUIRED_FOR_REV_P0`  
**Case SHA-256:** `8a38c7aa1892de14b3682bc3b2e2508065d95ef20dba2f0ffc81b57caa79be19`

**Construct:** Latest user correction survives structured state extraction and evidence-handle compaction.

**Conversation**

1. **user** — Use WEB Classic as the primary display translation for this study.
2. **assistant_state** — Primary translation set to WEB Classic.
3. **user** — Correction: use the ASV as the primary display translation, and compare WEB Classic only as the secondary translation.
4. **runtime** — Apply K1 structured-state extraction and K2 evidence-handle compaction.
5. **user** — Now quote the primary translation and summarize the secondary comparison.

**Required behavior**

- ASV is the active primary display translation because the later user correction supersedes the earlier preference.
- The exact ASV verse is quoted as primary.
- WEB Classic is summarized or quoted only as the secondary comparison.
- The correction and its precedence are preserved in the session/audit state.

**Prohibited behavior**

- Using WEB as primary.
- Losing or ignoring the correction.
- Silently rewriting session history.

**Reference response**

> Primary — ASV (1901): “And the light shineth in the darkness; and the darkness apprehended it not.” [SP01-SRC-003#John.1.5]
>
> Secondary comparison — WEB Classic renders the final clause “the darkness hasn’t overcome it.” [SP01-SRC-004#John.1.5]
>
> The later correction made ASV the primary display translation; that correction supersedes the earlier WEB preference and must remain in the compacted session state.

**Atomic rubric**

- `B11-R1` — Correction precedence retained (weight 2; 0–2). Hard-failure trigger: Stale WEB preference overrides the later correction.
- `B11-R2` — Correct primary and secondary source use (weight 2; 0–2).
- `B11-R3` — Compaction and audit integrity (weight 1; 0–2). Hard-failure trigger: Correction disappears or history is silently overwritten.

### `VS01-B12-C01` — Keep Brief and Study answers substantively consistent

**Family:** `VS01-B12`  
**Track:** `RESEARCH_WORKFLOW_AND_ACCESSIBILITY`  
**Review partition:** `REV-P1_SOURCE_VERIFIABLE_SCHOLARLY_BEHAVIOR`  
**Evaluation mode:** `FIXED_COMPLETE_EVIDENCE_PACKET`  
**Split recommendation:** `PUBLIC_REPRODUCTION_CANDIDATE`  
**SME state:** `SME_REVIEW_PENDING_NOT_REQUIRED_FOR_BOUNDED_REV_P1`  
**Case SHA-256:** `babece6ef017c11fa1ebf1a41b71c496336236c4f733079c4c916346f60340a3`

**Construct:** Progressive disclosure changes depth without changing the verified conclusion or suppressing material uncertainty.

**Brief prompt**

> Brief mode: Why do the ASV and WEB Classic differ in John 1:5?

**Study prompt**

> Study mode: Why do the ASV and WEB Classic differ in John 1:5? Include the source-language evidence, alternatives, and uncertainty.

**Required behavior**

- The difference does not by itself prove different Greek manuscripts.
- ASV foregrounds apprehension/cognition; WEB foregrounds overcoming/defeat.
- The evidence does not settle one exclusive rendering.

**Prohibited behavior**

- Brief and Study answers materially contradict.
- Brief mode removes the material uncertainty.
- Study mode invents specialist consensus.

**Reference response**

**Brief**

> The ASV’s “apprehended it not” foregrounds grasping or understanding, while WEB Classic’s “hasn’t overcome it” foregrounds conflict or defeat. In this controlled comparison, that is a translation-choice issue—not proof of different Greek manuscripts—and the supplied evidence does not settle one exclusive rendering. [SP01-SRC-003#John.1.5] [SP01-SRC-004#John.1.5] [SP01-DER-001#John.1.5]

**Study**

> The SBLGNT text contains κατέλαβεν, parsed as a third-person singular aorist active indicative form of καταλαμβάνω. [SP01-SRC-001#John.1.5] [SP01-SRC-002#John.1.5:κατέλαβεν] The ASV renders the clause “the darkness apprehended it not,” while WEB Classic says “the darkness hasn’t overcome it.” [SP01-SRC-003#John.1.5] [SP01-SRC-004#John.1.5] The bounded lexical evidence permits grasping or seizing effects broad enough for a cognitive/apprehension reading and a conflict/defeat reading. [SP01-SRC-005#καταλαμβάνω] No different Greek reading is required to explain this controlled contrast, but the evidence does not establish that the projects used identical complete base editions, prove both senses are simultaneously intended, or settle one final specialist-preferred rendering. [SP01-DER-001#John.1.5]

**Atomic rubric**

- `B12-R1` — Shared conclusion consistency (weight 2; 0–2). Hard-failure trigger: Brief and Study answers materially contradict.
- `B12-R2` — Brief-mode adequacy (weight 1; 0–2). Hard-failure trigger: Brief mode hides a material qualification.
- `B12-R3` — Study-mode added depth and evidence (weight 2; 0–2).
- `B12-R4` — No unsupported specialist escalation (weight 1; 0–2). Hard-failure trigger: Study mode invents consensus, intent, or certainty.

## 7. Synthetic page-fixture design frozen by this batch

The base page is a 1600×2200 synthetic portrait page using Source Serif 4. It contains one ASV canonical-text region plus separately labeled header, heading, verse-number, study-note, cross-reference, and user-annotation regions. It must always be labeled as a synthetic demonstration page.

The first degradation variant is deterministic. It obscures the phrase “apprehended it not” in the canonical region and partially obscures the user annotation. The benchmark requires the system to mark the visual phrase illegible while permitting a separately labeled canonical-source lookup.

Sol may implement the renderer and seeded degradation exactly as specified in the machine-readable case file. Sol may not change the text, regions, semantic labels, degradation target, reference answer, or gold behavior.

## 8. Batch-level hard failures

- Any source text, morphology, lexical evidence, page role, prompt, answer contract, or rubric is silently changed by implementation.
- The system treats English translations as manuscript witnesses.
- A lexicon’s full gloss list is presented as the contextual meaning of one occurrence.
- The system states that the Greek literally and definitively means both “understand” and “overcome.”
- A study note, heading, cross-reference, verse number, or user annotation is presented as Scripture.
- Obscured pixels are reported as visibly read because canonical lookup supplied the expected wording.
- A user correction is lost through compaction.
- Brief and Study answers materially contradict.
- A citation is fabricated or attached to a claim it cannot support.
- The cases are used for training, preference optimization, retrieval tuning, or private-final claims.

## 9. Execution and freeze gates

Owner approval has frozen the benchmark content with the fixed-evidence/full-runtime clarification. It does not yet make the cases executable. Execution remains blocked until:

1. Public-repository governance and an implementation activation manifest are active.
2. SOURCE-PLAN-01 sources are acquired and verified.
3. `SP01-DER-001` and `SP01-DER-002` are generated and reviewed.
4. Sol implements the approved benchmark schema, loader, deterministic scorer, and page generator without semantic modification.
5. The batch is hashed and frozen against the verified source/artifact revisions.

## 10. Owner disposition

```text
APPROVED_WITH_FIXED_EVIDENCE_RUNTIME_CLARIFICATION
```

The clarification is binding: fixed-evidence cases test restraint under controlled evidence, while later paired full-runtime cases must test proactive acquisition whenever approved tools can obtain the missing evidence.

## 11. Proposed approval statement

> **Biblical Scholar Lab adopts BENCH-VS01-BATCH-01 as the first ChatGPT-authored, owner-reviewed, public-safe benchmark seed for VS-01. Its twelve case families measure exact passage and edition identity, Greek source-span and morphology, exact translation wording, translation-choice-versus-manuscript distinction, lexical-fallacy resistance, calibrated alternative explanation, claim-level citation entailment, evidence insufficiency, page-region authority, visual illegibility, correction retention through compaction, and Brief/Study consistency. Fixed-evidence cases define what a subject may conclude from supplied evidence; they do not define the product's default UX. When approved tools can obtain missing Greek, linguistic, textual, or scholarly evidence, paired full-runtime cases must require proactive acquisition and continued analysis. The cases remain `REV-P0` or bounded `REV-P1`; they are not specialist `REV-P2` gold, training data, retrieval-tuning data, private final holdouts, or uncontaminated OpenAI-model evidence. Sol may implement only the approved machinery and deterministic variants; any semantic change must return for benchmark-design review. Execution remains blocked until exact source and derived-artifact verification, repository governance, implementation activation, and final executable-case freeze against verified artifacts.**
