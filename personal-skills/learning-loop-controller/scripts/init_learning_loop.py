#!/usr/bin/env python3
"""Reserve one non-authorizing learning-to-update run ledger."""
from __future__ import annotations

import argparse, datetime as dt, json, re, uuid
from pathlib import Path

def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:64] or "learning-loop"

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--intent", required=True)
    parser.add_argument("--directory", default="learning-loop-runs")
    args = parser.parse_args()
    run_id = f"ll-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    root = Path(args.directory) / f"{run_id}-{slugify(args.intent)}"
    root.mkdir(parents=True, exist_ok=False)
    ledger = {"schema_version": 1, "run_id": run_id, "intent": args.intent, "created_at": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"), "state": "intent-captured", "artifacts": [], "non_authority": "routing ledger only; target selection, approval, and delivery remain human/trusted-host gates"}
    path = root / "run-ledger.json"
    path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    print(path.resolve())

if __name__ == "__main__":
    raise SystemExit(main())
