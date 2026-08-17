---
name: mutation-custodian-cell
description: Execute one exact, separately approved mutation and return verification and rollback evidence. Use only when a coordinator work order includes a valid hash-bound approval artifact and a supported delivery contract; never approve, broaden, batch, or self-initiate changes.
---

# Mutation Custodian Cell

First read `$coordinator-core` and its work-order reference. Reject missing or expired approval, ambiguous targets, globs, multiple actions, changed hashes, or absent rollback.

Use only the named installer, injector, or staged delivery contract. Dry-run first when supported. Return the required host report with receipt and rollback path. Stop on every failed precondition; never publish, delete, install, or mutate outside the exact approval.
