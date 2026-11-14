# 0015. The front door with three guides: Oregon stays at `/`

- Status: Proposed (it becomes Accepted when the maintainer approves the merge of the Washington guide)
- Date: 2026-11-12

## Context

[adding-a-guide.md](../adding-a-guide.md) says the first step for a third guide is to decide the front door: what should `/` be? [roadmap.md](../roadmap.md) ("A front door for every state") left the question open, and [0014](0014-guide-list.md) said it would come due when Washington arrived.

A Washington guide, for Apple Health, is now built. Three things were on the table:

- Today `/` is the Oregon home page. Oregon readers, and every link to the site made since 0.1.0, land there.
- Each guide's home page starts with the state switch, "Pick your state", above the headline. It already shows every guide in the list.
- On a phone, three states do not fit on one row. The third wraps to a second row.

## Decision

- **Oregon stays primary, and `/` stays the Oregon home page.** No address changes. The Oregon guide came first, has been checked the longest, and is the one existing links point to.
- **The state switch is the front door for the other guides.** It stays the first thing under the menu on every guide's home page, so a reader in the wrong guide sees it before the headline.
- **The order is Oregon, Washington, Utah,** everywhere the switch or a list of states appears: the switch, the footers, the "page not found" page, and the "Three guides" part of each About page. The order comes from `SECTIONS` in `tools/build.py`, so the Washington entry sits between Oregon's and Utah's. It is still before the `both` entry, as [adding-a-guide.md](../adding-a-guide.md) asks.
- **The wrap on a phone is accepted.** At 320 px the switch shows one state per row, each a full-width button, in the same order. At widths where two fit side by side, the third starts a second row, the same size as the other two and lined up under the first. On a wide screen all three share one row. Nothing scrolls sideways. `tools/browser_check.py` checks that on every push, and saves the 320 px screenshots when run with `--shots`.
- **Washington's addresses follow the Utah pattern:** `washington`, `washington-check`, `washington-apply`, and so on. Flat, with the guide's name as the prefix.

## Options considered

| Option | Why it was not chosen |
|---|---|
| Make `/` a page that only asks "Which state?" | It would change the purpose of the address Oregon readers already use, and add a step for every reader. [0013](0013-utah-section.md) turned this down for two guides; a third does not change the reasoning. |
| Move Oregon to `/oregon` and redirect `/` | Every existing link would cost a redirect, and Cloudflare Pages redirects would be a new moving part ([0011](0011-cloudflare-pages.md)). |
| Order the switch by the date each guide was added (Oregon, Utah, Washington) | The maintainer asked for Oregon, Washington, Utah. |
| A one-row switch on phones (smaller buttons, or a menu) | Smaller targets, or a control that hides the choices. Three full-width rows keep the 48 px targets and the plain words. |

## Consequences

- A reader who lands on `/` from Washington or Utah still has to see and use the switch. That is the cost of keeping Oregon's address.
- The Washington guide sits second in the list although it is the newest. Its About page and its "Every source" page say in plain words which of its sources have not yet been read in full. The guide merged on Nov. 12, 2026 on the owner's direction, ahead of the source review checkpointed for Nov. 26, 2026; the pre-merge source read ([adding-a-guide.md](../adding-a-guide.md), "Before you write a page", step 2).
- If a fourth guide arrives, or the site gets its own address, this decision should be looked at again. A list of four on a phone is a long way to the headline.
