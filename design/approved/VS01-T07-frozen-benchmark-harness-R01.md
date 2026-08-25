# VS01-T07-R01 — Frozen VS-01 Benchmark Harness and Execution Protocol

| Field | Value |
|---|---|
| Design ID | `VS01-T07` |
| Status | **CHATGPT FROZEN REVISION R01 — OWNER APPROVAL REQUIRED; IMPLEMENTATION NOT AUTHORIZED** |
| Owner authorization | `APPROVE_VS01_T07_DESIGN` |
| Approval date | 2026-08-24 |
| Repository base | `ffcc2892b2096f8c951fb822c6cf01a5634b6793` |
| Repository tree | `f109f874cdfa8652198ed929f9876ebf9d49f676` |
| Frozen batch | `BENCH-VS01-BATCH-01` |
| Batch JSON SHA-256 | `4241a0bf5baf50a12ce5fe6dcfef6ed5492cde410f3d92f5aad8a9f26ba3113f` |
| Batch Markdown SHA-256 | `f1f0be8a3be9b4f56de0968ad3f166306a4fdfbdd57e7a45a5d972bbb50b66ff` |
| Machine protocol | `VS01-T07-benchmark-execution-protocol-R01.json` |
| Protocol SHA-256 | `bf48cbd15b09673f965e4a6300dbec61aec924f56f026032d8c9ccaaa12014bb` |
| Implementation authority | **None in this design turn** |
| Benchmark execution authority | **None in this design turn** |

## 1. Approved change

Freeze the project-owned execution, isolation, scorer-firewall, deterministic-reference,
scoring, result, publication, and no-go protocol for the twelve already approved
`BENCH-VS01-BATCH-01` cases.

T07 does **not** rewrite the examination. The authoritative prompts, evidence contracts,
answer boundaries, deterministic checks, rubrics, reference responses, case hashes, review
partitions, split recommendations, contamination state, and B08 runtime clarification
remain exactly where they were frozen in:

```text
design/approved/BENCH-VS01-BATCH-01.md
design/approved/BENCH-VS01-BATCH-01-cases.json
```

## 2. Governing rule

> **The benchmark content, subject-visible package, hidden scorer authority, execution
> engine, subject, raw output, scoring pass, result bundle, and promotion decision remain
> separate versioned authorities. No weighted score may override a hard failure, leakage,
> identity defect, omitted case, or missing runtime prerequisite.**

## 3. Exact frozen inventory

```text
Evidence contracts: 7
Cases:               12
Atomic criteria:     37
Criterion weights:   60
Maximum points:      120

REV-P0:
  7 cases
  64 maximum points

REV-P1:
  5 cases
  56 maximum points

REV-P2:
  0 cases
```

The case inventory is:

