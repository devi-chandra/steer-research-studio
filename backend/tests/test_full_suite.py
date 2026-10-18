import os
import json
import pytest
from pathlib import Path
import pptx
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.database import init_db, get_db_connection
from app.core.security import is_safe_url
from app.services.ingestion.pdf_extractor import extract_pdf_document
from app.services.extraction.claim_extractor import extract_and_store_claims
from app.services.verification.evidence_verifier import verify_project_evidence
from app.services.content_generation.carousel_generator import generate_instagram_carousel
from app.services.content_generation.post_generator import generate_static_instagram_post
from app.services.reel_generation.two_stories_generator import generate_two_stories
from app.services.reel_generation.inside_body_generator import generate_inside_body_storyboard
from app.services.localization.local_voice_service import generate_localvoice_script
from app.services.powerpoint.pptx_generator import generate_powerpoint_presentation
from app.services.review.feedback_service import submit_doctor_review, get_project_reviews, get_active_review_rules
from app.services.verification.consistency_service import run_cross_format_consistency_checks
from app.services.export.export_service import generate_export_package

TEST_PROJECT_ID = "test-proj-001"

def test_sample_pdf_endpoint_returns_a_real_pdf():
    response = TestClient(app).get("/api/settings/sample-pdf")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    assert response.content.startswith(b"%PDF-")

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    init_db()
    test_pdf = settings.BASE_DIR / "sample_papers" / "stamatakis_vilpa_nature_med_2022.pdf"
    assert test_pdf.exists(), f"Sample test paper must exist at {test_pdf}"

    conn = get_db_connection()
    conn.execute("INSERT OR REPLACE INTO projects (id, title, doi, year, source_type, source_path) VALUES (?, ?, ?, ?, 'pdf', ?)",
                 (TEST_PROJECT_ID, "VILPA Nature Medicine 2022 Trial", "10.1038/s41591-022-02100-x", "2022", str(test_pdf)))
    conn.commit()
    conn.close()

def test_ssrf_security_rules():
    # Loopback and private addresses must be blocked
    unsafe_urls = [
        "http://127.0.0.1:8000/admin",
        "http://localhost:3000",
        "http://169.254.169.254/latest/meta-data/",
        "ftp://example.com/file.pdf",
        "file:///etc/passwd"
    ]
    for url in unsafe_urls:
        safe, reason = is_safe_url(url)
        assert safe is False, f"URL {url} should have been blocked for SSRF!"

def test_pdf_ingestion_and_claim_extraction():
    test_pdf = settings.BASE_DIR / "sample_papers" / "stamatakis_vilpa_nature_med_2022.pdf"

    # 1. Test Ingestion
    ingest_res = extract_pdf_document(test_pdf, TEST_PROJECT_ID)
    assert ingest_res["total_pages"] == 3
    assert ingest_res["total_characters"] > 1000
    assert ingest_res["is_scanned"] is False
    assert "10.1038" in ingest_res["detected_doi"]

    # 2. Test Claim Extraction
    extract_res = extract_and_store_claims(TEST_PROJECT_ID)
    assert extract_res["total_claims"] >= 3
    claims = extract_res["claims"]
    assert any("CLM-" in c["claim_id"] for c in claims)

    # Refreshing evidence must invalidate already-generated project content.
    conn = get_db_connection()
    conn.execute("""
    INSERT INTO reel_scenes (
        id, project_id, reel_mode, scene_index, title, visual_description,
        narration_text, render_status
    ) VALUES ('stale-scene-test', ?, 'everyday', 1, 'Stale', 'Old evidence', 'Old narration', 'ready')
    """, (TEST_PROJECT_ID,))
    conn.execute("""
    INSERT INTO assets (
        id, project_id, asset_type, title, status
    ) VALUES ('stale-pptx-test', ?, 'pptx', 'Stale deck', 'rendered')
    """, (TEST_PROJECT_ID,))
    conn.commit()
    conn.close()

    extract_and_store_claims(TEST_PROJECT_ID)
    conn = get_db_connection()
    stale_scenes = conn.execute(
        "SELECT COUNT(*) FROM reel_scenes WHERE project_id = ?", (TEST_PROJECT_ID,)
    ).fetchone()[0]
    stale_assets = conn.execute(
        "SELECT COUNT(*) FROM assets WHERE project_id = ?", (TEST_PROJECT_ID,)
    ).fetchone()[0]
    conn.close()
    assert stale_scenes == 0
    assert stale_assets == 0

    # 3. Test Evidence Verification
    verify_res = verify_project_evidence(TEST_PROJECT_ID)
    assert verify_res["total_claims_checked"] >= 3
    assert verify_res["directly_supported"] + verify_res["partially_supported"] >= 2

