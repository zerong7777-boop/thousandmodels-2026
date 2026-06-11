import { Button, Card, List, Space, Tag, Typography } from "antd";
import type { Incident } from "../types";

interface IncidentQueueProps {
  incidents: Incident[];
  onCreateProposal?: (incidentId: string) => void;
}

export function IncidentQueue({ incidents, onCreateProposal }: IncidentQueueProps) {
  return (
    <Card title="Incident 队列">
      {incidents.length === 0 ? (
        <Typography.Text type="secondary">暂无异常。商户上报库存或排队状态后会生成 Incident。</Typography.Text>
      ) : (
        <List
          dataSource={incidents}
          renderItem={(incident) => (
            <List.Item
              actions={[
                <Button key="proposal" size="small" onClick={() => onCreateProposal?.(incident.incident_id)}>
                  生成恢复方案
                </Button>
              ]}
            >
              <Space orientation="vertical" size={4}>
                <Space wrap>
                  <Tag color={incident.severity === "high" ? "red" : "gold"}>{incident.type}</Tag>
                  <Tag>{incident.status}</Tag>
                  <Typography.Text>{incident.trigger_detail}</Typography.Text>
                </Space>
                <Typography.Text type="secondary">
                  影响商户：{incident.affected_merchants.join(", ") || "-"} / 路线点：
                  {incident.affected_route_points.join(", ") || "-"}
                </Typography.Text>
              </Space>
            </List.Item>
          )}
        />
      )}
    </Card>
  );
}
