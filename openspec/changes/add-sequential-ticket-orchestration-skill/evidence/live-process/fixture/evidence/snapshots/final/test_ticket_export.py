import csv
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("ticket_export.py")


class ExportTests(unittest.TestCase):
    def run_export(self, tickets, format, status=None):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "tickets.json"
            source.write_text(json.dumps(tickets))
            args = [sys.executable, str(SCRIPT), str(source), "--format", format]
            if status is not None:
                args += ["--status", status]
            original_bytes = source.read_bytes()
            result = subprocess.run(args, capture_output=True, check=True)
            self.assertEqual(source.read_bytes(), original_bytes)
            return result.stdout.decode()

    def test_json_sorts_items_and_trims_titles(self):
        tickets = [{"id": 2, "title": " Second ", "status": "todo"}, {"id": 1, "title": "First", "status": "done"}]
        self.assertEqual(json.loads(self.run_export(tickets, "json")), [{"id": 1, "title": "First", "status": "done"}, {"id": 2, "title": "Second", "status": "todo"}])

    def test_csv_filters_done_items(self):
        tickets = [{"id": 1, "title": "First", "status": "todo"}, {"id": 2, "title": "Second", "status": "done"}]
        self.assertEqual(list(csv.DictReader(io.StringIO(self.run_export(tickets, "csv", "done")))), [{"id": "2", "title": "Second", "status": "done"}])

    def test_filter_matches_normalized_status_in_both_formats(self):
        tickets = [{"id": 10, "title": " Tenth ", "status": " DONE "}, {"id": 3, "title": "Later", "status": " ToDo "}, {"id": 2, "title": " Second ", "status": "Done"}]
        for format in ("csv", "json"):
            with self.subTest(format=format):
                output = self.run_export(tickets, format, "done")
                if format == "json":
                    self.assertEqual(json.loads(output), [{"id": 2, "title": "Second", "status": "done"}, {"id": 10, "title": "Tenth", "status": "done"}])
                else:
                    self.assertEqual(list(csv.DictReader(io.StringIO(output))), [{"id": "2", "title": "Second", "status": "done"}, {"id": "10", "title": "Tenth", "status": "done"}])

    def test_unfiltered_formats_preserve_quoted_multiline_titles_and_numeric_order(self):
        tickets = [{"id": 10, "title": " Tenth ", "status": " ToDo "}, {"id": 2, "title": '  First, "quoted"\r\nsecond line  ', "status": " DONE "}]
        expected = [{"id": 2, "title": 'First, "quoted"\r\nsecond line', "status": "done"}, {"id": 10, "title": "Tenth", "status": "todo"}]
        self.assertEqual(json.loads(self.run_export(tickets, "json")), expected)
        csv_output = self.run_export(tickets, "csv")
        self.assertEqual(next(csv.reader(io.StringIO(csv_output, newline=""))), ["id", "title", "status"])
        csv_rows = list(csv.DictReader(io.StringIO(csv_output, newline="")))
        for row in csv_rows:
            row["id"] = int(row["id"])
        self.assertEqual(csv_rows, expected)

    def test_empty_input_and_nonmatching_filter_have_empty_results(self):
        cases = [([], None), ([{"id": 1, "title": "First", "status": "done"}], "todo")]
        for tickets, status in cases:
            with self.subTest(tickets=tickets, status=status):
                self.assertEqual(self.run_export(tickets, "csv", status), "id,title,status\r\n")
                self.assertEqual(json.loads(self.run_export(tickets, "json", status)), [])

    def test_todo_filter_matches_normalized_input_in_both_formats(self):
        tickets = [{"id": 10, "title": " Later ", "status": " ToDo "}, {"id": 2, "title": "First", "status": "DONE"}]
        self.assertEqual(json.loads(self.run_export(tickets, "json", "todo")), [{"id": 10, "title": "Later", "status": "todo"}])
        self.assertEqual(list(csv.DictReader(io.StringIO(self.run_export(tickets, "csv", "todo")))), [{"id": "10", "title": "Later", "status": "todo"}])


if __name__ == "__main__":
    unittest.main()
