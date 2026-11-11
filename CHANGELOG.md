# Changelog

All notable changes. Dates are when facts were checked or changes were made.

## 0.2.0 beta (2026-11-10)

A second guide, for Utah Medicaid, and a re-check of the Oregon court note. Built on the `utah-section` branch.

### New: the Utah Medicaid guide

- 17 pages for people applying for Utah Medicaid, starting at `/utah`, the same set the OHP guide has: home, a 1-minute check, the rules, reasons you may not have to meet them (Utah's exclusions and exceptions, and proof of tribal status), how to apply, letters, being turned down, past medical bills, health conditions, immigration status, free help and languages, words on letters, a printable hours log, why the guide exists, privacy, accessibility, and every source. Same page pattern, word rules, and design as the OHP guide.
- 116 Utah claims in the fact log (IDs start with `U-`: 105 facts, 4 inferences, 2 math, 4 design promises, and 1 tip) and 40 Utah entries in the source registry (IDs start with `U`; 33 were read, and 18 are Utah documents that explain the changes).
- 11 places where Utah's own pages disagree or are unclear, in a new Utah part of [docs/corrections.md](docs/corrections.md): the months a current member must meet, whose income counts toward $580, foster care wording, jail and treatment, two general phone numbers, a child's age, income numbers, fax numbers, where the paper form asks about the rules, whether Targeted Adult Medicaid ends, and document dates.
- A Utah 1-minute check at `/utah-check`, built from the lists on Utah's own pages. It has the same 3 steps, the same promises, and the same tests as the Oregon check. Every question and result is in [docs/checker-logic.md](docs/checker-logic.md).
- **The Utah guide is whole.** Every link on a Utah page leads to a Utah page or an official source. The banner, footer, and source lists on Utah pages lead to Utah's own About, Privacy, Accessibility, and Every source pages. The Utah "Every source" page lists Utah's sources and the federal, court, and site sources the Utah guide uses, and no Oregon sources. The build enforces all of this. The one way across is the link to the other guide's home page.
- The Utah About page and the Utah "Every source" page say plainly that the Utah documents were read with a research tool and that a person has not yet read each one.
- Every design choice: [docs/decisions/0013-utah-section.md](docs/decisions/0013-utah-section.md).
- A second pass the same day fetched 19 of the Utah sources again and compared them with the fact log. Everything compared matched. Two changes came out of it: the turned-down page now says the 15 days to keep medical benefits run from the date on the notice, and the corrections log notes that Utah's glossary names a different hearing office than its hearings page. Details and what was not fetched again: [docs/research-log.md](docs/research-log.md).
- **Read this before sharing the Utah guide.** It was researched in one day through a tool that answers questions about a document instead of returning its full text. No person has read the Utah documents end to end. Checkpoint 2026-11-24 covers that, and [docs/research-log.md](docs/research-log.md) lists what could not be checked.

### Oregon

- Checkpoint 2026-11-16 done early, on Nov. 10. OHA's federal changes page (S07, still last updated Sept. 18, 2026), provider FAQ (S01), and exemptions explainer (S03) had not changed and did not mention the Oct. 29, 2026 court ruling. The "In the news" note on the reasons and health pages now says "As of Nov. 10, 2026." OHP.Oregon.gov/HR1 (S24) still has to be read by hand.
- The court entered judgment and dismissed *Commonwealth of Massachusetts v. Oz* on Oct. 29, 2026. No notice of appeal appeared in the docket entries through Nov. 6. The docket is now in the registry as S40. Next checkpoint: 2026-12-10.
- The home page, the About page, and the 404 page link to the Utah guide. The About page has a "Two guides" section.

### Both guides

- Every page's source list now shows the date each source was last checked, next to the date printed on it. Before, one line gave a single date for all of them, which stopped being true as soon as one source was re-read.
- Each home page links to the other guide right under its first lines, and the link stays visible in "Just the key points" mode.
- The footer's "All pages" list shows every page of the guide you are in, then one link to the other guide.
- The "page not found" page belongs to neither guide. It shows both guides, with a menu and footer that name both states.
- The Oregon About page no longer speaks for Utah. Its "not run by" and "only OHP decides" lines are back to their 0.1.3 wording.

### Build and upkeep

- `tools/build.py`: guide sections (`section: utah` in page metadata), a copy of each `shared: yes` page for each guide with `<!-- utah -->` and `<!-- oregon -->` blocks for the parts that differ, a rule that stops the build if a page links to, cites, or borrows facts from the other guide, one "facts last checked" date per guide, a count check for Utah's documents like the one for Oregon's, a format check on every source's `checked` date, and dates written in the site's style from one value instead of two constants that could drift apart.
- `data/review.json`: Utah checkpoints for 2026-11-24 (a person reads the Utah pages against their sources), 2027-03-01 (renewals), and 2027-06-15 (Targeted Adult Medicaid), and Utah work added to the Dec. 10, Dec. 13, Dec. 31, and Jan. 15 checkpoints.
- Docs updated to match: README, methodology, style guide, boundaries, design, maintenance, roadmap, research log, and decision 0012 (a recorded difference from Strand).
- The check's script is now one engine (`checker.js`) and one file of words for each state (`checker-oregon.js`, `checker-utah.js`). The Oregon words did not change. The browser tests run every path through both checks, pick every choice once to confirm each has words, and fail if a result names the other state or links to the other guide.
- Checked on Nov. 10, 2026: build freshness, structure lint (35 pages), contrast, reading level (Utah pages grade 2.4 to 7.1), dated checkpoints, and the real-browser tests on all 35 pages. Not run: axe-core, the link check, and the live-site check, which need the GitHub workflows.

## 0.1.3 beta (2026-11-03)

Third review follow-up. Nothing readers see changes.

- Merged Dependabot's first six proposals (#1 to #6), each of which had passed every check: actions/checkout, setup-python, setup-node, and upload-artifact to v7; axe-core 4.14.0; Playwright 1.64.1. Strand moved to the same test tool versions the same day.

- New `.github/dependabot.yml`: monthly update proposals for the GitHub Actions and the test-only tools, the same setup as Strand. Expect update proposals for the Actions, which are several major versions behind Strand's.
- The browser test tools are now pinned to Strand's versions in `test-tools/requirements.txt` (Playwright 1.63.0) and `test-tools/package.json` (axe-core 4.10.2). Before this, the workflow installed any Playwright 1.x and any axe-core 4.x. The site build still uses only the Python standard library.
- `docs/testing.md` no longer carries a dated results summary that went stale with each release. It now lists each check, its tool, and when it runs; results live in the Actions logs, the generated reports, and this changelog.

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
