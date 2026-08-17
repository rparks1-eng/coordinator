# Evidence-gated skill self-optimization

Use this workflow when a skill is structurally inefficient, repeatedly misroutes, loads too much context, or underperforms the same task family. It diagnoses and proposes changes; it does not grant itself authority, credentials, network access, or a right to silently rewrite the active skill.

## Local diagnostic loop

1. Preserve the exact active skill with `scripts/skill_snapshot.py`.
2. Run `scripts/skill_efficiency_audit.py audit <skill-folder>`. This is an inert, network-free structural audit; it never executes the skill's scripts.
3. Classify each finding as metadata, routing, duplicate source of truth, broken reference, excessive context, behavioral failure, or missing executable capability.
4. Create an immutable candidate outside active skill roots. Change at most five files and 120 lines in one optimization step.
5. Forward-test the active and candidate snapshots on the same three or more tasks. Include at least one held-out neighboring task that did not motivate the edit. Capture task pass/fail, false completions, loaded words, tool calls, elapsed time, regressions, and security blockers.
6. Have an independent critic inspect the candidate and evidence. The author must not be the only judge.
7. Run `scripts/skill_efficiency_audit.py gate` with both audits and the comparison evidence. Bind evidence to the exact `content_manifest_sha256` values in both audits. Reject on quality regression, false-completion growth, security blockers, unbounded edits, malformed evidence, or no measured improvement.
8. Activate only the exact passing snapshot. Retain the previous snapshot and rollback pointer. Record rejected edits so the next attempt does not repeat them.

## What may change automatically

With explicit user authorization for the current local run, the engine may make and test low-risk candidate changes to descriptions, routing, broken local links, duplicated guidance, and reference layout. It must still keep the active snapshot unchanged until the gate passes. Dependency additions, executable changes, credentials, provider calls, hooks, schedules, production behavior, and external publication require their normal review and approval boundaries.

Do not schedule recursive self-rewrites. Trigger a new bounded run only after a real failure, three independent repetitions of the same inefficiency, a requested audit, or a material upstream change. Optimize one hypothesis at a time so causality remains interpretable.

## Restructuring rules

- Keep `SKILL.md` as the small router and move specialist detail into named on-demand references.
- Keep one durable home per fact; replace copies with links.
- Reach task-specific content within two routing reads.
- Separate stable policy from run evidence and generated reports.
- Rebuild generated indexes; never hand-edit them.
- Reduce context or tool calls only when correctness, security, and false-completion performance do not regress.
- Do not optimize toward a single benchmark screenshot, phrase, model, or seed.

## SkillOpt decision

Microsoft SkillOpt was evaluated as a method reference at canonical commit `9c776fcb51ae681c046d6f619b55e5f337d4f900` (MIT). Its useful ideas are bounded text edits, held-out validation, best-version selection, rejected-edit memory, and slower consolidation of repeated patterns. The repository itself is **not installed or executed** here: the local security preflight blocks automatic use because the repo includes credential access, schedulers/persistence examples, subprocess and network backends, provider dependencies, and test secret fixtures. Its standard runtime also expects model/provider access and therefore conflicts with this no-API, private-by-default path.

The local implementation is independent, standard-library-only, network-free, and narrower than SkillOpt. It audits structure and gates evidence supplied by real forward tests; it does not claim to reproduce Microsoft Research results.

Primary references:

- Microsoft Research, “SkillOpt: Agent skills as trainable parameters”: <https://www.microsoft.com/en-us/research/blog/skillopt-agent-skills-as-trainable-parameters/>
- Canonical source and MIT license: <https://github.com/microsoft/SkillOpt>
