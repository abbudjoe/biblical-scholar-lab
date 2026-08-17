# SOURCE-PLAN-01 — John 1:5 Vertical-Slice Source Admission Plan

| Field | Value |
|---|---|
| Artifact ID | `SOURCE-PLAN-01` |
| Status | `APPROVED` |
| Approval date | 2026-08-17 |
| Artifact type | Binding source-admission and derivation plan for `VS-01` |
| Project owner | Joseph Abbud |
| Source, product, benchmark, and experiment designer | ChatGPT |
| Independent implementation and evidence reviewer | ChatGPT |
| Depends on | `VS-01`; DR-04, DR-05, DR-07, DR-09, DR-10, DR-14, DR-17, DR-20, DR-21, DR-28, and DR-30 |
| Approval authority | Joseph Abbud |
| Implementation authority | GPT-5.6 Sol may acquire, verify, normalize, and implement only the approved components and operations after this plan is approved and activated |
| Execution authority | GPT-5.6 Luna has no role in source selection or acquisition for `VS-01`; this plan authorizes no cloud execution |
| Legal status | Project governance and rights-risk classification, not legal advice |
| Owner disposition | Approved without amendment on 2026-08-17 |
| Approved change | Freezes the exact external sources, revisions, components, rights lineages, allowed operations, exclusions, derived evidence packet, and synthetic-page inputs required for the John 1:5 vertical slice |

## 1. Governing principle

> **VS-01 will admit only the smallest source set needed to prove one exact, cited, source-aware John 1:5 translation-comparison and page-study workflow. Public availability is not permission; a source-level license is not automatically a component-level authorization; and a use allowed by a license is not activated merely because it is legally possible. Unknown or mixed rights fail closed.**

This plan distinguishes:

```text
source is legally/openly available
    from
source is admitted for one exact project operation
    from
source is activated for model training or public redistribution
```

No source admitted here is authorized for continued pretraining, SFT, preference optimization, embedding generation, vector indexing, or full-corpus redistribution.

## 2. Admission result

### External sources admitted

| ID | Source | Revision rule | VS-01 role | Rights lineage | Disposition |
|---|---|---|---|---|---|
| `SP01-SRC-001` | SBL Greek New Testament | Faithlife commit `c4d241a9c1c479a55b989ba35a4976c1d0b8052c` | Authoritative Greek text for John 1:5 | `L0_OPEN_PERMISSIVE` | `ADMIT_OPEN` |
| `SP01-SRC-002` | MorphGNT: SBLGNT Edition 6.12 | Tag `6.12`, commit `a2afca0e96e367fb2ca113395bae978115942dfb` | Lemma and morphology for John 1:5 | `L1_OPEN_RECIPROCAL` | `ADMIT_OPEN_RECIPROCAL` |
| `SP01-SRC-003` | American Standard Version Bible (1901), openbibleinfo digital edition | Commit `5c83ee265c75b3b1c056435eff622a875f1edc45` | English translation A; canonical verse text | `L0_OPEN_PERMISSIVE` | `ADMIT_PUBLIC_DOMAIN` |
| `SP01-SRC-004` | World English Bible Classic | Official `eng-web_usfm.zip`; acquisition-time SHA-256 required | English translation B; canonical verse text | `L0_OPEN_PERMISSIVE` | `ADMIT_PUBLIC_DOMAIN_SNAPSHOT_REQUIRED` |
| `SP01-SRC-005` | Abbott-Smith Greek Lexicon TEI, release 1.1 | Tag `1.1`, commit `64fd85df2139209abb82261b633fe9dbcf91afc5` | Public-domain lexical evidence for `καταλαμβάνω` | `L0_OPEN_PERMISSIVE` | `ADMIT_PUBLIC_DOMAIN_COMPONENT` |
| `SP01-SRC-006` | Source Serif 4 font software | Release `4.005R`, commit `2823e993c53fca27c5c8749f529b56a5a7c77b6b` | Deterministic synthetic-page rendering | `L0_OPEN_PERMISSIVE_DEPENDENCY` | `ADMIT_OFL_DEPENDENCY` |

### Project-authored derivatives authorized after source verification

