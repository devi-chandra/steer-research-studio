import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.core.config import settings
from app.core.database import get_db_connection
from app.core.security import sanitize_filename
from app.services.ingestion.pdf_extractor import extract_pdf_document
from app.services.ingestion.url_extractor import extract_url_document
from app.schemas.project import IngestUrlRequest, ProjectResponse

router = APIRouter(prefix="/api/projects", tags=["Projects"])

@router.post("/upload-pdf")
async def upload_pdf_project(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    project_id = f"proj-{uuid.uuid4().hex[:8]}"
    clean_name = sanitize_filename(file.filename)
    dest_path = settings.UPLOADS_DIR / f"{project_id}_{clean_name}"

    # Read and save file
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds 50MB maximum limit.")

    with open(dest_path, "wb") as f:
        f.write(content)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO projects (id, title, source_type, source_path, extraction_status)
    VALUES (?, ?, 'pdf', ?, 'pending')
    """, (project_id, clean_name, str(dest_path)))
    conn.commit()
    conn.close()

    # Automatically trigger PDF extraction
    try:
        extraction_res = extract_pdf_document(dest_path, project_id)
        if extraction_res["total_pages"] == 0 or extraction_res["total_characters"] == 0:
            raise ValueError("PDF contains no extractable text.")
        if extraction_res["is_scanned"]:
            raise ValueError("PDF appears to be scanned or image-only; OCR is unavailable, so evidence generation was stopped.")
        return {
            "success": True,
            "project_id": project_id,
            "message": "PDF uploaded and processed successfully.",
            "extraction": extraction_res
        }
    except Exception as e:
        conn = get_db_connection()
        conn.execute(
            "UPDATE projects SET extraction_status = 'failed', limitation_notes = ? WHERE id = ?",
            (str(e), project_id),
        )
        conn.commit()
        conn.close()
        raise HTTPException(status_code=422, detail=f"PDF extraction failed: {e}")

@router.post("/ingest-url")
async def ingest_url_project(req: IngestUrlRequest):
    project_id = f"proj-{uuid.uuid4().hex[:8]}"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO projects (id, title, source_type, source_url, extraction_status)
    VALUES (?, ?, 'url', ?, 'pending')
    """, (project_id, req.url, req.url))
    conn.commit()
    conn.close()

    try:
        extraction_res = await extract_url_document(req.url, project_id)
        return {
            "success": True,
            "project_id": project_id,
            "message": "URL ingested and processed successfully.",
            "extraction": extraction_res
        }
    except Exception as e:
        # Update failed status honestly
        conn = get_db_connection()
        conn.execute("UPDATE projects SET extraction_status = 'failed', limitation_notes = ? WHERE id = ?", (str(e), project_id))
        conn.commit()
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("")
def list_projects():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT p.*,
           (SELECT COUNT(*) FROM claims WHERE project_id = p.id) as claims_count,
           (SELECT COUNT(*) FROM assets WHERE project_id = p.id) as assets_count,
           (SELECT COUNT(*) FROM claims WHERE project_id = p.id AND review_status = 'Pending Review') as pending_reviews_count
    FROM projects p
    ORDER BY p.created_at DESC
    """)
    projects = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"projects": projects}

@router.get("/{project_id}")
def get_project(project_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT p.*,
           (SELECT COUNT(*) FROM claims WHERE project_id = p.id) as claims_count,
           (SELECT COUNT(*) FROM assets WHERE project_id = p.id) as assets_count,
           (SELECT COUNT(*) FROM claims WHERE project_id = p.id AND review_status = 'Pending Review') as pending_reviews_count
    FROM projects p
    WHERE p.id = ?
    """, (project_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Project not found.")

    # Get page summary
    cursor.execute("SELECT page_number, char_count, section_headings FROM document_pages WHERE project_id = ? ORDER BY page_number ASC", (project_id,))
    pages = [dict(r) for r in cursor.fetchall()]
    conn.close()

    proj_dict = dict(row)
    proj_dict["pages"] = pages
    return proj_dict

@router.delete("/{project_id}")
def delete_project(project_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"Project {project_id} deleted."}
