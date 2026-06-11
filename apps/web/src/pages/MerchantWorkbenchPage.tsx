import { Alert, Button, Card, List, Space, Tag, Typography, message } from "antd";
import { useEffect, useState } from "react";
import { api } from "../api";
import type { Incident, MerchantRuntimeState, MerchantTask, MerchantWorkbench } from "../types";

interface MerchantWorkbenchPageProps {
  merchantId: string;
}

export function MerchantWorkbenchPage({ merchantId }: MerchantWorkbenchPageProps) {
  const [workbench, setWorkbench] = useState<MerchantWorkbench>({ tasks: [] });
  const [incident, setIncident] = useState<Incident | null>(null);

  const load = async () => {
    const data = await api.getMerchantWorkbench(merchantId);
    setWorkbench({ ...data, tasks: data.tasks ?? [] });
  };

  useEffect(() => {
    load().catch(() => setWorkbench({ tasks: [] }));
  }, [merchantId]);

  const submitState = async (payload: Partial<MerchantRuntimeState>) => {
    const result = await api.updateRuntimeState(merchantId, payload);
    setWorkbench((current) => ({
      ...current,
      runtime_state: result.runtime_state || result
    }));
    setIncident(result.incident || null);
    if (result.incident) message.warning("Runtime status synced to organizer exceptions.");
  };

  return (
    <Space orientation="vertical" size={16} className="full-width">
      <Typography.Title level={2}>Merchant Workbench</Typography.Title>
      <Alert
        type="info"
        showIcon
        title={workbench.merchant?.name || merchantId}
        description="Merchant endpoint for assigned tasks, inventory, queue, and availability updates."
      />
      <Card title="Today Tasks">
        <List
          dataSource={workbench.tasks}
          locale={{ emptyText: "No tasks yet. Tasks appear after the organizer approves an event plan." }}
          renderItem={(task: MerchantTask) => (
            <List.Item>
              <List.Item.Meta
                title={
                  <Space wrap>
                    <span>{task.role}</span>
                    <Tag>{task.time_slot}</Tag>
                    <Tag color={task.task_status === "active" ? "green" : "orange"}>{task.task_status}</Tag>
                  </Space>
                }
                description={task.visitor_task}
              />
            </List.Item>
          )}
        />
      </Card>
      <Card title="Runtime Status">
        <Space orientation="vertical" className="full-width">
          <Space wrap>
            <Tag>Inventory: {workbench.runtime_state?.inventory_status || "unknown"}</Tag>
            <Tag>Queue: {workbench.runtime_state?.queue_status || "unknown"}</Tag>
            <Tag>{workbench.runtime_state?.available_for_visitors === false ? "Paused" : "Available"}</Tag>
          </Space>
          <Space wrap>
            <Button onClick={() => submitState({ inventory_status: "normal", available_for_visitors: true })}>
              Report normal inventory
            </Button>
            <Button onClick={() => submitState({ inventory_status: "low", queue_status: "busy" })}>
              Report low inventory
            </Button>
            <Button
              danger
              onClick={() =>
                submitState({
                  inventory_status: "sold_out",
                  queue_status: "busy",
                  available_for_visitors: false,
                  temporary_note: "Merchant reported sold out"
                })
              }
            >
              Report sold out
            </Button>
            <Button onClick={() => submitState({ queue_status: "overloaded" })}>Report queue overload</Button>
          </Space>
          {incident && <Alert type="warning" showIcon title={`Triggered ${incident.type} incident`} />}
        </Space>
      </Card>
    </Space>
  );
}
