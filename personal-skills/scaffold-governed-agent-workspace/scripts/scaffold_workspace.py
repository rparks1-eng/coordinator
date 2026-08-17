#!/usr/bin/env python3
"""Proposal-first scaffold and structural validator for a governed ICM pilot."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

REQUIRED = ["AGENTS.md", "CONTEXT.md", "_system/artifact-envelope-template.md", "_system/evaluation-template.md", "01_intake-and-research/CONTEXT.md", "02_workspace-design/CONTEXT.md", "03_evaluation-and-update-plan/CONTEXT.md"]

def files(unit, outcome, owner, classification, threshold, retention):
    meta = f"Owner: {owner}\nData classification: {classification}\nRetention: {retention}\nRecurring unit: {unit}\nOutcome: {outcome}\nEvaluation threshold: {threshold}\n\n"
    return {
      "AGENTS.md": "# Governed Agent Workspace\n\nRead `CONTEXT.md` to route work. This local, sequential workspace does not authorize runtime, promotion, or external actions.\n",
      "CONTEXT.md": meta + "# Workspace routing\n\n1. `01_intake-and-research/` captures an editable brief.\n2. `02_workspace-design/` defines artifact handoffs.\n3. `03_evaluation-and-update-plan/` records a baseline and stops before promotion.\n",
      "_system/artifact-envelope-template.md": "# Artifact envelope\n\n- run_id:\n- producer:\n- recipient:\n- input_hash:\n- status:\n- output_path:\n- human_check:\n- failure_route:\n\nNon-authority: provenance only; not an approval, credential, or delivery instruction.\n",
      "_system/evaluation-template.md": meta + "# Evaluation record\n\n- Baseline:\n- Representative cases:\n- Held-out cases:\n- Regression threshold:\n- Cost/latency observation:\n- Independent human review:\n\nA valid file write or hash does not prove improvement.\n",
      "01_intake-and-research/CONTEXT.md": "# 01 Intake and research\n\n## Inputs\n- Working: `output/brief.md`\n- Reference: `../_system/artifact-envelope-template.md`\n\n## Process\n1. Record sources and assumptions.\n2. Write an editable brief.\n\n## Outputs\n- `output/brief.md`\n\n## Human check\nConfirm scope, classification, and source suitability.\n\n## Failure route\nBlock on missing owner, scope, or classification.\n",
      "02_workspace-design/CONTEXT.md": "# 02 Workspace design\n\n## Inputs\n- Working: `../01_intake-and-research/output/brief.md`\n- Reference: `../_system/artifact-envelope-template.md`\n\n## Process\n1. Define one artifact per handoff.\n2. Record owner, recipient, hash, status, human check, and failure route.\n\n## Outputs\n- `output/workspace-design.md`\n\n## Human check\nApprove the design before implementation.\n\n## Failure route\nReturn to intake if a boundary is ambiguous.\n",
      "03_evaluation-and-update-plan/CONTEXT.md": "# 03 Evaluation and update plan\n\n## Inputs\n- Working: `../02_workspace-design/output/workspace-design.md`\n- Reference: `../_system/evaluation-template.md`\n\n## Process\n1. Define baseline and held-out checks.\n2. Write a plan with evidence and unresolved gates.\n\n## Outputs\n- `output/evaluation-record.md`\n- `output/update-plan.md`\n\n## Human check\nReview evidence and explicitly select any future target outside this workspace.\n\n## Failure route\nStop before candidate generation, staging, or installation.\n",
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--validate", type=Path); p.add_argument("--destination", type=Path)
    p.add_argument("--unit"); p.add_argument("--outcome"); p.add_argument("--owner")
    p.add_argument("--classification", choices=["public", "internal", "restricted"])
    p.add_argument("--threshold"); p.add_argument("--retention", default="unknown"); p.add_argument("--apply", action="store_true")
    a = p.parse_args()
    if a.validate:
        dest = a.validate.resolve(); missing = [x for x in REQUIRED if not (dest / x).is_file()]
        print(json.dumps({"valid": not missing, "destination": str(dest), "missing": missing, "validation": "structural-only"}, indent=2)); return 0 if not missing else 2
    if not all([a.destination, a.unit, a.outcome, a.owner, a.classification, a.threshold]): p.error("--destination, --unit, --outcome, --owner, --classification, and --threshold are required")
    dest = a.destination.resolve()
    if dest.exists() and any(dest.iterdir()): p.error("destination exists and is not empty")
    proposal = {"operation": "scaffolded" if a.apply else "proposal", "destination": str(dest), "files": REQUIRED, "non_authority": "does not run agents, grant approval, select targets, or perform promotion"}
    if not a.apply: print(json.dumps(proposal, indent=2)); return 0
    for rel, body in files(a.unit, a.outcome, a.owner, a.classification, a.threshold, a.retention).items():
        target = dest / rel; target.parent.mkdir(parents=True, exist_ok=True); target.write_text(body, encoding="utf-8")
    print(json.dumps(proposal, indent=2)); return 0

if __name__ == "__main__": raise SystemExit(main())
