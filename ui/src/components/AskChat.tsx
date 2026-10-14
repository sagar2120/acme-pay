import { Button, Input } from "antd";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { askAboutPay, type Answer, type AskFilters } from "../api";
import { formatMoney } from "../lib/money";
import { toQueryString } from "../lib/query";

type Message =
  | { from: "you"; text: string }
  | { from: "acme"; text: string; filters?: AskFilters }
  | { from: "acme"; text: string; refused: true };

const WELCOME =
  "Ask about pay in plain words, e.g. what do we pay in Pune by level, or compare departments in London.";

/**
 * Looks like a chat, behaves like a filter. Each reply is the database's own
 * summary for the filters the AI chose; the AI never writes a number or a
 * sentence of its own. "Show on page" opens the full table.
 */
export function AskChat() {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState<Message[]>([{ from: "acme", text: WELCOME }]);
  const bottom = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottom.current?.scrollIntoView({ block: "end" });
  }, [messages, open]);

  const send = async () => {
    const asked = question.trim();
    if (asked.length < 3 || busy) return;
    setQuestion("");
    setMessages((m) => [...m, { from: "you", text: asked }]);
    setBusy(true);
    try {
      const answer = await askAboutPay(asked);
      setMessages((m) => [...m, { from: "acme", text: summarise(answer), filters: answer.filters }]);
    } catch (error) {
      setMessages((m) => [...m, { from: "acme", text: (error as Error).message, refused: true }]);
    } finally {
      setBusy(false);
    }
  };

  const showOnPage = (filters: AskFilters) => {
    navigate(
      `/${toQueryString({
        group_by: filters.group_by,
        location_id: filters.location_id ?? undefined,
        department_id: filters.department_id ?? undefined,
        level: filters.level ?? undefined,
      })}`,
    );
    setOpen(false);
  };

  return (
    <>
      <button
        type="button"
        className="chat-launcher"
        aria-label={open ? "Close pay questions" : "Ask about pay"}
        onClick={() => setOpen((o) => !o)}
      >
        {open ? "×" : "?"}
      </button>

      {open && (
        <section className="chat" aria-label="Pay questions">
          <header className="chat-head">
            <strong>Ask about pay</strong>
            <span>The AI picks the filters; the numbers are the database's.</span>
          </header>
          <div className="chat-body">
            {messages.map((m, i) => (
              <div key={i} className={`bubble ${m.from}${"refused" in m ? " refused" : ""}`}>
                <p>{m.text}</p>
                {"filters" in m && m.filters && (
                  <Button size="small" onClick={() => showOnPage(m.filters!)}>
                    Show on page
                  </Button>
                )}
              </div>
            ))}
            {busy && <div className="bubble acme thinking">Looking it up…</div>}
            <div ref={bottom} />
          </div>
          <footer className="chat-foot">
            <Input
              placeholder="Type a question"
              aria-label="Your question"
              maxLength={500}
              value={question}
              disabled={busy}
              onChange={(e) => setQuestion(e.target.value)}
              onPressEnter={send}
            />
            <Button type="primary" onClick={send} loading={busy}>
              Send
            </Button>
          </footer>
        </section>
      )}
    </>
  );
}

function summarise({ filters, summary }: Answer): string {
  const where = [filters.location_name, filters.department_name, filters.level].filter(Boolean).join(", ") || "All of ACME";
  const o = summary.overall;
  const usd = (v: string) => formatMoney(v, "USD");
  const top = summary.groups[0];
  const topLine =
    summary.groups.length > 1 && top
      ? ` Highest median by ${filters.group_by}: ${top.name} at ${usd(top.median_usd)}.`
      : "";
  return `${where}, by ${filters.group_by}: ${o.headcount.toLocaleString("en-US")} people, median ${usd(o.median_usd)}, middle half ${usd(o.p25_usd)} to ${usd(o.p75_usd)}.${topLine}`;
}
