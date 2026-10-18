from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

fonts_to_check = [
    "C:/Windows/Fonts/Nirmala.ttf",
    "C:/Windows/Fonts/Nirmalab.ttf",
    "C:/Windows/Fonts/mangal.ttf",
    "C:/Windows/Fonts/gautami.ttf",
    "C:/Windows/Fonts/latha.ttf",
    "C:/Windows/Fonts/tunga.ttf",
    "C:/Windows/Fonts/kartika.ttf",
]

for f in fonts_to_check:
    p = Path(f)
    print(f"{p.name}: {'FOUND' if p.exists() else 'MISSING'}")

# Test drawing regional text with Nirmala.ttf
if Path("C:/Windows/Fonts/Nirmala.ttf").exists():
    im = Image.new("RGB", (400, 200), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("C:/Windows/Fonts/Nirmala.ttf", 20)
    draw.text((10, 10), "Hindi: 10 मिनट की वॉक", font=font, fill=(0, 0, 0))
    draw.text((10, 40), "Telugu: 10 నిమిషాలు నడిస్తే", font=font, fill=(0, 0, 0))
    draw.text((10, 70), "Tamil: 10 நிமிடம் நடைப்பயிற்சி", font=font, fill=(0, 0, 0))
    draw.text((10, 100), "Kannada: 10 ನಿಮಿಷ ವಾಕ್", font=font, fill=(0, 0, 0))
    draw.text((10, 130), "Malayalam: 10 മിനിറ്റ് നടന്നാൽ", font=font, fill=(0, 0, 0))
    im.save("scratch_font_test.png")
    print("Successfully rendered all 5 Indian language scripts into scratch_font_test.png!")
