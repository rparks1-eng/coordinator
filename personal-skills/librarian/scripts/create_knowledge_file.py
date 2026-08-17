#!/usr/bin/env python3
"""Reserve a unique topic-grouped Markdown knowledge file."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re
import unicodedata


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    return slug[:72] or "topic"


def reserve_path(directory: Path, topic: str) -> Path:
    topic_slug = slugify(topic)
    destination_directory = directory / topic_slug
    destination_directory.mkdir(parents=True, exist_ok=True)
    stem = f"{date.today().isoformat()}--{topic_slug}-knowledge"
    for number in range(1, 10_000):
        suffix = "" if number == 1 else f"-{number}"
        destination = destination_directory / f"{stem}{suffix}.md"
        try:
            with destination.open("x", encoding="utf-8") as handle:
                handle.write(f"# Knowledge: {topic}\n\n")
            return destination
        except FileExistsError:
            continue
    raise RuntimeError("Could not reserve a unique knowledge filename.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", required=True, help="Topic shown in the knowledge file title")
    parser.add_argument(
        "--directory",
        default="knowledge",
        help="Knowledge root (default: knowledge)",
    )
    args = parser.parse_args()
    print(reserve_path(Path(args.directory), args.topic).resolve())


if __name__ == "__main__":
    main()
