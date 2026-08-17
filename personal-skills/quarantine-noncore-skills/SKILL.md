---
name: quarantine-noncore-skills
description: Create a recoverable, manifest-bound plan to remove noncore personal skills from Codex discovery by moving them into a local quarantine, with exact inventory, hashes, and restoration instructions. Use only after an owner-approved core profile and a tested staging/activation path exist. Never permanently delete skills, infer the core set, quarantine shared/plugin/system skills, or act without an explicit manifest and apply request.
---

# Quarantine Noncore Skills

Do not run this as the first step. Require a validated core profile, staged
package test, explicit list of direct personal skill folders, quarantine root,
and restore procedure. Default to a dry-run plan. `--apply` must move only exact
listed folders into a new timestamped quarantine and record hashes; it never
deletes them.

Put the reviewed manifest in a file and run:

```bash
python3 scripts/quarantine_skills.py --manifest /absolute/quarantine-manifest.json
```

After separately confirming the dry-run receipt, rerun that exact command with
`--apply`. The script rejects system skills, symlinks, inferred folder names,
and hash mismatches.

If any task uses a skill outside the core, stop and stage/activate it first.
Read `references/quarantine-contract.md`.
