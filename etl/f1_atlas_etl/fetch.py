"""Download F1DB CSV release into data/raw."""

from __future__ import annotations

import zipfile
from pathlib import Path

import httpx

DEFAULT_TAG = "v2026.16.0"
ASSET = "f1db-csv.zip"


def fetch_f1db_csv(raw_dir: Path, tag: str = DEFAULT_TAG, force: bool = False) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    zip_path = raw_dir / ASSET
    csv_dir = raw_dir / "csv"
    marker = csv_dir / "f1db-seasons.csv"

    if marker.exists() and not force:
        return csv_dir

    url = f"https://github.com/f1db/f1db/releases/download/{tag}/{ASSET}"
    if force or not zip_path.exists():
        with httpx.stream("GET", url, follow_redirects=True, timeout=120.0) as resp:
            resp.raise_for_status()
            with zip_path.open("wb") as fh:
                for chunk in resp.iter_bytes():
                    fh.write(chunk)

    if csv_dir.exists():
        for child in csv_dir.iterdir():
            if child.is_file():
                child.unlink()
    else:
        csv_dir.mkdir(parents=True)

    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(csv_dir)
    return csv_dir
