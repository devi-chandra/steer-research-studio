"""
Character & Scene Animation Engine for Steer Scheme 2 Everyday Mode Reels.
Programmatically renders expressive 2D cartoon characters, animated faces,
viseme mouth talk cycles, eye blinks, squash-and-stretch physics, props,
and thematic backgrounds for:
1. Talking Fruits & Food Characters (Interactive Manny the Mango & Appu Apple Duo)
2. Inside Your Body (Happy Heart, Brainy Neuron, Glowy Glucose, Capillary Flow)
3. Clean Infographic (Animated Metric Bar Charts, Moving Diagrams, Evidence Network)
4. Colourful Cartoon (Joyful animated cartoon environment with stars and sparkles)
5. Relatable Human Situations (Techie Raj, Active Maya, Sleepy Sam)
"""

import functools
import math
from typing import Dict, Any, Tuple, Optional, List
from PIL import Image, ImageDraw, ImageFont

@functools.lru_cache(maxsize=32)
def _get_font(size: int, bold: bool = False):
    font_names = [
        "georgiab.ttf" if bold else "georgia.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
        "segoeuib.ttf" if bold else "segoeui.ttf",
        "C:/Windows/Fonts/NirmalaB.ttf" if bold else "C:/Windows/Fonts/Nirmala.ttc",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"
    ]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()

# ---------------------------------------------------------------------------
# Easing & Motion Functions for Organic Motion Graphics
# ---------------------------------------------------------------------------

def ease_out_back(t: float, s: float = 1.70158) -> float:
    """Overshoot and settle back easing, ideal for bouncy pop-ins."""
    t = max(0.0, min(1.0, t))
    t = t - 1.0
    return t * t * ((s + 1.0) * t + s) + 1.0

def ease_in_out_cubic(t: float) -> float:
    """Smooth S-curve acceleration and deceleration."""
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return 4.0 * t * t * t
    else:
        return 1.0 - math.pow(-2.0 * t + 2.0, 3) / 2.0

def ease_out_cubic(t: float) -> float:
    """Fast initial movement with smooth gentle deceleration."""
    t = max(0.0, min(1.0, t))
    return 1.0 - math.pow(1.0 - t, 3)

def ease_in_out_sine(t: float) -> float:
    """Gentle sinusoidal oscillation."""
    t = max(0.0, min(1.0, t))
    return -(math.cos(math.pi * t) - 1.0) / 2.0

# ---------------------------------------------------------------------------
# Backgrounds & Environment Rendering
# ---------------------------------------------------------------------------

def draw_gradient_background(
    draw: ImageDraw.ImageDraw,
    W: int,
    H: int,
    top_color: Tuple[int, int, int],
    bot_color: Tuple[int, int, int]
):
    """Draws a smooth vertical gradient backdrop."""
    steps = 60
    step_h = H // steps
    for i in range(steps):
        ratio = i / float(steps)
        r = int(top_color[0] * (1 - ratio) + bot_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bot_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bot_color[2] * ratio)
        y0 = i * step_h
        y1 = H if i == steps - 1 else (i + 1) * step_h
        draw.rectangle([0, y0, W, y1], fill=(r, g, b))