| Case | Mode | Partition | Max | Screening case minimum | Content SHA-256 |
|---|---|---:|---:|---:|---|
| `VS01-B01-C01` — Resolve and quote John 1:5 from the approved ASV edition | `DETERMINISTIC_TOOLS_ONLY` | `REV-P0` | 6 | 5 | `2c78be090f24fe8bb4c1b10adfbd127053c55e78f39b4a34f91ea77b76e7c311` |
| `VS01-B02-C01` — Identify the Greek target span and morphology | `FIXED_PRIMARY_EVIDENCE` | `REV-P0` | 10 | 8 | `d324b140332ce34ca2c9efa79116c274918cba078c2caf7253bd2887391c65d6` |
| `VS01-B03-C01` — Compare exact ASV and WEB wording without interpretation | `FIXED_PRIMARY_EVIDENCE` | `REV-P0` | 6 | 5 | `e2cb06b09d758e1b653d114544acc0c13789c0b281dd2a0091b8d01970d9cbb1` |
| `VS01-B04-C01` — Reject the false manuscript-variant inference | `FIXED_COMPLETE_EVIDENCE_PACKET` | `REV-P1` | 12 | 10 | `71742fbd96204eb29d89501828c592b347be7de881b9b97924d4f730fe6b4600` |
| `VS01-B05-C01` — Correct illegitimate totality transfer | `FIXED_COMPLETE_EVIDENCE_PACKET` | `REV-P1` | 10 | 8 | `f360ef4636850b47623701f0148cd3ef402851c0bef66ffa186abf0d1c16b811` |
| `VS01-B06-C01` — Explain alternatives without false certainty | `FIXED_COMPLETE_EVIDENCE_PACKET` | `REV-P1` | 14 | 12 | `ca11fca8be3fc20e4653dd8210b85bf0d92821b0552c6bd434058b3242d2e0ee` |
| `VS01-B07-C01` — Attach each claim to evidence that actually supports it | `FIXED_COMPLETE_EVIDENCE_PACKET` | `REV-P0` | 12 | 10 | `d0da41800aa0470b573cfe6b7b1227d7c097bb34e44b70674c86e2d93ea7616a` |
| `VS01-B08-C01` — Qualify when only translations are available | `FIXED_PRIMARY_EVIDENCE` | `REV-P1` | 8 | 7 | `28ebe4b02d19b316e027b2c68dce02114e7a40c1f050bba357a4b8cb43d5529a` |
| `VS01-B09-C01` — Separate Scripture from page paratext and user annotation | `IMAGE_PLUS_TOOLS` | `REV-P0` | 10 | 8 | `395090789236f9e61096be3470987000e320ff784b6231994764bbf3d9ef9367` |
| `VS01-B10-C01` — Do not invent obscured page text | `IMAGE_PLUS_TOOLS` | `REV-P0` | 10 | 8 | `dccf12a80604494847853850d86706da17dce45e4663cedbf6c07a68f2d3fa06` source / `f158ea959695243e18c6fc46661387d17f7fe2268bd479f24db02ef868ac7eab` JCS |
| `VS01-B11-C01` — Preserve a corrected edition preference through compaction | `COMPACTED_SESSION` | `REV-P0` | 10 | 8 | `82e8ed750187ca4d83d8e60510e96684a62f8d011288ca50bee641269a872090` |
| `VS01-B12-C01` — Keep Brief and Study answers substantively consistent | `FIXED_COMPLETE_EVIDENCE_PACKET` | `REV-P1` | 12 | 10 | `370eaa8169bc82c79960654e5b6229f2afe21a9f4c12557500082d80be9eea28` |




## 3A. B10 case-hash compatibility erratum

`BENCH-VS01-BATCH-01-ERRATA-01` is binding.

The approved case file remains byte-preserved at:

```text
4241a0bf5baf50a12ce5fe6dcfef6ed5492cde410f3d92f5aad8a9f26ba3113f
```

For B10, the source-declared legacy identity and the RFC 8785 execution
identity are distinct:

```text
Source-declared compatibility identity:
dccf12a80604494847853850d86706da17dce45e4663cedbf6c07a68f2d3fa06

RFC 8785 execution identity:
f158ea959695243e18c6fc46661387d17f7fe2268bd479f24db02ef868ac7eab
```

The distinction is caused solely by numeric serialization of `18.0`.
No prompt, evidence, degradation, answer, rubric, reference, review, or
benchmark semantic field changes.

T07 validates both identities and uses the RFC 8785 value for every newly
created sample/result identity while retaining the source-declared value for
compatibility with the approved batch.

## 4. Upstream authority

```text
T04 packet identity:
aebcbb50fc8383f2f4f395bc71116563325c1fde237427dc8c1bc8140e8ebe31

T04 packet SHA-256:
9f81621785924161cc4861e2af9f010bd18e822b60199d62a6327eff44ea0409

T05 canonical run:
01a030a1-c3ca-76f6-b4c8-f74392e2cd91

T05 canonical session:
01a030a1-c3cb-72d0-aac0-19da47db369e

T06 fixture identity:
929ddc1c1aeb1e976a70cfbceb238f0ef6a55e8ca1b354a0210463cec50b4d9b

T06 base PNG:
2c0cebc7245eb1032b2b1e4c0ee16e6f74dec47e6a53d8f49c4b9d0a847abbfb

T06 degraded PNG:
cb47073c8e40da01285d90d26ebb7144b34047a2cde8f58e4ba0d1f2cfb67fce

T06 fixture JSON:
c8cfc4eafee6b0a16fc2e0442190782a35e2b03477a619854105d5272f08417f

T06 publication receipt:
01a034c2-d6e4-73f4-91b2-7410e7453783
```

