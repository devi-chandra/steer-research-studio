import time
from pathlib import Path
from PIL import Image, ImageDraw

def test_render():
    t0 = time.time()
    frames = []
    width, height = 720, 1280  # fast high-def vertical preview
    out_dir = Path("scratch_test_frames")
    out_dir.mkdir(exist_ok=True)
    
    for i in range(48):  # 2 seconds at 24fps
        im = Image.new("RGB", (width, height), (245, 235, 223))
        draw = ImageDraw.Draw(im)
        # draw a bobbing circle (character head)
        y = 500 + int(20 * (i % 12 - 6))
        draw.ellipse([width//2 - 120, y - 120, width//2 + 120, y + 120], fill=(192, 78, 42))
        # mouth
        mouth_open = (i % 6 < 3)
        if mouth_open:
            draw.ellipse([width//2 - 30, y + 20, width//2 + 30, y + 50], fill=(53, 29, 29))
        else:
            draw.line([width//2 - 30, y + 35, width//2 + 30, y + 35], fill=(53, 29, 29), width=5)
        im.save(out_dir / f"frame_{i:04d}.png")
    
    dur = time.time() - t0
    print(f"Rendered 48 frames in {dur:.2f} seconds ({48/dur:.1f} fps)")

if __name__ == '__main__':
    test_render()
