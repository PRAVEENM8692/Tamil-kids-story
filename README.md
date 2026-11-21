# Solved Crime Files - Tamil

Tamil true-crime YouTube channel, produced end to end with GitHub Actions. One folder per case in `crime/<case>/`: `script.txt`, `scenes.json`, `plan.json`, `subs_en.txt`, `youtube.json`, `shorts.json`, `thumb_prompts.json`.

## Pipeline (Actions > Run workflow, input `case`)
1. `crime-voice-full`: Gemini Charon voice per script section.
2. `crime-pictures`: story pictures (Cloudflare FLUX.2 klein, 16:9), about one per 7 seconds.
3. `crime-manim`: animated clips (timelines, charts) from `crime/manim_scenes.py`, overlaid by the build.
4. `crime-build`: video with captions, music, channel intro and Manim overlays.
5. `crime-shorts`: three Shorts cut from the video (no text on the frames).
6. `crime-thumb-gemini` and `crime/thumb_layouts.py` (board, circle, split): thumbnails, a new layout each episode.
7. After approval: `crime-upload` (private), `crime-captions` (Tamil + English), `crime-thumb-set`, `crime-shorts-upload`, `crime-playlists`.

Other tools: `crime-channel` (channel branding and about text), `crime-desc` and `crime-desc-replace` (edit descriptions of uploaded videos).

## Secrets (Settings > Secrets and variables > Actions)
`GEMINI_API_KEY`, `CF_ACCOUNT_ID`, `CF_API_TOKEN` (optional `CF_ACCOUNT_ID_2`, `CF_API_TOKEN_2`), `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.

See `crime/NEXT_EPISODE.md` for the episode checklist.
