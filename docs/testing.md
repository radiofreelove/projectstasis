# Testing

## What runs, and where

Results are not kept in this file, so it cannot go out of date. Each run's log is in the repository's Actions tab, the generated reports are linked below, and [CHANGELOG.md](../CHANGELOG.md) says what changed in each release.

| Check | Tool | When it runs |
|---|---|---|
| Built pages match their sources; every link registered; every fact logged; font files match their checksums | `tools/build.py --check` | Every push, in GitHub Actions and in the Cloudflare build |
| Structure, privacy, and accessibility lint, including the security headers in `site/_headers` | `tools/check_structure.py` | Every push, in GitHub Actions and in the Cloudflare build |
| Color contrast (7:1 text) | `tools/check_contrast.py` | Every push. Report: [contrast.md](contrast.md) |
| Reading level (target grade 6, fails above 8) | `tools/check_reading_level.py` | Every push. Report: [reading-level.md](reading-level.md) |
| Dated checkpoints and expired notes | `tools/check_review_dates.py` | Every push (reported only); Mondays and Jan. 1 (opens an issue) |
| Real browser on a server that behaves like Cloudflare Pages: every page in each display setting, every path through both checks, no outside requests, nothing left in storage, and axe-core | `tools/browser_check.py` | Every push. Report: [testing-browser.md](testing-browser.md) |
| Official links | `tools/check_links.py` | Mondays |
| Live site matches the repository, headers included | `tools/check_live.py` | After every push to `main`, and Mondays |

The browser checks use two test-only tools, pinned to the same versions as The Strand Project: Playwright ([test-tools/requirements.txt](../test-tools/requirements.txt)) and axe-core ([test-tools/package.json](../test-tools/package.json)). Dependabot proposes updates to them and to the GitHub Actions each month ([.github/dependabot.yml](../.github/dependabot.yml)). The site build itself uses only the Python standard library. The test tools sit in `test-tools/`, not the repository root, because Cloudflare Pages installs any `package.json` it finds at the root on every deploy ([Cloudflare docs: Build image](https://developers.cloudflare.com/pages/configuration/build-image/), updated Oct. 26, 2026).

## What the browser test found and fixed

The first run (0.1.0 beta, Nov. 3, 2026) found sideways scrolling at 320 px with extra-large text and extra spacing on 8 pages. Long web addresses such as `benefits.oregon.gov` could not wrap. Fix: `overflow-wrap: anywhere` on the page, and phone numbers may wrap at their dashes at the largest settings. Second run: no problems.

## Not tested yet

- Screen readers (NVDA, JAWS, VoiceOver on iPhone and Mac, TalkBack).
- Voice control, switch access, and screen magnifiers.
- Real applicants, including neurodivergent people, people with low literacy, and people reading in a second language.
- Older phones and slow connections. The pages are small: the home page is about 13 KB of HTML, plus 16 KB of styles, 5 KB of script on most pages (18 KB on the check page), and a 1 KB logo, all before compression. No photos. The optional reading font adds about 25 KB, and only for readers who choose it.

These are the next priority. See [roadmap.md](roadmap.md).

## How to run everything

```bash
python3 tools/build.py --check
python3 tools/check_structure.py
python3 tools/check_contrast.py --check
python3 tools/check_reading_level.py --check
python3 tools/check_review_dates.py
pip install -r test-tools/requirements.txt && python3 -m playwright install chromium
npm install --prefix test-tools --no-package-lock
AXE_JS=test-tools/node_modules/axe-core/axe.min.js python3 tools/browser_check.py --shots screenshots
python3 tools/check_links.py
python3 tools/check_live.py
```