| ID | Artifact | Role | Review state at creation | Disposition |
|---|---|---|---|---|
| `SP01-DER-001` | John 1:5 source-verifiable Translation Nuance evidence packet | Runtime and benchmark evidence | `CHATGPT_DESIGNED`, `SOURCE_VERIFIED`, `CHATGPT_METHODOLOGY_REVIEWED`, `OWNER_REVIEW_PENDING`; no SME claim | `AUTHORIZE_AFTER_SOURCE_VERIFICATION` |
| `SP01-DER-002` | Synthetic John 1:5 study-page fixture | Page-role, correction, OCR/VLM, and audit fixture | Deterministic ground truth; semantic note limited to `REV-P1` evidence | `AUTHORIZE_AFTER_SOURCE_VERIFICATION` |

### Explicit hold and exclusion decisions

| Source or component | Decision | Reason |
|---|---|---|
| MACULA Greek integrated files | `HOLD_FOR_LATER_COMPONENT_REVIEW` | The integrated files combine openly licensed MACULA fields with third-party MARBLE/Louw–Nida fields described as used with permission. VS-01 does not need to acquire mixed-rights files; MorphGNT 6.12 cleanly supplies the required lemma and morphology. |
| SBLGNT apparatus directories | `EXCLUDE_FROM_VS01` | VS-01 does not require an apparatus; admitting it would expand rights, parsing, and textual-critical scope unnecessarily. |
| MorphGNT text as an independent Greek edition | `EXCLUDE_AS_TEXT_AUTHORITY` | MorphGNT text columns are alignment aids. `SP01-SRC-001` remains the authoritative Greek text. |
| ASV and WEB footnotes, headings, and paratext | `EXCLUDE_FROM_CANONICAL_TRANSLATION_EVIDENCE` | Only exact verse text is needed. The synthetic page uses project-authored paratext so no historical or translator-note claim is implied. |
| Abbott-Smith scanned PDF | `EXCLUDE` | The repository states that restrictions apply to the PDF. The public-domain TEI is sufficient. |
| Copyrighted modern translations and study-Bible pages | `EXCLUDE` | Not required for the slice and would create avoidable rights and release complexity. |
| User-uploaded page images | `EXCLUDE` | VS-01 uses one public-safe synthetic fixture; no private data is needed. |
| YouVersion, BibleHub, Bible Gateway, search snippets, and similar display sites | `VERIFICATION_ONLY_NOT_SOURCE_ARTIFACTS` | They may corroborate discovery during planning but are not authoritative acquired inputs for VS-01. |
| Any model-generated source text, morphology, lexicon entry, or citation | `EXCLUDE_AS_SOURCE` | Model output cannot replace acquired source evidence. |

## 3. Operation-activation matrix

The table records **what this plan activates**, not the maximum permissions a license might permit.

Legend:

```text
A   activated
C   activated with stated conditions
N   not activated by SOURCE-PLAN-01
D   denied or excluded
```

| Source/artifact | Acquire and retain | Parse/normalize | Exact runtime lookup | Public benchmark excerpt | Synthetic page | Public demo | CPT/SFT/preference | Embedding/vector index | Full-source redistribution |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `SP01-SRC-001` SBLGNT | C | C | A | C | N | C | N | N | N |
| `SP01-SRC-002` MorphGNT | C | C | A | C | N | C | N | N | N |
| `SP01-SRC-003` ASV | C | C | A | C | A | C | N | N | N |
| `SP01-SRC-004` WEB Classic | C | C | A | C | N | C | N | N | N |
| `SP01-SRC-005` Abbott-Smith TEI | C | C | A | C | N | C | N | N | N |
| `SP01-SRC-006` Source Serif | C | N | N | N | A | C | N | N | N |
| `SP01-DER-001` evidence packet | N/A | A | A | C | C | C | N | N | C, bounded project artifact only |
| `SP01-DER-002` synthetic page | N/A | A | A | C | A | C | N | N | C, generated fixture only |

Conditions common to every `C` cell:

- Exact source revision or acquisition snapshot is recorded.
- Raw and normalized hashes are preserved.
- Component-specific attribution and notices are retained.
- Rights and review state are included in every derived record.
- Public output is limited to the bounded John 1:5 slice and its approved fixture.
- No later operation inherits authorization automatically.

## 4. `SP01-SRC-001` — SBL Greek New Testament

### 4.1 Exact identity

