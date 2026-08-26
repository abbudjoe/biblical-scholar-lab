# VS01-T09 — Read-Only Local Study Workspace and Evidence Inspector

| Field | Value |
|---|---|
| Design ID | `VS01-T09` |
| Specification | `VS01-T09-LOCAL-STUDY-WORKSPACE-v1` |
| Status | **FROZEN CANDIDATE — OWNER APPROVAL REQUIRED; IMPLEMENTATION NOT AUTHORIZED** |
| Owner authorization ID | `APPROVE_VS01_T09_DESIGN_AND_T09A` |
| Candidate date | 2026-08-26 |
| Repository base | `2c074e6d9ba03a3a33a95e9a94f1fc28780a5f69` |
| Repository tree | `ba8027e9e63632109f9c5218ad2f3cd775e568e5` |
| Vertical slice | `VS-01` |
| Primary route | `DETERMINISTIC_LOCAL_ONLY` |
| User-visible mode | `STUDY` |
| Public contract introduced by T09A | `VS01StudyWorkspaceProjection` |
| Implementation ladder | `VS01-T09A` → `VS01-T09B` → `VS01-T09-OP01` |

## 1. Purpose

VS01-T09 introduces the first user-facing local workspace over the completed John 1:5 backend slice.

The workspace does not execute the T08 runtime, invoke a model, acquire sources, or write scholarly state. It reads and verifies the already published T08 reference result and the already published T06 synthetic-page authority, derives one public-safe workspace projection, and presents that projection through an accessible loopback-only web experience.

The bounded user promise is:

> A user can open one local John 1:5 Study workspace, compare the approved ASV and WEB Classic wording, inspect the controlled Greek and morphology, understand the bounded lexical and textual-state assessment, inspect claim/evidence/citation links, examine the synthetic page and its region authority, and inspect the exact deterministic route and publication receipts that support the answer.

This is a read-only UX milestone. It is not a general chat product, a model evaluation, a correction editor, a notes system, or a public release.

## 2. Why T09 is split

T09 is divided into two implementation tasks and one operational acceptance step.

### `VS01-T09A` — canonical workspace projection

T09A adds one strict public contract and one deterministic read-only assembler. It verifies the canonical T08 and T06 publication authority and produces a public-safe workspace projection and generated fixture.

T09A adds no HTTP server, web package, JavaScript dependency, database migration, runtime execution, or archive write.

### `VS01-T09B` — loopback API and accessible web client

T09B adds the first activated HTTP and web surface:

- a same-origin loopback API;
- exact page-asset routes;
- a TypeScript/React/Vite client;
- semantic, keyboard-operable, responsive presentation;
- no component framework, analytics, telemetry, service worker, remote asset, or model route.

### `VS01-T09-OP01` — local browser acceptance

After T09B is reviewed and merged, OP01 starts the loopback server on the owner Mac, loads the real canonical projection, performs browser and accessibility smoke tests, captures screenshots and an accessibility transcript, and stops the server. It performs no canonical mutation.

This split keeps each implementation root turn within DR-30 review budgets and prevents the web stack from defining or obscuring scholarly authority.

## 3. Frozen upstream authority

### Repository

```text
main:
2c074e6d9ba03a3a33a95e9a94f1fc28780a5f69

tree:
ba8027e9e63632109f9c5218ad2f3cd775e568e5
```

### T08 published runtime pair

```text
pair specification:
98c5df4b4906261cd96fa194ecf2035474633bdc9988388886c8b081e1835f51

acquisition run:
3ac851b431e75b14b5d50fcb24a16e6243e19eca1f916d8ed81cb95969c9337e

answer projection:
ce9500860ea1be8c4bf4916a554ce541040a34784633389beddb12f80cc321c3

fixed-case result:
eb3ae952a7cb62911e259350ca847299b95f1661daf98be879c86f646ae1c880

pair result:
f73ffd20f5096f2b465f3bd91bdb093f4d44a1c9fa5f717f6589ea5ae11d9426

pair-result file SHA-256:
04c9b4680a0d612bda05508da65720eb583587ebb83ab6f766ac151f1c656222

publication receipt UUID:
01a03f23-35e7-7ef4-b482-d84dafa77010

receipt canonical SHA-256:
8af561aba1c2d0df41ba58f8bd65f6a93de547b5353e8be7eac2c1ece505fac9

receipt file SHA-256:
1b2498a08e9221ab53dde1c9dea59e021cf1c361356f24b6420e872c96d638b6

implementation commit:
2c074e6d9ba03a3a33a95e9a94f1fc28780a5f69
```

