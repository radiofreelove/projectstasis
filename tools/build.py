#!/usr/bin/env python3
"""
Build The Stasis Project site.

    python3 tools/build.py           Write site/*.html, site/sitemap.xml,
                                     site/robots.txt, site/_headers,
                                     docs/sources.md, and docs/claims.md.
    python3 tools/build.py --check   Rebuild in memory and fail if any
                                     committed output is out of date.

Inputs
    src/pages/*.html    Page bodies, each starting with a metadata comment.
                        "section: utah" puts a page in the Utah guide; pages
                        without it belong to the Oregon guide. "shared: yes"
                        marks pages both guides need (About, Privacy,
                        Accessibility, Every source). A shared page is built
                        once for each guide, as "about" and "utah-about", so
                        a reader never leaves the guide they are in. Text
                        between <!-- oregon --> and <!-- /oregon --> (or
                        utah) appears only in that guide's copy, and
                        "utah_title", "utah_description", and "utah_sources"
                        replace the plain values in the Utah copy.
    data/sources.json   Registry of every outside source and link.
    data/claims.json    Ledger of every factual statement on the site.

The build refuses to finish if a page links to an address that is not in
the source registry, uses a claim that is not in the ledger, or uses a
claim whose sources are not listed for that page. That is how the site
keeps "each page lists the official sources behind it" true.

It also refuses to finish if a page in one guide links to a page in the
other guide (except the other guide's home page), lists the other state's
sources, or uses the other state's facts. That is how each guide stays
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
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "pages"
SITE = ROOT / "site"
DOCS = ROOT / "docs"
DATA = ROOT / "data"
FONTS = SITE / "assets" / "fonts"
FONTS_LOCK = ROOT / "fonts.lock.json"

SITE_NAME = "The Stasis Project"
TAGLINE = "OHP, made plain"
BASE_URL = "https://projectstasis.pages.dev/"
PROJECT_REPO = "https://github.com/radiofreelove/projectstasis"
# The day the whole Oregon guide was last re-checked against its sources.
# Sources re-read since then carry their own "checked" date in the registry,
# and every page shows that date next to each source.
FACTS_CHECKED_ISO = "2026-11-02"
# The day the whole Utah guide was last checked against its sources.
UTAH_FACTS_CHECKED_ISO = "2026-11-10"
VERSION = "0.2.0 beta"

AP_MONTHS = ["Jan.", "Feb.", "March", "April", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."]


def ap_date(iso: str) -> str:
    """2026-11-02 -> Nov. 2, 2026 (docs/style-guide.md: AP month style, always with the year)."""
    year, month, day = (int(part) for part in iso.split("-"))
    return f"{AP_MONTHS[month - 1]} {day}, {year}"


FACTS_CHECKED_TEXT = ap_date(FACTS_CHECKED_ISO)

NAV = [("index", "Home"), ("check", "Check"), ("apply", "Apply"), ("help", "Get help")]

# One guide per state. Every page belongs to one section, which sets its
# tagline, menu, footer text, and "facts last checked" date. See
# docs/decisions/0013-utah-section.md.
SECTIONS = {
    "oregon": {
        "tagline": TAGLINE,
        "prefix": "",
        "shared_order": 0,
        "home": "index",
        "nav": NAV,
        "facts_iso": FACTS_CHECKED_ISO,
        "explainer_kind": "state-explainer",
        "footer_why": (
            "The state explains the new OHP rules across more than a dozen documents. This site puts what "
            "applicants need in one place, in plain words. Each page lists the official sources behind it."
        ),
        "footer_independent": (
            "Not run by the State of Oregon, the Oregon Health Authority (OHA), or the Oregon Department of "
            "Human Services (ODHS). Only OHP decides who qualifies."
        ),
        "about_label": "Why this site exists",
        "other_guide": ("utah", "Utah Medicaid guide"),
    },
    "utah": {
        "tagline": "Utah Medicaid, made plain",
        # A shared page is built for this guide as "utah-" plus its slug,
        # and listed after the guide's own pages.
        "prefix": "utah-",
        "shared_order": 30,
        "home": "utah",
        "nav": [("utah", "Utah home"), ("utah-check", "Check"), ("utah-apply", "Apply"), ("utah-help", "Get help")],
        "facts_iso": UTAH_FACTS_CHECKED_ISO,
        "explainer_kind": "utah-explainer",
        "footer_why": (
            "Utah explains the new Medicaid rules across more than a dozen pages and papers. This guide puts "
            "what applicants need in one place, in plain words. Each page lists the official sources behind it."
        ),
        "footer_independent": (
            "Not run by the State of Utah, the Utah Department of Health and Human Services (DHHS), or the "
            "Utah Department of Workforce Services (DWS). Only the state decides who qualifies."
        ),
        "about_label": "Why this guide exists",
        "other_guide": ("index", "Oregon Health Plan guide"),
    },
    # Not a guide: the frame for a page that belongs to neither state, which
    # today is only the "page not found" page. Its menu is the two guides.
    "both": {
        "guide": False,
        "tagline": "OHP and Utah Medicaid, made plain",
        "prefix": "",
        "home": "index",
        "nav": [("index", "Oregon guide"), ("utah", "Utah guide")],
        "facts_iso": None,
        "footer_why": (
            "Oregon and Utah each explain their new Medicaid rules across more than a dozen documents. "
            "This site puts what applicants need in one place, in plain words, with one guide for each state."
        ),
        "footer_independent": (
            "Not run by the State of Oregon, the State of Utah, or any of their agencies. "
            "Only the state decides who qualifies."
        ),
        "about_label": "Why this site exists",
        "other_guide": None,
    },
}
GUIDES = {name: section for name, section in SECTIONS.items() if section.get("guide", True)}

# Source kinds that belong to the Oregon guide only. Utah sources are the
# ones whose IDs start with U. Every other kind (federal rule, court,
# standards, the host) may back a page in either guide.
OREGON_ONLY_KINDS = {"state-explainer", "state-page", "state-form", "advocacy"}
SECTION_BLOCK_RE = re.compile(r"[ \t]*<!-- (oregon|utah) -->\n(.*?)[ \t]*<!-- /\1 -->\n", re.S)

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


def parse_page(path: Path):
    text = path.read_text(encoding="utf-8")
    match = META_RE.match(text)
    if not match:
        raise BuildError(f"{path.name}: missing the metadata comment at the top")
    meta = {}
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise BuildError(f"{path.name}: bad metadata line {line!r}")
        meta[key.strip()] = value.strip()
    for required in ("slug", "order", "title", "short_title", "description"):
        if not meta.get(required):
            raise BuildError(f"{path.name}: metadata needs '{required}'")
    meta["order"] = int(meta["order"])
    meta["sources"] = [s.strip() for s in meta.get("sources", "").split(",") if s.strip()]
    meta["scripts"] = [s.strip() for s in meta.get("scripts", "").split(",") if s.strip()]
    meta["in_lists"] = meta.get("in_lists", "yes") != "no"
    meta["section"] = meta.get("section", "oregon")
    if meta["section"] not in SECTIONS:
        raise BuildError(f"{path.name}: unknown section {meta['section']!r}")
    meta["shared"] = meta.get("shared", "no") == "yes"
    meta["base_slug"] = meta["slug"]
    body = text[match.end():]
    return meta, body


def section_blocks(body: str, section: str) -> str:
    """Keep the blocks marked for this guide, and drop the other guide's."""
    return SECTION_BLOCK_RE.sub(lambda m: m.group(2) if m.group(1) == section else "", body)


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
        </fieldset>
        <fieldset>
          <legend>How much to show</legend>
          <label class="choice"><input type="radio" name="details" value="all" checked> Everything</label>
          <label class="choice"><input type="radio" name="details" value="fewer"> Just the key points</label>
        </fieldset>
        <div class="settings-actions">
          <button type="button" class="button-secondary" data-reset-settings>Reset to standard</button>
          <p>Your choices are saved on this device only.</p>
        </div>
      </div>
    </details>
    <p id="settings-status" class="visually-hidden" role="status" aria-live="polite"></p>
