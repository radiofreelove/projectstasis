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
import hashlib
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

# The hash of the comparison-rules block, the same in both projects (see OneSetOfRules).
RULES_BLOCK_SHA256 = "1e34858acd2a520b6c39ba569c912a4a17d5e465b2deb1f63ae765933b6dea1f"

PAGE = """<!doctype html>
<html><head><title>Work rules</title>
<style>p { color: red }</style>
<script>var stamp = "%s";</script></head>
<body><h1>Work   rules</h1>
<p>The rules start <b>Jan.&nbsp;1,
2027</b>.</p><ul><li>80 hours a month</li><li>%s</li></ul></body></html>
"""

# Every real source has well over audit.MIN_WORDS words; a reply with fewer is
# not taken as the source. Pages these tests have the tool fetch or carry
# forward get this paragraph, so they are the size of a real page.
ENOUGH = ("Adults who get Medicaid through the expansion group must show 80 hours a month of work, school, "
          "volunteering, or a work program, unless an exemption applies. People who are pregnant, care for a "
          "young child, are medically frail, or are in treatment for drug or alcohol use are exempt. Hours can "
          "be reported online, by phone, by mail, or in person, and free help is available.")
SERVED_PAGE = PAGE.replace("</ul></body>", "</ul><p>" + ENOUGH + "</p></body>")


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


# ---------------------------------------------------------------------------
# The comparison rules. Each class below copies one way an unchanged source
# looked changed in November 2026, and fails under the rules before RULES 2.

class LineBreaksAndSpaces(unittest.TestCase):
    """The same words, with the lines broken in other places, are the same text."""

    # The header of an Oregon.gov page, as two computers turned it into text.
    SPLIT = ("Skip to main content\nAn official website of the State of Oregon\nLearn\nHow you know »\n"
             "Please call 800-699-9075, go to\nBenefits.Oregon.gov, or\nvisit your local office.\nContact Us\n\u200b\nMedia")
    JOINED = ("Skip to main content\nAn official website of the State of Oregon Learn How you know »\n"
              "Please call 800-699-9075, go to Benefits.Oregon.gov, or visit your local office.\nContact Us\n\u200b Media")

    def test_where_lines_break_does_not_change_the_hash(self):
        self.assertEqual(audit.text_digest(self.SPLIT), audit.text_digest(self.JOINED))

    def test_the_hash_is_the_canonical_words(self):
        self.assertEqual(audit.canonical("A\n  b\tc\u00a0d \u200b\ne\u00ad"), "A b c d e")

    def test_a_changed_word_still_changes_the_hash(self):
        self.assertNotEqual(audit.text_digest(self.JOINED), audit.text_digest(self.JOINED.replace("800-699", "800-698")))

    def test_html_with_other_line_breaks_hashes_the_same(self):
        one = b"<html><body><p>Please call 800-699-9075, go to\n<a href=x>Benefits.Oregon.gov</a>, or visit.</p></body></html>"
        two = b"<html><body><p>Please call 800-699-9075, go to <a href=x>Benefits.Oregon.gov</a>,\n  or visit.</p></body></html>"
        self.assertEqual(audit.normalize(one, "text/html")[2], audit.normalize(two, "text/html")[2])

    def test_a_line_join_is_not_shown_as_a_change(self):
        self.assertEqual(audit.bounded_diff(self.SPLIT, self.JOINED), "")

    def test_a_changed_word_is_shown_with_its_line(self):
        diff = audit.bounded_diff(self.SPLIT, self.JOINED.replace("local office", "nearest office"))
        self.assertIn("-visit your local office.", diff)
        self.assertIn("+Please call 800-699-9075, go to Benefits.Oregon.gov, or visit your nearest office.", diff)
        self.assertNotIn("Learn", diff)

    def test_words_added_at_the_end_are_shown(self):
        diff = audit.bounded_diff("One\nTwo", "One Two\nThree\nFour")
        self.assertEqual(diff, "@@ after: One Two @@\n+Three\n+Four")


