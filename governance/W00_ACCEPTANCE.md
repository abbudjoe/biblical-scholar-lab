# W00 acceptance criteria

W00 is complete only when all tests are evidenced on the public repository.

## Bootstrap merge rule

W00 is the one owner-manual bootstrap merge. The trusted exact-head workflows do not yet exist on `main`, so the W00 PR must not use the ordinary Codex merge-only path as proof of those checks.

The sequence is:

1. Sol implements W00 on the assigned branch and publishes the draft-PR handoff.
2. ChatGPT reviews the exact live PR head.
3. Joseph explicitly approves that exact head.
4. Joseph manually squash-merges W00.
5. Post-merge validation proves the base-controlled validator and protected authorization workflow are active from `main`.
6. W01 becomes the first live Codex merge-only proof.

W02 and later work remain blocked until W01 proves the ordinary merge-only path.

## Positive paths

- Valid activation accepted.
- Valid implementation plus final handoff-only commit accepted.
- Existing `gh` auth identifies active login `abbudjoe` without token display.
- No token override environment variable is present.
- Valid ChatGPT clean review for the current head accepted.
- W00 owner-manual exact-head squash merge completed after ChatGPT review and Joseph approval.
- The four defense-in-depth checks are operational after W00 merge; expected-App matching is not claimed as workflow provenance.
- W01 proves the first live base-controlled trusted-validator and protected-environment authorization receipts.
- Local and fixture validation proves schema-valid current-head owner authorization is accepted and stale/mismatched authorization is rejected.
- Post-merge validation succeeds.

## Negative paths

- Direct push to `main` rejected.
- Merge during implementation root turn rejected.
- Token environment-variable override rejected.
- `gh auth token`, `--show-token`, login, logout, refresh, and account switch rejected.
- Governance mutation, `--admin`, `--auto`, and unrestricted mutating `gh api` rejected.
- Authorization for a different or stale head rejected by fixtures.
- Reuse of an authorization record rejected by fixtures.
- New commit invalidates ChatGPT review and owner authorization.
- Missing or invalid activation blocks.
- Out-of-scope file change blocks.
- Missing handoff blocks.
- Final commit containing code plus handoff blocks.
- Handoff parent mismatch blocks.
- Sol merge-readiness claim blocks.
- Luna/code-author model-role violation blocks.
- Placeholder/TODO/stub and oversized unwaived PR blocks.
- Invalid or stale ChatGPT review cannot satisfy `chatgpt-review-integrity`.

## W00 evidence bundle

- Ruleset screenshots or API export.
- Public review-limit setting.
- Redacted `gh auth status` receipt showing active login and authentication health.
- Token-override absence receipt.
- GitHub CLI operation-policy positive and negative fixture report.
- Required-check implementation and post-merge run links.
- Draft PR and exact final head.
- Handoff pair.
- ChatGPT review record.
- Joseph exact-head approval reference.
- Owner-manual W00 squash-merge receipt.
- Post-merge validation showing the trusted validator and authorization workflow on `main`.
- Explicit statement that the live Codex merge-only proof is deferred to W01 and blocks W02.

The evidence bundle must state clearly that GitHub did not independently authenticate human versus agent under the shared credential.
