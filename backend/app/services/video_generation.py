import asyncio
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from app.core.config import settings

class VideoGenerationService:
    def __init__(self):
        self.width = settings.VIDEO_WIDTH  # 1080
        self.height = settings.VIDEO_HEIGHT  # 1920
        self.fps = settings.VIDEO_FPS

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

    def render_scene_frame(self, scene: Dict[str, Any], total_scenes: int, output_path: Path) -> Path:
        """
        Renders a premium 1080x1920 vertical visual frame for an AI-assisted reel scene.
        Includes clinical metadata, hook typography, and safe margins for Instagram Reel UI.
        """
        img = Image.new("RGB", (self.width, self.height), color=self.c_cream)
        draw = ImageDraw.Draw(img)

        # Elegant Editorial Inner Container
        margin_x = 55
        margin_y = 100
        draw.rounded_rectangle(
            [margin_x, margin_y, self.width - margin_x, self.height - margin_y],
            radius=40,
            fill=self.c_soft_paper,
            outline=self.c_blush,
            width=3
        )

        scene_num = scene.get("scene_number", 1)

        # Top Progress Segments (Instagram Stories / Reels style)
        seg_y = margin_y + 40
        seg_w = (self.width - (margin_x * 2) - 80 - ((total_scenes - 1) * 12)) // total_scenes
        seg_start_x = margin_x + 40
        for i in range(total_scenes):
            color = self.c_rust if i < scene_num else self.c_blush
            draw.rounded_rectangle(
                [seg_start_x + (i * (seg_w + 12)), seg_y, seg_start_x + (i * (seg_w + 12)) + seg_w, seg_y + 8],
                radius=4,
                fill=color
            )

        # Header Badge & Reel Title
        header_y = seg_y + 45
        font_badge = self._get_font("sans_bold", 26)
        draw.rounded_rectangle([seg_start_x, header_y, seg_start_x + 380, header_y + 50], radius=25, fill=self.c_blush)
        draw.text((seg_start_x + 28, header_y + 10), "STEER CLINICAL REEL", font=font_badge, fill=self.c_maroon)

        font_counter = self._get_font("sans_bold", 28)
        draw.text((self.width - margin_x - 180, header_y + 10), f"PART {scene_num:02d}/{total_scenes:02d}", font=font_counter, fill=self.c_clay)

        # Eyebrow / Scene Label
        eyebrow_y = header_y + 110
        font_eyebrow = self._get_font("sans_bold", 32)
        eyebrow_text = f"SCENE {scene_num} • METABOLIC SCIENCE PROTOCOL"
        draw.text((seg_start_x, eyebrow_y), eyebrow_text, font=font_eyebrow, fill=self.c_rust)

        # On-Screen Headline Text
        headline = scene.get("on_screen_text", "Metabolic Health Insight")
        font_headline = self._get_font("serif_bold", 72)
        lines = self._wrap_text(headline, font_headline, self.width - 240, draw)
        
        cur_y = eyebrow_y + 65
        for line in lines:
            draw.text((seg_start_x, cur_y), line, font=font_headline, fill=self.c_ink)
            cur_y += 88

        cur_y += 40

        # Visual Cue / Description Card (Illustrates the clinical insight)
        cue_box_top = cur_y
        cue_box_bottom = cue_box_top + 280
        draw.rounded_rectangle(
            [seg_start_x, cue_box_top, self.width - seg_start_x, cue_box_bottom],
            radius=24,
            fill=self.c_cream,
            outline=self.c_clay,
            width=2
        )

        font_cue_lbl = self._get_font("sans_bold", 24)
        font_cue_txt = self._get_font("serif", 36)
        draw.text((seg_start_x + 35, cue_box_top + 30), "CLINICAL OBSERVATION & VISUAL ACTION", font=font_cue_lbl, fill=self.c_rust)
        
        visual_cue = scene.get("visual_cue", "Observation of metabolic response.")
        cue_lines = self._wrap_text(visual_cue, font_cue_txt, self.width - (seg_start_x * 2) - 70, draw)
        c_y = cue_box_top + 80
        for l in cue_lines[:3]:
            draw.text((seg_start_x + 35, c_y), l, font=font_cue_txt, fill=self.c_ink)
            c_y += 50

        # Doctor Guidance Card (Lower Middle)
        guidance_top = cue_box_bottom + 45
        guidance_bottom = min(guidance_top + 380, self.height - 320)
        draw.rounded_rectangle(
            [seg_start_x, guidance_top, self.width - seg_start_x, guidance_bottom],
            radius=24,
            fill="#FFF9F4",
            outline=self.c_blush,
            width=2
        )

        font_dr_hdr = self._get_font("sans_bold", 26)
        font_dr_body = self._get_font("serif", 38)
        draw.text((seg_start_x + 35, guidance_top + 28), "STEER DOCTOR NARRATION", font=font_dr_hdr, fill=self.c_maroon)
        
        narration = scene.get("narration", "")
        narr_lines = self._wrap_text(narration, font_dr_body, self.width - (seg_start_x * 2) - 70, draw)
        n_y = guidance_top + 82
        for nl in narr_lines[:5]:
            draw.text((seg_start_x + 35, n_y), nl, font=font_dr_body, fill=self.c_ink)
            n_y += 52

        # Subtitle Safe Zone Box (Bottom 260px - High contrast for video overlay)
        sub_top = self.height - 290
        sub_bottom = self.height - 130
        draw.rounded_rectangle(
            [seg_start_x, sub_top, self.width - seg_start_x, sub_bottom],
            radius=20,
            fill=self.c_ink
        )

        subtitle = scene.get("subtitle_text") or scene.get("narration", "")
        font_sub = self._get_font("sans_bold", 34)
        sub_lines = self._wrap_text(subtitle, font_sub, self.width - (seg_start_x * 2) - 60, draw)
        
        sub_y = sub_top + 30
        for sl in sub_lines[:2]:
            # Centered subtitle
            bbox = draw.textbbox((0, 0), sl, font=font_sub)
            sw = bbox[2] - bbox[0]
            draw.text(((self.width - sw) // 2, sub_y), sl, font=font_sub, fill="#FFFFFF")
            sub_y += 46

        # Source footer
        clm_tags = " • ".join(scene.get("claim_ids", []))
        font_foot = self._get_font("sans", 22)
        draw.text((seg_start_x + 10, self.height - 110), f"Doctor-Led Metabolic Research • {clm_tags}", font=font_foot, fill=self.c_clay)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(output_path), "PNG", quality=95)
        return output_path

    def get_audio_duration(self, audio_path: Path) -> float:
        """Probes the exact duration of an audio file in seconds via ffprobe"""
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(audio_path)
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            if res.returncode == 0 and res.stdout.strip():
                return float(res.stdout.strip())
        except Exception as e:
            print(f"[Probe] Error getting audio duration: {e}")
        return 5.0

    async def generate_voiceover_audio(self, narration_text: str, output_audio_path: Path, voice: Optional[str] = None) -> Path:
        """
        Generates realistic voiceover audio using edge-tts with the specified regional voice.
        Falls back to pyttsx3 or generates tone track if offline.
        """
        output_audio_path.parent.mkdir(parents=True, exist_ok=True)
        selected_voice = voice or settings.TTS_VOICE
        
        # 1. Try edge-tts with selected voice (using energetic +15% rate suited for Reels)
        try:
            communicate = edge_tts.Communicate(narration_text, selected_voice, rate="+15%")
            await communicate.save(str(output_audio_path))
            if output_audio_path.exists() and output_audio_path.stat().st_size > 500:
                return output_audio_path
        except Exception as e:
            print(f"[TTS] edge-tts error with voice {selected_voice}: {e}")
            # Try alternate voice for the same language (NEVER silently replace regional with English)
            voice_fallbacks = {
                "hi-IN-SwaraNeural": "hi-IN-MadhurNeural",
                "hi-IN-MadhurNeural": "hi-IN-SwaraNeural",
                "te-IN-ShrutiNeural": "te-IN-MohanNeural",
                "te-IN-MohanNeural": "te-IN-ShrutiNeural",
                "ta-IN-PallaviNeural": "ta-IN-ValluvarNeural",
                "ta-IN-ValluvarNeural": "ta-IN-PallaviNeural",
                "kn-IN-SapnaNeural": "kn-IN-GaganNeural",
                "kn-IN-GaganNeural": "kn-IN-SapnaNeural",
                "ml-IN-SobhanaNeural": "ml-IN-MidhunNeural",
                "ml-IN-MidhunNeural": "ml-IN-SobhanaNeural",
                "en-IN-NeerjaNeural": "en-IN-PrabhatNeural",
                "en-IN-PrabhatNeural": "en-IN-NeerjaNeural",
            }
            alt_voice = voice_fallbacks.get(selected_voice)
            if alt_voice:
                try:
                    communicate = edge_tts.Communicate(narration_text, alt_voice, rate="+15%")
                    await communicate.save(str(output_audio_path))
                    if output_audio_path.exists() and output_audio_path.stat().st_size > 500:
                        return output_audio_path
                except Exception as e2:
                    print(f"[TTS] alternate regional voice {alt_voice} error: {e2}")

        # 2. Try pyttsx3 offline system voice
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 145)
            engine.save_to_file(narration_text, str(output_audio_path))
            engine.runAndWait()
            if output_audio_path.exists() and output_audio_path.stat().st_size > 500:
                return output_audio_path
        except Exception as e:
            print(f"[TTS] pyttsx3 error: {e}. Creating synthetic audio via ffmpeg...")

        # 3. Fallback: Generate subtle audio track with ffmpeg so MP4 has valid audio
        cmd = [
            settings.FFMPEG_PATH,
            "-y",
            "-f", "lavfi",
            "-i", "sine=frequency=300:duration=5",
            "-af", "volume=0.05",
            "-c:a", "aac",
            str(output_audio_path)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_audio_path

    async def render_animated_scene(
        self,
        scene: Dict[str, Any],
        scene_idx: int,
        total_scenes: int,
        proj_reel_dir: Path,
        voice: Optional[str] = None,
        force_reencode: bool = False
    ) -> Dict[str, Any]:
        """
        Renders an authentic 24fps animated scene:
        1. Synthesizes voiceover narration in specified regional voice
        2. Probes exact spoken audio duration
        3. Renders multi-frame procedural animation with AnimationEngine
        4. Compiles scene frames + audio into vertical 1080x1920 MP4
        """
        from app.services.animation_engine import AnimationEngine
        anim_engine = AnimationEngine(width=720, height=1280, fps=24)

        scene_num = scene.get("scene_number", scene_idx + 1)
        scene_dir = proj_reel_dir / f"scene_{scene_num:02d}"
        scene_dir.mkdir(parents=True, exist_ok=True)

        audio_path = scene_dir / "narration.mp3"
        scene_mp4 = scene_dir / f"scene_{scene_num:02d}.mp4"
        thumb_path = scene_dir / "thumbnail.png"

        # 1. Generate Voiceover Audio
        narration = scene.get("narration", "")
        await self.generate_voiceover_audio(narration, audio_path, voice=voice)

        # 2. Get Spoken Audio Duration
        dur = self.get_audio_duration(audio_path)
        # Ensure minimum duration so viewer can comfortably absorb visual action
        dur = max(3.5, round(dur, 2))
        scene["duration_seconds"] = dur

        # 3. Render Procedural Animation Frames (24fps)
        frames_dir = scene_dir / "frames"
        if frames_dir.exists():
            for f in frames_dir.glob("*.png"):
                try:
                    f.unlink()
                except Exception:
                    pass

        frames = anim_engine.render_scene_frames(
            scene=scene,
            scene_idx=scene_idx,
            total_scenes=total_scenes,
            duration_seconds=dur,
            out_dir=frames_dir
        )

        # Copy mid frame as thumbnail
        if frames:
            mid_frame = frames[len(frames) // 2]
            try:
                import shutil
                shutil.copy(str(mid_frame), str(thumb_path))
            except Exception:
                pass

        # 4. Compile Scene MP4 (1080x1920, 24fps, H.264 / AAC)
        cmd = [
            settings.FFMPEG_PATH, "-y",
            "-framerate", "24",
            "-i", str(frames_dir / "frame_%04d.png").replace("\\", "/"),
            "-i", str(audio_path).replace("\\", "/"),
            "-vf", "scale=1080:1920:flags=lanczos,format=yuv420p",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            str(scene_mp4).replace("\\", "/")
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0 or not scene_mp4.exists():
            print(f"[FFmpeg] Scene {scene_num} encode error: {res.stderr}")
            raise RuntimeError(f"Scene {scene_num} video encoding failed: {res.stderr}")

        return {
            "scene_number": scene_num,
            "duration_seconds": dur,
            "scene_mp4": str(scene_mp4),
            "audio_path": str(audio_path),
            "thumbnail_path": str(thumb_path),
            "frame_count": len(frames)
        }

    async def render_full_animated_reel(
        self,
        scenes: List[Dict[str, Any]],
        proj_reel_dir: Path,
        output_mp4: Path,
        voice: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Renders all animated scenes, builds authoritative render manifest with
        exact timeline timestamps, and concatenates them into a finished vertical 9:16 MP4 reel.
        """
        import json
        proj_reel_dir.mkdir(parents=True, exist_ok=True)
        total_scenes = len(scenes)
        scene_mp4s = []
        scene_manifests = []
        cumulative_time = 0.0

        for idx, scene in enumerate(scenes):
            start_sec = round(cumulative_time, 2)
            scene_res = await self.render_animated_scene(
                scene=scene,
                scene_idx=idx,
                total_scenes=total_scenes,
                proj_reel_dir=proj_reel_dir,
                voice=voice
            )
            scene_mp4s.append(Path(scene_res["scene_mp4"]))
            dur = scene_res["duration_seconds"]
            end_sec = round(start_sec + dur, 2)
            cumulative_time = end_sec

            # Calculate formatted timeline range e.g. "00:00 - 00:12 (12s)"
            start_fmt = f"{int(start_sec//60):02d}:{int(start_sec%60):02d}"
            end_fmt = f"{int(end_sec//60):02d}:{int(end_sec%60):02d}"
            time_range = f"{start_fmt} - {end_fmt} ({round(dur)}s)"

            scene["duration_seconds"] = dur
            scene["start_time_seconds"] = start_sec
            scene["end_time_seconds"] = end_sec
            scene["time_range"] = time_range
            scene["render_status"] = "completed"

            scene_manifests.append({
                "scene_id": f"scene_{scene.get('scene_number', idx+1):02d}",
                "order": idx + 1,
                "scene_number": scene.get("scene_number", idx + 1),
                "title": scene.get("title") or scene.get("on_screen_text") or f"Scene {idx+1}",
                "start_time_seconds": start_sec,
                "end_time_seconds": end_sec,
                "start_time_formatted": start_fmt,
                "end_time_formatted": end_fmt,
                "time_range": time_range,
                "actual_duration_seconds": dur,
                "script": scene.get("narration"),
                "narration": scene.get("narration"),
                "subtitle_text": scene.get("subtitle_text"),
                "visual_cue": scene.get("visual_cue"),
                "thumbnail_file": str(Path(scene_res["thumbnail_path"]).name),
                "video_file": str(Path(scene_res["scene_mp4"]).name),
                "render_status": "completed"
            })

        # Concatenate scene MP4s via FFmpeg concat demuxer
        concat_txt = proj_reel_dir / "concat_reel.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for mp4 in scene_mp4s:
                safe_path = str(mp4).replace("\\", "/")
                f.write(f"file '{safe_path}'\n")

        concat_cmd = [
            settings.FFMPEG_PATH, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_txt).replace("\\", "/"),
            "-c", "copy",
            "-movflags", "+faststart",
            str(output_mp4).replace("\\", "/")
        ]
        res = subprocess.run(concat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0 or not output_mp4.exists() or output_mp4.stat().st_size < 1000:
            # Fallback re-encode if concat copy failed
            cmd_reencode = [
                settings.FFMPEG_PATH, "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_txt).replace("\\", "/"),
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-c:a", "aac",
                "-movflags", "+faststart",
                str(output_mp4).replace("\\", "/")
            ]
            res_re = subprocess.run(cmd_reencode, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res_re.returncode != 0:
                raise RuntimeError(f"FFmpeg reel concat failed: {res_re.stderr}")

        # Authoritative Render Manifest
        manifest_data = {
            "version": "1.0",
            "resolution": "1080x1920",
            "aspect_ratio": "9:16",
            "fps": 24,
            "total_duration_seconds": round(cumulative_time, 2),
            "total_scenes": total_scenes,
            "video_file": str(output_mp4.name),
            "file_size_bytes": output_mp4.stat().st_size if output_mp4.exists() else 0,
            "scenes": scene_manifests
        }

        manifest_path = proj_reel_dir / "render_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as mf:
            json.dump(manifest_data, mf, indent=2)

        return {
            "status": "success",
            "video_path": str(output_mp4),
            "width": 1080,
            "height": 1920,
            "fps": 24,
            "duration_seconds": round(cumulative_time, 2),
            "file_size_bytes": output_mp4.stat().st_size if output_mp4.exists() else 0,
            "scene_count": total_scenes,
            "manifest": manifest_data,
            "manifest_path": str(manifest_path)
        }

video_generation_service = VideoGenerationService()
