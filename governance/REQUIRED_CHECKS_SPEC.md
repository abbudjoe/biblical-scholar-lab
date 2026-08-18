# Required checks specification

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

This is a static future W00B contract. It is inactive and not required in W00A.

A PR-controlled defense-in-depth check exercises the structured review validator against adversarial fixtures. It verifies:

- Review marker and schema.
- PR and activation match.
- `reviewed_head_sha` equals current head.
- Disposition is `CHATGPT_REVIEW_CLEAN`.
- Review references the completed handoff and evidence set.

It does not accept a live review or prove workflow provenance. The protected authorization workflow later requeries and validates the actual clean review from trusted base code.

The check must be attached to the reviewed head and become absent/stale on a new push.

## owner-merge-record-integrity

This is a static future W00B contract. It is inactive and not required in W00A.

A PR-controlled defense-in-depth check exercises the structured `OwnerMergeAuthorizationRecord` validator against adversarial fixtures. It verifies:

- Authorization marker and schema.
- Repository, PR, activation, and ChatGPT review identity.
- `authorized_head_sha` equals the current PR head.
- The referenced ChatGPT review remains current and clean.
- Merge method is `squash`.
- Status is `AUTHORIZED`.
- The record has not expired, been superseded, or been reused.

It is quality evidence only. The protected environment and base-controlled authorization workflow provide the live owner receipt; neither check-name nor expected-App matching proves provenance.

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

In W00A, merge commands remain unavailable and Joseph performs the bootstrap merge. W00B must implement and prove the merge-only surface before W01.
