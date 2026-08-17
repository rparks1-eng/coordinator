---
name: acquire-capabilities
description: Detect, acquire, security-screen, repair, self-audit, optimize, restructure, version, update, validate, and integrate AI or software capabilities. Invoke implicitly—without requiring the user to name this skill—when an ordinary requested outcome is blocked by evidence that no adequate installed skill, tool, product primitive, provider path, or verifier exists. Also use for trusted-source discovery, quarantine, skill repair or optimization, immutable updates and rollback, capability-development tasks, measurable improvement, or a bounded council. Do not invoke merely for uncertainty, weak prompting, missing user input or authority, transient failure, or a fixable bug/no-op.
---

# Acquire Capabilities

For Wix draft staging, exact embedded-HTML synchronization, responsive preview verification, and address-search QA, route to `$wix-stage-preview-qa` after completing the normal capability inventory.

Turn “I cannot do this yet” into a bounded, evidence-backed capability run. Treat a skill as procedural knowledge, not executable power. Prefer adapting existing code and tools before acquiring anything new.

## Operating contract

1. For an outcome that may exceed installed abilities, read `references/capability-reflex.md`. The user need not know or name this skill.
2. Translate the request into a testable outcome and acceptance checks.
3. Inventory relevant installed skills, callable tools, local executables, provider-reported apps, project primitives, and security constraints.
   Route unresolved knowledge through `references/research-depth-router.md`; use the shallowest research tier that can support the decision.
4. Classify the gap using the taxonomy below and try the shortest existing-capability path first.
   When the user reports that prior fixes did not work, run the causal gate in `references/outcome-learning-loop.md` before another implementation.
5. If the gap is real, create a file-based capability run with `scripts/init_capability_run.py`.
6. Discover candidates from primary sources and run `scripts/source_preflight.py` before fetching. Prefer built-in code, then local/open-source tools, then account-included connectors, then paid services.
   For JavaScript packages, apply `references/npm-public-registry-policy.md`; a free public package never proves free operation or safe execution.
7. Run `scripts/security_preflight.py` before any install, import, build, hook, or execution.
8. Evaluate and sandbox candidates using `references/evaluation-policy.md`.
9. Integrate only the narrow adapter needed for the acceptance test.
10. Rerun the same test from clean state and compare evidence.
11. Promote only a measurable improvement. Record rejection reasons for failed candidates.
12. At completion, record routing/context/tool-call inefficiencies. If a real failure appears or the same inefficiency recurs three independent times, start the bounded self-optimization route without waiting for another prompt.
13. Close the outcome-learning loop in `references/outcome-learning-loop.md`; create a skill candidate only for a repeatable procedural gap, never as a substitute for missing product code.

Continue autonomously through read-only discovery, analysis, local scaffolding, tests, and reversible changes that the user requested. Pause for a decision before enabling billing, granting new credentials, publishing, weakening security, accepting restrictive licensing, or making an external mutation outside the requested scope.

## Workflow router

- **Implicit capability reflex:** read `references/capability-reflex.md`; decide `Proceed | Acquire | Ask/stop`, prevent re-entry, and return to the unchanged parent acceptance checks.
- **Prior fixes failed or the user challenges the diagnosis:** read `references/outcome-learning-loop.md`; distinguish causes with evidence before editing again.
- **Facts or candidate choices remain uncertain:** read `references/research-depth-router.md`; escalate from local evidence to targeted web research or deep multi-source research only when its trigger is met.
- **Acquire a missing capability:** follow this file, `references/trusted-sources.md`, and `references/evaluation-policy.md`.
- **Install or update a skill:** read `references/skill-registry-and-updates.md`. Activate only an immutable approved snapshot; never run directly from a live repository.
- **Repair a broken skill:** read `references/skill-first-aid.md` and run `scripts/skill_first_aid.py` before editing.
- **Diagnose, optimize, or restructure a skill:** read `references/self-optimization.md`, run `scripts/skill_efficiency_audit.py audit`, then forward-test and gate a bounded candidate before activation.
- **Compare two skill snapshots:** use `scripts/skill_snapshot.py`; treat its manifest and diff as evidence, not a safety verdict.
- **Council requested or required by the reflex predicate:** invoke `$council-deliberation`. It is advisory and cannot expand authority. Use real subagents only when the runtime exposes them and the user authorized the additional deliberation; otherwise label the sequential single-model fallback honestly.

## Gap taxonomy

- **Knowledge gap**: The executable capability exists, but the model lacks correct instructions. Create or update a skill/reference.
- **Routing gap**: The capability exists, but intent or tool selection is wrong. Fix routing and tests.
- **Primitive gap**: The product lacks a data type, renderer, scene primitive, or operation. Implement product code.
- **Adapter gap**: A provider/tool can do the work, but its events or outputs are not normalized. Build a narrow adapter.
- **Execution gap**: No installed executable can perform the operation. Evaluate a CLI, library, MCP server, or local service.
- **Provider gap**: Quality or compute requires an outside model/service. Probe account-included options; otherwise request approval with cost.
- **Verification gap**: Work may be produced but cannot be proven. Add deterministic checks and, where useful, independent semantic evaluation.
- **Bug/no-op gap**: The system falsely reports success or loses state. Fix this before adding capability.

