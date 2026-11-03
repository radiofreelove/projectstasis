# Security

## Reporting a problem

If you find a security or privacy problem (for example, a way the site could leak what someone types), please use GitHub's private vulnerability reporting for this repository if it is turned on. If it is not, open an issue that says only "Security contact needed," with no details, and the maintainer will reply.

## What protects visitors

- No server code, accounts, or stored visitor data.
- A Content Security Policy on every page that blocks network requests, form submission, inline scripts, anything loaded from other sites, and framing by other sites. Cloudflare Pages sends it as a header from `site/_headers`, and each page repeats it in a meta tag. See [docs/privacy.md](docs/privacy.md).
- `tools/check_structure.py` fails the build if a page or `site/_headers` loses the policy, or a page adds inline scripts or styles or event-handler attributes.
- `tools/check_live.py` checks after every push to `main` and every Monday that the live site matches this repository byte for byte, with every header, so a change made outside the repository shows up.

## Workflow hardening

- Each workflow asks for the fewest permissions it needs (`contents: read` by default; `issues: write` only for the weekly report).
- Actions are pinned to major versions from GitHub (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/setup-node@v4`, `actions/upload-artifact@v4`). Pinning to full commit hashes is on the roadmap.
- No secrets are stored in the repository. The weekly job uses the built-in `GITHUB_TOKEN` only to open issues.

## Hosting access

- Cloudflare Pages builds the site through Cloudflare's GitHub app, Cloudflare Workers and Pages, which reads this repository. No Cloudflare keys are stored here.
- The site has no server code. Pages Functions (a `functions/` folder or `_worker.js`) must not be added; see [docs/maintenance.md](docs/maintenance.md#never-turn-these-on).
