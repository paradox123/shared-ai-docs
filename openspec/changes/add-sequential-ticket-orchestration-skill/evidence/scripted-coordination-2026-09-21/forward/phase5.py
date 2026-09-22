from drive import *
a=status()['tickets']['A']
op('18-revalidation-send-confirmed',{'op':'record','ticket':'A','request_id':a['request_id'],'outcome':'confirmed','evidence':evidence('revalidate-send','Synthetic send confirmed.')})
result=evidence('integration-T2-result','Candidate C1 unchanged; tested T2. Fixture expected operation A 42, actual 42; combined checks pass. Synthetic PR base release/demo, head C1. No new behavior; current C1 completion preserved. No active processes.')
r=call(['report','--packet',a['packet'],'--result',result,'--status','ready','--content-ref','C1','--target-ref','T2'])
print(pathlib.Path(result).read_text())
e=evidence('integration-final-inspection','Coordinator inspected unchanged candidate C1, completion record, combined expected/actual T2 proof, PR base release/demo/head C1 and required checks. Separate fresh synthetic remote observation still T2.')
s=op('19-consume-and-grant',{'op':'consume','ticket':'A','event':r['event'],'next':{'phase':'delivering','content_ref':'C1','target_ref':'T2','current_target_ref':'T2','evidence':e,'instruction':'Synthetic delivery grant only for exact C1 on exact T2 to release/demo. Recheck immediately before merge; stop on movement. Report actual merge, contents mapping, closure and quiescence. No real external action authorized.'}})
a=s['tickets']['A']
op('20-grant-send-confirmed',{'op':'record','ticket':'A','request_id':a['request_id'],'outcome':'confirmed','evidence':evidence('grant-send','Synthetic send confirmed.')})
result=evidence('delivery-result','Synthetic merge M1 includes accepted C1 on T2, release/demo. Synthetic PR fixture-A merged, ticket A explicitly closed. Worker and nested agents quiescent. No real merge or closure happened.')
r=call(['report','--packet',a['packet'],'--result',result,'--status','ready','--content-ref','C1','--target-ref','T2'])
print(pathlib.Path(result).read_text())
op('21-delivery-awaiting-confirmation',{'op':'consume','ticket':'A','event':r['event'],'next':{'phase':'confirming','content_ref':'C1','evidence':evidence('delivery-inspection','Synthetic worker report matches grant C1/T2; ready for independent remote confirmation.')}})
op('22-delivery-confirmed',{'op':'advance','ticket':'A','phase':'cleanup','quiescent':True,'evidence':evidence('delivery-confirmation','Synthetic independent remote evidence confirms release/demo M1 includes C1, fixture PR merged, A closed and no active writers; not real remote verification.'),'delivery':{'target':'release/demo','content_ref':'C1','merge_ref':'M1','pr':'synthetic:fixture-A','closed':True}})
op('23-B-now-eligible',{'op':'prepare','ticket':'B','phase':'registering','allowance':1,'instruction':'Synthetic eligibility proof only: A delivered, begin B from release/demo at M1. No actual create_thread. Original scope local CLI test only.'})
(ROOT/'final-status.json').write_text(json.dumps(status(),indent=2))
