"""Create the crime channel playlists (private) and add the episodes. Safe to run again: existing playlists and items are skipped. Nothing is deleted."""
import os, requests
API = "https://www.googleapis.com/youtube/v3"
r = requests.post("https://oauth2.googleapis.com/token", timeout=60, data={"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"], "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"})
r.raise_for_status(); T = r.json()["access_token"]; H = {"Authorization": f"Bearer {T}"}
print("key permissions:", [s.rsplit("/", 1)[-1] for s in requests.get("https://oauth2.googleapis.com/tokeninfo", params={"access_token": T}, timeout=60).json().get("scope", "").split()])
PL = [
 ("பழைய வழக்குகள் | Old Solved Cases", "1999-க்கு முன் நடந்த தீர்ந்த வழக்குகள்: ஆளவந்தார் (1952), ஷகெரே கலீலி (1991), ஆட்டோ சங்கர் (1988).", ["RfsLccFhTGM", "SwKOLgA6htU", "eEn4tz1mMp0"]),
 ("புதிய வழக்குகள் | New Solved Cases", "2000-க்குப் பிறகு நடந்த தீர்ந்த வழக்குகள்.", ["fVTeuVVa2A0", "z9_ZLjTbRu8", "dnmYgxEv2qc", "oYWyz1SFCK0", "mnRiXwOWtL4"]),
 ("வழக்கு அப்டேட் | Case Updates", "நம்ம வழக்குகளோட இப்போதைய நிலவரம்.", []),
]
have = {}
tok = None
while True:
    d = requests.get(f"{API}/playlists", headers=H, params={"part": "snippet", "mine": "true", "maxResults": 50, **({"pageToken": tok} if tok else {})}, timeout=60).json()
    if "error" in d: raise SystemExit(f"cannot read playlists: {d['error'].get('code')} {d['error'].get('message')}")
    for it in d.get("items", []): have[it["snippet"]["title"]] = it["id"]
    tok = d.get("nextPageToken")
    if not tok: break
for title, desc, vids in PL:
    pid = have.get(title)
    if not pid:
        c = requests.post(f"{API}/playlists", headers=H, params={"part": "snippet,status"}, timeout=60, json={"snippet": {"title": title, "description": desc, "defaultLanguage": "ta"}, "status": {"privacyStatus": "private"}})
        if c.status_code >= 400: raise SystemExit(f"create failed for {title}: {c.status_code} {c.text[:300]}")
        pid = c.json()["id"]; print("created:", title, pid)
    else: print("exists:", title, pid)
    cur, tok = set(), None
    while True:
        d = requests.get(f"{API}/playlistItems", headers=H, params={"part": "contentDetails", "playlistId": pid, "maxResults": 50, **({"pageToken": tok} if tok else {})}, timeout=60).json()
        cur |= {i["contentDetails"]["videoId"] for i in d.get("items", [])}; tok = d.get("nextPageToken")
        if not tok: break
    for v in vids:
        if v in cur: print("  already in:", v); continue
        a = requests.post(f"{API}/playlistItems", headers=H, params={"part": "snippet"}, timeout=60, json={"snippet": {"playlistId": pid, "resourceId": {"kind": "youtube#video", "videoId": v}}})
        print("  added" if a.status_code < 400 else f"  FAILED {a.status_code} {a.text[:200]}", v)
