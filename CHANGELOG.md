# Changelog

All notable changes. Dates are when facts were checked or changes were made.

## 0.1.2 beta (2026-11-03)

Second review follow-up.

- Security headers now match The Strand Project exactly: four more blocked browser features (accelerometer, browsing-topics, gyroscope, magnetometer) and `Strict-Transport-Security`. The Content Security Policy is unchanged.
- New [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), adapted from Strand's. Linked from the README and CONTRIBUTING.
- Decision 0012 now records the shared headers, the tool-page source lists, the code of conduct, and the different doc naming as intentional.

## 0.1.1 beta (2026-11-03)

Follow-up to an outside review that compared this project with The Strand Project. Shared conventions are now recorded in [docs/decisions/0012-shared-with-strand.md](docs/decisions/0012-shared-with-strand.md).

- Jan. 1, 2027: the medical bills box on the home page now stays after the change. Only the "Read this before Jan. 1, 2027" line and the "Through Dec. 31, 2026" sentence hide after Dec. 31; the 1-month rule is now a full sentence that reads true on either side of the date. The "Through Dec. 31, 2026" line on the bills page also hides after Dec. 31, and that page's opening line no longer says the window "is getting shorter."
- Dated checkpoints: new Dec. 13, 2026 dry run before the switch. The Dec. 31 checkpoint now covers deleting the expired notes for readers without JavaScript and rewording the home page title and headline. The weekly review workflow also runs on Jan. 1 each year, so notes that expire on Dec. 31 are flagged that day instead of the next Monday.
- Display settings: new optional font, Atkinson Hyperlegible Next, the same files and setting as The Strand Project. It is served from this site, pinned by SHA-256 in `fonts.lock.json`, checked by the build, and downloaded only by readers who choose it. The Content Security Policy adds `font-src 'self'`. The default font order now matches Strand (system font first).
- "Report a mistake" is now in the banner on every page. It opens a new About section that says reports and GitHub account names are public.
- Every page footer now names the licenses, and the About page has a "Reuse this guide" section (roadmap item 4).

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
