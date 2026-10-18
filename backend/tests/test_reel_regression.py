import pytest
import json
import sqlite3
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.database import get_db_connection
from app.services.localization.tts_adapter import tts_adapter
from app.services.reel_generation.video_renderer import is_ffmpeg_available

client = TestClient(app)

PROJECT_ID = "test-proj-001"

@pytest.fixture(autouse=True)
def ensure_test_project_and_claims():
    """Ensures test-proj-001 exists with verified claims."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM projects WHERE id = ?", (PROJECT_ID,))
    if not c.fetchone():
        c.execute("""
        INSERT INTO projects (id, title, doi, source_type, extraction_status, metadata_verified)
        VALUES (?, 'Association of wearable device-measured VILPA with mortality', '10.1038/s41591-022-02100-x', 'pdf', 'extracted', 1)
        """, (PROJECT_ID,))
    c.execute("SELECT count(*) FROM claims WHERE project_id = ?", (PROJECT_ID,))
    if c.fetchone()[0] == 0:
        c.execute("""
        INSERT INTO claims (id, project_id, claim_id, claim_text, exact_quote, page_number, numerical_result, sample_size, limitations, uncertainty, evidence_status, review_status)
        VALUES ('clm-test-01', ?, 'CLM-01', '3-4 bouts of VILPA reduced mortality by 40%', '3-4 bouts of 1-2 min VILPA per day', 1, '40% reduction in all-cause mortality', 'n=25,241 non-exercisers', 'Observational accelerometer cohort', 'HR=0.60 (95% CI 0.50-0.73)', 'Directly supported', 'Approved')
        """, (PROJECT_ID,))
    conn.commit()
    conn.close()

def test_project_reel_config_persists_and_validates():
    response = client.put(
        f"/api/projects/{PROJECT_ID}/reel-config",
        json={"style": "animated_explainer", "theme": "pastel_educational"},
    )
    assert response.status_code == 200
    assert client.get(f"/api/projects/{PROJECT_ID}/reel-config").json() == {
        "project_id": PROJECT_ID,
        "style": "animated_explainer",
        "theme": "pastel_educational",
    }
    invalid = client.put(
        f"/api/projects/{PROJECT_ID}/reel-config",
        json={"style": "unknown", "theme": "space"},
    )
    assert invalid.status_code == 422

# 1. Professional Mode storyboard -> MP4
def test_regression_1_professional_mode_mp4():
    assert is_ffmpeg_available(), "FFmpeg must be available"
    response = client.post(
        f"/api/projects/{PROJECT_ID}/render/video-reel",
        json={"reel_mode": "professional", "language_code": "en"}
    )
    assert response.status_code == 200, f"Render failed: {response.text}"
    data = response.json()
    assert data["success"] is True
    assert data["reel_mode"] == "professional"
    assert data["resolution"] == "1080x1920"
    assert data["total_duration_seconds"] > 0

    video_rel_path = data["video_url"].lstrip("/")
    video_abs_path = settings.BASE_DIR / video_rel_path
    assert video_abs_path.exists(), f"Video file must exist at {video_abs_path}"
    assert video_abs_path.stat().st_size > 10000, "Rendered MP4 must be non-empty"

# 2. Everyday Mode storyboard -> MP4
def test_regression_2_everyday_mode_mp4():
    assert is_ffmpeg_available(), "FFmpeg must be available"
    response = client.post(
        f"/api/projects/{PROJECT_ID}/render/video-reel",
        json={"reel_mode": "everyday", "language_code": "en"}
    )
    assert response.status_code == 200, f"Everyday render failed: {response.text}"
    data = response.json()
    assert data["success"] is True
    assert data["reel_mode"] == "everyday"
    assert data["resolution"] == "1080x1920"
    assert len(data["scenes"]) >= 1

    video_abs_path = settings.BASE_DIR / data["video_url"].lstrip("/")
    assert video_abs_path.exists()
    assert video_abs_path.stat().st_size > 10000

# 3. LocalVoice English -> MP4
def test_regression_3_localvoice_english_mp4():
    assert is_ffmpeg_available(), "FFmpeg must be available"
    response = client.post(
        f"/api/projects/{PROJECT_ID}/render/video-reel",
        json={"reel_mode": "localvoice", "language_code": "en"}
    )
    assert response.status_code == 200, f"LocalVoice English render failed: {response.text}"
    data = response.json()
    assert data["success"] is True
    assert data["language_code"] == "en"
    video_abs_path = settings.BASE_DIR / data["video_url"].lstrip("/")
    assert video_abs_path.exists()
    assert video_abs_path.stat().st_size > 10000

# 4. LocalVoice Telugu -> MP4
def test_regression_4_localvoice_telugu_mp4():
    assert is_ffmpeg_available(), "FFmpeg must be available"
    response = client.post(
        f"/api/projects/{PROJECT_ID}/render/video-reel",
        json={"reel_mode": "localvoice", "language_code": "te_en"}
    )
    assert response.status_code == 200, f"LocalVoice Telugu render failed: {response.text}"
    data = response.json()
    assert data["success"] is True
    assert data["language_code"] == "te_en"

    # Verify scene timeline
    assert len(data["scenes"]) >= 1
    for sc in data["scenes"]:
        assert sc["duration"] > 0
        assert sc["tts_provider"] in ("edge-tts", "gTTS")

    video_abs_path = settings.BASE_DIR / data["video_url"].lstrip("/")
    assert video_abs_path.exists()
    assert video_abs_path.stat().st_size > 10000

# 5. LocalVoice Hindi -> MP4
def test_regression_5_localvoice_hindi_mp4():
    assert is_ffmpeg_available(), "FFmpeg must be available"
    response = client.post(
        f"/api/projects/{PROJECT_ID}/render/video-reel",
        json={"reel_mode": "localvoice", "language_code": "hi_en"}
    )
    assert response.status_code == 200, f"LocalVoice Hindi render failed: {response.text}"
    data = response.json()
    assert data["success"] is True
    assert data["language_code"] == "hi_en"

    video_abs_path = settings.BASE_DIR / data["video_url"].lstrip("/")
    assert video_abs_path.exists()
    assert video_abs_path.stat().st_size > 10000

# 6. Missing storyboard -> automatic generation without failing
def test_regression_6_missing_storyboard_auto_generation():
    # Clear scenes for kannada
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM reel_scenes WHERE project_id = ? AND reel_mode = 'localvoice' AND language_code = 'kn_en'", (PROJECT_ID,))
    conn.commit()
    conn.close()

    # Request render without pre-generating storyboard
    response = client.post(
        f"/api/projects/{PROJECT_ID}/render/video-reel",
        json={"reel_mode": "localvoice", "language_code": "kn_en"}
    )
    assert response.status_code == 200, f"Auto-generation failed: {response.text}"
    data = response.json()
    assert data["success"] is True
    assert data["language_code"] == "kn_en"

    # Verify scenes now exist in database
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT count(*) FROM reel_scenes WHERE project_id = ? AND reel_mode = 'localvoice' AND language_code = 'kn_en'", (PROJECT_ID,))
    count = c.fetchone()[0]
    conn.close()
    assert count >= 1, "Scenes must have been persisted by auto-generation"

# 7. Unknown mode -> clear validation error
def test_regression_7_unknown_mode_validation_error():
    response = client.post(
        f"/api/projects/{PROJECT_ID}/render/video-reel",
        json={"reel_mode": "hollywood_blockbuster", "language_code": "en"}
    )
    assert response.status_code == 422
    assert "Invalid reel mode" in response.text

# 8. Invalid TTS voice -> explicit failure rather than false success
@pytest.mark.asyncio
async def test_regression_8_invalid_tts_voice_explicit_failure():
    out_file = settings.GENERATED_DIR / "audio" / "test_invalid.mp3"
    success, prov, details = await tts_adapter.generate_speech(
        "Invalid voice test text",
        "xx_unsupported_language",
        out_file,
        allow_mock=False
    )
    assert success is False, "Must not return success for invalid language"
    assert "Unsupported language" in details or prov == "none"

# 9. Repeated render request -> no duplicate or corrupted scenes
def test_regression_9_repeated_render_idempotency():
    # Render Tamil reel first time
    res1 = client.post(
        f"/api/projects/{PROJECT_ID}/render/video-reel",
        json={"reel_mode": "localvoice", "language_code": "ta_en"}
    )
    assert res1.status_code == 200

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT count(*) FROM reel_scenes WHERE project_id = ? AND reel_mode = 'localvoice' AND language_code = 'ta_en'", (PROJECT_ID,))
    count_first = c.fetchone()[0]
    conn.close()

    # Render Tamil reel second time
    res2 = client.post(
        f"/api/projects/{PROJECT_ID}/render/video-reel",
        json={"reel_mode": "localvoice", "language_code": "ta_en"}
    )
    assert res2.status_code == 200

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT count(*) FROM reel_scenes WHERE project_id = ? AND reel_mode = 'localvoice' AND language_code = 'ta_en'", (PROJECT_ID,))
    count_second = c.fetchone()[0]
    conn.close()

    assert count_first == count_second, f"Scene count changed from {count_first} to {count_second} upon re-render"

# 10. Scientific evidence remains consistent across modes
def test_regression_10_scientific_evidence_consistency():
    two_stories_res = client.get(f"/api/projects/{PROJECT_ID}/two-stories")
    assert two_stories_res.status_code == 200
    stories_data = two_stories_res.json()
    assert stories_data["exists"] is True

    prof_scenes = stories_data["professional"]["scenes"]
    evry_scenes = stories_data["everyday"]["scenes"]
    assert len(prof_scenes) == len(evry_scenes)

    # Verify claim IDs are shared
    for i in range(len(prof_scenes)):
        prof_claim = prof_scenes[i]["claim_ids"][0] if prof_scenes[i]["claim_ids"] else None
        evry_claim = evry_scenes[i]["claim_ids"][0] if evry_scenes[i]["claim_ids"] else None
        assert prof_claim is not None
        assert prof_claim == evry_claim, f"Scene {i+1} claims diverge: {prof_claim} vs {evry_claim}"

    # Verify localvoice scenes retain the same claim IDs
    loc_res = client.get(f"/api/projects/{PROJECT_ID}/localvoice?language_code=te_en")
    assert loc_res.status_code == 200
    loc_data = loc_res.json()
    if loc_data["exists"]:
        for i, sc in enumerate(loc_data["scenes"]):
            assert sc["claim_ids"][0] == prof_scenes[i]["claim_ids"][0]
