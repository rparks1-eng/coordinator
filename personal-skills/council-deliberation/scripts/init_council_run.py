#!/usr/bin/env python3
"""Create a cold-readable council run without overwriting existing work."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SAFE_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def initialize(root: Path, slug: str, mode: str, request: str) -> Path:
    if not SAFE_SLUG.fullmatch(slug):
        raise ValueError("slug must be lowercase hyphen-case")
    run = root.absolute() / slug
    if run.exists() or run.is_symlink():
        raise FileExistsError(f"refusing to overwrite existing run: {run}")
    for relative in ("input", "01_drafts", "02_critiques", "03_revisions", "04_synthesis"):
        (run / relative).mkdir(parents=True, exist_ok=True)
    context = f"""# Council run: {slug}

Mode: `{mode}`

## Route

1. Read `input/request.md` and `input/sources.md`.
2. Five independent drafts go to `01_drafts/`.
3. Append-only critiques go to `02_critiques/`.
4. Author revisions and ledgers go to `03_revisions/`.
5. The disagreement matrix and CEO decision go to `04_synthesis/`.

## Human check

Confirm the decision preserves dissent, cites evidence, respects external approval gates, and names the next reversible test.
"""
    (run / "CONTEXT.md").write_text(context, encoding="utf-8")
    (run / "input" / "request.md").write_text(request.rstrip() + "\n", encoding="utf-8")
    (run / "input" / "sources.md").write_text("# Sources\n\nAdd the bounded source packet here.\n", encoding="utf-8")
    return run


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--mode", choices=("bounded", "full"), default="bounded")
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    print(initialize(args.root, args.slug, args.mode, args.request))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
