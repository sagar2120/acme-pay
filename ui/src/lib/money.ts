const SYMBOL: Record<string, string> = { INR: "₹", USD: "$", EUR: "€", GBP: "£", SGD: "S$" };

// Indian grouping (18,00,000) only for rupees; everyone else groups in thousands.
const INDIAN = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 });
const WESTERN = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });

export function formatMoney(amount: string | number | null, currency: string): string {
  if (amount === null) return "—";
  const grouping = currency === "INR" ? INDIAN : WESTERN;
  return `${SYMBOL[currency] ?? `${currency} `}${grouping.format(Number(amount))}`;
}
