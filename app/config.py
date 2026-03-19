from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración de la aplicación"""

    # App
    APP_NAME: str = "CareldPOS"
    APP_VERSION: str = "0.3.1"
    DEBUG: bool = True

    # Server
    PORT: int = 8100

    # Database
    DATABASE_URL: str = "sqlite:///./data/repair_shop.db"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Obtener configuración cached"""
    return Settings()


settings = get_settings()
