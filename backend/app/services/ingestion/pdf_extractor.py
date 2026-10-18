import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import pymupdf as fitz
from app.core.database import get_db_connection

def extract_pdf_document(file_path: Path, project_id: str) -> Dict[str, Any]:
    """
    Extracts text, page boundaries, headings, and metadata from a scientific PDF.
    Detects scanned documents when OCR is needed.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found at {file_path}")

    doc = fitz.open(str(file_path))
    total_pages = len(doc)
    
    pages_data = []
    total_chars = 0
    detected_title = ""
    detected_authors = ""
    detected_doi = ""
    detected_year = ""
    section_headings_list = []

    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear any old pages for this project
    cursor.execute("DELETE FROM document_pages WHERE project_id = ?", (project_id,))

    for page_idx in range(total_pages):
        page = doc[page_idx]
        page_num = page_idx + 1
        page_text = page.get_text("text") or ""
        total_chars += len(page_text.strip())

        # Extract headings using font size blocks if available
        headings = []
        try:
            blocks = page.get_text("dict").get("blocks", [])
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            size = span.get("size", 10)
                            text_span = span.get("text", "").strip()
                            if size >= 13 and len(text_span) > 3 and not text_span.isdigit():
                                if text_span not in headings:
                                    headings.append(text_span)
        except Exception:
            pass

        # Heuristic fallback for headings
        if not headings:
            for line in page_text.split('\n')[:8]:
                l_strip = line.strip()
                if l_strip.isupper() and 4 < len(l_strip) < 50:
                    headings.append(l_strip)

        heading_str = " | ".join(headings[:4]) if headings else "General Content"
        if heading_str != "General Content":
            section_headings_list.extend(headings[:2])

        # Heuristic metadata extraction from first page
        if page_idx == 0:
            lines = [l.strip() for l in page_text.split('\n') if l.strip()]
            # Article titles are often the largest first-page text blocks, while
            # journal/date headers appear earlier in reading order.
            title_lines = []
            try:
                for block in page.get_text("dict").get("blocks", []):
                    for line in block.get("lines", []):
                        spans = line.get("spans", [])
                        line_value = " ".join(s.get("text", "").strip() for s in spans).strip()
                        max_size = max((s.get("size", 0) for s in spans), default=0)
                        if max_size >= 13 and 20 <= len(line_value) <= 240:
                            title_lines.append((line.get("bbox", [0, 0, 0, 0])[1], line_value))
            except Exception:
                title_lines = []
            if title_lines:
                detected_title = " ".join(value for _, value in sorted(title_lines)[:3])
                detected_title = re.sub(r"[\s\u00a0\u2000-\u200b]+", " ", detected_title).replace("\ufffd", " ").strip()
            if lines:
                # Potential title is usually the first non-trivial line
                if not detected_title:
                    for l in lines[:8]:
                        if len(l) > 20 and not re.match(r'^(http|www|vol|issn|doi|page|european journal|nature medicine)', l, re.I):
                            detected_title = l
                            break
            # DOI detection
            doi_match = re.search(r'\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b', page_text, re.IGNORECASE)
            if doi_match:
                detected_doi = doi_match.group(0)

            # Year detection
            year_match = re.search(r'\b(19\d{2}|20\d{2})\b', page_text)
            if year_match:
                detected_year = year_match.group(1)

        # Store page record
        cursor.execute("""
        INSERT INTO document_pages (project_id, page_number, text_content, char_count, section_headings)
        VALUES (?, ?, ?, ?, ?)
        """, (project_id, page_num, page_text, len(page_text), heading_str))

        pages_data.append({
            "page_number": page_num,
            "text_content": page_text,
            "char_count": len(page_text),
            "section_headings": heading_str
        })

    is_scanned = total_chars < 150 and total_pages > 0
    limitation_notes = "Document appears to be scanned or contains image-only pages; OCR may be required." if is_scanned else ""

    # Fallback title if none found
    if not detected_title:
        detected_title = file_path.stem.replace('_', ' ').replace('-', ' ').title()

    # Update project record
    cursor.execute("""
    UPDATE projects
    SET title = COALESCE(NULLIF(?, ''), title),
        doi = COALESCE(NULLIF(?, ''), doi),
        year = COALESCE(NULLIF(?, ''), year),
        extraction_status = ?,
        metadata_verified = ?,
        limitation_notes = ?
    WHERE id = ?
    """, (
        detected_title,
        detected_doi,
        detected_year,
        "extracted" if not is_scanned else "scanned_needs_ocr",
        1 if detected_doi else 0,
        limitation_notes,
        project_id
    ))

    conn.commit()
    conn.close()
    doc.close()

    return {
        "project_id": project_id,
        "total_pages": total_pages,
        "total_characters": total_chars,
        "is_scanned": is_scanned,
        "detected_title": detected_title,
        "detected_doi": detected_doi,
        "detected_year": detected_year,
        "headings": list(set(section_headings_list))[:6],
        "pages": pages_data
    }