class WholeReplies(unittest.TestCase):
    """A reply that is not all there is never hashed."""

    def test_a_reply_shorter_than_its_content_length_is_cut_short(self):
        with self.assertRaises(audit.CutShort):
            audit.check_whole(b"<html><p>Where to send", "text/html", "118961")
        audit.check_whole(b"<html><p>All</p></html>", "text/html", "23")

    def test_a_pdf_without_a_length_must_end_with_its_marker(self):
        with self.assertRaises(audit.CutShort):
            audit.check_whole(b"%PDF-1.7\n1 0 obj", "application/pdf", None)
        audit.check_whole(b"%PDF-1.7\n1 0 obj\n%%EOF\n", "application/pdf", None)

    def test_the_same_cut_twice_is_cut_short_both_times(self):
        # U08, Nov. 2026: three of six fetches stopped at the same 81,642 of
        # 209,710 bytes. Under rules 1 two such fetches hashed the same, and the
        # PDF would have been called unchanged on a tenth of its bytes.
        part = b"%PDF-1.7\n" + b"x" * 81_633
        for _ in range(2):
            with self.assertRaises(audit.CutShort):
                audit.check_whole(part, "application/pdf", "209710")

    def test_a_whole_pdf_with_a_length_needs_no_marker(self):
        audit.check_whole(b"%PDF-1.7 x", "application/pdf", "10")

    def test_a_page_without_closing_tags_is_whole(self):
        # Some real pages end without </body> or </html>, and are whole.
        audit.check_whole(b"<!doctype html><html><body><p>News</p><style>.x{}</style>", "text/html", None)


class NotTheSource(unittest.TestCase):
    """A page that checks for automated visitors, or has no words, is never hashed."""

    def test_a_check_for_automated_visitors_is_checker_blocked(self):
        body = b"<html><body><h1>One moment, please...</h1><p>Please wait while your request is being verified...</p></body></html>"
        result = audit.examine(body, "text/html", str(len(body)))
        self.assertEqual(result["state"], audit.BLOCKED)
        self.assertNotIn("sha256", result)
        self.assertIn("check for automated visitors", result["note"])

    def test_a_captcha_page_is_checker_blocked(self):
        body = (b"<html><body><p>Your request has been flagged as potentially automated. If you are human user "
                b"receiving this message, please complete the CAPTCHA</p></body></html>")
        self.assertEqual(audit.examine(body, "text/html", None)["state"], audit.BLOCKED)

    def test_a_page_with_no_words_is_checker_blocked(self):
        body = (b'<html><head><meta http-equiv="refresh" content="0;/.well-known/sgcaptcha/?r=%2F"></meta>'
                b"</head></html>")
        result = audit.examine(body, "text/html", None)
        self.assertEqual(result["state"], audit.BLOCKED)
        self.assertIn("no readable words", result["note"])

    def test_a_page_too_short_to_be_the_source_is_checker_blocked(self):
        # A check page in words no list has yet. Hashed, it would match itself
        # on the next fetch, and the source would be called unchanged unread.
        body = b"<html><body><noscript></noscript><div id=root>You need to enable JavaScript to run this app.</div></body></html>"
        result = audit.examine(body, "text/html", str(len(body)))
        self.assertEqual(result["state"], audit.BLOCKED)
        self.assertNotIn("sha256", result)
        self.assertIn("only 9 words", result["note"])

    def test_the_same_check_page_twice_is_never_unchanged(self):
        # S27, Nov. 2026: the baseline and the next fetch were the same CAPTCHA
        # page, with lines broken differently. Under rules 1 only the line breaks
        # made it "changed"; with them ignored it would have been "unchanged".
        page = ("<html><body><h1>Request Access</h1><p>Due to aggressive automated scraping of FederalRegister.gov "
                "and eCFR.gov, programmatic access to these sites is limited to access to our extensive developer "
                "APIs.</p><p>Your request has been flagged as potentially automated. If you are human user receiving "
                "this message, please complete the CAPTCHA (bot test) below and click \"Request Access\". You may "
                "occassionally be asked to complete the CAPTCHA again, this is normal and part of our security "
                "measures.</p></body></html>")
        for body in (page, page.replace(" ", "\n", 9)):
            self.assertEqual(audit.examine(body.encode(), "text/html", None)["state"], audit.BLOCKED)

    def test_other_common_checks_are_checker_blocked(self):
        for words in ("Just a moment... Verifying you are human. This may take a few seconds. example.gov needs to "
                      "review the security of your connection before proceeding.",
                      "Request unsuccessful. Incapsula incident ID: 1234-5678",
                      "Pardon Our Interruption. As you were browsing something about your browser made us think "
                      "you were a bot."):
            body = f"<html><body><p>{words}</p></body></html>".encode()
            self.assertEqual(audit.examine(body, "text/html", None)["state"], audit.BLOCKED, words)

    def test_the_shortest_real_source_is_read(self):
        # The shortest source text in November 2026 (U22) had 165 words.
        body = ("<html><body><p>" + " ".join([ENOUGH] * 3) + "</p></body></html>").encode()
        self.assertGreaterEqual(len(audit.canonical(audit.html_text(body.decode())).split()), 165)
        self.assertEqual(audit.examine(body, "text/html", None)["state"], audit.FETCHED)

    def test_a_long_page_that_quotes_a_phrase_is_read(self):
        body = ("<html><body><p>" + "Words. " * 600 + "verify you are human</p></body></html>").encode()
        self.assertEqual(audit.examine(body, "text/html", None)["state"], audit.FETCHED)

    def test_a_pdf_is_never_called_a_check_page(self):
        body = b"%PDF-1.7\n%%EOF"
        self.assertEqual(audit.examine(body, "application/pdf", None)["mode"], "bytes")


