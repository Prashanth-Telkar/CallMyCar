import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.qr_code import QRCode
from app.models.call_log import CallLog
from app.schemas.call import CallOwnerRequest, CallOwnerResponse, WhatsAppOwnerRequest
from app.services import exotel_service, whatsapp_service
from app.utils.security import is_rate_limited

logger = logging.getLogger(__name__)
router = APIRouter(tags=["call"])


@router.post("/call-owner", response_model=CallOwnerResponse, status_code=status.HTTP_200_OK)
def call_owner(
    payload: CallOwnerRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Initiate a masked call to the vehicle owner via QR code."""
    caller_ip = request.client.host if request.client else "unknown"

    # Validate QR
    qr = db.query(QRCode).filter(QRCode.qr_code_id == payload.qr_code_id).first()
    if not qr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found",
        )
    if not qr.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="QR code is inactive. Vehicle owner has not linked this QR.",
        )

    # Rate limit check
    if is_rate_limited(db, payload.qr_code_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many calls for this QR code. Try again later.",
        )

    # Get owner phone
    vehicle = qr.vehicle
    if not vehicle or not vehicle.owner:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Vehicle owner data is missing.",
        )

    owner_phone = vehicle.owner.phone_number

    # Call via Exotel
    try:
        result = exotel_service.connect_call(
            owner_phone=owner_phone,
            caller_phone=payload.caller_phone,
        )
        call_status = "success"
    except Exception as e:
        logger.error("Call failed for QR %s: %s", payload.qr_code_id, str(e))
        call_status = "failed"
        result = {}

    # Log the call
    call_log = CallLog(
        qr_code_id=payload.qr_code_id,
        caller_ip=caller_ip,
        contact_type="call",
        status=call_status,
    )
    db.add(call_log)
    db.commit()

    if call_status == "failed":
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to connect call. Try again later.",
        )

    logger.info("Call initiated: qr=%s, ip=%s", payload.qr_code_id, caller_ip)
    return CallOwnerResponse(
        status="calling",
        message="Connecting you to the vehicle owner.",
        call_id=result.get("call_id", ""),
    )


@router.post("/whatsapp-owner", response_model=CallOwnerResponse, status_code=status.HTTP_200_OK)
def whatsapp_owner(
    payload: WhatsAppOwnerRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Send a masked WhatsApp message to the vehicle owner via QR code."""
    caller_ip = request.client.host if request.client else "unknown"

    # Validate QR
    qr = db.query(QRCode).filter(QRCode.qr_code_id == payload.qr_code_id).first()
    if not qr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found",
        )
    if not qr.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="QR code is inactive. Vehicle owner has not linked this QR.",
        )

    # Rate limit check (shared with calls)
    if is_rate_limited(db, payload.qr_code_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many contacts for this QR code. Try again later.",
        )

    # Get owner info
    vehicle = qr.vehicle
    if not vehicle or not vehicle.owner:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Vehicle owner data is missing.",
        )

    owner_phone = vehicle.owner.phone_number
    vehicle_number = vehicle.vehicle_number

    # Send WhatsApp (mock)
    try:
        result = whatsapp_service.send_whatsapp(
            owner_phone=owner_phone,
            vehicle_number=vehicle_number,
            message=payload.message,
        )
        wa_status = "success"
    except Exception as e:
        logger.error("WhatsApp failed for QR %s: %s", payload.qr_code_id, str(e))
        wa_status = "failed"

    # Log
    call_log = CallLog(
        qr_code_id=payload.qr_code_id,
        caller_ip=caller_ip,
        contact_type="whatsapp",
        status=wa_status,
    )
    db.add(call_log)
    db.commit()

    if wa_status == "failed":
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to send WhatsApp. Try again later.",
        )

    logger.info("WhatsApp sent: qr=%s, ip=%s", payload.qr_code_id, caller_ip)
    return CallOwnerResponse(status="sent", message="WhatsApp message sent to the vehicle owner.")
