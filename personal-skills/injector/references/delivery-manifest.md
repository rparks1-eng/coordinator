# Delivery manifest schema

```json
{"schema_version":1,"candidate_directory":"/absolute/inactive/candidate","candidate_sha256":"<hex>","destination":"/absolute/active/SKILL.md","destination_before_sha256":"<hex>","operation":"stage-only","stage_destination":"/absolute/staging/SKILL.md","authorization_reference":"human-change-id","expires_at":"YYYY-MM-DDTHH:MM:SSZ","rollback_root":"/absolute/rollback"}
```

This is a **closed approval manifest**, not a delivery letter. It must be separately issued by a human/trusted-host authority and bind all fields exactly. `replace-file` needs a trusted-host transaction, exact approval, destination lock, same-filesystem atomic replacement, post-write validation, independently operable rollback, and recoverable backup. The bundled helper accepts only `stage-only` and never performs active replacement.
