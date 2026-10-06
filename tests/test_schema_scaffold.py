from pathlib import Path
import sqlite3
import tempfile

from f1_atlas_etl.schema import SCHEMA


def test_schema_creates_core_tables():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "atlas.sqlite"
        conn = sqlite3.connect(db)
        conn.executescript(SCHEMA)
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        conn.close()
        assert {
            "meta",
            "seasons",
            "races",
            "drivers",
            "constructors",
            "circuits",
            "race_results",
            "driver_standings",
        } <= tables
