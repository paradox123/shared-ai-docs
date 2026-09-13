"""Owned stdio app-server process; parent loss closes stdin and stops the group."""
import json
import os
from pathlib import Path
import queue
import select
import signal
import subprocess
import sys
import threading
import time


class RpcFailure(Exception):
    def __init__(self, category, code=None, detail=None):
        super().__init__(category)
        self.category, self.code = category, code
        self.detail = detail


class CodexProcess:
    def __init__(self, executable, cwd, environment, timeout=15):
        self.timeout = timeout
        self.pending = queue.Queue(maxsize=4096)
        self.notifications = []
        self.counter = 0
        self.process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()),
            '--supervise', executable], cwd=cwd, env=environment,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, start_new_session=True)
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()
        try:
            self.ownership = self._next(time.monotonic() + timeout)['supervisorStarted']
        except Exception:
            self.close()
            raise

    def _read(self):
        try:
            for line in self.process.stdout:
                try:
                    self.pending.put(json.loads(line), timeout=self.timeout)
                except (json.JSONDecodeError, queue.Full):
                    break
        finally:
            try:
                self.pending.put(None, timeout=self.timeout)
            except queue.Full:
                pass

    def _next(self, deadline):
        try:
            value = self.pending.get(timeout=max(0, deadline - time.monotonic()))
        except queue.Empty:
            raise RpcFailure('timeout') from None
        if value is None:
            raise RpcFailure('process-failure')
        return value

    def notify(self, method, params=None):
        self._send({'method': method, **({'params': params} if params is not None else {})})

    def _send(self, value):
        try:
            self.process.stdin.write(json.dumps(value) + '\n')
            self.process.stdin.flush()
        except (BrokenPipeError, OSError):
            raise RpcFailure('process-failure') from None

    def request(self, method, params):
        self.counter += 1
        identity = self.counter
        self._send({'id': identity, 'method': method, 'params': params})
        deadline = time.monotonic() + self.timeout
        while True:
            value = self._next(deadline)
            if value.get('id') == identity and 'method' not in value:
                if 'error' in value:
                    # Raw upstream errors can include credentials or private paths.
                    raise RpcFailure('rpc-rejected', value['error'].get('code'), value['error'].get('message'))
                return value['result']
            self._observe(value)

    def _observe(self, value):
        if 'id' in value and 'method' in value:
            self._send({'id': value['id'], 'error': {'code': -32601,
                       'message': 'Probe does not authorize server requests'}})
        else:
            self.notifications.append(value)
            if len(self.notifications) > 4096:
                raise RpcFailure('notification-overflow')

    def wait_notification(self, method, predicate=lambda _: True):
        deadline = time.monotonic() + self.timeout
        while True:
            for index, value in enumerate(self.notifications):
                if value.get('method') == method and predicate(value.get('params', {})):
                    return self.notifications.pop(index)['params']
            self._observe(self._next(deadline))

    def close(self):
        if self.process.stdin:
            try:
                self.process.stdin.close()
            except OSError:
                pass
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(self.process.pid, signal.SIGKILL)
            self.process.wait(timeout=5)
        self.reader.join(timeout=1)
        self.process.stdout.close()
        return {'processGroupId': self.process.pid, 'status': 'stopped',
                'exitCode': self.process.returncode}


def supervise(executable):
    # This supervisor remains the process-group owner even if Codex exits first.
    # EOF on the owning adapter's pipe also covers an adapter SIGKILL.
    child = subprocess.Popen([executable, 'app-server', '--stdio'],
        stdin=subprocess.PIPE, stdout=sys.stdout, stderr=subprocess.DEVNULL)
    # Set this after spawn so Codex does not inherit an ignored SIGTERM.
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    print(json.dumps({'supervisorStarted': {'processGroupId': os.getpid(),
        'processId': child.pid, 'ownerProcessId': os.getppid()}}), flush=True)
    try:
        while child.poll() is None:
            readable, _, _ = select.select([sys.stdin.buffer], [], [], .05)
            if readable:
                data = os.read(sys.stdin.fileno(), 65536)
                if not data:
                    break
                child.stdin.write(data)
                child.stdin.flush()
    finally:
        # Kill the entire owned group, including descendants surviving the leader.
        os.killpg(os.getpgrp(), signal.SIGTERM)
        try:
            child.wait(timeout=.2)
        except subprocess.TimeoutExpired:
            pass
        os.killpg(os.getpgrp(), signal.SIGKILL)


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] != '--supervise':
        raise SystemExit(2)
    supervise(sys.argv[2])
