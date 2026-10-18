"""Machine-checkable production checks for rendered social assets.

Pixel checks catch missing, incorrectly sized, or nearly blank files. They do
not assess medical accuracy or replace a visual review by a person.
"""
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from PIL import Image, ImageStat


class AssetQualityService:
    EXPECTED_SIZES = {"carousel_slide": (1080, 1350), "static_post": (1080, 1350)}

    @staticmethod
    def _image_report(path: Path, expected: tuple[int, int], asset_type: str) -> Dict[str, Any]:
        if not path.exists():
            return {"asset_type": asset_type, "path": str(path), "status": "missing", "checks": []}
        try:
            with Image.open(path) as image:
                image.load()
                size = image.size
                rgb = image.convert("RGB")
                extrema = ImageStat.Stat(rgb).stddev
                checks = [
                    {"name": "dimensions", "status": "passed" if size == expected else "flagged",
                     "expected": list(expected), "actual": list(size)},
                    {"name": "visible-content", "status": "passed" if max(extrema) > 8 else "flagged",
                     "details": "Image has visible tonal variation." if max(extrema) > 8 else "Image appears nearly blank or flat."},
                ]
                return {"asset_type": asset_type, "path": str(path), "status": "passed" if all(c["status"] == "passed" for c in checks) else "flagged",
                        "format": image.format, "mode": image.mode, "size": list(size), "checks": checks}
        except Exception as exc:
            return {"asset_type": asset_type, "path": str(path), "status": "error", "error": str(exc), "checks": []}

    @staticmethod
    def _video_report(path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {"asset_type": "reel_video", "path": str(path), "status": "missing", "checks": []}
        command = ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,codec_name:format=duration,size", "-of", "json", str(path)]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=15, check=True)
            data = json.loads(result.stdout)
            streams = data.get("streams", [])
            video = next((s for s in streams if s.get("codec_type") == "video"), {})
            audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
            size_ok = (video.get("width"), video.get("height")) == (1080, 1920)
            duration = float(data.get("format", {}).get("duration", 0))
            checks = [
                {"name": "vertical-resolution", "status": "passed" if size_ok else "flagged", "expected": [1080, 1920], "actual": [video.get("width"), video.get("height")]},
                {"name": "duration", "status": "passed" if duration >= 5 else "flagged", "actual_seconds": duration},
                {"name": "audio-track", "status": "passed" if audio else "flagged", "details": "Audio stream present." if audio else "No audio stream found."},
            ]
            return {"asset_type": "reel_video", "path": str(path), "status": "passed" if all(c["status"] == "passed" for c in checks) else "flagged",
                    "duration_seconds": duration, "video_codec": video.get("codec_name"), "audio_codec": audio.get("codec_name") if audio else None, "checks": checks}
        except Exception as exc:
            return {"asset_type": "reel_video", "path": str(path), "status": "error", "error": str(exc), "checks": []}

    def inspect_project(self, project_dir: Path) -> Dict[str, Any]:
        reports: List[Dict[str, Any]] = []
        carousel_dir = project_dir / "carousel" / "slides"
        slides = sorted(carousel_dir.glob("slide_*.png")) if carousel_dir.exists() else []
        if slides:
            reports.extend(self._image_report(p, self.EXPECTED_SIZES["carousel_slide"], "carousel_slide") for p in slides)
        else:
            reports.append({"asset_type": "carousel_slide", "status": "missing", "checks": []})
        reports.append(self._image_report(project_dir / "static_post.png", self.EXPECTED_SIZES["static_post"], "static_post"))
        reports.append(self._video_report(project_dir / "reel" / "final_reel.mp4"))
        flagged = sum(r["status"] != "passed" for r in reports)
        return {
            "overall_status": "review_required" if flagged else "passed",
            "assets_checked": len(reports),
            "flagged_assets": flagged,
            "reports": reports,
            "human_review_required": True,
            "limits": "Automated checks cover file presence, dimensions, visible tonal variation, video duration, and audio track. They do not assess clipping, legibility, visual polish, source accuracy, or clinical safety; inspect every slide and subtitle manually.",
        }


asset_quality_service = AssetQualityService()
