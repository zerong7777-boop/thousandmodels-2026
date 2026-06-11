import { Alert, Button, Card, Col, List, Row, Space, Table, Tag, Typography, message } from "antd";
import { useEffect, useState } from "react";
import { api } from "../api";
import { AgentTracePanel } from "../components/AgentTracePanel";
import { PlanVersionDiff } from "../components/PlanVersionDiff";
import { RoutePointTimeline } from "../components/RoutePointTimeline";
import type { AgentTrace, MerchantTask, PlanVersion } from "../types";

interface ActivityWorkspacePageProps {
  eventId: string;
}

export function ActivityWorkspacePage({ eventId }: ActivityWorkspacePageProps) {
  const [plan, setPlan] = useState<PlanVersion | null>(null);
  const [traces, setTraces] = useState<AgentTrace[]>([]);
  const [tasks, setTasks] = useState<MerchantTask[]>([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    const [current, agentTraces, merchantTasks] = await Promise.allSettled([
      api.getCurrentPlan(eventId),
      api.getAgentTraces(eventId),
      api.getMerchantTasks(eventId)
    ]);
    if (current.status === "fulfilled") setPlan(current.value);
    if (agentTraces.status === "fulfilled") setTraces(agentTraces.value);
    if (merchantTasks.status === "fulfilled") setTasks(merchantTasks.value);
  };

  useEffect(() => {
    load();
  }, [eventId]);

  const seed = async () => {
    setLoading(true);
    try {
      await api.seed();
      message.success("演示活动已初始化");
      await load();
    } finally {
      setLoading(false);
    }
  };

  const generate = async () => {
    setLoading(true);
    try {
      const response = await api.generatePlan(eventId);
      setPlan(response.current_plan);
      setTraces([response.agent_trace]);
      setTasks(response.merchant_tasks);
    } finally {
      setLoading(false);
    }
  };

  const approve = async () => {
    if (!plan) return;
    const approved = await api.approvePlanVersion(eventId, plan.version);
    setPlan(approved);
  };

  return (
    <Space orientation="vertical" size={16} className="full-width">
      <Typography.Title level={2}>活动工作区</Typography.Title>
      <Space wrap>
        <Button onClick={seed} loading={loading}>初始化演示活动</Button>
        <Button type="primary" onClick={generate} loading={loading}>生成 v1 方案</Button>
        <Button onClick={approve} disabled={!plan || plan.status === "approved"}>
          确认 v{plan?.version || 1} 方案
        </Button>
        <Button href={`/organizer/events/${eventId}/exceptions`}>进入异常中心</Button>
        <Button href={`/public/events/${eventId}`} target="_blank">打开游客 H5</Button>
        <Button href="/merchant/m001" target="_blank">打开商户工作台</Button>
      </Space>
      <Row gutter={[16, 16]}>
        <Col xs={24} xl={7}>
          <PlanVersionDiff plan={plan} />
          <Card title="发布控制" className="mt-16">
            <Alert
              type={plan?.status === "approved" ? "success" : "warning"}
              showIcon
              title={plan?.status === "approved" ? "当前方案已确认" : "方案等待主办方确认"}
            />
          </Card>
        </Col>
        <Col xs={24} xl={10}>
          <Card title="路线点">
            <RoutePointTimeline points={plan?.route_points || []} />
          </Card>
          <Card title="商户任务" className="mt-16">
            <Table
              rowKey="task_id"
              size="small"
              pagination={false}
              dataSource={tasks}
              columns={[
                { title: "商户", dataIndex: "merchant_id" },
                { title: "角色", dataIndex: "role" },
                { title: "时段", dataIndex: "time_slot" },
                {
                  title: "状态",
                  dataIndex: "task_status",
                  render: (value) => <Tag>{value}</Tag>
                }
              ]}
            />
          </Card>
        </Col>
        <Col xs={24} xl={7}>
          <AgentTracePanel traces={traces} />
          <Card title="风险预案" className="mt-16">
            <List
              size="small"
              dataSource={plan?.risk_plan || []}
              renderItem={(item) => <List.Item>{item}</List.Item>}
            />
          </Card>
        </Col>
      </Row>
    </Space>
  );
}
