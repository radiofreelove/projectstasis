# Changelog

All notable changes. Dates are when facts were checked or changes were made.

## 0.3.4 beta (2026-11-14)

Extra detail is now marked on 21 more pages, so "Show just the key points" hides something on them. Marking only: no wording, fact, link, or source list changed, and the strip itself did not change. Before this, the browser report listed 26 pages where the strip hid nothing. It now lists 5.

- **Oregon:** the home page, Past medical bills, Free help, OHP sent me a letter, Why this site exists, and Every source.
- **Utah:** the home page, Past medical bills, Turned down, Free help, Immigration status, Utah sent me a letter, Words on your letters, Why this guide exists, and Every source.
- **Washington:** Past medical bills, Turned down, Free help, Words on your letters, Why this guide exists, and Every source. The 0.3.0 beta entry below says the Washington pages are marked; these 6 had no marks.
- **What was marked:** names the state uses for things, where a fact comes from, notes that state pages differ, office hours, pointers to an agency page for more, and, on the About and Every source pages, how the guide is made and how to reuse it. Steps, deadlines, phone numbers, warnings, and the links a reader needs to act stay in key-points mode.
- **Still hiding nothing, on purpose:** the "page not found" page, Oregon's Immigration status page, Oregon's Words on your letters page, and the Oregon and Utah hours logs. Each line on those pages is a step, a warning, a meaning, or part of the form.
- Details marked as extra across all pages went from 43 to 88. The count is in [docs/testing-browser.md](docs/testing-browser.md).

## 0.3.3 beta (2026-11-13)

Source reads on Nov. 13, 2026. The reads were done by the AI assistant; the source review by a person is still checkpointed for Nov. 26, 2026 (Washington) and Nov. 24, 2026 (Utah).

- Read in full on Nov. 13, 2026, and marked so in the source registry with that checked date: Washington WA12, WA13, WA14, WA15, WA16, WA17, WA18, WA19, WA20, WA21, WA22, WA23, and WA24. WA05 was also read at HCA's own address that day. Utah: U15S, U19S, U34, U35, and U36.
- Still marked as not read in full: WA25, U32, and U38. Each registry note says what was read on Nov. 13, 2026 and what was not: WA25's own address refused the request and the filed complaint was read from the copy the Washington Attorney General links; U32 is a sign-in site that answered 404; U38 is a 514-page code list of which the title page, definitions, section headings, first two pages, and last page were read.
- Drafting claims settled: 14 of the 17 Washington drafting claims. 13 were confirmed as written by the read of every source they rest on: WA-RULE-09, WA-APP-08, WA-APP-09, WA-LTR-02, WA-DEN-03, WA-DEN-04, WA-DEN-05, WA-HLT-04, WA-IMM-02, WA-IMM-03, WA-WRD-02, WA-WRD-05, and WA-LOG-03. One was corrected: WA-DEN-01.
- The correction readers see: the Washington turned-down page now says a person has 90 days from the day coverage ended to send a completed renewal, and that the rule saying coverage comes back with no gap runs only until Jan. 1, 2027. The version of WAC 182-504-0035 that takes effect Jan. 1, 2027 keeps the 90 days and says no new application is needed, and no longer says "with no gap."
- The Washington health page note now says the state's paper on how Washington checks a health condition (WA21) was read on Nov. 13, 2026, and that a person on this project has not yet checked it; the detail itself is not added.
- Still drafting claims, waiting for the owner's ruling: WA-CHK-01, WA-IMM-04, and WA-RSN-15. Their notes in the fact log say why each read did not confirm the claim as written.
- The 12 open Washington points in docs/corrections.md are unchanged in disposition. The remaining unread sources are unchanged apart from the registry notes above.
## 0.3.2 beta (2026-11-13)

Four Washington source addresses that had gone dead were replaced with the addresses the agencies now publish, each verified on Nov. 13, 2026 against the facts it supports: WA11 (HCA, Filing an application) and WA23 (HCA, Apple Health Expansion) moved in HCA's site restructure, and WA16 (WAC 182-504-0035) and WA17 (WAC 182-504-0130) now point to the legislature's current WAC address, the same form the registry already uses for WAC 182-505-0250. The WA11 registry note no longer says the page states the Apple Health for Adults test, because the moved page does not state it; the facts WA11 supports are unchanged. This fix carries its own version because v0.3.1-beta was tagged from the tidy merge before the fix merged; the 0.3.1 beta entry below originally described the fix as part of that version, and this entry corrects that.

