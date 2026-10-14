import { Alert, Input } from "antd";
import { useState } from "react";
import { askAboutPay, type AskFilters } from "../api";

type Props = { onAnswered: (filters: AskFilters) => void };

const EXAMPLES = "e.g. what do we pay senior engineers in Pune, or compare departments in London";

/**
 * A question in plain words becomes the same filters as the controls below.
 * The language model only translates the question; the numbers shown are the
 * database's, exactly as they are for any filter.
 */
export function AskBox({ onAnswered }: Props) {
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<{ kind: "error" | "info"; text: string } | null>(null);

  const ask = async () => {
    const asked = question.trim();
    if (asked.length < 3) return;
    setBusy(true);
    setNote(null);
    try {
      const answer = await askAboutPay(asked);
      onAnswered(answer.filters);
      setNote({ kind: "info", text: `Showing ${describe(answer.filters)}. The figures come from the database, not the model.` });
    } catch (error) {
      setNote({ kind: "error", text: (error as Error).message });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="ask">
      <Input.Search
        size="large"
        placeholder={EXAMPLES}
        aria-label="Ask a question about pay"
        enterButton="Ask"
        loading={busy}
        maxLength={500}
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        onSearch={ask}
      />
      {note && <Alert type={note.kind} showIcon message={note.text} style={{ marginTop: 8 }} />}
    </div>
  );
}

function describe(filters: AskFilters): string {
  const parts = [`pay by ${filters.group_by}`];
  if (filters.location_name) parts.push(`in ${filters.location_name}`);
  if (filters.department_name) parts.push(`for ${filters.department_name}`);
  if (filters.level) parts.push(`at ${filters.level}`);
  return parts.join(" ");
}
