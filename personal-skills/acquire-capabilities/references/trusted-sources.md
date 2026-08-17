# Trusted discovery and intelligence sources

## Principle

No repository, registry, directory, or scanner makes code inherently safe. Use these sources for provenance and vulnerability evidence, then run the full local security and sandbox gates. Do not bulk-download executable code for “future use.” Cache signed or hash-pinned metadata and advisory snapshots; fetch a candidate only for a defined acceptance test.

## Source order

1. Installed local skills, tools, and project primitives.
2. Official vendor documentation and the vendor's canonical source repository.
3. OpenAI-curated or Anthropic-official plugin/connector directories, treated as metadata rather than execution approval.
4. Official language registries with package provenance and exact-version pinning.
5. Well-maintained upstream open-source repositories with a clear license and security policy.
6. Other sources only after explicit review; never execute a search-result download directly.

GitHub hosting, stars, a verified badge, or a package-registry listing is not proof of safety. Reject typosquats, abandoned forks, shortened download links, unsigned repackaging, unclear ownership, missing licenses, and repositories whose requested privileges exceed their declared purpose.

## Local/offline security intelligence

Maintain snapshots outside product source and record source URL, retrieval time, version/commit, checksum, license, and expiry. Refresh deliberately; do not run a permanent updater with credentials.

- **GitHub Advisory Database**: canonical repository `https://github.com/github/advisory-database`, CC-BY-4.0. Clone or download a pinned snapshot; do not require its API.
- **OSV**: official scanner and distributed vulnerability data at `https://google.github.io/osv-scanner/`. Use its offline database mode after separately verifying the scanner release and SLSA provenance.
- **CISA Known Exploited Vulnerabilities**: official catalog and downloadable feeds under `https://www.cisa.gov/known-exploited-vulnerabilities-catalog`. Use it to prioritize known exploitation, not as a complete vulnerability list.
- **NVD data feeds**: official vulnerability feeds under `https://nvd.nist.gov/vuln/data-feeds`. Treat CVSS as one input, not an automatic decision.
- **ClamAV official signatures**: update only with `freshclam` from the official distribution network. CVD containers are digitally signed. Run `clamscan` locally with official databases only.

## Package and connector discovery

- JavaScript: `https://www.npmjs.com/` and `https://registry.npmjs.org/` for metadata and exact packages. Apply [npm-public-registry-policy.md](npm-public-registry-policy.md) before fetching or installing.
- Python: `https://pypi.org/` and verified project links.
- Rust: `https://crates.io/`.
- Go: canonical module source plus `https://pkg.go.dev/`.
- Java: `https://central.sonatype.com/`.
- MCP: official Model Context Protocol registry/directory pages and the server's canonical repository.
- Codex/ChatGPT: provider-reported `app/list` plus OpenAI's curated plugin sources.
- Claude: Anthropic's official connector/plugin directory plus the canonical server repository.

Registries are distribution channels, not allowlists. Inspect lifecycle scripts, bundled binaries, provenance, maintainers, dependencies, permissions, and network behavior before installation.

## Privacy-preserving search

Search only with generic capability terms, such as `local PDF renderer JavaScript Apache license`, never with user or project material. Do not include:

- Names, email addresses, account identifiers, or business records.
- Local paths or repository names.
- Prompts, source code, screenshots, or proprietary copy.
- Pairing tokens, API keys, cookies, auth files, environment variables, or hashes of secrets.

Store candidate metadata locally. Do not upload an unknown repository to an online scanner. If external reputation analysis would require transmitting the file or hash, request approval and explain the disclosure first.