Do not label a weak prompt as a missing tool. Do not label missing product code as a missing skill.

## Inventory

Run `scripts/inventory_skills.py` against the relevant skill roots. Also inspect callable tools and the target repository because installed skill metadata alone is not proof of execution.

For artifact creation and preview work, read `references/artifact-runtime-first-run.md`.

## Candidate discovery

Search primary sources first: official documentation, official package registries, and the upstream repository. Read `references/trusted-sources.md` before searching for external capability. Run `scripts/source_preflight.py` on the proposed source URL and pin before fetching it. Record candidate name, exact version/commit, capability, license, maintenance, provenance, dependencies, permissions, network behavior, expected cost, and sandbox plan.

Sanitize all discovery queries. Never include user names, project names, local paths, prompts, proprietary text, pairing tokens, keys, cookies, or repository contents. Search with generic capability terms. Do not call a remote package, vulnerability, or model API. Prefer local indexes, ordinary official web pages, and pinned read-only repository snapshots.

Use available internet search, browser, or read-only GitHub tools for public discovery when the environment provides them. A skill cannot grant network access by itself: if no approved internet tool is available, report that limitation instead of bypassing it. Public discovery needs no account credential. Access a private repository only after explicit user authorization with the narrowest read-only scope; never treat a connected account as blanket permission.

Do not bulk-import community skills. Search metadata before loading bodies, shortlist at most three candidates, and inspect only the files needed to assess the finalists. A repository containing prompts is not an executable capability. An MCP server is a connector, not proof that the underlying service is free or safe.

For a GitHub-hosted skill, preserve the canonical upstream URL and exact commit even when an approved snapshot is mirrored under the user's account. Ownership improves availability, not trust. A personal mirror may back up an accepted version or hold reviewed patches, but it never replaces the provenance and security gates.

## Skill updates and repair

Treat an updater as an update-candidate generator. It may check approved upstream metadata, pin a newer revision, produce a diff, and run the same preflight and benchmark gates. It must not silently alter the active skill. Keep candidate folders outside active skill search paths; promote by changing an explicit active-version pointer only after approval, and retain the prior version for rollback.

Repair locally before reacquiring. Diagnose whether failure is metadata, routing, broken references, syntax, tests, dependency drift, provider authentication, or a missing executable. Apply the smallest reversible patch and rerun the original failing check. If repair requires outside code, start a normal acquisition run rather than copying an unreviewed fix into the trusted skill.

## Self-optimization

Treat self-improvement as a bounded candidate experiment, never as permission for recursive mutation. Follow `references/self-optimization.md`. Diagnose locally first, change one hypothesis within the edit budget, compare the same forward tests plus a held-out task, and require no regression in correctness, false completion, security, or privacy. Context, tool-call, or time savings count only when quality is preserved. Keep rejected-edit evidence and the last-known-good snapshot.

The post-run diagnosis is automatic; activation is not. The engine may autonomously create, restructure, and test a local candidate when the trigger is met, but it must preserve the active snapshot until the evidence gate passes and must retain normal approval boundaries for executable, credential, provider, scheduled, external, or production changes.

## Council mode

Use `$council-deliberation` for the six-seat workflow. Council deliberation improves decisions, not executable power, and never bypasses this skill's source, security, cost, credential, sandbox, or human-approval gates.

## Safety and promotion

Follow `references/evaluation-policy.md`. Never execute newly discovered code in the main checkout first. Pin versions or commits. Run `scripts/security_preflight.py` while the candidate is inert. A `fail` or `review` result blocks automatic execution and promotion. Use an isolated worktree/container/process boundary with an empty/minimal environment, no credentials, no home-directory access, a dedicated writable directory, and no network by default. Scan dependencies and run the candidate's tests plus adversarial tests relevant to its permissions.

Never expose the user's shell environment to acquired code. Construct an explicit environment allowlist. Exclude all variables matching `*KEY*`, `*TOKEN*`, `*SECRET*`, `*PASSWORD*`, `*COOKIE*`, `*AUTH*`, and provider-specific credential names. Never mount or read `.ssh`, `.aws`, `.config`, `.codex`, `.claude`, browser profiles, keychains, Messages, pairing files, or the broader home directory.

Do not promise that any scanner makes code safe. Combine provenance, inert static inspection, signature scanning when locally available, dependency advisories, sandboxing, runtime network denial, behavioral tests, and removal/rollback. If a required layer is unavailable, fail closed for binaries and state the limitation.

Require all of the following before promotion:

- The baseline and rerun use the same acceptance test.
- Evidence is tied to the exact code and candidate version.
- The output visibly or deterministically improves.
- No critical security, license, privacy, or cost gate is unresolved.
- Removal and rollback are documented and tested.
- Human approval is retained for material production or paid-provider mutations.

If no safe/free path remains, stop with a precise capability task and decision options. Never fake the result.

## Durable run state

Initialize a run:

```bash
python3 scripts/init_capability_run.py --root <project> --slug <capability-slug> --objective "<testable objective>"
```

The generated pipeline is the audit state. Keep routing files short; store each fact once and link to it. Another model must be able to enter cold and determine current status within three reads.

## Completion report

Report the requested outcome, acceptance result, reused capabilities, gap classification, candidates considered, exact change, safety/cost result, baseline-versus-rerun evidence, rollback path, and remaining limitations.