T09 never reruns T08. It verifies the immutable object, stable snapshot, and retained receipt read-only.

### T06 synthetic page

```text
fixture identity:
929ddc1c1aeb1e976a70cfbceb238f0ef6a55e8ca1b354a0210463cec50b4d9b

base PNG SHA-256:
2c0cebc7245eb1032b2b1e4c0ee16e6f74dec47e6a53d8f49c4b9d0a847abbfb

degraded PNG SHA-256:
cb47073c8e40da01285d90d26ebb7144b34047a2cde8f58e4ba0d1f2cfb67fce

fixture JSON SHA-256:
c8cfc4eafee6b0a16fc2e0442190782a35e2b03477a619854105d5272f08417f

publication receipt UUID:
01a034c2-d6e4-73f4-91b2-7410e7453783
```

### Transitive answer authority

The T08 result binds the existing T04/T05 authority. T09 displays those identities but does not directly read T03, raw source objects, or owner PostgreSQL.

```text
T04 packet:
aebcbb50fc8383f2f4f395bc71116563325c1fde237427dc8c1bc8140e8ebe31

T05 execution:
f0697ce01cfa4579223a59042e49de7377d3ec5dee7cca29468bbab3cfba20cc

T05 Study answer:
f18264255ab9117cdd7fa40d9da35c614d31a9bfcabce7a5e95e7b0a040424fd
```

## 4. T09A public projection contract

T09A introduces exactly one registered top-level public contract:

```text
VS01StudyWorkspaceProjection
```

Nested display records remain implementation details of that contract and are not independently registered.

The projection contains:

```text
schema version and contract name
workspace ID and RFC 8785 identity
route and active Study context
exact John 1:5 question
two approved translation realizations
controlled Greek clause and target token
lemma and exact morphology
seven ordered Study blocks
twelve ordered evidence records
fifteen ordered claim records
ten ordered citation records
three accepted alternative IDs
two material UNKNOWN claim IDs
user-visible evidence horizon and limitations
T06 base/degraded page assets and seven region roles
T04/T05/T06/T08 audit and publication bindings
zero model/network/database/raw-source operation disclosure
```

The projection identity is:

```text
SHA-256(
  RFC8785(
    complete projection excluding workspace_identity
  )
)
```

T09A must compile the real projection twice and produce byte-identical canonical JSON.

The projection must not expose:

```text
absolute archive paths
database coordinates
credentials
private local evidence paths
hidden scorer plans
expected model answers
raw source bytes
T03 object paths
operational shell details
```

## 5. Study context and answer authority

The visible active context is fixed for this slice:

```text
passage: John 1:5
Greek edition: SBLGNT
translation A: American Standard Version
translation B: World English Bible Classic
answer depth: STUDY
method: EVIDENCE_FIRST
route: DETERMINISTIC_LOCAL_ONLY
evidence state: SUFFICIENT_WITH_QUALIFICATION
model route: NONE
```

The exact question remains:

> You have only the supplied ASV and WEB Classic wording for John 1:5. Does the Greek mean both “understand” and “overcome,” and is a textual variant involved?

The seven Study blocks remain, in order:

```text
STUDY-DIRECT
STUDY-TEXTS
STUDY-GREEK
STUDY-LEXICON
STUDY-ALTERNATIVES
STUDY-TEXTUAL-STATE
STUDY-ASSESSMENT
```

The interface may progressively disclose technical detail. It may not hide the material textual-state uncertainty or imply that translations are manuscript witnesses.

## 6. Translation comparison

The primary comparison presents exactly:

```text
ASV:
And the light shineth in the darkness; and the darkness apprehended it not.

WEB Classic:
The light shines in the darkness, and the darkness hasn’t overcome it.
```

The focal difference is labeled as a translation-choice and interpretive-effect contrast.

The comparison must not:

- rank one translation as globally best;
- treat wording frequency as manuscript support;
- state that the Greek simply “literally means both”;
- state that no textual variant exists;
- imply that Abbott-Smith alone settles the contextual sense.

On narrow screens the two translations become a linear list without loss of labels or focal-span information.

## 7. Greek, morphology, and lexical evidence

The workspace displays:

```text
καὶ ἡ σκοτία αὐτὸ οὐ κατέλαβεν.

target:
κατέλαβεν

lemma:
καταλαμβάνω

parse:
third-person singular aorist active indicative
```

Morphology is explicitly labeled as formal evidence, not decisive contextual meaning.

The lexical section preserves:

