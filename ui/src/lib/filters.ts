export type Filters = {
  q?: string;
  location_id?: number;
  department_id?: number;
  level?: string;
};

export function filtersFrom(params: URLSearchParams): Filters {
  const filters: Filters = {};
  const q = params.get("q");
  const level = params.get("level");
  const location = idFrom(params.get("location_id"));
  const department = idFrom(params.get("department_id"));
  if (q) filters.q = q;
  if (location !== undefined) filters.location_id = location;
  if (department !== undefined) filters.department_id = department;
  if (level) filters.level = level;
  return filters;
}

function idFrom(value: string | null): number | undefined {
  const id = Number(value);
  return value && Number.isInteger(id) ? id : undefined;
}
