# Recommendation report contract

Create one new report with this frontmatter:

```yaml
---
status: advisory-not-approval
created_at: <UTC ISO-8601 timestamp>
map_path: <exact absolute path>
map_sha256: <observed SHA-256>
scope: static-only | partial-contract-analysis | contract-analysis
---
```

Use these sections in order:

1. `# Skill Connectivity Recommendations`
2. `## Input evidence`
3. `## Static observations`
4. `## Contract and handoff assessment`
5. `## Prioritized improvements`
6. `## Suggested execution orders`
7. `## Troubleshooting routes`
8. `## Automation and cross-chat requirements`
9. `## Authority and safety`
10. `## Verification`
11. `## No-change option`
12. `## Smallest reversible next step`

Every proposed route names source paths and hashes, its handoff artifact, evidence class, owner, preconditions, human gate, stop condition, fallback, confidence, and one discriminating test. Do not claim execution, delivery, approval, active status, compatibility, scheduling, or self-improvement unless the cited evidence independently supports that exact claim.

Use the report to minimize copied contract prose. Redact secret-like values; do not replace reproducible path and hash evidence indiscriminately.
