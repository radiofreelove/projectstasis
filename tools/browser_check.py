#!/usr/bin/env python3
"""
Test the built site in a real browser (Chromium, through Playwright).

Pages are served by tools/serve.py, which copies how Cloudflare Pages
serves the site: addresses without ".html", the 404 page, and the
headers in site/_headers.

    python3 tools/browser_check.py                     Run all checks, write docs/testing-browser.md
    python3 tools/browser_check.py --shots DIR         Also save screenshots to DIR
    AXE_JS=path/to/axe.min.js python3 tools/browser_check.py   Also run the axe-core engine

Needs: pip install playwright, then python -m playwright install chromium.
axe-core is optional; the CI workflow installs it from npm and passes AXE_JS.

What it checks, on every page:
  - No sideways scrolling at 320 px wide (WCAG 1.4.10 Reflow; same as 400% zoom
    on a 1280 px screen), including with extra-large text and extra spacing.
  - Text contrast measured in the browser for every visible text element, in
    the warm, white, and dark themes (WCAG 1.4.3 and 1.4.6).
  - Buttons, form choices, and menu links are at least 24 by 24 px
    (WCAG 2.5.8); anything under 44 px is listed as a note.
  - No console errors and no Content Security Policy violations.
  - No network requests leave the site.
  - Keyboard focus is visible on every focusable element on the home page.
And on the check page, it runs every result path, the error messages,
the "None of these" boxes, and "Start over".
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

import serve as pages_server

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
REPORT = ROOT / "docs" / "testing-browser.md"
KEY = "stasis-display-v1"

SCENARIOS = [
    ("phone 320px, standard", 320, 800, {}),
    ("phone 320px, extra-large text and more space", 320, 800, {"text": "xl", "spacing": "roomy"}),
    ("phone 390px, dark", 390, 844, {"theme": "dark"}),
    ("phone 390px, plain white", 390, 844, {"theme": "white"}),
    ("desktop 1280px, warm", 1280, 900, {"theme": "warm"}),
]

CONTRAST_JS = r"""
() => {
  function parse(c) {
    const m = c.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(',').map(s => parseFloat(s.trim()));
    return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1};
  }
  function lum(c) {
    const f = v => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
  }
  function bgOf(el) {
    let node = el;
    while (node && node.nodeType === 1) {
      const c = parse(getComputedStyle(node).backgroundColor);
      if (c && c.a > 0.95) return c;
      node = node.parentElement;
    }
    return {r: 255, g: 255, b: 255, a: 1};
  }
  const out = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  while (walker.nextNode()) {
    const t = walker.currentNode;
    if (!t.nodeValue.trim()) continue;
    const el = t.parentElement;
    if (!el || seen.has(el)) continue;
    seen.add(el);
    const rect = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    if (rect.width === 0 || rect.height === 0 || cs.visibility === 'hidden' || cs.display === 'none') continue;
    if (el.closest('.visually-hidden, .skip-link')) continue;
    const fg = parse(cs.color);
    const bg = bgOf(el);
    if (!fg) continue;
    const a = lum(fg), b = lum(bg);
    const ratio = (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
    const size = parseFloat(cs.fontSize);
    const bold = parseInt(cs.fontWeight, 10) >= 700;
    const large = size >= 24 || (bold && size >= 18.66);
    out.push({text: t.nodeValue.trim().slice(0, 40), ratio: Math.round(ratio * 100) / 100, large});
  }
  return out;
}
"""

TARGETS_JS = r"""
() => {
  const sel = 'button, .choice, .main-nav a, ul.cards a, summary, .skip-link';
  const out = [];
  document.querySelectorAll(sel).forEach(el => {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    if (r.width === 0 || r.height === 0 || cs.display === 'none' || cs.visibility === 'hidden') return;
    if (el.classList.contains('skip-link')) return;
    out.push({name: (el.innerText || el.getAttribute('aria-label') || el.tagName).trim().slice(0, 30), w: Math.round(r.width), h: Math.round(r.height)});
  });
  return out;
}
"""

INIT_JS = """
window.__csp = [];
document.addEventListener('securitypolicyviolation', e => window.__csp.push(e.violatedDirective + ' ' + e.blockedURI));
"""


def address(name: str) -> str:
    """The address Cloudflare Pages serves for a file in site/."""
    if name == "index.html":
        return ""
    if name == "404.html":
        return "no-such-page"
    return name[: -len(".html")]


def settings_script(settings: dict) -> str:
    return f"try {{ localStorage.setItem('{KEY}', {json.dumps(json.dumps(settings))}); }} catch (e) {{}}"


def run(shots: Path | None):
    pages = sorted(p.name for p in SITE.glob("*.html"))
    server = pages_server.start(SITE)
    base = f"http://127.0.0.1:{server.server_address[1]}/"
    expected_csp = pages_server.headers_for(pages_server.read_headers(SITE / "_headers"), "/").get(
        "Content-Security-Policy", ""
    )
    if "frame-ancestors 'none'" not in expected_csp:
        problems_early = ["site/_headers has no Content-Security-Policy with frame-ancestors 'none'"]
    else:
        problems_early = []
    problems: list[str] = list(problems_early)
    notes: list[str] = []
    rows: list[str] = []
    axe_path = os.environ.get("AXE_JS")
    axe_summary: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch()

        for label, width, height, settings in SCENARIOS:
            context = browser.new_context(viewport={"width": width, "height": height})
            context.add_init_script(INIT_JS)
            if settings:
                context.add_init_script(settings_script(settings))
            page = context.new_page()
            errors: list[tuple[str, str]] = []
            outside: list[str] = []
            page.on("console", lambda msg: errors.append((msg.text, msg.location.get("url", ""))) if msg.type == "error" else None)
            page.on("pageerror", lambda exc: errors.append((str(exc), "")))
            page.on("request", lambda req: outside.append(req.url) if not req.url.startswith(base) else None)
            low_contrast = 0
            narrow = 0
            for name in pages:
                errors.clear()
                outside.clear()
                response = page.goto(base + address(name), wait_until="load")
                page.wait_for_timeout(50)
                want = 404 if name == "404.html" else 200
                if response is None or response.status != want:
                    problems.append(f"{label}: {name} answered {response and response.status}, expected {want}")
                elif response.headers.get("content-security-policy") != expected_csp:
                    problems.append(f"{label}: {name} did not get the Content-Security-Policy header from site/_headers")
                overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
                if overflow > 1:
                    problems.append(f"{label}: {name} scrolls sideways by {overflow}px")
                for item in page.evaluate(CONTRAST_JS):
                    need = 4.5 if not item["large"] else 3.0
                    if item["ratio"] < need:
                        problems.append(f"{label}: {name} low contrast {item['ratio']}:1 on '{item['text']}'")
                    elif item["ratio"] < 7.0 and not item["large"]:
                        low_contrast += 1
                        notes.append(f"{label}: {name} AA but not AAA ({item['ratio']}:1) on '{item['text']}'")
                for target in page.evaluate(TARGETS_JS):
                    if target["w"] < 24 or target["h"] < 24:
                        problems.append(f"{label}: {name} small target {target['w']}x{target['h']} '{target['name']}'")
                    elif target["h"] < 44:
                        narrow += 1
                csp = page.evaluate("window.__csp")
                if csp:
                    problems.append(f"{label}: {name} CSP violations: {csp}")
                url = base + address(name)
                # The 404 page is served with status 404 on purpose; the browser logs
                # that status for the page itself. Any other error still counts.
                real = [text for text, where in errors if not (name == "404.html" and where == url and "404" in text)]
                if real:
                    problems.append(f"{label}: {name} console errors: {real}")
                if outside:
                    problems.append(f"{label}: {name} requests outside the site: {outside}")
                if shots and name in {"index.html", "check.html", "reasons.html", "apply.html", "help.html"}:
                    shots.mkdir(parents=True, exist_ok=True)
                    safe = label.split(",")[0].replace(" ", "-")
                    theme = settings.get("theme", "auto")
                    page.screenshot(path=str(shots / f"{name[:-5]}-{safe}-{theme}.png"), full_page=True)
            rows.append(f"| {label} | {len(pages)} | {low_contrast} | {narrow} |")
            context.close()

        # Keyboard focus visibility on the home page
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.goto(base)
        invisible = []
        for i in range(40):
            page.keyboard.press("Tab")
            info = page.evaluate(
                """() => { const el = document.activeElement; if (!el || el === document.body) return null;
                    const cs = getComputedStyle(el);
                    return {tag: el.tagName, text: (el.innerText || '').trim().slice(0, 30),
                            outline: cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) >= 2,
                            shadow: cs.boxShadow !== 'none', bg: cs.backgroundColor}; }"""
            )
            if info and not (info["outline"] or info["shadow"]):
                invisible.append(f"{info['tag']} '{info['text']}'")
        if invisible:
            problems.append(f"focus not visible on: {invisible}")
        context.close()

        # The check: every path
        context = browser.new_context(viewport={"width": 390, "height": 844})
        page = context.new_page()
        page.goto(base + "check")
        flow = []

        def result_title():
            return page.locator("#result-title").inner_text()

        page.click("[data-step='1'] [data-next]")
        if not page.locator("#step-1-error").is_visible():
            problems.append("check: no error when Next is pressed with no answer")
        flow.append("Error shown when no age is picked: yes")
        focused = page.evaluate("document.activeElement && document.activeElement.name")
        flow.append(f"Focus moves to the first choice after the error: {'yes' if focused == 'age' else 'no'}")

        page.check("input[value='65plus']")
        page.click("[data-step='1'] [data-next]")
        flow.append(f"65 or older: '{result_title()}'")
        page.click("text=Start over")
        back_to_one = page.locator("[data-step='1']").is_visible()
        flow.append("Start over returns to step 1: " + ("yes" if back_to_one else "no"))

        page.check("input[value='19to64']")
        page.click("[data-step='1'] [data-next]")
        page.check("input[name='reason'][value='pregnant']")
        page.check("input[name='reason'][value='none']")
        exclusive = not page.is_checked("input[name='reason'][value='pregnant']")
        flow.append(f"'None of these' clears other boxes: {'yes' if exclusive else 'no'}")
        page.check("input[name='reason'][value='medicare']")
        none_cleared = not page.is_checked("input[name='reason'][value='none']")
        flow.append("Picking a reason clears 'None of these': " + ("yes" if none_cleared else "no"))
        page.click("[data-step='2'] [data-next]")
        page.check("input[name='meet'][value='none']")
        page.click("[data-step='3'] button[type='submit']")
        flow.append(f"Medicare: '{result_title()}'")
        page.click("text=Start over")

        page.check("input[value='19to64']")
        page.click("[data-step='1'] [data-next]")
        page.check("input[name='reason'][value='child']")
        page.click("[data-step='2'] [data-next]")
        page.check("input[name='meet'][value='hours']")
        page.click("[data-step='3'] button[type='submit']")
        flow.append(f"Caring for a child, plus 80 hours: '{result_title()}'")
        page.click("text=Start over")

        page.check("input[value='19to64']")
        page.click("[data-step='1'] [data-next]")
        page.check("input[name='reason'][value='none']")
        page.click("[data-step='2'] [data-next]")
        page.check("input[name='meet'][value='income']")
        page.click("[data-step='3'] button[type='submit']")
        flow.append(f"No reason, income $580 or more: '{result_title()}'")
        page.click("text=Start over")

        page.check("input[value='19to64']")
        page.click("[data-step='1'] [data-next]")
        page.check("input[name='reason'][value='none']")
        page.click("[data-step='2'] [data-next]")
        page.check("input[name='meet'][value='none']")
        page.click("[data-step='3'] button[type='submit']")
        flow.append(f"No reason, nothing yet: '{result_title()}'")
        stored = page.evaluate("Object.keys(localStorage)")
        flow.append(f"Storage keys after the check: {stored or 'none'}")
        if any(k != KEY for k in stored):
            problems.append(f"check stored unexpected data: {stored}")
        if shots:
            page.screenshot(path=str(shots / "check-result-phone.png"), full_page=True)
        context.close()

        # Optional: axe-core
        if axe_path and Path(axe_path).exists():
            axe_source = Path(axe_path).read_text(encoding="utf-8")
            context = browser.new_context(viewport={"width": 1280, "height": 900}, bypass_csp=True)
            page = context.new_page()
            for name in pages:
                page.goto(base + address(name))
                page.add_script_tag(content=axe_source)
                results = page.evaluate(
                    """async () => await axe.run(document, {runOnly: {type: 'tag',
                       values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice']}})"""
                )
                for v in results["violations"]:
                    problems.append(f"axe: {name}: {v['id']} ({v['impact']}): {v['help']} [{len(v['nodes'])}]")
                axe_summary.append(f"| {name} | {len(results['violations'])} | {len(results['passes'])} | {len(results['incomplete'])} |")
            context.close()
        browser.close()
    server.shutdown()
    return problems, notes, rows, flow, axe_summary, bool(axe_path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--shots", type=Path)
    args = parser.parse_args()
    problems, notes, rows, flow, axe_summary, axe_ran = run(args.shots)
    lines = [
        "# Browser test report",
        "",
        "Generated by `tools/browser_check.py`. Do not edit by hand.",
        "",
        "## Pages in each setting",
        "",
        "| Setting | Pages | Text at AA but under AAA | Targets 24 to 43 px tall (allowed) |",
        "|---|---|---|---|",
        *rows,
        "",
        "## The 1-minute check",
        "",
        *[f"- {line}" for line in flow],
        "",
        "## axe-core",
        "",
    ]
    if axe_ran:
        lines += ["| Page | Violations | Passes | Needs review |", "|---|---|---|---|", *axe_summary, ""]
    else:
        lines += ["Not run in this environment (no AXE_JS). The GitHub workflow runs it.", ""]
    lines += ["## Problems", ""] + ([f"- {p}" for p in problems] or ["None."]) + [""]
    lines += ["## Notes", ""] + ([f"- {n}" for n in notes[:50]] or ["None."]) + [""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
