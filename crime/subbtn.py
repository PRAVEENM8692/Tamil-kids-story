"""Make the LIKE / SUBSCRIBE overlay clips (transparent .mov, 30 fps) used by build.py (plan.json "buttons": [{"sec","cue","clip"}], clip = both|like|sub, bottom-left):
  assets/crime_subscribe.mov  both buttons, 7 s   (used at the closing line)
  assets/crime_like.mov       LIKE only, 4 s       (used in the middle of the video)
  assets/crime_sub.mov        SUBSCRIBE only, 5 s  (used a little later, so they come one by one)
Buttons bounce in from the left, a finger taps (LIKE turns blue and pops; SUBSCRIBE turns grey 'SUBSCRIBED', confetti, bell rings and gets a red '1'), then they slide out.
Usage: python3 crime/subbtn.py"""
import math, os, random, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont
S = 2
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; EMO = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
def emoji(ch, px):
    im = Image.new("RGBA", (136, 128), (0, 0, 0, 0)); ImageDraw.Draw(im).text((0, 0), ch, font=ImageFont.truetype(EMO, 109), embedded_color=True)
    c = im.crop(im.getbbox()); return c.resize((px, int(px * c.height / c.width)), Image.LANCZOS)
THUMB, BELL, HAND = emoji("👍", 56 * S), emoji("🔔", 54 * S), emoji("👆", 64 * S)
F1, F2, F3 = (ImageFont.truetype(BOLD, n * S) for n in (40, 42, 34)); FB = ImageFont.truetype(BOLD, 20 * S)
def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def back(x): x = min(max(x, 0), 1); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def pill(d, b, fill): d.rounded_rectangle(b, radius=(b[3] - b[1]) // 2, fill=fill)
random.seed(7); CONF = [(random.uniform(-1, 1), random.uniform(0.4, 1.4), random.choice([(255, 214, 51), (255, 255, 255), (229, 25, 31), (30, 136, 229), (76, 175, 80)]), random.uniform(3, 7)) for _ in range(46)]
def press(t, t0): return 1 - 0.09 * math.sin(min(max((t - t0) / 0.25, 0), 1) * math.pi) if t0 <= t < t0 + 0.25 else 1
def scale(b, k): cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2; return [cx - (cx - b[0]) * k, cy - (cy - b[1]) * k, cx + (b[2] - cx) * k, cy + (b[3] - cy) * k]
# per clip: canvas size, duration, tap times (None = button not shown), y shift of the SUBSCRIBE button
CFG = {"both": dict(W=640, H=380, dur=7.0, like=1.8, sub=4.0, oy=0, out="assets/crime_subscribe.mov"),
       "like": dict(W=420, H=170, dur=4.0, like=1.2, sub=None, oy=0, out="assets/crime_like.mov"),
       "sub": dict(W=640, H=190, dur=5.2, like=None, sub=1.2, oy=126, out="assets/crime_sub.mov")}
def frame(t, mode):
    c = CFG[mode]; W, H, DUR, tl, ts = c["W"], c["H"], c["dur"], c["like"], c["sub"]; oy = c["oy"]
    base = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); sh = Image.new("RGBA", base.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    slide = back(t / 0.7) if t < DUR - 0.6 else 1 - ease((t - (DUR - 0.6)) / 0.5)
    dx = int(-(W + 60) * (1 - slide) * S)
    liked, subbed = tl is not None and t >= tl + 0.1, ts is not None and t >= ts + 0.1
    lb = scale([dx + 24 * S, 34 * S, dx + 330 * S, 130 * S], press(t, (tl or 99) - 0.1)); sb = scale([dx + 24 * S, (160 - oy) * S, dx + 456 * S, (266 - oy) * S], press(t, (ts or 99) - 0.1))
    boxes = []
    if tl is not None: boxes.append((lb, (30, 136, 229, 170) if liked else (0, 0, 0, 150)))
    if ts is not None: boxes.append((sb, (0, 0, 0, 150) if subbed else (229, 25, 31, 170)))
    for b, g in boxes: ds.rounded_rectangle([b[0], b[1] + 8 * S, b[2], b[3] + 8 * S], radius=(b[3] - b[1]) // 2, fill=g)
    base = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10 * S)), base); d = ImageDraw.Draw(base)
    if tl is not None:
        pill(d, lb, (30, 136, 229, 255) if liked else (28, 28, 32, 240)); cy = (lb[1] + lb[3]) / 2
        pop = 1 + 0.35 * math.sin(min(max((t - tl) / 0.4, 0), 1) * math.pi) if liked else 1
        th = THUMB.resize((int(THUMB.width * pop), int(THUMB.height * pop)), Image.LANCZOS); base.alpha_composite(th, (int(lb[0] + 30 * S - (th.width - THUMB.width) / 2), int(cy - th.height / 2)))
        d.text((lb[0] + 106 * S, cy), "LIKE", font=F1, fill="white", anchor="lm")
    if ts is not None:
        pill(d, sb, (80, 80, 86, 250) if subbed else (229, 25, 31, 255)); cy2 = (sb[1] + sb[3]) / 2
        d.text((sb[0] + 40 * S, cy2), "SUBSCRIBED" if subbed else "SUBSCRIBE", font=F3 if subbed else F2, fill="white", anchor="lm")
        if subbed:
            u = t - ts; b = BELL.rotate(24 * math.sin(u * 24) * max(0, 1 - u / 1.8), resample=Image.BICUBIC, expand=True); bx, by = int(sb[2] + 18 * S), int(cy2 - b.height / 2); base.alpha_composite(b, (bx, by))
            if u > 0.25:
                r = 15 * S * min(1, (u - 0.25) / 0.2); x0, y0 = bx + b.width - 4 * S, by + 8 * S; d.ellipse([x0 - r, y0 - r, x0 + r, y0 + r], fill=(229, 25, 31, 255))
                if r > 12 * S: d.text((x0, y0), "1", font=FB, fill="white", anchor="mm")
            if u < 1.3:
                ox, oyy = (sb[0] + sb[2]) / 2, sb[1]
                for vx, vy, col, sz in CONF:
                    x = ox + vx * 230 * S * u; y = oyy - vy * 190 * S * u + 330 * S * u * u; d.rectangle([x, y, x + sz * S, y + sz * S * 0.6], fill=col + (int(255 * (1 - u / 1.3)),))
    # finger arrives from the right-bottom, taps each shown button, leaves
    stops = []
    if tl is not None: stops.append((tl, (250, 108)))
    if ts is not None: stops.append((ts, (360, 236 - oy)))
    keys = [(stops[0][0] - 0.9, (stops[0][1][0] + 170, stops[0][1][1] + 222))]
    for k, (tt, pos) in enumerate(stops): keys += [(tt - 0.3, pos), (tt + 0.7, pos)]
    keys.append((keys[-1][0] + 0.8, (keys[-1][1][0] + 200, keys[-1][1][1] + 140)))
    pos = None
    if keys[0][0] < t < keys[-1][0]:
        for (ta, pa), (tb, pb) in zip(keys, keys[1:]):
            if ta <= t <= tb: e = ease((t - ta) / (tb - ta)); pos = ((pa[0] + (pb[0] - pa[0]) * e) * S + dx, (pa[1] + (pb[1] - pa[1]) * e) * S); break
    if pos:
        tap = sum(8 * S * math.sin(min(max((t - (tt - 0.05)) / 0.3, 0), 1) * math.pi) for tt, _ in stops)
        base.alpha_composite(HAND, (int(pos[0] - HAND.width / 2), int(pos[1] - 6 * S + tap)))
    return base.resize((W, H), Image.LANCZOS)
FPS = 30
for mode, c in CFG.items():
    tmp = tempfile.mkdtemp()
    for i in range(int(c["dur"] * FPS)): frame(i / FPS, mode).save(f"{tmp}/f{i:04d}.png")
    os.makedirs("assets", exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{tmp}/f%04d.png", "-c:v", "qtrle", "-pix_fmt", "argb", c["out"]], check=True)
    frame((c["sub"] or c["like"]) + 0.6, mode).save(f"/tmp/btn_{mode}.png"); print(mode, "ok")
