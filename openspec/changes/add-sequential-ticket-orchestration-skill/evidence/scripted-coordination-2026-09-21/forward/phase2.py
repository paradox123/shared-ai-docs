from drive import *
s=status();a=s['tickets']['A'];r=evidence('registration','Simulated direct identity lookup confirmed worker-A, owned /tmp/scripted-flow-forward/worktree-A, branch synthetic/A, base T0. No real worker exists.')
op('04-registration-confirmed',{'op':'record','ticket':'A','request_id':a['request_id'],'outcome':'confirmed','evidence':r,'worker':{'thread_id':'synthetic-worker-A','host_id':'local','worktree':str(ROOT/'worktree-A'),'branch':'synthetic/A','base_sha':'T0'}})
s=op('05-implement-A',{'op':'prepare','ticket':'A','phase':'implementing','instruction':'Implement synthetic criterion A; return measured expected/actual result with current contents. No real code edits.'})
a=s['tickets']['A'];op('06-implementation-dispatch-confirmed',{'op':'record','ticket':'A','request_id':a['request_id'],'outcome':'confirmed','evidence':evidence('implement-send','Simulated send confirmed.')})
result=evidence('implementation-result','Contents C1. Criterion: operation A expected 42, fixture actual 42. Changed scope synthetic A. No active processes; no real implementation or runtime proof.')
event=call(['report','--packet',a['packet'],'--result',result,'--status','ready','--content-ref','C1'])
(ROOT/'implementation-report-response.json').write_text(json.dumps(event,indent=2))