These authorities are read-only. T07 does not create another scholarly packet, runtime
run, page fixture, database row, or archive mutation.

## 5. Subject-visible versus scorer-only evidence

Each case is projected through an explicit whitelist into a
`SubjectCasePackage`. The subject package contains only:

```text
case identity and frozen content hash
exact user-visible prompt, turns, or paired prompts
declared evaluation and answer mode
whitelisted evidence bytes or deterministic tool interface
case-local structured response schema
```

It never contains:

```text
answer contract
deterministic checks
rubric
hard-failure rule
reference response
review or contamination metadata
scorer path or object reference
```

For B09, the subject receives only the committed base PNG and exact ASV lookup. The
T06 fixture JSON, region map, authority labels, and extraction truth remain scorer-only.

For B10, the subject receives only the committed degraded PNG and exact ASV lookup. The
base PNG, degradation mask, underlying obscured wording, fixture JSON, and reference
response remain scorer-only.

Any leakage makes the complete run invalid, regardless of score.

## 6. Deterministic reference subject

The initial subject is:

```text
VS01-T07-REFERENCE-SUBJECT-v1
type: DETERMINISTIC_TOOL_SUITE
model calls: 0
OCR calls: 0
VLM calls: 0
network requests: 0
```

It is an oracle fixture for harness and scorer conformance—not an evaluated capability.
Its exact structured outputs are precompiled from the frozen reference response fields.
During execution, the subject process receives only the subject-visible package and the
precompiled response keyed by case hash; it cannot open the benchmark source or scorer
store.

The required reference result is:

```text
all 12 cases attempted once
all 37 criteria = 2
hard failures = 0
REV-P0 = 64 / 64
REV-P1 = 56 / 56
total = 120 / 120
classification = REFERENCE_CONFORMANT
```

A future `VS01BenchmarkSubjectAdapter` is typed but has no provider, model, prompt,
implementation, or invocation authority under T07.

## 7. Case isolation and replay

Each case receives:

```text
fresh subject instance
fresh temporary directory
no cross-case memory
no mutable shared state
one requested attempt
zero automatic retries
zero semantic rerolls
```

Errors, refusals, timeouts, and malformed outputs remain in the denominator.

B11 is internally multi-turn by design. B12 contains its paired Brief and Study outputs.
Neither exception permits state to cross into another case.

Two complete deterministic runs are required. They must produce identical sample and
run semantics and the same content-addressed result identity. Only receipt UUID,
timestamp, and measured duration may differ.

## 8. Exact scoring

Every criterion uses the frozen scale:

```text
0 = absent, incorrect, or materially unsupported
1 = partially correct but materially incomplete, imprecise, or weakly supported
2 = correct, sufficiently supported, and appropriately qualified
```

```text
criterion points = raw score × frozen weight
case points      = sum of criterion points
batch points     = sum of all twelve case points
```

Hard failures have precedence:

```text
HF-1_CRITICAL → immediate no-go
HF-2_MAJOR    → case failure and batch no-go
HF-3_MATERIAL → case failure and review required
HF-4_MINOR    → retained and reported; does not alone override a gate
```

### Reference implementation gate

```text
64 / 64 REV-P0
56 / 56 REV-P1
120 / 120 total
no hard failure
no leakage
two identical replays
```

Anything less is `REFERENCE_NONCONFORMANT_REPAIR_REQUIRED`.

### Future public-seed screening gate

A later separately authorized subject must:

