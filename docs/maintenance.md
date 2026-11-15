# Maintenance runbook

## What runs on its own

| When | What | Where | If it fails |
|---|---|---|---|
| Every push and pull request | Build freshness, structure lint, contrast, reading level, browser tests with axe-core | [checks.yml](../.github/workflows/checks.yml) | The commit shows a red X. Fix it before merging. |
| Every push to any branch | Cloudflare Pages runs build freshness and structure lint, then publishes `site/`: `main` to <https://projectstasis.pages.dev/>, other branches and pull requests to preview addresses | Cloudflare (settings below) | Nothing new is published, and the live site stays as it was. The commit shows a failed Cloudflare check. |
| Every push to `main`, after Cloudflare publishes | Live-site check: every page, asset, and header matches the commit (waits up to 15 minutes) | [live.yml](../.github/workflows/live.yml) | The commit shows a red X: visitors are not getting what is in `main`. Check the Cloudflare build. |
| Mondays, and Jan. 1 each year, 15:17 UTC (morning in Oregon) | Official link check (respects robots.txt), evidence audit (what each source says, compared with its baseline), dated checkpoints, and a live-site check that every page, asset, and header matches this repository | [weekly.yml](../.github/workflows/weekly.yml) | Opens one GitHub issue with all the reports. |
| The same run, only if the repository variable `MECHANICAL_UPDATES` is `on` (it is off) | Drafts "checked" date updates for sources the evidence audit found unchanged | [weekly.yml](../.github/workflows/weekly.yml), job `mechanical` | Opens a pull request for a person to review. Nothing merges it. See "The mechanical update switch" below. |

## Cloudflare Pages settings

These live in the Cloudflare dashboard, not in this repository, so they are recorded here. Change them only on purpose, then run the live-site check by hand (Actions tab, **Live site check**, **Run workflow**).

