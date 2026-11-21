#!/usr/bin/env python3
"""
Build The Stasis Project site.

    python3 tools/build.py           Write site/*.html, site/sitemap.xml,
                                     site/robots.txt, site/_headers,
                                     docs/sources.md, and docs/claims.md.
    python3 tools/build.py --check   Rebuild in memory and fail if any
                                     committed output is out of date.
    python3 tools/build.py --theme spacefast --out site-spacefast
                                     Write a Spacefast-themed static site to
                                     site-spacefast/ (using spacefast/theme.css,
                                     spacefast/logo.svg, and the Radix MIT
                                     license), leaving site/ and docs/ untouched.
                                     Also accepts SITE_THEME=spacefast.

Inputs
    src/pages/<guide>/*.html
                        Page bodies, each starting with a metadata comment.
                        The folder says which guide a page belongs to:
                        src/pages/oregon/, src/pages/washington/, and
                        src/pages/utah/ today. The guides themselves are
                        listed in SECTIONS below.
    src/pages/<guide>/_not-found.html
                        That guide's part of the "page not found" page: a
                        heading and its main links. No metadata comment.
    src/pages/shared/*.html
                        Pages every guide needs (About, Privacy,
                        Accessibility, Every source), marked "shared: yes".
                        A shared page is built once for each guide, as
                        "about", "washington-about", and "utah-about", so a
                        reader never leaves the guide they are in. Text between <!-- oregon -->
                        and <!-- /oregon --> (or any guide's name) appears
                        only in that guide's copy, and "<guide>_title",
                        "<guide>_description", and "<guide>_sources" (for
                        example "utah_title") replace the plain values in
                        that guide's copy. The "page not found" page lives
                        here too; it belongs to no guide.
    data/sources.json   Registry of every outside source and link. Each
                        entry's "guide" says which guide may use it:
                        a guide's name, or "all".
    data/claims.json    Ledger of every factual statement on the site, each
                        with a "guide" in the same way.

Placeholders a page body may use
    {{GUIDE_SWITCH}}          The "Pick your state" buttons. Every guide's
                              home page must have it.
    {{DOC_COUNT}}             How many state explainers this guide's
                              registry entries hold.
    {{SOURCES_TABLE}}         This guide's full source list.
    {{APPLICATION_LANGUAGES}} The paper application in each language.
    {{GUIDE_START_LISTS}}     Every guide's _not-found.html, in order.
    {{FACTS_CHECKED_TEXT}}, {{FACTS_CHECKED_ISO}}

The build refuses to finish if a page links to an address that is not in
the source registry, uses a claim that is not in the ledger, or uses a
claim whose sources are not listed for that page. That is how the site
keeps "each page lists the official sources behind it" true.

It also refuses to finish if a page in one guide links to a page in
another guide (except that guide's home page), lists another state's
sources, or uses another state's facts. That is how each guide stays
whole: every link on a Utah page leads to a Utah page.

Page sources link to each other as "check.html" so the build can confirm
every target exists. The built pages use the addresses Cloudflare Pages
serves ("check", and "./" for the home page), so no click costs a redirect.
site/_headers holds the HTTP headers Cloudflare Pages sends, including the
same Content Security Policy as each page's meta tag plus frame-ancestors,
which only works as a header.

Standard library only, so anyone can read, audit, and run it.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "pages"
SITE = ROOT / "site"
DOCS = ROOT / "docs"
DATA = ROOT / "data"
FONTS = SITE / "assets" / "fonts"
FONTS_LOCK = ROOT / "fonts.lock.json"
SPACEFAST_DIR = ROOT / "spacefast"

SITE_NAME = "The Stasis Project"
BASE_URL = "https://projectstasis.pages.dev/"
PROJECT_REPO = "https://github.com/radiofreelove/projectstasis"
VERSION = "0.3.15 beta"

ODHS_COLORS_LINE = (
    "Colors come from the Oregon Department of Human Services' published palette. "
    "Every text color pair is checked for contrast."
)
SPACEFAST_COLORS_LINE = (
    "Colors come from Radix Colors, an open source color system by Radix "
    '(<a href="assets/licenses/radix-mit.txt">MIT License</a>). '
    "Every text color pair is checked for contrast."
)
SPACEFAST_COLOR_SOURCE = {
    "id": "S31",
    "guide": "all",
    "title": "Radix Colors",
    "short": "Radix Colors",
    "publisher": "Radix (WorkOS)",
    "url": "https://www.radix-ui.com/colors",
    "format": "Web page",
    "kind": "design-standard",
    "date_on_document": "Live page",
    "checked": "2026-11-14",
    "opened": True,
    "notes": (
        "Source of the color palette for this copy. An open source color system, "
        "MIT licensed; the license text ships with this site at assets/licenses/radix-mit.txt. "
        "Values taken from the @radix-ui/colors package, version 3.0.0, and checked against "
        "this copy's contrast tests."
    ),
}

AP_MONTHS = ["Jan.", "Feb.", "March", "April", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."]


def ap_date(iso: str) -> str:
    """2026-11-02 -> Nov. 2, 2026 (docs/style-guide.md: AP month style, always with the year)."""
    year, month, day = (int(part) for part in iso.split("-"))
    return f"{AP_MONTHS[month - 1]} {day}, {year}"


# One guide per state. This list is the only place the guides are named:
# the build, the state switch, the footers, the "page not found" page, and
# the tests all read it. A guide's pages live in src/pages/<name>/. Every
# page belongs to one section, which sets its tagline, menu, footer text,
# and "facts last checked" date. Order here is the order readers see.
# To add a state, follow docs/adding-a-guide.md. See also
# docs/decisions/0013-utah-section.md, docs/decisions/0014-guide-list.md,
# and docs/decisions/0015-front-door-with-three-guides.md (why the order
# is Oregon, Washington, Utah, and why Oregon keeps the address "/").
ABOUT_LABEL = "Why this site exists"

SECTIONS = {
    "oregon": {
        "state": "Oregon",
        "tagline": "OHP, made plain",
        "prefix": "",
        "shared_order": 0,
        "home": "index",
        "nav": [("index", "Home"), ("check", "Check"), ("apply", "Apply"), ("help", "Get help")],
        # Baseline day the whole guide was last re-checked against its sources.
        # Each built page's footer date advances automatically to the newest
        # "checked" date among the sources cited on that page.
        "facts_iso": "2026-11-02",
        "footer_why": (
            "The state explains the new OHP rules across more than a dozen documents. This site puts what "
            "applicants need in one place, in plain words. Each page lists the official sources behind it."
        ),
        "footer_independent": (
            "Not run by the State of Oregon, the Oregon Health Authority (OHA), or the Oregon Department of "
            "Human Services (ODHS). Only OHP decides who qualifies."
        ),
        "about_label": ABOUT_LABEL,
        # What the other guides' footers call this guide.
        "guide_label": "Oregon Health Plan guide",
        # The state switch on every guide's home page: the words under this
        # state's name when the reader is in this guide, and when they are not.
        "switch_here": "This is the OHP guide.",
        "switch_go": "Go to the Oregon Health Plan guide",
        # The "Every source" page: (heading, anchor, which sources).
        # "own and shared" lists this guide's sources and the ones every
        # guide may use, in registry order.
        "source_groups": [("Oregon, federal, and site sources", "oregon-sources", "own and shared")],
        # For tools/browser_check.py: the 1-minute check's page, the value
        # of its "caring for someone" reason, and the words that belong to
        # this guide and must never show in another guide's check results.
        "check": "check",
        "check_care_reason": "child",
        "own_words": ["OHP"],
    },
    "washington": {
        "state": "Washington",
        "tagline": "Apple Health, made plain",
        "prefix": "washington-",
        "shared_order": 60,
        "home": "washington",
        "nav": [
            ("washington", "Washington home"), ("washington-check", "Check"),
            ("washington-apply", "Apply"), ("washington-help", "Get help"),
        ],
        "facts_iso": "2026-11-12",
        # No "more than a dozen" here: the registry holds 9 'state-explainer'
        # entries for this guide, so the guide does not make that claim.
        "footer_why": (
            "The facts about the new Apple Health rules are spread across many official pages and papers. "
            "This guide puts what applicants need in one place, in plain words. Each page lists the official "
            "sources behind it."
        ),
        "footer_independent": (
            "Not run by Washington's government, the Health Care Authority (HCA), or DSHS. "
            "Only Washington decides who meets the rules."
        ),
        "about_label": ABOUT_LABEL,
        "guide_label": "Apple Health guide",
        "switch_here": "This is the Apple Health guide.",
        "switch_go": "Go to the Apple Health guide",
        "source_groups": [
            ("Washington sources", "washington-sources", "own"),
            ("Federal, court, and site sources", "other-sources", "shared, used"),
        ],
        # Shown on "Every source" for a source marked "opened": false. The
        # Washington entries came from research notes, and their "notes" say
        # how far each one was read.
        "unread_note": "read in part or not at all; see the note",
        "check": "washington-check",
        "check_care_reason": "care",
        "own_words": ["Apple Health", "Washington"],
    },
    "utah": {
        "state": "Utah",
        "tagline": "Utah Medicaid, made plain",
        # A shared page is built for this guide as "utah-" plus its slug,
        # and listed after the guide's own pages.
        "prefix": "utah-",
        "shared_order": 30,
        "home": "utah",
        "nav": [("utah", "Utah home"), ("utah-check", "Check"), ("utah-apply", "Apply"), ("utah-help", "Get help")],
        "facts_iso": "2026-11-10",
        "footer_why": (
            "Utah explains the new Medicaid rules across more than a dozen pages and papers. This guide puts "
            "what applicants need in one place, in plain words. Each page lists the official sources behind it."
        ),
        "footer_independent": (
            "Not run by the State of Utah, the Utah Department of Health and Human Services (DHHS), or the "
            "Utah Department of Workforce Services (DWS). Only the state decides who qualifies."
        ),
        "about_label": ABOUT_LABEL,
        "guide_label": "Utah Medicaid guide",
        "switch_here": "This is the Utah Medicaid guide.",
        "switch_go": "Go to the Utah Medicaid guide",
        # "own" lists this guide's sources. "shared, used" lists the sources
        # every guide may use that a page in this guide lists or links to.
        "source_groups": [
            ("Utah sources", "utah-sources", "own"),
            ("Federal, court, and site sources", "other-sources", "shared, used"),
        ],
        "check": "utah-check",
        "check_care_reason": "care",
        "own_words": ["Utah"],
    },
    # Not a guide: the frame for a page that belongs to no state, which
    # today is only the "page not found" page. Its menu is the guides. Its
    # words name every state, so a person rewrites them when a guide is added.
    "both": {
        "guide": False,
        "tagline": "OHP, Apple Health, and Utah Medicaid, made plain",
        "prefix": "",
        "home": "index",
        "nav": [("index", "Oregon guide"), ("washington", "Washington guide"), ("utah", "Utah guide")],
        "facts_iso": None,
        "footer_why": (
            "Oregon, Washington, and Utah each explain their new Medicaid rules across many pages and papers. "
            "This site puts what applicants need in one place, in plain words, with one guide for each state."
        ),
        "footer_independent": (
            "Not run by Oregon, Washington, or Utah, or by any of their agencies. "
            "Only the state decides who qualifies."
        ),
        "about_label": ABOUT_LABEL,
        "footer_title": "All guides",
    },
}
GUIDES = {name: section for name, section in SECTIONS.items() if section.get("guide", True)}

# The registry kind that counts toward "more than a dozen documents."
EXPLAINER_KIND = "state-explainer"
# The words that count must back up. A guide that says them, in its footer
# or on any of its pages, needs more than 12 entries of that kind. A guide
# that does not say them makes no such claim, and its count is only shown
# where a page asks for {{DOC_COUNT}}.
DOZEN_WORDS = "more than a dozen"
# Files in a guide's folder that are parts of a page, not pages.
NOT_FOUND_PART = "_not-found.html"


def owners() -> set:
    """Who a source or a fact may belong to: one guide, or "all" of them
    (federal rules, court papers, standards, and what this site promises
    about itself)."""
    return set(GUIDES) | {"all"}


META_RE = re.compile(r"\A<!--\s*\n(.*?)\n-->\s*\n", re.S)
HREF_RE = re.compile(r'href="([^"]+)"')
CLAIM_RE = re.compile(r'data-claim="([^"]+)"')

CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; "
    "connect-src 'none'; form-action 'none'; base-uri 'none'; object-src 'none'"
)

# Sent by Cloudflare Pages with every response (site/_headers). The header
# version of the policy adds frame-ancestors, which a meta tag cannot set.
# The same set The Strand Project sends (docs/decisions/0012-shared-with-strand.md).
# HSTS changes nothing on pages.dev, because the whole .dev domain is already
# HTTPS-only in browsers; it matters only if the site moves to a custom domain.
HEADERS = [
    ("Content-Security-Policy", CSP + "; frame-ancestors 'none'"),
    ("Referrer-Policy", "no-referrer"),
    ("X-Content-Type-Options", "nosniff"),
    ("X-Frame-Options", "DENY"),
    ("Permissions-Policy", "accelerometer=(), browsing-topics=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()"),
    ("Cross-Origin-Opener-Policy", "same-origin"),
    ("Strict-Transport-Security", "max-age=31536000"),
]

PAGE_LINK_RE = re.compile(r'href="([a-z0-9-]+)\.html(#[^"]*)?"')


class BuildError(Exception):
    pass


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def page_label(path: Path) -> str:
    """How error messages name a page source: "utah/utah-check.html"."""
    return f"{path.parent.name}/{path.name}"


def parse_page(path: Path):
    label = page_label(path)
    folder = path.parent.name
    text = path.read_text(encoding="utf-8")
    match = META_RE.match(text)
    if not match:
        raise BuildError(f"{label}: missing the metadata comment at the top")
    meta = {}
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise BuildError(f"{label}: bad metadata line {line!r}")
        meta[key.strip()] = value.strip()
    for required in ("slug", "order", "title", "short_title", "description"):
        if not meta.get(required):
            raise BuildError(f"{label}: metadata needs '{required}'")
    meta["order"] = int(meta["order"])
    meta["sources"] = [s.strip() for s in meta.get("sources", "").split(",") if s.strip()]
    meta["scripts"] = [s.strip() for s in meta.get("scripts", "").split(",") if s.strip()]
    meta["in_lists"] = meta.get("in_lists", "yes") != "no"
    meta["shared"] = meta.get("shared", "no") == "yes"
    meta["show_short_toggle"] = meta.get("show_short_toggle", "true").lower() not in {"false", "no", "0"}
    # The folder decides which guide a page belongs to.
    if folder in GUIDES:
        if meta.get("section", folder) != folder:
            raise BuildError(f"{label}: says section {meta['section']!r} but sits in the {folder} folder")
        if meta["shared"]:
            raise BuildError(f"{label}: a shared page belongs in src/pages/shared/")
        meta["section"] = folder
    elif folder == "shared":
        frame = meta.get("section")
        if meta["shared"]:
            if frame:
                raise BuildError(f"{label}: a shared page is built for every guide, so it names no section")
            # variants() sets the section of each guide's copy.
            meta["section"] = next(iter(GUIDES))
        elif frame not in SECTIONS or frame in GUIDES:
            raise BuildError(
                f"{label}: a page in src/pages/shared/ needs 'shared: yes', or a 'section' that is not a guide"
            )
    else:
        raise BuildError(f"{label}: unknown folder. Use a guide's name ({', '.join(GUIDES)}) or 'shared'")
    meta["base_slug"] = meta["slug"]
    body = text[match.end():]
    return meta, body


def load_sources():
    """Read src/pages: every page as (path, meta, body), and each guide's "not found" part."""
    stray = sorted(SRC.glob("*.html"))
    if stray:
        raise BuildError(f"{stray[0].name}: pages live in a folder: src/pages/<guide>/ or src/pages/shared/")
    parsed = []
    for path in sorted(SRC.glob("*/*.html"), key=lambda p: (p.name, p.parent.name)):
        if path.name.startswith("_"):
            if path.name != NOT_FOUND_PART or path.parent.name not in GUIDES:
                raise BuildError(f"{page_label(path)}: unknown page part")
            continue
        parsed.append((path, *parse_page(path)))
    parts = {}
    for name in GUIDES:
        part = SRC / name / NOT_FOUND_PART
        if not part.is_file():
            raise BuildError(f"the {name} guide needs src/pages/{name}/{NOT_FOUND_PART} for the 'page not found' page")
        parts[name] = part.read_text(encoding="utf-8").strip("\n")
    return parsed, parts


