import { Card, Empty, Timeline } from "antd";
import type { AuditLog, EventPlan, RecoveryAction, ReviewReport } from "../types";

interface AuditTimelineProps {
  plan: EventPlan | null;
  recovery: RecoveryAction | null;
  report: ReviewReport | null;
  logs: AuditLog[];
}

export function AuditTimeline({ plan, recovery, report, logs }: AuditTimelineProps) {
  const inferred = [
    plan && `EventPlan v${plan.version}: ${plan.approval_status}`,
    recovery && `RecoveryAction ${recovery.action_id}: ${recovery.approval_status}`,
    report && `ReviewReport: ${report.event_id}`
  ].filter(Boolean) as string[];
  const items = [
    ...logs.map((log) => ({ children: `${log.actor_type}/${log.action_type}: ${log.note}` })),
    ...inferred.map((item) => ({ children: item }))
  ];

  return (
    <Card title="审计记录">
      {items.length === 0 ? <Empty description="尚无审计事件" /> : <Timeline items={items} />}
    </Card>
  );
}
