# Sol root-turn prompt template

Repository:
`<ABSOLUTE_REPOSITORY_PATH>`

Base branch and required base SHA:
```text
main
<EXACT_BASE_SHA>
```

Task branch:
```text
<TASK_BRANCH>
```

Approved activation:
```text
<ACTIVATION_PATH>
<ACTIVATION_SHA256>
```

GitHub execution identity:
```text
login: abbudjoe
auth mode: GH_CLI_EXISTING_AUTH
```

Use **GPT-5.6 Sol** with the effort specified by the activation.

This prompt authorizes one bounded implementation root turn only.

Read and obey, in order:

1. `AGENTS.md`
2. `EXPERIMENT_AUTHORITY.md`
3. `governance/GITHUB_CLI_OPERATION_POLICY.md`
4. The activation manifest
5. Every approved design/source/benchmark artifact referenced by the activation

Before any GitHub write, verify the active `gh` login is `abbudjoe`, verify no token override environment variable is present, and do not expose the token.

Implement only the activated capability. Do not create future scaffolding. Do not alter experiment, source, benchmark, product, safety, rights, or architecture semantics.

Reusable sequence: task-specific activation and CI → Sol draft PR and concise handoff → ChatGPT exact-head review → Joseph exact-head approval → separate merge-only prompt/turn → unchanged-head and task-specific-check verification → `--match-head-commit`.

At completion:

1. Run every required validation.
2. Commit implementation changes.
3. Create the append-only Markdown/JSON handoff pair in a final handoff-only commit.
4. Push only the task branch.
5. Open or update the draft PR.
6. Post the completion comment with the live PR head.
7. Stop with an allowed disposition.

Do not mark ready, submit approval, merge, enable auto-merge, push to `main`, start another task, or claim merge readiness during this root turn.

A later separately prompted merge-only turn may merge only the unchanged head that ChatGPT reviewed and Joseph explicitly approved, using `--match-head-commit` after task-specific checks and conversations pass.
