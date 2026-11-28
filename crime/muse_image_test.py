"""Meta Model API: Muse Image test for the crime channel pictures (16:9, comic style, faceless).
Env: META_API_KEY. Optional SCENES (json like crime/<case>/scenes.json), ONLY (scene numbers). Default = 3 test scenes.
Writes out/NN.png and out/report.txt. Standard library + Pillow (only to check the size)."""
import base64, io, json, os, time, urllib.error, urllib.request

KEY = os.environ.get("META_API_KEY", "").strip()
if not KEY:
    raise SystemExit("META_API_KEY secret is not set on this repo")
URL = "https://api.meta.ai/v1/images/generations"
MODEL, SIZE = "muse-image-1.0", os.environ.get("SIZE") or "1792x1024"
STYLE = ("Indian crime graphic-novel illustration, natural realistic colours, clean ink outlines, soft cinematic lighting, "
         "faceless or turned-away characters, serious documentary mood, wide 16:9 composition. ")
END = " No text, no letters, no numbers, no captions, no watermark, no border."
DEFAULT = [
    {"n": 1, "scene": "Night view of a quiet house in a small Indian town, a family asleep behind the windows, a faint street light, the front door closed."},
    {"n": 2, "scene": "A masked and capped figure seen only as a dark silhouette walking down a narrow street at night, face hidden, seen from behind."},
    {"n": 3, "scene": "A dim police control room with a wall of monitors showing blurry street footage, an officer seen from behind."},
]
shots = json.load(open(os.environ["SCENES"], encoding="utf-8"))["shots"] if os.environ.get("SCENES") else DEFAULT
only = {int(x) for x in (os.environ.get("ONLY") or "").replace(" ", "").split(",") if x}
os.makedirs("out", exist_ok=True)
rep, fails = [], 0

def gen(prompt):
    body = json.dumps({"model": MODEL, "prompt": prompt, "size": SIZE, "n": 1, "output_format": "png"}).encode()
    req = urllib.request.Request(URL, body, {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=300))["data"][0]
    if d.get("b64_json"): return base64.b64decode(d["b64_json"])
    return urllib.request.urlopen(d["url"], timeout=120).read()

for s in shots:
    if only and s["n"] not in only: continue
    f = f"out/{s['n']:02d}.png"
    if os.path.exists(f): continue
    for attempt in range(3):
        try:
            t = time.time(); raw = gen(STYLE + s["scene"] + END)
            open(f, "wb").write(raw)
            from PIL import Image
            w, h = Image.open(io.BytesIO(raw)).size
            rep.append(f"{s['n']:02d} ok {w}x{h} ratio {w/h:.3f} (16:9 = 1.778) {time.time()-t:.0f}s"); fails = 0; break
        except urllib.error.HTTPError as e:
            msg = f"{s['n']:02d} HTTP {e.code}: {e.read()[:300]!r}"; print(msg)
            if e.code in (400, 401, 403): rep.append(msg); fails += 1; break
            time.sleep(5 * (attempt + 1))
        except Exception as e:
            print(s["n"], e); time.sleep(5 * (attempt + 1))
    else:
        rep.append(f"{s['n']:02d} FAILED"); fails += 1
    if fails >= 3: rep.append("3 failures in a row, stopping"); break
open("out/report.txt", "w").write("\n".join(rep) + "\n"); print("\n".join(rep))
if not any(" ok " in r for r in rep): raise SystemExit("no picture was drawn")
