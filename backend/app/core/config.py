import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Steer Research-to-Content Studio"
    VERSION: str = "1.0.0"
    
    # Server
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    # Base Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    STORAGE_DIR: Path = BASE_DIR.parent / "storage"
    
    # Database
    DATABASE_URL: str = ""

    # AI Configuration
    AI_PROVIDER: str = "local_sample"  # "gemini", "openai", "local_sample"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # Media & TTS
    TTS_ENGINE: str = "edge-tts"  # "edge-tts" or "pyttsx3"
    TTS_VOICE: str = "en-IN-NeerjaNeural"
    VIDEO_FPS: int = 30
    VIDEO_WIDTH: int = 1080
    VIDEO_HEIGHT: int = 1920
    FFMPEG_PATH: str = "ffmpeg"

    # Brand Colors (Hex and RGB)
    BRAND_CREAM: str = "#F5EBDF"
    BRAND_RUST: str = "#C04E2A"
    BRAND_MAROON: str = "#661414"
    BRAND_INK: str = "#351D1D"
    BRAND_CLAY: str = "#B58777"
    BRAND_BLUSH: str = "#E6CBBD"
    BRAND_SOFT_PAPER: str = "#F8F2EB"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def uploads_dir(self) -> Path:
        p = self.STORAGE_DIR / "uploads"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def generated_dir(self) -> Path:
        p = self.STORAGE_DIR / "generated"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def sample_papers_dir(self) -> Path:
        p = self.BASE_DIR / "sample_papers"
        p.mkdir(parents=True, exist_ok=True)
        return p

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

if not settings.DATABASE_URL:
    db_path = settings.STORAGE_DIR / "steer_studio.db"
    settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    settings.DATABASE_URL = f"sqlite:///{db_path}"
