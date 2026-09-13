"""Public deterministic adapter CLI cases for source, surface and process integrity."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from tests.publication_fixture import PublicationFixture, git
from tests import test_control_plane_black_box as harness


class PublicationAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='publication-integrity-')
        self.addCleanup(self.temporary.cleanup)
        self.fixture = PublicationFixture(Path(self.temporary.name), 43)
        self.addCleanup(self.fixture.close)

    def invoke(self, stage, optimize=False):
        plan = self.fixture.plan
        process = subprocess.run([sys.executable, *(['-O'] if optimize else []), str(harness.PILOT_ROOT / 'publication_adapter.py')],
            input=json.dumps({'stage': stage, 'plan': plan, 'fixture': str(harness.FIXTURE),
                'correlation': {'repository': plan['repository'], 'issueNumber': 43},
                'runId': '00000000-0000-4000-8000-000000000043'}), text=True,
            capture_output=True, timeout=40)
        self.assertEqual(0, process.returncode, process.stderr)
        return json.loads(process.stdout)

    def test_secret_removed_from_tip_still_blocks_outgoing_history(self):
        path = self.fixture.repo / 'credential.txt'
        path.write_text('token=ghp_' + 's' * 30)
        git(self.fixture.repo, 'add', '.')
        git(self.fixture.repo, 'commit', '-qm', 'Accidental secret')
        path.unlink()
        git(self.fixture.repo, 'add', '.')
        git(self.fixture.repo, 'commit', '-qm', 'Remove from tip')
        result = self.invoke('evidence')
        self.assertEqual('sensitive-outgoing-source', result.get('blocker'), result)

    def test_same_base_in_another_remote_does_not_authorize_that_destination(self):
        other = Path(self.temporary.name) / 'other.git'
        subprocess.run(['git', 'clone', '--bare', '-q', str(self.fixture.remote), str(other)], check=True)
        git(self.fixture.repo, 'remote', 'set-url', 'origin', str(other))
        result = self.invoke('preflight')
        self.assertEqual('git-remote-repository-mismatch', result.get('blocker'), result)

    def test_missing_screenshot_fields_are_rejected_during_readiness(self):
        from tests.publication_fixture import probe
        criterion = self.fixture.plan['criteria'][0]
        criterion['kind'] = 'ui'
        criterion['phases'] = [{'name': name, 'probe': probe(), 'execute': probe('Hello, Ada!')}
                               for name in ('interaction', 'screenshot', 'read-back')]
        result = self.invoke('preflight')
        self.assertEqual('invalid-evidence-plan', result.get('blocker'), result)

    def test_excessive_stderr_is_bounded_before_admission(self):
        self.fixture.plan['prerequisites']['tools']['argv'] = [sys.executable, '-c',
            'import sys; sys.stderr.write("x" * 1100000); print("surface available")']
        result = self.invoke('preflight')
        self.assertEqual('prerequisite-failed:tools', result.get('blocker'), result)

    def test_optimized_interpreter_cannot_disable_assignment_validation(self):
        self.fixture.plan['issueNumber'] = 999
        result = self.invoke('preflight', optimize=True)
        self.assertEqual('invalid-evidence-plan', result.get('blocker'), result)

    def test_png_without_pixel_bytes_cannot_pass_surface_readiness(self):
        import struct
        import zlib
        import hashlib
        from tests.publication_fixture import probe
        def chunk(kind, data):
            return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
        self.fixture.probe_image = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 6, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress(b'\x00')) + chunk(b'IEND', b''))
        criterion = self.fixture.plan['criteria'][0]
        criterion['kind'] = 'ui'
        criterion['phases'] = [{'name': name, 'probe': probe(), 'execute': probe('Hello, Ada!')}
                               for name in ('interaction', 'screenshot', 'read-back')]
        criterion['phases'][1].update(imagePath=str(self.fixture.root / 'result.png'),
            imageUrl=self.fixture.origin + '/image', probeImageUrl=self.fixture.origin + '/image-ready',
            probeImageSha256=hashlib.sha256(self.fixture.probe_image).hexdigest())
        result = self.invoke('preflight')
        self.assertEqual('surface-unavailable:AC1:screenshot', result.get('blocker'), result)

    def test_killed_adapter_does_not_leave_a_capture_command_running(self):
        import os
        import signal
        import time
        marker = self.fixture.root / 'capture.pid'
        (self.fixture.repo / 'greeting.py').write_text(self.fixture.agent_content)
        self.fixture.plan['criteria'][0]['phases'][0]['execute']['argv'] = [sys.executable, '-c',
            'import os,time; from pathlib import Path; Path(' + repr(str(marker)) + ').write_text(str(os.getpid())); time.sleep(20)']
        plan = self.fixture.plan
        process = subprocess.Popen([sys.executable, str(harness.PILOT_ROOT / 'publication_adapter.py')],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        def cleanup():
            if process.poll() is None: process.kill()
            process.wait(timeout=5)
            process.stdout.close(); process.stderr.close()
            if marker.exists():
                try: os.killpg(os.getpgid(int(marker.read_text())), signal.SIGKILL)
                except ProcessLookupError: pass
        self.addCleanup(cleanup)
        process.stdin.write(json.dumps({'stage': 'evidence', 'plan': plan, 'fixture': str(harness.FIXTURE),
            'correlation': {'repository': plan['repository'], 'issueNumber': 43}, 'runId': 'capture-liveness'}))
        process.stdin.close()
        deadline = time.monotonic() + 15
        while not marker.exists() and time.monotonic() < deadline: time.sleep(.05)
        self.assertTrue(marker.exists(), 'Capture command did not start')
        process.kill(); process.wait(timeout=5)
        pid = marker.read_text()
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            observed = subprocess.run(['ps', '-o', 'stat=', '-p', pid], capture_output=True, text=True).stdout.strip()
            if not observed or observed.startswith('Z'): break
            time.sleep(.05)
        else: self.fail('An abandoned capture command can still mutate the surface after replacement')
