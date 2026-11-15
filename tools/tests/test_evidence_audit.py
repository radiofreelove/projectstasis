"""
Tests for tools/evidence_audit.py, against fixture content on this computer.

    python3 -m unittest discover -s tools/tests

No request leaves the machine. The first tests feed the tool small pieces
of HTML and made-up baselines. The last ones run the whole tool against
small servers here that copy the ways a source can answer:

  - a web page that stays the same, apart from its markup and scripts
  - a web page whose words change after the baseline
  - a PDF, compared by its bytes
  - a server that answers 403 to this tool
  - a site whose robots.txt keeps this tool out
  - a port nothing answers on, and a page that is gone
  - a registry entry marked "link_check": "by hand", which must not be
    requested at all
  - a source that was added after the baseline was written

Standard library only.
"""
from __future__ import annotations

import contextlib
import http.client
import http.server
import io
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

import evidence_audit as audit  # noqa: E402

PAGE = """<!doctype html>
<html><head><title>Work rules</title>
<style>p { color: red }</style>
<script>var stamp = "%s";</script></head>
<body><h1>Work   rules</h1>
<p>The rules start <b>Jan.&nbsp;1,
2027</b>.</p><ul><li>80 hours a month</li><li>%s</li></ul></body></html>
"""


class Normalization(unittest.TestCase):
    def test_html_becomes_the_words_a_reader_sees(self):
        text = audit.html_text(PAGE % ("abc", "School counts"))
        self.assertEqual(text, "Work rules\nWork rules\nThe rules start Jan. 1, 2027.\n80 hours a month\nSchool counts")

    def test_scripts_styles_and_markup_do_not_change_the_hash(self):
        first = audit.normalize((PAGE % ("run 1", "School counts")).encode(), "text/html; charset=utf-8")
        again = (PAGE % ("run 2", "School counts")).replace("<b>", '<strong class="x">').replace("</b>", "</strong>")
        second = audit.normalize(again.replace("\n", "\n   ").encode(), "text/html")
        self.assertEqual(first[0], "text")
        self.assertEqual(first[2], second[2])
        self.assertEqual(first[3], len(first[1]))

    def test_a_changed_word_changes_the_hash(self):
        first = audit.normalize((PAGE % ("x", "School counts")).encode(), "text/html")
        second = audit.normalize((PAGE % ("x", "School no longer counts")).encode(), "text/html")
        self.assertNotEqual(first[2], second[2])

    def test_html_is_recognized_without_a_content_type(self):
        self.assertEqual(audit.normalize(b"<html><body><p>Hello</p></body></html>", "")[1], "Hello")

    def test_a_pdf_is_compared_by_its_bytes(self):
        body = b"%PDF-1.7\n1 0 obj\n<< /Title (Form) >>\nendobj\n"
        mode, text, digest, length = audit.normalize(body, "application/pdf")
        self.assertEqual((mode, text, length), ("bytes", None, len(body)))
        # Served with the wrong type, it is still a PDF.
        self.assertEqual(audit.normalize(body, "text/html")[0], "bytes")
        self.assertNotEqual(digest, audit.normalize(body + b" ", "application/pdf")[2])

    def test_a_diff_is_cut_to_a_limit(self):
        old = "\n".join(f"line {n}" for n in range(200))
        new = "\n".join(f"line {n} changed " + "x" * 500 for n in range(200))
        diff = audit.bounded_diff(old, new, limit=10, width=50)
        self.assertEqual(len(diff.splitlines()), 11)
        self.assertIn("more diff lines not shown", diff)
        self.assertTrue(all(len(line) <= 60 for line in diff.splitlines()))
        self.assertNotIn("```", audit.bounded_diff("a", "```\nb"))


def fetched(digest="aaa", mode="text"):
    return {"state": audit.FETCHED, "mode": mode, "sha256": digest, "length": 3, "text": "abc"}


def entry(source_id="T1", digest="aaa", url="https://example.test/a", **extra):
    return dict({"id": source_id, "url": url, "fetched": "2026-11-15", "state": audit.FETCHED if digest else
                 audit.BLOCKED, "mode": "text" if digest else None, "sha256": digest,
                 "length": 3 if digest else None, "registry_checked": "2026-11-10"}, **extra)


