from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Health
class HealthResponse(BaseModel):
    status: str
    version: str
    ai_provider: str
    tts_engine: str
    ffmpeg_available: bool
    database_connected: bool

# Settings
class SettingsResponse(BaseModel):
    ai_provider: str
    gemini_key_configured: bool
    openai_key_configured: bool
    tts_engine: str
    tts_voice: str
    storage_dir: str

class SettingsUpdateRequest(BaseModel):
    ai_provider: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    tts_engine: Optional[str] = None
    tts_voice: Optional[str] = None

# Projects
class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    campaign_topic: Optional[str] = Field(None, max_length=255)
    source_type: str = Field("pdf", pattern="^(pdf|url)$")
    source_url: Optional[str] = None

class PaperMetadata(BaseModel):
    title: Optional[str] = None
    authors: Optional[List[str]] = []
    year: Optional[int] = None
    doi: Optional[str] = None
    journal: Optional[str] = None
    abstract: Optional[str] = None
    study_type: Optional[str] = None
    key_findings: Optional[List[str]] = []
    limitations: Optional[List[str]] = []
    page_count: Optional[int] = 0

class EffortRecordSchema(BaseModel):
    ingest_duration_ms: int = 0
    ai_extraction_duration_ms: int = 0
    ai_content_duration_ms: int = 0
    media_rendering_duration_ms: int = 0
    total_ai_duration_ms: int = 0
    manual_edit_seconds: int = 0
    manual_review_seconds: int = 0
    estimated_traditional_hours: float = 4.5
    estimated_time_saved_hours: float = 4.0

    class Config:
        from_attributes = True

class EffortUpdateRequest(BaseModel):
    manual_edit_seconds: Optional[int] = None
    manual_review_seconds: Optional[int] = None

# Claims
class ClaimBase(BaseModel):
    claim_id: str
    claim_text: str
    evidence_quote: str
    source_document: Optional[str] = None
    page_number: Optional[int] = None
    section: Optional[str] = None
    evidence_type: str = "Unknown"
    population: Optional[str] = None
    sample_size: Optional[str] = None
    limitations: List[str] = []
    uncertainty_notes: List[str] = []
    confidence_estimate: Optional[float] = None
    verification_status: str = "pending"
    support_level: str = "strong"
    support_notes: Optional[str] = None

class ClaimResponse(ClaimBase):
    id: str
    project_id: str
    original_claim_text: Optional[str] = None
    reviewer_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ClaimUpdateRequest(BaseModel):
    claim_text: str
    reviewer_notes: Optional[str] = None

class ClaimReviewRequest(BaseModel):
    action: str = Field(..., pattern="^(approve|reject|flag|edit)$")
    notes: Optional[str] = None
    reviewer_role: Optional[str] = "Medical Reviewer"
    edited_claim_text: Optional[str] = None

# Content Drafts
class CarouselSlide(BaseModel):
    slide_number: int
    eyebrow: Optional[str] = None
    headline: str
    body_text: str
    key_stat: Optional[str] = None
    stat_label: Optional[str] = None
    practical_tip: Optional[str] = None
    source_citation: Optional[str] = None
    claim_ids: List[str] = []

class StaticPostData(BaseModel):
    eyebrow: Optional[str] = "METABOLIC SCIENCE INSIGHT"
    headline: str
    body_copy: str
    practical_takeaway: str
    badge: Optional[str] = "Doctor-Led Metabolic Health"
    source_citation: Optional[str] = None
    claim_ids: List[str] = []

class ReelScene(BaseModel):
    scene_number: int
    duration_seconds: float = 5.0
    visual_cue: str
    on_screen_text: str
    narration: str
    subtitle_text: str
    visual_style: Optional[str] = "talking_characters"
    visual_theme: Optional[str] = "warm_editorial"
    animation_action: Optional[str] = "talking_character"
    character_name: Optional[str] = None
    claim_ids: List[str] = []

class ReelScript(BaseModel):
    reel_title: str
    hook: str
    target_duration_seconds: int = 30
    mode: str = "everyday"
    visual_style: str = "talking_characters"
    visual_theme: str = "warm_editorial"
    language: str = "en"
    voice_name: Optional[str] = "en-IN-NeerjaNeural"
    scenes: List[ReelScene]
    practical_takeaway: str
    caption: str
    hashtags: List[str]
    claim_ids: List[str] = []
    source_citation: Optional[str] = None

class ReelGenerateRequest(BaseModel):
    mode: str = "everyday"
    visual_style: str = "talking_characters"
    visual_theme: Optional[str] = "warm_editorial"
    language: str = "en"
    voice_name: Optional[str] = None

class ReelSceneUpdateRequest(BaseModel):
    narration: Optional[str] = None
    subtitle_text: Optional[str] = None
    on_screen_text: Optional[str] = None
    visual_cue: Optional[str] = None
    visual_style: Optional[str] = None
    visual_theme: Optional[str] = None
    animation_action: Optional[str] = None
    duration_seconds: Optional[float] = None


class ContentDraftResponse(BaseModel):
    id: str
    project_id: str
    content_type: str
    audience: Optional[str] = None
    main_message: Optional[str] = None
    hook: Optional[str] = None
    body_copy: Optional[str] = None
    practical_takeaway: Optional[str] = None
    caption: Optional[str] = None
    hashtags: List[str] = []
    reasoning: Dict[str, Any] = {}
    claim_ids: List[str] = []
    slide_data: Optional[List[Dict[str, Any]]] = None
    static_data: Optional[Dict[str, Any]] = None
    reel_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Artifacts
class ArtifactResponse(BaseModel):
    id: str
    project_id: str
    artifact_type: str
    filename: str
    file_path: str
    mime_type: str
    file_size_bytes: int
    metadata_json: Dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True

# Review Action
class ReviewActionResponse(BaseModel):
    id: str
    project_id: str
    claim_id: str
    action: str
    previous_status: Optional[str] = None
    new_status: str
    reviewer_role: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Project Detailed Response
class ProjectResponse(BaseModel):
    id: str
    title: str
    campaign_topic: Optional[str] = None
    source_type: str
    source_filename: Optional[str] = None
    source_url: Optional[str] = None
    status: str
    current_stage: int
    stage_message: str
    error_message: Optional[str] = None
    paper_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    claims: List[ClaimResponse] = []
    content_drafts: List[ContentDraftResponse] = []
    artifacts: List[ArtifactResponse] = []
    effort_record: Optional[EffortRecordSchema] = None

    class Config:
        from_attributes = True

class DashboardMetrics(BaseModel):
    total_projects: int
    total_claims: int
    approved_claims: int
    pending_claims: int
    flagged_claims: int
    rejected_claims: int
    total_artifacts: int
    total_hours_saved: float
    recent_projects: List[ProjectResponse] = []
