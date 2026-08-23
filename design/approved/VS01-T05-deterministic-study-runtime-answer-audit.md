# VS01-T05 — Deterministic Study Runtime, Answer Artifact, and Audit Receipt

| Field | Value |
|---|---|
| Design ID | `VS01-T05` |
| Status | **APPROVED — FROZEN DESIGN; IMPLEMENTATION NOT AUTHORIZED** |
| Owner authorization | `APPROVE_VS01_T05_DESIGN` |
| Approval date | 2026-08-22 |
| Repository base | `7db0ff4a1ade89c043a9330b89de90467dba612c` |
| Repository base tree | `7c120218ebd04331a476a374bd3bf3786d0ca5a3` |
| Required input | Published `John15TranslationNuanceEvidencePacket` |
| Packet identity | `aebcbb50fc8383f2f4f395bc71116563325c1fde237427dc8c1bc8140e8ebe31` |
| Packet canonical SHA-256 | `9f81621785924161cc4861e2af9f010bd18e822b60199d62a6327eff44ea0409` |
| Machine-readable runtime spec | `VS01-T05-runtime-spec.json` |
| Runtime-spec SHA-256 | `06e97f36db1071d9085688ceb33dbc66f02dd0349889ab4df4d0fa280801d9e5` |
| Codex implementation authority | **None in this design turn** |
| Runtime execution authority | **None in this design turn** |

## 1. Approved change

Freeze the smallest complete deterministic backend runtime for the John 1:5 vertical slice.

T05 consumes the already published T04 packet and receipt, resolves one exact corrected Study request, builds one deterministic A2 research plan, preserves all packet evidence and claims in typed ledgers, constructs a structured answer candidate, verifies it, renders exact Brief and Study artifacts from the same verified claim ledger, and emits an immutable runtime audit receipt.

T05 is deliberately model-free. It proves the runtime authority boundary before any model adapter, retrieval system, page workflow, benchmark execution, or web interface is introduced.

## 2. Governing rule

> **The runtime may disclose less detail in Brief mode, but it may not change the conclusion, hide material uncertainty, add a claim not present in the published T04 packet, weaken a citation, or turn an interpretive effect into manuscript evidence, translator intent, consensus, or theology.**

The exact flow is:

```text
exact request revision
    → exact packet and receipt validation
    → deterministic classification and A2 plan
    → evidence ledger
    → claim ledger
    → structured answer candidate
    → deterministic verification
    → Brief and Study artifacts
    → audit receipt
    → optional append-only PostgreSQL persistence after separate authorization
```

## 3. Exact input authority

T05 may read only:

```text
/Volumes/BSL-Archive/BiblicalScholarLab/.bsl-archive-root.json
/Volumes/BSL-Archive/BiblicalScholarLab/objects/sha256/9f/9f81621785924161cc4861e2af9f010bd18e822b60199d62a6327eff44ea0409
/Volumes/BSL-Archive/BiblicalScholarLab/snapshots/evidence/john-1-5-translation-nuance.json
/Volumes/BSL-Archive/BiblicalScholarLab/manifests/evidence/john-1-5-translation-nuance/evidence-packet-receipt.json
```

The packet must validate with:

```text
packet identity:
  aebcbb50fc8383f2f4f395bc71116563325c1fde237427dc8c1bc8140e8ebe31

canonical SHA-256:
  9f81621785924161cc4861e2af9f010bd18e822b60199d62a6327eff44ea0409

receipt disposition:
  PUBLISHED

receipt implementation commit:
  7db0ff4a1ade89c043a9330b89de90467dba612c
```

The implementation must read the exact published T04 receipt UUID and receipt-file SHA-256 from the fixed receipt path and bind those literal values into the execution record, answer artifacts, audit receipt, and persisted run row.

The authorization supplied no T04 operational receipt UUID or file hash. The design therefore freezes the exact discovery-and-binding rule rather than inventing values. A changed receipt UUID, receipt hash, packet byte, path, mode, root binding, or publication state blocks the run.

T05 may not read:

```text
T03 normalization paths
source snapshots or manifests
raw source objects
quarantine or source-admission records
```

## 4. Public contract boundary

Exactly four public contracts are frozen.

### `John15StudyRequest`

