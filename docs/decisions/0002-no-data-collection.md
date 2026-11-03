# 0002. Collect nothing, and let the browser enforce it

- Status: Accepted
- Date: 2026-11-02

## Context

The people who use this site may be worried about immigration status, health privacy, or being judged. The questions in the 1-minute check touch on pregnancy, disability, substance use treatment, incarceration, and tribal status.

## Decision

- No accounts, forms that submit, cookies, analytics, ads, or third-party resources.
- The check keeps answers in page memory only.
- Every page has a Content Security Policy with `connect-src 'none'` and `form-action 'none'`, sent as a header by the host and repeated in the page, so the browser blocks network requests even if a script tried.
- Only display settings are stored, in one localStorage key, and they are not sensitive.

## Consequences

- No usage numbers. Success has to be measured another way, such as feedback from community partners.
- Cloudflare, the host, still processes visitors' IP addresses; the privacy page says so ([0011](0011-cloudflare-pages.md)).
