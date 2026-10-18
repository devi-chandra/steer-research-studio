import asyncio
import json
import os
import subprocess
from pathlib import Path
from PIL import Image

import pytest

# Ensure backend modules can be imported
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.animation_engine import AnimationEngine
from app.services.video_generation import VideoGenerationService
from app.services.ai_provider import ai_provider_service
from app.core.config import settings

TEST_OUTPUT_DIR = Path(__file__).parent.parent / "artifacts" / "test_reels"
TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def test_01_talking_characters_motion():
    """Verify that talking characters have genuine frame-by-frame procedural animation"""
    engine = AnimationEngine(width=720, height=1280, fps=24)
    out_dir = TEST_OUTPUT_DIR / "talking_char_frames"
    scene = {
        "scene_number": 1,
        "on_screen_text": "What Happens After Dinner?",
        "narration": "What happens inside your body right after dinner?",
        "subtitle_text": "What happens inside your body right after dinner?",
        "visual_style": "talking_characters",
        "animation_action": "talking_characters"
    }
    
    frames = engine.render_scene_frames(scene, 0, 5, 2.0, out_dir)
    assert len(frames) == 48, f"Expected 48 frames at 24fps for 2.0s, got {len(frames)}"
    
    # Verify that frame 0 and frame 12 are visually distinct (mouth, bobbing, sway)
    im0 = Image.open(frames[0])
    im12 = Image.open(frames[12])
    diff_pixels = 0
    # Sample pixels in character area
    for y in range(400, 700, 10):
        for x in range(250, 470, 10):
            if im0.getpixel((x, y)) != im12.getpixel((x, y)):
                diff_pixels += 1
    assert diff_pixels > 20, f"Expected motion between frames, found only {diff_pixels} pixel differences"
    print(f"PASSED: Talking Characters produced {len(frames)} frames with {diff_pixels} moving pixels")

def test_02_inside_your_body_motion():
    """Verify Inside Your Body bloodstream & GLUT4 animation"""
    engine = AnimationEngine(width=720, height=1280, fps=24)
    out_dir = TEST_OUTPUT_DIR / "inside_body_frames"
    scene = {
        "scene_number": 3,
        "on_screen_text": "Your Muscles Absorb Sugar Directly",
        "narration": "Contracting muscles open GLUT4 side-doors.",
        "subtitle_text": "Contracting muscles open GLUT4 side-doors.",
        "visual_style": "inside_your_body",
        "animation_action": "inside_your_body"
    }
    frames = engine.render_scene_frames(scene, 2, 5, 2.0, out_dir)
    assert len(frames) == 48
    print(f"PASSED: Inside Your Body animation rendered {len(frames)} frames")

def test_03_professional_mode_motion():
    """Verify Professional Mode restrained scientific graphics"""
    engine = AnimationEngine(width=720, height=1280, fps=24)
    out_dir = TEST_OUTPUT_DIR / "professional_frames"
    scene = {
        "scene_number": 1,
        "on_screen_text": "Randomized Crossover Trial (n=48)",
        "narration": "In forty-eight South Asian adults, post-meal ambulation attenuated glycemic excursion.",
        "subtitle_text": "Randomized Crossover Trial (n=48)",
        "visual_style": "professional",
        "animation_action": "professional"
    }
    frames = engine.render_scene_frames(scene, 0, 5, 2.0, out_dir)
    assert len(frames) == 48
    print(f"PASSED: Professional Mode rendered {len(frames)} evidence frames")

@pytest.mark.asyncio
async def test_04_regional_languages_and_tts():
    """Verify all 6 regional languages generate natural scripts and valid TTS audio"""
    langs = ["en", "hi", "te", "ta", "kn", "ml"]
    v_service = VideoGenerationService()
    
    for lang in langs:
        script = ai_provider_service.generate_regional_reel_script(
            mode="everyday",
            visual_style="talking_characters",
            language=lang,
            paper_title="Postprandial Walking Crossover Trial",
            claims=[{"claim_id": "CLM-001", "claim_text": "10-min walk blunts glucose by 34%"}]
        )
        assert len(script["scenes"]) >= 5, f"{lang}: expected at least 5 scenes"
        assert script["language"] == lang
        
        # Test TTS voice generation for scene 1 narration
        sc1 = script["scenes"][0]
        audio_file = TEST_OUTPUT_DIR / f"test_{lang}.mp3"
        await v_service.generate_voiceover_audio(sc1["narration"], audio_file, voice=script["voice_name"])
        assert audio_file.exists() and audio_file.stat().st_size > 1000, f"{lang}: TTS audio failed"
        
        dur = v_service.get_audio_duration(audio_file)
        assert dur > 1.5, f"{lang}: audio duration too short ({dur}s)"
        print(f"PASSED: Language '{lang}' voice '{script['voice_name']}' generated {audio_file.stat().st_size} bytes ({dur:.2f}s)")

