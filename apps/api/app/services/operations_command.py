from __future__ import annotations

from typing import TYPE_CHECKING

from app.schemas import (
    AuditLog,
    EventOperationsSummary,
    OperationActionItem,
    OperationReadinessCheck,
    OperationTimelineItem,
)
from app.services.event_merchants import summarize_event_merchants

if TYPE_CHECKING:
    from app.store import MVPStore


ACTIVE_INCIDENT_STATUSES = {"open", "proposal_ready"}
TIMELINE_LIMIT = 12


def _check(
    check_id: str,
    label: str,
    status: str,
    summary: str,
    *,
    blocking: bool = True,
    evidence_refs: list[str] | None = None,
) -> OperationReadinessCheck:
    return OperationReadinessCheck(
        check_id=check_id,
        label=label,
        status=status,
        summary=summary,
        blocking=blocking,
        evidence_refs=evidence_refs or [],
    )


def _latest_published_page(store: "MVPStore", event_id: str, plan_version: int):
    pages = [
        page
        for page in store.list_event_pages(event_id)
        if page.status == "published" and page.plan_version == plan_version
    ]
    if not pages:
        return None
    return max(
        pages,
        key=lambda page: (
            page.plan_version,
            page.published_at or "",
            page.updated_at or "",
            page.id,
        ),
    )


def _merchant_setup_check(store: "MVPStore", event_id: str) -> OperationReadinessCheck:
    setup = summarize_event_merchants(store, event_id)
    if event_id == "demo-night-tour" and setup.total_count == 0:
        return _check(
            "merchant_setup",
            "Merchant setup",
            "warning",
            "Demo event is using the seeded merchant catalog without a manual event roster.",
            blocking=False,
            evidence_refs=["event_merchant_participants:demo-fallback"],
        )
    if setup.ready_for_planning:
        return _check(
            "merchant_setup",
            "Merchant setup",
            "ready",
            f"{setup.ready_count}/{setup.total_count} selected merchants are planning-ready.",
            evidence_refs=[f"event_merchant_roster:{event_id}"],
        )
    summary = (
        "No participating merchants have been selected for this event."
        if setup.total_count == 0
        else f"{setup.ready_count}/{setup.total_count} selected merchants are planning-ready."
    )
    return _check(
        "merchant_setup",
        "Merchant setup",
        "blocked",
        summary,
        evidence_refs=[f"event_merchant_roster:{event_id}"],
    )


def _approved_plan_check(store: "MVPStore", event) -> tuple[OperationReadinessCheck, object | None]:
    plan = None
    if event.current_plan_version:
        plan = store.get_plan_version(event.event_id, event.current_plan_version)
    if plan and plan.status == "approved":
        return (
            _check(
                "plan_approval",
                "Plan approval",
                "ready",
                f"Current route plan v{plan.version} is approved.",
                evidence_refs=[f"plan:{event.event_id}:v{plan.version}"],
            ),
            plan,
        )
    if plan:
        summary = f"Current route plan v{plan.version} is {plan.status}."
        evidence_refs = [f"plan:{event.event_id}:v{plan.version}"]
    else:
        summary = "No approved current route plan is available."
        evidence_refs = []
    return (
        _check(
            "plan_approval",
            "Plan approval",
            "blocked",
            summary,
            evidence_refs=evidence_refs,
        ),
        None,
    )


def _event_page_check(store: "MVPStore", event_id: str, plan) -> OperationReadinessCheck:
    if plan is None:
        return _check(
            "event_page",
            "Visitor event page",
            "blocked",
            "Publish the visitor event page after approving a route plan.",
            evidence_refs=[],
        )
    page = _latest_published_page(store, event_id, plan.version)
    if page:
        return _check(
            "event_page",
            "Visitor event page",
            "ready",
            f"Visitor page {page.id} is published for plan v{plan.version}.",
            evidence_refs=[f"event_page:{page.id}"],
        )
    latest = store.get_latest_event_page(event_id)
    return _check(
        "event_page",
        "Visitor event page",
        "blocked",
        f"No published visitor page exists for plan v{plan.version}.",
        evidence_refs=[f"event_page:{latest.id}"] if latest else [],
    )


def _package_check(store: "MVPStore", event_id: str, plan) -> tuple[OperationReadinessCheck, dict]:
    packages = store.list_merchant_interaction_packages(event_id)
    if plan is None:
        summary = {
            "required_merchant_ids": [],
            "active_package_count": 0,
            "total_package_count": len(packages),
            "missing_merchant_ids": [],
        }
        return (
            _check(
                "merchant_packages",
                "Merchant packages",
                "blocked",
                "Generate merchant packages after approving a route plan.",
                evidence_refs=[],
            ),
            summary,
        )

    required = list(plan.merchant_assignments)
    active = [
        package
        for package in packages
        if package.plan_version == plan.version and package.status == "active"
    ]
    active_ids = {package.merchant_id for package in active}
    missing = [merchant_id for merchant_id in required if merchant_id not in active_ids]
    summary = {
        "required_merchant_ids": required,
        "active_package_count": len(active),
        "total_package_count": len(packages),
        "missing_merchant_ids": missing,
    }
    if required and not missing:
        return (
            _check(
                "merchant_packages",
                "Merchant packages",
                "ready",
                f"{len(active)}/{len(required)} merchant packages are active for plan v{plan.version}.",
                evidence_refs=[f"merchant_interaction_packages:{event_id}:v{plan.version}"],
            ),
            summary,
        )
    return (
        _check(
            "merchant_packages",
            "Merchant packages",
            "blocked",
            f"{len(active)}/{len(required)} merchant packages are active for plan v{plan.version}.",
            evidence_refs=[f"merchant_interaction_packages:{event_id}:v{plan.version}"],
        ),
        summary,
    )


