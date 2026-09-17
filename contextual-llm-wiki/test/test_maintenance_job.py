"""Tests at the scheduled helper's process boundary; CLI peers are test doubles."""
import json
import fcntl
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/maintain-index.py'


class MaintenanceJob(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        peer = self.root / 'peer'
        peer.write_text('''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
kind = Path(sys.argv[0]).name
step = kind + (':' + sys.argv[1] if kind != 'reconcile' else '')
with open(os.environ['CALLS'], 'a') as f: f.write(step + '\\n')
if step == os.environ.get('FAIL'):
    print('forced failure', file=sys.stderr)
    sys.exit(7)
if kind == 'reconcile': result = {'status':'ok'}
elif kind == 'wiki':
    result = {'ok':True}
    if sys.argv[1] == 'maintain': result.update(noop=True, pages=[], qmdSafe=True, completed=[], unchanged=[], pending=[], failures=[])
    if sys.argv[1] == 'status': result.update(pending=[], review=[], changes={'added':[], 'changed':[], 'removed':[]}, pages=[], sourceCount=0, lastCompleted='2026-09-13T00:00:00Z')
    if sys.argv[1] == 'lint': result.update(pending=[], review=[], activeIssues=[], unresolvedCompilerErrors=[], forbiddenStores=[])
else: result = {'qmd':sys.argv[1]}
if step == os.environ.get('MALFORMED'):
    print('not json')
    sys.exit(0)
if step == os.environ.get('INVALID'):
    result = json.loads(os.environ['RESPONSE'])
if step == 'wiki:maintain' and os.environ.get('PARTIAL'):
    result = {'ok':False, 'qmdSafe':True, 'pages':[], 'changes':{'added':[], 'changed':['alpha.md'], 'removed':[]},
              'completed':['concepts/control'], 'unchanged':[], 'failures':[{'error':'broken branch'}],
              'pending':[{'phase':'compile', 'sources':['alpha.md'], 'pages':['concepts/affected']}], 'error':'broken branch'}
if kind == 'wiki' and sys.argv[1] in ['status', 'lint'] and os.environ.get('PARTIAL'):
    result.update(pending=[{'phase':'compile', 'sources':['alpha.md'], 'pages':['concepts/affected']}],
                  review=[{'id':'concepts/affected'}])
    if sys.argv[1] == 'status':
        result.update(changes={'added':[], 'changed':['alpha.md'], 'removed':[]},
                      pages=[{'id':'concepts/affected', 'withdrawn':True}])
    else: result['ok'] = False
if step == 'wiki:maintain' and isinstance(result, dict):
    artifact = Path(os.environ['CALLS']).parent / 'wiki-report.json'
    result['report'] = str(artifact)
    if os.environ.get('DROP_FIELD'): result.pop(os.environ['DROP_FIELD'], None)
    artifact.write_text(json.dumps(result))
    if os.environ.get('BROKEN_REPORT') == 'missing': artifact.unlink()
    if os.environ.get('BROKEN_REPORT') == 'invalid': artifact.write_text('not json')
print(json.dumps(result))
if step == 'wiki:maintain' and os.environ.get('PARTIAL'): sys.exit(1)
''')
        peer.chmod(0o755)
        for name in ['wiki', 'qmd', 'reconcile']:
            (self.root / name).symlink_to(peer)
        self.config = self.root / 'config.json'
        self.config.write_text(json.dumps({'context':'test', 'scope':'general'}))
        self.env = dict(os.environ, CALLS=str(self.root / 'calls'))

    def run_job(self, name='run'):
        p = subprocess.run([sys.executable, str(SCRIPT), '--config', str(self.config),
                            '--artifacts', str(self.root / name), '--wiki', str(self.root / 'wiki'),
                            '--qmd', str(self.root / 'qmd'), '--reconcile', str(self.root / 'reconcile')],
                           env=self.env, text=True, capture_output=True)
        return p, json.loads(p.stdout.splitlines()[-1])

    def test_successful_noop_still_updates_retrieval_and_keeps_evidence(self):
        p, report = self.run_job()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertTrue(report['ok'])
        self.assertTrue(report['contexts'][0]['noop'])
        self.assertEqual((self.root / 'calls').read_text().splitlines(), [
            'reconcile', 'wiki:maintain', 'wiki:status', 'wiki:lint',
            'qmd:update', 'qmd:embed', 'qmd:status'])
        self.assertEqual(json.loads((self.root / 'run/report.json').read_text()), report)
        self.assertTrue((self.root / 'run/02-maintain-test.exitcode').exists())

    def test_success_exit_cannot_hide_pending_work_or_invalid_contract(self):
        for i, (step, response) in enumerate([
            ('reconcile', {}), ('reconcile', {'status':'blocked'}),
            ('wiki:maintain', {'ok':True}),
            ('wiki:status', {'ok':True, 'pending':[{'phase':'compile'}]}),
            ('wiki:lint', {'ok':True, 'activeIssues':['broken link']}),
        ]):
            with self.subTest(step=step, response=response):
                (self.root / 'calls').write_text('')
                self.env.update(INVALID=step, RESPONSE=json.dumps(response))
                p, report = self.run_job('invalid-' + str(i))
                self.assertNotEqual(p.returncode, 0)
                self.assertFalse(report['ok'])
                self.assertNotIn('qmd:update', (self.root / 'calls').read_text())

    def test_verified_partial_run_continues_qmd_but_retains_failure_and_pending_work(self):
        self.env['PARTIAL'] = '1'
        p, report = self.run_job()
        self.assertNotEqual(p.returncode, 0)
        self.assertFalse(report['ok'])
        self.assertIn('qmd:embed', (self.root / 'calls').read_text())
        self.assertEqual(report['contexts'][0]['pending'][0]['sources'], ['alpha.md'])
        self.assertEqual(report['contexts'][0]['completed'], ['concepts/control'])
        self.assertEqual((self.root / 'run/02-maintain-test.exitcode').read_text(), '1\n')
        self.assertIn('broken branch', (self.root / 'run/02-maintain-test.stdout').read_text())

    def test_failed_command_retains_exit_and_stderr_and_blocks_embed(self):
        self.env['FAIL'] = 'qmd:update'
        p, report = self.run_job()
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(report['failedStep'], 'qmd-update')
        self.assertEqual((self.root / 'run/05-qmd-update.exitcode').read_text(), '7\n')
        self.assertIn('forced failure', (self.root / 'run/05-qmd-update.stderr').read_text())
        self.assertNotIn('qmd:embed', (self.root / 'calls').read_text())

    def test_missing_result_fields_or_run_reports_never_authorize_qmd(self):
        for i, (key, value) in enumerate([
            ('DROP_FIELD', 'pending'), ('DROP_FIELD', 'completed'),
            ('DROP_FIELD', 'failures'), ('DROP_FIELD', 'qmdSafe'),
            ('DROP_FIELD', 'report'), ('BROKEN_REPORT', 'missing'),
            ('BROKEN_REPORT', 'invalid'),
        ]):
            with self.subTest(key=key, value=value):
                (self.root / 'calls').write_text('')
                self.env.pop('DROP_FIELD', None)
                self.env.pop('BROKEN_REPORT', None)
                self.env[key] = value
                p, report = self.run_job('missing-' + str(i))
                self.assertNotEqual(p.returncode, 0)
                self.assertFalse(report['ok'])
                self.assertNotIn('qmd:update', (self.root / 'calls').read_text())

    def test_malformed_json_blocks_following_commands(self):
        self.env['MALFORMED'] = 'wiki:maintain'
        p, report = self.run_job()
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(report['failedStep'], 'maintain-test')
        self.assertNotIn('qmd:update', (self.root / 'calls').read_text())

    def test_concurrent_run_is_rejected_before_mutation(self):
        with (self.root / 'maintenance.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            p, report = self.run_job()
        self.assertNotEqual(p.returncode, 0)
        self.assertFalse(report['ok'])
        self.assertFalse((self.root / 'calls').exists())

    def test_existing_artifacts_are_never_overwritten(self):
        self.run_job()
        before = (self.root / 'run/report.json').read_text()
        p, _ = self.run_job()
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual((self.root / 'run/report.json').read_text(), before)


if __name__ == '__main__':
    unittest.main()
