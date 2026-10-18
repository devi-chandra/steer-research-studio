from fastapi import APIRouter, HTTPException
from app.services.export.export_service import generate_export_package

router = APIRouter(prefix="/api/projects", tags=["Export Center"])

@router.post("/{project_id}/export")
def api_generate_export(project_id: str):
    try:
        res = generate_export_package(project_id)
        return {"success": True, "export": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{project_id}/export")
def api_get_export(project_id: str):
    try:
        res = generate_export_package(project_id)
        return {"success": True, "export": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