def _incident_check(store: "MVPStore", event_id: str) -> tuple[OperationReadinessCheck, dict]:
    incidents = store.list_incidents(event_id)
    active = [incident for incident in incidents if incident.status in ACTIVE_INCIDENT_STATUSES]
    active_high = [incident for incident in active if incident.severity == "high"]
    active_lower = [incident for incident in active if incident.severity != "high"]
    summary = {
        "total_count": len(incidents),
        "active_count": len(active),
        "active_high_count": len(active_high),
        "active_warning_count": len(active_lower),
        "active_incident_ids": [incident.incident_id for incident in active],
    }
    if active_high:
        return (
            _check(
                "incident_queue",
                "Incident queue",
                "blocked",
                f"{len(active_high)} high-severity incident needs recovery review.",
                evidence_refs=[f"incident:{incident.incident_id}" for incident in active_high],
            ),
            summary,
        )
    if active_lower:
        return (
            _check(
                "incident_queue",
                "Incident queue",
                "warning",
                f"{len(active_lower)} active incident should be watched by operations.",
                blocking=False,
                evidence_refs=[f"incident:{incident.incident_id}" for incident in active_lower],
            ),
            summary,
        )
    return (
        _check(
            "incident_queue",
            "Incident queue",
            "ready",
            "No active incidents are waiting for recovery review.",
            evidence_refs=[],
        ),
        summary,
    )


def _notice_check(store: "MVPStore", event_id: str, incident_summary: dict) -> tuple[OperationReadinessCheck, dict]:
    notices = store.list_public_notices(event_id)
    published = [notice for notice in notices if notice.publish_status == "published"]
    summary = {
        "total_count": len(notices),
        "published_count": len(published),
        "draft_count": len(notices) - len(published),
    }
    active_incidents = int(incident_summary.get("active_count", 0))
    if active_incidents and not notices:
        return (
            _check(
                "public_notices",
                "Public notices",
                "warning",
                "Active incidents exist without public notice evidence.",
                blocking=False,
                evidence_refs=[],
            ),
            summary,
        )
    return (
        _check(
            "public_notices",
            "Public notices",
            "ready",
            f"{len(notices)} public notice records are available.",
            evidence_refs=[f"public_notice:{notice.notice_id}" for notice in notices[:3]],
        ),
        summary,
    )


def _timeline_item(log: AuditLog) -> OperationTimelineItem:
    return OperationTimelineItem(
        item_id=log.log_id,
        actor_type=log.actor_type,
        actor_id=log.actor_id,
        action_type=log.action_type,
        summary=log.note,
        timestamp=log.timestamp,
        evidence_ref=f"audit_log:{log.log_id}",
    )


def _timeline(store: "MVPStore", event_id: str) -> list[OperationTimelineItem]:
    logs = sorted(
        store.list_audit_logs(event_id),
        key=lambda log: (log.timestamp, log.log_id),
        reverse=True,
    )
    return [_timeline_item(log) for log in logs[:TIMELINE_LIMIT]]


def _audit_check(timeline: list[OperationTimelineItem]) -> OperationReadinessCheck:
    if timeline:
        return _check(
            "audit_evidence",
            "Action evidence",
            "ready",
            f"{len(timeline)} recent actions are available for review.",
            evidence_refs=[item.evidence_ref for item in timeline[:3]],
        )
    return _check(
        "audit_evidence",
        "Action evidence",
        "warning",
        "No recent event action evidence is available.",
        blocking=False,
        evidence_refs=[],
    )


def _action_from_check(check: OperationReadinessCheck) -> OperationActionItem | None:
    if check.status == "ready":
        return None
    return OperationActionItem(
        action_id=f"action_{check.check_id}",
        label=check.summary,
        status="todo" if check.status == "blocked" else "watch",
        severity="critical" if check.status == "blocked" and check.blocking else "warning",
        target=check.label,
        evidence_refs=check.evidence_refs,
    )


def build_event_operations_summary(store: "MVPStore", event_id: str) -> EventOperationsSummary:
    event = store.get_event_summary(event_id)
    if event is None:
        raise LookupError("event not found")

    merchant_check = _merchant_setup_check(store, event_id)
    plan_check, current_plan = _approved_plan_check(store, event)
    event_page_check = _event_page_check(store, event_id, current_plan)
    package_check, package_summary = _package_check(store, event_id, current_plan)
    incident_check, incident_summary = _incident_check(store, event_id)
    notice_check, notice_summary = _notice_check(store, event_id, incident_summary)
    timeline = _timeline(store, event_id)
    audit_check = _audit_check(timeline)
    checks = [
        merchant_check,
        plan_check,
        event_page_check,
        package_check,
        incident_check,
        notice_check,
        audit_check,
    ]
    blocker_count = sum(1 for check in checks if check.status == "blocked" and check.blocking)
    warning_count = sum(1 for check in checks if check.status == "warning")
    if blocker_count:
        overall_status = "blocked"
    elif warning_count:
        overall_status = "warning"
    else:
        overall_status = "ready"

    return EventOperationsSummary(
        event=event,
        overall_status=overall_status,
        blocker_count=blocker_count,
        warning_count=warning_count,
        checks=checks,
        action_items=[
            action
            for action in (_action_from_check(check) for check in checks)
            if action is not None
        ],
        timeline=timeline,
        incident_summary=incident_summary,
        package_summary=package_summary,
        notice_summary=notice_summary,
    )
