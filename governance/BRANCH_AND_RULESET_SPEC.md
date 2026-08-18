# Branch and ruleset specification

## Branches

```text
main
codex/<activation-id-or-task-slug>
```

Each root turn uses one task branch and one draft PR. Repairs append commits to the same branch/PR unless ChatGPT requires a split.

## Same-account, existing-`gh` operating model

Codex and Joseph both appear on GitHub as:

```text
@abbudjoe
```

Codex uses the already-authorized GitHub CLI session. No separate token, bot account, or GitHub App is required for ordinary Git and PR operations.

Because pull-request authors cannot approve their own pull requests, required PR/code-owner approval is disabled. Human approval occurs outside GitHub's review identity through Joseph's explicit exact-head approval in the current ChatGPT conversation.

The existing credential can have owner-level capabilities. GitHub therefore cannot distinguish Joseph from Codex by login or token. The repository supplements branch rules with a binding root-turn stop rule, an exact-head ChatGPT review, an exact-head owner-authorization record, and a separate merge-only turn.

## Ruleset — main-quality-and-authorization-gates

Target the default branch. Bypass list: empty.

Require:

- Pull request before merge.
- Zero required PR approvals.
- No required code-owner approval.
- All review conversations resolved.
- Strict/current-head required checks.
- Linear history.
- Force-push protection.
- Branch-deletion protection.

Required defense-in-depth checks for the W00A bootstrap:

```text
project-integrity
turn-handoff-integrity
```

Expected-App matching is defense in depth, not workflow provenance. The base-controlled validator becomes operational only after W00A is on `main`. W00B later activates authorization-chain checks and receipt consumption.

Only squash merging is enabled. Auto-merge is disabled.

## Merge sequence

```text
W00A → exact-head review/approval → Joseph manual squash merge
W00B → trusted W00A validation → exact-head review/approval → Joseph manual squash merge
W01 → first live proof of trusted validation, owner receipt consumption, and merge-only execution
```

After W00B activates the merge-only path, the approved Codex merge command is:

```bash
gh pr merge <PR> --squash --match-head-commit <AUTHORIZED_HEAD_SHA> --delete-branch
```

`--admin`, `--auto`, direct push, force-push, and merge-queue bypass are prohibited.

A new commit invalidates the ChatGPT review and owner authorization.

No automatic merge is permitted.
