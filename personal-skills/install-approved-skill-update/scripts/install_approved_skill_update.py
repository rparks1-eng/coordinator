#!/usr/bin/env python3
"""Install exactly one approved local skill candidate, or roll it back safely."""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import uuid

ACTIVE_ROOT = Path("/Users/brandonparks/.codex/skills").resolve()
CANDIDATE_ROOT = Path("/Users/brandonparks/Documents/ChatGPT/coordinator/system-updates/osUpdates").resolve()
ROLLBACK_PARENT = Path("/Users/brandonparks/Documents/ChatGPT/coordinator/skill-install-rollbacks").resolve()
HEX64 = set("0123456789abcdef")
REQUIRED = {
    "schema_version", "approval_id", "candidate_directory", "candidate_sha256",
    "destination", "destination_before_sha256", "operation",
    "authorization_reference", "expires_at", "rollback_root",
}


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_within(path, root, label):
    try:
        path.relative_to(root)
    except ValueError:
        fail(f"{label} is outside its trusted root")


def regular(path, label):
    if path.is_symlink() or not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
        fail(f"{label} must be a non-symlink regular file")


def hash_value(value, label):
    if not isinstance(value, str) or len(value) != 64 or any(char not in HEX64 for char in value):
        fail(f"{label} must be a lowercase SHA-256")


