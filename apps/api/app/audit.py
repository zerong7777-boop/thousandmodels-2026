from datetime import UTC, datetime
from uuid import uuid4

from app.schemas import AuditLog


def build_audit_log(
    event_id: str,
    actor_type: str,
    actor_id: str,
    action_type: str,
    note: str,
    input_ref: str = "",
    output_ref: str = "",
) -> AuditLog:
    return AuditLog(
        log_id=f"log_{uuid4().hex[:10]}",
        event_id=event_id,
        actor_type=actor_type,
        actor_id=actor_id,
        action_type=action_type,
        input_ref=input_ref,
        output_ref=output_ref,
        timestamp=datetime.now(UTC).isoformat(),
        note=note,
    )
