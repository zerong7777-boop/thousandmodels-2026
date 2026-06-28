import type { Translator } from "./types";

type LocalizableRoutePoint = {
  point_id?: string;
  name?: string;
  story?: string;
  visitor_task?: string;
  current_status?: string;
};

const demoTextKeys: Record<string, string> = {
  "Historic District Night Tour": "demo.event.title",
  "Rua da Felicidade": "demo.event.area",
  "Merchant m001": "demo.merchant.name",
  "Indoor tea stop": "demo.route.rp002.name",
  "A restored street story linking old shops and evening foot traffic.": "demo.route.rp001.story",
  "Collect the red facade stamp.": "demo.route.rp001.task",
  "A sheltered stop used after the recovery plan.": "demo.route.rp002.story",
  "Try the heritage tea pairing.": "demo.route.rp002.task",
  "A cultural stop on tonight's walking route.": "demo.route.genericStory",
  "Follow the story prompt at this stop.": "demo.route.genericTask",
  "Please continue to the indoor tea stop.": "demo.notice.indoorTea",
  "Route updated": "demo.notice.routeUpdated",
  "Route updated for tonight": "demo.notice.routeUpdatedTonight",
  "Please continue to the indoor tea stop. Your route has been updated.": "demo.notice.routeUpdatedFull",
  "Heritage snack stop": "demo.task.roleSnack",
  "Prepare twenty tasting cards.": "demo.task.visitorTastingCards",
  "Queue marker": "demo.task.queueMarker",
  "Stamp card": "demo.task.stampCard",
  "Tonight only heritage tasting": "demo.task.promoTasting",
  "Pause intake and notify organizer.": "demo.task.fallbackPause",
  "H5 visits 428; recovery confirmation reduced confused arrivals.": "demo.review.summary",
  "Route v2 kept the visitor flow active.": "demo.review.routeResult",
  "Merchant tasks were updated after the exception.": "demo.review.merchantResult",
  "Merchant tasks were updated after the incident.": "demo.review.merchantResult",
  "One inventory exception was approved into a recovered route.": "demo.review.incidentSummary",
  "Inventory telemetry needs earlier merchant prompts.": "demo.review.lessonTelemetry",
  "H5 visits 428": "demo.review.lessonVisits",
  "Check-ins 136": "demo.review.lessonCheckins",
  "Response time 4 min": "demo.review.lessonResponse",
  "Reduce sold-out merchant routing weight": "demo.review.recommendWeight",
  "Add one more sheltered stop": "demo.review.recommendShelter",
  "Pre-stage an indoor backup stop.": "demo.review.recommendBackup",
  "Route completed": "demo.report.routeCompleted",
  "Merchants completed": "demo.report.merchantsCompleted",
  "Organizer approved recovery": "demo.report.approvedRecovery",
  "Organizer confirmed recovery": "demo.report.confirmedRecovery",
  "Old street story": "demo.misc.oldStreetStory",
  "Answer a question": "demo.misc.answerQuestion",
  "A street story": "demo.misc.streetStory",
  "Collect a stamp": "demo.misc.collectStamp",
  "inventory incident recovery": "demo.plan.reasonRecovery",
  "Pause sold-out stop": "demo.plan.diffPause",
  "Add indoor tea stop": "demo.plan.diffIndoor",
  "Merchant inventory incident": "demo.agent.triggerInventory",
  "Rule-based route recovery evidence.": "demo.agent.reasonRouteRecovery",
  "Merchant m001 reported sold out.": "demo.incident.soldOut"
};

const statusKeys: Record<string, string> = {
  active: "common.status.active",
  inactive: "common.status.inactive",
  suspended: "common.status.suspended",
  approved: "common.status.approved",
  open: "common.status.open",
  ready: "common.status.ready",
  published: "common.status.published",
  paused: "common.status.paused",
  normal: "common.status.normal",
  low: "common.status.low",
  sold_out: "common.status.sold_out",
  busy: "common.status.busy",
  overloaded: "common.status.overloaded",
  draft: "common.status.draft",
  pending: "common.status.pending",
  confirmed: "common.status.confirmed",
  current: "common.status.current",
  proposal_ready: "common.status.proposal_ready",
  superseded: "common.status.superseded",
  completed: "common.status.completed",
  replaced: "common.status.replaced",
  stale: "common.status.stale",
  eligible: "common.status.eligible",
  needs_review: "common.status.needs_review",
  ineligible: "common.status.ineligible"
};

export function localizedDemoText(value: string | undefined | null, t: Translator): string {
  if (!value) {
    return "";
  }
  const key = demoTextKeys[value];
  return key ? t(key) : value;
}

export function localizedDemoList(values: Array<string | undefined | null>, t: Translator): string[] {
  return values.map((value) => localizedDemoText(value, t)).filter(Boolean);
}

export function localizedStatus(value: string | undefined | null, t: Translator): string {
  if (!value) {
    return "";
  }
  const key = statusKeys[value];
  return key ? t(key) : value;
}

export function localizedRoutePoint<T extends LocalizableRoutePoint>(point: T, t: Translator): T {
  const pointKey = point.point_id === "rp001" ? "demo.route.rp001" : point.point_id === "rp002" ? "demo.route.rp002" : null;
  return {
    ...point,
    name: pointKey ? t(`${pointKey}.name`) : localizedDemoText(point.name, t),
    story: pointKey ? t(`${pointKey}.story`) : localizedDemoText(point.story, t),
    visitor_task: pointKey ? t(`${pointKey}.task`) : localizedDemoText(point.visitor_task, t),
    current_status: localizedStatus(point.current_status, t)
  };
}
