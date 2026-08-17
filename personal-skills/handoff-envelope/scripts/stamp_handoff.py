#!/usr/bin/env python3
"""Embed or verify a non-authorizing transit envelope in one Markdown artifact."""
from __future__ import annotations

import argparse, datetime as dt, hashlib, json, os, re, uuid
from pathlib import Path

START = "<!-- transit-envelope-v1\n"
END = "\n-->"
PATTERN = re.compile(re.escape(START) + r"(.*?)" + re.escape(END) + r"\n?", re.S)

def canonical(path: Path) -> Path:
    if path.is_symlink() or not path.is_file():
        raise SystemExit(f"refusing non-regular or symlink artifact: {path}")
    return path.resolve()

def normalized(text: str) -> str:
    return re.sub(r'"artifact_sha256":\s*"[0-9a-f]{64}"', '"artifact_sha256":"' + "0" * 64 + '"', text)

def content_hash(text: str) -> str:
    return hashlib.sha256(normalized(text).encode("utf-8")).hexdigest()

def parse(text: str) -> tuple[dict, re.Match[str]]:
    match = PATTERN.search(text)
    if not match:
        raise SystemExit("missing transit-envelope-v1")
    try:
        envelope = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid transit envelope JSON: {exc}")
    return envelope, match

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--producer")
    parser.add_argument("--recipient")
    parser.add_argument("--artifact-type")
    parser.add_argument("--run-id")
    parser.add_argument("--step-id")
    parser.add_argument("--previous-handoff", type=Path)
    parser.add_argument("--input", action="append", type=Path, default=[])
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    path = canonical(args.artifact)
    text = path.read_text(encoding="utf-8")
    if args.verify:
        envelope, _ = parse(text)
        required = {"schema_version", "run_id", "step_id", "artifact_type", "producer", "intended_recipient", "artifact_path", "artifact_sha256", "created_at", "input_artifacts", "previous_handoff_sha256", "evidence_class", "non_authority"}
        if envelope.get("schema_version") != 1 or required - set(envelope):
            raise SystemExit("invalid transit envelope schema")
        if envelope["artifact_path"] != str(path) or envelope["artifact_sha256"] != content_hash(text):
            raise SystemExit("transit envelope path or hash mismatch")
        print(json.dumps(envelope, indent=2))
        return 0
    if not all((args.producer, args.recipient, args.artifact_type, args.run_id, args.step_id)):
        parser.error("stamping requires --producer, --recipient, --artifact-type, --run-id, and --step-id")
    inputs = []
    for source in args.input:
        source = canonical(source)
        inputs.append({"path": str(source), "sha256": hashlib.sha256(source.read_bytes()).hexdigest()})
    previous = None
    if args.previous_handoff:
        previous_path = canonical(args.previous_handoff)
        previous_text = previous_path.read_text(encoding="utf-8")
        previous_envelope, _ = parse(previous_text)
        if previous_envelope.get("artifact_sha256") != content_hash(previous_text):
            raise SystemExit("previous handoff hash mismatch")
        previous = previous_envelope["artifact_sha256"]
    text = PATTERN.sub("", text)
    envelope = {"schema_version": 1, "run_id": args.run_id, "step_id": args.step_id, "artifact_type": args.artifact_type, "producer": args.producer, "intended_recipient": args.recipient, "artifact_path": str(path), "artifact_sha256": "0" * 64, "created_at": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"), "input_artifacts": inputs, "previous_handoff_sha256": previous, "evidence_class": "artifact-provenance", "non_authority": "transit-only; does not select targets, approve changes, or authorize delivery"}
    provisional = START + json.dumps(envelope, sort_keys=True, separators=(",", ":")) + END + "\n" + text
    envelope["artifact_sha256"] = content_hash(provisional)
    final = START + json.dumps(envelope, sort_keys=True, separators=(",", ":")) + END + "\n" + text
    if content_hash(final) != envelope["artifact_sha256"]:
        raise SystemExit("internal envelope hash failure")
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(final, encoding="utf-8")
    os.replace(temporary, path)
    print(path)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
