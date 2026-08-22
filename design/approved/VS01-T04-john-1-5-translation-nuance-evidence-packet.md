# VS01-T04 — John 1:5 Translation Nuance Evidence Packet

| Field | Value |
|---|---|
| Design ID | `VS01-T04` |
| Status | **APPROVED — FROZEN DESIGN; IMPLEMENTATION NOT AUTHORIZED** |
| Owner authorization | `APPROVE_VS01_T04_DESIGN` |
| Approval date | 2026-08-22 |
| Base repository commit | `5a558f9ff1049295985da88096d36542283b4e50` |
| Base tree | `b9003b206c740dac2b68b99f5270c8bcd3cb85e9` |
| Required input | Published `John15NormalizationBundle` |
| Input bundle identity | `9e147d9e218564d744360fd94b794758d1cc3e98e3826380008939eb0c494f32` |
| Input canonical SHA-256 | `397f7c8908bf8e8533b23eb808ab7c0ede796c95d7b49451fa92f40261ee19d6` |
| Derivative identity | `SP01-DER-001` |
| Machine-readable claim spec | `VS01-T04-claim-evidence-spec.json` |
| Claim-spec SHA-256 | `48254fb7a8f68bfe6baf09f8fe33781c2dd5bf848a7fd2eb782fbc8da9588936` |
| Implementation authority | **None in this design turn** |

## 1. Approved change

Freeze the exact deterministic scholarly-evidence layer for the John 1:5 ASV/WEB comparison. The later implementation may consume only the published VS01-T03 normalization bundle and its receipt, then produce one content-addressed `John15TranslationNuanceEvidencePacket` and one `John15TranslationNuanceEvidenceReceipt`.

T04 is the evidence layer between normalization and runtime answer generation. It is not an answer generator, a model prompt, a database design, a benchmark run, or a synthetic-page task.

## 2. Governing principle

> **Direct source data, project synthesis, accepted alternatives, unknowns, and prohibited inferences remain separately typed. A packet may explain why two translations can differ without turning translation wording into manuscript evidence, a lexicon into contextual meaning, an interpretive effect into translator intent, or a bounded REV-P1 assessment into scholarly consensus.**

The packet must preserve:

```text
published T03 normalization authority
    → exact comparison frame
    → exact difference unit
    → source-role-compatible evidence items
    → typed claims and claim/evidence links
    → candidate diagnoses and interpretive alternatives
    → explicit evidence sufficiency and withheld evidence
    → review, rights, and public-display boundaries
```

## 3. Exact input authority

The sole scholarly-data input is:

```text
snapshot:
  snapshots/normalization/john-1-5.json

receipt:
  manifests/normalization/john-1-5/normalization-receipt.json

bundle identity:
  9e147d9e218564d744360fd94b794758d1cc3e98e3826380008939eb0c494f32

bundle canonical SHA-256:
  397f7c8908bf8e8533b23eb808ab7c0ede796c95d7b49451fa92f40261ee19d6

T03 implementation commit:
  5a558f9ff1049295985da88096d36542283b4e50
```

The implementation must validate the raw JSON bytes of the T03 bundle and receipt, require receipt disposition `PUBLISHED`, verify the content-addressed object, and bind the exact receipt identity and SHA-256 into the new packet.

**Raw-source reparsing is prohibited.** T04 may not read `snapshots/source`, `manifests/source`, quarantine, or the original source objects to reconstruct evidence already frozen by T03.

## 4. Activated public contracts

A later implementation activation may add exactly two public contracts.

### 4.1 `John15TranslationNuanceEvidencePacket`

A strict frozen deterministic contract with no timestamp, operation UUID, hostname, username, or machine identity in its semantic hash.

Required sections:

```text
input authority
comparison frame
difference unit
evidence items
claims
claim/evidence links
diagnosis matrix
accepted alternatives
evidence sufficiency
review vector
rights projection
public-display constraints
known limitations
prohibited inferences
packet identity
```

`packet_identity` is SHA-256 over RFC 8785 canonical semantic fields excluding `packet_identity` itself.

### 4.2 `John15TranslationNuanceEvidenceReceipt`

