# GOV-01 — Public Repository Governance and Review Package, Revision 3

| Field | Value |
|---|---|
| Artifact ID | `GOV-01` |
| Status | `APPROVED` |
| Approved revision | `3` |
| Proposal date | 2026-08-17 |
| Approval date | 2026-08-17 |
| Owner disposition | Approved without further amendment after selecting existing authenticated GitHub CLI operation |
| Project owner | Joseph Abbud (`@abbudjoe`) |
| Governance and review designer | ChatGPT |
| Implementation authority | GPT-5.6 Sol only |
| Frozen-operation authority | GPT-5.6 Luna only when delegated by Sol under an approved activation or campaign |
| GitHub execution identity | `@abbudjoe` through the already authenticated GitHub CLI credential store |
| Human merge-approval mechanism | Explicit exact-head owner authorization in the current ChatGPT conversation, followed by one separate merge-only Sol turn |
| Depends on | Design baseline `2056d707865df8ab5e3f5ba55e07bd372c6ef752`; DR-20, DR-21, DR-25, DR-30; VS-01; SOURCE-PLAN-01; BENCH-VS01-BATCH-01 |
| Purpose | Establish public-repository authority, branch protection, root-turn handoff, exact-head ChatGPT review, explicit owner authorization, same-account GitHub CLI operation, merge control, model-role, activation, and anti-slop contracts before Sol writes production implementation |

## 1. Governing principle

> **Codex may use Joseph's existing authenticated `gh` CLI session and Git identity to commit, push task branches, open or update pull requests, post review records, and—only after explicit exact-head owner approval—perform a squash merge. The implementation root turn always stops before merge. A separate merge-only turn receives the owner authorization, validates the live PR head and all required checks, posts the authorization record, merges, verifies `main`, and stops.**

The governance system remains efficient: internal subagents and frozen Luna operations do not create separate pull requests or manual review cycles; the accountable Sol root turn does.

## 2. Accepted same-credential limitation

Joseph and Codex use the same GitHub account and the same already authenticated GitHub CLI credential. GitHub therefore cannot independently prove whether a command executed under `@abbudjoe` came from Joseph personally or from Codex.

This package does **not** claim cryptographic human/agent separation. The human-approval boundary is procedural and exact-head bound:

```text
Sol implementation turn stops
    → ChatGPT reviews exact PR head
    → Joseph explicitly approves that exact head in this conversation
    → ChatGPT produces a merge-only authorization prompt
    → Sol executes only that merge action
```

A required `owner-merge-record-integrity` check prevents accidental stale-head or malformed authorization, but comment authorship is not treated as proof that a human—not Codex—created it.

If stronger technical separation becomes necessary later, the approved options are a separate least-privilege credential, a GitHub App, or a hardware-/biometric-signed out-of-band approval. None is required for the initial project because Joseph explicitly chose the existing `gh` CLI workflow.

## 3. Existing GitHub CLI authentication

Codex uses the authentication already stored by `gh` for `github.com`.

Before any GitHub write operation, it must run a nonsecret preflight equivalent to:

```text
gh auth status --active --hostname github.com
```

and verify that the active login is:

```text
abbudjoe
```

The environment variables `GH_TOKEN`, `GITHUB_TOKEN`, `GH_ENTERPRISE_TOKEN`, and `GITHUB_ENTERPRISE_TOKEN` must be absent unless a later approved activation deliberately changes the authentication design, because they override stored GitHub CLI credentials.

Codex must never run or expose:

```text
gh auth token
gh auth status --show-token
gh auth login
gh auth logout
gh auth refresh
gh auth switch
```

or read/export the underlying credential store. It may use the authenticated CLI; it may not extract or alter its secret.

## 4. GitHub command policy

### Allowed during an implementation root turn

```text
gh auth status          without --show-token
gh repo view
gh pr create
gh pr edit
gh pr view
gh pr comment
gh pr checks
gh pr status
gh run list/view/watch  read-only
git fetch/status/diff/log/commit/push on the assigned task branch
```

`gh api` is read-only unless the activation names an exact write endpoint and purpose.

### Allowed only during an owner-authorized merge-only turn

```text
gh pr view
gh pr checks --required
gh pr ready
gh pr comment           authorization and merge receipts only
gh pr merge --squash --match-head-commit <SHA> --delete-branch    exact approved PR only
git fetch/log/status    verification only
```

