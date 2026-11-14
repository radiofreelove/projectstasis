# The Stasis Project: OHP, Apple Health, and Utah Medicaid, made plain

A free, independent guide for people applying for the Oregon Health Plan (OHP), for Apple Health in Washington, and for Utah Medicaid, as new work or activity rules start on **Jan. 1, 2027**.

**The site:** <https://projectstasis.pages.dev/>

**Why it exists:** Each state explains the new rules across more than a dozen documents ([`data/sources.json`](data/sources.json) lists 22 from Oregon as of Nov. 2, 2026, 18 from Utah as of Nov. 10, 2026, and 25 from Washington as of Nov. 12, 2026). Many carry no date. Some were written before the latest federal rule and a federal court ruling, and a few disagree with each other. This site puts what applicants need on short pages, in plain words, and lists the official source behind every fact.

**Status:** Beta (current version in [CHANGELOG.md](CHANGELOG.md)). Not yet reviewed by a lawyer, a benefits advocate, or people who use assistive technology. See [docs/roadmap.md](docs/roadmap.md).

**The Utah guide was added on Nov. 10, 2026.** It starts at <https://projectstasis.pages.dev/utah>. It was researched in one day through a tool that answers questions about a document instead of returning its text. Every Utah source was accessed and reviewed against the facts it supports; the source registry shows which were read in full. A source review of the Utah guide is checkpointed for Nov. 24, 2026. See [docs/decisions/0013-utah-section.md](docs/decisions/0013-utah-section.md) and [docs/research-log.md](docs/research-log.md).

**The Washington guide was added on Nov. 12, 2026.** It starts at <https://projectstasis.pages.dev/washington>. It was built from a research dossier. Every Washington source was accessed and reviewed against the facts it supports; 14 of its 25 sources have not yet been read in full, and the source registry shows which. A source review of the Washington guide is checkpointed for Nov. 26, 2026. The Washington About page and its source list carry the same warning. See [docs/decisions/0015-front-door-with-three-guides.md](docs/decisions/0015-front-door-with-three-guides.md) and [docs/research-log.md](docs/research-log.md).

## What it is

- Three complete guides built the same way, 17 pages each for OHP applicants, Apple Health applicants, and Utah Medicaid applicants. Each guide has its own home page, 1-minute check, About, Privacy, Accessibility, and Every source pages, so a reader never lands in another state's guide by accident. The build stops if a page in one guide links to a page in another, other than its home page. Each page is written in a Smart Brevity style: a plain headline, one line on why the page exists, a few bold-labeled bullets, then details.
- A 1-minute check ("Do the rules fit me?") for each state that runs in the browser. Answers are never stored or sent.
- Links to each state's own forms, phone lines, and pages, including the paper OHP application in 17 languages and Utah's application in English and Spanish. Nothing is copied or re-hosted, so the forms are always the state's current versions.
- Display settings for text size, spacing, an easy-to-read font (Atkinson Hyperlegible Next, the same option as The Strand Project), colors (warm, white, dark), and a "just the key points" mode.

## What it is not

- Not run by the State of Oregon, the Oregon Health Authority (OHA), or the Oregon Department of Human Services (ODHS).
- Not run by the State of Utah, the Utah Department of Health and Human Services (DHHS), or the Utah Department of Workforce Services (DWS).
- Not run by Washington, the Health Care Authority (HCA), or the Department of Social and Health Services (DSHS).
- Not an application, not an eligibility decision, and not legal advice. Only the state decides who qualifies.

## How the sausage is made

Everything behind the site is public and checkable.

