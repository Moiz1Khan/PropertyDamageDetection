from pydantic_settings import BaseSettings


class Settings(BaseSettings):
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


settings = Settings()
