"""Hype-style thumbnail 1280x720 (red headline banner, white second banner, red arrow, comic picture).
python crime/thumb_hype.py PICTURE OUT "EPISODE 4" "BANNER1" "BANNER2" [ARROW_X ARROW_Y]"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
pic, out, tag, b1, b2 = sys.argv[1:6]
ax, ay = (int(sys.argv[6]), int(sys.argv[7])) if len(sys.argv) > 7 else (760, 470)
FLIP = len(sys.argv) > 8 and sys.argv[8].upper() == "L"   # arrow comes from the right and points left
TAMIL = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"; SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W, H = 1280, 720; YEL = (255, 214, 51); RED = (200, 16, 24)
import os
THEME = os.environ.get("THEME", "red")   # red (default) or yellow: rotate the design, keep the pattern
B1BG, B1FG, B2BG, B2FG = ((RED, YEL, (250, 250, 250), (170, 10, 20)) if THEME != "yellow" else (YEL, (170, 10, 20), (15, 15, 20), (255, 255, 255)))
src = Image.open(pic).convert("RGB"); src = src.crop((14, 14, src.width - 14, src.height - 14)).resize((W, H))
im = ImageEnhance.Contrast(ImageEnhance.Color(src).enhance(1.25)).enhance(1.15); d = ImageDraw.Draw(im)
def fit(t, p, s, w):
    while ImageFont.truetype(p, s).getlength(t) > w: s -= 4
    return ImageFont.truetype(p, s)
# banner 1: red with yellow text
d.rectangle((0, 0, W, 150), fill=B1BG); d.rectangle((0, 150, W, 158), fill=(255, 255, 255))
f = fit(b1, TAMIL, 118, W - 60); d.text((W // 2, 78), b1, font=f, fill=B1FG, anchor="mm", stroke_width=6, stroke_fill=(60, 0, 0) if THEME != "yellow" else (255, 255, 255))
# banner 2: white with black/red text
d.rectangle((0, 158, W, 262), fill=B2BG); d.rectangle((0, 262, W, 268), fill=(0, 0, 0))
f = fit(b2, TAMIL, 96, W - 60); d.text((W // 2, 212), b2, font=f, fill=B2FG, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
# big red arrow pointing at the action
arrow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); a = ImageDraw.Draw(arrow)
a.polygon([(ax - 330, ay + 90), (ax - 330, ay + 30), (ax - 130, ay + 30), (ax - 130, ay - 30), (ax, ay + 55), (ax - 130, ay + 140), (ax - 130, ay + 80)], fill=(230, 20, 25, 255), outline=(255, 255, 255, 255))
arrow = arrow.transpose(Image.FLIP_LEFT_RIGHT) if FLIP else arrow
im = Image.alpha_composite(im.convert("RGBA"), arrow).convert("RGB"); d = ImageDraw.Draw(im)
# episode tag and channel badge
d.rounded_rectangle((24, 292, 304, 362), 14, fill=YEL); d.text((164, 327), tag, font=ImageFont.truetype(SANS, 36), fill=(20, 20, 20), anchor="mm")
d.rounded_rectangle((24, 640, 520, 700), 10, fill=(10, 10, 20)); d.text((272, 670), "SOLVED CRIME FILES - TAMIL", font=ImageFont.truetype(SANS, 28), fill=YEL, anchor="mm")
im.save(out, quality=92)