An operational contract binding:

```text
UUIDv7 receipt identity
generated-at timestamp
implementation commit
archive root
DRY_RUN_VALIDATED | PUBLISHED | VERIFIED_EXISTING
input bundle identity and SHA-256
input T03 receipt identity and SHA-256
packet identity and canonical SHA-256
fixed publication paths
input-authority fingerprint before and after
published / verified-existing flags
```

The packet and receipt are distinct. Operational timestamps and UUIDs never enter the packet identity.

## 5. Exact comparison frame and difference unit

```text
comparison frame:
  CF-VS01-T04-JOHN-1-5-ASV-WEB-v1

purpose:
  EXPLAIN_TRANSLATION_DIFFERENCE

source reference:
  SP01-SRC-001 SBLGNT controlled Greek wording

target realizations:
  SP01-SRC-003 ASV
  SP01-SRC-004 WEB Classic

actual translation-project source-base status:
  SOURCE_BASE_NOT_ESTABLISHED
```

Canonical difference unit:

```text
TDU-VS01-T04-JOHN-1-5-FINAL-CLAUSE-v1

Greek selector:
  SP01-SRC-001#John.1.5:κατέλαβεν

ASV selector:
  “apprehended it not”

WEB selector:
  “hasn’t overcome it”

scope:
  LEXICAL + SEMANTIC

materiality:
  POTENTIAL_NUANCE_DIFFERENCE
```

Canonical text is included. Footnotes, headings, cross-references, study notes, apparatus evidence, and translator documentation are excluded.

## 6. Frozen source distinctions

The packet must preserve these exact source facts:

1. SBLGNT supplies the controlled Greek wording.
2. MorphGNT supplies the target lemma and morphological form only.
3. ASV supplies the exact phrase “apprehended it not.”
4. WEB Classic supplies the exact phrase “hasn’t overcome it.”
5. Abbott-Smith separates:
   - sense 1: “to lay hold of; seize; appropriate”;
   - sense 2: “to overtake,” explicitly including John 1:5;
   - sense 3: mental action, “to apprehend; comprehend,” illustrated by other passages and **not directly assigned there to John 1:5**.
6. Source Serif has no T04 scholarly-evidence role.

This structure prevents the packet from pretending that Abbott-Smith itself classifies John 1:5 under its mental-action sense.

## 7. Frozen claim ledger

The machine-readable spec freezes **16 claims**, their exact propositions, epistemic statuses, review tiers, qualifications, and evidence links.

The ledger includes:

```text
DIRECTLY_ATTESTED
  exact input identity
  exact Greek wording
  exact morphology
  exact ASV wording
  exact WEB wording
  exact surface contrast
  exact Abbott-Smith sense structure
  exact John 1:5 placement under “to overtake”
  exact separation of the mental-action sense from the target locator

STRONGLY_SUPPORTED
  morphology alone does not settle contextual meaning
  translation wording does not prove different manuscripts
  no different Greek reading is required for this controlled explanation
  all lexicon senses are not simultaneously active by lookup
  strongest bounded diagnosis is translation choice / lexical construal,
  not a demonstrated textual-state difference

UNKNOWN
  identical complete Greek base editions
  broader textual-critical state without apparatus evidence
```

Every claim has one or more explicit `ClaimEvidenceLink` records. The permitted relation vocabulary is:

```text
DIRECTLY_SUPPORTS
SUPPLIES_PRIMARY_EVIDENCE
DEFINES_METHOD
QUALIFIES
LIMITS
NO_SUPPORT
```

Translations may receive `NO_SUPPORT` links for manuscript-attestation claims; this records source-role incompatibility rather than treating absence of support as contradictory evidence.

## 8. Accepted alternatives and calibrated asymmetry

T04 intentionally does not force false equivalence among the alternatives.

### `ALT-T04-COGNITIVE`

```text
effect:
  COGNITIVE_OR_EPISTEMIC_EFFECT

status:
  PLAUSIBLE
```

The ASV wording can make an apprehension or grasping construal salient, including a cognitive reading. But Abbott-Smith does not directly assign John 1:5 to its mental-action sense, historical ASV target-language semantics are not supplied, and translator intent is unknown.