def load_pages():
    """Every page the site builds, in menu order: one dict per built page."""
    parsed, parts = load_sources()
    shared_slugs = {meta["slug"] for _, meta, _ in parsed if meta["shared"]}
    pages = []
    for path, meta, body in parsed:
        for page in variants(meta, body):
            # Name both the file and the built page in error messages.
            label = page_label(path)
            page["file"] = label if page["slug"] == meta["slug"] else f"{label} (as {page['slug']})"
            page["body"] = localize_links(page["body"], page["section"], shared_slugs)
            pages.append(page)
    pages.sort(key=lambda p: p["order"])
    return pages, shared_slugs, parts


def guide_slugs():
    """For the tests: the built pages of each guide, as {guide: set of slugs}."""
    pages, _, _ = load_pages()
    return {name: {p["slug"] for p in pages if p["section"] == name} for name in GUIDES}


def section_blocks(body: str, section: str) -> str:
    """Keep the blocks marked for this guide, and drop every other guide's."""
    block = re.compile(r"[ \t]*<!-- (" + "|".join(GUIDES) + r") -->\n(.*?)[ \t]*<!-- /\1 -->\n", re.S)
    return block.sub(lambda m: m.group(2) if m.group(1) == section else "", body)


def variants(meta, body):
    """One page per guide for a shared page; the page itself otherwise."""
    if not meta["shared"]:
        yield dict(meta, body=section_blocks(body, meta["section"]))
        return
    for name, section in GUIDES.items():
        page = dict(meta, section=name, slug=section["prefix"] + meta["slug"],
                    order=meta["order"] + section["shared_order"], body=section_blocks(body, name))
        for key in ("title", "short_title", "description"):
            page[key] = meta.get(f"{name}_{key}", meta[key])
        if f"{name}_sources" in meta:
            page["sources"] = [s.strip() for s in meta[f"{name}_sources"].split(",") if s.strip()]
        yield page


