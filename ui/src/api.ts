import { useEffect, useState } from "react";
import type { Filters } from "./lib/filters";

export type Option = { id: number; name: string };
export type Options = { locations: Option[]; departments: Option[]; levels: string[] };

export type EmployeeRow = {
  id: string;
  full_name: string;
  job_title: string;
  level: string;
  location: string;
  department: string;
  pay_amount: string | null;
  pay_currency: string | null;
  pay_usd: string | null;
};
export type EmployeePage = { items: EmployeeRow[]; total: number; page: number; page_size: number };

export type PayRecord = {
  id: number;
  amount: string;
  currency: string;
  amount_usd: string;
  effective_from: string;
  note: string | null;
};
export type EmployeeDetail = {
  id: string;
  full_name: string;
  job_title: string;
  location: string;
  currency: string;
  hire_date: string;
  pay_history: PayRecord[];
};

export type GroupBy = "location" | "department" | "level";
export type PayGroup = {
  name: string;
  headcount: number;
  payroll_usd: string;
  min_usd: string;
  p25_usd: string;
  median_usd: string;
  p75_usd: string;
  max_usd: string;
};
export type PaySummary = { group_by: GroupBy; overall: PayGroup; groups: PayGroup[] };

export type PayChange = { amount: number; effective_from: string; note?: string };
export type { Filters };

export type RowError = { line: number; employee_id: string; error: string };
export type ImportReport = { saved: number; errors: RowError[] };

export class ApiError extends Error {}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    // Our own errors carry a sentence in `detail`; anything else gets a plain fallback.
    const reason = typeof body.detail === "string" ? body.detail : `Request failed (${response.status})`;
    throw new ApiError(reason);
  }
  return body as T;
}

export function recordPayChange(employeeId: string, change: PayChange): Promise<PayRecord> {
  return request(`/api/employees/${employeeId}/pay`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(change),
  });
}

/** Upload a CSV of pay changes. A 422 with row errors is a report, not a failure. */
export async function importPayChanges(file: File): Promise<ImportReport> {
  const form = new FormData();
  form.append("file", file);
  const response = await fetch("/api/pay/import", { method: "POST", body: form });
  const body = await response.json().catch(() => ({}));
  if (response.status === 422 && Array.isArray(body.errors)) return body as ImportReport;
  if (!response.ok) {
    throw new ApiError(typeof body.detail === "string" ? body.detail : `Upload failed (${response.status})`);
  }
  return body as ImportReport;
}

/** GET a path; keeps the previous data on screen while the next request loads. */
export function useApi<T>(path: string | null, reloadKey = 0) {
  const [state, setState] = useState<{ data?: T; error?: string; loading: boolean }>({
    loading: path !== null,
  });

  useEffect(() => {
    if (path === null) return;
    const controller = new AbortController();
    setState((previous) => ({ ...previous, loading: true }));
    request<T>(path, { signal: controller.signal })
      .then((data) => setState({ data, loading: false }))
      .catch((error: Error) => {
        if (!controller.signal.aborted) setState({ error: error.message, loading: false });
      });
    return () => controller.abort();
  }, [path, reloadKey]);

  return state;
}
