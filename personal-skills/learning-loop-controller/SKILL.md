---
name: learning-loop-controller
description: Route a user’s learning intent through Educator, Learning Path Binder, Librarian, and a governed skill-update planning gate using exact, stamped artifacts. Use when a user asks for a closed research-to-knowledge-to-improvement loop, wants learning outputs turned into a reviewable update plan, or needs a traceable handoff chain. This controller never selects targets automatically, approves candidates, sends messages, stages files, or installs skills.
---

# Learning Loop Controller

Create one bounded run per user intent; a loop means feedback can start a new linked run, not recursive self-modification. Use `$handoff-envelope` for every produced artifact and stop on any failed verification.

## Initialize and route

Run `scripts/init_learning_loop.py --intent "<user intent>"` in the chosen workspace. Preserve its `run_id` in every transit envelope.

1. Invoke `$educator` with the user intent. Stamp the resulting learning path as `learning-path`, producer `educator`, recipient `learning-path-binder`, step `path-created`.
2. Verify the path envelope, then invoke `$learning-path-binder` on that exact path. Stamp its binder as `research-binder`, producer `learning-path-binder`, recipient `librarian`, step `binder-created`, with the learning path as input and prior handoff.
3. Verify the binder envelope, then invoke `$librarian` on that exact binder. Stamp each knowledge file as `topic-knowledge`, producer `librarian`, recipient `learning-loop-controller`, step `knowledge-synthesized`, with its binder as input and prior handoff.
4. Produce one `update-plan` in the run directory from the verified knowledge. It must name supported findings, inferences, limitations, candidate target skills, proposed changes, tests, and `target-selection-required` status. Stamp it for `system-update`.

## Human gates and delivery lane

- Stop after the update plan until the user explicitly selects exact canonical target `SKILL.md` paths and an external inactive candidate root.
- Only then invoke `$system-update` with the exact plan/knowledge paths and targets. It creates inactive candidates only; freeze candidate/replacement hashes after static validation and do not transit-stamp or alter them.
- `$manifest` may create an optional delivery letter for review. It is never an approval manifest or Injector input.
- `$injector` may receive an inactive candidate only with its separately issued closed approval manifest. Its supported default is stage-only; active replacement remains a trusted-host gate.

## Re-entry and limits

Keep one artifact per stage per run, no inferred “latest” file, and a maximum depth of one research-to-plan pass. A stage receipt, rejection, or review finding can seed a **new** run only when the user supplies new intent or explicitly asks for a linked review. Do not auto-call Educator, System Update, or Injector from a receipt.

## Finish

Report the run ledger, exact artifacts, current truthful state, blocked gates, and the smallest reversible next action. The controller’s routing evidence never grants approval or delivery authority.
