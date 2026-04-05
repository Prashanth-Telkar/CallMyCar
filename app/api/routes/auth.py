import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserRegisterRequest, UserResponse
from app.schemas.call import OTPVerifyRequest
from app.services import otp_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["auth"])


@router.post("/register", response_model=dict, status_code=status.HTTP_200_OK)
def register_user(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register user and send OTP."""
    existing = db.query(User).filter(User.phone_number == payload.phone_number).first()
    if existing:
        # User exists — just resend OTP
        otp_service.send_otp(payload.phone_number)
        return {"message": "OTP sent to registered number"}

    user = User(phone_number=payload.phone_number)
    db.add(user)
    db.commit()
    db.refresh(user)

    otp_service.send_otp(payload.phone_number)
    logger.info("User registered: %s", payload.phone_number)
    return {"message": "OTP sent. Verify to complete registration."}


@router.post("/verify", response_model=dict, status_code=status.HTTP_200_OK)
def verify_otp(payload: OTPVerifyRequest, db: Session = Depends(get_db)):
    """Verify OTP and activate user."""
    if not otp_service.verify_otp(payload.phone_number, payload.otp):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP",
        )

    user = db.query(User).filter(User.phone_number == payload.phone_number).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please register first.",
        )

    user.is_active = True
    db.commit()
    logger.info("User verified: %s", payload.phone_number)
    return {"message": "Phone number verified successfully"}
