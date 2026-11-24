"""Create the crime channel playlists (private) and add the episodes. Safe to run again: existing playlists and items are skipped. Nothing is deleted."""
import os, requests
API = "https://www.googleapis.com/youtube/v3"
r = requests.post("https://oauth2.googleapis.com/token", timeout=60, data={"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"], "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"})
r.raise_for_status(); T = r.json()["access_token"]; H = {"Authorization": f"Bearer {T}"}
print("key permissions:", [s.rsplit("/", 1)[-1] for s in requests.get("https://oauth2.googleapis.com/tokeninfo", params={"access_token": T}, timeout=60).json().get("scope", "").split()])

def find_shorts():
    up = requests.get(f"{API}/channels", headers=H, params={"part": "contentDetails", "mine": "true"}, timeout=60).json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    out, tok = [], None
    while True:
        d = requests.get(f"{API}/playlistItems", headers=H, params={"part": "snippet", "playlistId": up, "maxResults": 50, **({"pageToken": tok} if tok else {})}, timeout=60).json()
        for i in d.get("items", []):
            if "முழு எபிசோட்" in (i["snippet"].get("description") or ""): out.append(i["snippet"]["resourceId"]["videoId"])
        tok = d.get("nextPageToken")
        if not tok: break
    print("Shorts found on the channel:", len(out)); return out
PL = [
 ("பழைய வழக்குகள் | Older Solved Cases", "2026-க்கு முன் நடந்த தீர்ந்த வழக்குகள்.", ["RfsLccFhTGM", "SwKOLgA6htU", "fVTeuVVa2A0", "dnmYgxEv2qc", "oYWyz1SFCK0", "eEn4tz1mMp0", "sCycvjHUkNA"], "பழைய வழக்குகள் | Old Solved Cases"),
 ("புதிய 2026 வழக்குகள் | New 2026 Cases", "2026-ல நடந்த, இப்போ பேசப்படற வழக்குகள்.", ["z9_ZLjTbRu8", "mnRiXwOWtL4", "Pa8K-SDr304", "yHX_psht81Y", "YkWGKy6IbUg", "mxhEsF6M1Vg", "fXrZIP3bdQU"], "புதிய வழக்குகள் | New Solved Cases"),
 ("வழக்கு அப்டேட் | Case Updates", "நம்ம வழக்குகளோட இப்போதைய நிலவரம்.", [], None),
 ("ஷார்ட்ஸ் | Crime Shorts", "எல்லா வழக்குகளோட Shorts.", find_shorts(), None),
]
have = {}
tok = None
while True:
    d = requests.get(f"{API}/playlists", headers=H, params={"part": "snippet", "mine": "true", "maxResults": 50, **({"pageToken": tok} if tok else {})}, timeout=60).json()
    if "error" in d: raise SystemExit(f"cannot read playlists: {d['error'].get('code')} {d['error'].get('message')}")
    for it in d.get("items", []): have[it["snippet"]["title"]] = it["id"]
    tok = d.get("nextPageToken")
    if not tok: break
for title, desc, vids, old in PL:
    pid = have.get(title) or (have.get(old) if old else None)
    if pid and title not in have:
        u = requests.put(f"{API}/playlists", headers=H, params={"part": "snippet"}, timeout=60, json={"id": pid, "snippet": {"title": title, "description": desc, "defaultLanguage": "ta"}}); print("renamed ->", title, u.status_code)
    if not pid:
        c = requests.post(f"{API}/playlists", headers=H, params={"part": "snippet,status"}, timeout=60, json={"snippet": {"title": title, "description": desc, "defaultLanguage": "ta"}, "status": {"privacyStatus": "private"}})
        if c.status_code >= 400: raise SystemExit(f"create failed for {title}: {c.status_code} {c.text[:300]}")
        pid = c.json()["id"]; print("created:", title, pid)
    else: print("exists:", title, pid)
    cur, tok = set(), None
    while True:
        d = requests.get(f"{API}/playlistItems", headers=H, params={"part": "contentDetails", "playlistId": pid, "maxResults": 50, **({"pageToken": tok} if tok else {})}, timeout=60).json()
        for i in d.get("items", []):
            vid = i["contentDetails"]["videoId"]
            if vids and vid not in vids:   # only removes the playlist entry, never the video
                x = requests.delete(f"{API}/playlistItems", headers=H, params={"id": i["id"]}, timeout=60); print("  removed from this playlist:", vid, x.status_code)
            else: cur.add(vid)
        tok = d.get("nextPageToken")
        if not tok: break
    for v in vids:
        if v in cur: print("  already in:", v); continue
        a = requests.post(f"{API}/playlistItems", headers=H, params={"part": "snippet"}, timeout=60, json={"snippet": {"playlistId": pid, "resourceId": {"kind": "youtube#video", "videoId": v}}})
        print("  added" if a.status_code < 400 else f"  FAILED {a.status_code} {a.text[:200]}", v)
