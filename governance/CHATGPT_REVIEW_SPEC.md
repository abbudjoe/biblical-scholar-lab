# ChatGPT exact-head review specification

## Dispositions

```text
CHATGPT_REVIEW_CLEAN
REPAIR_REQUIRED
BLOCKED_MISSING_EVIDENCE
NO_GO_EXPERIMENT
SPLIT_REQUIRED
```

## Binding identity

A review applies only to one exact PR head. Any new commit invalidates it.

## Posting

Joseph normally posts the structured review record from ChatGPT as a PR comment using the marker and JSON format in `governance/templates/chatgpt-review.md`.

Because Codex and Joseph use the same GitHub login and credential, comment authorship is not treated as proof of owner approval. The trusted check validates content and exact-head identity.

The trusted check accepts only a record:

- On the target PR.
- Matching the current PR head and activation.
- With disposition `CHATGPT_REVIEW_CLEAN`.
- Matching the required schema and completion-handoff identity.

## Effect

A clean ChatGPT review allows Joseph to make the exact-head owner decision. It does not approve or merge automatically.

After Joseph approves, ChatGPT produces the separate merge-only authorization prompt.