- grasping/seizing range;
- Abbott-Smith sense 2, “to overtake,” with John 1:5;
- mental-action “apprehend/comprehend” elsewhere in the entry;
- the limitation that the mental-action sense is not directly assigned there to John 1:5;
- the prohibition against totality transfer.

## 8. Evidence, claims, and citations

Every consequential citation is keyboard-operable and exposes:

```text
claim
evidence ID
source role
source handle or exact selector
quoted span when display is authorized
epistemic status
required qualification
inspection level
```

T09 does not show one global confidence number.

Material claim statuses are conveyed in text and accessible semantics, not color alone.

The evidence inspector is an inline disclosure or adjacent region. Hover-only citation behavior and inaccessible custom modal behavior are prohibited.

## 9. Page study

The workspace exposes both T06 variants:

```text
BASE
DEGRADED_ILLEGIBILITY
```

It preserves the seven exact region roles:

```text
CANONICAL_TEXT
VERSE_NUMBER
SECTION_HEADING
STUDY_NOTE_OR_FOOTNOTE
CROSS_REFERENCE
USER_ANNOTATION
PAGE_HEADER
```

A visual overlay may reinforce the regions, but a complete ordered region list is mandatory for keyboard, screen-reader, narrow-screen, and low-vision use.

The degraded view must communicate uncertainty and must not substitute expected canonical text for illegible pixels.

No OCR or VLM is invoked in T09.

## 10. Evidence horizon and limitations

The following limitations are visible without opening the audit inspector:

```text
critical apparatus and witness evidence are absent
translation-project source-base documentation is absent
translator documentation is absent
modern specialist scholarship is absent
historical English semantic evidence for ASV “apprehended” is absent
```

The workspace also discloses that:

```text
the reference runtime is deterministic and model-free
the slice covers one passage
the result is not REV-P2 specialist gold
the result is not a broad product-capability claim
```

## 11. T09B local API

The first HTTP boundary is same-origin and loopback-only.

```text
GET /api/v1/vs01/john-1-5/workspace
GET /api/v1/vs01/john-1-5/page/base.png
GET /api/v1/vs01/john-1-5/page/degraded.png
```

No other method or endpoint is activated.

The server command is:

```text
bsl web vs01 --port <loopback-port>
```

The server always binds:

```text
127.0.0.1
```

It does not accept a host override.

The built React client and API are served from the same origin. CORS is not enabled. The server exposes no archive path, database endpoint, shell route, upload endpoint, model endpoint, generic file route, or directory listing.

All API and image responses use exact content types, deterministic ETags, `nosniff`, and a restrictive same-origin content-security policy suitable for the built client.

## 12. T09B web client

The first web client uses the approved TypeScript/React/Vite baseline.

The information architecture is one passage-centered workspace:

```text
skip link
visible route/context bar
question and direct answer
parallel translation comparison
Greek and morphology
lexical evidence
alternatives
textual-state limits
claim/evidence/citation inspector
page study
audit and publication details
```

Visual direction:

```text
clear
quiet
scholarly
approachable
inspectable
user-controlled
```

The client uses:

- native semantic HTML before ARIA;
- local/system font stacks only;
- no remote fonts, scripts, images, or analytics;
- no component library;
- no gradients, gamification, streaks, chat typing simulation, or “thinking” animation;
- visible focus;
- readable line lengths;
- responsive linearization;
- reduced-motion support;
- persistent disclosure state only for the current browser session.

The user-facing text must distinguish Scripture, translation wording, generated explanation, evidence, and audit metadata.

## 13. Accessibility

The target is WCAG 2.2 Level AA for the activated surface.

Required evidence includes:

- landmark and heading order;
- skip link;
- complete keyboard operation;
- visible focus not obscured;
- meaningful accessible names;
- no hover-only information;
- text alternatives for the page images;
- accessible ordered alternative to every overlay;
- status conveyed by text, not color alone;
- 200% zoom without loss of content or operation;
- narrow-screen linearization;
- prefers-reduced-motion behavior;
- automated accessibility checks;
- one owner-Mac VoiceOver smoke transcript during `VS01-T09-OP01`.

Automation supports but does not itself establish full WCAG conformance.

## 14. Runtime and security boundary

T09 is read-only.

At runtime it may read:

```text
canonical T08 result object/snapshot/receipt
published T06 fixture authority
committed T09 schema and built client assets
```

It may not read:

```text
T03
raw source objects
owner PostgreSQL
private vault
provider credentials
model checkpoints
```

It performs:

```text
archive writes: 0
database writes: 0
model calls: 0
OCR calls: 0
VLM calls: 0
external network calls: 0
cloud calls: 0
```

