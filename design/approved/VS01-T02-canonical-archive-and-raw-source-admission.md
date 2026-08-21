# VS01-T02 — Canonical Archive Bootstrap and Raw Source Admission

| Field | Value |
|---|---|
| Design ID | `VS01-T02` |
| Status | `APPROVED` |
| Parent | `VS-01` and `SOURCE-PLAN-01` |
| Approved archive profile | `ARCHIVE-PROFILE-BSL-ARCHIVE-v1` |
| Profile receipt SHA-256 | `6c3baa9f428bbe55b0062a06af214a1892510375edcb82f47748e5fc5ff8da0c` |
| APFS snapshot SHA-256 | `5cbef8cee7f9f180afc941380eb2bbfc5d053026ce94444ea513da5360818870` |
| Current implementation base | `a0f7e76e99f63c0bdd0229a995733ebbe2e6bf7a` |
| Canonical root | `/Volumes/BSL-Archive/BiblicalScholarLab` |
| Designer and exact-head reviewer | ChatGPT |
| Project owner | Joseph Abbud |
| Implementation authority | GPT-5.6 Sol after a separately approved activation |
| Cloud / model / training authority | None |

## 1. Purpose

VS01-T02 creates the canonical retained archive boundary and admits the six raw sources frozen by `SOURCE-PLAN-01`. It ends when:

1. the approved `BSL-Archive` profile has one initialized project root;
2. archive objects, manifests, snapshots, quarantine, and incident paths are active;
3. each of the six sources has one immutable `FetchReceipt` and `SourceSnapshot`;
4. every admitted raw byte is content-addressed and rights-bound; and
5. no normalization, evidence-packet generation, page rendering, benchmark execution, retrieval, or model work has begun.

## 2. Why T02 is split

Code is reviewed before it is allowed to write the canonical archive or contact a source. The stage is therefore four bounded turns:

```text
T02A-IMP  Archive bootstrap kernel, synthetic fixtures only
    ↓ merge
T02A-EXEC Initialize the approved archive root and publish one canary
    ↘
      T02B-IMP Source-admission kernel, synthetic transport fixtures only
          ↓ merge
T02B-EXEC Acquire and admit the six sources sequentially
```

After T02A-IMP merges, T02A-EXEC and T02B-IMP may run in parallel. T02B-EXEC waits for both to finish successfully.

## 3. Canonical root and initial layout

The dedicated volume is not used as an ordinary mutable working directory. The project root is:

```text
/Volumes/BSL-Archive/BiblicalScholarLab
```

T02A creates only the currently activated layout:

```text
BiblicalScholarLab/
    .bsl-archive-root.json
    registry/
        archive-initialization/
    objects/
        sha256/<first-two>/<full-hash>
    manifests/
        archive/
        source/
    snapshots/
        source/
    quarantine/
    incidents/
    .incoming/
```

Later tasks may add checkpoints, results, database backups, public projections, or other DR-28 paths only when activated.

## 4. Approved profile authority

The public-safe profile manifest records only the two approved private-evidence hashes and non-identifying requirements. It contains no live device identifier, stable volume UUID, stable physical UUID, username, hostname, serial, passphrase, or raw plist.

Every authoritative operation must:

1. verify the private receipt hash equals `6c3baa9f428bbe55b0062a06af214a1892510375edcb82f47748e5fc5ff8da0c`;
2. verify the private APFS snapshot hash equals `5cbef8cee7f9f180afc941380eb2bbfc5d053026ce94444ea513da5360818870`;
3. validate the private receipt through `ArchivePreflightReceipt`;
4. rerun the live read-only preflight;
5. require identity and security agreement with the approved private receipt;
6. reject any profile invalidation condition; and
7. refuse internal-disk, temporary, network, other-removable, or cloud fallback.

## 5. T02A-IMP — Archive bootstrap kernel

T02A-IMP is code-only. It may not write the real archive.

It introduces exactly three contracts:

```text
ApprovedArchiveProfile
ArchiveRootMarker
ArchiveInitializationReceipt
```

It reuses `ArchivePreflightReceipt` and `ArchiveObjectPromotionReceipt`.

It implements:

```text
bsl archive initialize   --profile profiles/archive/ARCHIVE-PROFILE-BSL-ARCHIVE-v1.json   --private-receipt <ignored-path>   --private-apfs-snapshot <ignored-path>   --root /Volumes/BSL-Archive/BiblicalScholarLab
```

The command is idempotent:

- an absent root may be initialized only after all private and live checks pass;
- an existing exact marker is verified and returns `VERIFIED_EXISTING`;
- a nonempty unmarked root, changed marker, changed identity, or unsafe path fails closed.

The initializer creates the directories, root marker, one project-authored canary object, and one immutable initialization receipt through `.incoming`, fsync, SHA-256 verification, and no-overwrite atomic promotion.

The canary bytes are exactly:

```text
BSL_ARCHIVE_INITIALIZATION_CANARY_V1\n
```

T02A-IMP uses synthetic temporary volumes and fake identifiers in tests. It performs no real archive mutation and no external network request.

## 6. T02A-EXEC — Live initialization

T02A-EXEC is a separate owner-approved operational turn after the kernel is merged.

It may:

- run the merged initializer once against the exact approved profile;
- create the canonical root and current layout;
- retain the marker, canary object, and initialization receipt; and
- publish only redacted hashes and booleans in its Git handoff.

