# VS01-T06 — Synthetic John 1:5 Page Fixture and Region-Grounded Evidence

| Field | Value |
|---|---|
| Design ID | `VS01-T06` |
| Status | **APPROVED — FROZEN DESIGN; IMPLEMENTATION NOT AUTHORIZED** |
| Owner authorization | `APPROVE_VS01_T06_DESIGN` |
| Approval date | 2026-08-23 |
| Repository base | `58f51798b385df9ba0216147e1a4db2864b468aa` |
| Repository tree | `d44a44f1e21232dd9acb515647fc3764071c83b4` |
| Derivative identity | `SP01-DER-002` |
| Machine-readable specification | `VS01-T06-page-fixture-spec.json` |
| Specification SHA-256 | `dd76d124b0ab9c42cb3551e1afd5a9e0326ac402977ae3f4625d9092fd80b285` |
| Scene-spec identity | `ed19a7d564a00da054a26347f750b799e4a2b489412bd47c6159d1ca2097bcea` |
| T04 packet identity | `aebcbb50fc8383f2f4f395bc71116563325c1fde237427dc8c1bc8140e8ebe31` |
| T04 packet SHA-256 | `9f81621785924161cc4861e2af9f010bd18e822b60199d62a6327eff44ea0409` |
| T05 canonical run | `01a030a1-c3ca-76f6-b4c8-f74392e2cd91` |
| Implementation authority | **None in this design turn** |

## 1. Approved change

Freeze the exact public-safe synthetic John 1:5 page fixture required by the `VS01-B09-C01` and `VS01-B10-C01` benchmark families. The fixture consists of one clean page view, one deterministic degraded view, seven exact page regions, explicit functional and authority classes, exact reading order and hierarchy, author-supplied extraction ground truth, and a receipt-last content-addressed publication model.

This task creates no page image. It defines the page scene and the exact rules by which a later separately authorized implementation must render, validate, review, and eventually publish it.

## 2. Governing rule

> **The synthetic raster, authored scene graph, region role, content authority, visual legibility, hidden scorer truth, canonical lookup, user annotation, scholarly interpretation, and later OCR or VLM hypotheses remain separate evidence layers. Ground truth comes from the frozen authored scene—not from recognizing the generated pixels.**

The page is always described as:

```text
Synthetic demonstration page — not a historical facsimile or published study Bible.
```

## 3. Upstream authority

### T04

```text
Packet identity:
aebcbb50fc8383f2f4f395bc71116563325c1fde237427dc8c1bc8140e8ebe31

Canonical SHA-256:
9f81621785924161cc4861e2af9f010bd18e822b60199d62a6327eff44ea0409

Receipt identity:
01a02bbe-bda5-776b-a95e-16bb40d18597

Receipt-file SHA-256:
02272e1ec458a33e449aa93f9508a57d4eaacf3d9dccc48888f3952bbe96dad4
```

T04 supplies the exact ASV wording, the bounded lexical/translation claims used by the project-authored note, rights lineage, and the exact Source Serif dependency bindings. It is read-only and may not be modified or republished.

### T05

```text
Run ID:
01a030a1-c3ca-76f6-b4c8-f74392e2cd91

Session ID:
01a030a1-c3cb-72d0-aac0-19da47db369e

Request revision:
2

Supersedes run:
null

Request identity:
5b0d413278c3dcf03421989dcec84228a828d13236a232977b448b14bd0b68ef

Execution-record identity:
f0697ce01cfa4579223a59042e49de7377d3ec5dee7cca29468bbab3cfba20cc

Brief answer identity:
b97e895bfc640d0020f7146cd88112fd0f6f9ec8669bfab316c8d49688aef2a0

Study answer identity:
f18264255ab9117cdd7fa40d9da35c614d31a9bfcabce7a5e95e7b0a040424fd
```

T05 is a persisted consistency authority. It proves the active revision-2 runtime retained the same bounded scholarly conclusion. It is not a source of page pixels or new page wording, and no T05 row may be changed.

## 4. Exact page canvas and coordinates

```text
Canvas:
1600 × 2200 pixels

Physical page:
8 × 11 inches

Resolution:
200 pixels per inch

Pixel format:
8-bit RGB, sRGB, no alpha

Pixel origin:
top-left

Pixel bounding-box convention:
[x, y, width, height], half-open
```

Every region also carries an exact six-decimal normalized `[x_min, y_min, x_max, y_max]` box derived from the pixel box against the 1600 × 2200 canvas. Normalized values are identity fields, not approximate display hints.

