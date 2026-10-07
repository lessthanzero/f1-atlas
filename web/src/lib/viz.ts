export type ReliabilityOutcome = 'win' | 'podium' | 'points' | 'finish' | 'dnf' | 'other';

export function outcomeFromResult(r: {
  pos?: number | null;
  posText?: string | null;
  points?: number | null;
  retired?: string | null;
}): ReliabilityOutcome {
  const text = (r.posText ?? '').toUpperCase();
  if (r.retired || text === 'DNF' || text === 'DSQ' || text === 'DNS') return 'dnf';
  if (typeof r.pos === 'number') {
    if (r.pos === 1) return 'win';
    if (r.pos <= 3) return 'podium';
    if ((r.points ?? 0) > 0) return 'points';
    return 'finish';
  }
  return 'other';
}

export function abbrevName(name: string): string {
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 8);
  return parts[parts.length - 1].slice(0, 10);
}
