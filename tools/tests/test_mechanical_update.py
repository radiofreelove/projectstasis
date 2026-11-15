"""
Tests for tools/mechanical_update.py: what it will write, and what it refuses.

    python3 -m unittest discover -s tools/tests

Every test works on a made-up registry, baseline, and audit in a temporary
folder. The real data/sources.json is read once, to prove the tool can
find every source's date in it, and is never written.

Standard library only.
"""
from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

import mechanical_update as mech  # noqa: E402

# Laid out like data/sources.json, with traps: a note that quotes a
# "checked" date, an id that starts with another id, and a second list
# whose entries have no id.
REGISTRY = """{
  "registry_version": "2026-11-14",
  "notes": "'opened' means the document was read on the 'checked' date.",
  "sources": [
    {
      "id": "T1",
      "url": "https://example.test/one",
      "checked": "2026-11-10",
      "opened": true,
      "notes": "Says \\"checked\\": \\"2026-11-10\\" in its text. Not a field."
    },
    {
      "id": "T10",
      "url": "https://example.test/ten",
      "date_on_document": "2026-11-10",
      "checked": "2026-11-10",
      "opened": false,
      "notes": "Français"
    },
    {
      "id": "T2",
      "url": "https://example.test/two",
      "checked": "2026-11-02",
      "opened": true,
      "notes": ""
    },
    {
      "id": "T3",
      "url": "https://example.test/three",
      "checked": "2026-11-16",
      "opened": true,
      "notes": ""
    }
  ],
  "application_languages": {
    "items": [
      {
        "hreflang": "en",
        "url": "https://example.test/form.pdf"
      }
    ]
  }
}
"""


def result(source_id, state="unchanged", digest=None, **extra):
    urls = {"T1": "one", "T10": "ten", "T2": "two", "T3": "three"}
    return dict({"id": source_id, "url": f"https://example.test/{urls.get(source_id, 'x')}", "state": state,
                 "mode": "text", "sha256": digest or f"hash-{source_id}", "length": 10, "unverified": False}, **extra)


def base(source_id, digest=None, hashed=True):
    return {"id": source_id, "url": result(source_id)["url"], "fetched": "2026-11-15",
            "state": "fetched" if hashed else "checker-blocked", "mode": "text" if hashed else None,
            "sha256": (digest or f"hash-{source_id}") if hashed else None, "length": 10 if hashed else None}


class Case(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="stasis-mechanical-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.registry = self.tmp / "sources.json"
        self.registry.write_text(REGISTRY, encoding="utf-8")
        self.baseline = [base("T1"), base("T10"), base("T2"), base("T3")]

    def run_tool(self, results, *args, audit_date="2026-11-16", today="2026-11-16"):
        (self.tmp / "audit.json").write_text(json.dumps({"audit_date": audit_date, "results": results}))
        (self.tmp / "baseline.json").write_text(json.dumps({"sources": self.baseline}))
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = mech.main(["--audit", str(self.tmp / "audit.json"), "--registry", str(self.registry),
                              "--baseline", str(self.tmp / "baseline.json"), "--today", today, *args])
        return code, out.getvalue(), err.getvalue()

    def dates(self):
        return {src["id"]: src["checked"] for src in json.loads(self.registry.read_text(encoding="utf-8"))["sources"]}

    def assertRefused(self, outcome, *fragments):
        code, out, err = outcome
        self.assertEqual(code, 2, out + err)
        self.assertIn("Nothing was written", err)
        for fragment in fragments:
            self.assertIn(fragment, err)
        self.assertEqual(self.registry.read_text(encoding="utf-8"), REGISTRY)


class Updates(Case):
    def test_only_unchanged_sources_get_the_audit_date(self):
        code, out, _ = self.run_tool([result("T1"), result("T10"), result("T2", "changed", "new"),
                                      result("T3", "checker-blocked", sha256=None)])
        self.assertEqual(code, 0)
        self.assertEqual(self.dates(), {"T1": "2026-11-16", "T10": "2026-11-16", "T2": "2026-11-02", "T3": "2026-11-16"})
        self.assertIn("2 checked dates updated", out)
        self.assertIn("- T1: 2026-11-10 to 2026-11-16", out)
        self.assertIn("- T10: 2026-11-10 to 2026-11-16", out)
        self.assertNotIn("T2", out)

    def test_nothing_but_the_checked_lines_changes(self):
        self.run_tool([result("T1"), result("T10"), result("T2")])
        old, new = REGISTRY.splitlines(), self.registry.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(old), len(new))
        different = [(a, b) for a, b in zip(old, new) if a != b]
        self.assertEqual(len(different), 3)
        for a, b in different:
            self.assertTrue(a.strip().startswith('"checked": "'), a)
            self.assertEqual(b.strip(), '"checked": "2026-11-16",')
        # The traps stayed as they were: the quoted date in a note, T10's
        # other date, the registry version, and the letters in "Français".
        text = self.registry.read_text(encoding="utf-8")
        for kept in ('\\"checked\\": \\"2026-11-10\\"', '"date_on_document": "2026-11-10"',
                     '"registry_version": "2026-11-14"', "Français"):
            self.assertIn(kept, text)

    def test_a_date_never_moves_backward(self):
        code, out, _ = self.run_tool([result("T3")], audit_date="2026-11-15", today="2026-11-16")
        self.assertEqual(code, 0)
        self.assertEqual(self.registry.read_text(encoding="utf-8"), REGISTRY)
        self.assertIn("- T3: already checked on 2026-11-16", out)

    def test_an_unverified_connection_is_left_alone(self):
        code, out, _ = self.run_tool([result("T1", unverified=True), result("T2")])
        self.assertEqual(code, 0)
        self.assertEqual(self.dates()["T1"], "2026-11-10")
        self.assertEqual(self.dates()["T2"], "2026-11-16")
        self.assertIn("- T1: read over a connection the audit could not verify", out)

    def test_only_limits_the_run(self):
        code, _, _ = self.run_tool([result("T1"), result("T2")], "--only", "T2")
        self.assertEqual(code, 0)
        self.assertEqual((self.dates()["T1"], self.dates()["T2"]), ("2026-11-10", "2026-11-16"))

    def test_the_summary_can_go_to_a_file(self):
        self.run_tool([result("T1")], "--summary", str(self.tmp / "summary.md"))
        self.assertIn("- T1: 2026-11-10 to 2026-11-16", (self.tmp / "summary.md").read_text(encoding="utf-8"))

    def test_every_date_in_the_real_registry_can_be_found(self):
        # Read only: plan and apply work on text in memory.
        text = mech.REGISTRY.read_text(encoding="utf-8")
        registry = json.loads(text)
        updates = [(src["id"], src["checked"], "2099-01-01") for src in registry["sources"]]
        after = json.loads(mech.apply(text, updates))
        self.assertTrue(all(src["checked"] == "2099-01-01" for src in after["sources"]))
        self.assertEqual(after["application_languages"], registry["application_languages"])
        self.assertEqual(mech.REGISTRY.read_text(encoding="utf-8"), text)


