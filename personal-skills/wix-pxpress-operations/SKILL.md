---
name: wix-pxpress-operations
description: Wire, diagnose, verify, stage, and safely promote PXPress Wix business operations. Use for PXPress reservation intake, operational routing, cost and pricing inputs, credited deposits, capacity and unavailable dates, Wix CMS collections, owner dashboards, automations, Wix Payments event scaffolding, Wix CLI packaging, connector or authorization failures, staging tests, rollback, and production-readiness reviews.
---

# Wix PXPress Operations

Build on the existing PXPress operating system and Wix app without rediscovering account state, duplicating business rules, or falsely calling configuration “live.” Keep all externally consequential effects closed until their evidence gates pass.

## Route the work

1. Start at the repository root and read `business-operations/FILE-MAP.md`.
2. Read only the needed sources:
   - current identities/state: `business-operations/company/current-state.md`;
   - durable decisions: `business-operations/company/decision-log.md`;
   - implementation baseline: `business-operations/_meta/wix-wiring-implementation-2026-08-16.md`;
   - release evidence: `business-operations/dashboards/01-production-gates.md`;
   - notification diagnosis: `business-operations/_meta/notification-403-diagnosis.md`.
3. For Wix API or dashboard facts, use the available Wix connector first and call WixREADME before other Wix management operations. Use browser control only when the connector lacks the operation or requires reauthentication.
4. Use `wix:wix-app` for extension code, `wix:wix-manage` for business APIs, and `guard-production-deployments` for staging or release work.
5. Classify every intended action as `inspect`, `prepare`, `stage`, or `activate`. Do not let a broad request silently turn preparation into production activation.

## Preserve the architecture

- Keep Wix as the customer-data system of record unless an approved, measured limitation changes that decision.
- Keep the custom RideRequest lifecycle authoritative. Treat calendar, notification, and payment records as derived effects.
- Persist intake before routing, pricing, or notification calls.
- Use deterministic request IDs, payload fingerprints, immutable snapshots, append-oriented events, and effect attempt records.
- Calculate all operational legs: base to pickup, passenger service, optional passenger return, and final return to base.
- Treat fallback routing as degraded and never pricing-eligible.
- Apply the flat `$25` deposit once and credit it to the ride total.
- Treat blocked holidays as unavailable dates, not surcharge dates.
- Never invent missing costs. Keep rate generation closed until inputs and a policy version are approved.
- Do not call a trigger acceptance “delivered.” Record `accepted/queued` separately from provider or inbox evidence.

Read `references/wiring-contract.md` before changing schemas, lifecycle behavior, automation effects, or payment/calendar projections.

## Execute the shortest safe loop

1. Capture the exact target account, site, app, environment, existing app version, and rollback path from verified sources.
2. Inspect the worktree before editing; preserve unrelated and uncommitted user work.
3. Make additive schema changes. Preserve legacy fields as compatibility projections until migration evidence exists.
4. Keep these flags false by default: pricing, quote generation, owner notification, customer messaging, payment links, calendar projection, and automatic confirmation.
5. Run the deterministic domain tests.
6. Bundle-check the two APIs, collection extension, dashboard, and site widget.
7. Run the full Wix build only after local checks pass. Report partial packaging honestly when Wix authentication or network access prevents completion.
8. Deploy to an explicitly designated isolated site, never an assumed disposable site.
9. Run the staged acceptance ladder in `references/acceptance-ladder.md`.
10. Promote one effect at a time only after its gate has observed evidence and an independent kill switch.

## Diagnose efficiently

Read `references/known-failures.md` before investigating Wix CLI, connector, app-namespace, or automation authorization errors. Do not print full Wix CLI debug logs: they may contain authorization headers or customer data. Search for error names/status codes and redact surrounding values.

Repair the narrow cause before adding providers, databases, or plugins. An account ID identifies the account but is not an API credential. Browser login, connector authorization, Wix CLI login, and installed-app authorization are separate states.

## Finish truthfully

Report:

- what changed locally, in staging, and in production as three separate scopes;
- exact tests and observed results;
- which effect flags remain off;
- costs, credentials, permissions, or customer data touched;
- rollback target and whether rollback was actually tested;
- blockers that require owner approval or Wix reauthorization;
- the smallest safe next action.

Never mark the workflow complete because schemas, templates, or automations merely exist. Completion requires the applicable observed acceptance evidence.

