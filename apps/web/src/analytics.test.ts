import test from "node:test";
import assert from "node:assert/strict";
import { period, sum, dayOffset } from "./analytics.ts";
import type { Daily } from "./types.ts";
const row = (day: string, views: number | null): Daily => ({
  day,
  views,
  resource_id: "a",
  minutes: null,
  gained: null,
  lost: null,
  likes: null,
  comments: null,
  shares: null,
  revenue: null,
  source: "test",
  kind: "official_daily",
});
test("missing dates do not become zeros or valid comparisons", () => {
  const value = period(
    [row("2026-01-01", 10), row("2026-01-03", 20)],
    "2026-01-03",
    "2026-01-04",
  );
  assert.equal(value.full, false);
  assert.equal(value.delta("views"), null);
});
test("equal complete periods compare and retain zero denominator as unavailable", () => {
  const rows = [
    row("2026-01-01", 10),
    row("2026-01-02", 10),
    row("2026-01-03", 20),
    row("2026-01-04", 20),
  ];
  assert.equal(period(rows, "2026-01-03", "2026-01-04").delta("views"), 100);
  assert.equal(
    period(
      [row("2026-01-01", 0), row("2026-01-02", 10)],
      "2026-01-02",
      "2026-01-02",
    ).delta("views"),
    null,
  );
});
test("partial monetary permissions never turn missing revenue into zero", () => {
  assert.equal(sum([row("2026-01-01", 2)], "revenue"), null);
  assert.equal(sum([], "views"), null);
  assert.equal(dayOffset("2026-03-01", -1), "2026-02-28");
});
