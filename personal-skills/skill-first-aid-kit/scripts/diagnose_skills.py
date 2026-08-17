#!/usr/bin/env python3
"""Create one read-only diagnostic prescription for each requested Codex skill."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import py_compile
import re
import tempfile


DEFAULT_ROOT = Path.home() / ".codex" / "skills"


def resolve_skill(value: str) -> Path:
    candidate = Path(value).expanduser()
    if candidate.is_dir():
        return candidate.resolve()
    return (DEFAULT_ROOT / value).resolve()


def finding(category: str, severity: str, evidence: str, prescription: str) -> dict[str, str]:
    return {"category": category, "severity": severity, "evidence": evidence, "prescription": prescription}


def inspect_skill(folder: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    skill_md = folder / "SKILL.md"
    if not folder.is_dir():
        return [finding("syntax/contract", "blocking", f"Folder does not exist: {folder}", "Supply the installed skill path or correct skill name.")]
    if not skill_md.is_file():
        return [finding("trigger/metadata", "blocking", "SKILL.md is missing.", "Restore SKILL.md with valid name and description frontmatter.")]
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    frontmatter = re.match(r"\A---\s*\n(.*?)\n---", text, re.DOTALL)
    if not frontmatter:
        findings.append(finding("trigger/metadata", "blocking", "SKILL.md has no YAML frontmatter.", "Add name and description frontmatter."))
    else:
        metadata = frontmatter.group(1)
        for field in ("name", "description"):
            if not re.search(rf"^{field}:\s*\S", metadata, re.MULTILINE):
                findings.append(finding("trigger/metadata", "blocking", f"Frontmatter lacks {field}.", f"Add a concise {field} field."))
    if "[TODO:" in text or "TODO:" in text:
        findings.append(finding("routing/context", "medium", "SKILL.md still contains TODO placeholders.", "Replace placeholders with executable, scoped instructions."))
    for link in re.findall(r"\[[^\]]+\]\(([^)#]+)\)", text):
        target = (folder / link).resolve()
        if not target.exists():
            findings.append(finding("reference", "high", f"Broken relative reference: {link}", "Restore the target or update the link."))
    agent_yaml = folder / "agents" / "openai.yaml"
    if not agent_yaml.exists():
        findings.append(finding("trigger/metadata", "low", "agents/openai.yaml is absent.", "Generate optional UI metadata with skill-creator when desired."))
    for script in folder.glob("scripts/**/*.py"):
        try:
            py_compile.compile(str(script), doraise=True)
        except py_compile.PyCompileError as error:
            findings.append(finding("syntax/contract", "blocking", f"Python does not compile: {script.relative_to(folder)}: {error.msg}", "Fix the syntax error, then rerun this diagnostic."))
        source = script.read_text(encoding="utf-8", errors="replace")
        if re.search(r"os\.environ|getenv\(", source) and re.search(r"urlopen|requests\.|http", source):
            findings.append(finding("security", "medium", f"{script.relative_to(folder)} combines environment access and network behavior.", "Review credential handling and ensure secrets are never logged or sent to unintended hosts."))
    if not findings:
        findings.append(finding("no fault observed", "info", "Structural checks found no obvious defect.", "Reproduce the reported task failure and add its exact error to a follow-up diagnosis."))
    return findings


def write_prescription(folder: Path, findings: list[dict[str, str]], output: Path) -> Path:
    output.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = output / f"{folder.name}-prescription-{stamp}.md"
    lines = [f"# Prescription: {folder.name}", "", f"Inspected: {folder}", f"Created: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", "", "## Findings"]
    for index, item in enumerate(findings, start=1):
        lines.extend(["", f"### {index}. {item['category']} — {item['severity']}", "", f"Evidence: {item['evidence']}", "", f"Prescription: {item['prescription']}"])
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output, delete=False) as temporary:
        temporary.write("\n".join(lines) + "\n")
        temporary_path = Path(temporary.name)
    temporary_path.replace(path)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose local Codex skills without modifying them.")
    parser.add_argument("skills", nargs="+", help="skill folder paths or names under ~/.codex/skills")
    parser.add_argument("--out", type=Path, default=Path.home() / ".codex" / "skill-prescriptions")
    args = parser.parse_args()
    for value in args.skills:
        folder = resolve_skill(value)
        print(write_prescription(folder, inspect_skill(folder), args.out.expanduser()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
