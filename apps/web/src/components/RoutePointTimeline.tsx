import { List, Space, Tag, Typography } from "antd";
import type { RoutePoint } from "../types";

interface RoutePointTimelineProps {
  points: RoutePoint[];
}

export function RoutePointTimeline({ points }: RoutePointTimelineProps) {
  if (!points.length) {
    return <Typography.Text type="secondary">暂无路线点。生成并确认方案后会显示路线。</Typography.Text>;
  }

  return (
    <List
      dataSource={points}
      renderItem={(point, index) => (
        <List.Item>
          <Space orientation="vertical" size={4}>
            <Space wrap>
              <Tag color="green">{index + 1}</Tag>
              <Typography.Text strong>{point.name}</Typography.Text>
              <Tag>{point.is_indoor ? "室内" : "户外"}</Tag>
              <Tag color={point.current_status === "active" ? "blue" : "orange"}>{point.current_status}</Tag>
            </Space>
            <Typography.Text>{point.story}</Typography.Text>
            <Typography.Text type="secondary">任务：{point.visitor_task}</Typography.Text>
          </Space>
        </List.Item>
      )}
    />
  );
}
