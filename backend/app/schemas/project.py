from pydantic import BaseModel, Field
from typing import Optional, List, Any

class IngestUrlRequest(BaseModel):
    url: str = Field(..., description="Public scientific article or paper URL")

class ProjectResponse(BaseModel):
    id: str
    title: str
    authors: str
    publication: str
    year: str
    doi: str
    source_type: str
    source_url: str
    extraction_status: str
    metadata_verified: bool
    limitation_notes: str
    created_at: str
    updated_at: str
    claims_count: int = 0
    assets_count: int = 0
    pending_reviews_count: int = 0

class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
