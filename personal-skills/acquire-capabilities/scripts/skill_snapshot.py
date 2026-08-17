#!/usr/bin/env python3
"""Create and compare inert, content-addressed skill manifests without execution."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


EXCLUDED = {".git", "__pycache__", ".DS_Store"}
MAX_FILES = 5000
MAX_BYTES = 512 * 1024 * 1024


def write_new(path: Path | None, value: dict[str, object]) -> None:
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if path is None:
        print(rendered, end="")
        return
    if path.exists() or path.is_symlink():
        raise SystemExit(f"refusing to overwrite output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8")


def snapshot(root: Path, source_url: str | None, source_ref: str | None) -> dict[str, object]:
    root = root.absolute()
    if root.is_symlink() or not root.is_dir():
        raise SystemExit("skill root must be a real directory")
    files: dict[str, dict[str, object]] = {}
    total = 0
    for directory, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        base = Path(directory)
        dirnames[:] = sorted(name for name in dirnames if name not in EXCLUDED)
        for name in sorted(filenames):
            if name in EXCLUDED:
                continue
            path = base / name
            rel = path.relative_to(root).as_posix()
            if path.is_symlink() or not path.is_file():
                raise SystemExit(f"refusing special or symlinked file: {rel}")
            size = path.stat().st_size
            total += size
            if len(files) >= MAX_FILES or total > MAX_BYTES:
                raise SystemExit("skill exceeds snapshot safety limits")
            digest = hashlib.sha256()
            with path.open("rb") as handle:
                while chunk := handle.read(1024 * 1024):
                    digest.update(chunk)
            files[rel] = {"bytes": size, "sha256": digest.hexdigest(), "executable": bool(path.stat().st_mode & 0o111)}
    manifest_basis = json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    return {
        "schema": 1,
        "skill": root.name,
        "source_url": source_url,
        "source_ref": source_ref,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": files,
        "file_count": len(files),
        "total_bytes": total,
        "manifest_sha256": hashlib.sha256(manifest_basis).hexdigest(),
    }


def compare(before: dict[str, object], after: dict[str, object]) -> dict[str, object]:
    old = before.get("files", {})
    new = after.get("files", {})
    if not isinstance(old, dict) or not isinstance(new, dict):
        raise SystemExit("manifest files field must be an object")
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = sorted(name for name in set(old) & set(new) if old[name] != new[name])
    return {
        "schema": 1,
        "decision": "changed" if added or removed or changed else "unchanged",
        "before_manifest": before.get("manifest_sha256"),
        "after_manifest": after.get("manifest_sha256"),
        "added": added,
        "removed": removed,
        "changed": changed,
        "claim": "Content diff only; this is not a security or compatibility verdict.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    snap = sub.add_parser("snapshot")
    snap.add_argument("skill_folder", type=Path)
    snap.add_argument("--source-url")
    snap.add_argument("--source-ref")
    snap.add_argument("--output", type=Path)
    diff = sub.add_parser("compare")
    diff.add_argument("before", type=Path)
    diff.add_argument("after", type=Path)
    diff.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "snapshot":
        write_new(args.output, snapshot(args.skill_folder, args.source_url, args.source_ref))
    else:
        before = json.loads(args.before.read_text(encoding="utf-8"))
        after = json.loads(args.after.read_text(encoding="utf-8"))
        write_new(args.output, compare(before, after))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
