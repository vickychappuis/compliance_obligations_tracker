import { describe, expect, it } from "vitest";

import { formatDate } from "@/lib/format";

describe("formatDate", () => {
  it("formats an ISO date in English", () => {
    expect(formatDate("2026-03-01", "en")).toBe("Mar 1, 2026");
  });

  it("formats an ISO date in Spanish", () => {
    expect(formatDate("2026-03-01", "es")).toMatch(/2026/);
  });
});
