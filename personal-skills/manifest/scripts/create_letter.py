#!/usr/bin/env python3
"""Render a non-authorizing file delivery letter to stdout."""
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--sender', required=True)
parser.add_argument('--recipient', required=True)
parser.add_argument('--instruction', required=True)
parser.add_argument('--subject', default='File instruction')
args = parser.parse_args()

for label, value in (('sender', args.sender), ('recipient', args.recipient)):
    if not value or value.endswith('/') or '*' in value or '?' in value or '://' in value:
        parser.error(f'unsafe or ambiguous {label} filename')

print(f'''# File Delivery Letter

**From:** `{args.sender}`
**To:** `{args.recipient}`
**Subject:** {args.subject}

## Instructions

```
{args.instruction}
```

## Boundary

This letter communicates a requested change or delivery. It does not authorize, copy, replace, execute, or delete any file.
''')