class RulesVersions(unittest.TestCase):
    """A hash written under other rules is never compared, and can be carried forward."""
    URL = "https://example.test/a"
    TEXT = "Work rules\nThe rules start\nJan. 1, 2027.\n" + ENOUGH

    def old(self, text=TEXT, **extra):
        """An entry as the tool wrote it before RULES: no "rules", the saved text hashed as it was."""
        return dict({"id": "T1", "url": self.URL, "fetched": "2026-11-15", "state": audit.FETCHED, "mode": "text",
                     "sha256": hashlib.sha256(text.encode()).hexdigest(), "length": len(text)}, **extra)

    def test_an_old_rules_entry_is_not_yet_baselined_never_changed(self):
        now = {"state": audit.FETCHED, "mode": "text", "text": self.TEXT, "sha256": audit.text_digest(self.TEXT)}
        self.assertEqual(audit.classify(now, self.old(), self.URL), audit.NOT_BASELINED)
        self.assertTrue(audit.older_rules(self.old(), self.URL))

    def test_a_refresh_keeps_an_old_rules_hash_it_cannot_replace(self):
        # Nov. 16, 2026: a refresh that could not read U01 and nine other sources
        # wrote "unreachable" over their only hashes. Kept, a hash can still be
        # carried forward or checked against the next whole fetch.
        blocked = {"id": "T1", "url": self.URL, "state": audit.UNREACHABLE, "sha256": None}
        merged, kept = audit.merge_baseline({"T1": self.old()}, {"T1": blocked}, ["T1"])
        self.assertEqual(merged[0], self.old())
        self.assertEqual(kept, ["T1"])
        # Kept, but still never compared.
        now = {"state": audit.FETCHED, "mode": "text", "sha256": audit.text_digest(self.TEXT)}
        self.assertEqual(audit.classify(now, merged[0], self.URL), audit.NOT_BASELINED)

    def test_a_refresh_still_drops_an_old_rules_hash_for_another_address(self):
        moved = {"id": "T1", "url": "https://example.test/new", "state": audit.UNREACHABLE, "sha256": None}
        merged, kept = audit.merge_baseline({"T1": self.old()}, {"T1": moved}, ["T1"])
        self.assertIsNone(merged[0]["sha256"])
        self.assertEqual(kept, [])

    def test_carrying_forward_rehashes_the_saved_text(self):
        carried, why = audit.carry_forward(self.old(), self.TEXT)
        self.assertIsNone(why)
        self.assertEqual((carried["rules"], carried["sha256"]), (audit.RULES, audit.text_digest(self.TEXT)))
        joined = {"state": audit.FETCHED, "mode": "text", "sha256": audit.text_digest(self.TEXT.replace("\n", " "))}
        self.assertEqual(audit.classify(joined, carried, self.URL), audit.UNCHANGED)

    def test_carrying_forward_needs_the_text_the_baseline_hashed(self):
        self.assertIsNone(audit.carry_forward(self.old(), "other words")[0])
        self.assertIsNone(audit.carry_forward(self.old(), None)[0])

    def test_a_check_page_is_never_carried_forward(self):
        page = "One moment, please...\nPlease wait while your request is being verified..."
        carried, why = audit.carry_forward(self.old(page), page)
        self.assertIsNone(carried)
        self.assertIn("not the source", why)

    def test_a_bytes_entry_is_never_carried_forward(self):
        # Under rules 1, 9 of the 37 PDF hashes were of replies cut short (U08:
        # 81,642 of 209,710 bytes). There is no saved copy to re-take a bytes
        # hash from, so it is written again from a whole fetch instead.
        carried, why = audit.carry_forward(self.old(mode="bytes"), None)
        self.assertIsNone(carried)
        self.assertIn("not known", why)

    def test_a_stub_is_never_carried_forward(self):
        stub = "Loading\nPlease enable JavaScript to view this page."
        carried, why = audit.carry_forward(self.old(stub), stub)
        self.assertIsNone(carried)
        self.assertIn("too few to be the source", why)


