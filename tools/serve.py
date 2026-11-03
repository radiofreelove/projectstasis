#!/usr/bin/env python3
"""
Serve site/ on your computer the way Cloudflare Pages serves it.

    python3 tools/serve.py               then open http://127.0.0.1:8000
    python3 tools/serve.py --port 9000

It copies the Cloudflare Pages behavior this site depends on (see
docs/decisions/0011-cloudflare-pages.md):

  - /check serves check.html, and / serves index.html.
  - /check.html redirects to /check with status 308, as Pages does.
  - An address with no file gets 404.html with status 404.
  - Every response carries the headers listed in site/_headers,
    including the Content Security Policy.
  - _headers itself is never served.

tools/browser_check.py uses this server, so the browser tests see the
same addresses and headers that visitors get. Standard library only.
"""
from __future__ import annotations

import argparse
import http.server
import threading
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
NOT_SERVED = {"/_headers", "/_redirects"}


def read_headers(path: Path) -> list[tuple[str, list[tuple[str, str]], list[str]]]:
    """Read a Cloudflare Pages _headers file into (pattern, headers to set, headers to detach)."""
    rules: list[tuple[str, list[tuple[str, str]], list[str]]] = []
    if not path.exists():
        return rules
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw[0].isspace():
            rules.append((raw.strip(), [], []))
            continue
        if not rules:
            raise ValueError(f"_headers: header line before any path: {raw.strip()!r}")
        line = raw.strip()
        if line.startswith("!"):
            rules[-1][2].append(line[1:].strip())
        else:
            name, sep, value = line.partition(":")
            if not sep:
                raise ValueError(f"_headers: line without a colon: {line!r}")
            rules[-1][1].append((name.strip(), value.strip()))
    return rules


def pattern_matches(pattern: str, path: str) -> bool:
    if "*" in pattern:
        prefix, _, suffix = pattern.partition("*")
        return path.startswith(prefix) and path.endswith(suffix)
    return path == pattern


def headers_for(rules, path: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for pattern, to_set, to_detach in rules:
        if not pattern_matches(pattern, path):
            continue
        for name, value in to_set:
            key = name.lower()
            if key in result:
                result[key] = (result[key][0], result[key][1] + ", " + value)
            else:
                result[key] = (name, value)
        for name in to_detach:
            result.pop(name.lower(), None)
    return {name: value for name, value in result.values()}


class PagesHandler(http.server.SimpleHTTPRequestHandler):
    """Static file handler with Cloudflare Pages addresses, 404 page, and headers."""

    site: Path = SITE

    def log_message(self, format, *args):  # noqa: A002 (name from the base class)
        pass

    def resolve(self) -> tuple[str, object]:
        path = urllib.parse.unquote(urllib.parse.urlsplit(self.path).path)
        if path in NOT_SERVED:
            return "missing", None
        if path.endswith("/index.html"):
            return "redirect", path[: -len("index.html")]
        if path.endswith(".html"):
            return "redirect", path[: -len(".html")]
        site = self.site.resolve()
        candidate = (site / path.lstrip("/")).resolve()
        if candidate != site and site not in candidate.parents:
            return "missing", None
        if candidate.is_dir():
            index = candidate / "index.html"
            return ("file", index) if index.is_file() else ("missing", None)
        if candidate.is_file():
            return "file", candidate
        page = candidate.with_name(candidate.name + ".html")
        if page.is_file():
            return "file", page
        return "missing", None

    def respond(self, send_body: bool) -> None:
        path = urllib.parse.urlsplit(self.path).path
        extra = headers_for(read_headers(self.site / "_headers"), path)
        kind, target = self.resolve()
        if kind == "redirect":
            self.send_response(308)
            self.send_header("Location", target or "/")
            self.send_header("Content-Length", "0")
            for name, value in extra.items():
                self.send_header(name, value)
            self.end_headers()
            return
        status = 200
        if kind == "missing":
            status = 404
            target = self.site / "404.html"
        body = Path(target).read_bytes()
        self.send_response(status)
        self.send_header("Content-Type", self.guess_type(str(target)))
        self.send_header("Content-Length", str(len(body)))
        for name, value in extra.items():
            self.send_header(name, value)
        self.end_headers()
        if send_body:
            self.wfile.write(body)

    def do_GET(self):  # noqa: N802 (name from the base class)
        self.respond(send_body=True)

    def do_HEAD(self):  # noqa: N802 (name from the base class)
        self.respond(send_body=False)


def start(site: Path = SITE, port: int = 0) -> http.server.ThreadingHTTPServer:
    """Start the server in a background thread and return it."""
    handler = type("SiteHandler", (PagesHandler,), {"site": site})
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    handler = type("SiteHandler", (PagesHandler,), {"site": SITE})
    server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"Serving site/ like Cloudflare Pages at http://127.0.0.1:{args.port}/ (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