Base and degraded views use the same coordinate spaces and identity transform. No crop, deskew, dewarp, perspective transform, or geometry change occurs.

## 5. Exact public-safe page content

The seven frozen content regions are:

| Region | Text | Benchmark role | Functional class | Authority class | Pixel bbox |
|---|---|---|---|---|---|
| `r_header` | `John 1` | `PAGE_HEADER` | `RUNNING_HEADER` | `EDITORIAL_PARATEXT` | `[120,80,1360,110]` |
| `r_heading` | `The Light in the Darkness` | `SECTION_HEADING` | `SECTION_HEADING` | `EDITORIAL_PARATEXT` | `[120,250,1360,150]` |
| `r_verse_number` | `5` | `VERSE_NUMBER` | `VERSE_NUMBER` | `CANONICAL_ADDRESS_MARKER` | `[120,500,70,90]` |
| `r_canonical` | `And the light shineth in the darkness; and the darkness apprehended it not.` | `CANONICAL_TEXT` | `VERSE_TEXT` | `TRANSLATION_TEXT`; canonical Scripture | `[220,470,1160,280]` |
| `r_note` | exact frozen study note | `STUDY_NOTE_OR_FOOTNOTE` | `STUDY_NOTE` | `STUDY_CONTENT` | `[180,930,1240,320]` |
| `r_crossref` | `Cross-reference: John 12:35` | `CROSS_REFERENCE` | `CROSS_REFERENCE` | `EDITORIAL_PARATEXT` | `[180,1320,620,80]` |
| `r_annotation` | `understand—or overcome?` | `USER_ANNOTATION` | `USER_HANDWRITING` | `USER_ANNOTATION` | `[860,1500,520,150]` |

Only `r_canonical` is canonical Scripture text. `r_verse_number` is an address marker. Every other region is noncanonical page content.

The exact study note is:

> Study note: The verb translated “apprehended” can express grasping or seizing. WEB Classic makes the conflict-oriented effect explicit with “hasn’t overcome it.” This note does not establish one exclusive rendering.

## 6. Exact typography and layout

Source Serif 4 release `4.005R`, commit `2823e993c53fca27c5c8749f529b56a5a7c77b6b`, is the only font family. The static TTF Regular and Italic faces are rendering dependencies, not scholarly evidence. Exact font-object hashes and the renderer container/toolchain are mandatory activation bindings because this design turn cannot access or render the font files.

The machine specification freezes font face and size, color, anchors, draw positions, manual line breaks, line heights, note box, annotation rotation, the header rule, and disabled kerning/ligatures. No runtime line wrapping, system-font fallback, font substitution, dynamic layout, or locale-sensitive shaping is permitted.

## 7. Hierarchy and reading order

```text
g_page
├── r_header
├── r_heading
├── g_scripture
│   ├── r_verse_number
│   └── r_canonical
├── g_paratext
│   ├── r_note
│   └── r_crossref
└── g_annotation
    └── r_annotation → annotates r_canonical
```

The benchmark flat order is exactly:

```text
r_header
r_heading
r_verse_number
r_canonical
r_note
r_crossref
r_annotation
```

Printed reading order excludes the annotation overlay. Physical position, printed reading order, and semantic relation are separately recorded.

## 8. Base page ground truth

`SP01-DER-002#base-page` contains the exact seven regions and all are legible. Ground truth is supplied by the authored scene graph. It is not OCR, VLM, or model output. The canonical region also binds exact ASV lookup evidence and must match it visibly. The benchmark subject receives the raster, not the scorer-only ground-truth records.

## 9. Degraded page ground truth

`SP01-DER-002#degraded-illegibility-v1` is derived from the base page with seed `150105` and exactly two operations:

1. Gaussian-blur the glyph-ink mask for the substring `apprehended it not` in `r_canonical`, with sigma `18.0`.
2. Apply an opaque glare mask to the rightmost `55%` of `r_annotation`.

The page geometry, source strings, region identities, role labels, hierarchy, reading order, and authority classes remain unchanged.

Required degraded visual extraction:

```text
And the light shineth in the darkness; and the darkness [illegible].
```

The exact full ASV phrase may be returned only as a separately labeled deterministic canonical lookup. It may not be described as visually read from the obscured pixels. The degraded user annotation is marked partially illegible; no hidden handwriting may be invented.

## 10. Public contracts

Exactly four public contracts are frozen:

```text
John15SyntheticPageFixture
John15PageRegionGroundTruth
John15PageExtractionGroundTruth
John15SyntheticPagePublicationReceipt
```

