"""Animate comic pictures with a free Hugging Face ZeroGPU Space (Wan 2.2 image-to-video).
env: IMGS (comma list of image paths), PROMPT, HF_TOKEN (optional, uses your own ZeroGPU quota), SECS (default 3.5)"""
import os, sys, time, shutil, json
from gradio_client import Client, handle_file
SPACE = "zerogpu-aoti/wan2-2-fp8da-aoti-faster"
tok = os.environ.get("HF_TOKEN") or None
imgs = [p for p in os.environ["IMGS"].split(",") if p]
prompt = os.environ.get("PROMPT") or "slow cinematic camera push-in, subtle natural motion, comic illustration style, no distortion"
secs = float(os.environ.get("SECS", "3.5"))
os.makedirs("out", exist_ok=True)
c = Client(SPACE, token=tok) if tok else Client(SPACE)
print("api:", [k for k in c.view_api(return_format="dict")["named_endpoints"]])
log = []
for i, p in enumerate(imgs, 1):
    t = time.time()
    try:
        r = c.predict(input_image=handle_file(p), prompt=prompt, steps=6, negative_prompt="blurry, distorted, extra limbs, text, watermark",
                      duration_seconds=secs, guidance_scale=1, guidance_scale_2=1, seed=42, randomize_seed=True, api_name="/generate_video")
        v = r[0]["video"] if isinstance(r[0], dict) else r[0]
        shutil.copy(v, f"out/clip{i}.mp4"); log.append({"img": p, "ok": True, "sec": round(time.time() - t, 1)})
    except Exception as e:
        log.append({"img": p, "ok": False, "err": str(e)[:300], "sec": round(time.time() - t, 1)}); print("ERR", e)
    print(log[-1])
json.dump(log, open("out/log.json", "w"), indent=1)
