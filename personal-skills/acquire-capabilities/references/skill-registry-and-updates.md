# Skill registry and guarded updates

## Contents

1. Trust model
2. Registry structure
3. Initial acquisition
4. Update checks
5. Promotion and rollback

## 1. Trust model

Never execute a skill from a moving branch or live repository. The active unit is an immutable local snapshot tied to its canonical upstream URL, exact commit or package version, manifest hash, license, preflight evidence, benchmark, and approval decision.

A user-owned GitHub mirror is optional backup and patch storage. It is not a trust shortcut. Preserve both upstream and mirror provenance when a mirror is used.

Keep unapproved candidates outside every active skill-discovery root. A malicious `SKILL.md` can be an instruction attack even when its scripts never run.

## 2. Registry structure

Use this shape inside the target project or a dedicated private skill-registry repository:

```text
.coordinator/skills/
├── AGENTS.md
├── registry.yaml
├── installed/
│   └── <skill-id>/
│       ├── versions/<immutable-id>/
│       └── active.yaml
├── candidates/<update-run-id>/
├── update-checks/<skill-id>/<check-id>/
└── policies/
```

`registry.yaml` is a catalog, not a payload. Store detailed provenance and evidence beside each version. `active.yaml` names one approved immutable version. Changing that pointer is the promotion or rollback action.

Recommended lifecycle:

`discovered → source-cleared → quarantined → security-cleared → sandbox-tested → benchmarked → awaiting-approval → installed → active → superseded|revoked`

## 3. Initial acquisition

1. Search with generic terms through an approved internet/browser/GitHub tool.
2. Confirm the canonical upstream owner, URL, license, and exact pin.
3. Run `source_preflight.py`. Stop on `review` or `fail` pending a decision.
4. Fetch into `candidates/`, never `installed/` or a global skill root.
5. Run `security_preflight.py` while the candidate is inert. Stop on `review` or `fail`.
6. Create a snapshot manifest with `skill_snapshot.py`.
7. Sandbox and benchmark with no network, credentials, home access, or parent environment.
8. Present the evidence and request approval when activation changes trusted state.
9. Copy the exact accepted snapshot to `installed/<id>/versions/<immutable-id>/` and atomically update `active.yaml`.

## 4. Update checks

An update checker may run periodically only when the user has requested scheduling. Default to public, credential-free metadata checks. Private-source checks require explicit per-source read-only authorization.

For each active skill:

1. Read its recorded upstream and installed pin.
2. Check whether the canonical upstream advertises a newer immutable revision.
3. If unchanged, record only the check time and result.
4. If changed, run source preflight before fetching.
5. Fetch into a new candidate directory with hooks, global configuration, credentials, and inherited environment disabled.
6. Run security preflight before importing, building, interpreting, installing, or executing anything.
7. Produce file manifests and an old-versus-new diff.
8. Classify changes: instructions, references, scripts, dependencies, binaries, permissions, network behavior, and external side effects.
9. Rerun the same acceptance benchmark in isolation.
10. Write an update proposal. Never change `active.yaml` automatically.

Do not operate a permanent credentialed updater. Prefer a bounded scheduled check that writes an artifact and stops.

## 5. Promotion and rollback

Promotion requires exact provenance, passing gates, measurable benchmark improvement or a justified defect fix, compatible licensing, removal instructions, and human approval for material trust changes.

Retain at least the current and immediately previous approved snapshots. Rollback changes only `active.yaml`, then reruns the skill's health check and acceptance test. Revocation removes a version from activation eligibility but preserves its evidence record.