The loopback HTTP exchange is local product traffic and is not an external network or provider route.

## 15. Task ladder

### T09A — workspace projection

Activated output:

- exact design and activation authority;
- one Pydantic public contract;
- one generated Draft 2020-12 schema;
- one registry entry;
- one read-only canonical assembler;
- one deterministic generated projection fixture;
- focused adversarial tests;
- minimal status updates recording T08 publication and T09A activation.

T09A does not add FastAPI, Uvicorn, `web/`, HTTP routes, or JavaScript dependencies.

### T09B — loopback API and client

Activated output:

- FastAPI-compatible project adapter;
- fixed loopback server command;
- three exact GET routes;
- TypeScript/React/Vite client;
- JSON Schema runtime validation and schema-derived TypeScript typing;
- unit, API, browser, responsive, and automated accessibility tests;
- no new scholarly contract or persistence.

### T09-OP01 — real local acceptance

Activated output:

- start/stop local server;
- load the real T09 projection;
- verify exact API and image hashes;
- keyboard flow;
- responsive flow;
- automated accessibility report;
- VoiceOver smoke transcript;
- screenshots;
- zero-mutation receipt.

## 16. T09A implementation budget

```text
new public contracts:                 1
new direct dependencies:              0
database migrations:                  0
HTTP endpoints:                       0
handwritten production files:        <= 3
handwritten production nonblank LOC: <= 500
handwritten tests nonblank LOC:      <= 500
inclusive handwritten hard limit:   <= 1,000
generated schemas/fixture:            reported separately
```

T09A uses no simplicity waiver unless the owner separately approves one after review.

## 17. T09B implementation budget

```text
new public scholarly contracts:       0
new Python runtime dependencies:      <= 2
web runtime direct dependencies:      <= 4
web development direct dependencies: <= 12
database migrations:                  0
HTTP endpoints:                       3
handwritten production files:        <= 18
handwritten substantive changed LOC: target 900–1,400
mandatory split-or-waiver threshold:  > 1,500
```

The approved baseline is:

```text
Python 3.12
FastAPI-compatible adapter
Uvicorn-compatible loopback runner
TypeScript strict
pnpm
React
Vite
Biome
Vitest
Playwright
Ajv or schema-derived validation
```

Exact dependency versions are pinned only after a reviewed compatibility probe during T09B. The probe may not add a component library, router, state-management framework, CSS framework, analytics package, or duplicate schema system.

## 18. Explicit non-goals

T09 does not activate:

- model inference;
- arbitrary questions or passages;
- a chat composer;
- streaming;
- user accounts;
- saved notes;
- interactive correction or correction persistence;
- uploads;
- OCR or VLM;
- source acquisition or refresh;
- textual apparatus or modern scholarship acquisition;
- general search;
- vector retrieval;
- public hosting;
- LAN pairing;
- mobile clients;
- service workers or offline caching;
- telemetry or analytics;
- collaboration preview;
- Brief or Scholarly mode switching;
- T10 or later work.

Those capabilities remain absent rather than stubbed.

## 19. Completion criteria

T09 is complete only when:

1. T09A projection authority is implemented, reviewed, merged, and reproducible from real canonical T08/T06 authority.
2. T09B consumes only the public projection and exact image routes.
3. The real local page passes the frozen semantic and accessibility acceptance checks.
4. The server is loopback-only and performs no mutation.
5. The UI exposes the material evidence horizon and does not overstate T08.
6. No model, OCR, VLM, raw-source, T03, PostgreSQL, external-network, or cloud route is used.
7. ChatGPT reviews exact implementation heads and Joseph approves exact merges.
8. No later task begins automatically.

## 20. Freeze statement

> **VS01-T09 freezes one read-only local John 1:5 Study workspace over the canonically published T08 deterministic runtime result and T06 page fixture. T09A will create one strict public-safe workspace projection without HTTP or new dependencies. T09B will expose that projection through exactly three same-origin loopback GET routes and one accessible TypeScript/React/Vite passage workspace. The interface will present the exact ASV/WEB comparison, controlled Greek and morphology, bounded lexical evidence, seven Study blocks, claim/evidence/citation links, material textual-state uncertainty, page-region authority, and audit identities without invoking or simulating a model. It will target WCAG 2.2 AA, provide linear alternatives to two-dimensional views, disclose the deterministic local route, and perform zero canonical archive writes, database writes, T03/raw-source reads, OCR/VLM/model calls, external network calls, or cloud activity. Interactive corrections, notes, arbitrary questions, public hosting, mobile clients, and later tasks remain unactivated.**
