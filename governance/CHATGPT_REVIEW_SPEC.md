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

Because Codex and Joseph use the same GitHub login and credential, comment authorship is not treated as proof of owner approval. The ordinary same-named check is regression evidence only; the protected authorization workflow validates the live record from trusted base code.

The protected validator accepts only a record:

- On the target PR.
- Matching the current PR head and activation.
- With disposition `CHATGPT_REVIEW_CLEAN`.
- Matching the required schema and a canonical `https://github.com/<repo>/blob/<reviewed-head>/handoffs/<task>/<turn>.json` evidence URL.

## Effect

A clean ChatGPT review allows Joseph to make the exact-head owner decision. It does not approve or merge automatically.

After Joseph approves, ChatGPT produces the separate merge-only authorization prompt.
