from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
UPLOAD_ROOT = BACKEND_DIR / "uploads"


class Settings(BaseSettings):
    # Reads backend/.env locally; on the server systemd injects deploy/.env.production.
    model_config = SettingsConfigDict(env_file=str(BACKEND_DIR / ".env"), extra="ignore")

    app_name: str = "OffmarketStream API"
    secret_key: str = "offmarketstream-fyp-demo-secret-change-in-prod"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    database_url: str = "sqlite:///./offmarketstream.db"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "https://prop-iq-eight.vercel.app",
        "http://3.14.42.168",
    ]
    rentcast_api_key: str = ""

    # Gemini vision (free tier: ~15 requests/min, ~500/day on flash-lite)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"
    gemini_timeout_seconds: float = 25.0
    gemini_max_images: int = 10
    gemini_rpm_limit: int = 14


settings = Settings()
