"""Make the one-line voice that closes every Short (owner's own AI voice by default, NARRATOR=gemini for Charon). Usage: python3 crime/outro_voice.py OUT.mp3 ["text"]"""
import base64, os, subprocess, sys, time, wave
import numpy as np, requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import tts_clean
OUT = sys.argv[1]; TEXT = sys.argv[2] if len(sys.argv) > 2 else "முழு வீடியோவுக்கு, ரிலேட்டட் வீடியோ லிங்கைப் பாருங்கள்."
if (os.environ.get("NARRATOR") or "myvoice").lower() == "myvoice":     # owner's own AI voice, same as the episodes (2026-11-27)
    import myvoice_tts
    myvoice_tts.speak(TEXT, "/tmp/outro.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "/tmp/outro.wav", "-b:a", "128k", OUT], check=True)
    print("outro voice (my voice)", myvoice_tts.STATS); sys.exit(0)
KEY = os.environ["GEMINI_API_KEY"]; VOICE = os.environ.get("NARRATOR_VOICE") or "Charon"
MODELS = [m.strip() for m in (os.environ.get("TTS_MODEL") or "gemini-3.8-flash-tts,gemini-3.8-flash-lite-tts,gemini-3.1-flash-tts-preview").split(",") if m.strip()]
last = ""
for n in range(8):
    model = MODELS[0] if n < 3 else MODELS[n % len(MODELS)]
    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", headers={"x-goog-api-key": KEY}, timeout=240, json={
        "contents": [{"parts": [{"text": TEXT}]}],
        "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}}}})
    if r.status_code < 400:
        try:
            d = base64.b64decode(r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
            if d[:4] == b"RIFF":
                i = d.find(b"data", 12); d = d[i + 8:]
            x = np.frombuffer(d, dtype=np.int16).copy(); tts_clean.strip_tail(x, 24000)
            with wave.open("/tmp/outro.wav", "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(x.tobytes())
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "/tmp/outro.wav", "-b:a", "128k", OUT], check=True)
            print("outro voice", round(len(x) / 24000, 1), "s", model); sys.exit(0)
        except Exception as e: last = f"no audio: {str(e)[:80]}"
    else: last = f"HTTP {r.status_code} {r.text[:200]}"
    print(model, last); time.sleep((30 if "429" in last else 8) * (n + 1))
raise SystemExit("Gemini voice failed: " + last)
