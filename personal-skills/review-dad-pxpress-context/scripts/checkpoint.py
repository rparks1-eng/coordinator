#!/usr/bin/env python3
"""Privacy-preserving checkpoint helper for the Messages review skill."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any


SCHEMA_VERSION = 1
MAX_SELECT = 100
MAX_RETAINED = 500


def default_state_dir() -> Path:
    return Path.home() / ".codex" / "private" / "pxpress-message-intake"


def canonical_message(value: dict[str, Any]) -> bytes:
    allowed = {
        "direction": value.get("direction"),
        "timestamp": value.get("timestamp"),
        "text": value.get("text"),
        "links": value.get("links", []),
        "attachments": value.get("attachments", []),
    }
    return json.dumps(
        allowed, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def fingerprint(value: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_message(value)).hexdigest()


def read_stdin_list() -> list[Any]:
    try:
        value = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON input: {exc}") from exc
    if not isinstance(value, list):
        raise SystemExit("input must be a JSON array")
    return value


def ensure_fingerprints(values: list[Any]) -> list[str]:
    result: list[str] = []
    for value in values:
        if not isinstance(value, str) or len(value) != 64:
            raise SystemExit("each fingerprint must be a 64-character SHA-256 hex string")
        try:
            int(value, 16)
        except ValueError as exc:
            raise SystemExit("fingerprint contains non-hexadecimal characters") from exc
        result.append(value.lower())
    return result


def state_path(state_dir: Path) -> Path:
    return state_dir / "checkpoint.json"


def load_state(state_dir: Path) -> dict[str, Any]:
    path = state_path(state_dir)
    if not path.exists():
        return {
            "schema_version": SCHEMA_VERSION,
            "conversation_key": None,
            "fingerprints": [],
            "processed_count": 0,
        }
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if value.get("schema_version") != SCHEMA_VERSION:
        raise SystemExit("unsupported checkpoint schema")
    return value


def save_state(state_dir: Path, value: dict[str, Any]) -> None:
    state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(state_dir, 0o700)
    fd, temp_name = tempfile.mkstemp(prefix="checkpoint-", suffix=".json", dir=state_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
        os.chmod(temp_name, 0o600)
        os.replace(temp_name, state_path(state_dir))
        os.chmod(state_path(state_dir), 0o600)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def run_hash() -> None:
    values = read_stdin_list()
    if not all(isinstance(value, dict) for value in values):
        raise SystemExit("hash input must contain JSON objects")
    json.dump([fingerprint(value) for value in values], sys.stdout)
    sys.stdout.write("\n")


def run_select(state_dir: Path, limit: int) -> None:
    if not 1 <= limit <= MAX_SELECT:
        raise SystemExit(f"limit must be between 1 and {MAX_SELECT}")
    candidates = ensure_fingerprints(read_stdin_list())
    known = set(load_state(state_dir).get("fingerprints", []))
    unseen = [value for value in candidates if value not in known]
    json.dump(unseen[-limit:], sys.stdout)
    sys.stdout.write("\n")


def run_commit(state_dir: Path, conversation_key: str) -> None:
    if len(conversation_key) != 64:
        raise SystemExit("conversation key must be a 64-character SHA-256 hex string")
    try:
        int(conversation_key, 16)
    except ValueError as exc:
        raise SystemExit("conversation key contains non-hexadecimal characters") from exc
    incoming = ensure_fingerprints(read_stdin_list())
    state = load_state(state_dir)
    previous = list(state.get("fingerprints", []))
    merged = list(dict.fromkeys(previous + incoming))[-MAX_RETAINED:]
    state.update(
        {
            "schema_version": SCHEMA_VERSION,
            "conversation_key": conversation_key.lower(),
            "fingerprints": merged,
            "processed_count": int(state.get("processed_count", 0)) + len(incoming),
        }
    )
    save_state(state_dir, state)
    json.dump({"committed": len(incoming), "retained": len(merged)}, sys.stdout)
    sys.stdout.write("\n")


def run_status(state_dir: Path) -> None:
    state = load_state(state_dir)
    json.dump(
        {
            "initialized": state_path(state_dir).exists(),
            "has_conversation_key": bool(state.get("conversation_key")),
            "retained_fingerprints": len(state.get("fingerprints", [])),
            "processed_count": int(state.get("processed_count", 0)),
        },
        sys.stdout,
        sort_keys=True,
    )
    sys.stdout.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--state-dir", type=Path, default=default_state_dir(), help="private state directory"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("hash", help="hash normalized messages from standard input")
    select_parser = subparsers.add_parser("select", help="return unseen hashes without mutation")
    select_parser.add_argument("--limit", type=int, default=MAX_SELECT)
    commit_parser = subparsers.add_parser("commit", help="commit processed hashes")
    commit_parser.add_argument("--conversation-key", required=True)
    subparsers.add_parser("status", help="show nonsensitive checkpoint status")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "hash":
        run_hash()
    elif args.command == "select":
        run_select(args.state_dir, args.limit)
    elif args.command == "commit":
        run_commit(args.state_dir, args.conversation_key)
    elif args.command == "status":
        run_status(args.state_dir)


if __name__ == "__main__":
    main()
