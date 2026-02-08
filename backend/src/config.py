from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str
    log_level: str = "info"
    debug: bool = False
    auth_secret: str = "your-super-secret-key-change-this-in-production"
    better_auth_secret: str = "your-super-secret-key-change-this-in-production"
    better_auth_url: str = "http://localhost:8001"
    jwt_secret: str = "176f456422b77149264b6bd478543c5a7d4a5c1d5870524eaf13e92bac252a2df1f5d6b296112e0ecee4d76704f1559d0c04ef6c0271274cce0349b184a4871e"
    jwt_expiration_delta_minutes: int = 30
    groq_api_key: str = ""
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "llama-3.3-70b-versatile"

    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8001

    # CORS configuration
    allowed_origins: str = "http://localhost:3000"

    # Rate limiting configuration
    enable_rate_limiting: bool = False
    rate_limit_per_minute: int = 100

    class Config:
        env_file = ".env"


settings = Settings()