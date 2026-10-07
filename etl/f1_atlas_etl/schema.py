"""Atlas SQLite schema (projected from F1DB CSVs)."""

SCHEMA = """
PRAGMA journal_mode = WAL;

CREATE TABLE meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE seasons (
  year INTEGER PRIMARY KEY
);

CREATE TABLE countries (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  alpha2 TEXT
);

CREATE TABLE circuits (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  full_name TEXT,
  country_id TEXT,
  place_name TEXT,
  latitude REAL,
  longitude REAL,
  length_km REAL,
  turns INTEGER,
  total_races_held INTEGER
);

CREATE TABLE drivers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  first_name TEXT,
  last_name TEXT,
  abbreviation TEXT,
  nationality_country_id TEXT,
  total_championship_wins INTEGER,
  total_race_starts INTEGER,
  total_race_wins INTEGER,
  total_podiums INTEGER,
  total_poles INTEGER,
  total_fastest_laps INTEGER,
  total_points REAL
);

CREATE TABLE constructors (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  full_name TEXT,
  country_id TEXT,
  total_championship_wins INTEGER,
  total_race_starts INTEGER,
  total_race_wins INTEGER,
  total_podiums INTEGER,
  total_poles INTEGER,
  total_points REAL
);

CREATE TABLE races (
  id INTEGER PRIMARY KEY,
  year INTEGER NOT NULL,
  round INTEGER NOT NULL,
  date TEXT,
  name TEXT NOT NULL,
  circuit_id TEXT,
  grand_prix_id TEXT,
  FOREIGN KEY (year) REFERENCES seasons(year),
  FOREIGN KEY (circuit_id) REFERENCES circuits(id)
);

CREATE TABLE race_results (
  race_id INTEGER NOT NULL,
  position_order INTEGER NOT NULL,
  position_number INTEGER,
  position_text TEXT,
  driver_id TEXT NOT NULL,
  constructor_id TEXT,
  grid_position INTEGER,
  positions_gained INTEGER,
  laps INTEGER,
  time TEXT,
  points REAL,
  reason_retired TEXT,
  fastest_lap INTEGER,
  PRIMARY KEY (race_id, position_order),
  FOREIGN KEY (race_id) REFERENCES races(id),
  FOREIGN KEY (driver_id) REFERENCES drivers(id),
  FOREIGN KEY (constructor_id) REFERENCES constructors(id)
);

CREATE TABLE qualifying_results (
  race_id INTEGER NOT NULL,
  position_order INTEGER NOT NULL,
  position_number INTEGER,
  position_text TEXT,
  driver_id TEXT NOT NULL,
  constructor_id TEXT,
  time TEXT,
  PRIMARY KEY (race_id, position_order),
  FOREIGN KEY (race_id) REFERENCES races(id)
);

CREATE TABLE driver_standings (
  year INTEGER NOT NULL,
  position_order INTEGER NOT NULL,
  position_number INTEGER,
  position_text TEXT,
  driver_id TEXT NOT NULL,
  points REAL,
  championship_won INTEGER,
  PRIMARY KEY (year, position_order),
  FOREIGN KEY (year) REFERENCES seasons(year),
  FOREIGN KEY (driver_id) REFERENCES drivers(id)
);

CREATE TABLE constructor_standings (
  year INTEGER NOT NULL,
  position_order INTEGER NOT NULL,
  position_number INTEGER,
  position_text TEXT,
  constructor_id TEXT NOT NULL,
  points REAL,
  championship_won INTEGER,
  PRIMARY KEY (year, position_order),
  FOREIGN KEY (year) REFERENCES seasons(year),
  FOREIGN KEY (constructor_id) REFERENCES constructors(id)
);

CREATE INDEX idx_races_year ON races(year);
CREATE INDEX idx_results_driver ON race_results(driver_id);
CREATE INDEX idx_results_constructor ON race_results(constructor_id);
"""
