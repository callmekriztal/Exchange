from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App & Environment
    APP_ENV: str = "development"
    APP_NAME: str = "The AI Economy"
    DEBUG: bool = True
    PORT: int = 8000
    SECRET_KEY: str = "change_this_to_a_super_secret_key_at_least_32_chars_long"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres_dev_password@db:5432/ai_economy_db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres_dev_password"
    POSTGRES_DB: str = "ai_economy_db"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    # OpenAI API
    OPENAI_API_KEY: str = "mock-or-actual-openai-api-key"
    OPENAI_MODEL: str = "gpt-4o-mini"

    # PayPal Sandbox Configuration
    PAYPAL_MODE: str = "sandbox"
    PAYPAL_MOCK_MODE: bool = False
    PAYPAL_CLIENT_ID: str = ""
    PAYPAL_CLIENT_SECRET: str = ""
    PAYPAL_WEBHOOK_ID: str = ""
    PAYPAL_BASE_URL: str = "https://api-m.sandbox.paypal.com"

    # CORS & Frontend
    FRONTEND_URL: str = "http://localhost:5173"
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Platform & Accounting
    PLATFORM_FEE_PERCENTAGE: float = 0.05
    DEFAULT_CURRENCY: str = "USD"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()
