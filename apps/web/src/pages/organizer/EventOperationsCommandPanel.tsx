import { localizedStatus, useI18n } from "../../i18n";
import { Badge } from "../../ui/badge";
import { MetricTile } from "../../components/product";
import type {
  EventOperationsSummary,
  OperationActionItem,
  OperationReadinessCheck,
  OperationReadinessStatus
} from "../../types";

function statusVariant(status: OperationReadinessStatus): "success" | "warning" | "danger" {
  if (status === "ready") return "success";
  if (status === "warning") return "warning";
  return "danger";
}

function metricTone(status: OperationReadinessStatus): "success" | "warning" | "danger" {
  if (status === "ready") return "success";
  if (status === "warning") return "warning";
  return "danger";
}

function actionVariant(action: OperationActionItem): "warning" | "danger" | "neutral" {
  if (action.severity === "critical") return "danger";
  if (action.severity === "warning") return "warning";
  return "neutral";
}

function CheckCard({ check }: { check: OperationReadinessCheck }) {
  const { t } = useI18n();
  return (
    <div className="rounded-md border border-slate-200 bg-white p-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-sm font-semibold text-ink">{check.label}</h3>
        <Badge variant={statusVariant(check.status)}>{localizedStatus(check.status, t)}</Badge>
      </div>
      <p className="mt-2 text-sm leading-5 text-slate-600">{check.summary}</p>
      {check.evidence_refs.length ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {check.evidence_refs.slice(0, 3).map((evidenceRef) => (
            <Badge key={evidenceRef} variant="neutral">
              {evidenceRef}
            </Badge>
          ))}
        </div>
      ) : null}
    </div>
  );
}

export function EventOperationsCommandPanel({ summary }: { summary: EventOperationsSummary | null }) {
  const { t } = useI18n();

  if (!summary) {
    return null;
  }

  const checks = summary.checks ?? [];
  const actionItems = summary.action_items ?? [];
  const timeline = summary.timeline ?? [];
  const overallStatus = summary.overall_status ?? "warning";
  const blockerCount = summary.blocker_count ?? 0;
  const warningCount = summary.warning_count ?? 0;

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold text-ink">{t("organizer.operations.title")}</h2>
          <p className="mt-1 text-sm leading-5 text-slate-600">{t("organizer.operations.description")}</p>
        </div>
        <Badge variant={statusVariant(overallStatus)}>
          {localizedStatus(overallStatus, t)}
        </Badge>
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <MetricTile
          label={t("organizer.operations.overallStatus")}
          value={localizedStatus(overallStatus, t)}
          detail={t("organizer.operations.overallStatusDetail")}
          tone={metricTone(overallStatus)}
        />
        <MetricTile
          label={t("organizer.operations.blockers")}
          value={String(blockerCount)}
          detail={t("organizer.operations.blockersDetail")}
          tone={blockerCount ? "danger" : "success"}
        />
        <MetricTile
          label={t("organizer.operations.warnings")}
          value={String(warningCount)}
          detail={t("organizer.operations.warningsDetail")}
          tone={warningCount ? "warning" : "success"}
        />
      </div>

      <div className="mt-5 grid gap-4 xl:grid-cols-[minmax(0,1.1fr)_minmax(280px,0.9fr)]">
        <div>
          <h3 className="text-sm font-semibold text-ink">{t("organizer.operations.checksTitle")}</h3>
          <div className="mt-3 grid gap-3 md:grid-cols-2">
            {checks.map((check) => (
              <CheckCard key={check.check_id} check={check} />
            ))}
            {!checks.length ? (
              <p className="rounded-md border border-dashed border-slate-200 p-3 text-sm text-slate-500">
                {t("organizer.operations.checksEmpty")}
              </p>
            ) : null}
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
            <h3 className="text-sm font-semibold text-ink">{t("organizer.operations.actionItemsTitle")}</h3>
            <div className="mt-3 space-y-2">
              {actionItems.map((item) => (
                <div key={item.action_id} className="rounded-md border border-slate-200 bg-white p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-sm font-semibold text-ink">{item.target}</span>
                    <Badge variant={actionVariant(item)}>{localizedStatus(item.status, t)}</Badge>
                  </div>
                  <p className="mt-2 text-sm leading-5 text-slate-600">{item.label}</p>
                </div>
              ))}
              {!actionItems.length ? (
                <p className="text-sm text-slate-500">{t("organizer.operations.actionItemsEmpty")}</p>
              ) : null}
            </div>
          </div>

          <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
            <h3 className="text-sm font-semibold text-ink">{t("organizer.operations.timelineTitle")}</h3>
            <div className="mt-3 space-y-2">
              {timeline.slice(0, 5).map((item) => (
                <div key={item.item_id} className="rounded-md border border-slate-200 bg-white p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-sm font-semibold text-ink">{item.action_type}</span>
                    <span className="text-xs text-slate-500">{item.timestamp}</span>
                  </div>
                  <p className="mt-2 text-sm leading-5 text-slate-600">{item.summary}</p>
                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    <Badge variant="neutral">{item.actor_type}</Badge>
                    <Badge variant="neutral">{item.evidence_ref}</Badge>
                  </div>
                </div>
              ))}
              {!timeline.length ? <p className="text-sm text-slate-500">{t("organizer.operations.timelineEmpty")}</p> : null}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
