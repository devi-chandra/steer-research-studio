import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_full_pipeline_end_to_end():
    # 1. Create Project
    create_resp = client.post("/api/projects", json={
        "title": "Postprandial Walking & Glycemic Spikes Study",
        "campaign_topic": "Shatapadi & Glucose Management",
        "source_type": "pdf"
    })
    assert create_resp.status_code == 200
    proj_data = create_resp.json()
    proj_id = proj_data["id"]
    assert proj_id is not None

    # 2. Upload Sample PDF
    sample_pdf = settings.sample_papers_dir / "sample_postprandial_walk_study.pdf"
    assert sample_pdf.exists()
    
    with open(sample_pdf, "rb") as f:
        upload_resp = client.post(
            f"/api/projects/{proj_id}/upload",
            files={"file": ("sample_postprandial_walk_study.pdf", f, "application/pdf")}
        )
    assert upload_resp.status_code == 200

    # 3. Process Pipeline
    proc_resp = client.post(f"/api/projects/{proj_id}/process")
    assert proc_resp.status_code == 200
    proc_json = proc_resp.json()
    assert proc_json["status"] == "success"
    assert proc_json["claims_count"] >= 3

    # 4. Verify Claims Extracted
    claims_resp = client.get(f"/api/projects/{proj_id}/claims")
    assert claims_resp.status_code == 200
    claims = claims_resp.json()
    assert len(claims) >= 3
    
    first_claim = claims[0]
    assert first_claim["claim_id"] == "CLM-001"
    assert first_claim["verification_status"] == "pending"
    assert first_claim["confidence_estimate"] is not None

    # 5. Medical Review Gate: Approve First Claim
    rev_resp = client.post(
        f"/api/projects/{proj_id}/claims/{first_claim['claim_id']}/review",
        json={
            "action": "approve",
            "notes": "Verified against trial methodology and Table 1 results.",
            "reviewer_role": "Senior Clinical Reviewer"
        }
    )
    assert rev_resp.status_code == 200
    assert rev_resp.json()["verification_status"] == "approved"

    # Medical Review Gate: Edit Second Claim
    second_claim = claims[1]
    edit_resp = client.post(
        f"/api/projects/{proj_id}/claims/{second_claim['claim_id']}/review",
        json={
            "action": "edit",
            "edited_claim_text": "Leg muscle contractions facilitate GLUT4 glucose absorption without stressing the pancreas.",
            "notes": "Simplified medical terminology for everyday Indian audience.",
            "reviewer_role": "Medical Reviewer"
        }
    )
    assert edit_resp.status_code == 200
    assert edit_resp.json()["verification_status"] == "edited"
    assert edit_resp.json()["original_claim_text"] is not None

    # 6. Generate Carousel
    car_resp = client.post(f"/api/projects/{proj_id}/generate-carousel")
    assert car_resp.status_code == 200
    assert car_resp.json()["slide_count"] >= 5

    # 7. Generate Static Post
    stat_resp = client.post(f"/api/projects/{proj_id}/generate-static")
    assert stat_resp.status_code == 200
    assert stat_resp.json()["file_size_bytes"] > 50000

    # 8. Generate Reel Video MP4
    reel_resp = client.post(f"/api/projects/{proj_id}/generate-reel")
    assert reel_resp.status_code == 200
    assert reel_resp.json()["video_file"] == "final_reel.mp4"
    assert reel_resp.json()["file_size_bytes"] > 10000

    # 9. Verify Artifacts Registered
    art_resp = client.get(f"/api/projects/{proj_id}/artifacts")
    assert art_resp.status_code == 200
    artifacts = art_resp.json()
    art_types = [a["artifact_type"] for a in artifacts]
    assert "carousel_slide" in art_types
    assert "carousel_zip" in art_types
    assert "static_post" in art_types
    assert "reel_video" in art_types

    # 10. Build All Exports
    export_resp = client.post(f"/api/projects/{proj_id}/export/build-all")
    assert export_resp.status_code == 200
    assert export_resp.json()["exported_count"] >= 3

    # Check export files on disk
    export_dir = settings.generated_dir / proj_id / "exports"
    assert (export_dir / "captions_and_hashtags.txt").exists()
    assert (export_dir / "claims_evidence_ledger.json").exists()
    assert (export_dir / "claims_evidence_ledger.csv").exists()
    assert (export_dir / "project_audit_summary.json").exists()

    # 11. Effort Tracking Check
    effort_update = client.post(f"/api/projects/{proj_id}/effort", json={
        "manual_edit_seconds": 120,
        "manual_review_seconds": 180
    })
    assert effort_update.status_code == 200
    assert effort_update.json()["manual_edit_seconds"] == 120
    assert effort_update.json()["estimated_time_saved_hours"] > 3.0
