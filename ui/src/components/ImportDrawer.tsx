import { Alert, App, Button, Drawer, Table, Upload } from "antd";
import { useState } from "react";
import { importPayChanges, type ImportReport, type RowError } from "../api";

type Props = { open: boolean; onClose: () => void; onSaved: () => void };

const TEMPLATE = "employee_id,amount,effective_from,note\nACME-2021-00001,1900000,2026-04-01,Annual review\n";

export function ImportDrawer({ open, onClose, onSaved }: Props) {
  const { message } = App.useApp();
  const [report, setReport] = useState<ImportReport | null>(null);
  const [problem, setProblem] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const send = async (file: File) => {
    setBusy(true);
    setProblem(null);
    setReport(null);
    try {
      const result = await importPayChanges(file);
      setReport(result);
      if (result.saved > 0) {
        message.success(`${result.saved} pay changes saved`);
        onSaved();
      }
    } catch (error) {
      setProblem((error as Error).message);
    } finally {
      setBusy(false);
    }
    return false; // we upload ourselves; stop Ant Design from doing it too
  };

  const templateUrl = `data:text/csv;charset=utf-8,${encodeURIComponent(TEMPLATE)}`;

  return (
    <Drawer open={open} onClose={onClose} width={520} title="Import pay changes from a CSV file" destroyOnClose>
      <p className="overall" style={{ marginBottom: 12 }}>
        One row per pay change, with the columns <code>employee_id, amount, effective_from, note</code>. Amount is
        annual, in the person's local currency; the date is <code>YYYY-MM-DD</code>.{" "}
        <a href={templateUrl} download="pay-changes-template.csv">
          Download a template
        </a>
        .
      </p>
      <p className="overall">
        Every row is checked first. If any row has a problem, nothing is saved and the problem rows are listed
        here, so you can fix the file and upload it again.
      </p>

      <div className="drop-zone">
        <Upload.Dragger accept=".csv,text/csv" maxCount={1} showUploadList={false} beforeUpload={send} disabled={busy}>
          <p style={{ margin: 16 }}>{busy ? "Checking…" : "Drop a CSV file here, or click to choose one"}</p>
        </Upload.Dragger>
      </div>

      {problem && <Alert type="error" showIcon message={problem} style={{ marginTop: 16 }} />}

      {report && report.saved > 0 && (
        <Alert type="success" showIcon message={`${report.saved} pay changes saved.`} style={{ marginTop: 16 }} />
      )}

      {report && report.errors.length > 0 && (
        <>
          <Alert
            type="warning"
            showIcon
            message={`Nothing was saved. ${report.errors.length} row${report.errors.length === 1 ? "" : "s"} need fixing.`}
            style={{ marginTop: 16, marginBottom: 12 }}
          />
          <Table<RowError>
            size="small"
            rowKey="line"
            pagination={false}
            dataSource={report.errors}
            columns={[
              { title: "Line", dataIndex: "line", width: 70 },
              { title: "Employee", dataIndex: "employee_id", width: 160 },
              { title: "Problem", dataIndex: "error" },
            ]}
          />
        </>
      )}

      <Button onClick={onClose} style={{ marginTop: 24 }}>
        Close
      </Button>
    </Drawer>
  );
}
