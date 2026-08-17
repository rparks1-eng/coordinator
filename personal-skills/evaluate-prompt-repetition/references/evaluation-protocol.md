# Prompt repetition evaluation protocol

## Evidence boundary

The supplied knowledge source summarizes a preprint that reported benefits for exact full-prompt repetition in selected non-reasoning model/benchmark combinations. It is motivation for a test, not proof of a benefit in another model, workload, or provider version.

## Required evaluation record

| Field | Record |
| --- | --- |
| Decision question | One user-visible quality outcome and eligible workflow. |
| Frozen configuration | Provider, model/version, date, system/developer messages, tools, retrieval, sampling, response schema. |
| Example set | Selection rule, count, source approval, de-identification status, task segments. |
| Variants | Baseline `Q`; exact repeat `Q + Q`; length-matched inert padding. |
| Scoring | Predeclared rubric, blind scorer, handling of ties/failures. |
| Metrics | Quality, format/safety, input/output tokens, p50/p95 latency, errors, context headroom, estimated cost. |
| Decision | Reject, investigate, or limited flagged follow-up; exact rollback trigger. |

## Common confounders

- Input length: use a length-matched inert-padding control.
- Prompt order: record whether question appears before or after the context/options.
- Sampling and model drift: freeze settings and record the exact model/version/date.
- Rubric bias: blind scoring and retain raw outputs for review.
- Aggregate masking: inspect segment regressions and invalid structured output.
- Product mismatch: benchmark accuracy may not correspond to groundedness, safety, latency, tool use, or customer value.

## Initial decision rule

Only propose a limited flagged follow-up if the repeat arm delivers a decision-relevant quality improvement against both baseline and the length control, without unacceptable safety, format, cost, latency, context, or error regressions. Otherwise reject or investigate the specific unresolved cause. A new model or prompt-template version invalidates the prior conclusion until reevaluated.
