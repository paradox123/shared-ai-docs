"""Qualification contract through the delivery worker and authenticated run API."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

from tests import test_control_plane_black_box as harness
from tests.publication_fixture import PublicationFixture, git, probe
from tests import test_evidence_recovery as recovery
from tests.qualification_proof import record


class HeadQualificationTests(harness.ControlPlaneProcessHarness, unittest.TestCase):
    pause_delivery = recovery.EvidenceRecoveryTests.pause_capture
    def assignment(self):
        run_id = self.new_run()
        fixture = PublicationFixture(Path(self.scratch.name) / run_id,
            self.read_run(run_id)['correlation']['issueNumber'])
        self.addCleanup(fixture.close)
        skills = {}
        for name in ('code-review', 'codebase-design', 'domain-modeling'):
            path = fixture.root / (name + '.md')
            path.write_text('Review the supplied ' + name + ' scope independently.')
            skills[name] = {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        fixture.plan['headQualification'] = {'verification': probe('checks passed'),
            'requirements': 'AC1: Greeting returns Hello, Ada!', 'guidance': [], 'skills': skills}
        fixture.save()
        return run_id, fixture

    def deliver(self, run_id, fixture):
        result = harness.command_output(['dotnet', str(harness.WORKER_DLL),
            '--connection-string', self.connection_string, '--fixture', str(self.fixture_path),
            '--run-id', run_id, '--worker-id', 'qualification', '--codex-python', sys.executable,
            '--publication-plan', str(fixture.path)], timeout=180)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        run = self.read_run(run_id)
        record(self._testMethodName, run, fixture, 'controlled Codex adapter')
        return run

    def test_failed_verification_that_mutates_head_is_rejected(self):
        run_id, fixture = self.assignment()
        script = ('import subprocess; from pathlib import Path; '
            'Path("greeting.py").write_text("def greet(): return 0\\n"); '
            'subprocess.run(["git", "add", "."], check=True); '
            'subprocess.run(["git", "commit", "-qm", "Mutated during check"], check=True); '
            'raise SystemExit(1)')
        fixture.plan['headQualification']['verification'] = {
            'argv': [sys.executable, '-c', script], 'expected': 'checks passed'}
        fixture.save()
        run = self.deliver(run_id, fixture)
        self.assertEqual('qualification-blocked', run['state'], run['publication'])
        qualification = run['publication']['headQualification']
        self.assertEqual('qualification-head-drift', qualification['blocker'])
        self.assertIsNone(qualification['qualifiedHeadSha'])
        self.assertNotEqual(run['publication']['intent']['headSha'], git(fixture.repo, 'rev-parse', 'HEAD'))

    def test_three_fresh_peer_blind_reviews_qualify_only_the_current_head(self):
        run_id, fixture = self.assignment()
        run = self.deliver(run_id, fixture)
        self.assertEqual('qualified', run['state'], run['publication'])
        qualification = run['publication']['headQualification']
        head = fixture.pulls[0]['head']['sha']
        self.assertEqual(head, qualification['qualifiedHeadSha'])
        round_ = qualification['rounds'][0]
        self.assertEqual('check-passed', round_['verification']['state'])
        self.assertEqual(3, len(round_['reviews']))
        self.assertEqual(3, len({r['report']['sessionId'] for r in round_['reviews']}))
        self.assertEqual({'requirements', 'code-quality', 'architecture'}, {r['axis'] for r in fixture.review_requests})
        for request in fixture.review_requests:
            self.assertEqual(head, request['headSha'])
            self.assertEqual('gpt-5.6-terra', request['policy']['model'])
            self.assertEqual('xhigh', request['policy']['reasoningEffort'])
            self.assertEqual('read-only', request['policy']['access'])
            self.assertIn('Hello, Ada!', request['input']['requirements'])
            self.assertTrue(request['input']['diff'])
            self.assertNotIn('reviews', request['input'])
            self.assertNotIn('verdict', json.dumps(request['input']))
        self.assertTrue(fixture.pulls[0]['draft'])
        self.assertEqual(1, fixture.creates)
        self.assertEqual(1, fixture.agent_starts)
        cls = type(self)
        cls.stop_process(cls.api); cls.start_api()
        repeated = self.deliver(run_id, fixture)
        self.assertEqual(qualification, repeated['publication']['headQualification'])
        self.assertEqual(3, len(fixture.review_requests))

    def test_actionable_findings_repair_same_writer_then_reverify_new_head(self):
        run_id, fixture = self.assignment()
        def fail_initial(request, result):
            if not fixture.repair_requests and request['axis'] in ('requirements', 'architecture'):
                result.update(verdict='fail', findings=[{'location': 'greeting.py:1',
                    'description': 'Include the required repair marker.'}])
        fixture.review_override = fail_initial
        run = self.deliver(run_id, fixture)
        self.assertEqual('qualified', run['state'], run['publication'].get('headQualification'))
        q = run['publication']['headQualification']
        self.assertEqual(1, len(q['repairs']))
        self.assertEqual(2, len(q['rounds']))
        old, new = q['rounds']
        self.assertNotEqual(old['headSha'], new['headSha'])
        self.assertEqual(new['headSha'], q['qualifiedHeadSha'])
        assignment = fixture.repair_requests[0]
        self.assertEqual(1, assignment['number'])
        self.assertEqual(fixture.session, assignment['writerSessionId'])
        self.assertEqual(str(fixture.repo), assignment['localPath'])
        self.assertEqual({'requirements', 'architecture'}, {f['axis'] for f in assignment['findings']})
        self.assertEqual(new['headSha'], new['evidence']['headSha'])
        self.assertEqual(new['headSha'], new['verification']['headSha'])
        self.assertEqual(6, len({r['report']['sessionId'] for round_ in q['rounds'] for r in round_['reviews']}))
        self.assertEqual(new['headSha'], fixture.pulls[0]['head']['sha'])
        self.assertIn(new['headSha'], fixture.pulls[0]['body'])
        self.assertEqual(1, fixture.creates)
        self.assertEqual(1, fixture.agent_starts)

    def test_three_unsuccessful_repairs_leave_concrete_human_request_and_no_fourth(self):
        run_id, fixture = self.assignment()
        def fail(request, result):
            if request['axis'] == 'code-quality':
                result.update(verdict='fail', findings=[{'location': 'greeting.py:1',
                    'description': 'Resolve the missing greeting normalization.'}])
        fixture.review_override = fail
        fixture.plan['headQualification']['verification'] = probe('check observed a failure')
        fixture.plan['headQualification']['verification']['expected'] = 'checks passed'
        fixture.save()
        run = self.deliver(run_id, fixture)
        self.assertEqual('awaiting-human', run['state'])
        q = run['publication']['headQualification']
        self.assertEqual([1, 2, 3], [r['number'] for r in q['repairs']])
        self.assertEqual(4, len(q['rounds']))
        self.assertEqual(12, len(fixture.review_requests))
        self.assertTrue(all(r['verification']['state'] == 'check-failed' for r in q['rounds']))
        self.assertEqual('gpt-5.6-sol', fixture.repair_requests[-1]['policy']['model'])
        self.assertEqual('final_repair_round', fixture.repair_requests[-1]['policy']['escalationReason'])
        self.assertIn('greeting normalization', q['humanRequest']['problem'])
        self.assertEqual('repair-limit-exhausted', q['blocker'])
        self.assertIsNone(q['qualifiedHeadSha'])
        cls = type(self)
        cls.stop_process(cls.api); cls.start_api()
        self.assertEqual(q, self.deliver(run_id, fixture)['publication']['headQualification'])
        self.assertEqual(3, len(fixture.repair_requests))
        self.assertEqual(1, fixture.creates)
        self.assertTrue(fixture.pulls[0]['draft'])

    def test_invalid_review_is_retained_and_never_repaired(self):
        run_id, fixture = self.assignment()
        def wrong_head(request, result):
            if request['axis'] == 'requirements': result['headSha'] = '0' * 40
        fixture.review_override = wrong_head
        run = self.deliver(run_id, fixture)
        self.assertEqual('qualification-blocked', run['state'])
        q = run['publication']['headQualification']
        self.assertEqual('invalid-review-batch', q['blocker'])
        result = q['rounds'][0]['reviews'][0]['report']
        self.assertEqual('0' * 40, result['receipt']['result']['headSha'])
        self.assertEqual(3, len(fixture.review_requests))
        self.assertEqual([], fixture.repair_requests)

    def test_changed_provider_head_invalidates_qualified_head_on_redelivery(self):
        run_id, fixture = self.assignment()
        run = self.deliver(run_id, fixture)
        self.assertEqual('qualified', run['state'])
        fixture.pulls[0]['head']['sha'] = 'f' * 40
        run = self.deliver(run_id, fixture)
        q = run['publication']['headQualification']
        self.assertEqual('qualification-head-drift', q['blocker'])
        self.assertIsNone(q['qualifiedHeadSha'])
        self.assertEqual(3, len(fixture.review_requests))
        self.assertEqual([], fixture.repair_requests)

    def test_worker_replacement_adopts_review_receipt_without_new_session(self):
        run_id, fixture = self.assignment()
        before = self.pause_delivery(run_id, fixture, 'after-qualification-review-response')
        self.assertIsNone(before['publication']['headQualification']['rounds'][0]['reviews'][0]['report'])
        self.assertEqual(1, len(fixture.review_requests))
        run = self.deliver(run_id, fixture)
        self.assertEqual('qualified', run['state'])
        self.assertEqual(3, len(fixture.review_requests))

    def test_worker_replacement_adopts_repair_in_same_numbered_round(self):
        run_id, fixture = self.assignment()
        def fail_initial(request, result):
            if not fixture.repair_requests and request['axis'] == 'requirements':
                result.update(verdict='fail', findings=[{'location': 'greeting.py:1', 'description': 'Add repair marker.'}])
        fixture.review_override = fail_initial
        before = self.pause_delivery(run_id, fixture, 'after-qualification-repair-response')
        self.assertIsNone(before['publication']['headQualification']['repairs'][0]['report'])
        self.assertEqual(1, len(fixture.repair_requests))
        run = self.deliver(run_id, fixture)
        self.assertEqual('qualified', run['state'])
        self.assertEqual(1, len(fixture.repair_requests))
        self.assertEqual(1, run['publication']['headQualification']['repairs'][0]['number'])

    def test_interrupted_verification_never_reexecutes_check(self):
        run_id, fixture = self.assignment()
        self.pause_delivery(run_id, fixture, 'before-qualification-verification')
        run = self.deliver(run_id, fixture)
        self.assertEqual('verification-interrupted', run['publication']['headQualification']['blocker'])
        self.assertEqual([], fixture.review_requests)

    def test_lost_repair_reply_remains_owned_until_same_operation_is_adopted(self):
        run_id, fixture = self.assignment()
        fixture.repair_lose_reply = True
        def fail_initial(request, result):
            if not fixture.repair_requests and request['axis'] == 'requirements':
                result.update(verdict='fail', findings=[{'location': 'greeting.py:1', 'description': 'Add repair marker.'}])
        fixture.review_override = fail_initial
        run = self.deliver(run_id, fixture)
        self.assertEqual('qualification-uncertain', run['state'])
        successor, other = self.assignment()
        self.assertEqual('repository-publication-busy', self.deliver(successor, other)['publication']['blocker'])
        run = self.deliver(run_id, fixture)
        self.assertEqual('qualified', run['state'])
        self.assertEqual(1, len(fixture.repair_requests))


if __name__ == '__main__':
    unittest.main()
