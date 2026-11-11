#!/usr/bin/env python3
"""
Fail when a dated checkpoint has passed, so a person re-checks the sources.

    python3 tools/check_review_dates.py           Fail if any checkpoint is past
    python3 tools/check_review_dates.py --today 2027-01-02   Test a date

Checks two things:
  1. data/review.json checkpoints (review_by dates).
  2. data-show-until dates in src/pages. The browser hides those notes on
     its own after the date, but the text should be retired by a person.

Every claim named in a checkpoint must exist in data/claims.json.
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--today", help="YYYY-MM-DD, for testing")
    args = parser.parse_args()
    today = args.today or datetime.date.today().isoformat()

    review = json.loads((ROOT / "data" / "review.json").read_text(encoding="utf-8"))
    claims = {c["id"] for c in json.loads((ROOT / "data" / "claims.json").read_text(encoding="utf-8"))["claims"]}

    problems, upcoming = [], []
    for point in review["checkpoints"]:
        for cid in point["claims"]:
            if cid not in claims:
                problems.append(f"checkpoint {point['review_by']} names unknown claim {cid}")
        if today > point["review_by"]:
            problems.append(f"Past due since {point['review_by']}: {point['what']}")
        else:
            upcoming.append(f"{point['review_by']}: {point['what']}")

    for path in sorted((ROOT / "src" / "pages").rglob("*.html")):
        for until in re.findall(r'data-show-until="(\d{4}-\d{2}-\d{2})"', path.read_text(encoding="utf-8")):
            if today > until:
                problems.append(f"{path.parent.name}/{path.name}: a note expired on {until}; retire or update it")

    if upcoming:
        print("Upcoming checkpoints:\n  " + "\n  ".join(upcoming))
    if problems:
        print("\nNeeds a person:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1
    print("\nNo checkpoints are past due.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