### Prohibited unless a later owner-approved activation says otherwise

```text
gh ruleset
gh secret
gh variable
gh repo edit
gh workflow run/enable/disable
gh api write operations outside an exact allowlist
any environment/deployment approval API
any authentication mutation or token display
any direct push to main
any force push after review begins
any merge before owner authorization
```

## 5. Bootstrap phases

### `GOV-B0 — Owner bootstrap`

Joseph creates the public repository and lands only the static, owner-approved governance and design package. Before Sol starts, Joseph configures:

- Squash-only merge.
- Auto-merge disabled.
- A no-bypass `main` ruleset.
- The existing authenticated GitHub CLI login remains active.

No production code, source acquisition, benchmark execution, Lambda operation, or model work is authorized.

### `GOV-B1 — W00 governance implementation`

Sol implements the automated governance checks under `ACT-W00-REPOSITORY-GOVERNANCE-v1` in one draft PR. W00 adds no biblical domain behavior.

W00 is the one bootstrap exception: because its trusted workflows do not yet exist on `main`, Joseph performs the final manual squash merge after ChatGPT reviews the exact head and the provisional bootstrap rules pass.

### `GOV-B2 — Governance proof`

After W00 merges, the governance proof must show that:

- The existing `gh` CLI session operates as `@abbudjoe`.
- No token override environment variable is active.
- Direct push to `main`, force push, branch deletion, and merge with missing required checks are blocked.
- The implementation root-turn prompt and handoff prohibit merge.
- The exact-head ChatGPT review check becomes stale on a new commit.
- A merge-only authorization record for another head is rejected.
- A separate merge-only turn can squash-merge only the exact approved head after all checks pass.
- Luna cannot write repository code or configuration.

The proof cannot and must not claim that GitHub distinguishes Joseph from Codex under the shared credential.

## 6. Exact GitHub posture after W00

### Ruleset — `main-quality-and-authorization-gates`

Target: default branch. Bypass list: empty.

Required:

- Pull request before merge.
- Required approving reviews: `0`.
- Required code-owner review: disabled.
- All review conversations resolved.
- Strict required checks against the current head.
- Linear history.
- Block force pushes.
- Block branch deletion.

Required trusted checks:

```text
project-integrity
turn-handoff-integrity
chatgpt-review-integrity
owner-merge-record-integrity
```

Only squash merging is enabled; auto-merge is disabled.

`owner-merge-record-integrity` validates the exact-head authorization record. It does not claim to verify that the GitHub actor was physically Joseph.

## 7. Root-turn review boundary

One Sol root turn may include:

- Implementation by Sol.
- Read-only exploration or review subagents.
- Tests and local validation.
- Frozen Luna operations explicitly allowed by the activation.
- Sol synthesis of delegated evidence.

It ends when Sol:

1. Commits the implementation.
2. Creates one append-only Markdown/JSON handoff in a final handoff-only commit.
3. Pushes the task branch using the existing authenticated `gh`/Git setup.
4. Opens or updates one draft PR.
5. Posts the completion comment binding the handoff to the live PR head.
6. Stops with an allowed disposition.

The implementation root turn never marks ready, authorizes, or merges.

## 8. Exact-head ChatGPT review

ChatGPT review is represented by a structured record containing:

```text
review ID
PR URL
activation ID
base SHA
reviewed PR-head SHA
disposition
findings and evidence
required next action
timestamp
```

The trusted `chatgpt-review-integrity` check validates the record against the live head. Comment authorship is not treated as proof of human approval.

Any new commit changes the head and invalidates the review.

## 9. Exact-head owner authorization

After `CHATGPT_REVIEW_CLEAN` and all nonowner checks pass, Joseph explicitly authorizes or rejects the exact PR head in the current ChatGPT conversation.

The approval should identify:

```text
PR URL or number
exact head SHA
ChatGPT review ID
merge method: squash
```

ChatGPT then produces a separate merge-only prompt containing one schema-valid `OwnerMergeAuthorizationRecord` for that exact head.

The merge-only Sol turn:

