# 0016. Use Spacefast as a secondary host

- Status: Accepted
- Date: 2026-11-20

## Context

The site already runs on Cloudflare Pages (`https://projectstasis.pages.dev/`), which remains the primary host. Having an active secondary host gives the project an independent live copy built from the same source.

## Decision

Keep Cloudflare Pages (`https://projectstasis.pages.dev/`) as the primary host, and publish Spacefast as an active secondary host from `main` (and manual workflow runs) via `.github/workflows/deploy-spacefast.yml`.

The workflow builds a Spacefast-themed output, checks contrast, and publishes the prebuilt folder:

1. `python3 tools/build.py --theme spacefast --out site-spacefast`
2. `python3 tools/check_contrast.py --dir site-spacefast`
3. Install `spacefast@0.10.0` and run `sf publish ./site-spacefast --prebuilt`

## Consequences

- Spacefast hosts an independent copy of the site, and each run replaces the published snapshot.
- There are no pull-request previews on Spacefast; pull-request previews remain on Cloudflare Pages.
- Automated live checks (`live.yml` and `weekly.yml`) continue checking Cloudflare Pages as the primary host.
