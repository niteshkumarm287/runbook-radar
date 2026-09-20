import tempfile
import unittest
from pathlib import Path

from search import load_runbooks, search_runbooks


class SearchTests(unittest.TestCase):
    def test_empty_inputs_and_limit(self):
        self.assertEqual(search_runbooks("disk full", []), [])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "disk-space.md").write_text(
                "Disk space full cleanup", encoding="utf-8"
            )
            books = load_runbooks(path)
            self.assertEqual(search_runbooks(" ", books), [])
            self.assertEqual(search_runbooks("disk space", books, limit=0), [])
            self.assertEqual(
                search_runbooks("disk space", books)[0]["name"], "disk-space"
            )

    def test_filename_fallback_with_empty_body(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "disk-space.md").write_text("the and", encoding="utf-8")
            books = load_runbooks(path)
            self.assertEqual(
                search_runbooks("disk space", books)[0]["name"], "disk-space"
            )
            self.assertEqual(search_runbooks("unrelated database", books), [])

    def test_nested_runbook_names(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "ops").mkdir()
            (path / "ops/disk-space.md").write_text(
                "Disk space cleanup", encoding="utf-8"
            )
            self.assertEqual(load_runbooks(path)[0]["name"], "ops/disk-space")

    def test_invalid_options(self):
        with self.assertRaises(ValueError):
            search_runbooks("disk", [], limit=-1)
        with self.assertRaises(ValueError):
            search_runbooks("disk", [], minimum_similarity=2)
