"""Opt-in real GitHub acceptance; creates issues and retains open draft PRs.

Set WPCP_LIVE_GITHUB_REPOSITORY to an explicitly provisioned, empty private
repository owned by the authenticated gh user. Never point this at a work repo.
Only the intentionally incomplete agent and business surface are controlled.
"""
import json
import os
from pathlib import Path
import select
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timezone

from tests import test_control_plane_black_box as harness
from tests.publication_fixture import PublicationFixture, git, probe


def github(path, body=None):
    command = ['gh', 'api', path]
    if body is not None:
        command += ['--method', 'POST', '--input', '-']
    result = subprocess.run(command, input=None if body is None else json.dumps(body),
                            capture_output=True, text=True, timeout=60, check=True)
    return json.loads(result.stdout)


@unittest.skipUnless(os.environ.get('WPCP_LIVE_GITHUB_REPOSITORY'), 'real GitHub acceptance is opt-in')
class LiveGitHubEvidenceRecoveryTests(harness.ControlPlaneProcessHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof_directory = Path(os.environ['WPCP_PUBLICATION_PROOF_DIR']).resolve()
        cls.proof_directory.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=cls.proof_directory):
            pass
        cls.repository = github('repos/' + os.environ['WPCP_LIVE_GITHUB_REPOSITORY'])
        cls.actor = github('user')
        if not (cls.repository['private'] and cls.repository['owner']['id'] == cls.actor['id']
                and cls.repository['name'].startswith('wpcp-evidence-recovery-')):
            raise RuntimeError('Requires an owned private wpcp-evidence-recovery-* test repository')
        cls.prefix = 'repos/' + cls.repository['full_name']
        if github(cls.prefix + '/branches'):
            raise RuntimeError('Requires an empty repository; existing refs must not be overwritten')
        cls.token = subprocess.check_output(['gh', 'auth', 'token'], text=True).strip()
        cls.issues = [github(cls.prefix + '/issues', {
            'title': 'Issue 12 acceptance: ' + scenario,
            'body': 'Synthetic acceptance fixture for bounded evidence recovery. ' +
                    'Keep this issue and any draft PR as reviewable evidence. No merge requested.'})
            for scenario in ('recovery and interrupted publication', 'capture exhaustion', 'successor')]
        super().setUpClass()
        cls.next_issue = cls.issues[0]['number']
        # Seed only a verified empty, disposable repository. No workflow files.
        bootstrap = PublicationFixture(Path(cls.scratch.name) / 'bootstrap', 0)
        cls.addClassCleanup(bootstrap.close)
        cls.bind_remote(bootstrap.repo)
        git(bootstrap.repo, 'push', 'origin', 'main')
        cls.base_sha = github(cls.prefix + '/commits/main')['sha']

    @classmethod
    def bind_remote(cls, checkout):
        git(checkout, 'remote', 'set-url', 'origin', cls.repository['clone_url'])
        git(checkout, 'config', 'credential.helper', '')
        git(checkout, 'config', '--add', 'credential.helper',
            '!' + shlex.quote(shutil.which('gh')) + ' auth git-credential')

    @classmethod
    def start_api(cls, **_):
        fixture = json.loads(cls.fixture_path.read_text())
        fixture['provider']['repositories'] = [{
            'repositoryId': 'repo-1', 'fullName': cls.repository['full_name'],
            'providerRepositoryId': cls.repository['id'],
            'issues': [{'issueId': str(i['id']), 'issueNumber': i['number'], 'title': i['title']}
                       for i in cls.issues]}]
        cls.fixture_path.write_text(json.dumps(fixture))
        cls.provider.tokens['actor-authorized'] = cls.token
        environment = dict(os.environ)
        environment.pop('WPCP_GITHUB_TEST_ORIGIN', None)
        environment['WPCP_FIXTURE_ACCESS_TOKEN'] = cls.fixture_access_token
        cls.api_port = harness.free_port()
        cls.base_url = f'http://127.0.0.1:{cls.api_port}'
        cls.api = subprocess.Popen(['dotnet', str(harness.API_DLL), '--connection-string',
            cls.connection_string, '--fixture', str(cls.fixture_path), '--urls', cls.base_url],
            cwd=harness.PILOT_ROOT, env=environment, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, start_new_session=True)
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and cls.api.poll() is None:
            if cls.request('GET', '/healthz')[0] == 200:
                return
            time.sleep(.1)
        raise RuntimeError('Live-authorized API failed to start')

    def prepared(self):
        run_id = self.new_run()
        issue = self.read_run(run_id)['correlation']['issueNumber']
        fixture = PublicationFixture(Path(self.scratch.name) / run_id, issue)
        self.addCleanup(fixture.close)
        self.bind_remote(fixture.repo)
        git(fixture.repo, 'fetch', 'origin', 'main')
        git(fixture.repo, 'checkout', '-B', 'main', 'origin/main')
        git(fixture.repo, 'checkout', '-B', fixture.branch)
        fixture.base = self.base_sha
        fixture.plan.update(repository={'repositoryId': 'repo-1',
            'fullName': self.repository['full_name'], 'providerRepositoryId': self.repository['id']},
            expectedBaseSha=self.base_sha, providerOrigin='https://api.github.com',
            title=f'Issue 12 evidence recovery acceptance for issue #{issue}')
        fixture.result_evidence = [{'criterion': 'AC1', 'verdict': 'pass', 'kind': 'idempotency',
            'observed_interface': 'controlled business API', 'expected_result': 'count=1',
            'observations': [{'phase': 'request', 'description': 'Original worker request only',
                              'artifact': 'count=1', 'correlation_id': None}]}]
        canary = json.loads(self.fixture_path.read_text())['redactionPolicy']['controlledCanaries'][0]['value']
        code = 'import json,urllib.request; from greeting import greet; assert greet()=="Hello, Ada!"; '
        request = ('r=urllib.request.Request(' + repr(fixture.origin + '/business') +
                   ',json.dumps({"id":' + repr(str(issue)) + '}).encode(),'+
                   '{"Content-Type":"application/json"}); ')
        read = 'r=' + repr(fixture.origin + '/business') + '; '
        observed = 'value=json.load(urllib.request.urlopen(r)); assert value["count"]==1; '
        criterion = fixture.plan['criteria'][0]
        criterion.update(kind='idempotency', surface=fixture.origin + '/business',
            description='Repeating the same request retains exactly one record',
            expectedReadBack='count=1; authorization=' + canary)
        criterion['phases'] = [{'name': phase, 'probe': probe(), 'execute': {
            'argv': [sys.executable, '-c', code + (request if phase in ('request', 'repeat') else read)
                     + observed + 'print(' + repr(criterion['expectedReadBack'] if phase == 'read-back' else 'count=1') + ')'],
            'expected': criterion['expectedReadBack'] if phase == 'read-back' else 'count=1'}}
            for phase in ('request', 'response', 'repeat', 'read-back')]
        fixture.save()
        return run_id, fixture

    def worker_arguments(self, run_id, fixture):
        return ['dotnet', str(harness.WORKER_DLL), '--connection-string', self.connection_string,
            '--fixture', str(self.fixture_path), '--run-id', run_id, '--worker-id', 'live-github',
            '--codex-python', sys.executable, '--publication-plan', str(fixture.path)]

    def publish(self, run_id, fixture):
        worker = harness.command_output(self.worker_arguments(run_id, fixture), timeout=180,
            env={**os.environ, 'WPCP_PUBLICATION_TOKEN': self.token})
        self.assertEqual(0, worker.returncode, worker.stdout + worker.stderr)
        return self.read_run(run_id)

    def events(self, run_id):
        status, page, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        self.assertEqual(200, status)
        self.assertFalse(page.get('hasMore'), 'Acceptance history must be complete')
        return page['events']

    def pulls(self, fixture):
        return github(self.prefix + '/pulls?state=all&head=' + self.actor['login'] + ':' + fixture.branch)

    def assert_published(self, run_id, fixture):
        run = self.read_run(run_id)
        self.assertEqual('draft-published', run['state'], run.get('publication'))
        pulls = self.pulls(fixture)
        self.assertEqual(1, len(pulls))
        pull = github(self.prefix + '/pulls/' + str(pulls[0]['number']))
        head = run['publication']['captureHeadSha']
        self.assertTrue(pull['draft'])
        self.assertEqual('open', pull['state'])
        self.assertIsNone(pull['merged_at'])
        self.assertEqual(self.repository['id'], pull['head']['repo']['id'])
        self.assertEqual(fixture.branch, pull['head']['ref'])
        self.assertEqual('main', pull['base']['ref'])
        self.assertEqual(head, pull['head']['sha'])
        self.assertEqual(head, github(self.prefix + '/commits/' + fixture.branch)['sha'])
        self.assertEqual(head, git(fixture.repo, 'ls-remote', 'origin', 'refs/heads/' + fixture.branch).split()[0])
        self.assertEqual(head, git(fixture.repo, 'rev-parse', 'HEAD'))
        self.assertEqual(head, run['publication']['intent']['headSha'])
        self.assertEqual(fixture.branch, git(fixture.repo, 'branch', '--show-current'))
        self.assertEqual('1', git(fixture.repo, 'rev-list', '--count', fixture.base + '..HEAD'))
        self.assertEqual('', git(fixture.repo, 'status', '--porcelain'))
        self.assertEqual(run['publication']['intent']['body'], pull['body'])
        self.assertIn(head, pull['body'])
        self.assertIn('count=1', pull['body'])
        self.assertIn('[REDACTED:CONTROLLED-CANARY]', pull['body'])
        self.assertEqual(1, fixture.agent_starts)
        self.assertFalse(any(a['state'] == 'running' for a in run['activities'] + run['attempts']))
        events = self.events(run_id)
        qualification = run['publication']['qualification']
        self.assertTrue(qualification['schemaValid'])
        self.assertFalse(qualification['complete'])
        self.assertEqual([{'criterion': 'AC1', 'phase': phase}
            for phase in ('response', 'repeat', 'read-back')], qualification['missingPhases'])
        session = next(a['session'] for a in run['attempts'] if a.get('session'))
        self.assertEqual(fixture.result_evidence, session['originalResult']['evidence'])
        self.assertEqual(session['sessionId'], qualification['source']['sessionId'])
        for kind in ('EvidenceQualificationObserved', 'EvidenceCaptureStarted', 'EvidenceCaptureObserved'):
            self.assertEqual(1, len([e for e in events if e['eventType'] == kind]))
        self.assertEqual((1, 'correction', 'succeeded'), tuple(run['publication']['capture'][key]
            for key in ('number', 'kind', 'state')))
        self.assertEqual(0, fixture.creates, 'Controlled provider must never receive publication')
        return {'operator': run, 'events': events, 'githubPull': pull,
                'implementationStarts': fixture.agent_starts, 'gitHead': head,
                'gitBranch': fixture.branch, 'outgoingCommitCount': 1}

    def retain(self, proof):
        serialized = json.dumps(proof, indent=2)
        forbidden = [self.token, self.fixture_access_token] + [c['value'] for c in
            json.loads(self.fixture_path.read_text())['redactionPolicy']['controlledCanaries']]
        self.assertFalse(any(value in serialized for value in forbidden), 'Sensitive value in acceptance evidence')
        destination = self.proof_directory
        destination.mkdir(parents=True, exist_ok=True)
        (destination / 'live-github-recovery.json').write_text(serialized + '\n')

    def test_recovery_adoption_exhaustion_and_successor_on_real_github(self):
        proof = {'observedAt': datetime.now(timezone.utc).isoformat(),
            'githubOrigin': 'https://api.github.com', 'repository': {
                key: self.repository[key] for key in ('id', 'full_name', 'html_url', 'private')},
            'actor': {key: self.actor[key] for key in ('id', 'login')},
            'issues': [{key: i[key] for key in ('id', 'number', 'html_url', 'title')} for i in self.issues],
            'controlledSurfaces': ['intentionally incomplete worker', 'synthetic business API'],
            'realSurfaces': ['GitHub authorization', 'Git push', 'GitHub draft PR', 'Operator HTTP', 'PostgreSQL']}
        run_id, fixture = self.prepared()
        worker = subprocess.Popen(self.worker_arguments(run_id, fixture) +
            ['--pause-at', 'after-provider-effect'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, start_new_session=True, env={**os.environ, 'WPCP_PUBLICATION_TOKEN': self.token})
        self.addCleanup(self.stop_process, worker)
        self.assertTrue(select.select([worker.stdout], [], [], 180)[0], 'No publication boundary')
        line = worker.stdout.readline()
        self.assertIn('after-provider-effect', line, self.read_run(run_id).get('publication'))
        before = self.read_run(run_id)
        self.assertEqual(1, len(self.pulls(fixture)))
        os.killpg(worker.pid, signal.SIGKILL)
        worker.wait(timeout=10)
        worker.stdout.close()
        worker.stderr.close()
        type(self).stop_process(type(self).api)
        type(self).start_api()
        adopted = self.publish(run_id, fixture)
        self.assertTrue(adopted['publication']['report']['adopted'])
        proof['interruptedBeforeReceipt'] = before
        proof['recovered'] = self.assert_published(run_id, fixture)
        self.publish(run_id, fixture)
        proof['terminalSuccessReplay'] = self.assert_published(run_id, fixture)
        self.retain(proof)

        blocked_id, blocked_fixture = self.prepared()
        counter = blocked_fixture.root / 'failed-captures.txt'
        blocked_fixture.plan['criteria'][0]['phases'][-1]['execute'] = {
            'argv': [sys.executable, '-c', 'from pathlib import Path; p=Path(' + repr(str(counter)) + '); '
                'p.write_text(p.read_text()+"capture\\n" if p.exists() else "capture\\n"); print("unavailable")'],
            'expected': blocked_fixture.plan['criteria'][0]['expectedReadBack']}
        blocked_fixture.save()
        blocked = self.publish(blocked_id, blocked_fixture)
        self.assertEqual('publication-blocked', blocked['state'])
        self.assertEqual('evidence-failed:AC1:read-back', blocked['publication']['blocker'])
        self.assertTrue(blocked['publication']['report']['exhausted'])
        self.assertTrue(blocked['publication']['report']['requiredAction'])
        self.assertFalse(any(a['state'] == 'running' for a in blocked['activities'] + blocked['attempts']))
        captures = [e['payload']['capture']['number'] for e in self.events(blocked_id)
                    if e['eventType'] == 'EvidenceCaptureStarted']
        self.assertEqual([1, 2], captures)
        self.publish(blocked_id, blocked_fixture)
        self.assertEqual('capture\ncapture\n', counter.read_text())
        self.assertEqual(1, blocked_fixture.agent_starts)
        self.assertEqual([], self.pulls(blocked_fixture))
        self.assertEqual('', git(blocked_fixture.repo, 'ls-remote', 'origin', 'refs/heads/' + blocked_fixture.branch))
        proof['exhausted'] = {'operator': blocked, 'events': self.events(blocked_id),
            'captureExecutionsAfterReplay': 2, 'githubPullCount': 0, 'remoteBranchPresent': False}
        self.retain(proof)

        successor_id, successor_fixture = self.prepared()
        self.publish(successor_id, successor_fixture)
        proof['successor'] = self.assert_published(successor_id, successor_fixture)
        self.assertEqual(self.base_sha, github(self.prefix + '/commits/main')['sha'])
        proof['baseUnchanged'] = True
        proof['acceptancePassed'] = True
        self.retain(proof)