```text
attempt all cases exactly once
meet every case-specific minimum
have no criterion scored 0
have no HF-1, HF-2, or HF-3
reach at least 58 / 64 REV-P0
reach at least 45 / 56 REV-P1
reach at least 102 / 120 overall
pass B09 and B10
lose no B11 correction
```

The best permitted classification is:

```text
SCREENING_PASS_WITH_EXPLICIT_LIMITATIONS
```

It is only `EL-1_SCREENING` evidence.

## 9. Why this batch cannot promote the runtime or product

Even a perfect 120/120 non-reference result cannot authorize runtime or product
promotion because:

- the cases are ChatGPT-authored public seed content;
- the batch is not private-final or fresh post-freeze evidence;
- it contains no REV-P2 specialist gold;
- it cannot independently examine an OpenAI frontier model without contamination
  qualification;
- `VS01-B08-RUNTIME-C01` remains required but not yet authored or approved.

The fixed B08 case measures restraint under translations-only evidence. It does not
establish that the full runtime proactively acquires available Greek, morphology, and
lexical evidence.

T07 therefore freezes:

```text
product_or_runtime_promotion = PROHIBITED
```

## 10. Public contracts

Exactly four public contracts are frozen:

```text
VS01BenchmarkExecutionSpecification
VS01BenchmarkCaseResult
VS01BenchmarkRunResult
VS01BenchmarkExecutionReceipt
```

Semantic contracts use RFC 8785 and SHA-256. The receipt uses UUIDv7 and an
offset-aware timestamp while also binding the canonical result hash.

## 11. Result publication

A later implementation may dry-run:

```bash
bsl benchmark vs01-batch-01       --subject deterministic-reference       --dry-run
```

A separately authorized publication uses:

```text
objects/sha256/<prefix>/<run-result-sha256>
snapshots/benchmark/vs01-batch-01/reference-conformance.json
manifests/benchmark/vs01-batch-01/reference-conformance/
  benchmark-execution-receipt.json
```

The receipt is linked last. Exact partial states may be recovered only when all bytes
match. Mismatches fail closed. Unrelated `.incoming` entries are preserved and ignored.

## 12. Adversarial controls

T07 requires explicit rejection of:

- changed, missing, duplicated, silently retried, or denominator-dropped cases;
- subject access to scorer authority;
- B08 exposure to Greek or T04 evidence;
- B09 exposure to page ground truth;
- B10 exposure to clean pixels, masks, or hidden text;
- false visual transcription of the blurred phrase;
- lost B11 correction;
- contradictory B12 depth modes;
- fabricated or role-incompatible citations;
- a hard failure hidden by a high aggregate;
- nonzero model, OCR, VLM, network, archive-write, or database-write counts;
- T04, T05, or T06 authority drift;
- mismatched result, snapshot, receipt, or exact stage.

## 13. Complexity budget

```text
Handwritten active target:       1,300 lines
Hard limit:                       1,800 lines
Handwritten production files:       ≤ 6
Public contracts:                    4
New direct dependencies:             0
Migrations:                           0
Task-specific workflows:            ≤ 1
Function logical lines:             ≤ 60
Cyclomatic complexity:              ≤ 10
Nesting:                             ≤ 3
Production class logical lines:    ≤ 250
Production module physical lines:  ≤ 500
```

## 14. Freeze statement

> **VS01-T07 freezes the execution protocol for the twelve existing VS-01 public
> benchmark-seed cases without changing their content. The deterministic reference
> subject, explicit subject/scorer firewall, one-attempt isolation, hard-failure-first
> scoring, exact 120-point rubric, replay identity, result contracts, receipt-last
> publication, and no-go gates are binding. T07 may prove harness conformance and later
> support a limited public screening result. It cannot authorize runtime or product
> promotion until the B08 full-runtime pair and later independent/fresh evidence exist.
> No implementation, benchmark execution, model/OCR/VLM invocation, result publication,
> database mutation, archive modification, or later task is authorized by this design.**
