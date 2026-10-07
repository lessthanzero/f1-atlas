import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const root = join(process.cwd(), 'src/data/generated');

function readJson<T>(rel: string): T {
  return JSON.parse(readFileSync(join(root, rel), 'utf8')) as T;
}

export function hasGeneratedData(): boolean {
  return existsSync(join(root, 'meta.json'));
}

export function getMeta() {
  return readJson<Record<string, string>>('meta.json');
}

export function getHome() {
  return readJson<{
    latestSeason: number | null;
    driverCount: number;
    constructorCount: number;
    circuitCount: number;
    raceCount: number;
    attribution?: string;
    sourceTag?: string;
  }>('home.json');
}

export function getSeasons(): number[] {
  return readJson<number[]>('seasons.json');
}

export function getSeason(year: number) {
  return readJson<{
    year: number;
    races: Array<{
      id: number;
      round: number;
      date: string | null;
      name: string;
      circuitId: string | null;
      circuitName: string | null;
    }>;
    driverStandings: Array<{
      pos: number | null;
      posText: string | null;
      driverId: string;
      driverName: string;
      points: number | null;
    }>;
    constructorStandings: Array<{
      pos: number | null;
      posText: string | null;
      constructorId: string;
      constructorName: string;
      points: number | null;
    }>;
  }>(`seasons/${year}.json`);
}

export function getDrivers() {
  return readJson<
    Array<{
      id: string;
      name: string;
      abbreviation: string | null;
      countryId: string | null;
      countryName: string | null;
      countryCode: string | null;
      titles: number;
      starts: number;
      wins: number;
      podiums: number;
      poles: number;
      points: number;
    }>
  >('drivers.json');
}

export function getDriver(id: string) {
  return readJson<any>(`drivers/${id}.json`);
}

export function getConstructors() {
  return readJson<
    Array<{
      id: string;
      name: string;
      countryId: string | null;
      countryName: string | null;
      countryCode: string | null;
      titles: number;
      starts: number;
      wins: number;
      podiums: number;
      poles: number;
      points: number;
    }>
  >('constructors.json');
}

export function getConstructor(id: string) {
  return readJson<any>(`constructors/${id}.json`);
}

export function getCircuits() {
  return readJson<
    Array<{
      id: string;
      name: string;
      countryId: string | null;
      countryName: string | null;
      countryCode: string | null;
      place: string | null;
      races: number | null;
      length_km: number | null;
      turns: number | null;
    }>
  >('circuits.json');
}

export function getCircuit(id: string) {
  return readJson<any>(`circuits/${id}.json`);
}

export function getRace(id: number) {
  return readJson<any>(`races/${id}.json`);
}

export function listRaceIds(): number[] {
  const dir = join(root, 'races');
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((f) => f.endsWith('.json'))
    .map((f) => Number(f.replace('.json', '')))
    .filter((n) => !Number.isNaN(n));
}

export function getSearchIndex() {
  return readJson<{
    drivers: Array<{ id: string; name: string; type: string }>;
    constructors: Array<{ id: string; name: string; type: string }>;
    circuits: Array<{ id: string; name: string; type: string }>;
    seasons: Array<{ id: string; name: string; type: string }>;
  }>('search.json');
}

export function hrefFor(type: string, id: string): string {
  const base = import.meta.env.BASE_URL;
  switch (type) {
    case 'driver':
      return `${base}drivers/${id}/`;
    case 'constructor':
      return `${base}constructors/${id}/`;
    case 'circuit':
      return `${base}circuits/${id}/`;
    case 'season':
      return `${base}seasons/${id}/`;
    case 'race':
      return `${base}races/${id}/`;
    default:
      return base;
  }
}
