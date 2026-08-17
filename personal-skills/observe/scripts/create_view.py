#!/usr/bin/env python3
"""Create one immutable Markdown view from caller-provided prompt and response files."""
import argparse, datetime as dt, pathlib, uuid

p = argparse.ArgumentParser()
p.add_argument('--prompt-file', required=True)
p.add_argument('--response-file', required=True)
p.add_argument('--host', default='unspecified host')
p.add_argument('--directory', default='observations')
a = p.parse_args()

prompt_path = pathlib.Path(a.prompt_file)
response_path = pathlib.Path(a.response_file)
if not prompt_path.is_file() or not response_path.is_file():
    p.error('prompt-file and response-file must be readable regular files')
prompt, response = prompt_path.read_text(), response_path.read_text()
out_dir = pathlib.Path(a.directory)
out_dir.mkdir(parents=True, exist_ok=True)
stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H-%M-%SZ')
out = out_dir / f'{stamp}--view-{uuid.uuid4().hex[:8]}.md'
out.write_text(f'''# Conversation View

Created: {dt.datetime.now(dt.timezone.utc).isoformat()}\nHost: {a.host}\n
## User prompt

```text
{prompt}
```

## Host response

```text
{response}
```

## Boundary

This is an observation snapshot, not authorization or a command queue.
''')
print(out.resolve())
