from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.models import Claim, ReviewAction, Project, ContentDraft

class MedicalReviewService:
    @staticmethod
    def process_claim_review(
        db: Session,
        project_id: str,
        claim_id: str,
        action: str,  # approve, reject, flag, edit
        notes: Optional[str] = None,
        reviewer_role: str = "Medical Reviewer",
        edited_claim_text: Optional[str] = None
    ) -> Claim:
        """
        Executes a human medical review action on a scientific claim.
        Maintains complete audit history and preserves original text if edited.
        Never automatically approves claims without explicit human action.
        """
        claim = db.query(Claim).filter(Claim.project_id == project_id, Claim.claim_id == claim_id).first()
        if not claim:
            # Fallback check by primary id
            claim = db.query(Claim).filter(Claim.project_id == project_id, Claim.id == claim_id).first()
            if not claim:
                raise ValueError(f"Claim with ID {claim_id} not found in project {project_id}.")

        prev_status = claim.verification_status

        if action == "approve":
            claim.verification_status = "approved"
        elif action == "reject":
            claim.verification_status = "rejected"
        elif action == "flag":
            claim.verification_status = "flagged"
        elif action == "edit":
            if not edited_claim_text or not edited_claim_text.strip():
                raise ValueError("Edited claim text cannot be empty.")
            if not claim.original_claim_text:
                claim.original_claim_text = claim.claim_text
            claim.claim_text = edited_claim_text.strip()
            claim.verification_status = "edited"  # Remains pending re-approval

        claim.reviewer_notes = notes
        claim.reviewed_by = reviewer_role
        claim.reviewed_at = datetime.utcnow()

        # Audit action record
        audit_record = ReviewAction(
            project_id=project_id,
            claim_id=claim.claim_id,
            action=action,
            previous_status=prev_status,
            new_status=claim.verification_status,
            reviewer_role=reviewer_role,
            notes=notes
        )
        db.add(audit_record)

        # Update project status if all claims are reviewed
        all_claims = db.query(Claim).filter(Claim.project_id == project_id).all()
        any_pending = any(c.verification_status in ["pending", "flagged"] for c in all_claims)
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            if not any_pending and all(c.verification_status in ["approved", "edited"] for c in all_claims):
                project.status = "approved"
                project.stage_message = "All extracted claims have been verified and approved by medical reviewer."
            else:
                project.status = "reviewing"
                project.stage_message = f"Medical review in progress ({sum(1 for c in all_claims if c.verification_status == 'approved')}/{len(all_claims)} approved)."

        db.commit()
        # Claim edits/flags invalidate the currently generated content approval.
        # The next export must be based on a newly reviewed content version.
        draft = db.query(ContentDraft).filter(ContentDraft.project_id == project_id).first()
        if draft and action in {"edit", "flag", "reject"}:
            draft.version = (draft.version or 0) + 1
            draft.review_status = "draft"
            draft.approved_version = None
            db.commit()
        db.refresh(claim)
        return claim

review_service = MedicalReviewService()
