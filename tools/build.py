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
    data/sources.json   Registry of every outside source and link.
    data/claims.json    Ledger of every factual statement on the site.

The build refuses to finish if a page links to an address that is not in
the source registry, uses a claim that is not in the ledger, or uses a
claim whose sources are not listed for that page. That is how the site
keeps "each page lists the official sources behind it" true.

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
FACTS_CHECKED_ISO = "2026-11-02"
FACTS_CHECKED_TEXT = "Nov. 2, 2026"
VERSION = "0.1.2 beta"

NAV = [("index", "Home"), ("check", "Check"), ("apply", "Apply"), ("help", "Get help")]

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
    body = text[match.end():]
    return meta, body


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
        items.append(
            f'      <li id="src-{esc(source_id.lower())}"><a href="{esc(src["url"])}">{esc(src["title"])}</a>{fmt}<br>'
            f'{esc(src["publisher"])}. Date on it: {esc(dated)}.</li>'
        )
    return (
        '    <section class="sources" aria-labelledby="sources-title">\n'
        '      <h2 id="sources-title">Sources for this page</h2>\n'
        f'      <p>We checked these on <time datetime="{FACTS_CHECKED_ISO}">{FACTS_CHECKED_TEXT}</time>. '
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


def render_page(meta, body, pages, by_id, state_doc_count):
    slug = meta["slug"]
    if slug == "index":
        title_tag = f"{SITE_NAME}: {TAGLINE}"
    else:
        title_tag = f"{meta['title']} | {SITE_NAME}"

    nav_links = []
    for target, label in NAV:
        current = ' aria-current="page"' if target == slug else ""
        nav_links.append(f'          <li><a href="{target}.html"{current}>{esc(label)}</a></li>')

    footer_links = []
    for page in pages:
        if not page["in_lists"]:
            continue
        current = ' aria-current="page"' if page["slug"] == slug else ""
        footer_links.append(
            f'          <li><a href="{page["slug"]}.html"{current}>{esc(page["short_title"])}</a></li>'
        )

    scripts = "".join(
        f'\n  <script src="assets/js/{esc(name)}.js" defer></script>' for name in meta["scripts"]
    )
    sources_html = render_sources_section(meta["sources"], by_id) if meta["sources"] else ""
    body = body.replace("{{STATE_DOC_COUNT}}", str(state_doc_count))
    body = body.replace("{{FACTS_CHECKED_TEXT}}", FACTS_CHECKED_TEXT)
    body = body.replace("{{FACTS_CHECKED_ISO}}", FACTS_CHECKED_ISO)

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
        <p><strong>Independent guide.</strong> Not run by the state. <a href="about.html">Why this site exists</a>. <a href="about.html#report">Report a mistake</a>.</p>
      </div>
    </div>
    <div class="wrap">
      <div class="header-row">
        <a class="brand" href="index.html">
          <img src="assets/img/logo.svg" alt="" width="40" height="40">
          <span><span class="brand-name">{SITE_NAME}</span><span class="brand-tag">{TAGLINE}</span></span>
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
      <h2>Why this site exists</h2>
      <p>The state explains the new OHP rules across more than a dozen documents. This site puts what applicants need in one place, in plain words. Each page lists the official sources behind it.</p>
      <p><strong>Independent.</strong> Not run by the State of Oregon, the Oregon Health Authority (OHA), or the Oregon Department of Human Services (ODHS). Only OHP decides who qualifies.</p>
      <p><strong>Private.</strong> No accounts, ads, cookies, or tracking. <a href="privacy.html">How your privacy is protected</a>.</p>
      <p>Facts last checked <time datetime="{FACTS_CHECKED_ISO}">{FACTS_CHECKED_TEXT}</time>. Version {VERSION}. <a href="{PROJECT_REPO}">See how this site is made</a>.</p>
      <p>Words: <a href="{PROJECT_REPO}/blob/main/LICENSE">CC BY 4.0</a>. Code: <a href="{PROJECT_REPO}/blob/main/LICENSE-CODE">MIT</a>. <a href="about.html#license">Reuse this guide</a>.</p>
      <nav class="footer-pages" aria-label="All pages">
        <h2>All pages</h2>
        <ul>
{chr(10).join(footer_links)}
        </ul>
      </nav>
    </div>
  </footer>
</body>
</html>
"""


def render_sources_page_table(registry):
    rows = []
    pdf_tag = ' <span class="tag">PDF</span>'
    for src in registry["sources"]:
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
    langs = registry["application_languages"]
    return (
        '      <ol class="all-sources">\n' + "\n".join(rows) + "\n      </ol>\n"
        f'      <p>We also link to the paper application in {len(langs["items"])} languages, '
        'exactly as listed on OHA\'s how-to-apply page. See <a href="help.html#languages">Free help and other languages</a>.</p>\n'
    )


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
        entries.append(f"  <url><loc>{loc}</loc><lastmod>{FACTS_CHECKED_ISO}</lastmod></url>")
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

    state_doc_count = sum(1 for s in registry["sources"] if s["kind"] == "state-explainer")
    if state_doc_count <= 12:
        errors.append(
            f"the site says 'more than a dozen documents' but the registry counts {state_doc_count}"
        )

    pages = []
    for path in sorted(SRC.glob("*.html")):
        meta, body = parse_page(path)
        meta["body"] = body
        meta["file"] = path.name
        pages.append(meta)
    pages.sort(key=lambda p: p["order"])
    slugs = {p["slug"] for p in pages}

    usage: dict[str, set] = {}
    outputs: dict[Path, str] = {}

    for page in pages:
        body = page["body"]
        if "{{SOURCES_TABLE}}" in body:
            body = body.replace("{{SOURCES_TABLE}}", render_sources_page_table(registry))
        if "{{APPLICATION_LANGUAGES}}" in body:
            body = body.replace("{{APPLICATION_LANGUAGES}}", render_language_list(registry))

        for sid in page["sources"]:
            if sid not in by_id:
                errors.append(f"{page['file']}: lists unknown source {sid}")

        for attr in CLAIM_RE.findall(body):
            for cid in attr.split():
                usage.setdefault(cid, set()).add(page["slug"])
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
            elif href.startswith(("mailto:", "tel:")):
                continue
            elif href.startswith("#"):
                continue
            else:
                target = href.split("#", 1)[0]
                if target.endswith(".html"):
                    if target[:-5] not in slugs:
                        errors.append(f"{page['file']}: link to missing page {href}")
                elif not (SITE / target).exists():
                    errors.append(f"{page['file']}: link to missing file {href}")

        rendered = pretty_links(render_page(page, body, pages, by_id, state_doc_count))
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
