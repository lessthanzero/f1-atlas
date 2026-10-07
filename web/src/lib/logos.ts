import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

export type LogoEntry = {
  file: string;
  source?: string;
  license?: string;
};

type Manifest = Record<string, LogoEntry>;

let cached: Manifest | null = null;

function loadManifest(): Manifest {
  if (cached) return cached;
  const path = join(process.cwd(), 'public/logos/constructors/_manifest.json');
  if (!existsSync(path)) {
    cached = {};
    return cached;
  }
  cached = JSON.parse(readFileSync(path, 'utf8')) as Manifest;
  return cached;
}

export function logoFor(constructorId: string): LogoEntry | null {
  return loadManifest()[constructorId] ?? null;
}

export function monogram(name: string): string {
  const cleaned = name.replace(/[^A-Za-z0-9 ]/g, ' ').trim();
  const parts = cleaned.split(/\s+/).filter(Boolean);
  if (parts.length === 0) return '?';
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
}