def draw_environment_background(
    draw: ImageDraw.ImageDraw,
    style: str,
    card_box: Tuple[int, int, int, int],
    time_sec: float,
    theme: str = "steer"
):
    """Draws thematic animated environment inside the center visual card."""
    cx0, cy0, cx1, cy1 = card_box
    cW = cx1 - cx0
    cH = cy1 - cy0

    if style == "clean_infographic" or theme == "clean_infographic":
        # Scientific dark slate matrix background with coordinate grid & scanning laser beam
        draw.rectangle([cx0, cy0, cx1, cy1], fill="#101726")
        # Subtle coordinate grid
        grid_step = 65
        for gx in range(cx0 + grid_step, cx1, grid_step):
            draw.line([gx, cy0, gx, cy1], fill="#1B283D", width=1)
        for gy in range(cy0 + grid_step, cy1, grid_step):
            draw.line([cx0, gy, cx1, gy], fill="#1B283D", width=1)
            # Intersecting coordinate crosshairs
            for gx in range(cx0 + grid_step, cx1, grid_step * 2):
                draw.line([gx - 4, gy, gx + 4, gy], fill="#168AAD", width=1)
                draw.line([gx, gy - 4, gx, gy + 4], fill="#168AAD", width=1)
        # Moving vertical laser scan beam
        scan_y = cy0 + int((time_sec * 90) % (cH - 20))
        draw.line([cx0 + 20, scan_y, cx1 - 20, scan_y], fill="#52B788", width=2)
        draw.line([cx0 + 20, scan_y + 1, cx1 - 20, scan_y + 1], fill="#168AAD", width=1)

    elif style == "inside_body":
        # Deep microscopic cellular bio-matrix
        draw.rectangle([cx0, cy0, cx1, cy1], fill="#140E26")
        # Multilayered floating cellular micro-particles with depth parallax
        for i in range(16):
            px = cx0 + 40 + ((i * 67 + int(time_sec * 12)) % (cW - 80))
            py = cy0 + 35 + ((i * 59 + int(math.sin(time_sec * 1.5 + i) * 18)) % (cH - 70))
            rad = 6 + (i % 4) * 3
            draw.ellipse([px - rad, py - rad, px + rad, py + rad], fill=(138, 77, 240, 45), outline="#7209B7", width=1)
        # Capillary / vascular track
        pts = [(cx0 + x, cy0 + int(cH * 0.80 + math.sin(x * 0.02 + time_sec * 3.5) * 14)) for x in range(0, cW, 10)]
        if len(pts) > 1:
            draw.line(pts, fill="#E63946", width=8)
            # Flowing red blood cell micro-discs along the capillary
            for r in range(5):
                flow_x = (int(time_sec * 90 + r * (cW // 5))) % (cW - 40)
                flow_y = cy0 + int(cH * 0.80 + math.sin((flow_x) * 0.02 + time_sec * 3.5) * 14)
                draw.ellipse([cx0 + flow_x - 8, flow_y - 6, cx0 + flow_x + 8, flow_y + 6], fill="#FF4D6D", outline="#800F2F", width=2)

    elif style == "fruits_food":
        # Warm kitchen counter with pastel wood shelves & rising aroma wisps
        bg_col = "#FFF4D6" if theme == "colorful_cartoon" else "#FFF9F2"
        draw.rectangle([cx0, cy0, cx1, cy1], fill=bg_col)
        # Wooden shelf at top
        draw.rectangle([cx0, cy0 + 60, cx1, cy0 + 85], fill="#EAD5C3")
        draw.rectangle([cx0, cy0 + 85, cx1, cy0 + 92], fill="#D8BEA7")
        # Cute spice jars on shelf
        for jx in [cx0 + 80, cx0 + 160, cx1 - 180, cx1 - 100]:
            draw.rounded_rectangle([jx, cy0 + 20, jx + 45, cy0 + 60], radius=6, fill="#F2E6D8", outline="#C9B29B", width=2)
            draw.rectangle([jx + 10, cy0 + 14, jx + 35, cy0 + 20], fill="#8A6D55")
        # Floating aroma steam curves
        for a in range(3):
            ax = cx0 + 180 + a * 260
            ay = cy1 - 130 - int((time_sec * 40 + a * 30) % 180)
            sway = int(math.sin(time_sec * 3.0 + a) * 12)
            draw.arc([ax + sway - 12, ay - 20, ax + sway + 12, ay + 20], start=45, end=225, fill="#EAD5C3", width=2)
        # If colorful_cartoon theme: add floating rotating cartoon stars and sparkles
        if theme == "colorful_cartoon":
            for s in range(5):
                star_x = cx0 + 60 + ((s * 170 + int(time_sec * 20)) % (cW - 120))
                star_y = cy0 + 110 + int(math.sin(time_sec * 2.0 + s) * 25)
                # Draw playful 4-point cartoon sparkle
                draw.line([star_x - 8, star_y, star_x + 8, star_y], fill="#EF476F", width=3)
                draw.line([star_x, star_y - 8, star_x, star_y + 8], fill="#EF476F", width=3)
                draw.ellipse([star_x - 3, star_y - 3, star_x + 3, star_y + 3], fill="#FFD166")
        # Countertop line at bottom
        draw.rectangle([cx0, cy1 - 90, cx1, cy1], fill="#E5CBB7")
        draw.line([cx0, cy1 - 90, cx1, cy1 - 90], fill="#C4A48C", width=3)

    elif style == "funny_science_convo":
        # Creator Podcast / Science Studio
        draw.rectangle([cx0, cy0, cx1, cy1], fill="#1C1A24")
        for row in range(3):
            for col in range(6):
                hx = cx0 + 60 + col * 120 + (row % 2) * 60
                hy = cy0 + 50 + row * 85
                draw.rectangle([hx - 35, hy - 25, hx + 35, hy + 25], fill="#282535", outline="#3C374D", width=1)
        draw.rounded_rectangle([cx0 + cW // 2 - 140, cy0 + 25, cx0 + cW // 2 + 140, cy0 + 68], radius=8, fill="#2A1B28", outline="#E63980", width=2)
        draw.rectangle([cx0, cy1 - 85, cx1, cy1], fill="#2D283E")
        draw.line([cx0, cy1 - 85, cx1, cy1 - 85], fill="#6A5A8C", width=3)

    else:
        # Relatable Human: Modern cozy room with window, sunlight beam & animated clock
        draw.rectangle([cx0, cy0, cx1, cy1], fill="#F7F1E5")
        wx0, wy0, wx1, wy1 = cx1 - 220, cy0 + 40, cx1 - 50, cy0 + 220
        draw.rectangle([wx0, wy0, wx1, wy1], fill="#E3F2FD", outline="#C5D3E8", width=3)
        draw.line([(wx0 + wx1) // 2, wy0, (wx0 + wx1) // 2, wy1], fill="#C5D3E8", width=2)
        draw.line([wx0, (wy0 + wy1) // 2, wx1, (wy0 + wy1) // 2], fill="#C5D3E8", width=2)
        sun_shift = int(math.sin(time_sec * 0.8) * 15)
        draw.polygon([(wx0, wy1), (wx1, wy1), (wx1 - 80 + sun_shift, cy1 - 100), (wx0 - 140 + sun_shift, cy1 - 100)], fill="#FFF3CD")
        clock_cx, clock_cy = cx0 + 100, cy0 + 80
        draw.ellipse([clock_cx - 30, clock_cy - 30, clock_cx + 30, clock_cy + 30], fill="#FFFFFF", outline="#7D6B5D", width=3)
        tick_t = time_sec % 1.0
        tick_angle = math.floor(time_sec) * (math.pi / 30) + ease_out_cubic(tick_t) * (math.pi / 30)
        hx = clock_cx + int(math.sin(tick_angle) * 18)
        hy = clock_cy - int(math.cos(tick_angle) * 18)
        draw.line([clock_cx, clock_cy, hx, hy], fill="#661414", width=2)
        draw.ellipse([clock_cx - 3, clock_cy - 3, clock_cx + 3, clock_cy + 3], fill="#351D1D")
        draw.rectangle([cx0, cy1 - 85, cx1, cy1], fill="#D4BBA5")
        draw.line([cx0, cy1 - 85, cx1, cy1 - 85], fill="#B89B82", width=3)

# ---------------------------------------------------------------------------
# Facial Features: Expressive Eyes & Viseme Mouth
# ---------------------------------------------------------------------------

def draw_cartoon_eyes(
    draw: ImageDraw.ImageDraw,
    ex: int,
    ey: int,
    eye_dist: int,
    eye_rad: int,
    is_blinking: bool,
    pupil_offset: Tuple[int, int] = (0, 0)
):
    """Draws expressive cartoon eyes with blinking, smooth eyelids, and pupil gaze."""
    if is_blinking:
        for offset in [-eye_dist // 2, eye_dist // 2]:
            bx = ex + offset
            draw.arc([bx - eye_rad, ey - 6, bx + eye_rad, ey + 6], start=0, end=180, fill="#222222", width=3)
    else:
        for offset in [-eye_dist // 2, eye_dist // 2]:
            bx = ex + offset
            draw.ellipse([bx - eye_rad, ey - eye_rad, bx + eye_rad, ey + eye_rad], fill="#FFFFFF", outline="#222222", width=2)
            px = bx + pupil_offset[0]
            py = ey + pupil_offset[1]
            p_rad = max(4, eye_rad // 2)
            draw.ellipse([px - p_rad, py - p_rad, px + p_rad, py + p_rad], fill="#1A1A1A")
            draw.ellipse([px - p_rad + 2, py - p_rad + 2, px - 1, py - 1], fill="#FFFFFF")

def draw_cartoon_mouth(
    draw: ImageDraw.ImageDraw,
    mx: int,
    my: int,
    mouth_w: int,
    mouth_state: int
):
    """Renders speech mouth visemes."""
    if mouth_state == 0:
        draw.arc([mx - mouth_w // 2, my - 8, mx + mouth_w // 2, my + 8], start=0, end=180, fill="#222222", width=3)
    elif mouth_state == 1:
        draw.ellipse([mx - mouth_w // 3, my - 10, mx + mouth_w // 3, my + 10], fill="#8A1C24", outline="#222222", width=2)
        draw.ellipse([mx - 6, my + 1, mx + 6, my + 8], fill="#FF85A1")
    elif mouth_state == 2:
        draw.chord([mx - mouth_w // 2, my - 12, mx + mouth_w // 2, my + 16], start=0, end=180, fill="#7D131B", outline="#222222", width=2)
        draw.rectangle([mx - mouth_w // 3, my - 12, mx + mouth_w // 3, my - 6], fill="#FFFFFF")
        draw.ellipse([mx - mouth_w // 4, my + 4, mx + mouth_w // 4, my + 14], fill="#FF85A1")
    else:
        draw.chord([mx - mouth_w // 2, my - 8, mx + mouth_w // 2, my + 16], start=0, end=180, fill="#FFFFFF", outline="#222222", width=2)
        draw.line([mx - mouth_w // 2, my - 8, mx + mouth_w // 2, my - 8], fill="#222222", width=2)

# ---------------------------------------------------------------------------
# Character Rendering: Interactive Talking Characters Duo
# ---------------------------------------------------------------------------

def render_talking_characters_duo(
    draw: ImageDraw.ImageDraw,
    stage_cx: int,
    stage_cy: int,
    scale: float,
    time_sec: float,
    mouth_state: int,
    action: str,
    scene_idx: int = 1,
    theme: str = "steer"
) -> int:
    """
    Renders an interactive 2-character dialogue between Manny the Mango and Appu the Apple.
    They visibly move, speak, react, and interact with each other:
    - In odd scenes: Manny speaks, Appu nods and listens attentively.
    - In even scenes: Appu speaks, Manny nods and listens attentively.
    Returns the x-coordinate of the active speaker for dialogue bubble tail alignment.
    """
    # Determine active speaker based on scene index for natural conversational turn-taking
    manny_speaking = (scene_idx % 2 == 1)
    
    # Left character: Manny the Mango
    mx = stage_cx - 150
    my = stage_cy + 25
    
    # Right character: Appu the Apple
    ax = stage_cx + 150
    ay = stage_cy + 25

    # 1. Manny the Mango
    bounce_m = math.sin(time_sec * 6.5) if manny_speaking else math.sin(time_sec * 3.5)
    dy_m = int(bounce_m * 12.0) if manny_speaking else int(bounce_m * 4.0)
    my_cur = my + dy_m
    sx_m = 1.0 + (0.05 * bounce_m if manny_speaking else 0.02 * bounce_m)
    sy_m = 1.0 - (0.05 * bounce_m if manny_speaking else 0.02 * bounce_m)
    rx_m, ry_m = int(85 * scale * sx_m), int(105 * scale * sy_m)

    # Shoes
    draw.ellipse([mx - 45, my_cur + ry_m - 12, mx - 10, my_cur + ry_m + 10], fill="#C04E2A")
    draw.ellipse([mx + 10, my_cur + ry_m - 12, mx + 45, my_cur + ry_m + 10], fill="#C04E2A")
    # Body
    draw.ellipse([mx - rx_m, my_cur - ry_m + 12, mx + rx_m, my_cur + ry_m], fill="#FFB703", outline="#D48600", width=4)
    # Highlights & Cheek blush
    draw.arc([mx - rx_m + 12, my_cur - ry_m + 20, mx, my_cur], start=160, end=270, fill="#FFE600", width=5)
    draw.ellipse([mx - 50, my_cur + 10, mx - 25, my_cur + 25], fill="#FF8C38")
    draw.ellipse([mx + 25, my_cur + 10, mx + 50, my_cur + 25], fill="#FF8C38")
    # Leaf on Head
    leaf_angle = math.cos(time_sec * 6.0) * 8.0
    draw.ellipse([mx - 8 + int(leaf_angle), my_cur - ry_m - 16, mx + 28 + int(leaf_angle), my_cur - ry_m + 4], fill="#2D6A4F", outline="#1B4332", width=2)
    draw.line([mx, my_cur - ry_m + 8, mx + 4, my_cur - ry_m - 12], fill="#5C3D2E", width=3)

    # Manny Face & Arms
    blink_m = (int(time_sec * 3.2) % 12 == 0) and (int(time_sec * 20) % 3 < 2)
    gaze_m = (4, 1) if not manny_speaking else (2, 0)  # Glances right toward Appu when listening
    draw_cartoon_eyes(draw, mx, my_cur - 20, int(45 * scale), int(15 * scale), blink_m, pupil_offset=gaze_m)
    m_mouth = mouth_state if manny_speaking else 0
    draw_cartoon_mouth(draw, mx, my_cur + 25, int(38 * scale), m_mouth)

    if manny_speaking:
        # Articulated arm extending toward Appu / Evidence
        draw.line([mx + rx_m - 8, my_cur + 8, mx + rx_m + 30, my_cur - 10], fill="#FFB703", width=8)
        draw.line([mx + rx_m + 30, my_cur - 10, mx + rx_m + 55, my_cur - 25], fill="#FFB703", width=7)
        draw.ellipse([mx + rx_m + 45, my_cur - 35, mx + rx_m + 68, my_cur - 15], fill="#FFB703", outline="#D48600", width=2)
        # Pulsing gleam at fingertip
        halo_r = int(5 + 3 * abs(math.sin(time_sec * 10.0)))
        draw.ellipse([mx + rx_m + 65 - halo_r, my_cur - 25 - halo_r, mx + rx_m + 65 + halo_r, my_cur - 25 + halo_r], outline="#FFE600", width=2)
        draw.line([mx - rx_m + 8, my_cur + 8, mx - rx_m - 25, my_cur + 25], fill="#FFB703", width=7)
    else:
        # Listening arm pose: relaxed nod
        draw.line([mx - rx_m + 8, my_cur + 8, mx - rx_m - 15, my_cur + 25], fill="#FFB703", width=7)
        draw.line([mx + rx_m - 8, my_cur + 8, mx + rx_m + 15, my_cur + 25], fill="#FFB703", width=7)

    # 2. Appu the Apple
    bounce_a = math.sin(time_sec * 6.5) if not manny_speaking else math.sin(time_sec * 3.5)
    dy_a = int(bounce_a * 12.0) if not manny_speaking else int(bounce_a * 4.0)
    ay_cur = ay + dy_a
    rad_ax = int(90 * scale * (1.0 + (0.04 * bounce_a if not manny_speaking else 0.02 * bounce_a)))
    rad_ay = int(90 * scale * (1.0 - (0.04 * bounce_a if not manny_speaking else 0.02 * bounce_a)))

    # Shoes with tap
    tap_r = int(abs(math.cos(time_sec * 8.0)) * 6) if not manny_speaking else 0
    draw.ellipse([ax - 45, ay_cur + rad_ay - 8, ax - 10, ay_cur + rad_ay + 12], fill="#661414")
    draw.ellipse([ax + 10, ay_cur + rad_ay - 8 - tap_r, ax + 45, ay_cur + rad_ay + 12 - tap_r], fill="#661414")
    # Body
    draw.ellipse([ax - rad_ax, ay_cur - rad_ay + 8, ax + rad_ax, ay_cur + rad_ay], fill="#E63946", outline="#9E1B24", width=4)
    draw.arc([ax - rad_ax + 14, ay_cur - rad_ay + 16, ax - 8, ay_cur], start=170, end=270, fill="#FFAAA6", width=4)
    # Stem & leaf
    draw.rectangle([ax - 4, ay_cur - rad_ay - 16, ax + 4, ay_cur - rad_ay + 12], fill="#5C3D2E")
    draw.ellipse([ax + 2, ay_cur - rad_ay - 22, ax + 30, ay_cur - rad_ay - 6], fill="#2A9D8F")
    # Cheeks
    draw.ellipse([ax - 50, ay_cur + 8, ax - 30, ay_cur + 22], fill="#FFAAA6")
    draw.ellipse([ax + 30, ay_cur + 8, ax + 50, ay_cur + 22], fill="#FFAAA6")

    # Appu Face & Glasses
    blink_a = (int(time_sec * 3.4) % 11 == 0) and (int(time_sec * 20) % 3 < 2)
    gaze_a = (-4, 1) if manny_speaking else (-2, 0)  # Glances left toward Manny when listening
    draw_cartoon_eyes(draw, ax, ay_cur - 20, int(42 * scale), int(15 * scale), blink_a, pupil_offset=gaze_a)
    a_mouth = mouth_state if not manny_speaking else 0
    draw_cartoon_mouth(draw, ax, ay_cur + 20, int(35 * scale), a_mouth)

    # Smart glasses with gleam
    draw.ellipse([ax - 38, ay_cur - 32, ax - 10, ay_cur - 8], outline="#1D3557", width=3)
    draw.ellipse([ax + 10, ay_cur - 32, ax + 38, ay_cur - 8], outline="#1D3557", width=3)
    draw.line([ax - 10, ay_cur - 20, ax + 10, ay_cur - 20], fill="#1D3557", width=3)
    gleam_pos = int((time_sec * 40) % 50) - 15
    draw.line([ax - 28 + gleam_pos, ay_cur - 28, ax - 20 + gleam_pos, ay_cur - 12], fill="#FFFFFF", width=2)

    # Appu Arms
    if not manny_speaking:
        draw.line([ax - rad_ax + 8, ay_cur + 8, ax - rad_ax - 28, ay_cur - 12], fill="#E63946", width=7)
        draw.ellipse([ax - rad_ax - 38, ay_cur - 22, ax - rad_ax - 18, ay_cur - 2], fill="#E63946", outline="#9E1B24", width=2)
        draw.line([ax + rad_ax - 8, ay_cur + 8, ax + rad_ax + 20, ay_cur + 25], fill="#E63946", width=7)
    else:
        draw.line([ax - rad_ax + 8, ay_cur + 8, ax - rad_ax - 15, ay_cur + 25], fill="#E63946", width=7)
        draw.line([ax + rad_ax - 8, ay_cur + 8, ax + rad_ax + 15, ay_cur + 25], fill="#E63946", width=7)

    # 3. Active Speaker Indicator Badges
    speaker_font = _get_font(18, bold=True)
    if manny_speaking:
        # Manny talking badge
        draw.rounded_rectangle([mx - 85, my - ry_m - 50, mx + 85, my - ry_m - 24], radius=6, fill="#FFB703", outline="#D48600", width=2)
        draw.text((mx - 75, my - ry_m - 46), "MANNY MANGO (TALKING)", fill="#351D1D", font=speaker_font)
        # Appu listening badge
        draw.rounded_rectangle([ax - 55, ay - rad_ay - 48, ax + 55, ay - rad_ay - 24], radius=6, fill="#FFFFFF", outline="#E6CBBD", width=1)
        draw.text((ax - 42, ay - rad_ay - 44), "Appu Apple", fill="#7D6B5D", font=speaker_font)
        return mx
    else:
        # Appu talking badge
        draw.rounded_rectangle([ax - 80, ay - rad_ay - 50, ax + 80, ay - rad_ay - 24], radius=6, fill="#E63946", outline="#9E1B24", width=2)
        draw.text((ax - 70, ay - rad_ay - 46), "APPU APPLE (TALKING)", fill="#FFFFFF", font=speaker_font)
        # Manny listening badge
        draw.rounded_rectangle([mx - 60, my - ry_m - 48, mx + 60, my - ry_m - 24], radius=6, fill="#FFFFFF", outline="#E6CBBD", width=1)
        draw.text((mx - 48, my - ry_m - 44), "Manny Mango", fill="#7D6B5D", font=speaker_font)
        return ax

# ---------------------------------------------------------------------------
# Inside Your Body: Physiological Organ Character & Vascular Circulation
# ---------------------------------------------------------------------------

def render_organ_character(
    draw: ImageDraw.ImageDraw,
    char_type: str,
    cx: int,
    cy: int,
    scale: float,
    time_sec: float,
    mouth_state: int,
    action: str
):
    """
    Renders Inside Your Body character:
    - Happy Heart with realistic dual-phase heartbeat contraction (systole/diastole),
      athletic sweatband, flexing bicep curls, and capillary pulse.
    - Brainy Neuron with synaptic sparks and glowing aura.
    - Glowy Glucose with chemical ring structure and orbital bond motion.
    """
    blink = (int(time_sec * 3.5) % 11 == 0) and (int(time_sec * 20) % 3 < 2)

    if "brain" in char_type.lower() or "neuron" in char_type.lower():
        # Brainy Neuron: Luminescent purple brain
        bob = int(math.sin(time_sec * 5.0) * 10.0)
        cy += bob
        bw, bh = int(120 * scale), int(90 * scale)
        aura_rad = int(15 + 8 * abs(math.sin(time_sec * 6.0)))
        draw.ellipse([cx - bw - aura_rad, cy - bh - aura_rad, cx + bw + aura_rad, cy + bh + aura_rad], fill=(138, 77, 240, 50))
        draw.ellipse([cx - bw, cy - bh, cx + 5, cy + bh], fill="#9B5DE5", outline="#7209B7", width=3)
        draw.ellipse([cx - 5, cy - bh, cx + bw, cy + bh], fill="#A663EC", outline="#7209B7", width=3)
        draw.arc([cx - bw + 20, cy - 30, cx - 10, cy + 30], start=30, end=200, fill="#5A189A", width=3)
        draw.arc([cx + 10, cy - 30, cx + bw - 20, cy + 30], start=340, end=150, fill="#5A189A", width=3)
        spark_angle = time_sec * 8.0
        spark_x = cx + int(math.cos(spark_angle) * (bw + 20))
        spark_y = cy - bh + int(math.sin(spark_angle) * 20)
        draw.line([spark_x - 8, spark_y, spark_x + 8, spark_y], fill="#FFE600", width=3)
        draw.line([spark_x, spark_y - 8, spark_x, spark_y + 8], fill="#FFE600", width=3)
        draw_cartoon_eyes(draw, cx, cy - 10, int(50 * scale), int(16 * scale), blink)
        draw_cartoon_mouth(draw, cx, cy + 30, int(40 * scale), mouth_state)

    elif "glucose" in char_type.lower():
        # Glowy Glucose: Joyful amber hexagon with orbiting bonds
        bob = int(math.sin(time_sec * 7.0) * 10.0)
        cy += bob
        rad = int(95 * scale)
        hex_pts = []
        for i in range(6):
            ang = i * (math.pi / 3) + (math.pi / 6)
            hex_pts.append((cx + int(math.cos(ang) * rad), cy + int(math.sin(ang) * rad)))
        draw.polygon(hex_pts, fill="#F77F00", outline="#D62828", width=4)
        orb_ang = time_sec * 4.0
        ox = cx + int(math.cos(orb_ang) * (rad + 35))
        oy = cy + int(math.sin(orb_ang) * (rad * 0.4))
        draw.ellipse([ox - 10, oy - 10, ox + 10, oy + 10], fill="#FFE600", outline="#D62828", width=2)
        draw_cartoon_eyes(draw, cx, cy - 15, int(45 * scale), int(16 * scale), blink)
        draw_cartoon_mouth(draw, cx, cy + 25, int(38 * scale), mouth_state)

    else:
        # Happy Heart (Default for VILPA / Cardiovascular Research)
        t_beat = (time_sec * 2.0) % 1.0
        if t_beat < 0.2:
            squeeze = math.sin(t_beat / 0.2 * math.pi) * 0.14
        elif t_beat < 0.5:
            squeeze = -math.sin((t_beat - 0.2) / 0.3 * math.pi) * 0.06
        else:
            squeeze = 0.0

        hw = int(115 * scale * (1.0 - squeeze))
        hh = int(115 * scale * (1.0 + squeeze * 0.5))

        # Anatomical Target Banner above heart
        banner_font = _get_font(18, bold=True)
        draw.rounded_rectangle([cx - 240, cy - hh - 65, cx + 240, cy - hh - 35], radius=6, fill="#661414", outline="#C04E2A", width=1)
        draw.text((cx - 225, cy - hh - 58), "ANATOMICAL TARGET: CARDIOVASCULAR & CELLULAR SYSTEM", fill="#FFF9F2", font=banner_font)

        # Heart Lobes
        draw.ellipse([cx - hw + 10, cy - hh, cx + 5, cy + 10], fill="#D62828", outline="#9E1B24", width=4)
        draw.ellipse([cx - 5, cy - hh, cx + hw - 10, cy + 10], fill="#D62828", outline="#9E1B24", width=4)
        draw.polygon([(cx - hw + 14, cy - 30), (cx + hw - 14, cy - 30), (cx, cy + hh)], fill="#D62828", outline="#9E1B24")
        # Athletic White Sweatband
        draw.rectangle([cx - hw + 25, cy - hh + 20, cx + hw - 25, cy - hh + 45], fill="#FFFFFF", outline="#1D3557", width=2)
        draw.line([cx - hw + 25, cy - hh + 32, cx + hw - 25, cy - hh + 32], fill="#E63946", width=2)
        # Flexing arms with bicep contraction curl timed with beat
        curl = int(abs(squeeze) * 30)
        draw.line([cx - hw + 10, cy - 10, cx - hw - 35, cy - 40 - curl], fill="#D62828", width=8)
        draw.line([cx - hw - 35, cy - 40 - curl, cx - hw - 20, cy - 70 - curl], fill="#D62828", width=8)
        draw.ellipse([cx - hw - 30, cy - 80 - curl, cx - hw - 10, cy - 60 - curl], fill="#D62828")
        draw.line([cx + hw - 10, cy - 10, cx + hw + 35, cy - 40 - curl], fill="#D62828", width=8)
        draw.line([cx + hw + 35, cy - 40 - curl, cx + hw + 20, cy - 70 - curl], fill="#D62828", width=8)
        draw.ellipse([cx + hw + 10, cy - 80 - curl, cx + hw + 30, cy - 60 - curl], fill="#D62828")
        # Rosy Cheeks
        draw.ellipse([cx - hw + 35, cy + 10, cx - hw + 60, cy + 25], fill="#FF758F")
        draw.ellipse([cx + hw - 60, cy + 10, cx + hw - 35, cy + 25], fill="#FF758F")
        # Eyes & Mouth
        draw_cartoon_eyes(draw, cx, cy - 15, int(50 * scale), int(18 * scale), blink)
        draw_cartoon_mouth(draw, cx, cy + 30, int(42 * scale), mouth_state)

# ---------------------------------------------------------------------------
# Clean Infographic: Animated Metric Bar Charts & Moving Data Diagrams
# ---------------------------------------------------------------------------

def render_clean_infographic_scene(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    card_box: Tuple[int, int, int, int],
    time_sec: float,
    frame_progress: float,
    desc_lines: List[str],
    theme_accent: str,
    theme_ink: str,
    theme_card: str
):
    """
    Renders high-end motion graphics for Clean Infographic:
    - Absolutely NO talking human presenter.
    - Moving diagrams, animated metric bars, labels, and evidence flow conduits.
    - Concentric expanding radar rings and traveling photon packets.
    """
    cx0, cy0, cx1, cy1 = card_box

    # 1. Infographic Header Label
    head_font = _get_font(22, bold=True)
    draw.rounded_rectangle([cx - 220, cy0 + 20, cx + 220, cy0 + 58], radius=8, fill="#1B283D", outline="#168AAD", width=2)
    draw.text((cx - 195, cy0 + 28), "EVIDENCE METRIC & FLOW DIAGRAM", fill="#52B788", font=head_font)

    # 2. Animated Metric Comparison Bar Chart
    chart_y = cy0 + 100
    chart_h = 160
    base_w = 120
    b1_x = cx - 180
    b2_x = cx + 60

    label_font = _get_font(18, bold=True)
    val_font = _get_font(24, bold=True)

    # Bar 1: Baseline Inactive Routine (100% Risk Reference)
    draw.rounded_rectangle([b1_x, chart_y + 20, b1_x + base_w, chart_y + chart_h], radius=6, fill="#1E2A3A", outline="#4A5568", width=2)
    draw.text((b1_x + 10, chart_y + chart_h + 10), "Standard Routine", fill="#A0AEC0", font=label_font)
    draw.text((b1_x + 35, chart_y + 45), "100%", fill="#E2E8F0", font=val_font)

    # Bar 2: Daily VILPA (60% Risk - 40% Reduction)
    anim_factor = ease_out_cubic(min(1.0, frame_progress * 1.5))
    target_top = chart_y + 20 + int(chart_h * 0.40 * anim_factor)
    draw.rounded_rectangle([b2_x, target_top, b2_x + base_w, chart_y + chart_h], radius=6, fill="#168AAD", outline="#52B788", width=2)
    draw.text((b2_x + 15, chart_y + chart_h + 10), "3-4 Daily Bouts", fill="#52B788", font=label_font)
    draw.text((b2_x + 40, target_top + 25), "60%", fill="#FFFFFF", font=val_font)

    # Highlighted Risk Reduction Pill
    pill_font = _get_font(20, bold=True)
    draw.rounded_rectangle([cx - 160, chart_y + chart_h + 45, cx + 160, chart_y + chart_h + 85], radius=20, fill="#52B788")
    draw.text((cx - 140, chart_y + chart_h + 52), "-40% ALL-CAUSE MORTALITY", fill="#101726", font=pill_font)

    # 3. Evidence Flow Conduits & Traveling Photon Packets
    flow_cy = cy0 + 440
    nodes = [
        (cx - 240, flow_cy, "DOSE", "3-4 Bouts / Day"),
        (cx, flow_cy, "COHORT", "n=25,241"),
        (cx + 240, flow_cy, "OUTCOME", "HR 0.60 (0.50-0.73)"),
    ]

    # Conduits
    draw.line([nodes[0][0], flow_cy, nodes[1][0], flow_cy], fill="#2D3748", width=4)
    draw.line([nodes[1][0], flow_cy, nodes[2][0], flow_cy], fill="#2D3748", width=4)

    # Traveling photons
    ph1 = (time_sec * 1.5) % 1.0
    px1 = int(nodes[0][0] * (1 - ph1) + nodes[1][0] * ph1)
    draw.ellipse([px1 - 6, flow_cy - 6, px1 + 6, flow_cy + 6], fill="#52B788")
    ph2 = (time_sec * 1.5 + 0.5) % 1.0
    px2 = int(nodes[1][0] * (1 - ph2) + nodes[2][0] * ph2)
    draw.ellipse([px2 - 6, flow_cy - 6, px2 + 6, flow_cy + 6], fill="#52B788")

    # Render Nodes
    for nx, ny, n_tag, n_sub in nodes:
        draw.ellipse([nx - 45, ny - 45, nx + 45, ny + 45], fill="#1A202C", outline="#168AAD", width=3)
        draw.ellipse([nx - 12, ny - 12, nx + 12, ny + 12], fill="#52B788")
        draw.text((nx - 24, ny + 55), n_tag, fill="#E2E8F0", font=label_font)
        sub_f = _get_font(15, bold=False)
        draw.text((nx - 55, ny + 80), n_sub, fill="#A0AEC0", font=sub_f)

# ---------------------------------------------------------------------------
# Relatable Human Characters
# ---------------------------------------------------------------------------

def render_human_character(
    draw: ImageDraw.ImageDraw,
    char_type: str,
    cx: int,
    cy: int,
    scale: float,
    time_sec: float,
    mouth_state: int,
    action: str
):
    """Renders Relatable Human character (Techie Raj, Active Maya, etc.) with natural speech posture & breathing."""
    breath = math.sin(time_sec * 2.5) * 4.0
    bob = int(math.sin(time_sec * 6.0) * 5.0)
    cy += bob
    blink = (int(time_sec * 3.4) % 10 == 0) and (int(time_sec * 20) % 3 < 2)

    body_w = int((90 + breath) * scale)
    body_h = int(120 * scale)
    outfit_color = "#3A86FF" if "maya" in char_type.lower() else "#2D6A4F"
    draw.rounded_rectangle([cx - body_w // 2, cy + 40, cx + body_w // 2, cy + 40 + body_h], radius=16, fill=outfit_color, outline="#1A1A1A", width=3)

    draw.rectangle([cx - 15, cy + 20, cx + 15, cy + 45], fill="#F1C27D")
    head_rad = int(60 * scale)
    draw.ellipse([cx - head_rad, cy - head_rad, cx + head_rad, cy + head_rad], fill="#F1C27D", outline="#1A1A1A", width=3)

    if "maya" in char_type.lower():
        draw.chord([cx - head_rad - 5, cy - head_rad - 15, cx + head_rad + 5, cy + 5], start=180, end=360, fill="#2C1A1D")
        draw.ellipse([cx + head_rad - 10, cy - 30, cx + head_rad + 30, cy + 10], fill="#2C1A1D")
    else:
        draw.chord([cx - head_rad - 5, cy - head_rad - 15, cx + head_rad + 5, cy + 5], start=180, end=360, fill="#1B1B1B")

    if "raj" in char_type.lower() or "techie" in char_type.lower() or "desk" in char_type.lower():
        draw.ellipse([cx - 40, cy - 15, cx - 8, cy + 15], outline="#1A1A1A", width=3)
        draw.ellipse([cx + 8, cy - 15, cx + 40, cy + 15], outline="#1A1A1A", width=3)
        draw.line([cx - 8, cy, cx + 8, cy], fill="#1A1A1A", width=3)

    draw_cartoon_eyes(draw, cx, cy - 5, int(45 * scale), int(15 * scale), blink)
    draw_cartoon_mouth(draw, cx, cy + 30, int(35 * scale), mouth_state)

    if "walk" in action.lower() or "active" in action.lower():
        swing = math.sin(time_sec * 8.0) * 25
        draw.line([cx - body_w // 2, cy + 55, cx - body_w // 2 - 25, cy + 110 + int(swing)], fill="#F1C27D", width=8)
        draw.line([cx + body_w // 2, cy + 55, cx + body_w // 2 + 25, cy + 110 - int(swing)], fill="#F1C27D", width=8)
    else:
        draw.line([cx - body_w // 2, cy + 55, cx - body_w // 2 - 30, cy + 85], fill="#F1C27D", width=8)
        draw.line([cx + body_w // 2, cy + 55, cx + body_w // 2 + 35, cy + 60], fill="#F1C27D", width=8)
        mug_x, mug_y = cx + body_w // 2 + 40, cy + 55
        draw.rounded_rectangle([mug_x - 12, mug_y - 15, mug_x + 12, mug_y + 15], radius=4, fill="#FFFFFF", outline="#1A1A1A", width=2)
        draw.arc([mug_x + 8, mug_y - 10, mug_x + 18, mug_y + 8], start=270, end=90, fill="#1A1A1A", width=2)
        steam_y = mug_y - 20 - int((time_sec * 25) % 30)
        draw.arc([mug_x - 6, steam_y - 10, mug_x + 6, steam_y + 10], start=45, end=225, fill="#9E9E9E", width=2)

# Helper for backward compatibility
def render_fruit_character(draw: ImageDraw.ImageDraw, char_type: str, cx: int, cy: int, scale: float, time_sec: float, mouth_state: int, action: str):
    """Wrapper that routes to interactive duo."""
    render_talking_characters_duo(draw, cx, cy, scale, time_sec, mouth_state, action, scene_idx=1)

def render_explainer_graphics(draw, cx, cy, card_box, time_sec, frame_progress, desc_lines, theme_accent, theme_ink, theme_card):
    """Wrapper that routes to clean infographic renderer."""
    render_clean_infographic_scene(draw, cx, cy, card_box, time_sec, frame_progress, desc_lines, theme_accent, theme_ink, theme_card)

def render_podcast_duo(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float, time_sec: float, mouth_state: int, active_speaker: str):
    """Renders 2-character Funny Science Conversation (Curious Vikram & Dr. Chitra)."""
    v_cx = cx - 180
    v_cy = cy + 20
    v_speaking = "vikram" in active_speaker.lower() or "curious" in active_speaker.lower() or "friend" in active_speaker.lower()
    v_mouth = mouth_state if v_speaking else 0
    v_bob = int(math.sin(time_sec * 7.0) * 5.0) if v_speaking else 0

    draw.rounded_rectangle([v_cx - 45, v_cy + 30 + v_bob, v_cx + 45, v_cy + 130 + v_bob], radius=14, fill="#E76F51", outline="#1A1A1A", width=3)
    draw.ellipse([v_cx - 45, v_cy - 45 + v_bob, v_cx + 45, v_cy + 45 + v_bob], fill="#E0AC69", outline="#1A1A1A", width=3)
    draw.chord([v_cx - 48, v_cy - 58 + v_bob, v_cx + 48, v_cy - 5 + v_bob], start=180, end=360, fill="#264653")
    draw_cartoon_eyes(draw, v_cx, v_cy - 5 + v_bob, 38, 14, False, pupil_offset=(4, 0))
    draw_cartoon_mouth(draw, v_cx, v_cy + 25 + v_bob, 32, v_mouth)
    draw.line([v_cx + 40, v_cy + 80, v_cx + 25, v_cy + 25], fill="#4A4E69", width=4)
    draw.ellipse([v_cx + 15, v_cy + 10, v_cx + 35, cy + 30], fill="#222222", outline="#C9ADA7", width=2)

    c_cx = cx + 180
    c_cy = cy + 10
    c_speaking = not v_speaking
    c_mouth = mouth_state if c_speaking else 0
    c_bob = int(math.sin(time_sec * 7.0) * 5.0) if c_speaking else 0

    draw.rounded_rectangle([c_cx - 48, c_cy + 30 + c_bob, c_cx + 48, c_cy + 130 + c_bob], radius=14, fill="#F8F9FA", outline="#1A1A1A", width=3)
    draw.arc([c_cx - 25, c_cy + 35 + c_bob, c_cx + 25, c_cy + 75 + c_bob], start=0, end=180, fill="#457B9D", width=3)
    draw.ellipse([c_cx - 45, c_cy - 45 + c_bob, c_cx + 45, c_cy + 45 + c_bob], fill="#F1C27D", outline="#1A1A1A", width=3)
    draw.chord([c_cx - 48, c_cy - 58 + c_bob, c_cx + 48, c_cy - 5 + c_bob], start=180, end=360, fill="#3D0066")
    draw.ellipse([c_cx - 32, c_cy - 12 + c_bob, c_cx - 8, c_cy + 12 + c_bob], outline="#1A1A1A", width=2)
    draw.ellipse([c_cx + 8, c_cy - 12 + c_bob, c_cx + 32, c_cy + 12 + c_bob], outline="#1A1A1A", width=2)
    draw.line([c_cx - 8, c_cy + c_bob, c_cx + 8, c_cy + c_bob], fill="#1A1A1A", width=2)
    draw_cartoon_eyes(draw, c_cx, c_cy - 5 + c_bob, 38, 14, False, pupil_offset=(-3, 0))
    draw_cartoon_mouth(draw, c_cx, c_cy + 25 + c_bob, 32, c_mouth)
    draw.line([c_cx - 40, c_cy + 80, c_cx - 25, c_cy + 25], fill="#4A4E69", width=4)
    draw.ellipse([c_cx - 35, c_cy + 10, c_cx - 15, cy + 30], fill="#222222", outline="#C9ADA7", width=2)

    active_cx = v_cx if v_speaking else c_cx
    active_label = "VIKRAM" if v_speaking else "DR. CHITRA"
    draw.rounded_rectangle([active_cx - 45, cy - 85, active_cx + 45, cy - 60], radius=6, fill="#FFE600", outline="#222222", width=1)
    draw.text((active_cx - 32, cy - 80), active_label, fill="#1A1A1A")
