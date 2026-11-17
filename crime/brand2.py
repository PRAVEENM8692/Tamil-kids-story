"""Noir 'thrilling suspense' channel art for Solved Crime Files - Tamil: logo (magnifying glass over a glowing red fingerprint, crime tape, SOLVED stamp)
and banner (same mark, city skyline, spotlight beams, tape). English letters only. Writes out/logo2.png, out/banner2.png (+ previews)."""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, features
EN = os.environ.get("EN_FONT") or "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BLACK, INK, RED, DRED, WHITE, YEL, GREEN, TAPE_Y = (8, 8, 12), (18, 18, 26), (226, 24, 52), (120, 8, 24), (255, 255, 255), (253, 224, 71), (34, 197, 94), (250, 204, 21)
os.makedirs("out", exist_ok=True); random.seed(7)
def font(s): return ImageFont.truetype(EN, s)

def radial(w, h, cx, cy, r, inner, outer):
    y, x = np.mgrid[0:h, 0:w]; d = np.clip(np.hypot(x - cx, y - cy) / r, 0, 1)[..., None]
    return Image.fromarray((np.array(inner) * (1 - d) + np.array(outer) * d).astype("uint8"), "RGB").convert("RGBA")
def glow(im, cx, cy, r, color, alpha):
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(ov).ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (alpha,))
    return Image.alpha_composite(im, ov.filter(ImageFilter.GaussianBlur(r * 0.45)))
def vignette(im, strength=0.75):
    w, h = im.size; y, x = np.mgrid[0:h, 0:w]; d = np.hypot((x - w / 2) / (w / 2), (y - h / 2) / (h / 2)) / 1.2
    a = (np.clip(d, 0, 1) ** 2.2 * 255 * strength).astype("uint8"); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); ov.putalpha(Image.fromarray(a, "L")); return Image.alpha_composite(im, ov)
def drop(im, layer, pos, blur=16, off=(10, 18), alpha=150):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); s = Image.new("RGBA", layer.size, (0, 0, 0, 0)); s.paste((0, 0, 0, alpha), (0, 0), layer.split()[3])
    sh.paste(s, (pos[0] + off[0], pos[1] + off[1]), s); im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(blur))); im.paste(layer, pos, layer); return im
def text_glow(im, xy, text, f, fill, gcol, blur=14, gal=200, shadow=True):
    g = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).text(xy, text, font=f, fill=gcol + (gal,)); im = Image.alpha_composite(im, g.filter(ImageFilter.GaussianBlur(blur)))
    d = ImageDraw.Draw(im)
    if shadow: d.text((xy[0] + 5, xy[1] + 6), text, font=f, fill=(0, 0, 0, 255))
    d.text(xy, text, font=f, fill=fill); return im

def tape(length, h, text="CRIME FILES"):
    im = Image.new("RGBA", (length, h), TAPE_Y + (255,)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, length, int(h * 0.09)], fill=(17, 17, 17)); d.rectangle([0, h - int(h * 0.09), length, h], fill=(17, 17, 17))
    f = font(int(h * 0.50)); l, t, r, b = f.getbbox(text); step = (r - l) + int(h * 1.5); x = int(h * 0.4)
    while x < length:
        d.text((x - l, (h - (b - t)) / 2 - t), text, font=f, fill=(17, 17, 17)); cx = x + (r - l) + int(h * 0.75); q = h * 0.16
        d.polygon([(cx, h / 2 - q), (cx + q, h / 2), (cx, h / 2 + q), (cx - q, h / 2)], fill=(17, 17, 17)); x += step
    return im
