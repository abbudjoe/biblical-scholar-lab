# GitHub owner setup

> **HISTORICAL PRE-S03 BOOTSTRAP RECORD — NON-AUTHORITATIVE** — Retained for audit only. `GOV-01-S03` controls the current sequence: task-specific activation and CI → Sol draft PR and concise handoff → ChatGPT exact-head review → Joseph exact-head approval → separate merge-only turn → unchanged-head and task-specific-check verification → `--match-head-commit`.

## Historical detail

This is an owner action. Codex may use the existing authenticated `gh` CLI session as `@abbudjoe` for ordinary task-branch and PR operations. Human merge authorization remains a separate exact-head action in ChatGPT.

## 1. Create the repository

- Owner: `@abbudjoe`
- Proposed name: `biblical-scholar-lab`
- Visibility: public
- Default branch: `main`
- Merge method: squash only
- Auto-merge: disabled
- Force-pushes/deletions on `main`: disabled

Land only the approved static design/governance package before Sol begins.

## 2. Verify existing GitHub CLI authentication

Do not create a new token for Codex.

Verify the already-authorized session:

```bash
gh auth status --active --hostname github.com
```

The active login must be:

```text
abbudjoe
```

Do not use `--show-token` or `gh auth token`.

Ensure these environment variables are absent from Codex sessions:

```text
GH_TOKEN
GITHUB_TOKEN
GH_ENTERPRISE_TOKEN
GITHUB_ENTERPRISE_TOKEN
```

They override ordinary credential-store selection and are not part of the approved operating model.

During bootstrap, configure Git to use GitHub CLI as its credential helper if needed:

```bash
gh auth setup-git --hostname github.com
```

Codex must not run `gh auth login`, `logout`, `refresh`, or `switch`.

Record only a redacted auth-preflight receipt containing host, active login, authentication health, and confirmation that no token override was present. Do not record token values or fingerprints.

## 3. Accept the shared-credential boundary

The existing `gh` credential belongs to the owner account and may have broad repository authority. GitHub cannot use that credential to distinguish Joseph's human action from Codex activity.

The approved controls are therefore:

- Protected `main` rules.
- Exact-head trusted checks.
- `governance/GITHUB_CLI_OPERATION_POLICY.md`.
- Implementation-root-turn stop before merge.
- Explicit owner approval of exact head in ChatGPT.
- Separate merge-only prompt and turn.
- Exact-head `gh pr merge --match-head-commit`.
- Owner-manual merge fallback if the merge-only boundary cannot be implemented faithfully.

## 4. Enable public review limits

Repository Settings → Moderation options → Code review limits:

```text
Limit to users explicitly granted read or higher access
```

This reduces review noise. Formal PR review is not the owner-authorization mechanism because the PR author and owner share the same GitHub account.

## 5. Bootstrap ruleset

Before W00 exists, create a no-bypass ruleset on the default branch with:

- Require pull request before merge.
- Required approvals: `0`.
- Code-owner approval: disabled.
- Resolve all conversations.
- Require linear history.
- Block force pushes.
- Block deletion.

W00 is merged manually by Joseph after exact-head ChatGPT review because the trusted checks do not yet exist on `main`.

## 6. Strengthen the ruleset after W00

After W00 merges, require:

```text
project-integrity
turn-handoff-integrity
chatgpt-review-integrity
owner-merge-record-integrity
```

Use strict/current-head checks. Keep the bypass list empty.

## 7. Protect CODEOWNERS and governance

Confirm GitHub recognizes `@abbudjoe` as owner of:

```text
*
/.github/
/AGENTS.md
/EXPERIMENT_AUTHORITY.md
/governance/
/activations/
/handoffs/
/reviews/
```

CODEOWNERS remains an ownership and notification map; it is not a required self-approval gate.

## 8. Bootstrap verification

Record evidence that:

1. Existing `gh` auth identifies `@abbudjoe` without token display.
2. No token override environment variable is present.
3. Codex can push a task branch and open a draft PR as `@abbudjoe`.
4. Direct push to `main` is rejected.
5. The implementation root turn cannot merge under its approved prompt and validators.
6. A stale or malformed owner authorization record is rejected.
7. `--admin`, `--auto`, auth mutation, governance mutation, and unrestricted mutating `gh api` are prohibited.
8. A new commit invalidates ChatGPT review and owner authorization.
9. An unresolved conversation blocks merge.
10. Force-push and branch deletion are blocked.
11. Only squash merge is available.
12. A separately authorized merge-only turn can merge only the exact approved head—or Joseph performs the merge personally.

The governance proof must not claim GitHub can independently authenticate human versus agent under the shared credential.
