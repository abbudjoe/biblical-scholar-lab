# GOV-01-ERRATA-02 — W00 Activation Scope Integrity

| Field | Value |
|---|---|
| Status | APPROVED CONFORMANCE CORRECTION |
| Approved | 2026-08-17 |
| Applies to | GOV-01 revision 3; GOV-01-ERRATA-01; `ACT-W00-REPOSITORY-GOVERNANCE-v2` |
| Authority | ChatGPT design correction approved under the owner's instruction to proceed with clean-room closure |

## Problem

`ACT-W00-REPOSITORY-GOVERNANCE-v2` correctly superseded v1 and corrected the W00 bootstrap merge procedure, but its `activated_paths` still named the superseded v1 activation manifest. An implementation activation is an immutable scope boundary. It must not authorize Sol to edit a superseded activation, and its objective must not imply that W00 itself performs the live Codex merge-only proof that GOV-01-ERRATA-01 moved to W01.

## Binding correction

A new immutable activation revision, `ACT-W00-REPOSITORY-GOVERNANCE-v3`, must supersede v2 and satisfy all of the following:

1. It retains the owner-manual W00 bootstrap squash-merge exception from GOV-01-ERRATA-01.
2. It does not list any activation manifest as an implementation-writable path.
3. It identifies W00's merge-related responsibility as implementing and fixture-testing the exact-head authorization and merge-only controls, not executing the live Codex merge-only path on W00 itself.
4. It records W01 as the first live Codex merge-only conformance proof and blocks W02 and later work until that proof closes.
5. It preserves every other approved GOV-01, DR-30, model-role, anti-slop, GitHub CLI, handoff, and exact-head review requirement.

## Historical records

- `ACT-W00-REPOSITORY-GOVERNANCE-v1` remains immutable and `SUPERSEDED`.
- `ACT-W00-REPOSITORY-GOVERNANCE-v2` remains immutable and becomes `SUPERSEDED`.
- `ACT-W00-REPOSITORY-GOVERNANCE-v3` becomes the only active W00 implementation manifest.

## No semantic expansion

This correction does not activate new product, source, benchmark, model, cloud, database, UI, or training work. It narrows W00's writable scope and aligns the activation with the already approved bootstrap merge procedure.
