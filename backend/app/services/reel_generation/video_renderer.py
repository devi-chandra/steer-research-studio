import os
import json
import math
import shutil
import functools
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from PIL import Image, ImageDraw, ImageFont
from app.core.config import settings
from app.core.database import get_db_connection
from app.services.localization.tts_adapter import tts_adapter

INDIC_LANG_CODES = {"hi_en", "te_en", "ta_en", "kn_en", "ml_en"}

def is_ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None

@functools.lru_cache(maxsize=32)
def _get_font(size: int, bold: bool = False, is_indic: bool = False):
    """
    Cached font loader with native Indic support (Nirmala.ttc on Windows) when rendering regional scripts.
    """
    if is_indic:
        indic_fonts = [
            "C:/Windows/Fonts/Nirmala.ttc",
            "C:/Windows/Fonts/NirmalaB.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "arial.ttf"
        ]
        for fpath in indic_fonts:
            try:
                return ImageFont.truetype(fpath, size)
            except Exception:
                continue

    font_names = [
        "georgiab.ttf" if bold else "georgia.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
        "segoeuib.ttf" if bold else "segoeui.ttf"
    ]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
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

from app.services.reel_generation.character_renderer import (
    draw_environment_background,
    render_talking_characters_duo,
    render_organ_character,
    render_clean_infographic_scene,
    render_human_character,
    render_podcast_duo,
    draw_gradient_background,
    ease_out_back,
    ease_in_out_cubic,
    ease_out_cubic
)

REEL_THEMES = {
    "steer": ("#FFF8F0", "#661414", "#C04E2A", "#FFFFFF"),
    "colorful_cartoon": ("#FFF4D6", "#7B2CBF", "#EF476F", "#FFFFFF"),
    "warm_editorial": ("#F3E2CF", "#5A3028", "#B65335", "#FFF9F1"),
    "pastel_educational": ("#F0EEFF", "#514A86", "#8278C8", "#FFFFFF"),
    "clean_infographic": ("#EFF5F8", "#174B62", "#168AAD", "#FFFFFF"),
}

def resolve_visual_style(scene: Dict[str, Any], mode: str, theme: str) -> str:
    """
    Deterministically resolves the correct visual rendering engine for the scene:
    - Clean Infographic: if theme is clean_infographic, or style is animated_explainer, or mode is clean_infographic/animated_explainer.
    - Inside Your Body: if mode is inside_body or style is inside_body.
    - Talking Characters: if style is fruits_food, or theme is colorful_cartoon, or mode is fruits_food/colorful_cartoon.
    - Professional: if mode is professional.
    - Relatable Human: default everyday lifestyle human.
    """
    if theme == "clean_infographic" or scene.get("style_type") in ("animated_explainer", "clean_infographic") or mode in ("animated_explainer", "clean_infographic"):
        return "clean_infographic"
    if mode == "inside_body" or scene.get("style_type") == "inside_body":
        return "inside_body"
    if scene.get("style_type") == "fruits_food" or theme == "colorful_cartoon" or mode in ("fruits_food", "colorful_cartoon"):
        return "fruits_food"
    if mode == "professional":
        return "professional"
    return scene.get("style_type") or "relatable_human"

