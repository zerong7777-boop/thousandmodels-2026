import { Button, Card, List, Space, Typography } from "antd";
import { useEffect, useState } from "react";
import { api } from "../api";
import { MetricSummary } from "../components/MetricSummary";
import type { ReviewReport } from "../types";

interface ReviewCenterPageProps {
  eventId: string;
}

export function ReviewCenterPage({ eventId }: ReviewCenterPageProps) {
  const [report, setReport] = useState<ReviewReport | null>(null);

  const load = async () => {
    try {
      setReport(await api.getReviewReport(eventId));
    } catch {
      setReport(await api.generateReport(eventId));
    }
  };

  useEffect(() => {
    load();
  }, [eventId]);

  return (
    <Space orientation="vertical" size={16} className="full-width">
      <Typography.Title level={2}>复盘中心</Typography.Title>
      <Button onClick={load}>生成/刷新复盘报告</Button>
      <MetricSummary report={report} />
      <Card title="复盘摘要">
        <Typography.Paragraph>{report?.summary || "暂无复盘报告。"}</Typography.Paragraph>
        <Typography.Paragraph>{report?.incident_summary}</Typography.Paragraph>
      </Card>
      <Card title="指标驱动经验">
        <List
          dataSource={report?.lessons_learned || []}
          renderItem={(item) => <List.Item>{item}</List.Item>}
        />
      </Card>
      <Card title="下次活动建议">
        <List
          dataSource={report?.next_event_recommendations || []}
          renderItem={(item) => <List.Item>{item}</List.Item>}
        />
      </Card>
    </Space>
  );
}
