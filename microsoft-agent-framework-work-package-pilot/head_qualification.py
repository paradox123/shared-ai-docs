"""Head-bound deterministic and external qualification boundaries."""
import hashlib
import json
import os
from pathlib import Path
import urllib.parse
import urllib.request
import uuid

from publication_adapter import Blocked, Provider, checked, git, redact

AXES = ('requirements', 'code-quality', 'architecture')
SKILLS = {'requirements': ('code-review',), 'code-quality': ('code-review',),
          'architecture': ('codebase-design', 'domain-modeling')}


def require(condition):
    if not condition: raise ValueError("invalid-qualification-contract")


def validate_config(config):
    try:
        command = config['verification']
        require(isinstance(command['argv'], list) and command['argv'] and all(isinstance(a, str) and a for a in command['argv']))
        require(isinstance(command['expected'], str) and command['expected'].strip())
        require(isinstance(config['requirements'], str) and config['requirements'].strip())
        require(isinstance(config['guidance'], list))
        for path in config['guidance']:
            require(isinstance(path, str) and path and not Path(path).is_absolute() and '..' not in Path(path).parts)
        require(set(config['skills']) == {'code-review', 'codebase-design', 'domain-modeling'})
        for skill in config['skills'].values():
            require(Path(skill['path']).is_absolute())
            require(hashlib.sha256(Path(skill['path']).read_bytes()).hexdigest() == skill['sha256'])
    except (ValueError, KeyError, TypeError, OSError):
        raise Blocked('invalid-head-qualification-plan') from None


def current_head(plan, head, pull_number):
    if (git(plan, 'rev-parse', 'HEAD') != head or git(plan, 'status', '--porcelain') or
            git(plan, 'branch', '--show-current') != plan['branch']):
        raise Blocked('qualification-head-drift')
    provider = Provider(plan)
    provider.check_repository()
    pull = provider.request('/pulls/' + str(pull_number))
    if (pull['state'] != 'open' or pull['draft'] is not True or
            pull['head']['sha'] != head or pull['head']['ref'] != plan['branch'] or
            pull['head']['repo']['id'] != plan['repository']['providerRepositoryId'] or
            pull['base']['ref'] != plan['baseBranch'] or
            pull['base']['repo']['id'] != plan['repository']['providerRepositoryId'] or
            provider.head(plan['branch']) != head):
        raise Blocked('qualification-head-drift')
    return {'state': 'head-current', 'headSha': head}


def verify(plan, head, pull_number):
    current_head(plan, head, pull_number)
    try:
        report = {'state': 'check-passed', **checked(plan['headQualification']['verification'], plan, head)}
    except Blocked as error:
        report = {'state': 'check-failed', 'blocker': str(error),
                  'argv': plan['headQualification']['verification']['argv']}
    finally:
        current_head(plan, head, pull_number)
    return {**report, 'headSha': head}


def review_input(plan, head, intent, fixture):
    config = plan['headQualification']
    validate_config(config)
    return redact({'requirements': config['requirements'], 'evidence': intent['entries'],
        'diff': git(plan, 'diff', plan['expectedBaseSha'], head),
        'guidance': {p: git(plan, 'show', head + ':' + p) for p in config['guidance']}}, fixture)


def review_policy(config, axis):
    return {'model': 'gpt-5.6-terra', 'reasoningEffort': 'xhigh', 'access': 'read-only',
        'skills': [{'name': name, 'sha256': config['skills'][name]['sha256']} for name in SKILLS[axis]]}


