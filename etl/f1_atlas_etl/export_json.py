"""Export atlas.sqlite slices to JSON for Astro static pages."""

from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from pathlib import Path


def _dump(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + "\n")


def export_site_json(db_path: Path, out_dir: Path) -> None:
    if out_dir.exists():
        for p in out_dir.rglob("*"):
            if p.is_file():
                p.unlink()
    out_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        meta = {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM meta")}
        seasons = [r["year"] for r in conn.execute("SELECT year FROM seasons ORDER BY year DESC")]
        countries = [
            dict(r)
            for r in conn.execute(
                "SELECT id AS countryId, name AS countryName, alpha2 AS countryCode FROM countries ORDER BY name"
            )
        ]
        _dump(out_dir / "meta.json", meta)
        _dump(out_dir / "seasons.json", seasons)
        _dump(out_dir / "countries.json", countries)

        drivers = [
            dict(r)
            for r in conn.execute(
                """
                SELECT d.id, d.name, d.abbreviation,
                       d.nationality_country_id AS countryId,
                       c.name AS countryName,
                       c.alpha2 AS countryCode,
                       d.total_championship_wins AS titles, d.total_race_starts AS starts,
                       d.total_race_wins AS wins, d.total_podiums AS podiums,
                       d.total_poles AS poles, d.total_points AS points
                FROM drivers d
                LEFT JOIN countries c ON c.id = d.nationality_country_id
                WHERE d.total_race_starts > 0
                ORDER BY d.total_race_wins DESC, d.total_points DESC, d.name
                """
            )
        ]
        constructors = [
            dict(r)
            for r in conn.execute(
                """
                SELECT co.id, co.name,
                       co.country_id AS countryId,
                       c.name AS countryName,
                       c.alpha2 AS countryCode,
                       co.total_championship_wins AS titles, co.total_race_starts AS starts,
                       co.total_race_wins AS wins, co.total_podiums AS podiums,
                       co.total_poles AS poles, co.total_points AS points
                FROM constructors co
                LEFT JOIN countries c ON c.id = co.country_id
                WHERE co.total_race_starts > 0
                ORDER BY co.total_race_wins DESC, co.total_points DESC, co.name
                """
            )
        ]
        circuits = [
            dict(r)
            for r in conn.execute(
                """
                SELECT ci.id, ci.name,
                       ci.country_id AS countryId,
                       c.name AS countryName,
                       c.alpha2 AS countryCode,
                       ci.place_name AS place,
                       ci.total_races_held AS races, ci.length_km, ci.turns
                FROM circuits ci
                LEFT JOIN countries c ON c.id = ci.country_id
                ORDER BY ci.total_races_held DESC, ci.name
                """
            )
        ]
        _dump(out_dir / "drivers.json", drivers)
        _dump(out_dir / "constructors.json", constructors)
        _dump(out_dir / "circuits.json", circuits)

        search = {
            "drivers": [{"id": d["id"], "name": d["name"], "type": "driver"} for d in drivers],
            "constructors": [
                {"id": c["id"], "name": c["name"], "type": "constructor"} for c in constructors
            ],
            "circuits": [{"id": c["id"], "name": c["name"], "type": "circuit"} for c in circuits],
            "seasons": [{"id": str(y), "name": str(y), "type": "season"} for y in seasons],
        }
        _dump(out_dir / "search.json", search)

        for year in seasons:
            _export_season(conn, out_dir / "seasons", year)

        for d in drivers:
            _export_driver(conn, out_dir / "drivers", d["id"])

        for c in constructors:
            _export_constructor(conn, out_dir / "constructors", c["id"])

        for c in circuits:
            _export_circuit(conn, out_dir / "circuits", c["id"])

        race_ids = [r["id"] for r in conn.execute("SELECT id FROM races ORDER BY year DESC, round")]
        for race_id in race_ids:
            _export_race(conn, out_dir / "races", race_id)

        _dump(
            out_dir / "home.json",
            {
                "latestSeason": seasons[0] if seasons else None,
                "driverCount": len(drivers),
                "constructorCount": len(constructors),
                "circuitCount": len(circuits),
                "raceCount": len(race_ids),
                "attribution": meta.get("attribution"),
                "sourceTag": meta.get("source_tag"),
            },
        )
    finally:
        conn.close()


def _export_season(conn: sqlite3.Connection, folder: Path, year: int) -> None:
    races = [
        dict(r)
        for r in conn.execute(
            """
            SELECT r.id, r.round, r.date, r.name, r.circuit_id AS circuitId,
                   c.name AS circuitName
            FROM races r
            LEFT JOIN circuits c ON c.id = r.circuit_id
            WHERE r.year = ?
            ORDER BY r.round
            """,
            (year,),
        )
    ]
    drivers = [
        dict(r)
        for r in conn.execute(
            """
            SELECT s.position_number AS pos, s.position_text AS posText,
                   s.driver_id AS driverId, d.name AS driverName, s.points
            FROM driver_standings s
            JOIN drivers d ON d.id = s.driver_id
            WHERE s.year = ?
            ORDER BY s.position_order
            """,
            (year,),
        )
    ]
    constructors = [
        dict(r)
        for r in conn.execute(
            """
            SELECT s.position_number AS pos, s.position_text AS posText,
                   s.constructor_id AS constructorId, c.name AS constructorName, s.points
            FROM constructor_standings s
            JOIN constructors c ON c.id = s.constructor_id
            WHERE s.year = ?
            ORDER BY s.position_order
            """,
            (year,),
        )
    ]
    _dump(
        folder / f"{year}.json",
        {"year": year, "races": races, "driverStandings": drivers, "constructorStandings": constructors},
    )


def _export_driver(conn: sqlite3.Connection, folder: Path, driver_id: str) -> None:
    info = dict(
        conn.execute(
            """
            SELECT d.id, d.name, d.abbreviation,
                   d.nationality_country_id AS countryId,
                   c.name AS countryName,
                   c.alpha2 AS countryCode,
                   d.total_championship_wins AS titles, d.total_race_starts AS starts,
                   d.total_race_wins AS wins, d.total_podiums AS podiums,
                   d.total_poles AS poles, d.total_fastest_laps AS fastestLaps,
                   d.total_points AS points
            FROM drivers d
            LEFT JOIN countries c ON c.id = d.nationality_country_id
            WHERE d.id = ?
            """,
            (driver_id,),
        ).fetchone()
    )
    results = [
        dict(r)
        for r in conn.execute(
            """
            SELECT rr.race_id AS raceId, r.year, r.round, r.name AS raceName,
                   rr.position_number AS pos, rr.position_text AS posText,
                   rr.grid_position AS grid, rr.positions_gained AS gained,
                   rr.constructor_id AS constructorId, co.name AS constructorName,
                   rr.points, rr.reason_retired AS retired
            FROM race_results rr
            JOIN races r ON r.id = rr.race_id
            LEFT JOIN constructors co ON co.id = rr.constructor_id
            WHERE rr.driver_id = ?
            ORDER BY r.year DESC, r.round DESC
            """,
            (driver_id,),
        )
    ]
    # Compact sparkline of finishing positions (newest last for left→right career)
    finishes = [
        r["pos"]
        for r in reversed(results)
        if r["pos"] is not None
    ]
    _dump(
        folder / f"{driver_id}.json",
        {**info, "results": results, "finishSparkline": finishes[-80:]},
    )


def _export_constructor(conn: sqlite3.Connection, folder: Path, constructor_id: str) -> None:
    info = dict(
        conn.execute(
            """
            SELECT co.id, co.name, co.full_name AS fullName,
                   co.country_id AS countryId,
                   c.name AS countryName,
                   c.alpha2 AS countryCode,
                   co.total_championship_wins AS titles, co.total_race_starts AS starts,
                   co.total_race_wins AS wins, co.total_podiums AS podiums,
                   co.total_poles AS poles, co.total_points AS points
            FROM constructors co
            LEFT JOIN countries c ON c.id = co.country_id
            WHERE co.id = ?
            """,
            (constructor_id,),
        ).fetchone()
    )
    by_year: dict[int, dict] = defaultdict(lambda: {"wins": 0, "podiums": 0, "points": 0.0})
    for r in conn.execute(
        """
        SELECT r.year,
               SUM(CASE WHEN rr.position_number = 1 THEN 1 ELSE 0 END) AS wins,
               SUM(CASE WHEN rr.position_number IS NOT NULL AND rr.position_number <= 3 THEN 1 ELSE 0 END) AS podiums,
               SUM(COALESCE(rr.points, 0)) AS points
        FROM race_results rr
        JOIN races r ON r.id = rr.race_id
        WHERE rr.constructor_id = ?
        GROUP BY r.year
        ORDER BY r.year
        """,
        (constructor_id,),
    ):
        by_year[r["year"]] = {
            "year": r["year"],
            "wins": r["wins"],
            "podiums": r["podiums"],
            "points": r["points"],
        }
    _dump(folder / f"{constructor_id}.json", {**info, "seasons": list(by_year.values())})


def _export_circuit(conn: sqlite3.Connection, folder: Path, circuit_id: str) -> None:
    info = dict(
        conn.execute(
            """
            SELECT ci.id, ci.name, ci.full_name AS fullName,
                   ci.country_id AS countryId,
                   c.name AS countryName,
                   c.alpha2 AS countryCode,
                   ci.place_name AS place, ci.latitude, ci.longitude,
                   ci.length_km AS lengthKm, ci.turns, ci.total_races_held AS races
            FROM circuits ci
            LEFT JOIN countries c ON c.id = ci.country_id
            WHERE ci.id = ?
            """,
            (circuit_id,),
        ).fetchone()
    )
    races = [
        dict(r)
        for r in conn.execute(
            """
            SELECT id, year, round, date, name,
                   (SELECT driver_id FROM race_results
                    WHERE race_id = races.id AND position_number = 1 LIMIT 1) AS winnerId
            FROM races
            WHERE circuit_id = ?
            ORDER BY year DESC, round DESC
            """,
            (circuit_id,),
        )
    ]
    for race in races:
        if race["winnerId"]:
            row = conn.execute(
                "SELECT name FROM drivers WHERE id = ?", (race["winnerId"],)
            ).fetchone()
            race["winnerName"] = row["name"] if row else None
        else:
            race["winnerName"] = None
    _dump(folder / f"{circuit_id}.json", {**info, "races": races})


def _export_race(conn: sqlite3.Connection, folder: Path, race_id: int) -> None:
    race = dict(
        conn.execute(
            """
            SELECT r.id, r.year, r.round, r.date, r.name, r.circuit_id AS circuitId,
                   c.name AS circuitName
            FROM races r
            LEFT JOIN circuits c ON c.id = r.circuit_id
            WHERE r.id = ?
            """,
            (race_id,),
        ).fetchone()
    )
    results = [
        dict(r)
        for r in conn.execute(
            """
            SELECT rr.position_number AS pos, rr.position_text AS posText,
                   rr.driver_id AS driverId, d.name AS driverName,
                   rr.constructor_id AS constructorId, co.name AS constructorName,
                   rr.grid_position AS grid, rr.positions_gained AS gained,
                   rr.laps, rr.time, rr.points, rr.reason_retired AS retired,
                   rr.fastest_lap AS fastestLap
            FROM race_results rr
            JOIN drivers d ON d.id = rr.driver_id
            LEFT JOIN constructors co ON co.id = rr.constructor_id
            WHERE rr.race_id = ?
            ORDER BY rr.position_order
            """,
            (race_id,),
        )
    ]
    qualifying = [
        dict(r)
        for r in conn.execute(
            """
            SELECT q.position_number AS pos, q.position_text AS posText,
                   q.driver_id AS driverId, d.name AS driverName,
                   q.constructor_id AS constructorId, co.name AS constructorName,
                   q.time
            FROM qualifying_results q
            JOIN drivers d ON d.id = q.driver_id
            LEFT JOIN constructors co ON co.id = q.constructor_id
            WHERE q.race_id = ?
            ORDER BY q.position_order
            """,
            (race_id,),
        )
    ]
    _dump(
        folder / f"{race_id}.json",
        {**race, "results": results, "qualifying": qualifying},
    )
