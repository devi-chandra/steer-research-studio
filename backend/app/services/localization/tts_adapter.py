import os
import asyncio
from pathlib import Path
from typing import Dict, Any, Tuple
from app.core.config import settings

VOICE_MAP = {
    "en": "en-US-ChristopherNeural",
    "hi_en": "hi-IN-MadhurNeural",
    "te_en": "te-IN-MohanNeural",
    "ta_en": "ta-IN-ValluvarNeural",
    "kn_en": "kn-IN-GaganNeural",
    "ml_en": "ml-IN-MidhunNeural"
}

GTTS_LANG_MAP = {
    "en": "en",
    "hi_en": "hi",
    "te_en": "te",
    "ta_en": "ta",
    "kn_en": "kn",
    "ml_en": "ml"
}

class TTSAdapter:
    def __init__(self):
        self.provider = settings.TTS_PROVIDER

    async def generate_speech(self, text: str, lang_code: str, output_path: Path, allow_mock: bool = False) -> Tuple[bool, str, str]:
        """
        Generates spoken narration audio (.mp3).
        Uses edge-tts for high quality natural neural voices for Indian regional languages and English.
        Falls back to gTTS if edge-tts network request is temporarily interrupted.
        Returns (success, provider_used, error_or_voice_info).
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if lang_code not in VOICE_MAP and lang_code not in GTTS_LANG_MAP:
            return False, "none", f"Unsupported language or voice code '{lang_code}'. Supported languages: {list(VOICE_MAP.keys())}"

        if allow_mock:
            try:
                import subprocess
                cmd = [
                    "ffmpeg", "-y", "-f", "lavfi",
                    "-i", "anullsrc=r=24000:cl=mono",
                    "-t", "4",
                    "-q:a", "9",
                    "-acodec", "libmp3lame",
                    str(output_path)
                ]
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                return True, "mock-audio", "Mock synthetic audio generated for test environment"
            except Exception as e:
                return False, "none", f"Mock audio synthesis failed: {str(e)}"

        voice = VOICE_MAP.get(lang_code, "en-US-ChristopherNeural")

        # 1. Try edge-tts
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(output_path))
            if output_path.exists() and output_path.stat().st_size > 500:
                return True, "edge-tts", f"Voice: {voice}"
        except Exception as e:
            print(f"[TTSAdapter] edge-tts error for voice {voice}: {e}")

        # 2. Fallback to gTTS
        try:
            from gtts import gTTS
            gtts_lang = GTTS_LANG_MAP.get(lang_code, "en")
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            tts.save(str(output_path))
            if output_path.exists() and output_path.stat().st_size > 500:
                return True, "gTTS", f"Language: {gtts_lang} (Google TTS Fallback)"
        except Exception as e:
            print(f"[TTSAdapter] gTTS fallback error for {lang_code}: {e}")

        # 3. Explicit failure unless mock mode is explicitly requested for testing
        if allow_mock:
            try:
                import subprocess
                cmd = [
                    "ffmpeg", "-y", "-f", "lavfi",
                    "-i", "anullsrc=r=24000:cl=mono",
                    "-t", "4",
                    "-q:a", "9",
                    "-acodec", "libmp3lame",
                    str(output_path)
                ]
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                return True, "mock-audio", "Mock synthetic audio generated for test environment"
            except Exception as e:
                return False, "none", f"Mock audio synthesis failed: {str(e)}"

        return False, "none", f"TTS speech generation failed for language '{lang_code}' (voice '{voice}'). Both neural edge-tts and gTTS services failed."

    async def test_language_voice(self, lang_code: str) -> Dict[str, Any]:
        """
        Tests voice generation for a specific language and returns file details.
        """
        test_phrases = {
            "en": "Welcome to Steer Medical Studio. Verified scientific research transformed into clinical briefings.",
            "hi_en": "Steer Studio mein aapka swagat hai. Scientific evidence ab aasaani se samajhiye.",
            "te_en": "Steer Medical Studio ki swagatham. Verified research ipudu meeru thelusukondi.",
            "ta_en": "Steer Studio virivil puthiya scientific findings ungalukkaaga.",
            "kn_en": "Steer Medical Studio ge swagatha. Namma arogyada bagge scientific vishayagalu.",
            "ml_en": "Steer Studio-ilekk swaagatham. Nammude aarogyathine pattiya puthiya research."
        }

        phrase = test_phrases.get(lang_code, "Steer Medical Studio verified clinical audio.")
        out_file = settings.GENERATED_DIR / "audio" / f"test_voice_{lang_code}.mp3"

        success, provider, details = await self.generate_speech(phrase, lang_code, out_file)
        
        file_size = out_file.stat().st_size if out_file.exists() else 0

        return {
            "language_code": lang_code,
            "success": success,
            "provider_used": provider,
            "details": details,
            "test_phrase": phrase,
            "audio_url": f"/storage/generated/audio/test_voice_{lang_code}.mp3" if success else None,
            "file_size_bytes": file_size
        }

tts_adapter = TTSAdapter()
