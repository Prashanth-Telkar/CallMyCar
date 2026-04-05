import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.qr_code import QRCode
from app.schemas.vehicle import LinkQRRequest
from app.schemas.qr import QRStatusResponse, QRLinkResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["qr"])


@router.post("/link-qr", response_model=QRLinkResponse, status_code=status.HTTP_200_OK)
def link_qr_to_vehicle(payload: LinkQRRequest, db: Session = Depends(get_db)):
    """Link a QR code to a vehicle owned by a registered user."""
    # Validate user
    user = db.query(User).filter(User.phone_number == payload.phone_number).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Register first.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not verified. Complete OTP verification first.",
        )

    # Validate QR exists
    qr = db.query(QRCode).filter(QRCode.qr_code_id == payload.qr_code_id).first()
    if not qr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found. Use a valid QR code ID.",
        )
    if qr.vehicle_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="QR code already linked to a vehicle.",
        )

    # Create or find vehicle
    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.vehicle_number == payload.vehicle_number.upper(),
            Vehicle.user_id == user.id,
        )
        .first()
    )
    if not vehicle:
        vehicle = Vehicle(
            user_id=user.id,
            vehicle_number=payload.vehicle_number.upper(),
        )
        db.add(vehicle)
        db.flush()

    # Link QR to vehicle
    qr.vehicle_id = vehicle.id
    qr.is_active = True
    db.commit()

    logger.info("QR %s linked to vehicle %s", payload.qr_code_id, vehicle.vehicle_number)
    return QRLinkResponse(
        qr_code_id=payload.qr_code_id,
        vehicle_number=vehicle.vehicle_number,
        status="active",
    )


@router.get("/api/qr-status/{qr_code_id}", response_model=QRStatusResponse, status_code=status.HTTP_200_OK)
def get_qr_status(qr_code_id: str, db: Session = Depends(get_db)):
    """Public endpoint: check if a QR code is active."""
    qr = db.query(QRCode).filter(QRCode.qr_code_id == qr_code_id).first()
    if not qr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found",
        )
    return QRStatusResponse(status="active" if qr.is_active else "inactive")
