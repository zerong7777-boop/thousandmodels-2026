import { api } from "../../api";
import { AgentEvidencePanel, latestRunForTrigger } from "../../components/agent";
import { MetricTile, ProductPageHeader } from "../../components/product";
import { localizedDemoList, localizedDemoText, useI18n } from "../../i18n";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { asArray, useAsyncData } from "../productUtils";

export function OrganizerReviewPage({ eventId = "demo-night-tour" }: { eventId?: string }) {
  const { t } = useI18n();
  const { data: report } = useAsyncData(() => api.getReviewReport(eventId), null);
  const { data: agentRuns } = useAsyncData(() => api.getAgentRuns(eventId), [], [eventId]);
  const reviewRun = latestRunForTrigger(asArray(agentRuns), "review_generation");
  const { data: reviewDrafts } = useAsyncData(() => api.getAgentDrafts(eventId, "review_summary"), [], [eventId]);
  const { data: reviewModelCalls } = useAsyncData(
    () => (reviewRun ? api.getAgentModelCalls(eventId, reviewRun.run_id) : Promise.resolve([])),
    [],
    [eventId, reviewRun?.run_id]
  );
  const { data: reviewEvaluations } = useAsyncData(
    () => (reviewRun ? api.getAgentEvaluations(eventId, reviewRun.run_id) : Promise.resolve([])),
    [],
    [eventId, reviewRun?.run_id]
  );
  const recommendations = localizedDemoList(asArray(report?.next_event_recommendations), t);
  const lessons = localizedDemoList(asArray(report?.lessons_learned), t);

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow={t("organizer.review.eyebrow")}
        title={t("organizer.review.title")}
        description={report?.summary ? localizedDemoText(report.summary, t) : t("organizer.review.descriptionFallback")}
        meta={[
          t("organizer.review.metaVisits"),
          t("organizer.review.metaCheckins"),
          t("organizer.review.metaResponse"),
          t("organizer.review.metaBudget")
        ]}
        status="ready"
      />
      <div className="grid gap-4 md:grid-cols-5">
        <MetricTile label={t("organizer.review.h5Visits")} value="428" detail={t("organizer.review.metaVisits")} tone="info" />
        <MetricTile label={t("organizer.review.checkIns")} value="136" detail={t("organizer.review.checkInsDetail")} tone="success" />
        <MetricTile label={t("organizer.review.responseTime")} value="4 min" detail={t("organizer.review.responseTimeDetail")} tone="success" />
        <MetricTile label={t("organizer.review.queuePressure")} value={t("organizer.review.queuePressureValue")} detail={t("organizer.review.queuePressureDetail")} tone="warning" />
        <MetricTile label={t("organizer.review.budgetUsed")} value="82%" detail={t("organizer.review.budgetUsedDetail")} tone="success" />
      </div>
      <AgentEvidencePanel
        title={t("organizer.agentEvidence.reviewTitle")}
        description={t("organizer.agentEvidence.reviewDescription")}
        runs={reviewRun ? [reviewRun] : []}
        steps={[]}
        toolCalls={[]}
        drafts={asArray(reviewDrafts).filter((draft) => draft.source_run_id === reviewRun?.run_id)}
        modelCalls={asArray(reviewModelCalls)}
        evaluations={asArray(reviewEvaluations)}
        emptyMessage={t("organizer.agentEvidence.emptyReview")}
      />
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>{t("organizer.review.whatWorked")}</CardTitle>
            <CardDescription>{t("organizer.review.whatWorkedDescription")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-slate-700">
            <p>{report?.route_result ? localizedDemoText(report.route_result, t) : t("organizer.review.routePending")}</p>
            <p>{report?.merchant_result ? localizedDemoText(report.merchant_result, t) : t("organizer.review.merchantPending")}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>{t("organizer.review.recommendations")}</CardTitle>
            <CardDescription>{t("organizer.review.recommendationsDescription")}</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="list-disc space-y-1 pl-5 text-sm text-slate-700">
              {recommendations.map((item) => (
                <li key={item}>{item}</li>
              ))}
              {!recommendations.length ? <li>{t("organizer.review.noRecommendation")}</li> : null}
            </ul>
          </CardContent>
        </Card>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>{t("organizer.review.metricsLessons")}</CardTitle>
          <CardDescription>{t("organizer.review.metricsLessonsDescription")}</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="list-disc space-y-1 pl-5 text-sm text-slate-700">
            {lessons.map((item) => (
              <li key={item}>{item}</li>
            ))}
            {!lessons.length ? <li>{t("organizer.review.noMetricLesson")}</li> : null}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
