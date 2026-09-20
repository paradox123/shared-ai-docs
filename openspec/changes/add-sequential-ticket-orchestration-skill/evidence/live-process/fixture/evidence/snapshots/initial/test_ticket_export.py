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
            result = subprocess.run(args, capture_output=True, text=True, check=True)
            return result.stdout

    def test_json_sorts_items_and_trims_titles(self):
        tickets = [{"id": 2, "title": " Second ", "status": "todo"}, {"id": 1, "title": "First", "status": "done"}]
        self.assertEqual(json.loads(self.run_export(tickets, "json")), [{"id": 1, "title": "First", "status": "done"}, {"id": 2, "title": "Second", "status": "todo"}])

    def test_csv_filters_done_items(self):
        tickets = [{"id": 1, "title": "First", "status": "todo"}, {"id": 2, "title": "Second", "status": "done"}]
        self.assertEqual(list(csv.DictReader(io.StringIO(self.run_export(tickets, "csv", "done")))), [{"id": "2", "title": "Second", "status": "done"}])


if __name__ == "__main__":
    unittest.main()
