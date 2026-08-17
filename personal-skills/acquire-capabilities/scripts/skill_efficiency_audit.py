#!/usr/bin/env python3
"""Audit a Codex skill and gate bounded, evidence-backed optimizations.

This tool is deliberately local and inert. It does not execute skill scripts,
contact a provider, read transcripts, or modify the audited skill.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
QUOTED_YAML_VALUE = re.compile(r'^\s*([a-z_]+):\s*(["\'])(.*?)\2\s*$')
MAX_TEXT_BYTES = 2 * 1024 * 1024
MAX_FILES = 2_000
RESOURCE_DIRS = {"references", "scripts", "assets"}
IGNORED_PARTS = {".git", "__pycache__", ".DS_Store"}


def finding(severity: str, code: str, path: str, detail: str) -> dict[str, str]:
    return {"severity": severity, "code": code, "path": path, "detail": detail}


def read_text(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise ValueError("not a regular non-symlink file")
    if path.stat().st_size > MAX_TEXT_BYTES:
        raise ValueError("file exceeds 2 MiB audit limit")
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}
    values: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def local_link(source: Path, raw: str, root: Path) -> Path | None:
    if raw.startswith(("http://", "https://", "mailto:", "#")):
        return None
    clean = raw.split("#", 1)[0].strip()
    if not clean:
        return None
    target = (source.parent / clean).resolve()
    target.relative_to(root.resolve())
    return target


def normalized_paragraphs(text: str) -> list[str]:
    body = text
    if body.startswith("---\n"):
        parts = body.split("---", 2)
        if len(parts) == 3:
            body = parts[2]
    paragraphs: list[str] = []
    for chunk in re.split(r"\n\s*\n", body):
        lines = [line.strip() for line in chunk.splitlines()]
        if not lines or any(line.startswith("```") for line in lines):
            continue
        joined = " ".join(lines).strip()
        if len(joined) < 120 or joined.startswith("#"):
            continue
        normalized = re.sub(r"\s+", " ", joined).casefold()
        paragraphs.append(normalized)
    return paragraphs


def audit_skill(root: Path) -> dict[str, Any]:
    root = root.absolute()
    findings: list[dict[str, str]] = []
    if root.is_symlink() or not root.is_dir():
        return {
            "schema": 1,
            "kind": "skill-efficiency-audit",
            "status": "broken",
            "findings": [finding("error", "invalid-root", root.name, "Skill root must be a real directory.")],
            "metrics": {},
            "recommendations": [],
        }
    root = root.resolve()

    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if any(part in IGNORED_PARTS for part in path.parts):
            continue
        if path.is_symlink():
            findings.append(finding("error", "symlink-resource", path.relative_to(root).as_posix(), "Symlinked skill resources are not auditable."))
        elif path.is_file():
            files.append(path)
    if len(files) > MAX_FILES:
        findings.append(finding("error", "file-count-limit", ".", f"Skill exceeds the {MAX_FILES}-file audit limit."))

    skill_path = root / "SKILL.md"
    try:
        skill_text = read_text(skill_path)
    except (OSError, UnicodeError, ValueError) as error:
        findings.append(finding("error", "skill-unreadable", "SKILL.md", str(error)))
        return _finish(root.name, findings, {}, [], "")

    meta = parse_frontmatter(skill_text)
    name = meta.get("name", "")
    description = meta.get("description", "")
    if not NAME.fullmatch(name):
        findings.append(finding("error", "invalid-name", "SKILL.md", "Frontmatter name must be lowercase hyphen-case."))
    if not description:
        findings.append(finding("error", "missing-description", "SKILL.md", "Frontmatter description is required."))
    elif len(description) > 1_024:
        findings.append(finding("error", "description-too-long", "SKILL.md", "Description exceeds the 1,024-character discovery limit."))
    elif len(description) < 40:
        findings.append(finding("warning", "description-too-vague", "SKILL.md", "Description is probably too short to route reliably."))

    skill_lines = len(skill_text.splitlines())
    skill_words = len(skill_text.split())
    if skill_lines > 500:
        findings.append(finding("error", "entry-over-500-lines", "SKILL.md", "Move detail to routed references; keep SKILL.md under 500 lines."))
    elif skill_lines > 350:
        findings.append(finding("warning", "entry-context-heavy", "SKILL.md", "Consider moving specialist detail to on-demand references."))

    text_by_path: dict[str, str] = {}
    total_words = 0
    total_bytes = 0
    content_manifest = hashlib.sha256()
    for path in files:
        rel = path.relative_to(root).as_posix()
        total_bytes += path.stat().st_size
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        content_manifest.update(f"{rel}\0{path.stat().st_size}\0{digest}\n".encode())
        if path.suffix.lower() not in {".md", ".yaml", ".yml", ".py", ".json", ".txt"}:
            continue
        try:
            text = read_text(path)
        except (OSError, UnicodeError, ValueError) as error:
            findings.append(finding("error", "resource-unreadable", rel, str(error)))
            continue
        text_by_path[rel] = text
        total_words += len(text.split())

    resources = {
        rel for rel in text_by_path
        if rel.split("/", 1)[0] in RESOURCE_DIRS
        and not rel.startswith("scripts/test_")
    }
    graph: dict[str, set[str]] = defaultdict(set)
    for rel, text in text_by_path.items():
        if not rel.endswith(".md"):
            continue
        source = root / rel
        for raw in LINK.findall(text):
            try:
                target = local_link(source, raw, root)
            except ValueError:
                findings.append(finding("error", "link-escapes-root", rel, f"Relative link escapes the skill root: {raw}"))
                continue
            if target is None:
                continue
            if not target.exists():
                findings.append(finding("error", "broken-relative-link", rel, f"Missing target: {raw}"))
                continue
            if target.is_file():
                graph[rel].add(target.relative_to(root).as_posix())
        for resource in resources:
            if resource in text:
                graph[rel].add(resource)

    depth: dict[str, int] = {"SKILL.md": 0}
    queue: deque[str] = deque(["SKILL.md"])
    while queue:
        current = queue.popleft()
        for target in sorted(graph.get(current, set())):
            if target not in depth:
                depth[target] = depth[current] + 1
                queue.append(target)

    for resource in sorted(resources):
        if resource not in depth:
            findings.append(finding("warning", "unrouted-resource", resource, "Resource is not reachable from SKILL.md; link it or archive it."))
        elif depth[resource] > 2:
            findings.append(finding("warning", "deep-resource-hop", resource, f"Resource needs {depth[resource]} routing hops; target at most two."))

    paragraph_locations: dict[str, list[str]] = defaultdict(list)
    for rel, text in text_by_path.items():
        if not rel.endswith(".md"):
            continue
        for paragraph in set(normalized_paragraphs(text)):
            paragraph_locations[paragraph].append(rel)
    duplicates = [paths for paths in paragraph_locations.values() if len(set(paths)) > 1]
    for paths in sorted(duplicates, key=lambda item: tuple(item)):
        unique = sorted(set(paths))
        findings.append(finding("warning", "duplicated-guidance", unique[0], f"Substantial paragraph is duplicated in: {', '.join(unique)}"))

    agent_path = root / "agents" / "openai.yaml"
    try:
        agent_text = read_text(agent_path)
    except (OSError, UnicodeError, ValueError) as error:
        findings.append(finding("warning", "agent-metadata-unreadable", "agents/openai.yaml", str(error)))
        agent_text = ""
    if agent_text:
        values: dict[str, str] = {}
        for line in agent_text.splitlines():
            match = QUOTED_YAML_VALUE.match(line)
            if match:
                values[match.group(1)] = match.group(3)
        short_description = values.get("short_description", "")
        default_prompt = values.get("default_prompt", "")
        if short_description and not 25 <= len(short_description) <= 64:
            findings.append(finding("warning", "short-description-length", "agents/openai.yaml", "short_description should contain 25-64 characters."))
        if name and f"${name}" not in default_prompt:
            findings.append(finding("warning", "default-prompt-missing-skill", "agents/openai.yaml", "default_prompt must explicitly mention the skill."))

    metrics = {
        "file_count": len(files),
        "total_bytes": total_bytes,
        "total_words": total_words,
        "skill_lines": skill_lines,
        "skill_words": skill_words,
        "routed_resource_count": sum(resource in depth for resource in resources),
        "resource_count": len(resources),
        "max_resource_hops": max((depth.get(resource, 0) for resource in resources), default=0),
        "duplicate_paragraph_groups": len(duplicates),
        "error_count": sum(item["severity"] == "error" for item in findings),
        "warning_count": sum(item["severity"] == "warning" for item in findings),
    }
    recommendations = recommendations_for(findings)
    return _finish(name or root.name, findings, metrics, recommendations, content_manifest.hexdigest())


def recommendations_for(findings: list[dict[str, str]]) -> list[dict[str, str]]:
    mapping = {
        "entry-over-500-lines": "Move specialist content into one-hop references and leave a concise route in SKILL.md.",
        "entry-context-heavy": "Measure forward-test quality before splitting high-cost entry content into references.",
        "unrouted-resource": "Link the resource from the smallest relevant routing section or archive it; never load it implicitly.",
        "deep-resource-hop": "Flatten the route so a cold agent reaches the needed resource within two reads.",
        "duplicated-guidance": "Choose one source of truth and replace copies with links.",
        "broken-relative-link": "Repair the link locally and rerun the original skill test.",
        "description-too-vague": "Add concrete trigger phrases and task boundaries to the frontmatter description.",
        "default-prompt-missing-skill": "Update default_prompt so it explicitly invokes the skill by name.",
    }
    seen: set[str] = set()
    output: list[dict[str, str]] = []
    for item in findings:
        code = item["code"]
        if code in mapping and code not in seen:
            output.append({"finding": code, "action": mapping[code], "automatic": "false"})
            seen.add(code)
    return output


def _finish(skill: str, findings: list[dict[str, str]], metrics: dict[str, Any], recommendations: list[dict[str, str]], content_manifest: str) -> dict[str, Any]:
    severities = {item["severity"] for item in findings}
    status = "broken" if "error" in severities else "needs-review" if "warning" in severities else "healthy"
    return {
        "schema": 1,
        "kind": "skill-efficiency-audit",
        "skill": skill,
        "status": status,
        "claim": "Static structure and context-cost signals only; forward tests decide behavioral quality.",
        "content_manifest_sha256": content_manifest,
        "metrics": metrics,
        "findings": findings,
        "recommendations": recommendations,
    }


def load_json(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_TEXT_BYTES:
        raise ValueError(f"invalid evidence file: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("evidence must be a JSON object")
    return value


def gate_optimization(baseline: dict[str, Any], candidate: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    before = evidence.get("baseline", {})
    after = evidence.get("candidate", {})
    change = evidence.get("change_budget", {})
    before_tasks = before.get("task_ids", [])
    after_tasks = after.get("task_ids", [])
    held_out = evidence.get("held_out_task_ids", [])
    task_lists_valid = all(
        isinstance(items, list)
        and len(items) == len(set(items))
        and all(isinstance(item, str) and item.strip() for item in items)
        for items in (before_tasks, after_tasks, held_out)
    )
    if not task_lists_valid or before_tasks != after_tasks or len(before_tasks) < 3:
        reasons.append("Baseline and candidate must run the same set of at least three tasks.")
    if not task_lists_valid or not held_out or not set(held_out).issubset(set(before_tasks)):
        reasons.append("At least one declared held-out task must be part of the comparison.")
    baseline_hash = baseline.get("content_manifest_sha256")
    candidate_hash = candidate.get("content_manifest_sha256")
    if not isinstance(baseline_hash, str) or evidence.get("baseline_manifest_sha256") != baseline_hash:
        reasons.append("Baseline evidence is not bound to the audited baseline manifest.")
    if not isinstance(candidate_hash, str) or evidence.get("candidate_manifest_sha256") != candidate_hash:
        reasons.append("Candidate evidence is not bound to the audited candidate manifest.")

    numeric_fields = {
        "baseline.passed": before.get("passed"),
        "baseline.false_completions": before.get("false_completions"),
        "candidate.passed": after.get("passed"),
        "candidate.false_completions": after.get("false_completions"),
        "candidate.regression_failures": after.get("regression_failures"),
        "candidate.security_blockers": after.get("security_blockers"),
        "change_budget.changed_files": change.get("changed_files"),
        "change_budget.changed_lines": change.get("changed_lines"),
    }
    for label, value in numeric_fields.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            reasons.append(f"{label} must be a finite non-negative number.")
    if _number(after.get("passed"), -1) < _number(before.get("passed"), 0):
        reasons.append("Candidate passes fewer tasks than baseline.")
    if _number(after.get("false_completions"), 0) > _number(before.get("false_completions"), 0):
        reasons.append("Candidate increases false completions.")
    if _number(after.get("regression_failures"), -1) != 0:
        reasons.append("Candidate has regression failures.")
    if _number(after.get("security_blockers"), -1) != 0:
        reasons.append("Candidate has unresolved security blockers.")
    before_metrics = baseline.get("metrics", {})
    after_metrics = candidate.get("metrics", {})
    if int(after_metrics.get("error_count", 0)) > int(before_metrics.get("error_count", 0)):
        reasons.append("Candidate introduces structural errors.")
    if _number(change.get("changed_files"), 10_000) > 5 or _number(change.get("changed_lines"), 10_000) > 120:
        reasons.append("Candidate exceeds the bounded edit budget of five files or 120 changed lines.")

    improvements: list[str] = []
    if _number(after.get("passed"), 0) > _number(before.get("passed"), 0):
        improvements.append("task passes increased")
    if int(after_metrics.get("warning_count", 0)) < int(before_metrics.get("warning_count", 0)):
        improvements.append("static warnings decreased")
    for key in ("median_loaded_words", "median_tool_calls", "median_elapsed_ms"):
        old = before.get(key)
        new = after.get(key)
        if isinstance(old, (int, float)) and isinstance(new, (int, float)) and old > 0 and new <= old * 0.95:
            improvements.append(f"{key} improved by at least 5%")
    if not improvements:
        reasons.append("No measured quality or efficiency improvement cleared the threshold.")

    return {
        "schema": 1,
        "kind": "skill-optimization-gate",
        "decision": "promote" if not reasons else "reject",
        "reasons": reasons,
        "measured_improvements": improvements,
        "claim": "A passing gate supports only the tested tasks, model, harness, and skill snapshot.",
    }


def _number(value: Any, default: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return default
    return float(value)


def write_report(report: dict[str, Any], output: Path | None) -> None:
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output is None:
        print(rendered, end="")
        return
    if output.exists() or output.is_symlink():
        raise SystemExit(f"refusing to overwrite output: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit")
    audit.add_argument("skill_folder", type=Path)
    audit.add_argument("--output", type=Path)
    gate = sub.add_parser("gate")
    gate.add_argument("--baseline-audit", required=True, type=Path)
    gate.add_argument("--candidate-audit", required=True, type=Path)
    gate.add_argument("--evidence", required=True, type=Path)
    gate.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "audit":
        report = audit_skill(args.skill_folder)
        write_report(report, args.output)
        return {"healthy": 0, "needs-review": 2, "broken": 3}[report["status"]]
    try:
        report = gate_optimization(load_json(args.baseline_audit), load_json(args.candidate_audit), load_json(args.evidence))
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(str(error)) from error
    write_report(report, args.output)
    return 0 if report["decision"] == "promote" else 3


if __name__ == "__main__":
    raise SystemExit(main())
