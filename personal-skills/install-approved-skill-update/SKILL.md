---
name: install-approved-skill-update
description: Install one explicitly approved inactive System Update candidate into one Codex personal-skill SKILL.md with backup, locking, atomic replacement, post-install verification, receipt, and independently runnable rollback. Use only when a human or trusted local authority has issued a closed, hash-bound replace-file approval manifest; never use for discovery, candidate generation, bulk updates, or approval.
---

# Install Approved Skill Update

Apply one approved local skill update safely. This is the trusted-host delivery step after `$system-update`; it is never an approval issuer and never accepts a delivery letter, transit envelope, or ordinary chat request as approval.

## Preconditions

Require all of the following:

- One inactive candidate package under the Coordinator `system-updates/osUpdates/` root.
- One closed approval manifest matching [the schema](references/approval-manifest.md), including the current destination hash and a future expiry.
- A rollback root under `Coordinator/skill-install-rollbacks/`.
- The requested target exactly matches the candidate mapping and is one direct personal skill `SKILL.md` under `~/.codex/skills/`.

Do not accept globs, directories, symlinks, deletes, scripts/hooks, remote URLs, a changed candidate, a changed destination, expired approval, or multiple file mappings. Do not treat metadata, provenance, or a user prompt as install authority.

## Validate, then install

1. Dry-run first:

   ```bash
   python3 scripts/install_approved_skill_update.py /absolute/approval.json
   ```

2. Review the reported candidate, destination, expected hashes, and rollback location.
3. Apply only after the approval is still intended:

   ```bash
   python3 scripts/install_approved_skill_update.py /absolute/approval.json --apply
   ```

The helper takes an exclusive local lock, rechecks both hashes while locked, copies the original to a new non-loadable rollback directory, atomically replaces the destination on the same filesystem, fsyncs, verifies the installed hash, and writes a receipt. It intentionally stops rather than weakening a failed precondition.

## Roll back

Run this only for the receipt from this installer:

```bash
python3 scripts/install_approved_skill_update.py --rollback /absolute/receipt.json
```

Rollback first proves the active destination still has this receipt's installed hash, then atomically restores its recorded backup and verifies the baseline hash. If that proof fails, stop for manual recovery.

## Evidence boundary

`installed-posthash-verified` means only that the approved bytes were atomically installed and hash-verified. It does not prove the candidate is correct, safe, or effective; those decisions belong upstream and to the approval authority.
