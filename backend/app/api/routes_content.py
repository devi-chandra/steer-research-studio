import json
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db_connection
from app.services.content_generation.carousel_generator import generate_instagram_carousel
from app.services.content_generation.post_generator import generate_static_instagram_post

router = APIRouter(prefix="/api/projects", tags=["Content Studio"])

class GenerateCarouselRequest(BaseModel):
    slide_count: Optional[int] = 6

class GeneratePostRequest(BaseModel):
    custom_headline: Optional[str] = ""
    custom_body: Optional[str] = ""

@router.post("/{project_id}/generate/carousel")
def api_generate_carousel(project_id: str, req: GenerateCarouselRequest):
    try:
        count = req.slide_count if req.slide_count and 3 <= req.slide_count <= 10 else 6
        res = generate_instagram_carousel(project_id, slide_count=count)
        return {"success": True, "carousel": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{project_id}/carousel")
def api_get_carousel(project_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets WHERE project_id = ? AND asset_type = 'carousel'", (project_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"exists": False, "carousel": None}

    meta = json.loads(row["metadata_json"] or "{}")
    return {
        "exists": True,
        "asset_id": row["id"],
        "status": row["status"],
        "preview_url": row["preview_url"],
        "zip_url": f"/storage/generated/carousels/{project_id}/carousel_{project_id}.zip",
        "slides": meta.get("slides", [])
    }

@router.post("/{project_id}/generate/post")
def api_generate_post(project_id: str, req: GeneratePostRequest):
    try:
        res = generate_static_instagram_post(project_id, req.custom_headline, req.custom_body)
        return {"success": True, "post": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{project_id}/post")
def api_get_post(project_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets WHERE project_id = ? AND asset_type = 'post'", (project_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"exists": False, "post": None}

    meta = json.loads(row["metadata_json"] or "{}")
    return {
        "exists": True,
        "asset_id": row["id"],
        "status": row["status"],
        "preview_url": row["preview_url"],
        "headline": meta.get("headline", ""),
        "explanation": meta.get("explanation", ""),
        "limitations": meta.get("limitations", "")
    }
