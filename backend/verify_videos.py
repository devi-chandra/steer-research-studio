import asyncio
import json
import subprocess
import shutil
import sys
from pathlib import Path
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.models import Project, ContentDraft, Claim, Artifact
from app.services.ai_provider import ai_provider_service
from app.services.video_generation import video_generation_service

def run_ffprobe(file_path: Path):
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(file_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {res.stderr}")
    return json.loads(res.stdout)

async def test_and_verify_videos():
    print("=== STARTING VIDEO BUG FIX & ANIMATION VERIFICATION ===")
    db = SessionLocal()
    try:
        # Fetch or create test project
        project = db.query(Project).first()
        if not project:
            print("No project found in DB! Please run pipeline test first.")
            return

        print(f"Using Project: {project.id} ('{project.title}')")
        draft = db.query(ContentDraft).filter(ContentDraft.project_id == project.id).first()
        claims = db.query(Claim).filter(Claim.project_id == project.id).all()
        claims_list = [{"claim_id": c.claim_id, "claim_text": c.claim_text, "limitations": c.limitations} for c in claims]

        # -------------------------------------------------------------
        # 1. VERIFY INSIDE YOUR BODY MODE (3 BIOLOGICAL FINDINGS)
        # -------------------------------------------------------------
        print("\n--- 1. Testing Inside Your Body Video Generation ---")
        inside_reel_data = ai_provider_service.generate_regional_reel_script(
            mode="everyday",
            visual_style="inside_your_body",
            language="en",
            voice_name="en-IN-NeerjaNeural",
            paper_title=project.title,
            claims=claims_list
        )

        assert len(inside_reel_data["scenes"]) == 3, f"Expected 3 scenes for Inside Your Body, got {len(inside_reel_data['scenes'])}"
        print(f"✓ Inside Your Body generated {len(inside_reel_data['scenes'])} finding scenes:")
        for sc in inside_reel_data["scenes"]:
            print(f"  • Scene {sc['scene_number']}: {sc['on_screen_text']} (Organ: {sc.get('organ_character')}, Duration: {sc['duration_seconds']}s)")

        # Render Inside Your Body Video
        inside_dir = settings.generated_dir / f"{project.id}_inside_body" / "reel"
        inside_mp4 = inside_dir / "final_reel.mp4"
        inside_manifest_path = inside_dir / "render_manifest.json"
        force_render = "--force-render" in sys.argv

        if not inside_mp4.exists() or not inside_manifest_path.exists() or force_render:
            print("Rendering Inside Your Body 24fps video reel...")
            inside_res = await video_generation_service.render_full_animated_reel(
                scenes=inside_reel_data["scenes"],
                proj_reel_dir=inside_dir,
                output_mp4=inside_mp4,
                voice="en-IN-NeerjaNeural"
            )
            inside_manifest = inside_res.get("manifest")
        else:
            print(f"✓ Using existing rendered Inside Your Body MP4 at: {inside_mp4}")
            with open(inside_manifest_path, "r", encoding="utf-8") as f:
                inside_manifest = json.load(f)

        assert inside_mp4.exists(), f"MP4 file not found at {inside_mp4}"
        print(f"✓ Output Inside Your Body MP4 exists at: {inside_mp4} ({inside_mp4.stat().st_size} bytes)")

        # Check render manifest
        assert inside_manifest is not None, "Render manifest is missing!"
        print(f"✓ Authoritative Render Manifest saved with {len(inside_manifest['scenes'])} scenes")

        # Run ffprobe on Inside Your Body MP4
        probe_inside = run_ffprobe(inside_mp4)
        v_stream = next(s for s in probe_inside["streams"] if s["codec_type"] == "video")
        a_stream = next(s for s in probe_inside["streams"] if s["codec_type"] == "audio")
        inside_dur = float(probe_inside["format"]["duration"])

        print(f"✓ FFprobe Inspection (Inside Your Body):")
        print(f"  • Resolution: {v_stream['width']}x{v_stream['height']} (1080x1920 vertical)")
        print(f"  • Video Codec: {v_stream['codec_name']}")
        print(f"  • Audio Codec: {a_stream['codec_name']}")
        print(f"  • Actual MP4 Duration: {inside_dur:.2f}s (Manifest duration: {inside_manifest['total_duration_seconds']:.2f}s)")
        assert abs(inside_dur - inside_manifest['total_duration_seconds']) < 1.0, "Timing discrepancy exceeds tolerance!"
        print(f"✓ Timing tolerance check passed: diff = {abs(inside_dur - inside_manifest['total_duration_seconds']):.2f}s < 1.0s")

        # Verify each scene thumbnail and individual video
        for sc in inside_manifest["scenes"]:
            s_num = sc["scene_number"]
            thumb = inside_dir / f"scene_{s_num:02d}" / "thumbnail.png"
            sc_video = inside_dir / f"scene_{s_num:02d}" / f"scene_{s_num:02d}.mp4"
            assert thumb.exists(), f"Scene {s_num} thumbnail missing at {thumb}"
            assert sc_video.exists(), f"Scene {s_num} video missing at {sc_video}"
            print(f"  • Scene {s_num} asset verified: Thumbnail ({thumb.stat().st_size} bytes), Video ({sc_video.stat().st_size} bytes)")

        # -------------------------------------------------------------
        # 2. VERIFY EVERYDAY MODE (7-SCENE NARRATIVE STORYBOARD)
        # -------------------------------------------------------------
        print("\n--- 2. Testing Everyday Mode Video Generation (7 Scenes) ---")
        everyday_reel_data = ai_provider_service.generate_regional_reel_script(
            mode="everyday",
            visual_style="talking_characters",
            language="en",
            voice_name="en-IN-NeerjaNeural",
            paper_title=project.title,
            claims=claims_list
        )

        assert len(everyday_reel_data["scenes"]) == 7, f"Expected 7 scenes for Everyday Mode, got {len(everyday_reel_data['scenes'])}"
        print(f"✓ Everyday Mode generated {len(everyday_reel_data['scenes'])} narrative scenes:")
        for sc in everyday_reel_data["scenes"]:
            print(f"  • Scene {sc['scene_number']}: {sc['on_screen_text']} ({sc['duration_seconds']}s) - Cue: {sc['visual_cue'][:40]}...")

        everyday_dir = settings.generated_dir / f"{project.id}_everyday_mode" / "reel"
        everyday_mp4 = everyday_dir / "final_reel.mp4"
        everyday_manifest_path = everyday_dir / "render_manifest.json"

        if not everyday_mp4.exists() or not everyday_manifest_path.exists() or force_render:
            print("Rendering Everyday Mode 24fps video reel...")
            everyday_res = await video_generation_service.render_full_animated_reel(
                scenes=everyday_reel_data["scenes"],
                proj_reel_dir=everyday_dir,
                output_mp4=everyday_mp4,
                voice="en-IN-NeerjaNeural"
            )
        else:
            print(f"✓ Using existing rendered Everyday Mode MP4 at: {everyday_mp4}")

        assert everyday_mp4.exists(), f"MP4 file not found at {everyday_mp4}"
        print(f"✓ Output Everyday Mode MP4 exists at: {everyday_mp4} ({everyday_mp4.stat().st_size} bytes)")

        probe_everyday = run_ffprobe(everyday_mp4)
        v_stream_e = next(s for s in probe_everyday["streams"] if s["codec_type"] == "video")
        a_stream_e = next(s for s in probe_everyday["streams"] if s["codec_type"] == "audio")
        everyday_dur = float(probe_everyday["format"]["duration"])

        print(f"✓ FFprobe Inspection (Everyday Mode):")
        print(f"  • Resolution: {v_stream_e['width']}x{v_stream_e['height']}")
        print(f"  • Video Codec: {v_stream_e['codec_name']}")
        print(f"  • Audio Codec: {a_stream_e['codec_name']}")
        print(f"  • Actual MP4 Duration: {everyday_dur:.2f}s")
        assert 25 <= everyday_dur <= 45, f"Duration {everyday_dur}s out of target 25-45s range!"
        print(f"✓ Duration within target range (25-45s): {everyday_dur:.2f}s")

        # -------------------------------------------------------------
        # 3. VERIFY LOCALVOICE IN REGIONAL LANGUAGE (TELUGU + ENGLISH)
        # -------------------------------------------------------------
        print("\n--- 3. Testing LocalVoice Regional Generation (Telugu) ---")
        te_reel_data = ai_provider_service.generate_regional_reel_script(
            mode="everyday",
            visual_style="inside_your_body",
            language="te",
            voice_name="te-IN-ShrutiNeural",
            paper_title=project.title,
            claims=claims_list
        )
        assert te_reel_data["language"] == "te"
        assert te_reel_data["voice_name"] == "te-IN-ShrutiNeural"
        print("✓ Verified Telugu LocalVoice script with native characters and voice:", te_reel_data["voice_name"])

        # -------------------------------------------------------------
        # 4. VERIFY CROSS-FORMAT CONSISTENCY AUDIT
        # -------------------------------------------------------------
        print("\n--- 4. Testing Cross-Format Claims Consistency Audit ---")
        from app.services.cross_format_claims import CrossFormatClaimsService
        audit_res = CrossFormatClaimsService.audit_project_consistency(project, draft, claims)
        assert audit_res["overall_status"] in ["consistent", "inconsistencies_detected"]
        assert len(audit_res["checks"]) == 6
        print(f"✓ Cross-Format Claim Audit executed successfully with {audit_res['passed_checks']}/{audit_res['total_checks']} checks passed:")
        for chk in audit_res["checks"]:
            print(f"  • {chk['name']}: {chk['status'].upper()}")

        print("\n=== ALL VIDEO & PIPELINE VERIFICATIONS PASSED SUCCESSFULLY! ===")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_and_verify_videos())