## 0.3.1 beta (2026-11-13)

Repository tidy. Nothing readers see changes except the two README paragraphs below.

- Wording standard applied across the repository: no guide is described as more or less checked than another, and nothing claims or implies that sources were read end to end. The standard wording is that every source was accessed and reviewed against the facts it supports, the registry shows which were read in full and when each was checked, and the scheduled reviews are named as source reviews with their dates (Utah, Nov. 24, 2026; Washington, Nov. 26, 2026). The places changed: the README's Utah and Washington paragraphs, decisions 0013 and 0015, docs/adding-a-guide.md, docs/research-log.md, data/review.json, the rules header and drafting claim notes in data/claims.json, and the header and stale pre-merge notes in data/sources.json. Two sentences in the 0.2.0 beta entry below and one line in docs/research-log.md were rewritten in place under the same standard, and this entry records that they were.
- Decision 0015 now records that the Washington guide merged on Nov. 12, 2026 on the owner's direction, ahead of its source review.

## 0.3.0 beta (2026-11-12)

Two changes: a third guide, for Apple Health in Washington, and the "How much to show" setting moved to where readers can see it. Merged on Nov. 12, 2026, ahead of the Washington source review ([docs/adding-a-guide.md](docs/adding-a-guide.md), "Before you write a page", step 2), on the project owner's direction. That review is now the Nov. 26, 2026 checkpoint in [data/review.json](data/review.json), and the Washington pages and the README carry the same new-guide warning the Utah guide carried at its merge.

### New: the Apple Health guide for Washington

