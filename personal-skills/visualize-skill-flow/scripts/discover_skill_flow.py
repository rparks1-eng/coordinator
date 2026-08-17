#!/usr/bin/env python3
"""Create a read-only declared-interaction map from bounded skill roots."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import os
import re
from collections import defaultdict
from pathlib import Path

SKILL_REF = re.compile(r"\$([a-z][a-z0-9-]*)\b")
PATH_REF = re.compile(r"(?:~|/)[^\s)`]+/SKILL\.md")
SKIP_DIRS = {".git", ".cache", "node_modules", "venv", ".venv", "__pycache__"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative_depth(path: Path, root: Path) -> int:
    return len(path.relative_to(root).parts)


def walk_skill_files(root: Path, max_depth: int = 12) -> list[Path]:
    if not root.is_dir():
        return []
    matches: list[Path] = []
    for current, dirs, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        depth = relative_depth(current_path, root)
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        if depth >= max_depth:
            dirs[:] = []
        if "SKILL.md" in files:
            candidate = current_path / "SKILL.md"
            if candidate.is_file() and not candidate.is_symlink():
                matches.append(candidate.resolve())
    return sorted(set(matches))


def parse_skill(path: Path, source: str) -> dict:
    raw = path.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()
    name = path.parent.name
    description = ""
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if line.startswith("name:"):
                name = line.split(":", 1)[1].strip().strip("\"'") or name
            elif line.startswith("description:"):
                description = line.split(":", 1)[1].strip().strip("\"'")
    inactive = any(part in {"osUpdates", "system-updates", "replacement", "candidates"} for part in path.parts)
    return {
        "name": name,
        "path": str(path),
        "sha256": digest(path),
        "source": source,
        "status": "inactive-candidate" if inactive else "discovered",
        "description": description,
        "raw": raw,
    }


def git_roots(root: Path, max_depth: int) -> list[Path]:
    if not root.is_dir():
        return []
    found: set[Path] = set()
    for current, dirs, _ in os.walk(root, followlinks=False):
        current_path = Path(current)
        depth = relative_depth(current_path, root)
        if depth > max_depth:
            dirs[:] = []
            continue
        if ".git" in dirs or (current_path / ".git").is_file():
            found.add(current_path.resolve())
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    return sorted(found)


def node_id(index: int) -> str:
    return f"S{index}"


def clean(value: str) -> str:
    return value.replace('"', "'").replace("\n", " ").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--chatgpt-root", type=Path)
    parser.add_argument("--codex-root", type=Path, default=Path.home() / ".codex" / "skills")
    parser.add_argument("--agents-root", type=Path, default=Path.home() / ".agents" / "skills")
    parser.add_argument("--plugin-root", type=Path, default=Path.home() / ".codex" / "plugins" / "cache" / "personal")
    parser.add_argument("--max-git-depth", type=int, default=5)
    parser.add_argument("--output-dir", type=Path, default=Path.home() / ".codex" / "skill-flow-maps")
    parser.add_argument("--slug", default="discovered-personal-skills")
    args = parser.parse_args()
    if args.max_git_depth < 0:
        raise SystemExit("--max-git-depth must be non-negative")

    workspace = args.workspace.expanduser().resolve()
    chatgpt_root = (args.chatgpt_root or workspace.parent).expanduser().resolve()
    root_specs = [
        ("codex-personal", args.codex_root.expanduser().resolve()),
        ("agents-shared", args.agents_root.expanduser().resolve()),
        ("personal-plugin", args.plugin_root.expanduser().resolve()),
        ("coordinator-workspace", workspace),
        ("chatgpt-workspace", chatgpt_root),
    ]
    seen: dict[Path, str] = {}
    # Give discovered Git worktrees precedence over their enclosing ChatGPT root.
    # This preserves useful provenance without widening discovery beyond that root.
    for repo in git_roots(chatgpt_root, args.max_git_depth):
        for path in walk_skill_files(repo):
            seen.setdefault(path, f"git-worktree:{repo}")
    for source, root in root_specs:
        for path in walk_skill_files(root):
            seen.setdefault(path, source)

    skills = [parse_skill(path, source) for path, source in sorted(seen.items(), key=lambda item: str(item[0]))]
    by_name: dict[str, list[int]] = defaultdict(list)
    by_path = {skill["path"]: index for index, skill in enumerate(skills)}
    for index, skill in enumerate(skills):
        by_name[skill["name"]].append(index)

    edges: dict[tuple[int, int], str] = {}
    unresolved: set[tuple[str, str]] = set()
    for source_index, skill in enumerate(skills):
        for ref in SKILL_REF.findall(skill["raw"]):
            targets = by_name.get(ref, [])
            if targets:
                for target_index in targets:
                    if target_index != source_index:
                        edges.setdefault((source_index, target_index), "declared skill reference; unverified handoff")
            elif "-" in ref:
                unresolved.add((skill["name"], f"${ref}"))
        for raw_path in PATH_REF.findall(skill["raw"]):
            candidate = Path(raw_path).expanduser().resolve(strict=False)
            target_index = by_path.get(str(candidate))
            if target_index is not None and target_index != source_index:
                edges.setdefault((source_index, target_index), "declared skill path; unverified handoff")

    connected = {source for source, _ in edges} | {target for _, target in edges}
    isolated = [skill for index, skill in enumerate(skills) if index not in connected]
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = args.output_dir.expanduser().resolve() / f"{timestamp}-{args.slug}-map.md"
    if output.exists():
        raise SystemExit(f"refusing to overwrite {output}")
    output.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "---",
        "status: discovered-static-map",
        f"created_at: {dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')}",
        f"skill_count: {len(skills)}",
        f"declared_edge_count: {len(edges)}",
        "validation: structural-only",
        "---",
        "",
        "# Discovered Personal Skill Action Flow",
        "",
        "## Scope and boundary",
        "",
        "Read-only discovery covered bounded Codex personal, shared-agent, personal-plugin, Coordinator workspace, ChatGPT workspace, and Git-worktree roots. Edges mean only a skill body declared a skill reference or exact skill path; they do not prove compatible inputs, execution order, authority, or automation. Skills without a declared edge are listed as disconnected, not assumed to be incompatible.",
        "",
        "## Source inventory",
        "",
        "| Skill | Source | Status | SHA-256 | Exact path |",
        "| --- | --- | --- | --- | --- |",
    ]
    for skill in skills:
        lines.append(f"| `{skill['name']}` | {clean(skill['source'])} | `{skill['status']}` | `{skill['sha256']}` | `{skill['path']}` |")
    lines += ["", "## Declared action flow", "", "```mermaid", "flowchart LR"]
    for index, skill in enumerate(skills):
        label = f"{skill['name']}\\n{skill['status']}"
        lines.append(f'  {node_id(index)}["{clean(label)}"]')
    for (source, target), label in sorted(edges.items()):
        lines.append(f"  {node_id(source)} -. {clean(label)} .-> {node_id(target)}")
    lines += ["```", "", "## Declared interactions", "", "| From | To | Evidence class | Status |", "| --- | --- | --- | --- |"]
    if edges:
        for (source, target), label in sorted(edges.items()):
            lines.append(f"| `{skills[source]['name']}` | `{skills[target]['name']}` | `static-inference` | {label} |")
    else:
        lines.append("| — | — | `static-inference` | No declared skill-to-skill references found. |")
    lines += ["", "## No declared interaction", ""]
    if isolated:
        lines.append("These skills had no mapped incoming or outgoing declared reference in the scanned bodies. This is a documentation finding, not a defect or a claim they cannot interact.")
        lines.append("")
        lines.append("| Skill | Source | Reason |")
        lines.append("| --- | --- | --- |")
        for skill in isolated:
            lines.append(f"| `{skill['name']}` | {clean(skill['source'])} | No declared skill reference or exact path edge. |")
    else:
        lines.append("Every discovered skill has at least one declared interaction.")
    lines += ["", "## Unresolved declared references", ""]
    if unresolved:
        lines.append("| Referencing skill | Unresolved reference |")
        lines.append("| --- | --- |")
        for source, ref in sorted(unresolved):
            lines.append(f"| `{source}` | `{ref}` |")
    else:
        lines.append("- None within the scanned inventory.")
    lines += ["", "## Authority boundary", "", "This map is evidence only. It does not select skills, invoke workflows, create candidates, approve delivery, stage files, install skills, or grant authority.", "", "## Smallest reversible next step", "", "Review only the declared edges marked `unverified`; add an explicit artifact contract to a skill pair only when a real handoff is desired."]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    raise SystemExit(main())
