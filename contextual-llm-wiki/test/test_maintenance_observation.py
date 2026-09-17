import json
import os
import shutil
from pathlib import Path
import subprocess
import tempfile
import time
import unittest

RUNNER = Path(__file__).resolve().parents[1] / 'scripts/run-maintenance.py'

class MaintenanceObservation(unittest.TestCase):
    def test_exited_helper_without_report_is_not_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            helper = root / 'helper.py'
            helper.write_text('print("No final report")\n')
            result = subprocess.run(['python3', str(RUNNER), '--helper', str(helper), '--artifacts', str(root/'run'), '--config', str(root/'config.json')], capture_output=True, text=True, timeout=4)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout.strip().splitlines()[-1])['outcome'], 'missing-or-invalid-report')

    def test_missing_report_is_finite_and_diagnoses_the_single_owned_helper(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            helper = root / 'helper.py'
            helper.write_text("import sys,time,pathlib,json\np=pathlib.Path(sys.argv[sys.argv.index('--artifacts')+1]);p.mkdir();(p/'progress.json').write_text(json.dumps({'phase':'held','active':True,'remaining':[{'sources':['alpha/a.md']}]}));time.sleep(30)\n")
            start = time.monotonic()
            result = subprocess.run(['python3', str(RUNNER), '--helper', str(helper), '--artifacts', str(root/'run'), '--budget-seconds', '0.2', '--termination-grace-seconds', '0.1', '--observation-margin-seconds', '0.2', '--stall-seconds', '0.1', '--config', str(root/'config.json'), '--qmd', '/usr/bin/true', '--reconcile', '/dev/null'], capture_output=True, text=True, timeout=4)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertLess(time.monotonic()-start, 3)
            value = json.loads(result.stdout.strip().splitlines()[-1])
            self.assertFalse(value['ok'])
            self.assertEqual(value['outcome'], 'observation-expired')
            self.assertEqual(value['helper']['starts'], 1)
            self.assertFalse(value['helper']['running'])
            self.assertEqual(value['progress']['remaining'][0]['sources'], ['alpha/a.md'])
            self.assertTrue((root/'run/diagnosis.json').exists())
            self.assertEqual(json.loads((root/'run/observation.json').read_text()), value)
            if os.environ.get('WIKI_TEST_ROOT'):
                target = Path(os.environ['WIKI_TEST_ROOT']) / ('missing-report-' + str(time.time_ns()))
                shutil.copytree(root/'run', target)
                print('Missing-report evidence: ' + str(target))

    def test_completion_requires_matching_exit_report_and_no_remaining_work(self):
        for name, code, ok, remaining, expected in [('success', 0, True, [], 0), ('failed', 1, True, [], 1), ('incomplete', 0, False, [], 1), ('pending', 0, True, ['source'], 1)]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                helper = root/'helper.py'
                report = {'ok': ok, 'contexts': [{'ok': True}], 'remaining': remaining}
                helper.write_text("import sys,pathlib,json\np=pathlib.Path(sys.argv[sys.argv.index('--artifacts')+1]);p.mkdir();(p/'report.json').write_text(" + repr(json.dumps(report)) + ");sys.exit("+str(code)+")\n")
                result = subprocess.run(['python3', str(RUNNER), '--helper', str(helper), '--artifacts', str(root/'run')], capture_output=True, text=True, timeout=4)
                self.assertEqual(result.returncode, expected, result.stderr)
                value = json.loads(result.stdout.strip().splitlines()[-1])
                self.assertEqual(value['ok'], expected == 0)
                self.assertEqual(value['helper']['starts'], 1)

    def test_equal_form_lock_cannot_bypass_an_existing_owner(self):
        import fcntl
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            lock=root/'shared.lock'
            with lock.open('w') as owned:
                fcntl.flock(owned, fcntl.LOCK_EX)
                result=subprocess.run(['python3',str(RUNNER),'--artifacts',str(root/'runs/run'),'--lock-file='+str(lock),'--config',str(root/'missing.json'),'--qmd','/usr/bin/true','--reconcile','/dev/null'],capture_output=True,text=True,timeout=4)
            value=json.loads(result.stdout.strip().splitlines()[-1])
            self.assertEqual(result.returncode,1)
            self.assertIn('Resource temporarily unavailable',value['report']['error'])
            self.assertFalse((root/'runs/maintenance.lock').exists())

    def test_artifact_failure_still_emits_structured_non_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            helper=root/'helper.py'
            helper.write_text("import sys,pathlib,json\np=pathlib.Path(sys.argv[sys.argv.index('--artifacts')+1]);p.mkdir();(p/'report.json').write_text(json.dumps({'ok':True,'contexts':[{'ok':True}]}));o=p.parent/'process.json';o.unlink();o.mkdir()\n")
            result=subprocess.run(['python3',str(RUNNER),'--helper',str(helper),'--artifacts',str(root/'run')],capture_output=True,text=True,timeout=4)
            value=json.loads(result.stdout.strip().splitlines()[-1])
            self.assertEqual(result.returncode,1)
            self.assertFalse(value['ok'])
            self.assertEqual(value['outcome'],'observer-storage-failure')
            self.assertEqual(value['helper']['exitCode'],0)

    def test_reusing_artifacts_cannot_reuse_an_old_success_or_start_again(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            helper=root/'helper.py'
            helper.write_text("import sys,pathlib,json\np=pathlib.Path(sys.argv[sys.argv.index('--artifacts')+1]);p.mkdir();(p/'report.json').write_text(json.dumps({'ok':True,'contexts':[{'ok':True}]}));c=p.parent.parent/'starts';c.write_text(c.read_text()+'1' if c.exists() else '1')\n")
            args=['python3',str(RUNNER),'--helper',str(helper),'--artifacts',str(root/'run')]
            first=subprocess.run(args,capture_output=True,text=True,timeout=4)
            self.assertEqual(first.returncode,0)
            original=(root/'run/observation.json').read_bytes()
            second=subprocess.run(args,capture_output=True,text=True,timeout=4)
            self.assertEqual(second.returncode,1)
            value=json.loads(second.stdout.strip().splitlines()[-1])
            self.assertFalse(value['ok'])
            self.assertEqual(value['helper']['starts'],0)
            self.assertEqual(value['outcome'],'artifact-directory-unavailable')
            self.assertEqual((root/'starts').read_text(),'1')
            self.assertEqual((root/'run/observation.json').read_bytes(),original)
            if os.environ.get('WIKI_TEST_ROOT'):
                target=Path(os.environ['WIKI_TEST_ROOT']) / ('critical-artifact-reuse-' + str(time.time_ns()) + '.json')
                target.write_text(json.dumps({'first':json.loads(first.stdout.strip().splitlines()[-1]),'second':value,'firstExit':first.returncode,'secondExit':second.returncode,'starts':(root/'starts').read_text(),'oldReportPreserved':True},indent=2))
                print('Artifact reuse evidence: ' + str(target))
