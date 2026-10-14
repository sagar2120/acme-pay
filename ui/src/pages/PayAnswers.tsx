import { Alert, Segmented, Table } from "antd";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useApi, type Filters, type GroupBy, type Options, type PayGroup, type PaySummary } from "../api";
import { AskBox } from "../components/AskBox";
import { FilterBar } from "../components/FilterBar";
import { PayRange } from "../components/PayRange";
import { filtersFrom } from "../lib/filters";
import { formatMoney } from "../lib/money";
import { toQueryString } from "../lib/query";

const GROUPINGS: { label: string; value: GroupBy }[] = [
  { label: "Location", value: "location" },
  { label: "Department", value: "department" },
  { label: "Level", value: "level" },
];

const usd = (amount: string) => formatMoney(amount, "USD");
const millions = (amount: string) => `$${(Number(amount) / 1_000_000).toFixed(1)}M`;

export function PayAnswers() {
  const [params, setParams] = useSearchParams();
  const navigate = useNavigate();
  const groupBy = (params.get("group_by") as GroupBy) || "location";
  const filters = filtersFrom(params);

  const options = useApi<Options>("/api/options");
  const summary = useApi<PaySummary>(`/api/pay/summary${toQueryString({ group_by: groupBy, ...filters })}`);

  const show = (next: Filters, grouping: GroupBy = groupBy) =>
    setParams(new URLSearchParams(toQueryString({ group_by: grouping, ...next })));

  // Clicking a group opens the People list narrowed to that group.
  const openPeople = (group: PayGroup) => {
    const narrowed = { ...filters };
    if (groupBy === "level") narrowed.level = group.name;
    if (groupBy === "location")
      narrowed.location_id = options.data?.locations.find((o) => o.name === group.name)?.id;
    if (groupBy === "department")
      narrowed.department_id = options.data?.departments.find((o) => o.name === group.name)?.id;
    navigate(`/people${toQueryString(narrowed)}`);
  };

  const overall = summary.data?.overall;
  const scaleMax = Math.max(1, ...(summary.data?.groups.map((g) => Number(g.max_usd)) ?? []));

  return (
    <>
      <h1>What does ACME pay?</h1>
      <p className="overall">
        {overall ? (
          <>
            <strong>{overall.headcount.toLocaleString("en-US")}</strong> people ·{" "}
            <strong>{millions(overall.payroll_usd)}</strong> annual payroll · median pay{" "}
            <strong>{usd(overall.median_usd)}</strong>; the middle half earn{" "}
            <strong>{usd(overall.p25_usd)}</strong> to <strong>{usd(overall.p75_usd)}</strong>. All figures are
            annual base pay in USD.
            <br />
            <span className="legend">Pay spread: line from lowest to highest, band for the middle half, dot at the median.</span>
          </>
        ) : (
          " "
        )}
      </p>

      <AskBox
        onReset={() => show({}, "location")}
        onAnswered={(picked) =>
          show(
            {
              location_id: picked.location_id ?? undefined,
              department_id: picked.department_id ?? undefined,
              level: picked.level ?? undefined,
            },
            picked.group_by,
          )
        }
      />

      <div className="toolbar">
        <Segmented
          options={GROUPINGS}
          value={groupBy}
          onChange={(value) => show(filters, value as GroupBy)}
          aria-label="Group by"
        />
        <FilterBar options={options.data} value={filters} onChange={(next) => show(next)} />
      </div>

      {summary.error && <Alert type="error" showIcon message={summary.error} style={{ marginBottom: 16 }} />}

      <Table<PayGroup>
        rowKey="name"
        loading={summary.loading}
        dataSource={summary.data?.groups}
        pagination={false}
        locale={{ emptyText: "No people match these filters." }}
        onRow={(group) => ({ onClick: () => openPeople(group), style: { cursor: "pointer" } })}
        columns={[
          { title: GROUPINGS.find((g) => g.value === groupBy)!.label, dataIndex: "name" },
          { title: "People", dataIndex: "headcount", className: "money", render: (n: number) => n.toLocaleString("en-US") },
          { title: "Payroll", dataIndex: "payroll_usd", className: "money", render: millions },
          {
            title: "Pay spread",
            key: "range",
            width: "28%",
            render: (_, g) => (
              <PayRange
                lowest={Number(g.min_usd)}
                p25={Number(g.p25_usd)}
                median={Number(g.median_usd)}
                p75={Number(g.p75_usd)}
                highest={Number(g.max_usd)}
                scaleMax={scaleMax}
              />
            ),
          },
          { title: "Lowest", dataIndex: "min_usd", className: "money", render: usd },
          { title: "25th pct", dataIndex: "p25_usd", className: "money", render: usd },
          { title: "Median", dataIndex: "median_usd", className: "money", render: (v: string) => <strong>{usd(v)}</strong> },
          { title: "75th pct", dataIndex: "p75_usd", className: "money", render: usd },
          { title: "Highest", dataIndex: "max_usd", className: "money", render: usd },
        ]}
      />
    </>
  );
}
