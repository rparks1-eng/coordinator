#!/usr/bin/env python3
"""Inert structural diagnosis and conservative mechanical repair for Codex skills."""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path


NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
MAX_TEXT = 2 * 1024 * 1024


def add(findings: list[dict[str, str]], severity: str, code: str, path: str, detail: str) -> None:
    findings.append({"severity": severity, "code": code, "path": path, "detail": detail})


def read_text(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise ValueError("not a regular non-symlink file")
    if path.stat().st_size > MAX_TEXT:
        raise ValueError("file exceeds 2 MiB diagnostic limit")
    return path.read_text(encoding="utf-8")


def frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}
    values: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def scan(root: Path, repair: bool) -> dict[str, object]:
    findings: list[dict[str, str]] = []
    repairs: list[str] = []
    if root.is_symlink() or not root.is_dir():
        add(findings, "error", "invalid-root", root.name, "Skill root must be a real directory, not a symlink.")
        return {"schema": 1, "status": "broken", "findings": findings, "repairs": repairs}

    skill_file = root / "SKILL.md"
    try:
        skill_text = read_text(skill_file)
    except (OSError, UnicodeError, ValueError) as error:
        add(findings, "error", "skill-file-unreadable", "SKILL.md", str(error))
        return {"schema": 1, "status": "broken", "findings": findings, "repairs": repairs}

    meta = frontmatter(skill_text)
    name = meta.get("name", "")
    description = meta.get("description", "")
    if not NAME.fullmatch(name):
        add(findings, "error", "invalid-name", "SKILL.md", "Frontmatter name must be lowercase hyphen-case.")
    if name and root.name != name:
        add(findings, "warning", "folder-name-mismatch", "SKILL.md", f"Folder is {root.name!r}, frontmatter name is {name!r}.")
    if not description:
        add(findings, "error", "missing-description", "SKILL.md", "Frontmatter description is required.")
    if "TODO" in skill_text:
        add(findings, "warning", "todo-marker", "SKILL.md", "Unresolved TODO marker remains in the skill contract.")

    for path in sorted(root.rglob("*")):
        if ".git" in path.parts or "__pycache__" in path.parts or not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            add(findings, "error", "symlink-file", rel, "Symlinked skill files are not accepted by first aid.")
            continue
        if path.suffix.lower() in {".md", ".yaml", ".yml", ".py", ".json", ".txt"}:
            try:
                text = read_text(path)
            except (OSError, UnicodeError, ValueError) as error:
                add(findings, "error", "text-unreadable", rel, str(error))
                continue
            if text and not text.endswith("\n"):
                if repair:
                    path.write_text(text + "\n", encoding="utf-8")
                    repairs.append(f"added-final-newline:{rel}")
                else:
                    add(findings, "repairable", "missing-final-newline", rel, "Add a final newline.")
            if path.suffix.lower() == ".md":
                for target in LINK.findall(text):
                    if target.startswith(("http://", "https://", "#", "mailto:")):
                        continue
                    clean = target.split("#", 1)[0]
                    resolved = (path.parent / clean).resolve()
                    try:
                        resolved.relative_to(root.resolve())
                    except ValueError:
                        add(findings, "error", "link-escapes-root", rel, f"Relative link escapes skill root: {target}")
                        continue
                    if not resolved.exists():
                        add(findings, "error", "broken-relative-link", rel, f"Missing target: {target}")
            if path.suffix.lower() == ".py":
                try:
                    ast.parse(text, filename=rel)
                except SyntaxError as error:
                    add(findings, "error", "python-syntax", rel, f"Line {error.lineno}: {error.msg}")

    agent_file = root / "agents" / "openai.yaml"
    if not agent_file.exists():
        add(findings, "warning", "missing-agent-metadata", "agents/openai.yaml", "Generate UI metadata with skill-creator.")
    else:
        try:
            agent_text = read_text(agent_file)
            if name and f"${name}" not in agent_text:
                add(findings, "warning", "default-prompt-missing-skill", "agents/openai.yaml", "Default prompt should mention the skill explicitly.")
        except (OSError, UnicodeError, ValueError) as error:
            add(findings, "error", "agent-metadata-unreadable", "agents/openai.yaml", str(error))

    rank = {"repairable": 0, "warning": 1, "error": 2}
    highest = max((rank[item["severity"]] for item in findings), default=-1)
    status = "broken" if highest >= 2 else "needs-review" if highest >= 0 else "healthy"
    return {"schema": 1, "skill": name or root.name, "status": status, "findings": findings, "repairs": repairs}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill_folder", type=Path)
    parser.add_argument("--repair", action="store_true", help="Only add missing final newlines; never rewrite skill meaning.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = scan(args.skill_folder.absolute(), args.repair)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        if args.output.exists() or args.output.is_symlink():
            raise SystemExit(f"refusing to overwrite output: {args.output}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return {"healthy": 0, "needs-review": 2, "broken": 3}[str(report["status"])]


if __name__ == "__main__":
    raise SystemExit(main())
