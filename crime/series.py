"""Keep every part of a multi-part case linked to all the other parts.
crime/series.json = {"key": {"name": "...", "parts": [video ids in part order]}}. For each video of each series (or only SERIES=key) the description gets one top line
'▶ <name> எல்லா பாகங்கள்: பார்ட் 1: url | பார்ட் 2: url ...' (an older such line, and old single 'part N' link lines, are replaced). Env: SERIES (optional), DRY=1 to only print."""
import json, os, re, requests
API = "https://www.googleapis.com/youtube/v3"
r = requests.post("https://oauth2.googleapis.com/token", timeout=60, data={"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
                  "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"}); r.raise_for_status()
H = {"Authorization": "Bearer " + r.json()["access_token"]}
OLD = re.compile(r"^▶ (எல்லா|.*எல்லா பாகங்கள்|பார்ட் \d|பாகம் \d|முதல் பாகம்|முந்தைய பாகம்)")
for key, s in json.load(open("crime/series.json", encoding="utf-8")).items():
    if os.environ.get("SERIES") and os.environ["SERIES"] != key: continue
    line = f"▶ {s['name']} எல்லா பாகங்கள்: " + " | ".join(f"பார்ட் {i}: https://youtu.be/{v}" for i, v in enumerate(s["parts"], 1))
    for vid in s["parts"]:
        g = requests.get(f"{API}/videos", headers=H, params={"part": "snippet", "id": vid}, timeout=60).json()
        if not g.get("items"): print(vid, "not found"); continue
        sn = g["items"][0]["snippet"]; keep = [l for l in sn.get("description", "").split("\n") if not OLD.match(l)]
        new = line + "\n\n" + re.sub(r"^\n+", "", "\n".join(keep))
        new = re.sub(r"\n{3,}", "\n\n", new)
        if new == sn.get("description"): print(vid, "already up to date"); continue
        if os.environ.get("DRY"): print(vid, "would change:\n", new[:400]); continue
        sn["description"] = new
        body = {"id": vid, "snippet": {k: sn[k] for k in ("title", "description", "categoryId") if k in sn} | ({"tags": sn["tags"]} if sn.get("tags") else {})}
        u = requests.put(f"{API}/videos", headers=H, params={"part": "snippet"}, json=body, timeout=90)
        print(vid, "update:", u.status_code, u.text[:200] if u.status_code >= 400 else "ok")
