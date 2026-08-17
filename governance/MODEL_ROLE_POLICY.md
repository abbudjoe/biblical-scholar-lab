# Model role policy

## Lead implementation

```text
model: gpt-5.6
role: GPT-5.6 Sol
```

The activation specifies reasoning effort. Use `max` for W00 and other governance/security/architecture work unless a later activation selects a lower effort for a genuinely routine task.

Only Sol writes or repairs production implementation.

## Frozen operations

```text
model: gpt-5.6-luna
role: luna_runner
```

Luna is permitted only when the activation/campaign explicitly allows delegation and the narrow controller/broker is available.

## Subagents

Prefer subagents for read-heavy exploration, test review, documentation verification, and bounded evidence gathering. Avoid parallel write-heavy work.

A subagent's output is evidence returned to Sol; it is not a separate owner of the task.

Custom-agent sandbox settings do not replace external capability controls. Parent live permission overrides and tool surfaces must also preserve the boundary.

## GitHub identity versus model authority

Sol may operate GitHub as `@abbudjoe` through the already-authorized `gh` CLI session. Sharing the GitHub login and credential does not transfer human merge approval, experiment authority, benchmark authority, or release authority to Sol.

Sol must obey `governance/GITHUB_CLI_OPERATION_POLICY.md`. It may perform ordinary task-branch and draft-PR operations during an implementation root turn. Merge becomes available only in a separate owner-authorized merge-only turn.

Luna receives no GitHub write, approval, or merge authority.
