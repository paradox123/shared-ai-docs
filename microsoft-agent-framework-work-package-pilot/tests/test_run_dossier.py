"""Ticket 09 acceptance through authorized HTTP and separate process clients."""
import unittest
import http.client
import json
import os
import base64
import hashlib
import threading
import subprocess
import signal
import time
import io
import zipfile
import uuid
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from tests import test_control_plane_black_box as harness
from tests import test_fake_codex_attempt as fake_tests


class RunDossierTests(harness.ControlPlaneProcessHarness, unittest.TestCase):
    @classmethod
    def start_api(cls, **kwargs):
        fixture = json.loads(cls.fixture_path.read_text())
        if len(fixture['redactionPolicy']['controlledCanaries']) == 2:
            fixture['redactionPolicy']['version'] = 'controlled-dossier-canary-v1'
            fixture['redactionPolicy']['controlledCanaries'] += [
                {'name': 'authorization', 'value': 'Bearer wpcp-auth-canary-v1'},
                {'name': 'credential', 'value': 'wpcp-password-canary-v1'},
                {'name': 'email', 'value': 'canary.person@wpcp.invalid'},
                {'name': 'person', 'value': 'Wpcp Canary Person'},
            ]
            cls.fixture_path.write_text(json.dumps(fixture))
        cls.artifact_root = Path(cls.scratch.name) / 'artifacts'
        previous = os.environ.get('WPCP_ARTIFACT_ROOT')
        os.environ['WPCP_ARTIFACT_ROOT'] = str(cls.artifact_root)
        try:
            super().start_api(**kwargs)
        finally:
            if previous is None:
                os.environ.pop('WPCP_ARTIFACT_ROOT', None)
            else:
                os.environ['WPCP_ARTIFACT_ROOT'] = previous

    def run_evidence_worker(self, run_id, port, *extra, timeout=90):
        return harness.command_output(self.fake_worker_args(run_id, port, *extra), timeout=timeout,
            env={**os.environ, 'WPCP_ARTIFACT_ROOT': str(self.artifact_root)})

    def evidence_provider(self, count=4, large_bytes=0, sensitive_binary=True, jsonl=False, binary_encoding="utf-8", terminal_result=False):
        policy = json.loads(self.fixture_path.read_text())['redactionPolicy']
        canaries = ' '.join(item['value'] for item in policy['controlledCanaries'])
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def do_PUT(self):
                request = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                operation = self.path.rsplit('/', 1)[-1]
                if self.path.startswith('/operations/'):
                    receipt = dict(request, contractVersion='AgentSessionAdapter/v1', operationKey=operation,
                        processStatus='completed', processId=None, reconciliation='reconciled', effects=[],
                        response={'text': canaries + 'x' * large_bytes, 'artifact': {
                            'mediaType': 'text/plain', 'contentBase64': base64.b64encode(canaries.encode()).decode()}})
                    body = json.dumps(receipt).encode()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
                events = [{'sequence': i + 1, 'type': 'message', 'data': {
                    'text': f'observation {i + 1} ' + canaries + ('x' * large_bytes if i == 0 else '')}}
                    for i in range(count)]
                for media, content in [('text/plain', ('diagnostic ' + canaries).encode()),
                                       ('application/octet-stream', bytes(range(256)) * 1024),
                                       ('application/octet-stream', b'\x00' + canaries.encode(binary_encoding))]:
                    if media == 'application/octet-stream' and content.startswith(b'\x00wpcp') and not sensitive_binary:
                        continue
                    events.append({'sequence': len(events) + 1, 'type': 'artifact', 'data': {
                        'mediaType': media, 'contentBase64': base64.b64encode(content).decode()}})
                if jsonl:
                    escaped = ''.join('\\u%04x' % ord(c) for c in canaries)
                    content = ('{"message":"' + escaped + '"}\n').encode()
                    events.append({'sequence': len(events) + 1, 'type': 'artifact', 'data': {
                        'mediaType': 'application/x-ndjson', 'contentBase64': base64.b64encode(content).decode()}})
                events.append({'sequence': len(events) + 1, 'type': 'process-exit', 'data': {
                    'exitCode': 17, 'exception': canaries}})
                if terminal_result:
                    events[-1] = {'sequence': len(events), 'type': 'result', 'data': {
                        'schemaVersion': 'fake-worker-result/v1', 'status': 'blocked', 'reason': canaries + 'x' * large_bytes}}
                body = json.dumps({'contractVersion': 'AgentSessionAdapter/v1', 'operationKey': operation,
                    'sessionId': str(uuid.uuid5(uuid.NAMESPACE_URL, operation)), 'events': events}).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                try:
                    self.wfile.write(body)
                except (BrokenPipeError, ConnectionResetError):
                    pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return server.server_port

    def artifact_bytes(self, run_id, artifact_id, actor='actor-observer'):
        connection = http.client.HTTPConnection('127.0.0.1', self.api_port, timeout=20)
        try:
            connection.request('GET', f'/api/v1/runs/{run_id}/artifacts/{artifact_id}', headers={
                'Authorization': 'Bearer ' + self.provider.tokens[actor],
                'X-Wpcp-Fixture-Access': self.fixture_access_token})
            response = connection.getresponse()
            return response.status, response.read()
        finally:
            connection.close()

    def test_artifacts_are_decoded_redacted_and_checksum_bound_before_publication(self):
        run_id = self.new_run()
        worker = self.run_evidence_worker(run_id, self.evidence_provider())
        self.assertEqual(0, worker.returncode, worker.stdout + worker.stderr)
        status, manifest, raw = self.request('GET', f'/api/v1/runs/{run_id}/artifacts')
        self.assertEqual(200, status, raw)
        self.assertEqual(3, len(manifest['artifacts']))
        available = [a for a in manifest['artifacts'] if a['availability'] == 'available']
        self.assertEqual(2, len(available))
        for artifact in available:
            status, content = self.artifact_bytes(run_id, artifact['artifactId'])
            self.assertEqual(200, status)
            self.assertEqual(artifact['sha256'], hashlib.sha256(content).hexdigest())
            self.assertEqual(len(content), artifact['sizeBytes'])
            if artifact['mediaType'] == 'application/octet-stream':
                self.assertEqual(bytes(range(256)) * 1024, content)
            else:
                self.assertIn(b'[REDACTED:', content)
        withheld = next(a for a in manifest['artifacts'] if a['availability'] == 'withheld')
        self.assertEqual('binary-controlled-canary', withheld['reason'])
        self.assertTrue(withheld['redaction']['occurred'])
        self.assertEqual(410, self.artifact_bytes(run_id, withheld['artifactId'])[0])
        self.assertEqual(403, self.artifact_bytes(run_id, available[0]['artifactId'], 'actor-unauthorized')[0])
        for canary in json.loads(self.fixture_path.read_text())['redactionPolicy']['controlledCanaries']:
            self.assertNotIn(canary['value'], raw)

    def evidence_pause(self, run_id, port, hook):
        path = Path(self.scratch.name) / f'{run_id}-{hook}.log'
        output = path.open('w')
        self.addCleanup(output.close)
        process = subprocess.Popen(self.fake_worker_args(run_id, port, '--pause-at', hook),
            stdout=output, stderr=output, start_new_session=True,
            env={**os.environ, 'WPCP_ARTIFACT_ROOT': str(self.artifact_root)})
        self.addCleanup(self.stop_process, process)
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            if hook in path.read_text():
                return process
            if process.poll() is not None:
                self.fail('Worker exited before boundary: ' + path.read_text())
            time.sleep(.05)
        self.fail('Worker missed boundary')

    def test_large_original_is_externalized_and_recovery_uses_immutable_safe_bytes(self):
        run_id, port = self.new_run(), self.evidence_provider(large_bytes=100000)
        worker = self.evidence_pause(run_id, port, 'after-session-mapping')
        run = self.read_run(run_id)
        self.assertLess(len(json.dumps(run)), 20000, 'Large original leaked into workflow projection')
        session = next(a['session'] for a in run['attempts'] if a.get('session'))
        self.assertIn('artifactId', session['observedResponse'])
        os.killpg(worker.pid, signal.SIGKILL)
        worker.wait(timeout=10)
        recovered = self.run_evidence_worker(run_id, port)
        self.assertEqual(0, recovered.returncode, recovered.stdout)
        final = self.read_run(run_id)
        self.assertEqual('process-failure', final['state'])
        self.assertEqual(session['sessionId'], next(a['session']['sessionId'] for a in final['attempts'] if a.get('session')))
        _, page, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        observation = next(e for e in page['events'] if e['payload'].get('sourceSequence') == 1)
        self.assertLess(len(json.dumps(observation)), 4000)
        artifact_id = observation['payload']['data']['artifactId']
        status, content = self.artifact_bytes(run_id, artifact_id)
        self.assertEqual(200, status)
        self.assertGreater(len(content), 100000)
        self.assertIn(b'[REDACTED:', content)

    def test_missing_or_corrupt_bytes_block_the_public_qualification_prerequisite(self):
        run_id = self.new_run()
        self.assertEqual(0, self.run_evidence_worker(run_id,
            self.evidence_provider(sensitive_binary=False)).returncode)
        path = f'/api/v1/runs/{run_id}/artifacts'
        _, original, _ = self.request('GET', path)
        self.assertTrue(original['qualificationEligible'])
        artifact = original['artifacts'][0]
        blob = self.artifact_root / artifact['sha256']
        content = blob.read_bytes()
        for fault in ('missing', 'corrupt'):
            with self.subTest(fault=fault):
                if fault == 'missing':
                    blob.unlink()
                else:
                    blob.write_bytes(b'corrupt fixture')
                _, manifest, _ = self.request('GET', path)
                self.assertFalse(manifest['qualificationEligible'])
                broken = next(a for a in manifest['artifacts'] if a['artifactId'] == artifact['artifactId'])
                self.assertEqual(fault, broken['availability'])
                self.assertTrue(broken['redaction']['policyVersion'])
                status, body = self.artifact_bytes(run_id, artifact['artifactId'])
                self.assertEqual(410, status)
                self.assertEqual(fault, json.loads(body)['availability'])
                blob.write_bytes(content)

    def export_bytes(self, run_id, actor='actor-observer'):
        connection = http.client.HTTPConnection('127.0.0.1', self.api_port, timeout=30)
        try:
            connection.request('GET', f'/api/v1/runs/{run_id}/export', headers={
                'Authorization': 'Bearer ' + self.provider.tokens[actor],
                'X-Wpcp-Fixture-Access': self.fixture_access_token})
            response = connection.getresponse()
            return response.status, response.read()
        finally:
            connection.close()

    def test_export_contains_portable_history_projection_artifacts_and_provenance(self):
        run_id = self.new_run()
        self.assertEqual(0, self.run_evidence_worker(run_id,
            self.evidence_provider(large_bytes=100000),
            '--durable-task-orchestration-id', 'ticket-09-correlation').returncode)
        status, body = self.export_bytes(run_id)
        self.assertEqual(200, status)
        with zipfile.ZipFile(io.BytesIO(body)) as dossier:
            manifest = json.loads(dossier.read('manifest.json'))
            self.assertEqual('wpcp-run-dossier/v1', manifest['formatVersion'])
            for name, digest in manifest['files'].items():
                self.assertEqual(digest, hashlib.sha256(dossier.read(name)).hexdigest())
            projection = json.loads(dossier.read('projection.json'))
            history = json.loads(dossier.read('history.json'))
            self.assertEqual('process-failure', projection['state'])
            self.assertEqual(list(range(1, projection['lastPosition'] + 1)), [e['position'] for e in history])
            self.assertEqual('r1', manifest['provenance']['sourceRevision'])
            self.assertIn('AgentSessionAdapter/v1', manifest['adapterContracts'])
            self.assertTrue(manifest['runtime'])
            self.assertTrue(any(e['durableTaskOrchestrationId'] == 'ticket-09-correlation'
                for e in manifest['frameworkCorrelation']))
            for artifact in manifest['artifacts']:
                if artifact['availability'] == 'available':
                    self.assertEqual(artifact['sha256'], hashlib.sha256(dossier.read('artifacts/' + artifact['sha256'])).hexdigest())
        self.assertEqual(403, self.export_bytes(run_id, 'actor-unauthorized')[0])
        _, checksums, _ = self.request('GET', f'/api/v1/runs/{run_id}/checksums')
        self.assertEqual(manifest['files']['history.json'], checksums['historySha256'])
        self.assertEqual(manifest['files']['projection.json'], checksums['projectionSha256'])
        path = Path(self.scratch.name) / 'cli-dossier.zip'
        exit_code, output, _ = self.operator_cli('export', '--run-id', run_id, '--output', str(path),
            '--actor-id', 'actor-observer')
        self.assertEqual(0, exit_code, output)
        self.assertTrue(zipfile.is_zipfile(path))

    def fresh_components(self):
        fresh = type('FreshDossierComponents', (RunDossierTests,), {})
        self.addCleanup(fresh.doClassCleanups)
        fresh.setUpClass()
        return fresh()

    def restore(self, data):
        path = Path(self.scratch.name) / ('restore-' + uuid.uuid4().hex + '.zip')
        path.write_bytes(data)
        return harness.command_output(['dotnet', str(harness.WORKER_DLL), '--restore-dossier', str(path),
            '--fixture', str(self.fixture_path)], env={**os.environ,
                'WPCP_CONNECTION_STRING': self.connection_string, 'WPCP_ARTIFACT_ROOT': str(self.artifact_root)})

    def test_restore_in_fresh_components_preserves_public_checksums_and_is_read_only(self):
        run_id = self.new_run()
        self.assertEqual(0, self.run_evidence_worker(run_id, self.evidence_provider(large_bytes=100000)).returncode)
        _, data = self.export_bytes(run_id)
        _, expected, _ = self.request('GET', f'/api/v1/runs/{run_id}/checksums')
        fresh = self.fresh_components()
        result = fresh.restore(data)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual('dossier-restored', json.loads(result.stdout)['code'])
        status, restored, _ = fresh.request('GET', f'/api/v1/runs/{run_id}/checksums')
        self.assertEqual(200, status)
        self.assertEqual(expected, restored)
        run = fresh.read_run(run_id)
        self.assertEqual('process-failure', run['state'])
        self.assertFalse(run['authorization']['canClaim'])
        control = run['control']
        status, decision, _ = fresh.request('POST', f'/api/v1/runs/{run_id}/control/claim', {
            'targetAttemptId': control['targetAttemptId'], 'expectedRunVersion': control['runVersion'],
            'expectedHeadSha': control['headSha'], 'leaseEpoch': control['leaseEpoch']})
        self.assertEqual(409, status)
        self.assertEqual('restored-dossier-read-only', decision['code'])
        self.assertNotEqual(0, fresh.restore(data).returncode)
        self.assertEqual(403, fresh.request('GET', f'/api/v1/runs/{run_id}/events', actor_id='actor-unauthorized')[0])
        for artifact in expected['artifacts']:
            status, content = fresh.artifact_bytes(run_id, artifact['artifactId'])
            if artifact['availability'] == 'available':
                self.assertEqual(200, status)
                self.assertEqual(artifact['sha256'], hashlib.sha256(content).hexdigest())
            else:
                self.assertEqual(410, status)
        _, source_page, _ = self.request('GET', f'/api/v1/runs/{run_id}/events?after=4&limit=3')
        _, restored_page, _ = fresh.request('GET', f'/api/v1/runs/{run_id}/events?after=4&limit=3')
        self.assertEqual(source_page, restored_page)

    def test_restored_holder_and_pending_transfer_do_not_enable_control(self):
        run_id = self.new_run()
        request_id = str(uuid.uuid4())
        for action, actor in (('claim', 'actor-authorized'), ('request-transfer', 'actor-contributor')):
            control = self.read_run(run_id)['control']
            status, decision, _ = self.request('POST', f'/api/v1/runs/{run_id}/control/{action}', {
                'targetAttemptId': control['targetAttemptId'], 'expectedRunVersion': control['runVersion'],
                'expectedHeadSha': control['headSha'], 'leaseEpoch': control['leaseEpoch'],
                'requestId': request_id, 'reason': 'Preserve responsibility in historical evidence'}, actor_id=actor)
            self.assertEqual(200, status, decision)
        status, data = self.export_bytes(run_id)
        self.assertEqual(200, status)
        fresh = self.fresh_components()
        result = fresh.restore(data)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        _, expected, _ = fresh.request('GET', f'/api/v1/runs/{run_id}/checksums')
        original_control = self.read_run(run_id)['control']
        for actor in ('actor-authorized', 'actor-contributor'):
            run = fresh.read_run(run_id, actor)
            self.assertTrue(run['authorization']['historical'])
            self.assertEqual(original_control, run['control'])
            for capability in ('canClaim', 'canRelease', 'canRequestTransfer', 'canDecideTransfer', 'canForceTakeover'):
                with self.subTest(actor=actor, capability=capability):
                    self.assertFalse(run['authorization'][capability])
            for action in ('request-transfer', 'approve-transfer', 'reject-transfer', 'force-takeover'):
                status, decision, _ = fresh.request('POST', f'/api/v1/runs/{run_id}/control/{action}', {
                    'targetAttemptId': original_control['targetAttemptId'],
                    'expectedRunVersion': original_control['runVersion'],
                    'expectedHeadSha': original_control['headSha'], 'leaseEpoch': original_control['leaseEpoch'],
                    'requestId': request_id, 'reason': 'Attempt to change historical ownership'}, actor_id=actor)
                self.assertEqual(409, status, decision)
                self.assertEqual('restored-dossier-read-only', decision['code'])
        _, after, _ = fresh.request('GET', f'/api/v1/runs/{run_id}/checksums')
        self.assertEqual(expected, after)

    def test_restore_rejects_dropped_artifact_inventory_and_corrupt_core_without_publication(self):
        run_id = self.new_run()
        self.assertEqual(0, self.run_evidence_worker(run_id, self.evidence_provider()).returncode)
        _, data = self.export_bytes(run_id)
        fresh = self.fresh_components()
        for fault in ('dropped-inventory', 'corrupt-history'):
            changed = io.BytesIO()
            with zipfile.ZipFile(io.BytesIO(data)) as source, zipfile.ZipFile(changed, 'w') as target:
                for name in source.namelist():
                    content = source.read(name)
                    if fault == 'dropped-inventory':
                        if name.startswith('artifacts/'):
                            continue
                        if name == 'manifest.json':
                            manifest = json.loads(content)
                            manifest['artifacts'] = []
                            manifest['files'] = {k: v for k, v in manifest['files'].items() if not k.startswith('artifacts/')}
                            content = json.dumps(manifest).encode()
                    elif name == 'history.json':
                        content = b'[]'
                    target.writestr(name, content)
            result = fresh.restore(changed.getvalue())
            self.assertNotEqual(0, result.returncode, fault)
            self.assertEqual(404, fresh.request('GET', f'/api/v1/runs/{run_id}')[0])

    def test_more_than_ten_thousand_events_reconnect_after_api_and_worker_kills_and_restore(self):
        run_id, port = self.new_run(), self.evidence_provider(count=10005, large_bytes=200000)
        before_commit = self.evidence_pause(run_id, port, 'after-session-start')
        os.killpg(before_commit.pid, signal.SIGKILL)
        before_commit.wait(timeout=10)
        middle = self.evidence_pause(run_id, port, 'after-source-sequence-5000')
        exit_code, first, raw_client = self.operator_cli('events', '--run-id', run_id, '--after', '0',
            '--actor-id', 'actor-observer')
        self.assertEqual(0, exit_code, raw_client)
        acknowledged = first['nextAfter']
        self.assertEqual(250, acknowledged)
        os.killpg(middle.pid, signal.SIGKILL)
        middle.wait(timeout=10)
        cls = type(self)
        os.killpg(cls.api.pid, signal.SIGKILL)
        cls.api.wait(timeout=10)
        cls.start_api(excluded_ports={cls.api_port})
        stream = self.open_stream(run_id, acknowledged)
        self.assertEqual(200, stream.status)
        log_path = Path(self.scratch.name) / 'replacement-worker.log'
        with log_path.open('w') as log:
            worker = subprocess.Popen(self.fake_worker_args(run_id, port), stdout=log, stderr=log,
                start_new_session=True, env={**os.environ, 'WPCP_ARTIFACT_ROOT': str(self.artifact_root)})
            self.addCleanup(self.stop_process, worker)
            streamed = []
            deadline = time.monotonic() + 150
            while time.monotonic() < deadline:
                frame = self.frame(stream)
                if frame == ': keepalive':
                    continue
                self.assertTrue(frame, 'SSE ended before terminal failure')
                event = json.loads(next(line[6:] for line in frame.splitlines() if line.startswith('data: ')))
                streamed.append(event)
                if event['eventType'] == 'AgentAttemptCompleted':
                    break
            self.assertEqual('AgentAttemptCompleted', streamed[-1]['eventType'])
            self.assertEqual(0, worker.wait(timeout=10), log_path.read_text())
        _, final, _ = self.request('GET', f'/api/v1/runs/{run_id}')
        self.assertEqual('process-failure', final['state'])
        self.assertGreater(final['lastPosition'], 10000)
        self.assertEqual(list(range(acknowledged + 1, final['lastPosition'] + 1)), [e['position'] for e in streamed])
        self.assertEqual(len(streamed), len({e['eventId'] for e in streamed}))
        self.assertGreater(len(json.dumps(streamed)), 16384)
        fetched, after = [], acknowledged
        while True:
            _, page, _ = self.request('GET', f'/api/v1/runs/{run_id}/events?after={after}&limit=1000', actor_id='actor-contributor')
            fetched.extend(page['events'])
            after = page['nextAfter']
            if not page['hasMore']:
                break
        self.assertEqual(streamed, fetched)
        _, dossier = self.export_bytes(run_id)
        _, expected, _ = self.request('GET', f'/api/v1/runs/{run_id}/checksums')
        fresh = self.fresh_components()
        restored = fresh.restore(dossier)
        self.assertEqual(0, restored.returncode, restored.stdout)
        _, actual, _ = fresh.request('GET', f'/api/v1/runs/{run_id}/checksums')
        self.assertEqual(expected, actual)
        # Supplemental negative proof scans only disposable product storage, not external input fixtures.
        dump = harness.command_output(['docker', 'exec', self.postgres_name,
            'pg_dump', '-U', 'wpcp_test', '-d', 'wpcp_test', '--data-only'])
        self.assertEqual(0, dump.returncode)
        restored_dump = harness.command_output(['docker', 'exec', fresh.postgres_name,
            'pg_dump', '-U', 'wpcp_test', '-d', 'wpcp_test', '--data-only'])
        self.assertEqual(0, restored_dump.returncode)
        surfaces = [dump.stdout.encode(), restored_dump.stdout.encode(), raw_client.encode(), json.dumps(streamed).encode(),
            json.dumps(final).encode(), json.dumps(actual).encode(), log_path.read_bytes()]
        surfaces.extend(path.read_bytes() for path in self.artifact_root.iterdir() if path.is_file())
        surfaces.extend(path.read_bytes() for path in fresh.artifact_root.iterdir() if path.is_file())
        surfaces.extend(path.read_bytes() for path in Path(self.scratch.name).glob('*.log'))
        with zipfile.ZipFile(io.BytesIO(dossier)) as archive:
            surfaces.extend(archive.read(name) for name in archive.namelist())
        for item in json.loads(self.fixture_path.read_text())['redactionPolicy']['controlledCanaries']:
            for index, surface in enumerate(surfaces):
                self.assertNotIn(item['value'].encode(), surface, (item['name'], index))
        destination = os.environ.get('WPCP_DOSSIER_PROOF_DIR')
        if destination:
            directory = Path(destination)
            directory.mkdir(parents=True, exist_ok=True)
            (directory / 'run-dossier.zip').write_bytes(dossier)
            (directory / 'public-proof.json').write_text(json.dumps({
                'source': expected, 'restored': actual,
                'reconnect': {'acknowledged': acknowledged, 'lastPosition': final['lastPosition'],
                    'receivedCount': len(streamed), 'streamBytes': len(json.dumps(streamed)),
                    'first': streamed[0], 'last': streamed[-1], 'gaps': 0, 'duplicates': 0, 'reordered': 0},
                'redaction': {'policyVersion': json.loads(self.fixture_path.read_text())['redactionPolicy']['version'],
                    'canaryKinds': [item['name'] for item in json.loads(self.fixture_path.read_text())['redactionPolicy']['controlledCanaries']],
                    'surfacesScanned': len(surfaces), 'rawMatches': 0},
                'outcome': final['state'], 'apiKilled': True, 'workersKilled': 2,
                'freshPostgresAndArtifactRoot': True}, indent=2) + '\n')
        print(json.dumps({'ticket09': {'events': final['lastPosition'], 'reconnectedEvents': len(streamed),
            'streamBytes': len(json.dumps(streamed)), 'historySha256': expected['historySha256'],
            'projectionSha256': expected['projectionSha256'], 'artifacts': len(expected['artifacts']),
            'scannedSurfaces': len(surfaces), 'rawCanaryMatches': 0, 'freshRestore': 'equal'}}))

    def test_jsonl_artifacts_redact_decoded_fields_before_storage_and_export(self):
        run_id = self.new_run()
        worker = self.run_evidence_worker(run_id, self.evidence_provider(jsonl=True))
        self.assertEqual(0, worker.returncode, worker.stdout)
        _, manifest, _ = self.request('GET', f'/api/v1/runs/{run_id}/artifacts')
        artifact = next(a for a in manifest['artifacts'] if a['mediaType'] == 'application/x-ndjson')
        status, content = self.artifact_bytes(run_id, artifact['artifactId'])
        self.assertEqual(200, status)
        text = json.loads(content)['message']
        for item in json.loads(self.fixture_path.read_text())['redactionPolicy']['controlledCanaries']:
            self.assertNotIn(item['value'], text)
        self.assertTrue(artifact['redaction']['occurred'])
        self.assertIn('[REDACTED:', text)

    def test_missing_and_corrupt_artifacts_remain_visible_after_dossier_restore(self):
        run_id = self.new_run()
        self.assertEqual(0, self.run_evidence_worker(run_id,
            self.evidence_provider(sensitive_binary=False)).returncode)
        _, data = self.export_bytes(run_id)
        changed = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(data)) as source, zipfile.ZipFile(changed, 'w') as target:
            artifacts = [name for name in source.namelist() if name.startswith('artifacts/')]
            self.assertEqual(2, len(artifacts))
            for name in source.namelist():
                if name == artifacts[0]:
                    continue
                target.writestr(name, b'corrupted artifact' if name == artifacts[1] else source.read(name))
        fresh = self.fresh_components()
        restored = fresh.restore(changed.getvalue())
        self.assertEqual(0, restored.returncode, restored.stdout)
        _, manifest, _ = fresh.request('GET', f'/api/v1/runs/{run_id}/artifacts')
        self.assertFalse(manifest['qualificationEligible'])
        self.assertEqual({'missing', 'corrupt'}, {a['availability'] for a in manifest['artifacts']})
        for artifact in manifest['artifacts']:
            self.assertEqual(410, fresh.artifact_bytes(run_id, artifact['artifactId'])[0])
        _, exported = fresh.export_bytes(run_id)
        with zipfile.ZipFile(io.BytesIO(exported)) as archive:
            self.assertEqual({'missing', 'corrupt'},
                {a['availability'] for a in json.loads(archive.read('manifest.json'))['artifacts']})

    def test_active_operation_output_uses_the_same_safe_artifact_boundary(self):
        run_id = self.new_run()
        worker = self.run_evidence_worker(run_id, self.evidence_provider(large_bytes=100000),
            '--live-activity-key', 'dossier-proof')
        self.assertEqual(0, worker.returncode, worker.stdout)
        run = self.read_run(run_id)
        self.assertLess(len(json.dumps(run)), 20000)
        active = next(a['liveOperation'] for a in run['attempts'] if a.get('liveOperation'))
        self.assertEqual('completed', active['state'])
        self.assertIn('artifactId', active['currentOperation']['response'])
        _, artifacts, _ = self.request('GET', f'/api/v1/runs/{run_id}/artifacts')
        self.assertGreaterEqual(len(artifacts['artifacts']), 2)
        for artifact in artifacts['artifacts']:
            status, content = self.artifact_bytes(run_id, artifact['artifactId'])
            self.assertEqual(200, status)
            for item in json.loads(self.fixture_path.read_text())['redactionPolicy']['controlledCanaries']:
                self.assertNotIn(item['value'].encode(), content)
        _, data = self.export_bytes(run_id)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            self.assertIn('AgentSessionAdapter/v1', json.loads(archive.read('manifest.json'))['adapterContracts'])

    def test_binary_utf16_canaries_are_withheld_before_persistence(self):
        run_id = self.new_run()
        self.assertEqual(0, self.run_evidence_worker(run_id,
            self.evidence_provider(binary_encoding='utf-16-le')).returncode)
        _, manifest, _ = self.request('GET', f'/api/v1/runs/{run_id}/artifacts')
        withheld = [a for a in manifest['artifacts'] if a['availability'] == 'withheld']
        self.assertEqual(1, len(withheld))
        self.assertEqual('binary-controlled-canary', withheld[0]['reason'])
        self.assertEqual(410, self.artifact_bytes(run_id, withheld[0]['artifactId'])[0])

    def test_large_terminal_original_stays_retrievable_without_inflating_the_projection(self):
        run_id = self.new_run()
        worker = self.run_evidence_worker(run_id, self.evidence_provider(large_bytes=100000, terminal_result=True))
        self.assertEqual(0, worker.returncode, worker.stdout)
        run = self.read_run(run_id)
        self.assertEqual('blocked', run['state'])
        self.assertLess(len(json.dumps(run)), 20000)
        session = next(a['session'] for a in run['attempts'] if a.get('session'))
        status, content = self.artifact_bytes(run_id, session['originalResult']['artifactId'])
        self.assertEqual(200, status)
        self.assertEqual('blocked', json.loads(content)['status'])
        self.assertGreater(len(json.loads(content)['reason']), 100000)
        self.assertLess(len(session['humanRequest']['problem']), 2000)

    def test_legacy_artifact_uri_without_bytes_is_visible_and_blocks_qualification(self):
        run_id = self.new_run()
        self.assertEqual(0, self.run_fake(run_id, self.start_fake()).returncode)
        _, manifest, _ = self.request('GET', f'/api/v1/runs/{run_id}/artifacts')
        self.assertFalse(manifest['qualificationEligible'])
        self.assertEqual(1, len(manifest['artifacts']))
        missing = manifest['artifacts'][0]
        self.assertEqual('external-artifact-unavailable', missing['reason'])
        self.assertEqual(410, self.artifact_bytes(run_id, missing['artifactId'])[0])
        _, page, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        observation = next(e for e in page['events'] if e['payload'].get('type') == 'artifact')
        self.assertEqual('fake://report', observation['payload']['data']['uri'])
        self.assertEqual(missing['artifactId'], observation['payload']['data']['artifact']['artifactId'])

    start_fake = fake_tests.FakeCodexTests.start_fake
    fake_worker_args = fake_tests.FakeCodexTests.fake_worker_args
    run_fake = fake_tests.FakeCodexTests.run_fake
    paused_worker = fake_tests.FakeCodexTests.paused_worker

    def test_bounded_pages_resume_after_delivered_cursor_without_skipping_history(self):
        run_id = self.new_run()
        result = self.run_fake(run_id, self.start_fake())
        self.assertEqual(0, result.returncode, result.stdout)
        path = f'/api/v1/runs/{run_id}/events'
        status, first, _ = self.request('GET', path + '?after=0&limit=2')
        self.assertEqual(200, status)
        self.assertEqual([1, 2], [e['position'] for e in first['events']])
        self.assertEqual(2, first['nextAfter'])
        self.assertTrue(first['hasMore'])
        self.assertGreater(first['lastPosition'], first['nextAfter'])
        events, page = list(first['events']), first
        while page['hasMore']:
            _, page, _ = self.request('GET', path + f"?after={page['nextAfter']}&limit=2")
            events.extend(page['events'])
        self.assertEqual(list(range(1, page['lastPosition'] + 1)), [e['position'] for e in events])
        self.assertEqual(len(events), len({e['eventId'] for e in events}))
        for query in ('?limit=0', '?limit=1001', '?after=-1', '?after=999999'):
            status, _, _ = self.request('GET', path + query)
            self.assertEqual(400, status, query)

    def open_stream(self, run_id, after=0, actor='actor-observer'):
        connection = http.client.HTTPConnection('127.0.0.1', self.api_port, timeout=10)
        connection.request('GET', f'/api/v1/runs/{run_id}/events/stream', headers={
            'Authorization': 'Bearer ' + self.provider.tokens[actor],
            'X-Wpcp-Fixture-Access': self.fixture_access_token, 'Last-Event-ID': str(after)})
        response = connection.getresponse()
        self.addCleanup(connection.close)
        return response

    @staticmethod
    def frame(response):
        lines = []
        while True:
            line = response.readline().decode().strip()
            if not line:
                return '\n'.join(lines)
            lines.append(line)

    def test_sse_replays_acknowledged_cursor_and_ends_on_permission_revocation(self):
        run_id = self.new_run()
        self.assertEqual(0, self.run_fake(run_id, self.start_fake()).returncode)
        _, page, _ = self.request('GET', f'/api/v1/runs/{run_id}/events?after=3')
        stream = self.open_stream(run_id, 3)
        self.assertEqual(200, stream.status)
        self.assertEqual('text/event-stream', stream.getheader('Content-Type'))
        for event in page['events']:
            frame = self.frame(stream)
            self.assertIn(f"id: {event['position']}\n", frame)
            data = next(line[6:] for line in frame.splitlines() if line.startswith('data: '))
            self.assertEqual(event, json.loads(data))
        self.assertEqual(': keepalive', self.frame(stream))
        self.provider.identities['actor-observer']['read'] = False
        self.addCleanup(self.provider.identities['actor-observer'].__setitem__, 'read', True)
        for _ in range(3):
            frame = self.frame(stream)
            if 'access-revoked' in frame:
                break
        self.assertIn('event: access-revoked', frame)
        self.assertEqual(b'', stream.read())
        self.assertEqual(403, self.open_stream(run_id, 3).status)


if __name__ == '__main__':
    unittest.main()