It may not acquire a source or add product code.

## 7. T02B-IMP — Source-admission kernel

T02B-IMP is also code-only and uses synthetic transport fixtures. It introduces the smallest records needed by the approved architecture:

```text
FetchReceipt
SourceSnapshot
AdmissionDecision
```

It implements a one-source-at-a-time command. No `--all` network blast-radius command is required:

```text
bsl source acquire   --source-id SP01-SRC-00N   --manifest design/approved/SOURCE-PLAN-01-source-admission-manifest.json   --archive-root /Volumes/BSL-Archive/BiblicalScholarLab
```

All six source specifications are data-driven and immutable.

### GitHub-pinned sources

For SBLGNT, MorphGNT, ASV, Abbott-Smith, and Source Serif:

- use GitHub commit/tag metadata plus exact `raw.githubusercontent.com` paths;
- never clone, fetch, or download a repository archive;
- never checkout or execute upstream code;
- fetch only admitted component files and narrowly identified rights-evidence files;
- verify the full commit and, where applicable, tag resolution.

This rule prevents an excluded component—especially the Abbott-Smith PDF—from entering quarantine merely because it shares a repository.

Frozen paths include:

```text
SBLGNT:
  README.md
  LICENSE
  data/sblgnt/text/John.txt

MorphGNT:
  README.md
  64-Jn-morphgnt.txt

ASV:
  README.md
  License.html
  usx/43-JHN.usx

Abbott-Smith:
  abbott-smith.tei.xml
  README.md  # rights evidence only; not normalized content

Source Serif 4:
  TTF/SourceSerif4-Regular.ttf
  TTF/SourceSerif4-It.ttf
  LICENSE.md
```

### WEB Classic

Use only:

```text
https://ebible.org/Scriptures/eng-web_usfm.zip
```

The connector records the redirect chain, HTTP metadata, acquisition time, package hash, archive inventory, and per-file hashes. It rejects traversal, symlinks, nested archives, encrypted entries, executable content, file-count/byte-limit violations, wrong translation identity, and unexpected John 1:5 content. The acquired package becomes one frozen snapshot and never auto-refreshes.

### Rights and source boundaries

Every source attempt starts in a unique quarantine directory. Admission requires exact revision or frozen package identity, complete rights evidence, expected component inventory, expected John 1:5 or lexical/font checks, content hashes, and one explicit decision.

No unit test or public CI contacts a source URL.

## 8. T02B-EXEC — Live six-source admission

After T02B-IMP merges and the archive root is initialized, one separately approved live turn acquires sources sequentially in source-ID order.

Rules:

- one source command at a time;
- stop on the first unresolved or hard failure;
- prior admitted snapshots remain immutable;
- reruns are idempotent and may only verify an identical snapshot;
- a changed upstream byte, rights statement, tag mapping, or package produces quarantine and review rather than replacement;
- all source bytes remain outside Git.

The execution turn may end partially complete. It may never weaken a gate to finish the batch.

## 9. T02 completion

VS01-T02 completes only when all six source snapshots are admitted and independently reviewed. T02 does not normalize John 1:5.

The next stage is:

```text
VS01-T03 — John 1:5 Source Normalization
```

T03 may then split into parallel Greek/morphology, English translation, and lexical/font tracks against immutable T02 snapshots.

## 10. Explicit non-goals

VS01-T02 does not authorize:

- John 1:5 normalized records;
- PostgreSQL or migrations;
- evidence-packet or synthetic-page generation;
- benchmark execution;
- embeddings, indexes, retrieval, models, training, Lambda, or cloud;
- MACULA, apparatuses, copyrighted translations, private sources, or full-source redistribution;
- source execution, repository cloning, automatic refresh, or silent replacement;
- `BSL-Private`;
- public release of acquired source bytes.


## 11. T02A implementation clarifications approved with activation

The T02A implementation turn is synthetic and code-only:

- it may not read, copy, hash, or inspect the owner's private receipt or APFS snapshot;
- it may not run `diskutil`, `system_profiler`, or the real archive commands;
- it may not create or verify `/Volumes/BSL-Archive/BiblicalScholarLab`;
- every test uses sanitized temporary fixtures and injected read-only observations.

The later live initializer must verify both approved private-evidence hashes, validate the private receipt semantically, rerun the live preflight in memory, and require current APFS quota, encryption, unlocked state, volume identity, physical-store identity, and Thunderbolt agreement before writing.

Only an absent canonical root may be initialized. Any existing unmarked root, including an empty one, fails closed. An exact marked root may be verified without mutation.

First initialization is assembled in a unique same-volume sibling staging directory, fully fsynced, and atomically renamed to the absent canonical root.

The exact canary bytes are:

```text
BSL_ARCHIVE_INITIALIZATION_CANARY_V1\n
```

Their SHA-256 is:

```text
faeb22898dfceb94a94874b336f75be3d084f03f8fce2b24b8bf077134a9407b
```

`ArchiveObjectPromotionReceipt` remains unchanged and fixture-only. The authoritative canary is instead bound by the new `ArchiveInitializationReceipt`.

Joseph approved this design and authorized only `VS01-T02A-IMP` on August 20, 2026. No T02A live execution, source connector, source acquisition, or archive write is authorized by this approval.
