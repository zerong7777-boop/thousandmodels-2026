import { Alert, Button, Card, List, Space, Tag, Typography } from "antd";
import { CheckCircle2, CloudRain, PackageX } from "lucide-react";
import { api } from "../api";
import type { RecoveryAction } from "../types";

interface RecoveryPanelProps {
  recovery: RecoveryAction | null;
  canTrigger: boolean;
  onRecovery: (action: RecoveryAction) => void;
  onApproved: (action: RecoveryAction) => void;
  onError: (error: unknown) => void;
}

export function RecoveryPanel({
  recovery,
  canTrigger,
  onRecovery,
  onApproved,
  onError
}: RecoveryPanelProps) {
  const run = async (fn: () => Promise<RecoveryAction>) => {
    try {
      onRecovery(await fn());
    } catch (error) {
      onError(error);
    }
  };

  const approve = async () => {
    if (!recovery) return;
    try {
      onApproved(await api.approveRecovery(recovery.action_id));
    } catch (error) {
      onError(error);
    }
  };

  return (
    <Card title="异常恢复">
        <Space orientation="vertical" size="middle" className="full-width">
        <Space wrap>
          <Button
            icon={<PackageX size={16} />}
            disabled={!canTrigger}
            onClick={() => run(api.triggerInventory)}
          >
            触发库存不足
          </Button>
          <Button icon={<CloudRain size={16} />} disabled={!canTrigger} onClick={() => run(api.triggerWeather)}>
            触发强降雨
          </Button>
        </Space>
        {recovery && (
          <Alert
            type={recovery.approval_status === "approved" ? "success" : "warning"}
            showIcon
            message={
              <Space wrap>
                <Typography.Text strong>{recovery.trigger_detail}</Typography.Text>
                <Tag color={recovery.approval_status === "approved" ? "green" : "gold"}>
                  {recovery.approval_status}
                </Tag>
              </Space>
            }
            description={
              <Space orientation="vertical" className="full-width">
                <List
                  size="small"
                  dataSource={recovery.recommended_changes}
                  renderItem={(item) => <List.Item>{item}</List.Item>}
                />
                <Typography.Text>{recovery.tourist_notification}</Typography.Text>
                <Button
                  type="primary"
                  icon={<CheckCircle2 size={16} />}
                  disabled={recovery.approval_status === "approved"}
                  onClick={approve}
                >
                  主办方确认调整
                </Button>
              </Space>
            }
          />
        )}
      </Space>
    </Card>
  );
}
