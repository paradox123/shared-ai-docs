"""Submission intake through public HTTP; GitHub is the external test boundary."""
import unittest
import json
import os
import subprocess
import time
from pathlib import Path
from tests.test_control_plane_black_box import ControlPlaneProcessHarness, API_DLL, PILOT_ROOT, free_port


class SubmissionProcessHarness(ControlPlaneProcessHarness):
    @classmethod
    def start_api(cls, *, excluded_ports=None):
        configuration = getattr(cls, 'deployment_configuration', None) or json.loads(cls.fixture_path.read_text())
        configuration.pop('fixtureVersion', None)
        for repository in configuration['provider']['repositories']:
            repository.pop('issues', None)
        config_path = Path(cls.scratch.name) / 'submission-config.json'
        config_path.write_text(json.dumps(configuration))
        environment = {**os.environ, 'WPCP_CONNECTION_STRING': cls.connection_string,
            'WPCP_GITHUB_TEST_ORIGIN': cls.provider.origin}
        environment.update(getattr(cls, 'service_environment', {}))
        environment.pop('WPCP_FIXTURE_ACCESS_TOKEN', None)
        if getattr(cls, 'live_github', False):
            environment.pop('WPCP_GITHUB_TEST_ORIGIN', None)
        for _ in range(5):
            port = free_port(excluded=excluded_ports)
            process = subprocess.Popen(['dotnet', str(API_DLL), '--submission-config', str(config_path),
                '--urls', f'http://127.0.0.1:{port}'], cwd=PILOT_ROOT, env=environment,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            deadline = time.monotonic() + 15
            while process.poll() is None and time.monotonic() < deadline:
                if cls.request('GET', '/healthz', port=port)[0] == 200:
                    cls.api, cls.api_port, cls.base_url = process, port, f'http://127.0.0.1:{port}'
                    return
                time.sleep(.1)
            cls.stop_process(process)
        raise RuntimeError('Submission API did not become ready')


class SubmissionTests(SubmissionProcessHarness, unittest.TestCase):
    def test_admitted_provider_snapshot_survives_restart_without_a_run(self):
        self.provider.issues['301'] = {
            'id': 7301, 'number': 301, 'title': 'Provider title: import contacts',
            'body': 'Keep the first version. wpcp-controlled-secret-canary-v1',
            'html_url': 'https://github.com/pilot/fixture/issues/301',
            'updated_at': '2026-09-14T08:00:00Z', 'state': 'open',
            'labels': [{'name': 'ready-for-agent'}],
        }
        status, submission, raw = self.request('POST', '/api/v1/submissions',
            {'sourceUrl': 'https://github.com/pilot/fixture/issues/301'},
            include_fixture_access=False)
        self.assertEqual(201, status, raw)
        self.assertEqual('admitted', submission['state'])
        self.assertIsNone(submission['runId'])
        self.assertEqual('Provider title: import contacts', submission['title'])
        self.assertEqual('Keep the first version. [REDACTED:CONTROLLED-CANARY]', submission['body'])
        self.assertEqual(7301, submission['source']['providerIssueId'])
        self.assertEqual('2026-09-14T08:00:00+00:00', submission['source']['updatedAt'])
        self.assertEqual({'repositoryId': 'repo-1', 'fullName': 'pilot/fixture',
            'providerRepositoryId': 9001}, submission['repository'])
        self.assertTrue(submission['redaction']['occurred'])
        self.provider.issues['301']['body'] = 'Later source edit'
        self.stop_process(self.api)
        self.start_api()
        status, read, raw = self.request('GET', '/api/v1/submissions/' + submission['submissionId'],
            actor_id='actor-observer', include_fixture_access=False)
        self.assertEqual(200, status, raw)
        self.assertEqual(submission, read)
        status, overview, raw = self.request('GET', '/api/v1/submissions',
            actor_id='actor-observer', include_fixture_access=False)
        self.assertEqual(200, status, raw)
        self.assertIn(submission, overview['submissions'])

    def test_duplicate_delivery_and_concurrent_clients_keep_one_original_snapshot(self):
        from concurrent.futures import ThreadPoolExecutor
        self.provider.issues['302'] = {
            'id': 7302, 'number': 302, 'title': 'Original concurrent issue', 'body': 'Original body',
            'html_url': 'https://github.com/pilot/fixture/issues/302',
            'updated_at': '2026-09-14T08:00:00Z', 'state': 'open',
            'labels': [{'name': 'ready-for-agent'}],
        }
        def submit(_):
            return self.request('POST', '/api/v1/submissions',
                {'sourceUrl': 'https://github.com/Pilot/Fixture/issues/302#issuecomment-1'},
                include_fixture_access=False)
        with ThreadPoolExecutor(max_workers=6) as executor:
            results = list(executor.map(submit, range(12)))
        self.assertEqual(1, sum(status == 201 for status, _, _ in results), results)
        self.assertEqual({200, 201}, {status for status, _, _ in results})
        self.assertEqual(1, len({payload['submissionId'] for _, payload, _ in results}))
        self.provider.issues['302']['title'] = 'Changed title'
        self.provider.issues['302']['body'] = 'Changed body'
        self.provider.issues['302']['updated_at'] = '2026-09-15T08:00:00Z'
        status, replay, raw = submit(None)
        self.assertEqual(200, status, raw)
        self.assertEqual(results[0][1], replay)

    def test_access_and_invalid_source_fail_without_disclosing_or_saving_content(self):
        issue = {'id': 7303, 'number': 303, 'title': 'Authorized issue', 'body': 'Authorized body',
            'html_url': 'https://github.com/pilot/fixture/issues/303',
            'updated_at': '2026-09-14T08:00:00Z', 'state': 'open',
            'labels': [{'name': 'ready-for-agent'}]}
        self.provider.issues['303'] = issue
        def submit(actor='actor-authorized', url='https://github.com/pilot/fixture/issues/303'):
            return self.request('POST', '/api/v1/submissions', {'sourceUrl': url},
                actor_id=actor, include_fixture_access=False)
        for actor, code, expected in [
            ('actor-observer', 'repository-contribution-required', 403),
            ('actor-unauthorized', 'repository-access-denied', 403),
            ('worker-bot', 'human-identity-required', 403),
            ('invalid', 'provider-authentication-required', 401),
        ]:
            with self.subTest(actor=actor):
                status, error, _ = submit(actor)
                self.assertEqual((expected, code), (status, error.get('code')))
        for mutation, code, expected in [
            ({'labels': []}, 'implementation-authorization-required', 422),
            ({'state': 'closed'}, 'github-issue-closed', 422),
            ({'pull_request': {}}, 'github-source-is-pull-request', 422),
            ({'html_url': 'https://github.com/elsewhere/repo/issues/303'}, 'github-source-identity-mismatch', 409),
        ]:
            with self.subTest(code=code):
                self.provider.issues['303'] = {**issue, **mutation}
                status, error, _ = submit()
                self.assertEqual((expected, code), (status, error.get('code')))
        self.provider.issues['303'] = issue
        for url, code, expected in [
            ('http://127.0.0.1/issues/303', 'invalid-github-issue-url', 400),
            ('https://github.com/pilot/fixture/pull/303', 'invalid-github-issue-url', 400),
            ('https://github.com/pilot/other/issues/303', 'repository-not-configured', 403),
            ('https://github.com/pilot/fixture/issues/999', 'github-issue-not-found', 404),
        ]:
            with self.subTest(url=url):
                status, error, _ = submit(url=url)
                self.assertEqual((expected, code), (status, error.get('code')))
        self.provider.repository_id = 9010
        try:
            status, error, _ = submit()
            self.assertEqual((403, 'repository-identity-mismatch'), (status, error.get('code')))
        finally:
            self.provider.repository_id = 9001
        _, overview, _ = self.request('GET', '/api/v1/submissions')
        self.assertNotIn(7303, [s['source']['providerIssueId'] for s in overview['submissions']])
        status, admitted, raw = submit()
        self.assertEqual(201, status, raw)
        path = '/api/v1/submissions/' + admitted['submissionId']
        self.provider.identities['actor-authorized']['read'] = False
        try:
            status, _, raw = self.request('GET', path)
            self.assertEqual(403, status)
            self.assertNotIn('Authorized body', raw)
            _, overview, _ = self.request('GET', '/api/v1/submissions')
            self.assertEqual([], overview['submissions'])
            status, _, _ = submit()
            self.assertEqual(403, status)
        finally:
            self.provider.identities['actor-authorized']['read'] = True
        self.provider.failure = 503
        try:
            self.assertEqual(503, submit()[0])
            self.assertEqual(503, self.request('GET', path)[0])
        finally:
            self.provider.failure = None

    def test_operator_gui_is_served_without_fixture_capability(self):
        status, _, raw = self.request('GET', '/operator/', include_fixture_access=False)
        self.assertEqual(200, status)
        self.assertIn('<title>Anforderungen', raw)
        self.assertIn('GitHub-Issue-URL', raw)
        self.assertIn('type="module"', raw)
