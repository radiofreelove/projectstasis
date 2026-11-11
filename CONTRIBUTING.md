# Contributing

Thank you for helping applicants. A few rules keep the site accurate and safe. Everyone follows the [Code of Conduct](CODE_OF_CONDUCT.md).

## Never share personal details

Issues and pull requests are public. Do not include anyone's name, case number, address, health information, immigration status, or letters from OHP. Describe the problem in general terms instead.

## Every fact needs an official source

1. Find the official source (OHA or ODHS for Oregon; Utah Medicaid or DWS for Utah; the federal rule; or a court order). Read it, do not rely on a summary. A source from one state never supports a fact about the other.
2. Add it to `data/sources.json` with today's date in `checked`, `opened: true`, and a `guide`: `oregon`, `utah`, or `all` for a source any guide may use (a federal rule, a court order).
3. Add or change the claim in `data/claims.json`, with the same kind of `guide`. By habit, Utah claims start with `U-`, but the build goes by `guide`.
4. Mark the sentence in the page (`src/pages/oregon/`, `src/pages/utah/`, or `src/pages/shared/` for the 4 pages both guides have) with `data-claim="ID"`, and list the source ID in that page's `sources:` line.
5. If official sources disagree, add an item to `docs/corrections.md`.

The build refuses links that are not in the registry and facts that are not in the ledger.

## Write plainly

Follow [docs/style-guide.md](docs/style-guide.md): purpose line, short version, short sentences, "may" for anything OHP decides, plain word first and OHP's word second.

## Run the checks

```bash
python3 tools/build.py
python3 -m unittest discover -s tools/tests
python3 tools/check_structure.py
python3 tools/check_contrast.py
python3 tools/check_reading_level.py
python3 tools/check_review_dates.py
python3 tools/serve.py    # look at the result at http://127.0.0.1:8000
```

Add a line to `CHANGELOG.md`. Commit `src/`, `data/`, `site/`, and `docs/` together.

## Licenses for what you contribute

By contributing, you agree to share your words and data under [CC BY 4.0](LICENSE) and your code under the [MIT License](LICENSE-CODE), like the rest of the project. Contribute only work you have the right to share.

## What we will not accept

Analytics, trackers, third-party scripts or fonts, questions about immigration or citizenship status, copies of state forms, or wording that tells someone what OHP will decide.
