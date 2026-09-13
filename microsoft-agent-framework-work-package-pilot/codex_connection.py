"""Multiplex the pinned public app-server protocol on one owned process."""
from concurrent.futures import Future
import itertools
import threading
from codex_process import CodexProcess, RpcFailure


class Connection:
    def __init__(self, executable, repository, environment, on_event=lambda event: None):
        self.owned = CodexProcess(executable, repository, environment, timeout=60)
        self.waiters = {}
        self.ids = itertools.count(1)
        self.lock = threading.Lock()
        self.events = []
        self.on_event = on_event
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()
        self.initialized = self.request('initialize', {'clientInfo': {'name': 'wpcp_real_adapter', 'version': '1'},
                                   'capabilities': {'experimentalApi': False}})
        self.send({'method': 'initialized'})

    def send(self, message):
        with self.lock:
            self.owned._send(message)

    def request(self, method, params, timeout=60):
        future = Future()
        with self.lock:
            identity = next(self.ids)
            self.waiters[identity] = future
            self.owned._send({'id': identity, 'method': method, 'params': params})
        try:
            return future.result(timeout=timeout)
        finally:
            with self.lock:
                self.waiters.pop(identity, None)

    def _read(self):
        while True:
            event = self.owned.pending.get()
            if event is None:
                with self.lock:
                    for future in self.waiters.values():
                        if not future.done(): future.set_exception(RpcFailure('process-failure'))
                self.on_event({'method': 'wpcp/runtimeExited', 'params': {'process': self.owned.ownership}})
                return
            if 'id' in event and 'method' not in event:
                with self.lock:
                    future = self.waiters.get(event['id'])
                    if future and not future.done():
                        if 'error' in event:
                            future.set_exception(RpcFailure('rpc-rejected', event['error'].get('code'),
                                                           event['error'].get('message')))
                        else: future.set_result(event['result'])
            elif 'id' in event:
                # The MCP execution channel owns tools. Never accept an unexpected
                # native approval, permission request or dynamically injected tool.
                self.send({'id': event['id'], 'error': {'code': -32601, 'message': 'Unsupported capability'}})
            else:
                if not event.get('method', '').endswith('/delta'):
                    self.events.append(event)
                    if len(self.events) > 8192: del self.events[:4096]
                self.on_event(event)

    def close(self):
        result = self.owned.close()
        self.reader.join(timeout=2)
        return result
