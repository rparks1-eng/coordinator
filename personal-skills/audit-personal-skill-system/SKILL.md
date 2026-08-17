---
name: audit-personal-skill-system
description: Assess the complete committed Coordinator personal-skill registry for composition, routing, duplicate content, missing contracts, metadata quality, and maintainability; use a bounded council to turn evidence into a detailed skill-system improvement plan and inactive per-skill update candidates. Use when auditing, simplifying, refining, or enhancing a personal skill system as a whole. Never activate, delete, merge, install, or overwrite skills automatically.
---

# Audit Personal Skill System

Use the committed registry as the source of truth. Reuse `$sync-personal-skill-registry`, `$visualize-skill-flow`, `$council-deliberation`, `$system-update`, `$injector`, and `$install-approved-skill-update`; do not reimplement their roles.

## Audit and deliberate

1. Verify `skill-registry/catalog.json` matches `personal-skills/`; if it drifts, run `$sync-personal-skill-registry` in dry-run mode and stop for an explicit capture decision.
2. Create a new output directory under `skill-system-audits/<UTC-run-id>/`; never overwrite or choose a latest run.
3. Run:

   ```bash
   python3 scripts/audit_registry.py --repo /absolute/Coordinator --output /absolute/skill-system-audits/<run>/structural-audit.json
   ```

   The helper is read-only. It detects only exact duplicate trees, name collisions, declared skill references, unresolved references, file/word counts, and incomplete metadata. It does not decide semantic redundancy.
4. Use `$visualize-skill-flow` for a declared-interaction map, then `$council-deliberation` in bounded mode. Give the council the audit JSON, map, catalog, adapter requirements, and exact active/source paths. Require a plan that labels evidence, inference, dissent, expected benefit, risk, validation, rollback, and each proposed file change.
5. Save one `improvement-plan.md`. Mark each proposal `keep`, `candidate`, `needs-owner-decision`, or `reject`. Treat deletion, same-name divergent skills, authority changes, new dependencies, and active installs as `needs-owner-decision`.

## Candidate and promotion lane

Only after the owner selects exact `candidate` targets, call `$system-update` once per target with the plan as knowledge. It produces inactive packages only. Validate each package, review its diff, then use `$injector` and `$install-approved-skill-update` only with a separately issued closed approval manifest. Never use a council result, plan, registry entry, or this skill as approval.

## Acceptance

An audit is complete when its output names every registry skill, reports static evidence separately from judgment, includes a no-change option, and yields no active mutation. A promotion is separately complete only after its existing installer receipt and rollback evidence exist.
