"""Cut vertical Shorts (1080x1920) out of a finished episode video.
Usage: python3 crime/shorts.py CASE VIDEO.mp4 OUTDIR     (reads crime/CASE/shorts.json and crime/CASE/subs_ta.srt)
shorts.json = [{"id": "a", "from_cue": 67, "to_cue": 76, "hook": "…", "tail": "…"}]   cue numbers are those of subs_ta.srt
Layout: blurred copy of the picture fills the screen, the sharp 16:9 picture sits in the middle, a red hook box on top for the first seconds,
Tamil captions below the picture, and a 'full episode' line at the bottom. Audio (voice + music) is kept from the episode."""
import json, os, re, subprocess, sys
CASE, VIDEO, OUT = sys.argv[1:4]
FONT = os.environ.get("FONT") or "FreeSerif"
FONTSDIR = os.environ.get("FONTSDIR") or "/usr/share/fonts/truetype/freefont"
os.makedirs(OUT, exist_ok=True)
def sec(s):
    h, m, r = s.split(":"); x, ms = r.split(","); return int(h) * 3600 + int(m) * 60 + int(x) + int(ms) / 1000
def ts(t):
    t = max(t, 0); return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"
cues = {}
for b in open(f"crime/{CASE}/subs_ta.srt", encoding="utf-8").read().strip().split("\n\n"):
    l = b.split("\n"); a, e = l[1].split(" --> "); cues[int(l[0])] = (sec(a), sec(e), " ".join(l[2:]))
for sp in json.load(open(f"crime/{CASE}/shorts.json", encoding="utf-8")):
    t0, t1 = cues[sp["from_cue"]][0], cues[sp["to_cue"]][1] + 0.3
    ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: cap,{FONT},66,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,6,2,8,70,70,0,1
Style: hook,{FONT},84,&H0000F0FF,&H000000FF,&H001010B0,&H001010B0,1,0,0,0,100,100,0,0,3,18,0,8,60,60,230,1
Style: foot,{FONT},52,&H0000F0FF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,5,2,2,60,60,150,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    if sp.get("hook"): ass += f"Dialogue: 1,{ts(0)},{ts(4.2)},hook,,0,0,0,,{{\\fad(150,350)}}{sp['hook']}\n"
    for k in range(sp["from_cue"], sp["to_cue"] + 1):
        a, e, tx = cues[k]
        ass += f"Dialogue: 0,{ts(a - t0)},{ts(min(e, t1) - t0)},cap,,0,0,1290,,{tx}\n"
    if sp.get("tail", "x"): ass += f"Dialogue: 0,{ts(0)},{ts(t1 - t0)},foot,,0,0,0,,{sp.get('tail', 'முழு எபிசோட்: Solved Crime Files - Tamil')}\n"
    af = f"{OUT}/{sp['id']}.ass"; open(af, "w", encoding="utf-8").write(ass)
    fc = ("[0:v]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:6,eq=brightness=-0.18[bg];"
          "[b]scale=1080:-2[fg];[bg][fg]overlay=0:(H-h)/2-120,"
          f"ass={af}:fontsdir={FONTSDIR},format=yuv420p[v];[0:a]afade=t=in:d=0.3,afade=t=out:st={t1 - t0 - 0.5:.2f}:d=0.5[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t0:.2f}", "-to", f"{t1:.2f}", "-i", VIDEO, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                    "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-c:a", "aac", "-b:a", "160k", f"{OUT}/{sp['id']}.mp4"], check=True)
    print(sp["id"], f"{t1 - t0:.1f}s")
