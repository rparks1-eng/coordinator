#!/usr/bin/env python3
"""Emit a bounded metadata-only catalog of readable local skills."""
import argparse, hashlib, json
from pathlib import Path

DEFAULT_ROOTS = [Path("/Users/brandonparks/.codex/skills"), Path("/Users/brandonparks/.agents/skills"), Path("/Users/brandonparks/.codex/plugins/cache/personal")]

def frontmatter(text):
    if not text.startswith("---\n"): return None
    end = text.find("\n---", 4)
    if end < 0: return None
    fields = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"')
    return fields if fields.get("name") and fields.get("description") else None

def inactive(path):
    return any(part.lower() in {"osupdates", "system-updates", "replacement", "candidates"} for part in path.parts)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", action="append", type=Path)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    args = parser.parse_args()
    roots, skills, warnings = args.root or DEFAULT_ROOTS, [], []
    for root in roots:
        if not root.is_dir() or root.is_symlink():
            warnings.append(f"unreadable root: {root}"); continue
        for path in root.rglob("SKILL.md"):
            relative = path.relative_to(root)
            if path.is_symlink() or inactive(relative) or any(part.startswith(".") for part in relative.parts): continue
            try: raw = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                warnings.append(f"unreadable: {path}: {exc}"); continue
            data = frontmatter(raw)
            if not data:
                warnings.append(f"malformed: {path}"); continue
            skills.append({"name": data["name"], "description": data["description"], "path": str(path.resolve()), "sha256": hashlib.sha256(raw.encode()).hexdigest()})
    result = {"roots": [str(root) for root in roots], "count": len(skills), "skills": sorted(skills, key=lambda item: (item["name"], item["path"])), "warnings": warnings, "non_authority": "catalog-only; no execution, target selection, approval, or delivery"}
    print(json.dumps(result, indent=2) if args.format == "json" else "# Skill catalog\n\nCount: " + str(result["count"]))

if __name__ == "__main__": main()
