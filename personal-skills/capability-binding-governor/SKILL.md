---
name: capability-binding-governor
description: Govern one proposed capability binding between a skill and the coordinator core or a role cell. Use when a new or improved skill may improve a cell, when a binding needs ownership/evaluation, or when a capability is deprecated. Produce reviewable binding records and never auto-activate, merge, delete, quarantine, install, or publish skills.
---

# Capability Binding Governor

First read `$coordinator-core` and `references/binding-record.md`. Require one exact capability path, proposed owner, evidence paths, three motivating cases, one held-out neighbor, and a declared output root.

1. Classify the capability as `core`, `cell`, `shared-on-demand`, or `unassigned`. Core requires evidence that most held-out routes need it; otherwise prefer a cell or on-demand binding.
2. Compare the proposed owner against its role contract. Record why another role or no binding is worse.
3. Write a binding record with `proposed` status and an evaluation plan. Send the host report; do not alter a role skill.
4. After independent evaluation and a human decision, route a selected update through inactive candidate, validation, and separately approved installation workflows.
5. For retirement, first mark `deprecated`, test a replacement and rollback, then propose exact quarantine targets. Never delete; a separate approved custodian may perform a recoverable action.

The core owns binding policy and approval presentation. Role cells may propose evidence but cannot bind capabilities to themselves.
