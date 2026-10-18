import uuid
from typing import Dict, List, Any
from app.core.database import get_db_connection
from app.core.ai_provider import ai_provider

def extract_and_store_claims(project_id: str) -> Dict[str, Any]:
    """
    Extracts structured evidence claims from stored document pages and saves them to the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get project info
    cursor.execute("SELECT id, title FROM projects WHERE id = ?", (project_id,))
    proj = cursor.fetchone()
    if not proj:
        conn.close()
        raise ValueError(f"Project {project_id} not found.")

    paper_title = proj["title"]

    # Get pages
    cursor.execute("SELECT page_number, text_content, section_headings FROM document_pages WHERE project_id = ? ORDER BY page_number ASC", (project_id,))
    pages = [dict(row) for row in cursor.fetchall()]

    if not pages:
        conn.close()
        raise ValueError(f"No document pages found for project {project_id}. Extraction required first.")

    # Call AI Provider
    raw_claims, provider_used = ai_provider.extract_claims(pages, paper_title)
    if not raw_claims:
        conn.close()
        raise ValueError("No source-grounded evidence claims could be extracted from this document.")

    # Clear previous claims for project
    cursor.execute("DELETE FROM claims WHERE project_id = ?", (project_id,))

    saved_claims = []
    for c in raw_claims:
        exact_quote = str(c.get("exact_quote") or "").strip()
        if not exact_quote:
            continue
        claim_uuid = f"clm-{uuid.uuid4().hex[:8]}"
        claim_id_code = c.get("claim_id", f"CLM-{len(saved_claims)+1:02d}")
        # Keep the published sentence itself as the claim; model paraphrases can
        # add causality or certainty that the cited sentence does not support.
        claim_text = exact_quote
        page_num = int(c.get("page_number", 1))
        sec = c.get("section_heading", "Results")
        page_text = next((p["text_content"] for p in pages if p["page_number"] == page_num), "")
        def source_value(field: str) -> str:
            value = str(c.get(field) or "").strip()
            return value if value and value.casefold() in page_text.casefold() else ""
        study_type = source_value("study_type")
        population = source_value("population")
        sample_size = source_value("sample_size")
        outcome = source_value("outcome_measured")
        num_res = source_value("numerical_result")
        units = source_value("units")
        conditions = source_value("study_conditions")
        limitations = source_value("limitations")
        uncertainty = source_value("uncertainty")
        status = "Pending Verification"

        cursor.execute("""
        INSERT INTO claims (
            id, project_id, claim_id, claim_text, exact_quote, page_number,
            section_heading, study_type, population, sample_size, outcome_measured,
            numerical_result, units, study_conditions, limitations, uncertainty,
            evidence_status, review_status, review_notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending Review', ?)
        """, (
            claim_uuid, project_id, claim_id_code, claim_text, exact_quote, page_num,
            sec, study_type, population, sample_size, outcome,
            num_res, units, conditions, limitations, uncertainty,
            status, f"Extracted via {provider_used}"
        ))

        saved_claims.append({
            "id": claim_uuid,
            "claim_id": claim_id_code,
            "claim_text": claim_text,
            "exact_quote": exact_quote,
            "page_number": page_num,
            "section_heading": sec,
            "numerical_result": num_res,
            "sample_size": sample_size,
            "evidence_status": status,
            "review_status": "Pending Review"
        })

    if not saved_claims:
        conn.close()
        raise ValueError("The extractor returned no claims with exact source quotations.")

    # Claims are the source for all generated content. Invalidate project-scoped
    # derivatives so an older script, reel, carousel, or deck cannot outlive a
    # refreshed evidence ledger.
    cursor.execute("DELETE FROM reel_scenes WHERE project_id = ?", (project_id,))
    cursor.execute(
        "DELETE FROM assets WHERE project_id = ? AND asset_type IN "
        "('carousel', 'post', 'reel_professional', 'reel_everyday', "
        "'reel_localvoice', 'reel_inside_body', 'pptx')",
        (project_id,),
    )

    conn.commit()
    conn.close()

    return {
        "project_id": project_id,
        "total_claims": len(saved_claims),
        "provider_used": provider_used,
        "claims": saved_claims
    }
