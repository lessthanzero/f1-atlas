/** ISO 3166-1 alpha-2 → regional-indicator flag emoji. */
export function flagEmoji(code: string | null | undefined): string {
  if (!code || code.length !== 2) return '';
  const upper = code.toUpperCase();
  if (!/^[A-Z]{2}$/.test(upper)) return '';
  const A = 0x1f1e6;
  return String.fromCodePoint(
    A + (upper.charCodeAt(0) - 65),
    A + (upper.charCodeAt(1) - 65)
  );
}

export function countryLabel(opts: {
  countryName?: string | null;
  countryCode?: string | null;
  countryId?: string | null;
}): string {
  const name = opts.countryName?.trim();
  if (name) {
    const flag = flagEmoji(opts.countryCode);
    return flag ? `${flag} ${name}` : name;
  }
  return opts.countryId ?? '—';
}
