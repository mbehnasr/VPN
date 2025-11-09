import secrets
from functools import lru_cache
from typing import List

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    telegram_token: str = Field(..., env="TELEGRAM_TOKEN")
    admin_chat_ids: List[int] = Field(default_factory=list, env="ADMIN_CHAT_IDS")
    database_url: str = Field(default="sqlite:///./vpn.db", env="DATABASE_URL")
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    auto_accept_days: int = Field(default=3)
    trial_quota_mb: int = Field(default=200)
    trial_duration_days: int = Field(default=1)
    base_currency: str = Field(default="EUR")
    stripe_api_key: str | None = None
    zarinpal_merchant_id: str | None = None

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