### `ALT-T04-CONFLICT`

```text
effect:
  CONFLICT_OR_DEFEAT_EFFECT

status:
  STRONGLY_SUPPORTED
```

WEB’s “overcome” directly foregrounds conflict/defeat, and Abbott-Smith explicitly places John 1:5 under “to overtake.” This remains an interpretive-effect assessment, not a translator-intent or current-consensus claim.

### `ALT-T04-DOUBLE-RESONANCE`

```text
effect:
  AMBIGUITY_OR_DOUBLE_RESONANCE_POSSIBLE

status:
  PLAUSIBLE
```

More than one apprehension, grasping, overtaking, or defeat resonance may remain relevant. The packet must not say that every sense is active or that the Greek “literally means both.”

## 9. Diagnosis matrix

The packet freezes three bounded diagnosis states:

```text
DIA-T04-LEXICAL-POLYSEMY
  STRONGLY_SUPPORTED
  lexical construal and target realization explain the controlled contrast

DIA-T04-DIFFERENT-SOURCE-READING
  UNSUPPORTED within this packet
  no apparatus, witness, or source-base documentation establishes it

DIA-T04-TRANSLATOR-INTENT
  UNKNOWN
  no translator documentation is admitted
```

`UNSUPPORTED` is packet-scoped. It must not be rendered as “disproved in the broader manuscript tradition.”

## 10. Evidence sufficiency

Overall classification:

```text
SUFFICIENT_WITH_QUALIFICATION
```

The packet can support exact texts, morphology, bounded lexical range, the surface contrast, source-role discipline, a translation-choice explanation that requires no different Greek reading, calibrated alternatives, and lexical-fallacy correction.

It cannot support identical complete base editions, the broader apparatus state, translator intent, historical ASV target-word semantics, one final contextual sense, a specialist-preferred rendering, current consensus, or theology.

Withheld or absent evidence includes:

```text
critical apparatus and witness evidence
modern specialist scholarship
ASV/WEB translation committee documentation
historical English semantic evidence for “apprehended”
broader Johannine context and discourse study
SME adjudication
```

## 11. Review and eligibility vector

```text
review partition:
  REV-P1_SOURCE_VERIFIABLE_SCHOLARLY_BEHAVIOR

design authority:
  CHATGPT_DESIGNED

owner design state:
  OWNER_APPROVED_FROZEN_DESIGN

source state at generation:
  SOURCE_VERIFIED_FROM_PUBLISHED_T03

methodology review:
  CHATGPT_METHODOLOGY_REVIEWED

SME state:
  SME_REVIEW_PENDING_NOT_REQUIRED_FOR_BOUNDED_REV_P1

training eligibility:
  NOT_AUTHORIZED

benchmark role:
  FIXED_EVIDENCE_INPUT_ONLY_REQUIRES_SEPARATE_EXECUTION_AUTHORIZATION

public release:
  PUBLIC_SAFE_CANDIDATE_BOUNDED_EXCERPTS_ONLY_REQUIRES_RELEASE_REVIEW
```

Publication of a packet does not authorize benchmark execution, training, model use, or public release.

## 12. Rights and public-display boundary

The packet is a project-authored derivative under `SP01-DER-001`. It may preserve bounded John 1:5 quotations and short Abbott-Smith sense excerpts with exact source identity and attribution.

Authorized operations for the later bounded packet are:

```text
parse normalized input
create derived packet
exact runtime lookup
bounded quote or display excerpt
private evaluation
```

Not authorized:

```text
full-source redistribution
embedding or vector indexing
continued pretraining
supervised fine-tuning
preference training
benchmark execution without separate approval
```

## 13. Prohibited inferences

The machine spec freezes 17 exact prohibited inferences. They include:

- translation difference proves different manuscripts;
- identical complete Greek base editions;
- no variant exists anywhere;
- “the Greek literally means both”;
- all lexicon senses are simultaneously active;
- Abbott-Smith assigns John 1:5 to sense 3;
- morphology or aorist form settles meaning;
- translator intent;
- final preferred rendering;
- current consensus;
- lexicon lookup settles the verse;
- translation frequency as manuscript evidence;
- theology;
- Source Serif as scholarly evidence;
- model output replacing source evidence.

