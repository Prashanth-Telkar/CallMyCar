from pydantic import BaseModel, Field


class LinkQRRequest(BaseModel):
    qr_code_id: str = Field(..., min_length=1, max_length=50)
    vehicle_number: str = Field(..., min_length=1, max_length=20)
    phone_number: str = Field(
        ..., min_length=10, max_length=15, pattern=r"^\+?[0-9]{10,15}$"
    )


class VehicleResponse(BaseModel):
    id: str
    vehicle_number: str
    user_id: str

    model_config = {"from_attributes": True}
