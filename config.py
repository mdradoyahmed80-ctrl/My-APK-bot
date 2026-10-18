import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    bot_token: str = ""
    owner_telegram_id: int = 0
    # Put primary and backup Grok keys in one Render variable, separated by a comma.
    ai_api_key: str = ""
    ai_base_url: str = "https://api.x.ai/v1"
    ai_model: str = "grok-3-mini"
    database_url: str = "sqlite:///./agent.db"
    public_base_url: str = "http://127.0.0.1:8000"
    android_device_token: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

def get_ai_keys() -> list[str]:
    return [key.strip() for key in settings.ai_api_key.replace("\n", ",").split(",") if key.strip()]
