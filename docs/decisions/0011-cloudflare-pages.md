# 0011. Host on Cloudflare Pages

- Status: Accepted
- Date: 2026-11-03

## Context

The site is plain files with no server code, so almost any static host works. Two things decide between them:

- **HTTP headers.** A Content Security Policy in a meta tag cannot set `frame-ancestors`, so without a real header, other sites can show these pages inside their own. GitHub Pages cannot send custom headers. In GitHub's community forum, a reply written for GitHub said in May 2023 that "a meta tag unfortunately is the only way," and in July 2024 that the feature "is not an area that is being prioritized at the moment." Users were still asking for it in September 2026 ([discussion #54257](https://github.com/orgs/community/discussions/54257), user reports).
- **An address of its own.** Browsers give each address one shared storage area. A site published under another site's address would share that storage. Each Cloudflare Pages project gets its own address.

## Decision

- Host `site/` on Cloudflare Pages, free plan, as the project `projectstasis`, at <https://projectstasis.pages.dev/>.
- Connect the repository through Cloudflare's GitHub app, Cloudflare Workers and Pages. For every push, Cloudflare runs `python3 tools/build.py --check && python3 tools/check_structure.py`, then publishes `site/`: `main` to the live address, other branches and pull requests to preview addresses. The exact dashboard settings are in [maintenance.md](../maintenance.md#cloudflare-pages-settings).
- Send security headers from `site/_headers`, which the build writes from the same policy as each page's meta tag, plus `frame-ancestors 'none'`. Details are in [privacy.md](../privacy.md).
- Link pages by the addresses Pages serves (`check`, not `check.html`). Pages redirects `.html` addresses to the shorter ones ([Cloudflare docs: Serving Pages](https://developers.cloudflare.com/pages/configuration/serving-pages/), updated Oct. 10, 2026), so `.html` links would cost every click a redirect.
- Test against a local server that behaves like Pages (`tools/serve.py`), and check the live site after every push to `main` and every week (`tools/check_live.py`).

## Options considered

| Option | Why it was not chosen |
|---|---|
| GitHub Pages | No custom headers, and only one site per account gets an address of its own. |
| Cloudflare Workers with static assets | Cloudflare's Pages docs now say "Start new projects with Workers" (updated Aug. 25, 2026). But a Workers address on Cloudflare's free domain includes the account's own subdomain, while Pages gives the shorter `projectstasis.pages.dev`. Pages is still offered on all plans, and Cloudflare publishes a guide for moving to Workers later. |
| Deploying from GitHub Actions with a Cloudflare API token | Keeps deploy logs public, but needs a Cloudflare secret stored in the repository settings. The Git integration needs no secret, and `tools/check_live.py` shows publicly that the live site matches the repository. |

## Consequences

- Cloudflare processes visitors' IP addresses and traffic data. The privacy page says so (claim C-PRIV-HOST, registry S34).
- Some Cloudflare dashboard switches would break the site's promises, for example Web Analytics, which adds a script to every page on the next deploy. [maintenance.md](../maintenance.md#never-turn-these-on) lists them, and `tools/check_live.py` catches any change to what visitors receive.
- Cloudflare's build logs are visible only in the maintainer's Cloudflare account. GitHub shows each build's result as a check on the commit, and the public live-site check shows whether the published site matches it.
- Preview addresses are public by default, though search engines are told not to index them.
- Pages adds `Access-Control-Allow-Origin: *` to every response. It is left as is because the pages hold nothing private.
- If Cloudflare ever retires Pages, the site moves to Workers or another host, and the address changes unless a custom domain is added first.
