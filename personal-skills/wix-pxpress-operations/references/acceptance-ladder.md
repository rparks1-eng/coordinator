# PXPress Acceptance Ladder

Run gates sequentially so failures remain attributable.

## Gate 0 — Identity and recovery

- Verify account, site, app, environment, existing version, data baseline, and flags.
- Identify a staging site explicitly.
- Preserve an independently operable rollback target.
- Do not call an export a database backup.

## Gate 1 — Local checks

- Test the credited deposit, missing-cost/degraded-route fail-closed behavior, annualization, lifecycle shortcuts, capacity overlap, automation deduplication/redaction, and full route-leg summation.
- Bundle-check both APIs, collection extension, dashboard, and widget.
- Require the full Wix build before calling a deployment build-verified.

## Gate 2 — Staged intake

- Submit one synthetic request.
- Replay the same key/payload and observe one request with no repeated effect.
- Reuse the key with a changed payload and observe a conflict.
- Force route and notification failures independently; preserve the request and exception.

## Gate 3 — Route, price, and capacity

- Use pinned route fixtures and tolerances.
- Count every operational leg once.
- Prevent incomplete costs or degraded routes from creating payable quotes.
- Race overlapping one-vehicle holds and accept at most one.
- Prove blocked-date boundaries in the business timezone.

## Gate 4 — Effects

- Refresh installed-app authorization without uninstalling the app.
- Send one allowlisted internal notification and prove exactly one received message.
- Force retry exhaustion and verify exception ownership.
- Verify payment authenticity, idempotency, and reconciliation before live payment links.
- Prove calendar reconciliation from authoritative request/capacity state.

## Gate 5 — Limited beta

- Define volume, mileage, payment, message, and time caps.
- Define measurable stop conditions and an owner.
- Exercise kill switches and rollback separately from compensation.
- Review evidence before enabling another effect or broader traffic.

