#!/usr/bin/env python3
"""Validate the structural contract of a skill-connectivity recommendation report."""

from __future__ import annotations

import argparse
import json
import stat
from pathlib import Path


REQUIRED = [
    "# Skill Connectivity Recommendations",
    "## Input evidence",
    "## Static observations",
    "## Contract and handoff assessment",
    "## Prioritized improvements",
    "## Suggested execution orders",
    "## Troubleshooting routes",
    "## Automation and cross-chat requirements",
    "## Authority and safety",
    "## Verification",
    "## No-change option",
    "## Smallest reversible next step",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", help="Exact absolute report path")
    args = parser.parse_args()
    path = Path(args.report)
    errors: list[str] = []
    if not path.is_absolute():
        errors.append("report path must be absolute")
    else:
        try:
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
                errors.append("report must be a regular non-symlink file")
            else:
                text = path.read_text(encoding="utf-8", errors="replace")
                if "status: advisory-not-approval" not in text[:600]:
                    errors.append("frontmatter must declare status: advisory-not-approval")
                errors.extend(f"missing required section: {heading}" for heading in REQUIRED if heading not in text)
                lowered = text.lower()
                if "no execution" not in lowered or "no approval" not in lowered:
                    errors.append("authority section must state no execution and no approval")
        except FileNotFoundError:
            errors.append("report is missing")
    print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
