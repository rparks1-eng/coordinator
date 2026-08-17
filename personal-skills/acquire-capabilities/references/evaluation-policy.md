# Capability candidate evaluation policy

## Contents

1. Evidence record
2. Source and license
3. Maintenance and reputation
4. Dependency and vulnerability review
5. Permission and data-flow review
6. Sandbox trial
7. Benchmark and promotion

## 1. Evidence record

Create one record per candidate. Include exact package version or commit, upstream URL, retrieval date, checksums where available, reviewer, and decision. Never assess an unpinned moving branch as the promotion unit.

Before fetching, run `/Users/brandonparks/.codex/skills/acquire-capabilities/scripts/source_preflight.py` against the proposed URL and immutable pin. This gate rejects credential-bearing URLs, query strings, non-HTTPS or unapproved hosts, floating versions, and missing provenance fields. Passing establishes source metadata only, not code safety.

## 2. Source and license

- Prefer official repositories and registries.
- Confirm the repository owner matches the advertised project.
- Read the actual license file and package metadata.
- Check whether code, model weights, bundled assets, and plugins carry different licenses.
- Reject unclear provenance for executable code.
- Flag copyleft or noncommercial restrictions for a product-distribution decision; do not silently assume compatibility.

## 3. Maintenance and reputation

Record release recency, commit activity, security policy, maintainer identity, issue responsiveness, signed releases if available, and deprecation status. Popularity is supporting evidence, not a security property.

## 4. Dependency and vulnerability review

- Inspect install scripts and lifecycle hooks before installation.
- Enumerate direct and transitive dependencies.
- Run the ecosystem's audit and a source/security scanner when available.
- Compare findings to the target repository's baseline; do not hide inherited findings.
- Reject packages that require broad privilege for a narrow capability.

## 5. Permission and data-flow review

Document required filesystem roots, subprocesses, environment variables, credentials, network domains, listening ports, telemetry, retained data, and external side effects. Default-deny everything not necessary for the benchmark.

Never expose the parent shell environment wholesale. Use an allowlist. Never transmit source, prompts, artifacts, or credentials unless the user approved that provider and data flow.

Run `/Users/brandonparks/.codex/skills/acquire-capabilities/scripts/security_preflight.py` before the candidate enters a package manager, build system, hook runner, interpreter, or compiler. Preserve its JSON report with the candidate evidence. A `fail` or `review` decision blocks automatic continuation.

Treat install scripts, executable hooks, unsigned binaries, symlink escapes, archive traversal, secret-like material, credential-path access, persistence mechanisms, browser/keychain access, hidden network clients, obfuscation, and subprocess launch as explicit findings. Review requested behavior against the declared capability; reject unrelated privilege.

## 6. Sandbox trial

Test in a disposable worktree, container, VM, or tightly restricted subprocess before integration. Use a constructed environment containing only essential locale/runtime variables, bounded input/output, resource limits, no network by default, a dedicated writable directory, no personal credentials, and representative malformed or hostile inputs. Do not mount the user's home directory. Record every granted path, executable, environment variable, and host.

Capture commands, logs, hashes, outputs, and cleanup result. Do not promote a candidate that cannot be removed cleanly.

## 7. Benchmark and promotion

Use the same clean-state task before and after integration. Separate instruction adherence from target similarity and subjective quality. Require deterministic checks appropriate to the artifact plus human or independent visual review where semantics matter.

Promotion is a proposal until all required gates pass. Paid services, new account creation, public hosting, production credentials, or broad external writes always require explicit user approval. Malware or vulnerability scanning is evidence, not a warranty; retain rollback and do not promote unexplained behavior.
