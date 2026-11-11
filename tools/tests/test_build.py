"""
Tests for the rules in tools/build.py that keep each guide whole.

    python3 -m unittest discover -s tools/tests

Each test copies src/pages and data to a temporary folder, breaks one
thing, and confirms the build stops with a message that names the problem.
The last test adds a third guide to the copy, to prove the build, the
state switch, the footers, and the "page not found" page all follow the
guide list and nothing still assumes two states.

Standard library only.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

import build  # noqa: E402


class BuildCase(unittest.TestCase):
    """Run the build against a throwaway copy of the page sources and data."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="stasis-build-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        shutil.copytree(build.SRC, self.tmp / "pages")
        shutil.copytree(build.DATA, self.tmp / "data")
        for name, value in (("SRC", self.tmp / "pages"), ("DATA", self.tmp / "data")):
            patcher = mock.patch.object(build, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def page(self, relative: str) -> Path:
        return self.tmp / "pages" / relative

    def edit(self, relative: str, old: str, new: str):
        path = self.page(relative)
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text, f"{relative} no longer contains {old!r}; update this test")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def edit_json(self, name: str, change):
        path = self.tmp / "data" / name
        data = json.loads(path.read_text(encoding="utf-8"))
        change(data)
        path.write_text(json.dumps(data), encoding="utf-8")

    def assertBuildFails(self, *fragments: str):
        with self.assertRaises(build.BuildError) as caught:
            build.build()
        message = str(caught.exception)
        for fragment in fragments:
            self.assertIn(fragment, message)


class CopyBuildsClean(BuildCase):
    def test_untouched_copy_builds_and_matches_the_committed_site(self):
        outputs = build.build()
        for path, content in outputs.items():
            self.assertEqual(path.read_text(encoding="utf-8"), content, f"{path.name} is out of date")

    def test_every_guide_home_page_has_the_state_switch(self):
        outputs = build.build()
        for name, guide in build.GUIDES.items():
            html = outputs[build.SITE / f"{guide['home']}.html"]
            self.assertEqual(html.count('class="guide-state"'), len(build.GUIDES), name)
            self.assertEqual(html.count('aria-current="page"><span class="guide-state"'), 1, name)


class GuidesStayWhole(BuildCase):
    def test_a_page_cannot_list_another_guides_source(self):
        self.edit("utah/utah.html", "sources: ", "sources: S01, ")
        self.assertBuildFails("utah/utah.html: lists S01, a source that belongs to the oregon guide")

    def test_a_page_cannot_use_another_guides_fact(self):
        self.edit("oregon/index.html", "<h1>", '<p data-claim="U-START">x</p>\n    <h1>')
        self.assertBuildFails("oregon/index.html: uses U-START, a fact that belongs to the utah guide")

    def test_a_page_cannot_link_inside_another_guide(self):
        self.edit("oregon/index.html", "<h1>", '<p><a href="utah-apply.html">x</a></p>\n    <h1>')
        self.assertBuildFails("oregon/index.html: links to utah-apply.html, a page in another guide")

    def test_a_page_may_link_to_another_guides_home_page(self):
        self.edit("oregon/apply.html", "<h1>", '<p><a href="utah.html">x</a></p>\n    <h1>')
        build.build()

    def test_a_page_cannot_link_to_another_states_paper_forms(self):
        registry = json.loads((self.tmp / "data" / "sources.json").read_text(encoding="utf-8"))
        form = registry["application_languages"]["items"][1]["url"]
        self.edit("utah/utah.html", "<h1>", f'<p><a href="{form}">x</a></p>\n    <h1>')
        self.assertBuildFails("utah/utah.html: links to another state's source")

    def test_a_fact_cannot_rely_on_another_guides_source(self):
        def change(ledger):
            claim = next(c for c in ledger["claims"] if c["id"] == "U-START")
            claim["sources"].append("S01")
        self.edit_json("claims.json", change)
        self.assertBuildFails("claim U-START: relies on S01, a source that belongs to the oregon guide")


