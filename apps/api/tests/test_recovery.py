from app.schemas import MerchantRuntimeState
from app.services.recovery import build_inventory_recovery, build_weather_recovery


def test_inventory_recovery_requires_approval():
    action = build_inventory_recovery(
        "demo-night-tour",
        MerchantRuntimeState(
            merchant_id="m001",
            inventory_status="sold_out",
            queue_status="busy",
            available_for_visitors=False,
            updated_at="2026-07-18T19:00:00Z",
        ),
    )
    assert action.approval_status == "pending"
    assert action.requires_approval is True
    assert "m001" in action.affected_merchants
    assert "游客" not in action.action_id


def test_weather_recovery_switches_indoor_route():
    action = build_weather_recovery("demo-night-tour")
    assert action.trigger_type == "weather"
    assert "m008" in action.affected_merchants
    assert "雨天" in " ".join(action.recommended_changes)
