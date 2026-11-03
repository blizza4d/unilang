export function fuzzyMatch(pattern: string, text: string): boolean {
  if (!pattern) return true;
  const p = pattern.toLowerCase();
  const t = text.toLowerCase();

  let pIdx = 0;
  let tIdx = 0;

  while (pIdx < p.length && tIdx < t.length) {
    if (p[pIdx] === t[tIdx]) {
      pIdx++;
    }
    tIdx++;
  }

  return pIdx === p.length;
}

export function filterByFuzzy<T>(
  items: T[],
  query: string,
  keyExtractor: (item: T) => string
): T[] {
  if (!query.trim()) return items;
  return items.filter((item) => fuzzyMatch(query, keyExtractor(item)));
}
