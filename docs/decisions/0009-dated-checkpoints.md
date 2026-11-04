# 0009. Dated checkpoints instead of silent staleness

- Status: Accepted
- Date: 2026-11-02

## Context

The rules change on known dates (Jan. 1, 2027; late 2027; 2028) and on unknown ones (court rulings, a final federal rule, new OHA guidance). A guide that looks current but is not is worse than no guide.

## Decision

- Time-limited notes carry `data-show-until`; the browser hides them after that date. A note can be a whole section, one sentence, or part of a heading, so the words around it stay true after it hides.
- Text around a time-limited note names its own dates ("Starting Jan. 1, 2027, ..."), so readers without JavaScript see something out of season, never something false.
- `data/review.json` lists dated checkpoints with the work to do. The weekly workflow opens an issue when one passes. It also runs on Jan. 1 each year, so notes that expire on Dec. 31 are flagged the same day.
- A checkpoint two to three weeks before a fixed change date is a dry run: re-read the source, then run `tools/check_review_dates.py --today` with a date after the change to see what will expire.
- Every page shows the date its facts were last checked.

## Consequences

- Someone has to do the work at each checkpoint. The site does not shut itself off when a checkpoint passes; it keeps linking to official sources, which stay correct, while the issue reminds a person to update its own words.
