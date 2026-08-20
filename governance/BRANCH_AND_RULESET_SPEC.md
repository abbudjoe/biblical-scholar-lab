# Branch and ruleset specification

## GOV-01-S03 active rule

Each activation names its task-specific CI; no universal custom status check is required. Preserve an empty bypass list, pull requests with zero required approvals, resolved conversations, linear history, force-push and deletion protection, squash-only merging, and disabled auto-merge.

The active sequence is task-specific activation and CI → Sol draft PR and concise handoff → ChatGPT exact-head review → Joseph exact-head approval in the current ChatGPT conversation → separate Sol merge-only turn → `gh pr merge --squash --match-head-commit <SHA>`. A new commit invalidates review and approval.

## Historical pre-S03 specification — non-authoritative

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

Required trusted checks after W00:

```text
project-integrity
turn-handoff-integrity
chatgpt-review-integrity
owner-merge-record-integrity
```

Untrusted PR code must not be able to forge a successful trusted check.

Only squash merging is enabled. Auto-merge is disabled.

## Merge sequence

```text
Sol draft PR + handoff
→ project and handoff checks
→ ChatGPT exact-head review
→ chatgpt-review-integrity succeeds
→ Joseph explicitly approves exact head in ChatGPT
→ ChatGPT emits separate merge-only prompt and authorization record
→ Sol merge-only turn posts exact-head authorization record
→ owner-merge-record-integrity succeeds
→ exact-head squash merge
→ post-merge validation and receipt
```

The approved Codex merge command is:

```bash
gh pr merge <PR> --squash --match-head-commit <AUTHORIZED_HEAD_SHA> --delete-branch
```

`--admin`, `--auto`, direct push, force-push, and merge-queue bypass are prohibited.

A new commit invalidates the ChatGPT review and owner authorization.

No automatic merge is permitted.