class EveryEntryNamesItsGuide(BuildCase):
    def test_a_source_needs_a_guide(self):
        self.edit_json("sources.json", lambda registry: registry["sources"][0].pop("guide"))
        self.assertBuildFails("'guide' must be one of all, oregon, utah")

    def test_a_source_cannot_name_an_unknown_guide(self):
        self.edit_json("sources.json", lambda registry: registry["sources"][0].update(guide="idaho"))
        self.assertBuildFails("'guide' must be one of all, oregon, utah")

    def test_a_fact_needs_a_guide(self):
        self.edit_json("claims.json", lambda ledger: ledger["claims"][0].pop("guide"))
        self.assertBuildFails("claim C-STATE-DOCS: 'guide' must be one of")


class FoldersDecideTheGuide(BuildCase):
    def test_a_page_outside_a_folder_is_refused(self):
        shutil.copy(self.page("oregon/apply.html"), self.page("apply.html"))
        self.assertBuildFails("apply.html: pages live in a folder")

    def test_a_page_cannot_claim_a_different_guide_than_its_folder(self):
        self.edit("utah/utah-apply.html", "slug: utah-apply\n", "slug: utah-apply\nsection: oregon\n")
        self.assertBuildFails("utah/utah-apply.html: says section 'oregon' but sits in the utah folder")

    def test_an_unknown_folder_is_refused(self):
        (self.tmp / "pages" / "idaho").mkdir()
        shutil.copy(self.page("oregon/apply.html"), self.page("idaho/apply.html"))
        self.assertBuildFails("idaho/apply.html: unknown folder")

    def test_each_guide_needs_its_not_found_part(self):
        self.page("utah/_not-found.html").unlink()
        self.assertBuildFails("the utah guide needs src/pages/utah/_not-found.html")

    def test_each_guide_home_page_needs_the_state_switch(self):
        self.edit("utah/utah.html", "{{GUIDE_SWITCH}}\n", "")
        self.assertBuildFails("utah/utah.html: a guide's home page needs {{GUIDE_SWITCH}}")


WASHINGTON = {
    "state": "Washington",
    "tagline": "Apple Health, made plain",
    "prefix": "washington-",
    "shared_order": 60,
    "home": "washington",
    "nav": [("washington", "Washington home"), ("washington-check", "Check")],
    "facts_iso": "2026-12-01",
    "footer_why": "Test words.",
    "footer_independent": "Test words.",
    "about_label": "Why this guide exists",
    "guide_label": "Apple Health guide",
    "switch_here": "This is the Apple Health guide.",
    "switch_go": "Go to the Apple Health guide",
    "source_groups": [
        ("Washington sources", "washington-sources", "own"),
        ("Federal, court, and site sources", "other-sources", "shared, used"),
    ],
    "check": "washington-check",
    "check_care_reason": "care",
    "own_words": ["Apple Health"],
}


