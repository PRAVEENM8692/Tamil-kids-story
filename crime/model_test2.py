"""Shraddha test: natural-colour comic, flux-2-klein-4b vs dreamshaper-8-lcm, 2 scenes; also tries to read neuron usage."""
import base64, io, json, os, time, urllib.error, urllib.request, datetime
from PIL import Image
ID, TOK = os.environ["CF_ACCOUNT_ID"], os.environ["CF_API_TOKEN"]
NATURAL = ("Indian crime graphic-novel illustration, natural realistic colours, clean ink outlines, soft cinematic lighting, "
           "grounded true-to-life palette, detailed background, faceless or turned-away characters, serious documentary mood. ")
END = " Clean floor, calm tidy scene. Nothing cut off at the frame edges. No text, no letters, no numbers, no captions, no watermark, no border."
SC = {1: "A young man seen only from behind sits on the floor of a small rented flat at night, facing a tall silver refrigerator, a laptop glowing beside him, quiet and tense.",
      2: "A police officer's hand points at a wall map with pins, beside a table with a smartphone showing a glowing bank notification, case files, dim office light."}
os.makedirs("out", exist_ok=True); log = open("out/log.txt", "w")
def say(*a):
    s = " ".join(str(x) for x in a); print(s); log.write(s + "\n"); log.flush()
def run(model, body, dst, multipart=False):
    url = f"https://api.cloudflare.com/client/v4/accounts/{ID}/ai/run/@cf/{model}"
    if multipart:
        b = "----bnd7f3a"
        data = "".join(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n' for k, v in body.items()).encode() + f"--{b}--\r\n".encode()
        hdr = {"Authorization": f"Bearer {TOK}", "Content-Type": f"multipart/form-data; boundary={b}"}
    else:
        data = json.dumps(body).encode(); hdr = {"Authorization": f"Bearer {TOK}", "Content-Type": "application/json"}
    t = time.time()
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, data, hdr), timeout=240); raw = r.read()
        if r.headers.get("content-type", "").startswith("application/json"): raw = base64.b64decode(json.loads(raw)["result"]["image"])
        im = Image.open(io.BytesIO(raw)).convert("RGB"); im.save(dst, quality=90); say("OK", dst, im.size, round(time.time() - t, 1), "s")
    except urllib.error.HTTPError as e: say("FAIL", dst, e.code, e.read()[:300])
    except Exception as e: say("FAIL", dst, str(e)[:300])
def neurons(tag):
    now = datetime.datetime.utcnow(); a = (now - datetime.timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
    q = {"query": 'query{viewer{accounts(filter:{accountTag:"%s"}){aiInferenceAdaptiveGroups(limit:50,filter:{datetime_geq:"%s"}){count dimensions{modelId} sum{totalNeurons}}}}}' % (ID, a)}
    try:
        r = urllib.request.urlopen(urllib.request.Request("https://api.cloudflare.com/client/v4/graphql", json.dumps(q).encode(), {"Authorization": f"Bearer {TOK}", "Content-Type": "application/json"}), timeout=60)
        say("NEURONS", tag, r.read()[:1500].decode())
    except Exception as e: say("NEURONS-FAIL", tag, str(e)[:200], getattr(e, "read", lambda: b"")()[:300])
neurons("before"); time.sleep(5)
for n, sc in SC.items():
    run("black-forest-labs/flux-2-klein-4b", {"prompt": (NATURAL + sc + END)[:2000], "width": "1280", "height": "720"}, f"out/a_klein4b_natural_{n}.jpg", multipart=True)
    run("lykon/dreamshaper-8-lcm", {"prompt": (NATURAL + sc + END)[:1500], "width": 1024, "height": 576, "num_steps": 8, "guidance": 1.5}, f"out/b_dreamshaper_natural_{n}.jpg")
time.sleep(60); neurons("after")
