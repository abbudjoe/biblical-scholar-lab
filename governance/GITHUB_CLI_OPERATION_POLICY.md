# GitHub CLI operation policy

## Purpose

Codex uses Joseph's already-authorized GitHub CLI session:

```text
login: abbudjoe
auth mode: GH_CLI_EXISTING_AUTH
```

This file defines which `gh` and Git operations are allowed during an implementation root turn, which become available only in a separate owner-authorized merge-only turn, and which are prohibited.

GitHub cannot distinguish Joseph from Codex under the shared account and stored credential. The human gate is Joseph's explicit approval of an exact PR head in the current ChatGPT conversation, followed by a separate merge-only Sol turn.

## Authentication preflight

Before any GitHub write, Codex must verify:

```bash
gh auth status --active --hostname github.com
```

The active login must be:

```text
abbudjoe
```

These environment variables must be absent:

```text
GH_TOKEN
GITHUB_TOKEN
GH_ENTERPRISE_TOKEN
GITHUB_ENTERPRISE_TOKEN
```

The following commands or flags are prohibited:

```text
gh auth token
gh auth status --show-token
gh auth login
gh auth logout
gh auth refresh
gh auth switch
```

No token value, token fingerprint, credential-store record, or authentication secret may enter logs, handoffs, CI, artifacts, prompts, or model context.

## Class A — implementation-root-turn operations

The approved task branch and draft PR may use:

```text
gh auth status --active --hostname github.com
gh repo view
gh pr create
gh pr edit
gh pr comment
gh pr view
gh pr status
gh pr checks
gh pr diff
gh run list
gh run view
gh run watch
```

Equivalent read-only queries may be implemented through a project-owned allowlisted wrapper.

Ordinary Git may be used to:

- Commit on the assigned task branch.
- Push the assigned task branch.
- Fetch refs.
- Read status, logs, and diffs.

The implementation root turn must not mark the PR ready or merge it.

## Class B — owner-authorized merge-only operations

These operations become eligible only after:

1. ChatGPT has reviewed the exact live PR head and returned `CHATGPT_REVIEW_CLEAN`.
2. Every required check passes for that exact head.
3. Joseph explicitly approves that exact head in the current ChatGPT conversation.
4. ChatGPT produces a separate merge-only prompt containing a schema-valid `OwnerMergeAuthorizationRecord`.
5. Joseph sends that merge-only prompt to Sol.

The merge-only turn may use:

```text
gh pr view
gh pr checks --required
gh pr ready
gh pr comment
gh pr merge --squash --match-head-commit <AUTHORIZED_HEAD_SHA> --delete-branch
```

The exact approved command is:

```bash
gh pr merge <PR> --squash --match-head-commit <AUTHORIZED_HEAD_SHA> --delete-branch
```

Any head mismatch, failed check, unresolved conversation, or malformed/stale authorization must stop without merge.

## Class C — prohibited operations

Codex must not execute or indirectly cause:

```text
gh pr merge --admin
gh pr merge --auto
gh pr review --approve
gh repo edit
gh secret *
gh variable *
gh workflow disable
gh workflow enable
gh release create
gh auth token
gh auth status --show-token
gh auth login/logout/refresh/switch
```

Codex must not use mutating `gh api` or GraphQL calls to:

- Change rulesets or branch protection.
- Change repository settings, collaborators, teams, bypass actors, merge methods, or default branch.
- Change Actions permissions, secrets, variables, environments, workflows, or required checks.
- Merge, close, retarget, or administratively alter a PR outside the approved merge-only action.
- Approve or bypass a deployment or environment review.

Codex must not:

- Push directly to `main`.
- Force-push any reviewed branch.
- Delete `main` or a protected branch.
- Change the remote URL or active authenticated account to evade this policy.

## Read-only API access

When W00 needs REST or GraphQL data unavailable through ordinary `gh` subcommands, Sol may implement an allowlisted read-only wrapper.

The wrapper must:

- Permit only `GET` or explicitly read-only GraphQL operations.
- Restrict repositories and endpoints.
- Reject request bodies that can mutate state.
- Redact headers and credentials.
- Log endpoint, status, timestamp, and response hash rather than secrets.

Raw unrestricted `gh api` is not part of the ordinary Codex tool surface.

GOV-01-S02 gives W00A one non-reusable exception: the exact allowlisted `PUT` may change only ruleset `20960975` to require `project-integrity` and `turn-handoff-integrity`. Owner-environment mutation and every other mutation remain prohibited. Class B stays inactive until W00B.

## Enforcement and fallback

W00B must prove that:

- The implementation prompt and validator prohibit Class B and Class C operations during root turns.
- The merge-only prompt permits only the exact authorized merge sequence.
- The exact head is enforced through `--match-head-commit`.
- New commits make the authorization stale.

Because the GitHub credential is shared, these are process and executable-policy controls, not independent identity authentication.

If the merge-only boundary cannot be implemented faithfully, Codex may still commit, push, and manage draft PRs through existing `gh` authentication, but Joseph must perform every merge personally.
