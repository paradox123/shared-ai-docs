"""Ticket 08: public Operator contracts across independent hosts and providers."""
import json
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import unittest
import uuid
from tests import test_control_plane_black_box as harness
from tests import test_fake_codex_attempt as fake


class ControlTransferTests(harness.ControlPlaneProcessHarness, unittest.TestCase):
    def setUp(self):
        self.proof_runs = []
        self.proof_facts = {}

    def new_run(self):
        run_id = super().new_run()
        self.proof_runs.append(run_id)
        return run_id

    def tearDown(self):
        destination = os.environ.get('WPCP_TRANSFER_PROOF_DIR')
        if destination:
            directory = Path(destination)
            directory.mkdir(parents=True, exist_ok=True)
            observations = []
            for run_id in self.proof_runs:
                run = self.read_run(run_id, 'actor-observer')
                _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events', actor_id='actor-observer')
                observations.append(dict(run=run, history=history))
            text = json.dumps(dict(observations=observations, facts=self.proof_facts), indent=2) + '\n'
            for token in self.provider.tokens.values():
                self.assertNotIn(token, text)
            (directory / (self._testMethodName + '.json')).write_text(text)


    @staticmethod
    def fences(control):
        return dict(targetAttemptId=control['targetAttemptId'], expectedRunVersion=control['runVersion'],
                    expectedHeadSha=control['headSha'], leaseEpoch=control['leaseEpoch'])

    def action(self, run_id, action, actor='actor-authorized', control=None, **extra):
        control = control or self.read_run(run_id)['control']
        return self.request('POST', f'/api/v1/runs/{run_id}/control/{action}',
                            dict(self.fences(control), **extra), actor_id=actor)

    def claimed_run(self):
        run_id = self.new_run()
        status, decision, _ = self.action(run_id, 'claim')
        self.assertEqual(200, status, decision)
        return run_id

    def test_request_survives_restart_and_only_holder_can_reject(self):
        run_id = self.claimed_run()
        before = self.read_run(run_id)['control']
        request_id = str(uuid.uuid4())
        status, decision, _ = self.action(run_id, 'request-transfer', 'actor-contributor',
            requestId=request_id, reason='I can continue the work')
        self.assertEqual(200, status, decision)
        current = decision['current']
        self.assertEqual(before['holder'], current['holder'])
        self.assertEqual(before['leaseEpoch'], current['leaseEpoch'])
        self.assertEqual(request_id, current['transferRequest']['requestId'])
        self.assertEqual('103', current['transferRequest']['requester']['subjectId'])
        for action in ('release', 'reject-transfer'):
            status, denied, _ = self.action(run_id, action, 'actor-contributor',
                requestId=request_id, reason='Not the holder')
            self.assertEqual(409, status, denied)
        cls = type(self)
        cls.stop_process(cls.api)
        cls.start_api(excluded_ports={cls.api_port})
        self.assertEqual(current, self.read_run(run_id, 'actor-contributor')['control'])
        status, rejected, _ = self.action(run_id, 'reject-transfer', requestId=request_id, reason='Still working')
        self.assertEqual(200, status, rejected)
        self.assertEqual('rejected', rejected['current']['transferRequest']['state'])
        self.assertEqual(before['holder'], rejected['current']['holder'])
        self.assertEqual(before['leaseEpoch'], rejected['current']['leaseEpoch'])
        status, stale, _ = self.action(run_id, 'reject-transfer', requestId=request_id, reason='Duplicate')
        self.assertEqual(409, status, stale)
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        self.assertEqual(['ImplementationRunStarted', 'ControlLeaseClaimed', 'ControlTransferRequested',
                          'ControlTransferRejected'], [e['eventType'] for e in history['events']])

    def test_approval_moves_lease_once_and_revalidates_recipient(self):
        run_id = self.claimed_run()
        request_id = str(uuid.uuid4())
        status, requested, _ = self.action(run_id, 'request-transfer', 'actor-contributor',
            requestId=request_id, reason='handover')
        self.assertEqual(200, status, requested)
        status, denied, _ = self.action(run_id, 'approve-transfer', 'actor-contributor',
            requestId=request_id, reason='self approval')
        self.assertEqual(409, status, denied)
        current = self.read_run(run_id)['control']
        self.provider.identities['actor-contributor']['push'] = False
        try:
            status, denied, _ = self.action(run_id, 'approve-transfer', requestId=request_id, reason='approve')
            self.assertEqual(409, status, denied)
            self.assertEqual('transfer-recipient-not-contributor', denied['code'])
            self.assertEqual(current, self.read_run(run_id)['control'])
        finally:
            self.provider.identities['actor-contributor']['push'] = True
        code, approved, raw = self.operator_cli('approve-transfer', '--run-id', run_id,
            *fake.FakeCodexTests.fence(self, {'control': current}), '--request-id', request_id,
            '--reason', 'Planning handover')
        self.assertEqual(0, code, raw)
        self.assertEqual('103', approved['current']['holder']['subjectId'])
        self.assertEqual(current['leaseEpoch'] + 1, approved['current']['leaseEpoch'])
        self.assertEqual('approved', approved['current']['transferRequest']['state'])
        status, duplicate, _ = self.action(run_id, 'approve-transfer', control=current,
            requestId=request_id, reason='Planning handover')
        self.assertEqual(409, status, duplicate)
        observed = self.read_run(run_id, 'actor-authorized')
        self.assertFalse(observed['authorization']['canRelease'])
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        changes = [e for e in history['events'] if e['eventType'] == 'ControlLeaseTransferred']
        self.assertEqual(1, len(changes))
        self.assertEqual('voluntary', changes[0]['payload']['detail']['mode'])
        self.assertEqual('Planning handover', changes[0]['payload']['detail']['reason'])

    def test_twenty_takeovers_across_two_api_hosts_have_one_winner_per_epoch(self):
        run_id = self.claimed_run()
        cls = type(self)
        first_api, first_port = cls.api, cls.api_port
        cls.start_api(excluded_ports={first_port})
        self.addCleanup(cls.stop_process, first_api)
        for number in range(40):
            actor = f'contributor-{number}'
            self.provider.identities[actor] = dict(id=200 + number, type='User', read=True, push=True)
            self.provider.tokens[actor] = uuid.uuid4().hex
        for epoch_round in range(2):
            before = self.read_run(run_id)['control']
            body = dict(self.fences(before), reason='Explicit forced takeover')
            with ThreadPoolExecutor(max_workers=20) as pool:
                jobs = [pool.submit(self.request, 'POST', f'/api/v1/runs/{run_id}/control/force-takeover',
                    body, f'contributor-{number + epoch_round * 20}', port=first_port if number % 2 else cls.api_port)
                    for number in range(20)]
                results = [job.result() for job in jobs]
            outcomes = [r[0] for r in results]
            self.proof_facts[f'epochRound{epoch_round}'] = outcomes
            self.assertEqual([200] + [409] * 19, sorted(outcomes), [(r[0], r[1].get('code')) for r in results])
            current = self.read_run(run_id)['control']
            self.assertEqual(before['leaseEpoch'] + 1, current['leaseEpoch'])
            self.assertEqual(before['runVersion'] + 1, current['runVersion'])
            self.assertNotEqual(before['holder'], current['holder'])
            status, stale, _ = self.action(run_id, 'release', control=before)
            self.assertEqual(409, status, stale)
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        transfers = [e for e in history['events'] if e['eventType'] == 'ControlLeaseForcedTakenOver']
        self.assertEqual(2, len(transfers))
        for event in transfers:
            self.assertEqual('forced', event['payload']['detail']['mode'])
            self.assertTrue(event['occurredAt'])
            self.assertEqual(run_id, event['correlation']['runId'])

    start_fake = fake.FakeCodexTests.start_fake
    fake_worker_args = fake.FakeCodexTests.fake_worker_args
    run_fake = fake.FakeCodexTests.run_fake

    def opened_session(self, scenario='blocked'):
        run_id, port = self.new_run(), self.start_fake(scenario=scenario, open_mode='same-session')
        result = self.run_fake(run_id, port)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(200, self.action(run_id, 'claim')[0])
        attempt = next(a for a in self.read_run(run_id)['attempts'] if a.get('session'))
        request_id = attempt['session']['humanRequest']['requestId']
        code, opened, raw = self.operator_cli('open', '--run-id', run_id, '--attempt-id', attempt['attemptId'],
            '--request-id', request_id, '--command-id', str(uuid.uuid4()))
        self.assertEqual(0, code, raw)
        return run_id, port, attempt, request_id

    def test_takeover_fences_pending_opened_session_write_across_restart(self):
        run_id, port, attempt, request_id = self.opened_session('interaction-before-effect-failure')
        command_id = str(uuid.uuid4())
        before = self.read_run(run_id)
        status, unavailable, _ = self.action(run_id, 'write', requestId=request_id,
            commandId=command_id, message='delayed old writer')
        self.assertEqual(503, status, unavailable)
        status, changed, _ = self.action(run_id, 'force-takeover', 'actor-contributor', reason='Owner unavailable')
        self.assertEqual(200, status, changed)
        _, receipt, _ = self.request('GET', f'/api/v1/runs/{run_id}/continuations/{command_id}')
        self.assertEqual('fenced', receipt['operation']['state'])
        for actor in ('actor-authorized', 'same-human-other-client'):
            status, denied, _ = self.action(run_id, 'write', actor, requestId=request_id,
                commandId=str(uuid.uuid4()), message='old open window still writing')
            self.assertEqual(409, status, denied)
        cls = type(self)
        cls.stop_process(cls.api)
        cls.start_api(excluded_ports={cls.api_port})
        after = self.read_run(run_id, 'actor-authorized')
        self.assertEqual(before['state'], after['state'])
        self.assertEqual(before['attempts'], after['attempts'])
        self.assertEqual(before['control']['headSha'], after['control']['headSha'])
        _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(0, diagnostics['interactionCount'])
        self.assertEqual(1, diagnostics['sessionCount'])
        status, late, _ = self.request('POST',
            f"/sessions/{attempt['session']['sessionId']}/interactions/{receipt['operation']['operationKey']}",
            dict(message='delayed old writer'), port=port)
        self.assertEqual(409, status, late)
        self.assertEqual('operation-fenced', late['code'])

    def test_takeover_reconciles_accepted_write_before_preserving_it(self):
        run_id, port, attempt, request_id = self.opened_session('interaction-success-gap')
        command_id = str(uuid.uuid4())
        status, unavailable, _ = self.action(run_id, 'write', requestId=request_id,
            commandId=command_id, message='accepted before takeover')
        self.assertEqual(503, status, unavailable)
        _, external, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(1, external['interactionCount'])
        status, reconciled, _ = self.action(run_id, 'force-takeover', 'actor-contributor', reason='Finish handover')
        self.assertEqual(409, status, reconciled)
        self.assertEqual('control-effects-reconciled', reconciled['code'])
        _, receipt, _ = self.request('GET', f'/api/v1/runs/{run_id}/continuations/{command_id}')
        self.assertEqual('applied', receipt['operation']['state'])
        before = self.read_run(run_id)
        status, changed, _ = self.action(run_id, 'force-takeover', 'actor-contributor', reason='Finish handover')
        self.assertEqual(200, status, changed)
        after = self.read_run(run_id, 'actor-authorized')
        self.assertEqual(before['state'], after['state'])
        self.assertEqual(before['attempts'], after['attempts'])
        cls = type(self)
        cls.stop_process(cls.api)
        cls.start_api(excluded_ports={cls.api_port})
        _, external_after, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(external['interactions'], external_after['interactions'])
        self.assertEqual(1, external_after['interactionCount'])

    def test_takeover_invalidates_queue_but_preserves_running_operation(self):
        from tests.test_active_agent_control import ActiveAgentControlTests as live
        self.live_providers = {}
        run_id = self.new_run()
        port = live.start_fake(self)
        live.start_live(self, run_id, port, 'running')
        self.assertEqual(200, self.action(run_id, 'claim')[0])
        before = self.read_run(run_id)
        attempt = next(a for a in before['attempts'] if a.get('liveOperation'))
        operation = attempt['liveOperation']['currentOperation']
        control = before['control']
        status, queued, _ = self.request('POST', f'/api/v1/runs/{run_id}/agent-commands/queue',
            dict(self.fences(control), commandId=str(uuid.uuid4()), message='old holder queued work'))
        self.assertEqual(202, status, queued)
        status, changed, _ = self.action(run_id, 'force-takeover', 'actor-contributor', reason='New contributor')
        self.assertEqual(200, status, changed)
        after = next(a for a in self.read_run(run_id)['attempts'] if a.get('liveOperation'))
        self.assertEqual(operation, after['liveOperation']['currentOperation'])
        self.assertEqual(attempt['state'], after['state'])
        self.assertEqual(attempt['liveOperation']['sessionId'], after['liveOperation']['sessionId'])
        self.assertEqual('rejected', after['liveOperation']['commands'][0]['state'])
        self.assertEqual('control-lease-changed', after['liveOperation']['commands'][0]['rejectionReason'])
        live.complete(self, port, operation)
        live.deliver(self, run_id, port)
        _, external, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(1, external['operationCount'])

    def test_closed_transfer_request_identity_cannot_be_reused(self):
        run_id = self.claimed_run()
        original = str(uuid.uuid4())
        for request_id in (original, str(uuid.uuid4())):
            self.assertEqual(200, self.action(run_id, 'request-transfer', 'actor-contributor',
                requestId=request_id, reason='ask')[0])
            self.assertEqual(200, self.action(run_id, 'reject-transfer',
                requestId=request_id, reason='decline')[0])
        before = self.read_run(run_id)['control']
        status, replay, _ = self.action(run_id, 'request-transfer', 'actor-contributor',
            requestId=original, reason='reuse closed identity')
        self.assertEqual(409, status, replay)
        self.assertEqual(before, self.read_run(run_id)['control'])

    def test_release_expires_pending_request_and_new_holder_can_request_again(self):
        run_id = self.claimed_run()
        request_id = str(uuid.uuid4())
        self.assertEqual(200, self.action(run_id, 'request-transfer', 'actor-contributor',
            requestId=request_id, reason='ask')[0])
        self.assertEqual(200, self.action(run_id, 'release')[0])
        status, claimed, _ = self.action(run_id, 'claim', 'actor-contributor')
        self.assertEqual(200, status, claimed)
        self.assertFalse(self.read_run(run_id, 'actor-contributor')['authorization']['canDecideTransfer'])
        status, requested, _ = self.action(run_id, 'request-transfer',
            requestId=str(uuid.uuid4()), reason='ask new holder')
        self.assertEqual(200, status, requested)

    def test_transfer_permissions_fences_and_redacted_reason(self):
        run_id = self.claimed_run()
        current = self.read_run(run_id)['control']
        for action in ('request-transfer', 'force-takeover', 'approve-transfer', 'reject-transfer'):
            for actor in ('actor-observer', 'actor-unauthorized', 'worker-bot'):
                status, denied, _ = self.action(run_id, action, actor, requestId=str(uuid.uuid4()), reason='denied')
                self.assertEqual(403, status, denied)
                self.assertEqual(current if actor == 'actor-observer' else None, denied['current'])
        for field, value in [('targetAttemptId', str(uuid.uuid4())), ('expectedRunVersion', 1),
                             ('expectedHeadSha', 'a' * 40), ('leaseEpoch', 0)]:
            for missing in (False, True):
                body = dict(self.fences(current), reason='stale')
                if missing:
                    body.pop(field)
                else:
                    body[field] = value
                status, denied, _ = self.request('POST', f'/api/v1/runs/{run_id}/control/force-takeover',
                                                body, 'actor-contributor')
                self.assertEqual(400 if missing else 409, status, denied)
                self.assertEqual(current, denied['current'])
        status, denied, _ = self.action(run_id, 'force-takeover', 'actor-contributor')
        self.assertEqual(400, status, denied)
        policy = json.loads(harness.FIXTURE.read_text())['redactionPolicy']
        secret = policy['controlledCanaries'][0]['value']
        code, changed, raw = self.operator_cli('force-takeover', '--run-id', run_id,
            *fake.FakeCodexTests.fence(self, {'control': current}), '--reason', secret,
            '--actor-id', 'actor-contributor')
        self.assertEqual(0, code, raw)
        _, history, raw = self.request('GET', f'/api/v1/runs/{run_id}/events')
        self.assertNotIn(secret, raw)
        self.assertEqual(policy['marker'], history['events'][-1]['payload']['detail']['reason'])
        self.assertTrue(history['events'][-1]['redaction']['occurred'])
        self.assertTrue(self.read_run(run_id)['redaction']['occurred'])

    def test_voluntary_transfer_fences_old_window_and_new_holder_writes_same_session(self):
        run_id, port, attempt, request_id = self.opened_session()
        transfer = str(uuid.uuid4())
        code, requested, raw = self.operator_cli('request-transfer', '--run-id', run_id,
            *fake.FakeCodexTests.fence(self, self.read_run(run_id)), '--request-id', transfer,
            '--reason', 'take responsibility', '--actor-id', 'actor-contributor')
        self.assertEqual(0, code, raw)
        before = self.read_run(run_id)
        self.assertEqual(200, self.action(run_id, 'approve-transfer', requestId=transfer, reason='approved')[0])
        after = self.read_run(run_id)
        self.assertEqual(before['attempts'], after['attempts'])
        self.assertEqual(before['state'], after['state'])
        self.assertEqual(409, self.action(run_id, 'write', requestId=request_id,
            commandId=str(uuid.uuid4()), message='old window')[0])
        status, written, _ = self.action(run_id, 'write', 'actor-contributor', requestId=request_id,
            commandId=str(uuid.uuid4()), message='new owner same session')
        self.assertEqual(200, status, written)
        _, external, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(1, external['sessionCount'])
        self.assertEqual(1, external['interactionCount'])
        self.assertEqual(attempt['session']['sessionId'], external['interactions'][0]['sessionId'])

    def test_api_sigkill_then_takeover_fences_inflight_adapter_write(self):
        import signal
        import time
        run_id, port, attempt, request_id = self.opened_session('interaction-delayed')
        cls = type(self)
        first_api, first_port = cls.api, cls.api_port
        cls.start_api(excluded_ports={first_port})
        self.addCleanup(cls.stop_process, first_api)
        command_id = str(uuid.uuid4())
        body = dict(self.fences(self.read_run(run_id)['control']), requestId=request_id,
                    commandId=command_id, message='in flight from old API')
        with ThreadPoolExecutor(max_workers=1) as pool:
            inflight = pool.submit(self.request, 'POST', f'/api/v1/runs/{run_id}/control/write', body,
                                   'actor-authorized', port=first_port)
            for _ in range(100):
                _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
                if diagnostics['pendingInteractions']:
                    break
                time.sleep(.02)
            else:
                self.fail('adapter never received the in-flight write')
            os.killpg(first_api.pid, signal.SIGKILL)
            first_api.wait(timeout=10)
            self.assertEqual(-signal.SIGKILL, first_api.returncode)
            self.proof_facts['oldApiExitCode'] = first_api.returncode
            status, changed, _ = self.action(run_id, 'force-takeover', 'actor-contributor', reason='API crashed')
            self.assertEqual(200, status, changed)
            self.assertEqual(200, self.request('POST', '/release-interactions', {}, port=port)[0])
            self.assertEqual(0, inflight.result()[0])
        for _ in range(100):
            _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
            if not diagnostics['pendingInteractions']:
                break
            time.sleep(.02)
        self.assertFalse(diagnostics['pendingInteractions'])
        self.proof_facts['delayedInteractionCount'] = diagnostics['interactionCount']
        self.assertEqual(0, diagnostics['interactionCount'])
        _, receipt, _ = self.request('GET', f'/api/v1/runs/{run_id}/continuations/{command_id}')
        self.assertEqual('fenced', receipt['operation']['state'])
        cls.stop_process(cls.api)
        cls.start_api(excluded_ports={cls.api_port})
        _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(0, diagnostics['interactionCount'])

    def test_invalid_external_reconciliation_does_not_append_partial_history(self):
        run_id, port, attempt, request_id = self.opened_session('interaction-malformed-events')
        command_id = str(uuid.uuid4())
        status, unavailable, _ = self.action(run_id, 'write', requestId=request_id,
            commandId=command_id, message='malformed provider observation')
        self.assertEqual(503, status, unavailable)
        _, before, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        current = self.read_run(run_id)['control']
        status, denied, _ = self.action(run_id, 'force-takeover', 'actor-contributor', reason='Cannot trust receipt')
        self.assertEqual(409, status, denied)
        self.assertEqual('control-fencing-unavailable', denied['code'])
        _, after, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        self.assertEqual(before, after)
        self.assertEqual(current, self.read_run(run_id)['control'])

    def test_pending_continuation_settles_before_responsibility_only_change(self):
        run_id, port, attempt, request_id = self.opened_session('continuation-success-gap')
        status, unavailable, _ = self.action(run_id, 'fork', requestId=request_id, commandId=str(uuid.uuid4()))
        self.assertEqual(503, status, unavailable)
        before = self.read_run(run_id)
        status, denied, _ = self.action(run_id, 'force-takeover', 'actor-contributor', reason='handover')
        self.assertEqual(409, status, denied)
        self.assertEqual('control-continuation-pending', denied['code'])
        self.assertEqual(before['attempts'], self.read_run(run_id)['attempts'])
        cls = type(self)
        cls.stop_process(cls.api)
        cls.start_api(excluded_ports={cls.api_port})
        before = self.read_run(run_id)
        self.assertEqual(200, self.action(run_id, 'force-takeover', 'actor-contributor', reason='handover')[0])
        self.assertEqual(before['attempts'], self.read_run(run_id)['attempts'])

    def test_pending_live_delivery_rejects_transfer_without_partial_session_fencing(self):
        import signal
        from tests.test_active_agent_control import ActiveAgentControlTests as live
        run_id, port, attempt, request_id = self.opened_session('interaction-before-effect-failure')
        command_id = str(uuid.uuid4())
        self.assertEqual(503, self.action(run_id, 'write', requestId=request_id,
            commandId=command_id, message='pending write')[0])
        self.live_providers = {}
        live_port = live.start_fake(self)
        live.start_live(self, run_id, live_port, 'parallel')
        target = next(a['liveOperation'] for a in self.read_run(run_id)['attempts'] if a.get('liveOperation'))
        self.assertEqual(202, live.command(self, run_id, target['attemptId'])[0])
        live.complete(self, live_port, target['currentOperation'])
        worker = fake.FakeCodexTests.paused_worker(self, run_id, live_port,
            'before-active-delivery', '--deliver-active', 'true')
        os.killpg(worker.pid, signal.SIGKILL)
        worker.wait(timeout=10)
        before = self.read_run(run_id)['control']
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        status, denied, _ = self.action(run_id, 'force-takeover', 'actor-contributor', reason='pending delivery')
        self.assertEqual(409, status, denied)
        self.assertEqual('control-active-delivery-pending', denied['code'])
        self.assertEqual(before, self.read_run(run_id)['control'])
        _, after, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        self.assertEqual(history, after)
        _, receipt, _ = self.request('GET', f'/api/v1/runs/{run_id}/continuations/{command_id}')
        self.assertEqual('pending', receipt['operation']['state'])
        live.deliver(self, run_id, live_port)
        self.assertEqual(200, self.action(run_id, 'force-takeover', 'actor-contributor', reason='delivery settled')[0])

    def test_restart_adopts_applied_write_after_adapter_fence_success_gap(self):
        import signal
        run_id, port, attempt, request_id = self.opened_session('interaction-success-gap')
        command_id = str(uuid.uuid4())
        self.assertEqual(503, self.action(run_id, 'write', requestId=request_id,
            commandId=command_id, message='already accepted write')[0])
        _, receipt, _ = self.request('GET', f'/api/v1/runs/{run_id}/continuations/{command_id}')
        operation = receipt['operation']
        # Controlled external seam: fence committed, then the API dies before local adoption.
        status, fenced, _ = self.request('POST', f"/control-operations/{operation['operationKey']}/fence",
            dict(sourceSessionId=operation['sourceSessionId'], action='write'), port=port)
        self.assertEqual(200, status, fenced)
        self.assertEqual('applied', fenced['state'])
        cls = type(self)
        os.killpg(cls.api.pid, signal.SIGKILL)
        cls.api.wait(timeout=10)
        cls.start_api(excluded_ports={cls.api_port})
        _, recovered, _ = self.request('GET', f'/api/v1/runs/{run_id}/continuations/{command_id}')
        self.assertEqual('applied', recovered['operation']['state'])
        self.assertEqual(fenced['receipt'], recovered['adapterReceipt'])
        self.assertEqual(200, self.action(run_id, 'force-takeover', 'actor-contributor', reason='Recovered')[0])
        _, external, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(1, external['interactionCount'])
