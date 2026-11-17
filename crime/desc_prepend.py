"""Put one line at the top of an existing video's description (keeps title, tags, category). Env: VIDEO_ID, LINE."""
import os, requests
API = "https://www.googleapis.com/youtube/v3"
r = requests.post("https://oauth2.googleapis.com/token", timeout=60, data={"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
                  "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"}); r.raise_for_status()
H = {"Authorization": "Bearer " + r.json()["access_token"]}
vid, line = os.environ["VIDEO_ID"].strip(), os.environ["LINE"].strip()
g = requests.get(f"{API}/videos", headers=H, params={"part": "snippet", "id": vid}, timeout=60).json()
if not g.get("items"): raise SystemExit(f"video not found / not readable: {g}")
sn = g["items"][0]["snippet"]
if line in sn.get("description", ""): raise SystemExit("line already present, nothing changed")
sn["description"] = line + "\n\n" + sn.get("description", "")
body = {"id": vid, "snippet": {k: sn[k] for k in ("title", "description", "categoryId") if k in sn} | ({"tags": sn["tags"]} if sn.get("tags") else {})}
u = requests.put(f"{API}/videos", headers=H, params={"part": "snippet"}, json=body, timeout=90)
print("update:", u.status_code, u.text[:300] if u.status_code >= 400 else "ok")