The fixture embeds the exact region and extraction records and binds both realized raster objects. Operational UUIDs and timestamps live only in the receipt.

## 11. Raster identity boundary

The page scene identity is frozen now:

```text
ed19a7d564a00da054a26347f750b799e4a2b489412bd47c6159d1ca2097bcea
```

A realized PNG hash cannot honestly be frozen in this turn because page generation is explicitly unauthorized. Before implementation, ChatGPT must freeze the exact renderer image/digest, Pillow/Python/FreeType/libpng/zlib versions, Source Serif object hashes, and PNG encoder settings. Sol has no authority to select them.

After authorization, two clean base renders and two clean degraded renders must be byte-identical. Only then may the realized base PNG hash, degraded PNG hash, fixture identity, and fixture JSON SHA become exact implementation constants subject to ChatGPT visual review.

## 12. PNG contract

```text
PNG truecolor RGB
8-bit channels
no alpha
sRGB
200 PPI via pHYs
allowed chunk order: IHDR, sRGB, pHYs, IDAT, IEND
no timestamp, textual metadata, EXIF, or private identifier chunks
```

The byte identity is SHA-256 of the exact PNG bytes. Metadata JSON remains a separate content-addressed object.

## 13. Rights and display

The canonical text is the public-domain American Standard Version (1901) in the admitted openbibleinfo digital edition. Page paratext and the annotation are project-authored. Source Serif 4 is used under SIL OFL 1.1.

The page may be a public-safe benchmark/demo candidate, but it may never be represented as a historical page, facsimile, commercial publication, publisher-produced study Bible, or reproduction of a real study-Bible layout. Font files are not included in this design package or the public page bundle.

## 14. Receipt-last publication

A later implementation may add:

```text
bsl page john-1-5-synthetic-fixture   --archive-root /Volumes/BSL-Archive/BiblicalScholarLab   [--dry-run]
```

Publication consists of three content-addressed objects—base PNG, degraded PNG, and fixture JSON—one stable fixture snapshot, and a receipt linked last as the commit marker.

Exact partial states are recoverable only when existing bytes match. Mismatches fail closed. Unrelated `.incoming` evidence is preserved and never inspected as page evidence, incorporated, or deleted.

The implementation turn may produce ignored local renders for proof and ChatGPT visual inspection. It may not publish the canonical fixture. Live publication requires a separate owner operational authorization.

## 15. Visual acceptance

ChatGPT must inspect the real pinned renders at 100% and 200% and require no clipping, collisions, missing glyphs, or overflow; exact ASV text; visible authority distinctions; a clean legible base; a truly unreadable degraded final phrase while the prefix remains legible; no invented degraded annotation text; no imitation of a recognizable commercial study Bible; and complete synthetic/rights metadata.

Visual review validates a deterministic authored fixture; it does not create ground truth through OCR or VLM inference.

## 16. Benchmark boundary

T06 materializes only the frozen inputs for:

```text
VS01-B09-C01 — page role and authority classification
VS01-B10-C01 — visible illegibility versus canonical lookup
```

It does not execute the benchmark, implement scoring, expose scorer-only ground truth to the subject, or modify benchmark content.

## 17. Complexity budget

```text
Handwritten active target:       1,250 lines
Hard limit:                       1,750 lines
Handwritten production files:       ≤ 6
Public contracts:                    4
Direct dependencies:                ≤ 1
Migrations:                           0
Task-specific workflows:            ≤ 1
Function logical lines:             ≤ 60
Cyclomatic complexity:              ≤ 10
Nesting:                             ≤ 3
Production class logical lines:    ≤ 250
Production module physical lines:  ≤ 500
```

No generic page-understanding engine, OCR pipeline, multimodal harness, layout model, plugin system, or future-page abstraction is authorized.

## 18. Freeze statement

> **VS01-T06 is frozen as one source-traceable, public-safe, deterministic synthetic John 1:5 page scene with one clean raster view and one fixed degraded-illegibility view. Seven stable regions preserve functional role, content authority, exact geometry, hierarchy, reading order, visible text, and scorer-only ground truth. The design explicitly separates visible pixels, authored ground truth, canonical lookup, paratext, user annotation, and future OCR/VLM hypotheses. The ASV verse, project-authored study material, Source Serif dependency, T04 packet, and persisted T05 run retain exact provenance. Real page ingestion, OCR/VLM ground-truth generation, benchmark execution, archive publication, database mutation, model invocation, and later work remain separately unauthorized.**
