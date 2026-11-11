#!/usr/bin/env python3
"""
Say what the next GitHub release should be called and what it should say.

    python3 tools/release_notes.py                  Print the tag, title, and notes.
    python3 tools/release_notes.py --field tag      Print one of: tag, title,
                                                    prerelease, body.
    python3 tools/release_notes.py --check          Fail if CHANGELOG.md has no
                                                    entry for the version in
                                                    tools/build.py.

The version comes from VERSION in tools/build.py ("0.2.1 beta"), the same
value every page shows in its footer. The tag is that version with a "v"
in front and a hyphen for the space ("v0.2.1-beta"). The notes are that
version's entry in CHANGELOG.md, so a release never says anything the
changelog does not. The only change is to links: a link to a file in this
repository, such as (docs/roadmap.md), would not work on a release page,
so it is pointed at that file as it stood at the tag.

.github/workflows/release.yml runs this after the checks pass on main and
publishes the release if the tag does not exist yet. Before this tool, a
person had to remember to do it. See docs/maintenance.md.

Standard library only.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import build

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = ROOT / "CHANGELOG.md"
PRERELEASE_WORDS = ("alpha", "beta", "rc")


class ReleaseError(Exception):
    pass


def tag_for(version: str) -> str:
    if not re.fullmatch(r"\d+\.\d+\.\d+( [a-z0-9]+)?", version):
        raise ReleaseError(f"VERSION {version!r} is not like '0.2.1 beta' or '1.0.0'")
    return "v" + version.replace(" ", "-")


def is_prerelease(version: str) -> bool:
    return any(word in version for word in PRERELEASE_WORDS)


def changelog_entry(version: str, changelog: str) -> str:
    """The text under this version's heading, up to the next version's heading."""
    lines = changelog.splitlines()
    start = None
    for number, line in enumerate(lines):
        if re.fullmatch(rf"## {re.escape(version)}( \(\d{{4}}-\d{{2}}-\d{{2}}\))?", line.strip()):
            start = number + 1
            break
    if start is None:
        raise ReleaseError(f"CHANGELOG.md has no entry headed '## {version} (date)'")
    end = next((n for n in range(start, len(lines)) if lines[n].startswith("## ")), len(lines))
    entry = "\n".join(lines[start:end]).strip()
    if not entry:
        raise ReleaseError(f"CHANGELOG.md's entry for {version} is empty")
    return entry + "\n"


def absolute_links(entry: str, tag: str) -> str:
    """Point links to files in this repository at those files as of the tag."""
    return re.sub(
        r"\]\((?!https?://|mailto:|#)([^)\s]+)\)",
        lambda match: f"]({build.PROJECT_REPO}/blob/{tag}/{match.group(1)})",
        entry,
    )


def release(version: str | None = None, changelog: str | None = None) -> dict:
    version = version or build.VERSION
    changelog = CHANGELOG.read_text(encoding="utf-8") if changelog is None else changelog
    tag = tag_for(version)
    return {
        "tag": tag,
        "title": version,
        "prerelease": "true" if is_prerelease(version) else "false",
        "body": absolute_links(changelog_entry(version, changelog), tag),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--field", choices=("tag", "title", "prerelease", "body"))
    parser.add_argument("--check", action="store_true", help="fail if the changelog has no entry for this version")
    args = parser.parse_args()
    try:
        info = release()
    except ReleaseError as error:
        print(error, file=sys.stderr)
        return 1
    if args.check:
        print(f"CHANGELOG.md has an entry for {info['title']} (tag {info['tag']}).")
    elif args.field:
        print(info[args.field], end="" if args.field == "body" else "\n")
    else:
        print(f"Tag: {info['tag']}\nTitle: {info['title']}\nPre-release: {info['prerelease']}\n\n{info['body']}", end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
