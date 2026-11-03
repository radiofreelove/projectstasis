# Accessibility notes

## Standard

- **Target:** [WCAG 2.2](https://www.w3.org/TR/WCAG22/) Level AA (W3C Recommendation, 12 December 2024), with Level AAA where practical: text contrast of 7:1 (1.4.6), main controls at least 44 by 44 px (2.5.5), and no timing (2.2.3).
- **Cognitive and learning disabilities:** W3C's [Making Content Usable for People with Cognitive and Learning Disabilities](https://www.w3.org/TR/coga-usable/) (Working Group Note, 29 April 2021). It is supplemental guidance, not required for WCAG conformance. It is the closest published standard to "neurodivergent-friendly" design. There is no legal or W3C standard called "neurodivergent compliance," so this site does not claim one.
- **Claim on the site:** "Built to meet," not "certified." No audit by people who use assistive technology has happened yet.

## Design patterns, mapped to W3C's cognitive accessibility objectives

| Objective (COGA) | What this site does |
|---|---|
| 1. Help users understand what things are | Every page starts with a plain headline and a "purpose" line. Same header, menu, and footer on every page. Buttons look like buttons; links are underlined. |
| 2. Help users find what they need | Four menu items only (Home, Check, Apply, Get help). "Go deeper" cards on the home page. A full page list in every footer. One topic per page. |
| 3. Use clear content | Short sentences, plain words, literal language, no idioms. Bold labels on key bullets. Numbers as digits, with plain equivalents ("about $135 a week," "about 20 hours a week"). Reading level measured for every page ([reading-level.md](reading-level.md)). |
| 4. Help users avoid mistakes | The check asks one step at a time, shows "Step 1 of 3," has Back buttons, keeps answers when going back, and gives plain error messages that say how to fix them. "Start over" is always offered. |
| 5. Help users focus | No pop-ups, carousels, autoplay, animation, or ads. A "Just the key points" setting hides extra detail. |
| 6. Do not rely on memory | No accounts or logins. Results list what the person picked. Pages and results can be printed. An hours log can be printed. |
| 7. Provide help and support | "Get help" is in the same place on every page (also WCAG 3.2.6). Phone numbers for people, free helpers, language lines, and legal help. The check's results always name a next step. |
| 8. Support adaptation and personalization | Display settings: text size (3 levels), spacing (WCAG 1.4.12 values or more), colors (device, warm light, plain white, dark), and how much to show. Respects the device's dark mode and reduced-motion settings, Windows high contrast (forced colors), and browser zoom. |

## Other details

- Skip link to the main content on every page.
- Landmarks: header, two navigation regions with distinct names, main, and footer.
- One h1 per page; headings never skip a level (checked by `tools/check_structure.py`).
- Form controls are wrapped in labels; groups use fieldset and legend; descriptions and errors are linked with `aria-describedby`.
- Focus: a thick outline plus a yellow halo; focused links turn yellow with black text. Never removed.
- Language of parts: the paper application links in other languages use `lang` on their native names and `hreflang` on the links (WCAG 3.1.2).
- Links say where they go. PDFs are labeled "PDF." No link opens a new window.
- Reflow: no sideways scrolling at 320 px wide, including with extra-large text and extra spacing (checked in the browser).
- Print: clean black-on-white, with web addresses printed after links.
- No images of text. The only image is the decorative logo, with empty alt text.

## Testing done for 0.1.0

See [testing.md](testing.md) and the generated [testing-browser.md](testing-browser.md). In short: structure lint, contrast for 31 color pairs, reading level for 16 pages, and real-browser tests in 5 settings all passed. The axe-core engine could not be installed in the build environment, so it was not run locally; the GitHub workflow runs it.

## Known gaps

1. No testing yet with people who use screen readers, switch access, voice control, or magnification, or with neurodivergent applicants. This matters more than any automated score.
2. Reading level is above the grade 6 target on the health and immigration pages, mostly because of names of conditions and programs that cannot be simplified ([reading-level.md](reading-level.md)).
3. State PDFs the site links to may not be accessible. The site tells people they can ask OHP for another format for free.
4. The site is in English only. It links to the state's translated forms and language lines instead of machine-translating ([decisions/0007-no-machine-translation.md](decisions/0007-no-machine-translation.md)).
5. The "Just the key points" mode is new and has not been tested with users.
