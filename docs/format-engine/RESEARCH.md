# Format engine: open-source and API research (2026-11-10)

Licence = the repo's own LICENSE as GitHub reports it (SPDX), checked on 2026-11-10 with `gh api repos/<repo>`, plus the
weights' licence where models are downloaded separately. Rule for anything we'd ship or run in a paid product:
MIT, BSD, Apache-2.0, ISC, Unlicense, CC0, OFL only. No GPL/AGPL code, no non-commercial weights.

## Measuring a reel

| need | repo | licence | stars | last push | verdict |
|---|---|---|---|---|---|
| cuts (incl. jump cuts) | ffmpeg frame difference (`format_spec.py`) | LGPL ffmpeg, already required | | | **used**: 15/15 jump cuts found on a built reel, median error 0 s |
| cuts, fallback for fades | Breakthrough/PySceneDetect | BSD-3-Clause | 5.4k | 2026-11-10 | next, if dissolves/fades matter |
| cuts, learned | soCzech/TransNetV2 | MIT | 1.1k | 2023-12 | stale; only if PySceneDetect misses |
| on-screen text | macOS Vision (`ocr_text.js`) | part of macOS | | | **used** (Thai + English, positions) |
| on-screen text, Thai stylised / cross-platform | PaddlePaddle/PaddleOCR | Apache-2.0 | 92.5k | 2026-09 | next for Windows / better Thai |
| on-screen text | mindee/doctr | Apache-2.0 | 6.4k | 2026-11-09 | alternative |
| on-screen text | JaidedAI/EasyOCR | Apache-2.0 | 30.1k | 2025-12 | slower to update |
| faces | OpenCV YuNet (`face_track.py`) | MIT model | | | **used** |
| faces, pose, hands | google-ai-edge/mediapipe | Apache-2.0 | 37.6k | 2026-11-10 | already in the venv (gestures, body framing later) |
| segmentation (what's footage vs overlay) | facebookresearch/sam2 | Apache-2.0 | 20.1k | 2026-05 | later |
| loudness | ffmpeg ebur128 | | | | **used** |
| loudness (Python) | csteinmetz1/pyloudnorm | MIT | 0.8k | 2026-01 | not needed |
| beats, music onsets | librosa/librosa | ISC | 8.8k | 2026-11-09 | next: cut-on-beat measure |
| beats (learned) | CPJKU/beat_this | MIT code; check the checkpoints' licence before use | 0.5k | 2026-05 | candidate |
| music structure | mir-aidj/all-in-one | MIT | 0.9k | 2024-05 | stale |
| beats | CPJKU/madmom | code BSD, **model files under a separate licence** | 1.7k | 2026-03 | **avoid** the models |
| audio analysis | MTG/essentia | **AGPL-3.0** | 3.8k | | **avoid** |
| speech | SYSTRAN/faster-whisper | MIT | 26.6k | 2026-11-06 | alternative to mlx-whisper off Apple silicon |
| speech + word times | m-bain/whisperX | BSD-2-Clause (pyannote models: check terms) | 25.2k | 2026-10 | alternative |
| vision-language reading | QwenLM/Qwen3-VL | Apache-2.0 (per-size weight licences: check) | 20.2k | 2026-01 | local reader option; Claude reads the sheets today |
| object detection | ultralytics/ultralytics | **AGPL-3.0** | 63.3k | | **avoid** |
| silence-based editing | WyattBlue/auto-editor | Unlicense | 5.8k | 2026-11-10 | ideas for pause stats |

## Getting the reels (sources)

| source | how | licence / terms | verdict |
|---|---|---|---|
| Instagram | **Graph API Business Discovery**: `business_discovery.username(X){media{...}}` on the user's own professional account: another business/creator account's media list, `view_count`; media URLs are omitted for reels whose owner turned off downloads (Meta reference) | Meta Platform Terms | **product path** for listing and metadata; test whether `media_url` comes back for reels |
| Instagram | instaloader/instaloader | MIT | Instagram terms forbid automated collection | dev only |
| TikTok | official Display API (own content), Research API (academic) | TikTok terms forbid scraping | links the user pastes + their own browser |
| TikTok | davidteather/TikTok-Api | MIT, unofficial | terms risk | **avoid** in the product |
| YouTube Shorts | YouTube Data API v3 (listing, stats) | Google API terms; downloading isn't covered | listing yes, download no |
| any | yt-dlp/yt-dlp | Unlicense | the tool is fine; the platforms' terms are the issue | dev / the user's own action only |

Platform terms were read from secondary summaries in this pass (Instagram: no automated collection without
permission; TikTok: no scraping without written approval; YouTube: no automated access except search engines). A
lawyer reads the primary texts before a sale.

## Projects doing the same thing (leads, not used)

| repo | licence | what | note |
|---|---|---|---|
| kevinbadi/open-edits | MIT | Claude Code skills; a `reverse-engineer` skill measures a reference video (cuts, shot lengths, faces, palette, loudness, words per minute) and scaffolds a style skill | closest match; not read here, to keep the clean room clean; its MIT licence would allow reuse after the clean-room method exists, as a comparison |
| ryanbiddy/zing | MIT | studies a video you like, cuts clips in that style | pre-alpha |
| nopefallacy/vertical-video-editing-skills | MIT | Claude Code skill: captions, b-roll, presets | |
| sasateguh/awesome-ai-video-for-creators | CC0 | weekly list of open-source AI video tools | watch list |
| WyattBlue/auto-editor | Unlicense | silence-based cutting | |

Sources: GitHub API (repo metadata, 2026-11-10); [Instagram Business Discovery](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-facebook-login/business-discovery);
[IG Media reference](https://developers.facebook.com/documentation/instagram-platform/reference/instagram-media);
[GSAP standard licence](https://gsap.com/community/standard-license/); [Webflow: GSAP free](https://webflow.com/blog/gsap-becomes-free);
[Webflow forum on competing tools](https://discourse.webflow.com/t/webflow-makes-gsap-100-free/319967);
[TikTok terms summary](https://conductatlas.com/platform/tiktok/tiktok-terms-of-service/prohibition-on-scraping-and-data-extraction/);
[awesome-ai-video-for-creators](https://github.com/sasateguh/awesome-ai-video-for-creators).
