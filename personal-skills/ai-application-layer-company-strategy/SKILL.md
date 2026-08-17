---
name: ai-application-layer-company-strategy
description: Test and design an AI-enabled company around a measurable customer workflow rather than a generic model, agent, or harness. Use when Codex must select a customer wedge, conduct evidence-based discovery, compare fixed workflows with constrained agents, define outcome evaluations, or assess provider and governance dependencies for an AI product.
---

# AI Application-Layer Company Strategy

Treat “application layer” as a hypothesis, not an identity. Do not claim a company, moat, customer need, or market readiness without evidence.

## Start with the customer outcome

Create three one-page hypotheses. Each must name the role, recurring workflow, current workaround, measurable improved outcome, economic buyer, access path, permitted representative cases, and unacceptable failure.

Reject a hypothesis that is merely “uses agents,” has no buyer, has no measurable outcome, or relies only on market size or enthusiasm.

## Discover before building

Interview for recent concrete behavior: last instance, time/money/error cost, current tools and approvals, buyer, risk owner, switch condition, and pilot commitment. Treat interest as weak evidence. Strong evidence includes representative cases, named success criteria, data-access process, and a reversible paid or design-partner pilot.

Use [the discovery and evaluation rubric](references/workflow-rubric.md). Keep conclusions labeled as evidence, inference, or open hypothesis.

## Choose the least autonomy that works

Use a simple prompt, retrieval, deterministic logic, or fixed workflow first for defined and auditable work. Consider a constrained agent only when the path genuinely varies, feedback is available, the outcome can be checked, and the added autonomy improves a predeclared metric over the fixed baseline.

Do not build a generalized harness or multi-provider abstraction without a measured need. Record provider/model version, quality, latency, cost, data constraints, and fallback threshold.

## Build an evaluation asset

Before broadening a prototype, collect representative permitted cases and define graders. Measure completion, time, accuracy/error, rework/escalation, acceptance/override, cost per successful outcome, latency, reliability, and relevant privacy/safety failures. Compare the same cases against the existing workaround and any fixed-workflow baseline.

## Govern the workflow

Map every action as **suggest**, **draft**, **approve**, or **execute**. Define data origin/permitted use, human review, logging, incident/error correction, vendor dependencies, fallback, and user-visible limitations. Keep early pilots reversible and do not grant broad credentials or irreversible action authority to an agent.

## Deliverable

Produce a two-page opportunity memo: customer/workflow hypothesis, evidence and gaps, baseline, prototype scope, evaluation set and metric, autonomy decision, risks/controls, provider assumptions, pilot gate, and the next disconfirming test. State explicitly when no opportunity is yet validated.
