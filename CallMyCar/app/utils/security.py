from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.call_log import CallLog
from app.core.config import get_settings

settings = get_settings()


def is_rate_limited(db: Session, qr_code_id: str) -> bool:
    """Check if a QR code has exceeded the max calls per hour."""
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    count = (
        db.query(func.count(CallLog.id))
        .filter(
            CallLog.qr_code_id == qr_code_id,
            CallLog.created_at >= one_hour_ago,
            CallLog.status == "success",
        )
        .scalar()
    )
    return count >= settings.MAX_CALLS_PER_QR_PER_HOUR
