"""One-off public API/CLI evidence capture; no application state is read via SQL."""
import json
import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'microsoft-agent-framework-work-package-pilot'))
from tests.test_control_plane_black_box import ObservableRunBlackBoxTests as Harness

OUT = Path(__file__).resolve().parent
records = []
lines = []

def now():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds')

def emit(message):
    line = f'{now()} {message}'
    lines.append(line)
    print(line, flush=True)

def capture(label, method, path, actor='actor-authorized', payload=None, port=None):
    status, response, raw = Harness.request(method, path, payload, actor_id=actor, port=port)
    for token in [Harness.fixture_access_token, *Harness.provider.tokens.values()]:
        assert token not in raw, 'Credential leaked into public response'
    records.append({'time': now(), 'label': label, 'transport': 'HTTP', 'method': method,
                    'path': path, 'actorFixture': actor, 'apiPort': port or Harness.api_port,
                    'request': payload, 'httpStatus': status, 'response': response})
    return status, response

apis = []
try:
    Harness.setUpClass()
    test = Harness()
    apis.append(Harness.api)
    emit('BOUNDARY real API + Operator CLI + PostgreSQL; GitHub HTTP fixture')
    status, started = capture('admission', 'POST', '/api/v1/issues/repo-1/43/runs', payload={
        'commandId': str(uuid.uuid4()), 'note': 'Public Ticket 03 proof capture',
        'provenance': {'sourceRevision': 'working-tree-2026-09-11', 'packageRevision': 'locked',
                       'configurationRevision': 'isolated-fixture', 'contractRevision': 'ticket-03'}})
    assert status == 201
    run_id = started['runId']
    emit(f'RUN {run_id} HTTP={status}')
    base = f'/api/v1/runs/{run_id}'
    status, projection = capture('reader observes', 'GET', base, 'actor-observer')
    assert status == 200 and not projection['authorization']['canClaim']
    emit(f'READER GET HTTP={status} canClaim={str(projection["authorization"]["canClaim"]).lower()}')
    initial = projection['control']
    fence = test.fence(initial)
    status, denied = capture('reader cannot claim', 'POST', base+'/control/claim', 'actor-observer', fence)
    assert status == 403 and denied['current'] == initial
    emit(f'READER CLAIM HTTP={status} {denied["code"]}')

    first_port = Harness.api_port
    Harness.start_api(excluded_ports={first_port})
    apis.append(Harness.api)
    emit(f'API PROCESSES pid={apis[0].pid},port={first_port}; pid={apis[1].pid},port={Harness.api_port}')
    claimants = [('actor-authorized', first_port), ('actor-contributor', Harness.api_port)]
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(capture, 'concurrent claim', 'POST', base+'/control/claim', actor, fence, port)
                for actor, port in claimants]
        outcomes = [job.result() for job in jobs]
    assert sorted(r[0] for r in outcomes) == [200, 409]
    winner = next(actor for (actor, _), (status, _) in zip(claimants, outcomes) if status == 200)
    loser = next(actor for (actor, _), (status, _) in zip(claimants, outcomes) if status == 409)
    current = next(result['current'] for status, result in outcomes if status == 200)
    for (actor, _), (status, result) in zip(claimants, outcomes):
        emit(f'RACE {actor} HTTP={status} {result["code"]} holder=github:{result["current"]["holder"]["subjectId"]} epoch={result["current"]["leaseEpoch"]}')

    status, result = capture('non-holder cannot release', 'POST', base+'/control/release', loser, test.fence(current))
    assert status == 409 and result['current'] == current
    emit(f'NON-HOLDER RELEASE HTTP={status} {result["code"]}')
    for field, value, expected in [
        ('targetAttemptId', str(uuid.uuid4()), 'stale-target-attempt'),
        ('expectedRunVersion', 1, 'stale-run-version'),
        ('expectedHeadSha', 'a'*40, 'stale-head-sha'),
        ('leaseEpoch', 0, 'stale-lease-epoch')]:
        stale = {**test.fence(current), field: value}
        status, result = capture(f'stale {field}', 'POST', base+'/control/release', winner, stale)
        assert status == 409 and result['code'] == expected and result['current'] == current
        emit(f'FENCE HTTP={status} {result["code"]} unchanged=true')
    status, events = capture('history after rejected mutations', 'GET', base+'/events', 'actor-observer')
    assert [e['eventType'] for e in events['events']] == ['ImplementationRunStarted', 'ControlLeaseClaimed']
    emit(f'HISTORY AFTER DENIALS positions={[e["position"] for e in events["events"]]} claimEvents=1 releaseEvents=0')

    for api in apis:
        Harness.stop_process(api)
    Harness.provider.tokens['reconnect-winner'] = uuid.uuid4().hex
    Harness.provider.identities['reconnect-winner'] = Harness.provider.identities[winner]
    Harness.start_api(excluded_ports={first_port, Harness.api_port})
    apis.append(Harness.api)
    exit_code, reconnected, raw = Harness.operator_cli('run', '--run-id', run_id, '--actor-id', 'reconnect-winner')
    assert exit_code == 0 and reconnected['control'] == current
    assert reconnected['authorization']['canRelease']
    records.append({'time': now(), 'label': 'same human, new token, API restarted', 'transport': 'Operator CLI',
                    'args': ['run', '--run-id', run_id], 'apiPid': Harness.api.pid,
                    'exitCode': exit_code, 'response': reconnected})
    emit(f'RECONNECT CLI exit={exit_code} newApiPid={Harness.api.pid} sameRun=true sameHolder=true epoch={current["leaseEpoch"]}')

    Harness.provider.identities[winner]['push'] = False
    status, revoked = capture('contributor permission removed upstream', 'POST', base+'/control/release', winner, test.fence(current))
    assert status == 403 and revoked['current']['holder'] is None
    assert revoked['current']['leaseEpoch'] == current['leaseEpoch']+1
    emit(f'REVOKED RELEASE HTTP={status} {revoked["code"]} holder=null epoch={revoked["current"]["leaseEpoch"]}')

    exit_code, worker_output = test.worker('--run-id', run_id, '--worker-id', 'proof-worker',
        '--evidence-note', 'Public actor-kind evidence')
    assert exit_code == 0
    status, projection = capture('worker evidence readback', 'GET', base, 'actor-observer')
    assert status == 200 and projection['executionEvidence'][0]['actor']['kind'] == 'service'
    status, rejected = capture('bot cannot claim human lease', 'POST', base+'/control/claim', 'worker-bot', test.fence(revoked['current']))
    assert status == 403 and rejected['current'] is None
    status, history = capture('canonical history', 'GET', base+'/events', 'actor-observer')
    assert [e['eventType'] for e in history['events']] == ['ImplementationRunStarted', 'ControlLeaseClaimed', 'ControlLeaseRevoked']
    emit('HISTORY ' + ' -> '.join(f'{e["position"]}:{e["eventType"]}' for e in history['events']))
    status, audit = capture('security audit', 'GET', base+'/audit', 'actor-observer')
    assert status == 200 and audit['entries'][-1]['actor']['kind'] == 'service'
    emit(f'IDENTITIES human=github:{current["holder"]["subjectId"]} worker=service botClaim=403')
    emit('PASS all assertions; raw HTTP/CLI responses saved without credentials')
finally:
    for api in apis:
        Harness.stop_process(api)
    Harness.doClassCleanups()
    records.sort(key=lambda row: row['time'])
    raw = ''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in records)
    if hasattr(Harness, 'provider'):
        for token in [Harness.fixture_access_token, *Harness.provider.tokens.values()]:
            assert token not in raw, 'Credential leaked into evidence'
    (OUT/'http-cli-responses.jsonl').write_text(raw)
    (OUT/'proof.log').write_text('\n'.join(lines)+'\n')
