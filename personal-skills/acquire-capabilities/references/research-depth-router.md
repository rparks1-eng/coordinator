# Research depth router

Use research to close a decision-relevant knowledge gap, not to postpone local diagnosis. A skill does not create network access; use only internet tools the host already exposes.

## Choose the shallowest sufficient tier

### Tier 0 — local evidence

Use repository code, tests, logs, installed skill metadata, and tool/runtime probes when the question is about the current workspace or a reproducible defect. Do not browse merely because the answer is uncertain. A local bug with direct evidence is a product-code task, not a research project.

### Tier 1 — targeted research

Search or open one to three primary or authoritative sources when a fact may have changed, an official interface/version must be confirmed, a candidate's provenance or license is unknown, or local evidence identifies a narrow external question. Stop when the acceptance decision is supported. Record source, date, exact claim, and remaining uncertainty.

### Tier 2 — deep research

Use a bounded multi-source investigation when at least one condition holds:

- the user explicitly requests deep research;
- the decision is materially consequential in security, privacy, legal, medical, financial, production, or substantial cost/time terms and uncertainty remains;
- a capability choice spans multiple systems or vendors and requires comparing architecture, maintenance, licensing, permissions, and cost;
- targeted primary sources conflict or leave a core acceptance criterion unresolved;
- a novel or fast-moving topic has no single authoritative source.

Define the research question and stop conditions first. Prefer primary sources, then independent authoritative analysis. Compare at least three relevant sources when available, separate sourced facts from inference, note contradictions, and end with a decision tied to the original acceptance checks. Deep research is not permission to fetch or execute code.

## Do not escalate when

- the missing fact can be obtained by inspecting or testing the local system;
- the user must supply intent, credentials, authority, or a material choice;
- the blocker is a fixable bug, missing product primitive, or failed verification;
- more sources would not change the decision;
- research would expose private context in a query.

## Capability-acquisition boundary

Sanitize every query. Never include private prompts, names, paths, repository contents, credentials, tokens, or proprietary terms. Before fetching an external candidate, return to `references/trusted-sources.md` and run `scripts/source_preflight.py`. Before install, build, hook, interpreter use, or execution, run `scripts/security_preflight.py`. `review` or `fail` stops automatic continuation.

Record the chosen tier and why. On completion, record whether the research changed the candidate list or decision; if it did not, treat repeated unnecessary escalation as an efficiency failure for the self-optimization loop.
