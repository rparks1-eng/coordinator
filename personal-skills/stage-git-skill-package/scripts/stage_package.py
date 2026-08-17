#!/usr/bin/env python3
"""Stage one repository skill into an inactive directory."""
import argparse
import hashlib
import io
import json
import subprocess
import tarfile
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("--repo", required=True)
parser.add_argument("--commit", required=True)
parser.add_argument("--skill", required=True)
parser.add_argument("--destination", required=True)
parser.add_argument("--expected-archive-sha256", required=True)
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

repo = Path(args.repo).resolve()
destination = Path(args.destination).resolve()
tree = f"personal-skills/{args.skill}"
if not repo.joinpath(".git").exists():
    raise SystemExit("--repo must be a local Git working tree")
if Path(args.skill).name != args.skill or args.skill in {"", ".", ".."}:
    raise SystemExit("--skill must be one direct skill folder name")

check = subprocess.run(
    ["git", "-C", str(repo), "cat-file", "-e", f"{args.commit}:{tree}/SKILL.md"],
    capture_output=True,
    text=True,
)
if check.returncode:
    raise SystemExit("skill is missing at the pinned commit")

archive = subprocess.run(
    ["git", "-C", str(repo), "archive", args.commit, tree],
    check=True,
    capture_output=True,
).stdout
digest = hashlib.sha256(archive).hexdigest()
if digest != args.expected_archive_sha256.lower():
    raise SystemExit("archive hash does not match --expected-archive-sha256")

if args.apply:
    if destination.exists() and any(destination.iterdir()):
        raise SystemExit("destination must be empty")
    prefix = f"{tree}/"
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        members = tar.getmembers()
        if not members or any(
            not member.name.startswith(prefix)
            or Path(member.name).is_absolute()
            or ".." in Path(member.name).parts
            or member.issym()
            or member.islnk()
            for member in members
        ):
            raise SystemExit("archive contains an unsafe or unexpected entry")
        destination.mkdir(parents=True, exist_ok=True)
        tar.extractall(destination, members=members)

print(json.dumps({
    "repo": str(repo),
    "commit": args.commit,
    "skill": args.skill,
    "archive_sha256": digest,
    "destination": str(destination),
    "staged": args.apply,
    "staged_root": str(destination / tree),
    "non_authority": "staging only; no active installation",
}))
