# Privacy notes

## What the site collects

Nothing. There are no accounts, forms that submit, cookies, analytics, ads, embedded videos, maps, fonts, or scripts from other companies.

## Data flows, end to end

| Data | Where it lives | Leaves the device? |
|---|---|---|
| Answers in the 1-minute check | In page memory only, cleared by "Start over" or by leaving the page | No. Never written to storage. Blocked from sending by the CSP. |
| Display settings (text size, spacing, colors, how much to show) | One localStorage key, `stasis-display-v1`, in this browser | No. "Reset to standard" removes it. |
| Page requests | Cloudflare Pages servers | Yes, as with any website. [Cloudflare's privacy policy](https://www.cloudflare.com/privacypolicy/) (effective Nov. 4, 2025, registry S34) says it processes the IP addresses and traffic data of people who visit its customers' sites, as a processor for those customers, and it gives no fixed retention period. This project cannot see or change that. |
| Clicks on links to state websites | Your browser goes to the state site | The state site sees your visit. Because of `Referrer-Policy: no-referrer`, it does not see which of our pages sent you. |
| Problem reports | GitHub Issues | Yes, and they are **public**. Templates warn people not to include personal details. |

## How it is enforced

Cloudflare Pages sends these headers with every response. They come from [`site/_headers`](../site/_headers), which `tools/build.py` writes, so they cannot drift from the pages:

```text
Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self';
  connect-src 'none'; form-action 'none'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'
Referrer-Policy: no-referrer
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()
Cross-Origin-Opener-Policy: same-origin
```

Every page also repeats the same policy in a meta tag (without `frame-ancestors`, which works only as a header), so the protection travels with the page if it is ever served from somewhere else.

- `connect-src 'none'`: scripts cannot make network requests (fetch, XHR, beacons, WebSockets).
- `form-action 'none'`: forms cannot submit anywhere.
- `default-src 'none'` with `'self'` for scripts, styles, and images: nothing loads from other sites, and inline scripts and styles are blocked.
- `frame-ancestors 'none'` and `X-Frame-Options: DENY`: other sites cannot show these pages inside their own.
- `Referrer-Policy: no-referrer`: replaces Cloudflare's default (`strict-origin-when-cross-origin`), so state sites do not learn which of our pages sent a visitor.
- `Permissions-Policy`: the pages cannot use the camera, microphone, location, payments, or USB devices.

Cloudflare Pages also adds `Access-Control-Allow-Origin: *` to every response ([Cloudflare docs: Serving Pages](https://developers.cloudflare.com/pages/configuration/serving-pages/), updated Oct. 10, 2026). That lets other websites read these public pages through a visitor's browser. The pages hold nothing private, so it is left as is.

## What the checks prove, and what they cannot

- `tools/check_structure.py` fails if any page loses the meta policy, or if `site/_headers` stops sending the full policy with `frame-ancestors 'none'` and `Referrer-Policy: no-referrer`.
- `tools/browser_check.py` serves the site the way Cloudflare Pages does (`tools/serve.py`, headers included) and fails if any request leaves the site, any policy violation occurs, a page arrives without the policy header, or the check leaves anything in storage.
- Both of those test the files in this repository. `tools/check_live.py` tests what Cloudflare actually serves: every file must match the repository byte for byte, with every header present. It runs after every push to `main` ([live.yml](../.github/workflows/live.yml)) and every Monday ([weekly.yml](../.github/workflows/weekly.yml)), which opens an issue if anything differs. This is what would catch a dashboard setting that changes the pages, such as Cloudflare Web Analytics, which adds a script to every page on the next deploy ([Cloudflare docs: Web Analytics](https://developers.cloudflare.com/pages/how-to/web-analytics/), updated Apr. 21, 2026).

## Preview addresses

Cloudflare Pages publishes a preview at its own address for every branch and pull request. Previews are public by default, carry `X-Robots-Tag: noindex` so search engines leave them out, and can be limited to the maintainer's Cloudflare account ([Cloudflare docs: Preview deployments](https://developers.cloudflare.com/pages/configuration/preview-deployments/), updated Oct. 12, 2026). Previews get the same headers as the live site.

## How anyone can verify it

1. Open any page, then your browser's developer tools.
2. Network tab: only files from this site load. Select the page itself to see the response headers listed above.
3. Application or Storage tab: at most one key, `stasis-display-v1`, and only after changing display settings.
4. View the page source: the meta policy is near the top.
5. From a terminal: `curl -I https://projectstasis.pages.dev/` prints the headers.

## Things this site does not ask

Immigration or citizenship status, names, birth dates, addresses, case numbers, income amounts, or diagnoses.
