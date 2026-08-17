#!/usr/bin/env python3
"""Read-only, bounded file-composition evidence collector."""
import argparse, hashlib, json, re
from pathlib import Path

SKIP = {".git", ".venv", "node_modules", "__pycache__"}
MAX_BYTES = 512_000

def text_file(path):
    if path.is_symlink() or path.stat().st_size > MAX_BYTES: return None
    try: return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError): return None

def normalized(text):
    return re.sub(r"\s+", " ", text).strip().lower()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--root", action="append", type=Path, dest="extra")
    parser.add_argument("--format", choices=("json",), default="json")
    parser.add_argument("--near-threshold", type=float, default=.88)
    parser.add_argument("--near-limit", type=int, default=64)
    args = parser.parse_args()
    roots = [args.root, *(args.extra or [])]
    files, warnings = [], []
    for root in roots:
        if not root.is_dir() or root.is_symlink(): warnings.append(f"unreadable root: {root}"); continue
        for path in root.rglob("*"):
            if not path.is_file() or path.is_symlink() or any(part in SKIP for part in path.relative_to(root).parts): continue
            text = text_file(path)
            if text is None: continue
            clean = normalized(text)
            files.append({"path": str(path.resolve()), "sha256": hashlib.sha256(text.encode()).hexdigest(), "bytes": len(text.encode()), "normalized": clean, "tokens": set(re.findall(r"[a-z0-9]{3,}", clean)), "inactive": any(part.lower() in {"candidates", "replacement", "osupdates", "system-updates"} for part in path.parts)})
    exact = {}
    for item in files: exact.setdefault(item["sha256"], []).append(item["path"])
    findings = [{"kind":"exact-duplicate", "paths":paths, "evidence":"same-sha256"} for paths in exact.values() if len(paths) > 1]
    near_files = sorted(files, key=lambda item: item["bytes"], reverse=True)[:args.near_limit]
    if len(files) > len(near_files): warnings.append(f"near-duplicate scan limited to {len(near_files)} largest readable files; exact hashes cover all {len(files)} files")
    for index, left in enumerate(near_files):
        for right in near_files[index + 1:]:
            if left["sha256"] == right["sha256"] or not left["tokens"] or not right["tokens"]: continue
            ratio = len(left["tokens"] & right["tokens"]) / len(left["tokens"] | right["tokens"])
            if ratio >= args.near_threshold: findings.append({"kind":"near-duplicate-candidate", "paths":[left["path"], right["path"]], "similarity":round(ratio, 3), "evidence":"token-jaccard-heuristic"})
    print(json.dumps({"roots":[str(r) for r in roots], "files":[{k:v for k,v in item.items() if k not in {"normalized", "tokens"}} for item in files], "findings":findings, "warnings":warnings, "non_authority":"read-only evidence; no canonical selection, deletion, copy, move, or approval"}, indent=2))

if __name__ == "__main__": main()
