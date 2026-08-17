#!/usr/bin/env python3
"""Safely refresh and optionally publish the direct personal-skill registry."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_ROOT = Path("/Users/brandonparks/.codex/skills")
INVENTORY = DEFAULT_ROOT / "list-personal-skills/scripts/list_personal_skills.py"
APPROVED_REMOTE = "https://github.com/rparks1-eng/coordinator.git"
TEXT = {".md", ".py", ".js", ".mjs", ".ts", ".json", ".yaml", ".yml", ".toml", ".txt", ".svg"}
ALLOWED = TEXT | {".png", ".jpg", ".jpeg", ".webp"}
SECRET = re.compile(r"(?:-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\b(?:sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,}|AIza[A-Za-z0-9_-]{20,})\b|(?i:(?:api[_-]?key|secret|token|password)\s*[:=]\s*[\"']?[A-Za-z0-9_-]{12,}))")
CLI = re.compile(r"(?<![\w.-])(python3|node|npm|npx|git|gh|yt-dlp|ollama|pdftotext|ffmpeg)(?![\w.-])")
API = re.compile(r"\b([A-Z][A-Z0-9_]*(?:API|TOKEN|KEY))\b")


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def run(*args, cwd=None, check=True):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if check and result.returncode:
        fail(result.stderr.strip() or result.stdout.strip() or "command failed")
    return result


def git(repo, *args, check=True):
    return run("git", "-C", str(repo), *args, check=check)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_text(path):
    data = path.read_bytes()
    if b"\0" in data:
        fail(f"binary text file: {path}")
    try:
        value = data.decode("utf-8")
    except UnicodeDecodeError:
        fail(f"non-UTF-8 text file: {path}")
    if SECRET.search(value):
        fail(f"secret-like value: {path}")
    return value


def source_files(skill):
    result = []
    for current, dirs, names in os.walk(skill, followlinks=False):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in {"__pycache__", "node_modules"}]
        for name in names:
            path = Path(current) / name
            if path.parent.name == "scripts" and name.startswith("test_"):
                continue
            if path.is_symlink() or not path.is_file():
                fail(f"non-regular source: {path}")
            if path.suffix.lower() not in ALLOWED and path.name not in {"LICENSE", "NOTICE"}:
                fail(f"unsupported or binary source: {path}")
            if path.suffix.lower() in TEXT:
                read_text(path)
            result.append(path)
    return sorted(result)


def declared_name(skill):
    for line in read_text(skill / "SKILL.md").splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip('"')
    fail(f"missing name frontmatter: {skill / 'SKILL.md'}")


def inventory(root):
    if not INVENTORY.is_file():
        fail(f"inventory helper missing: {INVENTORY}")
    payload = run("python3", str(INVENTORY), "--format", "json").stdout
    items = json.loads(payload).get("skills", [])
    selected = []
    for item in items:
        path = Path(item["path"]).resolve()
        if path.parent.parent == root and path.name == "SKILL.md":
            selected.append(path.parent)
    return sorted(set(selected))


def build_snapshot(root, output):
    records, adapters, snapshots = [], {}, {}
    for skill in inventory(root):
        files = source_files(skill)
        hashes = {str(path.relative_to(skill)): digest(path) for path in files}
        tree = hashlib.sha256("".join(hashes[key] for key in sorted(hashes)).encode()).hexdigest()
        skill_id = skill.name
        snapshots[skill_id] = files
        records.append({
            "id": skill_id,
            "declared_name": declared_name(skill),
            "origin": str(skill),
            "tree_sha256": tree,
            "files": hashes,
            "status": "captured",
            "duplicate_of": None,
        })
        requirements = []
        for path in files:
            if path.suffix.lower() not in TEXT:
                continue
            text = read_text(path)
            for number, line in enumerate(text.splitlines(), 1):
                commands = sorted(set(CLI.findall(line)))
                variables = sorted(set(API.findall(line)))
                if commands or variables:
                    requirements.append({"file": str(path.relative_to(skill)), "line": number, "commands": commands, "environment_names": variables, "evidence_class": "heuristic"})
        adapters[skill_id] = {"findings": requirements, "credentials": "not included", "activation_status": "not projected"}
    seen = {}
    for record in records:
        if record["tree_sha256"] in seen:
            record["status"] = "alias"
            record["duplicate_of"] = seen[record["tree_sha256"]]
        else:
            seen[record["tree_sha256"]] = record["id"]
    catalog = {
        "schema_version": 2,
        "captured_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_root": str(root),
        "skills": records,
        "excluded_roots": ["shared-agent", "plugin-cache", "Coordinator candidates", "ChatGPT/Git worktrees pending provenance review"],
    }
    snapshots_dir = output / "personal-skills"
    for record in records:
        if record["status"] == "alias":
            continue
        skill_id = record["id"]
        source = root / skill_id
        for path in snapshots[skill_id]:
            destination = snapshots_dir / skill_id / path.relative_to(source)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
    registry = output / "skill-registry"
    registry.mkdir(parents=True, exist_ok=True)
    (registry / "catalog.json").write_text(json.dumps(catalog, indent=2) + "\n")
    (registry / "adapter-requirements.json").write_text(json.dumps(adapters, indent=2) + "\n")
    (registry / "CONTEXT.md").write_text("# Personal skill registry\n\nPortable source snapshots and declarative adapter requirements. This directory does not activate skills.\n")
    return records


def changed_paths(repo, staging, active_ids):
    paths = []
    expected = set()
    for path in sorted(staging.rglob("*")):
        if path.is_dir():
            continue
        relative = path.relative_to(staging)
        expected.add(relative)
        target = repo / relative
        if not target.exists() or digest(path) != digest(target):
            paths.append(relative)
    tracked = git(repo, "ls-files", "--", "personal-skills").stdout.splitlines()
    for raw in tracked:
        relative = Path(raw)
        if len(relative.parts) < 3 or relative.parts[1] not in active_ids or relative in expected:
            continue
        paths.append(relative)
    return sorted(set(paths))


def ensure_clean_generated_paths(repo, paths):
    dirty = set(git(repo, "status", "--porcelain", "--", "personal-skills", "skill-registry").stdout.splitlines())
    if dirty:
        fail("generated registry paths are already dirty; review or commit them separately")
    for relative in paths:
        parent = repo / relative.parent
        if parent.exists() and parent.is_symlink():
            fail(f"symlinked target directory: {parent}")


def apply_snapshot(repo, staging, paths):
    for relative in paths:
        source, target = staging / relative, repo / relative
        if not source.exists():
            if target.exists():
                target.unlink()
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.is_symlink():
            fail(f"symlinked target: {target}")
        shutil.copy2(source, target)


def ensure_remote(repo):
    remote = git(repo, "remote", "get-url", "origin", check=False)
    if remote.returncode:
        fail(f"origin is not configured; expected {APPROVED_REMOTE}")
    if remote.stdout.strip().rstrip("/") != APPROVED_REMOTE.rstrip("/"):
        fail(f"origin is {remote.stdout.strip()!r}, not the approved Coordinator remote")


def stage_commit_push(repo, paths, message, push, draft_pr):
    staged = git(repo, "diff", "--cached", "--name-only").stdout.splitlines()
    if staged:
        fail("Git index already has entries; refusing a mixed commit")
    git(repo, "add", "--", *[str(path) for path in paths])
    staged = git(repo, "diff", "--cached", "--name-only").stdout.splitlines()
    expected = {str(path) for path in paths}
    if not staged or not set(staged).issubset(expected):
        fail("staged paths are not the planned registry changes")
    git(repo, "diff", "--cached", "--check")
    branch = git(repo, "branch", "--show-current").stdout.strip()
    if branch in {"main", "master"}:
        branch = f"codex/sync-personal-skills-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        git(repo, "switch", "-c", branch)
    git(repo, "commit", "-m", message)
    if not push:
        return branch
    ensure_remote(repo)
    git(repo, "push", "-u", "origin", branch)
    if draft_pr:
        run("gh", "--version")
        run("gh", "auth", "status")
        run("gh", "pr", "create", "--draft", "--fill", "--head", branch, cwd=repo)
    return branch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--draft-pr", action="store_true")
    parser.add_argument("--message")
    args = parser.parse_args()
    if args.commit and (not args.write or not args.message):
        fail("--commit requires --write and --message")
    if (args.push or args.draft_pr) and not args.commit:
        fail("--push and --draft-pr require --commit")
    repo, root = args.repo.resolve(), args.source_root.resolve()
    if root != DEFAULT_ROOT.resolve():
        fail("non-default roots require an owner-reviewed policy update")
    if not (repo / ".git").exists():
        fail("repository is not a Git worktree")
    if args.push:
        ensure_remote(repo)
    with tempfile.TemporaryDirectory(prefix="skill-registry-", dir=repo) as temp:
        staging = Path(temp)
        records = build_snapshot(root, staging)
        paths = changed_paths(repo, staging, {record["id"] for record in records})
        print(json.dumps({"skills": len(records), "changed_paths": [str(path) for path in paths], "write": args.write, "commit": args.commit, "push": args.push}, indent=2))
        if not args.write:
            return
        ensure_clean_generated_paths(repo, paths)
        apply_snapshot(repo, staging, paths)
    if args.commit:
        branch = stage_commit_push(repo, paths, args.message, args.push, args.draft_pr)
        print(json.dumps({"branch": branch, "published": args.push}, indent=2))


if __name__ == "__main__":
    main()
