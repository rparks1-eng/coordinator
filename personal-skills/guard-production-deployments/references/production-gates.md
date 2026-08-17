# Production gates

Use this as an evidence checklist. `Pass` means a control exists and was inspected or tested. A plan to add it is `Fail` until implemented.

## Ownership and scope

- Environment and account are identified; production cannot be confused with preview or staging.
- Service owner, security contact, cost owner, and incident contact are named.
- Data classification, retention, deletion, residency, and compliance obligations are known.
- Architecture shows public entry points, trust boundaries, private services, stores, third parties, and outbound connections.

## Internet edge and abuse resistance

- Public traffic reaches an edge proxy, gateway, or load balancer; private origins are not directly reachable.
- Provider DDoS protections appropriate to the risk are enabled.
- Rate limits exist by relevant key: IP, account, token, tenant, endpoint, or expensive operation.
- Authentication and authorization are server-side; object-level access is tested.
- Request bodies, uploads, headers, queries, responses, timeouts, concurrency, queues, retries, and fan-out are bounded.
- Suspicious traffic can be blocked quickly by IP, identity, token, geography, signature, or rule.

## Application and supply chain

- Inputs are validated; output encoding, injection defenses, CSRF/CORS, SSRF, and file handling match the application.
- Dependencies and images are pinned, scanned, and updated through a controlled process.
- Generated or uploaded files are isolated, type-checked, size-limited, scanned where appropriate, and never executed by default.
- Untrusted or AI-generated code runs confined, without production secrets, private network access, or broad filesystem access.

## Identity, secrets, and data

- Humans and workloads use separate scoped identities; privileged humans use MFA.
- Secrets use managed storage and have rotation and revocation procedures.
- Data is encrypted in transit and at rest; database access is private or tightly allowlisted.
- Backups, point-in-time recovery, retention, and restore tests match recovery objectives.
- Audit logs capture privileged changes and sensitive access without recording secrets.

## Scaling and cost containment

- Maximum instances or workers and minimum scale are explicit.
- Per-request CPU, memory, duration, model tokens, external calls, and payload sizes are bounded.
- Per-user or tenant quotas, global concurrency, queue depth, retry count, and background-job fan-out are bounded.
- Storage, logs, egress, build minutes, database capacity, and third-party usage have limits or lifecycle controls.
- Budgets and anomaly alerts notify named owners at multiple thresholds.
- A tested circuit breaker or kill switch can stop expensive traffic without waiting for a redeploy.
- Load and abuse tests demonstrate behavior at limits: reject, shed, queue, degrade, or fail closed—never scale without bound.

## Release, observability, and recovery

- Infrastructure and application changes are reviewable and reproducible.
- Staging resembles production for tested controls and contains no unnecessary production data.
- Metrics and alerts cover errors, latency, traffic, saturation, auth failures, blocks, and cost.
- Canary, beta, blue/green, feature flags, or phased rollout limit impact where risk warrants it.
- Rollback is documented, accessible, and tested; database changes are backward-compatible or have a recovery plan.
- Incident response covers containment, rotation, blocking, evidence, communication, recovery, and review.

## Evidence record

| Gate | Status | Evidence | Owner | Follow-up date |
|---|---|---|---|---|
| Example: maximum workers | Pass | Provider config max = 10; load test rejected overflow | Platform owner | 2026-09-01 |

Prefer reproducible configuration, tests, and audit logs over screenshots alone.