An immutable request revision containing exact user wording, passage, selected editions, answer depth, language, correction lineage, and a canonical identity.

### `John15StudyExecutionRecord`

One deterministic record containing:

```text
resolved task
classification
research execution plan
runtime state sequence
12-item evidence ledger
16-claim claim ledger
10 citation records
structured answer candidate
verification report
Brief/Study consistency result
```

### `John15StudyAnswerArtifact`

One instance per rendering mode:

```text
BRIEF
STUDY
```

Each binds the request, execution record, exact packet, mode, edition order, visible claims, material uncertainty, citation records, exact rendered Markdown, and content identity.

### `John15RuntimeAuditReceipt`

An operational UUIDv7 receipt binding all exact inputs and outputs, the runtime specification, persistence state, state-machine result, executor identity, tool use, zero model/network use, correction lineage, latency, and cost.

No fifth public contract is authorized.

## 5. Exact request and correction

### Revision 1

```text
Using the World English Bible Classic as the primary translation and the American Standard Version as the comparison, explain why John 1:5 says “the darkness hasn’t overcome it” in WEB Classic but “the darkness apprehended it not” in the ASV. Does this difference require a different Greek manuscript? Give me a Study-mode answer with sources and make the uncertainty clear.
```

Identity:

```text
782f577a42001df95b1f2094b7c44a075102bd3c54ee157e809828853352ec80
```

### User correction

```text
Use the American Standard Version as the primary translation instead; keep the World English Bible Classic as the comparison.
```

Correction identity:

```text
bfd475b96f4e0296396b6e3771767194b9210e841643bc66ab3657e995d0d97d
```

### Active revision 2

```text
Using the American Standard Version as the primary translation and the World English Bible Classic as the comparison, explain why John 1:5 says “the darkness apprehended it not” in the ASV but “the darkness hasn’t overcome it” in WEB Classic. Does this difference require a different Greek manuscript? Give me a Study-mode answer with sources and make the uncertainty clear.
```

Identity:

```text
5b0d413278c3dcf03421989dcec84228a828d13236a232977b448b14bd0b68ef
```

The canonical T05 run uses revision 2.

The correction does not mutate revision 1. It creates a new immutable request revision and, when persistence is later authorized, a new run row that references the superseded run.

## 6. Resolved task and plan

```text
domain:
  BIBLICAL_STUDIES

intent:
  TRANSLATION_NUANCE_DIAGNOSIS

task types:
  TRANSLATION_COMPARISON
  TRANSLATION_NUANCE_DIAGNOSIS
  ORIGINAL_LANGUAGE_ANALYSIS

assurance:
  A2_SCHOLARLY_RESEARCH

execution mode:
  DETERMINISTIC_ONLY

primary edition:
  SP01-SRC-003 ASV

comparison edition:
  SP01-SRC-004 WEB Classic

evidence mode:
  EC-VS01-03-COMPLETE-TNC

answer modes:
  BRIEF + STUDY

model route:
  NONE

model calls:
  0

network requests:
  0

tool calls:
  exactly 1 packet-load operation

repair attempts:
  0
```

The runtime does not run acquisition, normalization, retrieval, context composition, model execution, or generative repair.

## 7. Runtime state sequence

The exact successful sequence is:

```text
RECEIVED
NORMALIZED
CLASSIFIED
IDENTITIES_RESOLVED
PLAN_FROZEN
EVIDENCE_ASSESSED
CANDIDATE_RECEIVED
VERIFYING
RENDERED
AUDITED
COMPLETE
```

`EVIDENCE_ACQUIRING`, `CONTEXT_COMPOSED`, `MODEL_EXECUTING`, and `REPAIRING` are absent for documented deterministic reasons. They are not silently skipped.

## 8. Evidence and claim ledgers

The evidence ledger contains all and only the 12 T04 evidence items. It preserves every source role, selector, rights boundary, and method/limitation record.

The claim ledger contains all and only the 16 T04 claims with their exact propositions and epistemic statuses.

Rendering rules:

```text
Brief-visible claims:
  10

Study-visible claims:
  15

Internal-only input-identity claim:
  CLM-T04-001

Material uncertainty visible in both modes:
  CLM-T04-042
  CLM-T04-043
```

