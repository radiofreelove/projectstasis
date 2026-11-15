#!/usr/bin/env python3
"""
Draft the "checked" date updates an evidence audit run has proved.

    python3 tools/evidence_audit.py --report evidence-report.md --results evidence-results.json
    python3 tools/mechanical_update.py --audit evidence-results.json

For every source the audit found unchanged, this sets the source's
"checked" date in data/sources.json to the day of the audit. The proof is
the hash match: the source returned the same content as its baseline in
data/evidence_baseline.json. It changes nothing else: no other field, no
other source, no other file. It prints every date it changed.

A date set this way means "a tool found the same content as the last
verified check", not "a person read it again". The weekly workflow uses
this only to open a pull request for a person to review, and only when
the repository variable MECHANICAL_UPDATES is "on" (docs/maintenance.md).

It refuses to write anything, and exits with code 2, if:

  - a source named with --only is not "unchanged" in the audit (changed,
    checker-blocked, unreachable, not yet baselined, or missing);
  - a source the audit calls unchanged does not match the baseline: a
    different hash, a different address, or no stored hash;
  - a source the audit calls unchanged is not in the registry, or its
    address there is different;
  - the audit lists a source twice, names a state this tool does not
    know, or is more than MAX_AGE_DAYS days old or dated in the future.

Two kinds of unchanged source are left alone and listed:

  - one read over a connection the audit could not verify (a site that
    sends an incomplete certificate chain);
  - one whose "checked" date is already the audit's date or later. A
    date never moves backward.

Standard library only.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "data" / "sources.json"
BASELINE = ROOT / "data" / "evidence_baseline.json"

UNCHANGED = "unchanged"
STATES = {UNCHANGED, "changed", "unreachable", "checker-blocked", "not yet baselined"}
# An audit older than this proves nothing about today.
MAX_AGE_DAYS = 2
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


class Refused(Exception):
    """The audit does not prove what this tool would write."""


def plan(audit: dict, registry: dict, baseline: dict, today: str, only=None):
    """Work out the updates. Returns (updates, left_alone).

    updates: [(source id, old date, new date)]. left_alone: [(id, why)].
    Raises Refused, with every reason, if the audit cannot be trusted for
    any source this run would touch.
    """
    problems = []
    audit_date = audit.get("audit_date", "")
    if not DATE_RE.fullmatch(audit_date):
        raise Refused("the audit has no 'audit_date' like 2026-11-16")
    age = (datetime.date.fromisoformat(today) - datetime.date.fromisoformat(audit_date)).days
    if age < 0:
        problems.append(f"the audit is dated {audit_date}, after today ({today})")
    elif age > MAX_AGE_DAYS:
        problems.append(f"the audit is from {audit_date}, more than {MAX_AGE_DAYS} days ago; run it again")

    results: dict[str, dict] = {}
    for result in audit.get("results", []):
        source_id = result.get("id")
        if source_id in results:
            problems.append(f"{source_id}: listed twice in the audit")
        if result.get("state") not in STATES:
            problems.append(f"{source_id}: unknown state {result.get('state')!r}")
        results[source_id] = result

    by_id = {src["id"]: src for src in registry["sources"]}
    base = {entry["id"]: entry for entry in baseline.get("sources", [])}
    if only:
        wanted = list(dict.fromkeys(only))
        for source_id in wanted:
            state = results.get(source_id, {}).get("state", "not in the audit")
            if state != UNCHANGED:
                problems.append(f"{source_id}: the audit says {state}, so its date cannot be updated")
    else:
        wanted = [source_id for source_id, result in results.items() if result.get("state") == UNCHANGED]

    updates, left_alone = [], []
    for source_id in wanted:
        result = results.get(source_id)
        if not result or result.get("state") != UNCHANGED:
            continue  # already reported above
        src, entry = by_id.get(source_id), base.get(source_id)
        if src is None:
            problems.append(f"{source_id}: unchanged in the audit, but not in the registry")
            continue
        if not entry or not entry.get("sha256"):
            problems.append(f"{source_id}: unchanged in the audit, but the baseline holds no hash for it")
            continue
        if result.get("sha256") != entry["sha256"]:
            problems.append(f"{source_id}: the audit's hash is not the baseline's hash")
            continue
        if not (result.get("url") == entry.get("url") == src["url"]):
            problems.append(f"{source_id}: the audit, the baseline, and the registry do not name one address")
            continue
        if result.get("unverified"):
            left_alone.append((source_id, "read over a connection the audit could not verify"))
        elif src["checked"] >= audit_date:
            left_alone.append((source_id, f"already checked on {src['checked']}"))
        else:
            updates.append((source_id, src["checked"], audit_date))

    if problems:
        raise Refused("\n  - ".join(problems))
    return updates, left_alone


def apply(text: str, updates) -> str:
    """Change only the "checked" lines of the named sources in the registry's
    text, so the file's layout and every other character stay as they were.
    Confirms the result by reading both versions back and comparing them."""
    new_text = text
    for source_id, old, new in updates:
        # From this source's "id" to the first "checked" after it, with no
        # other source's "id" in between.
        pattern = re.compile(
            r'("id":\s*' + re.escape(json.dumps(source_id)) + r'(?:(?!"id":).)*?"checked":\s*")'
            + re.escape(old) + '"', re.S)
        new_text, count = pattern.subn(lambda match: match.group(1) + new + '"', new_text, count=1)
        if count != 1:
            raise Refused(f"{source_id}: could not find its 'checked' date in the registry file")

    expected = json.loads(text)
    dates = {source_id: new for source_id, _, new in updates}
    for src in expected["sources"]:
        if src["id"] in dates:
            src["checked"] = dates[src["id"]]
    old_lines, new_lines = text.splitlines(), new_text.splitlines()
    changed_lines = sum(1 for a, b in zip(old_lines, new_lines) if a != b)
    if json.loads(new_text) != expected or len(old_lines) != len(new_lines) or changed_lines != len(updates):
        raise Refused("the edit would change more than the 'checked' dates; nothing was written")
    return new_text


def summary(updates, left_alone, audit_date: str) -> str:
    lines = [f"Evidence audit of {audit_date}: {len(updates)} checked dates updated.", ""]
    lines += [f"- {source_id}: {old} to {new}" for source_id, old, new in updates]
    if left_alone:
        lines += ["", f"Unchanged in the audit and left alone ({len(left_alone)}):", ""]
        lines += [f"- {source_id}: {why}" for source_id, why in left_alone]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--audit", type=Path, required=True,
                        help="the JSON file tools/evidence_audit.py wrote with --results")
    parser.add_argument("--only", nargs="+", metavar="ID", help="only these source ids")
    parser.add_argument("--registry", type=Path, default=REGISTRY, help="the registry file to update (for tests)")
    parser.add_argument("--baseline", type=Path, default=BASELINE, help="the baseline file (for tests)")
    parser.add_argument("--summary", type=Path, help="also write the summary to this file")
    parser.add_argument("--today", help="YYYY-MM-DD, for testing")
    args = parser.parse_args(argv)
    today = args.today or datetime.date.today().isoformat()

    try:
        audit = json.loads(args.audit.read_text(encoding="utf-8"))
        text = args.registry.read_text(encoding="utf-8")
        baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
        updates, left_alone = plan(audit, json.loads(text), baseline, today, args.only)
        new_text = apply(text, updates)
    except Refused as refusal:
        print(f"Refused. Nothing was written.\n  - {refusal}", file=sys.stderr)
        return 2
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        print(f"Refused. Nothing was written.\n  - could not read the audit, registry, or baseline: {error!r}",
              file=sys.stderr)
        return 2

    if updates:
        args.registry.write_text(new_text, encoding="utf-8")
    report = summary(updates, left_alone, audit["audit_date"])
    print(report, end="")
    if args.summary:
        args.summary.write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
