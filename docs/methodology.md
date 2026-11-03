# Methodology

How facts get onto the site, how they are worded, and how they stay current.

## 1. Who the site is for

People applying for OHP, including people applying again after being turned down. Renewal guidance for current members is out of scope for this release (see [decisions/0006-applicants-first.md](decisions/0006-applicants-first.md)).

## 2. Where facts may come from

Every factual statement must trace to a source in [`data/sources.json`](../data/sources.json) that was **opened and read** on the date in its `checked` field. Addresses that came from another official source but were not opened are allowed as **links only**; they never support a claim.

When sources disagree, the site follows this order and discloses the disagreement in [corrections.md](corrections.md):

1. Federal statute.
2. Federal rule (here, the interim final rule at 91 Fed. Reg. 33348, registry S27).
3. Court orders about that rule (registry S28 and S29).
4. Oregon statutes and Oregon Administrative Rules. None implementing the work or activity rules were found on Nov. 2, 2026; see [research-log.md](research-log.md).
5. OHA and ODHS guidance: web pages, fact sheets, notices, and presentations. Newer and more specific beats older and more general.
6. Other organizations (legal aid, advocacy groups), only for their own services and phone numbers.

The federal statute itself (Public Law 119-21, sections 71119 and others) was not opened for this release. Statements about federal requirements rest on the federal rule (S27), which quotes and implements the statute. That is a gap to close in a future review.

## 3. Kinds of claims

Every statement in [`data/claims.json`](../data/claims.json) has a kind:

| Kind | Meaning | Needs a source? |
|---|---|---|
| fact | Stated in the listed source | Yes |
| math | Arithmetic on a sourced number, shown in the note | Yes |
| inference | Our careful reading of sources; worded with "may" on the page | Yes, plus a note explaining the reasoning |
| design | A promise about this site, checked in code or tests | No |
| tip | General good practice, not a rule | No |

## 4. How the build enforces it

- Pages mark factual text with `data-claim="ID"`.
- [`tools/build.py`](../tools/build.py) stops if a page uses a claim ID that is not in the ledger, if a claim's sources are not listed on that page, if a page links to an address not in the registry, or if a ledger claim is used nowhere.
- The build writes [claims.md](claims.md) and [sources.md](sources.md) so anyone can read the ledger without opening JSON.

## 5. Wording rules

Full rules are in [style-guide.md](style-guide.md). The ones that protect accuracy:

- Only OHP decides. The site never says "you are exempt," "you qualify," or "you will be approved." It says "you may."
- Plain word first, OHP's word second, so people recognize the word on their letters ("a reason you do not have to meet the rules; OHP calls this an exemption").
- Every date includes the year. Time-limited notes carry a `data-show-until` date and a checkpoint in [`data/review.json`](../data/review.json).
- Numbers that change often (income limits, office hours) are linked, not copied.

## 6. Link out, do not copy

The site links to the state's own forms and pages instead of re-hosting them. That keeps forms current without anyone updating this repository. The trade-off: if the state moves a page, the link breaks. The weekly link check catches that (see [maintenance.md](maintenance.md)).

## 7. Review

- **Automated, weekly:** links, dated checkpoints, and whether the live site still matches this repository ([`.github/workflows/weekly.yml`](../.github/workflows/weekly.yml)). Failures open a GitHub issue.
- **By a person, at least every 30 days and at each checkpoint:** re-read the sources behind every claim whose topic changed, plus the OHP.Oregon.gov pages that block automated tools.
- **Before calling this release "1.0":** review by a benefits attorney or advocate, and usability testing with applicants, including people who use assistive technology and neurodivergent people. See [roadmap.md](roadmap.md).

## 8. AI assistance

Research, drafting, and code for release 0.1.0 were produced with an AI assistant (Claude, by Anthropic) working under the maintainer's direction on Nov. 2, 2026. Every source marked "read by us" was fetched and read in that session; quotes in [corrections.md](corrections.md) come from those reads. A person should still verify claims against sources before relying on them for anyone's case.
