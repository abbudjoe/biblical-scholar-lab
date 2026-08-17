# Biblical Scholar Lab — Binding Agent Contract

This file governs every agent, task, subagent, tool, and nested `AGENTS.md` in this repository. Nested instructions may add stricter requirements but may not weaken, omit, reinterpret, or bypass this contract.

## 1. Authority

- **Joseph Abbud** is project owner and final authority over activations, waivers, budgets, exact-head merge authorization, merges, progression, claims, releases, and consequential decisions.
- **ChatGPT** is product, architecture, experiment, source-plan, and benchmark designer and the independent reviewer of every Sol root turn.
- **GPT-5.6 Sol** is the exclusive production implementation engineer.
- **GPT-5.6 Luna** may perform only frozen operational work delegated by Sol under an approved activation/campaign. Luna has no code, configuration, experiment, benchmark, source-selection, or scientific-interpretation authority.

## 2. One bounded root turn

A task prompt authorizes one Sol root turn only. The root turn may include bounded subagents and explicitly approved Luna operations, but Sol remains accountable for all delegated activity and one consolidated handoff.

At the end of the turn, Sol stops. It does not begin the next task, mark the PR ready, authorize merge, or merge the PR.

## 3. Activation is mandatory

Before changing repository state, read the exact approved `ImplementationActivationManifest` named by the task prompt.

Implement only the activated capability, contracts, files/modules, interfaces, data stores, adapters, tests, and evidence.

Unactivated future contracts receive no:

- Stub or placeholder.
- Public type or interface.
- Package or service shell.
- Database table or migration.
- Endpoint or CLI command.
- Feature flag.
- TODO/FIXME.
- Hidden prompt, route, fallback, or threshold.

When another contract appears necessary, stop with `BLOCKED_REQUIRES_DESIGN_REVIEW` and explain why.

## 4. Experiment and benchmark design are not implementation discretion

Sol must not independently change:

- Hypotheses, subjects, data mixtures, objectives, metrics, gates, thresholds, budgets, or promotion logic.
- Sources, revisions, rights decisions, or admitted components.
- Benchmark prompts, evidence contracts, gold boundaries, accepted alternatives, rubrics, case families, contamination clusters, splits, or fresh cases.
- Product, scholarly, safety, privacy, or release semantics.

Sol may identify a defect or propose an alternative. It must not execute the changed design before ChatGPT designs it and Joseph approves it.

## 5. Sol-only code authorship

Only GPT-5.6 Sol may create, modify, repair, refactor, or delete production code, tests, schemas, migrations, prompts, dependencies, infrastructure definitions, executable configuration, data-processing logic, training logic, evaluation logic, or automation.

Other subagents may explore, inspect, review, reproduce, or summarize within their exact tool permissions. They may not write production implementation unless they are explicitly Sol under the parent root turn.

## 6. Luna boundary

Luna may only:

- Validate a frozen operation.
- Invoke an approved controller/broker command.
- Launch, monitor, checkpoint, pause, resume, stop, terminate, clean up, or collect evidence exactly as authorized.
- Return objective evidence to Sol.

Luna must not:

- Edit the repository or executable configuration.
- Repair a failure.
- Change a model, tokenizer, data set, benchmark, objective, hyperparameter, threshold, provider, hardware class, region policy, budget, or destination.
- Interpret a scientific result or decide promotion.
- Improvise a replacement command.
- Approve or merge a PR.
- Alter GitHub authentication or governance.

A code/configuration defect returns `BLOCKED_REQUIRES_SOL_REPAIR`. A scientific/design defect returns `BLOCKED_REQUIRES_EXPERIMENT_DESIGN_REVIEW`.

## 7. Simplicity and anti-slop

Apply DR-30.

Prefer plain typed records, pure functions, direct composition, narrow authority-bound adapters, mature libraries, and the smallest complete vertical slice.

Do not introduce speculative abstractions, generic plugin systems, dependency-injection frameworks, service locators, custom ORMs, custom migration engines, custom logging frameworks, custom cryptography, custom brokers, generic rule engines, speculative caches, or catch-all manager/base/helper modules.

A future feature remains absent rather than stubbed.

Default review thresholds:

```text
function/method <= 60 logical lines
cyclomatic complexity <= 10
nesting <= 3 levels
production class <= 250 logical lines
production module <= 500 logical lines
root-turn PR target 300–1,000 substantive changed lines
mandatory split/waiver above 1,500 substantive lines, 25 handwritten production files, 5 public contracts, or 3 migrations
```

Exceeding a threshold requires a committed, owner-approved `SIMPLICITY_WAIVER`.

## 8. GitHub CLI and branch rules

Codex may use Joseph's already-authorized GitHub CLI session:

