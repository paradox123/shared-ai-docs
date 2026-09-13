"""Real pinned Codex/TUI to controlled provider draft, through public run surfaces."""
import json
import os
from pathlib import Path
import sys
import unittest
from tests import test_control_plane_black_box as harness
from tests import test_real_codex_adapter as native
from tests.publication_fixture import PublicationFixture, git
from tests import test_publication_worker as publication


@unittest.skipUnless(os.environ.get('WPCP_CODEX_ENDPOINT_PROBE') == '1', 'explicit real Codex endpoint')
class NativePublicationTests(harness.ControlPlaneProcessHarness, unittest.TestCase):
    start_real = native.RealCodexAdapterTests.start_real
    open_and_claim = native.RealCodexAdapterTests.open_and_claim
    run_native_ui = native.RealCodexAdapterTests.run_native_ui
    publish = publication.PublicationWorkerTests.publish

    def test_real_native_issue_publishes_its_executed_evidence_as_one_draft(self):
        port = self.start_real()
        run_id = self.new_run()
        fixture = PublicationFixture(Path(self.scratch.name) / run_id, self.read_run(run_id)['correlation']['issueNumber'])
        self.addCleanup(fixture.close)
        repository = self.adapter_root / 'repository'
        fixture.repo.rename(repository)
        fixture.repo = repository
        fixture.plan['localPath'] = str(repository)
        fixture.plan['agentOrigin'] = f'http://127.0.0.1:{port}'
        (repository / 'greeting.py').write_text('def greet(): return "Wrong"\n')
        (repository / 'ISSUE.md').write_text('Fix greet() to return exactly Hello, Ada! Run a failing assertion first and a passing assertion after. Change greeting.py only.\n')
        git(repository, 'add', '.')
        git(repository, 'commit', '-qm', 'Bounded issue')
        fixture.base = git(repository, 'rev-parse', 'HEAD')
        git(repository, 'update-ref', 'refs/heads/main', fixture.base)
        git(repository, 'push', '-q', 'origin', 'main')
        fixture.plan['expectedBaseSha'] = fixture.base
        fixture.save()
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        run = self.read_run(run_id)
        self.assertEqual('awaiting-agent', run['state'], run)
        attempt = self.open_and_claim(run_id, run)
        prompt = ('Implement ISSUE.md now using mcp__wpcp__execute. Read ISSUE.md and greeting.py, '
            'execute a failing Python assertion, fix greeting.py, execute the assertion again. '
            'Return completed canonical output with actual red/green observations and evidence. '
            'Do not create __pycache__; use Python -B. Interpreter: ' + sys.executable)
        _, history = self.run_native_ui(run_id, attempt, prompt)
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        run = self.read_run(run_id)
        self.assertEqual('draft-published', run['state'], run)
        self.assertEqual(1, fixture.creates)
        self.assertEqual(0, self.publish(run_id, fixture.path).returncode)
        self.assertEqual(1, fixture.creates)
        if destination := os.environ.get('WPCP_PUBLICATION_PROOF_DIR'):
            root = Path(destination); root.mkdir(parents=True, exist_ok=True)
            (root / 'real-native-publication.json').write_text(json.dumps({
                'run': self.read_run(run_id), 'history': history, 'providerPullRequest': fixture.pulls[0],
                'providerKind': 'controlled HTTP GitHub boundary with real local bare Git',
                'runtimeKind': 'real pinned Codex with native TUI'}, indent=2))
