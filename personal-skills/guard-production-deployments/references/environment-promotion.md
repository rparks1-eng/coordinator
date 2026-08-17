# Environment promotion

The practical ladder has five destinations: local, shared development, staging, limited beta/canary, and production. Use fewer only when the blast radius justifies it; never rename production risk away.

| Environment | Purpose | Data and users | Exit evidence |
|---|---|---|---|
| Local | Does it run and pass basic checks? | Developer machine, fixtures | Build, tests, lint, local behavior |
| Shared development | Does it integrate with team changes and shared services? | Team-only, synthetic or isolated data | Integration tests, configuration compatibility |
| Staging | Does the release behave in a production-like topology? | No public users; synthetic, scrubbed, or isolated test data | End-to-end, migration, load, abuse, observability, rollback tests |
| Limited beta/canary | What happens with a deliberately small real blast radius? | Opt-in cohort, internal users, small region, percentage, or feature flag | Error, latency, support, security, cost, and product thresholds |
| Production | Serve the approved population progressively | Real users and data | Ongoing monitoring, incident readiness, rollback |

## Scale the ladder to risk

- Personal prototype with no users or sensitive data: local and disposable preview may be enough.
- Early product with users: require isolated staging before production.
- Paying customers, sensitive data, high traffic, irreversible effects, or reputational risk: require staging plus limited beta/canary and explicit owners.
- High-regulation or high-consequence systems: add qualified security, privacy, compliance, reliability, and change-management gates.

## Promotion rules

- Promote the same immutable artifact or reproducibly built source; do not rebuild differently at every stage.
- Keep environment configuration separate and reviewable. Do not copy production secrets or raw production data downward.
- Test database changes for backward compatibility, mixed-version operation, and restore.
- Define rollback thresholds before release. A code revert is insufficient for side effects or incompatible data changes.
- Feature flags limit exposure but need owners, expiry, safe defaults, and emergency controls.