"""


def render_page(meta, body, pages, by_id, doc_counts):
    slug = meta["slug"]
    section = SECTIONS[meta["section"]]
    tagline = section["tagline"]
    facts_iso = section["facts_iso"]
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

    # "All pages": every page of this guide, including its own copy of the
    # shared pages, then one link to the other guide.
    own = [p for p in pages if p["in_lists"] and p["section"] == meta["section"]]
    footer_links = []
    for page in own:
        current = ' aria-current="page"' if page["slug"] == slug else ""
        footer_links.append(
            f'          <li><a href="{page["slug"]}.html"{current}>{esc(page["short_title"])}</a></li>'
        )
    if section["other_guide"]:
        other_slug, other_label = section["other_guide"]
        footer_links.append(f'          <li><a href="{other_slug}.html">{esc(other_label)}</a></li>')
    else:
        # Each guide already names the link to the other one; show both.
        footer_links = [
            f'          <li><a href="{guide_slug}.html">{esc(guide_label)}</a></li>'
            for guide_slug, guide_label in sorted(guide["other_guide"] for guide in GUIDES.values())
        ]

    scripts = "".join(
        f'\n  <script src="assets/js/{esc(name)}.js" defer></script>' for name in meta["scripts"]
    )
    sources_html = render_sources_section(meta["sources"], by_id) if meta["sources"] else ""
    body = body.replace("{{STATE_DOC_COUNT}}", str(doc_counts["oregon"]))
    body = body.replace("{{UTAH_DOC_COUNT}}", str(doc_counts["utah"]))
    body = body.replace("{{FACTS_CHECKED_TEXT}}", facts_text)
    body = body.replace("{{FACTS_CHECKED_ISO}}", facts_iso or "")

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
        <nav class="main-nav" aria-label="Main">
        <ul>
{chr(10).join(nav_links)}
        </ul>
        </nav>
      </div>
{SETTINGS_PANEL}    </div>
  </header>
  <main id="main" tabindex="-1">
    <div class="wrap">
    <p class="fewer-note">Some details are hidden. To see everything, open Display settings at the top.</p>
{body.rstrip()}
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
      <nav class="footer-pages" aria-label="{"All pages" if section["other_guide"] else "Both guides"}">
        <h2>{"All pages" if section["other_guide"] else "Both guides"}</h2>
        <ul>
{chr(10).join(footer_links)}
        </ul>
      </nav>
    </div>
  </footer>
</body>
</html>
"""


