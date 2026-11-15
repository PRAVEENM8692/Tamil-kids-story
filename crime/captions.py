"""Upload the Tamil and English subtitle tracks (crime/<case>/subs_ta.srt, subs_en.srt) to a YouTube video as closed captions.
Env: CASE, VIDEO_ID (leave empty to use the newest video whose title matches crime/<case>/youtube.json), YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN.
Replaces an existing track of the same language. Never changes privacy."""
import json, os, requests
CASE = os.environ.get("CASE") or "alavandar"; API = "https://www.googleapis.com/youtube/v3"
r = requests.post("https://oauth2.googleapis.com/token", timeout=60, data={"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"], "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"})
if r.status_code >= 400: raise SystemExit(f"YouTube key refused: {r.status_code} {r.text[:200]}")
H = {"Authorization": "Bearer " + r.json()["access_token"]}
def upload_captions(vid, case=CASE):
    ok = True
    have = requests.get(f"{API}/captions", headers=H, params={"part": "snippet", "videoId": vid}, timeout=60).json().get("items", [])
    for lang, name in (("ta", "தமிழ்"), ("en", "English")):
        path = f"crime/{case}/subs_{lang}.srt"
        if not os.path.exists(path): print(f"captions {lang}: {path} not found, skipped"); continue
        for c in have:
            if c["snippet"]["language"] == lang: requests.delete(f"{API}/captions", headers=H, params={"id": c["id"]}, timeout=60)
        meta = json.dumps({"snippet": {"videoId": vid, "language": lang, "name": name, "isDraft": False}})
        x = requests.post("https://www.googleapis.com/upload/youtube/v3/captions?uploadType=multipart&part=snippet", timeout=120,
                          headers={**H, "Content-Type": "multipart/related; boundary=capb"},
                          data=("--capb\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n" + meta + "\r\n--capb\r\nContent-Type: application/octet-stream\r\n\r\n").encode() + open(path, "rb").read() + b"\r\n--capb--")
        print(f"captions {lang}:", x.status_code, "" if x.status_code < 400 else x.text[:300]); ok &= x.status_code < 400
    return ok
if __name__ == "__main__":
    vid = os.environ.get("VIDEO_ID", "").strip()
    if not vid:
        title = json.load(open(f"crime/{CASE}/youtube.json", encoding="utf-8"))["title"]
        up = requests.get(f"{API}/channels", headers=H, params={"part": "contentDetails", "mine": "true"}, timeout=60).json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        for it in requests.get(f"{API}/playlistItems", headers=H, params={"part": "snippet", "playlistId": up, "maxResults": 50}, timeout=60).json().get("items", []):
            if it["snippet"]["title"] == title: vid = it["snippet"]["resourceId"]["videoId"]; break
    if not vid: raise SystemExit("video not found on the channel")
    if not upload_captions(vid): raise SystemExit("captions failed (the key may lack the youtube.force-ssl permission)")
