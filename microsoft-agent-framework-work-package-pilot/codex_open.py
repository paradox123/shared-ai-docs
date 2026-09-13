"""Open the selected attempt in the pinned native Codex TUI."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlparse
import uuid
from codex_adapter import http_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api-url', required=True); parser.add_argument('--run-id', required=True)
    parser.add_argument('--attempt-id', required=True)
    parser.add_argument('--config', default=str(Path(__file__).with_name('codex-runtime-pin.json')))
    parser.add_argument('--prompt')
    args = parser.parse_args()
    pin = json.loads(Path(args.config).read_text())
    if hashlib.sha256(Path(pin['executable']).read_bytes()).hexdigest() != pin['sha256']:
        raise SystemExit('runtime-drift')
    headers = {'Authorization': 'Bearer ' + os.environ['WPCP_PROVIDER_TOKEN']}
    if fixture := os.environ.get('WPCP_FIXTURE_ACCESS_TOKEN'):
        headers['X-Wpcp-Fixture-Access'] = fixture
    base = args.api_url.rstrip('/') + '/api/v1/runs/' + str(uuid.UUID(args.run_id))
    status, run = http_json(base, headers=headers)
    if status != 200: raise SystemExit('run-access-denied')
    attempt = next(a for a in run['attempts'] if a['attemptId'] == args.attempt_id)
    status, opened = http_json(base + '/attempts/' + args.attempt_id + '/open', 'POST', {
        'commandId': str(uuid.uuid4()), 'requestId': attempt['session']['humanRequest']['requestId']}, headers)
    capability = opened.get('capability') or {}
    if status != 200 or capability.get('mode') != 'same-session':
        raise SystemExit('Direct opening unavailable; use the explicit Operator handoff decision.')
    url = capability.get('url', '')
    parsed = urlparse(url)
    session = attempt['session']['sessionId']
    if parsed.scheme != 'ws' or parsed.hostname != '127.0.0.1' or parsed.path != '/sessions/' + session:
        raise SystemExit('Unverified native endpoint')
    environment = os.environ.copy()
    environment['WPCP_NATIVE_CREDENTIAL'] = 'wpcp1.' + base64.urlsafe_b64encode(json.dumps({
        'sessionId': session, 'credential': headers['Authorization']}).encode()).decode()
    command = [pin['executable'], '--remote', f'ws://{parsed.netloc}', '--remote-auth-token-env', 'WPCP_NATIVE_CREDENTIAL',
               '--sandbox', 'read-only', '--ask-for-approval', 'never', '--no-alt-screen', 'resume', session]
    if args.prompt: command.append(args.prompt)
    os.execve(pin['executable'], command, environment)


if __name__ == '__main__':
    main()
