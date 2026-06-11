import { Card, Empty, List, Space, Typography } from "antd";
import type { ReviewReport } from "../types";

export function ReviewReportPanel({ report }: { report: ReviewReport | null }) {
  return (
    <Card title="复盘报告">
      {!report ? (
        <Empty description="尚未生成复盘报告" />
      ) : (
        <Space orientation="vertical" size="middle" className="full-width">
          <Typography.Paragraph>{report.summary}</Typography.Paragraph>
          <Typography.Text>{report.route_result}</Typography.Text>
          <Typography.Text>{report.merchant_result}</Typography.Text>
          <Typography.Text>{report.incident_summary}</Typography.Text>
          <List size="small" header="经验沉淀" dataSource={report.lessons_learned} renderItem={(item) => <List.Item>{item}</List.Item>} />
          <List
            size="small"
            header="下次建议"
            dataSource={report.next_event_recommendations}
            renderItem={(item) => <List.Item>{item}</List.Item>}
          />
        </Space>
      )}
    </Card>
  );
}
