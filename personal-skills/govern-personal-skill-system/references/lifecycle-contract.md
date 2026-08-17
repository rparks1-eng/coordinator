# Lifecycle contract

## Identity chain

For any active mutation, preserve this exact sequence:

`scoped evidence + baseline hash -> selected plan row -> inactive candidate hash -> candidate validation -> closed approval -> installer dry-run -> installer receipt -> post-install check -> rollback reference`

Every arrow is a gate. A missing, stale, mismatched, or ambiguous identity stops the route and produces a human decision.

## Specialist ownership

| Stage | Owner | Output or boundary |
| --- | --- | --- |
| Declared interaction map | `$visualize-skill-flow` | Read-only map; no target selection or update |
| Connectivity advice | `$skill-connectivity-optimizer` | Evidence-bound advisory report |
| Registry preflight and system audit | `$audit-personal-skill-system` | Audit and candidate-labelled plan; active skills unchanged |
| Material design disagreement | `$council-deliberation` | Advisory decision and dissent only |
| Selected plan execution | `$execute-skill-improvement-plan` | Exact inactive candidates; stops at approval pending |
| SKILL.md candidate compilation | `$system-update` | Inactive package only |
| Script/dependency repair candidate | `$acquire-capabilities` | Isolated, tested candidate; active snapshot preserved |
| One-file active installation | `$install-approved-skill-update` | Closed hash-bound approval, receipt, rollback |

## Required records

- Scope: exact workspace, input paths, and hashes.
- Evidence: static facts separately from inference and dissent.
- Candidate: exact source/destination mapping, baseline and candidate hashes, validation evidence, and unresolved gates.
- Approval: issuer, expiry, operation, candidate hash, destination, expected current hash, and rollback location.
- Completion: installer receipt, behavioral post-install check, and rollback reference.

## Consolidation evidence

Before proposing a merge, deletion, deprecation, or rename, demonstrate all of the following: equivalent trigger and input contracts; equivalent behavior on representative and held-out cases; no retained unique side effect, security boundary, or consumer; an explicit migration map; independently operable rollback; and owner approval. A same-name, similar description, or shared reference alone is not redundancy proof.

## Host automation boundary

Do not claim that a file-based workflow creates autonomous cross-chat orchestration. A host-level loop needs durable state, artifact identity, idempotency, scoped locking, retry/cancellation caps, cost and rate controls, least privilege, audit trail, human review, retention, and independent rollback. Without that contract, report the idea as `blocked-by-host-capability`.
