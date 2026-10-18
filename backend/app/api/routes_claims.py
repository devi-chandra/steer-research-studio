from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.models import Claim, Project
from app.schemas.schemas import ClaimResponse, ClaimUpdateRequest, ClaimReviewRequest
from app.services.review_service import review_service

router = APIRouter(prefix="/api/projects/{project_id}/claims", tags=["claims"])

@router.get("", response_model=List[ClaimResponse])
def get_project_claims(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    claims = db.query(Claim).filter(Claim.project_id == project_id).order_by(Claim.claim_id).all()
    return claims

@router.patch("/{claim_id}", response_model=ClaimResponse)
def update_claim(
    project_id: str,
    claim_id: str,
    payload: ClaimUpdateRequest,
    db: Session = Depends(get_db)
):
    claim = db.query(Claim).filter(Claim.project_id == project_id, Claim.claim_id == claim_id).first()
    if not claim:
        claim = db.query(Claim).filter(Claim.project_id == project_id, Claim.id == claim_id).first()
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")

    if not claim.original_claim_text:
        claim.original_claim_text = claim.claim_text

    claim.claim_text = payload.claim_text.strip()
    if payload.reviewer_notes:
        claim.reviewer_notes = payload.reviewer_notes.strip()
    claim.verification_status = "edited"

    db.commit()
    db.refresh(claim)
    return claim

@router.post("/{claim_id}/review", response_model=ClaimResponse)
def review_claim(
    project_id: str,
    claim_id: str,
    payload: ClaimReviewRequest,
    db: Session = Depends(get_db)
):
    try:
        updated_claim = review_service.process_claim_review(
            db=db,
            project_id=project_id,
            claim_id=claim_id,
            action=payload.action,
            notes=payload.notes,
            reviewer_role=payload.reviewer_role or "Medical Reviewer",
            edited_claim_text=payload.edited_claim_text
        )
        return updated_claim
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cross-format-checks")
def get_cross_format_checks(project_id: str, db: Session = Depends(get_db)):
    from app.models.models import ContentDraft
    from app.services.cross_format_claims import cross_format_claims_service

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    draft = db.query(ContentDraft).filter(ContentDraft.project_id == project_id).first()
    claims = db.query(Claim).filter(Claim.project_id == project_id).order_by(Claim.claim_id).all()

    report = cross_format_claims_service.audit_project_consistency(project=project, draft=draft, claims=claims)
    from app.services.overclaim_check import overclaim_check_service
    overclaim = overclaim_check_service.audit(draft, claims, project.paper_metadata or {}) if draft else None
    if overclaim:
        report["checks"].extend(overclaim["checks"])
        report["summary"] = {
            "total_checks": len(report["checks"]),
            "passed_checks": sum(1 for c in report["checks"] if c["status"] == "passed"),
            "flagged_checks": sum(1 for c in report["checks"] if c["status"] == "flagged"),
        }
        report["overall_status"] = "review_required" if report["summary"]["flagged_checks"] else "passed"
        report["overclaim_disclaimer"] = overclaim["disclaimer"]
    return report
