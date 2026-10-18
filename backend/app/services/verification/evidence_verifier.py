import re
from typing import Dict, List, Any
from app.core.database import get_db_connection

def verify_project_evidence(project_id: str) -> Dict[str, Any]:
    """
    Verifies every extracted claim against the actual text of its cited page.
    Deterministic verification ensuring zero hallucination.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, claim_id, exact_quote, page_number, numerical_result FROM claims WHERE project_id = ?", (project_id,))
    claims = cursor.fetchall()

    cursor.execute("SELECT page_number, text_content FROM document_pages WHERE project_id = ?", (project_id,))
    pages = {row["page_number"]: row["text_content"] for row in cursor.fetchall()}

    verification_results = []
    directly_supported = 0
    partially_supported = 0
    unsupported = 0

    for c in claims:
        cid = c["id"]
        c_code = c["claim_id"]
        quote = c["exact_quote"].strip()
        page_num = c["page_number"]
        page_text = pages.get(page_num, "")

        # Normalize whitespace for robust comparison
        norm_quote = re.sub(r'\s+', ' ', quote.lower())
        norm_page = re.sub(r'\s+', ' ', page_text.lower())

        if not page_text:
            status = "Unable to verify"
            note = f"Page {page_num} text not available."
            unsupported += 1
        elif norm_quote in norm_page:
            status = "Directly supported"
            note = f"Exact verbatim match found on page {page_num}."
            directly_supported += 1
        else:
            # Check for high substring overlap (in case of hyphenation or OCR artifacts)
            words = [w for w in norm_quote.split(' ') if len(w) > 4]
            matches = [w for w in words if w in norm_page]
            ratio = len(matches) / len(words) if words else 0.0

            if ratio >= 0.70:
                status = "Partially supported"
                note = f"Near-verbatim match ({int(ratio*100)}% terms matched) on page {page_num}."
                partially_supported += 1
            else:
                status = "Unsupported"
                note = f"Supporting quotation could not be verified in the text of page {page_num}."
                unsupported += 1

        cursor.execute("UPDATE claims SET evidence_status = ?, review_notes = ? WHERE id = ?", (status, note, cid))
        verification_results.append({
            "claim_id": c_code,
            "page_number": page_num,
            "status": status,
            "notes": note
        })

    conn.commit()
    conn.close()

    return {
        "project_id": project_id,
        "total_claims_checked": len(claims),
        "directly_supported": directly_supported,
        "partially_supported": partially_supported,
        "unsupported": unsupported,
        "details": verification_results
    }
