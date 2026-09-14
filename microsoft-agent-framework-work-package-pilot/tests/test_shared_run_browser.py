"""Shared run view verified through the public GUI and persisted HTTP contract."""
import json
import subprocess
import unittest
import select
from tests.test_submission_execution import SubmissionExecutionHarness
from tests.test_control_plane_black_box import PILOT_ROOT


def shared_browser(payload):
    result = subprocess.run(['node', str(PILOT_ROOT / 'tests/shared_run_browser.cjs')],
        input=json.dumps(payload), text=True, capture_output=True, timeout=90)
    if result.returncode:
        raise AssertionError('Shared run browser proof failed: ' + result.stderr)
    return json.loads(result.stdout)


def observe_shared_run(test, payload, start_worker, finish_worker, stop_worker):
    process = subprocess.Popen(['node', str(PILOT_ROOT / 'tests/shared_observation_browser.cjs')],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
    test.addCleanup(test.stop_process, process)
    for pipe in (process.stdin, process.stdout, process.stderr): test.addCleanup(pipe.close)
    def send(value):
        process.stdin.write(json.dumps(value) + '\n'); process.stdin.flush()
    def receive():
        ready, _, _ = select.select([process.stdout], [], [], 210 if payload.get('live') else 40)
        test.assertTrue(ready, 'Browser did not reach the next stage')
        line = process.stdout.readline()
        if not line: test.fail(process.stderr.read())
        return json.loads(line)
    send(payload)
    queued = receive()
    test.assertEqual('queued', queued['stage'])
    worker = start_worker()
    send({'continue': True})
    test.assertEqual('running', receive()['stage'])
    finish_worker()
    send({'continue': True})
    completed = receive()
    test.assertEqual('completed', completed['stage'])
    stop_worker(worker)
    test.stop_process(test.api)
    test.start_api()
    send({'baseUrl': test.base_url})
    verified = receive()
    test.assertEqual('verified', verified['stage'])
    test.assertEqual(0, process.wait(timeout=10), process.stderr.read())
    return {'start': queued, 'completed': completed, 'reopened': verified}


class SharedRunBrowserTests(SubmissionExecutionHarness, unittest.TestCase):
    def test_revocation_during_initial_hydration_cannot_reconnect_the_cleared_workspace(self):
        self.worker()
        _, selected, _ = self.post('', {'sourceUrl': self.issue(811), 'start': True})
        self.await_state(selected['submissionId'], 'completed')
        _, other, _ = self.post('', {'sourceUrl': self.issue(812)})
        shared_browser({'baseUrl': self.base_url,
            'credential': self.provider.tokens['actor-authorized'], 'submissionId': selected['submissionId'],
            'runId': selected['runId'], 'revokedDuringOpen': other['submissionId']})

    def test_unrelated_hanging_status_read_does_not_block_opening_a_saved_run(self):
        self.worker()
        records = []
        for number in (809, 810):
            _, record, _ = self.post('', {'sourceUrl': self.issue(number), 'start': True})
            self.await_state(record['submissionId'], 'completed')
            records.append(record)
        shared_browser({'baseUrl': self.base_url,
            'credential': self.provider.tokens['actor-authorized'],
            'submissionId': records[0]['submissionId'], 'blockedOther': records[1]['submissionId']})

    def test_admitted_requirements_remain_truthful_when_another_client_starts_them(self):
        worker = self.worker()
        _, previous, _ = self.post('', {'sourceUrl': self.issue(808), 'start': True})
        self.await_state(previous['submissionId'], 'completed')
        self.stop_process(worker)
        _, record, _ = self.post('', {'sourceUrl': self.issue(805)})
        shared_browser({'baseUrl': self.base_url,
            'credential': self.provider.tokens['actor-authorized'], 'previousSubmissionId': previous['submissionId'],
            'submissionId': record['submissionId'], 'admitted': True})

    def test_late_previous_run_reads_cannot_replace_the_current_selection(self):
        self.worker()
        _, first, _ = self.post('', {'sourceUrl': self.issue(806), 'start': True})
        _, second, _ = self.post('', {'sourceUrl': self.issue(807), 'start': True})
        for record in (first, second): self.await_state(record['submissionId'], 'completed')
        shared_browser({'baseUrl': self.base_url,
            'credential': self.provider.tokens['actor-authorized'],
            'submissionId': first['submissionId'], 'otherSubmissionId': second['submissionId']})

    def test_real_worker_updates_and_api_reopening_preserve_run_view_and_step_focus(self):
        self.analysis.release.clear()
        self.addCleanup(self.analysis.release.set)
        observe_shared_run(self, {'baseUrl': self.base_url,
            'credential': self.provider.tokens['actor-authorized'], 'sourceUrl': self.issue(804)},
            self.worker, self.analysis.release.set, self.stop_process)

    def test_public_states_and_transport_recovery_keep_navigation_and_focus(self):
        self.worker()
        _, record, _ = self.post('', {'sourceUrl': self.issue(803), 'start': True})
        self.await_state(record['submissionId'], 'completed')
        shared_browser({'baseUrl': self.base_url,
            'credential': self.provider.tokens['actor-authorized'],
            'submissionId': record['submissionId'], 'states': True})

    def test_saved_run_opens_result_with_keyboard_access_to_all_four_views(self):
        self.worker()
        source = self.issue(802)
        self.provider.issues['802']['body'] = 'Long retained requirements.\n' * 100
        _, record, _ = self.post('', {'sourceUrl': source, 'start': True})
        self.await_state(record['submissionId'], 'completed')
        shared_browser({'baseUrl': self.base_url,
            'credential': self.provider.tokens['actor-authorized'],
            'submissionId': record['submissionId'], 'navigation': True})

    def test_completed_run_list_and_header_agree_with_public_execution(self):
        self.worker()
        _, record, _ = self.post('', {'sourceUrl': self.issue(801), 'start': True})
        self.await_state(record['submissionId'], 'completed')
        shared_browser({'baseUrl': self.base_url,
            'credential': self.provider.tokens['actor-authorized'],
            'submissionId': record['submissionId']})


class SharedRunFaultBrowserTests(unittest.TestCase):
    def check_fault(self, mode):
        result = subprocess.run(['node', str(PILOT_ROOT / 'tests/shared_focus_browser.cjs'), mode],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_rejected_intake_does_not_stop_the_selected_run_observation(self):
        self.check_fault('rejection')

    def test_live_events_preserve_session_disclosure_and_artifact_button_focus(self):
        self.check_fault('focus')
