import { Button, Layout, Menu, Space, Tag, Typography } from "antd";
import { Bell, ClipboardList, LogOut, Store, ToggleLeft } from "lucide-react";
import type { ReactNode } from "react";
import type { DemoSession } from "../auth/session";

const { Header, Content, Sider } = Layout;

interface MerchantShellProps {
  activeKey: string;
  title: string;
  session: DemoSession;
  onNavigate: (path: string) => void;
  onLogout: () => void;
  children: ReactNode;
}

const link = (href: string, label: string) => <a href={href}>{label}</a>;

export function MerchantShell({ activeKey, title, session, onLogout, children }: MerchantShellProps) {
  return (
    <Layout className="app-layout merchant-layout" data-testid="merchant-shell">
      <Sider breakpoint="lg" collapsedWidth="0" className="app-sider">
        <div className="brand-block">
          <Typography.Title level={4}>Merchant Portal</Typography.Title>
          <Typography.Text>Today tasks and status</Typography.Text>
        </div>
        <Menu
          theme="dark"
          selectedKeys={[activeKey]}
          items={[
            {
              key: "dashboard",
              icon: <Store size={18} />,
              label: link("/merchant/dashboard", "Workbench")
            },
            {
              key: "tasks",
              icon: <ClipboardList size={18} />,
              label: link("/merchant/events/demo-night-tour/tasks", "Tasks")
            },
            {
              key: "status",
              icon: <ToggleLeft size={18} />,
              label: link("/merchant/events/demo-night-tour/status", "Runtime Status")
            },
            {
              key: "notices",
              icon: <Bell size={18} />,
              label: link("/merchant/notifications", "Notices")
            }
          ]}
        />
      </Sider>
      <Layout>
        <Header className="app-header">
          <Space orientation="vertical" size={2} className="full-width">
            <Space wrap>
              <Typography.Title level={3}>{title}</Typography.Title>
              <Tag color="blue">Merchant</Tag>
              <Tag>{session.display_name}</Tag>
              <Button icon={<LogOut size={14} />} onClick={onLogout}>
                Logout
              </Button>
            </Space>
            <Typography.Text type="secondary">
              Lightweight execution surface for assigned tasks and runtime reports.
            </Typography.Text>
          </Space>
        </Header>
        <Content className="app-content">{children}</Content>
      </Layout>
    </Layout>
  );
}
