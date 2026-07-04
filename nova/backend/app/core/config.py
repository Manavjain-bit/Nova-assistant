import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Nova"
    ENV: str = os.getenv("ENV", "development")

    # Database: defaults to local SQLite for zero-config dev/testing.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./nova.db")

    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # AI providers - optional. If absent, services fall back to local/mock logic.
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    ELEVENLABS_API_KEY: str | None = os.getenv("ELEVENLABS_API_KEY")
    GOOGLE_CLIENT_ID: str | None = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str | None = os.getenv("GOOGLE_CLIENT_SECRET")

    FILE_SEARCH_WORKSPACE_DIR: str = os.getenv("FILE_SEARCH_WORKSPACE_DIR", "./workspace")

    class Config:
        env_file = ".env"


settings = Settings()
