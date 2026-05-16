from pathlib import Path
from typing import List, Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "E-Commerce API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    APP_ENV: Literal["development", "production"] = "development"
    SECRET_KEY: str = "secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    REFRESH_TOKEN_COOKIE_NAME: str = "refresh_token"
    REFRESH_TOKEN_COOKIE_PATH: str = "/api"
    REFRESH_TOKEN_COOKIE_SECURE: bool = True
    REFRESH_TOKEN_COOKIE_SAMESITE: Literal["strict", "lax", "none"] = "lax"
    PORT: int = 8000
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./ecommerce.db"
    MIDTRANS_SERVER_KEY: str = "midtrans_server_key"
    MIDTRANS_CLIENT_KEY: str = "midtrans_client_key"
    MIDTRANS_IS_PRODUCTION: bool = False
    MIDTRANS_FINISH_REDIRECT_URL: str = "http://localhost:5173/checkout/status?state=finish"
    MIDTRANS_ERROR_REDIRECT_URL: str = "http://localhost:5173/checkout/status?state=error"
    MIDTRANS_PENDING_REDIRECT_URL: str = "http://localhost:5173/checkout/status?state=pending"
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    MIDTRANS_USE_STUB: bool = True

    @model_validator(mode="after")
    def apply_environment_policies(self):
        if self.APP_ENV == "production":
            self.REFRESH_TOKEN_COOKIE_SECURE = True
            self.REFRESH_TOKEN_COOKIE_SAMESITE = "strict"
        else:
            self.REFRESH_TOKEN_COOKIE_SECURE = False
            self.REFRESH_TOKEN_COOKIE_SAMESITE = "lax"

        return self
    
    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")

settings = Settings()
