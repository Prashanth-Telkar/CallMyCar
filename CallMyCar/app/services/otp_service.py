import logging

logger = logging.getLogger(__name__)

# In-memory OTP store: phone_number -> otp
# For MVP, OTP is always "1234"
_otp_store: dict[str, str] = {}

MOCK_OTP = "1234"


def send_otp(phone_number: str) -> bool:
    """Send OTP to phone number. Mock implementation always stores '1234'."""
    _otp_store[phone_number] = MOCK_OTP
    logger.info("OTP sent to %s (mock: %s)", phone_number, MOCK_OTP)
    return True


def verify_otp(phone_number: str, otp: str) -> bool:
    """Verify OTP for phone number."""
    stored = _otp_store.get(phone_number)
    if stored and stored == otp:
        _otp_store.pop(phone_number, None)
        logger.info("OTP verified for %s", phone_number)
        return True
    logger.warning("OTP verification failed for %s", phone_number)
    return False
