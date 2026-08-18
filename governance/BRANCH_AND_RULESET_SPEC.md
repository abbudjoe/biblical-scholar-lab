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

Required defense-in-depth checks after W00:

```text
project-integrity
turn-handoff-integrity
chatgpt-review-integrity
owner-merge-record-integrity
```

Expected-App matching for these contexts is defense in depth; it does not prove which workflow, event, branch, or revision produced a same-named check. Project-level trusted evidence comes only from the base-controlled `trusted-governance-validator` receipt, which binds the inspected head, base revision, workflow/run identity, and validator hash without executing candidate code.

Only squash merging is enabled. Auto-merge is disabled.

## Merge sequence

```text
Sol draft PR + handoff
→ four ordinary defense-in-depth checks
→ base-controlled trusted-governance-validator receipt succeeds for that head
→ ChatGPT exact-head review
→ Joseph explicitly approves exact head in ChatGPT
→ protected owner-merge-authorization environment is approved and emits its exact-head receipt
→ ChatGPT emits separate merge-only prompt and authorization record
→ Sol merge-only turn posts exact-head authorization record
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
