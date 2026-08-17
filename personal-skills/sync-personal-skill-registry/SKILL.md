---
name: sync-personal-skill-registry
description: Capture reviewed user-authored Codex skills into a portable Coordinator Git source registry, inventory CLI/API requirements declaratively, identify exact duplicates, and make an explicitly scoped Git commit. Use when consolidating personal skills from approved local roots into Coordinator; never use to copy system, bundled, cached, candidate, credential, binary, or uncertain-provenance skills, activate a skill, install a CLI, authenticate an API, or delete source skills.
---

# Sync Personal Skill Registry

Make Coordinator a portable source-of-record, not a runtime mirror. Use [the policy](references/registry-policy.md) before changing the default roots.

## Capture

Run a dry run first. The only default eligible root is the direct user-managed Codex skill root; other discovered roots are recorded as review-only until the owner explicitly classifies them.

```bash
python3 scripts/sync_registry.py --repo /Users/brandonparks/Documents/ChatGPT/coordinator
python3 scripts/sync_registry.py --repo /Users/brandonparks/Documents/ChatGPT/coordinator --write
```

The helper copies only non-symlink, portable skill files to `personal-skills/<id>/`, writes `skill-registry/catalog.json` and `skill-registry/adapter-requirements.json`, and refuses source drift, secret-like values, binaries, invalid skills, or conflicting snapshots. CLI/API entries are requirements only; no credentials, executable, environment file, provider configuration, or activation is captured.

## Review and commit

Run `git diff --check`, inspect `git diff --cached --name-only`, and stage only `personal-skills` and `skill-registry`. Commit only when the owner explicitly requested it:

```bash
python3 scripts/sync_registry.py --repo /Users/brandonparks/Documents/ChatGPT/coordinator --write --commit --message 'chore(skills): add personal skill source registry'
```

The helper refuses to commit when the index already contains unrelated entries. It does not delete or overwrite active sources. Exact content duplicates become aliases in the catalog; same-name divergent skills and semantic overlap remain `needs-owner-decision`.
