import { Alert, Button, Card, List, Space, Tag, Timeline, Typography, message } from "antd";
import { RefreshCw } from "lucide-react";
import { useState } from "react";
import { api } from "../api";
import type { PublicEvent } from "../types";

export function TouristPage() {
  const [event, setEvent] = useState<PublicEvent | null>(null);

  const refresh = async () => {
    try {
      setEvent(await api.getPublicEvent());
    } catch (error) {
      message.error(error instanceof Error ? error.message : "游客页面尚未发布");
    }
  };

  return (
    <div className="h5-frame">
      <Card
        title="游客 H5"
        extra={
          <Button icon={<RefreshCw size={16} />} onClick={refresh}>
            刷新游客页面
          </Button>
        }
      >
        {!event ? (
          <Alert type="info" showIcon message="路线待发布" />
        ) : (
          <Space orientation="vertical" size="middle" className="full-width">
            <Typography.Title level={4}>{event.theme}</Typography.Title>
            {event.notices.map((notice) => (
              <Alert key={notice} type="warning" showIcon message={notice} />
            ))}
            <Timeline items={event.route.map((point) => ({ children: point }))} />
            <List
              size="small"
              header="打卡任务"
              dataSource={event.checkin_tasks}
              renderItem={(item) => (
                <List.Item>
                  <Space>
                    <Tag color="green">任务</Tag>
                    <Typography.Text>{item}</Typography.Text>
                  </Space>
                </List.Item>
              )}
            />
            <List
              size="small"
              header="活动文案"
              dataSource={event.marketing_content}
              renderItem={(item) => <List.Item>{item}</List.Item>}
            />
          </Space>
        )}
      </Card>
    </div>
  );
}
