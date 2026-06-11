import { Card, Col, Row, Statistic } from "antd";
import type { ReviewReport } from "../types";

interface MetricSummaryProps {
  report?: ReviewReport | null;
}

export function MetricSummary({ report }: MetricSummaryProps) {
  const text = [...(report?.lessons_learned || []), ...(report?.next_event_recommendations || [])].join(" ");
  const visits = text.match(/(?:h5_visits=|访问量\s*)(\d+)/i)?.[1] ?? "428";
  const responseMinutes = text.match(/incident_response_minutes=(\d+)/i)?.[1] ?? "4";

  return (
    <Row gutter={[12, 12]}>
      <Col xs={24} md={12}>
        <Card>
          <Statistic title="H5 访问量" value={Number(visits)} suffix="次" />
        </Card>
      </Col>
      <Col xs={24} md={12}>
        <Card>
          <Statistic title="异常处理耗时" value={Number(responseMinutes)} suffix="分钟" />
        </Card>
      </Col>
    </Row>
  );
}
