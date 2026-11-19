"""Draw realistic thumbnail pictures (16:9) with Google Gemini image models using GEMINI_API_KEY. Tries the models in order and prints exactly which worked.
Prompts come from crime/<case>/thumb_prompts.json: {"a": "...", "b": "..."}. Output: out/thumb_<key>.jpg. No real person's likeness is ever requested."""
import base64, io, json, os, sys, requests
from PIL import Image
CASE = os.environ["CASE"]; KEY = os.environ["GEMINI_API_KEY"]
MODELS = [m for m in os.environ.get("MODELS", "gemini-2.5-flash-image,gemini-3.1-flash-image-preview,gemini-3-pro-image-preview,gemini-2.0-flash-preview-image-generation,gemini-2.0-flash-exp-image-generation").split(",") if m]
P = json.load(open(f"crime/{CASE}/thumb_prompts.json", encoding="utf-8")); os.makedirs("out", exist_ok=True)
SUFFIX = " Photorealistic cinematic photograph, 16:9 wide frame, dramatic moody lighting, shallow depth of field, no text, no letters, no logos, no watermark, no identifiable real person, faces not visible."
ok = 0
for k, prompt in P.items():
    done = False
    for m in MODELS:
        body = {"contents": [{"parts": [{"text": prompt + SUFFIX}]}], "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9"}}}
        r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent", headers={"x-goog-api-key": KEY}, json=body, timeout=180)
        if r.status_code >= 400:
            print(f"[{k}] {m}: HTTP {r.status_code} {r.text[:160].replace(chr(10), ' ')}"); continue
        img = None
        for c in r.json().get("candidates", []):
            for p in c.get("content", {}).get("parts", []):
                d = p.get("inlineData") or p.get("inline_data")
                if d: img = base64.b64decode(d["data"])
        if not img: print(f"[{k}] {m}: no image returned"); continue
        im = Image.open(io.BytesIO(img)).convert("RGB"); print(f"[{k}] {m}: OK {im.size}")
        im = im.resize((1280, 720)) if abs(im.width / im.height - 16 / 9) < 0.02 else im.resize((1280, int(1280 * im.height / im.width))).crop((0, max(0, (int(1280 * im.height / im.width) - 720) // 2), 1280, max(0, (int(1280 * im.height / im.width) - 720) // 2) + 720))
        im.save(f"out/thumb_{k}.jpg", quality=92); ok += 1; done = True; break
    if not done: print(f"[{k}] no model worked")
print("pictures made:", ok)
