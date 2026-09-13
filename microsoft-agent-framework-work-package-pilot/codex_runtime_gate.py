"""Bounded real Codex preflight. No product repository or arbitrary prompt input."""
import argparse
import json
import hashlib
from pathlib import Path
import os
import subprocess
import tempfile
import importlib.metadata
import sys
import fcntl
import time
import shutil
import socket
import shlex
from datetime import datetime, timezone
from codex_contract import CANONICAL_PATH, endpoint_schema, validate_result
from codex_process import CodexProcess, RpcFailure


HOOK_PROMPT = 'WPCP synthetic input: reject this prompt before model dispatch.'


def install_prompt_probe(codex_state):
    # Only this reviewed canary is trusted, in disposable state. Other turns
    # retain their existing behavior; this is not a production lease hook.
    script = codex_state / 'prompt_probe.py'
    script.write_text('import json,sys\n'
        'request = json.load(sys.stdin)\n'
        f'if request.get("prompt") == {HOOK_PROMPT!r}:\n'
        '    print(json.dumps({"decision": "block", "reason": "WPCP_PROMPT_PROBE_DENIED"}))\n')
    command = shlex.join([sys.executable, str(script)])
    (codex_state / 'hooks.json').write_text(json.dumps({'hooks': {'UserPromptSubmit': [
        {'hooks': [{'type': 'command', 'command': command, 'timeout': 5}]}]}}))
    return command


def prompt_probe_configuration(runtime, repository, command):
    listed = runtime.request('hooks/list', {'cwds': [str(repository)]})
    hooks = [hook for entry in listed['data'] for hook in entry['hooks']]
    if (len(hooks) != 1 or hooks[0]['command'] != command
            or hooks[0]['eventName'] != 'userPromptSubmit' or not hooks[0]['enabled']):
        raise RpcFailure('prompt-hook-configuration-mismatch')
    hook = hooks[0]
    # This is a public thread/start config override, scoped to this session.
    # No personal hook trust, native database, or global bypass is modified.
    return {'hooks.state': {hook['key']: {'trusted_hash': hook['currentHash']}}}


def probe_prompt_hook(runtime, session_id, capabilities):
    turn = runtime.request('turn/start', {'threadId': session_id,
        'input': [{'type': 'text', 'text': HOOK_PROMPT}]})['turn']
    def matches(params):
        return params.get('threadId') == session_id and params.get('turnId') == turn['id']
    completed = runtime.wait_notification('turn/completed',
        lambda params: params.get('threadId') == session_id and params['turn']['id'] == turn['id'])
    hooks = [event['params']['run'] for event in runtime.notifications
        if event.get('method') == 'hook/completed' and matches(event['params'])]
    agent_output = any(event.get('method') == 'item/completed' and matches(event['params'])
        and event['params']['item'].get('type') != 'userMessage' for event in runtime.notifications)
    blocked = [hook for hook in hooks if hook['eventName'] == 'userPromptSubmit'
        and hook['status'] == 'blocked' and any(entry.get('text') == 'WPCP_PROMPT_PROBE_DENIED'
            for entry in hook['entries'])]
    passed = len(blocked) == 1 and completed['turn']['status'] == 'completed' and not agent_output
    capabilities['promptHook'] = {'status': 'passed' if passed else 'failed',
        'sessionId': session_id, 'turnId': turn['id'],
        'hookStatus': blocked[0]['status'] if blocked else None,
        'turnStatus': completed['turn']['status'], 'agentOutputObserved': agent_output,
        'leaseIntegrationVerified': False, 'scope': 'synthetic-trusted-hook-only'}
    if not passed:
        raise RpcFailure('prompt-hook-probe-failed')


