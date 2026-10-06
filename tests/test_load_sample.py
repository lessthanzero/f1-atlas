from pathlib import Path
import sqlite3
import tempfile

from f1_atlas_etl.load import load_csv_dir
from f1_atlas_etl.export_json import export_site_json

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "raw" / "csv"


def test_load_and_export_from_local_csv():
    if not (CSV / "f1db-seasons.csv").exists():
        return  # skip until fetch has run in this workspace
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "atlas.sqlite"
        out = Path(tmp) / "json"
        load_csv_dir(CSV, db, source_tag="test")
        conn = sqlite3.connect(db)
        seasons = conn.execute("SELECT COUNT(*) FROM seasons").fetchone()[0]
        races = conn.execute("SELECT COUNT(*) FROM races").fetchone()[0]
        results = conn.execute("SELECT COUNT(*) FROM race_results").fetchone()[0]
        conn.close()
        assert seasons >= 70
        assert races >= 1000
        assert results >= 10000
        export_site_json(db, out)
        assert (out / "home.json").exists()
        assert (out / "seasons.json").exists()
        assert (out / "drivers.json").exists()