def is_utah_source(src) -> bool:
    """Utah sources carry IDs that start with U (U01, U15S, and so on)."""
    return src["id"].startswith("U")


def foreign_source(section: str, src) -> bool:
    """True if this source belongs to the other state's guide."""
    if section == "utah":
        return src["kind"] in OREGON_ONLY_KINDS
    return is_utah_source(src)


def render_sources_page_table(registry, section, used):
    """Each guide's "Every source" page lists that guide's sources only.

    The Utah page lists every Utah source, then the federal, court, and site
    sources that a Utah page lists or links to ("used"). The Oregon page lists
    every source that is not Utah's.
    """

    def group(title, anchor, sources):
        return (
            f'      <h2 id="{anchor}">{title}</h2>\n'
            '      <ol class="all-sources">\n' + "\n".join(source_rows(sources)) + "\n      </ol>\n"
        )

    if section == "utah":
        utah = [s for s in registry["sources"] if is_utah_source(s)]
        other = [s for s in registry["sources"] if not is_utah_source(s) and s["id"] in used]
        return group("Utah sources", "utah-sources", utah) + group(
            "Federal, court, and site sources", "other-sources", other
        )
    oregon = [s for s in registry["sources"] if not is_utah_source(s)]
    langs = registry["application_languages"]
    return (
        group("Oregon, federal, and site sources", "oregon-sources", oregon)
        + f'      <p>We also link to the paper application in {len(langs["items"])} languages, '
        'exactly as listed on OHA\'s how-to-apply page. See <a href="help.html#languages">Free help and other languages</a>.</p>\n'
    )


def source_rows(sources):
    rows = []
    pdf_tag = ' <span class="tag">PDF</span>'
    for src in sources:
        if src["opened"]:
            opened = "Yes"
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


def render_sitemap(pages):
    entries = []
    for page in pages:
        if not page["in_lists"]:
            continue
        loc = BASE_URL if page["slug"] == "index" else f"{BASE_URL}{page['slug']}"
        lastmod = SECTIONS[page["section"]]["facts_iso"] or FACTS_CHECKED_ISO
        entries.append(f"  <url><loc>{loc}</loc><lastmod>{lastmod}</lastmod></url>")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )


def render_robots():
    return f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}sitemap.xml\n"


