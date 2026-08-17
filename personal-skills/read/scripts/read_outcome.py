#!/usr/bin/env python3
"""Read one explicit regular outcome file without directory discovery."""
import datetime, hashlib, pathlib, sys

if len(sys.argv) != 2:
    raise SystemExit('usage: read_outcome.py <outcome-file>')
raw = pathlib.Path(sys.argv[1])
if raw.is_symlink() or not raw.is_file():
    raise SystemExit('refusing non-regular, missing, or symlink outcome file')
path = raw.resolve()
data = path.read_bytes()
digest = hashlib.sha256(data).hexdigest()
timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
print(
    '# Handoff v1\n\n'
    '- producer: `read`\n'
    f'- artifact_path: `{path}`\n'
    f'- sha256: `{digest}`\n'
    f'- read_at: `{timestamp}`\n'
    '- evidence_class: `exact-read`\n'
    '- non_authority: `read-only; no selection, approval, staging, or delivery authority`\n\n'
    f'# Outcome contents\n\n{data.decode("utf-8")}')