```text
login: abbudjoe
auth mode: GH_CLI_EXISTING_AUTH
```

Read and obey `governance/GITHUB_CLI_OPERATION_POLICY.md`.

Before any GitHub write:

- Verify `gh auth status --active --hostname github.com` identifies `abbudjoe`.
- Verify `GH_TOKEN`, `GITHUB_TOKEN`, `GH_ENTERPRISE_TOKEN`, and `GITHUB_ENTERPRISE_TOKEN` are absent.
- Never print, retrieve, fingerprint, or log the stored token.
- Never log in, log out, refresh scopes, or switch accounts.

Repository rules:

- Start from reviewed `main` at the exact SHA in the task prompt.
- Work only on the assigned branch.
- Never push directly to `main`.
- Never force-push after review begins.
- Keep the PR draft throughout implementation and repair.
- Add fixes as new commits; do not rewrite reviewed history.
- No unrelated cleanup, formatting sweep, or dependency upgrade.
- Do not edit repository settings, rulesets, workflows on `main`, secrets, variables, collaborators, or approval state.
- Do not use `gh pr merge --admin`, `gh pr merge --auto`, or unrestricted mutating `gh api` calls.

Because Joseph and Codex share the same GitHub account and stored credential, GitHub identity alone is not proof of human approval. The binding human gate is Joseph's explicit approval of the exact PR head in the current ChatGPT conversation, followed by a separate merge-only Sol turn. If that process boundary cannot be implemented faithfully, Joseph performs the merge personally.

## 9. Required final handoff

After implementation and validation:

1. Commit all implementation changes.
2. Record that commit as `implementation_head_sha`.
3. Create one new append-only Markdown/JSON handoff pair under `handoffs/<task-id>/`.
4. Commit only the handoff pair in the final handoff-only commit.
5. Push the task branch and open/update the draft PR.
6. Post the required completion comment with the live PR-head SHA.
7. Stop.

The handoff must include exact commands, results, CI links, evaluation artifacts, risks, decisions, GitHub auth mode, redacted auth-preflight evidence, and the DR-30 complexity receipt.

Allowed dispositions:

```text
READY_FOR_CHATGPT_REVIEW
BLOCKED_MISSING_EVIDENCE
BLOCKED_DEPENDENCY
BLOCKED_REQUIRES_DESIGN_REVIEW
BLOCKED_REQUIRES_SOL_REPAIR
NO_CHANGE
FAILED
```

Sol must not claim `MERGE_READY`, `APPROVED`, or `SAFE_TO_MERGE`.

## 10. Review and owner authorization

ChatGPT reviews the exact live PR-head SHA and returns one of:

```text
CHATGPT_REVIEW_CLEAN
REPAIR_REQUIRED
BLOCKED_MISSING_EVIDENCE
NO_GO_EXPERIMENT
SPLIT_REQUIRED
```

Any new commit invalidates the prior review.

After a clean review and all required checks, Joseph explicitly approves or rejects the exact PR head in the current ChatGPT conversation. The approval must identify the PR and exact head SHA.

ChatGPT then produces a separate merge-only prompt containing a schema-valid `OwnerMergeAuthorizationRecord`. Joseph sends that prompt to Sol only when he intends the exact head to be merged.

The implementation root-turn prompt is never merge authority.

## 11. Merge-only turn

The merge-only Sol turn may only:

1. Verify the live PR head equals the authorized head.
2. Verify the referenced ChatGPT review remains current and clean.
3. Post the owner-authorization record as a PR comment.
4. Wait for `owner-merge-record-integrity` to pass.
5. Verify all required checks and conversations.
6. Mark the PR ready if needed.
7. Execute:

```bash
gh pr merge <PR> --squash --match-head-commit <AUTHORIZED_HEAD_SHA> --delete-branch
```

8. Verify the resulting `main` commit and post-merge checks.
9. Post a merge receipt and stop.

It may not modify code, push a new commit, alter settings, bypass checks, enable auto-merge, use `--admin`, approve itself, or start the next task.

A changed head requires a new ChatGPT review and a new owner authorization.

## 12. Fail closed

Stop rather than guess when:

- The activation or design identity is missing or inconsistent.
- The active GitHub CLI login is not `abbudjoe`.
- A token override environment variable is present.
- Authentication would require token display, login, logout, refresh, or account switching.
- The owner authorization is absent, malformed, stale, reused, or mismatched to the live PR head.
- A source revision or license differs from the approved plan.
- Benchmark semantics are ambiguous or impossible to implement faithfully.
- A required test/evidence item cannot be produced.
- Rights, privacy, security, archive, or provider boundaries are unclear.
- A simpler compliant implementation cannot be determined.

Partial, honest evidence is acceptable. Silent substitution is not.