1. Verifies the live head equals `authorized_head_sha`.
2. Verifies the referenced ChatGPT review remains current and clean.
3. Posts the machine-readable authorization record as a PR comment.
4. Waits for `owner-merge-record-integrity` to pass.
5. Verifies every required check and conversation state.
6. Marks the PR ready if needed.
7. Executes `gh pr merge <PR> --squash --match-head-commit <AUTHORIZED_HEAD_SHA> --delete-branch`.
8. Verifies the resulting `main` commit and post-merge checks.
9. Posts a merge receipt and stops.

It may not modify code, push a new commit, alter settings, bypass checks, enable auto-merge, or start the next task.

A changed head requires a new ChatGPT review and a new owner authorization.

## 10. Non-self-referential handoff protocol

A committed handoff cannot include the SHA of its own containing commit. The protocol remains:

```text
implementation commit(s)
    ↓
record implementation_head_sha
    ↓
final handoff-only commit containing Markdown/JSON pair
    ↓
push draft PR
    ↓
completion comment records live PR-head SHA
```

`turn-handoff-integrity` verifies the parent/head relationship and append-only handoff.

## 11. Model authority

### GPT-5.6 Sol

Sol is the exclusive production-code author. It implements only the owner-approved activation and may make only design-neutral engineering decisions.

### GPT-5.6 Luna

Luna may perform only frozen, controller-bounded operations delegated by Sol. It receives no repository-write, GitHub-merge, experiment-design, or source/benchmark authority.

### ChatGPT and Joseph

ChatGPT owns product, experiment, source, benchmark, and architecture design and reviews every exact PR head. Joseph owns all activations, waivers, budgets, merge authorization, progression, public claims, and release.

## 12. Non-self-hosting and trusted checks

Trusted checks run from the reviewed default-branch workflow definitions and do not execute untrusted PR code when validating review or authorization comments.

Untrusted PR code must not be able to forge a successful trusted check.

The authorization check validates:

- Record marker and schema.
- Repository, PR, activation, and review identity.
- `authorized_head_sha` equals the current PR head.
- The referenced ChatGPT review is clean and current.
- Merge method is `squash`.
- Authorization has not expired, been superseded, or been reused.

It explicitly does not assert independent human-origin authentication.

## 13. W00 scope

The first Sol PR implements only:

```text
project-integrity
turn-handoff-integrity
chatgpt-review-integrity
owner-merge-record-integrity
activation validation
handoff validation
review-record validation
owner-authorization-record validation
live GitHub-governance verification
positive and negative governance fixtures
```

It excludes:

- Source acquisition.
- Benchmark execution.
- Biblical domain models.
- PostgreSQL domain schemas.
- LangGraph.
- Inspect AI.
- Embeddings or vector search.
- Model inference.
- Lambda.
- Training.
- Web UI.
- Future service shells.

## 14. Required GOV-01 artifacts

The package contains:

- Root `AGENTS.md`.
- `EXPERIMENT_AUTHORITY.md`.
- `.github/CODEOWNERS`.
- Pull-request template.
- GitHub owner setup, CLI operation policy, and branch/ruleset specification.
- Root-turn handoff and ChatGPT review specifications.
- Owner merge-authorization specification.
- Required-checks and W00 acceptance specifications.
- JSON Schemas and templates.
- Sol implementation and merge-only prompt templates.
- Luna custom-agent policy.
- Proposed W00 activation.

The static package contains no executable GitHub Actions workflows or validators. Sol writes those during W00.

## 15. Approval statement

> **Biblical Scholar Lab will allow GPT-5.6 Sol to use Joseph Abbud's existing authenticated GitHub CLI session and GitHub identity for task-branch commits, pushes, pull-request operations, review-record posting, and exact-head squash merging. The implementation root turn will always stop after publishing its draft-PR handoff. ChatGPT will review the exact live PR head, and Joseph will explicitly approve or reject that exact head in the current conversation. A separate merge-only Sol turn will receive a schema-valid owner authorization, post it to the PR, wait for the exact-head authorization check, verify all required checks and conversations, squash-merge, validate `main`, and stop. GitHub's shared account and credential cannot independently authenticate whether a command came from Joseph or Codex; this limitation will be stated openly rather than obscured by a false protected-environment claim. The repository will block direct `main` pushes, force pushes, branch deletion, stale reviews, stale authorization, missing handoffs, failed checks, and non-squash merge, while the binding human gate remains Joseph's explicit exact-head approval and the separately authorized merge-only turn.**
