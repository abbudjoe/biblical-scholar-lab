# Sol merge-only prompt template

Repository:
`<ABSOLUTE_REPOSITORY_PATH>`

Pull request:
```text
<PR_URL_OR_NUMBER>
```

Authorized head:
```text
<EXACT_AUTHORIZED_HEAD_SHA>
```

ChatGPT review:
```text
<CHATGPT_REVIEW_ID>
CHATGPT_REVIEW_CLEAN
```

Owner authorization record:

```json
<OWNER_MERGE_AUTHORIZATION_RECORD>
```

Use **GPT-5.6 Sol**.

This prompt authorizes one merge-only turn. It does not authorize code changes, branch updates, repairs, rebases, settings changes, review changes, or the next task.

Read:

1. `AGENTS.md`
2. `governance/GITHUB_CLI_OPERATION_POLICY.md`
3. `governance/OWNER_MERGE_AUTHORIZATION_SPEC.md`

Perform only this sequence:

1. Verify active `gh` login is `abbudjoe`; do not expose the token.
2. Verify no token override environment variable is present.
3. Fetch and inspect the PR.
4. Verify the live head exactly equals `<EXACT_AUTHORIZED_HEAD_SHA>`.
5. Verify the referenced ChatGPT review is current and clean.
6. Verify all required checks pass and all conversations are resolved.
7. Post the authorization record as the required machine-readable PR comment.
8. Wait for `owner-merge-record-integrity` to succeed on the exact head.
9. Mark the PR ready if necessary.
10. Execute exactly:

```bash
gh pr merge <PR_URL_OR_NUMBER> --squash --match-head-commit <EXACT_AUTHORIZED_HEAD_SHA> --delete-branch
```

11. Verify the resulting `main` commit and post-merge checks.
12. Post a merge receipt.
13. Stop.

Prohibited:

- `--admin`
- `--auto`
- code or configuration changes
- new commits
- branch update or rebase
- force-push
- repository/ruleset/workflow/authentication mutation
- beginning another task

Any mismatch or failed gate requires stopping without merge and reporting the exact reason.
