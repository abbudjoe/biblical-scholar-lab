# W00 acceptance criteria

W00 is complete only when all tests are evidenced on the public repository.

## Positive paths

- Valid activation accepted.
- Valid implementation + final handoff-only commit accepted.
- Existing `gh` auth identifies active login `abbudjoe` without token display.
- No token override environment variable is present.
- Valid ChatGPT clean review for current head accepted.
- A schema-valid exact-head owner authorization record is accepted only after the referenced clean review.
- A separately authorized merge-only turn can post the record, satisfy `owner-merge-record-integrity`, and squash-merge the exact approved head.
- Post-merge validation succeeds.

## Negative paths

- Direct push to `main` rejected.
- Merge during implementation root turn rejected.
- Merge attempt without owner authorization rejected.
- Token environment-variable override rejected.
- `gh auth token`, `--show-token`, login, logout, refresh, and account switch rejected.
- Governance mutation, `--admin`, `--auto`, and unrestricted mutating `gh api` rejected.
- Authorization for a different/stale head rejected.
- Reuse of an authorization record rejected.
- New commit invalidates ChatGPT review and owner authorization.
- Missing/invalid activation blocks.
- Out-of-scope file change blocks.
- Missing handoff blocks.
- Final commit containing code plus handoff blocks.
- Handoff parent mismatch blocks.
- Sol merge-readiness claim blocks.
- Luna/code-author model-role violation blocks.
- Placeholder/TODO/stub and oversized unwaived PR blocks.
- Invalid/stale ChatGPT review cannot satisfy `chatgpt-review-integrity`.
- If merge-only boundary enforcement cannot be proven, Codex merge execution remains disabled and owner-manual merge is required.

## W00 evidence bundle

- Ruleset screenshots/API export.
- Public review-limit setting.
- Redacted `gh auth status` receipt showing active login and authentication health.
- Token-override absence receipt.
- GitHub CLI operation-policy positive and negative fixture report.
- Required-check run links.
- Draft PR and exact final head.
- Handoff pair.
- ChatGPT review record.
- Owner exact-head authorization record.
- Exact-head Codex or owner squash-merge receipt.
- Post-merge validation.

The evidence bundle must state clearly that GitHub did not independently authenticate human versus agent under the shared credential.
