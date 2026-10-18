import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import pymupdf  # PyMuPDF

class PDFExtractionService:
    @staticmethod
    def extract_pdf(file_path: Path) -> Dict[str, Any]:
        """
        Extracts structured text, page numbers, sections, and metadata from a PDF.
        Detects scanned pages with no extractable text.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found at: {file_path}")

        doc = pymupdf.open(str(file_path))
        page_count = len(doc)
        
        pages_data: List[Dict[str, Any]] = []
        total_text_length = 0
        all_text = ""

        # Metadata from PDF properties
        doc_meta = doc.metadata or {}
        extracted_meta = {
            "pdf_title": doc_meta.get("title", "").strip() or None,
            "pdf_author": doc_meta.get("author", "").strip() or None,
            "pdf_subject": doc_meta.get("subject", "").strip() or None,
            "page_count": page_count,
        }

        # Page-by-page extraction
        for page_idx in range(page_count):
            page = doc[page_idx]
            page_num = page_idx + 1
            page_text = page.get_text("text").strip()
            total_text_length += len(page_text)
            all_text += f"\n--- [Page {page_num}] ---\n" + page_text

            # Extract text blocks with bounding boxes and font sizes to detect headings
            blocks = page.get_text("blocks")
            detected_sections = []
            
            for b in blocks:
                block_text = b[4].strip()
                # Check for common academic section headers
                if re.match(r"^(Abstract|Introduction|Methods|Methodology|Results|Discussion|Conclusion|Limitations|References)\b", block_text, re.IGNORECASE):
                    detected_sections.append(block_text.split("\n")[0])

            pages_data.append({
                "page_number": page_num,
                "text": page_text,
                "detected_sections": detected_sections,
                "char_count": len(page_text)
            })

        doc.close()

        # Check for scanned PDF with zero or negligible text
        if total_text_length < 100 and page_count > 0:
            raise ValueError(
                "This PDF appears to be a scanned image with no embedded digital text. "
                "OCR processing is required to extract text from scanned documents."
            )

        # Basic metadata heuristics from text
        first_page_text = pages_data[0]["text"] if pages_data else ""
        doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", all_text)
        year_match = re.search(r"\b(19\d\d|20\d\d)\b", first_page_text)
        
        # Look for Abstract
        abstract = ""
        abs_match = re.search(r"Abstract[:\s\n]+(.*?)(?=\n\s*(?:Introduction|Keywords|Background|Methods|1\.|\n\n\n))", all_text, re.DOTALL | re.IGNORECASE)
        if abs_match:
            abstract = abs_match.group(1).strip()
            if len(abstract) > 1500:
                abstract = abstract[:1500] + "..."

        title = extracted_meta["pdf_title"]
        if not title:
            # First significant line on page 1
            lines = [l.strip() for l in first_page_text.split("\n") if len(l.strip()) > 15]
            if lines:
                title = lines[0]
            else:
                title = file_path.stem.replace("_", " ").title()

        return {
            "title": title,
            "authors": [extracted_meta["pdf_author"]] if extracted_meta["pdf_author"] else [],
            "year": int(year_match.group(1)) if year_match else None,
            "doi": doi_match.group(0) if doi_match else None,
            "abstract": abstract if abstract else None,
            "page_count": page_count,
            "pages": pages_data,
            "full_text": all_text
        }