class Classification(unittest.TestCase):
    URL = "https://example.test/a"

    def test_each_source_gets_one_state(self):
        self.assertEqual(audit.classify(fetched("aaa"), entry(), self.URL), audit.UNCHANGED)
        self.assertEqual(audit.classify(fetched("bbb"), entry(), self.URL), audit.CHANGED)
        self.assertEqual(audit.classify({"state": audit.UNREACHABLE, "note": "x"}, entry(), self.URL), audit.UNREACHABLE)
        self.assertEqual(audit.classify({"state": audit.BLOCKED, "note": "x"}, entry(), self.URL), audit.BLOCKED)

    def test_a_missing_baseline_is_never_a_change(self):
        self.assertEqual(audit.classify(fetched("bbb"), None, self.URL), audit.NOT_BASELINED)
        self.assertEqual(audit.classify(fetched("bbb"), entry(digest=None), self.URL), audit.NOT_BASELINED)

    def test_a_baseline_for_another_address_does_not_apply(self):
        self.assertEqual(audit.classify(fetched("bbb"), entry(url="https://example.test/old"), self.URL),
                         audit.NOT_BASELINED)

    def test_blocked_stays_blocked_with_or_without_a_baseline(self):
        blocked = {"state": audit.BLOCKED, "note": "x"}
        self.assertEqual(audit.classify(blocked, None, self.URL), audit.BLOCKED)
        self.assertEqual(audit.classify(blocked, entry(digest=None), self.URL), audit.BLOCKED)


class BaselineHandling(unittest.TestCase):
    def test_an_entry_records_what_the_tool_saw(self):
        src = {"id": "T1", "url": "https://example.test/a", "checked": "2026-11-10"}
        made = audit.baseline_entry(src, fetched("abc", "bytes"), "2026-11-15")
        self.assertEqual(made, {"id": "T1", "url": src["url"], "fetched": "2026-11-15", "state": "fetched",
                                "mode": "bytes", "sha256": "abc", "length": 3, "registry_checked": "2026-11-10"})
        blocked = audit.baseline_entry(src, {"state": audit.BLOCKED, "note": "403"}, "2026-11-15")
        self.assertIsNone(blocked["sha256"])
        self.assertEqual(blocked["note"], "403")

    def test_a_refresh_keeps_a_hash_it_cannot_replace(self):
        old = {"T1": entry("T1", "aaa"), "T2": entry("T2", "bbb"), "GONE": entry("GONE", "ccc")}
        fresh = {"T1": entry("T1", None), "T2": entry("T2", "new")}
        merged, kept = audit.merge_baseline(old, fresh, ["T1", "T2"])
        self.assertEqual([item["sha256"] for item in merged], ["aaa", "new"])
        self.assertEqual(kept, ["T1"])

    def test_a_refresh_does_not_keep_a_hash_for_an_old_address(self):
        old = {"T1": entry("T1", "aaa", url="https://example.test/old")}
        merged, kept = audit.merge_baseline(old, {"T1": entry("T1", None)}, ["T1"])
        self.assertIsNone(merged[0]["sha256"])
        self.assertEqual(kept, [])

    def test_refreshing_one_source_leaves_the_others(self):
        old = {"T1": entry("T1", "aaa"), "T2": entry("T2", "bbb")}
        merged, _ = audit.merge_baseline(old, {"T2": entry("T2", "new")}, ["T1", "T2"])
        self.assertEqual([item["sha256"] for item in merged], ["aaa", "new"])

    def test_a_snapshot_counts_only_if_it_is_the_baseline_text(self):
        folder = Path(tempfile.mkdtemp(prefix="stasis-audit-test-"))
        self.addCleanup(shutil.rmtree, folder, ignore_errors=True)
        _, text, digest, _ = audit.normalize(b"<html><p>Hello</p></html>", "text/html")
        audit.save_snapshot(folder, "T/1", text)
        self.assertEqual(audit.load_snapshot(folder, "T/1", digest), "Hello")
        self.assertIsNone(audit.load_snapshot(folder, "T/1", "another hash"))
        self.assertIsNone(audit.load_snapshot(folder, "T2", digest))


