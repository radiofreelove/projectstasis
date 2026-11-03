#!/usr/bin/env python3
"""
Structure, privacy, and accessibility lint for every page in site/.

    python3 tools/check_structure.py

Fails (exit 1) if any page breaks a rule below. Each rule names the
promise or standard it protects. Standard library only.

  1. <html lang="en"> is set (WCAG 3.1.1).
  2. Each page has a unique, non-empty <title> (WCAG 2.4.2).
  3. Exactly one <h1>, and headings never skip a level (WCAG 1.3.1, 2.4.6).
  4. A skip link points to #main, and #main exists (WCAG 2.4.1).
  5. header, nav, main, and footer landmarks exist (WCAG 1.3.1).
  6. Every <img> has an alt attribute (WCAG 1.1.1).
  7. Every visible input sits inside a <label> (WCAG 1.3.1, 3.3.2, 4.1.2).
  8. Every button has text (WCAG 4.1.2).
  9. IDs are unique, and every aria-labelledby or aria-describedby
     reference exists (WCAG 4.1.2).
 10. No inline style attributes, inline scripts, or on* handlers
     (needed for the Content Security Policy).
 11. The CSP meta tag blocks network requests (connect-src 'none',
     form-action 'none') and referrer is no-referrer (privacy page).
 12. No link opens a new window (target attribute) (COGA: no surprises).
 13. No form control mentions immigration or citizenship (promise on
     the check and immigration pages).
 14. Same-page links (#id) point to an element that exists.
 15. Links to other pages use the addresses Cloudflare Pages serves
     ("check", not "check.html", which would cost a redirect), and every
     link, image, script, and stylesheet in the site points to a file
     that exists.
 16. site/_headers sends the same Content Security Policy as the pages,
     plus frame-ancestors 'none' (other sites cannot frame the pages), and
     Referrer-Policy: no-referrer (privacy page).
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

import serve

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
FORBIDDEN_WORDS = ("immigra", "citizen")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.lang = None
        self.title = ""
        self.in_title = False
        self.headings = []
        self.ids = []
        self.refs = []
        self.hash_links = []
        self.landmarks = set()
        self.errors = []
        self.meta_csp = None
        self.meta_referrer = None
        self.label_depth = 0
        self.label_text = []
        self.labels = []
        self.button_depth = 0
        self.button_text = []
        self.script_open = False
        self.script_has_src = False
        self.script_text = []
        self.skip_link = False
        self.local_refs = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.stack.append(tag)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "title":
            self.in_title = True
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.headings.append(int(tag[1]))
        if tag in {"header", "nav", "main", "footer"}:
            self.landmarks.add(tag)
        if "id" in a:
            self.ids.append(a["id"])
        for key in ("aria-labelledby", "aria-describedby"):
            if a.get(key):
                self.refs.extend(a[key].split())
        if "style" in a:
            self.errors.append(f"inline style attribute on <{tag}>")
        for key in a:
            if key.startswith("on"):
                self.errors.append(f"inline event handler {key} on <{tag}>")
        if tag == "a":
            href = a.get("href", "")
            if "target" in a:
                self.errors.append(f"link opens a new window: {href}")
            if href.startswith("#") and len(href) > 1:
                self.hash_links.append(href[1:])
            if href == "#main" and "skip-link" in (a.get("class") or ""):
                self.skip_link = True
        for key in ("href", "src"):
            value = a.get(key)
            if value and tag in {"a", "link", "img", "script"}:
                if not value.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
                    self.local_refs.append(value)
        if tag == "img" and "alt" not in a:
            self.errors.append(f"image without alt: {a.get('src')}")
        if tag == "meta":
            if (a.get("http-equiv") or "").lower() == "content-security-policy":
                self.meta_csp = a.get("content", "")
            if a.get("name") == "referrer":
                self.meta_referrer = a.get("content")
        if tag == "label":
            self.label_depth += 1
            self.label_text = []
        if tag == "input" and a.get("type") not in {"hidden"}:
            if self.label_depth == 0:
                self.errors.append(f"input without a wrapping label: name={a.get('name')}")
        if tag == "button":
            self.button_depth += 1
            self.button_text = []
        if tag == "script":
            self.script_open = True
            self.script_has_src = "src" in a
            self.script_text = []

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "label" and self.label_depth:
            self.labels.append(" ".join("".join(self.label_text).split()))
            self.label_depth -= 1
        if tag == "button" and self.button_depth:
            if not "".join(self.button_text).strip():
                self.errors.append("button without text")
            self.button_depth -= 1
        if tag == "script" and self.script_open:
            if not self.script_has_src or "".join(self.script_text).strip():
                self.errors.append("inline script content (blocked by the CSP)")
            self.script_open = False
        if self.stack and tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.label_depth:
            self.label_text.append(data)
        if self.button_depth:
            self.button_text.append(data)
        if self.script_open:
            self.script_text.append(data)


def check(path: Path, titles: dict) -> list[str]:
    page = Page()
    page.feed(path.read_text(encoding="utf-8"))
    errors = list(page.errors)
    if page.lang != "en":
        errors.append("html lang is not 'en'")
    title = " ".join(page.title.split())
    if not title:
        errors.append("empty <title>")
    elif title in titles:
        errors.append(f"title also used by {titles[title]}")
    else:
        titles[title] = path.name
    if page.headings.count(1) != 1:
        errors.append(f"expected one <h1>, found {page.headings.count(1)}")
    for before, after in zip(page.headings, page.headings[1:]):
        if after > before + 1:
            errors.append(f"heading jumps from h{before} to h{after}")
            break
    if not page.skip_link or "main" not in page.ids:
        errors.append("skip link to #main is missing or broken")
    for landmark in ("header", "nav", "main", "footer"):
        if landmark not in page.landmarks:
            errors.append(f"missing <{landmark}>")
    seen = set()
    for element_id in page.ids:
        if element_id in seen:
            errors.append(f"duplicate id '{element_id}'")
        seen.add(element_id)
    for ref in page.refs:
        if ref not in seen:
            errors.append(f"aria reference to missing id '{ref}'")
    for target in page.hash_links:
        if target not in seen:
            errors.append(f"same-page link to missing id '#{target}'")
    csp = page.meta_csp or ""
    for needed in ("connect-src 'none'", "form-action 'none'", "script-src 'self'"):
        if needed not in csp:
            errors.append(f"CSP missing {needed}")
    if page.meta_referrer != "no-referrer":
        errors.append("referrer policy is not no-referrer")
    for ref in page.local_refs:
        target = ref.split("#", 1)[0]
        if re.search(r"\.html$", target):
            errors.append(f"link uses .html, which Cloudflare Pages would redirect: {ref}")
            continue
        name = target.lstrip("/")
        if name.startswith("./"):
            name = name[2:]
        if name in ("", "."):
            name = "index"
        if not ((SITE / name).is_file() or (SITE / f"{name}.html").is_file()):
            errors.append(f"link to a missing page or file: {ref}")
    for label in page.labels:
        lowered = label.lower()
        if any(word in lowered for word in FORBIDDEN_WORDS):
            errors.append(f"form control mentions immigration or citizenship: {label!r}")
    return errors


def check_headers(meta_csp: str) -> list[str]:
    errors = []
    sent = serve.headers_for(serve.read_headers(SITE / "_headers"), "/")
    csp = sent.get("Content-Security-Policy", "")
    if not csp:
        return ["site/_headers sends no Content-Security-Policy"]
    directives = {d.strip() for d in csp.split(";") if d.strip()}
    for needed in [d.strip() for d in meta_csp.split(";") if d.strip()] + ["frame-ancestors 'none'"]:
        if needed not in directives:
            errors.append(f"site/_headers Content-Security-Policy is missing {needed}")
    if sent.get("Referrer-Policy") != "no-referrer":
        errors.append("site/_headers does not send Referrer-Policy: no-referrer")
    return errors


def main() -> int:
    titles: dict[str, str] = {}
    failed = 0
    pages = sorted(SITE.glob("*.html"))
    first = Page()
    first.feed((SITE / "index.html").read_text(encoding="utf-8"))
    header_errors = check_headers(first.meta_csp or "")
    if header_errors:
        failed += 1
        print("_headers:")
        for error in header_errors:
            print(f"  - {error}")
    for path in pages:
        errors = check(path, titles)
        if errors:
            failed += 1
            print(f"{path.name}:")
            for error in errors:
                print(f"  - {error}")
    if failed:
        print(f"\n{failed} of {len(pages)} pages have problems.", file=sys.stderr)
        return 1
    print(f"All {len(pages)} pages and site/_headers pass the structure checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