```text
Repository: https://github.com/Faithlife/SBLGNT
Commit: c4d241a9c1c479a55b989ba35a4976c1d0b8052c
Version described by repository: v1.2, dated 2023-07-10
Admitted file: data/sblgnt/text/John.txt
Rights-evidence files: README.md and LICENSE
```

### 4.2 Admitted content

Only the exact John 1:5 passage and the minimum adjacent addressing information required to resolve and cite it are normalized for VS-01.

Expected display text, subject to byte verification against the pinned file:

```text
καὶ τὸ φῶς ἐν τῇ σκοτίᾳ φαίνει, καὶ ἡ σκοτία αὐτὸ οὐ κατέλαβεν.
```

The original source bytes remain authoritative. Unicode normalization creates a separately identified view and may not overwrite the source representation.

### 4.3 License and attribution

The repository identifies SBLGNT as CC BY 4.0 and gives copyright to the Society of Biblical Literature and Logos Bible Software.

Required project attribution:

```text
SBL Greek New Testament (SBLGNT), copyright © 2010
Society of Biblical Literature and Logos Bible Software,
licensed CC BY 4.0.
```

Public electronic quotations must retain a source link in the attribution bundle.

### 4.4 Explicit exclusions

- Apparatus data.
- Other books and passages except the minimal source context approved later in the benchmark evidence contract.
- Treating the edition as an extant autograph or universally certain original text.
- Exact quotation without edition identity.
- Training or vector indexing.

### 4.5 Acceptance checks

- Commit exists and matches the approved hash.
- The acquired file hash is recorded.
- John 1:5 resolves exactly once.
- The verse matches the expected grapheme sequence after declared display normalization.
- Source and normalized views remain separately retrievable.
- Attribution appears in public-safe fixture and evidence manifests.

## 5. `SP01-SRC-002` — MorphGNT 6.12

### 5.1 Exact identity

```text
Repository: https://github.com/morphgnt/sblgnt
Release/tag: 6.12
Commit: a2afca0e96e367fb2ca113395bae978115942dfb
DOI: 10.5281/zenodo.376200
Admitted file: 64-Jn-morphgnt.txt
Rights-evidence file: README.md plus the release record
Citation: Tauber, J. K., ed. (2017), MorphGNT: SBLGNT Edition, Version 6.12
```

### 5.2 Admitted fields

Only these fields are admitted for John 1:5:

```text
book/chapter/verse coordinate
part of speech
parsing code
source token used for alignment verification
word with punctuation removed
normalized word
lemma
```

The project adapter may derive explicit person, tense, voice, mood, case, number, gender, and degree fields only by the release-documented parsing-code mapping.

For the target verb, the expected source-verified analysis is:

```text
surface: κατέλαβεν
lemma: καταλαμβάνω
part of speech: verb
person: third
number: singular
tense-form: aorist
voice-form: active
mood-form: indicative
```

This is a morphological-form record. It does not by itself determine English sense, aspectual interpretation, discourse effect, or theology.

### 5.3 License and lineage

The repository states that morphological parsing and lemmatization are CC BY-SA; the project will record the 3.0 license target exposed by the release documentation and preserve the component as `L1_OPEN_RECIPROCAL`.

Required attribution:

```text
Tauber, J. K., ed. (2017). MorphGNT: SBLGNT Edition,
Version 6.12. DOI: 10.5281/zenodo.376200.
Morphological parsing and lemmatization licensed CC BY-SA 3.0.
```

If the acquired release evidence does not unambiguously establish the expected license version, acquisition stops with:

```text
HOLD_LICENSE_VERSION_UNRESOLVED
```

### 5.4 Authority boundary

- `SP01-SRC-001` supplies authoritative Greek wording.
- MorphGNT text fields are used only to align the morphology to that wording.
- A token mismatch blocks normalization rather than silently replacing SBLGNT.
- No syntax, semantic role, gloss, or word-sense field is inferred from this source.
- No whole-New-Testament materialization is activated.

### 5.5 Why MACULA is not admitted in VS-01

MACULA is a valuable later source, but its integrated files include third-party fields whose permissions are not expressed as the project’s own open downstream license. Acquiring the integrated file merely to discard those fields would weaken DR-10’s component-level fail-closed rule. MorphGNT provides the exact lemma and morphology needed for VS-01 without that mixed-rights ingestion.

## 6. `SP01-SRC-003` — American Standard Version

