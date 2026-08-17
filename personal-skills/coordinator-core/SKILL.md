---
name: coordinator-core
description: Issue and close bounded role-cell work orders for a human-facing coordinator. Use when a central chat host must route one request to a least-privilege role cell, require structured report-back, or present a human gate. Never create background loops, auto-activate skills, or authorize mutations.
---

# Coordinator Core

Create one work order per user request. Read `references/work-order.md` before issuing it.

1. Record objective, owner, classification, inputs, output root, role, success test, budget, expiry, and forbidden actions.
2. Route to one role cell. Load no extra skills unless the work order names them.
3. Accept only the role's host report. If it requests a human gate, present the exact decision and stop.
4. Close as `completed`, `needs-human`, `blocked`, or `failed`.

For a proposed new or improved capability, dispatch `$capability-binding-governor`; it determines whether the capability belongs in core, one cell, shared on-demand access, or nowhere. Do not add a capability to a role from a report alone.

The host is the only conversational ingress. A role can request a successor but cannot start, schedule, or broaden one.
