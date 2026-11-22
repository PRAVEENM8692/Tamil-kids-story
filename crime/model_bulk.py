"""Draw up to 90 pictures with flux-2-klein-9b (vivid prompt) across both Cloudflare accounts; log how many each account allows."""
import base64, io, json, os, time, urllib.error, urllib.request
from PIL import Image
ACC = [(os.environ.get(a), os.environ.get(b)) for a, b in (("CF_ACCOUNT_ID", "CF_API_TOKEN"), ("CF_ACCOUNT_ID_2", "CF_API_TOKEN_2"))]
ACC = [(i.strip(), t.strip()) for i, t in ACC if i and t]
SH = json.load(open("crime/samayapuram/scenes.json", encoding="utf-8"))["shots"]
VIVID = ("Vibrant colourful graphic-novel comic illustration, bold saturated colours, thick black ink outlines, high contrast dramatic lighting with glowing red, orange and electric teal accents, dynamic low camera angle, rich detailed background, eye-catching movie-poster look, cinematic. ")
END = " Clean floor, calm tidy scene. Nothing cut off at the frame edges. No text, no letters, no numbers, no captions, no watermark, no border."
os.makedirs("out", exist_ok=True); cur = 0; cnt = [0] * len(ACC); log = open("out/log.txt", "w")
def say(s): print(s); log.write(s + "\n"); log.flush()
n = 0
while n < 90 and cur < len(ACC):
    sc = SH[n % len(SH)]["scene"]; i, t = ACC[cur]; b = "----bb7f"
    parts = {"prompt": (VIVID + sc + END)[:2000], "width": "1280", "height": "720"}
    body = "".join(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n' for k, v in parts.items()).encode() + f"--{b}--\r\n".encode()
    req = urllib.request.Request(f"https://api.cloudflare.com/client/v4/accounts/{i}/ai/run/@cf/black-forest-labs/flux-2-klein-9b", body, {"Authorization": f"Bearer {t}", "Content-Type": f"multipart/form-data; boundary={b}"})
    try:
        raw = base64.b64decode(json.load(urllib.request.urlopen(req, timeout=240))["result"]["image"])
        Image.open(io.BytesIO(raw)).convert("RGB").save(f"out/{n+1:02d}.jpg", quality=85); cnt[cur] += 1; n += 1
        if n % 10 == 0: say(f"{n} drawn, account counts {cnt}")
    except urllib.error.HTTPError as e:
        m = e.read()[:300]; say(f"HTTP {e.code} at picture {n+1}, account {cur+1}: {m!r}")
        if e.code == 429: cur += 1
        else: time.sleep(5)
    except Exception as e: say(f"err {e}"); time.sleep(5)
say(f"DONE total {n}, per account {cnt}")
