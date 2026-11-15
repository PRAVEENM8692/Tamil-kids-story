"""Subtitles for a crime episode: Tamil (the script text) and English (crime/<case>/subs_en.txt), as .srt files timed like the video.
python crime/subs.py CASE VOICE_DIR [--list]    VOICE_DIR holds durations.json from the voice branch.  --list prints the numbered Tamil sentences (to translate).
subs_en.txt has the same '## NN name' headers as the script and exactly one English line per Tamil caption (run --list to see them: sentences split after . ? !, short ones joined to the next).
Timing mirrors build.py: section starts add GAP (0.45 s) between sections; the 13 s channel intro is inserted after the hook (section 01); inside a section, time follows character count."""
import json, re, sys
CASE, VOICE = sys.argv[1], sys.argv[2]; GAP, INTRO = 0.45, 13.0
def sections(path):
    out = []
    for m in re.finditer(r"^## (\d\d) (\w+)\n(.*?)(?=^## |\Z)", open(path, encoding="utf-8").read(), re.S | re.M):
        sents = [s.strip().replace("\u0001", ".") for line in m.group(3).strip().replace("ஏ.என்.ஐ.", "ஏ\u0001என்\u0001ஐ\u0001").splitlines() for s in re.split(r"(?<=[.?!])\s+", line.strip()) if s.strip()]
        chunks = []                      # short sentences are joined with the next one so a caption stays on screen long enough (40-130 characters)
        for x in sents:
            if chunks and (len(chunks[-1]) < 40 and len(chunks[-1]) + len(x) < 130): chunks[-1] += " " + x
            else: chunks.append(x)
        out.append((m.group(1), m.group(2), chunks))
    return out
ta = sections(f"crime/{CASE}/script.txt")
if "--list" in sys.argv:
    for num, name, ss in ta:
        print(f"## {num} {name}")
        for i, s in enumerate(ss, 1): print(f"{i}. {s}")
    sys.exit()
en = [(m.group(1), m.group(2), [x.strip() for x in m.group(3).strip().splitlines() if x.strip()]) for m in re.finditer(r"^## (\d\d) (\w+)\n(.*?)(?=^## |\Z)", open(f"crime/{CASE}/subs_en.txt", encoding="utf-8").read(), re.S | re.M)]   # one line = one caption
dur = json.load(open(f"{VOICE}/durations.json"))
def stamp(x):
    h, r = divmod(x, 3600); m, r = divmod(r, 60); s = int(r); return f"{int(h):02d}:{int(m):02d}:{s:02d},{int((r - s) * 1000):03d}"
tracks = {"ta": [], "en": []}; t = 0.0
for (num, name, ts), (n2, _, es) in zip(ta, en):
    if num != n2 or len(ts) != len(es): raise SystemExit(f"section {num}: {len(ts)} Tamil sentences but {len(es)} English lines")
    d = dur[f"{num}_{name}"]; base = t + (INTRO if int(num) >= 2 else 0); total = sum(len(s) for s in ts); c = 0
    for s, e in zip(ts, es):
        a = base + d * c / total; c += len(s); b = base + d * c / total - 0.05
        tracks["ta"].append((a, b, s)); tracks["en"].append((a, b, e))
    t += d + GAP
for lang, rows in tracks.items():
    open(f"crime/{CASE}/subs_{lang}.srt", "w", encoding="utf-8").write("".join(f"{i}\n{stamp(a)} --> {stamp(b)}\n{x}\n\n" for i, (a, b, x) in enumerate(rows, 1)))
print({k: len(v) for k, v in tracks.items()}, "sentences; end", stamp(tracks["ta"][-1][1]))
