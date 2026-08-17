<!-- BSL_CHATGPT_REVIEW_V1 -->

```json
{
  "schema_version": "1.0",
  "review_id": "<REVIEW_ID>",
  "pr_url": "<PR_URL>",
  "activation_id": "<ACTIVATION_ID>",
  "base_sha": "<BASE_SHA>",
  "reviewed_head_sha": "<EXACT_CURRENT_PR_HEAD_SHA>",
  "reviewer": "ChatGPT",
  "disposition": "CHATGPT_REVIEW_CLEAN",
  "summary": "<SUMMARY>",
  "findings": [],
  "evidence_reviewed": [],
  "required_next_action": "OWNER_AUTHORIZATION",
  "review_timestamp": "<RFC3339_TIMESTAMP>"
}
```

This review applies only to the exact `reviewed_head_sha`. A new commit invalidates it. Joseph's later exact-head approval in the current conversation remains the binding human authorization.