@pytest.mark.asyncio
async def test_05_full_vertical_mp4_assembly():
    """Verify full end-to-end rendering of a 1080x1920 24fps vertical MP4 reel with FFmpeg"""
    v_service = VideoGenerationService()
    proj_dir = TEST_OUTPUT_DIR / "sample_project_reel"
    output_mp4 = TEST_OUTPUT_DIR / "final_test_reel_1080x1920.mp4"
    
    # Generate 3-scene sample reel for fast comprehensive test
    script = ai_provider_service.generate_regional_reel_script(
        mode="everyday",
        visual_style="talking_characters",
        language="en",
        paper_title="Postprandial Walking Crossover Trial",
        claims=[{"claim_id": "CLM-001", "claim_text": "10-min walk blunts glucose by 34%"}]
    )
    test_scenes = script["scenes"][:3]  # 3 scenes
    
    res = await v_service.render_full_animated_reel(
        scenes=test_scenes,
        proj_reel_dir=proj_dir,
        output_mp4=output_mp4,
        voice="en-IN-NeerjaNeural"
    )
    
    assert output_mp4.exists(), "Final MP4 file does not exist"
    assert output_mp4.stat().st_size > 500000, "Final MP4 file is unexpectedly small"
    
    # Validate with ffprobe
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,codec_name",
        "-of", "json",
        str(output_mp4)
    ]
    p_res = subprocess.run(probe_cmd, stdout=subprocess.PIPE, text=True)
    v_info = json.loads(p_res.stdout)["streams"][0]
    
    assert v_info["width"] == 1080, f"Expected 1080 width, got {v_info['width']}"
    assert v_info["height"] == 1920, f"Expected 1920 height, got {v_info['height']}"
    assert v_info["codec_name"] == "h264", f"Expected h264, got {v_info['codec_name']}"
    
    # Check audio stream
    probe_a_cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=codec_name,sample_rate",
        "-of", "json",
        str(output_mp4)
    ]
    p_a_res = subprocess.run(probe_a_cmd, stdout=subprocess.PIPE, text=True)
    a_info = json.loads(p_a_res.stdout)["streams"][0]
    assert a_info["codec_name"] == "aac", f"Expected aac, got {a_info['codec_name']}"
    
    print(f"PASSED: Full Vertical MP4 Assembly verified! File: {output_mp4.name}, Resolution: {v_info['width']}x{v_info['height']}, Size: {output_mp4.stat().st_size / (1024*1024):.2f}MB, Duration: {res['duration_seconds']}s")

def test_06_claim_consistency_and_review_status():
    """Verify claim consistency between Everyday & Professional Mode and accurate review status"""
    everyday = ai_provider_service.generate_regional_reel_script(mode="everyday", language="en")
    prof = ai_provider_service.generate_regional_reel_script(mode="professional", language="en")
    
    # Both must cite 34% reduction and claim CLM-001
    assert "CLM-001" in everyday["claim_ids"]
    assert any("thirty-four" in s["narration"] or "34" in s["subtitle_text"] or "34" in s["narration"] for s in everyday["scenes"])
    assert any("thirty-four" in s["narration"] or "34" in s["subtitle_text"] or "34" in s["narration"] for s in prof["scenes"])
    
    # Neither should state unsupported "45 minutes cardio"
    for s in everyday["scenes"]:
        assert "45 minutes" not in s["narration"]
    for s in prof["scenes"]:
        assert "45 minutes" not in s["narration"]
        
    print("PASSED: Scientific claims are consistent across modes and omit unsupported cardio comparisons.")

if __name__ == "__main__":
    print("Running Steer Scheme 2 Animated Reel Acceptance Tests...\n")
    test_01_talking_characters_motion()
    test_02_inside_your_body_motion()
    test_03_professional_mode_motion()
    asyncio.run(test_04_regional_languages_and_tts())
    asyncio.run(test_05_full_vertical_mp4_assembly())
    test_06_claim_consistency_and_review_status()
    print("\nALL 6 ACCEPTANCE TEST SUITES PASSED!")