def load_manifest(path):
    regular(path, "approval manifest")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"unreadable approval manifest: {error}")
    if not isinstance(manifest, dict) or set(manifest) != REQUIRED:
        fail("approval manifest must contain exactly the v1 fields")
    if manifest["schema_version"] != 1 or manifest["operation"] != "replace-file":
        fail("approval manifest is not a v1 replace-file authorization")
    if not isinstance(manifest["approval_id"], str) or not manifest["approval_id"].strip():
        fail("approval_id is required")
    if not isinstance(manifest["authorization_reference"], str) or not manifest["authorization_reference"].strip():
        fail("authorization_reference is required")
    for key in ("candidate_sha256", "destination_before_sha256"):
        hash_value(manifest[key], key)
    try:
        expires = dt.datetime.fromisoformat(manifest["expires_at"].replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        fail("expires_at must be ISO-8601 UTC")
    if expires.tzinfo is None or expires <= dt.datetime.now(dt.timezone.utc):
        fail("approval manifest is expired")
    return manifest


def resolve_paths(manifest):
    candidate_dir, destination, rollback_root = (Path(manifest[key]) for key in ("candidate_directory", "destination", "rollback_root"))
    if not candidate_dir.is_absolute() or not destination.is_absolute() or not rollback_root.is_absolute():
        fail("candidate, destination, and rollback paths must be absolute")
    if candidate_dir.is_symlink() or destination.is_symlink() or rollback_root.is_symlink():
        fail("candidate, destination, and rollback paths must not be symlinks")
    candidate_dir, destination, rollback_root = candidate_dir.resolve(), destination.resolve(), rollback_root.resolve()
    require_within(candidate_dir, CANDIDATE_ROOT, "candidate directory")
    require_within(destination, ACTIVE_ROOT, "destination")
    require_within(rollback_root, ROLLBACK_PARENT, "rollback root")
    if destination.parent.parent != ACTIVE_ROOT or destination.name != "SKILL.md":
        fail("destination must be exactly one direct personal skill SKILL.md")
    candidate, candidate_manifest = candidate_dir / "replacement" / "SKILL.md", candidate_dir / "candidate-manifest.json"
    for path, label in ((candidate, "candidate replacement"), (candidate_manifest, "candidate manifest"), (destination, "destination")):
        regular(path, label)
    if not rollback_root.is_dir() or rollback_root.is_symlink():
        fail("rollback root must be an existing non-symlink directory")
    return candidate_dir, candidate, candidate_manifest, destination, rollback_root


def validate_candidate(candidate, candidate_manifest, destination, manifest):
    try:
        candidate_data = json.loads(candidate_manifest.read_text(encoding="utf-8"))
        mapping = candidate_data["files"]
    except (KeyError, TypeError, json.JSONDecodeError) as error:
        fail(f"candidate manifest is invalid: {error}")
    if candidate_data.get("schema_version") != 1 or candidate_data.get("status") != "non-active":
        fail("candidate is not a non-active v1 package")
    if candidate_data.get("requires_separate_delivery_approval") is not True or len(mapping) != 1:
        fail("candidate lacks its separate-delivery boundary")
    mapping = mapping[0]
    if mapping.get("source") != "replacement/SKILL.md" or mapping.get("operation") != "replace-file":
        fail("candidate mapping is not one replacement SKILL.md")
    declared_destination = Path(mapping.get("destination", ""))
    if declared_destination.is_symlink() or declared_destination.resolve() != destination:
        fail("candidate and approval destination do not match")
    if mapping.get("sha256") != manifest["candidate_sha256"] or sha256(candidate) != manifest["candidate_sha256"]:
        fail("candidate replacement hash does not match approval")
    if candidate_data.get("target_baseline_sha256") != manifest["destination_before_sha256"]:
        fail("candidate baseline does not match approval")


def atomic_write(destination, data, mode):
    fd, temp_name = tempfile.mkstemp(prefix=".skill-install-", dir=destination.parent)
    temp_path = Path(temp_name)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, destination)
        directory_fd = os.open(destination.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def install(manifest_path, apply):
    manifest = load_manifest(manifest_path)
    candidate_dir, candidate, candidate_manifest, destination, rollback_root = resolve_paths(manifest)
    validate_candidate(candidate, candidate_manifest, destination, manifest)
    if sha256(destination) != manifest["destination_before_sha256"]:
        fail("destination baseline hash changed")
    print("PASS: approval and candidate validate")
    print(f"candidate: {candidate}\ndestination: {destination}\nrollback root: {rollback_root}")
    if not apply:
        print("DRY RUN: no destination changed")
        return
    lock_path = destination.with_name(f".{destination.name}.install.lock")
    with lock_path.open("a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            validate_candidate(candidate, candidate_manifest, destination, manifest)
            if sha256(destination) != manifest["destination_before_sha256"]:
                fail("destination changed while waiting for installation lock")
            rollback_dir = rollback_root / f"{manifest['approval_id']}-{uuid.uuid4().hex[:12]}"
            rollback_dir.mkdir(mode=0o700)
            backup = rollback_dir / "SKILL.md.backup"
            shutil.copy2(destination, backup)
            if sha256(backup) != manifest["destination_before_sha256"]:
                fail("backup hash mismatch; destination untouched")
            original_mode = stat.S_IMODE(destination.stat().st_mode)
            atomic_write(destination, candidate.read_bytes(), original_mode)
            installed = sha256(destination)
            if installed != manifest["candidate_sha256"]:
                fail("post-install hash mismatch; stop for manual recovery")
            receipt = {
                "schema_version": 1, "status": "installed-posthash-verified", "approval_id": manifest["approval_id"],
                "authorization_reference": manifest["authorization_reference"], "manifest_sha256": sha256(manifest_path),
                "candidate_directory": str(candidate_dir), "candidate_sha256": manifest["candidate_sha256"],
                "destination": str(destination), "baseline_sha256": manifest["destination_before_sha256"],
                "installed_sha256": installed, "backup": str(backup),
                "installed_at": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
                "non_authority": "receipt proves byte-level delivery only; it is not approval for another change"
            }
            (rollback_dir / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            print(f"PASS: installed-posthash-verified; receipt: {rollback_dir / 'receipt.json'}")
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def rollback(path):
    regular(path, "receipt")
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"unreadable receipt: {error}")
    needed = {"schema_version", "status", "destination", "baseline_sha256", "installed_sha256", "backup"}
    if not needed.issubset(receipt) or receipt["schema_version"] != 1 or receipt["status"] != "installed-posthash-verified":
        fail("not an installer receipt")
    destination, backup = Path(receipt["destination"]).resolve(), Path(receipt["backup"]).resolve()
    require_within(destination, ACTIVE_ROOT, "receipt destination")
    require_within(backup, ROLLBACK_PARENT, "receipt backup")
    regular(destination, "destination")
    regular(backup, "backup")
    for key in ("baseline_sha256", "installed_sha256"):
        hash_value(receipt[key], key)
    lock_path = destination.with_name(f".{destination.name}.install.lock")
    with lock_path.open("a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            if sha256(destination) != receipt["installed_sha256"]:
                fail("destination is no longer this receipt's installed state")
            if sha256(backup) != receipt["baseline_sha256"]:
                fail("backup hash mismatch")
            atomic_write(destination, backup.read_bytes(), stat.S_IMODE(destination.stat().st_mode))
            if sha256(destination) != receipt["baseline_sha256"]:
                fail("rollback posthash mismatch; stop for manual recovery")
            print("PASS: rollback posthash verified")
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", nargs="?")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--rollback")
    args = parser.parse_args()
    if bool(args.manifest) == bool(args.rollback) or (args.rollback and args.apply):
        fail("use either <approval.json> [--apply] or --rollback <receipt.json>")
    if args.rollback:
        rollback(Path(args.rollback).resolve())
    else:
        install(Path(args.manifest).resolve(), args.apply)


if __name__ == "__main__":
    main()
