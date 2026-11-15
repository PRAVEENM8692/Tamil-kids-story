"""Tamil crime story channel: draw the story pictures with the free Cloudflare Workers AI FLUX schnell model.
Env: CF_ACCOUNT_ID, CF_API_TOKEN. ONLY = scene numbers to draw (comma separated, empty = all still missing). Writes out/NN.jpg."""
import base64, io, json, os, sys, time, urllib.error, urllib.request

CF_ID, CF_TOKEN = os.environ.get("CF_ACCOUNT_ID"), os.environ.get("CF_API_TOKEN")
SCENES = os.environ.get("SCENES") or "crime/alavandar/scenes.json"
STYLE = ("Indian crime comic book illustration, bold clean black ink outlines, flat colours with soft cel shading, "
         "muted vintage palette of sepia, teal and amber, dramatic film-noir lighting, richly detailed background, expressive faces, cinematic. ")
END = " Clean floor, calm tidy scene. Nothing cut off at the frame edges. No text, no letters, no numbers, no captions, no watermark, no border."

def draw_pollinations(prompt, dst, seed):
    """Free, no key: pollinations.ai FLUX, drawn 16:9 (1280x720)."""
    from PIL import Image
    import urllib.parse
    last = None
    for n in range(4):
        try:
            u = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt[:1500]) + f"?width=1280&height=720&model=flux&nologo=true&private=true&seed={seed + n}"
            raw = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=240).read()
            im = Image.open(io.BytesIO(raw)).convert("RGB")
            if im.width < 800: raise ValueError(f"unexpected size {im.size}")
            im.save(dst, quality=90); return True
        except urllib.error.HTTPError as e: last = f"HTTP {e.code}: {e.read()[:200]!r}"
        except Exception as e: last = str(e)
        time.sleep(8 * (n + 1))
    print("picture failed:", last); return False

def draw(prompt, dst):
    from PIL import Image
    klein = (os.environ.get("MODEL") or "klein") != "schnell"      # default: FLUX.2 klein 4B drawn 16:9 (1280x720), about 105 neurons a picture; MODEL=schnell: FLUX.1 schnell, square, about 170
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ID}/ai/run/@cf/black-forest-labs/" + ("flux-2-klein-4b" if klein else "flux-1-schnell")
    last = None
    for n in range(4):
        try:
            if klein:
                b = "----crimeboundary7f3a"
                parts = {"prompt": prompt[:2000], "width": "1280", "height": "720"}
                body = "".join(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n' for k, v in parts.items()).encode() + f"--{b}--\r\n".encode()
                req = urllib.request.Request(url, body, {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": f"multipart/form-data; boundary={b}"})
            else:
                body = json.dumps({"prompt": prompt[:2000], "steps": 4}).encode()
                req = urllib.request.Request(url, body, {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"})
            raw = base64.b64decode(json.load(urllib.request.urlopen(req, timeout=180))["result"]["image"])
            Image.open(io.BytesIO(raw)).convert("RGB").save(dst, quality=90)
            return True
        except urllib.error.HTTPError as e: last = f"HTTP {e.code}: {e.read()[:300]!r}"
        except Exception as e: last = str(e)
        time.sleep(4 * (n + 1))
    print("picture failed:", last); return False

POLL = (os.environ.get("MODEL") or "") == "pollinations"
if not POLL and not (CF_ID and CF_TOKEN):
    raise SystemExit("CF_ACCOUNT_ID / CF_API_TOKEN secrets are not set on this repo (Settings > Secrets and variables > Actions)")
redo = {int(x) for x in (os.environ.get("REDO") or "").replace(" ", "").split(",") if x}
only = {int(x) for x in (os.environ.get("ONLY") or "").replace(" ", "").split(",") if x}
os.makedirs("out", exist_ok=True)
done, fails = [], 0
for s in json.load(open(SCENES, encoding="utf-8"))["shots"]:
    f = f"out/{s['n']:02d}.jpg"
    if s["n"] in redo and os.path.exists(f): os.remove(f)
    if (only and s["n"] not in only) or (not only and os.path.exists(f)): continue
    style = STYLE.replace("expressive faces, ", "") + "Objects only, absolutely no people, no faces, no portraits. " if s["scene"].startswith(("Still life", "A clean anatomy", "Empty")) else STYLE
    ok = draw_pollinations(style + s["scene"] + END, f, 1000 + s["n"]) if POLL else draw(style + s["scene"] + END, f)
    if ok: done.append(s["n"]); fails = 0; print(f"picture {s['n']:02d} drawn")
    else:
        fails += 1
        if fails >= 3: print("3 failures in a row (daily free limit?), stopping"); break
print("drawn:", done)
if not done: raise SystemExit("no pictures were drawn")
