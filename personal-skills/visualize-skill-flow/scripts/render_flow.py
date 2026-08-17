#!/usr/bin/env python3
"""Render a bounded Mermaid flow from a normalized, caller-produced JSON spec."""
import argparse
import json
from pathlib import Path

ALLOWED_TYPES = {"outcome", "catalog-preflight", "skill", "human-gate", "blocked", "unverified"}

def clean(value):
    return str(value).replace('"', "'").replace("\n", " ").strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    spec = json.loads(Path(args.spec).read_text())
    nodes, edges = spec.get("nodes"), spec.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list) or not nodes:
        raise SystemExit("spec requires non-empty nodes and an edges list")
    ids = set()
    for node in nodes:
        if not isinstance(node, dict) or node.get("id") in ids or node.get("type") not in ALLOWED_TYPES:
            raise SystemExit("each node needs a unique id and allowed type")
        ids.add(node["id"])
    for edge in edges:
        if not isinstance(edge, dict) or edge.get("from") not in ids or edge.get("to") not in ids:
            raise SystemExit("each edge must reference existing node ids")
    lines = ["```mermaid", "flowchart LR"]
    for node in nodes:
        lines.append(f'  {node["id"]}["{clean(node.get("label", node["id"]))}"]')
    for edge in edges:
        lines.append(f'  {edge["from"]} -->|{clean(edge.get("label", "unverified"))}| {edge["to"]}')
    lines += ["```", ""]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise SystemExit("refusing to overwrite output")
    output.write_text("\n".join(lines))

if __name__ == "__main__":
    main()
