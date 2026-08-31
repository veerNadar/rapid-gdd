from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_DEV_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


class Settings(BaseSettings):
    """App configuration, loaded from environment variables / backend/.env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://postgres:postgres@localhost:5432/postgres"
    google_api_key: str = ""

    # Comma-separated list of origins allowed to call the API, e.g.
    # "https://app.example.com,https://staging.example.com". Unset in
    # dev — falls back to Vite's default port on localhost/127.0.0.1.
    # Set this in production to the deployed frontend's real origin(s).
    cors_origins_raw: str = Field(default="", validation_alias="CORS_ORIGINS")

    @property
    def cors_origins(self) -> list[str]:
        if not self.cors_origins_raw.strip():
            return _DEFAULT_DEV_ORIGINS
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


settings = Settings()
