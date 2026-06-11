from datetime import UTC, datetime

from app.schemas import Incident, MerchantRuntimeState


def incident_from_runtime_state(event_id: str, state: MerchantRuntimeState) -> Incident | None:
    if state.inventory_status == "sold_out":
        return Incident(
            incident_id=f"inc_{event_id}_{state.merchant_id}_inventory",
            event_id=event_id,
            type="inventory",
            severity="high",
            source="merchant",
            trigger_detail=f"{state.merchant_id} inventory_status=sold_out",
            affected_route_points=["rp001"],
            affected_merchants=[state.merchant_id],
            status="open",
            created_at=datetime.now(UTC).isoformat(),
        )
    if state.queue_status == "overloaded":
        return Incident(
            incident_id=f"inc_{event_id}_{state.merchant_id}_queue",
            event_id=event_id,
            type="queue",
            severity="medium",
            source="merchant",
            trigger_detail=f"{state.merchant_id} queue_status=overloaded",
            affected_route_points=["rp001"],
            affected_merchants=[state.merchant_id],
            status="open",
            created_at=datetime.now(UTC).isoformat(),
        )
    return None
