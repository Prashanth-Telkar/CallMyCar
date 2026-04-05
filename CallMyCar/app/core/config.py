import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "CallMyCar"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/callmycar"

    # Exotel
    EXOTEL_SID: str = ""
    EXOTEL_API_KEY: str = ""
    EXOTEL_API_TOKEN: str = ""
    EXOTEL_VIRTUAL_NUMBER: str = ""

    # Rate limiting
    MAX_CALLS_PER_QR_PER_HOUR: int = 3

    # WhatsApp Business API (for future integration)
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_API_TOKEN: str = ""

    # Base URL for QR links
    BASE_URL: str = "http://localhost:8000"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
