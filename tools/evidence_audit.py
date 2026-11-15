#!/usr/bin/env python3
"""
Record what every official source says, and report when that changes.

    python3 tools/evidence_audit.py --report FILE    Fetch every source, compare
                                                     it with the baseline, and
                                                     write a report to FILE
    python3 tools/evidence_audit.py --write-baseline Fetch every source and
                                                     record what it says now
    python3 tools/evidence_audit.py --only S07 U02   Only these sources (works
                                                     with both modes)

The link check (tools/check_links.py) asks whether a source still answers.
This tool asks whether it still says the same thing. For every source in
data/sources.json it:

  1. Skips the address if its registry entry says "link_check": "by hand",
     and skips it if the site's robots.txt asks automated visitors to stay
     out. It uses the link check's own robots.txt reader, user agent, time
     limit, and pause between requests to one site.
  2. Sends a HEAD request, then a GET request for the content. As in the
     link check, only GET decides. If the reply is cut short, it waits and
     asks one more time; a partial reply is never compared.
  3. Turns the content into text that can be compared. For a web page:
     the words a reader sees, with tags, scripts, and styles removed and
     runs of spaces made into one. A PDF is not turned into text, because
     the project declares no PDF library; its raw bytes are compared, and
     the baseline marks it "mode": "bytes". A report that a "bytes" source
     changed is lower-confidence: a PDF saved again with the same words
     has new bytes.
  4. Compares the SHA-256 of that content with data/evidence_baseline.json.

Every source ends in one state:

  unchanged        The content matches the baseline.
  changed          It differs. For a web page the report shows what changed,
                   up to a limit, and names the facts and guide pages that
                   rest on the source.
  unreachable      The connection failed or the server answered with an
                   error.
  checker-blocked  The site answered 401 or 403, its robots.txt keeps this
                   tool out, or the registry says a person opens it by hand.
                   This says nothing about the source: it is not a dead
                   link and not a removed document.

A source the tool can read but that has no hash in the baseline is listed
as "not yet baselined". A missing baseline is never counted as a change.

The baseline holds hashes, not text. To show what changed, the tool keeps
the text of each web page in a folder that is not committed (--snapshots,
by default .evidence-snapshots/). It saves a page's text there when the
baseline is written, and whenever a page matches its baseline. If the old
text is not on hand, the report says so and shows no diff.

Some official sites send an incomplete certificate chain (see the link
check). This tool reads those too, and marks them, because the content
came over a connection it could not verify.

Exit code 1 if any source changed, otherwise 0. Blocked and unreachable
sources are reported and do not change the exit code; the link check is
what fails on an address that stopped answering.
Standard library only.
"""
from __future__ import annotations

import argparse
import datetime
import difflib
import hashlib
import http.client
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_links as links  # noqa: E402  (the same visitor, rules, and pauses as the link check)

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "data" / "evidence_baseline.json"
SNAPSHOTS = ROOT / ".evidence-snapshots"

UNCHANGED, CHANGED, UNREACHABLE, BLOCKED = "unchanged", "changed", "unreachable", "checker-blocked"
# Not a fifth verdict on the source: the tool read it, and there is nothing to compare it with.
NOT_BASELINED = "not yet baselined"
FETCHED = "fetched"

# Stop reading a reply after this many bytes. The largest source is far smaller.
MAX_BYTES = 60_000_000
# Limits on what a report quotes, so the weekly issue stays readable and
# under GitHub's size limit for an issue.
DIFF_LINES = 40
DIFF_LINE_CHARS = 240
DIFF_BUDGET = 24_000

BASELINE_NOTES = (
    "What each source in data/sources.json returned to tools/evidence_audit.py on its 'fetched' date. "
    "'mode' is how it is compared: 'text' is the readable words of a web page; 'bytes' is the raw file "
    "(every PDF), so a change report for it is lower-confidence. 'sha256' and 'length' describe that "
    "content. An entry with no 'sha256' was blocked or unreachable and has no baseline yet. "
    "'registry_checked' is the source's 'checked' date in the registry when this entry was written: "
    "the verified check this entry rests on. Writing a baseline is not a read of the source. "
    "Refresh an entry only on purpose, after a person has re-read the source (docs/maintenance.md)."
)


