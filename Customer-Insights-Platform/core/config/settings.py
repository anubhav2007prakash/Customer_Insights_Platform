"""Centralized application settings using Pydantic Settings v2."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.config.environments import Environment


class DatabaseSettings(BaseSettings):
    """PostgreSQL connection settings."""

    model_config = SettingsConfigDict(env_prefix="DB_", extra="ignore")

    host: str = "localhost"
    port: int = 5432
    name: str = "insightforge"
    user: str = "insightforge"
    password: str = Field(default="changeme", repr=False)
    pool_size: int = 20
    max_overflow: int = 40
    pool_timeout: int = 30
    pool_recycle: int = 1800
    echo: bool = False

    @property
    def url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class SecuritySettings(BaseSettings):
    """Security and authentication settings."""

    model_config = SettingsConfigDict(env_prefix="SECURITY_", extra="ignore")

    secret_key: str = Field(default="change-me-in-production", repr=False)
    password_min_length: int = 8
    password_max_length: int = 128
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numeric: bool = True
    password_require_special: bool = True
    password_history_count: int = 5
    password_expiration_days: int = 90
    bcrypt_rounds: int = 12
    session_ttl_hours: int = 24
    remember_me_ttl_days: int = 30
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_minutes: int = 60
    jwt_refresh_ttl_days: int = 30
    max_login_attempts: int = 5
    lockout_minutes: int = 15
    email_verification_token_ttl_hours: int = 24
    password_reset_token_ttl_minutes: int = 30
    username_unique: bool = True
    require_verified_email: bool = True


class AISettings(BaseSettings):
    """AI/ML service configuration."""

    model_config = SettingsConfigDict(env_prefix="AI_", extra="ignore")

    default_model: str = "insightforge-analyst"
    max_tokens: int = 4096
    temperature: float = 0.3
    embedding_dimensions: int = 1536
    inference_timeout_seconds: int = 120


class LoggingSettings(BaseSettings):
    """Logging configuration."""

    model_config = SettingsConfigDict(env_prefix="LOG_", extra="ignore")

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    format: Literal["json", "text"] = "text"
    file_path: str | None = None
    enable_sql_logging: bool = False


class CacheSettings(BaseSettings):
    """Cache layer settings."""

    model_config = SettingsConfigDict(env_prefix="CACHE_", extra="ignore")

    enabled: bool = True
    ttl_seconds: int = 300
    backend: Literal["memory", "redis"] = "memory"
    redis_url: str | None = Field(default=None, repr=False)


class Settings(BaseSettings):
    """Root application settings — single source of truth."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "InsightForge AI"
    app_version: str = "1.0.0"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    ai: AISettings = Field(default_factory=AISettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, v: object) -> bool:
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return bool(v)

    @property
    def is_production(self) -> bool:
        return self.environment.is_production


@lru_cache
def get_settings() -> Settings:
    """Return cached settings singleton (injectable)."""
    return Settings()