def adapter_request(plan, route, operation, request):
    origin = plan['agentOrigin'].rstrip('/')
    parsed = urllib.parse.urlsplit(origin)
    if (parsed.scheme != 'http' or parsed.hostname not in ('localhost', '127.0.0.1') or
            parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment):
        raise Blocked('agent-origin-invalid')
    headers = {'Content-Type': 'application/json',
        'X-Wpcp-Worker-Pid': os.environ.get('WPCP_PUBLICATION_OWNER_PID', str(os.getpid()))}
    if origin == os.environ.get('WPCP_REAL_ADAPTER_ORIGIN', '').rstrip('/'):
        headers['X-Wpcp-Adapter-Token'] = os.environ.get('WPCP_REAL_ADAPTER_TOKEN', '')
    url = origin + '/' + route + '/' + str(uuid.UUID(operation))
    with urllib.request.urlopen(urllib.request.Request(url, json.dumps(request).encode(), headers, method='PUT'), timeout=150) as response:
        return json.load(response)


def validate_review_result(result, axis, head):
    try:
        require(set(result) == {'schemaVersion', 'axis', 'headSha', 'verdict', 'rationale', 'findings'})
        require(result['schemaVersion'] == 'wpcp-review/v1' and result['axis'] == axis and result['headSha'] == head)
        require(result['verdict'] in ('pass', 'fail', 'not_applicable'))
        require(axis != 'requirements' or result['verdict'] != 'not_applicable')
        require(isinstance(result['rationale'], str) and result['rationale'].strip())
        require(isinstance(result['findings'], list))
        require(bool(result['findings']) == (result['verdict'] == 'fail'))
        for finding in result['findings']:
            require(set(finding) == {'location', 'description'})
            require(all(isinstance(v, str) and v.strip() for v in finding.values()))
    except (ValueError, KeyError, TypeError):
        raise Blocked('invalid-review-result') from None


def review(request, fixture):
    plan, head = request['plan'], request['headSha']
    current_head(plan, head, request['pullNumber'])
    axis = request['axis']
    policy = review_policy(plan['headQualification'], axis)
    assignment = {'runId': request['runId'], 'axis': axis, 'headSha': head,
        'localPath': plan['localPath'], 'policy': policy,
        'input': review_input(plan, head, request['intent'], fixture),
        'skills': {name: Path(plan['headQualification']['skills'][name]['path']).read_text() for name in SKILLS[axis]}}
    receipt = None
    try:
        receipt = adapter_request(plan, 'qualification-reviews', request['operationKey'], assignment)
        if (receipt['contractVersion'] != 'HeadQualificationAdapter/v1' or
                receipt['operationKey'] != request['operationKey'] or receipt['policy'] != policy):
            raise Blocked('invalid-review-receipt')
        uuid.UUID(receipt['sessionId'])
        validate_review_result(receipt['result'], axis, head)
    except (Blocked, KeyError, TypeError, ValueError) as error:
        return {'state': 'review-invalid', 'blocker': str(error) if isinstance(error, Blocked) else 'invalid-review-receipt',
                'receipt': receipt}
    finally:
        current_head(plan, head, request['pullNumber'])
    return {'state': 'review-completed', **receipt}


def repair_policy(number, local_path):
    if not 1 <= number <= 3:
        raise Blocked('repair-limit-exhausted')
    return {'model': 'gpt-5.6-sol' if number == 3 else 'gpt-5.6-terra',
        'reasoningEffort': 'xhigh', 'access': 'workspace-write', 'writableRoots': [local_path],
        'escalationReason': 'final_repair_round' if number == 3 else None}


