import { Alert, Button, Table } from "antd";
import type { SorterResult } from "antd/es/table/interface";
import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useApi, type EmployeePage, type EmployeeRow, type Filters, type Options } from "../api";
import { FilterBar } from "../components/FilterBar";
import { PayChangeDrawer } from "../components/PayChangeDrawer";
import { filtersFrom } from "../lib/filters";
import { formatMoney } from "../lib/money";
import { toQueryString } from "../lib/query";

const PAGE_SIZE = 50;
const SORT_FIELD: Record<string, string> = { full_name: "name", pay_usd: "pay_usd" };

export function People() {
  const [params, setParams] = useSearchParams();
  const [editing, setEditing] = useState<EmployeeRow | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  const filters = filtersFrom(params);
  const page = Number(params.get("page")) || 1;
  const sort = params.get("sort") || "name";

  const options = useApi<Options>("/api/options");
  const people = useApi<EmployeePage>(
    `/api/employees${toQueryString({ ...filters, sort, page, page_size: PAGE_SIZE })}`,
    reloadKey,
  );

  // A filter change starts again at page 1; sorting and paging keep the filters.
  const show = (next: Filters, nextSort = sort, nextPage = 1) =>
    setParams(new URLSearchParams(toQueryString({ ...next, sort: nextSort, page: nextPage })));

  const sortOrder = (field: string) =>
    sort === SORT_FIELD[field] ? "ascend" : sort === `-${SORT_FIELD[field]}` ? "descend" : null;

  return (
    <>
      <h1>People</h1>
      <p className="overall">
        {people.data ? (
          <>
            <strong>{people.data.total.toLocaleString("en-US")}</strong> people match. Pay is current annual base pay.
          </>
        ) : (
          " "
        )}
      </p>

      <div className="toolbar">
        <FilterBar withSearch options={options.data} value={filters} onChange={(next) => show(next)} />
      </div>

      {people.error && <Alert type="error" showIcon message={people.error} style={{ marginBottom: 16 }} />}

      <Table<EmployeeRow>
        rowKey="id"
        size="middle"
        loading={people.loading}
        dataSource={people.data?.items}
        locale={{ emptyText: "No people match these filters." }}
        pagination={{
          current: page,
          pageSize: PAGE_SIZE,
          total: people.data?.total,
          showSizeChanger: false,
        }}
        onChange={(pagination, _filters, sorter) => {
          const { field, order } = sorter as SorterResult<EmployeeRow>;
          const key = SORT_FIELD[String(field)];
          const nextSort = key && order ? (order === "descend" ? `-${key}` : key) : "name";
          show(filters, nextSort, nextSort === sort ? (pagination.current ?? 1) : 1);
        }}
        columns={[
          { title: "ID", dataIndex: "id", render: (id: string) => <span style={{ color: "#5E6B67" }}>{id}</span> },
          { title: "Name", dataIndex: "full_name", sorter: true, sortOrder: sortOrder("full_name") },
          { title: "Job title", dataIndex: "job_title" },
          { title: "Level", dataIndex: "level" },
          { title: "Location", dataIndex: "location" },
          { title: "Department", dataIndex: "department" },
          {
            title: "Pay (local)",
            key: "pay_local",
            className: "money",
            render: (_, p) => formatMoney(p.pay_amount, p.pay_currency ?? ""),
          },
          {
            title: "Pay (USD)",
            dataIndex: "pay_usd",
            className: "money",
            sorter: true,
            sortOrder: sortOrder("pay_usd"),
            render: (v: string | null) => formatMoney(v, "USD"),
          },
          {
            title: "",
            key: "action",
            render: (_, p) => (
              <Button type="link" onClick={() => setEditing(p)}>
                Record a pay change
              </Button>
            ),
          },
        ]}
      />

      <PayChangeDrawer
        person={editing}
        onClose={() => setEditing(null)}
        onSaved={() => setReloadKey((key) => key + 1)}
      />
    </>
  );
}
