# Changelog

All notable changes. Dates are when facts were checked or changes were made.

## 0.1.0 beta (2026-11-03)

First public beta of The Stasis Project, a plain-language guide for OHP applicants.

- 17 pages for applicants: home, the 1-minute check, the rules, reasons you may not have to meet them, how to apply, letters, being turned down, past medical bills, health conditions, immigration status, free help and languages, words on letters, a printable hours log, why the site exists, privacy, accessibility, and every source. Plus a 404 page.
- Display settings: text size, spacing, colors (device, warm, white, dark), and "just the key points."
- Source registry (52 entries, 26 read in full or in part, including 22 state documents that explain the changes) and claims ledger (120 claims: 90 facts, 7 inferences, 2 math, 18 design promises, 3 tips), enforced by the build.
- Corrections log with 8 places where official sources disagree or are unclear.
- Hosting on Cloudflare Pages at <https://projectstasis.pages.dev/>, with security headers from `site/_headers`, including a Content Security Policy that stops other sites from framing the pages. See [docs/decisions/0011-cloudflare-pages.md](docs/decisions/0011-cloudflare-pages.md).
- Checks: build freshness, structure and privacy lint (pages and headers), contrast (31 pairs), reading level, dated checkpoints, link check, real-browser tests on a server that behaves like Cloudflare Pages (including every path through the check), and a check after every push and every week that the live site matches this repository.
- GitHub workflows: checks on every push, a live-site check after every push to `main`, and a weekly link, checkpoint, and live-site review that opens an issue.
- Facts checked against sources on Nov. 2, 2026, including the Oct. 29, 2026 federal court order in *Commonwealth of Massachusetts v. Oz*.
- Licenses: CC BY 4.0 for words and data ([LICENSE](LICENSE)) and MIT for code ([LICENSE-CODE](LICENSE-CODE)). The logo is not licensed for reuse. See [docs/decisions/0010-license.md](docs/decisions/0010-license.md).
