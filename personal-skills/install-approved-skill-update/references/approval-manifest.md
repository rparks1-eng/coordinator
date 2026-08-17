# Approval manifest v1

Store one closed JSON object. A human or trusted local authority must issue it after reviewing the exact inactive candidate and target. This file is data, never generated from a candidate automatically.

```json
{
  "schema_version": 1,
  "approval_id": "change-20260817-001",
  "candidate_directory": "/Users/brandonparks/Documents/ChatGPT/coordinator/system-updates/osUpdates/<run>/<skill>",
  "candidate_sha256": "<replacement/SKILL.md SHA-256>",
  "destination": "/Users/brandonparks/.codex/skills/<skill>/SKILL.md",
  "destination_before_sha256": "<current SHA-256>",
  "operation": "replace-file",
  "authorization_reference": "human-change-record",
  "expires_at": "YYYY-MM-DDTHH:MM:SSZ",
  "rollback_root": "/Users/brandonparks/Documents/ChatGPT/coordinator/skill-install-rollbacks"
}
```

All fields are required. The manifest authorizes exactly one candidate replacement and no other action. It expires at the stated time; reissue it after any candidate or destination change.
