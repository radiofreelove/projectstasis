# 0003. Plain HTML, no framework, a standard-library build

- Status: Accepted
- Date: 2026-11-02

## Context

The site must load fast on old phones, work without JavaScript where possible, and be auditable by people who are not web developers.

## Decision

- Plain HTML pages, one CSS file, and three small scripts.
- A single Python build script using only the standard library wraps page text in the shared header and footer, adds source lists, and checks every link and fact.
- The built `site/` folder is committed, so hosting needs no build step, and a check confirms it matches its sources.

## Consequences

- No dependency updates or supply-chain risk in the site itself.
- Fewer conveniences for developers (no components or templates beyond the build script).
- Every page works without JavaScript except the 1-minute check, which shows links to the same information when JavaScript is off.
