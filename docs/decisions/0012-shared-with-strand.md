# 0012. Shared conventions with The Strand Project

- Status: Accepted
- Date: 2026-11-03

## Context

The Stasis Project and The Strand Project are sibling guides by the same maintainer, built the same way: claims-driven builds, the ODHS palette, Cloudflare Pages, and strict privacy headers. A review on Nov. 3, 2026 found places where the two differed without a stated reason (license file names, fonts, link colors, where the "Report a mistake" link sits). The maintainer asked that the two stay consistent in technical and design choices where practical, including the ODHS palette. The same record is kept in Strand as [ADR-0010](https://github.com/radiofreelove/projectstrand/blob/main/docs/decisions/ADR-0010-shared-with-stasis.md).

## Decision

Both projects follow these conventions. A change to one should be made in both, or recorded here as a difference.

| Area | Shared convention |
|---|---|
| Colors | The ODHS Brand Guidelines palette (form DE2022), as palette only: never ODHS names, logos, brandmarks, or typography rules ([0004](0004-odhs-palette-not-identity.md)). Text holds 7:1 contrast. |
| Independence | Every page says "Independent guide" in a banner near the top, and again in the footer. |
| Fonts | System fonts by default, `system-ui` first. Readers can choose Atkinson Hyperlegible Next (setting value `hyper`), served from the site itself. Same package, version (5.3.0), files, and SHA-256 values in each project's `fonts.lock.json`. |
| Links | One link color, visited or not. |
| Mistakes | "Report a mistake" in that banner opens the About page section `#report`. That section says reports and GitHub account names are public, then links to GitHub issues. GitHub issues are the only reporting route: the maintainer chose not to add a form (Nov. 3, 2026), which keeps both sites free of server code. |
| Saved settings | Display or reading settings are saved on the device automatically when the reader changes one. A reset or "Forget everything" control erases them. Strand's checklist checkmarks are still saved only if the reader turns on "Remember my checklist." |
| Licenses | `LICENSE` holds CC BY 4.0 (the words, which are most of each project). `LICENSE-CODE` holds MIT. The footer names both, and the About page section `#license` explains reuse. |
| Privacy headers | Content Security Policy with `connect-src 'none'`, `form-action 'none'`, and `font-src 'self'`; `Referrer-Policy: no-referrer`. |
| Interactive tools | Each tool has a public note in plain words that lists every question and every rule: [checker-logic.md](../checker-logic.md) here, [PATH-LOGIC.md](https://github.com/radiofreelove/projectstrand/blob/main/docs/PATH-LOGIC.md) in Strand. |
| Hosting | Code on GitHub, site on Cloudflare Pages' free tier. |

Differences kept on purpose:

| Stasis | Strand | Why |
|---|---|---|
| Commits the built site, including the font files | Builds on Cloudflare and downloads the font at build time | Each project's build model. Both pin the same checksums. |
| No "Leave quickly" button | "Leave quickly" on every page | Strand's readers may need to hide what they are reading from people in their household. |

Each site's dark theme keeps its own background, by the maintainer's choice of Nov. 3, 2026: black for Stasis and deep indigo for Strand. Both names nod to Destiny 2 powers. Stasis's color there is icy blue, so its dark theme shows glacial blue headings and links on black. Strand's color there is green, which lives in Strand's mark; its indigo comes from the ODHS palette. Both themes hold text at 7:1, and neither uses color alone to carry meaning: colored boxes have headings, and the current page is marked by shape, not only color.

## Consequences

- Readers who use both sites find the same font option, link behavior, and reporting route.
- A reviewer can compare the two projects line by line using this table.
- The font adds about 25 KB, downloaded only by readers who choose it.
