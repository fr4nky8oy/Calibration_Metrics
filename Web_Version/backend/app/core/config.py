"""
Application Configuration Settings
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_TITLE: str = "ACX Audio Analyzer API"
    API_DESCRIPTION: str = "Professional audio analysis API for ACX audiobook standards and ElevenLabs voice cloning compliance"
    API_VERSION: str = "1.0.0"

    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "https://*.vercel.app",
        "https://*.netlify.app",
    ]

    # File Upload Settings
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB in bytes
    ALLOWED_EXTENSIONS: List[str] = [".wav", ".mp3", ".flac", ".m4a"]
    UPLOAD_DIR: str = "/tmp/audio_uploads"

    # Analysis Settings
    ENABLE_PROGRESS_TRACKING: bool = False  # For future WebSocket support

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
