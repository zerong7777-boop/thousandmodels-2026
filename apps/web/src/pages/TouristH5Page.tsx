import { Alert, Card, Space, Tag, Typography } from "antd";
import { useEffect, useState } from "react";
import { api } from "../api";
import { RoutePointTimeline } from "../components/RoutePointTimeline";
import type { PublicEventV2 } from "../types";

interface TouristH5PageProps {
  eventId: string;
}

export function TouristH5Page({ eventId }: TouristH5PageProps) {
  const [event, setEvent] = useState<PublicEventV2 | null>(null);

  useEffect(() => {
    api.getPublicEvent(eventId)
      .then(setEvent)
      .catch(() => setEvent(null));
  }, [eventId]);

  const notices = (event?.public_notices || []).map((notice) => notice.message);
  const legacyNotices = event?.notices || [];
  const allNotices = notices.length ? notices : legacyNotices;

  return (
    <div className="h5-frame">
      <Space orientation="vertical" size={16} className="full-width">
        <Typography.Title level={2}>Tourist H5</Typography.Title>
        <Card>
          <Space orientation="vertical" size={8}>
            <Typography.Title level={3}>{event?.title || "Demo night tour"}</Typography.Title>
            <Space wrap>
              <Tag color="green">{event?.status || "active"}</Tag>
              <Tag>Route version {event?.current_plan_version || 1}</Tag>
            </Space>
            <Typography.Text type="secondary">
              Visitor route, stop stories, tasks, and live notices.
            </Typography.Text>
          </Space>
        </Card>
        {allNotices.map((notice) => (
          <Alert key={notice} type="warning" showIcon title={notice} />
        ))}
        <Card title="Route and Tasks">
          <RoutePointTimeline points={event?.route_points || []} />
        </Card>
      </Space>
    </div>
  );
}