Directly attested claims verify as `VERIFIED`. Strongly supported, plausible, and unknown states verify as `VERIFIED_WITH_QUALIFICATION`; the runtime does not convert them into direct attestation or certainty.

## 9. Exact citation set

The runtime uses ten stable citation records:

```text
CIT-T05-001  ASV canonical realization
CIT-T05-002  WEB Classic canonical realization
CIT-T05-003  controlled SBLGNT clause
CIT-T05-004  MorphGNT target form and morphology
CIT-T05-005  Abbott-Smith sense 1
CIT-T05-006  Abbott-Smith sense 2 and John 1:5 locator
CIT-T05-007  Abbott-Smith mental-action sense outside the target locator
CIT-T05-008  approved Translation Nuance method
CIT-T05-009  SOURCE-PLAN-01 evidence boundary
CIT-T05-010  complete normalized Abbott-Smith entry structure
```

Every answer-block claim must have at least one source-role-compatible cited evidence item through the frozen T04 link graph or an explicit method/qualification relation.

## 10. Exact Brief answer

```markdown
The difference is best explained here as a translation choice around the Greek verb κατέλαβεν, not as a different Greek reading required for this controlled comparison. The ASV says “apprehended it not,” while WEB Classic says “hasn’t overcome it.” [CIT-T05-001] [CIT-T05-002] [CIT-T05-003] [CIT-T05-008]

κατέλαβεν is the third-person singular aorist active indicative of καταλαμβάνω, but that morphology does not by itself choose the contextual English sense. Abbott-Smith explicitly lists John 1:5 under “to overtake,” so the conflict or overtaking effect has stronger direct support in this packet. A cognitive or apprehension effect and possible double resonance remain plausible. [CIT-T05-004] [CIT-T05-006] [CIT-T05-007] [CIT-T05-010]

This evidence does not establish that the two projects used identical complete Greek base editions, does not establish the broader textual-critical state of the verse, and does not establish translator intent, current scholarly consensus, or one final preferred rendering. [CIT-T05-008] [CIT-T05-009]
```

Brief may omit derivation. It may not omit the bounded manuscript statement, the three alternatives, or the two material unknowns.

## 11. Exact Study answer

```markdown
## Direct answer

No different Greek source reading is required to explain this controlled contrast. The strongest bounded assessment is a translation-choice difference associated with lexical construal and interpretive effect, not a demonstrated textual-state difference. [CIT-T05-003] [CIT-T05-008] [CIT-T05-009]

## The two approved renderings

The approved ASV reads, “And the light shineth in the darkness; and the darkness apprehended it not.” The approved WEB Classic reads, “The light shines in the darkness, and the darkness hasn’t overcome it.” The salient final-clause contrast is therefore “apprehended it not” versus “hasn’t overcome it.” [CIT-T05-001] [CIT-T05-002]

## The Greek form

The controlled SBLGNT final clause is “καὶ ἡ σκοτία αὐτὸ οὐ κατέλαβεν.” The target form, κατέλαβεν, comes from καταλαμβάνω and is parsed as third-person singular aorist active indicative. That formal morphology does not by itself establish the contextual English sense, aspectual interpretation, discourse effect, translator intent, or theology. [CIT-T05-003] [CIT-T05-004]

## What the lexical evidence contributes

Abbott-Smith distinguishes a grasping or seizing sense, an overtaking sense, and a separate mental-action “apprehend/comprehend” sense. It explicitly lists John 1:5 under sense 2, “to overtake.” Its mental-action sense is attested elsewhere in the entry and is not directly assigned there to John 1:5. The entry therefore supports a bounded lexical range, but its several senses are context-specific possibilities rather than meanings that become simultaneously active merely because they occur in one lexicon entry. [CIT-T05-005] [CIT-T05-006] [CIT-T05-007] [CIT-T05-010]

## Defensible effects and possibilities

The conflict or defeat effect is strongly supported within this packet: WEB Classic foregrounds darkness failing to overcome the light, and Abbott-Smith places John 1:5 under “to overtake.” A cognitive or apprehension effect remains plausible because the ASV wording can make that construal salient, although Abbott-Smith does not directly assign John 1:5 to its mental-action sense. Possible ambiguity or double resonance also remains plausible, but the packet does not establish that every lexical sense is active or that the Greek “literally means both.” [CIT-T05-001] [CIT-T05-002] [CIT-T05-005] [CIT-T05-006] [CIT-T05-007] [CIT-T05-010]

## What this does and does not say about manuscripts

The English wording difference does not by itself prove that the translations were based on different Greek manuscripts. Within this controlled comparison, no different Greek source reading is required to explain the contrast. Whether the ASV and WEB projects used identical complete Greek base editions is not established, and the broader textual-critical state of John 1:5 remains unknown here because apparatus and witness evidence are absent. [CIT-T05-001] [CIT-T05-002] [CIT-T05-003] [CIT-T05-008] [CIT-T05-009]

## Assessment and limits

The strongest source-verifiable conclusion is therefore a translation-choice contrast associated with lexical construal and interpretive effect, with conflict or overtaking more directly supported in this bounded packet and cognitive or double-resonance readings retained as plausible alternatives. The packet does not establish translator intent, current scholarly consensus, one final contextual sense, one specialist-preferred rendering, or a theological conclusion. [CIT-T05-006] [CIT-T05-007] [CIT-T05-008] [CIT-T05-009]
```

