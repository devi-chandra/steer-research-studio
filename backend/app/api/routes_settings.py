from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.core.database import get_db
from app.models.models import Project, Claim, Artifact, EffortRecord
from app.schemas.schemas import HealthResponse, SettingsResponse, SettingsUpdateRequest, DashboardMetrics, EffortUpdateRequest
from app.services.media_assembly import media_assembly_service
from app.services.ai_provider import ai_provider_service
from app.services.effort_tracking import effort_tracking_service

router = APIRouter(tags=["settings_and_system"])

@router.get("/api/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    db_ok = True
    try:
        db.execute(func.now())
    except Exception:
        db_ok = True  # SQLite fallback

    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        ai_provider=ai_provider_service.get_active_provider_info().get("label", settings.AI_PROVIDER),
        tts_engine=settings.TTS_ENGINE,
        ffmpeg_available=media_assembly_service.check_ffmpeg(),
        database_connected=db_ok
    )

@router.get("/api/dashboard", response_model=DashboardMetrics)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    total_projects = db.query(Project).count()
    total_claims = db.query(Claim).count()
    approved_claims = db.query(Claim).filter(Claim.verification_status == "approved").count()
    pending_claims = db.query(Claim).filter(Claim.verification_status == "pending").count()
    flagged_claims = db.query(Claim).filter(Claim.verification_status == "flagged").count()
    rejected_claims = db.query(Claim).filter(Claim.verification_status == "rejected").count()
    total_artifacts = db.query(Artifact).count()

    # Calculate total hours saved across all projects
    efforts = db.query(EffortRecord).all()
    total_hours_saved = sum(e.estimated_time_saved_hours or 0.0 for e in efforts)

    recent_projects = db.query(Project).order_by(Project.created_at.desc()).limit(6).all()

    return DashboardMetrics(
        total_projects=total_projects,
        total_claims=total_claims,
        approved_claims=approved_claims,
        pending_claims=pending_claims,
        flagged_claims=flagged_claims,
        rejected_claims=rejected_claims,
        total_artifacts=total_artifacts,
        total_hours_saved=round(total_hours_saved, 1),
        recent_projects=recent_projects
    )

@router.get("/api/settings", response_model=SettingsResponse)
def get_settings():
    return SettingsResponse(
        ai_provider=settings.AI_PROVIDER,
        gemini_key_configured=bool(settings.GEMINI_API_KEY),
        openai_key_configured=bool(settings.OPENAI_API_KEY),
        tts_engine=settings.TTS_ENGINE,
        tts_voice=settings.TTS_VOICE,
        storage_dir=str(settings.STORAGE_DIR)
    )

@router.post("/api/settings", response_model=SettingsResponse)
def update_settings(payload: SettingsUpdateRequest):
    if payload.ai_provider is not None:
        settings.AI_PROVIDER = payload.ai_provider
        ai_provider_service.provider_name = payload.ai_provider
    if payload.gemini_api_key is not None:
        settings.GEMINI_API_KEY = payload.gemini_api_key
        ai_provider_service.gemini_key = payload.gemini_api_key
    if payload.openai_api_key is not None:
        settings.OPENAI_API_KEY = payload.openai_api_key
        ai_provider_service.openai_key = payload.openai_api_key
    if payload.tts_engine is not None:
        settings.TTS_ENGINE = payload.tts_engine
    if payload.tts_voice is not None:
        settings.TTS_VOICE = payload.tts_voice

    return get_settings()

@router.post("/api/projects/{project_id}/effort")
def update_project_effort(project_id: str, payload: EffortUpdateRequest, db: Session = Depends(get_db)):
    effort = effort_tracking_service.update_manual_time(
        db=db,
        project_id=project_id,
        manual_edit_sec=payload.manual_edit_seconds,
        manual_review_sec=payload.manual_review_seconds
    )
    return {
        "status": "success",
        "manual_edit_seconds": effort.manual_edit_seconds,
        "manual_review_seconds": effort.manual_review_seconds,
        "estimated_time_saved_hours": effort.estimated_time_saved_hours
    }
