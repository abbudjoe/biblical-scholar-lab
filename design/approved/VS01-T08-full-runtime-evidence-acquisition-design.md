# VS01-T08 — Full-Runtime Evidence Acquisition Pair and Runtime Screening

| Field | Value |
|---|---|
| Design ID | `VS01-T08` |
| Specification | `VS01-T08-FULL-RUNTIME-PAIR-v1` |
| Pair | `BENCH-VS01-B08-PAIR-01` |
| Status | **APPROVED — FROZEN DESIGN; IMPLEMENTATION NOT AUTHORIZED** |
| Owner authorization | `APPROVE_VS01_T08_DESIGN` |
| Approval date | 2026-08-25 |
| Repository base | `daa282e1b8a58ccaef117bec386d2a09e2edb4e9` |
| Repository tree | `cb67f28438507cdf5fa0bb6632f150db0e8dbd49` |
| Runtime case | `VS01-B08-RUNTIME-C01` |
| Runtime case SHA-256 | `a1fdd253614df0ca7789a44372dabb895dcfda042656104ab68c9c6b351c17dd` |
| Specification identity | `98c5df4b4906261cd96fa194ecf2035474633bdc9988388886c8b081e1835f51` |

## 1. Exact paired question

Both conditions use the same prompt, byte-for-byte:

> You have only the supplied ASV and WEB Classic wording for John 1:5. Does the Greek mean both “understand” and “overcome,” and is a textual variant involved?

The pair changes only evidence availability:

| Condition | Initial evidence | Acquisition available | Correct behavior |
|---|---|---:|---|
| `VS01-B08-C01` | ASV + WEB Classic | no | qualify, abstain, and request the missing evidence |
| `VS01-B08-RUNTIME-C01` | ASV + WEB Classic | yes | record insufficiency, acquire the approved evidence, then answer with qualification |

The fixed case remains byte-preserved at
`28ebe4b02d19b316e027b2c68dce02114e7a40c1f050bba357a4b8cb43d5529a`.
Its published T07 reference outcome remains `8/8`. T08 neither edits nor
republishes that case.

## 2. Initial subject-visible state

The runtime subject initially receives only:

```text
ASV John 1:5
WEB Classic John 1:5
the exact user prompt
seven deterministic tool schemas
case-local output and budget contracts
```

It does not initially receive Greek, morphology, lexicon content, the T04
claim graph, the T05 answer, rubric, reference plan, expected tool order,
or scorer authority.

The required first conclusion is:

```text
INSUFFICIENT_FOR_REQUESTED_GREEK_AND_TEXTUAL_CRITICAL_CLAIMS
```

The translations establish their English wording difference. They do not
establish Greek lexical range, morphology, whether both effects are active,
or textual-variant status.

## 3. Exact acquisition plan

The reference runtime performs seven calls, once each and in this order:

1. `assess_evidence_sufficiency`
2. `load_published_t04_packet`
3. `select_sblgnt_exact_source_view`
4. `select_morphgnt_target_token`
5. `select_abbott_smith_entry_projection`
6. `select_t04_translation_nuance_projection`
7. `verify_complete_tnc_evidence_contract`

This is logical evidence acquisition over the already published T04
packet. It is not source acquisition or refresh. There is one packet load,
no raw-source read, no T03 read, no network request, and no model call.

The final evidence ledger contains exactly 12 T04 evidence records, and
the answer claim ledger contains exactly 15 T04 claims.

## 4. Evidence that becomes available

```text
SBLGNT:
  καὶ ἡ σκοτία αὐτὸ οὐ κατέλαβεν.

MorphGNT:
  κατέλαβεν
  lemma καταλαμβάνω
  third-person singular aorist active indicative

Abbott-Smith:
  grasping/seizing range
  sense 2 “to overtake,” with John 1:5 locator
  mental-action “apprehend/comprehend” elsewhere, not assigned there to John 1:5

T04 projection:
  claim/evidence links
  method boundaries
  accepted alternatives
  known limitations and prohibited inferences
```

Critical apparatus and witness evidence remain unavailable. The final
sufficiency state is therefore `SUFFICIENT_WITH_QUALIFICATION`, not
unqualified completeness.

## 5. Exact runtime answer authority

The answer uses the seven structured Study blocks already frozen by T05:

```text
STUDY-DIRECT
STUDY-TEXTS
STUDY-GREEK
STUDY-LEXICON
STUDY-ALTERNATIVES
STUDY-TEXTUAL-STATE
STUDY-ASSESSMENT
```

