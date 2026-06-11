import { Card, Descriptions, Empty, List, Space, Tag, Timeline, Typography } from "antd";
import type { EventPlan } from "../types";

export function EventPlanView({ plan }: { plan: EventPlan | null }) {
  if (!plan) {
    return (
      <Card title="AI 活动方案">
        <Empty description="尚未生成方案" />
      </Card>
    );
  }

  const budget = plan.budget_plan;
  return (
    <Card title="AI 活动方案" extra={<Tag color={plan.approval_status === "approved" ? "green" : "gold"}>{plan.approval_status}</Tag>}>
      <Space orientation="vertical" size="middle" className="full-width">
        <Typography.Title level={4}>{plan.theme}</Typography.Title>
        <Typography.Paragraph>{plan.narrative}</Typography.Paragraph>
        <Descriptions size="small" bordered column={{ xs: 1, md: 2 }}>
          <Descriptions.Item label="总预算">MOP {budget.total_mop.toLocaleString()}</Descriptions.Item>
          <Descriptions.Item label="宣传">MOP {budget.marketing_mop.toLocaleString()}</Descriptions.Item>
          <Descriptions.Item label="商户支持">MOP {budget.merchant_support_mop.toLocaleString()}</Descriptions.Item>
          <Descriptions.Item label="应急">MOP {budget.contingency_mop.toLocaleString()}</Descriptions.Item>
        </Descriptions>
        <Timeline items={plan.schedule.map((item) => ({ children: item }))} />
        <List
          size="small"
          header="风险预案"
          dataSource={plan.risk_plan}
          renderItem={(risk) => (
            <List.Item>
              <Space orientation="vertical" size={2}>
                <Space wrap>
                  <Tag color={risk.level === "high" ? "red" : "gold"}>{risk.level}</Tag>
                  <Typography.Text strong>{risk.description}</Typography.Text>
                </Space>
                <Typography.Text type="secondary">{risk.mitigation}</Typography.Text>
              </Space>
            </List.Item>
          )}
        />
      </Space>
    </Card>
  );
}
