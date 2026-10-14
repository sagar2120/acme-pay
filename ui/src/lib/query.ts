export type QueryValue = string | number | null | undefined;

export function toQueryString(params: Record<string, QueryValue>): string {
  const set = Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== "");
  if (set.length === 0) return "";
  return `?${new URLSearchParams(set.map(([key, value]) => [key, String(value)]))}`;
}
