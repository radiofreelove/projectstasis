# 0004. Use the ODHS palette, not the ODHS identity

- Status: Accepted
- Date: 2026-11-02

## Context

Using colors people already associate with Oregon human services makes the site feel familiar and trustworthy. The ODHS Brand Guidelines (registry S31) publish the palette with contrast pairings. But a site that looks like a state site could mislead people into thinking it is one, and the guidelines govern agency materials made by staff, contractors, vendors, and volunteers.

## Decision

- Use the published palette for colors only.
- Do not use the ODHS logo, brandmark, seal, name, or typeface as this site's brand. Use an original crystal mark and the name "The Stasis Project."
- Say "Independent guide. Not run by the state." in a banner at the top of every page, and name the State of Oregon, OHA, and ODHS in every footer.

## Consequences

- The site is visually related to state materials but clearly separate.
- If ODHS asks the project to change colors, it can do so by editing `site/assets/css/site.css` and `data/palette.json`, then re-running the contrast check.
