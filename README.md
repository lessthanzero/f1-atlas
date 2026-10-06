# F1 Atlas

Tiny, extremely fast open-source Formula 1 historical reference: dense tables, micro-visualisations, mobile-first, static/local-first.

> Do not compete with F1DB on data volume. Make F1 history easy to understand and explore.

## Stack

- Python ETL → SQLite
- Astro static site
- SVG/CSS micro-visualisations
- MIT license (code); F1DB-derived data under CC BY 4.0 attribution — see `DATA-SOURCES.md`

## Quick start

```bash
make bootstrap   # python venv + npm install
make etl         # fetch F1DB CSV → SQLite → JSON for Astro
make build       # etl + Astro static build
make test
make dev         # etl + Astro dev server
```

Data source: [F1DB](https://github.com/f1db/f1db) (CC BY 4.0). See `DATA-SOURCES.md`.

## MVP (v0.1)

Seasons · races · drivers · teams · circuits · results/qualifying tables · search · finish sparklines.

**Deferred:** Outlook projections (v0.2), deep engine pages, race investigation agents, live timing.

## Visual references

- https://biathlontime.com
- https://allekinos.de
- https://vladimirdesigner.github.io/otoplenie-tula/

## Layout

```text
data/           raw → normalised → derived
etl/            reproducible ingestion
web/            Astro site
visualisations/ shared SVG/CSS primitives
tests/
docs/
```
