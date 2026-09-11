"""Re-run Ticket 04's real process checks and retain sanitized public evidence."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[4]
PILOT = ROOT / 'microsoft-agent-framework-work-package-pilot'
sys.path.insert(0, str(PILOT))
os.chdir(PILOT)
from tests.test_fake_codex_attempt import FakeCodexTests
from tests import test_control_plane_black_box as harness

OUT = Path(__file__).resolve().parent
fixture = json.loads(harness.FIXTURE.read_text())
canaries = [entry['value'] for entry in fixture['redactionPolicy']['controlledCanaries']]
stream = (OUT / 'public-observations.jsonl').open('w')


def record(kind, **data):
    raw = json.dumps({'at': datetime.now(timezone.utc).isoformat(), 'kind': kind, **data}, ensure_ascii=False)
    for canary in canaries:
        raw = raw.replace(canary, '[REDACTED:CONTROLLED-CANARY]')
    stream.write(raw + '\n')
    stream.flush()


class RecordedProof(FakeCodexTests):
    @classmethod
    def request(cls, method, path, *args, **kwargs):
        status, body, raw = super().request(method, path, *args, **kwargs)
        if path != '/healthz' and status:
            record('http', method=method, path=path, actor=kwargs.get('actor_id'), status=status, body=body)
        return status, body, raw

    @classmethod
    def operator_cli(cls, *args):
        result = super().operator_cli(*args)
        record('operator-cli', command=args[0], exitCode=result[0], body=result[1])
        return result

    def paused_worker(self, run_id, port, hook, *extra):
        process = super().paused_worker(run_id, port, hook, *extra)
        record('worker-at-crash-boundary', runId=run_id, boundary=hook, pid=process.pid)
        self.addCleanup(lambda: record('worker-exit', runId=run_id, pid=process.pid, exitCode=process.poll()))
        return process

    def run_fake(self, run_id, port, *extra):
        result = super().run_fake(run_id, port, *extra)
        record('worker-delivery', runId=run_id, exitCode=result.returncode, stdout=result.stdout, stderr=result.stderr)
        return result


class Result(unittest.TextTestResult):
    def addSuccess(self, test):
        record('test-pass', name=test._testMethodName)
        super().addSuccess(test)

    def addFailure(self, test, error):
        record('test-fail', name=str(test))
        super().addFailure(test, error)

    def addError(self, test, error):
        record('test-error', name=str(test))
        super().addError(test, error)


with (OUT / 'test-results.txt').open('w') as log:
    result = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=Result).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(RecordedProof))
stream.close()
manifest = {
    'timeUtc': datetime.now(timezone.utc).isoformat(), 'testsRun': result.testsRun,
    'successful': result.wasSuccessful(), 'failures': len(result.failures), 'errors': len(result.errors),
    'sourceSha256': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted((PILOT / 'src').rglob('*.cs')) if '/obj/' not in str(path) and '/bin/' not in str(path)},
    'observationsSha256': hashlib.sha256((OUT / 'public-observations.jsonl').read_bytes()).hexdigest(),
}
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print((OUT / 'test-results.txt').read_text())
print(json.dumps({key: value for key, value in manifest.items() if key != 'sourceSha256'}, indent=2))
raise SystemExit(0 if result.wasSuccessful() else 1)
