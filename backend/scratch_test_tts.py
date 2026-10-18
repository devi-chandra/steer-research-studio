import asyncio
import edge_tts
from pathlib import Path

test_samples = [
    ("en", "en-IN-NeerjaNeural", "Did you know that taking a gentle 10-minute walk right after dinner blunts your blood sugar spike by 34 percent?"),
    ("hi", "hi-IN-SwaraNeural", "क्या आप जानते हैं कि डिनर के ठीक बाद सिर्फ 10 मिनट की वॉक आपके ब्लड शुगर स्पाइक को 34 परसेंट तक कम कर सकती है?"),
    ("te", "te-IN-ShrutiNeural", "డిన్నర్ తిన్న వెంటనే కేవలం 10 నిమిషాలు నడిస్తే బ్లడ్ షుగర్ స్పైక్ 34 శాతం తగ్గుతుందని మీకు తెలుసా?"),
    ("ta", "ta-IN-PallaviNeural", "சாப்பிட்ட உடனே வெறும் 10 நிமிடம் நடைப்பயிற்சி செய்தால் ரத்த சர்க்கரை அளவு 34 சதவீதம் குறையும் என்று தெரியுமா?"),
    ("kn", "kn-IN-SapnaNeural", "ಊಟವಾದ ತಕ್ಷಣ ಕೇವಲ 10 ನಿಮಿಷ ವಾಕ್ ಮಾಡಿದರೆ ರಕ್ತದಲ್ಲಿನ ಸಕ್ಕರೆ ಪ್ರಮಾಣ 34 ಪ್ರತಿಶತ ಕಡಿಮೆಯಾಗುತ್ತದೆ ಎಂದು ನಿಮಗೆ ತಿಳಿದಿದೆಯೇ?"),
    ("ml", "ml-IN-SobhanaNeural", "ഭക്ഷണത്തിന് ശേഷം വെറും 10 മിനിറ്റ് നടന്നാൽ രക്തത്തിലെ പഞ്ചസാരയുടെ അളവ് 34 ശതമാനം കുറയുമെന്ന് അറിയാമോ?")
]

async def test_all():
    out_dir = Path("scratch_tts_tests")
    out_dir.mkdir(exist_ok=True)
    for lang, voice, text in test_samples:
        out_file = out_dir / f"test_{lang}.mp3"
        print(f"Synthesizing {lang} with {voice}...")
        comm = edge_tts.Communicate(text, voice)
        await comm.save(str(out_file))
        print(f" -> {lang} saved ({out_file.stat().st_size} bytes)")

if __name__ == '__main__':
    asyncio.run(test_all())