class Gating(Case):
    def test_refuses_a_named_source_that_changed(self):
        self.assertRefused(self.run_tool([result("T1"), result("T2", "changed", "new")], "--only", "T1", "T2"),
                           "T2: the audit says changed")

    def test_refuses_a_named_source_that_was_blocked_or_unreachable(self):
        for state in ("checker-blocked", "unreachable", "not yet baselined"):
            self.assertRefused(self.run_tool([result("T1", state, sha256=None)], "--only", "T1"),
                               f"T1: the audit says {state}")

    def test_refuses_a_named_source_the_audit_did_not_cover(self):
        self.assertRefused(self.run_tool([result("T1")], "--only", "T2"), "T2: the audit says not in the audit")

    def test_refuses_an_unchanged_claim_the_baseline_does_not_back(self):
        self.assertRefused(self.run_tool([result("T1"), result("T2", digest="something else")]),
                           "T2: the audit's hash is not the baseline's hash")

    def test_refuses_when_the_baseline_has_no_hash(self):
        self.baseline[0] = base("T1", hashed=False)
        self.assertRefused(self.run_tool([result("T1")]), "T1: unchanged in the audit, but the baseline holds no hash")
        self.baseline.pop(0)
        self.assertRefused(self.run_tool([result("T1")]), "T1: unchanged in the audit, but the baseline holds no hash")

    def test_refuses_when_the_address_differs(self):
        self.assertRefused(self.run_tool([result("T1", url="https://example.test/moved")]),
                           "T1: the audit, the baseline, and the registry do not name one address")

    def test_refuses_a_source_that_is_not_in_the_registry(self):
        self.baseline.append(base("T99"))
        self.assertRefused(self.run_tool([result("T1"), result("T99")]), "T99: unchanged in the audit, but not in the registry")

    def test_one_bad_source_stops_the_whole_run(self):
        # T1 is fine. It is still not written, because the audit cannot be trusted.
        self.assertRefused(self.run_tool([result("T1"), result("T2", digest="wrong")]))

    def test_refuses_a_stale_or_future_audit(self):
        self.assertRefused(self.run_tool([result("T1")], audit_date="2026-11-10"), "more than 2 days ago")
        self.assertRefused(self.run_tool([result("T1")], audit_date="2026-11-20"), "after today")

    def test_refuses_an_audit_it_cannot_read(self):
        self.assertRefused(self.run_tool([result("T1"), result("T1")]), "T1: listed twice")
        self.assertRefused(self.run_tool([result("T1", "fine")]), "unknown state 'fine'")
        self.assertRefused(self.run_tool([result("T1")], audit_date="last week"), "no 'audit_date'")
        self.assertRefused(self.run_tool("not a list of results"))

    def test_a_changed_source_elsewhere_in_the_audit_does_not_block_the_rest(self):
        # Without --only, the tool touches only unchanged sources, so a
        # changed, blocked, or unreachable source is simply not touched.
        code, _, _ = self.run_tool([result("T1"), result("T2", "unreachable", sha256=None),
                                    result("T10", "changed", "new")])
        self.assertEqual(code, 0)
        self.assertEqual(self.dates(), {"T1": "2026-11-16", "T10": "2026-11-10", "T2": "2026-11-02", "T3": "2026-11-16"})


if __name__ == "__main__":
    unittest.main()
