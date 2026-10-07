"""Load F1DB CSVs into atlas.sqlite."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

from .schema import SCHEMA


def _int(v: str | None) -> int | None:
    if v is None or v == "":
        return None
    return int(float(v))


def _float(v: str | None) -> float | None:
    if v is None or v == "":
        return None
    return float(v)


def _bool_int(v: str | None) -> int:
    return 1 if v and v.lower() == "true" else 0


def load_csv_dir(csv_dir: Path, db_path: Path, source_tag: str) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
        _load_seasons(conn, csv_dir / "f1db-seasons.csv")
        _load_countries(conn, csv_dir / "f1db-countries.csv")
        _load_circuits(conn, csv_dir / "f1db-circuits.csv")
        _load_drivers(conn, csv_dir / "f1db-drivers.csv")
        _load_constructors(conn, csv_dir / "f1db-constructors.csv")
        _load_races(conn, csv_dir / "f1db-races.csv")
        _load_race_results(conn, csv_dir / "f1db-races-race-results.csv")
        _load_qualifying(conn, csv_dir / "f1db-races-qualifying-results.csv")
        _load_driver_standings(conn, csv_dir / "f1db-seasons-driver-standings.csv")
        _load_constructor_standings(conn, csv_dir / "f1db-seasons-constructor-standings.csv")
        conn.execute(
            "INSERT INTO meta(key, value) VALUES (?, ?)",
            ("schema_version", "0.3.0"),
        )
        conn.execute(
            "INSERT INTO meta(key, value) VALUES (?, ?)",
            ("source", "f1db"),
        )
        conn.execute(
            "INSERT INTO meta(key, value) VALUES (?, ?)",
            ("source_tag", source_tag),
        )
        conn.execute(
            "INSERT INTO meta(key, value) VALUES (?, ?)",
            ("attribution", "Historical Formula 1 data derived from F1DB (CC BY 4.0)"),
        )
        conn.commit()
    finally:
        conn.close()


def _rows(path: Path):
    with path.open(newline="", encoding="utf-8") as fh:
        yield from csv.DictReader(fh)


def _load_seasons(conn: sqlite3.Connection, path: Path) -> None:
    conn.executemany(
        "INSERT INTO seasons(year) VALUES (?)",
        [(int(r["year"]),) for r in _rows(path)],
    )


def _load_countries(conn: sqlite3.Connection, path: Path) -> None:
    conn.executemany(
        "INSERT INTO countries(id, name, alpha2) VALUES (?, ?, ?)",
        [
            (r["id"], r["name"], (r["alpha2Code"] or None))
            for r in _rows(path)
        ],
    )


def _load_circuits(conn: sqlite3.Connection, path: Path) -> None:
    conn.executemany(
        """
        INSERT INTO circuits(
          id, name, full_name, country_id, place_name,
          latitude, longitude, length_km, turns, total_races_held
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                r["id"],
                r["name"],
                r["fullName"] or None,
                r["countryId"] or None,
                r["placeName"] or None,
                _float(r["latitude"]),
                _float(r["longitude"]),
                _float(r["length"]),
                _int(r["turns"]),
                _int(r["totalRacesHeld"]),
            )
            for r in _rows(path)
        ],
    )


def _load_drivers(conn: sqlite3.Connection, path: Path) -> None:
    conn.executemany(
        """
        INSERT INTO drivers(
          id, name, first_name, last_name, abbreviation, nationality_country_id,
          total_championship_wins, total_race_starts, total_race_wins,
          total_podiums, total_poles, total_fastest_laps, total_points
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                r["id"],
                r["name"],
                r["firstName"] or None,
                r["lastName"] or None,
                r["abbreviation"] or None,
                r["nationalityCountryId"] or None,
                _int(r["totalChampionshipWins"]) or 0,
                _int(r["totalRaceStarts"]) or 0,
                _int(r["totalRaceWins"]) or 0,
                _int(r["totalPodiums"]) or 0,
                _int(r["totalPolePositions"]) or 0,
                _int(r["totalFastestLaps"]) or 0,
                _float(r["totalPoints"]) or 0.0,
            )
            for r in _rows(path)
        ],
    )


def _load_constructors(conn: sqlite3.Connection, path: Path) -> None:
    conn.executemany(
        """
        INSERT INTO constructors(
          id, name, full_name, country_id,
          total_championship_wins, total_race_starts, total_race_wins,
          total_podiums, total_poles, total_points
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                r["id"],
                r["name"],
                r["fullName"] or None,
                r["countryId"] or None,
                _int(r["totalChampionshipWins"]) or 0,
                _int(r["totalRaceStarts"]) or 0,
                _int(r["totalRaceWins"]) or 0,
                _int(r["totalPodiums"]) or 0,
                _int(r["totalPolePositions"]) or 0,
                _float(r["totalPoints"]) or 0.0,
            )
            for r in _rows(path)
        ],
    )


def _load_races(conn: sqlite3.Connection, path: Path) -> None:
    conn.executemany(
        """
        INSERT INTO races(id, year, round, date, name, circuit_id, grand_prix_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                int(r["id"]),
                int(r["year"]),
                int(r["round"]),
                r["date"] or None,
                r["officialName"] or r["grandPrixId"],
                r["circuitId"] or None,
                r["grandPrixId"] or None,
            )
            for r in _rows(path)
        ],
    )


def _load_race_results(conn: sqlite3.Connection, path: Path) -> None:
    conn.executemany(
        """
        INSERT INTO race_results(
          race_id, position_order, position_number, position_text,
          driver_id, constructor_id, grid_position, positions_gained,
          laps, time, points, reason_retired, fastest_lap
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                int(r["raceId"]),
                int(r["positionDisplayOrder"]),
                _int(r["positionNumber"]),
                r["positionText"] or None,
                r["driverId"],
                r["constructorId"] or None,
                _int(r["gridPositionNumber"]),
                _int(r["positionsGained"]),
                _int(r["laps"]),
                r["time"] or None,
                _float(r["points"]),
                r["reasonRetired"] or None,
                _bool_int(r["fastestLap"]),
            )
            for r in _rows(path)
        ],
    )


def _load_qualifying(conn: sqlite3.Connection, path: Path) -> None:
    conn.executemany(
        """
        INSERT INTO qualifying_results(
          race_id, position_order, position_number, position_text,
          driver_id, constructor_id, time
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                int(r["raceId"]),
                int(r["positionDisplayOrder"]),
                _int(r["positionNumber"]),
                r["positionText"] or None,
                r["driverId"],
                r["constructorId"] or None,
                r["time"] or None,
            )
            for r in _rows(path)
        ],
    )


def _load_driver_standings(conn: sqlite3.Connection, path: Path) -> None:
    conn.executemany(
        """
        INSERT INTO driver_standings(
          year, position_order, position_number, position_text,
          driver_id, points, championship_won
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                int(r["year"]),
                int(r["positionDisplayOrder"]),
                _int(r["positionNumber"]),
                r["positionText"] or None,
                r["driverId"],
                _float(r["points"]),
                _bool_int(r["championshipWon"]),
            )
            for r in _rows(path)
        ],
    )


def _load_constructor_standings(conn: sqlite3.Connection, path: Path) -> None:
    conn.executemany(
        """
        INSERT INTO constructor_standings(
          year, position_order, position_number, position_text,
          constructor_id, points, championship_won
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                int(r["year"]),
                int(r["positionDisplayOrder"]),
                _int(r["positionNumber"]),
                r["positionText"] or None,
                r["constructorId"],
                _float(r["points"]),
                _bool_int(r["championshipWon"]),
            )
            for r in _rows(path)
        ],
    )
