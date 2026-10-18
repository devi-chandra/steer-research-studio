import json
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Literal
from app.core.database import get_db_connection
from app.services.reel_generation.two_stories_generator import generate_two_stories
from app.services.reel_generation.inside_body_generator import generate_inside_body_storyboard
from app.services.reel_generation.everyday_reel_generator import (
    generate_everyday_storyboard,
    determine_auto_style,
    EVERYDAY_STYLES
)
from app.services.localization.local_voice_service import generate_localvoice_script, SUPPORTED_LANGUAGES
from app.services.reel_generation.video_renderer import render_video_reel, is_ffmpeg_available
from app.services.localization.tts_adapter import tts_adapter, VOICE_MAP

router = APIRouter(prefix="/api/projects", tags=["Reel Studio & Localization"])

VALID_REEL_MODES = {
    "professional", "everyday", "inside_body", "localvoice",
    "fruits_food", "animated_explainer", "clean_infographic",
    "colorful_cartoon", "relatable_human"
}

class LocalVoiceRequest(BaseModel):
    language_code: str = "hi_en"

class EverydayReelRequest(BaseModel):
    style: Optional[str] = "auto_select"

class ReelConfigRequest(BaseModel):
    style: Literal["fruits_food", "inside_body", "relatable_human", "animated_explainer"]
    theme: Literal["steer", "colorful_cartoon", "warm_editorial", "pastel_educational", "clean_infographic"]

class RenderReelRequest(BaseModel):
    reel_mode: str = "professional"  # professional, everyday, inside_body, localvoice
    language_code: Optional[str] = "en"
    style: Optional[str] = "auto_select"
    theme: Optional[str] = None

@router.get("/{project_id}/reel-config")
def get_reel_config(project_id: str):
    conn = get_db_connection()
    row = conn.execute("SELECT reel_style, reel_theme FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Project not found.")
    return {"project_id": project_id, "style": row["reel_style"], "theme": row["reel_theme"]}

@router.put("/{project_id}/reel-config")
def update_reel_config(project_id: str, req: ReelConfigRequest):
    conn = get_db_connection()
    cur = conn.execute(
        "UPDATE projects SET reel_style = ?, reel_theme = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (req.style, req.theme, project_id),
    )
    conn.commit()
    conn.close()
    if not cur.rowcount:
        raise HTTPException(status_code=404, detail="Project not found.")
    return {"project_id": project_id, "style": req.style, "theme": req.theme}

