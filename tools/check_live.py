#!/usr/bin/env python3
"""
Check what Cloudflare actually serves at the live address.

    python3 tools/check_live.py                   Check https://projectstasis.pages.dev/
    python3 tools/check_live.py --base URL        Check another address, such as a preview
    python3 tools/check_live.py --report FILE     Also write a Markdown report
    python3 tools/check_live.py --wait 900        Keep trying for up to 900 seconds, for
                                                  use right after a push while Cloudflare
                                                  publishes the new version

The other checks test the files in this repository. This one tests the
live site, so a host setting (for example, a dashboard switch that adds an
analytics script) cannot quietly change what visitors get. It fails if:

  - any page or asset in site/ does not load, or differs by even one byte
    from the file in this repository;
  - a response is missing a header that site/_headers promises, such as
    the Content Security Policy with frame-ancestors 'none';
  - a missing address does not get the 404 page with status 404;
  - an old ".html" address does not redirect to the page's real address.

Needs internet. Standard library only.
"""
from __future__ import annotations

import argparse
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import serve
from build import BASE_URL, PROJECT_REPO

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
USER_AGENT = f"StasisLiveCheck/1.0 (+{PROJECT_REPO})"
NOT_SERVED = {"_headers", "_redirects"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(url: str, follow: bool = True):
    """Return (status, headers, body) without raising on 4xx or 3xx."""
    handlers = [] if follow else [NoRedirect()]
    opener = urllib.request.build_opener(*handlers)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with opener.open(request, timeout=30) as response:
            return response.status, response.headers, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.headers, error.read()
    except (urllib.error.URLError, OSError) as error:
        return 0, {}, str(error).encode()


def address(relative: str) -> str:
    """The address Cloudflare Pages serves for a file in site/."""
    if relative == "index.html":
        return ""
    if relative.endswith(".html") and "/" not in relative:
        return relative[: -len(".html")]
    return relative


def first_difference(live: bytes, local: bytes) -> str:
    for index, (a, b) in enumerate(zip(live, local)):
        if a != b:
            start = max(0, index - 40)
            snippet = live[start : index + 80].decode("utf-8", "replace").replace("\n", " ")
            return f"first difference at byte {index}: ...{snippet}..."
    return f"live is {len(live)} bytes, the repository file is {len(local)} bytes"


def run(base: str) -> tuple[list[str], list[str]]:
    base = base if base.endswith("/") else base + "/"
    problems: list[str] = []
    passed: list[str] = []
    promised = serve.headers_for(serve.read_headers(SITE / "_headers"), "/")

    def check_headers(label: str, headers) -> None:
        for name, value in promised.items():
            if headers.get(name) != value:
                problems.append(f"{label}: header {name} is {headers.get(name)!r}, expected {value!r}")

    files = sorted(
        p.relative_to(SITE).as_posix()
        for p in SITE.rglob("*")
        if p.is_file() and p.name not in NOT_SERVED and p.name != "404.html"
    )
    for relative in files:
        url = base + address(relative)
        status, headers, body = fetch(url)
        if status != 200:
            problems.append(f"{url}: status {status}, expected 200")
            continue
        local = (SITE / relative).read_bytes()
        if body != local:
            problems.append(f"{url}: differs from site/{relative} ({first_difference(body, local)})")
            continue
        check_headers(url, headers)
        passed.append(f"{url} matches site/{relative}")

    missing = base + "this-address-does-not-exist"
    status, headers, body = fetch(missing)
    if status != 404:
        problems.append(f"{missing}: status {status}, expected 404")
    elif body != (SITE / "404.html").read_bytes():
        problems.append(f"{missing}: the 404 page differs from site/404.html")
    else:
        check_headers(missing, headers)
        passed.append(f"{missing} gets site/404.html with status 404")

    old = base + "check.html"
    status, headers, _ = fetch(old, follow=False)
    location = headers.get("Location", "") if headers else ""
    if status not in (301, 302, 307, 308) or not location.rstrip("/").endswith("/check"):
        problems.append(f"{old}: expected a redirect to /check, got status {status} to {location!r}")
    else:
        passed.append(f"{old} redirects ({status}) to {location}")

    for name in NOT_SERVED:
        status, _, _ = fetch(base + name)
        if status == 200 and name == "_headers":
            problems.append(f"{base}{name} is served publicly; Cloudflare should only read it")
    return problems, passed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", default=BASE_URL)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--wait", type=int, default=0, help="seconds to keep retrying until the site matches")
    args = parser.parse_args()
    deadline = time.monotonic() + args.wait
    problems, passed = run(args.base)
    while problems and time.monotonic() < deadline:
        print(f"Not matching yet ({len(problems)} problems). Trying again in 30 seconds.", flush=True)
        time.sleep(30)
        problems, passed = run(args.base)
    lines = [f"## Live site check ({args.base})", ""]
    if problems:
        lines += ["Problems:", ""] + [f"- {p}" for p in problems] + [""]
    lines += [f"{len(passed)} checks passed."]
    report = "\n".join(lines) + "\n"
    print(report)
    if args.report:
        args.report.write_text(report, encoding="utf-8")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
