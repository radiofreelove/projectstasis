# Boundaries

What this project will and will not do, and why.

## Not the state

- The site says "Independent guide. Not run by the state." at the top of every page. Every Oregon footer names the State of Oregon, OHA, and ODHS. Every Utah footer names the State of Utah, DHHS, and DWS.
- It uses the ODHS color palette, but not the ODHS logo, brandmark, seal, name, or typeface as its brand ([decisions/0004-odhs-palette-not-identity.md](decisions/0004-odhs-palette-not-identity.md)).
- It never collects applications, logins, signatures, or payments, and never imitates a state form or notice. The hours logs are labeled "This is not an OHP form" and "This is not a Utah Medicaid form."

## Information, not advice

- The site explains published rules and points to official sources. It does not tell any person what their outcome will be.
- Every result of the 1-minute check says "Only OHP decides. This check is not a decision."
- For individual help, it points to free legal help (the Public Benefits Hotline in Oregon, Utah Legal Services in Utah), Disability Rights Oregon, OHA's free community partners, and Take Care Utah.
- It names outside helpers only for their own services, and only helpers that a state source names or whose own site was read.
- No qualified legal review has been completed for this release.

## Privacy

- No data collection of any kind ([privacy.md](privacy.md)).
- No questions about immigration or citizenship status, enforced by `tools/check_structure.py`.
- Problem reports are public, and every report link warns people not to share personal details.

## Maintainers

- Use only public sources. Never use non-public information from any job, agency, or client. This holds for every state the site covers.
- Never post anyone's case details anywhere in the project.
- Disclose AI assistance in [methodology.md](methodology.md) and in commit trailers.
