# Runtime tools and services (not bundled)

| what | used for | licence / terms |
|---|---|---|
| HyperFrames CLI (through `scripts/hf.sh`, the version pinned in `scripts/HF_VERSION`) | lint, snapshot, render | Apache-2.0 (HeyGen); npx downloads the pinned version |
| GSAP 3 (loaded from jsDelivr by the composition at render time) | every timeline | GSAP Standard "No Charge" licence (Webflow, 2025): free incl. commercial; prohibited only in no-code visual animation builders that compete with Webflow; AI-generated GSAP code is expressly allowed |
| ffmpeg, Node, Python, numpy, OpenCV, Pillow | everything | their own licences; you install them (`doctor.sh`) |
| openai-whisper | transcription | MIT |
| mlx-whisper (optional, Apple silicon: `transcribe.py --backend mlx`, `islands_tx.py`) | faster transcription | MIT |
| Pexels videos (`broll_fetch.py get`, by the page's public download link) | stock B-roll originals | Pexels License (free, no attribution); you download them, nothing ships |
| Wikimedia Commons videos (`broll_fetch.py search` / `get commons:<id>`, no key) | stock B-roll | per file: CC0, public domain or CC BY only (credit line kept for the caption); CC BY-SA refused |
| Google Gemini API (`GEMINI_API_KEY`, free tier) | B-roll people rules + line match (`broll_vision.py`, `broll_qa.py`), own-footage descriptions, reference study, AI stills, rough-cut audits | Google's API terms; frames you check are sent to Google |
| ElevenLabs API (`ELEVENLABS_API_KEY`) | the vector explainer's narrator only | ElevenLabs terms; paid plans for commercial use |
| macOS Vision (`scripts/ocr_text.js` via `osascript`) | the caption size/contrast check in `broll_qa.py` | part of macOS; this check needs a Mac |
| simple-icons (fetched by slug at build time) | app logos in stan style / Seoul list icons | CC0 icons; the brands are their owners' trademarks |
| Google Fonts (`recipes/clean-os/fetch_fonts.py`) | Inter, Great Vibes in a Clean OS project | SIL OFL |