| Question | Where to look |
|---|---|
| What does each fact on the site rest on? | [docs/claims.md](docs/claims.md), generated from [data/claims.json](data/claims.json) |
| Which sources were used, what date is on each, when were they checked, and were they read? | [docs/sources.md](docs/sources.md), generated from [data/sources.json](data/sources.json) |
| Where do official sources disagree, and what does the site do about it? | [docs/corrections.md](docs/corrections.md) |
| How are facts chosen, ranked, and worded? | [docs/methodology.md](docs/methodology.md) and [docs/style-guide.md](docs/style-guide.md) |
| How does the 1-minute check decide what to show? | [docs/checker-logic.md](docs/checker-logic.md) |
| Is it accessible, and for whom? | [docs/accessibility.md](docs/accessibility.md), [docs/contrast.md](docs/contrast.md), [docs/reading-level.md](docs/reading-level.md), [docs/testing.md](docs/testing.md) |
| What happens to visitors' data, and what does the host see? | [docs/privacy.md](docs/privacy.md) |
| Where is it hosted, and how does it get there? | [docs/decisions/0011-cloudflare-pages.md](docs/decisions/0011-cloudflare-pages.md) and [docs/maintenance.md](docs/maintenance.md#cloudflare-pages-settings) |
| Why was it built this way? | [docs/decisions/](docs/decisions/) |
| When must it be re-checked, and how? | [data/review.json](data/review.json) and [docs/maintenance.md](docs/maintenance.md) |
| What was researched, and what could not be checked? | [docs/research-log.md](docs/research-log.md) |
| Where are the limits? | [docs/boundaries.md](docs/boundaries.md) |

## How it works

```text
src/pages/           page text, each with a short metadata header, in one
                     folder per guide (oregon/, utah/) plus shared/: the
                     4 pages marked "shared: yes", built once for each guide
data/sources.json    every outside source and link (the registry)
data/claims.json     every factual statement and what supports it (the fact log)
data/palette.json    ODHS colors and every color pair the site uses
data/review.json     dated checkpoints for re-checking sources
        |
        v
tools/build.py       wraps pages in their guide's header and footer, adds each
                     page's Sources list with the date each source was
                     checked, writes the HTTP headers file, and
                     refuses to build if a page uses an unregistered link or
                     an unlogged fact, or reaches into another guide. The
                     list of guides lives here (docs/adding-a-guide.md)
        |
        v
site/                plain HTML, CSS, three small scripts, and _headers.
                     No framework.
        |
        v
Cloudflare Pages     checks that site/ is current, then publishes it as is,
                     sending the headers in site/_headers
```

The build is Python standard library only. The site has no dependencies, no cookies, no analytics, and no third-party requests. Its Content Security Policy sets `connect-src 'none'`, so the browser itself blocks the page from sending data. Cloudflare sends the policy as a header, with `frame-ancestors 'none'` so other sites cannot frame the pages, and each page repeats it in a meta tag.

## Run it on your computer

```bash
python3 tools/build.py    # build site/ and the generated docs
python3 tools/serve.py    # serve it the way Cloudflare Pages does, then open http://127.0.0.1:8000
```

## Checks

| Command | What it proves |
|---|---|
| `python3 tools/build.py --check` | The site matches its sources; every link is registered; every fact is logged and sourced on its page |
| `python3 -m unittest discover -s tools/tests` | The tools themselves: the rules that keep each guide whole, a made-up third guide, the link checker against local test servers, and the release notes |
| `python3 tools/check_structure.py` | Language, titles, one h1, no skipped headings, skip link, landmarks, labels, unique IDs, valid ARIA references, CSP and referrer policy (in each page and in `site/_headers`), no new windows, no immigration questions, and every internal link points to a page or file that exists |
| `python3 tools/check_contrast.py` | Every color pair meets 7:1 for text and 3:1 for borders and focus |
| `python3 tools/check_reading_level.py` | Each page's estimated reading grade (target 6, fails above 8) |
| `python3 tools/check_review_dates.py` | No dated checkpoint is past due |
| `python3 tools/check_links.py` | Every official link answers, respecting robots.txt; addresses it cannot judge are listed for a person (needs internet) |
| `python3 tools/browser_check.py` | Real-browser tests on a server that behaves like Cloudflare Pages: reflow at 320 px, contrast in every theme, target sizes, focus visibility, no outside requests, the policy header on every page, every path through the check, and axe-core when `AXE_JS` is set (needs the test tools in `test-tools/requirements.txt` and `test-tools/package.json`) |
| `python3 tools/check_live.py` | The live site matches this repository byte for byte, with every header, the 404 page, and redirects from old `.html` addresses (needs internet) |

GitHub Actions run the checks on every push ([checks.yml](.github/workflows/checks.yml)), confirm after every push to `main` that the live site matches the commit ([live.yml](.github/workflows/live.yml)), and every Monday check links, checkpoints, and the live site, opening an issue if a person is needed ([weekly.yml](.github/workflows/weekly.yml)). When the version number changes, they tag the commit and publish a release once the checks pass ([release.yml](.github/workflows/release.yml)). Cloudflare Pages publishes `site/` from `main` after its own freshness and structure check ([settings](docs/maintenance.md#cloudflare-pages-settings)).

## Report a problem

Open an [issue](https://github.com/radiofreelove/projectstasis/issues). **Issues are public, and so is your GitHub account name.** Do not include names, case numbers, health details, immigration status, or anything else personal. See [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

The words and the code have different licenses, so each can be reused in the way that fits it. Copyright 2026 The Stasis Project.

| What | Files | License |
|---|---|---|
| Words and data | Every file not listed below, including the pages (`src/pages/` and `site/*.html`), `data/`, `docs/`, and this README | [CC BY 4.0](LICENSE) |
| Code | `tools/`, `site/assets/js/`, `site/assets/css/`, and `.github/workflows/` | [MIT](LICENSE-CODE) |
| Reading font | `site/assets/fonts/` (Atkinson Hyperlegible Next, by the Braille Institute) | [SIL Open Font License 1.1](site/assets/fonts/OFL.txt) |
| Logo | `site/assets/img/logo.svg` | Not licensed for reuse |

**To reuse the words,** for example in a clinic handout, a translation, or another state's guide: credit The Stasis Project, link to the site and to the license, and say what you changed (CC BY 4.0, section 3). For example:

> Adapted from The Stasis Project, <https://projectstasis.pages.dev/>, under CC BY 4.0, <https://creativecommons.org/licenses/by/4.0/>. Shortened for our clinic.

**To reuse the code,** keep the copyright and license notice in [LICENSE-CODE](LICENSE-CODE).

**Not covered:** the state's forms, letters, and pages that the site links to, which belong to their publishers, and the logo. Neither license gives trademark rights, and CC BY 4.0 does not let anyone imply that this project endorses their copy (section 2).

Why these licenses: [docs/decisions/0010-license.md](docs/decisions/0010-license.md). Contributions are accepted under the same licenses ([CONTRIBUTING.md](CONTRIBUTING.md)).
