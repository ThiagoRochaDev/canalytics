import type { Daily } from "./types";
export const dayOffset = (day: string, offset: number) =>
  new Date(new Date(day + "T12:00:00Z").getTime() + offset * 86400000)
    .toISOString()
    .slice(0, 10);
export const dayCount = (start: string, end: string) =>
  Math.round((Date.parse(end) - Date.parse(start)) / 86400000) + 1;
export const sum = (rows: Daily[], field: keyof Daily): number | null => {
  if (!rows.length || rows.some((r) => typeof r[field] !== "number"))
    return null;
  return rows.reduce((n, r) => n + (r[field] as number), 0);
};
export function period(rows: Daily[], start: string, end: string) {
  const length = dayCount(start, end);
  const current = rows.filter((r) => r.day >= start && r.day <= end);
  const previous = rows.filter(
    (r) => r.day >= dayOffset(start, -length) && r.day < start,
  );
  const full = new Set(current.map((r) => r.day)).size === length;
  const priorFull = new Set(previous.map((r) => r.day)).size === length;
  return {
    current,
    previous,
    full,
    priorFull,
    length,
    delta: (field: keyof Daily) => {
      const a = sum(current, field),
        b = sum(previous, field);
      return full && priorFull && a !== null && b !== null && b !== 0
        ? ((a - b) / Math.abs(b)) * 100
        : null;
    },
  };
}
export const fmt = (value: number | null | undefined, compact = false) =>
  value == null
    ? "—"
    : new Intl.NumberFormat("pt-BR", {
        notation: compact ? "compact" : "standard",
        maximumFractionDigits: compact ? 1 : 0,
      }).format(value);
export const shortDate = (value: string) =>
  new Date(
    value.length === 10 ? value + "T12:00:00Z" : value,
  ).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
export const labelProvider = (p: string) =>
  ({
    youtube: "YouTube",
    twitch: "Twitch",
    discord: "Discord",
    tiktok: "TikTok",
    bilibili: "Bilibili",
  })[p] || p;
