"""
Tests for tools/release_notes.py.

    python3 -m unittest discover -s tools/tests

Standard library only.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

import build  # noqa: E402
import release_notes  # noqa: E402

CHANGELOG = """# Changelog

All notable changes.

## 0.3.0 beta (2027-01-15)

A third guide.

### New

- One thing.
- Another thing.

## 0.2.1 beta (2026-11-11)

Upkeep.

## 1.0.0 (2027-06-01)

Out of beta.
"""


class ReleaseNotes(unittest.TestCase):
    def test_tag_and_title_come_from_the_version(self):
        info = release_notes.release("0.3.0 beta", CHANGELOG)
        self.assertEqual(info["tag"], "v0.3.0-beta")
        self.assertEqual(info["title"], "0.3.0 beta")
        self.assertEqual(info["prerelease"], "true")

    def test_a_plain_version_is_not_a_prerelease(self):
        info = release_notes.release("1.0.0", CHANGELOG)
        self.assertEqual(info["tag"], "v1.0.0")
        self.assertEqual(info["prerelease"], "false")

    def test_the_notes_are_that_versions_entry_and_nothing_else(self):
        body = release_notes.release("0.3.0 beta", CHANGELOG)["body"]
        self.assertTrue(body.startswith("A third guide.\n"))
        self.assertTrue(body.endswith("- Another thing.\n"))
        self.assertNotIn("Upkeep", body)
        self.assertNotIn("## ", body.replace("### ", ""))

    def test_the_last_entry_runs_to_the_end_of_the_file(self):
        self.assertEqual(release_notes.release("1.0.0", CHANGELOG)["body"], "Out of beta.\n")

    def test_links_to_repository_files_point_at_the_tagged_file(self):
        text = "## 0.4.0 (2027-02-01)\n\nSee [the plan](docs/roadmap.md), [OHA](https://www.oregon.gov/oha), and [below](#more).\n"
        body = release_notes.release("0.4.0", text)["body"]
        self.assertIn(f"[the plan]({build.PROJECT_REPO}/blob/v0.4.0/docs/roadmap.md)", body)
        self.assertIn("[OHA](https://www.oregon.gov/oha)", body)
        self.assertIn("[below](#more)", body)

    def test_a_version_with_no_entry_is_refused(self):
        with self.assertRaises(release_notes.ReleaseError):
            release_notes.release("0.9.9 beta", CHANGELOG)

    def test_an_odd_version_is_refused(self):
        with self.assertRaises(release_notes.ReleaseError):
            release_notes.release("version two", CHANGELOG)

    def test_the_real_changelog_has_an_entry_for_the_real_version(self):
        info = release_notes.release()
        self.assertEqual(info["title"], build.VERSION)
        self.assertTrue(info["body"].strip())


if __name__ == "__main__":
    unittest.main()
