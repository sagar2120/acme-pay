import { describe, expect, it } from "vitest";
import { filtersFrom } from "./filters";

describe("filtersFrom", () => {
  it("reads every filter from the address bar", () => {
    const params = new URLSearchParams("q=asha&location_id=3&department_id=1&level=L3");
    expect(filtersFrom(params)).toEqual({ q: "asha", location_id: 3, department_id: 1, level: "L3" });
  });

  it("ignores ids that are not numbers instead of sending them to the server", () => {
    expect(filtersFrom(new URLSearchParams("location_id=pune"))).toEqual({});
  });

  it("returns nothing when no filter is set", () => {
    expect(filtersFrom(new URLSearchParams("page=2"))).toEqual({});
  });
});
