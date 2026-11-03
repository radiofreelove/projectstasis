# Research log

Release 0.1.0 beta. Content research done on **Nov. 2, 2026**, and hosting research on **Nov. 3, 2026**, with an AI research assistant (Claude, by Anthropic) working under the maintainer's direction. Registry IDs refer to [sources.md](sources.md).

## Read in full or in part

| Source | What was read | Result |
|---|---|---|
| S01 OHA provider FAQ | Whole document | Timeline, ways to meet rules, medical exemptions, retroactive coverage, renewals, Healthier Oregon, Open Card |
| S02 OHA fact sheet (June 1, 2026) | Whole document | Who the rules apply to, exemptions list. Predates the federal rule. |
| S03 OHA exemptions explainer | Whole document | 3 tiers of exemptions, 2028 proof notes, contacts |
| S04 OHA journey maps | Whole document | Look-back, data checks, 35-day reply, reminders, hearings, reapplying, Marketplace, clinics |
| S05 OHA mythbusters | Whole document | Household $580, volunteering, individual review, no monthly reports, Healthier Oregon |
| S06 OHA talking points (June 9, 2026) | Whole document | Many already meet rules; Marketplace help limit; reapply any time |
| S07 OHA federal changes page (Sept. 18, 2026) | Whole page | Look-back for applicants, renewals, and reapplications; linked documents |
| S08 OHA sample outreach notice | Whole document | Reporting routes, mailing address, fax |
| S09 OHA how-to-apply page | Whole page | Ways to apply, hours, language lines, technical support, 17 paper applications, income chart |
| S10 OHP application 7210 (05/01/20) | Whole document except the last 747 characters | No questions about the new rules |
| S11 OHA Healthier Oregon page | Whole page | Eligibility, ways to apply, Open Card, public charge pointer |
| S12 OHA public charge page | Whole page | Sept. 18, 2026 federal change; legal help directories |
| S13 OHA OHP Bridge page | Whole page | Who Bridge covers; no member costs; silent on work rules |
| S14 OHA appeals and hearings page | Whole page | 60-day deadline for OHA notices, mostly about services |
| S25 Public Benefits Hotline | Whole page | Phone, hours, income limits, counties |
| S26 Disability Rights Oregon FAQ | Whole page | Disability exemptions, ADRC number, request-help form |
| S27 Federal interim final rule, 91 Fed. Reg. 33348 | First 100,000 of 500,000 characters (preamble through section II.C.8) | Who is covered, ways to comply, $580 test, school definition, work and community service definitions, credit-hour conversion |
| S28 Court order, Oct. 29, 2026 | Whole order | Vacatur and injunction on the medically frail clause; 6-month bar on penalties |
| S29 Court memorandum, Oct. 29, 2026 | Searched for "attestation" and "twelve" | Upheld 12-month look-back and self-attestation limit |
| S30 OHA and ODHS Senate presentation (Sept. 9, 2026) | Whole document | About 600,000 members could be subject; timeline; phased outreach |
| S31 ODHS brand guidelines (07/25) | Whole document | Palette and contrast pairings |
| S32 W3C COGA note | First 100,000 of 127,000 characters | Status, objectives, patterns |
| S33 WCAG 2.2 | Status and new criteria | Recommendation of 12 December 2024 |
| S34 Cloudflare Privacy Policy (effective Nov. 4, 2025) | Whole page | Processes visitors' IP addresses and traffic data as a processor for its customers; no fixed retention period |
| S35 Oregon DOJ release (June 29, 2026) | Whole page | Oregon joined the suit |
| K02 ODHS partner timeline | Whole document | Dates may change with federal guidance |

## Hosting research (Nov. 3, 2026)

Cloudflare's own documentation, read to set up hosting. The decision is in [decisions/0011-cloudflare-pages.md](decisions/0011-cloudflare-pages.md).

| Cloudflare page (last updated) | What it settled |
|---|---|
| [Pages overview](https://developers.cloudflare.com/pages/) (Aug. 25, 2026) | Cloudflare says "Start new projects with Workers." Pages is still offered on all plans. |
| [Serving Pages](https://developers.cloudflare.com/pages/configuration/serving-pages/) (Oct. 10, 2026) | `.html` addresses redirect to shorter ones; a top-level `404.html` is served for missing addresses; default headers, including `Access-Control-Allow-Origin: *` |
| [Headers](https://developers.cloudflare.com/pages/configuration/headers/) (Aug. 25, 2026) | `_headers` syntax; it replaces default headers of the same name; it is not served publicly; it does not apply to Pages Functions |
| [Preview deployments](https://developers.cloudflare.com/pages/configuration/preview-deployments/) (Oct. 12, 2026) | Public by default, with `X-Robots-Tag: noindex`; optional access policy |
| [Build image](https://developers.cloudflare.com/pages/configuration/build-image/) (Oct. 26, 2026) | Python 3.13.3 is installed, so the build command can run the checks |
| [Git integration guide](https://developers.cloudflare.com/pages/get-started/git-integration/) (Apr. 21, 2026) and [GitHub integration](https://developers.cloudflare.com/pages/configuration/git-integration/github-integration/) (Oct. 15, 2026) | Dashboard steps; the GitHub app is named Cloudflare Workers and Pages; builds report as checks on commits |
| [Web Analytics](https://developers.cloudflare.com/pages/how-to/web-analytics/) (Apr. 21, 2026) | Turning it on adds a script to every page on the next deploy |
| [Limits](https://developers.cloudflare.com/pages/platform/limits/) (Sept. 5, 2026) | Free plan: 500 builds a month, 20,000 files, 25 MiB per file, 100 header rules |

GitHub's lack of custom headers on GitHub Pages comes from [GitHub community discussion #54257](https://github.com/orgs/community/discussions/54257) (May 2023 to Sept. 2026, user reports and replies written for GitHub).

## Currency checks

- Court docket (CourtListener copy) searched for entries after Oct. 29, 2026: none found. CourtListener can lag the court's own system (PACER).
- OHA's federal changes page (S07) and provider FAQ (S01) were checked for any response to the Oct. 29 ruling: none found.
- Oregon Administrative Rules: one web search for filings implementing the work or activity rules found only an ODHS chapter 461 proposal (filed July 31, 2026) about noncitizen eligibility and related changes. The Oregon rule text for the work or activity rules is **unverified**.
- The federal statute (Public Law 119-21) was **not opened**. Federal requirements are taken from the federal rule (S27).

## Could not check

| What | Why |
|---|---|
| OHP.Oregon.gov/HR1 and OHP.Oregon.gov/Resources (S24, S23) | The site tells automated tools not to load it (robots.txt). Check by hand. |
| ODHS and OHA Writing Style Guide (me9412) | Same reason. |
| Whether ONE.Oregon.gov redirects to benefits.oregon.gov | Our tools could not follow the redirect. |
| News articles from Fierce Healthcare, Stateline, and U.S. News about the ruling | Site errors. The court order and memorandum were read directly instead. |
| axe-core accessibility engine | The package registry was not reachable from the build environment. The GitHub workflow installs and runs it. |
| The live site, projectstasis.pages.dev | Not reachable from the build environment. `tools/check_live.py` checks it from GitHub Actions every Monday. |

## Not used as support

Third-party summaries (law firm alerts, trade press, a national "Medicaid work navigator" site, and an AI-generated coverage site) were seen in search results. They were used only as leads, never as sources for claims.