def localize_links(text: str, section: str, shared_slugs) -> str:
    """Point links to shared pages at this guide's copy of them."""
    prefix = SECTIONS[section]["prefix"]
    if not prefix:
        return text
    for slug in shared_slugs:
        text = text.replace(f'href="{slug}.html', f'href="{prefix}{slug}.html')
    return text


def registry_maps(registry):
    by_id = {s["id"]: s for s in registry["sources"]}
    urls = {s["url"] for s in registry["sources"]}
    urls |= {item["url"] for item in registry["application_languages"]["items"]}
    return by_id, urls


def render_sources_section(ids, by_id):
    items = []
    for source_id in ids:
        src = by_id[source_id]
        fmt = f' <span class="tag">{esc(src["format"])}</span>' if src["format"] == "PDF" else ""
        dated = src["date_on_document"]
        checked = src["checked"]
        items.append(
            f'      <li id="src-{esc(source_id.lower())}"><a href="{esc(src["url"])}">{esc(src["title"])}</a>{fmt}<br>'
            f'{esc(src["publisher"])}. Date on it: {esc(dated)}. '
            f'Checked: <time datetime="{esc(checked)}">{esc(ap_date(checked))}</time>.</li>'
        )
    return (
        '    <section class="sources" aria-labelledby="sources-title">\n'
        '      <h2 id="sources-title">Sources for this page</h2>\n'
        '      <p>Each source shows the date printed on it and the date we last checked it. '
        'Want every detail? See <a href="sources.html">every source</a> and the public '
        f'<a href="{PROJECT_REPO}/blob/main/docs/claims.md">fact log</a>.</p>\n'
        '      <ol>\n' + "\n".join(items) + "\n      </ol>\n"
        "    </section>\n"
    )


SETTINGS_PANEL = """    <details class="display-settings" data-settings>
      <summary>Display settings</summary>
      <div class="settings-body">
        <fieldset>
          <legend>Text size</legend>
          <label class="choice"><input type="radio" name="text" value="m" checked> Standard</label>
          <label class="choice"><input type="radio" name="text" value="l"> Large</label>
          <label class="choice"><input type="radio" name="text" value="xl"> Extra large</label>
        </fieldset>
        <fieldset>
          <legend>Spacing</legend>
          <label class="choice"><input type="radio" name="spacing" value="normal" checked> Standard</label>
          <label class="choice"><input type="radio" name="spacing" value="roomy"> More space between lines and letters</label>
        </fieldset>
        <fieldset>
          <legend>Font</legend>
          <label class="choice"><input type="radio" name="font" value="system" checked> Standard</label>
          <label class="choice"><input type="radio" name="font" value="hyper"> Atkinson Hyperlegible, a font designed so letters are easy to tell apart</label>
        </fieldset>
        <fieldset>
          <legend>Colors</legend>
          <label class="choice"><input type="radio" name="theme" value="auto" checked> Match my device</label>
          <label class="choice"><input type="radio" name="theme" value="warm"> Warm light</label>
          <label class="choice"><input type="radio" name="theme" value="white"> Plain white</label>
          <label class="choice"><input type="radio" name="theme" value="dark"> Dark</label>
          <label class="choice"><input type="radio" name="theme" value="contrast"> High contrast</label>
        </fieldset>
        <fieldset>
          <legend>How much to show</legend>
          <label class="choice"><input type="radio" name="details" value="all" checked> Full version</label>
          <label class="choice"><input type="radio" name="details" value="fewer"> Short version</label>
        </fieldset>
        <div class="settings-actions">
          <button type="button" class="button-secondary" data-reset-settings>Reset to standard</button>
          <p>Your choices are saved on this device only.</p>
        </div>
      </div>
    </details>
    <p id="settings-status" class="visually-hidden" role="status" aria-live="polite"></p>
"""


