"""Tamil crime story channel: narrate a whole script with one voice - the owner's own AI voice (NARRATOR=myvoice, default,
owner's choice 2026-11-27) or one Gemini voice with no style instruction (NARRATOR=gemini, Charon).
Script file: sections start with a '## NN name' line. Writes out/NN_name.mp3, out/full.mp3 and out/durations.json."""
import base64, json, os, re, subprocess, sys, time, wave
import requests

API = "https://generativelanguage.googleapis.com/v1beta"
KEY = os.environ.get("GEMINI_API_KEY", "")
MODELS = [m.strip() for m in (os.environ.get("TTS_MODEL") or "gemini-3.8-flash-tts,gemini-3.8-flash-lite-tts,gemini-3.1-flash-tts-preview").split(",") if m.strip()]
VOICE = os.environ.get("NARRATOR_VOICE") or "Charon"
SCRIPT = os.environ.get("SCRIPT") or "crime/alavandar/script.txt"
MAX_CHARS = 900     # long sections are cut at line ends into pieces of about this size, so no call runs too long

def pieces(text):
    out, cur = [], ""
    for line in text.splitlines():
        if cur and len(cur) + len(line) > MAX_CHARS: out.append(cur); cur = ""
        cur = (cur + " " + line).strip()
    return out + ([cur] if cur else [])

def pcm_of(data):
    """Gemini may answer with a complete WAV file (44-byte RIFF header first) instead of bare samples.
    Played as samples, that header is a loud click at the start of every clip, so cut it off."""
    if data[:4] == b"RIFF" and data[8:12] == b"WAVE":
        i = data.find(b"data", 12)
        if i > 0: return data[i + 8:]
    return data

def clean(pcm):
    """Cut Gemini's loud noise burst at the end of the clip (heard as a squeak) - see tts_clean.py."""
    import numpy as np; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import tts_clean
    x = np.frombuffer(pcm, dtype=np.int16).copy(); ms = tts_clean.strip_tail(x, 24000)
    if ms: print(f'  end burst silenced ({ms} ms)')
    return x.tobytes()

EXPRESSIVE = os.environ.get("EXPRESSIVE", "") == "1"
STYLE_OF = {   # owner 2026-11-28: livelier, expressive storytelling (like a Tamil crime-show narrator); style line is given to the TTS model, not read aloud
    "hook": "Narrate like a gripping Tamil crime-show storyteller: low, tense voice, slow build, a sharp pause before the shocking line, then fast and urgent.",
    "disclaimer": "Speak calmly, clearly and seriously.",
    "intro": "Warm, engaging storytelling voice with natural variation in pitch.",
    "disappearance": "Suspenseful and hushed, slow, with dramatic pauses and rising tension.",
    "clue": "Curious and sharp, building suspense, emphasise key words.",
    "question": "Direct and teasing, as if asking the audience, pause after the question.",
    "answer": "Excited revelation, energetic, strong emphasis on each proof, quicker pace then a heavy pause.",
    "arrest": "Firm, fast, triumphant tone.",
    "court": "Serious, weighty and measured, emphasise the verdict words.",
    "ending": "Reflective, warm, then friendly and upbeat for the call to subscribe."}
CUR_STYLE = [""]

def tts(text):
    if EXPRESSIVE and CUR_STYLE[0]: text = f"{CUR_STYLE[0]} Say the following in Tamil, with real emotion and expression:\n{text}"
    last = ""
    for n in range(8):
        model = MODELS[0] if n < 3 else MODELS[n % len(MODELS)]     # stay on one model so the voice sounds the same; others only as a fallback
        r = requests.post(f"{API}/models/{model}:generateContent", headers={"x-goog-api-key": KEY}, timeout=240, json={
            "contents": [{"parts": [{"text": text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}}}})
        if r.status_code < 400:
            try: return pcm_of(base64.b64decode(r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])), model
            except Exception as e: last = f"no audio in answer: {str(e)[:80]}"
        else:
            last = f"HTTP {r.status_code} {r.text[:300]}"
        print(f"{model}: {last}"); time.sleep((30 if "429" in last else 8) * (n + 1))
    raise SystemExit(f"Gemini voice failed: {last}")

NARRATOR = (os.environ.get("NARRATOR") or "myvoice").lower()
if NARRATOR == "myvoice":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import myvoice_tts

    # which of the owner's 8 mood recordings each script section is spoken with (section name -> mood)
    MOOD_OF = {"hook": "hook", "disclaimer": "calm", "intro": "calm", "background": "calm", "disappearance": "suspense",
               "investigation": "suspense", "clue": "suspense", "clues": "suspense", "question": "question", "answer": "twist",
               "twist": "twist", "arrest": "success", "court": "calm", "verdict": "calm", "sad": "sad", "ending": "end"}
    CUR_MOOD = [None]

    def tts(text):
        """Owner's own AI voice (free Hugging Face GPU first, CPU fallback): same 24 kHz 16-bit PCM as the Gemini path."""
        import numpy as np, soundfile as sf
        tmp = "out/_piece.wav"; myvoice_tts.speak(text, tmp, mood=CUR_MOOD[0])
        a, _ = sf.read(tmp, dtype="float32"); os.remove(tmp)
        return (np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes(), "myvoice"

    def clean(pcm): return pcm        # the Gemini end-burst fix is not needed for this voice
elif not KEY: raise SystemExit("GEMINI_API_KEY is not set")
secs = [(m.group(1), m.group(2).strip().replace(" ", "_"), m.group(3).strip())
        for m in re.finditer(r"^## (\d+) ([^\n]*)\n(.*?)(?=^## |\Z)", open(SCRIPT, encoding="utf-8").read(), re.S | re.M)]
only = [s.strip() for s in os.environ.get("ONLY", "").split(",") if s.strip()]
os.makedirs("out", exist_ok=True)
durs, files = {}, []
for num, name, text in secs:
    if only and num not in only: continue
    pcm = b""
    CUR_STYLE[0] = STYLE_OF.get(name.split("_")[0].lower(), "")
    if NARRATOR == "myvoice":
        CUR_MOOD[0] = MOOD_OF.get(name.split("_")[0].lower(), "calm"); print(f"{num} {name}: mood {CUR_MOOD[0]}")
    for p in pieces(text):
        a, model = tts(p); a = clean(a); pcm += a + b"\0" * int(24000 * 2 * 0.35)      # a short breath between pieces
        if NARRATOR != "myvoice": time.sleep(7)       # stay under Gemini's per-minute limit
    wav = f"out/{num}_{name}.wav"
    with wave.open(wav, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
    files.append(wav); durs[f"{num}_{name}"] = round(len(pcm) / 48000, 1)
    print(f"{num} {name}: {durs[f'{num}_{name}']} s ({model})")
open("out/list.txt", "w").write("".join(f"file '{os.path.basename(f)}'\n" for f in files))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "out/list.txt", "-b:a", "128k", "out/full.mp3"], check=True)
for f in files:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-b:a", "128k", f[:-4] + ".mp3"], check=True); os.remove(f)
os.remove("out/list.txt")
durs["total"] = round(sum(durs.values()), 1)
json.dump(durs, open("out/durations.json", "w"), ensure_ascii=False, indent=1)
print("total:", durs["total"], "s")
if NARRATOR == "myvoice": print("my voice engine use:", myvoice_tts.STATS)
