import { describe, expect, it } from "vitest";
import { formatMoney } from "./money";

describe("formatMoney", () => {
  it("groups rupees the Indian way, in lakhs and crores", () => {
    expect(formatMoney("1800000.00", "INR")).toBe("₹18,00,000");
    expect(formatMoney("12500000", "INR")).toBe("₹1,25,00,000");
  });

  it("groups other currencies in thousands with their own symbol", () => {
    expect(formatMoney("125000.00", "USD")).toBe("$125,000");
    expect(formatMoney("72000", "EUR")).toBe("€72,000");
    expect(formatMoney("68000", "GBP")).toBe("£68,000");
    expect(formatMoney("105000", "SGD")).toBe("S$105,000");
  });

  it("rounds to whole units because pay is quoted annually", () => {
    expect(formatMoney("21600.49", "USD")).toBe("$21,600");
  });

  it("shows a dash when there is no amount", () => {
    expect(formatMoney(null, "USD")).toBe("—");
  });
});
