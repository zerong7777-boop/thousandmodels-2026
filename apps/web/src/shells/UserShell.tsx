import { Button, Layout, Space, Tag, Typography } from "antd";
import { LogOut } from "lucide-react";
import type { ReactNode } from "react";
import type { DemoSession } from "../auth/session";

const { Header, Content } = Layout;

interface UserShellProps {
  title: string;
  session: DemoSession;
  onNavigate: (path: string) => void;
  onLogout: () => void;
  children: ReactNode;
}

export function UserShell({ title, session, onLogout, children }: UserShellProps) {
  return (
    <Layout className="user-layout" data-testid="user-shell">
      <Header className="app-header">
        <Space orientation="vertical" size={2} className="full-width">
          <Space wrap>
            <Typography.Title level={3}>{title}</Typography.Title>
            <Tag color="green">Visitor</Tag>
            <Tag>{session.display_name}</Tag>
            <Button icon={<LogOut size={14} />} onClick={onLogout}>
              Logout
            </Button>
          </Space>
          <Typography.Text type="secondary">Route stories, tasks, and notices for visitors.</Typography.Text>
        </Space>
      </Header>
      <Content className="app-content">{children}</Content>
    </Layout>
  );
}
