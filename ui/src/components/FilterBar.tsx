import { Input, Select } from "antd";
import { useEffect, useState } from "react";
import type { Filters, Options } from "../api";

type Props = {
  options?: Options;
  value: Filters;
  onChange: (next: Filters) => void;
  withSearch?: boolean;
};

const SEARCH_DELAY_MS = 300;

export function FilterBar({ options, value, onChange, withSearch = false }: Props) {
  const [text, setText] = useState(value.q ?? "");

  // Wait until typing pauses before asking the server, instead of one request per key.
  useEffect(() => {
    if (text === (value.q ?? "")) return;
    const timer = setTimeout(() => onChange({ ...value, q: text || undefined }), SEARCH_DELAY_MS);
    return () => clearTimeout(timer);
    // Only the typed text restarts the timer; filters and onChange change on every render.
  }, [text]);

  return (
    <>
      {withSearch && (
        <Input.Search
          allowClear
          placeholder="Name or email"
          aria-label="Search by name or email"
          value={text}
          onChange={(event) => setText(event.target.value)}
          style={{ width: 240 }}
        />
      )}
      <Select
        allowClear
        placeholder="Location"
        aria-label="Location"
        style={{ width: 150 }}
        value={value.location_id}
        options={options?.locations.map((o) => ({ value: o.id, label: o.name }))}
        onChange={(location_id) => onChange({ ...value, location_id })}
      />
      <Select
        allowClear
        placeholder="Department"
        aria-label="Department"
        style={{ width: 160 }}
        value={value.department_id}
        options={options?.departments.map((o) => ({ value: o.id, label: o.name }))}
        onChange={(department_id) => onChange({ ...value, department_id })}
      />
      <Select
        allowClear
        placeholder="Level"
        aria-label="Level"
        style={{ width: 110 }}
        value={value.level}
        options={options?.levels.map((level) => ({ value: level, label: level }))}
        onChange={(level) => onChange({ ...value, level })}
      />
    </>
  );
}
