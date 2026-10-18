import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    campaign_topic = Column(String(255), nullable=True)
    source_type = Column(String(20), default="pdf")  # "pdf" or "url"
    source_filename = Column(String(255), nullable=True)
    source_url = Column(String(1024), nullable=True)
    
    # Pipeline status
    status = Column(String(50), default="created")  # created, ingesting, extracted, translating, content_ready, completed, error
    current_stage = Column(Integer, default=1)  # 1 to 7
    stage_message = Column(String(500), default="Project created")
    error_message = Column(Text, nullable=True)

    paper_metadata = Column(JSON, nullable=True)  # title, authors, year, doi, journal, abstract, study_type, key_findings, limitations, page_count
    extracted_text_pages = Column(JSON, nullable=True)  # list of {page_num, text, sections}
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    claims = relationship("Claim", back_populates="project", cascade="all, delete-orphan", order_by="Claim.claim_id")
    content_drafts = relationship("ContentDraft", back_populates="project", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="project", cascade="all, delete-orphan")
    review_actions = relationship("ReviewAction", back_populates="project", cascade="all, delete-orphan")
    effort_record = relationship("EffortRecord", uselist=False, back_populates="project", cascade="all, delete-orphan")


class Claim(Base):
    __tablename__ = "claims"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    claim_id = Column(String(20), nullable=False)  # e.g., "CLM-001"
    
    claim_text = Column(Text, nullable=False)
    original_claim_text = Column(Text, nullable=True)
    evidence_quote = Column(Text, nullable=False)
    source_document = Column(String(255), nullable=True)
    page_number = Column(Integer, nullable=True)
    section = Column(String(100), nullable=True)
    evidence_type = Column(String(100), default="Unknown")
    population = Column(String(200), nullable=True)
    sample_size = Column(String(100), nullable=True)
    
    limitations = Column(JSON, default=list)
    uncertainty_notes = Column(JSON, default=list)
    confidence_estimate = Column(Float, nullable=True)  # Explicitly labelled estimate 0.0 - 1.0
    
    # Review & Verification
    verification_status = Column(String(30), default="pending")  # pending, approved, flagged, rejected, edited
    support_level = Column(String(30), default="strong")  # strong, moderate, weak, unsupported
    support_notes = Column(Text, nullable=True)
    
    reviewer_notes = Column(Text, nullable=True)
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="claims")


class ContentDraft(Base):
    __tablename__ = "content_drafts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    content_type = Column(String(30), nullable=False)  # carousel, static, reel, captions
    
    audience = Column(String(255), nullable=True)
    main_message = Column(Text, nullable=True)
    hook = Column(Text, nullable=True)
    body_copy = Column(Text, nullable=True)
    practical_takeaway = Column(Text, nullable=True)
    
    caption = Column(Text, nullable=True)
    hashtags = Column(JSON, default=list)
    reasoning = Column(JSON, default=dict)
    claim_ids = Column(JSON, default=list)  # list of CLM-xxx
    
    # Specific format data
    slide_data = Column(JSON, nullable=True)  # For carousel: list of {slide_num, title, subtitle, body, takeaway, quote, citation}
    static_data = Column(JSON, nullable=True)  # For static post: {headline, subhead, body, takeaway, badge, citation}
    reel_data = Column(JSON, nullable=True)  # For reel: {scenes: [{scene_num, visual_cue, narration, on_screen_text, duration_sec, claim_ids}]}
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="content_drafts")


class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    artifact_type = Column(String(50), nullable=False)  # carousel_slide, carousel_zip, static_post, reel_video, reel_audio, captions_txt, claims_export_json, claims_export_csv, project_summary
    filename = Column(String(255), nullable=False)
    file_path = Column(String(1024), nullable=False)
    mime_type = Column(String(100), default="application/octet-stream")
    file_size_bytes = Column(Integer, default=0)
    metadata_json = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="artifacts")


class ReviewAction(Base):
    __tablename__ = "review_actions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    claim_id = Column(String(50), nullable=False)
    action = Column(String(30), nullable=False)  # approve, reject, flag, edit
    previous_status = Column(String(30), nullable=True)
    new_status = Column(String(30), nullable=False)
    reviewer_role = Column(String(100), default="Medical Reviewer")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="review_actions")


class EffortRecord(Base):
    __tablename__ = "effort_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    
    ingest_duration_ms = Column(Integer, default=0)
    ai_extraction_duration_ms = Column(Integer, default=0)
    ai_content_duration_ms = Column(Integer, default=0)
    media_rendering_duration_ms = Column(Integer, default=0)
    total_ai_duration_ms = Column(Integer, default=0)
    
    manual_edit_seconds = Column(Integer, default=0)
    manual_review_seconds = Column(Integer, default=0)
    
    estimated_traditional_hours = Column(Float, default=4.5)
    estimated_time_saved_hours = Column(Float, default=4.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="effort_record")