def probe_tools(runtime, repository, root, capabilities):
    policy = {'type': 'workspaceWrite', 'networkAccess': False, 'writableRoots': [str(repository)],
              'excludeSlashTmp': True, 'excludeTmpdirEnvVar': True}
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        listener.listen()
        # The only file writes and network destination are owned local canaries.
        script = '''import json, pathlib, socket
observed = {}
pathlib.Path(%r).write_text('probe')
observed['insideWriteAllowed'] = True
try:
    pathlib.Path(%r).write_text('must be denied')
    observed['outsideWriteDenied'] = False
except PermissionError:
    observed['outsideWriteDenied'] = True
try:
    with socket.create_connection(('127.0.0.1', %r), timeout=1):
        observed['networkDenied'] = False
except PermissionError:
    observed['networkDenied'] = True
print(json.dumps(observed))
''' % (str(repository / 'probe.txt'), str(root / 'outside.txt'), listener.getsockname()[1])
        result = runtime.request('command/exec', {'command': [sys.executable, '-c', script],
            'cwd': str(repository), 'timeoutMs': 5000, 'sandboxPolicy': policy})
        try:
            observed = json.loads(result['stdout'])
        except ValueError:
            observed = {}
        passed = result['exitCode'] == 0 and observed == {
            'insideWriteAllowed': True, 'outsideWriteDenied': True, 'networkDenied': True}
        capabilities['sandbox'] = {'status': 'passed' if passed else 'failed', 'policy': policy, **observed}
        capabilities['tools'] = {'status': 'passed' if passed else 'failed',
            'exitCode': result['exitCode'], 'interface': 'command/exec', 'tool': 'python'}
        if not passed:
            raise RpcFailure('sandbox-or-tools-probe-failed')
    start = time.monotonic()
    result = runtime.request('command/exec', {'command': [sys.executable, '-c',
        "import os,time; print(os.getpid(), flush=True); time.sleep(2); print('late-output')"],
        'cwd': str(repository), 'timeoutMs': 100, 'sandboxPolicy': policy})
    output = result['stdout'].strip()
    late = 'late-output' in output
    capabilities['timeout'] = {'status': 'passed' if result['exitCode'] == 124 and output.isdigit() and not late else 'failed',
        'commandProcessId': int(output) if output.isdigit() else None, 'timeoutMs': 100,
        'elapsedSeconds': round(time.monotonic() - start, 3), 'exitCode': result['exitCode'],
        'lateOutputObserved': late}


def probe_endpoint(runtime, session_id, capabilities, report):
    schema = endpoint_schema()
    result = {'schema_version': '3', 'outcome': 'blocked', 'summary': 'Schema probe only',
              'red_green_slices': [], 'changed_files': [], 'verification': [],
              'evidence': [], 'findings': [], 'intervention': None}
    turn = runtime.request('turn/start', {'threadId': session_id,
        'input': [{'type': 'text', 'text': 'Return this JSON unchanged; do not use tools: ' + json.dumps(result)}],
        'outputSchema': schema})['turn']
    report['probeTurnId'] = turn['id']
    completed = runtime.wait_notification('turn/completed',
        lambda params: params.get('threadId') == session_id and params['turn']['id'] == turn['id'])
    status = completed['turn']['status']
    messages = [event['params']['item']['text'] for event in runtime.notifications
        if event.get('method') == 'item/completed' and event['params'].get('threadId') == session_id
        and event['params']['item'].get('type') == 'agentMessage']
    valid = False
    if status == 'completed' and messages:
        try:
            output = json.loads(messages[-1])
            valid = not validate_result(output) and output == result
        except ValueError:
            pass
    capabilities['outputSchema'] = {'status': 'passed' if valid else 'failed',
        'sessionId': session_id, 'turnId': turn['id'], 'turnStatus': status,
        'endpointSchemaSha256': hashlib.sha256(json.dumps(schema, sort_keys=True).encode()).hexdigest(),
        'canonicalValidationPassed': valid, 'exactSyntheticResultMatched': valid}
    if not valid:
        raise RpcFailure('endpoint-schema-probe-failed')


def probe_interrupt(runtime, session_id, capabilities):
    turn = runtime.request('turn/start', {'threadId': session_id,
        'input': [{'type': 'text', 'text': 'Return the previous probe JSON again. Do not use tools.'}]})['turn']
    runtime.wait_notification('turn/started',
        lambda params: params.get('threadId') == session_id and params['turn']['id'] == turn['id'])
    runtime.request('turn/interrupt', {'threadId': session_id, 'turnId': turn['id']})
    completed = runtime.wait_notification('turn/completed',
        lambda params: params.get('threadId') == session_id and params['turn']['id'] == turn['id'])
    status = completed['turn']['status']
    capabilities['interrupt'] = {'status': 'passed' if status == 'interrupted' else 'failed',
        'sessionId': session_id, 'turnId': turn['id'], 'turnStatus': status}


