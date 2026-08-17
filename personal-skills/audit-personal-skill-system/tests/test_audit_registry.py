#!/usr/bin/env python3
"""Regression test for generic versus real unresolved skill references."""
import argparse
import json
import runpy
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_registry.py"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", type=Path, default=SCRIPT)
    parser.add_argument("--expected-unresolved", required=True)
    args = parser.parse_args()
    expected = args.expected_unresolved.split(",") if args.expected_unresolved else []
    with tempfile.TemporaryDirectory() as directory:
        repo = Path(directory)
        write(
            repo / "skill-registry/catalog.json",
            json.dumps({"skills": [{"id": "visualize-skill-flow"}, {"id": "read"}]}),
        )
        write(
            repo / "personal-skills/visualize-skill-flow/SKILL.md",
            "---\nname: visualize-skill-flow\ndescription: test\n---\n"
            "Use a declared $skill placeholder, $read, $reader, and $unknown-name.\n",
        )
        write(
            repo / "personal-skills/read/SKILL.md",
            "---\nname: read\ndescription: test\n---\nRead an explicit file.\n",
        )
        output = repo / "output" / "report.json"
        original_argv = sys.argv
        try:
            sys.argv = [str(args.script), "--repo", str(repo), "--output", str(output)]
            runpy.run_path(str(args.script), run_name="__main__")
        finally:
            sys.argv = original_argv
        report = json.loads(output.read_text())
        unresolved = report["unresolved_references"]["visualize-skill-flow"]
        assert unresolved == expected, unresolved
        assert report["declared_references"]["visualize-skill-flow"] == [
            "read",
            "reader",
            "skill",
            "unknown-name",
        ]


if __name__ == "__main__":
    main()