| Setting | Value |
|---|---|
| Project name | `projectstasis` (address <https://projectstasis.pages.dev/>) |
| Connected repository | `radiofreelove/projectstasis`, through the GitHub app Cloudflare Workers and Pages |
| Production branch | `main` |
| Framework preset | None |
| Build command | `python3 tools/build.py --check && python3 tools/check_structure.py` |
| Build output directory | `site` |
| Root directory | Blank (the repository root) |
| Environment variables | None |

If the Cloudflare build fails, open the failed Cloudflare check on the commit in GitHub (the log needs the maintainer's Cloudflare login), run the same two commands on your computer, fix the problem, and push again.

## Never turn these on

Each would break a promise the site makes, and the weekly live-site check would report it:

- **Web Analytics** (or any analytics): adds a tracking script to every page on the next deploy.
- **Zaraz** or any other "third-party tools" feature: loads code from other companies.
- **Pages Functions** (a `functions/` folder or a `_worker.js` file): runs server code, and the site promises it has none. Headers in `_headers` also do not apply to Functions responses.
- **A custom domain** without first changing `BASE_URL` in `tools/build.py`, rebuilding, and running `python3 tools/check_live.py --base` with the new address. Settings on the domain's Cloudflare zone could change the pages, and the live check is what would catch it.

Optional and safe: **Enable access policy** (Settings, General) limits preview addresses to the maintainer's Cloudflare account. The live address stays public.

## What a person must do

### At least every 30 days

1. Open the pages that block automated tools and read them by hand. They carry `"link_check": "by hand"` in `data/sources.json`, so the weekly link check lists them and does not request them:
   - <https://ohp.oregon.gov/HR1> (registry S24)
2. Open the newest **Weekly source check** run in the Actions tab and read its "Check by hand" list. Open at least one paper application link from it in a browser. The forms site (`sharedsystems.dhsoha.state.or.us`) sends an incomplete certificate chain, so the link check can tell that each form still answers but cannot verify the site the way a browser does.
3. Re-read OHA's federal changes page (S07) and note its "last updated" date in `data/sources.json`.
4. Search for new OHA notices, fact sheets, and forms about the rules. Add new ones to the registry as `state-explainer` entries.
5. Check the court docket for *Commonwealth of Massachusetts v. Oz*, No. 1:26-cv-12962 (D. Mass.), for appeals or new orders.
6. Search the Oregon Administrative Rules Database for filings that implement the work or activity rules (likely OAR chapter 410, division 200, or chapter 461; unverified).
7. Watch for a CMS final rule replacing the interim final rule (S27).

For the Utah guide, in the same sitting:

1. Open myCase, <https://jobs.utah.gov/mycase/> (registry U32), and confirm it still offers a way to sign in or apply. It is marked `"link_check": "by hand"` because it answers 404 to the link check. Confirm Utah Medicaid's apply page (U14) still sends people there.
2. Re-read Utah Medicaid's H.R. 1 page (U02), its community engagement page (U01), its support page (U03), and DWS's page for adults (U04). None shows a date, so compare the wording with the notes in `data/sources.json`.
3. Look for new Utah letters, toolkits, and forms on U02, and for form 742, the Medically Frail Exclusion Screener, and a new version of form 61MED.
4. Search the Utah State Bulletin and the Utah Administrative Code (title R414) for filings that implement the community engagement requirement (unverified whether any exist).
5. Check whether Utah's pages say anything about the court ruling.

For the Washington guide, in the same sitting:

1. Open HCA's work requirements page, <https://www.hca.wa.gov/free-or-low-cost-health-care/i-need-medical-dental-or-vision-care/apple-health-medicaid-work-requirements> (registry WA22), in a browser, and its screener at hca.wa.gov/ah-work-req. An automated fetch returned an empty page on Nov. 12, 2026, so only a person can read it. Compare its list of ways to meet the rule with step 3 of the Washington check.
2. Open the June 2026 fact sheet at its own HCA address (WA05). It answered 403 to an automated fetch on Nov. 12, 2026. Confirm the 5 ways to meet the rule and the exemption list still match `src/pages/washington/washington-rules.html` and `washington-reasons.html`.
3. Re-read HCA's two client pages on the changes (WA01, WA02) and its stakeholder page (WA03). None shows a date, so compare the wording with the notes in `data/sources.json`. Look for any change to the Jan. 1, 2027 start and for any word on a delay. The guide says nothing about a delay of the start until an official source does. Look also for Washington's choice on the federal hold harmless period (S41, claim WA-HH-05); do the same on OHA's pages for Oregon (C-HH-STATE) and Utah's pages for Utah (U-HH-STATE).
4. Re-read the Apple Health Expansion page (WA23) and note whether enrollment is open or closed. Update `washington-immigration.html` to match.
5. Check HCA's contact, apply, and appeal pages (WA06, WA07, WA08, WA11) for a changed phone number, fax number, or hours. The numbers on the Washington pages are copied from them.
6. Check the Attorney General's litigation tracker (WA14) and the docket (S40) for an appeal or a new order in *Commonwealth of Massachusetts v. Oz*, and for any other case about the work rules that names Washington.
7. Search the Washington Register and HCA's rulemaking pages for filings that amend chapter 182 of the Washington Administrative Code for H.R. 1, and re-read the five sections the guide relies on (WA15 to WA19) on the Legislature's site.
8. Look for what the research did not find: HCA's August 2026 eligibility training material, any state plan amendment or waiver request (including a good-faith delay request), the work requirements notice HCA sends clients, and the list of fact sheet languages. Add what you find to the registry, with `opened` set honestly.

### At each checkpoint in `data/review.json`

Do the listed work, then move or remove the checkpoint and say what you did in [CHANGELOG.md](../CHANGELOG.md).

## How to change a fact

1. Edit the page in its guide's folder: `src/pages/oregon/`, `src/pages/washington/`, `src/pages/utah/`, or `src/pages/shared/` for the 4 pages every guide has.
2. Update the claim in `data/claims.json` (statement, sources, kind, note).
3. If there is a new source, add it to `data/sources.json` with `checked` set to today and `opened` set honestly.
4. If official sources disagree, add an item to [corrections.md](corrections.md).
5. Set the source's `checked` date in `data/sources.json` to the day you re-read it. Each page shows that date next to the source. When you re-check a whole guide, also update that guide's `facts_iso` in the `SECTIONS` list in `tools/build.py`; the footer date comes from it.
6. Run:

   ```bash
   python3 tools/build.py
   python3 -m unittest discover -s tools/tests
   python3 tools/check_structure.py
   python3 tools/check_contrast.py
   python3 tools/check_reading_level.py
   python3 tools/check_review_dates.py
   python3 tools/browser_check.py
   ```

   To look at the result the way visitors will see it, run `python3 tools/serve.py` and open <http://127.0.0.1:8000>.

7. Add a line to [CHANGELOG.md](../CHANGELOG.md). Commit `src/`, `data/`, `site/`, and `docs/` together.

## Releasing a version

1. Change `VERSION` in `tools/build.py`. Every page shows it in the footer, so run `python3 tools/build.py`.
2. Add an entry to [CHANGELOG.md](../CHANGELOG.md) headed with the same version and the date, like `## 0.2.1 beta (2026-11-11)`. The checks fail if a version has no entry.
3. Merge to `main`. After the checks pass there, [release.yml](../.github/workflows/release.yml) tags the commit (`v0.2.1-beta`) and publishes a GitHub release whose notes are that changelog entry. If the tag already exists, it does nothing.

To see what a release would say before merging, run `python3 tools/release_notes.py`.

## Adding a guide for another state

See [adding-a-guide.md](adding-a-guide.md).

## If something on the site is wrong

1. If the fix is clear, fix it and push to `main`. Cloudflare publishes it within a few minutes.
2. If not, replace the sentence with a link to the official source and a plain line such as "Check OHA's page for the latest" (or Utah Medicaid's, on a Utah page). Saying less is better than saying something wrong.
3. Log it in [corrections.md](corrections.md) and the changelog.

## If an official link breaks

A source the evidence audit calls "checker-blocked" is not a broken link; see "Evidence audit" below. First read why the link check called it broken. "Broken" means the site answered with an error, did not answer, or has a certificate a browser would warn about. Addresses the tool could not judge are under "Check by hand" and do not open an issue. Open the address in a browser before changing anything.

1. Search the publisher's site for the new address.
2. Update `data/sources.json` (and the page, if the address is written in the text), with today's date.
3. If the document is gone, remove the claim or find another official source. Never point people to an unofficial copy of a state form.

## Evidence audit

The link check asks whether a source still answers. The evidence audit asks whether it still says the same thing.

```bash
python3 tools/evidence_audit.py --report evidence-report.md
```

For every source in `data/sources.json`, the tool fetches the address the way the link check does: it respects robots.txt, sends HEAD and then GET, asks one site at a time with a pause, and names itself. It turns the reply into text it can compare, and compares a SHA-256 of that text with [data/evidence_baseline.json](../data/evidence_baseline.json).

- **A web page** is compared as text: the words a reader sees, with tags, scripts, and styles removed.
- **A PDF** is compared by its bytes, because the project declares no PDF library. The baseline marks it `"mode": "bytes"`. A change report for a PDF is lower-confidence: the same words saved again make new bytes. Open the file before you believe it.

### The four states

Every source ends in exactly one.

| State | What it means | What to do |
|---|---|---|
| Unchanged | The content matches the baseline. | Nothing. |
| Changed | The content differs. For a web page, the report shows what changed, up to a limit. It names the claims in `data/claims.json` that cite the source and the guide pages that show those claims. | Re-read the source. A change is a prompt to read, not proof that a fact is wrong: a new menu item changes a page too. If a fact changed, follow "How to change a fact". Then refresh that source's baseline (below). |
| Unreachable | The connection failed, the reply was cut short twice, or the server answered with an error. Nothing was compared. | Read the link check report in the same issue. If the link check also calls the address broken, follow "If an official link breaks". If not, wait for next week's run. |
| Checker-blocked | The site answered 401 or 403 to this tool, its robots.txt keeps this tool out, or the registry says `"link_check": "by hand"`. | A person opens it, as in the 30-day list above. This state says nothing about the source. It is not a dead link, and it is not a removed document. |

The report has one more list, **Not yet baselined**: sources with no stored hash, because they were blocked or unreachable when the baseline was written, or were added to the registry since. A missing baseline is never counted as a change.

Only a changed source fails the run and opens the weekly issue. Blocked and unreachable sources are listed in the report and do not fail the run; the link check is what fails on an address that stops answering.

### The baseline

- **What the baselines rest on.** The baselines rest on the project's November 2026 verified source checks. Each entry records the source's `checked` date from the registry on the day it was written (`registry_checked`). That check is what stands behind the hash.
- **What the baseline run was not.** The run that wrote the baseline on Nov. 15, 2026 was a tool fetching each address and storing a hash. It was not a fresh read of every source by a person, and nothing here says it was.
- **What it holds.** One entry per source: its address, the fetch date, the fetch state, how it is compared (`text` or `bytes`), the SHA-256, and the length. On Nov. 15, 2026: 93 of 120 sources were read (56 as text, 37 as bytes), 16 were checker-blocked, and 11 were unreachable. The 27 with no hash are "not yet baselined".
- **Hashes, not text.** The repository does not keep copies of official pages. To show what changed, the tool keeps each page's text in `.evidence-snapshots/`, which is not committed. The weekly run saves that folder between runs. If the saved text is gone, the report still names the changed source, its claims, and its pages, and says there is no diff to show.
- **A baseline is refreshed only on purpose.** Comparing never rewrites it. Refresh one source after a person has re-read it and the registry's `checked` date is set:

  ```bash
  python3 tools/evidence_audit.py --write-baseline --only S07
  ```

  Do the same to give a "not yet baselined" source its first hash, after a person has read it. Never refresh a baseline to make a "changed" report go away without reading the source. A refresh keeps the old hash for any source it cannot read that day. Say what you refreshed, and why, in [CHANGELOG.md](../CHANGELOG.md).

### Dated language

[dated-language.md](dated-language.md) lists the wording whose truth depends on the date: start dates, deadlines, "as of" lines, and dated figures. Each entry gives the exact wording, where it is, the day it expires, and what to do then. Each is tied to a checkpoint in `data/review.json`, so the weekly check raises it. When you add dated wording to a page, add it to that list and add a checkpoint. When you do the work, remove the entry.

### The mechanical update switch

`tools/mechanical_update.py` drafts one kind of change: for each source an evidence audit found **unchanged**, it sets the `checked` date in `data/sources.json` to the day of the audit. The hash match is the proof. It changes no other field and no other source. It refuses to write anything if a source it would touch is changed, blocked, unreachable, or not yet baselined, or if the audit's hash or address does not match the baseline and the registry. It leaves alone any source read from a site that sends an incomplete certificate chain.

A date set this way means "a tool found the same content as the last verified check". It does not mean a person read the source again, and the baseline entry keeps the date of the check it rests on.

**The switch is off.** The weekly workflow has a second job, `mechanical`, that runs only when the repository variable `MECHANICAL_UPDATES` is exactly `on`. The variable does not exist until the owner makes it, so nothing runs.

To turn it on:

1. In the repository on GitHub: Settings, Secrets and variables, Actions, Variables, New repository variable. Name `MECHANICAL_UPDATES`, value `on`.
2. In Settings, Actions, General, Workflow permissions: allow GitHub Actions to create pull requests. Without it the job fails at its last step and changes nothing.

To turn it off, delete the variable or set it to anything else.

When it is on, each weekly run:

1. Runs the evidence audit again, after the first job, and runs the tool on its result.
2. Rebuilds the site, because every page shows each source's checked date.
3. Opens a pull request that holds the date changes in `data/sources.json` and the built files that show them (`site/`, `docs/sources.md`), and nothing else. If anything else differs, it stops and opens nothing. The pull request body lists every date changed and carries the audit report.

It never merges. A person reads the pull request and merges or closes it. GitHub does not start the checks on a pull request opened by a workflow, so run **Checks** by hand on its branch (Actions tab, **Checks**, **Run workflow**) before merging. This is the only job in the repository with permission to write to it (`contents: write`, `pull-requests: write`); the first job's permissions did not change.

To try the tool on your computer without changing the registry, give it a copy:

```bash
python3 tools/evidence_audit.py --report evidence-report.md --results evidence-results.json
cp data/sources.json /tmp/sources.json
python3 tools/mechanical_update.py --audit evidence-results.json --registry /tmp/sources.json
```

## Rules for maintainers

- Use only public sources. Never use non-public information from any job, agency, or client.
- Never post anyone's case details in issues, commits, or docs.
- Never add analytics, trackers, fonts, or scripts from other sites. The CSP will block them, and the privacy page promises there are none.
