#!/usr/bin/env python3
"""Inventory skill frontmatter without loading skill bodies into context."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")[:32768]
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    result: dict[str, str] = {}
    for key in ("name", "description"):
        match = re.search(rf"(?m)^{key}:\s*(.+?)\s*$", text[4:end])
        if match:
            result[key] = match.group(1).strip().strip('"\'')
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("roots", nargs="+", type=Path)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = parser.parse_args()
    rows = []
    seen = set()
    for root in args.roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("SKILL.md")):
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            meta = frontmatter(path)
            if meta.get("name"):
                rows.append({"name": meta["name"], "description": meta.get("description", ""), "path": str(resolved)})
    rows.sort(key=lambda row: (row["name"].lower(), row["path"]))
    if args.format == "json":
        print(json.dumps(rows, indent=2))
    else:
        print("| Skill | Description | Path |")
        print("|---|---|---|")
        for row in rows:
            description = row["description"].replace("|", "\\|").replace("\n", " ")
            print(f"| `{row['name']}` | {description} | `{row['path']}` |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
