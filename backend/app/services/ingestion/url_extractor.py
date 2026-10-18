import re
import httpx
from bs4 import BeautifulSoup
from app.core.security import is_safe_url
from app.core.database import get_db_connection

async def extract_url_document(url: str, project_id: str) -> dict:
    """
    Safely fetches and extracts research content from an accessible public web URL.
    Enforces SSRF prevention and provides honest error reporting.
    """
    safe, reason = is_safe_url(url)
    if not safe:
        raise ValueError(f"SSRF Security Violation: {reason}")

    headers = {
        "User-Agent": "SteerResearchBot/2.0 (+https://steer.health/bot; medical-research-parser)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    try:
        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                raise ValueError(f"Publisher server returned HTTP {response.status_code}. Content could not be retrieved.")

            html_content = response.text
    except httpx.TimeoutException:
        raise ValueError("Connection timed out while attempting to reach public research server.")
    except Exception as e:
        raise ValueError(f"Failed to fetch research URL: {str(e)}")

    soup = BeautifulSoup(html_content, "html.parser")

    # Remove script, style, nav, footer, ads
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "form"]):
        tag.decompose()

    # Extract title
    title = ""
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title["content"].strip()
    elif soup.title and soup.title.string:
        title = soup.title.string.strip()
    elif soup.find("h1"):
        title = soup.find("h1").get_text().strip()

    if not title:
        title = "Extracted Web Research Document"

    # Extract DOI if present
    doi = ""
    doi_meta = soup.find("meta", {"name": re.compile(r"dc\.identifier|citation_doi", re.I)})
    if doi_meta and doi_meta.get("content"):
        doi = doi_meta["content"].strip()
    else:
        doi_match = re.search(r'\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b', html_content, re.I)
        if doi_match:
            doi = doi_match.group(0)

    # Extract main body text
    body_container = soup.find("article") or soup.find("main") or soup.find("div", {"class": re.compile(r"article|content|body|abstract", re.I)}) or soup.body
    raw_text = body_container.get_text(separator="\n", strip=True) if body_container else soup.get_text(separator="\n", strip=True)

    # Split into clean paragraphs
    paragraphs = [p.strip() for p in raw_text.split('\n') if len(p.strip()) > 30]
    full_text = "\n\n".join(paragraphs)

    if len(full_text) < 100:
        raise ValueError("The target URL provided insufficient readable text or is behind a paywall/bot-blocker.")

    # Chunk into virtual pages of ~2000 chars to maintain consistent page citation architecture
    chunk_size = 2000
    virtual_pages = []
    start = 0
    page_num = 1
    while start < len(full_text):
        end = start + chunk_size
        chunk = full_text[start:end]
        virtual_pages.append({
            "page_number": page_num,
            "text_content": chunk,
            "char_count": len(chunk),
            "section_headings": f"Web Section {page_num}"
        })
        start = end
        page_num += 1

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM document_pages WHERE project_id = ?", (project_id,))

    for vp in virtual_pages:
        cursor.execute("""
        INSERT INTO document_pages (project_id, page_number, text_content, char_count, section_headings)
        VALUES (?, ?, ?, ?, ?)
        """, (project_id, vp["page_number"], vp["text_content"], vp["char_count"], vp["section_headings"]))

    cursor.execute("""
    UPDATE projects
    SET title = ?,
        doi = ?,
        extraction_status = 'extracted',
        metadata_verified = ?,
        limitation_notes = 'Extracted via public web article stream.'
    WHERE id = ?
    """, (title, doi, 1 if doi else 0, project_id))

    conn.commit()
    conn.close()

    return {
        "project_id": project_id,
        "total_pages": len(virtual_pages),
        "total_characters": len(full_text),
        "is_scanned": False,
        "detected_title": title,
        "detected_doi": doi,
        "pages": virtual_pages
    }
