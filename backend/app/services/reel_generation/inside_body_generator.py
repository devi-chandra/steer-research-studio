import json
import uuid
from typing import Dict, List, Any
from app.core.database import get_db_connection
from app.core.ai_provider import ai_provider

def generate_inside_body_storyboard(project_id: str) -> Dict[str, Any]:
    """
    Feature 2: Inside Your Body — Science in Motion.
    Explains physiological / biological mechanisms tailored specifically to the paper's topic.
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
           numerical_result, sample_size, limitations
    FROM claims WHERE project_id = ? AND evidence_status = 'Directly supported' ORDER BY page_number ASC
    """, (project_id,))
    claims = [dict(r) for r in cursor.fetchall()]

    if not claims:
        conn.close()
        raise ValueError("Extraction required before generating inside-body animation.")

    inside_data, provider_used = ai_provider.generate_inside_body(claims, proj["title"])

    # Clear previous inside_body scenes
    cursor.execute("DELETE FROM reel_scenes WHERE project_id = ? AND reel_mode = 'inside_body'", (project_id,))

    # Insert new scenes
    for sc in inside_data["scenes"]:
        sc_id = f"scn-body-{uuid.uuid4().hex[:8]}"
        cursor.execute("""
        INSERT INTO reel_scenes (
            id, project_id, reel_mode, scene_index, title, narrator_character,
            visual_description, narration_text, visual_type, duration_seconds,
            claim_ids_json, language_code, style_type, character_type, character_action, render_status
        ) VALUES (?, ?, 'inside_body', ?, ?, ?, ?, ?, 'animation', ?, ?, 'en', 'inside_body', 'happy_heart', 'point', 'ready')
        """, (
            sc_id, project_id, sc["scene_index"], sc["title"], f"{inside_data['target_system']} Narrator",
            sc["visual_description"], sc["narration_text"], sc.get("duration_seconds", 5.0),
            json.dumps([sc.get("claim_id", "CLM-01")])
        ))

    conn.commit()
    conn.close()

    return {
        "project_id": project_id,
        "provider_used": provider_used,
        "mechanism_type": inside_data["mechanism_type"],
        "target_system": inside_data["target_system"],
        "safeguard_notice": inside_data["safeguard_notice"],
        "scenes": inside_data["scenes"]
    }
