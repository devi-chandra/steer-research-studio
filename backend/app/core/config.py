import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Steer — Doctor-Led Research-to-Content Studio"
    PROJECT_VERSION: str = "2.0.0"
    DEBUG: bool = True
    PORT: int = 8005
    HOST: str = "127.0.0.1"

    # Base Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    STORAGE_DIR: Path = BASE_DIR / "storage"
    UPLOADS_DIR: Path = STORAGE_DIR / "uploads"
    GENERATED_DIR: Path = STORAGE_DIR / "generated"
    EXPORTS_DIR: Path = STORAGE_DIR / "exports"
    DATABASE_PATH: Path = STORAGE_DIR / "steer_studio.db"

    # AI Configuration
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    AI_PROVIDER: str = "auto"  # auto, gemini, openai, deterministic

    # TTS Configuration
    TTS_PROVIDER: str = "edge-tts"  # edge-tts, gtts, pyttsx3
    
    # Steer Brand Palette
    COLOR_CREAM: str = "#F5EBDF"
    COLOR_RUST: str = "#C04E2A"
    COLOR_MAROON: str = "#661414"
    COLOR_INK: str = "#351D1D"
    COLOR_CLAY: str = "#B58777"
    COLOR_BLUSH: str = "#E6CBBD"
    COLOR_PAPER: str = "#F8F2EB"

    # Supported Regional Languages
    SUPPORTED_LANGUAGES: list = [
        {"code": "en", "label": "English (Primary)", "tts_voice": "en-US-ChristopherNeural", "native_name": "English"},
        {"code": "hi_en", "label": "Hindi + English (Hinglish)", "tts_voice": "hi-IN-MadhurNeural", "native_name": "हिन्दी + English"},
        {"code": "te_en", "label": "Telugu + English", "tts_voice": "te-IN-MohanNeural", "native_name": "తెలుగు + English"},
        {"code": "ta_en", "label": "Tamil + English", "tts_voice": "ta-IN-ValluvarNeural", "native_name": "தமிழ் + English"},
        {"code": "kn_en", "label": "Kannada + English", "tts_voice": "kn-IN-GaganNeural", "native_name": "ಕನ್ನಡ + English"},
        {"code": "ml_en", "label": "Malayalam + English", "tts_voice": "ml-IN-MidhunNeural", "native_name": "മലയാളം + English"}
    ]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Ensure directories exist
for path in [
    settings.STORAGE_DIR,
    settings.UPLOADS_DIR,
    settings.GENERATED_DIR / "carousels",
    settings.GENERATED_DIR / "posts",
    settings.GENERATED_DIR / "reels",
    settings.GENERATED_DIR / "audio",
    settings.GENERATED_DIR / "pptx",
    settings.EXPORTS_DIR
]:
    path.mkdir(parents=True, exist_ok=True)