Any material appearance of one of these in the packet is a hard failure.

## 14. Deterministic implementation boundary

A later activation may implement exactly:

```text
bsl evidence john-1-5-translation-nuance   --archive-root /Volumes/BSL-Archive/BiblicalScholarLab   [--dry-run]
```

It must read only the published T03 object, normalization snapshot, and normalization receipt.

Fixed publication paths:

```text
objects/sha256/<prefix>/<packet-sha256>
snapshots/evidence/john-1-5-translation-nuance.json
manifests/evidence/john-1-5-translation-nuance/evidence-packet-receipt.json
```

Deterministic own-stage path:

```text
.incoming/john-1-5-translation-nuance-<packet-sha256>.evidence-stage
```

Receipt is linked last and is the commit marker. Object-only and object-plus-snapshot interrupted states are recoverable when exact. Mismatched states fail closed. Unrelated `.incoming` evidence is preserved and never incorporated or deleted.

The implementation root turn may run only two real **dry runs** against the canonical archive. Live packet publication requires a later, separate owner operational authorization.

## 15. Required tests

The machine spec freezes the complete test list. Key gates include:

1. Exact T03 bundle/receipt authority and no raw-source access.
2. Exact frame, difference unit, 12 evidence items, 16 claims, links, diagnoses, and three alternatives.
3. Source-role-compatible claim/evidence links and exact locators.
4. Direct versus inferred epistemic-status discipline.
5. Adversarial rejection of textual-variant, base-edition, intent, consensus, lexical-totality, aorist, and theological overclaims.
6. Rejection of a cognitive alternative marked directly attested.
7. Rejection of any statement that Abbott-Smith assigns John 1:5 to sense 3.
8. Stable RFC 8785 packet bytes and identity.
9. Dry-run no-write behavior.
10. Receipt-last fixture publication, recovery, idempotency, and unrelated-stage preservation.
11. Zero network, model, database, retrieval, benchmark, source, or raw-source operation.
12. Two real T03-bundle dry runs with identical packet identity/SHA and unchanged input authority fingerprint.

## 16. Evidence required for later implementation review

A later Sol handoff must include:

```text
exact design/spec/activation/implementation/PR/CI identities
T03 bundle and receipt verification
no-raw-source-access audit
claim/evidence matrix conformance
adversarial semantic mutation tests
two schema hashes and registry verification
two real dry-run identities and hashes
pre/post input-authority fingerprint equality
zero canonical archive writes
zero network/model/source/database/benchmark operations
DR-30 complexity receipt
```

## 17. Budgets

```text
substantive changed-line target:
  950

hard limit:
  1,400

handwritten production files:
  <= 6

new public contracts:
  exactly 2

new dependencies:
  0

migrations:
  0

function/method:
  <= 60 logical lines

complexity:
  <= 10

nesting:
  <= 3

production class:
  <= 250 logical lines

production module:
  <= 500 logical lines
```

No generic TNC engine, evidence framework, workflow system, plugin registry, database layer, retrieval layer, or future-passage generalization is authorized.

## 18. Non-goals

This design authorizes no implementation or execution. It does not authorize:

```text
Codex implementation or activation
live packet generation or publication
raw-source reparsing or acquisition
final user-facing answer generation
LLM inference
synthetic page work
benchmark execution
PostgreSQL or migration
retrieval or embeddings
model adapter
cloud, Lambda, training, evaluation, or billable action
VS01-T05 or later implementation
```

## 19. Freeze statement

> **VS01-T04 is frozen as a deterministic, content-addressed, source-verifiable John 1:5 Translation Nuance evidence packet. It binds the exact published VS01-T03 normalization bundle, preserves the asymmetry of the available lexical evidence, distinguishes source data from project synthesis, carries calibrated alternatives and unknowns, and fails closed against textual-variant, translator-intent, lexical-totality, consensus, and theological overclaims. Implementation and live publication remain separately unauthorized.**
