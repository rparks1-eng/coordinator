---
name: core-skill-profile
description: Create and validate a named, minimal local Codex skill profile with exact skill paths, hashes, owners, and fallback behavior. Use when a user wants a small always-installed core and a separate on-demand skill catalog. This skill only proposes a profile; it never removes, installs, stages, or publishes skills.
---

# Core Skill Profile

Build one explicit profile artifact outside active skill roots. It must name the
owner, exact local core paths, hashes, reason each is core, dependent workflow,
fallback for missing capabilities, and review date. Never infer that every
router dependency must be core.

Start with a planning profile, not a live migration. A reasonable initial core
candidate is the router plus a verifier/stager and a recovery tool, but the
owner selects the final membership after held-out route tests.

Use `scripts/validate_profile.py PROFILE.json` before proposing quarantine.
Every noncore skill must have a Git registry path, pinned revision, rollback
plan, and an explicit reactivation path. Read `references/profile-schema.md`.
