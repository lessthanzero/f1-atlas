#!/usr/bin/env python3
"""Download constructor SVGs from Wikimedia Commons; write simple wordmarks as fallback.

Targets: 2026 grid constructors + any constructor with >=1 win (from atlas.sqlite).
"""

from __future__ import annotations

import json
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "web" / "public" / "logos" / "constructors"
DB = ROOT / "data" / "derived" / "atlas.sqlite"

GRID_2026 = {
    "ferrari",
    "mclaren",
    "mercedes",
    "red-bull",
    "williams",
    "alpine",
    "aston-martin",
    "haas",
    "sauber",
    "kick-sauber",
    "racing-bulls",
    "rb",
}

# Verified / likely Commons File: titles (without File: prefix)
COMMONS_FILES: dict[str, list[str]] = {
    "alpine": ["Alpine_F1_Team_Logo.svg"],
    "haas": ["Haas_F1_Team_Logo.svg"],
    "sauber": ["Sauber_F1_Team_logo.svg"],
    "mercedes": [
        "Mercedes_AMG_Petronas_F1_Logo.svg",
        "Mercedes-AMG_Petronas_F1_Team_logo_(2026).svg",
    ],
    "williams": [
        "Atlassian_Williams_F1_Team_logo.svg",
        "Atlassian_Williams_F1_Team_horizontal_logo.svg",
        "Williams_Racing_2022_logo.svg",
    ],
    "mclaren": ["McLaren_2018_logo.svg", "McLaren_Speedmark.svg"],
    "honda": ["Logo_Honda_F1.svg", "Honda_Logo.svg"],
    "renault": ["RENAULT_F1.svg"],
    "bmw-sauber": ["BMW_logo_(gray).svg"],
    "porsche": ["Porsche_wordmark.svg"],
    "brawn": ["Brawn_GP_logo.svg"],
    "tyrrell": ["Tyrrell_Racing_logo.svg"],
    "racing-point": ["BWT_Racing_Point_Logo.svg"],
    "alfa-romeo": ["Alfa_Romeo_logo.svg"],
}

# Display labels for generated wordmarks (black type, atlas-owned simple SVG)
WORDMARKS: dict[str, str] = {
    "ferrari": "FERRARI",
    "mclaren": "McLAREN",
    "mercedes": "MERCEDES",
    "red-bull": "RED BULL",
    "williams": "WILLIAMS",
    "aston-martin": "ASTON MARTIN",
    "alpine": "ALPINE",
    "haas": "HAAS",
    "sauber": "SAUBER",
    "kick-sauber": "KICK SAUBER",
    "racing-bulls": "RACING BULLS",
    "rb": "RB",
    "lotus": "LOTUS",
    "lotus-f1": "LOTUS",
    "brabham": "BRABHAM",
    "renault": "RENAULT",
    "benetton": "BENETTON",
    "alfa-romeo": "ALFA ROMEO",
    "alphatauri": "ALPHATAURI",
    "toro-rosso": "TORO ROSSO",
}


def commons_url(filename: str) -> str:
    return "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(
        filename
    )


def target_ids() -> set[str]:
    ids = set(GRID_2026)
    if DB.exists():
        conn = sqlite3.connect(DB)
        try:
            for (cid,) in conn.execute(
                "SELECT id FROM constructors WHERE total_race_wins >= 1"
            ):
                ids.add(cid)
        finally:
            conn.close()
    return ids


def download(url: str, dest: Path) -> bool:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "F1AtlasLogoFetch/0.1 (historical reference; local build)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = resp.read()
            ctype = (resp.headers.get("Content-Type") or "").lower()
    except urllib.error.HTTPError as exc:
        print(f"  FAIL {exc.code} {url}")
        return False
    except Exception as exc:  # noqa: BLE001
        print(f"  FAIL {exc}")
        return False

    head = data.lstrip()[:200].lower()
    if b"<svg" not in head and "svg" not in ctype:
        print(f"  SKIP non-SVG")
        return False

    dest.write_bytes(data)
    return True


def write_wordmark(dest: Path, label: str) -> None:
    text = escape(label)
    # Compact black wordmark; scales via viewBox
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 48" role="img" aria-label="{text}">
  <text x="0" y="34" font-family="Arial Black, Helvetica Neue, Helvetica, Arial, sans-serif"
        font-size="28" font-weight="900" letter-spacing="-0.5" fill="#121212">{text}</text>
</svg>
'''
    dest.write_text(svg, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, dict] = {}
    ids = sorted(target_ids())
    print(f"Targets: {len(ids)}")

    for cid in ids:
        dest_name = f"{cid}.svg"
        dest = OUT / dest_name
        got = False
        for filename in COMMONS_FILES.get(cid, []):
            url = commons_url(filename)
            print(f"  fetch {cid} ← {filename}")
            time.sleep(0.8)
            if download(url, dest):
                manifest[cid] = {
                    "file": dest_name,
                    "source": f"https://commons.wikimedia.org/wiki/File:{filename}",
                    "license": "Wikimedia Commons (often PD-textlogo; trademarks still apply)",
                }
                got = True
                break

        if not got:
            label = WORDMARKS.get(cid)
            if label:
                print(f"  word {cid} ← {label}")
                write_wordmark(dest, label)
                manifest[cid] = {
                    "file": dest_name,
                    "source": "atlas-wordmark",
                    "license": "Simple wordmark generated for F1 Atlas (trademarks still apply)",
                }
            else:
                print(f"  mono  {cid}")
                if dest.exists():
                    dest.unlink()

    (OUT / "_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(manifest)} logos → {OUT}")


if __name__ == "__main__":
    main()
