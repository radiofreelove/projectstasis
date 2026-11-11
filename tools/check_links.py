#!/usr/bin/env python3
"""
Check that every official link still works.

    python3 tools/check_links.py                 Check and print a report
    python3 tools/check_links.py --report FILE   Also write the report to FILE

Reads every address from data/sources.json (sources and paper application
languages). For each one it:

  1. Skips the address if its registry entry says "link_check": "by hand".
     Those sites block automated tools, and docs/maintenance.md has a
     person open them at least every 30 days.
  2. Reads the site's robots.txt and skips the address if automated
     visitors are not allowed. Those are listed for a person to check.
  3. Sends a HEAD request, then a GET request if HEAD fails for any reason.
     Some servers refuse HEAD and answer GET, so only GET decides.
  4. Waits between requests to the same site, to be polite.

Some official sites send an incomplete certificate chain. Browsers fill
the gap; this tool cannot, so it cannot verify the site. For that one
problem only, it asks again without verifying, to learn whether the
address still answers. Nothing is sent but the request, and nothing in
the reply is used but its status. If the address answers, it is listed
under "Check by hand" with a note. If it does not, it is broken. Any
other certificate problem (expired, wrong name, self-signed) counts as
broken, because a reader's browser would warn about it too.

Exit code 1 if any address is broken (HTTP 400 or higher, or no answer).
"Check by hand" addresses do not change the exit code. The weekly
workflow opens a GitHub issue with the report when the exit code is 1.
Standard library only.
"""
from __future__ import annotations

import argparse
import json
import ssl
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


# OpenSSL's codes for "the site did not send its whole certificate chain":
# 20 = unable to get local issuer certificate, 21 = unable to verify the
# first certificate. Browsers fetch the missing piece; this tool cannot.
INCOMPLETE_CHAIN = {20, 21}
UNVERIFIED = ssl.create_default_context()
UNVERIFIED.check_hostname = False
UNVERIFIED.verify_mode = ssl.CERT_NONE
# Hosts found to send an incomplete chain during this run.
UNVERIFIABLE_HOSTS: set[str] = set()


def addresses(registry_path: Path | None = None):
    """Every address to check, as (id, url, by_hand)."""
    path = registry_path or ROOT / "data" / "sources.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    seen = []
    for src in registry["sources"]:
        seen.append((src["id"], src["url"], src.get("link_check") == "by hand"))
    for item in registry["application_languages"]["items"]:
        seen.append((f"7210-{item['hreflang']}", item["url"], False))
    return seen


def incomplete_chain(error: Exception) -> bool:
    """True if the only problem is a certificate chain this tool cannot complete."""
    reason = getattr(error, "reason", error)
    return isinstance(reason, ssl.SSLCertVerificationError) and reason.verify_code in INCOMPLETE_CHAIN


def open_url(request: urllib.request.Request):
    """Open a request, without verifying only for hosts known to send an incomplete chain."""
    host = urlsplit(request.full_url).netloc
    if host in UNVERIFIABLE_HOSTS:
        return urllib.request.urlopen(request, timeout=TIMEOUT, context=UNVERIFIED)
    return urllib.request.urlopen(request, timeout=TIMEOUT)


ROBOTS: dict[str, urllib.robotparser.RobotFileParser | None] = {}


def allowed(url: str) -> bool:
    parts = urlsplit(url)
    base = f"{parts.scheme}://{parts.netloc}"
    if base not in ROBOTS:
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(base + "/robots.txt")
        request = urllib.request.Request(base + "/robots.txt", headers={"User-Agent": USER_AGENT})
        for attempt in (1, 2):
            try:
                with open_url(request) as response:
                    parser.parse(response.read().decode("utf-8", "replace").splitlines())
                ROBOTS[base] = parser
            except urllib.error.HTTPError as error:
                # No robots.txt (404) means everything is allowed; 401/403 means stay out.
                ROBOTS[base] = None if error.code >= 500 or error.code in (404, 410) else "deny"  # type: ignore
            except Exception as error:
                if attempt == 1 and incomplete_chain(error):
                    # Read the site's rules anyway, so they are still respected.
                    UNVERIFIABLE_HOSTS.add(parts.netloc)
                    continue
                ROBOTS[base] = None
            break
    rules = ROBOTS[base]
    if rules == "deny":
        return False
    if rules is None:
        return True
    return rules.can_fetch(USER_AGENT, url)


def probe(url: str):
    """Return (status, final address, error text, certificate note).

    HEAD first, because it is cheap. If HEAD fails in any way, GET decides:
    some servers answer 401 or 403 to HEAD and 200 to GET.
    """
    host = urlsplit(url).netloc
    chain_error = None
    for method in ("HEAD", "GET", "GET"):
        request = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
        try:
            with open_url(request) as response:
                return response.status, response.geturl(), None, chain_error
        except urllib.error.HTTPError as error:
            if method == "HEAD":
                continue
            return error.code, url, str(error.reason), chain_error
        except Exception as error:  # network failure, timeout, TLS
            if incomplete_chain(error) and host not in UNVERIFIABLE_HOSTS:
                chain_error = str(getattr(error, "reason", error))
                UNVERIFIABLE_HOSTS.add(host)
                continue
            if method == "HEAD":
                continue
            return None, url, str(error), chain_error
    return None, url, "no answer", chain_error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--registry", type=Path, help="a registry file to check instead of data/sources.json (for tests)")
    args = parser.parse_args()

    broken, manual, good = [], [], []
    last_host_time: dict[str, float] = {}
    for source_id, url, by_hand in addresses(args.registry):
        if by_hand:
            manual.append((source_id, url, "the registry says this site blocks automated tools; "
                                           "a person opens it at least every 30 days (docs/maintenance.md)"))
            continue
        host = urlsplit(url).netloc
        wait = PAUSE - (time.time() - last_host_time.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        if not allowed(url):
            manual.append((source_id, url, "robots.txt asks automated visitors not to load this address"))
            continue
        status, final, error, chain_error = probe(url)
        last_host_time[host] = time.time()
        if status is None or status >= 400:
            broken.append((source_id, url, f"{status or 'no answer'} {error or ''}".strip()))
        elif chain_error or host in UNVERIFIABLE_HOSTS:
            manual.append((source_id, url, f"answers ({status}), but this tool could not verify the site's "
                                           "certificate because the site sends an incomplete chain. "
                                           "Open it in a browser"))
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
