from pydantic import BaseModel
from typing import Optional, List, Any

class ReviewSubmitRequest(BaseModel):
    project_id: str
    target_type: str  # 'claim', 'asset', 'scene', 'slide'
    target_id: str
    decision: str     # 'Approve', 'Edit', 'Request Changes', 'Reject'
    reason_category: str = "Other"
    original_content: Optional[str] = ""
    revised_content: Optional[str] = ""
    comments: Optional[str] = ""
    reviewer_name: Optional[str] = "Dr. Medical Reviewer (Demo Lead)"

class ReviewResponse(BaseModel):
    id: str
    project_id: str
    target_type: str
    target_id: str
    decision: str
    reason_category: str
    original_content: str
    revised_content: str
    comments: str
    reviewer_name: str
    created_at: str

class ReviewRuleResponse(BaseModel):
    id: str
    rule_type: str
    pattern_or_keyword: str
    description: str
    trigger_count: int
    is_active: bool
    created_at: str
