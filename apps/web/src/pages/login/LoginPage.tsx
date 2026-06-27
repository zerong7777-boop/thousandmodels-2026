import { Alert, Button, Card, Form, Input, Space, Typography } from "antd";
import { Building2, Map, Store } from "lucide-react";
import { useState, type ReactNode } from "react";
import { isDemoMode } from "../../api";
import { useAuth } from "../../auth/AuthProvider";
import { defaultPathForRole } from "../../auth/roleRouting";
import { LanguageSwitcher, useI18n } from "../../i18n";
import type { UserRole } from "../../types";

interface LoginPageProps {
  onNavigate: (path: string) => void;
}

interface DemoCredential {
  role: UserRole;
  labelKey: string;
  productLabelKey: string;
  descriptionKey: string;
  icon: ReactNode;
  username: string;
  password: string;
}

const demoCredentials: DemoCredential[] = [
  {
    role: "organizer",
    labelKey: "auth.organizerDemo",
    productLabelKey: "auth.organizerWorkspace",
    descriptionKey: "auth.organizerDescription",
    icon: <Building2 size={20} />,
    username: "organizer.demo",
    password: "demo1234"
  },
  {
    role: "merchant",
    labelKey: "auth.merchantDemo",
    productLabelKey: "auth.merchantWorkbench",
    descriptionKey: "auth.merchantDescription",
    icon: <Store size={20} />,
    username: "merchant.m001.demo",
    password: "demo1234"
  },
  {
    role: "tourist",
    labelKey: "auth.touristDemo",
    productLabelKey: "auth.visitorRoute",
    descriptionKey: "auth.visitorDescription",
    icon: <Map size={20} />,
    username: "tourist.demo",
    password: "demo1234"
  }
];

const roleColor: Record<UserRole, string> = {
  organizer: "#2f6f4f",
  merchant: "#2563eb",
  tourist: "#7c3aed"
};

export function LoginPage({ onNavigate }: LoginPageProps) {
  const { login } = useAuth();
  const { t } = useI18n();
  const demoMode = isDemoMode();
  const [form] = Form.useForm<{ username: string; password: string }>();
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const fillCredential = (credential: DemoCredential) => {
    form.setFieldsValue({ username: credential.username, password: credential.password });
    setError(null);
  };

  const submit = async (values: { username: string; password: string }) => {
    setSubmitting(true);
    setError(null);
    try {
      const user = await login(values.username, values.password);
      onNavigate(defaultPathForRole(user.role));
    } catch {
      setError(t("auth.invalidCredentials"));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="login-page bg-slate-100">
      <Card className="login-panel overflow-hidden border-0 shadow-xl">
        <div className="grid gap-0 lg:grid-cols-[minmax(0,1.05fr)_minmax(360px,0.95fr)]">
          <section className="bg-slate-950 p-7 text-white md:p-9">
            <div className="mb-5 flex justify-end">
              <LanguageSwitcher />
            </div>
            <p className="text-xs font-semibold uppercase tracking-normal text-teal-200">{t("auth.productAccess")}</p>
            <Typography.Title level={1} style={{ color: "white", margin: "8px 0 0" }}>
              {t("common.brand")}
            </Typography.Title>
            <p className="mt-3 max-w-xl text-sm leading-6 text-slate-300">{t("auth.productPurpose")}</p>

            {demoMode ? (
              <div className="mt-8 grid gap-3">
                {demoCredentials.map((credential) => (
                  <button
                    key={credential.role}
                    className="flex items-center gap-3 rounded-lg border border-white/10 bg-white/5 p-4 text-left transition hover:bg-white/10"
                    onClick={() => fillCredential(credential)}
                    type="button"
                  >
                    <span
                      className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-white text-slate-900"
                      style={{ color: roleColor[credential.role] }}
                    >
                      {credential.icon}
                    </span>
                    <span className="min-w-0">
                      <span className="block text-sm font-semibold text-white">{t(credential.productLabelKey)}</span>
                      <span className="mt-1 block text-xs leading-5 text-slate-300">{t(credential.descriptionKey)}</span>
                    </span>
                  </button>
                ))}
              </div>
            ) : null}

            <dl className="mt-8 grid gap-3 text-sm text-slate-300 sm:grid-cols-3">
              <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                <dt className="font-semibold text-white">{t("auth.operatorSummaryTitle")}</dt>
                <dd className="mt-1">{t("auth.operatorSummaryBody")}</dd>
              </div>
              <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                <dt className="font-semibold text-white">{t("auth.merchantSummaryTitle")}</dt>
                <dd className="mt-1">{t("auth.merchantSummaryBody")}</dd>
              </div>
              <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                <dt className="font-semibold text-white">{t("auth.visitorSummaryTitle")}</dt>
                <dd className="mt-1">{t("auth.visitorSummaryBody")}</dd>
              </div>
            </dl>
          </section>

          <section className="p-7 md:p-9">
            <Space orientation="vertical" size={20} className="full-width">
              <Space orientation="vertical" size={4}>
                <Typography.Title level={2} style={{ margin: 0 }}>
                  {t("auth.productAccess")}
                </Typography.Title>
                {demoMode ? <Typography.Text type="secondary">{t("auth.demoCredentialsHint")}</Typography.Text> : null}
              </Space>

              <Form form={form} layout="vertical" onFinish={submit} requiredMark={false}>
                <Form.Item
                  label={t("auth.username")}
                  name="username"
                  rules={[{ required: true, message: t("auth.usernameRequired") }]}
                >
                  <Input autoComplete="username" />
                </Form.Item>
                <Form.Item
                  label={t("auth.password")}
                  name="password"
                  rules={[{ required: true, message: t("auth.passwordRequired") }]}
                >
                  <Input.Password autoComplete="current-password" />
                </Form.Item>
                {error ? <Alert type="error" showIcon message={error} /> : null}
                <Button type="primary" htmlType="submit" loading={submitting} block className="mt-16">
                  {t("auth.signIn")}
                </Button>
              </Form>

              {demoMode ? (
                <div>
                  <Typography.Text type="secondary">{t("auth.demoQuickFill")}</Typography.Text>
                  <div className="mt-3 grid gap-2">
                    {demoCredentials.map((credential) => (
                      <Button
                        key={credential.role}
                        className="login-demo-button flex h-auto w-full justify-start py-2 text-left"
                        onClick={() => fillCredential(credential)}
                        style={{ borderColor: roleColor[credential.role] }}
                      >
                        <Space>
                          {credential.icon}
                          <span>
                            {t(credential.labelKey)}
                            <span className="ml-2 text-slate-500">{credential.username}</span>
                          </span>
                        </Space>
                      </Button>
                    ))}
                  </div>
                </div>
              ) : null}
            </Space>
          </section>
        </div>
      </Card>
    </main>
  );
}
