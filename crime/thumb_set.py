"""Replace the thumbnail of an already uploaded video (no re-upload). Env: VIDEO_ID, THUMB, YT_CLIENT_ID/SECRET/REFRESH_TOKEN."""
import os, requests
r = requests.post("https://oauth2.googleapis.com/token", timeout=60, data={"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
                  "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"})
r.raise_for_status()
H = {"Authorization": "Bearer " + r.json()["access_token"], "Content-Type": "image/jpeg"}
def setthumb(vid, path):
    t = requests.post(f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={vid}", headers=H, data=open(path, "rb").read(), timeout=180)
    print("thumbnail", vid, path, t.status_code, "" if t.status_code < 400 else t.text[:300]); return t.status_code < 400
if os.environ["VIDEO_ID"] == "BATCH":      # THUMB = json {"5": "assets/x.jpg"}: match uploads whose title starts with "EP 5 |"
    import json, re
    B = json.load(open(os.environ["THUMB"])); A = {"Authorization": H["Authorization"]}
    up = requests.get("https://www.googleapis.com/youtube/v3/channels", headers=A, params={"part": "contentDetails", "mine": "true"}, timeout=60).json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    tok, found = None, {}
    while True:
        d = requests.get("https://www.googleapis.com/youtube/v3/playlistItems", headers=A, params={"part": "snippet", "playlistId": up, "maxResults": 50, **({"pageToken": tok} if tok else {})}, timeout=60).json()
        for i in d.get("items", []):
            m = re.match(r"EP (\d+) \|", i["snippet"]["title"])
            if m: found[m.group(1)] = i["snippet"]["resourceId"]["videoId"]
        tok = d.get("nextPageToken")
        if not tok: break
    print("found", found); bad = [n for n in B if n not in found or not setthumb(found[n], B[n])]
    print("not done:", bad); raise SystemExit(1 if bad else 0)
setthumb(os.environ["VIDEO_ID"], os.environ["THUMB"]) or (_ for _ in ()).throw(SystemExit(1))
