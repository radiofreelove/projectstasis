# 0013. A Utah guide inside the same site

- Status: Proposed (built on a branch on 2026-11-10; becomes Accepted when the maintainer merges it)
- Date: 2026-11-10

## Context

The federal law that created Oregon's work or activity rules applies to every state that expanded Medicaid. Utah starts the same rules on Jan. 1, 2027, for adults in Adult Expansion Medicaid and Targeted Adult Medicaid, and explains them across at least 18 pages and papers (registry IDs that start with U). The maintainer asked for a Utah section that follows the same design and explainer principles as the OHP guide.

Utah is not Oregon with different phone numbers. Different agencies decide (the Department of Workforce Services), the state uses different words ("community engagement requirement," "exclusions and exceptions"), the deadlines differ, and Utah was not a party to the court case that Oregon joined.

## Decision

- **One site, two guides.** Utah pages live in the same repository and are built by the same script, so every rule in [methodology.md](../methodology.md) and [style-guide.md](../style-guide.md) applies to them: every fact is in the ledger, every link is in the registry, every page lists its sources.
- **Flat addresses.** Utah pages are `utah`, `utah-rules`, `utah-apply`, and so on, next to the Oregon pages. No folder. Every existing Oregon address stays the same, and every check tool keeps working without learning about folders.
- **Sections in the build.** A page says `section: utah` in its metadata. The section sets the tagline ("Utah Medicaid, made plain"), the menu, the footer text that names the state and its agencies, and the "facts last checked" date. Pages both guides need (About, Privacy, Accessibility, Every source) say `shared: yes`.
- **Separate facts.** Utah claims have IDs that start with `U-`, and Utah sources have IDs that start with `U`. A Utah page never borrows an Oregon fact. The only claims both guides share are promises about the site itself and two general tips.
- **Same order of authority.** Federal statute, federal rule, court orders, state rules, then state agency guidance, newest and most specific first. Where Utah's pages disagree, the disagreement is in [corrections.md](../corrections.md).
- **Applicants first**, as in [0006](0006-applicants-first.md). The Utah guide says one line about current members and leaves renewals for later.
- **Same look.** The Utah guide uses the site's existing design, including the ODHS-published palette ([0004](0004-odhs-palette-not-identity.md)). The palette is the site's own design system now, not a claim about any state. The banner and footer of every Utah page say the guide is independent and name the State of Utah, DHHS, and DWS.
- **No Utah check yet.** The 1-minute check is not copied for Utah in this release. A check that sorts people into "may apply" and "may not apply" needs Utah's own screener and form 742 to be public first, and it needs the same public logic note and browser tests as the Oregon check ([0008](0008-check-never-decides.md)). The Utah rules and reasons pages carry the same information.
- **Each source shows its own checked date.** With two guides checked on different days, one site-wide "we checked these on" line would be wrong for one of them. Each page now shows, for every source, the date printed on it and the date it was last checked.

## Options considered

| Option | Why it was not chosen |
|---|---|
| A second site and repository for Utah | Two copies of the build, the checks, and the privacy promises to keep in step, for one maintainer. |
| A `/utah/` folder | Shorter page names, but every tool that walks `site/*.html`, the 404 page, and the asset paths would need folder support. Flat names carry no such risk. |
| Turning the home page into a state chooser | It would change the address and purpose of the page Oregon readers already use. Each home page links to the other guide instead. |
| A new color palette for Utah | Two palettes to hold at 7:1 contrast, and a visual split inside one site. |

## Consequences

- The site's name and tagline no longer describe everything it covers. The Oregon pages still say "OHP, made plain"; the Utah pages say "Utah Medicaid, made plain."
- The shared pages (About, Privacy, Accessibility, Every source) show the Oregon menu. A Utah reader who opens one returns through the "Utah Medicaid guide" link in its footer or on the About page.
- More to maintain: 12 more pages, 111 more claims, 40 more registry entries, and Utah checkpoints in [review.json](../../data/review.json).
- The Utah research was done in one day through a tool that answers questions about a document instead of returning its text ([research-log.md](../research-log.md)). A person has not yet read the Utah documents end to end. Checkpoint 2026-11-24 exists for that, and the guide should not be promoted to Utah readers before it is done.
- This is a difference from The Strand Project ([0012](0012-shared-with-strand.md)): Strand has one guide, so it has no sections and keeps its single checked date.
