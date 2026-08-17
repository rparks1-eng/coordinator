# Episode contract

## State machine

`named-gap → research → ownership-decision → evaluation → target-selection →
inactive-candidate → validation → registry-dry-run → explicit-publication-gate`

Only the first four stages are available by default. Target selection, candidate
creation, registry writing, Git actions, and installation each require their
separate gate.

## Required outputs

- de-identified gap brief;
- learning path, binder, knowledge, and update plan;
- ownership decision with candidate/no-candidate rationale;
- motivating/held-out evaluation dossier;
- if selected, inactive candidate hash and validation report;
- registry dry-run report only.

## Correct abstention

Return `needs-human-review`, `no-skill-warranted`, or
`product-capability-required` whenever evidence does not justify a reusable
skill.