def render_headers():
    lines = [
        "# Generated by tools/build.py. Do not edit by hand.",
        "# Cloudflare Pages sends these headers with every response from this site.",
        "# See docs/privacy.md and docs/decisions/0011-cloudflare-pages.md.",
        "/*",
    ]
    lines += [f"  {name}: {value}" for name, value in HEADERS]
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
        "| ID | Source | Kind | Date on it | Checked | Read by us | Notes |",
        "|---|---|---|---|---|---|---|",
    ]
    for src in registry["sources"]:
        read = "Yes" if src["opened"] else f"No, address from {src.get('linked_from', 'another source')}"
        lines.append(
            f"| {src['id']} | [{md_escape(src['title'])}]({src['url']}) ({md_escape(src['publisher'])}) | "
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
    lines += ["", "| ID | Kind | Statement on the site | Sources | Pages | Notes |", "|---|---|---|---|---|---|"]
    for claim in claims["claims"]:
        srcs = ", ".join(f"[{sid}]({by_id[sid]['url']})" for sid in claim["sources"]) or "None (design)"
        pages = ", ".join(sorted(usage.get(claim["id"], []))) or "Not used"
        lines.append(
            f"| {claim['id']} | {claim['kind']} | {md_escape(claim['statement'])} | {srcs} | {pages} | "
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


def build():
    registry = load_json(DATA / "sources.json")
    claims = load_json(DATA / "claims.json")
    by_id, known_urls = registry_maps(registry)
    claim_by_id = {c["id"]: c for c in claims["claims"]}
    errors = []

    for claim in claims["claims"]:
        for sid in claim["sources"]:
            if sid not in by_id:
                errors.append(f"claim {claim['id']}: unknown source {sid}")
        if claim["kind"] not in {"fact", "math", "inference", "design", "tip"}:
            errors.append(f"claim {claim['id']}: unknown kind {claim['kind']}")
        if claim["kind"] in {"fact", "math", "inference"} and not claim["sources"]:
            errors.append(f"claim {claim['id']}: kind {claim['kind']} needs at least one source")

    doc_counts = {}
    for name, section in GUIDES.items():
        doc_counts[name] = sum(1 for s in registry["sources"] if s["kind"] == section["explainer_kind"])
        if doc_counts[name] <= 12:
            errors.append(
                f"the {name} guide says 'more than a dozen' but the registry counts {doc_counts[name]} "
                f"'{section['explainer_kind']}' entries"
            )

    for src in registry["sources"]:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", src.get("checked", "")):
            errors.append(f"source {src['id']}: 'checked' must be a date like 2026-11-02")

    parsed = [(path.name, *parse_page(path)) for path in sorted(SRC.glob("*.html"))]
    shared_slugs = {meta["slug"] for _, meta, _ in parsed if meta["shared"]}
    pages = []
    for file_name, meta, body in parsed:
        for page in variants(meta, body):
            # Name both the file and the built page in error messages.
            page["file"] = file_name if page["slug"] == meta["slug"] else f"{file_name} (as {page['slug']})"
            page["body"] = localize_links(page["body"], page["section"], shared_slugs)
            pages.append(page)
    pages.sort(key=lambda p: p["order"])
    slugs = {p["slug"] for p in pages}
    if len(slugs) != len(pages):
        errors.append("two pages share one slug")
    section_of = {p["slug"]: p["section"] for p in pages}
    homes = {section["home"] for section in GUIDES.values()}
    by_url = {s["url"]: s for s in registry["sources"]}
    oregon_form_urls = {item["url"] for item in registry["application_languages"]["items"]}

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

        for sid in page["sources"]:
            if sid not in by_id:
                errors.append(f"{page['file']}: lists unknown source {sid}")
            elif foreign_source(name, by_id[sid]):
                errors.append(f"{page['file']}: lists {sid}, a source that belongs to the other state's guide")

        for attr in CLAIM_RE.findall(body):
            for cid in attr.split():
                usage.setdefault(cid, set()).add(page["slug"])
                if cid.startswith("U-") and name != "utah":
                    errors.append(f"{page['file']}: uses {cid}, a fact that belongs to the Utah guide")
                claim = claim_by_id.get(cid)
                if not claim:
                    errors.append(f"{page['file']}: uses unknown claim {cid}")
                    continue
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
                    or (name == "utah" and href in oregon_form_urls)
                ):
                    errors.append(f"{page['file']}: links to the other state's source: {href}")
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
                            f"{page['file']}: links to {href}, a page in the other guide. "
                            "Only the other guide's home page may be linked."
                        )
                elif not (SITE / target).exists():
                    errors.append(f"{page['file']}: link to missing file {href}")

        rendered = localize_links(render_page(page, body, pages, by_id, doc_counts), name, shared_slugs)
        rendered = pretty_links(rendered)
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

    outputs[SITE / "sitemap.xml"] = render_sitemap(pages)
    outputs[SITE / "robots.txt"] = render_robots()
    outputs[SITE / "_headers"] = render_headers()
    outputs[DOCS / "sources.md"] = render_sources_md(registry)
    outputs[DOCS / "claims.md"] = render_claims_md(claims, by_id, usage)

    errors.extend(check_fonts())

    if errors:
        raise BuildError("Build stopped:\n  - " + "\n  - ".join(errors))
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail if committed output is out of date")
    args = parser.parse_args()
    try:
        outputs = build()
    except BuildError as error:
        print(error, file=sys.stderr)
        return 1

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
