#!/usr/bin/env python3
"""Validate a human-owned core skill profile without changing it."""
import argparse
import hashlib
import json
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("profile")
args = parser.parse_args()

profile = Path(args.profile)
data = json.loads(profile.read_text())
errors = []
for item in data.get("core", []):
    path = Path(item.get("path", ""))
    if not path.is_file():
        errors.append(f"missing: {path}")
        continue
    if hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
        errors.append(f"hash mismatch: {path}")
if data.get("owner") != "human":
    errors.append("owner must be human")
if not data.get("registry_ref") or not data.get("rollback"):
    errors.append("registry_ref and rollback required")
print(json.dumps({"valid": not errors, "errors": errors}))
raise SystemExit(bool(errors))