### 6.1 Exact identity

```text
Repository: https://github.com/openbibleinfo/American-Standard-Version-Bible
Commit: 5c83ee265c75b3b1c056435eff622a875f1edc45
Admitted file: usx/43-JHN.usx
Rights-evidence files: README.md and License.html
Edition represented: American Standard Version, 1901, in the named digital USX edition
```

### 6.2 Admitted content

Only John 1:5 canonical verse text is normalized for VS-01.

Expected normalized display wording, subject to exact source verification:

```text
And the light shineth in the darkness; and the darkness apprehended it not.
```

The digital repository states that it aims to provide a high-fidelity public-domain edition and preserves paragraphs and footnotes. Its footnotes contain documented modernization changes; therefore footnotes and paratext are deliberately excluded from VS-01 evidence.

### 6.3 Rights and provenance

The source identifies the work as public domain. The project will still preserve:

```text
American Standard Version (1901)
openbibleinfo high-fidelity digital USX edition
exact repository commit and file hash
```

Public-domain status is not used to erase edition identity or provenance.

## 7. `SP01-SRC-004` — World English Bible Classic

### 7.1 Exact identity

```text
Official source: https://ebible.org/find/details.php?id=eng-web
Official developer package: https://ebible.org/Scriptures/eng-web_usfm.zip
Translation ID: ENGWEB / eng-web
Edition: World English Bible Classic, 2020 stable text
Revision identity: acquisition timestamp + package SHA-256 + per-file hashes
Admitted component: John USFM file and required metadata/license files
```

The official package is a mutable download rather than a Git commit. The bytes acquired after owner approval become the frozen VS-01 source snapshot. A later correction or package update creates a new proposal and snapshot; it cannot silently replace the approved one.

### 7.2 Admitted content

Only John 1:5 canonical verse text is normalized.

Expected normalized display wording, subject to exact package verification:

```text
The light shines in the darkness, and the darkness hasn’t overcome it.
```

Notes and paratext are excluded from the canonical comparison evidence.

### 7.3 Rights and trademark condition

The official source dedicates the translation to the public domain and states that “World English Bible” is a trademark. Exact wording may be identified as World English Bible Classic. A modified derivative may not be presented as the World English Bible.

The project may normalize presentation in a separately identified view, but the exact-source quotation remains available and all substantive changes are labeled project derivatives rather than WEB text.

### 7.4 Acquisition hard gates

- Fetch only from the official eBible package URL.
- Record retrieval date, HTTP metadata, archive hash, archive inventory, and file hashes.
- Reject nested archives or unexpected executable content.
- Verify translation ID and John 1:5 fixture.
- Quarantine any unexpected text or metadata change.
- Never auto-refresh this snapshot.

## 8. `SP01-SRC-005` — Abbott-Smith TEI lexicon

### 8.1 Exact identity

```text
Repository: https://github.com/translatable-exegetical-tools/Abbott-Smith
Release/tag: 1.1
Commit: 64fd85df2139209abb82261b633fe9dbcf91afc5
Admitted file: abbott-smith.tei.xml
Excluded file: manualgreeklexic00abborich.pdf
```

The repository states that the TEI lexicon, including its marked-up version, is public domain, while restrictions apply to the PDF.

### 8.2 Admitted component

Only the entry whose lemma is exactly:

```text
καταλαμβάνω
```

is normalized. The parser must find exactly one intended lexical entry or stop for source review.

The project preserves:

- Exact TEI entry selector.
- Page marker or locator present in the TEI.
- Exact source wording.
- Structural sense divisions.
- Cross-references contained in the entry.
- Public-domain status and source provenance.

### 8.3 Epistemic limits

The lexicon supports possible lexical range. It does not by itself establish:

- The one correct contextual meaning in John 1:5.
- A textual variant.
- Translator intent.
- Current scholarly consensus.
- A theological conclusion.

The evidence packet must never dump every gloss into the answer as though all senses apply simultaneously.

## 9. `SP01-SRC-006` — Source Serif 4

### 9.1 Exact identity

```text
Repository: https://github.com/adobe-fonts/source-serif
Release/tag: 4.005R
Commit: 2823e993c53fca27c5c8749f529b56a5a7c77b6b
Admitted font files: static TTF Regular and Italic faces from the 4.005R release
License: SIL Open Font License 1.1
```

