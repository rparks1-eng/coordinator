---
name: skill-first-aid-kit
description: Diagnose one or more local Codex skills and create one read-only prescription file per skill. Use when a user provides skill paths or names and wants to find broken metadata, references, scripts, runtime assumptions, safety risks, or unclear routing without changing the skills.
---

# Skill first aid kit

Inspect only the skills the user names. Read their instructions, resources, and executable source; do not execute the target skills or modify them.

1. Run the bundled diagnostic with one or more skill paths or installed skill names.

   ```bash
   python3 ~/.codex/skills/skill-first-aid-kit/scripts/diagnose_skills.py SKILL_PATH_OR_NAME [...]
   ```

2. Create one Markdown prescription per inspected skill in `~/.codex/skill-prescriptions/` by default. Use `--out PATH` only when the user requests another location.
3. Classify findings as trigger/metadata, routing/context, reference, syntax/contract, dependency/runtime, provider/auth, security, or regression/no-op. Tie each prescription to observed files and use the narrowest repair proposal.
4. Do not edit, install, update, promote, or execute a target skill. Ask for approval before any repair that needs credentials, billing, production access, or external code.