def persist(path, value):
    temporary = path.with_suffix('.tmp')
    with temporary.open('w') as output:
        os.chmod(temporary, 0o600)
        json.dump(value, output)
        output.flush()
        os.fsync(output.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def now():
    return datetime.now(timezone.utc).isoformat()


def probe(config, report, checkpoint=lambda: None, pause_at=None, state_dir=None):
    capabilities = report['capabilities'] = {name: {'status': 'not-executed', 'reason': 'prior-prerequisite'}
        for name in ('startFresh', 'read', 'resume', 'fork', 'interrupt', 'outputSchema', 'tools', 'protocol', 'promptHook')}
    report['issueWorkStarted'] = False
    with tempfile.TemporaryDirectory(prefix='probe-', dir=state_dir) as temporary:
        root = Path(temporary).resolve()
        repository, codex_state = root / 'repository', root / 'codex-home'
        repository.mkdir()
        codex_state.mkdir()
        hook_command = install_prompt_probe(codex_state)
        if config.get('probeEndpoint'):
            source = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'auth.json'
            if not source.is_file():
                raise RpcFailure('codex-authentication-unavailable')
            shutil.copyfile(source, codex_state / 'auth.json')
            os.chmod(codex_state / 'auth.json', 0o600)
        env = {key: os.environ[key] for key in ('PATH', 'HOME', 'TMPDIR', 'LANG') if key in os.environ}
        env['CODEX_HOME'] = str(codex_state)
        env['GIT_CONFIG_GLOBAL'] = os.devnull
        env['GIT_CONFIG_NOSYSTEM'] = '1'
        protocol_root = root / 'protocol'
        generated = subprocess.run([config['executable'], 'app-server', 'generate-json-schema',
            '--out', str(protocol_root)], env=env, capture_output=True, timeout=15)
        if generated.returncode:
            raise RpcFailure('protocol-generation-failed')
        protocol_bytes = (protocol_root / 'ClientRequest.json').read_bytes()
        report['runtime']['protocolSha256'] = hashlib.sha256(protocol_bytes).hexdigest()
        if report['runtime']['protocolSha256'] != config['protocolSha256']:
            raise RpcFailure('protocol-drift')
        methods = [variant['properties']['method']['enum'][0]
                   for variant in json.loads(protocol_bytes)['oneOf']]
        required = ['thread/start', 'thread/read', 'thread/resume', 'thread/fork',
                    'turn/start', 'turn/interrupt', 'command/exec', 'hooks/list']
        missing = sorted(set(required) - set(methods))
        capabilities['protocol'] = {'status': 'failed' if missing else 'passed',
                                    'requiredMethods': required, 'missingMethods': missing,
                                    'experimentalApi': False}
        if missing:
            raise RpcFailure('protocol-incompatible')
        report['dependencies'] = {'python': sys.version.split()[0],
                                 'jsonschema': importlib.metadata.version('jsonschema')}
        if report['dependencies']['jsonschema'] != config['jsonschemaVersion']:
            raise RpcFailure('dependency-version-mismatch')
        subprocess.run(['git', 'init', '--quiet', '--template=', str(repository)], env=env, check=True,
                       capture_output=True, timeout=10)
        remotes = subprocess.run(['git', '-C', str(repository), 'remote'], env=env, check=True,
                                 capture_output=True, text=True, timeout=10).stdout.splitlines()
        report['repository'] = {'disposable': True, 'remoteCount': len(remotes), 'issueWorkStarted': False}
        if remotes:
            raise RpcFailure('nonlocal-repository-configuration')
        runtime = CodexProcess(config['executable'], repository, env, config.get('rpcTimeoutSeconds', 15))
        report['process'] = runtime.ownership
        report['process']['startedAt'] = now()
        checkpoint()
        try:
            initialized = runtime.request('initialize', {'clientInfo': {'name': 'wpcp_runtime_gate', 'version': '1'},
                                         'capabilities': {'experimentalApi': False}})
            runtime.notify('initialized')
            report['runtime']['userAgent'] = initialized['userAgent']
            hook_configuration = prompt_probe_configuration(runtime, repository, hook_command)
            report['sessionStartState'] = 'dispatching'
            checkpoint()
            started = runtime.request('thread/start', {'cwd': str(repository),
                'sandbox': 'read-only', 'approvalPolicy': 'never', 'ephemeral': False,
                'config': hook_configuration,
                'baseInstructions': 'You are an output-format test. Never call tools or access files. Echo the JSON supplied by the user.'})
            if pause_at == 'after-session-start':
                report['faultHook'] = pause_at
                checkpoint()
                while True:
                    time.sleep(.1)
            session = started['thread']
            report['sessionStartState'] = 'mapped'
            report['capabilities']['startFresh'] = {'status': 'passed', 'sessionId': session['id']}
            checkpoint()
            report['capabilities']['sandbox'] = {'status': 'observed', 'policy': started['sandbox']}
            report['capabilities']['openInCodex'] = {'status': 'unsupported',
                'sameSession': False, 'appTaskVisible': False, 'url': None,
                'reason': 'native-client-lease-fencing-unverified',
                'canAcceptDirectInput': session.get('canAcceptDirectInput')}
            report['reasons'] = ['native-client-lease-fencing-unverified']
            report['runtime']['model'] = started['model']
            report['runtime']['reasoningEffort'] = started.get('reasoningEffort')
            probe_tools(runtime, repository, root, capabilities)
            if config.get('probeEndpoint'):
                probe_endpoint(runtime, session['id'], capabilities, report)
                checkpoint()
            for name, method in (('read', 'thread/read'), ('resume', 'thread/resume'), ('fork', 'thread/fork')):
                try:
                    response = runtime.request(method, {'threadId': session['id']})
                    target = response['thread']
                    identity_ok = (target['id'] != session['id'] and target.get('forkedFromId') == session['id']) if name == 'fork' else target['id'] == session['id']
                    capabilities[name] = {'status': 'passed' if identity_ok else 'failed',
                        'sessionId': target['id'], 'sourceSessionId': session['id'],
                        'parentSessionId': target.get('forkedFromId')}
                except RpcFailure as error:
                    capabilities[name] = {'status': 'failed', 'category': error.category, 'rpcCode': error.code,
                                          'sourceSessionId': session['id']}
            if config.get('probeEndpoint'):
                probe_interrupt(runtime, session['id'], capabilities)
            else:
                capabilities['interrupt'] = {'status': 'not-executed', 'reason': 'no-active-model-turn'}
                capabilities['outputSchema'] = {'status': 'not-executed', 'reason': 'endpoint-probe-required'}
            probe_prompt_hook(runtime, session['id'], capabilities)
        finally:
            report['processStop'] = runtime.close()
            report['processStop']['stoppedAt'] = now()


def evaluate(args, config, checkpoint, report):
    digest = hashlib.sha256(Path(config['executable']).read_bytes()).hexdigest()
    report['runtime'] = {'sha256': digest, 'expectedVersion': config['version']}
    if digest != config['sha256']:
        report['reasons'] = ['runtime-drift']
        return
    version = subprocess.run([config['executable'], '--version'], capture_output=True,
                             text=True, timeout=10)
    if version.returncode or version.stdout.strip() != config['version']:
        report['reasons'] = ['runtime-version-mismatch']
        return
    contract_digest = hashlib.sha256(CANONICAL_PATH.read_bytes()).hexdigest()
    report['runtime']['canonicalSchemaSha256'] = contract_digest
    if config['contractVersion'] != 'AgentSessionAdapter/v1' or contract_digest != config['canonicalSchemaSha256']:
        raise RpcFailure('contract-incompatible')
    probe(config, report, checkpoint, args.pause_at, args.state_dir)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--state-dir', required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--attempt-id', required=True)
    parser.add_argument('--pause-at', choices=['after-session-start'])
    parser.add_argument('--read', action='store_true')
    args = parser.parse_args()
    state = Path(args.state_dir)
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    if args.read:
        path = state / 'receipt.json'
        report = json.loads(path.read_text())['report'] if path.exists() else {'decision': 'no-go', 'reasons': ['not-started']}
        print(json.dumps(report))
        return 2
    with (state / 'delivery.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        config_bytes = Path(args.config).read_bytes()
        intent = {'runId': args.run_id, 'attemptId': args.attempt_id,
                  'configSha256': hashlib.sha256(config_bytes).hexdigest()}
        receipt_path = state / 'receipt.json'
        if receipt_path.exists():
            receipt = json.loads(receipt_path.read_text())
            report = receipt['report']
            if receipt['intent'] != intent:
                print(json.dumps({'decision': 'no-go', 'reasons': ['intent-conflict'],
                                  'runId': args.run_id, 'attemptId': args.attempt_id}))
                return 2
            if receipt['state'] != 'complete':
                report['reasons'] = ['session-start-uncertain']
                report['recovery'] = {'status': 'unsafe', 'newSessionStarted': False,
                                      'reason': 'incomplete-probe-has-no-independent-adoption-receipt'}
                receipt['state'] = 'complete'
                persist(receipt_path, receipt)
                for temporary in state.glob('probe-*'):
                    if temporary.is_dir() and not temporary.is_symlink():
                        shutil.rmtree(temporary)
            print(json.dumps(report))
            return 2
        report = {'schemaVersion': 'codex-runtime-gate/v1', 'decision': 'no-go', 'reasons': ['unprobed'],
                  'runId': args.run_id, 'attemptId': args.attempt_id,
                  'startedAt': now(), 'issueWorkStarted': False}
        receipt = {'intent': intent, 'state': 'running', 'report': report}
        checkpoint = lambda: persist(receipt_path, receipt)
        checkpoint()
        try:
            config = json.loads(config_bytes)
            if not isinstance(config, dict):
                raise ValueError('Configuration must be an object')
            evaluate(args, config, checkpoint, report)
        except RpcFailure as error:
            report['reasons'] = [error.category]
        except subprocess.TimeoutExpired:
            report['reasons'] = ['timeout']
        except (OSError, subprocess.CalledProcessError):
            report['reasons'] = ['infrastructure-failure']
        except (KeyError, ValueError, TypeError, importlib.metadata.PackageNotFoundError):
            report['reasons'] = ['preflight-configuration-invalid']
        report['completedAt'] = now()
        receipt['state'] = 'complete'
        checkpoint()
        print(json.dumps(report))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
