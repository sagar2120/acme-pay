import { describe, expect, it } from "vitest";
import { toQueryString } from "./query";

describe("toQueryString", () => {
  it("leaves out filters that are not set", () => {
    expect(toQueryString({ location_id: 3, department_id: undefined, level: null, q: "" })).toBe(
      "?location_id=3",
    );
  });

  it("is empty when no filter is set", () => {
    expect(toQueryString({ q: "", level: undefined })).toBe("");
  });

  it("encodes text so names with spaces survive", () => {
    expect(toQueryString({ q: "asha patel", page: 2 })).toBe("?q=asha+patel&page=2");
  });
});
