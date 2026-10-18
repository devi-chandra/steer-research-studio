from pydantic import BaseModel
from typing import Optional, List

class ClaimResponse(BaseModel):
    id: str
    project_id: str
    claim_id: str
    claim_text: str
    exact_quote: str
    page_number: int
    section_heading: str
    study_type: str
    population: str
    sample_size: str
    outcome_measured: str
    numerical_result: str
    units: str
    study_conditions: str
    limitations: str
    uncertainty: str
    evidence_status: str
    review_status: str
    review_notes: str
    reviewer_name: str
    created_at: str
    updated_at: str

class ClaimUpdateRequest(BaseModel):
    claim_text: Optional[str] = None
    numerical_result: Optional[str] = None
    limitations: Optional[str] = None
    evidence_status: Optional[str] = None
    review_status: Optional[str] = None
    review_notes: Optional[str] = None
