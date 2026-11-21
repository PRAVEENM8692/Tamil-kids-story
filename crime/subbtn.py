"""Make assets/crime_subscribe.mov: a 560x330 transparent overlay, 6 s, 30 fps. A LIKE and a SUBSCRIBE button slide in from the left side,
LIKE is pressed (turns blue), SUBSCRIBE is pressed (turns grey, 'SUBSCRIBED', the bell rings), then both slide out. build.py lays it over the video
(plan.json "buttons": [{"sec","cue"}]), bottom-left. Usage: python3 crime/subbtn.py"""
import math, os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont
W, H, FPS, DUR, S = 560, 330, 30, 6.0, 2
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
EMO = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
def emoji(ch, px):
    im = Image.new("RGBA", (136, 128), (0, 0, 0, 0)); ImageDraw.Draw(im).text((0, 0), ch, font=ImageFont.truetype(EMO, 109), embedded_color=True)
    return im.crop(im.getbbox()).resize((px, int(px * im.crop(im.getbbox()).height / im.crop(im.getbbox()).width)), Image.LANCZOS)
THUMB, BELL = emoji("👍", 46 * S), emoji("🔔", 44 * S)
F1, F2 = ImageFont.truetype(BOLD, 34 * S), ImageFont.truetype(BOLD, 36 * S)
def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def pill(d, box, fill): d.rounded_rectangle(box, radius=(box[3] - box[1]) // 2, fill=fill)
def frame(t):
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    slide = ease(t / 0.55) if t < DUR - 0.6 else 1 - ease((t - (DUR - 0.6)) / 0.5)
    dx = int((-(W + 40) * (1 - slide)) * S)
    liked, subbed = t >= 1.5, t >= 3.0
    # LIKE
    k = 1 - 0.08 * math.sin(min(max((t - 1.4) / 0.25, 0), 1) * math.pi) if 1.4 <= t < 1.65 else 1
    bx = [dx + 20 * S, 28 * S, dx + 270 * S, 108 * S]; cx, cy = (bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2
    bx = [cx - (cx - bx[0]) * k, cy - (cy - bx[1]) * k, cx + (bx[2] - cx) * k, cy + (bx[3] - cy) * k]
    pill(d, bx, (30, 136, 229, 255) if liked else (32, 32, 36, 235))
    im.alpha_composite(THUMB, (int(bx[0] + 22 * S), int(cy - THUMB.height / 2)))
    d.text((bx[0] + 82 * S, cy), "LIKE", font=F1, fill="white", anchor="lm")
    # SUBSCRIBE
    k = 1 - 0.08 * math.sin(min(max((t - 2.9) / 0.25, 0), 1) * math.pi) if 2.9 <= t < 3.15 else 1
    bx = [dx + 20 * S, 138 * S, dx + 360 * S, 222 * S]; cx, cy = (bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2
    bx = [cx - (cx - bx[0]) * k, cy - (cy - bx[1]) * k, cx + (bx[2] - cx) * k, cy + (bx[3] - cy) * k]
    pill(d, bx, (80, 80, 86, 245) if subbed else (229, 25, 31, 255))
    d.text((bx[0] + 36 * S, cy), "SUBSCRIBED" if subbed else "SUBSCRIBE", font=F2 if not subbed else ImageFont.truetype(BOLD, 30 * S), fill="white", anchor="lm")
    if subbed:
        ang = 22 * math.sin((t - 3.0) * 22) * max(0, 1 - (t - 3.0) / 1.6)
        b = BELL.rotate(ang, resample=Image.BICUBIC, expand=True); im.alpha_composite(b, (int(bx[2] + 14 * S), int(cy - b.height / 2)))
    # tap ripples
    for t0, (rx, ry) in ((1.4, (150, 68)), (2.9, (190, 180))):
        r = (t - t0) / 0.5
        if 0 <= r <= 1:
            R = (18 + 40 * r) * S; a = int(150 * (1 - r)); x0, y0 = dx + rx * S, ry * S
            d.ellipse([x0 - R, y0 - R, x0 + R, y0 + R], outline=(255, 255, 255, a), width=4 * S)
    return im.resize((W, H), Image.LANCZOS)
tmp = tempfile.mkdtemp()
for i in range(int(DUR * FPS)): frame(i / FPS).save(f"{tmp}/f{i:04d}.png")
os.makedirs("assets", exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{tmp}/f%04d.png", "-c:v", "qtrle", "-pix_fmt", "argb", "assets/crime_subscribe.mov"], check=True)
frame(2.0).save("/tmp/btn_preview.png"); frame(4.0).save("/tmp/btn_preview2.png"); print("ok")