- 17 pages for people applying for Apple Health, starting at `/washington`, the same set the other guides have: home, a 1-minute check, the rules, reasons you may not have to meet them, how to apply, letters, being turned down, past medical bills, health conditions, immigration status, free help and languages, words on letters, a printable hours log, why the guide exists, privacy, accessibility, and every source.
- Built from a research dossier dated Nov. 12, 2026, and from nothing else. 25 Washington entries in the source registry (IDs start with `WA`) and 76 Washington claims in the fact log (IDs start with `WA-`). 14 of the 25 sources are marked as not read in full, and the 17 claims that rest on any of them are marked "Drafting claim" in the fact log. [docs/research-log.md](docs/research-log.md) lists them and the reading list. One claim in the dossier, on how Washington checks medical frailty, is marked "pending, do not publish" and is in neither the fact log nor any page.
- The guide calls the state "Washington". It names the Health Care Authority (HCA), Washington Healthplanfinder, DSHS, MEDS, the Office of Administrative Hearings, and the WAC sections the dossier gives. Nothing was carried over from Oregon or Utah.
- A Washington 1-minute check at `/washington-check`, with the same 3 steps and the same promises. Step 3 lists the 5 ways to meet the rule on HCA's June 2026 fact sheet, as that sheet lists them. The sheet has no way for hours at a paid job by themselves, so the check has none, and the page says so. Every question and result: [docs/checker-logic.md](docs/checker-logic.md).
- 12 open points, none resolved, in a new Washington part of [docs/corrections.md](docs/corrections.md): the 19 to 64 or 19 to 65 age band; paid work as a way of its own; "exemptions" or "exclusions"; three wordings of a child's age; differing counts; how the start date is framed; whether Washington will delay the rules (the guide says nothing); what the $580 counts; SNAP and TANF wording; how far the court order reaches; good cause (the guide says nothing); and two sources that could not be read at their own addresses.
- **Oregon stays the front door.** `/` is still the Oregon home page, and the state switch on every home page reads Oregon, Washington, Utah. Decision: [0015](docs/decisions/0015-front-door-with-three-guides.md). The words that frame the "page not found" page now name all three states.
- The Washington guide does not say the state explains the rules across "more than a dozen" documents, because the registry holds 9 such documents for it. The build now checks that count for a guide that makes the claim (Oregon and Utah still do) and not for one that does not.
- The other guides change only where they list the guides: the state switch, the footers, the "page not found" page, and the "Three guides" part of each About page.
- Washington checkpoints in [data/review.json](data/review.json) (the end-to-end read, checkpointed for Nov. 26, 2026, a 30-day re-check, and Washington's part of the Jan. 1, 2027 checkpoints), and Washington hand-checks in [docs/maintenance.md](docs/maintenance.md).

### "How much to show," where readers can see it

- Every page now starts with a slim strip above the heading: "Still too much to take in?", a "Show just the key points" button, and one line saying what it does. Before, the setting was the fifth group inside Display settings, and nothing on the page said it existed.
- In key-points mode the strip is the banner: "You are seeing just the key points. Some details are hidden." with a "Show everything" button. The old banner sent readers back into the menu.
- It is the same setting, saved in the same place (`stasis-display-v1`). The strip and Display settings always agree, and nothing new is stored. The status line now says what happened ("Just the key points. Extra details on this page are now hidden.").
- One real button: Tab reaches it, Enter or Space works it, and focus stays on it. Without JavaScript the strip does not show and the full page does.
- A link that points into hidden detail turns "Everything" back on first, then goes there.
- Printing always shows everything. Before, a page printed in key-points mode printed short. The strip does not print.
- Presentation only: no claim, source list, or legal wording changed on any page.
- New checks: `tools/check_structure.py` fails if any page lacks the strip or its exact words, and `tools/browser_check.py` turns the mode on and off by keyboard on every page, in print, from Display settings, through a link into hidden detail, and without JavaScript.
- Extra detail is still marked by hand. The Washington pages are marked. The Oregon and Utah pages keep the marks they had, so on some of them, including both home pages, the strip hides nothing yet; the browser report lists those pages.

### Tools

- The test with a made-up extra guide now adds a fourth state, since Washington is real, and two new tests cover the "more than a dozen" rule.

## 0.2.1 beta (2026-11-11)

Groundwork for a third guide, and upkeep. Readers see 2 changes: the version number in each footer, and a longer note about myCase on the Utah "Every source" page, live since Nov. 11, 2026. The rework itself changes nothing they see: before the version number changed, the rebuilt site matched the published one byte for byte. Decision: [0014](docs/decisions/0014-guide-list.md). Steps for the next state: [docs/adding-a-guide.md](docs/adding-a-guide.md).

### One list of guides

- Every source in `data/sources.json` and every fact in `data/claims.json` now has a `guide` field: `oregon`, `utah`, or `all` (federal rules, court papers, standards, national groups, the host, and what the site promises about itself). The build goes by that field. Before, it treated an ID that started with `U` as Utah's and everything else as Oregon's, which could not hold a third state. 43 sources are Oregon's, 40 are Utah's, and 10 are shared; 102 facts are Oregon's, 116 are Utah's, and 18 are shared. Two Oregon groups that were open to both guides by accident (S25 and S38) are now Oregon's only. New rule: a fact may rely only on its own guide's sources or on shared ones.
- Utah's source kinds are now the same as Oregon's (`state-explainer`, `state-page`, `state-form`), since the `guide` field says whose they are.
- The state switch on each home page and the state lists on the "page not found" page are built from the guide list in `tools/build.py`. They were written by hand in three files. Each guide keeps its own part of the "page not found" page in `src/pages/<guide>/_not-found.html`. The build stops if a guide's home page lacks the switch.
- The build no longer names a state anywhere but that list. Gone: the Utah-only settings (`{{UTAH_DOC_COUNT}}` and `{{STATE_DOC_COUNT}}` are now `{{DOC_COUNT}}`, each guide's own count), the rule that each guide links to exactly one other guide (footers now list every other guide), and the pattern that knew only `oregon` and `utah` blocks.
- The browser tests read the same list. For each guide they run its check and fail if a result uses another guide's own words or links into another guide. Before, they named the Oregon and Utah pair in the code.
- Page sources are grouped by state: `src/pages/oregon/`, `src/pages/utah/`, and `src/pages/shared/`. The folder decides the guide, so Utah pages no longer say `section: utah`. No public address changed.

### Upkeep

- New tests for the tools (`tools/tests/`, 32 tests, Python standard library): the rules that keep each guide whole, a made-up third guide that must build with a three-state switch, footers, and "page not found" page, the link checker against local servers that copy each failure it has met, and the release notes. They run on every push.
- New release step ([release.yml](.github/workflows/release.yml), `tools/release_notes.py`): after the checks pass on `main`, GitHub tags the commit and publishes a release if the version has no tag yet. The notes are this file's entry for the version, with its links pointed at the tagged files. The checks now fail if a version has no entry here. Before, a person had to remember; 0.2.0 beta was published by hand.
- `tools/check_links.py` no longer calls a link broken when the tool is the problem (issue #7: 23 Oregon links reported broken on Nov. 9, 2026; on Nov. 11 the 5 that could be opened all loaded, and OHA's how-to-apply page still listed all 17 paper application links). A GET request now decides when HEAD fails. A site that sends an incomplete certificate chain is asked again without verification, only to learn whether the address answers: if it does, it goes under "Check by hand"; if not, it is broken. Any other certificate problem still counts as broken. Registry entries marked `"link_check": "by hand"` (S23, S24, and U32, which block or mislead automated tools) are listed for a person and not requested. Tested against local servers that copy each case, then run for real on Nov. 11, 2026 against all 110 addresses, Utah's included for the first time: 73 worked, 35 were listed for a person (all 20 addresses on Oregon's forms site answered), and 2 were reported broken. One was myCase (U32), a login site that answered 404 to the tool while Utah's apply page still linked to it; it is now checked by hand. The other, OHA's appeals page (S14), answered 401 to the tool on both runs but loaded when opened; it is still open in issue #9.
- `SECURITY.md` listed action versions from before the Dependabot updates of Nov. 3, 2026. It now lists the versions the workflows use.
- Not done here, because repository settings cannot be changed from the session that did this work: turning on "Automatically delete head branches," deleting the two merged branches (`utah-section` and Dependabot's `upload-artifact-7`), and updating the repository's description and topics, which still describe an Oregon-only guide.
- Checked on Nov. 11, 2026: build freshness, the 32 tool tests, structure lint (35 pages), contrast, reading level, dated checkpoints, and the real-browser tests on all 35 pages.

## 0.2.0 beta (2026-11-11)

A second guide, for Utah Medicaid, and a re-check of the Oregon court note. Built and fact-checked on Nov. 10, 2026. Merged and published on Nov. 11, 2026, when decision 0013 became Accepted.

### New: the Utah Medicaid guide

- 17 pages for people applying for Utah Medicaid, starting at `/utah`, the same set the OHP guide has: home, a 1-minute check, the rules, reasons you may not have to meet them (Utah's exclusions and exceptions, and proof of tribal status), how to apply, letters, being turned down, past medical bills, health conditions, immigration status, free help and languages, words on letters, a printable hours log, why the guide exists, privacy, accessibility, and every source. Same page pattern, word rules, and design as the OHP guide.
- 116 Utah claims in the fact log (IDs start with `U-`: 105 facts, 4 inferences, 2 math, 4 design promises, and 1 tip) and 40 Utah entries in the source registry (IDs start with `U`; 33 were read, and 18 are Utah documents that explain the changes).
- 11 places where Utah's own pages disagree or are unclear, in a new Utah part of [docs/corrections.md](docs/corrections.md): the months a current member must meet, whose income counts toward $580, foster care wording, jail and treatment, two general phone numbers, a child's age, income numbers, fax numbers, where the paper form asks about the rules, whether Targeted Adult Medicaid ends, and document dates.
- A Utah 1-minute check at `/utah-check`, built from the lists on Utah's own pages. It has the same 3 steps, the same promises, and the same tests as the Oregon check. Every question and result is in [docs/checker-logic.md](docs/checker-logic.md).
- **The Utah guide is whole.** Every link on a Utah page leads to a Utah page or an official source. The banner, footer, and source lists on Utah pages lead to Utah's own About, Privacy, Accessibility, and Every source pages. The Utah "Every source" page lists Utah's sources and the federal, court, and site sources the Utah guide uses, and no Oregon sources. The build enforces all of this. The one way across is the link to the other guide's home page.
- The Utah About page and the Utah "Every source" page say plainly that the Utah documents were read with a research tool and that not every one has yet been read in full; the registry shows which.
- Every design choice: [docs/decisions/0013-utah-section.md](docs/decisions/0013-utah-section.md).
- A second pass the same day fetched 19 of the Utah sources again and compared them with the fact log. Everything compared matched. Two changes came out of it: the turned-down page now says the 15 days to keep medical benefits run from the date on the notice, and the corrections log notes that Utah's glossary names a different hearing office than its hearings page. Details and what was not fetched again: [docs/research-log.md](docs/research-log.md).
- **Read this before sharing the Utah guide.** It was researched in one day through a tool that answers questions about a document instead of returning its full text. The Utah documents were accessed and reviewed against the facts they support; the registry shows which were read in full. Checkpoint 2026-11-24 covers the source review, and [docs/research-log.md](docs/research-log.md) lists what could not be checked.

### Oregon

- Checkpoint 2026-11-16 done early, on Nov. 10. OHA's federal changes page (S07, still last updated Sept. 18, 2026), provider FAQ (S01), and exemptions explainer (S03) had not changed and did not mention the Oct. 29, 2026 court ruling. The "In the news" note on the reasons and health pages now says "As of Nov. 10, 2026." OHP.Oregon.gov/HR1 (S24) still has to be read by hand.
- The court entered judgment and dismissed *Commonwealth of Massachusetts v. Oz* on Oct. 29, 2026. No notice of appeal appeared in the docket entries through Nov. 6. The docket is now in the registry as S40. Next checkpoint: 2026-12-10.
- The home page, the About page, and the 404 page link to the Utah guide. The About page has a "Two guides" section.

### Both guides

- Every page's source list now shows the date each source was last checked, next to the date printed on it. Before, one line gave a single date for all of them, which stopped being true as soon as one source was re-read.
- Each home page has a state switch above its headline: two big buttons under "Pick your state," Oregon first and Utah second. The guide you are in is filled and says so in words. The other is an outlined button that names the guide it opens. It replaces a one-line text link that sat below the first screen on a phone. It uses the menu's look and colors, stacks on narrow screens and at large text sizes, stays visible in "Just the key points" mode, and prints without the fill. The browser tests measure it as a tap target.
- The footer's "All pages" list shows every page of the guide you are in, then one link to the other guide.
- The "page not found" page belongs to neither guide. It shows both guides, with a menu and footer that name both states.
- The Oregon About page no longer speaks for Utah. Its "not run by" and "only OHP decides" lines are back to their 0.1.3 wording.

### Build and upkeep

- `tools/build.py`: guide sections (`section: utah` in page metadata), a copy of each `shared: yes` page for each guide with `<!-- utah -->` and `<!-- oregon -->` blocks for the parts that differ, a rule that stops the build if a page links to, cites, or borrows facts from the other guide, one "facts last checked" date per guide, a count check for Utah's documents like the one for Oregon's, a format check on every source's `checked` date, and dates written in the site's style from one value instead of two constants that could drift apart.
- `data/review.json`: Utah checkpoints for 2026-11-24 (a person reads the Utah pages against their sources), 2027-03-01 (renewals), and 2027-06-15 (Targeted Adult Medicaid), and Utah work added to the Dec. 10, Dec. 13, Dec. 31, and Jan. 15 checkpoints.
- Docs updated to match: README, methodology, style guide, boundaries, design, maintenance, roadmap, research log, and decision 0012 (a recorded difference from Strand).
- The check's script is now one engine (`checker.js`) and one file of words for each state (`checker-oregon.js`, `checker-utah.js`). The Oregon words did not change. The browser tests run every path through both checks, pick every choice once to confirm each has words, and fail if a result names the other state or links to the other guide.
- Checked on Nov. 10, 2026: build freshness, structure lint (35 pages), contrast, reading level (Utah pages grade 2.4 to 7.1), dated checkpoints, and the real-browser tests on all 35 pages. On Nov. 11, 2026, the GitHub workflows passed axe-core on all 35 pages before the merge, and the live-site check after it. The link check ran on the Utah links for the first time the same day (see 0.2.1 beta).

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
