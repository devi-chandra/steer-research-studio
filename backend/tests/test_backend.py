import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.core.config import settings
from app.core.database import SessionLocal, engine, Base
from app.services.pdf_extraction import PDFExtractionService
from app.services.evidence_tracking import EvidenceTrackingService
from app.services.carousel_renderer import carousel_renderer
from app.services.static_post_renderer import static_post_renderer
from app.services.video_generation import video_generation_service
from app.services.media_assembly import media_assembly_service

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert data["ffmpeg_available"] is True

def test_dashboard_metrics():
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "total_projects" in data
    assert "total_claims" in data
    assert "total_hours_saved" in data

def test_pdf_extraction_with_sample_paper():
    sample_pdf = settings.sample_papers_dir / "sample_postprandial_walk_study.pdf"
    assert sample_pdf.exists(), "Sample paper PDF must exist"
    
    extracted = PDFExtractionService.extract_pdf(sample_pdf)
    assert extracted["page_count"] == 5
    assert len(extracted["pages"]) == 5
    assert "Postprandial Glycemic Excursions" in extracted["full_text"]
    assert "GLUT4" in extracted["full_text"]
    assert "34%" in extracted["full_text"]

def test_evidence_verification_exact_and_fuzzy():
    sample_pdf = settings.sample_papers_dir / "sample_postprandial_walk_study.pdf"
    extracted = PDFExtractionService.extract_pdf(sample_pdf)
    
    # 1. Exact quote verification
    exact_claim = {
        "claim_text": "A 10-minute walk reduces post-meal glucose spike by 34%.",
        "evidence_quote": "A 10-minute post-meal walk initiated within 30 minutes of ingestion produced a 34% reduction in peak glucose elevation compared with sedentary rest",
        "page_number": 3
    }
    res_exact = EvidenceTrackingService.verify_claim_evidence(exact_claim, extracted["full_text"], extracted["pages"])
    assert res_exact["support_level"] == "strong"
    assert res_exact["verification_status"] == "pending"

    # 2. Weakly supported or fabricated quote check
    unsupported_claim = {
        "claim_text": "Walking completely cures type 2 diabetes overnight.",
        "evidence_quote": "Walking immediately cures type 2 diabetes overnight with zero dietary changes.",
        "page_number": 1
    }
    res_unsupp = EvidenceTrackingService.verify_claim_evidence(unsupported_claim, extracted["full_text"], extracted["pages"])
    assert res_unsupp["support_level"] in ["weak", "unsupported"]
    assert res_unsupp["verification_status"] == "flagged"

    # 3. Completely absent quote
    absent_claim = {
        "claim_text": "Quantum teleportation across entangled photons.",
        "evidence_quote": "Quantum teleportation across entangled photons in cryogenic vacuum.",
        "page_number": 1
    }
    res_absent = EvidenceTrackingService.verify_claim_evidence(absent_claim, extracted["full_text"], extracted["pages"])
    assert res_absent["support_level"] == "unsupported"
    assert res_absent["verification_status"] == "flagged"

def test_carousel_rendering(tmp_path):
    test_slides = [
        {
            "slide_number": 1,
            "eyebrow": "METABOLIC SCIENCE",
            "headline": "The 10-Minute Walk Outsmarts Dinner Spikes",
            "body_text": "Testing continuous glucose monitoring in South Asian adults.",
            "key_stat": "34%",
            "stat_label": "Reduction in peak glucose",
            "practical_tip": "Walk within 30 minutes of eating.",
            "source_citation": "ICMR Collaborative Study",
            "claim_ids": ["CLM-001"]
        },
        {
            "slide_number": 2,
            "eyebrow": "CLINICAL DISCOVERY",
            "headline": "Muscles Drink Glucose Directly",
            "body_text": "Contraction activates GLUT4 receptors without pancreatic strain.",
            "key_stat": "GLUT4",
            "stat_label": "Insulin-independent uptake",
            "practical_tip": "Gentle pacing suffices.",
            "source_citation": "Metabolic Research Review",
            "claim_ids": ["CLM-002"]
        }
    ]
    
    result = carousel_renderer.render_carousel_deck(test_slides, tmp_path)
    assert result["slide_count"] == 2
    assert Path(result["zip_file"]).exists()
    
    # Verify slide 1 is a valid 1080x1350 image
    slide_1 = Path(result["slide_files"][0])
    assert slide_1.exists()
    with Image.open(slide_1) as im:
        assert im.size == (1080, 1350)

def test_static_post_rendering(tmp_path):
    post_data = {
        "eyebrow": "DOCTOR-LED METABOLIC INSIGHT",
        "headline": "10 Minutes of Walking Beats 45 Minutes of Cardio If Your Timing Is Right.",
        "body_copy": "A clinical study revealed a 10-minute walk within 30 minutes blunts glycemic spikes by 34%.",
        "practical_takeaway": "The Steer Rule: Walk 100 paces immediately after dinner.",
        "badge": "Steer Clinical Standard",
        "source_citation": "Crossover Trial (n=48)",
        "claim_ids": ["CLM-001"]
    }
    out_file = tmp_path / "static_post.png"
    static_post_renderer.render_static_post(post_data, out_file)
    assert out_file.exists()
    with Image.open(out_file) as im:
        assert im.size == (1080, 1350)

@pytest.mark.asyncio
async def test_reel_mp4_generation(tmp_path):
    # Test scene frame rendering
    scene = {
        "scene_number": 1,
        "duration_seconds": 3.0,
        "visual_cue": "Indian dinner plate with glucose trajectory curve overlay",
        "on_screen_text": "What happens after dinner?",
        "narration": "What happens inside your body right after dinner?",
        "subtitle_text": "What happens inside your body right after dinner?",
        "claim_ids": ["CLM-001"]
    }
    frame_path = tmp_path / "scene_01.png"
    video_generation_service.render_scene_frame(scene, 1, frame_path)
    assert frame_path.exists()
    with Image.open(frame_path) as im:
        assert im.size == (1080, 1920)

    # Test audio generation
    audio_path = tmp_path / "voiceover.mp3"
    await video_generation_service.generate_voiceover_audio(scene["narration"], audio_path)
    assert audio_path.exists()
    assert audio_path.stat().st_size > 500

    # Test FFmpeg assembly
    output_mp4 = tmp_path / "test_reel.mp4"
    res = media_assembly_service.assemble_reel_mp4(
        scene_frames=[frame_path],
        scene_durations=[3.0],
        audio_path=audio_path,
        output_mp4_path=output_mp4
    )
    assert res["status"] == "success"
    assert output_mp4.exists()
    assert output_mp4.stat().st_size > 10000
    assert res["width"] == 1080
    assert res["height"] == 1920
