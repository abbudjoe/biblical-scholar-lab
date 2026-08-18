# W00 acceptance criteria

W00 is complete only when all tests are evidenced on the public repository.

## Bootstrap merge rule

GOV-01-S02 splits bootstrap into W00A (validation foundation) and W00B (owner authorization and receipt consumption). Both are owner-manual exact-head squash merges; neither may claim a live Codex merge-only path.

The sequence is:

1. W00A installs the base-controlled validator; ChatGPT reviews and Joseph approves/merges its exact head manually.
2. A new base-approved activation and PR implement W00B under that trusted validator; Joseph again approves/merges manually.
3. W01 becomes the first live proof of trusted validation, protected authorization, receipt consumption, and merge-only execution.

W02 and later work remain blocked until W01 proves the ordinary merge-only path.

## Positive paths

- Valid activation accepted.
- Valid implementation plus final handoff-only commit accepted.
- Existing `gh` auth identifies active login `abbudjoe` without token display.
- No token override environment variable is present.
- Valid W00A completion and record ordering accepted without activating authorization or merge records.
- W00A requires only `project-integrity` and `turn-handoff-integrity`; they are defense in depth, not provenance.
- The trusted validator becomes operational only from `main` after W00A's manual merge.
- Post-merge validation succeeds.

## Negative paths

- Direct push to `main` rejected.
- Merge during implementation root turn rejected.
- Token environment-variable override rejected.
- `gh auth token`, `--show-token`, login, logout, refresh, and account switch rejected.
- Governance mutation, `--admin`, `--auto`, and unrestricted mutating `gh api` rejected.
- Authorization or merge records are rejected while W00B is inactive.
- New commit invalidates the handoff/completion/review binding.
- Missing or invalid activation blocks.
- Out-of-scope file change blocks.
- Missing handoff blocks.
- Final commit containing code plus handoff blocks.
- Handoff parent mismatch blocks.
- Sol merge-readiness claim blocks.
- Luna/code-author model-role violation blocks.
- Placeholder/TODO/stub and oversized unwaived PR blocks.
- Candidate scripts, workflows, Actions, hooks, dependencies, and generated commands are never executed by the trusted validator.

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
- Joseph exact-head approval reference and owner-manual W00A squash-merge receipt (post-turn).
- Post-merge validation showing the trusted validator on `main`; owner authorization remains absent until W00B.
- Explicit W00B prerequisites and statement that the live Codex merge-only proof is deferred to W01.

The evidence bundle must state clearly that GitHub did not independently authenticate human versus agent under the shared credential.
