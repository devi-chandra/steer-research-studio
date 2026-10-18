import re
import httpx
from typing import Dict, Any, List

class URLIngestionService:
    @staticmethod
    async def fetch_paper_from_url(url: str) -> Dict[str, Any]:
        """
        Fetches public research papers from web URLs (PubMed Central, open journals, preprint servers).
        Detects paywalls, access restrictions, or unsupported page formats.
        """
        if not url.startswith(("http://", "https://")):
            raise ValueError("Invalid URL format. Please provide a full URL starting with http:// or https://")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 SteerResearchBot/1.0"
        }

        try:
            async with httpx.AsyncClient(timeout=25.0, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 403 or response.status_code == 401:
                    raise PermissionError(
                        f"Access to this paper is restricted (HTTP {response.status_code}). "
                        "The publisher requires a subscription or institutional login. "
                        "Please download the paper PDF and upload it directly instead."
                    )
                elif response.status_code >= 400:
                    raise ValueError(f"Failed to fetch paper from URL. Server returned HTTP {response.status_code}.")

                html_content = response.text

        except httpx.TimeoutException:
            raise TimeoutError("Request timed out while connecting to the paper URL. Please try again or upload the PDF.")
        except httpx.RequestError as e:
            raise ConnectionError(f"Network error while connecting to URL: {str(e)}. Please upload the PDF instead.")

        # Check for common paywall markers in HTML
        paywall_signals = [
            "purchase access",
            "access through your institution",
            "institutional login",
            "subscribe to view",
            "buy this article",
            "paywall",
            "readcube.com/articles/purchase",
            "requires a subscription",
            "login to view full text"
        ]
        
        lower_html = html_content.lower()
        if any(signal in lower_html for signal in paywall_signals) and len(html_content) < 15000:
            raise PermissionError(
                "This paper appears to be behind a publisher paywall or requires institutional access. "
                "Steer Studio cannot bypass access controls. Please upload the PDF of the paper directly."
            )

        # Extract title from <title> or <h1>
        title_match = re.search(r"<h1[^>]*>(.*?)</h1>", html_content, re.IGNORECASE | re.DOTALL)
        if not title_match:
            title_match = re.search(r"<title[^>]*>(.*?)</title>", html_content, re.IGNORECASE | re.DOTALL)
        
        raw_title = title_match.group(1) if title_match else "Extracted Scientific Research"
        clean_title = re.sub(r"<[^>]+>", "", raw_title).strip()
        clean_title = re.sub(r"\s+", " ", clean_title)

        # Remove scripts and styles
        clean_html = re.sub(r"<script[^>]*>.*?</script>", " ", html_content, flags=re.DOTALL | re.IGNORECASE)
        clean_html = re.sub(r"<style[^>]*>.*?</style>", " ", clean_html, flags=re.DOTALL | re.IGNORECASE)
        
        # Extract abstract if available
        abstract = None
        abstract_match = re.search(r"(?:<section[^>]*class=[\"'][^\"']*abstract[^\"']*[\"'][^>]*>|<div[^>]*class=[\"'][^\"']*abstract[^\"']*[\"'][^>]*>)(.*?)(?:</section>|</div>)", clean_html, re.DOTALL | re.IGNORECASE)
        if abstract_match:
            abstract = re.sub(r"<[^>]+>", " ", abstract_match.group(1)).strip()
            abstract = re.sub(r"\s+", " ", abstract)

        # Extract clean text
        text = re.sub(r"<[^>]+>", " ", clean_html)
        text = re.sub(r"&nbsp;", " ", text)
        text = re.sub(r"&[a-z]+;", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        if len(text) < 300:
            raise ValueError(
                "The web page contains insufficient research text. "
                "The content might be rendered dynamically by JavaScript or protected. "
                "Please upload the paper PDF instead."
            )

        # Split into synthetic pages (approx 2500 characters per page)
        chunk_size = 2500
        pages: List[Dict[str, Any]] = []
        page_chunks = [text[i:i+chunk_size] for i in range(0, min(len(text), 25000), chunk_size)]
        
        for idx, chunk in enumerate(page_chunks):
            pages.append({
                "page_number": idx + 1,
                "text": chunk,
                "detected_sections": ["Web Article Extract"],
                "char_count": len(chunk)
            })

        return {
            "title": clean_title,
            "authors": [],
            "year": None,
            "doi": None,
            "abstract": abstract[:1200] if abstract else None,
            "page_count": len(pages),
            "pages": pages,
            "full_text": text[:25000],
            "source_url": url
        }
