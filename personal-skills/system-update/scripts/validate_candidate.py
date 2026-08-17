#!/usr/bin/env python3
import hashlib,json,pathlib,sys
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def bad(s): print('FAIL:',s);raise SystemExit(1)
root=pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)==2 else bad('usage: validate_candidate.py <directory>')
for rel in ('osUpdate.md','replacement/SKILL.md','candidate-manifest.json','EVIDENCE.md','VALIDATION.md'):
 if not (root/rel).is_file():bad('missing '+rel)
m=json.loads((root/'candidate-manifest.json').read_text());f=m.get('files',[])
if m.get('schema_version')!=1 or m.get('status')!='non-active' or m.get('requires_separate_delivery_approval') is not True:bad('invalid status')
if len(f)!=1 or f[0].get('source')!='replacement/SKILL.md' or f[0].get('operation')!='replace-file':bad('invalid mapping')
if f[0].get('sha256')!=sha(root/'replacement/SKILL.md'):bad('hash mismatch')
if not pathlib.PurePath(f[0].get('destination','')).is_absolute():bad('destination not absolute')
cover=(root/'osUpdate.md').read_text()
if 'non-active' not in cover or f[0]['destination'] not in cover or 'Injector must not deliver without a separate hash-bound approval' not in cover:bad('cover incomplete')
print('PASS: static candidate checks; no delivery authorization granted')
