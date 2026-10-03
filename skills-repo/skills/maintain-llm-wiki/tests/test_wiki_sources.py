import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CLI = Path(__file__).resolve().parents[1] / "scripts/wiki_sources.py"
ABC_SHA256 = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


class WikiSourcesTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.vault = Path(self.temporary.name)
        self.wiki = self.vault / "wiki"
        (self.wiki / "notes").mkdir(parents=True)
        self.source = self.vault / "original.md"
        self.source.write_text("abc")
        self.page = self.wiki / "notes/topic.md"
        self.page.write_text(
            '---\ntitle: Topic\nreviewed_at: "2026-10-02T00:00:00Z"\n'
            'wiki_sources: [{"path":"original.md","sha256":"' + ABC_SHA256 + '"}]\n'
            '---\n\n# Topic\n\nA retained synthesis.\n'
        )

    def run_cli(self, command, *arguments):
        result = subprocess.run(
            [sys.executable, str(CLI), command, "--vault", str(self.vault),
             "--wiki", str(self.wiki), *map(str, arguments)],
            text=True, capture_output=True,
        )
        return result, json.loads(result.stdout)

    def test_check_reports_existing_page_against_literal_source_version(self):
        before = self.page.read_bytes()
        result, report = self.run_cli("check")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(report["pages"]), 1)
        page = report["pages"][0]
        self.assertEqual(page["status"], "unchanged")
        self.assertEqual(page["sources"][0]["status"], "unchanged")
        self.assertEqual(page["sources"][0]["actual_sha256"], ABC_SHA256)
        self.assertEqual(self.page.read_bytes(), before)

    def test_record_preserves_prose_and_other_metadata_then_detects_source_change(self):
        self.page.write_text('---\ntitle: Topic\nauthor: Daniel\n---\n\n# Topic\n\nReviewed prose.\n')
        result, report = self.run_cli("record", "--page", self.page, "--source", self.source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(report["ok"])
        text = self.page.read_text()
        self.assertIn("title: Topic\nauthor: Daniel\n", text)
        self.assertTrue(text.endswith("---\n\n# Topic\n\nReviewed prose.\n"))
        _, checked = self.run_cli("check", "--page", self.page)
        self.assertEqual(checked["pages"][0]["status"], "unchanged")
        self.source.write_text("changed original")
        before = self.page.read_bytes()
        result, checked = self.run_cli("check", "--page", self.page)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(checked["pages"][0]["status"], "review")
        self.assertEqual(checked["pages"][0]["sources"][0]["status"], "changed")
        self.assertEqual(self.page.read_bytes(), before)

    def test_missing_source_only_requires_review_for_its_page(self):
        other = self.wiki / "notes/unrelated.md"
        other_source = self.vault / "other.md"
        other_source.write_text("abc")
        other.write_text(self.page.read_text().replace("original.md", "other.md"))
        self.source.unlink()
        before = {p: p.read_bytes() for p in [self.page, other]}
        result, report = self.run_cli("check")
        self.assertEqual(result.returncode, 1)
        by_page = {Path(p["page"]).name: p for p in report["pages"]}
        self.assertEqual(by_page["topic.md"]["status"], "review")
        self.assertEqual(by_page["topic.md"]["sources"][0]["status"], "missing")
        self.assertEqual(by_page["unrelated.md"]["status"], "unchanged")
        for page, content in before.items():
            self.assertEqual(page.read_bytes(), content)
        selected, report = self.run_cli("check", "--page", "notes/unrelated.md")
        self.assertEqual(selected.returncode, 0)
        self.assertEqual(len(report["pages"]), 1)

    def test_bad_metadata_and_page_escape_are_invalid_json_reports(self):
        for content in ["# Missing provenance", "---\nwiki_sources: nope\n---\n", "---\nwiki_sources: []\n---\n"]:
            with self.subTest(content=content):
                self.page.write_text(content)
                result, report = self.run_cli("check", "--page", self.page)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(report["pages"][0]["status"], "invalid")
        result, report = self.run_cli("check", "--page", "../original.md")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["pages"][0]["status"], "invalid")

    def test_record_rejects_unsafe_or_missing_sources_without_editing(self):
        technical = self.vault / ".state/sources/copied.md"
        technical.parent.mkdir(parents=True)
        technical.write_text("abc")
        before = self.page.read_bytes()
        for source in [self.page, technical, self.vault.parent / "outside.md", self.vault / "missing.md"]:
            with self.subTest(source=source):
                result, report = self.run_cli("record", "--page", self.page, "--source", source)
                self.assertEqual(result.returncode, 1)
                self.assertFalse(report["ok"])
                self.assertEqual(self.page.read_bytes(), before)

    def test_source_symlink_outside_vault_is_rejected(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "external.md"
            target.write_text("abc")
            self.source.unlink()
            self.source.symlink_to(target)
            result, report = self.run_cli("check")
            self.assertEqual(result.returncode, 1)
            self.assertEqual(report["pages"][0]["status"], "invalid")

    def test_nonexistent_wiki_cannot_report_success_for_empty_scope(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "check", "--vault", str(self.vault),
             "--wiki", str(self.vault / "not-a-wiki")], text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["ok"])

    def test_metadata_without_review_stamp_is_invalid(self):
        self.page.write_text(self.page.read_text().replace('reviewed_at: "2026-10-02T00:00:00Z"\n', ""))
        result, report = self.run_cli("check")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["pages"][0]["status"], "invalid")

    def test_malformed_review_stamp_produces_invalid_instead_of_a_crash(self):
        original_text = self.page.read_text()
        for value in [123, {}, "broken-date", "2026-10-02"]:
            with self.subTest(value=value):
                self.page.write_text(original_text.replace('"2026-10-02T00:00:00Z"', json.dumps(value)))
                result, report = self.run_cli("check")
                self.assertEqual(result.returncode, 1)
                self.assertEqual(report["pages"][0]["status"], "invalid")

    def test_record_uses_same_frontmatter_boundary_as_check(self):
        self.page.write_text(self.page.read_text().replace("---\n", "--- \n"))
        result, report = self.run_cli("check")
        self.assertEqual(result.returncode, 0)
        result, report = self.run_cli("record", "--page", self.page, "--source", self.source)
        self.assertEqual(result.returncode, 0)
        text = self.page.read_text()
        self.assertEqual(text.count("wiki_sources:"), 1)
        self.assertEqual(text.count("reviewed_at:"), 1)
        self.assertIn("title: Topic\n", text)
        self.assertTrue(text.endswith("---\n\n# Topic\n\nA retained synthesis.\n"))

    def test_stored_absolute_source_path_is_invalid_even_inside_vault(self):
        text = self.page.read_text().replace('"original.md"', json.dumps(str(self.source)))
        self.page.write_text(text)
        result, report = self.run_cli("check")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["pages"][0]["status"], "invalid")

    def test_stored_tilde_path_is_relative_to_vault_and_never_home_expanded(self):
        with tempfile.TemporaryDirectory(dir=Path.home(), prefix=".wiki-provenance-") as directory:
            vault = Path(directory)
            (vault / "wiki/notes").mkdir(parents=True)
            (vault / "original.md").write_text("abc")
            home_alias = "~/" + str(vault.relative_to(Path.home())) + "/original.md"
            page = vault / "wiki/notes/topic.md"
            page.write_text(self.page.read_text().replace('"original.md"', json.dumps(home_alias)))
            result = subprocess.run(
                [sys.executable, str(CLI), "check", "--vault", str(vault), "--wiki", str(vault / "wiki")],
                text=True, capture_output=True,
            )
            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(report["pages"][0]["status"], "review")
            self.assertEqual(report["pages"][0]["sources"][0]["status"], "missing")


if __name__ == "__main__":
    unittest.main()
