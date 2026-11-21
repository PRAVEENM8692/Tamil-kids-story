"""Replace text in the description of existing videos (keeps title, tags, category). Env: VIDEO_IDS (comma separated), OLD, NEW."""
import os, requests
API = "https://www.googleapis.com/youtube/v3"
r = requests.post("https://oauth2.googleapis.com/token", timeout=60, data={"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
                  "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"}); r.raise_for_status()
H = {"Authorization": "Bearer " + r.json()["access_token"]}
old, new = os.environ["OLD"].strip(), os.environ["NEW"].strip()
for vid in (v.strip() for v in os.environ["VIDEO_IDS"].split(",") if v.strip()):
    g = requests.get(f"{API}/videos", headers=H, params={"part": "snippet", "id": vid}, timeout=60).json()
    if not g.get("items"): print(vid, "not found"); continue
    sn = g["items"][0]["snippet"]
    if old not in sn.get("description", ""): print(vid, "old text not present, skipped"); continue
    sn["description"] = sn["description"].replace(old, new)
    body = {"id": vid, "snippet": {k: sn[k] for k in ("title", "description", "categoryId") if k in sn} | ({"tags": sn["tags"]} if sn.get("tags") else {})}
    u = requests.put(f"{API}/videos", headers=H, params={"part": "snippet"}, json=body, timeout=90)
    print(vid, "update:", u.status_code, u.text[:200] if u.status_code >= 400 else "ok")
