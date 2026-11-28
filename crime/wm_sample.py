"""Watermark style samples: 'தமிழ் க்ரைம் ஸ்டோரி' at centre-right on a sample frame (3 colour styles)."""
import glob, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
bg = Image.open("crime/vijayawada/test_img.jpg").convert("RGB").resize((1920, 1080))
cands = glob.glob("/usr/share/fonts/truetype/noto/NotoSansTamil-*Bold.ttf") + glob.glob("/usr/share/fonts/truetype/noto/NotoSansTamil-Black.ttf")
cands.sort(key=lambda p: ("Black" not in p, "ExtraBold" not in p))
FONT = cands[0] if cands else "/usr/share/fonts/truetype/noto/NotoSansTamil-Bold.ttf"
print("font", FONT)
T = "தமிழ் க்ரைம் ஸ்டோரி"
STYLES = {"gold": ((255, 238, 130), (255, 150, 30), (255, 170, 60)),
          "cyan": ((200, 255, 250), (60, 200, 255), (80, 210, 255)),
          "red": ((255, 215, 190), (255, 90, 70), (255, 110, 80))}
os.makedirs("out", exist_ok=True)
for name, (c1, c2, ln) in STYLES.items():
    F = ImageFont.truetype(FONT, 56, layout_engine=ImageFont.Layout.RAQM)
    l, tp, r, b = F.getbbox(T); w, h = r - l + 24, b - tp + 24
    mask = Image.new("L", (w, h), 0); ImageDraw.Draw(mask).text((12 - l, 12 - tp), T, font=F, fill=255)
    g = np.zeros((h, w, 3), np.uint8)
    for y in range(h):
        k = y / h; g[y, :] = [int(c1[i] + (c2[i] - c1[i]) * k) for i in range(3)]
    col = Image.fromarray(g).convert("RGBA"); col.putalpha(mask.point(lambda v: int(v * 0.8)))
    sh = Image.new("L", (w + 40, h + 40), 0); sh.paste(mask.point(lambda v: int(v * 0.7)), (20, 24)); sh = sh.filter(ImageFilter.GaussianBlur(5))
    x, y = 1920 - w - 44, (1080 - h) // 2
    lay = bg.convert("RGBA"); blk = Image.new("RGBA", sh.size, (0, 0, 0, 255)); blk.putalpha(sh); lay.alpha_composite(blk, (x - 20, y - 20))
    lay.alpha_composite(col, (x, y))
    ImageDraw.Draw(lay, "RGBA").rounded_rectangle((x + 12, y + h, x + w - 12, y + h + 3), 2, fill=ln + (170,))
    lay.convert("RGB").save(f"out/wm_{name}.jpg", quality=92)
