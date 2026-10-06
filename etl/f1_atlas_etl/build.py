"""CLI: fetch F1DB → SQLite → site JSON."""

from __future__ import annotations

from pathlib import Path

import typer

from .export_json import export_site_json
from .fetch import DEFAULT_TAG, fetch_f1db_csv
from .load import load_csv_dir

app = typer.Typer(add_completion=False)

ROOT = Path(__file__).resolve().parents[2]


@app.command()
def fetch(
    tag: str = typer.Option(DEFAULT_TAG, help="F1DB release tag"),
    force: bool = typer.Option(False, help="Re-download even if present"),
) -> None:
    csv_dir = fetch_f1db_csv(ROOT / "data" / "raw", tag=tag, force=force)
    typer.echo(f"CSV ready at {csv_dir}")


@app.command("load")
def load_cmd(
    tag: str = typer.Option(DEFAULT_TAG, help="F1DB release tag recorded in meta"),
    out: Path = typer.Option(ROOT / "data" / "derived" / "atlas.sqlite", "--out"),
) -> None:
    csv_dir = ROOT / "data" / "raw" / "csv"
    if not (csv_dir / "f1db-seasons.csv").exists():
        fetch_f1db_csv(ROOT / "data" / "raw", tag=tag)
    load_csv_dir(csv_dir, out, source_tag=tag)
    typer.echo(f"Wrote {out}")


@app.command("export")
def export_cmd(
    db: Path = typer.Option(ROOT / "data" / "derived" / "atlas.sqlite", "--db"),
    out: Path = typer.Option(ROOT / "web" / "src" / "data" / "generated", "--out"),
) -> None:
    export_site_json(db, out)
    typer.echo(f"Exported JSON to {out}")


@app.command()
def build(
    tag: str = typer.Option(DEFAULT_TAG, help="F1DB release tag"),
    force_fetch: bool = typer.Option(False, "--force-fetch"),
) -> None:
    csv_dir = fetch_f1db_csv(ROOT / "data" / "raw", tag=tag, force=force_fetch)
    db = ROOT / "data" / "derived" / "atlas.sqlite"
    load_csv_dir(csv_dir, db, source_tag=tag)
    export_site_json(db, ROOT / "web" / "src" / "data" / "generated")
    typer.echo(f"Atlas build complete → {db}")


if __name__ == "__main__":
    # Default to full pipeline when invoked with no subcommand.
    import sys

    if len(sys.argv) == 1:
        sys.argv.append("build")
    app()
