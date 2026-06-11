import { Alert, Button, Card, Col, List, Row, Space, Tag, Typography, message } from "antd";
import { useEffect, useState } from "react";
import { api } from "../api";
import { IncidentQueue } from "../components/IncidentQueue";
import { PlanVersionDiff } from "../components/PlanVersionDiff";
import type { ApproveRecoveryResponse, Incident, PlanVersion, RecoveryProposal } from "../types";

interface ExceptionCenterPageProps {
  eventId: string;
}

export function ExceptionCenterPage({ eventId }: ExceptionCenterPageProps) {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [proposal, setProposal] = useState<RecoveryProposal | null>(null);
  const [approved, setApproved] = useState<ApproveRecoveryResponse | null>(null);
  const [plan, setPlan] = useState<PlanVersion | null>(null);

  const load = async () => {
    const [incidentResult, planResult] = await Promise.allSettled([
      api.getIncidents(eventId),
      api.getCurrentPlan(eventId)
    ]);
    if (incidentResult.status === "fulfilled") setIncidents(incidentResult.value);
    if (planResult.status === "fulfilled") setPlan(planResult.value);
  };

  useEffect(() => {
    load();
  }, [eventId]);

  const triggerMerchantIncident = async () => {
    const response = await api.updateRuntimeState("m001", {
      inventory_status: "sold_out",
      queue_status: "busy",
      available_for_visitors: false,
      temporary_note: "商户端上报：杏仁饼售罄"
    });
    if (response.incident) {
      message.warning("已生成库存 Incident");
    }
    await load();
  };

  const createProposal = async (incidentId: string) => {
    const created = await api.createRecoveryProposal(eventId, incidentId);
    setProposal(created);
    message.success("RecoveryProposal 已生成");
    await load();
  };

  const approveProposal = async () => {
    if (!proposal) return;
    const result = await api.approveRecoveryProposal(eventId, proposal.proposal_id);
    setApproved(result);
    setPlan(result.current_plan);
    message.success("恢复方案已确认，已生成 v2");
    await load();
  };

  return (
    <Space orientation="vertical" size={16} className="full-width">
      <Typography.Title level={2}>异常中心</Typography.Title>
      <Alert
        type="warning"
        showIcon
        title="运行期异常处理"
        description="异常中心只处理状态变化、影响范围、RecoveryProposal 和主办方确认，不嵌入游客端页面。"
      />
      <Space wrap>
        <Button onClick={triggerMerchantIncident}>模拟商户库存售罄</Button>
        <Button href={`/public/events/${eventId}`} target="_blank">打开游客入口</Button>
      </Space>
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={10}>
          <IncidentQueue incidents={incidents} onCreateProposal={createProposal} />
        </Col>
        <Col xs={24} lg={7}>
          <Card title="RecoveryProposal">
            {proposal ? (
              <Space orientation="vertical" className="full-width">
                <Tag color={proposal.approval_status === "approved" ? "green" : "gold"}>
                  {proposal.approval_status}
                </Tag>
                <Typography.Text>{proposal.impact_summary}</Typography.Text>
                <List
                  size="small"
                  dataSource={proposal.recommended_changes}
                  renderItem={(item) => <List.Item>{item}</List.Item>}
                />
                <Button type="primary" onClick={approveProposal}>主办方确认恢复</Button>
              </Space>
            ) : (
              <Typography.Text type="secondary">选择一个 Incident 生成恢复方案。</Typography.Text>
            )}
          </Card>
        </Col>
        <Col xs={24} lg={7}>
          <PlanVersionDiff plan={approved?.current_plan || plan} />
          {approved?.notice && (
            <Card title="公开通知" className="mt-16">
              <Tag color="green">{approved.notice.publish_status}</Tag>
              <Typography.Paragraph>{approved.notice.message}</Typography.Paragraph>
            </Card>
          )}
        </Col>
      </Row>
    </Space>
  );
}