The Study artifact uses the canonical answer architecture:

```text
Direct answer
The two approved renderings
The Greek form
What the lexical evidence contributes
Defensible effects and possibilities
What this does and does not say about manuscripts
Assessment and limits
```

## 12. Verification boundary

The verifier is deterministic and fails closed.

It verifies:

1. Exact T04 packet and receipt bytes, modes, paths, hashes, identities, and `PUBLISHED` state.
2. Exact request revision and correction lineage.
3. Exact A2 deterministic plan.
4. Exact 12-item evidence ledger.
5. Exact 16-claim ledger.
6. Exact quotations, selectors, edition labels, and citation records.
7. Claim/evidence entailment and source-role compatibility.
8. Exact epistemic calibration.
9. Absence of all 17 T04 prohibited inferences.
10. Brief/Study conclusion and uncertainty consistency.
11. Zero model, network, and hidden route use.
12. Exact transactional persistence after later authorization.

An answer is rendered only after the structured candidate verifies.

## 13. Typed future model boundary

T05 may define one private protocol:

```text
ScholarModelAdapter.propose_candidate(request, plan, packet)
```

No implementation, registry, provider dependency, prompt, route, or invocation is authorized.

The T05 deterministic executor must reject a non-null adapter. The audit receipt records:

```text
model route:
  NONE

model invocations:
  0
```

## 14. Minimum PostgreSQL boundary

T05 freezes one PostgreSQL schema, three tables, one reviewed SQL migration, and one direct driver dependency.

```text
schema:
  bsl_runtime

migration:
  migrations/0001_vs01_t05_runtime.sql

reference baseline:
  PostgreSQL 18

ORM:
  none

Alembic:
  not activated in T05

driver:
  psycopg[binary], one exact pinned version selected during implementation
```

The migration is committed but is not applied to a real development database during implementation. Applying it requires separate post-merge owner authorization.

### `bsl_runtime.study_run`

Immutable root row for one request revision and packet-bound deterministic execution.

| Column | Type | Rule |
|---|---|---|
| `run_id` | `uuid` | primary key; application-generated UUIDv7 |
| `session_id` | `uuid` | not null; application-generated UUIDv7 |
| `request_revision` | `integer` | not null; >= 1 |
| `supersedes_run_id` | `uuid` | nullable self foreign key |
| `request_identity` | `char(64)` | not null |
| `run_key_sha256` | `char(64)` | not null unique idempotency key |
| `packet_identity` | `char(64)` | not null; exact aebcbb50fc8383f2f4f395bc71116563325c1fde237427dc8c1bc8140e8ebe31 |
| `packet_sha256` | `char(64)` | not null; exact 9f81621785924161cc4861e2af9f010bd18e822b60199d62a6327eff44ea0409 |
| `packet_receipt_identity` | `uuid` | not null; exact published T04 receipt UUID |
| `packet_receipt_file_sha256` | `char(64)` | not null; exact published T04 receipt file hash |
| `runtime_spec_sha256` | `char(64)` | not null; exact frozen T05 spec |
| `executor_kind` | `text` | not null; DETERMINISTIC_REFERENCE only |
| `created_at` | `timestamptz` | not null |

