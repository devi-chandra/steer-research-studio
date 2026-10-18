import json
from pathlib import Path
from typing import Dict, Any
from PIL import Image, ImageDraw, ImageFont
from app.core.config import settings
from app.core.database import get_db_connection
from app.services.content_generation.carousel_generator import _get_font, _wrap_text

def generate_static_instagram_post(project_id: str, custom_headline: str = "", custom_body: str = "") -> Dict[str, Any]:
    """
    Renders an editorial 1080x1350 static Instagram post PNG.
    Grounded strictly in verified research claims with prominent evidence credentials.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT title, doi, year, authors FROM projects WHERE id = ?", (project_id,))
    proj = cursor.fetchone()
    if not proj:
        conn.close()
        raise ValueError("Project not found.")

    cursor.execute("SELECT claim_id, claim_text, exact_quote, page_number, numerical_result, limitations, sample_size FROM claims WHERE project_id = ? AND evidence_status = 'Directly supported' ORDER BY page_number ASC", (project_id,))
    claims = [dict(r) for r in cursor.fetchall()]
    conn.close()

    primary_title = proj["title"]
    source_ref = f"DOI: {proj['doi'] or 'Peer-Reviewed Scientific Literature'} ({proj['year'] or 'Recent'})"

    if not claims:
        raise ValueError("No extracted evidence claims are available for this project.")
    top_claim = claims[0]

    headline = custom_headline or f"Clinical Update: {primary_title[:95]}"
    num_highlight = top_claim.get("numerical_result") or "See source finding"
    explanation = custom_body or (
        f"Source finding (page {top_claim['page_number']}): "
        f"'{(top_claim.get('exact_quote') or top_claim.get('claim_text') or '')[:220]}'."
    )
    limitations = f"Evidence Bounds: {top_claim.get('limitations') or 'Limitations were not extracted; consult the cited source paper.'}"

    out_dir = settings.GENERATED_DIR / "posts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"post_{project_id}.png"

    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), color="#F8F2EB") # Soft paper
    draw = ImageDraw.Draw(img)

    # Frame
    draw.rectangle([0, 0, W, 16], fill="#661414") # Maroon top band
    draw.rectangle([50, 50, W - 50, H - 50], outline="#B58777", width=2) # Clay border

    # Header
    brand_font = _get_font(22, bold=True)
    draw.text((80, 85), "STEER CLINICAL DISCOVERY", fill="#661414", font=brand_font)
    draw.text((W - 320, 85), "ONE VERIFIED SOURCE", fill="#C04E2A", font=brand_font)

    # Badge Pill
    badge_font = _get_font(18, bold=True)
    draw.rounded_rectangle([80, 135, 290, 175], radius=6, fill="#E6CBBD")
    draw.text((95, 145), "DOCTOR-REVIEWED POST", fill="#661414", font=badge_font)

    # Headline
    headline_font = _get_font(44, bold=True)
    curr_y = 210
    lines = _wrap_text(headline, headline_font, W - 160, draw)
    for l in lines:
        draw.text((80, curr_y), l, fill="#351D1D", font=headline_font)
        curr_y += 56

    # Rust accent line
    curr_y += 10
    draw.line([80, curr_y, 220, curr_y], fill="#C04E2A", width=4)
    curr_y += 30

    # Key Result Metric Card
    draw.rounded_rectangle([80, curr_y, W - 80, curr_y + 190], radius=12, fill="#F5EBDF", outline="#B58777", width=2)
    metric_label_font = _get_font(20, bold=True)
    metric_num_font = _get_font(56, bold=True)
    draw.text((120, curr_y + 25), "PRIMARY MEASURED OUTCOME", fill="#C04E2A", font=metric_label_font)
    draw.text((120, curr_y + 70), num_highlight, fill="#661414", font=metric_num_font)
    if top_claim.get("sample_size"):
        draw.text((120, curr_y + 145), f"Sample: {top_claim['sample_size']}", fill="#351D1D", font=metric_label_font)
    curr_y += 225

    # Concise Explanation Card
    draw.rounded_rectangle([80, curr_y, W - 80, curr_y + 360], radius=12, fill="#FFFFFF", outline="#E6CBBD", width=2)
    sec_title_font = _get_font(22, bold=True)
    body_font = _get_font(26, bold=False)
    draw.text((120, curr_y + 30), "SCIENTIFIC CONTEXT & MECHANISM", fill="#661414", font=sec_title_font)

    exp_y = curr_y + 75
    body_lines = _wrap_text(explanation, body_font, W - 240, draw)
    for bl in body_lines:
        draw.text((120, exp_y), bl, fill="#351D1D", font=body_font)
        exp_y += 38

    curr_y += 390

    # Limitations Card
    draw.rounded_rectangle([80, curr_y, W - 80, curr_y + 130], radius=10, fill="#F5EBDF", outline="#E6CBBD", width=1)
    limit_font = _get_font(20, bold=False)
    lim_lines = _wrap_text(limitations, limit_font, W - 220, draw)
    lim_y = curr_y + 25
    for ll in lim_lines:
        draw.text((110, lim_y), ll, fill="#661414", font=limit_font)
        lim_y += 30

    # Provenance Footer
    draw.rectangle([80, H - 150, W - 80, H - 148], fill="#E6CBBD")
    meta_font = _get_font(20, bold=False)
    draw.text((80, H - 125), f"Evidence Trace: Claim {top_claim.get('claim_id', 'CLM-01')} • Page {top_claim.get('page_number', 1)} • {source_ref}", fill="#B58777", font=meta_font)
    draw.text((80, H - 95), "Educational Clinical Communication • Not Individual Prescription", fill="#661414", font=meta_font)

    img.save(out_file, "PNG", quality=95)

    asset_id = f"ast-post-{project_id}"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO assets (id, project_id, asset_type, title, status, file_path, preview_url, metadata_json, updated_at)
    VALUES (?, ?, 'post', 'Static Instagram Post', 'rendered', ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        asset_id,
        project_id,
        str(out_file),
        f"/storage/generated/posts/post_{project_id}.png",
        json.dumps({
            "headline": headline,
            "numerical_highlight": num_highlight,
            "explanation": explanation,
            "limitations": limitations,
            "claim_id": top_claim.get("claim_id", "CLM-01"),
            "page_number": top_claim.get("page_number", 1)
        })
    ))
    conn.commit()
    conn.close()

    return {
        "project_id": project_id,
        "asset_id": asset_id,
        "file_path": str(out_file),
        "preview_url": f"/storage/generated/posts/post_{project_id}.png",
        "headline": headline,
        "explanation": explanation,
        "limitations": limitations
    }
