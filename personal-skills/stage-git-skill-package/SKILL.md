---
name: stage-git-skill-package
description: Verify and stage one exact personal skill package from an approved local Coordinator Git revision into an inactive local cache. Use when an owner-selected on-demand skill must be prepared for review or later activation. Never fetch arbitrary remotes, select skills automatically, overwrite active skills, activate staged content, or publish Git changes.
---

# Stage Git Skill Package

Require an exact repository path, immutable commit SHA, canonical skill ID,
expected Git-archive SHA-256, and inactive destination. First run dry mode. Verify the
path is `personal-skills/<id>/`, its `SKILL.md` is valid, and the destination is
outside active skill roots. Stage only when the owner explicitly requests it.

Staging is not activation. Codex may need a new task/app reload before an active
skill is recognized; do not claim otherwise without a host-specific test.

Use `scripts/stage_package.py` and retain its receipt. Read
`references/staging-contract.md`.
