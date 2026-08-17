# GOV-01-ERRATA-01 — W00 Bootstrap Merge Conformance

| Field | Value |
|---|---|
| Artifact ID | `GOV-01-ERRATA-01` |
| Status | `APPROVED_CONFORMANCE_CORRECTION` |
| Date | 2026-08-17 |
| Project owner | Joseph Abbud |
| Designer and reviewer | ChatGPT |
| Applies to | GOV-01 revision 3; `ACT-W00-REPOSITORY-GOVERNANCE-v1` |
| Purpose | Resolve an internal contradiction without changing the approved same-account GitHub CLI or exact-head owner-authorization policy |

## Correction

GOV-01 section `GOV-B1` correctly states that the W00 bootstrap pull request is a one-time owner-manual merge because the trusted default-branch workflows do not yet exist on `main` and therefore cannot securely validate their own bootstrap PR.

`ACT-W00-REPOSITORY-GOVERNANCE-v1` incorrectly required a live separate Sol merge-only turn for that same W00 bootstrap PR. That requirement is superseded.

The binding sequence is:

```text
W00 Sol implementation root turn
    → draft PR and append-only handoff
    → ChatGPT exact-head review
    → Joseph explicit exact-head approval
    → Joseph manually squash-merges W00
    → post-merge validation proves the four trusted checks exist on main
    → W01 becomes the first live Codex merge-only proof
```

W01 may not merge until the exact-head ChatGPT review, owner authorization, `--match-head-commit`, and all GOV-01 checks succeed. W02 and later implementation remain blocked until the W01 live merge-only proof is complete.

This correction does not change:

- Existing authenticated `gh` CLI use under `@abbudjoe`.
- Sol-only code authorship.
- Luna's no-code frozen-operation boundary.
- Exact-head ChatGPT review.
- Joseph's explicit owner approval.
- Separate merge-only Sol turns after W00.
- No direct push, force-push, bypass, auto-merge, or `--admin` use.
