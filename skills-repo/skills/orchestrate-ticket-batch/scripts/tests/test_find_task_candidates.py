import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'find_task_candidates.py'
TITLE = 'CRM #4: Projektfakten'
FIRST = '01a0a948-3b72-7612-b191-fd789bc582f7'
SECOND = '01a0a8ff-42e6-79d3-ba11-45ca41f70de0'


class CandidateCliTests(unittest.TestCase):
    def run_index(self, rows):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'session_index.jsonl'
            contents = ''.join(json.dumps(row) + '\n' for row in rows)
            path.write_text(contents)
            result = subprocess.run(
                [sys.executable, str(SCRIPT), '--index', str(path), '--title', TITLE,
                 '--not-before', '2026-09-16T08:10:00Z'],
                capture_output=True, text=True)
            self.assertEqual(path.read_text(), contents)
            return result.returncode, json.loads(result.stdout) if result.stdout.strip() else {}

    def test_finds_exact_title_even_after_later_activity_without_leaking_other_rows(self):
        code, result = self.run_index([
            {'id': SECOND, 'thread_name': 'Unrelated secret title', 'updated_at': '2026-09-16T09:00:00Z'},
            {'id': FIRST, 'thread_name': TITLE, 'updated_at': '2026-09-17T10:00:00.123456789Z'},
        ])
        self.assertEqual((code, result['status']), (0, 'candidate'))
        self.assertEqual([row['id'] for row in result['candidates']], [FIRST])
        self.assertNotIn('secret', json.dumps(result))

    def test_duplicate_rows_do_not_hide_multiple_distinct_candidates(self):
        row = {'id': FIRST, 'thread_name': TITLE, 'updated_at': '2026-09-16T08:14:39Z'}
        code, result = self.run_index([row, row, {**row, 'id': SECOND}])
        self.assertEqual((code, result['status']), (2, 'ambiguous'))
        self.assertEqual(len(result['candidates']), 2)

    def test_malformed_matching_metadata_returns_error_not_a_safe_empty_result(self):
        code, result = self.run_index([
            {'id': FIRST, 'thread_name': TITLE, 'updated_at': 'broken'},
        ])
        self.assertEqual(code, 3)
        self.assertEqual(result.get('status'), 'error')
        self.assertEqual(result.get('candidates'), [])

    def test_no_recent_exact_match_does_not_infer_absence_of_the_task(self):
        code, result = self.run_index([
            {'id': FIRST, 'thread_name': TITLE, 'updated_at': '2026-09-16T07:00:00Z'},
            {'id': SECOND, 'thread_name': TITLE + ' extra', 'updated_at': '2026-09-16T09:00:00Z'},
        ])
        self.assertEqual((code, result['status'], result['count']), (2, 'not-found', 0))
        self.assertTrue(result['requiresDirectVerification'])

    def test_repeated_index_entries_for_one_id_are_one_candidate(self):
        row = {'id': FIRST, 'thread_name': TITLE, 'updated_at': '2026-09-16T10:14:39+02:00'}
        code, result = self.run_index([row, {**row, 'updated_at': '2026-09-16T08:12:00Z'}])
        self.assertEqual((code, result['count']), (0, 1))
        self.assertEqual(result['candidates'][0]['updated_at'], row['updated_at'])

    def test_output_is_bounded_without_hiding_ambiguity(self):
        rows = [{'id': '00000000-0000-0000-0000-%012d' % number,
                 'thread_name': TITLE, 'updated_at': '2026-09-16T09:00:00Z'} for number in range(15)]
        code, result = self.run_index(rows)
        self.assertEqual((code, result['status']), (2, 'ambiguous'))
        self.assertEqual((result['count'], len(result['candidates']), result['omitted']), (15, 10, 5))

    def test_provisional_id_is_not_a_task_candidate(self):
        code, result = self.run_index([
            {'id': 'client-new-thread:abc', 'thread_name': TITLE, 'updated_at': '2026-09-16T09:00:00Z'},
        ])
        self.assertEqual((code, result['status']), (3, 'error'))

    def test_invalid_title_metadata_is_an_error_even_before_title_filtering(self):
        for title_fields in ({}, {'thread_name': None}, {'thread_name': 42}):
            with self.subTest(title_fields=title_fields):
                code, result = self.run_index([
                    {'id': FIRST, 'updated_at': '2026-09-16T09:00:00Z', **title_fields},
                ])
                self.assertEqual((code, result['status']), (3, 'error'))


if __name__ == '__main__':
    unittest.main()
