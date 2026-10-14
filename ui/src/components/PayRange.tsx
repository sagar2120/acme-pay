import { formatMoney } from "../lib/money";

type Props = { lowest: number; median: number; highest: number; scaleMax: number };

/** Lowest-to-highest pay as a line, median as a dot, on a scale shared by every row. */
export function PayRange({ lowest, median, highest, scaleMax }: Props) {
  const at = (usd: number) => `${(usd / scaleMax) * 100}%`;
  const label = `Lowest ${formatMoney(lowest, "USD")}, median ${formatMoney(median, "USD")}, highest ${formatMoney(highest, "USD")}`;
  return (
    <div className="range" role="img" aria-label={label} title={label}>
      <div className="track" style={{ left: at(lowest), width: `calc(${at(highest)} - ${at(lowest)})` }} />
      <div className="median" style={{ left: at(median) }} />
    </div>
  );
}
