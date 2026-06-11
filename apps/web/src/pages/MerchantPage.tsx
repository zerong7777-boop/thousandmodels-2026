import { Button, Card, Empty, message, Segmented, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { RefreshCw } from "lucide-react";
import { useState } from "react";
import { api } from "../api";
import type { MerchantPack, MerchantRuntimeState } from "../types";

export function MerchantPage() {
  const [packs, setPacks] = useState<MerchantPack[]>([]);
  const [states, setStates] = useState<MerchantRuntimeState[]>([]);

  const load = async () => {
    try {
      setPacks(await api.getPacks());
      setStates(await api.getRuntimeStates());
    } catch (error) {
      message.error(error instanceof Error ? error.message : "读取商户数据失败");
    }
  };

  const columns: ColumnsType<MerchantPack> = [
    { title: "商户", dataIndex: "merchant_id", key: "merchant_id", render: (value) => <Tag color="green">{value}</Tag> },
    { title: "角色", dataIndex: "role", key: "role" },
    { title: "时段", dataIndex: "time_slot", key: "time_slot" },
    { title: "准备事项", dataIndex: "preparation_items", key: "preparation_items", render: (items: string[]) => items.join(" / ") }
  ];

  return (
    <Space orientation="vertical" size="large" className="full-width">
      <Card
        title="商户执行台"
        extra={
          <Button icon={<RefreshCw size={16} />} onClick={load}>
            刷新
          </Button>
        }
      >
        {packs.length === 0 ? (
          <Empty description="等待主办方生成执行包" />
        ) : (
          <Table rowKey="merchant_id" columns={columns} dataSource={packs} pagination={false} scroll={{ x: 760 }} />
        )}
      </Card>
      <Card title="运行状态">
        {states.length === 0 ? (
          <Empty description="等待商户状态" />
        ) : (
          <Space wrap>
            {states.map((state) => (
              <Card key={state.merchant_id} size="small" className="merchant-state-card">
                <Space orientation="vertical" size={6}>
                  <Typography.Text strong>{state.merchant_id}</Typography.Text>
                  <Tag color={state.inventory_status === "sold_out" ? "red" : "green"}>{state.inventory_status}</Tag>
                  <Segmented size="small" value={state.queue_status} options={["normal", "busy", "overloaded"]} />
                </Space>
              </Card>
            ))}
          </Space>
        )}
      </Card>
    </Space>
  );
}