# The same setting as the "How much to show" choices in SETTINGS_PANEL,
# where a reader can see it: a slim strip at the top of content pages' main
# area, above the heading. Pages with "show_short_toggle: false" omit it.
# One button, so keyboard focus stays put when it is used. The style sheet
# shows the words that match the html element's data-details value ("all" or
# "fewer"), so the strip is right from the first paint, and
# assets/js/settings.js keeps it and the panel in step. Without JavaScript
# the strip is not shown (the style sheet waits for the data-js mark that
# settings.js sets), and the full page shows. aria-pressed says whether
# short-version mode is on; settings.js sets it.
# The wording is fixed; tools/check_structure.py checks it on every page.
DETAIL_STRIP = """    <div class="detail-strip" data-detail-strip>
      <p class="detail-ask when-all">Still too much to take in?</p>
      <p class="fewer-note when-fewer">You are seeing the short version. Some details are hidden.</p>
      <button type="button" class="button-secondary" data-toggle-details aria-pressed="false"><span class="when-all">Show the short version</span><span class="when-fewer">Show the full version</span></button>
      <p class="detail-hint when-all">This hides the extra details on this page. The main points, the steps, and the links you need stay here.</p>
    </div>
"""


# Shared 24x24 inline SVG icons (1.75px rounded strokes, currentColor, zero
# external requests). Every decorative icon sets aria-hidden="true" and
# focusable="false". Keep in step with The Strand Project's icon vocabulary.
ICONS = {
    "alert": '<path d="M12 3L2.5 19.5h19L12 3z"/><path d="M12 9.5v4.5"/><path d="M12 17h.01"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5"/><path d="M12 8h.01"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="M8.5 12.5l2.5 2.5 4.5-5.5"/>',
    "shield": '<path d="M12 3l7.5 3v6c0 4.5-3.2 7.8-7.5 9-4.3-1.2-7.5-4.5-7.5-9V6L12 3z"/>',
    "income": '<path d="M12 3v18"/><path d="M16.5 7.5a3.5 3.5 0 0 0-3.5-2.5h-2a3 3 0 0 0 0 6h2a3 3 0 0 1 0 6h-2.5a3.5 3.5 0 0 1-3.5-2.5"/>',
    "school": '<path d="M2.5 9.5L12 5l9.5 4.5L12 14 2.5 9.5z"/><path d="M6.5 11.5v5c0 1.5 2.5 2.75 5.5 2.75s5.5-1.25 5.5-2.75v-5"/><path d="M21.5 9.5v5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/>',
    "circle": '<circle cx="12" cy="12" r="7"/>',
    "triangle": '<path d="M12 4L3.5 19h17L12 4z"/>',
    "square": '<rect x="5" y="5" width="14" height="14" rx="2"/>',
    "online": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a13 13 0 0 1 0 18"/><path d="M12 3a13 13 0 0 0 0 18"/>',
    "phone": '<path d="M6.5 4.5h3l1.5 4-2 1.5a11 11 0 0 0 5 5l1.5-2 4 1.5v3a2 2 0 0 1-2 2C10.5 19.5 4.5 13.5 4.5 6.5a2 2 0 0 1 2-2z"/>',
    "inperson": '<path d="M4 20h16"/><path d="M6 20V7l6-3 6 3v13"/><path d="M10 20v-4h4v4"/><path d="M9.5 10h.01M14.5 10h.01M9.5 13h.01M14.5 13h.01"/>',
    "paper": '<path d="M6 3h8l4 4v14H6V3z"/><path d="M14 3v4h4"/><path d="M9 12h6M9 16h6"/>',
    "helper": '<circle cx="9" cy="8.5" r="3"/><path d="M3.5 19a5.5 5.5 0 0 1 11 0"/><circle cx="16.5" cy="9.5" r="2.25"/><path d="M15.5 14a4.5 4.5 0 0 1 5 5"/>',
    "languages": '<path d="M4 5h16v10H9l-5 4V5z"/><path d="M8 9.5h8M8 12.5h5"/>',
    "letter": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 6.5L12 13l8.5-6.5"/>',
    "denied": '<path d="M12 4v16"/><path d="M5 7h14"/><path d="M7 7l-3 6h6l-3-6z"/><path d="M17 7l-3 6h6l-3-6z"/><path d="M8 20h8"/>',
    "health": '<path d="M12 20s-7.5-4.5-7.5-10a4.5 4.5 0 0 1 7.5-3.3A4.5 4.5 0 0 1 19.5 10c0 5.5-7.5 10-7.5 10z"/><path d="M12 9v5M9.5 11.5h5"/>',
    "immigration": '<rect x="5" y="3" width="14" height="18" rx="2"/><circle cx="12" cy="11" r="3.5"/><path d="M8.5 17.5h7"/>',
    "words": '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H12v17H6.5A2.5 2.5 0 0 0 4 22V5.5z"/><path d="M20 5.5A2.5 2.5 0 0 0 17.5 3H12v17h5.5a2.5 2.5 0 0 1 2.5 2V5.5z"/>',
    "log": '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V3h6v1"/><path d="M8.5 10l1.5 1.5 3-3"/><path d="M14.5 10h2"/><path d="M8.5 15l1.5 1.5 3-3"/><path d="M14.5 15h2"/>',
}

ICON_RE = re.compile(r"\{\{ICON:([a-z0-9_-]+)\}\}")

# Default icon + short sentence-case status label for each callout box class
# so meaning never relies on left-border color alone.
CALLOUT_META = {
    "warn": ("alert", "Heads up"),
    "callout": ("info", "Key point"),
    "good": ("check", "Good to know"),
    "promise": ("shield", "Privacy"),
}

CALLOUT_TAG_RE = re.compile(
    r'(<(?P<tag>div|section)\b(?P<attrs>[^>]*\bclass="(?P<cls>[^"]+)"[^>]*)>)'
)


def render_icon(name: str, extra_class: str = "") -> str:
    if name not in ICONS:
        raise BuildError(f"unknown icon '{name}'")
    cls = f"icon {extra_class}".strip()
    return (
        f'<svg class="{cls}" viewBox="0 0 24 24" width="24" height="24" '
        'fill="none" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true" focusable="false">{ICONS[name]}</svg>'
    )


