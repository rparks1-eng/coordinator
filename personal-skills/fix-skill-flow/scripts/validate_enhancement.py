#!/usr/bin/env python3
"""Validate the structural contract of a fix-skill-flow enhancement outcome."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = (
    "# Skill Flow Enhancement",
    "## Outcome status",
    "## Target skill inventory",
    "## Integration question",
    "## Council synthesis",
    "## Proposed cohesive flow",
    "## Handoff and state contracts",
    "## Detailed implementation plan",
    "## Verification plan",
    "## Safety, authority, and human gates",
    "## Risks, dissent, and unresolved items",
    "## Next reversible step",
)

CANONICAL_QUESTION = (
    "How can these explicitly supplied skills be composed into one efficient, "
    "cohesive flow that completes all required handoffs without asking the user "
    "for ordinary text between steps, while preserving every skill's safety, "
    "authority, evidence, and approval gates?"
)


def validate(path: Path, expected_skills: list[str]) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"outcome does not exist: {path}"]
    if path.is_symlink() or not path.is_file():
        return [f"outcome must be a regular non-symlink file: {path}"]

    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append("missing YAML frontmatter")
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not frontmatter_match:
        errors.append("frontmatter is not closed")
        frontmatter = ""
    else:
        frontmatter = frontmatter_match.group(1)

    if not re.search(r"(?m)^status:\s*(proposal|partial|blocked)\s*$", frontmatter):
        errors.append("frontmatter status must be proposal, partial, or blocked")
    for field in ("created_at", "target_count", "council_run"):
        if not re.search(rf"(?m)^{field}:\s*\S.*$", frontmatter):
            errors.append(f"frontmatter is missing {field}")

    positions: list[int] = []
    for heading in REQUIRED_HEADINGS:
        matches = list(re.finditer(rf"(?m)^{re.escape(heading)}\s*$", text))
        if len(matches) != 1:
            errors.append(f"expected exactly one heading: {heading}")
        else:
            positions.append(matches[0].start())
    if positions and positions != sorted(positions):
        errors.append("required headings are out of order")

    normalized = text.replace("’", "'")
    if CANONICAL_QUESTION not in normalized:
        errors.append("canonical integration question is missing or changed")

    mermaid = re.findall(r"```mermaid\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if len(mermaid) != 1:
        errors.append("expected exactly one Mermaid block")
    elif not re.search(r"(?m)^\s*flowchart\s+(TD|TB|LR|RL|BT)\b", mermaid[0]):
        errors.append("Mermaid block must contain a flowchart declaration")
    elif "-->" not in mermaid[0] and "---" not in mermaid[0]:
        errors.append("Mermaid flowchart has no edges")

    lower = text.lower()
    for concept in ("automatic", "human-gate", "blocked", "static-inference", "rollback", "dissent"):
        if concept not in lower:
            errors.append(f"required concept is missing: {concept}")

    if not re.search(r"(?m)^\|.+\|.+\|$", text):
        errors.append("expected at least one Markdown contract or inventory table")
    if not re.search(r"`[^`]*(?:/|\.(?:md|py|js|ts|yaml|yml))[^`]*`", text):
        errors.append("implementation plan does not name a concrete file or path")

    for skill in expected_skills:
        if skill.casefold() not in text.casefold():
            errors.append(f"expected skill is absent from outcome: {skill}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("outcome", type=Path)
    parser.add_argument("--expected-skill", action="append", default=[])
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    outcome = args.outcome.expanduser().absolute()
    errors = validate(outcome, args.expected_skill)
    result = {"valid": not errors, "path": str(outcome), "errors": errors}
    if args.as_json:
        print(json.dumps(result, indent=2))
    elif errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
    else:
        print(f"VALID: {outcome}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
