# 0014. One list of guides, and a state field on every source and fact

- Status: Accepted (the maintainer approved the merge on 2026-11-11)
- Date: 2026-11-11

## Context

[0013](0013-utah-section.md) added a second guide. It was built as "Oregon, plus Utah": Oregon was the default, and Utah was the exception. That showed in the code.

- The build decided a source or a fact was Utah's by its ID (`U01`, `U-START`). Everything else counted as Oregon's.
- Each guide's settings named exactly one "other guide."
- The state switch on each home page, and the state lists on the "page not found" page, were written by hand.
- The build had Utah-named settings (`{{UTAH_DOC_COUNT}}`, a pattern that knew only `oregon` and `utah` blocks), and the browser tests named the Oregon and Utah pair in their code, including the rule that "OHP" never shows in a Utah result.
- All 31 page sources sat in one folder, told apart by a `utah-` file name and a `section: utah` line.

On 2026-11-11 the maintainer said a Washington guide is planned and asked for this groundwork before it starts. A third guide would have turned each of those into guesswork or a third special case.

## Decision

- **One list.** `SECTIONS` in `tools/build.py` is the only place the guides are named. The build, the state switch, the footers, the "page not found" page, and the browser tests all read it. Its order is the order readers see.
- **A `guide` field on every source and every fact.** `oregon`, `utah`, or `all`. `all` is for what any guide may use: federal rules, court papers, standards, national groups, the host, and what the site promises about itself. The build goes by the field and never by the ID. The ID letters stay, as a habit that keeps IDs easy to read.
- **One more rule.** A fact may rely only on its own guide's sources or on shared ones. The build stops otherwise.
- **The same source kinds for every state.** Utah's `utah-explainer`, `utah-form`, and `utah-page` became `state-explainer`, `state-form`, and `state-page`. The `guide` field says whose they are.
- **Folders for page sources.** `src/pages/oregon/`, `src/pages/utah/`, and `src/pages/shared/`. The folder decides the guide. File names still match the built page (`utah/utah-check.html` builds `utah-check`), so a link in a page source reads the same as before.
- **Built, not written by hand:** the state switch (`{{GUIDE_SWITCH}}`), each guide's count of state documents (`{{DOC_COUNT}}`), the footer links to every other guide, and the "page not found" page's state lists, which come from one `_not-found.html` part in each guide's folder. The build stops if a guide's home page has no switch.
- **No public address changes.** Every page keeps its address. Before the version number changed, the rebuilt site matched the published one byte for byte.
- **A test with three guides.** `tools/tests/test_build.py` adds a made-up third guide to a copy of the sources and builds it, so "nothing assumes two states" is checked on every push and not only claimed.

Steps for adding a state: [adding-a-guide.md](../adding-a-guide.md).

## Options considered

| Option | Why it was not chosen |
|---|---|
| Add Washington as a third special case (`W` IDs, a third pattern) | Each new state would touch the build's rules again, and the rule "everything that is not Utah's is Oregon's" would be wrong the day a third state arrived. |
| Move the guide list out of `tools/build.py` into a data file | The list holds menus and sentences next to the code that uses them, and one Python file can be read top to bottom. Other tools import it, so there is still one list. |
| Rename Utah's files to drop the `utah-` prefix inside its folder | A page source would then link to `utah-check.html` while the file was named `check.html`. Matching names are easier to search. |
| Move the built pages into folders too (`/utah/check`) | It would change every Utah address one day after they were published, and the tools that walk `site/*.html` would need folder support. Still open for the front-door decision. |
| Keep ownership in the ID and only add a `W` prefix | The ID cannot say "all." Shared sources looked like Oregon's, and two Oregon groups (S25, S38) were open to the Utah guide by accident. |

## Consequences

- Adding a state is now a list entry, a folder of pages, and registry and ledger entries marked with its name. It is still weeks of reading and writing; only the plumbing got shorter.
- Not decided here: what `/` should be when there are three guides ([roadmap.md](../roadmap.md), "A front door"). The state switch already shows three states, but on a phone the third wraps to a second row. The frame for pages that belong to no guide (`both` in the list) still has hand-written words that name Oregon and Utah, and a person rewrites them when a guide is added.
- A shared page (About, Privacy, Accessibility, Every source) needs a `<guide>_sources` line and a `<!-- guide -->` block for each new guide. The build says so if they are missing.
- The registry and the ledger grew by one field on each entry. `docs/sources.md` and `docs/claims.md` show it in a new Guide column.
- This is a further difference from The Strand Project ([0012](0012-shared-with-strand.md)), which has one guide and none of this.
