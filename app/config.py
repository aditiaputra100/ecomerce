from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "E-Commerce API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    PORT: int = 8000
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./ecommerce.db"
    MIDTRANS_SERVER_KEY: str
    MIDTRANS_CLIENT_KEY: str
    MIDTRANS_IS_PRODUCTION: bool = False
    MIDTRANS_FINISH_REDIRECT_URL: str = "http://localhost:5173/checkout/status?state=finish"
    MIDTRANS_ERROR_REDIRECT_URL: str = "http://localhost:5173/checkout/status?state=error"
    MIDTRANS_PENDING_REDIRECT_URL: str = "http://localhost:5173/checkout/status?state=pending"
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    MIDTRANS_USE_STUB: bool = True
    
    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")

settings = Settings()
