# npm public registry and zero-spend policy

## Classification

`https://www.npmjs.com/` and `https://registry.npmjs.org/` are approved primary sources for public JavaScript package metadata and exact-version distribution. They are distribution channels, not security allowlists.

The npm Free plan includes unlimited public packages at $0. This describes npm account hosting and registry access only. It does not prove that a package:

- is safe, maintained, correctly named, or open source;
- has a license suitable for the target project;
- avoids install scripts, native binaries, telemetry, persistence, or network access;
- can operate without credentials, a subscription, cloud infrastructure, or a metered third-party API.

## Zero-spend invariant

Default to no new chargeable action. Without a separate, explicit approval and a provider-enforced cost ceiling, do not:

- upgrade npm to Pro or Teams, create a paid organization, add paid seats, or enter payment information;
- purchase private-package access or use a paid/private registry;
- create a subscription, trial that auto-converts, paid cloud resource, or billable API credential;
- call an external service merely because its client package is free;
- treat a local environment flag as a substitute for a provider-side spending limit.

If a package needs an external provider, record the provider, authentication, free allowance, overage behavior, renewal behavior, and provider-side hard limit. If any cost fact is unresolved, keep the package inactive.

## Package gate

For a defined acceptance test only:

1. Read registry metadata without logging in: exact version, canonical repository, maintainers, license, integrity/provenance, release date, dependencies, binaries, and lifecycle scripts.
2. Confirm the canonical upstream and run `source_preflight.py` with the immutable version and verified SHA-256 before fetching.
3. Fetch into a candidate/quarantine directory with scripts disabled. Never install a discovered package globally or into the main checkout first.
4. Run `security_preflight.py` while inert. Inspect `preinstall`, `install`, `postinstall`, `prepare`, native build files, bundled executables, obfuscation, telemetry, credential access, persistence, and outbound network behavior.
5. Resolve license, vulnerability, privacy, and external-service cost findings before execution.
6. Sandbox with a minimal allowlisted environment, no credentials, no home-directory access, no network by default, and a dedicated writable directory.
7. Promote only the exact tested version when it measurably improves the original acceptance test and retains a documented rollback.

Automatic npm audit warnings and registry provenance are useful evidence, never a safety warranty.

## Account hygiene

- An npm account is not required to install public packages.
- Use two-factor authentication for publishing or account changes.
- Never expose npm tokens to candidate code or prompts.
- Never publish project files, prompts, assets, credentials, or private source as a public package.
- Use `npm publish --dry-run` and inspect the complete file list before any separately authorized publication.

## Cost decision

`free package download` and `free package operation` are independent checks. Both must pass before a candidate can be described as zero-cost.
