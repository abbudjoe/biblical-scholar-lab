# VS01-T06-ERRATA-01 — Font Authority and Pinned Renderer Boundary

| Field | Value |
|---|---|
| Erratum ID | `VS01-T06-ERRATA-01` |
| Status | **APPROVED IMPLEMENTATION CLARIFICATION** |
| Applies to | `VS01-T06` and `VS01-T06-PAGE-FIXTURE-SPEC-v1` |
| Design authority | ChatGPT |
| Owner implementation authorization | Joseph Abbud, 2026-08-23 |
| Scholarly-content change | **None** |
| Page-scene change | **None** |

## 1. Correct font-authority source

The frozen T06 design correctly requires the exact Source Serif Regular,
Italic, and OFL object hashes before rendering. Its prose imprecisely
describes those object bindings as directly exposed by T04.

T04 freezes the six upstream source snapshot/content identities, but the
exact object-level Source Serif bindings are retained in the published T03
`John15NormalizationBundle.source_serif` section.

Implementation is therefore authorized to read exactly:

```text
/Volumes/BSL-Archive/BiblicalScholarLab/snapshots/normalization/john-1-5.json

/Volumes/BSL-Archive/BiblicalScholarLab/manifests/normalization/john-1-5/
  normalization-receipt.json
```

solely to validate and extract:

```text
source_serif.regular_font
  relative_path = TTF/SourceSerif4-Regular.ttf

source_serif.italic_font
  relative_path = TTF/SourceSerif4-It.ttf

source_serif.license_object
  relative_path = LICENSE.md
```

Exact T03 authority:

```text
Bundle identity:
9e147d9e218564d744360fd94b794758d1cc3e98e3826380008939eb0c494f32

Bundle canonical SHA-256:
397f7c8908bf8e8533b23eb808ab7c0ede796c95d7b49451fa92f40261ee19d6

Receipt identity:
01a02a37-79f8-7f29-abf7-a2dd9d7161ba

Receipt-file SHA-256:
e4871e859481614da6d4f52e77fa41e35234884b9f5baacad68c4855e2ed6af2
```

This is a narrow object-binding read, not a new scholarly input and not
permission to reparse T03 text, morphology, translations, lexicon content,
or any raw source. The three hashes, byte counts, and archive object paths
are mechanically derived authority values. Sol may not select substitutes.

## 2. Pinned renderer selected by ChatGPT

The exact rendering platform is:

```text
Platform:
linux/amd64

Python image:
python:3.12.13-slim-bookworm@sha256:d50fb7611f86d04a3b0471b46d7557818d88983fc3136726336b2a4c657aa30b

Python:
3.12.13

Pillow:
12.3.0

Pillow source commit:
bb1d8e8ab8d29048624d96e3ee53cecf7c13d13d

Pillow wheel:
pillow-12.3.0-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl

Pillow wheel SHA-256:
78cb2c6865a35ab8ff8b75fd122f6033b92a62c82801110e48ddd6c936a45d91

Pillow wheel URL:
https://files.pythonhosted.org/packages/84/21/a35af28dcc61f37ed850a2d64c65c701321dfbf25085e469d5559360cbbf/pillow-12.3.0-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl
```

The wheel may be downloaded once into ignored local tooling evidence after
exact hash verification. The Docker image may be pulled by exact digest.
No floating image tag, alternate wheel, source build, package resolver, or
fallback platform is permitted.

## 3. Mechanically derived renderer characterization

Before production implementation or page rendering, two fresh containers
from the exact image and wheel must independently report identical:

```text
resolved linux/amd64 child-manifest digest
Docker image ID
Python version
Pillow version
FreeType version
libpng version exposed by Pillow
zlib compile/runtime versions
regular font path/hash/byte count
italic font path/hash/byte count
OFL path/hash/byte count
```

Those values are not implementation choices. They are deterministic
measurements of authorities selected above. Persist them in:

```text
design/approved/VS01-T06-renderer-authority.json
design/approved/VS01-T06-renderer-authority.sha256
```

Production code and rendering may begin only after the two characterizations
agree byte-for-byte and the font bindings validate against the exact T03
bundle and its `SP01-SRC-006` source record.

## 4. Immutable fixture assets, not dynamic production rendering

T06 implementation generates the clean and degraded PNGs in the pinned
renderer, verifies two independent reproductions, and commits the exact
public-safe fixture bytes and realized metadata.

The production `bsl page john-1-5-synthetic-fixture` command verifies and
dry-runs or publishes those committed immutable bytes. It does not rerender
them dynamically and therefore does not require Pillow or Docker as a
project runtime dependency.

The renderer script remains a bounded reproducibility tool. It is not a
generic page engine.

## 5. Dependency and network boundary

```text
New project direct dependencies:
0

Authorized tooling network:
- exact Docker image pull by digest
- exact Pillow wheel download by URL and SHA-256

Authorized source reads:
- published T04 packet and receipt
- published T03 bundle and receipt only for Source Serif bindings
- exact three T03-bound Source Serif archive objects

Unauthorized:
- font download from the public internet
- any other source acquisition or refresh
- OCR, VLM, model, benchmark, or page publication
```

The frozen T06 design and machine specification remain byte-preserved. This
erratum is the only approved reconciliation of the font-authority seam and
renderer realization boundary.
