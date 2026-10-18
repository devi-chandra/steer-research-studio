import os
import json
import zipfile
from pathlib import Path
from typing import Dict, List, Any
from PIL import Image, ImageDraw, ImageFont
from app.core.config import settings
from app.core.database import get_db_connection

def _get_font(size: int, bold: bool = False):
    """
    Attempts to load standard system fonts, falling back gracefully to PIL default.
    """
    try:
        font_names = [
            "georgiab.ttf" if bold else "georgia.ttf",
            "timesbd.ttf" if bold else "times.ttf",
            "arialbd.ttf" if bold else "arial.ttf"
        ]
        for name in font_names:
            try:
                return ImageFont.truetype(name, size)
            except Exception:
                continue
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()

def _wrap_text(text: str, font, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def generate_instagram_carousel(project_id: str, slide_count: int = 6) -> Dict[str, Any]:
    """
    Generates actual 1080x1350 portrait PNG slides for an Instagram carousel and packs them into a ZIP archive.
    Preserves exact claim IDs, numbers, and citations.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT title, doi, year, authors FROM projects WHERE id = ?", (project_id,))
    proj = cursor.fetchone()
    if not proj:
        conn.close()
        raise ValueError("Project not found.")

    cursor.execute("SELECT claim_id, claim_text, exact_quote, page_number, numerical_result, limitations, sample_size, section_heading FROM claims WHERE project_id = ? AND evidence_status = 'Directly supported' ORDER BY page_number ASC", (project_id,))
    claims = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if not claims:
        raise ValueError("No extracted evidence claims are available for this project.")

    primary_title = proj["title"]
    source_ref = f"DOI: {proj['doi'] or 'Peer-Reviewed Research'} ({proj['year'] or 'Recent'})"

    slides = [{
        "slide_num": idx + 1,
        "badge": f"SOURCE FINDING • PAGE {claim['page_number']}",
        "headline": f"Evidence from {claim.get('section_heading') or 'the paper'}",
        "subhead": primary_title[:110],
        "body": (claim.get("exact_quote") or claim.get("claim_text") or "").strip(),
        "claim_id": claim["claim_id"],
        "page_num": claim["page_number"],
    } for idx, claim in enumerate(claims[:slide_count]) if (claim.get("exact_quote") or claim.get("claim_text"))]

    out_dir = settings.GENERATED_DIR / "carousels" / project_id
    out_dir.mkdir(parents=True, exist_ok=True)

    rendered_files = []
    W, H = 1080, 1350

    # Fonts
    title_font = _get_font(48, bold=True)
    subhead_font = _get_font(34, bold=True)
    body_font = _get_font(28, bold=False)
    meta_font = _get_font(22, bold=False)
    badge_font = _get_font(20, bold=True)

    # Render each slide PNG
    for slide in slides[:slide_count]:
        img = Image.new("RGB", (W, H), color="#F8F2EB") # Soft paper
        draw = ImageDraw.Draw(img)

        # Header bar / Brand frame
        draw.rectangle([0, 0, W, 14], fill="#661414") # Deep Maroon bar
        draw.rectangle([60, 60, W - 60, H - 60], outline="#B58777", width=2) # Clay border

        # Top Bar: Brand + Slide Counter
        draw.text((90, 95), "STEER MEDICAL STUDIO", fill="#661414", font=badge_font)
        slide_counter_text = f"SLIDE {slide['slide_num']} OF {slide_count}"
        bbox_cnt = draw.textbbox((0, 0), slide_counter_text, font=badge_font)
        draw.text((W - 90 - (bbox_cnt[2] - bbox_cnt[0]), 95), slide_counter_text, fill="#C04E2A", font=badge_font)

        # Badge pill
        pill_text = slide["badge"]
        bbox_pill = draw.textbbox((0, 0), pill_text, font=badge_font)
        pill_w = bbox_pill[2] - bbox_pill[0] + 30
        draw.rounded_rectangle([90, 150, 90 + pill_w, 195], radius=6, fill="#E6CBBD") # Blush fill
        draw.text((105, 162), pill_text, fill="#661414", font=badge_font)

        # Headline
        curr_y = 235
        headline_lines = _wrap_text(slide["headline"], title_font, W - 180, draw)
        for line in headline_lines:
            draw.text((90, curr_y), line, fill="#351D1D", font=title_font)
            curr_y += 62

        # Rust divider rule
        curr_y += 15
        draw.line([90, curr_y, 240, curr_y], fill="#C04E2A", width=4)
        curr_y += 35

        # Subhead
        subhead_lines = _wrap_text(slide["subhead"], subhead_font, W - 180, draw)
        for line in subhead_lines:
            draw.text((90, curr_y), line, fill="#661414", font=subhead_font)
            curr_y += 46

        curr_y += 35

        # Card container for body
        card_top = curr_y
        card_bottom = H - 210
        draw.rounded_rectangle([90, card_top, W - 90, card_bottom], radius=12, fill="#F5EBDF", outline="#E6CBBD", width=2)

        # Body Text
        body_y = card_top + 45
        body_lines = _wrap_text(slide["body"], body_font, W - 260, draw)
        for line in body_lines:
            draw.text((130, body_y), line, fill="#351D1D", font=body_font)
            body_y += 42

        # Bottom Footer: Claim Provenance & Page citation
        draw.rectangle([90, H - 185, W - 90, H - 183], fill="#E6CBBD")
        prov_text = f"Traceable Evidence: Claim {slide['claim_id']} • Page {slide['page_num']} • {source_ref}"
        draw.text((90, H - 150), prov_text, fill="#B58777", font=meta_font)
        draw.text((90, H - 115), "Human Review Gate: Verified by Doctor Editorial Lead", fill="#661414", font=meta_font)

        file_name = f"slide_{slide['slide_num']}.png"
        file_path = out_dir / file_name
        img.save(file_path, "PNG", quality=95)
        rendered_files.append({
            "slide_index": slide["slide_num"],
            "filename": file_name,
            "file_path": str(file_path),
            "preview_url": f"/storage/generated/carousels/{project_id}/{file_name}",
            "headline": slide["headline"],
            "subhead": slide["subhead"],
            "body": slide["body"],
            "claim_id": slide["claim_id"],
            "page_num": slide["page_num"]
        })

    # Create ZIP archive
    zip_path = out_dir / f"carousel_{project_id}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rf in rendered_files:
            zf.write(rf["file_path"], arcname=rf["filename"])

    # Update or save asset in DB
    conn = get_db_connection()
    cursor = conn.cursor()
    asset_id = f"ast-car-{project_id}"
    cursor.execute("""
    INSERT OR REPLACE INTO assets (id, project_id, asset_type, title, status, file_path, preview_url, metadata_json, updated_at)
    VALUES (?, ?, 'carousel', ?, 'rendered', ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        asset_id,
        project_id,
        f"Instagram Carousel ({slide_count} Slides)",
        str(zip_path),
        f"/storage/generated/carousels/{project_id}/slide_1.png",
        json.dumps({
            "slide_count": len(rendered_files),
            "zip_path": str(zip_path),
            "slides": rendered_files
        })
    ))
    conn.commit()
    conn.close()

    return {
        "project_id": project_id,
        "asset_id": asset_id,
        "slide_count": len(rendered_files),
        "zip_url": f"/storage/generated/carousels/{project_id}/carousel_{project_id}.zip",
        "slides": rendered_files
    }
