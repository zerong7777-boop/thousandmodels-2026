import { Layout, Menu, Space, Tag, Typography } from "antd";
import {
  AlertTriangle,
  BarChart3,
  CalendarDays,
  ClipboardList,
  LayoutDashboard,
  Smartphone,
  Store
} from "lucide-react";
import type { ReactNode } from "react";

const { Header, Content, Sider } = Layout;

interface AppShellProps {
  activeKey: string;
  title: string;
  children: ReactNode;
}

const link = (href: string, label: string) => <a href={href}>{label}</a>;

export function AppShell({ activeKey, title, children }: AppShellProps) {
  return (
    <Layout className="app-layout">
      <Sider breakpoint="lg" collapsedWidth="0" className="app-sider">
        <div className="brand-block">
          <Typography.Title level={4}>智引濠江</Typography.Title>
          <Typography.Text>旧区活动运营</Typography.Text>
        </div>
        <Menu
          theme="dark"
          selectedKeys={[activeKey]}
          items={[
            {
              key: "organizer",
              icon: <LayoutDashboard size={18} />,
              label: link("/organizer", "活动运营")
            },
            {
              key: "workspace",
              icon: <ClipboardList size={18} />,
              label: link("/organizer/events/demo-night-tour", "活动工作区")
            },
            {
              key: "exceptions",
              icon: <AlertTriangle size={18} />,
              label: link("/organizer/events/demo-night-tour/exceptions", "异常中心")
            },
            {
              key: "merchant",
              icon: <Store size={18} />,
              label: link("/merchant/m001", "商户工作台")
            },
            {
              key: "public",
              icon: <Smartphone size={18} />,
              label: link("/public/events/demo-night-tour", "游客入口")
            },
            {
              key: "review",
              icon: <BarChart3 size={18} />,
              label: link("/review/demo-night-tour", "复盘中心")
            }
          ]}
        />
      </Sider>
      <Layout>
        <Header className="app-header">
          <Space orientation="vertical" size={2}>
            <Space wrap>
              <Typography.Title level={3}>{title}</Typography.Title>
              <Tag color="green">福隆新街-新马路-内港</Tag>
              <Tag icon={<CalendarDays size={13} />}>2026-07-18 18:00-21:30</Tag>
            </Space>
            <Typography.Text type="secondary">
              旧区文旅活动编排与运行协同
            </Typography.Text>
          </Space>
        </Header>
        <Content className="app-content">{children}</Content>
      </Layout>
    </Layout>
  );
}
