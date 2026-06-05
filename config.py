from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    WEDDING_DATE: str = "2026-09-19T12:00:00"
    SECRET_ADMIN_PASSWORD: str = "changeme"
    DATABASE_URL: str = "sqlite:///./wedding.db"


settings = Settings()