# ---------------------------------------------------------------------------
# Turning content into text that can be compared

# Their content is not words on the page.
SKIPPED_TAGS = {"script", "style", "template", "svg"}
# Tags that start a new line of text, so a diff shows one sentence or item per line.
BLOCK_TAGS = {
    "address", "article", "aside", "blockquote", "br", "dd", "div", "dl", "dt", "fieldset", "figcaption",
    "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "header", "hr", "li", "main", "nav",
    "ol", "option", "p", "pre", "section", "table", "td", "th", "title", "tr", "ul",
}


class ReadableText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skipping = 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIPPED_TAGS:
            self.skipping += 1
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in SKIPPED_TAGS:
            self.skipping = max(0, self.skipping - 1)
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skipping:
            # A line break in the page's source is only a space to a reader.
            lead = " " if data[:1].isspace() else ""
            trail = " " if data[-1:].isspace() else ""
            self.parts.append(lead + " ".join(data.split()) + trail)


def collapse(text: str) -> str:
    """One line per block of text, single spaces, no empty lines."""
    text = unicodedata.normalize("NFC", text)
    lines = (" ".join(line.split()) for line in text.split("\n"))
    return "\n".join(line for line in lines if line)


def html_text(markup: str) -> str:
    """The words a reader sees on a web page: one line for each heading,
    paragraph, list item, or table cell."""
    parser = ReadableText()
    parser.feed(markup)
    parser.close()
    return collapse("".join(parser.parts))


def is_pdf(body: bytes, content_type: str) -> bool:
    return body.lstrip()[:5] == b"%PDF-" or "application/pdf" in content_type


def charset_of(content_type: str) -> str:
    found = re.search(r"charset=\"?([\w.-]+)", content_type, re.I)
    return found.group(1) if found else "utf-8"


def normalize(body: bytes, content_type: str = ""):
    """Return (mode, text or None, sha256, length) for a reply.

    "text" mode hashes the readable text, and "length" counts its
    characters. "bytes" mode hashes the reply as it came, and "length"
    counts its bytes.
    """
    content_type = content_type.lower()
    if is_pdf(body, content_type):
        return "bytes", None, hashlib.sha256(body).hexdigest(), len(body)
    try:
        decoded = body.decode(charset_of(content_type), "replace")
    except LookupError:  # a charset Python does not know
        decoded = body.decode("utf-8", "replace")
    if "html" in content_type or re.search(r"<(!doctype|html|head|body)\b", decoded[:4000], re.I):
        text = html_text(decoded)
    elif content_type.startswith("text/") or not content_type:
        text = collapse(decoded)
    else:
        return "bytes", None, hashlib.sha256(body).hexdigest(), len(body)
    return "text", text, hashlib.sha256(text.encode("utf-8")).hexdigest(), len(text)


# ---------------------------------------------------------------------------
# Fetching, with the link check's manners

def sources(registry_path: Path | None = None):
    registry = json.loads((registry_path or ROOT / "data" / "sources.json").read_text(encoding="utf-8"))
    return registry["sources"]


# A reply that stops partway is never compared: it is not what the source says.
CUT_SHORT = (http.client.IncompleteRead, http.client.RemoteDisconnected, ConnectionResetError)


