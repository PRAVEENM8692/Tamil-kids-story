"""Real AI image-to-video on CPU only (free GitHub runner, slow): LTX-Video 2B through diffusers.
Memory trick for the 16 GB runner: the big T5 text encoder runs first, is thrown away, then the video model loads.
env: IMGS, PROMPT, FRAMES (8k+1, default 49 = about 2 s), STEPS (default 30), OUT (default out)"""
import os, gc, time, json
import torch
from PIL import Image
from diffusers import LTXImageToVideoPipeline
from diffusers.utils import export_to_video

REPO = "Lightricks/LTX-Video"
imgs = [p for p in os.environ["IMGS"].split(",") if p]
PROMPT = os.environ.get("PROMPT") or "comic illustration, slow cinematic camera push-in, the people move slightly and naturally, dramatic light, stable faces"
NEG = "worst quality, blurry, jittery, distorted faces, extra limbs, text, watermark"
FRAMES = int(os.environ.get("FRAMES") or 49)
STEPS = int(os.environ.get("STEPS") or 30)
W, H = 512, 288                      # small 16:9 size, both divisible by 32; upscaled to 720p afterwards
OUT = os.environ.get("OUT") or "out"; os.makedirs(OUT, exist_ok=True)
torch.set_num_threads(os.cpu_count() or 4)
log = []

t0 = time.time()
enc = LTXImageToVideoPipeline.from_pretrained(REPO, transformer=None, vae=None, torch_dtype=torch.bfloat16)
with torch.no_grad():
    pe, pm, ne, nm = enc.encode_prompt(PROMPT, NEG, do_classifier_free_guidance=True, device="cpu", max_sequence_length=128)
pe, pm, ne, nm = [x.float() for x in (pe, pm, ne, nm)]
del enc; gc.collect()
print("text encoded in", round(time.time() - t0), "s", flush=True)

pipe = LTXImageToVideoPipeline.from_pretrained(REPO, text_encoder=None, tokenizer=None, torch_dtype=torch.float32)
pipe.vae.enable_tiling()
print("video model loaded at", round(time.time() - t0), "s", flush=True)

for i, p in enumerate(imgs, 1):
    t = time.time()
    try:
        img = Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)
        with torch.no_grad():
            fr = pipe(image=img, prompt_embeds=pe, prompt_attention_mask=pm, negative_prompt_embeds=ne, negative_prompt_attention_mask=nm,
                      width=W, height=H, num_frames=FRAMES, num_inference_steps=STEPS, guidance_scale=3.0,
                      generator=torch.Generator().manual_seed(42)).frames[0]
        raw = f"{OUT}/ltx{i}_raw.mp4"; export_to_video(fr, raw, fps=24)
        os.system(f"ffmpeg -y -loglevel error -i {raw} -vf scale=1280:720:flags=lanczos -c:v libx264 -crf 20 -pix_fmt yuv420p {OUT}/ltx{i}.mp4 && rm {raw}")
        log.append({"img": p, "ok": True, "sec": round(time.time() - t, 1), "frames": FRAMES, "steps": STEPS})
    except Exception as e:
        log.append({"img": p, "ok": False, "err": str(e)[:400], "sec": round(time.time() - t, 1)})
    print(log[-1], flush=True)
    json.dump(log, open(f"{OUT}/ltx_log.json", "w"), indent=1)
