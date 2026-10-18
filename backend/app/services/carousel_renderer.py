import os
import zipfile
from pathlib import Path
from typing import List, Dict, Any
from PIL import Image, ImageDraw, ImageFont
from app.core.config import settings

class CarouselRenderer:
    def __init__(self):
        self.width = 1080
        self.height = 1350
        
        # Steer Brand Palette
        self.c_cream = "#F5EBDF"
        self.c_rust = "#C04E2A"
        self.c_maroon = "#661414"
        self.c_ink = "#351D1D"
        self.c_clay = "#B58777"
        self.c_blush = "#E6CBBD"
        self.c_soft_paper = "#F8F2EB"

    def _get_font(self, font_type: str, size: int) -> ImageFont.ImageFont:
        """Returns TrueType font with robust cross-platform fallbacks"""
        font_names = []
        if font_type == "serif_bold":
            font_names = ["georgiab.ttf", "timesbd.ttf", "palab.ttf", "arialbd.ttf"]
        elif font_type == "serif":
            font_names = ["georgia.ttf", "times.ttf", "pala.ttf", "arial.ttf"]
        elif font_type == "sans_bold":
            font_names = ["segoeuib.ttf", "arialbd.ttf", "calibrib.ttf"]
        else:  # sans
            font_names = ["segoeui.ttf", "arial.ttf", "calibri.ttf"]

        for name in font_names:
            try:
                return ImageFont.truetype(name, size)
            except Exception:
                continue
        return ImageFont.load_default()

    def _wrap_text(self, text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_w = bbox[2] - bbox[0]
            if line_w <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        if current_line:
            lines.append(" ".join(current_line))
        return lines

    def render_slide(self, slide_data: Dict[str, Any], total_slides: int, output_path: Path) -> Path:
        """Renders an individual 1080x1350 Instagram carousel slide"""
        img = Image.new("RGB", (self.width, self.height), color=self.c_cream)
        draw = ImageDraw.Draw(img)

        # Subtle elegant inner border / soft frame
        frame_pad = 40
        draw.rounded_rectangle(
            [frame_pad, frame_pad, self.width - frame_pad, self.height - frame_pad],
            radius=28,
            outline=self.c_blush,
            width=2,
            fill=self.c_soft_paper
        )

        # Header bar: Steer Club Badge and Slide Number
        header_y = 75
        slide_num = slide_data.get("slide_number", 1)
        
        font_badge = self._get_font("sans_bold", 24)
        font_slide_counter = self._get_font("sans_bold", 26)

        # Steer badge
        draw.rounded_rectangle([75, header_y, 340, header_y + 44], radius=22, fill=self.c_blush)
        draw.text((95, header_y + 8), "STEER CLINICAL", font=font_badge, fill=self.c_maroon)

        # Slide counter (e.g., "02 / 06")
        counter_text = f"{slide_num:02d} / {total_slides:02d}"
        draw.text((self.width - 180, header_y + 8), counter_text, font=font_slide_counter, fill=self.c_clay)

        # Eyebrow tag
        eyebrow = slide_data.get("eyebrow", "METABOLIC SCIENCE").upper()
        font_eyebrow = self._get_font("sans_bold", 28)
        draw.text((75, 175), eyebrow, font=font_eyebrow, fill=self.c_rust)

        # Headline
        headline = slide_data.get("headline", "Clinical Metabolic Finding")
        font_headline = self._get_font("serif_bold", 62)
        headline_lines = self._wrap_text(headline, font_headline, self.width - 150, draw)
        
        cur_y = 225
        for line in headline_lines:
            draw.text((75, cur_y), line, font=font_headline, fill=self.c_ink)
            cur_y += 76

        cur_y += 25

        # Key Stat Callout Box (if available)
        key_stat = slide_data.get("key_stat")
        stat_label = slide_data.get("stat_label")
        if key_stat:
            box_top = cur_y
            box_bottom = box_top + 150
            draw.rounded_rectangle([75, box_top, self.width - 75, box_bottom], radius=20, fill=self.c_cream, outline=self.c_clay, width=2)
            
            font_stat = self._get_font("serif_bold", 72)
            font_stat_lbl = self._get_font("sans_bold", 28)
            
            draw.text((105, box_top + 28), str(key_stat), font=font_stat, fill=self.c_rust)
            if stat_label:
                lbl_lines = self._wrap_text(stat_label, font_stat_lbl, 550, draw)
                lbl_y = box_top + 40
                for lbl_line in lbl_lines:
                    draw.text((360, lbl_y), lbl_line, font=font_stat_lbl, fill=self.c_ink)
                    lbl_y += 36
            
            cur_y = box_bottom + 35

        # Body text
        body_text = slide_data.get("body_text", "")
        font_body = self._get_font("serif", 36)
        body_lines = self._wrap_text(body_text, font_body, self.width - 150, draw)
        for line in body_lines:
            draw.text((75, cur_y), line, font=font_body, fill=self.c_ink)
            cur_y += 48

        cur_y += 35

        # Practical Tip Card
        tip_text = slide_data.get("practical_tip")
        if tip_text and cur_y < 1100:
            tip_top = cur_y
            tip_bottom = min(cur_y + 115, 1140)
            draw.rounded_rectangle([75, tip_top, self.width - 75, tip_bottom], radius=16, fill="#FFF9F4", outline=self.c_blush, width=2)
            
            font_tip_hdr = self._get_font("sans_bold", 22)
            font_tip_body = self._get_font("sans", 26)
            
            draw.text((105, tip_top + 16), "STEER CLINICAL PROTOCOL", font=font_tip_hdr, fill=self.c_rust)
            tip_lines = self._wrap_text(tip_text, font_tip_body, self.width - 210, draw)
            if tip_lines:
                draw.text((105, tip_top + 50), tip_lines[0], font=font_tip_body, fill=self.c_ink)

        # Footer divider and source citation
        footer_y = self.height - 130
        draw.line([75, footer_y, self.width - 75, footer_y], fill=self.c_blush, width=2)

        font_footer = self._get_font("sans", 22)
        citation = slide_data.get("source_citation") or "Doctor-led metabolic health research • Steer Health Club"
        clm_tags = " • ".join(slide_data.get("claim_ids", []))
        if clm_tags:
            citation += f" [{clm_tags}]"
        
        draw.text((75, footer_y + 18), citation[:85], font=font_footer, fill=self.c_clay)
        draw.text((self.width - 240, footer_y + 18), "steerhealth.in", font=font_footer, fill=self.c_rust)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(output_path), "PNG", quality=95)
        return output_path

    def render_carousel_deck(self, slides: List[Dict[str, Any]], project_dir: Path) -> Dict[str, Any]:
        """Renders all slides in the deck and generates a zip bundle"""
        slides_dir = project_dir / "carousel"
        slides_dir.mkdir(parents=True, exist_ok=True)
        
        slide_paths: List[Path] = []
        total = len(slides)

        for s in slides:
            s_num = s.get("slide_number", 1)
            file_name = f"slide_{s_num:02d}.png"
            file_path = slides_dir / file_name
            self.render_slide(s, total, file_path)
            slide_paths.append(file_path)

        # Generate ZIP bundle
        zip_path = project_dir / "carousel_slides.zip"
        with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zipf:
            for sp in slide_paths:
                zipf.write(str(sp), arcname=sp.name)

        return {
            "slide_count": total,
            "slide_files": [str(p) for p in slide_paths],
            "zip_file": str(zip_path)
        }

carousel_renderer = CarouselRenderer()
