# Root-turn handoff specification

## Files

```text
handoffs/<task-id>/<turn-id>.md
handoffs/<task-id>/<turn-id>.json
```

Handoffs are append-only. A repair creates a new turn ID; it never overwrites an earlier handoff.

## Commit protocol

The final commit of the root turn must modify only the new handoff pair. The JSON field `implementation_head_sha` must equal that final commit's first parent.

## Required evidence

The handoff must identify:

- Activation, task, turn, branch, base, and implementation SHA.
- GitHub login `abbudjoe` and auth mode `GH_CLI_EXISTING_AUTH`.
- A redacted auth-preflight receipt confirming the active login and absence of token overrides without exposing the token.
- Draft PR and compare URL.
- Objective, acceptance criteria, and design conformance.
- Files and symbols most important for review.
- Exact validation commands, exit codes, and evidence links.
- Evaluations and artifacts.
- Risks, limitations, skipped checks, and decisions required.
- Delegated Luna/subagent work.
- Billable actions and actual cost.
- Complete DR-30 complexity receipt.
- One allowed disposition.

## Completion comment

After pushing the handoff commit, Sol posts the completion-comment template containing the live PR-head SHA and links to the committed handoff.

## Stop rule

After posting the handoff and completion comment, Sol stops. It does not mark the PR ready, create or post an owner authorization, merge, or start the next task.

Merge, when authorized, occurs later through a separate merge-only Sol turn or by Joseph personally.
