#!/usr/bin/env python3
"""Validate acquisition-source metadata locally without contacting the source."""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
from urllib.parse import urlsplit


HOSTS = {
    "github.com": "source-distribution",
    "docs.clamav.net": "security-documentation",
    "google.github.io": "security-documentation",
    "www.cisa.gov": "government-security-intelligence",
    "cisa.gov": "government-security-intelligence",
    "nvd.nist.gov": "government-security-intelligence",
    "www.npmjs.com": "package-registry",
    "registry.npmjs.org": "package-registry",
    "pypi.org": "package-registry",
    "files.pythonhosted.org": "package-distribution",
    "crates.io": "package-registry",
    "static.crates.io": "package-distribution",
    "pkg.go.dev": "package-documentation",
    "proxy.golang.org": "package-distribution",
    "central.sonatype.com": "package-registry",
    "repo1.maven.org": "package-distribution",
    "modelcontextprotocol.io": "protocol-documentation",
    "registry.modelcontextprotocol.io": "connector-registry",
    "developers.openai.com": "provider-documentation",
    "platform.openai.com": "provider-documentation",
    "code.claude.com": "provider-documentation",
    "claude.com": "provider-documentation",
}
FULL_COMMIT = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)
CHECKSUM = re.compile(r"^(?:sha256:)?[0-9a-f]{64}$", re.IGNORECASE)


def finding(severity: str, code: str, detail: str) -> dict[str, str]:
    return {"severity": severity, "code": code, "detail": detail}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--kind", required=True, choices=("official-doc", "git-repository", "package", "advisory-snapshot", "binary-release"))
    parser.add_argument("--commit")
    parser.add_argument("--version")
    parser.add_argument("--checksum")
    parser.add_argument("--license")
    parser.add_argument("--canonical-owner")
    parser.add_argument("--signature-verified", action="store_true")
    args = parser.parse_args()
    parts = urlsplit(args.url)
    findings: list[dict[str, str]] = []
    host = (parts.hostname or "").lower()
    if parts.scheme != "https":
        findings.append(finding("blocker", "non-https-source", "Only HTTPS sources may be fetched."))
    if parts.username or parts.password:
        findings.append(finding("blocker", "url-credentials", "Credentials in source URLs are forbidden."))
    if parts.query or parts.fragment:
        findings.append(finding("blocker", "url-query-or-fragment", "Queries and fragments can leak tokens or make provenance ambiguous."))
    if not host or host not in HOSTS:
        findings.append(finding("blocker", "unapproved-host", "Host is not in the local discovery catalog."))
    try:
        address = ipaddress.ip_address(host.strip("[]"))
        if address.is_private or address.is_loopback or address.is_link_local:
            findings.append(finding("blocker", "local-or-private-source", "Local and private network sources are forbidden for acquisition."))
    except ValueError:
        pass

    if args.kind == "git-repository":
        pieces = [piece for piece in parts.path.split("/") if piece]
        owner = pieces[0] if len(pieces) >= 2 else ""
        if host != "github.com" or len(pieces) < 2:
            findings.append(finding("blocker", "noncanonical-git-url", "Use the canonical GitHub owner/repository URL for this catalog."))
        if not args.canonical_owner or args.canonical_owner.lower() != owner.lower():
            findings.append(finding("high", "owner-unconfirmed", "Record and independently confirm the canonical upstream owner."))
        if not args.commit or not FULL_COMMIT.fullmatch(args.commit):
            findings.append(finding("high", "unpinned-commit", "Use a full 40-character commit hash, not a branch or tag alone."))
    if args.kind == "package":
        if not args.version or args.version.lower() in {"latest", "next", "main", "master"} or any(mark in args.version for mark in ("*", "^", "~", ">", "<")):
            findings.append(finding("high", "unfixed-version", "Use one exact immutable package version."))
    if args.kind in {"package", "advisory-snapshot", "binary-release"}:
        if not args.checksum or not CHECKSUM.fullmatch(args.checksum):
            findings.append(finding("high", "missing-checksum", "Record and verify a SHA-256 digest after download and before use."))
    if args.kind == "binary-release" and not args.signature_verified:
        findings.append(finding("high", "signature-unverified", "Verify release signature or SLSA provenance before execution."))
    if args.kind not in {"official-doc"} and not args.license:
        findings.append(finding("high", "license-unrecorded", "Record the exact applicable license before acquisition."))

    severities = {item["severity"] for item in findings}
    decision = "fail" if "blocker" in severities else "review" if "high" in severities else "pass"
    report = {
        "schema": 1,
        "decision": decision,
        "claim": "Source-metadata gate only; passing does not make downloaded code safe.",
        "host": host,
        "source_class": HOSTS.get(host, "unapproved"),
        "kind": args.kind,
        "findings": findings,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return {"pass": 0, "review": 2, "fail": 3}[decision]


if __name__ == "__main__":
    raise SystemExit(main())
