---
name: model-recommendation
description: Recommend and, where the active AI host exposes a supported control, apply the best available chat, coding, or reasoning model and effort for the current prompt. Use when choosing or changing a model/effort in ChatGPT, Codex, Claude, Claude Code, or another AI workspace; when assessing an AI-produced plan, diff, log, document, or repository; or when handing work to a new model or agent.
---

# Model Recommendation

Assess the actual work before selecting a model. Use the active prompt plus only the plans, files, diffs, logs, and repository instructions that materially affect scope. Do not equate a long prompt with a difficult task.

## Determine the host and controls

1. Identify the current AI host from its system context, UI metadata, or available tools. Do not infer it from the user mentioning a different product.
2. Discover the host's currently available model choices, effort/reasoning controls, and session or agent model-change control. Treat these live controls as authoritative; model names and availability change.
3. Classify the target:
   - **Current session**: change only if the host supplies a supported control.
   - **New agent or task**: select its model/effort only when creating or configuring that agent is already in scope.
   - **Recommendation only**: never mutate a session or create an agent.

Do not claim to have changed a model unless the control returned success and the active selection can be confirmed. If no control exists, provide the exact recommended available option and concise manual action. A subagent's model override does not change the user's current chat.

## Assess scope

Read the attached/current prompt first. Then inspect referenced artifacts proportionately and decide:

- **Task shape**: answer, edit, implementation, debugging, review, planning, research, or production-sensitive work.
- **Coupling**: isolated file or decision versus multiple systems, contracts, migrations, deployment, or hidden interactions.
- **Uncertainty**: clear requirements and a known path versus ambiguous intent, unfamiliar code, conflicting evidence, or need for diagnosis.
- **Risk**: reversible local work versus security, data, money, production, release, or broad user impact.
- **Verification burden**: a simple check versus tests, device runs, integration validation, or independent review.
- **Artifact quality**: completed and evidenced, partial but coherent, or inconsistent/missing evidence.

Ask one focused question only if an undiscoverable missing fact would materially change the tier. Otherwise state the assumption and continue.

## Choose a capability tier and effort

Map the assessment to the host's live choices. Prefer the least expensive option that comfortably covers the work; use a stronger model or effort for uncertainty and verification, not verbosity.

| Tier | Use for | Effort |
| --- | --- | --- |
| Fast | Formatting, extraction, straightforward explanation, narrow mechanical edits | low |
| Balanced | Bounded implementation or debugging with clear acceptance criteria | medium |
| Strong | Multi-file changes, non-obvious bugs, meaningful design/review, plans that require validation | high |
| Frontier | Security, production/release decisions, architecture, migrations, high ambiguity, or expensive mistakes | xhigh or the highest supported bounded effort |

When the host labels models differently, select the available model whose documented or UI-described capability matches the tier. For a coding task, favor the strongest suitable coding/agent model over a general chat model. For writing or synthesis, favor the suitable general reasoning/chat model. Do not name an unavailable model or invent an effort label.

Set the chosen effort one level lower when the task has a well-tested, repeatable path; set it one level higher when scope, correctness, or evidence is unclear. Reserve maximum effort for work where additional reasoning has a credible, material payoff.

## Apply and report

If the current host exposes a supported model/effort change operation, apply the chosen available values autonomously when the request authorizes a model recommendation or change. Preserve the user's explicit pin or budget limit. Confirm the resulting selection.

Return this compact decision record:

```text
Host: <detected host>
Target: <current session | new agent | recommendation only>
Recommendation: <exact available model> — <exact available effort>
Why: <one sentence tied to scope, uncertainty, risk, and verification>
Action: <applied and confirmed | unavailable; manual selection needed | intentionally not changed>
```

If artifacts show that the prior plan is incomplete, say what changed the recommendation. Do not treat a model recommendation as proof that the plan, tests, deployment, or approval gates have passed.