Content authority:

```text
T05 execution record:
f0697ce01cfa4579223a59042e49de7377d3ec5dee7cca29468bbab3cfba20cc

T05 Study answer:
f18264255ab9117cdd7fa40d9da35c614d31a9bfcabce7a5e95e7b0a040424fd

T05 Study Markdown SHA-256:
aa32440433e71db2c74c24b2b43ec6f5ba077a15b5231517f5750eafb27b0cc6
```

The answer must say that no different Greek source reading is required to
explain this controlled contrast. It must not say that no variant exists.
The complete base editions and broader textual-critical state remain
unknown because apparatus, witness, and project-source documentation are
absent.

## 6. Runtime state and audit

The state sequence contains 15 exact states and activates the state T05
previously skipped:

```text
EVIDENCE_ACQUIRING
```

The audit contains 17 exact events from `RUN_RECEIVED` through
`RUN_COMPLETE`. The event chain is content-addressed. Operational
timestamps are excluded from semantic identities.

An answer candidate cannot be bound before:

```text
EVIDENCE_SUFFICIENCY_REASSESSED
```

## 7. Correction behavior

A correction creates a new immutable request revision and run. It never
overwrites the prior request, plan, evidence ledger, answer, or audit.

Evidence whose source and selector remain valid may be re-bound into the
new run, but the old answer cannot be reused silently. Sufficiency,
planning, verification, and rendering must run again under the corrected
request.

The reference B08 runtime case itself contains no correction event.

## 8. Scoring

The fixed case contributes `8` points. The runtime case contributes `28`
points across eight criteria. The pair maximum is `36`.

Reference conformance requires:

```text
fixed case:   8 / 8
runtime case: 28 / 28
pair:         36 / 36
exact tool calls: 7 / 7
exact events: 17 / 17
hard failures: 0
leakage incidents: 0
two replay identities equal
```

A later separately authorized subject may receive at most:

```text
RUNTIME_SCREENING_PASS_WITH_EXPLICIT_LIMITATIONS
```

That gate requires at least `7/8`, `24/28`, and `32/36`, with no criterion
at zero, no HF-1/HF-2/HF-3, no early answer, no hidden evidence, and no
missing tool call.

## 9. What this can and cannot prove

T08 can prove that the deterministic runtime:

- distinguishes unavailable evidence from available evidence;
- freezes and executes the approved acquisition plan;
- preserves provenance and hidden-evidence boundaries;
- produces the existing bounded source-verified Study content;
- records a reproducible event and audit chain.

T08 does not prove autonomous model tool selection, model scholarly
capability, specialist validation, or product readiness. The reference
runtime is deterministic and model-free.

## 10. Four public contracts

```text
VS01B08RuntimePairSpecification
VS01RuntimeAcquisitionRun
VS01B08RuntimePairResult
VS01RuntimeScreeningReceipt
```

Tool calls, evidence-ledger records, claim-ledger records, answer
projections, and audit events are strict nested records inside the
acquisition-run contract.

## 11. Receipt-last publication

A later separately authorized live run may publish:

```text
objects/sha256/<prefix>/<pair-result-sha256>

snapshots/benchmark/
  vs01-b08-runtime-pair/reference-screening.json

manifests/benchmark/vs01-b08-runtime-pair/reference-screening/
  runtime-screening-receipt.json
```

The receipt is linked last. All retained authority is mode `0444`.
Exact partial states are recoverable only when bytes match; mismatches fail
closed; unrelated `.incoming` entries are preserved.

## 12. Complexity budget

```text
Handwritten active target:       1,500 lines
Hard limit:                       2,200 lines
Handwritten production files:       ≤ 7
Public contracts:                    4
Direct dependencies:                 0
Migrations:                           0
Task-specific workflows:            ≤ 1
Function logical lines:             ≤ 60
Cyclomatic complexity:              ≤ 10
Nesting:                             ≤ 3
Production class logical lines:    ≤ 250
Production module physical lines:  ≤ 500
```

## 13. Freeze statement

> **VS01-T08 freezes one exact paired experiment: the existing translations-only
> B08 case must abstain because acquisition is unavailable, while the new
> full-runtime B08 case must recognize the same initial insufficiency, acquire
> the approved T04-bound Greek, morphology, lexical, and claim-graph evidence
> through seven deterministic audited calls, and render the bounded T05 Study
> content with retained uncertainty. No model, raw source, network, database
> mutation, archive publication, benchmark execution, UI, or later task is
> authorized by this design.**
