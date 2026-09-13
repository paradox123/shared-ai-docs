"""Evidence recovery through process commands and authenticated public read-back."""
import json
import sys
import unittest
from pathlib import Path
from tests import test_control_plane_black_box as harness
from tests.publication_fixture import PublicationFixture, git, probe
from tests import test_publication_worker as publication_tests


class EvidenceRecoveryTests(harness.ControlPlaneProcessHarness, unittest.TestCase):
    publish = publication_tests.PublicationWorkerTests.publish

    def prepared(self):
        run_id = self.new_run()
        fixture = PublicationFixture(Path(self.scratch.name) / run_id,
                                     self.read_run(run_id)['correlation']['issueNumber'])
        self.addCleanup(fixture.close)
        fixture.result_evidence = [{'criterion': 'AC1', 'verdict': 'pass', 'kind': 'idempotency',
            'observed_interface': 'greet', 'expected_result': 'Hello, Ada!',
            'observations': [{'phase': 'request', 'description': 'Called greeting',
                              'artifact': 'Hello, Ada!', 'correlation_id': None}]}]
        criterion = fixture.plan['criteria'][0]
        execute = criterion['phases'][0]['execute']
        criterion['kind'] = 'idempotency'
        criterion['phases'] = [{'name': name, 'probe': probe(), 'execute': execute}
            for name in ('request', 'response', 'repeat', 'read-back')]
        fixture.save()
        return run_id, fixture

    def events(self, run_id):
        status, page, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        self.assertEqual(200, status)
        return page['events']

    def test_valid_worker_result_reports_exact_missing_phases_separately(self):
        run_id, fixture = self.prepared()
        worker = self.publish(run_id, fixture.path)
        self.assertEqual(0, worker.returncode, worker.stdout + worker.stderr)
        run = self.read_run(run_id)
        qualification = run['publication'].get('qualification')
        self.assertIsNotNone(qualification, 'Completed schema validation hides semantic evidence gaps')
        self.assertTrue(qualification['schemaValid'])
        self.assertFalse(qualification['complete'])
        self.assertEqual([{'criterion': 'AC1', 'phase': phase}
            for phase in ('response', 'repeat', 'read-back')], qualification['missingPhases'])
        session = next(a['session'] for a in run['attempts'] if a.get('session'))
        self.assertEqual(fixture.result_evidence, session['originalResult']['evidence'])
        self.assertEqual(session['sessionId'], qualification['source']['sessionId'])
        rejected = [e for e in self.events(run_id) if e['eventType'] == 'EvidenceQualificationObserved']
        self.assertEqual(1, len(rejected))
        self.assertEqual(qualification, rejected[0]['payload']['qualification'])

    def test_missing_evidence_is_captured_in_numbered_activity_on_same_head(self):
        run_id, fixture = self.prepared()
        canary = json.loads(self.fixture_path.read_text())['redactionPolicy']['controlledCanaries'][0]['value']
        expected = 'Greeting: Hello, Ada!; authorization: ' + canary
        fixture.plan['criteria'][0]['expectedReadBack'] = expected
        fixture.plan['criteria'][0]['phases'][-1]['execute'] = {
            'argv': [sys.executable, '-c', 'from greeting import greet; print("Greeting: " + greet() + ' + repr('; authorization: ' + canary) + ')'],
            'expected': expected}
        fixture.save()
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        run = self.read_run(run_id)
        events = self.events(run_id)
        starts = [e['payload'] for e in events if e['eventType'] == 'EvidenceCaptureStarted']
        self.assertEqual(1, len(starts), 'Missing worker phases were silently captured without a numbered correction')
        capture = starts[0]['capture']
        self.assertEqual((1, 'correction', 'running'), (capture['number'], capture['kind'], capture['state']))
        head = starts[0]['captureHeadSha']
        self.assertEqual('draft-published', run['state'])
        self.assertEqual(head, git(fixture.repo, 'rev-parse', 'HEAD'))
        self.assertEqual(fixture.branch, git(fixture.repo, 'branch', '--show-current'))
        self.assertEqual('', git(fixture.repo, 'status', '--porcelain'))
        self.assertEqual('1', git(fixture.repo, 'rev-list', '--count', fixture.base + '..HEAD'))
        self.assertEqual(head, fixture.pulls[0]['head']['sha'])
        self.assertEqual(head, run['publication']['intent']['headSha'])
        self.assertEqual('succeeded', run['publication']['capture']['state'])
        self.assertEqual(1, len([e for e in events if e['eventType'] == 'EvidenceCaptureObserved']))
        self.assertNotIn(canary, json.dumps(events) + json.dumps(run) + fixture.pulls[0]['body'])
        self.assertIn('Greeting: Hello, Ada!', fixture.pulls[0]['body'])
        self.assertEqual(1, fixture.agent_starts)
        cls = type(self)
        cls.stop_process(cls.api); cls.start_api()
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        self.assertEqual(1, fixture.creates)
        self.assertEqual(run['publication']['capture'], self.read_run(run_id)['publication']['capture'])

    def test_exhausted_capture_is_terminal_on_replay_and_releases_successor(self):
        run_id, fixture = self.prepared()
        counter = fixture.root / 'captures.txt'
        phase = fixture.plan['criteria'][0]['phases'][-1]
        phase['execute'] = {'argv': [sys.executable, '-c',
            'from pathlib import Path; p=Path(' + repr(str(counter)) + '); '
            'p.write_text(p.read_text()+"capture\\n" if p.exists() else "capture\\n"); print("unavailable")'],
            'expected': 'Hello, Ada!'}
        fixture.save()
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        run = self.read_run(run_id)
        starts = [e['payload']['capture']['number'] for e in self.events(run_id)
                  if e['eventType'] == 'EvidenceCaptureStarted']
        self.assertEqual([1, 2], starts, 'Failed evidence has no bounded correction activity')
        self.assertEqual('publication-blocked', run['state'])
        self.assertEqual('evidence-failed:AC1:read-back', run['publication']['blocker'])
        self.assertEqual([{'criterion': 'AC1', 'phase': 'read-back'}],
                         run['publication']['capture']['report']['failedPhases'])
        self.assertTrue(run['publication']['report']['exhausted'])
        self.assertIn('requiredAction', run['publication']['report'])
        self.assertFalse(any(a['state'] == 'running' for a in run['activities'] + run['attempts']))
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        self.assertEqual('capture\ncapture\n', counter.read_text())
        self.assertEqual(1, fixture.agent_starts)
        self.assertEqual(0, fixture.creates)
        successor, next_fixture = self.prepared()
        self.assertEqual(0, self.publish(successor, next_fixture.path).returncode)
        self.assertEqual('draft-published', self.read_run(successor)['state'])

    def test_worker_death_during_capture_stops_its_tool_before_replacement(self):
        import os
        import signal
        import subprocess
        import time
        run_id, fixture = self.prepared()
        marker = fixture.root / 'live-capture.pid'
        fixture.plan['criteria'][0]['phases'][0]['execute'] = {
            'argv': [sys.executable, '-c', 'import os,time; from pathlib import Path; from greeting import greet\n'
                'p=Path(' + repr(str(marker)) + ')\n'
                'if not p.exists():\n p.write_text(str(os.getpid()))\n time.sleep(20)\nprint(greet())'],
            'expected': 'Hello, Ada!'}
        fixture.save()
        process = subprocess.Popen(['dotnet', str(harness.WORKER_DLL),
            '--connection-string', self.connection_string, '--fixture', str(self.fixture_path),
            '--run-id', run_id, '--worker-id', 'live-crash', '--codex-python', sys.executable,
            '--publication-plan', str(fixture.path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(self.stop_process, process)
        deadline = time.monotonic() + 30
        while not marker.exists() and time.monotonic() < deadline: time.sleep(.05)
        self.assertTrue(marker.exists(), 'No in-flight capture tool')
        def cleanup_tool():
            try: os.killpg(os.getpgid(int(marker.read_text())), signal.SIGKILL)
            except ProcessLookupError: pass
        self.addCleanup(cleanup_tool)
        process.kill(); process.wait(timeout=10)
        process.stdout.close(); process.stderr.close()
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            state = subprocess.run(['ps', '-o', 'stat=', '-p', marker.read_text()],
                                   capture_output=True, text=True).stdout.strip()
            if not state or state.startswith('Z'): break
            time.sleep(.05)
        else: self.fail('Killed worker left its capture tool alive')
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        run = self.read_run(run_id)
        self.assertEqual('draft-published', run['state'])
        self.assertEqual(2, run['publication']['capture']['number'])
        self.assertEqual(1, fixture.agent_starts)
        successor, next_fixture = self.prepared()
        self.assertEqual(0, self.publish(successor, next_fixture.path).returncode)
        self.assertEqual('draft-published', self.read_run(successor)['state'])

    def pause_capture(self, run_id, fixture, boundary="after-evidence-capture-start"):
        import os
        import select
        import signal
        import subprocess
        process = subprocess.Popen(['dotnet', str(harness.WORKER_DLL),
            '--connection-string', self.connection_string, '--fixture', str(self.fixture_path),
            '--run-id', run_id, '--worker-id', 'interrupted-capture', '--codex-python', sys.executable,
            '--publication-plan', str(fixture.path), '--pause-at', boundary],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
        self.addCleanup(self.stop_process, process)
        self.assertTrue(select.select([process.stdout], [], [], 40)[0], 'No capture dispatch boundary')
        line = process.stdout.readline()
        self.assertIn(boundary, line)
        run = self.read_run(run_id)
        if boundary == 'after-evidence-capture-start':
            self.assertEqual(1, len([a for a in run['activities']
                if a['activityType'] == 'evidence-correction' and a['state'] == 'running']))
        os.killpg(process.pid, signal.SIGKILL); process.wait(timeout=10)
        process.stdout.close(); process.stderr.close()
        return run

    def test_replacement_counts_interruption_and_finishes_same_head(self):
        run_id, fixture = self.prepared()
        before = self.pause_capture(run_id, fixture)
        head = before['publication']['captureHeadSha']
        cls = type(self)
        cls.stop_process(cls.api); cls.start_api()
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        after = self.read_run(run_id)
        self.assertEqual('draft-published', after['state'])
        self.assertEqual(head, after['publication']['intent']['headSha'])
        self.assertEqual(head, git(fixture.repo, 'rev-parse', 'HEAD'))
        captures = [e['payload']['capture'] for e in self.events(run_id)
                    if e['eventType'] == 'EvidenceCaptureObserved']
        self.assertEqual([(1, 'interrupted'), (2, 'succeeded')], [(c['number'], c['state']) for c in captures])
        self.assertEqual(1, fixture.agent_starts)
        self.assertFalse(any(a['state'] == 'running' for a in after['activities'] + after['attempts']))

    def test_failed_capture_that_mutates_source_branch_or_head_blocks_immediately(self):
        mutations = {
            'source': 'Path("greeting.py").write_text("changed")',
            'branch': 'subprocess.run(["git", "switch", "-qc", "codex/drift"], check=True)',
            'head': 'subprocess.run(["git", "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "Unexpected"], check=True)'}
        for mutation, script in mutations.items():
            with self.subTest(mutation=mutation):
                run_id, fixture = self.prepared()
                fixture.plan['criteria'][0]['phases'][0]['execute'] = {
                    'argv': [sys.executable, '-c', 'from pathlib import Path; import subprocess; ' + script + '; print("wrong")'],
                    'expected': 'Hello, Ada!'}
                fixture.save()
                self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
                run = self.read_run(run_id)
                self.assertEqual('evidence-head-drift', run['publication']['blocker'])
                self.assertEqual(1, run['publication']['capture']['number'])
                self.assertEqual('publication-blocked', run['state'])
                self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
                self.assertEqual(1, fixture.agent_starts)
                self.assertEqual(0, fixture.creates)
                self.assertEqual('', git(fixture.repo, 'ls-remote', 'origin', 'refs/heads/' + fixture.branch))

    def test_two_interrupted_rounds_cannot_restart_or_hold_repository(self):
        run_id, fixture = self.prepared()
        first = self.pause_capture(run_id, fixture)
        second = self.pause_capture(run_id, fixture)
        self.assertEqual(2, second['publication']['capture']['number'])
        self.assertEqual(first['publication']['captureHeadSha'], second['publication']['captureHeadSha'])
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        after = self.read_run(run_id)
        self.assertEqual('publication-blocked', after['state'])
        self.assertEqual('evidence-capture-interrupted', after['publication']['blocker'])
        self.assertTrue(after['publication']['report']['exhausted'])
        self.assertFalse(any(a['state'] == 'running' for a in after['activities'] + after['attempts']))
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        self.assertEqual(1, fixture.agent_starts)
        self.assertEqual(0, fixture.creates)
        successor, next_fixture = self.prepared()
        self.assertEqual(0, self.publish(successor, next_fixture.path).returncode)
        self.assertEqual('draft-published', self.read_run(successor)['state'])

    def test_second_capture_recovers_transient_surface_failure(self):
        run_id, fixture = self.prepared()
        counter = fixture.root / 'round.txt'
        fixture.plan['criteria'][0]['phases'][-1]['execute'] = {
            'argv': [sys.executable, '-c', 'from pathlib import Path; from greeting import greet; '
                'p=Path(' + repr(str(counter)) + '); ready=p.exists(); p.write_text("seen"); '
                'print(greet() if ready else "not yet available")'], 'expected': 'Hello, Ada!'}
        fixture.save()
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        after = self.read_run(run_id)
        self.assertEqual('draft-published', after['state'])
        self.assertEqual(2, after['publication']['capture']['number'])
        self.assertEqual(1, fixture.agent_starts)
        captures = [e['payload']['capture'] for e in self.events(run_id)
                    if e['eventType'] == 'EvidenceCaptureObserved']
        self.assertEqual([(1, 'failed'), (2, 'succeeded')], [(c['number'], c['state']) for c in captures])

    def test_persisted_drift_remains_terminal_after_crash_and_repository_restore(self):
        run_id, fixture = self.prepared()
        trigger = fixture.root / 'mutated-once'
        fixture.plan['criteria'][0]['phases'][0]['execute'] = {
            'argv': [sys.executable, '-c', 'from pathlib import Path; p=Path(' + repr(str(trigger)) + '); '
                'Path("greeting.py").write_text("drift") if not p.exists() else None; p.touch(); print("Hello, Ada!")'],
            'expected': 'Hello, Ada!'}
        fixture.save()
        self.pause_capture(run_id, fixture, 'after-evidence-capture-result')
        git(fixture.repo, 'restore', 'greeting.py')
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        after = self.read_run(run_id)
        self.assertEqual('publication-blocked', after['state'])
        self.assertEqual('evidence-head-drift', after['publication']['blocker'])
        self.assertEqual(1, after['publication']['capture']['number'])
        self.assertEqual(0, fixture.creates)
