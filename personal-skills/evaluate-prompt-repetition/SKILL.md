---
name: evaluate-prompt-repetition
description: Design, run, or review a controlled evaluation of exact full-prompt repetition for an LLM task. Use when assessing whether transforming a non-reasoning prompt from Q to Q plus Q improves a specific workflow; when comparing prompt variants, model versions, quality, latency, token use, or safety/format regressions; or when preparing a reversible rollout recommendation. Do not use to enable repetition universally or to replace general model evaluation, security review, or deployment gates.
---

# Evaluate Prompt Repetition

Treat prompt repetition as a testable transformation, not a default. Read `references/evaluation-protocol.md` before designing or reviewing an evaluation.

## Set the decision boundary

1. Name one user-visible task and the quality outcome that matters.
2. Confirm the test is eligible: a bounded non-reasoning configuration, adequate context headroom, approved non-sensitive examples, and a baseline fallback.
3. State exclusions: reasoning-enabled calls, tool-heavy or retrieval-heavy workflows, near-limit prompts, sensitive data, or high-impact decisions require separate evidence before inclusion.
4. Freeze the model/version, system and developer instructions, tools, retrieval, sampling parameters, response schema, and scoring rubric.

Do not infer provider behavior, cost, cache behavior, or safety impact from a paper or another model.

## Run the minimum discriminating comparison

Use paired examples and exactly these initial variants:

- **Baseline:** `Q`
- **Repeat:** exact full prompt `Q + Q`
- **Length control:** `Q` plus inert padding matched to the repeat variant’s added length

Randomize run order, blind the scorer to variant, and retain raw inputs, outputs, and failures. Use at least 30 representative fixed examples as a screening set; do not present it as a statistical guarantee. Segment results by prompt length, context/question order, task family, model version, and reasoning mode if separately tested.

Record quality, format/schema compliance, safety outcomes, input/output tokens, p50/p95 latency, context headroom, error rate, and estimated cost. Investigate regressions and ties as carefully as wins.

## Interpret and recommend

Separate:

- **Observed result:** exact frozen configuration and paired outcomes.
- **Inference:** why a pattern might apply elsewhere.
- **Unknown:** untested prompt segments, provider changes, retrieval/tools, and operational effects.

Recommend only one of: **reject**, **investigate**, or **limited flagged follow-up**. A limited follow-up needs de-identified/approved data, an off-by-default flag, exposure cap, monitoring, baseline fallback, and predefined rollback conditions. This skill never authorizes production changes; invoke applicable production, security, privacy, or provider controls separately.

## Deliverable

Produce one concise evaluation record containing: decision question; eligibility/exclusions; frozen configuration; example selection; variant definitions; scoring rubric; paired results; segmented failure analysis; operational metrics; limitations; and the smallest reversible next step. Cite model/version and date so future readers do not mistake a past result for current behavior.

## Guardrails

- Do not duplicate sensitive, privileged, or user-provided content merely to run this technique.
- Do not treat an aggregate accuracy gain as sufficient when the workflow needs groundedness, structured output, tool reliability, privacy, or safety.
- Do not enable a variant universally, promote it broadly, or claim causal mechanism without application-specific evidence.
- Re-evaluate after a model, provider, prompt-template, tool, retrieval, or policy change.
