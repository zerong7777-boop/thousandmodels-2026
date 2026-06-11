import { Card, List, Space, Tag, Typography } from "antd";
import type { PlanVersion } from "../types";

interface PlanVersionDiffProps {
  plan?: PlanVersion | null;
}

export function PlanVersionDiff({ plan }: PlanVersionDiffProps) {
  if (!plan) {
    return (
      <Card title="方案版本">
        <Typography.Text type="secondary">暂无方案版本。</Typography.Text>
      </Card>
    );
  }

  const diff = plan.diff_from_previous.length
    ? plan.diff_from_previous
    : ["初始方案，无上一版本差异"];

  return (
    <Card
      title={
        <Space>
          <span>方案版本</span>
          <Tag color={plan.status === "approved" ? "green" : "blue"}>v{plan.version}</Tag>
          <Tag>{plan.status}</Tag>
        </Space>
      }
    >
      <List
        size="small"
        dataSource={diff}
        renderItem={(item) => <List.Item>{item}</List.Item>}
      />
      {plan.approved_by && (
        <Typography.Text type="secondary">
          {plan.approved_by} 于 {plan.approved_at} 确认
        </Typography.Text>
      )}
    </Card>
  );
}
