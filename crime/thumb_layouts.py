"""Crime thumbnails with DIFFERENT layouts (not the banner pattern). 1280x720.
python crime/thumb_layouts.py LAYOUT OUT EPISODE_NO TITLE LINE2 PIC1 [PIC2]
LAYOUT = board (evidence board, tilted paper title) | circle (red circle on the key clue + yellow callout) | split (two scenes, diagonal split, bottom bar)"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
lay, out, ep, title, line2, pic1 = sys.argv[1:7]; pic2 = sys.argv[7] if len(sys.argv) > 7 else None
CALL = sys.argv[8] if len(sys.argv) > 8 else ""
TAM = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"; LAT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W, H = 1280, 720; YEL = (255, 214, 51); RED = (205, 20, 28)
def load(p): return ImageEnhance.Contrast(ImageEnhance.Color(Image.open(p).convert("RGB").resize((W, H))).enhance(1.2)).enhance(1.12)
def fit(t, f, s, w):
    while ImageFont.truetype(f, s).getlength(t) > w: s -= 4
    return ImageFont.truetype(f, s)
def tilted(text, fnt, fg, bg, pad, angle, stroke=0, strokec=(0, 0, 0)):
    b = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), text, font=fnt, stroke_width=stroke)
    w, h = b[2] - b[0] + pad * 2, b[3] - b[1] + pad * 2
    t = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    if bg: d.rectangle((0, 0, w, h), fill=bg)
    d.text((pad - b[0], pad - b[1]), text, font=fnt, fill=fg, stroke_width=max(stroke, 2), stroke_fill=fg if not stroke else strokec)
    return t.rotate(angle, expand=True, resample=Image.BICUBIC)
def paste(im, t, xy):
    sh = Image.new("RGBA", t.size, (0, 0, 0, 0)); sh.putalpha(t.split()[3].point(lambda v: min(160, v)))
    sh = Image.merge("RGBA", (Image.new("L", t.size, 0),) * 3 + (sh.split()[3],)).filter(ImageFilter.GaussianBlur(6))
    im.paste(sh, (xy[0] + 8, xy[1] + 10), sh); im.paste(t, xy, t)
def tag(d, txt, xy, bg=(15, 15, 18), fg=(255, 255, 255), s=30):
    f = ImageFont.truetype(TAM if any(ord(c) > 127 for c in txt) else LAT, s + (8 if any(ord(c) > 127 for c in txt) else 0)); b = d.textbbox(xy, txt, font=f); d.rounded_rectangle((b[0] - 14, b[1] - 8, b[2] + 14, b[3] + 8), 10, fill=bg); d.text(xy, txt, font=f, fill=fg)
if lay == "board":
    im = load(pic1).convert("RGBA"); v = Image.new("RGBA", (W, H), (0, 0, 0, 0)); vd = ImageDraw.Draw(v)
    for i in range(160): vd.rectangle((0, i, W, i + 1), fill=(0, 0, 0, int(150 * (1 - i / 160))))
    im = Image.alpha_composite(im, v)
    t1 = title.split("\n"); y = 24
    for k, t in enumerate(t1):
        paste(im, tilted(t, fit(t, TAM, 96, 640), (15, 15, 18), (255, 232, 130), 18, 2 if k == 0 else -2), (36 + 20 * k, y)); y += 138
    paste(im, tilted(line2, fit(line2, TAM, 64, 560), (255, 255, 255), RED, 18, -3), (60, y + 4))
    im = im.convert("RGB"); d = ImageDraw.Draw(im); tag(d, f"CASE {ep}", (W - 190, 34), bg=RED); tag(d, "SOLVED CRIME FILES - TAMIL", (28, H - 62), s=24)
elif lay == "circle":
    im = load(pic1); d = ImageDraw.Draw(im, "RGBA")
    for i in range(260): d.rectangle((0, i, W, i + 1), fill=(0, 0, 0, int(200 * (1 - i / 260))))
    f = fit(max(title.split("\n"), key=len), TAM, 104, W - 270); d.multiline_text((40, 14), title, font=f, fill=(255, 255, 255), stroke_width=9, stroke_fill=(0, 0, 0), spacing=4)
    cx, cy, rx, ry = [int(x) for x in (CALL.split("|")[0] if CALL else "700,545,150,70").split(",")]
    for k in range(7): d.ellipse((cx - rx - k, cy - ry - k, cx + rx + k, cy + ry + k), outline=RED, width=3)
    d.line((cx, cy - ry - 8, cx + 60, 330), fill=YEL, width=5)
    cal = tilted(line2, fit(line2, TAM, 60, 470), (15, 15, 18), YEL, 20, 2); paste(im, cal, (cx - 20, 250))
    tag(d, f"CASE {ep}", (W - 190, 34), bg=RED); tag(d, "SOLVED CRIME FILES - TAMIL", (28, H - 62), s=24)
else:
    a, b = load(pic1), load(pic2); m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon([(0, 0), (700, 0), (560, H), (0, H)], fill=255)
    im = Image.composite(a, b, m); d = ImageDraw.Draw(im, "RGBA"); d.line((700, 0, 560, H), fill=(255, 255, 255), width=10)
    d.rectangle((0, 0, W, 230), fill=(0, 0, 0, 175)); f = fit(max(title.split("\n"), key=len), TAM, 100, W - 80); d.multiline_text((W // 2, 116), title, font=f, fill=YEL, anchor="mm", align="center", stroke_width=8, stroke_fill=(0, 0, 0), spacing=6)
    d.rectangle((0, H - 120, W, H), fill=(0, 0, 0, 190)); f = fit(line2, TAM, 66, W - 340); d.text((W // 2 - 90, H - 60), line2, font=f, fill=(255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=(0, 0, 0))
    l, r = (CALL.split("|") + ["", ""])[:2] if CALL else ("", "")
    if l: tag(d, l, (40, 262), bg=RED, s=34)
    if r: tag(d, r, (W - 60 - int(ImageFont.truetype(TAM, 42).getlength(r)), 262), bg=RED, s=34)
    tag(d, f"CASE {ep}", (W - 190, H - 100), bg=RED, s=26)
im.save(out, quality=93)