def expand_icons(text: str) -> str:
    return ICON_RE.sub(lambda m: render_icon(m.group(1)), text)


def decorate_callouts(body: str) -> str:
    """Prepend a shape icon + short status word inside each callout container."""
    def repl(match: re.Match) -> str:
        full = match.group(0)
        attrs = match.group("attrs")
        classes = match.group("cls").split()
        kind = next((c for c in ("warn", "callout", "good", "promise") if c in classes), None)
        if not kind:
            return full
        icon_name, label = CALLOUT_META[kind]
        kicker_m = re.search(r'\bdata-kicker="([^"]+)"', attrs)
        if kicker_m:
            label = kicker_m.group(1)
            if label.lower() in {"update", "policy update"}:
                icon_name = "info"
        icon_m = re.search(r'\bdata-icon="([^"]+)"', attrs)
        if icon_m:
            icon_name = icon_m.group(1)
        badge = (
            '\n      <p class="box-kicker">'
            f'<span class="box-icon">{render_icon(icon_name)}</span>'
            f'<span>{esc(label)}</span></p>'
        )
        return full + badge

    return CALLOUT_TAG_RE.sub(repl, body)


def render_guide_switch(current: str) -> str:
    """The "Pick your state" buttons: every guide, in order, with the reader's own guide filled."""
    items = []
    for name, guide in GUIDES.items():
        here = name == current
        mark = ' aria-current="page"' if here else ""
        note = guide["switch_here"] if here else guide["switch_go"]
        items.append(
            f'        <li><a href="{guide["home"]}.html"{mark}><span class="guide-state">{esc(guide["state"])}</span> '
            f'<span class="guide-note">{esc(note)}</span></a></li>'
        )
    return (
        '    <nav class="guide-switch" aria-labelledby="guide-switch-label">\n'
        '      <p class="guide-switch-label" id="guide-switch-label">Pick your state</p>\n'
        '      <ul>\n' + "\n".join(items) + "\n      </ul>\n"
        "    </nav>"
    )


def render_header_state_switcher(current: str) -> str:
    """Compact, keyboard-accessible state indicator and switcher pill in the header."""
    items = []
    for name, guide in GUIDES.items():
        here = name == current
        mark = ' aria-current="page"' if here else ""
        items.append(
            f'            <li><a href="{guide["home"]}.html"{mark}>'
            f'<span class="state-switcher-name">{esc(guide["state"])}</span>'
            f'<span class="state-switcher-guide">{esc(guide["guide_label"])}</span></a></li>'
        )
    if current in GUIDES:
        label = f"State: {GUIDES[current]['state']}"
        aria = f"State: {GUIDES[current]['state']}. Switch state guide"
    else:
        label = "Pick your state"
        aria = "Pick your state guide"
    return (
        '        <details class="state-switcher" data-state-switcher>\n'
        f'          <summary aria-label="{esc(aria)}">'
        f'<span class="state-switcher-label">{esc(label)}</span>'
        '<span class="state-switcher-caret" aria-hidden="true">&#9662;</span></summary>\n'
        '          <ul class="state-switcher-menu">\n' + "\n".join(items) + "\n          </ul>\n"
        '        </details>'
    )


def page_facts_iso(meta, by_id, registry=None, used=None) -> str | None:
    """Compute a page's 'Facts last checked' date so it never lags behind its cited sources."""
    section = SECTIONS[meta["section"]]
    base_iso = section["facts_iso"]
    if not base_iso:
        return None
    dates = [base_iso]
    for sid in meta["sources"]:
        if sid in by_id:
            dates.append(by_id[sid]["checked"])
    if meta.get("base_slug") == "sources" and registry is not None:
        sec_name = meta["section"]
        used_ids = (used or {}).get(sec_name, set())
        picks = {
            "own": lambda s: s["guide"] == sec_name,
            "own and shared": lambda s: s["guide"] in (sec_name, "all"),
            "shared, used": lambda s: s["guide"] == "all" and s["id"] in used_ids,
        }
        for _, _, which in section["source_groups"]:
            for src in registry["sources"]:
                if picks[which](src):
                    dates.append(src["checked"])
    return max(dates)


def render_page(meta, body, pages, by_id, doc_counts, registry=None, used=None):
    slug = meta["slug"]
    section = SECTIONS[meta["section"]]
    tagline = section["tagline"]
    facts_iso = page_facts_iso(meta, by_id, registry=registry, used=used)
    facts_text = ap_date(facts_iso) if facts_iso else ""
    facts_line = f'Facts last checked <time datetime="{facts_iso}">{facts_text}</time>. ' if facts_iso else ""
    if slug == section["home"]:
        title_tag = f"{SITE_NAME}: {tagline}"
    else:
        title_tag = f"{meta['title']} | {SITE_NAME}"

    nav_links = []
    for target, label in section["nav"]:
        current = ' aria-current="page"' if target == slug else ""
        nav_links.append(f'          <li><a href="{target}.html"{current}>{esc(label)}</a></li>')

    # A guide's footer lists "All pages": every page of this guide, including
    # its own copy of the shared pages, then the home page of each other guide.
    # A page that belongs to no guide lists the guides.
    other_guides = [
        f'          <li><a href="{guide["home"]}.html">{esc(guide["guide_label"])}</a></li>'
        for name, guide in GUIDES.items() if name != meta["section"]
    ]
    if meta["section"] in GUIDES:
        footer_title = "All pages"
        footer_links = []
        for page in pages:
            if not (page["in_lists"] and page["section"] == meta["section"]):
                continue
            current = ' aria-current="page"' if page["slug"] == slug else ""
            footer_links.append(
                f'          <li><a href="{page["slug"]}.html"{current}>{esc(page["short_title"])}</a></li>'
            )
        footer_links += other_guides
    else:
        footer_title = section["footer_title"]
        footer_links = other_guides

    scripts = "".join(
        f'\n  <script src="assets/js/{esc(name)}.js" defer></script>' for name in meta["scripts"]
    )
    sources_html = render_sources_section(meta["sources"], by_id) if meta["sources"] else ""
    if "{{DOC_COUNT}}" in body:
        body = body.replace("{{DOC_COUNT}}", str(doc_counts[meta["section"]]))
    body = body.replace("{{FACTS_CHECKED_TEXT}}", facts_text)
    body = body.replace("{{FACTS_CHECKED_ISO}}", facts_iso or "")
    body = decorate_callouts(body)
    body = expand_icons(body)

    detail_strip = DETAIL_STRIP if meta.get("show_short_toggle", True) else ""
    state_switcher = render_header_state_switcher(meta["section"])

    canonical = ""
    if meta["in_lists"]:
        canonical = f'  <link rel="canonical" href="{BASE_URL}{"" if slug == "index" else slug}">\n'

    return f"""<!doctype html>
<html lang="en" data-theme="auto" data-text="m" data-spacing="normal" data-font="system" data-details="all">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="{CSP}">
  <meta name="referrer" content="no-referrer">
  <title>{esc(title_tag)}</title>
  <meta name="description" content="{esc(meta['description'])}">
{canonical}  <link rel="icon" href="assets/img/logo.svg" type="image/svg+xml">
  <link rel="stylesheet" href="assets/css/site.css">
  <script src="assets/js/settings.js"></script>
  <script src="assets/js/site.js" defer></script>{scripts}
</head>
<body>
  <a class="skip-link" href="#main">Skip to main content</a>
  <header class="site-header">
    <div class="independent-banner">
      <div class="wrap">
        <p><strong>Independent guide.</strong> Not run by the state. <a href="about.html">{esc(section["about_label"])}</a>. <a href="about.html#report">Report a mistake</a>.</p>
      </div>
    </div>
    <div class="wrap">
      <div class="header-row">
        <a class="brand" href="{section["home"]}.html">
          <img src="assets/img/logo.svg" alt="" width="40" height="40">
          <span><span class="brand-name">{SITE_NAME}</span><span class="brand-tag">{esc(tagline)}</span></span>
        </a>
{state_switcher}
      </div>
      <nav class="main-nav" aria-label="Main">
        <ul>
{chr(10).join(nav_links)}
        </ul>
      </nav>
{SETTINGS_PANEL}    </div>
  </header>
  <main id="main" tabindex="-1">
    <div class="wrap">
{detail_strip}{body.rstrip()}
{sources_html}    </div>
  </main>
  <footer class="site-footer">
    <div class="wrap">
      <h2>{esc(section["about_label"])}</h2>
      <p>{esc(section["footer_why"])}</p>
      <p><strong>Independent.</strong> {esc(section["footer_independent"])}</p>
      <p><strong>Private.</strong> No accounts, ads, cookies, or tracking. <a href="privacy.html">How your privacy is protected</a>.</p>
      <p>{facts_line}Version {VERSION}. <a href="{PROJECT_REPO}">See how this site is made</a>.</p>
      <p>Words: <a href="{PROJECT_REPO}/blob/main/LICENSE">CC BY 4.0</a>. Code: <a href="{PROJECT_REPO}/blob/main/LICENSE-CODE">MIT</a>. <a href="about.html#license">Reuse this guide</a>.</p>
      <nav class="footer-pages" aria-label="{footer_title}">
        <h2>{footer_title}</h2>
        <ul>
{chr(10).join(footer_links)}
        </ul>
      </nav>
    </div>
  </footer>
</body>
</html>
"""


