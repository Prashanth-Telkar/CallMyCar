from pydantic import BaseModel, Field


class CallOwnerRequest(BaseModel):
    qr_code_id: str = Field(..., min_length=1, max_length=50)
    caller_phone: str = Field(
        ..., min_length=10, max_length=15, pattern=r"^\+?[0-9]{10,15}$"
    )


class CallOwnerResponse(BaseModel):
    status: str
    message: str
    call_id: str = ""


class WhatsAppOwnerRequest(BaseModel):
    qr_code_id: str = Field(..., min_length=1, max_length=50)
    message: str = Field(default="", max_length=500)


class OTPVerifyRequest(BaseModel):
    phone_number: str = Field(
        ..., min_length=10, max_length=15, pattern=r"^\+?[0-9]{10,15}$"
    )
    otp: str = Field(..., min_length=4, max_length=6)
