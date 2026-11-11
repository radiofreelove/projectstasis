"""
Tests for tools/check_links.py, against small servers on this computer.

    python3 -m unittest discover -s tools/tests

No request leaves the machine. Each server copies one way an official site
has answered the real link check:

  - a site whose certificate chain is incomplete (Oregon's forms site),
    with a page that is there, a page that is gone, and a robots.txt rule
  - a server that refuses HEAD but answers GET
  - a server that refuses both
  - a self-signed certificate, which a browser would warn about
  - a registry entry marked "link_check": "by hand", which must not be
    requested at all

The certificates are made fresh for each run with the openssl command.
If openssl is not installed, these tests are skipped.

Standard library only.
"""
from __future__ import annotations

import http.server
import json
import os
import shutil
import ssl
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent


def openssl(*args: str, cwd: Path):
    subprocess.run(["openssl", *args], cwd=cwd, check=True, capture_output=True)


def make_handler(routes: dict, robots: str | None, hits: list):
    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def answer(self, method: str):
            hits.append((method, self.path))
            if self.path == "/robots.txt":
                if robots is None:
                    self.send_response(404)
                    self.end_headers()
                    return
                body = robots.encode()
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                if method == "GET":
                    self.wfile.write(body)
                return
            code = routes.get((method, self.path), routes.get(self.path, 404))
            self.send_response(code)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def do_HEAD(self):
            self.answer("HEAD")

        def do_GET(self):
            self.answer("GET")

    return Handler


@unittest.skipUnless(shutil.which("openssl"), "the openssl command is not installed")
class LinkCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="stasis-link-test-"))
        cls.addClassCleanup(shutil.rmtree, cls.tmp, ignore_errors=True)
        cls.hits: list = []
        cls.servers: list = []
        cls.addClassCleanup(lambda: [server.shutdown() for server in cls.servers])

        # A private certificate authority signs "leaf". The servers send the
        # leaf alone, so a visitor cannot complete the chain: the same
        # problem as a site that leaves out its intermediate certificate.
        openssl("req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", "ca.key", "-out", "ca.pem",
                "-days", "2", "-subj", "/CN=Test CA", cwd=cls.tmp)
        openssl("req", "-newkey", "rsa:2048", "-nodes", "-keyout", "leaf.key", "-out", "leaf.csr",
                "-subj", "/CN=localhost", cwd=cls.tmp)
        (cls.tmp / "ext.cnf").write_text("subjectAltName=DNS:localhost,IP:127.0.0.1\nbasicConstraints=CA:FALSE\n")
        openssl("x509", "-req", "-in", "leaf.csr", "-CA", "ca.pem", "-CAkey", "ca.key", "-CAcreateserial",
                "-out", "leaf.pem", "-days", "2", "-extfile", "ext.cnf", cwd=cls.tmp)
        openssl("req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", "self.key", "-out", "self.pem",
                "-days", "2", "-subj", "/CN=localhost", "-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1",
                cwd=cls.tmp)

        incomplete = cls.serve({"/ok.pdf": 200, "/gone.pdf": 404}, cert="leaf")
        plain = cls.serve({("HEAD", "/head401"): 401, ("GET", "/head401"): 200, "/really401": 401, "/fine": 200})
        self_signed = cls.serve({"/x": 200}, cert="self")
        with_rules = cls.serve({"/private/a": 200, "/open": 200}, cert="leaf",
                               robots="User-agent: *\nDisallow: /private/\n")

        def source(source_id, url, **extra):
            return dict(id=source_id, url=url, **extra)

        registry = {
            "sources": [
                source("T1", f"https://127.0.0.1:{incomplete}/ok.pdf"),
                source("T2", f"https://127.0.0.1:{incomplete}/gone.pdf"),
                source("T3", f"http://127.0.0.1:{plain}/head401"),
                source("T4", f"http://127.0.0.1:{plain}/really401"),
                source("T5", f"http://127.0.0.1:{plain}/fine"),
                source("T6", f"https://127.0.0.1:{self_signed}/x"),
                source("T7", f"https://localhost:{with_rules}/private/a"),
                source("T8", f"https://localhost:{with_rules}/open"),
                source("T9", "http://127.0.0.1:9/never-requested", link_check="by hand"),
                source("T10", "http://127.0.0.1:9/closed-port"),
            ],
            "application_languages": {"items": [{"hreflang": "xx", "url": f"https://127.0.0.1:{incomplete}/ok.pdf"}]},
        }
        registry_path = cls.tmp / "registry.json"
        registry_path.write_text(json.dumps(registry), encoding="utf-8")

        # The tool must reach the test servers directly, not through a proxy.
        env = {key: value for key, value in os.environ.items() if "proxy" not in key.lower()}
        cls.result = subprocess.run(
            [sys.executable, str(TOOLS / "check_links.py"), "--registry", str(registry_path)],
            capture_output=True, text=True, env=env, timeout=180,
        )
        cls.report = cls.result.stdout

    @classmethod
    def serve(cls, routes: dict, cert: str | None = None, robots: str | None = None) -> int:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), make_handler(routes, robots, cls.hits))
        if cert:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(cls.tmp / f"{cert}.pem", cls.tmp / f"{cert}.key")
            server.socket = context.wrap_socket(server.socket, server_side=True)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        cls.servers.append(server)
        return server.server_address[1]

    def listed(self, heading: str) -> set:
        self.assertIn(f"## {heading}", self.report, self.result.stderr)
        part = self.report.split(f"## {heading}")[1].split("\n## ")[0]
        return {line.split(":")[0][2:] for line in part.splitlines() if line.startswith("- ")}

    def test_broken_means_gone_refused_or_a_certificate_a_browser_would_warn_about(self):
        # T2: page gone. T4: refused on HEAD and GET. T6: self-signed. T10: no answer.
        self.assertEqual(self.listed("Broken"), {"T2", "T4", "T6", "T10"})

    def test_what_the_tool_cannot_judge_goes_to_a_person(self):
        # T1 and the form: answer, but the chain is incomplete. T7, T8: same
        # site, one blocked by robots.txt. T9: marked by hand in the registry.
        self.assertEqual(self.listed("Check by hand"), {"T1", "T7", "T8", "T9", "7210-xx"})

    def test_get_decides_when_head_is_refused(self):
        self.assertEqual(self.listed("Working"), {"T3", "T5"})

    def test_a_by_hand_entry_is_never_requested(self):
        self.assertFalse([hit for hit in self.hits if "never-requested" in hit[1]])

    def test_robots_rules_are_respected_even_when_the_chain_is_incomplete(self):
        self.assertFalse([hit for hit in self.hits if hit[1] == "/private/a"])

    def test_only_broken_links_change_the_exit_code(self):
        self.assertEqual(self.result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
