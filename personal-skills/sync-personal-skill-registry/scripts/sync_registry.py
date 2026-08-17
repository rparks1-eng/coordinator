#!/usr/bin/env python3
"""Capture portable direct Codex skills into a scoped Coordinator Git registry."""
import argparse, hashlib, json, os, re, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_ROOT = Path('/Users/brandonparks/.codex/skills')
TEXT = {'.md','.py','.js','.mjs','.ts','.json','.yaml','.yml','.toml','.txt','.svg'}
ALLOWED = TEXT | {'.png','.jpg','.jpeg','.webp'}
SECRET = re.compile(r'(?:-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\b(?:sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,}|AIza[A-Za-z0-9_-]{20,})\b|(?i:(?:api[_-]?key|secret|token|password)\s*[:=]\s*["\']?[A-Za-z0-9_-]{12,}))')
CLI = re.compile(r'(?<![\w.-])(python3|node|npm|npx|git|gh|yt-dlp|ollama|pdftotext|ffmpeg)(?![\w.-])')
API = re.compile(r'\b([A-Z][A-Z0-9_]*(?:API|TOKEN|KEY))\b')

def bad(x): print('FAIL:',x,file=sys.stderr); raise SystemExit(1)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def safe_text(p):
    data=p.read_bytes()
    if b'\0' in data: bad(f'binary text file: {p}')
    text=data.decode('utf-8')
    if SECRET.search(text): bad(f'secret-like value: {p}')
    return text
def files(skill):
    out=[]
    for cur, dirs, names in os.walk(skill, followlinks=False):
        dirs[:]=[d for d in dirs if not d.startswith('.') and d not in {'__pycache__','node_modules'}]
        for name in names:
            p=Path(cur)/name
            if p.parent.name == 'scripts' and name.startswith('test_'):
                continue
            if p.is_symlink() or not p.is_file(): bad(f'non-regular source: {p}')
            if p.suffix.lower() not in ALLOWED and p.name not in {'LICENSE','NOTICE'}: bad(f'unsupported or binary source: {p}')
            if p.suffix.lower() in TEXT: safe_text(p)
            out.append(p)
    return sorted(out)
def git(repo,*args): return subprocess.run(['git','-C',str(repo),*args],text=True,capture_output=True)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',required=True,type=Path); ap.add_argument('--source-root',type=Path,default=DEFAULT_ROOT); ap.add_argument('--write',action='store_true'); ap.add_argument('--commit',action='store_true'); ap.add_argument('--message'); a=ap.parse_args()
    if a.commit and (not a.write or not a.message): bad('--commit requires --write and --message')
    repo=a.repo.resolve(); root=a.source_root.resolve()
    if root != DEFAULT_ROOT.resolve(): bad('non-default roots require an owner-reviewed policy update; not imported automatically')
    if not (repo/'.git').exists(): bad('repository is not a Git worktree')
    skill_dirs=[p for p in sorted(root.iterdir()) if p.is_dir() and not p.name.startswith('.') and (p/'SKILL.md').is_file() and not (p/'SKILL.md').is_symlink()]
    records=[]; adapters={}
    for d in skill_dirs:
        parts=files(d); hashes={str(p.relative_to(d)):sha(p) for p in parts}; blob=''.join(hashes[k] for k in sorted(hashes)); tree=hashlib.sha256(blob.encode()).hexdigest()
        skill=safe_text(d/'SKILL.md'); name=next((x.split(':',1)[1].strip() for x in skill.splitlines() if x.startswith('name:')),d.name)
        records.append({'id':d.name,'declared_name':name,'origin':str(d),'tree_sha256':tree,'files':hashes,'status':'captured','duplicate_of':None})
        adapters[d.name]={'commands':sorted(set(CLI.findall(skill))),'environment_names':sorted(set(API.findall(skill))),'credentials':'not included','activation_status':'not projected'}
    seen={}
    for r in records:
        if r['tree_sha256'] in seen: r['status']='alias'; r['duplicate_of']=seen[r['tree_sha256']]
        else: seen[r['tree_sha256']]=r['id']
    catalog={'schema_version':1,'captured_at':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'source_root':str(root),'skills':records,'excluded_roots':['shared-agent','plugin-cache','Coordinator candidates','ChatGPT/Git worktrees pending provenance review']}
    print(json.dumps({'skills':len(records),'exact_aliases':sum(r['status']=='alias' for r in records),'write':a.write},indent=2))
    if not a.write:return
    dest=repo/'personal-skills'; reg=repo/'skill-registry'
    if dest.exists() or reg.exists(): bad('registry paths already exist; review or move prior registry before recapturing')
    for r in records:
        if r['status']=='alias': continue
        source=root/r['id']; target=dest/r['id']
        for file in files(source):
            out=target/file.relative_to(source); out.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(file,out)
    reg.mkdir(); (reg/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n'); (reg/'adapter-requirements.json').write_text(json.dumps(adapters,indent=2)+'\n'); (reg/'CONTEXT.md').write_text('# Personal skill registry\n\nPortable source snapshots and declarative adapter requirements. See `catalog.json`; this directory does not activate skills.\n')
    if a.commit:
        if git(repo,'diff','--cached','--name-only').stdout.strip(): bad('Git index already has entries; refusing mixed commit')
        add=git(repo,'add','--','personal-skills','skill-registry')
        if add.returncode: bad(add.stderr.strip())
        check=git(repo,'diff','--cached','--check')
        if check.returncode: bad(check.stdout+check.stderr)
        commit=git(repo,'commit','-m',a.message)
        if commit.returncode: bad(commit.stderr.strip())
        print(commit.stdout.strip())
if __name__=='__main__': main()
