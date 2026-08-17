---
name: council-deliberation
description: Run a bounded six-seat deliberation with five independent contributor perspectives, complete cross-critique, author revisions, and one evidence-weighted CEO synthesis. Use when the user asks for a council, panel, multiple agents or personalities, debate, red-team review, five perspectives, all-to-all critique, or a synthesized decision; or when an important reversible architecture, capability, safety, or strategy decision materially benefits from documented disagreement. Do not invoke automatically for routine questions or mechanical edits.
---

# Council Deliberation

Produce independent thinking, traceable critique, and one decision without mistaking agreement for truth.

## Operating contract

1. Read `references/protocol.md` completely.
2. Choose `rapid-causal` mode for diagnosis or “what must be built” questions with a shared evidence packet. Choose `bounded` for broader architecture/strategy, and `full` only when explicitly requested or material risk justifies twenty critiques.
3. If durable artifacts are requested, initialize a run with `scripts/init_council_run.py` and write every phase to its designated folder.
4. Start the five contributors independently with the same bounded request and source packet. Batch drafts and critiques up to available agent capacity, waiting for a slot before starting another; preserve partial evidence if capacity does not recover within the configured cap. Do not reveal other drafts or a preferred conclusion.
5. Keep critiques append-only. In `rapid-causal`, critique only disputed causal claims and high-impact risks; batch assignments to available agent capacity. In other modes follow the review matrix.
6. Return material critiques to the affected author for one revision and change ledger. Do not revise an uncontested draft merely to satisfy ceremony.
7. Let the CEO Synthesizer see the source packet, revised drafts, ledgers, and disagreement matrix—not hidden chain-of-thought.
8. Weight evidence, constraints, and reversible tests above votes. Preserve unresolved dissent.
9. Stop on the configured round/time/token cap, repeated conclusions, no new evidence, a security issue, agent/thread capacity, or user interruption. Preserve partial evidence rather than retrying orchestration indefinitely.

Use real subagents only when the runtime exposes them and the user authorized the additional deliberation. If unavailable, run separated perspectives sequentially and label the result `single-model simulated council`; never claim independence that did not occur.

Council output is advisory. It cannot approve credentials, billing, external mutations, acquired-code execution, production changes, or another workflow's human gate.
