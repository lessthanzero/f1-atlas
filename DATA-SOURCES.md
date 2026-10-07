# Data sources & attribution

## F1DB

Primary historical structured data: [F1DB](https://github.com/f1db/f1db)  
License: [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)

Redistributed or derived datasets in this repository must retain F1DB attribution.
Example credit line:

> Historical Formula 1 data derived from [F1DB](https://www.f1db.com) (CC BY 4.0).

## Jolpica

API-compatible historical/current results (Ergast-compatible). Check upstream terms before redistributing raw dumps; prefer regenerating via ETL.

## Constructor logos

Wordmark/logo SVGs for the current grid and constructors with ≥1 win live under `web/public/logos/constructors/`, sourced from Wikimedia Commons where available (`scripts/fetch_logos.py`). See `web/public/logos/README.md` for trademark notice and `_manifest.json` for per-file links.

## Rules

- Never invent race results, standings, or derived statistics silently.
- Every derived metric must be explainable and tested.
- Site chrome, copy, and original visualisations are covered by the project MIT license; upstream data remains under its own terms.
