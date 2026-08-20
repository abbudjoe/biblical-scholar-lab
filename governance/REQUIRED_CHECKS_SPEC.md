# Required checks specification

## GOV-01-S03 active rule

There is no universal custom required status check. Each activation names its task-specific CI. Structured review comments are optional evidence, and no owner-record workflow is required. Root-turn handoffs remain concise and append-only without a universal validator.

## Historical W00A1a and planned checks — non-authoritative

## project-integrity

Validates, at minimum:

- Approved activation exists and is schema-valid.
- Changed production files are within activation scope.
- No prohibited placeholder/TODO/stub patterns.
- Namespace and model-role rules.
- Dependency and size budgets.
- Source and benchmark content remain unchanged unless the activation explicitly authorizes a project-designed update.
- Unit/test/lint/type/contract commands required by the activation pass.

## turn-handoff-integrity

Validates:

- One new Markdown/JSON handoff pair.
- Append-only path and unique turn ID.
- JSON schema.
- Final commit is handoff-only.
- `implementation_head_sha` equals final commit parent.
- Activation, branch, task, PR, GitHub login, and auth mode agree.
- Status is allowed.
- `merge_performed` and `next_task_started` are false.
- Complexity receipt is complete.
- Redacted GitHub auth preflight confirms `GH_CLI_EXISTING_AUTH` and active login `abbudjoe` without token output.

## chatgpt-review-integrity

A trusted default-branch workflow/check parses the structured review record without checking out or executing PR code. It verifies:

- Review marker and schema.
- PR and activation match.
- `reviewed_head_sha` equals current head.
- Disposition is `CHATGPT_REVIEW_CLEAN`.
- Review references the completed handoff and evidence set.

Because the PR author and owner share `@abbudjoe`, comment authorship is not treated as human-approval proof. Human approval is represented separately by an exact-head owner authorization record created only after Joseph explicitly approves in the current ChatGPT conversation.

The check must be attached to the reviewed head and become absent/stale on a new push.

## owner-merge-record-integrity

A trusted default-branch workflow/check parses the structured `OwnerMergeAuthorizationRecord` without checking out or executing PR code. It verifies:

- Authorization marker and schema.
- Repository, PR, activation, and ChatGPT review identity.
- `authorized_head_sha` equals the current PR head.
- The referenced ChatGPT review remains current and clean.
- Merge method is `squash`.
- Status is `AUTHORIZED`.
- The record has not expired, been superseded, or been reused.

This check validates exact-head consistency. It does not claim independent authentication of the human origin of the record under the shared GitHub credential.

A new push makes the check stale.

## github-cli-policy-conformance

W00 must prove, through local and repository fixtures, that the approved Codex execution surface:

- Uses the existing `gh` credential-store session for active login `abbudjoe`.
- Rejects token environment-variable overrides.
- Never prints or retrieves the token.
- Permits ordinary task-branch and draft-PR operations.
- Prohibits auth mutation, governance mutation, `--admin`, `--auto`, and direct/force push to `main`.
- Keeps merge unavailable during implementation root turns.
- Permits only the exact authorized merge sequence during a merge-only turn.
- Uses `--match-head-commit` for every Codex-executed merge.

If this cannot be proven, the check reports `OWNER_MANUAL_MERGE_REQUIRED`; implementation may continue, but Codex merge execution remains disabled.