def repair_stage(request, fixture):
    from publication_adapter import prepare, check_capture_head
    plan, stage = request['plan'], request['stage']
    head, number = request['headSha'], request['number']
    if stage == 'repair-assignment':
        current_head(plan, head, request['pullNumber'])
        findings = []
        for review_ in request['reviews']:
            result = review_['report']['result']
            if result['verdict'] == 'fail':
                findings.extend({'axis': result['axis'], 'headSha': head, **f} for f in result['findings'])
        if not findings: raise Blocked('no-actionable-review-findings')
        return {'state': 'repair-assigned', 'assignment': {
            'runId': request['runId'], 'number': number, 'headSha': head,
            'writerSessionId': request['writerSessionId'], 'localPath': plan['localPath'],
            'branch': plan['branch'], 'policy': repair_policy(number, plan['localPath']),
            'findings': findings, 'verification': request['verification'],
            'priorAttempts': request['priorAttempts'],
            'input': review_input(plan, head, request['intent'], fixture),
            'decisionBoundary': 'Repair small reversible implementation details within the accepted requirements. '
                'If product behavior, security, data lifecycle, scope or access requires a human decision, '
                'return intervention with a concrete question. Do not merge, push, deploy or release. '
                'Modify only this worktree; the control plane owns commits and publication.'}}
    if stage == 'repair-head':
        assignment = request['assignment']
        # The persisted adapter operation reconciles an already applied write; a
        # clean-head check here would incorrectly reject that legitimate replay.
        try:
            receipt = adapter_request(plan, 'qualification-repairs', request['operationKey'], assignment)
        except Exception:
            return {'state': 'repair-uncertain', 'blocker': 'repair-adapter-operation-uncertain'}
        if (receipt.get('contractVersion') != 'HeadQualificationAdapter/v1' or
                receipt.get('operationKey') != request['operationKey'] or
                receipt.get('sessionId') != assignment['writerSessionId'] or
                receipt.get('policy') != assignment['policy']):
            raise Blocked('invalid-repair-receipt')
        result = receipt.get('result', {})
        if (set(result) != {'schemaVersion', 'outcome', 'summary'} or
                result['schemaVersion'] != 'wpcp-repair/v1' or
                result['outcome'] not in ('completed', 'intervention') or
                not isinstance(result['summary'], str) or not result['summary'].strip()):
            raise Blocked('invalid-repair-result')
        return {'state': 'repair-' + result['outcome'], **receipt}
    if stage == 'prepare-repair':
        prepared = prepare(plan, request['correlation'], fixture)
        if prepared['headSha'] == head: raise Blocked('repair-did-not-create-new-head')
        git(plan, 'merge-base', '--is-ancestor', head, prepared['headSha'])
        return prepared
    if stage == 'publish-repair':
        intent = request['intent']
        new_head = intent['headSha']
        check_capture_head(plan, new_head)
        provider = Provider(plan)
        provider.check_repository()
        pull = provider.request('/pulls/' + str(request['pullNumber']))
        if (pull['draft'] is not True or pull['state'] != 'open' or
                pull['head']['sha'] not in (head, new_head) or pull['head']['ref'] != plan['branch'] or
                pull['base']['ref'] != plan['baseBranch'] or
                any(pull[side]['repo']['id'] != plan['repository']['providerRepositoryId'] for side in ('head', 'base')) or
                pull['body'] not in (request['previousIntent']['body'], intent['body'])):
            raise Blocked('repair-publication-conflict')
        remote = git(plan, 'ls-remote', '--exit-code', plan['remoteName'], 'refs/heads/' + plan['branch']).split()[0]
        if remote not in (head, new_head): raise Blocked('repair-remote-head-conflict')
        if remote == head:
            git(plan, 'merge-base', '--is-ancestor', head, new_head)
            git(plan, 'push', '--porcelain', '--force-with-lease=refs/heads/' + plan['branch'] + ':' + head,
                plan['remoteName'], new_head + ':refs/heads/' + plan['branch'])
        if provider.head(plan['branch']) != new_head: raise Blocked('repair-provider-head-conflict')
        if pull['body'] != intent['body']:
            provider.request('/pulls/' + str(request['pullNumber']), {'body': intent['body']}, method='PATCH')
        current_head(plan, new_head, request['pullNumber'])
        pull = provider.request('/pulls/' + str(request['pullNumber']))
        if pull['body'] != intent['body']: raise Blocked('repair-provider-body-conflict')
        return {'state': 'draft-updated', 'pullRequest': pull}
    raise Blocked('unknown-qualification-stage')
