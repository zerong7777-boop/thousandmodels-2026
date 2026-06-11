import { Card, Empty, Table, Tag } from "antd";
import type { ColumnsType } from "antd/es/table";
import type { MerchantPack } from "../types";

const columns: ColumnsType<MerchantPack> = [
  {
    title: "商户",
    dataIndex: "merchant_id",
    key: "merchant_id",
    width: 100,
    render: (value) => <Tag color="green">{value}</Tag>
  },
  { title: "角色", dataIndex: "role", key: "role" },
  { title: "时段", dataIndex: "time_slot", key: "time_slot", width: 130 },
  { title: "游客任务", dataIndex: "visitor_task", key: "visitor_task" },
  { title: "异常提示", dataIndex: "fallback_instruction", key: "fallback_instruction" }
];

export function MerchantPackTable({ packs }: { packs: MerchantPack[] }) {
  return (
    <Card title="商户执行包">
      {packs.length === 0 ? (
        <Empty description="尚未生成执行包" />
      ) : (
        <Table
          rowKey={(record) => record.merchant_id}
          columns={columns}
          dataSource={packs}
          pagination={false}
          size="middle"
          scroll={{ x: 860 }}
        />
      )}
    </Card>
  );
}
