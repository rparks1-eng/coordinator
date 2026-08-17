---
name: governed-gap-to-skill-worker
description: Run one human-governed learning-to-skill episode for an explicitly named knowledge gap. Use when a user wants a dedicated worker to research a gap, evaluate whether an existing skill owns it, prepare an inactive candidate skill or improvement plan, and prepare a scoped personal-skill registry review. Never use for background monitoring, transcript capture, self-modification, automatic installation, automatic Git publication, or a gap that is not explicitly named.
---

# Governed Gap-to-Skill Worker

Run exactly one named gap per invocation. This is a sequential, artifact-based
worker—not a persistent agent or autonomous loop.

## Intake gate

Require: the exact gap, desired outcome, data classification, human owner, and
whether research may use public internet sources. If the gap is absent or the
classification is restricted without handling rules, stop and request it.

Create or select a dedicated run folder. Record only the de-identified gap
brief. Do not collect a chat transcript, secrets, credentials, private links,
or raw attachments.

## Learning lane

Invoke `learning-loop-controller` with the exact gap. Preserve its stamped
learning path, research binder, knowledge file, and update plan. The plan may
recommend an existing owner, a future isolated candidate, a product capability,
or no durable change; it does not select a target or authorize delivery.

## Ownership and evaluation gate

Before proposing a candidate skill, require three motivating cases, one held-out
neighbor, observable acceptance criteria, and a comparison against the best
existing owner. A missing executable, tool, provider, or verifier is a product
capability gap—not a skill-writing justification.

Use `council-deliberation` only when the ownership or architecture decision is
material and reversible. Preserve dissent and a no-candidate outcome.

## Candidate and repository gates

Only after the human selects an exact canonical target `SKILL.md` path and a
separate inactive candidate root may `system-update` prepare an inactive
candidate. Validate its hashes and tests. Do not change active skills.

Use `sync-personal-skill-registry` first in dry-run mode. A registry write,
commit, push, or draft PR requires a separate explicit user instruction naming
that desired action. Installation requires its own closed, hash-bound approval
manifest; this worker cannot issue one.

## Finish

Return the exact run artifacts, evidence status, ownership decision, candidate
status, blocked gates, and one smallest reversible next action. Read
`references/episode-contract.md` before creating a run.
