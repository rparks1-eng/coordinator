#!/usr/bin/env python3
import datetime as dt,hashlib,json,pathlib,shutil,sys
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bad(s):print('FAIL:',s);raise SystemExit(1)
if len(sys.argv)!=2:bad('usage: stage_delivery.py <manifest.json>')
manifest_path=pathlib.Path(sys.argv[1]).resolve()
m=json.loads(manifest_path.read_text())
need={'schema_version','candidate_directory','candidate_sha256','destination','destination_before_sha256','operation','stage_destination','authorization_reference','expires_at','rollback_root'}
if set(m)!=need or m['schema_version']!=1 or m['operation']!='stage-only' or not m['authorization_reference']:bad('invalid or unauthorized manifest')
if dt.datetime.fromisoformat(m['expires_at'].replace('Z','+00:00'))<=dt.datetime.now(dt.timezone.utc):bad('expired')
c=pathlib.Path(m['candidate_directory']).resolve()/'replacement/SKILL.md';d=pathlib.Path(m['destination']).resolve();s=pathlib.Path(m['stage_destination']).resolve()
if not c.is_file() or not d.is_file() or s==d or not s.parent.is_dir():bad('unsafe paths')
if sha(c)!=m['candidate_sha256'] or sha(d)!=m['destination_before_sha256']:bad('hash precondition')
shutil.copy2(c,s)
if sha(s)!=m['candidate_sha256']:bad('stage mismatch')
s.with_name(s.name+'.receipt.json').write_text(json.dumps({'status':'staged','operation':'stage-only','candidate':str(c),'stage':str(s),'sha256':sha(s),'manifest_sha256':sha(manifest_path),'staged_at':dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z'),'evidence_class':'hash-verified-stage','authorization_reference':m['authorization_reference'],'non_authority':'staging receipt is not installation or replacement authority'},indent=2)+'\n')
print('PASS: staged only; active destination unchanged')