def foreign_source(section: str, src) -> bool:
    """True if this source belongs to another state's guide."""
    return src["guide"] not in (section, "all")


def render_sources_page_table(registry, section, used):
    """Each guide's "Every source" page lists that guide's sources only.

    The guide's "source_groups" setting gives the headings and what goes
    under each: its own sources, the sources every guide may use, or only
    the shared ones that a page in this guide lists or links to ("used").
    """
    picks = {
        "own": lambda s: s["guide"] == section,
        "own and shared": lambda s: s["guide"] in (section, "all"),
        "shared, used": lambda s: s["guide"] == "all" and s["id"] in used,
    }
    table = ""
    for title, anchor, which in SECTIONS[section]["source_groups"]:
        sources = [s for s in registry["sources"] if picks[which](s)]
        table += (
            f'      <h2 id="{anchor}">{title}</h2>\n'
            '      <ol class="all-sources">\n' + "\n".join(source_rows(sources)) + "\n      </ol>\n"
        )
    langs = registry["application_languages"]
    if langs["guide"] == section:
        table += (
            f'      <p>We also link to the paper application in {len(langs["items"])} languages, '
            'exactly as listed on OHA\'s how-to-apply page. See <a href="help.html#languages">Free help and other languages</a>.</p>\n'
        )
    return table


def unread_words(src):
    """What to say for a source marked "opened": false that names no
    "linked_from": the words its guide sets ("unread_note"), if any."""
    if "linked_from" in src:
        return None
    return GUIDES.get(src["guide"], {}).get("unread_note")


def source_rows(sources):
    rows = []
    pdf_tag = ' <span class="tag">PDF</span>'
    for src in sources:
        if src["opened"]:
            opened = "Yes"
        elif unread_words(src):
            opened = "No (" + unread_words(src) + ")"
        else:
            opened = "No (address from " + src.get("linked_from", "another official source") + ")"
        tag = pdf_tag if src["format"] == "PDF" else ""
        rows.append(
            "        <li>"
            f'<a href="{esc(src["url"])}">{esc(src["title"])}</a>{tag}<br>'
            f"{esc(src['publisher'])}. Date on it: {esc(src['date_on_document'])}. "
            f"Checked: {esc(src['checked'])}. Read by us: {esc(opened)}.<br>"
            f"<span>Why we list it: {esc(src['notes'])}</span></li>"
        )
    return rows


def render_language_list(registry):
    items = []
    for item in registry["application_languages"]["items"]:
        if item["native"]:
            label = (
                f'<span lang="{esc(item["hreflang"])}">{esc(item["native"])}</span> '
                f'({esc(item["english"])})'
            )
        else:
            label = esc(item["english"])
        items.append(
            f'        <li><a href="{esc(item["url"])}" hreflang="{esc(item["hreflang"])}">{label}</a> '
            '<span class="tag">PDF</span></li>'
        )
    return '      <ul class="language-list">\n' + "\n".join(items) + "\n      </ul>\n"


def render_sitemap(pages, by_id, registry, used):
    entries = []
    for page in pages:
        if not page["in_lists"]:
            continue
        loc = BASE_URL if page["slug"] == "index" else f"{BASE_URL}{page['slug']}"
        lastmod = page_facts_iso(page, by_id, registry=registry, used=used)
        entries.append(f"  <url><loc>{loc}</loc><lastmod>{lastmod}</lastmod></url>")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )


def render_robots():
    return f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}sitemap.xml\n"


def render_headers(theme: str = "default"):
    lines = [
        "# Generated by tools/build.py. Do not edit by hand.",
        "# Cloudflare Pages sends these headers with every response from this site.",
        "# See docs/privacy.md and docs/decisions/0011-cloudflare-pages.md.",
        "/*",
    ]
    for name, value in HEADERS:
        if theme == "spacefast" and name == "Strict-Transport-Security":
            continue
        lines.append(f"  {name}: {value}")
    return "\n".join(lines) + "\n"


def pretty_links(rendered: str) -> str:
    """Point page links at the addresses Cloudflare Pages serves: "check", and "./" for home."""

    def swap(match):
        slug, fragment = match.group(1), match.group(2) or ""
        return f'href="{"./" if slug == "index" else slug}{fragment}"'

    return PAGE_LINK_RE.sub(swap, rendered)


