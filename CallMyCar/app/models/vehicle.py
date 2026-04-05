import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    vehicle_number: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )

    owner: Mapped["User"] = relationship("User", back_populates="vehicles")
    qr_codes: Mapped[list["QRCode"]] = relationship(
        "QRCode", back_populates="vehicle", lazy="selectin"
    )
