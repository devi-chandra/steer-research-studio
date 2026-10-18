import pytest
import asyncio
from app.services.reel_generation.everyday_reel_generator import (
    generate_everyday_storyboard,
    determine_auto_style,
    EVERYDAY_STYLES,
    VALID_STYLES
)
from app.services.reel_generation.video_renderer import render_video_reel
from app.services.localization.local_voice_service import generate_localvoice_script
from app.core.ai_provider import ai_provider

from app.core.database import get_db_connection

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

def test_available_styles_definition():
    assert len(EVERYDAY_STYLES) == 5
    style_ids = {s["id"] for s in EVERYDAY_STYLES}
    assert style_ids == VALID_STYLES

def test_auto_style_determination():
    # Test nutrition
    style, rationale = determine_auto_style([], "Impact of Mediterranean Diet on Health")
    assert style == "fruits_food"
    assert "nutritional" in rationale.lower()

    # Test physiological / heart
    style, rationale = determine_auto_style([], "Vascular Endothelial Function and Blood Pressure")
    assert style == "inside_body"
    assert "physiological" in rationale.lower()

    # Test daily habit / exercise
    style, rationale = determine_auto_style([], "Association of daily step count and walking bouts")
    assert style == "relatable_human"
    assert "lifestyle" in rationale.lower()

    # Test complex trial
    style, rationale = determine_auto_style([], "Double-blind randomized clinical trial endpoints")
    assert style == "animated_explainer"

def test_generate_all_storyboard_styles():
    from app.core.database import get_db_connection
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT claim_id, claim_text, exact_quote FROM claims WHERE project_id = ? ORDER BY page_number ASC",
        (PROJECT_ID,),
    ).fetchall()
    conn.close()
    claim_text_by_id = {r["claim_id"]: (r["exact_quote"] or r["claim_text"]) for r in rows}

    for style in ["fruits_food", "inside_body", "relatable_human", "animated_explainer", "auto_select"]:
        res = generate_everyday_storyboard(PROJECT_ID, style)
        scenes = res["scenes"]
        assert 1 <= len(scenes) <= min(5, len(claim_text_by_id))
        assert scenes[0]["scene_index"] == 1
        for s in scenes:
            assert s["claim_ids"]
            assert s["narration_text"] == ai_provider._to_everyday_conversational(claim_text_by_id[s["claim_ids"][0]])
            assert s.get("character_type")
            assert s.get("character_action")

def test_professional_and_inside_body_scripts_repeat_only_source_quotes():
    from app.core.database import get_db_connection
    conn = get_db_connection()
    claims = [dict(r) for r in conn.execute(
        "SELECT claim_id, claim_text, exact_quote, page_number FROM claims WHERE project_id = ? AND evidence_status = 'Directly supported' ORDER BY page_number ASC",
        (PROJECT_ID,),
    ).fetchall()]
    conn.close()
    source_quotes = {c["exact_quote"] or c["claim_text"] for c in claims}
    stories, _ = ai_provider.generate_two_stories(claims, "test paper")
    inside, _ = ai_provider.generate_inside_body(claims, "test paper")
    for scene in stories["professional"]["scenes"] + inside["scenes"]:
        assert scene["narration_text"] in source_quotes
    # Everyday mode translates findings into conversational language
    assert stories["everyday"]["scenes"][0]["narration_text"] != stories["professional"]["scenes"][0]["narration_text"]
    assert any("40%" in scene["narration_text"] or "risk" in scene["narration_text"].lower() for scene in stories["everyday"]["scenes"])
    for scene in stories["everyday"]["scenes"]:
        assert "researchers found" in scene["narration_text"].lower() or "science" in scene["narration_text"].lower()

@pytest.mark.asyncio
async def test_render_everyday_video_reel():
    res = generate_everyday_storyboard(PROJECT_ID, "relatable_human")
    # Render with allow_mock_tts=True for fast automated testing
    render_result = await render_video_reel(PROJECT_ID, "everyday", res["scenes"][:3], lang_code="en", allow_mock_tts=True)
    assert render_result["success"] is True
    assert render_result["resolution"] == "1080x1920"
    assert render_result["file_size_bytes"] > 100000
    assert "everyday" in render_result["video_url"]

@pytest.mark.asyncio
async def test_localvoice_everyday_integration():
    loc_res = generate_localvoice_script(PROJECT_ID, "hi_en")
    assert loc_res["language_code"] == "hi_en"
    assert len(loc_res["scenes"]) >= 5
    for sc in loc_res["scenes"]:
        assert sc.get("subtitle_native")
        assert sc.get("style_type")