class Exposure(unittest.TestCase):
    CLAIMS = [
        {"id": "X-START", "sources": ["T1", "T2"]},
        {"id": "X-HOURS", "sources": ["T2"]},
        {"id": "X-DESIGN", "sources": []},
    ]
    USAGE = {"X-START": ["oregon/rules.html", "oregon/index.html"], "X-HOURS": ["oregon/log.html"]}

    def test_names_the_claims_that_cite_a_source_and_their_pages(self):
        self.assertEqual(audit.exposure("T1", self.CLAIMS, self.USAGE),
                         [("X-START", ["oregon/index.html", "oregon/rules.html"])])
        self.assertEqual([claim for claim, _ in audit.exposure("T2", self.CLAIMS, self.USAGE)], ["X-START", "X-HOURS"])
        self.assertEqual(audit.exposure("T9", self.CLAIMS, self.USAGE), [])

    def test_the_mapping_matches_the_build(self):
        # docs/claims.md is written by the build, with the pages that use each claim.
        usage = audit.claim_pages()
        rows = [line.split(" | ") for line in (audit.ROOT / "docs" / "claims.md").read_text(encoding="utf-8").splitlines()
                if line.startswith("| ") and not line.startswith(("| ID", "|---"))]
        self.assertGreater(len(rows), 300)
        for row in rows:
            claim_id, pages = row[0][2:], row[5]
            self.assertEqual(len(usage[claim_id]), len(pages.split(", ")), claim_id)
        # A shared page is named with the guide's copy that shows the claim.
        self.assertIn("shared/about.html (as utah-about)", usage["U-NEW-GUIDE"])
        self.assertIn("oregon/rules.html", usage["C-HH-OPTION"])


def make_handler(site: dict, hits: list):
    """site: {path: (status, content type, body)}, plus "robots" text or None."""
    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def answer(self, method: str):
            hits.append((method, self.path))
            if self.path == "/robots.txt":
                status, kind, body = (200, "text/plain", site["robots"].encode()) if site.get("robots") else (404, "", b"")
            else:
                status, kind, body = site.get(self.path, (404, "text/plain", b"gone"))
            self.send_response(status)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if method == "GET":
                self.wfile.write(body)

        def do_HEAD(self):
            self.answer("HEAD")

        def do_GET(self):
            self.answer("GET")

    return Handler


class CutShort(unittest.TestCase):
    """A reply that stops partway is asked for once more, and never compared."""

    class Reply:
        headers = {"Content-Type": "text/html"}

        def __init__(self, body):
            self.body = body

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, limit):
            if self.body is None:
                raise http.client.IncompleteRead(b"<p>half a pa")
            return self.body

    def fetch(self, get_bodies):
        asked = []

        def open_url(request):
            asked.append(request.get_method())
            return self.Reply(b"" if request.get_method() == "HEAD" else get_bodies.pop(0))

        with mock.patch.object(audit.links, "open_url", open_url), mock.patch.object(audit.links, "PAUSE", 0):
            return audit.fetch("https://example.invalid/page"), asked

    def test_a_cut_short_reply_is_asked_for_once_more(self):
        result, asked = self.fetch([None, b"<html><p>All of it</p></html>"])
        self.assertEqual(asked, ["HEAD", "GET", "GET"])
        self.assertEqual((result["state"], result["text"]), (audit.FETCHED, "All of it"))

    def test_two_cut_short_replies_are_unreachable_and_nothing_is_hashed(self):
        result, asked = self.fetch([None, None])
        self.assertEqual(asked, ["HEAD", "GET", "GET"])
        self.assertEqual(result["state"], audit.UNREACHABLE)
        self.assertIn("asked twice", result["note"])
        self.assertNotIn("sha256", result)


