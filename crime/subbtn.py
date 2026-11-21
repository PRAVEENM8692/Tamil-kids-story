"""Make assets/crime_subscribe.mov: a 640x380 transparent overlay, 7 s, 30 fps. LIKE and SUBSCRIBE buttons bounce in from the left side, a finger taps LIKE
(turns blue, the thumb pops), then taps SUBSCRIBE (turns grey 'SUBSCRIBED', confetti, the bell rings and gets a red '1'), then both slide out.
build.py lays it over the video, bottom-left (plan.json "buttons": [{"sec","cue"}]). Usage: python3 crime/subbtn.py"""
import math, os, random, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont
W, H, FPS, DUR, S = 640, 380, 30, 7.0, 2
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; EMO = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
def emoji(ch, px):
    im = Image.new("RGBA", (136, 128), (0, 0, 0, 0)); ImageDraw.Draw(im).text((0, 0), ch, font=ImageFont.truetype(EMO, 109), embedded_color=True)
    c = im.crop(im.getbbox()); return c.resize((px, int(px * c.height / c.width)), Image.LANCZOS)
THUMB, BELL, HAND = emoji("👍", 56 * S), emoji("🔔", 54 * S), emoji("👆", 64 * S)
F1, F2, F3 = (ImageFont.truetype(BOLD, n * S) for n in (40, 42, 34))
def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def back(x):
    x = min(max(x, 0), 1); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def pill(d, b, fill): d.rounded_rectangle(b, radius=(b[3] - b[1]) // 2, fill=fill)
random.seed(7); CONF = [(random.uniform(-1, 1), random.uniform(0.4, 1.4), random.choice([(255, 214, 51), (255, 255, 255), (229, 25, 31), (30, 136, 229), (76, 175, 80)]), random.uniform(3, 7)) for _ in range(46)]
def press(t, t0): return 1 - 0.09 * math.sin(min(max((t - t0) / 0.25, 0), 1) * math.pi) if t0 <= t < t0 + 0.25 else 1
def scale(b, k): cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2; return [cx - (cx - b[0]) * k, cy - (cy - b[1]) * k, cx + (b[2] - cx) * k, cy + (b[3] - cy) * k]
def frame(t):
    base = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); sh = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(base); ds = ImageDraw.Draw(sh)
    slide = back(t / 0.7) if t < DUR - 0.6 else 1 - ease((t - (DUR - 0.6)) / 0.5)
    dx = int(-(W + 60) * (1 - slide) * S)
    liked, subbed = t >= 1.9, t >= 4.1
    lb = scale([dx + 24 * S, 34 * S, dx + 330 * S, 130 * S], press(t, 1.8)); sb = scale([dx + 24 * S, 160 * S, dx + 456 * S, 266 * S], press(t, 4.0))
    for b, glow in ((lb, (30, 136, 229, 170) if liked else (0, 0, 0, 150)), (sb, (229, 25, 31, 170) if not subbed else (0, 0, 0, 150))):
        ds.rounded_rectangle([b[0], b[1] + 8 * S, b[2], b[3] + 8 * S], radius=(b[3] - b[1]) // 2, fill=glow)
    base = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10 * S)), base); d = ImageDraw.Draw(base)
    # LIKE
    pill(d, lb, (30, 136, 229, 255) if liked else (28, 28, 32, 240)); cy = (lb[1] + lb[3]) / 2
    pop = 1 + 0.35 * math.sin(min(max((t - 1.9) / 0.4, 0), 1) * math.pi) if liked else 1
    th = THUMB.resize((int(THUMB.width * pop), int(THUMB.height * pop)), Image.LANCZOS); base.alpha_composite(th, (int(lb[0] + 30 * S - (th.width - THUMB.width) / 2), int(cy - th.height / 2)))
    d.text((lb[0] + 106 * S, cy), "LIKE", font=F1, fill="white", anchor="lm")
    # SUBSCRIBE
    pill(d, sb, (80, 80, 86, 250) if subbed else (229, 25, 31, 255)); cy2 = (sb[1] + sb[3]) / 2
    d.text((sb[0] + 40 * S, cy2), "SUBSCRIBED" if subbed else "SUBSCRIBE", font=F3 if subbed else F2, fill="white", anchor="lm")
    if subbed:
        ang = 24 * math.sin((t - 4.1) * 24) * max(0, 1 - (t - 4.1) / 1.8)
        b = BELL.rotate(ang, resample=Image.BICUBIC, expand=True); bx, by = int(sb[2] + 18 * S), int(cy2 - b.height / 2); base.alpha_composite(b, (bx, by))
        if t > 4.35:
            r = 15 * S * min(1, (t - 4.35) / 0.2); cx0, cy0 = bx + b.width - 4 * S, by + 8 * S
            d.ellipse([cx0 - r, cy0 - r, cx0 + r, cy0 + r], fill=(229, 25, 31, 255))
            if r > 12 * S: d.text((cx0, cy0), "1", font=ImageFont.truetype(BOLD, 20 * S), fill="white", anchor="mm")
    # confetti
    if t >= 4.1:
        u = t - 4.1
        if u < 1.3:
            ox, oy = (sb[0] + sb[2]) / 2, sb[1]
            for vx, vy, col, sz in CONF:
                x = ox + vx * 230 * S * u; y = oy - vy * 190 * S * u + 330 * S * u * u; a = int(255 * (1 - u / 1.3))
                d.rectangle([x, y, x + sz * S, y + sz * S * 0.6], fill=col[:3] + (a,))
    # finger: arrives, taps LIKE (1.3-2.2), moves, taps SUBSCRIBE (3.4-4.5), leaves
    def fpos(t):
        keys = [(0.9, (dx + 420 * S, 330 * S)), (1.5, (dx + 250 * S, 108 * S)), (2.4, (dx + 250 * S, 108 * S)), (3.5, (dx + 360 * S, 236 * S)), (4.6, (dx + 360 * S, 236 * S)), (5.4, (dx + 560 * S, 370 * S))]
        if t <= keys[0][0] or t >= keys[-1][0]: return None
        for (ta, pa), (tb, pb) in zip(keys, keys[1:]):
            if ta <= t <= tb: e = ease((t - ta) / (tb - ta)); return (pa[0] + (pb[0] - pa[0]) * e, pa[1] + (pb[1] - pa[1]) * e)
    p = fpos(t)
    if p:
        tap = 8 * S * math.sin(min(max((t - 1.75) / 0.3, 0), 1) * math.pi) + 8 * S * math.sin(min(max((t - 3.85) / 0.3, 0), 1) * math.pi)
        base.alpha_composite(HAND, (int(p[0] - HAND.width / 2), int(p[1] - 6 * S + tap)))
    return base.resize((W, H), Image.LANCZOS)
tmp = tempfile.mkdtemp()
for i in range(int(DUR * FPS)): frame(i / FPS).save(f"{tmp}/f{i:04d}.png")
os.makedirs("assets", exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{tmp}/f%04d.png", "-c:v", "qtrle", "-pix_fmt", "argb", "assets/crime_subscribe.mov"], check=True)
for k, tt in (("a", 1.85), ("b", 4.4)): frame(tt).save(f"/tmp/btn_{k}.png")
print("ok")
