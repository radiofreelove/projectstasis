# Roadmap

The goal: help as many applicants as possible keep or get coverage through the 2027 and 2028 changes. Ordered by impact.

## Before calling it 1.0

1. **Expert review.** A benefits attorney or advocate reads every claim in [claims.md](claims.md). Disability Rights Oregon and the Public Benefits Hotline are natural reviewers.
2. **Usability testing with applicants.** Paid sessions with people who use screen readers, voice control, and magnification; neurodivergent people; people with low literacy; and people reading in a second language. Fix what they find before anything else.
3. **Send the corrections log to OHA** ([corrections.md](corrections.md)), and record the reply.
4. ~~**Show the license on the site.**~~ Done in 0.1.1: a footer line on every page and a "Reuse this guide" section on the About page.

## The Utah guide

Added in 0.2.0 ([decisions/0013-utah-section.md](decisions/0013-utah-section.md)). Before telling Utah readers about it:

- **A person reads every Utah page against its sources** (checkpoint 2026-11-24). The research was done through a tool that returns answers, not full text ([research-log.md](research-log.md)).
- **Review by someone who works with Utah Medicaid applicants.** Utah Legal Services and Take Care Utah are natural reviewers.
- **Send the Utah part of the corrections log to Utah Medicaid** ([corrections.md](corrections.md#utah)), and record the reply.

Then:

- **A Utah check**, once Utah posts form 742 and its medically frail screener, with its own public logic note and browser tests.
- **Utah renewals**, before current members reach reviews for renewals due in March 2027.
- **Utah forms in Spanish**, checked by a Spanish reader: the guide links to 2 Spanish forms it has not opened.

## Next pages

5. **Gig and self-employed workers**, using OHA's gig workers guide (registry K04).
6. **People without stable housing**, using OHA's houseless guide (K06): how to get mail, how to keep contact information current.
7. **Renewals** for people who become members, before six-month renewals start in late 2027.
8. **2028 proof checklist**, when OHA publishes what it will accept.
9. **More letter types**, as OHA posts sample notices.

## Reach

10. **Translations reviewed by people from each community**, starting with languages chosen with community partners from the 16 non-English languages OHA already supports. No machine translation ([decisions/0007-no-machine-translation.md](decisions/0007-no-machine-translation.md)).
11. **One-page handouts** for clinics, libraries, food banks, and shelters, each with a short web address.
12. **A partner kit** for community partners and clinic front desks: the same plain facts, formatted for a conversation.
13. **A "what changed" page** generated from the changelog, for helpers who need to keep up.
14. **A way to pick a state** that does not depend on the footer: the shared pages (About, Privacy, Accessibility, Every source) show the Oregon menu to Utah readers too.

## Engineering

15. Pin GitHub Actions to commit hashes ([SECURITY.md](../SECURITY.md)).
16. An installable, offline version, only with a design that cannot show stale rules after a checkpoint passes.
17. A text-only version for very slow connections.
18. Open the federal statute (Public Law 119-21) and cite it directly, so federal requirements no longer rest on the rule alone ([methodology.md](methodology.md), section 2).