class WholeTool(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="stasis-audit-test-"))
        cls.addClassCleanup(shutil.rmtree, cls.tmp, ignore_errors=True)
        cls.hits: list = []
        cls.servers: list = []
        cls.addClassCleanup(lambda: [server.shutdown() for server in cls.servers])

        # The tool must reach the test servers directly, not through a proxy,
        # must not pause between requests, and must start with no memory of
        # other sites' robots.txt files.
        clean = {key: value for key, value in os.environ.items() if "proxy" not in key.lower()}
        for patcher in (mock.patch.dict(os.environ, clean, clear=True),
                        mock.patch.object(urllib.request, "_opener", None),
                        mock.patch.object(audit.links, "PAUSE", 0),
                        mock.patch.object(audit.links, "ROBOTS", {}),
                        mock.patch.object(audit.links, "UNVERIFIABLE_HOSTS", set())):
            patcher.start()
            cls.addClassCleanup(patcher.stop)

        html = "text/html; charset=utf-8"
        cls.site = {
            "/same": (200, html, (PAGE % ("run 1", "School counts")).encode()),
            "/moving": (200, html, (PAGE % ("x", "School counts")).encode()),
            "/form.pdf": (200, "application/pdf", b"%PDF-1.7 first version"),
            "/refused": (403, "text/plain", b"no"),
            "/later": (200, html, b"<html><body><p>Added later</p></body></html>"),
        }
        open_port = cls.serve(cls.site)
        ruled = cls.serve({"/private/a": (200, html, b"<p>x</p>"), "robots": "User-agent: *\nDisallow: /private/\n"})

        def source(source_id, url, **extra):
            return dict(id=source_id, url=url, short=f"Test source {source_id}", checked="2026-11-10", **extra)

        base = f"http://127.0.0.1:{open_port}"
        cls.registry = {"sources": [
            source("T-SAME", f"{base}/same"),
            # S41 is a real id, so the report can name the real claims and pages that rest on it.
            source("S41", f"{base}/moving"),
            source("T-PDF", f"{base}/form.pdf"),
            source("T-403", f"{base}/refused"),
            source("T-ROBOTS", f"http://127.0.0.1:{ruled}/private/a"),
            source("T-DOWN", "http://127.0.0.1:9/closed-port"),
            source("T-GONE", f"{base}/gone"),
            source("T-HAND", f"{base}/never-requested", link_check="by hand"),
        ]}
        cls.registry_path = cls.tmp / "registry.json"
        cls.baseline_path = cls.tmp / "baseline.json"
        cls.common = ["--registry", str(cls.registry_path), "--baseline", str(cls.baseline_path),
                      "--snapshots", str(cls.tmp / "snapshots")]
        cls.write_registry()

        # 1. Write the baseline.
        cls.baseline_code, cls.baseline_out = cls.run_tool("--write-baseline", "--today", "2026-11-15")
        cls.baseline_text = cls.baseline_path.read_text(encoding="utf-8")
        cls.baseline = {item["id"]: item for item in json.loads(cls.baseline_text)["sources"]}

        # 2. Nothing changed, except scripts and markup on one page.
        cls.site["/same"] = (200, html, (PAGE % ("run 2", "School counts")).replace("<b>", "<em>").encode())
        cls.quiet_code, cls.quiet_report = cls.run_tool("--report", str(cls.tmp / "quiet.md"), "--today", "2026-11-16")

        # 3. One page's words change, the PDF is replaced, and a source is added.
        cls.site["/moving"] = (200, html, (PAGE % ("x", "School no longer counts")).encode())
        cls.site["/form.pdf"] = (200, "application/pdf", b"%PDF-1.7 second version")
        cls.registry["sources"].append(source("T-NEW", f"{base}/later"))
        cls.write_registry()
        cls.code, cls.report = cls.run_tool("--report", str(cls.tmp / "report.md"),
                                            "--results", str(cls.tmp / "results.json"), "--today", "2026-11-23")
        cls.results = {item["id"]: item for item in
                       json.loads((cls.tmp / "results.json").read_text(encoding="utf-8"))["results"]}

    @classmethod
    def write_registry(cls):
        cls.registry_path.write_text(json.dumps(cls.registry), encoding="utf-8")

    @classmethod
    def serve(cls, site: dict) -> int:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), make_handler(site, cls.hits))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        cls.servers.append(server)
        return server.server_address[1]

    @classmethod
    def run_tool(cls, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = audit.main([*cls.common, *args])
        return code, out.getvalue()

    def part(self, heading: str) -> str:
        self.assertIn(f"\n## {heading}", self.report)
        return self.report.split(f"\n## {heading}")[1].split("\n## ")[0]

    def test_the_baseline_records_each_source(self):
        self.assertEqual(self.baseline_code, 0)
        self.assertEqual(list(self.baseline), ["T-SAME", "S41", "T-PDF", "T-403", "T-ROBOTS", "T-DOWN", "T-GONE", "T-HAND"])
        same = self.baseline["T-SAME"]
        self.assertEqual((same["state"], same["mode"], same["fetched"], same["registry_checked"]),
                         ("fetched", "text", "2026-11-15", "2026-11-10"))
        self.assertEqual(len(same["sha256"]), 64)
        self.assertEqual(self.baseline["T-PDF"]["mode"], "bytes")
        self.assertEqual(self.baseline["T-PDF"]["length"], len(b"%PDF-1.7 first version"))
        for source_id, state in (("T-403", "checker-blocked"), ("T-ROBOTS", "checker-blocked"),
                                 ("T-HAND", "checker-blocked"), ("T-DOWN", "unreachable"), ("T-GONE", "unreachable")):
            self.assertEqual(self.baseline[source_id]["state"], state, source_id)
            self.assertIsNone(self.baseline[source_id]["sha256"], source_id)
        self.assertIn("fetched: 3", self.baseline_out)
        self.assertIn("checker-blocked: 3", self.baseline_out)
        self.assertIn("unreachable: 2", self.baseline_out)

    def test_a_run_with_no_change_passes(self):
        # Blocked and unreachable sources are reported and do not fail the run.
        self.assertEqual(self.quiet_code, 0)
        self.assertIn("| Changed | 0 |", self.quiet_report)
        self.assertIn("| Unchanged | 3 |", self.quiet_report)

    def test_a_changed_source_fails_the_run_and_shows_what_changed(self):
        self.assertEqual(self.code, 1)
        changed = self.part("Changed (2)")
        self.assertIn("### S41:", changed)
        self.assertIn("```diff", changed)
        self.assertIn("-School counts", changed)
        self.assertIn("+School no longer counts", changed)

    def test_a_changed_source_names_its_claims_and_pages(self):
        changed = self.part("Changed (2)").split("### T-PDF")[0]
        self.assertIn("C-HH-OPTION: ", changed)
        self.assertIn("oregon/rules.html", changed)
        self.assertIn("WA-HH-04: washington/washington-rules.html", changed)

    def test_a_changed_pdf_is_reported_as_lower_confidence(self):
        pdf = self.part("Changed (2)").split("### T-PDF")[1]
        self.assertIn("Lower confidence", pdf)
        self.assertNotIn("```diff", pdf)
        self.assertIn("No fact in data/claims.json cites it", pdf)

    def test_blocked_is_never_called_dead_or_removed(self):
        blocked = self.part("Checker-blocked (3)")
        for source_id in ("T-403", "T-ROBOTS", "T-HAND"):
            self.assertIn(f"- {source_id}:", blocked)
        self.assertIn("not a dead link and not a removed document", blocked)
        self.assertEqual(self.results["T-403"]["state"], "checker-blocked")
        for source_id in ("T-403", "T-ROBOTS", "T-HAND"):
            self.assertNotIn(source_id, self.part("Unreachable (2)"))
            self.assertNotIn(source_id, self.part("Changed (2)"))

    def test_unreachable_means_no_answer_or_a_server_error(self):
        unreachable = self.part("Unreachable (2)")
        self.assertIn("- T-DOWN:", unreachable)
        self.assertIn("- T-GONE:", unreachable)
        self.assertIn("404", unreachable)

    def test_a_source_with_no_stored_hash_is_not_yet_baselined_and_not_a_change(self):
        waiting = self.part("Not yet baselined (6)")
        self.assertIn("- T-NEW:", waiting)
        self.assertIn("readable now", waiting)
        self.assertIn("- T-403:", waiting)
        self.assertEqual(self.results["T-NEW"]["state"], "not yet baselined")
        self.assertNotIn("T-NEW", self.part("Changed (2)"))

    def test_unchanged_is_a_hash_match(self):
        self.assertIn("T-SAME", self.part("Unchanged (1)"))
        self.assertEqual(self.results["T-SAME"]["state"], "unchanged")
        self.assertEqual(self.results["T-SAME"]["sha256"], self.baseline["T-SAME"]["sha256"])

    def test_every_source_has_exactly_one_state(self):
        self.assertEqual(len(self.results), len(self.registry["sources"]))
        self.assertEqual({item["state"] for item in self.results.values()},
                         {"unchanged", "changed", "unreachable", "checker-blocked", "not yet baselined"})

    def test_comparing_never_rewrites_the_baseline(self):
        self.assertEqual(self.baseline_path.read_text(encoding="utf-8"), self.baseline_text)

    def test_a_by_hand_entry_and_a_robots_refusal_are_never_requested(self):
        self.assertFalse([hit for hit in self.hits if "never-requested" in hit[1] or hit[1] == "/private/a"])

    def test_head_then_get(self):
        asked = [method for method, path in self.hits if path == "/same"]
        self.assertEqual(asked[:2], ["HEAD", "GET"])

    def test_an_unknown_id_is_refused(self):
        code, _ = self.run_tool("--only", "NOPE")
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
