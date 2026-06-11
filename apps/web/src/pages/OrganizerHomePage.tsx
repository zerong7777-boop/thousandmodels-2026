import { Alert, Button, Card, Col, List, Row, Space, Statistic, Tag, Typography } from "antd";
import { useEffect, useState } from "react";
import { api } from "../api";
import type { EventSummary } from "../types";

const DEMO_EVENT_ID = "demo-night-tour";

export function OrganizerHomePage() {
  const [events, setEvents] = useState<EventSummary[]>([]);

  useEffect(() => {
    api.getEvents().then(setEvents).catch(() => setEvents([]));
  }, []);

  const event = events[0];

  return (
    <Space orientation="vertical" size={16} className="full-width">
      <Typography.Title level={2}>活动运营</Typography.Title>
      <Alert
        type="info"
        showIcon
        title="当前工作台"
        description="这里是主办方日常入口：活动列表、待审批、风险告警和执行状态放在首屏。"
      />
      <Row gutter={[16, 16]}>
        <Col xs={24} md={6}>
          <Card>
            <Statistic title="活动总数" value={events.length || 1} />
          </Card>
        </Col>
        <Col xs={24} md={6}>
          <Card>
            <Statistic title="待审批" value={1} />
          </Card>
        </Col>
        <Col xs={24} md={6}>
          <Card>
            <Statistic title="风险告警" value={2} />
          </Card>
        </Col>
        <Col xs={24} md={6}>
          <Card>
            <Statistic title="当前版本" value={event?.current_plan_version || 0} prefix="v" />
          </Card>
        </Col>
      </Row>
      <Card title="活动列表">
        <List
          dataSource={
            events.length
              ? events
              : [
                  {
                    event_id: DEMO_EVENT_ID,
                    title: "福隆新街周末旧区夜游",
                    area: "福隆新街-新马路-内港",
                    date: "2026-07-18",
                    time_window: "18:00-21:30",
                    status: "draft",
                    current_plan_version: 0,
                    public_release_status: "draft"
                  } satisfies EventSummary
                ]
          }
          renderItem={(item) => (
            <List.Item
              actions={[
                <Button key="workspace" type="primary" href={`/organizer/events/${item.event_id}`}>
                  进入活动工作区
                </Button>,
                <Button key="exceptions" href={`/organizer/events/${item.event_id}/exceptions`}>
                  异常中心
                </Button>,
                <Button key="review" href={`/review/${item.event_id}`}>
                  复盘中心
                </Button>
              ]}
            >
              <List.Item.Meta
                title={
                  <Space wrap>
                    <Typography.Text strong>{item.title}</Typography.Text>
                    <Tag color={item.status === "active" ? "green" : "blue"}>{item.status}</Tag>
                    <Tag>{item.public_release_status}</Tag>
                  </Space>
                }
                description={`${item.area} / ${item.date} ${item.time_window}`}
              />
            </List.Item>
          )}
        />
      </Card>
    </Space>
  );
}
