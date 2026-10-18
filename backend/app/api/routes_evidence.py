from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.core.database import get_db_connection
from app.services.extraction.claim_extractor import extract_and_store_claims
from app.services.verification.evidence_verifier import verify_project_evidence
from app.schemas.claim import ClaimUpdateRequest

router = APIRouter(prefix="/api/projects", tags=["Evidence Ledger"])

@router.post("/{project_id}/extract-claims")
def trigger_claim_extraction(project_id: str):
    try:
        res = extract_and_store_claims(project_id)
        # Automatically run verification against source page text
        verify_res = verify_project_evidence(project_id)
        return {
            "success": True,
            "extraction": res,
            "verification": verify_res
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{project_id}/claims")
def get_project_claims(
    project_id: str,
    evidence_status: Optional[str] = Query(None),
    review_status: Optional[str] = Query(None)
):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM claims WHERE project_id = ?"
    params = [project_id]

    if evidence_status:
        query += " AND evidence_status = ?"
        params.append(evidence_status)

    if review_status:
        query += " AND review_status = ?"
        params.append(review_status)

    query += " ORDER BY page_number ASC, claim_id ASC"
    cursor.execute(query, params)
    claims = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return {"project_id": project_id, "total": len(claims), "claims": claims}

@router.post("/{project_id}/verify-evidence")
def run_evidence_verification(project_id: str):
    try:
        res = verify_project_evidence(project_id)
        return {"success": True, "verification": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/claims/{claim_id}")
def update_claim(claim_id: str, req: ClaimUpdateRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    updates = []
    params = []

    if req.claim_text is not None:
        updates.append("claim_text = ?")
        params.append(req.claim_text)
    if req.numerical_result is not None:
        updates.append("numerical_result = ?")
        params.append(req.numerical_result)
    if req.limitations is not None:
        updates.append("limitations = ?")
        params.append(req.limitations)
    if req.evidence_status is not None:
        updates.append("evidence_status = ?")
        params.append(req.evidence_status)
    if req.review_status is not None:
        updates.append("review_status = ?")
        params.append(req.review_status)
    if req.review_notes is not None:
        updates.append("review_notes = ?")
        params.append(req.review_notes)

    if not updates:
        conn.close()
        return {"message": "No updates specified."}

    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(claim_id)

    cursor.execute(f"UPDATE claims SET {', '.join(updates)} WHERE id = ? OR claim_id = ?", params + [claim_id])
    conn.commit()

    cursor.execute("SELECT * FROM claims WHERE id = ? OR claim_id = ?", (claim_id, claim_id))
    updated = cursor.fetchone()
    conn.close()

    if not updated:
        raise HTTPException(status_code=404, detail="Claim not found.")

    return {"success": True, "claim": dict(updated)}
