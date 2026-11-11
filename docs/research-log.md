# Research log

Registry IDs refer to [sources.md](sources.md).

- [Release 0.1.0 beta](#release-010-beta-oregon): Oregon content research on **Nov. 2, 2026**, and hosting research on **Nov. 3, 2026**.
- [Release 0.2.0 beta](#release-020-beta-utah-and-an-oregon-re-check): Utah content research and an Oregon re-check on **Nov. 10, 2026**.

All of it was done with an AI research assistant (Claude, by Anthropic) working under the maintainer's direction.

## Release 0.1.0 beta: Oregon

### Read in full or in part

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

### Hosting research (Nov. 3, 2026)

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

### Currency checks

- Court docket (CourtListener copy) searched for entries after Oct. 29, 2026: none found. CourtListener can lag the court's own system (PACER).
- OHA's federal changes page (S07) and provider FAQ (S01) were checked for any response to the Oct. 29 ruling: none found.
- Oregon Administrative Rules: one web search for filings implementing the work or activity rules found only an ODHS chapter 461 proposal (filed July 31, 2026) about noncitizen eligibility and related changes. The Oregon rule text for the work or activity rules is **unverified**.
- The federal statute (Public Law 119-21) was **not opened**. Federal requirements are taken from the federal rule (S27).

### Could not check

| What | Why |
|---|---|
| OHP.Oregon.gov/HR1 and OHP.Oregon.gov/Resources (S24, S23) | The site tells automated tools not to load it (robots.txt). Check by hand. |
| ODHS and OHA Writing Style Guide (me9412) | Same reason. |
| Whether ONE.Oregon.gov redirects to benefits.oregon.gov | Our tools could not follow the redirect. |
| News articles from Fierce Healthcare, Stateline, and U.S. News about the ruling | Site errors. The court order and memorandum were read directly instead. |
| axe-core accessibility engine | The package registry was not reachable from the build environment. The GitHub workflow installs and runs it. |
| The live site, projectstasis.pages.dev | Not reachable from the build environment. `tools/check_live.py` checks it from GitHub Actions every Monday. |

### Not used as support

Third-party summaries (law firm alerts, trade press, a national "Medicaid work navigator" site, and an AI-generated coverage site) were seen in search results. They were used only as leads, never as sources for claims.

## Release 0.2.0 beta: Utah, and an Oregon re-check

Done on **Nov. 10, 2026**.

### How the Utah documents were read

The assistant could not download pages in this session. It read each Utah page and PDF through a fetch tool that answers questions about a document instead of returning its full text. For each source, it asked for the exact wording of every date, number, list, phone number, and address, and it asked more than one source about the same fact wherever it could.

What that means:

- "Read by us: Yes" for a Utah source means read this way, on this date. It does not mean a person or the assistant saw the whole text.
- Words inside quotation marks in the Utah part of [corrections.md](corrections.md) and in the fact log are words the tool returned as quotations. Everything else is paraphrase.
- Long documents were cut off by the tool. The federal rule (S27) and the federal letter to Utah (U30) were read only in their first 100,000 characters.
- A person should read the Utah documents end to end before the Utah guide is promoted. Checkpoint 2026-11-24 in [review.json](../data/review.json) exists for that.

### Utah sources read

| Source | What was asked | Result |
|---|---|---|
| U01 Community engagement page | Who, activities, $580, exclusions, look-back, proof, phones, court or waiver mentions | The core list; says nothing about a court ruling |
| U02 H.R. 1 page for members | Every document link, each rule's wording, tribal status proof, contacts | The hub; a second general phone number; retroactive coverage wording |
| U03 Support page on meeting the rules | How to report, how exclusions are confirmed, how to send papers | Records first; form 742; 3 ways to confirm a medically frail or treatment exclusion |
| U04 DWS page for adults | Start dates, look-back, exclusions, exceptions, verification | Jan. 1, 2027 for applicants; renewals due March 2027 or later for members; the 30-day form |
| U05 Exclusions and exceptions table | Every row | Exclusions, mandatory exceptions, optional hardships; 2 must be requested |
| U06, U13 Staff toolkits | Scripts, deadlines, verification | Personal letter from DWS; no day counts |
| U07 Member letter (July 2026) | Every statement | No action yet; keep myCase current |
| U08 Glossary (August 2026) | Every term | Agency roles; TAM ending; retroactive coverage |
| U09 Quick guide (June 2026), U10 flyer | Every statement | Immigrant change; half-time as the school defines it |
| U11 Partner FAQ (January 2026), U12 member FAQ | Every topic | Waiver request of July 3, 2025; about 83,000 members in the 2 programs |
| U14 Apply page, U15 form 61MED, U16 DWS how-to-apply page | Ways to apply, addresses, fax numbers, timing, language help | 3 ways to apply; two sets of fax numbers; 30 and 90 days; the form does not ask about the rules |
| U17 Hearings page, U18 and U20 DWS appeal pages, U19 form 490 | Who hears what, deadlines, continued benefits, how to ask | DWS hears eligibility disputes; 90 days; 15 days to keep medical benefits |
| U21, U22, U24 Support site | Options after losing coverage, free help | No waiting period to apply again; Emergency Medicaid; Take Care Utah |
| U23 Take Care Utah, U37 Utah Legal Services | Their own services and contact details | Free help; statewide |
| U25 Expansion page, U26 TAM page | Eligibility, income, employer insurance, TAM changes | Income table; two different sets of income numbers on one page |
| U27 Immigrant letter, U28 tribal status letter, U29 letter key | Every statement | Groups listed; proof list and Jan. 1, 2027 date; paper colors |
| U30 Federal letter to Utah (Sept. 25, 2026) | Whether it approves a Utah-designed requirement | It does not; it conforms Utah's demonstration to the federal requirement |
| U31 Language services page | What help, how to ask | Free language help; no TTY number |
| U33 DWS office finder | Whether it loads | It loads |
| S27 Federal rule | Household income, community service definition, half-time, re-applying, notice period | Confirmed in sections I and II.C; sections II.E, II.H, and II.J were beyond what the tool read |
| S28 Court order, S40 docket | The order's full text; docket entries 139 to 151 | Read in full through CourtListener's records. Utah is not among the plaintiffs. Judgment entered Oct. 29; no notice of appeal through the Nov. 6 entries |

### Second pass on the Utah facts

Done the same day, before the branch was offered to the maintainer. The assistant fetched the sources again, without relying on the first pass, and compared the answers with the fact log.

- **Fetched again:** U01, U02, U03, U04, U05, U08, U14, U15, U16, U17, U18, U19, U20, U21, U22, U28, U29, the federal rule (S27, first 100,000 characters), OHA's federal changes page (S07), and the court record (docket entries 145 to 151, with the text of the Oct. 29 memorandum, order, and judgment).
- **Result:** every date, number, phone number, fax number, address, and list that was compared matched the fact log. The disagreements in [corrections.md](corrections.md) items 1, 3, 4, 5, 8, and 9 showed up again the same way.
- **Changed because of it:** the page for people who were turned down now says the 15 days to keep medical benefits run from the date on the notice (U19). The corrections log now notes that the glossary (U08) names a different hearing office than the hearings page (U17).
- **Confirmed to load, not read:** the Spanish application (U15S), the Spanish hearing form (U19S), and the Emergency Medicaid page (U36). The two Spanish forms show the same form numbers and dates as the English ones.
- **Not fetched again:** U06, U07, U09, U10, U11, U12, U13, U23, U24, U25, U26, U27, U30, U31, U33, and U37. Claims that rest only on those sources have had one pass.
- **Same limit as the first pass:** the tool answers questions about a document. Two passes with it do not replace a person reading the documents. Checkpoint 2026-11-24 stands.

### Oregon re-check

Done early, ahead of checkpoint 2026-11-16.

- **S07** (federal changes page): still "Last updated Sept. 18, 2026." No mention of the ruling.
- **S01** (provider FAQ) and **S03** (exemptions explainer): no date shown; no mention of the ruling; the work-limit sentence in S01 is unchanged.
- **S24 and S23** (OHP.Oregon.gov pages) still have to be read by hand.
- **Court docket (S40):** entry 149 enters judgment and dismisses the case on Oct. 29, 2026. Entries 150 and 151 (Nov. 6) are a transcript and its notice. No notice of appeal appeared. CourtListener can lag the court's own system (PACER).
- The rest of the Oregon sources were **not** re-read. The Oregon guide's "facts last checked" date stays Nov. 2, 2026, and each re-read source shows its own date.

### Utah: could not check

| What | Why |
|---|---|
| Utah Legal Services' Get Help page (intake hours, who qualifies) | The page returned an error. Its phone numbers come from the state's hearing form (U19). |
| Form 742 (Community Engagement Declaration), the Medically Frail Exclusion Screener, and the provider attestation form | Named on U03 without links, and not on DWS's public forms page. |
| myCase (U32) | A login page. |
| The Spanish forms (U15S, U19S), Emergency Medicaid page (U36), 211 Utah (U35), HealthCare.gov (U34), the diagnosis code list (U38) | Linked only; not opened. |
| The CourtListener docket web page (S40) | It tells automated tools not to load it. The docket was read through CourtListener's search service instead. |
| Whether the phone and fax numbers work | Nobody called them. |
| The federal statute (Public Law 119-21) | Still **not opened**. |
| Utah Administrative Code filings that implement the requirement | One web search found none; a March 26, 2026 Utah Medicaid rules summary listed none. **Unverified.** |
| The live link check | The session had no general internet access from its command line. The weekly workflow runs it. |

### Utah: not used

- **Disability Law Center (Utah's protection and advocacy agency).** Its site says it does not help with applications for, or denials of, public benefits like Medicaid, so the Utah guide does not send people there for that.
- Third-party summaries seen in search results (an insurance sales site, a news aggregator, an advocacy petition) were used only as leads, never as sources for claims.

