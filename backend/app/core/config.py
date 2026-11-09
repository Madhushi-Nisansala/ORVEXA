from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="ORVEXA", validation_alias="APP_NAME")
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    app_version: str = Field(default="0.1.0", validation_alias="APP_VERSION")
    debug: bool = Field(default=False, validation_alias="DEBUG")
    api_host: str = Field(default="127.0.0.1", validation_alias="API_HOST")
    api_port: int = Field(default=8000, validation_alias="API_PORT")
    api_v1_prefix: str = Field(default="/api/v1", validation_alias="API_V1_PREFIX")
    secret_key: SecretStr = Field(
        default=SecretStr("CHANGE_ME"), validation_alias="SECRET_KEY"
    )
    jwt_secret_key: SecretStr = Field(
        validation_alias="JWT_SECRET_KEY",
    )
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=15, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = Field(
        default=14, validation_alias="REFRESH_TOKEN_EXPIRE_DAYS"
    )
    auth_rate_limit_window_seconds: int = Field(
        default=60, validation_alias="AUTH_RATE_LIMIT_WINDOW_SECONDS"
    )
    auth_rate_limit_attempts: int = Field(
        default=10, validation_alias="AUTH_RATE_LIMIT_ATTEMPTS"
    )
    database_url: str | None = Field(default=None, validation_alias="DATABASE_URL")
    postgres_db: str = Field(default="orvexa_db", validation_alias="POSTGRES_DB")
    postgres_user: str = Field(default="orvexa", validation_alias="POSTGRES_USER")
    postgres_password: SecretStr = Field(
        default=SecretStr("your_local_database_password"), validation_alias="POSTGRES_PASSWORD"
    )
    postgres_host: str = Field(default="localhost", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, validation_alias="POSTGRES_PORT")
    cors_allowed_origins: str = Field(
        default="http://localhost:3000",
        validation_alias="CORS_ALLOWED_ORIGINS",
    )
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    database_connect_timeout: float = Field(
        default=3.0, validation_alias="DATABASE_CONNECT_TIMEOUT"
    )
    database_pool_size: int = Field(default=5, validation_alias="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=5, validation_alias="DATABASE_MAX_OVERFLOW")
    document_storage_root: str = Field(
        default="storage/documents", validation_alias="DOCUMENT_STORAGE_ROOT"
    )
    document_max_file_size_bytes: int = Field(
        default=25 * 1024 * 1024, validation_alias="DOCUMENT_MAX_FILE_SIZE_BYTES"
    )
    worker_poll_interval_seconds: float = Field(default=2.0, validation_alias="WORKER_POLL_INTERVAL_SECONDS")
    worker_stale_timeout_seconds: int = Field(default=900, validation_alias="WORKER_STALE_TIMEOUT_SECONDS")
    worker_error_backoff_seconds: float = Field(default=5.0, validation_alias="WORKER_ERROR_BACKOFF_SECONDS")
    worker_schema_revision: str | None = Field(default=None, validation_alias="WORKER_SCHEMA_REVISION")
    extraction_max_attempts: int = Field(default=3, validation_alias="EXTRACTION_MAX_ATTEMPTS")
    extraction_retry_base_delay_seconds: int = Field(default=30, validation_alias="EXTRACTION_RETRY_BASE_DELAY_SECONDS")
    extraction_retry_max_delay_seconds: int = Field(default=3600, validation_alias="EXTRACTION_RETRY_MAX_DELAY_SECONDS")
    extraction_processing_version: str = Field(default="stage2-v1", validation_alias="EXTRACTION_PROCESSING_VERSION")
    tesseract_cmd: str | None = Field(default=None, validation_alias="TESSERACT_CMD")
    tessdata_prefix: str | None = Field(default=None, validation_alias="TESSDATA_PREFIX")
    ocr_default_lang: str = Field(default="eng", validation_alias="OCR_DEFAULT_LANG")
    ocr_supported_languages: str = Field(default="eng,sin,tam", validation_alias="OCR_SUPPORTED_LANGUAGES")
    ocr_timeout_seconds: int = Field(default=60, validation_alias="OCR_TIMEOUT_SECONDS")
    ocr_max_image_pixels: int = Field(default=25_000_000, validation_alias="OCR_MAX_IMAGE_PIXELS")
    analysis_provider: str = Field(default="unavailable", validation_alias="ANALYSIS_PROVIDER")
    analysis_model: str | None = Field(default=None, validation_alias="ANALYSIS_MODEL")
    openai_api_key: SecretStr | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_model: str | None = Field(default=None, validation_alias="OPENAI_MODEL")
    analysis_timeout_seconds: int = Field(default=60, validation_alias="ANALYSIS_TIMEOUT_SECONDS")
    analysis_max_input_characters: int = Field(default=120_000, validation_alias="ANALYSIS_MAX_INPUT_CHARACTERS")
    analysis_max_repair_attempts: int = Field(default=1, validation_alias="ANALYSIS_MAX_REPAIR_ATTEMPTS")
    analysis_retry_attempts: int = Field(default=2, validation_alias="ANALYSIS_RETRY_ATTEMPTS")
    analysis_retry_base_delay_seconds: float = Field(default=0.5, validation_alias="ANALYSIS_RETRY_BASE_DELAY_SECONDS")

    @field_validator("api_v1_prefix")
    @classmethod
    def normalize_prefix(cls, value: str) -> str:
        return "/" + value.strip("/")

    @field_validator("jwt_algorithm")
    @classmethod
    def validate_jwt_algorithm(cls, value: str) -> str:
        if value not in {"HS256"}:
            raise ValueError("Unsupported JWT algorithm")
        return value

    @field_validator("database_pool_size", "database_max_overflow")
    @classmethod
    def validate_pool_settings(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Database pool settings must not be negative")
        return value

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, value: SecretStr) -> SecretStr:
        secret = value.get_secret_value()
        if secret in {"", "CHANGE_ME"} or len(secret.encode("utf-8")) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 bytes")
        return value

    @field_validator("worker_poll_interval_seconds", "worker_error_backoff_seconds")
    @classmethod
    def validate_worker_delays(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("Worker delays must be positive")
        return value

    @field_validator("worker_stale_timeout_seconds")
    @classmethod
    def validate_worker_stale_timeout(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Worker stale timeout must be positive")
        return value

    @field_validator("analysis_provider")
    @classmethod
    def validate_analysis_provider(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"", "none", "unavailable", "openai"}:
            raise ValueError("Unsupported document intelligence provider")
        return normalized or "unavailable"

    @field_validator("analysis_timeout_seconds", "analysis_max_input_characters")
    @classmethod
    def validate_positive_analysis_setting(cls, value: int) -> int:
        if value < 1:
            raise ValueError("Analysis settings must be positive")
        return value

    @field_validator("analysis_retry_attempts")
    @classmethod
    def validate_retry_attempts(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Analysis retry attempts must not be negative")
        return value

    @field_validator("analysis_retry_base_delay_seconds")
    @classmethod
    def validate_retry_delay(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Analysis retry delay must not be negative")
        return value

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.app_env.lower() in {"production", "staging"}:
            jwt_secret = self.jwt_secret_key.get_secret_value()
            if jwt_secret in {"", "CHANGE_ME"} or len(jwt_secret) < 32:
                raise ValueError("JWT_SECRET_KEY must be at least 32 characters in production")
            if self.debug:
                raise ValueError("DEBUG must be false in production and staging")
            if not self.cors_origins or "*" in self.cors_origins:
                raise ValueError("CORS_ALLOWED_ORIGINS must contain explicit origins in production")
            if self.document_max_file_size_bytes > 100 * 1024 * 1024:
                raise ValueError("DOCUMENT_MAX_FILE_SIZE_BYTES is too large for production")
        return self

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()
        ]

    @property
    def configured_ocr_languages(self) -> list[str]:
        return [language.strip() for language in self.ocr_supported_languages.split(",") if language.strip()]

    def get_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        password = quote_plus(self.postgres_password.get_secret_value())
        return f"postgresql+asyncpg://{quote_plus(self.postgres_user)}:{password}@{self.postgres_host}:{self.postgres_port}/{quote_plus(self.postgres_db)}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
