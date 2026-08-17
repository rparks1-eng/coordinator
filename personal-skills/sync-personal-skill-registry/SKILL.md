---
name: sync-personal-skill-registry
description: Safely inventory direct personal Codex skills, refresh their portable Coordinator Git registry snapshots, and optionally create a scoped commit, push it to the approved Coordinator remote, and open a draft pull request. Use when publishing or updating the personal-skill source registry; never use to capture system, shared, plugin, credential, binary, or uncertain-provenance content, or to stage unrelated workspace artifacts.
---

# Sync and Publish Personal Skills

Use this as the one workflow for the personal-skill registry. It composes the inventory and Git-publish steps without treating every discovered skill root as approved for capture.

## Scope

The only automatic capture root is `/Users/brandonparks/.codex/skills`, excluding `.system`. Shared-agent roots and plugin caches are inventoried as review-only and are never copied unless this skill is deliberately redesigned with an owner-approved provenance policy.

The approved remote is `https://github.com/rparks1-eng/coordinator.git`. This workflow verifies it; it never silently replaces an existing remote.

## Run

Start with a dry run. It produces the current inventory and planned registry changes without writing anything:

```bash
python3 scripts/sync_registry.py --repo /Users/brandonparks/Documents/ChatGPT/coordinator
```

After reviewing the report, write the registry update:

```bash
python3 scripts/sync_registry.py --repo /Users/brandonparks/Documents/ChatGPT/coordinator --write
```

Publish only after the owner explicitly requests this exact registry change. The command creates a scoped branch when starting from `main`, stages only the generated registry paths, commits, pushes, and opens a draft PR:

```bash
python3 scripts/sync_registry.py --repo /Users/brandonparks/Documents/ChatGPT/coordinator --write --commit --push --draft-pr --message 'chore(skills): sync personal skill registry'
```

## Safety contract

The helper rejects secret-like text, symlinks, unsupported files, malformed skills, source drift, a wrong or missing approved remote, dirty generated registry paths, and a pre-staged mixed index. It never stages broad workspace changes, deletes active source skills, installs a CLI, authenticates an API, or activates a captured skill.

Registry snapshots are portable source records, not runtime targets. Adapter findings are labeled heuristic and preserve file/line provenance; they never grant credentials or installation authority. Exact tree duplicates become aliases; divergent names and semantic overlap remain review findings.

If a run stops because generated paths are already dirty, review or commit those changes separately. Do not use `git add -A` to bypass the boundary.