def stamp(text, size, color=RED):
    f = font(size); l, t, r, b = f.getbbox(text); tw, th = r - l, b - t; p = int(size * 0.30); lw = max(4, size // 9); Wd, Hh = tw + 2 * p + 4 * lw, th + 2 * p + 4 * lw
    im = Image.new("RGBA", (Wd, Hh), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, Wd - 1, Hh - 1], radius=size // 4, fill=(12, 12, 16, 235))
    d.rounded_rectangle([lw // 2, lw // 2, Wd - lw // 2, Hh - lw // 2], radius=size // 5, outline=color, width=lw)
    d.rounded_rectangle([lw * 2, lw * 2, Wd - lw * 2, Hh - lw * 2], radius=size // 7, outline=color, width=max(2, lw // 3))
    d.text(((Wd - tw) / 2 - l, (Hh - th) / 2 - t), text, font=f, fill=color); return im

def fingerprint(S, color, width):
    """Whorl-like concentric ridges with random gaps, on a transparent square."""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = S / 2; n = int(S / (width * 2.4))
    for i in range(2, n):
        r = i * width * 2.4 * 0.5 * 2 / 2.0; rx, ry = r * 0.82, r * 1.0; ox = math.sin(i * 0.55) * width * 0.9; oy = i * 0.22 - n * 0.06
        a = random.uniform(0, 360)
        while a < 360 + 1:
            span = random.uniform(40, 120); gap = random.uniform(5, 16) if i > 4 else 0
            d.arc([c - rx + ox, c - ry + oy, c + rx + ox, c + ry + oy], a, min(a + span, 360 + 200), fill=color, width=width); a += span + gap
            if gap == 0 and a > 360: break
    return im

def mark(S):
    """Magnifying glass over a glowing red fingerprint: the lens shows the print big and bright; outside it is dim. Transparent square of side S."""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); cx, cy, R = int(S * 0.40), int(S * 0.40), int(S * 0.33)
    # handle
    hl = Image.new("RGBA", (S, S), (0, 0, 0, 0)); hd = ImageDraw.Draw(hl); a = math.radians(45); x0, y0 = cx + (R + 6) * math.cos(a), cy + (R + 6) * math.sin(a); x1, y1 = cx + (R + S * 0.30) * math.cos(a), cy + (R + S * 0.30) * math.sin(a)
    hd.line([x0, y0, x1, y1], fill=(52, 54, 66, 255), width=int(S * 0.095)); hd.line([x0 + 3, y0 + 3, x1 - 12, y1 - 12], fill=(100, 104, 120, 255), width=int(S * 0.03))
    hd.line([x0 + (x1 - x0) * 0.55, y0 + (y1 - y0) * 0.55, x1, y1], fill=(24, 24, 32, 255), width=int(S * 0.10)); im = Image.alpha_composite(im, hl)
    # lens interior
    lens = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ld = ImageDraw.Draw(lens); ld.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(30, 6, 14, 255))
    fp = fingerprint(int(R * 2.3), RED + (255,), max(5, int(S * 0.016))); fpg = fp.filter(ImageFilter.GaussianBlur(10))
    lens.alpha_composite(fpg, (cx - fpg.width // 2, cy - fpg.height // 2)); lens.alpha_composite(fp, (cx - fp.width // 2, cy - fp.height // 2))
    m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255); lens.putalpha(Image.composite(lens.split()[3], Image.new("L", (S, S), 0), m))
    im = Image.alpha_composite(im, lens)
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh); sd.pieslice([cx - R * 0.8, cy - R * 0.8, cx + R * 0.8, cy + R * 0.8], 200, 262, fill=(255, 255, 255, 60)); im = Image.alpha_composite(im, sh)
    rd = ImageDraw.Draw(im); w = int(S * 0.045); rd.ellipse([cx - R - w // 2, cy - R - w // 2, cx + R + w // 2, cy + R + w // 2], outline=(70, 72, 86, 255), width=w)
    rd.ellipse([cx - R + w // 3, cy - R + w // 3, cx + R - w // 3, cy + R - w // 3], outline=(150, 154, 170, 255), width=max(3, w // 4)); return im

def beams(W, H, xs, base_y, spread, alpha=26, top=0):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for x in xs: d.polygon([(x - 12, top), (x + 12, top), (x + spread, base_y), (x - spread, base_y)], fill=(255, 255, 255, alpha))
    return ov.filter(ImageFilter.GaussianBlur(26))

def skyline(W, H, y_base, hmax, color=(6, 6, 10)):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); x = -20
    while x < W:
        w = random.randint(110, 240); h = random.randint(int(hmax * 0.3), hmax); d.rectangle([x, y_base - h, x + w, H], fill=color + (255,))
        if random.random() < 0.3: d.rectangle([x + w * 0.45, y_base - h - 60, x + w * 0.55, y_base - h], fill=color + (255,))
        for wy in range(y_base - h + 24, y_base - 10, 38):
            for wx in range(x + 18, x + w - 24, 34):
                if random.random() < 0.09: d.rectangle([wx, wy, wx + 14, wy + 20], fill=(255, 196, 80, 235) if random.random() < 0.8 else (230, 40, 60, 235))
        x += w + random.randint(0, 18)
    return ov

def logo(S=1600):
    im = radial(S, S, S * 0.5, S * 0.45, S * 0.75, (52, 10, 24), BLACK)
    im = Image.alpha_composite(im, beams(S, S, [S * 0.30, S * 0.5, S * 0.70], int(S * 0.8), int(S * 0.20), 22)); im = glow(im, S * 0.45, S * 0.43, S * 0.36, RED, 90)
    tp = tape(int(S * 1.7), int(S * 0.115)).rotate(24, resample=Image.BICUBIC, expand=True); im = drop(im, tp, (int(S / 2 - tp.width / 2), int(S * 0.76 - tp.height / 2)), blur=14, off=(6, 12), alpha=150)
    mk = mark(int(S * 0.96)); im = drop(im, mk, (int(S * 0.02), int(S * 0.0)), blur=24, off=(14, 22), alpha=170)
    st = stamp("SOLVED", int(S * 0.115)).rotate(-12, resample=Image.BICUBIC, expand=True); im = drop(im, st, (int(S * 0.64 - st.width / 2), int(S * 0.76 - st.height / 2) - 6), blur=12, off=(6, 10), alpha=150)
    return vignette(im, 0.55).convert("RGB").resize((800, 800), Image.LANCZOS)

L = logo(); L.save("out/logo2.png")
m = Image.new("L", (800, 800), 0); ImageDraw.Draw(m).ellipse([0, 0, 799, 799], fill=255); pv = Image.new("RGB", (800, 800), (255, 255, 255)); pv.paste(L, (0, 0), m); pv.save("out/logo2_round_preview.png")

W, H = 2560, 1440; sx0, sy0, sw, sh_ = (W - 1546) // 2, (H - 423) // 2, 1546, 423
b = radial(W, H, sx0 + 260, H / 2, W * 0.75, (58, 10, 26), BLACK)
b = Image.alpha_composite(b, beams(W, H, [W * 0.18, W * 0.38, W * 0.62, W * 0.84], int(H * 0.95), 260, 18)); b = glow(b, sx0 + 230, H / 2, 380, RED, 85); b = glow(b, W * 0.88, H * 0.12, 300, (230, 40, 60), 40)
b = Image.alpha_composite(b, skyline(W, H, int(H * 0.99), 330)); 
for yy, ang in ((int(H * 0.15), -3), (int(H * 0.87), 2)):
    tp = tape(W + 400, 92).rotate(ang, resample=Image.BICUBIC, expand=True); b = drop(b, tp, (-200, yy - tp.height // 2), blur=10, off=(4, 8), alpha=150)
mk = mark(470); b = drop(b, mk, (sx0 - 40, sy0 - 28), blur=20, off=(12, 18), alpha=170)
tx = sx0 + 450; avail = sw - 450 - 10; size = 126
while True:
    f1 = font(size); b1, b2 = f1.getbbox("SOLVED"), f1.getbbox("CRIME FILES"); sp = int(size * 0.30); tot = (b1[2] - b1[0]) + sp + (b2[2] - b2[0])
    if tot <= avail or size <= 60: break
    size -= 2
top = min(b1[1], b2[1]); ny = sy0 + 36
b = text_glow(b, (tx - b1[0], ny - top), "SOLVED", f1, RED + (255,), RED, blur=18, gal=230)
b = text_glow(b, (tx + (b1[2] - b1[0]) + sp - b2[0], ny - top), "CRIME FILES", f1, WHITE + (255,), (255, 255, 255), blur=10, gal=90)
d = ImageDraw.Draw(b); bot = max(b1[3], b2[3]); fp_ = font(46); pb = fp_.getbbox("TAMIL"); pw, ph = (pb[2] - pb[0]) + 60, 76; uy = ny + (bot - top) + 34
d.rounded_rectangle([tx, uy, tx + pw, uy + ph], radius=ph // 2, fill=RED); d.text((tx + 30 - pb[0], uy + (ph - (pb[3] - pb[1])) / 2 - pb[1]), "TAMIL", font=fp_, fill=WHITE)
fe = font(42); sub = "TRUE CRIME STORIES IN TAMIL"; eb = fe.getbbox(sub); d.text((tx + pw + 30 - eb[0], uy + (ph - (eb[3] - eb[1])) / 2 - eb[1]), sub, font=fe, fill=YEL)
parts = ["Real cases", "Court verdicts", "How the police cracked them"]; gap = 50; s2 = 42
while True:
    fl = font(s2); ws = [fl.getbbox(x) for x in parts]; tot = sum(w[2] - w[0] for w in ws) + gap * 2
    if tot <= avail - 330 or s2 <= 26: break
    s2 -= 2
x = tx; y = uy + ph + 36
for k, (t, w) in enumerate(zip(parts, ws)):
    d.text((x - w[0], y - min(v[1] for v in ws)), t, font=fl, fill=(235, 235, 240)); x += w[2] - w[0]
    if k < 2: cy = y + s2 * 0.5; d.ellipse([x + gap / 2 - 7, cy - 7, x + gap / 2 + 7, cy + 7], fill=RED); x += gap
st = stamp("CASE SOLVED", 38).rotate(-6, resample=Image.BICUBIC, expand=True); b = drop(b, st, (sx0 + sw - st.width - 12, sy0 + sh_ - st.height - 2), blur=8, off=(4, 6), alpha=150)
b = vignette(b, 0.5).convert("RGB"); b.save("out/banner2.png"); b.crop((sx0, sy0, sx0 + sw, sy0 + sh_)).save("out/banner2_phone_preview.png"); print("done")
