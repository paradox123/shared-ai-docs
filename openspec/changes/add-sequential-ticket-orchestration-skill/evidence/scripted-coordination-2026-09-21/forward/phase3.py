from drive import *
response=json.loads((ROOT/'implementation-report-response.json').read_text());event=response['event']
print((ROOT/'implementation-result.md').read_text())
accept=evidence('implementation-acceptance','Coordinator inspected fixture implementation-result.md: criterion expected 42, actual 42, contents C1; sufficient synthetic evidence to delegate change-accepted. No real acceptance implied.')
s=op('07-ready-and-verify',{'op':'consume','ticket':'A','event':event,'next':{'phase':'verifying','instruction':'Apply change-accepted to synthetic C1, perform critical verification then code-review, return current completion record. Honor one sequential nested-agent allowance. This fixture does not run agents.','content_ref':'C1','evidence':accept}})
a=s['tickets']['A'];(ROOT/'verification-packet-path.txt').write_text(a['packet'])
op('08-lost-tool-response',{'op':'record','ticket':'A','request_id':a['request_id'],'outcome':'unknown','evidence':evidence('lost-send','Synthetic tool response lost. Delivery cannot be inferred.')})
op('09-replayed-earlier-worker-event',{'op':'consume','ticket':'A','event':event,'next':{'phase':'verifying','instruction':'Do not dispatch a duplicate command; this tests replay protection.','content_ref':'C1','evidence':accept}})
op('10-no-replacement-during-unknown',{'op':'prepare','ticket':'A','phase':'verifying','instruction':'Attempt a replacement only as a negative CLI test; never dispatch it.','content_ref':'C1','evidence':accept})
op('11-reconciled-delivery',{'op':'record','ticket':'A','request_id':a['request_id'],'outcome':'confirmed','evidence':evidence('reconcile-send','Synthetic destination lookup observed the exact prepared verification packet in worker-A history. Outcome confirmed; do not resend.')})
print(pathlib.Path(a['packet']).read_text())
