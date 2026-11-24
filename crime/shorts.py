"""Cut vertical Shorts (1080x1920) out of a finished episode video.
Usage: python3 crime/shorts.py CASE VIDEO.mp4 OUTDIR     (reads crime/CASE/shorts.json and crime/CASE/subs_ta.srt)
shorts.json = [{"id": "a", "from_cue": 67, "to_cue": 76, "hook": "…", "tail": "…"}]   cue numbers are those of subs_ta.srt
Layout: blurred copy of the picture fills the screen, the sharp 16:9 picture sits in the middle, a red hook box on top for the first seconds,
Tamil captions below the picture, and a 'full episode' line at the bottom. Audio (voice + music) is kept from the episode."""
import json, os, subprocess, sys
CASE, VIDEO, OUT = sys.argv[1:4]
FONT = os.environ.get("FONT") or "FreeSerif"
FONTSDIR = os.environ.get("FONTSDIR") or "/usr/share/fonts/truetype/freefont"
OUTRO_VOICE = os.environ.get("OUTRO_VOICE") or ""     # mp3 with the closing line (crime/outro_voice.py); empty = no closing card
OUTRO_LINES = os.environ.get("OUTRO_TEXT") or "முழு வீடியோவுக்கு\\Nரிலேட்டட் வீடியோ லிங்கைப்\\Nபாருங்கள்"
BTN = "assets/crime_subscribe.mov"      # LIKE then SUBSCRIBE buttons (7 s), shown at the bottom while the closing voice plays
OUTRO_LEN = 7.0
os.makedirs(OUT, exist_ok=True)
def sec(s):
    h, m, r = s.split(":"); x, ms = r.split(","); return int(h) * 3600 + int(m) * 60 + int(x) + int(ms) / 1000
def ts(t):
    t = max(t, 0); return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"
cues = {}
for b in open(f"crime/{CASE}/subs_ta.srt", encoding="utf-8").read().strip().split("\n\n"):
    l = b.split("\n"); a, e = l[1].split(" --> "); cues[int(l[0])] = (sec(a), sec(e), " ".join(l[2:]))
def add_outro(sid, t1):
    """Closing card (about 7 s): dark blurred picture, a text card with the line, the closing voice, LIKE + SUBSCRIBE buttons at the bottom."""
    base = f"{OUT}/{sid}"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t1 - 0.4:.2f}", "-i", VIDEO, "-frames:v", "1", f"{base}_last.png"], check=True)
    ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: card,{FONT},92,&H0000F0FF,&H000000FF,&H001010B0,&H001010B0,1,0,0,0,100,100,0,0,3,26,0,5,60,60,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,{ts(0)},{ts(OUTRO_LEN)},card,,0,0,0,,{{\\fad(250,300)}}{OUTRO_LINES}
"""
    af = f"{base}_outro.ass"; open(af, "w", encoding="utf-8").write(ass)
    fc = ("[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:6,eq=brightness=-0.32,format=yuv420p[bg];"
          f"[bg]ass={af}:fontsdir={FONTSDIR}[tx];[1:v]format=rgba[bt];[tx][bt]overlay=(W-w)/2:H-h-230:shortest=1,fps=30,format=yuv420p[v];"
          f"[2:a]aformat=sample_rates=44100:channel_layouts=stereo,adelay=500|500,apad,atrim=0:{OUTRO_LEN}[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-t", str(OUTRO_LEN), "-i", f"{base}_last.png", "-i", BTN, "-i", OUTRO_VOICE, "-filter_complex", fc,
                    "-map", "[v]", "-map", "[a]", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-c:a", "aac", "-b:a", "160k", "-t", str(OUTRO_LEN), f"{base}_outro.mp4"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{base}.mp4", "-i", f"{base}_outro.mp4", "-filter_complex",
                    "[0:v]fps=30,format=yuv420p[v0];[1:v]fps=30,format=yuv420p[v1];[0:a]aformat=sample_rates=44100:channel_layouts=stereo[a0];[1:a]aformat=sample_rates=44100:channel_layouts=stereo[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]",
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-c:a", "aac", "-b:a", "160k", f"{base}_final.mp4"], check=True)
    for x in ("_last.png", "_outro.ass", "_outro.mp4"): os.remove(base + x)
    os.replace(f"{base}_final.mp4", f"{base}.mp4"); print(sid, "closing card added")
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
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t0:.2f}", "-t", f"{t1 - t0:.2f}", "-i", VIDEO, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                    "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-c:a", "aac", "-b:a", "160k", f"{OUT}/{sp['id']}.mp4"], check=True)
    if OUTRO_VOICE and os.path.exists(OUTRO_VOICE): add_outro(sp["id"], t1)
    print(sp["id"], f"{t1 - t0:.1f}s")
