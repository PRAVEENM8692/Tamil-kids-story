"""Tamil crime story channel: draw the story pictures with the free Cloudflare Workers AI FLUX schnell model.
Env: CF_ACCOUNT_ID, CF_API_TOKEN. ONLY = scene numbers to draw (comma separated, empty = all still missing). Writes out/NN.jpg."""
import base64, io, json, os, time, urllib.error, urllib.request

ACCTS = [(i.strip(), t.strip()) for i, t in ((os.environ.get("CF_ACCOUNT_ID"), os.environ.get("CF_API_TOKEN")), (os.environ.get("CF_ACCOUNT_ID_2"), os.environ.get("CF_API_TOKEN_2"))) if i and t]
CUR = 0     # index of the Cloudflare account in use; moves to the next one when the daily free limit (HTTP 429, code 4006) is hit
CF_ID, CF_TOKEN = ACCTS[0] if ACCTS else (None, None)
SCENES = os.environ.get("SCENES") or "crime/alavandar/scenes.json"
STYLE = os.environ.get("PIC_STYLE") or ("Photorealistic cinematic photograph, shot on a full-frame camera, 35mm lens, natural realistic colours, true-to-life lighting and textures, real Indian location, moody documentary crime-news look, any person only seen from behind or in silhouette with the face not visible. ")
MODEL = os.environ.get("IMG_MODEL") or "flux-2-klein-4b"
END = " Clean floor, calm tidy scene. Nothing cut off at the frame edges. No text, no letters, no numbers, no captions, no watermark, no border."

def draw(prompt, dst):
    global CUR
    from PIL import Image
    last = None
    for n in range(4 + len(ACCTS)):
        CF_ID, CF_TOKEN = ACCTS[CUR]
        url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ID}/ai/run/@cf/black-forest-labs/{MODEL}"
        try:
            b = "----crimeboundary7f3a"
            parts = {"prompt": prompt[:2000], "width": "1280", "height": "720"}
            body = "".join(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n' for k, v in parts.items()).encode() + f"--{b}--\r\n".encode()
            req = urllib.request.Request(url, body, {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": f"multipart/form-data; boundary={b}"})
            raw = base64.b64decode(json.load(urllib.request.urlopen(req, timeout=180))["result"]["image"])
            Image.open(io.BytesIO(raw)).convert("RGB").save(dst, quality=90)
            return True
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read()[:300]!r}"
            if e.code == 429 and "4006" in last and CUR + 1 < len(ACCTS):
                CUR += 1; print(f"account {CUR} hit the daily limit, switching to account {CUR + 1}"); continue
        except Exception as e: last = str(e)
        time.sleep(4 * (n + 1))
    print("picture failed:", last); return False

if not ACCTS:
    raise SystemExit("CF_ACCOUNT_ID / CF_API_TOKEN secrets are not set on this repo (Settings > Secrets and variables > Actions)")
redo = {int(x) for x in (os.environ.get("REDO") or "").replace(" ", "").split(",") if x}
only = {int(x) for x in (os.environ.get("ONLY") or "").replace(" ", "").split(",") if x}
os.makedirs("out", exist_ok=True)
done, fails = [], 0
for s in json.load(open(SCENES, encoding="utf-8"))["shots"]:
    f = f"out/{s['n']:02d}.jpg"
    if s["n"] in redo and os.path.exists(f): os.remove(f)
    if (only and s["n"] not in only) or (not only and os.path.exists(f)): continue
    style = STYLE + "Objects only, absolutely no people, no faces, no portraits. " if s["scene"].startswith(("Still life", "A clean anatomy", "Empty")) else STYLE
    ok = draw(style + s["scene"] + END, f)
    if ok: done.append(s["n"]); fails = 0; print(f"picture {s['n']:02d} drawn")
    else:
        fails += 1
        if fails >= 3: print("3 failures in a row (daily free limit?), stopping"); break
print("drawn:", done)
if not done: raise SystemExit("no pictures were drawn")
