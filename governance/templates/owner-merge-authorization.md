<!-- BSL_OWNER_MERGE_AUTHORIZATION_V1 -->

```json
{
  "schema_version": "1.0",
  "authorization_id": "<AUTHORIZATION_ID>",
  "repository": "<OWNER/REPO>",
  "pr_url": "<PR_URL>",
  "activation_id": "<ACTIVATION_ID>",
  "chatgpt_review_id": "<CHATGPT_REVIEW_ID>",
  "authorized_head_sha": "<EXACT_CURRENT_PR_HEAD_SHA>",
  "owner_login": "abbudjoe",
  "authorization_channel": "CHATGPT_CONVERSATION_EXPLICIT_APPROVAL",
  "owner_approval_reference": "<CHATGPT_CONVERSATION_TURN_OR_APPROVAL_ID>",
  "approved_at": "<RFC3339_TIMESTAMP>",
  "merge_method": "squash",
  "status": "AUTHORIZED"
}
```

This authorization is valid only for the exact `authorized_head_sha`, referenced clean ChatGPT review, and one merge attempt. GitHub account identity alone is not represented as proof of human approval.