def fetch(url: str) -> dict:
    """Ask for one address. Returns "state" (fetched, unreachable, or
    checker-blocked) and, when fetched, the content. HEAD first, as the
    link check does; GET brings the content, and only GET decides. If the
    reply is cut short, it waits and asks one more time."""
    host = urlsplit(url).netloc
    methods = ["HEAD", "GET"]
    asked_again = False
    while methods:
        method = methods.pop(0)
        request = urllib.request.Request(url, method=method, headers={"User-Agent": links.USER_AGENT})
        try:
            with links.open_url(request) as response:
                if method == "HEAD":
                    continue
                body = response.read(MAX_BYTES + 1)
                if len(body) > MAX_BYTES:
                    return {"state": UNREACHABLE, "note": f"the reply is larger than {MAX_BYTES} bytes; not compared"}
                mode, text, digest, length = normalize(body, response.headers.get("Content-Type", ""))
                return {"state": FETCHED, "mode": mode, "text": text, "sha256": digest, "length": length,
                        "unverified": host in links.UNVERIFIABLE_HOSTS}
        except urllib.error.HTTPError as error:
            if method == "HEAD":
                continue
            if error.code in (401, 403):
                return {"state": BLOCKED, "note": f"the site answered {error.code} to this tool"}
            return {"state": UNREACHABLE, "note": f"{error.code} {error.reason}"}
        except Exception as error:  # network failure, timeout, TLS
            if links.incomplete_chain(error) and host not in links.UNVERIFIABLE_HOSTS:
                links.UNVERIFIABLE_HOSTS.add(host)
                methods = ["GET"]
                continue
            if method == "HEAD":
                continue
            if isinstance(getattr(error, "reason", error), CUT_SHORT) and not asked_again:
                asked_again = True
                time.sleep(links.PAUSE)
                methods = ["GET"]
                continue
            note = str(getattr(error, "reason", error))
            return {"state": UNREACHABLE, "note": note + ("; asked twice" if asked_again else "")}
    return {"state": UNREACHABLE, "note": "no answer"}


