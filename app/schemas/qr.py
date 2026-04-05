from pydantic import BaseModel


class QRStatusResponse(BaseModel):
    status: str  # "active" | "inactive"


class QRLinkResponse(BaseModel):
    qr_code_id: str
    vehicle_number: str
    status: str
