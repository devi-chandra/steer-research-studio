import json
import pytest
import subprocess
from pathlib import Path
from PIL import Image
from app.core.config import settings
from app.core.database import get_db_connection
from app.services.reel_generation.everyday_reel_generator import generate_everyday_storyboard
from app.services.reel_generation.video_renderer import render_video_reel, is_ffmpeg_available

PROJECT_ID = "test-proj-001"

@pytest.fixture(autouse=True)
def ensure_project():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM projects WHERE id = ?", (PROJECT_ID,))
    if not c.fetchone():
        c.execute("""
        INSERT INTO projects (id, title, doi, source_type, extraction_status, metadata_verified)
        VALUES (?, 'Association of wearable device-measured VILPA with mortality', '10.1038/s41591-022-02100-x', 'pdf', 'extracted', 1)
        """, (PROJECT_ID,))
    c.execute("SELECT count(*) FROM claims WHERE project_id = ?", (PROJECT_ID,))
    if c.fetchone()[0] == 0:
        c.execute("""
        INSERT INTO claims (id, project_id, claim_id, claim_text, exact_quote, page_number, numerical_result, sample_size, limitations, uncertainty, evidence_status, review_status)
        VALUES ('clm-test-01', ?, 'CLM-01', '3-4 bouts of VILPA reduced mortality by 40%', '3-4 bouts of 1-2 min VILPA per day', 1, '40% reduction in all-cause mortality', 'n=25,241 non-exercisers', 'Observational accelerometer cohort', 'HR=0.60 (95% CI 0.50-0.73)', 'Directly supported', 'Approved')
        """, (PROJECT_ID,))
    conn.commit()
    conn.close()

STYLE_THEME_PAIRS = [
    ("fruits_food", "colorful_cartoon"),
    ("inside_body", "steer"),
    ("relatable_human", "warm_editorial"),
    ("animated_explainer", "pastel_educational"),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("style,theme", STYLE_THEME_PAIRS)
async def test_reel_style_normal_frame_rate_mp4(style: str, theme: str):
    """
    Verifies that all four reel styles produce normal-frame-rate MP4s (15 fps, not 2 fps),
    with full video decoding, audio stream presence, correct duration, and distinctive theme palettes.
    Note: Audio presence and parameters are verified programmatically;
    subjective audio quality is explicitly NOT claimed without human listening.
    """
    assert is_ffmpeg_available(), "FFmpeg must be installed"

    # 1. Generate storyboard for this specific style
    sb = generate_everyday_storyboard(PROJECT_ID, requested_style=style)
    scenes = sb["scenes"]
    assert len(scenes) >= 1
    assert scenes[0]["style_type"] == style

    # 2. Render using the intended production frame rate (fps=15, default)
    # Using allow_mock_tts=True for fast, deterministic local test execution
    render_res = await render_video_reel(
        project_id=PROJECT_ID,
        reel_mode="everyday",
        scenes=scenes[:1],
        lang_code="en",
        fps=15,
        allow_mock_tts=True,
        theme=theme
    )
    assert render_res["success"] is True

    mp4_path = settings.BASE_DIR / render_res["video_url"].lstrip("/")
    assert mp4_path.exists(), f"Rendered MP4 must exist at {mp4_path}"
    assert mp4_path.stat().st_size > 30000, "Rendered MP4 must be non-empty"

    # 3. Probe video stream with ffprobe: verify 15 fps, 1080x1920, h264
    probe_v_cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,width,height,avg_frame_rate,r_frame_rate,nb_frames,duration",
        "-of", "json", str(mp4_path)
    ]
    v_proc = subprocess.run(probe_v_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert v_proc.returncode == 0, f"ffprobe video failed: {v_proc.stderr}"
    v_data = json.loads(v_proc.stdout)
    v_stream = v_data["streams"][0]

    assert v_stream["codec_name"] == "libx264" or v_stream["codec_name"] == "h264"
    assert v_stream["width"] == 1080
    assert v_stream["height"] == 1920

    # Strict check: production frame rate is 15 fps (15/1), NOT 2 fps diagnostic render
    avg_fps = v_stream["avg_frame_rate"]
    assert avg_fps in ("15/1", "15"), f"Expected 15 fps, got {avg_fps}"
    assert float(eval(avg_fps)) >= 14.9, f"Frame rate must be >= 14.9 fps, got {avg_fps}"

    # 4. Probe audio stream: verify audio presence (aac, channels, sample_rate, duration)
    probe_a_cmd = [
        "ffprobe", "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=codec_name,channels,sample_rate,duration",
        "-of", "json", str(mp4_path)
    ]
    a_proc = subprocess.run(probe_a_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert a_proc.returncode == 0, f"ffprobe audio failed: {a_proc.stderr}"
    a_data = json.loads(a_proc.stdout)
    assert len(a_data.get("streams", [])) > 0, "Audio stream must be present in MP4"
    a_stream = a_data["streams"][0]
    assert a_stream["codec_name"] == "aac"
    assert int(a_stream["channels"]) >= 1
    assert int(a_stream["sample_rate"]) >= 22050
    assert float(a_stream["duration"]) > 0

    # 5. Full decode test with ffmpeg null muxer (validates that video & audio decode cleanly without error)
    decode_cmd = [
        "ffmpeg", "-v", "error", "-i", str(mp4_path),
        "-f", "null", "-"
    ]
    dec_proc = subprocess.run(decode_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert dec_proc.returncode == 0, f"FFmpeg full decode encountered error: {dec_proc.stderr}"
    assert dec_proc.stderr.strip() == "", f"FFmpeg decode emitted warnings/errors: {dec_proc.stderr}"

    # 6. Verify duration
    duration = float(v_stream["duration"])
    assert duration >= 2.0, f"Duration {duration}s is too short"
    assert abs(duration - render_res["total_duration_seconds"]) < 0.5


def test_theme_visual_differences():
    """
    Verifies that different themes produce distinctly different color palettes / pixel values
    in the rendered frames.
    """
    from app.services.reel_generation.video_renderer import REEL_THEMES, _render_scene_frame_dynamic

    temp_dir = settings.GENERATED_DIR / "theme_test"
    temp_dir.mkdir(parents=True, exist_ok=True)

    dummy_scene = {
        "title": "Evidence Test",
        "narration_text": "Sample clinical finding text for theme test.",
        "visual_description": "Card preview description",
        "claim_ids": ["CLM-01"],
        "style_type": "relatable_human",
        "character_type": "techie",
        "character_action": "explain"
    }

    frames = {}
    for theme_name in ["steer", "colorful_cartoon", "warm_editorial", "pastel_educational", "clean_infographic"]:
        out_png = temp_dir / f"theme_{theme_name}.png"
        _render_scene_frame_dynamic(
            scene=dummy_scene,
            mode="everyday",
            scene_idx=1,
            total_scenes=1,
            frame_progress=0.5,
            lang_code="en",
            desc_lines=["Sample line 1"],
            sub_lines=["Sample subtitle line 1"],
            output_path=out_png,
            time_sec=1.0,
            theme=theme_name
        )
        assert out_png.exists()
        img = Image.open(out_png)
        # Sample pixels from top background (x=500, y=10) and card area (x=500, y=300)
        top_pixel = img.getpixel((500, 10))
        card_pixel = img.getpixel((500, 300))
        frames[theme_name] = (top_pixel, card_pixel)

    # Verify that different themes produce different colors
    theme_colors = list(frames.values())
    # All themes should have unique top/card pixel combinations
    assert len(set(theme_colors)) == len(frames), "Each theme must render distinctive colors"
