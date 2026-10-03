import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import time
import unittest


RUNNER = Path(__file__).resolve().parents[1] / 'run-qmd-daily.py'



class QmdRunnerTests(unittest.TestCase):
    def test_timeout_stops_owned_descendant_before_reporting_completion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            started = root / 'started'
            late = root / 'late-write'
            child = "from pathlib import Path; import time; Path(%r).write_text('started'); time.sleep(1.5); Path(%r).write_text('late')" % (str(started), str(late))
            parent = root / 'parent.py'
            parent.write_text('import subprocess, sys, time\nsubprocess.Popen([sys.executable, "-c", %r], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\ntime.sleep(60)\n' % child)
            step = runpy.run_path(str(RUNNER))['run_step']
            result = step(root, 'owned-timeout', [sys.executable, str(parent)], 1)
            self.assertTrue(started.exists(), 'fixture must launch its child before the timeout')
            self.assertEqual(result['exitCode'], 124)
            time.sleep(1.2)
            self.assertFalse(late.exists(), 'owned child must not mutate files after timeout completion')
            self.assertIn('Timed out', (root / result['stderr']).read_text())

    def run_cli(self, fail_update=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / 'shared-ai-docs/scripts/run-qmd-daily.py'
            script.parent.mkdir(parents=True)
            shutil.copy2(RUNNER, script)
            reconcile = root / 'danielsvault-rag/scripts/sync-qmd-collections.py'
            reconcile.parent.mkdir(parents=True)
            reconcile.write_text('import json\nprint(json.dumps({"status":"ok","unchanged":["original"],"missing":[],"conflicts":[]}))\n')
            binaries = root / 'bin'
            binaries.mkdir()
            trace = root / 'trace'
            qmd = binaries / 'qmd'
            qmd.write_text('#!'+sys.executable+'\nimport os, sys\nfrom pathlib import Path\nwith Path(os.environ["TEST_QMD_TRACE"]).open("a") as f: f.write(sys.argv[1]+"\\n")\nif sys.argv[1]=="status": print("Total: 3 files indexed\\nVectors: 2 embedded")\nif sys.argv[1]=="update" and os.environ.get("TEST_FAIL_UPDATE")=="1": sys.exit(9)\n')
            qmd.chmod(0o755)
            node = binaries / 'node'
            node.write_text('#!/bin/sh\nexit 0\n')
            node.chmod(0o755)
            database = root / 'index.sqlite'
            database.touch()
            artifacts = root / 'artifacts'
            env = os.environ.copy()
            env.update(PATH=str(binaries)+os.pathsep+env.get('PATH',''), INDEX_PATH=str(database), TEST_QMD_TRACE=str(trace), TEST_FAIL_UPDATE='1' if fail_update else '0', PYTHONDONTWRITEBYTECODE='1')
            process = subprocess.run([sys.executable,str(script),'--artifacts',str(artifacts)],env=env,capture_output=True,text=True)
            return process.returncode, json.loads((artifacts/'report.json').read_text()), trace.read_text().splitlines()

    def test_public_runner_preserves_successful_pipeline_and_counts(self):
        code, report, commands = self.run_cli()
        self.assertEqual(code, 0)
        self.assertTrue(report['ok'])
        self.assertEqual(commands, ['status','update','embed','status'])
        self.assertEqual(report['index'], {'documents':3,'vectors':2,'pendingEmbeddings':0})
        self.assertEqual(report['collections'], {'unchanged':1,'missing':[]})

    def test_public_runner_skips_embedding_and_reports_failure_after_update_error(self):
        code, report, commands = self.run_cli(fail_update=True)
        self.assertEqual(code, 1)
        self.assertFalse(report['ok'])
        self.assertEqual(commands, ['status','update','status'])
        self.assertEqual(report['steps']['update']['exitCode'], 9)
        self.assertEqual(report['steps']['embed'], {'skipped':'update failed'})
        self.assertEqual(report['steps']['finalStatus']['exitCode'], 0)


if __name__ == '__main__':
    unittest.main()
