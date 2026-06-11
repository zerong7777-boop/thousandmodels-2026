import { Button, Layout, Menu, Space, Tag, Typography } from "antd";
import { AlertTriangle, BarChart3, ClipboardList, LayoutDashboard, LogOut } from "lucide-react";
import type { ReactNode } from "react";
import type { DemoSession } from "../auth/session";

const { Header, Content, Sider } = Layout;

interface OrganizerShellProps {
  activeKey: string;
  title: string;
  session: DemoSession;
  onNavigate: (path: string) => void;
  onLogout: () => void;
  children: ReactNode;
}

const link = (href: string, label: string) => <a href={href}>{label}</a>;

export function OrganizerShell({ activeKey, title, session, onLogout, children }: OrganizerShellProps) {
  return (
    <Layout className="app-layout" data-testid="organizer-shell">
      <Sider breakpoint="lg" collapsedWidth="0" className="app-sider">
        <div className="brand-block">
          <Typography.Title level={4}>Zhiyin Haojiang</Typography.Title>
          <Typography.Text>Organizer operations</Typography.Text>
        </div>
        <Menu
          theme="dark"
          selectedKeys={[activeKey]}
          items={[
            {
              key: "dashboard",
              icon: <LayoutDashboard size={18} />,
              label: link("/organizer/dashboard", "Operations Dashboard")
            },
            {
              key: "workspace",
              icon: <ClipboardList size={18} />,
              label: link("/organizer/events/demo-night-tour", "Activity Workspace")
            },
            {
              key: "exceptions",
              icon: <AlertTriangle size={18} />,
              label: link("/organizer/events/demo-night-tour/exceptions", "Exception Center")
            },
            {
              key: "review",
              icon: <BarChart3 size={18} />,
              label: link("/organizer/events/demo-night-tour/review", "Review Center")
            }
          ]}
        />
      </Sider>
      <Layout>
        <Header className="app-header">
          <Space orientation="vertical" size={2} className="full-width">
            <Space wrap>
              <Typography.Title level={3}>{title}</Typography.Title>
              <Tag color="green">Organizer</Tag>
              <Tag>{session.display_name}</Tag>
              <Button icon={<LogOut size={14} />} onClick={onLogout}>
                Logout
              </Button>
            </Space>
            <Typography.Text type="secondary">
              Event operations, approvals, exceptions, recovery, and review.
            </Typography.Text>
          </Space>
        </Header>
        <Content className="app-content">{children}</Content>
      </Layout>
    </Layout>
  );
}
