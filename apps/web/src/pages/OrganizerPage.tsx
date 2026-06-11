import { Alert, Button, Card, Col, Descriptions, message, Row, Space, Statistic, Steps, Tag } from "antd";
import { CheckCircle2, FileText, Play, RefreshCw } from "lucide-react";
import { useState } from "react";
import { api } from "../api";
import { AuditTimeline } from "../components/AuditTimeline";
import { EventPlanView } from "../components/EventPlanView";
import { MerchantPackTable } from "../components/MerchantPackTable";
import { RecoveryPanel } from "../components/RecoveryPanel";
import { ReviewReportPanel } from "../components/ReviewReportPanel";
import type { AuditLog, EventPlan, MerchantPack, RecoveryAction, ReviewReport } from "../types";

const steps = ["创建活动", "生成方案", "商户执行包", "游客 H5", "异常恢复", "复盘报告"];

export function OrganizerPage() {
  const [plan, setPlan] = useState<EventPlan | null>(null);
  const [packs, setPacks] = useState<MerchantPack[]>([]);
  const [recovery, setRecovery] = useState<RecoveryAction | null>(null);
  const [report, setReport] = useState<ReviewReport | null>(null);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(false);

  const currentStep = report ? 5 : recovery?.approval_status === "approved" ? 4 : packs.length ? 2 : plan ? 1 : 0;

  const onError = (error: unknown) => {
    const content = error instanceof Error ? error.message : "请求失败";
    message.error(content);
  };

  const refreshLogs = async () => {
    try {
      setLogs(await api.getAuditLogs());
    } catch {
      setLogs([]);
    }
  };

  const seedAndGenerate = async () => {
    setLoading(true);
    try {
      await api.seed();
      const nextPlan = await api.generatePlan();
      setPlan(nextPlan);
      setPacks(await api.getPacks());
      setRecovery(null);
      setReport(null);
      await refreshLogs();
      message.success("活动方案已生成");
    } catch (error) {
      onError(error);
    } finally {
      setLoading(false);
    }
  };

  const approvePlan = async () => {
    try {
      setPlan(await api.approvePlan());
      await refreshLogs();
      message.success("方案已确认");
    } catch (error) {
      onError(error);
    }
  };

  const approveRecovery = async (action: RecoveryAction) => {
    setRecovery(action);
    await refreshLogs();
    message.success("恢复动作已确认，游客端通知已发布");
  };

  const generateReport = async () => {
    try {
      setReport(await api.generateReport());
      await refreshLogs();
      message.success("复盘报告已生成");
    } catch (error) {
      onError(error);
    }
  };

  return (
    <Space orientation="vertical" size="large" className="full-width">
      <Steps current={currentStep} items={steps.map((title) => ({ title }))} />
      <Row gutter={[16, 16]}>
        <Col xs={24} xl={8}>
          <Card title="活动创建">
            <Space orientation="vertical" size="middle" className="full-width">
              <Descriptions size="small" column={1}>
                <Descriptions.Item label="片区">福隆新街-新马路-内港</Descriptions.Item>
                <Descriptions.Item label="时段">2026-07-18 18:00-21:30</Descriptions.Item>
                <Descriptions.Item label="预算">MOP 50,000</Descriptions.Item>
                <Descriptions.Item label="目标客群">年轻游客、亲子游客</Descriptions.Item>
              </Descriptions>
              <Space wrap>
                <Button type="primary" icon={<Play size={16} />} loading={loading} onClick={seedAndGenerate}>
                  生成活动方案
                </Button>
                <Button
                  icon={<CheckCircle2 size={16} />}
                  disabled={!plan || plan.approval_status === "approved"}
                  onClick={approvePlan}
                >
                  主办方确认方案
                </Button>
              </Space>
            </Space>
          </Card>
        </Col>
        <Col xs={24} sm={8} xl={5}>
          <Card>
            <Statistic title="方案状态" value={plan?.approval_status ?? "未生成"} />
          </Card>
        </Col>
        <Col xs={24} sm={8} xl={5}>
          <Card>
            <Statistic title="商户执行包" value={packs.length} suffix="个" />
          </Card>
        </Col>
        <Col xs={24} sm={8} xl={6}>
          <Card>
            <Statistic title="待确认恢复" value={recovery?.approval_status === "pending" ? 1 : 0} suffix="项" />
          </Card>
        </Col>
      </Row>

      {recovery?.approval_status === "pending" && (
        <Alert
          type="warning"
          showIcon
          message="存在待主办方确认的恢复动作"
          description={recovery.tourist_notification}
        />
      )}

      <Row gutter={[16, 16]}>
        <Col xs={24} xl={14}>
          <EventPlanView plan={plan} />
        </Col>
        <Col xs={24} xl={10}>
          <RecoveryPanel
            recovery={recovery}
            canTrigger={!!plan}
            onRecovery={setRecovery}
            onApproved={approveRecovery}
            onError={onError}
          />
        </Col>
        <Col xs={24}>
          <MerchantPackTable packs={packs} />
        </Col>
        <Col xs={24} xl={12}>
          <Card title="游客端发布状态">
            <Space wrap>
              <Tag color={plan?.approval_status === "approved" ? "green" : "default"}>方案确认</Tag>
              <Tag color={recovery?.approval_status === "approved" ? "green" : "gold"}>恢复通知</Tag>
              <Button icon={<RefreshCw size={16} />} onClick={refreshLogs}>
                刷新审计
              </Button>
            </Space>
          </Card>
        </Col>
        <Col xs={24} xl={12}>
          <Card title="复盘动作">
            <Button type="primary" icon={<FileText size={16} />} disabled={!plan} onClick={generateReport}>
              生成复盘报告
            </Button>
          </Card>
        </Col>
        <Col xs={24} xl={12}>
          <AuditTimeline plan={plan} recovery={recovery} report={report} logs={logs} />
        </Col>
        <Col xs={24} xl={12}>
          <ReviewReportPanel report={report} />
        </Col>
      </Row>
    </Space>
  );
}
