# Adding a guide for another state

This is the plumbing. The real work is the reading: every rule in [methodology.md](methodology.md) applies to a new state from its first sentence. Why it works this way: [decisions/0014-guide-list.md](decisions/0014-guide-list.md).

The examples use Washington. The build stops with a plain message if a step is missed, so you can run `python3 tools/build.py` after each one.

## Before you write a page

1. **Decide the front door.** With a third guide, the question in [roadmap.md](roadmap.md) ("A front door") comes due: what should `/` be? Record the answer as a decision in [decisions/](decisions/).
2. **Read the state's sources yourself.** The Utah guide went live before a person had read its sources end to end ([decisions/0013-utah-section.md](decisions/0013-utah-section.md)). For the next guide, finish that read before the guide is merged.
3. **Learn the state's own words.** A new state has its own program names, agencies, deadlines, and ways to apply. Nothing carries over from another state without a source from the new one.

## The steps

1. **Add the guide to the list.** In `tools/build.py`, add an entry to `SECTIONS` before the `both` entry. Copy Utah's and change every value: the state's name, tagline, menu, footer words, the words for the state switch, the headings for its "Every source" page, its check page, and `own_words` (the program names that must never show in another state's check results). Pick a `prefix` such as `washington-` and a `shared_order` that leaves room after the last guide (Utah uses 30, so 60).
2. **Rewrite the `both` entry by hand.** It frames the "page not found" page, and its tagline, menu, and footer words name every state.
3. **Add the sources.** In `data/sources.json`, add each one with `"guide": "washington"`. Sources any guide may use are already there, marked `"guide": "all"`. The build needs more than 12 entries of kind `state-explainer` for a guide before it lets that guide's footer or pages say "more than a dozen." A guide with fewer leaves those words out, as the Washington guide does with 9. Classify entries honestly; do not stretch the kind to reach the number.
4. **Add the facts.** In `data/claims.json`, add each one with `"guide": "washington"`. A fact may rely only on its own guide's sources or on shared ones.
5. **Make the folder.** `src/pages/washington/`, with the guide's home page, its other pages, and `_not-found.html` (a heading and the guide's main links, for the "page not found" page). The folder decides the guide, so pages need no `section` line. Name each file after its slug. By habit, each slug starts with the guide's prefix, so no two guides ask for the same address. Give each page an `order` number no other page uses.
6. **Put the state switch on the home page.** `{{GUIDE_SWITCH}}` on the first line of the body, above the headline. `{{DOC_COUNT}}` gives the guide's count of state documents.
7. **Give the shared pages their Washington parts.** In each file in `src/pages/shared/` marked `shared: yes`, add a `washington_sources:` line (and `washington_title:` and `washington_description:` where the plain ones name another state), and a `<!-- washington -->` block wherever there is a block for the other guides.
8. **Add the check.** A `checker-washington.js` file of words next to the other states' files, and a check page that loads it ([checker-logic.md](checker-logic.md)).
9. **Add checkpoints** for the new guide to `data/review.json`, and its hand-checks to [maintenance.md](maintenance.md).
10. **Look at the state switch on a phone.** Three states fit, but the third wraps to a second row. Decide whether that is still right, with the front door decision.
11. **Run everything** in [testing.md](testing.md), including `python3 -m unittest discover -s tools/tests`.

## What you do not need to touch

- The other guides' pages. Their state switch, their footers, and the "page not found" page pick up the new guide from the list.
- The rules that keep guides apart. They read the `guide` field and the folders.
- The browser tests. They run each guide's check from the list.
