# PXPress Wiring Contract

## Record boundaries

Use one canonical request identifier and linked records for request identity/current projection, route snapshot, quote/policy snapshot, lifecycle event, capacity/unavailability block, automation attempt, payment event, and operational exception.

Snapshots and events are append-oriented. Dashboard views may project current state but must not silently rewrite history.

## Intake invariants

- Validate size and required fields before provider calls.
- Normalize the accepted payload and compute a stable fingerprint.
- Same idempotency key plus same fingerprint returns the existing request without repeating effects.
- Same key plus different fingerprint returns a conflict.
- Persist the request before route, quote, notification, payment, or calendar work.
- A downstream failure must leave the request visible with a correlated exception.

## Pricing invariants

Fail closed unless required costs are approved, an immutable policy is approved, the full route is authoritative, the service rule exists, and quote generation is enabled.

The `$25` deposit reduces the balance once and never increases the ride total. Late-night and long-distance rules remain inputs until policy-approved.

## One-vehicle capacity

Use half-open intervals and reject real overlaps. Before accepting money, create or prove an authoritative capacity hold with guarded concurrency. If Wix Bookings cannot supply atomic holds, keep the custom availability block authoritative and project to the calendar afterward.

## Effects

Use deterministic effect IDs such as `request-id:event-name:version`. Record suppression, claim, attempt count, next attempt, sanitized error, terminal state, and reconciliation ownership. Distinguish Wix acceptance/queueing, automation execution, provider acceptance, and delivery evidence.

Payment changes require verified events, idempotent processing, and reconciliation. Rollback reverses code/config; compensation handles already-created payments or messages.

## Privacy and authority

- Privilege customer-data collections and owner controls.
- Keep state transitions and money/message effects behind backend commands.
- Do not log addresses, emails, phones, message payloads, tokens, headers, or full provider responses.
- Apply retention, collaborator/MFA review, rate limits, quotas, timeouts, bot controls, and sanitized public errors before broad traffic.

