import json
import uuid
import re
from typing import Dict, List, Any, Tuple
from app.core.database import get_db_connection
from app.core.ai_provider import ai_provider

VALID_STYLES = {"fruits_food", "inside_body", "relatable_human", "animated_explainer", "auto_select"}

EVERYDAY_STYLES = [
    {
        "id": "fruits_food",
        "title": "Talking Fruits & Food Characters",
        "description": "Expressive mangoes, apples, bananas, and anthropomorphic foods. Playful banter grounded in nutrition evidence.",
        "icon": "mango"
    },
    {
        "id": "inside_body",
        "title": "Inside Your Body",
        "description": "Body-themed evidence cards that present the paper's findings without inventing biological mechanisms.",
        "icon": "heart"
    },
    {
        "id": "relatable_human",
        "title": "Relatable Human Situations",
        "description": "Expressive cartoon humans walking, sitting, studying, or working desk routines that lead to research findings.",
        "icon": "human"
    },
    {
        "id": "animated_explainer",
        "title": "Animated Explainer",
        "description": "Evidence cards and motion graphics that present extracted findings without adding mechanisms.",
        "icon": "chart"
    },
    {
        "id": "auto_select",
        "title": "Auto-Select Best Story",
        "description": "Analyzes the paper's findings and automatically picks the most suitable style with creative rationale.",
        "icon": "sparkles"
    }
]

def determine_auto_style(claims: List[Dict[str, Any]], paper_title: str) -> Tuple[str, str]:
    """
    Analyzes the paper's title and claims to automatically select the most suitable story style.
    Returns (chosen_style, style_rationale).
    """
    text = (paper_title + " " + " ".join(c.get("claim_text", "") + " " + c.get("outcome_measured", "") for c in claims)).lower()

    if any(k in text for k in ["diet", "food", "nutrition", "fruit", "vitamin", "sugar", "meal", "antioxidant", "supplement", "caffeine", "coffee", "eating"]):
        return "fruits_food", "Paper investigates nutritional or dietary biomarkers. Talking Fruits & Food characters provide a fun, relatable visual metaphor without claiming miracle cures."

    if any(k in text for k in ["heart", "cardio", "blood pressure", "artery", "vascular", "brain", "neuron", "glucose", "insulin", "mitochondria", "organ", "cellular", "muscle"]):
        return "inside_body", "The paper has a physiological topic; scenes restate extracted evidence and do not infer a mechanism."

    if any(k in text for k in ["activity", "walk", "exercise", "sitting", "sedentary", "steps", "lifestyle", "habit", "desk", "sleep", "screen", "wearable", "accel"]):
        return "relatable_human", "Daily lifestyle and movement habits evaluated. Relatable Human characters in everyday situations connect directly with viewer routines."

    return "animated_explainer", "No visual topic was confidently identified; using neutral evidence graphics."

def generate_everyday_storyboard(project_id: str, requested_style: str = "auto_select") -> Dict[str, Any]:
    """
    Generates an entertaining, character-driven 5-7 scene Everyday Mode storyboard
    grounded in the paper's verified evidence ledger.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT title, doi, year FROM projects WHERE id = ?", (project_id,))
    proj = cursor.fetchone()
    if not proj:
        conn.close()
        raise ValueError(f"Project '{project_id}' not found.")

    cursor.execute("""
    SELECT id, claim_id, claim_text, exact_quote, page_number, section_heading,
           numerical_result, sample_size, limitations, uncertainty
    FROM claims WHERE project_id = ? AND evidence_status = 'Directly supported' ORDER BY page_number ASC
    """, (project_id,))
    claims = [dict(r) for r in cursor.fetchall()]

    if not claims:
        conn.close()
        raise ValueError(f"No claims found for project '{project_id}'. Extract claims first.")

    # 1. Resolve style
    if requested_style == "auto_select":
        chosen_style, rationale = determine_auto_style(claims, proj["title"])
    elif requested_style not in VALID_STYLES:
        conn.close()
        raise ValueError(f"Unsupported creative style '{requested_style}'. Choose one of: {sorted(VALID_STYLES)}")
    else:
        chosen_style = requested_style
        style_names = {
            "fruits_food": "Talking Fruits & Food Characters",
            "inside_body": "Inside Your Body: Science in Motion",
            "relatable_human": "Relatable Human Situations",
            "animated_explainer": "Animated Explainer"
        }
        rationale = f"User selected '{style_names.get(chosen_style, chosen_style)}' for entertaining creator-style delivery."

    # Build every spoken statement from the stored evidence verbatim. Creative style
    # changes presentation only; it must never add a study design, mechanism, or advice.
    character_by_style = {
        "fruits_food": ("Evidence Guide", "manny_mango", "reveal"),
        "inside_body": ("Evidence Guide", "happy_heart", "point"),
        "relatable_human": ("Research Presenter", "techie_raj", "explain"),
        "animated_explainer": ("Research Presenter", "explainer", "present"),
    }
    narrator, character_type, character_action = character_by_style[chosen_style]
    scenes = []
    for idx, claim in enumerate(claims[:5]):
        quote = (claim.get("exact_quote") or claim.get("claim_text") or "").strip()
        if not quote:
            continue
        scenes.append({
            "scene_index": len(scenes) + 1,
            "title": f"Evidence p.{claim.get('page_number', '?')}",
            "narrator_character": narrator,
            "character_type": character_type,
            "character_action": character_action,
            "visual_description": f"Present the paper's extracted statement as an engaging everyday visual (page {claim.get('page_number', '?')}).",
            "narration_text": ai_provider._to_everyday_conversational(quote, claim.get("numerical_result", "")),
            "duration_seconds": 6.0,
            "claim_ids": [claim["claim_id"]],
        })
    if not scenes:
        conn.close()
        raise ValueError("No source-backed claim text is available for reel generation.")

    # 3. Persist into reel_scenes under reel_mode = 'everyday'
    cursor.execute("DELETE FROM reel_scenes WHERE project_id = ? AND reel_mode = 'everyday'", (project_id,))

    for sc in scenes:
        sc["style_type"] = chosen_style
        sc_id = f"scn-evry-{uuid.uuid4().hex[:8]}"
        cursor.execute("""
        INSERT INTO reel_scenes (
            id, project_id, reel_mode, scene_index, title, narrator_character,
            visual_description, narration_text, visual_type, duration_seconds,
            claim_ids_json, language_code, style_type, character_type, character_action, render_status
        ) VALUES (?, ?, 'everyday', ?, ?, ?, ?, ?, 'character', ?, ?, 'en', ?, ?, ?, 'ready')
        """, (
            sc_id, project_id, sc["scene_index"], sc["title"], sc.get("narrator_character", "Presenter"),
            sc["visual_description"], sc["narration_text"], sc.get("duration_seconds", 4.5),
            json.dumps(sc.get("claim_ids", [])), chosen_style, sc.get("character_type", ""),
            sc.get("character_action", "")
        ))

    conn.commit()
    conn.close()

    return {
        "project_id": project_id,
        "style_type": chosen_style,
        "style_chosen": chosen_style,
        "style_rationale": rationale,
        "scenes_count": len(scenes),
        "scenes": scenes
    }
