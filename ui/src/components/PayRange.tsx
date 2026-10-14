import { formatMoney } from "../lib/money";

type Props = { lowest: number; p25: number; median: number; p75: number; highest: number; scaleMax: number };

/**
 * One group's pay on a scale shared by every row: a thin line from lowest to
 * highest, a thicker band for the middle half (25th to 75th percentile), and
 * a dot at the median.
 */
export function PayRange({ lowest, p25, median, p75, highest, scaleMax }: Props) {
  const at = (usd: number) => `${(usd / scaleMax) * 100}%`;
  const span = (from: number, to: number) => ({ left: at(from), width: `calc(${at(to)} - ${at(from)})` });
  const label = `Lowest ${formatMoney(lowest, "USD")}, middle half ${formatMoney(p25, "USD")} to ${formatMoney(p75, "USD")}, median ${formatMoney(median, "USD")}, highest ${formatMoney(highest, "USD")}`;
  return (
    <div className="range" role="img" aria-label={label} title={label}>
      <div className="track" style={span(lowest, highest)} />
      <div className="middle-half" style={span(p25, p75)} />
      <div className="median" style={{ left: at(median) }} />
    </div>
  );
}
