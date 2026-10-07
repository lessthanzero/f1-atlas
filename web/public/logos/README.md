# Constructor logos

SVGs for the current grid and historic constructors with ≥1 win, sourced from Wikimedia Commons where available.

Teams without a file use a monogram in the UI (`ConstructorMark`).

## Trademark notice

Constructor names and logos are trademarks of their respective owners. They are included here for historical reference in a non-commercial open-source atlas. Copyright status of individual files varies (many simple wordmarks are tagged PD-textlogo on Commons); trademark rights still apply.

See `_manifest.json` for per-file Commons source links.

## Refresh

```bash
# requires data/derived/atlas.sqlite from `make etl`
python3 scripts/fetch_logos.py
```
