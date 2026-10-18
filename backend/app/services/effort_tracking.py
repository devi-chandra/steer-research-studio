from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.models import EffortRecord, Project

class EffortTrackingService:
    @staticmethod
    def get_or_create_effort_record(db: Session, project_id: str) -> EffortRecord:
        record = db.query(EffortRecord).filter(EffortRecord.project_id == project_id).first()
        if not record:
            record = EffortRecord(
                project_id=project_id,
                ingest_duration_ms=0,
                ai_extraction_duration_ms=0,
                ai_content_duration_ms=0,
                media_rendering_duration_ms=0,
                total_ai_duration_ms=0,
                manual_edit_seconds=0,
                manual_review_seconds=0,
                estimated_traditional_hours=4.5,
                estimated_time_saved_hours=4.0
            )
            db.add(record)
            db.commit()
            db.refresh(record)
        return record

    @staticmethod
    def record_automated_durations(
        db: Session,
        project_id: str,
        ingest_ms: int = 0,
        extraction_ms: int = 0,
        content_ms: int = 0,
        rendering_ms: int = 0
    ) -> EffortRecord:
        record = EffortTrackingService.get_or_create_effort_record(db, project_id)
        if ingest_ms > 0:
            record.ingest_duration_ms = ingest_ms
        if extraction_ms > 0:
            record.ai_extraction_duration_ms = extraction_ms
        if content_ms > 0:
            record.ai_content_duration_ms = content_ms
        if rendering_ms > 0:
            record.media_rendering_duration_ms = rendering_ms
            
        record.total_ai_duration_ms = (
            record.ingest_duration_ms +
            record.ai_extraction_duration_ms +
            record.ai_content_duration_ms +
            record.media_rendering_duration_ms
        )
        
        # Calculate time saved estimate
        # Manual baseline: ~4.5 hours (270 mins) for manual medical paper review, claim extraction, 6 carousel slides, static post, reel script, voiceover, and video edit
        automated_minutes = (record.total_ai_duration_ms / 60000.0) + ((record.manual_edit_seconds + record.manual_review_seconds) / 60.0)
        time_saved_hours = max(0.5, round((270 - automated_minutes) / 60.0, 1))
        record.estimated_time_saved_hours = time_saved_hours

        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def update_manual_time(
        db: Session,
        project_id: str,
        manual_edit_sec: Optional[int] = None,
        manual_review_sec: Optional[int] = None
    ) -> EffortRecord:
        record = EffortTrackingService.get_or_create_effort_record(db, project_id)
        if manual_edit_sec is not None:
            record.manual_edit_seconds = manual_edit_sec
        if manual_review_sec is not None:
            record.manual_review_seconds = manual_review_sec
            
        automated_minutes = (record.total_ai_duration_ms / 60000.0) + ((record.manual_edit_seconds + record.manual_review_seconds) / 60.0)
        time_saved_hours = max(0.5, round((270 - automated_minutes) / 60.0, 1))
        record.estimated_time_saved_hours = time_saved_hours

        db.commit()
        db.refresh(record)
        return record

effort_tracking_service = EffortTrackingService()