def fetch_all(entries, pause: float | None = None):
    """Fetch each source in order, one at a time. Yields (source, result)."""
    pause = links.PAUSE if pause is None else pause
    last_host_time: dict[str, float] = {}
    for src in entries:
        url = src["url"]
        if src.get("link_check") == "by hand":
            yield src, {"state": BLOCKED, "note": "the registry says this site blocks automated tools; "
                                                  "a person opens it (docs/maintenance.md)"}
            continue
        host = urlsplit(url).netloc
        wait = pause - (time.time() - last_host_time.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        if not links.allowed(url):
            yield src, {"state": BLOCKED, "note": "robots.txt asks automated visitors not to load this address"}
            continue
        result = fetch(url)
        last_host_time[host] = time.time()
        yield src, result


# ---------------------------------------------------------------------------
# The baseline

def load_baseline(path: Path) -> dict:
    """The baseline as {source id: entry}. A missing file is an empty baseline."""
    if not path.exists():
        return {}
    return {entry["id"]: entry for entry in json.loads(path.read_text(encoding="utf-8"))["sources"]}


def baseline_entry(src: dict, result: dict, today: str) -> dict:
    entry = {
        "id": src["id"],
        "url": src["url"],
        "fetched": today,
        "state": result["state"],
        "mode": result.get("mode"),
        "sha256": result.get("sha256"),
        "length": result.get("length"),
        "registry_checked": src.get("checked"),
    }
    if result.get("unverified"):
        entry["certificate"] = "incomplete chain; the connection was not verified"
    if result.get("note"):
        entry["note"] = result["note"]
    return entry


def merge_baseline(old: dict, fresh: dict, order: list) -> tuple[list, list]:
    """Put freshly fetched entries into a baseline. Returns (entries, kept).

    A refresh never throws away a hash it cannot replace: if a source was
    blocked or unreachable this time and the old entry holds a hash for
    the same address, the old entry stays. "kept" lists those ids.
    Sources that left the registry are dropped.
    """
    entries, kept = [], []
    for source_id in order:
        new, was = fresh.get(source_id), old.get(source_id)
        if new is None:
            if was:
                entries.append(was)
            continue
        if new["sha256"] is None and was and was.get("sha256") and was["url"] == new["url"]:
            entries.append(was)
            kept.append(source_id)
        else:
            entries.append(new)
    return entries, kept


def save_baseline(path: Path, entries: list, today: str):
    data = {"notes": BASELINE_NOTES, "written": today, "sources": entries}
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def snapshot_path(folder: Path, source_id: str) -> Path:
    return folder / (re.sub(r"[^A-Za-z0-9._-]", "_", source_id) + ".txt")


def save_snapshot(folder: Path, source_id: str, text: str | None):
    if text is None:
        return
    folder.mkdir(parents=True, exist_ok=True)
    snapshot_path(folder, source_id).write_text(text, encoding="utf-8")


def load_snapshot(folder: Path, source_id: str, digest: str) -> str | None:
    """The saved text for a source, only if it is the text the baseline hashed."""
    path = snapshot_path(folder, source_id)
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    return text if hashlib.sha256(text.encode("utf-8")).hexdigest() == digest else None


# ---------------------------------------------------------------------------
# Comparing

def classify(result: dict, entry: dict | None, url: str) -> str:
    """One state for one source, from this run's fetch and its baseline entry."""
    if result["state"] != FETCHED:
        return result["state"]
    if not entry or not entry.get("sha256") or entry.get("url") != url:
        return NOT_BASELINED
    return UNCHANGED if result["sha256"] == entry["sha256"] else CHANGED


def bounded_diff(old: str, new: str, limit: int = DIFF_LINES, width: int = DIFF_LINE_CHARS) -> str:
    """A unified diff of two normalized texts, cut to a fixed size."""
    lines = list(difflib.unified_diff(old.splitlines(), new.splitlines(), "baseline", "now", lineterm="", n=1))
    shown = [line if len(line) <= width else line[:width] + " [cut]" for line in lines[:limit]]
    if len(lines) > limit:
        shown.append(f"[{len(lines) - limit} more diff lines not shown]")
    # Three backticks in a source would end the report's code block early.
    return "\n".join(shown).replace("```", "'''")


# ---------------------------------------------------------------------------
# Which facts and pages rest on a source

def claim_pages() -> dict:
    """{claim id: the page sources that render it}, worked out the way the
    build does: from the data-claim attributes in each built page's body."""
    import build
    pages, _, _ = build.load_pages()
    usage: dict[str, list] = {}
    for page in pages:
        for attr in build.CLAIM_RE.findall(page["body"]):
            for claim_id in attr.split():
                if page["file"] not in usage.setdefault(claim_id, []):
                    usage[claim_id].append(page["file"])
    return usage


def listing_pages() -> dict:
    """{source id: the pages that list it in their sources line}."""
    import build
    pages, _, _ = build.load_pages()
    listed: dict[str, list] = {}
    for page in pages:
        for source_id in page["sources"]:
            listed.setdefault(source_id, []).append(page["file"])
    return listed


def exposure(source_id: str, claims: list, usage: dict) -> list:
    """The claims that cite a source, each with the pages that render it."""
    return [(claim["id"], sorted(usage.get(claim["id"], [])))
            for claim in claims if source_id in claim.get("sources", [])]


# ---------------------------------------------------------------------------
# The report

def render_report(rows: list, baseline: dict, registry_ids: set, claims: list, usage: dict, listed: dict,
                  snapshots: Path, today: str, partial: bool = False) -> str:
    """rows: (source, result, state) for each source audited."""
    def of(state):
        return [(src, result) for src, result, found in rows if found == state]

    def was(src):
        entry = baseline.get(src["id"])
        if entry and entry.get("sha256") and entry.get("url") == src["url"]:
            return f"It was readable when its baseline was set on {entry['fetched']}."
        return "It has no baseline yet."

    changed, unreachable, blocked = of(CHANGED), of(UNREACHABLE), of(BLOCKED)
    fresh, same = of(NOT_BASELINED), of(UNCHANGED)
    no_hash = [(src, result) for src, result, found in rows
               if found in (UNREACHABLE, BLOCKED) and "no baseline" in was(src)]

    lines = [
        "# Evidence audit report", "",
        f"Run on {today}. Compared {len(rows)} sources with data/evidence_baseline.json."
        + (" Only the sources named with --only were audited." if partial else ""), "",
        "| State | Sources |", "|---|---|",
        f"| Changed | {len(changed)} |", f"| Unchanged | {len(same)} |",
        f"| Unreachable | {len(unreachable)} |", f"| Checker-blocked | {len(blocked)} |",
        f"| Not yet baselined (readable now) | {len(fresh)} |", "",
        "A change is a prompt to re-read the source. It does not say a fact on the site is wrong. "
        "See docs/maintenance.md, \"Evidence audit\".", "",
        f"## Changed ({len(changed)})", "",
    ]
    budget = DIFF_BUDGET
    for src, result in changed:
        entry = baseline[src["id"]]
        lines += [f"### {src['id']}: {src['short']}", "", f"- Address: {src['url']}",
                  f"- Baseline set on {entry['fetched']}, resting on the source check of "
                  f"{entry.get('registry_checked') or 'an unrecorded date'}."]
        if result.get("unverified"):
            lines.append("- The site sends an incomplete certificate chain, so this tool could not verify the connection.")
        cited = exposure(src["id"], claims, usage)
        if cited:
            lines.append("- Facts that cite it, and the pages that show them:")
            lines += [f"  - {claim_id}: {', '.join(pages) or 'no page'}" for claim_id, pages in cited]
        else:
            lines.append("- No fact in data/claims.json cites it.")
        also = sorted(set(listed.get(src["id"], [])) - {page for _, pages in cited for page in pages})
        if also:
            lines.append(f"- Pages that list it as a source without a fact that cites it: {', '.join(also)}")
        old = load_snapshot(snapshots, src["id"], entry["sha256"]) if entry.get("mode") == "text" else None
        if result["mode"] != "text" or entry.get("mode") != "text":
            lines += ["", f"Compared as {entry.get('mode')} then, {result['mode']} now. A file compared by its bytes "
                          "has no text to show. Lower confidence: the same words saved again have new bytes. "
                          f"Size then: {entry.get('length')}. Size now: {result['length']}. Open it and compare."]
        elif old is None:
            lines += ["", "The baseline text is not on hand on this computer, so there is no diff to show. "
                          f"Length then: {entry.get('length')} characters. Length now: {result['length']}."]
        else:
            diff = bounded_diff(old, result["text"])
            if len(diff) > budget:
                lines += ["", "The diff is left out to keep this report short. Run "
                              f"`python3 tools/evidence_audit.py --only {src['id']} --report FILE` to see it."]
            else:
                budget -= len(diff)
                lines += ["", "What changed in the page's text (cut to a limit):", "", "```diff", diff, "```"]
        lines.append("")

    lines += [f"## Unreachable ({len(unreachable)})", "",
              "The connection failed or the server answered with an error. Not compared this time.", ""]
    lines += [f"- {src['id']}: {src['url']} ({result['note']}). {was(src)}" for src, result in unreachable] + [""]
    lines += [f"## Checker-blocked ({len(blocked)})", "",
              "These sites do not let this tool read them. That says nothing about the source: it is not a dead "
              "link and not a removed document. A person opens these by hand.", ""]
    lines += [f"- {src['id']}: {src['url']} ({result['note']}). {was(src)}" for src, result in blocked] + [""]
    lines += [f"## Not yet baselined ({len(fresh) + len(no_hash)})", "",
              "No stored hash to compare with. This is not a change. After a person has read the source, run "
              "`python3 tools/evidence_audit.py --write-baseline --only ID`.", ""]
    for src, result in fresh:
        moved = baseline.get(src["id"], {}).get("url") not in (None, src["url"])
        why = "its address changed since the baseline" if moved else "no stored hash"
        lines.append(f"- {src['id']}: {src['url']} (readable now; {why})")
    lines += [f"- {src['id']}: {src['url']} ({found} now)" for src, result, found in rows if (src, result) in no_hash]
    lines.append("")
    gone = sorted(set(baseline) - registry_ids)
    if gone:
        lines += ["## In the baseline but not in the registry", "",
                  ", ".join(gone) + ". The next deliberate baseline refresh drops them.", ""]
    lines += [f"## Unchanged ({len(same)})", "", ", ".join(src["id"] for src, _ in same) or "None.", ""]
    marked = [src["id"] for src, result in same if result.get("unverified")]
    if marked:
        lines += ["Read over a connection this tool could not verify (incomplete certificate chain): "
                  + ", ".join(marked) + ".", ""]
    return "\n".join(lines)


def results_json(rows: list, today: str) -> dict:
    """The run in a form tools/mechanical_update.py reads."""
    return {
        "audit_date": today,
        "results": [
            {"id": src["id"], "url": src["url"], "state": state, "mode": result.get("mode"),
             "sha256": result.get("sha256"), "length": result.get("length"),
             "unverified": bool(result.get("unverified")), "note": result.get("note")}
            for src, result, state in rows
        ],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--report", type=Path, help="write the Markdown report to this file")
    parser.add_argument("--write-baseline", action="store_true",
                        help="record what each source says now, instead of comparing")
    parser.add_argument("--only", nargs="+", metavar="ID", help="only these source ids")
    parser.add_argument("--results", type=Path, help="also write the run as JSON, for tools/mechanical_update.py")
    parser.add_argument("--baseline", type=Path, default=BASELINE, help="the baseline file (for tests)")
    parser.add_argument("--registry", type=Path, help="a registry file instead of data/sources.json (for tests)")
    parser.add_argument("--snapshots", type=Path, default=SNAPSHOTS,
                        help="folder for the text of each web page, used to show what changed; not committed")
    parser.add_argument("--today", help="YYYY-MM-DD, for testing")
    args = parser.parse_args(argv)
    today = args.today or datetime.date.today().isoformat()

    registry = sources(args.registry)
    entries = registry
    if args.only:
        unknown = sorted(set(args.only) - {src["id"] for src in registry})
        if unknown:
            print(f"Not in the registry: {', '.join(unknown)}", file=sys.stderr)
            return 2
        entries = [src for src in registry if src["id"] in args.only]
    baseline = load_baseline(args.baseline)

    if args.write_baseline:
        fresh, counts = {}, {}
        for src, result in fetch_all(entries):
            fresh[src["id"]] = baseline_entry(src, result, today)
            counts[result["state"]] = counts.get(result["state"], 0) + 1
            if result["state"] == FETCHED:
                save_snapshot(args.snapshots, src["id"], result["text"])
            print(f"{src['id']}: {result['state']}" + (f" ({result['note']})" if result.get("note") else ""), flush=True)
        merged, kept = merge_baseline(baseline, fresh, [src["id"] for src in registry])
        save_baseline(args.baseline, merged, today)
        print(f"\nWrote {args.baseline} ({len(merged)} entries; {len(fresh)} fetched in this run).")
        for state in (FETCHED, BLOCKED, UNREACHABLE):
            print(f"  {state}: {counts.get(state, 0)}")
        modes = [entry["mode"] for entry in fresh.values() if entry["mode"]]
        print(f"  compared as text: {modes.count('text')}; as bytes: {modes.count('bytes')}")
        if kept:
            print("  Kept the earlier hash for sources that could not be read this time: " + ", ".join(kept))
        return 0

    rows = []
    for src, result in fetch_all(entries):
        entry = baseline.get(src["id"])
        state = classify(result, entry, src["url"])
        if state == UNCHANGED and result["mode"] == "text" and \
                load_snapshot(args.snapshots, src["id"], entry["sha256"]) is None:
            # The text matches the baseline's hash, so it is the baseline text. Keep it for a later diff.
            save_snapshot(args.snapshots, src["id"], result["text"])
        rows.append((src, result, state))

    claims = json.loads((ROOT / "data" / "claims.json").read_text(encoding="utf-8"))["claims"]
    report = render_report(rows, baseline, {src["id"] for src in registry}, claims, claim_pages(), listing_pages(),
                           args.snapshots, today, partial=bool(args.only))
    print(report)
    if args.report:
        args.report.write_text(report, encoding="utf-8")
    if args.results:
        args.results.write_text(json.dumps(results_json(rows, today), indent=2) + "\n", encoding="utf-8")
    return 1 if any(state == CHANGED for _, _, state in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