Constraints:
- unique(session_id, request_revision)
- unique(run_key_sha256)
- SHA-256 format checks
- no UPDATE or DELETE trigger

### `bsl_runtime.runtime_artifact`

Immutable content-addressed request, execution, answer, and audit records.

| Column | Type | Rule |
|---|---|---|
| `artifact_sha256` | `char(64)` | primary key; RFC 8785 JSON hash |
| `run_id` | `uuid` | not null foreign key study_run |
| `artifact_type` | `text` | REQUEST | EXECUTION_RECORD | ANSWER_BRIEF | ANSWER_STUDY | AUDIT_RECEIPT |
| `contract_name` | `text` | not null |
| `artifact_json` | `jsonb` | not null |
| `created_at` | `timestamptz` | not null |

Constraints:
- unique(run_id, artifact_type)
- SHA-256 format check
- no UPDATE or DELETE trigger

### `bsl_runtime.runtime_event`

Append-only hash-chained runtime state transitions.

| Column | Type | Rule |
|---|---|---|
| `event_id` | `uuid` | primary key; application-generated UUIDv7 |
| `run_id` | `uuid` | not null foreign key study_run |
| `stream_sequence` | `smallint` | not null |
| `state` | `text` | exact T05 state vocabulary |
| `artifact_sha256` | `char(64)` | nullable foreign key runtime_artifact |
| `event_json` | `jsonb` | not null |
| `previous_event_sha256` | `char(64)` | nullable for first event |
| `event_sha256` | `char(64)` | not null; canonical envelope hash |
| `created_at` | `timestamptz` | not null |

Constraints:
- unique(run_id, stream_sequence)
- unique(run_id, event_sha256)
- SHA-256 format checks
- no UPDATE or DELETE trigger

### Transaction and idempotency

One live run inserts, in one transaction:

```text
1 study_run
5 runtime_artifact rows
11 runtime_event rows
```

Any failure rolls back everything.

A deterministic `run_key_sha256` makes an exact rerun idempotent. An identical rerun verifies existing rows and returns `VERIFIED_EXISTING`; it does not rewrite them.

A correction creates a new `study_run` revision and a new event chain.

### Append-only rule

All three tables reject `UPDATE` and `DELETE` through one shared trigger function. Ordinary correction is supersession, not mutation.

T05 stores only the fixed public-safe development fixture. RLS is therefore not activated here; it becomes mandatory before any private user session is stored.

No outbox, worker queue, generic event store, ORM, retrieval index, or database service layer is authorized.

## 15. CLI and execution behavior

Frozen command:

```bash
bsl study john-1-5-translation-nuance \
  --archive-root /Volumes/BSL-Archive/BiblicalScholarLab \
  --render both \
  [--dry-run]
```

Live persistence reads `BSL_DATABASE_URL` only as a local deployment coordinate. The DSN may not appear in semantic identities, output, logs, committed config, or the audit receipt.

### Implementation-turn dry run

After the implementation commit, Sol must run the exact command twice with `--dry-run` against the real T04 publication.

Both runs must produce identical deterministic identities and exact Brief/Study Markdown while performing:

```text
archive writes:
  0

database connections or writes:
  0

T03/raw-source reads:
  0

network requests:
  0

model invocations:
  0
```

### Future live run

After merge and separate owner authorization:

1. Apply the one exact SQL migration to the approved local PostgreSQL development database.
2. Verify schema revision and append-only controls.
3. Execute the canonical revision-2 request once.
4. Persist the run transactionally.
5. Verify all rows and event hashes.
6. Stop.

No migration runs automatically on merge or application startup.

## 16. CI and test boundary

A later activation may add one task-specific T05 workflow with an ephemeral PostgreSQL 18 service pinned by exact image digest.

Required tests include:

