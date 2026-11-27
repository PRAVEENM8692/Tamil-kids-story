# Kaggle GPU test: Wan 2.2 TI2V 5B (text->video and image->video), fp16 + CPU offload for T4/P100.
import subprocess, sys, time, json, os, traceback
t0 = time.time()
def log(*a):
    print(f"[{time.time()-t0:7.1f}s]", *a, flush=True)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "diffusers>=0.35", "transformers", "accelerate", "ftfy", "imageio-ffmpeg"], check=True)
import torch
log("torch", torch.__version__, "gpu", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NONE")
from diffusers import WanPipeline, AutoencoderKLWan
from diffusers.utils import export_to_video, load_image
cfg = {}  # __CFG__
W, H = cfg.get("w", 832), cfg.get("h", 480)
FRAMES, STEPS = cfg.get("frames", 49), cfg.get("steps", 30)
PROMPT = cfg.get("prompt", "Comic book style, 1950s Madras street at night, a police inspector in khaki uniform with a torch walks slowly toward a dark old building, rain falling, light flickering, cinematic camera slowly pushing in, dramatic shadows")
NEG = "blurry, distorted face, extra limbs, text, watermark, low quality, static"
mid = "Wan-AI/Wan2.2-TI2V-5B-Diffusers"
dt = torch.float16
vae = AutoencoderKLWan.from_pretrained(mid, subfolder="vae", torch_dtype=torch.float32)
pipe = WanPipeline.from_pretrained(mid, vae=vae, torch_dtype=dt)
pipe.enable_model_cpu_offload()
log("model loaded")
res = {"gpu": torch.cuda.get_device_name(0), "w": W, "h": H, "frames": FRAMES, "steps": STEPS}
os.makedirs("/kaggle/working/out", exist_ok=True)
jobs = [("t2v", None)]
img_url = cfg.get("image_url")
if img_url:
    jobs.append(("i2v", img_url))
for name, img in jobs:
    try:
        s = time.time()
        kw = dict(prompt=PROMPT, negative_prompt=NEG, height=H, width=W, num_frames=FRAMES,
                  num_inference_steps=STEPS, guidance_scale=5.0)
        if img:
            kw["image"] = load_image(img).resize((W, H))
        frames = pipe(**kw).frames[0]
        p = f"/kaggle/working/out/{name}.mp4"
        export_to_video(frames, p, fps=24)
        res[name] = round(time.time() - s, 1)
        log(name, "done in", res[name], "s")
    except Exception as e:
        traceback.print_exc()
        res[name] = "FAILED: " + str(e)[:300]
    torch.cuda.empty_cache()
res["total_s"] = round(time.time() - t0, 1)
json.dump(res, open("/kaggle/working/out/result.json", "w"), indent=1)
log(res)