The release’s TTF artifacts are selected rather than CFF2 variable OTFs. Exact asset and file hashes are frozen at acquisition.

### 9.2 Use

The font is used only to render `SP01-DER-002`. It is not a source of scholarly evidence.

The font license and copyright notice remain in the fixture build manifest. The generated PNG and annotation JSON do not become subject to the OFL merely because the font rendered them.

The font binary is not committed to Git or distributed as a user-facing project artifact unless a later release plan explicitly permits and packages the required notice.

## 10. `SP01-DER-001` — source-verifiable evidence packet

### 10.1 Review partition

```text
Review partition: REV-P1_SOURCE_VERIFIABLE_SCHOLARLY_BEHAVIOR
Design author: ChatGPT
Owner status: OWNER_APPROVED_FOR_DESIGN; generated artifact remains subject to source verification and artifact review
SME status: SME_REVIEW_PENDING / not required for bounded P1 use
Training eligibility: NOT_AUTHORIZED
```

The packet is intended to prove epistemic discipline, not to settle the final specialist interpretation of John 1:5.

### 10.2 Required source-linked claims

The packet may contain only claims that survive the acquired-source checks:

1. `SP01-SRC-001` supplies the exact SBLGNT wording of John 1:5.
2. `SP01-SRC-002` identifies `κατέλαβεν` as a third-person singular aorist active indicative form of `καταλαμβάνω`.
3. The ASV digital edition renders the final clause with “apprehended it not.”
4. The WEB Classic snapshot renders the final clause with “hasn’t overcome it.”
5. No different Greek source reading is required to explain this controlled comparison; the case does **not** claim that the two translation projects used the same complete base edition.
6. The lexical evidence permits a family of grasping/apprehending/seizing ideas broad enough to motivate both cognitive and conflict/defeat renderings.
7. The English translations make different interpretive effects salient.
8. The evidence packet does not establish one final specialist-preferred rendering.

### 10.3 Accepted analysis boundary

The packet must preserve at least these possibilities:

```text
COGNITIVE_OR_EPISTEMIC_EFFECT
    darkness did not understand, apprehend, or grasp the light

CONFLICT_OR_DEFEAT_EFFECT
    darkness did not overcome, master, seize, or extinguish the light

AMBIGUITY_OR_DOUBLE_RESONANCE_POSSIBLE
    the source wording may permit more than one effect to remain relevant
```

The packet may report that one translation resolves the wording more explicitly toward one effect, but it may not infer translator intent without translation documentation.

### 10.4 Prohibited claims

- “The Greek literally means both.”
- “All translations agree.”
- “Most translations prove the manuscript reading.”
- “The ASV and WEB used exactly the same Greek edition.”
- “One rendering is definitively correct.”
- “The aorist proves a once-for-all action.”
- “The lexical entry settles the verse.”
- Any claim of current scholarly consensus.
- Any theological conclusion not separately evidenced.

### 10.5 Required packet structure

```text
packet identity and hash
source and rights snapshot IDs
passage and edition identities
exact source and target spans
morphology record
lexical evidence handle
translation realizations
source-textual-state assessment
translation-difference unit
accepted causal/effect alternatives
claim/evidence links
counterevidence or limitations
required uncertainty
public-display constraints
review states
```

## 11. `SP01-DER-002` — synthetic study-page fixture

### 11.1 Purpose

The fixture demonstrates page-role classification and evidence separation without using a copyrighted study Bible, private user image, or historical facsimile.

### 11.2 Source content

```text
Canonical verse text:
    exact SP01-SRC-003 ASV John 1:5

Page header:
    project-authored “John 1”

Section heading:
    project-authored “The Light in the Darkness”

Study note:
    project-authored bounded note pointing to the source-linked
    translation comparison; not represented as canonical text

Cross-reference:
    project-authored “John 12:35”

User annotation:
    project-authored “understand—or overcome?”
```

The fixture must display a visible label in its metadata and public documentation:

```text
Synthetic demonstration page — not a historical facsimile or published study Bible.
```

### 11.3 Required ground-truth regions

```text
CANONICAL_TEXT
VERSE_NUMBER
SECTION_HEADING
STUDY_NOTE_OR_FOOTNOTE
CROSS_REFERENCE
USER_ANNOTATION
PAGE_HEADER
```

