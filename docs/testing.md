# Testing

## Summary for 0.1.0 beta (Nov. 3, 2026)

| Test | Tool | Result |
|---|---|---|
| Build freshness, registered links, logged facts | `tools/build.py --check` | Pass |
| Structure, privacy, and accessibility lint (16 rules, 18 pages and `site/_headers`) | `tools/check_structure.py` | Pass |
| Color contrast (31 pairs, 3 themes) | `tools/check_contrast.py` | Pass; see [contrast.md](contrast.md) |
| Reading level (16 pages) | `tools/check_reading_level.py` | 14 on target (grade 6 or lower); health and immigration pages above target but under the limit; see [reading-level.md](reading-level.md) |
| Dated checkpoints | `tools/check_review_dates.py` | None past due; next on 2026-11-16 |
| Real browser, 5 settings x 18 pages, served like Cloudflare Pages (`tools/serve.py`) | `tools/browser_check.py` | Pass; see [testing-browser.md](testing-browser.md) |
| Every path through the 1-minute check | `tools/browser_check.py` | Pass |
| axe-core | `tools/browser_check.py` with `AXE_JS` | Not run locally (package registry unreachable). Runs in [checks.yml](../.github/workflows/checks.yml). |
| Official link check | `tools/check_links.py` | Not run locally (most outside sites unreachable from the build environment). Runs weekly in [weekly.yml](../.github/workflows/weekly.yml). |
| Live site matches the repository | `tools/check_live.py` | Not run locally (the live site is unreachable from the build environment). Runs after every push to `main` in [live.yml](../.github/workflows/live.yml), weekly in [weekly.yml](../.github/workflows/weekly.yml), and by hand after any change to the Cloudflare settings. |

## What the browser test found and fixed

The first run found sideways scrolling at 320 px with extra-large text and extra spacing on 8 pages. Long web addresses such as `benefits.oregon.gov` could not wrap. Fix: `overflow-wrap: anywhere` on the page, and phone numbers may wrap at their dashes at the largest settings. Second run: no problems.

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
pip install playwright && python3 -m playwright install chromium
npm install --no-save axe-core@4
AXE_JS=node_modules/axe-core/axe.min.js python3 tools/browser_check.py --shots screenshots
python3 tools/check_links.py
python3 tools/check_live.py
```