class EarlierHash(unittest.TestCase):
    """A fresh fetch that replaces a hash says whether it says what that hash said."""
    URL = "https://example.test/a"

    def old(self, digest, mode="text", rules=None):
        made = {"id": "T1", "url": self.URL, "fetched": "2026-11-15", "state": audit.FETCHED, "mode": mode,
                "sha256": digest}
        if rules:
            made["rules"] = rules
        return made

    def now(self, mode, digest):
        return {"state": audit.FETCHED, "mode": mode, "sha256": digest}

    def test_the_same_bytes_carry_the_check_forward(self):
        said = audit.compared_with_earlier(self.old("abc", "bytes"), self.now("bytes", "abc"), self.URL, None)
        self.assertEqual(said, "the same as the entry of 2026-11-15 (rules 1)")

    def test_a_cut_short_old_hash_is_reported_different(self):
        whole, part = b"%PDF-1.7 whole file %%EOF", b"%PDF-1.7 whole"
        said = audit.compared_with_earlier(self.old(hashlib.sha256(part).hexdigest(), "bytes"),
                                           self.now("bytes", hashlib.sha256(whole).hexdigest()), self.URL, None)
        self.assertTrue(said.startswith("different from the entry of 2026-11-15"))

    def test_old_text_is_compared_under_the_new_rules(self):
        split, joined = "Please call 800-699-9075, go to\nBenefits.Oregon.gov", "Please call 800-699-9075, go to Benefits.Oregon.gov"
        old = self.old(hashlib.sha256(split.encode()).hexdigest())
        self.assertTrue(audit.compared_with_earlier(old, self.now("text", audit.text_digest(joined)), self.URL,
                                                    split).startswith("the same as"))
        changed = audit.text_digest(joined.replace("699", "698"))
        self.assertTrue(audit.compared_with_earlier(old, self.now("text", changed), self.URL,
                                                    split).startswith("different from"))

    def test_without_the_old_text_it_is_not_known(self):
        said = audit.compared_with_earlier(self.old("abc"), self.now("text", "def"), self.URL, None)
        self.assertTrue(said.startswith("not known"))
        # Saved text that is not the text the old hash was taken from does not count.
        said = audit.compared_with_earlier(self.old("abc"), self.now("text", "def"), self.URL, "other words")
        self.assertTrue(said.startswith("not known"))

    def test_current_rules_hashes_are_compared_directly(self):
        self.assertTrue(audit.compared_with_earlier(self.old("abc", rules=audit.RULES), self.now("text", "abc"),
                                                    self.URL, None).startswith("the same as"))

    def test_nothing_to_say_without_an_earlier_hash_for_this_address(self):
        self.assertIsNone(audit.compared_with_earlier(None, self.now("text", "abc"), self.URL, None))
        self.assertIsNone(audit.compared_with_earlier(self.old("abc"), self.now("text", "abc"), "https://example.test/b", None))
        self.assertIsNone(audit.compared_with_earlier(self.old("abc"), {"state": audit.BLOCKED}, self.URL, None))


