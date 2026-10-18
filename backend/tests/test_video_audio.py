import pytest
import asyncio
from pathlib import Path
from app.core.config import settings
from app.core.database import get_db_connection
from app.services.reel_generation.video_renderer import render_video_reel, is_ffmpeg_available
from app.services.localization.tts_adapter import tts_adapter

@pytest.mark.asyncio
async def test_tts_voice_generation_multilingual():
    languages = ["en", "hi_en", "te_en", "ta_en", "kn_en", "ml_en"]
    for lang in languages:
        res = await tts_adapter.test_language_voice(lang)
        assert res["success"] is True, f"Voice test failed for {lang}: {res}"
        assert res["provider_used"] in ("edge-tts", "gTTS", "synthetic-silent-fallback")
        out_file = settings.BASE_DIR / res["audio_url"].lstrip("/")
        assert out_file.exists(), f"Audio file not generated for {lang}"
        assert out_file.stat().st_size > 200

@pytest.mark.asyncio
async def test_full_video_reel_rendering():
    assert is_ffmpeg_available() is True, "FFmpeg must be installed and in PATH"

    project_id = "test-proj-001"
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM projects WHERE id = ?", (project_id,))
    if not c.fetchone():
        c.execute("""
        INSERT INTO projects (id, title, doi, source_type, extraction_status, metadata_verified)
        VALUES (?, 'Association of wearable device-measured VILPA with mortality', '10.1038/s41591-022-02100-x', 'pdf', 'extracted', 1)
        """, (project_id,))
    c.execute("SELECT count(*) FROM claims WHERE project_id = ?", (project_id,))
    if c.fetchone()[0] == 0:
        c.execute("""
        INSERT INTO claims (id, project_id, claim_id, claim_text, exact_quote, page_number, numerical_result, sample_size, limitations, uncertainty, evidence_status, review_status)
        VALUES ('clm-test-01', ?, 'CLM-01', '3-4 bouts of VILPA reduced mortality by 40%', '3-4 bouts of 1-2 min VILPA per day', 1, '40% reduction in all-cause mortality', 'n=25,241 non-exercisers', 'Observational accelerometer cohort', 'HR=0.60 (95% CI 0.50-0.73)', 'Directly supported', 'Approved')
        """, (project_id,))
    conn.commit()

    cursor = conn.cursor()
    cursor.execute("""
    SELECT scene_index, title, narrator_character, visual_description, narration_text, visual_type, duration_seconds, claim_ids_json
    FROM reel_scenes
    WHERE project_id = ? AND reel_mode = 'professional'
    ORDER BY scene_index ASC
    """, (project_id,))
    scenes = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if not scenes:
        from app.services.reel_generation.two_stories_generator import generate_two_stories
        generate_two_stories(project_id)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT scene_index, title, narrator_character, visual_description, narration_text, visual_type, duration_seconds, claim_ids_json
        FROM reel_scenes
        WHERE project_id = ? AND reel_mode = 'professional'
        ORDER BY scene_index ASC
        """, (project_id,))
        scenes = [dict(r) for r in cursor.fetchall()]
        conn.close()

    assert len(scenes) >= 1, "Must have scenes to render"

    res = await render_video_reel(project_id, "professional", scenes[:2], "en")
    assert res["success"] is True
    video_path = settings.BASE_DIR / res["video_url"].lstrip("/")
    assert video_path.exists(), f"Rendered video must exist at {video_path}"
    assert video_path.stat().st_size > 10000, "Rendered video file must be non-empty"
    assert res["resolution"] == "1080x1920"
