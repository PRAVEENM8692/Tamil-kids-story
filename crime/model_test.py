"""Compare image models for the crime comic pictures on the same scenes. Writes out/<variant>_<n>.jpg and out/log.txt"""
import base64, io, json, os, time, urllib.error, urllib.request, requests
from PIL import Image
CF_ID, CF_TOKEN = os.environ.get("CF_ACCOUNT_ID"), os.environ.get("CF_API_TOKEN"); GKEY = os.environ.get("GEMINI_API_KEY")
SC = {s["n"]: s["scene"] for s in json.load(open("crime/samayapuram/scenes.json", encoding="utf-8"))["shots"]}
NS = [1, 31]
OLD = ("Indian crime comic book illustration, bold clean black ink outlines, flat colours with soft cel shading, muted vintage palette of sepia, teal and amber, dramatic film-noir lighting, richly detailed background, expressive faces, cinematic. ")
VIVID = ("Vibrant colourful graphic-novel comic illustration, bold saturated colours, thick black ink outlines, high contrast dramatic lighting with glowing red, orange and electric teal accents, dynamic low camera angle, rich detailed background, eye-catching movie-poster look, cinematic. ")
END = " Clean floor, calm tidy scene. Nothing cut off at the frame edges. No text, no letters, no numbers, no captions, no watermark, no border."
os.makedirs("out", exist_ok=True); log = open("out/log.txt", "w")
def say(*a):
    s = " ".join(str(x) for x in a); print(s); log.write(s + "\n"); log.flush()
def cf(model, prompt, dst, extra=None):
    b = "----bnd7f3a"; parts = {"prompt": prompt[:2000], "width": "1280", "height": "720"}; parts.update(extra or {})
    body = "".join(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n' for k, v in parts.items()).encode() + f"--{b}--\r\n".encode()
    req = urllib.request.Request(f"https://api.cloudflare.com/client/v4/accounts/{CF_ID}/ai/run/@cf/black-forest-labs/{model}", body, {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": f"multipart/form-data; boundary={b}"})
    t = time.time()
    try:
        raw = base64.b64decode(json.load(urllib.request.urlopen(req, timeout=240))["result"]["image"])
        im = Image.open(io.BytesIO(raw)).convert("RGB"); im.save(dst, quality=90); say("OK", dst, im.size, round(time.time() - t, 1), "s")
    except urllib.error.HTTPError as e: say("FAIL", dst, e.code, e.read()[:200])
    except Exception as e: say("FAIL", dst, str(e)[:200])
def gem(prompt, dst):
    body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9"}}}
    r = requests.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent", headers={"x-goog-api-key": GKEY}, json=body, timeout=180)
    if r.status_code >= 400: say("FAIL", dst, r.status_code, r.text[:200].replace("\n", " ")); return
    for c in r.json().get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            d = p.get("inlineData") or p.get("inline_data")
            if d: Image.open(io.BytesIO(base64.b64decode(d["data"]))).convert("RGB").resize((1280, 720)).save(dst, quality=90); say("OK", dst); return
    say("FAIL", dst, "no image")
for n in NS:
    sc = SC[n]
    cf("flux-2-klein-4b", OLD + sc + END, f"out/1_klein4b_old_{n}.jpg")
    cf("flux-2-klein-4b", VIVID + sc + END, f"out/2_klein4b_vivid_{n}.jpg")
    cf("flux-2-klein-9b", VIVID + sc + END, f"out/3_klein9b_vivid_{n}.jpg")
    cf("flux-2-dev", VIVID + sc + END, f"out/4_fluxdev_vivid_{n}.jpg", {"steps": "20"})
    if GKEY: gem(VIVID + sc + END + " 16:9 wide frame.", f"out/5_gemini_vivid_{n}.jpg")
