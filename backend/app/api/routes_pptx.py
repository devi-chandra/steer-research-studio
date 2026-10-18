import json
from fastapi import APIRouter, HTTPException
from app.core.database import get_db_connection
from app.services.powerpoint.pptx_generator import generate_powerpoint_presentation

router = APIRouter(prefix="/api/projects", tags=["PowerPoint Studio"])

@router.post("/{project_id}/generate/pptx")
def api_generate_pptx(project_id: str):
    try:
        res = generate_powerpoint_presentation(project_id)
        return {"success": True, "powerpoint": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{project_id}/pptx")
def api_get_pptx(project_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets WHERE project_id = ? AND asset_type = 'pptx'", (project_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"exists": False, "powerpoint": None}

    meta = json.loads(row["metadata_json"] or "{}")
    return {
        "exists": True,
        "asset_id": row["id"],
        "status": row["status"],
        "download_url": row["preview_url"],
        "slide_count": meta.get("slide_count", 10),
        "theme": meta.get("theme", "Steer Clinical Editorial"),
        "file_size_bytes": meta.get("file_size", 0)
    }
