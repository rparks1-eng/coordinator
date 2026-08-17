#!/usr/bin/env python3
"""Move exact direct personal-skill folders into a recoverable quarantine."""
import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def tree_hash(folder: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(folder.rglob("*")):
        if item.is_symlink():
            raise ValueError(f"symlink not allowed: {item}")
        if item.is_file():
            digest.update(str(item.relative_to(folder)).encode() + b"\0")
            digest.update(hashlib.sha256(item.read_bytes()).digest())
    return digest.hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument("--manifest", required=True)
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

manifest_path = Path(args.manifest).resolve()
manifest = json.loads(manifest_path.read_text())
if manifest.get("schema_version") != 1 or not manifest.get("core_profile_sha256"):
    raise SystemExit("manifest must be schema version 1 and bind a core profile hash")
source_root = Path(manifest.get("source_root", "")).resolve()
quarantine_root = Path(manifest.get("quarantine_root", "")).resolve()
if not source_root.is_dir() or source_root.name != "skills":
    raise SystemExit("source_root must be an existing personal skills directory")
if source_root.parent.name != ".codex" or quarantine_root == source_root:
    raise SystemExit("source_root/quarantine_root are not allowed")
entries = manifest.get("skills")
if not isinstance(entries, list) or not entries:
    raise SystemExit("manifest must list one or more skills")

planned = []
seen = set()
for entry in entries:
    name = entry.get("folder") if isinstance(entry, dict) else None
    expected = entry.get("expected_tree_sha256") if isinstance(entry, dict) else None
    if not isinstance(name, str) or Path(name).name != name or name in {"", ".system"}:
        raise SystemExit("every folder must be a direct, non-system skill directory")
    if name in seen:
        raise SystemExit("skill folders must be unique")
    seen.add(name)
    folder = source_root / name
    if not folder.is_dir() or folder.is_symlink():
        raise SystemExit(f"not a direct non-symlink skill directory: {name}")
    actual = tree_hash(folder)
    if actual != expected:
        raise SystemExit(f"tree hash mismatch: {name}")
    planned.append({"folder": name, "tree_sha256": actual})

receipt = {
    "schema_version": 1,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "manifest": str(manifest_path),
    "core_profile_sha256": manifest["core_profile_sha256"],
    "source_root": str(source_root),
    "skills": planned,
    "applied": args.apply,
}
if args.apply:
    destination = quarantine_root / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination.mkdir(parents=True, exist_ok=False)
    for item in planned:
        shutil.move(str(source_root / item["folder"]), str(destination / item["folder"]))
    receipt["quarantine_directory"] = str(destination)
    (destination / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
