#!/usr/bin/env python3
"""Create a non-overwriting, non-active governance run record."""
from __future__ import annotations

import argparse
import re
from datetime import UTC, datetime
from pathlib import Path


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError("slug must contain at least one letter or digit")
    return slug[:64]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--mode", required=True, choices=("advisory-lifecycle", "mutation-lifecycle"))
    parser.add_argument("--objective", required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir() or root.is_symlink():
        raise SystemExit("--root must be an existing, non-symlink directory")
    run_id = f"{datetime.now(UTC):%Y%m%dT%H%M%SZ}-{safe_slug(args.slug)}"
    run = root / "skill-system-governance-runs" / run_id
    if run.exists():
        raise SystemExit(f"refusing to overwrite existing run: {run}")
    for relative in ("evidence", "decisions", "handoffs", "verification"):
        (run / relative).mkdir(parents=True, exist_ok=False)
    (run / "CONTEXT.md").write_text(
        "# Governance run\n\n"
        f"- Mode: `{args.mode}`\n"
        f"- Objective: {args.objective}\n"
        "- Status: `intake-recorded`\n"
        "- Authority: advisory until an existing specialist validates its own gate.\n",
        encoding="utf-8",
    )
    (run / "handoffs" / "README.md").write_text(
        "Record exact source and destination paths, SHA-256 values, owner, gate, and result for every handoff.\n",
        encoding="utf-8",
    )
    print(run)


if __name__ == "__main__":
    main()