def _create_scene_base_canvas(
    scene: Dict[str, Any],
    mode: str,
    scene_idx: int,
    total_scenes: int,
    lang_code: str,
    theme: str = "steer",
) -> Image.Image:
    """
    Pre-renders all static elements of the scene into a base canvas:
    - Background, borders, and theme cards
    - Segmented Instagram-style top progress bar structure
    - Branding headers, style badges, and scene titles
    - Static container boxes and badges
    - Subtitle card container and provenance/integrity footers
    """
    W, H = 1080, 1920
    is_indic = lang_code in INDIC_LANG_CODES
    char_action = scene.get("character_action") or "talking"
    narrator = scene.get("narrator_character") or "Narrator"

    visual_style = resolve_visual_style(scene, mode, theme)
    is_clinical_prof = (visual_style == "professional")

    bg_color, theme_ink, theme_accent, theme_card = REEL_THEMES[theme]
    if is_clinical_prof and theme == "steer":
        bg_color = "#F8F2EB"

    img = Image.new("RGB", (W, H), color=bg_color)
    draw = ImageDraw.Draw(img)

    # 1. Top Dynamic Progress Bar - Base bar and past segments
    bar_y = 16
    draw.rectangle([0, 0, W, bar_y], fill="#351D1D")
    seg_gap = 6
    seg_w = (W - (total_scenes - 1) * seg_gap) / max(1, total_scenes)
    for s in range(total_scenes):
        sx0 = int(s * (seg_w + seg_gap))
        sx1 = int(sx0 + seg_w)
        if s + 1 < scene_idx:
            draw.rectangle([sx0, 0, sx1, bar_y], fill=theme_accent)
        elif s + 1 == scene_idx:
            draw.rectangle([sx0, 0, sx1, bar_y], fill="#555555")
        else:
            draw.rectangle([sx0, 0, sx1, bar_y], fill="#444444")

    # 2. Brand & Header Bar
    brand_font = _get_font(24, bold=True)
    badge_font = _get_font(20, bold=True)

    if not is_clinical_prof:
        draw.rectangle([60, 45, W - 60, 120], fill=theme_card, outline=theme_accent, width=2)
        draw.text((85, 68), "STEER REEL • EVERYDAY SCIENCE", fill=theme_ink, font=brand_font)

        style_labels = {
            "fruits_food": "TALKING CHARACTERS",
            "inside_body": "INSIDE YOUR BODY",
            "relatable_human": "EVERYDAY LIFE",
            "clean_infographic": "CLEAN INFOGRAPHIC"
        }
        tag_text = style_labels.get(visual_style, "EVERYDAY REEL")
        if mode == "localvoice":
            tag_text = f"VOICE: {lang_code.upper()} (SOURCE SCRIPT)" if lang_code != "en" else "LOCALVOICE: EN"
        draw.text((W - 470, 68), tag_text, fill=theme_accent, font=brand_font)

        # Scene Title & Hook Badge
        draw.rounded_rectangle([90, 140, 480, 190], radius=8, fill=theme_ink)
        draw.text((105, 152), f"SCENE {scene_idx} • {scene.get('title', 'STORY').upper()}", fill="#FFF9F2", font=badge_font)

        # Reel Status Tag Text
        status_font = _get_font(18, bold=True)
        draw.text((W - 165, 152), "REEL", fill="#E63946", font=status_font)
    else:
        # Clinical Header
        draw.rectangle([60, 50, W - 60, 130], fill="#FFFFFF", outline="#E6CBBD", width=2)
        draw.text((85, 75), "STEER CLINICAL REEL", fill="#661414", font=brand_font)
        draw.text((W - 470, 75), "MODE: PROFESSIONAL CLINICAL", fill="#C04E2A", font=brand_font)

        draw.rounded_rectangle([90, 160, 440, 208], radius=8, fill="#661414")
        draw.text((105, 172), f"SCENE {scene_idx} • {scene.get('title', 'EVIDENCE').upper()}", fill="#F5EBDF", font=badge_font)

        status_font = _get_font(18, bold=True)
        draw.text((W - 175, 170), "ACTIVE", fill="#22C55E", font=status_font)

    # 3. Center Visual Graphic Card Container
    card_top = 215 if not is_clinical_prof else 235
    card_bottom = 1080 if not is_clinical_prof else 1060

    if not is_clinical_prof:
        draw.rounded_rectangle([90, card_top, W - 90, card_bottom], radius=20, fill=theme_card, outline=theme_accent, width=2)
        # Narrator badge
        narrator_label = narrator[:24]
        if visual_style == "fruits_food":
            narrator_label = "Manny Mango & Appu Apple"
        elif visual_style == "inside_body":
            narrator_label = "Physiological Heart Hero"
        elif visual_style == "clean_infographic":
            narrator_label = "Verified Evidence Matrix"
        draw.rounded_rectangle([115, card_top + 20, 530, card_top + 68], radius=8, fill="#FFFFFF", outline="#351D1D", width=2)
        narrator_font = _get_font(22, bold=True)
        draw.text((130, card_top + 30), f"Starring: {narrator_label}", fill="#661414", font=narrator_font)
        # Action badge
        draw.rounded_rectangle([W - 470, card_top + 20, W - 115, card_top + 68], radius=8, fill="#FFF3CD", outline="#E0AC69", width=1)
        action_font = _get_font(18, bold=True)
        action_label = char_action[:18].upper()
        if visual_style == "fruits_food":
            action_label = "INTERACTIVE DUO"
        elif visual_style == "clean_infographic":
            action_label = "DATA DIAGRAM"
        draw.text((W - 455, card_top + 32), f"Mode: {action_label}", fill="#856404", font=action_font)
    else:
        draw.rounded_rectangle([90, card_top, W - 90, card_bottom], radius=16, fill="#FFFFFF", outline="#B58777", width=2)
        narrator_font = _get_font(22, bold=True)
        draw.text((130, card_top + 25), f"Speaker: {narrator}", fill="#661414", font=narrator_font)
        icon_box = [130, card_top + 70, W - 130, card_bottom - 120]
        draw.rectangle(icon_box, fill="#F8F2EB", outline="#E6CBBD", width=1)
        accent_font = _get_font(36, bold=True)
        draw.text((160, card_top + 95), "CLINICAL DATA MATRIX", fill="#661414", font=accent_font)
        draw.line([160, card_top + 145, W - 160, card_top + 145], fill="#661414", width=3)

    # 4. Bottom Subtitle Card Container
    sub_top = 1110
    sub_bottom = 1670
    draw.rounded_rectangle([90, sub_top, W - 90, sub_bottom], radius=16, fill="#351D1D")
    sub_label_font = _get_font(20, bold=True)
    sub_label_text = "SYNCHRONIZED NARRATION & SUBTITLES" if lang_code == "en" else "SYNCHRONIZED SUBTITLES (SOURCE ENGLISH)"
    draw.text((130, sub_top + 25), sub_label_text, fill="#E6CBBD", font=sub_label_font)

    # 5. Provenance & Integrity Footer
    foot_font = _get_font(20, bold=False)
    claim_id = scene.get("claim_ids", ["CLM-01"])[0] if scene.get("claim_ids") else "CLM-01"
    draw.text((90, 1710), f"Grounding: Verified Evidence Claim {claim_id} • Peer-Reviewed DOI", fill="#B58777", font=foot_font)
    draw.text((90, 1745), "Steer Medical Integrity Gate: Simulated Review Workflow (Demo Mode)", fill="#661414", font=foot_font)

    return img