@router.post("/{project_id}/generate/everyday-reel")
def api_generate_everyday_reel(project_id: str, req: EverydayReelRequest):
    try:
        res = generate_everyday_storyboard(project_id, req.style or "auto_select")
        return {"success": True, "everyday": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{project_id}/everyday-reel")
def api_get_everyday_reel(project_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT scene_index, title, narrator_character, visual_description, narration_text, visual_type, duration_seconds, claim_ids_json, style_type, character_type, character_action
    FROM reel_scenes
    WHERE project_id = ? AND reel_mode = 'everyday'
    ORDER BY scene_index ASC
    """, (project_id,))
    scenes = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT id, title, reel_style, reel_theme FROM projects WHERE id = ?", (project_id,))
    proj = cursor.fetchone()
    cursor.execute("SELECT id, claim_id, claim_text FROM claims WHERE project_id = ?", (project_id,))
    claims = [dict(r) for r in cursor.fetchall()]
    conn.close()

    for s in scenes:
        s["claim_ids"] = json.loads(s.get("claim_ids_json", "[]"))

    auto_style, rationale = determine_auto_style(claims, proj["title"] if proj else "")
    current_style = scenes[0].get("style_type") if scenes else auto_style

    return {
        "exists": bool(scenes),
        "scenes": scenes,
        "current_style": current_style,
        "recommended_style": auto_style,
        "rationale": rationale,
        "available_styles": EVERYDAY_STYLES
    }

@router.post("/{project_id}/generate/two-stories")
def api_generate_two_stories(project_id: str):
    try:
        res = generate_two_stories(project_id)
        return {"success": True, "stories": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{project_id}/two-stories")
def api_get_two_stories(project_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT scene_index, title, narrator_character, visual_description, narration_text, visual_type, duration_seconds, claim_ids_json
    FROM reel_scenes
    WHERE project_id = ? AND reel_mode = 'professional'
    ORDER BY scene_index ASC
    """, (project_id,))
    prof_scenes = [dict(r) for r in cursor.fetchall()]

    cursor.execute("""
    SELECT scene_index, title, narrator_character, visual_description, narration_text, visual_type, duration_seconds, claim_ids_json
    FROM reel_scenes
    WHERE project_id = ? AND reel_mode = 'everyday'
    ORDER BY scene_index ASC
    """, (project_id,))
    evry_scenes = [dict(r) for r in cursor.fetchall()]
    conn.close()

    for s in prof_scenes + evry_scenes:
        s["claim_ids"] = json.loads(s.get("claim_ids_json", "[]"))

    # Comparison view
    comparison = []
    for i in range(min(len(prof_scenes), len(evry_scenes))):
        comparison.append({
            "scene_index": i + 1,
            "claim_id": prof_scenes[i]["claim_ids"][0] if prof_scenes[i]["claim_ids"] else "CLM-01",
            "professional_wording": prof_scenes[i]["narration_text"],
            "everyday_wording": evry_scenes[i]["narration_text"],
            "shared_facts": "Grounded in same extracted claim ID"
        })

    return {
        "exists": bool(prof_scenes and evry_scenes),
        "professional": {"scenes": prof_scenes},
        "everyday": {"scenes": evry_scenes},
        "shared_evidence_comparison": comparison
    }

@router.post("/{project_id}/generate/inside-body")
def api_generate_inside_body(project_id: str):
    try:
        res = generate_inside_body_storyboard(project_id)
        return {"success": True, "inside_body": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{project_id}/inside-body")
def api_get_inside_body(project_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT scene_index, title, narrator_character, visual_description, narration_text, visual_type, duration_seconds, claim_ids_json
    FROM reel_scenes
    WHERE project_id = ? AND reel_mode = 'inside_body'
    ORDER BY scene_index ASC
    """, (project_id,))
    scenes = [dict(r) for r in cursor.fetchall()]
    conn.close()

    for s in scenes:
        s["claim_ids"] = json.loads(s.get("claim_ids_json", "[]"))

    return {"exists": bool(scenes), "scenes": scenes}

@router.post("/{project_id}/generate/localvoice")
def api_generate_localvoice(project_id: str, req: LocalVoiceRequest):
    if req.language_code not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported LocalVoice language '{req.language_code}'. Supported languages: {sorted(list(SUPPORTED_LANGUAGES))}."
        )
    try:
        res = generate_localvoice_script(project_id, req.language_code)
        return {"success": True, "localvoice": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{project_id}/localvoice")
def api_get_localvoice(project_id: str, language_code: Optional[str] = "hi_en"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT scene_index, title, narrator_character, visual_description, narration_text, visual_type, duration_seconds, claim_ids_json, language_code, subtitle_native
    FROM reel_scenes
    WHERE project_id = ? AND reel_mode = 'localvoice' AND language_code = ?
    ORDER BY scene_index ASC
    """, (project_id, language_code))
    scenes = [dict(r) for r in cursor.fetchall()]
    conn.close()

    for s in scenes:
        s["claim_ids"] = json.loads(s.get("claim_ids_json", "[]"))

    return {
        "exists": bool(scenes),
        "language_code": language_code,
        "translation_available": False if language_code != "en" else True,
        "translation_notice": (
            "Regional translation provider unavailable. Original English source text preserved to prevent clinical inaccuracy."
            if language_code != "en" else "English source text active."
        ),
        "scenes": scenes
    }

@router.post("/{project_id}/render/video-reel")
async def api_render_video_reel(project_id: str, req: RenderReelRequest):
    # 1. Validate reel_mode
    if req.reel_mode not in VALID_REEL_MODES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid reel mode '{req.reel_mode}'. Must be one of: {sorted(list(VALID_REEL_MODES))}."
        )

    # 2. Validate language for localvoice
    lang = req.language_code or "en"
    if req.reel_mode == "localvoice" and lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported LocalVoice language '{lang}'. Supported languages: {sorted(list(SUPPORTED_LANGUAGES))}."
        )

    # 3. Validate project existence and evidence claims
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, reel_style, reel_theme FROM projects WHERE id = ?", (project_id,))
    proj = cursor.fetchone()
    if not proj:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")

    cursor.execute("SELECT COUNT(*) FROM claims WHERE project_id = ?", (project_id,))
    claim_count = cursor.fetchone()[0]
    conn.close()

    if claim_count == 0:
        raise HTTPException(status_code=400, detail=f"No verified evidence claims found for project '{project_id}'. Extract claims first.")

    # 4. Map visual modes if passed as reel_mode
    target_mode = req.reel_mode
    if req.reel_mode in ("fruits_food", "animated_explainer", "relatable_human"):
        target_mode = "everyday"
        if not req.style or req.style == "auto_select":
            req.style = req.reel_mode
    elif req.reel_mode == "clean_infographic":
        target_mode = "everyday"
        req.style = "animated_explainer"
        if not req.theme:
            req.theme = "clean_infographic"
    elif req.reel_mode == "colorful_cartoon":
        target_mode = "everyday"
        req.style = "fruits_food"
        if not req.theme:
            req.theme = "colorful_cartoon"

    conn = get_db_connection()
    cursor = conn.cursor()

    if target_mode == "localvoice":
        cursor.execute("""
        SELECT scene_index, title, narrator_character, visual_description, narration_text, visual_type, duration_seconds, claim_ids_json, language_code, subtitle_native, style_type, character_type, character_action
        FROM reel_scenes
        WHERE project_id = ? AND reel_mode = 'localvoice' AND language_code = ?
        ORDER BY scene_index ASC
        """, (project_id, lang))
        scenes = [dict(r) for r in cursor.fetchall()]
        conn.close()

        if not scenes:
            try:
                generate_localvoice_script(project_id, lang)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to auto-generate LocalVoice storyboard for {lang}: {str(e)}")

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            SELECT scene_index, title, narrator_character, visual_description, narration_text, visual_type, duration_seconds, claim_ids_json, language_code, subtitle_native, style_type, character_type, character_action
            FROM reel_scenes
            WHERE project_id = ? AND reel_mode = 'localvoice' AND language_code = ?
            ORDER BY scene_index ASC
            """, (project_id, lang))
            scenes = [dict(r) for r in cursor.fetchall()]
            conn.close()

    elif target_mode == "everyday":
        cursor.execute("""
        SELECT scene_index, title, narrator_character, visual_description, narration_text, visual_type, duration_seconds, claim_ids_json, subtitle_native, style_type, character_type, character_action
        FROM reel_scenes
        WHERE project_id = ? AND reel_mode = 'everyday'
        ORDER BY scene_index ASC
        """, (project_id,))
        scenes = [dict(r) for r in cursor.fetchall()]
        conn.close()

        # If scenes missing, or user requested a specific style different from current
        selected_style = req.style if req.style and req.style != "auto_select" else (proj["reel_style"] or "auto_select")
        need_gen = (not scenes) or (scenes and scenes[0].get("style_type") != selected_style)
        if need_gen:
            try:
                generate_everyday_storyboard(project_id, selected_style)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to generate everyday storyboard: {str(e)}")

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            SELECT scene_index, title, narrator_character, visual_description, narration_text, visual_type, duration_seconds, claim_ids_json, subtitle_native, style_type, character_type, character_action
            FROM reel_scenes
            WHERE project_id = ? AND reel_mode = 'everyday'
            ORDER BY scene_index ASC
            """, (project_id,))
            scenes = [dict(r) for r in cursor.fetchall()]
            conn.close()

    elif target_mode == "professional":
        cursor.execute("""
        SELECT scene_index, title, narrator_character, visual_description, narration_text, visual_type, duration_seconds, claim_ids_json, subtitle_native
        FROM reel_scenes
        WHERE project_id = ? AND reel_mode = 'professional'
        ORDER BY scene_index ASC
        """, (project_id,))
        scenes = [dict(r) for r in cursor.fetchall()]
        conn.close()

        if not scenes:
            try:
                generate_two_stories(project_id)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to auto-generate professional storyboard: {str(e)}")

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            SELECT scene_index, title, narrator_character, visual_description, narration_text, visual_type, duration_seconds, claim_ids_json, subtitle_native
            FROM reel_scenes
            WHERE project_id = ? AND reel_mode = 'professional'
            ORDER BY scene_index ASC
            """, (project_id,))
            scenes = [dict(r) for r in cursor.fetchall()]
            conn.close()

    elif target_mode == "inside_body":
        cursor.execute("""
        SELECT scene_index, title, narrator_character, visual_description, narration_text, visual_type, duration_seconds, claim_ids_json, subtitle_native, style_type, character_type, character_action
        FROM reel_scenes
        WHERE project_id = ? AND reel_mode = 'inside_body'
        ORDER BY scene_index ASC
        """, (project_id,))
        scenes = [dict(r) for r in cursor.fetchall()]
        conn.close()

        if not scenes:
            try:
                generate_inside_body_storyboard(project_id)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to auto-generate inside_body storyboard: {str(e)}")

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            SELECT scene_index, title, narrator_character, visual_description, narration_text, visual_type, duration_seconds, claim_ids_json, subtitle_native, style_type, character_type, character_action
            FROM reel_scenes
            WHERE project_id = ? AND reel_mode = 'inside_body'
            ORDER BY scene_index ASC
            """, (project_id,))
            scenes = [dict(r) for r in cursor.fetchall()]
            conn.close()

        for sc in scenes:
            sc["style_type"] = "inside_body"
            sc["character_type"] = sc.get("character_type") or "happy_heart"
            sc["character_action"] = sc.get("character_action") or "point"

    if not scenes:
        raise HTTPException(status_code=400, detail=f"No scenes generated for mode '{req.reel_mode}'. Generate storyboard first.")

    for s in scenes:
        s["claim_ids"] = json.loads(s.get("claim_ids_json", "[]"))

    try:
        selected_theme = req.theme or proj["reel_theme"] or "steer"
        if req.style == "animated_explainer" and not req.theme:
            selected_theme = "clean_infographic"
        if selected_theme not in {"steer", "colorful_cartoon", "warm_editorial", "pastel_educational", "clean_infographic"}:
            raise HTTPException(status_code=422, detail=f"Unsupported reel theme '{selected_theme}'.")
        res = await render_video_reel(project_id, target_mode, scenes, lang, theme=selected_theme)
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Video rendering failed: {str(e)}")

@router.get("/tts/test-voice")
async def api_test_tts_voice(language_code: str = Query("hi_en")):
    res = await tts_adapter.test_language_voice(language_code)
    return res
