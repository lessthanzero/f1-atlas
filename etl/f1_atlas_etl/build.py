"""Build SQLite atlas from normalised sources.

v0.1 scaffold: creates schema + placeholder tables. Wire F1DB / Jolpica ingest next.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import typer

app = typer.Typer(add_completion=False)

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS seasons (
  year INTEGER PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS circuits (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  country TEXT
);
CREATE TABLE IF NOT EXISTS drivers (
  id TEXT PRIMARY KEY,
  code TEXT,
  forename TEXT,
  surname TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS constructors (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS races (
  id INTEGER PRIMARY KEY,
  year INTEGER NOT NULL,
  round INTEGER NOT NULL,
  name TEXT NOT NULL,
  circuit_id TEXT REFERENCES circuits(id),
  date TEXT
);
"""


@app.command()
def main(out: Path = typer.Option(..., "--out", help="Output SQLite path")) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    conn = sqlite3.connect(out)
    try:
        conn.executescript(SCHEMA)
        conn.execute(
            "INSERT INTO meta(key, value) VALUES (?, ?)",
            ("schema_version", "0.1.0"),
        )
        conn.execute(
            "INSERT INTO meta(key, value) VALUES (?, ?)",
            ("status", "scaffold"),
        )
        conn.commit()
    finally:
        conn.close()
    typer.echo(f"Wrote {out}")


if __name__ == "__main__":
    app()
