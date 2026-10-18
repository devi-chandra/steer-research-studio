import shutil
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.core.config import settings
from app.core.ai_provider import ai_provider
from app.services.reel_generation.video_renderer import is_ffmpeg_available

router = APIRouter(prefix="/api/settings", tags=["Settings & Status"])

@router.get("/sample-pdf")
def get_sample_pdf():
    sample_path = settings.BASE_DIR / "sample_papers" / "stamatakis_vilpa_nature_med_2022.pdf"
    if not sample_path.is_file():
        raise HTTPException(status_code=404, detail="Sample research PDF is unavailable.")
    return FileResponse(sample_path, media_type="application/pdf", filename=sample_path.name)

@router.get("/status")
def get_system_status():
    ai_status = ai_provider.get_status()
    ffmpeg_ok = is_ffmpeg_available()

    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "ai_provider": ai_status,
        "tts_provider": settings.TTS_PROVIDER,
        "supported_languages": settings.SUPPORTED_LANGUAGES,
        "ffmpeg_available": ffmpeg_ok,
        "ffmpeg_path": shutil.which("ffmpeg") or "Not found in PATH",
        "brand_palette": {
            "cream": settings.COLOR_CREAM,
            "rust": settings.COLOR_RUST,
            "maroon": settings.COLOR_MAROON,
            "ink": settings.COLOR_INK,
            "clay": settings.COLOR_CLAY,
            "blush": settings.COLOR_BLUSH,
            "paper": settings.COLOR_PAPER
        },
        "storage": {
            "uploads_dir": str(settings.UPLOADS_DIR),
            "generated_dir": str(settings.GENERATED_DIR),
            "exports_dir": str(settings.EXPORTS_DIR)
        }
    }