### 11.4 Base rendering contract

```text
format: PNG plus canonical JSON annotation record
canvas: fixed portrait dimensions selected in the benchmark blueprint
background: plain high-contrast page
font: pinned Source Serif 4 Regular/Italic TTFs
randomness: none for the base fixture
renderer identity: exact code commit and environment
source selectors: exact ASV verse and project-authored text records
output: pixel hash, region geometry, reading order, authority class, provenance
```

Degraded or randomized variants are not activated by this source plan. They require the later benchmark case-batch specification.

## 12. Acquisition and verification workflow

Sol must implement this exact source workflow after approval:

```text
1. Validate SOURCE-PLAN-01 identity and owner approval.
2. Create one quarantined acquisition attempt per source.
3. Fetch only the approved repository revision, release, package, and files.
4. Preserve rights evidence and retrieval metadata.
5. Scan archive structure and reject unsafe or unexpected content.
6. Compute raw object and aggregate SHA-256 hashes.
7. Validate expected edition, language, file, and John 1:5 fixtures.
8. Create immutable SourceSnapshot and FetchReceipt records.
9. Normalize only the activated passage, morphology fields, lexical entry,
   and translation realizations.
10. Verify cross-source token and reference alignment.
11. Produce attribution, rights, lineage, and public-display manifests.
12. Promote verified source objects atomically to the authoritative archive.
13. Generate SP01-DER-001 and SP01-DER-002 only from promoted inputs.
14. Run source, rights, semantic-boundary, and page-ground-truth tests.
15. Publish one consolidated Sol handoff and stop for ChatGPT review.
```

No source fetch may occur in ordinary unit tests or public CI.

## 13. Required source snapshot fields

Every source snapshot must record at least:

```text
source ID
provider and repository/package identity
exact commit, tag, release, or acquisition-time snapshot
retrieval timestamp
retrieval URL
HTTP/Git metadata
raw archive and file inventory
per-file and aggregate SHA-256
license and rights-evidence snapshots
admitted and excluded components
allowed operations
lineage and storage zone
language, script, work, edition, and passage identity
normalization and extraction code identity
upstream update policy
review state
```

## 14. Attribution bundle

The public-safe attribution bundle must include, as applicable:

```text
SBLGNT copyright and CC BY 4.0 notice
MorphGNT citation, DOI, and CC BY-SA 3.0 notice
ASV edition and public-domain provenance
WEB Classic identity, public-domain statement, and trademark caveat
Abbott-Smith TEI source and public-domain status
Source Serif 4 copyright and OFL 1.1 notice
project-authored evidence-packet and synthetic-fixture provenance
```

Attribution remains attached to exports and benchmark evidence even when the UI uses a compact display.

## 15. Upstream update policy

Every admitted source is frozen.

```text
Git source changes
    → new commit proposal

WEB package changes
    → new package snapshot proposal

license or rights changes
    → quarantine and impact analysis

source correction
    → new immutable revision and affected-case review
```

Sol may detect and report updates. It may not adopt them automatically.

## 16. Hard failures

The source plan fails if any of the following occurs:

- A repository or package revision differs from the approved identity without a new proposal.
- License or rights evidence is absent, conflicting, or materially changed.
- MACULA or any other unapproved mixed-rights dataset enters VS-01.
- MorphGNT fields outside the approved morphology/lemma contract enter normalized data.
- MorphGNT text silently replaces SBLGNT wording.
- The Greek, ASV, or WEB John 1:5 fixture does not match its approved source.
- Footnotes, headings, notes, or annotations are classified as canonical text.
- The Abbott-Smith PDF is acquired or used as the authoritative lexical source.
- Every lexicon gloss is presented as contextual meaning.
- A model-generated source, parse, quotation, or citation is promoted as acquired evidence.
- A public artifact omits required attribution or WEB trademark handling.
- Source content enters training, embeddings, vector indexes, or full-source redistribution under this plan.
- A synthetic page is represented as a historical page or published study Bible.
- A font binary is committed or shared without an approved packaging decision and notice.
- Tests make live network calls.
- An upstream update silently mutates a frozen source snapshot.

## 17. Sol’s implementation discretion

Sol may decide only reversible, design-neutral mechanics such as:

