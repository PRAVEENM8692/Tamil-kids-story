"""2.5D motion for still pictures, CPU only (free GitHub runner).
Depth-Anything V2 Small guesses how far each pixel is; the camera then pushes in / drifts sideways,
near things move more than the background, so a still comic picture looks like a moving camera shot.
env: IMGS (comma list of image paths), SECS (seconds per clip, default 7), OUT (default out)"""
import os, time, json, subprocess
import numpy as np, cv2, torch
from PIL import Image
from transformers import pipeline

W, H, FPS = 1280, 720, 30
imgs = [p for p in os.environ["IMGS"].split(",") if p]
SECS = float(os.environ.get("SECS") or 7)
OUT = os.environ.get("OUT") or "out"; os.makedirs(OUT, exist_ok=True)
torch.set_num_threads(os.cpu_count() or 4)
depth_model = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device="cpu")

# camera moves, picked in turn so consecutive pictures don't all move the same way
MOVES = [dict(zoom=0.10, pan=0.00), dict(zoom=0.05, pan=0.035), dict(zoom=0.05, pan=-0.035), dict(zoom=-0.08, pan=0.0)]

def ease(t): return t * t * (3 - 2 * t)

def clip(path, move, out):
    im = Image.open(path).convert("RGB")
    src = cv2.resize(np.array(im), (W, H), interpolation=cv2.INTER_LANCZOS4)
    d = np.array(depth_model(Image.fromarray(src))["depth"].resize((W, H)), dtype=np.float32)
    d = (d - d.min()) / max(1e-6, d.max() - d.min())          # 1 = near, 0 = far
    d = cv2.GaussianBlur(d, (0, 0), 6)                         # soft edges, less tearing
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W / 2, H / 2
    n = int(SECS * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for k in range(n):
        t = ease(k / max(1, n - 1))
        z0 = 1.06                                              # small overscan so edges never show
        z = z0 + (move["zoom"] * t if move["zoom"] > 0 else -move["zoom"] * (1 - t))
        scale = 1 + (z - 1) * (0.35 + 0.65 * d)                 # near pixels zoom more
        shift = move["pan"] * W * (t - 0.5) * (0.3 + 0.7 * d)  # near pixels slide more
        mx = cx + (xs - cx) / scale - shift
        my = cy + (ys - cy) / scale
        fr = cv2.remap(src, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait()

log = []
for i, p in enumerate(imgs, 1):
    t = time.time()
    try:
        clip(p, MOVES[(i - 1) % len(MOVES)], f"{OUT}/parallax{i}.mp4")
        log.append({"img": p, "ok": True, "sec": round(time.time() - t, 1)})
    except Exception as e:
        log.append({"img": p, "ok": False, "err": str(e)[:300]})
    print(log[-1], flush=True)
json.dump(log, open(f"{OUT}/parallax_log.json", "w"), indent=1)