def md_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def render_sources_md(registry):
    lines = [
        "# Source registry",
        "",
        "Generated from `data/sources.json` by `tools/build.py`. Do not edit by hand.",
        "",
        f"Registry version {registry['registry_version']}. {registry['notes']}",
        "",
        "| ID | Guide | Source | Kind | Date on it | Checked | Read by us | Notes |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for src in registry["sources"]:
        if src["opened"]:
            read = "Yes"
        elif unread_words(src):
            read = f"No, {unread_words(src)}"
        else:
            read = f"No, address from {src.get('linked_from', 'another source')}"
        lines.append(
            f"| {src['id']} | {src['guide']} | [{md_escape(src['title'])}]({src['url']}) ({md_escape(src['publisher'])}) | "
            f"{src['kind']} | {md_escape(src['date_on_document'])} | {src['checked']} | {md_escape(read)} | "
            f"{md_escape(src['notes'])} |"
        )
    lines += ["", "## Paper application languages", "", registry["application_languages"]["notes"], ""]
    for item in registry["application_languages"]["items"]:
        name = f"{item['native']} ({item['english']})" if item["native"] else item["english"]
        lines.append(f"- [{name}]({item['url']})")
    lines.append("")
    return "\n".join(lines)


def render_claims_md(claims, by_id, usage):
    kinds = {
        "fact": "Fact: stated in the listed source.",
        "math": "Math: arithmetic on a sourced number.",
        "inference": "Inference: our reading of the sources, worded with care on the page.",
        "design": "Design promise: something this site does or does not do, checked in code.",
        "tip": "Tip: general good practice, not a rule.",
    }
    lines = [
        "# Fact log (claims ledger)",
        "",
        "Generated from `data/claims.json` by `tools/build.py`. Do not edit by hand.",
        "",
        "Every factual statement on the site carries a `data-claim` attribute in the page source.",
        "The build fails if a page uses a claim that is not here, or if the claim's sources are",
        "not listed in that page's Sources section.",
        "",
        "Kinds:",
        "",
    ]
    for key, label in kinds.items():
        lines.append(f"- **{key}**: {label}")
    lines += ["", "| ID | Guide | Kind | Statement on the site | Sources | Pages | Notes |", "|---|---|---|---|---|---|---|"]
    for claim in claims["claims"]:
        srcs = ", ".join(f"[{sid}]({by_id[sid]['url']})" for sid in claim["sources"]) or "None (design)"
        pages = ", ".join(sorted(usage.get(claim["id"], []))) or "Not used"
        lines.append(
            f"| {claim['id']} | {claim['guide']} | {claim['kind']} | {md_escape(claim['statement'])} | {srcs} | {pages} | "
            f"{md_escape(claim.get('note', ''))} |"
        )
    lines.append("")
    return "\n".join(lines)


def check_fonts():
    """Every font file named in fonts.lock.json exists and matches its SHA-256."""
    lock = json.loads(FONTS_LOCK.read_text(encoding="utf-8"))
    errors = []
    for item in lock["files"]:
        path = FONTS / item["dest"]
        if not path.is_file():
            errors.append(f"font file missing: {path.relative_to(ROOT)}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            errors.append(f"font file changed (checksum mismatch): {path.relative_to(ROOT)}")
    return errors


def build(theme: str = "default"):
    registry = load_json(DATA / "sources.json")
    if theme == "spacefast":
        registry["sources"] = [
            {**SPACEFAST_COLOR_SOURCE, "checked": src["checked"]} if src.get("id") == "S31" else src
            for src in registry["sources"]
        ]
    claims = load_json(DATA / "claims.json")
    by_id, known_urls = registry_maps(registry)
    claim_by_id = {c["id"]: c for c in claims["claims"]}
    errors = []

    for src in registry["sources"]:
        if src.get("guide") not in owners():
            errors.append(f"source {src['id']}: 'guide' must be one of {', '.join(sorted(owners()))}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", src.get("checked", "")):
            errors.append(f"source {src['id']}: 'checked' must be a date like 2026-11-02")
    forms_guide = registry["application_languages"].get("guide")
    if forms_guide not in GUIDES:
        errors.append("application_languages: 'guide' must name the guide whose paper forms these are")

    for claim in claims["claims"]:
        if claim.get("guide") not in owners():
            errors.append(f"claim {claim['id']}: 'guide' must be one of {', '.join(sorted(owners()))}")
        for sid in claim["sources"]:
            if sid not in by_id:
                errors.append(f"claim {claim['id']}: unknown source {sid}")
            elif by_id[sid].get("guide") not in (claim.get("guide"), "all"):
                errors.append(
                    f"claim {claim['id']}: relies on {sid}, a source that belongs to the {by_id[sid].get('guide')} guide"
                )
        if claim["kind"] not in {"fact", "math", "inference", "design", "tip"}:
            errors.append(f"claim {claim['id']}: unknown kind {claim['kind']}")
        if claim["kind"] in {"fact", "math", "inference"} and not claim["sources"]:
            errors.append(f"claim {claim['id']}: kind {claim['kind']} needs at least one source")
    if errors:
        raise BuildError("Build stopped:\n  - " + "\n  - ".join(errors))

    pages, shared_slugs, not_found_parts = load_pages()
    doc_counts = {}
    for name, guide in GUIDES.items():
        doc_counts[name] = sum(1 for s in registry["sources"] if s["guide"] == name and s["kind"] == EXPLAINER_KIND)
        says_dozen = DOZEN_WORDS in guide["footer_why"] or any(
            DOZEN_WORDS in p["body"] for p in pages if p["section"] == name
        )
        if says_dozen and doc_counts[name] <= 12:
            errors.append(
                f"the {name} guide says 'more than a dozen' but the registry counts {doc_counts[name]} "
                f"'{EXPLAINER_KIND}' entries for it"
            )
    slugs = {p["slug"] for p in pages}
    if len(slugs) != len(pages):
        errors.append("two pages share one slug")
    if len({p["order"] for p in pages}) != len(pages):
        errors.append("two pages share one 'order' number")
    section_of = {p["slug"]: p["section"] for p in pages}
    homes = {section["home"] for section in GUIDES.values()}
    by_url = {s["url"]: s for s in registry["sources"]}
    form_urls = {item["url"] for item in registry["application_languages"]["items"]}
    for name, guide in GUIDES.items():
        home = next((p for p in pages if p["slug"] == guide["home"] and p["section"] == name), None)
        if home is None:
            errors.append(f"the {name} guide has no home page with slug {guide['home']!r}")
        elif "{{GUIDE_SWITCH}}" not in home["body"]:
            errors.append(f"{home['file']}: a guide's home page needs {{{{GUIDE_SWITCH}}}}, the way to the other guides")
        own_slugs = {p["slug"] for p in pages if p["section"] == name}
        for target in [slug for slug, _ in guide["nav"]] + [guide["check"]]:
            if target not in own_slugs:
                errors.append(f"the {name} guide's settings name {target!r}, which is not one of its pages")

    # Which sources each guide lists or links to, for its "Every source" page.
    used: dict[str, set] = {name: set() for name in SECTIONS}
    for page in pages:
        used[page["section"]].update(sid for sid in page["sources"] if sid in by_id)
        for href in HREF_RE.findall(page["body"]):
            if href in by_url:
                used[page["section"]].add(by_url[href]["id"])

    usage: dict[str, set] = {}
    outputs: dict[Path, str] = {}

    for page in pages:
        body = page["body"]
        name = page["section"]
        any_guide = page.get("any_guide") == "yes"
        if "{{SOURCES_TABLE}}" in body:
            body = body.replace("{{SOURCES_TABLE}}", render_sources_page_table(registry, name, used[name]))
        if "{{APPLICATION_LANGUAGES}}" in body:
            body = body.replace("{{APPLICATION_LANGUAGES}}", render_language_list(registry))
        if "{{GUIDE_SWITCH}}" in body:
            if name not in GUIDES:
                errors.append(f"{page['file']}: {{{{GUIDE_SWITCH}}}} works only on a guide's page")
            else:
                body = body.replace("{{GUIDE_SWITCH}}", render_guide_switch(name))
        if "{{GUIDE_START_LISTS}}" in body:
            body = body.replace("{{GUIDE_START_LISTS}}", "\n\n".join(not_found_parts[g] for g in GUIDES))
        if "{{DOC_COUNT}}" in body and name not in GUIDES:
            errors.append(f"{page['file']}: {{{{DOC_COUNT}}}} works only on a guide's page")
            body = body.replace("{{DOC_COUNT}}", "")

        for sid in page["sources"]:
            if sid not in by_id:
                errors.append(f"{page['file']}: lists unknown source {sid}")
            elif foreign_source(name, by_id[sid]):
                errors.append(f"{page['file']}: lists {sid}, a source that belongs to the {by_id[sid]['guide']} guide")

        for attr in CLAIM_RE.findall(body):
            for cid in attr.split():
                usage.setdefault(cid, set()).add(page["slug"])
                claim = claim_by_id.get(cid)
                if not claim:
                    errors.append(f"{page['file']}: uses unknown claim {cid}")
                    continue
                if claim["guide"] not in (name, "all"):
                    errors.append(f"{page['file']}: uses {cid}, a fact that belongs to the {claim['guide']} guide")
                missing = [sid for sid in claim["sources"] if sid not in page["sources"]]
                if missing:
                    errors.append(
                        f"{page['file']}: claim {cid} relies on {', '.join(missing)}, "
                        "which this page does not list in its sources"
                    )

        for href in HREF_RE.findall(body):
            if href.startswith(("http://", "https://")):
                if href.startswith(PROJECT_REPO):
                    continue
                if href not in known_urls:
                    errors.append(f"{page['file']}: link not in source registry: {href}")
                elif not any_guide and (
                    (href in by_url and foreign_source(name, by_url[href]))
                    or (href in form_urls and forms_guide != name)
                ):
                    errors.append(f"{page['file']}: links to another state's source: {href}")
            elif href.startswith(("mailto:", "tel:")):
                continue
            elif href.startswith("#"):
                continue
            else:
                target = href.split("#", 1)[0]
                if target.endswith(".html"):
                    if target[:-5] not in slugs:
                        errors.append(f"{page['file']}: link to missing page {href}")
                    elif not any_guide and section_of[target[:-5]] != name and target[:-5] not in homes:
                        errors.append(
                            f"{page['file']}: links to {href}, a page in another guide. "
                            "Only another guide's home page may be linked."
                        )
                elif not (SITE / target).exists():
                    errors.append(f"{page['file']}: link to missing file {href}")

        rendered = localize_links(
            render_page(page, body, pages, by_id, doc_counts, registry=registry, used=used),
            name,
            shared_slugs,
        )
        rendered = pretty_links(rendered)
        if theme == "spacefast":
            rendered = rendered.replace(
                '  <link rel="stylesheet" href="assets/css/site.css">',
                '  <link rel="stylesheet" href="assets/css/site.css">\n'
                '  <link rel="stylesheet" href="assets/css/spacefast-theme.css">',
                1,
            )
            rendered = rendered.replace(ODHS_COLORS_LINE, SPACEFAST_COLORS_LINE)
        if page.get("root_absolute") == "yes":
            # Cloudflare Pages serves 404.html at whatever address was missing, so
            # its links and assets must not depend on the current folder.
            rendered = re.sub(r'(href|src)="(assets/[^"]+)"', r'\1="/\2"', rendered)
            rendered = re.sub(r'href="\./(#[^"]*)?"', r'href="/\1"', rendered)
            rendered = re.sub(r'href="([a-z0-9-]+)(#[^"]*)?"', r'href="/\1\2"', rendered)
        outputs[SITE / f"{page['slug']}.html"] = rendered

    for claim in claims["claims"]:
        if claim["id"] not in usage:
            errors.append(f"claim {claim['id']} is in the ledger but no page uses it")

    outputs[SITE / "sitemap.xml"] = render_sitemap(pages, by_id, registry, used)
    outputs[SITE / "robots.txt"] = render_robots()
    outputs[SITE / "_headers"] = render_headers(theme=theme)
    outputs[DOCS / "sources.md"] = render_sources_md(registry)
    outputs[DOCS / "claims.md"] = render_claims_md(claims, by_id, usage)

    errors.extend(check_fonts())

    if errors:
        raise BuildError("Build stopped:\n  - " + "\n  - ".join(errors))
    return outputs


def write_standalone_site(outputs: dict[Path, str], out_dir: Path, theme: str) -> int:
    """Write a complete static site copy (pages + assets) into out_dir without touching site/ or docs/."""
    if out_dir.resolve() == SITE.resolve():
        raise BuildError("--out must not point at site/ when building a themed copy")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SITE / "assets", out_dir / "assets", dirs_exist_ok=True)
    if theme == "spacefast":
        shutil.copyfile(SPACEFAST_DIR / "theme.css", out_dir / "assets" / "css" / "spacefast-theme.css")
        shutil.copyfile(SPACEFAST_DIR / "logo.svg", out_dir / "assets" / "img" / "logo.svg")
        licenses_dir = out_dir / "assets" / "licenses"
        licenses_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SPACEFAST_DIR / "radix-mit.txt", licenses_dir / "radix-mit.txt")
    written = 0
    for path, content in outputs.items():
        if path.parent == SITE:
            target = out_dir / path.name
            target.write_text(content, encoding="utf-8")
            written += 1
    return written


