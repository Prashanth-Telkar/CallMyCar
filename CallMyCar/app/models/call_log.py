import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CallLog(Base):
    __tablename__ = "call_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    qr_code_id: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    caller_ip: Mapped[str] = mapped_column(String(45), nullable=True)
    contact_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="call"
    )  # "call" or "whatsapp"
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
