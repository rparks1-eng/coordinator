---
name: guard-production-deployments
description: Plan, review, or execute production deployments with mandatory environment promotion, security, abuse-resistance, reliability, rollback, observability, and cost-containment gates. Use for servers, cloud infrastructure, hosting, public APIs, databases, authentication, networking, firewalls, autoscaling, queues, storage, DNS, CI/CD, or any request to launch, publish, deploy, expose, scale, or modify a production service.
---

# Guard Production Deployments

Treat AI as an implementation assistant, never as the authority that declares a production system safe. Make controls real in infrastructure, application code, provider settings, tests, and alerts; Markdown alone enforces nothing.

## Workflow

1. Classify the target as local, shared development, staging, limited beta/canary, or production. Treat an internet-accessible service with real users, secrets, money, or data as production even if it is called a demo.
2. Choose the minimum promotion path proportionate to blast radius. Read [references/environment-promotion.md](references/environment-promotion.md).
3. Inventory the request path, trust boundaries, identities, secrets, data stores, outbound access, scaling behavior, billable resources, and rollback mechanism.
4. Read [references/production-gates.md](references/production-gates.md). Mark every applicable gate `pass`, `fail`, or `not applicable`, with evidence. Never infer `pass` from intention.
5. Resolve failures before promotion. If a gate requires user authority, credentials, an owner, vendor configuration, or specialist review, stop and state the exact blocker.
6. Test in isolation. Include abuse, authentication failure, malformed input, repeated requests, resource exhaustion, migration compatibility, stale events, and rollback.
7. Promote progressively. Set explicit scale and spend bounds before traffic. Confirm the kill switch and rollback path first.
8. Observe each release using errors, latency, traffic, saturation, security events, user impact, and cost signals. Roll back on predefined thresholds.
9. Record what changed, evidence, residual risks, owner, rollback control, and review date.

## Non-negotiable rules

- Put abuse controls before expensive work: edge filtering, authentication where appropriate, rate and size limits, concurrency limits, timeouts, and bounded queues.
- Configure explicit maximum instances, workers, concurrency, job duration, retries, storage growth, and per-user or tenant consumption. Autoscaling without a maximum is a cost-amplification path.
- Treat budgets and alerts as detection, not prevention. Pair them with quotas, caps, circuit breakers, or automated shutdown.
- Keep secrets out of clients, repositories, logs, prompts, artifacts, and screenshots. Use scoped identities, secret storage, rotation, and least privilege.
- Default-deny network and data access. Separate public ingress from private origins and databases. Restrict outbound access for untrusted or generated code.
- Never give model-generated code direct production credentials or an unrestricted shell. Stage, validate, review, and promote bounded artifacts.
- Require backups and a tested restore path before destructive schema or data changes.
- Keep deployment and rollback operable if the AI system is unavailable.
- A code revert cannot undo user exposure, leaked data, notifications, payments, or incompatible migrations. Limit blast radius before release.
- Do not claim compliance, penetration-test coverage, DDoS immunity, or safety without named evidence and qualified review where required.

## Output

Return the environment classification, promotion path, gate table with evidence, blockers by severity, deployment and rollback plan, and residual risks with human owners. For implementation, store the same record in the project's durable workspace.
