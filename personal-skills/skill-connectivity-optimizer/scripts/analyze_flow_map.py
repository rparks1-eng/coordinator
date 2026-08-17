#!/usr/bin/env python3
"""Read one exact flow map and selected SKILL.md contracts without execution."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
from collections import defaultdict
from pathlib import Path


def regular_absolute(path_text: str, label: str) -> Path:
    path = Path(path_text)
    if not path.is_absolute():
        raise ValueError(f"{label} must be an absolute path: {path_text}")
    try:
        info = path.lstat()
    except FileNotFoundError as exc:
        raise ValueError(f"{label} is missing: {path}") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise ValueError(f"{label} must be a regular non-symlink file: {path}")
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip('"')
    return values


def inventory_rows(text: str) -> list[dict[str, str]]:
    section = re.search(r"## Source inventory\n(.*?)(?:\n## |\Z)", text, re.S)
    if not section:
        return []
    rows: list[dict[str, str]] = []
    for line in section.group(1).splitlines():
        if not line.startswith("|") or "---" in line or "Skill |" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 5:
            rows.append({"name": cells[0].strip("`"), "source": cells[1], "status": cells[2].strip("`"), "sha256": cells[3].strip("`"), "path": cells[4].strip("`")})
    return rows


def parse_expected(entries: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for entry in entries:
        path_text, separator, digest = entry.rpartition("=")
        if not separator or not path_text or not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
            raise ValueError("expected contract hash must be ABSOLUTE_PATH=64_HEX_SHA256")
        result[str(regular_absolute(path_text, "expected contract path"))] = digest.lower()
    return result


def selected_contract(path_text: str, expected: dict[str, str]) -> dict[str, object]:
    path = regular_absolute(path_text, "contract")
    observed = sha256(path)
    metadata = frontmatter(path.read_text(encoding="utf-8", errors="replace"))
    expected_hash = expected.get(str(path))
    return {"path": str(path), "sha256": observed, "expected_sha256": expected_hash,
            "hash_match": expected_hash in (None, observed), "declared_name": metadata.get("name"),
            "declared_description": metadata.get("description"),
            "analysis_boundary": "metadata-only; body content is not executed or followed"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("map", help="Exact absolute Markdown flow-map path")
    parser.add_argument("--expected-map-sha256")
    parser.add_argument("--contract", action="append", default=[], help="Exact absolute SKILL.md path; repeatable")
    parser.add_argument("--expected-contract-sha256", action="append", default=[], metavar="PATH=SHA256")
    args = parser.parse_args()
    try:
        map_path = regular_absolute(args.map, "map")
        observed_map_hash = sha256(map_path)
        if args.expected_map_sha256 and args.expected_map_sha256.lower() != observed_map_hash:
            raise ValueError("map SHA-256 mismatch")
        expected_contracts = parse_expected(args.expected_contract_sha256)
        map_text = map_path.read_text(encoding="utf-8", errors="replace")
        metadata, rows = frontmatter(map_text), inventory_rows(map_text)
        groups: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            groups[row["name"]].append(row)
        payload = {
            "status": "advisory-input-analysis",
            "map": {"path": str(map_path), "sha256": observed_map_hash, "expected_sha256": args.expected_map_sha256,
                    "metadata": metadata, "inventory_rows": len(rows), "declared_edge_count": metadata.get("declared_edge_count"), "validation": metadata.get("validation")},
            "observations": {"duplicate_canonical_names": {name: entries for name, entries in groups.items() if len(entries) > 1},
                             "inactive_candidates": [row for row in rows if "inactive" in row["status"].lower() or "candidate" in row["status"].lower()],
                             "warning": "Map edges are static declarations unless separately tested; this output does not prove compatibility or authority."},
            "selected_contracts": [selected_contract(value, expected_contracts) for value in args.contract],
            "authority": "No skills were invoked, no files were written, and caller-supplied paths bound analysis scope only."}
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
