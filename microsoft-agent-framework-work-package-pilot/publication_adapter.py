"""Deterministic trusted-plan runner. PostgreSQL worker owns dispatch/recovery state."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import shutil
import subprocess
import sys
import urllib.request
import urllib.parse

PHASES = {'command': ['read-back'], 'rest': ['request', 'response', 'read-back'],
          'ui': ['interaction', 'screenshot', 'read-back'],
          'idempotency': ['request', 'response', 'repeat', 'read-back'],
          'document': ['generate', 'render', 'inspect', 'read-back'],
          'negative-gate': ['rejection', 'read-back'], 'recovery': ['restart', 'read-back'],
          'background': ['request', 'read-back']}
PREREQUISITES = {'contract', 'tools', 'dependencies', 'access', 'sandbox'}


class Blocked(Exception):
    pass


def run_command(argv, cwd, env=None, timeout=30):
    if not isinstance(argv, list) or not argv or not all(isinstance(a, str) and a for a in argv):
        raise Blocked('invalid-command')
    environment = {k: os.environ[k] for k in ('PATH', 'HOME', 'TMPDIR', 'LANG') if k in os.environ}
    environment.update(PYTHONDONTWRITEBYTECODE='1', GIT_TERMINAL_PROMPT='0', GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
    environment.update(env or {})
    process = subprocess.Popen(argv, cwd=cwd, env=environment, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, start_new_session=True)
    try:
        stdout, _ = process.communicate(timeout=timeout)
    except BaseException:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise
    if process.returncode != 0 or len(stdout) > 1024 * 1024:
        raise Blocked('command-failed')
    return stdout.decode('utf-8').strip()


def git(plan, *args):
    return run_command(['git', '-c', 'core.hooksPath=/dev/null', '-C', plan['localPath'], *args], plan['localPath'])


def checked(command, plan, head=None):
    output = run_command(command['argv'], plan['localPath'], {'WPCP_EVIDENCE_HEAD': head or ''})
    if output != command['expected']:
        raise Blocked('business-assertion-failed')
    return {'argv': command['argv'], 'expected': command['expected'], 'observed': output}


def validate(plan, correlation):
    try:
        assert plan['schemaVersion'] == 'wpcp-publication-plan/v1'
        assert plan['repository'] == correlation['repository']
        assert plan['issueNumber'] == correlation['issueNumber']
        assert Path(plan['localPath']).is_absolute() and Path(plan['localPath']).is_dir()
        assert re.fullmatch(r'[0-9a-f]{40}', plan['expectedBaseSha'])
        assert re.fullmatch(r'[A-Za-z0-9_-]+', plan['remoteName'])
        assert plan['branch'] != plan['baseBranch']
        for name in ('branch', 'baseBranch'):
            git(plan, 'check-ref-format', 'refs/heads/' + plan[name])
        origin = urllib.parse.urlsplit(plan['providerOrigin'])
        assert origin.scheme == 'https' or (origin.scheme == 'http' and origin.hostname in ('127.0.0.1', 'localhost'))
        assert not origin.username and not origin.password and origin.path in ('', '/') and not origin.query and not origin.fragment
        assert PREREQUISITES <= set(plan['prerequisites'])
        assert isinstance(plan['title'], str) and plan['title'].strip()
        assert plan['criteria'] and len({c['id'] for c in plan['criteria']}) == len(plan['criteria'])
        commands = list(plan['prerequisites'].values())
        for criterion in plan['criteria']:
            assert all(isinstance(criterion[k], str) and criterion[k].strip() for k in ('id', 'description', 'surface', 'expectedReadBack'))
            assert [p['name'] for p in criterion['phases']] == PHASES[criterion['kind']]
            assert criterion['phases'][-1]['execute']['expected'] == criterion['expectedReadBack']
            for phase in criterion['phases']:
                commands.extend([phase['probe'], phase['execute']])
        for command in commands:
            assert isinstance(command['argv'], list) and command['argv'] and all(isinstance(a, str) and a for a in command['argv'])
            assert isinstance(command['expected'], str) and command['expected'].strip()
    except (AssertionError, KeyError, TypeError, ValueError, Blocked):
        raise Blocked('invalid-evidence-plan') from None


class Provider:
    def __init__(self, plan):
        self.plan = plan
        self.origin = plan['providerOrigin'].rstrip('/')
        self.prefix = '/repos/' + plan['repository']['fullName']

    def request(self, path, body=None):
        headers = {'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json'}
        if self.origin == 'https://api.github.com' and os.environ.get('WPCP_PUBLICATION_TOKEN'):
            headers['Authorization'] = 'Bearer ' + os.environ['WPCP_PUBLICATION_TOKEN']
        request = urllib.request.Request(self.origin + self.prefix + path,
            None if body is None else json.dumps(body).encode(), headers,
            method='GET' if body is None else 'POST')
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.load(response)

    def check_repository(self):
        repo = self.request('')
        if repo.get('id') != self.plan['repository']['providerRepositoryId'] or repo.get('full_name') != self.plan['repository']['fullName']:
            raise Blocked('provider-repository-mismatch')
        if repo.get('permissions', {}).get('push') is not True:
            raise Blocked('provider-write-access-unavailable')

    def head(self, branch):
        return self.request('/commits/' + urllib.parse.quote(branch, safe=''))['sha']


def base_check(plan, provider):
    provider.check_repository()
    expected = plan['expectedBaseSha']
    local = git(plan, 'rev-parse', '--verify', 'refs/heads/' + plan['baseBranch'])
    remote = git(plan, 'ls-remote', '--exit-code', plan['remoteName'], 'refs/heads/' + plan['baseBranch']).split()[0]
    actual = provider.head(plan['baseBranch'])
    if not expected == local == remote == actual:
        raise Blocked('repository-base-mismatch')
    if git(plan, 'branch', '--show-current') != plan['branch']:
        raise Blocked('repository-branch-mismatch')
    git(plan, 'merge-base', '--is-ancestor', expected, 'HEAD')
    return {'expected': expected, 'local': local, 'remote': remote, 'provider': actual}


def agent_readiness(plan):
    origin = plan['agentOrigin'].rstrip('/')
    parsed = urllib.parse.urlsplit(origin)
    if parsed.scheme != 'http' or parsed.hostname not in ('localhost', '127.0.0.1') or parsed.username or parsed.password:
        raise Blocked('agent-origin-invalid')
    headers = {}
    if origin == os.environ.get('WPCP_REAL_ADAPTER_ORIGIN', '').rstrip('/'):
        headers['X-Wpcp-Adapter-Token'] = os.environ.get('WPCP_REAL_ADAPTER_TOKEN', '')
    request = urllib.request.Request(origin + '/publication-readiness', headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        readiness = json.load(response)
    if (readiness.get('contractVersion') != 'AgentSessionAdapter/v1' or
        Path(readiness.get('localPath', '')).resolve() != Path(plan['localPath']).resolve() or readiness.get('runtimeReady') is not True or
        readiness.get('sandboxReady') is not True):
        raise Blocked('agent-readiness-mismatch')
    if readiness.get('activeTurn'): raise Blocked('agent-turn-active')
    return readiness


def preflight(plan, correlation):
    validate(plan, correlation)
    from codex_contract import canonical_schema
    from jsonschema import Draft202012Validator
    Draft202012Validator.check_schema(canonical_schema())
    observations = []
    base = base_check(plan, Provider(plan))
    if git(plan, 'status', '--porcelain'):
        raise Blocked('initial-worktree-dirty')
    for name, command in plan['prerequisites'].items():
        try: observation = checked(command, plan)
        except Exception: raise Blocked('prerequisite-failed:' + name) from None
        observations.append({'prerequisite': name, **observation})
    for criterion in plan['criteria']:
        for phase in criterion['phases']:
            try:
                if not shutil.which(phase['execute']['argv'][0]): raise Blocked('tool-unavailable')
                observation = checked(phase['probe'], plan)
            except Exception: raise Blocked('surface-unavailable:' + criterion['id'] + ':' + phase['name']) from None
            observations.append({'criterion': criterion['id'], 'phase': phase['name'], **observation})
    adapter = agent_readiness(plan)
    if git(plan, 'status', '--porcelain'): raise Blocked('readiness-mutated-worktree')
    return {'state': 'ready', 'base': base, 'plan': plan['criteria'], 'probes': observations, 'adapter': adapter}


def evidence(plan, correlation, fixture, run_id):
    validate(plan, correlation)
    base_check(plan, Provider(plan))
    agent_readiness(plan)
    # Scan current and previously committed outgoing content; never rewrite source.
    diff = git(plan, 'diff', '--binary', plan['expectedBaseSha'])
    if redact(diff, fixture) != diff:
        raise Blocked('sensitive-outgoing-source')
    untracked = git(plan, 'ls-files', '--others', '--exclude-standard').splitlines()
    for relative in untracked:
        try: content = (Path(plan['localPath']) / relative).read_text()
        except (UnicodeError, OSError): raise Blocked('uninspectable-outgoing-source') from None
        if redact(content, fixture) != content:
            raise Blocked('sensitive-outgoing-source')
    if git(plan, 'status', '--porcelain'):
        git(plan, 'add', '--all')
        git(plan, '-c', 'user.name=WPCP Publication', '-c', 'user.email=wpcp@localhost',
            '-c', 'commit.gpgsign=false', 'commit', '-qm', 'Implement issue #' + str(plan['issueNumber']))
    head = git(plan, 'rev-parse', 'HEAD')
    if head == plan['expectedBaseSha']:
        raise Blocked('branch-not-ahead')
    entries = []
    for criterion in plan['criteria']:
        phases = []
        for phase in criterion['phases']:
            try:
                observation = checked(phase['execute'], plan, head)
                if phase['name'] == 'screenshot':
                    image = Path(phase['imagePath']).read_bytes()
                    if not image.startswith(b'\x89PNG\r\n\x1a\n'):
                        raise Blocked('invalid-screenshot')
                    with urllib.request.urlopen(phase['imageUrl'], timeout=10) as response:
                        public = response.read(4 * 1024 * 1024 + 1)
                    if image != public: raise Blocked('screenshot-readback-mismatch')
                    observation.update(imageUrl=phase['imageUrl'], imageSha256=hashlib.sha256(image).hexdigest())
            except Exception:
                raise Blocked('evidence-failed:' + criterion['id'] + ':' + phase['name']) from None
            phases.append({'name': phase['name'], 'headSha': head, **observation})
        entries.append({k: criterion[k] for k in ('id', 'description', 'kind', 'surface', 'expectedReadBack')} | {'phases': phases})
    if git(plan, 'rev-parse', 'HEAD') != head or git(plan, 'status', '--porcelain'):
        raise Blocked('evidence-head-drift')
    safe = redact(entries, fixture)
    body = ['<!-- wpcp-run:' + run_id + ' -->', 'Closes #' + str(plan['issueNumber']),
            'Evidence for commit/head `' + head + '`.',
            'Review qualification is a separate gate.']
    for entry in safe:
        body += ['### ' + entry['id'] + ': ' + entry['description'],
                 'Kind: ' + entry['kind'] + '; surface: ' + entry['surface'],
                 'Expected read-back: ' + entry['expectedReadBack']]
        for phase in entry['phases']:
            body += ['**' + phase['name'] + '**', '<pre>' + __import__('html').escape(json.dumps(phase, ensure_ascii=False, indent=2)) + '</pre>']
            if 'imageUrl' in phase: body.append('![Decisive screenshot](' + phase['imageUrl'] + ')')
    intent = {'headSha': head, 'branch': plan['branch'], 'baseBranch': plan['baseBranch'],
              'body': '\n\n'.join(body), 'title': redact(plan['title'], fixture), 'entries': safe}
    if len(intent['body']) > 60000: raise Blocked('evidence-body-too-large')
    return {'state': 'evidence-ready', 'intent': intent}


def publish(plan, correlation, intent, allow_create):
    validate(plan, correlation)
    provider = Provider(plan)
    provider.check_repository()
    head = intent['headSha']
    if git(plan, 'rev-parse', 'HEAD') != head or git(plan, 'status', '--porcelain'):
        raise Blocked('publication-head-drift')
    if intent['branch'] != plan['branch'] or intent['baseBranch'] != plan['baseBranch']:
        raise Blocked('publication-intent-conflict')
    # All states, including closed/merged PRs, prevent a duplicate creation.
    pulls = []
    for page in range(1, 101):
        found = provider.request('/pulls?state=all&head=' + urllib.parse.quote(plan['repository']['fullName'].split('/')[0] + ':' + plan['branch']) + '&per_page=100&page=' + str(page))
        if not isinstance(found, list): raise Blocked('provider-receipt-invalid')
        pulls.extend(p for p in found if p['head']['ref'] == plan['branch'] and p['head']['repo']['id'] == plan['repository']['providerRepositoryId'])
        if len(found) < 100: break
    else: raise Blocked('provider-receipt-unbounded')
    if len(pulls) > 1: raise Blocked('provider-receipt-ambiguous')
    if not pulls:
        if not allow_create: raise Blocked('publication-create-uncertain')
        base_check(plan, provider)
        remote_ref = git(plan, 'ls-remote', plan['remoteName'], 'refs/heads/' + plan['branch'])
        if remote_ref and remote_ref.split()[0] != head:
            raise Blocked('remote-branch-conflict')
        git(plan, 'push', '--porcelain', '--force-with-lease=refs/heads/' + plan['branch'] + ':' + (head if remote_ref else ''),
            plan['remoteName'], head + ':refs/heads/' + plan['branch'])
        if provider.head(plan['branch']) != head: raise Blocked('provider-head-mismatch')
        created = provider.request('/pulls', {'title': intent['title'], 'body': intent['body'],
            'head': plan['branch'], 'base': plan['baseBranch'], 'draft': True})
        pulls = [created]
    pull = provider.request('/pulls/' + str(pulls[0]['number']))
    if (pull['draft'] is not True or pull['state'] != 'open' or pull['head']['sha'] != head or
        pull['head']['ref'] != plan['branch'] or pull['head']['repo']['id'] != plan['repository']['providerRepositoryId'] or
        pull['base']['ref'] != plan['baseBranch'] or pull['base']['repo']['id'] != plan['repository']['providerRepositoryId'] or
        pull['body'] != intent['body'] or provider.head(plan['branch']) != head):
        raise Blocked('provider-receipt-conflict')
    return {'state': 'draft-published', 'pullRequest': pull, 'adopted': not allow_create}


def redact(value, fixture):
    policy = fixture['redactionPolicy']
    marker = policy['marker']
    def text(value):
        for canary in sorted((c['value'] for c in policy['controlledCanaries']), key=len, reverse=True):
            value = value.replace(canary, marker)
        value = re.sub(r'(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+', r'\1' + marker, value)
        value = re.sub(r'\b(?:gh[pousr]_[A-Za-z0-9_]{10,}|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{12,})\b', marker, value)
        value = re.sub(r'(?i)((?:password|token|secret|authorization)\s*[:=]\s*)[^\s,;]+', r'\1' + marker, value)
        value = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', marker, value)
        return value
    if isinstance(value, str): return text(value)
    if isinstance(value, list): return [redact(v, fixture) for v in value]
    if isinstance(value, dict):
        return {text(k): marker if k.lower() in ('password', 'token', 'secret', 'authorization') else redact(v, fixture) for k, v in value.items()}
    return value


def main():
    request = json.load(sys.stdin)
    fixture = json.loads(Path(request['fixture']).read_text())
    try:
        stage = request['stage']
        if stage == 'preflight': result = preflight(request['plan'], request['correlation'])
        elif stage == 'evidence': result = evidence(request['plan'], request['correlation'], fixture, request['runId'])
        elif stage == 'publish': result = publish(request['plan'], request['correlation'], request['intent'], request['allowCreate'])
        else: raise Blocked('unknown-publication-stage')
    except Blocked as error:
        result = {'state': 'preflight-blocked' if request['stage'] == 'preflight' else 'publication-blocked', 'blocker': str(error)}
    except Exception:
        result = {'state': 'preflight-blocked' if request['stage'] == 'preflight' else 'publication-blocked', 'blocker': 'publication-evidence-unavailable'}
    print(json.dumps(redact(result, fixture)))


if __name__ == '__main__': main()