- Module and function decomposition.
- The exact safe Git/HTTP client implementation.
- XML, USX, USFM, and TEI parser libraries within the approved dependency budget.
- Equivalent hash and archive-validation mechanics.
- Local test fixture organization.

Sol may not independently:

- Replace, add, or remove a source.
- Change a revision.
- Admit a field or component.
- Change an operation status.
- Modify the evidence-packet claims or prohibited claims.
- Alter the synthetic page’s semantic roles.
- Choose a different English translation.
- Activate training, embeddings, vector search, or cloud execution.
- Resolve a license ambiguity in favor of use.

A material issue returns:

```text
BLOCKED_REQUIRES_SOURCE_DESIGN_REVIEW
```

## 18. Explicit non-goals

SOURCE-PLAN-01 does not authorize:

- Comprehensive New Testament ingestion.
- MACULA integration.
- Syntax, semantic-role, or referent datasets.
- A critical apparatus.
- Modern copyrighted translations.
- Modern scholarly articles or commentaries.
- Vector retrieval.
- Training or model selection.
- Lambda usage.
- Full-canon context.
- Mobile or desktop model deployment.
- Public release of source corpora.
- `REV-P2` specialist gold.

## 19. Decisions intentionally deferred

- Whether MACULA enters a later, component-separated source plan.
- Whether MorphGNT’s reciprocal lineage is included in a later released benchmark package or represented through a public-safe derived record.
- Additional Greek lexica and grammars.
- The preferred specialist interpretation of John 1:5.
- Degraded synthetic-page variants.
- The exact public benchmark license.
- Any training eligibility for the admitted sources.

## 20. Approval effect

Approval of SOURCE-PLAN-01 authorizes the later implementation-activation manifest to instruct Sol to:

- Build the minimum source registry and acquisition path for these six external sources.
- Acquire and verify only the named components.
- Materialize only John 1:5 and the admitted morphology/lexical records.
- Generate the two approved project derivatives.
- Produce source, rights, attribution, and fixture evidence for review.

This approved plan does **not** authorize acquisition before the public repository governance and relevant implementation activation are active.

## 21. Approval statement

> **Biblical Scholar Lab will admit the SBL Greek New Testament at Faithlife commit `c4d241a9c1c479a55b989ba35a4976c1d0b8052c`, MorphGNT SBLGNT Edition 6.12 at commit `a2afca0e96e367fb2ca113395bae978115942dfb`, the American Standard Version digital USX edition at commit `5c83ee265c75b3b1c056435eff622a875f1edc45`, one acquisition-frozen official World English Bible Classic USFM package, the public-domain Abbott-Smith TEI release 1.1 at commit `64fd85df2139209abb82261b633fe9dbcf91afc5`, and Source Serif 4 release 4.005R at commit `2823e993c53fca27c5c8749f529b56a5a7c77b6b` solely for the bounded John 1:5 vertical slice. Only the exact Greek passage, MorphGNT lemma and morphology, two English verse realizations, one public-domain lexical entry, font files needed for deterministic rendering, one project-authored source-verifiable evidence packet, and one synthetic study-page fixture will be materialized. MACULA integrated files, apparatuses, copyrighted translations, historical or commercial study-Bible pages, user images, full-corpus indexing, embeddings, training, and source redistribution remain excluded. Every acquired and derived object will retain exact revision, hash, rights, lineage, source selector, attribution, review state, and operation authorization, while source changes and ambiguities fail closed and require a new owner-approved source design.**

## 22. Source-verification references

The source plan was prepared from official provider pages and repositories current on 2026-08-17:

- Faithlife SBLGNT repository and pinned commit: `https://github.com/Faithlife/SBLGNT`
- MorphGNT SBLGNT release 6.12 and DOI record: `https://github.com/morphgnt/sblgnt/releases/tag/6.12`; `https://doi.org/10.5281/zenodo.376200`
- American Standard Version digital repository: `https://github.com/openbibleinfo/American-Standard-Version-Bible`
- World English Bible Classic official detail and developer package pages: `https://ebible.org/find/details.php?id=eng-web`
- Abbott-Smith TEI repository and release 1.1: `https://github.com/translatable-exegetical-tools/Abbott-Smith/releases/tag/1.1`
- Source Serif release 4.005R and OFL file: `https://github.com/adobe-fonts/source-serif/releases/tag/4.005R`
