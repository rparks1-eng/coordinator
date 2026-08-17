# Skill first-aid protocol

## Contents

1. Stabilize
2. Diagnose
3. Repair
4. Verify
5. Escalate

## 1. Stabilize

Do not reinstall or update first. Preserve the failing skill, exact request, error, runtime, active version, and last-known-good version. Disable only the failing route when practical; do not delete evidence or overwrite the active snapshot.

Run `scripts/skill_first_aid.py <skill-folder>` for inert structural checks. Use `--repair` only for its explicitly listed mechanical repairs. The script never downloads dependencies or executes the skill.

## 2. Diagnose

Classify the failure:

- **Trigger/metadata:** missing or invalid frontmatter, unclear description, stale `agents/openai.yaml`.
- **Routing/context:** the correct reference or script is not linked, instructions conflict, or context is oversized.
- **Reference:** broken relative link, missing template, duplicate source of truth.
- **Syntax/contract:** a bundled script cannot parse, arguments drifted, output schema changed.
- **Dependency/runtime:** an executable, library, environment feature, or platform assumption disappeared.
- **Provider/auth:** capability exists but current account access or authorization is absent.
- **Security:** new permission, network, credential, binary, hook, or provenance risk.
- **Regression/no-op:** the skill runs but no longer improves the acceptance test.

Reproduce the smallest failing check before editing. Do not call every failure a missing capability.

## 3. Repair

Apply the narrowest reversible repair in an isolated copy or worktree:

1. Fix local metadata, routing, references, or syntax before changing dependencies.
2. Preserve user modifications and the original evidence.
3. Do not weaken a safety gate merely to make a test pass.
4. If outside code is required, open a normal acquisition run and quarantine it.
5. If upstream fixed the defect, treat the newer revision as an update candidate, not an automatic patch.

## 4. Verify

Run, in order:

1. `skill_first_aid.py` again.
2. The skill-creator `quick_validate.py` check.
3. Bundled script unit tests with a minimal environment.
4. The original failing example from clean state.
5. At least one neighboring regression example.
6. Security preflight when executable content changed.

Compare the same acceptance evidence before and after. Promote only if the failure is fixed without creating a more serious regression.

## 5. Escalate

Stop and request a decision for credentials, billing, private-source access, license exceptions, production changes, weakened containment, or security `review`/`fail`. If repair is impossible, keep the last-known-good version active and produce a bounded replacement-capability task.
