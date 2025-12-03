# AgriCare/server/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    SMTP_HOST : str
    SMTP_PORT : int
    EMAIL_NAME : str
    EMAIL_USERNAME : str
    EMAIL_PASSWORD : str
    REDIS_URL : Optional[str] = None
    JWT_SECRET_KEY : str
    JWT_ALGORITHM : str
    JWT_EXPIRE_DAYS : int
    GOOGLE_MAPS_API_KEY : str

    # Class Variable
    model_config = SettingsConfigDict(
        env_file = str(Path(__file__).parent / ".env")
    )


Config = Settings()