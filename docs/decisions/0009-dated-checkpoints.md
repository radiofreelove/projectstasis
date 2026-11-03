# 0009. Dated checkpoints instead of silent staleness

- Status: Accepted
- Date: 2026-11-02

## Context

The rules change on known dates (Jan. 1, 2027; late 2027; 2028) and on unknown ones (court rulings, a final federal rule, new OHA guidance). A guide that looks current but is not is worse than no guide.

## Decision

- Time-limited notes carry `data-show-until`; the browser hides them after that date.
- `data/review.json` lists dated checkpoints with the work to do. The weekly workflow opens an issue when one passes.
- Every page shows the date its facts were last checked.

## Consequences

- Someone has to do the work at each checkpoint. The site does not shut itself off when a checkpoint passes; it keeps linking to official sources, which stay correct, while the issue reminds a person to update its own words.
