import math
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def render_sample_talking_character(out_dir: Path, total_frames: int = 48):
    out_dir.mkdir(parents=True, exist_ok=True)
    w, h = 720, 1280  # 9:16 vertical
    font_path = "C:/Windows/Fonts/Nirmala.ttc"
    
    font_title = ImageFont.truetype(font_path, 32)
    font_sub = ImageFont.truetype(font_path, 28)
    font_badge = ImageFont.truetype(font_path, 20)

    for i in range(total_frames):
        p = i / total_frames
        im = Image.new("RGB", (w, h), (245, 235, 223))  # Steer Cream
        draw = ImageDraw.Draw(im)

        # Background card
        draw.rounded_rectangle([30, 60, w - 30, h - 60], radius=30, fill=(248, 242, 235), outline=(230, 203, 189), width=3)

        # Top progress bar
        draw.rounded_rectangle([60, 90, w - 60, 98], radius=4, fill=(230, 203, 189))
        draw.rounded_rectangle([60, 90, int(60 + (w - 120) * p), 98], radius=4, fill=(192, 78, 42))

        # Badge
        draw.rounded_rectangle([60, 120, 360, 160], radius=20, fill=(230, 203, 189))
        draw.text((80, 128), "STEER EVERYDAY REEL", font=font_badge, fill=(102, 20, 20))

        # On-screen Hook
        draw.text((60, 190), "Feeling lazy after dinner?", font=font_title, fill=(53, 29, 29))

        # Character Center Position with gentle bobbing
        bob_y = int(8 * math.sin(2 * math.pi * i / 18))
        cx, cy = w // 2, 540 + bob_y

        # Character Body (Friendly Orange / Amla Fruit)
        body_r = 150
        draw.ellipse([cx - body_r, cy - body_r, cx + body_r, cy + body_r], fill=(225, 110, 50), outline=(192, 78, 42), width=6)
        
        # Leaf / Stem
        stem_sway = int(4 * math.sin(2 * math.pi * i / 18))
        draw.polygon([(cx, cy - body_r), (cx + 20 + stem_sway, cy - body_r - 40), (cx + 50 + stem_sway, cy - body_r - 20)], fill=(76, 175, 80))

        # Cute rosy cheeks
        draw.ellipse([cx - 100, cy + 20, cx - 60, cy + 50], fill=(240, 150, 130))
        draw.ellipse([cx + 60, cy + 20, cx + 100, cy + 50], fill=(240, 150, 130))

        # Eyes with natural blinking
        is_blinking = (i % 30) in [0, 1]
        eye_y = cy - 30
        if is_blinking:
            draw.line([cx - 70, eye_y, cx - 30, eye_y], fill=(53, 29, 29), width=5)
            draw.line([cx + 30, eye_y, cx + 70, eye_y], fill=(53, 29, 29), width=5)
        else:
            draw.ellipse([cx - 65, eye_y - 25, cx - 35, eye_y + 15], fill=(53, 29, 29))
            draw.ellipse([cx + 35, eye_y - 25, cx + 65, eye_y + 15], fill=(53, 29, 29))
            # Eye highlights
            draw.ellipse([cx - 60, eye_y - 20, cx - 45, eye_y - 5], fill=(255, 255, 255))
            draw.ellipse([cx + 40, eye_y - 20, cx + 55, eye_y - 5], fill=(255, 255, 255))

        # Eyebrows
        eyebrow_y = eye_y - 42
        draw.arc([cx - 75, eyebrow_y, cx - 25, eyebrow_y + 20], start=190, end=350, fill=(53, 29, 29), width=4)
        draw.arc([cx + 25, eyebrow_y, cx + 75, eyebrow_y + 20], start=190, end=350, fill=(53, 29, 29), width=4)

        # Mouth (Cycles between phoneme mouth shapes while speaking)
        mouth_cycle = (i // 3) % 4
        mouth_y = cy + 45
        if mouth_cycle == 0:
            # Closed smile
            draw.arc([cx - 40, mouth_y - 20, cx + 40, mouth_y + 20], start=20, end=160, fill=(53, 29, 29), width=6)
        elif mouth_cycle == 1:
            # Medium open "Ah"
            draw.ellipse([cx - 30, mouth_y - 15, cx + 30, mouth_y + 25], fill=(120, 30, 30), outline=(53, 29, 29), width=4)
            draw.ellipse([cx - 18, mouth_y + 5, cx + 18, mouth_y + 22], fill=(240, 100, 100)) # tongue
        elif mouth_cycle == 2:
            # Wide open "Oh"
            draw.ellipse([cx - 38, mouth_y - 18, cx + 38, mouth_y + 35], fill=(120, 30, 30), outline=(53, 29, 29), width=4)
            draw.ellipse([cx - 22, mouth_y + 10, cx + 22, mouth_y + 30], fill=(240, 100, 100))
        else:
            # Small "Oo"
            draw.ellipse([cx - 18, mouth_y - 10, cx + 18, mouth_y + 20], fill=(120, 30, 30), outline=(53, 29, 29), width=4)

        # Gesturing hand holding an animated indicator
        hand_x = cx + body_r - 20
        hand_y = cy + 30 + int(6 * math.sin(2 * math.pi * i / 14))
        draw.ellipse([hand_x, hand_y, hand_x + 50, hand_y + 50], fill=(225, 110, 50), outline=(192, 78, 42), width=4)
        
        # Speech bubble
        sb_top = cy + body_r + 40
        draw.rounded_rectangle([70, sb_top, w - 70, sb_top + 130], radius=18, fill=(255, 255, 255), outline=(230, 203, 189), width=2)
        draw.text((100, sb_top + 30), "That heavy sluggish feeling...", font=font_sub, fill=(53, 29, 29))
        draw.text((100, sb_top + 70), "is your blood sugar spiking!", font=font_sub, fill=(192, 78, 42))

        # Bottom Subtitle Safe Zone
        draw.rounded_rectangle([60, h - 210, w - 60, h - 110], radius=16, fill=(53, 29, 29))
        sub_text = "Ever felt super lazy right after dinner?"
        bbox = draw.textbbox((0, 0), sub_text, font=font_sub)
        draw.text(((w - (bbox[2] - bbox[0])) // 2, h - 175), sub_text, font=font_sub, fill=(255, 255, 255))

        im.save(out_dir / f"frame_{i:04d}.png")

    print(f"Rendered {total_frames} animated talking character frames!")

if __name__ == '__main__':
    render_sample_talking_character(Path("scratch_talking_char_frames"))
