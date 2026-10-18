import json
import uuid
from typing import Dict, List, Any
from app.core.database import get_db_connection
from app.core.ai_provider import ai_provider

def generate_two_stories(project_id: str) -> Dict[str, Any]:
    """
    Feature 1: Same Evidence, Two Stories.
    Derives Mode A (Professional) and Mode B (Everyday) from identical evidence claims.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT title, doi, year FROM projects WHERE id = ?", (project_id,))
    proj = cursor.fetchone()
    if not proj:
        conn.close()
        raise ValueError(f"Project {project_id} not found.")

    cursor.execute("""
    SELECT id, claim_id, claim_text, exact_quote, page_number, section_heading,
           numerical_result, sample_size, limitations, uncertainty
    FROM claims WHERE project_id = ? AND evidence_status = 'Directly supported' ORDER BY page_number ASC
    """, (project_id,))
    claims = [dict(r) for r in cursor.fetchall()]

    if not claims:
        conn.close()
        raise ValueError(f"No claims found for project {project_id}. Extraction required first.")

    # Call AI Provider
    stories_data, provider_used = ai_provider.generate_two_stories(claims, proj["title"])

    # Clear previous scenes for this project
    cursor.execute("DELETE FROM reel_scenes WHERE project_id = ? AND reel_mode IN ('professional', 'everyday')", (project_id,))

    # Save Professional scenes
    for sc in stories_data["professional"]["scenes"]:
        sc_id = f"scn-prof-{uuid.uuid4().hex[:8]}"
        cursor.execute("""
        INSERT INTO reel_scenes (
            id, project_id, reel_mode, scene_index, title, narrator_character,
            visual_description, narration_text, visual_type, duration_seconds,
            claim_ids_json, language_code, render_status
        ) VALUES (?, ?, 'professional', ?, ?, ?, ?, ?, ?, ?, ?, 'en', 'ready')
        """, (
            sc_id, project_id, sc["scene_index"], sc["title"], sc.get("narrator_character", "Senior Clinical Lead"),
            sc["visual_description"], sc["narration_text"], sc.get("visual_type", "graphic"),
            sc.get("duration_seconds", 4.5), json.dumps(sc.get("claim_ids", []))
        ))

    # Save Everyday scenes
    for sc in stories_data["everyday"]["scenes"]:
        sc_id = f"scn-evry-{uuid.uuid4().hex[:8]}"
        cursor.execute("""
        INSERT INTO reel_scenes (
            id, project_id, reel_mode, scene_index, title, narrator_character,
            visual_description, narration_text, visual_type, duration_seconds,
            claim_ids_json, language_code, style_type, character_type, character_action, render_status
        ) VALUES (?, ?, 'everyday', ?, ?, ?, ?, ?, ?, ?, ?, 'en', ?, ?, ?, 'ready')
        """, (
            sc_id, project_id, sc["scene_index"], sc["title"], sc.get("narrator_character", "Curious Scientist Character"),
            sc["visual_description"], sc["narration_text"], sc.get("visual_type", "character"),
            sc.get("duration_seconds", 4.5), json.dumps(sc.get("claim_ids", [])),
            sc.get("style_type", "relatable_human"), sc.get("character_type", "techie_raj"),
            sc.get("character_action", "explain")
        ))

    conn.commit()
    conn.close()

    return {
        "project_id": project_id,
        "provider_used": provider_used,
        "professional": stories_data["professional"],
        "everyday": stories_data["everyday"],
        "shared_evidence_comparison": stories_data["shared_evidence_comparison"]
    }
