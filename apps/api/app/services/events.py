from __future__ import annotations

import re
from typing import TYPE_CHECKING
from uuid import uuid4

from app.schemas import (
    EventBrief,
    EventCreateRequest,
    EventSummary,
    EventUpdateRequest,
)

if TYPE_CHECKING:
    from app.store import MVPStore


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return re.sub(r"-+", "-", slug)


def normalize_event_id(payload: EventCreateRequest) -> str:
    if payload.event_id is not None:
        event_id = _slugify(payload.event_id)
        if not event_id:
            raise ValueError("event_id is invalid")
        return event_id
    base = _slugify(f"{payload.title}-{payload.date}") or "event"
    return f"{base}-{uuid4().hex[:8]}"


def create_event(store: MVPStore, payload: EventCreateRequest) -> EventSummary:
    event_id = normalize_event_id(payload)
    if store.get_event_summary(event_id) or store.get_event_brief(event_id):
        raise ValueError("event already exists")

    brief = EventBrief(
        event_id=event_id,
        area=payload.area,
        date=payload.date,
        time_window=payload.time_window,
        budget_mop=payload.budget_mop,
        target_audience=payload.target_audience,
        event_goal=payload.event_goal,
        theme_preferences=payload.theme_preferences,
        constraints=payload.constraints,
        priority_rules=payload.priority_rules,
    )
    event = EventSummary(
        event_id=event_id,
        title=payload.title,
        area=payload.area,
        date=payload.date,
        time_window=payload.time_window,
        status="draft",
        current_plan_version=0,
        public_release_status="draft",
    )
    store.save_event_brief(brief)
    store.save_event_summary(event)
    return event


def update_draft_event(
    store: MVPStore,
    event_id: str,
    payload: EventUpdateRequest,
) -> EventSummary:
    brief = store.get_event_brief(event_id)
    event = store.get_event_summary(event_id)
    if not brief or not event:
        raise LookupError("event not found")
    if event.status != "draft" or event.current_plan_version != 0:
        raise RuntimeError("event can only be updated before planning")

    event_payload = event.model_dump()
    for field in ("title", "area", "date", "time_window"):
        value = getattr(payload, field)
        if value is not None:
            event_payload[field] = value

    brief_payload = brief.model_dump()
    for field in (
        "area",
        "date",
        "time_window",
        "budget_mop",
        "target_audience",
        "event_goal",
        "theme_preferences",
        "constraints",
        "priority_rules",
    ):
        value = getattr(payload, field)
        if value is not None:
            brief_payload[field] = value

    updated_brief = EventBrief.model_validate(brief_payload)
    updated_event = EventSummary.model_validate(event_payload)
    store.save_event_brief(updated_brief)
    store.save_event_summary(updated_event)
    return updated_event


def mark_public_release_stale(event: EventSummary) -> EventSummary:
    if event.public_release_status == "published":
        event.public_release_status = "stale"
    return event


def mark_public_release_published(event: EventSummary) -> EventSummary:
    event.public_release_status = "published"
    return event


def mark_public_release_for_plan_approval(
    store: MVPStore,
    event: EventSummary,
    version: int,
) -> EventSummary:
    published_pages = [
        page for page in store.list_event_pages(event.event_id) if page.status == "published"
    ]
    if any(page.plan_version == version for page in published_pages):
        next_event = mark_public_release_published(event)
    elif published_pages:
        next_event = mark_public_release_stale(event)
    else:
        event.public_release_status = "draft"
        next_event = event
    return next_event