class AThirdGuide(BuildCase):
    """Add a made-up Washington guide to the copy and build all three."""

    def add_washington(self):
        for target in (build.SECTIONS, build.GUIDES):
            patcher = mock.patch.dict(target, {"washington": WASHINGTON})
            patcher.start()
            self.addCleanup(patcher.stop)

        def add_sources(registry):
            for number in range(1, 14):
                registry["sources"].append({
                    "id": f"W{number:02d}", "guide": "washington", "title": f"Test paper {number}",
                    "short": "Test", "publisher": "Test publisher", "url": f"https://example.org/wa/{number}",
                    "format": "Web page", "kind": "state-explainer", "date_on_document": "No date shown",
                    "checked": "2026-12-01", "opened": True, "notes": "Test entry.",
                })
        self.edit_json("sources.json", add_sources)

        folder = self.tmp / "pages" / "washington"
        folder.mkdir()
        (folder / "washington.html").write_text(
            "<!--\nslug: washington\norder: 59\ntitle: Test home\nshort_title: Washington home\n"
            "description: Test.\nsources: W01\n-->\n{{GUIDE_SWITCH}}\n    <h1>Test home</h1>\n"
            "    <p>We have found {{DOC_COUNT}} so far.</p>\n",
            encoding="utf-8",
        )
        (folder / "washington-check.html").write_text(
            "<!--\nslug: washington-check\norder: 60\ntitle: Test check\nshort_title: Check\n"
            "description: Test.\n-->\n    <h1>Test check</h1>\n",
            encoding="utf-8",
        )
        (folder / "_not-found.html").write_text(
            '    <h2>Apple Health</h2>\n    <ul class="cards">\n'
            '      <li><a href="washington.html">Washington home page</a></li>\n    </ul>\n',
            encoding="utf-8",
        )

        # A shared page lists sources. Each guide's copy needs its own list,
        # because it may not list another state's.
        registry = json.loads((self.tmp / "data" / "sources.json").read_text(encoding="utf-8"))
        shared_ids = {s["id"] for s in registry["sources"] if s["guide"] == "all"}
        for path in sorted((self.tmp / "pages" / "shared").glob("*.html")):
            text = path.read_text(encoding="utf-8")
            if "shared: yes" not in text:
                continue
            listed = next((line for line in text.splitlines() if line.startswith("utah_sources:")), None) \
                or next((line for line in text.splitlines() if line.startswith("sources:")), "sources:")
            keep = [s.strip() for s in listed.split(":", 1)[1].split(",") if s.strip() in shared_ids]
            path.write_text(text.replace("shared: yes\n", "shared: yes\nwashington_sources: " + ", ".join(keep) + "\n", 1),
                            encoding="utf-8")

    def test_without_its_own_source_lists_a_new_guide_is_refused(self):
        self.add_washington()
        about = self.page("shared/about.html")
        text = about.read_text(encoding="utf-8")
        about.write_text("\n".join(l for l in text.splitlines() if not l.startswith("washington_sources:")) + "\n",
                         encoding="utf-8")
        self.assertBuildFails("shared/about.html (as washington-about): lists", "a source that belongs to the oregon guide")

    def test_three_guides_build_and_every_part_follows_the_list(self):
        self.add_washington()
        outputs = build.build()
        site = {path.name: text for path, text in outputs.items() if path.parent == build.SITE}

        # The new guide's pages, and its own copies of the shared pages.
        for name in ("washington.html", "washington-check.html", "washington-about.html",
                     "washington-privacy.html", "washington-accessibility.html", "washington-sources.html"):
            self.assertIn(name, site)

        # The state switch on every home page shows three states, in order,
        # with the reader's own guide marked.
        for home, here in (("index.html", "Oregon"), ("utah.html", "Utah"), ("washington.html", "Washington")):
            html = site[home]
            states = [part.split("<")[0] for part in html.split('<span class="guide-state">')[1:]]
            self.assertEqual(states, ["Oregon", "Utah", "Washington"], home)
            self.assertIn(f'aria-current="page"><span class="guide-state">{here}</span>', html)
        self.assertIn("Go to the Apple Health guide", site["index.html"])
        self.assertIn("This is the Apple Health guide.", site["washington.html"])

        # Every footer links to the other two guides, and only those.
        utah_footer = site["utah-apply.html"].split('<nav class="footer-pages"')[1]
        self.assertIn(">Oregon Health Plan guide</a>", utah_footer)
        self.assertIn(">Apple Health guide</a>", utah_footer)
        self.assertNotIn(">Utah Medicaid guide</a>", utah_footer)

        # The "page not found" page lists all three guides.
        for heading in ("Oregon Health Plan (OHP)", "Utah Medicaid", "Apple Health"):
            self.assertIn(f"<h2>{heading}</h2>", site["404.html"])

        # Counts and source lists are each guide's own.
        self.assertIn("We have found 13 so far.", site["washington.html"])
        self.assertIn('<h2 id="washington-sources">Washington sources</h2>', site["washington-sources.html"])
        self.assertNotIn("oregon.gov", site["washington-sources.html"])
        self.assertNotIn("example.org/wa/", site["sources.html"])
        self.assertNotIn("example.org/wa/", site["utah-sources.html"])

        # The existing guides' pages are the same as before, except where
        # they name the other guides: the switch, the footer, and the
        # "page not found" page.
        untouched = (build.SITE / "utah-apply.html").read_text(encoding="utf-8")
        self.assertEqual(site["utah-apply.html"].split('<nav class="footer-pages"')[0],
                         untouched.split('<nav class="footer-pages"')[0])


if __name__ == "__main__":
    unittest.main()