def test_carousel_and_post_generation():
    # Carousel
    car_res = generate_instagram_carousel(TEST_PROJECT_ID, slide_count=6)
    assert car_res["slide_count"] == 6
    zip_path = settings.BASE_DIR / car_res["zip_url"].lstrip("/")
    assert zip_path.exists()
    assert zip_path.stat().st_size > 5000

    # Static Post
    post_res = generate_static_instagram_post(TEST_PROJECT_ID)
    post_path = Path(post_res["file_path"])
    assert post_path.exists()
    assert post_path.stat().st_size > 5000

def test_two_stories_and_inside_body():
    # Feature 1: Two Stories
    stories = generate_two_stories(TEST_PROJECT_ID)
    assert len(stories["professional"]["scenes"]) >= 3
    assert len(stories["everyday"]["scenes"]) >= 3
    assert len(stories["shared_evidence_comparison"]) >= 3

    # Feature 2: Inside Your Body
    body_res = generate_inside_body_storyboard(TEST_PROJECT_ID)
    assert len(body_res["scenes"]) >= 3
    assert body_res["target_system"] != ""

def test_localvoice_script_adaptation():
    # Ensure everyday scenes exist first
    generate_two_stories(TEST_PROJECT_ID)

    # Feature 3: LocalVoice 6 language variants
    for lang in ["hi_en", "te_en", "ta_en", "kn_en", "ml_en"]:
        loc = generate_localvoice_script(TEST_PROJECT_ID, lang)
        assert loc["language_code"] == lang
        assert len(loc["scenes"]) >= 3
        # Check subtitles exist
        assert "subtitle_native" in loc["scenes"][0]

def test_powerpoint_generation_and_validation():
    # Feature 4: PowerPoint PPTX
    pptx_res = generate_powerpoint_presentation(TEST_PROJECT_ID)
    pptx_file = Path(pptx_res["file_path"])
    assert pptx_file.exists()
    assert pptx_res["slide_count"] == 10

    # Reopen with python-pptx to structurally validate
    prs = pptx.Presentation(str(pptx_file))
    assert len(prs.slides) == 10

def test_doctor_feedback_and_consistency():
    # Feature 5: Doctor Feedback Loop
    rev_res = submit_doctor_review(
        project_id=TEST_PROJECT_ID,
        target_type="claim",
        target_id="CLM-01",
        decision="Edit",
        reason_category="Missing limitation",
        original_content="Risk reduced by 48%",
        revised_content="Relative cardiovascular risk reduced by 48% in non-exercisers (observational cohort).",
        comments="Specified relative risk and observational nature."
    )
    assert rev_res["success"] is True

    # Review history
    reviews = get_project_reviews(TEST_PROJECT_ID)
    assert len(reviews) >= 1
    assert reviews[0]["decision"] == "Edit"

    # Review Rules
    rules = get_active_review_rules()
    assert len(rules) >= 1

    # Cross-Format Claim Safety
    checks = run_cross_format_consistency_checks(TEST_PROJECT_ID)
    assert "total_checks_run" in checks

def test_export_package():
    exp = generate_export_package(TEST_PROJECT_ID)
    assert exp["deliverables_count"] >= 1
    master_zip = settings.BASE_DIR / exp["master_zip_url"].lstrip("/")
    assert master_zip.exists()
    assert master_zip.stat().st_size > 1000
