"""Opt-in real GitHub/Codex acceptance of the shared run entry and observation."""
import json
import os
from pathlib import Path
import unittest
from tests.test_submission_execution_live import LiveSubmissionExecutionHarness
from tests.test_shared_run_browser import observe_shared_run


class LiveSharedRunTests(LiveSubmissionExecutionHarness, unittest.TestCase):
    def test_real_analysis_open_observe_and_reopen_on_desktop_and_mobile(self):
        self.start_adapter()
        evidence = Path(os.environ.get('WPCP_SUBMISSION_PROOF_DIR', self.scratch.name))
        proof = observe_shared_run(self, {'baseUrl': self.base_url,
            'credential': self.provider.tokens['live-human'], 'sourceUrl': self.live_issue['html_url'],
            'live': True, 'evidence': str(evidence)},
            self.detached_worker, lambda: None, self.stop_detached_worker)
        proof['sourceUrl'] = self.live_issue['html_url']
        proof['providerWrites'] = False
        proof['topology'] = 'Independent local API, worker and browser processes; physical multi-machine proof remains Ticket 16.'
        for name, path in [('submission', '/api/v1/submissions/' + proof['start']['submissionId']),
                ('execution', '/api/v1/submissions/' + proof['start']['submissionId'] + '/execution'),
                ('run', '/api/v1/runs/' + proof['start']['runId']),
                ('history', '/api/v1/runs/' + proof['start']['runId'] + '/events?limit=1000'),
                ('artifacts', '/api/v1/runs/' + proof['start']['runId'] + '/artifacts')]:
            status, body, _ = self.request('GET', path, actor_id='live-human', include_fixture_access=False)
            self.assertEqual(200, status)
            proof[name] = body
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / 'live-shared-run.json').write_text(json.dumps(proof, indent=2) + '\n')
