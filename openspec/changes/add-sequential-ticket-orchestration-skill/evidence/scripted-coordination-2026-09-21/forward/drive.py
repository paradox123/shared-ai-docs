import json, pathlib, subprocess, shlex
ROOT=pathlib.Path('/tmp/scripted-flow-forward')
CLI='/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/orchestrate-ticket-batch/scripts/batch_state.py'
LOG=ROOT/'transcript.md'
def call(args):
    cmd=['python3',CLI]+args
    r=subprocess.run(cmd,text=True,capture_output=True)
    with LOG.open('a') as f: f.write('\n```sh\n'+shlex.join(cmd)+'\n```\nExit '+str(r.returncode)+'\n```text\n'+r.stdout+r.stderr+'```\n')
    print(r.returncode,r.stdout.strip(),r.stderr.strip())
    return json.loads(r.stdout) if r.stdout.strip().startswith('{') else None

def status(): return call(['status','--ledger',str(ROOT/'state.json')])
def op(name,body):
    p=ROOT/(name+'.json');p.write_text(json.dumps(body,indent=2))
    with LOG.open('a') as f: f.write('\nInput '+str(p)+'\n```json\n'+p.read_text()+'\n```\n')
    s=status()
    return call(['coordinate','--ledger',str(ROOT/'state.json'),'--expect-revision',str(s['revision']),'--input',str(p)])
def evidence(name,text):
    p=ROOT/(name+'.md');p.write_text('SYNTHETIC LOCAL TEST FIXTURE — no external facts verified.\n'+text+'\n');return str(p)
if __name__=='__main__':
    op('02-blocked-B',{'op':'prepare','ticket':'B','phase':'registering','instruction':'Synthetic registration B after A delivery.'})
    op('03-register-A',{'op':'prepare','ticket':'A','phase':'registering','allowance':1,'instruction':'Synthetic A fixture. Scope /tmp/scripted-flow-forward only. Target release/demo, base T0, owned synthetic branch/worktree. Implement acceptance criterion: operation A returns expected result. Original authority local CLI simulation only. No tools/tasks/network/subagents. Runtime profile not exercised.'})
