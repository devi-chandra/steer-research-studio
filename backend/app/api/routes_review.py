import json
from fastapi import APIRouter, HTTPException
from app.core.database import get_db_connection
from app.schemas.review import ReviewSubmitRequest
from app.services.review.feedback_service import submit_doctor_review, get_project_reviews, get_active_review_rules
from app.services.verification.consistency_service import run_cross_format_consistency_checks

router = APIRouter(prefix="", tags=["Review Gate & Consistency"])

@router.post("/api/reviews/submit")
def api_submit_review(req: ReviewSubmitRequest):
    try:
        res = submit_doctor_review(
            project_id=req.project_id,
            target_type=req.target_type,
            target_id=req.target_id,
            decision=req.decision,
            reason_category=req.reason_category,
            original_content=req.original_content or "",
            revised_content=req.revised_content or "",
            comments=req.comments or "",
            reviewer_name=req.reviewer_name or "Dr. Medical Reviewer (Demo Lead)"
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/projects/{project_id}/reviews")
def api_get_reviews(project_id: str):
    reviews = get_project_reviews(project_id)
    return {"project_id": project_id, "reviews": reviews}

@router.get("/api/reviews/rules")
def api_get_rules():
    rules = get_active_review_rules()
    return {"rules": rules}

@router.post("/api/projects/{project_id}/check-consistency")
def api_check_consistency(project_id: str):
    try:
        res = run_cross_format_consistency_checks(project_id)
        return {"success": True, "results": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/projects/{project_id}/consistency-checks")
def api_get_consistency_checks(project_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM consistency_checks WHERE project_id = ? ORDER BY created_at DESC", (project_id,))
    checks = [dict(r) for r in cursor.fetchall()]
    conn.close()

    for c in checks:
        c["affected_assets"] = json.loads(c.get("affected_assets_json", "[]"))

    critical = sum(1 for c in checks if c["severity"] == "critical" and not c["resolved"])
    return {
        "project_id": project_id,
        "total": len(checks),
        "critical_count": critical,
        "is_publication_ready": (critical == 0),
        "checks": checks
    }
