"""
Configuration settings for A/B This backend
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # API settings
    app_name: str = "A/B This API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"

    # CORS settings
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "https://*.vercel.app",
    ]

    # File upload settings
    max_file_size_mb: int = 50
    allowed_extensions: List[str] = [".wav", ".mp3", ".flac", ".m4a", ".aiff", ".ogg"]

    # Audio processing settings
    downsample_sr: int = 22050  # Downsample to 22kHz for speed
    analysis_timeout: int = 120  # Maximum 2 minutes per analysis

    # Environment
    environment: str = "development"
    debug: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()