class RewriteRun(unittest.TestCase):
    """--write-baseline over an older baseline: what the Nov. 16, 2026 recapture
    needed. A source it cannot read keeps its old hash; a source it can read
    says whether it says what the old hash said."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="stasis-audit-test-"))
        cls.addClassCleanup(shutil.rmtree, cls.tmp, ignore_errors=True)
        clean = {key: value for key, value in os.environ.items() if "proxy" not in key.lower()}
        for patcher in (mock.patch.dict(os.environ, clean, clear=True),
                        mock.patch.object(urllib.request, "_opener", None),
                        mock.patch.object(audit.links, "PAUSE", 0),
                        mock.patch.object(audit.links, "ROBOTS", {}),
                        mock.patch.object(audit.links, "UNVERIFIABLE_HOSTS", set())):
            patcher.start()
            cls.addClassCleanup(patcher.stop)
        whole_pdf = b"%PDF-1.7\n" + b"x" * 200 + b"\n%%EOF\n"
        page = "<html><body><h1>Work rules</h1><p>" + ENOUGH + "</p></body></html>"
        hits: list = []
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), make_handler({
            "/same": (200, "text/html", page.encode()),
            "/moved-on": (200, "text/html", page.replace("80 hours", "100 hours").encode()),
            "/form.pdf": (200, "application/pdf", whole_pdf),
            "/refused": (403, "text/plain", b"no"),
        }, hits))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        cls.addClassCleanup(server.shutdown)
        base = f"http://127.0.0.1:{server.server_address[1]}"
        ids = {"T-SAME": "/same", "T-MOVED": "/moved-on", "T-PDF": "/form.pdf", "T-403": "/refused", "T-NEW": "/same"}
        registry = {"sources": [{"id": i, "url": base + path, "short": i, "checked": "2026-11-10"} for i, path in ids.items()]}
        (cls.tmp / "registry.json").write_text(json.dumps(registry), encoding="utf-8")
        # The rules-1 text as another computer saved it: the same words, lines broken elsewhere.
        old_text = "Work rules\n" + ENOUGH.replace(", ", ",\n")

        def old(source_id, digest, mode="text"):
            return {"id": source_id, "url": base + ids[source_id], "fetched": "2026-11-15", "state": "fetched",
                    "mode": mode, "sha256": digest, "length": 1, "registry_checked": "2026-11-10"}
        rules1 = hashlib.sha256(old_text.encode()).hexdigest()
        cls.before = {"T-SAME": old("T-SAME", rules1), "T-MOVED": old("T-MOVED", rules1),
                      "T-PDF": old("T-PDF", hashlib.sha256(whole_pdf[:120]).hexdigest(), "bytes"),
                      "T-403": old("T-403", rules1)}
        (cls.tmp / "baseline.json").write_text(json.dumps({"sources": list(cls.before.values())}), encoding="utf-8")
        for source_id in ("T-SAME", "T-MOVED", "T-403"):
            audit.save_snapshot(cls.tmp / "snapshots", source_id, old_text)
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            cls.code = audit.main(["--write-baseline", "--registry", str(cls.tmp / "registry.json"), "--baseline",
                                   str(cls.tmp / "baseline.json"), "--snapshots", str(cls.tmp / "snapshots"),
                                   "--today", "2026-11-17"])
        cls.out = out.getvalue()
        cls.after = {item["id"]: item for item in
                     json.loads((cls.tmp / "baseline.json").read_text(encoding="utf-8"))["sources"]}

    def test_a_source_it_cannot_read_keeps_its_old_hash(self):
        self.assertEqual(self.after["T-403"], self.before["T-403"])
        self.assertIn("Kept the earlier hash for sources that could not be read this time: T-403", self.out)

    def test_the_same_words_carry_the_check_forward(self):
        self.assertEqual(self.after["T-SAME"]["earlier"], "the same as the entry of 2026-11-15 (rules 1)")
        self.assertEqual(self.after["T-SAME"]["rules"], audit.RULES)

    def test_changed_words_are_named_for_a_person(self):
        self.assertTrue(self.after["T-MOVED"]["earlier"].startswith("different from the entry of 2026-11-15"))
        self.assertIn("a person reads these before the new hash is relied on: T-MOVED", self.out)

    def test_a_pdf_hashed_cut_short_before_is_named_for_a_person(self):
        self.assertTrue(self.after["T-PDF"]["earlier"].startswith("different from"))
        self.assertIn("T-MOVED, T-PDF", self.out)

    def test_a_first_hash_is_named_for_a_person(self):
        self.assertNotIn("earlier", self.after["T-NEW"])
        self.assertIn("A first hash, with no earlier one to compare (a person reads these first): T-NEW", self.out)


class OneSetOfRules(unittest.TestCase):
    """The comparison-rules block is the same in The Stasis Project and The Strand Project."""

    def test_the_block_is_the_shared_one(self):
        source = Path(audit.__file__).read_text(encoding="utf-8")
        begin = source.index("# ===========================================================================\n# The comparison rules (begin)")
        end = source.index("# The comparison rules (end)")
        block = source[begin:end]
        self.assertEqual(hashlib.sha256(block.encode("utf-8")).hexdigest(), RULES_BLOCK_SHA256,
                         "The comparison rules changed. Make the same change in the other project's audit, "
                         "raise RULES if a hash changes, and update RULES_BLOCK_SHA256 in both projects' tests.")


def fetched(digest="aaa", mode="text"):
    return {"state": audit.FETCHED, "mode": mode, "sha256": digest, "length": 3, "text": "abc"}


def entry(source_id="T1", digest="aaa", url="https://example.test/a", **extra):
    made = {"id": source_id, "url": url, "fetched": "2026-11-15", "state": audit.FETCHED if digest else
            audit.BLOCKED, "mode": "text" if digest else None, "sha256": digest,
            "length": 3 if digest else None, "registry_checked": "2026-11-10"}
    if digest:
        made["rules"] = audit.RULES
    return dict(made, **extra)


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
                                "mode": "bytes", "sha256": "abc", "length": 3, "registry_checked": "2026-11-10",
                                "rules": audit.RULES})
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
        result, asked = self.fetch([None, ("<html><p>All of it</p><p>" + ENOUGH + "</p></html>").encode()])
        self.assertEqual(asked, ["HEAD", "GET", "GET"])
        self.assertEqual((result["state"], result["text"]), (audit.FETCHED, "All of it\n" + ENOUGH))

    def test_two_cut_short_replies_are_unreachable_and_nothing_is_hashed(self):
        result, asked = self.fetch([None, None])
        self.assertEqual(asked, ["HEAD", "GET", "GET"])
        self.assertEqual(result["state"], audit.UNREACHABLE)
        self.assertIn("asked twice", result["note"])
        self.assertNotIn("sha256", result)


class StopsPartway(unittest.TestCase):
    """A server that announces a length, sends part of it, and closes. Python's
    read with a size limit returns the part without an error; the tool must
    not hash it."""

    @classmethod
    def setUpClass(cls):
        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_HEAD(self):
                self.send_response(200)
                self.end_headers()

            def do_GET(self):
                body = b"<html><body><p>Where to send your verification</p>" + b"<p>More</p>" * 50
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(body) * 3))
                self.end_headers()
                self.wfile.write(body)
                self.close_connection = True

        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.addClassCleanup(cls.server.shutdown)
        clean = {key: value for key, value in os.environ.items() if "proxy" not in key.lower()}
        for patcher in (mock.patch.dict(os.environ, clean, clear=True),
                        mock.patch.object(urllib.request, "_opener", None),
                        mock.patch.object(audit.links, "PAUSE", 0)):
            patcher.start()
            cls.addClassCleanup(patcher.stop)

    def test_python_returns_the_part_without_an_error(self):
        url = f"http://127.0.0.1:{self.server.server_address[1]}/page"
        with urllib.request.urlopen(url, timeout=10) as response:
            body = response.read(audit.MAX_BYTES + 1)
            self.assertLess(len(body), int(response.headers["Content-Length"]))

    def test_the_part_is_never_hashed(self):
        result = audit.fetch(f"http://127.0.0.1:{self.server.server_address[1]}/page")
        self.assertEqual(result["state"], audit.UNREACHABLE)
        self.assertIn("bytes it announced", result["note"])
        self.assertIn("asked twice", result["note"])
        self.assertNotIn("sha256", result)


class CarryForwardRun(unittest.TestCase):
    """--carry-forward re-hashes from saved text and fetches nothing."""

    def test_old_entries_are_carried_forward_from_their_saved_text(self):
        tmp = Path(tempfile.mkdtemp(prefix="stasis-audit-test-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        text, page = "Work rules\nThe rules start\n" + ENOUGH, "One moment, please...\nPlease wait while your request is being verified..."
        old = lambda source_id, words: {"id": source_id, "url": f"https://example.invalid/{source_id}",
                                        "fetched": "2026-11-15", "state": "fetched", "mode": "text",
                                        "sha256": hashlib.sha256(words.encode()).hexdigest(), "length": len(words),
                                        "registry_checked": "2026-11-10"}
        (tmp / "baseline.json").write_text(json.dumps({"sources": [old("T1", text), old("T2", page)]}), encoding="utf-8")
        (tmp / "registry.json").write_text(json.dumps({"sources": [
            {"id": source_id, "url": f"https://example.invalid/{source_id}", "short": source_id} for source_id in ("T1", "T2")]}),
            encoding="utf-8")
        for source_id, words in (("T1", text), ("T2", page)):
            audit.save_snapshot(tmp / "snapshots", source_id, words)
        with mock.patch.object(audit, "fetch", side_effect=AssertionError("nothing is fetched")), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            code = audit.main(["--carry-forward", "--baseline", str(tmp / "baseline.json"), "--registry",
                               str(tmp / "registry.json"), "--snapshots", str(tmp / "snapshots"), "--today", "2026-11-16"])
        self.assertEqual(code, 0)
        written = {item["id"]: item for item in json.loads((tmp / "baseline.json").read_text(encoding="utf-8"))["sources"]}
        self.assertEqual((written["T1"]["rules"], written["T1"]["sha256"]), (audit.RULES, audit.text_digest(text)))
        self.assertEqual(written["T1"]["fetched"], "2026-11-15")
        self.assertNotIn("rules", written["T2"])
        self.assertIn("T2: not carried forward (the baseline text is not the source", out.getvalue())


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
            "/same": (200, html, (SERVED_PAGE % ("run 1", "School counts")).encode()),
            "/moving": (200, html, (SERVED_PAGE % ("x", "School counts")).encode()),
            "/form.pdf": (200, "application/pdf", b"%PDF-1.7 first version"),
            "/refused": (403, "text/plain", b"no"),
            "/later": (200, html, ("<html><body><p>Added later</p><p>" + ENOUGH + "</p></body></html>").encode()),
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
        cls.site["/same"] = (200, html, (SERVED_PAGE % ("run 2", "School counts")).replace("<b>", "<em>").encode())
        cls.quiet_code, cls.quiet_report = cls.run_tool("--report", str(cls.tmp / "quiet.md"), "--today", "2026-11-16")

        # 3. One page's words change, the PDF is replaced, and a source is added.
        cls.site["/moving"] = (200, html, (SERVED_PAGE % ("x", "School no longer counts")).encode())
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
