#!/usr/bin/env python3
"""
Check that every official link still works.

    python3 tools/check_links.py                 Check and print a report
    python3 tools/check_links.py --report FILE   Also write the report to FILE

Reads every address from data/sources.json (sources and paper application
languages). For each one it:

  1. Reads the site's robots.txt and skips the address if automated
     visitors are not allowed. Those are listed for a person to check.
  2. Sends a HEAD request, then a GET request if HEAD is refused.
  3. Waits between requests to the same site, to be polite.

Exit code 1 if any allowed address is broken (HTTP 400 or higher, or no
answer). The weekly workflow opens a GitHub issue with the report.
Standard library only.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
import urllib.robotparser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
USER_AGENT = "StasisLinkCheck/1.0 (+https://github.com/radiofreelove/projectstasis)"
TIMEOUT = 25
PAUSE = 1.5


def addresses():
    registry = json.loads((ROOT / "data" / "sources.json").read_text(encoding="utf-8"))
    seen = []
    for src in registry["sources"]:
        seen.append((src["id"], src["url"]))
    for item in registry["application_languages"]["items"]:
        seen.append((f"7210-{item['hreflang']}", item["url"]))
    return seen


ROBOTS: dict[str, urllib.robotparser.RobotFileParser | None] = {}


def allowed(url: str) -> bool:
    parts = urlsplit(url)
    base = f"{parts.scheme}://{parts.netloc}"
    if base not in ROBOTS:
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(base + "/robots.txt")
        try:
            request = urllib.request.Request(base + "/robots.txt", headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                parser.parse(response.read().decode("utf-8", "replace").splitlines())
            ROBOTS[base] = parser
        except urllib.error.HTTPError as error:
            # No robots.txt (404) means everything is allowed; 401/403 means stay out.
            ROBOTS[base] = None if error.code >= 500 or error.code in (404, 410) else "deny"  # type: ignore
        except Exception:
            ROBOTS[base] = None
    rules = ROBOTS[base]
    if rules == "deny":
        return False
    if rules is None:
        return True
    return rules.can_fetch(USER_AGENT, url)


def probe(url: str):
    last_error = None
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                return response.status, response.geturl(), None
        except urllib.error.HTTPError as error:
            last_error = error
            if method == "HEAD" and error.code in (400, 403, 405, 406, 429, 501):
                continue
            return error.code, url, str(error.reason)
        except Exception as error:  # network failure, timeout, TLS
            last_error = error
            if method == "HEAD":
                continue
            return None, url, str(error)
    return None, url, str(last_error)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    broken, manual, good = [], [], []
    last_host_time: dict[str, float] = {}
    for source_id, url in addresses():
        host = urlsplit(url).netloc
        wait = PAUSE - (time.time() - last_host_time.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        if not allowed(url):
            manual.append((source_id, url, "robots.txt asks automated visitors not to load this address"))
            continue
        status, final, error = probe(url)
        last_host_time[host] = time.time()
        if status is None or status >= 400:
            broken.append((source_id, url, f"{status or 'no answer'} {error or ''}".strip()))
        else:
            note = "" if final == url else f"redirects to {final}"
            good.append((source_id, url, note))

    lines = ["# Link check report", "", f"Checked {len(good) + len(broken) + len(manual)} addresses.", ""]
    lines += [f"## Broken ({len(broken)})", ""] + [f"- {i}: {u} ({why})" for i, u, why in broken] + [""]
    lines += [f"## Check by hand ({len(manual)})", ""] + [f"- {i}: {u} ({why})" for i, u, why in manual] + [""]
    lines += [f"## Working ({len(good)})", ""] + [f"- {i}: {u}{' (' + n + ')' if n else ''}" for i, u, n in good] + [""]
    report = "\n".join(lines)
    print(report)
    if args.report:
        args.report.write_text(report, encoding="utf-8")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
