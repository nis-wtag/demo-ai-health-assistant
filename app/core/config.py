from pathlib import Path
from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    APP_ENV: str = Field("dev", validate_default=True)

    # Database configuration
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    # Test Database configuration
    POSTGRES_TEST_USER: str
    POSTGRES_TEST_PASSWORD: str
    POSTGRES_TEST_HOST: str
    POSTGRES_TEST_PORT: int
    POSTGRES_TEST_DB: str

    # JWT settings for authentication
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # JWT token values
    COOKIE_SECURE: bool = True
    COOKIE_HTTPONLY: bool = True
    COOKIE_SAMESITE: str = "strict"

    # Gemini API Key
    GEMINI_API_KEY: str

    @property
    def DATABASE_URL(self):
        if self.APP_ENV == "dev":
            return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        else:
            return f"postgresql+psycopg2://{self.POSTGRES_TEST_USER}:{self.POSTGRES_TEST_PASSWORD}@{self.POSTGRES_TEST_HOST}:{self.POSTGRES_TEST_PORT}/{self.POSTGRES_TEST_DB}"

    @property
    def TEST_SERVER_DATABASE_URL(self):
        return f"postgresql+psycopg2://{self.POSTGRES_TEST_USER}:{self.POSTGRES_TEST_PASSWORD}@{self.POSTGRES_TEST_HOST}:{self.POSTGRES_TEST_PORT}/"

    # Pydantic model configuration to load from the .env file
    env_file_path: ClassVar[Path] = Path(__file__).parent.parent.parent / ".env"

    model_config = SettingsConfigDict(
        env_file=env_file_path, env_file_encoding="utf-8", case_sensitive=True
    )


# Create a single instance of the settings to be used throughout the application
settings = Settings()
