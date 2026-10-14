import { Alert, App, Button, DatePicker, Drawer, Form, Input, InputNumber } from "antd";
import dayjs, { type Dayjs } from "dayjs";
import { useEffect, useState } from "react";
import { recordPayChange, useApi, type EmployeeDetail, type EmployeeRow } from "../api";
import { formatMoney } from "../lib/money";

type Props = { person: EmployeeRow | null; onClose: () => void; onSaved: () => void };
type FormValues = { amount: number; effective_from: Dayjs; note?: string };

export function PayChangeDrawer({ person, onClose, onSaved }: Props) {
  const { message } = App.useApp();
  const [form] = Form.useForm<FormValues>();
  const [refusal, setRefusal] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);
  const detail = useApi<EmployeeDetail>(person ? `/api/employees/${person.id}` : null, reloadKey);

  useEffect(() => {
    form.resetFields();
    setRefusal(null);
  }, [person, form]);

  const save = async (values: FormValues) => {
    if (!person) return;
    setSaving(true);
    setRefusal(null);
    try {
      await recordPayChange(person.id, {
        amount: values.amount,
        effective_from: values.effective_from.format("YYYY-MM-DD"),
        note: values.note,
      });
      message.success(`Pay change saved for ${person.full_name}`);
      form.resetFields();
      setReloadKey((key) => key + 1);
      onSaved();
    } catch (error) {
      // The server explains which rule the change broke; show its words as they are.
      setRefusal((error as Error).message);
    } finally {
      setSaving(false);
    }
  };

  const currency = detail.data?.currency ?? person?.pay_currency ?? "";

  return (
    <Drawer
      open={person !== null}
      onClose={onClose}
      width={440}
      title={person ? `Record a pay change for ${person.full_name}` : ""}
      destroyOnClose
    >
      {person && (
        <>
          <p className="overall" style={{ marginBottom: 20 }}>
            {person.job_title}, {person.location}. Current pay{" "}
            <strong>{formatMoney(person.pay_amount, currency)}</strong> a year.
          </p>

          <Form<FormValues>
            form={form}
            layout="vertical"
            onFinish={save}
            initialValues={{ effective_from: dayjs() }}
            requiredMark={false}
          >
            <Form.Item
              label={`Annual amount (${currency})`}
              name="amount"
              rules={[{ required: true, message: "Enter the new annual amount." }]}
            >
              <InputNumber style={{ width: "100%" }} min={1} step={1000} />
            </Form.Item>
            <Form.Item label="Effective from" name="effective_from" rules={[{ required: true, message: "Pick a date." }]}>
              <DatePicker style={{ width: "100%" }} format="D MMM YYYY" />
            </Form.Item>
            <Form.Item label="Note" name="note">
              <Input.TextArea maxLength={500} rows={2} placeholder="Promotion, annual review, correction…" />
            </Form.Item>

            {refusal && <Alert type="error" showIcon message={refusal} style={{ marginBottom: 16 }} />}

            <Button type="primary" htmlType="submit" loading={saving}>
              Save pay change
            </Button>
          </Form>

          <h3 style={{ marginTop: 32, fontSize: 15 }}>Pay history</h3>
          <ul className="history">
            {detail.data?.pay_history.map((record) => (
              <li key={record.id}>
                <span>
                  {dayjs(record.effective_from).format("D MMM YYYY")}
                  {record.note && <span className="note"> · {record.note}</span>}
                </span>
                <span>{formatMoney(record.amount, record.currency)}</span>
              </li>
            ))}
          </ul>
        </>
      )}
    </Drawer>
  );
}
