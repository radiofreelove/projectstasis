# Maintenance runbook

## What runs on its own

| When | What | Where | If it fails |
|---|---|---|---|
| Every push and pull request | Build freshness, structure lint, contrast, reading level, browser tests with axe-core | [checks.yml](../.github/workflows/checks.yml) | The commit shows a red X. Fix it before merging. |
| Every push to any branch | Cloudflare Pages runs build freshness and structure lint, then publishes `site/`: `main` to <https://projectstasis.pages.dev/>, other branches and pull requests to preview addresses | Cloudflare (settings below) | Nothing new is published, and the live site stays as it was. The commit shows a failed Cloudflare check. |
| Every push to `main`, after Cloudflare publishes | Live-site check: every page, asset, and header matches the commit (waits up to 15 minutes) | [live.yml](../.github/workflows/live.yml) | The commit shows a red X: visitors are not getting what is in `main`. Check the Cloudflare build. |
| Mondays, and Jan. 1 each year, 15:17 UTC (morning in Oregon) | Official link check (respects robots.txt), dated checkpoints, and a live-site check that every page, asset, and header matches this repository | [weekly.yml](../.github/workflows/weekly.yml) | Opens a GitHub issue with the report. |

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

1. Open the pages that block automated tools and read them by hand:
   - <https://ohp.oregon.gov/HR1> (registry S24)
   - <https://ohp.oregon.gov/Resources> (registry S23)
2. Re-read OHA's federal changes page (S07) and note its "last updated" date in `data/sources.json`.
3. Search for new OHA notices, fact sheets, and forms about the rules. Add new ones to the registry as `state-explainer` entries.
4. Check the court docket for *Commonwealth of Massachusetts v. Oz*, No. 1:26-cv-12962 (D. Mass.), for appeals or new orders.
5. Search the Oregon Administrative Rules Database for filings that implement the work or activity rules (likely OAR chapter 410, division 200, or chapter 461; unverified).
6. Watch for a CMS final rule replacing the interim final rule (S27).

### At each checkpoint in `data/review.json`

Do the listed work, then move or remove the checkpoint and say what you did in [CHANGELOG.md](../CHANGELOG.md).

## How to change a fact

1. Edit the page in `src/pages/`.
2. Update the claim in `data/claims.json` (statement, sources, kind, note).
3. If there is a new source, add it to `data/sources.json` with `checked` set to today and `opened` set honestly.
4. If official sources disagree, add an item to [corrections.md](corrections.md).
5. Update `FACTS_CHECKED_ISO` and `FACTS_CHECKED_TEXT` in `tools/build.py` when you re-check the whole site.
6. Run:

   ```bash
   python3 tools/build.py
   python3 tools/check_structure.py
   python3 tools/check_contrast.py
   python3 tools/check_reading_level.py
   python3 tools/check_review_dates.py
   python3 tools/browser_check.py
   ```

   To look at the result the way visitors will see it, run `python3 tools/serve.py` and open <http://127.0.0.1:8000>.

7. Add a line to [CHANGELOG.md](../CHANGELOG.md). Commit `src/`, `data/`, `site/`, and `docs/` together.

## If something on the site is wrong

1. If the fix is clear, fix it and push to `main`. Cloudflare publishes it within a few minutes.
2. If not, replace the sentence with a link to the official source and a plain line such as "Check OHA's page for the latest." Saying less is better than saying something wrong.
3. Log it in [corrections.md](corrections.md) and the changelog.

## If an official link breaks

1. Search the publisher's site for the new address.
2. Update `data/sources.json` (and the page, if the address is written in the text), with today's date.
3. If the document is gone, remove the claim or find another official source. Never point people to an unofficial copy of a state form.

## Rules for maintainers

- Use only public sources. Never use non-public information from any job, agency, or client.
- Never post anyone's case details in issues, commits, or docs.
- Never add analytics, trackers, fonts, or scripts from other sites. The CSP will block them, and the privacy page promises there are none.
