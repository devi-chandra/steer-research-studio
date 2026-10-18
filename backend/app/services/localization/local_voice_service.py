import json
import uuid
from typing import Dict, List, Any
from app.core.database import get_db_connection
from app.core.ai_provider import ai_provider
from app.services.reel_generation.two_stories_generator import generate_two_stories

SUPPORTED_LANGUAGES = {"en", "hi_en", "te_en", "ta_en", "kn_en", "ml_en"}

def generate_localvoice_script(project_id: str, language_code: str = "hi_en") -> Dict[str, Any]:
    """
    Feature 3: LocalVoice Regional Health Reels.
    Localizes Everyday Mode script into target regional language pair, preserving medical facts.
    Automatically generates Everyday Mode storyboard first if it does not yet exist.
    """
    if language_code not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language code '{language_code}'. Supported languages: {sorted(list(SUPPORTED_LANGUAGES))}")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if everyday scenes exist; if not, auto-generate them
    cursor.execute("""
    SELECT scene_index, title, narrator_character, visual_description, narration_text, visual_type, duration_seconds, claim_ids_json, style_type, character_type, character_action
    FROM reel_scenes
    WHERE project_id = ? AND reel_mode = 'everyday'
    ORDER BY scene_index ASC
    """, (project_id,))
    scenes = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if not scenes:
        # Automatically generate two stories (Professional & Everyday)
        generate_two_stories(project_id)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT scene_index, title, narrator_character, visual_description, narration_text, visual_type, duration_seconds, claim_ids_json, style_type, character_type, character_action
        FROM reel_scenes
        WHERE project_id = ? AND reel_mode = 'everyday'
        ORDER BY scene_index ASC
        """, (project_id,))
        scenes = [dict(r) for r in cursor.fetchall()]
        conn.close()

    if not scenes:
        raise ValueError(f"Unable to retrieve or generate Everyday Mode scenes for project '{project_id}'. Evidence claims required.")

    for sc in scenes:
        sc["claim_ids"] = json.loads(sc.get("claim_ids_json", "[]"))

    localized_scenes, provider_used = ai_provider.localize_script(scenes, language_code)

    # Persist localized scenes cleanly with transaction
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reel_scenes WHERE project_id = ? AND reel_mode = 'localvoice' AND language_code = ?", (project_id, language_code))

    for sc in localized_scenes:
        sc_id = f"scn-loc-{uuid.uuid4().hex[:8]}"
        cursor.execute("""
        INSERT INTO reel_scenes (
            id, project_id, reel_mode, scene_index, title, narrator_character,
            visual_description, narration_text, visual_type, duration_seconds,
            claim_ids_json, language_code, subtitle_native, render_status,
            style_type, character_type, character_action
        ) VALUES (?, ?, 'localvoice', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ready', ?, ?, ?)
        """, (
            sc_id, project_id, sc["scene_index"], sc["title"], sc.get("narrator_character", "Regional Lead"),
            sc["visual_description"], sc["narration_text"], sc.get("visual_type", "character"),
            sc.get("duration_seconds", 4.5), json.dumps(sc.get("claim_ids", [])),
            language_code, sc.get("subtitle_native", sc["narration_text"]),
            sc.get("style_type", "relatable_human"), sc.get("character_type", ""), sc.get("character_action", "")
        ))

    conn.commit()
    conn.close()

    return {
        "project_id": project_id,
        "language_code": language_code,
        "provider_used": provider_used,
        "scenes": localized_scenes
    }
