#!/usr/bin/env python3
"""Create a cold-startable ICM pipeline for one capability acquisition run."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


STAGES = (
    ("01_define", "Define the outcome, baseline, acceptance checks, and constraints."),
    ("02_inventory", "Map installed skills, tools, project primitives, and the exact gap."),
    ("03_discover", "Shortlist candidates from primary sources and record provenance."),
    ("04_evaluate", "Run inert security preflight; review provenance, license, maintenance, dependencies, vulnerabilities, permissions, privacy, cost, and sandbox plan."),
    ("05_sandbox", "Run pinned candidates in isolation and capture raw evidence."),
    ("06_integrate", "Implement the narrowest reversible adapter or product change."),
    ("07_verify", "Rerun the clean-state benchmark and make the promotion decision."),
)


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug or len(slug) > 64:
        raise ValueError("slug must contain 1-64 lowercase letters, digits, or hyphens")
    return slug


def write_new(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(content)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--objective", required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir() or root.is_symlink():
        raise SystemExit("root must be an existing, non-symlink directory")
    slug = safe_slug(args.slug)
    run = root / ".coordinator" / "capability-runs" / slug
    if run.exists():
        raise SystemExit(f"refusing to overwrite existing run: {run}")
    run.mkdir(parents=True)
    write_new(run / "AGENTS.md", f"""# Capability run: {slug}

Objective: {args.objective}

Read `CONTEXT.md`, then enter the first numbered stage without a completed `output/decision.md`. Read only that stage's `CONTEXT.md`, declared inputs, and linked references. Never install or execute a candidate outside `05_sandbox`. Never promote without `07_verify/output/decision.md`.
""")
    stage_lines = "\n".join(f"- `{name}/`: {job}" for name, job in STAGES)
    write_new(run / "CONTEXT.md", f"""# Capability acquisition pipeline

## Objective

{args.objective}

## Route

{stage_lines}

## State

Status is the first numbered stage lacking `output/decision.md`. Each decision links its evidence rather than copying it. Human approval is mandatory for paid services, credentials, external mutation, license exceptions, and production promotion.
""")
    previous = "user request and root CONTEXT.md"
    for name, job in STAGES:
        write_new(run / name / "CONTEXT.md", f"""# {name}

## Inputs

- {previous}
- `/Users/brandonparks/.codex/skills/acquire-capabilities/references/evaluation-policy.md` when assessing or promoting external capability
- `/Users/brandonparks/.codex/skills/acquire-capabilities/references/trusted-sources.md` during external discovery

## Process

{job}

## Outputs

- `output/decision.md`: conclusion, evidence links, unresolved risks, and next-stage instruction
- Put raw logs, manifests, screenshots, diffs, and scan reports under `evidence/`

## Human check

Confirm the conclusion follows from the linked evidence and no approval boundary was crossed.
""")
        (run / name / "output").mkdir()
        (run / name / "evidence").mkdir()
        previous = f"`../{name}/output/decision.md`"
    print(run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
