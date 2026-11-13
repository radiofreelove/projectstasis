# Design notes

## Colors

All colors come from the [ODHS Brand Guidelines](https://sharedsystems.dhsoha.state.or.us/DHSForms/Served/dhs2022.pdf) (form de2022, revised 07/25), registry S31. The guidelines say their listed pairings meet WCAG 2.2 Level AA; this site holds text to 7:1 (AAA) and checks every pair it uses in [contrast.md](contrast.md).

| ODHS name | Hex | Role on this site |
|---|---|---|
| North Star Indigo | `#2e3192` | Headings, links, primary buttons, independent-guide banner (light themes); logo edges and lower facets |
| Glacial Blue | `#b4dcf5` | Callout boxes (light); headings, links, and buttons (dark); logo halo, sides, and center |
| Fog Gray | `#f4f2ed` | Page background (warm light, the default); body text (dark) |
| Forest Green | `#184e49` | Footer; left edge of "good to know" boxes |
| Willamette Green | `#86c679` | Left edge of "good to know" boxes (dark) |
| Mist Grey | `#d8e1e5` | Not used at present |
| Marionberry Red | `#a91f50` | Left edge of warning boxes (light) only. The guidelines reserve bold reds for intentional emphasis, so it is never used for text. |
| Harvest Gold | `#ecd263` | Keyboard focus highlight; warning edge (dark) |
| Desert Sand | `#eddfd4` | Warning box background (light) |
| Primary Black | `#000000` | Page background (dark); focus outline (light) |
| Primary White | `#ffffff` | Cards and header (light); button text; logo top facets |
| Ashland Charcoal | `#414042` | Body text (light); cards and callouts (dark) |

### Brand boundary

The Washington and Utah guides use the same palette and components as the Oregon guide. The palette is the site's design system; it does not signal any tie to any state ([decisions/0013-utah-section.md](decisions/0013-utah-section.md)).

The site uses the ODHS **palette** only. It does not use the ODHS logo, brandmark, name, or typeface as its brand, and every page says "Independent guide. Not run by the state." in a banner and again in the footer. The logo is an original mark: a still, six-sided crystal, lit from above, drawn only from palette colors. A light outer edge and a dark inner edge keep it visible on light and dark backgrounds. See [decisions/0004-odhs-palette-not-identity.md](decisions/0004-odhs-palette-not-identity.md).

## Themes

- **Match my device** (default): warm light, or dark when the device prefers dark.
- **Warm light:** Fog Gray background. Softer than pure white, which some readers find glaring.
- **Plain white:** for people who prefer maximum brightness or print-like pages.
- **Dark:** black background, Fog Gray text, Glacial Blue headings and links.
- **Forced colors** (Windows high contrast): borders switch to system colors so boxes and buttons stay visible.
- **Print:** black on white, web addresses printed after links, menus and settings hidden.

## Type

- System fonts by default, in the same order as The Strand Project (system-ui first). Readers can choose Atkinson Hyperlegible Next in Display settings; it is served from this site and downloaded only when chosen. See [decisions/0012-shared-with-strand.md](decisions/0012-shared-with-strand.md).
- Base size 18 px at the browser's default, set as a percentage so the browser's own text-size setting still works. Large and extra large raise it to 21 and 24 px.
- Line height 1.6; "More space" raises it to 2 and adds letter and word spacing beyond the WCAG 1.4.12 values.
- Text column about 38 characters wide in rem units, which keeps lines near 60 to 75 characters.
- No italics for long text, no all caps, no justified text.

## Components

| Component | Purpose |
|---|---|
| Purpose line | The thick left rule under each h1: why this page exists |
| Short version | Bold label, then one plain line. Smart Brevity in a list. |
| Callout (blue) | Next step or bottom line |
| Good box (green edge) | A way to meet the rules, or trusted help |
| Warning box (sand, red edge) | Something that can cost coverage or money |
| Steps | Numbered circles for things to do in order |
| Cards | Big tap targets for "go deeper" links |
| "How much to show" strip | A slim box at the top of every page, above the heading: the question "Still too much to take in?", one button ("Show just the key points"), and one line saying what it does. In key-points mode the same box is the banner ("You are seeing just the key points. Some details are hidden.") with a "Show everything" button. It is the same setting as "How much to show" in Display settings: one saved value, and each control follows the other. One button, so keyboard focus stays where it is. Hidden without JavaScript, and never printed; a printed page always shows everything. A link into hidden detail turns "Everything" back on first. Writers mark extra detail by hand with `class="more"`. |
| State switch | One big button for each state above the headline of each home page, under the words "Pick your state." The order is Oregon, Washington, Utah ([decisions/0015-front-door-with-three-guides.md](decisions/0015-front-door-with-three-guides.md)). The guide you are in is filled and says so in words ("This is the OHP guide."); the others are outlined and name the guide they open. Same look as the menu, so it reads as part of the site. Side by side when they fit, stacked on narrow screens and at large text sizes: at 320 px each state has its own row. Built from the guide list in `tools/build.py` (`{{GUIDE_SWITCH}}`), so a new guide appears on every home page at once. |
| Choice rows | Radio buttons and checkboxes inside full-width bordered rows, at least 48 px tall |
| Tag | "PDF" label after links to PDFs |

## Motion

None. No transitions, animations, carousels, or auto-advancing content. Reduced-motion settings are respected anyway.
