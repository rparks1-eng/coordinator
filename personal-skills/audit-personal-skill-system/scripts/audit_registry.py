#!/usr/bin/env python3
"""Read-only structural evidence for a Coordinator personal-skill registry."""
import argparse, hashlib, json, re, sys
from collections import defaultdict
from pathlib import Path

REF=re.compile(r'\$([a-z][a-z0-9-]*)\b')
GENERIC_REFERENCE_PLACEHOLDERS = {"skill"}
def fail(x): print('FAIL:',x,file=sys.stderr); raise SystemExit(1)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(); p.add_argument('--repo',required=True,type=Path); p.add_argument('--output',required=True,type=Path); a=p.parse_args(); repo=a.repo.resolve(); catalog_path=repo/'skill-registry/catalog.json'; root=repo/'personal-skills'
 if not catalog_path.is_file() or not root.is_dir(): fail('missing committed registry')
 data=json.loads(catalog_path.read_text()); records=data.get('skills',[]); names=defaultdict(list); trees=defaultdict(list); findings=[]; refs=defaultdict(list); ids={r['id'] for r in records}
 for r in records:
  skill=root/r['id']/'SKILL.md'
  if not skill.is_file(): findings.append({'skill':r['id'],'kind':'missing-snapshot','evidence':str(skill)}); continue
  text=skill.read_text(errors='replace'); words=len(text.split()); names[r.get('declared_name',r['id'])].append(r['id']); trees[r.get('tree_sha256','')].append(r['id'])
  if not text.startswith('---\n') or 'description:' not in text.split('---',2)[1]: findings.append({'skill':r['id'],'kind':'incomplete-metadata','evidence':'SKILL.md frontmatter'})
  if words>2500: findings.append({'skill':r['id'],'kind':'large-router','evidence':f'{words} words'})
  for x in REF.findall(text): refs[r['id']].append(x)
 for name,group in names.items():
  if len(group)>1: findings.append({'kind':'name-collision','name':name,'skills':group,'status':'needs-owner-decision'})
 for tree,group in trees.items():
  if tree and len(group)>1: findings.append({'kind':'exact-duplicate','skills':group,'status':'alias-candidate'})
 unresolved={k:sorted(unknown) for k,v in refs.items() if (unknown := set(v)-ids-GENERIC_REFERENCE_PLACEHOLDERS)}
 report={'schema_version':1,'registry_skill_count':len(records),'registry_catalog_sha256':sha(catalog_path),'findings':findings,'declared_references':{k:sorted(set(v)) for k,v in refs.items()},'unresolved_references':unresolved,'limits':'structural evidence only; no semantic redundancy, quality, or promotion decision'}
 out=a.output.resolve(); out.parent.mkdir(parents=True,exist_ok=False); out.write_text(json.dumps(report,indent=2)+'\n'); print(out)
if __name__=='__main__': main()
