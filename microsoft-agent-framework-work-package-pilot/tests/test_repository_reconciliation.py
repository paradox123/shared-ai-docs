"""Ticket 05 proof exclusively through process, Operator and external Git/HTTP seams."""
import json
import os
from pathlib import Path
import signal
import subprocess
import time
import unittest
from tests import test_control_plane_black_box as harness


class RepositoryReconciliationTests(harness.ControlPlaneProcessHarness, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.local = Path(cls.scratch.name) / 'local'
        cls.remote = Path(cls.scratch.name) / 'provider.git'
        cls.git('init', '--bare', str(cls.remote))
        cls.git('init', '-b', 'main', str(cls.local))
        cls.git('-C', str(cls.local), 'config', 'user.name', 'Controlled Test')
        cls.git('-C', str(cls.local), 'config', 'user.email', 'test@example.invalid')
        cls.git('-C', str(cls.local), 'commit', '--allow-empty', '-m', 'initial')
        cls.git('-C', str(cls.local), 'remote', 'add', 'origin', str(cls.remote))
        cls.git('-C', str(cls.local), 'push', 'origin', 'main')
        cls.initial = cls.git('-C', str(cls.local), 'rev-parse', 'main')
        cls.effect_port = cls.start_external('repository_provider_fixture.py', '--repository', str(cls.remote))
        cls.agent_port = cls.start_external('fake_codex_provider.py')
        cls.plan_path = Path(cls.scratch.name) / 'plan.json'
        cls.plan = {'repository': {'repositoryId': 'repo-1', 'fullName': 'pilot/fixture', 'providerRepositoryId': 9001},
            'localPath': str(cls.local), 'remoteName': 'origin', 'baseBranch': 'main',
            'providerOrigin': f'http://127.0.0.1:{cls.effect_port}',
            'agentOrigin': f'http://127.0.0.1:{cls.agent_port}', 'expectedBaseSha': cls.initial,
            'predecessorIssueNumber': None}
        cls.plan_path.write_text(json.dumps(cls.plan))

    @staticmethod
    def git(*arguments):
        result = harness.command_output(['git', *arguments])
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        return result.stdout.strip()

    @classmethod
    def start_external(cls, script, *extra):
        port = harness.free_port()
        process = subprocess.Popen(['python3', str(harness.PILOT_ROOT / 'tests' / script),
            '--port', str(port), '--database', str(Path(cls.scratch.name) / f'{port}.sqlite'), *extra],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        cls.addClassCleanup(cls.stop_process, process)
        for _ in range(100):
            status, _, _ = cls.request('GET', '/diagnostics', port=port)
            if status == 200:
                return port
            time.sleep(.05)
        raise AssertionError('controlled provider not ready')

    def setUp(self):
        self.proof_states = []
        self.proof_workers = []
        head = self.git('--git-dir', str(self.remote), 'rev-parse', 'main')
        self.git('-C', str(self.local), 'reset', '--hard', head)
        self.plan_path.write_text(json.dumps(dict(self.plan, expectedBaseSha=head)))

    def paused_worker(self, run_id, hook):
        log = Path(self.scratch.name) / f'{run_id}-{hook}.log'
        output = log.open('w')
        self.addCleanup(output.close)
        process = subprocess.Popen(self.worker_args(run_id, '--pause-at', hook), stdout=output,
            stderr=output, start_new_session=True)
        self.addCleanup(self.stop_process, process)
        for _ in range(200):
            if hook in log.read_text():
                self.proof_workers.append((run_id, hook, process))
                return process
            if process.poll() is not None:
                self.fail('worker exited before crash boundary: ' + log.read_text() + json.dumps(self.read_run(run_id)))
            time.sleep(.05)
        self.fail('worker did not reach crash boundary: ' + log.read_text())

    def test_git_success_gap_adopts_the_existing_ref_once(self):
        run_id = self.new_run()
        worker = self.paused_worker(run_id, 'after-git-effect')
        before = self.read_run(run_id)['repositoryExecution']
        operation = before['effects'][0]
        self.assertEqual('pending', operation['state'])
        ref = f'refs/heads/wpcp/{run_id}'
        target = self.git('-C', str(self.local), 'rev-parse', ref)
        os.killpg(worker.pid, signal.SIGKILL)
        worker.wait(timeout=10)
        after = self.deliver(run_id)['repositoryExecution']
        effect = after['effects'][0]
        self.assertEqual(operation['operationId'], effect['operationId'])
        self.assertEqual('adopted', effect['state'])
        self.assertEqual(target, effect['receipt']['headSha'])
        entries = self.git('-C', str(self.local), 'reflog', 'show', '--format=%gs', ref).splitlines()
        self.assertEqual([operation['operationId']], entries)

    def test_provider_success_gap_adopts_one_independent_receipt(self):
        run_id = self.new_run()
        worker = self.paused_worker(run_id, 'after-provider-effect')
        before = self.read_run(run_id)['repositoryExecution']
        effect = next(e for e in before['effects'] if e['kind'] == 'provider')
        self.assertEqual('pending', effect['state'])
        _, external, _ = self.request('GET', '/diagnostics', port=self.effect_port)
        receipt = next(e for e in external['effects'] if e['operationId'] == effect['operationId'])
        os.killpg(worker.pid, signal.SIGKILL)
        worker.wait(timeout=10)
        after = self.deliver(run_id)['repositoryExecution']
        adopted = next(e for e in after['effects'] if e['kind'] == 'provider')
        self.assertEqual('adopted', adopted['state'])
        self.assertEqual(receipt, adopted['receipt'])
        _, external, _ = self.request('GET', '/diagnostics', port=self.effect_port)
        self.assertEqual(1, sum(e['operationId'] == effect['operationId'] for e in external['effects']))

    def test_session_success_gap_and_concurrent_replacement_keep_one_session(self):
        from concurrent.futures import ThreadPoolExecutor
        run_id = self.new_run()
        worker = self.paused_worker(run_id, 'after-session-start')
        before = self.read_run(run_id)
        attempt = next(a for a in before['attempts'] if a.get('session'))
        _, external, _ = self.request('GET', '/diagnostics', port=self.agent_port)
        session = next(s for s in external['sessions'] if s['operationKey'] == attempt['attemptId'])
        os.killpg(worker.pid, signal.SIGKILL)
        worker.wait(timeout=10)
        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(lambda _: self.deliver(run_id), range(2)))
        after = self.read_run(run_id)
        selected = next(a for a in after['attempts'] if a.get('session'))
        self.assertEqual(attempt['attemptId'], selected['attemptId'])
        self.assertEqual(session['sessionId'], selected['session']['sessionId'])
        effect = next(e for e in after['repositoryExecution']['effects'] if e['kind'] == 'session')
        self.assertEqual(attempt['attemptId'], effect['operationId'])
        self.assertEqual(session['sessionId'], effect['receipt']['receiptId'])
        self.assertEqual('blocked', after['state'])
        _, external, _ = self.request('GET', '/diagnostics', port=self.agent_port)
        self.assertEqual(1, sum(s['operationKey'] == attempt['attemptId'] for s in external['sessions']))
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        self.assertEqual(1, sum(e['eventType'] == 'AgentResultObserved' for e in history['events']))

    def test_repository_owner_survives_crash_and_terminal_releases_successor(self):
        first = self.new_run()
        worker = self.paused_worker(first, 'after-git-effect')
        os.killpg(worker.pid, signal.SIGKILL)
        worker.wait(timeout=10)
        successor = self.new_run()
        blocked = self.deliver(successor)
        self.assertEqual('repository-busy', blocked['repositoryExecution']['blocker'])
        self.assertEqual(first, blocked['repositoryExecution']['ownerRunId'])
        self.assertFalse(any(a.get('session') for a in blocked['attempts']))
        finished = self.deliver(first)
        self.assertFalse(finished['repositoryExecution']['active'])
        self.assertIsNone(finished['repositoryExecution']['ownerRunId'])
        self.assertEqual('blocked', self.deliver(successor)['state'])
        replay = self.deliver(first)
        self.assertEqual(finished['lastPosition'], replay['lastPosition'])

    def control_args(self, run_id):
        control = self.read_run(run_id)['control']
        return ['--run-id', run_id, '--target-attempt-id', control['targetAttemptId'],
            '--expected-run-version', str(control['runVersion']), '--expected-head-sha', control['headSha'] or 'null',
            '--lease-epoch', str(control['leaseEpoch'])]

    def decide(self, action, run_id, *extra):
        code, result, _ = self.operator_cli(action, *self.control_args(run_id), *extra)
        self.assertEqual(0, code, result)
        return result

    def test_operator_reconcile_adopt_retry_survive_api_restart(self):
        run_id = self.new_run()
        worker = self.paused_worker(run_id, 'after-git-effect')
        os.killpg(worker.pid, signal.SIGKILL)
        worker.wait(timeout=10)
        self.decide('claim', run_id)
        self.decide('reconcile', run_id)
        before = self.read_run(run_id)['repositoryExecution']
        self.assertEqual('reconcile', before['requestedAction'])
        cls = type(self)
        cls.stop_process(cls.api)
        cls.start_api(excluded_ports={cls.api_port})
        reconciled = self.deliver(run_id)['repositoryExecution']
        self.assertEqual('adoptable', reconciled['state'])
        self.assertEqual(1, len(reconciled['effects']))
        effect = reconciled['effects'][0]
        self.decide('adopt', run_id, '--operation-id', effect['operationId'], '--receipt-id', effect['receipt']['receiptId'])
        adopted = self.deliver(run_id)['repositoryExecution']
        self.assertEqual('adopted', adopted['effects'][0]['state'])
        self.assertEqual(1, len(adopted['effects']))
        self.decide('retry', run_id)
        finished = self.deliver(run_id)
        self.assertEqual('blocked', finished['state'])
        self.assertFalse(finished['repositoryExecution']['active'])
        self.assertEqual(effect['operationId'], finished['repositoryExecution']['effects'][0]['operationId'])

    def test_retire_settles_existing_effects_releases_owner_and_fences_late_worker(self):
        run_id = self.new_run()
        worker = self.paused_worker(run_id, 'after-session-start')
        os.killpg(worker.pid, signal.SIGKILL)
        worker.wait(timeout=10)
        self.decide('claim', run_id)
        self.decide('retire', run_id)
        retired = self.deliver(run_id)
        self.assertEqual('retired', retired['state'])
        execution = retired['repositoryExecution']
        self.assertTrue(execution['terminal'])
        self.assertFalse(execution['active'])
        self.assertIsNone(execution['ownerRunId'])
        self.assertIsNone(retired['control']['holder'])
        self.assertFalse(any(a['state'] == 'running' for a in retired['activities']))
        self.assertFalse(any(a['state'] == 'running' for a in retired['attempts']))
        successor = self.new_run()
        self.assertEqual('blocked', self.deliver(successor)['state'])
        replay = self.deliver(run_id)
        self.assertEqual(retired['lastPosition'], replay['lastPosition'])
        standalone = harness.command_output(['dotnet', str(harness.WORKER_DLL), '--connection-string', self.connection_string,
            '--fixture', str(self.fixture_path), '--run-id', run_id, '--worker-id', 'late-worker',
            '--fake-agent-origin', self.plan['agentOrigin']])
        self.assertEqual(2, standalone.returncode)
        self.assertEqual('repository-execution-required', json.loads(standalone.stdout)['code'])
        self.assertEqual('retired', self.read_run(run_id)['state'])

    def test_conflicting_git_effect_requires_specific_human_decision(self):
        run_id = self.new_run()
        worker = self.paused_worker(run_id, 'after-git-effect')
        os.killpg(worker.pid, signal.SIGKILL)
        worker.wait(timeout=10)
        effect = self.read_run(run_id)['repositoryExecution']['effects'][0]
        wrong = self.git('-C', str(self.local), 'commit-tree', 'HEAD^{tree}', '-p', 'HEAD', '-m', 'conflicting external effect')
        self.git('-C', str(self.local), 'update-ref', effect['target'], wrong)
        conflict = self.deliver(run_id)['repositoryExecution']
        self.assertEqual('human-decision', conflict['state'])
        self.assertEqual('git-target-conflict', conflict['blocker'])
        self.assertEqual(effect['operationId'], conflict['humanDecision']['operationId'])
        self.assertEqual(wrong, conflict['humanDecision']['observedHeadSha'])
        self.assertTrue(conflict['active'])
        self.decide('claim', run_id)
        self.decide('retire', run_id)
        self.assertEqual('human-decision', self.deliver(run_id)['state'])
        # Repair only the external Git fixture, never the control-plane database.
        self.git('-C', str(self.local), 'update-ref', effect['target'], effect['headSha'])
        self.decide('reconcile', run_id)
        repaired = self.deliver(run_id)['repositoryExecution']['effects'][0]
        self.decide('adopt', run_id, '--operation-id', repaired['operationId'], '--receipt-id', repaired['receipt']['receiptId'])
        self.deliver(run_id)
        self.decide('retire', run_id)
        self.assertEqual('retired', self.deliver(run_id)['state'])

    def test_recovery_commands_require_holder_fresh_fences_and_stopped_delivery(self):
        run_id = self.new_run()
        worker = self.paused_worker(run_id, 'after-git-effect')
        self.decide('claim', run_id)
        code, result, _ = self.operator_cli('retry', *self.control_args(run_id))
        self.assertEqual(1, code)
        self.assertEqual('worker-delivery-active', result['code'])
        os.killpg(worker.pid, signal.SIGKILL)
        worker.wait(timeout=10)
        original = self.read_run(run_id)
        fence = original['control']
        payload = {'targetAttemptId': fence['targetAttemptId'], 'expectedRunVersion': fence['runVersion'],
            'expectedHeadSha': fence['headSha'], 'leaseEpoch': fence['leaseEpoch']}
        import uuid
        for action in ('retry', 'reconcile', 'adopt', 'retire'):
            for actor in ('actor-observer', 'actor-contributor', 'actor-unauthorized', 'worker-bot'):
                status, rejected, _ = self.request('POST', f'/api/v1/runs/{run_id}/control/{action}', payload, actor_id=actor)
                self.assertIn(status, (403, 409), rejected)
            for field, value in [('targetAttemptId', str(uuid.uuid4())), ('expectedRunVersion', fence['runVersion'] - 1),
                ('expectedHeadSha', '0' * 40), ('leaseEpoch', fence['leaseEpoch'] - 1)]:
                status, rejected, _ = self.request('POST', f'/api/v1/runs/{run_id}/control/{action}', dict(payload, **{field: value}))
                self.assertEqual(409, status, rejected)
        for action in ('retry', 'reconcile', 'retire'):
            status, rejected, _ = self.request('POST', f'/api/v1/runs/{run_id}/control/{action}',
                dict(payload, operationId='wpcp-controlled-secret-canary-v1', receiptId='unrelated-input'))
            self.assertEqual(409, status, rejected)
        self.assertEqual(original['lastPosition'], self.read_run(run_id)['lastPosition'])
        code, accepted, _ = self.operator_cli('retire', *self.control_args(run_id))
        self.assertEqual(0, code, accepted)
        status, repeated, _ = self.request('POST', f'/api/v1/runs/{run_id}/control/retire', payload)
        self.assertEqual(409, status, repeated)
        self.assertEqual('retired', self.deliver(run_id)['state'])

    def test_missing_committed_receipt_is_not_recreated_by_replacement(self):
        run_id = self.new_run()
        worker = self.paused_worker(run_id, 'after-provider-effect')
        os.killpg(worker.pid, signal.SIGKILL)
        worker.wait(timeout=10)
        effect = self.read_run(run_id)['repositoryExecution']['effects'][0]
        self.git('-C', str(self.local), 'update-ref', '-d', effect['target'])
        result = self.deliver(run_id)['repositoryExecution']
        self.assertEqual('human-decision', result['state'])
        self.assertEqual('git-receipt-missing', result['blocker'])
        self.assertEqual('', self.git('-C', str(self.local), 'for-each-ref', '--format=%(refname)', effect['target']))
        self.git('-C', str(self.local), 'update-ref', '--create-reflog', '-m', effect['operationId'], effect['target'], effect['headSha'])
        self.decide('claim', run_id)
        self.decide('retire', run_id)
        self.assertEqual('retired', self.deliver(run_id)['state'])

    def test_ambiguous_provider_receipts_and_changed_adopt_selection_fail_closed(self):
        run_id = self.new_run()
        worker = self.paused_worker(run_id, 'after-provider-effect')
        os.killpg(worker.pid, signal.SIGKILL)
        worker.wait(timeout=10)
        effect = next(e for e in self.read_run(run_id)['repositoryExecution']['effects'] if e['kind'] == 'provider')
        fault_path = '/faults/' + effect['operationId']
        self.request('PUT', fault_path, {'mode': 'ambiguous'}, port=self.effect_port)
        conflict = self.deliver(run_id)['repositoryExecution']
        self.assertEqual('provider-receipt-ambiguous', conflict['blocker'])
        self.assertEqual(effect['operationId'], conflict['humanDecision']['operationId'])
        self.assertEqual(2, len(conflict['humanDecision']['candidates']))
        _, _, history = self.request('GET', f'/api/v1/runs/{run_id}/events')
        self.assertNotIn('wpcp-controlled-secret-canary-v1', history + json.dumps(conflict))
        self.assertIn('[REDACTED:CONTROLLED-CANARY]', history)
        self.decide('claim', run_id)
        self.request('PUT', fault_path, {'mode': 'none'}, port=self.effect_port)
        self.decide('reconcile', run_id)
        reconciled = self.deliver(run_id)['repositoryExecution']
        selected = next(e for e in reconciled['effects'] if e['kind'] == 'provider')
        self.decide('adopt', run_id, '--operation-id', selected['operationId'], '--receipt-id', selected['receipt']['receiptId'])
        self.request('PUT', fault_path, {'mode': 'conflict'}, port=self.effect_port)
        changed = self.deliver(run_id)['repositoryExecution']
        self.assertEqual('provider-receipt-conflict', changed['blocker'])
        self.request('PUT', fault_path, {'mode': 'none'}, port=self.effect_port)
        self.decide('retire', run_id)
        retired = self.deliver(run_id)
        self.assertEqual('retired', retired['state'])
        self.assertIsNone(retired['repositoryExecution']['humanDecision'])
        _, external, _ = self.request('GET', '/diagnostics', port=self.effect_port)
        self.assertEqual(1, sum(e['operationId'] == effect['operationId'] for e in external['effects']))

    def test_expected_base_retry_and_predecessor_checks_use_provider_evidence(self):
        run_id = self.new_run()
        self.plan_path.write_text(json.dumps(dict(self.plan, expectedBaseSha='0' * 40)))
        before = self.deliver(run_id)
        self.assertEqual('expected-base-stale', before['repositoryExecution']['blocker'])
        self.assertFalse(before['repositoryExecution']['effects'])
        self.decide('claim', run_id)
        self.decide('retry', run_id)
        after = self.deliver(run_id)
        base = after['repositoryExecution']['base']
        self.assertEqual(base['providerSha'], base['expectedSha'])
        self.assertEqual('blocked', after['state'])
        predecessor = self.new_run()
        head = self.git('--git-dir', str(self.remote), 'rev-parse', 'main')
        self.plan_path.write_text(json.dumps(dict(self.plan, expectedBaseSha=head, predecessorIssueNumber=999)))
        blocked = self.deliver(predecessor)
        self.assertEqual('predecessor-not-completed', blocked['repositoryExecution']['blocker'])
        self.assertFalse(any(a.get('session') for a in blocked['attempts']))
        self.decide('claim', predecessor)
        self.decide('retire', predecessor)
        self.assertEqual('retired', self.deliver(predecessor)['state'])

    def test_reconcile_crash_reuses_committed_observation_without_duplicate_history(self):
        run_id = self.new_run()
        worker = self.paused_worker(run_id, 'after-git-effect')
        os.killpg(worker.pid, signal.SIGKILL)
        worker.wait(timeout=10)
        self.decide('claim', run_id)
        self.decide('reconcile', run_id)
        recovery = self.paused_worker(run_id, 'after-reconciled-effect')
        os.killpg(recovery.pid, signal.SIGKILL)
        recovery.wait(timeout=10)
        self.assertEqual('reconcile', self.read_run(run_id)['repositoryExecution']['requestedAction'])
        self.deliver(run_id)
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        observations = [e for e in history['events'] if e['eventType'] == 'RepositoryEffectObserved']
        self.assertEqual(1, len(observations))
        self.decide('retire', run_id)
        self.assertEqual('retired', self.deliver(run_id)['state'])

    def test_completed_effect_receipts_stay_immutable_after_finalization_crash(self):
        run_id = self.new_run()
        worker = self.paused_worker(run_id, 'after-session-receipt')
        before = self.read_run(run_id)['repositoryExecution']['effects']
        os.killpg(worker.pid, signal.SIGKILL)
        worker.wait(timeout=10)
        after = self.deliver(run_id)['repositoryExecution']['effects']
        self.assertEqual(before, after)
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        self.assertEqual(3, sum(e['eventType'] == 'RepositoryEffectObserved' for e in history['events']))

    def test_settled_recovery_releases_repository_after_provider_head_advances(self):
        run_id = self.new_run()
        worker = self.paused_worker(run_id, 'after-session-receipt')
        before = self.read_run(run_id)['repositoryExecution']['effects']
        os.killpg(worker.pid, signal.SIGKILL)
        worker.wait(timeout=10)
        self.git('-C', str(self.local), 'commit', '--allow-empty', '-m', 'independent provider advancement')
        self.git('-C', str(self.local), 'push', 'origin', 'main')
        after = self.deliver(run_id)['repositoryExecution']
        self.assertTrue(after['terminal'])
        self.assertFalse(after['active'])
        self.assertEqual(before, after['effects'])

    def read_run(self, run_id, actor="actor-authorized"):
        run = super().read_run(run_id, actor)
        execution = run.get('repositoryExecution')
        if execution is not None and not any(s['runId'] == run_id and s['position'] == run['lastPosition'] for s in self.proof_states):
            self.proof_states.append({'runId': run_id, 'position': run['lastPosition'], 'state': run['state'],
                'execution': {key: value for key, value in execution.items() if key != 'plan'}})
        return run

    def tearDown(self):
        destination = os.environ.get('WPCP_PROOF_DIR')
        if not destination:
            return
        operations = {effect['operationId'] for state in self.proof_states for effect in state['execution'].get('effects') or []}
        _, provider, _ = self.request('GET', '/diagnostics', port=self.effect_port)
        _, agent, _ = self.request('GET', '/diagnostics', port=self.agent_port)
        histories = {}
        for run_id in dict.fromkeys(state['runId'] for state in self.proof_states):
            _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
            histories[run_id] = [{'position': event['position'], 'eventId': event['eventId'], 'type': event['eventType'],
                'payload': {key: value for key, value in event['payload'].items() if key != 'plan'}} for event in history['events']]
        git_counts = {}
        for state in self.proof_states:
            for effect in state['execution'].get('effects') or []:
                if effect['kind'] == 'git' and effect['operationId'] not in git_counts:
                    entries = self.git('-C', str(self.local), 'reflog', 'show', '--format=%gs', effect['target']).splitlines()
                    git_counts[effect['operationId']] = entries.count(effect['operationId'])
        proof = {'test': self._testMethodName, 'crashes': [{'runId': run_id, 'boundary': hook, 'workerExitCode': process.poll()}
            for run_id, hook, process in self.proof_workers], 'observedStates': self.proof_states,
            'externalGitOperationCounts': git_counts,
            'externalProviderReceipts': [e for e in provider['effects'] if e['operationId'] in operations],
            'externalSessionReceipts': [e for e in agent['sessions'] if e['operationKey'] in operations],
            'canonicalHistory': histories}
        output = Path(destination)
        output.mkdir(parents=True, exist_ok=True)
        (output / (self._testMethodName + '.json')).write_text(json.dumps(proof, indent=2) + '\n')

    def worker_args(self, run_id, *extra):
        return ['dotnet', str(harness.WORKER_DLL), '--connection-string', self.connection_string,
            '--fixture', str(self.fixture_path), '--run-id', run_id, '--worker-id', 'repository-worker',
            '--repository-plan', str(self.plan_path), *extra]

    def deliver(self, run_id, *extra):
        result = harness.command_output(self.worker_args(run_id, *extra), timeout=30)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return self.read_run(run_id)

    def test_stale_local_base_blocks_before_any_agent_start(self):
        run_id = self.new_run()
        _, before_sessions, _ = self.request('GET', '/diagnostics', port=self.agent_port)
        self.git('-C', str(self.local), 'commit', '--allow-empty', '-m', 'predecessor merged')
        current = self.git('-C', str(self.local), 'rev-parse', 'main')
        self.git('-C', str(self.local), 'push', 'origin', 'main')
        self.git('-C', str(self.local), 'reset', '--hard', self.initial)
        self.request('PUT', '/completed/42', {}, port=self.effect_port)
        self.plan_path.write_text(json.dumps(dict(self.plan, expectedBaseSha=current, predecessorIssueNumber=42)))
        run = self.deliver(run_id)
        self.assertEqual('preflight-blocked', run['state'])
        execution = run['repositoryExecution']
        self.assertEqual('local-base-stale', execution['blocker'])
        self.assertEqual(current, execution['base']['expectedSha'])
        self.assertEqual(current, execution['base']['providerSha'])
        self.assertEqual(self.initial, execution['base']['localSha'])
        self.assertFalse(any(a.get('session') for a in run['attempts']))
        _, external, _ = self.request('GET', '/diagnostics', port=self.agent_port)
        self.assertEqual(before_sessions['sessionCount'], external['sessionCount'])
        self.git('-C', str(self.local), 'fetch', 'origin')
        self.git('-C', str(self.local), 'reset', '--hard', 'origin/main')
        after = self.deliver(run_id)
        self.assertEqual('blocked', after['state'])
        self.assertEqual(current, after['repositoryExecution']['base']['localSha'])
        self.assertEqual(current, after['repositoryExecution']['base']['expectedSha'])
        self.assertTrue(any(a.get('session') for a in after['attempts']))


class RepositoryRegistrationTests(harness.ControlPlaneProcessHarness, unittest.TestCase):
    def test_existing_standalone_session_cannot_gain_later_base_provenance(self):
        run_id = self.new_run()
        port = RepositoryReconciliationTests.start_external.__func__(type(self), 'fake_codex_provider.py')
        result = harness.command_output(['dotnet', str(harness.WORKER_DLL), '--connection-string', self.connection_string,
            '--fixture', str(self.fixture_path), '--run-id', run_id, '--worker-id', 'legacy-worker',
            '--fake-agent-origin', f'http://127.0.0.1:{port}'])
        self.assertEqual(0, result.returncode, result.stdout)
        original = self.read_run(run_id)
        local = Path(self.scratch.name) / 'legacy'
        RepositoryReconciliationTests.git('init', '-b', 'main', str(local))
        plan_path = Path(self.scratch.name) / 'legacy-plan.json'
        plan_path.write_text(json.dumps({'repository': original['correlation']['repository'],
            'localPath': str(local), 'remoteName': 'origin', 'baseBranch': 'main',
            'providerOrigin': f'http://127.0.0.1:{port}', 'agentOrigin': f'http://127.0.0.1:{port}',
            'expectedBaseSha': '1' * 40}))
        promoted = harness.command_output(['dotnet', str(harness.WORKER_DLL), '--connection-string', self.connection_string,
            '--fixture', str(self.fixture_path), '--run-id', run_id, '--worker-id', 'managed-worker',
            '--repository-plan', str(plan_path)])
        self.assertEqual(2, promoted.returncode, promoted.stdout)
        self.assertEqual('agent-assignment-conflict', json.loads(promoted.stdout)['code'])
        after = self.read_run(run_id)
        self.assertIsNone(after['repositoryExecution'])
        self.assertEqual(original['attempts'], after['attempts'])
        self.assertEqual(original['lastPosition'], after['lastPosition'])

    def test_registration_cannot_overlap_an_active_standalone_delivery(self):
        legacy_run, managed_run = self.new_run(), self.new_run()
        port = RepositoryReconciliationTests.start_external.__func__(type(self), 'fake_codex_provider.py')
        log = Path(self.scratch.name) / 'legacy-active.log'
        output = log.open('w')
        self.addCleanup(output.close)
        legacy = subprocess.Popen(['dotnet', str(harness.WORKER_DLL), '--connection-string', self.connection_string,
            '--fixture', str(self.fixture_path), '--run-id', legacy_run, '--worker-id', 'legacy-worker',
            '--fake-agent-origin', f'http://127.0.0.1:{port}', '--pause-at', 'after-session-start'],
            stdout=output, stderr=output, start_new_session=True)
        self.addCleanup(self.stop_process, legacy)
        for _ in range(200):
            if 'after-session-start' in log.read_text():
                break
            time.sleep(.05)
        else:
            self.fail(log.read_text())
        local = Path(self.scratch.name) / 'registration'
        RepositoryReconciliationTests.git('init', '-b', 'main', str(local))
        plan = Path(self.scratch.name) / 'registration.json'
        plan.write_text(json.dumps({'repository': self.read_run(managed_run)['correlation']['repository'],
            'localPath': str(local), 'remoteName': 'origin', 'baseBranch': 'main',
            'providerOrigin': f'http://127.0.0.1:{port}', 'agentOrigin': f'http://127.0.0.1:{port}',
            'expectedBaseSha': '1' * 40}))
        arguments = ['dotnet', str(harness.WORKER_DLL), '--connection-string', self.connection_string,
            '--fixture', str(self.fixture_path), '--run-id', managed_run, '--worker-id', 'managed-worker',
            '--repository-plan', str(plan)]
        racing = harness.command_output(arguments, timeout=20)
        self.assertEqual(2, racing.returncode, racing.stdout)
        self.assertEqual('repository-registration-busy', json.loads(racing.stdout)['code'])
        self.assertIsNone(self.read_run(managed_run)['repositoryExecution'])
        os.killpg(legacy.pid, signal.SIGKILL)
        legacy.wait(timeout=10)
        replacement = harness.command_output(arguments, timeout=20)
        self.assertEqual(0, replacement.returncode, replacement.stdout)
        self.assertIsNotNone(self.read_run(managed_run)['repositoryExecution'])


if __name__ == '__main__':
    unittest.main()