def main() -> int:
    env_theme = os.environ.get("SITE_THEME", "default").strip() or "default"
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail if committed output is out of date")
    parser.add_argument(
        "--theme",
        choices=["default", "spacefast"],
        default=env_theme if env_theme in ("default", "spacefast") else "default",
        help="color theme to build (default: ODHS palette in site/; spacefast: Radix palette override)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="output directory for a standalone build (defaults to site-spacefast when --theme spacefast is used)",
    )
    args = parser.parse_args()
    try:
        outputs = build(theme=args.theme)
    except BuildError as error:
        print(error, file=sys.stderr)
        return 1

    if args.theme == "spacefast" or args.out is not None:
        out_dir = args.out if args.out is not None else (ROOT / "site-spacefast")
        if not out_dir.is_absolute():
            out_dir = ROOT / out_dir
        try:
            written = write_standalone_site(outputs, out_dir, args.theme)
        except BuildError as error:
            print(error, file=sys.stderr)
            return 1
        print(f"Wrote {written} site files and assets to {out_dir.relative_to(ROOT)}/ (theme: {args.theme}).")
        return 0

    if args.check:
        stale = []
        for path, content in outputs.items():
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(str(path.relative_to(ROOT)))
        if stale:
            print("Out of date. Run python3 tools/build.py and commit:\n  " + "\n  ".join(stale), file=sys.stderr)
            return 1
        print(f"Build is current ({len(outputs)} files).")
        return 0

    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(f"Wrote {len(outputs)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
