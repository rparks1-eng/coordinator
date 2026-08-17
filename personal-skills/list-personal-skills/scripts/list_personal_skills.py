#!/usr/bin/env python3
"""List readable personal skills without executing their contents."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Any


def default_roots() -> list[tuple[str, Path]]:
    user_home = Path.home()
    configured_codex = Path(os.environ.get("CODEX_HOME", user_home / ".codex"))
    candidates = [
        ("codex-personal", configured_codex / "skills"),
        ("codex-personal", user_home / ".codex" / "skills"),
        ("agents-shared", user_home / ".agents" / "skills"),
        ("personal-plugin", user_home / ".codex" / "plugins" / "cache" / "personal"),
    ]
    seen: set[Path] = set()
    result: list[tuple[str, Path]] = []
    for label, candidate in candidates:
        canonical = candidate.expanduser().resolve(strict=False)
        if canonical not in seen:
            seen.add(canonical)
            result.append((label, canonical))
    return result


def parse_frontmatter(path: Path) -> tuple[str | None, str | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return None, None, f"unreadable: {exc}"
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, None, "missing YAML frontmatter"
    end = next((index for index in range(1, len(lines)) if lines[index].strip() == "---"), None)
    if end is None:
        return None, None, "unterminated YAML frontmatter"

    values: dict[str, str] = {}
    for line in lines[1:end]:
        if line.startswith((" ", "\t")) or ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        value = raw_value.strip().strip('"\'')
        if key.strip() in {"name", "description"} and value not in {"", ">", "|"}:
            values[key.strip()] = value
    name = values.get("name")
    if not name:
        return None, values.get("description"), "missing frontmatter name"
    return name, values.get("description", ""), None


def discover(roots: list[tuple[str, Path]]) -> tuple[list[dict[str, Any]], list[str]]:
    skills: list[dict[str, Any]] = []
    warnings: list[str] = []
    for source, root in roots:
        if not root.is_dir():
            warnings.append(f"missing root: {root}")
            continue
        try:
            candidates = sorted(root.rglob("SKILL.md"))
        except OSError as exc:
            warnings.append(f"unreadable root {root}: {exc}")
            continue
        for candidate in candidates:
            try:
                relative = candidate.relative_to(root)
            except ValueError:
                warnings.append(f"outside root after discovery: {candidate}")
                continue
            if any(part.startswith(".") for part in relative.parts[:-1]):
                continue
            if not candidate.is_file():
                warnings.append(f"not a regular file: {candidate}")
                continue
            name, description, error = parse_frontmatter(candidate)
            if error:
                warnings.append(f"{candidate}: {error}")
                continue
            skills.append(
                {
                    "name": name,
                    "alias": candidate.parent.name,
                    "description": description or "",
                    "source": source,
                    "root": str(root),
                    "path": str(candidate.resolve(strict=False)),
                    "status": "resolved",
                }
            )

    name_counts: dict[str, int] = {}
    for skill in skills:
        name_counts[skill["name"]] = name_counts.get(skill["name"], 0) + 1
    for skill in skills:
        if name_counts[skill["name"]] > 1:
            skill["status"] = "duplicate-name-use-exact-path"
    skills.sort(key=lambda item: (item["name"].casefold(), item["path"]))
    return skills, warnings


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def render_markdown(
    roots: list[tuple[str, Path]], skills: list[dict[str, Any]], warnings: list[str]
) -> str:
    output = [
        "# Personal skill inventory",
        "",
        f"Count: {len(skills)}",
        "",
        "## Roots searched",
        "",
    ]
    output.extend(f"- `{root}` ({label})" for label, root in roots)
    output.extend(
        [
            "",
            "## Skills",
            "",
            "| # | Canonical name | Alias | Description | Source | Exact SKILL.md path | Status |",
            "| ---: | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for index, skill in enumerate(skills, start=1):
        output.append(
            f"| {index} | `{escape_cell(skill['name'])}` | `{escape_cell(skill['alias'])}` | "
            f"{escape_cell(skill['description'])} | {escape_cell(skill['source'])} | "
            f"`{escape_cell(skill['path'])}` | {escape_cell(skill['status'])} |"
        )
    output.extend(
        [
            "",
            "## Fix-skill-flow-ready targets",
            "",
            "Supply only the desired exact paths after `$fix-skill-flow`; each line below is an unambiguous target:",
            "",
        ]
    )
    output.extend(skill["path"] for skill in skills)
    output.extend(["", "## Warnings", ""])
    output.extend(f"- {warning}" for warning in warnings)
    if not warnings:
        output.append("- None.")
    body = "\n".join(output)
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    handoff = [
        "",
        "## Handoff v1",
        "",
        "- producer: `list-personal-skills`",
        "- artifact_path: `stdout (non-durable inventory)`",
        f"- content_sha256: `{digest}`",
        f"- created_at: `{datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}`",
        "- evidence_class: `static-inference`",
        "- non_authority: `inventory-only; no target selection, approval, or delivery authority`",
    ]
    return body + "\n" + "\n".join(handoff)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("markdown", "json", "paths"), default="markdown")
    parser.add_argument(
        "--root", action="append", type=Path, help="Use an explicit personal skill root; repeat as needed."
    )
    args = parser.parse_args()

    if args.root:
        roots = [("explicit", root.expanduser().resolve(strict=False)) for root in args.root]
    else:
        roots = default_roots()
    skills, warnings = discover(roots)

    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    if args.format == "paths":
        print("\n".join(skill["path"] for skill in skills))
    elif args.format == "json":
        payload = {
            "count": len(skills),
            "roots": [{"source": label, "path": str(root)} for label, root in roots],
            "skills": skills,
            "warnings": warnings,
        }
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
        payload["handoff"] = {
            "version": 1,
            "producer": "list-personal-skills",
            "artifact_path": "stdout (non-durable inventory)",
            "content_sha256": digest,
            "created_at": created_at,
            "evidence_class": "static-inference",
            "non_authority": "inventory-only; no target selection, approval, or delivery authority",
        }
        print(
            json.dumps(payload, indent=2)
        )
    else:
        print(render_markdown(roots, skills, warnings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