- Exact T04 object/snapshot/receipt raw-byte validation; wrong hash, mode, path, receipt disposition, packet identity, or implementation commit fails.
- Packet generation reads only the root marker and exact T04 authority trio; T03, raw-source, quarantine, and source-object reads are denied.
- The exact canonical request revision 2 and its request identity validate; any wording, passage, edition, depth, language, correction, or lineage change fails.
- The exact deterministic A2 plan validates and contains one tool call, zero model calls, zero network calls, and zero repairs.
- The evidence ledger contains exactly the 12 packet evidence items with matching roles and selectors.
- The claim ledger contains exactly the 16 packet claims with exact propositions, statuses, qualifications, and rendering states.
- The nine citations match exact packet evidence selectors and excerpts; wrong edition, quote, selector, or source role fails.
- Every answer-block claim/citation relation is compatible with the T04 link graph and method/qualification relations.
- The structured candidate contains only frozen blocks, claims, alternatives, citations, uncertainty, and no extra prose.
- The Brief and Study Markdown renderings match the exact frozen outputs byte-for-byte.
- Brief and Study use the same core conclusion and material uncertainty; removing an unknown or alternative from Brief fails.
- Any T04 prohibited inference, translator-intent statement, textual-variant overclaim, all-glosses claim, aorist overclaim, consensus claim, final-preference claim, or theology fails.
- The deterministic executor rejects a non-null ScholarModelAdapter and records model invocations zero.
- Request, execution record, and answer artifact identities are stable across repeated construction.
- Dry run writes neither PostgreSQL nor the archive and requires no database URL.
- The SQL migration applies to a clean PostgreSQL 18 reference service and produces exactly schema bsl_runtime, three tables, one mutation-rejection trigger function, required triggers, constraints, and indexes.
- UPDATE and DELETE on every T05 table fail; a correction creates a new run and leaves prior rows byte-for-byte unchanged.
- A live fixture run inserts one run, five artifacts, and 11 events atomically; injected failure rolls the entire transaction back.
- An identical live fixture rerun verifies existing rows without mutation; a changed artifact under the same run key fails closed.
- The event stream has exact state order, contiguous sequence, correct previous hashes, and a valid terminal COMPLETE event.
- Two exact real-archive dry runs after the implementation commit produce identical deterministic artifact identities, unchanged T04 authority fingerprint, zero archive writes, zero database writes, zero network, and zero model calls.
- Full regression, schema drift, Ruff, Pyright, branch coverage >= 90%, migration conformance, and all DR-30 gates pass.

## 17. Complexity budget

```text
handwritten active implementation target:
  1,300 substantive changed lines

hard limit:
  1,800

handwritten production files:
  <= 7

public contracts:
  exactly 4

direct dependencies:
  <= 1

migrations:
  exactly 1

new CI workflows:
  <= 1

PostgreSQL schemas:
  1

PostgreSQL tables:
  3

function or method:
  <= 60 logical lines

cyclomatic complexity:
  <= 10

nesting:
  <= 3

production class:
  <= 250 logical lines

production module:
  <= 500 logical lines
```

Frozen design artifacts, generated JSON Schemas, generated migration evidence, activation, and handoffs are reported separately from handwritten active implementation.

## 18. Explicit non-goals

This design authorizes none of the following:

- No Codex implementation or activation in this design turn.
- No runtime answer execution.
- No model invocation or adapter implementation.
- No database creation, migration execution, or persistent row write.
- No T04 packet modification or republication.
- No T03, raw-source, source-acquisition, quarantine, or archive-cleanup operation.
- No synthetic page or page-region work.
- No benchmark execution or benchmark-content change.
- No web UI, FastAPI service, retrieval, embedding, LangGraph, Agents SDK, cloud, Lambda, training, evaluation, or billable action.
- No VS01-T06 or later implementation.

## 19. Status correction for the later activation

The first T05 authority commit must minimally state:

```text
VS01-T04 complete and canonically published
VS01-T05 active under its approved activation
T04 packet is the immutable runtime input
T03 and raw-source reparsing are prohibited
no live T05 migration or runtime execution has occurred
```

No status-only PR is needed.

## 20. Freeze statement

> **VS01-T05 is frozen as a passage-specific, deterministic, model-free Study runtime that consumes only the published T04 packet, produces one exact verified claim ledger and two consistent answer depths, persists immutable runtime records through a three-table append-only PostgreSQL boundary only after separate execution authorization, preserves user corrections as new revisions, and emits an auditable receipt without reparsing upstream evidence or inventing scholarly claims.**
