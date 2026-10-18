from pathlib import Path
from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont

class StaticPostRenderer:
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
        font_names = []
        if font_type == "serif_bold":
            font_names = ["georgiab.ttf", "timesbd.ttf", "palab.ttf", "arialbd.ttf"]
        elif font_type == "serif":
            font_names = ["georgia.ttf", "times.ttf", "pala.ttf", "arial.ttf"]
        elif font_type == "sans_bold":
            font_names = ["segoeuib.ttf", "arialbd.ttf", "calibrib.ttf"]
        else:
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

    def render_static_post(self, post_data: Dict[str, Any], output_path: Path) -> Path:
        """Renders finished 1080x1350 static Instagram post PNG"""
        img = Image.new("RGB", (self.width, self.height), color=self.c_cream)
        draw = ImageDraw.Draw(img)

        # Outer framing
        frame_pad = 48
        draw.rounded_rectangle(
            [frame_pad, frame_pad, self.width - frame_pad, self.height - frame_pad],
            radius=32,
            outline=self.c_blush,
            width=2,
            fill=self.c_soft_paper
        )

        # Header Badge
        header_y = 90
        badge_text = post_data.get("badge") or "DOCTOR-LED METABOLIC HEALTH"
        font_badge = self._get_font("sans_bold", 24)
        draw.rounded_rectangle([90, header_y, 490, header_y + 48], radius=24, fill=self.c_blush)
        draw.text((115, header_y + 10), badge_text.upper(), font=font_badge, fill=self.c_maroon)

        # Eyebrow
        eyebrow = post_data.get("eyebrow", "CLINICAL RESEARCH INSIGHT").upper()
        font_eyebrow = self._get_font("sans_bold", 28)
        draw.text((90, 195), eyebrow, font=font_eyebrow, fill=self.c_rust)

        # Main Headline
        headline = post_data.get("headline", "Metabolic Health Finding")
        font_headline = self._get_font("serif_bold", 66)
        headline_lines = self._wrap_text(headline, font_headline, self.width - 180, draw)
        
        cur_y = 250
        for line in headline_lines:
            draw.text((90, cur_y), line, font=font_headline, fill=self.c_ink)
            cur_y += 82

        cur_y += 35

        # Horizontal accent line
        draw.line([90, cur_y, 350, cur_y], fill=self.c_rust, width=4)
        cur_y += 45

        # Body copy
        body_copy = post_data.get("body_copy", "")
        font_body = self._get_font("serif", 40)
        body_lines = self._wrap_text(body_copy, font_body, self.width - 180, draw)
        for line in body_lines:
            draw.text((90, cur_y), line, font=font_body, fill=self.c_ink)
            cur_y += 56

        cur_y += 50

        # Practical Takeaway Highlight Box
        takeaway = post_data.get("practical_takeaway", "Take a 10-minute post-meal stroll tonight.")
        box_top = cur_y
        box_bottom = min(cur_y + 200, 1160)
        draw.rounded_rectangle([90, box_top, self.width - 90, box_bottom], radius=22, fill=self.c_cream, outline=self.c_clay, width=2)

        font_tk_hdr = self._get_font("sans_bold", 26)
        font_tk_body = self._get_font("sans", 32)
        
        draw.text((125, box_top + 28), "STEER CLINICAL ACTION", font=font_tk_hdr, fill=self.c_rust)
        tk_lines = self._wrap_text(takeaway, font_tk_body, self.width - 250, draw)
        tk_y = box_top + 72
        for line in tk_lines[:3]:
            draw.text((125, tk_y), line, font=font_tk_body, fill=self.c_ink)
            tk_y += 42

        # Footer
        footer_y = self.height - 120
        draw.line([90, footer_y, self.width - 90, footer_y], fill=self.c_blush, width=2)

        font_footer = self._get_font("sans", 24)
        citation = post_data.get("source_citation") or "Steer Metabolic Health Club Protocol"
        clms = " • ".join(post_data.get("claim_ids", []))
        if clms:
            citation += f" [{clms}]"
        
        draw.text((90, footer_y + 16), citation[:80], font=font_footer, fill=self.c_clay)
        draw.text((self.width - 260, footer_y + 16), "steerhealth.in", font=font_footer, fill=self.c_rust)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(output_path), "PNG", quality=95)
        return output_path

static_post_renderer = StaticPostRenderer()