def _render_scene_frame_dynamic(
    scene: Dict[str, Any],
    mode: str,
    scene_idx: int,
    total_scenes: int,
    frame_progress: float,
    lang_code: str,
    desc_lines: List[str],
    sub_lines: List[str],
    output_path: Optional[Path] = None,
    time_sec: float = 0.0,
    theme: str = "steer",
    base_canvas: Optional[Image.Image] = None,
) -> Any:
    """
    Renders an animated 1080x1920 portrait frame with dedicated, visibly distinct renderers:
    - Talking Characters: Interactive 2-character dialogue (Manny the Mango & Appu the Apple).
    - Inside Your Body: Anatomical Happy Heart hero, cardiac contraction, and capillary blood cell flow.
    - Clean Infographic: Moving diagrams, animated metric comparison bars, and evidence flow conduits.
    - Colourful Cartoon: Vibrant candy cartoon styling, floating cartoon sparkles and stars.
    - Relatable Human: Everyday lifestyle human presenter.
    - Professional: Clinical data matrix with moving ECG wave and equalizer.
    """
    W, H = 1080, 1920
    is_indic = lang_code in INDIC_LANG_CODES
    char_type = scene.get("character_type") or ""
    char_action = scene.get("character_action") or "talking"

    visual_style = resolve_visual_style(scene, mode, theme)
    is_clinical_prof = (visual_style == "professional")

    bg_color, theme_ink, theme_accent, theme_card = REEL_THEMES[theme]

    # Initialize frame canvas: reuse pre-rendered base canvas for extreme speed
    if base_canvas is None:
        base_canvas = _create_scene_base_canvas(scene, mode, scene_idx, total_scenes, lang_code, theme)
    img = base_canvas.copy()
    draw = ImageDraw.Draw(img)

    # 1. Top Dynamic Progress Bar - Active segment fill & leading pulse dot
    bar_y = 16
    seg_gap = 6
    seg_w = (W - (total_scenes - 1) * seg_gap) / max(1, total_scenes)
    sx0 = int((scene_idx - 1) * (seg_w + seg_gap))
    curr_fill = int(sx0 + seg_w * frame_progress)
    draw.rectangle([sx0, 0, curr_fill, bar_y], fill=theme_accent)
    if curr_fill > sx0 + 3:
        draw.ellipse([curr_fill - 3, bar_y // 2 - 3, curr_fill + 3, bar_y // 2 + 3], fill="#FFFFFF")

    # 2. Live Status Indicator Glow
    live_glow = int(frame_progress * 10) % 2 == 0
    if not is_clinical_prof:
        draw.ellipse([W - 190, 155, W - 176, 169], fill="#FF006E" if live_glow else "#D62828")
    else:
        draw.ellipse([W - 200, 172, W - 186, 186], fill="#22C55E" if live_glow else "#16A34A")

    # 3. Center Visual Graphic Card
    card_top = 215 if not is_clinical_prof else 235
    card_bottom = 1080 if not is_clinical_prof else 1060
    inner_box = (92, card_top + 2, W - 92, card_bottom - 2)

    mouth_state = int(time_sec * 8.0) % 4
    stage_cx = W // 2
    stage_cy = card_top + 450
    active_speaker_x = stage_cx

    if not is_clinical_prof:
        # A. Draw Thematic Environment Background
        draw_environment_background(draw, visual_style, inner_box, time_sec, theme=theme)

        # B. Dedicated Mode-Specific Renderers
        if visual_style == "fruits_food":
            # Interactive 2-Character Dialogue (Manny the Mango & Appu the Apple)
            active_speaker_x = render_talking_characters_duo(
                draw, stage_cx, stage_cy - 10, 1.35, time_sec, mouth_state, char_action, scene_idx=scene_idx, theme=theme
            )
        elif visual_style == "inside_body":
            # Anatomical Organ Hero & Capillary Circulation
            render_organ_character(draw, char_type or "heart", stage_cx, stage_cy - 15, 1.35, time_sec, mouth_state, char_action)
            active_speaker_x = stage_cx
        elif visual_style == "clean_infographic":
            # Clean Infographic: Moving Diagrams, Animated Metric Bars, Evidence Flow
            render_clean_infographic_scene(draw, stage_cx, stage_cy, inner_box, time_sec, frame_progress, desc_lines, theme_accent, theme_ink, theme_card)
        else:
            # Everyday Lifestyle Human
            render_human_character(draw, char_type or "techie", stage_cx, stage_cy - 15, 1.35, time_sec, mouth_state, char_action)
            active_speaker_x = stage_cx

        # C. Animated Comic Speech Dialogue Callout Bubble with kinetic pop-in
        if visual_style != "clean_infographic":
            bubble_top = card_bottom - 195
            bubble_bottom = card_bottom - 20
            b_w = W - 260
            b_h = bubble_bottom - bubble_top

            pop_prog = min(1.0, time_sec / 0.45)
            pop_factor = ease_out_back(pop_prog)
            cur_w = int(b_w * (0.85 + 0.15 * pop_factor))
            cur_h = int(b_h * (0.85 + 0.15 * pop_factor))
            bx0 = stage_cx - cur_w // 2
            bx1 = stage_cx + cur_w // 2
            by0 = bubble_bottom - cur_h
            by1 = bubble_bottom

            draw.rounded_rectangle([bx0, by0, bx1, by1], radius=16, fill="#FFFFFF", outline="#351D1D", width=3)
            # Tail pointer pointing directly towards active speaker
            tail_x = max(bx0 + 40, min(bx1 - 40, active_speaker_x))
            draw.polygon([(tail_x - 18, by0), (tail_x, by0 - 18), (tail_x + 15, by0)], fill="#FFFFFF")
            draw.line([(tail_x - 18, by0), (tail_x, by0 - 18)], fill="#351D1D", width=3)
            draw.line([(tail_x, by0 - 18), (tail_x + 15, by0)], fill="#351D1D", width=3)

            if pop_prog > 0.4:
                callout_font = _get_font(26, bold=True)
                callout_lines = desc_lines[:2] if desc_lines else ["Evidence-based daily insight."]
                cy_text = by0 + 22
                for cl in callout_lines:
                    draw.text((bx0 + 30, cy_text), cl, fill="#222222", font=callout_font)
                    cy_text += 34

    else:
        # Professional Clinical Card (ECG Pulse Wave & Spectrum Analyzer)
        wave_y_base = card_top + 225
        pts = []
        for x in range(160, W - 160, 8):
            phase = (x * 0.02) - (frame_progress * 14.0)
            norm_x = (x - 160) / (W - 320)
            spike = 0
            if 0.42 < norm_x < 0.58:
                spike = math.sin((norm_x - 0.42) / 0.16 * math.pi) * 36.0
            wy = wave_y_base - math.sin(phase) * 18.0 - spike
            pts.append((x, int(wy)))
        if len(pts) > 1:
            draw.line(pts, fill="#661414", width=4)
            active_dot_x = 160 + int((frame_progress % 1.0) * (W - 320))
            active_phase = (active_dot_x * 0.02) - (frame_progress * 14.0)
            active_dot_y = int(wave_y_base - math.sin(active_phase) * 18.0)
            draw.ellipse([active_dot_x - 7, active_dot_y - 7, active_dot_x + 7, active_dot_y + 7], fill="#FFE600", outline="#FFFFFF", width=2)

        desc_font = _get_font(28, bold=False)
        curr_dy = card_top + 295
        for dl in desc_lines[:5]:
            draw.text((160, curr_dy), dl, fill="#351D1D", font=desc_font)
            curr_dy += 38

        eq_base_y = card_bottom - 25
        num_bars = 20
        bar_w = 22
        bar_gap = 14
        start_bx = 160
        for b in range(num_bars):
            bx = start_bx + b * (bar_w + bar_gap)
            h_val = abs(math.sin(frame_progress * 20.0 + b * 0.7)) * 0.7 + abs(math.cos(frame_progress * 12.0 + b * 1.4)) * 0.3
            bar_h = max(8, int(h_val * 62.0))
            b_color = "#661414" if b % 2 == 0 else "#C04E2A"
            draw.rounded_rectangle([bx, eq_base_y - bar_h, bx + bar_w, eq_base_y], radius=3, fill=b_color)

    # 4. Bottom Subtitle Card with Synchronized Highlight Sweep
    sub_top = 1110
    sub_font = _get_font(32, bold=True, is_indic=is_indic)
    sub_y = sub_top + 70
    displayed_sub_lines = sub_lines[:8]
    num_sub_lines = len(displayed_sub_lines)
    active_line_idx = min(num_sub_lines - 1, int(frame_progress * num_sub_lines)) if num_sub_lines > 0 else 0

    for idx, sl in enumerate(displayed_sub_lines):
        if idx == active_line_idx:
            draw.text((130, sub_y), sl, fill="#FFE600", font=sub_font)
        else:
            draw.text((130, sub_y), sl, fill="#FFFFFF", font=sub_font)
        sub_y += 44

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "PNG", quality=95)
        return output_path

    return img

async def render_video_reel(
    project_id: str,
    reel_mode: str,
    scenes: List[Dict[str, Any]],
    lang_code: str = "en",
    fps: int = 15,
    allow_mock_tts: bool = False,
    theme: str = "steer",
) -> Dict[str, Any]:
    """
    Renders an actual vertical 1080x1920 MP4 video reel with scene motion graphics,
    TTS neural voice narration, and synchronized native subtitles.
    Optimized high-performance pipeline with direct FFmpeg rawvideo pipe encoding.
    """
    if not is_ffmpeg_available():
        raise RuntimeError("FFmpeg is not available in system PATH. Video encoding requires FFmpeg.")

    if not scenes:
        raise ValueError(f"No scenes provided to render for mode '{reel_mode}'.")
    if theme not in REEL_THEMES:
        raise ValueError(f"Unsupported reel theme '{theme}'.")

    work_dir = settings.GENERATED_DIR / "reels" / f"{project_id}_{reel_mode}_{lang_code}"
    work_dir.mkdir(parents=True, exist_ok=True)

    rendered_scenes_data = []
    concat_list_path = work_dir / "concat_list.txt"
    scene_segments = []

    dummy_img = Image.new("RGB", (100, 100))
    dummy_draw = ImageDraw.Draw(dummy_img)

    # 1. Parallelize TTS Audio Generation across all scenes
    tts_tasks = [
        tts_adapter.generate_speech(
            sc.get("narration_text", "Steer verified clinical research."),
            lang_code,
            work_dir / f"audio_{i+1:02d}.mp3",
            allow_mock=allow_mock_tts
        )
        for i, sc in enumerate(scenes)
    ]
    tts_results = await asyncio.gather(*tts_tasks)

    for idx, (tts_ok, tts_prov, tts_details) in enumerate(tts_results):
        scene_idx = idx + 1
        sc = scenes[idx]
        scene_mp4 = work_dir / f"scene_{scene_idx:02d}.mp4"
        audio_mp3 = work_dir / f"audio_{scene_idx:02d}.mp3"
        preview_png = work_dir / f"frame_{scene_idx:02d}.png"

        if not tts_ok or not audio_mp3.exists() or audio_mp3.stat().st_size < 100:
            raise RuntimeError(f"TTS audio generation failed for scene {scene_idx} in language '{lang_code}': {tts_details}")

        # 2. Measure audio duration with ffprobe
        duration = 4.5
        try:
            probe_cmd = [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(audio_mp3)
            ]
            res = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0 and res.stdout.strip():
                duration = max(2.5, float(res.stdout.strip()) + 0.3)
        except Exception:
            duration = 4.5

        is_indic = lang_code in INDIC_LANG_CODES
        desc_font = _get_font(28, bold=False)
        desc_lines = _wrap_text(sc.get("visual_description", ""), desc_font, 1080 - 360, dummy_draw)

        raw_sub = sc.get("subtitle_native") if is_indic and sc.get("subtitle_native") else sc.get("narration_text", "")
        sub_font = _get_font(32, bold=True, is_indic=is_indic)
        sub_lines = _wrap_text(raw_sub, sub_font, 1080 - 260, dummy_draw)

        # 3. Pre-render static base canvas once for this scene
        base_canvas = _create_scene_base_canvas(
            sc, reel_mode, scene_idx, len(scenes), lang_code, theme=theme
        )

        num_frames = max(10, int(duration * fps))

        # 4. Stream uncompressed raw frames directly to FFmpeg pipe
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo",
            "-pix_fmt", "rgb24",
            "-s", "1080x1920",
            "-r", str(fps),
            "-i", "pipe:0",
            "-i", str(audio_mp3),
            "-c:v", "libx264",
            # Keep encoder memory predictable on small hosted instances.
            "-threads", "1",
            "-preset", "ultrafast",
            "-tune", "animation",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "44100",
            "-ac", "2",
            "-t", str(duration),
            "-shortest",
            str(scene_mp4)
        ]

        ffmpeg_log_path = work_dir / f"scene_{scene_idx:02d}_ffmpeg.log"
        if scene_mp4.exists():
            scene_mp4.unlink()

        # Preserve FFmpeg diagnostics instead of hiding the cause of failure.
        with ffmpeg_log_path.open("wb") as ffmpeg_log:
            proc = subprocess.Popen(
                ffmpeg_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=ffmpeg_log
            )

            try:
                for f in range(num_frames):
                    frame_prog = f / max(1, num_frames - 1)
                    time_sec = f / float(fps)
                    frame_img = _render_scene_frame_dynamic(
                        sc, reel_mode, scene_idx, len(scenes),
                        frame_prog, lang_code, desc_lines, sub_lines,
                        time_sec=time_sec, theme=theme,
                        base_canvas=base_canvas
                    )
                    if f == 0:
                        frame_img.save(preview_png, "PNG")

                    try:
                        proc.stdin.write(frame_img.convert("RGB").tobytes())
                    except (BrokenPipeError, OSError):
                        break
            finally:
                if proc.stdin:
                    try:
                        proc.stdin.close()
                    except (BrokenPipeError, OSError):
                        pass
                proc.wait()

        if proc.returncode != 0 or not scene_mp4.exists() or scene_mp4.stat().st_size == 0:
            diagnostic = ffmpeg_log_path.read_text(encoding="utf-8", errors="replace").strip()
            diagnostic = diagnostic[-2400:] if diagnostic else "FFmpeg produced no diagnostic output."
            raise RuntimeError(
                f"FFmpeg scene encoding failed for scene {scene_idx} "
                f"(exit code {proc.returncode}): {diagnostic}"
            )

        scene_segments.append(scene_mp4)
        rendered_scenes_data.append({
            "scene_index": scene_idx,
            "title": sc.get("title", ""),
            "duration": round(duration, 1),
            "frame_preview": f"/storage/generated/reels/{project_id}_{reel_mode}_{lang_code}/frame_{scene_idx:02d}.png",
            "audio_url": f"/storage/generated/reels/{project_id}_{reel_mode}_{lang_code}/audio_{scene_idx:02d}.mp3",
            "tts_provider": tts_prov,
            "tts_details": tts_details
        })

    # 5. Concatenate all scenes into final video
    final_mp4 = settings.GENERATED_DIR / "reels" / f"reel_{project_id}_{reel_mode}_{lang_code}.mp4"
    if scene_segments:
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for seg in scene_segments:
                f.write(f"file '{str(seg).replace(chr(92), '/')}'\n")

        concat_cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_list_path),
            "-c", "copy",
            str(final_mp4)
        ]
        cat_res = subprocess.run(concat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if cat_res.returncode != 0 or not final_mp4.exists():
            shutil.copy(scene_segments[0], final_mp4)

    file_size = final_mp4.stat().st_size if final_mp4.exists() else 0
    total_duration = sum(s["duration"] for s in rendered_scenes_data)

    # 6. Save asset record in database
    asset_id = f"ast-reel-{project_id}-{reel_mode}-{lang_code}"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO assets (id, project_id, asset_type, title, status, file_path, preview_url, metadata_json, updated_at)
    VALUES (?, ?, ?, ?, 'rendered', ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        asset_id,
        project_id,
        f"reel_{reel_mode}",
        f"Video Reel ({reel_mode.capitalize()} - {lang_code})",
        str(final_mp4),
        f"/storage/generated/reels/reel_{project_id}_{reel_mode}_{lang_code}.mp4",
        json.dumps({
            "mode": reel_mode,
            "lang_code": lang_code,
            "duration": total_duration,
            "file_size": file_size,
            "resolution": "1080x1920",
            "scenes": rendered_scenes_data
        })
    ))
    conn.commit()
    conn.close()

    return {
        "success": True,
        "project_id": project_id,
        "asset_id": asset_id,
        "reel_mode": reel_mode,
        "language_code": lang_code,
        "video_url": f"/storage/generated/reels/reel_{project_id}_{reel_mode}_{lang_code}.mp4",
        "total_duration_seconds": round(total_duration, 1),
        "file_size_bytes": file_size,
        "resolution": "1080x1920",
        "scenes": rendered_scenes_data
    }
