---
name: core-skill-runtime
description: Coordinate a core-plus-on-demand personal skill architecture by routing requests to a validated core profile, staging one pinned Git package when the core lacks capability, and preserving explicit activation and rollback gates. Use when operating or designing a lean Codex skill environment. This skill is a coordinator contract, not a literal merge of skill bodies and never auto-fetches, activates, quarantines, deletes, or publishes skills.
---

# Core Skill Runtime

This is the single entry-point contract for the new component set. It does not
merge instructions; it composes their narrow roles.

1. Run `route-prompt-to-skill-flow` against the active core.
2. If it returns `no-supported-route`, identify one owner-selected candidate in
   the pinned registry; do not search arbitrary Git history.
3. Use `stage-git-skill-package` in dry mode, validate the package, then ask for
   an explicit activation decision.
4. Use `core-skill-profile` to maintain the minimal installed set.
5. Use `quarantine-noncore-skills` only after the staged activation path has
   been proven in a fresh task and the owner approves an exact manifest.

Read `references/runtime-boundaries.md` before making recommendations.
