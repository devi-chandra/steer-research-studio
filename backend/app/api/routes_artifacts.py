import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.models import Artifact
from app.schemas.schemas import ArtifactResponse

router = APIRouter(tags=["artifacts"])

@router.get("/api/projects/{project_id}/artifacts", response_model=List[ArtifactResponse])
def list_project_artifacts(project_id: str, db: Session = Depends(get_db)):
    artifacts = db.query(Artifact).filter(Artifact.project_id == project_id).order_by(Artifact.created_at.desc()).all()
    return artifacts

@router.get("/api/artifacts/{artifact_id}/file")
def get_artifact_file(artifact_id: str, download: bool = Query(False), db: Session = Depends(get_db)):
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    file_path = Path(artifact.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Artifact file does not exist on disk")

    disposition = "attachment" if download else "inline"
    return FileResponse(
        path=str(file_path),
        media_type=artifact.mime_type,
        filename=artifact.filename,
        headers={"Content-Disposition": f'{disposition}; filename="{artifact.filename}"'}
    )
