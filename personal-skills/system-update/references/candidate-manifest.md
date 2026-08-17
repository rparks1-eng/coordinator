# Candidate manifest schema

```json
{"schema_version":1,"candidate_id":"system-update/<run>/<skill>","status":"non-active","target_skill_id":"skill-id","target_baseline_sha256":"<hex|unknown>","knowledge_sources":[{"path":"/absolute/file.md","sha256":"<hex>"}],"files":[{"source":"replacement/SKILL.md","destination":"/absolute/skill/SKILL.md","operation":"replace-file","sha256":"<hex>"}],"requires_separate_delivery_approval":true,"handoff":{"version":1,"producer":"system-update","candidate_path":"/absolute/inactive/candidate","replacement_sha256":"<hex>","created_at":"YYYY-MM-DDTHH:MM:SSZ","evidence_class":"static-candidate","non_authority":"candidate-only"}}
```

Reject globs, relative destinations, traversal, symlinks, deletion, and commands. `unknown` baseline blocks delivery. Candidate status never means approved, staged, or installed.
