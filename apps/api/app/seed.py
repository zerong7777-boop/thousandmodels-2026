import json
from datetime import UTC, datetime
from pathlib import Path

from app.schemas import (
    AuthUserRecord,
    EventBrief,
    EventSummary,
    MerchantProfile,
    MerchantRuntimeState,
    OperationalMetric,
    RoutePoint,
)
from app.security import hash_password
from app.store_paths import project_root
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.store import MVPStore


DEMO_AUTH_USERS = [
    {
        "user_id": "usr_org_demo",
        "username": "organizer.demo",
        "password": "demo1234",
        "role": "organizer",
        "display_name": "Organizer Demo",
        "merchant_id": None,
    },
    {
        "user_id": "usr_merchant_m001_demo",
        "username": "merchant.m001.demo",
        "password": "demo1234",
        "role": "merchant",
        "display_name": "Merchant m001 Demo",
        "merchant_id": "m001",
    },
    {
        "user_id": "usr_tourist_demo",
        "username": "tourist.demo",
        "password": "demo1234",
        "role": "tourist",
        "display_name": "Tourist Demo",
        "merchant_id": None,
    },
]


def data_root() -> Path:
    return project_root() / "data" / "mock"


def load_json(name: str):
    with (data_root() / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def seed_demo_accounts(store: "MVPStore") -> None:
    store.ensure_auth_schema()
    now = datetime.now(UTC).isoformat()
    for account in DEMO_AUTH_USERS:
        existing = store.get_user_by_username(account["username"])
        password_hash = existing.password_hash if existing else hash_password(account["password"])
        store.upsert_user(
            AuthUserRecord(
                user_id=account["user_id"],
                username=account["username"],
                password_hash=password_hash,
                role=account["role"],
                display_name=account["display_name"],
                merchant_id=account["merchant_id"],
                status="active",
                created_at=existing.created_at if existing else now,
            )
        )


def seed_demo(store: "MVPStore", event_id: str = "demo-night-tour") -> EventBrief:
    store.clear_demo(event_id)
    brief = EventBrief.model_validate(load_json("demo_event.json"))
    store.save_event_brief(brief)
    now = datetime.now(UTC).isoformat()
    store.save_event_summary(
        EventSummary(
            event_id=brief.event_id,
            title="福隆新街周末旧区夜游",
            area=brief.area,
            date=brief.date,
            time_window=brief.time_window,
            status="draft",
            current_plan_version=0,
            public_release_status="draft",
        )
    )
    route_points = [
        RoutePoint(
            point_id="rp001",
            name="福隆新街开场点",
            type="street",
            is_indoor=False,
            estimated_stay_minutes=20,
            story="以老字号街景作为夜游起点，串联街区美食记忆。",
            linked_merchants=["m001"],
            visitor_task="完成老字号问答",
            rainy_day_score=2,
            crowd_risk="medium",
            current_status="active",
        ),
        RoutePoint(
            point_id="rp002",
            name="新马路文创线索点",
            type="creative",
            is_indoor=True,
            estimated_stay_minutes=18,
            story="以手绘地图和街区明信片引导游客理解旧城肌理。",
            linked_merchants=["m003"],
            visitor_task="领取街区线索卡",
            rainy_day_score=4,
            crowd_risk="medium",
            current_status="active",
        ),
        RoutePoint(
            point_id="rp003",
            name="内港故事点",
            type="culture",
            is_indoor=False,
            estimated_stay_minutes=25,
            story="讲述内港海贸和街坊生活的历史联系。",
            linked_merchants=["m005"],
            visitor_task="完成内港故事打卡",
            rainy_day_score=3,
            crowd_risk="low",
            current_status="active",
        ),
        RoutePoint(
            point_id="rp004",
            name="十月初五茶餐厅补给点",
            type="food",
            is_indoor=True,
            estimated_stay_minutes=25,
            story="以本地茶餐厅作为夜游补给和分流节点。",
            linked_merchants=["m004"],
            visitor_task="完成澳门味道小问答",
            rainy_day_score=5,
            crowd_risk="high",
            current_status="active",
        ),
        RoutePoint(
            point_id="rp005",
            name="旧区社区客厅",
            type="backup",
            is_indoor=True,
            estimated_stay_minutes=30,
            story="社区空间承接雨天讲解和亲子互动。",
            linked_merchants=["m008"],
            visitor_task="完成社区记忆贴纸任务",
            rainy_day_score=5,
            crowd_risk="low",
            current_status="active",
        ),
        RoutePoint(
            point_id="rp007",
            name="新街手信铺备用点",
            type="shopping",
            is_indoor=False,
            estimated_stay_minutes=20,
            story="作为库存异常时的备用手信购买点。",
            linked_merchants=["m007"],
            visitor_task="领取备用手信优惠",
            rainy_day_score=3,
            crowd_risk="medium",
            current_status="active",
        ),
    ]
    for point in route_points:
        store.save_route_point(point)
    for metric in [
        OperationalMetric(
            metric_id="metric_h5_visits",
            event_id=brief.event_id,
            name="h5_visits",
            value=428,
            unit="visits",
            source="mock",
            captured_at=now,
        ),
        OperationalMetric(
            metric_id="metric_checkins_completed",
            event_id=brief.event_id,
            name="checkins_completed",
            value=286,
            unit="checkins",
            source="mock",
            captured_at=now,
        ),
        OperationalMetric(
            metric_id="metric_avg_queue_minutes",
            event_id=brief.event_id,
            name="avg_queue_minutes",
            value=9,
            unit="minutes",
            source="mock",
            captured_at=now,
        ),
        OperationalMetric(
            metric_id="metric_incident_response_minutes",
            event_id=brief.event_id,
            name="incident_response_minutes",
            value=4,
            unit="minutes",
            source="mock",
            captured_at=now,
        ),
        OperationalMetric(
            metric_id="metric_budget_spent_mop",
            event_id=brief.event_id,
            name="budget_spent_mop",
            value=43800,
            unit="MOP",
            source="mock",
            captured_at=now,
        ),
    ]:
        store.save_operational_metric(metric)
    for payload in load_json("merchants.json"):
        merchant = MerchantProfile.model_validate(payload)
        store.save_merchant(merchant)
        store.save_runtime_state(
            MerchantRuntimeState(
                merchant_id=merchant.merchant_id,
                inventory_status="normal",
                queue_status="normal",
                available_for_visitors=True,
                temporary_note="",
                updated_at=now,
            )
        )
    return brief
