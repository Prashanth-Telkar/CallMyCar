from pydantic import BaseModel, Field
from datetime import datetime


class UserRegisterRequest(BaseModel):
    phone_number: str = Field(
        ..., min_length=10, max_length=15, pattern=r"^\+?[0-9]{10,15}$"
    )


class UserResponse(BaseModel):
    id: str
    phone_number: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
