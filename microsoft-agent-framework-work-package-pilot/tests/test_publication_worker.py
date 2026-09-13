"""Publication admission through worker commands and authenticated HTTP read-back."""
import json
import sys
import unittest
from pathlib import Path
from tests import test_control_plane_black_box as harness
from tests.publication_fixture import PublicationFixture


class PublicationWorkerTests(harness.ControlPlaneProcessHarness, unittest.TestCase):
    def publish(self, run_id, path):
        return harness.command_output(['dotnet', str(harness.WORKER_DLL),
            '--connection-string', self.connection_string, '--fixture', str(self.fixture_path),
            '--run-id', run_id, '--worker-id', 'publication', '--codex-python', sys.executable,
            '--publication-plan', str(path)])

    def test_missing_dependency_is_named_without_starting_agent(self):
        run_id = self.new_run()
        fixture = PublicationFixture(Path(self.scratch.name) / run_id, self.read_run(run_id)['correlation']['issueNumber'])
        self.addCleanup(fixture.close)
        fixture.plan['prerequisites']['dependencies'] = {'argv': ['/does-not-exist/wpcp-tool'], 'expected': 'available'}
        fixture.save()
        worker = self.publish(run_id, fixture.path)
        self.assertEqual(0, worker.returncode, worker.stdout)
        run = self.read_run(run_id)
        self.assertEqual('prerequisite-failed:dependencies', run['publication']['blocker'])
        self.assertFalse(any(a.get('session') for a in run['attempts']))

    def test_incomplete_plan_blocks_before_any_agent_start(self):
        run_id = self.new_run()
        plan = Path(self.scratch.name) / (run_id + '.json')
        plan.write_text(json.dumps({'schemaVersion': 'wpcp-publication-plan/v1'}))
        worker = harness.command_output(['dotnet', str(harness.WORKER_DLL),
            '--connection-string', self.connection_string, '--fixture', str(self.fixture_path),
            '--run-id', run_id, '--worker-id', 'publication', '--codex-python', sys.executable,
            '--publication-plan', str(plan)])
        self.assertEqual(0, worker.returncode, worker.stdout + worker.stderr)
        run = self.read_run(run_id)
        self.assertEqual('preflight-blocked', run['state'], run)
        self.assertEqual('invalid-evidence-plan', run['publication']['blocker'])
        self.assertFalse(any(a.get('session') for a in run['attempts']))

    def test_completed_assignment_publishes_one_readable_draft_at_committed_head(self):
        run_id = self.new_run()
        fixture = PublicationFixture(Path(self.scratch.name) / run_id, self.read_run(run_id)['correlation']['issueNumber'])
        self.addCleanup(fixture.close)
        worker = self.publish(run_id, fixture.path)
        self.assertEqual(0, worker.returncode, worker.stdout + worker.stderr)
        run = self.read_run(run_id)
        self.assertEqual('draft-published', run['state'], run)
        self.assertEqual(1, fixture.creates)
        pull = fixture.pulls[0]
        self.assertTrue(pull['draft'])
        self.assertIn('Hello, Ada!', pull['body'])
        self.assertIn(pull['head']['sha'], pull['body'])
        self.assertEqual(pull['head']['sha'], run['publication']['intent']['headSha'])
        self.assertEqual(1, fixture.agent_starts)

    def test_large_completed_result_is_read_from_verified_artifact(self):
        import os
        from unittest.mock import patch
        run_id = self.new_run()
        fixture = PublicationFixture(Path(self.scratch.name) / run_id, self.read_run(run_id)['correlation']['issueNumber'])
        self.addCleanup(fixture.close)
        fixture.result_summary = 'Implemented greeting. ' * 1200
        with patch.dict(os.environ, {'WPCP_ARTIFACT_ROOT': str(fixture.root / 'artifacts')}):
            worker = self.publish(run_id, fixture.path)
        self.assertEqual(0, worker.returncode, worker.stdout + worker.stderr)
        run = self.read_run(run_id)
        session = next(a['session'] for a in run['attempts'] if a.get('session'))
        self.assertIn('artifactId', session['originalResult'])
        self.assertEqual('draft-published', run['state'], run['publication'])
        self.assertEqual(1, fixture.creates)

    def test_adapter_must_prove_it_uses_the_planned_checkout_before_start(self):
        run_id = self.new_run()
        fixture = PublicationFixture(Path(self.scratch.name) / run_id, self.read_run(run_id)['correlation']['issueNumber'])
        self.addCleanup(fixture.close)
        fixture.adapter_path = '/wrong/checkout'
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        self.assertEqual('agent-readiness-mismatch', self.read_run(run_id)['publication']['blocker'])
        self.assertEqual(0, fixture.agent_starts)

    def test_lost_create_reply_is_adopted_after_api_replacement(self):
        run_id = self.new_run()
        fixture = PublicationFixture(Path(self.scratch.name) / run_id, self.read_run(run_id)['correlation']['issueNumber'])
        self.addCleanup(fixture.close)
        fixture.lose_reply = True
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        self.assertEqual('publication-blocked', self.read_run(run_id)['state'])
        self.assertEqual(1, fixture.creates)
        cls = type(self)
        cls.stop_process(cls.api); cls.start_api()
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        run = self.read_run(run_id)
        self.assertEqual('draft-published', run['state'], run)
        self.assertTrue(run['publication']['report']['adopted'])
        self.assertEqual(1, fixture.creates)
        self.assertEqual(1, fixture.agent_starts)
        # The provider is authoritative on every replay, even after success.
        fixture.pulls[0]['draft'] = False
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        self.assertEqual('provider-receipt-conflict', self.read_run(run_id)['publication']['blocker'])
        self.assertEqual(1, fixture.creates)
        fixture.pulls[0]['draft'] = True
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)

    def test_missing_phases_and_log_surrogates_fail_before_agent_start(self):
        for kind in ('rest', 'ui', 'idempotency', 'document', 'log', 'dashboard'):
            with self.subTest(kind=kind):
                run_id = self.new_run()
                fixture = PublicationFixture(Path(self.scratch.name) / run_id, self.read_run(run_id)['correlation']['issueNumber'])
                self.addCleanup(fixture.close)
                fixture.plan['criteria'][0]['kind'] = kind
                fixture.save()
                self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
                self.assertEqual('invalid-evidence-plan', self.read_run(run_id)['publication']['blocker'])
                self.assertEqual(0, fixture.agent_starts)
                self.assertEqual(0, fixture.creates)

    def test_failed_business_assertion_blocks_without_push(self):
        run_id = self.new_run()
        fixture = PublicationFixture(Path(self.scratch.name) / run_id, self.read_run(run_id)['correlation']['issueNumber'])
        self.addCleanup(fixture.close)
        criterion = fixture.plan['criteria'][0]
        criterion['expectedReadBack'] = 'Expected different result'
        criterion['phases'][0]['execute']['expected'] = criterion['expectedReadBack']
        fixture.save()
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        self.assertEqual('evidence-failed:AC1:read-back', self.read_run(run_id)['publication']['blocker'])
        self.assertEqual(0, fixture.creates)
        from tests.publication_fixture import git
        self.assertEqual('', git(fixture.repo, 'ls-remote', 'origin', 'refs/heads/' + fixture.branch))

    def test_surface_and_sandbox_failures_remain_concrete(self):
        for missing in ('surface', 'sandbox', 'contract'):
            with self.subTest(missing=missing):
                run_id = self.new_run()
                fixture = PublicationFixture(Path(self.scratch.name) / run_id, self.read_run(run_id)['correlation']['issueNumber'])
                self.addCleanup(fixture.close)
                if missing == 'surface':
                    fixture.plan['criteria'][0]['phases'][0]['probe']['expected'] = 'unavailable'
                    expected = 'surface-unavailable:AC1:read-back'
                else:
                    fixture.plan['prerequisites'][missing]['expected'] = 'unavailable'
                    expected = 'prerequisite-failed:' + missing
                fixture.save()
                self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
                self.assertEqual(expected, self.read_run(run_id)['publication']['blocker'])
                self.assertEqual(0, fixture.agent_starts)

    def test_redacted_observations_survive_provider_and_operator_readback(self):
        from tests.publication_fixture import probe
        run_id = self.new_run()
        fixture = PublicationFixture(Path(self.scratch.name) / run_id, self.read_run(run_id)['correlation']['issueNumber'])
        self.addCleanup(fixture.close)
        canary = json.loads(self.fixture_path.read_text())['redactionPolicy']['controlledCanaries'][0]['value']
        expected = 'Customer count: 1; authorization: ' + canary
        criterion = fixture.plan['criteria'][0]
        criterion['expectedReadBack'] = expected
        criterion['phases'][0]['execute'] = probe(expected)
        fixture.save()
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        run = self.read_run(run_id)
        self.assertEqual('draft-published', run['state'], run)
        self.assertNotIn(canary, json.dumps(run))
        self.assertNotIn(canary, fixture.pulls[0]['body'])
        self.assertIn('Customer count: 1', fixture.pulls[0]['body'])

    def test_plan_is_immutable_and_standalone_cannot_bypass_readiness(self):
        run_id = self.new_run()
        fixture = PublicationFixture(Path(self.scratch.name) / run_id, self.read_run(run_id)['correlation']['issueNumber'])
        self.addCleanup(fixture.close)
        fixture.plan['prerequisites']['sandbox']['expected'] = 'denied'
        fixture.save()
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        command = ['dotnet', str(harness.WORKER_DLL), '--connection-string', self.connection_string,
            '--fixture', str(self.fixture_path), '--run-id', run_id, '--worker-id', 'bypass',
            '--codex-python', sys.executable, '--real-agent-origin', fixture.origin]
        attempted = harness.command_output(command)
        self.assertEqual(2, attempted.returncode, attempted.stdout)
        self.assertEqual(0, fixture.agent_starts)
        fixture.plan['title'] = 'Changed immutable assignment'
        fixture.save()
        self.assertEqual(2, self.publish(run_id, fixture.path).returncode)

    def test_rest_repeat_ui_and_document_phases_execute_on_real_surfaces(self):
        import os
        from tests.publication_fixture import probe
        run_id = self.new_run()
        fixture = PublicationFixture(Path(self.scratch.name) / run_id, self.read_run(run_id)['correlation']['issueNumber'])
        self.addCleanup(fixture.close)
        runtime = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/node'
        node = os.environ.get('WPCP_TEST_NODE', str(runtime / 'bin/node'))
        playwright = os.environ.get('WPCP_TEST_PLAYWRIGHT', str(runtime / 'node_modules/playwright'))
        def command(script, expected): return {'argv': [sys.executable, '-B', '-c', script], 'expected': expected}
        def phase(name, execute): return {'name': name, 'probe': probe(), 'execute': execute}
        def criterion(identity, kind, phases, expected):
            return {'id': identity, 'description': 'One readable record', 'kind': kind,
                'surface': fixture.origin + '/business', 'expectedReadBack': expected, 'phases': phases}
        get = command('import urllib.request; print(urllib.request.urlopen(' + repr(fixture.origin + '/business') + ').read().decode())', '{"count": 1}')
        post = command('import urllib.request; print(urllib.request.urlopen(urllib.request.Request(' +
            repr(fixture.origin + '/business') + ',data=b\'{"id":"one"}\',method="POST")).read().decode())', '{"count": 1}')
        screenshot = fixture.root / 'evidence.png'
        browser = {'argv': [node, str(harness.PILOT_ROOT / 'tests/publication_browser.cjs'), playwright,
            fixture.origin + '/app', str(screenshot), 'interact'], 'expected': 'Records: 1'}
        image = phase('screenshot', command('from pathlib import Path; assert Path(' + repr(str(screenshot)) + ').read_bytes().startswith(b"\\x89PNG"); print("Rendered record count: 1")', 'Rendered record count: 1'))
        import hashlib
        image.update(imagePath=str(screenshot), imageUrl=fixture.origin + '/image',
                     probeImageUrl=fixture.origin + '/image-ready', probeImageSha256=hashlib.sha256(fixture.probe_image).hexdigest())
        document = fixture.root / 'document.html'
        generate = command('from pathlib import Path; Path(' + repr(str(document)) + ').write_text("<title>Report</title><h1>Records: 1</h1>"); print("Report generated")', 'Report generated')
        render = {'argv': [node, str(harness.PILOT_ROOT / 'tests/publication_browser.cjs'), playwright,
            fixture.origin + '/document', str(fixture.root / 'document.png'), 'render'], 'expected': 'Records: 1'}
        inspect = command('from pathlib import Path; assert "<h1>Records: 1</h1>" in Path(' + repr(str(document)) + ').read_text(); print("Records: 1")', 'Records: 1')
        doc_read = command('import urllib.request; assert "<h1>Records: 1</h1>" in urllib.request.urlopen(' + repr(fixture.origin + '/document') + ').read().decode(); print("Records: 1")', 'Records: 1')
        fixture.plan['criteria'] = [
            criterion('REST', 'rest', [phase('request', post), phase('response', get), phase('read-back', get)], '{"count": 1}'),
            criterion('REPEAT', 'idempotency', [phase('request', post), phase('response', get), phase('repeat', post), phase('read-back', get)], '{"count": 1}'),
            criterion('UI', 'ui', [phase('interaction', browser), image, phase('read-back', get)], '{"count": 1}'),
            criterion('DOC', 'document', [phase('generate', generate), phase('render', render), phase('inspect', inspect), phase('read-back', doc_read)], 'Records: 1')]
        fixture.save()
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        run = self.read_run(run_id)
        self.assertEqual('draft-published', run['state'], run['publication'])
        self.assertEqual(1, len(fixture.records))
        self.assertIn('![Decisive screenshot]', fixture.pulls[0]['body'])
        qualification = run['publication']['qualification']
        self.assertTrue(qualification['schemaValid'])
        self.assertEqual([{'criterion': identity, 'phase': phase} for identity, phases in (
            ('REST', ('request', 'response', 'read-back')),
            ('REPEAT', ('request', 'response', 'repeat', 'read-back')),
            ('UI', ('interaction', 'screenshot', 'read-back')),
            ('DOC', ('generate', 'render', 'inspect', 'read-back')))
            for phase in phases], qualification['missingPhases'])
        self.assertEqual('correction', run['publication']['capture']['kind'])
        self.assertEqual(1, run['publication']['capture']['number'])
        self.assertEqual(run['publication']['captureHeadSha'], run['publication']['intent']['headSha'])
        self.assertFalse(any(a['state'] == 'running' for a in run['activities'] + run['attempts']))
        if destination := os.environ.get('WPCP_PUBLICATION_PROOF_DIR'):
            import shutil
            import urllib.request
            root = Path(destination); root.mkdir(parents=True, exist_ok=True)
            status, events, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
            self.assertEqual(200, status)
            with urllib.request.urlopen(fixture.origin + '/repos/pilot/fixture/pulls/1') as response:
                provider_pull = json.load(response)
            (root / 'direct-surfaces.json').write_text(json.dumps({'run': run, 'events': events,
                'providerPullRequest': provider_pull}, indent=2))
            shutil.copyfile(screenshot, root / 'direct-ui.png')
            shutil.copyfile(fixture.root / 'document.png', root / 'document.png')


    def test_second_run_waits_for_unsettled_publication_in_same_repository(self):
        first = self.new_run()
        fixture = PublicationFixture(Path(self.scratch.name) / first, self.read_run(first)['correlation']['issueNumber'])
        self.addCleanup(fixture.close)
        fixture.lose_reply = True
        self.assertEqual(0, self.publish(first, fixture.path).returncode)
        second = self.new_run()
        successor = PublicationFixture(Path(self.scratch.name) / second, self.read_run(second)['correlation']['issueNumber'])
        self.addCleanup(successor.close)
        self.assertEqual(0, self.publish(second, successor.path).returncode)
        run = self.read_run(second)
        self.assertEqual('repository-publication-busy', run['publication']['blocker'], run['publication'])
        self.assertEqual(0, successor.agent_starts)
        self.assertEqual(0, self.publish(first, fixture.path).returncode)
        self.assertEqual(0, self.publish(second, successor.path).returncode)
        self.assertEqual('draft-published', self.read_run(second)['state'])

    def test_unknown_create_receipt_never_authorizes_a_second_create(self):
        run_id = self.new_run()
        fixture = PublicationFixture(Path(self.scratch.name) / run_id, self.read_run(run_id)['correlation']['issueNumber'])
        self.addCleanup(fixture.close)
        fixture.lose_reply = True
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        existing = fixture.pulls[:]
        fixture.pulls.clear()
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        self.assertEqual('publication-create-uncertain', self.read_run(run_id)['publication']['blocker'])
        self.assertEqual(1, fixture.creates)
        fixture.pulls.extend(existing)
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)

    def test_sensitive_source_and_evidence_head_drift_prevent_push(self):
        from tests.publication_fixture import git
        for failure in ('source', 'drift'):
            with self.subTest(failure=failure):
                run_id = self.new_run()
                fixture = PublicationFixture(Path(self.scratch.name) / run_id, self.read_run(run_id)['correlation']['issueNumber'])
                self.addCleanup(fixture.close)
                if failure == 'source':
                    fixture.agent_content += '# token=ghp_' + 's' * 30 + '\n'
                    expected = 'sensitive-outgoing-source'
                else:
                    fixture.plan['criteria'][0]['phases'][0]['execute']['argv'] = [sys.executable, '-c',
                        'from pathlib import Path; Path("unexpected.txt").write_text("drift"); print("Hello, Ada!")']
                    fixture.save()
                    expected = 'evidence-head-drift'
                self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
                self.assertEqual(expected, self.read_run(run_id)['publication']['blocker'])
                self.assertEqual(0, fixture.creates)
                self.assertEqual('', git(fixture.repo, 'ls-remote', 'origin', 'refs/heads/' + fixture.branch))

    def test_stale_base_rejects_before_agent_start(self):
        run_id = self.new_run()
        fixture = PublicationFixture(Path(self.scratch.name) / run_id, self.read_run(run_id)['correlation']['issueNumber'])
        self.addCleanup(fixture.close)
        fixture.plan['expectedBaseSha'] = '0' * 40
        fixture.save()
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        self.assertEqual('repository-base-mismatch', self.read_run(run_id)['publication']['blocker'])
        self.assertEqual(0, fixture.agent_starts)

    def test_worker_killed_after_provider_success_adopts_the_same_draft(self):
        import subprocess
        import signal
        run_id = self.new_run()
        fixture = PublicationFixture(Path(self.scratch.name) / run_id, self.read_run(run_id)['correlation']['issueNumber'])
        self.addCleanup(fixture.close)
        process = subprocess.Popen(['dotnet', str(harness.WORKER_DLL),
            '--connection-string', self.connection_string, '--fixture', str(self.fixture_path),
            '--run-id', run_id, '--worker-id', 'crash-publication', '--codex-python', sys.executable,
            '--publication-plan', str(fixture.path), '--pause-at', 'after-provider-effect'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
        self.addCleanup(self.stop_process, process)
        import select
        self.assertTrue(select.select([process.stdout], [], [], 30)[0], 'No publication boundary')
        line = process.stdout.readline()
        self.assertIn('after-provider-effect', line)
        self.assertEqual(1, fixture.creates)
        import os
        os.killpg(process.pid, signal.SIGKILL); process.wait(timeout=10)
        process.stdout.close(); process.stderr.close()
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        self.assertEqual('draft-published', self.read_run(run_id)['state'])
        self.assertEqual(1, fixture.creates)
        self.assertEqual(1, fixture.agent_starts)

    def test_registered_publication_rejects_other_managed_execution_modes(self):
        run_id = self.new_run()
        fixture = PublicationFixture(Path(self.scratch.name) / run_id, self.read_run(run_id)['correlation']['issueNumber'])
        self.addCleanup(fixture.close)
        fixture.plan['prerequisites']['sandbox']['expected'] = 'denied'
        fixture.save()
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        repository_plan = fixture.root / 'repository-plan.json'
        repository_plan.write_text(json.dumps({key: fixture.plan[key] for key in
            ('repository', 'localPath', 'remoteName', 'baseBranch', 'providerOrigin', 'agentOrigin', 'expectedBaseSha')}))
        for mode in (['--fake-agent-origin', fixture.origin, '--live-activity-key', 'bypass'],
                     ['--repository-plan', str(repository_plan)]):
            with self.subTest(mode=mode[0]):
                worker = harness.command_output(['dotnet', str(harness.WORKER_DLL),
                    '--connection-string', self.connection_string, '--fixture', str(self.fixture_path),
                    '--run-id', run_id, '--worker-id', 'bypass', *mode])
                self.assertEqual(2, worker.returncode, worker.stdout)
        self.assertFalse(any(a.get('session') or a.get('liveOperation') for a in self.read_run(run_id)['attempts']))


class StandalonePublicationTests(harness.ControlPlaneProcessHarness, unittest.TestCase):
    publish = PublicationWorkerTests.publish

    def test_existing_standalone_session_cannot_gain_later_readiness_provenance(self):
        run_id = self.new_run()
        fixture = PublicationFixture(Path(self.scratch.name) / run_id, self.read_run(run_id)['correlation']['issueNumber'])
        self.addCleanup(fixture.close)
        worker = harness.command_output(['dotnet', str(harness.WORKER_DLL),
            '--connection-string', self.connection_string, '--fixture', str(self.fixture_path),
            '--run-id', run_id, '--worker-id', 'standalone', '--codex-python', sys.executable,
            '--real-agent-origin', fixture.origin])
        self.assertEqual(0, worker.returncode)
        # A prepared future plan must not grant provenance to work already started.
        from tests.publication_fixture import git
        git(fixture.repo, 'add', '.')
        git(fixture.repo, 'commit', '-qm', 'Prior work')
        result = self.publish(run_id, fixture.path)
        self.assertEqual(2, result.returncode, result.stdout)
        self.assertEqual(0, fixture.creates)
