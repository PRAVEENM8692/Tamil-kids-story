"""Upload the Shorts of crime/<CASE>/shorts.json as PRIVATE videos (files in shorts/<id>.mp4). Env: CASE, FULL (link of the full episode). Skips titles that already exist."""
import json, os, requests
CASE, FULL = os.environ["CASE"], os.environ["FULL"]
API = "https://www.googleapis.com/youtube/v3"
r = requests.post("https://oauth2.googleapis.com/token", timeout=60, data={"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"], "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"})
if r.status_code >= 400: raise SystemExit(f"key refused: {r.status_code}")
H = {"Authorization": "Bearer " + r.json()["access_token"]}
up = requests.get(f"{API}/channels", headers=H, params={"part": "contentDetails", "mine": "true"}, timeout=60).json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
have, page = set(), None
while True:
    d = requests.get(f"{API}/playlistItems", headers=H, params={"part": "snippet", "playlistId": up, "maxResults": 50, **({"pageToken": page} if page else {})}, timeout=60).json()
    have |= {i["snippet"]["title"] for i in d.get("items", [])}; page = d.get("nextPageToken")
    if not page: break
for s in json.load(open(f"crime/{CASE}/shorts.json", encoding="utf-8")):
    if s["title"] in have: print("exists:", s["title"]); continue
    desc = f"{s['desc']}\n\n▶ முழு எபிசோட் இங்கே: {FULL}\n\n#Shorts #SolvedCrimeFiles #TamilCrime #TrueCrimeTamil"
    body = {"snippet": {"title": s["title"], "description": desc, "tags": ["tamil true crime", "solved crime files", "shorts", "crime story tamil"], "categoryId": "22", "defaultLanguage": "ta", "defaultAudioLanguage": "ta"},
            "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False, "embeddable": True}}
    f = f"shorts/{s['id']}.mp4"; size = os.path.getsize(f)
    i = requests.post("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status", timeout=120, headers={**H, "Content-Type": "application/json; charset=UTF-8", "X-Upload-Content-Length": str(size), "X-Upload-Content-Type": "video/mp4"}, json=body)
    if i.status_code >= 400: raise SystemExit(f"start refused: {i.status_code} {i.text[:300]}")
    d = requests.put(i.headers["Location"], data=open(f, "rb"), headers={"Content-Type": "video/mp4"}, timeout=1800)
    if d.status_code >= 400: raise SystemExit(f"upload failed: {d.status_code} {d.text[:300]}")
    print(f"uploaded (private) {s['id']}: https://youtu.be/{d.json()['id']}")
